#!/usr/bin/env python3
"""PTMC units (PTMC-DECLARATION.md sections 2.1-2.3): one in-process run of E_R's driver per unit, in the deploy tree
built by make_tree.sh (M's grid, the OOFVC option, PTMC's bootstrap hunk). The driver's own OmniFold call is
observed, not replaced; inside it, before OmniFold runs, IBU (REF-C2C1's binned_problem and roounfold_bayes) is solved
on the very arrays OmniFold receives. The unit's hXSec2D is OmniFold's; IBU's cross sections come from the driver's
recorded extraction (ref_c2c1.xsec_at_every_k) and are written to the unit's npz.

  python3 ptmc_run.py --tree DEPLOY --rows ROWS.npz --rows-sha256 SHA --join-record JOIN.json --out OUT
                      --unit p_off_c|p_R_c|p_off_b{1..5}|p_R_b{1..200} [--unit ...]
Exit 0 only if every unit's controls pass; a refused precondition is 4, a failed control 6.

MEASURES: one driver run per unit. CANNOT AUTHORIZE: a reading (ptmc_score.py applies the declared ones) or a claim.
"""
from __future__ import annotations

import argparse
import contextlib
import copy
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path
from unittest import mock

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ptmc_lib as P  # noqa: E402

RC_GATE, RC_CONTROL = 4, 6
MINERVA_ARGV = ["--signal-convention", "minerva", "--oofvc-rows"]
UNIT_RE = re.compile(r"^p_(off|R)_(c|b(\d+))$")
SEEDS = {"off": range(1, 6), "R": range(1, 201)}
RTOL = {"fill": 1e-9, "roo": 1e-9, "sim": 1e-9, "pair_y": 1e-9, "comp": 1e-12}
# the declared inputs (PTMC-DECLARATION.md section 1): r3's rows file and join record, pinned here, never taken from
# the caller (codex r1 #10); the fixture tests patch this dict
PINS = {"rows": "cbf34bd8cad0f4978dc1aea22713eb5057bf521118dc7ce8d10b93b30defcb03",
        "join": "13674f6d0c12bbb7c7ba133346940976bada2c765585ecb4e78593ec63521a4b"}


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        while block := fh.read(1 << 24):
            h.update(block)
    return h.hexdigest()


def parse_unit(name: str) -> tuple[str, int | None]:
    m = UNIT_RE.match(name)
    if not m:
        raise ValueError(f"unknown unit {name!r}")
    conv, b = m.group(1), (int(m.group(3)) if m.group(3) else None)
    if b is not None and b not in SEEDS[conv]:
        raise ValueError(f"unit {name}: seed {b} is outside the declared set for {conv}")
    return conv, b


def import_runner(tree: Path):
    sys.path.insert(0, str(tree / "2d-unfolding" / "ref_c2c1"))
    import ref_c2c1 as C
    if Path(C.__file__).resolve().parent != (tree / "2d-unfolding" / "ref_c2c1").resolve():
        raise RuntimeError(f"ref_c2c1 resolved outside the deploy tree: {C.__file__}")
    return C


def global_index_fn(tree: Path):
    sys.path.insert(0, str(tree / "2d-unfolding" / "oofvc"))
    import oofvc_lib as L
    return L.global_index


