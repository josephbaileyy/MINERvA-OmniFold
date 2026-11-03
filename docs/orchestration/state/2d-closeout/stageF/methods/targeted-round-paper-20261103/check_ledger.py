#!/usr/bin/env python3
"""Check the targeted paper round's ledger: r22/step2/check_ledger.py, run with this round's base, ledger and batch.

The checks are step2/check_ledger.py's (one implementation; see its docstring). This round sets:
  - the base 7bdd39f69 (origin/main after #727; the round is read under DECISION-20261103-joseph-retire-density-gate.md
    item 3: the over-qualified sentences the PRD-referee read quoted, and III A, IV D's background closure and V C moved
    whole to the note);
  - the ledger default targeted-round-paper-20261103/ledger.md;
  - the batch with paper_body.tex (prefix PB) and primer_body.tex (prefix PM) added, as in the cut-list round;
  - PROTECTED without paper_body.tex (the round's edits) and values_fived16.tex (generated, --check). main_paper.tex and
    main_note.tex stay byte-identical, so ABSTRACT is empty;
  - REMOVED_LABELS: paper_body.tex's sec:uncertainty-status (III A), fig:bkg-residual (Fig. 2, with IV D's closure) and
    sec:central (V C). The note has no labels of these names; the paper's sec:coverage was removed by the cut-list
    round and stays out of the base.
usage: as step2/check_ledger.py (--files, --list, --self-test, --no-n4-frozen)."""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("check_ledger2", HERE.parent / "r22" / "step2" / "check_ledger.py")
cl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cl)
BASE = "7bdd39f69"
cl.PREFIX["paper_body.tex"] = "PB"
cl.PREFIX["primer_body.tex"] = "PM"
# the id pattern is compiled from PREFIX at import, so it is rebuilt here with PB and PM in it
cl.IDRX = cl.re.compile(r"\b(" + "|".join(sorted(cl.PREFIX.values(), key=len, reverse=True)) + r")\d+\b")
cl.PROTECTED = [p for p in cl.PROTECTED if p not in ("values_fived16.tex", "paper_body.tex")]
cl.REMOVED_LABELS = {"paper_body.tex": {"sec:uncertainty-status", "fig:bkg-residual", "sec:central"}}
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
