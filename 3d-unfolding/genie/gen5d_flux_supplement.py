#!/usr/bin/env python3
"""gen5d flux fix, round 2: E_nu 50-100 GeV supplements, full predictions, GiBUU reweight.

Builds on gen5d_flux_reweight.py (imported, unchanged; same directory) and its products in
gen5d_fluxfix/. Subcommands (analysis env: source setup_salloc_env.sh):

  make-flux      flux_phi_t_50_100.root:flux_numu, 128 bins as flux_numu, content =
                 phi_t density x bin width on [50,100] GeV, 0 elsewhere. Both GENIE
                 (TH1::GetRandom) and NuWro (EnergyProfile) pick a bin by CONTENT and E
                 uniformly inside it, so this samples phi_t on 50-100 GeV exactly.
                 Refuses to overwrite (the samples were generated from the file on disk).
  graphs-check   gspl2root regenerations of xsec_graphs.root (-e 50, must reproduce it) and
                 to 100 GeV (sigma_CC for the supplement normalisation)
  supplement     --generator {genie_cv,genie_mec,nuwro}: sampling check, supplement 5D,
                 continuity, merge with the <50 GeV product -> <gen>_xsec5d_full.npz
  gibuu          gibuu_cv_xsec5d_fluxfix.npz: per-event r(E) = (phi_t/Phi_t)/phi_gibuu on 0-20 GeV
  receipt        gen5d-fluxfix-2.json, and gen5d-fluxfix.json regenerated through
                 gen5d_flux_reweight.cmd_receipt with every file named by a full path

Supplement normalisation. With the supplement flux, phi_s = phi_t / int_50^100 phi_t, so the
per-event weight r = int_50^100 phi_t / Phi_t is a constant and the self-normalised forms of
gen5d_flux_reweight.py become
  genie_cv   supp = S_50^100 * N_bin / N_CC                 S_50^100 = int_50^100 phi_t sigma_CC / Phi_t
  genie_mec  supp = N_bin * (S_50^100 / N_nonMEC CC)
  nuwro      supp = sum_bin w_e r / N_total                  (w_e: NuWro <sigma> over its 50-100 spectrum)
and the full prediction is the <50 GeV product plus the supplement; sumw2 and nevt add.
"""
import argparse
import glob
import json
import math
import os
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen5d_flux_reweight as gfr  # noqa: E402

S5P = gfr.S5P
OUT = f"{S5P}/gen5d_fluxfix"
SUPP = f"{OUT}/supp"
FLUX_SUPP = f"{SUPP}/flux_phi_t_50_100.root"
GRAPHS_50 = f"{SUPP}/xsec_graphs_regen_e50.root"
GRAPHS_100 = f"{SUPP}/xsec_graphs_regen_e100.root"
SUPP_FILES = {"genie_cv": f"{SUPP}/genie_cv/genie_supp_cv.gst.root",
              "genie_mec": f"{SUPP}/genie_mec/genie_supp_mec.gst.root",
              "nuwro": f"{SUPP}/nuwro/nuwro_supp_flat5d.root"}
LO, HI = 50.0, 100.0
BARE_RE = __import__("re").compile(
    r"[\w./\-]+(?:\.npz|\.npy|\.h5|\.hdf5|\.root|\.pkl|\.parquet|\.out|\.err|\.log)\b")


def code_record():
    me = Path(__file__).resolve()
    return [{"path": str(me), "sha256": gfr.sha256(me)},
            {"path": str(Path(gfr.__file__).resolve()), "sha256": gfr.sha256(Path(gfr.__file__).resolve())},
            {"path": str(Path(__file__).resolve().parent / "run_gen5d_supplement.sh"),
             "sha256": gfr.sha256(Path(__file__).resolve().parent / "run_gen5d_supplement.sh")}]


def phi_t_arrays():
    z, meta, p = gfr.load_phi_t(OUT)
    return z["edges"], z["phi_t_density"], float(z["Phi_t"]), meta, p


# ---------------------------------------------------------------------------
def cmd_make_flux(args):
    if os.path.exists(FLUX_SUPP):
        raise SystemExit(f"{FLUX_SUPP} exists; not overwriting (samples were generated from it)")
    ROOT = gfr.import_root()
    edges, phi_t, Phi_t, meta, p = phi_t_arrays()
    w = np.diff(edges)
    m = (edges[:-1] >= LO - 1e-12) & (edges[1:] <= HI + 1e-12)
    c = np.where(m, phi_t * w, 0.0)
    os.makedirs(SUPP, exist_ok=True)
    import array
    f = ROOT.TFile.Open(FLUX_SUPP, "RECREATE")
    h = ROOT.TH1D("flux_numu", "phi_t x width on [50,100] GeV;E_{#nu} (GeV);per-bin flux",
                  w.size, array.array("d", edges))
    for i, v in enumerate(c, start=1):
        h.SetBinContent(i, float(v))
    h.SetDirectory(f)
    h.Write()
    f.Close()
    gfr.dump_json({"created_utc": gfr.now(), "file": gfr.file_record(FLUX_SUPP, "supplement flux"),
                   "definition": "content_i = phi_t_i * w_i for bins inside [50,100] GeV, else 0",
                   "phi_t_npz": p, "code": code_record()}, f"{SUPP}/flux_phi_t_50_100.json")
    print(FLUX_SUPP)


def check_flux_file(ROOT):
    """The supplement flux on disk must hold exactly phi_t x width on [50,100]."""
    edges, phi_t, Phi_t, _, _ = phi_t_arrays()
    e, c = gfr.read_th1(ROOT, FLUX_SUPP, "flux_numu")
    w = np.diff(edges)
    m = (edges[:-1] >= LO - 1e-12) & (edges[1:] <= HI + 1e-12)
    ok = bool(np.array_equal(e, edges) and np.array_equal(c, np.where(m, phi_t * w, 0.0)))
    if not ok:
        raise SystemExit("supplement flux file does not equal phi_t x width on [50,100]")
    return {"file": gfr.file_record(FLUX_SUPP, "supplement flux (content = phi_t x width, 50-100 GeV)"),
            "contents_equal_phi_t_x_width_bitwise": ok,
            "bins": [[float(a), float(b)] for a, b in zip(edges[:-1][m], edges[1:][m])]}