def run_paired(C, driver, ohf, argv, out_root: Path, ks, unfolder, staging: Path) -> dict:
    """One driver main() with the paired seam and the capture wrappers; returns the capture."""
    cap = C.Capture()
    pt_e, pz_e = np.asarray(driver.PT_EDGES, float), np.asarray(driver.PZ_EDGES, float)
    real = {n: getattr(driver, n) for n in ("extract_cross_section_2d", "compute_omnifold_completeness_2d",
                                            "collect_signal_arrays_2d", "fill_bkg_reco_2d", "re2_injected_entries",
                                            "refine_stay_positive", "p1_draw_bkg_factors", "fill_data_reco_2d",
                                            "collect_truth_denom_arrays")}
    real_omnifold = ohf.omnifold

    def extract(hUnfold, *a, **k):
        cap.setdefault("extract", (a, k))
        return real["extract_cross_section_2d"](hUnfold, *a, **k)

    def completeness(*a, **k):
        out = real["compute_omnifold_completeness_2d"](*a, **k)
        cap.setdefault("completeness_calls", []).append(True)
        return out

    def loader(*a, **k):
        sig = real["collect_signal_arrays_2d"](*a, **k)
        cap["sig_cv"] = {key: (np.array(v, copy=True) if isinstance(v, np.ndarray) else copy.deepcopy(v))
                         for key, v in sig.items()}
        return sig

    def fill_bkg(*a, **k):
        out = real["fill_bkg_reco_2d"](*a, **k)
        cap["bkg_cv"] = {"pt": np.array(out[0], float, copy=True), "pz": np.array(out[1], float, copy=True),
                         "w": np.array(out[2], float, copy=True)}
        if len(out) > 3:  # the fill rows (three-stream replicas only)
            cap["fill_rows"] = {kk: np.array(v, copy=True) for kk, v in out[3].items()}
        return out

    def fill_data(*a, **k):
        out = real["fill_data_reco_2d"](*a, **k)
        cap["data_cv"] = {"pt": np.array(out[0], float, copy=True), "pz": np.array(out[1], float, copy=True)}
        return out

    def truth_denom(*a, **k):
        out = real["collect_truth_denom_arrays"](*a, **k)
        cap["truth_denom"] = {kk: np.array(v, copy=True) for kk, v in out.items()}
        return out

    def injected(*a, **k):
        out = real["re2_injected_entries"](*a, **k)
        cap["inj_entries"] = np.array(out, dtype=np.int64, copy=True)
        return out

    def draw_bkg(seed, n_entries):
        cap["n_bkg_entries"] = int(n_entries)
        return real["p1_draw_bkg_factors"](seed, n_entries)

    def refine(feat, signed_w, *a, **k):
        cap["signed_w"] = np.array(signed_w, dtype=float, copy=True)
        cap["signed_feat"] = np.array(feat, dtype=float, copy=True)
        out = real["refine_stay_positive"](feat, signed_w, *a, **k)
        cap["refined_w"] = np.array(out[0], copy=True)  # the original dtype (C-REFINE compares digests)
        return out

    def paired(MCgen, MCreco, measured, pr, ptm, mpr, iters, MCgen_weights=None, MCreco_weights=None,
               measured_weights=None, **k):
        arrays = (MCgen, MCreco, measured, pr, ptm, mpr, MCgen_weights, MCreco_weights, measured_weights)
        cap["digest_ibu"] = P.digest(*arrays)
        T, M, y, t = C.binned_problem(np.asarray(MCgen), np.asarray(MCreco), np.asarray(measured), pr, ptm,
                                      MCgen_weights, MCreco_weights, measured_weights, driver.PT_EDGES,
                                      driver.PZ_EDGES)
        traj = unfolder(M, T, y, ks)
        pt_mask = np.asarray(ptm, bool)
        meas = np.asarray(measured, float)
        mw = np.asarray(measured_weights, float)
        inside = ((meas[:, 0] >= pt_e[0]) & (meas[:, 0] < pt_e[-1]) & (meas[:, 1] >= pz_e[0])
                  & (meas[:, 1] < pz_e[-1]))  # ROOT's cells: a value on the last upper edge is overflow
        y_np, _, _ = np.histogram2d(meas[inside, 0], meas[inside, 1], bins=[pt_e, pz_e], weights=mw[inside])
        cap.update(T=T, M=M, y=y, traj=traj, tin=t[pt_mask], w_in=np.asarray(MCgen_weights, float)[pt_mask],
                   y_np=y_np.reshape(-1), w_truth_seen=np.array(MCgen_weights, float, copy=True),
                   w_reco_seen=np.array(MCreco_weights, float, copy=True), measured_weights=mw.copy(),
                   seam={"MCgen": np.array(MCgen, copy=True), "MCreco": np.array(MCreco, copy=True),
                         "pass_reco": np.array(pr, copy=True), "pass_truth": np.array(ptm, copy=True),
                         "measured_pass_reco": np.array(mpr, copy=True), "n_measured": int(meas.shape[0]),
                         "measured_weights_raw": np.array(measured_weights, copy=True)})
        cap["digest_omnifold"] = P.digest(*arrays)
        return real_omnifold(MCgen, MCreco, measured, pr, ptm, mpr, iters, MCgen_weights=MCgen_weights,
                             MCreco_weights=MCreco_weights, measured_weights=measured_weights, **k)

    patches = [mock.patch.object(driver, "extract_cross_section_2d", extract),
               mock.patch.object(driver, "compute_omnifold_completeness_2d", completeness),
               mock.patch.object(driver, "collect_signal_arrays_2d", loader),
               mock.patch.object(driver, "fill_bkg_reco_2d", fill_bkg),
               mock.patch.object(driver, "fill_data_reco_2d", fill_data),
               mock.patch.object(driver, "collect_truth_denom_arrays", truth_denom),
               mock.patch.object(driver, "re2_injected_entries", injected),
               mock.patch.object(driver, "refine_stay_positive", refine),
               mock.patch.object(driver, "p1_draw_bkg_factors", draw_bkg),
               mock.patch.object(ohf, "omnifold", staticmethod(paired))]
    patches += C.recording_lightgbm(cap, None)
    patches.append(C.tfile_guard((staging,), (Path(out_root).resolve().parent,),
                                 "the driver (outside the staging root)"))
    saved = sys.argv
    with contextlib.ExitStack() as stack:
        for p in patches:
            stack.enter_context(p)
        sys.argv = ["re2_driver.py", *argv, "--out", str(out_root)]
        try:
            driver.main()
        finally:
            sys.argv = saved
    cap["real_extract"] = real["extract_cross_section_2d"]
    cap["ptmc_record"] = copy.deepcopy(getattr(driver, "PTMC_RECORD", {}))
    return cap


