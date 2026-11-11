#!/usr/bin/env python3
"""FD-PRR probe: one level of the prior-retention study through the bound closure runner, unchanged.

Declaration: docs/orchestration/state/measurement-paper/5d-community-20261024/FD-PRR-DECLARATION.md (rev 2).

    prr_probe.py run --level L --truth T -- <s5p_nullexp.py arguments>
    prr_probe.py manifest --out JSON
    prr_probe.py tasks --out DIR --stage-dir DIR --runs DIR
    prr_probe.py gate --task ID --queue TSV --log DIR --t0 EPOCH --limit-h H --mode {dry,full}
    prr_probe.py stage --manifest JSON --dest DIR --out JSON
    prr_probe.py verify-stage --stage JSON
    prr_probe.py pair --stage JSON --runs DIR --out JSON
    prr_probe.py price

A LEVEL is configuration (e) (s5e candidate R: the refinement at 400 trees and 31 leaves, the three OmniFold estimators
at the deterministic F2 parameters, K = 5) with at most one factor changed (declaration §3.3):

* F1, the iteration count K: ``--iters``;
* F2, the capacity (n_estimators, num_leaves) of the three OmniFold estimators: ``--capacity``, through the bound
  ``s5p_numerics.omnifold_capacity``. The refinement keeps 400/31;
* F3, the unfolding-MC size: ``--mc-fraction quarter``;
* F4, the observables the OmniFold estimators see: a column mask around ``omnifold_nn_core.omnifold_loop`` for one
  invocation (``column_mask``). It slices the loop's three coordinate arguments only. The truth histogram, the
  extraction and the refinement keep all five coordinates, so every level reports the same 16 cells.

The runner is ``s5p_nullexp.py``, unchanged, in its noise-free closure mode (``--expectation --no-nuisance``), with
FD-STAB's truth plumbing (``estimator_stability_probe.pvl_truth`` and ``closure_truth_kind``). Nothing in a production
module is edited: ``install`` rebinds, for one invocation, ``omnifold_nn_core.omnifold_loop`` (F4 only) and
``s5n_pseudo.write_product`` (every product's meta gains a ``prior_retention`` block), and checks the runner's own
parsed arguments against the level (``check_namespace``) before it does anything. No product is written unless that
check ran, and a masked level writes nothing unless the loop was called exactly once through the mask.

Before any import of the runner, ``run`` checks every bound module against its digest (control C-PINS) and the input
npz's axis names and edges against the pv-ladder's 5D fine grid (control C-COLS).

``gate`` lets a queued task start only if the job's projected charge, tail included, stays within 0.9 of its
``--time`` (declaration §10.3). In a full job every level must have a rate measured by the dry run.

``stage`` copies each shared input once through O_NOATIME (REF-G1's ``copy_noatime``) and records its stat before
and after. It refuses if the copy's digest differs from its pin, or if the source's atime, mtime, size or inode moved.
``pair`` is control C-PAIR (B0 against FD-STAB's control closures, bitwise) and C-MASK (the five-column mask against
B0, bitwise), on the dry run's products.

MEASURES: one level's closure products. CANNOT AUTHORIZE: a reading (``prr_read.py``), an estimator change, or any
claim.
"""
from __future__ import annotations

import argparse
import hashlib
import heapq
import json
import math
import os
import sys
import time
from contextlib import contextmanager
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ND = HERE.parent
REPO = ND.parent
for _p in (ND, ND / "pv-ladder"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

SCHEMA = "prior-retention-probe/1"

# ------------------------------------------------------------------------------------------- C-PINS (bound modules)
# Each digest is the file at main 52334c34, where FD-STAB's production modules are unchanged since its pin cc54d86f.
CODE_PINS = {
    "nd-unfolding/s5p_nullexp.py": "789271bb76e0d589e8b3252ce72ef7e4fab40acdf1ab4744162bd64e339fd2ab",
    "nd-unfolding/s5p_numerics.py": "7ad8ca0f73989128b783b59d55670687c293d186b2643ea799a3e67c047bf185",
    "nd-unfolding/s5c_unfold.py": "510d749a2e82fa448de6172753ae2adc9ebd81a89d4f18bf76beb5faa8bb3968",
    "nd-unfolding/omnifold_nn_core.py": "24f87f119073c4f125c2f753310507d4375b6f8a1b7751e59d3615dd50e90582",
    "nd-unfolding/s5n_pseudo.py": "8981f97b96b418cfe46f1e940cb120f174053d7d3429f3b0b01a229c6c02ee6c",
    "nd-unfolding/s5e_trace.py": "c47e9dd3feef9eab323e40f4e0da770ad67e86431a1ce95f99a10007decc66c1",
    "nd-unfolding/s5e_candidate.py": "bda8c48ce2365e173bbba083b18233d6f6b7c2dfbab5179156073860c8281ec7",
    "nd-unfolding/s5e_deform.py": "6726ff99c7787d1ee6dff7fa5d08df88f9df76285d98c4c462f964ac6164779f",
    "nd-unfolding/s5p_truths.py": "40b6506d441d379e8915506d6d6cd4390b8d86bf704dfccb82fff2df86cf3913",
    "nd-unfolding/s5c_pseudo.py": "d81d4f46fb55f25fdf7ce2e4b9a9a63bf876beaf754bdc250eee974579e11f5d",
    "nd-unfolding/xsec_nd.py": "454001f3c9ac3aa6485d184aadb8aba65dd71dba124816962b9c3b6344920fa5",
    "nd-unfolding/s5p_universe.py": "805a00063a6136e25c6f8f57d228ec996c85a9bc997981632643baeee6c13d80",
    "nd-unfolding/estimator_stability_probe.py": "37ff9d028e53685db1c5adc606061235b21e5cb8a86752f5f0f987e6851dd9b0",
    "nd-unfolding/pv-ladder/pvl_lib.py": "f8a7d2c2fcd37b025ae3c028088d496b1aea7519d347febb3d63da6511015481",
    # the refinement: s5n_pseudo imports the driver's refine_stay_positive at call time, and records its digest
    "2d-unfolding/unfold_2d_omnifold_unbinned.py": "74a4ed69c3fa9c4ae5b6866f36343212b8d3f903fddde6c7bd40c382c1167d56",
}


class Refused(RuntimeError):
    """A declared check refused: nothing is run or written."""


def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 22), b""):
            h.update(block)
    return h.hexdigest()


