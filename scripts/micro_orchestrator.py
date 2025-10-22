#!/usr/bin/env python3
import os, json, subprocess, time, tempfile
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

REPO_DIR = os.getcwd()  # корень репо
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
    # если ветка ещё не создана на origin — создаём от main локально
    code, out, err = run(["git", "rev-parse", "--verify", f"origin/{BRANCH}"])
    if code != 0:
        run(["git", "checkout", "main"])
        run(["git", "checkout", "-B", BRANCH])
        run(["git", "push", "-u", "origin", BRANCH])
    else:
        run(["git", "checkout", "-B", BRANCH, f"origin/{BRANCH}"])
        run(["git", "pull", "origin", BRANCH])

def json_reply(handler, payload, status=200):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)

class H(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):  # тише лог
        return

    def do_GET(self):
        if self.path.startswith("/health"):
            return json_reply(self, {"ok": True, "ts": int(time.time())})
        return json_reply(self, {"ok": False, "error": "not found"}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)

        if parsed.path == "/diagnostics":
            code, out, err = run(["python3", "diagnostics.py", "--json"])
            try:
                payload = json.loads(out) if out.strip().startswith("{") else {"raw": out}
            except Exception:
                payload = {"raw": out}
            payload["meta"] = {"code": code, "stderr_tail": err[-400:]}
            return json_reply(self, payload)

        if parsed.path == "/patch":
            # принимаем unified diff из тела: либо text/plain, либо {"diff": "..."} JSON
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

            # мини-валидация: начало похоже на unified diff?
            if not any(diff_text.strip().startswith(p) for p in ("diff --git", "--- ", "+++ ")):
                return json_reply(self, {"ok": False, "error": "body must contain unified diff"}, 400)

            ensure_branch()

            # всегда работаем через временный файл — никаких stdin
            with tempfile.NamedTemporaryFile("w+", delete=False) as tf:
                tf.write(diff_text); tf.flush()
                # сначала пробуем чисто
                codeA, outA, errA = run(["git", "apply", "--whitespace=fix", tf.name])
                if codeA != 0:
                    # пробуем с --reject
                    codeB, outB, errB = run(["git", "apply", "--reject", tf.name])
                    if codeB != 0:
                        return json_reply(
                            self,
                            {"ok": False, "apply_err": (errA + "\n" + errB)[-800:]},
                            422
                        )

            # коммит и пуш
            qs = parse_qs(parsed.query or "")
            msg = qs.get("msg", ["chore: patch via micro_orchestrator"])[0]
            run(["git", "add", "-A"])
            codeC, outC, errC = run(["git", "commit", "-m", msg])
            if codeC != 0 and "nothing to commit" not in (outC + errC):
                return json_reply(self, {"ok": False, "commit_err": errC[-400:]}, 500)

            codeP, outP, errP = run(["git", "push", "origin", BRANCH], timeout=1200)

            # после пуша — короткий отчёт диагностики
            codeD, outD, errD = run(["python3", "scripts/diag_report.py"])

            return json_reply(
                self,
                {
                    "ok": codeP == 0,
                    "push_stdout_tail": outP[-400:],
                    "push_stderr_tail": errP[-400:],
                    "diag": {"code": codeD, "stdout_tail": outD[-400:], "stderr_tail": errD[-400:]}
                },
                200 if codeP == 0 else 500
            )

        return json_reply(self, {"ok": False, "error": "not found"}, 404)

def main():
    httpd = HTTPServer((HOST, PORT), H)
    print(f"[micro_orchestrator] listening on http://{HOST}:{PORT} (branch={BRANCH})")
    httpd.serve_forever()

if __name__ == "__main__":
    main()
