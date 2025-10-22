#!/usr/bin/env python3
import os, json, subprocess, time, tempfile, glob
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from pathlib import Path

REPO_DIR = os.getcwd()
BRANCH   = os.getenv("WORK_BRANCH", "msp-dev")
HOST     = "127.0.0.1"
PORT     = 8078

def run(cmd, cwd=None, timeout=600):
    p = subprocess.Popen(cmd, cwd=cwd or REPO_DIR,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        out, err = p.communicate(timeout=timeout)
        code = p.returncode
    except subprocess.TimeoutExpired:
        p.kill(); out, err = p.communicate(); code = 124
    return code, out, err

def ensure_branch():
    run(["git", "fetch", "origin"])
    code, _, _ = run(["git", "rev-parse", "--verify", f"origin/{BRANCH}"])
    if code != 0:
        run(["git", "checkout", "main"])
        run(["git", "checkout", "-B", BRANCH])
        run(["git", "push", "-u", "origin", BRANCH])
    else:
        run(["git", "checkout", "-B", BRANCH, f"origin/{BRANCH}"])
        run(["git", "pull", "origin", BRANCH])

def json_reply(h, payload, status=200):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    h.send_response(status)
    h.send_header("Content-Type", "application/json; charset=utf-8")
    h.send_header("Content-Length", str(len(data)))
    h.end_headers()
    h.wfile.write(data)

def gh_pr_get_url():
    c1, o1, _ = run(["gh","pr","view","--head",BRANCH,"--json","url","--jq",".url"])
    if c1 == 0 and o1.strip(): return o1.strip()
    c2, o2, _ = run(["gh","pr","list","--head",BRANCH,"--state","all","--json","url","--jq",".[0].url"])
    if c2 == 0 and o2.strip(): return o2.strip()
    return ""

def gh_pr_create_or_get(title, body):
    url = gh_pr_get_url()
    if url: return {"created": False, "url": url}
    with tempfile.NamedTemporaryFile("w+", delete=False) as tf:
        tf.write(body); tf.flush()
        c,o,e = run(["gh","pr","create","--base","main","--head",BRANCH,"--title",title,"--body-file",tf.name], timeout=600)
    url2 = gh_pr_get_url()
    if url2: return {"created": (c==0), "url": url2, "stdout_tail": o[-400:], "stderr_tail": e[-400:]}
    if c == 0: return {"created": True, "url": o.strip()}
    return {"created": False, "error": (e or o)[-400:]}

SAFE_TASKS = {
    "build": ["bash","-lc","npm ci || true; npm run build"],
    "diag":  ["bash","-lc","python3 diagnostics.py --json || true"],
    "test":  ["bash","-lc","npm test --if-present -- --ci --reporters=default || true"],
    "smoke": ["bash","-lc","chmod +x scripts/smoke.sh && scripts/smoke.sh || true"],
    "kpi":   ["bash","-lc","chmod +x scripts/validate_kpi.py && scripts/validate_kpi.py data/sample_kpi.csv || true"],
}

def collect_donesheet():
    dist_ok = Path(REPO_DIR, "dist", "index.html").exists()
    logs = sorted(glob.glob(os.path.join(REPO_DIR, "logs", "diagnostics-*.json")))
    last_log = logs[-1] if logs else ""
    c, out, _ = run(["git","rev-parse","--short","HEAD"])
    last_commit = out.strip() if c==0 else ""
    c2, out2, _ = run(["git","status","--porcelain"])
    clean = (out2.strip() == "")
    lines = []
    lines.append("### Definition of Done (auto)")
    lines.append(f"- [{'x' if dist_ok else ' '}] Build OK (dist/index.html present)")
    lines.append(f"- [{'x' if bool(last_log) else ' '}] Diagnostics report exists ({Path(last_log).name if last_log else 'n/a'})")
    lines.append(f"- [{'x' if clean else ' '}] Git working tree clean")
    lines.append(f"- Commit: `{last_commit}` on `{BRANCH}`")
    if last_log:
        lines.append(f"- Last diag log: `logs/{Path(last_log).name}`")
    return "\n".join(lines)

def gh_pr_update_body(extra_body):
    url = gh_pr_get_url()
    if not url:
        return {"ok": False, "error": "no PR found for head branch"}
    with tempfile.NamedTemporaryFile("w+", delete=False) as tf:
        tf.write(extra_body); tf.flush()
        c,o,e = run(["gh","pr","edit",url,"--body-file",tf.name], timeout=600)
    ok = (c == 0)
    return {"ok": ok, "url": url, "stdout_tail": o[-400:], "stderr_tail": e[-400:]}

class H(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): return

    def do_GET(self):
        if self.path.startswith("/health"):
            return json_reply(self, {"ok": True, "ts": int(time.time()), "branch": BRANCH})
        return json_reply(self, {"ok": False, "error": "not found"}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)

        if parsed.path == "/diagnostics":
            c,o,e = run(["python3","diagnostics.py","--json"])
            try:
                payload = json.loads(o) if o.strip().startswith("{") else {"raw": o}
            except Exception:
                payload = {"raw": o}
            payload["meta"] = {"code": c, "stderr_tail": e[-400:]}
            return json_reply(self, payload)

        if parsed.path == "/patch":
            length = int(self.headers.get("Content-Length") or "0")
            body = self.rfile.read(length) if length else b""
            ctype = (self.headers.get("Content-Type") or "").lower()
            if "application/json" in ctype:
                try:
                    diff_text = json.loads(body.decode("utf-8"))["diff"]
                except Exception:
                    return json_reply(self, {"ok": False, "error": "bad json"}, 400)
            else:
                diff_text = body.decode("utf-8", errors="ignore")
            if not any(diff_text.strip().startswith(p) for p in ("diff --git","--- ","+++ ")):
                return json_reply(self, {"ok": False, "error": "body must contain unified diff"}, 400)

            ensure_branch()
            with tempfile.NamedTemporaryFile("w+", delete=False) as tf:
                tf.write(diff_text); tf.flush()
                c1,o1,e1 = run(["git","apply","--whitespace=fix",tf.name])
                if c1 != 0:
                    c2,o2,e2 = run(["git","apply","--reject",tf.name])
                    if c2 != 0:
                        return json_reply(self, {"ok": False, "apply_err": (e1+"\n"+e2)[-800:]}, 422)

            qs = parse_qs(parsed.query or "")
            msg = qs.get("msg", ["chore: patch via micro_orchestrator"])[0]
            run(["git","add","-A"])
            cc,oc,ec = run(["git","commit","-m",msg])
            if cc != 0 and "nothing to commit" not in (oc+ec):
                return json_reply(self, {"ok": False, "commit_err": ec[-400:]}, 500)

            cp,op,ep = run(["git","push","origin",BRANCH], timeout=1200)
            cd,od,ed = run(["python3","scripts/diag_report.py"])
            return json_reply(self, {
                "ok": cp==0,
                "push_stdout_tail": op[-400:], "push_stderr_tail": ep[-400:],
                "diag": {"code": cd, "stdout_tail": od[-400:], "stderr_tail": ed[-400:]}
            }, 200 if cp==0 else 500)

        if parsed.path == "/pr":
            ensure_branch()
            length = int(self.headers.get("Content-Length") or "0")
            body = self.rfile.read(length).decode("utf-8") if length else ""
            title = "chore(msp): automated PR from micro_orchestrator"
            result = gh_pr_create_or_get(title, body if body.strip() else "Automated PR")
            ok = "error" not in result
            return json_reply(self, {"ok": ok, **result}, 200)

        if parsed.path == "/run":
            qs = parse_qs(parsed.query or "")
            task = (qs.get("task", [""])[0] or "").strip().lower()
            if task not in SAFE_TASKS:
                return json_reply(self, {"ok": False, "error": f"unknown task '{task}'"}, 400)
            c,o,e = run(SAFE_TASKS[task], timeout=1800)
            return json_reply(self, {"ok": True, "task": task, "code": c, "stdout_tail": o[-1200:], "stderr_tail": e[-1200:]})

        if parsed.path == "/donesheet":
            sheet = collect_donesheet()
            res = gh_pr_update_body(sheet)
            return json_reply(self, {"ok": res.get("ok", False), **res}, 200)

        return json_reply(self, {"ok": False, "error": "not found"}, 404)

def main():
    httpd = HTTPServer((HOST, PORT), H)
    print(f"[micro_orchestrator] listening on http://{HOST}:{PORT} (branch={BRANCH})")
    httpd.serve_forever()

if __name__ == "__main__":
    main()
