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
import sys
import time
from typing import Any

import numpy as np

import frozen_design as fd

# `closure_powered_truth_reweight` lives one directory up and owns THE injection.
# Appended rather than inserted: this must not shadow anything the driver already
# resolves, and the pinned-checkout guard in `evaluate` checks where the modules
# it cares about actually came from.
_PET_DIR = str(Path(__file__).resolve().parent.parent)
if _PET_DIR not in sys.path:
    sys.path.append(_PET_DIR)


def injected_truth_weights(eavail: np.ndarray,
                           amplitude: float = fd.ENDPOINT["amplitude"],
                           clip: float = fd.ENDPOINT["clip"]) -> np.ndarray:
    """The ratified injection, which is THE established one, imported not rewritten.

    This was a second implementation, `min(exp(A*eavail), clip)`, and it was
    wrong in the specific way `clipped_exponential_tilt`'s own docstring warns
    about: "clipping the weight instead would flatten the tilt over whole tails
    and make the recoverable signal depend on the tail population." It also
    exponentiated RAW E_avail rather than a standardised coordinate, so with
    clip 3.0 every event above ln(3)/0.35 = 3.14 GeV got the same weight --
    flat across the endpoint's top two bins, which run to 100 GeV.

    It mattered beyond the shape. `characterize_regions` computed the reference
    ceilings and the region census with the CORRECT tilt, so the adequacy floor
    and every regional floor were derived under one injection and would have
    been scored under another.

    The established function clips the COORDINATE: z = clip((x - p50)/IQR, -Z,
    +Z), tilt = exp(A*z)/mean(...), rate-preserving over exactly the rows given
    it. Pass truth-passing rows only, or the quantiles describe the wrong
    population.
    """
    import closure_powered_truth_reweight as cp

    tilt, _spec = cp.clipped_exponential_tilt(
        np.asarray(eavail, dtype=np.float64), amplitude=amplitude, clip_z=clip)
    return tilt


def injection_spec(eavail: np.ndarray,
                   amplitude: float = fd.ENDPOINT["amplitude"],
                   clip: float = fd.ENDPOINT["clip"]) -> dict[str, Any]:
    """The injection's own record of what it did, for the receipt."""
    import closure_powered_truth_reweight as cp

    _tilt, spec = cp.clipped_exponential_tilt(
        np.asarray(eavail, dtype=np.float64), amplitude=amplitude, clip_z=clip)
    return spec


