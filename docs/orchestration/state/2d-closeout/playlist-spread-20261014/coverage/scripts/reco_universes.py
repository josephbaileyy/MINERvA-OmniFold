"""Q3 (reco level) and Q4: the proxy R under every systematic universe, per playlist; per-playlist consistency chi2.

Usage: python -I reco_universes.py <work_proxy.npz> <proxy_hists_meta.json> <dir with uni_<PL>.npz> <work_cov.npz> \
                                   <out.json> <out.txt> [dir with a second, disjoint sample uni_<PL>.npz]

Per playlist p and universe u (universe_reco_sample.py, a sample of mc_signal_reco and all of mc_background):
  rS_pu = S_u / S_CV and rB_pu = B_u / B_CV per proxy bin, on the same events.
  The universe yields are those ratios applied to the full May CV yields (proxy_hists.py), so the CV is exactly the
  prior look's.  R_pu = (D_p - k_p B_pu) / (k_p S_pu), k_p = POT_d / POT_mc.
Band covariances use MAT's CalcCovMx form: mean-centred, 1/N; Flux with the nu-e+IMD universe weights.

Q3 (reco): does any band move the pooled proxy, or the block-vs-1A-1E ratio, like the observed block shapes?
Q4: chi2 of the 12 per-playlist totals about their GLS mean, in y_p = ln R_p (a fractional systematic is then an
additive one, so the GLS mean has no Peelle's-pertinent-puzzle bias), with
  (i)   statistics only (data and MC);
  (ii)  + every band as an IDENTICAL fractional shift in all playlists (fully correlated): cancels by construction;
  (iii) + every band with its MEASURED per-playlist response (fully correlated universe by universe);
  (iv)  + every band uncorrelated across playlists (not physical; an upper bound on what the bands could absorb);
  (v)   + the detector bands only (Muon reconstruction group), uncorrelated across playlists;
  (vi)  + the detector bands only, fully correlated within each run period (1A-1E, 1F, 1G-1M, 1N-1P) and
        uncorrelated between periods.
"""
import json
import sys

import numpy as np
from scipy import stats

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import common as C  # noqa: E402

proxy_npz, meta_json, uni_dir, cov_npz, out_json, out_txt = sys.argv[1:7]
split_dir = sys.argv[7] if len(sys.argv) > 7 else None
P = np.load(proxy_npz)
META = json.load(open(meta_json))
wflux = np.load(cov_npz)["wflux"]
U = {p: np.load(f"{uni_dir}/uni_{p}.npz") for p in C.PLS}
lines = []
pr = lines.append
res = {"_inputs": {"work_proxy": C.file_record(proxy_npz), "meta": C.file_record(meta_json),
                   "work_cov": C.file_record(cov_npz),
                   "universe_samples": [C.file_record(f"{uni_dir}/uni_{p}.npz") for p in C.PLS],
                   "split_samples": ([C.file_record(f"{split_dir}/uni_{p}.npz") for p in ("1D", "1M", "1N")] if split_dir else [])}}

unis = [str(u) for u in U["1A"]["universes"]]
for p in C.PLS:
    assert [str(u) for u in U[p]["universes"]] == unis, p
band_of = {u: u.rsplit("_", 1)[0] for u in unis}
bands = sorted(set(band_of.values()))
members = {b: sorted((u for u in unis if band_of[u] == b), key=lambda s: int(s.rsplit("_", 1)[1])) for b in bands}
assert len(members["Flux"]) == 100

# controls: universe-file CV against the May CV inputs
ctl = {}
for p in C.PLS:
    Dm, Bm = P[f"{p}__proxy__D"], P[f"{p}__proxy__B"]
    ctl[p] = {"data_entries_universe_file_in_grid": float(U[p]["D"].sum()), "data_entries_may_in_grid": float(Dm.sum()),
              "bkg_cv_universe_file": float(U[p]["B__CV"].sum()), "bkg_cv_may": float(Bm.sum()),
              "pot_data_universe_file": float(U[p]["pot_data"]), "pot_data_may": META[p]["pot_data"],
              "pot_mc_universe_file": float(U[p]["pot_mc"]), "pot_mc_may": META[p]["pot_mc"],
              "sig_entries_used": int(U[p]["n_sig_entries_used"]), "sig_entries_total": int(U[p]["n_sig_entries_total"]),
              "sig_pass_used": int(U[p]["n_sig_pass_used"]), "sig_pass_may_total": META[p]["n_sig_pass"],
              "sample_S_cv_over_may_S_total": float(U[p]["S__CV"].sum() / P[f"{p}__proxy__S"].sum())}
