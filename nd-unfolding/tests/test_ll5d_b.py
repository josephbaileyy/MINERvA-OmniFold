"""LL5D amendment A1b (ll5d_b.py): the REQUIRED tests of LL5D-DECLARATION.md sections 10 and 12 that A1b carries, and
the director's conditions on A1b (2026-11-08): the sealed clip-prep consumer, the weakened label (strict < 0.9, an
allowlist of gate-record keys, descriptive only), the new module. Every rule is tested in the direction it acts and the
other.

    python3 -B nd-unfolding/tests/test_ll5d_b.py
"""
from __future__ import annotations

import argparse
import builtins
import functools
import hashlib
import io
import json
import os
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

import fd_1b_inv as inv  # noqa: E402
import fd_1b_mc as mc  # noqa: E402
import fd_1b_moded as moded  # noqa: E402
import fd_1b_null as fn  # noqa: E402
import fd_1b_score as fs  # noqa: E402
import fd_1b_toys as toys  # noqa: E402
import ll5d  # noqa: E402
import ll5d_b as b  # noqa: E402
import s1_assemble as sa  # noqa: E402
import s5p_universe  # noqa: E402
from test_ll5d import Fixture, digest  # noqa: E402


def fake_unfold(exp, threads, seed=42, *rest):
    """A deterministic stand-in for the estimator: the observed counts' histogram on the fine grid, times a seed
    factor, so the paths' plumbing is tested without OmniFold."""
    edges = exp.get("edges") or exp["inputs_edges"]
    h, _ = np.histogramdd(np.asarray(exp["obs"], float), bins=edges, weights=np.asarray(exp["obs_counts"], float))
    return h.ravel() * (1.0 + 1e-3 * (seed - 42)) + 1.0, {"fake": True}


def same(tc: unittest.TestCase, x, y, where: str) -> None:
    """Exact equality through dicts, lists and arrays (bitwise for float arrays)."""
    if isinstance(x, dict):
        tc.assertEqual(set(x), set(y), where)
        for k in x:
            same(tc, x[k], y[k], f"{where}.{k}")
    elif isinstance(x, (list, tuple)):
        tc.assertEqual(len(x), len(y), where)
        for i, (u, v) in enumerate(zip(x, y)):
            same(tc, u, v, f"{where}[{i}]")
    elif isinstance(x, np.ndarray) or isinstance(y, np.ndarray):
        np.testing.assert_array_equal(np.asarray(x), np.asarray(y), err_msg=where)
    else:
        tc.assertEqual(x, y, where)


class World(Fixture):
    def setUp(self):
        super().setUp()
        self.ps_b = [mock.patch.object(ll5d, "verified_weights", lambda world, a, tag: self.load(tag)),
                     mock.patch.object(mc, "truth_ratio", lambda t, p: (None, None)),
                     mock.patch.object(mc, "truth_weight", lambda t, inputs, ratio, push: self.r[t]),
                     mock.patch.object(mc, "via_noatime", self.via)]
        for p in self.ps_b:
            p.start()

    def tearDown(self):
        for p in reversed(self.ps_b):
            p.stop()
        super().tearDown()

    def via(self, reader, path):
        if reader is toys.flux_probabilities:
            return self.flux_p
        if reader is fs.load_s1:
            return self.s1_full()
        if reader is sa.flux_weights:
            return self.flux_p * 100.0
        raise AssertionError(f"unexpected read {path}")

    def s1_full(self):
        rng = np.random.default_rng(41)
        blocks = {f"lat:{bb}": np.outer(v, v) for bb, v in
                  ((bb, rng.normal(0, 0.01, sa.N_CELLS) * self.s1["f"]) for bb in sa.LATERAL_BANDS)}
        return dict(self.s1, blocks=blocks)

    def ns(self, **kw):
        base = dict(bank=self.w.bank, detector_dir=self.w.det, prep=self.tmp, flux_constraint=self.w.constraint,
                    threads=1, truth="g18", clip_prep=None, expect_clip_prep_sha256=None)
        base.update(kw)
        return argparse.Namespace(**base)

    def V(self):
        P = self.prepared()
        rel, geo, V, cv = ll5d.c2_inputs(P, self.s1, self.fm)
        return P, geo, V, cv


# ------------------------------------------------------------------------------------------------ the items


