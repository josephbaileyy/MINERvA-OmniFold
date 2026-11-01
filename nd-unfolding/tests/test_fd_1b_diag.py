"""Controls for 1B's gate-D diagnosis (state/measurement-paper/5d-community-20261024/FD-1B-DIAG-DECLARATION.md), in
both directions: each localization rule passes the fixture built to satisfy it and fails the one built not to.

* one band whose toy shifts S1 does not hold: L1 names exactly that band, and the run reads LOCALIZED;
* S1's blocks equal to the toys' uncarried ones: L2 passes with rho_raw = 1;
* three such bands: L1 names exactly that set; four: L1 fails at K_MAX = 3, L2 fails, NOT LOCALIZED;
* rho reproduces gate D's readout bit for bit, and a departing readout refuses; a missing product refuses.

No real data are read: the fixtures are synthetic derivation products and a synthetic S1 assembly."""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

ND = Path(__file__).resolve().parents[1]
sys.path.insert(1, str(ND))
sys.path.insert(1, str(Path(__file__).resolve().parent))

import fd_1b_diag as fdg  # noqa: E402
import fd_1b_score as fs  # noqa: E402
import fd_1b_toys as toys  # noqa: E402
import s1_assemble as sa  # noqa: E402
from test_fd_1b import digest, toy_meta  # noqa: E402


class World:
    """Derivation products whose band shifts are `scale[b]` x 3 % of x_cv, and an S1 assembly whose band blocks are
    the toys' own blocks carried by g = f / x_T (``s1="carried"``) or uncarried (``s1="raw"``), with `s1_factor[b]`
    scaling a band's S1 block."""

    def __init__(self, tmp: Path, scale=None, s1="carried", s1_factor=None, g=1.4):
        rng = np.random.default_rng(5)
        self.tmp = tmp
        self.f = rng.uniform(1.0, 3.0, 16)
        self.x_t = self.f / g
        x_cv = self.x_t * rng.uniform(0.97, 1.03, 16)
        w = rng.uniform(0.5, 4.0, 100)
        self.constraint = tmp / "c.txt"
        self.constraint.write_text("".join(f"Flux {i} {w[i]!r}\n" for i in range(100)))
        scale, s1_factor = scale or {}, s1_factor or {}
        x = {"CV": x_cv}
        for b in sorted(sa.EXPECT):
            for i in range(sa.EXPECT[b]):
                x[f"{b}_{i}"] = x_cv * (1 + scale.get(b, 1.0) * rng.normal(0, 0.03, 16))
        self.der = tmp / "der"
        self.der.mkdir()
        for tag, v in x.items():
            m = toy_meta("derivation", None, json.loads(json.dumps(toys.single_universe(tag))), mode="derivation",
                         universe=tag)
            np.savez_compressed(self.der / f"t_{tag}.npz", xsec_flat=v, xtrue_flat=self.x_t, meta=json.dumps(m))
        carry = np.outer(self.f / self.x_t, self.f / self.x_t) if s1 == "carried" else 1.0
        blocks = {"stat": np.diag((0.01 * self.f) ** 2), "normalization": np.outer(0.014 * self.f, 0.014 * self.f),
                  "seed": np.zeros((16, 16))}
        for b in sa.LATERAL_BANDS:
            blocks[f"lat:{b}"] = np.diag((0.02 * self.f) ** 2)
        for b in sorted(sa.EXPECT):
            X = np.array([x[f"{b}_{i}"] for i in range(sa.EXPECT[b])])
            blocks[f"band:{b}"] = sa.mat_cov(X, w if b == sa.FLUX else None) * carry * s1_factor.get(b, 1.0)
        self.s1 = tmp / "s1.npz"
        np.savez_compressed(self.s1, f=self.f, U=np.eye(16, dtype=np.float32), C_e=sum(blocks.values()),
                            **{"C_" + k.replace(":", "_"): v for k, v in blocks.items()},
                            meta=json.dumps({"blocks": sorted(blocks)}))

    def run(self, name="diag", gate_d=None):
        """Gate D, then the diagnosis against gate D's readout; returns (rc, readout or None, gate D's readout)."""
        gd = self.tmp / f"{name}-gate-d.json"
        out = self.tmp / f"{name}.json"
        common = ["--derivation", str(self.der), "--tag", "t", "--s1-npz", str(self.s1),
                  "--flux-constraint", str(self.constraint)]
        with mock.patch.object(fs, "S1_NPZ_SHA256", digest(self.s1)), \
                mock.patch.object(sa, "CONSTRAINT_SHA256", digest(self.constraint)), \
                mock.patch("sys.stdout"), mock.patch("sys.stderr"):
            fs.main(["gate-d", *common, "--out", str(gd)])
            if gate_d is not None:
                gd.write_text(json.dumps(gate_d(json.loads(gd.read_text()))))
            rc = fdg.main([*common, "--gate-d", str(gd), "--out", str(out)])
        return rc, (json.loads(out.read_text()) if out.exists() else None), json.loads(gd.read_text())


