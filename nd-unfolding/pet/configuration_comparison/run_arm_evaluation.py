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
    # NO --target-npy here. The certified Gate-2 negweight-refined target is
    # the REAL-data nominal's measured leg. This is a closure: `mc-only`, no
    # measured loader, nothing to consume. Requiring it would have been a
    # fail-closed check on an artifact this path must not use.
    parser.add_argument("--identity-sidecar", type=Path, default=None,
                        help="the event-identity sidecar; the stage split "
                             "is assigned from it")
    parser.add_argument("--theirs-cache", type=Path, default=None,
                        help="one-time gather from prematerialize_theirs")
    parser.add_argument("--half-size", type=int, default=None,
                        help="rows per disjoint half; defaults to the largest "
                             "that fits twice inside this stage's share")
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
    """Run one arm on the POWERED CLOSURE, following the established protocol.

    This used to build the production loaders and unfold the REAL measured
    inventory while its docstring claimed the opposite. It never applied the
    injection. The protocol below is `closure_powered_truth_reweight`'s, whose
    every clause exists because the ordinary closure has structurally zero
    power -- the pseudo-data IS the MC, so a constant estimator optimises it:

    * `bkg_mode='mc-only'`, so there is NO measured loader and no real spectrum
      is ever unfolded. Also no ROOT, hence no ROOT/TF environment conflict.
    * TWO DISJOINT HALVES from one seeded permutation: pseudo-data from half A,
      prior from half B, so the estimator never sees the events it must
      reweight. An overlapping split restores the identity shortcut and power
      returns to zero.
    * The injection on half A's TRUTH-PASSING rows only -- it is a truth-level
      reweighting and is undefined where no truth record exists.
    * Step-1 rows `pass_reco & pass_gen` on BOTH sides, or one side carries
      reco-only rows whose tilt is undefined and step 1 sees a second
      difference on top of the injection.
    * float32 weights, because the engine multiplies them against float32
      logits and a float64 array dies inside a tf.function naming Keras
      internals rather than the caller.

    The arms differ at step 1 only: his tokens replace the step-1 reco inputs
    on both legs. Step 2 is the production PET on the production truth cloud
    for both.
    """
    import numpy as np

    repo = Path(args.repo).resolve()
    for extra in (repo / "nd-unfolding" / "pet", repo / "omnifold_nn"):
        if str(extra) not in sys.path:
            sys.path.insert(0, str(extra))

    from keras_backend import configure_production_precision
    configure_production_precision(strict=True)

    import fullevent_fps_dataloader as ffd
    import closure_powered_truth_reweight as cp
    import train_fullevent_nominal as prod
    from omnifold.omnifold import MultiFold
    from omnifold.dataloader import DataLoader
    from omnifold.net import PET
    import training_recipe as recipe
    import tensorflow as tf
    from annealed_estimator import make_annealed_multifold

    _shadowed = [m.__name__ for m in (ffd, recipe)
                 if not str(Path(m.__file__).resolve()).startswith(str(repo))]
    if _shadowed:
        raise SystemExit(
            f"[arm] {_shadowed} resolved OUTSIDE the pinned checkout {repo}. "
            "The production driver puts its own repo on sys.path[0], and a run "
            "that silently used production's loader would not be measuring "
            "this commit at all")

    started = time.perf_counter()

    # The seed seeds the ESTIMATOR. Production fixes the subsample and varies
    # this; within a stage both arms must see the same events, so the paired
    # difference averages over initialisation rather than over the draw.
    tf.keras.utils.set_random_seed(int(args.seed))

    need = int(args.max_events)
    data_leg, mc, imc, coord_reco, coord_gen, meta = ffd.build_fullevent_loaders(
        str(args.inputs_npz), max_events=need,
        seed=int(prod.NOMINAL_SEED_POLICY["subsample_seed"]), bkg_mode="mc-only")
    if data_leg is not None:
        raise SystemExit(
            "[arm] mc-only returned a measured loader; wrong build path. The "
            "closure must not have a real measured leg -- that is the check "
            "that keeps this from unfolding data")
    imc = np.asarray(imc)

    eavail = _truth_eavail(np, ffd, args.inputs_npz, imc)

    reco = np.asarray(mc.reco); reco_evt = np.asarray(mc.reco_evt)
    gen = np.asarray(mc.gen); gen_evt = np.asarray(mc.gen_evt)
    pr = np.asarray(mc.pass_reco).astype(bool)
    pg = np.asarray(mc.pass_gen).astype(bool)
    w_truth = np.asarray(mc.weight, dtype=np.float64)
    leg = getattr(mc, "weight_reco", None)
    if leg is None:
        raise SystemExit("[arm] loader supplied no reco leg; dual-leg weights are required")
    w_reco = np.asarray(leg, dtype=np.float64)

    # THE STAGE SPLIT. Frozen since 2026-09-20 and, until now, unimplemented:
    # every stage trained on the same events, so the learning rate would have
    # been chosen on the data the effect is measured on and the pilot's
    # variance -- which sizes the final -- would have been in-sample.
    #
    # The two disjoint halves are taken INSIDE this stage's events, so the
    # closure's own split and the stage split compose rather than fight.
    import stage_splits as ss

    identity = _identity_of(np, args.identity_sidecar, imc)
    stage_pos = ss.rows_for_stage(identity, args.stage)
    split_census = ss.census(identity)
    # The half size comes from the STAGE unless pinned. A stage owns its own
    # share of the subsample -- 0.20/0.20/0.60 -- so one constant across all
    # three either wastes the final's events or cannot be met by tuning. The
    # pilot's halves are therefore smaller than the final's, which OVERSTATES
    # the variance the pilot measures and so sizes the final conservatively
    # rather than optimistically. That direction is the safe one, and it is
    # recorded in the receipt rather than left to be noticed.
    half = (int(args.half_size) if args.half_size is not None
            else ss.usable_half_size(identity, args.stage))
    if half <= 0:
        raise SystemExit(
            f"[arm] stage {args.stage!r} owns {stage_pos.size} events; there is "
            "nothing to split into halves")
    if stage_pos.size < 2 * half:
        raise SystemExit(
            f"[arm] stage {args.stage!r} owns {stage_pos.size} of the "
            f"{identity.shape[0]} subsampled events, which cannot supply two "
            f"disjoint halves of {half}. Raise --max-events or lower "
            f"--half-size; do not borrow another stage's events")
    ja, jb = cp.deterministic_halves(stage_pos.size, half=half,
                                     seed=int(fd.SPLITS["split_seed"]))
    ia, ib = stage_pos[ja], stage_pos[jb]

    pg_a = pg[ia]
    tilt_a = np.ones(ia.size, dtype=np.float64)
    tilt_on_truth, tilt_spec = cp.clipped_exponential_tilt(
        eavail[ia][pg_a], amplitude=float(fd.ENDPOINT["amplitude"]),
        clip_z=float(fd.ENDPOINT["clip"]))
    tilt_a[pg_a] = tilt_on_truth

    s1_a = pr[ia] & pg_a
    s1_b = pr[ib] & pg[ib]
    if not (s1_a.any() and s1_b.any()):
        raise SystemExit("[arm] a step-1 side has no pass_reco & pass_gen rows (fail closed)")

    substitution = None
    if args.arm == "theirs":
        import theirs_loader_substitution as tls
        import theirs_omnifold_arm as toa
        # His tokens for exactly the inventory rows each leg uses. Absolute
        # dump rows, so the gather cannot be confused by the subsample.
        blocks = _load_joined(args, np, imc[ia][s1_a], imc[ib],
                              subsample_seed=int(
                                  prod.NOMINAL_SEED_POLICY["subsample_seed"]),
                              max_events=need, half_size=half,
                              stage=args.stage)
        reco_a = blocks["pdata"]["packed"]
        reco_evt_a = blocks["pdata"]["globals"]
        reco_b = blocks["mc"]["packed"]
        reco_evt_b = blocks["mc"]["globals"]
        substitution = {
            "substituted": ["reco", "reco_evt"],
            "source": blocks["source"],
            "pdata_rows": int(reco_a.shape[0]),
            "mcB_rows": int(reco_b.shape[0]),
            "step2_untouched": True,
        }
        model_reco_factory = lambda: toa.TheirsCompleteArm(
            num_part=fd.THEIRS_COMPLETE["token_cap"])
    else:
        reco_a = reco[ia][s1_a]
        reco_evt_a = reco_evt[ia][s1_a]
        reco_b = reco[ib]
        reco_evt_b = reco_evt[ib]
        model_reco_factory = None

    pdata = DataLoader(reco=reco_a,
                       weight=((w_reco[ia] * tilt_a)[s1_a]).astype(np.float32),
                       normalize=True, reco_evt=reco_evt_a)
    mcB = DataLoader(reco=reco_b, gen=gen[ib], pass_reco=s1_b, pass_gen=pg[ib],
                     weight=w_truth[ib].astype(np.float32),
                     weight_reco=w_reco[ib].astype(np.float32),
                     normalize=True,
                     normalization_factor=ffd.STEP1_MC_NORMALIZATION,
                     reco_evt=reco_evt_b, gen_evt=gen_evt[ib])
    for name, loader in (("pdata", pdata), ("mcB", mcB)):
        for field in ("weight", "weight_reco"):
            arr = getattr(loader, field, None)
            if arr is not None and np.asarray(arr).dtype != np.float32:
                raise SystemExit(
                    f"[arm] {name}.{field} is {np.asarray(arr).dtype}, not "
                    "float32; the engine multiplies it against float32 logits")

    P = int(np.asarray(reco_b).shape[1])
    model_reco = (model_reco_factory() if model_reco_factory is not None
                  else PET(int(np.asarray(reco_b).shape[-1]),
                           num_evt=int(meta["n_evt_reco"]), num_part=P,
                           num_transformer=2, num_heads=2, projection_dim=32,
                           local=True, K=3, coord_idx=coord_reco))
    # STEP 2 IS IDENTICAL FOR BOTH ARMS -- STEP_SCOPE, frozen 2026-09-20.
    model_gen = PET(int(gen.shape[-1]), num_evt=int(meta["n_evt_truth"]),
                    num_part=int(gen.shape[1]), num_transformer=2, num_heads=2,
                    projection_dim=32, local=True, K=3, coord_idx=coord_gen)

    batch = (fd.THEIRS_COMPLETE["batch_size"] if args.arm == "theirs"
             else fd.OURS_INCUMBENT["batch_size"])

    folder = Path(args.weights_folder)
    folder.mkdir(parents=True, exist_ok=True)

    # The annealed estimator, because that is the incumbent: the engine's own
    # anneal is dead code. Both arms get it -- the estimator is not what the
    # arms differ in.
    fit_lr_records: list[dict[str, Any]] = []
    Annealed = make_annealed_multifold(MultiFold, tf, fit_lr_records)
    unfolder = Annealed(f"{args.arm}-{args.stage}-seed{args.seed}",
                        model_reco, model_gen, pdata, mcB,
                        niter=int(args.niter), epochs=int(recipe.EPOCHS),
                        batch_size=batch, lr=args.learning_rate,
                        weights_folder=str(folder), verbose=False)
    unfolder.Unfold()

    push = np.asarray(unfolder.weights_push, dtype=np.float64)
    if push.shape[0] != ib.size:
        raise SystemExit(
            f"[arm] push {push.shape} is not aligned to half B ({ib.size}); "
            "scoring would attach each weight to the wrong event")

    # ABSOLUTE dump rows for both halves, so the scorer rebuilds the spectra
    # from the dump rather than replaying the subsample and split logic.
    out = folder / f"weights_{args.arm}_{args.stage}_{args.seed}.npz"
    np.savez_compressed(out, weights=push,
                        dump_rows_a=imc[ia].astype(np.int64),
                        dump_rows_b=imc[ib].astype(np.int64),
                        tilt_a=tilt_a, pass_gen_a=pg_a,
                        pass_gen_b=pg[ib], mc_indices=imc.astype(np.int64))
    return {
        **plan_of(args),
        "seconds": time.perf_counter() - started,
        "closure": {
            "powered": True, "bkg_mode": "mc-only",
            "measured_leg_is_real_data": False,
            "half_size": half,
            "half_size_source": ("pinned" if args.half_size is not None
                                 else "derived from the stage's share"),
            "split_seed": int(fd.SPLITS["split_seed"]),
            "halves_disjoint": True,
            "stage_split": split_census,
            "stage_rows_available": int(stage_pos.size),
            "pdata_rows": int(s1_a.sum()), "prior_rows": int(ib.size),
            "injection": tilt_spec,
        },
        "substitution": substitution,
        "estimator": {"annealed": True, "epochs": int(recipe.EPOCHS),
                      "estimator_seed": int(args.seed),
                      "subsample_seed": int(
                          prod.NOMINAL_SEED_POLICY["subsample_seed"]),
                      "batch_size": int(batch),
                      "fits_recorded": len(fit_lr_records),
                      "realized_learning_rates": fit_lr_records},
        "weights_finite": bool(np.isfinite(push).all()),
        "weights_path": str(out),
        "scored_here": False,
        "note": "scoring is a separate step over the frozen endpoint",
    }


