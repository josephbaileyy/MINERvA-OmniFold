#!/usr/bin/env python3
"""REF-C2C1: c2 (binned IBU on E_R's own 2D inputs) and c1 (E_R's pipeline plus the joint-test estimator's four
deterministic keys), each by running E_R's own driver in-process with one seam changed (frozen driver).

Declaration: ``docs/orchestration/state/measurement-paper/5d-community-20261024/REF-C2C1-DECLARATION.md``, bound at
step one by ``REF-C2C1-BINDING-1.md`` (no universe pass). Every number comes from ``config.json`` beside this file.

E_R's driver, ``2d-unfolding/re2/re2_driver.py`` (digest-pinned), runs with E_R's recorded argv (``re2/run/
partb_runs.tsv`` rows ER and S1_b). Its inputs, background, refinement, extraction and output are E_R's by
construction; only the seam named below differs. (The pinned driver equals E_R's deploy blob dbdad2f9 but for the
COV2D ``--data-file`` option, inert without that flag.)

  c2   the driver's one OmniFold call (``OmniFold_helper_functions.omnifold``) is replaced by binned D'Agostini IBU on
       the same arrays: the MC truth and reco on E_R's own 14 x 16 grid (``re2_driver.PT_EDGES``/``PZ_EDGES``), the
       response from the matched MC rows (``w_reco``) over the truth rows (``w_truth``), the measured histogram the
       sum of E_R's per-event refined weights w~ per reco bin, the prior the MC truth. RooUnfoldBayes does it in
       production; ``dagostini`` is the same update in numpy, the tests' seam and the C-ROO comparator. The call
       returns, per truth-passing MC event, IBU's unfolded/prior in its truth bin, so the driver's own fill
       (``hUnfold2D``, ratio x w_truth) is IBU's unfolded histogram, and its own extraction (completeness, flux,
       target, POT, the area Jacobian) gives hXSec2D. The driver's ``extract_cross_section_2d`` call is recorded and
       re-applied to IBU's unfolded vector at every K of the frozen scan.
  c1   every LightGBM the driver builds (both OmniFold steps, the miss regressor, and the Stay-Positive refinement
       classifier) gets ``s5c_unfold.config_params("deterministic", threads)`` merged in; every construction's
       parameters are recorded (C-SET).
  er   the driver unchanged, through the same runner: C-REF (c) and C-CV reproduce E_R's hXSec2D at RE-2's 1e-8 rule.

Units: er, c2_central, c2_replica:B, c1_central, c1_replica:B (B a bootstrap seed of the bound replica set; a replica
adds E_R's ``--bootstrap-seed B --bootstrap-streams three``). Each writes ``<unit>.root`` (the driver's own output)
and ``<unit>.npz`` (cross sections per K for c2, recorded parameters for c1) with a done-marker.

MEASURES: one driver run per unit. CANNOT AUTHORIZE: a reading (``ref_c2c1_read.py`` applies the declared ones), a
reported 2D estimator, or any claim.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.util
import json
import os
import sys
import time
from pathlib import Path
from unittest import mock

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
CONFIG = HERE / "config.json"
RE2 = REPO / "2d-unfolding" / "re2" / "re2_driver.py"
HELPER = REPO / "unbinned_unfolding" / "python"
ND = REPO / "nd-unfolding"
RC_GATE, RC_CONTROL = 4, 6


class GateFailure(RuntimeError):
    """A pinned digest or a precondition disagreed: the unit is not a result."""


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while block := fh.read(1 << 24):
            h.update(block)
    return h.hexdigest()


def sha256_noatime(path: Path) -> str:
    """sha256 read through O_NOATIME where the platform has it (Linux; the inputs' purge clocks are not touched)."""
    fd = os.open(str(path), os.O_RDONLY | getattr(os, "O_NOATIME", 0))
    h = hashlib.sha256()
    with os.fdopen(fd, "rb") as fh:
        while block := fh.read(1 << 24):
            h.update(block)
    return h.hexdigest()


def staging_root(cfg: dict) -> Path:
    root = (cfg["inputs"].get("staging") or {}).get("root")
    if not root:
        raise GateFailure("the staging root is bound at step two; config.json has none")
    return Path(root).resolve()


def staged(cfg: dict) -> dict:
    """The staged copies the units read: CV and MC under the staging root, never the originals (the director's
    ruling: the driver opens them with ROOT.TFile.Open, which cannot take O_NOATIME)."""
    root = staging_root(cfg)
    return {k: str(root / cfg["inputs"]["staging"][k]) for k in ("CV", "MC")}


def under(path, root: Path) -> bool:
    try:
        Path(path).resolve().relative_to(root)
        return True
    except (ValueError, TypeError):
        return False


def check_inputs(cfg: dict) -> dict:
    """C-IN at open time: the staged CV omnifile and flux file lie under the staging root and equal their pins before
    the driver opens them; returns what was verified, which every unit records."""
    verified = {}
    root = staging_root(cfg)
    for key, path in staged(cfg).items():
        if not under(path, root):
            raise GateFailure(f"input {key} {path} is not under the staging root {root}")
        got = sha256_noatime(Path(path))
        if got != cfg["inputs"][f"{key}_sha256"]:
            raise GateFailure(f"input {key} digest {got[:12]} differs from config.json")
        verified[key] = got
    return verified


def check_code(cfg: dict) -> None:
    for rel, digest in cfg["code_sha256"].items():
        if sha256(REPO / rel) != digest:
            raise GateFailure(f"{rel} digest differs from config.json")


def load_driver():
    """E_R's driver, imported from this checkout (it imports ROOT)."""
    spec = importlib.util.spec_from_file_location("re2_driver", RE2)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["re2_driver"] = mod
    spec.loader.exec_module(mod)
    if str(HELPER) not in sys.path:
        sys.path.insert(0, str(HELPER))
    import omnifold  # noqa: E402  (the module the driver's main imports its helper from)
    if Path(omnifold.__file__).resolve().parent != HELPER.resolve():
        raise GateFailure(f"omnifold resolved outside this checkout: {omnifold.__file__}")
    return mod, omnifold.OmniFold_helper_functions


# ------------------------------------------------------------------------------------------- binned IBU


def bin_index(x: np.ndarray, edges) -> np.ndarray:
    """TH1's bin of each value as 0..n-1, -1 outside: lower edge in, upper edge out (the last edge's overflow)."""
    e = np.asarray(edges, float)
    i = np.searchsorted(e, np.asarray(x, float), side="right") - 1
    return np.where((i >= 0) & (i < e.size - 1), i, -1)


def global_index(pt: np.ndarray, pz: np.ndarray, pt_edges, pz_edges) -> np.ndarray:
    """(pT bin) x n_pz + (p|| bin): the paper's GlobalID order (compare_to_paper_fullcov.flatten_ours)."""
    ip, iz = bin_index(pt, pt_edges), bin_index(pz, pz_edges)
    return np.where((ip >= 0) & (iz >= 0), ip * (len(pz_edges) - 1) + iz, -1)


def binned_problem(MCgen, MCreco, measured, pass_reco, pass_truth, w_truth, w_reco, w_meas, pt_edges, pz_edges):
    """T (truth, w_truth over truth-passing rows in the grid), M[reco, truth] (w_reco over rows passing both, both in
    the grid) and y (sum of the measured weights per reco bin)."""
    n = (len(pt_edges) - 1) * (len(pz_edges) - 1)
    pt_ok = np.asarray(pass_truth, bool)
    pr_ok = np.asarray(pass_reco, bool)
    t = global_index(MCgen[:, 0], MCgen[:, 1], pt_edges, pz_edges)
    r = global_index(MCreco[:, 0], MCreco[:, 1], pt_edges, pz_edges)
    keep_t = pt_ok & (t >= 0)
    T = np.bincount(t[keep_t], weights=np.asarray(w_truth, float)[keep_t], minlength=n)
    keep_m = pt_ok & pr_ok & (t >= 0) & (r >= 0)
    M = np.zeros((n, n))
    np.add.at(M, (r[keep_m], t[keep_m]), np.asarray(w_reco, float)[keep_m])
    rm = global_index(measured[:, 0], measured[:, 1], pt_edges, pz_edges)
    y = np.bincount(rm[rm >= 0], weights=np.asarray(w_meas, float)[rm >= 0], minlength=n)
    return T, M, y, t


def dagostini(M: np.ndarray, T: np.ndarray, y: np.ndarray, ks) -> dict:
    """D'Agostini's update with the MC truth as prior and no fakes, RooUnfoldBayes's algorithm without smoothing:
    u <- u * R^T (y / R u) / eff, R = M / T column by column, eff = column sums of R."""
    R = np.divide(M, T[None, :], out=np.zeros_like(M), where=T[None, :] > 0)
    eff = R.sum(axis=0)
    u = T.astype(float).copy()
    out = {}
    for k in range(1, max(ks) + 1):
        fold = R @ u
        ratio = np.divide(y, fold, out=np.zeros_like(y), where=fold > 0)
        u = np.divide(u * (R.T @ ratio), eff, out=np.zeros_like(u), where=eff > 0)
        if k in ks:
            out[k] = u.copy()
    return out


def roounfold_bayes(M: np.ndarray, T: np.ndarray, y: np.ndarray, ks, lib: str) -> dict:
    """RooUnfoldBayes on the same response, measured histogram and prior (flattened 1D bins)."""
    import ROOT
    if ROOT.gSystem.Load(lib) < 0:
        raise GateFailure(f"libRooUnfold did not load from {lib}")
    n = T.size
    hm, ht, hy = (ROOT.TH1D(name, "", n, 0, n) for name in ("ref_meas", "ref_truth", "ref_y"))
    hr = ROOT.TH2D("ref_resp", "", n, 0, n, n, 0, n)
    for i in range(n):
        hm.SetBinContent(i + 1, M[i].sum())
        ht.SetBinContent(i + 1, T[i])
        hy.SetBinContent(i + 1, y[i])
        for j in np.flatnonzero(M[i]):
            hr.SetBinContent(i + 1, int(j) + 1, M[i, j])
    resp = ROOT.RooUnfoldResponse(hm, ht, hr)
    out = {}
    for k in ks:
        u = ROOT.RooUnfoldBayes(resp, hy, int(k))
        h = u.Hunfold() if hasattr(u, "Hunfold") else u.Hreco()
        out[k] = np.array([h.GetBinContent(i + 1) for i in range(n)])
    return out


def event_factors(u: np.ndarray, T: np.ndarray, tin: np.ndarray) -> np.ndarray:
    """IBU's per-event step-2 factor: unfolded / prior in each truth-passing event's truth bin (1 outside the grid)."""
    factor = np.divide(u, T, out=np.ones_like(u), where=T > 0)
    return np.where(tin >= 0, factor[np.clip(tin, 0, None)], 1.0)


def filled(driver, tin: np.ndarray, w_in: np.ndarray, step2: np.ndarray, name: str):
    """The driver's hUnfold2D fill (ratio x w_truth per truth-passing event, re2_driver.py:2398-2400) as a TH2D."""
    import ROOT
    nx, ny = len(driver.PT_EDGES) - 1, len(driver.PZ_EDGES) - 1
    ok = tin >= 0
    v = np.bincount(tin[ok], weights=(step2 * w_in)[ok], minlength=nx * ny)
    h = ROOT.TH2D(name, "", nx, np.asarray(driver.PT_EDGES, float), ny, np.asarray(driver.PZ_EDGES, float))
    for g in range(nx * ny):
        h.SetBinContent(g // ny + 1, g % ny + 1, v[g])
    return h


def th2_vector(h, nx: int, ny: int) -> np.ndarray:
    return np.array([h.GetBinContent(ix, iy) for ix in range(1, nx + 1) for iy in range(1, ny + 1)])


# ------------------------------------------------------------------------------------------- the runner


class Capture(dict):
    """What one driver run hands the seams: the binned problem (c2), the extraction's arguments, the parameters of
    every LightGBM construction (c1)."""


def recording_lightgbm(capture: Capture, extra: dict | None):
    """Wrap lightgbm's estimators so every construction is recorded, with ``extra`` merged in (c1) or not."""
    import lightgbm

    def wrap(base, kind):
        class Recorded(base):
            def __init__(self, **params):
                params = {**params, **(extra or {})}
                capture.setdefault("lgbm", []).append({"kind": kind, "params": {k: params[k] for k in sorted(params)}})
                super().__init__(**params)
        Recorded.__name__ = base.__name__
        return Recorded

    return [mock.patch.object(lightgbm, "LGBMClassifier", wrap(lightgbm.LGBMClassifier, "classifier")),
            mock.patch.object(lightgbm, "LGBMRegressor", wrap(lightgbm.LGBMRegressor, "regressor"))]


def run_driver(driver, ohf, argv: list[str], out_root: Path, *, ibu: dict | None = None,
               extra: dict | None = None, staging: Path | None = None) -> Capture:
    """One in-process run of E_R's driver main() with its argv and output. ``ibu`` (c2) replaces the OmniFold call;
    ``extra`` (c1) merges keys into every LightGBM; neither (er) leaves the driver as it is."""
    capture = Capture()
    real_extract = driver.extract_cross_section_2d

    def extract(hUnfold, *a, **k):
        capture.setdefault("extract", (a, k))  # the first call is hXSec2D's (re2_driver.py:2479)
        return real_extract(hUnfold, *a, **k)

    real_completeness = driver.compute_omnifold_completeness_2d

    def completeness(*a, **k):
        out = real_completeness(*a, **k)
        capture.setdefault("completeness", out)  # (hCompleteness, hOFInputTruth, hOFTruthDenom)
        return out

    patches = [mock.patch.object(driver, "extract_cross_section_2d", extract),
               mock.patch.object(driver, "compute_omnifold_completeness_2d", completeness)]
    if ibu is not None:
        def omnifold(MCgen, MCreco, measured, MC_pass_reco_mask, MC_pass_truth_mask, measured_pass_reco_mask,
                     num_iterations, MCgen_weights=None, MCreco_weights=None, measured_weights=None, **_):
            T, M, y, t = binned_problem(np.asarray(MCgen), np.asarray(MCreco), np.asarray(measured),
                                        MC_pass_reco_mask, MC_pass_truth_mask, MCgen_weights, MCreco_weights,
                                        measured_weights, driver.PT_EDGES, driver.PZ_EDGES)
            traj = ibu["unfolder"](M, T, y, ibu["ks"])
            pt_mask = np.asarray(MC_pass_truth_mask, bool)
            tin = t[pt_mask]
            capture.update(T=T, M=M, y=y, traj=traj, tin=tin, w_in=np.asarray(MCgen_weights, float)[pt_mask],
                           measured_weights=np.asarray(measured_weights, float).copy())
            step2 = event_factors(traj[ibu["primary"]], T, tin)
            return np.ones(int(np.asarray(MC_pass_reco_mask, bool).sum())), step2
        patches.append(mock.patch.object(ohf, "omnifold", staticmethod(omnifold)))
    else:
        real_omnifold = ohf.omnifold

        def observed(MCgen, MCreco, measured, MC_pass_reco_mask, MC_pass_truth_mask, *a, **k):
            """er and c1: the driver's own OmniFold call, unchanged; its refined measured weights are binned on the
            way in, so C-REF (d) can compare c2's measured histogram with E_R's bin by bin."""
            _, _, y, _ = binned_problem(np.asarray(MCgen), np.asarray(MCreco), np.asarray(measured), MC_pass_reco_mask,
                                        MC_pass_truth_mask, k.get("MCgen_weights"), k.get("MCreco_weights"),
                                        k.get("measured_weights"), driver.PT_EDGES, driver.PZ_EDGES)
            capture["y"] = y
            return real_omnifold(MCgen, MCreco, measured, MC_pass_reco_mask, MC_pass_truth_mask, *a, **k)
        patches.append(mock.patch.object(ohf, "omnifold", staticmethod(observed)))
    patches += recording_lightgbm(capture, extra)
    if staging is not None:
        import ROOT
        real_open = ROOT.TFile.Open

        def guarded(path, mode="READ", *a, **k):
            """Every file the driver opens for reading must be a staged copy under the root (the director's ruling)."""
            if str(mode).upper() in ("", "READ") and not under(path, staging):
                raise GateFailure(f"the driver opened {path} for reading outside the staging root {staging}")
            return real_open(path, mode, *a, **k)
        patches.append(mock.patch.object(ROOT.TFile, "Open", staticmethod(guarded)))
    saved = sys.argv
    with contextlib.ExitStack() as stack:
        for p in patches:
            stack.enter_context(p)
        sys.argv = ["re2_driver.py", *argv, "--out", str(out_root)]
        try:
            driver.main()
        finally:
            sys.argv = saved
    capture["real_extract"] = real_extract
    return capture


def xsec_at_every_k(driver, capture: Capture, ks) -> dict:
    """The driver's own extraction, re-applied to IBU's unfolded vector at every K (recorded arguments)."""
    import ROOT
    a, k = capture["extract"]
    nx, ny = len(driver.PT_EDGES) - 1, len(driver.PZ_EDGES) - 1
    out = {}
    for K in ks:
        h = ROOT.TH2D(f"ref_unfold_K{K}", "", nx, np.asarray(driver.PT_EDGES, float), ny,
                      np.asarray(driver.PZ_EDGES, float))
        u = capture["traj"][K]
        for ix in range(nx):
            for iy in range(ny):
                h.SetBinContent(ix + 1, iy + 1, u[ix * ny + iy])
        out[K] = th2_vector(capture["real_extract"](h, *a, **k), nx, ny)
    return out


def c_sim(driver, capture: Capture, unfolder, ks, rtol: float) -> dict:
    """C-SIM through the full chain (the declaration's "through the full chain"; the audit's K1): IBU on the MC's own
    reco expectation (M summed over truth), the seam's per-event factors (``event_factors``), the driver's fill and
    the driver's recorded extraction (completeness, flux, target, POT, area), against the MC's FULL-truth cross
    section, the driver's own truth denominator (hOFTruthDenom2D) through the same normalisation with unit
    completeness. With prior = truth and measured = R T exactly, IBU's efficiency and the extraction's completeness
    must return the full truth at every K, to ``rtol``, on every cell the extraction covers (completeness > 0). A
    double efficiency correction or a mis-indexed factor moves it."""
    T, M, tin, w_in = capture["T"], capture["M"], capture["tin"], capture["w_in"]
    a, k = capture["extract"]
    h_comp, _, h_den = capture["completeness"]
    nx, ny = len(driver.PT_EDGES) - 1, len(driver.PZ_EDGES) - 1
    unit = h_comp.Clone("ref_csim_unit")
    for ix in range(1, nx + 1):
        for iy in range(1, ny + 1):
            unit.SetBinContent(ix, iy, 1.0)
    ref = th2_vector(capture["real_extract"](h_den, unit, *a[1:], **k), nx, ny)
    covered = th2_vector(h_comp, nx, ny) > 0
    traj = unfolder(M, T, M.sum(axis=1), ks)
    worst = 0.0
    for K in ks:
        h = filled(driver, tin, w_in, event_factors(traj[K], T, tin), f"ref_csim_K{K}")
        x = th2_vector(capture["real_extract"](h, *a, **k), nx, ny)
        nz = covered & (ref != 0)
        if np.any(x[covered & (ref == 0)] != 0):
            return {"max_rel": float("inf"), "pass": False}
        worst = max(worst, float(np.max(np.abs(x[nz] / ref[nz] - 1))) if nz.any() else 0.0)
    return {"max_rel": worst, "cells_covered": int(covered.sum()), "pass": bool(worst <= rtol and covered.any())}


# ------------------------------------------------------------------------------------------- units


def cpu_count() -> int:
    """The CPUs this process may use (its affinity on Linux), which sets LightGBM's pool and the refit's noise."""
    try:
        return len(os.sched_getaffinity(0))
    except AttributeError:  # pragma: no cover - macOS has no affinity call
        return os.cpu_count() or 0


def resolve_argv(cfg: dict, b: int | None) -> list[str]:
    e = cfg["e_r"]
    subs = {"$CV": staged(cfg)["CV"], "$MC": staged(cfg)["MC"]}
    argv = [subs.get(x, x) for x in e["argv"]]
    if b is not None:
        argv += [x.format(b=b) for x in e["replica_argv_extra"]]
    return argv


def replica_set(cfg: dict) -> tuple[int, int]:
    rs = cfg["replica_set"]
    if rs["choice"] not in rs["options"]:
        raise GateFailure("the replica set is bound at step two from C-DRAW's verdict; config.json has none")
    o = rs["options"][rs["choice"]]
    return o["first"], o["last"]


def parse_units(cfg: dict, specs: list[str]) -> list[tuple]:
    out = []
    for s in specs:
        kind, _, rest = s.partition(":")
        if kind in ("er", "c2_central", "c1_central") and not rest:
            out.append((kind, None))
        elif kind == "c2_replica" and rest.isdigit():
            first, last = replica_set(cfg)
            if not first <= int(rest) <= last:
                raise ValueError(f"c2 replica {rest} outside the bound set {first}-{last}")
            out.append((kind, int(rest)))
        elif kind == "c1_replica" and rest.isdigit():
            r = cfg["c1"]["replicas"]
            if not r["first"] <= int(rest) <= r["last"]:
                raise ValueError(f"c1 replica {rest} outside {r['first']}-{r['last']}")
            out.append((kind, int(rest)))
        else:
            raise ValueError(f"unknown unit {s!r}")
    return out


def unit_name(u: tuple) -> str:
    return u[0] if u[1] is None else f"{u[0]}_b{u[1]}"


def deterministic_keys(cfg: dict) -> dict:
    if str(ND) not in sys.path:
        sys.path.insert(0, str(ND))
    import s5c_unfold
    extra = s5c_unfold.config_params("deterministic", int(cfg["c1"]["threads"]))
    if sorted(extra) != sorted(cfg["c1"]["deterministic_keys"]):
        raise GateFailure(f"s5c_unfold's deterministic keys {sorted(extra)} are not the declared four")
    return extra


def run_unit(driver, ohf, cfg: dict, u: tuple, out: Path, unfolder=None, inputs_verified: dict | None = None) -> int:
    """One unit; its done-marker carries its control verdict, and only a PASS unit is skipped on a rerun."""
    name = unit_name(u)
    root, npz, marker = out / f"{name}.root", out / f"{name}.npz", out / f"{name}.done"
    if npz.exists() or root.exists():
        verdict = json.loads(marker.read_text()).get("verdict") if marker.exists() else None
        if verdict == "PASS":
            return 0
        print(f"refusing: {name} exists without a PASS done-marker (verdict {verdict})", file=sys.stderr)
        return RC_CONTROL
    cpus = cpu_count()
    if cpus != int(cfg["e_r"]["cpus"]):  # like for like with E_R: the refit's noise depends on the CPU count
        print(f"refusing: {name} needs E_R's {cfg['e_r']['cpus']} CPUs, this process has {cpus}", file=sys.stderr)
        return RC_GATE
    threads = {k: os.environ.get(k) for k in cfg["e_r"]["thread_env"]}
    if threads != cfg["e_r"]["thread_env"]:  # and its thread environment: LightGBM's pool follows OMP_NUM_THREADS
        print(f"refusing: {name} needs E_R's thread environment {cfg['e_r']['thread_env']}, not {threads}",
              file=sys.stderr)
        return RC_GATE
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    argv = resolve_argv(cfg, u[1])
    meta = {"schema": "ref-c2c1-unit/1", "unit": name, "argv": argv, "bootstrap_seed": u[1],
            "runner_sha256": sha256(Path(__file__).resolve()), "config_sha256": sha256(CONFIG),
            "code_sha256": cfg["code_sha256"], "slurm_job": os.environ.get("SLURM_JOB_ID"),
            "inputs_sha256": inputs_verified, "cpus": cpus, "thread_env": threads}
    controls = {}
    if u[0].startswith("c2"):
        c2 = cfg["c2"]
        ks = list(c2["iterations"]["scan"])
        lib = cfg["inputs"]["roounfold_lib"]
        prod = unfolder or (lambda M, T, y, k: roounfold_bayes(M, T, y, k, lib))
        cap = run_driver(driver, ohf, argv, root, ibu={"unfolder": prod, "ks": ks, "primary": c2["iterations"]["primary"]},
                         staging=staging_root(cfg))
        xs = xsec_at_every_k(driver, cap, ks)
        arrays = {"ks": np.array(ks), "xsec": np.array([xs[K] for K in ks]), "unfolded": np.array([cap["traj"][K] for K in ks]),
                  "T": cap["T"], "y": cap["y"]}
        # C-FILL: the driver's own per-event fill and extraction (hXSec2D, written at the primary K) against the recorded
        # extraction of IBU's unfolded vector, on the data, where the factors are not 1; a mis-indexed or mis-scaled
        # factor moves cells by O(1). (C-SIM's fixed point has every factor exactly 1, so it cannot.) 1e-9, not tighter:
        # the driver sums w f event by event and u = f sum w, so their rounding grows with a truth bin's event count.
        import ROOT
        f = ROOT.TFile.Open(str(root))
        nx, ny = len(driver.PT_EDGES) - 1, len(driver.PZ_EDGES) - 1
        own = th2_vector(f.Get("hXSec2D"), nx, ny)
        f.Close()
        prim = xs[c2["iterations"]["primary"]]
        nz = prim != 0
        fill_rel = float(np.max(np.abs(own[nz] / prim[nz] - 1))) if nz.any() else 0.0
        controls["C-FILL"] = {"max_rel": fill_rel,
                              "pass": bool(fill_rel <= c2["c_fill_rtol"] and np.all(own[~nz] == 0))}
        meta["measured_weights_sha256"] = hashlib.sha256(cap["measured_weights"].tobytes()).hexdigest()
        meta["measured_weights_sum"] = float(cap["measured_weights"].sum())
        if u[0] == "c2_central":
            controls["C-SIM"] = c_sim(driver, cap, dagostini, ks, c2["c_sim_rtol"])
            if unfolder is None:  # C-ROO: RooUnfoldBayes against the same update in numpy, on the data
                ref = dagostini(cap["M"], cap["T"], cap["y"], ks)
                worst = max(float(np.max(np.abs(cap["traj"][K] - ref[K]) / np.maximum(np.abs(ref[K]), 1e-300)))
                            for K in ks)
                controls["C-ROO"] = {"max_rel": worst, "pass": bool(worst <= c2["c_roo_rtol"])}
    else:
        extra = deterministic_keys(cfg) if u[0].startswith("c1") else None
        cap = run_driver(driver, ohf, argv, root, extra=extra, staging=staging_root(cfg))
        arrays = {"lgbm_params": np.array(json.dumps(cap.get("lgbm", []))), "y": cap["y"]}
        meta["extra_keys"] = extra
    meta["controls"] = controls
    meta["seconds"] = round(time.time() - t0, 3)
    passed = all(c["pass"] for c in controls.values())
    np.savez_compressed(npz, **arrays, meta=json.dumps(meta, default=str))
    marker.write_text(json.dumps({"unit": name, "verdict": "PASS" if passed else "FAIL", "sha256": sha256(npz),
                                  "root_sha256": sha256(root)}) + "\n")
    print(json.dumps({"unit": name, "seconds": meta["seconds"], "controls": {k: v["pass"] for k, v in controls.items()}}),
          flush=True)
    return 0 if passed else RC_CONTROL


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--unit", action="append", required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    cfg = json.loads(CONFIG.read_text())
    try:
        units = parse_units(cfg, a.unit)
    except (ValueError, GateFailure) as e:
        print(f"refusing: {e}", file=sys.stderr)
        return 2
    try:
        check_code(cfg)
        verified = check_inputs(cfg)
        driver, ohf = load_driver()
    except (GateFailure, OSError) as e:
        print(f"refusing: {e}", file=sys.stderr)
        return RC_GATE
    rc = 0
    for u in units:
        rc = rc or run_unit(driver, ohf, cfg, u, a.out, inputs_verified=verified)
    return rc


if __name__ == "__main__":
    sys.exit(main())
