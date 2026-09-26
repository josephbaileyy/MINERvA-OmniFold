"""Freeze the tuned configurations, then aggregate the evaluation into the results JSON and the
memo tables.

    summarize_matched.py --results <dir> --freeze        # tune/ -> frozen_config.json
    summarize_matched.py --results <dir>                 # eval/ -> SCALAR_AUSSIE_MATCHED-20260925.json,
                                                         #          tables-20260925.md, tasks .jsonl.gz

Every number is read from the per-task JSON files; the count of task files found is compared with
the declared task count and a shortfall is a refusal (a resumed or partial run is never summarized
as complete). Development evidence; simulation only.
"""
from __future__ import annotations

import argparse
import gzip
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.append(str(HERE))

import matched_design as md  # noqa: E402
import selection_data as sd  # noqa: E402

RULES = ("carry", "efficiency_corrected")
PAIR_LABEL = {"efficiency_corrected": "AUSSIE lambda=0 vs OmniFold eff-corrected",
              "carry": "AUSSIE lambda=1000 vs OmniFold carry-misses"}
CASE_ORDER = ("dev",) + sd.STRESS_CASES + tuple(sd.DERIVED_CONTROL)


def load_tasks(root: Path) -> list[dict[str, Any]]:
    return [json.loads(p.read_text()) for p in sorted(root.glob("*/*.json"))]


# ------------------------------------------------------------------------------------------- #
# Freeze
# ------------------------------------------------------------------------------------------- #
def freeze(results: Path, out_path: Path) -> dict[str, Any]:
    tasks = load_tasks(results / "tune")
    expected = 2 * 2 * 4 * len(md.TUNE_SEEDS)
    if len(tasks) != expected:
        raise SystemExit(f"tune: {len(tasks)} task files, {expected} declared")
    table: dict[str, dict[str, dict[str, Any]]] = defaultdict(lambda: defaultdict(dict))
    for t in tasks:
        task = t["task"]
        if task["method"] == "omnifold":
            it = [i for i in t["iterations"] if i["k"] == md.PRIMARY_K][0]
            r, sec = it["eavail"]["recovery"], t["seconds_method"]
        else:
            r, sec = t["score"]["eavail"]["recovery"], t["seconds_method"]
        cell = table[task["method"]][task["miss"]].setdefault(
            task["cfg"], {"R": {}, "seconds": {}})
        cell["R"][str(task["seed"])] = r
        cell["seconds"][str(task["seed"])] = sec
    frozen: dict[str, dict[str, str]] = {}
    for method, grid in (("omnifold", md.HGB_GRID), ("aussie", md.AUSSIE_GRID)):
        frozen[method] = {}
        for miss in RULES:
            best, best_r = None, -np.inf
            for cfg in grid:                           # grid order: ties go to the first point
                c = table[method][miss][cfg]
                c["mean_R"] = float(np.mean(list(c["R"].values())))
                if c["mean_R"] > best_r:
                    best, best_r = cfg, c["mean_R"]
            frozen[method][miss] = best
    out = {"schema": "pfd-scalar/frozen-config/1",
           "criterion": f"mean over tuning seeds {list(md.TUNE_SEEDS)} of E_avail R on "
                        f"{md.TUNE_SELECTION} (OmniFold at k={md.PRIMARY_K}); truth set "
                        f"{md.TUNE_TRUTH_SET}; ties -> first grid point",
           "grids": {"omnifold": md.HGB_GRID, "aussie": md.AUSSIE_GRID},
           "table": json.loads(json.dumps(table)), "frozen": frozen}
    out_path.write_text(json.dumps(out, indent=1) + "\n")
    return out