def check_pins(pins: dict = CODE_PINS, root: Path = REPO) -> None:
    """C-PINS: every bound module is the file its digest names; refuses on the first that is not."""
    for rel, want in pins.items():
        p = root / rel
        if not p.is_file() or sha256_path(p) != want:
            raise Refused(f"C-PINS: {rel} is not the bound file ({want[:12]}...)")


# ------------------------------------------------------------------------------------------- the levels (§3.3)
AXES = ("pt", "pz", "eavail", "q3", "W")  # the classifier columns, checked on the input (C-COLS), never assumed
NO_W = ("pt", "pz", "eavail", "q3")
MASKS = {  # level -> (columns of MCgen: step-2 classifier and regressor; columns of MCreco and measured: step 1)
    "O5": (AXES, AXES),
    "O4r": (AXES, NO_W),
    "O4": (NO_W, NO_W),
    "O3": (("pt", "pz", "eavail"),) * 2,
    "O2": (("pt", "pz"),) * 2,
}
# id: factor, iters, capacity, mc_fraction, mask, units (u = one B0 unfold; the multipliers are §10.1's assumptions)
LEVELS = {
    "B0": dict(factor=None, iters=5, capacity=None, mc_fraction="half", mask=None, units=1.0),
    "K2": dict(factor="F1", iters=2, capacity=None, mc_fraction="half", mask=None, units=0.4),
    "K10": dict(factor="F1", iters=10, capacity=None, mc_fraction="half", mask=None, units=2.0),
    "K20": dict(factor="F1", iters=20, capacity=None, mc_fraction="half", mask=None, units=4.0),
    "K50": dict(factor="F1", iters=50, capacity=None, mc_fraction="half", mask=None, units=10.0),
    "C25": dict(factor="F2", iters=5, capacity=(25, 4), mc_fraction="half", mask=None, units=0.5),
    "C400": dict(factor="F2", iters=5, capacity=(400, 31), mc_fraction="half", mask=None, units=4.0),
    "C1000": dict(factor="F2", iters=5, capacity=(1000, 63), mc_fraction="half", mask=None, units=15.0),
    "MCq": dict(factor="F3", iters=5, capacity=None, mc_fraction="quarter", mask=None, units=1.0),
    "O4r": dict(factor="F4", iters=5, capacity=None, mc_fraction="half", mask="O4r", units=1.0),
    "O4": dict(factor="F4", iters=5, capacity=None, mc_fraction="half", mask="O4", units=1.0),
    "O3": dict(factor="F4", iters=5, capacity=None, mc_fraction="half", mask="O3", units=1.0),
    "O2": dict(factor="F4", iters=5, capacity=None, mc_fraction="half", mask="O2", units=1.0),
    "O5": dict(factor="C-MASK", iters=5, capacity=None, mc_fraction="half", mask="O5", units=1.0),
}
FACTORS = {"F1": ("K2", "K10", "K20", "K50"), "F2": ("C25", "C400", "C1000"), "F3": ("MCq",),
           "F4": ("O4r", "O4", "O3", "O2")}
FLOOR_LEVEL = {"F1": "K20", "F2": "C400", "F3": "MCq", "F4": "O2"}  # each factor's measured level for s_F (§3.5)

# ------------------------------------------------------------------------------------------- truths and splits (§3.2, §3.5)
TRUTHS = ("nominal", "W1", "W2", "W3", "q3", "stage0c_gibuu", "closure_nuwro", "A7_mnvtune", "A7_genie_cv",
          "A7_genie_mec", "A7_nuwro", "A7_gibuu")  # Table II's 12 graded truths, in F0's order
