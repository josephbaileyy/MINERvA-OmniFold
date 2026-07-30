#!/usr/bin/env python3
"""Event-feature ranking arms: does the event-feature channel saturate at {pT, p‖}? (B-3)

CONTEXT. `FULL_EVENT_FEATURE_CONTRACT.md:19-21` declares the publication estimator needs the
FULL muon object + vertex + view/timing, and `:116-123` justifies the adopted reduced set
{pT, p‖} by ASSERTION. The only quantitative feature comparison on the books is CLM-006, and
its own caveat voids it: the two arms differed in niter (5 vs 2) AND train size (40M vs 2M) AND
representation, so "4.25%" mixes three effects; OMNIFOLD-DOSSIER.md:67 records "differences
reported, no tolerance". This driver measures the thing that number was supposed to measure,
with every arm at MATCHED niter/epochs/rows/subsample so only the feature block varies.

WHY eavail/q3. `fullevent_fps_dataloader.SCALAR_COLS` is
{"pt":0, "pparallel":1, "eavail":2, "q3":3} -- so two additional reco AND truth event features
are ALREADY DUMPED and simply unread by the adopted 2-feature schema. They cost no C++ dump,
no regeneration, and no bound-file edit (`feature_names` is a plumbed parameter). They are NOT
part of the proposed extension schema, so this does not directly license the C++ ask; it
answers the question underneath it -- whether the event-feature channel is already saturated.
A null result here is evidence AGAINST an expensive extension; a shift is evidence the channel
has headroom.

WHAT THIS RUN IS (and is not). `measured_scalars` is absent from the xps2 pc npz (CLM-007) and
the sidecar `of_inputs_5d_fps_xps2.npz` is not on this host, so there is no real-data leg. The
arms therefore run as a CLOSURE: pseudo-data is an INDEPENDENT MC half reweighted by a KNOWN
truth-level tilt in pT. That yields three things that are prerequisites for interpreting any
real-data arm, and which must be in hand first anyway:

  (1) MATCHED POSITIVE CONTROL. The tilt lives entirely inside {pT, p‖}, so the BASE arm must
      recover it. If base cannot, "the extension arm moved" would be uninterpretable.
  (2) RETRAINING FLOOR. Base is repeated at several estimator seeds. Any inter-arm shift
      smaller than this seed-to-seed spread is noise. This is the guard
      FULL_EVENT_FEATURE_CONTRACT.md:250 mandates and the one CLM-006 lacked.
  (3) VARIANCE INFLATION. Extension arms are also repeated, so an added feature that buys shape
      recovery while inflating seed variance more shows up as a NET LOSS rather than a win.

It does NOT measure whether eavail/q3 help on real data -- data and MC differ there for
physical reasons this closure does not contain. That arm unblocks when the sidecar returns.

OUTPUT. One JSON per arm holding the normalized truth-level spectrum on the canonical extended
(pT,p‖) grid. Inter-arm shifts Dx are formed downstream; the whitened SVD ranking needs a
covariance C_base, which comes from the C_stat replica machinery and does NOT exist at reduced
scale, so this run deliberately emits the UNWHITENED shift ingredients only.

SPECTRA ARE SHAPES. Every spectrum is normalized to unit sum before comparison, so the arms are
compared on SHAPE and the overall rate is out of scope. Rate normalization is B1's subject
(`step1_class_ratio`) and entangling the two here would make neither measurable.
"""
import argparse
import json
import os
import sys
import time

import numpy as np

_REPO = os.environ.get("MNV_REPO") or os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for _p in (f"{_REPO}/omnifold_nn", f"{_REPO}/nd-unfolding"):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import fullevent_fps_dataloader as fed          # noqa: E402  (path set above)

# Feature blocks under test. "base" is the adopted schema; the rest ADD already-dumped columns.
ARM_BLOCKS = {
    "base":   ("pt", "pparallel"),
    "eavail": ("pt", "pparallel", "eavail"),
    "q3":     ("pt", "pparallel", "q3"),
    "both":   ("pt", "pparallel", "eavail", "q3"),
}
# Default seed plan: base gets 3 (the floor needs >=3 to have a spread, not just a difference),
# extensions get 2 each (enough to separate a real shift from a one-seed fluctuation).
DEFAULT_SEEDS = {"base": (101, 202, 303), "eavail": (101, 202),
                 "q3": (101, 202), "both": (101, 202)}