res["controls_universe_file_vs_may"] = ctl


def ratio_safe(a, b):
    with np.errstate(divide="ignore", invalid="ignore"):
        r = a / b
    return np.where(np.isfinite(r) & (b > 0), r, 1.0)


k = {p: META[p]["pot_data"] / META[p]["pot_mc"] for p in C.PLS}
Dp = {p: P[f"{p}__proxy__D"] for p in C.PLS}
Sp = {p: P[f"{p}__proxy__S"] for p in C.PLS}
Bp = {p: P[f"{p}__proxy__B"] for p in C.PLS}
S2p = {p: P[f"{p}__proxy__S2"] for p in C.PLS}
B2p = {p: P[f"{p}__proxy__B2"] for p in C.PLS}


def yields(p, u):
    if u == "CV":
        return Dp[p], k[p] * Sp[p], k[p] * Bp[p]
    rs = ratio_safe(U[p][f"S__{u}"], U[p]["S__CV"])
    rb = ratio_safe(U[p][f"B__{u}"], U[p]["B__CV"])
    return Dp[p], k[p] * Sp[p] * rs, k[p] * Bp[p] * rb


Y = {(p, u): yields(p, u) for p in C.PLS for u in ["CV"] + unis}


def Rgrp(pls, u, ax):
    D = sum(Y[(p, u)][0] for p in pls)
    S = sum(Y[(p, u)][1] for p in pls)
    B = sum(Y[(p, u)][2] for p in pls)
    if ax == "tot":
        return (D.sum() - B.sum()) / S.sum()
    if ax == "lohi":
        e = C.PZ_P
        lo = (e[:-1] >= C.STEP_LO[0]) & (e[1:] <= C.STEP_LO[1])
        hi = (e[:-1] >= C.STEP_HI[0]) & (e[1:] <= C.STEP_HI[1])
        f = lambda m: (D.sum(0)[m].sum() - B.sum(0)[m].sum()) / S.sum(0)[m].sum()
        return np.array([f(lo), f(hi)])
    return (D.sum(ax) - B.sum(ax)) / S.sum(ax)


def stats_of(pls_num, pls_den, u):
    """total, step, pz marginal of R(num)/R(den) (den None: R(num) itself)."""
    if pls_den is None:
        t, lh, pz = Rgrp(pls_num, u, "tot"), Rgrp(pls_num, u, "lohi"), Rgrp(pls_num, u, 0)
    else:
        t = Rgrp(pls_num, u, "tot") / Rgrp(pls_den, u, "tot")
        lh = Rgrp(pls_num, u, "lohi") / Rgrp(pls_den, u, "lohi")
        pz = Rgrp(pls_num, u, 0) / Rgrp(pls_den, u, 0)
    return t, lh[1] / lh[0], pz


targets = {"pooled": (C.PLS, None), "1G-1M_vs_1A-1E": (C.BLOCKS["1G-1M"], C.REF),
           "1N-1P_vs_1A-1E": (C.BLOCKS["1N-1P"], C.REF)}
cv = {t: stats_of(a, b, "CV") for t, (a, b) in targets.items()}
res["observed"] = {t: {"total": float(v[0]), "step_ratio": float(v[1]), "pz": np.round(v[2], 5).tolist()} for t, v in cv.items()}
shift = {}
for t, (a, b) in targets.items():
    for u in unis:
        tt, st, pz = stats_of(a, b, u)
        shift[(t, u)] = (tt / cv[t][0] - 1, st / cv[t][1] - 1, pz / cv[t][2] - 1)


def band_sd(vals, b):
    w = wflux if b == "Flux" else np.ones(len(vals))
    vals = np.asarray(vals)
    mu = np.sum(w * vals.T, axis=-1) / w.sum() if vals.ndim > 1 else np.sum(w * vals) / w.sum()
    return np.sqrt(np.sum(w * ((vals - mu) ** 2).T, axis=-1) / w.sum()) if vals.ndim > 1 else float(np.sqrt(np.sum(w * (vals - mu) ** 2) / w.sum()))


