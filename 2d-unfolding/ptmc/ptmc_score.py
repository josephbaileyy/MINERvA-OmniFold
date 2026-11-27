#!/usr/bin/env python3
"""PTMC's scorer (PTMC-DECLARATION.md sections 3-5): every control and the disposition first, then the statistic, the
readings and the statement. It reads only fetched copies (the units, the D4 baseline products) and committed records.

  python3 ptmc_score.py --tree DEPLOY --units unit_names()_DIR --d4 D4_DIR --repo REPO --rows ROWS.npz --rows-sha256 SHA
                        --pins PINS.json --out score.json

unit_names()_DIR holds the 207 units (<unit>.npz, .root, .done) and the runner's pins files. D4_DIR holds the fetched
baseline: c2_central.npz, c2_replica_b{1..200}.npz, and the staged copies 000..201 (000 the publication). REPO is a
checkout at the binding's commit (the committed markers, readout.json and cells.root). PINS.json is the binding's
pin set. Exit 0 with a reading; 3 for a STOP (STOP.json written, no T formed); 2 for a refused invocation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ptmc_lib as P  # noqa: E402

REF_RECEIPTS = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-ref-c2c1/step2"
READOUT = f"{REF_RECEIPTS}/read-2/readout.json"
CELLS = f"{REF_RECEIPTS}/cells/cells.root"
# The declared constants (PTMC-DECLARATION.md sections 1-4), in one place. The CLI has no way to change them; the
# fixture-scale scorer test patches CONST (mock.patch.dict) to a small N and rank.
CONST = {"N": P.N_REPLICAS, "RANK": P.RANK, "N_OFF": 5, "CELLS_SHA": "f06e4a26efc3085eac71d80fce5f806f17dc04cb89bfcc51ee2c939332aed743",
     "E_R_SHA": "a5c13fc38d64242bc9ee459fac87568a2f97fddf7a3ac97cc6f91eb4c2a31cef",
     "PUB_SHA": "6c6dce72050bb8f128fab8e286349b250bc60d1c767e162bf15a0f009f3573e3", "C_PUB": 465.41527219152636,
     "NDF": 205, "COUNTS": {"appended": 536518, "outside": 7644, "dropped_appended_weight": 0,
                            "dropped_outside_weight": 0},
     "SCAN": [1, 2, 3, 4, 5, 10, 15, 20],
     "Q_R_SRC": "/pscratch/sd/j/josephrb/2d-closeout-re2-20261023/partb/out/S1_{b:03d}/xsec.root"}


def unit_names() -> list:
    return (["p_off_c", "p_R_c"] + [f"p_off_b{b}" for b in range(1, CONST["N_OFF"] + 1)]
            + [f"p_R_b{b}" for b in range(1, CONST["N"] + 1)])


def seeds():
    return range(1, CONST["N"] + 1)
FIX = ("hOFTruthDenom2D", "hDataReco2D", "hFlux_pt", "dataPOT", "mcPOT", "potScale", "fluxIntegral_m2_per_POT",
       "fluxIntegral_cm2_per_POT", "nNucleons")
EDGES = ([0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55, 0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50],
         [1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 6, 7, 8, 9, 10, 15, 20, 40, 60])


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        while block := fh.read(1 << 24):
            h.update(block)
    return h.hexdigest()


class Stop(RuntimeError):
    pass


# --------------------------------------------------------------------------------------------- ROOT reads


def root_objects(path: Path) -> dict:
    """Every TH1 (contents and errors over all cells, overflow included), TParameter and TNamed of a ROOT file."""
    import ROOT
    f = ROOT.TFile.Open(str(path))
    if not f or f.IsZombie():
        raise Stop(f"{path} does not open")
    out = {}
    for k in f.GetListOfKeys():
        o = k.ReadObj()
        if o.InheritsFrom("TH1"):
            n = o.GetNcells()
            out[k.GetName()] = ("TH1", np.array([o.GetBinContent(i) for i in range(n)]),
                                np.array([o.GetBinError(i) for i in range(n)]))
        elif o.ClassName().startswith("TParameter"):
            out[k.GetName()] = ("TParameter", o.GetVal())
        elif o.ClassName() == "TNamed":
            out[k.GetName()] = ("TNamed", o.GetTitle())
    f.Close()
    return out


def vec(path: Path, name: str = "hXSec2D") -> np.ndarray:
    """The 224-cell vector in GlobalID order, after checking the axes are section 2.5's."""
    import ROOT
    f = ROOT.TFile.Open(str(path))
    h = f.Get(name) if f and not f.IsZombie() else None
    if not h:
        raise Stop(f"{path} has no {name}")
    ax = [[h.GetXaxis().GetBinLowEdge(i) for i in range(1, h.GetNbinsX() + 2)],
          [h.GetYaxis().GetBinLowEdge(i) for i in range(1, h.GetNbinsY() + 2)]]
    v = np.array([h.GetBinContent(ix, iy) for ix in range(1, h.GetNbinsX() + 1) for iy in range(1, h.GetNbinsY() + 1)])
    f.Close()
    if not (np.allclose(ax[0], EDGES[0], rtol=0, atol=1e-12) and np.allclose(ax[1], EDGES[1], rtol=0, atol=1e-12)):
        raise Stop(f"{path} {name}: axes are not section 2.5's")
    if v.shape != (224,) or not np.all(np.isfinite(v)):
        raise Stop(f"{path} {name}: not a finite 224-vector")
    return v


