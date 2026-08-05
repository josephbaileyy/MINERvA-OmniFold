"""SUBMISSION-SIDE GATE for the D2 powered truth-reweight closure.

Two of `closure_powered_truth_reweight.py`'s three acceptance criteria do not involve the estimator
at all:

    gap      = L1(h_prior_B, h_target_A)    w_truth, the seed-7 halves, the closed-form tilt
    floor    = L1(h_prior_B, h_untilt_A)    w_truth, the seed-7 halves
    residual = L1(h_unfold_B, h_target_A)   ALSO `weights_push` <- the ~8-GPU-hour MultiFold run

`gap` and `floor` are deterministic functions of the dump plus two seeds. Nothing the training does
can move them. So a run whose `gap < GAP_MIN` or `floor/gap > FLOOR_OVER_GAP_MAX` is a guaranteed
FAIL that is knowable BEFORE the GPU is allocated, and the only thing 12 queued hours buy in that
case is a slower way to find out. This script computes them in ~9 s on a login node and fails closed.

WHY THIS EXISTS, measured 2026-08-05. The predeclared run was submitted (slurm 56355818) on the
strength of a GPU smoke that exited 3 -- the driver's `return 0 if ok else 3`, i.e. it completed the
full protocol and reported verdict FAIL. At the smoke's half-size of 20,000 that FAIL is expected and
carries no information: `floor` scales as 1/sqrt(n), so shrinking the halves 100x inflates floor/gap
by ~10x and the criterion fails on sampling noise alone. But the smoke's report was not retained, so
the one question that mattered -- was it the noise-driven floor/gap criterion (benign, scales away at
2M) or the size-invariant `gap` criterion (fatal at any size) -- could not be answered from the
record. This gate answers it directly, at the real configuration, and WRITES THE RECEIPT.

COST. Reads only `w_truth`, `pass_truth` and `truth_scalars` out of the zip -- about 1 GB
uncompressed. It never touches `part_reco`/`part_gen`, which is what makes it seconds instead of the
minutes and 12.84 GiB the full loader needs. No TensorFlow: the driver's module-level imports are
numpy-only (its `import tensorflow` is inside `main`), so importing it here loads no engine and
allocates no GPU.

ONE IMPLEMENTATION, NOT TWO. The tilt, the spectra, the L1 and the split come from
`closure_powered_truth_reweight` by import, for the reason its own docstring gives at
`clipped_exponential_tilt`: a second copy is a second thing to drift. The thresholds come from the
same module, so a reviewed change to the protocol moves the gate with it.

THE ONE DUPLICATION, AND HOW IT IS KEPT HONEST. The `imc` subsample draw
(`sort(default_rng(subsample_seed).choice(N, max_events))`) is reproduced here instead of imported,
because the only way to get it from the loader is to CALL `build_fullevent_loaders`, which imports
TensorFlow and decompresses both point clouds -- exactly the cost this gate exists to avoid. It
cannot be factored into a shared helper either: `fullevent_fps_dataloader.py` is hash-pinned by the
Gate-2 runtime receipt, so editing it for a refactor invalidates that receipt. The duplication is
therefore load-bearing and unavoidable, which means it must be MEASURED rather than trusted:
`sbatch_powered_closure.sh` cross-checks this receipt's `gap`/`floor` against the finished driver
report's `metrics.gap`/`metrics.floor` on every run, and fails the run if they diverge. A wrong
subsample or a wrong tilt here moves those numbers by percent-level or more and is caught; float32
normalization round-off in the engine's copy of the weights does not (see PREFLIGHT_XCHECK_RTOL in
the launcher).

EXIT CODES, mirroring the driver so a collector can read both the same way:
    0  the training-independent criteria are met -- the GPU run is worth allocating
    3  they are NOT met -- the run would FAIL for a reason training cannot fix
    1  the gate could not be evaluated (missing member, bad row budget, ...) -- fail closed
"""
import argparse
import json
import os
import sys
import zipfile

import numpy as np
import numpy.lib.format as npf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import fullevent_fps_dataloader as fe                          # noqa: E402  numpy-only at import
from closure_powered_truth_reweight import (                   # noqa: E402  ditto
    FLOOR_OVER_GAP_MAX,
    GAP_MIN,
    HALF_SIZE,
    RESIDUAL_OVER_GAP_MAX,
    SPLIT_SEED,
    TILT_AMPLITUDE,
    TILT_CLIP_Z,
    clipped_exponential_tilt,
    deterministic_halves,
    l1,
    unit_spectrum,
)
from train_fullevent_nominal import NOMINAL_SEED_POLICY        # noqa: E402  ditto