res["Q3_reco"] = {}
for t in targets:
    res["Q3_reco"][t] = {}
    for b in bands:
        tot = [shift[(t, u)][0] for u in members[b]]
        stp = [shift[(t, u)][1] for u in members[b]]
        pzs = np.array([shift[(t, u)][2] for u in members[b]])
        res["Q3_reco"][t][b] = {"n": len(members[b]), "total_sd": band_sd(tot, b), "total_min": float(min(tot)),
                                "total_max": float(max(tot)), "step_sd": band_sd(stp, b), "step_min": float(min(stp)),
                                "step_max": float(max(stp)), "pz_sd": np.round(band_sd(pzs, b), 6).tolist()}
obs = {"1G-1M": (cv["1G-1M_vs_1A-1E"][0] - 1, cv["1G-1M_vs_1A-1E"][1] - 1),
       "1N-1P": (cv["1N-1P_vs_1A-1E"][0] - 1, cv["1N-1P_vs_1A-1E"][1] - 1)}
pr("Q3 (reco level, per-playlist universe files, sample). Observed block ratios against 1A-1E:")
for g, (t, s) in obs.items():
    pr(f"  {g}: total {100 * t:+.2f} %, step r[8,15)/r[1.5,8) - 1 = {100 * s:+.2f} %")
pr("  band (N)               | pooled proxy: total sd, min..max; step sd, min..max | 1G-1M/1A-1E ratio: total sd; step sd, min..max"
   " | 1N-1P/1A-1E ratio: total sd, min..max; step sd   [%]")
rk = sorted(bands, key=lambda b: -(res["Q3_reco"]["pooled"][b]["total_sd"] + res["Q3_reco"]["pooled"][b]["step_sd"]))
for b in rk:
    a, g1, g2 = (res["Q3_reco"][t][b] for t in targets)
    if a["total_sd"] < 1e-6 and a["step_sd"] < 1e-6 and g1["total_sd"] < 1e-6 and g2["total_sd"] < 1e-6:
        continue
    pr(f"  {b:22s}({a['n']:3d}) | {100 * a['total_sd']:5.2f}, {100 * a['total_min']:+6.2f}..{100 * a['total_max']:+6.2f}; "
       f"{100 * a['step_sd']:5.2f}, {100 * a['step_min']:+6.2f}..{100 * a['step_max']:+6.2f}"
       f" | {100 * g1['total_sd']:5.2f}; {100 * g1['step_sd']:5.2f}, {100 * g1['step_min']:+6.2f}..{100 * g1['step_max']:+6.2f}"
       f" | {100 * g2['total_sd']:5.2f}, {100 * g2['total_min']:+6.2f}..{100 * g2['total_max']:+6.2f}; {100 * g2['step_sd']:5.2f}")
for t in ("1G-1M_vs_1A-1E", "1N-1P_vs_1A-1E"):
    tot_sd = np.sqrt(sum(res["Q3_reco"][t][b]["total_sd"] ** 2 for b in bands))
    stp_sd = np.sqrt(sum(res["Q3_reco"][t][b]["step_sd"] ** 2 for b in bands))
    res["Q3_reco"][t]["_all_bands_quadrature"] = {"total_sd": float(tot_sd), "step_sd": float(stp_sd)}
    pr(f"  all bands in quadrature, {t}: total sd {100 * tot_sd:.3f} %, step sd {100 * stp_sd:.3f} %")
pr("  pooled proxy p_|| marginal at the two universes of selected bands [%] (proxy p_|| bins "
   + " ".join(f"{a:g}-{b:g}" for a, b in zip(C.PZ_P[:-1], C.PZ_P[1:])) + "):")
for b in ("MinosEfficiency", "Muon_Energy_MINOS", "Muon_Energy_MINERvA"):
    for u in members[b]:
        pr(f"   {u:22s} " + " ".join(f"{100 * v:+6.2f}" for v in shift[('pooled', u)][2]))
# shape-only match on the proxy p_|| marginal: block (q_pz - 1, data-weighted mean removed) against each band's
# pooled universe shifts (mean removed). For a band: least-squares fit in the span of its leading modes (99 % of the
# trace of the weighted covariance); report the residual fraction and the fit's length in band sigma.
Dref_pz = sum(Dp[p] for p in C.PLS).sum(0)
def demean(v):
    return v - np.average(v, weights=Dref_pz)
