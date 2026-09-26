"""Controls for s5p_universe (no LightGBM or ROOT): the row-alignment guard fires on a misaligned bank and
stays silent on an aligned one with exactly the declared sentinel rows; a universe replaces every CV
weight it should (signal, denominator, template) and nothing else; the CV control reproduces the
production data path bitwise."""
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(1, str(Path(__file__).resolve().parents[1]))
sys.path.insert(1, str(Path(__file__).resolve().parent))
import s5n_pseudo  # noqa: E402
import s5p_universe as su  # noqa: E402
from test_s5e_trace import EDGES, toy_inputs  # noqa: E402
from test_s5p_stage2_tools import Stubbed  # noqa: E402


def bank_for(inputs, bkg, n_sentinel):
    gen = np.array(inputs["MCgen"], np.float32, copy=True)
    gen[:n_sentinel, 3] = np.nan
    return {"MCgen": gen, "MCreco": inputs["MCreco"], "pass_reco": inputs["pass_reco"], "pass_truth": inputs["pass_truth"],
            "measured": inputs["measured"], "bkg_cols": bkg["bkg_reco"],
            "td_pt": inputs["MCgen"][:, 0], "td_pz": inputs["MCgen"][:, 1], "td_ea": inputs["MCgen"][:, 2],
            "td_q3": inputs["MCgen"][:, 3], "td_w": inputs["MCgen"][:, 4]}


