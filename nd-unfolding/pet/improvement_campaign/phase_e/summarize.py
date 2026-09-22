"""Merge the Phase-E job outputs on scratch into the committed `phase_e/results/` files.

The jobs write one file per array task under the task directory; this reads them, trims what is
per-iteration bulk, and writes the machine-readable results that travel with the repository:

    results/identifiability.json      every distortion's AUC statistic, null and L1 distances
    results/references.json           every case x replicate: IBU (both miss-handling modes) and
                                      GBDT OmniFold recovery at every k, the per-bin residual at
                                      k = 3 and k = 10, and the across-replicate mean/sd
    results/reference_assessment.json pool-S references at the historical size and at 8x
    results/toy_reference.json        the known-function toy
    results/prepare.json              the input census, D3 standardization and pool digests
    results/d5_rebuild_check.json     the committed D5 tables rebuilt from the canonical files
    results/summary.json              every file's sha256 and the headline tables

Every value keeps its ingredients: inputs and their sha256s, the replicate draw digests, the pool,
the sample sizes, the distortion content hash and the commit.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

import common as cm

scm = cm.scm
FULL_AT = (3, 10)


def _trim_iterations(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for r in rows:
        row = {k: r[k] for k in ("iteration", "recovery", "recovery_by_region",
                                 "overshoot_projection") if k in r}
        if r["iteration"] in FULL_AT:
            full = r.get("full")
            if full is not None:
                row["signed_residual_per_bin"] = full["signed_residual_per_bin"]
                row["injected_per_bin"] = full["injected_per_bin"]
                row["regions"] = {k: {kk: v[kk] for kk in ("recovery", "injected_l1", "residual_l1")}
                                  for k, v in full["regions"].items()}
            for extra in ("spurious", "joint", "step1_reco_eavail7_recovery"):
                if extra in r:
                    row[extra] = r[extra]
        out.append(row)
    return out


def merge_references(files: list[Path]) -> dict[str, Any]:
    merged: dict[str, Any] = {"schema": "phase-e-references-merged/1", "cases": {}, "sources": []}
    for path in sorted(files):
        payload = json.loads(path.read_text())
        merged["sources"].append({"path": str(path), "sha256": scm.sha256_file(path),
                                  "commit": payload["commit"], "replicate": payload["replicate"],
                                  "chunk": payload["chunk"], "seconds": payload["seconds"],
                                  "environment": payload["environment"]})
        merged.setdefault("design", payload["design"])
        merged.setdefault("inputs", payload["inputs"])
        merged.setdefault("historical_sources", payload.get("historical_sources"))
        for name, res in payload["results"].items():
            entry = merged["cases"].setdefault(name, {"case": res["case"],
                                                      "content_hash": res["content_hash"],
                                                      "predeclared": res.get("predeclared", True),
                                                      "replicates": {}})
            rep = {"truth_distortion": res.get("truth_distortion"),
                   "reco_distortion": res.get("reco_distortion"),
                   "pseudodata_weight_summary": res.get("pseudodata_weight_summary"),
                   "moved_reco_cells": res.get("moved_reco_cells"),
                   "reco_eavail_mean_ratio": res.get("reco_eavail_mean_ratio"),
                   "target_aggregate_hist": res["target"]["aggregate_hist"],
                   "ibu": {mode: {"best": v["best"], "iterations": _trim_iterations(v["iterations"])}
                           for mode, v in res["ibu"].items()},
                   "gbdt_omnifold": {"seed": res["gbdt_omnifold"]["seed"],
                                     "iterations": _trim_iterations(
                                         res["gbdt_omnifold"]["iterations"])},
                   "seconds": res["seconds"]}
            entry["replicates"][str(payload["replicate"])] = rep
    return merged


def across_replicates(merged: dict[str, Any]) -> dict[str, Any]:
    """Mean and sd over replicates of the aggregate and regional recovery at k = 3, 10 and best."""
    out: dict[str, Any] = {}
    for name, entry in merged["cases"].items():
        row: dict[str, Any] = {}
        reps = entry["replicates"]
        for est in ("ibu/carry_misses", "ibu/efficiency_corrected", "gbdt_omnifold"):
            vals: dict[str, list[float]] = {"k3": [], "k10": [], "best": [], "best_k": []}
            regions: dict[str, dict[str, list[float]]] = {}
            for rep in reps.values():
                if est.startswith("ibu/"):
                    node = rep["ibu"].get(est.split("/", 1)[1])
                else:
                    node = rep.get(est)
                if node is None:
                    continue
                its = node["iterations"]
                by_k = {r["iteration"]: r for r in its}
                for k, key in ((3, "k3"), (10, "k10")):
                    if k in by_k:
                        vals[key].append(by_k[k]["recovery"])
                        for rname, rv in by_k[k]["recovery_by_region"].items():
                            regions.setdefault(key, {}).setdefault(rname, []).append(rv)
                best = max(its, key=lambda r: r["recovery"])
                vals["best"].append(best["recovery"])
                vals["best_k"].append(best["iteration"])
            row[est] = {k: ({"mean": float(np.mean(v)),
                             "sd": float(np.std(v, ddof=1)) if len(v) > 1 else None,
                             "values": v} if v else None) for k, v in vals.items()}
            row[est]["regions"] = {k: {rn: {"mean": float(np.mean(rv)),
                                            "sd": float(np.std(rv, ddof=1)) if len(rv) > 1 else None}
                                       for rn, rv in d.items()} for k, d in regions.items()}
        out[name] = row
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--task-dir", type=Path, required=True, help="the Perlmutter phaseE1 directory")
    ap.add_argument("--results-dir", type=Path, default=Path(__file__).resolve().parent / "results")
    args = ap.parse_args()
    args.results_dir.mkdir(parents=True, exist_ok=True)
    written: dict[str, Any] = {}

    refs = sorted(args.task_dir.glob("references/references_r*_c*.json"))
    if refs:
        merged = merge_references(refs)
        merged["across_replicates"] = across_replicates(merged)
        cm.write_json(args.results_dir / "references.json", merged)
    for name, pattern in (("identifiability", "identifiability/identifiability.json"),
                          ("reference_assessment", "assessment/reference_assessment.json"),
                          ("toy_reference", "toy/toy_reference.json"),
                          ("d5_rebuild_check", "d5check/d5_rebuild_check.json"),
                          ("prepare", "prep/prepare.json")):
        src = args.task_dir / pattern
        if src.exists():
            cm.write_json(args.results_dir / f"{name}.json", json.loads(src.read_text()))
    for path in sorted(args.results_dir.glob("*.json")):
        if path.name != "summary.json":
            written[path.name] = {"sha256": scm.sha256_file(path), "bytes": path.stat().st_size}
    cm.write_json(args.results_dir / "summary.json",
                  {"schema": "phase-e-summary/1", "commit": scm.repo_commit(), "files": written,
                   "scope": ("simulation-only Phase-E results; PET is diagnostic method "
                             "development; no value here is a threshold, a bound or an adoption")},
                  compact=False)
    print(json.dumps({k: v["bytes"] for k, v in written.items()}, indent=1))


if __name__ == "__main__":
    main()
