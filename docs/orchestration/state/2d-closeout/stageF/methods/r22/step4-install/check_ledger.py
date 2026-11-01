#!/usr/bin/env python3
"""Check r22 Step 4 part 2's ledger (the figure restyle's install): r22/step2/check_ledger.py, with this round's base.

The checks are step2/check_ledger.py's, unchanged (one implementation; see its docstring). Part 2 sets the base
70eaad8fc (origin/main after BINDING-A2.md, #621; the install branch is built on #624's run-a2 commits, which change
no note source), no abstract pair, and the ledger default step4-install/ledger.md. PROTECTED keeps the paper and the
values files byte-identical.
usage: as step2/check_ledger.py (--files, --list, --self-test, --no-n4-frozen)."""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("check_ledger2", HERE.parent / "step2" / "check_ledger.py")
cl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cl)
BASE = "70eaad8fc"
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
