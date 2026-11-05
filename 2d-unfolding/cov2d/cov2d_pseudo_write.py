"""COV2D's pseudo-data job, step B (COV2D-DECLARATION.md sections 4.2, 4.4, 9.4 and 9.11): section 9.4 first, then
every nature's data file and its truth cross section, from step A's products (cov2d_pseudo.py). root_6_28 (PyROOT, no
uproot).

* Section 9.4 (the director's R1, 2026-11-04), before any data file is written: step A's CV truth at r = 1, normalized
  by the driver's own ``extract_cross_section_2d`` at completeness 1 with the CV flux, must equal E_R's own
  ``extract_cross_section_2d(hTruth2D, hOFCompleteness2D, ...)`` to 1e-12 relative on E_R's 205 reported cells, with
  two cross-checks on E_R's file: hTruth2D equals hOFInputTruth2D, and hOFTruthDenom2D at completeness 1 equals the
  reference. E_R's flux, data POT and nucleon count are its own records; the CV flux read here must equal its hFlux_pt.
* The data files: each nature's counts through ``cov2d_writer.expand`` (signal rows, then background rows) and
  ``write_data_file`` (one tree cycle, addendum A1), with $CV's dataPOTUsed. Each is read back (section 9.11): exactly
  sum k rows over the rows that pass; its per-reco-cell histogram equals the per-cell sum of the counts; every row's
  (measured, measured_pz) is a passing row's (sim, sim_pz); and d_T's total is within 5 Poisson sigma of sum lambda+
  over the rows that pass. Its sha256 is recorded (the driver's dataFileSha256).
* The truth cross sections: each nature's clipped truth per cell through ``extract_cross_section_2d`` at completeness
  1, with the nature's flux: the drawn Flux universe's integral (``load_flux_universe_bins``, as ``--universe
  Flux:IDX`` uses it), or the CV flux for the realization.

Inputs (COV2D addendum A2, Joseph's ruling of 2026-11-05): the three shared inputs (E_R, the MC file, the flux-universe
file) are first staged into ``<out>/stage`` by ``cov2d.stage_copy``, each an O_NOATIME copy hashed against its pin,
with the shared file's atime recorded before and after (a record, not a stop). ROOT opens files plainly, so it gets a
second, working copy in $TMPDIR, made from the staged copy through O_NOATIME; the staged copies are never opened
plainly. The guard watches only the staged copies: their atime at the start and at the end, both values recorded
(``atime_ns``); any move STOPs.

  python cov2d_pseudo_write.py --a DIR --out DIR [--er PATH] [--mcfile PATH] [--flux-universe-file PATH]

MEASURES: the data files and truths of declared natures, and section 9.4. CANNOT AUTHORIZE: an unfold, or a verdict.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
DEPLOY = REPO     # the checkout this code runs from: the job's deploy at M
CLIP = REPO / "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-cov2d/clip"
for p in (HERE, CLIP, REPO / "2d-unfolding" / "re2"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
import cov2d as c  # noqa: E402
import cov2d_writer as cw  # noqa: E402

A_ROOT = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/baseline_flux"
PINS = {   # RE-2's pins (re2/run/launch/re2_env.sh:11-16; re2c_rollup.py:110)
    "er": ("/pscratch/sd/j/josephrb/2d-closeout-re2-20261023/partb/out/ER/xsec.root",
           "a5c13fc38d64242bc9ee459fac87568a2f97fddf7a3ac97cc6f91eb4c2a31cef"),
    "mcfile": (f"{A_ROOT}/runEventLoopMC_MEFHC.root", "d40aea69235cdc98644e1bb3e622e579d6b81904c004c83fe50465079989f316"),
    "flux_universe_file": (f"{A_ROOT}/flux_integral_universes_MEFHC.root",
                           "5eecae84509ba8ededbe8fdee63508d8e36cd057cc0547a940383f80248580eb"),
}
FLUX_HIST = "pTmu_reweightedflux_integrated"   # the driver's --flux-hist default, as E_R ran
TOL_94 = 1e-12
SIGMA_9_11 = 5.0


def copy_noatime(src: str, dst_dir: Path, want: str | None) -> tuple[Path, str]:
    """Read src through O_NOATIME, check its sha256 (unless want is None), and write a private copy for ROOT."""
    fd = os.open(src, os.O_RDONLY | os.O_NOATIME)
    try:
        chunks = []
        while True:
            b = os.read(fd, 1 << 24)
            if not b:
                break
            chunks.append(b)
    finally:
        os.close(fd)
    data = b"".join(chunks)
    got = hashlib.sha256(data).hexdigest()
    if want is not None and got != want:
        raise c.Refusal(f"{src} sha256 {got} != pinned {want}")
    dst = dst_dir / Path(src).name
    dst.write_bytes(data)
    return dst, got


def driver():
    import re2_driver
    return re2_driver


def th2(f, name) -> np.ndarray:
    h = f.Get(name)
    if not h:
        raise c.Refusal(f"missing {name}")
    return np.array([[h.GetBinContent(i, j) for j in range(1, h.GetNbinsY() + 1)]
                     for i in range(1, h.GetNbinsX() + 1)])


def to_th2(drv, name: str, a: np.ndarray):
    h = drv.make_th2d(name, name, drv.PT_EDGES, drv.PZ_EDGES)
    for i in range(a.shape[0]):
        for j in range(a.shape[1]):
            h.SetBinContent(i + 1, j + 1, float(a[i, j]))
    return h


def xsec(drv, counts: np.ndarray, completeness: np.ndarray, flux_bins: np.ndarray, data_pot: float,
         n_nucleons: float) -> np.ndarray:
    """The driver's extract_cross_section_2d on numpy cell arrays (pT, p_par)."""
    import ROOT
    h = drv.extract_cross_section_2d(to_th2(drv, "hU", counts), to_th2(drv, "hC", completeness),
                                     np.asarray(flux_bins, float), float(data_pot), float(n_nucleons),
                                     drv.PT_EDGES, drv.PZ_EDGES)
    out = np.array([[h.GetBinContent(i, j) for j in range(1, h.GetNbinsY() + 1)]
                    for i in range(1, h.GetNbinsX() + 1)])
    ROOT.SetOwnership(h, True)
    return out


