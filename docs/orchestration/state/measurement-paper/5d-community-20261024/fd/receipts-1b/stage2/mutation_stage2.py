#!/usr/bin/env python3
"""1B stage 2's mutation receipt for the code FD-1B-STAGE2-DECLARATION.md adds to ``fd_1b_tasks.py``: job 2a-0, the
derivation split and the ``walls`` re-price rules. It runs stage 1's harness (``../stage1/mutation_fd_1b.py``: the
mutant tree outside the repository, the exactly-once preflight, the unmutated control) with this table in place of
stage 1's. A mutant that no test kills is printed UNKILLED and is a finding.

    python3 mutation_stage2.py [--only U01,W03] [--list]

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
    ("U01", T, "    if not set(DERIVATION_FIRST) <= set(every):", "    if False:",
     "a derivation selection naming a universe S1 did not unfold is accepted"),
    ("U02", T, '    raise SystemExit(f"[FAIL] no derivation selection {which!r}")', "    return every",
     "an undeclared derivation selection runs every universe"),
    ("U03", T, 'DERIVATION_FIRST = ("CV", "Flux_0", "MaRES_1", "GEANT_Pion_0")',
     'DERIVATION_FIRST = ("CV", "Flux_0", "MaRES_1")', "2a-0 runs three derivation universes, not the declared four"),
    ("U04", T, '("pilot", "toy", 2_600_000, 2_600_001)', '("pilot", "toy", 2_600_000, 2_600_002)',
     "a pilot toy runs in both 2a-0 and 2a"),
    ("U05", T, '"2a-0": {"nodes": 1, "limit": "01:00:00", "most_per_lane": 1,',
     '"2a-0": {"nodes": 1, "limit": "01:00:00", "most_per_lane": 2,', "2a-0's declared fullest lane departs"),
    ("U06", T, '"2a": {"nodes": 3, "limit": "02:40:00"', '"2a": {"nodes": 3, "limit": "03:00:00"',
     "2a keeps the first declaration's 3:00 limit"),
    ("U07", T, 'DECLARED_CAPS = {"2a-0": 1.0, "2a": 8.0,', 'DECLARED_CAPS = {"2a-0": 1.0, "2a": 9.0,',
     "2a's declared cap stays at 9.00, so stage 2 would exceed 23.0"),
    ("W01", T, "n_steps[str(k)] * load + len(c) * w", "len(c) * w", "the re-price rule drops each step's load"),
    ("W02", T, '        if m.get("numpy_version") != np.__version__:', "        if False:",
     "a product made under another numpy passes the walls gate"),
    ("W03", T, "        if not p.exists():\n            raise SystemExit", "        if False:\n            raise SystemExit",
     "a missing product passes the walls gate"),
    ("W04", T, "    ok &= rss <= RSS_LIMIT_KIB", "    pass", "the RSS re-price rule is dropped"),
    ("W05", T, "statistics.median(pilot)", "min(pilot)", "the pilot rule reads the fastest toy, not the median"),
    ("W06", T, '0.8 * hours(JOBS["2a"]["limit"])', '1.0 * hours(JOBS["2a"]["limit"])',
     "2a's re-price margin of 0.8 x its limit is dropped"),
    ("W07", T, "1.25 * TOY_UNIT_S", "1.3 * TOY_UNIT_S", "the protocol's 1.25 x 832 s pilot rule is loosened"),
]

if __name__ == "__main__":
    for f in (T, "tests/test_fd_1b.py"):
        print(f"sha256 {hashlib.sha256((harness.ND / f).read_bytes()).hexdigest()}  nd-unfolding/{f}")
    harness.MUTATIONS = MUTATIONS
    sys.exit(harness.main())
