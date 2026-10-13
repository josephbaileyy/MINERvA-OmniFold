#!/usr/bin/env python3
"""P1 no-op and plumbing controls for driver_p1.py (login node; no unfold is run).

  python test_noop.py --d2 D2 --omnifile OMNI --mcfile FLUX --workdir DIR --report REPORT.json

D2 holds the production driver unfold_2d_omnifold_unbinned.py (sha256 74a4ed69...) and driver_p1.py side by
side (and uq/reported_cells.py). Each configuration runs the driver's own main() in a fresh subprocess, up to
the OmniFold call: a stand-in `omnifold` module records every array main() passes to ohf.omnifold, plus main()'s
locals at that point (factor vectors, histograms, loader outputs), as sha256 digests, then stops the run.
Bitwise equality is digest equality of the raw bytes, dtype and shape.

Configurations (all: --iters 5 --use-weights --estimator lgbm --seed 42, CV purity path; bootstrap seed S=7):
  prod_cv    production driver, no bootstrap (the central path)
  p1_cv      driver_p1, no new option
  prod_both  production driver, --bootstrap-seed S (existing 'both' mode)
  p1_both    driver_p1, --bootstrap-seed S
  p1_unit    driver_p1, --bootstrap-seed S --bootstrap-streams three --unit-factors
  p1_bkg     driver_p1, --bootstrap-seed S --bootstrap-streams bkg
  p1_three   driver_p1, --bootstrap-seed S --bootstrap-streams three

Controls:
  C0 refusals: the new options refuse --closure, negweight modes, --universe, a missing --bootstrap-seed, and
     --unit-factors without three|bkg (in-process, before any file is opened).
  C1 options off: p1_cv == prod_cv and p1_both == prod_both on every recorded array and histogram; the
     background loader with return_fill_rows=False/True returns the production arrays and histogram bit for
     bit, and a refill of its recorded rows with b == 1 reproduces hBkgReco2D bit for bit.
  C2 b == 1: p1_unit == prod_cv on every recorded array (OmniFold inputs, loaders, completeness weights,
     production histograms); D*, B* and the starred training target equal hDataReco2D, hBkgReco2D and
     hMeasTrain2D; the purity equals the central measured weights; all three factor vectors are 1.
  C3 bkg arm: against prod_cv only B*, the purity, the starred training target and the measured weights
     differ (each must differ); data and MC factors are all 1; b_bkg is the declared draw; D*, B*, purity and
     measured weights are recomputed independently in the worker.
  C4 pairing: p1_three has the same data and MC factors, MC weights and kinematics as prod_both; its B* equals
     p1_bkg's (same seed); its measured weights are the recomputed purity(D*, B*) x b_data.
Exit 0 iff every control passes.
"""
import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time
import types

import numpy as np

S = 7
CONFIGS = {
    "prod_cv": ("prod", []),
    "p1_cv": ("p1", []),
    "prod_both": ("prod", ["--bootstrap-seed", str(S)]),
    "p1_both": ("p1", ["--bootstrap-seed", str(S)]),
    "p1_unit": ("p1", ["--bootstrap-seed", str(S), "--bootstrap-streams", "three", "--unit-factors"]),
    "p1_bkg": ("p1", ["--bootstrap-seed", str(S), "--bootstrap-streams", "bkg"]),
    "p1_three": ("p1", ["--bootstrap-seed", str(S), "--bootstrap-streams", "three"]),
}
PROD_HISTS = ("hDataReco2D", "hBkgReco2D", "hMeasSub2D", "hMeasTrain2D")
STAR_HISTS = ("hDataRecoStar2D", "hBkgRecoStar2D", "hMeasTrainStar2D")
STAR_OF = {"hDataRecoStar2D": "hDataReco2D", "hBkgRecoStar2D": "hBkgReco2D",
           "hMeasTrainStar2D": "hMeasTrain2D"}


