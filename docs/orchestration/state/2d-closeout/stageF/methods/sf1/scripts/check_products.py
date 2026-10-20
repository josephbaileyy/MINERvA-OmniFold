"""SF-1 step 1 product checks: a quarter product against the production half product of the same seed (format,
same seed/split/draws/truth), and the half rerun against production (bitwise reproduction).
usage: check_products.py <null> <seed> [<seed> ...]"""
import json, sys
from pathlib import Path
import numpy as np

S = Path("/pscratch/sd/j/josephrb/methods-paper/sf1-20261019")
P = Path("/pscratch/sd/j/josephrb/s5p-20260926/runs/prod/cal")
VOLATILE = {"slurm_job", "seconds_unfold"}


def load(p):
    z = np.load(p, allow_pickle=False)
    return {k: z[k] for k in z.files if k != "meta"}, json.loads(str(z["meta"])), sorted(z.files)


def diff_meta(a, b, path=""):
    out = []
    for k in sorted(set(a) | set(b)):
        if path == "" and k in VOLATILE:
            continue
        if k not in a or k not in b:
            out.append(f"{path}{k}: only in {'quarter/rerun' if k in a else 'production'}")
        elif isinstance(a[k], dict) and isinstance(b[k], dict):
            out += diff_meta(a[k], b[k], f"{path}{k}.")
        elif a[k] != b[k]:
            out.append(f"{path}{k}: {a[k]!r} vs {b[k]!r}")
    return out


null = sys.argv[1]
res = {}
for seed in map(int, sys.argv[2:]):
    prod = P / null / f"cal_{null}_s{seed}.npz"
    ap, mp, kp = load(prod)
    r = {"production": str(prod)}
    q = S / "runs/quarter" / null / f"sf1q_{null}_s{seed}.npz"
    if q.exists():
        aq, mq, kq = load(q)
        r["quarter"] = {"path": str(q), "files_equal": kq == kp,
                        "shapes": {k: [list(aq[k].shape), str(aq[k].dtype), list(ap[k].shape), str(ap[k].dtype)] for k in ap},
                        "xtrue_bitwise_equal": bool(np.array_equal(aq["xtrue_flat"], ap["xtrue_flat"])),
                        "xsec_bitwise_equal": bool(np.array_equal(aq["xsec_flat"], ap["xsec_flat"])),
                        "xsec_rel_diff_median": float(np.median(np.abs(aq["xsec_flat"] - ap["xsec_flat"]) / np.maximum(np.abs(ap["xsec_flat"]), 1e-300))),
                        "meta_differences": diff_meta(mq, mp), "n_unfolding_mc": mq["experiment"].get("n_unfolding_mc"),
                        "seconds_unfold": mq["seconds_unfold"], "slurm_job": mq["slurm_job"]}
    h = S / "runs/halfcheck" / null / f"cal_{null}_s{seed}.npz"
    if h.exists():
        ah, mh, kh = load(h)
        r["half_rerun"] = {"path": str(h), "files_equal": kh == kp,
                           "xsec_bitwise_equal": bool(np.array_equal(ah["xsec_flat"], ap["xsec_flat"])),
                           "xtrue_bitwise_equal": bool(np.array_equal(ah["xtrue_flat"], ap["xtrue_flat"])),
                           "meta_differences": diff_meta(mh, mp), "seconds_unfold": mh["seconds_unfold"],
                           "production_seconds_unfold": mp["seconds_unfold"]}
    res[seed] = r
print(json.dumps(res, indent=1))
