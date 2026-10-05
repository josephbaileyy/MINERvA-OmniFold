"""Exploratory GBDT fill-in: the matched study's scalar OmniFold on the PET final-bank draws.

    pgc_run_fb.py --pet-source <bc356b0c checkout> --raw <dir of copied run dirs> \
        --reco-scalars reco_scalars.npy --row-features row_features.npz \
        --tasks tasks.json --out <results dir> [--workers 2 --threads 2] \
        [--budget-core-hours 8.0 --stop-core-hours 7.5]

For every task (one PET run directory, i.e. one stage x FB draw x case) the GBDT is trained on that
run's own `replicate_arrays.npz` and every iteration's push is scored by the final-design scorer
(`score_design.DesignScorer.block`) against the same prior and pseudodata truth the PET runs were
scored against. The recipe is fixed by `PLAN-20261005.md` (`RECIPE` below); nothing is tuned.

**Blinding.** A task is refused unless its run is listed COMPLETE in the look-1 completeness record
(`freeze/COMPLETENESS-look1.tsv` at the pinned commit); reserve-bank and coverage (S5) runs are
refused by name before any byte is read.

**Budget.** Every finished task is charged `wall seconds x threads per worker / 3600` core-hours
(the reserved cores, an upper bound on the CPU used; the process CPU time is recorded beside it) in
`<out>/cpu_ledger.jsonl`, which persists across invocations and counts failed tasks too. A task is
started only if the charged total plus the in-flight and new tasks, each at 1.25 x the largest
charge seen so far (or `--first-task-core-hours` before any), stays within `--stop-core-hours`.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import re
import resource
import sys
import time
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import pgc_source  # noqa: E402

SCHEMA = "pet-gbdt-comparison/fb-task/1"
RECIPE = {
    "estimator": "scalar OmniFold, final_design/scalar/scalar_estimators.run_omnifold",
    "classifier": "HGBRatio (HistGradientBoosting), matched-study frozen config h1",
    "cfg": "h1",
    "miss_rule": "efficiency_corrected",
    "truth_set": "truth4_species",
    "iterations": 10,
    "operating_points": {"primary": 7, "secondary": [3, 10]},
    "seed_rule": "seed = 1 + FB draw index",
}
THREAD_VARS = ("OMP_NUM_THREADS",)
SINGLE_THREAD_VARS = ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
                      "NUMEXPR_NUM_THREADS")
RUN_RE = re.compile(r"^(S4[FS])-([A-Za-z0-9]+)-FB(\d+)(?:-(.+))?$")


def parse_run(name: str) -> dict[str, Any]:
    m = RUN_RE.match(name)
    if not m:
        raise ValueError(f"not a look-1 final-bank run name: {name!r}")
    return {"stage": m.group(1), "design": m.group(2), "fb": int(m.group(3)),
            "case": m.group(4) or "dev"}


def unblinded_look1(pet_source: Path) -> set[str]:
    path = pet_source / "nd-unfolding/pet/final_design/freeze/COMPLETENESS-look1.tsv"
    rows = set()
    for line in path.read_text().splitlines():
        if line.startswith("#") or not line.strip():
            continue
        f = line.split("\t")
        if len(f) >= 3 and f[2] == "COMPLETE":
            rows.add(f[1])
    return rows


def refuse_blinded(names: list[str], pet_source: Path) -> None:
    """Fail closed on any task outside the look-1 group."""
    bad = [n for n in names if re.search(r"^S5|-RB\d", n)]
    if bad:
        raise SystemExit(f"refusing reserve-bank or coverage runs: {bad[:3]}")
    open_rows = unblinded_look1(pet_source)
    blinded = [n for n in names if n not in open_rows]
    if blinded:
        raise SystemExit(f"refusing runs not COMPLETE in COMPLETENESS-look1.tsv: {blinded[:3]}")


def task_name(run: str) -> str:
    p = parse_run(run)
    return f"GBDT-{p['stage']}-FB{p['fb']}-{p['case']}"


# --------------------------------------------------------------------------------------------- #
# budget ledger
# --------------------------------------------------------------------------------------------- #
def read_ledger(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def charged(entries: list[dict[str, Any]]) -> float:
    return float(sum(e["charge_core_hours"] for e in entries))


def may_start(total: float, in_flight: int, largest: float | None, first: float,
              stop: float) -> bool:
    """True if starting one more task cannot cross ``stop`` at the projected per-task charge."""
    per = 1.25 * largest if largest is not None else first
    return total + (in_flight + 1) * per <= stop


# --------------------------------------------------------------------------------------------- #
# one task (runs in a spawned worker)
# --------------------------------------------------------------------------------------------- #
def run_task(args: tuple[dict[str, Any], dict[str, str], int]) -> dict[str, Any]:
    task, paths, threads = args
    t_wall = time.perf_counter()
    r0 = resource.getrusage(resource.RUSAGE_SELF)
    out: dict[str, Any] = {"task": task, "ok": False}
    try:
        out.update(_run_task(task, paths))
        out["ok"] = True
    except Exception as exc:  # noqa: BLE001  (recorded; the task is charged and retried by hand)
        out["error"] = f"{type(exc).__name__}: {exc}"
    r1 = resource.getrusage(resource.RUSAGE_SELF)
    out["wall_seconds"] = time.perf_counter() - t_wall
    out["cpu_seconds"] = (r1.ru_utime - r0.ru_utime) + (r1.ru_stime - r0.ru_stime)
    out["threads"] = threads
    return out


def _run_task(task: dict[str, Any], paths: dict[str, str]) -> dict[str, Any]:
    import numpy as np
    pet_source = Path(paths["pet_source"])
    source = pgc_source.activate(pet_source)
    import matched_design as md
    import scalar_estimators as se
    import score_design as sdz
    import selection_data as sd
    import pgc_fb

    run_dir = Path(paths["raw"]) / task["run"]
    cols = pgc_fb.InventoryColumns(paths["reco_scalars"], paths["row_features"])
    t0 = time.perf_counter()
    prob = pgc_fb.build_problem(run_dir, cols, sd)
    scorer = sdz.DesignScorer(run_dir, sdz.RowFeatures(paths["row_features"]))
    load_seconds = time.perf_counter() - t0
    keep = scorer.prior.keep
    params = md.HGB_GRID[RECIPE["cfg"]]
    iterations: list[dict[str, Any]] = []

    def on_it(k: int, push: np.ndarray, info: dict[str, Any]) -> None:
        pw = np.where(keep, push, 0.0)
        stab = scorer.stability(push, push)
        for key in [k_ for k_ in stab if k_.startswith(("pull_", "n_nonfinite_pull",
                                                         "n_negative_pull"))]:
            stab.pop(key)
        iterations.append({"k": k, "fit": info, "stability": stab,
                           "histograms": scorer.block(pw)})

    seconds = se.run_omnifold(prob, truth_set=RECIPE["truth_set"],
                              miss_rule=RECIPE["miss_rule"], params=params, seed=task["seed"],
                              iterations=RECIPE["iterations"], on_iteration=on_it)
    import sklearn
    return {"schema": SCHEMA, "name": task_name(task["run"]), "recipe": RECIPE,
            "classifier_params": params, "case": scorer.case, "identity": scorer.identity,
            "problem": prob.record, "n": scorer.n,
            "provenance": {"pet_source": source["commit"],
                           "pet_files_loaded": pgc_source.loaded_files(pet_source),
                           "replicate_arrays_sha256": sdz.sha256_file(
                               run_dir / "replicate_arrays.npz"),
                           "reco_scalars": paths["reco_scalars"],
                           "row_features": paths["row_features"]},
            "versions": {"python": sys.version.split()[0], "numpy": np.__version__,
                         "sklearn": sklearn.__version__},
            "load_seconds": load_seconds, "seconds_method": seconds,
            "oracle_anchor": scorer.oracle_anchor(), "iterations": iterations}


# --------------------------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pet-source", type=Path, required=True)
    ap.add_argument("--raw", type=Path, required=True)
    ap.add_argument("--reco-scalars", type=Path, required=True)
    ap.add_argument("--row-features", type=Path, required=True)
    ap.add_argument("--tasks", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--threads", type=int, default=2)
    ap.add_argument("--max-threads", type=int, default=4)
    ap.add_argument("--budget-core-hours", type=float, default=8.0)
    ap.add_argument("--stop-core-hours", type=float, default=7.5)
    ap.add_argument("--first-task-core-hours", type=float, default=0.1)
    ap.add_argument("--limit", type=int, default=None, help="run at most this many new tasks")
    a = ap.parse_args(argv)
    if a.workers * a.threads > a.max_threads:
        raise SystemExit(f"{a.workers} workers x {a.threads} threads > {a.max_threads}")
    if a.stop_core_hours > a.budget_core_hours:
        raise SystemExit("--stop-core-hours exceeds --budget-core-hours")
    pgc_source.verify_checkout(a.pet_source)
    tasks = json.loads(a.tasks.read_text())["tasks"]
    refuse_blinded([t["run"] for t in tasks], a.pet_source)
    for t in tasks:
        if t["seed"] != 1 + parse_run(t["run"])["fb"]:
            raise SystemExit(f"{t['run']}: seed {t['seed']} violates {RECIPE['seed_rule']}")
    a.out.mkdir(parents=True, exist_ok=True)
    ledger_path = a.out / "cpu_ledger.jsonl"
    todo = [t for t in tasks if not (a.out / f"{task_name(t['run'])}.json").exists()]
    skipped = len(tasks) - len(todo)
    if a.limit is not None:
        todo = todo[:a.limit]
    for v in THREAD_VARS:
        os.environ[v] = str(a.threads)
    for v in SINGLE_THREAD_VARS:
        os.environ[v] = "1"
    paths = {"pet_source": str(a.pet_source.resolve()), "raw": str(a.raw.resolve()),
             "reco_scalars": str(a.reco_scalars.resolve()),
             "row_features": str(a.row_features.resolve())}
    import multiprocessing as mp
    ctx = mp.get_context("spawn")
    entries = read_ledger(ledger_path)
    written, stopped = [], None
    pending: list[Any] = []
    with ctx.Pool(a.workers, maxtasksperchild=1) as pool:
        queue = list(todo)
        while queue or pending:
            largest = max((e["charge_core_hours"] for e in entries), default=None)
            while queue and len(pending) < a.workers:
                if not may_start(charged(entries), len(pending), largest,
                                 a.first_task_core_hours, a.stop_core_hours):
                    stopped = (f"budget stop: charged {charged(entries):.3f} core-h, "
                               f"{len(pending)} in flight, next task projected "
                               f"{1.25 * (largest or 0):.3f}")
                    queue = []
                    break
                t = queue.pop(0)
                pending.append((t, pool.apply_async(run_task, ((t, paths, a.threads),))))
            if not pending:
                break
            time.sleep(1.0)
            still = []
            for t, res in pending:
                if not res.ready():
                    still.append((t, res))
                    continue
                r = res.get()
                entry = {"task": task_name(t["run"]), "run": t["run"], "ok": r["ok"],
                         "error": r.get("error"), "wall_seconds": r["wall_seconds"],
                         "cpu_seconds": r["cpu_seconds"], "threads": r["threads"],
                         "charge_core_hours": r["wall_seconds"] * r["threads"] / 3600.0,
                         "cpu_core_hours": r["cpu_seconds"] / 3600.0,
                         "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
                with open(ledger_path, "a") as f:
                    f.write(json.dumps(entry) + "\n")
                entries.append(entry)
                if r["ok"]:
                    path = a.out / f"{entry['task']}.json"
                    tmp = path.with_suffix(".tmp")
                    r.update({k: entry[k] for k in ("wall_seconds", "cpu_seconds", "threads",
                                                    "charge_core_hours")})
                    tmp.write_text(json.dumps(r, allow_nan=False, default=_default))
                    os.replace(tmp, path)
                    written.append(entry["task"])
                print(f"[{entry['task']}] ok={r['ok']} wall={r['wall_seconds']:.0f}s "
                      f"cpu={r['cpu_seconds']:.0f}s charged total {charged(entries):.3f} core-h"
                      + (f" ERROR {r.get('error')}" if not r["ok"] else ""), flush=True)
            pending = still
    log = {"tasks_declared": len(tasks), "skipped_existing": skipped, "written": len(written),
           "stopped": stopped, "charged_core_hours_total": charged(entries),
           "cpu_core_hours_total": sum(e["cpu_core_hours"] for e in entries),
           "workers": a.workers, "threads_per_worker": a.threads,
           "host": platform.node(), "machine": platform.machine(),
           "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    with open(a.out / "runlog.jsonl", "a") as f:
        f.write(json.dumps(log) + "\n")
    print(json.dumps(log))
    return 0


def _default(o: Any) -> Any:
    import numpy as np
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(type(o))


if __name__ == "__main__":
    sys.exit(main())
