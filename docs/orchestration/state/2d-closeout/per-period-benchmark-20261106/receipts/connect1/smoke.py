import json, os, sys
sys.path.insert(0, os.getcwd())
import numpy as np
import per_period_benchmark as P
out = {"stage": "smoke"}
m = P.import_reused()
rows = P.read_inputs()
pick = [r for r in rows if P.Path(r[1]).name.startswith("cov_ptpl_") or P.Path(r[1]).parent.name == "pu_PA_b01"]
assert len(pick) == 2, pick
dest = sys.argv[1]
os.makedirs(dest)
at = {}
for _, src in pick:
    st0 = os.stat(src)
    P.noatime_copy(src, os.path.join(dest, P.copy_name(src)))
    st1 = os.stat(src)
    at[src] = {"atime_before": st0.st_atime_ns, "atime_after": st1.st_atime_ns, "equal": st0.st_atime_ns == st1.st_atime_ns}
out["source_atimes"] = at
ver = P.verify_copies(dest, pick)
out["verify"] = ver
if ver["verdict"] != "PASS" or not all(v["equal"] for v in at.values()):
    out["verdict"] = "FAIL"
    print(json.dumps(out, indent=1)); sys.exit(3)
cov = os.path.join(dest, P.copy_name([s for _, s in pick if "cov_ptpl" in s][0]))
prod = os.path.join(dest, P.copy_name([s for _, s in pick if "pu_PA_b01" in s][0]))
roles = {"published": cov, "E_R": prod, "CTRL": prod,
         "groups": {g: {"s42": prod, "s43": prod, "boot": {r: prod for r in range(1, 11)}} for g in P.GROUPS}}
pub, prods = P.load_all(m, roles)
mask = np.diag(pub["stat"]) > 0
x = prods["PA_b01"]
txt = np.zeros(224)
with open(os.path.join(str(P.REPO), "2d-unfolding/minerva_paper_anc/data_result_ptpl_2D_minerva_inclusive_6GeV.txt")) as fh:
    next(fh)
    for line in fh:
        if line.strip():
            pz, pt, xs = line.split(",")[:3]
            txt[(int(pt) - 1) * 16 + (int(pz) - 1)] = float(xs)
rel_txt = float(np.max(np.abs(pub["p"][mask] - txt[mask]) / np.abs(txt[mask])))
cells = P.ctl_cells(m.reported_cells, np.flatnonzero(mask), {"PA_b01": x})
checks = {
    "published_shapes": [list(pub["p"].shape), list(pub["total"].shape), list(pub["stat"].shape)],
    "n_reported": int(mask.sum()),
    "total_symmetric_max_abs": float(np.max(np.abs(pub["total"] - pub["total"].T))),
    "published_vs_text_release_max_rel_reported_cells": rel_txt,
    "product_shape": list(x.shape), "product_finite": bool(np.all(np.isfinite(x))),
    "product_positive_cells": int((x > 0).sum()), "cells_control": cells,
    "n_products_loaded": len(prods),
}
ok = (checks["published_shapes"] == [[224], [224, 224], [224, 224]] and checks["n_reported"] == 205
      and rel_txt <= 5e-3 * (1 + 1e-9)
      and checks["product_finite"] and cells["verdict"] == "PASS" and len(prods) == 38)
# total_symmetric_max_abs is printed only: exact symmetry of the published TMatrix is not a declared property
out["checks"] = checks
out["verdict"] = "PASS" if ok else "FAIL"
print(json.dumps(out, indent=1))
sys.exit(0 if ok else 3)