def named_json(path: Path, name: str) -> dict:
    o = root_objects(path).get(name)
    return json.loads(o[1]) if o and o[0] == "TNamed" and o[1] else {}


# ---------------------------------------------------------------------------------------------- the units


def npz(path: Path) -> dict:
    z = np.load(path, allow_pickle=False)
    out = {k: z[k] for k in z.files}
    out["meta"] = json.loads(str(out["meta"]))
    return out


def ibu(z: dict, K: int) -> np.ndarray:
    ks = [int(k) for k in z["ks"]]
    if K not in ks:
        raise Stop(f"K = {K} is not in the unit's ks {ks}")
    x = np.asarray(z["xsec"][ks.index(K)], float)
    if x.shape != (224,) or not np.all(np.isfinite(x)):
        raise Stop("an IBU vector is not a finite 224-vector")
    return x


def check_units(units: Path, pins: dict, scan: list) -> tuple[dict, dict]:
    """C-UNITS and C-PINS, and every unit's own controls."""
    found = sorted(p.stem for p in units.glob("p_*.done"))
    if found != sorted(unit_names()):
        raise Stop(f"C-UNITS: inventory {len(found)} units; missing {sorted(set(unit_names()) - set(found))[:5]}, extra "
                   f"{sorted(set(found) - set(unit_names()))[:5]}")
    metas, runtimes, failed = {}, set(), []
    for u in unit_names():
        mk = json.loads((units / f"{u}.done").read_text())
        if mk.get("unit") != u or mk.get("verdict") != "PASS":
            raise Stop(f"C-UNITS: {u} marker {mk}")
        if sha256(units / f"{u}.npz") != mk["sha256"] or sha256(units / f"{u}.root") != mk["root_sha256"]:
            raise Stop(f"C-UNITS: {u} products differ from its marker")
        z = npz(units / f"{u}.npz")
        m = z["meta"]
        conv, b = ("R" if u.startswith("p_R") else "off"), (None if u.endswith("_c") else int(u.split("_b")[1]))
        argv = m["argv"]
        has_conv = "--signal-convention" in argv
        has_boot = "--bootstrap-seed" in argv
        if (conv == "R") != has_conv or (b is not None) != has_boot or "--unit-factors" in argv:
            raise Stop(f"C-UNITS: {u} argv flags")
        if b is not None and (argv[argv.index("--bootstrap-seed") + 1] != str(b)
                              or argv[argv.index("--bootstrap-streams") + 1] != "three"):
            raise Stop(f"C-UNITS: {u} bootstrap flags")
        if [int(k) for k in z["ks"]] != list(scan) or m["ks"] != list(scan):
            raise Stop(f"C-UNITS: {u} ks")
        if m["unfolder"] in ("numpy unfolder",) or m["unfolder"] != pins["roounfold_lib_sha256"]:
            raise Stop(f"C-UNITS: {u} unfolder {m['unfolder']}")
        if m["cpus"] != pins["cpus"] or m["thread_env"] != pins["thread_env"]:
            raise Stop(f"C-UNITS: {u} CPUs or threads")
        runtimes.add(json.dumps(m["runtime"], sort_keys=True))
        if m["runner_sha256"] != pins["ptmc_run"] or m["lib_sha256"] != pins["ptmc_lib"]:
            raise Stop(f"C-PINS: {u} runner or library")
        if m["code_sha256"] != pins["code_sha256"] or m["inputs_sha256"] != pins["inputs"]:
            raise Stop(f"C-PINS: {u} code or inputs")
        bad = [k for k, c in m["controls"].items() if not c.get("pass")]
        if bad:
            failed.append((u, bad))
        metas[u] = m
    if len(runtimes) != 1:
        raise Stop(f"C-UNITS: {len(runtimes)} distinct runtime sets")
    if failed:
        raise Stop(f"a unit control failed: {failed[:5]}")
    for pf in units.glob("pins_*.json"):
        p = json.loads(pf.read_text())
        if not p.get("pass") or p["before"]["driver"] != pins["driver"] or p["before"]["rows"] != pins["rows"]:
            raise Stop(f"C-PINS: {pf.name}")
    return metas, {"C-UNITS": {"pass": True, "units": len(unit_names()), "runtime": json.loads(runtimes.pop())},
                   "C-PINS": {"pass": True}}