# ---------------------------------------------------------------------------
def cmd_graphs_check(args):
    ROOT = gfr.import_root()
    G = gfr.DEFAULTS["genie_dir"]
    ref = os.path.join(G, "xsec_graphs.root")
    res = {"created_utc": gfr.now(), "reference": gfr.file_record(ref, f"{ref} (the graphs gen5d and gen5d_fluxfix used)"),
           "regen_e50": gfr.file_record(GRAPHS_50, "gspl2root -e 50"),
           "regen_e100": gfr.file_record(GRAPHS_100, "gspl2root -e 100"), "graphs": {}}
    fr, f50, f100 = (ROOT.TFile.Open(x) for x in (ref, GRAPHS_50, GRAPHS_100))
    for d in ("nu_mu_C12", "nu_mu_H1"):
        for gname in ("tot_cc", "mec_cc"):
            gr, g50, g100 = fr.Get(d).Get(gname), f50.Get(d).Get(gname), f100.Get(d).Get(gname)
            xr = np.array([gr.GetX()[i] for i in range(gr.GetN())])
            yr = np.array([gr.GetY()[i] for i in range(gr.GetN())])
            x5 = np.array([g50.GetX()[i] for i in range(g50.GetN())])
            y5 = np.array([g50.GetY()[i] for i in range(g50.GetN())])
            e100 = np.array([g100.Eval(float(x)) for x in xr])
            nz = yr != 0
            res["graphs"][f"{d}/{gname}"] = {
                "n_ref": int(xr.size), "n_regen_e50": int(x5.size), "n_regen_e100": g100.GetN(),
                "e50_x_bitwise": bool(np.array_equal(xr, x5)), "e50_y_bitwise": bool(np.array_equal(yr, y5)),
                "e50_max_rel_diff_y": float(np.max(np.abs(y5 - yr)[nz] / np.abs(yr[nz]))) if nz.any() and x5.size == xr.size else None,
                "e100_at_ref_knots_max_rel_diff": float(np.max(np.abs(e100 - yr)[nz] / np.abs(yr[nz]))) if nz.any() else None,
                "e100_x_max": float(max(g100.GetX()[i] for i in range(g100.GetN()))),
                "e100_at_ref_knots_max_rel_diff_by_Emin": {
                    str(t): (float(np.max((np.abs(e100 - yr) / np.abs(yr))[nz & (xr >= t)])) if (nz & (xr >= t)).any() else None)
                    for t in (0.5, 1.0, 2.0, 5.0, 20.0)},
                "e100_vs_ref_linear_extrapolation_50_100": (
                    {str(E): float(g100.Eval(E) / gr.Eval(E)) for E in (55.0, 70.0, 85.0, 100.0)} if nz.any() else None),
                "ref_all_zero": bool(not nz.any())}
    gfr.dump_json(res, f"{OUT}/graphs_check.json")
    print(json.dumps(res["graphs"], indent=1))


def sigma100(ROOT, target="CH"):
    return gfr.SigmaCC(ROOT, GRAPHS_100, target)


# ---------------------------------------------------------------------------
class Unit:
    """sigma == 1 (event counts that follow the flux alone)."""
    x_max = float("inf")

    def integral(self, lo, hi):
        return hi - lo


def pz_marginal(g5, x):
    vol = g5.widths(*g5.AXES)
    return (x * vol).sum(axis=(0, 2, 3, 4))


def load5(p, shape):
    z = np.load(p, allow_pickle=True)
    return ({k: np.asarray(z[k]) for k in ("xsec_flat", "sumw2_flat", "nevt_flat")},
            json.loads(str(z["meta_json"])))