def truth_tilt(truth_scalars, amplitude, pass_truth=None):
    """The KNOWN injected distortion: a smooth monotone shape tilt in TRUTH pT.

    Chosen to sit entirely inside the adopted {pT, p‖} block so the base arm is a matched
    positive control (requirement 1). Robust-scaled (median/IQR) so `amplitude` means the same
    thing regardless of the pT units or the subsample drawn, and exponentiated so the weight is
    strictly positive -- a tilt that could go negative would collide with the Stay-Positive
    machinery and confound this with the background treatment.

    The median/IQR are taken over pass_truth rows ONLY. Rows without a truth gate carry
    sentinels and are never binned, so letting them set the scale would make `amplitude` mean
    something different from run to run for no physical reason.
    """
    pt = np.asarray(truth_scalars, np.float64)[:, fed.SCALAR_COLS["pt"]]
    scale_rows = np.isfinite(pt) & (pt > 0)
    if pass_truth is not None:
        scale_rows &= np.asarray(pass_truth, bool)
    if scale_rows.sum() < 100:
        raise SystemExit(f"only {scale_rows.sum()} rows available to set the tilt scale")
    med = np.median(pt[scale_rows])
    q75, q25 = np.percentile(pt[scale_rows], [75, 25])
    iqr = max(q75 - q25, 1e-9)
    u = np.clip((pt - med) / iqr, -3.0, 3.0)     # clip so a sentinel row cannot dominate
    return np.exp(amplitude * u)


def spectrum(truth_scalars, weights, pass_truth, edges_pt, edges_ppar):
    """Normalized truth-level (pT,p‖) shape over the canonical extended grid.

    Returns (flat_shape, n_eff). Rows failing truth are excluded: they have no truth kinematics
    to bin. Normalizing to unit sum makes this a SHAPE (see module docstring).
    """
    ts = np.asarray(truth_scalars, np.float64)
    sel = np.asarray(pass_truth, bool)
    w = np.asarray(weights, np.float64)[sel]
    h, _, _ = np.histogram2d(ts[sel, fed.SCALAR_COLS["pt"]],
                             ts[sel, fed.SCALAR_COLS["pparallel"]],
                             bins=[edges_pt, edges_ppar], weights=w)
    tot = h.sum()
    if not np.isfinite(tot) or tot <= 0:
        raise SystemExit("degenerate spectrum: total weight is not positive")
    n_eff = (w.sum() ** 2) / max(float((w ** 2).sum()), 1e-300)
    return (h / tot).ravel(), float(n_eff)


def run_arm(cache, arm, seed, cfg):
    """Train one arm and return its normalized unfolded spectrum + telemetry."""
    import tensorflow as tf
    from omnifold import PET, MultiFold
    from omnifold.dataloader import DataLoader

    names = ARM_BLOCKS[arm]
    ia, ib = cache["ia"], cache["ib"]
    edges_pt, edges_ppar = cache["edges_pt"], cache["edges_ppar"]

    # --- event features. Built on the FULL retained row set so the z-normalization statistic is
    # identical across arms (a per-half statistic would make the arms incomparable), then split.
    # measured_scalars = the DATA-half reco scalars: this is the closure's pseudo-data leg, and
    # it is MC by construction -- NOT a CLM-007 fallback, which is about real data silently
    # indexing MC rows. There is no real data in this run.
    ev_reco, ev_truth, ev_data_all, fmeta = fed.build_event_features(
        cache["reco_scalars"], cache["truth_scalars"], cache["reco_scalars"],
        feature_names=names, pass_reco=cache["pass_reco"], pass_truth=cache["pass_truth"])
    fed.assert_no_truth_leakage(ev_reco, cache["reco_scalars"], cache["truth_scalars"],
                                names, pass_reco=cache["pass_reco"])

    # --- data leg (half A, reco-level only: unreconstructed rows are not observable as data)
    a_pass = ia[cache["pass_reco"][ia]]
    w_data = (cache["w_truth"][a_pass] * cache["tilt"][a_pass]).astype(np.float32)
    cloud_data, _ = fed.build_reco_cloud(cache["part_reco"][a_pass])
    evt_data = ev_data_all[a_pass]

    # --- MC leg (half B, ALL rows incl. misses: step 2 needs the miss population)
    cloud_reco, coord_reco = fed.build_reco_cloud(cache["part_reco"][ib])
    cloud_gen, coord_gen = fed.build_truth_cloud(cache["part_gen"][ib])
    w_mc = cache["w_truth"][ib].astype(np.float32)

    tf.keras.utils.set_random_seed(seed)
    data = DataLoader(reco=cloud_data, weight=w_data, normalize=True, reco_evt=evt_data)
    mc = DataLoader(reco=cloud_reco, gen=cloud_gen,
                    pass_reco=cache["pass_reco"][ib], pass_gen=cache["pass_truth"][ib],
                    weight=w_mc, normalize=True,
                    reco_evt=ev_reco[ib], gen_evt=ev_truth[ib])

    n_evt = len(names)
    m1 = PET(cloud_reco.shape[-1], num_evt=n_evt, num_part=cloud_reco.shape[1],
             num_transformer=cfg.num_transformer, num_heads=cfg.num_heads,
             projection_dim=cfg.projection_dim, local=True, K=cfg.knn, coord_idx=coord_reco)
    m2 = PET(cloud_gen.shape[-1], num_evt=n_evt, num_part=cloud_gen.shape[1],
             num_transformer=cfg.num_transformer, num_heads=cfg.num_heads,
             projection_dim=cfg.projection_dim, local=True, K=cfg.knn, coord_idx=coord_gen)
    tag = f"frank_{arm}_s{seed}"
    of = MultiFold(tag, m1, m2, data, mc, niter=cfg.niter, epochs=cfg.epochs,
                   batch_size=cfg.batch_size, weights_folder=os.path.join(cfg.workdir, tag),
                   verbose=False)
    t0 = time.time()
    of.Unfold()
    secs = time.time() - t0

    # weights_push is the step-2 fit: a function of GEN only, i.e. the truth-level answer.
    push = np.asarray(of.weights_push, np.float64)
    shape, n_eff = spectrum(cache["truth_scalars"][ib], w_mc * push,
                            cache["pass_truth"][ib], edges_pt, edges_ppar)
    return {"arm": arm, "seed": seed, "feature_names": list(names), "n_evt": n_evt,
            "spectrum": shape.tolist(), "n_eff": n_eff, "train_seconds": secs,
            "push_mean": float(push.mean()), "push_max": float(push.max()),
            "push_finite": bool(np.isfinite(push).all()),
            "feature_meta": fmeta}


