import os, subprocess, sys
from pathlib import Path
M = Path(__file__).resolve().parent
sys.path.insert(0, str(M.parent / "reviewB"))
from mutants_v2 import MUTANTS
W = M.parent / "wt-fig"
tgt = W / "nd-unfolding/fd_g_figures.py"
ORIG = (M / "orig_current.py").read_text()
assert tgt.read_text() == ORIG
ids = sys.argv[1:]
res = {}
try:
    for mid, desc, old, new in [m for m in MUTANTS if m[0] in ids]:
        if ORIG.count(old) != 1:
            print(mid, "NOT APPLICABLE", flush=True); continue
        tgt.write_text(ORIG.replace(old, new, 1))
        p = subprocess.run([sys.executable, "-B", "-m", "unittest", "test_fd_g_figures"], cwd=W / "nd-unfolding/tests",
                           env={**os.environ, "TMPDIR": str(M / "tmp")}, capture_output=True, text=True, timeout=900)
        res[mid] = p.returncode != 0
        print(mid, "KILLED" if p.returncode else "SURVIVED", desc, flush=True)
finally:
    tgt.write_text(ORIG)
print("rerun", len(res), "killed", sum(res.values()), "survived", sorted(k for k, v in res.items() if not v))
