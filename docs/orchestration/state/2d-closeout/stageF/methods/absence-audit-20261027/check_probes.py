#!/usr/bin/env python3
"""Check this audit's ledger probes. usage: check_probes.py <worktree>

It loads note-n2/check_ledger.py and runs its check() with no batch files and no protected files, so only the probes
are judged (the round checker's sentence-coverage and protected-file rules belong to register rounds, not to this
audit). Exit 1 on any failure."""
import importlib.util
import sys
from pathlib import Path

here = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("cl", here.parent / "note-n2" / "check_ledger.py")
cl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cl)
wt = Path(sys.argv[1]).resolve()
fails, n_rows, n_probes = cl.check(wt, {}, {}, [], (here / "ledger.md").read_text(), {}, {})[:3]
for f in fails:
    print("  FAIL " + f)
print(f"ledger rows {n_rows}, probes {n_probes}, failures {len(fails)}")
sys.exit(1 if fails else 0)
