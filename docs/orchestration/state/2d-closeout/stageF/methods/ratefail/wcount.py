import json, sys
from pathlib import Path
import numpy as np
WT = Path(sys.argv[1]); sys.path.insert(0, str(WT / "nd-unfolding"))
import s5c_coverage as cov
S = WT / "docs/orchestration/state/s5c"
U, names = cov.reported_functionals(json.loads((S / "contract.json").read_text()))
rec = json.loads((S / "tier_s/interim_400.json").read_text()); g = {x["truth"]: x for x in rec["grid"]}
z = np.load(S / "p3/products/p3_nominal_s1.npz"); xt = z["xtrue_flat"]; Wb = np.unravel_index(np.arange(xt.size), tuple(z["shape"]))[4]
den = (U * xt).sum(1)
cls = np.full(len(names), "mixed", object)
for lab, m in (("W<1.4", Wb <= 1), ("1.4-2.2", (Wb == 2) | (Wb == 3)), ("2.2-3", Wb == 4), (">=3", Wb == 5), (">=2.2", Wb >= 4)):
    sh = (U * (xt * m)).sum(1) / den
    cls[(sh > 0.999) & (cls == "mixed")] = lab
for t in ("nominal", "eavail_tilt"):
    fut = np.array(g[t]["ucb68"]) < 0.66
    c68 = np.array(g[t]["hits68"]) / 400
    print(t, "futile68", fut.sum())
    for lab in ("W<1.4", "1.4-2.2", "2.2-3", ">=3", ">=2.2", "mixed"):
        m = cls == lab
        print(f"  {lab:8s} n={m.sum():3d} futile={int((fut & m).sum()):3d} median cov68={np.median(c68[m]) if m.any() else float('nan'):.3f}")
print("mixed:", [n for n, c in zip(names, cls) if c == "mixed"])