def cmd_supplement(args):
    ROOT = gfr.import_root()
    g5 = gfr.load_g5(gfr.DEFAULTS["gen5d_tree"])
    gen = args.generator
    key = "nuwro_cv" if gen == "nuwro" else gen
    AX, E5 = g5.AXES, g5.EDGES
    shape = tuple(g5.SHAPE)
    dV5 = g5.widths(*AX)
    edges, phi_t, Phi_t, phit_meta, phit_path = phi_t_arrays()
    flux_rec = check_flux_file(ROOT)
    e_s, c_s = gfr.read_th1(ROOT, FLUX_SUPP, "flux_numu")
    phi_s, rbin, rng = gfr.flux_weights(e_s, c_s, phi_t, Phi_t, LO, HI)
    r_const = float(np.sum((phi_t * np.diff(edges))[rng]) / Phi_t)
    if not np.allclose(rbin[rng], r_const, rtol=1e-12, atol=0):
        raise SystemExit("supplement r is not constant")
    sigCH = sigma100(ROOT, "CH")
    sigC = sigma100(ROOT, "C12")
    I_CH = sigCH.bin_integrals(edges)
    S_50_100 = float(np.sum((phi_t / Phi_t * I_CH)[rng]))
    main_p = os.path.join(OUT, f"{key}_xsec5d.npz")
    main, main_meta = load5(main_p, shape)
    supp_file = SUPP_FILES[gen]
    inputs = [gfr.file_record(main_p, "<50 GeV repaired product"), flux_rec["file"],
              gfr.file_record(supp_file, "supplement events"), gfr.file_record(GRAPHS_100, "sigma_CC to 100 GeV"),
              gfr.file_record(phit_path, "phi_t")]
    if gen in ("genie_cv", "genie_mec"):
        ev, norm, diag = g5.extract_genie(supp_file, gen == "genie_mec", GRAPHS_100, FLUX_SUPP,
                                          "flux_numu", args.parity_n)
        d = ROOT.RDataFrame("gst", supp_file).AsNumpy(["cc", "mec", "Ev", "El", "pxl", "pyl", "pzl"])
        cc = d["cc"].astype(bool)
        mec = d["mec"].astype(bool)
        Ev = d["Ev"]
        pop = cc & ~mec
        N_pop = int(pop.sum()) if gen == "genie_mec" else int(cc.sum())
        if N_pop != (norm["N_nonMEC_cc"] if gen == "genie_mec" else norm["N_cc"]):
            raise SystemExit("normalising population disagrees with extract_genie")
        samp = [gfr.sampling_test(Ev[pop], e_s, c_s, LO, HI, sigCH, True, "non-MEC CC events (all)")]
        if gen == "genie_mec":
            samp.append(gfr.sampling_test(Ev[cc & mec], e_s, c_s, LO, HI, sigCH, False, "MEC CC events"))
        nevt = g5.hist([ev[a] for a in AX], None, [E5[a] for a in AX])
        pe = S_50_100 / N_pop
        x_s = S_50_100 * (nevt / N_pop) / dV5 if gen == "genie_cv" else nevt * pe / dV5
        v_s = nevt * (pe ** 2) / dV5 ** 2
        supp_norm = {"convention": ("S_50^100 * N_bin / N_CC" if gen == "genie_cv"
                                    else "N_bin * (S_50^100 / N_nonMEC CC)"),
                     "S_50_100_cm2": S_50_100, "N_normalising_population": N_pop,
                     "N_events_in_file": int(cc.size), "N_cc": int(cc.sum()),
                     "N_nonMEC_cc": int(pop.sum()), "r_constant": r_const,
                     "per_event_xsec_cm2": pe}
        if gen == "genie_mec":
            supp_norm["nonMEC_over_CC"] = float(pop.sum() / cc.sum())
        # main (<50 GeV) per-event pieces for continuity / E>20 shares
        mg = main_meta["normalisation"]
        A_main = mg["sigma_CC_t_lt50_per_nucleon_cm2"]
        B_main = mg["sum_r_normalising_population"]
        mev = main_genie_events(ROOT, g5, gen, edges, phi_t, Phi_t)
        e_main_cc, w_main_cc = mev["E_pop"], mev["r_pop"] * A_main / B_main
        e_supp_cc, w_supp_cc = Ev[pop], np.full(int(pop.sum()), pe)
        kin_main, kin_supp = mev["kin"], genie_kin(d, pop)
        E_ps_main, w_ps_main, pz_ps_main = mev["E_ps"], mev["r_ps"] * A_main / B_main, mev["pz_ps"]
        in_ps_supp = np.zeros(cc.size, bool)
        pt_all = np.hypot(d["pxl"], d["pyl"])
        in_ps = g5.u3d.u2d.in_truth_phase_space
        PT, PZ = E5["pt"], E5["pz"]
        in_ps_supp[:] = np.fromiter((c and in_ps(float(a), float(b), PT[0], PT[-1], PZ[0], PZ[-1])
                                     for c, a, b in zip(cc.tolist(), pt_all.tolist(), d["pzl"].tolist())),
                                    dtype=bool, count=cc.size)
        E_ps_supp, pz_ps_supp = Ev[in_ps_supp], d["pzl"][in_ps_supp]
        w_ps_supp = np.full(E_ps_supp.size, pe)
        main_check = mev["recon_vs_product"](main["xsec_flat"], A_main, B_main)
        sig_expect = lambda a, b: float(np.sum([sigCH.integral(max(a, x0), min(b, x1)) * p / Phi_t
                                                for x0, x1, p in zip(edges[:-1], edges[1:], phi_t)
                                                if x1 > a and x0 < b]))
    else:
        ev, norm, diag = g5.extract_nuwro([supp_file], [supp_file])
        cols = ["cc", "pt", "pz", "Enu", "weight", "dyn", "q0"]
        d = ROOT.RDataFrame("nuwro_obs", supp_file).AsNumpy(cols)
        fn = ROOT.TFile.Open(supp_file)
        N_total = int(fn.Get("nTotal").GetVal())
        fn.Close()
        ccm = d["cc"].astype(bool)
        Ev = d["Enu"]
        dism = (d["dyn"] > 1) & (d["dyn"] < 6)
        samp = [gfr.sampling_test(Ev[ccm], e_s, c_s, LO, HI, sigC, False, "all CC events"),
                gfr.sampling_test(Ev[ccm & dism], e_s, c_s, LO, HI, sigC, False, "CC RES/DIS (dyn 2-5)"),
                gfr.sampling_test(Ev[ccm & ~dism], e_s, c_s, LO, HI, sigC, False, "CC QEL/COH/MEC")]
        r_ps = np.full(ev["pt"].size, r_const)
        x_s, v_s = gfr.build_weighted_nuwro(g5, ev, r_ps, float(N_total), dV5)
        nevt = g5.hist([ev[a] for a in AX], None, [E5[a] for a in AX])
        supp_norm = {"convention": "sum_bin w_e r / N_total, r = int_50^100 phi_t / Phi_t (constant)",
                     "r_constant": r_const, "N_total": N_total, "N_cc": int(ccm.sum()),
                     "weight_mean_cm2": float(np.mean(d["weight"])),
                     "weight_unique": int(np.unique(d["weight"]).size),
                     "S_50_100_nuwro_cm2": float(np.mean(d["weight"]) * r_const),
                     "S_50_100_genie_C12_graph_cm2": float(np.sum((phi_t / Phi_t * sigC.bin_integrals(edges))[rng]))}
        mev = main_nuwro_events(ROOT, g5, edges, phi_t, Phi_t)
        e_main_cc, w_main_cc = mev["E_all"], mev["w_all"]
        w_supp_all = d["weight"] * r_const / N_total
        e_supp_cc, w_supp_cc = Ev, w_supp_all
        kin_main, kin_supp = mev["kin"], nuwro_kin(d, ccm)
        E_ps_main, w_ps_main, pz_ps_main = mev["E_ps"], mev["w_ps"], mev["pz_ps"]
        PT, PZ = E5["pt"], E5["pz"]
        pt_, pz_ = d["pt"], d["pz"]
        m = (ccm & np.isfinite(pt_) & np.isfinite(pz_) & (pt_ >= PT[0]) & (pt_ <= PT[-1])
             & (pz_ >= PZ[0]) & (pz_ <= PZ[-1]) & (np.arctan2(pt_, pz_) < g5.u3d.u2d.MAX_MUON_THETA_RAD))
        E_ps_supp, pz_ps_supp, w_ps_supp = Ev[m], pz_[m], w_supp_all[m]
        main_check = mev["recon_vs_product"](main["xsec_flat"])
        sig_expect = None

    # ---- continuity across 50 GeV
    cont = []
    for (a, b, which) in ((40, 45, "main"), (45, 50, "main"), (50, 55, "supp"), (55, 60, "supp")):
        E_, W_, K_ = ((e_main_cc, w_main_cc, kin_main) if which == "main" else (e_supp_cc, w_supp_cc, kin_supp))
        s = (E_ >= a) & (E_ < b)
        sig_est = float(W_[s].sum())
        flux_share = float(np.sum([p * (min(b, x1) - max(a, x0)) for x0, x1, p in
                                   zip(edges[:-1], edges[1:], phi_t) if x1 > a and x0 < b]) / Phi_t)
        sK = (K_["E"] >= a) & (K_["E"] < b)
        row = {"E_lo": a, "E_hi": b, "sample": which, "n_events": int(s.sum()),
               "sigma_contribution_cm2": sig_est,
               "implied_sigma_per_nucleon_over_E_cm2_per_GeV": sig_est / flux_share / (0.5 * (a + b)),
               "stat_rel_err": float(np.sqrt(np.sum(W_[s] ** 2)) / sig_est) if sig_est > 0 else None,
               "cc_mean_muon_pz_over_Enu": float(np.mean(K_["pz"][sK] / K_["E"][sK])),
               "cc_frac_in_ps_diagnostic": float(np.mean(K_["inps"][sK]))}
        if sig_expect is not None:
            row["sigma_contribution_over_graph_expectation"] = sig_est / sig_expect(a, b)
        cont.append(row)

    # ---- merge
    x_m = main["xsec_flat"].reshape(shape)
    v_m = main["sumw2_flat"].reshape(shape)
    n_m = main["nevt_flat"].reshape(shape)
    x_f, v_f, n_f = x_m + x_s, v_m + v_s, n_m + nevt
    vol = dV5
    mnv = np.asarray(np.load(os.path.join(gfr.DEFAULTS["gen5d_dir"], "mnvtune_v1_xsec5d.npz"),
                             allow_pickle=True)["xsec_flat"], float).reshape(shape)
    pzM, pzS, pzF, pzN = (pz_marginal(g5, x) for x in (x_m, x_s, x_f, mnv))
    vS = (v_s * vol ** 2).sum(axis=(0, 2, 3, 4))
    vF = (v_f * vol ** 2).sum(axis=(0, 2, 3, 4))
    nS = nevt.sum(axis=(0, 2, 3, 4))
    with np.errstate(divide="ignore", invalid="ignore"):
        share = pzS / pzF
        supp_relerr = np.sqrt(vS) / pzS
    affected = share >= 0.01
    pz_e = E5["pz"]
    hi6 = pz_e[:-1] >= 6
    # E > 20 GeV shares of the full in-grid prediction (for the GiBUU report)
    E_all = np.concatenate([E_ps_main, E_ps_supp])
    W_all = np.concatenate([w_ps_main, w_ps_supp])
    PZ_all = np.concatenate([pz_ps_main, pz_ps_supp])
    tot = float(x_f.reshape(-1) @ vol.reshape(-1))
    shares20 = {"frac_sigma_in_grid_from_E_gt_20": float(W_all[E_all > 20].sum() / W_all.sum()),
                "frac_sigma_pz_lt_6_from_E_gt_20": float(W_all[(E_all > 20) & (PZ_all < 6)].sum()
                                                         / W_all[PZ_all < 6].sum()),
                "event_sum_over_grid_total": float(W_all.sum() / tot)}
    res = {
        "schema": "gen5d-fluxfix-full/v1", "created_utc": gfr.now(), "generator": key,
        "generator_label": main_meta["generator_label"], "quantity": main_meta["quantity"],
        "axes": list(AX), "shape": list(shape), "order": "C",
        "edges": {a: E5[a].tolist() for a in AX},
        "phase_space": main_meta["phase_space"], "definitions": main_meta["definitions"],
        "composition": ("full = <50 GeV product (" + main_p + ") + E_nu 50-100 GeV supplement; "
                        "sumw2 and nevt add; E_nu > 100 GeV is absent (phi_t ends at 100 GeV)"),
        "supplement": {"events": gfr.file_record(supp_file, "supplement events"), "flux": flux_rec,
                       "normalisation": supp_norm, "n_in_grid": int(nevt.sum()),
                       "integrated_sigma_cm2": float((x_s * vol).sum()),
                       "stat_rel_err": float(np.sqrt((v_s * vol ** 2).sum()) / (x_s * vol).sum()),
                       "sampling_model": samp, "extract_diagnostics": diag},
        "main_event_reconstruction_check": main_check,
        "continuity_across_50_GeV": cont,
        "sigma_CC_graphs_to_100": {"file": GRAPHS_100,
                                   "S_0_100_over_Phi_t_CH_cm2": float(np.sum(phi_t / Phi_t * I_CH)),
                                   "S_50_100_over_Phi_t_CH_cm2": S_50_100,
                                   "frac_50_100_of_0_100": S_50_100 / float(np.sum(phi_t / Phi_t * I_CH))},
        "pz": {"edges": pz_e.tolist(),
               "ratio_to_mnvtune_main_lt50": (pzM / pzN).tolist(),
               "ratio_to_mnvtune_full": (pzF / pzN).tolist(),
               "supplement_share_of_full": share.tolist(),
               "supplement_stat_rel_err": supp_relerr.tolist(),
               "supplement_raw_events": nS.astype(int).tolist(),
               "full_stat_rel_err": (np.sqrt(vF) / pzF).tolist(),
               "affected_bins_rule": "supplement share of the full >= 1%",
               "affected_bins": [int(i) for i in np.where(affected)[0]],
               "max_supplement_rel_err_in_affected_bins": float(np.max(supp_relerr[affected])),
               "ratio_to_mnvtune_40_60_full": float(pzF[-1] / pzN[-1])},
        "integrated_sigma_cm2": {"main_lt50": float((x_m * vol).sum()), "full": tot,
                                 "full_over_main": tot / float((x_m * vol).sum()),
                                 "full_stat_rel_err": float(np.sqrt((v_f * vol ** 2).sum()) / tot),
                                 "frac_pz_ge_6_main": float(pzM[hi6].sum() / pzM.sum()),
                                 "frac_pz_ge_6_full": float(pzF[hi6].sum() / pzF.sum()),
                                 "mnvtune_v1": float(pzN.sum()),
                                 "frac_pz_ge_6_mnvtune": float(pzN[hi6].sum() / pzN.sum())},
        "E_gt_20_shares_of_full": shares20,
        "inputs": inputs, "code": code_record(), "environment": gfr.environment(), "argv": sys.argv,
    }
    out = os.path.join(OUT, f"{key}_xsec5d_full.npz")
    np.savez(out, xsec_flat=x_f.reshape(-1), sumw2_flat=v_f.reshape(-1), nevt_flat=n_f.reshape(-1),
             n_events=np.int64(n_f.sum()), **{f"edges_{a}": E5[a] for a in AX},
             shape=np.asarray(shape), meta_json=np.asarray(json.dumps(res)))
    gfr.dump_json(res, os.path.splitext(out)[0] + ".meta.json")
    print(json.dumps({"sampling": [(s["population"], s["pass"], s["across_bins_content_proportional"]["p"],
                                    s["within_bin_uniform_x_sigma"]["p"]) for s in samp],
                      "continuity": cont, "pz": {k: res["pz"][k] for k in
                                                 ("ratio_to_mnvtune_full", "supplement_share_of_full",
                                                  "supplement_stat_rel_err", "affected_bins",
                                                  "max_supplement_rel_err_in_affected_bins")},
                      "integrated": res["integrated_sigma_cm2"], "main_check": main_check,
                      "shares20": shares20, "supp_norm": supp_norm}, indent=1))
    if not all(s["pass"] for s in samp):
        raise SystemExit("STOP: supplement sampling check failed (product written for inspection)")


