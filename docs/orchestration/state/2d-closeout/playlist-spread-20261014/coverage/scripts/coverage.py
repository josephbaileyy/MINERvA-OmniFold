"""Q1-Q3(unfolded): bands of the quoted 2D covariance (VL175), and the playlist-spread shifts against them.

Usage: python -I coverage.py <work_cov.npz> <work_proxy.npz> <proxy_hists_meta.json> <prior outputs dir> \
                             <fig67 EU_repaired_summary.txt> <out.json> <out.txt>

work_cov.npz   : export_cov.py  (VL175 blocks, ML, E_U, the 187 unfolded universe outputs, Flux weights)
work_proxy.npz : proxy_hists.py (per-playlist D, S, B on the proxy and analysis grids, May CV inputs)
prior outputs  : ../outputs/{ref_shape,mix_bias}.json of the 2026-10-14 playlist-spread look

Bias vectors (fractional, on the 205 reported cells; absolute = fraction x E_U):
  J36   : the production-mix / per-playlist-mix IBU ratio - 1 on the triage TRUTH grid (mix_bias.json 'ibu').
  block : s_B(cell) * (q_B(cell) - 1), the shift of the combined proxy if block B alone is off by q_B against 1A-1E
          and every other playlist is right. s_B = the block's share of the per-playlist-mix MC signal in that
          proxy cell (k-scaled S). The data-POT share is the cruder 'about' version and is also reported.
  ref   : q_all(cell) - 1, the full data set against the 1A-1E reference (prior REPORT section 1.3).
Each q is mapped from the proxy grid to the analysis cells in two ways:
  sep : q_pT(jpt) * q_pz(jpz) / q_tot (separable; uses only the well-measured marginals);
  bin : q(jpt, jpz) where both block and reference have >= 50 data events, else sep;
  interp : as sep, but each marginal is linearly interpolated between proxy-bin centres (a smoothed step).
Both are reco-level ratios placed on true-variable cells: migration is ignored (approximation).
"""
import json
import sys

import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import common as C  # noqa: E402

cov_npz, proxy_npz, meta_json, prior_dir, fig67_txt, out_json, out_txt = sys.argv[1:8]
W = np.load(cov_npz)
P = np.load(proxy_npz)
META = json.load(open(meta_json))
REFSHAPE = json.load(open(f"{prior_dir}/ref_shape.json"))
MIX = json.load(open(f"{prior_dir}/mix_bias.json"))

cells = W["cells"]
x = W["EU"].ravel(order="C")[cells]
A = C.area(cells)
Ppt, Ppz = C.proj_matrix("pt", cells), C.proj_matrix("pz", cells)
cpt, cpz = Ppt @ x, Ppz @ x
jpt, jpz = C.proxy_index_of_cells(cells)
res = {"_inputs": {"work_cov": C.file_record(cov_npz), "work_proxy": C.file_record(proxy_npz),
                   "meta": C.file_record(meta_json), "ref_shape": C.file_record(f"{prior_dir}/ref_shape.json"),
                   "mix_bias": C.file_record(f"{prior_dir}/mix_bias.json"), "fig67_summary": C.file_record(fig67_txt)},
       "_grid": {"pt_edges": C.PT_A.tolist(), "pz_edges": C.PZ_A.tolist(), "cells_flat_index": cells.tolist(),
                 "note": "cells: C-order flat index ipt*16+ipz of the 14x16 grid; 205 reported"}}
lines = []
pr = lines.append

# ------------------------------------------------------------------ Q1: the covariance and its bands
bands = sorted(k[len("cov__hCov_universe_"):] for k in W.files
               if k.startswith("cov__hCov_universe_") and k != "cov__hCov_universe_total")
Cb = {b: W[f"cov__hCov_universe_{b}"] for b in bands}
C_univ = W["cov__hCov_universe_total"]
C_comb = W["cov__hCov_combined"]
C_ml = W["cov__ML"]
C_boot = C_comb - C_univ
C_tot = C_comb + C_ml
acc = np.zeros_like(C_univ)
for b in bands:
    acc += Cb[b]
res["Q1_controls"] = {"sum_of_bands_vs_universe_total_rel_maxdiff": float(np.abs(acc - C_univ).max() / np.abs(C_univ).max()),
                      "n_bands_incl_normalization": len(bands)}
G = {g: np.zeros_like(C_univ) for g in C.GROUPS}
for b in bands:
    G[C.category_for_band(b)] += Cb[b]
G["Statistical"] = C_boot
G["ML"] = C_ml
G["Total"] = C_tot


def frac_cell(Cm):
    return np.sqrt(np.maximum(np.diag(Cm), 0)) / x


def frac_marg(Cm, Pm, c):
    return np.sqrt(np.maximum(np.diag(Pm @ Cm @ Pm.T), 0)) / c