class Items(unittest.TestCase):
    def test_829_items_per_truth_and_13_in_the_pilot(self):
        it = b.items("g18")
        self.assertEqual(len(it), 829)
        self.assertEqual(sum(r == "block" for r, _ in it), 175)
        self.assertEqual(sum(r == "toy" for r, _ in it), 600)
        self.assertEqual(sum(r == "stat" for r, _ in it), 50)
        self.assertEqual([i for r, i in it if r == "clipmean"], ["minus2", "all"])
        self.assertEqual(len(b.PILOT), 13)
        self.assertIn(("g18", "toy", "minus2_4751000"), b.PILOT)
        self.assertIn(("ar23", "stat", "1"), b.PILOT)

    def test_toy_items_name_a_reading_and_a_declared_seed(self):
        self.assertEqual(b.parse_toy("all_4761299", "ar23"), ("all", 4761299))
        for bad in ("half_4751000", "minus2_4761000", "minus2_x", "minus2"):
            with self.assertRaises(b.Refusal):
                b.parse_toy(bad, "g18")


# ------------------------------------------------------------------------------------------------ the nature


class Nature(World):
    def test_compose_order_and_each_tree_clipped_on_its_own_composite(self):
        P, geo, V, cv = self.V()
        draw = self.draws("g18", 1)[0]
        for tags in (draw, ll5d.drop2(draw)):
            ui, ub, acc, rec = b.nature_inputs(self.world(), self.load, tags, self.r["g18"])
            cols = [P["col"][x] for x in tags]
            for q in ("wt", "wr", "bkgw", "tdw"):
                np.testing.assert_array_equal(acc[q], ll5d.compose_rows(V[q], np.asarray(cv[q], float), cols)[0], q)
            np.testing.assert_array_equal(ui["w_truth"], np.maximum(acc["wt"], 0.0))
            np.testing.assert_array_equal(ui["w_reco"], np.maximum(acc["wr"], 0.0))
            np.testing.assert_array_equal(ub["bkg_w"], np.maximum(acc["bkgw"], 0.0))
            np.testing.assert_array_equal(ui["denom_nd"], s5p_universe.denominator(
                self.bank_cv, np.maximum(acc["tdw"], 0.0), self.inputs["edges"]))
            np.testing.assert_array_equal(ui["flux"], self.flux[int(tags[0].rpartition("_")[2])])

    def test_k1_gives_universe_inputs_arrays_bitwise(self):
        """Section 10's k = 1 control: MaRES_0 and Flux_0, all four arrays (the denominator through section 3.4), and
        GEANT_Pion_0's wt, wr and bkgw, as universe_inputs gives them."""
        for tag in ("MaRES_0", "Flux_0", "GEANT_Pion_0"):
            ui, ub, acc, _ = b.nature_inputs(self.world(), self.load, [tag], self.r["g18"])
            single, _ = mc._single(self.inputs, self.bkg, self.bank_cv, tag, self.weights[tag], self.flux)
            for q in ("wt", "wr", "bkgw"):
                np.testing.assert_array_equal(acc[q], single[q], f"{tag} {q}")
            if "tdw" in self.weights[tag]:
                np.testing.assert_array_equal(ui["denom_nd"], single["denom"], tag)
            else:
                np.testing.assert_array_equal(acc["tdw"], self.tdw_ref)

    def test_the_experiment_at_r1_is_d_experiments(self):
        """Section 10: a k = 1 nature's experiment at r = 1 equals fd_1b_moded.d_experiment's bitwise (kappa's nature),
        with every Poisson draw at its mean."""
        ones = np.ones(self.inputs["w_truth"].shape[0])
        for tag in ("MaRES_0", "Flux_0"):
            ui, ub, _, _ = b.nature_inputs(self.world(), self.load, [tag], ones)
            u_i, u_b = mc.compose(self.inputs, self.bkg, self.bank_cv, [tag], lambda t: self.weights[t], self.flux)[:2]
            mine, _, _ = toys.build_full(ui, ub, ones, ones, np.ones(ub["bkg_w"].shape[0]), None, expectation=True)
            mine = inv.with_mc(mine, self.inputs, self.bkg)
            ref, _ = moded.d_experiment(self.inputs, self.bkg, u_i, u_b, ones)
            same(self, mine, ref, tag)

    def test_the_toys_truth_is_the_receipts_and_takes_phi_u(self):
        P, geo, V, cv = self.V()
        draw = self.draws("g18", 2)[1]
        inputs = self.inputs
        const_full = {"n_nucleons": float(inputs["n_nucleons"]), "data_pot": float(inputs["data_pot"]),
                      "edges": inputs["edges"]}
        for tags in (draw, ll5d.drop2(draw)):
            ui, ub, acc, _ = b.nature_inputs(self.world(), self.load, tags, self.r["g18"])
            exp, x_true = mc.toy_experiment(inputs, self.bkg, ui, ub, self.r["g18"], 4751001)
            nt = ll5d.nature_truth(acc, self.r["g18"], geo, ui["flux"], const_full)
            np.testing.assert_allclose(self.U @ np.ravel(x_true), self.U @ nt["x"], rtol=1e-12, atol=0)
            np.testing.assert_array_equal(exp["flux"], inputs["flux"])            # the unfolding MC divides by Phi_CV
            self.assertFalse(np.array_equal(ui["flux"], inputs["flux"]))          # the truth takes Phi_u


