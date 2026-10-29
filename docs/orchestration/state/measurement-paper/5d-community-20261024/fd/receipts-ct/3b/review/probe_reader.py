"""Probes of fd_ct_readers mismatch via the committed test harness (no tracked file modified).
P1: closures planted with the first-order physical relation h = -d (pseudo-data shift vs response shift): what the
    tool prints. P2: the MP-1 zero data unfold equal to f exactly (near_f masking): does the guard falsely refuse?"""
import sys, json
sys.path.insert(0, "/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/4ddb8e26-d8ce-4841-bbeb-6b0f99a3fec7/scratchpad/review-3b/nd-unfolding/tests"); sys.path.insert(0, "/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/4ddb8e26-d8ce-4841-bbeb-6b0f99a3fec7/scratchpad/review-3b/nd-unfolding")
import numpy as np, unittest
import test_fd_ct_readers as T
from test_fd_ct_readers import Tree, bc, ct, digest

class P(T.Base):
    def _rewrite_closure(self, t, v, b):
        p = t.cdir / f"closure_{v}.npz"
        with np.load(p) as z:
            meta, xt, shp = str(z["meta"]), z["xtrue_flat"], z["shape"]
        p.unlink()
        np.savez_compressed(p, xsec_flat=t.cellwise(t.T * (1 + b)), xtrue_flat=xt, shape=shp, meta=meta)

    def test_P1_physical_relation_prints_negative_cosine(self):
        t = self.tree().write_mismatch()
        for s in ct.SPECIES:
            d = (t.D[f"{s}_p1"] - t.D[f"{s}_m1"]) / (2 * t.f)
            for sgn, v in ((+1, f"{s}_p1"), (-1, f"{s}_m1")):
                self._rewrite_closure(t, v, t.b["zero"] - sgn * d)   # closure bias = -(data shift), first order
        rc = self.run_tool(t, t.argv_mismatch, t.mismatch_patches())
        print("\nP1 rc", rc); print(self.stdout)

    def test_P2_zero_data_unfold_equal_to_f(self):
        t = self.tree().write_mismatch()
        p = bc.product_path(t.udir, "zero")
        with np.load(p) as z:
            meta, shp = str(z["meta"]), z["shape"]
        p.unlink()
        np.savez_compressed(p, xsec_flat=t.cellwise(t.f), shape=shp, meta=meta)
        t.bpins["zero"] = (digest(p),) + t.bpins["zero"][1:]
        rc = self.run_tool(t, t.argv_mismatch, t.mismatch_patches())
        print("\nP2 rc", rc, self.stderr[-300:])

if __name__ == "__main__":
    unittest.main(verbosity=1)
