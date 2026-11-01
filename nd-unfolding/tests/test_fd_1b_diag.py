"""Controls for 1B's gate-D diagnosis (state/measurement-paper/5d-community-20261024/FD-1B-DIAG-DECLARATION.md), in
both directions: each localization rule passes the fixture built to satisfy it and fails the one built not to.

* one band whose toy shifts S1 does not hold: L1 names exactly that band, and the run reads LOCALIZED;
* S1's blocks equal to the toys' uncarried ones: L2 passes with rho_raw = 1;
* three such bands: L1 names exactly that set; four: L1 fails at K_MAX = 3, L2 fails, NOT LOCALIZED;
* L1 on constructed diagonals: ties are all listed and their union named; a union over K_MAX fails; a substitution
  that fixes one cell but breaks another is no hit (every cell); the window's edges are inside; truncation keeps the
  count;
* the shares add up; rho reproduces gate D's readout bit for bit; each refusal says why.

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

    def run(self, name="diag", gate_d=None, pin=True, stderr=None):
        """Gate D, then the diagnosis against gate D's readout, pinned as the committed one unless ``pin`` is False;
        returns (rc, readout or None, gate D's readout)."""
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
            with mock.patch.object(fdg, "GATE_D_SHA256", digest(gd) if pin else fdg.GATE_D_SHA256), \
                    mock.patch("sys.stderr", stderr) if stderr is not None else mock.patch("sys.stderr"):
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
        self.assertEqual(r["L1_named_bands"]["named"], ["MaRES"])
        self.assertEqual(r["verdict"], "LOCALIZED")
        self.assertIn("fd_1b_diag.py", r["code_sha256"])
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

    def test_the_window_is_gate_ds_unrelaxed_and_inclusive(self):
        self.assertEqual(tuple(fdg.WINDOW), (0.9, 1.1))
        self.assertIs(fdg.WINDOW, fs.GATE_D_WINDOW)
        self.assertTrue(fdg.in_window(np.array([0.9, 1.0, 1.1])))
        self.assertFalse(fdg.in_window(np.array([0.9, 1.1000001])))
        self.assertFalse(fdg.in_window(np.array([0.8999999, 1.0])))

    @staticmethod
    def diag(**bands):
        """A two-cell L1 world: fixed 0.1, M_d 1; each band ``name=(e_cell0, e_cell1)`` against S1's 0.3."""
        m = {f"band:{b}": np.array([0.3, 0.3]) for b in bands}
        e = {f"band:{b}": np.array(v, float) for b, v in bands.items()}
        Ed = 0.1 + sum(e.values())
        Md = np.ones(2) * (0.1 + 0.3 * len(bands))
        return e, m, Ed, Md

    def test_l1_lists_every_tie_and_names_their_union(self):
        e, m, Ed, Md = self.diag(A=(0.45, 0.45), B=(0.45, 0.45), C=(0.3, 0.3))  # either A or B alone is enough
        L = fdg.localized_bands(e, m, Ed, Md)
        self.assertEqual((L["verdict"], L["size"], L["n_sets"], L["sets"]), ("PASS", 1, 2, [["A"], ["B"]]))
        self.assertEqual((L["named"], L["union"], L["intersection"]), (["A", "B"], ["A", "B"], []))
        with mock.patch.object(fdg, "LISTED_MAX", 1):
            L = fdg.localized_bands(e, m, Ed, Md)
        self.assertEqual((L["n_sets"], L["sets"], L["union"]), (2, [["A"]], ["A", "B"]))  # the count and union are all

    def test_l1_fails_when_the_union_names_more_than_k_max(self):
        e, m, Ed, Md = self.diag(**{b: (0.39, 0.39) for b in "ABCDE"}, F=(0.3, 0.3))  # rho^2 1.237; any one of five -> 1.189
        self.assertFalse(fdg.in_window(np.sqrt(Ed / Md)))
        L = fdg.localized_bands(e, m, Ed, Md)
        self.assertEqual((L["verdict"], L["size"], L["n_sets"], L["named"]), ("FAIL", 1, 5, []))
        self.assertEqual(L["union"], list("ABCDE"))

    def test_l1_holds_every_cell_not_only_the_cells_out_of_the_window(self):
        # A fixes cell 0 but breaks cell 1, where B's excess offsets A's deficit; only {A, B} holds both
        e, m, Ed, Md = self.diag(A=(0.6, 0.0), B=(0.3, 0.6), C=(0.3, 0.3))
        self.assertFalse(fdg.in_window(np.sqrt(Ed / Md)))
        L = fdg.localized_bands(e, m, Ed, Md)
        self.assertEqual((L["verdict"], L["size"], L["sets"]), ("PASS", 2, [["A", "B"]]))

    def test_the_shares_add_up(self):
        w = self.world(scale={"MaRES": 10.0}, s1_factor={"MaRES": 0.01})
        rc, r, _ = w.run()
        z = np.load(w.s1)
        fixed = sum(np.diag(z[k]) for k in z.files if k.startswith("C_") and (k in ("C_stat", "C_normalization")
                                                                              or k.startswith("C_lat_")))
        Md = sum(np.diag(z[k]) for k in z.files if k.startswith("C_") and k not in ("C_e", "C_seed"))
        Ed = np.array(r["rho"]) ** 2 * Md
        s1 = sum(np.array(v["share_s1"]) for v in r["per_band"].values())
        toys = sum(np.array(v["share_toys"]) for v in r["per_band"].values())
        np.testing.assert_allclose(s1 + fixed / Md, 1.0, rtol=1e-12)
        np.testing.assert_allclose(toys + fixed / Ed, 1.0, rtol=1e-12)

    def test_each_refusal_says_why(self):
        import io
        w = self.world(scale={"MaRES": 10.0}, s1_factor={"MaRES": 0.01})
        moved = lambda g: {**g, "rho": [v * (1 + 1e-15) if i == 3 else v for i, v in enumerate(g["rho"])]}  # noqa: E731
        for name, kw, why in (("moved", {"gate_d": moved}, "does not reproduce gate D"),
                              ("unpinned", {"pin": False}, "is not gate D's committed readout")):
            err = io.StringIO()
            rc, r, _ = w.run(name, stderr=err, **kw)
            self.assertEqual((rc, r), (4, None))
            self.assertIn(why, err.getvalue())
        (w.der / "t_MaRES_1.npz").unlink()
        err = io.StringIO()
        rc, r, _ = w.run("missing", stderr=err)
        self.assertEqual((rc, r), (4, None))
        self.assertIn("no derivation product for MaRES_1", err.getvalue())

    def test_a_readout_is_never_overwritten(self):
        w = self.world()
        rc, r, _ = w.run("once")
        self.assertEqual(rc, 0)
        with mock.patch.object(fs, "S1_NPZ_SHA256", digest(w.s1)), mock.patch.object(fdg, "GATE_D_SHA256",
                                                                                     digest(w.tmp / "once-gate-d.json")), \
                mock.patch.object(sa, "CONSTRAINT_SHA256", digest(w.constraint)), mock.patch("sys.stderr"):
            self.assertEqual(fdg.main(["--derivation", str(w.der), "--tag", "t", "--s1-npz", str(w.s1),
                                       "--flux-constraint", str(w.constraint), "--gate-d",
                                       str(w.tmp / "once-gate-d.json"), "--out", str(w.tmp / "once.json")]), 4)


if __name__ == "__main__":
    unittest.main()
