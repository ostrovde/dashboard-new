#!/usr/bin/env python3
import os, json, subprocess, time, urllib.request, urllib.parse, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_FILE = LOG_DIR / f"diagnostics-{int(time.time())}.json"

def run(cmd, cwd=None, timeout=300):
    p = subprocess.Popen(cmd, cwd=str(cwd) if cwd else None,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        out, err = p.communicate(timeout=timeout)
        code = p.returncode
    except subprocess.TimeoutExpired:
        p.kill()
        out, err = p.communicate()
        code = 124
    return code, out, err

def post_telegram(text: str):
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        return "telegram: skipped (no env)"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": True
    }).encode()
    try:
        with urllib.request.urlopen(url, data=data, timeout=10) as r:
            return f"telegram: {r.status}"
    except Exception as e:
        return f"telegram: error {e}"

def main():
    code, out, err = run(["python3", "diagnostics.py", "--json"], cwd=ROOT)
    try:
        report = json.loads(out) if out.strip().startswith("{") else {"raw": out}
    except Exception:
        report = {"raw": out}
    report["meta"] = {"code": code, "stderr_tail": err[-400:]}
    REPORT_FILE.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    # краткое резюме
    issues = report.get("issues", [])
    levels = [i.get("level","warn") for i in issues]
    errors = sum(1 for l in levels if l == "error")
    warns  = sum(1 for l in levels if l != "error")

    summary = f"Diagnostics: {errors} errors, {warns} warnings. File: {REPORT_FILE.name}"
    tel = post_telegram(summary)
    print(summary, tel)

if __name__ == "__main__":
    sys.exit(main() or 0)
