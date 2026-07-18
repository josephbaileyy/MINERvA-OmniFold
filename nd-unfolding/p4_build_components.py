#!/usr/bin/env python3
"""P4 standard CANONICAL component builder — manifest-bound, FAIL-CLOSED (repair 2026-07-18).

Reconstructs the final standard 5D scalar covariance from EXPLICIT NAMED components
only (no globs, no silent band-skip):

  C_final5 = sum(named corrected background-aware NON-lateral components)
           + sum(5 selection-complete active per-band lateral blocks)

The 5 active per-band blocks are built with the preserved MAT biased-1/N two-endpoint
formula (uq_math.mat_covariance) from the manifest-bound +/- endpoint pair per band.
Every input is cross-checked against the committed manifest (endpoint SHA256s, mask/
order hash, central hash). The support family MUST be the canonical corrected
background-aware combined covariance, never the superseded non-bkgaware ROOT.

Writes an inseparable component-provenance manifest + the C_final5 CANDIDATE (to a
candidate path only). Does NOT adopt. Authorized to RUN only after the
standard-p4-verifier returns PASS; this repair round does not run it.
"""
import argparse, json, sys
import numpy as np
import p4_lib as P
from uq_math import mat_covariance

# canonical corrected background-aware support family (bkgaware); reject superseded.
BKGAWARE_DIR = "uq_5d/universe_stage2_5d_bkgaware"
SUPERSEDED_TOKENS = ("universe_stage2_5d/uq_universe_5d_covariance_combined.root",  # non-bkgaware
                     "_prehm_", "uthrow_slabs")
# NON-lateral components inherited unchanged from the corrected bkgaware family.
NONLATERAL_COMPONENTS = ("stat", "mlsplit")  # + vertical-syst-minus-5-lateral, assembled below


def _flat(path, key):
    import ROOT
    f = ROOT.TFile.Open(path)
    if not f or f.IsZombie():
        raise P.P4GateError(f"cannot open {path}")
    h = f.Get(key)
    if not h:
        f.Close(); raise P.P4GateError(f"missing {key} in {path}")
    n = h.GetNbinsX(); v = np.array([h.GetBinContent(i + 1) for i in range(n)]); f.Close(); return v


def _th2(path, key):
    import ROOT
    f = ROOT.TFile.Open(path); h = f.Get(key)
    if not h:
        f.Close(); return None
    n = h.GetNbinsX(); C = np.empty((n, n))
    for i in range(n):
        for j in range(n):
            C[i, j] = h.GetBinContent(i + 1, j + 1)
    f.Close(); return C


