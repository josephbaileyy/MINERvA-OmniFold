#!/usr/bin/env python3
"""Check r22 Step 3's note fact ledger: step2/check_ledger.py, run with this round's base, ledger and pairs.

The checks are step2/check_ledger.py's, unchanged (one implementation; see its docstring). Step 3 sets:
  - base 14a0415f, origin/main at the round's start (STEP3-PLAN.md section 2). Its note sources are those the note
    round adopted (#539, f47b1b4a), so Step 2's two abstract pairs are already in the base;
  - ABSTRACT / ABSTRACT_PINS: this round's own pairs (B01-g-07, A4), empty until the director passes the pinned pair
    to Joseph; an unpinned pair allows nothing, so main_note.tex stays byte-identical until then;
  - the ledger default step3/ledger.md.
usage: as step2/check_ledger.py (--files, --list, --self-test, --no-n4-frozen)."""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("check_ledger2", HERE.parent / "step2" / "check_ledger.py")
cl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cl)
BASE = "14a0415f"
# (id, old, new); pin = check_ledger.pin(old, new). Set when Joseph approves a pinned pair.
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
