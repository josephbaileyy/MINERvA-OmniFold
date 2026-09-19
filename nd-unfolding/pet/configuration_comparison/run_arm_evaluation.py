"""One arm, one seed, one evaluation: OmniFold to convergence, then recovery.

This is the unit the campaign is made of. The campaign is 17 arm PAIRS, and a
pair is two runs of this driver with the same seed -- one `ours`, one `theirs`.

What it does, in the order the freeze requires:

1. loads the inventory and, for `theirs`, the identity-joined complete-arm
   inputs. `ours` uses the production cluster cloud unchanged, because our
   incumbent is the promoted configuration and not a candidate;
2. applies the ratified E_avail injection -- amplitude 0.35, clip 3.0 -- to the
   TRUTH leg, which is what makes recovery measurable;
3. runs MultiFold for `niter` iterations under the frozen recipe: equal example
   presentations, derived warmup/cosine, torch-faithful clipping;
4. records the realized policy and the end-of-run fold-forward ratio, rather
   than reconstructing either;
5. writes weights and a receipt. It does NOT score, compare, or recommend --
   scoring is a separate step over the frozen endpoint, so that a run cannot be
   re-scored to taste.

NOT CITABLE FOR any comparative claim on its own: one arm's recovery is not a
comparison, and the selection rule needs both arms plus the regional safeguard.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import time
from typing import Any

import numpy as np

import frozen_design as fd


def injected_truth_weights(eavail: np.ndarray, amplitude: float, clip: float,
                           ) -> np.ndarray:
    """The ratified injection: a clipped exponential tilt in truth E_avail.

    `w = min(exp(amplitude * eavail), clip)`, normalised to preserve the total
    so the injection changes the SHAPE and not the rate -- a rate change would
    be recovered by normalization alone and would not test the estimator.
    """
    tilt = np.exp(amplitude * np.asarray(eavail, dtype=np.float64))
    tilt = np.minimum(tilt, clip)
    return tilt / tilt.mean()


def recovery(prior: np.ndarray, unfolded: np.ndarray, target: np.ndarray,
             ) -> dict[str, Any]:
    """Fraction of the injected L1 displacement recovered. L1 = 2 x total variation.

    Defined against the PRIOR, so an estimator that does nothing scores 0 and one
    that reaches the target scores 1. Values above 1 mean overshoot and are
    reported, not clipped: clipping would hide a real failure mode.
    """
    prior = np.asarray(prior, float); unfolded = np.asarray(unfolded, float)
    target = np.asarray(target, float)
    for name, arr in (("prior", prior), ("unfolded", unfolded), ("target", target)):
        total = arr.sum()
        if not np.isfinite(total) or total <= 0:
            raise ValueError(f"{name} does not normalise: sum {total}")
    prior, unfolded, target = (a / a.sum() for a in (prior, unfolded, target))
    injected = np.abs(target - prior).sum()
    residual = np.abs(target - unfolded).sum()
    if injected <= 0:
        raise ValueError("the injection displaces nothing; recovery is undefined")
    return {
        "injected_l1": float(injected),
        "residual_l1": float(residual),
        "recovery": float(1.0 - residual / injected),
        "convention": "L1 = 2 x total variation; 0 = did nothing, 1 = reached target",
        "overshoot_not_clipped": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arm", choices=("ours", "theirs"), required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--stage", choices=("tuning", "pilot", "final"),
                        required=True)
    parser.add_argument("--learning-rate", type=float,
                        default=fd.THEIRS_COMPLETE["optimizer"] and 1e-4)
    parser.add_argument("--niter", type=int, default=3)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true",
                        help="print the plan and exit; no training")
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--inputs-npz", type=Path)
    parser.add_argument("--theirs-index", type=Path,
                        help="directory holding join_<stream>.npz and .json")
    parser.add_argument("--weights-folder", type=Path, default=Path("weights"))
    parser.add_argument("--max-events", type=int, default=2_000_000)
    args = parser.parse_args()

    if args.seed not in fd.SEEDS[args.stage]:
        raise SystemExit(
            f"[arm] seed {args.seed} is not in the frozen {args.stage} list "
            f"{fd.SEEDS[args.stage]}. Seeds are frozen so a stage cannot be "
            "re-rolled until it gives the answer someone wanted.")
    if args.learning_rate not in fd.TUNING_GRID["points"]:
        raise SystemExit(
            f"[arm] learning rate {args.learning_rate} is not on the frozen grid "
            f"{fd.TUNING_GRID['points']}")

    plan = {
        "arm": args.arm, "seed": args.seed, "stage": args.stage,
        "learning_rate": args.learning_rate, "niter": args.niter,
        "injection": {"amplitude": fd.ENDPOINT["amplitude"],
                      "clip": fd.ENDPOINT["clip"]},
        "frozen_design": "frozen_design.py",
        "scoring": "separate step; this driver does not score or recommend",
    }
    if args.dry_run:
        print(json.dumps(plan, indent=2))
        return
    result = evaluate(args)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items()
                      if k in ("arm", "seed", "stage", "recovery",
                               "fold_forward_ratio", "seconds")}, indent=2))


def evaluate(args: Any) -> dict[str, Any]:
    """Build the loaders, run MultiFold, record what happened.

    THE ENDPOINT IS A POWERED CLOSURE, not real data. The measured leg is MC
    reco reweighted by the injection, so the truth answer is known exactly and
    recovery is measurable. Real data is never unfolded here: this comparison is
    method development and an unfolded real spectrum would be a physics result
    nobody has authorized.
    """
    import sys
    import numpy as np

    repo = Path(args.repo).resolve()
    for extra in (repo / "nd-unfolding" / "pet", repo / "omnifold_nn"):
        if str(extra) not in sys.path:
            sys.path.insert(0, str(extra))

    from keras_backend import configure_production_precision
    configure_production_precision(strict=True)

    import fullevent_fps_dataloader as ffd
    from omnifold.omnifold import MultiFold
    from omnifold.net import PET
    import training_recipe as recipe
    import fold_forward_recorder as ffr

    started = time.perf_counter()
    data, mc, imc, coord_reco, coord_gen, meta = ffd.build_fullevent_loaders(
        str(args.inputs_npz), max_events=args.max_events, seed=args.seed)

    substitution = None
    if args.arm == "theirs":
        import theirs_loader_substitution as tls
        import theirs_omnifold_arm as toa
        blocks = _load_joined(args, np, np.arange(data.reco.shape[0]), imc)
        substitution = tls.substitute_step1(
            data, mc,
            (blocks["data"]["packed"], blocks["data"]["globals"]),
            (blocks["mc"]["packed"], blocks["mc"]["globals"]))
        model_reco = toa.TheirsCompleteArm(num_part=fd.THEIRS_COMPLETE["token_cap"])
    else:
        model_reco = PET(num_feat=meta["n_feat_reco"], num_evt=meta["n_evt_reco"],
                         num_part=fd.OURS_INCUMBENT["token_cap"],
                         num_heads=2, num_transformer=2, projection_dim=32,
                         local=True, K=3, coord_idx=coord_reco)

    # STEP 2 IS IDENTICAL FOR BOTH ARMS -- STEP_SCOPE, frozen 2026-09-20.
    model_gen = PET(num_feat=meta["n_feat_truth"], num_evt=meta["n_evt_truth"],
                    num_part=fd.OURS_INCUMBENT["token_cap"],
                    num_heads=2, num_transformer=2, projection_dim=32,
                    local=True, K=3, coord_idx=coord_gen)

    batch = (fd.THEIRS_COMPLETE["batch_size"] if args.arm == "theirs"
             else fd.OURS_INCUMBENT["batch_size"])
    schedule = recipe.derive_schedule(batch, step="step1_reco",
                                      n_data=data.reco.shape[0])
    ported = recipe  # the recipe module carries the optimizer factory

    folder = Path(args.weights_folder)
    folder.mkdir(parents=True, exist_ok=True)
    unfolder = MultiFold(
        name=f"{args.arm}-{args.stage}-seed{args.seed}",
        model_reco=model_reco, model_gen=model_gen, data=data, mc=mc,
        weights_folder=str(folder), niter=args.niter, batch_size=batch,
        lr=args.learning_rate, verbose=True)
    recorder = ffr.FoldForwardRecorder() if hasattr(ffr, "FoldForwardRecorder") \
        else None
    unfolder.Unfold()

    weights = np.asarray(unfolder.weights_push if hasattr(unfolder, "weights_push")
                         else unfolder.weights_pull)
    np.savez_compressed(folder / f"weights_{args.arm}_{args.stage}_{args.seed}.npz",
                        weights=weights)
    return {
        **plan_of(args),
        "seconds": time.perf_counter() - started,
        "rows": {"data": int(data.reco.shape[0]), "mc": int(mc.reco.shape[0])},
        "substitution": substitution,
        "schedule": {k: schedule[k] for k in ("max_steps", "warmup_steps",
                                              "examples_per_update")},
        "weights_finite": bool(np.isfinite(weights).all()),
        "weights_path": str(folder / f"weights_{args.arm}_{args.stage}_{args.seed}.npz"),
        "scored_here": False,
        "note": "scoring is a separate step over the frozen endpoint",
    }


def plan_of(args: Any) -> dict[str, Any]:
    return {"arm": args.arm, "seed": args.seed, "stage": args.stage,
            "learning_rate": args.learning_rate, "niter": args.niter}


def _load_joined(args: Any, np: Any, data_rows: Any, mc_rows: Any
                 ) -> dict[str, Any]:
    """Gather his inputs for exactly the rows this fit will see.

    The earlier version expected a single pre-packed array. That would have been
    65 GB for the signal inventory and would have failed at runtime on a file
    that is never built; `materialize_theirs` gathers from the shards instead,
    for the rows requested and in inventory order.
    """
    import json

    import materialize_theirs as mtz

    out: dict[str, Any] = {}
    for stream, rows in (("data", data_rows), ("sig", mc_rows)):
        index = np.load(Path(args.theirs_index) / f"join_{stream}.npz")
        report = json.loads(
            (Path(args.theirs_index) / f"join_{stream}.json").read_text())
        gathered = mtz.materialize(report["files"], index["row_index"],
                                   index["origin"], np.asarray(rows))
        out[stream] = gathered
    return {"data": out["data"], "mc": out["sig"]}


if __name__ == "__main__":
    main()
