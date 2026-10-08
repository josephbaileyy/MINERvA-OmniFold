"""Controls for s5p_assemble on synthetic fine-grid products: C_stat is the replica sample covariance,
a band's block is the CV-centred mean outer product of its universe shifts, the bounded component is the
scaled maximum |prior shift| and never enters C_prob, and a missing universe fails closed."""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(1, str(Path(__file__).resolve().parents[1]))
import s5p_assemble as sa  # noqa: E402

N = 65856
REPO = Path(__file__).resolve().parents[2]


def save(path, x):
    np.savez(path, xsec_flat=x)


class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="s5p-assemble-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        rng = np.random.default_rng(1)
        self.cv = rng.uniform(1.0, 2.0, N)
        save(self.tmp / "central.npz", self.cv)
        (self.tmp / "boot").mkdir()
        for b in range(8):
            save(self.tmp / "boot" / f"b{b}.npz", self.cv * (1 + 0.01 * rng.normal(size=N)))
        (self.tmp / "uni").mkdir()
        for tag, s in (("MaRES_0", 1.02), ("MaRES_1", 0.98), ("Flux_0", 1.01), ("Flux_1", 0.995), ("Flux_2", 1.0)):
            save(self.tmp / "uni" / f"u_{tag}.npz", self.cv * s)
        save(self.tmp / "uni" / "u_CV.npz", self.cv)
        (self.tmp / "pri").mkdir()
        for k, s in (("d1", 1.05), ("d2", 0.97)):
            save(self.tmp / "pri" / f"p_prior_{k}.npz", self.cv * s)
        save(self.tmp / "lat_Muon_Energy_MINOS_0_b-_j-.npz", self.cv * 1.03)
        save(self.tmp / "lat_Muon_Energy_MINOS_1_b-_j-.npz", self.cv * 0.97)

    def run_it(self, expect=5, out="a.npz"):
        argv = ["--definition", "RD2", "--stage1", str(REPO / "docs/orchestration/state/s5p/stage1/stage1_inspect.json"),
                "--s5c-contract", str(REPO / "docs/orchestration/state/s5c/contract.json"),
                "--central", str(self.tmp / "central.npz"), "--bootstrap", *map(str, sorted((self.tmp / "boot").glob("*.npz"))),
                "--numerical", "absorbed", "--universe-dir", str(self.tmp / "uni"), "--universe-tag", "u",
                "--lateral", str(self.tmp / "lat_Muon_Energy_MINOS_0_b-_j-.npz"), str(self.tmp / "lat_Muon_Energy_MINOS_1_b-_j-.npz"),
                "--priors", *map(str, sorted((self.tmp / "pri").glob("*.npz"))), "--envelope-scale", "1.5",
                "--expect-universes", str(expect), "--out", str(self.tmp / out)]
        return sa.main(argv)

    def test_blocks(self):
        self.assertEqual(self.run_it(), 0)
        z = np.load(self.tmp / "a.npz", allow_pickle=False)
        meta = json.loads(str(z["meta"]))
        f = z["f"]
        np.testing.assert_allclose(z["C_band_MaRES"], np.outer(0.02 * f, 0.02 * f), rtol=1e-9)
        np.testing.assert_allclose(z["C_band_lat_Muon_Energy_MINOS"], np.outer(0.03 * f, 0.03 * f), rtol=1e-9)
        np.testing.assert_allclose(z["h"], 1.5 * 0.05 * f, rtol=1e-9)
        C = z["C_stat"] + z["C_band_MaRES"] + z["C_band_Flux"] + z["C_band_lat_Muon_Energy_MINOS"] + z["C_normalization"]
        np.testing.assert_allclose(z["C_prob"], C, rtol=1e-12)
        self.assertEqual(meta["functional_names"][-1], "total")
        self.assertEqual(len(meta["functional_names"]), 28)  # 27 reported H2 cells + total

    def test_missing_universe_fails_closed(self):
        with self.assertRaises(SystemExit):
            self.run_it(expect=6, out="b.npz")


if __name__ == "__main__":
    unittest.main()
