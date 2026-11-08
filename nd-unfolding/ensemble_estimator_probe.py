#!/usr/bin/env python3
"""ENS1: the ensemble-averaged estimator E_96, one internal seed at a time, through the bound runners.

Declaration: docs/orchestration/state/measurement-paper/5d-community-20261024/fd/rounding-stability-20261106/ensemble/
ENS1-DECLARATION.md (bound by ENS1-BINDING-1.md at D = 15305f2d). E_N(y) = mean_k F(y + delta_k(y)); this module runs
the single fits F(y + delta_k(y)), and ``ensemble_estimator_analyze.py`` averages them.

    ensemble_estimator_probe.py stability --k K[,K...] -- <s5p_numerics arguments, one pair -:S>
    ensemble_estimator_probe.py base -- <s5p_numerics arguments, pair -:0>       F64(x), G0's base (no internal jitter)
    ensemble_estimator_probe.py closure --k K[,K...] --truth T -- <s5p_nullexp arguments>
    ensemble_estimator_probe.py tasks --stage {1,2} --out-dir DIR --runs DIR --npz P --bkg P --bank P --detector-dir P
                                      --closure-ratio-dir P --expect-npz-sha256 H --expect-bkg-sha256 H

The internal jitter (§2.1): delta_k(y) = u_k * spacing32(round32(y)), u_k ~ U(-1/2, 1/2) from default_rng(10000 + k),
drawn per coordinate array in the fixed order MCgen, MCreco, measured, bkg_reco, and added to y in float64 at full
precision; zero where round32(y) is a grid edge of its axis. It never casts y to float32 (the trap of §2.2:
``s5e_trace.jitter_coords`` does, ``s5e_trace.py:358``).

Rebindings, each of a name the bound code resolves at call time, restored on exit:
* stability: ``s5p_numerics.jittered`` (seed 0 is the float64 copy ``jittered(inputs, bkg, None)``; then delta_k is
  added), so the runner's own grid-membership check (``s5p_numerics.py:186-191``, exit 5) covers the total move;
* closure: ``s5p_nullexp.build`` (delta_k added to ui and ub before the bound build, outside its ExpectationRNG
  window, after this module's own grid-membership check) and ``s5p_numerics.unfold_one`` (float64 for the closure's
  hard-coded float32, ``s5p_nullexp.py:342``);
* ``s5n_pseudo.write_product``: the meta gains an ``ens1`` block; nothing is written unless ENS1's namespace check ran;
* ``argparse.ArgumentParser.parse_args``: the runner's parsed arguments must be the declared input.

MEASURES: single fits. CANNOT AUTHORIZE: a reading (the analysis evaluates §4-§5), or any change to the estimator.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from contextlib import contextmanager
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
import estimator_stability_probe as esp  # noqa: E402
import rounding_mechanism_probe as rmp  # noqa: E402
import s5n_pseudo  # noqa: E402
import s5p_numerics  # noqa: E402

SCHEMA = "ens1-ensemble-estimator/1"
N_ENS = 96
INTERNAL_BASE = 10000
INTERNAL_SEEDS = tuple(range(INTERNAL_BASE + 1, INTERNAL_BASE + N_ENS + 1))   # 10001-10096
PROTOCOL_SEEDS = tuple(range(1, 21))                                          # s = 1-20, P = 10 pairs
BASE_SEED = rmp.UNJITTERED_F64                                                # 0: the float64 unjittered input
STABILITY = rmp.STABILITY                                                     # FD-STAB's and RS1's input (§3.1)
CLOSURE_TRUTHS = tuple(name for name, *_ in esp.CLOSURES)
DETERMINISM = ("nominal", "A7_mnvtune")
COORDS = ("MCgen", "MCreco", "measured")                                      # s5p_numerics.COORD_KEYS
CHUNK = 2                                                                     # internal seeds per task (§8)
SHARDS = 6
DRY1 = tuple((s, k) for s in (BASE_SEED, 1) for k in (1, 2, 3, 4))            # + the F64 base task
DRY2 = (("nominal", 1), ("nominal", 2), ("nominal", 3), ("nominal", 4), ("W1", 1), ("W1", 2), ("A7_mnvtune", 1))


class Refusal(RuntimeError):
    pass


def sha256_bytes(*arrays) -> str:
    h = hashlib.sha256()
    for a in arrays:
        h.update(np.ascontiguousarray(a).tobytes())
    return h.hexdigest()


# ------------------------------------------------------------------------------------------ the internal jitter
def internal_step(y: np.ndarray, rng: np.random.Generator, edges: list | None) -> np.ndarray:
    """delta for one coordinate array: u * spacing32(round32(y)), u ~ U(-1/2, 1/2); zero on a grid edge."""
    y = np.asarray(y, np.float64)
    r32 = y.astype(np.float32)
    ulp = np.spacing(np.abs(r32)).astype(np.float64)
    step = rng.uniform(-0.5, 0.5, y.shape) * ulp
    if edges is not None:
        r64 = r32.astype(np.float64)
        for a, e in enumerate(edges):
            step[np.isin(r64[:, a], np.asarray(e, np.float32).astype(np.float64)), a] = 0.0
    return step


def internal_jitter(inputs: dict, bkg: dict, k: int) -> tuple[dict, dict, dict]:
    """(inputs, bkg) with delta_k added at full precision in float64, and the four coordinate digests after it."""
    if k not in range(1, N_ENS + 1):
        raise Refusal(f"internal seed index {k} is not one of 1-{N_ENS}")
    rng = np.random.default_rng(INTERNAL_BASE + k)
    edges = inputs["edges"]
    ji, jb = dict(inputs), dict(bkg)
    for key in COORDS:
        y = np.asarray(inputs[key], np.float64)
        ji[key] = y + internal_step(y, rng, edges)
    y = np.asarray(bkg["bkg_reco"], np.float64)
    jb["bkg_reco"] = y + internal_step(y, rng, edges)
    digests = {key: sha256_bytes(ji[key]) for key in COORDS} | {"bkg_reco": sha256_bytes(jb["bkg_reco"])}
    return ji, jb, digests


# ----------------------------------------------------------------------------------------------- the checks
def check_stability_namespace(ns, mode: str) -> str | None:
    """The stability input exactly (§3.1), one pair; mode 'stability' allows -:0 and -:1..20, mode 'base' only -:0."""
    want = STABILITY
    if getattr(ns, "truth", None) != want["truth"] or float(getattr(ns, "amplitude", -1)) != want["amplitude"]:
        return f"ENS1 runs only the declared stability truth {want['truth']} at amplitude {want['amplitude']}"
    ratio = getattr(ns, "eavail_ratio", None)
    if ratio is None or rmp.sha256_path(Path(ratio)) != want["ratio_sha256"]:
        return "the --eavail-ratio file is not the declared one"
    if getattr(ns, "expect_npz_sha256", None) != want["npz_sha256"] or \
            getattr(ns, "expect_bkg_sha256", None) != want["bkg_sha256"]:
        return "the expected input digests are not the declared of_inputs_5d.npz and bkg_dump.npz"
    for key in ("iters", "threads", "estimator_seed"):
        if getattr(ns, key, None) != want[key]:
            return f"--{key.replace('_', '-')} must be {want[key]}"
    if getattr(ns, "fixed_split_seed", None) is not None or getattr(ns, "pseudo_seeds", None) is not None:
        return "--fixed-split-seed and --pseudo-seeds are refused"
    pairs = s5p_numerics.parse_pairs(getattr(ns, "pairs", ""))
    allowed = {(None, BASE_SEED)} if mode == "base" else {(None, s) for s in (BASE_SEED, *PROTOCOL_SEEDS)}
    if len(pairs) != 1 or pairs[0] not in allowed:
        return "ENS1 runs one declared pair per call: -:0 (the base) or -:1..20" if mode == "stability" else \
            "the F64 base is the single pair -:0"
    return None


def closure_argv(truth: str, a) -> list[str]:
    """FD-STAB's own control closure argv for one truth (``esp.candidate_tasks``), without its --tag and --out."""
    for tid, _n, argv in esp.candidate_tasks(a, "control"):
        if tid == f"stab_control_closure_{truth}":
            rest = argv[argv.index("--") + 1:]
            out = []
            skip = False
            for i, tok in enumerate(rest):
                if skip:
                    skip = False
                    continue
                if tok in ("--tag", "--out"):
                    skip = True
                    continue
                out.append(tok)
            return out
    raise Refusal(f"unknown closure truth {truth!r}")


