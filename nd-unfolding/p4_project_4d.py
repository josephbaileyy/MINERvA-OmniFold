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
import argparse, json, sys
import numpy as np
import p4_lib as P

CEN5 = "products/5d/xsec_5d_MEFHC_5iter_lgbm.root"
CEN4 = "products/4d/xsec_4d_MEFHC_5iter_lgbm.root"
CENTRAL_REL = 3.0e-2          # fixed in code; NOT a CLI knob
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

    edges = canonical_edges()
    ebv = P.edges_bin_volume_hash(edges)
    if "edge_hash" in man:
        P.require(ebv["edge_hash"] == man["edge_hash"], "edge-array hash drift vs manifest")

    x5 = _flat(CEN5); x4 = _flat(CEN4); m5 = x5 > 0; m4 = x4 > 0
    P.require(int(m5.sum()) == man["mask5d_nreported"], "5D reported count drift")
    P.require(int(m4.sum()) == man["mask4d_nreported"], "4D reported count drift")
    h5, _ = P.mask_order_hash(m5)
    P.require(h5 == man["mask5d_hash"], "5D mask/order hash drift")

    M = P.build_projection_M(edges, W_AXIS, m5, m4)               # deterministic
    cpath, ckey = a.c5.rsplit(":", 1)
    C5 = _th2(cpath, ckey)
    P.require(C5.shape[0] == int(m5.sum()), "C5 dim != 5D reported bins")
    C4, stats = P.check_projection_nonmutation(C5, M, x5[m5], x4[m4], rtol_central=CENTRAL_REL)

    P.require(P.sha256_file(CEN5) == pre5 and P.sha256_file(CEN4) == pre4,
              "frozen central ROOT changed during projection")

    import ROOT
    n = C4.shape[0]; fo = ROOT.TFile.Open(a.out, "RECREATE")
    h = ROOT.TH2D("hCov_std_proj4d_candidate", "std 5D->4D projected CANDIDATE", n, 0, n, n, 0, n)
    h.SetContent(np.ascontiguousarray(np.pad(C4, 1), dtype=np.float64).ravel()); h.Write(); fo.Close()
    json.dump({"edge_hash": ebv["edge_hash"], "bin_volume_hash": ebv["bin_volume_hash"],
               "mask5d_hash": man["mask5d_hash"], "mask4d_hash": man["mask4d_hash"],
               "central5d_sha256": pre5, "central4d_sha256": pre4,
               "central_reproduction_rel": stats["central_max_rel"], "central_rel_tol": CENTRAL_REL,
               "M_shape": list(M.shape), "psd": stats},
              open(a.out.replace(".root", "_projmanifest.json"), "w"), indent=2)
    print(f"CANDIDATE {a.out} n={n} central_rel={stats['central_max_rel']:.2e}<= {CENTRAL_REL}")
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except P.P4GateError as e:
        print(f"FAIL-CLOSED :: {e}"); sys.exit(1)
