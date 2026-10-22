#!/usr/bin/env python3
"""S11, kept apart from the glossary batch so the author can reverse it on its own: a claim correction, not a
vocabulary change. Run AFTER apply_glossary.py (which rewrites sec_joint.tex from the base and so removes S11).

usage: apply_s11.py <worktree> [--revert]

Replaces "simple hypotheses" by "hybrid null hypotheses" in the first paragraph of sec:joint5d, adding the pointer to
sec:joint5d-design, where the hybrid null is defined. Asserts exactly one match; --revert restores the base text.
Sources: docs/orchestration/state/2d-closeout/stageF/methods/M2-AUDIT.md:39-40; sec_execsummary.tex:83 ("Calibrated
tests of hybrid null hypotheses for five predictions") and its source comment at :81; main_note.tex abstract.
"""
import re
import sys
from pathlib import Path

F = "docs/analysis-note/sec_joint.tex"
BEFORE = "The tests evaluate\nsimple hypotheses about five predictions."
AFTER = "The tests evaluate\nhybrid null hypotheses about five predictions (\\S\\ref{sec:joint5d-design})."


def main(argv):
    path = Path(argv[1]) / F
    text = path.read_text()
    old, new = (AFTER, BEFORE) if "--revert" in argv else (BEFORE, AFTER)
    n = text.count(old)
    if n != 1:
        print(f"S11 :: FAIL ({n} matches of {old!r} in {F})")
        return 1
    line = text[:text.index(old)].count("\n") + 1
    path.write_text(text.replace(old, new))
    print(f"S11 :: PASS ({'reverted' if '--revert' in argv else 'applied'} at {F}:{line}-{line + 1})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
