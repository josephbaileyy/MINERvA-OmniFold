"""Stage A checklist analysis for E_U (2d-closeout A-2). Reads products.json, inputs.json and the
committed paper ancillary files; prints one JSON of measurements. Pure numpy, float64; sums with math.fsum."""
import csv, json, math, sys
import numpy as np

D, REPO = sys.argv[1], sys.argv[2]
pr = json.load(open(f"{D}/products.json"))
inp = json.load(open(f"{D}/inputs.json"))
P = pr["products"]
out = {}

def arr(h, key="vals"):
    return np.array([[float(x) for x in row] for row in h[key]])

def hist(prod, name):
    return P[prod]["hists"][name]

# ---------- paper ancillary ----------
anc = f"{REPO}/2d-unfolding/minerva_paper_anc"
bm = list(csv.DictReader(open(f"{anc}/bin_mapping.txt")))
paper = {}
for r in csv.DictReader(open(f"{anc}/data_result_ptpl_2D_minerva_inclusive_6GeV.txt")):
    gid = (int(r["Ptbin"]) - 1) * 16 + (int(r["P||bin"]) - 1)
    paper[gid] = float(r["cross_section"])
pt_edges_paper = sorted({float(r["Ptbin_lowedge"]) for r in bm} | {float(r["Ptbin_highedge"]) for r in bm})
pz_edges_paper = sorted({float(r["P||bin_lowedge"]) for r in bm} | {float(r["P||bin_highedge"]) for r in bm})
gid_check = all(int(r["GlobalID"]) == (int(r["Ptbin"]) - 1) * 16 + (int(r["P||bin"]) - 1) for r in bm)
paper_reported = sorted(g for g, x in paper.items() if x > 0)