class Diagnosis(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="fd1b-diag-"))

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def world(self, **kw):
        d = self.tmp / str(len(list(self.tmp.iterdir())))
        d.mkdir()
        return World(d, **kw)

    def test_one_band_s1_does_not_hold_is_named_by_l1(self):
        # the toys move MaRES ten times as far as S1's block holds
        rc, r, gd = self.world(scale={"MaRES": 10.0}, s1_factor={"MaRES": 0.01}).run()
        self.assertEqual((rc, gd["verdict"]), (0, "FAIL"))  # gate D fails on it
        self.assertEqual(r["rho"], gd["rho"])
        self.assertEqual((r["L1_named_bands"]["verdict"], r["L1_named_bands"]["size"]), ("PASS", 1))
        self.assertEqual(r["L1_named_bands"]["sets"], [["MaRES"]])
        self.assertEqual(r["verdict"], "LOCALIZED")
        np.testing.assert_allclose(r["per_band"]["MaRES"]["sigma_ratio"], 10.0, rtol=1e-9)
        np.testing.assert_allclose(r["per_band"]["MaRES"]["sigma_ratio_raw"], 10.0 / 1.4, rtol=1e-9)
        self.assertEqual(r["per_band"]["MaRES"]["group"], "interaction")

    def test_s1_blocks_equal_to_the_uncarried_toys_pass_l2(self):
        rc, r, gd = self.world(s1="raw").run()
        self.assertEqual((rc, gd["verdict"]), (0, "FAIL"))  # carried by g = 1.4, rho is out of the window
        np.testing.assert_allclose(r["rho_raw"], 1.0, rtol=1e-9)
        np.testing.assert_allclose(r["g"], 1.4, rtol=1e-12)
        self.assertEqual((r["L2_carry"]["verdict"], r["verdict"]), ("PASS", "LOCALIZED"))

    def test_three_bands_are_named_and_four_are_not_localized(self):
        three = {"MaRES": 10.0, "MaCCQE": 10.0, "2p2h": 10.0}
        rc, r, _ = self.world(scale=three, s1_factor={b: 0.01 for b in three}).run()
        self.assertEqual((r["L1_named_bands"]["verdict"], r["L1_named_bands"]["size"]), ("PASS", 3))
        self.assertEqual(r["L1_named_bands"]["sets"], [sorted(three)])
        four = {**three, "LowQ2": 10.0}
        rc, r, gd = self.world(scale=four, s1_factor={b: 0.01 for b in four}).run()
        self.assertEqual((rc, gd["verdict"]), (0, "FAIL"))
        self.assertEqual((r["L1_named_bands"]["verdict"], r["L1_named_bands"]["n_sets"]), ("FAIL", 0))
        self.assertEqual(r["L2_carry"]["verdict"], "FAIL")
        self.assertEqual(r["verdict"], "NOT LOCALIZED")
        self.assertEqual(fdg.K_MAX, 3)

    def test_the_window_is_gate_ds_unrelaxed(self):
        self.assertEqual(tuple(fdg.WINDOW), (0.9, 1.1))
        self.assertIs(fdg.WINDOW, fs.GATE_D_WINDOW)

    def test_rho_must_reproduce_gate_ds_readout_and_a_missing_product_refuses(self):
        w = self.world(scale={"MaRES": 10.0}, s1_factor={"MaRES": 0.01})
        moved = lambda g: {**g, "rho": [v * (1 + 1e-15) if i == 3 else v for i, v in enumerate(g["rho"])]}  # noqa: E731
        rc, r, _ = w.run("moved", gate_d=moved)
        self.assertEqual((rc, r), (4, None))
        (w.der / "t_MaRES_1.npz").unlink()
        rc, r, _ = w.run("missing")
        self.assertEqual((rc, r), (4, None))

    def test_a_readout_is_never_overwritten(self):
        w = self.world()
        rc, r, _ = w.run("once")
        self.assertEqual(rc, 0)
        with mock.patch.object(fs, "S1_NPZ_SHA256", digest(w.s1)), \
                mock.patch.object(sa, "CONSTRAINT_SHA256", digest(w.constraint)), mock.patch("sys.stderr"):
            self.assertEqual(fdg.main(["--derivation", str(w.der), "--tag", "t", "--s1-npz", str(w.s1),
                                       "--flux-constraint", str(w.constraint), "--gate-d",
                                       str(w.tmp / "once-gate-d.json"), "--out", str(w.tmp / "once.json")]), 4)


if __name__ == "__main__":
    unittest.main()
