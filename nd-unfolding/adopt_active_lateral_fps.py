#!/usr/bin/env python3
"""P6-FPS active-lateral adoption (Agent C), hardened repair-3. Swap the support-limited FPS lateral
block for the selection-complete active block by PURE COMPONENT SUM (never subtraction), gated by the
publication manifest + receipt chain. Manifest/receipt/hash gates run BEFORE ROOT (login-safe); ROOT lazy.

Fail-closed (unconditional):
  - publication manifest + manifest PASS receipt (binds this manifest digest);
  - p4_validation transition receipt (predecessor = active cov sha; candidate = active cov sha);
  - RECOMPUTE the active cov sha == the p4 receipt candidate (no substituted covariance);
  - RECOMPUTE every manifest artifact hash; reject output aliasing any input.
Product: C_comb_active = SUM(non-lateral universe4d bands incl norm) + stat + ML + active_lateral
(all PSD pieces). HARD gate: pure sum == same-source subtraction to float precision. Superseded support
lateral blocks renamed *__SUPERSEDED_support (never re-summed). Emits an active_adoption receipt LAST
(predecessor = active cov sha; candidate = the activelat combined sha).

  python adopt_active_lateral_fps.py --manifest M --pass-receipt R --p4-receipt P4 \
      --combined COMBINED.root --active active_scalar_lateral_fps_cov.root:hCov_universe4d_total \
      --stat S.root:hCov_statfps_reported --ml ML.root:hCov_mlsplitfps_reported \
      --out OUT.root --out-receipt receipt_active_adoption.json --utc <iso>
"""
import argparse, datetime, json, os
import numpy as np

import fps_provenance as fp

LATERAL = fp.BANDS
PURE_SUM_SUB_TOL = 1e-9


def _load_root():
    import ROOT
    ROOT.gROOT.SetBatch(True)
    return ROOT


def _th2(h):
    n = h.GetNbinsX()
    return np.array([[h.GetBinContent(i + 1, j + 1) for j in range(n)] for i in range(n)])


