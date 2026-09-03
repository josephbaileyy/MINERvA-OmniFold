#!/usr/bin/env python3
"""Post-hoc correction of Phi_CV-normalized Flux universes in saved slabs (J28).

Every saved unified-throw and block-unit universe divided by the CV flux integral
Phi_CV instead of its own Phi_u. Re-unfolding is not required to fix this: flux
normalization enters only at final extraction, and `extract_cross_section_nd`
divides by the flux along the pT axis alone, so the saved cross section is exactly
linear in 1/Phi(pT). A universe saved with Phi_CV is corrected by

    x_corrected[i_pt, ...] = x_saved[i_pt, ...] / r_u[i_pt],
    r_u = Phi_u / Phi_CV   (per pT bin, from the throw's own saved flux-universe ID)

This is an identity, not an approximation, and it is why the exact corrected
covariance is cheap. Given the corrected slabs the tool rebuilds, with the same
estimators the combine uses (uq_math):

    C_unified   joint mean-centered throw covariance (mat_covariance)
    mean_shift  joint throw mean minus CV, reported separately
    C_blocksum  sum_b MAT(knob_b-, knob_b+) + MAT({flux universes})
    C_cross     C_unified - C_blocksum
    g           per-bin inflation sqrt(max(v_uni, v_block)) / sqrt(v_block),
                the adopt_unified_5d.py:86 construction, in both the
                mean-centered and --cv-centered (mean-shift^2 added) variants

What it does NOT do: adopt anything. It writes its own output and prints a
before/after comparison. Correcting the same Flux draw in the unified and block
ensembles moves g, the tail inflation and the finite-throw cross terms together,
so the corrected numbers are only meaningful when computed from the real slabs --
which live on /pscratch. Do not quote a first-order estimate in their place.

Knob endpoints are left alone: a knob universe does not move the flux integral,
so CV flux was already the right denominator there.

  # correct slabs in place of a re-throw, then combine as usual
  python rescale_flux_universes.py \
      --throw-slabs 'uq_5d/uthrow5d_slab_*.npz' \
      --block-slabs 'uq_5d/block5d_*.npz' \
      --bank bank_uthrow_5d --cv products/5d/xsec_5d_MEFHC_5iter_lgbm.root \
      --out-dir uq_5d/rescaled --out-root uq_5d/unified_throw_cov_5d_fluxfix.root
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
# OI-136: root derived from __file__, never the hardcoded cluster root
_CODE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (f"{_CODE_ROOT}/2d-unfolding", f"{_CODE_ROOT}/nd-unfolding"):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import flux_universe
from uq_math import joint_throw_covariance, mat_covariance


def load_cv_flat(path):
    """Flat CV xsec vector from a product ROOT (hXSecND_flat) or an .npy/.npz."""
    if path.endswith(".npy"):
        return np.asarray(np.load(path), float).ravel(order="C")
    if path.endswith(".npz"):
        with np.load(path) as z:
            key = "x_cv" if "x_cv" in z.files else z.files[0]
            return np.asarray(z[key], float).ravel(order="C")
    import ROOT
    f = ROOT.TFile.Open(path, "READ")
    if not f or f.IsZombie():
        raise SystemExit(f"[FAIL] cannot open CV product {path}")
    try:
        h = f.Get("hXSecND_flat")
        if not h:
            raise SystemExit(f"[FAIL] {path} has no hXSecND_flat")
        return np.asarray([h.GetBinContent(i + 1) for i in range(h.GetNbinsX())], float)
    finally:
        f.Close()


def bank_geometry(bank):
    """(shape, pt_edges, cv_flux, n_flux_in_bank) from the throw bank's cv.npz."""
    cv = np.load(os.path.join(bank, "cv.npz"), allow_pickle=True)
    n_edges = sum(1 for k in cv.files if k.startswith("edges_"))
    edges = [np.asarray(cv[f"edges_{i}"], float) for i in range(n_edges)]
    shape = tuple(len(e) - 1 for e in edges)
    n_flux = len({int(fn.split("_")[-1].split(".")[0])
                  for fn in os.listdir(bank) if fn.startswith("sig_flux_t_")})
    return shape, edges[0], np.asarray(cv["flux"], float), (n_flux or None)


def _already_normalized(z):
    return "flux_normalized" in z.files and int(z["flux_normalized"]) == 1


