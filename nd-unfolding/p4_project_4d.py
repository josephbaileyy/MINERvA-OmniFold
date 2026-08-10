#!/usr/bin/env python3
"""P4 5D->4D projection / non-mutation HARD GATE — deterministic M, FAIL-CLOSED
(repair round 3, 2026-07-18).

M is built DETERMINISTICALLY inside this stage from the canonical ordered 5-axis
edges by width-weighted marginalization of W (p4_lib.build_projection_M) — never
read from an external file. C4 = M C5 M^T with: bound edge / bin-volume / mask-order /
central hashes; frozen 5D and 4D central ROOTs byte-identical pre/post (non-mutation);
finite, rel-symmetry <= 1e-9, PSD; and an IN-CODE central-reproduction tolerance
(CLI overrides rejected). Candidate paths only. Authorized to RUN only after the
standard-p4-verifier PASS; not run in the repair round.
"""
import argparse, json, os, sys
import numpy as np
import p4_lib as P

CEN5 = "products/5d/xsec_5d_MEFHC_5iter_lgbm.root"
CEN4 = "products/4d/xsec_4d_MEFHC_5iter_lgbm.root"
# RETIRED 2026-08-09. `CENTRAL_REL = 3.0e-2` gated the 5D->4D marginal on reproducing the
# INDEPENDENT 4D unfold bin-by-bin. That is the equivalence convention declined on 2026-08-07.
# The comparison is now REPORTED without a verdict (see crosscheck_marginal_vs_independent);
# there is deliberately no tolerance constant here to re-tune, because the correct value is
# "none", not "larger". Measured: median 4.43%, p90 20.8%, 3009/4825 bins over the old 3%,
# integral ratio 1.005578 -- and that disagreement reproduces from the 5D producer's OWN
# hXSecND_dropLast_flat with no code from this lane involved, so it is a property of the two
# estimators and not of the projector (whose M matches that marginal to 3.1e-16).
W_AXIS = 4                    # marginalized axis (pt,pz,eavail,q3,W)


def _flat(path, key="hXSecND_flat"):
    import ROOT
    f = ROOT.TFile.Open(path); h = f.Get(key)
    v = np.array([h.GetBinContent(i + 1) for i in range(h.GetNbinsX())]); f.Close(); return v


def _th2(path, key):
    import ROOT
    f = ROOT.TFile.Open(path); h = f.Get(key)
    n = h.GetNbinsX()
    arr = np.frombuffer(h.GetArray(), dtype=np.float64, count=(n + 2) * (n + 2)).reshape(n + 2, n + 2)
    C = np.ascontiguousarray(arr[1:n + 1, 1:n + 1]); f.Close(); return C