def median_fill_nonfinite(scalars, mask, label):
    """Replace non-finite scalar entries with the finite-row median of their column.

    WHY THIS IS NEEDED (found the hard way, Delta job 20599606 died here). `truth_scalars` col 3
    (`q3`) carries 14 non-finite values among pass_truth rows in a 400k subsample -- ~1,700 in the
    full 49.15M inventory. `_event_block` applies NO nan_to_num, unlike the cloud path
    (`_scale_clean`, dataloader.py:90). So `tsd = tsub.std(0)` is NaN, the WHOLE event_truth column
    becomes NaN, and step 2 trains to `Last val loss nan`. Step 1 is unaffected because the reco
    leg's q3 is clean, which is exactly the observed signature.

    `assert_no_truth_leakage` does not catch it: it asserts event_reco != the truth block, and NaN
    compares unequal, so the guard PASSES. Production is safe only because the adopted schema reads
    cols 0,1; any added column carrying a NaN kills step 2 with no pointer to the cause.

    Median fill, not row dropping, on purpose: dropping rows would change the row set and make the
    already-completed arms incomparable, reintroducing the very confound these arms exist to avoid.
    A median-filled row lands at z-score ~0 after normalization -- the block mean -- which is the
    same neutral treatment the loader already gives undefined (!pass) rows at :171-172.
    """
    a = np.array(scalars, dtype=np.float32, copy=True)
    bad = ~np.isfinite(a)
    if not bad.any():
        return a, {}
    report = {}
    for col in range(a.shape[1]):
        n_bad = int(bad[:, col].sum())
        if not n_bad:
            continue
        good = np.isfinite(a[:, col]) & np.asarray(mask, bool)
        if good.sum() == 0:
            raise SystemExit(f"{label} col{col}: no finite in-mask rows to take a median from")
        med = float(np.median(a[good, col]))
        a[bad[:, col], col] = med
        report[f"col{col}"] = {"n_nonfinite": n_bad, "median_fill": med}
        print(f"[frank] NON-FINITE FILL {label} col{col}: {n_bad} rows -> median {med:.6g} "
              f"({100.0*n_bad/a.shape[0]:.5f}% of rows)", flush=True)
    return a, report


