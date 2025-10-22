import json, sys
ROUTES = ["/", "/map", "/stats"]
def main():
    mp="dist/.vite/manifest.json"
    try: m=json.load(open(mp,encoding="utf-8"))
    except Exception as e: print(f"ERROR manifest:{e}"); sys.exit(2)
    entries=[k for k,v in m.items() if v.get("isEntry")]
    missing=[]
    if not entries: missing.append("no-entry")
    if not any("index.html" in k for k in m.keys()): missing.append("missing:index.html")
    print("OK" if not missing else "WARN:"+";".join(missing))
    sys.exit(0 if not missing else 1)
if __name__=="__main__": main()
