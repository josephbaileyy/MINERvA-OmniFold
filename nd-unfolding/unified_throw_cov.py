#!/usr/bin/env python3
"""Rigorous many-throw unified systematic covariance vs the block-sum (prepub #1).

The block-sum cov assumes the unfolding responds LINEARLY to each band, so
C_total = sum_b C_b. The decisive test is a TRUE unified throw: shift ALL bands
together per universe, re-unfold, and build the covariance directly. In the linear
regime C_unified == C_blocksum exactly; the difference is the unfolding's nonlinear
cross-band term.

The 2026-06-04 ratio-product proxy was artifact-prone because it multiplied BINNED
spectrum ratios (low-w_cv tail events compounded -> 25x inflation). This driver
avoids that by composing weights at the PER-EVENT level and RE-UNFOLDING each throw
(the proper construction a multi-band event-loop universe would produce, for the
reweight/vertical systematics):

    throw j:  g_b ~ N(0,1) per +-1sigma knob band b;  u ~ U{0..Nflux-1}
    rho_b(g) = rho_plus**g (g>=0), rho_minus**(-g) (g<0)
    w_truth^(j) = w_truth * prod_b rho_b(g_b) * (wt_flux_u/w_truth)
    (same for w_reco and the truth-denom weights), clipped per event for positivity
    x_j = OmniFold-reunfold(w^(j))   [compare_unified_throw._xsec_for_weights]

Reads the per-event bank produced for the superposition probe (bank_uthrow/): cv.npz
(MCgen/MCreco/measured/pass_*/w_*/td_*/edges/flux/...) + per-band absolute universe
weights sig_<band>_{t,r}_<idx>.npy, td_<band>_<idx>.npy, flux as 100 universes.

Two phases (throws array-parallelise; combine aggregates):
  # one array task -> a slab of throws
  python unified_throw_cov.py --throws 8 --throw-offset 0 --seed 1000 \
      --bank bank_uthrow --iters 5 --out uthrow_slab_0.npz
  # after all slabs land
  python unified_throw_cov.py --combine 'uthrow_slab_*.npz' --bank bank_uthrow \
      --iters 5 --out-root uq_4d/unified_throw_cov.root
"""
import argparse
import glob
import os
import sys
import tempfile

import numpy as np

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
for _p in (f"{_REPO}/2d-unfolding", f"{_REPO}/nd-unfolding"):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import flux_universe
from compare_unified_throw import _xsec_for_weights
from uq_math import (interpolate_asymmetric_ratio, joint_throw_covariance,
                     mat_covariance)

# +-1sigma reweight knobs (idx 0 = -1sigma, idx 1 = +1sigma).
# Flux is handled separately as a 100-universe set.
KNOB_BANDS = ["2p2h", "CCQEPauliSupViaKF", "FrAbs_pi", "FrElas_N", "HighQ2",
              "LowQ2", "MaCCQE", "MaRES", "MFP_N", "MvRES", "Rvn2pi", "Rvp2pi"]
RHO_CLIP = (1e-2, 1e2)     # per-event ratio clip (positivity / tail guard)
EXPECTED_FLUX_UNIVERSES = 100


def _opt(bank, name):
    p = os.path.join(bank, name)
    return np.load(p).astype(np.float64) if os.path.exists(p) else None


