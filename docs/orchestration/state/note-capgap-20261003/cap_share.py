"""Read-only: share of the flux-repaired GENIE-CV, GENIE+MEC and NuWro (E_avail, W) corner and
integrated cross sections carried by E_nu >= 20 GeV, i.e. the part the GiBUU 2019 sample lacks
(KNOWN_ISSUES 82). Imports the s5p gen5d_fluxfix code unchanged; writes only to OUTDIR."""
import glob, json, os, sys
sys.dont_write_bytecode = True
import numpy as np
CODE = "/pscratch/sd/j/josephrb/s5p-20260926/gen5d_fluxfix/code"
sys.path.insert(0, CODE)
import gen5d_flux_reweight as gfr
import gen5d_flux_supplement as sup
OUTDIR = "/pscratch/sd/j/josephrb/note-capgap-20261003"
ECUT = 20.0
ROOT = gfr.import_root()
g5 = gfr.load_g5(gfr.DEFAULTS["gen5d_tree"])
AX, E5 = g5.AXES, g5.EDGES
shape = tuple(g5.SHAPE)
dV = g5.widths(*AX)
edges, phi_t, Phi_t, _, _ = sup.phi_t_arrays()
iE, iW = AX.index("eavail"), AX.index("W")
ce = np.asarray(E5["eavail"])[:-1] >= 0.8 - 1e-9
cw = np.asarray(E5["W"])[:-1] >= 1.8 - 1e-9
idx = [slice(None)] * 5
corner = np.zeros(shape, bool)
sl = [np.ones(n, bool) for n in shape]; sl[iE] = ce; sl[iW] = cw
corner = np.ix_(*sl)

def proj(x):
    s = np.asarray(x, float).reshape(shape) * dV.reshape(shape)
    return float(s[corner].sum()), float(s.sum())

out = {"axes": list(AX), "eavail_edges": list(map(float, E5["eavail"])), "W_edges": list(map(float, E5["W"])),
       "Ecut_GeV": ECUT, "generators": {}}
G = gfr.DEFAULTS["genie_dir"]
for gen in ("genie_cv", "genie_mec", "nuwro"):
    key = "nuwro_cv" if gen == "nuwro" else gen
    main, meta = sup.load5(os.path.join(sup.OUT, f"{key}_xsec5d.npz"), shape)
    full, _ = sup.load5(os.path.join(sup.OUT, f"{key}_xsec5d_full.npz"), shape)
    if gen != "nuwro":
        A = meta["normalisation"]["sigma_CC_t_lt50_per_nucleon_cm2"]
        B = meta["normalisation"]["sum_r_normalising_population"]
        mev = sup.main_genie_events(ROOT, g5, gen, edges, phi_t, Phi_t)
        gst = os.path.join(G, "genie_mefhc_cv_ALL.gst.root" if gen == "genie_cv" else "genie_mefhc_mec_ALL.gst.root")
        ev, _, _ = g5.extract_genie(gst, gen == "genie_mec", os.path.join(G, "xsec_graphs.root"),
                                    os.path.join(G, "flux_mefhc_numu.root"), "flux_numu", 0)
        aligned = bool(np.array_equal(ev["pz"], mev["pz_ps"]))
        r, E = mev["r_ps"], mev["E_ps"]
        build = lambda rr: gfr.build_genie(g5, gen, ev, rr, A, B, dV)[0]
    else:
        new = sorted(glob.glob(os.path.join(gfr.DEFAULTS["gen5d_dir"], "nuwro_flat5d", "nuwro_flat5d_p*.root")))
        e_s, c_s = gfr.read_th1(ROOT, os.path.join(G, "flux_mefhc_numu_nuwro.root"), "flux_numu")
        _, rbin, rng = gfr.flux_weights(e_s, c_s, phi_t, Phi_t, 0.5, 50.0)
        cols = ["cc", "pt", "pz", "Enu", "weight"]
        acc = {k: [] for k in cols}
        N_total = 0
        for fn in new:
            dd = ROOT.RDataFrame("nuwro_obs", fn).AsNumpy(cols)
            for k in cols:
                acc[k].append(dd[k])
            f = ROOT.TFile.Open(fn); N_total += int(f.Get("nTotal").GetVal()); f.Close()
        d = {k: np.concatenate(v) for k, v in acc.items()}
        PT, PZ = E5["pt"], E5["pz"]
        pt, pz = d["pt"], d["pz"]
        m = (d["cc"].astype(bool) & np.isfinite(pt) & np.isfinite(pz) & (pt >= PT[0]) & (pt <= PT[-1])
             & (pz >= PZ[0]) & (pz <= PZ[-1]) & (np.arctan2(pt, pz) < g5.u3d.u2d.MAX_MUON_THETA_RAD))
        oldf = sorted(glob.glob(os.path.join(G, "work_nuwro_p*/nuwro_flat.root")))
        ev, _, _ = g5.extract_nuwro(new, oldf)
        aligned = bool(np.array_equal(ev["pt"], pt[m]) and np.array_equal(ev["weight_raw"], d["weight"][m]))
        r, E = gfr.r_of(d["Enu"], e_s, rbin, rng)[m], d["Enu"][m]
        build = lambda rr: gfr.build_weighted_nuwro(g5, ev, rr, float(N_total), dV)[0]
    x_main = build(r)
    x_lt = build(r * (E < ECUT))
    recon = gfr.compare_arrays(np.asarray(x_main).reshape(-1), main["xsec_flat"])
    c_full, t_full = proj(full["xsec_flat"])
    c_main, t_main = proj(main["xsec_flat"])
    c_lt, t_lt = proj(x_lt)
    out["generators"][gen] = {
        "aligned": aligned, "recon_main_vs_product": recon,
        "corner_full": c_full, "total_full": t_full, "corner_main_lt50": c_main, "total_main_lt50": t_main,
        "corner_lt20": c_lt, "total_lt20": t_lt,
        "share_ge20_corner": 1 - c_lt / c_full, "share_ge20_total": 1 - t_lt / t_full,
        "n_events_ps": int(E.size), "n_events_ps_ge20": int((E >= ECUT).sum()),
        "n_events_ps_ge20_corner": int(((E >= ECUT) & (np.asarray(ev["eavail"]) >= 0.8) & (np.asarray(ev["W"]) >= 1.8)).sum()),
    }
    print(gen, json.dumps(out["generators"][gen], default=str), flush=True)
gib, _ = sup.load5(os.path.join(sup.OUT, "gibuu_cv_xsec5d_fluxfix.npz"), shape)
out["gibuu_fluxfix"] = dict(zip(("corner", "total"), proj(gib["xsec_flat"])))
os.makedirs(OUTDIR, exist_ok=True)
json.dump(out, open(os.path.join(OUTDIR, "cap_share.json"), "w"), indent=1, default=str)
print(json.dumps({k: v for k, v in out.items() if k != "generators"}, default=str))
