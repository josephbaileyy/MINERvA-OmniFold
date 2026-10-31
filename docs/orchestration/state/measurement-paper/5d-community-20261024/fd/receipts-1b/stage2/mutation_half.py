#!/usr/bin/env python3
"""1B stage 2's mutation receipt for the half-MC truth fix (FD-1B-STAGE2-AMENDMENT-1.md): the toy mode holds one
truth per run only where the mode fixes it, and checks each half-MC truth against its split; the scorer's half read-back
returns a truth per toy, held to its split, and the lateral carry uses each toy's own. It runs stage 1's harness
(``../stage1/mutation_fd_1b.py``) with this table in place of stage 1's. A mutant no test kills is UNKILLED, a finding.

    python3 mutation_half.py [--only H01] [--list]

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

TY, SC = "fd_1b_toys.py", "fd_1b_score.py"
# (id, file, old, new, the rule it breaks)
MUTATIONS = [
    ("H01", TY, "        if a.mode in FIXED_TRUTH_MODES:\n", "        if True:\n",
     "one truth per run in half mode too: the defect job 60624652 hit"),
    ("H02", TY, "        elif not np.array_equal(x_true, half_truth(seed, inputs, truth, ratio)):",
     "        elif False:", "a half-MC truth is not checked against its split"),
    ("H03", TY, 'FIXED_TRUTH_MODES = ("toy", "derivation")', 'FIXED_TRUTH_MODES = ("derivation",)',
     "toy mode no longer holds one truth per run"),
    ("H04", SC, '        if mode == "half" and (m.get("experiment") or {}).get("split_key") != s5c_pseudo.split_key_for(s):',
     "        if False:", "the scorer reads a half toy without checking its recorded split"),
    ("H05", SC, "        if mode in toys.FIXED_TRUTH_MODES and truths and not np.array_equal(xt, truths[0]):",
     "        if truths and not np.array_equal(xt, truths[0]):", "the scorer holds half toys to one truth"),
    ("H06", SC, "    return np.array(X), (T[0] if mode in toys.FIXED_TRUTH_MODES else T), draws",
     "    return np.array(X), T[0], draws", "the scorer returns one truth for half toys"),
    ("H07", SC, "deltas[b] * g[t] / 2.0", "deltas[b] * g[0] / 2.0", "the lateral carry uses the first toy's truth"),
]

if __name__ == "__main__":
    for f in (TY, SC, "tests/test_fd_1b.py"):
        print(f"sha256 {hashlib.sha256((harness.ND / f).read_bytes()).hexdigest()}  nd-unfolding/{f}")
    harness.MUTATIONS = MUTATIONS
    sys.exit(harness.main())
