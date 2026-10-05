"""Per-unfolding A100 GPU-hours at each design's declared packing (PROTOCOL-20260925 section 6.7).

Runs execute with several worker slots per GPU (`jobs/pfd_worker_chain.sh`, SLOTS_PER_GPU), so a
run's wall time x 1 GPU overstates the cost of a packed run. The prospective per-unfolding cost of
a design at its declared packing (the densest packing its memory allows) is

    gpu_hours = ( K x mean_i(iteration_seconds_i / slots) + load_seconds / slots ) / 3600

over the run's iterations executed at the declared packing (`slots` = the declared slots per GPU;
iterations run at another packing are ignored). K is the design's iteration count; the load is
paid once per unfolding. A run with no iteration at the declared packing is excluded and listed
with its reason.

Packing of an iteration: each receipt segment names the Slurm job that executed it
(`first_iteration`..`last_iteration`, inclusive; a later segment overrides an earlier one on the
same iteration); the job's chain log `<run parent>/chain-<job>.txt` carries
`job <id> slots <n>/gpu x <g> gpus, ...`. An iteration whose job has no such log (or no segment
covers it) has unknown packing and is ignored (counted and its jobs listed per run).

Blinding: receipts also carry training statistics (fits, closure, per-iteration weight
statistics, ...). `read_timing` returns only `iterations[].{iteration,seconds}`,
`segments[].{job,first_iteration,last_iteration}` and `load_seconds`; everything else is dropped
as soon as the file is parsed and never reaches the output or stdout. (`iteration` is the
iteration index, used to place an iteration in its segment; list position when absent.)

PET2 (`../pet2/run_pet2_replicate.py`) runs through `hybrid_driver.HybridMultiFold`, a subclass of
the same B2 loop, so its receipt carries the same `iterations`/`segments`/`load_seconds`; its extra
per-step `resources` timing is not read.

    python cost_from_receipts.py --runs <OUT>/S4F-H2S1K5-FB0 <OUT>/S4F-H2S1K5-FB1 ... \\
        --packing H2S1=2 L128S1=2 P2preS1=1 [--candidate-of REGEX] --out cost.json

`--candidate-of`: a regex with named groups `cid` (candidate id) and `k` (iteration count) matched
against each run directory's name; the default handles
`<STAGE>-<CID>K<k>-<BANK><r>[-<case>][-b<m>]` (`S4F-H2S1K5-FB3` -> H2S1, 5;
`S3P-L128S1K5-DEV0-D1_m0.350` -> L128S1, 5).

cost.json: {"schema", "definition", "packing_declared", "candidate_pattern", "unmatched_runs",
            "candidates": {cid: {"k", "packing", "gpu_hours_per_unfolding": [per run], "runs": [...],
                                 "excluded": [...], "median", "mean", "sd", "evidence_cost"}}}
`evidence_cost` is the `decide.py` evidence declaration's per-candidate "cost" block
(`unfoldings_per_result` = 6: the section-9 estimate is the mean of B = 6 bootstrap-member
unfoldings; `inference_gpu_hours` = 0.0), or null with a reason when fewer than 2 runs remain
(`inference.cost_ratio_lb` needs >= 2).
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

SCHEMA = "pfd-cost-from-receipts/1"
UNFOLDINGS_PER_RESULT = 6
INFERENCE_GPU_HOURS = 0.0
DEFAULT_CANDIDATE_RE = (r"^(?P<stage>[A-Za-z0-9]+)-(?P<cid>[A-Za-z0-9]+)K(?P<k>\d+)"
                        r"-(?P<bank>[A-Za-z]+)(?P<rep>\d+)"
                        r"(?:-(?!b\d+$)(?P<case>[^-].*?))?(?:-b(?P<member>\d+))?$")
CHAIN_LINE = re.compile(r"^job (\S+) slots (\d+)/gpu\b")
DEFINITION = ("gpu_hours = (K * mean(iteration_seconds / slots) + load_seconds / slots) / 3600 over "
              "the iterations executed at the declared packing (slots per GPU)")


# ------------------------------------------------------------------------------------------- #
# Inputs
# ------------------------------------------------------------------------------------------- #
def _number(value: Any, what: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{what} is not a number")
    v = float(value)
    if not math.isfinite(v) or v < 0:
        raise ValueError(f"{what} is not finite and non-negative")
    return v


def _index(value: Any, what: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{what} is not a non-negative integer")
    return value


def read_timing(receipt: Path) -> dict[str, Any]:
    """The timing fields of a run receipt and nothing else (blinding; module docstring).

    Error messages name fields and indices only, never receipt content."""
    doc = json.loads(Path(receipt).read_text())
    try:
        if not isinstance(doc, dict):
            raise ValueError("receipt is not a JSON object")
        raw_it, raw_seg = doc.get("iterations"), doc.get("segments")
        if not isinstance(raw_it, list) or not isinstance(raw_seg, list):
            raise ValueError("receipt lacks iterations/segments lists")
        iterations = []
        for pos, r in enumerate(raw_it):
            if not isinstance(r, dict) or "seconds" not in r:
                raise ValueError(f"iterations[{pos}] has no seconds")
            iterations.append({"iteration": _index(r.get("iteration", pos),
                                                   f"iterations[{pos}].iteration"),
                               "seconds": _number(r["seconds"], f"iterations[{pos}].seconds")})
        segments = []
        for pos, s in enumerate(raw_seg):
            if not isinstance(s, dict) or "first_iteration" not in s:
                raise ValueError(f"segments[{pos}] has no first_iteration")
            job = s.get("job")
            last = s.get("last_iteration")
            segments.append({
                "job": None if job is None else str(job),
                "first_iteration": _index(s["first_iteration"], f"segments[{pos}].first_iteration"),
                "last_iteration": (None if last is None
                                   else _index(last, f"segments[{pos}].last_iteration"))})
        load = _number(doc.get("load_seconds"), "load_seconds")
    finally:
        del doc
    return {"iterations": iterations, "segments": segments, "load_seconds": load}


def parse_chain_log(path: Path) -> tuple[str, int] | None:
    """(job, slots per GPU) from a chain log's `job <id> slots <n>/gpu ...` line, or None."""
    for line in Path(path).read_text().splitlines():
        m = CHAIN_LINE.match(line.strip())
        if m:
            return m.group(1), int(m.group(2))
    return None