def frac_int(Cm):
    return float(np.sqrt(A @ Cm @ A) / (A @ x))


def summary(Cm):
    fc = frac_cell(Cm)
    return {"cell_median_pct": 100 * float(np.median(fc)), "cell_max_pct": 100 * float(fc.max()),
            "cell_min_pct": 100 * float(fc.min()), "integral_pct": 100 * frac_int(Cm),
            "pz_marginal_pct": (100 * frac_marg(Cm, Ppz, cpz)).round(4).tolist(),
            "pt_marginal_pct": (100 * frac_marg(Cm, Ppt, cpt)).round(4).tolist(),
            "cell_pct": (100 * fc).round(4).tolist()}


res["Q1_groups"] = {g: summary(Cm) for g, Cm in G.items()}
res["Q1_bands"] = {b: summary(Cm) for b, Cm in Cb.items()}
# control against the committed Fig. 6/7 summary (E_U, repaired)
fig = {}
axis = None
for ln in open(fig67_txt):
    t = ln.strip()
    if t.endswith("projection:"):
        axis = t.split()[0]
    elif axis and "median=" in t:
        name = t.split("median=")[0].strip()
        fig[(axis, name)] = float(t.split("median=")[1].split("%")[0])
ctl = {}
for (ax, name), v in fig.items():
    if name in G:
        m = float(np.median(res["Q1_groups"][name][f"{ax}_marginal_pct"]))
        ctl[f"{ax}:{name}"] = {"committed_median_pct": v, "this_median_pct": round(m, 4), "ok": abs(m - v) < 6e-4}
res["Q1_controls"]["fig67_EU_repaired_medians"] = ctl

pr("Q1. Quoted 2D covariance VL175 (repaired rollup + VL170 bootstrap + ML), central E_U, 205 cells")
pr(f"  control: sum of 45 band blocks = hCov_universe_total, rel max diff {res['Q1_controls']['sum_of_bands_vs_universe_total_rel_maxdiff']:.1e}")
pr("  control: marginal medians vs committed fig67/EU_repaired_summary.txt: " +
   ", ".join(f"{k} {v['this_median_pct']:.3f}/{v['committed_median_pct']:.3f} {'ok' if v['ok'] else 'MISMATCH'}"
             for k, v in ctl.items()))
pr("")
pr("  group / band            cell median  cell max   integral   pz-marg median (min-max)   pT-marg median (min-max)   [%]")
show = list(G) + ["full_Flux", "full_MinosEfficiency", "full_Muon_Energy_MINOS", "full_Muon_Energy_MINERvA",
                  "full_MuonResolution", "full_BeamAngleX", "full_BeamAngleY", "__Normalization_flat"]
for name in show:
    s = res["Q1_groups"].get(name) or res["Q1_bands"][name]
    pz, pt = np.array(s["pz_marginal_pct"]), np.array(s["pt_marginal_pct"])
    pr(f"  {name:24s} {s['cell_median_pct']:8.3f} {s['cell_max_pct']:9.3f} {s['integral_pct']:9.3f}"
       f"     {np.median(pz):6.3f} ({pz.min():.3f}-{pz.max():.3f})        {np.median(pt):6.3f} ({pt.min():.3f}-{pt.max():.3f})")
pr("")
pr("  p_|| marginal, fractional sigma per bin [%] (Total, Flux, Muon reco, Normalization, Stat)")
pr("   pz bin [GeV/c]   " + "  ".join(f"{a:g}-{b:g}" for a, b in zip(C.PZ_A[:-1], C.PZ_A[1:])))
for g in ("Total", "Flux", "Muon reconstruction", "Normalization", "Statistical", "Models", "Hadronic response"):
    pr(f"   {g:18s}" + " ".join(f"{v:6.2f}" for v in res["Q1_groups"][g]["pz_marginal_pct"]))
pr("  p_T marginal, fractional sigma per bin [%]")
pr("   pT bin [GeV/c]   " + "  ".join(f"{a:g}-{b:g}" for a, b in zip(C.PT_A[:-1], C.PT_A[1:])))
for g in ("Total", "Flux", "Muon reconstruction", "Normalization", "Statistical", "Models", "Hadronic response"):
    pr(f"   {g:18s}" + " ".join(f"{v:6.2f}" for v in res["Q1_groups"][g]["pt_marginal_pct"]))
pr("")
pr("  per-cell fractional sigma [%] on the 14 x 16 grid (rows p_T, columns p_||; '.' = not reported)")
for g in ("Total", "Flux", "Muon reconstruction", "Statistical"):
    full = np.full(C.NPT * C.NPZ, np.nan)
    full[cells] = res["Q1_groups"][g]["cell_pct"]
    pr(f"   {g}")
    pr("    pT \\ pz  " + " ".join(f"{a:>5g}" for a in C.PZ_A[:-1]))
    for i in range(C.NPT):
        row = full[i * C.NPZ:(i + 1) * C.NPZ]
        pr(f"    {C.PT_A[i]:>5g}    " + " ".join("    ." if not np.isfinite(v) else f"{v:5.1f}" for v in row))
