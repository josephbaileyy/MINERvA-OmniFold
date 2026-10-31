#!/usr/bin/env python3
"""Check paper pass 3's ledger: step2p/check_paper.py, run with this pass's base and ledger (STEP2-PAPER.md section 6).

The checks are check_paper.py's, unchanged (one implementation; see its docstring). Pass 3 sets the base 4121f185d60d
(origin/main at the pass's start, which already holds pass 2's two Joseph pairs, so PAIRS is empty: main_paper.tex
must be byte-identical to the base) and the ledger default step2p/pass3/ledger.md. Option B's caption is held by that
ledger's P:: probe of its full text, since PAIRS covers main_paper.tex only.
After adoption (section 6.2; pass3/runs/adoption.tsv), only the rows of the decided change (i), Option B, are checked
when the three gaps were not adopted (ADOPT NO): the paper then is BASE' and the gap rows assert NEW's text.
--all-rows checks every row, as on NEW (1405c8a3).
usage: as check_paper.py (--list, --self-test), plus --all-rows."""
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
OPTION_B_ROWS = {"P3-1"}


def adopted():
    rows = [l.split("\t") for l in (HERE / "runs" / "adoption.tsv").read_text().splitlines()]
    return rows[1][rows[0].index("ADOPT")] == "YES"


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--all-rows" in args:
        args.remove("--all-rows")
    elif (HERE / "runs" / "adoption.tsv").exists() and not adopted():
        all_rows = cp.rows
        cp.rows = lambda text: (r for r in all_rows(text) if not r[0].startswith("P3-") or r[0] in OPTION_B_ROWS)
        print("pass 3 not adopted (runs/adoption.tsv): checking Option B's rows only")
    if "--base" not in args:
        args += ["--base", BASE]
    if "--ledger" not in args:  # the self-test too: its KEEP plant strips this ledger's F-ids
        args += ["--ledger", str(HERE / "ledger.md")]
    sys.argv = [sys.argv[0]] + args
    sys.exit(cp.main())
