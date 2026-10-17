#!/usr/bin/env python3
"""F4 independent recomputation of the Stage C production S5 blocks from the per-job unfolded vectors.

Written from DESIGN.md §8 (and the c04-repair definitions it cites). Does NOT import or execute s5_rollup.py,
analyze_prod.py or build_repair.py. Read-only on every input; writes only into the verifier directory.
"""
import hashlib
import json
import os
import sys

import numpy as np
import ROOT

ROOT.gROOT.SetBatch(True)
ROOT.gSystem.Load("libMAT.so")

NS = "/pscratch/sd/j/josephrb/2d-closeout-stageC-production-20261015"
OUT = f"{NS}/out"
D2 = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding"
BF = f"{D2}/baseline_flux"
EU = f"{D2}/uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root"
SWEEPS = f"{NS}/repo_k/docs/orchestration/state/2d-closeout/stageB/evidence/b-genie-truth/sweeps.json"
CONS = ("/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/"
        "sorted_NuEConstraint_FHC_RHC_IMD.txt")
NPZ = f"{NS}/results/s5/production_cov.npz"
S5J = f"{NS}/results/s5/s5.json"
VL175_MINOS = "/pscratch/sd/j/josephrb/2d-closeout-c04repair-20261012/build/minos_rescaled.npz"
PLAYLISTS = ["1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P"]
FLUXH = "pTmu_reweightedflux_integrated"
LAT = ["BeamAngleX", "BeamAngleY", "MuonResolution", "Muon_Energy_MINERvA", "Muon_Energy_MINOS"]
SEEDS = [42, 45, 48, 51, 54]
VD = sys.argv[1]

res = {"checks": {}, "agreement": {}, "functionals": {}, "summaries": {}}