def sha_file(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def dig(a):
    a = np.ascontiguousarray(np.asarray(a))
    return f"{a.dtype.str}{list(a.shape)}:{hashlib.sha256(a.tobytes()).hexdigest()}"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def hist_arrays(h):
    n = h.GetNcells()
    c = np.frombuffer(h.GetArray(), dtype=np.float64, count=n).copy()
    w2 = np.frombuffer(h.GetSumw2().GetArray(), dtype=np.float64, count=n).copy()
    return c, w2


def global_bins(h, xs, ys):
    """ROOT's own bin lookup (the one TH2D::Fill uses), one global bin per point."""
    ax, ay = h.GetXaxis(), h.GetYaxis()
    nx2 = h.GetNbinsX() + 2
    return np.fromiter((ax.FindFixBin(float(x)) + nx2 * ay.FindFixBin(float(y)) for x, y in zip(xs, ys)),
                       dtype=np.int64, count=len(xs))


class _Stop(Exception):
    pass


def worker(a):
    """Run one configuration's main() up to ohf.omnifold; write digests + checks to a JSON."""
    import ROOT
    ROOT.gROOT.SetBatch(True)
    who, extra = CONFIGS[a.worker]
    path = os.path.join(a.d2, "unfold_2d_omnifold_unbinned.py" if who == "prod" else "driver_p1.py")
    rec = {"config": a.worker, "driver": path, "driver_sha256": sha_file(path), "argv_extra": extra}

    def fake_omnifold(MCgen, MCreco, measured, pass_reco, pass_truth, meas_mask, iters, **kw):
        loc = sys._getframe(1).f_locals
        d = {}
        for k, v in (("MCgen", MCgen), ("MCreco", MCreco), ("measured", measured), ("pass_reco", pass_reco),
                     ("pass_truth", pass_truth), ("meas_mask", meas_mask)):
            d["of." + k] = dig(v)
        for k in ("MCgen_weights", "MCreco_weights", "measured_weights"):
            d["of." + k] = dig(kw[k])
        for k in ("meas_pt", "meas_pz", "bkg_reco_pt", "bkg_reco_pz", "bkg_reco_w"):
            d[k] = dig(loc[k])
        for k, v in loc["sig"].items():
            d["sig." + k] = dig(v)
        for k, v in (loc["truth_denom"] or {}).items():
            d["td." + k] = dig(v)
        wcv = loc.get("w_truth_cv")
        d["completeness_w_truth"] = dig(wcv if wcv is not None else loc["sig"]["w_truth"])
        hists, small = {}, {}
        for name in PROD_HISTS + STAR_HISTS:
            if name in loc:
                c, w2 = hist_arrays(loc[name])
                d[f"h.{name}.content"], d[f"h.{name}.sumw2"] = dig(c), dig(w2)
                hists[name] = c
                small[f"{name}.integral_in_grid"] = float(loc[name].Integral())
        for k in ("b_data", "b_truth", "b_bkg", "p1_purity"):
            if k in loc:
                d[k] = dig(loc[k])
                small[f"{k}.sum"] = float(np.sum(loc[k]))
                small[f"{k}.n"] = int(np.size(loc[k]))
                if k.startswith("b_"):
                    small[f"{k}.all_one"] = bool(np.all(loc[k] == 1.0))
        rows = loc.get("p1_bkg_rows")
        if rows is not None:
            for k, v in rows.items():
                d["p1rows." + k] = dig(v)
        checks = {}
        if "b_bkg" in loc:  # P1 path: independent recomputation of D*, B*, purity, measured weights
            b_data, b_bkg, pur = loc["b_data"], loc["b_bkg"], loc["p1_purity"]
            n_bkg = loc["t_bkg"].GetEntries()
            if not loc["args"].unit_factors:
                want = np.random.default_rng(S + 20_000_000).poisson(1.0, n_bkg).astype(float)
                checks["b_bkg_is_declared_draw"] = bool(np.array_equal(b_bkg, want))
            checks["b_bkg_n_equals_tree_entries"] = bool(b_bkg.size == n_bkg)
            hD, hB = loc["hDataRecoStar2D"], loc["hBkgRecoStar2D"]
            ncell = hD.GetNcells()
            g_data = global_bins(hD, loc["meas_pt"], loc["meas_pz"])
            d_sum = np.bincount(g_data, weights=b_data, minlength=ncell)
            checks["Dstar_equals_sum_b_data"] = bool(np.array_equal(d_sum, hists["hDataRecoStar2D"]))
            g_bkg = global_bins(hB, rows["pt"], rows["pz"])
            b_sum = np.bincount(g_bkg, weights=b_bkg[rows["entry"]] * rows["w_pot"], minlength=ncell)
            hb = hists["hBkgRecoStar2D"]
            rel = np.abs(b_sum - hb) / np.maximum(np.abs(hb), 1e-300)
            checks["Bstar_max_rel_diff_vs_bincount"] = float(rel[np.abs(hb) > 0].max(initial=0.0))
            checks["Bstar_zero_cells_agree"] = bool(np.array_equal(b_sum == 0, hb == 0))
            checks["Bstar_matches_bincount_1e-12"] = bool(checks["Bstar_max_rel_diff_vs_bincount"] <= 1e-12
                                                          and checks["Bstar_zero_cells_agree"])
            dc, bc = hists["hDataRecoStar2D"][g_data], hb[g_data]
            with np.errstate(divide="ignore", invalid="ignore"):
                p = np.where(dc > 0, np.maximum(0.0, dc - bc) / dc, 0.0)
            checks["purity_recomputed_bitwise"] = bool(np.array_equal(p, pur))
            checks["measured_equals_purity_x_b_data_bitwise"] = bool(
                np.array_equal(kw["measured_weights"], pur * b_data))
            checks["n_bkg_fill_rows"] = int(rows["entry"].size)
            checks["n_bkg_fill_rows_outside_grid"] = int(np.sum(
                (rows["pt"] < hB.GetXaxis().GetXmin()) | (rows["pt"] >= hB.GetXaxis().GetXmax())
                | (rows["pz"] < hB.GetYaxis().GetXmin()) | (rows["pz"] >= hB.GetYaxis().GetXmax())))
            checks["n_cells_Bstar_differs_from_B"] = int(np.sum(hb != hist_arrays(loc["hBkgReco2D"])[0]))
        rec.update(digests=d, small=small, checks=checks,
                   n_fakes=int(loc["n_fakes"]), n_entries={"data_rows": int(np.size(loc["meas_pt"])),
                                                         "mc_background": int(loc["t_bkg"].GetEntries()),
                                                         "mc_signal_rows": int(loc["sig"]["w_truth"].size)})
        raise _Stop

    fake = types.ModuleType("omnifold")
    fake.OmniFold_helper_functions = types.SimpleNamespace(omnifold=fake_omnifold)
    sys.modules["omnifold"] = fake
    mod = load(f"drv_{a.worker}", path)
    sys.argv = [path, "--omnifile", a.omnifile, "--mcfile", a.mcfile, "--iters", "5", "--use-weights",
                "--estimator", "lgbm", "--seed", "42", "--out", os.path.join(a.workdir, "never_written.root"),
                *extra]
    t0 = time.time()
    try:
        mod.main()
        rec["error"] = "main() returned without reaching ohf.omnifold"
    except _Stop:
        rec["seconds_to_omnifold"] = round(time.time() - t0, 1)
    with open(os.path.join(a.workdir, f"{a.worker}.json"), "w") as fh:
        json.dump(rec, fh, indent=1, sort_keys=True)
    return 0 if "error" not in rec else 2


def refusals(d2):
    """C0: each forbidden combination must SystemExit before the input file is opened."""
    diag = load("p1_refusal", os.path.join(d2, "driver_p1.py"))
    base = ["x", "--omnifile", "/nonexistent.root", "--use-weights"]
    cases = {
        "three_without_bootstrap_seed": ["--bootstrap-streams", "three"],
        "three_with_closure": ["--bootstrap-seed", "1", "--bootstrap-streams", "three", "--closure"],
        "bkg_with_negweight": ["--bootstrap-seed", "1", "--bootstrap-streams", "bkg", "--bkg-mode", "negweight"],
        "three_with_negweight_refined": ["--bootstrap-seed", "1", "--bootstrap-streams", "three",
                                         "--bkg-mode", "negweight-refined"],
        "three_with_universe": ["--bootstrap-seed", "1", "--bootstrap-streams", "three", "--universe", "MaRES:0"],
        "unit_factors_without_p1_stream": ["--bootstrap-seed", "1", "--unit-factors"],
    }
    out = {}
    for k, extra in cases.items():
        sys.argv = base + extra
        try:
            diag.main()
            out[k] = {"refused": False, "msg": "main() returned"}
        except SystemExit as e:
            msg = str(e)
            out[k] = {"refused": "P1" in msg or "--unit-factors" in msg, "msg": msg}
        except Exception as e:  # opening the file means the guard did not fire
            out[k] = {"refused": False, "msg": f"{type(e).__name__}: {e}"}
    return out


def loader_level(d2, omni):
    """C1 at the background loader: off == production; rows reproduce hBkgReco2D at b == 1."""
    import inspect
    import ROOT
    ROOT.gROOT.SetBatch(True)
    prod = load("prod_ll", os.path.join(d2, "unfold_2d_omnifold_unbinned.py"))
    diag = load("p1_ll", os.path.join(d2, "driver_p1.py"))
    f = ROOT.TFile.Open(omni)
    data_pot, mc_pot, pot = prod.get_pot_scales(f)
    lim = dict(pt_lo=prod.PT_EDGES[0], pt_hi=prod.PT_EDGES[-1], pz_lo=prod.PZ_EDGES[0], pz_hi=prod.PZ_EDGES[-1])
    res = {}

    def run(mod, name, **kw):
        h = prod.make_th2d(name, name, prod.PT_EDGES, prod.PZ_EDGES)
        out = mod.fill_bkg_reco_2d(f.Get("mc_background"), h, pot, **lim, **kw)
        return out, h

    (r0, h0) = run(prod, "h_prod")
    (r1, h1) = run(diag, "h_off")
    (r2, h2) = run(diag, "h_rows", return_fill_rows=True)
    c0 = hist_arrays(h0)
    res["off_returns_3_arrays"] = len(r1) == 3
    res["off_arrays_bitwise"] = all(np.array_equal(x, y) for x, y in zip(r0, r1))
    res["off_hist_bitwise"] = all(np.array_equal(x, y) for x, y in zip(c0, hist_arrays(h1)))
    res["rows_first3_bitwise"] = all(np.array_equal(x, y) for x, y in zip(r0, r2[:3]))
    res["rows_hist_bitwise"] = all(np.array_equal(x, y) for x, y in zip(c0, hist_arrays(h2)))
    rows = r2[3]
    n_ent = f.Get("mc_background").GetEntries()
    ones = np.ones(n_ent)
    hr = diag.p1_refill_bkg_2d("h_refill", "h", rows, ones, prod.PT_EDGES, prod.PZ_EDGES)
    res["refill_b1_hist_bitwise"] = all(np.array_equal(x, y) for x, y in zip(c0, hist_arrays(hr)))
    e = rows["entry"]
    res["n_entries"] = int(n_ent)
    res["n_fill_rows"] = int(e.size)
    res["n_rows_returned_in_window"] = int(r0[0].size)
    res["n_fill_rows_outside_window"] = int(e.size - r0[0].size)
    res["entries_strictly_increasing"] = bool(np.all(np.diff(e) > 0)) and bool(e.min() >= 0 and e.max() < n_ent)
    res["hBkgReco2D_integral_in_grid"] = float(h0.Integral())
    res["hBkgReco2D_sum_incl_flow"] = float(c0[0].sum())
    res["sum_w_pot_rows"] = float(rows["w_pot"].sum())
    f.Close()
    same_src = {}
    for fn in ("fill_data_reco_2d", "collect_signal_arrays_2d", "collect_truth_denom_arrays",
               "build_measured_training_2d", "compute_omnifold_completeness_2d", "make_th2d"):
        same_src[fn] = inspect.getsource(getattr(prod, fn)) == inspect.getsource(getattr(diag, fn))
    res["unchanged_function_source_identical"] = same_src
    res["PASS"] = bool(res["off_returns_3_arrays"] and res["off_arrays_bitwise"] and res["off_hist_bitwise"]
                       and res["rows_first3_bitwise"] and res["rows_hist_bitwise"]
                       and res["refill_b1_hist_bitwise"] and res["entries_strictly_increasing"]
                       and all(same_src.values()))
    return res


def diff_keys(a, b, keys=None):
    keys = sorted(set(a) & set(b)) if keys is None else keys
    return sorted(k for k in keys if a.get(k) != b.get(k))


def parent(a):
    os.makedirs(a.workdir, exist_ok=True)
    rep = {"schema": "p1-test-noop/1", "omnifile": a.omnifile, "omnifile_bytes": os.path.getsize(a.omnifile),
           "mcfile": a.mcfile, "bootstrap_seed": S, "host": os.uname().nodename,
           "drivers": {n: {"path": os.path.join(a.d2, n), "sha256": sha_file(os.path.join(a.d2, n))}
                       for n in ("unfold_2d_omnifold_unbinned.py", "driver_p1.py")},
           "test_noop_sha256": sha_file(os.path.abspath(__file__)),
           "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    if a.omnifile_sha256:
        rep["omnifile_sha256_given"] = a.omnifile_sha256
    rep["C0_refusals"] = refusals(a.d2)
    rep["C0_PASS"] = all(v["refused"] for v in rep["C0_refusals"].values())
    rep["C1_loader_level"] = loader_level(a.d2, a.omnifile)

    procs = {}
    names = list(CONFIGS)
    runs = {}
    while names or procs:
        while names and len(procs) < a.jobs:
            n = names.pop(0)
            log = open(os.path.join(a.workdir, f"{n}.txt"), "w")
            cmd = [sys.executable, os.path.abspath(__file__), "--worker", n, "--d2", a.d2,
                   "--omnifile", a.omnifile, "--mcfile", a.mcfile, "--workdir", a.workdir]
            procs[n] = (subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT), log)
        time.sleep(5)
        for n in list(procs):
            p, log = procs[n]
            if p.poll() is not None:
                log.close()
                runs[n] = {"rc": p.returncode}
                del procs[n]
    rec = {}
    for n in CONFIGS:
        jp = os.path.join(a.workdir, f"{n}.json")
        rec[n] = json.load(open(jp)) if os.path.exists(jp) else {"error": f"no record (rc {runs[n]['rc']})"}
        runs[n].update(seconds_to_omnifold=rec[n].get("seconds_to_omnifold"), error=rec[n].get("error"),
                       driver_sha256=rec[n].get("driver_sha256"), n_fakes=rec[n].get("n_fakes"),
                       n_entries=rec[n].get("n_entries"))
    rep["runs"] = runs
    if any(r.get("error") or r["rc"] != 0 for r in runs.values()):
        rep["PASS"] = False
        rep["why"] = "a worker failed"
        return rep
    D = {n: rec[n]["digests"] for n in CONFIGS}
    Sm = {n: rec[n]["small"] for n in CONFIGS}
    prod_keys = sorted(D["prod_cv"])

    # C1
    c1 = {"p1_cv_vs_prod_cv_differing": diff_keys(D["prod_cv"], D["p1_cv"]),
          "p1_cv_extra_keys": sorted(set(D["p1_cv"]) - set(D["prod_cv"])),
          "p1_both_vs_prod_both_differing": diff_keys(D["prod_both"], D["p1_both"]),
          "p1_both_extra_keys": sorted(set(D["p1_both"]) - set(D["prod_both"])),
          "n_keys_compared_cv": len(prod_keys), "n_keys_compared_both": len(D["prod_both"])}
    c1["PASS"] = bool(rep["C1_loader_level"]["PASS"] and not c1["p1_cv_vs_prod_cv_differing"]
                      and not c1["p1_cv_extra_keys"] and not c1["p1_both_vs_prod_both_differing"]
                      and not c1["p1_both_extra_keys"])
    rep["C1"] = c1

    # C2
    u = D["p1_unit"]
    star_eq = {s: (u.get(f"h.{s}.content") == u.get(f"h.{p}.content")
                   and u.get(f"h.{s}.sumw2") == u.get(f"h.{p}.sumw2")) for s, p in STAR_OF.items()}
    c2 = {"p1_unit_vs_prod_cv_differing": diff_keys(D["prod_cv"], u, prod_keys),
          "star_hists_equal_production_hists": star_eq,
          "purity_equals_central_measured_weights": u.get("p1_purity") == D["prod_cv"]["of.measured_weights"],
          "factors_all_one": {k: Sm["p1_unit"].get(f"{k}.all_one") for k in ("b_data", "b_truth", "b_bkg")},
          "n_keys_compared": len(prod_keys)}
    c2["PASS"] = bool(not c2["p1_unit_vs_prod_cv_differing"] and all(star_eq.values())
                      and c2["purity_equals_central_measured_weights"] and all(c2["factors_all_one"].values()))
    rep["C2"] = c2

    # C3
    bk = D["p1_bkg"]
    ext = dict(D["prod_cv"])
    for s, p in STAR_OF.items():  # compare each starred hist with its production counterpart
        ext[f"h.{s}.content"], ext[f"h.{s}.sumw2"] = ext[f"h.{p}.content"], ext[f"h.{p}.sumw2"]
    ext["p1_purity"] = ext["of.measured_weights"]
    keys3 = sorted(set(ext) & set(bk))
    differ = diff_keys(ext, bk, keys3)
    allowed = {"of.measured_weights", "p1_purity", "h.hBkgRecoStar2D.content", "h.hBkgRecoStar2D.sumw2",
               "h.hMeasTrainStar2D.content", "h.hMeasTrainStar2D.sumw2"}
    must = {"of.measured_weights", "p1_purity", "h.hBkgRecoStar2D.content"}
    ch3 = rec["p1_bkg"]["checks"]
    c3 = {"differing_vs_prod_cv": differ, "unexpected_differences": sorted(set(differ) - allowed),
          "required_differences_missing": sorted(must - set(differ)),
          "data_mc_factors_all_one": {k: Sm["p1_bkg"].get(f"{k}.all_one") for k in ("b_data", "b_truth")},
          "b_bkg_sum": Sm["p1_bkg"].get("b_bkg.sum"), "b_bkg_n": Sm["p1_bkg"].get("b_bkg.n"),
          "Bstar_integral_in_grid": Sm["p1_bkg"].get("hBkgRecoStar2D.integral_in_grid"),
          "B_integral_in_grid": Sm["p1_bkg"].get("hBkgReco2D.integral_in_grid"),
          "worker_checks": ch3, "n_keys_compared": len(keys3)}
    wc3 = [ch3[k] for k in ("b_bkg_is_declared_draw", "b_bkg_n_equals_tree_entries", "Dstar_equals_sum_b_data",
                            "Bstar_matches_bincount_1e-12", "purity_recomputed_bitwise",
                            "measured_equals_purity_x_b_data_bitwise")]
    c3["PASS"] = bool(not c3["unexpected_differences"] and not c3["required_differences_missing"]
                      and all(c3["data_mc_factors_all_one"].values()) and all(wc3))
    rep["C3"] = c3

    # C4
    th = D["p1_three"]
    shared = [k for k in D["prod_both"] if k in th and (k.startswith(("of.MC", "of.pass", "of.measured", "sig.",
                                                                        "td.", "meas_", "bkg_reco_", "h.h"))
                                                         or k in ("b_data", "b_truth", "completeness_w_truth"))
              and k not in ("of.measured_weights",)]
    ch4 = rec["p1_three"]["checks"]
    c4 = {"vs_prod_both_differing_shared": diff_keys(D["prod_both"], th, shared),
          "factors_paired": {k: th.get(k) == D["prod_both"].get(k) for k in ("b_data", "b_truth")},
          "measured_weights_differ_from_fixed_purity": th["of.measured_weights"] != D["prod_both"]["of.measured_weights"],
          "Bstar_equals_bkg_arm": th.get("h.hBkgRecoStar2D.content") == bk.get("h.hBkgRecoStar2D.content"),
          "b_bkg_equals_bkg_arm": th.get("b_bkg") == bk.get("b_bkg"),
          "worker_checks": ch4, "n_shared_keys": len(shared)}
    wc4 = [ch4[k] for k in ("b_bkg_is_declared_draw", "Dstar_equals_sum_b_data", "Bstar_matches_bincount_1e-12",
                            "purity_recomputed_bitwise", "measured_equals_purity_x_b_data_bitwise")]
    c4["PASS"] = bool(not c4["vs_prod_both_differing_shared"] and all(c4["factors_paired"].values())
                      and c4["measured_weights_differ_from_fixed_purity"] and c4["Bstar_equals_bkg_arm"]
                      and c4["b_bkg_equals_bkg_arm"] and all(wc4))
    rep["C4"] = c4
    rep["n_fakes_all_zero"] = all(rec[n]["n_fakes"] == 0 for n in CONFIGS)
    rep["PASS"] = bool(rep["C0_PASS"] and c1["PASS"] and c2["PASS"] and c3["PASS"] and c4["PASS"]
                       and rep["n_fakes_all_zero"])
    rep["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    return rep


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--d2", required=True)
    ap.add_argument("--omnifile", required=True)
    ap.add_argument("--mcfile", required=True)
    ap.add_argument("--workdir", required=True)
    ap.add_argument("--report")
    ap.add_argument("--omnifile-sha256", default=None, help="recorded only (hash it separately)")
    ap.add_argument("--jobs", type=int, default=2, help="workers at once (memory: ~1 config each)")
    ap.add_argument("--worker", choices=list(CONFIGS))
    a = ap.parse_args()
    sys.path.insert(0, a.d2)
    if a.worker:
        return worker(a)
    rep = parent(a)
    with open(a.report, "w") as fh:
        json.dump(rep, fh, indent=1, sort_keys=True)
    print(json.dumps({k: rep.get(k) for k in ("C0_PASS", "PASS", "why")}, indent=1))
    for c in ("C1", "C2", "C3", "C4"):
        if c in rep:
            print(c, rep[c]["PASS"])
    return 0 if rep["PASS"] else 2


if __name__ == "__main__":
    sys.exit(main())
