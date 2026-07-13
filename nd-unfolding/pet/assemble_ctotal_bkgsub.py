#!/usr/bin/env python3
"""Phase 8: assemble the corrected PET C_total and project the 4D marginal.

C_total = C_syst + C_stat + C_ml (+ C_lateral when available), all on ONE
corrected-nominal reported-bin mask/order (10,550 bins). Then build the EXACT
5D->4D density projection matrix M (integrate over W with its bin widths, since
the PET xsec is a density d^5sigma/prod dx_a) and form the 4D marginal
C_4D = M C_5D M^T, projecting the central value with the same convention.

Runs on the login node (pure numpy). Components are the npz products written by
combine_cstat_bkgsub / combine_cml_bkgsub / build_csyst_prelim_bkgsub, each
carrying `C_*`, `reported_mask` (65856-len bool), and `cv` (65856 xsec_flat).
"""
import argparse
import json
import os

import numpy as np

SHAPE5 = (14, 16, 7, 7, 6)   # pt, pz, eavail, q3, W (corrected 5D reporting grid)


def build_5d_to_4d_projection(reported_mask, shape5, w_edges):
    """M (n4d_rep, n5d_rep): 4D density = integral over W of the 5D density.
    M[q,p] = dW_{m(p)} if the 4D bin of p == 4D bin q, else 0."""
    shape5 = tuple(int(s) for s in shape5)
    shape4 = shape5[:4]
    dW = np.diff(np.asarray(w_edges, float))
    if len(dW) != shape5[4]:
        raise ValueError(f"W edges give {len(dW)} bins != shape5[4]={shape5[4]}")
    rep5 = np.asarray(reported_mask, bool).ravel()
    if rep5.size != int(np.prod(shape5)):
        raise ValueError(f"reported_mask size {rep5.size} != prod(shape5) {np.prod(shape5)}")
    rep5_idx = np.flatnonzero(rep5)
    idx5 = np.unravel_index(rep5_idx, shape5)
    q4 = np.ravel_multi_index(idx5[:4], shape4)
    wcol = dW[idx5[4]]
    rep4_idx = np.unique(q4)
    pos = {int(q): a for a, q in enumerate(rep4_idx)}
    rows = np.fromiter((pos[int(q)] for q in q4), dtype=np.int64, count=q4.size)
    M = np.zeros((rep4_idx.size, rep5_idx.size))
    M[rows, np.arange(rep5_idx.size)] = wcol
    return M, rep5_idx, rep4_idx, shape4


