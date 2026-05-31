#!/usr/bin/env python3
"""Rederive the flux <-> muon-energy-scale joint covariance block -- the one
off-block-diagonal correlation the Ruterbories paper admits (Bashyal low-recoil
fit, JINST 16 P08068), and uq_statistical_methods open question #1.

Two routes:
  A. PAPER rederivation. The data release ships marginal blocks Total, Stat,
     Flux, MuonEnergyScale (224x224; 205 reported). MuonEnergyScale is rank-1
     (single +-1sigma scale mode e_hat). The residual D = Total-Stat-Flux-ES
     contains the unshipped *independent* sources PLUS the flux<->ES cross term;
     the cross term is the ONLY part of D that couples e_hat to the flux
     subspace. So
         u = P_flux( D @ e_hat ),   C_cross = u e_hat^T + e_hat u^T   (rank 2),
     and the implied correlation rho = |u| / sqrt(v_f * v_e), with
     v_f = f_hat^T Flux f_hat, v_e = e_hat^T ES e_hat, f_hat = u/|u|.

  B. OURS-ONLY reconstruction. Using our own per-band shift vectors
     d_f = sqrt(lambda_max) v_max of our Flux band cov, d_e likewise of our
     (Muon_Energy_MINOS + Muon_Energy_MINERvA) band cov, build
         C_cross^ours = rho ( d_f d_e^T + d_e d_f^T )
     (rho from route A, or from Bashyal) and add it to our block-diagonal
     C^syst. Report the rank / condition / flux-ES-coupling effect.

Run in the analysis env (root_6_28).
"""
import os
import numpy as np
import ROOT

HERE = os.path.dirname(os.path.abspath(__file__))
ANC = os.path.join(HERE, "..", "minerva_paper_anc",
                   "cov_ptpl_minerva_inclusive_6GeV.root")
OURS = os.path.join(HERE, "universe_stage2_MEFHC_full_matcorr",
                    "uq_universe_covariance_full_matcorr.root")


def m2np(M):
    n = M.GetNrows()
    a = np.empty((n, n))
    for i in range(n):
        for j in range(n):
            a[i, j] = M(i, j)
    return a


def th2np(h):
    nx = h.GetNbinsX()
    a = np.empty((nx, nx))
    for i in range(nx):
        for j in range(nx):
            a[i, j] = h.GetBinContent(i + 1, j + 1)
    return a


def lead_mode(C):
    """sigma-scaled leading eigenvector sqrt(lambda_max) v_max (sign-fixed)."""
    w, v = np.linalg.eigh(C)
    vmax = v[:, -1]
    vmax = vmax * np.sign(vmax[np.argmax(np.abs(vmax))])
    return np.sqrt(max(w[-1], 0.0)) * vmax, w[-1]


