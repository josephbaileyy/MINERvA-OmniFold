"""Controls for s5p_nullexp's nuisance factors (review round 1): the interaction-model universe is applied to the
signal source's response with the source truth unchanged per fine cell (F6); the model-universe list excludes
the flux and the detector (GEANT) bands, so no detector band is applied twice; the factors are the products of
the declared universe ratios."""
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(1, str(Path(__file__).resolve().parents[1]))
import s5p_nullexp as ne  # noqa: E402

EDGES = [np.array([0.0, 1.0, 2.0]), np.array([0.0, 1.0, 2.0]), np.array([0.0, 0.5, 1.0]),
         np.array([0.0, 1.0, 2.0, 3.0]), np.array([0.0, 1.5, 3.0])]


def inputs(n=5000, seed=0):
    rng = np.random.default_rng(seed)
    gen = np.column_stack([rng.uniform(0, 2, n), rng.uniform(0, 2, n), rng.uniform(0, 1, n),
                           rng.uniform(0, 3, n), rng.uniform(0, 3, n)])
    gen[:20] = -9999.0
    pass_truth = np.ones(n, bool)
    pass_truth[:20] = False
    return {"MCgen": gen, "edges": EDGES, "w_truth": rng.uniform(0.5, 1.5, n), "w_reco": rng.uniform(0.2, 1.0, n),
            "pass_truth": pass_truth}


def fine_flat(inp):
    ok, idx = ne.s5p_truths.cell_of(inp["MCgen"], EDGES)
    return ok, np.ravel_multi_index(idx, [len(e) - 1 for e in EDGES])


