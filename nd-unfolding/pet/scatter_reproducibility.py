#!/usr/bin/env python3
"""Is the D2 per-bin scatter STRUCTURAL or run-to-run NOISE? The answer decides whether ensembling fixes it.

Session A established the D2 shortfall is 97.8% per-bin scatter rather than bias: the signed mean response
already sits at the dilution ideal, and the loss comes from the closure's per-cell absolute value converting
symmetric scatter into a one-sided penalty.

That leaves a question worth real money. Two possibilities produce the same aggregate number:

  * NOISE  -- each training run scatters cells independently. Then averaging N runs shrinks the scatter
              like 1/sqrt(N), and an ensembled estimator could pass a criterion a single run fails.
  * STRUCTURE -- every run misses the same cells the same way. Then averaging changes nothing and the
              criterion (or the estimator) has to change.

Two independent runs at the identical configuration now exist -- 56381674 and the epochs-8 control
56431649 -- and each report carries all 285 cells. So the question is directly answerable:

  1. correlate the per-cell residuals of the two runs. High correlation => structure.
  2. build the ENSEMBLE spectrum (mean of the two unfolded) and recompute recovery the way the closure
     does. If recovery improves toward 0.80, ensembling is the lever; if it barely moves, it is not.

Test 2 is the one that matters, because it measures the actual proposed remedy rather than a proxy for it.
"""
import json
import os

import numpy as np

P = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/powered_closure"
A = os.path.join(P, "POWERED_CLOSURE_REPORT.slurm-56381674.json")
B = os.path.join(P, "underfit_probe/POWERED_CLOSURE_PROBE_REPORT.probe-ctl8-slurm-56431649.json")


def load(path):
    d = json.load(open(path))
    out = {k: np.asarray(d[k], float) for k in ("h_prior", "h_target", "h_unfolded", "h_untilted")}
    out["metrics"] = d["metrics"]
    return out


def l1(a, b):
    return float(np.abs(a - b).sum())


def main():
    a, b = load(A), load(B)
    np.testing.assert_allclose(a["h_prior"], b["h_prior"], rtol=0, atol=0,
                               err_msg="the two runs do not share a prior; not comparable")
    np.testing.assert_allclose(a["h_target"], b["h_target"], rtol=0, atol=0,
                               err_msg="the two runs do not share a target; not comparable")
    tgt, pri = a["h_target"], a["h_prior"]
    gap = l1(pri, tgt)
    print(f"shared prior and target confirmed identical; gap = {gap:.6f}")
    print(f"  run A 56381674  recovery {a['metrics']['recovery']:.6f}")
    print(f"  run B 56431649  recovery {b['metrics']['recovery']:.6f}")
    print()

    ra, rb = a["h_unfolded"] - tgt, b["h_unfolded"] - tgt
    print("=== 1. are the two runs' per-cell residuals the SAME pattern? ===")
    live = (np.abs(ra) > 0) | (np.abs(rb) > 0)
    c = float(np.corrcoef(ra[live], rb[live])[0, 1])
    print(f"  cells compared              {int(live.sum())} of {tgt.size}")
    print(f"  Pearson r(residual_A, residual_B)   {c:.6f}")
    print(f"  L1 distance between the two unfolded  {l1(a['h_unfolded'], b['h_unfolded']):.6f}"
          f"   (vs gap {gap:.6f})")
    verdict = ("STRUCTURAL -- the runs miss the same cells the same way"
               if c > 0.9 else
               "MIXED" if c > 0.5 else
               "NOISE-LIKE -- largely independent between runs")
    print(f"  => {verdict}")
    print()

    print("=== 2. does ENSEMBLING actually help? (recompute recovery on the mean spectrum) ===")
    ens = 0.5 * (a["h_unfolded"] + b["h_unfolded"])
    for name, spec in (("run A", a["h_unfolded"]), ("run B", b["h_unfolded"]),
                       ("mean(A,B)", ens)):
        res = l1(spec, tgt)
        print(f"  {name:10s} residual {res:.6f}   recovery {1 - res/gap:.6f}")
    res_ens = l1(ens, tgt)
    best = min(l1(a["h_unfolded"], tgt), l1(b["h_unfolded"], tgt))
    gain = (best - res_ens) / best * 100.0
    print()
    print(f"  ensemble reduces residual by {gain:.2f}% vs the better single run")
    print(f"  recovery needed 0.80; ensemble of 2 gives {1 - res_ens/gap:.4f}")
    # If scatter were independent, 2-run averaging cuts the scatter part by 1/sqrt(2) ~ 29%.
    print(f"  for reference, independent noise would cut the SCATTER term by "
          f"{(1 - 1/np.sqrt(2))*100:.1f}% with 2 runs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
