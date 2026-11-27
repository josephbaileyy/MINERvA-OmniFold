"""Tests for c2_eff.py on synthetic inputs (no fetched data is read). run: python3 -I -B test_c2_eff.py"""
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("c2_eff", os.path.join(HERE, "c2_eff.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

RNG = np.random.default_rng(12345)
CELLS = np.sort(RNG.choice(224, 205, replace=False))


def synth(n=300):
    stat = np.zeros((224, 224))
    d = RNG.random(205) + 0.5
    stat[CELLS, CELLS] = d
    of = RNG.normal(size=(n, 224))
    ibu = np.repeat(of[:, None, :], len(m.KS), axis=1) * 2.0
    s_stat = np.sqrt(d.sum())
    s_of = m.sqrt_tr_cov(of[:, CELLS])
    return ibu, of, stat, s_stat, s_of / s_stat


class Core(unittest.TestCase):
    def test_sqrt_tr_cov_matches_numpy(self):
        X = RNG.normal(size=(40, 7))
        self.assertAlmostEqual(m.sqrt_tr_cov(X), float(np.sqrt(np.trace(np.cov(X, rowvar=False, ddof=1)))), 12)

    def test_ratios_on_a_known_scaling(self):
        ibu, of, stat, t, r = synth()
        out = m.compute(ibu, of, stat, CELLS, t, r)
        k = out["per_K"][str(m.PRIMARY)]
        self.assertAlmostEqual(k["r_a_ibu_over_of"], 2.0, 12)
        self.assertLess(k["r_a_jackknife_se"], 1e-10)
        self.assertAlmostEqual(k["r_b_ibu_over_statonly"], 2.0 * r, 12)
        self.assertAlmostEqual(k["median_sigma_ratio_ibu_over_of"], 2.0, 12)
        self.assertEqual(out["cells"], 205)
        self.assertEqual(sorted(out["per_K"]), sorted(str(K) for K in m.KS))

    def test_jackknife_se_of_a_mean(self):
        x = RNG.normal(size=50)
        se = m.jackknife_se(lambda idx: float(np.mean(x[idx])), 50)
        self.assertAlmostEqual(se, float(np.std(x, ddof=1) / np.sqrt(50)), 10)

    def test_c_qr_refuses_another_ensemble(self):
        ibu, of, stat, t, r = synth()
        with self.assertRaisesRegex(m.Stop, "C-QR"):
            m.compute(ibu, of, stat, CELLS, t, r * (1 + 1e-5))

    def test_c_qr_accepts_within_tolerance(self):
        ibu, of, stat, t, r = synth()
        m.compute(ibu, of, stat, CELLS, t, r * (1 + 5e-7))

    def test_c_stat_refuses(self):
        ibu, of, stat, t, r = synth()
        with self.assertRaisesRegex(m.Stop, "C-STAT"):
            m.compute(ibu, of, stat, CELLS, t * (1 + 1e-5), r)

    def test_c_cells_refuses_a_different_set(self):
        ibu, of, stat, t, r = synth()
        other = CELLS.copy()
        other[0] = [i for i in range(224) if i not in set(CELLS)][0]
        with self.assertRaisesRegex(m.Stop, "C-CELLS"):
            m.compute(ibu, of, stat, np.sort(other), t, r)

    def test_c_finite_refuses(self):
        ibu, of, stat, t, r = synth()
        ibu[3, 5, CELLS[0]] = np.nan
        with self.assertRaisesRegex(m.Stop, "C-FINITE"):
            m.compute(ibu, of, stat, CELLS, t, r)

    def test_cells_outside_the_set_do_not_enter(self):
        ibu, of, stat, t, r = synth()
        outside = [i for i in range(224) if i not in set(CELLS)]
        ibu2 = ibu.copy()
        ibu2[:, :, outside] *= 1e6
        a = m.compute(ibu, of, stat, CELLS, t, r)["per_K"]["10"]["r_a_ibu_over_of"]
        b = m.compute(ibu2, of, stat, CELLS, t, r)["per_K"]["10"]["r_a_ibu_over_of"]
        self.assertEqual(a, b)


class Files(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="c2eff-t-")

    def tearDown(self):
        shutil.rmtree(self.d)

    def th2(self, name, edges_pt=m.PT_EDGES, edges_pz=m.PZ_EDGES, vals=None):
        import uproot
        p = os.path.join(self.d, name + ".root")
        v = np.arange(224, dtype=float).reshape(14, 16) if vals is None else vals
        with uproot.recreate(p) as f:
            f["hXSec2D"] = (v, edges_pt, edges_pz)
        return p

    def test_flatten_is_global_id_order(self):
        np.testing.assert_array_equal(m.th2_values(self.th2("a"), "hXSec2D"), np.arange(224.0))

    def test_wrong_axes_refuse(self):
        bad = m.PT_EDGES.copy()
        bad[3] += 0.01
        with self.assertRaisesRegex(m.Stop, "C-AXES"):
            m.th2_values(self.th2("b", edges_pt=bad), "hXSec2D")

    def unit(self, b, **over):
        meta = {"unit": f"c2_replica_b{b}", "bootstrap_seed": b, "config_sha256": "cfg",
                "controls": {"C-FILL": {"pass": True}}}
        meta.update(over)
        os.makedirs(os.path.join(self.d, "files", "units"), exist_ok=True)
        np.savez_compressed(os.path.join(self.d, "files", "units", f"c2_replica_b{b}.npz"), ks=np.array(m.KS),
                            xsec=np.ones((8, 224)), meta=json.dumps(meta))

    def test_meta_checks(self):
        for b in range(1, m.N_REP + 1):
            self.unit(b)
        self.assertEqual(m.load_ibu(self.d, "cfg").shape, (300, 8, 224))
        for over, word in (({"bootstrap_seed": 7}, "seed"), ({"config_sha256": "zzz"}, "config"),
                           ({"unit": "c2_replica_b9"}, "unit"), ({"controls": {"C-FILL": {"pass": False}}}, "controls")):
            self.unit(5, **over)
            with self.assertRaisesRegex(m.Stop, "C-META"):
                m.load_ibu(self.d, "cfg")
            self.unit(5)

    def test_fetch_tamper_refuses(self):
        os.makedirs(os.path.join(self.d, "files"))
        lines = []
        for i in range(903):
            p = os.path.join(self.d, "files", f"f{i}")
            open(p, "wb").write(bytes([i % 256]))
            lines.append(f"{m.sha_file(p)}  files/f{i}\n")
        open(os.path.join(self.d, "SHA256SUMS"), "w").writelines(lines)
        m.check_fetch(self.d)
        open(os.path.join(self.d, "files", "f17"), "wb").write(b"x")
        with self.assertRaisesRegex(m.Stop, "C-FETCH"):
            m.check_fetch(self.d)

    def test_main_refuses_an_existing_record(self):
        p = os.path.join(self.d, "r.json")
        open(p, "w").close()
        self.assertEqual(m.main([self.d, "--out", p]), 2)

    def test_a_stop_is_recorded_not_raised(self):
        p = os.path.join(self.d, "r.json")
        self.assertEqual(m.main([os.path.join(self.d, "nothing"), "--out", p]), 3)
        rec = json.load(open(p))
        self.assertEqual(rec["status"], "STOP")


if __name__ == "__main__":
    unittest.main(verbosity=2)