# ------------------------------------------------------------------------------------------- #
# Evaluation
# ------------------------------------------------------------------------------------------- #
def flat_rows(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """One row per (task, operating point)."""
    rows = []
    for t in tasks:
        task = t["task"]
        base = {"selection": task["unit"][0], "case": task["unit"][1], "method": task["method"],
                "miss": task["miss"], "truth_set": task["truth_set"], "cfg": task["cfg"],
                "seed": task["seed"], "seconds_method": t["seconds_method"],
                "oracle_R": t["constants"]["oracle"]["eavail"]["recovery"]}
        scores = ([(i["k"], i) for i in t["iterations"]] if "iterations" in t
                  else [(None, t["score"])])
        for k, s in scores:
            e, top = s["eavail"], s["topology"]
            rows.append({**base, "k": k, "R": e["recovery"], "moves_away": e["moves_away"],
                         "R_region": e["recovery_by_region"],
                         "moves_away_region": e["moves_away_by_region"],
                         "resid": e["signed_residual_per_bin"],
                         "R_joint_p": top["joint_eavail_p"]["recovery"],
                         "R_joint_n": top["joint_eavail_n"]["recovery"],
                         "ma_joint_p": top["joint_eavail_p"]["moves_away"],
                         "ma_joint_n": top["joint_eavail_n"]["moves_away"],
                         "R_class_p": top["class_p"]["recovery"],
                         "R_class_n": top["class_n"]["recovery"]})
    return rows


def variant_key(r: dict[str, Any]) -> str:
    if r["method"] == "ibu":
        return f"ibu|{r['miss']}"
    return f"{r['method']}|{r['miss']}|{r['truth_set']}"


def _nanmean(x: list[Any]) -> float | None:
    v = [a for a in x if a is not None]
    return float(np.mean(v)) if v else None


def operating_points(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """k per iterative variant: 3, 10 and k_F0 (max mean R on F0 over seeds)."""
    ops: dict[str, dict[str, Any]] = {}
    by = defaultdict(list)
    for r in rows:
        if r["k"] is not None and r["selection"] == "F0":
            by[(variant_key(r), r["k"])].append(r["R"])
    for v in {variant_key(r) for r in rows if r["k"] is not None}:
        means = {k: float(np.mean(by[(v, k)])) for (vv, k) in by if vv == v}
        kf0 = max(sorted(means), key=lambda k: means[k])
        ops[v] = {"k3": 3, "k10": 10, "kF0": kf0, "F0_mean_R_by_k": means}
    return ops


def aggregate(rows: list[dict[str, Any]], ops: dict[str, dict[str, Any]]
              ) -> dict[str, dict[str, dict[str, Any]]]:
    """case -> "variant@op" -> aggregate over replicates x seeds."""
    sel_rows: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        v = variant_key(r)
        if r["k"] is None:
            sel_rows[(r["case"], v)].append(r)
        else:
            for op, k in (("k3", 3), ("k10", 10), ("kF0", ops[v]["kF0"])):
                if r["k"] == k:
                    sel_rows[(r["case"], f"{v}@{op}")].append(r)
    out: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for (case, v), rs in sel_rows.items():
        R = np.array([r["R"] for r in rs])
        by_rep = defaultdict(list)
        for r in rs:
            by_rep[r["selection"]].append(r["R"])
        seed_sd = {s: (float(np.std(x, ddof=1)) if len(x) > 1 else 0.0)
                   for s, x in by_rep.items()}
        out[case][v] = {
            "n": len(rs), "mean_R": float(R.mean()), "min_R": float(R.min()),
            "max_R": float(R.max()),
            "mean_R_by_replicate": {s: float(np.mean(x)) for s, x in sorted(by_rep.items())},
            "seed_sd_by_replicate": seed_sd,
            "mean_seed_sd": float(np.mean(list(seed_sd.values()))),
            "moves_away": int(sum(r["moves_away"] for r in rs)),
            "moves_away_region": {g: int(sum(r["moves_away_region"][g] for r in rs))
                                  for g in rs[0]["moves_away_region"]},
            "mean_R_region": {g: float(np.mean([r["R_region"][g] for r in rs]))
                              for g in rs[0]["R_region"]},
            "mean_signed_residual": np.mean([r["resid"] for r in rs], axis=0).round(5).tolist(),
            "mean_R_joint_p": _nanmean([r["R_joint_p"] for r in rs]),
            "mean_R_joint_n": _nanmean([r["R_joint_n"] for r in rs]),
            "moves_away_joint_p": int(sum(r["ma_joint_p"] for r in rs)),
            "moves_away_joint_n": int(sum(r["ma_joint_n"] for r in rs)),
            "mean_R_class_p": _nanmean([r["R_class_p"] for r in rs]),
            "mean_R_class_n": _nanmean([r["R_class_n"] for r in rs]),
            "mean_seconds_run": float(np.mean([r["seconds_method"] for r in rs])),
            "mean_oracle_R": float(np.mean([r["oracle_R"] for r in rs])),
        }
    return json.loads(json.dumps(out))


def library_stats(agg: dict[str, dict[str, dict[str, Any]]], v: str) -> dict[str, Any]:
    cells = {c: agg[c][v] for c in CASE_ORDER if c in agg and v in agg[c]}
    worst_case = min(cells, key=lambda c: cells[c]["mean_R"])
    sds = [sd_ for c in cells.values() for sd_ in c["seed_sd_by_replicate"].values()]
    return {"cases": len(cells), "cells": sum(c["n"] for c in cells.values()),
            "moves_away": sum(c["moves_away"] for c in cells.values()),
            "moves_away_joint_p": sum(c["moves_away_joint_p"] for c in cells.values()),
            "moves_away_joint_n": sum(c["moves_away_joint_n"] for c in cells.values()),
            "worst_case": worst_case, "worst_case_mean_R": cells[worst_case]["mean_R"],
            "min_cell_R": min(c["min_R"] for c in cells.values()),
            "library_mean_R": float(np.mean([c["mean_R"] for c in cells.values()])),
            "median_seed_sd": float(np.median(sds)), "max_seed_sd": float(np.max(sds)),
            "mean_seconds_run": float(np.mean([c["mean_seconds_run"] for c in cells.values()]))}


def decide(agg: dict[str, dict[str, dict[str, Any]]]) -> dict[str, Any]:
    out = {}
    for miss in RULES:
        for ts in md.TRUTH_SETS:
            a = library_stats(agg, f"aussie|{miss}|{ts}")
            for op in ("k3", "k10", "kF0"):
                o = library_stats(agg, f"omnifold|{miss}|{ts}@{op}")
                rob = ((a["moves_away"] < o["moves_away"]
                        and a["worst_case_mean_R"] >= o["worst_case_mean_R"])
                       or (a["worst_case_mean_R"] > o["worst_case_mean_R"]
                           and a["moves_away"] <= o["moves_away"]))
                stab = (a["median_seed_sd"] < o["median_seed_sd"]
                        and a["max_seed_sd"] < o["max_seed_sd"])
                out[f"{miss}|{ts}|{op}"] = {
                    "pair": PAIR_LABEL[miss], "truth_set": ts, "omnifold_op": op,
                    "primary": ts == "truth4" and op == "k3",
                    "aussie": a, "omnifold": o, "robustness_win": bool(rob),
                    "stability_win": bool(stab), "aussie_advances": bool(rob or stab)}
    return out


def fmt(x: Any, nd: int = 3) -> str:
    return "–" if x is None else f"{x:+.{nd}f}" if isinstance(x, float) and x < 0 else \
        f"{x:.{nd}f}" if isinstance(x, float) else str(x)


def tables(agg: dict[str, Any], dec: dict[str, Any], ops: dict[str, Any]) -> str:
    L = []
    cols = [("IBU carry k3", "ibu|carry@k3"), ("IBU eff k3", "ibu|efficiency_corrected@k3"),
            ("OF carry k3", "omnifold|carry|truth4@k3"),
            ("AUSSIE λ=1000", "aussie|carry|truth4"),
            ("OF eff k3", "omnifold|efficiency_corrected|truth4@k3"),
            ("OF eff k10", "omnifold|efficiency_corrected|truth4@k10"),
            ("AUSSIE λ=0", "aussie|efficiency_corrected|truth4"),
            ("oracle", None)]
    L.append("| case | " + " | ".join(c for c, _ in cols) + " |")
    L.append("|---|" + "---|" * len(cols))
    for case in CASE_ORDER:
        if case not in agg:
            continue
        cells = []
        for _c, v in cols:
            if v is None:
                any_v = next(iter(agg[case].values()))
                cells.append(fmt(any_v["mean_oracle_R"]))
                continue
            a = agg[case].get(v)
            if a is None:
                cells.append("–")
                continue
            s = fmt(a["mean_R"])
            if a["moves_away"]:
                s = f"**{s}** ({a['moves_away']}/{a['n']} away)"
            cells.append(s)
        L.append(f"| {case} | " + " | ".join(cells) + " |")
    return "\n".join(L)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--results", type=Path, default=HERE / "results")
    ap.add_argument("--freeze", action="store_true")
    ap.add_argument("--frozen", type=Path, default=HERE / "frozen_config.json")
    a = ap.parse_args(argv)
    if a.freeze:
        out = freeze(a.results, a.frozen)
        print(json.dumps(out["frozen"], indent=1))
        return 0
    tasks = load_tasks(a.results / "eval")
    n_units = len(sd.library())
    expected = n_units * 2 * (1 + 2 * len(md.TRUTH_SETS) * len(md.EVAL_SEEDS))
    if len(tasks) != expected:
        raise SystemExit(f"eval: {len(tasks)} task files, {expected} declared")
    rows = flat_rows(tasks)
    ops = operating_points(rows)
    agg = aggregate(rows, ops)
    dec = decide(agg)
    frozen = json.loads(a.frozen.read_text())
    runtime = defaultdict(list)
    for t in tasks:
        runtime[f"{t['task']['method']}|{t['task']['miss']}|{t['task']['truth_set']}"].append(
            t["seconds_method"])
    payload = {"schema": "pfd-scalar/matched-results/1",
               "label": "DEVELOPMENT EVIDENCE (simulation only; DEV library)",
               "design": md.__doc__, "frozen": frozen["frozen"],
               "task_files": len(tasks), "operating_points": ops, "per_case": agg,
               "decision": dec,
               "runtime_seconds": {k: {"n": len(v), "mean": float(np.mean(v)),
                                       "max": float(np.max(v))} for k, v in runtime.items()}}
    (a.results / "SCALAR_AUSSIE_MATCHED-20260925.json").write_text(
        json.dumps(payload, indent=1) + "\n")
    with gzip.open(a.results / "matched_task_rows-20260925.jsonl.gz", "wt") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    (a.results / "tables-20260925.md").write_text(tables(agg, dec, ops) + "\n")
    print(tables(agg, dec, ops))
    for k, d in dec.items():
        print(k, "rob", d["robustness_win"], "stab", d["stability_win"],
              "| A ma", d["aussie"]["moves_away"], "wc", round(d["aussie"]["worst_case_mean_R"], 3),
              "sd", round(d["aussie"]["median_seed_sd"], 4),
              "| O ma", d["omnifold"]["moves_away"], "wc",
              round(d["omnifold"]["worst_case_mean_R"], 3),
              "sd", round(d["omnifold"]["median_seed_sd"], 4))
    return 0


if __name__ == "__main__":
    sys.exit(main())