# ----------------------------------------------------------------------------------------------- the unfolds


class Unfold(World):
    def clip_prep_file(self, n=300, scale=1.0):
        rng = np.random.default_rng(5)
        nr, nb = self.inputs["w_truth"].shape[0], self.bkg["bkg_w"].shape[0]
        seal = {}
        for rd in ll5d.READINGS:
            seal[f"signal_negative_lambda_sum_{rd}"] = scale * np.where(rng.uniform(size=nr) < 0.1, rng.uniform(0, 3, nr), 0.0)
            seal[f"background_negative_lambda_sum_{rd}"] = scale * np.where(rng.uniform(size=nb) < 0.1, 1.0, 0.0)
            seal[f"U_T_clipped_{rd}"] = rng.normal(1.0, 0.01, (n, 16))
            seal[f"U_T_unclipped_{rd}"] = rng.normal(1.0, 0.01, (n, 16))
            seal[f"draws_{rd}"] = np.array(n)
        f = self.tmp / f"cp-{n}-{scale}.clipprep.npz"
        np.savez(f, **seal)
        return f, digest(f), seal

    def item_run(self, role, item, truth="g18", **kw):
        with mock.patch.object(mc, "_unfold_s1", fake_unfold), mock.patch.object(mc, "_unfold", fake_unfold), \
                mock.patch.object(mc, "_unfold_one64", fake_unfold), mock.patch.object(mc, "_unfold_one32", fake_unfold):
            return b.run_item(self.ns(truth=truth, **kw), self.world(), role, item)

    def test_each_role_writes_its_arrays(self):
        for role, item in (("central", "T"), ("seed", "T"), ("block", "MaRES_1"), ("block", "GEANT_Proton_0"),
                           ("block", "Flux_7"), ("stat", "3"), ("toy", "minus2_4751002"), ("toy", "all_4751002")):
            arrays, meta = self.item_run(role, item)
            self.assertTrue(np.all(np.isfinite(arrays["xsec_flat"])), (role, item))
            if role == "toy":
                self.assertEqual(meta["reading"], item.split("_")[0])
                self.assertEqual(set(meta["nature"]), {"n1_max", "clipped_fraction_signal", "clipped_fraction_background",
                                                       "fine_cells_dn0_where_ref_positive",
                                                       "fine_cells_ofin0_where_cv_positive"})
                self.assertIn("clip_reco_fine", arrays)
                removed = [t for t in meta["universes"] if t.rpartition("_")[0] in ll5d.REMOVED]
                self.assertEqual(bool(removed), item.startswith("all"))
            if role == "stat":
                self.assertEqual(meta["stat_seed"], ll5d.STAT_SEED["g18"])
        ar, mr = self.item_run("stat", "3", truth="ar23")
        self.assertEqual(mr["stat_seed"], 4_770_200)
        seen, real = [], mc.stat_experiment
        with mock.patch.object(mc, "stat_experiment", lambda i, k, r, seed, b_: seen.append(seed) or real(i, k, r, seed, b_)):
            self.item_run("stat", "4")
            self.item_run("stat", "4", truth="ar23")
        self.assertEqual(seen, [4_770_100, 4_770_200])           # the realization d~_T at section 3.6's seeds

    def test_the_seed_role_differs_from_central_only_by_the_estimator_seed(self):
        a1, _ = self.item_run("central", "T")
        a2, _ = self.item_run("seed", "T")
        np.testing.assert_array_equal(a1["xtrue_flat"], a2["xtrue_flat"])
        self.assertFalse(np.array_equal(a1["xsec_flat"], a2["xsec_flat"]))     # the fake estimator sees the seed

    def test_refusals(self):
        for role, item, why in (("block", "Rvp1pi_0", "175"), ("toy", "minus2_4761000", "declared"),
                                ("stat", "51", "set A"), ("central", "X", "item T"), ("clipmean", "half", "reading")):
            with self.assertRaisesRegex(b.Refusal, why):
                self.item_run(role, item)
        with self.assertRaisesRegex(b.Refusal, "control"):
            self.item_run("control", "MaRES_9", truth="data")

    def test_r_t_must_be_positive_everywhere(self):
        bad = self.r["g18"].copy()
        bad[3] = 0.0
        with mock.patch.object(mc, "truth_weight", lambda t, inputs, ratio, push: bad), \
                self.assertRaisesRegex(b.Refusal, "r_T > 0"):
            self.item_run("central", "T")

    def test_the_clipmean_adds_the_mean_clipped_mass_and_reads_only_the_sealed_digest(self):
        f, sha, seal = self.clip_prep_file()
        a_cm, m = self.item_run("clipmean", "minus2", clip_prep=f, expect_clip_prep_sha256=sha)
        self.assertEqual(m["clip_prep_sha256"], sha)
        exp0, _ = mc.mean_experiment(self.inputs, self.bkg, self.r["g18"])
        exp1, _ = b.clipmean_experiment(self.inputs, self.bkg, self.r["g18"], seal, "minus2")
        added = float(np.sum(exp1["obs_counts"])) - float(np.sum(exp0["obs_counts"]))
        reco = np.asarray(self.inputs["pass_reco"], bool)
        import s5n_pseudo
        sig = seal["signal_negative_lambda_sum_minus2"] / 300
        bm = seal["background_negative_lambda_sum_minus2"] / 300
        keep_s = s5n_pseudo.fid_mask(np.asarray(self.inputs["MCreco"])[reco & (sig > 0)], self.inputs["edges"])
        keep_b = s5n_pseudo.fid_mask(np.asarray(self.bkg["bkg_reco"])[bm > 0], self.inputs["edges"])
        self.assertAlmostEqual(added, float(sig[reco & (sig > 0)][keep_s].sum() + bm[bm > 0][keep_b].sum()), places=9)
        with self.assertRaisesRegex(b.Refusal, "not the sealed file"):
            self.item_run("clipmean", "all", clip_prep=f, expect_clip_prep_sha256="0" * 64)
        g, gsha, _ = self.clip_prep_file(n=299)
        with self.assertRaisesRegex(b.Refusal, "not 300"):
            self.item_run("clipmean", "all", clip_prep=g, expect_clip_prep_sha256=gsha)