res["Q3_reco_pz_shape_match"] = {}
for g in ("1G-1M", "1N-1P"):
    fz = demean(cv[f"{g}_vs_1A-1E"][2] - 1)
    out = {}
    for b in bands:
        X = np.stack([demean(shift[("pooled", u)][2]) for u in members[b]])
        w = wflux if b == "Flux" else None
        Cz = C.wcov(X, w)
        lam, V = np.linalg.eigh(0.5 * (Cz + Cz.T))
        lam, V = np.maximum(lam[::-1], 0), V[:, ::-1]
        if lam.sum() <= 1e-14:
            continue
        kk = int(np.searchsorted(np.cumsum(lam) / lam.sum(), 0.99) + 1)
        pj = V[:, :kk].T @ fz
        out[b] = {"modes": kk, "resid_frac": float(np.sum((fz - V[:, :kk] @ pj) ** 2) / np.sum(fz ** 2)),
                  "sigma_needed": float(np.sqrt(np.sum(pj ** 2 / lam[:kk]))),
                  "band_shape_rms": float(np.sqrt(lam.sum() / len(fz)))}
    res["Q3_reco_pz_shape_match"][g] = {"block_shape_rms": float(np.sqrt(np.mean(fz ** 2))),
                                        "bands": dict(sorted(out.items(), key=lambda kv: kv[1]["resid_frac"]))}
    best = list(res["Q3_reco_pz_shape_match"][g]["bands"].items())[:6]
    pr(f"  p_|| SHAPE match (pooled universes vs undiluted {g}, means removed; block shape rms "
       f"{100 * res['Q3_reco_pz_shape_match'][g]['block_shape_rms']:.2f} %): " +
       "; ".join(f"{b} resid {v['resid_frac']:.2f} at {v['sigma_needed']:.1f} sigma (k={v['modes']}, band shape rms "
                 f"{100 * v['band_shape_rms']:.2f} %)" for b, v in best))
fl = np.array([shift[("pooled", u)][1] for u in members["Flux"]])
pr(f"  Flux universes, pooled step: weighted sd {100 * band_sd(fl, 'Flux'):.2f} %, max |step| {100 * np.abs(fl).max():.2f} %;"
   f" 1G-1M/1A-1E step: max |.| {100 * max(abs(shift[('1G-1M_vs_1A-1E', u)][1]) for u in members['Flux']):.3f} %")
pr("")

# ------------------------------------------------------------------ Q4
Rp = np.array([Rgrp([p], "CV", "tot") for p in C.PLS])
Dt = np.array([Dp[p].sum() for p in C.PLS])
St = np.array([k[p] * Sp[p].sum() for p in C.PLS])
S2t = np.array([k[p] ** 2 * S2p[p].sum() for p in C.PLS])
B2t = np.array([k[p] ** 2 * B2p[p].sum() for p in C.PLS])
var_d = Dt / St ** 2
var_mc = (Rp ** 2 * S2t + B2t) / St ** 2
Cstat = np.diag((var_d + var_mc) / Rp ** 2)          # of y = ln R
Y_ = np.log(Rp)
Dl = {u: np.log(np.array([Rgrp([p], u, "tot") for p in C.PLS]) / Rp) for u in unis}
Csys_meas = np.zeros((12, 12))
Csys_pd = np.zeros((12, 12))
Csys_ident = np.zeros((12, 12))
per_band_meas, per_band_pd = {}, {}
pot = np.array([META[p]["pot_data"] for p in C.PLS])
for b in bands:
    X = np.stack([Dl[u] for u in members[b]])
    w = wflux if b == "Flux" else None
    Cb = C.wcov(X, w)
    per_band_meas[b] = Cb
    Csys_meas += Cb
    # playlist-dependent part: each universe's response minus its data-POT-weighted mean over playlists. A common
    # part is degenerate with the fitted mean and drops out of the chi2; this is the same chi2, better conditioned.
    xm = (X * pot).sum(1) / pot.sum()
    per_band_pd[b] = C.wcov(X - xm[:, None], w)
    Csys_pd += per_band_pd[b]
    # identical fractional shift: the data-POT-weighted mean response, the same in every playlist
    vb = float(C.wcov(xm[:, None], w)[0, 0])
    Csys_ident += vb * np.ones((12, 12))
