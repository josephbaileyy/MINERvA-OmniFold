"""cov2d (the bank, draws, first-order composition, N1, lambda+) and cov2d_receipt on synthetic omnifiles.
Needs numpy, uproot 5.6.9 and PyROOT (the receipt imports re2_driver for the truth phase space). From the checkout:
    python -B -m pytest -q 2d-unfolding/cov2d/tests/test_cov2d.py
"""
from __future__ import annotations

import contextlib
import io
import itertools
import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE.parent))
import cov2d as c  # noqa: E402

PARTB_RUNS = REPO / "docs/orchestration/state/2d-closeout/stageF/methods/re2/run/partb_runs.tsv"
W_FLUX = np.linspace(0.5, 1.5, 100)


def noatime():
    return mock.patch.object(os, "O_NOATIME", getattr(os, "O_NOATIME", 0), create=True)


class Bank(unittest.TestCase):
    def test_bank_is_part_b_universe_block(self):
        labels = set()
        for line in PARTB_RUNS.read_text().splitlines()[1:]:
            f = line.split("\t")
            if f[0].startswith("J2"):
                a = f[5].split()
                labels.add(a[a.index("--universe") + 1])
        mine = {f"{b}:{i}" for b in c.ORDER for i in range(c.BANDS[b])}
        self.assertEqual(mine, labels)
        self.assertEqual((len(c.BANDS), c.N_UNIVERSES), (38, 175))
        self.assertEqual(c.ORDER[0], c.FLUX)
        self.assertEqual(list(c.ORDER[1:]), sorted(c.ORDER[1:]))

    def test_flux_weights(self):
        text = "\n".join(f"Flux {i} {w!r}" for i, w in enumerate(W_FLUX)) + "\nOther 3 1.0\n"
        np.testing.assert_array_equal(c.flux_weights(text), W_FLUX)
        with self.assertRaises(c.Refusal):
            c.flux_weights("\n".join(f"Flux {i} 1.0" for i in range(99)))
        with self.assertRaises(c.Refusal):
            c.flux_weights("\n".join(f"Flux {i} {-1.0 if i == 7 else 1.0}" for i in range(100)))

    def test_seeds(self):
        g, a = c.TOY_SEEDS["G18"], c.TOY_SEEDS["AR23"]
        self.assertEqual((len(g), len(a)), (300, 300))
        others = {c.REALIZATION_SEED["G18"], c.REALIZATION_SEED["AR23"], c.NULL_SEED}
        self.assertFalse(set(g) & set(a) or (set(g) | set(a)) & others)


class Draws(unittest.TestCase):
    def test_deterministic_and_ordered(self):
        d1, d2 = c.draw(5_720_017, W_FLUX), c.draw(5_720_017, W_FLUX)
        self.assertEqual(d1, d2)
        self.assertEqual([b for b, _ in d1.universes], list(c.ORDER))
        for b, i in d1.universes:
            self.assertTrue(0 <= i < c.BANDS[b])
        self.assertEqual(len(d1.lateral_signs), len(c.LATERAL_BANDS))
        self.assertTrue(set(d1.lateral_signs) <= {-1, 1})
        self.assertNotEqual(c.draw(5_720_018, W_FLUX), d1)

    def test_generator_is_seed_and_salt(self):
        d = c.draw(5_730_123, W_FLUX)
        rng = np.random.default_rng([5_730_123, c.DRAW_SALT])
        want = [(c.FLUX, int(rng.choice(100, p=W_FLUX / W_FLUX.sum())))]
        want += [(b, int(rng.integers(c.BANDS[b]))) for b in c.ORDER[1:]]
        self.assertEqual(list(d.universes), want)
        self.assertEqual(d.lateral_signs, tuple(int(x) for x in rng.choice((-1, 1), size=5)))
        self.assertEqual(d.norm_z, float(rng.standard_normal()))

    def test_flux_probability(self):
        w = np.zeros(100)
        w[[3, 61]] = [1.0, 3.0]
        got = [c.draw(s, w).universes[0][1] for s in range(4000)]
        self.assertEqual(set(got), {3, 61})
        self.assertAlmostEqual(got.count(61) / 4000, 0.75, delta=0.03)

    def test_pair_bands_uniform(self):
        got = [c.draw(s, W_FLUX).universes[1:] for s in range(2000)]
        for k, b in enumerate(c.ORDER[1:]):
            counts = np.bincount([g[k][1] for g in got], minlength=c.BANDS[b])
            self.assertTrue(np.all(np.abs(counts / 2000 - 1 / c.BANDS[b]) < 0.05), (b, counts))