def genie_kin(d, pop):
    cc = d["cc"].astype(bool)
    pt = np.hypot(d["pxl"], d["pyl"])
    th = np.arctan2(pt, d["pzl"])
    inps = cc & (pt <= 4.5) & (d["pzl"] >= 1.5) & (d["pzl"] <= 60) & (th < np.deg2rad(20))
    return {"E": d["Ev"][pop], "pz": d["pzl"][pop], "inps": inps[pop], "mask": pop}


def nuwro_kin(d, ccm):
    pt, pz = d["pt"][ccm], d["pz"][ccm]
    inps = (np.isfinite(pt) & np.isfinite(pz) & (pt <= 4.5) & (pz >= 1.5) & (pz <= 60)
            & (np.arctan2(pt, pz) < np.deg2rad(20)))
    return {"E": d["Enu"][ccm], "pz": np.where(np.isfinite(pz), pz, 0.0), "inps": inps, "mask": ccm}


def main_genie_events(ROOT, g5, gen, edges, phi_t, Phi_t):
    """<50 GeV sample: per-event E and r, the same selection as gen5d_flux_reweight.cmd_reweight."""
    G = gfr.DEFAULTS["genie_dir"]
    gst = os.path.join(G, "genie_mefhc_cv_ALL.gst.root" if gen == "genie_cv" else "genie_mefhc_mec_ALL.gst.root")
    e_s, c_s = gfr.read_th1(ROOT, os.path.join(G, "flux_mefhc_numu.root"), "flux_numu")
    _, rbin, rng = gfr.flux_weights(e_s, c_s, phi_t, Phi_t, 0.0, 50.0)
    d = ROOT.RDataFrame("gst", gst).AsNumpy(["cc", "mec", "Ev", "pxl", "pyl", "pzl"])
    cc = d["cc"].astype(bool)
    mec = d["mec"].astype(bool)
    pt = np.hypot(d["pxl"], d["pyl"])
    pz = d["pzl"]
    in_ps = g5.u3d.u2d.in_truth_phase_space
    PT, PZ = g5.EDGES["pt"], g5.EDGES["pz"]
    inps = np.fromiter((c and in_ps(float(a), float(b), PT[0], PT[-1], PZ[0], PZ[-1])
                        for c, a, b in zip(cc.tolist(), pt.tolist(), pz.tolist())), dtype=bool, count=cc.size)
    r = gfr.r_of(d["Ev"], e_s, rbin, rng)
    pop = cc if gen == "genie_cv" else (cc & ~mec)
    sel = np.where(inps)[0]

    def recon(xsec_flat, A, B):
        # rebuild the <50 GeV product from these per-event weights through gen_to_xsec5d's extraction
        ev, _, _ = g5.extract_genie(gst, gen == "genie_mec", os.path.join(G, "xsec_graphs.root"),
                                    os.path.join(G, "flux_mefhc_numu.root"), "flux_numu", 0)
        if not (np.array_equal(ev["pt"], pt[sel]) and np.array_equal(ev["pz"], pz[sel])):
            return {"aligned": False}
        x, _ = gfr.build_genie(g5, gen, ev, r[sel], A, B, g5.widths(*g5.AXES))
        return {"aligned": True, **gfr.compare_arrays(x.reshape(-1), np.asarray(xsec_flat))}

    return {"E_pop": d["Ev"][pop], "r_pop": r[pop], "E_ps": d["Ev"][sel], "r_ps": r[sel], "pz_ps": pz[sel],
            "kin": genie_kin(d, pop), "recon_vs_product": recon}


