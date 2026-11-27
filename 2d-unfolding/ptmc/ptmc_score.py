#!/usr/bin/env python3
"""PTMC's scorer (PTMC-DECLARATION.md sections 3-5): every control and the disposition first, then the statistic, the
readings and the statement. It reads only fetched copies (the units, the D4 baseline products) and committed records.

  python3 ptmc_score.py --tree DEPLOY --units UNITS_DIR --d4 D4_DIR --repo REPO --rows ROWS.npz --rows-sha256 SHA
                        --pins PINS.json --out score.json

UNITS_DIR holds exactly the 207 units (<unit>.npz, .root, .done) and the runner's pins files. D4_DIR holds exactly the
staging's manifest.json and the products it lists as copied. REPO is a checkout at the binding's commit (the committed
markers, readout.json and cells.root). PINS.json is the binding's pin manifest.

Exit 0 with a reading; 3 for a STOP (STOP.json written, nothing classified); 2 for a refused invocation. Every
failure, an unexpected exception included, is a STOP, never a reading.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
import traceback
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ptmc_lib as P  # noqa: E402

REF_RECEIPTS = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-ref-c2c1/step2"
READOUT = f"{REF_RECEIPTS}/read-2/readout.json"
CELLS = f"{REF_RECEIPTS}/cells/cells.root"
CENTRAL_MARKER = f"{REF_RECEIPTS}/units-centrals/c2_central.done"
# The declared constants (PTMC-DECLARATION.md sections 1-4), in one place. The CLI has no way to change them; the
# fixture-scale scorer test patches CONST (mock.patch.dict) to a small N and rank and its own pins.
CONST = {"N": P.N_REPLICAS, "RANK": P.RANK, "N_OFF": 5,
         "CELLS_SHA": "f06e4a26efc3085eac71d80fce5f806f17dc04cb89bfcc51ee2c939332aed743",
         "E_R_SHA": "a5c13fc38d64242bc9ee459fac87568a2f97fddf7a3ac97cc6f91eb4c2a31cef",
         "PUB_SHA": "6c6dce72050bb8f128fab8e286349b250bc60d1c767e162bf15a0f009f3573e3", "C_PUB": 465.41527219152636,
         "NDF": 205, "COUNTS": {"appended": 536518, "outside": 7644, "dropped_appended_weight": 0,
                                "dropped_outside_weight": 0},
         "SCAN": [1, 2, 3, 4, 5, 10, 15, 20],
         "READOUT_SHA": "0ee21301744cf04df4e1ebf7224692a00fba5188532b31af9d596be8ce69cf5a",
         "CENTRAL_MARKER_SHA": "929d0e78011ead72e9677a05bad06eec80e914e181c8d02f94bbdea1c43b76f4",
         "ROWS_SHA": "cbf34bd8cad0f4978dc1aea22713eb5057bf521118dc7ce8d10b93b30defcb03",
         "CPUS": 64, "THREADS": {"OMP_NUM_THREADS": "64", "MKL_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1"},
         "RUNTIME_KEYS": ["python", "numpy", "ROOT", "lightgbm", "sklearn"],
         "Q_R_SRC": "/pscratch/sd/j/josephrb/2d-closeout-re2-20261023/partb/out/S1_{b:03d}/xsec.root",
         "OFFSETS": {"data": 0, "mc": 10_000_000, "bkg": 20_000_000}}
TREE_FILES = ("2d-unfolding/re2/re2_driver.py", "2d-unfolding/ref_c2c1/config.json", "2d-unfolding/ref_c2c1/ref_c2c1.py",
              "2d-unfolding/ref_c2c1/ref_c2c1_read.py", "unbinned_unfolding/python/omnifold.py",
              "2d-unfolding/compare_to_paper_fullcov.py", "2d-unfolding/uq/reported_cells.py",
              "2d-unfolding/oofvc/oofvc_lib.py")
OWN_FILES = ("ptmc_lib.py", "ptmc_score.py", "ptmc_run.py")
FIX = ("hOFTruthDenom2D", "hDataReco2D", "hFlux_pt", "dataPOT", "mcPOT", "potScale", "fluxIntegral_m2_per_POT",
       "fluxIntegral_cm2_per_POT", "nNucleons")
EDGES = ([0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55, 0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50],
         [1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 6, 7, 8, 9, 10, 15, 20, 40, 60])
DRIVER_EDGE_LINES = ("PT_EDGES = [0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55,",
                     "            0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50]  # GeV/c, 14 bins",
                     "PZ_EDGES = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0,",
                     "            6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0, 40.0, 60.0]  # GeV/c, 16 bins")
HEX64 = re.compile(r"[0-9a-f]{64}")


def unit_names() -> list:
    return (["p_off_c", "p_R_c"] + [f"p_off_b{b}" for b in range(1, CONST["N_OFF"] + 1)]
            + [f"p_R_b{b}" for b in range(1, CONST["N"] + 1)])


def seeds():
    return range(1, CONST["N"] + 1)


sha256 = P.sha256_file


class Stop(RuntimeError):
    pass


def need(cond, why):
    if not cond:
        raise Stop(why)


# --------------------------------------------------------------------------------------------- ROOT reads


def root_objects(path: Path) -> dict:
    """Every TH1 (its axes, contents and errors over all cells, overflow included), TParameter and TNamed."""
    import ROOT
    f = ROOT.TFile.Open(str(path))
    need(f and not f.IsZombie(), f"{path} does not open")
    out = {}
    for k in f.GetListOfKeys():
        o = k.ReadObj()
        if o.InheritsFrom("TH1"):
            n = o.GetNcells()
            axes = []
            for ax in (o.GetXaxis(), o.GetYaxis(), o.GetZaxis()):
                axes.append([ax.GetBinLowEdge(i) for i in range(1, ax.GetNbins() + 2)])
            out[k.GetName()] = ("TH1", o.ClassName(), np.array(axes, dtype=object),
                                np.array([o.GetBinContent(i) for i in range(n)]),
                                np.array([o.GetBinError(i) for i in range(n)]))
        elif o.ClassName().startswith("TParameter"):
            out[k.GetName()] = ("TParameter", o.ClassName(), float(o.GetVal()))
        elif o.ClassName() == "TNamed":
            out[k.GetName()] = ("TNamed", o.GetTitle())
    f.Close()
    return out


def vec(path: Path, name: str = "hXSec2D") -> np.ndarray:
    """The 224-cell vector in GlobalID order, after checking the axes are section 2.5's exactly."""
    import ROOT
    f = ROOT.TFile.Open(str(path))
    h = f.Get(name) if f and not f.IsZombie() else None
    need(bool(h), f"{path} has no {name}")
    ax = ([h.GetXaxis().GetBinLowEdge(i) for i in range(1, h.GetNbinsX() + 2)],
          [h.GetYaxis().GetBinLowEdge(i) for i in range(1, h.GetNbinsY() + 2)])
    v = np.array([h.GetBinContent(ix, iy) for ix in range(1, h.GetNbinsX() + 1) for iy in range(1, h.GetNbinsY() + 1)])
    f.Close()
    need(ax[0] == [float(e) for e in EDGES[0]] and ax[1] == [float(e) for e in EDGES[1]],
         f"C-GRID: {path} {name}: the axes are not section 2.5's exactly")
    need(v.shape == (224,) and np.all(np.isfinite(v)), f"{path} {name}: not a finite 224-vector")
    return v


