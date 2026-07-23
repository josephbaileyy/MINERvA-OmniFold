#!/usr/bin/env python3
"""Report or verify the isolated PET2 runtime without importing ROOT/TF."""

from __future__ import annotations

import argparse
import json

from .utils import environment_receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-delta", action="store_true")
    args = parser.parse_args()
    receipt = environment_receipt()
    problems = []
    if args.require_delta:
        if receipt.get("torch") is None:
            problems.append("PyTorch is absent")
        elif not str(receipt["torch"]).split("+")[0].startswith("2.8."):
            problems.append(f"PyTorch {receipt['torch']} is not the module-locked 2.8 series")
        if receipt.get("safetensors") != "0.5.3":
            problems.append(
                f"safetensors {receipt.get('safetensors')} != package lock 0.5.3"
            )
        if not receipt.get("cuda_available"):
            problems.append("CUDA is unavailable")
    receipt["verification"] = {
        "mode": "delta" if args.require_delta else "report_only",
        "status": "pass" if not problems else "fail",
        "problems": problems,
    }
    print(json.dumps(receipt, sort_keys=True))
    return 0 if not problems else 2


if __name__ == "__main__":
    raise SystemExit(main())
