"""Tests for c2_corr.py on synthetic inputs (no fetched data). run: python3 -I -B test_c2_corr.py"""
import importlib.util
import json
import os
import shutil
import tempfile
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("c2_corr", os.path.join(HERE, "c2_corr.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
E = m.E

RNG = np.random.default_rng(7)
CELLS = np.sort(RNG.choice(224, 205, replace=False))


def synth(n=300):
    stat = np.zeros((224, 224))
    d = RNG.random(205) + 0.5
    stat[CELLS, CELLS] = d
    of = RNG.normal(size=(n, 224))
    noise = RNG.normal(size=(n, len(E.KS), 224)) * 0.5
    ibu = of[:, None, :] * np.arange(1, len(E.KS) + 1)[None, :, None] * 0.3 + noise
    s_stat = np.sqrt(d.sum())
    rec_ratio = E.sqrt_tr_cov(of[:, CELLS]) / s_stat
    ibu_c = RNG.normal(size=(len(E.KS), 224))
    er_c = RNG.normal(size=224)
    want = {K: m.t_stat(ibu_c[E.KS.index(K)] - er_c, ibu[:, E.KS.index(K), :] - of, m.RANK) for K in (10, 5)}
    return ibu, of, stat, s_stat, rec_ratio, ibu_c, er_c, want


class Core(unittest.TestCase):
    def test_end_to_end_synthetic(self):
        ibu, of, stat, t, r, ic, ec, want = synth()
        out = m.analyse(ibu, of, stat, CELLS, t, r, ic, ec, want)
        self.assertTrue(out["controls"]["C-PAIR"]["pass"])
        self.assertEqual(sorted(out["figure_spectra"]), ["C_IBU_K10", "C_OF", "StatOnly"])
        self.assertEqual(len(out["figure_spectra"]["C_OF"]), 205)
        self.assertEqual(sorted(out["paired_difference"]), sorted(str(K) for K in E.KS))
        json.dumps(out, allow_nan=False)

    def test_headline_copies_the_record_fields(self):
        ibu, of, stat, t, r, ic, ec, want = synth()
        out = m.analyse(ibu, of, stat, CELLS, t, r, ic, ec, want)
        h = out["headline"]
        self.assertEqual(h["r_a_k10_ibu_over_of"], out["c2_eff_ratios_K10"]["r_a_ibu_over_of"])
        self.assertEqual(h["r_b_k10_ibu_over_published"], out["c2_eff_ratios_K10"]["r_b_ibu_over_statonly"])
        self.assertEqual(h["participation_ratio_of"], out["structure"]["C_OF"]["participation_ratio"])
        self.assertEqual(h["participation_ratio_published"], out["structure"]["StatOnly"]["participation_ratio"])
        self.assertEqual(h["neighbour_rho_ppar_ibu_k10"],
                         out["structure"]["C_IBU_K10"]["mean_rho_neighbours_along_ppar"])
        self.assertEqual(h["leading_vector_cosine_ibu_k10_published"],
                         out["principal_cosines"]["C_IBU_K10|StatOnly"]["1"][0])
        self.assertEqual(h["paired_per_cell_corr_k10_median"],
                         out["paired_difference"]["10"]["per_cell_corr_ibu_of"]["median"])
        self.assertEqual(len(h), 5 + 4 * 3 + 3 + 2)

    def test_c_pair_refuses_a_wrong_value(self):
        ibu, of, stat, t, r, ic, ec, want = synth()
        want[10] *= 1 + 1e-6
        with self.assertRaisesRegex(m.Stop, "C-PAIR"):
            m.c_pair(ic, ec, ibu, of, want)

    def test_c_pair_refuses_a_shuffled_pairing(self):
        ibu, of, stat, t, r, ic, ec, want = synth()
        with self.assertRaisesRegex(m.Stop, "C-PAIR"):
            m.c_pair(ic, ec, ibu, of[np.roll(np.arange(300), 1)], want)

    def test_c_pair_uses_the_rank_75_rule(self):
        self.assertEqual(m.RANK, 300 // 4)

    def test_diagonal_matrix_structure(self):
        lam = np.array([4.0, 3.0, 2.0, 1.0])
        s = m.structure(np.diag(lam), "d", (np.array([[0, 1]]), np.array([[2, 3]])))
        self.assertEqual(s["mean_abs_offdiag_rho"], 0.0)
        self.assertAlmostEqual(s["participation_ratio"], 100 / 30, 12)
        self.assertAlmostEqual(s["topk_trace_share"]["1"], 0.4, 12)
        self.assertEqual(s["eigenvalues_desc"], [4.0, 3.0, 2.0, 1.0])

    def test_correlation_summary_signs(self):
        C = np.array([[1.0, -0.5, 0.2], [-0.5, 1.0, 0.0], [0.2, 0.0, 1.0]])
        s = m.structure(C, "c", (np.array([[0, 1]]), np.array([[0, 2]])))
        self.assertAlmostEqual(s["mean_rho_neighbours_along_ppar"], -0.5, 12)
        self.assertAlmostEqual(s["mean_rho_neighbours_along_pt"], 0.2, 12)
        self.assertAlmostEqual(s["max_abs_offdiag_rho"], 0.5, 12)
        self.assertAlmostEqual(s["fraction_offdiag_negative"], 2 / 6, 12)

    def test_psd_refuses(self):
        with self.assertRaisesRegex(m.Stop, "C-PSD"):
            m.psd_check("x", np.array([[1.0, 2.0], [2.0, 1.0]]))
        with self.assertRaisesRegex(m.Stop, "C-PSD"):
            m.psd_check("x", np.array([[1.0, 0.5], [0.4, 1.0]]))

    def test_corr_refuses_zero_variance(self):
        with self.assertRaisesRegex(m.Stop, "C-CORR"):
            m.corr(np.diag([1.0, 0.0]), "z")

    def test_neighbours_on_the_grid(self):
        cells = np.array([0, 1, 16, 17, 40])
        pz, pt = m.neighbours(cells)
        self.assertEqual(sorted(map(tuple, pz.tolist())), [(0, 1), (2, 3)])
        self.assertEqual(sorted(map(tuple, pt.tolist())), [(0, 2), (1, 3)])

    def test_row_end_is_not_a_neighbour(self):
        pz, pt = m.neighbours(np.array([15, 16]))
        self.assertEqual(len(pz), 0)

    def test_principal_cosines(self):
        A = np.diag([5.0, 4.0, 3.0, 2.0, 1.0, 0.5, 0.4, 0.3, 0.2, 0.1, 0.05])
        c = m.principal_cosines(A, A)
        self.assertTrue(np.allclose(c["10"], 1.0))
        B = np.diag([1.0, 5.0, 3.0, 2.0, 4.0, 0.5, 0.4, 0.3, 0.2, 0.1, 0.05])
        self.assertAlmostEqual(m.principal_cosines(A, B)["1"][0], 0.0, 12)

    def test_paired_identity_and_values(self):
        of = RNG.normal(size=(300, 205))
        ibu = np.repeat(of[:, None, :], len(E.KS), axis=1) * 2.0 + RNG.normal(size=(300, len(E.KS), 205)) * 0.1
        p = m.paired(ibu, of)["10"]
        self.assertGreater(p["per_cell_corr_ibu_of"]["median"], 0.99)
        self.assertAlmostEqual(p["sqrt_tr_delta_over_sqrt_tr_of"], 1.0, 1)

    def test_c2_eff_controls_still_apply(self):
        ibu, of, stat, t, r, ic, ec, want = synth()
        with self.assertRaisesRegex(E.Stop, "C-QR"):
            m.analyse(ibu, of, stat, CELLS, t, r * (1 + 1e-5), ic, ec, want)


class Files(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="c2corr-t-")

    def tearDown(self):
        shutil.rmtree(self.d)

    def test_main_refuses_existing_outputs(self):
        p = os.path.join(self.d, "r.json")
        open(p, "w").close()
        self.assertEqual(m.main([self.d, "--out", p]), 2)
        q = os.path.join(self.d, "s.png")
        open(q, "w").close()
        self.assertEqual(m.main([self.d, "--out", os.path.join(self.d, "new.json"), "--png", q]), 2)

    def test_stop_is_recorded(self):
        p = os.path.join(self.d, "r.json")
        self.assertEqual(m.main([os.path.join(self.d, "none"), "--out", p]), 3)
        self.assertEqual(json.load(open(p))["status"], "STOP")

    def test_plot_writes_a_png(self):
        rec = {"figure_spectra": {k: list(np.logspace(-80, -82, 205)) for k in ("C_IBU_K10", "C_OF", "StatOnly")}}
        p = os.path.join(self.d, "s.png")
        m.plot(rec, p)
        with open(p, "rb") as f:
            self.assertEqual(f.read(8), b"\x89PNG\r\n\x1a\n")


if __name__ == "__main__":
    unittest.main(verbosity=2)
