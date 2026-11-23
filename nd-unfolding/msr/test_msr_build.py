#!/usr/bin/env python3
"""Synthetic tests of msr_build.py on IBU-1's own fixture (``test_ibu1.synthetic_inputs``), never on real inputs.

    python3 -m unittest nd-unfolding/msr/test_msr_build.py
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import msr_build as B  # noqa: E402  (puts the reused code on sys.path)
import ibu1  # noqa: E402
import ref_g1 as G  # noqa: E402
from test_ibu1 import synthetic_bkg, synthetic_inputs  # noqa: E402

CFG = json.loads(G.CONFIG.read_text())
LIB = G.Lib(CFG)
CONTRACT = json.loads((G.REPO / LIB.ibu1_cfg["contract"]["path"]).read_text())
INPUTS, BKG = synthetic_inputs(), synthetic_bkg()
JW, GW = G.worlds(LIB, CFG, INPUTS, CONTRACT, chunk=7_000)
DID = LIB.prod.did
import s5n_pseudo as S5N  # noqa: E402
N = INPUTS["MCgen"].shape[0]
WT, WR = np.asarray(INPUTS["w_truth"], float), np.asarray(INPUTS["w_reco"], float)


class Capture(unittest.TestCase):
    def setUp(self):
        self.tmpl = B.bkg_template(GW, S5N, BKG)
        self.half = G.full_half(N, WT, WR)
        self.cap = B.capture_problem(DID, GW, self.half, self.tmpl)

    def test_capture_restores_did_and_runs_no_iteration(self):
        self.assertIs(DID.ibu.__name__, "ibu")
        self.assertEqual(DID.ibu.__module__, DID.__name__)
        self.assertEqual(DID.make_grid.__module__, DID.__name__)

    def test_captured_problem_is_unfold_ibus_own(self):
        """IBU on the captured (R, b, prior) with some y equals ibu1.unfold_ibu's own trajectory for that y."""
        y = np.asarray(self.cap["R"] @ (1.1 * self.cap["prior"]) + self.cap["b"]).ravel()
        res = DID.ibu(self.cap["R"], y, self.cap["b"], self.cap["prior"], 3, maps=np.eye(self.cap["grid"].n_cells),
                      record=(3,))
        share = DID.share_matrix(self.cap["grid"], self.cap["u_fine"])
        mine = ibu1.extract(GW, share @ res.trajectory[-1], self.cap["u_fine"])
        ref = ibu1.unfold_ibu(GW, self.half, y, self.tmpl, [3])["F"][-1]
        np.testing.assert_allclose(mine, ref, rtol=1e-12, atol=0)

    def test_known_term_split_is_exact(self):
        np.testing.assert_allclose(self.cap["b_known"] + self.cap["b_extra"], self.cap["b"], rtol=0, atol=0)
        k = JW.known_rows
        want = np.bincount(GW.rflat[k], weights=WR[k], minlength=GW.n_fine)
        np.testing.assert_allclose(self.cap["b_known"], want, rtol=1e-12, atol=1e-12)

    def test_reported_map_is_linear_and_equals_extract(self):
        L = B.reported_map(DID, ibu1, GW, self.cap)
        share = DID.share_matrix(self.cap["grid"], self.cap["u_fine"])
        rng = np.random.default_rng(3)
        for t in (self.cap["prior"], self.cap["prior"] * rng.uniform(0.5, 1.5, self.cap["prior"].size)):
            np.testing.assert_allclose(L @ t, ibu1.extract(GW, share @ t, self.cap["u_fine"]), rtol=1e-12, atol=1e-300)
        self.assertEqual(L.shape, (GW.U.shape[0], self.cap["grid"].n_cells))

    def test_half_scaling(self):
        rows = np.arange(0, N, 2)
        cap_h = B.capture_problem(DID, GW, ibu1.Half(rows, 2 * WT[rows], 2 * WR[rows]), self.tmpl)
        self.assertEqual(cap_h["R"].shape, self.cap["R"].shape)
        self.assertGreater(float(cap_h["prior"].sum()), 0.5 * float(self.cap["prior"].sum()))

    def test_r_id_runs_on_a_capture(self):
        import prr_ibu
        rid = prr_ibu.r_id(DID, GW.U, [{"grid": self.cap["grid"], "u_fine": self.cap["u_fine"]},
                                       {"R": self.cap["R"], "b": self.cap["b"], "prior": self.cap["prior"]}])
        self.assertEqual(len(rid["sigma_rel"]), GW.U.shape[0])
        self.assertEqual(rid["n_cells_grid"], self.cap["grid"].n_cells)