def main():
    ROOT.gErrorIgnoreLevel = ROOT.kError
    # ---- paper blocks, restricted to the 205 reported bins ----
    fp = ROOT.TFile.Open(ANC)
    T = m2np(fp.Get("TotalCovariance")); S = m2np(fp.Get("StatOnlyCovariance"))
    F = m2np(fp.Get("FluxCovariance")); E = m2np(fp.Get("MuonEnergyScaleCovariance"))
    fp.Close()
    rep = np.diag(S) > 0
    idx = np.where(rep)[0]
    T, S, F, E = (M[np.ix_(idx, idx)] for M in (T, S, F, E))
    n = T.shape[0]
    print(f"[load] paper blocks restricted to {n} reported bins")

    # ---- Route A: rederive the cross block from the paper ----
    we, le = np.linalg.eigh(E)
    e_hat = le[:, -1]; e_hat *= np.sign(e_hat[np.argmax(np.abs(e_hat))])
    rk_E = int((we > 1e-12 * we.max()).sum())
    print(f"[A] MuonEnergyScale rank={rk_E}  sigma_ES=|d_e|={np.sqrt(we[-1]):.3e}")

    # flux leading mode (normalization-dominated direction the Bashyal fit
    # couples to muon-E scale)
    df_paper, lf_paper = lead_mode(F)
    f_hat = df_paper / np.linalg.norm(df_paper)

    # (a) DEFENSIBLE estimate: Cauchy-Schwarz-bounded correlation between the
    #     flux-mode and ES-mode amplitudes IN the published TotalCov.
    rho_cs = float((f_hat @ T @ e_hat)
                   / np.sqrt((f_hat @ T @ f_hat) * (e_hat @ T @ e_hat)))
    # (b) CONTAMINATED cross-check: isolate by subtraction. D mixes the cross
    #     term with unshipped independent sources -> not robust (rho can exceed 1).
    D = T - S - F - E
    wf2, vf2 = np.linalg.eigh(F)
    Vf = vf2[:, wf2 > 1e-9 * wf2.max()]
    u = (Vf @ Vf.T) @ (D @ e_hat)
    rho_sub = float(np.linalg.norm(u)
                    / np.sqrt((f_hat @ F @ f_hat) * (e_hat @ E @ e_hat)))
    print(f"[A] flux<->muon-E correlation:")
    print(f"      (a) Cauchy-Schwarz in published TotalCov : rho = {rho_cs:+.3f}  (defensible, <=1)")
    print(f"      (b) subtraction D=T-S-F-E (contaminated) : rho = {rho_sub:+.3f}  "
          f"({'UNPHYSICAL >1 -> ' if rho_sub>1 else ''}other sources couple to muon-E dir)")
    rho = min(rho_cs, 1.0)
    print(f"[A] -> use rho = {rho:+.3f} for the ours-only reconstruction "
          f"(faithful value needs the Bashyal fit posterior, JINST 16 P08068)")

    # ---- Route B: ours-only reconstruction ----
    fo = ROOT.TFile.Open(OURS)
    Csyst = th2np(fo.Get("hCov_universe_total"))
    F_ours = th2np(fo.Get("hCov_universe_full_Flux"))
    Emo = th2np(fo.Get("hCov_universe_full_Muon_Energy_MINOS"))
    Emi = th2np(fo.Get("hCov_universe_full_Muon_Energy_MINERvA"))
    fo.Close()
    E_ours = Emo + Emi
    assert Csyst.shape == (n, n), f"ours C^syst {Csyst.shape} != ({n},{n})"
    print(f"\n[B] loaded our C^syst {Csyst.shape}; Flux/Muon-E bands")

    d_f, lf = lead_mode(F_ours)
    d_e, le_ = lead_mode(E_ours)
    C_cross_ours = rho * (np.outer(d_f, d_e) + np.outer(d_e, d_f))
    print(f"[B] our flux mode |d_f|={np.linalg.norm(d_f):.3e}  "
          f"muon-E mode |d_e|={np.linalg.norm(d_e):.3e}  (rho={rho:+.3f} from route A)")

    def rank(C):
        return int(np.linalg.matrix_rank(C, tol=1e-12 * np.trace(C)))

    def cond(C):
        w = np.linalg.eigvalsh(C); w = w[w > 0]
        return w.max() / w.min() if w.size else np.inf

    Cnew = Csyst + C_cross_ours
    fdf = d_f / np.linalg.norm(d_f); ede = d_e / np.linalg.norm(d_e)

    def corr(C):
        return (fdf @ C @ ede) / np.sqrt((fdf @ C @ fdf) * (ede @ C @ ede))

    print(f"\n[B] effect of adding the rederived cross block to C^syst:")
    print(f"      rank     : {rank(Csyst)}  ->  {rank(Cnew)}  (of {n})  "
          f"[cross dirs already in range(C^syst): no new rank]")
    print(f"      cond     : {cond(Csyst):.2e}  ->  {cond(Cnew):.2e}")
    print(f"      corr(flux-mode, muon-E-mode) : {corr(Csyst):+.3f}  ->  {corr(Cnew):+.3f}  "
          f"(closure target rho={rho:+.3f})")
    print(f"      sqrt(trace C^syst)           : {np.sqrt(np.trace(Csyst)):.3e}  "
          f"-> {np.sqrt(np.trace(Cnew)):.3e}  (cross is ~traceless: {np.trace(C_cross_ours):+.1e})")

    # save the rederived ours-only cross block + augmented C^syst
    out = os.path.join(HERE, "flux_muonE_cross.root")
    fout = ROOT.TFile.Open(out, "RECREATE")
    def np2th(a, name, title):
        h = ROOT.TH2D(name, title, n, 0, n, n, 0, n)
        for i in range(n):
            for j in range(n):
                h.SetBinContent(i + 1, j + 1, a[i, j])
        h.Write(); return h
    np2th(C_cross_ours, "hCov_flux_muonE_cross",
          f"rederived flux<->muon-E cross cov (rho={rho:+.3f})")
    np2th(Cnew, "hCov_syst_with_cross", "C^syst + flux<->muon-E cross")
    ROOT.TParameter("double")("rho_flux_muonE", rho).Write()
    fout.Close()
    print(f"\n[out] wrote {out}: hCov_flux_muonE_cross, hCov_syst_with_cross, rho={rho:+.3f}")


if __name__ == "__main__":
    main()