class Compose(unittest.TestCase):
    def setUp(self):
        r = np.random.default_rng(1)
        self.cv = r.normal(1, 0.5, 50)
        self.cv[3] = 0.0
        self.u = [r.normal(1, 0.5, 50) for _ in range(4)]

    def test_one_universe_is_bitwise(self):
        got = c.compose(self.cv, [self.u[0]])
        self.assertTrue(np.array_equal(got.view(np.uint64), self.u[0].view(np.uint64)))
        self.assertIsNot(got, self.u[0])

    def test_first_order_in_draw_order(self):
        want = self.u[0].copy()
        for a in self.u[1:]:
            want += a - self.cv
        got = c.compose(self.cv, self.u)
        self.assertTrue(np.array_equal(got.view(np.uint64), want.view(np.uint64)))
        np.testing.assert_allclose(got, self.cv + sum(a - self.cv for a in self.u), rtol=1e-12, atol=1e-12)
        self.assertEqual(got[3], sum(a[3] for a in self.u))     # a_CV = 0: the sum of the universes

    def test_refuses_empty(self):
        with self.assertRaises(c.Refusal):
            c.compose(self.cv, [])

    def test_n1_conventions(self):
        got = c.n1_composite(np.array([0.0, 2.0, -3.0, 1.0]), np.array([0.0, 0.0, 1.5, 4.0]))
        np.testing.assert_array_equal(got, [1.0, np.inf, 2.0, 0.25])
        self.assertFalse(np.any(np.isnan(got)))

    def test_bound_is_never_below_the_exact_maximum(self):
        r = np.random.default_rng(7)
        sizes = (3, 2, 2, 2)
        for trial in range(30):
            n = 40
            cv = r.normal(0.5, 0.6, n)
            cv[:3] = 0.0
            bands = [r.normal(0.5, 0.8, (k, n)) for k in sizes]
            bands[1][:, 4] = 0.0
            bands[2][:, 5] = 0.0
            bands[3][:, 5] = 0.0
            bands[0][:, 5] = 0.0
            cv[5] = 0.0
            exact = np.zeros(n)
            for pick in itertools.product(*[range(k) for k in sizes]):
                univ = [bands[b][i] for b, i in enumerate(pick)]
                exact = np.maximum(exact, c.n1_composite(c.compose(cv, univ), c.peak(univ)))
            bound = c.all_draws_bound(cv, bands)
            self.assertTrue(np.all(bound >= exact * (1 - 1e-12)), trial)

    def test_lam_plus(self):
        lam, rec = c.lam_plus(np.array([1.5, -0.25, 0.0, -1.0, 2.0]))
        np.testing.assert_array_equal(lam, [1.5, 0.0, 0.0, 0.0, 2.0])
        self.assertEqual(rec, {"sum_lambda": 2.25, "sum_lambda_neg": -1.25, "rows_neg": 2})

    def test_sha256_through_noatime(self):
        with tempfile.NamedTemporaryFile(delete=False) as fh:
            fh.write(b"cov2d")
        try:
            sentinel = 1 << 29
            calls = []
            real = os.open
            with mock.patch.object(os, "O_NOATIME", sentinel, create=True), \
                    mock.patch.object(os, "open", lambda p, fl, *a: calls.append(fl) or real(p, os.O_RDONLY)):
                got = c.sha256_file(fh.name)
            self.assertEqual(calls, [os.O_RDONLY | sentinel])
            import hashlib
            self.assertEqual(got, hashlib.sha256(b"cov2d").hexdigest())
        finally:
            os.unlink(fh.name)


# ----------------------------------------------------------------------------------------------- the receipt
try:
    import ROOT  # noqa: F401
    import uproot  # noqa: F401
    HAVE = True
except Exception:  # pragma: no cover
    HAVE = False