# ---------------------------------------------------------------------------------------------- the score


def score(a) -> dict:
    pins = json.loads(Path(a.pins).read_text())
    sys.path.insert(0, str(a.tree / "2d-unfolding" / "ref_c2c1"))
    import ref_c2c1_read as RR
    sys.path.insert(0, str(a.tree / "2d-unfolding" / "oofvc"))
    import oofvc_lib as L
    controls, printed = {}, {}
    if sha256(a.rows) != a.rows_sha256:
        raise Stop("C-IN: the rows file")
    for f, want in (("2d-unfolding/ref_c2c1/ref_c2c1_read.py", pins["ref_c2c1_read"]),
                    ("2d-unfolding/re2/re2_driver.py", pins["driver"]),
                    ("2d-unfolding/uq/reported_cells.py", pins["reported_cells"]),
                    ("2d-unfolding/compare_to_paper_fullcov.py", pins["compare"])):
        if sha256(a.tree / f) != want:
            raise Stop(f"C-PINS: the scorer's {f}")
    scan = list(CONST["SCAN"])
    metas, c = check_units(a.units, pins, scan)
    controls.update(c)
    # the mandatory E_R central (C-IN), the publication and the cells (C-CELLS, C-PUB)
    e_r = a.d4 / "001_xsec.root"
    if not e_r.is_file() or sha256(e_r) != CONST["E_R_SHA"]:
        raise Stop("C-IN: the mandatory E_R central (001) is absent or not a5c13fc3")
    pub_path = a.d4 / "000_cov_ptpl_minerva_inclusive_6GeV.root"
    if not pub_path.is_file() or sha256(pub_path) != CONST["PUB_SHA"]:
        raise Stop("C-IN: the publication copy (000)")
    cells = a.repo / CELLS
    if sha256(cells) != CONST["CELLS_SHA"]:
        raise Stop("C-CELLS: the committed cells.root")
    import ROOT
    import reported_cells as rc
    cp = RR.compare()
    f = ROOT.TFile.Open(str(pub_path))
    pub_x = cp.flatten_th2d(f.Get("pt_pl_cross_section"))
    pub_cov = cp.tmatrix_to_numpy(f.Get("TotalCovariance"))
    pub_stat = cp.tmatrix_to_numpy(f.Get("StatOnlyCovariance"))
    f.Close()
    rule = rc.reported_indices((np.diag(pub_stat) > 0).reshape(rc.GRID_SHAPE))
    fc = ROOT.TFile.Open(str(cells))
    bound, _ = rc.read_cells(fc)
    fc.Close()
    try:
        rc.require_same_cells(np.asarray(bound), np.asarray(rule), "committed cells", "the receipt's rule")
    except Exception as e:  # reported_cells.CellIdentityError and its kin
        raise Stop(f"C-CELLS: {e}") from None
    try:
        rc.require_same_cells(np.asarray(bound), rc.reported_indices((np.diag(pub_cov) > 0).reshape(rc.GRID_SHAPE)),
                              "committed cells", "TotalCovariance's mask")
    except Exception as e:
        raise Stop(f"C-CELLS: {e}") from None
    cells_idx = np.asarray(bound, int)
    controls["C-CELLS"] = {"pass": True, "cells": int(cells_idx.size)}

    def dist(x):
        chi2, ndf, _ = cp.chi2_with_cov(np.asarray(x, float) - pub_x, pub_cov, "", report=False)
        return chi2 / ndf, ndf
    x_er = vec(e_r)
    d_er, ndf = dist(x_er)
    if ndf != CONST["NDF"] or abs(d_er * ndf / CONST["C_PUB"] - 1) > 1e-8:
        raise Stop(f"C-PUB: chi2 {d_er * ndf} over {ndf}")
    controls["C-PUB"] = {"pass": True, "chi2": d_er * ndf, "ndf": ndf}
    # C-GRID: every unit's hXSec2D axes (vec() refuses otherwise)
    U = {u: npz(a.units / f"{u}.npz") for u in unit_names()}
    X_OF = {u: vec(a.units / f"{u}.root") for u in unit_names()}
    controls["C-GRID"] = {"pass": True}
    # C-FIX: R against production, bit for bit with errors and overflow
    ro, rr = root_objects(a.units / "p_off_c.root"), root_objects(a.units / "p_R_c.root")
    fix = {}
    for name in FIX:
        o, r = ro.get(name), rr.get(name)
        fix[name] = bool(o is not None and r is not None and o[0] == r[0] and all(
            np.array_equal(np.asarray(x), np.asarray(y)) for x, y in zip(o[1:], r[1:])))
    if not all(fix.values()):
        raise Stop(f"C-FIX: {fix}")
    controls["C-FIX"] = {"pass": True, "equal": fix}
    # C-MOVE: the sets, the counts and the removal per reco cell
    rows = {k: v for k, v in np.load(a.rows).items()}
    meta_r = metas["p_R_c"]
    counts = meta_r["oofvc_counts"]
    want = dict(CONST["COUNTS"])
    if counts != want:
        raise Stop(f"C-MOVE: counts {counts} != {want}")
    entries = np.asarray(rows["entry"], np.int64)
    app = np.asarray(U["p_R_c"]["appended_entry"], np.int64)
    in_grid = L.global_index(rows["reco_pt"], rows["reco_pz"], *EDGES) >= 0
    outside = np.setdiff1d(entries, app)
    if not (np.array_equal(np.sort(app), np.sort(entries[in_grid])) and np.intersect1d(app, outside).size == 0
            and app.size + outside.size == entries.size):
        raise Stop("C-MOVE: the appended and reco-outside sets do not partition the rows file")
    n_sig = {u: int(U[u]["meta"]["controls"]["C-DRAW-R"]["n_original"] + U[u]["meta"]["controls"]["C-DRAW-R"]
                    ["n_appended"]) for u in ("p_off_c", "p_R_c")}
    if n_sig["p_R_c"] - n_sig["p_off_c"] != want["appended"]:
        raise Stop(f"C-MOVE: the signal arrays grow by {n_sig['p_R_c'] - n_sig['p_off_c']}")
    pot = ro["potScale"][1]
    w = np.asarray(rows["w_reco"], float)
    rect = ((rows["reco_pt"] >= EDGES[0][0]) & (rows["reco_pt"] <= EDGES[0][-1]) & (rows["reco_pz"] >= EDGES[1][0])
            & (rows["reco_pz"] <= EDGES[1][-1]))
    filled = rect & (w >= 0) & (w < 1e6)
    g = L.global_index(rows["reco_pt"], rows["reco_pz"], *EDGES)
    expect = np.bincount(g[filled & (g >= 0)], weights=w[filled & (g >= 0)] * pot, minlength=224)
    b_off, b_r = vec(a.units / "p_off_c.root", "hBkgReco2D"), vec(a.units / "p_R_c.root", "hBkgReco2D")
    removed = b_off - b_r
    tol = 1e-12 * np.abs(b_off)
    ok = np.all(np.abs(removed - expect) <= tol) and np.all(removed[b_off == 0] == 0)
    if not ok or not np.all(np.isfinite(removed)):
        raise Stop("C-MOVE: the removal per reco cell")
    edge = int(np.sum(rect & (g < 0)))
    controls["C-MOVE"] = {"pass": True, "counts": counts, "max_dev_over_cell": float(np.max(np.divide(
        np.abs(removed - expect), np.abs(b_off), out=np.zeros(224), where=b_off != 0)))}
    printed["upper_edge_rows"] = edge
    # C-NORM: the extraction's fixed arguments as consumed, equal in every unit to p_off_c's
    ref_norm = metas["p_off_c"]["extract_args_sha256"]
    bad = [u for u in unit_names() if metas[u].get("extract_args_sha256") != ref_norm]
    if bad:
        raise Stop(f"C-NORM: {bad[:5]}")
    controls["C-NORM"] = {"pass": True, "sha256": ref_norm}
    # C-MOVE's sets in every R replica: the ordered fill records (entry, pT, p||, w x POT) are p_off_b1's with the rows
    # file's entries removed, order and multiplicity preserved; the ordered injection is the driver's fiducial rule on
    # that filtered reference (a duplicated retained row fails; the confirm read's finding 3)
    ref = U["p_off_b1"]
    keep = ~np.isin(np.asarray(ref["fill_entry"], np.int64), entries)
    if not keep.any():
        raise Stop("C-MOVE: p_off_b1 recorded no fill rows")
    want = {k: np.asarray(ref[k])[keep] for k in ("fill_entry", "fill_pt", "fill_pz", "fill_w")}
    want_inj = P.injected_entries({"entry": want["fill_entry"], "pt": want["fill_pt"], "pz": want["fill_pz"]},
                                  EDGES[0][0], EDGES[0][-1], EDGES[1][0], EDGES[1][-1])
    bad = [u for u in unit_names() if u.startswith("p_R_b")
           and not (all(np.array_equal(np.asarray(U[u][k]), want[k]) for k in want)
                    and np.array_equal(np.asarray(U[u]["inj_entries"], np.int64), want_inj))]
    bad += [u for u in unit_names() if u.startswith("p_R") and not metas[u]["controls"].get("C-MOVE-UNIT", {}).get("pass")]
    if bad:
        raise Stop(f"C-MOVE: replica sets {bad[:5]}")
    controls["C-MOVE"]["replica_sets"] = True
    # the unit-level controls the scorer reads: C-COUPLE and C-SIM's coverage by index (C-SUPPORT is printed)
    for u in ("p_off_c", "p_R_c"):
        if not metas[u]["controls"]["C-COUPLE"]["pass"]:
            raise Stop(f"C-COUPLE: {u}")
    for u in ("p_off_c", "p_R_c"):
        comp = np.asarray(U[u]["completeness"], float)
        if not np.all(comp[cells_idx] > 0):
            raise Stop(f"C-SIM coverage: {u} has reported cells without completeness")
    controls["C-COUPLE"] = {u: metas[u]["controls"]["C-COUPLE"] for u in ("p_off_c", "p_R_c")}
    printed["C-SUPPORT"] = metas["p_R_c"].get("support")
    # C-BASE: production central against E_R (mandatory) and REF's c2_central (optional)
    r = P.rel_close(X_OF["p_off_c"], x_er, 1e-8)
    if not r["pass"]:
        raise Stop(f"C-BASE: E_R {r}")
    controls["C-BASE"] = {"pass": True, "e_r_max_rel": r["max_rel"]}
    # C-D4: every optional product (section 3.2); absence and mismatch are told apart
    readout = json.loads((a.repo / READOUT).read_text())
    marker_files = list((a.repo / REF_RECEIPTS).rglob("c2_replica_b*.done")) + list(
        (a.repo / REF_RECEIPTS / "units-centrals").glob("c2_central.done"))
    markers = {}
    for mf in marker_files:
        mk = json.loads(mf.read_text())
        if mk.get("unit") != mf.stem or mk.get("verdict") != "PASS":
            raise Stop(f"C-D4: marker {mf}")
        if mf.stem in markers and markers[mf.stem] != mk["sha256"]:
            raise Stop(f"C-D4: two markers for {mf.stem} disagree")
        markers[mf.stem] = mk["sha256"]
    absent, mismatch = [], []
    ref_c2 = {}
    for name, unit, b in [("c2_central.npz", "c2_central", None)] + [
            (f"c2_replica_b{b}.npz", f"c2_replica_b{b}", b) for b in seeds()]:
        p = a.d4 / name
        if not p.exists():
            absent.append(name)
            continue
        try:
            z = npz(p)
            ok = (p.is_file() and sha256(p) == markers.get(unit) and [int(k) for k in z["ks"]] == scan
                  and z["meta"].get("unit") == unit)
            argv = z["meta"].get("argv", [])
            if b is None:
                ok = ok and "--bootstrap-seed" not in argv
            else:
                ok = ok and argv[argv.index("--bootstrap-seed") + 1] == str(b) and \
                    argv[argv.index("--bootstrap-streams") + 1] == "three"
        except (OSError, ValueError, KeyError, IndexError):
            ok = False
        if not ok:
            mismatch.append(name)
        else:
            ref_c2[b] = z
    q_r = {}
    staged = readout["staged_sha256"]
    for b in seeds():
        name = P.staged_index(b)
        p = a.d4 / name
        if not p.exists():
            absent.append(name)
            continue
        src = CONST["Q_R_SRC"].format(b=b)
        try:
            st = named_json(p, "p1Streams")
            ok = (sha256(p) == staged.get(src) and st.get("bootstrap_seed") == b and st.get("streams") == "three")
        except Stop:
            ok = False
        if not ok:
            mismatch.append(name)
        else:
            q_r[b] = p
    repoff = None
    if not mismatch and not absent:
        x1 = vec(q_r[1])
        r1 = P.rel_close(X_OF["p_off_b1"], x1, 1e-8)
        r2 = [P.rel_close(ibu(U["p_off_b1"], K), ibu(ref_c2[1], K), 1e-8) for K in (10, 5)]
        ref_q, ref_p = named_json(q_r[1], "re2Refinement"), named_json(a.units / "p_off_b1.root", "re2Refinement")
        agg = (all(ref_q.get(k) == ref_p.get(k) for k in ("signed_sum", "n_data", "n_injected"))
               and all(P.rel_close([ref_p.get(k, math.nan)], [ref_q.get(k, math.nan)], 1e-8)["pass"]
                       for k in ("refined_sum", "clipped_fraction")))
        repoff = bool(r1["pass"] and all(x["pass"] for x in r2) and agg)
        controls["C-REPOFF"] = {"pass": repoff, "e_r": r1["max_rel"], "ibu": [x["max_rel"] for x in r2],
                                "refinement": agg}
        # C-BASE's IBU vector half
        rb = [P.rel_close(ibu(U["p_off_c"], K), ibu(ref_c2[None], K), 1e-8) for K in scan]
        if not all(x["pass"] for x in rb):
            raise Stop("C-BASE: REF's c2_central")
        controls["C-BASE"]["ibu_max_rel"] = max(x["max_rel"] for x in rb)
    elif "c2_central.npz" in absent and not mismatch:
        d_ibu = {K: dist(ibu(U["p_off_c"], K))[0] for K in scan}
        want_d = {int(k): v for k, v in readout["D_IBU_every_K"].items()}
        if not all(P.rel_close([d_ibu[K]], [want_d[K]], 1e-6)["pass"] for K in scan):
            raise Stop("C-BASE: the D_IBU fallback")
        controls["C-BASE"]["ibu_fallback"] = "distances (c2_central absent)"
    controls["C-D4"] = {"absent": absent, "mismatch": mismatch}
    disp = P.disposition(True, True, bool(absent), bool(mismatch), repoff)
    controls["disposition"] = disp
    if disp == "stop":
        raise Stop(f"the disposition is STOP: absent {absent[:5]}, mismatch {mismatch[:5]}, C-REPOFF {repoff}")
    # C-DRAW-R's aggregate half against Q_R's p1Streams (B formed only)
    if disp == "formed":
        bad = []
        for b in seeds():
            st = named_json(q_r[b], "p1Streams")
            d = metas[f"p_R_b{b}"]["controls"]["C-DRAW-R"]
            rec = named_json(a.units / f"p_R_b{b}.root", "p1Streams")
            if not (st["n"]["data"] == d["n_data"] and st["sum"]["data"] == d["data_sum"]
                    and st["n"]["mc"] == d["n_original"] and st["sum"]["mc"] == d["original_sum"]
                    and st["n"]["bkg"] == rec["n"]["bkg"] and st["sum"]["bkg"] == rec["sum"]["bkg"]):
                bad.append(b)
        if bad:
            raise Stop(f"C-DRAW-R against Q_R's p1Streams: seeds {bad[:10]}")
        controls["C-DRAW-R"] = {"pass": True, "aggregate_seeds": CONST["N"]}
    # the statistic, each arm after C-SHAPE
    rec = {"schema": "ptmc-score/1", "controls": controls}
    arms = {}
    for K in (10, 5):
        delta = ibu(U["p_R_c"], K) - X_OF["p_R_c"]
        D = np.array([ibu(U[f"p_R_b{b}"], K) - X_OF[f"p_R_b{b}"] for b in seeds()])
        arms[("R", K)] = (delta, D)
        if disp == "formed":
            delta_b = ibu(ref_c2[None], K) - x_er
            D_b = np.array([ibu(ref_c2[b], K) - vec(q_r[b]) for b in seeds()])
            arms[("B", K)] = (delta_b, D_b)
    for key, (delta, D) in arms.items():
        sg = P.shape_gate(delta, D, rank=CONST["RANK"], n=CONST["N"])
        if not sg["pass"]:
            raise Stop(f"C-SHAPE: {key} {sg}")
        printed.setdefault("lambda_ratio_rank_over_top", {})[f"{key[0]}_K{key[1]}"] = sg["lambda_ratio_rank_over_top"]
        cond = P.conditioning(D, rank=CONST["RANK"])  # the binding's guard: below 1e-10 is a STOP to the director
        if not cond["pass"]:
            raise Stop(f"the conditioning guard: {key} lambda_r/lambda_1 = {cond['ratio']:.3g} < 1e-10")
    controls["C-SHAPE"] = {"pass": True}
    readings = {}
    for (arm, K), (delta, D) in arms.items():
        t = RR.t_and_null(delta, D, CONST["RANK"])
        if not P.finite_t(t):
            raise Stop(f"C-SHAPE: a non-finite T or bar in {arm} K={K}")
        readings[f"{arm}_K{K}"] = {**t, "reading": RR.classify_t(t, P.WORDS),
                                   "T_over_q95": (t["T"] / t["q95"]) if t["q95"] > 0 else None}
    r1 = readings["R_K10"]["reading"]
    bread = readings["B_K10"]["reading"] if disp == "formed" else None
    rec.update(readings=readings, primary_K=10, disposition=disp, **{"PTMC-R1": r1, "PTMC-B": bread},
               statement=P.statement(r1, disp, bread))
    # C-PROTO (a diagnostic) and the printed values, read by nothing
    if disp == "formed":
        dB, DB = arms[("B", 10)]
        CB = np.cov(DB, rowvar=False, ddof=1)
        Dp = np.array([ibu(U[f"p_off_b{b}"], 10) - X_OF[f"p_off_b{b}"] for b in range(1, CONST["N_OFF"] + 1)])
        Cplus = RR.pinv_rank(CB, CONST["RANK"])
        delta_c = (ibu(U["p_off_c"], 10) - X_OF["p_off_c"]) - dB
        printed["C-PROTO"] = {**P.proto_eps(Dp, DB[:5], np.diag(CB)),
                              "whitened": [float(np.sqrt(max(d @ Cplus @ d, 0))) for d in (Dp - DB[:5])],
                              "whitened_central": float(np.sqrt(max(delta_c @ Cplus @ delta_c, 0)))}
    printed["hartlap"] = (CONST["N"] - CONST["RANK"] - 2) / (CONST["N"] - 1)
    printed["D_under_R"] = {"D_E_R": dist(X_OF["p_R_c"])[0],
                            "D_IBU": {K: dist(ibu(U["p_R_c"], K))[0] for K in scan}}
    for K in (10, 5):
        rho = []
        for b in seeds():
            de = dist(X_OF[f"p_R_b{b}"])[0]
            if de > 0 and math.isfinite(de):
                v = dist(ibu(U[f"p_R_b{b}"], K))[0] / de
                if math.isfinite(v):
                    rho.append(v)
        printed[f"rho_K{K}"] = {"n_defined": len(rho), "interval": (
            [float(np.quantile(rho, 0.05)), float(np.quantile(rho, 0.95))] if rho else None)}
    delta, D = arms[("R", 10)]
    var = np.var(D, axis=0, ddof=1)
    printed["delta_over_sigma"] = [float(d / math.sqrt(v)) if v > 0 else None for d, v in zip(delta, var)]
    rec["printed_read_by_nothing"] = printed
    return rec


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--tree", type=Path, required=True)
    ap.add_argument("--units", type=Path, required=True)
    ap.add_argument("--d4", type=Path, required=True)
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--rows", type=Path, required=True)
    ap.add_argument("--rows-sha256", required=True)
    ap.add_argument("--pins", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        print(f"refusing: {a.out} exists", file=sys.stderr)
        return 2
    try:
        rec = score(a)
    except Stop as e:
        stop = {"schema": "ptmc-stop/1", "stopped": True, "why": str(e)}
        (a.out.parent / "STOP.json").write_text(json.dumps(stop, indent=1) + "\n")
        print(f"STOP: {e}", file=sys.stderr)
        return 3
    a.out.write_text(json.dumps(rec, indent=1, default=float) + "\n")
    print(json.dumps({"PTMC-R1": rec["PTMC-R1"], "PTMC-B": rec["PTMC-B"], "disposition": rec["disposition"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
