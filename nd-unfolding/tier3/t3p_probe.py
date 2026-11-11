#!/usr/bin/env python3
"""T3 probe: the tasks, the queues, one traced run of one arm, staging, C-PAIR and the gate.

Declaration: ``docs/orchestration/state/measurement-paper/5d-community-20261024/fd/tier3-20261110/
T3-PIPELINE-TESTS-DECLARATION.md`` rev 2 (§3 the design, §6 the controls, §9 the price and jobs).

One task is FD-PRR's own queue line for (K50, truth, seed) through ``s5p_nullexp.main``, unchanged, with three
fields set for the arm: ``--iters`` (50, or 2 for OP), ``--tag`` and ``--out``. For that one invocation it rebinds,
and restores on exit:
* ``argparse.ArgumentParser.parse_args``: the namespace check on the runner's own parse (``check_namespace``);
* ``s5n_pseudo.build_pseudo``: SO's ``no_background=True``, and the capture of r on the unfolding half;
* ``s5p_numerics.unfold_one``: the arm's traced unfold (``t3p_arms.traced_unfold_arm``) on ``unfold_one``'s own
  inputs (``s5e_trace.measured_side``, ``s5e_trace.unf_inputs``);
* ``s5p_truths.load_fine_rho``: the staged copy of a fine-ratio rho array, by its sha256 (FD-PRR Addendum A4's rule);
* ``s5n_pseudo.write_product``: the trace arrays and the ``tier3`` block, refused unless every step above happened
  exactly once.

MEASURES: the declared products. CANNOT AUTHORIZE: a reading (``t3p_read``), an estimator change, or a run outside
the bound jobs.
"""
from __future__ import annotations

