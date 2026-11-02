#!/usr/bin/env python3
"""Check the GENCMP amendment E paper round's ledger: r22/step2/check_ledger.py, run with this round's base, ledger and batch.

The checks are step2/check_ledger.py's (one implementation; see its docstring). This round sets:
  - the base a4cd6ffcf (origin/main after #662, FD-GENCMP-AMENDMENT-E-REPORT.md, whose section 8 row "E-1 completes"
    applies);
  - the ledger default gencmp-e-20261101/ledger.md;
  - the batch with paper_body.tex (prefix PB) and primer_body.tex (prefix PM) added, as in the GENCMP round;
  - PROTECTED without paper_body.tex (the scoping sentence of the sensitivity paragraph goes) and values_fived16.tex
    (generated, --check). main_paper.tex and main_note.tex stay byte-identical, so ABSTRACT is empty;
  - REMOVED_LABELS empty: no label is removed.
usage: as step2/check_ledger.py (--files, --list, --self-test, --no-n4-frozen)."""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("check_ledger2", HERE.parent / "r22" / "step2" / "check_ledger.py")
cl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cl)
BASE = "a4cd6ffcf"
cl.PREFIX["paper_body.tex"] = "PB"
cl.PREFIX["primer_body.tex"] = "PM"
# the id pattern is compiled from PREFIX at import, so it is rebuilt here with PB and PM in it
cl.IDRX = cl.re.compile(r"\b(" + "|".join(sorted(cl.PREFIX.values(), key=len, reverse=True)) + r")\d+\b")
cl.PROTECTED = [p for p in cl.PROTECTED if p not in ("values_fived16.tex", "paper_body.tex")]
cl.REMOVED_LABELS = {}
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
