"""fd_1b_binning (A2.1, the director's items 3 and 4): the two offset identities against direct per-row composition
on two binnings, the effect's form, and the seek read against np.load."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import fd_1b_binning as fb  # noqa: E402


class Identities(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(1)
        self.n, rows = 12, 40
        self.c64 = rng.integers(0, self.n, rows)
        self.c32 = self.c64.copy()
        self.moved_idx = [3, 17, 29]
        for k in self.moved_idx:
            self.c32[k] = (self.c64[k] + 1) % self.n
        self.cv = rng.uniform(0.5, 1.5, rows)
        self.tags = ["Flux_0", "MaRES_1", "GEANT_Pion_0", "LowQ2_0", "MinosEfficiency_1"]
        self.bank = {t: self.cv * rng.uniform(0.9, 1.1, rows) for t in self.tags if not t.startswith(("GEANT", "Minos"))}
        self.moved = [(k, int(self.c64[k]), int(self.c32[k]), float(self.cv[k])) for k in self.moved_idx]
        self.rows_u = {t: v[self.moved_idx] for t, v in self.bank.items()}

    def h(self, cells, w):
        return np.bincount(cells, weights=w, minlength=self.n)

    def composite(self, d_of, d_cv):
        d = [d_of(t) for t in self.tags]
        return d[0] + sum(x - d_cv for x in d[1:])

    def test_bound_minus_e2(self):
        d64, d32 = self.h(self.c64, self.cv), self.h(self.c32, self.cv)
        bound = self.composite(lambda t: self.h(self.c32, self.bank[t]) if t in self.bank else d64, d64)
        e2 = self.composite(lambda t: self.h(self.c32, self.bank[t]) if t in self.bank else d32, d32)
        np.testing.assert_allclose(bound - e2, fb.bound_minus_e2(self.tags, fb.delta_cv(self.moved, self.n)),
                                   atol=1e-12)
        np.testing.assert_allclose(fb.delta_cv(self.moved, self.n), d32 - d64, atol=1e-12)
        self.assertEqual(fb.bound_minus_e2(self.tags, np.ones(1))[0], 2.0)        # k - 1 = 4, two detectors after

    def test_e2_minus_f64(self):
        d32 = self.h(self.c32, self.cv)
        e2 = self.composite(lambda t: self.h(self.c32, self.bank[t]) if t in self.bank else d32, d32)
        rows = self.bank[self.tags[0]].copy()
        for t in self.tags[1:]:
            rows += (self.bank[t] if t in self.bank else self.cv) - self.cv
        f64 = self.h(self.c64, rows)
        np.testing.assert_allclose(e2 - f64, fb.e2_minus_f64(self.tags, self.moved, self.rows_u, self.n), atol=1e-12)

    def test_a_detector_first_refuses(self):
        with self.assertRaises(fb.c2.Refusal):
            fb.bound_minus_e2(["GEANT_Pion_0", "Flux_0"], np.ones(2))


class Effect(unittest.TestCase):
    def test_zero_shift_and_the_ratio_form(self):
        edges = [np.array([0, 1, 2.0]), np.array([0, 1.0]), np.array([0, 1.0]), np.array([0, 1.0]), np.array([0, 1.0])]
        const = {"n_nucleons": 1.0, "data_pot": 1.0, "shape": (2, 1, 1, 1, 1), "edges": edges}
        A, B, D = np.array([2.0, 3.0]), np.array([4.0, 3.0]), np.array([5.0, 6.0])
        U, sigma, flux = np.eye(2), np.ones(2), np.array([1.0, 1.0])
        self.assertTrue(np.all(fb.effect(np.zeros(2), A, B, D, flux, const, U, sigma) == 0))
        z = fb.effect(np.array([-0.5, 0.5]), A, B, D, flux, const, U, sigma)
        np.testing.assert_allclose(z, 1e4 * np.array([-0.5 * 2 / 4, 0.5 * 3 / 3]))   # x = 1e4 A D / B
        U1 = np.ones((1, 2))                                       # one reporting cell: cancels only where A/B agree
        self.assertNotEqual(fb.effect(np.array([-0.5, 0.5]), A, B, D, flux, const, U1, np.ones(1))[0], 0)
        A2 = np.array([3.0, 3.0]) * B / B.sum() * 2
        self.assertAlmostEqual(fb.effect(np.array([-0.5, 0.5]), A2, B, D, flux, const, U1, np.ones(1))[0], 0,
                               places=9)


class Seek(unittest.TestCase):
    def test_rows_at_equals_np_load_and_checks_the_pin(self):
        tmp = Path(tempfile.mkdtemp())
        p = tmp / "x_tdw.npy"
        v = np.arange(100, dtype=np.float32) * 0.5
        v[7] = np.nan
        np.save(p, v)
        st = p.stat()
        with mock.patch.object(fb.inv, "NOATIME_FLAG", 0):
            got = fb.rows_at(p, [3, 7, 99], {"size": st.st_size, "mtime_ns": st.st_mtime_ns})
            np.testing.assert_array_equal(got, [1.5, 0.0, 49.5])
            with self.assertRaisesRegex(fb.c2.Refusal, "changed after it was pinned"):
                fb.rows_at(p, [3], {"size": st.st_size + 1, "mtime_ns": st.st_mtime_ns})


import hashlib  # noqa: E402
import json  # noqa: E402

import s1_assemble as sa  # noqa: E402
import test_fd_1b_mc as tmc  # noqa: E402


class Job(tmc.Case):
    def test_main_over_the_toy_world(self):
        inputs = self.inputs
        n = int(np.prod([np.asarray(e).size - 1 for e in inputs["edges"]]))
        cells = fb.mc.td_cells(self.bank_cv, inputs["edges"])
        shape = tuple(np.asarray(e).size - 1 for e in inputs["edges"])
        k = int(np.flatnonzero(cells >= 0)[0])
        u = np.array(np.unravel_index(cells[k], shape))
        u[1] = (u[1] + 1) % shape[1]
        c32 = int(np.ravel_multi_index(tuple(u), shape))
        cvd = {"verdict": "PASS", "checks": {"B_tolerance": {"passes": True, "rows": [[k, int(cells[k]), c32, 1.0]]}}}
        p = self.tmp / "cvd.json"
        p.write_text(json.dumps(cvd))
        fm = np.arange(n) % sa.N_CELLS
        U = np.vstack([np.where(fm == c, 1.0, 0.0) for c in range(sa.N_CELLS)])
        s1 = {"U": U, "f": np.ones(sa.N_CELLS)}
        out = self.tmp / "binning.json"
        sha = lambda q: hashlib.sha256(Path(q).read_bytes()).hexdigest()  # noqa: E731
        argv = ["--npz", str(self.w.inputs), "--bank", str(self.w.bank), "--detector-dir", str(self.w.det),
                "--pins", str(self.w.pins), "--flux-constraint", str(self.w.constraint), "--definition", "d",
                "--staged", str(self.tmp), "--prep", str(self.tmp), "--cvdenom", str(p), "--out", str(out),
                "--expect-pins-sha256", sha(self.w.pins), "--expect-cvdenom-sha256", sha(p)]
        r = np.random.default_rng(3).uniform(0.8, 1.2, inputs["w_truth"].shape[0])
        with mock.patch.object(sa, "INPUT_NPZ_SHA256", sha(self.w.inputs)), \
                mock.patch.object(fb.inv, "load_inputs", lambda q: dict(inputs)), \
                mock.patch.object(sa, "fine_map", lambda q: fm), mock.patch.object(sa, "functional_matrix", lambda f: U), \
                mock.patch.object(fb.mc, "via_noatime", lambda f, q: s1 if f is fb.fs.load_s1 else f(q)), \
                mock.patch.object(fb.fs, "reported_matrix", lambda s: np.eye(sa.N_CELLS) * 1e-80), \
                mock.patch.object(fb.mc, "truth_ratio", lambda t, q: (None, None)), \
                mock.patch.object(fb.mc, "truth_weight", lambda t, i, ra, pu: r), \
                mock.patch.object(fb.mc, "TOY_SEEDS", {"g18": [3_620_000, 3_620_001], "ar23": [3_630_000]}):
            self.assertEqual(fb.main(argv), 0)
        rec = json.loads(out.read_text())
        self.assertEqual(rec["moved_rows"], 1)
        self.assertEqual(rec["item3"][0]["same_reporting_cell"], bool(fm[cells[k]] == fm[c32]))
        self.assertEqual(rec["item4"]["g18"]["draws"], 2)
        self.assertEqual(len(rec["item4"]["ar23"]["e2_vs_float64"]["per_cell_max"]), sa.N_CELLS)
        self.assertGreater(rec["item4"]["g18"]["amendment_2_as_bound_vs_float64"]["largest"],
                           rec["item4"]["g18"]["e2_vs_float64"]["largest"])
        self.assertEqual(set(rec["nominal_basis_f32_minus_f64_sigma"]), {"nominal", "g18", "ar23"})


if __name__ == "__main__":
    unittest.main()