def sha(p):
    h = hashlib.sha256()
    with open(os.path.realpath(p), "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def grid(path, name="hXSec2D"):
    f = ROOT.TFile.Open(path)
    h = f.Get(name)
    nx, ny = h.GetNbinsX(), h.GetNbinsY()
    a = np.zeros((nx, ny))
    for i in range(nx):
        for j in range(ny):
            a[i, j] = h.GetBinContent(i + 1, j + 1)
    wx = np.array([h.GetXaxis().GetBinWidth(i + 1) for i in range(nx)])
    wy = np.array([h.GetYaxis().GetBinWidth(j + 1) for j in range(ny)])
    tx, ty = h.GetXaxis().GetTitle(), h.GetYaxis().GetTitle()
    f.Close()
    return a, wx, wy, (tx, ty)


def h1(path, name):
    f = ROOT.TFile.Open(path)
    h = f.Get(name)
    v = np.array([h.GetBinContent(i + 1) for i in range(h.GetNbinsX())])
    f.Close()
    return v


cv, wx, wy, titles = grid(EU)
NX, NY = cv.shape
mask = (cv > 0)
rep = mask.reshape(-1)          # C order: index = ix*NY + iy, ix = pT
x_eu = cv.reshape(-1)[rep]
area = np.outer(wx, wy).reshape(-1)[rep]
res["checks"]["grid"] = {"NX": NX, "NY": NY, "n_reported": int(rep.sum()), "axis_titles": titles}
print("grid", NX, NY, int(rep.sum()), titles)
consumed = {}


def vec(path):
    a = grid(path)[0]
    return a.reshape(-1)[rep]


def job(name):
    p = f"{OUT}/{name}/xsec.root"
    consumed[name] = sha(p)
    return p


def cov_mean(X, ddof):
    Z = X - X.mean(axis=0)
    return Z.T @ Z / (X.shape[0] - ddof)


def cov_weighted(X, w):
    w = np.asarray(w, float)
    m = (w[:, None] * X).sum(axis=0) / w.sum()
    Z = X - m
    return (Z * w[:, None]).T @ Z / w.sum()


# ---------------- universe block
sw = json.load(open(SWEEPS))
res["checks"]["sweeps_json_sha256"] = sha(SWEEPS)
pn = {}
badsha = []
for k, r in sw.items():
    if not k.startswith("pn/") or k == "pn/CV":
        continue
    band, idx = k[3:].rsplit("_", 1)
    if sha(r["path"]) != r["sha256"]:
        badsha.append(k)
    pn.setdefault(band, {})[int(idx)] = r["path"]
res["checks"]["july_bands"] = len(pn)
res["checks"]["july_universes"] = sum(len(v) for v in pn.values())
res["checks"]["july_sha_mismatch"] = badsha
print("july", len(pn), sum(len(v) for v in pn.values()), "bad", badsha)

bands = {}
for b, d in pn.items():
    if b in LAT or b == "Rvp1pi":
        continue
    assert sorted(d) == list(range(len(d))), (b, sorted(d))
    bands[b] = np.stack([vec(d[i]) for i in sorted(d)])

# Flux weights: the constraint file, "Flux <idx> <w>"
cons = {}
dup = 0
for line in open(CONS):
    t = line.split()
    if len(t) == 3 and t[0] == "Flux":
        if int(t[1]) in cons:
            dup += 1
        cons[int(t[1])] = float(t[2])
nflux = bands["Flux"].shape[0]
w = np.array([cons[i] for i in range(nflux)])
res["checks"]["constraint_entries"] = len(cons)
res["checks"]["constraint_dup_indices"] = dup
res["checks"]["flux_universes"] = nflux
res["checks"]["flux_weight_sum"] = float(w.sum())
res["checks"]["flux_weight_neff"] = float(w.sum() ** 2 / (w ** 2).sum())

# MAT flux weights cross-check (GetUnivWgts on each playlist's flux MnvH1D), and X01 fluxes
mat_ok = True
phi_min, pot = [], []
wl = []
try:
    for pl in PLAYLISTS:
        f = ROOT.TFile.Open(f"{BF}/runEventLoopMC_{pl}.root")
        h = f.Get(FLUXH)
        n = h.GetNbinsX()
        wl.append(np.array(list(h.GetVertErrorBand("Flux").GetUnivWgts())))
        mb = h.GetVertErrorBand("Muon_Energy_MINOS")
        phi_min.append(np.array([[mb.GetHist(u).GetBinContent(i + 1) for i in range(n)] for u in range(2)]))
        f.Close()
        fd = ROOT.TFile.Open(f"{BF}/runEventLoopData_{pl}.root")
        pot.append(float(fd.Get("POTUsed").GetVal()))
        fd.Close()
except Exception as e:  # MAT missing
    mat_ok = False
    res["checks"]["mat_error"] = repr(e)
res["checks"]["mat_available"] = mat_ok
if mat_ok:
    res["checks"]["mat_weights_equal_constraint_all_playlists"] = all(
        x.size == nflux and np.array_equal(x, w) for x in wl)
    pot = np.array(pot)
    res["checks"]["pot"] = pot.tolist()
    phi_minos = np.tensordot(pot, np.stack(phi_min), axes=([0], [0])) / pot.sum()   # (2, n_pT)
phi_cv = h1(f"{BF}/runEventLoopMC_MEFHC.root", FLUXH)

# laterals: S3 outputs replace the 5 bands
lat_paths = {}
for b in LAT:
    for i in (0, 1):
        lat_paths[(b, i)] = job(f"2dc_P_S3_{b.replace('_', '')}{i}")
    bands[b] = np.stack([vec(lat_paths[(b, i)]) for i in (0, 1)])

# X01 on Muon_Energy_MINOS: each S3 output x Phi_CV(pT)/Phi_MINOS,u(pT), per pT row
used = np.stack([h1(lat_paths[("Muon_Energy_MINOS", u)], "hFlux_pt") for u in (0, 1)])
res["checks"]["minos_hFlux_pt_vs_phi_cv_maxrel"] = float(np.abs(used - phi_cv).max() / np.abs(phi_cv).max())
scale = phi_cv[None, :] / phi_minos
ref_scale = np.load(VL175_MINOS)["scale"]
res["checks"]["x01_scale_vs_vl175_npz_maxrel"] = float(np.abs(scale - ref_scale).max() / np.abs(ref_scale).max())
mx = np.stack([(grid(lat_paths[("Muon_Energy_MINOS", u)])[0] * scale[u][:, None]).reshape(-1)[rep]
               for u in (0, 1)])
raw_minos = bands["Muon_Energy_MINOS"].copy()
bands["Muon_Energy_MINOS"] = mx

blocks = {}
for b, X in bands.items():
    blocks[b] = cov_weighted(X, w) if b == "Flux" else cov_mean(X, 0)
norm = np.outer(0.014 * x_eu, 0.014 * x_eu)
C_univ = sum(blocks[b] for b in sorted(blocks)) + norm
res["checks"]["n_universe_bands"] = len(blocks)

# ---------------- stat and bkg-separable
X1 = np.stack([vec(job(f"2dc_P_S1_{n:03d}")) for n in range(1, 301)])
X2 = np.stack([vec(job(f"2dc_P_S2_{n:03d}")) for n in range(1, 101)])
C_stat = cov_mean(X1, 1)
C_bkg = cov_mean(X2, 1)

# ---------------- c08 (seed main effect) and X02
Y = np.stack([np.stack([vec(job(f"2dc_P_S1_{n:03d}" if s == 42 else f"2dc_P_S4B_s{s}_{n:02d}"))
                        for n in range(1, 21)]) for s in SEEDS])
mt = Y.mean(axis=1)
C08 = cov_mean(mt, 1)
R = Y - Y.mean(axis=1, keepdims=True) - Y.mean(axis=0, keepdims=True) + Y.mean(axis=(0, 1), keepdims=True)
Rf = R.reshape(-1, R.shape[-1])
C_int = Rf.T @ Rf / ((5 - 1) * (20 - 1))

C_tot = C_univ + C_stat + C08

# also read the S4(ii) panel outputs (X03 inputs) so their digests are compared too
for u in ["NormDISCC0", "Flux23", "MaRES0", "MaCCQE0", "2p2h0", "MinosEfficiency0", "Muon_Energy_MINOS0"]:
    for s in SEEDS:
        job(f"2dc_P_S4U_{u}_s{s}")
for s in SEEDS[1:]:
    job(f"2dc_P_S4CV_s{s}")
job("2dc_P_C0_cv")

# ---------------- compare with the NPZ
res["checks"]["npz_sha256"] = sha(NPZ)
Z = np.load(NPZ)
res["checks"]["npz_keys"] = sorted(Z.files)


def agree(name, mine, theirs):
    d = float(np.abs(mine - theirs).max())
    m = float(np.abs(theirs).max())
    res["agreement"][name] = {"max_abs_diff": d, "max_abs_block": m, "ratio": d / m if m else None}
    return d / m if m else d


for k, mine in (("cells_x_EU", x_eu), ("area", area), ("universe", C_univ), ("stat", C_stat), ("c08", C08),
                ("total", C_tot), ("bkg_separable", C_bkg), ("x02_interaction", C_int)):
    agree(k, mine, Z[k])
for b in blocks:
    agree(f"band_{b}", blocks[b], Z[f"band_{b}"])
agree("band___Normalization_flat", norm, Z["band___Normalization_flat"])
extra = sorted(set(k for k in Z.files if k.startswith("band_")) - {f"band_{b}" for b in blocks}
               - {"band___Normalization_flat"})
res["checks"]["npz_band_keys_not_rebuilt"] = extra
# total = universe + stat + c08 inside the NPZ itself
res["checks"]["npz_internal_total_minus_sum_rel"] = float(
    np.abs(Z["total"] - (Z["universe"] + Z["stat"] + Z["c08"])).max() / np.abs(Z["total"]).max())
# unrescaled MINOS band, to show the X01 rescale matters
res["checks"]["minos_band_if_not_rescaled_rel"] = float(
    np.abs(cov_mean(raw_minos, 0) - Z["band_Muon_Energy_MINOS"]).max() / np.abs(Z["band_Muon_Energy_MINOS"]).max())
res["checks"]["flux_band_if_unweighted_rel"] = float(
    np.abs(cov_mean(bands["Flux"], 0) - Z["band_Flux"]).max() / np.abs(Z["band_Flux"]).max())

# ---------------- functionals
ix, iy = np.divmod(np.flatnonzero(rep), NY)
F = np.zeros((1 + NX + NY, ix.size))
F[0] = area
for k in range(NX):
    F[1 + k, ix == k] = wy[iy[ix == k]]
for k in range(NY):
    F[1 + NX + k, iy == k] = wx[ix[iy == k]]
agree("functionals_map", F, Z["functionals"])
sig = 100 * np.sqrt(np.diag(F @ C_tot @ F.T)) / np.abs(F @ x_eu)
# independent of matrices: total functional variance from the vectors themselves
Vf = (np.cov(X1 @ F.T, rowvar=False) + np.cov(mt @ F.T, rowvar=False)
      + sum((cov_weighted(bands[b] @ F.T, w) if b == "Flux" else cov_mean(bands[b] @ F.T, 0)) for b in bands)
      + np.outer(0.014 * F @ x_eu, 0.014 * F @ x_eu))
sig_v = 100 * np.sqrt(np.diag(Vf)) / np.abs(F @ x_eu)
s5 = json.load(open(S5J))
theirs = np.array(s5["numbers"]["functionals_total_sigma_rel_pct"])
res["functionals"] = {
    "mine_from_matrix": sig.tolist(), "mine_from_vectors": sig_v.tolist(), "s5json": theirs.tolist(),
    "max_rel_diff_matrix_vs_s5json": float(np.max(np.abs(sig - theirs) / theirs)),
    "max_rel_diff_vectors_vs_s5json": float(np.max(np.abs(sig_v - theirs) / theirs)),
    "integral": float(sig[0]), "pT_range": [float(sig[1:1 + NX].min()), float(sig[1:1 + NX].max())],
    "ppar_range": [float(sig[1 + NX:].min()), float(sig[1 + NX:].max())]}


def summ(C):
    r = np.sqrt(np.maximum(np.diag(C), 0)) / x_eu
    ev = np.linalg.eigvalsh((C + C.T) / 2)
    return {"median_pct": float(100 * np.median(r)), "p84_pct": float(100 * np.percentile(r, 84)),
            "min_pct": float(100 * r.min()), "max_pct": float(100 * r.max()),
            "integral_sigma_pct": float(100 * np.sqrt(area @ C @ area) / (x_eu @ area)),
            "rank_1e-10": int(np.sum(ev > 1e-10 * ev.max())), "min_over_max_eig": float(ev.min() / ev.max()),
            "asym": float(np.abs(C - C.T).max() / np.abs(C).max())}


for n, C in (("universe", C_univ), ("stat", C_stat), ("c08", C08), ("total", C_tot)):
    res["summaries"][n] = {"mine": summ(C), "s5json": s5["numbers"][f"{n}_summary"],
                           "s5json_rank": s5["numbers"][f"{n}_rank"]}
res["summaries"]["sigma_bkg_over_stat_median"] = {
    "mine": float(np.median(np.sqrt(np.diag(C_bkg)) / np.sqrt(np.diag(C_stat)))),
    "s5json": s5["numbers"]["bkg_separable"]["sigma_bkg_over_sigma_stat_median"]}
res["summaries"]["x02_median"] = {"mine": float(np.median(np.diag(C_int) / np.diag(C_stat))),
                                  "s5json": s5["numbers"]["x02"]["interaction_var_over_stat_var_median"]}
res["summaries"]["stat_centring_over_sigma_mean"] = {
    "mine": float(np.median(np.abs(X1.mean(axis=0) - x_eu) / (np.sqrt(np.diag(C_stat)) / np.sqrt(300)))),
    "s5json": s5["numbers"]["centring"]["stat"]["median_abs_offset_over_sigma_mean"]}

# ---------------- consumed-file digests vs s5.json and SHA256SUMS.pscratch
po = s5["inputs"]["production_outputs"]
res["checks"]["consumed_n"] = len(consumed)
res["checks"]["consumed_vs_s5json_mismatch"] = sorted(k for k in consumed if po.get(k) != consumed[k])
res["checks"]["s5json_outputs_not_consumed_here"] = sorted(set(po) - set(consumed))
sums = {}
for line in open(f"{VD}/SHA256SUMS.pscratch.cfs"):
    h_, p_ = line.split(None, 1)
    sums[p_.strip().lstrip("./")] = h_
res["checks"]["consumed_vs_SHA256SUMS_mismatch"] = sorted(
    k for k in consumed if sums.get(f"out/{k}/xsec.root") != consumed[k])

json.dump(res, open(f"{VD}/recompute_result.json", "w"), indent=1, default=str)
for k, v in res["agreement"].items():
    print(f"{k:40s} maxdiff {v['max_abs_diff']:.3e}  maxblock {v['max_abs_block']:.3e}  ratio {v['ratio']}")
print(json.dumps(res["checks"], default=str)[:3000])
print(json.dumps({k: v for k, v in res["functionals"].items() if not k.startswith(("mine", "s5json"))}))
print(json.dumps(res["summaries"], indent=0)[:4000])
