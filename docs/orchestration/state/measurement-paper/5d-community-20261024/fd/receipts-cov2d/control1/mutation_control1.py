"""control1_content_check mutants. Run from a scratchpad: TMPDIR=<dir> python3 mutation_control1.py <worktree>. It
rewrites control1_content_check.py per mutant, runs the fixture suite, and restores the file."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

WT = Path(sys.argv[1])
S = WT / "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-cov2d/control1"
src = (S / "control1_content_check.py").read_text()
M = [
    ("bitwise compare finds nothing", "return np.flatnonzero(a.view(u) != b.view(u))",
     "return np.flatnonzero(np.zeros(len(a), bool))"),
    ("value compare instead of bitwise", "return np.flatnonzero(a.view(u) != b.view(u))", "return np.flatnonzero(a != b)"),
    ("last partial chunk skipped", "for start in range(0, n, step):", "for start in range(0, n - step + 1, step):"),
    ("CV-only branch not failed", "for b in sorted(bcv - buni):", "for b in []:"),
    ("declared branch not checked", "for b in DECLARED.get(name, ()):", "for b in ():"),
    ("entry counts not checked", "if tcv.num_entries != tuni.num_entries:", "if False:"),
    ("interpretation not checked", "if str(dcv) != str(duni):", "if False:"),
    ("dtype not checked", "if a.dtype != u.dtype or len(a) != len(u)", "if len(a) != len(u)"),
    ("atime move not failed", "if atime != before[k][1]:", "if False:"),
    ("exit code always 0", "return 3 if failures else 0", "return 0"),
    ("CV-only tree not failed", "for t in sorted(tcv - tuni):", "for t in []:"),
    ("only the first shared tree compared", "for t in sorted(tcv & tuni):", "for t in sorted(tcv & tuni)[:1]:"),
    ("only the first shared branch compared", "shared = sorted(bcv & buni)", "shared = sorted(bcv & buni)[:1]"),
    ("first-row index drops the chunk start", 's["first"] = (start + r,', 's["first"] = (r,'),
    ("O_NOATIME dropped", "os.O_RDONLY | os.O_NOATIME", "os.O_RDONLY"),
    ("UNI digest fed the CV column", 's["h_uni"].update(u.dtype.str.encode() + u.tobytes())',
     's["h_uni"].update(a.dtype.str.encode() + a.tobytes())'),
]
orig = S / "control1_content_check.py"
bak = Path(os.environ["TMPDIR"]) / "control1_content_check.orig"
shutil.copy(orig, bak)
try:
    for name, a, b in M:
        if src.count(a) != 1:
            print(f"NOMATCH {name}")
            continue
        orig.write_text(src.replace(a, b))
        r = subprocess.run([sys.executable, "-B", "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider",
                            str(S / "test_control1_content_check.py")], cwd=WT, capture_output=True, text=True)
        print(f"{'KILLED ' if r.returncode else 'SURVIVED'} {name}", flush=True)
finally:
    shutil.copy(bak, orig)