def _identity_of(np: Any, sidecar: Any, imc: Any):
    """The frozen identity fields for the subsampled rows.

    Read from the identity sidecar rather than reconstructed, because the
    sidecar is what records the `occurrence` discriminator and the per-stream
    field order, and a second reconstruction of an identity is a second thing
    that can disagree about which event is which.
    """
    if sidecar is None:
        raise SystemExit(
            "[arm] --identity-sidecar is required: the stage split is assigned "
            "by event identity, and without it the split would fall back to "
            "row order, which is a property of the file and not of the event")
    blob = np.load(str(sidecar), mmap_mode="r")
    return np.asarray(blob["sig_event_id"]).astype(np.int64)[np.asarray(imc)]


def _truth_eavail(np: Any, ffd: Any, inputs_npz: Any, imc: Any):
    """Truth E_avail for the subsampled rows, read straight from the dump."""
    import zipfile

    import numpy.lib.format as npf

    with zipfile.ZipFile(str(inputs_npz)) as archive:
        with archive.open("truth_scalars.npy") as handle:
            scalars = npf.read_array(handle, allow_pickle=False)[np.asarray(imc)]
    return scalars[:, ffd.SCALAR_COLS["eavail"]].astype(np.float64)


def cp_half_size() -> int:
    """The established half size, read from the closure module, not copied."""
    import closure_powered_truth_reweight as cp
    return int(cp.HALF_SIZE)