pr("")

# ------------------------------------------------------------------ Q2: shifts mapped to the analysis cells
Q = {g: C.block_q(P, META, pls) for g, pls in C.BLOCKS.items()}
# control: reproduce the prior ref_shape.json marginals
rs_ok = {}
for g in ("1G-1M", "1N-1P", "all"):
    prior = REFSHAPE[f"{g}_vs_1A-1E"]
    rs_ok[g] = {"pz_maxdiff": float(np.abs(np.array(prior["by_pz"]) - Q[g]["pz"]).max()),
                "pt_maxdiff": float(np.abs(np.array(prior["by_pt"]) - Q[g]["pt"]).max()),
                "tot_diff": float(abs(prior["total"] - Q[g]["tot"]))}
res["Q2_control_ref_shape_reproduced"] = rs_ok


IPT, IPZ = C.cell_ipt_ipz(cells)
CPT_A = 0.5 * (C.PT_A[IPT] + C.PT_A[IPT + 1])
CPZ_A = 0.5 * (C.PZ_A[IPZ] + C.PZ_A[IPZ + 1])
CPT_P = 0.5 * (C.PT_P[:-1] + C.PT_P[1:])
CPZ_P = 0.5 * (C.PZ_P[:-1] + C.PZ_P[1:])


def map_q(q, mode):
    sep = q["pt"][jpt] * q["pz"][jpz] / q["tot"]
    if mode == "sep":
        return sep
    if mode == "interp":
        return np.interp(CPT_A, CPT_P, q["pt"]) * np.interp(CPZ_A, CPZ_P, q["pz"]) / q["tot"]
    b = q["bin"][jpt, jpz]
    ok = q["ok"][jpt, jpz] & np.isfinite(b)
    return np.where(ok, b, sep)


def map_q_err(q):
    return q["bin_err"][jpt, jpz]


pot_share = {g: sum(META[p]["pot_data"] for p in pls) / sum(META[p]["pot_data"] for p in C.PLS)
             for g, pls in C.BLOCKS.items()}
res["Q2_pot_share"] = pot_share
s_cell = {g: Q[g]["S_share"][jpt, jpz] for g in C.BLOCKS}

# J36 (IBU, truth grid)
j36_bin = np.array(MIX["ibu"]["bin_bias_10x10_pt_rows"], float)
j36_pt = np.array(MIX["ibu"]["pt_marginal_bias"], float)
j36_pz = np.array(MIX["ibu"]["pz_marginal_bias"], float)
f_j36_bin = j36_bin[jpt, jpz]
f_j36_sep = (1 + j36_pt[jpt]) * (1 + j36_pz[jpz]) / (1 + MIX["ibu"]["total_bias"]) - 1
n_nan = int((~np.isfinite(f_j36_bin)).sum())
f_j36_bin = np.where(np.isfinite(f_j36_bin), f_j36_bin, f_j36_sep)

F = {"J36_ibu_bin": f_j36_bin, "J36_ibu_sep": f_j36_sep}
for g in ("1G-1M", "1N-1P"):
    for mode in ("sep", "bin", "interp"):
        F[f"block_{g}_{mode}_Sshare"] = s_cell[g] * (map_q(Q[g], mode) - 1)
    F[f"block_{g}_sep_POTshare"] = pot_share[g] * (map_q(Q[g], "sep") - 1)
for mode in ("sep", "bin", "interp"):
    F[f"ref_all_vs_1A-1E_{mode}"] = map_q(Q["all"], mode) - 1
# the undiluted block shapes (what one block alone looks like), for Q3
SH = {f"shape_{g}_{m}": map_q(Q[g], m) - 1 for g in ("1G-1M", "1N-1P") for m in ("sep", "bin")}
res["Q2_J36_cells_without_truth_grid_value"] = n_nan

REL = {"Total": G["Total"], "Flux": G["Flux"], "Muon reconstruction": G["Muon reconstruction"],
       "Normalization": G["Normalization"], "full_MinosEfficiency": Cb["full_MinosEfficiency"],
       "full_Muon_Energy_MINOS": Cb["full_Muon_Energy_MINOS"]}


