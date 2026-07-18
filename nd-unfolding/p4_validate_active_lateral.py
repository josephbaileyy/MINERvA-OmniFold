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
import argparse, json, sys
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
    out = {"gates": [], "result": "FAIL"}
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

        active = {b: _th2(a.candidate, f"hCov_active5d_{b}") for b in P.BANDS}
        active = {b: c for b, c in active.items() if c is not None}
        P.require_exact_bands(active); out["gates"].append("exact_5_active_bands")
        out["active_traces"] = P.component_traces_positive_finite(active); out["gates"].append("traces_pos_finite")
        active_total = _th2(a.candidate, "hCov_active5d_total")
        P.require(active_total is not None, "candidate active-only total missing")
        out["active_only_sum_relerr"] = P.check_component_sum(active_total, active)
        out["gates"].append("active_total_eq_sum5")
        for key in ("hCov_active5d_total", "hCov_stdsyst5d_total_candidate", "hCov_stdcombined5d_total_candidate"):
            P.check_symmetric_psd(_th2(a.candidate, key))
        out["gates"].append("symmetric_psd")
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
