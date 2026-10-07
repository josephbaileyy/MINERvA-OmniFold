"""Run the tuning or evaluation stage of the scalar matched comparison (local CPU).

    run_matched.py --data <dir with selection_*.npz> --out <results dir> --stage tune|eval \
        [--workers 3 --threads 3] [--methods omnifold aussie ibu] [--units F0:dev T0:D4c_p_up]

One JSON per task under ``<out>/<stage>/<method>/``; an existing task file is skipped (and the
skip is COUNTED in the stage log, so a resumed run is not mistaken for a complete one). Tasks are
grouped by (unit, method, miss rule, truth set) so each worker builds the problem and scorer once
per group. Simulation only; see `matched_design.py` for the declared design.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.append(str(HERE))

import matched_design as md  # noqa: E402


def task_name(unit: tuple[str, str], method: str, miss: str, truth_set: str, cfg: str,
              seed: int | None) -> str:
    s = "" if seed is None else f"__s{seed}"
    return f"{unit[0]}__{unit[1]}__{method}__{miss}__{truth_set}__{cfg}{s}"


def groups_for(stage: str, methods: list[str], units: list[tuple[str, str]] | None,
               frozen: dict[str, Any] | None) -> list[dict[str, Any]]:
    import selection_data as sd
    out = []
    rules = ("carry", "efficiency_corrected")
    if stage == "tune":
        unit = md.TUNE_SELECTION
        for method, grid in (("omnifold", md.HGB_GRID), ("aussie", md.AUSSIE_GRID)):
            if method not in methods:
                continue
            for miss in rules:
                for cfg in grid:
                    out.append({"unit": unit, "method": method, "miss": miss,
                                "truth_set": md.TUNE_TRUTH_SET, "cfg": cfg,
                                "seeds": list(md.TUNE_SEEDS),
                                "iterations": md.PRIMARY_K})
        return out
    lib = sd.library() if units is None else units
    for unit in lib:
        for miss in rules:
            if "ibu" in methods:
                out.append({"unit": unit, "method": "ibu", "miss": miss, "truth_set": "none",
                            "cfg": "muon_eavail", "seeds": [None],
                            "iterations": md.IBU_ITERATIONS})
            for method in ("omnifold", "aussie"):
                if method not in methods:
                    continue
                cfg = frozen[method][miss]
                for ts in md.TRUTH_SETS:
                    out.append({"unit": unit, "method": method, "miss": miss, "truth_set": ts,
                                "cfg": cfg, "seeds": list(md.EVAL_SEEDS),
                                "iterations": md.OMNIFOLD_ITERATIONS})
    return out


def run_group(args: tuple[dict[str, Any], str, str, str, int]) -> list[str]:
    group, data_dir, out_dir, stage, threads = args
    import numpy as np
    import selection_data as sd
    import scalar_estimators as se
    import scalar_scoring as ss
    if group["method"] == "aussie":
        import torch
        torch.set_num_threads(threads)
    todo = []
    for seed in group["seeds"]:
        name = task_name(group["unit"], group["method"], group["miss"], group["truth_set"],
                         group["cfg"], seed)
        path = Path(out_dir) / stage / group["method"] / f"{name}.json"
        if not path.exists():
            todo.append((seed, name, path))
    if not todo:
        return []
    sel_name, case = group["unit"]
    t_load = time.perf_counter()
    prob = sd.build_problem(sd.load_selection(Path(data_dir) / f"selection_{sel_name}.npz"),
                            sel_name, case)
    scorer = ss.Scorer(prob)
    load_seconds = time.perf_counter() - t_load
    written = []
    for seed, name, path in todo:
        rec: dict[str, Any] = {"schema": "pfd-scalar/matched-task/1", "stage": stage,
                               "task": {**group, "seeds": None, "seed": seed},
                               "problem": prob.record, "constants": scorer.constants(),
                               "load_seconds": load_seconds}
        t0 = time.perf_counter()
        if group["method"] == "omnifold":
            params = md.HGB_GRID[group["cfg"]]
            its = []

            def on_it(k: int, push: np.ndarray, info: dict[str, Any]) -> None:
                t = time.perf_counter()
                s = scorer.score(push)
                its.append({"k": k, **s, "fit": info,
                            "score_seconds": time.perf_counter() - t})
                print(f"[{name}] k={k} R={s['eavail']['recovery']:.4f} "
                      f"t={info['seconds_iteration']:.0f}s", flush=True)

            rec["seconds_method"] = se.run_omnifold(
                prob, truth_set=group["truth_set"], miss_rule=group["miss"], params=params,
                seed=seed, iterations=group["iterations"], on_iteration=on_it)
            rec["classifier_params"] = params
            rec["iterations"] = its
        elif group["method"] == "aussie":
            params = md.AUSSIE_GRID[group["cfg"]]
            lam = se.AUSSIE_LAMBDA[group["miss"]]
            push, info = se.run_aussie(prob, truth_set=group["truth_set"], lam=lam, seed=seed,
                                       **params)
            rec["seconds_method"] = info["seconds"]
            rec["params"] = {**params, "lambda_miss": lam}
            rec["fit"] = info
            rec["score"] = scorer.score(push)
            print(f"[{name}] R={rec['score']['eavail']['recovery']:.4f} "
                  f"t={info['seconds']:.0f}s", flush=True)
        else:
            its = []
            for step in se.run_ibu_iter(prob, group["miss"], group["iterations"]):
                its.append({"k": step["iteration"], **scorer.score(step["push"]),
                            "lost_data": step["lost_data"]})
            rec["iterations"] = its
            rec["seconds_method"] = time.perf_counter() - t0
        rec["seconds_total"] = time.perf_counter() - t0
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(rec, allow_nan=False, default=_default))
        os.replace(tmp, path)
        written.append(name)
    return written


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


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--stage", choices=("tune", "eval"), required=True)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--threads", type=int, default=3)
    ap.add_argument("--methods", nargs="+", default=["omnifold", "aussie", "ibu"])
    ap.add_argument("--units", nargs="*", default=None, help="SEL:CASE (default: all)")
    ap.add_argument("--frozen", type=Path, default=HERE / "frozen_config.json")
    a = ap.parse_args(argv)
    os.environ["OMP_NUM_THREADS"] = str(a.threads)
    frozen = None
    if a.stage == "eval":
        frozen = json.loads(a.frozen.read_text())["frozen"]
    units = None if a.units is None else [tuple(u.split(":", 1)) for u in a.units]
    groups = groups_for(a.stage, a.methods, units, frozen)
    t0 = time.perf_counter()
    import multiprocessing as mp
    ctx = mp.get_context("spawn")
    done: list[str] = []
    with ctx.Pool(a.workers, maxtasksperchild=1) as pool:
        for names in pool.imap_unordered(
                run_group, [(g, str(a.data), str(a.out), a.stage, a.threads) for g in groups]):
            done.extend(names)
    n_tasks = sum(len(g["seeds"]) for g in groups)
    log = {"stage": a.stage, "groups": len(groups), "tasks_declared": n_tasks,
           "tasks_written_this_run": len(done),
           "tasks_skipped_existing": n_tasks - len(done), "workers": a.workers,
           "threads_per_worker": a.threads, "seconds": time.perf_counter() - t0,
           "host": platform.node(), "machine": platform.machine(),
           "python": sys.version.split()[0], "commit": _commit()}
    import sklearn
    import numpy
    log["versions"] = {"sklearn": sklearn.__version__, "numpy": numpy.__version__}
    try:
        import torch
        log["versions"]["torch"] = torch.__version__
    except ImportError:
        pass
    a.out.mkdir(parents=True, exist_ok=True)
    with open(a.out / f"{a.stage}_runlog.jsonl", "a") as f:
        f.write(json.dumps(log) + "\n")
    print(json.dumps(log))
    return 0


def _commit() -> str:
    try:
        head = subprocess.run(["git", "-C", str(HERE), "rev-parse", "HEAD"], capture_output=True,
                              text=True, check=True).stdout.strip()
        dirty = subprocess.run(["git", "-C", str(HERE), "status", "--porcelain", "--", "."],
                               capture_output=True, text=True).stdout.strip()
        return head + ("+dirty" if dirty else "")
    except Exception:  # noqa: BLE001
        return "unknown"


if __name__ == "__main__":
    sys.exit(main())