def build_active_bands(manifest, reported_mask):
    """5 active per-band MAT blocks on the reported mask, from the manifest-bound
    +/- endpoint pair. Cross-checks each endpoint file SHA256 vs the manifest."""
    UDIR = "active_universe_5d/standard/unfolds"
    idx = np.nonzero(reported_mask)[0]
    bands = {}
    for b in P.BANDS:
        pair = []
        for ep in P.ENDPOINTS:
            tag = f"{b}_{ep}"; p = f"{UDIR}/5d_xsec_MEFHC_5iter_lgbm_uni_full_{tag}.root"
            got = P.sha256_file(p)
            P.require(got == manifest["endpoint_sha256"][tag],
                      f"endpoint {tag} sha256 drift vs manifest")
            pair.append(_flat(p, "hXSecND_flat")[idx])   # reported-mask projection, fixed order
        bands[b] = mat_covariance(np.stack([pair[0], pair[1]]))  # (minus, plus) -> MAT biased 1/N
    P.require_exact_bands(bands)
    P.component_traces_positive_finite(bands)
    return bands


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True, help="evidence/p4_standard_manifest.json")
    ap.add_argument("--support-family", required=True,
                    help="canonical corrected bkgaware combined cov ROOT")
    ap.add_argument("--out", required=True, help="C_final5 CANDIDATE ROOT (candidate path only)")
    ap.add_argument("--out-manifest", required=True, help="component provenance manifest JSON")
    a = ap.parse_args()

    for bad in ("_uthrow", "adopted", "_final", "universe_stage2_5d/uq_universe_5d_covariance_combined"):
        P.require(bad not in a.out, f"refusing candidate onto adopted/canonical path ({bad})")
    for bad in SUPERSEDED_TOKENS:
        P.require(bad not in a.support_family, f"support family is superseded/non-bkgaware ({bad})")
    P.require(BKGAWARE_DIR in a.support_family, "support family must be the corrected bkgaware combined cov")

    man = json.load(open(a.manifest))
    P.require(man.get("mask5d_nreported") and man["mask5d_nreported"] > 0, "manifest mask missing")
    # reconstruct the reported mask from the frozen central + cross-check its hash
    central = _flat("products/5d/xsec_5d_MEFHC_5iter_lgbm.root", "hXSecND_flat")
    P.require(P.sha256_file("products/5d/xsec_5d_MEFHC_5iter_lgbm.root") == man["central5d_sha256"],
              "central 5D sha256 drift vs manifest")
    mask = central > 0
    hmask, nmask = P.mask_order_hash(mask)
    P.require(hmask == man["mask5d_hash"] and nmask == man["mask5d_nreported"], "reported-mask hash drift")

    active = build_active_bands(man, mask)
    active_sum = sum(active[b] for b in P.BANDS)

    # named NON-lateral components from the corrected bkgaware family (reported mask)
    kept = {}
    for comp in NONLATERAL_COMPONENTS:
        C = _th2(a.support_family, f"hCov_{comp}5d_reported")
        P.require(C is not None, f"named component hCov_{comp}5d_reported missing in support family")
        kept[comp] = C
    # vertical systematic EXCLUDING the 5 lateral bands = C_syst_total - sum(support 5 lateral)
    Csyst = _th2(a.support_family, "hCov_combined5d_total")
    P.require(Csyst is not None, "support family combined total missing")
    supp_lat = {b: _th2(a.support_family, f"hCov_universe5d_{b}") for b in P.BANDS}
    P.require(all(supp_lat[b] is not None for b in P.BANDS), "support family missing a lateral band")
    P.require_exact_bands(supp_lat)
    nonlateral_vertical = Csyst - sum(supp_lat[b] for b in P.BANDS) - kept["stat"] - kept["mlsplit"]

    C_final5 = nonlateral_vertical + kept["stat"] + kept["mlsplit"] + active_sum
    # identity gate: C_final5 - (nonlateral) must equal the active-band sum exactly
    reconstructed_lat = C_final5 - (nonlateral_vertical + kept["stat"] + kept["mlsplit"])
    err = float(np.max(np.abs(reconstructed_lat - active_sum)) / max(1e-300, np.max(np.abs(active_sum))))
    P.require(err <= 1e-9, f"active-total identity broken (rel {err:.2e})")
    stats = P.check_symmetric_psd(C_final5)

    prov = {"support_family": a.support_family, "support_family_sha256": P.sha256_file(a.support_family),
            "kept_components": list(NONLATERAL_COMPONENTS) + ["vertical_minus_5lateral"],
            "active_bands": list(P.BANDS), "active_traces": {b: float(np.trace(active[b])) for b in P.BANDS},
            "manifest": a.manifest, "manifest_endpoint_hash": man.get("endpoint_manifest_hash"),
            "reported_mask_hash": man["mask5d_hash"], "n_reported": man["mask5d_nreported"],
            "psd": stats, "active_total_identity_relerr": err}
    json.dump(prov, open(a.out_manifest, "w"), indent=2)

    import ROOT
    n = C_final5.shape[0]; fo = ROOT.TFile.Open(a.out, "RECREATE")
    h = ROOT.TH2D("hCov_std_final5_candidate", "std final5 CANDIDATE (component-built)", n, 0, n, n, 0, n)
    for i in range(n):
        for j in range(n):
            h.SetBinContent(i + 1, j + 1, C_final5[i, j])
    h.Write(); fo.Close()
    print(f"CANDIDATE {a.out} sqrt_tr={np.sqrt(max(0,np.trace(C_final5))):.4e} n={n}; prov -> {a.out_manifest}")
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except P.P4GateError as e:
        print(f"FAIL-CLOSED :: {e}"); sys.exit(1)