def load_cache(path, half_seed):
    d = np.load(path, allow_pickle=True)
    c = {k: np.asarray(d[k]) for k in
         ("part_reco", "part_gen", "reco_scalars", "truth_scalars",
          "pass_reco", "pass_truth", "w_truth")}
    c["pass_reco"] = c["pass_reco"].astype(bool)
    c["pass_truth"] = c["pass_truth"].astype(bool)
    c["reco_scalars"], rrep = median_fill_nonfinite(
        c["reco_scalars"], c["pass_reco"], "reco_scalars")
    c["truth_scalars"], trep = median_fill_nonfinite(
        c["truth_scalars"], c["pass_truth"], "truth_scalars")
    c["nonfinite_report"] = {"reco_scalars": rrep, "truth_scalars": trep}
    fed.assert_extended_fps_edges(d["edges_0"], d["edges_1"])   # measurement-domain guard
    c["edges_pt"] = np.asarray(d["edges_0"], float)
    c["edges_ppar"] = np.asarray(d["edges_1"], float)
    # Disjoint halves, FIXED seed: identical across arms, so the data/MC split is never a
    # confound between arms. An arm that got its own split would conflate split noise with the
    # feature effect -- exactly the CLM-006 failure mode in a different variable.
    n = c["pass_reco"].shape[0]
    perm = np.random.default_rng(half_seed).permutation(n)
    c["ia"], c["ib"] = np.sort(perm[: n // 2]), np.sort(perm[n // 2:])
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="feature_rank_cache_400k.npz")
    ap.add_argument("--outdir", default="products/pet/feature_rank")
    ap.add_argument("--workdir", default="/tmp/feature_rank")
    ap.add_argument("--arms", default="base,eavail,q3,both",
                    help="comma list from " + ",".join(ARM_BLOCKS))
    ap.add_argument("--seeds", default="",
                    help="comma list applied to EVERY arm; default = per-arm plan "
                         "(base 3 seeds for the floor, extensions 2)")
    ap.add_argument("--amplitude", type=float, default=0.35,
                    help="injected truth-pT tilt strength (exp of robust-scaled pT)")
    ap.add_argument("--half-seed", type=int, default=7,
                    help="data/MC half split; FIXED across arms on purpose")
    ap.add_argument("--niter", type=int, default=2)
    ap.add_argument("--epochs", type=int, default=4)
    ap.add_argument("--batch-size", type=int, default=512)
    ap.add_argument("--num-transformer", type=int, default=2)
    ap.add_argument("--num-heads", type=int, default=2)
    ap.add_argument("--projection-dim", type=int, default=32)
    ap.add_argument("--knn", type=int, default=3)
    cfg = ap.parse_args()

    os.makedirs(cfg.outdir, exist_ok=True)
    os.makedirs(cfg.workdir, exist_ok=True)
    arms = [a.strip() for a in cfg.arms.split(",") if a.strip()]
    bad = [a for a in arms if a not in ARM_BLOCKS]
    if bad:
        raise SystemExit(f"unknown arm(s) {bad}; choose from {sorted(ARM_BLOCKS)}")

    cache = load_cache(cfg.cache, cfg.half_seed)
    cache["tilt"] = truth_tilt(cache["truth_scalars"], cfg.amplitude,
                               pass_truth=cache["pass_truth"])
    print(f"[frank] rows={cache['pass_reco'].shape[0]} halfA={cache['ia'].size} "
          f"halfB={cache['ib'].size} tilt_amplitude={cfg.amplitude} "
          f"tilt range [{cache['tilt'].min():.3f}, {cache['tilt'].max():.3f}]", flush=True)

    # Reference shapes. TARGET is what the data half actually encodes (the truth answer the
    # estimator is supposed to find); PRIOR is the untouched MC half. Recovery is measured as
    # the fraction of the PRIOR->TARGET gap that an arm closes, so an arm that does nothing
    # scores 0 and a perfect arm scores 1 -- independent of the tilt amplitude.
    target, _ = spectrum(cache["truth_scalars"][cache["ia"]],
                         cache["w_truth"][cache["ia"]] * cache["tilt"][cache["ia"]],
                         cache["pass_truth"][cache["ia"]], cache["edges_pt"], cache["edges_ppar"])
    prior, _ = spectrum(cache["truth_scalars"][cache["ib"]], cache["w_truth"][cache["ib"]],
                        cache["pass_truth"][cache["ib"]], cache["edges_pt"], cache["edges_ppar"])
    gap = float(np.abs(prior - target).sum())
    print(f"[frank] injected gap L1(prior,target) = {gap:.5f} over "
          f"{target.size} cells ({cache['edges_pt'].size-1}x{cache['edges_ppar'].size-1})",
          flush=True)
    if gap < 1e-6:
        raise SystemExit("injected gap is numerically zero -- raise --amplitude")

    # IRREDUCIBLE STATISTICAL FLOOR. `target` is built from half A and the answer from half B,
    # so `gap` contains the A-vs-B sampling difference on top of the injected tilt. No estimator
    # can close that part, and quoting recovery without it would credit the arms with less than
    # they achieved (or, if the tilt were small, flatter a null into a result). This is the
    # ceiling on `recovery`, measured the same way the gap is.
    a_untilted, _ = spectrum(cache["truth_scalars"][cache["ia"]], cache["w_truth"][cache["ia"]],
                             cache["pass_truth"][cache["ia"]],
                             cache["edges_pt"], cache["edges_ppar"])
    stat_floor = float(np.abs(a_untilted - prior).sum())
    ceiling = 1.0 - stat_floor / gap
    print(f"[frank] A-vs-B statistical floor L1 = {stat_floor:.5f} "
          f"({100.0*stat_floor/gap:.2f}% of the gap) -> recovery ceiling {ceiling:+.4f}",
          flush=True)
    if stat_floor > 0.5 * gap:
        print("[frank] WARNING: the sampling floor exceeds half the injected gap; the arms are "
              "being compared through mostly noise. Raise --amplitude or --n-events.", flush=True)

    seeds_override = [int(s) for s in cfg.seeds.split(",") if s.strip()] if cfg.seeds else None
    results = []
    for arm in arms:
        for seed in (seeds_override or DEFAULT_SEEDS[arm]):
            r = run_arm(cache, arm, seed, cfg)
            spec = np.asarray(r["spectrum"], float)
            r["l1_to_target"] = float(np.abs(spec - target).sum())
            r["recovery"] = 1.0 - r["l1_to_target"] / gap
            r["gap"] = gap
            results.append(r)
            with open(os.path.join(cfg.outdir, f"arm_{arm}_s{seed}.json"), "w") as fh:
                json.dump(r, fh, indent=2)
            print(f"[frank] {arm:7s} seed={seed:4d} n_evt={r['n_evt']} "
                  f"L1(target)={r['l1_to_target']:.5f} recovery={r['recovery']:+.4f} "
                  f"push[mean={r['push_mean']:.4f} max={r['push_max']:.3f}] "
                  f"{r['train_seconds']:.0f}s", flush=True)

    # --- floor and inter-arm separation. Reported here, decided nowhere: this run establishes
    # the floor, it does not adopt a tolerance.
    print("\n[frank] ---- summary ----")
    by_arm = {}
    for r in results:
        by_arm.setdefault(r["arm"], []).append(r)
    floor = None
    for arm, rs in by_arm.items():
        recs = np.array([x["recovery"] for x in rs])
        specs = np.array([x["spectrum"] for x in rs])
        spread = (float(np.abs(specs[0] - specs[1]).sum()) if len(rs) == 2 else
                  float(np.mean([np.abs(a - b).sum() for i, a in enumerate(specs)
                                 for b in specs[i + 1:]])) if len(rs) > 2 else float("nan"))
        print(f"[frank] {arm:7s} recovery mean={recs.mean():+.4f} sd={recs.std(ddof=1) if len(recs)>1 else float('nan'):.4f} "
              f"n={len(rs)}  intra-arm spectrum spread L1={spread:.5f}")
        if arm == "base":
            floor = spread
    if floor is not None and floor == floor:
        base_mean = np.mean([x["spectrum"] for x in by_arm["base"]], axis=0)
        for arm, rs in by_arm.items():
            if arm == "base":
                continue
            shift = float(np.abs(np.mean([x["spectrum"] for x in rs], axis=0) - base_mean).sum())
            verdict = "ABOVE floor" if shift > floor else "at/below floor -> NOT RANKED"
            print(f"[frank] shift(base -> {arm:7s}) L1={shift:.5f} vs base floor {floor:.5f}"
                  f"  [{shift/floor:.2f}x]  {verdict}")

    with open(os.path.join(cfg.outdir, "arms_summary.json"), "w") as fh:
        json.dump({"config": vars(cfg), "gap": gap, "stat_floor": stat_floor,
                   "recovery_ceiling": ceiling,
                   "nonfinite_report": cache["nonfinite_report"],
                   "target": target.tolist(),
                   "prior": prior.tolist(), "arms": results}, fh, indent=2)
    print(f"\n[frank] wrote {cfg.outdir}/arms_summary.json")


if __name__ == "__main__":
    main()
