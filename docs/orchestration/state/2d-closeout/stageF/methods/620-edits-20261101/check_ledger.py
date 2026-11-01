#!/usr/bin/env python3
"""Check the 620 round's ledger: r22/step2/check_ledger.py, run with this round's base, ledger and batch.

The checks are step2/check_ledger.py's (one implementation; see its docstring). This round sets:
  - the base c93a73bce (origin/main after #619, #634, #622 and #637);
  - the ledger default 620-edits-20261101/ledger.md;
  - the batch with paper_body.tex added (prefix PB), so every paper sentence that no longer prints verbatim must be named
    by a row: Joseph's four editorial fixes keep every fact (DECISION-20261031-joseph-eavail-switch-pricing-and-edits.md
    item 2), and the rows say where each one now prints;
  - PROTECTED without the files this round changes by decision: paper_body.tex (the four fixes, the departure sentence
    of DECISION-20261101-joseph-eavail-keep-135.md item 2, and the 1B disclosure) and values_fived16.tex (generated,
    --check). main_paper.tex and main_note.tex, with both abstracts, stay byte-identical: ABSTRACT is empty;
  - REMOVED_LABELS: tab:estimators, Table I's, which fix 4 replaces by a paragraph; no source may still reference it.
usage: as step2/check_ledger.py (--files, --list, --self-test, --no-n4-frozen)."""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("check_ledger2", HERE.parent / "r22" / "step2" / "check_ledger.py")
cl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cl)
BASE = "c93a73bce"
cl.PREFIX["paper_body.tex"] = "PB"
# the id pattern is compiled from PREFIX at import, so it is rebuilt here with PB in it
cl.IDRX = cl.re.compile(r"\b(" + "|".join(sorted(cl.PREFIX.values(), key=len, reverse=True)) + r")\d+\b")
cl.PROTECTED = [p for p in cl.PROTECTED if p not in ("values_fived16.tex", "paper_body.tex")]
cl.REMOVED_LABELS = {"paper_body.tex": {"tab:estimators"}}   # Table I, replaced by a paragraph (fix 4)
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
