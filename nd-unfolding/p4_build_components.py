#!/usr/bin/env python3
"""P4 standard CANONICAL component builder — manifest-bound, PURE-ADDITION, FAIL-CLOSED
(repair round 3, 2026-07-18).

No subtraction anywhere. Enumerates EVERY corrected background-aware per-band universe
component by exact key + content hash, proves the corrected identities

    C_syst      == sum(all corrected per-band components)              (from support family)
    C_combined  == C_syst + C_stat + C_ML                              (stat/ML from SEPARATE ROOTs)

then builds the candidate by dropping only the 5 named support LATERAL bands and ADDING
the 5 selection-complete active per-band MAT blocks:

    C_syst_active     = sum(retained non-lateral bands) + sum(5 active MAT bands)
    C_combined_active = C_syst_active + C_stat + C_ML

Persists in ROOT: 5 active per-band keys, active-only total, C_syst_active, C_combined_active;
and in JSON: every retained pure component key + content hash + source, active traces, and
all identities. Candidate path only. NOT run in the repair round (candidate construction is
gated on the standard-p4-verifier PASS).
"""
import argparse, json, sys
import numpy as np
import p4_lib as P
from uq_math import mat_covariance

BKGAWARE_DIR = "uq_5d/universe_stage2_5d_bkgaware"
SUPERSEDED_TOKENS = ("universe_stage2_5d/uq_universe_5d_covariance_combined.root", "_prehm_", "uthrow_slabs")
SUPPORT_LATERAL = set(P.BANDS)           # the 5 bands replaced by active blocks


def _th2(path, key):
    import ROOT
    f = ROOT.TFile.Open(path)
    if not f or f.IsZombie():
        raise P.P4GateError(f"cannot open {path}")
    h = f.Get(key)
    if not h:
        f.Close(); return None
    n = h.GetNbinsX()
    arr = np.frombuffer(h.GetArray(), dtype=np.float64, count=(n + 2) * (n + 2)).reshape(n + 2, n + 2)
    C = np.ascontiguousarray(arr[1:n + 1, 1:n + 1]); f.Close(); return C


def _flat(path, key):
    import ROOT
    f = ROOT.TFile.Open(path); h = f.Get(key)
    if not h:
        f.Close(); raise P.P4GateError(f"missing {key} in {path}")
    v = np.array([h.GetBinContent(i + 1) for i in range(h.GetNbinsX())]); f.Close(); return v


def _band_keys(path):
    import ROOT
    f = ROOT.TFile.Open(path)
    ks = [k.GetName() for k in f.GetListOfKeys()]; f.Close()
    return sorted(k[len("hCov_universe5d_"):] for k in ks
                  if k.startswith("hCov_universe5d_") and k != "hCov_universe5d_total")


def _chash(C):
    return P.hashlib.sha256(np.ascontiguousarray(C, dtype=np.float64).tobytes()).hexdigest()