def named_json(path: Path, name: str) -> dict:
    o = root_objects(path).get(name)
    need(o is not None and o[0] == "TNamed" and o[1], f"{path} has no {name}")
    return json.loads(o[1])


def fix_equal(ro: dict, rr: dict) -> dict:
    """C-FIX: each fixed object of two units' ROOT files equal bit for bit (axes, contents, errors, overflow),
    of the same class, and finite. Shared by the scorer and the pilot's post."""
    fix = {}
    for nm in FIX:
        o, r = ro.get(nm), rr.get(nm)
        if o is None or r is None or o[:2] != r[:2]:
            fix[nm] = False
        elif o[0] == "TH1":
            fix[nm] = bool(o[2].tolist() == r[2].tolist() and bits(o[3]) == bits(r[3]) and bits(o[4]) == bits(r[4])
                           and np.all(np.isfinite(o[3])) and np.all(np.isfinite(o[4])))
        else:
            fix[nm] = bool(bits([o[2]]) == bits([r[2]]) and math.isfinite(o[2]))
    return fix


def bits(a) -> bytes:
    a = np.ascontiguousarray(np.asarray(a, dtype=float))
    return a.tobytes()


# ---------------------------------------------------------------------------------------------- the units


def load(path: Path, keys=None) -> dict:
    with np.load(path, allow_pickle=False) as z:
        out = {k: z[k] for k in (keys if keys is not None else z.files)}
    if "meta" in out:
        out["meta"] = json.loads(str(out["meta"]))
    return out


def ibu(z: dict, K: int) -> np.ndarray:
    ks = z["ks"]
    need(ks.dtype.kind in "iu" and ks.tolist() == CONST["SCAN"], "an IBU product's scan is not the declared one")
    x = np.asarray(z["xsec"][ks.tolist().index(K)], float)
    need(x.shape == (224,) and np.all(np.isfinite(x)), "an IBU vector is not a finite 224-vector")
    return x


def canonical_argv(tree_cfg: dict, conv: str, b, rows: Path) -> list:
    e = tree_cfg["e_r"]
    stage = tree_cfg["inputs"]["staging"]
    subs = {"$CV": str(Path(stage["root"]) / stage["CV"]), "$MC": str(Path(stage["root"]) / stage["MC"])}
    argv = [subs.get(x, x) for x in e["argv"]]
    if conv == "R":
        argv += ["--signal-convention", "minerva", "--oofvc-rows", str(Path(stage["root"]) / rows.name)]
    if b is not None:
        argv += [x.format(b=b) for x in e["replica_argv_extra"]]
    return argv