def toy(n=4000):
    inputs = toy_inputs(n, 5)
    inputs["measured"] = inputs["MCreco"][inputs["pass_reco"]][: n // 3].copy()
    bkg = {"bkg_reco": inputs["MCreco"][:300].copy(), "bkg_w": np.full(300, 0.05), "bkg_nd": None}
    return inputs, bkg


class AlignmentTests(unittest.TestCase):
    def setUp(self):
        self.orig = su.SENTINEL_ROWS
        su.SENTINEL_ROWS = 7

    def tearDown(self):
        su.SENTINEL_ROWS = self.orig

    def with_sentinels(self, inputs, k):
        inputs["MCgen"] = np.array(inputs["MCgen"], copy=True)
        inputs["MCgen"][:k, 3] = -9999.0
        return inputs

    def test_aligned_bank_passes_with_the_declared_sentinels(self):
        inputs, bkg = toy()
        inputs = self.with_sentinels(inputs, 7)
        ev = su.check_alignment(bank_for(inputs, bkg, 7), inputs, bkg)
        self.assertEqual(ev["sentinel_rows"], 7)

    def test_shifted_bank_rows_are_refused(self):
        inputs, bkg = toy()
        inputs = self.with_sentinels(inputs, 7)
        bank = bank_for(inputs, bkg, 7)
        bank["MCreco"] = np.roll(bank["MCreco"], 1, axis=0)
        with self.assertRaises(RuntimeError):
            su.check_alignment(bank, inputs, bkg)

    def test_truth_difference_outside_the_sentinels_is_refused(self):
        inputs, bkg = toy()
        inputs = self.with_sentinels(inputs, 7)
        bank = bank_for(inputs, bkg, 7)
        bank["MCgen"][100, 0] += 0.01
        with self.assertRaises(RuntimeError):
            su.check_alignment(bank, inputs, bkg)

    def test_wrong_sentinel_count_is_refused(self):
        inputs, bkg = toy()
        inputs = self.with_sentinels(inputs, 6)
        with self.assertRaises(RuntimeError):
            su.check_alignment(bank_for(inputs, bkg, 6), inputs, bkg)


class UniverseTests(Stubbed):
    def test_universe_replaces_signal_denominator_and_template_weights_only(self):
        inputs, bkg = toy()
        inputs["denom_nd"] = np.full(tuple(len(e) - 1 for e in EDGES), 80.0)
        bank = bank_for(inputs, bkg, 0)
        n = inputs["MCgen"].shape[0]
        w = {"wt": np.asarray(inputs["w_truth"]) * 1.1, "wr": np.asarray(inputs["w_reco"]) * 0.9,
             "tdw": np.full(n, 0.2), "bkgw": np.asarray(bkg["bkg_w"]) * 2.0}
        ui, ub, info = su.universe_inputs(inputs, bkg, bank, w, "MaCCQE", "0", None)
        np.testing.assert_array_equal(ui["w_truth"], w["wt"])
        np.testing.assert_array_equal(ui["w_reco"], w["wr"])
        np.testing.assert_array_equal(ub["bkg_w"], w["bkgw"])
        self.assertAlmostEqual(ui["denom_nd"].sum(), 0.2 * n, places=6)
        for key in ("MCgen", "MCreco", "measured", "pass_reco", "pass_truth", "flux"):
            self.assertIs(ui[key], inputs[key])
        self.assertAlmostEqual(info["wt_over_cv_median"], 1.1, places=9)

    def test_flux_universe_without_a_flux_file_is_refused(self):
        inputs, bkg = toy()
        inputs["denom_nd"] = np.full(tuple(len(e) - 1 for e in EDGES), 80.0)
        n = inputs["MCgen"].shape[0]
        w = {"wt": np.asarray(inputs["w_truth"]), "wr": np.asarray(inputs["w_reco"]), "tdw": np.ones(n), "bkgw": np.asarray(bkg["bkg_w"])}
        with self.assertRaises(RuntimeError):
            su.universe_inputs(inputs, bkg, bank_for(inputs, bkg, 0), w, "Flux", "3", None)

    def test_prior_reweight_moves_the_denominator_with_the_truth(self):
        inputs, bkg = toy()
        shape = tuple(len(e) - 1 for e in EDGES)
        inputs["denom_nd"] = np.full(shape, 80.0)
        r = np.where(inputs["MCgen"][:, 2] > 0.4, 1.5, 1.0)
        ui = su.prior_inputs(inputs, r)
        np.testing.assert_array_equal(ui["w_truth"], np.asarray(inputs["w_truth"]) * r)
        m = inputs["pass_truth"]
        samp = np.asarray(inputs["MCgen"])[m].astype(float)
        of0, _ = np.histogramdd(samp, bins=EDGES, weights=np.asarray(inputs["w_truth"])[m])
        of1, _ = np.histogramdd(samp, bins=EDGES, weights=ui["w_truth"][m])
        ok = of0 > 0
        np.testing.assert_allclose((of1 / ui["denom_nd"])[ok], (of0 / inputs["denom_nd"])[ok])  # completeness unchanged
        self.assertGreater(ui["denom_nd"].sum(), inputs["denom_nd"].sum())

    def test_constant_prior_reweight_leaves_the_cross_section_unchanged(self):
        inputs, bkg = toy()
        inputs["denom_nd"] = np.full(tuple(len(e) - 1 for e in EDGES), 80.0)
        import s5p_numerics
        x0, _ = s5p_numerics.unfold_one(s5n_pseudo.build_data(inputs, bkg), np.float32, 42, 1, 3)
        ui = su.prior_inputs(inputs, np.full(inputs["MCgen"].shape[0], 1.3))
        x1, _ = s5p_numerics.unfold_one(s5n_pseudo.build_data(ui, bkg), np.float32, 42, 1, 3)
        np.testing.assert_allclose(x1, x0, rtol=1e-4)  # the defect this guards against gives 1/1.3

    def test_cv_control_is_the_production_data_path(self):
        inputs, bkg = toy()
        exp = s5n_pseudo.build_data(inputs, bkg)
        xs_prod, _ = s5n_pseudo.unfold_negweight(exp, 42, 1, 3)
        import s5p_numerics
        xs, _ = s5p_numerics.unfold_one(s5n_pseudo.build_data(inputs, bkg), np.float32, 42, 1, 3)
        np.testing.assert_array_equal(xs, xs_prod)


if __name__ == "__main__":
    unittest.main()
