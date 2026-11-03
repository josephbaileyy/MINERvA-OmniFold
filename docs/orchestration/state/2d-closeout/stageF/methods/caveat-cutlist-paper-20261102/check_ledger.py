#!/usr/bin/env python3
"""Check the caveat cut-list paper round's ledger: r22/step2/check_ledger.py, run with this round's base, ledger and batch.

The checks are step2/check_ledger.py's (one implementation; see its docstring). This round sets:
  - the base 589eb47d0 (origin/main after #706, the cut list; the round is read under
    DECISION-20261102-joseph-caveat-cut-list.md);
  - the ledger default caveat-cutlist-paper-20261102/ledger.md;
  - the batch with paper_body.tex (prefix PB) and primer_body.tex (prefix PM) added, as in the GENCMP round;
  - PROTECTED without paper_body.tex (the approved moves) and
    values_fived16.tex (generated, --check). main_paper.tex and main_note.tex stay byte-identical, so ABSTRACT is empty;
  - REMOVED_LABELS: paper_body.tex's sec:coverage, with Sec. IV F (move MV13, to the note's sec:coverage-5d). The note
    has a label of the same name, so the reference check counts only the paper's own sources for it.
usage: as step2/check_ledger.py (--files, --list, --self-test, --no-n4-frozen)."""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("check_ledger2", HERE.parent / "r22" / "step2" / "check_ledger.py")
cl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cl)
BASE = "589eb47d0"
cl.PREFIX["paper_body.tex"] = "PB"
cl.PREFIX["primer_body.tex"] = "PM"
# the id pattern is compiled from PREFIX at import, so it is rebuilt here with PB and PM in it
cl.IDRX = cl.re.compile(r"\b(" + "|".join(sorted(cl.PREFIX.values(), key=len, reverse=True)) + r")\d+\b")
cl.PROTECTED = [p for p in cl.PROTECTED if p not in ("values_fived16.tex", "paper_body.tex")]
cl.REMOVED_LABELS = {"paper_body.tex": {"sec:coverage"}}
# The note defines its own sec:coverage (sec_validation.tex, the 2D fixed-truth test), which its sources cite and the
# paper reaches as N-sec:coverage through \nsec; only the paper's own sources can refer to the paper's removed label
_refs_to = cl.refs_to
cl.refs_to = lambda lab, srcs: [g for g in _refs_to(lab, srcs)
                                if lab != "sec:coverage" or g in ("paper_body.tex", "main_paper.tex")]
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