def assess(f):
    b = f * x
    o = {"cell_shift_pct": {"median": 100 * float(np.median(f)), "min": 100 * float(f.min()), "max": 100 * float(f.max())},
         "integral_shift_pct": 100 * float(A @ b / (A @ x))}
    mz, mt = Ppz @ b / cpz, Ppt @ b / cpt
    o["pz_marginal_shift_pct"] = (100 * mz).round(4).tolist()
    o["pt_marginal_shift_pct"] = (100 * mt).round(4).tolist()
    o["vs"] = {}
    for name, Cm in REL.items():
        z = np.abs(f) / frac_cell(Cm)
        zz = np.abs(mz) / frac_marg(Cm, Ppz, cpz)
        zt = np.abs(mt) / frac_marg(Cm, Ppt, cpt)
        d = {"cell_z_median": float(np.median(z)), "cell_z_max": float(z.max()), "n_cells_z_gt_1": int((z > 1).sum()),
             "pz_marg_z_max": float(zz.max()), "pt_marg_z_max": float(zt.max()),
             "integral_z": float(abs(A @ b) / np.sqrt(A @ Cm @ A))}
        if name == "Total":
            chi2, nk, cond = C.mahalanobis2(b, Cm)
            d["chi2_205_pinv"] = chi2
            d["chi2_205_kept_modes"] = nk
            d["chi2_205_cond"] = cond
            for ax, Pm in (("pz", Ppz), ("pt", Ppt)):
                c2, nk2, cond2 = C.mahalanobis2(Pm @ b, Pm @ Cm @ Pm.T)
                d[f"chi2_{ax}_marginal"] = c2
                d[f"chi2_{ax}_marginal_ndim"] = nk2
                d[f"chi2_{ax}_marginal_cond"] = cond2
        o["vs"][name] = d
    return o


res["Q2"] = {k: assess(f) for k, f in F.items()}
# noise floor: data-stat noise of the 'bin' mapping alone, expected chi2 under C_tot
for g, key in (("1G-1M", "block_1G-1M_bin_Sshare"), ("1N-1P", "block_1N-1P_bin_Sshare"), ("all", "ref_all_vs_1A-1E_bin")):
    e = map_q_err(Q[g]) * (s_cell[g] if g != "all" else 1.0) * x
    e = np.where(Q[g]["ok"][jpt, jpz], e, 0.0)
    pidx = jpt * 10 + jpz
    Nm = np.where(pidx[:, None] == pidx[None, :], np.outer(e, e), 0.0)
    lam, V = np.linalg.eigh(0.5 * (C_tot + C_tot.T))
    keep = lam > 1e-12 * lam.max()
    Ci = (V[:, keep] / lam[keep]) @ V[:, keep].T
    res["Q2"][key]["expected_chi2_from_data_stat_noise_alone"] = float(np.trace(Ci @ Nm))

# which eigenmodes of the p_|| marginal covariance carry each chi2 (fractional units)
Cz = Ppz @ C_tot @ Ppz.T
Fz = Cz / np.outer(cpz, cpz)
lamz, Vz = np.linalg.eigh(0.5 * (Fz + Fz.T))
lamz, Vz = lamz[::-1], Vz[:, ::-1]
rmsz = np.sqrt(np.maximum(lamz, 0) / len(lamz))       # per-bin rms of each unit-sigma mode
res["Q2_pz_mode_breakdown"] = {"mode_per_bin_rms_pct": (100 * rmsz).round(4).tolist()}
MODEKEYS = ("block_1G-1M_sep_Sshare", "block_1G-1M_interp_Sshare", "block_1N-1P_sep_Sshare", "ref_all_vs_1A-1E_sep",
            "ref_all_vs_1A-1E_interp", "J36_ibu_bin")
for kname in MODEKEYS:
    fz = Ppz @ (F[kname] * x) / cpz
    contrib = (Vz.T @ fz) ** 2 / lamz
    res["Q2_pz_mode_breakdown"][kname] = {"chi2_by_mode": contrib.round(4).tolist(),
                                          "chi2_from_modes_with_per_bin_rms_ge_0.5pct": float(contrib[rmsz >= 0.005].sum()),
                                          "chi2_total": float(contrib.sum())}
pr("Q2. Shifts on the 205 cells against the quoted covariance (per-cell diagonal, marginal diagonal, and full chi2)")
pr("  control: prior ref_shape.json marginals reproduced, max |diff| " +
   ", ".join(f"{g} pz {v['pz_maxdiff']:.1e} pT {v['pt_maxdiff']:.1e}" for g, v in rs_ok.items()))
pr(f"  data-POT share: 1G-1M {pot_share['1G-1M']:.4f}, 1N-1P {pot_share['1N-1P']:.4f}")
for g in ("1G-1M", "1N-1P"):
    s = s_cell[g]
    pr(f"  MC-signal share per cell ({g}): median {np.median(s):.4f}, range {s.min():.4f}-{s.max():.4f}")
pr("")
pr("  shift                         integral  cell min..max [%]    pz-marg min..max   pT-marg min..max   "
   "| vs Total: cell z max, n(z>1), pz z max, pT z max, integral z, chi2_205, chi2_pz16, chi2_pT14")
