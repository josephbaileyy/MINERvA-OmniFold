"""Probe: does the planted-leak test exercise the guard's integral TABLE, or only its 1e-30 floor?
(a) run test_a_planted_leak_is_refused with the guard's table emptied (the mutant 'guard: no integrals', applied by
    mock, not by editing the file); (b) plant a RATIO leak X_PB / f - 1 (O(1e-2), above the floor) with the real guard
    and with the emptied one."""
import sys, unittest
from pathlib import Path
from unittest import mock
W = Path(sys.argv[1]); sys.path.insert(0, str(W / "nd-unfolding")); sys.path.insert(0, str(W / "nd-unfolding/tests"))
import numpy as np
import test_fd_ct_5b_audit as T
au, cp = T.au, T.cp
real_guarded = cp.guarded
empty = mock.patch.object(cp, "guarded", lambda f, integrals: real_guarded(f, []))

def run(name, extra):
    with extra:
        r = unittest.TextTestRunner(verbosity=0, stream=open("/dev/null", "w")).run(T.Audit(name))
    return r.wasSuccessful()

print("(a) planted-leak test passes with the integral table EMPTIED:", run("test_a_planted_leak_is_refused", empty))

class Ratio(T.Base):
    def check(self, table_empty):
        t = self.tree()
        real = au.item3
        def leaky(*a, **k):
            o = real(*a, **k)
            o["leak"] = (t.pt.X["PB"] / t.f - 1.0).tolist()     # a ratio of a 5B unfold integral to f
            return o
        ex = [mock.patch.object(au, "item3", leaky)] + ([empty] if table_empty else [])
        return t.run(ex), float(np.median(np.abs(t.pt.X["PB"] / t.f - 1.0)))
    def test(self):
        rc1, mag = self.check(False)
        rc2, _ = self.check(True)
        print(f"(b) ratio leak |X_PB/f - 1| ~ {mag:.3g}: exit with real guard {rc1}, with emptied table {rc2}")
unittest.TextTestRunner(verbosity=0, stream=open("/dev/null", "w")).run(Ratio("test"))
