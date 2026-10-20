"""MP-5 prep smoke tests on a login node (small reads only; writes only under mp5/prep):
P1 one MAD file + its G2 1L rows: join coverage, T2 muon check, T4 recompute, timing.
P2 the GENIE event path on the 72 MB supplement gst: n = z reproduces extract_genie bitwise; a toy tilt runs."""
import json, sys, time
from pathlib import Path
sys.dont_write_bytecode = True
C = Path(sys.argv[1]); sys.path.insert(0, str(C))
import numpy as np
import mp5_tune as T
import event_identity as eid
ROOT = T._root()
res = {}
man = [l.strip() for l in open(f"{T.MANIFESTS}/1L_MC.txt") if l.strip()]
t = time.time(); fn, n_all, mad = T.read_mad(man[0]); res["P1_read_s"] = time.time() - t
res["P1_file"], res["P1_truth_entries"], res["P1_prefiltered"] = fn, n_all, int(mad["mc_run"].size)
runs = np.unique(mad["mc_run"]); res["P1_runs"] = runs.tolist()
g = ROOT.RDataFrame("mc_truth_denom", f"{T.G2_DIR}/runEventLoopOmniFold_G2_FPS_1L.root").AsNumpy(T.G2COLS)
g = {k: np.asarray(v) for k, v in g.items()}
m = np.isin(g["mc_run"], runs); g = {k: v[m] for k, v in g.items()}
gk = eid.pack_identity(g["mc_run"], g["mc_subrun"], g["mc_nthEvtInFile"]); mk = eid.pack_identity(mad["mc_run"], mad["mc_subrun"], mad["mc_nthEvtInFile"])
res["P1_g2_rows_this_run"], res["P1_mad_keys_unique"] = int(gk.size), bool(np.unique(mk).size == mk.size)
o = np.argsort(mk); pos = np.clip(np.searchsorted(mk[o], gk), 0, mk.size - 1); hit = mk[o][pos] == gk
res["P1_matched"] = int(hit.sum()); j = o[pos]
e = {k: mad[k][j] for k in T.MADCOLS}
bx, by, bz = T.rotx(e["lx"], e["ly"], e["lz"], T.A_BEAM)
res["P1_mu_true_maxabs_MeV"] = max(T.maxabs(bx, g["mu_true_px"]), T.maxabs(by, g["mu_true_py"]), T.maxabs(bz, g["mu_true_pz"]))
P = np.sqrt(e["lx"]**2 + e["ly"]**2 + e["lz"]**2); th = T.theta_of(bx, by, bz)
M = np.where(e["mc_targetNucleon"] == 2112, T.M_N, np.where(e["mc_targetNucleon"] == 2212, T.M_P, T.M_NUCLEON))
res["P1_pt_maxabs"] = T.maxabs(P / 1000. * np.sin(th), g["MC"]); res["P1_pz_maxabs"] = T.maxabs(P / 1000. * np.cos(th), g["MC_pz"])
Wb = T.w_cvu(M, e["mc_incomingE"], e["lE"], th) / 1000.
res["P1_W_maxabs"] = T.maxabs(Wb, g["MC_W"]); res["P1_W_nan_differs"] = int(np.sum(np.isnan(Wb) != np.isnan(g["MC_W"])))
res["P1_q3_maxabs"] = T.maxabs(np.sqrt(e["mc_Q2"] + (e["mc_incomingE"] - e["lE"])**2) / 1000., g["MC_q3"])
k = np.column_stack([e["kx"], e["ky"], e["kz"]]); kn = k / np.linalg.norm(k, axis=1)[:, None]
nb = T.rotx(kn[:, 0], kn[:, 1], kn[:, 2], T.A_BEAM); res["P1_alpha_mrad"] = T.q(1e3 * T.theta_of(*nb))
print(json.dumps(res, indent=1), flush=True)
# P2
import mp5_genie as G
import gen5d_flux_reweight as gfr, gen5d_flux_supplement as sup
g5 = gfr.load_g5(gfr.DEFAULTS["gen5d_tree"])
t = time.time()
ref, _, _ = g5.extract_genie(sup.SUPP_FILES["genie_cv"], False, sup.GRAPHS_100, sup.FLUX_SUPP, "flux_numu", 0)
ev0, i0 = G.events(ROOT, g5, sup.SUPP_FILES["genie_cv"], None)
r2 = {"P2_bitwise": {kk: bool(np.array_equal(ev0[kk], ref[kk])) for kk in ref}, "P2_nu_along_z": i0["nu_along_z"], "P2_n_in_ps": i0["n_in_ps"]}
a = 2e-3; n = np.tile([np.sin(a), 0.0, np.cos(a)], (i0["n_entries"], 1))
ev1, i1 = G.events(ROOT, g5, sup.SUPP_FILES["genie_cv"], n)
r2.update({"P2_tilt2mrad_n_in_ps": i1["n_in_ps"], "P2_s": time.time() - t,
           "P2_pT_shift_MeV": T.q(1e3 * (np.hypot(*G.rotate(np.ones(3), np.zeros(3), np.ones(3), n[:3])[:2]) - 1)),
           "P2_W_identical_frac": float(np.mean(np.isin(ev1["W"], ev0["W"])))})
print(json.dumps(r2, indent=1), flush=True)