def _load_bank(bank):
    """Return (d, bands, n_flux) WITHOUT loading any weight arrays into memory.
    d is the cv dict for _xsec_for_weights; bands = available knob names; n_flux =
    number of available flux universes. Weight arrays are loaded lazily (the full
    set is ~80 GB in float64 -- never hold them all)."""
    cv = np.load(os.path.join(bank, "cv.npz"))
    d = {k: cv[k] for k in cv.files}
    nedges = sum(1 for k in cv.files if k.startswith("edges_"))
    d["edges"] = [cv[f"edges_{i}"] for i in range(nedges)]
    missing_knob_files = []
    for b in KNOB_BANDS:
        for idx in (0, 1):
            for stem in (f"sig_{b}_t_{idx}", f"sig_{b}_r_{idx}", f"td_{b}_{idx}"):
                if not os.path.exists(os.path.join(bank, f"{stem}.npy")):
                    missing_knob_files.append(f"{stem}.npy")
    if missing_knob_files:
        raise RuntimeError(f"[FAIL] incomplete knob bank: missing {missing_knob_files}")
    bands = list(KNOB_BANDS)

    def flux_ids(prefix):
        out = set()
        for path in glob.glob(os.path.join(bank, f"{prefix}*.npy")):
            suffix = os.path.basename(path)[len(prefix):-4]
            if suffix.isdigit():
                out.add(int(suffix))
        return out

    flux_sets = [flux_ids(p) for p in ("sig_flux_t_", "sig_flux_r_", "td_flux_")]
    if not flux_sets[0] or not (flux_sets[0] == flux_sets[1] == flux_sets[2]):
        raise RuntimeError(f"[FAIL] incomplete/mismatched flux bank IDs: {flux_sets}")
    expected_flux = set(range(EXPECTED_FLUX_UNIVERSES))
    if flux_sets[0] != expected_flux:
        raise RuntimeError(f"[FAIL] flux bank must contain exactly "
                           f"{EXPECTED_FLUX_UNIVERSES} universes: "
                           f"missing={sorted(expected_flux-flux_sets[0])}, "
                           f"extra={sorted(flux_sets[0]-expected_flux)}")
    n_flux = len(expected_flux)
    print(f"[bank] {len(bands)} knob bands, {n_flux} flux universes, "
          f"{d['MCgen'].shape[0]} events, edges {[len(e)-1 for e in d['edges']]}")
    return d, bands, n_flux


def _atomic_savez(path, **arrays):
    """Replace a slab only after the compressed NPZ has closed successfully."""
    path = os.path.abspath(os.fspath(path))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    handle = tempfile.NamedTemporaryFile(
        prefix=os.path.basename(path) + ".", suffix=".tmp.npz",
        dir=os.path.dirname(path), delete=False)
    tmp = handle.name
    handle.close()
    try:
        np.savez_compressed(tmp, **arrays)
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def _ratio(rho, label, invalid_policy="error"):
    """Validate a banked universe/CV ratio with an explicit invalid-value policy."""
    rho = np.asarray(rho, dtype=np.float64)
    bad = ~np.isfinite(rho) | (rho <= 0.0)
    if np.any(bad):
        msg = f"{label}: {int(bad.sum())}/{rho.size} ratios are non-finite or <=0"
        if invalid_policy == "error":
            raise ValueError(msg)
        print(f"[ratio][WARN] {msg}; explicitly replacing with neutral ratio 1", flush=True)
        rho = rho.copy()
        rho[bad] = 1.0
    clipped = (rho < RHO_CLIP[0]) | (rho > RHO_CLIP[1])
    if np.any(clipped):
        print(f"[ratio][WARN] {label}: clipping {int(clipped.sum())}/{rho.size} "
              f"ratios to {RHO_CLIP}", flush=True)
    return np.clip(rho, *RHO_CLIP)


def _knob_ratios(bank, bands, invalid_policy):
    """Load both asymmetric endpoints for every knob and event-weight view."""
    ratios = {}
    for b in bands:
        ratios[b] = {}
        for view, stem in (("t", "sig_{b}_t_{idx}.npy"),
                           ("r", "sig_{b}_r_{idx}.npy"),
                           ("td", "td_{b}_{idx}.npy")):
            minus = _ratio(_opt(bank, stem.format(b=b, idx=0)),
                           f"{b}:{view}:-1", invalid_policy).astype(np.float32)
            plus = _ratio(_opt(bank, stem.format(b=b, idx=1)),
                          f"{b}:{view}:+1", invalid_policy).astype(np.float32)
            ratios[b][view] = (plus, minus)
    return ratios


def _flux_universe(bank, u):
    """Lazy-load the three weight arrays for flux universe u."""
    return (_opt(bank, f"sig_flux_t_{u}.npy"),
            _opt(bank, f"sig_flux_r_{u}.npy"),
            _opt(bank, f"td_flux_{u}.npy"))


def _flux_normalized(slab):
    """True when a slab was produced with per-universe flux normalization (J28).

    Slabs written before the fix carry no stamp; combine refuses them rather than
    folding Phi_CV-normalized flux universes into a fresh adopted covariance.
    rescale_flux_universes.py corrects such a slab in place of a re-throw and
    stamps the result.
    """
    return "flux_normalized" in slab.files and int(slab["flux_normalized"]) == 1