N_CELLS = 16  # R00-R15
FLAGGED = ("A7_gibuu", "q3")
PRIOR = "nominal"  # P_c: the nominal truth's x_true at the same split (§4.1)
PRIMARY_SEED = 991000  # FD-STAB's closure seed: B0 is FD-STAB's control at every truth
FLOOR_SEEDS = (994001, 994002, 994003, 994004)  # not 991001: two committed tests use it as the refused value
FLOOR_TRUTH = "A7_gibuu"
FLOOR_LEVELS = ("B0",) + tuple(FLOOR_LEVEL.values())


def closure_spec(name: str) -> tuple:
    """FD-STAB's closure row for a truth (name, hypothesis, alternative, kind, amplitude), read, never retyped."""
    import estimator_stability_probe as esp
    rows = {r[0]: r for r in esp.CLOSURES}
    if name not in rows:
        raise KeyError(f"{name} is not an FD-STAB closure")
    return rows[name]


# ------------------------------------------------------------------------------------------- the tasks and jobs (§10)
def task_id(level: str, truth: str, seed: int) -> str:
    return f"prr_{level}_{truth}_s{seed}"


def all_tasks() -> list[tuple[str, str, int]]:
    """(level, truth, seed) of every declared unfold: 12 truths at every level of F1-F4 and B0, the five-column mask
    at the nominal truth (C-MASK), and the floor: at each floor seed, A7 GiBUU at B0 and each factor's measured level,
    and the nominal truth at B0."""
    out = [(lv, t, PRIMARY_SEED) for lv in LEVELS if lv != "O5" for t in TRUTHS]
    out.append(("O5", "nominal", PRIMARY_SEED))
    for s in FLOOR_SEEDS:
        out += [(lv, FLOOR_TRUTH, s) for lv in FLOOR_LEVELS] + [("B0", PRIOR, s)]
    return out


CAP_TO_MISC = TRUTHS[-4:]  # (1000, 63) at these four truths runs in misc: 11 tasks of 15 u on 8 lanes would put two
# on three lanes of cap (a 10.0 h --time at the conservative unit); split 7 + 4, the five limits sum to 27.0 (price())


def job_of(level: str, truth: str, seed: int) -> str:
    """dry: one nominal task per level type and the C-MASK level, and B0 at A7 GiBUU, so C-PAIR is complete before any
    full job; iter: the rest of F1; cap: the rest of F2, except (1000, 63) at CAP_TO_MISC; misc: everything else."""
    if seed == PRIMARY_SEED and (truth == "nominal" or (level == "B0" and truth == FLOOR_TRUTH)):
        return "dry"
    if seed != PRIMARY_SEED or (level == "C1000" and truth in CAP_TO_MISC):
        return "misc"
    return {"F1": "iter", "F2": "cap"}.get(LEVELS[level]["factor"], "misc")


JOBS = ("dry", "iter", "cap", "misc")
LANES = 8
UNIT_S = 0.022828 * 3600 * LANES  # 657 s of one lane per B0 unfold (FD-1B-STAGED-DECLARATION.md:530, measured on S1)
UNIT_CONSERVATIVE_S = 1062.0  # 1.25 x the I2 maximum 849.6 s (FD-1B-STAGED-DECLARATION.md:528, :532)
GATE_FRACTION = 0.9
DRY_ALLOWANCE_H = 0.25  # the dry job's staging, verify and pair steps before and after its queue (not projected)
JOB_LIMIT_H = {"dry": 5.25, "iter": 7.5, "cap": 6.5, "misc": 7.25, "ibu": 0.5}  # each job's --time; see price()
CAP_NODE_H = 27.0  # the sum of the limits: on one node a job cannot charge more than its --time


def units(level: str) -> float:
    return float(LEVELS[level]["units"])


def ordered(tasks: list[tuple[str, str, int]]) -> list[tuple[str, str, int]]:
    """Longest first (the dry run's assumed units), then by id: xargs -P feeds the lanes in this order."""
    return sorted(tasks, key=lambda x: (-units(x[0]), task_id(*x)))


def pack(durations: list[float], lanes: int = LANES, busy: list[float] | None = None) -> float:
    """The wall of a queue fed in order to the lane that frees first (as ``xargs -P`` does), the lanes starting with
    ``busy`` seconds left on their running tasks: when the last lane finishes, tail included."""
    free = sorted(busy or [])[:lanes]
    free = free + [0.0] * (lanes - len(free))
    heapq.heapify(free)
    for d in durations:
        heapq.heappush(free, heapq.heappop(free) + d)
    return max(free) if free else 0.0


def price(unit_s: float = UNIT_CONSERVATIVE_S) -> dict:
    """Per job: its units, its packed lane wall at ``unit_s`` and the least --time the gate's 0.9 rule passes with,
    rounded up to a quarter hour (the dry job adds its unprojected steps)."""
    out = {}
    for j in JOBS:
        tasks = ordered([t for t in all_tasks() if job_of(*t) == j])
        wall = pack([units(t[0]) * unit_s for t in tasks])
        need = wall / 3600 / GATE_FRACTION + (DRY_ALLOWANCE_H if j == "dry" else 0.0)
        out[j] = {"tasks": len(tasks), "units": round(sum(units(t[0]) for t in tasks), 3), "wall_h": wall / 3600,
                  "least_limit_h": math.ceil(need * 4 - 1e-9) / 4, "limit_h": JOB_LIMIT_H[j]}
    return out