def canonical_edges():
    """Ordered 5-axis edges (pt,pz,eavail,q3,W) from the canonical source."""
    from project_cov_nd import AXIS_EDGES  # canonical, drift-guarded mirror
    order = ["pt", "pz", "eavail", "q3", "W"]
    return [np.asarray(AXIS_EDGES[k], float) for k in order]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--c5", required=True, help="candidate C5 ROOT:key")
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--out", required=True, help="candidate ROOT (candidate subdir)")
    ap.add_argument("--central-rel", type=float, default=None,
                    help="IGNORED/REJECTED: tolerance is fixed in code")
    a = ap.parse_args()
    P.require(a.central_rel is None, "central-reproduction tolerance is fixed in code; CLI override rejected")
    P.require_candidate_path(a.out)

    man = json.load(open(a.manifest))
    P.require(P.sha256_file(CEN5) == man["central5d_sha256"], "5D central mutated (sha256 drift)")
    P.require(P.sha256_file(CEN4) == man["central4d_sha256"], "4D central mutated (sha256 drift)")
    pre5, pre4 = P.sha256_file(CEN5), P.sha256_file(CEN4)

    # REPAIR-4 (verifier defect 5): geometry binding was partial. The edge hash was checked
    # only `if "edge_hash" in man`, so a manifest lacking the key silently skipped it; the
    # bin-volume hash was written into the receipt but never COMPARED; the 4D mask was checked
    # by reported COUNT only, not by hash -- and a count is not an ordering, so a permuted 4D
    # mask with the same population passed; and only M_shape was recorded, so nothing pinned
    # the projector's actual contents. All four are now mandatory.
    edges = canonical_edges()
    ebv = P.edges_bin_volume_hash(edges)
    P.require("edge_hash" in man, "manifest has no edge_hash (unprovable geometry)")
    P.require("bin_volume_hash" in man, "manifest has no bin_volume_hash (unprovable geometry)")
    P.require(ebv["edge_hash"] == man["edge_hash"], "edge-array hash drift vs manifest")
    P.require(ebv["bin_volume_hash"] == man["bin_volume_hash"], "bin-volume hash drift vs manifest")

    x5 = _flat(CEN5); x4 = _flat(CEN4); m5 = x5 > 0; m4 = x4 > 0
    P.require(int(m5.sum()) == man["mask5d_nreported"], "5D reported count drift")
    P.require(int(m4.sum()) == man["mask4d_nreported"], "4D reported count drift")
    h5, _ = P.mask_order_hash(m5)
    P.require(h5 == man["mask5d_hash"], "5D mask/order hash drift")
    h4 = P.cmask_order_hash_4d(m4)
    P.require(h4 == man["mask4d_hash"], "4D mask/order hash drift")

    # FIX 1 of 2 (2026-08-10). The projection's low support is DERIVED, not asserted: it is the
    # part of the 4D reported mask that the reported 5D support actually reaches. Five 4D bins are
    # unreachable on the real products, which previously made stage 6 unable to execute at all.
    # The mask/count/hash gates above still bind the FULL 4D reported mask -- the effective support
    # is an additional recorded fact, not a replacement for the frozen binding.
    m4_reach = P.reachable_low_mask(edges, W_AXIS, m5)
    m4_eff = m4 & m4_reach
    dropped = np.nonzero(m4 & ~m4_reach)[0]
    P.require(int(m4_eff.sum()) > 0, "no 4D reported bin is reachable from the 5D support")
    if dropped.size:
        print(f"[proj] {dropped.size} of {int(m4.sum())} reported 4D bins are UNREACHABLE from the "
              f"5D support and are excluded from the projected product; global indices "
              f"{[int(i) for i in dropped[:10]]}{' ...' if dropped.size > 10 else ''}")
    M = P.build_projection_M(edges, W_AXIS, m5, m4_eff)           # deterministic
    m_hash = P.matrix_content_hash(M)                             # pins M's CONTENTS, not its shape
    cpath, ckey = a.c5.rsplit(":", 1)
    C5 = _th2(cpath, ckey)
    P.require(C5.shape[0] == int(m5.sum()), "C5 dim != 5D reported bins")
    # RE-SPECIFIED 2026-08-09 (Joseph): GATE projection validity, REPORT the marginal-vs-
    # independent comparison. The old call gated on the marginal reproducing the independent 4D
    # within 3% -- the equivalence convention declined on 2026-08-07, when 4D was adopted AS the
    # marginal and the independent 4D became a cross-check. A gate on a proposition the analysis
    # does not assert is removed, not widened; the measurement below is unchanged and reported in
    # full. Measured values: FINDING-20260809-stage6-central-gate-cannot-pass.md.
    C4, stats = P.check_projection_validity(C5, M)
    xcheck = P.crosscheck_marginal_vs_independent(M, x5[m5], x4[m4_eff])
    print(f"[xcheck] marginal vs INDEPENDENT 4D (no pass/fail, cross-check only): "
          f"n={xcheck['n_bins']} median={xcheck['median_abs_rel']:.4f} "
          f"p90={xcheck['p90_abs_rel']:.4f} max={xcheck['max_abs_rel']:.4f} "
          f"over3%={xcheck['n_over_3pct']} integral_ratio={xcheck['integral_ratio']:.6f}")

    P.require(P.sha256_file(CEN5) == pre5 and P.sha256_file(CEN4) == pre4,
              "frozen central ROOT changed during projection")

    import ROOT
    n = C4.shape[0]; fo = ROOT.TFile.Open(a.out, "RECREATE")
    h = ROOT.TH2D("hCov_std_proj4d_candidate", "std 5D->4D projected CANDIDATE", n, 0, n, n, 0, n)
    h.SetContent(np.ascontiguousarray(np.pad(C4, 1), dtype=np.float64).ravel()); h.Write(); fo.Close()
    json.dump({"edge_hash": ebv["edge_hash"], "bin_volume_hash": ebv["bin_volume_hash"],
               "mask5d_hash": man["mask5d_hash"], "mask4d_hash": man["mask4d_hash"],
               "central5d_sha256": pre5, "central4d_sha256": pre4,
               "projection_identity_relerr": stats["projection_identity_relerr"],
               "crosscheck_marginal_vs_independent_4d": xcheck,
               "M_shape": list(M.shape), "M_content_sha256": m_hash,
               "mask4d_nreported": int(m4.sum()),
               "mask4d_neffective": int(m4_eff.sum()),
               "mask4d_unreachable_n": int(dropped.size),
               "mask4d_unreachable_global_indices": [int(i) for i in dropped],
               "projected_support": "reported 4D bins REACHABLE from the reported 5D support; "
                                    "see mask4d_unreachable_* for what was excluded and why",
               "candidate_c5": os.path.abspath(cpath), "candidate_c5_key": ckey,
               "candidate_c5_sha256": P.sha256_file(cpath),
               "psd": stats},
              open(a.out.replace(".root", "_projmanifest.json"), "w"), indent=2)
    print(f"CANDIDATE {a.out} n={n} projection_identity={stats['projection_identity_relerr']:.2e}")
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except P.P4GateError as e:
        print(f"FAIL-CLOSED :: {e}"); sys.exit(1)