def rescale_throw_slab(z, divisors):
    """Correct every throw row by its own saved flux-universe ID.

    `divisors[u]` is the flat per-bin r_u. A throw with flux_u < 0 drew no flux
    universe (n_flux == 0 bank) and is already correct.
    """
    xs = np.asarray(z["xs"], float)
    flux_u = np.asarray(z["flux_u"], int)
    if flux_u.size != xs.shape[0]:
        raise SystemExit(f"[FAIL] slab has {xs.shape[0]} rows but {flux_u.size} flux IDs")
    out = xs.copy()
    touched = 0
    for j, u in enumerate(flux_u):
        if u < 0:
            continue
        if u not in divisors:
            raise SystemExit(f"[FAIL] throw row {j} cites flux universe {u}, which the "
                             "flux ratio table does not cover")
        out[j] = xs[j] / divisors[u]
        touched += 1
    return out, touched


def rescale_block_slab(z, divisors):
    """Correct the `flux` block units; leave `knob` endpoints at CV flux."""
    xs = np.asarray(z["xs"], float)
    labels = [str(v) for v in z["labels"]]
    kinds = [str(v) for v in z["kinds"]]
    out = xs.copy()
    touched = 0
    for i, (label, kind) in enumerate(zip(labels, kinds)):
        if kind != "flux":
            continue
        if not label.startswith("flux") or not label[4:].isdigit():
            raise SystemExit(f"[FAIL] malformed flux block label {label!r}")
        u = int(label[4:])
        if u not in divisors:
            raise SystemExit(f"[FAIL] block unit {label} cites a flux universe the "
                             "ratio table does not cover")
        out[i] = xs[i] / divisors[u]
        touched += 1
    return out, touched


def build_covariances(throw_rows, block_slabs, base, rep):
    """C_unified / mean_shift / C_blocksum / C_cross on the reported bins.

    Mirrors unified_throw_cov.do_combine exactly, so the before/after difference
    is the flux normalization and nothing else.
    """
    X = np.concatenate(throw_rows, axis=0)[:, rep]
    C_uni, mean_shift = joint_throw_covariance(X, base)

    knob_x, flux_x = {}, {}
    for xs, labels, kinds in block_slabs:
        for x, label, kind in zip(xs, labels, kinds):
            if kind == "knob":
                band, idx = label.rsplit(":", 1)
                knob_x.setdefault(band, {})[idx] = x[rep]
            elif kind == "flux":
                flux_x[int(label[4:])] = x[rep]
            else:
                raise SystemExit(f"[FAIL] unknown block kind {kind}")
    nrep = int(rep.sum())
    C_block = np.zeros((nrep, nrep))
    for band in sorted(knob_x):
        if set(knob_x[band]) != {"0", "1"}:
            raise SystemExit(f"[FAIL] {band} block is missing a +/- endpoint")
        C_block += mat_covariance(np.stack([knob_x[band]["0"], knob_x[band]["1"]]))
    C_flux = None
    if flux_x:
        C_flux = mat_covariance(np.asarray([flux_x[u] for u in sorted(flux_x)]))
        C_block += C_flux
    return C_uni, mean_shift, C_block, C_uni - C_block, C_flux, X.shape[0]


def inflation_g(C_uni, C_block, mean_shift=None):
    """adopt_unified_5d.py:86 per-bin inflation g = sqrt(max(v_uni, v_b)) / sqrt(v_b)."""
    vu = np.clip(np.diag(C_uni), 0, None)
    vb = np.clip(np.diag(C_block), 0, None)
    if mean_shift is not None:
        vu = vu + np.asarray(mean_shift, float) ** 2
    sb = np.sqrt(vb)
    g = np.ones(vu.size)
    m = sb > 0
    g[m] = np.sqrt(np.maximum(vu, vb))[m] / sb[m]
    return g