class Tests(unittest.TestCase):
    def test_truth_preserving_keeps_every_source_fine_cell_truth(self):
        inp = inputs()
        rng = np.random.default_rng(1)
        k = rng.uniform(0.7, 1.4, inp["w_truth"].size)
        source = rng.uniform(size=k.size) < 0.5
        g = ne.truth_preserving(k, inp, source)
        ok, flat = fine_flat(inp)
        wt = inp["w_truth"][ok]
        s = source[ok]
        before = np.bincount(flat[s], weights=wt[s], minlength=144)
        after = np.bincount(flat[s], weights=(wt * k[ok] * g[ok])[s], minlength=144)
        np.testing.assert_allclose(after, before, rtol=1e-12)
        self.assertTrue(np.all(g[:20] == 1.0))
        self.assertGreater(np.std(g[ok]), 0.0)  # it acts: a non-trivial renormalization

    def test_model_bands_exclude_flux_and_detector_bands(self):
        with tempfile.TemporaryDirectory() as d:
            for b in ("Flux_3", "GEANT_Proton_0", "GEANT_Pion_1", "MaRES_1", "2p2h_0", "FrAbs_pi_0"):
                np.save(Path(d) / f"{b}_bkgw.npy", np.ones(3))
            self.assertEqual(ne.model_bands(Path(d)), ["2p2h_0", "FrAbs_pi_0", "MaRES_1"])

    def test_source_factors_are_the_declared_products(self):
        inp = inputs()
        n = inp["w_truth"].size
        nb = 300
        rng = np.random.default_rng(2)
        bkg = {"bkg_w": rng.uniform(0.1, 1.0, nb)}
        source = rng.uniform(size=n) < 0.5
        with tempfile.TemporaryDirectory() as d:
            bank, det = Path(d) / "bank", Path(d) / "det"
            bank.mkdir()
            det.mkdir()
            u = {}
            for tag, where in (("Flux_7", bank), ("MaRES_1", bank)) + tuple((f"{b}_1", det) for b in ne.DETECTOR_BANDS):
                u[tag] = {"wt": inp["w_truth"] * rng.uniform(0.8, 1.2, n), "wr": inp["w_reco"] * rng.uniform(0.8, 1.2, n),
                          "bkgw": bkg["bkg_w"] * rng.uniform(0.8, 1.2, nb)}
                for key, v in u[tag].items():
                    np.save(where / f"{tag}_{key}.npy", v)
                np.save(where / f"{tag}_{'tdw' if where == bank else 'denom_nd'}.npy", np.ones(4))
            d_ = {"flux": 7, "model": {"MaRES": "MaRES_1"}, "detector": {b: 1 for b in ne.DETECTOR_BANDS}}
            fs, fb = ne.source_factors(d_, inp, bkg, bank, det, source)
        wr, bw = inp["w_reco"], bkg["bkg_w"]
        g = ne.truth_preserving(u["MaRES_1"]["wt"] / inp["w_truth"], inp, source)
        want_s = u["Flux_7"]["wr"] / wr * u["MaRES_1"]["wr"] / wr * g
        want_b = u["Flux_7"]["bkgw"] / bw * u["MaRES_1"]["bkgw"] / bw
        for b in ne.DETECTOR_BANDS:
            want_s = want_s * u[f"{b}_1"]["wr"] / wr
            want_b = want_b * u[f"{b}_1"]["bkgw"] / bw
        np.testing.assert_allclose(fs, want_s, rtol=1e-12)
        np.testing.assert_allclose(fb, want_b, rtol=1e-12)

    def test_expectation_build_is_the_poisson_mean_and_quarter_halves_the_unfolding_mc(self):
        inp = inputs(n=4000, seed=5)
        rng = np.random.default_rng(6)
        n = inp["w_truth"].size
        inp.update({"MCreco": inp["MCgen"] + rng.normal(scale=0.05, size=(n, 5)), "pass_reco": rng.uniform(size=n) < 0.8,
                    "denom_nd": np.full(tuple(len(e) - 1 for e in EDGES), 50.0), "flux": np.ones(2), "data_pot": 1.0,
                    "n_nucleons": 1.0})
        inp["MCreco"][:20] = 0.5
        nb = 500
        bkg = {"bkg_reco": np.column_stack([rng.uniform(0, 2, nb), rng.uniform(0, 2, nb), rng.uniform(0, 1, nb),
                                            rng.uniform(0, 3, nb), rng.uniform(0, 3, nb)]),
               "bkg_w": rng.uniform(0.1, 1.0, nb), "bkg_nd": None}
        r_h = rng.uniform(0.8, 1.2, n)
        orig = ne.s5n_pseudo.truth_weight
        ne.s5n_pseudo.truth_weight = lambda name, i, amp, rr: r_h
        try:
            exp, _, _ = ne.build(inp, bkg, 11, 123, True, "half")
            expq, _, infoq = ne.build(inp, bkg, 11, 123, True, "quarter")
            exp_p, _, _ = ne.build(inp, bkg, 11, 123, False, "half")
        finally:
            ne.s5n_pseudo.truth_weight = orig
        is_b = ne.s5c_pseudo.half_mask(n, 11)
        is_c = ne.s5c_pseudo.half_mask(nb, ne.s5n_pseudo.bkg_split_key(11))
        b_reco = is_b & inp["pass_reco"]
        want = np.concatenate([2.0 * inp["w_reco"][b_reco] * r_h[b_reco], 2.0 * bkg["bkg_w"][is_c]])
        coords = np.concatenate([inp["MCreco"][b_reco], bkg["bkg_reco"][is_c]])
        keep = ne.s5n_pseudo.fid_mask(coords, EDGES)
        np.testing.assert_allclose(exp["obs_counts"], want[keep], rtol=1e-12)
        self.assertFalse(np.allclose(exp_p["obs_counts"][:50], exp["obs_counts"][:50]))  # the Poisson path is untouched
        self.assertIs(ne.np.random.default_rng, np.random.default_rng)
        a = ~is_b
        self.assertEqual(exp["MCgen"].shape[0], int(a.sum()))
        self.assertEqual(expq["MCgen"].shape[0], infoq["n_unfolding_mc"])
        self.assertLess(abs(expq["MCgen"].shape[0] / a.sum() - 0.5), 0.05)
        self.assertAlmostEqual(expq["w_truth"].sum() / exp["w_truth"].sum(), 1.0, delta=0.05)
        np.testing.assert_allclose(expq["obs_counts"], exp["obs_counts"], rtol=0)

    def test_detector_source_prefers_the_dump_then_the_bank_and_refuses_a_missing_band(self):
        with tempfile.TemporaryDirectory() as d:
            bank, det = Path(d) / "bank", Path(d) / "det"
            bank.mkdir()
            det.mkdir()
            np.save(bank / "GEANT_Pion_1_wr.npy", np.ones(2))
            np.save(bank / "MinosEfficiency_1_wr.npy", np.ones(2))
            np.save(det / "MinosEfficiency_1_wr.npy", np.ones(2))
            self.assertEqual(ne.detector_source(det, bank, "MinosEfficiency_1"), det)
            self.assertEqual(ne.detector_source(det, bank, "GEANT_Pion_1"), bank)
            self.assertEqual(ne.detector_source(None, bank, "GEANT_Pion_1"), bank)
            with self.assertRaises(FileNotFoundError):
                ne.detector_source(None, bank, "GEANT_Proton_0")

    def test_draw_covers_exactly_the_declared_detector_bands(self):
        rng = np.random.default_rng(3)
        g = ne.model_groups(["MaRES_0", "MaRES_1"])
        d = ne.draw(rng, [1, 2], g, ("GEANT_Pion", "GEANT_Proton"))
        self.assertEqual(set(d["detector"]), {"GEANT_Pion", "GEANT_Proton"})
        self.assertEqual(set(ne.draw(rng, [1], g)["detector"]), set(ne.DETECTOR_BANDS))

    def test_model_groups(self):
        g = ne.model_groups(["2p2h_0", "2p2h_1", "2p2h_2", "MaRES_0", "MaRES_1", "FrAbs_pi_0", "FrAbs_pi_1"])
        self.assertEqual(g, {"2p2h": ["2p2h_0", "2p2h_1", "2p2h_2"], "FrAbs_pi": ["FrAbs_pi_0", "FrAbs_pi_1"],
                             "MaRES": ["MaRES_0", "MaRES_1"]})
        with self.assertRaises(ValueError):
            ne.model_groups(["cv"])

    def test_every_band_is_drawn_and_the_prior_variance_is_the_band_sum(self):
        """Review round 2 H1: the drawn interaction-model prior must carry the band-sum covariance (MAT: per band
        the mean over its universes of (u - cv)^2), not one universe of all bands."""
        inp = inputs(n=3000, seed=8)
        rng = np.random.default_rng(9)
        n = inp["w_truth"].size
        bkg = {"bkg_w": rng.uniform(0.1, 1.0, 200)}
        eps = {"A": 0.05, "B": 0.03, "C": 0.08}
        pattern = {k: rng.normal(size=n) * 0.2 + 1.0 for k in eps}  # a row pattern, so the effect is not flat
        with tempfile.TemporaryDirectory() as d:
            bank = Path(d)
            unis = []
            for k, e in eps.items():
                for i, s in enumerate((+1, -1)):
                    u = f"{k}_{i}"
                    unis.append(u)
                    np.save(bank / f"{u}_wr.npy", inp["w_reco"] * (1 + s * e * pattern[k]))
                    np.save(bank / f"{u}_wt.npy", inp["w_truth"])
                    np.save(bank / f"{u}_tdw.npy", np.ones(4))
                    np.save(bank / f"{u}_bkgw.npy", bkg["bkg_w"] * (1 + s * e))
            groups = ne.model_groups(unis)
            cache = ne.ModelCache(bank, unis, inp, bkg, preload=True)
            S = []
            draws = [ne.draw(np.random.default_rng([s, 1]), [0], groups, ())["model"] for s in range(3000)]
            self.assertTrue(all(set(m) == set(eps) for m in draws))  # every band, every experiment
            for m in draws:
                k_wr, _, k_b = cache.product(list(m.values()))
                S.append((inp["w_reco"] * k_wr).sum())
        cv = inp["w_reco"].sum()
        band_sum = sum((((inp["w_reco"] * e * pattern[k]).sum()) ** 2) for k, e in eps.items())
        self.assertAlmostEqual(np.var(S) / band_sum, 1.0, delta=0.08)
        self.assertAlmostEqual(np.mean(S) / cv, 1.0, delta=0.003)

    def test_streaming_and_preloaded_products_agree(self):
        inp = inputs(n=500, seed=10)
        bkg = {"bkg_w": np.random.default_rng(11).uniform(0.1, 1.0, 50)}
        with tempfile.TemporaryDirectory() as d:
            bank = Path(d)
            for i, u in enumerate(("X_0", "X_1", "Y_0", "Y_1")):
                np.save(bank / f"{u}_wr.npy", inp["w_reco"] * (1 + 0.01 * (i + 1)))
                np.save(bank / f"{u}_wt.npy", inp["w_truth"] * (1 - 0.01 * i))
                np.save(bank / f"{u}_tdw.npy", np.ones(4))
                np.save(bank / f"{u}_bkgw.npy", bkg["bkg_w"] * (1 + 0.02 * i))
            a = ne.ModelCache(bank, ["X_0", "X_1", "Y_0", "Y_1"], inp, bkg, preload=True).product(["X_1", "Y_0"])
            b = ne.ModelCache(bank, ["X_0", "X_1", "Y_0", "Y_1"], inp, bkg).product(["X_1", "Y_0"])
        for x, y in zip(a, b):
            np.testing.assert_array_equal(x, y)

    def test_drawn_detector_bands_none_without_nuisance_and_checked_with(self):
        with tempfile.TemporaryDirectory() as d:
            bank = Path(d)
            np.save(bank / "GEANT_Pion_0_wr.npy", np.ones(2))
            np.save(bank / "GEANT_Pion_1_wr.npy", np.ones(2))
            self.assertEqual(ne.drawn_detector_bands("MinosEfficiency,GEANT_Pion", True, None, bank), ())
            self.assertEqual(ne.drawn_detector_bands("GEANT_Pion", False, None, bank), ("GEANT_Pion",))
            with self.assertRaises(FileNotFoundError):
                ne.drawn_detector_bands("MinosEfficiency,GEANT_Pion", False, None, bank)

    def test_negative_universe_weights_are_clipped_and_counted(self):
        inp = inputs(n=400, seed=14)
        rng = np.random.default_rng(15)
        bkg = {"bkg_w": rng.uniform(0.1, 1.0, 30)}
        with tempfile.TemporaryDirectory() as d:
            bank = Path(d)
            wr_bad = inp["w_reco"].copy()
            wr_bad[:7] *= -3.0
            for u, wrx in (("LowQ2_1", wr_bad), ("Flux_2", inp["w_reco"])):
                np.save(bank / f"{u}_wr.npy", wrx)
                np.save(bank / f"{u}_wt.npy", inp["w_truth"])
                np.save(bank / f"{u}_tdw.npy", np.ones(4))
                np.save(bank / f"{u}_bkgw.npy", bkg["bkg_w"])
            d_ = {"flux": 2, "model": {"LowQ2": "LowQ2_1"}, "detector": {}}
            fs, fb = ne.source_factors(d_, inp, bkg, bank, None)
        self.assertTrue(np.all(fs >= 0) and np.all(np.isfinite(fs)))
        self.assertEqual(d_["clipped_rows"]["signal"], 7)
        self.assertTrue(np.all(fs[:7] == 0.0))


if __name__ == "__main__":
    unittest.main()