def check_closure_namespace(ns, truth: str) -> str | None:
    """FD-STAB's closure for this truth: its hypothesis and alternative files, noise-free, the declared split."""
    entry = {name: (hyp, alt, kind, amp) for name, hyp, alt, kind, amp in esp.CLOSURES}.get(truth)
    if entry is None:
        return f"unknown closure truth {truth!r}"
    hyp, alt, kind, amp = entry
    if getattr(ns, "expect_npz_sha256", None) != STABILITY["npz_sha256"] or \
            getattr(ns, "expect_bkg_sha256", None) != STABILITY["bkg_sha256"]:
        return "the expected input digests are not the declared of_inputs_5d.npz and bkg_dump.npz"
    for key in ("iters", "threads", "estimator_seed"):
        if getattr(ns, key, None) != STABILITY[key]:
            return f"--{key.replace('_', '-')} must be {STABILITY[key]}"
    if not (getattr(ns, "expectation", False) and getattr(ns, "no_nuisance", False)) or \
            getattr(ns, "mc_fraction", None) != esp.CLOSURE_MC_FRACTION or \
            getattr(ns, "pseudo_seeds", None) != f"{esp.CLOSURE_SEED}:{esp.CLOSURE_SEED}":
        return "closures are FD-STAB's: --expectation --no-nuisance --mc-fraction half at the declared split"
    if str(getattr(ns, "hypothesis", "")) != hyp and not str(getattr(ns, "hypothesis", "")).endswith("/" + hyp):
        return f"truth {truth}: the hypothesis is not {hyp}"
    got_alt = getattr(ns, "alternative", None)
    if alt is None:
        if got_alt is not None:
            return f"truth {truth} has no alternative"
    else:
        tail = alt[len("CLUSTER:"):] if alt.startswith("CLUSTER:") else alt
        if got_alt is None or not str(got_alt).endswith(tail) or float(getattr(ns, "alternative_amplitude", -1)) != amp:
            return f"truth {truth}: the alternative is not {alt} at amplitude {amp}"
    return None


