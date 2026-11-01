#!/usr/bin/env python3
"""Check the 5B text round's ledger: r22/step2/check_ledger.py, run with this round's base, ledger and abstract pairs.

The checks are step2/check_ledger.py's (one implementation; see its docstring). This round sets:
  - the base ac8fb9ae3 (origin/main at the round's start, after #614);
  - the ledger default 5b-text-20261031/ledger.md;
  - PROTECTED without the files this round changes by decision (DECISION-20261030 item 2, DECISION-20261031-joseph-j1-
    j2-and-protections-split.md): values_fived16.tex (generated, --check), paper_body.tex and main_paper.tex (checked by
    the ledger's P:: and N: probes, check_held.py and agy);
  - ABSTRACT: main_note.tex's two changed abstract sentences, each pinned by sha256 once Joseph approves the whole
    revised abstract (A4, DECISION-20261031 item 3). Unpinned, a pair allows nothing, so check 4 fails until then.
usage: as step2/check_ledger.py (--files, --list, --self-test, --no-n4-frozen)."""
import hashlib
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("check_ledger2", HERE.parent / "r22" / "step2" / "check_ledger.py")
cl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cl)
BASE = "ac8fb9ae3"
cl.PROTECTED = [p for p in cl.PROTECTED if p not in ("values_fived16.tex", "paper_body.tex", "main_paper.tex")]
cl.ABSTRACT = [
    ("5B-a1", r"It is reported in sixteen cells, with a covariance whose median per-cell uncertainty is \fvval{sigmed-C_total_resp}\%.",
     r"It is reported in sixteen cells, with a covariance whose median per-cell uncertainty is \fvval{sigmed-reported}\%."),
    ("5B-a2", r"In a fake-data study, the reported uncertainty does not cover the estimator's bias at GiBUU-like truths or at a synthetic $q_{3}$ tilt.",
     r"In a fake-data study, the estimator's bias exceeds the thresholds set against the reported uncertainty at a GiBUU-like truth and at a synthetic $q_{3}$ tilt."),
]
# set when Joseph approves the revised note abstract as a whole: sha256(old + "\0" + new)[:16] per pair
cl.ABSTRACT_PINS = {}
if __name__ == "__main__":
    if "--pins" in sys.argv:
        for i, old, new in cl.ABSTRACT:
            print(i, hashlib.sha256((old + "\0" + new).encode()).hexdigest()[:16])
        sys.exit(0)
    args = sys.argv[1:]
    if "--base" not in args:
        args += ["--base", BASE]
    if "--ledger" not in args:
        args += ["--ledger", str(HERE / "ledger.md")]
    sys.argv = [sys.argv[0]] + args
    sys.exit(cl.main())