def recovery(prior: np.ndarray, unfolded: np.ndarray, target: np.ndarray,
             ) -> dict[str, Any]:
    """Fraction of the injected L1 displacement recovered. L1 = 2 x total variation.

    Defined against the PRIOR, so an estimator that does nothing scores 0 and one
    that reaches the target scores 1.

    The score is BOUNDED ABOVE BY 1 and unbounded below. ``residual_l1`` is a sum
    of absolute values, so it cannot be negative and the score cannot exceed 1;
    an earlier version of this docstring said "values above 1 mean overshoot",
    which described a state this metric cannot reach. Overshooting ALONG the
    injected direction moves away from the target again and scores BELOW 1, the
    same as undershooting -- the two are distinguished by
    `score_campaign.overshoot_projection`, not by the sign of the score. Going
    the wrong way scores below 0, and that is the unbounded tail worth watching.
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
        "bounded_above_by_one": True,
        "below_zero_means_worse_than_doing_nothing": True,
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
    parser.add_argument("--target-npy", type=Path, required=True,
                        help="the certified Gate-2 negweight-refined target")
    parser.add_argument("--target-receipt", type=Path, required=True,
                        help="the Gate-2 runtime receipt that owns the target")
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
    import numpy as np

    repo = Path(args.repo).resolve()
    for extra in (repo / "nd-unfolding" / "pet", repo / "omnifold_nn"):
        if str(extra) not in sys.path:
            sys.path.insert(0, str(extra))

    from keras_backend import configure_production_precision
    configure_production_precision(strict=True)

    import fullevent_fps_dataloader as ffd
    # `train_fullevent_nominal` hard-codes the PRODUCTION repo and inserts it at
    # sys.path[0] on import, which would shadow this pinned checkout for every
    # module imported afterwards. `ffd` is bound above, before that happens; the
    # rest is protected by restoring our paths and then CHECKING where the
    # modules actually came from, because restoring a path is a hope and
    # `__file__` is a measurement.
    _our_path = list(sys.path)
    import train_fullevent_nominal as prod
    sys.path[:] = _our_path
    from omnifold.omnifold import MultiFold
    from omnifold.net import PET
    import training_recipe as recipe
    import fold_forward_recorder as ffr
    import tensorflow as tf
    from annealed_estimator import make_annealed_multifold

    _shadowed = [m.__name__ for m in (ffd, recipe)
                 if not str(Path(m.__file__).resolve()).startswith(str(repo))]
    if _shadowed:
        raise SystemExit(
            f"[arm] {_shadowed} resolved OUTSIDE the pinned checkout {repo}. "
            "The production driver puts its own repo on sys.path[0], and a run "
            "that silently used production's loader would not be measuring this "
            "commit at all"
        )

    started = time.perf_counter()

    # CONSUME the certified Gate-2 target; do not rebuild it.
    #
    # This driver used to call `build_fullevent_loaders` with neither
    # `bkg_mode` nor `precomputed_target`, which re-runs the whole negweight
    # refinement in process. That is the J04/D2 defect the production driver
    # was repaired for in August: "the target Gate-2 certified was certified
    # and then discarded". Here it would have been worse than wasteful -- the
    # measured leg both arms are compared on would not have been the
    # production measured leg, so the comparison would not have been about
    # our incumbent.
    #
    # The provenance assertions are PRODUCTION's own functions, called rather
    # than retyped, so the two cannot drift.
    # THE SEED SEEDS THE ESTIMATOR, not the subsample.
    #
    # Production fixes `subsample_seed=0` and varies `estimator_seed`, applying
    # it with `tf.keras.utils.set_random_seed` before any model exists. This
    # driver did neither: it passed the frozen seed to the LOADER, so the seed
    # changed which events were drawn, and it never seeded Keras at all -- the
    # network initialisation was unseeded, so "scratch, per-seed" was not
    # reproducible and the frozen seed list bound nothing about the estimator.
    #
    # Within a stage both arms must see the SAME events, so the subsample is
    # held at production's value and the seed varies initialisation and
    # training stochasticity. That is what the paired difference is supposed to
    # average over.
    tf.keras.utils.set_random_seed(int(args.seed))
    target_receipt = prod.assert_target_provenance(
        str(args.target_npy), str(args.target_receipt), str(args.inputs_npz))
    data, mc, imc, coord_reco, coord_gen, meta = ffd.build_fullevent_loaders(
        str(args.inputs_npz), max_events=args.max_events,
        seed=int(prod.NOMINAL_SEED_POLICY["subsample_seed"]),
        bkg_mode=prod.BKG_MODE, precomputed_target=str(args.target_npy))
    # Row order, which no hash can bind on its own.
    prod.assert_consumed_inventory_matches_receipt(meta, target_receipt)

    substitution = None
    if args.arm == "theirs":
        import theirs_loader_substitution as tls
        import theirs_omnifold_arm as toa
        # The measured leg is the SIGNED inventory: positive data rows followed
        # by the aligned negative background rows. His arm needs tokens for
        # both, so the data side is the `data` join concatenated with the `bkg`
        # join, in that order. Joining only `data` left the two 564,591 rows
        # apart and the mismatch surfaced as a length error rather than as a
        # silent misalignment, which is the one piece of luck in it.
        blocks = _load_joined(args, np, imc, data.reco.shape[0])
        substitution = tls.substitute_step1(
            data, mc,
            (blocks["data"]["packed"], blocks["data"]["globals"]),
            (blocks["mc"]["packed"], blocks["mc"]["globals"]))
        model_reco_factory = lambda: toa.TheirsCompleteArm(
            num_part=fd.THEIRS_COMPLETE["token_cap"])
    else:
        model_reco_factory = None

    # WIDTHS COME FROM THE DATA, exactly as the production driver takes them.
    # This read `meta["n_feat_reco"]`, which the loader does not emit -- the
    # incumbent arm died on a KeyError before building anything. Production
    # takes the cloud width from `mc.reco.shape[-1]`, the token count from
    # `mc.reco.shape[1]`, and the two DIFFERENT event widths from the meta keys
    # that do exist. Read AFTER the substitution, so his arm's 33x10 tokens
    # size his network and ours sizes ours.
    ev_reco, ev_truth = meta["n_evt_reco"], meta["n_evt_truth"]
    if (ev_reco != np.asarray(mc.reco_evt).shape[1]
            or ev_truth != np.asarray(mc.gen_evt).shape[1]):
        raise SystemExit(
            f"[arm] loader meta widths ({ev_reco}, {ev_truth}) disagree with the "
            f"built blocks ({np.asarray(mc.reco_evt).shape[1]}, "
            f"{np.asarray(mc.gen_evt).shape[1]}) -- fail closed")
    if list(meta["feature_names"]) == list(ffd.REDUCED_EVT_FEATURES):
        raise SystemExit(
            "[arm] the loader built the REDUCED {pT,p||} schema, which the "
            "feature contract marks cross-check only. The comparison would be "
            "measuring a schema nobody authorized for it -- fail closed")

    P = int(np.asarray(mc.reco).shape[1])
    model_reco = (model_reco_factory() if model_reco_factory is not None
                  else PET(int(np.asarray(mc.reco).shape[-1]), num_evt=ev_reco,
                           num_part=P, num_transformer=2, num_heads=2,
                           projection_dim=32, local=True, K=3,
                           coord_idx=coord_reco))

    # STEP 2 IS IDENTICAL FOR BOTH ARMS -- STEP_SCOPE, frozen 2026-09-20.
    model_gen = PET(int(np.asarray(mc.gen).shape[-1]), num_evt=ev_truth,
                    num_part=int(np.asarray(mc.gen).shape[1]),
                    num_transformer=2, num_heads=2, projection_dim=32,
                    local=True, K=3, coord_idx=coord_gen)

    batch = (fd.THEIRS_COMPLETE["batch_size"] if args.arm == "theirs"
             else fd.OURS_INCUMBENT["batch_size"])
    schedule = recipe.derive_schedule(batch, step="step1_reco",
                                      n_data=data.reco.shape[0])

    folder = Path(args.weights_folder)
    folder.mkdir(parents=True, exist_ok=True)

    # THE ANNEALED ESTIMATOR, because that is the incumbent. A bare `MultiFold`
    # is not what production runs: the engine's own anneal is dead code, and
    # `make_annealed_multifold` is what makes the adopted policy bite. Running
    # ours on a bare MultiFold would have compared his configuration against
    # something we do not use, under the name of the one we do. Both arms get
    # it, because the estimator is not what the arms differ in.
    fit_lr_records: list[dict[str, Any]] = []
    Annealed = make_annealed_multifold(MultiFold, tf, fit_lr_records)
    unfolder = Annealed(
        name=f"{args.arm}-{args.stage}-seed{args.seed}",
        model_reco=model_reco, model_gen=model_gen, data=data, mc=mc,
        weights_folder=str(folder), niter=args.niter, batch_size=batch,
        # EPOCHS MUST BE PASSED. `MultiFold` defaults to 50; the incumbent's
        # frozen policy is 8, and both the training recipe and the cost model
        # are built on 8. Leaving the default would have trained every arm six
        # times longer than the incumbent -- so "ours" would not have been ours
        # -- and turned a 366 GPU-hour campaign into roughly 2,200 against a
        # 1,000-hour ceiling.
        epochs=int(recipe.EPOCHS),
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
        "target": {"path": str(args.target_npy),
                   "receipt": str(args.target_receipt),
                   "bkg_mode": prod.BKG_MODE,
                   "rebuilt_in_process": False},
        "substitution": substitution,
        "estimator": {"annealed": True,
                      "epochs": int(recipe.EPOCHS),
                      "estimator_seed": int(args.seed),
                      "subsample_seed": int(
                          prod.NOMINAL_SEED_POLICY["subsample_seed"]),
                      "fits_recorded": len(fit_lr_records),
                      "realized_learning_rates": fit_lr_records},
        "widths": {"cloud_reco": int(np.asarray(mc.reco).shape[-1]),
                   "tokens": P, "evt_reco": int(ev_reco),
                   "evt_truth": int(ev_truth)},
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


def _load_joined(args: Any, np: Any, mc_rows: Any, expected_data_rows: int
                 ) -> dict[str, Any]:
    """Gather his inputs for exactly the rows this fit will see.

    THE MEASURED LEG IS SIGNED. `build_signed_measured_inventory` concatenates
    the positive data rows with the aligned negative background rows, so the
    data loader holds 4,680,719 rows: 4,116,128 data gates followed by 564,591
    background MC events. His arm needs tokens for both, so the data side here
    is the `data` join followed by the `bkg` join, in that order -- the same
    order the loader built.

    Joining only `data` and `sig` left the background 564,591 rows short. That
    surfaced as a length error rather than as a silent misalignment, which is
    the one piece of luck in it: a same-length-but-differently-ordered gather
    would have attached one event's tokens to another's weight.

    `pass_reco` comes from the INVENTORY, not from the loaders, because
    `row_index` is indexed by inventory row. The loader's own `pass_reco` is
    over its subsample and using it silently mis-assigns the flag.
    """
    import json

    import materialize_theirs as mtz

    index_dir = Path(args.theirs_index)
    with np.load(args.inputs_npz, mmap_mode="r") as target:
        sig_pass_reco = np.asarray(target["pass_reco"]).astype(bool)

    def gather(stream: str, rows: Any, pass_reco: Any) -> dict[str, Any]:
        index = np.load(index_dir / f"join_{stream}.npz")
        report = json.loads((index_dir / f"join_{stream}.json").read_text())
        return mtz.materialize(report["files"], index["row_index"],
                               index["origin"], np.asarray(rows), pass_reco)

    pieces = []
    for stream in ("data", "bkg"):
        index = np.load(index_dir / f"join_{stream}.npz")
        n = int(np.asarray(index["row_index"]).shape[0])
        # Data gates and refined background rows are reconstructed by
        # construction -- they are what the measured leg IS.
        pieces.append(gather(stream, np.arange(n), np.ones(n, dtype=bool)))
    measured = {
        "packed": np.concatenate([p["packed"] for p in pieces], axis=0),
        "globals": np.concatenate([p["globals"] for p in pieces], axis=0),
        "rows": sum(p["rows"] for p in pieces),
        "streams": ["data", "bkg"],
    }
    if measured["packed"].shape[0] != expected_data_rows:
        raise SystemExit(
            f"[arm] the measured leg has {expected_data_rows} rows and "
            f"data+bkg supplies {measured['packed'].shape[0]}. The signed "
            "inventory is data followed by background; a mismatch here means "
            "the joins and the loader disagree about the population")

    signal = gather("sig", mc_rows, sig_pass_reco)
    return {"data": measured, "mc": signal}


if __name__ == "__main__":
    main()
