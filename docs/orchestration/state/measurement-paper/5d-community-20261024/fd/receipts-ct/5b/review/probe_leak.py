"""Probe: the control record's q and tau_rel, with MP-1's committed zero unfold (bitwise the ALL unfold when K2
passes), give f per cell up to a two-fold sign choice. The guard does not refuse."""
import contextlib, io, json, shutil, sys, tempfile
from pathlib import Path
import numpy as np
WT = Path(sys.argv[1])
sys.path.insert(1, str(WT / "nd-unfolding")); sys.path.insert(1, str(WT / "nd-unfolding/tests"))
import test_fd_ct_periods as T
import fd_ct_periods as cp, s1_assemble as sa
tmp = Path(tempfile.mkdtemp()); (tmp / "out").mkdir()
t = T.PTree(tmp).write()
with contextlib.ExitStack() as st:
    for p in t.patches():
        st.enter_context(p)
    (t.B / "control").mkdir()
    rc, out, err = T.quiet(cp.main, t.control_argv())
print("control rc", rc)
o = json.loads((t.B / "control/fd_ct_5b_control.json").read_text())
U = sa.functional_matrix(sa.fine_map(T.DEFINITION))
X = U @ np.load(t.mp1_path)["xsec_flat"]            # the committed MP-1 zero product's integrals (public)
s = np.array(o["K3_within_tolerance_of_f"]["q"]) * np.array(o["K3_within_tolerance_of_f"]["tau_rel"])
cand = np.stack([X / (1 + s), X / (1 - s)])
best = np.min(np.abs(cand / t.f - 1), axis=0)
print("verdict", o["verdict"], "| max over cells of min_candidate |f_rec/f - 1|:", f"{best.max():.2e}",
      "| candidate separation (median):", f"{np.median(2 * s):.2e}")
shutil.rmtree(tmp)