def check_units(units: Path, pins: dict, tree_cfg: dict, rows: Path) -> tuple[dict, dict]:
    """C-UNITS and C-PINS (codex r1 #10, #11): the exact inventory, every unit's strict receipt, its canonical argv,
    literal CPUs, threads and scan, a complete and uniform runtime, and pins files that cover every unit."""
    names = unit_names()
    want_files = {f"{u}.{x}" for u in names for x in ("npz", "root", "done")}
    have = {p.name for p in units.iterdir()}
    pins_files = sorted(n for n in have if re.fullmatch(r"pins_[A-Za-z0-9_.]+\.json", n))
    extra, missing = have - want_files - set(pins_files), want_files - have
    need(not extra and not missing, f"C-UNITS: inventory: missing {sorted(missing)[:5]}, extra {sorted(extra)[:5]}")
    metas, runtimes = {}, set()
    want_inputs = {"CV": tree_cfg["inputs"]["CV_sha256"], "MC": tree_cfg["inputs"]["MC_sha256"]}
    for u in names:
        r = P.unit_receipt(units, u)
        need(r["ok"], f"C-UNITS: {u}: {r['why']}")
        m = r["meta"]
        conv, b = P.unit_kind(u)
        need(m["argv"] == canonical_argv(tree_cfg, conv, b, rows), f"C-UNITS: {u}: argv is not the canonical one")
        need(m.get("unfolder") == pins["roounfold_lib_sha256"], f"C-UNITS: {u}: unfolder {m.get('unfolder')}")
        need(m.get("cpus") == CONST["CPUS"] and m.get("thread_env") == CONST["THREADS"], f"C-UNITS: {u}: CPUs or threads")
        rt = m.get("runtime", {})
        need(sorted(rt) == sorted(CONST["RUNTIME_KEYS"]) and all(isinstance(v, str) and v and
                                                                   not v.startswith("unavailable") for v in rt.values()),
             f"C-UNITS: {u}: the runtime record is incomplete")
        runtimes.add(json.dumps(rt, sort_keys=True))
        need(m.get("runner_sha256") == pins["own"]["ptmc_run.py"] and m.get("lib_sha256") == pins["own"]["ptmc_lib.py"],
             f"C-PINS: {u}: runner or library")
        need(m.get("code_sha256") == tree_cfg["code_sha256"] and m.get("inputs_sha256") == want_inputs,
             f"C-PINS: {u}: code or inputs")
        need(isinstance(m.get("extract_args_sha256"), str) and HEX64.fullmatch(m["extract_args_sha256"]),
             f"C-NORM: {u}: no valid digest")
        metas[u] = m
    need(len(runtimes) == 1, f"C-UNITS: {len(runtimes)} distinct runtime sets")
    covered = set()
    need(pins_files, "C-PINS: no runner pins file")
    for pf in pins_files:
        p = json.loads((units / pf).read_text())
        need(p.get("pass") is True and p.get("before") == p.get("after"), f"C-PINS: {pf} did not pass")
        bfr = p["before"]
        need(bfr.get("driver") == pins["tree"][TREE_FILES[0]] and bfr.get("config") == pins["tree"][TREE_FILES[1]]
             and bfr.get("runner") == pins["tree"][TREE_FILES[2]] and bfr.get("ptmc_run") == pins["own"]["ptmc_run.py"]
             and bfr.get("ptmc_lib") == pins["own"]["ptmc_lib.py"] and bfr.get("rows") == pins["rows"]
             and bfr.get("join_record") == pins["join"] and bfr.get("roounfold_lib") == pins["roounfold_lib_sha256"],
             f"C-PINS: {pf}: a recorded pin differs")
        for u, outs in p.get("outputs", {}).items():
            need(u in names, f"C-PINS: {pf} names an unknown unit {u}")
            mk = json.loads((units / f"{u}.done").read_text())
            need(outs.get(f"{u}.npz") == mk["sha256"] and outs.get(f"{u}.root") == mk["root_sha256"],
                 f"C-PINS: {pf}: {u}'s outputs differ from its marker")
            covered.add(u)
    need(covered == set(names), f"C-PINS: pins files cover {len(covered)} of {len(names)} units")
    return metas, {"C-UNITS": {"pass": True, "units": len(names), "runtime": json.loads(runtimes.pop())},
                   "C-PINS": {"pass": True, "pins_files": len(pins_files)}}


# ------------------------------------------------------------------------------------------------ the D4


