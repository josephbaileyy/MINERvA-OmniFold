#!/usr/bin/env python3
"""Split-bootstrap analysis: closure (C_data + C_mc ?= C_both) and the
data-statistical vs paper-StatOnly comparison (magnitude AND structure).

Resolves technote App B open question #1 — why our joint Poisson
bootstrap stat block is ~2.55x smaller (and differently structured) than the
paper's StatOnlyCovariance. The data/MC-split campaign fluctuates ONLY the data
weights (boot_data/) or ONLY the MC weights (boot_mc/); both streams use
independent RNGs (rng_data seed=S, rng_mc seed=S+1e7), so in expectation
Cov(both) = Cov(data) + Cov(mc). Comparing C_data alone to the paper StatOnly
tells us whether the 2.55x is (a) just the MC-stat contribution we add on top
(then C_data ~ paper), or (b) genuine OmniFold statistical efficiency vs the
paper's binned D'Agostini stat error (then C_data < paper), or (c) a structural
mismatch (our bootstrap is correlated; the paper StatOnly is ~diagonal).

All covariances are taken on the 205 paper-reported bins in the shared
row-major (pt,pz) / gid=(ptbin-1)*16+(pzbin-1) ordering, so analyze_uq's
hCov2D_reported aligns bin-for-bin with the paper StatOnly masked to reported.

Run in the analysis env (root_6_28):
  python compare_split_bootstrap.py \
    --data  boot_data/uq_covariance_bootdata200.root:hCov2D_reported \
    --mc    boot_mc/uq_covariance_bootmc200.root:hCov2D_reported \
    --both  bootstrap_MEFHC_300/uq_covariance_boot300.root:hCov2D_reported
"""
import argparse
import numpy as np
import ROOT

ANC = ("/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/"
       "minerva_paper_anc/cov_ptpl_minerva_inclusive_6GeV.root")
N_PT, N_PZ, N = 14, 16, 224


def load_cov(spec):
    path, hname = spec.rsplit(":", 1)
    f = ROOT.TFile.Open(path)
    if not f or f.IsZombie():
        raise SystemExit(f"[FAIL] cannot open {path}")
    h = f.Get(hname)
    if not h:
        raise SystemExit(f"[FAIL] hist {hname!r} missing in {path}")
    nx, ny = h.GetNbinsX(), h.GetNbinsY()
    a = np.array([[h.GetBinContent(i, j) for j in range(1, ny + 1)]
                  for i in range(1, nx + 1)])
    f.Close()
    return a


def paper_statonly_reported():
    f = ROOT.TFile.Open(ANC)
    tm = f.Get("StatOnlyCovariance")
    n = tm.GetNrows()
    C = np.array([[tm(i, j) for j in range(n)] for i in range(n)])
    f.Close()
    mask = np.diag(C) > 0
    return C[np.ix_(mask, mask)], int(mask.sum())


def sqrt_tr(C):
    return float(np.sqrt(np.trace(C)))


def off_diag_fraction(C):
    """Mean |corr| off-diagonal — how non-diagonal the matrix is (0 = diagonal)."""
    d = np.sqrt(np.clip(np.diag(C), 0, None))
    ok = d > 0
    R = np.zeros_like(C)
    R[np.ix_(ok, ok)] = C[np.ix_(ok, ok)] / np.outer(d[ok], d[ok])
    iu = np.triu_indices_from(R, k=1)
    return float(np.mean(np.abs(R[iu])))


