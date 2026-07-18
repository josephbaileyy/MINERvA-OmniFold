#!/usr/bin/env python3
"""P4 5D->4D projection / non-mutation HARD GATE — FAIL-CLOSED (repair 2026-07-18).

C4 = M C5 M^T with exact mask/order/edge bindings (10,694 -> 4,830), finite, rel
symmetry <= 1e-9, PSD (lambda_min >= -1e-12*|lambda_max|), a mandatory declared
central-reproduction threshold, AND byte-identical pre/post SHA256 of BOTH frozen
5D and 4D central ROOTs (non-mutation of the frozen centrals). Fails BEFORE writing
any product on any violation. Authorized to RUN only after the standard-p4-verifier
returns PASS; this repair round does not run it (candidate C5 does not yet exist).
"""
import argparse, json, sys
import numpy as np
import p4_lib as P

CEN5 = "products/5d/xsec_5d_MEFHC_5iter_lgbm.root"
CEN4 = "products/4d/xsec_4d_MEFHC_5iter_lgbm.root"


def _flat(path, key="hXSecND_flat"):
    import ROOT
    f = ROOT.TFile.Open(path); h = f.Get(key)
    v = np.array([h.GetBinContent(i + 1) for i in range(h.GetNbinsX())]); f.Close(); return v


def _th2(path, key):
    import ROOT
    f = ROOT.TFile.Open(path); h = f.Get(key)
    n = h.GetNbinsX(); C = np.empty((n, n))
    for i in range(n):
        for j in range(n):
            C[i, j] = h.GetBinContent(i + 1, j + 1)
    f.Close(); return C


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--c5", required=True, help="candidate C5 ROOT:key (5D reported)")
    ap.add_argument("--proj", required=True, help="M projection npz (key 'M', 4830x10694)")
    ap.add_argument("--manifest", required=True, help="component/standard manifest JSON (hash bindings)")
    ap.add_argument("--out", required=True, help="C4 CANDIDATE ROOT (candidate path only)")
    ap.add_argument("--central-rel", type=float, default=3e-2, help="declared central-reproduction threshold")
    a = ap.parse_args()
    for bad in ("_uthrow", "adopted", "_final", "uq_4d/corrected"):
        P.require(bad not in a.out, f"refusing candidate onto adopted/protected path ({bad})")

    man = json.load(open(a.manifest))
    # non-mutation: frozen centrals must be byte-identical to the manifest bindings
    P.require(P.sha256_file(CEN5) == man["central5d_sha256"], "5D central ROOT mutated (sha256 drift)")
    P.require(P.sha256_file(CEN4) == man["central4d_sha256"], "4D central ROOT mutated (sha256 drift)")
    pre5, pre4 = P.sha256_file(CEN5), P.sha256_file(CEN4)

    cpath, ckey = a.c5.rsplit(":", 1) if ":" in a.c5 else (a.c5, "hCov_std_final5_candidate")
    C5 = _th2(cpath, ckey)
    P.check_symmetric_psd(C5)
    M = np.load(a.proj)["M"]
    x5 = _flat(CEN5); x4 = _flat(CEN4)
    # reported-mask projections of both centrals
    m5 = x5 > 0; m4 = x4 > 0
    P.require(int(m5.sum()) == man["mask5d_nreported"], "5D reported-bin count drift")
    P.require(int(m4.sum()) == man["mask4d_nreported"], "4D reported-bin count drift")
    P.require(M.shape == (int(m4.sum()), int(m5.sum())),
             f"M shape {M.shape} != ({int(m4.sum())},{int(m5.sum())})")
    P.require(C5.shape[0] == int(m5.sum()), "C5 dim != 5D reported bins")

    C4, stats = P.check_projection_nonmutation(C5, M, x5[m5], x4[m4], rtol_central=a.central_rel)

    # frozen centrals unchanged after the whole operation (byte-identical)
    P.require(P.sha256_file(CEN5) == pre5 and P.sha256_file(CEN4) == pre4,
              "frozen central ROOT changed during projection")

    import ROOT
    n = C4.shape[0]; fo = ROOT.TFile.Open(a.out, "RECREATE")
    h = ROOT.TH2D("hCov_std_proj4d_candidate", "std 5D->4D projected CANDIDATE", n, 0, n, n, 0, n)
    for i in range(n):
        for j in range(n):
            h.SetBinContent(i + 1, j + 1, C4[i, j])
    h.Write(); fo.Close()
    print(f"CANDIDATE {a.out} n={n} central_max_rel={stats['central_max_rel']:.2e} "
          f"min/max_eig={stats['min_eig']/max(1e-300,abs(stats['max_eig'])):.2e}")
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except P.P4GateError as e:
        print(f"FAIL-CLOSED :: {e}"); sys.exit(1)