def runner_argv(a, level: str, truth: str, seed: int) -> list[str]:
    """The s5p_nullexp arguments of one task: FD-STAB's closure line for the truth (estimator_stability_probe
    .candidate_tasks), with the level's flags and this study's tag and output."""
    name, hyp, alt, kind, amp = closure_spec(truth)
    L = LEVELS[level]
    argv = ["--npz", str(a.npz), "--bkg", str(a.bkg), "--expect-npz-sha256", a.expect_npz_sha256,
            "--expect-bkg-sha256", a.expect_bkg_sha256, "--config", "R", "--iters", str(L["iters"]), "--threads", "32",
            "--bank", str(a.bank), "--detector-dir", str(a.detector_dir), "--hypothesis", hyp,
            "--pseudo-seeds", f"{seed}:{seed}", "--no-nuisance", "--expectation", "--mc-fraction", L["mc_fraction"]]
    if L["capacity"] is not None:
        argv += ["--capacity", f"{L['capacity'][0]},{L['capacity'][1]}"]
    argv += ["--tag", f"prr_{level}_{truth}", "--out", f"{a.runs}/{level}/{truth}"]
    if alt is not None:
        path = f"{a.closure_ratio_dir}/{alt[len('CLUSTER:'):]}" if alt.startswith("CLUSTER:") else alt
        argv += ["--alternative", path, "--alternative-truth", kind, "--alternative-amplitude", str(amp)]
    return argv


def queue_lines(a, job: str) -> list[str]:
    """A job's queue: tab-separated id, level, units, script, argv."""
    lines = [f"# FD-PRR queue {job}: columns id, level, units, script, argv (longest first)"]
    for lv, t, s in ordered([x for x in all_tasks() if job_of(*x) == job]):
        argv = ["run", "--level", lv, "--truth", t, "--", *runner_argv(a, lv, t, s)]
        lines.append("\t".join([task_id(lv, t, s), lv, str(units(lv)), "prior_retention/prr_probe.py", *argv]))
    return lines


# ------------------------------------------------------------------------------------------- C-COLS and the mask
def check_columns(npz: Path) -> tuple[str, ...]:
    """C-COLS: the input's axis names (pvl_lib.npz_axes: pt, pz, then the stored extras) are AXES, in that order, and
    its edges are the pv-ladder's 5D fine grid. Read from the file, before any mask is applied."""
    import pvl_lib
    with np.load(npz, allow_pickle=True) as z:
        names = tuple(pvl_lib.npz_axes(z))
        edges = [np.asarray(z[f"edges_{i}"], float) for i in range(int(z["nedges"]))]
    if names != AXES:
        raise Refused(f"C-COLS: the input's columns are {names}, not {AXES}")
    try:
        pvl_lib.check_edges(names, edges)
    except ValueError as e:
        raise Refused(f"C-COLS: {e}") from None
    return names


def column_indices(cols: tuple[str, ...]) -> list[int]:
    return [AXES.index(c) for c in cols]


@contextmanager
def column_mask(mask: str | None, record: dict):
    """For one invocation: ``omnifold_nn_core.omnifold_loop`` sees only the mask's columns of MCgen (the step-2
    classifier and the regressor) and of MCreco and measured (the step-1 classifier). Every other argument passes
    unchanged, and so does the return. ``s5c_unfold.unfold`` resolves the loop in the module at call time, then
    histograms the full five-column MCgen itself. ``record`` counts the calls and holds the columns applied."""
    import omnifold_nn_core as onc
    record.update(calls=0, gen=None, reco=None)
    if mask is None:
        yield
        return
    gen_cols, reco_cols = MASKS[mask]
    gi, ri = column_indices(gen_cols), column_indices(reco_cols)
    orig = onc.omnifold_loop

    def masked(MCgen, MCreco, measured, *args, **kwargs):
        MCgen, MCreco, measured = (np.asarray(x) for x in (MCgen, MCreco, measured))
        for x in (MCgen, MCreco, measured):
            if x.ndim != 2 or x.shape[1] != len(AXES):
                raise Refused(f"the loop was handed a {x.shape} array, not five columns")
        record["calls"] += 1
        record["gen"], record["reco"] = list(gen_cols), list(reco_cols)
        return orig(MCgen[:, gi], MCreco[:, ri], measured[:, ri], *args, **kwargs)

    onc.omnifold_loop = masked
    try:
        yield
    finally:
        onc.omnifold_loop = orig


