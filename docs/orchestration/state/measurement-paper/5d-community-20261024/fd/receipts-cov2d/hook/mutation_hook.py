"""--data-file hook mutants. Run from a scratchpad: TMPDIR=<dir> python mutation_hook.py <worktree>, with an
interpreter that has PyROOT, LightGBM and scikit-learn. It rewrites 2d-unfolding/re2/re2_driver.py per mutant, runs
test_re2_data_file.py, and restores the file. A kill counts only on a test failure (unittest rc != 0)."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

WT = Path(sys.argv[1])
D = WT / "2d-unfolding/re2/re2_driver.py"
T = WT / "2d-unfolding/re2/tests/test_re2_data_file.py"
src = D.read_text()
M = [
    ("data tree not replaced", '        t_data = f_data.Get("data")\n', '        f_data.Get("data")\n'),
    ("POT guard removed", "        if not p_own or not p_omni or p_own.GetVal() != p_omni.GetVal():",
     "        if False:"),
    ("POT guard skips a missing POT", "        if not p_own or not p_omni or p_own.GetVal() != p_omni.GetVal():",
     "        if p_own and p_omni and p_own.GetVal() != p_omni.GetVal():"),
    ("closure guard removed", "        if args.closure:\n            raise SystemExit(\"[FAIL] --data-file and --closure",
     "        if False:\n            raise SystemExit(\"[FAIL] --data-file and --closure"),
    ("data digest not recorded", '        provenance.append(("dataFileSha256", file_sha256(args.data_file)))',
     "        pass"),
    ("data digest recorded without the flag",
     '    if args.data_file is not None:  # COV2D\n        provenance.append(("dataFileSha256"',
     '    if True:  # COV2D\n        provenance.append(("dataFileSha256"'),
    ("digest of the omnifile instead", 'provenance.append(("dataFileSha256", file_sha256(args.data_file)))',
     'provenance.append(("dataFileSha256", file_sha256(args.omnifile)))'),
    ("simulation read from the data file", '    t_bkg = f_in.Get("mc_background")\n    t_data = f_in.Get("data")\n',
     '    t_bkg = f_in.Get("mc_background")\n    t_data = f_in.Get("data")\n    f_in = ROOT.TFile.Open(args.data_file) if args.data_file else f_in\n'),
]
bak = Path(os.environ["TMPDIR"]) / "re2_driver.orig"
shutil.copy(D, bak)
try:
    for name, a, b in M:
        if src.count(a) != 1:
            print(f"NOMATCH {name}", flush=True)
            continue
        D.write_text(src.replace(a, b))
        r = subprocess.run([sys.executable, "-B", "-m", "unittest", str(T)], cwd=WT, capture_output=True, text=True)
        print(f"{'KILLED ' if r.returncode else 'SURVIVED'} {name}", flush=True)
finally:
    shutil.copy(bak, D)
