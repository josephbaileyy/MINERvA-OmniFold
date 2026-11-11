"""Read-only: the vi that A21Equality's reference carries, and LL5D's on the same fixture."""
import json, sys, unittest
from pathlib import Path
T = Path(sys.argv[1]); sys.path.insert(0, str(T)); sys.path.insert(0, str(T.parent))
import numpy as np
import test_ll5d as tl
import fd_1b_c2 as c2
import ll5d

class Probe(tl.A21Equality):
    def test_vi(self):
        draws = {t: self.draws(t, 6) for t in ll5d.TRUTHS}
        ref = self.reference(draws)
        P = self.prepared()
        rel, geo, V, cv = ll5d.c2_inputs(P, self.s1, self.fm)
        vi = c2.c2_vi(P, cv, self.fm, geo)
        rvi = json.loads(str(ref["json"]))["vi"]
        strip = lambda d: {k: v for k, v in d.items() if not k.endswith("per_cell")}
        print("REF_VI", json.dumps(strip(rvi)))
        print("LL5D_VI", json.dumps(strip(vi)))

r = unittest.TextTestRunner(verbosity=1).run(unittest.TestSuite([Probe("test_vi")]))
sys.exit(0 if r.wasSuccessful() else 1)