def _load_key(ROOT, path, key, required=True):
    f = ROOT.TFile.Open(path)
    if not f or f.IsZombie():
        raise SystemExit(f"[FAIL] cannot open {path}")
    h = f.Get(key)
    if not h:
        f.Close()
        if required:
            raise SystemExit(f"[FAIL] missing {key} in {path}")
        return None
    C = _th2(h); f.Close(); return C


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--pass-receipt", required=True)
    ap.add_argument("--p4-receipt", required=True)
    ap.add_argument("--combined", default="uq_fps/corrected/universe_stage2_fps/uq_universe_fps_covariance_combined.root")
    ap.add_argument("--active", default="active_universe_5d/fps/covariance/active_scalar_lateral_fps_cov.root:hCov_universe4d_total")
    ap.add_argument("--stat", default="uq_fps/corrected/uq_cov_stat_fps.root:hCov_statfps_reported")
    ap.add_argument("--ml", default="uq_fps/corrected/uq_cov_mlsplit_fps.root:hCov_mlsplitfps_reported")
    ap.add_argument("--out", default="uq_fps/corrected/universe_stage2_fps/uq_universe_fps_covariance_combined_activelat.root")
    ap.add_argument("--out-receipt", default="active_universe_5d/fps/covariance/receipt_active_adoption.json")
    ap.add_argument("--utc", default=None)
    a = ap.parse_args()
    utc = a.utc or datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    ap_path = a.active.rsplit(":", 1)[0]

    # ---- login-safe gates (no ROOT) ----
    manifest = json.load(open(a.manifest))
    fp.require_publication_manifest(manifest)
    manifest_digest = fp.sha256_file(a.manifest)
    fp.require_pass_receipt(json.load(open(a.pass_receipt)), manifest_digest)
    fp.require_recompute_hashes(manifest)
    active_sha = fp.sha256_file(ap_path)
    p4 = json.load(open(a.p4_receipt))
    fp.require_transition_receipt(p4, "p4_validation", manifest_digest, predecessor_sha=active_sha)
    if p4.get("candidate_sha256") != active_sha:
        raise fp.FpsGateError("active cov sha != p4 receipt candidate (substituted covariance)")
    fp.require_no_path_alias(a.out, a.combined, ap_path,
                             a.stat.rsplit(":", 1)[0], a.ml.rsplit(":", 1)[0])

    # ---- ROOT numeric section (lazy) ----
    ROOT = _load_root()
    C_active = _load_key(ROOT, ap_path, a.active.rsplit(":", 1)[1]); n = C_active.shape[0]
    if n != fp.N_REPORTED:
        raise fp.FpsGateError(f"active dim {n} != {fp.N_REPORTED}")
    fc = ROOT.TFile.Open(a.combined)
    if not fc or fc.IsZombie():
        raise SystemExit(f"[FAIL] cannot open {a.combined}")
    band_blocks, C_nonlat = {}, np.zeros((n, n))
    lateral_seen, C_support_lat = [], np.zeros((n, n))
    for k in fc.GetListOfKeys():
        name = k.GetName()
        if not name.startswith("hCov_universe4d_") or name == "hCov_universe4d_total":
            continue
        band = name[len("hCov_universe4d_"):]
        mat = _th2(fc.Get(name))
        if mat.shape != (n, n):
            raise SystemExit(f"[FAIL] {name} shape {mat.shape} != {(n, n)}")
        band_blocks[band] = mat
        if band in LATERAL:
            lateral_seen.append(band); C_support_lat = C_support_lat + mat
        else:
            C_nonlat = C_nonlat + mat
    C_comb_orig = _th2(fc.Get("hCov_combined4d_total")); fc.Close()
    if sorted(lateral_seen) != sorted(LATERAL):
        raise SystemExit(f"[FAIL] support lateral bands {sorted(lateral_seen)} != {sorted(LATERAL)}")

    C_stat = _load_key(ROOT, a.stat.rsplit(":", 1)[0], a.stat.rsplit(":", 1)[1])
    C_ml = _load_key(ROOT, a.ml.rsplit(":", 1)[0], a.ml.rsplit(":", 1)[1])
    C_comb_active = 0.5 * ((C_nonlat + C_stat + C_ml + C_active) + (C_nonlat + C_stat + C_ml + C_active).T)
    C_check = C_comb_orig - C_support_lat + C_active
    max_abs_diff, rel_diff = fp.pure_sum_vs_sub_residual(C_comb_active, C_check)
    fp.require_pure_sum_matches_sub(C_comb_active, C_check, tol=PURE_SUM_SUB_TOL)
    fp.require_psd(C_comb_active, tag="active-lateral combined")

    fo = ROOT.TFile.Open(a.out, "RECREATE")

    def wcov(name, mat, title=None):
        h = ROOT.TH2D(name, title or name, n, 0, n, n, 0, n)
        for i in range(n):
            for j in range(n):
                h.SetBinContent(i + 1, j + 1, float(mat[i, j]))
        h.Write()

    wcov("hCov_combined4d_total", C_comb_active, "combined FPS cov (active lateral, pre-uthrow)")
    for band, mat in band_blocks.items():
        if band in LATERAL:
            wcov(f"hCov_universe4d_{band}__SUPERSEDED_support", mat, f"SUPERSEDED support {band}")
        else:
            wcov(f"hCov_universe4d_{band}", mat)
    wcov("hCov_universe4d_active_lateral_total", C_active, "selection-complete active lateral")
    ROOT.TNamed("provenance", json.dumps({
        "product": "SUM(non-lateral bands incl norm) + stat + ML + active_lateral (pure sum)",
        "manifest_sha256": manifest_digest, "reported_mask_hash": manifest["reported_mask_hash"],
        "centering": "MAT biased 1/N, mean-centered", "sum_vs_sub_rel": rel_diff,
        "source_sha256": {"combined": fp.sha256_file(a.combined), "active": active_sha,
                          "stat": fp.sha256_file(a.stat.rsplit(':', 1)[0]),
                          "ml": fp.sha256_file(a.ml.rsplit(':', 1)[0])}})).Write()
    fo.Close()

    cand = fp.sha256_file(a.out)
    receipt = fp.make_transition_receipt(
        "active_adoption", manifest_digest, predecessor_sha=active_sha, candidate_sha=cand,
        central_sha=manifest["central_cv_sha256"], reported_mask_hash=manifest["reported_mask_hash"],
        utc=utc, extra={"candidate_path": os.path.abspath(a.out), "sum_vs_sub_rel": rel_diff})
    fp.require_transition_receipt(receipt, "active_adoption", manifest_digest, predecessor_sha=active_sha)
    with open(a.out_receipt, "w") as fh:
        json.dump(receipt, fh, indent=2)
    print(f"[swap] wrote {a.out} (cand {cand[:16]}); pure-sum vs sub rel={rel_diff:.2e} <= {PURE_SUM_SUB_TOL:.0e}")
    print(f"[swap] active_adoption receipt {a.out_receipt}")


if __name__ == "__main__":
    main()