def ratio_json(seed: int) -> dict:
    sys.path.insert(0, str(REPO / "nd-unfolding" / "pv-ladder"))
    import pvl_lib
    edges = [list(pvl_lib.FINE[a]) for a in pvl_lib.AXES5]
    n = int(np.prod([len(e) - 1 for e in edges]))
    rho = np.random.default_rng(seed).uniform(0.8, 1.25, n)
    return {"schema": "s5e-shape-ratio/1", "axes": [0, 1, 2, 3, 4], "edges": edges, "shape_ratio": rho.tolist(),
            "k": 1.0}


class World:
    """A synthetic universe omnifile: each tree's CV weight and 175 universe columns, mc_truth_denom's five truth
    variables. ``factor`` maps (tree, band, idx) to a per-row multiplier of the CV, applied after a mild default."""

    def __init__(self, d: Path, n: int = 1500, seed: int = 3):
        self.d, self.n = d, n
        r = np.random.default_rng(seed)
        self.r = r
        self.trees = {}
        for tree, pre in (("mc_signal_reco", "w_reco"), ("mc_truth_denom", "w_truth"), ("mc_background", "w_bkg")):
            cv = r.uniform(0.2, 1.5, n)
            cols = {pre: cv}
            for b in c.ORDER:
                for i in range(c.BANDS[b]):
                    cols[c.column(pre, b, i)] = cv * r.uniform(0.97, 1.03, n)
            self.trees[tree] = cols
        td = self.trees["mc_truth_denom"]
        td["MC"] = r.uniform(0.0, 2.4, n)
        td["MC_pz"] = r.uniform(1.6, 25.0, n)
        td["MC_eavail"], td["MC_q3"], td["MC_W"] = r.uniform(0, 2, n), r.uniform(0, 2.5, n), r.uniform(0.9, 3, n)

    def write(self) -> dict:
        import uproot
        uni = self.d / "uni.root"
        with uproot.recreate(uni) as f:
            for tree, cols in self.trees.items():
                f.mktree(tree, {k: v.dtype for k, v in cols.items()}).extend(cols)
        prep = self.d / "prep"
        (prep / "bridged").mkdir(parents=True, exist_ok=True)
        for k, name in enumerate(("genie_v3_g18", "genie_v3_ar23")):
            (prep / "bridged" / f"{name}.json").write_text(json.dumps(ratio_json(11 + k)))
        cons = self.d / "constraint.txt"
        cons.write_text("\n".join(f"Flux {i} {w!r}" for i, w in enumerate(W_FLUX)) + "\n")
        future = time.time() + 86400
        for p in [uni, cons] + list((prep / "bridged").glob("*.json")):
            os.utime(p, (future, os.stat(p).st_mtime))
        return {"uni": uni, "prep": prep, "cons": cons}


