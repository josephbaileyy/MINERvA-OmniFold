"""Local smoke: S2R and B0 through the production loop with REAL LightGBM on FD-STAB's synthetic fine-grid inputs."""
import sys, time
from pathlib import Path
import numpy as np
ND = Path.home() / "s2r-wt/nd-unfolding"
for p in (ND / "s2r", ND, ND / "tier3", ND / "tests", ND / "pv-ladder", ND / "prior_retention"):
    sys.path.insert(0, str(p))
import s2r_arm as S, t3p_arms as A
import test_estimator_stability_probe as TS
inp = TS.fine_inputs(40000, 3)
unf = {k: inp[k] for k in ("MCgen", "MCreco", "pass_reco", "pass_truth", "w_truth", "w_reco", "denom_nd", "flux",
                           "data_pot", "n_nucleons", "edges", "measured", "measured_weights")}
n = len(inp["MCgen"])
r = np.random.default_rng(5).uniform(0.7, 1.3, n)
ncell = int(np.prod([len(e) - 1 for e in inp["edges"]]))
fm = (np.arange(ncell) % 17 - 1).astype(int)
M16 = np.vstack([(fm == c).astype(float) for c in range(16)])
S.ITERS.update({"B0": 5, "S2R": 8})
out = {}
for arm, it in (("B0", 5), ("S2R", 8)):
    t0 = time.time()
    rec = A.ArmRecorder(unf, r, M16, fm, it)
    xs, params, tr = S.traced_unfold_s2r(unf, rec, 42, 4, it, arm, r)
    a = rec.arrays(tr)
    out[arm] = a
    ev = tr.evidence
    print(arm, "iters", it, "s", round(time.time() - t0, 1), "lgbm params deterministic:",
          [p.get("deterministic") for p in params], "s2r_fits", ev["s2r_fits"],
          "max round trip", max(ev["s2r_max_round_trip"], default=None), "clipped", ev["s2r_clipped"][:3],
          "clip_step2 max", a["clip_step2"].max(axis=0).tolist())
b, s = out["B0"]["X16_push"], out["S2R"]["X16_push"]
print("C-ONE max rel k=1:", float(np.max(np.abs(s[0] / b[0] - 1))))
print("k=5 max rel S2R vs B0:", float(np.max(np.abs(s[4] / b[4] - 1))))
print("norm_push B0", np.round(out["B0"]["norm_push"], 4).tolist(), "S2R", np.round(out["S2R"]["norm_push"], 4).tolist())
