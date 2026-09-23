"""Build the B2 tables from the committed result files (local; no cluster access needed).

Reads `results/*.scores.json` (unfold runs, written by `b2_score.py`), `results/*.truth_only.json`
(the truth-only receipts of `b2_driver.py --mode truth_only`) and `results/truth_scalar_ref.json`
(T3), and writes `results/summary.json` (every input file with its sha256, and the tabulated
numbers) while printing the markdown tables used in `PET_DIAGNOSTICS-20260922.md`.

Run groups come from the file names: `<arm>-s<seed>.scores.json`, e.g. `b2e3-H-K10-s1`.
"""

from __future__ import annotations

import hashlib
import json
import re
import statistics
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
REGIONS = ("low_acceptance", "moderate", "good")
K_SHOW = (1, 2, 3, 4, 5, 8, 10, 12, 15, 16, 20)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def fmt(x: Any, nd: int = 3) -> str:
    return "—" if x is None else f"{x:.{nd}f}"


def stats(values: list[float]) -> dict[str, Any]:
    values = [v for v in values if v is not None]
    if not values:
        return {"n": 0}
    return {"n": len(values), "mean": statistics.fmean(values),
            "sd": statistics.stdev(values) if len(values) > 1 else 0.0,
            "min": min(values), "max": max(values), "values": values}


def cell(values: list[float]) -> str:
    s = stats(values)
    if not s["n"]:
        return "—"
    return f"{s['mean']:.3f}" + (f" ± {s['sd']:.3f}" if s["n"] > 1 else "")


def load_unfold() -> dict[str, dict[int, dict[str, Any]]]:
    """{arm: {seed: scores}} from results/<arm>-s<seed>.scores.json."""
    runs: dict[str, dict[int, Any]] = {}
    for path in sorted(RESULTS.glob("*.scores.json")):
        name = path.name[: -len(".scores.json")]
        match = re.match(r"(.+)-s(\d+)$", name)
        if not match:
            continue
        arm, seed = match.group(1), int(match.group(2))
        runs.setdefault(arm, {})[seed] = {"path": path, "sha256": sha256(path),
                                          "data": json.loads(path.read_text())}
    return runs


def by_k(run: dict[str, Any]) -> dict[int, dict[str, Any]]:
    return {r["k"]: r for r in run["data"]["iterations"]}


def table_recovery(runs: dict[str, dict[int, Any]]) -> tuple[str, dict[str, Any]]:
    ks = sorted({r["k"] for arm in runs.values() for run in arm.values()
                 for r in run["data"]["iterations"]} & set(K_SHOW))
    lines = ["| arm (seeds) | " + " | ".join(f"k={k}" for k in ks) + " |",
             "|---|" + "---|" * len(ks)]
    payload: dict[str, Any] = {}
    for arm, seeds in sorted(runs.items()):
        row, record = [], {}
        for k in ks:
            values = [by_k(run).get(k, {}).get("push", {}).get("recovery")
                      for run in seeds.values()]
            record[k] = stats([v for v in values if v is not None])
            row.append(cell([v for v in values if v is not None]))
        lines.append(f"| `{arm}` ({len(seeds)}) | " + " | ".join(row) + " |")
        payload[arm] = record
    return "\n".join(lines), payload


def table_regions(runs: dict[str, dict[int, Any]], k: int) -> str:
    lines = [f"| arm | k | aggregate | " + " | ".join(REGIONS) + " | overshoot |",
             "|---|---|---|" + "---|" * (len(REGIONS) + 1)]
    for arm, seeds in sorted(runs.items()):
        rows = [by_k(run).get(k) for run in seeds.values()]
        rows = [r for r in rows if r]
        if not rows:
            continue
        agg = cell([r["push"]["recovery"] for r in rows])
        regs = [cell([r["push"]["recovery_by_region"][name] for r in rows]) for name in REGIONS]
        over = cell([r["push"]["aggregate"]["overshoot_projection"] for r in rows])
        lines.append(f"| `{arm}` | {k} | {agg} | " + " | ".join(regs) + f" | {over} |")
    return "\n".join(lines)


def table_steps(runs: dict[str, dict[int, Any]], arm: str) -> str:
    seeds = runs[arm]
    ks = sorted({r["k"] for run in seeds.values() for r in run["data"]["iterations"]})
    names = ["reco_eavail_7", "muon_cells", "reco_pt", "reco_pparallel",
             "stored_sumE_deciles", "stored_n"]
    lines = ["| k | push | pull | " + " | ".join(f"step1 {n}" for n in names) +
             " | pull(acc) | push(acc) | push(miss) | ESS/n | push p99.9 |",
             "|---|" + "---|" * (len(names) + 8)]
    for k in ks:
        rows = [by_k(run).get(k) for run in seeds.values()]
        rows = [r for r in rows if r and "step1_detector" in r]
        if not rows:
            continue
        det = [cell([r["step1_detector"][n]["recovery"] for r in rows]) for n in names]
        pv = cell([r["pulled_vs_pushed"]["accepted"]["pull"]["recovery"] for r in rows])
        pa = cell([r["pulled_vs_pushed"]["accepted"]["push"]["recovery"] for r in rows])
        pm = cell([r["pulled_vs_pushed"]["misses"]["push"]["recovery"] for r in rows])
        ess = cell([r["final_truth_weights_ess"]["ess"] / r["final_truth_weights_ess"]["n"]
                    for r in rows])
        tail = cell([r["push_weights_on_truth_passing"]["p99.9"] for r in rows])
        lines.append(f"| {k} | {cell([r['push']['recovery'] for r in rows])} | "
                     f"{cell([r['pull']['recovery'] for r in rows])} | " + " | ".join(det) +
                     f" | {pv} | {pa} | {pm} | {ess} | {tail} |")
    return "\n".join(lines)