for k, o in res["Q2"].items():
    t = o["vs"]["Total"]
    pr(f"  {k:30s} {o['integral_shift_pct']:+7.3f}  {o['cell_shift_pct']['min']:+6.2f}..{o['cell_shift_pct']['max']:+6.2f}"
       f"     {min(o['pz_marginal_shift_pct']):+6.2f}..{max(o['pz_marginal_shift_pct']):+6.2f}"
       f"     {min(o['pt_marginal_shift_pct']):+6.2f}..{max(o['pt_marginal_shift_pct']):+6.2f}"
       f"   | {t['cell_z_max']:.2f}, {t['n_cells_z_gt_1']}, {t['pz_marg_z_max']:.2f}, {t['pt_marg_z_max']:.2f},"
       f" {t['integral_z']:.2f}, {t['chi2_205_pinv']:.2f}, {t['chi2_pz_marginal']:.2f}, {t['chi2_pt_marginal']:.2f}")
pr("")
pr("  same shifts against single bands/groups: cell z max / pz-marg z max / pT-marg z max / integral z")
for k, o in res["Q2"].items():
    pr(f"  {k:30s} " + "  ".join(f"{n.replace('full_', '')}: {d['cell_z_max']:.2f}/{d['pz_marg_z_max']:.2f}/"
                                  f"{d['pt_marg_z_max']:.2f}/{d['integral_z']:.2f}"
                                  for n, d in o["vs"].items() if n != "Total"))
for k in ("block_1G-1M_bin_Sshare", "block_1N-1P_bin_Sshare", "ref_all_vs_1A-1E_bin"):
    pr(f"  {k}: expected chi2_205 from the proxy's data-stat noise alone = "
       f"{res['Q2'][k]['expected_chi2_from_data_stat_noise_alone']:.2f}")
pr(f"  J36: {n_nan} cells had no finite truth-grid value and used the separable form")
pr("  p_|| marginal chi2 by eigenmode of the quoted p_|| covariance (per-bin rms of each 1-sigma mode [%]; chi2 of the shift in that mode):")
pr("   mode rms/bin             " + " ".join(f"{v:6.2f}" for v in res["Q2_pz_mode_breakdown"]["mode_per_bin_rms_pct"]))
for kname in MODEKEYS:
    d = res["Q2_pz_mode_breakdown"][kname]
    pr(f"   {kname:26s}" + " ".join(f"{v:6.2f}" for v in d["chi2_by_mode"]) +
       f"   (modes with per-bin rms >= 0.5 %: {d['chi2_from_modes_with_per_bin_rms_ge_0.5pct']:.2f} of {d['chi2_total']:.2f})")

pr("")
pr("  p_|| marginal shift per analysis bin [%]")
pr("   pz bin [GeV/c]                 " + " ".join(f"{a:g}-{b:g}" for a, b in zip(C.PZ_A[:-1], C.PZ_A[1:])))
for k in ("J36_ibu_bin", "block_1G-1M_sep_Sshare", "block_1N-1P_sep_Sshare", "ref_all_vs_1A-1E_sep"):
    pr(f"   {k:30s}" + " ".join(f"{v:+6.2f}" for v in res["Q2"][k]["pz_marginal_shift_pct"]))
pr(f"   {'Total sigma':30s}" + " ".join(f"{v:6.2f}" for v in res["Q1_groups"]["Total"]["pz_marginal_pct"]))
pr("  p_T marginal shift per analysis bin [%]")
pr("   pT bin [GeV/c]                 " + " ".join(f"{a:g}-{b:g}" for a, b in zip(C.PT_A[:-1], C.PT_A[1:])))
for k in ("J36_ibu_bin", "block_1G-1M_sep_Sshare", "block_1N-1P_sep_Sshare", "ref_all_vs_1A-1E_sep"):
    pr(f"   {k:30s}" + " ".join(f"{v:+6.2f}" for v in res["Q2"][k]["pt_marginal_shift_pct"]))
pr(f"   {'Total sigma':30s}" + " ".join(f"{v:6.2f}" for v in res["Q1_groups"]["Total"]["pt_marginal_pct"]))
pr("")

# ------------------------------------------------------------------ Q3 (unfolded level): can a band make the shapes?
# block shapes on the proxy grid, step statistic from the yields directly
def block_step(pls):
    Dg, Sg, Bg, _, _ = C.proxy_yields(P, META, pls)
    Dr, Sr, Br, _, _ = C.proxy_yields(P, META, C.REF)
    e = C.PZ_P
    lo = (e[:-1] >= C.STEP_LO[0]) & (e[1:] <= C.STEP_LO[1])
    hi = (e[:-1] >= C.STEP_HI[0]) & (e[1:] <= C.STEP_HI[1])
    def r(m):
        return ((Dg.sum(0)[m] - Bg.sum(0)[m]).sum() / Sg.sum(0)[m].sum()) / ((Dr.sum(0)[m] - Br.sum(0)[m]).sum() / Sr.sum(0)[m].sum())
    return r(hi) / r(lo) - 1, r(lo), r(hi)


