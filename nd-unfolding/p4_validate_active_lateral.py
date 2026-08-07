#!/usr/bin/env python3
"""P4 standard candidate validator — FAIL-CLOSED (repair round 3, 2026-07-18).

Validates the component-built candidate against the predeclared gates and ties it
INSEPARABLY to the audited merged inputs (no cosmetic --merged-dir):
  - candidate carries exactly the 5 active per-band keys (hCov_active5d_<band>),
    positive-finite traces;
  - active-only total == exact sum of the 5 active bands;
  - symmetry+PSD on active-only / candidate C_syst / candidate full;
  - complete support-limited comparison (active-only vs sum of 5 support lateral bands);
  - MERGED INSEPARABILITY: the manifest's 10 merged SHA256 == the merged-audit receipt's
    10 per-endpoint SHA256, exactly (and both are the canonical 10).
Any failure -> nonzero exit, no PASS summary. Reuses p4_lib gates.
"""
import argparse, json, os, sys
import numpy as np
import p4_lib as P


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True, help="p4_build_components output ROOT")
    ap.add_argument("--support", required=True, help="corrected bkgaware combined cov ROOT")
    ap.add_argument("--manifest", required=True, help="p4_standard_manifest.json (merged SHA + digest)")
    ap.add_argument("--merged-audit", required=True, help="p4_merged_audit.json")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    # J32 (AUDIT-FINDINGS-20260731): the PASS receipt used to carry `gates`, `active_traces`,
    # `active_only_sum_relerr`, `support_comparison` and `result` -- and NO candidate path and NO
    # candidate sha256. There was nothing in it to bind a candidate to, so ANY pass receipt
    # satisfied ANY candidate and `p4_adopt_standard.py` could only test that its own candidate was
    # readable. The fix has to start here, not in the adopter: record WHAT was validated.
    out = {"gates": [], "result": "FAIL",
           "candidate": os.path.abspath(a.candidate),
           "candidate_sha256": P.sha256_file(a.candidate)}
    try:
        # merged inseparability (no cosmetic dir): manifest 10 SHA == merged-audit 10 SHA
        man = json.load(open(a.manifest)); aud = json.load(open(a.merged_audit))
        man_sha = man.get("merged_sha256") or {}
        aud_sha = {t: r.get("sha256") for t, r in aud.get("merged", {}).items() if r.get("sha256")}
        # normalize manifest keys (path->sha) to tag->sha
        def _tag(p): return p.split("active_")[-1].replace(".root", "")
        man_by_tag = {}
        for k, v in man_sha.items():
            man_by_tag[_tag(k) if "/" in k or ".root" in k else k] = v
        P.require(len(aud_sha) == P.N_ENDPOINTS, f"merged-audit has {len(aud_sha)} != 10 hashes")
        P.require(len(man_by_tag) == P.N_ENDPOINTS, f"manifest has {len(man_by_tag)} != 10 merged hashes")
        P.require(set(man_by_tag) == set(aud_sha) and all(man_by_tag[t] == aud_sha[t] for t in aud_sha),
                  "merged SHA256 mismatch between manifest and merged-audit receipt")
        out["gates"].append("merged_inseparability")

        # REPAIR-4 (defect 3e): the merged-audit JSON was LOADED and then used only for its ten
        # SHA values. Every census, completeness and migration field it carries -- the evidence
        # the audit exists to produce -- was ignored, so a validator PASS said nothing about
        # whether the endpoints were the declared ones or behaved as declared.
        NONZERO_MIG = {"BeamAngleX", "BeamAngleY"}
        ZERO_SEL = {"MuonResolution", "Muon_Energy_MINERvA", "Muon_Energy_MINOS"}
        for b in P.BANDS:
            for ep in P.ENDPOINTS:
                t = f"{b}_{ep}"
                r = aud.get("merged", {}).get(t)
                P.require(r is not None, f"merged-audit has no entry for {t}")
                P.require(r.get("band_meta") == b,
                          f"merged-audit {t} band identity {r.get('band_meta')!r} != {b}")
                idx = r.get("idx_meta")
                P.require(idx is not None and int(float(idx)) == int(ep),
                          f"merged-audit {t} endpoint INDEX {idx!r} != {ep}")
                te = r.get("tree_entries") or {}
                P.require(te and all(int(v) > 0 for v in te.values()),
                          f"merged-audit {t} has an empty tree")
                P.require(int(te.get("mc_signal_reco", -1)) == int(te.get("mc_truth_denom", -2)),
                          f"merged-audit {t} completeness: signal_reco != truth_denom")
                sm = r.get("selection_migration_abs")
                P.require(sm is not None, f"merged-audit {t} has no migration census")
                if b in NONZERO_MIG:
                    P.require(int(sm) > 0, f"merged-audit {t} expected NONZERO migration, got {sm}")
                else:
                    P.require(b in ZERO_SEL, f"merged-audit {t} band {b} in neither migration set")
                    P.require(int(sm) == 0,
                              f"merged-audit {t} is bin-migration-only but migrated {sm}")
        out["gates"].append("merged_audit_census_and_migration")

        # D4f: bind the component manifest the builder wrote next to this candidate, and prove
        # it describes THIS file. Previously the validator never opened it, so candidate and
        # component provenance were separable -- either could be swapped without detection.
        comp_path = os.path.join(os.path.dirname(os.path.abspath(a.candidate)),
                                 "std_component_manifest.json")
        P.require(os.path.exists(comp_path),
                  f"component manifest not found beside the candidate ({comp_path})")
        comp = json.load(open(comp_path))
        P.require(comp.get("candidate_sha256") == out["candidate_sha256"],
                  "component manifest does not describe THIS candidate (sha256 mismatch)")
        P.require(comp.get("identities", {}).get("pure_addition"),
                  "component manifest is not pure-addition")
        P.require(comp.get("reported_mask_hash") == man.get("mask5d_hash"),
                  "component manifest reported-mask hash != evidence manifest")
        for k in comp.get("candidate_keys", []):
            P.require(_th2(a.candidate, k) is not None,
                      f"component manifest claims key {k} which the candidate does not contain")
        out["component_manifest"] = comp_path
        out["component_manifest_sha256"] = P.sha256_file(comp_path)
        out["gates"].append("component_manifest_bound")

        active = {b: _th2(a.candidate, f"hCov_active5d_{b}") for b in P.BANDS}
        active = {b: c for b, c in active.items() if c is not None}
        P.require_exact_bands(active); out["gates"].append("exact_5_active_bands")
        out["active_traces"] = P.component_traces_positive_finite(active); out["gates"].append("traces_pos_finite")
        active_total = _th2(a.candidate, "hCov_active5d_total")
        P.require(active_total is not None, "candidate active-only total missing")
        out["active_only_sum_relerr"] = P.check_component_sum(active_total, active)
        out["gates"].append("active_total_eq_sum5")
        for key in (P.CANDIDATE_ACTIVE_TOTAL_KEY, P.CANDIDATE_SYST_KEY, P.CANDIDATE_TOTAL_KEY):
            P.check_symmetric_psd(_th2(a.candidate, key))
        out["gates"].append("symmetric_psd")
        # D4f: RECOMPUTE the full-total identity rather than trusting the manifest's boolean.
        # C_combined = C_syst + C_stat + C_ML, so the residual must itself be a covariance:
        # symmetric and PSD. A candidate whose combined total was not built by pure addition
        # from its own C_syst fails here, using only what is inside the candidate file.
        Csyst = _th2(a.candidate, P.CANDIDATE_SYST_KEY)
        Ccomb = _th2(a.candidate, P.CANDIDATE_TOTAL_KEY)
        resid = Ccomb - Csyst
        P.check_symmetric_psd(resid)
        out["combined_minus_syst_min_eig_ratio"] = float(
            np.min(np.linalg.eigvalsh((resid + resid.T) / 2.0)) / max(1e-300, np.abs(resid).max()))
        out["gates"].append("combined_minus_syst_is_psd")
        support_bands = {b: _th2(a.support, f"hCov_universe5d_{b}") for b in P.BANDS}
        P.require(all(support_bands[b] is not None for b in P.BANDS), "support family lateral block incomplete")
        out["support_comparison"] = P.check_support_comparison(active_total, sum(support_bands[b] for b in P.BANDS))
        out["gates"].append("complete_support_comparison")
        out["result"] = "PASS"
    except P.P4GateError as e:
        out["error"] = str(e); json.dump(out, open(a.out, "w"), indent=2)
        print(f"RESULT FAIL :: {e}"); sys.exit(1)
    json.dump(out, open(a.out, "w"), indent=2)
    print("RESULT PASS — gates:", ",".join(out["gates"]),
          f"support_ratio={out['support_comparison']['ratio']:.3f}")
    sys.exit(0)


if __name__ == "__main__":
    main()