def main_nuwro_events(ROOT, g5, edges, phi_t, Phi_t):
    G = gfr.DEFAULTS["genie_dir"]
    new = sorted(glob.glob(os.path.join(gfr.DEFAULTS["gen5d_dir"], "nuwro_flat5d", "nuwro_flat5d_p*.root")))
    e_s, c_s = gfr.read_th1(ROOT, os.path.join(G, "flux_mefhc_numu_nuwro.root"), "flux_numu")
    _, rbin, rng = gfr.flux_weights(e_s, c_s, phi_t, Phi_t, 0.5, 50.0)
    cols = ["cc", "pt", "pz", "Enu", "weight", "dyn", "q0"]
    acc = {k: [] for k in cols}
    for fn in new:
        dd = ROOT.RDataFrame("nuwro_obs", fn).AsNumpy(cols)
        for k in cols:
            acc[k].append(dd[k])
    d = {k: np.concatenate(v) for k, v in acc.items()}
    N_total = 0
    for fn in new:
        f = ROOT.TFile.Open(fn)
        N_total += int(f.Get("nTotal").GetVal())
        f.Close()
    ccm = d["cc"].astype(bool)
    r = gfr.r_of(d["Enu"], e_s, rbin, rng)
    w = d["weight"] * r / N_total
    PT, PZ = g5.EDGES["pt"], g5.EDGES["pz"]
    pt, pz = d["pt"], d["pz"]
    m = (ccm & np.isfinite(pt) & np.isfinite(pz) & (pt >= PT[0]) & (pt <= PT[-1]) & (pz >= PZ[0])
         & (pz <= PZ[-1]) & (np.arctan2(pt, pz) < g5.u3d.u2d.MAX_MUON_THETA_RAD))

    def recon(xsec_flat):
        oldf = sorted(glob.glob(os.path.join(G, "work_nuwro_p*/nuwro_flat.root")))
        ev, _, _ = g5.extract_nuwro(new, oldf)
        if not (np.array_equal(ev["pt"], pt[m]) and np.array_equal(ev["weight_raw"], d["weight"][m])):
            return {"aligned": False}
        x, _ = gfr.build_weighted_nuwro(g5, ev, r[m], float(N_total), g5.widths(*g5.AXES))
        return {"aligned": True, **gfr.compare_arrays(x.reshape(-1), np.asarray(xsec_flat))}

    return {"E_all": d["Enu"], "w_all": w, "E_ps": d["Enu"][m], "w_ps": w[m], "pz_ps": pz[m],
            "kin": nuwro_kin(d, ccm), "recon_vs_product": recon}


# ---------------------------------------------------------------------------
def gibuu_events(g5, files):
    """gen_to_xsec5d.extract_gibuu, statement for statement, plus each event's E_nu."""
    gib3d, gibew = g5.gib3d, g5.gibew
    MASS_PI, MASS_P = gib3d.MASS_PI, gib3d.MASS_P
    M_N, M_MU, MUON_IDS = gibew.M_NUCLEON, gibew.M_MU, gibew.MUON_IDS
    out = {k: [] for k in ("pt", "pz", "eavail", "q3", "W", "w", "enu")}
    n_events = 0
    enu_all = []
    for fn in files:
        d = np.loadtxt(fn, comments="#")
        if d.ndim == 1:
            d = d[None, :]
        run = d[:, 0].astype(np.int64); ev = d[:, 1].astype(np.int64)
        pid = d[:, 2].astype(int); ch = d[:, 3].astype(int)
        pw = d[:, 4]; E = d[:, 8]; px = d[:, 9]; py = d[:, 10]; pz = d[:, 11]
        enu = d[:, 14]
        key = run * 10_000_000 + ev
        ukey, inv = np.unique(key, return_inverse=True)
        nev = ukey.size
        n_events += nev
        lep = np.isin(pid, MUON_IDS)
        pt_e = np.full(nev, np.nan); pz_e = np.full(nev, np.nan); w_e = np.zeros(nev)
        emu_e = np.full(nev, np.nan); enu_e = np.full(nev, np.nan)
        px_e = np.full(nev, np.nan); py_e = np.full(nev, np.nan)
        li = inv[lep]
        pt_e[li] = np.hypot(px[lep], py[lep]); pz_e[li] = pz[lep]; w_e[li] = pw[lep]
        emu_e[li] = E[lep]; enu_e[li] = enu[lep]
        px_e[li] = px[lep]; py_e[li] = py[lep]
        had = (pw != 0) & (~lep)
        econ = np.zeros(d.shape[0])
        m = had & (pid == 1) & (ch == 1);           econ[m] = E[m] - MASS_P
        m = had & (pid == 101) & (np.abs(ch) == 1); econ[m] = E[m] - MASS_PI
        m = had & (pid == 101) & (ch == 0);         econ[m] = E[m]
        m = had & (pid == 999);                     econ[m] = E[m]
        ea_e = np.zeros(nev); np.add.at(ea_e, inv, econ)
        pmu = np.sqrt(np.clip(emu_e**2 - M_MU**2, 0, None))
        with np.errstate(invalid="ignore", divide="ignore"):
            costh = np.clip(pz_e / pmu, -1.0, 1.0)
            theta = np.arccos(costh)
            q2 = 4.0 * enu_e * emu_e * np.sin(theta / 2.0) ** 2
            w2 = M_N**2 + 2.0 * (enu_e - emu_e) * M_N - q2
            W_e = np.where(w2 > 0, np.sqrt(np.clip(w2, 0, None)), 0.0)
        _, q3_e = g5.q3_true(enu_e, 0.0, 0.0, enu_e, emu_e, px_e, py_e, pz_e)
        # every event's E_nu (any row of the event carries it) for the sampling test
        e_first = np.full(nev, np.nan); e_first[inv[::-1]] = enu[::-1]
        enu_all.append(e_first)
        ok = np.isfinite(pt_e) & (w_e > 0)
        for k, v in (("pt", pt_e), ("pz", pz_e), ("eavail", ea_e), ("q3", q3_e),
                     ("W", W_e), ("w", w_e), ("enu", enu_e)):
            out[k].append(v[ok])
    a = {k: np.concatenate(v) for k, v in out.items()}
    PT, PZ = g5.EDGES["pt"], g5.EDGES["pz"]
    m = (np.isfinite(a["pt"]) & np.isfinite(a["pz"])
         & (a["pt"] >= PT[0]) & (a["pt"] <= PT[-1]) & (a["pz"] >= PZ[0]) & (a["pz"] <= PZ[-1])
         & (np.arctan2(a["pt"], a["pz"]) < g5.u3d.u2d.MAX_MUON_THETA_RAD))
    a = {k: v[m] for k, v in a.items()}
    return a, float(len(files)), n_events, np.concatenate(enu_all)