@unittest.skipUnless(HAVE, "needs PyROOT and uproot")
class Receipt(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        p = noatime()
        p.start()
        self.addCleanup(p.stop)
        import cov2d_receipt
        self.rc = cov2d_receipt

    def run_receipt(self, world: World, chunk: int = 400):
        paths = world.write()
        out = Path(self.tmp.name) / "receipt.json"
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = self.rc.main(["--out", str(out), "--uni", str(paths["uni"]), "--prep", str(paths["prep"]),
                                 "--constraint", str(paths["cons"]), "--chunk", str(chunk), "--no-pins"])
        return code, json.loads(out.read_text()), buf.getvalue()

    def test_mild_bank_passes_and_every_row_is_evaluated(self):
        w = World(Path(self.tmp.name))
        code, rec, text = self.run_receipt(w)
        self.assertEqual(code, 0, rec["stop"])
        self.assertEqual(rec["verdict"], "PASS")
        self.assertIn("COV2D-RECEIPT PASS", text)
        self.assertEqual(rec["n_draws"], 600)
        for name in ("wr", "wt", "bkgw"):
            self.assertEqual(rec["n1"][name]["rows"], w.n)
            self.assertEqual(rec["n1"][name]["rows_above"], 0)
        self.assertEqual(rec["atime_moved"], [])

    def set_row(self, w: World, tree: str, row: int, cv: float, factor: float):
        pre = {"mc_signal_reco": "w_reco", "mc_truth_denom": "w_truth", "mc_background": "w_bkg"}[tree]
        cols = w.trees[tree]
        cols[pre][row] = cv
        for b in c.ORDER:
            for i in range(c.BANDS[b]):
                cols[c.column(pre, b, i)][row] = cv * factor

    def test_compounding_row_stops(self):
        w = World(Path(self.tmp.name))
        self.set_row(w, "mc_background", 917, 0.4, 1.5)       # (1 + 38 x 0.5) / 1.5 = 13.3 at every draw
        code, rec, _ = self.run_receipt(w)
        self.assertEqual(code, 3)
        self.assertEqual(rec["n1"]["bkgw"]["rows_above"], 1)
        self.assertEqual(rec["n1"]["bkgw"]["above"][0]["row"], 917)
        self.assertAlmostEqual(rec["n1"]["bkgw"]["above"][0]["composite"], 20 / 1.5, places=9)
        self.assertEqual(rec["n1"]["wr"]["rows_above"], 0)

    def test_the_bound_is_exact_at_the_edge(self):
        for eps, rows in ((1e-6, 1), (-1e-6, 0)):
            with self.subTest(eps=eps):
                w = World(Path(self.tmp.name), seed=5)
                d = (9 + eps) / (28 - eps)                     # (1 + 38 d) / (1 + d) = 10 + eps
                self.set_row(w, "mc_signal_reco", 401, 0.8, 1 + d)
                code, rec, _ = self.run_receipt(w)
                self.assertEqual(rec["n1"]["wr"]["rows_above"], rows)
                self.assertEqual(code, 3 if rows else 0)

    def test_an_unequal_band_is_not_certified_by_its_largest_universe(self):
        w = World(Path(self.tmp.name), seed=6)
        self.set_row(w, "mc_signal_reco", 222, 1.0, 1.4)       # every universe 1.4 x the CV of 1.0
        w.trees["mc_signal_reco"]["w_reco_LowQ2_0"][222] = 6.0
        # LowQ2_1 draws: (1 + 38 x 0.4) / 1.4 = 11.57; LowQ2_0 draws: (1 + 37 x 0.4 + 5) / 6 = 3.47
        code, rec, _ = self.run_receipt(w)
        self.assertEqual(code, 3)
        self.assertEqual(rec["n1"]["wr"]["rows_above"], 1)
        self.assertAlmostEqual(rec["n1"]["wr"]["above"][0]["composite"], 16.2 / 1.4, places=9)

    def test_negative_composites_are_counted(self):
        w = World(Path(self.tmp.name))
        cols = w.trees["mc_signal_reco"]
        cols["w_reco_LowQ2_1"][:10] = -0.5 * cols["w_reco"][:10]
        code, rec, _ = self.run_receipt(w)
        self.assertGreater(rec["n1"]["wr"]["neg_rows"], 0)
        self.assertGreater(rec["n1"]["wr"]["neg_pairs"], 0)
        self.assertEqual(rec["n1"]["bkgw"]["neg_rows"], 0)

    def test_nonfinite_weights_are_zeroed_and_counted(self):
        w = World(Path(self.tmp.name))
        w.trees["mc_signal_reco"]["w_reco_MaRES_0"][[5, 6]] = np.nan
        code, rec, _ = self.run_receipt(w)
        self.assertEqual(rec["n1"]["wr"]["nonfinite_zeroed"], 2)

    def test_a_nonpositive_truth_cell_stops(self):
        w = World(Path(self.tmp.name))
        td = w.trees["mc_truth_denom"]
        td["MC"][:] = np.where(np.arange(w.n) < 40, 0.30, td["MC"])
        td["MC_pz"][:] = np.where(np.arange(w.n) < 40, 7.5, td["MC_pz"])
        for b in ("MaRES", "LowQ2"):
            for i in range(2):
                td[c.column("w_truth", b, i)][:40] = -3.0 * td["w_truth"][:40]
        code, rec, text = self.run_receipt(w)
        self.assertEqual(code, 3)
        self.assertGreater(rec["truth_cells"]["G18"]["draws_with_nonpositive_cell"], 0)
        self.assertIn("truth cells", text)

    def test_truth_cells_are_recomputed_independently(self):
        import pvl_lib
        import s5e_deform
        w = World(Path(self.tmp.name), seed=8)
        code, rec, _ = self.run_receipt(w)
        td = w.trees["mc_truth_denom"]
        gen = np.stack([td[k] for k in ("MC", "MC_pz", "MC_eavail", "MC_q3", "MC_W")], axis=1)
        cell = self.rc.truth_cell(gen[:, 0], gen[:, 1])
        ok = cell >= 0
        for k, tune in enumerate(("G18", "AR23")):
            r = s5e_deform.ratio_weight(gen, [pvl_lib.FINE[a] for a in pvl_lib.AXES5], td["w_truth"],
                                        ratio_json(11 + k), 1.0)
            h = lambda col: np.bincount(cell[ok], weights=(td[col] * r)[ok], minlength=224)
            h_cv = h("w_truth")
            pos = h_cv > 0
            worst = np.inf
            for d in c.declared_draws(tune, W_FLUX):
                H = c.compose(h_cv, [h(c.column("w_truth", b, i)) for b, i in d.universes])
                worst = min(worst, float(np.min(H[pos] / h_cv[pos])))
            self.assertAlmostEqual(rec["truth_cells"][tune]["min_cell_ratio_to_cv"], worst, places=12)
            self.assertAlmostEqual(rec["truth_cells"][tune]["r_min"], float(r.min()), places=14)
            self.assertEqual(rec["truth_cells"][tune]["cv_total"], float(h_cv.sum()))
            self.assertNotEqual(float(h_cv.sum()), float(np.bincount(cell[ok], weights=td["w_truth"][ok]).sum()))

    def test_driver_names_without_root_equal_the_import(self):
        import re2_driver as drv
        ns = self.rc.driver_phase_space()
        self.assertEqual((ns["PT_EDGES"], ns["PZ_EDGES"], ns["MAX_MUON_THETA_RAD"]),
                         (drv.PT_EDGES, drv.PZ_EDGES, drv.MAX_MUON_THETA_RAD))
        r = np.random.default_rng(13)
        lim = (drv.PT_EDGES[0], drv.PT_EDGES[-1], drv.PZ_EDGES[0], drv.PZ_EDGES[-1])
        for a, b in zip(r.uniform(-0.2, 5.0, 4000), r.uniform(0.5, 65.0, 4000)):
            self.assertEqual(ns["in_truth_phase_space"](a, b, *lim), drv.in_truth_phase_space(a, b, *lim))
        self.assertNotIn("ROOT", ns)

    def test_truth_cell_matches_a_th2d(self):
        import ROOT
        import re2_driver as drv
        r = np.random.default_rng(9)
        pt = np.concatenate([r.uniform(-0.1, 4.7, 3000), np.array(drv.PT_EDGES), [0.3, 0.3]])
        pz = np.concatenate([r.uniform(1.0, 62.0, 3000), np.full(len(drv.PT_EDGES), 20.0), [60.0, 1.5]])
        cell = self.rc.truth_cell(pt, pz)
        h = ROOT.TH2D("h_tc", "", len(drv.PT_EDGES) - 1, np.array(drv.PT_EDGES, float), len(drv.PZ_EDGES) - 1,
                      np.array(drv.PZ_EDGES, float))
        nz = len(drv.PZ_EDGES) - 1
        for a, b, k in zip(pt, pz, cell):
            ok = drv.in_truth_phase_space(a, b, drv.PT_EDGES[0], drv.PT_EDGES[-1], drv.PZ_EDGES[0], drv.PZ_EDGES[-1])
            bx, by = h.GetXaxis().FindFixBin(a), h.GetYaxis().FindFixBin(b)
            inside = 1 <= bx <= len(drv.PT_EDGES) - 1 and 1 <= by <= nz
            want = (bx - 1) * nz + (by - 1) if (ok and inside) else -1
            self.assertEqual(int(k), want, (a, b))

    def test_atime_move_stops(self):
        w = World(Path(self.tmp.name))
        real = self.rc.atime
        calls = {"n": 0}

        def moving(p):
            calls["n"] += 1
            return real(p) + (1 if calls["n"] > 4 and str(p).endswith("uni.root") else 0)

        with mock.patch.object(self.rc, "atime", moving):
            code, rec, _ = self.run_receipt(w)
        self.assertEqual(code, 3)
        self.assertEqual(len(rec["atime_moved"]), 1)


if __name__ == "__main__":
    unittest.main()
