"""Controls for s5p_prefreeze.units: lambda = b' W^-1 b of the asimov bias; a shift that increases the bias
raises T (positive null-SD units), one that reduces it lowers T."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(1, str(Path(__file__).resolve().parents[1]))
import s5p_joint as sj  # noqa: E402
import s5p_prefreeze as pf  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
STAGE1 = REPO / "docs/orchestration/state/s5p/stage1/stage1_inspect.json"
S5C = REPO / "docs/orchestration/state/s5c/contract.json"


class Tests(unittest.TestCase):
    def test_units(self):
        stage1 = json.loads(STAGE1.read_text())
        supported = json.loads(S5C.read_text())["measurement"]["partition_J"]["supported_cells"]
        U, names, pz = sj.j_matrix(stage1, supported)
        rng = np.random.default_rng(3)
        x0 = rng.uniform(0.5, 1.5, U.shape[1]) * 1e-39
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            np.savez(d / "pred.npz", xsec_flat=x0, sumw2_flat=np.zeros_like(x0))
            for k, f in (("fine", 1.05), ("coarse", 1.08), ("mid", 1.04)):
                np.savez(d / f"{k}.npz", xsec_flat=x0 * f)
            np.savez(d / "D.npz", D_J=np.zeros(U.shape[0]), d_pairs=np.zeros((4, U.shape[0])))
            design = {"nulls": {"G": {"prediction": str(d / "pred.npz")}},
                      "process_shift": {"G": {"path": str(d / "D.npz"), "sha256": sj.sha256(d / "D.npz"), "mode": "bias_aligned_upper"}}}
            f0 = U @ x0
            V = np.diag((0.01 * f0) ** 2)
            asim = {"generators": {"G": {k: str(d / f"{k}.npz") for k in ("fine", "coarse", "mid")}}}
            r = pf.units(design, V, U, pz, asim)["G"]
        b = 0.05 * f0
        self.assertAlmostEqual(r["lambda"], float(np.sum((b / (0.01 * f0)) ** 2)), delta=1e-6 * r["lambda"])
        self.assertGreater(r["F2_coarse_minus_fine"], 0)  # coarse has the larger bias
        self.assertLess(r["M1_mid_minus_fine"], 0)       # mid has the smaller bias
        self.assertEqual(r["D16_bias_aligned_upper"], 0.0)


if __name__ == "__main__":
    unittest.main()
