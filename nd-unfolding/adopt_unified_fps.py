#!/usr/bin/env python3
"""Blocker 5 (Agent C): hardened FPS unified-throw final adoption. FPS wrapper around the
adopt_unified_4d.py math (C_final = C_pre - C_vertical + (g g^T) o C_vertical) with fail-closed
gates so the publishable covariance is reproducible and cannot be built from mismatched inputs.

Gates (fps_provenance):
  - reported dim/order equality across combined (C_pre), unified-throw, and CV-defined mask;
  - reject diag(C_blocksum)<=0 < diag(C_unified) (ill-defined inflation / mask-estimator mismatch);
  - reject output aliasing any input;
  - require the written C_final to satisfy the reconstruction identity to float precision;
  - PSD at the declared tolerance.
Preserves hJointMeanShift SEPARATELY, labels the mean-centered policy, and writes C_vertical + g +
source hashes so C_final is reproducible from the final ROOT plus this inseparable provenance.

NOT RUN in the 2026-07-18 repair round (no active-lateral combined exists yet; gated on the
verifier-approved negweight-refined chain).

  python adopt_unified_fps.py \
      --combined uq_fps/corrected/universe_stage2_fps/uq_universe_fps_covariance_combined_activelat.root \
      --uthrow  uq_fps/corrected/unified_throw_cov_fps.root \
      --prod    uq_fps/universe_sweep/fps2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root \
      --out     uq_fps/corrected/universe_stage2_fps/uq_universe_fps_covariance_combined_uthrow_activelat.root
"""
import argparse
import json

import numpy as np
import ROOT

import fps_provenance as fp

ROOT.gROOT.SetBatch(True)
# the 13 vertical bands the unified throw covers (12 knobs + Flux); the lateral bands are orthogonal
# (added components) and pass through the adoption untouched.
VERT_BANDS = ["2p2h", "CCQEPauliSupViaKF", "FrAbs_pi", "FrElas_N", "HighQ2", "LowQ2",
              "MaCCQE", "MaRES", "MFP_N", "MvRES", "Rvn2pi", "Rvp2pi", "Flux"]
PSD_TOL = -1e-12


def _th2(h):
    n = h.GetNbinsX()
    C = np.empty((n, n))
    for i in range(n):
        for j in range(n):
            C[i, j] = h.GetBinContent(i + 1, j + 1)
    return C


