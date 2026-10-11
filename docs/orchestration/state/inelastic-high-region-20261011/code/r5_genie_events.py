"""R5 + A1-c: GENIE 2.12.10 CV event-level model decomposition of regions C and M (PLAN.md §5, §8).

Runs on Perlmutter in the root_6_28 environment. Imports the s5p flux-fix code unchanged (as cap_share.py
does) for the per-event flux weights and the analysis variables; writes only to OUTDIR. All channel and
species labels are GENIE's model labels, not observed mechanisms.

Per event (in the truth phase space): analysis (p_T, p_par, E_avail, q3, W); E_nu; GENIE mode flags; target
(H or C); generator hadronic invariant mass Ws; energy carried by p, pi+-, pi0+gamma, n and other species;
omega = E_nu - E_mu. Main (< 50 GeV) events carry sigma weight A*r/B (gen5d_flux_reweight.build_genie for
genie_cv); supplement (50-100 GeV) events carry the receipt's constant per-event cross section.

Usage: python3 r5_genie_events.py OUTDIR
"""
import json
import os
import resource
import sys

sys.dont_write_bytecode = True
import numpy as np  # noqa: E402

CODE = "/pscratch/sd/j/josephrb/s5p-20260926/gen5d_fluxfix/code"
sys.path.insert(0, CODE)
import gen5d_flux_reweight as gfr  # noqa: E402
import gen5d_flux_supplement as sup  # noqa: E402

OUTDIR = sys.argv[1]
ROOT = gfr.import_root()
g5 = gfr.load_g5(gfr.DEFAULTS["gen5d_tree"])
AX, E5 = g5.AXES, g5.EDGES
shape = tuple(g5.SHAPE)
dV = g5.widths(*AX)
G = gfr.DEFAULTS["genie_dir"]

def species_cpp(which):
    """Scalar sum over final-state particles of one species bucket (no RVec columns)."""
    body = {"p": "if (pdg == 2212) r += E - 0.93827;",
            "pipm": "if (a == 211) r += E - 0.135;",
            "pi0g": "if (pdg == 111 || pdg == 22) r += E;",
            "n": "if (pdg == 2112) r += E - 0.939565;",
            "oth": ("if (!(pdg == 2212 || pdg == 2112 || a == 211 || pdg == 111 || pdg == 22))"
                    " r += (a > 1000 ? E - 0.939565 : E);")}[which]
    return ("double r = 0.0; for (int j = 0; j < nf; ++j) { const int pdg = pdgf[j]; const double E = Ef[j];"
            " const int a = std::abs(pdg); " + body + " } return r;")


SPC = ["p", "pipm", "pi0g", "n", "oth"]
COLS = ["cc", "Ev", "pxv", "pyv", "pzv", "El", "pxl", "pyl", "pzl", "qel", "res", "dis", "coh", "tgt", "Ws",
        "eav5d"] + ["sp_" + k for k in SPC]


def read(gst):
    df = ROOT.RDataFrame("gst", gst).Define("eav5d", g5.EAVAIL_CPP)
    for k in SPC:
        df = df.Define("sp_" + k, species_cpp(k))
    d = df.AsNumpy(COLS)
    d["spc"] = np.stack([d["sp_" + k] for k in SPC], axis=1)
    return d


def kin(d, sel):
    Ev, pxv, pyv, pzv = (d[k][sel] for k in ("Ev", "pxv", "pyv", "pzv"))
    El, pxl, pyl, pzl = (d[k][sel] for k in ("El", "pxl", "pyl", "pzl"))
    W = np.fromiter((g5.gew.w_true((a, b, c, e), (f, g, h, i)) for a, b, c, e, f, g, h, i in
                     zip(Ev.tolist(), pxv.tolist(), pyv.tolist(), pzv.tolist(),
                         El.tolist(), pxl.tolist(), pyl.tolist(), pzl.tolist())), dtype=float, count=sel.size)
    _, q3 = g5.q3_true(Ev, pxv, pyv, pzv, El, pxl, pyl, pzl)
    return {"pt": np.hypot(pxl, pyl), "pz": pzl, "eavail": d["eav5d"][sel], "q3": q3, "W": W}


