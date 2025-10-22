import json, sys, re, os, glob, csv
def msg(level, code, text): return {"level":level,"code":code,"msg":text}
def scan_document_write(root="src"):
    rx=re.compile(r'document\.write\('); bad=[]
    for p in glob.glob(f"{root}/**/*.*", recursive=True):
        if p.endswith((".js",".ts",".tsx")):
            try:
                if rx.search(open(p,encoding="utf-8").read()): bad.append(p)
            except: pass
    return bad
def check_manifest(path="dist/.vite/manifest.json"):
    try:
        m=json.load(open(path,encoding="utf-8"));  return [] if m else ["empty-manifest"]
    except Exception as e: return [f"manifest-error:{e}"]
def check_yield_csv(path="data/yield/*.csv"):
    zeros=0; total=0
    for f in glob.glob(path):
        with open(f,encoding="utf-8") as fh:
            r=csv.DictReader(fh)
            for row in r:
                total+=1
                try:
                    y=float(row.get("yield_cgha","nan"))
                    if y==0: zeros+=1
                except: pass
    return {"rows":total,"zeros":zeros}
def main():
    res={"errors":[],"warnings":[],"metrics":{}}
    bad=scan_document_write()
    if bad: res["errors"].append(msg("error","E_JS_WRITE",f"document.write: {bad}"))
    man=check_manifest()
    if man: res["warnings"].append(msg("warn","W_ASSETS",f"assets: {man}"))
    y=check_yield_csv()
    res["metrics"]["yield_rows"]=y["rows"]; res["metrics"]["yield_zeros"]=y["zeros"]
    ok=(len(res["errors"])==0)
    print(json.dumps({"ok":ok, **res}, ensure_ascii=False))
    sys.exit(0 if ok else 2)
if __name__=="__main__": main()