def edge_jump_test(E, edges, contents, lo, hi, delta):
    """A piecewise-constant proposal makes the count density jump at every point boundary by
    c_k / c_(k-1) (P_keep is continuous). Counts in [x-delta, x) and [x, x+delta) at each
    internal edge x in (lo, hi) must split binomially with p = c_k / (c_(k-1) + c_k)."""
    rows, chi2 = [], 0.0
    for k in range(1, edges.size - 1):
        x = edges[k]
        if not (lo < x < hi) or contents[k - 1] <= 0 or contents[k] <= 0:
            continue
        nb = int(np.sum((E >= x - delta) & (E < x)))
        na = int(np.sum((E >= x) & (E < x + delta)))
        n = na + nb
        p = contents[k] / (contents[k - 1] + contents[k])
        z = (na - n * p) / math.sqrt(n * p * (1 - p)) if n else 0.0
        chi2 += z * z
        rows.append({"edge_GeV": float(x), "n_below": nb, "n_above": na,
                     "expected_ratio": float(contents[k] / contents[k - 1]),
                     "observed_ratio": float(na / nb) if nb else None, "z": float(z)})
    ndf = len(rows)
    pval = gfr.chi2_sf(chi2, ndf)
    return {"population": f"edge-jump test, all written events, edges in ({lo},{hi}) GeV, delta={delta} GeV",
            "mode": "density jump at flux-point boundaries = content ratio (no free parameter)",
            "n_events": int(E.size), "n_outside_generation_bins": 0,
            "across_bins_content_proportional": {"chi2": chi2, "ndf": ndf, "p": pval,
                                                 "max_abs_pull": float(max(abs(r["z"]) for r in rows)),
                                                 "E_lo_of_max_pull": float(max(rows, key=lambda r: abs(r["z"]))["edge_GeV"]),
                                                 "pull_per_bin": [r["z"] for r in rows]},
            "across_bins_alternative_density_x_width": None,
            "within_bin_uniform_x_sigma": {"chi2": None, "ndf": 0, "p": None, "max_abs_pull": None,
                                           "wide_bins_chi2": None, "wide_bins_ndf": 0, "wide_bins_p": None},
            "edges": rows, "pass_rule": f"p >= {gfr.P_MIN}", "pass": bool(pval >= gfr.P_MIN)}