def load_truth_only() -> dict[str, dict[int, Any]]:
    out: dict[str, dict[int, Any]] = {}
    for path in sorted(RESULTS.glob("*.truth_only.json")):
        name = path.name[: -len(".truth_only.json")]
        match = re.match(r"(.+)-s(\d+)$", name)
        if not match:
            continue
        out.setdefault(match.group(1), {})[int(match.group(2))] = {
            "path": path, "sha256": sha256(path), "data": json.loads(path.read_text())}
    return out


def truth_only_tables(runs: dict[str, dict[int, Any]]) -> tuple[str, dict[str, Any]]:
    """Learnability (B x ratio vs B x the tilt function) and the endpoint score, per epoch.

    `epoch 8` is the historical fit (8 epochs, last-epoch weights, same rate and seeds);
    `best-val` is the epoch the recipe hands on (minimum validation loss, restore='best');
    `max` is the best epoch BY THE EVALUATION ITSELF -- an oracle selection, shown only to size
    the epoch-to-epoch fluctuation, never a result.
    """
    lines = ["| arm (seeds) | epoch 8 (historical fit) | best-val epoch | at best-val | endpoint at "
             "best-val | low | moderate | good | max over epochs (oracle) |",
             "|---|---|---|---|---|---|---|---|---|"]
    curves: dict[str, Any] = {}
    for arm, seeds in sorted(runs.items()):
        at8, best_ep, best, ep_end, oracle = [], [], [], [], []
        regs: dict[str, list] = {r: [] for r in REGIONS}
        for run in seeds.values():
            epochs = run["data"]["epochs_on_half_b"]
            values = [e.get("learnability", {}).get("aggregate", {}).get("recovery")
                      for e in epochs]
            if not values or None in values:
                continue
            vloss = [e["val_loss"] for e in epochs]
            index = min(range(len(vloss)), key=lambda i: vloss[i])
            at8.append(values[7] if len(values) >= 8 else None)
            best_ep.append(index + 1)
            best.append(values[index])
            oracle.append(max(values))
            ep_end.append(epochs[index]["endpoint"]["recovery"])
            for name in REGIONS:
                regs[name].append(epochs[index]["learnability"]["regions"][name]["recovery"])
            curves.setdefault(arm, {})[run["data"]["config"]["step2"]["seed"]] = {
                "learnability_by_epoch": values,
                "endpoint_by_epoch": [e["endpoint"]["recovery"] for e in epochs],
                "val_loss_by_epoch": vloss, "best_val_epoch": index + 1}
        if not best:
            continue
        lines.append(f"| `{arm}` ({len(best)}) | {cell([v for v in at8 if v is not None])} | "
                     f"{'/'.join(str(e) for e in best_ep)} | {cell(best)} | {cell(ep_end)} | "
                     + " | ".join(cell(regs[name]) for name in REGIONS)
                     + f" | {cell(oracle)} |")
    return "\n".join(lines), curves


def t3_table() -> tuple[str, dict[str, Any]]:
    path = RESULTS / "truth_scalar_ref.json"
    if not path.exists():
        return "", {}
    data = json.loads(path.read_text())
    lines = ["| scalar reference (T3) | learnability | endpoint | low | moderate | good |",
             "|---|---|---|---|---|---|"]
    groups: dict[str, list] = {}
    for r in data["results"]:
        groups.setdefault(f"{r['input_set']} / {r['model']}", []).append(r)
    for key, rows in sorted(groups.items()):
        lines.append(f"| {key} | {cell([r['learnability']['aggregate']['recovery'] for r in rows])}"
                     f" | {cell([r['endpoint']['recovery'] for r in rows])} | "
                     + " | ".join(cell([r["learnability"]["regions"][n]["recovery"]
                                        for r in rows]) for n in REGIONS) + " |")
    return "\n".join(lines), {"sha256": sha256(path), "groups": sorted(groups)}


def main() -> None:
    runs = load_unfold()
    truth = load_truth_only()
    summary: dict[str, Any] = {"schema": "phase-b2-summary/1", "files": {}}
    for arm, seeds in runs.items():
        for seed, run in seeds.items():
            summary["files"][run["path"].name] = run["sha256"]
    for arm, seeds in truth.items():
        for seed, run in seeds.items():
            summary["files"][run["path"].name] = run["sha256"]
    if runs:
        table, payload = table_recovery(runs)
        summary["recovery_by_k"] = payload
        print("\n### Recovery vs iteration (push, mean ± sd over seeds)\n")
        print(table)
        for k in (3, 10):
            print(f"\n### Regions at k = {k}\n")
            print(table_regions(runs, k))
        for arm in sorted(runs):
            if any("step1_detector" in r for run in runs[arm].values()
                   for r in run["data"]["iterations"]):
                print(f"\n### Step-wise closure, `{arm}`\n")
                print(table_steps(runs, arm))
    if truth:
        table, curves = truth_only_tables(truth)
        summary["truth_only"] = curves
        print("\n### Truth-only learnability (step 2 alone, the KNOWN tilt)\n")
        print(table)
    table, t3 = t3_table()
    if table:
        summary["t3"] = t3
        print("\n### T3 scalar references (same protocol)\n")
        print(table)
    (RESULTS / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(f"\nwrote {RESULTS / 'summary.json'}", file=sys.stderr)


if __name__ == "__main__":
    main()