def _flux_ratio_table(args, d, n_flux):
    """Phi_u/Phi_CV per pT bin for every flux universe -- fail-closed (J28).

    A Flux universe reweights the events AND changes the flux integral the xsec
    divides by; applying only the reweights and keeping Phi_CV is the Task #70
    bug. The uthrow banks already carry this table on their own pT grid
    (unified_throw.py --dump writes flux_univ_ratio.npy), so the correction needs
    no re-dump; --flux-universe-file is the fallback. There is no CV fallback.
    """
    if not n_flux:
        return None
    n_pt = len(d["flux"])
    try:
        table = flux_universe.load_banked_flux_ratio_table(args.bank, n_pt, n_flux)
        source = os.path.join(args.bank, flux_universe.BANKED_RATIO_NAME)
    except (RuntimeError, ValueError, OSError) as exc:
        print(f"[bank] no usable banked flux ratio table ({exc});\n"
              f"[bank] rebuilding from {args.flux_universe_file}", flush=True)
        import unfold_2d_omnifold_unbinned as u2d      # ROOT; fallback path only
        table = flux_universe.resolve_flux_ratio_table(
            n_pt=n_pt, n_flux=n_flux, universe_file=args.flux_universe_file,
            pt_edges=d["edges"][0], cv_flux_bins=d["flux"],
            ref_edges=np.asarray(u2d.PT_EDGES, float))
        source = args.flux_universe_file
    spread = float(np.abs(table - 1.0).max())
    print(f"[bank] flux ratio table {table.shape} from {source}: "
          f"max |Phi_u/Phi_CV - 1| = {spread:.4f}")
    return table


def _flux_for_universe(d, table, u):
    """The integrated flux a Flux universe must divide by: Phi_u = Phi_CV * r_u."""
    return np.asarray(d["flux"], float) * table[u]


def do_throws(args):
    d, bands, n_flux = _load_bank(args.bank)
    edges = d["edges"]
    w_truth, w_reco, td_cv = d["w_truth"], d["w_reco"], d["td_w"]
    ratios = _knob_ratios(args.bank, bands, args.invalid_ratio)
    flux_ratio = _flux_ratio_table(args, d, n_flux)

    xs = []
    metas = []
    for j in range(args.throws):
        gj = args.throw_offset + j
        rng = np.random.default_rng(args.seed + gj)
        g = {b: float(rng.standard_normal()) for b in bands}
        rt = np.ones_like(w_truth); rr = np.ones_like(w_reco); rtd = np.ones_like(td_cv)
        for b in bands:
            rt *= interpolate_asymmetric_ratio(g[b], *ratios[b]["t"])
            rr *= interpolate_asymmetric_ratio(g[b], *ratios[b]["r"])
            rtd *= interpolate_asymmetric_ratio(g[b], *ratios[b]["td"])
        wt_j = w_truth * rt; wr_j = w_reco * rr; wtd_j = td_cv * rtd
        if n_flux:
            u = int(rng.integers(n_flux))
            fwt, fwr, fwtd = _flux_universe(args.bank, u)
            wt_j *= _ratio(fwt, f"Flux:{u}:t", args.invalid_ratio)
            wr_j *= _ratio(fwr, f"Flux:{u}:r", args.invalid_ratio)
            wtd_j *= _ratio(fwtd, f"Flux:{u}:td", args.invalid_ratio)
            # ...and divide by THAT universe's flux integral, not the CV one (J28).
            flux_j = _flux_for_universe(d, flux_ratio, u)
        else:
            u = -1
            flux_j = None
        # Systematic throws all use the SAME estimator seed. ML variation belongs
        # exclusively in C_ML and must not leak into C_syst.
        x = _xsec_for_weights(d, edges, wt_j, wr_j, wtd_j, args.iters, args.seed,
                              flux=flux_j)
        xs.append(x.ravel(order="C"))
        metas.append((gj, u))
        print(f"[throw {gj}] flux_u={u} sum(x)={x.sum():.4e}", flush=True)
        # save incrementally so a killed job (e.g. interactive alloc expiry) keeps
        # every completed throw rather than losing the whole slab.
        _atomic_savez(args.out, xs=np.array(xs),
                      throws=np.array([m[0] for m in metas]),
                      flux_u=np.array([m[1] for m in metas]),
                      seed=np.int64(args.seed),
                      flux_normalized=np.int64(1),
                      bands=np.array(bands, dtype=object))
    print(f"[throws] wrote {args.out}: xs{np.array(xs).shape}")