def plan_of(args: Any) -> dict[str, Any]:
    return {"arm": args.arm, "seed": args.seed, "stage": args.stage,
            "learning_rate": args.learning_rate, "niter": args.niter}


def _load_joined(args: Any, np: Any, pdata_rows: Any, mcb_rows: Any, *,
                 subsample_seed: int, max_events: int, half_size: int,
                 stage: str) -> dict[str, Any]:
    """His tokens for the two closure legs, from the one-time cache if it exists.

    MEASURED, job 58599158: gathering in-process cost 15.5 minutes before his
    arm's first training step, against 75 seconds for ours to the same point.
    Every task gathers the SAME rows -- subsample seed, subsample size, split
    seed and half size are all frozen and only the estimator seed varies -- so
    `prematerialize_theirs` does it once and each task memory-maps the result.
    The cache carries a key over everything the rows depend on, and a key
    mismatch is refused rather than gathered around.

    Falling back to an in-process gather keeps the driver runnable without the
    cache; it is slow, not wrong, and the receipt records which path was used.
    """
    import json

    import materialize_theirs as mtz
    import prematerialize_theirs as pre

    key = pre.cache_key(inputs_npz=Path(args.inputs_npz),
                        subsample_seed=subsample_seed, max_events=max_events,
                        split_seed=int(fd.SPLITS["split_seed"]),
                        half_size=half_size, stage=stage)
    cache = getattr(args, "theirs_cache", None)
    if cache is not None and Path(cache).exists():
        blob = pre.load(Path(cache), expected_key=key)
        return {
            "pdata": {"packed": np.asarray(blob["pdata_packed"]),
                      "globals": np.asarray(blob["pdata_globals"])},
            "mc": {"packed": np.asarray(blob["prior_packed"]),
                   "globals": np.asarray(blob["prior_globals"])},
            "source": {"cache": str(cache), "key": key},
        }

    index_dir = Path(args.theirs_index)
    with np.load(args.inputs_npz, mmap_mode="r") as target:
        sig_pass_reco = np.asarray(target["pass_reco"]).astype(bool)
    index = np.load(index_dir / "join_sig.npz")
    report = json.loads((index_dir / "join_sig.json").read_text())

    def gather(rows: Any) -> dict[str, Any]:
        return mtz.materialize(report["files"], index["row_index"],
                               index["origin"], np.asarray(rows), sig_pass_reco)

    return {"pdata": gather(pdata_rows), "mc": gather(mcb_rows),
            "source": {"cache": None, "key": key,
                       "note": "gathered in process; slow but not wrong"}}


