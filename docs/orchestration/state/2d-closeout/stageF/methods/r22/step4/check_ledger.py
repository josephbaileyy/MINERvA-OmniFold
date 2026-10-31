#!/usr/bin/env python3
"""Check r22 Step 4's ledger: step2/check_ledger.py, run with this round's base and ledger (STEP4-PLAN.md section 3).

The checks are step2/check_ledger.py's, unchanged (one implementation; see its docstring). Step 4 sets the base
4121f185d60d (origin/main at the round's start), no abstract pair, and the ledger default step4/ledger.md.
usage: as step2/check_ledger.py (--files, --list, --self-test, --no-n4-frozen)."""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("check_ledger2", HERE.parent / "step2" / "check_ledger.py")
cl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cl)
BASE = "4121f185d60d"
cl.ABSTRACT = []
cl.ABSTRACT_PINS = {}
if __name__ == "__main__":
    args = sys.argv[1:]
    if "--base" not in args:
        args += ["--base", BASE]
    if "--ledger" not in args:
        args += ["--ledger", str(HERE / "ledger.md")]
    sys.argv = [sys.argv[0]] + args
    sys.exit(cl.main())
