#!/usr/bin/env python3
"""Check the Stage 0 / R10 round's ledger: r22/step2/check_ledger.py, run with this round's base, ledger and batch.

The checks are step2/check_ledger.py's (one implementation; see its docstring). This round sets:
  - the base 2f62fe4ee (origin/main after #640);
  - the ledger default stage0-r10-20261101/ledger.md;
  - the batch with paper_body.tex added (prefix PB), so the one paper sentence this round changes, the C_model
    sentence that now points to the note's account of Stage 0 and R10, must be named by a row;
  - PROTECTED without the files this round changes by the director's instruction of 2026-11-01 (under
    DECISION-20261024-joseph-5d-community-standard-route.md item 3): paper_body.tex (the pointer) and values_fived16.tex
    (generated, --check). main_paper.tex and main_note.tex, with both abstracts, stay byte-identical: ABSTRACT is empty;
  - REMOVED_LABELS empty: no label is removed.
usage: as step2/check_ledger.py (--files, --list, --self-test, --no-n4-frozen)."""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("check_ledger2", HERE.parent / "r22" / "step2" / "check_ledger.py")
cl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cl)
BASE = "2f62fe4ee"
cl.PREFIX["paper_body.tex"] = "PB"
# the id pattern is compiled from PREFIX at import, so it is rebuilt here with PB in it
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
