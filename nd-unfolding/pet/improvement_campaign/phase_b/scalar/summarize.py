"""Collect the Phase-B1 result files into `results/summary.json` and print the report's tables.

Reads only files under `results/` (copied from the task directory with their sha256 recorded in
the summary). Seed statistics are mean, sample standard deviation (ddof=1) and range over the
seeds present; nothing is dropped silently -- a missing seed is listed.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
RES = HERE / "results"
REGIONS = ("low_acceptance", "moderate", "good")
K_TABLE = (1, 2, 3, 4, 5, 10, 20, 30, 50)
IT_TABLE = (1, 2, 3, 4, 5, 8, 10, 15, 20)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _stats(values: list[float]) -> dict[str, Any]:
    a = np.asarray(values, dtype=np.float64)
    return {"n": int(a.size), "mean": float(a.mean()),
            "sd": float(a.std(ddof=1)) if a.size > 1 else None,
            "min": float(a.min()), "max": float(a.max())}


def _fmt(x: float | None, nd: int = 3) -> str:
    return "—" if x is None else f"{x:.{nd}f}"


def ibu_tables(ibu: dict) -> dict[str, Any]:
    ref = ibu["reference_curve"]
    out: dict[str, Any] = {"reference": {str(k): {"aggregate": ref["aggregate"][k - 1],
                                                   **{r: ref["regional"][r][k - 1] for r in REGIONS}}
                                          for k in K_TABLE}}
    for run in ibu["runs"]:
        name = f"{run['reco_binning']}/{run['mode']}/{run['normalization']}"
        its = {r["iteration"]: r for r in run["iterations"]}
        out[name] = {str(k): {
            "aggregate": its[k]["push"]["recovery"],
            **its[k]["push"]["recovery_by_region"],
            "overshoot_projection": its[k]["push"]["aggregate"]["overshoot_projection"],
            "pull_aggregate": its[k]["pull"]["recovery"],
            "signed_residual_per_bin": its[k]["push"]["aggregate"]["signed_residual_per_bin"],
        } for k in K_TABLE if k in its}
        best = max(its.values(), key=lambda r: r["push"]["recovery"])
        out[name]["best"] = {"iteration": best["iteration"],
                             "aggregate": best["push"]["recovery"]}
    return out


def omnifold_tables(files: list[Path]) -> dict[str, Any]:
    groups: dict[str, list[dict]] = {}
    for path in files:
        d = json.loads(path.read_text())
        d["_file"] = path.name
        t = d["task"]
        groups.setdefault(f"{t['inputs']}/{t['model']}", []).append(d)
    out: dict[str, Any] = {}
    for name, runs in sorted(groups.items()):
        seeds = sorted(r["task"]["seed"] for r in runs)
        n_it = min(len(r["iterations"]) for r in runs)
        rows = {}
        for k in range(1, n_it + 1):
            recs = [r["iterations"][k - 1] for r in runs]
            rows[str(k)] = {
                "aggregate": _stats([x["push"]["recovery"] for x in recs]),
                **{reg: _stats([x["push"]["recovery_by_region"][reg] for x in recs])
                   for reg in REGIONS},
                "pull_aggregate": _stats([x["pull"]["recovery"] for x in recs]),
                "overshoot_projection": _stats([x["push"]["aggregate"]["overshoot_projection"]
                                                for x in recs]),
                "step1_reco_eavail7": _stats([x["step1_reco_eavail7_recovery"]["recovery"]
                                              for x in recs
                                              if x["step1_reco_eavail7_recovery"]["recovery"]
                                              is not None] or [float("nan")]),
                "signed_residual_per_bin_mean": np.mean(
                    [x["push"]["aggregate"]["signed_residual_per_bin"] for x in recs],
                    axis=0).tolist(),
                "fit_seconds_mean": float(np.mean([x["step1"]["seconds"] + x["step2"]["seconds"]
                                                   for x in recs])),
            }
        out[name] = {"seeds": seeds, "iterations": n_it, "by_iteration": rows,
                     "files": sorted(r["_file"] for r in runs)}
    return out


def learnability_tables(d: dict) -> dict[str, Any]:
    groups: dict[str, list[dict]] = {}
    for r in d["results"]:
        groups.setdefault(f"{r['input_set']}/{r['model']}", []).append(r)
    out = {}
    for name, rs in sorted(groups.items()):
        out[name] = {
            "seeds": [r["seed"] for r in rs],
            "held_out_aggregate": _stats([r["held_out"]["aggregate"]["recovery"] for r in rs]),
            **{f"held_out_{reg}": _stats([r["held_out"]["regions"][reg]["recovery"] for r in rs])
               for reg in REGIONS},
            "in_sample_aggregate": (_stats([r["in_sample"]["aggregate"]["recovery"] for r in rs])
                                    if "in_sample" in rs[0] else None),
        }
    return out


def main() -> None:
    summary: dict[str, Any] = {"schema": "phase-b1-summary/1", "files": {}}
    for path in sorted(RES.glob("*.json")):
        if path.name != "summary.json":
            summary["files"][path.name] = _sha(path)
    pop = json.loads((RES / "populations.json").read_text())
    summary["reproduction"] = {"all_checks_agree": pop["all_checks_agree"],
                               "n_checks": len(pop["checks"]), "commit": pop["commit"],
                               "accepted_fraction": pop["accepted_fraction"]}
    anchors = json.loads((RES / "anchors.json").read_text())
    summary["anchors"] = {k: {"aggregate": v["recovery"], **v["recovery_by_region"],
                              "overshoot_projection": v["aggregate"]["overshoot_projection"]}
                          for k, v in anchors["scores"].items()}
    ibu = json.loads((RES / "ibu.json").read_text())
    summary["ibu"] = ibu_tables(ibu)
    learn_path = RES / "truth_learnability.json"
    if learn_path.exists():
        summary["truth_learnability"] = learnability_tables(json.loads(learn_path.read_text()))
    omni = sorted(RES.glob("omnifold_*.json"))
    if omni:
        summary["omnifold"] = omnifold_tables(omni)
    (RES / "summary.json").write_text(json.dumps(summary, indent=1, allow_nan=True) + "\n")

    # ---- markdown tables for the report --------------------------------------------------
    print("\n### anchors\n| push | aggregate | low | moderate | good | projection |\n|---|---|---|---|---|---|")
    for k, v in summary["anchors"].items():
        print(f"| {k} | {_fmt(v['aggregate'])} | {_fmt(v['low_acceptance'])} | "
              f"{_fmt(v['moderate'])} | {_fmt(v['good'])} | {_fmt(v['overshoot_projection'])} |")
    print("\n### IBU aggregate vs k\n| variant | " + " | ".join(f"k={k}" for k in K_TABLE)
          + " | best (k) |\n|---|" + "---|" * (len(K_TABLE) + 1))
    for name, rows in summary["ibu"].items():
        if name == "reference":
            vals = [rows[str(k)]["aggregate"] for k in K_TABLE]
            print("| reference 1-(1-a)^k | " + " | ".join(_fmt(v) for v in vals) + " | — |")
            continue
        vals = [rows[str(k)]["aggregate"] for k in K_TABLE]
        print(f"| {name} | " + " | ".join(_fmt(v) for v in vals)
              + f" | {_fmt(rows['best']['aggregate'])} ({rows['best']['iteration']}) |")
    for reg in REGIONS:
        print(f"\n### IBU {reg} vs k\n| variant | " + " | ".join(f"k={k}" for k in K_TABLE)
              + " |\n|---|" + "---|" * len(K_TABLE))
        for name, rows in summary["ibu"].items():
            print(f"| {name} | " + " | ".join(_fmt(rows[str(k)][reg]) for k in K_TABLE) + " |")
    if "truth_learnability" in summary:
        print("\n### truth-only learnability (held-out; mean ± sd over seeds)\n"
              "| inputs/model | aggregate | low | moderate | good | in-sample |\n|---|---|---|---|---|---|")
        for name, v in summary["truth_learnability"].items():
            def ms(s):
                return "—" if s is None else (f"{s['mean']:.4f}" + (f" ± {s['sd']:.4f}" if s["sd"] else ""))
            print(f"| {name} | {ms(v['held_out_aggregate'])} | {ms(v['held_out_low_acceptance'])} | "
                  f"{ms(v['held_out_moderate'])} | {ms(v['held_out_good'])} | {ms(v['in_sample_aggregate'])} |")
    if "omnifold" in summary:
        for name, v in summary["omnifold"].items():
            print(f"\n### scalar OmniFold {name} (seeds {v['seeds']}; mean ± sd [min, max])\n"
                  "| it | aggregate | low | moderate | good | pull | projection | reco-E_avail step-1 check |\n"
                  "|---|---|---|---|---|---|---|---|")
            for k in IT_TABLE:
                row = v["by_iteration"].get(str(k))
                if row is None:
                    continue

                def cell(s):
                    sd = f" ± {s['sd']:.3f}" if s["sd"] is not None else ""
                    return f"{s['mean']:.3f}{sd} [{s['min']:.3f}, {s['max']:.3f}]"
                print(f"| {k} | {cell(row['aggregate'])} | {cell(row['low_acceptance'])} | "
                      f"{cell(row['moderate'])} | {cell(row['good'])} | "
                      f"{row['pull_aggregate']['mean']:.3f} | "
                      f"{row['overshoot_projection']['mean']:.3f} | "
                      f"{row['step1_reco_eavail7']['mean']:.3f} |")


if __name__ == "__main__":
    main()