def build_active_bands(manifest, idx):
    UDIR = "active_universe_5d/standard/unfolds"
    bands = {}
    for b in P.BANDS:
        pair = []
        for ep in P.ENDPOINTS:
            tag = f"{b}_{ep}"; p = f"{UDIR}/5d_xsec_MEFHC_5iter_lgbm_uni_full_{tag}.root"
            P.require(P.sha256_file(p) == manifest["endpoint_sha256"][tag], f"endpoint {tag} sha256 drift")
            pair.append(_flat(p, "hXSecND_flat")[idx])
        bands[b] = mat_covariance(np.stack([pair[0], pair[1]]))   # MAT biased 1/N (preserved)
    P.require_exact_bands(bands); P.component_traces_positive_finite(bands)
    return bands


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--support-family", required=True, help="corrected bkgaware combined cov ROOT")
    ap.add_argument("--stat-cov", default="uq_cov_stat_5d.root:hCov_stat5d_reported")
    ap.add_argument("--ml-cov", default="uq_cov_mlsplit_5d.root:hCov_mlsplit5d_reported")
    ap.add_argument("--out", required=True, help="candidate ROOT (under candidate subdir)")
    ap.add_argument("--out-manifest", required=True)
    a = ap.parse_args()

    P.require_candidate_path(a.out)                       # positive+negative guard (fixes round-2 self-reject)
    for bad in SUPERSEDED_TOKENS:
        P.require(bad not in a.support_family, f"support family superseded/non-bkgaware ({bad})")
    P.require(BKGAWARE_DIR in a.support_family, "support family must be the corrected bkgaware combined cov")

    man = json.load(open(a.manifest))
    central_path = "products/5d/xsec_5d_MEFHC_5iter_lgbm.root"
    P.require(P.sha256_file(central_path) == man["central5d_sha256"], "central 5D sha256 drift vs manifest")
    central = _flat(central_path, "hXSecND_flat"); mask = central > 0
    hmask, nmask = P.mask_order_hash(mask)
    P.require(hmask == man["mask5d_hash"] and nmask == man["mask5d_nreported"], "reported-mask hash drift")
    idx = np.nonzero(mask)[0]

    # --- enumerate EVERY corrected per-band component (key + content hash) ---
    all_bands = _band_keys(a.support_family)
    comp = {b: _th2(a.support_family, f"hCov_universe5d_{b}") for b in all_bands}
    P.require(all(comp[b] is not None for b in all_bands), "a per-band component failed to load")
    for b in SUPPORT_LATERAL:
        P.require(b in comp, f"support family missing lateral band {b}")
    comp_hash = {b: _chash(comp[b]) for b in all_bands}

    # --- prove corrected identities (NO subtraction) ---
    Csyst_total = _th2(a.support_family, "hCov_universe5d_total")
    Ccomb_total = _th2(a.support_family, "hCov_combined5d_total")
    P.require(Csyst_total is not None and Ccomb_total is not None, "support family totals missing")
    syst_sum = np.zeros_like(Csyst_total)
    for b in all_bands:
        syst_sum = syst_sum + comp[b]
    P.prove_identity(Csyst_total, syst_sum, 1e-6, "C_syst == sum(all per-band)")
    sp, sk = a.stat_cov.split(":"); mp, mk = a.ml_cov.split(":")
    C_stat = _th2(sp, sk); C_ml = _th2(mp, mk)
    P.require(C_stat is not None and C_ml is not None, "stat/ML component ROOT missing")
    P.prove_identity(Ccomb_total, Csyst_total + C_stat + C_ml, 1e-6, "C_combined == C_syst + C_stat + C_ML")

    # --- pure-addition candidate ---
    active = build_active_bands(man, idx)
    active_only = np.zeros_like(Csyst_total)
    for b in P.BANDS:
        active_only = active_only + active[b]
    retained = [b for b in all_bands if b not in SUPPORT_LATERAL]
    Csyst_active = np.zeros_like(Csyst_total)
    for b in retained:
        Csyst_active = Csyst_active + comp[b]
    Csyst_active = Csyst_active + active_only
    Ccomb_active = Csyst_active + C_stat + C_ml
    # identity gates: active-only == sum(5 active); full == retained + active + stat + ml
    P.check_component_sum(active_only, active)                          # exactly 5 bands
    full_check = sum(comp[b] for b in retained) + active_only + C_stat + C_ml
    P.prove_identity(Ccomb_active, full_check, 1e-9, "candidate full == retained + active + stat + ML")
    P.check_symmetric_psd(Csyst_active); P.check_symmetric_psd(Ccomb_active)

    prov = {"support_family": a.support_family, "support_family_sha256": P.sha256_file(a.support_family),
            "stat_cov": a.stat_cov, "stat_sha256": P.sha256_file(sp),
            "ml_cov": a.ml_cov, "ml_sha256": P.sha256_file(mp),
            "all_syst_bands": all_bands, "retained_bands": retained,
            "replaced_lateral_bands": sorted(SUPPORT_LATERAL),
            "component_content_hash": comp_hash, "active_traces": {b: float(np.trace(active[b])) for b in P.BANDS},
            "manifest": a.manifest, "manifest_endpoint_hash": man.get("endpoint_manifest_hash"),
            "reported_mask_hash": man["mask5d_hash"], "n_reported": man["mask5d_nreported"],
            "identities": {"C_syst_eq_sum_bands": True, "C_combined_eq_syst_stat_ml": True,
                           "active_only_eq_sum5": True, "pure_addition": True}}
    json.dump(prov, open(a.out_manifest, "w"), indent=2)

    import ROOT
    n = Ccomb_active.shape[0]; fo = ROOT.TFile.Open(a.out, "RECREATE")
    def wr(name, C, title):
        h = ROOT.TH2D(name, title, n, 0, n, n, 0, n)
        h.SetContent(np.ascontiguousarray(np.pad(C, 1)[0:n + 2, 0:n + 2], dtype=np.float64).ravel())
        h.Write()
    for b in P.BANDS:
        wr(f"hCov_active5d_{b}", active[b], f"active MAT band {b}")
    wr("hCov_active5d_total", active_only, "active-only total (sum of 5 MAT bands)")
    wr("hCov_stdsyst5d_total_candidate", Csyst_active, "candidate C_syst (retained + active)")
    wr("hCov_stdcombined5d_total_candidate", Ccomb_active, "candidate full total (C_syst + stat + ML)")
    fo.Close()
    print(f"CANDIDATE {a.out}: sqrt_tr_syst={np.sqrt(max(0,np.trace(Csyst_active))):.4e} "
          f"sqrt_tr_full={np.sqrt(max(0,np.trace(Ccomb_active))):.4e} bands={len(all_bands)} "
          f"retained={len(retained)}; prov -> {a.out_manifest}")
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except P.P4GateError as e:
        print(f"FAIL-CLOSED :: {e}"); sys.exit(1)