def in_ps(d):
    pt = np.hypot(d["pxl"], d["pyl"])
    f = g5.u3d.u2d.in_truth_phase_space
    PT, PZ = E5["pt"], E5["pz"]
    return np.fromiter((c and f(float(a), float(b), PT[0], PT[-1], PZ[0], PZ[-1])
                        for c, a, b in zip(d["cc"].astype(bool).tolist(), pt.tolist(), d["pzl"].tolist())),
                       dtype=bool, count=pt.size)


def main():
    edges, phi_t, Phi_t, _, _ = sup.phi_t_arrays()
    main_np, meta = sup.load5(os.path.join(sup.OUT, "genie_cv_xsec5d.npz"), shape)
    full_np, fmeta = sup.load5(os.path.join(sup.OUT, "genie_cv_xsec5d_full.npz"), shape)
    A = meta["normalisation"]["sigma_CC_t_lt50_per_nucleon_cm2"]
    B = meta["normalisation"]["sum_r_normalising_population"]
    pe_supp = fmeta["supplement"]["normalisation"]["per_event_xsec_cm2"]

    gst_main = os.path.join(G, "genie_mefhc_cv_ALL.gst.root")
    mev = sup.main_genie_events(ROOT, g5, "genie_cv", edges, phi_t, Phi_t)
    dm = read(gst_main)
    sm = np.where(in_ps(dm))[0]
    km = kin(dm, sm)
    aligned = bool(np.array_equal(km["pz"], mev["pz_ps"]))
    w_main = A * mev["r_ps"] / B
    ds = read(sup.SUPP_FILES["genie_cv"])
    ss = np.where(in_ps(ds))[0]
    ks = kin(ds, ss)
    w_supp = np.full(ss.size, pe_supp)

    ev = {k: np.concatenate([km[k], ks[k]]) for k in km}
    for k in ("Ev", "El", "qel", "res", "dis", "coh", "tgt", "Ws"):
        ev[k] = np.concatenate([dm[k][sm], ds[k][ss]]).astype(float)
    spc = np.concatenate([dm["spc"][sm], ds["spc"][ss]])
    w = np.concatenate([w_main, w_supp])
    omega = ev["Ev"] - ev["El"]

    # Control: weighted 5D histogram reproduces the committed full product
    cols = [ev[a] for a in AX]
    x5 = g5.hist(cols, w, [E5[a] for a in AX]) / dV
    rec = gfr.compare_arrays(np.asarray(x5).reshape(-1), full_np["xsec_flat"])
    rec["rel_total"] = float((x5 * dV).sum() / (np.asarray(full_np["xsec_flat"]).reshape(shape) * dV).sum() - 1)

    iA = np.digitize(ev["eavail"], E5["eavail"]) - 1
    iW = np.digitize(ev["W"], E5["W"]) - 1
    ingrid = np.ones(w.size, bool)
    for a in AX:
        e = np.asarray(E5[a])
        ingrid &= (ev[a] >= e[0]) & (ev[a] < e[-1])
    regions = {
        "total": ingrid,
        "C": ingrid & (ev["eavail"] >= 0.8) & (ev["W"] >= 1.8),
        "C_no_overflow": ingrid & (ev["eavail"] >= 0.8) & (ev["eavail"] < 3) & (ev["W"] >= 1.8) & (ev["W"] < 3),
        "C_overflow": ingrid & (ev["eavail"] >= 0.8) & (ev["W"] >= 1.8) & ((ev["eavail"] >= 3) | (ev["W"] >= 3)),
        "M": ingrid & (ev["W"] >= 1.4) & (ev["W"] < 1.8),
    }
    for j in range(6):
        regions[f"W{j}"] = ingrid & (iW == j)
    tgt_codes, tgt_counts = np.unique(ev["tgt"].astype(np.int64), return_counts=True)
    isH = ev["tgt"].astype(np.int64) != 1000060120
    out = {"schema": "inelastic-r5/1", "aligned_main": aligned, "reconstruction_vs_full_product": rec,
           "n_events": {"main_ps": int(sm.size), "supp_ps": int(ss.size)}, "regions": {},
           "tgt_codes": {str(int(c)): int(n) for c, n in zip(tgt_codes, tgt_counts)}}
    bands = [0, 5, 10, 20, 50, 100.000001]
    for name, m in regions.items():
        wm = w[m]
        s = wm.sum()
        r = {"sigma_cm2": float(s), "n_events": int(m.sum())}
        r["mode_frac"] = {k: float((wm * ev[k][m]).sum() / s) for k in ("qel", "res", "dis", "coh")}
        r["H_frac"] = float(wm[isH[m]].sum() / s)
        # per-nucleon C-only over CH: sigma_C-only/N = sum_C w / (12/13); sigma_CH/N = sum w
        r["Conly_over_CH_per_nucleon"] = float(wm[~isH[m]].sum() / (12.0 / 13.0) / s)
        r["Enu_band_frac"] = {f"{bands[i]}-{int(round(bands[i + 1]))}": float(
            wm[(ev['Ev'][m] >= bands[i]) & (ev['Ev'][m] < bands[i + 1])].sum() / s) for i in range(len(bands) - 1)}
        r["Enu_mean"] = float((wm * ev["Ev"][m]).sum() / s)
        om = omega[m]
        r["omega_mean"] = float((wm * om).sum() / s)
        sp = spc[m]
        r["E_share_of_omega"] = {lab: float((wm * sp[:, i]).sum() / (wm * om).sum())
                                 for i, lab in enumerate(["p_KE", "pipm_KE135", "pi0_gamma_E", "n_KE", "other"])}
        r["Eavail_over_omega_mean"] = float((wm * ev["eavail"][m]).sum() / (wm * om).sum())
        A_ = ev["eavail"][m]
        r["Eavail_share"] = {lab: float((wm * sp[:, i]).sum() / (wm * A_).sum())
                             for i, lab in enumerate(["p_KE", "pipm_KE135", "pi0_gamma_E"])}
        Ws = ev["Ws"][m]
        r["Wgen_frac"] = {"lt1.4": float(wm[Ws < 1.4].sum() / s), "1.4-1.7": float(wm[(Ws >= 1.4) & (Ws < 1.7)].sum() / s),
                          "1.7-1.8": float(wm[(Ws >= 1.7) & (Ws < 1.8)].sum() / s), "1.8-2.2": float(wm[(Ws >= 1.8) & (Ws < 2.2)].sum() / s),
                          "2.2-3": float(wm[(Ws >= 2.2) & (Ws < 3)].sum() / s), "ge3": float(wm[Ws >= 3].sum() / s)}
        out["regions"][name] = r
    tot = out["regions"]["total"]
    for name, r in out["regions"].items():
        r["Conly_over_CH_rel_to_total"] = r["Conly_over_CH_per_nucleon"] / tot["Conly_over_CH_per_nucleon"]

    # A1-c: GENIE spline sigma_CC/E per nucleon
    fg = ROOT.TFile.Open(sup.GRAPHS_100)
    gr = {}
    for k in fg.GetListOfKeys():
        nm = k.GetName()
        if nm.startswith("nu_mu") and ("C12" in nm or "H1" in nm):
            gr["C12" if "C12" in nm else "H1"] = fg.Get(nm).Get("tot_cc")
    sig = {}
    for E in (3, 5, 6.5, 8, 10, 12, 16, 20, 30, 40, 50):
        c, h = gr["C12"].Eval(E), gr["H1"].Eval(E)
        sig[str(E)] = {"C12_isoscalar_per_nucleon_over_E": c / 12.0 / E, "CH_per_nucleon_over_E": (c + h) / 13.0 / E,
                       "H1_over_E": h / E}
    out["genie_sigma_over_E_1e-38_cm2_per_GeV"] = {"graphs": sup.GRAPHS_100, "values": sig}
    os.makedirs(OUTDIR, exist_ok=True)
    json.dump(out, open(os.path.join(OUTDIR, "r5_genie_events.json"), "w"), indent=1)
    print(json.dumps({"aligned": aligned, "rec": rec, "tgt": out["tgt_codes"]}, default=str))
    for name in ("total", "C", "C_no_overflow", "C_overflow", "M"):
        r = out["regions"][name]
        print(name, json.dumps({k: r[k] for k in ("mode_frac", "H_frac", "Conly_over_CH_rel_to_total", "Enu_band_frac",
                                                  "Eavail_over_omega_mean", "E_share_of_omega", "Wgen_frac")}))
    print(json.dumps(sig))
    ru = resource.getrusage(resource.RUSAGE_SELF)
    rc = resource.getrusage(resource.RUSAGE_CHILDREN)
    print(f"BUDGET_REMOTE_CPU_S={ru.ru_utime + ru.ru_stime + rc.ru_utime + rc.ru_stime:.3f}")


main()