def d4_manifest(d4: Path) -> dict:
    """The staging's manifest reconciled with the fetched directory (codex r1 #8): exactly manifest.json and the
    copied products; each fetched file's sha256 equals the manifest's; the mandatory 000 and 001 copied."""
    mf = d4 / "manifest.json"
    need(mf.is_file(), "C-D4: no staging manifest")
    m = json.loads(mf.read_text())
    copied, absent = m.get("copied", {}), m.get("absent", [])
    have = {p.name for p in d4.iterdir()}
    need(have == set(copied) | {"manifest.json"}, f"C-D4: the fetched files are not the manifest's: "
                                                  f"{sorted(have ^ (set(copied) | {'manifest.json'}))[:5]}")
    for name, rec in copied.items():
        need(sha256(d4 / name) == rec.get("sha256"), f"C-D4: {name} differs from its staging digest")
    for name in ("000_cov_ptpl_minerva_inclusive_6GeV.root", "001_xsec.root"):
        need(name in copied, f"C-IN: the mandatory {name} was not staged")
    return {"copied": set(copied), "absent": [Path(a).name for a in absent]}


def ref_markers(repo: Path) -> dict:
    """The committed REF markers: exactly one per unit (a duplicate, even identical, fails), each a PASS naming its
    unit; the central marker's own bytes pinned."""
    base = repo / REF_RECEIPTS
    need(sha256(repo / CENTRAL_MARKER) == CONST["CENTRAL_MARKER_SHA"], "C-D4: the committed central marker's sha256")
    files = list(base.rglob("c2_replica_b*.done")) + list((base / "units-centrals").glob("c2_central.done"))
    out = {}
    for f in files:
        mk = json.loads(f.read_text())
        need(mk.get("unit") == f.stem and mk.get("verdict") == "PASS" and HEX64.fullmatch(str(mk.get("sha256"))),
             f"C-D4: marker {f}")
        need(f.stem not in out, f"C-D4: two markers for {f.stem}")
        out[f.stem] = mk["sha256"]
    return out


def ref_ibu_ok(z: dict, unit: str, b) -> bool:
    m = z.get("meta", {})
    argv = m.get("argv", [])
    if m.get("unit") != unit or z["ks"].dtype.kind not in "iu" or z["ks"].tolist() != CONST["SCAN"]:
        return False
    if b is None:
        if "--bootstrap-seed" in argv or "--bootstrap-streams" in argv:
            return False
    else:
        if argv.count("--bootstrap-seed") != 1 or argv.count("--bootstrap-streams") != 1:
            return False
        if argv[argv.index("--bootstrap-seed") + 1] != str(b) or argv[argv.index("--bootstrap-streams") + 1] != "three":
            return False
    x = np.asarray(z["xsec"], float)
    return x.shape == (len(CONST["SCAN"]), 224) and bool(np.all(np.isfinite(x)))


def q_r_ok(st: dict, b: int) -> bool:
    return (st.get("bootstrap_seed") == b and st.get("streams") == "three" and st.get("unit_factors") is False
            and st.get("seed_offsets") == CONST["OFFSETS"] and isinstance(st.get("n"), dict)
            and isinstance(st.get("sum"), dict) and set(st["n"]) == {"data", "mc", "bkg"}
            and set(st["sum"]) == {"data", "mc", "bkg"})


# ---------------------------------------------------------------------------------------------- the score


def check_bytes(a, pins: dict) -> None:
    """C-IN / C-PINS on the bytes used, before anything they define is imported (codex r1 #10)."""
    need(set(pins.get("tree", {})) == set(TREE_FILES) and set(pins.get("own", {})) == set(OWN_FILES),
         "C-PINS: the pin manifest is incomplete")
    for f in TREE_FILES:
        need(sha256(a.tree / f) == pins["tree"][f], f"C-PINS: the deploy tree's {f}")
    for f in OWN_FILES:
        need(sha256(HERE / f) == pins["own"][f], f"C-PINS: the scorer's own {f}")
    need(a.rows_sha256 == CONST["ROWS_SHA"] and sha256(a.rows) == CONST["ROWS_SHA"] and pins.get("rows") ==
         CONST["ROWS_SHA"], "C-IN: the rows file")
    text = (a.tree / TREE_FILES[0]).read_text()
    need(all(text.count(line + "\n") == 1 for line in DRIVER_EDGE_LINES), "C-GRID: the deployed driver's edges")


