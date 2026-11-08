import ast, json, re, sys
import numpy as np
products, L, deploy, probe_sha, out = sys.argv[1:6]
sys.path.insert(0, f"{deploy}/nd-unfolding")
import ensemble_estimator_probe as eep  # noqa: E402  (SCHEMA, INTERNAL_BASE, DETERMINISM, DRY2: the bound values)
ZERO = {"MCgen": 0, "MCreco": 0, "measured": 0, "bkg_reco": 0}
rec = {"schema": "ens1-a1-s2-dry-postrun/1", "numpy": np.__version__, "products": {}, "timing": {}}
fails = []
rows = [l.rstrip("\n").split("\t") for l in open(products) if l.strip()]
want_ids = {f"ens1_{t}_k{k:03d}" for t, k in eep.DRY2}
if {r[0] for r in rows} != want_ids:
    fails.append(f"the dry tasks {sorted(r[0] for r in rows)} are not DRY2 {sorted(want_ids)}")
arrays = {}
for tid, path in rows:
    m = re.fullmatch(r"ens1_(.+)_k(\d\d\d)", tid)
    truth, k = m.group(1), int(m.group(2))
    with np.load(path, allow_pickle=False) as z:
        meta = json.loads(str(z["meta"]))
        arrays[(truth, k)] = {n: z[n].copy() for n in ("xsec_flat", "xtrue_flat") if n in z.files}
    b = meta.get("ens1") or {}
    want = {"schema": eep.SCHEMA, "mode": "closure", "k": k, "internal_seed": eep.INTERNAL_BASE + k, "truth": truth}
    got = {key: b.get(key) for key in want}
    moved, code, dt = b.get("moved_rows"), b.get("code_sha256"), b.get("closure_dtype_requested")
    rec["products"][tid] = {"path": path, "block": got, "moved_rows": moved, "code_sha256": code,
                            "closure_dtype_requested": dt, "coord_sha256": b.get("coord_sha256"),
                            "hypothesis_sha256": (meta.get("hypothesis") or {}).get("sha256"),
                            "alternative_sha256": (meta.get("alternative") or {}).get("sha256"),
                            "pseudo_seed": meta.get("pseudo_seed"), "development": meta.get("development"),
                            "seconds_unfold_meta": meta.get("seconds_unfold")}
    if got != want:
        fails.append(f"{tid}: ens1 block {got}, the task states {want}")
    if moved != ZERO:
        fails.append(f"{tid}: moved_rows {moved}")
    if code != probe_sha:
        fails.append(f"{tid}: code_sha256 {code}")
    if dt is None:
        fails.append(f"{tid}: closure_dtype_requested not recorded")
    if set(arrays[(truth, k)]) != {"xsec_flat", "xtrue_flat"}:
        fails.append(f"{tid}: xsec_flat or xtrue_flat missing")
    log = open(f"{L}/tasks/{tid}.log", errors="replace").read()
    parsed = [ast.literal_eval(s) for s in re.findall(r"\[ens1\] grid membership moved rows (\{[^}]*\})", log)]
    if len(parsed) != 1 or parsed[0] != ZERO:
        fails.append(f"{tid}: log moved-rows lines {parsed}")
    outl = [json.loads(l) for l in log.splitlines() if l.startswith('{"out"')]
    if len(outl) != 1 or outl[0].get("rc") != 0 or outl[0].get("out") != path.rsplit("/", 1)[-1]:
        fails.append(f"{tid}: runner lines {outl}")
    t0, t1 = float(open(f"{L}/{tid}.start").read()), float(open(f"{L}/{tid}.end").read())
    rec["timing"][tid] = {"seconds": [o.get("seconds") for o in outl], "seconds_unfold_meta": meta.get("seconds_unfold"),
                          "wall": round(t1 - t0, 1)}


def same(a, b):
    return a.dtype == b.dtype and a.shape == b.shape and a.tobytes() == b.tobytes()


cmp = {}
nom1, a7 = arrays.get(("nominal", 1)), arrays.get((eep.DETERMINISM[1], 1))
if nom1 and a7 and set(nom1) == set(a7) == {"xsec_flat", "xtrue_flat"}:
    cmp["determinism"] = {n: {"dtype": [str(nom1[n].dtype), str(a7[n].dtype)], "shape": [list(nom1[n].shape), list(a7[n].shape)],
                              "bitwise_identical": bool(same(nom1[n], a7[n]))} for n in ("xsec_flat", "xtrue_flat")}
    for n, v in cmp["determinism"].items():
        if not v["bitwise_identical"]:
            fails.append(f"DETERMINISM: A7_mnvtune k=1 {n} DIFFERS from nominal k=1")
else:
    fails.append("DETERMINISM: nominal k=1 or A7_mnvtune k=1 is missing")
cmp["truth_vectors"] = {}
for t in sorted({t for t, _ in eep.DRY2 if t != eep.DETERMINISM[1]}):
    ks = sorted(k for (t_, k) in arrays if t_ == t)
    xs = [arrays[(t, k)].get("xtrue_flat") for k in ks]
    ok = len(xs) > 1 and all(x is not None for x in xs) and all(same(xs[0], x) for x in xs[1:])
    cmp["truth_vectors"][t] = {"k": ks, "bitwise_identical": bool(ok)}
    if not ok:
        fails.append(f"TRUTH VECTORS: {t} xtrue_flat differs across k {ks}")
rec["compare"] = cmp
secs = [s for r in rec["timing"].values() for s in r["seconds"] if s is not None]
t = max(secs) if secs else None
w = max((r["wall"] for r in rec["timing"].values()), default=None)
rec["projection"] = {"t_max_seconds": t, "task_wall_max": w, "lane_unfolds": 34, "bound_t": 705, "limit_h": 6.75,
                     "shard_wall_h_from_t": None if t is None else round((34 * t + 300) / 3600, 3),
                     "shard_wall_h_from_wall": None if w is None else round((34 * w + 300) / 3600, 3)}
rec["failures"] = fails
rec["verdict"] = "PASS" if not fails else "STOP"
with open(out, "w") as fh:
    json.dump(rec, fh, indent=1)
print(json.dumps({"verdict": rec["verdict"], "failures": fails, "compare": cmp, "projection": rec["projection"],
                  "timing": rec["timing"],
                  "dtype_requested": {k: v["closure_dtype_requested"] for k, v in rec["products"].items()}}))
sys.exit(0 if not fails else 4)
