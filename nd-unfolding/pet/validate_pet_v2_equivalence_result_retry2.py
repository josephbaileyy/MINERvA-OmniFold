#!/usr/bin/env python3
"""Read-only retry-2 validator using the unchanged retry-1 validation implementation."""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import validate_pet_v2_equivalence_result_retry1 as validator  # noqa: E402


validator.SCHEMA = "pet-v2-equivalence-changed-retry2-independent-readback-v1"
validator.RETRY_CONTRACT_ID = "PET-V2-FIXED-DRAW-EQUIVALENCE-CHANGED-RETRY2-20260826"


if __name__ == "__main__":
    raise SystemExit(validator.main())
