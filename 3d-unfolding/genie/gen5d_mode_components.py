#!/usr/bin/env python3
"""gen5d flux fix, round 3: per-mode GENIE E_avail components on the repaired flux.

Two note figures need per-mode information the 5D products do not carry:
compare_mec_eavail.py (the MEC-only E_avail component) and mode_decomp_eavail.py
(the QE/RES/DIS/COH decomposition of GENIE CV). This rebuilds that information from
the same events and per-event flux weights as the *_xsec5d_full.npz products of
gen5d_flux_supplement.py (the <50 GeV sample with r(E), plus the 50-100 GeV supplement),
and runs the UNCHANGED producers on it.

  files      genie_cv_xsec3d_modes.root and genie_mec_cv_xsec3d.root (committed histogram
             names). hXSec3D/2D/pt/pz/eavail are the _full product's marginals, computed
             with gen5d_to_rootpreds.integrate (the arithmetic of the coordinator's
             genie_cv_xsec3d.root); hXSec_eavail_{mec,nomec,qel,res,dis,coh,charm} are
             per-event sigma-weighted sums of the same events, required to add up to
             hXSec_eavail to <= 1e-12.
  mode-decomp  mode_decomp_eavail.main() with mode_counts replaced by a sigma-weighted
             version (the script shares dsigma_CV[b] among modes by N_mode[b]/N_total[b];
             with unequal per-event weights the exact analogue is W_mode[b]/W_total[b]).
  receipt    gen5d-fluxfix-3.json
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import gen5d_flux_reweight as gfr  # noqa: E402
import gen5d_flux_supplement as gfs  # noqa: E402

REPO = gfr.REPO
PRODUCERS = f"{gfr.S5P}/deploy/4e4b4f56/3d-unfolding/genie"   # unchanged producers, export of 4e4b4f56
GENFIG = f"{gfr.S5P}/stage7/genfig/3d-unfolding/genie"
DATA = f"{REPO}/3d-unfolding/xsec_3d_MEFHC_5iter_lgbm.root"
COV = f"{REPO}/3d-unfolding/uq_3d/universe_stage2_3d/uq_universe_3d_covariance.root"
OUT_CV = f"{GENFIG}/genie_cv_xsec3d_modes.root"
OUT_MEC = f"{GENFIG}/genie_mec_cv_xsec3d.root"
MODES = ("qel", "res", "dis", "coh", "charm")


def code_record():
    out = []
    for p in (Path(__file__).resolve(), Path(gfs.__file__).resolve(), Path(gfr.__file__).resolve(),
              Path(f"{PRODUCERS}/gen5d_to_rootpreds.py"), Path(f"{PRODUCERS}/compare_mec_eavail.py"),
              Path(f"{PRODUCERS}/mode_decomp_eavail.py")):
        out.append({"path": str(p), "sha256": gfr.sha256(p)})
    return out


def weighted_events(ROOT, g5, gen, sample):
    """In-PS CC events of one sample, with the per-event sigma contribution (cm^2/nucleon)
    that the _full product gives them, their E_avail and mode flags."""
    G = gfr.DEFAULTS["genie_dir"]
    if sample == "main":
        gst = os.path.join(G, "genie_mefhc_cv_ALL.gst.root" if gen == "genie_cv"
                           else "genie_mefhc_mec_ALL.gst.root")
        flux = os.path.join(G, "flux_mefhc_numu.root")
        graphs = os.path.join(G, "xsec_graphs.root")
    else:
        gst = gfs.SUPP_FILES[gen]
        flux = gfs.FLUX_SUPP
        graphs = gfs.GRAPHS_100
    ev, norm, _ = g5.extract_genie(gst, gen == "genie_mec", graphs, flux, "flux_numu", 0)
    d = ROOT.RDataFrame("gst", gst).AsNumpy(["cc", "mec", "Ev", "pxl", "pyl", "pzl"] + list(MODES))
    cc = d["cc"].astype(bool)
    pt = np.hypot(d["pxl"], d["pyl"])
    pz = d["pzl"]
    in_ps = g5.u3d.u2d.in_truth_phase_space
    PT, PZ = g5.EDGES["pt"], g5.EDGES["pz"]
    inps = np.fromiter((c and in_ps(float(a), float(b), PT[0], PT[-1], PZ[0], PZ[-1])
                        for c, a, b in zip(cc.tolist(), pt.tolist(), pz.tolist())), dtype=bool, count=cc.size)
    sel = np.where(inps)[0]
    if not (np.array_equal(pt[sel], ev["pt"]) and np.array_equal(pz[sel], ev["pz"])):
        raise SystemExit(f"alignment with extract_genie failed ({gen} {sample})")
    key = gen
    full_meta = json.load(open(os.path.join(gfs.OUT, f"{key}_xsec5d_full.meta.json")))
    if sample == "main":
        mm = json.load(open(os.path.join(gfs.OUT, f"{key}_xsec5d.meta.json")))["normalisation"]
        edges, phi_t, Phi_t, _, _ = gfs.phi_t_arrays()
        e_s, c_s = gfr.read_th1(ROOT, flux, "flux_numu")
        _, rbin, rng = gfr.flux_weights(e_s, c_s, phi_t, Phi_t, 0.0, 50.0)
        r = gfr.r_of(d["Ev"][sel], e_s, rbin, rng)
        w = r * (mm["sigma_CC_t_lt50_per_nucleon_cm2"] / mm["sum_r_normalising_population"])
        pop_n = mm["N_normalising_population"]
    else:
        sn = full_meta["supplement"]["normalisation"]
        w = np.full(sel.size, sn["per_event_xsec_cm2"])
        pop_n = sn["N_normalising_population"]
    flags = {m: d[m].astype(bool)[sel] for m in MODES}
    return {"eavail": ev["eavail"], "is_mec": ev["is_mec"], "w": w, "flags": flags,
            "n_cc": int(cc.sum()), "n_pop": pop_n, "gst": gst,
            "w_cc_all_mec_share": None}


def cmd_files(args):
    ROOT = gfr.import_root()
    g5 = gfr.load_g5(gfr.DEFAULTS["gen5d_tree"])
    sys.path.insert(0, PRODUCERS)
    sys.path.insert(0, str(Path(PRODUCERS).parent))
    import gen5d_to_rootpreds as g2r
    import unfold_3d_omnifold_unbinned as u3d
    EA = g5.EDGES["eavail"]
    dea = np.diff(EA)
    res = {"schema": "gen5d-fluxfix-modes/v1", "created_utc": gfr.now(), "files": {}}
    for gen, out in (("genie_cv", OUT_CV), ("genie_mec", OUT_MEC)):
        if os.path.exists(out):
            raise SystemExit(f"refusing to overwrite {out}")
        npz = os.path.join(gfs.OUT, f"{gen}_xsec5d_full.npz")
        x, e = g2r.load(npz)
        x3 = g2r.integrate(x, e, (0, 1, 2))
        ea = g2r.integrate(x, e, (2,))
        parts = [weighted_events(ROOT, g5, gen, s) for s in ("main", "supp")]
        E = np.concatenate([p["eavail"] for p in parts])
        W = np.concatenate([p["w"] for p in parts])
        MEC = np.concatenate([p["is_mec"] for p in parts])
        FL = {m: np.concatenate([p["flags"][m] for p in parts]) for m in MODES}
        h = lambda mask: np.histogram(E[mask], EA, weights=W[mask])[0] / dea
        allm = np.ones(E.size, bool)
        ea_events = h(allm)
        comp = {"mec": h(MEC), "nomec": h(~MEC), **{m: h(FL[m]) for m in MODES}}
        chk = {"events_vs_full_marginal_max_rel": float(np.max(np.abs(ea_events - ea) / ea)),
               "mec_plus_nomec_vs_full_marginal_max_rel": float(np.max(np.abs(comp["mec"] + comp["nomec"] - ea) / ea)),
               "qel_res_dis_coh_mec_vs_full_marginal_max_rel": float(np.max(np.abs(
                   comp["qel"] + comp["res"] + comp["dis"] + comp["coh"] + comp["mec"] - ea) / ea))}
        # exclusivity of the four modes (plus MEC) in these events
        nmode = sum(FL[m].astype(int) for m in ("qel", "res", "dis", "coh")) + MEC.astype(int)
        chk["n_events_not_in_exactly_one_of_qel_res_dis_coh_mec"] = int(np.sum(nmode != 1))
        if chk["events_vs_full_marginal_max_rel"] > 1e-12 or chk["mec_plus_nomec_vs_full_marginal_max_rel"] > 1e-12:
            raise SystemExit(f"event sums do not reproduce the _full E_avail marginal: {chk}")
        f = ROOT.TFile.Open(out, "RECREATE")
        lab = "GENIE-CV (flux-repaired)" if gen == "genie_cv" else "GENIE+MEC (flux-repaired)"
        u3d.numpy_to_th3d(x3, None, "hXSec3D", f"{lab} d^{{3}}#sigma", e[0], e[1], e[2]).Write()
        u3d.numpy_to_th2d((x3 * np.diff(e[2])).sum(axis=2), None, "hXSec2D", f"{lab} d^{{2}}#sigma", e[0], e[1]).Write()
        u3d.numpy_to_th1d(e[0], g2r.integrate(x, e, (0,)), "hXSec_pt", f"{lab} d#sigma/dp_{{T}}").Write()
        u3d.numpy_to_th1d(e[1], g2r.integrate(x, e, (1,)), "hXSec_pz", f"{lab} d#sigma/dp_{{||}}").Write()
        u3d.numpy_to_th1d(e[2], ea, "hXSec_eavail", f"{lab} d#sigma/dE_{{avail}}").Write()
        if gen == "genie_mec":
            u3d.numpy_to_th1d(e[2], comp["nomec"], "hXSec_eavail_nomec", "non-MEC part").Write()
            u3d.numpy_to_th1d(e[2], comp["mec"], "hXSec_eavail_mec", "MEC part").Write()
            n_cc = float(sum(p["n_cc"] for p in parts))
            ROOT.TParameter("double")("nCCtotal", n_cc).Write()
            ROOT.TParameter("double")("fMEC", float(np.sum(W[MEC]) / np.sum(W))).Write()
        for m in ("qel", "res", "dis", "coh", "charm"):
            u3d.numpy_to_th1d(e[2], comp[m], f"hXSec_eavail_{m}", f"{m} part").Write()
        f.Close()
        # compare hXSec_eavail with the coordinator's committed-format file of the same product
        coord = f"{GENFIG}/{'genie_cv_xsec3d.root' if gen == 'genie_cv' else 'genie_mec_xsec3d.root'}"
        fc = ROOT.TFile.Open(coord)
        hc = fc.Get("hXSec_eavail")
        vc = np.array([hc.GetBinContent(i) for i in range(1, hc.GetNbinsX() + 1)])
        fc.Close()
        res["files"][gen] = {
            "out": gfr.file_record(out, "per-mode E_avail components on the repaired flux"),
            "from_full_product": gfr.file_record(npz, "_full product"),
            "events": [gfr.file_record(p["gst"], f"{s} events") for p, s in zip(parts, ("main", "supp"))],
            "checks": chk,
            "hXSec_eavail_vs_coordinator_file": {"file": gfr.file_record(coord, "coordinator's committed-format file"),
                                                 "bitwise_equal": bool(np.array_equal(vc, ea)),
                                                 "max_rel_diff": float(np.max(np.abs(vc - ea) / ea))},
            "hXSec_eavail": ea.tolist(), "hXSec_eavail_mec": comp["mec"].tolist(),
            "mode_components": {m: comp[m].tolist() for m in ("qel", "res", "dis", "coh", "charm")},
            "definitions": {"hXSec_eavail": "gen5d_to_rootpreds.integrate(_full, keep E_avail)",
                            "components": "sum over in-PS CC events (main sample with r(E), supplement) of the "
                                          "per-event sigma contribution of the _full product, / dE_avail",
                            "fMEC": "sigma-weighted MEC share of the in-PS events (committed file: raw count "
                                    "fraction of all CC)", "nCCtotal": "raw CC count, main + supplement"}}
    res["code"] = code_record()
    res["environment"] = gfr.environment()
    gfr.dump_json(res, f"{GENFIG}/gen5d_mode_components_files.json")
    print(json.dumps({g: {"checks": v["checks"], "vs_coord": v["hXSec_eavail_vs_coordinator_file"]["bitwise_equal"],
                          "max_rel": v["hXSec_eavail_vs_coordinator_file"]["max_rel_diff"]}
                      for g, v in res["files"].items()}, indent=1))


def cmd_mode_decomp(args):
    """Run mode_decomp_eavail.main() unchanged, with mode_counts sigma-weighted."""
    ROOT = gfr.import_root()
    g5 = gfr.load_g5(gfr.DEFAULTS["gen5d_tree"])
    sys.path.insert(0, PRODUCERS)
    import mode_decomp_eavail as md
    EA = np.asarray(md.EA, float)
    parts = [weighted_events(ROOT, g5, "genie_cv", s) for s in ("main", "supp")]
    E = np.concatenate([p["eavail"] for p in parts])
    W = np.concatenate([p["w"] for p in parts])
    FL = {m: np.concatenate([p["flags"][m] for p in parts]) for m in MODES}
    Wn = W * (W.size / W.sum())         # mean 1: the script's np.maximum(tot, 1) is then inert

    def weighted_mode_counts(gst):
        tot = np.histogram(E, EA, weights=Wn)[0]
        per = {m: np.histogram(E[FL[m]], EA, weights=Wn[FL[m]])[0] for m in MODES}
        return tot, per, int(E.size)

    md.mode_counts = weighted_mode_counts
    tot, per, _ = weighted_mode_counts(None)
    diag = {"min_weighted_tot_per_bin": float(tot.min()), "n_events": int(E.size),
            "weight_normalisation": "per-event sigma contribution x N/sum (mean 1)",
            "events": [p["gst"] for p in parts]}
    print("[wrapper] " + json.dumps(diag))
    sys.argv = ["mode_decomp_eavail.py", "--gst", parts[0]["gst"], "--cv", OUT_CV, "--data", DATA,
                "--cov", COV, "--plot", f"{GENFIG}/mode_decomp_eavail.png"]
    md.main()


KEY_LINES = ("integrated deficit", "data-CV gap", "CV=", "deficit =", "2p2h equal to",
             "fraction of the positive deficit", "CC-in-PS events used", "wrote", "[wrapper]")


def cmd_runs(args):
    """The two figure producers, before (their committed default inputs) and after (repaired)."""
    G = gfr.DEFAULTS["genie_dir"]
    py = sys.executable
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    runs = {
        "compare_mec_eavail_before": [py, f"{PRODUCERS}/compare_mec_eavail.py", "--data", DATA,
                                      "--cv", f"{G}/genie_cv_xsec3d.root", "--mec", f"{G}/genie_mec_cv_xsec3d.root",
                                      "--cov", COV, "--plot", f"{GENFIG}/compare_mec_eavail_before.png"],
        "compare_mec_eavail": [py, f"{PRODUCERS}/compare_mec_eavail.py", "--data", DATA, "--cv", OUT_CV,
                               "--mec", OUT_MEC, "--cov", COV, "--plot", f"{GENFIG}/compare_mec_eavail.png"],
        "mode_decomp_eavail_before": [py, f"{PRODUCERS}/mode_decomp_eavail.py", "--gst",
                                      f"{G}/genie_mefhc_cv_ALL.gst.root", "--cv", f"{G}/genie_cv_xsec3d.root",
                                      "--data", DATA, "--cov", COV, "--plot", f"{GENFIG}/mode_decomp_eavail_before.png"],
        "mode_decomp_eavail": [py, str(Path(__file__).resolve()), "mode-decomp"],
    }
    out = {"schema": "gen5d-fluxfix-modes-runs/v1", "created_utc": gfr.now(), "cwd": GENFIG, "runs": {}}
    for name, cmd in runs.items():
        if args.only and name not in args.only:
            continue
        log = f"{GENFIG}/{name}.log"
        r = subprocess.run(cmd, cwd=GENFIG, env=env, capture_output=True, text=True, timeout=1700)
        text = r.stdout + ("\n[stderr]\n" + r.stderr if r.stderr.strip() else "")
        open(log, "w").write(text)
        png = f"{GENFIG}/{name}.png"
        out["runs"][name] = {"argv": cmd, "returncode": r.returncode, "log": gfr.file_record(log, "stdout+stderr"),
                             "plot": gfr.file_record(png, "figure") if os.path.exists(png) else None,
                             "key_lines": [ln.strip() for ln in r.stdout.splitlines()
                                           if any(k in ln for k in KEY_LINES)],
                             "table": [ln.rstrip() for ln in r.stdout.splitlines()
                                       if ln[:4].strip().isdigit() and "[" in ln]}
        print(name, r.returncode)
        for ln in out["runs"][name]["key_lines"]:
            print("   ", ln)
    prev = f"{GENFIG}/gen5d_mode_components_runs.json"
    if args.only and os.path.exists(prev):
        old = json.load(open(prev))
        old["runs"].update(out["runs"])
        out["runs"] = old["runs"]
    out["code"] = code_record()
    out["environment"] = gfr.environment()
    gfr.dump_json(out, prev)


def cmd_receipt(args):
    runs = json.load(open(f"{GENFIG}/gen5d_mode_components_runs.json"))
    files = json.load(open(f"{GENFIG}/gen5d_mode_components_files.json"))
    ROOT = gfr.import_root()
    G = gfr.DEFAULTS["genie_dir"]
    EA = np.asarray(gfr.load_g5(gfr.DEFAULTS["gen5d_tree"]).EDGES["eavail"], float)
    dea = np.diff(EA)[:-1]
    dip = EA[1:-1] <= 0.4

    def g(path, name):
        f = ROOT.TFile.Open(path)
        h = f.Get(name)
        v = np.array([h.GetBinContent(i) for i in range(1, h.GetNbinsX() + 1)])
        f.Close()
        return v[:-1]                     # catch bin dropped, as both scripts do
    dec = {}
    for tag, cv, mec in (("before", f"{G}/genie_cv_xsec3d.root", f"{G}/genie_mec_cv_xsec3d.root"),
                         ("after", OUT_CV, OUT_MEC)):
        c, t, m, nm = g(cv, "hXSec_eavail"), g(mec, "hXSec_eavail"), g(mec, "hXSec_eavail_mec"), g(mec, "hXSec_eavail_nomec")
        dat = g(DATA, "hXSec_eavail")
        dec[tag] = {"cv_file": cv, "mec_file": mec,
                    "integral_cv": float((c * dea).sum()), "integral_mec_file": float((t * dea).sum()),
                    "integral_mec_only": float((m * dea).sum()), "integral_nonmec_part": float((nm * dea).sum()),
                    "nonmec_part_over_cv": float((nm * dea).sum() / (c * dea).sum()),
                    "script_MEC_added_(mec_file_minus_cv)": float(((t - c) * dea).sum()),
                    "integral_data_minus_cv": float(((dat - c) * dea).sum()),
                    "mec_only_over_integrated_deficit": float((m * dea).sum() / ((dat - c) * dea).sum()),
                    "dip_mec_only": float((m * dea)[dip].sum()),
                    "dip_script_MEC_added": float(((t - c) * dea)[dip].sum()),
                    "dip_data_minus_cv": float(((dat - c) * dea)[dip].sum()),
                    "dip_mec_only_over_gap": float((m * dea)[dip].sum() / ((dat - c) * dea)[dip].sum())}
    dec["note"] = ("compare_mec_eavail.py's 'MEC added' is hXSec_eavail(MEC file) - hXSec_eavail(CV file); it equals "
                   "the MEC-only component only when the two files' non-MEC parts agree (nonmec_part_over_cv = 1)")
    rec = {"schema": "gen5d-fluxfix-3-receipt/v1", "created_utc": gfr.now(),
           "mec_decomposition_catch_bin_dropped": dec,
           "created_by": f"{Path(__file__).resolve()} receipt (machine-generated)",
           "output_dir": GENFIG, "code": code_record(), "files": files["files"], "runs": runs,
           "environment": gfr.environment(), "argv": sys.argv}
    bad = gfs.bare_names(rec)
    if bad:
        raise SystemExit(f"bare filenames in receipt: {bad}")
    p = os.path.join(gfs.OUT, "gen5d-fluxfix-3.json")
    gfr.dump_json(rec, p)
    print(p, gfr.sha256(p))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["files", "runs", "mode-decomp", "receipt"])
    ap.add_argument("--only", nargs="*", default=None)
    args = ap.parse_args()
    {"files": cmd_files, "runs": cmd_runs, "mode-decomp": cmd_mode_decomp,
     "receipt": cmd_receipt}[args.command](args)


if __name__ == "__main__":
    main()