def do_blockunits(args):
    """Producer for the block-sum: compute the xsec vector for each assigned
    block universe (both knob endpoints and/or flux index) and save them. Parallelises
    the otherwise-serial 112-unfold block-sum exactly like the throws. Combine
    aggregates these. --block-knobs all|csv ; --block-flux LO-HI (inclusive)."""
    d, bands, n_flux = _load_bank(args.bank)
    edges = d["edges"]
    w_truth, w_reco, td_cv = d["w_truth"], d["w_reco"], d["td_w"]
    flux_ratio = _flux_ratio_table(args, d, n_flux) if args.block_flux else None
    xs, labels, kinds = [], [], []

    knob_list = bands if args.block_knobs == "all" else [b for b in args.block_knobs.split(",") if b in bands]
    for b in knob_list:
        for idx, sign in ((0, "minus"), (1, "plus")):
            wt = w_truth * _ratio(_opt(args.bank, f"sig_{b}_t_{idx}.npy"),
                                  f"{b}:{sign}:t", args.invalid_ratio)
            wr = w_reco * _ratio(_opt(args.bank, f"sig_{b}_r_{idx}.npy"),
                                 f"{b}:{sign}:r", args.invalid_ratio)
            wtd = td_cv * _ratio(_opt(args.bank, f"td_{b}_{idx}.npy"),
                                 f"{b}:{sign}:td", args.invalid_ratio)
            # knob endpoints do not move the flux integral: CV flux is correct here
            x = _xsec_for_weights(d, edges, wt, wr, wtd, args.iters, args.seed).ravel(order="C")
            xs.append(x); labels.append(f"{b}:{idx}"); kinds.append("knob")
            print(f"[blockunit] knob {b} {sign} done", flush=True)
            _atomic_savez(args.out, xs=np.array(xs), labels=np.array(labels, dtype=object),
                          seed=np.int64(args.seed),
                          flux_normalized=np.int64(1),
                          kinds=np.array(kinds, dtype=object))
    if args.block_flux:
        lo, hi = (int(x) for x in args.block_flux.split("-"))
        for u in range(lo, min(hi, n_flux - 1) + 1):
            fwt, fwr, fwtd = _flux_universe(args.bank, u)
            x = _xsec_for_weights(
                d, edges,
                w_truth * _ratio(fwt, f"Flux:{u}:t", args.invalid_ratio),
                w_reco * _ratio(fwr, f"Flux:{u}:r", args.invalid_ratio),
                td_cv * _ratio(fwtd, f"Flux:{u}:td", args.invalid_ratio),
                args.iters, args.seed,
                flux=_flux_for_universe(d, flux_ratio, u)).ravel(order="C")
            xs.append(x); labels.append(f"flux{u}"); kinds.append("flux")
            print(f"[blockunit] flux {u} done", flush=True)
            _atomic_savez(args.out, xs=np.array(xs), labels=np.array(labels, dtype=object),
                          seed=np.int64(args.seed),
                          flux_normalized=np.int64(1),
                          kinds=np.array(kinds, dtype=object))
    print(f"[blockunit] wrote {args.out}: {len(xs)} units")


