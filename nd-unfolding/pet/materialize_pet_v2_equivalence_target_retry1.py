#!/usr/bin/env python3
"""Changed-retry wrapper for the frozen PET-v2 target operand."""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from pet_v2_equivalence_root_remap import run_original  # noqa: E402


if __name__ == "__main__":
    run_original("materialize_pet_v2_equivalence_target.py")
