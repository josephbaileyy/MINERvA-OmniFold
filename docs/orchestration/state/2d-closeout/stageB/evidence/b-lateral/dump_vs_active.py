"""Read-only: compare dump-mode lateral support (2D universes_full omnifile) with the
selection-complete active-universe merged file, for one lateral universe BAND_IDX.
Writes JSON to stdout. Row alignment is tested (truth MC/MC_pz identical row by row)."""
import json, sys, time, numpy as np, ROOT
ROOT.gROOT.SetBatch(True)
R = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
DUMP = R + "/2d-unfolding/runEventLoopOmniFold_MEFHC_universes_full.root"
u = sys.argv[1]
ACT = R + f"/nd-unfolding/active_universe_5d/standard/merged/runEventLoopOmniFold_5D_MEFHC_active_{u}.root"
PT = np.array([0,0.07,0.15,0.25,0.33,0.40,0.47,0.55,0.70,0.85,1.0,1.25,1.5,2.5,4.5])
PZ = np.array([1.5,2.0,2.5,3.0,3.5,4.0,4.5,5.0,6.0,7.0,8.0,9.0,10.0,15.0,20.0,40.0,60.0])
def win(pt, pz):
    return np.isfinite(pt) & np.isfinite(pz) & (pt >= 0) & (pt <= 4.5) & (pz >= 1.5) & (pz <= 60)
def h2(pt, pz, w):
    return np.histogram2d(pt, pz, bins=[PT, PZ], weights=w)[0]
def cols(fn, tree, names, lo, hi):
    df = ROOT.RDataFrame(tree, fn).Range(lo, hi)
    # ROOT 6.28 AsNumpy returns UChar_t columns as str (SB1 REPORT sec. 3): cast in C++ first.
    req = []
    for n in names:
        if n.endswith("_pass"):
            df = df.Define(n + "_i", f"(int){n}")
            req.append(n + "_i")
        else:
            req.append(n)
    d = df.AsNumpy(req)
    d = {(k[:-2] if k.endswith("_pass_i") else k): v for k, v in d.items()}
    return {k: np.asarray(v, dtype=np.float64) for k, v in d.items()}
t0 = time.time()
N = 32849103
CH = 4_000_000
out = {"universe": u, "dump": DUMP, "active": ACT, "chunks": 0}
acc = {k: 0 for k in ["rows","mc_equal","mcpz_equal","mcshift_equal","cv_pass","act_pass","dump_win","act_win",
                      "both","dump_only","act_only","sim_equal_both","simpz_equal_both","wreco_equal_both",
                      "wtruth_equal","wtruth_u_equal"]}
H = {k: np.zeros((14,16)) for k in ["cv","dump","act","dump_only","act_only"]}
for lo in range(0, N, CH):
    hi = min(N, lo + CH)
    d = cols(DUMP, "mc_signal_reco", ["MC","MC_pz","sim","sim_pz","sim_pass","w_reco","w_truth",
             f"sim_{u}", f"sim_pz_{u}", f"w_reco_{u}", f"MC_{u}", f"MC_pz_{u}", f"w_truth_{u}"], lo, hi)
    a = cols(ACT, "mc_signal_reco", ["MC","MC_pz","sim","sim_pz","sim_pass","w_reco","w_truth"], lo, hi)
    acc["rows"] += hi - lo
    acc["mc_equal"] += int(np.sum(d["MC"] == a["MC"]))
    acc["mcpz_equal"] += int(np.sum(d["MC_pz"] == a["MC_pz"]))
    acc["mcshift_equal"] += int(np.sum((d[f"MC_{u}"] == a["MC"]) & (d[f"MC_pz_{u}"] == a["MC_pz"])))
    acc["wtruth_equal"] += int(np.sum(d["w_truth"] == a["w_truth"]))
    acc["wtruth_u_equal"] += int(np.sum(d[f"w_truth_{u}"] == a["w_truth"]))
    cvp = d["sim_pass"] != 0
    ap = a["sim_pass"] != 0
    dw = cvp & win(d[f"sim_{u}"], d[f"sim_pz_{u}"])      # what the driver uses in dump mode
    aw = ap & win(a["sim"], a["sim_pz"])                   # selection-complete
    acc["cv_pass"] += int(cvp.sum()); acc["act_pass"] += int(ap.sum())
    acc["dump_win"] += int(dw.sum()); acc["act_win"] += int(aw.sum())
    both = dw & aw
    acc["both"] += int(both.sum()); acc["dump_only"] += int((dw & ~aw).sum()); acc["act_only"] += int((aw & ~dw).sum())
    acc["sim_equal_both"] += int(np.sum(d[f"sim_{u}"][both] == a["sim"][both]))
    acc["simpz_equal_both"] += int(np.sum(d[f"sim_pz_{u}"][both] == a["sim_pz"][both]))
    acc["wreco_equal_both"] += int(np.sum(d[f"w_reco_{u}"][both] == a["w_reco"][both]))
    cvw = cvp & win(d["sim"], d["sim_pz"])
    H["cv"] += h2(d["sim"][cvw], d["sim_pz"][cvw], d["w_reco"][cvw])
    H["dump"] += h2(d[f"sim_{u}"][dw], d[f"sim_pz_{u}"][dw], d[f"w_reco_{u}"][dw])
    H["act"] += h2(a["sim"][aw], a["sim_pz"][aw], a["w_reco"][aw])
    m = dw & ~aw; H["dump_only"] += h2(d[f"sim_{u}"][m], d[f"sim_pz_{u}"][m], d[f"w_reco_{u}"][m])
    m = aw & ~dw; H["act_only"] += h2(a["sim"][m], a["sim_pz"][m], a["w_reco"][m])
    out["chunks"] += 1
    print(f"[chunk] {lo}-{hi} {time.time()-t0:.0f}s", file=sys.stderr, flush=True)