def lead_overlap(A, B):
    """|cos| between the leading eigenvectors of A and B."""
    va = np.linalg.eigh(A)[1][:, -1]
    vb = np.linalg.eigh(B)[1][:, -1]
    return float(abs(va @ vb))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="ROOT:HIST for C_data")
    ap.add_argument("--mc", required=True, help="ROOT:HIST for C_mc")
    ap.add_argument("--both", required=True, help="ROOT:HIST for C_both (boot300)")
    args = ap.parse_args()
    ROOT.gErrorIgnoreLevel = ROOT.kError

    Cd = load_cov(args.data)
    Cm = load_cov(args.mc)
    Cb = load_cov(args.both)
    Cp, npaper = paper_statonly_reported()
    n = Cd.shape[0]
    if not (Cm.shape[0] == Cb.shape[0] == n):
        raise SystemExit(f"[FAIL] shape mismatch: data {Cd.shape} mc {Cm.shape} both {Cb.shape}")
    if Cp.shape[0] != n:
        print(f"[WARN] paper reported {Cp.shape[0]} != ours {n} — alignment check")

    Csum = Cd + Cm

    print(f"\n{'='*64}\n CLOSURE:  C_data + C_mc  vs  C_both (boot300)\n{'='*64}")
    print(f"  sqrt-tr  C_data      = {sqrt_tr(Cd):.4e}")
    print(f"  sqrt-tr  C_mc        = {sqrt_tr(Cm):.4e}")
    print(f"  sqrt-tr  C_data+C_mc = {sqrt_tr(Csum):.4e}")
    print(f"  sqrt-tr  C_both      = {sqrt_tr(Cb):.4e}")
    print(f"  --> trace ratio  tr(data+mc)/tr(both) = {np.trace(Csum)/np.trace(Cb):.4f}"
          f"   (1.00 = perfect closure)")
    fro = np.linalg.norm(Csum - Cb) / np.linalg.norm(Cb)
    print(f"  --> Frobenius ||(data+mc) - both|| / ||both|| = {fro:.4f}")
    dd_sum = np.sqrt(np.clip(np.diag(Csum), 0, None))
    dd_b = np.sqrt(np.clip(np.diag(Cb), 0, None))
    ok = dd_b > 0
    print(f"  --> per-bin sigma: median (data+mc)/both = "
          f"{np.median(dd_sum[ok]/dd_b[ok]):.4f}")
    print(f"  --> data/mc variance split: data {np.trace(Cd)/np.trace(Csum)*100:4.1f}% "
          f"/ mc {np.trace(Cm)/np.trace(Csum)*100:4.1f}%")

    print(f"\n{'='*64}\n DATA-STAT vs PAPER StatOnly  (open question #1)\n{'='*64}")
    print(f"  sqrt-tr  C_data        = {sqrt_tr(Cd):.4e}")
    print(f"  sqrt-tr  C_both        = {sqrt_tr(Cb):.4e}")
    print(f"  sqrt-tr  paper StatOnly= {sqrt_tr(Cp):.4e}")
    print(f"  --> sigma ratio  C_data / paper   = {sqrt_tr(Cd)/sqrt_tr(Cp):.3f}")
    print(f"  --> sigma ratio  C_both / paper   = {sqrt_tr(Cb)/sqrt_tr(Cp):.3f}  "
          f"(the known ~0.39 = 1/2.55)")
    print(f"\n  STRUCTURE (is ours diagonal like the paper?):")
    print(f"  --> mean |off-diag corr|:  C_data {off_diag_fraction(Cd):.3f}   "
          f"C_both {off_diag_fraction(Cb):.3f}   paper StatOnly {off_diag_fraction(Cp):.3f}"
          f"   (0 = diagonal)")
    print(f"  --> leading-eigvec overlap |cos|:  C_data·paper = {lead_overlap(Cd, Cp):.3f}   "
          f"C_both·paper = {lead_overlap(Cb, Cp):.3f}")
    wd = np.linalg.eigvalsh(Cd)[::-1]
    wp = np.linalg.eigvalsh(Cp)[::-1]
    print(f"  --> rank(>1e-12·max):  C_data {int((wd>wd[0]*1e-12).sum())}   "
          f"paper StatOnly {int((wp>wp[0]*1e-12).sum())} (diagonal => full {npaper})")

    print(f"\n{'='*64}\n VERDICT\n{'='*64}")
    rd = sqrt_tr(Cd) / sqrt_tr(Cp)
    if rd > 0.9:
        print("  C_data ~ paper StatOnly in magnitude: the 2.55x on C_both is the")
        print("  MC-stat contribution we ADD on top — paper stat ~ our data-stat alone.")
    elif rd < 0.6:
        print("  C_data << paper StatOnly: our DATA-statistical error is genuinely")
        print("  smaller than the paper's binned-D'Agostini stat error (OmniFold")
        print("  efficiency), independent of the MC stream.")
    else:
        print(f"  C_data / paper = {rd:.2f}: intermediate — partly OmniFold efficiency,")
        print("  partly the MC split; inspect structure below for the full story.")
    print("  (Structure: if mean|off-diag| differs a lot from the paper's, the gap is")
    print("   also a correlation-shape mismatch, not pure magnitude — see Check #3.)")


if __name__ == "__main__":
    main()
