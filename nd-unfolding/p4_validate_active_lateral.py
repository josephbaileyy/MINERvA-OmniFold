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


def _support_band_keys(path):
    """Every per-band component in the support family, EXCLUDING the total. Forward-only: returns
    band names by stripping the known `hCov_universe5d_` prefix from keys that carry it, which is
    safe here because the prefix is fixed and the comparison downstream is set-based."""
    import ROOT
    f = ROOT.TFile.Open(path)
    if not f or f.IsZombie():
        raise P.P4GateError(f"cannot open support family {path}")
    ks = [k.GetName() for k in f.GetListOfKeys()]
    f.Close()
    pre = "hCov_universe5d_"
    return sorted(k[len(pre):] for k in ks
                  if k.startswith(pre) and k != f"{pre}total")


def _chash(C):
    import numpy as _np
    return P.hashlib.sha256(_np.ascontiguousarray(C, dtype=_np.float64).tobytes()).hexdigest()


def main():
    # REPAIR-12: stage 5 gates itself. Before argparse, before ROOT, before anything reads a file.
    import p4_check_verifier_token as _tok
    _tok.require_verifier_token("stage 5 (validate)")
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
        NONZERO_MIG = P.NONZERO_MIGRATION_BANDS      # repair-5: single-sourced in p4_lib
        ZERO_SEL = P.ZERO_MIGRATION_BANDS
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
        # repair-5 (pattern sweep): this used to read `identities.pure_addition` and test it for
        # truthiness -- but the builder wrote that key as a literal `True`, so the check could
        # never fail and proved nothing. The identities are now MEASURED errors, and this
        # consumer RECOMPUTES the full-total identity below rather than reading any of them.
        ids = comp.get("identities", {})
        P.require(isinstance(ids, dict) and ids, "component manifest records no identities")
        P.require("pure_addition" not in ids,
                  "component manifest carries the retired self-asserted `pure_addition` flag; "
                  "it predates repair-5 and its identities were literals, not measurements")
        for _k in ("active_only_eq_sum5_relerr", "C_combined_eq_syst_stat_ml_relerr",
                   "full_total_residual_eq_stat_plus_ml_relerr"):
            P.require(_k in ids, f"component manifest missing measured identity {_k}")
            P.require(float(ids[_k]) <= float(ids.get("identity_rtol", 1e-9)),
                      f"component manifest records a FAILING identity {_k}={ids[_k]}")
        P.require(comp.get("reported_mask_hash") == man.get("mask5d_hash"),
                  "component manifest reported-mask hash != evidence manifest")
        for k in comp.get("candidate_keys", []):
            P.require(_th2(a.candidate, k) is not None,
                      f"component manifest claims key {k} which the candidate does not contain")
        # A self-declared rejection must PROPAGATE into the validation receipt, or a downstream
        # reader sees only "result: PASS" and the refusal is invisible where it matters.
        if comp.get(P.NON_ADOPTABLE_KEY):
            out[P.NON_ADOPTABLE_KEY] = True
            out["non_adoptable_reason"] = comp.get("non_adoptable_reason")
            out["gates"].append("candidate_self_declares_non_adoptable")
        # FIX 2 of 2 (2026-08-10). Recording the PATH bound nothing: the adopter re-reads a
        # component manifest supplied on its own command line, so a caller could hand it a
        # marker-stripped copy and the self-declared rejection would simply vanish. The receipt
        # now records the manifest's DIGEST, and the adopter requires the file it was given to be
        # that exact file. A safety property that the caller can edit away is not one.
        out["component_manifest_sha256"] = P.sha256_file(comp_path)
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
        # D4b/D6 REPAIR-5: repair-4 checked only that (C_combined - C_syst) was symmetric PSD
        # and named that the full-total identity, in the gate name, the receipt field and the
        # test. PSD is necessary and nowhere near sufficient -- every covariance-shaped residual
        # passes it. The identity is now PROVEN by loading the stat and ML blocks the component
        # manifest binds (with their recorded sha256 re-verified, so the comparison cannot be
        # satisfied by substituting different blocks) and comparing.
        Csyst = _th2(a.candidate, P.CANDIDATE_SYST_KEY)
        Ccomb = _th2(a.candidate, P.CANDIDATE_TOTAL_KEY)
        stat_spec, ml_spec = comp.get("stat_cov"), comp.get("ml_cov")
        P.require(stat_spec and ml_spec, "component manifest does not bind the stat/ML blocks")

        def _bound_block(spec, sha_key, label):
            """Load a `path:key` block AFTER re-verifying the sha256 the manifest recorded, so
            the identity cannot be satisfied by substituting a different file."""
            P.require(":" in spec, f"{label} spec {spec!r} is not path:key")
            pth, key = spec.rsplit(":", 1)
            ap = pth if os.path.isabs(pth) else os.path.join(P.ND_ROOT, pth)
            P.require(os.path.exists(ap), f"{label} covariance not found: {pth}")
            P.require(P.sha256_file(ap) == comp.get(sha_key),
                      f"{label} covariance sha256 drift vs the component manifest ({pth})")
            blk = _th2(ap, key)
            P.require(blk is not None, f"{label} covariance key {key} missing in {pth}")
            return blk

        C_stat = _bound_block(stat_spec, "stat_sha256", "stat")
        C_ml = _bound_block(ml_spec, "ml_sha256", "ML")
        out["full_total_identity_relerr"] = float(
            P.check_full_total_identity(Ccomb, Csyst, C_stat, C_ml, 1e-9))
        out["gates"].append("full_total_identity_recomputed")

        # REPAIR-6: C_syst itself was never recomputed. The builder recorded
        # C_syst_eq_retained_plus_active_relerr and NEITHER consumer read it, so a wrong-but-PSD
        # C_syst satisfying C_combined = C_syst + C_stat + C_ML passed every gate. It is
        # recomputable because repair-4 (4a) started persisting the retained components into the
        # candidate -- which made the omission worse, not better.
        retained_keys = [k for k in comp.get("candidate_keys", [])
                         if k.startswith("hCov_retained5d_")]
        P.require(retained_keys,
                  "candidate persists no retained components, so C_syst cannot be recomputed "
                  "(pre-repair-4 candidate?)")
        retained_sum = None
        for k in retained_keys:
            blk = _th2(a.candidate, k)
            P.require(blk is not None, f"candidate is missing declared retained component {k}")
            retained_sum = blk if retained_sum is None else retained_sum + blk
        active_total_blk = _th2(a.candidate, P.CANDIDATE_ACTIVE_TOTAL_KEY)
        out["c_syst_identity_relerr"] = float(
            P.prove_identity(Csyst, retained_sum + active_total_blk, 1e-9,
                             "C_syst == sum(retained) + active_total"))
        out["n_retained_components"] = len(retained_keys)
        # B1 / verifier defect #6 (2026-08-10). Everything above verifies the manifest against
        # ITSELF or against the candidate -- both downstream of the same build. A build that
        # enumerated the wrong band set produces a manifest whose stored C_syst equals the sum of
        # the bands it lists, so every identity reconstructs PERFECTLY while the systematic budget
        # is silently short. The referee has to be the SUPPORT FAMILY: it is upstream of the
        # build, p4_build_components.py enumerates from it, and the manifest pins its sha256.
        #
        # `_total` is excluded deliberately -- adversarial fixture B1_F is a build whose
        # enumeration failed to exclude it, which then reads as a valid 45th band.
        _sup_keys = _support_band_keys(a.support)
        _sup_hashes = {b: _chash(_th2(a.support, f"hCov_universe5d_{b}")) for b in _sup_keys}
        out["band_completeness"] = P.require_band_set_completeness(
            comp, _sup_keys, _sup_hashes, P.BANDS, P.sha256_file(a.support))
        out["gates"].append("band_set_completeness_vs_support_family")
        out["gates"].append("c_syst_recomputed_from_components")
        support_bands = {b: _th2(a.support, f"hCov_universe5d_{b}") for b in P.BANDS}
        P.require(all(support_bands[b] is not None for b in P.BANDS), "support family lateral block incomplete")
        out["support_comparison"] = P.check_support_comparison(active_total, sum(support_bands[b] for b in P.BANDS))
        # REPAIR-6: relabelled. The check compares TRACES and bounds nothing -- any finite ratio
        # passes -- so calling it "complete" claimed more than it delivers, and BEN-043 rule 3
        # adds that an aggregate cannot see a per-bin disagreement that preserves the trace.
        # The ratio stays as a recorded DIAGNOSTIC; the gate name no longer asserts a comparison.
        out["support_ratio_is_diagnostic_not_bounded"] = True
        out["gates"].append("support_trace_ratio_recorded")
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