def _get(f, key, required=True):
    h = f.Get(key)
    if not h and required:
        raise fp.FpsGateError(f"missing {key}")
    return h


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--combined", required=True, help="active-lateral pre-uthrow combined ROOT")
    ap.add_argument("--uthrow", required=True, help="unified_throw_cov_fps.root")
    ap.add_argument("--prod", required=True, help="CV unfold (defines reported mask/central)")
    ap.add_argument("--manifest", required=True, help="hash-bound PUBLICATION manifest")
    ap.add_argument("--pass-receipt", required=True, help="hash-bound PASS receipt for --manifest")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    # blocker 2: hash-bound publication manifest + PASS receipt mandatory at this transition
    manifest = json.load(open(a.manifest))
    fp.require_publication_manifest(manifest)
    fp.require_pass_receipt(json.load(open(a.pass_receipt)), fp.sha256_file(a.manifest))
    fp.require_no_path_alias(a.out, a.combined, a.uthrow, a.prod)

    fu = ROOT.TFile.Open(a.uthrow)
    C_uni = _th2(_get(fu, "C_unified"))
    C_block = _th2(_get(fu, "C_blocksum"))
    # blocker 5: hJointMeanShift is MANDATORY (not optional); validate present/finite/dim
    hms = _get(fu, "hJointMeanShift", required=True)
    mean_shift = np.array([hms.GetBinContent(i + 1) for i in range(hms.GetNbinsX())])
    fu.Close()
    fp.require_mean_shift(mean_shift)

    fc = ROOT.TFile.Open(a.combined)
    C_comb = _th2(_get(fc, "hCov_combined4d_total"))          # C_pre (active-lateral combined)
    C_vert = None
    for b in VERT_BANDS:
        C_vert = _th2(_get(fc, f"hCov_universe4d_{b}")) if C_vert is None \
            else C_vert + _th2(_get(fc, f"hCov_universe4d_{b}"))
    fc.Close()

    fpr = ROOT.TFile.Open(a.prod)
    hx = _get(fpr, "hXSecND_flat")
    xfull = np.array([hx.GetBinContent(i + 1) for i in range(hx.GetNbinsX())])
    fpr.Close()
    rep = xfull > 0
    n = int(rep.sum())

    # ---- dim/order equality across all inputs (blocker 5)
    for tag, C in (("C_unified", C_uni), ("C_blocksum", C_block),
                   ("combined", C_comb), ("C_vertical", C_vert)):
        fp.require_square_finite(C, expected_dim=n, tag=tag)

    vu = np.clip(np.diag(C_uni), 0, None)
    vb = np.clip(np.diag(C_block), 0, None)
    # ---- reject zero-block / nonzero-unified (blocker 5)
    fp.require_unified_inputs(vb, vu, tag="unified-vs-block")

    s_adopt = np.sqrt(np.maximum(vu, vb))
    sb = np.sqrt(vb)
    g = np.ones(n)
    m = sb > 0
    g[m] = s_adopt[m] / sb[m]                                  # >= 1
    G = np.outer(g, g)
    C_new = (C_comb - C_vert) + G * C_vert
    C_new = 0.5 * (C_new + C_new.T)

    # ---- identity + PSD gates (blocker 5)
    fp.require_final_identity(C_new, C_comb, C_vert, g, tag="FPS uthrow adoption")
    fp.require_psd(C_new, tol=PSD_TOL, tag="C_final")

    fo = ROOT.TFile.Open(a.out, "RECREATE")

    def wcov(name, mat, title=None):
        h = ROOT.TH2D(name, title or name, n, 0, n, n, 0, n)
        for i in range(n):
            for j in range(n):
                h.SetBinContent(i + 1, j + 1, float(mat[i, j]))
        h.Write()

    wcov("hCov_combined4d_total_uthrow", C_new,
         "PUBLISHABLE FPS cov (active lateral + stat + ML + unified-throw vertical inflation)")
    wcov("hCov_vertical_sweep", C_vert, "C_vertical (sum of 13 vertical per-band covs; adoption carrier)")
    hg = ROOT.TH1D("hInflation_g", "per-bin unified/block sigma inflation g>=1", n, 0, n)
    for i in range(n):
        hg.SetBinContent(i + 1, float(g[i]))
    hg.Write()
    # preserve hJointMeanShift SEPARATELY (mandatory; mean-centered policy -> NOT folded into C_final)
    hjm = ROOT.TH1D("hJointMeanShift", "joint mean shift (preserved; NOT added: mean-centered policy)",
                    mean_shift.size, 0, mean_shift.size)
    for i in range(mean_shift.size):
        hjm.SetBinContent(i + 1, float(mean_shift[i]))
    hjm.Write()
    prov = {
        "identity": "C_final = C_pre - C_vertical + (g g^T) o C_vertical",
        "C_pre": "hCov_combined4d_total from --combined (active-lateral)",
        "C_vertical": "hCov_vertical_sweep (written here) = sum of 13 vertical per-band covs",
        "g": "hInflation_g (written here)",
        "centering": "mean-centered (diag C_unified only); hJointMeanShift preserved separately, NOT added",
        "reported_dim": n, "layout_fingerprint": fp.layout_fingerprint(),
        "source_sha256": {"combined": fp.sha256_file(a.combined),
                          "uthrow": fp.sha256_file(a.uthrow),
                          "prod": fp.sha256_file(a.prod)},
        "reproducible_from_final_root": True,
    }
    ROOT.TNamed("provenance", json.dumps(prov)).Write()
    fo.Close()
    fpr_ = fp.cov_fingerprint(C_new)
    print(f"[uthrow-fps] wrote {a.out}")
    print(f"[uthrow-fps] dim={fpr_['dim']} rank={fpr_['rank']} sqrt_tr={fpr_['sqrt_trace']:.4e} "
          f"min/max_eig={fpr_['min_over_max_eig']:.2e}  g: median={np.median(g):.3f} max={g.max():.2f}")


if __name__ == "__main__":
    main()