def cmd_gibuu(args):
    ROOT = gfr.import_root()
    g5 = gfr.load_g5(gfr.DEFAULTS["gen5d_tree"])
    AX, E5 = g5.AXES, g5.EDGES
    shape = tuple(g5.SHAPE)
    dV5 = g5.widths(*AX)
    vol = dV5
    edges, phi_t, Phi_t, phit_meta, phit_path = phi_t_arrays()
    G = gfr.DEFAULTS["genie_dir"]
    files = sorted(glob.glob(os.path.join(G, "work_gibuu_arr/task*/FinalEvents.dat")))
    ev_ref, norm_ref, _ = g5.extract_gibuu(files)
    a, M, n_events, enu_every = gibuu_events(g5, files)
    aligned = all(np.array_equal(a[k], ev_ref[kk]) for k, kk in
                  (("pt", "pt"), ("pz", "pz"), ("eavail", "eavail"), ("q3", "q3"), ("W", "W"), ("w", "weight_raw")))
    if not aligned:
        raise SystemExit("GiBUU event alignment with extract_gibuu failed")
    # GiBUU's sampled density: esample.read_fluxfile zeroes points outside [lower, upper] cut,
    # normalises the cumulative sum; eneut draws point j by content, E uniform in enu_j +- step/2
    fl = np.loadtxt(gfr.DEFAULTS["gibuu_flux"], comments="#")
    Eg, fg = fl[:, 0], fl[:, 1]
    step = float(np.median(np.diff(Eg)))
    if not np.allclose(np.diff(Eg), step):
        raise SystemExit("GiBUU flux points not equally spaced")
    cut_lo, cut_hi = 0.0, 20.0
    jc = open(gfr.DEFAULTS["gibuu_jobcard"]).read()
    for line in jc.splitlines():
        s = line.split("!")[0].strip()
        if s.startswith("Enu_upper_cut"):
            cut_hi = float(s.split("=")[1])
        if s.startswith("Enu_lower_cut"):
            cut_lo = float(s.split("=")[1])
    fcut = np.where((Eg >= cut_lo) & (Eg <= cut_hi), fg, 0.0)
    g_edges = np.concatenate([Eg - 0.5 * step, [Eg[-1] + 0.5 * step]])
    g_edges[0] = max(g_edges[0], 0.0)
    phi_g = fcut / (step * fcut.sum())                   # normalised density, 1/GeV
    ig = np.clip(np.searchsorted(g_edges, a["enu"], side="right") - 1, 0, phi_g.size - 1)
    it = np.clip(np.searchsorted(edges, a["enu"], side="right") - 1, 0, phi_t.size - 1)
    if np.any(phi_g[ig] <= 0):
        raise SystemExit("GiBUU event in a zero-flux bin")
    r = (phi_t[it] / Phi_t) / phi_g[ig]
    ev = {"pt": a["pt"], "pz": a["pz"], "eavail": a["eavail"], "q3": a["q3"], "W": a["W"],
          "weight_raw": a["w"], "divisor": M, "scale": 1.0e-38}
    cols = [ev[k] for k in AX]
    e5 = [E5[k] for k in AX]

    def build(rr):
        wr = ev["weight_raw"] * rr
        x = g5.hist(cols, wr, e5) / M / dV5 * 1.0e-38
        v = g5.hist(cols, wr * wr, e5) / M ** 2 / dV5 ** 2 * 1.0e-38 ** 2
        return x, v

    old_p = os.path.join(gfr.DEFAULTS["gen5d_dir"], "gibuu_cv_xsec5d.npz")
    old = np.load(old_p, allow_pickle=True)
    x1, v1 = build(np.ones(r.size))
    nevt = g5.hist(cols, None, e5)
    ident = {"xsec_flat": gfr.compare_arrays(x1.reshape(-1), np.asarray(old["xsec_flat"])),
             "sumw2_flat": gfr.compare_arrays(v1.reshape(-1), np.asarray(old["sumw2_flat"])),
             "nevt_flat": gfr.compare_arrays(nevt.reshape(-1), np.asarray(old["nevt_flat"]))}
    ident["pass"] = bool(all(v["bitwise_equal"] or v["max_rel_diff_nonzero"] <= 1e-12 for v in ident.values()))
    # sampling. Event COUNTS per flux point follow phi_g(E) x P_keep(E): perweight carries sigma,
    # and a draw is dropped only when sigtot < sigmacut (Pauli blocking / below threshold).
    # P_keep rises steeply below ~1.5 GeV (measured: within-bin chi2/4 = 1086, 104, 24 in the
    # first three points), so the count tests use E >= E_TEST_MIN, where it is flat within a point.
    # The reweight does not depend on P_keep: r uses only the proposal density phi_g.
    E_TEST_MIN = 1.5
    fin = np.isfinite(enu_every)
    Et = enu_every[fin]
    samp = [gfr.sampling_test(Et[Et >= E_TEST_MIN], g_edges, fcut * 1.0, E_TEST_MIN, cut_hi, Unit(), False,
                              f"all written events with E_nu >= {E_TEST_MIN} GeV (counts)"),
            edge_jump_test(Et, g_edges, fcut, E_TEST_MIN, cut_hi, 0.1)]
    low = []
    for k in np.where((g_edges[:-1] < E_TEST_MIN) & (fcut > 0))[0]:
        a0, b0 = g_edges[k], g_edges[k + 1]
        o = np.histogram(Et[(Et >= a0) & (Et < b0)], 5, (a0, b0))[0].astype(float)
        e = o.sum() / 5
        low.append({"E_lo": float(a0), "n": int(o.sum()), "within_chi2_ndf4": float(np.sum((o - e) ** 2 / e)),
                    "sub_bin_counts": o.astype(int).tolist()})
    samp_diag = {"E_below_test_min_within_bin": low,
                 "note": ("the pre-registered form (all E, uniform within points) failed only through these "
                          "threshold points; the in-PS count population was dropped: acceptance depends on E")}
    x5, v5 = build(r)
    if not (ident["pass"]):
        raise SystemExit(f"STOP: GiBUU identity failed {ident}")
    mnv = np.asarray(np.load(os.path.join(gfr.DEFAULTS["gen5d_dir"], "mnvtune_v1_xsec5d.npz"),
                             allow_pickle=True)["xsec_flat"], float).reshape(shape)
    pzO, pzN, pzM = pz_marginal(g5, x1), pz_marginal(g5, x5), pz_marginal(g5, mnv)
    eaix = AX.index("eavail")
    ea = lambda x: (x * vol).sum(axis=tuple(i for i in range(5) if i != eaix))
    hi6 = E5["pz"][:-1] >= 6
    tot_o, tot_n = float((x1 * vol).sum()), float((x5 * vol).sum())
    full_shares = {}
    for k in ("genie_cv", "genie_mec", "nuwro_cv"):
        p = os.path.join(OUT, f"{k}_xsec5d_full.meta.json")
        if os.path.exists(p):
            full_shares[k] = json.load(open(p))["E_gt_20_shares_of_full"]
    sigma100_path = GRAPHS_100
    s100 = gfr.SigmaCC(ROOT, sigma100_path, "CH")
    part = phi_t / Phi_t * s100.bin_integrals(edges)
    meta = {
        "schema": "gen5d-fluxfix-gibuu/v1", "created_utc": gfr.now(), "generator": "gibuu_cv",
        "generator_label": "GiBUU 2019", "quantity": json.loads(str(old["meta_json"]))["quantity"],
        "axes": list(AX), "shape": list(shape), "order": "C", "edges": {k: E5[k].tolist() for k in AX},
        "fix": {"r": "r(E) = (phi_t(E)/Phi_t) / phi_gibuu(E), phi_gibuu = GiBUU's own flux zeroed outside "
                     f"[{cut_lo},{cut_hi}] GeV (esample.read_fluxfile) and normalised; E = the event's "
                     "neutrino energy (FinalEvents column 15)",
                "pred": "sum_bin perweight * r / M x 1e-38 (M = number of runs, as gibuu_to_xsec3d.py)",
                "why_exact": ("initNeutrino.f90: each nucleon draws flux_enu = userFlux() (eneut: content-"
                              "proportional point, uniform within +-step/2), perweight = sigma/numtry at that "
                              "energy, no flux factor; so sum perweight/M = <sigma> over the renormalised cut "
                              "flux and a per-event r(E) reweights it exactly to phi_t / Phi_t(0-100)"),
                "E_gt_cut": "absent (not patched)"},
        "gibuu_sampled_density": {"flux_file": gfr.file_record(gfr.DEFAULTS["gibuu_flux"], "GiBUU flux"),
                                  "jobcard": gfr.file_record(gfr.DEFAULTS["gibuu_jobcard"], "jobcard"),
                                  "cut_GeV": [cut_lo, cut_hi], "step_GeV": step,
                                  "n_points_in_cut": int((fcut > 0).sum())},
        "checks": {"identity_r1": ident, "event_alignment_with_extract_gibuu": aligned,
                   "sampling_model": samp, "sampling_diagnostic_low_E": samp_diag,
                   "r_quantiles_1_50_99": np.percentile(r, [1, 50, 99]).tolist(),
                   "r_min_max": [float(r.min()), float(r.max())],
                   "effective_N_in_grid": float((a["w"] * r).sum() ** 2 / ((a["w"] * r) ** 2).sum()),
                   "effective_N_in_grid_before": float(a["w"].sum() ** 2 / (a["w"] ** 2).sum()),
                   "n_in_grid": int(nevt.sum())},
        "integrated_sigma_cm2": {"before": tot_o, "after": tot_n, "after_over_before": tot_n / tot_o,
                                 "after_stat_rel_err": float(np.sqrt((v5 * vol ** 2).sum()) / tot_n),
                                 "frac_pz_ge_6_before": float(pzO[hi6].sum() / pzO.sum()),
                                 "frac_pz_ge_6_after": float(pzN[hi6].sum() / pzN.sum())},
        "pz": {"edges": E5["pz"].tolist(), "ratio_to_mnvtune_before": (pzO / pzM).tolist(),
               "ratio_to_mnvtune_after": (pzN / pzM).tolist(), "after_over_before": (pzN / pzO).tolist()},
        "eavail_ratio_to_mnvtune_before": (ea(x1) / ea(mnv)).tolist(),
        "eavail_ratio_to_mnvtune_after": (ea(x5) / ea(mnv)).tolist(),
        "E_gt_cut_absent_share": {
            "sigma_CC_phi_t_E_gt_cut_over_0_100_genie_CH_graphs_to_100": float(
                part[edges[:-1] >= cut_hi - 1e-12].sum() / part.sum()),
            "in_grid_shares_from_E_gt_20_of_other_generators_full_products": full_shares,
            "note": ("GiBUU has no E > 20 GeV events; these are the shares the other generators' full "
                     "(0-100 GeV) predictions put there, overall in the 5D grid and in its p_par < 6 GeV/c part")},
        "pre_fix_product": gfr.file_record(old_p, "pre-fix GiBUU 5D (identity reference)"),
        "inputs": [gfr.file_record(p, "events") for p in files] + [gfr.file_record(phit_path, "phi_t")],
        "code": code_record(), "environment": gfr.environment(), "argv": sys.argv,
    }
    out = os.path.join(OUT, "gibuu_cv_xsec5d_fluxfix.npz")
    np.savez(out, xsec_flat=x5.reshape(-1), sumw2_flat=v5.reshape(-1), nevt_flat=nevt.reshape(-1),
             n_events=np.int64(nevt.sum()), **{f"edges_{k}": E5[k] for k in AX},
             shape=np.asarray(shape), meta_json=np.asarray(json.dumps(meta)))
    gfr.dump_json(meta, os.path.splitext(out)[0] + ".meta.json")
    print(json.dumps({"identity": ident, "sampling": [(s["population"], s["pass"],
                      s["across_bins_content_proportional"]["p"], s["within_bin_uniform_x_sigma"]["p"])
                      for s in samp], "integrated": meta["integrated_sigma_cm2"], "pz": meta["pz"],
                      "E_gt_cut": meta["E_gt_cut_absent_share"], "r": meta["checks"]["r_quantiles_1_50_99"]},
                     indent=1))
    if not all(s["pass"] for s in samp):
        raise SystemExit("STOP: GiBUU sampling check failed (product written for inspection)")


