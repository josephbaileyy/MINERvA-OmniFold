#!/usr/bin/env python3
"""P6-FPS FINAL lateral adoption (Agent C): swap the support-limited FPS lateral block for the
selection-complete active scalar lateral block in the combined FPS covariance, by PURE COMPONENT
SUM (never subtraction -- the D5 lesson: subtracting a DIFFERENT-estimator block breaks PSD; here
we simply rebuild the combined by summing PSD pieces).

    C_comb_active = SUM_{band in universe4d blocks EXCEPT total and the 5 lateral} C_band   (incl.
                    __Normalization_flat, MinosEfficiency, and every vertical/model/hadronic band)
                  + C_stat (external uq_cov_stat_fps.root:hCov_statfps_reported)
                  + C_ML   (external uq_cov_mlsplit_fps.root:hCov_mlsplitfps_reported)
                  + C_active_lateral (active_scalar_lateral_fps_cov.root:hCov_universe4d_total)

Writes an intermediate combined ROOT that (a) carries the rebuilt hCov_combined4d_total, (b) copies
EVERY original per-band hCov_universe4d_<band> block through unchanged (so the downstream
adopt_unified_4d.py can still read the 13 vertical per-band carriers), and (c) records the active
lateral total under hCov_universe4d_active_lateral_total. A subtraction-based cross-check
(C_comb_orig - SUM(5 support lateral) + C_active) is reported for consistency but is NOT the product.

Then run the HARDENED unified-throw adopt (adopt_unified_fps.py) on THIS file for the publishable cov:
  python adopt_unified_fps.py --uthrow uq_fps/corrected/unified_throw_cov_fps.root \
      --combined <this --out> --prod uq_fps/universe_sweep/fps2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root \
      --out uq_fps/corrected/universe_stage2_fps/uq_universe_fps_covariance_combined_uthrow_activelat.root

  python adopt_active_lateral_fps.py    # defaults below
"""
import argparse
import json
import os

import numpy as np
import ROOT

import fps_provenance as fp

ROOT.gROOT.SetBatch(True)
LATERAL = ["BeamAngleX", "BeamAngleY", "MuonResolution",
           "Muon_Energy_MINERvA", "Muon_Energy_MINOS"]
PURE_SUM_SUB_TOL = 1e-9   # pure-sum must equal same-source subtraction to float precision


def _th2(h):
    n = h.GetNbinsX()
    C = np.empty((n, n))
    for i in range(n):
        for j in range(n):
            C[i, j] = h.GetBinContent(i + 1, j + 1)
    return C