def read_hist(C, driver, root: Path, name: str, allowed) -> np.ndarray:
    if not any(C.under(root, Path(r).resolve()) for r in allowed):
        raise C.GateFailure(f"{root} is outside {[str(r) for r in allowed]}")
    import ROOT
    f = ROOT.TFile.Open(str(root))
    v = C.th2_vector(f.Get(name), len(driver.PT_EDGES) - 1, len(driver.PZ_EDGES) - 1)
    f.Close()
    return v


def truth_sums(cap, gidx, conv: str) -> dict:
    """The CV truth-cell sums the premise and the completeness use: all truth-passing signal rows, and the original
    rows (all but the appended tail under R)."""
    sig = cap["sig_cv"]
    n = sig["w_truth"].shape[0]
    app = np.asarray(sig["oofvc_outside"]["appended_entry"]) if conv == "R" else np.zeros(0, np.int64)
    pt_ok = np.asarray(sig["pass_truth"], bool)
    g = gidx(sig["truth_pt"], sig["truth_pz"])
    orig = np.arange(n) < n - app.size
    return {"g": g, "pt_ok": pt_ok, "orig": orig, "n_orig": int(n - app.size),
            "t_all": P.cell_sums(g, sig["w_truth"], pt_ok), "t_orig": P.cell_sums(g, sig["w_truth"], pt_ok & orig)}


def comp_check(cap, ts: dict, conv: str, b: int | None, consumed_c: np.ndarray, d_cv: np.ndarray) -> dict:
    """C-COMP on the completeness the extraction consumed: on an R replica, c* recomputed from the CV rows, the seen
    (resampled) weights and D_CV; on every other unit, c from the CV weights (KNOWN_ISSUES 84's frozen value)."""
    c_cv = np.divide(ts["t_all"], d_cv, out=np.zeros_like(ts["t_all"]), where=d_cv != 0)  # TH2D::Divide's zero rule
    if conv == "R" and b is not None:
        ws = cap["w_truth_seen"]
        c_cv_orig = np.divide(ts["t_orig"], d_cv, out=np.zeros_like(ts["t_orig"]), where=d_cv != 0)
        r = P.c_star(P.cell_sums(ts["g"], ws, ts["pt_ok"]), P.cell_sums(ts["g"], ws, ts["pt_ok"] & ts["orig"]),
                     ts["t_orig"], d_cv, c_cv)
        rc = P.rel_close(consumed_c, r["c_star"], RTOL["comp"])
        return {"mode": "resampled", "n_keep_cv": r["n_keep_cv"], "n_lost_support": r["n_lost_support"],
                "max_rel": rc["max_rel"], "pass": bool(r["finite"] and rc["pass"])}
    rc = P.rel_close(consumed_c, c_cv, RTOL["comp"])
    return {"mode": "cv", "max_rel": rc["max_rel"], "pass": rc["pass"]}


