"""Read-only diagnosis: run RealChain's gate over the fixture and print its record.vi, plus what keys c2_vi hashes."""
import json, sys, unittest
from pathlib import Path
T = Path(sys.argv[1]); sys.path.insert(0, str(T)); sys.path.insert(0, str(T.parent))
import numpy as np
import test_ll5d as tl
import fd_1b_c2 as c2

seen = {}
orig = c2.row_match
def spy(gen, wt, in_ps, td, tdw, cs, cd):
    seen.update(n_sig=int(in_ps.sum()), n_td=int(td.shape[0]),
                wt_eq_tdw_any=bool(np.isin(np.asarray(wt[in_ps], np.float64), np.asarray(tdw, np.float64)).any()),
                gen_rows_in_td=int(sum(any(np.array_equal(g, r) for r in td) for g in np.asarray(gen[in_ps], np.float64)[:200])),
                dtypes={"gen": str(np.asarray(gen).dtype), "wt": str(np.asarray(wt).dtype), "td": str(np.asarray(td).dtype), "tdw": str(np.asarray(tdw).dtype)})
    return orig(gen, wt, in_ps, td, tdw, cs, cd)

class Probe(tl.RealChain):
    def test_vi(self):
        c2.row_match = spy
        try:
            g = self.gate()
        finally:
            c2.row_match = orig
        print("VERDICT", g["verdict"], "READS", json.dumps(g.get("reads")))
        print("VI", json.dumps({k: v for k, v in g["record"]["vi"].items() if not k.endswith("per_cell")}))
        print("ROW_MATCH_INPUTS", json.dumps(seen))

s = unittest.TestSuite([Probe("test_vi")])
r = unittest.TextTestRunner(verbosity=1).run(s)
sys.exit(0 if r.wasSuccessful() else 1)