def chain_packings(directory: Path) -> dict[str, int]:
    """job id -> slots per GPU over `directory/chain-<job>.txt`. A log whose job line names a
    different job than its file name, or that has no job line, contributes nothing."""
    out: dict[str, int] = {}
    for p in sorted(Path(directory).glob("chain-*.txt")):
        parsed = parse_chain_log(p)
        if parsed is None or parsed[0] != p.stem[len("chain-"):]:
            continue
        out[parsed[0]] = parsed[1]
    return out


def parse_run_name(name: str, pattern: str | re.Pattern = DEFAULT_CANDIDATE_RE,
                   k_of: Mapping[str, int] | None = None) -> tuple[str, int] | None:
    """(candidate id, K) from a run directory name, or None when it does not match. K comes from
    the name's `k` group, else from `k_of` (development runs carry no K in their names)."""
    m = re.match(pattern, name)
    if m is None:
        return None
    cid = m.group("cid")
    k = m.groupdict().get("k")
    if k is None:
        if not k_of or cid not in k_of:
            raise ValueError(f"run {name}: no K in the name and no --k-of entry for {cid}")
        return cid, int(k_of[cid])
    return cid, int(k)


def parse_packing(items: Sequence[str]) -> dict[str, int]:
    out: dict[str, int] = {}
    for item in items:
        cid, sep, slots = item.partition("=")
        if not sep or not cid or not slots.isdigit() or int(slots) < 1:
            raise ValueError(f"--packing entry {item!r} is not CAND=SLOTS with SLOTS >= 1")
        if cid in out:
            raise ValueError(f"--packing declares {cid} twice")
        out[cid] = int(slots)
    return out


# ------------------------------------------------------------------------------------------- #
# Cost
# ------------------------------------------------------------------------------------------- #
def run_cost(run_dir: Path, k: int, slots: int, packings: Mapping[str, int]) -> dict[str, Any]:
    """One run's per-unfolding GPU-hours at `slots` per GPU. Returns a record with `gpu_hours`,
    or with `excluded` (the reason) when no iteration ran at the declared packing."""
    run_dir = Path(run_dir)
    rec: dict[str, Any] = {"run": run_dir.name, "path": str(run_dir)}
    try:
        t = read_timing(run_dir / "receipt.json")
    except (OSError, ValueError) as exc:          # json.JSONDecodeError is a ValueError
        rec["excluded"] = f"receipt unreadable: {type(exc).__name__}: {exc}"
        return rec
    job_of: dict[int, str | None] = {}
    for s in t["segments"]:
        if s["last_iteration"] is None:
            continue                               # stopped before completing an iteration
        for i in range(s["first_iteration"], s["last_iteration"] + 1):
            job_of[i] = s["job"]
    used, other, unknown_jobs = [], {}, set()
    n_unknown = 0
    for it in t["iterations"]:
        job = job_of.get(it["iteration"])
        packing = packings.get(job) if job is not None else None
        if packing is None:
            n_unknown += 1
            unknown_jobs.add("<no segment>" if it["iteration"] not in job_of
                             else "<no job id>" if job is None else job)
        elif packing == slots:
            used.append(it["seconds"])
        else:
            other[str(packing)] = other.get(str(packing), 0) + 1
    rec.update({"iterations_total": len(t["iterations"]), "iterations_used": len(used),
                "iterations_other_packing": other, "iterations_unknown_packing": n_unknown,
                "unknown_packing_jobs": sorted(unknown_jobs),
                "segment_packings": {str(s["job"]): packings.get(s["job"])
                                     for s in t["segments"] if s["job"] is not None},
                "load_seconds": t["load_seconds"]})
    if not used:
        rec["excluded"] = f"no iteration executed at the declared packing ({slots}/gpu)"
        return rec
    mean_iter = float(np.mean(used))
    rec["mean_iteration_seconds"] = mean_iter
    rec["gpu_hours"] = (k * mean_iter / slots + t["load_seconds"] / slots) / 3600.0
    return rec