def c_sim(C, driver, cap, h_comp, h_den, ks) -> dict:
    """C-SIM through the full chain (REF-C2C1's construction, under section 3's numerical rule): IBU on the MC's own
    reco expectation, the per-event factors, the driver's fill and the recorded extraction, against the MC's full
    truth cross section, at every K on every covered cell; the covered cells are recorded by index (the scorer checks
    the reported 205 are among them). Every comparison is rel_close (NaN-safe, exact zeros)."""
    T, M, tin, w_in = cap["T"], cap["M"], cap["tin"], cap["w_in"]
    a, k = cap["extract"]
    nx, ny = len(driver.PT_EDGES) - 1, len(driver.PZ_EDGES) - 1
    unit = h_comp.Clone("ptmc_csim_unit")
    for ix in range(1, nx + 1):
        for iy in range(1, ny + 1):
            unit.SetBinContent(ix, iy, 1.0)
    ref = C.th2_vector(cap["real_extract"](h_den, unit, *a[1:], **k), nx, ny)
    covered = C.th2_vector(h_comp, nx, ny) > 0
    traj = C.dagostini(M, T, M.sum(axis=1), ks)
    worst, ok = 0.0, bool(covered.any())
    for K in ks:
        h = C.filled(driver, tin, w_in, C.event_factors(traj[K], T, tin), f"ptmc_csim_K{K}")
        x = C.th2_vector(cap["real_extract"](h, *a, **k), nx, ny)
        r = P.rel_close(x[covered], ref[covered], RTOL["sim"])
        worst, ok = max(worst, r["max_rel"]), ok and r["pass"]
    return {"max_rel": worst, "covered": np.flatnonzero(covered).tolist(), "pass": bool(ok)}


def runtime_versions() -> dict:
    import importlib
    out = {"python": sys.version.split()[0], "numpy": np.__version__}
    for mod in ("ROOT", "lightgbm", "sklearn"):
        try:
            m = importlib.import_module(mod)
            out[mod] = getattr(m, "__version__", None) or str(m.gROOT.GetVersion())
        except Exception as e:  # recorded, never hidden
            out[mod] = f"unavailable: {type(e).__name__}"
    return out


