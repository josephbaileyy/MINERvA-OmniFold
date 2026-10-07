"""Summarize committed representation evidence without opening detector sources."""

from __future__ import annotations

import gzip
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
BASE = "57b707b737ce817c1ef8d8bd0f0a39ce4becb7ba"
TAG = "evidence/prepublication-excluded-gregor-b65f9ff2"


def read_product(revision: str, path: str) -> tuple[dict[str, Any], str]:
    """Read and hash the exact preserved Git object, decompressing if necessary."""
    payload = subprocess.check_output(["git", "show", f"{revision}:{path}"], cwd=ROOT)
    if path.endswith(".gz"):
        payload = gzip.decompress(payload)
    return json.loads(payload), hashlib.sha256(payload).hexdigest()


def main() -> None:
    """Print derived counts and verify historical per-seed receipt hashes."""
    audit = "nd-unfolding/pet/source_audit_runs/20260910-repaired/audit/"
    telemetry, telemetry_hash = read_product(BASE, audit + "telemetry-summary.json.gz")
    receipt, receipt_hash = read_product(BASE, audit + "receipt.json.gz")
    fixed, fixed_hash = read_product(
        BASE,
        "docs/orchestration/runs/"
        "pet-typed-semantic-evidence-20260901/fixed-sample-telemetry.json",
    )
    roles = {}
    for role in ("data", "mc"):
        prefix = f"{role}/extension_16_4096/"
        histogram = telemetry["histograms"]
        pid: dict[str, int] = {}
        for position in ("zero", "later"):
            for code, count in histogram[prefix + "pid/" + position].items():
                pid[code] = pid.get(code, 0) + count
        roles[role] = {
            "rows": 4080,
            "prongs": sum(pid.values()),
            "pid_counts": pid,
            "pid_filter_lower_bound": pid.get("-999", 0) + pid.get("0", 0),
            "masked_dedx": histogram[prefix + "prong_valid_missing/dedx"]["[false]"],
            "masked_mass": histogram[prefix + "prong_valid_missing/mass"]["[false]"],
            "prong_zero_lepton_match": histogram[prefix + "lepton_match/zero"],
            "time_check": receipt["correspondence_checks"][f"{role}/extension_16_4096"][
                "prong_time"
            ],
            "fixed_16_blob_counts": fixed["families"]["blobs"]["counts"][role],
        }
    path = "nd-unfolding/pet2_torch/products/conditional_stress/recovery_job20441096/aggregate.json"
    aggregate, aggregate_hash = read_product(TAG, path)
    historical = {}
    for family, content in aggregate["families"].items():
        signal = content["modes"]["signal"]
        verified = []
        for run in signal["runs"]:
            for arm in ("parent", "enriched"):
                relative = (
                    "nd-unfolding/"
                    + run[arm]["receipt_path"].split("/nd-unfolding/", 1)[1]
                )
                _, sha = read_product(TAG, relative)
                if sha != run[arm]["receipt_sha256"]:
                    raise ValueError(f"Historical receipt mismatch: {relative}")
                verified.append({"path": relative, "sha256": sha})
        historical[family] = {
            "improvement_percent": signal["comparison"],
            "gate_pass": signal["gates"]["pass"],
            "verified_receipts": verified,
        }
    print(
        json.dumps(
            {
                "base": BASE,
                "source_receipt_sha256": receipt_hash,
                "telemetry_sha256": telemetry_hash,
                "fixed_sample_sha256": fixed_hash,
                "extension": roles,
                "historical_tag": TAG,
                "historical_aggregate_sha256": aggregate_hash,
                "historical_signal": historical,
                "scope": "Derived from committed convenience-sample and synthetic receipts; no new source measurement",
            },
            indent=2,
            allow_nan=False,
        )
    )


if __name__ == "__main__":
    main()