def cp_half_size() -> int:
    """The established half size, read from the closure module, not copied."""
    import closure_powered_truth_reweight as cp
    return int(cp.HALF_SIZE)


def plan_of(args: Any) -> dict[str, Any]:
    return {"arm": args.arm, "seed": args.seed, "stage": args.stage,
            "learning_rate": args.learning_rate, "niter": args.niter}


def _load_joined(args: Any, np: Any, pdata_rows: Any, mcb_rows: Any
                 ) -> dict[str, Any]:
    """His tokens for the two closure legs, by ABSOLUTE inventory row.

    Only the `sig` stream is needed: the closure runs `bkg_mode='mc-only'`, so
    there is no measured leg and no data or background join to gather. Both
    legs are MC rows of the signal inventory, named by their absolute dump
    index, so the gather cannot be confused by the subsample or the split.

    The pdata leg is `pass_reco & pass_gen` by construction, so every row must
    match. The prior leg is all of half B, so it contains !pass_reco rows;
    those come back zero, exactly as the production loader zeroes ours.
    """
    import json

    import materialize_theirs as mtz

    index_dir = Path(args.theirs_index)
    with np.load(args.inputs_npz, mmap_mode="r") as target:
        sig_pass_reco = np.asarray(target["pass_reco"]).astype(bool)

    index = np.load(index_dir / "join_sig.npz")
    report = json.loads((index_dir / "join_sig.json").read_text())

    def gather(rows: Any) -> dict[str, Any]:
        return mtz.materialize(report["files"], index["row_index"],
                               index["origin"], np.asarray(rows), sig_pass_reco)

    return {"pdata": gather(pdata_rows), "mc": gather(mcb_rows)}


if __name__ == "__main__":
    main()