class TwoD(unittest.TestCase):
    def bank(self, d: Path, fake=False) -> Path:
        import ref_c2c1
        cfg = json.loads((B.REPO / "2d-unfolding/ibukt/config.json").read_text())
        rng = np.random.default_rng(5)
        n = 20_000
        gen = np.column_stack([rng.uniform(0, 4.6, n), rng.uniform(1.4, 61, n)])
        reco = gen * rng.normal(1, 0.05, (n, 2))
        pt = rng.random(n) < 0.97
        pr = pt & (rng.random(n) < 0.8)
        if fake:
            pr[np.flatnonzero(~pt)[:1]] = True
        wt, wr = rng.uniform(0.5, 1.5, n), rng.uniform(0.5, 1.5, n)
        bkg = np.column_stack([rng.uniform(0, 4.5, 500), rng.uniform(1.5, 60, 500)])
        bw = rng.uniform(0.1, 1.0, 500)
        T, M, _, _ = ref_c2c1.binned_problem(gen, reco, bkg, pr, pt, wt, wr, bw, cfg["pt_edges"], cfg["pz_edges"])
        p = d / "bank.npz"
        sel_ids = np.sort(rng.choice(224, 205, replace=False))  # as run_ibukt.py:402 stores it: 205 integer cell ids
        np.savez(p, gen=gen, reco=reco, pr=pr, pt=pt, wt=wt, wr=wr, bkg=bkg, bw=bw, ibu_response=M, ibu_prior=T,
                 factor=np.ones(224), selected=sel_ids)
        return p

    def test_build_2d_reproduces_the_bank(self):
        with tempfile.TemporaryDirectory() as d:
            arrays, rec = B.build_2d(self.bank(Path(d)))
        self.assertEqual(rec["C-2D"]["M_vs_bank_ibu_response_max_abs"], 0.0)
        self.assertEqual(len(rec["selected_ids"]), 205)
        self.assertEqual(int(arrays["d2__selected_mask"].sum()), 205)
        np.testing.assert_array_equal(np.flatnonzero(arrays["d2__selected_mask"]), np.sort(arrays["d2__selected_ids"]))
        self.assertEqual(rec["C-2D"]["T_vs_bank_ibu_prior_max_rel"], 0.0)
        self.assertAlmostEqual(rec["C-2D"]["sum_b_bkg"], rec["C-2D"]["sum_bw_in_window"], places=9)
        for k in ("full", "halfA", "halfB"):
            self.assertEqual(arrays[f"d2_{k}__M"].shape, (224, 224))
        np.testing.assert_allclose(arrays["d2_halfA__T"] + arrays["d2_halfB__T"], 2 * arrays["d2_full__T"], rtol=1e-12)
        np.testing.assert_allclose(arrays["d2__b_bkg"], arrays["d2__b_bkg_globalindex"], rtol=1e-12, atol=0)
        for k in ("full", "halfA", "halfB"):
            np.testing.assert_allclose(arrays[f"d2_{k}__b_known"], arrays[f"d2_{k}__b_known_ibukt"], rtol=1e-12, atol=0)
        self.assertGreater(float(arrays["d2_full__b_known"].sum()), 0.0)  # the fixture has truth outside the grid

    def test_probe_times_the_halves_too(self):
        with tempfile.TemporaryDirectory() as d:
            arrays, rec = B.build_2d(self.bank(Path(d)), probe=True)
        self.assertIn("d2_halfA__M", arrays)
        self.assertNotIn("C-2D", rec)

    def test_a_signal_fake_is_refused(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(B.Refused):
                B.build_2d(self.bank(Path(d), fake=True))


def fixture_npz(d: Path) -> Path:
    """IBU-1's synthetic inputs written in of_inputs_5d.npz's key layout, with stand-in data keys."""
    arr = {k: INPUTS[k] for k in B.MC_KEYS}
    arr.update({k: INPUTS[k] for k in ("denom_nd", "flux", "data_pot", "n_nucleons")})
    arr["nedges"] = np.array(len(INPUTS["edges"]))
    arr.update({f"edges_{i}": np.asarray(e) for i, e in enumerate(INPUTS["edges"])})
    arr["measured"] = INPUTS["MCreco"][:100]
    arr["measured_weights"] = np.ones(100)
    p = d / "of_inputs_5d.npz"
    np.savez(p, **arr)
    return p


class Loader(unittest.TestCase):
    def test_nodata_loader_equals_the_pinned_loader_without_data_keys(self):
        import s5c_unfold
        with tempfile.TemporaryDirectory() as d:
            p = fixture_npz(Path(d))
            bk = Path(d) / "bkg.npz"
            np.savez(bk, bkg_reco=BKG["bkg_reco"], bkg_w=BKG["bkg_w"], bkg_nd=BKG["bkg_nd"], meta=json.dumps({"npz_sha256": "x"}))
            mine, _ = B.load_inputs_nodata(p, bk, None)
            ref = s5c_unfold.load_inputs(p)
        self.assertTrue(set(B.DATA_KEYS).isdisjoint(mine))
        for k in B.MC_KEYS + ("denom_nd", "flux", "data_pot", "n_nucleons", "nedges"):
            np.testing.assert_array_equal(mine[k], ref[k])
        for a, b in zip(mine["edges"], ref["edges"]):
            np.testing.assert_array_equal(a, b)

    def test_subsample_5d_keeps_layout_and_drops_data(self):
        with tempfile.TemporaryDirectory() as d:
            p = fixture_npz(Path(d))
            self.assertEqual(B.npz_rows(p, "MCgen"), INPUTS["MCgen"].shape[0])
            out = Path(d) / "sub" / "sub.npz"
            rec = B.subsample("5d", p, 0.1, out)
            z = np.load(out, allow_pickle=True)
            self.assertNotIn("measured", z.files)
            self.assertEqual(z["MCgen"].shape[0], rec["kept"])
            self.assertTrue(0.05 < rec["kept"] / rec["rows"] < 0.15)
            with self.assertRaises(B.Refused):
                B.subsample("5d", p, 0.1, out)


class BuildPart(unittest.TestCase):
    """build --part: one product per process, its record carries the peak RSS, and a peak above the cap is refused
    with no product written (the director's rulings for connect B)."""

    def run_r2d(self, d: Path, cap=None):
        from unittest import mock
        bank = TwoD().bank(d)
        dummy = d / "dummy"
        dummy.write_text("x")
        argv = ["build", "--part", "r2d", "--npz", str(dummy), "--bkg", str(dummy), "--bank", str(bank),
                "--t3-run", str(d), "--t3-stage-json", str(dummy), "--out", str(d / "out")]
        with mock.patch.object(B, "BANK_SHA", B.plain_sha256(bank)), mock.patch.object(B, "RSS_CAP", cap or B.RSS_CAP):
            return B.main(argv)

    def test_one_part_writes_its_product_and_record(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(self.run_r2d(Path(d)), 0)
            rec = json.loads((Path(d) / "out/r2d.json").read_text())
            self.assertEqual(rec["part"], "r2d")
            self.assertGreater(rec["peak_rss_bytes"], 0)
            self.assertEqual(rec["sha256"], B.plain_sha256(Path(d) / "out/r2d.npz"))
            with self.assertRaises(B.Refused):  # never overwritten
                self.run_r2d(Path(d))

    def test_a_peak_above_the_cap_is_refused_without_a_product(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(B.Refused):
                self.run_r2d(Path(d), cap=1.0)
            self.assertFalse((Path(d) / "out/r2d.npz").exists())
            self.assertIn("refused", json.loads((Path(d) / "out/r2d.json").read_text()))


class T3K(unittest.TestCase):
    def test_op_is_read_at_its_two_iterations_only(self):
        self.assertEqual(B.T3_KS["OP"], (2,))
        self.assertEqual(B.T3_KS["B0"], (5, 50))
        self.assertEqual(B.T3_KS["MO"], (5, 50))


class Reads(unittest.TestCase):
    def test_noatime_hash_and_stat(self):
        import os
        from unittest import mock
        with tempfile.TemporaryDirectory() as d, mock.patch.object(os, "O_NOATIME", os.O_NONBLOCK, create=True):
            p = Path(d) / "x.bin"
            p.write_bytes(b"abc")
            line = B.stat_line(p)
            self.assertEqual(line["sha256"], B.plain_sha256(p))
            self.assertIn("atime", line)

    def test_pins_hold_at_this_checkout(self):
        B.check_pins()


if __name__ == "__main__":
    unittest.main()