def run_unit(C, driver, ohf, cfg: dict, name: str, out: Path, rows_path: Path, unfolder, lib_label: str,
             inputs_verified: dict, gidx) -> int:
    conv, b = parse_unit(name)
    root, npz, marker = out / f"{name}.root", out / f"{name}.npz", out / f"{name}.done"
    if npz.exists() or root.exists() or marker.exists():
        # a unit is reused only if its marker is PASS, names it, and both products match the marker's digests
        try:
            mk = json.loads(marker.read_text())
            ok = (mk.get("verdict") == "PASS" and mk.get("unit") == name and npz.is_file() and root.is_file()
                  and sha256(npz) == mk.get("sha256") and sha256(root) == mk.get("root_sha256"))
        except (OSError, ValueError):
            ok = False
        if ok:
            return 0
        print(f"refusing: {name} exists, and its marker and products do not agree as a PASS", file=sys.stderr)
        return RC_CONTROL
    cpus = C.cpu_count()
    threads = {k: os.environ.get(k) for k in cfg["e_r"]["thread_env"]}
    if cpus != int(cfg["e_r"]["cpus"]) or threads != cfg["e_r"]["thread_env"]:
        print(f"refusing: {name} needs {cfg['e_r']['cpus']} CPUs and {cfg['e_r']['thread_env']}; has {cpus}, "
              f"{threads}", file=sys.stderr)
        return RC_GATE
    out.mkdir(parents=True, exist_ok=True)
    cfg_u = copy.deepcopy(cfg)
    if conv == "R":
        cfg_u["e_r"]["argv"] = list(cfg["e_r"]["argv"]) + MINERVA_ARGV + [str(rows_path)]
    argv = C.resolve_argv(cfg_u, b)
    if "--unit-factors" in argv:
        print("refusing: --unit-factors on a scored unit", file=sys.stderr)
        return RC_GATE
    ks = list(cfg["c2"]["iterations"]["scan"])
    t0 = time.time()
    cap = run_paired(C, driver, ohf, argv, root, ks, unfolder, C.staging_root(cfg))
    allowed = (out, C.staging_root(cfg))
    xs = C.xsec_at_every_k(driver, cap, ks)
    controls = {}
    # C-FILL-IBU: IBU's event-level route (ref_c2c1.filled, then the recorded extraction) against its direct route
    a, k = cap["extract"]
    nx, ny = len(driver.PT_EDGES) - 1, len(driver.PZ_EDGES) - 1
    worst, fill_ok = 0.0, True
    for K in ks:
        h = C.filled(driver, cap["tin"], cap["w_in"], C.event_factors(cap["traj"][K], cap["T"], cap["tin"]),
                     f"ptmc_fill_K{K}")
        r = P.rel_close(C.th2_vector(cap["real_extract"](h, *a, **k), nx, ny), xs[K], RTOL["fill"])
        worst, fill_ok = max(worst, r["max_rel"]), fill_ok and r["pass"]
    controls["C-FILL-IBU"] = {"max_rel": worst, "pass": bool(fill_ok)}
    # C-PAIR: the arrays OmniFold received are the ones IBU binned; y rebuilt independently
    y_r = P.rel_close(cap["y_np"], cap["y"], RTOL["pair_y"])
    mpr = np.asarray(cap["seam"]["measured_pass_reco"])
    mpr_ok = bool(mpr.dtype == bool and mpr.shape == (cap["seam"]["n_measured"],) and np.all(mpr))
    controls["C-PAIR"] = {"digest": cap["digest_ibu"], "same": cap["digest_ibu"] == cap["digest_omnifold"],
                          "y_max_rel": y_r["max_rel"], "measured_mask_all_true": mpr_ok,
                          "pass": bool(cap["digest_ibu"] == cap["digest_omnifold"] and y_r["pass"] and mpr_ok)}
    # C-ROO on every unit: the bound RooUnfoldBayes against the same update in numpy
    if lib_label == "numpy unfolder":
        controls["C-ROO"] = {"ran": False, "pass": True}
    else:
        ref = C.dagostini(cap["M"], cap["T"], cap["y"], ks)
        per_k = {int(K): P.rel_close(cap["traj"][K], ref[K], RTOL["roo"]) for K in ks}  # NaN-safe, exact zeros
        controls["C-ROO"] = {"ran": True, "max_rel": {K: r["max_rel"] for K, r in per_k.items()},
                             "pass": bool(all(r["pass"] for r in per_k.values()))}
    # C-DRAW-R, row level, at the refinement's entry and at OmniFold's
    sig_cv = cap["sig_cv"]
    app = (np.asarray(sig_cv["oofvc_outside"]["appended_entry"], np.int64) if conv == "R"
           else np.zeros(0, np.int64))
    pt_lo, pt_hi, pz_lo, pz_hi = (driver.PT_EDGES[0], driver.PT_EDGES[-1], driver.PZ_EDGES[0], driver.PZ_EDGES[-1])
    need = ["signed_w", "signed_feat", "bkg_cv", "data_cv"] + (["fill_rows", "inj_entries", "n_bkg_entries"]
                                                                if b is not None else [])
    missing = [x for x in need if x not in cap]
    if missing:
        controls["C-DRAW-R"] = {"pass": False, "why": f"not captured: {missing}"}
    else:
        n_data = cap["data_cv"]["pt"].size
        if b is not None:
            # the injection rebuilt independently from the ordered fill records by the driver's fiducial rule: entries,
            # coordinates and POT-scaled weights; the loader's returned arrays must equal it (codex r1 #14)
            fr = cap["fill_rows"]
            fpt, fpz = np.asarray(fr["pt"], float), np.asarray(fr["pz"], float)
            keep = (fpt >= pt_lo) & (fpt <= pt_hi) & (fpz >= pz_lo) & (fpz <= pz_hi)
            inj = np.asarray(fr["entry"], np.int64)[keep]
            inj_pt, inj_pz, inj_cv = fpt[keep], fpz[keep], np.asarray(fr["w_pot"], float)[keep]
            inj_same = bool(np.array_equal(inj, cap["inj_entries"])
                            and np.array_equal(inj_pt, cap["bkg_cv"]["pt"]) and np.array_equal(inj_pz, cap["bkg_cv"]["pz"])
                            and np.array_equal(inj_cv, cap["bkg_cv"]["w"]))
        else:  # a central has no fill record (one stream off): the loader's arrays, at unit factors
            inj_pt, inj_pz, inj_cv = cap["bkg_cv"]["pt"], cap["bkg_cv"]["pz"], cap["bkg_cv"]["w"]
            inj, inj_same = np.arange(inj_cv.size, dtype=np.int64), True
        feat = cap["signed_feat"]
        want_feat = np.concatenate([np.column_stack([cap["data_cv"]["pt"], cap["data_cv"]["pz"]]),
                                    np.column_stack([inj_pt, inj_pz])])
        feat_same = bool(feat.shape == want_feat.shape and np.array_equal(feat, want_feat))
        d = P.draw_check(b, n_data=n_data, n_entries=cap.get("n_bkg_entries", 0), appended_entry=app,
                         inj_entries=inj, inj_cv=inj_cv, signed_w=cap["signed_w"], w_truth_cv=sig_cv["w_truth"],
                         w_reco_cv=sig_cv["w_reco"], w_truth_seen=cap["w_truth_seen"], w_reco_seen=cap["w_reco_seen"])
        d.update(injected_entries_recomputed=inj_same, coordinates=feat_same)
        if conv == "R":
            rows = np.load(rows_path)
            in_grid = gidx(rows["reco_pt"], rows["reco_pz"]) >= 0
            wt, wr = np.asarray(rows["w_truth"], float), np.asarray(rows["w_reco"], float)
            w_ok = (wt >= 0) & (wt < 1e4) & (wr >= 0) & (wr < 1e4)
            want_app = np.asarray(rows["entry"], np.int64)[in_grid & w_ok]
            d["appended_list"] = bool(np.array_equal(want_app, app))
        d["pass"] = bool(d["pass"] and inj_same and feat_same and d.get("appended_list", True))
        controls["C-DRAW-R"] = d
    # C-REFINE: the refinement's return is the measured weight both methods received
    rw, mw_raw = cap.get("refined_w"), cap["seam"]["measured_weights_raw"]
    controls["C-REFINE"] = {"pass": bool(rw is not None and np.all(np.isfinite(np.asarray(rw, float)))
                                         and P.digest(rw) == P.digest(mw_raw))}
    # the R units' identity checks on the moved rows (C-MOVE's sets in every R unit; C-DRAW-R's appended rows)
    if conv == "R":
        rows = np.load(rows_path)
        listed = np.asarray(rows["entry"], np.int64)
        inj_ids = cap.get("inj_entries", np.zeros(0, np.int64))
        fill_ids = cap["fill_rows"]["entry"] if "fill_rows" in cap else np.zeros(0, np.int64)
        n_sig = sig_cv["w_truth"].shape[0]
        sm, lo = cap["seam"], n_sig - app.size  # coordinates and masks as OmniFold and IBU received them
        tail = {"reco_pt": np.asarray(sm["MCreco"])[lo:, 0], "reco_pz": np.asarray(sm["MCreco"])[lo:, 1],
                "truth_pt": np.asarray(sm["MCgen"])[lo:, 0], "truth_pz": np.asarray(sm["MCgen"])[lo:, 1],
                "pass_reco": np.asarray(sm["pass_reco"])[lo:], "pass_truth": np.asarray(sm["pass_truth"])[lo:],
                "w_truth": np.asarray(sig_cv["w_truth"])[lo:], "w_reco": np.asarray(sig_cv["w_reco"])[lo:]}
        f = __import__("ROOT").TFile.Open(str(root))
        pot = float(f.Get("potScale").GetVal())
        f.Close()
        ident = P.appended_identity(rows, app, pot, tail)
        controls["C-MOVE-UNIT"] = {"skip_disjoint_from_injected": bool(np.intersect1d(listed, inj_ids).size == 0),
                                   "skip_disjoint_from_fill_rows": bool(np.intersect1d(listed, fill_ids).size == 0),
                                   "appended_identity": ident,
                                   "pass": bool(np.intersect1d(listed, inj_ids).size == 0
                                                and np.intersect1d(listed, fill_ids).size == 0 and ident["pass"])}
    extract_args = [np.asarray(x, float) if hasattr(x, "__len__") else np.asarray([float(x)]) for x in a[1:]]
    args_finite = all(np.all(np.isfinite(x)) for x in extract_args)
    # C-COMP, on the histogram the extraction consumed (the recorded call's second argument)
    hc = a[0]
    axes_ok = (hc.GetNbinsX() == nx and hc.GetNbinsY() == ny
               and [hc.GetXaxis().GetBinLowEdge(i) for i in range(1, nx + 2)] == [float(e) for e in driver.PT_EDGES]
               and [hc.GetYaxis().GetBinLowEdge(i) for i in range(1, ny + 2)] == [float(e) for e in driver.PZ_EDGES])
    consumed_c = C.th2_vector(hc, nx, ny)
    d_cv = read_hist(C, driver, root, "hOFTruthDenom2D", allowed)
    ts = truth_sums(cap, gidx, conv)
    controls["C-COMP"] = comp_check(cap, ts, conv, b, consumed_c, d_cv)
    controls["C-COMP"]["axes"] = axes_ok
    controls["C-COMP"]["pass"] = bool(controls["C-COMP"]["pass"] and axes_ok)
    # section 2.2's printed counts: structural-zero cells whose moved truth weight the extraction suppresses
    suppressed = int(np.sum((ts["t_orig"] == 0) & (d_cv == 0) & (ts["t_all"] > ts["t_orig"]))) if conv == "R" else 0
    support_rec = None
    if b is None:
        # C-COUPLE: KNOWN_ISSUES 84's premise as an exact multiset identity per cell (the sums' agreement printed)
        if "truth_denom" not in cap:
            controls["C-COUPLE"] = {"pass": False, "why": "the canonical denominator was not loaded"}
        else:
            td = cap["truth_denom"]
            m = ts["pt_ok"] & ts["orig"]
            controls["C-COUPLE"] = P.coupling_exact(
                gidx(td["truth_pt"], td["truth_pz"]), td["truth_pt"], td["truth_pz"], td["w_truth"],
                np.where(m, ts["g"], -1), sig_cv["truth_pt"], sig_cv["truth_pz"], sig_cv["w_truth"])
            controls["C-COUPLE"]["sums"] = P.coupling(ts["t_orig"], d_cv)
            # the input's hasTruthOnlyMisses, read as the driver reads it: bool(int(...)), i.e. non-zero (hadd sums the
            # per-playlist flag: 12 on 43f8cc16, receipts/couple/run2)
            import ROOT
            fcv = ROOT.TFile.Open(C.staged(cfg)["CV"])
            par = fcv.Get("hasTruthOnlyMisses")
            flag = int(par.GetVal()) if par else 0
            fcv.Close()
            controls["C-COUPLE"]["hasTruthOnlyMisses"] = flag
            controls["C-COUPLE"]["pass"] = bool(controls["C-COUPLE"]["pass"] and flag != 0)
        # C-SIM on the centrals, through the completeness the extraction consumed
        import ROOT
        f = ROOT.TFile.Open(str(root))
        hd = f.Get("hOFTruthDenom2D")
        hd.SetDirectory(0)
        f.Close()
        controls["C-SIM"] = c_sim(C, driver, cap, hc, hd, ks)
        if conv == "R":  # C-SUPPORT (printed): the seeds' lost-support cells, which give 0 in both conventions
            support_rec = P.support(ts["g"], sig_cv["w_truth"], ts["pt_ok"] & ts["orig"], ts["n_orig"],
                                    SEEDS["R"])
    meta = {"schema": "ptmc-unit/1", "unit": name, "convention": conv, "bootstrap_seed": b, "argv": argv,
            "ks": ks, "unfolder": lib_label, "runner_sha256": sha256(Path(__file__).resolve()),
            "lib_sha256": sha256(HERE / "ptmc_lib.py"), "code_sha256": cfg["code_sha256"],
            "inputs_sha256": inputs_verified, "cpus": cpus, "thread_env": threads,
            "slurm_job": os.environ.get("SLURM_JOB_ID"), "controls": controls, "runtime": runtime_versions(),
            "oofvc_counts": sig_cv.get("oofvc_outside", {}).get("counts") if conv == "R" else None,
            "ptmc_record": {k2: v for k2, v in cap["ptmc_record"].items() if k2 != "completeness"},
            "support": support_rec, "extract_args_sha256": P.digest(*extract_args), "extract_args_finite": args_finite,
            "completeness_counts": {k2: v for k2, v in cap["ptmc_record"].get("completeness", {}).items()
                                    if k2 != "c_star"},
            "suppressed_moved_support_cells": suppressed,
            "seconds": round(time.time() - t0, 3)}
    passed = all(c["pass"] is True for c in controls.values()) and args_finite
    arrays = {"ks": np.array(ks), "xsec": np.array([xs[K] for K in ks]), "unfolded": np.array([cap["traj"][K] for K in ks]),
              "T": cap["T"], "M": cap["M"], "y": cap["y"], "completeness": consumed_c, "appended_entry": np.asarray(app),
              "lgbm_params": np.array(json.dumps(cap.get("lgbm", []))),
              "fill_entries": np.sort(np.asarray(cap["fill_rows"]["entry"], np.int64)) if "fill_rows" in cap
              else np.zeros(0, np.int64),
              # the ordered fill record and the ordered injection (multiplicity preserved; the scorer's C-MOVE)
              "fill_entry": np.asarray(cap["fill_rows"]["entry"], np.int64) if "fill_rows" in cap else np.zeros(0, np.int64),
              "fill_pt": np.asarray(cap["fill_rows"]["pt"], float) if "fill_rows" in cap else np.zeros(0),
              "fill_pz": np.asarray(cap["fill_rows"]["pz"], float) if "fill_rows" in cap else np.zeros(0),
              "fill_w": np.asarray(cap["fill_rows"]["w_pot"], float) if "fill_rows" in cap else np.zeros(0),
              "inj_entries": np.asarray(cap.get("inj_entries", np.zeros(0, np.int64)), np.int64)}
    np.savez_compressed(npz, **arrays, meta=json.dumps(meta, default=str))
    marker.write_text(json.dumps({"unit": name, "verdict": "PASS" if passed else "FAIL", "sha256": sha256(npz),
                                  "root_sha256": sha256(root)}) + "\n")
    print(json.dumps({"unit": name, "seconds": meta["seconds"], "controls": {k2: v["pass"] for k2, v in controls.items()}}),
          flush=True)
    return 0 if passed else RC_CONTROL