def _load_key(path, key, required=True):
    f = ROOT.TFile.Open(path)
    if not f or f.IsZombie():
        raise SystemExit(f"[FAIL] cannot open {path}")
    h = f.Get(key)
    if not h:
        f.Close()
        if required:
            raise SystemExit(f"[FAIL] missing {key} in {path}")
        return None
    C = _th2(h)
    f.Close()
    return C


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--combined",
                    default="uq_fps/corrected/universe_stage2_fps/uq_universe_fps_covariance_combined.root")
    ap.add_argument("--active",
                    default="active_universe_5d/fps/covariance/active_scalar_lateral_fps_cov.root:hCov_universe4d_total")
    ap.add_argument("--stat", default="uq_fps/corrected/uq_cov_stat_fps.root:hCov_statfps_reported")
    ap.add_argument("--ml", default="uq_fps/corrected/uq_cov_mlsplit_fps.root:hCov_mlsplitfps_reported")
    ap.add_argument("--manifest", required=True, help="hash-bound PUBLICATION manifest")
    ap.add_argument("--pass-receipt", required=True, help="hash-bound PASS receipt for --manifest")
    ap.add_argument("--out",
                    default="uq_fps/corrected/universe_stage2_fps/uq_universe_fps_covariance_combined_activelat.root")
    a = ap.parse_args()

    # blocker 2: hash-bound publication manifest + PASS receipt mandatory at this transition
    manifest = json.load(open(a.manifest))
    fp.require_publication_manifest(manifest)
    fp.require_pass_receipt(json.load(open(a.pass_receipt)), fp.sha256_file(a.manifest))

    # blocker 4: reject output aliasing any input (no in-place clobber of a source)
    fp.require_no_path_alias(a.out, a.combined, a.active.rsplit(":", 1)[0],
                             a.stat.rsplit(":", 1)[0], a.ml.rsplit(":", 1)[0])

    # active lateral (selection-complete)
    ap_path, ap_key = a.active.rsplit(":", 1)
    C_active = _load_key(ap_path, ap_key)
    n = C_active.shape[0]

    # enumerate every per-band block in the combined ROOT; sum the non-lateral ones
    fc = ROOT.TFile.Open(a.combined)
    if not fc or fc.IsZombie():
        raise SystemExit(f"[FAIL] cannot open {a.combined}")
    band_blocks = {}          # band -> matrix (copied through unchanged)
    C_nonlat = np.zeros((n, n))
    lateral_seen, C_support_lat = [], np.zeros((n, n))
    for k in fc.GetListOfKeys():
        name = k.GetName()
        if not name.startswith("hCov_universe4d_"):
            continue
        band = name[len("hCov_universe4d_"):]
        if band == "total":
            continue
        mat = _th2(fc.Get(name))
        if mat.shape != (n, n):
            raise SystemExit(f"[FAIL] {name} shape {mat.shape} != active {(n, n)}")
        band_blocks[band] = mat
        if band in LATERAL:
            lateral_seen.append(band)
            C_support_lat = C_support_lat + mat
        else:
            C_nonlat = C_nonlat + mat        # includes __Normalization_flat, MinosEfficiency, verticals
    C_comb_orig = _th2(fc.Get("hCov_combined4d_total"))
    fc.Close()

    if sorted(lateral_seen) != sorted(LATERAL):
        raise SystemExit(f"[FAIL] support lateral bands found {sorted(lateral_seen)} != {sorted(LATERAL)}")

    st_path, st_key = a.stat.rsplit(":", 1)
    ml_path, ml_key = a.ml.rsplit(":", 1)
    C_stat = _load_key(st_path, st_key)
    C_ml = _load_key(ml_path, ml_key)
    for tag, C in (("stat", C_stat), ("ml", C_ml), ("combined_orig", C_comb_orig)):
        if C.shape != (n, n):
            raise SystemExit(f"[FAIL] {tag} shape {C.shape} != {(n, n)}")

    # PURE-SUM product
    C_comb_active = C_nonlat + C_stat + C_ml + C_active
    C_comb_active = 0.5 * (C_comb_active + C_comb_active.T)

    # subtraction cross-check (NOT the product): should match to float precision iff the stored
    # combined == SUM(all bands)+norm+stat+ML with the same external stat/ML the budget used.
    C_check = C_comb_orig - C_support_lat + C_active
    max_abs_diff = float(np.max(np.abs(C_comb_active - C_check)))
    rel_diff = max_abs_diff / max(1e-300, float(np.max(np.abs(C_comb_active))))
    # blocker 4: HARD gate -- the PSD-safe pure sum must equal the same-source subtraction to float
    # precision, else the stored combined is not a clean SUM(bands)+stat+ML and the swap is unsafe.
    fp.require_pure_sum_matches_sub(C_comb_active, C_check, tol=PURE_SUM_SUB_TOL)

    ev = np.linalg.eigvalsh(C_comb_active)
    do = np.sqrt(np.clip(np.diag(C_comb_orig), 0, None))
    dn = np.sqrt(np.clip(np.diag(C_comb_active), 0, None))
    sa = np.sqrt(np.clip(np.diag(C_active), 0, None))
    ss = np.sqrt(np.clip(np.diag(C_support_lat), 0, None))
    print(f"[swap] reported bins            = {n}")
    print(f"[swap] non-lateral bands summed = {len(band_blocks) - len(lateral_seen)}  "
          f"(+ stat + ML + active lateral)")
    print(f"[swap] lateral sqrt-tr: support = {np.sqrt(np.trace(C_support_lat)):.4e}  "
          f"active = {np.sqrt(np.trace(C_active)):.4e}  "
          f"(x{np.sqrt(np.trace(C_active)/max(1e-300,np.trace(C_support_lat))):.3f})")
    print(f"[swap] combined sqrt-tr: old    = {np.sqrt(np.trace(C_comb_orig)):.4e}  "
          f"new = {np.sqrt(np.trace(C_comb_active)):.4e}  "
          f"(x{np.sqrt(np.trace(C_comb_active)/max(1e-300,np.trace(C_comb_orig))):.3f})")
    print(f"[swap] sum-vs-subtraction cross-check: max|diff|={max_abs_diff:.3e} rel={rel_diff:.2e}")
    print(f"[swap] PSD check: min eig = {ev[0]:.3e}  neg={(ev<0).sum()}  "
          f"most-neg/max = {ev[0]/max(1e-300,ev[-1]):.2e}")
    if ev[0] < -1e-12 * abs(ev[-1]):
        raise SystemExit("[FAIL] active-lateral combined is not PSD")
    print("[swap] PSD OK (pure sum of PSD pieces)")

    fo = ROOT.TFile.Open(a.out, "RECREATE")

    def wcov(name, mat, title=None):
        h = ROOT.TH2D(name, title or name, n, 0, n, n, 0, n)
        for i in range(n):
            for j in range(n):
                h.SetBinContent(i + 1, j + 1, float(mat[i, j]))
        h.Write()

    wcov("hCov_combined4d_total", C_comb_active,
         "combined FPS cov (selection-complete active lateral, pre-uthrow)")
    # non-lateral bands (incl norm/MinosEfficiency/verticals) keep their name (adopt reads verticals);
    # the 5 SUPERSEDED support laterals are renamed so nothing can re-sum them into a total.
    for band, mat in band_blocks.items():
        if band in LATERAL:
            wcov(f"hCov_universe4d_{band}__SUPERSEDED_support", mat,
                 f"SUPERSEDED support-limited {band} lateral (replaced by active; NOT in any total)")
        else:
            wcov(f"hCov_universe4d_{band}", mat)
    wcov("hCov_universe4d_active_lateral_total", C_active,
         "selection-complete active scalar lateral (sum of 5 bands)")
    # blocker 4: full reproducibility provenance
    ap_path = a.active.rsplit(":", 1)[0]
    prov = {
        "product": "hCov_combined4d_total = SUM(non-lateral universe4d bands incl norm) "
                   "+ stat + ML + active_lateral (PURE SUM, no subtraction)",
        "superseded": "5 support-limited lateral bands renamed *__SUPERSEDED_support (not summed)",
        "next": "run adopt_unified_fps.py on this file for the publishable uthrow covariance",
        "centering": "MAT biased 1/N, mean-centered (active lateral); combined per D5 precedent",
        "reported_dim": int(n),
        "layout_fingerprint": fp.layout_fingerprint(),
        "sum_vs_sub_max_abs_diff": max_abs_diff, "sum_vs_sub_rel": rel_diff,
        "sum_vs_sub_tol": PURE_SUM_SUB_TOL,
        "args": {"combined": a.combined, "active": a.active, "stat": a.stat, "ml": a.ml, "out": a.out},
        "source_sha256": {
            "combined": fp.sha256_file(a.combined),
            "active": fp.sha256_file(ap_path),
            "stat": fp.sha256_file(a.stat.rsplit(":", 1)[0]),
            "ml": fp.sha256_file(a.ml.rsplit(":", 1)[0]),
        },
        "code_sha256": {
            "adopt_active_lateral_fps.py": fp.sha256_file(os.path.abspath(__file__)),
            "fps_provenance.py": fp.sha256_file(
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "fps_provenance.py")),
        },
    }
    ROOT.TNamed("provenance", json.dumps(prov)).Write()
    ROOT.TParameter("double")("sqrt_tr_combined_active",
                              float(np.sqrt(np.trace(C_comb_active)))).Write()
    ROOT.TParameter("double")("sum_vs_sub_max_abs_diff", max_abs_diff).Write()
    fo.Close()
    print(f"[swap] wrote {a.out}")
    print(f"[swap] pure-sum vs subtraction rel={rel_diff:.2e} (<= {PURE_SUM_SUB_TOL:.0e} gate PASSED)")


if __name__ == "__main__":
    main()
