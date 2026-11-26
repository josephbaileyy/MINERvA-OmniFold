#!/usr/bin/env python3
"""EVW2D: the per-event unfolded weights of E_R, the 2D production unfold, written beside its histograms.

Declaration: ``docs/orchestration/state/2d-closeout/evw2d-20261124/EVW2D-DECLARATION.md``. Every number comes from
``config.json`` beside this file or from the constants below; the two reference vectors from ``references.npz``
(``make_references.py``).

E_R's driver runs unchanged, in-process, through REF-C2C1's runner (``ref_c2c1.run_driver``), both imported from a
clean checkout at the pinned commit (``config.json`` ``driver_tree``: its HEAD, its cleanliness and four file digests
are checked before the import, and the digests again after the run). Three pass-through recorders sit on the driver's
seams: the OmniFold call (``OmniFold_helper_functions.omnifold``), the truth-denominator loader
(``collect_truth_denom_arrays``) and the POT read (``get_pot_scales``). Each forwards its arguments unchanged, returns
the identical object the real call returned, and records it with a digest of its content (arrays by bytes; ROOT objects
by type only). C-REC re-takes the digests at the end.

What is written, for every truth-passing ``mc_signal_reco`` row (the rows whose step-2 weights fill ``hUnfold2D``):

  entry       the row's ROOT entry number in ``mc_signal_reco`` of the pinned omnifile (uint32); with the omnifile's
              sha256 it is the event key. The omnifile carries no run/subrun/gate identity (stage D §4.3).
  truth_pt    truth pT, GeV/c (float64, the driver's array)
  truth_pz    truth p||, GeV/c (float64)
  w_prior     the driver's MC truth weight w_truth, POT-scaled (float64)
  w_unfolded  float(step-2 ratio) x float(w_truth), the driver's ``hUnfold2D`` fill weight (float64)

with the constants that turn weighted counts into d2sigma/dpT dp|| (the driver's own extraction arguments, captured):
d2sigma = sum(w_unfolded) / (c Phi_i N POT dpT dp||) x 1e4, c the completeness (1 on every cell with positive
denominator content when C-COMPLETE and C-CMAP hold; otherwise the file carries the denominator table and c is
event-level).

Controls (the declaration's §4): C-BIND and the interpreter, checkout and allocation checks (refusals before anything
is created), C-PINS, C-KEY, C-REC, C-FLUX, C-COMPLETE, C-CMAP, C-CMAP-EVENT (fallback), C-FILE, C-FLOW, C-STAGE and
three exactness tests on the file read back from disk with its saved constants: C-SELF (this run's own hXSec2D),
C-EXACT-ER (E_R's committed hXSec2D, our edges) and C-EXACT-PAPER (Tier 1's hXSec2D on the paper's pT edges), each
<= 1e-8 relative. ``evw2d.done`` is published last and atomically; a product without a PASS one is not a result.

    python3 -B evw2d.py --config-sha256 SHA stage            # O_NOATIME copies of the two inputs, then a read-only root
    python3 -B evw2d.py --config-sha256 SHA run --out DIR    # inside a one-node srun step; DIR new, under the lane root
    python3 -B evw2d.py --config-sha256 SHA cleanup --out DIR  # after a PASS: delete the staged copies, with a ledger

MEASURES: one driver run and its weights. CANNOT AUTHORIZE: a reading, a claim, or publication.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import resource
import secrets
import socket
import stat
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
CONFIG = HERE / "config.json"
RC_GATE, RC_CONTROL = 4, 6
SCHEMA = "evw2d-weights/1"
TREE = "mc_signal_reco"
SIGNAL_BRANCHES = ("MC", "MC_pz", "sim", "sim_pz", "sim_pass", "w_truth", "w_reco")
WEIGHT_COLUMNS = ("entry", "truth_pt", "truth_pz", "w_prior", "w_unfolded")
DENOM_COLUMNS = ("truth_pt", "truth_pz", "w_truth")
SEAMS = ("omnifold", "collect_truth_denom_arrays", "get_pot_scales")
DENOM_META = {"schema": SCHEMA, "table": "mc_truth_denom rows kept by the driver"}
PRODUCTS = ("weights.npz", "constants.json", "xsec.root", "run.json")
FALLBACK_PRODUCT = "denominator.npz"
CM2_PER_M2 = 1.0e4
FLOW_RTOL = 1e-12
CMAP_ATOL = 1e-12
CMAP_ROUNDING = 1e-9  # a miss above CMAP_ATOL and at most this, with every zero cell zero, is summation rounding
# the reviewed values: config.json must carry exactly these (the binding cannot loosen them through the config)
ER_ARGV = ["--omnifile", "$CV", "--mcfile", "$MC", "--iters", "5", "--use-weights", "--estimator", "lgbm",
           "--seed", "42", "--branch-select", "all", "--bkg-mode", "negweight-refined",
           "--refine-n-estimators", "400", "--refine-num-leaves", "31"]
EXACT_RTOL = 1e-8
ER_CPUS = 64
ER_THREAD_ENV = {"OMP_NUM_THREADS": "64", "MKL_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1"}
INPUT_SHA256 = {"CV": "43f8cc16ab2688200d3e2e0ebb48012b23ada6d7882b8c68ecfc51c609aeb8df",
                "MC": "d40aea69235cdc98644e1bb3e622e579d6b81904c004c83fe50465079989f316"}
REFERENCES_SHA256 = "1b21458283c06531c9791efdc1e15f9d685d0733e398288a715768d61b612a03"
PAPER_PT_EDGES = [0, 0.075, 0.15, 0.25, 0.325, 0.40, 0.475, 0.55, 0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50]
SCRATCH_PREFIX = "/pscratch/sd/j/josephrb"
SLURM_NODES = 1
SLURM_RESERVED_STEPS = 0xFFFFFFF0  # Slurm's special step ids (batch, extern, interactive, pending) lie at and above
COMPUTE_HOST_PREFIX = "nid"
REQUIRED_PINS = ("2d-unfolding/re2/re2_driver.py", "unbinned_unfolding/python/omnifold.py",
                 "2d-unfolding/ref_c2c1/ref_c2c1.py", "2d-unfolding/ref_c2c1/config.json")
PRELOAD_FORBIDDEN = ("re2_driver", "ref_c2c1", "omnifold")
PROTECTED = (Path("/pscratch"), Path("/global/cfs"))
PYCACHE_DIRS = ("2d-unfolding/re2", "2d-unfolding/ref_c2c1", "unbinned_unfolding/python")


class GateFailure(RuntimeError):
    """A pinned digest, a binding, a precondition or a recorder disagreed: the run is not a result."""


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while block := fh.read(1 << 24):
            h.update(block)
    return h.hexdigest()


def digest(obj) -> str:
    """sha256 over an object's content: arrays by dtype, shape and bytes; floats by their hex; containers in order;
    any other object (a ROOT file or tree) by its type only."""
    h = hashlib.sha256()

    def feed(o):
        if isinstance(o, np.ndarray):
            a = np.ascontiguousarray(o)
            h.update(f"nd{a.dtype.str}{a.shape}".encode())
            h.update(a.tobytes())
        elif isinstance(o, (tuple, list)):
            h.update(f"seq{type(o).__name__}{len(o)}".encode())
            for x in o:
                feed(x)
        elif isinstance(o, dict):
            h.update(f"map{len(o)}".encode())
            for k in sorted(o, key=str):
                feed(str(k))
                feed(o[k])
        elif isinstance(o, float):
            h.update(b"f" + o.hex().encode())
        elif isinstance(o, (bool, int, str, type(None), np.generic)):
            h.update(f"{type(o).__name__}:{o!r}".encode())
        else:
            h.update(f"obj:{type(o).__name__}".encode())
    feed(obj)
    return h.hexdigest()


def under(path, root) -> bool:
    try:
        Path(path).resolve().relative_to(Path(root).resolve())
        return True
    except (ValueError, TypeError):
        return False


# ------------------------------------------------------------------------------------------- the binding (C-BIND)


def load_config() -> tuple[dict, str]:
    """config.json parsed from the very bytes whose digest is returned, so C-BIND judges the config that runs."""
    raw = CONFIG.read_bytes()
    return json.loads(raw), hashlib.sha256(raw).hexdigest()


def check_binding(cfg: dict, parsed_sha256: str, config_sha256: str, out: Path | None = None) -> None:
    """Refuses before anything is created unless the binding is complete and every path lies where it allows.
    - the digest of the bytes ``cfg`` was parsed from (``load_config``) equals the one given on the command line (the
      binding records it), and it carries the reviewed values: E_R's argv, CPUs and thread environment, the
      tolerance, the input and reference digests, the paper's pT edges and exactly the four required pins;
    - the declaration's digest equals the bound one;
    - the lane root lies strictly under SCRATCH_PREFIX; the driver tree, the staging root, this checkout (deploy_C)
      and the output lie strictly inside it;
    - the staged names are plain file names; the output is new and not the lane root."""
    if parsed_sha256 != config_sha256:
        raise GateFailure(f"config.json has sha256 {str(parsed_sha256)[:12]}, not the bound "
                          f"{str(config_sha256)[:12]}")
    reviewed = {"argv": (cfg.get("argv"), ER_ARGV), "exact_rtol": (cfg.get("exact_rtol"), EXACT_RTOL),
                "cpus": (cfg.get("cpus"), ER_CPUS), "thread_env": (cfg.get("thread_env"), ER_THREAD_ENV),
                "inputs": ({k: cfg["inputs"].get(f"{k}_sha256") for k in INPUT_SHA256}, INPUT_SHA256),
                "references": (cfg.get("references", {}).get("sha256"), REFERENCES_SHA256),
                "paper_pt_edges": (cfg.get("paper_pt_edges"), PAPER_PT_EDGES)}
    for name, (got_v, want_v) in reviewed.items():
        if got_v != want_v:
            raise GateFailure(f"config.json's {name} is not the reviewed value")
    if sorted(cfg["driver_tree"]["code_sha256"]) != sorted(REQUIRED_PINS):
        raise GateFailure("config.json does not pin exactly the four required files")
    dec = cfg.get("declaration_sha256")
    if not dec:
        raise GateFailure("declaration_sha256 is bound at the binding; config.json has none")
    got = sha256(REPO / cfg["declaration"])
    if got != dec:
        raise GateFailure(f"the declaration has sha256 {got[:12]}, not the bound {dec[:12]}")
    lane = cfg.get("lane_root")
    if not lane:
        raise GateFailure("the lane root is bound at the binding; config.json has none")
    if not under(lane, SCRATCH_PREFIX) or Path(lane).resolve() == Path(SCRATCH_PREFIX).resolve():
        raise GateFailure(f"the lane root {lane} is not strictly under {SCRATCH_PREFIX}")
    for what, p in (("the driver tree", driver_tree(cfg)), ("the staging root", staging_root(cfg)),
                    ("this checkout", REPO)):
        if not under(p, lane) or Path(p).resolve() == Path(lane).resolve():
            raise GateFailure(f"{what} {p} is not inside the lane root {lane}")
    for key in ("CV", "MC"):
        name = cfg["inputs"]["staging"][key]
        if not name or Path(name).name != name or name in (".", ".."):
            raise GateFailure(f"the staged {key} name {name!r} is not a plain file name")
    if out is not None:
        if not under(out, lane) or Path(out).resolve() == Path(lane).resolve():
            raise GateFailure(f"--out {out} is not inside the lane root {lane}")


def check_interpreter() -> None:
    """No bytecode is written or read from a redirected cache, and no module of the driver tree is already loaded."""
    if not sys.dont_write_bytecode:
        raise GateFailure("run with python -B: no bytecode cache may be written beside the pinned sources")
    if getattr(sys, "pycache_prefix", None):
        raise GateFailure(f"PYTHONPYCACHEPREFIX/-X pycache_prefix is set ({sys.pycache_prefix}): a cache could "
                          "supply code under -B")
    loaded = [m for m in PRELOAD_FORBIDDEN if m in sys.modules]
    if loaded:
        raise GateFailure(f"modules {loaded} are loaded before the driver tree's: they would shadow its files")


def git_env() -> dict:
    """git's environment: no inherited GIT_* variable (GIT_DIR or GIT_WORK_TREE would point the checks at another
    checkout) and no optional locks."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env["GIT_OPTIONAL_LOCKS"] = "0"
    return env