Cnorm = np.log(1.014) ** 2 * np.ones((12, 12))
DET = [b for b in bands if C.category_for_band(b) == "Muon reconstruction"]
Cdet = sum(per_band_meas[b] for b in DET)
period = np.array([0, 0, 0, 0, 0, 1, 2, 2, 2, 3, 3, 3])
Cdet_period = np.where(period[:, None] == period[None, :], Cdet, 0.0)


def gls_chi2(Cm):
    Ci = np.linalg.inv(Cm)
    one = np.ones(12)
    mu = float(one @ Ci @ Y_ / (one @ Ci @ one))
    r = Y_ - mu
    c2 = float(r @ Ci @ r)
    return c2, mu, float(stats.chi2.sf(c2, 11)), (r / np.sqrt(np.diag(Cm))).round(2).tolist()


Q4 = {}
for name, Cm in (("i_stat_only", Cstat),
                 ("ii_stat_plus_identical_correlated_bands_plus_norm", Cstat + Csys_ident + Cnorm),
                 ("iii_stat_plus_measured_per_playlist_response", Cstat + Csys_pd),
                 ("iii_same_with_full_response_incl_common_part", Cstat + Csys_meas + Cnorm),
                 ("iii_without_flux", Cstat + Csys_pd - per_band_pd["Flux"]),
                 ("iv_bands_uncorrelated_across_playlists_upper_bound", Cstat + np.diag(np.diag(Csys_meas)) + np.diag(np.diag(Cnorm))),
                 ("v_detector_bands_uncorrelated_across_playlists", Cstat + np.diag(np.diag(Cdet))),
                 ("vi_detector_bands_correlated_within_run_period_only", Cstat + Cdet_period)):
    c2, mu, pv, pulls = gls_chi2(Cm)
    Q4[name] = {"chi2": c2, "ndf": 11, "p_value": pv, "gls_mean_R": float(np.exp(mu)), "pulls": pulls}
res["Q4"] = {"playlists": C.PLS, "R_p": Rp.round(6).tolist(), "R_p_rel_1A-1D_mean": (Rp / Rp[:4].mean()).round(5).tolist(),
             "stat_err_data_rel": (np.sqrt(var_d) / Rp).round(6).tolist(), "stat_err_mc_rel": (np.sqrt(var_mc) / Rp).round(6).tolist(),
             "sys_measured_rel_sd_per_playlist": np.sqrt(np.diag(Csys_meas)).round(6).tolist(),
             "sys_measured_corr_matrix": (Csys_meas / np.sqrt(np.outer(np.diag(Csys_meas), np.diag(Csys_meas)))).round(4).tolist(),
             "chi2": Q4}
# which bands carry the playlist-dependent part: chi2 change when each band's measured response is added alone
alone = {}
c0 = gls_chi2(Cstat)[0]
for b in bands:
    if np.abs(per_band_meas[b]).max() == 0:
        continue
    alone[b] = gls_chi2(Cstat + per_band_pd[b])[0] - c0
res["Q4"]["detector_bands"] = DET
res["Q4"]["detector_bands_sd_per_playlist"] = np.sqrt(np.diag(Cdet)).round(6).tolist()
res["Q4"]["chi2_change_adding_one_band"] = dict(sorted(alone.items(), key=lambda kv: kv[1])[:12])
# the playlist-dependent residual of each band: sd across playlists of (Delta_p,u - pot-mean Delta_u), band-level
pd_sd = {}
pot = np.array([META[p]["pot_data"] for p in C.PLS])
for b in bands:
    X = np.stack([Dl[u] for u in members[b]])
    Xr = X - ((X * pot).sum(1) / pot.sum())[:, None]
    w = wflux if b == "Flux" else np.ones(len(X))
    v = (w[:, None] * Xr ** 2).sum(0) / w.sum()
    pd_sd[b] = float(np.sqrt(np.average(v, weights=pot)))
res["Q4"]["playlist_dependent_part_rms_by_band"] = dict(sorted(pd_sd.items(), key=lambda kv: -kv[1])[:10])
res["Q4"]["playlist_dependent_part_rms_all_bands_quadrature"] = float(np.sqrt(sum(v ** 2 for v in pd_sd.values())))
res["Q4"]["observed_rms_of_ln_R_about_pot_weighted_mean"] = float(np.sqrt(np.average((Y_ - np.average(Y_, weights=pot)) ** 2, weights=pot)))