def evidence_cost(values: Sequence[float]) -> dict[str, Any]:
    """The decide.py evidence declaration's per-candidate "cost" block."""
    return {"gpu_hours_per_unfolding": [float(v) for v in values],
            "unfoldings_per_result": UNFOLDINGS_PER_RESULT,
            "inference_gpu_hours": INFERENCE_GPU_HOURS}


def summarize(runs: Sequence[Path], packing: Mapping[str, int],
              pattern: str = DEFAULT_CANDIDATE_RE,
              k_of: Mapping[str, int] | None = None) -> dict[str, Any]:
    compiled = re.compile(pattern)
    if not {"cid", "k"} <= set(compiled.groupindex):
        raise ValueError("--candidate-of needs named groups 'cid' and 'k'")
    seen: set[Path] = set()
    groups: dict[str, list[Path]] = {}
    ks: dict[str, int] = {}
    unmatched = []
    for r in map(Path, runs):
        key = r.resolve()
        if key in seen:
            raise ValueError(f"run {r} listed twice")
        seen.add(key)
        parsed = parse_run_name(r.name, compiled, k_of)
        if parsed is None:
            unmatched.append(str(r))
            continue
        cid, k = parsed
        if ks.setdefault(cid, k) != k:
            raise ValueError(f"candidate {cid}: runs declare K = {ks[cid]} and {k}")
        groups.setdefault(cid, []).append(r)
    missing = sorted(set(groups) - set(packing))
    if missing:
        raise ValueError(f"no --packing declared for candidate(s) {', '.join(missing)}")
    logs: dict[Path, dict[str, int]] = {}
    candidates: dict[str, Any] = {}
    for cid in sorted(groups):
        k, slots = ks[cid], packing[cid]
        kept, excluded = [], []
        for r in groups[cid]:
            parent = r.absolute().parent
            if parent not in logs:
                logs[parent] = chain_packings(parent)
            rec = run_cost(r, k, slots, logs[parent])
            (excluded if "excluded" in rec else kept).append(rec)
        values = [rec["gpu_hours"] for rec in kept]
        v = np.asarray(values, dtype=np.float64)
        entry: dict[str, Any] = {
            "k": k, "packing": slots, "gpu_hours_per_unfolding": values, "runs": kept,
            "excluded": excluded, "n": len(values),
            "median": float(np.median(v)) if v.size else None,
            "mean": float(v.mean()) if v.size else None,
            "sd": float(v.std(ddof=1)) if v.size >= 2 else None}
        if v.size >= 2:
            entry["evidence_cost"] = evidence_cost(values)
        else:
            entry["evidence_cost"] = None
            entry["evidence_cost_reason"] = ("fewer than 2 runs at the declared packing "
                                             "(inference.cost_ratio_lb needs >= 2)")
        candidates[cid] = entry
    return {"schema": SCHEMA, "definition": DEFINITION, "packing_declared": dict(packing),
            "candidate_pattern": pattern, "unmatched_runs": unmatched, "candidates": candidates}


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--runs", nargs="+", required=True, type=Path, help="run directories")
    ap.add_argument("--packing", nargs="+", required=True, metavar="CAND=SLOTS",
                    help="declared worker slots per GPU for each candidate")
    ap.add_argument("--candidate-of", default=DEFAULT_CANDIDATE_RE, metavar="REGEX",
                    help="regex with named groups cid and k, matched against run names")
    ap.add_argument("--k-of", nargs="+", default=None, metavar="CAND=K",
                    help="K for candidates whose run names carry none (development stages)")
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args(argv)
    try:
        k_of = parse_packing(args.k_of) if args.k_of else None
        doc = summarize(args.runs, parse_packing(args.packing), args.candidate_of, k_of)
    except (ValueError, re.error) as exc:
        print(f"cost_from_receipts: {exc}", file=sys.stderr)
        return 2
    args.out.write_text(json.dumps(doc, indent=1) + "\n")
    print(json.dumps({"out": str(args.out), "unmatched_runs": len(doc["unmatched_runs"]),
                      "candidates": {c: {"k": e["k"], "packing": e["packing"], "n": e["n"],
                                         "excluded": len(e["excluded"]), "median": e["median"]}
                                     for c, e in doc["candidates"].items()}}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
