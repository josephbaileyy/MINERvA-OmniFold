"""Anchors on the historical endpoint: what the score gives when the push IS the injected function.

ORACLE TRUTH-LEVEL PUSH -- NOT AN ESTIMATOR AND NOT A DETECTOR-LEVEL BOUND. The pseudo-data are
half A's events reweighted by the tilt; the prior is half B. A push equal to the injected tilt
function evaluated on half B's own truth E_avail is what an estimator that learned the truth-level
density ratio EXACTLY would produce. Its recovery is below 1 only because half A and half B are
different finite samples: it is the closure's own sampling-noise ceiling for a push that is a
function of truth E_avail, and it scales every other number in this lane.

Two versions: the tilt function exactly as injected (half A's p50 / IQR / normalization, from the
historical `clipped_exponential_tilt` spec; the one-line evaluation is checked to reproduce the
recorded `tilt_a` bit for bit), and the historical function re-fit on half B's rows.
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np

import run_ibu
import scalar_common as scm


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--populations", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    started = time.perf_counter()
    sources = scm.verify_historical_sources()
    mods = scm.historical_modules()
    cp, fd = mods["cp"], mods["fd"]
    amp, clip = float(fd.ENDPOINT["amplitude"]), float(fd.ENDPOINT["clip"])

    pop = scm.load_populations(args.populations)
    endpoint = scm.endpoint_from_populations(pop)
    pga, pgb = pop["a_pass_truth"].astype(bool), pop["b_pass_truth"].astype(bool)
    ea, eb = pop["a_truth"][:, 2], pop["b_truth"][:, 2]

    tilt_a, spec_a = cp.clipped_exponential_tilt(ea[pga], amplitude=amp, clip_z=clip)

    def evaluate(x: np.ndarray, spec: dict) -> np.ndarray:
        # the spec's own stated form: exp(A*clip((x-p50)/IQR, -Z, +Z)) / mean(...)
        z = np.clip((x - spec["pt_p50"]) / spec["pt_iqr"], -spec["clip_z"], spec["clip_z"])
        return np.exp(spec["amplitude"] * z) / spec["pre_normalization_mean"]

    check = float(np.abs(evaluate(ea[pga], spec_a) - pop["a_tilt"][pga]).max())
    if check > 1e-12:
        raise SystemExit(f"[anchors] the spec evaluation does not reproduce tilt_a ({check})")
    push_a_spec = np.ones(pgb.size)
    push_a_spec[pgb] = evaluate(eb[pgb], spec_a)
    tilt_b, spec_b = cp.clipped_exponential_tilt(eb[pgb], amplitude=amp, clip_z=clip)
    push_b_spec = np.ones(pgb.size)
    push_b_spec[pgb] = tilt_b

    pushes = {
        "oracle_truth_push_half_A_spec": push_a_spec,
        "oracle_truth_push_half_B_spec": push_b_spec,
        "identity_push": np.ones(pgb.size),
        "historical_ours_seed127": pop["hist_push_ours127"],
        "historical_theirs_seed127": pop["hist_push_theirs127"],
    }
    scores = {name: scm.score_push(endpoint, push, run_ibu.SCOREABLE, run_ibu.INFORMATIONAL)
              for name, push in pushes.items()}
    for name, sc in scores.items():
        print(f"[anchors] {name:32s} R={sc['recovery']:.4f} "
              + " ".join(f"{k}={v:.4f}" for k, v in sc["recovery_by_region"].items())
              + f" proj={sc['aggregate']['overshoot_projection']:.3f}")
    payload = {
        "schema": "phase-b1-anchors/1",
        "label": ("ORACLE truth-level pushes are the injected function itself; they measure the "
                  "closure's sampling-noise ceiling for a truth-E_avail push, not an estimator "
                  "and not a detector-level bound"),
        "commit": scm.repo_commit(),
        "historical_sources": sources,
        "inputs": {"populations_npz": str(args.populations),
                   "populations_npz_sha256": scm.sha256_file(args.populations)},
        "spec_half_A": spec_a, "spec_half_B": spec_b,
        "spec_evaluation_reproduces_recorded_tilt_a_max_abs_dev": check,
        "scores": scores,
        "seconds": time.perf_counter() - started,
    }
    scm.write_json(args.output, payload, compact=True)


if __name__ == "__main__":
    main()