# ------------------------------------------------------------------------------------------------ the install
@contextmanager
def install(mode: str, k: int | None, truth: str | None = None):
    """Rebind for one runner call: mode 'stability' (internal seed k), 'base' (no internal jitter) or 'closure'."""
    import s5p_nullexp
    if mode not in ("stability", "base", "closure"):
        raise ValueError(f"unknown mode {mode!r}")
    if (mode == "base") != (k is None):
        raise ValueError("the base takes no internal seed; every other mode takes one")
    here = rmp.sha256_path(Path(__file__).resolve())
    st = {"checked": False}
    item: dict = {}
    saved = {"jittered": s5p_numerics.jittered, "unfold_one": s5p_numerics.unfold_one, "build": s5p_nullexp.build,
             "write_product": s5n_pseudo.write_product, "parse_args": argparse.ArgumentParser.parse_args}
    o = dict(saved)

    def jittered(inputs, bkg, seed):
        item["protocol_seed"] = seed
        ji, jb = o["jittered"](inputs, bkg, None if seed == BASE_SEED else seed)
        if k is None:
            return ji, jb
        ji, jb, item["coord_sha256"] = internal_jitter(ji, jb, k)
        return ji, jb

    def build(ui, ub, split, seed, expectation, mc_fraction):
        before = s5p_numerics.cell_membership(ui, ub["bkg_reco"])
        ji, jb, item["coord_sha256"] = internal_jitter(ui, ub, k)
        after = s5p_numerics.cell_membership(ji, jb["bkg_reco"])
        moved = {key: int((after[key] != before[key]).sum()) for key in before}
        if any(moved.values()):
            raise Refusal(f"internal seed {k} changed grid membership {moved}")
        return o["build"](ji, jb, split, seed, expectation, mc_fraction)

    def unfold_one(exp, dtype, *args, **kw):
        item["closure_dtype_requested"] = np.dtype(dtype).name
        return o["unfold_one"](exp, np.float64, *args, **kw)

    def write_product(out, arrays, meta):
        if not st["checked"]:
            raise Refusal("refusing to write: the runner's arguments were never checked by ENS1")
        block = {"schema": SCHEMA, "mode": mode, "k": k, "internal_seed": None if k is None else INTERNAL_BASE + k,
                 "truth": truth, "protocol_seed": item.get("protocol_seed"), "coord_sha256": item.get("coord_sha256"),
                 "closure_dtype_requested": item.get("closure_dtype_requested"), "code_sha256": here}
        item.clear()
        return o["write_product"](out, arrays, {**meta, "ens1": block})

    def parse_args(self, args=None, namespace=None):
        ns = o["parse_args"](self, args, namespace)
        if mode in ("stability", "base") and hasattr(ns, "pairs") and hasattr(ns, "construction"):
            why = check_stability_namespace(ns, mode)
        elif mode == "closure" and hasattr(ns, "hypothesis") and hasattr(ns, "expectation"):
            why = check_closure_namespace(ns, truth)
        else:
            return ns
        if why:
            print(f"refusing: {why}", file=sys.stderr)
            raise SystemExit(2)
        st["checked"] = True
        return ns

    if mode == "closure":
        s5p_nullexp.build, s5p_numerics.unfold_one = build, unfold_one
    else:
        s5p_numerics.jittered = jittered
    s5n_pseudo.write_product, argparse.ArgumentParser.parse_args = write_product, parse_args
    try:
        yield item
    finally:
        s5p_numerics.jittered, s5p_numerics.unfold_one = saved["jittered"], saved["unfold_one"]
        s5p_nullexp.build, s5n_pseudo.write_product = saved["build"], saved["write_product"]
        argparse.ArgumentParser.parse_args = saved["parse_args"]