RECEIPT_SCHEMA = "powered-closure-preflight-v1"


def read_member(z, name, rows=None):
    """One .npy member out of the dump, optionally subsampled.

    Reads through `numpy.lib.format` rather than `np.load(npz)[key]` for the same reason the driver
    does: an NpzFile materializes the whole member before any indexing, and the members this gate
    avoids are the 7 GB and 12 GB point clouds. Naming them explicitly is what keeps them unread.
    """
    if name + ".npy" not in z.namelist():
        raise SystemExit(f"[preflight] dump has no member {name!r} (fail closed)")
    with z.open(name + ".npy") as fh:
        a = npf.read_array(fh, allow_pickle=False)
    return a if rows is None else a[rows]


def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--inputs", required=True, help="the G2 full-event dump the run will train on")
    p.add_argument("--json", required=True, help="write the machine-readable receipt here")
    # Defaults are the driver's module constants, so the gate measures what the run will actually do.
    # Overriding them here without overriding the driver identically is how a gate goes vacuous, so
    # the receipt records every one of them and the launcher passes NONE.
    p.add_argument("--half-size", type=int, default=HALF_SIZE)
    p.add_argument("--amplitude", type=float, default=TILT_AMPLITUDE)
    p.add_argument("--clip-z", type=float, default=TILT_CLIP_Z)
    p.add_argument("--split-seed", type=int, default=SPLIT_SEED)
    p.add_argument("--max-events", type=int, default=None,
                   help="rows to load; defaults to 2*half-size, as in the driver")
    p.add_argument("--inputs-sha256", default=None,
                   help="digest of --inputs, if the caller already computed it. Recorded verbatim so "
                        "the receipt is self-standing without this gate re-hashing 9.9 GB.")
    return p.parse_args(argv)