# ---------- E_U cells ----------
xs = hist("E_U", "hXSec2D")
X = arr(xs)
nx, ny = xs["nx"], xs["ny"]
xe, ye = np.array(xs["xedges"]), np.array(xs["yedges"])
dpt, dpz = np.diff(xe), np.diff(ye)
area = np.outer(dpt, dpz)
eu_pos = sorted((ix * 16 + iy) for ix in range(nx) for iy in range(ny) if X[ix, iy] > 0)
eu_neg = int((X < 0).sum())
eu_zero = int((X == 0).sum())
refs = json.load(open(f"{REPO}/docs/orchestration/state/next-preparation-20261009/xr-linux/xr/manifest/references.json"))["references"]
out["cells"] = {
    "shape": [nx, ny], "n_positive": len(eu_pos), "n_zero": eu_zero, "n_negative": eu_neg,
    "pt_edges_equal_paper": bool(np.allclose(xe, pt_edges_paper, rtol=0, atol=1e-12)),
    "pz_edges_equal_paper": bool(np.allclose(ye, pz_edges_paper, rtol=0, atol=1e-12)),
    "bin_mapping_globalid_formula_holds": gid_check, "bin_mapping_rows": len(bm),
    "paper_reported_n": len(paper_reported),
    "E_U_positive_equals_paper_reported": eu_pos == paper_reported,
    "E_U_positive_equals_xr_references_CV42": eu_pos == refs["CV42"]["reported_globalid"],
    "unreported_globalids": sorted(set(range(224)) - set(paper_reported)),
    "uflow_oflow_sum": xs["uflow_oflow_sum"],
}
cells = paper_reported
mask = np.zeros((nx, ny), bool)
for g in cells:
    mask[g // 16, g % 16] = True

def integral(A, m=mask):
    return math.fsum((A * area)[m].ravel().tolist())

I_eu = integral(X)
I_paper = math.fsum(paper[g] * area[g // 16, g % 16] for g in cells)
out["integral"] = {"E_U_205": I_eu, "E_U_all_224": math.fsum((X * area).ravel().tolist()),
                   "paper_205": I_paper, "ratio": I_eu / I_paper,
                   "median_bin_ratio": float(np.median([X[g // 16, g % 16] / paper[g] for g in cells]))}
# projections vs the stored 1D histograms
hpt, hpz = np.array([float(v) for v in hist("E_U", "hXSec_pt")["vals"]]), np.array([float(v) for v in hist("E_U", "hXSec_pz")["vals"]])
out["projections"] = {
    "pt_from_2D_vs_stored_maxrel": float(np.max(np.abs((X * dpz[None, :]).sum(1) - hpt) / np.where(hpt != 0, np.abs(hpt), 1))),
    "pz_from_2D_vs_stored_maxrel": float(np.max(np.abs((X * dpt[:, None]).sum(0) - hpz) / np.where(hpz != 0, np.abs(hpz), 1))),
}

# ---------- units / normalization chain: recompute hXSec2D ----------
par = {k: float(v) for k, v in P["E_U"]["params"].items()}
U = arr(hist("E_U", "hUnfold2D"))
C = arr(hist("E_U", "hOFCompleteness2D"))
phi = np.array([float(v) for v in hist("E_U", "hFlux_pt")["vals"]])
den = C * phi[:, None] * par["nNucleons"] * par["dataPOT"] * area
Xr = np.where((C > 0) & (phi[:, None] > 0), U / np.where(den > 0, den, 1) * 1e4, 0.0)
rel = np.abs(Xr[mask] / X[mask] - 1)
out["units_recompute"] = {"formula": "U/(c*Phi[m^-2/POT]*N*POT*dpT*dpz)*1e4 -> cm^2/(GeV/c)^2/nucleon",
                          "max_rel_vs_stored_205": float(rel.max()), "median_rel": float(np.median(rel)),
                          "outside_mask_max_abs": float(np.abs(X[~mask]).max()),
                          "hXSec2D_title": xs["title"],
                          "flux_hist_title_units": "m^-2/POT (driver make_flux_hist)",
                          "paper_units": "cm^2/(GeV/c)^2 (README)"}

# ---------- params equality across products ----------
out["params"] = {k: P[k]["params"] for k in P if "params" in P[k]}
out["params_all_equal"] = all(P[k]["params"] == P["E_U"]["params"] for k in P if "params" in P[k])
out["fluxSource"] = {k: P[k]["named"].get("fluxSource") for k in P if "named" in P[k]}

# ---------- POT ----------
pl = inp["playlists"]
data_pot = [float(pl[p]["Data"]["params"]["POTUsed"]) for p in pl]
mc_pot = [float(pl[p]["MC"]["params"]["POTUsed"]) for p in pl]
om = pr["omnifiles"]
out["pot"] = {
    "per_playlist_data": dict(zip(pl, data_pot)), "per_playlist_mc": dict(zip(pl, mc_pot)),
    "sum_data": math.fsum(data_pot), "sum_mc": math.fsum(mc_pot),
    "E_U_dataPOT": par["dataPOT"], "E_U_mcPOT": par["mcPOT"], "E_U_potScale": par["potScale"],
    "omnifile_E_U": om["E_U_omnifile"]["params"], "omnifile_XR": om["XR_omnifile"]["params"],
    "flux_file": pr["flux"]["params"],
    "sum_data_rel_vs_E_U": math.fsum(data_pot) / par["dataPOT"] - 1,
    "sum_mc_rel_vs_E_U": math.fsum(mc_pot) / par["mcPOT"] - 1,
    "potScale_rel_vs_ratio": par["potScale"] / (par["dataPOT"] / par["mcPOT"]) - 1,
    "published_dataPOT": 10.61e20, "rel_vs_published": par["dataPOT"] / 10.61e20 - 1,
}

# ---------- flux ----------
fl = np.array([float(v) for v in pr["flux"]["hists"]["pTmu_reweightedflux_integrated"]["vals"]])
fl_edges = pr["flux"]["hists"]["pTmu_reweightedflux_integrated"]["edges"]
per = np.array([[float(v) for v in pl[p]["MC"]["flux"]] for p in pl])
w = np.array(data_pot)
comb = (per * w[:, None]).sum(0) / w.sum()
out["flux"] = {
    "E_U_hFlux_pt_vs_flux_file_maxabs": float(np.max(np.abs(phi - fl))),
    "flux_file_edges_equal_E_U_pt_edges": bool(np.allclose(fl_edges, xe, rtol=0, atol=1e-12)),
    "recombined_from_12_playlists_maxrel_vs_file": float(np.max(np.abs(comb / fl - 1))),
    "sum_bins_m2": math.fsum(phi.tolist()), "E_U_fluxIntegral_m2_per_POT": par["fluxIntegral_m2_per_POT"],
    "sum_rel_vs_param": math.fsum(phi.tolist()) / par["fluxIntegral_m2_per_POT"] - 1,
    "cm2_param_times_1e4_rel": par["fluxIntegral_cm2_per_POT"] * 1e4 / par["fluxIntegral_m2_per_POT"] - 1,
    "per_playlist_spread_maxrel_vs_combined": float(np.max(np.abs(per / comb[None, :] - 1))),
    "hFlux_pt_equal_across_products": {k: bool(np.array_equal(np.array([float(v) for v in P[k]["hists"]["hFlux_pt"]["vals"]]), phi)) for k in P if "hists" in P[k]},
}

# ---------- target count ----------
out["target"] = {"E_U_nNucleons": par["nNucleons"], "driver_constant": 3.2352943296224835e30,
                 "equal": par["nNucleons"] == 3.2352943296224835e30}

# ---------- purity / background ----------
Dd = arr(hist("E_U", "hDataReco2D"))
B = arr(hist("E_U", "hBkgReco2D"))
Msub = arr(hist("E_U", "hMeasSub2D"))
Mtr = arr(hist("E_U", "hMeasTrain2D"))
pur_expect = np.clip(Dd - B, 0, None)
def eq(prod, name):
    a, b = arr(hist(prod, name)), arr(hist("E_U", name))
    d = np.abs(a - b)
    return {"bitwise_equal": bool(np.array_equal(a, b)), "max_abs": float(d.max()),
            "max_rel": float(np.max(d / np.where(np.abs(b) > 0, np.abs(b), 1)))}
out["background"] = {
    "E_U_sum_data_reco": math.fsum(Dd.ravel().tolist()), "E_U_sum_bkg_reco": math.fsum(B.ravel().tolist()),
    "bkg_fraction": math.fsum(B.ravel().tolist()) / math.fsum(Dd.ravel().tolist()),
    "MeasSub_vs_clip(D-B)_maxabs": float(np.max(np.abs(Msub - pur_expect))),
    "MeasTrain_vs_MeasSub_maxabs": float(np.max(np.abs(Mtr - Msub))),
    "MeasTrain_vs_clip(D-B)_maxrel": float(np.max(np.abs(Mtr - pur_expect) / np.where(pur_expect > 0, pur_expect, 1))),
    "vs_L0": {n: eq("L0", n) for n in ("hDataReco2D", "hBkgReco2D", "hMeasSub2D", "hMeasTrain2D", "hTruth2D", "hEffNum", "hEffDen")},
    "vs_E_C": {n: eq("E_C", n) for n in ("hDataReco2D", "hBkgReco2D", "hMeasSub2D", "hMeasTrain2D")},
    "vs_PN_CV": {n: eq("PN_CV", n) for n in ("hDataReco2D", "hBkgReco2D", "hMeasSub2D", "hMeasTrain2D")},
    "L0_runConfig_bkg_mode": json.loads(P["L0"]["named"]["runConfig"]).get("bkg_mode") if not P["L0"]["named"]["runConfig"].endswith("(truncated)") else "truncated",
}

# ---------- completeness ----------
Cin, Cden = arr(hist("E_U", "hOFInputTruth2D")), arr(hist("E_U", "hOFTruthDenom2D"))
out["completeness"] = {
    "max_abs_c_minus_1_reported": float(np.max(np.abs(C[mask] - 1))),
    "max_abs_c_minus_1_all_nonzero": float(np.max(np.abs(C[C != 0] - 1))),
    "n_cells_c_zero": int((C == 0).sum()),
    "sum_input_truth": math.fsum(Cin.ravel().tolist()), "sum_truth_denom": math.fsum(Cden.ravel().tolist()),
    "global_c": math.fsum(Cin.ravel().tolist()) / math.fsum(Cden.ravel().tolist()),
    "vs_L0": eq("L0", "hOFCompleteness2D"), "vs_E_C": eq("E_C", "hOFCompleteness2D"),
    "omnifile_trees": inp["trees"],
}

# ---------- effective seeds / reproduction ----------
def cmp(prod):
    Y = arr(hist(prod, "hXSec2D"))
    r = np.abs(Y[mask] / X[mask] - 1)
    return {"max_rel": float(r.max()), "median_rel": float(np.median(r)),
            "argmax_globalid": int(np.array(cells)[int(np.argmax(r))]),
            "n_over_1e-8": int((r > 1e-8).sum()), "n_bitwise": int((Y[mask] == X[mask]).sum()),
            "integral_rel": integral(Y) / I_eu - 1,
            "sha256": P[prod].get("sha256")}
out["reproduction"] = {k: cmp(k) for k in ("E_U_cfs", "L0", "PN_CV", "SEED1", "L1", "E_C")}
ss = json.load(open(f"{D}/seedscan.json"))
def cmp_seed(v):
    Y = np.array([[float(x) for x in row] for row in v["vals"]])
    r = np.abs(Y[mask] / X[mask] - 1)
    return {"sha256": v["sha256"], "max_rel": float(r.max()), "median_rel": float(np.median(r)),
            "n_over_1e-8": int((r > 1e-8).sum())}
out["seedscan_vs_E_U"] = {k: cmp_seed(v) for k, v in ss.items()}
l0cfg = P["L0"]["named"]["runConfig"]
out["L0_runConfig_head"] = l0cfg[:2000]
out["L0_driverSha256"] = P["L0"]["named"]["driverSha256"]
out["L0_helperSha256"] = P["L0"]["named"]["omnifoldHelperSha256"]
out["sha256"] = {k: P[k].get("sha256") for k in P}
out["flux_file_sha256"] = pr["flux"]["sha256"]
print(json.dumps(out, indent=1, default=str))