def rel(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.max(np.abs(a - b)) / np.max(np.abs(b)))


def section_9_4(drv, er_copy: Path, truth_cv_r1: np.ndarray, flux_cv: np.ndarray, data_pot: float) -> dict:
    """Section 9.4 and its two cross-checks, on E_R's 205 reported cells."""
    import ROOT
    f = ROOT.TFile.Open(str(er_copy))
    T, C, I, D, X = (th2(f, n) for n in ("hTruth2D", "hOFCompleteness2D", "hOFInputTruth2D", "hOFTruthDenom2D",
                                          "hXSec2D"))
    hf = f.Get("hFlux_pt")
    flux_er = np.array([hf.GetBinContent(i) for i in range(1, hf.GetNbinsX() + 1)])
    pot_er = float(f.Get("dataPOT").GetVal())
    nn_er = float(f.Get("nNucleons").GetVal())
    f.Close()
    cells = X > 0
    ones = np.ones_like(T)
    ref = xsec(drv, T, C, flux_er, pot_er, nn_er)
    denom = xsec(drv, D, ones, flux_er, pot_er, nn_er)
    ours = xsec(drv, truth_cv_r1.reshape(T.shape), ones, flux_cv, data_pot, drv.TRACKER_FIDUCIAL_N_NUCLEONS)
    out = {"cells": int(cells.sum()),
           "hTruth2D_equals_hOFInputTruth2D": bool(np.array_equal(T, I)),
           "denominator_vs_reference": rel(denom[cells], ref[cells]),
           "truth_code_vs_reference": rel(ours[cells], ref[cells]),
           "flux_equal": bool(np.array_equal(np.asarray(flux_cv, float), flux_er)),
           "data_pot_equal": data_pot == pot_er, "n_nucleons_equal": drv.TRACKER_FIDUCIAL_N_NUCLEONS == nn_er}
    out["pass"] = (out["cells"] == 205 and out["hTruth2D_equals_hOFInputTruth2D"]
                   and out["denominator_vs_reference"] <= TOL_94 and out["truth_code_vs_reference"] <= TOL_94
                   and out["flux_equal"] and out["data_pot_equal"] and out["n_nucleons_equal"])
    return out