def check_checkout(cfg: dict) -> str:
    """The driver tree is the top level of a git checkout at the pinned commit with nothing beyond its committed
    content, judged with no inherited git variable."""
    tree = driver_tree(cfg)
    env = git_env()
    top = subprocess.run(["git", "-C", str(tree), "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                         env=env)
    if top.returncode != 0 or Path(top.stdout.strip()).resolve() != tree:
        raise GateFailure(f"the driver tree {tree} is not the top level of its own checkout "
                          f"({top.stdout.strip() or top.stderr.strip()})")
    head = subprocess.run(["git", "-C", str(tree), "rev-parse", "HEAD"], capture_output=True, text=True, env=env)
    if head.returncode != 0 or head.stdout.strip() != cfg["driver_tree"]["commit"]:
        raise GateFailure(f"the driver tree's HEAD {head.stdout.strip() or head.stderr.strip()} is not the pinned "
                          f"commit {cfg['driver_tree']['commit']}")
    st = subprocess.run(["git", "-C", str(tree), "status", "--porcelain", "--ignored"], capture_output=True,
                        text=True, env=env)
    if st.returncode != 0 or st.stdout.strip():
        raise GateFailure(f"the driver tree is not clean: {st.stdout.strip()[:200] or st.stderr.strip()}")
    return head.stdout.strip()


def check_allocation() -> dict:
    """Inside a numbered srun step (not the batch, extern or another reserved step) of a one-node Slurm job on a
    compute node. The job's time limit (the launcher's ``#SBATCH -t``, fixed by the binding) is the time cap; the
    wrapper does not query the scheduler for it."""
    job, step = os.environ.get("SLURM_JOB_ID") or "", os.environ.get("SLURM_STEP_ID") or ""
    nodes, host = os.environ.get("SLURM_JOB_NUM_NODES"), socket.gethostname()
    if (not job.isdigit() or not step.isdigit() or int(step) >= SLURM_RESERVED_STEPS
            or nodes != str(SLURM_NODES) or not host.startswith(COMPUTE_HOST_PREFIX)):
        raise GateFailure(f"the run needs an srun step of a {SLURM_NODES}-node job on a compute node, not "
                          f"job={job} step={step} nodes={nodes} host={host}")
    return {"job": job, "step": step, "nodes": nodes, "host": host}


# ------------------------------------------------------------------------------------------- the pinned tree (C-PINS)


def driver_tree(cfg: dict) -> Path:
    root = cfg["driver_tree"].get("root")
    if not root:
        raise GateFailure("the driver tree is bound at the binding; config.json has none")
    return Path(root).resolve()


def check_tree(cfg: dict) -> dict:
    """The four required files of the driver tree are plain files inside it (no link on the way) and equal their
    digests (re2_driver.py, the OmniFold helper, ref_c2c1.py and its config.json: zero changed bytes), and no bytecode
    cache sits beside them."""
    root = driver_tree(cfg)
    pins = cfg["driver_tree"]["code_sha256"]
    if sorted(pins) != sorted(REQUIRED_PINS):
        raise GateFailure("config.json does not pin exactly the four required files")
    for rel in PYCACHE_DIRS:
        if (root / rel / "__pycache__").exists():
            raise GateFailure(f"{rel}/__pycache__ exists in the driver tree: a cache could diverge from the source")
    got = {}
    for rel in REQUIRED_PINS:
        if (root / rel).resolve() != root / rel or not (root / rel).is_file():
            raise GateFailure(f"{rel} in the driver tree is not a plain file inside it (a link, or missing)")
        d = sha256(root / rel)
        if d != pins[rel]:
            raise GateFailure(f"{rel} in the driver tree has sha256 {d[:12]}, not {pins[rel][:12]}")
        got[rel] = d
    return got


def load_runner(cfg: dict):
    """REF-C2C1's module from the driver tree (its guards, staging checks and runner), and through it E_R's driver and
    OmniFold helper from the same tree; each loaded module's file is checked to be the pinned one."""
    root = driver_tree(cfg)
    path = root / "2d-unfolding" / "ref_c2c1" / "ref_c2c1.py"
    spec = importlib.util.spec_from_file_location("ref_c2c1", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["ref_c2c1"] = mod
    spec.loader.exec_module(mod)
    driver, ohf = mod.load_driver()
    loaded = {"2d-unfolding/ref_c2c1/ref_c2c1.py": mod.__file__, "2d-unfolding/re2/re2_driver.py": driver.__file__,
              "unbinned_unfolding/python/omnifold.py": sys.modules["omnifold"].__file__}
    for rel, f in loaded.items():
        if Path(f).resolve() != (root / rel).resolve():
            raise GateFailure(f"{rel} was loaded from {f}, not the driver tree")
    return mod, driver, ohf


# ------------------------------------------------------------------------------------------- recorders (C-REC)


class Recorder:
    """Pass-through recorders. Each wrapped call runs the real function with the very arguments it received and returns
    its result object itself; the recorder keeps references to both and the digests of the arguments before and after
    the call and of the result. ``verify`` re-takes the digests at the end of the run. Each seam is called once on the
    central path; a second call refuses before it runs."""

    def __init__(self):
        self.calls: dict[str, dict] = {}

    def wrap(self, name: str, real):
        def recorded(*a, **k):
            if name in self.calls:
                raise GateFailure(f"{name} was called twice; the central run calls it once")
            before = digest((a, k))
            out = real(*a, **k)
            self.calls[name] = {"args": a, "kwargs": k, "out": out, "args_before": before,
                                "args_after": digest((a, k)), "out_digest": digest(out)}
            return out
        recorded.__wrapped__ = real
        return recorded

    def require(self, names) -> None:
        missing = [n for n in names if n not in self.calls]
        if missing:
            raise GateFailure(f"the driver never reached the seams {missing}")

    def verify(self, names) -> dict:
        rows, ok = {}, True
        for n in names:
            c = self.calls.get(n)
            if c is None:
                rows[n] = {"called": False, "pass": False}
                ok = False
                continue
            now_args, now_out = digest((c["args"], c["kwargs"])), digest(c["out"])
            args_ok = c["args_before"] == c["args_after"] == now_args
            good = args_ok and now_out == c["out_digest"]
            rows[n] = {"called": True, "args_unchanged": args_ok, "out_unchanged": now_out == c["out_digest"],
                       "out_digest": c["out_digest"], "pass": good}
            ok = ok and good
        return {"calls": rows, "pass": ok}


def xsec_capture(driver, store: dict):
    """The driver's own hXSec2D, kept in memory as it is made: the global bins of the first extraction's result (the
    first call is hXSec2D's, re2_driver.py:2479; ref_c2c1 reads the same call). Passes the result through unchanged."""
    real = driver.extract_cross_section_2d

    def extract(hUnfold, hCompleteness, flux_bins, data_pot, n_nucleons, pt_edges, pz_edges, *a, **k):
        out = real(hUnfold, hCompleteness, flux_bins, data_pot, n_nucleons, pt_edges, pz_edges, *a, **k)
        if "hXSec2D" not in store:
            store["hXSec2D"] = th2_global(out, len(pt_edges) - 1, len(pz_edges) - 1)
        return out
    return mock.patch.object(driver, "extract_cross_section_2d", extract)


def recorder_patches(rec: Recorder, driver, ohf) -> list:
    return [mock.patch.object(ohf, "omnifold", staticmethod(rec.wrap("omnifold", ohf.omnifold))),
            mock.patch.object(driver, "collect_truth_denom_arrays",
                              rec.wrap("collect_truth_denom_arrays", driver.collect_truth_denom_arrays)),
            mock.patch.object(driver, "get_pot_scales", rec.wrap("get_pot_scales", driver.get_pot_scales))]


# ------------------------------------------------------------------------------------------- C-KEY


def read_signal_tree(path: Path) -> dict:
    """Every entry of mc_signal_reco's seven loader branches and its entry number, in entry order (ROOT RDataFrame,
    single-threaded). The loader's branch types are required: Double_t for the six numbers, UChar_t for sim_pass (the
    loader's ``array("B")`` buffer)."""
    import ROOT
    if ROOT.ROOT.IsImplicitMTEnabled():
        raise GateFailure("ROOT implicit multithreading is on: AsNumpy would not keep entry order")
    df = ROOT.RDataFrame(TREE, str(path))
    types = {k: str(df.GetColumnType(k)) for k in SIGNAL_BRANCHES}
    want = {k: ("UChar_t" if k == "sim_pass" else "Double_t") for k in SIGNAL_BRANCHES}
    if types != want:
        raise GateFailure(f"mc_signal_reco's branch types {types} are not the loader's {want}")
    cols = df.Define("evw2d_entry", "rdfentry_").AsNumpy([*SIGNAL_BRANCHES, "evw2d_entry"])
    out = {k: np.asarray(cols[k]) for k in SIGNAL_BRANCHES}
    out["entry"] = np.asarray(cols["evw2d_entry"]).astype(np.int64)
    n = {v.shape[0] for v in out.values()}
    if len(n) != 1:
        raise GateFailure(f"mc_signal_reco's columns have different lengths {sorted(n)}")
    if not np.array_equal(out["entry"], np.arange(out["entry"].size)):
        raise GateFailure("RDataFrame's entry numbers are not 0..n-1 in order")
    return out


def keep_rule(cols: dict, driver, pot_scale: float, bounds: tuple) -> dict:
    """The driver's ``collect_signal_arrays_2d`` keep rule and stored values (CV weights, ``use_weights``), applied to
    the independently read columns: weights finite and in [0, 1e4), truth pass by the driver's own
    ``in_truth_phase_space``, reco pass on the rectangle with ``sim_pass``. Returns the kept rows' ROOT entry numbers
    and the arrays the loader returns. The loader reads the tree sequentially and appends each kept row, so its k-th
    row is the k-th kept entry: the alignment rests on that traversal of the pinned loader."""
    pt_lo, pt_hi, pz_lo, pz_hi = bounds
    wt0, wr0 = cols["w_truth"], cols["w_reco"]
    with np.errstate(invalid="ignore"):
        good_w = np.isfinite(wt0) & np.isfinite(wr0) & (wt0 >= 0) & (wt0 < 1e4) & (wr0 >= 0) & (wr0 < 1e4)
        rp, rz = cols["sim"], cols["sim_pz"]
        rec_ok = np.isfinite(rp) & np.isfinite(rz) & (pt_lo <= rp) & (rp <= pt_hi) & (pz_lo <= rz) & (rz <= pz_hi)
    tru_ok = np.fromiter((driver.in_truth_phase_space(a, b, pt_lo, pt_hi, pz_lo, pz_hi)
                          for a, b in zip(cols["MC"].tolist(), cols["MC_pz"].tolist())), bool, cols["MC"].shape[0])
    passed = cols["sim_pass"] != 0
    keep = good_w & (tru_ok | (passed & rec_ok))
    pr = (passed & rec_ok)[keep]
    tp, tz = cols["MC"][keep], cols["MC_pz"][keep]
    return {"entry": cols["entry"][keep],
            "truth_pt": np.where(np.isfinite(tp), tp, -9999.0), "truth_pz": np.where(np.isfinite(tz), tz, -9999.0),
            "reco_pt": np.where(pr, rp[keep], -9999.0), "reco_pz": np.where(pr, rz[keep], -9999.0),
            "pass_reco": pr, "pass_truth": tru_ok[keep],
            "w_truth": wt0[keep] * pot_scale, "w_reco": wr0[keep] * pot_scale}


def same_bits(a, b) -> bool:
    """Equal shape, equal dtype and equal contents; float64 by bit pattern (signed zeros distinct)."""
    a, b = np.asarray(a), np.asarray(b)
    if a.shape != b.shape or a.dtype != b.dtype:
        return False
    if a.dtype == np.float64 and b.dtype == np.float64:
        return bool(np.array_equal(a.view(np.uint64), b.view(np.uint64)))
    return bool(np.array_equal(a, b))


def c_key(indep: dict, call: dict) -> dict:
    """The independently derived arrays equal, bit for bit, the arrays the driver passed to OmniFold; the kept entry
    numbers strictly increase (so the key is unique) and fit uint32."""
    a, k = call["args"], call["kwargs"]
    MCgen, MCreco, pass_reco, pass_truth = (np.asarray(x) for x in a[:2] + a[3:5])
    pairs = {"truth_pt": MCgen[:, 0], "truth_pz": MCgen[:, 1], "reco_pt": MCreco[:, 0], "reco_pz": MCreco[:, 1],
             "pass_reco": np.asarray(pass_reco, bool), "pass_truth": np.asarray(pass_truth, bool),
             "w_truth": np.asarray(k["MCgen_weights"]), "w_reco": np.asarray(k["MCreco_weights"])}
    equal = {n: same_bits(indep[n], v) for n, v in pairs.items()}
    e = indep["entry"]
    increasing = bool(e.size == 0 or np.all(np.diff(e) > 0))
    fits = bool(e.size == 0 or (e.min() >= 0 and e.max() < 2 ** 32))
    return {"equal": equal, "rows": int(e.size), "strictly_increasing": increasing, "fits_uint32": fits,
            "pass": bool(all(equal.values()) and increasing and fits)}


# ------------------------------------------------------------------------------------------- the table and controls


def driver_rows(call: dict) -> dict:
    """What the driver itself fills, from the recorded OmniFold call: its truth-passing rows' truth pT, p||, w_truth
    and float(step-2 ratio) x float(w_truth), in its fill order."""
    k = call["kwargs"]
    MCgen = np.asarray(call["args"][0])
    pt_mask = np.asarray(call["args"][4], bool)
    step2 = np.asarray(call["out"][1])
    w_prior = np.asarray(k["MCgen_weights"], np.float64)[pt_mask]
    if step2.shape != w_prior.shape:
        raise GateFailure(f"step-2 weights {step2.shape} do not match the truth-passing rows {w_prior.shape}")
    return {"pt_mask": pt_mask, "truth_pt": MCgen[pt_mask, 0].astype(np.float64),
            "truth_pz": MCgen[pt_mask, 1].astype(np.float64), "w_prior": w_prior,
            "w_unfolded": step2.astype(np.float64) * w_prior}


def weight_table(indep: dict, call: dict) -> dict:
    """The written columns: the driver's rows (``driver_rows``) keyed by the independently derived entry numbers."""
    d = driver_rows(call)
    return {"entry": indep["entry"][d["pt_mask"]].astype(np.uint32), "truth_pt": d["truth_pt"],
            "truth_pz": d["truth_pz"], "w_prior": d["w_prior"], "w_unfolded": d["w_unfolded"]}


def c_flux(flux_bins) -> dict:
    """The 14 flux values agree to one (finite) ulp of the largest. Then the entries are interchangeable, and one value
    serves a binning other than these 14 bins (their meaning as the integrated flux comes from the input's provenance)."""
    f = np.asarray(flux_bins, np.float64)
    if f.shape != (14,) or not np.all(np.isfinite(f)):
        return {"values": f.tolist(), "pass": False}
    with np.errstate(over="ignore"):  # np.spacing of the largest float is infinite, and refused below
        spread, ulp = float(f.max() - f.min()), float(np.spacing(f.max()))
    return {"values": f.tolist(), "spread": spread, "ulp": ulp,
            "pass": bool(np.isfinite(ulp) and np.all(f > 0) and spread <= ulp)}


def c_complete(table: dict, denom: dict) -> dict:
    """The truth-passing signal rows and the kept mc_truth_denom rows are the same multiset of (pT, p||, w_truth), bit
    for bit (sorted by bit pattern). Then on any binning both completeness histograms hold the same sum of the same
    values per cell, so c is 1 to summation rounding wherever the denominator is positive, and where it is zero both
    cross sections are zero."""
    s = (table["truth_pt"], table["truth_pz"], table["w_prior"])
    d = tuple(np.asarray(denom[c], np.float64) for c in DENOM_COLUMNS)
    if s[0].shape != d[0].shape:
        return {"signal_rows": int(s[0].size), "denominator_rows": int(d[0].size), "pass": False}
    i = np.lexsort(tuple(np.ascontiguousarray(x).view(np.uint64) for x in s[::-1]))
    j = np.lexsort(tuple(np.ascontiguousarray(x).view(np.uint64) for x in d[::-1]))
    equal = all(same_bits(a[i], b[j]) for a, b in zip(s, d))
    return {"signal_rows": int(s[0].size), "denominator_rows": int(d[0].size), "pass": bool(equal)}


def th2_global(h, nx: int, ny: int) -> np.ndarray:
    """Every global bin of a TH2D, under- and overflow included: bin = ix + (nx + 2) iy."""
    return np.array([h.GetBinContent(b) for b in range((nx + 2) * (ny + 2))], np.float64)


def interior(v, nx: int, ny: int) -> np.ndarray:
    """The grid cells of a global-bin vector, as (pT bin) x ny + (p|| bin) (``th2_vector``'s order)."""
    return np.asarray(v).reshape(ny + 2, nx + 2)[1:-1, 1:-1].T.reshape(-1)


def c_cmap(R, completeness, pt_edges, pz_edges, num_rows: dict, den_rows: dict) -> dict:
    """The driver's own completeness map (hOFCompleteness2D, hOFInputTruth2D, hOFTruthDenom2D) on its grid, judged when
    C-COMPLETE holds:
    - pass: c within CMAP_ATOL of 1 wherever the denominator is positive, and 0 where it is zero (ROOT's Divide);
    - rounding: every zero cell zero and the largest miss above CMAP_ATOL but at most CMAP_ROUNDING, and the map is the
      driver's own summation: the numerator and denominator refilled from the recorded rows in the driver's fill order
      (``num_rows``: its truth-passing rows; ``den_rows``: its denominator rows) equal hOFInputTruth2D and
      hOFTruthDenom2D bit for bit over every global bin, and their ratio equals hOFCompleteness2D bit for bit over
      every global bin. Equal
      multisets summed in two orders; the run takes the declared fallback and records the miss as a finding;
    - stop: anything else (a zero cell nonzero, no positive cell, a larger miss, or a map the rows do not make)."""
    h_c, h_num, h_den = completeness
    nx, ny = len(pt_edges) - 1, len(pz_edges) - 1
    c, den = R.th2_vector(h_c, nx, ny), R.th2_vector(h_den, nx, ny)
    pos = den > 0
    dev = float(np.max(np.abs(c[pos] - 1))) if pos.any() else float("inf")
    zeros = bool(np.all(c[~pos] == 0))
    num_g = fill_root_bins(num_rows["truth_pt"], num_rows["truth_pz"], num_rows["w_prior"], pt_edges, pz_edges)
    den_g = fill_root_bins(den_rows["truth_pt"], den_rows["truth_pz"], den_rows["w_truth"], pt_edges, pz_edges)
    refill = {"numerator": same_bits(num_g, th2_global(h_num, nx, ny)),
              "denominator": same_bits(den_g, th2_global(h_den, nx, ny)),
              "map": same_bits(np.divide(num_g, den_g, out=np.zeros_like(num_g), where=den_g != 0),
                               th2_global(h_c, nx, ny))}
    kind = ("pass" if pos.any() and zeros and dev <= CMAP_ATOL else
            "rounding" if pos.any() and zeros and dev <= CMAP_ROUNDING and all(refill.values()) else "stop")
    return {"max_dev": dev, "cells_positive": int(pos.sum()), "zero_cells_zero": zeros, "refill": refill,
            "kind": kind, "pass": kind == "pass"}


def fill_cells(pt, pz, w, pt_edges, pz_edges, bin_index) -> np.ndarray:
    """The driver's TH2D fill restricted to the grid: the sum of w per cell in row order, lower edge in, upper edge
    out, as (pT bin) x n_pz + (p|| bin)."""
    nx, ny = len(pt_edges) - 1, len(pz_edges) - 1
    ip, iz = bin_index(pt, pt_edges), bin_index(pz, pz_edges)
    ok = (ip >= 0) & (iz >= 0)
    return np.bincount((ip * ny + iz)[ok], weights=np.asarray(w, np.float64)[ok], minlength=nx * ny)


def fill_root_bins(pt, pz, w, pt_edges, pz_edges) -> np.ndarray:
    """The same fill over ROOT's global bins, under- and overflow included: bin = ix + (nx + 2) iy, ix in 0..nx+1."""
    pe, ze = np.asarray(pt_edges, np.float64), np.asarray(pz_edges, np.float64)
    nx, ny = pe.size - 1, ze.size - 1
    ix = np.searchsorted(pe, np.asarray(pt, np.float64), side="right")
    iy = np.searchsorted(ze, np.asarray(pz, np.float64), side="right")
    return np.bincount(ix + (nx + 2) * iy, weights=np.asarray(w, np.float64), minlength=(nx + 2) * (ny + 2))


def event_completeness(pt, pz, w_input, denom, pt_edges, pz_edges, bin_index) -> np.ndarray:
    """c per cell from the rows: (sum of w_input over the signal rows) / (sum of the denominator's w_truth), 0 where the
    denominator is 0 (ROOT's Divide)."""
    num = fill_cells(pt, pz, w_input, pt_edges, pz_edges, bin_index)
    den = fill_cells(denom["truth_pt"], denom["truth_pz"], denom["w_truth"], pt_edges, pz_edges, bin_index)
    return np.divide(num, den, out=np.zeros_like(num), where=den != 0)


def xsec_from_weights(pt, pz, w, pt_edges, pz_edges, flux_bins, data_pot, n_nucleons, bin_index, denom=None,
                      w_input=None, cm2_per_m2=CM2_PER_M2) -> np.ndarray:
    """d2sigma/dpT dp|| on the given edges from per-event weights: the driver's fill (``fill_cells``) and its
    extraction (``extract_cross_section_2d``: u / (c Phi_i N POT dpT dp||) x 1e4, zero where c, Phi, N or POT is not
    positive), the 14 flux values applied by pT-bin index. c is 1 without ``denom``; with it, ``event_completeness``."""
    nx, ny = len(pt_edges) - 1, len(pz_edges) - 1
    if len(flux_bins) != nx:
        raise GateFailure(f"{len(flux_bins)} flux values for {nx} pT bins")
    u = fill_cells(pt, pz, w, pt_edges, pz_edges, bin_index)
    c = np.ones(nx * ny) if denom is None else event_completeness(pt, pz, w_input, denom, pt_edges, pz_edges,
                                                                    bin_index)
    dpt, dpz = np.diff(np.asarray(pt_edges, np.float64)), np.diff(np.asarray(pz_edges, np.float64))
    out = np.zeros(nx * ny)
    for ix in range(nx):
        flux_i = float(flux_bins[ix])
        for iy in range(ny):
            g = ix * ny + iy
            if flux_i > 0 and n_nucleons > 0 and data_pot > 0 and c[g] > 0:
                out[g] = (u[g] / (c[g] * flux_i * n_nucleons * data_pot * dpt[ix] * dpz[iy])) * cm2_per_m2
    return out


def exact(x: np.ndarray, ref: np.ndarray, rtol: float) -> dict:
    x, ref = np.asarray(x, np.float64), np.asarray(ref, np.float64)
    if x.shape != ref.shape:
        return {"max_rel": float("inf"), "pass": False}
    nz = ref != 0
    rel = float(np.max(np.abs(x[nz] / ref[nz] - 1))) if nz.any() else 0.0
    zeros = bool(np.all(x[~nz] == 0))
    return {"max_rel": rel, "cells": int(nz.sum()), "zero_cells_zero": zeros,
            "pass": bool(nz.any() and rel <= rtol and zeros)}


def load_references(cfg: dict, driver) -> dict:
    """``references.npz`` at its pin, with both reference grids complete: E_R's on the driver's edges, Tier 1's on the
    bound paper pT edges and the driver's p|| edges."""
    path = REPO / cfg["references"]["path"]
    raw = path.read_bytes()  # hashed and loaded from one buffer: the vectors judged are the pinned bytes
    if hashlib.sha256(raw).hexdigest() != cfg["references"]["sha256"]:
        raise GateFailure(f"{path} does not match its pinned sha256")
    with np.load(io.BytesIO(raw), allow_pickle=False) as z:
        refs = {k: z[k] for k in z.files}
    want = {"er_pt_edges": driver.PT_EDGES, "er_pz_edges": driver.PZ_EDGES,
            "paper_pt_edges": cfg["paper_pt_edges"], "paper_pz_edges": driver.PZ_EDGES}
    if sorted(refs) != sorted([*want, "er", "paper", "meta"]):
        raise GateFailure(f"references.npz holds {sorted(refs)}")
    for k, v in want.items():
        if refs[k].dtype != np.float64 or not same_bits(refs[k], np.asarray(v, np.float64)):
            raise GateFailure(f"references.npz {k} differs from the bound grid")
    for k in ("er", "paper"):
        if refs[k].dtype != np.float64 or refs[k].shape != ((len(driver.PT_EDGES) - 1) * (len(driver.PZ_EDGES) - 1),):
            raise GateFailure(f"references.npz {k} has dtype {refs[k].dtype} and shape {refs[k].shape}")
    return refs


def own_hist(R, path: Path, name: str, pt_edges, pz_edges, flow: bool = False) -> np.ndarray:
    """One TH2D of the run's own xsec.root, its axes checked against the edges; the grid cells, or every global bin."""
    import ROOT
    f = ROOT.TFile.Open(str(path))
    try:
        h = f.Get(name)
        if not h:
            raise GateFailure(f"{path.name} has no {name}")
        for ax, e in ((h.GetXaxis(), pt_edges), (h.GetYaxis(), pz_edges)):
            got = [ax.GetBinLowEdge(i) for i in range(1, ax.GetNbins() + 2)]
            if not same_bits(np.asarray(got, np.float64), np.asarray(e, np.float64)):
                raise GateFailure(f"{name}'s axis {got} is not {list(e)}")
        nx, ny = len(pt_edges) - 1, len(pz_edges) - 1
        if flow:
            return np.array([h.GetBinContent(b) for b in range((nx + 2) * (ny + 2))])
        return R.th2_vector(h, nx, ny)
    finally:
        f.Close()


# ------------------------------------------------------------------------------------------- staging and custody


def staging_root(cfg: dict) -> Path:
    root = cfg["inputs"]["staging"].get("root")
    if not root:
        raise GateFailure("the staging root is bound at the binding; config.json has none")
    return Path(root).resolve()


def staged(cfg: dict) -> dict:
    root = staging_root(cfg)
    return {k: root / cfg["inputs"]["staging"][k] for k in ("CV", "MC")}


def stage(cfg: dict, R) -> dict:
    """O_NOATIME copies of the CV omnifile and the flux file into the staging root. Each goes to a partial name unique
    to this invocation (host, process and a random token), and only a partial this invocation created is removed. It
    is checked against its pin and made read-only, and is published under its final name by a hard
    link, which never replaces an existing file. A failed copy leaves no file of its own; a stale partial refuses. At
    the end the staging root is made read-only (0555), so its names cannot be replaced by an ordinary write."""
    out = {}
    root = staging_root(cfg)
    root.mkdir(parents=True, exist_ok=True)
    for key, dest in staged(cfg).items():
        stale = [p.name for p in root.iterdir() if p.name == dest.name or p.name.startswith(dest.name + ".partial")]
        if stale:
            raise GateFailure(f"{stale} exist in the staging root")
        part = dest.with_name(f"{dest.name}.partial.{socket.gethostname()}.{os.getpid()}.{secrets.token_hex(8)}")
        try:
            got = R.copy_noatime(Path(cfg["inputs"][f"{key}_source"]), part)  # creates the partial exclusively
        except FileExistsError:
            raise GateFailure(f"{part.name} exists: another invocation's partial, left in place") from None
        except BaseException:
            part.unlink(missing_ok=True)
            raise
        try:
            if got != cfg["inputs"][f"{key}_sha256"]:
                raise GateFailure(f"the staged {key} has sha256 {got[:12]}, not its pin")
            os.chmod(part, 0o444)
            os.link(part, dest)
        finally:
            part.unlink(missing_ok=True)
        out[key] = {"path": str(dest), "sha256": got}
    os.chmod(root, 0o555)
    return out


def identity(path) -> dict:
    """A file's identity (device, inode, size, mtime, mode), by path or by open descriptor."""
    st = os.stat(path)
    return {"dev": st.st_dev, "ino": st.st_ino, "size": st.st_size, "mtime_ns": st.st_mtime_ns, "mode": st.st_mode}


def same_file_key(ident: dict) -> tuple:
    """Identity without the device number, which a network filesystem may number differently on each node (the run
    verifies on a compute node; cleanup runs on a login node)."""
    return tuple(ident.get(k) for k in ("ino", "size", "mtime_ns", "mode"))


def held_sha256(fh) -> str:
    """sha256 of a held file by positioned reads (the handle's offset is never moved)."""
    h, off, fd = hashlib.sha256(), 0, fh.fileno()
    while block := os.pread(fd, 1 << 24, off):
        h.update(block)
        off += len(block)
    return h.hexdigest()


def held_path(entry: dict) -> str:
    """A path that opens the held file itself, whatever its name now names (/proc/self/fd on Linux, /dev/fd else)."""
    fd = entry["handle"].fileno()
    proc = Path("/proc/self/fd")
    return str(proc / str(fd)) if proc.is_dir() else f"/dev/fd/{fd}"


def public(verified: dict) -> dict:
    """``verified`` without its open handles, for the records."""
    return {k: {kk: vv for kk, vv in v.items() if kk != "handle"} for k, v in verified.items()}


def check_staged(cfg: dict, R) -> dict:
    """Each staged copy under the staging root is opened through O_NOATIME and held open for the run; the held file is
    the one the name names, and its bytes equal the pin. Returns digest, identity and the handle: the independent read
    and C-STAGE use the held file, so a name swapped and restored cannot feed them other bytes."""
    root = staging_root(cfg)
    verified = {}
    for key, path in staged(cfg).items():
        if not under(path, root) or path.is_symlink():
            raise GateFailure(f"{key} {path} is not a plain file under the staging root")
        fh = R.open_noatime(path)
        try:
            before = identity(path)
            if identity(fh.fileno()) != before:
                raise GateFailure(f"the staged {key} was replaced while it was opened")
            got = held_sha256(fh)
            if got != cfg["inputs"][f"{key}_sha256"]:
                raise GateFailure(f"the staged {key} has sha256 {got[:12]}, not its pin")
            if identity(path) != before:
                raise GateFailure(f"the staged {key} changed while it was hashed")
        except BaseException:
            fh.close()
            raise
        verified[key] = {"sha256": got, "identity": before, "handle": fh}
    return verified


def c_stage(cfg: dict, R, verified: dict) -> dict:
    """After the run: each staged name still names the held, verified file (device, inode, size, mtime, mode) with the
    same digest, read again through O_NOATIME, and the staging root admits no ordinary write."""
    rows = {}
    for key, path in staged(cfg).items():
        same = identity(path) == verified[key]["identity"]
        rows[key] = {"same_file": same, "sha256_again": R.sha256_noatime(path) == cfg["inputs"][f"{key}_sha256"]}
    ro = (os.stat(staging_root(cfg)).st_mode & 0o222) == 0
    return {**rows, "root_read_only": ro,
            "pass": bool(ro and all(r["same_file"] and r["sha256_again"] for r in rows.values()))}


def resolve_argv(cfg: dict) -> list[str]:
    subs = {"$CV": str(staged(cfg)["CV"]), "$MC": str(staged(cfg)["MC"])}
    return [subs.get(x, x) for x in cfg["argv"]]


def write_npz(path: Path, arrays: dict, meta: dict) -> str:
    with open(path, "xb") as fh:
        np.savez(fh, **arrays, meta=np.array(json.dumps(meta, sort_keys=True, default=str)))
    return sha256(path)


def write_constants(path: Path, meta: dict) -> None:
    with open(path, "x") as fh:
        fh.write(json.dumps(meta, indent=1, sort_keys=True, default=str) + "\n")


def read_npz(path: Path, columns) -> tuple[dict, dict]:
    with np.load(path, allow_pickle=False) as z:
        if sorted(z.files) != sorted([*columns, "meta"]):
            raise GateFailure(f"{path.name} holds {sorted(z.files)}")
        return {k: z[k] for k in columns}, json.loads(str(z["meta"]))


def acceptance(out: Path, files: dict, beside=()) -> dict:
    """The product set is exactly the expected one (the four products, plus denominator.npz with the fallback, plus
    SHA256SUMS and the names in ``beside``), and SHA256SUMS parses to exactly the expected digest map, each file
    re-hashed equal."""
    expected = set(PRODUCTS) | ({FALLBACK_PRODUCT} if FALLBACK_PRODUCT in files else set())
    listed = {}
    for line in (out / "SHA256SUMS").read_text().splitlines():
        d, _, n = line.partition("  ")
        listed[n] = d
    present = {p.name for p in out.iterdir()}
    checks = {"names": set(files) == expected, "manifest": listed == files,
              "present": present == expected | {"SHA256SUMS"} | set(beside),
              "rehash": all((out / n).is_file() and sha256(out / n) == d for n, d in files.items())}
    return {**checks, "pass": all(checks.values())}


def publish_done(out: Path, record: dict) -> None:
    """``evw2d.done`` by write-then-rename, so a crash leaves either no marker or a whole one."""
    tmp = out / ".evw2d.done.tmp"
    with open(tmp, "x") as fh:
        fh.write(json.dumps(record, sort_keys=True) + "\n")
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, out / "evw2d.done")


# ------------------------------------------------------------------------------------------- the run


def c_file(back, meta_back, meta, constants_back, cols, indep, call, den_back, den_meta_back, denom,
           fallback) -> dict:
    """The products read back against their sources, independently of the table that was written:
    - the saved meta and constants.json both equal the meta written; the dtypes are the declared ones;
    - the entries equal the independently derived truth-passing entry numbers, and each indexes the independently read
      tree to the saved truth pT, p|| and POT-scaled w_truth bit for bit;
    - the saved weights equal the driver's own rows recomputed from the recorded OmniFold call;
    - the fallback is present exactly when it is declared; its columns are float64 and equal the driver's denominator
      bit for bit, and its meta is the declared one."""
    pot = meta["constants"]["pot_scale"]
    written = json.loads(json.dumps(meta, sort_keys=True, default=str))
    e = back["entry"].astype(np.int64)
    in_range = bool(e.size == 0 or (e.min() >= 0 and e.max() < cols["MC"].size))
    rows = driver_rows(call)
    checks = {
        "meta": meta_back == written, "constants_json": constants_back == written,
        "cm2_per_m2": meta_back.get("constants", {}).get("cm2_per_m2") == CM2_PER_M2,
        "dtypes": back["entry"].dtype == np.uint32 and all(back[c].dtype == np.float64 for c in WEIGHT_COLUMNS[1:]),
        "entries": same_bits(e, indep["entry"][indep["pass_truth"]]),
        "truth_pt": in_range and same_bits(back["truth_pt"], cols["MC"][e]),
        "truth_pz": in_range and same_bits(back["truth_pz"], cols["MC_pz"][e]),
        "w_prior": in_range and same_bits(back["w_prior"], cols["w_truth"][e] * pot),
        "w_prior_driver": same_bits(back["w_prior"], rows["w_prior"]),
        "w_unfolded": same_bits(back["w_unfolded"], rows["w_unfolded"]),
        "fallback_declared": (den_back is not None) == fallback == (
            "event-level" in str(meta_back.get("constants", {}).get("completeness", ""))),  # the file's own selector
    }
    if den_back is not None:
        checks["denominator"] = all(same_bits(den_back[c], np.asarray(denom[c], np.float64)) for c in DENOM_COLUMNS)
        checks["denominator_meta"] = den_meta_back == DENOM_META
    return {**checks, "pass": bool(all(checks.values()))}


def c_flow(back: dict, R, out: Path, pt_edges, pz_edges) -> dict:
    """The file's weights over every global bin of the driver's grid (under- and overflow included) against the run's
    own hUnfold2D (w_unfolded) and hTruth2D (w_prior)."""
    res = {}
    for name, col in (("hUnfold2D", "w_unfolded"), ("hTruth2D", "w_prior")):
        mine = fill_root_bins(back["truth_pt"], back["truth_pz"], back[col], pt_edges, pz_edges)
        ref = own_hist(R, out / "xsec.root", name, pt_edges, pz_edges, flow=True)
        nz = ref != 0
        rel = float(np.max(np.abs(mine[nz] / ref[nz] - 1))) if nz.any() else 0.0
        res[name] = {"max_rel": rel, "flow_sum": float(mine.sum() - fill_cells(
            back["truth_pt"], back["truth_pz"], back[col], pt_edges, pz_edges, R.bin_index).sum()),
            "pass": bool(nz.any() and rel <= FLOW_RTOL and np.all(mine[~nz] == 0))}
    return {**res, "pass": all(v["pass"] for v in res.values())}


def c_cmap_event(back, den_back, completeness, R, pt_edges, pz_edges) -> dict:
    """With the fallback: the event-level completeness rebuilt from the saved rows equals the driver's own
    hOFCompleteness2D on its grid, zero cells included."""
    nx, ny = len(pt_edges) - 1, len(pz_edges) - 1
    mine = event_completeness(back["truth_pt"], back["truth_pz"], back["w_prior"], den_back, pt_edges, pz_edges,
                              R.bin_index)
    ref = R.th2_vector(completeness[0], nx, ny)
    nz = ref != 0
    rel = float(np.max(np.abs(mine[nz] / ref[nz] - 1))) if nz.any() else 0.0
    return {"max_rel": rel, "pass": bool(nz.any() and rel <= FLOW_RTOL and np.all(mine[~nz] == 0))}


def custody(out: Path, names) -> dict:
    """Each product's stat times and the scratch purge rule the binding confirms (files unread for 8 weeks)."""
    rows = {}
    for n in names:
        st = os.stat(out / n)
        rows[n] = {"atime": datetime.fromtimestamp(st.st_atime, timezone.utc).isoformat(timespec="seconds"),
                   "mtime": datetime.fromtimestamp(st.st_mtime, timezone.utc).isoformat(timespec="seconds"),
                   "size": st.st_size}
    return {"files": rows, "purge_rule": "pscratch purges files not read for 8 weeks; exposure = atime + 56 days, "
                                         "to be confirmed at the binding"}


def run(cfg: dict, out: Path, R, driver, ohf, tree_sha: dict, verified: dict, *, config_sha256: str,
        started: float) -> int:
    """One run of E_R's driver with the recorders, then the table, the controls and the files (EVW2D §3-§4)."""
    cpus = R.cpu_count()
    if cpus != int(cfg["cpus"]):
        raise GateFailure(f"E_R's {cfg['cpus']} CPUs are needed, this process has {cpus}")
    threads = {k: os.environ.get(k) for k in cfg["thread_env"]}
    if threads != cfg["thread_env"]:
        raise GateFailure(f"E_R's thread environment {cfg['thread_env']} is needed, not {threads}")
    if out.exists():
        raise GateFailure(f"{out} exists")
    refs = load_references(cfg, driver)
    out.mkdir(parents=True)
    phases, mark = {"preflight": round(time.time() - started, 3)}, [time.time()]

    def phase(name):
        now = time.time()
        phases[name] = round(now - mark[0], 3)
        mark[0] = now
    argv = resolve_argv(cfg)
    staging = staging_root(cfg)
    rec, made = Recorder(), {}
    with contextlib.ExitStack() as stack:
        for p in [*recorder_patches(rec, driver, ohf), xsec_capture(driver, made)]:
            stack.enter_context(p)
        capture = R.run_driver(driver, ohf, argv, out / "xsec.root", staging=staging)
    xsec_sha = sha256(out / "xsec.root")  # the driver's own output, hashed as it returns; acceptance re-hashes it
    rec.require(SEAMS)
    if "hXSec2D" not in made:
        raise GateFailure("the driver never extracted hXSec2D")
    phase("driver")
    a_ex, _ = capture["extract"]
    _, flux_bins, data_pot, n_nucleons, pt_edges, pz_edges = a_ex
    nx, ny = len(pt_edges) - 1, len(pz_edges) - 1
    pot = rec.calls["get_pot_scales"]["out"]
    bounds = (pt_edges[0], pt_edges[-1], pz_edges[0], pz_edges[-1])
    cols = read_signal_tree(held_path(verified["CV"]))  # the verified file itself, whatever the name names now
    indep = keep_rule(cols, driver, pot[2], bounds)
    phase("key")
    call = rec.calls["omnifold"]
    controls = {"C-KEY": c_key(indep, call)}
    if not controls["C-KEY"]["pass"]:  # no valid key: no weights are written; the run records FAIL and stops
        controls["C-REC"] = rec.verify(SEAMS)
        with open(out / "run.json", "x") as fh:
            fh.write(json.dumps({"schema": "evw2d-run/1", "controls_verdict": "FAIL", "controls": controls,
                                 "phases_seconds": phases, "note": "C-KEY failed: no weights were written"},
                                indent=1, sort_keys=True, default=str) + "\n")
        publish_done(out, {"verdict": "FAIL", "findings": [], "reason": "C-KEY", "phases_seconds": phases})
        print(json.dumps({"verdict": "FAIL", "controls": {"C-KEY": False}}), flush=True)
        return RC_CONTROL
    table = weight_table(indep, call)
    denom = rec.calls["collect_truth_denom_arrays"]["out"]
    controls["C-FLUX"] = c_flux(flux_bins)
    controls["C-COMPLETE"] = c_complete(table, denom)
    findings = [] if controls["C-COMPLETE"]["pass"] else ["C-COMPLETE"]
    if not findings:
        controls["C-CMAP"] = c_cmap(R, capture["completeness"], pt_edges, pz_edges, table, denom)
        if controls["C-CMAP"]["kind"] == "rounding":  # the director's condition: the declared fallback, recorded
            findings.append("C-CMAP")
    fallback = bool(findings)
    soft = {"C-COMPLETE"} | ({"C-CMAP"} if "C-CMAP" in findings else set())
    finding_sizes = {"C-CMAP": controls["C-CMAP"]["max_dev"]} if "C-CMAP" in findings else {}
    flux_ok = controls["C-FLUX"]["pass"]
    constants = {
        "flux_bins_m2_per_POT": [float(x) for x in flux_bins],
        "flux_note": (("the 14 values agree to one ulp (C-FLUX); each is the integrated flux Phi (m^-2/POT) by the "
                       "input's provenance. Both validated grids apply them by pT-bin index; another binning applies "
                       "phi_m2_per_POT to every pT bin. The file's fluxIntegral_m2_per_POT parameter is the sum of the "
                       "14 copies, about 14 Phi, and is not a flux.") if flux_ok else
                      "C-FLUX failed: the 14 values are applied by pT-bin index only; no scalar Phi is given."),
        "data_pot": float(data_pot), "mc_pot": float(pot[1]), "pot_scale": float(pot[2]),
        "n_nucleons": float(n_nucleons), "cm2_per_m2": CM2_PER_M2,
        "formula": "d2sigma/dpT dp|| [cm^2/(GeV/c)^2/nucleon] = sum(w_unfolded) / (c Phi N data_pot dpT dp||) x 1e4",
        "completeness": ("1 on every cell with positive denominator content (C-COMPLETE, C-CMAP); cells with none are "
                         "zero" if not fallback else
                         "event-level: c = sum(w_prior) / sum(denominator w_truth) per cell (denominator.npz)"),
        "phase_space": {"pt": [bounds[0], bounds[1]], "pz": [bounds[2], bounds[3]], "theta_max_deg": 20.0,
                        "cells": "lower edge in, upper edge out; rows on the top edges are in the file and in no cell"},
        "analysis_pt_edges": [float(x) for x in pt_edges], "analysis_pz_edges": [float(x) for x in pz_edges],
        "validated_grids": {"ours": [float(x) for x in pt_edges], "paper": [float(x) for x in cfg["paper_pt_edges"]]},
        "validity": "the central value; validated for observables of (pT, p||) only, on the two grids above",
    }
    if flux_ok:
        constants["phi_m2_per_POT"] = float(flux_bins[0])
    meta = {"schema": SCHEMA, "key": {"omnifile_sha256": cfg["inputs"]["CV_sha256"], "tree": TREE,
                                      "column": "entry", "meaning": "ROOT entry number in mc_signal_reco"},
            "columns": list(WEIGHT_COLUMNS), "rows": int(table["entry"].size), "constants": constants,
            "argv": argv, "driver_tree": {"commit": cfg["driver_tree"]["commit"], "code_sha256": tree_sha},
            "inputs_sha256": {k: v["sha256"] for k, v in verified.items()}, "config_sha256": config_sha256,
            "evw2d_sha256": sha256(Path(__file__)), "declaration_sha256": cfg.get("declaration_sha256"),
            "slurm_job": os.environ.get("SLURM_JOB_ID")}
    files = {"weights.npz": write_npz(out / "weights.npz", table, meta)}
    del table
    if fallback:  # the declared fallback (§3): the denominator table travels with the weights
        files[FALLBACK_PRODUCT] = write_npz(out / FALLBACK_PRODUCT,
                                            {c: np.asarray(denom[c], np.float64) for c in DENOM_COLUMNS},
                                            DENOM_META)
    write_constants(out / "constants.json", meta)
    phase("write")
    back, meta_back = read_npz(out / "weights.npz", WEIGHT_COLUMNS)  # every later test reads the files, not memory
    den_back, den_meta_back = (read_npz(out / FALLBACK_PRODUCT, DENOM_COLUMNS) if (out / FALLBACK_PRODUCT).exists()
                               else (None, None))
    constants_raw = (out / "constants.json").read_bytes()  # the manifest takes the digest of the bytes judged
    files["constants.json"] = hashlib.sha256(constants_raw).hexdigest()
    files["xsec.root"] = xsec_sha
    constants_back = json.loads(constants_raw)
    controls["C-FILE"] = c_file(back, meta_back, meta, constants_back, cols, indep, call, den_back, den_meta_back,
                                denom, fallback)
    del cols, indep
    controls["C-FLOW"] = c_flow(back, R, out, pt_edges, pz_edges)
    if fallback:
        controls["C-CMAP-EVENT"] = c_cmap_event(back, den_back, capture["completeness"], R, pt_edges, pz_edges)
    k = meta_back["constants"]  # the exactness tests use the saved constants, grids and completeness selector
    den_used = den_back if "event-level" in k["completeness"] else None

    def from_file(pte, pze):
        return xsec_from_weights(back["truth_pt"], back["truth_pz"], back["w_unfolded"], pte, pze,
                                 k["flux_bins_m2_per_POT"], k["data_pot"], k["n_nucleons"], R.bin_index,
                                 denom=den_used, w_input=back["w_prior"], cm2_per_m2=k["cm2_per_m2"])
    ours = from_file(k["analysis_pt_edges"], k["analysis_pz_edges"])
    self_exact = exact(ours, interior(made["hXSec2D"], nx, ny), EXACT_RTOL)  # the driver's own, in memory
    file_equals_driver = same_bits(own_hist(R, out / "xsec.root", "hXSec2D", pt_edges, pz_edges, flow=True),
                                   made["hXSec2D"])  # the persisted histogram is that one, bit for bit
    controls["C-SELF"] = {**self_exact, "file_equals_driver": file_equals_driver,
                          "pass": bool(self_exact["pass"] and file_equals_driver)}
    controls["C-EXACT-ER"] = exact(ours, refs["er"], EXACT_RTOL)
    controls["C-EXACT-PAPER"] = exact(from_file(k["validated_grids"]["paper"], k["analysis_pz_edges"]),
                                      refs["paper"], EXACT_RTOL)
    controls["C-REC"] = rec.verify(SEAMS)
    phase("controls")
    after = {rel: sha256(driver_tree(cfg) / rel) for rel in REQUIRED_PINS}
    caches = [rel for rel in PYCACHE_DIRS if (driver_tree(cfg) / rel / "__pycache__").exists()]
    controls["C-PINS"] = {"after_run": after, "caches_after_run": caches,
                          "pass": after == cfg["driver_tree"]["code_sha256"] == tree_sha and not caches}
    controls["C-STAGE"] = c_stage(cfg, R, verified)
    phase("final_verify")
    passed = all(v["pass"] for name, v in controls.items() if name not in soft)
    record = {"schema": "evw2d-run/1", "controls_verdict": "PASS" if passed else "FAIL", "findings": findings,
              "finding_sizes": finding_sizes,
              "verdict_note": "the run's verdict is evw2d.done's: the controls and the acceptance of the product set",
              "controls": controls, "files_sha256": dict(files), "phases_seconds": phases,
              "peak_rss_kb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, "cpus": cpus,
              "thread_env": threads, "lgbm": capture.get("lgbm", []), "staged": public(verified),
              "custody": custody(out, sorted(files)),
              **{key: meta[key] for key in ("argv", "driver_tree", "inputs_sha256", "config_sha256", "evw2d_sha256",
                                            "declaration_sha256", "slurm_job", "rows")}}
    with open(out / "run.json", "x") as fh:
        fh.write(json.dumps(record, indent=1, sort_keys=True, default=str) + "\n")
    files["run.json"] = sha256(out / "run.json")
    with open(out / "SHA256SUMS", "x") as fh:
        fh.write("".join(f"{files[n]}  {n}\n" for n in sorted(files)))
    acc = acceptance(out, files)
    phase("acceptance")
    verdict = "PASS" if passed and acc["pass"] else "FAIL"
    publish_done(out, {"verdict": verdict, "findings": findings, "finding_sizes": finding_sizes, "acceptance": acc,
                       "SHA256SUMS": sha256(out / "SHA256SUMS"), "phases_seconds": phases})
    print(json.dumps({"verdict": verdict, "findings": findings, "phases_seconds": phases,
                      "controls": {name: v["pass"] for name, v in controls.items()}}), flush=True)
    for f in findings:
        size = f" (largest miss {controls['C-CMAP']['max_dev']:.3e})" if f == "C-CMAP" else ""
        print(f"FINDING: {f} failed{size}; the declared fallback was taken (denominator.npz). Report it to the "
              "director.", file=sys.stderr)
    return 0 if verdict == "PASS" else RC_CONTROL


def accepted(out: Path) -> dict:
    """A product directory is a result only with a PASS evw2d.done whose manifest digest and files still hold, and
    with denominator.npz exactly when the run recorded findings."""
    done = json.loads((out / "evw2d.done").read_text())
    sums = out / "SHA256SUMS"
    files = {}
    for line in sums.read_text().splitlines():
        d, _, n = line.partition("  ")
        files[n] = d
    acc = acceptance(out, files, beside=("evw2d.done",))
    fallback_matches = (FALLBACK_PRODUCT in files) == bool(done.get("findings"))
    ok = (done.get("verdict") == "PASS" and done.get("SHA256SUMS") == sha256(sums) and acc["pass"]
          and fallback_matches)
    return {"done": done, "acceptance": acc, "fallback_matches_findings": fallback_matches, "pass": bool(ok)}


def cleanup(cfg: dict, out: Path, R, config_sha256: str) -> dict:
    """After a PASS run only: delete the two staged copies, with a ledger row per file in ``<lane_root>/deletions.tsv``
    (UTC time, path, sha256, size, reason). Before anything is deleted: the accepted run was bound to this config, and
    each staged name is a plain file that is the one the run verified (identity) with the run's and the pin's digest;
    the ledger is opened for appending without following a link."""
    acc = accepted(out)
    if not acc["pass"]:
        raise GateFailure(f"{out} is not an accepted product; the staged copies stay")
    rec = json.loads((out / "run.json").read_text())  # covered by the accepted manifest
    if rec.get("config_sha256") != config_sha256:
        raise GateFailure(f"the accepted run was bound to config {str(rec.get('config_sha256'))[:12]}, not this one; "
                          "the staged copies stay")
    sizes = {}
    for key, path in staged(cfg).items():
        ran = rec.get("staged", {}).get(key, {})
        got = None if path.is_symlink() else R.sha256_noatime(path)
        pin = cfg["inputs"][f"{key}_sha256"]
        if got is None or same_file_key(identity(path)) != same_file_key(ran.get("identity", {})) or not (
                got == ran.get("sha256") == pin):
            raise GateFailure(f"the staged {key} is not the file the accepted run verified; nothing is deleted")
        sizes[key] = (got, os.stat(path).st_size)
    root = staging_root(cfg)
    ledger = Path(cfg["lane_root"]) / "deletions.tsv"
    fd = os.open(ledger, os.O_WRONLY | os.O_APPEND | os.O_CREAT | os.O_NOFOLLOW, 0o644)
    st = os.fstat(fd)
    if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1:
        os.close(fd)
        raise GateFailure(f"{ledger} is not a singly linked regular file; nothing is deleted")
    rows = []
    try:
        os.chmod(root, 0o755)
        try:
            for key, path in staged(cfg).items():
                got, size = sizes[key]
                path.unlink()
                rows.append(f"{datetime.now(timezone.utc).isoformat(timespec='seconds')}\t{path}\t{got}\t{size}\t"
                            f"EVW2D run accepted ({out / 'evw2d.done'})\n")
        finally:
            os.chmod(root, 0o555)
    finally:
        os.write(fd, "".join(rows).encode())
        os.close(fd)
    return {"deleted": len(rows), "ledger": str(ledger)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--config-sha256", required=True, help="config.json's digest, as the binding records it")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("stage")
    for name in ("run", "cleanup"):
        sub.add_parser(name).add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    started = time.time()
    cfg, cfg_sha = load_config()
    gate_errors = (GateFailure, OSError)
    try:
        check_interpreter()
        out = a.out.resolve() if a.cmd in ("run", "cleanup") else None
        check_binding(cfg, cfg_sha, a.config_sha256, out)
        if a.cmd == "run" and out.exists():
            raise GateFailure(f"--out {out} exists")
        commit = check_checkout(cfg)
        tree_sha = check_tree(cfg)
        R, driver, ohf = load_runner(cfg)
        gate_errors = (GateFailure, R.GateFailure, OSError)
        if a.cmd == "stage":
            print(json.dumps(stage(cfg, R)))
            return 0
        if a.cmd == "cleanup":
            print(json.dumps(cleanup(cfg, out, R, cfg_sha)))
            return 0
        alloc = check_allocation()
        verified = check_staged(cfg, R)
        allowed = (staging_root(cfg), out, driver_tree(cfg), REPO)
        with R.read_guards(PROTECTED, allowed, writable=(out,)):
            rc = run(cfg, out, R, driver, ohf, tree_sha, verified, config_sha256=cfg_sha, started=started)
        print(json.dumps({"allocation": alloc, "commit": commit, "rc": rc}))
        return rc
    except gate_errors as e:
        print(f"refusing: {e}", file=sys.stderr)
        return RC_GATE


if __name__ == "__main__":
    sys.exit(main())