def _summary(tag, C_uni, C_block, C_cross, mean_shift, g, g_cv):
    return {
        "tag": tag,
        "sqrt_tr_unified": float(np.sqrt(np.trace(C_uni))),
        "sqrt_tr_blocksum": float(np.sqrt(np.trace(C_block))),
        "sqrt_tr_cross": float(np.sqrt(abs(np.trace(C_cross)))),
        "joint_mean_shift_norm": float(np.linalg.norm(mean_shift)),
        "g_mean": float(g.mean()), "g_max": float(g.max()),
        "g_cvcentered_mean": float(g_cv.mean()), "g_cvcentered_max": float(g_cv.max()),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--throw-slabs", required=True, help="glob of unified-throw slabs")
    ap.add_argument("--block-slabs", required=True, help="glob of block-unit slabs")
    ap.add_argument("--bank", required=True, help="throw bank (cv.npz + flux_univ_ratio.npy)")
    ap.add_argument("--cv", required=True,
                    help="CV product ROOT (hXSecND_flat) or .npy/.npz flat CV xsec")
    ap.add_argument("--flux-universe-file",
                    default=f"{_REPO}/2d-unfolding/baseline_flux/"
                            "flux_integral_universes_MEFHC.root",
                    help="fallback source of Phi_u/Phi_CV when the bank carries no "
                         "flux_univ_ratio.npy")
    ap.add_argument("--out-dir", default=None,
                    help="write the corrected slabs here (stamped flux_normalized=1) "
                         "so unified_throw_cov.py --combine will accept them")
    ap.add_argument("--out-root", default=None, help="corrected C_unified/C_blocksum/g")
    ap.add_argument("--out-json", default=None, help="before/after summary")
    ap.add_argument("--allow-normalized", action="store_true",
                    help="proceed even if a slab is already stamped flux_normalized "
                         "(default refuses: correcting twice divides by r_u squared)")
    args = ap.parse_args()

    shape, pt_edges, cv_flux, n_flux = bank_geometry(args.bank)
    # Prefer the bank's own table: it is already on the bank's pT grid, and taking
    # it needs neither ROOT nor the flux file. Only the fallback pulls in u2d for
    # the reference pT edges, so a bank that carries its table stays importable
    # off-cluster. Either way there is no CV fallback -- both paths raise.
    try:
        ratio = flux_universe.load_banked_flux_ratio_table(args.bank, shape[0], n_flux)
        ratio_src = os.path.join(args.bank, flux_universe.BANKED_RATIO_NAME)
    except (RuntimeError, ValueError, OSError) as exc:
        print(f"[rescale] bank table unusable ({exc});\n"
              f"[rescale] falling back to {args.flux_universe_file}")
        import unfold_2d_omnifold_unbinned as u2d      # ROOT; this path only
        ratio = flux_universe.resolve_flux_ratio_table(
            n_pt=shape[0], n_flux=n_flux, universe_file=args.flux_universe_file,
            pt_edges=pt_edges, cv_flux_bins=cv_flux,
            ref_edges=np.asarray(u2d.PT_EDGES, float))
        ratio_src = args.flux_universe_file
    divisors = {u: flux_universe.flat_flux_divisor(ratio[u], shape)
                for u in range(ratio.shape[0])}
    print(f"[rescale] bank {args.bank}: shape={shape} flux universes={ratio.shape[0]} "
          f"max |r_u - 1| = {float(np.abs(ratio - 1.0).max()):.4f} "
          f"(ratios from {ratio_src})")

    x_cv = load_cv_flat(args.cv)
    if x_cv.size != int(np.prod(shape)):
        raise SystemExit(f"[FAIL] CV vector has {x_cv.size} bins, bank shape {shape} "
                         f"implies {int(np.prod(shape))}")
    rep = x_cv > 0
    base = x_cv[rep]
    print(f"[rescale] reported bins = {int(rep.sum())}")

    tslabs = sorted(glob.glob(args.throw_slabs))
    bslabs = sorted(glob.glob(args.block_slabs))
    if not tslabs:
        raise SystemExit(f"[FAIL] no throw slabs match {args.throw_slabs}")
    if not bslabs:
        raise SystemExit(f"[FAIL] no block slabs match {args.block_slabs}")

    old_throws, new_throws, corrected = [], [], 0
    for path in tslabs:
        with np.load(path, allow_pickle=True) as z:
            if _already_normalized(z) and not args.allow_normalized:
                raise SystemExit(
                    f"[FAIL] {path} is already stamped flux_normalized=1; rescaling it "
                    "again would divide by r_u twice. Pass --allow-normalized only if "
                    "you know the stamp is wrong.")
            xs_new, touched = rescale_throw_slab(z, divisors)
            payload = {k: z[k] for k in z.files}
        old_throws.append(np.asarray(payload["xs"], float))
        new_throws.append(xs_new)
        corrected += touched
        if args.out_dir:
            os.makedirs(args.out_dir, exist_ok=True)
            payload["xs"] = xs_new
            payload["flux_normalized"] = np.int64(1)
            payload["flux_rescaled_from"] = np.array(os.path.abspath(path))
            np.savez_compressed(os.path.join(args.out_dir, os.path.basename(path)),
                                **payload)
        print(f"[rescale] {os.path.basename(path)}: {touched}/{len(xs_new)} throws corrected")

    old_blocks, new_blocks, bcorrected = [], [], 0
    for path in bslabs:
        with np.load(path, allow_pickle=True) as z:
            if _already_normalized(z) and not args.allow_normalized:
                raise SystemExit(f"[FAIL] {path} is already stamped flux_normalized=1")
            xs_new, touched = rescale_block_slab(z, divisors)
            payload = {k: z[k] for k in z.files}
            labels = [str(v) for v in z["labels"]]
            kinds = [str(v) for v in z["kinds"]]
        old_blocks.append((np.asarray(payload["xs"], float), labels, kinds))
        new_blocks.append((xs_new, labels, kinds))
        bcorrected += touched
        if args.out_dir:
            os.makedirs(args.out_dir, exist_ok=True)
            payload["xs"] = xs_new
            payload["flux_normalized"] = np.int64(1)
            payload["flux_rescaled_from"] = np.array(os.path.abspath(path))
            np.savez_compressed(os.path.join(args.out_dir, os.path.basename(path)),
                                **payload)
        print(f"[rescale] {os.path.basename(path)}: {touched}/{len(xs_new)} flux block "
              "units corrected")

    if corrected == 0 and bcorrected == 0:
        raise SystemExit("[FAIL] no flux universes were corrected; the slabs cite no "
                         "flux universe at all, so these are not the J28-affected slabs")

    results = {}
    for tag, throws, blocks in (("before", old_throws, old_blocks),
                                ("after", new_throws, new_blocks)):
        C_uni, ms, C_block, C_cross, C_flux, T = build_covariances(throws, blocks, base, rep)
        g = inflation_g(C_uni, C_block)
        g_cv = inflation_g(C_uni, C_block, mean_shift=ms)
        results[tag] = _summary(tag, C_uni, C_block, C_cross, ms, g, g_cv)
        results[tag]["n_throws"] = int(T)
        results[tag]["sqrt_tr_flux_block"] = (
            None if C_flux is None else float(np.sqrt(np.trace(C_flux))))
        if tag == "after":
            after = (C_uni, ms, C_block, C_cross, g, g_cv)

    print("\n===== flux-universe rescale: before -> after =====")
    for key in ("sqrt_tr_unified", "sqrt_tr_blocksum", "sqrt_tr_cross",
                "sqrt_tr_flux_block", "joint_mean_shift_norm", "g_mean", "g_max"):
        b, a = results["before"][key], results["after"][key]
        if b is None or a is None:
            continue
        delta = f"{100 * (a / b - 1):+.2f}%" if b else "n/a"
        print(f"  {key:24s} {b:.6e} -> {a:.6e}   ({delta})")
    print(f"  throws={results['after']['n_throws']}  corrected rows={corrected}  "
          f"corrected block units={bcorrected}")
    print("  (computed from the slabs given; this is the exact corrected covariance for "
          "THOSE slabs, not an extrapolation)")

    if args.out_json:
        os.makedirs(os.path.dirname(args.out_json) or ".", exist_ok=True)
        with open(args.out_json, "w") as fh:
            json.dump({"bank": os.path.abspath(args.bank),
                       "throw_slabs": [os.path.abspath(p) for p in tslabs],
                       "block_slabs": [os.path.abspath(p) for p in bslabs],
                       "results": results}, fh, indent=2)
        print(f"[rescale] wrote {args.out_json}")

    if args.out_root:
        import ROOT
        C_uni, ms, C_block, C_cross, g, g_cv = after
        nrep = C_uni.shape[0]
        os.makedirs(os.path.dirname(args.out_root) or ".", exist_ok=True)
        fo = ROOT.TFile.Open(args.out_root, "RECREATE")
        for name, M in (("C_unified", C_uni), ("C_blocksum", C_block),
                        ("C_cross", C_cross)):
            h = ROOT.TH2D(name, name, nrep, 0, nrep, nrep, 0, nrep)
            for i in range(nrep):
                for k in range(nrep):
                    h.SetBinContent(i + 1, k + 1, float(M[i, k]))
            h.Write()
        for name, v in (("hJointMeanShift", ms), ("hInflationG", g),
                        ("hInflationG_cvcentered", g_cv)):
            h = ROOT.TH1D(name, name, nrep, 0, nrep)
            for i, value in enumerate(v):
                h.SetBinContent(i + 1, float(value))
            h.Write()
        ROOT.TParameter("double")("sqrt_tr_unified",
                                  results["after"]["sqrt_tr_unified"]).Write()
        ROOT.TParameter("double")("sqrt_tr_block",
                                  results["after"]["sqrt_tr_blocksum"]).Write()
        ROOT.TParameter("double")("joint_mean_shift_norm",
                                  results["after"]["joint_mean_shift_norm"]).Write()
        ROOT.TParameter("int")("n_throws", results["after"]["n_throws"]).Write()
        ROOT.TParameter("int")("flux_normalized", 1).Write()
        fo.Close()
        print(f"[rescale] wrote {args.out_root}")


if __name__ == "__main__":
    main()
