#!/usr/bin/env python3
"""1B stage 2, amendment 1's mutation receipt (FD-1B-STAGE2-AMENDMENT-1.md): job 2a-r, its derivation selection, and
the ceiling rule that counts an ended job at its ledgered charge. It runs stage 1's harness
(``../stage1/mutation_fd_1b.py``) with this table in place of stage 1's. A mutant no test kills is UNKILLED, a finding.

    python3 mutation_amend1.py [--only A01] [--list]

MEASURES: which tests detect each mutation. CANNOT AUTHORIZE: anything.
"""
from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("mutation_fd_1b", HERE.parent / "stage1/mutation_fd_1b.py")
harness = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(harness)

T = "fd_1b_tasks.py"
# (id, file, old, new, the rule it breaks)
MUTATIONS = [
    ("A01", T, "    if job not in CHARGED_NODE_S:\n        return cap(job)", "    if True:\n        return cap(job)",
     "an ended job counts at its cap: the binding's cap-sum reading, which refuses 2a-r"),
    ("A02", T, "    if charged > cap(job) + 1e-9:", "    if False:", "a ledgered charge above its cap is accepted"),
    ("A03", T, "    if job in CHARGED_NODE_S:\n        raise SystemExit", "    if False:\n        raise SystemExit",
     "an ended job can be submitted again"),
    ("A04", T, '"2a": ((1, 6022), (1, 6046), (1, 6037))}', '"2a": ((1, 6022), (1, 6046), (1, 6036))}',
     "a charge constant departs from the committed ledger"),
    ("A05", T, '"2p2h_2", "AGKYxF1pi_0")', '"2p2h_2", "AGKYxF1pi_1")',
     "2a-r reruns a derivation universe 60624652 did make"),
    ("A06", T, '"items": [("pilot", "half", 2_600_000, 2_600_007), ("derivation", "derivation", "rerun", None)]',
     '"items": [("pilot", "half", 2_600_001, 2_600_007), ("derivation", "derivation", "rerun", None)]',
     "2a-r leaves a quarantined half pilot unmade"),
    ("A07", T, "        if sum(committed(j) for j in JOBS if j.startswith(stage)) > ceiling + 1e-9:",
     "        if sum(cap(j) for j in JOBS if j.startswith(stage)) > ceiling + 1e-9:",
     "the ceiling check sums caps, not ledgered charges"),
    ("A08", T, '    if which == "rerun":\n        return list(DERIVATION_RERUN)',
     '    if which == "rerun":\n        return list(DERIVATION_FIRST)', "the rerun selection runs other universes"),
]

if __name__ == "__main__":
    for f in (T, "tests/test_fd_1b.py"):
        print(f"sha256 {hashlib.sha256((harness.ND / f).read_bytes()).hexdigest()}  nd-unfolding/{f}")
    harness.MUTATIONS = MUTATIONS
    sys.exit(harness.main())
