#!/usr/bin/env python3
"""B1 closure: inject a known truth-level RATE change and verify the unfold recovers it.

WHY THIS EXISTS
---------------
`B1-NORMALIZATION-FIX-DESIGN.md` §4: "The current closure cannot detect this class of bug, which
is why it went unnoticed. Required: a closure that injects a known truth-level rate change and
verifies recovery." The ordinary closure reweights MC to itself, so a null estimator `push = ones`
passes it (`AUDIT-FINDINGS-20260729-B.md` §3). A pure rate change is exactly the deformation that
`normalize=True`-on-both erases, and exactly the one no existing closure injects.

This runs BOTH configurations on the same sample and requires them to disagree:

  * CORRECTED (B1 §2a): measured block normalized to 1e6*R  -> must RECOVER the injected rate.
  * BROKEN (pre-B1):    both blocks normalized to 1e6       -> must NOT recover it; the step-1
                        class ratio is 1 by construction, so there is no rate discrepancy to learn
                        and `push` stays at ~1.

A closure that only checks the corrected configuration proves the pipeline runs, not that it can
see this defect. The discriminating assertion is that the broken configuration FAILS.

WHAT IT ALSO PRODUCES: THE GATE-4 TOLERANCE
-------------------------------------------
§2d requires the Gate-4 fold-forward tolerance to be measured before it is frozen, and names three
terms. This script measures all three, and compares term 1 against a closed form.

  1. STRUCTURAL FLOOR. `omnifold.py:185` pins off-acceptance `pull` to 1, so step 2 regresses
     across both acceptance classes at once and smooths `pass_reco` pushes toward 1. When
     acceptance is statistically INDEPENDENT of the truth features -- the worst case, because the
     step-2 regressor then cannot separate the classes at all -- the recursion has a closed form:

         push_k = R - (1-a)^k * (R - 1)        =>   floor_k = (1-a)^k * (R-1) / R

     Verified against this script on 2026-07-29 (N=8000, epochs=25): observed vs predicted
     1.1734/1.1800 (R=1.30, a=0.60, k=1), 1.2577/1.2520 (k=2), 1.2773/1.2923 (k=4), and
     1.1078/1.1156 at the nominal-like point (R=1.135, a=0.621, k=2). Real acceptance IS partly
     predictable from truth kinematics, so the realized floor is BELOW this bound.
     At the nominal (a=0.621, R~1.135, niter=2) the bound is 1.71%.
  2. FINITE ITERATION. Folded into the same closed form via k = niter.
  3. SUBSAMPLE SAMPLING. The ratio is subsample-invariant in expectation, not algebraically.
     Re-run with several --seed values and read the spread.

Against that, the defect the gate must DETECT is the broken configuration's ratio of ~1, i.e. a
deviation of (R-1)/R ~ 11.9% at R = 1.135. `fold_forward_ratio_dev_max = 0.05` sits between the
1.71% bound and the 11.9% signal with roughly 2x headroom on each side. Re-run this at the
measured R on 2026-08-03 and replace the PROVISIONAL marking in
`validate_pet_nominal_gate4.py:FROZEN["tolerances"]`.

A GRADIENT-STEP CONFOUND -- READ THIS BEFORE CONCLUDING THE FIX DOES NOT WORK
-----------------------------------------------------------------------------
`epochs` is the nominal's 8, but epochs are not the unit of optimization: STEPS are, and steps
scale with N/batch_size. At N=8,000 and batch 512 that is ~16 steps per epoch against the
nominal's ~3,900 at 2M rows, so a small run is badly under-trained and the residual is an
optimization artifact, NOT the structural floor. Measured on this host, 2026-07-29, at
R=1.135 / a=0.621 / niter=2 / epochs=8, deviation of the corrected arm from R:

    N =   8,000   2.61% .. 6.72%   (seed spread std 0.0176)   <- artifact-dominated
    N =  30,000   1.84% .. 3.44%   (std 0.0075)
    N = 120,000   1.39% .. 1.61%   (std 0.0011)                <- at the 1.71% analytic bound

It converges onto the closed-form floor from above as the step count rises, which is the evidence
that the residual at small N is optimization and the residual at large N is structural. The
nominal's 2M rows sit far to the right of this table, so expect <= ~1.5%. The default N below is
chosen to be past the artifact-dominated regime; do not lower it and read the result as physics.

SCOPE, STATED HONESTLY
----------------------
This trains MLPs on 2-D features, not PET on point clouds. The B1 mechanism is entirely in the
DataLoader normalization -> step-1 class weight blocks (`omnifold.py:176-177`) -> weight recursion
(`:184-204`) path, which is byte-identical for both model types; the network only supplies the
density ratio. What this does NOT establish is PET-specific training behaviour at 2M rows on the
real clouds. `test_b1_normalization_fix.py` covers the other half of the seam -- that
`build_fullevent_loaders` really does hand the engine a class ratio of R.

LOGIN-SAFE: synthetic events, no ROOT, no /pscratch, no dump, CPU. It DOES import TensorFlow and
train, so budget CPU minutes rather than seconds.

USAGE
-----
    python3 closure_b1_rate_injection.py                        # defaults, ~1 min
    python3 closure_b1_rate_injection.py --r-inject 1.135 --acceptance 0.621 --niter 2
    python3 closure_b1_rate_injection.py --scan-seeds 5 --json closure.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
for _p in (os.path.join(_ROOT, "omnifold_nn"), _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)


def structural_floor(acceptance, r_inject, niter):
    """Closed-form worst-case term-1 bound: (1-a)^k * (R-1)/R. See the module docstring."""
    a, R, k = float(acceptance), float(r_inject), int(niter)
    if R <= 0:
        raise ValueError(f"r_inject must be > 0 (got {R})")
    return (1.0 - a) ** k * abs(R - 1.0) / R


def expected_push(acceptance, r_inject, niter):
    """Closed-form worst-case recovered push: R - (1-a)^k * (R-1)."""
    a, R, k = float(acceptance), float(r_inject), int(niter)
    return R - (1.0 - a) ** k * (R - 1.0)


def _build_sample(n_events, acceptance, smear, seed):
    """Signal MC (truth + smeared reco + acceptance mask) and an independent measured draw.

    The measured sample is drawn from the SAME underlying distribution as the MC reco, so the ONLY
    difference between the two classes is the total rate. That is the point: a shape-sensitive
    estimator has nothing to latch onto, and anything it recovers it recovered from the rate.
    """
    rng = np.random.default_rng(seed)
    gen = rng.normal(0.0, 1.0, (n_events, 2)).astype(np.float32)
    reco = (gen + rng.normal(0.0, smear, (n_events, 2))).astype(np.float32)
    pass_reco = rng.random(n_events) < acceptance
    pass_gen = np.ones(n_events, bool)
    measured = (rng.normal(0.0, 1.0, (n_events, 2))
                + rng.normal(0.0, smear, (n_events, 2))).astype(np.float32)
    return gen, reco, pass_reco, pass_gen, measured


def run_one(*, measured_normalization, n_events, acceptance, r_inject, niter, epochs, smear,
            seed, workdir, tag):
    """Train one configuration and return its reco-level fold-forward ratio.

    `measured_normalization` is the whole experiment: 1e6*R is the B1-corrected configuration,
    1e6 is the pre-B1 broken one. Everything else is held fixed between the two arms.
    """
    import tensorflow as tf
    from omnifold import MLP, MultiFold, DataLoader

    tf.keras.utils.set_random_seed(int(seed))
    gen, reco, pass_reco, pass_gen, measured = _build_sample(n_events, acceptance, smear, seed)
    mc = DataLoader(reco=reco, gen=gen, pass_reco=pass_reco, pass_gen=pass_gen,
                    weight=np.ones(n_events, np.float32), normalize=True,
                    normalization_factor=1.0e6)
    data = DataLoader(reco=measured, weight=np.ones(n_events, np.float32), normalize=True,
                      normalization_factor=float(measured_normalization))

    # The class ratio the engine actually sees at iteration 0 -- the quantity B1 is about.
    w_mc = np.asarray(mc.weight, np.float64)
    w_data = np.asarray(data.weight, np.float64)
    class_ratio_seen = float(w_data[np.asarray(data.pass_reco).astype(bool)].sum()
                             / w_mc[np.asarray(mc.pass_reco).astype(bool)].sum())

    of = MultiFold(tag, MLP(2), MLP(2), data, mc, niter=int(niter), epochs=int(epochs),
                   batch_size=512, weights_folder=os.path.join(workdir, f"w_{tag}"),
                   log_folder=workdir, verbose=False)
    of.Unfold()

    push = np.asarray(of.weights_push, np.float64)
    mask = np.asarray(mc.pass_reco).astype(bool)
    ratio = float((w_mc[mask] * push[mask]).sum() / w_mc[mask].sum())
    return {"measured_normalization": float(measured_normalization),
            "step1_class_ratio_seen": class_ratio_seen,
            "fold_forward_reco_ratio": ratio,
            "dev_from_R": abs(ratio / float(r_inject) - 1.0),
            "dev_from_1": abs(ratio - 1.0),
            "nearer_R_than_1": abs(ratio - float(r_inject)) < abs(ratio - 1.0)}


def run_closure(args, seed):
    import tempfile
    R = float(args.r_inject)
    with tempfile.TemporaryDirectory() as td:
        corrected = run_one(measured_normalization=1.0e6 * R, n_events=args.n_events,
                            acceptance=args.acceptance, r_inject=R, niter=args.niter,
                            epochs=args.epochs, smear=args.smear, seed=seed, workdir=td,
                            tag=f"b1_corrected_s{seed}")
        broken = run_one(measured_normalization=1.0e6, n_events=args.n_events,
                         acceptance=args.acceptance, r_inject=R, niter=args.niter,
                         epochs=args.epochs, smear=args.smear, seed=seed, workdir=td,
                         tag=f"b1_broken_s{seed}")

    floor = structural_floor(args.acceptance, R, args.niter)
    signal = abs(R - 1.0) / R
    rep = {
        "seed": int(seed), "r_inject": R, "acceptance": float(args.acceptance),
        "niter": int(args.niter), "epochs": int(args.epochs), "n_events": int(args.n_events),
        "corrected": corrected, "broken": broken,
        "structural_floor_worst_case": floor,
        "expected_push_worst_case": expected_push(args.acceptance, R, args.niter),
        "defect_signal_size": signal,
        "tolerance_used": float(args.tolerance),
    }
    # --- the closure verdict ---
    # The corrected arm must recover the rate; the broken arm must NOT. Both halves are required:
    # without the second, this only shows the pipeline runs.
    rep["corrected_recovers"] = bool(corrected["dev_from_R"] <= args.tolerance
                                     and corrected["nearer_R_than_1"])
    rep["broken_fails_to_recover"] = bool(not (broken["dev_from_R"] <= args.tolerance
                                               and broken["nearer_R_than_1"]))
    # Sanity: the corrected arm must actually be BETTER, not merely inside tolerance by luck.
    rep["corrected_beats_broken"] = bool(corrected["dev_from_R"] < broken["dev_from_R"])
    rep["verdict"] = ("PASS" if (rep["corrected_recovers"] and rep["broken_fails_to_recover"]
                                 and rep["corrected_beats_broken"]) else "FAIL")
    return rep


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--r-inject", type=float, default=1.135,
                    help="injected truth-level rate change (default 1.135, the recoil-only "
                         "estimate; use the MEASURED R on 08-03 to size the real tolerance)")
    ap.add_argument("--acceptance", type=float, default=0.621,
                    help="reco acceptance fraction (default = the nominal row fraction 0.621)")
    ap.add_argument("--niter", type=int, default=2, help="OmniFold iterations (nominal: 2)")
    ap.add_argument("--epochs", type=int, default=8, help="epochs per step (nominal: 8)")
    ap.add_argument("--n-events", type=int, default=60000,
                    help="past the artifact-dominated regime -- see the gradient-step confound "
                         "in the module docstring before lowering this")
    ap.add_argument("--smear", type=float, default=0.15, help="reco smearing width")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--scan-seeds", type=int, default=0,
                    help="run this many consecutive seeds and report the spread (term 3)")
    ap.add_argument("--tolerance", type=float, default=0.05,
                    help="fold-forward deviation tolerance under test (default: the provisional "
                         "value frozen in validate_pet_nominal_gate4.py)")
    ap.add_argument("--json", dest="json_out", default=None)
    args = ap.parse_args(argv)

    if not (0.0 < args.acceptance <= 1.0):
        print("[b1-closure][FAIL] --acceptance must be in (0, 1]", file=sys.stderr)
        return 2
    if args.r_inject <= 0.0:
        print("[b1-closure][FAIL] --r-inject must be > 0", file=sys.stderr)
        return 2

    seeds = ([args.seed] if args.scan_seeds <= 0
             else [args.seed + i for i in range(args.scan_seeds)])
    reps = [run_closure(args, s) for s in seeds]
    verdict = all(r["verdict"] == "PASS" for r in reps)

    print(f"\n  B1 rate-injection closure -- R_inject={args.r_inject}  acceptance="
          f"{args.acceptance}  niter={args.niter}  epochs={args.epochs}  N={args.n_events:,}")
    print(f"  worst-case structural floor (1-a)^k*(R-1)/R = {reps[0]['structural_floor_worst_case']:.4%}"
          f"   defect signal (R-1)/R = {reps[0]['defect_signal_size']:.4%}"
          f"   tolerance = {args.tolerance:.4%}")
    print(f"\n  {'seed':>5} {'arm':>10} {'class ratio':>12} {'fold-fwd':>10} "
          f"{'dev from R':>11} {'recovers':>9}")
    for r in reps:
        for arm in ("corrected", "broken"):
            a = r[arm]
            rec = (r["corrected_recovers"] if arm == "corrected"
                   else not r["broken_fails_to_recover"])
            print(f"  {r['seed']:5d} {arm:>10} {a['step1_class_ratio_seen']:12.6f} "
                  f"{a['fold_forward_reco_ratio']:10.6f} {a['dev_from_R']:11.4%} {str(rec):>9}")
    if len(reps) > 1:
        spread = [r["corrected"]["fold_forward_reco_ratio"] for r in reps]
        print(f"\n  term 3 (subsample sampling): corrected fold-forward ratio over "
              f"{len(reps)} seeds  mean={np.mean(spread):.6f}  std={np.std(spread):.6f}")

    print(f"\n  corrected recovers the injected rate : "
          f"{all(r['corrected_recovers'] for r in reps)}")
    print(f"  broken does NOT recover it           : "
          f"{all(r['broken_fails_to_recover'] for r in reps)}")
    print(f"  corrected strictly beats broken      : "
          f"{all(r['corrected_beats_broken'] for r in reps)}")
    print(f"\n  VERDICT: {'PASS' if verdict else 'FAIL'}\n")

    if args.json_out:
        with open(args.json_out, "w") as fh:
            json.dump({"verdict": "PASS" if verdict else "FAIL", "runs": reps}, fh, indent=2,
                      sort_keys=True)
        print(f"  wrote {args.json_out}\n")
    return 0 if verdict else 1


if __name__ == "__main__":
    raise SystemExit(main())