def publication(a, RR, rc) -> tuple:
    """The precision reference, validated before any mask or distance (codex r1 #19)."""
    import ROOT
    pub_path = a.d4 / "000_cov_ptpl_minerva_inclusive_6GeV.root"
    need(sha256(pub_path) == CONST["PUB_SHA"], "C-IN: the publication copy (000)")
    cp = RR.compare()
    f = ROOT.TFile.Open(str(pub_path))
    need(f and not f.IsZombie(), "C-IN: the publication does not open")
    x = np.asarray(cp.flatten_th2d(f.Get("pt_pl_cross_section")), float)
    cov = np.asarray(cp.tmatrix_to_numpy(f.Get("TotalCovariance")), float)
    stat = np.asarray(cp.tmatrix_to_numpy(f.Get("StatOnlyCovariance")), float)
    f.Close()
    need(x.shape == (224,) and cov.shape == (224, 224) and stat.shape == (224, 224)
         and all(np.all(np.isfinite(v)) for v in (x, cov, stat)), "C-CELLS: the publication's operands")
    cells = a.repo / CELLS
    need(sha256(cells) == CONST["CELLS_SHA"], "C-CELLS: the committed cells.root")
    fc = ROOT.TFile.Open(str(cells))
    bound, _ = rc.read_cells(fc)
    fc.Close()
    bound = np.asarray(bound, int)
    for name, M in (("StatOnlyCovariance", stat), ("TotalCovariance", cov)):
        try:
            rc.require_same_cells(bound, rc.reported_indices((np.diag(M) > 0).reshape(rc.GRID_SHAPE)),
                                  "committed cells", f"{name}'s mask")
        except Exception as e:  # reported_cells.CellIdentityError and its kin
            raise Stop(f"C-CELLS: {e}") from None
    need(bound.size == CONST["NDF"] and np.unique(bound).size == bound.size, "C-CELLS: the cell count")

    def dist(v):
        chi2, ndf, _ = cp.chi2_with_cov(np.asarray(v, float) - x, cov, "", report=False)
        need(math.isfinite(chi2) and ndf > 0, "a non-finite distance")
        return chi2 / ndf, ndf
    return dist, bound