# ------------------------------------------------------------------------------------------- the namespace check
def check_namespace(ns, level: str, truth: str) -> str | None:
    """The refusal, decided on the runner's own parsed arguments (last value wins, abbreviations resolved)."""
    import s5e_trace
    L = LEVELS[level]
    if getattr(ns, "config", None) != "R":
        return "a level is built on configuration (e): --config must be R"
    if not (getattr(ns, "expectation", False) and getattr(ns, "no_nuisance", False)):
        return "closures are noise-free: --expectation and --no-nuisance are required"
    if getattr(ns, "iters", None) != L["iters"]:
        return f"level {level} runs K = {L['iters']}, not {getattr(ns, 'iters', None)}"
    if s5e_trace.parse_pair(getattr(ns, "capacity", None)) != L["capacity"]:
        return f"level {level} has capacity {L['capacity']}, not {getattr(ns, 'capacity', None)}"
    if getattr(ns, "mc_fraction", None) != L["mc_fraction"]:
        return f"level {level} unfolds with MC {L['mc_fraction']}, not {getattr(ns, 'mc_fraction', None)}"
    seeds = getattr(ns, "pseudo_seeds", None) or ""
    a, _, b = seeds.partition(":")
    if not (a.isdigit() and a == b):
        return "one declared split per task: --pseudo-seeds S:S"
    s = int(a)
    if (level, truth, s) not in set(all_tasks()):
        return f"({level}, {truth}, seed {s}) is not a declared task"
    if getattr(ns, "estimator_seed", None) != 42 or getattr(ns, "threads", None) != 32:
        return "the estimator seed is 42 and the thread count 32, as FD-STAB's control ran"
    name, hyp, alt, kind, amp = closure_spec(truth)
    if str(getattr(ns, "hypothesis", "")) != hyp:
        return f"truth {truth}'s hypothesis is {hyp}"
    got_alt = getattr(ns, "alternative", None)
    if (alt is None) != (got_alt is None):
        return f"truth {truth}'s alternative is {alt}"
    if alt is not None and (float(getattr(ns, "alternative_amplitude", -1)) != float(amp)):
        return f"truth {truth}'s amplitude is {amp}"
    return None


@contextmanager
def namespace_guard(level: str, truth: str, state: dict):
    orig = argparse.ArgumentParser.parse_args

    def parse_args(self, args=None, namespace=None):
        ns = orig(self, args, namespace)
        why = check_namespace(ns, level, truth)
        if why:
            print(f"refusing: {why}", file=sys.stderr)
            raise SystemExit(2)
        state["columns"] = list(check_columns(Path(ns.npz)))
        state["checked"] = True
        return ns

    argparse.ArgumentParser.parse_args = parse_args
    try:
        yield
    finally:
        argparse.ArgumentParser.parse_args = orig


@contextmanager
def install(level: str, truth: str, guard: bool = True):
    """Rebind, for one invocation, the loop (F4 only) and the product writer; restore them on exit."""
    import s5n_pseudo
    if level not in LEVELS:
        raise ValueError(f"unknown level {level!r}")
    if truth not in TRUTHS:
        raise ValueError(f"unknown truth {truth!r}")
    L = LEVELS[level]
    state = {"checked": not guard, "columns": None}
    rec: dict = {}
    here = sha256_path(Path(__file__).resolve())
    orig_write = s5n_pseudo.write_product

    def write_product(out, arrays, meta):
        if not state["checked"]:
            raise RuntimeError("refusing to write: the runner's arguments were never checked")
        if L["mask"] is not None and rec.get("calls") != 1:
            raise RuntimeError(f"refusing to write: the loop was called {rec.get('calls')} times through the mask")
        cap = meta.get("capacity")
        block = {"schema": SCHEMA, "level": level, "truth": truth, "factor": L["factor"],
                 "declared": {"iters": L["iters"], "capacity": None if L["capacity"] is None else list(L["capacity"]),
                              "mc_fraction": L["mc_fraction"], "mask": L["mask"]},
                 "recorded": {"iters": meta.get("iters"), "capacity": None if cap is None else list(cap),
                              "mc_fraction": (meta.get("development") or {}).get("mc_fraction")},
                 "mask": {"calls": rec.get("calls"), "gen_columns": rec.get("gen"), "reco_columns": rec.get("reco")},
                 "input_columns": state["columns"], "code_sha256": here}
        rec["calls"] = 0
        return orig_write(out, arrays, {**meta, "prior_retention": block})

    s5n_pseudo.write_product = write_product
    try:
        with column_mask(L["mask"], rec):
            if guard:
                with namespace_guard(level, truth, state):
                    yield rec
            else:
                yield rec
    finally:
        s5n_pseudo.write_product = orig_write


PROTECTED = ("--capacity", "--config", "--pseudo-seeds", "--expectation", "--no-nuisance", "--mc-fraction", "--iters",
             "--hypothesis", "--alternative", "--alternative-amplitude", "--alternative-truth")


def refuse_argv(rest: list[str]) -> str | None:
    """A first check on argv (the decision is ``check_namespace``): a protected option is spelled in full, once,
    without '='."""
    seen = []
    for tok in rest:
        if not tok.startswith("--"):
            continue
        name = tok.split("=", 1)[0]
        if name in PROTECTED:
            if "=" in tok:
                return f"{name} must be given as a separate argument, not with '='"
            if name in seen:
                return f"{name} is given more than once"
            seen.append(name)
        elif any(p.startswith(name) for p in PROTECTED):
            return f"{name} abbreviates a protected option; spell it in full"
    return None


