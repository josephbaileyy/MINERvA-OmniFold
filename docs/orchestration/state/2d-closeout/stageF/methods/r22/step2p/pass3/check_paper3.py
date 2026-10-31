#!/usr/bin/env python3
"""Check paper pass 3's ledger: step2p/check_paper.py, run with this pass's base and ledger (STEP2-PAPER.md section 6).

The checks are check_paper.py's, unchanged (one implementation; see its docstring). Pass 3 sets the base 4121f185d60d
(origin/main at the pass's start, which already holds pass 2's two Joseph pairs, so PAIRS is empty: main_paper.tex
must be byte-identical to the base) and the ledger default step2p/pass3/ledger.md. Option B's caption is held by that
ledger's P:: probe of its full text, since PAIRS covers main_paper.tex only.
usage: as check_paper.py (--list, --self-test)."""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("check_paper", HERE.parent / "check_paper.py")
cp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cp)
BASE = "4121f185d60d"
cp.PAIRS = []
cp.PAIR_PINS = {}
# this base already holds pass 2's A4 pair, so the self-test plants on the pair's new text
cp.SELFTEST_AB = ("Three external generator predictions, compared on all sixteen cells,",
                  "Three external generator predictions, all compared on the sixteen cells,",
                  "Three external generator predictions")
if __name__ == "__main__":
    args = sys.argv[1:]
    if "--base" not in args:
        args += ["--base", BASE]
    if "--ledger" not in args:  # the self-test too: its KEEP plant strips this ledger's F-ids
        args += ["--ledger", str(HERE / "ledger.md")]
    sys.argv = [sys.argv[0]] + args
    sys.exit(cp.main())