def main(argv=None):
    a = parse_args(argv)
    pol = NOMINAL_SEED_POLICY
    need = int(a.max_events if a.max_events is not None else 2 * a.half_size)
    subsample_seed = int(pol["subsample_seed"])

    with zipfile.ZipFile(a.inputs) as z:
        w_full = read_member(z, "w_truth")
        n_dump = int(w_full.shape[0])
        # THE DUPLICATED DRAW -- fullevent_fps_dataloader.build_fullevent_loaders, `if max_events is
        # not None`. Kept character-for-character equivalent on purpose; the launcher's post-run
        # cross-check is what proves it still is.
        imc = np.sort(np.random.default_rng(subsample_seed).choice(
            n_dump, min(need, n_dump), replace=False))
        # float64 for the spectra arithmetic, where precision is free. The engine's own copy is
        # float32 by contract (see the driver's dtype note); that difference is why the launcher's
        # cross-check is a relative tolerance and not an equality.
        w_truth = np.asarray(w_full[imc], dtype=np.float64)
        del w_full
        pass_truth = read_member(z, "pass_truth", imc).astype(bool)
        truth_scalars = read_member(z, "truth_scalars", imc)

    pt_t = truth_scalars[:, fe.SCALAR_COLS["pt"]].astype(np.float64)
    pp_t = truth_scalars[:, fe.SCALAR_COLS["pparallel"]].astype(np.float64)
    del truth_scalars

    # Raises (exit 1) if the dump cannot supply two disjoint halves -- the driver's own row budget,
    # enforced here so that failure costs seconds instead of a queue slot plus a 9.9 GB load.
    n_rows = int(imc.size)
    ia, ib = deterministic_halves(n_rows, half=int(a.half_size), seed=int(a.split_seed))

    pg_a = pass_truth[ia]
    tilt_a = np.ones(ia.size, dtype=np.float64)
    tilt_on_truth, tilt_spec = clipped_exponential_tilt(
        pt_t[ia][pg_a], amplitude=float(a.amplitude), clip_z=float(a.clip_z))
    tilt_a[pg_a] = tilt_on_truth

    e_pt, e_pp = fe.CANONICAL_PT_EDGES, fe.CANONICAL_PPARALLEL_EDGES
    mb, ma = pass_truth[ib], pg_a
    h_prior = unit_spectrum(pt_t[ib][mb], pp_t[ib][mb], w_truth[ib][mb], e_pt, e_pp)
    h_target = unit_spectrum(pt_t[ia][ma], pp_t[ia][ma], (w_truth[ia] * tilt_a)[ma], e_pt, e_pp)
    h_untilt = unit_spectrum(pt_t[ia][ma], pp_t[ia][ma], w_truth[ia][ma], e_pt, e_pp)

    gap, floor = l1(h_prior, h_target), l1(h_prior, h_untilt)
    fog = (floor / gap) if gap > 0 else None
    gap_ok = bool(gap >= GAP_MIN)
    fog_ok = bool(fog is not None and fog <= FLOOR_OVER_GAP_MAX)
    ok = gap_ok and fog_ok

    # Diagnostic, not a gate. The absolute residual the run must reach is RESIDUAL_OVER_GAP_MAX*gap;
    # `floor` is the L1 two independent resamples of the SAME prior differ by, so it is the scale
    # below which "recovery" stops being distinguishable from a resample. The ratio says how much
    # room the estimator actually has. It cannot come out <= 1 while floor/gap passes, because
    # FLOOR_OVER_GAP_MAX < RESIDUAL_OVER_GAP_MAX makes that structural -- reported so that a future
    # loosening of either threshold shows up here instead of silently making the test unpassable.
    budget = RESIDUAL_OVER_GAP_MAX * gap
    headroom = (budget / floor) if floor > 0 else None

    receipt = {
        "receipt_schema": RECEIPT_SCHEMA,
        "gate": "powered-closure training-independent criteria",
        "verdict": "PASS" if ok else "FAIL",
        "criteria_are_training_independent": True,
        "metrics": {"gap": gap, "floor": floor, "floor_over_gap": fog,
                    "residual_budget_abs": budget, "budget_over_floor": headroom},
        "criteria": {"gap_min": GAP_MIN, "floor_over_gap_max": FLOOR_OVER_GAP_MAX,
                     "residual_over_gap_max": RESIDUAL_OVER_GAP_MAX},
        "checks": {"gap_at_or_above_min": gap_ok, "floor_over_gap_at_or_below_max": fog_ok},
        "spectra": {"h_prior": [float(x) for x in h_prior],
                    "h_target": [float(x) for x in h_target],
                    "h_untilted": [float(x) for x in h_untilt],
                    "bin_order": "pt-major row-major: cell = i_pt * n_pparallel_bins + i_pparallel",
                    "n_cells": int(h_prior.size)},
        "injection": tilt_spec,
        "samples": {"half_size": int(a.half_size), "split_seed": int(a.split_seed),
                    "subsample_seed": subsample_seed, "max_events": need,
                    "n_dump_rows": n_dump, "n_loaded": n_rows,
                    "n_truth_a": int(ma.sum()), "n_truth_b": int(mb.sum())},
        "source": {"inputs": os.path.abspath(a.inputs),
                   "inputs_size": int(os.path.getsize(a.inputs)),
                   "inputs_sha256": a.inputs_sha256,
                   "inputs_sha256_source": ("caller-supplied" if a.inputs_sha256
                                            else "not computed by this gate")},
        "members_read": ["w_truth", "pass_truth", "truth_scalars"],
        "members_deliberately_unread": ["part_reco", "part_gen", "measured_pc"],
        "not_evaluated_here": {
            "residual": "needs weights_push from the MultiFold run; this gate cannot bound it",
            "verdict_is_not_the_closure_verdict": True},
    }
    with open(a.json, "w") as fh:
        json.dump(receipt, fh, indent=2)
        fh.write("\n")

    print(f"[preflight] gap={gap:.4f} (min {GAP_MIN}) floor={floor:.4f} "
          f"floor/gap={fog:.4f} (max {FLOOR_OVER_GAP_MAX}) "
          f"residual_budget={budget:.4f} budget/floor={headroom:.2f}x -> "
          f"{'PASS' if ok else 'FAIL'}")
    print(f"[preflight] wrote receipt {a.json}")
    if not ok:
        why = []
        if not gap_ok:
            why.append(f"gap {gap:.4f} < {GAP_MIN} -- the injection is too weak to be recoverable "
                       f"at this configuration; training cannot fix this")
        if not fog_ok:
            why.append(f"floor/gap {fog:.4f} > {FLOOR_OVER_GAP_MAX} -- the A/B sampling floor eats "
                       f"too much of the injected signal; a larger half-size shrinks it as "
                       f"1/sqrt(n), training does not")
        for w in why:
            print(f"[preflight][FAIL] {w}", file=sys.stderr)
    return 0 if ok else 3


if __name__ == "__main__":
    raise SystemExit(main())
