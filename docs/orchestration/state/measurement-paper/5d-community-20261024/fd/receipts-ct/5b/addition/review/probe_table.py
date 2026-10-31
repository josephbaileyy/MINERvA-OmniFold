"""Run cmd_table on the committed readouts: 'without' = committed; 'with' = committed with the block's name substituted
for C_resp in every string and key (what a correct with-arm readout's naming would be)."""
import json, sys, hashlib, tempfile, argparse
from pathlib import Path
WT = Path(sys.argv[1]); sys.path.insert(0, str(WT / "nd-unfolding"))
import fd_cpl_addition as A
tmp = Path(tempfile.mkdtemp(prefix="tbl-", dir=sys.argv[2]))
def ren(o):
    if isinstance(o, dict): return {(k.replace("C_resp", A.NAME) if "C_resp" in k else k): ren(v) for k, v in o.items()}
    if isinstance(o, list): return [ren(v) for v in o]
    if isinstance(o, str): return o.replace("C_total + C_resp", "C_total + " + A.NAME)
    return o
ns, pins = {}, {}
for k in (*A.READOUTS, "data_product"):
    src = WT / A.COMMITTED[k][0]
    ns[f"{k}_without"] = src; pins[f"{k}_without"] = A.COMMITTED[k][1]
    js = json.loads(src.read_text())
    if k == "data_product":
        js["relative_sigma"][A.BLOCK] = [0.0] * 16; js["relative_sigma"][A.REPORTED] = js["relative_sigma"][A.WITHOUT]
    else:
        js = ren(js)
    q = tmp / f"{k}_with.json"; q.write_text(json.dumps(js)); ns[f"{k}_with"] = q
    pins[f"{k}_with"] = hashlib.sha256(q.read_bytes()).hexdigest()
a = argparse.Namespace(cmd="table", audit_json=WT / A.FD / "fd/readout/fd_ct_5b_audit.json", out_dir=tmp / "out", **ns)
rc = A.run(a, pins)
print("cmd_table rc", rc)
for p, (x) in [(r["prediction"] + " " + r["kind"], r["without"]["matrix"]) for r in A.curated(
        {k: json.loads(ns[f"{k}_without"].read_text()) for k in A.READOUTS},
        {k: json.loads(Path(ns[f"{k}_with"]).read_text()) for k in A.READOUTS},
        json.loads(ns["data_product_without"].read_text()), json.loads(Path(ns["data_product_with"]).read_text()))["stage_g"]][:2]:
    print("  without matrix of", p, "=", repr(x))