def _replace(argv: list[str], opt: str, value: str) -> list[str]:
    out = [t for i, t in enumerate(argv) if t != opt and (i == 0 or argv[i - 1] != opt)]
    return out + [opt, value]


def run(mode: str, ks: list[int | None], truth: str | None, rest: list[str], runs: Path) -> int:
    """One process, one bound-runner call per internal seed; the first non-zero rc stops the task."""
    for k in ks:
        if mode == "closure":
            tag, out = f"ens1_{truth}_k{k:03d}", runs / "closure" / truth
            argv = ["--candidate", "control", "closure", "--", *_replace(_replace(rest, "--tag", tag), "--out", str(out))]
        else:
            tag = "ens1_F64" if mode == "base" else f"ens1_k{k:03d}"
            out = runs / ("F64" if mode == "base" else "stability")
            argv = ["--candidate", "control", "stability", "--",
                    *_replace(_replace(rest, "--tag", tag), "--out", str(out))]
        try:
            with install(mode, k, truth):
                rc = esp.main(argv)
        except Refusal as exc:
            print(f"refusing: {exc}", file=sys.stderr)
            return 5
        if rc:
            return rc
    return 0


# ------------------------------------------------------------------------------------------------- the queue
def stability_args(a, s: int) -> list[str]:
    return ["--npz", str(a.npz), "--bkg", str(a.bkg), "--expect-npz-sha256", a.expect_npz_sha256,
            "--expect-bkg-sha256", a.expect_bkg_sha256, "--config", "R", "--iters", str(STABILITY["iters"]),
            "--threads", str(STABILITY["threads"]), "--construction", "pseudo", "--truth", STABILITY["truth"],
            "--amplitude", str(STABILITY["amplitude"]), "--eavail-ratio", STABILITY["ratio"],
            "--pseudo-seed", str(STABILITY["pseudo_seed"]), f"--pairs=-:{s}"]


def _pairs_of_k(skip: set) -> list[list[int]]:
    ks = [k for k in range(1, N_ENS + 1) if k not in skip]
    return [ks[i:i + CHUNK] for i in range(0, len(ks), CHUNK)]


def task_lines(a, stage: int) -> tuple[list[str], list[str]]:
    """(full-run lines, dry-run lines); each line: id, unfolds, script, argv."""
    full, dry = [], []
    common = ["--runs", str(a.runs)]

    def line(tid, ks, argv):
        return "\t".join([tid, str(len(ks)), "ensemble_estimator_probe.py", *argv])
    if stage == 1:
        dry.append(line("ens1_F64", [None], ["base", *common, "--", *stability_args(a, BASE_SEED)]))
        for s, k in DRY1:
            dry.append(line(f"ens1_s{s:02d}_k{k:03d}", [k], ["stability", "--k", str(k), *common, "--",
                                                               *stability_args(a, s)]))
        for s in (BASE_SEED, *PROTOCOL_SEEDS):
            skip = {k for (s_, k) in DRY1 if s_ == s}
            for ks in _pairs_of_k(skip):
                full.append(line(f"ens1_s{s:02d}_k{ks[0]:03d}", ks, ["stability", "--k", ",".join(map(str, ks)),
                                                                     *common, "--", *stability_args(a, s)]))
    else:
        for t, k in DRY2:
            dry.append(line(f"ens1_{t}_k{k:03d}", [k], ["closure", "--k", str(k), "--truth", t, *common, "--",
                                                         *closure_argv(t, a)]))
        for t in CLOSURE_TRUTHS:
            if t == DETERMINISM[1]:
                continue
            skip = {k for (t_, k) in DRY2 if t_ == t}
            for ks in _pairs_of_k(skip):
                full.append(line(f"ens1_{t}_k{ks[0]:03d}", ks, ["closure", "--k", ",".join(map(str, ks)), "--truth", t,
                                                                *common, "--", *closure_argv(t, a)]))
    return full, dry


