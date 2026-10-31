#!/usr/bin/env python3
"""Check r22 Step 3's note fact ledger: step2/check_ledger.py, run with this round's base, ledger and pairs.

The checks are step2/check_ledger.py's, unchanged (one implementation; see its docstring). Step 3 sets:
  - base 14a0415f, origin/main at the round's start (STEP3-PLAN.md section 2). Its note sources are those the note
    round adopted (#539, f47b1b4a), so Step 2's two abstract pairs are already in the base;
  - ABSTRACT / ABSTRACT_PINS: this round's own pair, B01-g-07 (A4), which Joseph approved as pinned on 2026-10-31
    (#571). main_note.tex may differ from the base only by that pair;
  - the ledger default step3/ledger.md;
  - after adoption (STEP3-PLAN.md section 4), only the adopted pieces' rows, read from step3/runs/adoption.tsv (ADOPT
    YES). A piece that was not adopted keeps its base text, so its rows, which assert NEW's text, are not checked, and
    the abstract pair, judged with B01, is allowed only if B01 was adopted. --all-pieces checks every row and the pair,
    as before adoption (NEW's tree, bb71f57b).
usage: as step2/check_ledger.py (--files, --list, --self-test, --no-n4-frozen), plus --all-pieces."""
import importlib.util
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("check_ledger2", HERE.parent / "step2" / "check_ledger.py")
cl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cl)
BASE = "14a0415f"
# (id, old, new); pin = check_ledger.pin(old, new), from step3/abstract-pairs.md. Joseph approved B01-g-07 as pinned
# (DECISION-20261031-joseph-note-abstract-reorder.md, #571); it is judged with piece B01.
cl.ABSTRACT = [
    ('B01-g-07',
     "The coverage of the result's intervals has not been validated; a bias test at two held-out GENIE~v3 truths finds the estimator's bias below the reported uncertainty in every cell but does not test interval widths. In a fake-data study, the reported uncertainty does not cover the estimator's bias at GiBUU-like truths or at a synthetic $q_{3}$ tilt.",
     "A bias test at two held-out GENIE~v3 truths finds the estimator's bias below the reported uncertainty in every cell but does not test interval widths. In a fake-data study, the reported uncertainty does not cover the estimator's bias at GiBUU-like truths or at a synthetic $q_{3}$ tilt. The coverage of the result's intervals has not been validated."),
]
cl.ABSTRACT_PINS = {'B01-g-07': '6f0fb222b469a666'}


def adopted():
    """The pieces with ADOPT YES in step3/runs/adoption.tsv (tools/adopt_step2.py's output)."""
    lines = (HERE / "runs" / "adoption.tsv").read_text().splitlines()
    head = lines[0].split("\t")
    return {r[0] for r in (x.split("\t") for x in lines[1:]) if r[head.index("ADOPT")] == "YES"}


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--all-pieces" in args:
        args.remove("--all-pieces")
    else:
        keep = adopted()
        all_rows = cl.rows
        # only a piece's own rows (B01-1, ...) are dropped; any other id, such as the self-test's planted rows, is kept
        cl.rows = lambda text: (r for r in all_rows(text) if not re.match(r"B\d\d-", r[0]) or r[0][:3] in keep)
        if "B01" not in keep:
            cl.ABSTRACT, cl.ABSTRACT_PINS = [], {}
        print(f"adopted pieces (step3/runs/adoption.tsv): {' '.join(sorted(keep))}; other pieces' rows not checked")
    if "--base" not in args:
        args += ["--base", BASE]
    if "--ledger" not in args:
        args += ["--ledger", str(HERE / "ledger.md")]
    sys.argv = [sys.argv[0]] + args
    sys.exit(cl.main())