# ---------------------------------------------------------------------------
def bare_names(obj):
    out = []

    def walk(o, path):
        if isinstance(o, dict):
            for k, v in o.items():
                walk(v, f"{path}.{k}")
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, f"{path}[{i}]")
        elif isinstance(o, str):
            out.extend((path, m) for m in BARE_RE.findall(o) if "/" not in m)
    walk(obj, "")
    return out


def cmd_receipt(args):
    # 1) gen5d-fluxfix.json through its own producer, then every file named by a full path
    gfr.cmd_receipt(argparse.Namespace(out_dir=OUT))
    p1 = os.path.join(OUT, "gen5d-fluxfix.json")
    r1 = json.load(open(p1))
    pu = json.load(open(os.path.join(OUT, "phi_t.json")))["environment"]["PLOTUTILSROOT"]
    B = gfr.DEFAULTS["baseline_flux"]
    r1["phi_t"]["histogram"] = (
        "PlotUtils::FluxReweighter::GetFluxReweighted(14) = flux_E_cvweighted after the nu-e Constrainer, of "
        + ", ".join(f"{pu}/data/flux/flux-gen2thin-pdg14-minervame{g}_rearrangedUniverses.root"
                    for g in ("1D", "1M", "1N"))
        + " (playlists 1A-1F, 1G/1L/1M and 1N/1O/1P respectively)")
    r1["phi_t"]["definition"] = r1["phi_t"]["definition"].replace(
        "runEventLoopData_<p>.root:POTUsed", f"POTUsed of {B}/runEventLoopData_1A.root ... {B}/runEventLoopData_1P.root")
    r1["regenerated"] = {"by": [c for c in code_record()],
                         "why": "every file a receipt names must be a full path (verify_receipt_artifacts.py); "
                                "only phi_t.histogram and phi_t.definition text changed",
                         "utc": gfr.now()}
    bad = bare_names(r1)
    if bad:
        raise SystemExit(f"bare filenames remain in {p1}: {bad}")
    gfr.dump_json(r1, p1)
    # 2) gen5d-fluxfix-2.json
    rec = {"schema": "gen5d-fluxfix-2-receipt/v1", "created_utc": gfr.now(),
           "created_by": f"{Path(__file__).resolve()} receipt (machine-generated from the products' meta)",
           "output_dir": OUT, "code": code_record(), "products": {}}
    for f in ("flux_phi_t_50_100.json",):
        rec["supplement_flux"] = json.load(open(os.path.join(SUPP, f)))
    rec["graphs_check"] = json.load(open(os.path.join(OUT, "graphs_check.json")))
    for key in ("genie_cv", "genie_mec", "nuwro_cv"):
        p = os.path.join(OUT, f"{key}_xsec5d_full.npz")
        m = json.loads(str(np.load(p, allow_pickle=True)["meta_json"]))
        sm = m["supplement"]
        rec["products"][f"{key}_full"] = {
            "npz": p, "npz_sha256": gfr.sha256(p), "meta_json": os.path.splitext(p)[0] + ".meta.json",
            "meta_json_sha256": gfr.sha256(os.path.splitext(p)[0] + ".meta.json"),
            "composition": m["composition"], "supplement_events": sm["events"],
            "supplement_generation_dir": os.path.dirname(sm["events"]["path"]),
            "supplement_normalisation": sm["normalisation"], "supplement_n_in_grid": sm["n_in_grid"],
            "supplement_integrated_sigma_cm2": sm["integrated_sigma_cm2"],
            "supplement_stat_rel_err": sm["stat_rel_err"],
            "sampling_model": [{"population": s["population"], "mode": s["mode"], "n_events": s["n_events"],
                                "n_outside_generation_bins": s["n_outside_generation_bins"],
                                "across": {k: v for k, v in s["across_bins_content_proportional"].items()
                                           if k != "pull_per_bin"},
                                "across_alternative": s["across_bins_alternative_density_x_width"],
                                "within": s["within_bin_uniform_x_sigma"], "pass": s["pass"]}
                               for s in sm["sampling_model"]],
            "main_event_reconstruction_check": m["main_event_reconstruction_check"],
            "continuity_across_50_GeV": m["continuity_across_50_GeV"],
            "sigma_CC_graphs_to_100": m["sigma_CC_graphs_to_100"], "pz": m["pz"],
            "integrated_sigma_cm2": m["integrated_sigma_cm2"],
            "E_gt_20_shares_of_full": m["E_gt_20_shares_of_full"], "inputs": m["inputs"],
            "code": m["code"]}
    p = os.path.join(OUT, "gibuu_cv_xsec5d_fluxfix.npz")
    m = json.loads(str(np.load(p, allow_pickle=True)["meta_json"]))
    ch = m["checks"]
    rec["products"]["gibuu_cv_fluxfix"] = {
        "npz": p, "npz_sha256": gfr.sha256(p), "meta_json": os.path.splitext(p)[0] + ".meta.json",
        "meta_json_sha256": gfr.sha256(os.path.splitext(p)[0] + ".meta.json"),
        "fix": m["fix"], "gibuu_sampled_density": m["gibuu_sampled_density"],
        "checks": {**{k: v for k, v in ch.items() if k != "sampling_model"},
                   "sampling_model": [{"population": s["population"], "mode": s["mode"], "n_events": s["n_events"],
                                       "n_outside_generation_bins": s["n_outside_generation_bins"],
                                       "across": {k: v for k, v in s["across_bins_content_proportional"].items()
                                                  if k != "pull_per_bin"},
                                       "within": s["within_bin_uniform_x_sigma"], "pass": s["pass"]}
                                      for s in ch["sampling_model"]]},
        "integrated_sigma_cm2": m["integrated_sigma_cm2"], "pz": m["pz"],
        "eavail_ratio_to_mnvtune_before": m["eavail_ratio_to_mnvtune_before"],
        "eavail_ratio_to_mnvtune_after": m["eavail_ratio_to_mnvtune_after"],
        "E_gt_cut_absent_share": m["E_gt_cut_absent_share"],
        "pre_fix_product": m["pre_fix_product"], "code": m["code"]}
    rec["receipt_v1"] = {"path": p1, "sha256": gfr.sha256(p1)}
    rec["environment"] = gfr.environment()
    rec["argv"] = sys.argv
    bad = bare_names(rec)
    if bad:
        raise SystemExit(f"bare filenames in gen5d-fluxfix-2.json: {bad}")
    p2 = os.path.join(OUT, "gen5d-fluxfix-2.json")
    gfr.dump_json(rec, p2)
    print(p1, gfr.sha256(p1))
    print(p2, gfr.sha256(p2))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["make-flux", "graphs-check", "supplement", "gibuu", "receipt"])
    ap.add_argument("--generator", choices=["genie_cv", "genie_mec", "nuwro"])
    ap.add_argument("--parity-n", type=int, default=20000)
    args = ap.parse_args()
    {"make-flux": cmd_make_flux, "graphs-check": cmd_graphs_check, "supplement": cmd_supplement,
     "gibuu": cmd_gibuu, "receipt": cmd_receipt}[args.command](args)


if __name__ == "__main__":
    main()
