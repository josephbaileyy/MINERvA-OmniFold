#!/usr/bin/env python3
"""S2R probe: the six tasks, one traced run of one arm, staging, C-PAIR / C-X / C-ONE, the gate and the price.

Declaration: ``docs/orchestration/state/measurement-paper/5d-community-20261024/fd/s2r-20261124/S2R-DECLARATION.md``.

Built on T3's probe (``tier3/t3p_probe.py``): one task is FD-PRR's own B0 queue line for (truth, 991000) through
``s5p_nullexp.main``, unchanged, with ``--iters``, ``--tag`` and ``--out`` set for the arm. For that one invocation it
rebinds, and restores on exit, the runner's parse (``check_namespace``), ``s5n_pseudo.build_pseudo`` (the capture of
r on the unfolding half; no development option), ``s5p_numerics.unfold_one`` (the arm's traced unfold),
``s5p_truths.load_fine_rho`` (the staged copy by sha256) and ``s5n_pseudo.write_product`` (refused unless every step
happened exactly once).

MEASURES: the declared products. CANNOT AUTHORIZE: an estimator change, or a run outside the bound job.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from contextlib import contextmanager
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ND = HERE.parent
REPO = ND.parent
for _p in (HERE, ND, ND / "tier3", ND / "pv-ladder", ND / "prior_retention"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
import prr_probe as P  # noqa: E402
import t3p_arms as TA  # noqa: E402
import t3p_probe as T  # noqa: E402
import s2r_arm as S  # noqa: E402

SCHEMA = "s2r-step2/1"
Refused = P.Refused
sha256_path = P.sha256_path

# C-PINS: FD-PRR's bound modules and probe, and T3's two modules this probe builds on (T3-BINDING-1 / addendum V1)
CODE_PINS = {**T.CODE_PINS,
             "nd-unfolding/tier3/t3p_arms.py": "4a685bde238dcc6dc25e9b1121029994f33becafab486cbec1a7bf846206bf84",
             "nd-unfolding/tier3/t3p_probe.py": "e27bf07a3e2c60320a749355eaedceed5a36574d2d8fa83675bd4b4721985bd2"}

TRUTHS = ("nominal", "A7_gibuu", "q3")
SEED = P.PRIMARY_SEED  # 991000: FD-PRR's and T3's primary split
LANES = 6
TASK_S = {"B0": 700.0, "S2R": 2100.0}  # 1.25 x (194 s + k x 72.6 s), FD-PRR's K = 2 and K = 50 maxima (339 s, 3,822 s)
JOB_LIMIT_H = 1.0
GATE_FRACTION = P.GATE_FRACTION
STAGE_ALLOWANCE_H = 0.25  # staging and the pair before and after the queue (T3's dry allowance)
CAP_NODE_H = JOB_LIMIT_H
PRR_OUT = T.PRR_OUT
JOB = "run"


def task_id(arm: str, truth: str, seed: int = SEED) -> str:
    return f"s2r_{arm}_{truth}_s{seed}"


def all_tasks() -> list[tuple[str, str, int]]:
    """Six tasks: B0 (k = 5) and S2R (traced to k = 20) at the nominal truth and the two flagged truths."""
    return [(arm, t, SEED) for t in TRUTHS for arm in S.ARMS]


def ordered(tasks):
    return sorted(tasks, key=lambda x: (-TASK_S[x[0]], task_id(*x)))


def price() -> dict:
    secs = [TASK_S[a] for a, _, _ in ordered(all_tasks())]
    wall = P.pack(secs, LANES)
    need = wall / 3600 / GATE_FRACTION + STAGE_ALLOWANCE_H
    return {"tasks": len(secs), "lane_s": sum(secs), "wall_h": wall / 3600,
            "least_limit_h": math.ceil(need * 4 - 1e-9) / 4, "limit_h": JOB_LIMIT_H, "cap_node_h": CAP_NODE_H,
            "units_B0": sum(1.0 for a, _, _ in all_tasks() if a == "B0"),
            "units_S2R_at_k20": sum(4.1 for a, _, _ in all_tasks() if a == "S2R")}


# ------------------------------------------------------------------------------------------- the queue lines
def product_path(runs: Path, arm: str, truth: str, seed: int = SEED) -> Path:
    return Path(runs) / arm / truth / f"{task_id(arm, truth, seed)}.npz"


def runner_argv(a, arm: str, truth: str, seed: int = SEED) -> list[str]:
    """FD-PRR's B0 line for (truth, seed), with this arm's iterations, tag and output."""
    argv = P.runner_argv(a, "B0", truth, seed)
    T._set(argv, "--iters", str(S.ITERS[arm]))
    T._set(argv, "--tag", f"s2r_{arm}_{truth}")
    T._set(argv, "--out", f"{a.runs}/{arm}/{truth}")
    return argv


def queue_lines(a) -> list[str]:
    lines = [f"# S2R queue {JOB}: columns id, arm, seconds, script, argv (longest first)"]
    for arm, t, s in ordered(all_tasks()):
        argv = ["run", "--arm", arm, "--truth", t, "--stage", str(a.stage_json), "--", *runner_argv(a, arm, t, s)]
        lines.append("\t".join([task_id(arm, t, s), arm, str(TASK_S[arm]), "s2r/s2r_probe.py", *argv]))
    return lines


# ------------------------------------------------------------------------------------------- the namespace check
def check_namespace(ns, arm: str, truth: str) -> str | None:
    import s5e_trace
    if getattr(ns, "config", None) != "R":
        return "every arm is built on configuration (e): --config must be R"
    if not (getattr(ns, "expectation", False) and getattr(ns, "no_nuisance", False)):
        return "the pseudo-data are noise-free: --expectation and --no-nuisance are required"
    if getattr(ns, "iters", None) != S.ITERS[arm]:
        return f"arm {arm} runs {S.ITERS[arm]} iterations, not {getattr(ns, 'iters', None)}"
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
    if getattr(ns, "tag", None) != f"s2r_{arm}_{truth}":
        return f"the tag is s2r_{arm}_{truth}"
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
@contextmanager
def install(arm: str, truth: str, rho: dict | None, guard: bool = True, M16=None, fm=None):
    """Rebind, for one invocation, the parse, the build, the unfold, the rho loader and the writer (module doc)."""
    import s5n_pseudo
    import s5p_numerics
    import s5p_truths
    import s5c_pseudo
    import s5e_trace
    if arm not in S.ARMS or truth not in TRUTHS:
        raise ValueError(f"unknown arm or truth: {arm!r}, {truth!r}")
    state = {"checked": not guard, "columns": None, "builds": 0, "unfolds": 0, "r_A": None, "trace": None,
             "evidence": None}
    here = {f: sha256_path(HERE / f) for f in ("s2r_probe.py", "s2r_arm.py", "s2r_rule.py")}
    saved = [(argparse.ArgumentParser, "parse_args", argparse.ArgumentParser.parse_args),
             (s5n_pseudo, "build_pseudo", s5n_pseudo.build_pseudo), (s5p_numerics, "unfold_one", s5p_numerics.unfold_one),
             (s5p_truths, "load_fine_rho", s5p_truths.load_fine_rho), (s5n_pseudo, "write_product", s5n_pseudo.write_product)]
    orig_parse, orig_build, _, orig_rho, orig_write = (v for _, _, v in saved)

    def parse_args(self, args=None, namespace=None):
        ns = orig_parse(self, args, namespace)
        if hasattr(ns, "pseudo_seeds"):
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
        exp, x_true, info = orig_build(inputs, bkg, truth_name, amplitude, split_key, pseudo_seed, ratio, **kw)
        r = np.asarray(s5n_pseudo.truth_weight(truth_name, inputs, amplitude, ratio), float)
        is_b = s5c_pseudo.half_mask(inputs["MCgen"].shape[0], split_key)
        state["r_A"] = r[~is_b]
        state["builds"] += 1
        return exp, x_true, info

    def unfold_one(exp, dtype, estimator_seed, threads, iters, unfold_fn=None):
        if unfold_fn is not None:
            raise Refused("unfold_one was given an unfold function: the arm's traced unfold is the only one")
        if state["r_A"] is None or len(state["r_A"]) != len(exp["MCgen"]):
            raise Refused("r was not captured on the unfolding half")
        feat, w_ref, ev = s5e_trace.measured_side(exp, estimator_seed, threads, None, dtype)
        unf_in = s5e_trace.unf_inputs(exp, feat, w_ref)
        m16 = M16 if M16 is not None else T._cell_matrix()
        fmap = fm if fm is not None else T._fine_map()
        rec = TA.ArmRecorder(unf_in, state["r_A"], m16, fmap, iters)
        xs, params, tracer = S.traced_unfold_s2r(unf_in, rec, estimator_seed, threads, iters, arm, state["r_A"])
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
        if ref.get("ran") is False:
            raise RuntimeError("refusing to write: the refinement did not run on background-inclusive pseudo-data")
        block = {"schema": SCHEMA, "arm": arm, "truth": truth, "iters": S.ITERS[arm], "evidence": state["evidence"],
                 "input_columns": state["columns"], "code_sha256": here}
        state["builds"] = state["unfolds"] = 0
        return orig_write(out, {**arrays, **state["trace"]}, {**meta, "s2r": block})

    argparse.ArgumentParser.parse_args = parse_args
    s5n_pseudo.build_pseudo = build_pseudo
    s5p_numerics.unfold_one = unfold_one
    s5p_truths.load_fine_rho = load_fine_rho
    s5n_pseudo.write_product = write_product
    try:
        yield state
    finally:
        T._restore(saved)


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
        rho = T.rho_copies(json.loads(Path(stage_json).read_text()))
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


# ------------------------------------------------------------------------------------------- staging
def pair_refs() -> list[tuple[str, int]]:
    """(truth, seed) of every FD-PRR B0 product C-PAIR, C-X and C-P read."""
    return [(t, SEED) for t in TRUTHS]


def sources(repo: Path = REPO) -> list[dict]:
    """FD-PRR's four inputs with FD-PRR's pins, the fine-ratio rho arrays the truths' hypotheses name (with the
    committed json's sha256), and FD-PRR's three B0 products at split 991000 (with the committed digests)."""
    base = [e for e in P.SOURCES if not e["role"].startswith("fd_stab_control_")]
    rho = {}
    for t in TRUTHS:
        hyp = json.loads((repo / P.closure_spec(t)[1]).read_text())
        if hyp.get("schema") == T.FINE_SCHEMA:
            src = hyp["rho_npz"]["path"]
            rho[src] = {"role": "rho_" + Path(src).stem.replace("rho-", "", 1), "src": src,
                        "sha256": hyp["rho_npz"]["sha256"], "name": f"s5p-nullsF/{Path(src).name}"}
    dig = T.prr_digests(repo / T.PRR_RECEIPTS.relative_to(T.REPO))
    prr = []
    for t, s in pair_refs():
        rel = T.prr_rel("B0", t, s)
        if rel not in dig:
            raise Refused(f"FD-PRR's listings carry no digest for {rel}")
        prr.append({"role": f"prr_B0_{t}_s{s}", "src": f"{PRR_OUT}/{rel}", "sha256": dig[rel],
                    "name": T.prr_name("B0", t, s)})
    return base + list(rho.values()) + prr


def staged_paths(stage_dir: Path, runs: Path, stage_json: Path) -> object:
    a = P.staged_paths(stage_dir, runs, None)
    a.stage_json = stage_json
    return a


# ------------------------------------------------------------------------------------------- C-PAIR, C-X, C-ONE
def pair(stage_rec: dict, runs: Path) -> dict:
    """C-PAIR: B0's k = 5 unfold equals FD-PRR's B0 product bitwise at each truth. C-X: every task's truth equals
    FD-PRR's B0 truth bitwise. C-ONE: S2R's R00-R15 at k = 1 equals B0's at k = 1 to 1e-12 relative (S2R acts from
    iteration 2 on)."""
    copies = {e["role"]: (Path(e["copy"]), e["sha256"]) for e in stage_rec["files"]}
    out = {"job": JOB, "C-PAIR": {}, "C-X": {}, "C-ONE": {}}
    for t, s in pair_refs():
        ref, pin = copies.get(f"prr_B0_{t}_s{s}", (None, None))
        ok = ref is not None and sha256_path(ref) == pin
        if not ok:
            out["C-PAIR"][t] = {"pass": False, "why": "the staged FD-PRR product is missing or not its pin"}
        else:
            out["C-PAIR"][t] = T.same(T._load(product_path(runs, "B0", t, s), "xsec_flat"), T._load(ref, "xsec_flat"))
        for arm in S.ARMS:
            key = task_id(arm, t, s)
            out["C-X"][key] = (T.same(T._load(product_path(runs, arm, t, s), "xtrue_flat"), T._load(ref, "xtrue_flat"))
                               if ok else {"pass": False, "why": "no staged FD-PRR product"})
        b = T._load(product_path(runs, "B0", t, s), "X16_push")[0]
        r = T._load(product_path(runs, "S2R", t, s), "X16_push")[0]
        out["C-ONE"][t] = {"pass": bool(np.allclose(r, b, rtol=1e-12, atol=0)),
                           "max_rel": float(np.max(np.abs(r / b - 1.0)))}
    out["pass"] = all(v["pass"] for blk in ("C-PAIR", "C-X", "C-ONE") for v in out[blk].values())
    return out


# ------------------------------------------------------------------------------------------- main
def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd, rest = (argv[0], argv[1:]) if argv else ("", [])
    if cmd == "run":
        if "--" not in rest:
            print("usage: s2r_probe.py run --arm A --truth T --stage STAGE_JSON -- <s5p_nullexp arguments>",
                  file=sys.stderr)
            return 2
        i = rest.index("--")
        ap = argparse.ArgumentParser(prog="s2r_probe.py run", allow_abbrev=False)
        ap.add_argument("--arm", choices=S.ARMS, required=True)
        ap.add_argument("--truth", choices=TRUTHS, required=True)
        ap.add_argument("--stage", type=Path, required=True)
        a = ap.parse_args(rest[:i])
        return run(a.arm, a.truth, a.stage, rest[i + 1:])
    if cmd == "tasks":
        ap = argparse.ArgumentParser(prog="s2r_probe.py tasks", allow_abbrev=False)
        for opt in ("--out", "--stage-dir", "--runs", "--stage-json"):
            ap.add_argument(opt, type=Path, required=True)
        a = ap.parse_args(rest)
        ns = staged_paths(a.stage_dir, a.runs, a.stage_json)
        a.out.mkdir(parents=True, exist_ok=True)
        lines = queue_lines(ns)
        (a.out / f"{JOB}.tsv").write_text("\n".join(lines) + "\n")
        print(json.dumps({"tasks": len(lines) - 1, "out": str(a.out)}))
        return 0
    if cmd == "manifest":
        ap = argparse.ArgumentParser(prog="s2r_probe.py manifest", allow_abbrev=False)
        ap.add_argument("--out", type=Path, required=True)
        a = ap.parse_args(rest)
        a.out.write_text(json.dumps(sources(), indent=1) + "\n")
        return 0
    if cmd == "gate":
        ap = argparse.ArgumentParser(prog="s2r_probe.py gate", allow_abbrev=False)
        ap.add_argument("--task", required=True)
        ap.add_argument("--queue", type=Path, required=True)
        ap.add_argument("--log", type=Path, required=True)
        ap.add_argument("--t0", type=float, required=True)
        ap.add_argument("--limit-h", type=float, required=True)
        a = ap.parse_args(rest)
        return gate(a.task, a.queue, a.log, a.t0, a.limit_h)
    if cmd in ("stage", "verify-stage", "pair"):
        ap = argparse.ArgumentParser(prog=f"s2r_probe.py {cmd}", allow_abbrev=False)
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
                rec = P.stage(json.loads(a.manifest.read_text()), a.dest)
                a.out.write_text(json.dumps(rec, indent=1) + "\n")
                print(json.dumps({"staged": len(rec["files"])}))
                return 0
            rec = json.loads(a.stage.read_text())
            P.verify_stage(rec)
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
    if cmd == "limit":
        h = JOB_LIMIT_H
        print(f"{int(h)}:{int(round((h - int(h)) * 60)):02d}:00")
        return 0
    print("usage: s2r_probe.py {run,manifest,tasks,gate,stage,verify-stage,pair,price,limit} ...", file=sys.stderr)
    return 2


def gate(task: str, queue_path: Path, log: Path, t0: float, limit_h: float, now: float | None = None) -> int:
    """T3's gate (``t3p_probe.gate``) in its dry mode: every task priced at its queue seconds, the 0.9 rule."""
    return T.gate(task, queue_path, log, t0, limit_h, "dry", now=now)


if __name__ == "__main__":
    sys.exit(main())