# background: binned comparison (row counts differ under migration)
db = cols(DUMP, "mc_background", ["sim_background_pass", f"sim_background_{u}", f"sim_background_pz_{u}", f"w_bkg_{u}"], 0, 10**9)
ab = cols(ACT, "mc_background", ["sim_background_pass", "sim_background", "sim_background_pz", "w_bkg"], 0, 10**9)
dbm = (db["sim_background_pass"] != 0) & win(db[f"sim_background_{u}"], db[f"sim_background_pz_{u}"])
abm = (ab["sim_background_pass"] != 0) & win(ab["sim_background"], ab["sim_background_pz"])
Hb_d = h2(db[f"sim_background_{u}"][dbm], db[f"sim_background_pz_{u}"][dbm], db[f"w_bkg_{u}"][dbm])
Hb_a = h2(ab["sim_background"][abm], ab["sim_background_pz"][abm], ab["w_bkg"][abm])
out["bkg"] = {"dump_rows": int(len(dbm)), "act_rows": int(len(abm)), "dump_win": int(dbm.sum()), "act_win": int(abm.sum()),
              "dump_wsum": float(Hb_d.sum()), "act_wsum": float(Hb_a.sum())}
out["signal"] = acc
mask = H["cv"] > 0
shift = H["act"] - H["cv"]
err = H["dump"] - H["act"]
with np.errstate(divide="ignore", invalid="ignore"):
    rel_err = np.where(mask, err / H["cv"], 0.0)
    rel_shift = np.where(mask, shift / H["cv"], 0.0)
    frac = np.where(mask & (np.abs(shift) > 0), np.abs(err) / np.abs(shift), np.nan)
out["cells_cv_positive"] = int(mask.sum())
out["sig_reco_rel_err"] = {"max_abs": float(np.max(np.abs(rel_err))), "median_abs": float(np.median(np.abs(rel_err[mask]))),
                           "argmax_ptbin_pzbin": [int(x) for x in np.unravel_index(np.argmax(np.abs(rel_err)), rel_err.shape)]}
out["sig_reco_rel_shift_active"] = {"max_abs": float(np.max(np.abs(rel_shift))), "median_abs": float(np.median(np.abs(rel_shift[mask])))}
f = frac[np.isfinite(frac)]
out["err_over_shift"] = {"n": int(f.size), "median": float(np.median(f)) if f.size else None, "p90": float(np.percentile(f, 90)) if f.size else None,
                         "max": float(np.max(f)) if f.size else None}
with np.errstate(divide="ignore", invalid="ignore"):
    bm = Hb_a > 0
    brel = np.where(bm, (Hb_d - Hb_a) / Hb_a, 0.0)
out["bkg_rel_err"] = {"max_abs": float(np.max(np.abs(brel))), "median_abs": float(np.median(np.abs(brel[bm]))) if bm.any() else None}
out["H"] = {k: v.tolist() for k, v in H.items()}
out["Hbkg"] = {"dump": Hb_d.tolist(), "act": Hb_a.tolist()}
out["seconds"] = time.time() - t0
print(json.dumps(out))