def score(a) -> dict:
    pins = json.loads(Path(a.pins).read_text())
    check_bytes(a, pins)
    sys.path.insert(0, str(a.tree / "2d-unfolding" / "ref_c2c1"))
    import ref_c2c1_read as RR
    sys.path.insert(0, str(a.tree / "2d-unfolding" / "oofvc"))
    import oofvc_lib as L
    import reported_cells as rc
    for mod, f in ((RR, TREE_FILES[3]), (L, TREE_FILES[7]), (rc, TREE_FILES[6])):
        need(Path(mod.__file__).resolve() == (a.tree / f).resolve(), f"C-PINS: {mod.__name__} resolved elsewhere")
    controls, printed = {}, {}
    tree_cfg = json.loads((a.tree / TREE_FILES[1]).read_text())
    scan = list(CONST["SCAN"])
    metas, c = check_units(a.units, pins, tree_cfg, a.rows)
    controls.update(c)
    man = d4_manifest(a.d4)
    e_r = a.d4 / "001_xsec.root"
    need(sha256(e_r) == CONST["E_R_SHA"], "C-IN: the mandatory E_R central (001) is not a5c13fc3")
    dist, cells_idx = publication(a, RR, rc)
    x_er = vec(e_r)
    d_er, ndf = dist(x_er)
    chi2 = d_er * ndf
    need(ndf == CONST["NDF"] and math.isfinite(chi2) and abs(chi2 / CONST["C_PUB"] - 1) <= 1e-8,
         f"C-PUB: chi2 {chi2} over {ndf}")
    controls["C-CELLS"] = {"pass": True, "cells": int(cells_idx.size)}
    controls["C-PUB"] = {"pass": True, "chi2": chi2, "ndf": ndf}
    names = unit_names()
    X_OF = {u: vec(a.units / f"{u}.root") for u in names}  # C-GRID on every unit, exactly
    X_IBU = {}
    for u in names:  # only the vectors the score uses are kept (codex r1 #24)
        z = load(a.units / f"{u}.npz", ["ks", "xsec"])
        X_IBU[u] = {K: ibu(z, K) for K in scan}
    controls["C-GRID"] = {"pass": True}
    # C-FIX: R against production, bit for bit, axes and errors included, finite
    ro, rr = root_objects(a.units / "p_off_c.root"), root_objects(a.units / "p_R_c.root")
    fix = fix_equal(ro, rr)
    need(all(fix.values()), f"C-FIX: {fix}")
    controls["C-FIX"] = {"pass": True, "equal": fix}
    # C-NORM
    ref_norm = metas["p_off_c"]["extract_args_sha256"]
    bad = [u for u in names if metas[u]["extract_args_sha256"] != ref_norm]
    need(not bad, f"C-NORM: {bad[:5]}")
    controls["C-NORM"] = {"pass": True, "sha256": ref_norm}
    # C-MOVE: the central sets, counts and removal
    rows = load(a.rows)
    need(metas["p_R_c"].get("oofvc_counts") == CONST["COUNTS"], f"C-MOVE: counts {metas['p_R_c'].get('oofvc_counts')}")
    entries = np.asarray(rows["entry"], np.int64)
    need(np.unique(entries).size == entries.size, "C-MOVE: the rows file repeats an entry")
    app = np.asarray(load(a.units / "p_R_c.npz", ["appended_entry"])["appended_entry"], np.int64)
    gid = L.global_index(rows["reco_pt"], rows["reco_pz"], *EDGES)
    wt, wr = np.asarray(rows["w_truth"], float), np.asarray(rows["w_reco"], float)
    w_ok = (wt >= 0) & (wt < 1e4) & (wr >= 0) & (wr < 1e4)
    need(np.array_equal(app, entries[(gid >= 0) & w_ok]), "C-MOVE: the appended set is not the in-grid, weight-passing "
                                                          "rows in order")
    outside = np.setdiff1d(entries, app)
    need(app.size + outside.size == entries.size and np.intersect1d(app, outside).size == 0,
         "C-MOVE: the appended and reco-outside sets do not partition the rows file")
    dr = {u: metas[u]["controls"]["C-DRAW-R"] for u in ("p_off_c", "p_R_c")}
    grew = (dr["p_R_c"]["n_original"] + dr["p_R_c"]["n_appended"]) - (dr["p_off_c"]["n_original"]
                                                                     + dr["p_off_c"]["n_appended"])
    need(grew == CONST["COUNTS"]["appended"], f"C-MOVE: the signal arrays grow by {grew}")
    pot = ro["potScale"][2]
    rect = ((rows["reco_pt"] >= EDGES[0][0]) & (rows["reco_pt"] <= EDGES[0][-1]) & (rows["reco_pz"] >= EDGES[1][0])
            & (rows["reco_pz"] <= EDGES[1][-1]))
    filled = rect & np.isfinite(wr) & (wr >= 0) & (wr < 1e6)
    expect = np.bincount(gid[filled & (gid >= 0)], weights=wr[filled & (gid >= 0)] * pot, minlength=224)
    b_off, b_r = vec(a.units / "p_off_c.root", "hBkgReco2D"), vec(a.units / "p_R_c.root", "hBkgReco2D")
    removed = b_off - b_r
    need(np.all(np.abs(removed - expect) <= 1e-12 * np.abs(b_off)) and np.all(removed[b_off == 0] == 0),
         "C-MOVE: the removal per reco cell")
    controls["C-MOVE"] = {"pass": True, "counts": metas["p_R_c"]["oofvc_counts"],
                          "max_dev_over_cell": float(np.max(np.divide(np.abs(removed - expect), np.abs(b_off),
                                                                      out=np.zeros(224), where=b_off != 0)))}
    printed["upper_edge_rows"] = int(np.sum(rect & (gid < 0)))
    # C-MOVE in every R replica: ordered, multiplicity-preserving fill records against p_off_b1's, streamed
    fill_keys = ("fill_entry", "fill_pt", "fill_pz", "fill_w")
    ref = load(a.units / "p_off_b1.npz", fill_keys)
    n_bkg = named_json(a.units / "p_off_b1.root", "p1Streams")["n"]["bkg"]

    def fill_ok(z):
        e = np.asarray(z["fill_entry"])
        n = e.size
        return (e.dtype.kind in "iu" and np.unique(e).size == n and (n == 0 or (e.min() >= 0 and e.max() < n_bkg))
                and all(np.asarray(z[k]).shape == (n,) for k in fill_keys)
                and all(np.all(np.isfinite(np.asarray(z[k], float))) for k in fill_keys[1:]))
    need(fill_ok(ref) and ref["fill_entry"].size > 0, "C-MOVE: p_off_b1's fill record")
    keep = ~np.isin(np.asarray(ref["fill_entry"], np.int64), entries)
    want = {k: np.asarray(ref[k])[keep] for k in fill_keys}
    want_inj = P.injected_entries({"entry": want["fill_entry"], "pt": want["fill_pt"], "pz": want["fill_pz"]},
                                  EDGES[0][0], EDGES[0][-1], EDGES[1][0], EDGES[1][-1])
    del ref
    for u in names:
        if not u.startswith("p_R_b"):
            continue
        z = load(a.units / f"{u}.npz", fill_keys + ("inj_entries",))
        need(fill_ok(z) and all(np.array_equal(np.asarray(z[k]), want[k]) for k in fill_keys)
             and np.array_equal(np.asarray(z["inj_entries"], np.int64), want_inj), f"C-MOVE: replica sets {u}")
    controls["C-MOVE"]["replica_sets"] = True
    # C-COUPLE, and C-SIM's coverage by index
    for u in ("p_off_c", "p_R_c"):
        cov = set(metas[u]["controls"]["C-SIM"].get("covered", []))
        need(set(cells_idx.tolist()) <= cov, f"C-SIM coverage: {u} misses reported cells")
    controls["C-COUPLE"] = {u: metas[u]["controls"]["C-COUPLE"] for u in ("p_off_c", "p_R_c")}
    printed["C-SUPPORT"] = metas["p_R_c"].get("support")
    printed["completeness_counts"] = {u: metas[u].get("completeness_counts") for u in names if u.startswith("p_R_b")}
    printed["suppressed_moved_support_cells"] = metas["p_R_c"].get("suppressed_moved_support_cells")
    # C-BASE (mandatory half)
    r = P.rel_close(X_OF["p_off_c"], x_er, 1e-8)
    need(r["pass"], f"C-BASE: E_R {r}")
    controls["C-BASE"] = {"pass": True, "e_r_max_rel": r["max_rel"]}
    # C-D4, per product
    need(sha256(a.repo / READOUT) == CONST["READOUT_SHA"], "C-D4: the committed readout's sha256")
    readout = json.loads((a.repo / READOUT).read_text())
    markers = ref_markers(a.repo)
    staged = readout["staged_sha256"]
    absent, mismatch, ref_c2, q_r = [], [], {}, {}
    optional = [("c2_central.npz", "c2_central", None)] + [(f"c2_replica_b{b}.npz", f"c2_replica_b{b}", b)
                                                           for b in seeds()]
    for name, unit, b in optional:
        if name not in man["copied"]:
            (absent if name in man["absent"] else mismatch).append(name)
            continue
        try:
            z = load(a.d4 / name, ["ks", "xsec", "meta"])
            ok = sha256(a.d4 / name) == markers.get(unit) and ref_ibu_ok(z, unit, b)
        except (OSError, ValueError, KeyError, IndexError):
            ok = False
        if ok:
            ref_c2[b] = {K: ibu(z, K) for K in scan}
        else:
            mismatch.append(name)
    for b in seeds():
        name = P.staged_index(b)
        if name not in man["copied"]:
            (absent if name in man["absent"] else mismatch).append(name)
            continue
        try:
            p = a.d4 / name
            st = named_json(p, "p1Streams")
            ok = sha256(p) == staged.get(CONST["Q_R_SRC"].format(b=b)) and q_r_ok(st, b)
            if ok:
                q_r[b] = {"x": vec(p), "st": st, "path": p}
        except Stop:
            ok = False
        if not ok:
            mismatch.append(name)
    # every accepted product's own checks, whatever else is absent (codex r1 #17)
    if None in ref_c2:
        rb = [P.rel_close(X_IBU["p_off_c"][K], ref_c2[None][K], 1e-8) for K in scan]
        need(all(x["pass"] for x in rb), "C-BASE: REF's c2_central")
        controls["C-BASE"]["ibu_max_rel"] = max(x["max_rel"] for x in rb)
    elif "c2_central.npz" in absent:
        want_d = {int(k): v for k, v in readout["D_IBU_every_K"].items()}
        need(all(P.rel_close([dist(X_IBU["p_off_c"][K])[0]], [want_d[K]], 1e-6)["pass"] for K in scan),
             "C-BASE: the D_IBU fallback")
        controls["C-BASE"]["ibu_fallback"] = "distances (c2_central cleanly absent)"
    repoff = None
    if 1 in ref_c2 and 1 in q_r:
        r1 = P.rel_close(X_OF["p_off_b1"], q_r[1]["x"], 1e-8)
        r2 = [P.rel_close(X_IBU["p_off_b1"][K], ref_c2[1][K], 1e-8) for K in (10, 5)]
        ref_q, ref_p = named_json(q_r[1]["path"], "re2Refinement"), named_json(a.units / "p_off_b1.root", "re2Refinement")
        exact = ("params", "signed_sum", "n_data", "n_injected")
        fitted = ("refined_sum", "clipped_fraction")
        agg = (all(k in ref_q and k in ref_p and ref_q[k] == ref_p[k] for k in exact)
               and all(k in ref_q and k in ref_p and P.rel_close([ref_p[k]], [ref_q[k]], 1e-8)["pass"] for k in fitted))
        repoff = bool(r1["pass"] and all(x["pass"] for x in r2) and agg)
        controls["C-REPOFF"] = {"pass": repoff, "e_r": r1["max_rel"], "ibu": [x["max_rel"] for x in r2],
                                "refinement": agg}
    bad = []
    for b, q in q_r.items():  # C-DRAW-R's aggregate half, on every accepted Q_R seed
        d = metas[f"p_R_b{b}"]["controls"]["C-DRAW-R"]
        rec = named_json(a.units / f"p_R_b{b}.root", "p1Streams")
        st = q["st"]
        if not (st["n"]["data"] == d["n_data"] and st["sum"]["data"] == d["data_sum"]
                and st["n"]["mc"] == d["n_original"] and st["sum"]["mc"] == d["original_sum"]
                and st["n"]["bkg"] == rec["n"]["bkg"] and st["sum"]["bkg"] == rec["sum"]["bkg"]):
            bad.append(b)
    need(not bad, f"C-DRAW-R against Q_R's p1Streams: seeds {bad[:10]}")
    controls["C-DRAW-R"] = {"pass": True, "aggregate_seeds": len(q_r)}
    controls["C-D4"] = {"absent": absent, "mismatch": mismatch}
    disp = P.disposition(True, True, bool(absent), bool(mismatch), repoff)
    controls["disposition"] = disp
    need(disp != "stop", f"the disposition is STOP: absent {absent[:5]}, mismatch {mismatch[:5]}, C-REPOFF {repoff}")
    # the statistic, each arm after C-SHAPE and the binding's conditioning guard
    arms = {}
    for K in (10, 5):
        arms[("R", K)] = (X_IBU["p_R_c"][K] - X_OF["p_R_c"],
                          np.array([X_IBU[f"p_R_b{b}"][K] - X_OF[f"p_R_b{b}"] for b in seeds()]))
        if disp == "formed":
            arms[("B", K)] = (ref_c2[None][K] - x_er, np.array([ref_c2[b][K] - q_r[b]["x"] for b in seeds()]))
    for key, (delta, D) in arms.items():
        sg = P.shape_gate(delta, D, rank=CONST["RANK"], n=CONST["N"])
        need(sg["pass"], f"C-SHAPE: {key} {sg}")
        printed.setdefault("lambda_ratio_rank_over_top", {})[f"{key[0]}_K{key[1]}"] = sg["lambda_ratio_rank_over_top"]
        cond = P.conditioning(D, rank=CONST["RANK"])
        need(cond["pass"], f"the conditioning guard: {key} lambda_r/lambda_1 = {cond['ratio']} < 1e-10")
    readings = {}
    for (arm, K), (delta, D) in arms.items():
        t = RR.t_and_null(delta, D, CONST["RANK"])
        need(P.finite_t(t), f"C-SHAPE: a non-finite T or bar in {arm} K={K}")
        readings[f"{arm}_K{K}"] = {**t, "reading": RR.classify_t(t, P.WORDS),
                                   "T_over_q95": (t["T"] / t["q95"]) if t["q95"] > 0 else None}
    controls["C-SHAPE"] = {"pass": True}
    r1 = readings["R_K10"]["reading"]
    bread = readings["B_K10"]["reading"] if disp == "formed" else None
    st = P.statement(r1, disp, bread)
    st.update(K=10, rank=CONST["RANK"], scope="statistical detectability in the retained rank-50 modes, at K = 10",
              protocols={"R": "under R (one shared refinement)",
                         "B": ("the production convention, in REF-C2C1's separate-refit protocol"
                               if disp == "formed" else None)},
              triples={arm: {k: readings[f"{arm}_K10"][k] for k in ("T", "q95", "max")}
                       for arm in (("R", "B") if disp == "formed" else ("R",))})
    rec = {"schema": "ptmc-score/2", "controls": controls, "readings": readings, "primary_K": 10,
           "disposition": disp, "PTMC-R1": r1, "PTMC-B": bread, "statement": st}
    # printed, read by nothing
    if disp == "formed":
        dB, DB = arms[("B", 10)]
        CB = np.cov(DB, rowvar=False, ddof=1)
        Dp = np.array([X_IBU[f"p_off_b{b}"][10] - X_OF[f"p_off_b{b}"] for b in range(1, CONST["N_OFF"] + 1)])
        dp = X_IBU["p_off_c"][10] - X_OF["p_off_c"]
        Cplus = RR.pinv_rank(CB, CONST["RANK"])
        printed["C-PROTO"] = {**P.proto_eps(Dp, DB[:CONST["N_OFF"]], np.diag(CB), dp, dB),
                              "whitened": [float(np.sqrt(max(d @ Cplus @ d, 0))) for d in (Dp - DB[:CONST["N_OFF"]])],
                              "whitened_central": float(np.sqrt(max((dp - dB) @ Cplus @ (dp - dB), 0)))}
    printed["hartlap"] = (CONST["N"] - CONST["RANK"] - 2) / (CONST["N"] - 1)
    printed["D_under_R"] = {"D_E_R": dist(X_OF["p_R_c"])[0], "D_IBU": {K: dist(X_IBU["p_R_c"][K])[0] for K in scan}}
    for K in (10, 5):
        per = {}
        for b in seeds():
            de, di = dist(X_OF[f"p_R_b{b}"])[0], dist(X_IBU[f"p_R_b{b}"][K])[0]
            per[b] = (di / de) if (de != 0 and math.isfinite(de) and math.isfinite(di)) else None
        vals = [v for v in per.values() if v is not None and math.isfinite(v)]
        printed[f"rho_K{K}"] = {"per_seed": per, "n_defined": len(vals),
                                "interval": [float(np.quantile(vals, 0.05)), float(np.quantile(vals, 0.95))]
                                if vals else None}
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
    if a.out.exists() or (a.out.parent / "STOP.json").exists():
        print(f"refusing: {a.out} or a STOP.json exists", file=sys.stderr)
        return 2
    try:
        rec = score(a)
    except Exception as e:  # every failure is a STOP, never a reading (codex r1 #22)
        why = str(e) if isinstance(e, Stop) else f"{type(e).__name__}: {e}"
        stop = {"schema": "ptmc-stop/1", "stopped": True, "why": why,
                "traceback": None if isinstance(e, Stop) else traceback.format_exc()[-4000:]}
        (a.out.parent / "STOP.json").write_text(json.dumps(stop, indent=1) + "\n")
        print(f"STOP: {why}", file=sys.stderr)
        return 3
    a.out.write_text(json.dumps(rec, indent=1, default=float) + "\n")
    print(json.dumps({"PTMC-R1": rec["PTMC-R1"], "PTMC-B": rec["PTMC-B"], "disposition": rec["disposition"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