res["Q3_block_stats"] = {}
for g in ("1G-1M", "1N-1P", "all"):
    st, rlo, rhi = block_step(C.BLOCKS[g])
    q = Q[g]
    res["Q3_block_stats"][g] = {"step_hi_over_lo_minus_1": float(st), "r_1.5-8": float(rlo), "r_8-15": float(rhi),
                                "total_minus_1": float(q["tot"] - 1),
                                "pz_marginal": q["pz"].round(5).tolist(), "pt_marginal": q["pt"].round(5).tolist()}

wflux = W["wflux"]
uni_bands = sorted(k[len("uni__"):] for k in W.files if k.startswith("uni__"))
pz_block = {g: (Ppz @ (SH[f"shape_{g}_sep"] * x)) / cpz for g in ("1G-1M", "1N-1P")}   # undiluted, analysis p_|| bins
wz = cpz * np.diff(C.PZ_A)


def fit_modes(Fr, f, frac=0.99):
    """Least-squares fit of f in the span of the leading eigenmodes of Fr that hold `frac` of its trace.
    Returns (k, residual fraction |f - fit|^2/|f|^2, Mahalanobis length of the fit in sigma of the band)."""
    lam, V = np.linalg.eigh(0.5 * (Fr + Fr.T))
    lam, V = lam[::-1], V[:, ::-1]
    lam = np.maximum(lam, 0)
    k = int(np.searchsorted(np.cumsum(lam) / lam.sum(), frac) + 1)
    pj = V[:, :k].T @ f
    resid = float(np.sum((f - V[:, :k] @ pj) ** 2) / np.sum(f ** 2))
    return k, resid, float(np.sqrt(np.sum(pj ** 2 / lam[:k])))


res["Q3_unfolded"] = {}
for b in uni_bands:
    X = W[f"uni__{b}"]
    w = wflux if b == "full_Flux" else np.ones(len(X))
    d = X / x - 1.0
    dz = (X @ Ppz.T) / cpz - 1.0                     # (N, 16) p_|| marginal shift
    steps = np.array([C.step_stat_from_marginal(C.PZ_A, 1 + dz[u], wz) for u in range(len(X))])
    tots = (X @ A) / (A @ x) - 1
    wm = lambda v: np.sum(w * v) / w.sum()
    sd = lambda v: float(np.sqrt(wm((v - wm(v)) ** 2)))
    s = {"n_universes": int(len(X)), "category": C.category_for_band(b),
         "step_sd": sd(steps), "step_min": float(steps.min()), "step_max": float(steps.max()),
         "integral_shift_sd": sd(tots), "integral_shift_min": float(tots.min()), "integral_shift_max": float(tots.max())}
    if s["integral_shift_sd"] < 1e-5 and s["step_sd"] < 1e-5 and np.abs(d - (w[:, None] * d).sum(0) / w.sum()).max() < 1e-4:
        s["no_effect_on_cc_signal"] = True
        res["Q3_unfolded"][b] = s
        continue
    Fr = C.wcov(d, w)
    Zc = d - (w[:, None] * d).sum(0) / w.sum()
    Zz = dz - (w[:, None] * dz).sum(0) / w.sum()
    s["match"] = {}
    for g in ("1G-1M", "1N-1P"):
        f = SH[f"shape_{g}_sep"]
        f0 = f - np.average(f, weights=A * x)
        k1, r1, m1 = fit_modes(Fr, f)
        k0, r0, m0 = fit_modes(Fr, f0)
        fz = pz_block[g] - np.average(pz_block[g], weights=wz)
        cz = (Zz @ fz) ** 2 / (np.sum(Zz ** 2, 1) * np.sum(fz ** 2) + 1e-300)
        cc = (Zc @ f) ** 2 / (np.sum(Zc ** 2, 1) * np.sum(f ** 2) + 1e-300)
        blk = res["Q3_block_stats"][g]
        s["match"][g] = {"modes_99pct": k1, "resid_frac_with_offset": r1, "sigma_needed_with_offset": m1,
                         "resid_frac_shape_only": r0, "sigma_needed_shape_only": m0,
                         "best_universe_cos2_cells": float(cc.max()), "best_universe_cos2_pz_shape": float(cz.max()),
                         "block_step_over_band_step_sd": float(blk["step_hi_over_lo_minus_1"] / s["step_sd"]) if s["step_sd"] > 0 else None,
                         "block_total_over_band_integral_sd": float(blk["total_minus_1"] / s["integral_shift_sd"]) if s["integral_shift_sd"] > 0 else None}
    s["pz_marginal_shift_pct_per_universe_first2"] = (100 * dz[:2]).round(3).tolist()
    res["Q3_unfolded"][b] = s