import argparse
import functools
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
for _p in (HERE, ND, ND / "pv-ladder", ND / "prior_retention"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
import prr_probe as P  # noqa: E402  (FD-PRR's bound probe: pins, columns, closures, argv, packing, staging)
import t3p_arms as A  # noqa: E402

SCHEMA = "t3-pipeline-tests/1"
Refused = P.Refused
sha256_path = P.sha256_path

# C-PINS: FD-PRR's fifteen bound modules, and FD-PRR's probe itself, which this module imports
CODE_PINS = {**P.CODE_PINS,
             "nd-unfolding/prior_retention/prr_probe.py": "f87ee90c58d2b8904fe881931edc61966a6adda8be7eb503da6644797a3d1232"}

TRUTHS = ("A7_gibuu", "q3")  # the two flagged truths (§3.2)
PRIOR = "nominal"
PRIMARY_SEED = P.PRIMARY_SEED  # 991000
FLOOR_SEEDS = P.FLOOR_SEEDS  # 994001-994004
FLOOR_TRUTH = "A7_gibuu"
BASE_LEVEL = "K50"  # the FD-PRR queue line each task starts from
PRR_OUT = "/pscratch/sd/j/josephrb/fd-prr-20261108"  # FD-PRR's run directory (its receipts' SHA256SUMS name runs/ in it)
PRR_RECEIPTS = REPO / "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-prr"


def task_id(arm: str, truth: str, seed: int) -> str:
    return f"t3p_{arm}_{truth}_s{seed}"


def all_tasks() -> list[tuple[str, str, int]]:
    """36 tasks: six arms at both flagged truths on the primary split, and at A7 GiBUU on the four floor splits."""
    out = [(arm, t, PRIMARY_SEED) for t in TRUTHS for arm in A.ARMS]
    out += [(arm, FLOOR_TRUTH, s) for s in FLOOR_SEEDS for arm in A.ARMS]
    return out


def job_of(arm: str, truth: str, seed: int) -> str:
    if seed == PRIMARY_SEED:
        return "dry" if truth == FLOOR_TRUTH else "q3"
    return "floor"


JOBS = ("dry", "q3", "floor")
LANES = P.LANES
GATE_FRACTION = P.GATE_FRACTION
DRY_ALLOWANCE_H = 0.25  # staging and C-PAIR before and after the dry queue (not projected)
# §9.1: 1.25 x FD-PRR's measured K = 50 maximum 3,822 s x 1.25 (the tracer's unmeasured overhead), rounded up; OP from
# FD-PRR's K = 2 maximum 339 s the same way
TASK_S = {50: 6000.0, 2: 600.0}
JOB_LIMIT_H = {"dry": 2.25, "q3": 2.0, "floor": 5.75}
CAP_NODE_H = 10.0


def task_seconds(arm: str) -> float:
    return TASK_S[A.ITERS[arm]]


def ordered(tasks):
    return sorted(tasks, key=lambda x: (-task_seconds(x[0]), task_id(*x)))


def price(task_s: dict | None = None) -> dict:
    """Per job: the packed lane wall at the conservative task seconds and the least --time the gate's 0.9 rule passes
    with, rounded up to a quarter hour (the dry job adds its unprojected steps)."""
    out = {}
    for j in JOBS:
        tasks = ordered([t for t in all_tasks() if job_of(*t) == j])
        secs = [(task_s or TASK_S)[A.ITERS[t[0]]] for t in tasks]
        wall = P.pack(secs)
        need = wall / 3600 / GATE_FRACTION + (DRY_ALLOWANCE_H if j == "dry" else 0.0)
        out[j] = {"tasks": len(tasks), "lane_s": sum(secs), "wall_h": wall / 3600,
                  "least_limit_h": math.ceil(need * 4 - 1e-9) / 4, "limit_h": JOB_LIMIT_H[j]}
    return out


# ------------------------------------------------------------------------------------------- the queue lines
def product_path(runs: Path, arm: str, truth: str, seed: int) -> Path:
    return Path(runs) / arm / truth / f"{task_id(arm, truth, seed)}.npz"


def _set(argv: list[str], opt: str, value: str) -> None:
    if argv.count(opt) != 1:
        raise ValueError(f"FD-PRR's line carries {opt} {argv.count(opt)} times")
    argv[argv.index(opt) + 1] = value


def runner_argv(a, arm: str, truth: str, seed: int) -> list[str]:
    """FD-PRR's K50 line for (truth, seed), with this arm's iterations, tag and output."""
    argv = P.runner_argv(a, BASE_LEVEL, truth, seed)
    _set(argv, "--iters", str(A.ITERS[arm]))
    _set(argv, "--tag", f"t3p_{arm}_{truth}")
    _set(argv, "--out", f"{a.runs}/{arm}/{truth}")
    return argv


def queue_lines(a, job: str) -> list[str]:
    """A job's queue: tab-separated id, arm, conservative seconds, script, argv (longest first)."""
    lines = [f"# T3 queue {job}: columns id, arm, seconds, script, argv (longest first)"]
    for arm, t, s in ordered([x for x in all_tasks() if job_of(*x) == job]):
        argv = ["run", "--arm", arm, "--truth", t, "--stage", str(a.stage_json), "--", *runner_argv(a, arm, t, s)]
        lines.append("\t".join([task_id(arm, t, s), arm, str(task_seconds(arm)), "tier3/t3p_probe.py", *argv]))
    return lines


# ------------------------------------------------------------------------------------------- the namespace check
def check_namespace(ns, arm: str, truth: str) -> str | None:
    """The refusal, decided on the runner's own parsed arguments (last value wins, abbreviations resolved)."""
    import s5e_trace
    if getattr(ns, "config", None) != "R":
        return "every arm is built on configuration (e): --config must be R"
    if not (getattr(ns, "expectation", False) and getattr(ns, "no_nuisance", False)):
        return "the pseudo-data are noise-free: --expectation and --no-nuisance are required"
    if getattr(ns, "iters", None) != A.ITERS[arm]:
        return f"arm {arm} runs {A.ITERS[arm]} iterations, not {getattr(ns, 'iters', None)}"
    if s5e_trace.parse_pair(getattr(ns, "capacity", None)) is not None:
        return "every arm keeps (e)'s capacity: no --capacity"
    if getattr(ns, "mc_fraction", None) != "half":
        return "every arm unfolds with MC half"
    seeds = getattr(ns, "pseudo_seeds", None) or ""
    a, _, b = seeds.partition(":")
    if not (a.isdigit() and a == b):
        return "one declared split per task: --pseudo-seeds S:S"
    if (arm, truth, int(a)) not in set(all_tasks()):
        return f"({arm}, {truth}, seed {a}) is not a declared task"
    if getattr(ns, "estimator_seed", None) != 42 or getattr(ns, "threads", None) != 32:
        return "the estimator seed is 42 and the thread count 32, as FD-PRR ran"
    if getattr(ns, "tag", None) != f"t3p_{arm}_{truth}":
        return f"the tag is t3p_{arm}_{truth}"
    name, hyp, alt, kind, amp = P.closure_spec(truth)
    if str(getattr(ns, "hypothesis", "")) != hyp:
        return f"truth {truth}'s hypothesis is {hyp}"
    got_alt = getattr(ns, "alternative", None)
    if (alt is None) != (got_alt is None):
        return f"truth {truth}'s alternative is {alt}"
    if alt is not None and float(getattr(ns, "alternative_amplitude", -1)) != float(amp):
        return f"truth {truth}'s amplitude is {amp}"
    return None


# ------------------------------------------------------------------------------------------- one run
def _restore(saved):
    for mod, name, val in saved:
        setattr(mod, name, val)


@contextmanager
def install(arm: str, truth: str, rho: dict | None, guard: bool = True, M16=None, fm=None):
    """Rebind, for one invocation, the parse, the build, the unfold, the rho loader and the writer (module doc).
    ``rho`` maps a fine-ratio rho array's sha256 to its staged copy; with None, any fine ratio is refused."""
    import s5n_pseudo
    import s5p_numerics
    import s5p_truths
    import s5c_pseudo
    import s5e_trace
    if arm not in A.ARMS or truth not in TRUTHS:
        raise ValueError(f"unknown arm or truth: {arm!r}, {truth!r}")
    state = {"checked": not guard, "columns": None, "builds": 0, "unfolds": 0, "r_A": None, "trace": None,
             "evidence": None, "so": None}
    here = {"t3p_probe.py": sha256_path(Path(__file__).resolve()),
            "t3p_arms.py": sha256_path(Path(A.__file__).resolve())}
    saved = [(argparse.ArgumentParser, "parse_args", argparse.ArgumentParser.parse_args),
             (s5n_pseudo, "build_pseudo", s5n_pseudo.build_pseudo), (s5p_numerics, "unfold_one", s5p_numerics.unfold_one),
             (s5p_truths, "load_fine_rho", s5p_truths.load_fine_rho), (s5n_pseudo, "write_product", s5n_pseudo.write_product)]
    orig_parse, orig_build, _, orig_rho, orig_write = (v for _, _, v in saved)

    def parse_args(self, args=None, namespace=None):
        ns = orig_parse(self, args, namespace)
        if hasattr(ns, "pseudo_seeds"):  # the runner's own parse (its prog is sys.argv[0], so not a usable key)
            why = check_namespace(ns, arm, truth)
            if why:
                print(f"refusing: {why}", file=sys.stderr)
                raise SystemExit(2)
            state["columns"] = list(P.check_columns(Path(ns.npz)))
            state["checked"] = True
        return ns

    def build_pseudo(inputs, bkg, truth_name, amplitude, split_key, pseudo_seed, ratio=None, **kw):
        if kw.get("no_background") or kw.get("prior_matches_truth"):
            raise Refused("the runner asked for a development option this study does not declare")
        kw = dict(kw, no_background=(arm == "SO"))
        exp, x_true, info = orig_build(inputs, bkg, truth_name, amplitude, split_key, pseudo_seed, ratio, **kw)
        r = np.asarray(s5n_pseudo.truth_weight(truth_name, inputs, amplitude, ratio), float)
        is_b = s5c_pseudo.half_mask(inputs["MCgen"].shape[0], split_key)
        state["r_A"] = r[~is_b]
        state["builds"] += 1
        state["so"] = {"no_background": arm == "SO", "template_rows": int(len(exp["tmpl_w"])),
                       "pseudo_background_events": float(info["pseudo_background_events"])}
        return exp, x_true, info

    def unfold_one(exp, dtype, estimator_seed, threads, iters, unfold_fn=None):
        if unfold_fn is not None:
            raise Refused("unfold_one was given an unfold function: the arm's traced unfold is the only one")
        if state["r_A"] is None or len(state["r_A"]) != len(exp["MCgen"]):
            raise Refused("r was not captured on the unfolding half")
        feat, w_ref, ev = s5e_trace.measured_side(exp, estimator_seed, threads, None, dtype)
        unf_in = s5e_trace.unf_inputs(exp, feat, w_ref)
        m16 = M16 if M16 is not None else _cell_matrix()
        fmap = fm if fm is not None else _fine_map()
        rec = A.ArmRecorder(unf_in, state["r_A"], m16, fmap, iters)
        xs, params, tracer = A.traced_unfold_arm(unf_in, rec, estimator_seed, threads, iters, arm, state["r_A"])
        state["trace"] = rec.arrays(tracer)
        state["evidence"] = tracer.evidence
        state["unfolds"] += 1
        return xs, {"refinement": ev, "estimator_params": params}

    def load_fine_rho(ratio):
        sha = ratio["rho_npz"]["sha256"]
        if not rho or sha not in rho:
            raise Refused(f"{ratio['rho_npz']['path']}: no staged copy carries its sha256")
        return orig_rho({**ratio, "rho_npz": {**ratio["rho_npz"], "path": str(rho[sha])}})

    def write_product(out, arrays, meta):
        if not state["checked"]:
            raise RuntimeError("refusing to write: the runner's arguments were never checked")
        if state["builds"] != 1 or state["unfolds"] != 1 or state["trace"] is None:
            raise RuntimeError(f"refusing to write: {state['builds']} builds, {state['unfolds']} unfolds")
        ref = meta.get("refinement") or {}
        if arm == "SO" and (ref.get("ran") is not False or state["so"]["template_rows"] != 0
                            or state["so"]["pseudo_background_events"] != 0):
            raise RuntimeError("refusing to write: C-ARM SO: the refinement ran or background is present")
        if arm != "SO" and ref.get("ran") is False:
            raise RuntimeError("refusing to write: the refinement did not run on background-inclusive pseudo-data")
        block = {"schema": SCHEMA, "arm": arm, "truth": truth, "iters": A.ITERS[arm], "evidence": state["evidence"],
                 "so": state["so"], "input_columns": state["columns"], "code_sha256": here}
        state["builds"] = state["unfolds"] = 0
        return orig_write(out, {**arrays, **state["trace"]}, {**meta, "tier3": block})

    argparse.ArgumentParser.parse_args = parse_args
    s5n_pseudo.build_pseudo = build_pseudo
    s5p_numerics.unfold_one = unfold_one
    s5p_truths.load_fine_rho = load_fine_rho
    s5n_pseudo.write_product = write_product
    try:
        yield state
    finally:
        _restore(saved)


def _h2_definition() -> Path:
    return ND / "pv-ladder/readouts/h2_definition.json"


def _cell_matrix():
    import estimator_stability_analyze as an
    return an.cell_matrix(str(_h2_definition()))


def _fine_map():
    import s1_assemble
    return s1_assemble.fine_map(_h2_definition())


def run(arm: str, truth: str, stage_json: Path, rest: list[str]) -> int:
    try:
        P.check_pins(CODE_PINS)
    except Refused as e:
        print(f"refusing: {e}", file=sys.stderr)
        return 2
    why = P.refuse_argv(rest)
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
    try:
        rho = rho_copies(json.loads(Path(stage_json).read_text()))
    except (OSError, KeyError, ValueError, Refused) as e:
        print(f"refusing: the stage record: {e}", file=sys.stderr)
        return 2
    import s5p_nullexp
    try:
        with install(arm, truth, rho), esp.pvl_truth():
            return s5p_nullexp.main(rest)
    except Refused as e:
        print(f"refusing: {e}", file=sys.stderr)
        return 2


# ------------------------------------------------------------------------------------------- staging (§9.4)
FINE_SCHEMA = "s5p-fine-ratio/1"
PRR_LEVEL_AT_K = {5: "B0", 10: "K10", 20: "K20", 50: "K50"}


def pair_refs() -> list[tuple[str, str, int, int | None]]:
    """(FD-PRR level, truth, seed, k) of every FD-PRR product C-PAIR and C-P read: B0's trace at k against FD-PRR's
    level at K = k (16), and the nominal truth at each split for P (5, k None)."""
    out = [(PRR_LEVEL_AT_K[k], t, PRIMARY_SEED, k) for t in TRUTHS for k in A.PAIR_KS]
    out += [(PRR_LEVEL_AT_K[k], FLOOR_TRUTH, s, k) for s in FLOOR_SEEDS for k in (5, 20)]
    out += [("B0", PRIOR, s, None) for s in (PRIMARY_SEED, *FLOOR_SEEDS)]
    return out


def prr_digests(receipts: Path = PRR_RECEIPTS) -> dict[str, str]:
    """Every FD-PRR product digest in its four jobs' committed SHA256SUMS, by its path under runs/; refuses if two
    listings disagree on one path."""
    out: dict[str, str] = {}
    files = sorted(receipts.glob("*/cluster/log-*/SHA256SUMS"))
    if len(files) != 4:
        raise Refused(f"expected FD-PRR's four SHA256SUMS, found {len(files)}")
    for f in files:
        for line in f.read_text().splitlines():
            if not line.strip():
                continue
            sha, path = line.split(None, 1)
            path = path.strip()
            if out.get(path, sha) != sha:
                raise Refused(f"FD-PRR's listings disagree on {path}")
            out[path] = sha
    return out


def prr_rel(level: str, truth: str, seed: int) -> str:
    return f"runs/{level}/{truth}/prr_{level}_{truth}_s{seed}.npz"


def prr_name(level: str, truth: str, seed: int) -> str:
    return f"fd-prr/{prr_rel(level, truth, seed)}"


def sources(repo: Path = REPO) -> list[dict]:
    """Every shared file the study reads, staged once: FD-PRR's four inputs with FD-PRR's pins, the fine-ratio rho
    arrays the two truths' hypotheses name (with the committed json's sha256), and the 21 FD-PRR products C-PAIR and
    C-P read (with the committed digests)."""
    base = [e for e in P.SOURCES if not e["role"].startswith("fd_stab_control_")]
    rho = {}
    for t in TRUTHS:
        hyp = json.loads((repo / P.closure_spec(t)[1]).read_text())
        if hyp.get("schema") == FINE_SCHEMA:
            src = hyp["rho_npz"]["path"]
            rho[src] = {"role": "rho_" + Path(src).stem.replace("rho-", "", 1), "src": src, "sha256": hyp["rho_npz"]["sha256"],
                        "name": f"s5p-nullsF/{Path(src).name}"}
    dig = prr_digests(repo / PRR_RECEIPTS.relative_to(REPO))
    prr = {}
    for lv, t, s, _ in pair_refs():
        rel = prr_rel(lv, t, s)
        if rel not in dig:
            raise Refused(f"FD-PRR's listings carry no digest for {rel}")
        prr[rel] = {"role": f"prr_{lv}_{t}_s{s}", "src": f"{PRR_OUT}/{rel}", "sha256": dig[rel],
                    "name": prr_name(lv, t, s)}
    return base + list(rho.values()) + list(prr.values())


def rho_copies(stage_rec: dict) -> dict[str, Path]:
    """The staged rho arrays by sha256 (every entry whose role starts with rho_), each under the stage directory."""
    root = Path(stage_rec["dest"]).resolve()
    out = {}
    for e in stage_rec["files"]:
        if e["role"].startswith("rho_"):
            if root not in Path(e["copy"]).resolve().parents:
                raise Refused(f"{e['copy']} is not under the stage directory")
            out[e["sha256"]] = Path(e["copy"])
    return out


def staged_paths(stage_dir: Path, runs: Path, out: Path | None = None, stage_json: Path | None = None):
    a = P.staged_paths(stage_dir, runs, out)
    a.stage_json = stage_json if stage_json is not None else Path(stage_dir).parent / "stage.json"
    return a


# ------------------------------------------------------------------------------------------- C-PAIR, C-X (§6)
def _load(path: Path, key: str) -> np.ndarray:
    with np.load(path, allow_pickle=False) as z:
        return np.asarray(z[key])


def same(a: np.ndarray, b: np.ndarray) -> dict:
    """Bitwise: the same dtype, shape and bytes (as LL5D A1b.1). Value equality would pass -0.0 against +0.0."""
    if a.dtype != b.dtype or a.shape != b.shape:
        return {"pass": False, "cells": int(b.size), "cells_differing": None}
    ab, bb = (np.ascontiguousarray(x).reshape(-1).view(np.uint8).reshape(x.size, x.itemsize) for x in (a, b))
    return {"pass": bool(a.tobytes() == b.tobytes()), "cells": int(b.size),
            "cells_differing": int(np.any(ab != bb, axis=1).sum())}


def pair(stage_rec: dict, runs: Path, job: str) -> dict:
    """C-PAIR for one job: B0's unfold at each k equals FD-PRR's product at K = k bitwise (its staged copy, carrying
    its pin). C-X: every arm's truth equals FD-PRR's B0 truth at the same truth and split bitwise."""
    copies = {e["role"]: (Path(e["copy"]), e["sha256"]) for e in stage_rec["files"]}
    out = {"job": job, "C-PAIR": {}, "C-X": {}}
    for lv, t, s, k in pair_refs():
        if k is None or job_of("B0", t, s) != job:
            continue
        key = f"{t}/s{s}/k{k}"
        ref, pin = copies.get(f"prr_{lv}_{t}_s{s}", (None, None))
        if ref is None or sha256_path(ref) != pin:
            out["C-PAIR"][key] = {"pass": False, "why": "the staged FD-PRR product is missing or not its pin"}
            continue
        ours = product_path(runs, "B0", t, s)
        out["C-PAIR"][key] = same(_load(ours, f"xs_k{k}"), _load(ref, "xsec_flat"))
    for arm, t, s in all_tasks():
        if job_of(arm, t, s) != job:
            continue
        ref, pin = copies.get(f"prr_B0_{t}_s{s}", (None, None))
        if ref is None or sha256_path(ref) != pin:
            out["C-X"][task_id(arm, t, s)] = {"pass": False, "why": "the staged FD-PRR product is missing or not its pin"}
            continue
        out["C-X"][task_id(arm, t, s)] = same(_load(product_path(runs, arm, t, s), "xtrue_flat"), _load(ref, "xtrue_flat"))
    out["pass"] = bool(out["C-PAIR"]) and all(v["pass"] for blk in ("C-PAIR", "C-X") for v in out[blk].values())
    return out


# ------------------------------------------------------------------------------------------- the gate (§9.3)
def arm_of(tid: str) -> str:
    return tid.split("_")[1]


def measured_rates(rec: dict) -> dict[str, float]:
    acc: dict[str, list[float]] = {}
    for tid, r in rec.items():
        if "start" in r and "end" in r and tid.startswith("t3p_") and arm_of(tid) in A.ARMS:
            acc.setdefault(arm_of(tid), []).append(r["end"] - r["start"])
    return {a: sum(v) / len(v) for a, v in acc.items()}


def project(now: float, t0: float, queue, rec: dict, lanes: int = LANES) -> dict:
    """The job's charge so far plus its projected remainder, on one node: an arm's rate is its measured mean, an
    unmeasured arm is priced at its queue seconds (the dry job only: a full job refuses one)."""
    rates = measured_rates(rec)
    busy, waiting, unmeasured = [], [], set()
    for tid, arm, secs in queue:
        r = rec.get(tid, {})
        if "end" in r:
            continue
        est = rates.get(arm)
        if est is None:
            est = secs
            unmeasured.add(arm)
        if "start" in r:
            busy.append(max(0.0, est - (now - r["start"])))
        else:
            waiting.append(est)
    elapsed = max(0.0, now - t0)
    wall_left = P.pack(waiting, lanes, busy)
    return {"charged_h": elapsed / 3600, "projected_h": (elapsed + wall_left) / 3600,
            "rates_s": {k: round(v, 3) for k, v in sorted(rates.items())}, "unmeasured": sorted(unmeasured)}


def gate(task: str, queue_path: Path, log: Path, t0: float, limit_h: float, mode: str, now: float | None = None) -> int:
    """0: start the task (its start is recorded). 4: it already ended: skip it. 3: stop; nothing further starts."""
    now = time.time() if now is None else now
    stop = log / "STOP"
    if stop.exists():
        return 3
    if (log / f"{task}.end").exists():
        return 4
    queue = P.read_queue(queue_path)
    if task not in {t for t, _, _ in queue}:
        stop.write_text(json.dumps({"reason": f"task {task} is not in the queue"}) + "\n")
        return 3
    p = project(now, t0, queue, P.read_log(log))
    why = None
    if mode == "full" and p["unmeasured"]:
        why = f"arms {p['unmeasured']} have no rate from the dry run: nothing starts on an assumed rate"
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


# ------------------------------------------------------------------------------------------- main
def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd, rest = (argv[0], argv[1:]) if argv else ("", [])
    if cmd == "run":
        if "--" not in rest:
            print("usage: t3p_probe.py run --arm A --truth T --stage STAGE_JSON -- <s5p_nullexp arguments>", file=sys.stderr)
            return 2
        i = rest.index("--")
        ap = argparse.ArgumentParser(prog="t3p_probe.py run", allow_abbrev=False)
        ap.add_argument("--arm", choices=A.ARMS, required=True)
        ap.add_argument("--truth", choices=TRUTHS, required=True)
        ap.add_argument("--stage", type=Path, required=True)
        a = ap.parse_args(rest[:i])
        return run(a.arm, a.truth, a.stage, rest[i + 1:])
    if cmd == "tasks":
        ap = argparse.ArgumentParser(prog="t3p_probe.py tasks", allow_abbrev=False)
        for opt in ("--out", "--stage-dir", "--runs", "--stage-json"):
            ap.add_argument(opt, type=Path, required=True)
        a = ap.parse_args(rest)
        ns = staged_paths(a.stage_dir, a.runs, a.out, a.stage_json)
        a.out.mkdir(parents=True, exist_ok=True)
        counts = {}
        for j in JOBS:
            lines = queue_lines(ns, j)
            (a.out / f"{j}.tsv").write_text("\n".join(lines) + "\n")
            counts[j] = len(lines) - 1
        print(json.dumps({"tasks": counts, "out": str(a.out)}))
        return 0
    if cmd == "manifest":
        ap = argparse.ArgumentParser(prog="t3p_probe.py manifest", allow_abbrev=False)
        ap.add_argument("--out", type=Path, required=True)
        a = ap.parse_args(rest)
        a.out.write_text(json.dumps(sources(), indent=1) + "\n")
        return 0
    if cmd == "gate":
        ap = argparse.ArgumentParser(prog="t3p_probe.py gate", allow_abbrev=False)
        ap.add_argument("--task", required=True)
        ap.add_argument("--queue", type=Path, required=True)
        ap.add_argument("--log", type=Path, required=True)
        ap.add_argument("--t0", type=float, required=True)
        ap.add_argument("--limit-h", type=float, required=True)
        ap.add_argument("--mode", choices=("dry", "full"), required=True)
        a = ap.parse_args(rest)
        return gate(a.task, a.queue, a.log, a.t0, a.limit_h, a.mode)
    if cmd in ("stage", "verify-stage", "pair"):
        ap = argparse.ArgumentParser(prog=f"t3p_probe.py {cmd}", allow_abbrev=False)
        if cmd == "stage":
            for opt in ("--manifest", "--dest", "--out"):
                ap.add_argument(opt, type=Path, required=True)
        else:
            ap.add_argument("--stage", type=Path, required=True)
            if cmd == "pair":
                ap.add_argument("--runs", type=Path, required=True)
                ap.add_argument("--job", choices=JOBS, required=True)
                ap.add_argument("--out", type=Path, required=True)
        a = ap.parse_args(rest)
        try:
            if cmd == "stage":
                rec = P.stage(json.loads(a.manifest.read_text()), a.dest)
                a.out.write_text(json.dumps(rec, indent=1) + "\n")
                print(json.dumps({"staged": len(rec["files"])}))
                return 0
            rec = json.loads(a.stage.read_text())
            P.verify_stage(rec)
            if cmd == "verify-stage":
                return 0
            res = pair(rec, a.runs, a.job)
        except (Refused, OSError, KeyError) as e:
            print(f"refusing: {e}", file=sys.stderr)
            return 2
        a.out.write_text(json.dumps(res, indent=1) + "\n")
        print(json.dumps({"pass": res["pass"]}))
        return 0 if res["pass"] else 1
    if cmd == "price":
        print(json.dumps(price(), indent=1))
        return 0
    if cmd == "limit":
        if not rest or rest[0] not in JOB_LIMIT_H:
            print("usage: t3p_probe.py limit {dry,q3,floor}", file=sys.stderr)
            return 2
        h = JOB_LIMIT_H[rest[0]]
        print(f"{int(h)}:{int(round((h - int(h)) * 60)):02d}:00")
        return 0
    print("usage: t3p_probe.py {run,manifest,tasks,gate,stage,verify-stage,pair,price,limit} ...", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
