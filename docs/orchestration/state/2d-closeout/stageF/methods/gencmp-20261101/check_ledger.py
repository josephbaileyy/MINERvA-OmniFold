#!/usr/bin/env python3
"""Check the GENCMP paper round's ledger: r22/step2/check_ledger.py, run with this round's base, ledger and batch.

The checks are step2/check_ledger.py's (one implementation; see its docstring). This round sets:
  - the base dfa137370 (origin/main after #651, DECISION-20261101-joseph-gencmp-paper-adoption.md);
  - the ledger default gencmp-20261101/ledger.md;
  - the batch with paper_body.tex (prefix PB) and primer_body.tex (prefix PM) added, so every paper and primer sentence
    the round changes must be named by a row;
  - PROTECTED without the files the decision's items 1-4 and 6 change: paper_body.tex (:42, :232, Table IV, the ratio
    figure's caption, the sensitivity paragraph) and values_fived16.tex (generated, --check). main_paper.tex and
    main_note.tex stay byte-identical, so ABSTRACT is empty: the abstracts' numbers follow Table IV through \\fvval
    (director's ruling 2 of 2026-11-01), with no word changed;
  - REMOVED_LABELS empty: no label is removed.
usage: as step2/check_ledger.py (--files, --list, --self-test, --no-n4-frozen)."""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("check_ledger2", HERE.parent / "r22" / "step2" / "check_ledger.py")
cl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cl)
BASE = "dfa137370"
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