# ------------------------------------------------------------------------------------------ walls, clipcheck


class Walls(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp(prefix="ll5d-b-walls-"))
        self.addCleanup(shutil.rmtree, self.d)

    def write(self, seconds=500.0, rss=1000, skip=None):
        for truth, role, item in b.PILOT:
            if (truth, role, item) == skip:
                continue
            np.savez(self.d / b.product_name(truth, role, item), xsec_flat=np.ones(3),
                     meta=json.dumps({"seconds_unfold": seconds, "peak_rss_kib": rss}))

    def test_the_unit_and_the_limit_both_ways(self):
        self.write()
        self.assertEqual(b.walls(self.d)["verdict"], "PASS")
        self.write(seconds=b.UNIT_SECONDS)
        self.assertEqual(b.walls(self.d)["verdict"], "PASS")
        self.write(seconds=b.UNIT_SECONDS + 0.001)
        self.assertEqual(b.walls(self.d)["verdict"], "REPRICE")
        self.write(rss=b.RSS_LIMIT_KIB + 1)
        self.assertEqual(b.walls(self.d)["verdict"], "REPRICE")

    def test_a_missing_product_is_a_reprice(self):
        for p in self.d.glob("*.npz"):
            p.unlink()
        self.write(skip=b.PILOT[5])
        r = b.walls(self.d)
        self.assertEqual(r["verdict"], "REPRICE")
        self.assertIn("missing", r["why"])