def shards(lines: list[str], n: int = SHARDS) -> list[list[str]]:
    return [lines[i::n] for i in range(n)]


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ["tasks"]:
        ap = argparse.ArgumentParser(prog="ensemble_estimator_probe.py tasks", allow_abbrev=False)
        ap.add_argument("--stage", type=int, choices=(1, 2), required=True)
        for opt in ("--out-dir", "--runs", "--npz", "--bkg", "--bank", "--detector-dir", "--closure-ratio-dir"):
            ap.add_argument(opt, type=Path, required=True)
        ap.add_argument("--expect-npz-sha256", required=True)
        ap.add_argument("--expect-bkg-sha256", required=True)
        a = ap.parse_args(argv[1:])
        full, dry = task_lines(a, a.stage)
        head = f"# ENS1 stage {a.stage} (ENS1-DECLARATION.md §8); columns: id, unfolds, script, argv"
        a.out_dir.mkdir(parents=True, exist_ok=True)
        (a.out_dir / "dry.tsv").write_text("\n".join([head, *dry]) + "\n")
        for i, sh in enumerate(shards(full)):
            (a.out_dir / f"shard{i}.tsv").write_text("\n".join([head, *sh]) + "\n")
        n = lambda ls: sum(int(l.split("\t")[1]) for l in ls)  # noqa: E731
        print(json.dumps({"stage": a.stage, "dry_tasks": len(dry), "dry_unfolds": n(dry), "full_tasks": len(full),
                          "full_unfolds": n(full), "shard_tasks": [len(s) for s in shards(full)]}))
        return 0
    if argv[:1] == ["expect"]:
        try:
            print("\n".join(str(p) for p in expected_outputs(argv[1:])))
        except (ValueError, SystemExit) as exc:
            print(f"refusing: {exc}", file=sys.stderr)
            return 2
        return 0
    try:
        mode, ks, truth, rest, runs = parse_task(argv)
    except ValueError as exc:
        print(f"refusing: {exc}" if str(exc).startswith("--k") else str(exc), file=sys.stderr)
        return 2
    return run(mode, ks, truth, rest, runs)


def parse_task(argv: list[str]):
    """A task's argv -> (mode, internal seeds, truth, runner arguments, runs directory)."""
    if argv[:1] not in (["stability"], ["base"], ["closure"]) or "--" not in argv:
        raise ValueError("usage: ensemble_estimator_probe.py {stability --k LIST | base | closure --k LIST --truth T} "
                         "--runs DIR -- <runner arguments>")
    mode, cut = argv[0], argv.index("--")
    ap = argparse.ArgumentParser(prog=f"ensemble_estimator_probe.py {mode}", allow_abbrev=False)
    ap.add_argument("--runs", type=Path, required=True)
    if mode != "base":
        ap.add_argument("--k", required=True)
    if mode == "closure":
        ap.add_argument("--truth", choices=CLOSURE_TRUTHS, required=True)
    a = ap.parse_args(argv[1:cut])
    ks: list[int | None] = [None] if mode == "base" else [int(v) for v in a.k.split(",")]
    if mode != "base" and (len(set(ks)) != len(ks) or any(k not in range(1, N_ENS + 1) for k in ks)):
        raise ValueError(f"--k must be distinct values in 1-{N_ENS}")
    return mode, ks, getattr(a, "truth", None), argv[cut + 1:], a.runs


def expected_outputs(argv: list[str]) -> list[Path]:
    """Every product a task writes, as ``run`` names them; the job script's teardown guard reads this (§8)."""
    mode, ks, truth, rest, runs = parse_task(argv)
    if mode == "closure":
        return [runs / "closure" / truth / f"ens1_{truth}_k{k:03d}_s{esp.CLOSURE_SEED}.npz" for k in ks]
    pairs = [t.split("=", 1)[1] for t in rest if t.startswith("--pairs=")]
    if len(pairs) != 1:
        raise ValueError("a stability task carries exactly one --pairs=")
    (b, j), = s5p_numerics.parse_pairs(pairs[0])
    if mode == "base":
        return [runs / "F64" / s5p_numerics.product_name("ens1_F64", b, j)]
    return [runs / "stability" / s5p_numerics.product_name(f"ens1_k{k:03d}", b, j) for k in ks]


if __name__ == "__main__":
    sys.exit(main())