def run(level: str, truth: str, rest: list[str]) -> int:
    try:
        check_pins()
    except Refused as e:
        print(f"refusing: {e}", file=sys.stderr)
        return 2
    why = refuse_argv(rest)
    if why:
        print(f"refusing: {why}", file=sys.stderr)
        return 2
    import estimator_stability_probe as esp
    rest = list(rest)
    if "--alternative-truth" in rest:
        i = rest.index("--alternative-truth") + 1
        try:
            rest[i] = esp.closure_truth_kind(Path(rest[rest.index("--alternative") + 1]), rest[i])
        except (ValueError, OSError) as exc:
            print(f"refusing: {exc}", file=sys.stderr)
            return 2
    import s5p_nullexp
    try:
        with install(level, truth), esp.pvl_truth():
            return s5p_nullexp.main(rest)
    except Refused as e:
        print(f"refusing: {e}", file=sys.stderr)
        return 2


# ------------------------------------------------------------------------------------------- the gate (§10.3)
def read_queue(path: Path) -> list[tuple[str, str, float]]:
    out = []
    for line in path.read_text().splitlines():
        if line and not line.startswith("#"):
            cols = line.split("\t")
            out.append((cols[0], cols[1], float(cols[2])))
    return out


def read_log(log: Path) -> dict[str, dict]:
    rec: dict[str, dict] = {}
    for p in log.glob("*.start"):
        rec.setdefault(p.stem, {})["start"] = float(p.read_text().split()[0])
    for p in log.glob("*.end"):
        rec.setdefault(p.stem, {})["end"] = float(p.read_text().split()[0])
    return rec


def level_of(tid: str) -> str:
    return tid.split("_")[1]


def measured_rates(rec: dict) -> dict[str, float]:
    """Per level, the mean lane seconds of its finished tasks (dry-run records included), one unfold per task."""
    acc: dict[str, list[float]] = {}
    for tid, r in rec.items():
        if "start" in r and "end" in r and tid.startswith("prr_") and level_of(tid) in LEVELS:
            acc.setdefault(level_of(tid), []).append(r["end"] - r["start"])
    return {lv: sum(v) / len(v) for lv, v in acc.items()}


def project(now: float, t0: float, queue, rec: dict, lanes: int = LANES, unit_s: float = UNIT_S) -> dict:
    """The job's charge so far plus its projected remainder, on one node. A level's rate is its measured mean; an
    unmeasured level is priced at ``unit_s`` x its assumed units (the dry job only: a full job refuses one)."""
    rates = measured_rates(rec)
    busy, waiting, unmeasured = [], [], set()
    for tid, lv, u in queue:
        r = rec.get(tid, {})
        if "end" in r:
            continue
        if lv in rates:
            est = rates[lv]
        else:
            est = u * unit_s
            unmeasured.add(lv)
        if "start" in r:
            busy.append(max(0.0, est - (now - r["start"])))
        else:
            waiting.append(est)
    elapsed = max(0.0, now - t0)
    wall_left = pack(waiting, lanes, busy)
    return {"charged_h": elapsed / 3600, "projected_h": (elapsed + wall_left) / 3600,
            "rates_s": {k: round(v, 3) for k, v in sorted(rates.items())}, "unmeasured": sorted(unmeasured)}


def gate(task: str, queue_path: Path, log: Path, t0: float, limit_h: float, mode: str, now: float | None = None) -> int:
    """0: start the task (its start is recorded). 4: it already ended: skip it. 3: stop; nothing further starts
    (log/STOP holds why)."""
    now = time.time() if now is None else now
    stop = log / "STOP"
    if stop.exists():
        return 3
    if (log / f"{task}.end").exists():
        return 4
    queue = read_queue(queue_path)
    if task not in {t for t, _, _ in queue}:
        stop.write_text(json.dumps({"reason": f"task {task} is not in the queue"}) + "\n")
        return 3
    p = project(now, t0, queue, read_log(log))
    why = None
    if mode == "full" and p["unmeasured"]:
        why = f"levels {p['unmeasured']} have no rate from the dry run: nothing starts on an assumed rate"
    elif p["projected_h"] > GATE_FRACTION * limit_h:
        why = (f"projected {p['projected_h']:.2f} h exceeds {GATE_FRACTION} x the job's --time {limit_h} h: stopped "
               f"before this launch; reprice to the director with the measured rates")
    if why:
        stop.write_text(json.dumps({"reason": why, "task": task, **p}, indent=1) + "\n")
        return 3
    tmp = log / f"{task}.start.tmp"
    tmp.write_text(f"{now}\n")
    tmp.replace(log / f"{task}.start")
    return 0


# ------------------------------------------------------------------------------------------- staging (noatime + stat)
def _ref_g1():
    p = str(ND / "ref_g1")
    if p not in sys.path:
        sys.path.insert(0, p)
    import ref_g1
    return ref_g1


def stat_record(path: Path) -> dict:
    st = os.stat(path)
    return {"size": st.st_size, "mtime_ns": st.st_mtime_ns, "atime_ns": st.st_atime_ns, "ino": st.st_ino}