def do_combine(args):
    d, bands, n_flux = _load_bank(args.bank)
    edges = d["edges"]
    w_truth, w_reco, td_cv = d["w_truth"], d["w_reco"], d["td_w"]

    # CV xsec (reported-bin mask)
    x_cv = _xsec_for_weights(d, edges, w_truth, w_reco, td_cv, args.iters, args.seed).ravel(order="C")
    rep = x_cv > 0
    base = x_cv[rep]
    nrep = int(rep.sum())
    print(f"[combine] reported bins = {nrep}")

    # unified covariance over all throws
    slabs = sorted(glob.glob(args.combine))
    if not slabs:
        raise SystemExit(f"no slabs match {args.combine}")
    slab_rows = []
    throw_ids = []
    slab_seeds = set()
    unnormalized = []
    for s in slabs:
        z = np.load(s, allow_pickle=True)
        if "seed" in z.files:
            slab_seeds.add(int(z["seed"]))
        if not _flux_normalized(z):
            unnormalized.append(s)
        xx = np.asarray(z["xs"], dtype=float)
        ids = np.asarray(z["throws"], dtype=int)
        if xx.ndim != 2 or xx.shape[0] != ids.size or xx.shape[1] != x_cv.size:
            raise SystemExit(f"[FAIL] malformed throw slab {s}: xs={xx.shape}, ids={ids.shape}")
        if not np.all(np.isfinite(xx)):
            raise SystemExit(f"[FAIL] non-finite throw output in {s}")
        slab_rows.append(xx)
        throw_ids.extend(ids.tolist())
    if len(throw_ids) != len(set(throw_ids)):
        raise SystemExit("[FAIL] duplicate throw ids across slabs")
    if not args.expected_throws:
        raise SystemExit("[FAIL] --expected-throws LO-HI is required for combine")
    throw_lo, throw_hi = (int(v) for v in args.expected_throws.split("-", 1))
    expected_throw_ids = set(range(throw_lo, throw_hi + 1))
    got_throw_ids = set(throw_ids)
    if got_throw_ids != expected_throw_ids:
        raise SystemExit(f"[FAIL] throw id mismatch: "
                         f"missing={sorted(expected_throw_ids-got_throw_ids)} "
                         f"extra={sorted(got_throw_ids-expected_throw_ids)}")
    X = np.concatenate(slab_rows, axis=0)[:, rep]
    T = X.shape[0]
    C_uni, mean_shift = joint_throw_covariance(X, base)
    print(f"[combine] {T} throws from {len(slabs)} slabs")
    print(f"[combine] joint-throw mean shift: norm={np.linalg.norm(mean_shift):.4e}, "
          f"max|shift|={np.max(np.abs(mean_shift)):.4e}")

    # block-sum covariance from precomputed block-unit slabs (knobs summed as
    # outer(delta); flux averaged then added). Falls back to inline if no slabs.
    C_block = np.zeros((nrep, nrep))
    bslabs = sorted(glob.glob(args.block_slabs)) if args.block_slabs else []
    if not bslabs:
        raise SystemExit(f"no block-unit slabs match {args.block_slabs}; run --blockunits first")
    flux_x = {}
    knob_x = {}
    for s in bslabs:
        z = np.load(s, allow_pickle=True)
        if "seed" in z.files:
            slab_seeds.add(int(z["seed"]))
        if not _flux_normalized(z):
            unnormalized.append(s)
        xx = np.asarray(z["xs"], dtype=float)
        if xx.ndim != 2 or xx.shape[1] != x_cv.size or not np.all(np.isfinite(xx)):
            raise SystemExit(f"[FAIL] malformed/non-finite block slab {s}: {xx.shape}")
        for x, label, kind in zip(xx, z["labels"], z["kinds"]):
            if str(kind) == "knob":
                band, idx = str(label).rsplit(":", 1)
                if idx not in ("0", "1") or idx in knob_x.setdefault(band, {}):
                    raise SystemExit(f"[FAIL] duplicate/malformed knob endpoint {label}")
                knob_x[band][idx] = x[rep]
            elif str(kind) == "flux":
                text = str(label)
                if not text.startswith("flux") or not text[4:].isdigit():
                    raise SystemExit(f"[FAIL] malformed flux block label {label}")
                flux_id = int(text[4:])
                if flux_id in flux_x:
                    raise SystemExit(f"[FAIL] duplicate flux block universe {flux_id}")
                flux_x[flux_id] = x[rep]
            else:
                raise SystemExit(f"[FAIL] unknown block kind {kind}")
    if set(knob_x) != set(bands):
        raise SystemExit(f"[FAIL] knob block inventory mismatch: "
                         f"missing={sorted(set(bands)-set(knob_x))} "
                         f"extra={sorted(set(knob_x)-set(bands))}")
    for band in sorted(knob_x):
        if set(knob_x[band]) != {"0", "1"}:
            raise SystemExit(f"[FAIL] {band} block is missing a +/- endpoint: {sorted(knob_x[band])}")
        C_block += mat_covariance(np.stack([knob_x[band]["0"], knob_x[band]["1"]]))
    expected_flux_ids = set(range(n_flux))
    if set(flux_x) != expected_flux_ids:
        raise SystemExit(f"[FAIL] flux block inventory mismatch: "
                         f"missing={sorted(expected_flux_ids-set(flux_x))} "
                         f"extra={sorted(set(flux_x)-expected_flux_ids)}")
    if flux_x:
        C_flux = mat_covariance(np.asarray([flux_x[u] for u in sorted(flux_x)]))
        C_block += C_flux
        print(f"[block] {len(knob_x)} +/- knobs + flux ({len(flux_x)} univ, "
              f"sqrt-tr={np.sqrt(np.trace(C_flux)):.3e}); MAT mean-centered 1/N")
    else:
        print(f"[block] {len(knob_x)} +/- knobs (no flux units); MAT mean-centered 1/N")

    # F2 guard: every throw/block slab must have been produced at the same
    # estimator seed as this combine (--seed), else C_uni/C_block would mix
    # estimator jitter across slabs. Seed is stamped by do_throws/do_blockunits.
    if slab_seeds and slab_seeds != {int(args.seed)}:
        raise SystemExit(f"[FAIL] slabs carry estimator seed(s) {sorted(slab_seeds)} != "
                         f"--seed {args.seed}; refusing mixed-seed combine")
    # J28 guard: a slab whose flux universes divided by the CV integral must not
    # be folded into a fresh covariance. Correct it with rescale_flux_universes.py
    # (exact, no re-unfold) or re-throw with the current code.
    if unnormalized:
        raise SystemExit(
            f"[FAIL] {len(unnormalized)} slab(s) carry no per-universe flux "
            f"normalization stamp, e.g. {unnormalized[0]}. They were produced "
            "before the J28 fix, so their Flux universes divided by the CV flux "
            "integral. Run rescale_flux_universes.py over them (exact post-hoc "
            "correction, no re-unfold) or regenerate the throws/blocks.")
    if not slab_seeds:
        raise SystemExit("[FAIL] slabs carry no estimator-seed stamp; refusing combine to "
                         "prevent accidental reuse of pre-remediation products -- regenerate "
                         "throws/blocks with the current code (they stamp the seed)")

    st_uni = float(np.sqrt(np.trace(C_uni)))
    st_block = float(np.sqrt(np.trace(C_block)))
    # Fixed-seed null: this must be exactly zero (within floating tolerance).
    # No scalar trace correction is applied: the stored covariance itself is the
    # mean-centered, fixed-estimator systematic covariance. ML lives only in C_ML.
    null_norm = None
    if args.null:
        x_cv2 = _xsec_for_weights(d, edges, w_truth, w_reco, td_cv, args.iters,
                                  args.seed).ravel(order="C")[rep]
        null_norm = float(np.linalg.norm(x_cv2 - base))
        tol = 1e-12 * max(float(np.linalg.norm(base)), 1.0)
        print(f"\n[null] fixed-seed ||CV2-CV|| = {null_norm:.3e} (tol={tol:.3e})")
        if null_norm > tol:
            raise SystemExit("[FAIL] CV re-unfold is non-deterministic at the fixed estimator "
                             "seed; the throws cannot be cleanly separated from C_ML "
                             "(this checks CV determinism only; per-slab seed provenance is "
                             "enforced separately below)")

    # cross term = unified - block (the nonlinear piece block-sum drops)
    C_cross = C_uni - C_block
    st_cross = float(np.sqrt(abs(np.trace(C_cross))))
    du = np.sqrt(np.clip(np.diag(C_uni), 0, None))
    db = np.sqrt(np.clip(np.diag(C_block), 0, None))
    med_ratio = float(np.median(du[db > 0] / db[db > 0]))
    print("\n===== Unified-throw vs block-sum =====")
    print(f"  sqrt-trace  unified={st_uni:.4e}  block={st_block:.4e}  "
          f"ratio={st_uni/st_block:.3f}")
    print(f"  sqrt-trace cross-term (unified-block) = {st_cross:.4e}  "
          f"({100*st_cross/st_block:.1f}% of block)")
    print(f"  per-bin sigma ratio unified/block: median={med_ratio:.3f}")
    print("  (throws and block endpoints share one estimator seed; the joint covariance is "
          "mean-centered and its mean shift is reported separately. ratio>>1 => the unfolding combines bands NONLINEARLY and "
          "the block-sum underestimates; ratio~1 => block-sum is a good approximation.)")

    if args.out_root:
        import ROOT
        os.makedirs(os.path.dirname(args.out_root) or ".", exist_ok=True)
        fo = ROOT.TFile.Open(args.out_root, "RECREATE")
        for name, M in [("C_unified", C_uni), ("C_blocksum", C_block), ("C_cross", C_cross)]:
            h = ROOT.TH2D(name, name, nrep, 0, nrep, nrep, 0, nrep)
            for i in range(nrep):
                for k in range(nrep):
                    h.SetBinContent(i + 1, k + 1, float(M[i, k]))
            h.Write()
        ROOT.TParameter("double")("sqrt_tr_unified", st_uni).Write()
        ROOT.TParameter("double")("sqrt_tr_block", st_block).Write()
        ROOT.TParameter("double")("joint_mean_shift_norm", float(np.linalg.norm(mean_shift))).Write()
        # NULL-AS-ABSENT, closed 2026-08-11 (quarantine cause 4). `fixed_seed_null_norm` is still
        # written only when the check ran -- a number nobody measured must not be invented -- but
        # `fixed_seed_null_checked` is now written UNCONDITIONALLY beside it. Without that flag, a
        # product built without `--null` carries no null key at all, and a downstream criterion phrased
        # as "the null norm is not large" PASSES ON IT VACUOUSLY: absence is indistinguishable from
        # zero. The flag makes "nobody checked" a readable state rather than an inference from a
        # missing key, so a consumer can fail closed on `checked == 0`.
        ROOT.TParameter("int")("fixed_seed_null_checked", 1 if null_norm is not None else 0).Write()
        if null_norm is not None:
            ROOT.TParameter("double")("fixed_seed_null_norm", null_norm).Write()
        ROOT.TParameter("int")("n_throws", T).Write()
        hs = ROOT.TH1D("hJointMeanShift", "joint throw mean minus CV", nrep, 0, nrep)
        for i, value in enumerate(mean_shift):
            hs.SetBinContent(i + 1, float(value))
        hs.Write()
        fo.Close()
        print(f"[combine] wrote {args.out_root}")
    return {
        "C_unified": C_uni,
        "C_blocksum": C_block,
        "C_cross": C_cross,
        "mean_shift": mean_shift,
        "x_cv_reported": base,
        "throw_ids": np.asarray(throw_ids, dtype=int),
        "fixed_seed_null_norm": null_norm,
        # Same reason as the ROOT stamp above: a consumer of this dict must be able to distinguish
        # "checked and zero" from "not checked", and `None` alone invites `or 0.0`.
        "fixed_seed_null_checked": null_norm is not None,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bank", default="bank_uthrow")
    ap.add_argument("--flux-universe-file",
                    default=f"{_REPO}/2d-unfolding/baseline_flux/"
                            "flux_integral_universes_MEFHC.root",
                    help="ROOT (hFluxCV/hFluxUniv) per-PPFX flux integrals, used to "
                         "divide each Flux universe by its own Phi_u. Only consulted "
                         "when the bank carries no flux_univ_ratio.npy.")
    ap.add_argument("--throws", type=int, default=0, help="number of throws this task")
    ap.add_argument("--throw-offset", type=int, default=0)
    ap.add_argument("--seed", type=int, default=1000)
    ap.add_argument("--iters", type=int, default=5)
    ap.add_argument("--out", default="uthrow_slab.npz")
    ap.add_argument("--combine", default=None, help="glob of throw slab npzs to aggregate")
    ap.add_argument("--block-slabs", default=None, help="glob of block-unit slabs (combine)")
    ap.add_argument("--expected-throws", default=None,
                    help="required exact throw-ID range LO-HI for combine")
    ap.add_argument("--blockunits", action="store_true", help="producer for block-sum units")
    ap.add_argument("--block-knobs", default="all", help="all|csv of knob bands")
    ap.add_argument("--block-flux", default=None, help="flux index range LO-HI (inclusive)")
    ap.add_argument("--null", action="store_true",
                    help="(combine) repeat the CV at the identical seed and require a null result")
    ap.add_argument("--invalid-ratio", choices=("error", "neutral"), default="error",
                    help="policy for zero/non-finite bank ratios; default fails loudly")
    ap.add_argument("--out-root", default=None)
    args = ap.parse_args()
    if args.combine:
        do_combine(args)
    elif args.blockunits:
        do_blockunits(args)
    elif args.throws > 0:
        do_throws(args)
    else:
        ap.error("pass --throws N, --blockunits, or --combine GLOB")


if __name__ == "__main__":
    main()