# Flux: the leading eigenmodes of the weighted fractional Flux covariance, p_|| marginal
Xf = W["uni__full_Flux"]
Ff = C.wcov(Xf / x, wflux)
lam, V = np.linalg.eigh(0.5 * (Ff + Ff.T))
lam, V = lam[::-1], V[:, ::-1]
modes = []
for m in range(4):
    v = np.sqrt(lam[m]) * V[:, m]
    vz = (Ppz @ (v * x)) / cpz
    st = C.step_stat_from_marginal(C.PZ_A, 1 + vz, wz)
    modes.append({"mode": m, "variance_fraction": float(lam[m] / lam.sum()), "integral_pct": 100 * float(A @ (v * x) / (A @ x)),
                  "pz_marginal_pct": (100 * vz).round(3).tolist(), "step_pct": 100 * float(st)})
res["Q3_flux_modes"] = modes

pr("Q3 (unfolded level, 187 universe outputs, E_U). Block statistics on the proxy grid (reco level):")
for g, s in res["Q3_block_stats"].items():
    pr(f"  {g:6s}: total-1 = {100 * s['total_minus_1']:+.2f} %, r[1.5,8) = {s['r_1.5-8']:.4f}, r[8,15) = {s['r_8-15']:.4f},"
       f" step r_hi/r_lo-1 = {100 * s['step_hi_over_lo_minus_1']:+.2f} %")
pr("  undiluted block p_|| shape on analysis bins (sep) [%]: ")
for g in pz_block:
    pr(f"   {g:6s}" + " ".join(f"{100 * v:+6.2f}" for v in pz_block[g]))
pr("")
pr("  band (N)                 step sd  step min..max  | integral sd  min..max [%] | 1G-1M: step/sd, k99, resid w/ offset, sigma, "
   "best cos2 cells, best cos2 pz-shape | 1N-1P: total/sd, k99, resid w/ offset, sigma, resid shape-only, best cos2 cells")
order = sorted(res["Q3_unfolded"], key=lambda b: -res["Q3_unfolded"][b]["integral_shift_sd"] - res["Q3_unfolded"][b]["step_sd"])
zero = []
for b in order:
    s = res["Q3_unfolded"][b]
    if s.get("no_effect_on_cc_signal"):
        zero.append(b.replace("full_", ""))
        continue
    m1, m2 = s["match"]["1G-1M"], s["match"]["1N-1P"]
    pr(f"  {b.replace('full_', ''):22s}({s['n_universes']:3d}) {100 * s['step_sd']:6.2f} {100 * s['step_min']:+6.2f}..{100 * s['step_max']:+6.2f}"
       f" | {100 * s['integral_shift_sd']:6.2f} {100 * s['integral_shift_min']:+6.2f}..{100 * s['integral_shift_max']:+6.2f}"
       f" | {m1['block_step_over_band_step_sd']:7.1f}, {m1['modes_99pct']:2d}, {m1['resid_frac_with_offset']:.2f}, {m1['sigma_needed_with_offset']:6.1f},"
       f" {m1['best_universe_cos2_cells']:.2f}, {m1['best_universe_cos2_pz_shape']:.2f}"
       f" | {m2['block_total_over_band_integral_sd']:7.1f}, {m2['modes_99pct']:2d}, {m2['resid_frac_with_offset']:.2f}, {m2['sigma_needed_with_offset']:6.1f},"
       f" {m2['resid_frac_shape_only']:.2f}, {m2['best_universe_cos2_cells']:.2f}")
pr(f"  bands with no effect on the CC signal (all universes equal): {', '.join(zero)}")
pr("  Flux band, leading eigenmodes (MAT-weighted fractional covariance), p_|| marginal at +1 sigma [%]:")
for mo in modes:
    pr(f"   mode {mo['mode']} ({100 * mo['variance_fraction']:.1f} % of variance): integral {mo['integral_pct']:+.2f}, step {mo['step_pct']:+.2f}; "
       + " ".join(f"{v:+.2f}" for v in mo["pz_marginal_pct"]))
for b in ("full_MinosEfficiency", "full_Muon_Energy_MINOS", "full_Muon_Energy_MINERvA", "full_GEANT_Pion"):
    for u, v in enumerate(res["Q3_unfolded"][b]["pz_marginal_shift_pct_per_universe_first2"]):
        pr(f"   {b.replace('full_', '')}_{u} p_|| marginal [%]: " + " ".join(f"{t:+.2f}" for t in v))
res["Q3_shape_vs_total"] = {}
for sk, f in SH.items():
    c2, nk, cond = C.mahalanobis2(f * x, C_tot)
    res["Q3_shape_vs_total"][sk] = {"chi2_205": c2}
