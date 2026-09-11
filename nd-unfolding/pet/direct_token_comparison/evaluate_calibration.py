"""Check calibration integrity and conservatively extrapolate the frozen matrix."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import pstats
from typing import Any


def evaluate(
    directory: Path, elapsed_seconds: int, prior_allocation_seconds: int
) -> dict[str, Any]:
    """Require closed calibration evidence before evaluating the resource gates.

    ``elapsed_seconds`` is the completed allocation's Slurm ElapsedRaw, not the
    Python process time. Call only after verifying COMPLETED and ExitCode 0:0.
    """
    if elapsed_seconds <= 0 or prior_allocation_seconds < 0:
        raise ValueError("Completed allocation accounting is required")
    if (directory / "terminal.txt").read_text().strip() != "COMPLETE":
        raise ValueError("Calibration did not complete")
    if (directory / "exit-code.txt").read_text().strip() != "0":
        raise ValueError("Calibration process failed")
    if "49 passed, 10 subtests passed" not in (directory / "tests.log").read_text():
        raise ValueError("Cluster test scope did not pass completely")
    for name in ("tests-guard.json", "guard.json"):
        records = [
            json.loads(line) for line in (directory / name).read_text().splitlines()
        ]
        if not records:
            raise ValueError(f"Missing guard evidence: {name}")
        for record in records:
            if record["verdict"] != "REPOSITORY-ORIGINS-INSPECTED" or record["allow"]:
                raise ValueError(f"Guard refusal or allowance: {name}")
    measured = directory / "measurement"
    run = json.loads((measured / "calibration.json").read_text())
    usage = json.loads((measured / "measurement.json").read_text())
    if (
        run["terminal"],
        run["mode"],
        run["seed"],
        run["training_rows"],
        run["test_rows"],
        run["iterations"],
        run["epochs_per_fit"],
        run["batch_size"],
    ) != ("COMPLETE", "injected", 17, 32768, 8192, 1, 1, 1024):
        raise ValueError("Calibration does not match the frozen run card")
    for name, digest in run["code_sha256"].items():
        source = Path(__file__).resolve().parents[1] / name
        if hashlib.sha256(source.read_bytes()).hexdigest() != digest:
            raise ValueError(f"Scientific code mismatch: {name}")
    if len(run["artifacts"]) != 6:
        raise ValueError("Missing calibration artifacts")
    for name, digest in run["artifacts"].items():
        if Path(name).name != name:
            raise ValueError("Artifact path escapes calibration")
        if hashlib.sha256((measured / name).read_bytes()).hexdigest() != digest:
            raise ValueError(f"Artifact hash mismatch: {name}")
    pooled, direct = (run["results"][route] for route in ("pooled", "direct"))
    for key in ("parameters", "initial_reco_sha256", "initial_truth_sha256"):
        if pooled[key] != direct[key]:
            raise ValueError(f"Paired initialization mismatch: {key}")
    fit_seconds = sum(
        arm["iterations"][0][key]
        for arm in (pooled, direct)
        for key in ("reco_fit_seconds", "truth_fit_seconds")
    )
    stats: Any = pstats.Stats(str(measured / "calibration.pstats"))
    inference_seconds = sum(
        value[3]
        for key, value in stats.stats.items()
        if Path(key[0]).name == "run_typed_token_comparison.py"
        and key[2] == "predict_ratio"
    )
    if inference_seconds <= 0:
        raise ValueError("Separate inference timing is missing")
    other_seconds = run["wall_seconds"] - fit_seconds - inference_seconds
    if other_seconds < 0 or run["wall_seconds"] > elapsed_seconds:
        raise ValueError("Inconsistent timing/accounting")
    # Round up partial batches. Scale every non-fit/non-inference second with
    # rows as well, including fixed initialization, serialization and profiling.
    train_scale = math.ceil(1000000 / 1024) / math.ceil(32768 / 1024)
    test_scale = math.ceil(250000 / 1024) / math.ceil(8192 / 1024)
    row_scale = max(train_scale, test_scale)
    job_seconds = (
        fit_seconds * train_scale * 15
        + inference_seconds * row_scale * 3
        + other_seconds * row_scale
        + elapsed_seconds
        - run["wall_seconds"]
    )
    host_GiB = usage["peak_rss_KiB"] * row_scale / 1024**2
    output_bytes = sum(p.stat().st_size for p in directory.rglob("*") if p.is_file())
    job_GiB = output_bytes * row_scale / 1024**3
    # Reserve 6 GiB for the measured 4.87-GiB runtime, code and small receipts.
    working_GiB = 6 + output_bytes / 1024**3 + 24 * job_GiB
    campaign_gpu_hours = 24 * job_seconds / 3600
    charged_seconds = elapsed_seconds + prior_allocation_seconds
    remaining_gpu_hours = 290 - charged_seconds / 3600
    checks = {
        "per_job_time_20pct_headroom": job_seconds <= 0.8 * 12 * 3600,
        "campaign_gpu_20pct_headroom": campaign_gpu_hours <= 0.8 * remaining_gpu_hours,
        "campaign_cpu_20pct_headroom": campaign_gpu_hours * 32
        <= 0.8 * (9296 - 16 - charged_seconds / 3600 * 32),
        "host_memory_20pct_headroom": host_GiB <= 0.8 * 56,
        "per_job_storage_20pct_headroom": job_GiB <= 0.8 * 4,
        "working_storage_20pct_headroom": working_GiB <= 0.8 * 100,
        "total_storage_20pct_headroom": working_GiB * 2 <= 0.8 * 200,
    }
    return {
        "decision": "PASS" if all(checks.values()) else "STOP",
        "checks": checks,
        "measured": {
            "allocation_seconds": elapsed_seconds,
            "prior_allocation_seconds": prior_allocation_seconds,
            "total_charged_seconds": charged_seconds,
            "fit_seconds": fit_seconds,
            "inference_seconds": inference_seconds,
            "other_seconds": other_seconds,
            "peak_rss_KiB": usage["peak_rss_KiB"],
            "output_bytes": output_bytes,
        },
        "extrapolated": {
            "job_hours": job_seconds / 3600,
            "campaign_gpu_hours": campaign_gpu_hours,
            "campaign_reserved_cpu_hours": campaign_gpu_hours * 32,
            "host_GiB": host_GiB,
            "job_GiB": job_GiB,
            "working_GiB": working_GiB,
        },
        "method": "Upper batch-count scaling; training x15, inference x3; fixed process memory and all other overhead also scaled with rows. Measured GPU batch peak retained separately; batch size is unchanged.",
        "non_claim": "Resource/integrity gate only; calibration learning scores do not enter this decision.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--allocation-seconds", type=int, required=True)
    parser.add_argument("--prior-allocation-seconds", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = evaluate(
        args.directory, args.allocation_seconds, args.prior_allocation_seconds
    )
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
