"""Local test of diag_period.py on the synthetic fixture, with the suspected mechanism planted: R12's central content
outside the 2D support is made tiny, so its X_sup is f to within 1e-13."""
import runpy, sys, tempfile
from pathlib import Path
from unittest import mock
WT = Path(sys.argv[1]); DIAG = sys.argv[2]
sys.path.insert(0, str(WT / "nd-unfolding/tests")); sys.path.insert(0, str(WT / "nd-unfolding"))
import numpy as np
import test_fd_ct_readers as T
import fd_ct_readers as ct
tmp = Path(tempfile.mkdtemp())
t = T.Tree(tmp / "tree")
shape = T.sa.s1.fine_shape()
ipt, ipz = np.unravel_index(np.arange(T.N), shape)[:2]
outside12 = (t.fm == 12) & np.isin(ipt * 16 + ipz, T.UNSUPPORTED)
t.xc = np.where(outside12, t.xc * 1e-12, t.xc)
t.f = t.U @ t.xc
t.write_common().write_period()
argv = list(t.argv_period); argv[argv.index("--out-json") + 1] = str(tmp / "diag-never.json")
ct.PINS.update(t.pins)
sys.argv = [DIAG, str(WT), *argv]
try:
    runpy.run_path(DIAG, run_name="__main__")
except SystemExit as e:
    print("diag exit", e.code)