def stage(manifest: list[dict], dest: Path) -> dict:
    """Each entry {role, src, sha256, name}: stat the source, copy it once through O_NOATIME into ``dest``/name (the
    copy's digest taken in the same pass, refused unless it is the pin), stat it again. Refuses if the source's atime,
    mtime, size or inode moved. ``dest`` must not exist."""
    R = _ref_g1()
    try:
        dest.mkdir(parents=True)
    except FileExistsError:
        raise Refused(f"{dest} exists: inputs are staged into a new directory") from None
    out = []
    for e in manifest:
        src, target = Path(e["src"]), dest / e["name"]
        target.parent.mkdir(parents=True, exist_ok=True)
        before = stat_record(src)
        try:
            got = R.copy_noatime(src, target)
        except R.GateFailure as exc:
            raise Refused(str(exc)) from None
        after = stat_record(src)
        if got != e["sha256"]:
            raise Refused(f"{e['role']}: {src} digest {got[:12]}... is not its pin {e['sha256'][:12]}...")
        moved = [k for k in before if before[k] != after[k]]
        if moved:
            raise Refused(f"{e['role']}: {src} {moved} moved while it was copied")
        out.append({**e, "copy": str(target), "stat_before": before, "stat_after": after})
    return {"schema": "prr-stage/1", "dest": str(dest), "files": out}


def verify_stage(rec: dict) -> None:
    """Every staged copy still carries its pin (a full job checks before its queue starts)."""
    for e in rec["files"]:
        if sha256_path(Path(e["copy"])) != e["sha256"]:
            raise Refused(f"the staged copy {e['copy']} no longer carries its pin")


# ------------------------------------------------------------------------------------------- C-PAIR and C-MASK
FD_STAB_CONTROL = {  # FD-STAB's control closures at split 991000 (fd/receipts-stab-a1r/{dry,full}/SHA256SUMS)
    "nominal": "3753f4149fdcda5b7a67fad0eddb5b783e4642636d1574849743b9eb733f6cf4",
    "A7_gibuu": "b4d2ba5c34199352f90aab36b3a3c1cc9ad55c3cab79b375eb2c398746435179",
}


FD_STAB_OUT = "/pscratch/sd/j/josephrb/fd-stab-a1r-20261104"
SOURCES = [  # every shared file the study reads, staged once (``stage``); pins from the committed listings cited
    {"role": "of_inputs_5d", "src": "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz",
     "sha256": "07fccc1abc7204bc29349b4ba96850986fe91e909e83fc54e8d1a6b3922a649f", "name": "of_inputs_5d.npz"},
    {"role": "bkg_dump", "src": "/pscratch/sd/j/josephrb/s5c-20260924/runs/p2/bkg_dump.npz",
     "sha256": "2addac8f26055c5ed69862e7afe29e12ac51dbe23a8d6eeed79d71bec9d82955", "name": "bkg_dump.npz"},
    {"role": "bank_cv", "src": "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/bank_sweep_5d_bkgaware/cv.npz",
     "sha256": "072643e1e86ed0f359fa2dc94b87eebe5c9437615c05df5fbeb65e7d89ce9e3b", "name": "bank/cv.npz"},
    {"role": "closure_ratio_nuwro", "src": "/pscratch/sd/j/josephrb/pv-ladder-20261024/prep/ratios/L-5D-PV/nuwro.json",
     "sha256": "38e47eb6b6ac63f6657022ae0cc5a2b5eaffc6a2e503735ce7222275771fea6e",
     "name": "pvl/prep/ratios/L-5D-PV/nuwro.json"},
] + [{"role": f"fd_stab_control_{t}", "src": f"{FD_STAB_OUT}/runs/control/closure/{t}/stab_control_{t}_s991000.npz",
      "sha256": pin, "name": f"fd-stab/stab_control_{t}_s991000.npz"} for t, pin in FD_STAB_CONTROL.items()]


def staged_paths(stage_dir: Path, runs: Path, out: Path | None = None):
    """The runner's input arguments, all pointing into the stage directory (the bank directory holds only cv.npz:
    under --no-nuisance the runner reads nothing else from it, and no detector band is drawn)."""
    import types
    pin = {e["role"]: e["sha256"] for e in SOURCES}
    return types.SimpleNamespace(npz=stage_dir / "of_inputs_5d.npz", bkg=stage_dir / "bkg_dump.npz",
                                 bank=stage_dir / "bank", detector_dir=stage_dir / "no-detector-band-is-drawn",
                                 expect_npz_sha256=pin["of_inputs_5d"], expect_bkg_sha256=pin["bkg_dump"],
                                 closure_ratio_dir=stage_dir / "pvl", runs=runs, out=out)


def product_path(runs: Path, level: str, truth: str, seed: int) -> Path:
    return runs / level / truth / f"prr_{level}_{truth}_s{seed}.npz"


def load_xsec(path: Path) -> np.ndarray:
    with np.load(path, allow_pickle=False) as z:
        return np.asarray(z["xsec_flat"])