class ClipOffset(unittest.TestCase):
    def test_the_offset_is_the_unfolds_shift_less_the_truths(self):
        rng = np.random.default_rng(1)
        U = np.eye(16)
        sigma = np.full(16, 2.0)
        tc, tu = rng.normal(1, 0.1, (300, 16)), rng.normal(1, 0.1, (300, 16))
        cp = {"U_T_clipped_minus2": tc, "U_T_unclipped_minus2": tu}
        xc, xT = rng.normal(5, 1, 16), rng.normal(5, 1, 16)
        r = b.clip_offset(U, xc, xT, sigma, cp, "minus2")
        tau = (tc - tu).mean(axis=0) / sigma
        np.testing.assert_allclose(r["o_c"], (xc - xT) / sigma - tau, rtol=1e-13)
        np.testing.assert_allclose(r["tau_c"], tau, rtol=1e-13)

    def test_delta_star_is_at_or_above(self):
        U, sigma = np.eye(16), np.ones(16)
        z = np.zeros((300, 16))
        cp = {"U_T_clipped_all": z, "U_T_unclipped_all": z}
        for d, hit in ((0.667, ["R03"]), (np.nextafter(0.667, 0), []), (-0.667, ["R03"])):
            xc = np.zeros(16)
            xc[3] = d
            self.assertEqual(b.clip_offset(U, xc, np.zeros(16), sigma, cp, "all")["cells_at_or_above_delta_star"], hit)
        self.assertEqual(b.CLIP_DELTA_STAR, 0.667)
        with self.assertRaises(b.Refusal):
            b.clip_offset(U, np.zeros(16), np.zeros(16), sigma, {"U_T_clipped_all": z[:10], "U_T_unclipped_all": z[:10]},
                          "all")


# ------------------------------------------------------------------------------- the blocks, null and readout


def synthetic_products(t: Fixture, d: Path, truth: str = "g18", seed: int = 0, toy_bias: float = 0.0) -> None:
    """Products a real run would write, made synthetically on the toy world's fine grid: d_T's central and seed
    values, every block, the stat replicas and every toy in both readings, with a draw record and a nature record."""
    rng = np.random.default_rng(seed)
    nf = t.U.shape[1]
    base = rng.uniform(1.0, 2.0, nf)
    meta = {"seconds_unfold": 1.0, "peak_rss_kib": 1}
    w = lambda name, x, **extra: np.savez(d / name, xsec_flat=x, meta=json.dumps(dict(meta, **extra)),  # noqa: E731
                                          **({"xtrue_flat": extra.pop("xtrue")} if "xtrue" in extra else {}))
    np.savez(d / b.product_name(truth, "central", "T"), xsec_flat=base, xtrue_flat=base * 1.001, meta=json.dumps(meta))
    np.savez(d / b.product_name(truth, "seed", "T"), xsec_flat=base, xtrue_flat=base * 1.001, meta=json.dumps(meta))
    for u in ll5d.layout("all")[2]:
        w(b.product_name(truth, "block", u), base * (1 + 0.02 * rng.normal(size=nf)))
    for s in mc.STAT_REPLICAS:
        w(b.product_name(truth, "stat", str(s)), base * (1 + 0.03 * rng.normal(size=nf)))
    nat = {"clipped_fraction_signal": 0.0, "clipped_fraction_background": 0.0, "fine_cells_dn0_where_ref_positive": 0,
           "fine_cells_ofin0_where_cv_positive": 0, "n1_max": {}}
    for rd in ll5d.READINGS:
        for s in ll5d.TOY_SEEDS[truth]:
            dr = toys.draw_for_seed(int(s), t.flux_p, t.groups)
            np.savez(d / b.product_name(truth, "toy", f"{rd}_{s}"),
                     xsec_flat=base * (1 + toy_bias + 0.05 * rng.normal(size=nf)), xtrue_flat=base,
                     meta=json.dumps(dict(meta, draw=dr, nature=nat)))