def psd_diagnostics(C):
    Cs = 0.5 * (C + C.T)
    ev = np.linalg.eigvalsh(Cs)
    return {"symmetry_max_abs_asym": float(np.abs(C - C.T).max()),
            "min_eig": float(ev.min()), "max_eig": float(ev.max()),
            "finite_diag": bool(np.isfinite(np.diag(C)).all()),
            "psd_within_tol": bool(ev.min() >= -1e-12 * max(abs(ev.max()), 1e-300))}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    D = "products/pet/bkgsub"
    ap.add_argument("--csyst", default=f"{D}/pet_csyst_prelim_bkgsub_5d.npz")
    ap.add_argument("--cstat", default=f"{D}/pet_cstat_bkgsub_5d.npz")
    ap.add_argument("--cml", default=f"{D}/pet_cml_bkgsub_5d.npz")
    ap.add_argument("--clateral", default=None, help="optional; omitted -> preliminary")
    ap.add_argument("--w-source", default="of_inputs_5d.npz")
    ap.add_argument("--out", default=f"{D}/pet_ctotal_bkgsub_5d.npz")
    ap.add_argument("--label", default="preliminary",
                    help="'preliminary' (no lateral / prelim C_syst) or 'final'")
    a = ap.parse_args()

    comps = {"C_syst": (a.csyst, "C_syst"), "C_stat": (a.cstat, "C_stat"),
             "C_ml": (a.cml, "C_ml")}
    if a.clateral:
        comps["C_lateral"] = (a.clateral, "C_lateral")

    loaded, masks, cvs, Cs = {}, {}, {}, {}
    for name, (path, key) in comps.items():
        if not os.path.exists(path):
            raise SystemExit(f"[FAIL] {name} product missing: {path}")
        z = np.load(path)
        Ck = key if key in z.files else ([k for k in z.files if k.startswith("C_")][0])
        Cs[name] = np.asarray(z[Ck], float)
        masks[name] = np.asarray(z["reported_mask"], bool)
        cvs[name] = np.asarray(z["cv"], float)
        loaded[name] = path

    # common mask/order + common central check
    ref_mask = masks["C_syst"]
    for name, m in masks.items():
        if not np.array_equal(m, ref_mask):
            raise SystemExit(f"[FAIL] {name} reported_mask differs from C_syst (common-mask violation)")
    ref_cv = cvs["C_syst"]
    for name, c in cvs.items():
        if not np.allclose(c, ref_cv, rtol=0, atol=0):
            # cv should be the identical corrected-nominal xsec_flat in every product
            if not np.array_equal(c, ref_cv):
                print(f"[warn] {name} cv not bit-identical to C_syst cv (max|d|={np.abs(c-ref_cv).max():.3e})")
    nrep = int(ref_mask.sum())
    for name, C in Cs.items():
        if C.shape != (nrep, nrep):
            raise SystemExit(f"[FAIL] {name} shape {C.shape} != ({nrep},{nrep})")

    C_total = sum(Cs.values())
    base = ref_cv[ref_mask]
    per = {}
    for name, C in list(Cs.items()) + [("C_total", C_total)]:
        sig = np.sqrt(np.clip(np.diag(C), 0, None))
        per[name] = {"sqrt_trace": float(np.sqrt(max(C.trace(), 0.0))),
                     "per_bin_rel_median": float(np.median(sig / base))}

    diag_total = psd_diagnostics(C_total)

    # ---- 5D -> 4D density marginal ----
    w_edges = np.asarray(np.load(a.w_source)["edges_4"], float)
    M, rep5_idx, rep4_idx, shape4 = build_5d_to_4d_projection(ref_mask, SHAPE5, w_edges)
    cv5 = base                                   # reported 5D density
    cv4 = M @ cv5
    C4 = M @ C_total @ M.T
    diag_4d = psd_diagnostics(C4)
    sig4 = np.sqrt(np.clip(np.diag(C4), 0, None))
    rel4 = sig4 / np.where(cv4 > 0, cv4, np.inf)

    np.savez_compressed(a.out, C_total_5d=C_total, cv_5d_reported=cv5,
                        reported_mask_5d=ref_mask, C_4d=C4, cv_4d=cv4,
                        M_5d_to_4d=M, rep4_flat_idx=rep4_idx, shape5=np.array(SHAPE5),
                        shape4=np.array(shape4))
    summary = {
        "campaign": f"PET bkgsub 5D corrected C_total assembly ({a.label})",
        "label": a.label,
        "components_present": sorted(Cs.keys()),
        "components_missing": ([] if a.clateral else ["C_lateral (GBDT rebank blocked)"]),
        "note": ("PRELIMINARY: C_syst is the support-limited pre-fix-bank vertical "
                 "block and C_lateral is omitted (GBDT rebank in flight). Not final; "
                 "not for ledger/note." if a.label != "final" else "final"),
        "n_reported_bins_5d": nrep, "n_reported_bins_4d": int(len(rep4_idx)),
        "per_component": per,
        "psd_5d_total": diag_total, "psd_4d": diag_4d,
        "total_sigma_5d_check": None,
        "cv_4d_finite": bool(np.isfinite(cv4).all()),
        "cv_4d_nonneg": bool((cv4 >= 0).all()),
        "per_bin_rel_median_4d": float(np.median(rel4[np.isfinite(rel4)])),
        "sources": loaded, "out": os.path.abspath(a.out),
    }
    spath = os.path.splitext(a.out)[0] + ".summary.json"
    json.dump(summary, open(spath, "w"), indent=2)

    print(f"[assemble] ({a.label}) components={sorted(Cs.keys())} "
          f"missing={summary['components_missing']}")
    for name in list(Cs.keys()) + ["C_total"]:
        print(f"    {name:10s} sqrt-tr={per[name]['sqrt_trace']:.3e} "
              f"per-bin rel median={100*per[name]['per_bin_rel_median']:.2f}%")
    print(f"[assemble] 5D C_total PSD: min_eig={diag_total['min_eig']:.3e} "
          f"sym={diag_total['symmetry_max_abs_asym']:.3e} psd={diag_total['psd_within_tol']}")
    print(f"[assemble] 4D marginal: {len(rep4_idx)} bins, cv4 finite={summary['cv_4d_finite']} "
          f"nonneg={summary['cv_4d_nonneg']}, per-bin rel median={100*summary['per_bin_rel_median_4d']:.2f}%, "
          f"PSD min_eig={diag_4d['min_eig']:.3e} psd={diag_4d['psd_within_tol']}")
    print(f"[assemble] wrote {a.out} + {spath}")


if __name__ == "__main__":
    main()