pr("  undiluted block shapes against the whole quoted covariance, chi2_205: " +
   ", ".join(f"{k} {v['chi2_205']:.1f}" for k, v in res["Q3_shape_vs_total"].items()))

# ------------------------------------------------------------------ Q2 noise floor by toys (sep and bin mappings)
rng = np.random.default_rng(20261014)
NT = 200
keys = {"block_1G-1M_sep_Sshare": ("1G-1M", "sep"), "block_1N-1P_sep_Sshare": ("1N-1P", "sep"),
        "ref_all_vs_1A-1E_sep": ("all", "sep"), "block_1G-1M_interp_Sshare": ("1G-1M", "interp"),
        "block_1N-1P_interp_Sshare": ("1N-1P", "interp"), "ref_all_vs_1A-1E_interp": ("all", "interp"),
        "block_1G-1M_bin_Sshare": ("1G-1M", "bin"),
        "block_1N-1P_bin_Sshare": ("1N-1P", "bin"), "ref_all_vs_1A-1E_bin": ("all", "bin")}
Ci = {}
for nm, Cm in (("205", C_tot), ("pz", Ppz @ C_tot @ Ppz.T), ("pt", Ppt @ C_tot @ Ppt.T)):
    lam_, V_ = np.linalg.eigh(0.5 * (Cm + Cm.T))
    kp = lam_ > 1e-12 * lam_.max()
    Ci[nm] = (V_[:, kp] / lam_[kp]) @ V_[:, kp].T
toy = {k: {"205": [], "pz": [], "pt": [], "f": []} for k in keys}
for t in range(NT):
    Pt = {}
    for q in C.PLS:
        for comp, var in (("D", "D"), ("S", "S2"), ("B", "B2")):
            v = P[f"{q}__proxy__{comp}"]
            Pt[f"{q}__proxy__{comp}"] = v + rng.normal(size=v.shape) * np.sqrt(np.maximum(P[f"{q}__proxy__{var}"] if comp != "D" else v, 0))
        Pt[f"{q}__proxy__S2"], Pt[f"{q}__proxy__B2"] = P[f"{q}__proxy__S2"], P[f"{q}__proxy__B2"]
    with np.errstate(divide="ignore", invalid="ignore"):
        Qt = {g: C.block_q(Pt, META, C.BLOCKS[g]) for g in ("1G-1M", "1N-1P", "all")}
    for k, (g, mode) in keys.items():
        ft = (map_q(Qt[g], mode) - 1) * (s_cell[g] if g != "all" else 1.0)
        dlt = (ft - F[k]) * x
        toy[k]["205"].append(float(dlt @ Ci["205"] @ dlt))
        dz_, dt_ = Ppz @ dlt, Ppt @ dlt
        toy[k]["pz"].append(float(dz_ @ Ci["pz"] @ dz_))
        toy[k]["pt"].append(float(dt_ @ Ci["pt"] @ dt_))
res["Q2_noise_toys"] = {"n_toys": NT, "note": "chi2 of (toy - nominal) shift: the part of each chi2 that the proxy's "
                        "data and MC statistics alone produce (Gaussian fluctuation of D, S, B per proxy bin and playlist)"}
pr("")
pr(f"Q2 noise floor ({NT} toys): mean chi2 of (toy - nominal) under the quoted covariance [205 / pz16 / pT14]")
for k in keys:
    r = {a: float(np.mean(toy[k][a])) for a in ("205", "pz", "pt")}
    res["Q2_noise_toys"][k] = {"mean_chi2_205": r["205"], "mean_chi2_pz16": r["pz"], "mean_chi2_pt14": r["pt"]}
    nom = res["Q2"][k]["vs"]["Total"]
    pr(f"  {k:28s} noise {r['205']:8.2f} / {r['pz']:6.2f} / {r['pt']:6.2f}    nominal {nom['chi2_205_pinv']:8.2f} / "
       f"{nom['chi2_pz_marginal']:6.2f} / {nom['chi2_pt_marginal']:6.2f}")
pr(f"  quoted covariance conditioning: 205 kept modes {res['Q2']['block_1G-1M_sep_Sshare']['vs']['Total']['chi2_205_kept_modes']},"
   f" cond {res['Q2']['block_1G-1M_sep_Sshare']['vs']['Total']['chi2_205_cond']:.2e}; pz16 cond "
   f"{res['Q2']['block_1G-1M_sep_Sshare']['vs']['Total']['chi2_pz_marginal_cond']:.2e}; pT14 cond "
   f"{res['Q2']['block_1G-1M_sep_Sshare']['vs']['Total']['chi2_pt_marginal_cond']:.2e}")

json.dump(res, open(out_json, "w"), indent=1)
open(out_txt, "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