class Pipeline(World):
    """null_step then readout over synthetic products (the estimator is out of scope here: the products stand in)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.unf = cls.tmp / "unfolds"
        cls.unf.mkdir()
        synthetic_products(cls, cls.unf)
        cls.cmodel = (np.eye(16) * 1e-4, np.eye(16) * 0.5e-4)

    def args(self, **kw):
        base = dict(staged=self.tmp, definition=self.tmp / "definition.json", unfolds=self.unf,
                    cmodel_json=self.tmp / "cmodel.json", flux_constraint=self.w.constraint, truth="g18")
        base.update(kw)
        return argparse.Namespace(**base)

    def common(self):
        small = functools.partial(fn.null_contents, n_mc=20_000)
        return [mock.patch.object(sa, "fine_map", lambda p: self.fm), mock.patch.object(sa, "functional_matrix",
                                                                                       lambda f: self.U),
                mock.patch.object(mc, "cmodel_parts", lambda s1, j: self.cmodel), mock.patch.object(fn, "null_contents", small),
                mock.patch.object(mc, "made_from", lambda a, U: {"definition_sha256": "d"}),
                mock.patch.object(fs, "reported_matrix", lambda s1: np.diag((0.05 * s1["f"]) ** 2))]

    def with_patches(self, fnc, *a, **k):
        ps = self.common()
        for p in ps:
            p.start()
        try:
            return fnc(*a, **k)
        finally:
            for p in reversed(ps):
                p.stop()

    def test_minus2_rebuilds_without_the_two_bands_and_the_removal_is_exact(self):
        s1, U, frac, minus, w = self.with_patches(b.setup, self.args())
        rms = {rd: self.with_patches(b.remade, self.unf, "g18", s1, U, w, frac, rd) for rd in ll5d.READINGS}
        self.assertNotIn("band:GEANT_Neutron", rms["minus2"]["blocks"])
        self.assertNotIn("band:GEANT_Proton", rms["minus2"]["blocks"])
        self.assertIn("band:GEANT_Pion", rms["minus2"]["blocks"])
        names = [n for n, _, _ in rms["minus2"]["laws"]]
        self.assertFalse({"band:GEANT_Neutron", "band:GEANT_Proton"} & set(names))
        self.assertEqual(len(rms["all"]["laws"]) - len(rms["minus2"]["laws"]), 2)
        ctl = b.removal_control(rms["all"], rms["minus2"])
        self.assertTrue(ctl["passes"])
        big = float(np.max(np.abs(rms["all"]["C_T"])))
        self.assertAlmostEqual(ctl["limit"], 1e-12 * big)
        bad = dict(rms["minus2"], C_T=rms["minus2"]["C_T"] + 2e-12 * big * np.eye(16))
        self.assertFalse(b.removal_control(rms["all"], bad)["passes"])
        near = dict(rms["minus2"], C_T=rms["minus2"]["C_T"] + 0.5e-12 * big * np.eye(16))
        self.assertTrue(b.removal_control(rms["all"], near)["passes"])
        np.testing.assert_allclose(fn.check_matched([law for _, law, _ in rms["minus2"]["laws"]], rms["minus2"]["gauss"],
                                                    rms["minus2"]["C_T"]), 0.0, atol=1e-12)

    def null(self):
        nf = self.tmp / "null.json"
        if not nf.exists():
            rec = self.with_patches(b.null_step, self.args())
            nf.write_text(json.dumps(rec, sort_keys=True))
        return nf

    def test_the_null_is_per_reading_at_the_declared_seeds(self):
        rec = json.loads(self.null().read_text())
        self.assertEqual(rec["verdict"], "PASS")
        self.assertTrue(rec["removal_control"]["passes"])
        for rd in ll5d.READINGS:
            e = f"g18/{rd}"
            self.assertEqual(rec[e]["C_T"]["seed"], ll5d.NULL_SEED[e])
            self.assertLessEqual(rec[e]["C_T"]["match_rel"], 1e-12)
            self.assertIn("C_T_minus_mec", rec[e])

    def gate_file(self, ratios: dict | None = None, extra: dict | None = None):
        rng = np.random.default_rng(3)
        ratios = ratios or {rd: rng.uniform(0.95, 1.05, 16) for rd in ll5d.READINGS}
        g = {"schema": ll5d.SCHEMA_GATE, "step": "ll5d-gate", "truth": "g18", "verdict": "PASS",
             "record": {"b": {f"g18/{rd}": {"variance_ratio": {"option_1_clipped": list(map(float, ratios[rd]))}}
                              for rd in ll5d.READINGS}}, **(extra or {})}
        f = self.tmp / f"gate-{hashlib.sha256(json.dumps(g).encode()).hexdigest()[:8]}.json"
        f.write_text(json.dumps(g))
        return f, digest(f)

    def clipcheck_file(self):
        z = np.zeros(16)
        cc = {"evaluations": {f"g18/{rd}": {"o_c": z.tolist(), "tau_c": z.tolist(), "unfold_shift": z.tolist(),
                                            "truth_shift": z.tolist()} for rd in ll5d.READINGS}, "verdict": "PROCEED"}
        f = self.tmp / "clipcheck.json"
        f.write_text(json.dumps(cc))
        return f, digest(f)

    def readout(self, gate=None):
        nf = self.null()
        cf, csha = self.clipcheck_file()
        gf, gsha = gate or self.gate_file()
        a = self.args(null=nf, expect_null_sha256=digest(nf), clipcheck=cf, expect_clipcheck_sha256=csha, gate=gf,
                      expect_gate_sha256=gsha)
        return self.with_patches(b.readout, a)

    def test_the_readout_grades_both_readings_and_compares_them(self):
        r = self.readout()
        self.assertEqual(set(r["evaluations"]), {"g18/minus2", "g18/all"})
        for e, v in r["evaluations"].items():
            self.assertIn(v["verdict"], ("COVERS", "UNDER-COVERS"), e)
            self.assertTrue(v["reading_rule"]["C_T"]["passes"])
            self.assertEqual(v["cholesky_check"]["compared"]["ndf"], 16)
            self.assertIn("weakened", v)
            self.assertIn("realization_check", v["readouts"])
        self.assertIn("between_readings", r)
        self.assertEqual(r["between_readings"]["note"], "descriptive; neither reading tests the other")

    def test_each_reading_takes_its_own_ratio_for_the_weakened_label(self):
        ratios = {"minus2": np.full(16, 0.5), "all": np.full(16, 1.0)}
        r = self.readout(gate=self.gate_file(ratios))
        g_m2, g_all = r["evaluations"]["g18/minus2"], r["evaluations"]["g18/all"]
        passes_m2 = [f"R{c:02d}" for c, fl in enumerate(g_m2["grade"]["cell_flag"]) if not fl]
        self.assertEqual(g_m2["weakened"]["weakened_cells"], passes_m2)
        self.assertEqual(g_all["weakened"]["weakened_cells"], [])

    def test_the_weakened_label_moves_no_verdict(self):
        r1 = self.readout(gate=self.gate_file({"minus2": np.full(16, 0.5), "all": np.full(16, 0.5)}))
        with mock.patch.object(b, "weakened", lambda flags, ratio: {}):
            r2 = self.readout(gate=self.gate_file({"minus2": np.full(16, 0.5), "all": np.full(16, 0.5)}))
        for e in r1["evaluations"]:
            for k in ("verdict", "grade"):
                self.assertEqual(json.dumps(r1["evaluations"][e][k], sort_keys=True),
                                 json.dumps(r2["evaluations"][e][k], sort_keys=True), (e, k))

    def test_the_gate_record_is_read_only_through_its_allowlist(self):
        gf, gsha = self.gate_file(extra={"receipt": {"secret": 1}, "clip_prep": {"sha256": "x"}, "reads": {}})
        seen = []

        class Rec(dict):
            def __getitem__(self, k):
                seen.append(k)
                v = dict.__getitem__(self, k)
                return Rec(v) if isinstance(v, dict) else v

            def get(self, k, d=None):
                seen.append(k)
                return dict.get(self, k, d)

            def __contains__(self, k):
                seen.append(k)
                return dict.__contains__(self, k)
        real = json.loads
        with mock.patch.object(b.json, "loads", lambda s, **k: Rec(real(s, **k))):
            out = b.gate_ratios(gf, gsha, "g18")
        self.assertEqual(set(out), {"g18/minus2", "g18/all"})
        allowed = set(b.GATE_KEYS) | {"b", "g18/minus2", "g18/all", "variance_ratio", "option_1_clipped"}
        self.assertTrue(set(seen) <= allowed, set(seen) - allowed)
        with self.assertRaisesRegex(b.Refusal, "digest"):
            b.gate_ratios(gf, "0" * 64, "g18")


class Weakened(unittest.TestCase):
    def test_strictly_below_0_9(self):
        flags = [False] * 16
        r = np.full(16, 1.0)
        r[0], r[1], r[2], r[3] = 0.9, np.nextafter(0.9, 0), 0.86, 0.94
        self.assertEqual(b.weakened(flags, r)["weakened_cells"], ["R01", "R02"])
        flags[1] = True                               # a flagged cell is not a pass: never weakened
        self.assertEqual(b.weakened(flags, r)["weakened_cells"], ["R02"])
        self.assertEqual(b.WEAK_RATIO, 0.9)


class CholeskyRule(unittest.TestCase):
    def ok(self, **kw):
        c = {"kappa2": 1e6, "tol": 1e-9, "compared": {"ndf": 16, "max_rel_diff": 1e-12, "tol": 1e-9}}
        for k, v in kw.items():
            if k.startswith("c_"):
                c["compared"][k[2:]] = v
            else:
                c[k] = v
        return c

    def test_the_rule_both_ways(self):
        self.assertTrue(b.reading_rule(self.ok())["passes"])
        self.assertTrue(b.reading_rule(self.ok(c_ndf=15, c_max_rel_diff=float("nan")))["passes"])
        for bad in (dict(c_max_rel_diff=float("nan")), dict(kappa2=float("inf")), dict(c_max_rel_diff=2e-9),
                    dict(c_tol=2e-9), dict(c_max_rel_diff=None), dict(tol=float("nan"))):
            self.assertFalse(b.reading_rule(self.ok(**bad))["passes"], bad)
        self.assertFalse(b.reading_rule({"kappa2": 1.0, "tol": 1e-9, "compared": {}})["passes"])

    def test_the_tolerance_is_a5s(self):
        sys.path.insert(0, str(ND.parent / "2d-unfolding" / "cov2d"))
        try:
            import cov2d_readout
        except Exception as exc:                      # its heavy imports may be absent on a test host
            self.skipTest(f"cov2d_readout not importable here: {exc}")
        rng = np.random.default_rng(2)
        Q, _ = np.linalg.qr(rng.normal(size=(16, 16)))
        C = Q @ np.diag(np.logspace(0, -10, 16)) @ Q.T           # kappa_2 near 1e10: 10 kappa eps decides the tol
        self.assertGreater(b.cholesky_tol(C)["tol"], 1e-6)
        self.assertEqual(b.cholesky_tol(C)["tol"], cov2d_readout.cholesky_tol(C)["tol"])
        self.assertEqual(b.cholesky_tol(C)["kappa2"], cov2d_readout.cholesky_tol(C)["kappa2"])


class NoAtime(World):
    FLAG = 1 << 29

    def test_the_clip_prep_the_gate_and_the_products_are_read_with_o_noatime_only(self):
        f, sha, _ = Unfold.clip_prep_file(self)
        g = self.tmp / "na-gate.json"
        g.write_text(json.dumps({"truth": "g18", "verdict": "PASS", "record": {"b": {
            f"g18/{rd}": {"variance_ratio": {"option_1_clipped": [1.0] * 16}} for rd in ll5d.READINGS}}}))
        gsha = digest(g)
        d = self.tmp / "na-unf"
        d.mkdir(exist_ok=True)
        np.savez(d / b.product_name("g18", "central", "T"), xsec_flat=np.ones(3))
        flagged, plain_opens = [], []
        real_os_open = os.open

        def os_open(path, flags, *a, **k):
            if flags & self.FLAG:
                flagged.append(os.fspath(path))
            return real_os_open(path, flags & ~self.FLAG, *a, **k)

        def recording(real):
            def opener(file, *a, **k):
                if isinstance(file, (str, os.PathLike)):
                    plain_opens.append(os.fspath(file))
                return real(file, *a, **k)
            return opener
        with mock.patch.object(inv, "NOATIME_FLAG", self.FLAG), mock.patch.object(inv.os, "open", os_open), \
                mock.patch.object(builtins, "open", recording(builtins.open)), mock.patch.object(io, "open", recording(io.open)):
            b.read_clip_prep(f, sha)
            b.gate_ratios(g, gsha, "g18")
            b._x(d, "g18", "central", "T")
        for p in (str(f), str(g), str(d / b.product_name("g18", "central", "T"))):
            self.assertIn(p, flagged)
            self.assertNotIn(p, plain_opens)


class ExitCodes(unittest.TestCase):
    def test_a_refusal_is_invalid_with_its_record(self):
        d = Path(tempfile.mkdtemp(prefix="ll5d-b-rc-"))
        self.addCleanup(shutil.rmtree, d)
        argv = ["null", "--staged", str(d), "--definition", str(d), "--unfolds", str(d), "--cmodel-json", str(d),
                "--flux-constraint", str(d), "--out", str(d / "null.json"), "--truth", "g18"]

        def boom(a):
            raise b.Refusal("the seed check failed: estimator seed 45 differs from 42 at T")
        with mock.patch.object(b, "null_step", boom), mock.patch.object(inv, "atime_check", lambda: {"moved": []}):
            self.assertEqual(b.main(argv), 5)
        rec = json.loads((d / "null.invalid.json").read_text())
        self.assertEqual(rec["verdict"], "INVALID")
        self.assertIn("seed check", rec["why"])
        self.assertFalse((d / "null.json").exists())


class Module(unittest.TestCase):
    def test_a1a_is_imported_unchanged_and_named_in_the_digests(self):
        d = b.code_digests()
        self.assertEqual(d["ll5d:ll5d.py"], hashlib.sha256(Path(ll5d.__file__).read_bytes()).hexdigest())
        self.assertIn("ll5d_b.py", d)
        self.assertNotIn("def receipt(", Path(b.__file__).read_text())

    def test_no_seed_or_constant_is_redeclared(self):
        self.assertIs(b.READINGS, ll5d.READINGS)
        self.assertIs(b.EVALUATIONS, ll5d.EVALUATIONS)
        self.assertEqual(b.N_DECLARED, 300)


if __name__ == "__main__":
    unittest.main()
