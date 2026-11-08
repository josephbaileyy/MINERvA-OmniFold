import ast, json, re, sys
import numpy as np
products, L, f64_old, probe_sha, out = sys.argv[1:6]
ZERO = {"MCgen": 0, "MCreco": 0, "measured": 0, "bkg_reco": 0}
rec = {"schema": "ens1-a1-dry-postrun/1", "numpy": np.__version__, "products": {}, "logs": {}, "timing": {}}
fails = []
rows = [l.rstrip("\n").split("\t") for l in open(products) if l.strip()]
f64_new = None
for tid, path in rows:
    with np.load(path, allow_pickle=False) as z:
        meta = json.loads(str(z["meta"]))
    b = meta.get("ens1") or {}
    m = re.fullmatch(r"ens1_s(\d\d)_k(\d\d\d)", tid)
    if tid == "ens1_F64":
        want = {"mode": "base", "k": None, "protocol_seed": 0}
        f64_new = path
    else:
        want = {"mode": "stability", "k": int(m.group(2)), "protocol_seed": int(m.group(1))}
    got = {k: b.get(k) for k in want}
    moved, code = b.get("moved_rows"), b.get("code_sha256")
    rec["products"][tid] = {"path": path, "moved_rows": moved, "block": got, "code_sha256": code}
    if moved != ZERO:
        fails.append(f"E5: {tid} records moved_rows {moved}")
    if got != want:
        fails.append(f"{tid}: ens1 block {got}, the task states {want}")
    if code != probe_sha:
        fails.append(f"{tid}: code_sha256 {code}")
    log = open(f"{L}/tasks/{tid}.log", errors="replace").read()
    parsed = [ast.literal_eval(s) for s in re.findall(r"\[ens1\] grid membership moved rows (\{[^}]*\})", log)]
    rec["logs"][tid] = parsed
    if not parsed or any(p != ZERO for p in parsed):
        fails.append(f"E5 log: {tid} logged {parsed}")
    su = []
    for line in log.splitlines():
        if line.startswith('{"out"'):
            su.append(float(json.loads(line)["seconds_unfold"]))
    t0, t1 = float(open(f"{L}/{tid}.start").read()), float(open(f"{L}/{tid}.end").read())
    rec["timing"][tid] = {"seconds_unfold": su, "wall": round(t1 - t0, 1)}
    if len(su) != 1:
        fails.append(f"{tid}: {len(su)} seconds_unfold lines, not 1")
cmp = {}
if f64_new is None:
    fails.append("no F64 product")
else:
    with np.load(f64_new, allow_pickle=False) as a, np.load(f64_old, allow_pickle=False) as o:
        rec["f64_keys"] = {"new": sorted(a.files), "attempt1": sorted(o.files)}
        for k in ("xsec_flat", "xtrue_flat"):
            if k not in a.files or k not in o.files:
                cmp[k] = {"present": [k in a.files, k in o.files], "bitwise_identical": False}
                fails.append(f"F64 {k} is not in both products")
                continue
            x, y = a[k], o[k]
            same = x.dtype == y.dtype and x.shape == y.shape and x.tobytes() == y.tobytes()
            cmp[k] = {"dtype": [str(x.dtype), str(y.dtype)], "shape": [list(x.shape), list(y.shape)],
                      "bitwise_identical": bool(same)}
            if not same:
                fails.append(f"F64 {k} DIFFERS from attempt 1")
rec["f64_compare"] = cmp
su_all = [v for r in rec["timing"].values() for v in r["seconds_unfold"]]
t = max(su_all) if su_all else None
w = max((r["wall"] for r in rec["timing"].values()), default=None)
rec["projection"] = {"t_max_seconds_unfold": t, "task_wall_max": w, "bound_t": 687, "limit_h": 8.1,
                     "shard_wall_h_from_t": None if t is None else round((42 * t + 300) / 3600, 3),
                     "shard_wall_h_from_wall": None if w is None else round((42 * w + 300) / 3600, 3)}
rec["failures"] = fails
rec["verdict"] = "PASS" if not fails else "STOP"
with open(out, "w") as fh:
    json.dump(rec, fh, indent=1)
print(json.dumps({"verdict": rec["verdict"], "failures": fails, "f64_compare": cmp,
                  "moved_rows": {k: v["moved_rows"] for k, v in rec["products"].items()},
                  "projection": rec["projection"]}))
sys.exit(0 if not fails else 4)