def pair(stage_rec: dict, runs: Path) -> dict:
    """C-PAIR: B0's unfolded array at split 991000 equals FD-STAB's control closure bitwise at the nominal truth and at
    A7 GiBUU (their staged copies, each carrying its pin). C-MASK: the five-column mask equals B0 bitwise at the
    nominal truth."""
    copies = {e["role"]: Path(e["copy"]) for e in stage_rec["files"]}
    out = {"C-PAIR": {}, "C-MASK": {}}
    for t, pin in FD_STAB_CONTROL.items():
        ref = copies.get(f"fd_stab_control_{t}")
        if ref is None or sha256_path(ref) != pin:
            out["C-PAIR"][t] = {"pass": False, "why": "the staged FD-STAB product is missing or not its pin"}
            continue
        ours = product_path(runs, "B0", t, PRIMARY_SEED)
        a, b = load_xsec(ours), load_xsec(ref)
        out["C-PAIR"][t] = {"pass": bool(a.dtype == b.dtype and np.array_equal(a, b)), "cells": int(b.size),
                            "cells_differing": int(np.sum(a != b)) if a.shape == b.shape else None}
    a = load_xsec(product_path(runs, "B0", "nominal", PRIMARY_SEED))
    b = load_xsec(product_path(runs, "O5", "nominal", PRIMARY_SEED))
    out["C-MASK"]["nominal"] = {"pass": bool(a.dtype == b.dtype and np.array_equal(a, b))}
    out["pass"] = all(v["pass"] for blk in ("C-PAIR", "C-MASK") for v in out[blk].values())
    return out


# ------------------------------------------------------------------------------------------- main
def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd, rest = (argv[0], argv[1:]) if argv else ("", [])
    if cmd == "run":
        if "--" not in rest:
            print("usage: prr_probe.py run --level L --truth T -- <s5p_nullexp arguments>", file=sys.stderr)
            return 2
        i = rest.index("--")
        ap = argparse.ArgumentParser(prog="prr_probe.py run", allow_abbrev=False)
        ap.add_argument("--level", choices=sorted(LEVELS), required=True)
        ap.add_argument("--truth", choices=TRUTHS, required=True)
        a = ap.parse_args(rest[:i])
        return run(a.level, a.truth, rest[i + 1:])
    if cmd == "tasks":
        ap = argparse.ArgumentParser(prog="prr_probe.py tasks", allow_abbrev=False)
        for opt in ("--out", "--stage-dir", "--runs"):
            ap.add_argument(opt, type=Path, required=True)
        a = ap.parse_args(rest)
        a = staged_paths(a.stage_dir, a.runs, a.out)
        a.out.mkdir(parents=True, exist_ok=True)
        counts = {}
        for j in JOBS:
            lines = queue_lines(a, j)
            (a.out / f"{j}.tsv").write_text("\n".join(lines) + "\n")
            counts[j] = len(lines) - 1
        print(json.dumps({"tasks": counts, "out": str(a.out)}))
        return 0
    if cmd == "manifest":
        ap = argparse.ArgumentParser(prog="prr_probe.py manifest", allow_abbrev=False)
        ap.add_argument("--out", type=Path, required=True)
        a = ap.parse_args(rest)
        a.out.write_text(json.dumps(SOURCES, indent=1) + "\n")
        return 0
    if cmd == "gate":
        ap = argparse.ArgumentParser(prog="prr_probe.py gate", allow_abbrev=False)
        ap.add_argument("--task", required=True)
        ap.add_argument("--queue", type=Path, required=True)
        ap.add_argument("--log", type=Path, required=True)
        ap.add_argument("--t0", type=float, required=True)
        ap.add_argument("--limit-h", type=float, required=True)
        ap.add_argument("--mode", choices=("dry", "full"), required=True)
        a = ap.parse_args(rest)
        return gate(a.task, a.queue, a.log, a.t0, a.limit_h, a.mode)
    if cmd in ("stage", "verify-stage", "pair"):
        ap = argparse.ArgumentParser(prog=f"prr_probe.py {cmd}", allow_abbrev=False)
        if cmd == "stage":
            for opt in ("--manifest", "--dest", "--out"):
                ap.add_argument(opt, type=Path, required=True)
        else:
            ap.add_argument("--stage", type=Path, required=True)
            if cmd == "pair":
                ap.add_argument("--runs", type=Path, required=True)
                ap.add_argument("--out", type=Path, required=True)
        a = ap.parse_args(rest)
        try:
            if cmd == "stage":
                rec = stage(json.loads(a.manifest.read_text()), a.dest)
                a.out.write_text(json.dumps(rec, indent=1) + "\n")
                print(json.dumps({"staged": len(rec["files"])}))
                return 0
            rec = json.loads(a.stage.read_text())
            verify_stage(rec)
            if cmd == "verify-stage":
                return 0
            res = pair(rec, a.runs)
        except (Refused, OSError, KeyError) as e:
            print(f"refusing: {e}", file=sys.stderr)
            return 2
        a.out.write_text(json.dumps(res, indent=1) + "\n")
        print(json.dumps({"pass": res["pass"]}))
        return 0 if res["pass"] else 1
    if cmd == "price":
        print(json.dumps(price(), indent=1))
        return 0
    if cmd == "limit":  # the declared --time of a job, as Slurm reads it (H:MM:SS), for the job script
        h = JOB_LIMIT_H[rest[0]]
        print(f"{int(h)}:{int(round((h - int(h)) * 60)):02d}:00")
        return 0
    print("usage: prr_probe.py {run,manifest,tasks,gate,stage,verify-stage,pair,price,limit} ...", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