def read_back(path: Path) -> dict:
    """The data tree as numpy. RDataFrame hands a UChar_t leaf back as one-character strings, so the pass leaf is read
    through an int column defined in the frame."""
    import ROOT
    df = ROOT.RDataFrame("data", str(path)).Define("measured_pass_int", "int(measured_pass)")
    a = df.AsNumpy(["measured", "measured_pz", "measured_pass_int"])
    return {"measured": np.asarray(a["measured"], np.float64), "measured_pz": np.asarray(a["measured_pz"], np.float64),
            "measured_pass": np.asarray(a["measured_pass_int"], np.int64)}


def pair_keys(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """(x, y) float64 pairs as 16-byte keys, so membership is bitwise."""
    xy = np.ascontiguousarray(np.stack([np.asarray(x, np.float64), np.asarray(y, np.float64)], axis=1))
    return xy.view(np.dtype((np.void, 16))).ravel()


def section_9_11(back: dict, sig: dict, bkg: dict, ks: np.ndarray, kb: np.ndarray, plus_passed: float | None,
                 cp) -> dict:
    ps_, pb_ = np.asarray(sig["sim_pass"]) != 0, np.asarray(bkg["sim_background_pass"]) != 0
    want = int(ks[ps_].sum() + kb[pb_].sum())
    n = int(back["measured"].size)
    _, cell_back = cp.reco_cell(back["measured"], back["measured_pz"], back["measured_pass"])
    _, cell_s = cp.reco_cell(np.asarray(sig["sim"], float), np.asarray(sig["sim_pz"], float), sig["sim_pass"])
    _, cell_b = cp.reco_cell(np.asarray(bkg["sim_background"], float), np.asarray(bkg["sim_background_pz"], float),
                             bkg["sim_background_pass"])
    nc = cp.N_CELLS
    h_back = np.bincount(cell_back[cell_back >= 0], minlength=nc)
    h_want = (np.bincount(cell_s[cell_s >= 0], weights=ks[cell_s >= 0], minlength=nc)
              + np.bincount(cell_b[cell_b >= 0], weights=kb[cell_b >= 0], minlength=nc))
    allowed = np.concatenate([pair_keys(sig["sim"], sig["sim_pz"])[ps_],
                              pair_keys(bkg["sim_background"], bkg["sim_background_pz"])[pb_]])
    member = np.isin(pair_keys(back["measured"], back["measured_pz"]), allowed)
    out = {"rows": n, "rows_expected": want, "rows_equal": n == want,
           "reco_cells_equal": bool(np.array_equal(h_back, h_want.astype(np.int64))),
           "rows_not_a_passing_row": int((~member).sum()),
           "pass_leaf_all_one": bool(np.all(back["measured_pass"] == 1))}
    ok = out["rows_equal"] and out["reco_cells_equal"] and out["rows_not_a_passing_row"] == 0 and out["pass_leaf_all_one"]
    if plus_passed is not None:
        z = (n - plus_passed) / np.sqrt(plus_passed)
        out["realization_z"] = float(z)
        ok = ok and abs(z) <= SIGMA_9_11
    out["pass"] = bool(ok)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True, help="step A's output directory")
    ap.add_argument("--out", required=True)
    for k, (path, _) in PINS.items():
        ap.add_argument("--" + k.replace("_", "-"), default=path)
    ap.add_argument("--no-pins", action="store_true", help="tests only: skip the digest pins")
    a = ap.parse_args(argv)
    import ROOT
    import clip_probe as cp
    ROOT.gROOT.SetBatch(True)
    ROOT.TH1.AddDirectory(False)   # extract_cross_section_2d clones into a fixed name on every call
    drv = driver()

    t0 = time.time()
    A = Path(a.a)
    rec_a = json.loads((A / "pseudo_a.json").read_text())
    if rec_a.get("verdict") != "PASS":
        raise c.Refusal(f"step A's verdict is {rec_a.get('verdict')}")
    M = c.deploy_head(DEPLOY)     # before any work: a dirty deploy is refused here
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=False)
    rec = {"truth": rec_a["truth"], "host": os.uname().nodename, "root": ROOT.gROOT.GetVersion(), "stop": [], "pins_checked": not a.no_pins,
           "M": M}
    srcs = {k: getattr(a, k) for k in PINS}
    stage = out / "stage"
    stage.mkdir()
    rec["staged"] = {k: c.stage_copy(src, stage, None if a.no_pins else PINS[k][1], f"{k}_{Path(src).name}")
                     for k, src in srcs.items()}
    rec["shared_atime_moved"] = [v["src"] for v in rec["staged"].values() if v["src_atime_moved"]]   # a record only
    staged = {k: v["path"] for k, v in rec["staged"].items()}
    before = c.atime_ns(staged.values())     # the guard watches the staged copies only
    with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as td:
        copies = {k: copy_noatime(p, Path(td), None if a.no_pins else PINS[k][1]) for k, p in staged.items()}   # ROOT's
        rec["inputs"] = {k: {"path": srcs[k], "staged": staged[k], "sha256": v[1]} for k, v in copies.items()}
        flux_cv = drv.load_flux_bins(str(copies["mcfile"][0]), FLUX_HIST, drv.PT_EDGES)[0]
        cells = np.load(A / "cells.npz")
        data_pot = float(rec_a["pot"]["data"])
        rec["section_9_4"] = section_9_4(drv, copies["er"][0], cells["truth_cv_r1"], flux_cv, data_pot)
        if not rec["section_9_4"]["pass"]:
            rec["stop"].append(f"section 9.4: {rec['section_9_4']}")
        else:
            sig, bkg = dict(np.load(A / "reco_signal.npz")), dict(np.load(A / "reco_background.npz"))
            shape = (len(drv.PT_EDGES) - 1, len(drv.PZ_EDGES) - 1)
            truth_x, files = [], []
            for k, nat in enumerate(rec_a["natures"]):
                seed, toy = nat["seed"], rec_a["toys"][k]
                if toy["seed"] != seed:
                    raise c.Refusal(f"step A's records are out of order at {k}")
                z = np.load(A / f"counts_{seed}.npz")
                ks, kb = z["signal"].astype(np.int64), z["background"].astype(np.int64)
                cols = cw.concat(cw.expand(sig["sim"], sig["sim_pz"], sig["sim_pass"], ks),
                                 cw.expand(bkg["sim_background"], bkg["sim_background_pz"],
                                           bkg["sim_background_pass"], kb))
                path = out / f"data_{seed}.root"
                cw.write_data_file(path, cols, data_pot)
                chk = section_9_11(read_back(path), sig, bkg, ks, kb,
                                   toy["sum_lambda_plus_passed"] if nat["role"] == "realization" else None, cp)
                files.append({"seed": seed, "role": nat["role"], "path": str(path),
                              "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "section_9_11": chk})
                if not chk["pass"]:
                    rec["stop"].append(f"section 9.11: seed {seed}: {chk}")
                flux = [u for u in nat["universes"] if u.startswith(c.FLUX + ":")]
                fb = (drv.load_flux_universe_bins(str(copies["flux_universe_file"][0]), int(flux[0].split(":")[1]),
                                                  drv.PT_EDGES, flux_cv) if flux else flux_cv)
                truth_x.append(xsec(drv, cells["truth_clipped"][k].reshape(shape), np.ones(shape), fb, data_pot,
                                    drv.TRACKER_FIDUCIAL_N_NUCLEONS))
            rec["files"] = files
            np.savez(out / "truth_xsec.npz", xsec=np.stack(truth_x), seeds=np.array([n["seed"] for n in rec_a["natures"]]))
    rec["atime_moved"], rec["atime_ns"] = c.atime_guard(before, c.atime_ns(staged.values()))
    if rec["atime_moved"]:
        rec["stop"].append(f"atime moved on {rec['atime_moved']}")
    if c.deploy_head(DEPLOY) != rec["M"]:
        rec["stop"].append(f"the deploy moved off {rec['M']} during step B")
    rec["verdict"] = "STOP" if rec["stop"] else "PASS"
    rec["seconds"] = round(time.time() - t0, 1)
    (out / "pseudo_b.json").write_text(json.dumps(rec, indent=1, sort_keys=True))
    print(f"COV2D-PSEUDO-B {rec['truth']} {rec['verdict']} files={len(rec.get('files', []))} stops={len(rec['stop'])}")
    if rec["shared_atime_moved"]:
        print(f"SHARED-ATIME (a record, not a stop) moved during staging on {rec['shared_atime_moved']}")
    for x in rec["stop"][:20]:
        print(f"STOP {x}")
    return 0 if rec["verdict"] == "PASS" else 3


if __name__ == "__main__":
    sys.exit(main())