pr("Q4. Per-playlist consistency of the proxy total R_p (proxy grid; May CV; per-playlist POT)")
pr("   PL    R_p     rel(1A-1D)  data stat  MC stat   sys sd (measured, per playlist)  [rel]")
for i, p in enumerate(C.PLS):
    pr(f"   {p}  {Rp[i]:.5f}  {Rp[i] / Rp[:4].mean():.5f}    {np.sqrt(var_d[i]) / Rp[i]:.5f}   {np.sqrt(var_mc[i]) / Rp[i]:.5f}"
       f"   {np.sqrt(Csys_meas[i, i]):.5f}")
for name, q in Q4.items():
    pr(f"  {name:52s} chi2 = {q['chi2']:9.2f} / 11   p = {q['p_value']:.2e}   GLS mean R = {q['gls_mean_R']:.5f}")
pr("  chi2 change when ONE band's measured per-playlist response is added to stat (most negative first): " +
   ", ".join(f"{b} {v:+.1f}" for b, v in res["Q4"]["chi2_change_adding_one_band"].items()))
pr(f"  playlist-dependent part, all bands in quadrature: {100 * res['Q4']['playlist_dependent_part_rms_all_bands_quadrature']:.3f} %;"
   f" observed POT-weighted rms of ln R_p: {100 * res['Q4']['observed_rms_of_ln_R_about_pot_weighted_mean']:.2f} %")
pr("  note: the GLS mean is meaningful only for i, ii and iv; with a common-mode band the fitted mean trades off "
   "against that band's pull")
pr("  playlist-dependent part of each band, POT-weighted rms over playlists [rel]: " +
   ", ".join(f"{b} {v:.5f}" for b, v in res["Q4"]["playlist_dependent_part_rms_by_band"].items()))
pr("  sample controls (universe file vs May CV): " + "; ".join(
    f"{p} D {v['data_entries_universe_file_in_grid']:.0f}/{v['data_entries_may_in_grid']:.0f} "
    f"B {v['bkg_cv_universe_file']:.1f}/{v['bkg_cv_may']:.1f} sigpass {v['sig_pass_used']}/{v['sig_pass_may_total']}"
    for p, v in ctl.items()))

if split_dir:
    res["split_sample_check"] = {}
    for p in ("1D", "1M", "1N"):
        U2 = np.load(f"{split_dir}/uni_{p}.npz")
        def tot_shift(Uz, u):
            rs = ratio_safe(Uz[f"S__{u}"], Uz["S__CV"])
            rb = ratio_safe(Uz[f"B__{u}"], Uz["B__CV"])
            Dd, Ss, Bb = Dp[p], k[p] * Sp[p] * rs, k[p] * Bp[p] * rb
            return np.log(((Dd.sum() - Bb.sum()) / Ss.sum()) / Rp[C.PLS.index(p)])
        out = {}
        for b in bands:
            d1 = np.array([tot_shift(U[p], u) for u in members[b]])
            d2 = np.array([tot_shift(U2, u) for u in members[b]])
            w = wflux if b == "Flux" else np.ones(len(d1))
            out[b] = {"band_sd_first": float(np.sqrt(C.wcov(d1[:, None], w)[0, 0])),
                      "band_sd_second": float(np.sqrt(C.wcov(d2[:, None], w)[0, 0])),
                      "rms_diff": float(np.sqrt(np.sum(w * (d1 - d2) ** 2) / w.sum()))}
        res["split_sample_check"][p] = {"first_entry_second_sample": int(U2["first_entry"]), "bands":
                                        dict(sorted(out.items(), key=lambda kv: -kv[1]["rms_diff"])[:8])}
        pr(f"  split-sample check {p} (entries 0-500k vs 500k-1M), largest rms difference of the per-universe total shift: " +
           ", ".join(f"{b} {100 * v['rms_diff']:.3f} % (band sd {100 * v['band_sd_first']:.2f}/{100 * v['band_sd_second']:.2f} %)"
                     for b, v in list(res['split_sample_check'][p]['bands'].items())[:4]))
json.dump(res, open(out_json, "w"), indent=1)
open(out_txt, "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