def run(a) -> int:
    try:
        names = [parse_unit(u) and u for u in a.unit]
    except ValueError as e:
        print(f"refusing: {e}", file=sys.stderr)
        return 2
    if len(set(names)) != len(names):
        print("refusing: a unit is named twice", file=sys.stderr)
        return 2
    C = import_runner(a.tree)
    cfg = json.loads(C.CONFIG.read_text())
    try:
        C.check_code(cfg)
        verified = C.check_inputs(cfg)
        driver, ohf = C.load_driver()
    except (C.GateFailure, OSError) as e:
        print(f"refusing: {e}", file=sys.stderr)
        return RC_GATE
    if (a.rows_sha256 != PINS["rows"] or sha256(a.rows) != PINS["rows"] or not C.under(a.rows, C.staging_root(cfg))
            or sha256(a.join_record) != PINS["join"]):
        print("refusing: the rows file or the join record is not its pin, or the rows are not under the staging "
              "root", file=sys.stderr)
        return RC_GATE
    lib = Path(cfg["inputs"]["roounfold_lib"])
    if a.numpy_unfolder:
        unfolder, lib_label = C.dagostini, "numpy unfolder"
    else:
        if not lib.is_file() or sha256(lib) != cfg["inputs"]["roounfold_lib_sha256"]:
            print("refusing: libRooUnfold.so is not its pin", file=sys.stderr)
            return RC_GATE
        unfolder, lib_label = (lambda M, T, y, k: C.roounfold_bayes(M, T, y, k, str(lib))), sha256(lib)
    gfn = global_index_fn(a.tree)

    def gidx(pt, pz):
        return gfn(pt, pz, driver.PT_EDGES, driver.PZ_EDGES)

    def pins():
        return {"driver": sha256(C.RE2), "runner": sha256(Path(C.__file__)), "ptmc_run": sha256(Path(__file__)),
                "ptmc_lib": sha256(HERE / "ptmc_lib.py"), "rows": sha256(a.rows), "join_record": sha256(a.join_record),
                "config": sha256(C.CONFIG),
                "inputs": C.check_inputs(cfg), "roounfold_lib": lib_label}
    before = pins()
    rc = 0
    outputs = {}
    for name in names:
        urc = run_unit(C, driver, ohf, cfg, name, a.out, a.rows, unfolder, lib_label, verified, gidx)
        outputs[name] = {n: sha256(a.out / n) for n in (f"{name}.done", f"{name}.npz", f"{name}.root")
                         if (a.out / n).exists()}
        rc = rc or urc
    after = pins()
    tag = "_".join(names) if len(names) <= 4 else f"{names[0]}..{names[-1]}_{len(names)}"
    (a.out / f"pins_{tag}.json").write_text(json.dumps({"units": names, "before": before, "after": after,
                                                       "outputs": outputs, "pass": before == after}, indent=1) + "\n")
    return rc or (0 if before == after else RC_CONTROL)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--tree", type=Path, required=True)
    ap.add_argument("--rows", type=Path, required=True)
    ap.add_argument("--rows-sha256", required=True)
    ap.add_argument("--join-record", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--unit", action="append", required=True)
    ap.add_argument("--numpy-unfolder", action="store_true",
                    help="tests only (no libRooUnfold locally): C-ROO does not run; the scorer refuses such units")
    return run(ap.parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
