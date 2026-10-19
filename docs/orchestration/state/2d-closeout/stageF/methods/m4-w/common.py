"""Shared W-relation helpers for the M4 truth-W residual measurement (MeV units)."""
import numpy as np

M_N = 939.56536
M_P = 938.272013
M_BAR = (1.5 * M_N + M_P) / 2.5
M_MU = 105.6583          # MinervaUnits::M_mu (reco GetEmu)
W_FINE = np.array([0, 1.1, 1.4, 1.8, 2.2, 3.0, 100.0]) * 1000.0
W_J = np.array([0, 1.4, 2.2, 100.0]) * 1000.0


def struck_mass(tn):
    tn = np.asarray(tn)
    return np.where(tn == 2112, M_N, np.where(tn == 2212, M_P, M_BAR))


def w_cvu(M, enu, emu, theta):
    """CVUniverse::GetTrueExperimentersW: sqrt(M^2+2M(Enu-Emu)-4EnuEmu sin^2(th/2)), NaN if W^2<0."""
    w2 = M * M + 2.0 * M * (enu - emu) - 4.0 * enu * emu * np.sin(theta / 2.0) ** 2
    with np.errstate(invalid="ignore"):
        return np.sqrt(w2)


def w_pred(pt, pz, q3, M, mmu=M_MU):
    """W from (pT, p||, q3) assuming the neutrino is along the theta axis (all MeV)."""
    p2 = pt * pt + pz * pz
    disc = q3 * q3 - pt * pt
    with np.errstate(invalid="ignore"):
        enu = pz + np.sqrt(disc)
        emu = np.sqrt(p2 + mmu * mmu)
        theta = np.arctan2(pt, pz)
        return w_cvu(M, enu, emu, theta), disc, enu


def wbin(w, edges):
    return np.digitize(w, edges) - 1


def summarize(d, wt=None):
    """Quantiles of a residual array d (MeV); NaNs reported separately."""
    fin = np.isfinite(d)
    x = d[fin]
    if x.size == 0:
        return {"n": int(d.size), "n_finite": 0}
    q = np.quantile(x, [0.0005, 0.025, 0.16, 0.5, 0.84, 0.975, 0.9995])
    return {"n": int(d.size), "n_finite": int(x.size), "median": float(q[3]),
            "r68": [float(q[2]), float(q[4])], "r95": [float(q[1]), float(q[5])],
            "r99.9": [float(q[0]), float(q[6])], "max_abs": float(np.max(np.abs(x))),
            "mean": float(x.mean()), "rms": float(x.std())}
