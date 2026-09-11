"""Apply the frozen synthetic comparison criteria to a complete paired matrix."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import t  # type: ignore[import-untyped]

SEEDS = (17, 29, 43, 59, 71, 89, 101, 113)


def summarize(directory: Path) -> dict[str, Any]:
    """Verify all receipts/artifacts and calculate paired seed confidence limits."""
    reference = None
    gains = []
    checks: dict[str, bool] = {}
    for mode in ("ordinary", "injected", "shuffle"):
        for seed in SEEDS:
            name = f"{mode}-{seed}"
            receipt = json.loads((directory / f"{name}.json").read_text())
            if (
                receipt["terminal"],
                receipt["mode"],
                receipt["seed"],
                receipt["training_rows"],
                receipt["test_rows"],
                receipt["iterations"],
                receipt["epochs_per_fit"],
                receipt["batch_size"],
            ) != ("COMPLETE", mode, seed, 1000000, 250000, 3, 5, 1024):
                raise ValueError(f"Incomplete or mismatched run: {name}")
            footing = [
                receipt[key]
                for key in (
                    "code_sha256",
                    "input_sha256",
                    "truth_sha256",
                    "normalization_sha256",
                )
            ]
            if reference is None:
                reference = footing
            elif footing != reference:
                raise ValueError(f"Mismatched common footing: {name}")
            if len(receipt["artifacts"]) != 6:
                raise ValueError(f"Missing artifacts: {name}")
            for filename, expected in receipt["artifacts"].items():
                path = directory / filename
                if (
                    path.parent != directory
                    or hashlib.sha256(path.read_bytes()).hexdigest() != expected
                ):
                    raise ValueError(f"Artifact mismatch: {filename}")
            pooled, direct = [
                receipt["results"][route] for route in ("pooled", "direct")
            ]
            for key in ("parameters", "initial_reco_sha256", "initial_truth_sha256"):
                if pooled[key] != direct[key]:
                    raise ValueError(f"Unmatched initial model: {name}/{key}")
            parent, child = [arm["iterations"][-1] for arm in (pooled, direct)]
            if mode == "injected":
                if parent["log_ratio_rmse"] <= 0:
                    raise ValueError(
                        "Parent RMSE is zero: relative improvement undefined"
                    )
                gains.append(
                    100
                    * (parent["log_ratio_rmse"] - child["log_ratio_rmse"])
                    / parent["log_ratio_rmse"]
                )
                checks[name + "/absolute_recovery"] = child["log_ratio_rmse"] <= 0.10
            else:
                checks[name + "/control"] = (
                    all(
                        m["log_ratio_rmse"] <= 0.10
                        and abs(m["normalization_ratio"] - 1) <= 0.02
                        for m in (parent, child)
                    )
                    and child["log_ratio_rmse"] - parent["log_ratio_rmse"] <= 0.02
                )
            for metric, expected in (
                ("ess", "target_ess"),
                ("tail_ess", "tail_target_ess"),
            ):
                checks[name + "/" + metric] = child[metric] / parent[
                    metric
                ] >= 0.90 and all(
                    abs(m[metric] / m[expected] - 1) <= 0.10 for m in (parent, child)
                )
            for axis in ("0", "1"):
                errors = [
                    m["truth_projections"][axis]["relative_l1"] for m in (parent, child)
                ]
                checks[name + "/projection" + axis] = (
                    max(errors) <= 0.05 and errors[1] - errors[0] <= 0.01
                )
            checks[name + "/caps"] = all(
                cap["count"] == 0 and abs(cap["ess"] / m["ess"] - 1) < 0.01
                for m in (parent, child)
                for cap in m["cap_diagnostics"].values()
            )
    mean = float(np.mean(gains))
    half_width = float(t.ppf(0.975, 7) * np.std(gains, ddof=1) / np.sqrt(8))
    checks["favorable_seeds"] = sum(gain > 0 for gain in gains) >= 7
    checks["material_paired_gain"] = mean - half_width > 5
    return {
        "scope": "synthetic routing only; no adoption or uncertainty authority",
        "paired_improvement_percent": gains,
        "paired_mean_95_percent_interval": [mean - half_width, mean + half_width],
        "checks": checks,
        "decision": "PASS_SYNTHETIC_ROUTING" if all(checks.values()) else "NO_PASS",
        "interpretation": "NO_PASS may be inconclusive or fail a safeguard; it is not proof of inferiority",
    }


def main() -> None:
    """Print the frozen comparison result, failing closed on incomplete inputs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    print(json.dumps(summarize(args.directory), indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
