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
            d_ = {"flux": 7, "model_universe": "MaRES_1", "detector": {b: 1 for b in ne.DETECTOR_BANDS}}
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


if __name__ == "__main__":
    unittest.main()
