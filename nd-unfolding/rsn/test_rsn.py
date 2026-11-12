#!/usr/bin/env python3
"""Tests of RSN's code (RSN-DECLARATION.md §8). Numpy only: the estimators are stubs, the products and records are
synthetic, and the committed records the code pins (the H2 definition, the Stage-1 receipt, i0.json, cmodel_5d.json,
the F1 prep manifest, pv-ladder's prep sums and tasks) are read from the checkout.

    python3 -B -m unittest nd-unfolding/rsn/test_rsn.py
"""
from __future__ import annotations

import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ND = HERE.parent
REPO = ND.parent
for _p in (str(HERE), str(ND / "pv-ladder"), str(ND), str(REPO / "2d-unfolding" / "pv2d"),
           str(REPO / "2d-unfolding" / "pv2d" / "cmodel")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import build_cmodel5d as B5  # noqa: E402
import fd_f0_regrade as R  # noqa: E402
import omnifold_nn_core as onc  # noqa: E402
import pvl_lib as L  # noqa: E402
import pvl_unfold as PU  # noqa: E402
import rsn_cmodel as CM  # noqa: E402
import rsn_prep as PR  # noqa: E402
import rsn_read as RD  # noqa: E402
import rsn_regrade as RG  # noqa: E402
import rsn_unfold as UF  # noqa: E402
import s2_h2_scope as S2  # noqa: E402
import s5n_pseudo  # noqa: E402

NFINE = int(np.prod(PR.SHAPE))
PZ_HI = np.asarray(L.FINE["pz"][1:])[np.unravel_index(np.arange(NFINE), PR.SHAPE)[1]]


def quiet(fn, *a, **k):
    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
        return fn(*a, **k)


def reporting_map():
    D = L.load_json(ND / "pv-ladder/readouts/h2_definition.json")
    cell, _ = S2.h2_of_fine()
    return np.asarray(D["h2_to_reporting_cell"])[cell], int(D["n_reporting_cells"])


# ---------------------------------------------------------------- prep


class FrozenFixture:
    """A frozen prep/ratios/L-5D-PV directory and the committed records it must reproduce, on the real fine grid."""

    def __init__(self, d: Path, seed=7):
        rng = np.random.default_rng(seed)
        self.d, self.ratios = d, d / "ratios"
        self.ratios.mkdir()
        p = rng.uniform(0.5, 2.0, NFINE)
        p[rng.random(NFINE) < 0.03] = 0.0
        self.p = p
        verts, sums = {}, {}
        for v in PR.VERTICES:
            label = rng.choice(np.array(["fine", "coarse", "noisy", "off"], dtype=object), NFINE, p=[0.3, 0.5, 0.1, 0.1])
            label[p == 0] = "noisy"
            if v == "gibuu":
                label[PZ_HI > 10.0] = "off"
            rho = np.where(np.isin(label, ("fine", "coarse")), rng.uniform(0.7, 1.3, NFINE), 1.0)
            r, k = L.normalize(rho, np.isin(label, ("fine", "coarse")), p)
            (self.ratios / f"{v}.json").write_text(json.dumps({"schema": L.RATIO_SCHEMA, "r": r.tolist()}))
            verts[v] = {"ratio_file": f"{v}.json", "rho": rho.tolist(), "label": label.tolist(), "k": k}
        (self.ratios / "ratios.json").write_text(json.dumps({"prior_truth_weight": p.tolist(), "vertices": verts}))
        for f in ["ratios.json"] + [f"{v}.json" for v in PR.VERTICES]:
            sums[f] = L.sha256_path(self.ratios / f)
        self.sums = d / "prep-SHA256SUMS"
        self.sums.write_text("".join(f"{s}  ./ratios/L-5D-PV/{f}\n" for f, s in sums.items()))
        rmap, n = reporting_map()
        near = np.zeros(NFINE, bool)
        for v in PR.VERTICES:
            r = np.asarray(json.loads((self.ratios / f"{v}.json").read_text())["r"])
            near |= np.isin(L.classify_cells(r, np.asarray(verts[v]["label"], dtype=object), PR.SHAPE), ("gate", "cut"))
        self.describe = d / "describe.json"
        self.describe.write_text(json.dumps({"step_adjacent_share_union": PR.shares(near, p, rmap, n).tolist()}))
        g = verts["gibuu"]
        r6, k6, _ = PR.g6(np.asarray(g["rho"]), np.asarray(g["label"], dtype=object), p, PZ_HI)
        self.domain = d / "domain.json"
        self.domain.write_text(json.dumps({"k": {"ii": k6}, "departure": {"ii": PR.departures(r6, p, rmap, n).tolist()}}))

    def argv(self, out):
        return ["--ratios", str(self.ratios), "--prep-sums", str(self.sums), "--describe", str(self.describe),
                "--domain", str(self.domain), "--out", str(out)]


class PrepUnits(unittest.TestCase):
    def test_box_sum_matches_a_brute_force_box(self):
        rng = np.random.default_rng(1)
        a = rng.random(NFINE)
        A = a.reshape(PR.SHAPE)
        for rad in (1, 2):
            got = PR.box_sum(a, rad).reshape(PR.SHAPE)
            for _ in range(40):
                c = tuple(int(rng.integers(0, s)) for s in PR.SHAPE)
                sl = tuple(slice(max(i - rad, 0), min(i + rad + 1, s)) for i, s in zip(c, PR.SHAPE))
                self.assertAlmostEqual(got[c], A[sl].sum(), places=10)

    def test_smoothing_is_the_weighted_box_mean_renormalized(self):
        rng = np.random.default_rng(2)
        r = rng.uniform(0.8, 1.2, NFINE)
        lab = np.full(NFINE, "fine", dtype=object)
        lab[rng.random(NFINE) < 0.2] = "off"
        p = rng.uniform(0.5, 2.0, NFINE)
        p[rng.random(NFINE) < 0.05] = 0.0
        rs, k = PR.smooth(r, lab, p, 1)
        region = lab != "off"
        assigned = region & (p > 0)
        self.assertTrue(np.all(rs[~assigned] == 1.0))
        self.assertTrue(np.all(rs > 0))
        self.assertAlmostEqual(float((p * rs)[assigned].sum()), float(p[assigned].sum()), places=6)
        R5, P5, G5 = r.reshape(PR.SHAPE), np.where(region, p, 0).reshape(PR.SHAPE), assigned.reshape(PR.SHAPE)
        for idx in np.flatnonzero(assigned)[:: max(1, assigned.sum() // 30)][:30]:
            c = np.unravel_index(idx, PR.SHAPE)
            sl = tuple(slice(max(i - 1, 0), i + 2) for i in c)
            want = (P5[sl] * R5[sl]).sum() / P5[sl].sum()
            self.assertAlmostEqual(rs[idx] / k, want, places=10)
            self.assertTrue(G5[c])

    def test_smoothing_a_constant_reweight_gives_one(self):
        lab = np.full(NFINE, "coarse", dtype=object)
        rs, _ = PR.smooth(np.full(NFINE, 1.3), lab, np.ones(NFINE), 2)
        self.assertTrue(np.allclose(rs, 1.0, rtol=0, atol=1e-12))

    def test_g6_is_off_above_6_and_the_frozen_rho_rescaled_below(self):
        rng = np.random.default_rng(3)
        rho = rng.uniform(0.7, 1.3, NFINE)
        lab = np.full(NFINE, "fine", dtype=object)
        lab[PZ_HI > 10] = "off"
        p = rng.uniform(0.5, 2, NFINE)
        r6, k6, lab6 = PR.g6(rho, lab, p, PZ_HI)
        hi = PZ_HI > 6.0
        self.assertTrue(np.all(r6[hi] == 1.0) and np.all(lab6[hi] == "off"))
        lo = ~hi
        self.assertTrue(np.allclose(r6[lo], rho[lo] * k6, rtol=1e-14, atol=0))
        self.assertAlmostEqual(float((p * r6)[lo].sum()), float(p[lo].sum()), places=6)
        self.assertTrue(np.any(PZ_HI == 6.0) and np.all(lab6[PZ_HI == 6.0] == "fine"))

    def test_a_step_marks_both_neighbours_and_a_small_one_marks_none(self):
        r = np.ones(NFINE)
        i = np.ravel_multi_index((3, 4, 2, 2, 2), PR.SHAPE)
        r[i] = 1.0 + 0.0999
        self.assertFalse(PR.near_step(r).any())
        r[i] = 1.0 + L.STEP + 1e-9
        near = PR.near_step(r)
        self.assertEqual(int(near.sum()), 1 + 2 * 5)
        self.assertTrue(near[i] and near[np.ravel_multi_index((3, 5, 2, 2, 2), PR.SHAPE)])

    def test_the_manipulation_check_boundaries(self):
        f = np.full(16, 0.9)
        self.assertTrue(PR.manipulation_check(f, np.full(16, 0.45))["pass"])
        self.assertFalse(PR.manipulation_check(f, np.full(16, 0.45 + 1e-9))["pass"])
        s = np.full(16, 0.1)
        s[:4] = 0.95
        self.assertTrue(PR.manipulation_check(f, s)["pass"])
        s[:5] = 0.95
        self.assertFalse(PR.manipulation_check(f, s)["pass"])


class PrepRun(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.fx = FrozenFixture(Path(cls.tmp.name))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def setUp(self):
        self.out = Path(tempfile.mkdtemp(dir=self.tmp.name)) / "prep"
        self.saved = PR.manipulation_check

    def tearDown(self):
        PR.manipulation_check = self.saved

    def test_the_prep_writes_g6_and_reproduces_its_controls(self):
        quiet(PR.main, self.fx.argv(self.out))
        rec = json.loads((self.out / "prep.json").read_text())
        self.assertEqual(set(rec["controls"]), {"frozen_reweights_reproduced", "gate_or_cut_share_reproduced",
                                                "g6_reproduces_option_ii"})
        g = json.loads((self.out / "G6" / "gibuu.json").read_text())
        self.assertEqual(g["schema"], L.RATIO_SCHEMA)
        self.assertEqual(rec["files"]["G6/gibuu.json"], L.sha256_path(self.out / "G6" / "gibuu.json"))
        self.assertTrue(np.all(np.asarray(g["r"])[PZ_HI > 6] == 1.0))

    def test_the_radius_ladder(self):
        def fake(passes):
            return lambda frozen, smoothed: {"pass": passes.pop(0)}

        for passes, radius, n_sm, status in (([True], 1, 3, "built"), ([False, True], 2, 3, "built"),
                                             ([False, False], None, 0, "not built")):
            out = Path(tempfile.mkdtemp(dir=self.tmp.name)) / "prep"
            PR.manipulation_check = fake(list(passes))
            quiet(PR.main, self.fx.argv(out))
            rec = json.loads((out / "prep.json").read_text())
            self.assertEqual(rec["sm"]["radius"], radius)
            self.assertEqual(len([f for f in rec["files"] if f.startswith("SM/")]), n_sm)
            self.assertEqual(sorted((out / "SM").glob("*.json")) != [], n_sm > 0)
            self.assertEqual(len(rec["sm"]["checks"]), len(passes))
            self.assertTrue(rec["sm"]["status"].startswith(status))

    def test_the_smoothed_reweights_are_written_at_the_passing_radius(self):
        PR.manipulation_check = lambda f, s: {"pass": True}
        quiet(PR.main, self.fx.argv(self.out))
        rec = json.loads((self.out / "prep.json").read_text())
        frozen = json.loads((self.fx.ratios / "ratios.json").read_text())
        for v in PR.VERTICES:
            sm = json.loads((self.out / "SM" / f"{v}.json").read_text())
            r0 = json.loads((self.fx.ratios / f"{v}.json").read_text())["r"]
            want, _ = PR.smooth(np.asarray(r0), np.asarray(frozen["vertices"][v]["label"], dtype=object), self.fx.p, 1)
            self.assertTrue(np.array_equal(np.asarray(sm["r"]), want))
            self.assertEqual(sm["radius"], 1)
        self.assertEqual(rec["sm"]["radius"], 1)

    def test_the_prep_refuses_on_each_control(self):
        def refuses(argv_edit, msg):
            out = Path(tempfile.mkdtemp(dir=self.tmp.name)) / "prep"
            with self.assertRaises(SystemExit) as cm:
                quiet(PR.main, argv_edit(self.fx.argv(out)))
            self.assertIn(msg, str(cm.exception))
            self.assertFalse(out.exists())

        d = Path(tempfile.mkdtemp(dir=self.tmp.name))
        bad_describe = d / "describe.json"
        v = json.loads(self.fx.describe.read_text())
        v["step_adjacent_share_union"][3] += 1e-9
        bad_describe.write_text(json.dumps(v))
        refuses(lambda a: [str(bad_describe) if x == str(self.fx.describe) else x for x in a], "h2_definition_describe")
        bad_domain = d / "domain.json"
        v = json.loads(self.fx.domain.read_text())
        v["k"]["ii"] *= 1 + 1e-9
        bad_domain.write_text(json.dumps(v))
        refuses(lambda a: [str(bad_domain) if x == str(self.fx.domain) else x for x in a], "option ii")
        v = json.loads(self.fx.domain.read_text())
        v["departure"]["ii"][5] += 1e-9
        bad_domain.write_text(json.dumps(v))
        refuses(lambda a: [str(bad_domain) if x == str(self.fx.domain) else x for x in a], "option ii")
        bad_sums = d / "sums"
        bad_sums.write_text(self.fx.sums.read_text().replace(L.sha256_path(self.fx.ratios / "nuwro.json"), "0" * 64))
        refuses(lambda a: [str(bad_sums) if x == str(self.fx.sums) else x for x in a], "sha256")
        exists = Path(tempfile.mkdtemp(dir=self.tmp.name))
        with self.assertRaises(SystemExit) as cm:
            quiet(PR.main, self.fx.argv(exists))
        self.assertIn("refusing to write", str(cm.exception))

    def test_a_frozen_reweight_that_normalize_does_not_reproduce_refuses(self):
        R5 = json.loads((self.fx.ratios / "ratios.json").read_text())
        frozen = {v: {"rho": np.asarray(R5["vertices"][v]["rho"]), "label": np.asarray(R5["vertices"][v]["label"], dtype=object),
                      "r": np.asarray(json.loads((self.fx.ratios / f"{v}.json").read_text())["r"]),
                      "k": R5["vertices"][v]["k"]} for v in PR.VERTICES}
        PR.check_frozen(frozen, self.fx.p)
        frozen["nuwro"]["r"] = frozen["nuwro"]["r"].copy()
        frozen["nuwro"]["r"][100] *= 1 + 1e-9
        with self.assertRaises(SystemExit) as cm:
            PR.check_frozen(frozen, self.fx.p)
        self.assertIn("frozen nuwro", str(cm.exception))


# ---------------------------------------------------------------- the weighted regressor


REWEIGHT = onc._reweight
LO = np.array([L.FINE[a][0] for a in L.AXES5])
HI = np.array([min(L.FINE[a][-1], c) for a, c in zip(L.AXES5, (4.5, 20.0, 3.0, 2.0, 3.0))])


class StubClf:
    def __init__(self, **kw):
        self.params = dict(kw)

    def set_params(self, **kw):
        self.params.update(kw)
        return self

    def get_params(self):
        return dict(self.params)

    def fit(self, X, y, sample_weight=None):
        X, y = np.asarray(X), np.asarray(y)
        w = np.ones(len(y)) if sample_weight is None else np.asarray(sample_weight, float)
        self.cut = float(np.median(X[:, 0]))
        lo = X[:, 0] < self.cut
        self.p = [float(w[m & (y == 1)].sum() / w[m].sum()) for m in (lo, ~lo)]
        return self

    def predict_proba(self, X):
        p = np.where(np.asarray(X)[:, 0] < self.cut, self.p[0], self.p[1])
        return np.column_stack([1 - p, p])


class StubReg(StubClf):
    """Records every fit: its row count, its sample weight and the w_push its loop had reached (from clf2)."""
    fits: list = []
    GEN = None

    def fit(self, X, y, sample_weight=None):
        clf2 = self.params.get("_clf2")
        push = None
        if clf2 is not None and StubReg.GEN is not None:
            push = REWEIGHT(StubReg.GEN, clf2) if hasattr(clf2, "cut") else np.ones(len(StubReg.GEN))
        StubReg.fits.append({"n": len(y), "w": None if sample_weight is None else np.array(sample_weight), "push": push})
        w = np.ones(len(y)) if sample_weight is None else np.asarray(sample_weight, float)
        lo = np.asarray(X)[:, 0] < 1.0
        self.m = [float((w * y)[m].sum() / w[m].sum()) if m.any() else 1.0 for m in (lo, ~lo)]
        return self

    def predict(self, X):
        return np.where(np.asarray(X)[:, 0] < 1.0, self.m[0], self.m[1])


def stub_make(kind, nvars, seed=None):
    clf2 = StubClf()
    return StubClf(), clf2, StubReg(_clf2=clf2)


def loop_unfold(d, cols, seed, threads, iters):
    _, wpush = onc.omnifold_loop(d["MCgen"], d["MCreco"], d["measured"], d["pass_reco"], d["pass_truth"],
                                 np.ones(len(d["measured"]), bool), iters, kind="lgbm", MCgen_weights=d["w_truth"],
                                 MCreco_weights=d["w_reco"], measured_weights=d["measured_weights"], seed=seed,
                                 verbose=False)
    return wpush, []


def toy(seed=5, n=3000, uniform=False, all_reco=False):
    """A toy MC on the five truth features, inside the fine grid."""
    rng = np.random.default_rng(seed)
    gen = LO + (HI - LO) * rng.random((n, 5))
    reco = gen * rng.normal(1.0, 0.05, (n, 5))
    pt = rng.random(n) < 0.9
    pr = np.ones(n, bool) if all_reco else rng.random(n) < (0.4 + 0.5 * (gen[:, 0] / HI[0]))
    w = np.ones(n) if uniform else rng.uniform(0.3, 3.0, n)
    meas = LO + (HI - LO) * rng.random((1500, 5)) ** 1.2
    return {"MCgen": gen, "MCreco": reco, "pass_truth": pt, "pass_reco": pr, "w_truth": w, "w_reco": w * 1.1,
            "measured": meas, "measured_weights": np.ones(1500)}


class WeightedRegressor(unittest.TestCase):
    def setUp(self):
        self.saved = (onc.make_estimators, onc._reweight, PU.unfold, PU.main, s5n_pseudo.write_product, L.row_weight,
                      UF.s5c_unfold.load_inputs, UF.s5p_truths.hypothesis_weight, UF.A7_HYPOTHESIS_SHA256)
        onc.make_estimators = stub_make
        StubReg.fits, StubReg.GEN = [], None

    def tearDown(self):
        (onc.make_estimators, onc._reweight, PU.unfold, PU.main, s5n_pseudo.write_product, L.row_weight,
         UF.s5c_unfold.load_inputs, UF.s5p_truths.hypothesis_weight, UF.A7_HYPOTHESIS_SHA256) = self.saved

    def test_the_regressor_is_fitted_on_w_push_times_w_truth_of_the_reco_passing_truth_rows(self):
        d = toy()
        m = d["pass_truth"]
        StubReg.GEN = d["MCgen"][m]
        ev = {}
        UF.instrument(loop_unfold, ev, True, False)(d, None, 42, 32, 4)
        pr = d["pass_reco"][m]
        wt = d["w_truth"][m][pr]
        self.assertEqual(len(StubReg.fits), 4)
        self.assertTrue(np.all(StubReg.fits[0]["push"] == 1.0))
        for f in StubReg.fits:
            self.assertTrue(np.array_equal(f["w"], wt * f["push"][pr]))
        self.assertFalse(np.array_equal(StubReg.fits[2]["w"], StubReg.fits[0]["w"]))
        self.assertEqual(ev["fit_calls"], 4)
        self.assertEqual(ev["weight_sums"], [float(f["w"].sum()) for f in StubReg.fits])
        self.assertIs(onc.make_estimators, stub_make)
        self.assertIs(onc._reweight, REWEIGHT)

    def test_unit_weights_and_no_push_reproduce_nothing_but_the_weighting_changes_the_loop(self):
        d = toy()
        plain, _ = loop_unfold(d, None, 42, 32, 3)
        weighted, _ = UF.instrument(loop_unfold, {}, True, False)(d, None, 42, 32, 3)
        self.assertFalse(np.array_equal(plain, weighted))
        same, _ = UF.instrument(loop_unfold, {}, False, False)(d, None, 42, 32, 3)
        self.assertTrue(np.array_equal(plain, same))

    def test_the_transfer_diagnostic_leaves_the_loop_untouched_and_records_every_iteration(self):
        d = toy()
        plain, _ = loop_unfold(d, None, 42, 32, 3)
        StubReg.fits = []
        ev = {}
        out, _ = UF.instrument(loop_unfold, ev, False, True)(d, None, 42, 32, 3)
        self.assertTrue(np.array_equal(plain, out))
        m = d["pass_truth"]
        n = int(d["pass_reco"][m].sum())
        self.assertEqual([f["n"] for f in StubReg.fits], [n - int(UF.mask_of(n, k).sum()) if i % 2 == 0 else n
                                                         for k in range(3) for i in range(2)])
        self.assertTrue(all(f["w"] is None for f in StubReg.fits))
        self.assertEqual([t["iteration"] for t in ev["transfer_records"]], [0, 1, 2])
        self.assertTrue(all(t["n_masked"] == int(UF.mask_of(n, t["iteration"]).sum()) for t in ev["transfer_records"]))
        self.assertTrue(np.array_equal(UF.mask_of(n, 1), UF.mask_of(n, 1)))
        self.assertFalse(np.array_equal(UF.mask_of(n, 1), UF.mask_of(n, 2)))
        self.assertEqual((UF.TRANSFER_SEED, UF.TRANSFER_FRACTION), (20261111, 0.2))
        self.assertLess(abs(UF.mask_of(100000, 0).mean() - 0.2), 0.01)
        self.assertEqual(len(ev["transfer_records"][0]["cell_bias"]), 16)
        StubReg.fits = []
        UF.instrument(loop_unfold, {}, True, True)(d, None, 42, 32, 2)
        probe, loop = StubReg.fits[2], StubReg.fits[3]
        mk = UF.mask_of(n, 1)
        self.assertTrue(np.array_equal(probe["w"], loop["w"][~mk]))

    def test_the_transfer_summary(self):
        y = np.array([1.0, 2.0, 1.0, 4.0])
        pred = np.array([1.5, 2.0, 0.5, 4.0])
        w = np.array([1.0, 1.0, 2.0, 1.0])
        cell = np.array([0, 0, 1, -1])
        acc = np.array([0.1, 0.5, 0.9, np.nan])
        s = UF.summarize(pred, y, w, cell, acc, 3)
        self.assertEqual(s["iteration"], 3)
        self.assertAlmostEqual(s["rel_bias"], (0.5 - 1.0) / 9.0)
        self.assertAlmostEqual(s["rel_rms"], np.sqrt((0.25 + 2 * 0.25) / 5) / (9 / 5))
        self.assertAlmostEqual(s["cell_bias"][0], 3.5 / 3.0 - 1)
        self.assertAlmostEqual(s["cell_bias"][1], 1.0 / 2.0 - 1)
        self.assertIsNone(s["cell_bias"][2])
        self.assertEqual(len(s["acceptance_decile_rel_bias"]), 10)
        self.assertAlmostEqual(s["acceptance_decile_rel_bias"][0], 0.5)
        self.assertAlmostEqual(s["acceptance_decile_rel_bias"][-1], -0.5)

    def test_the_wrapper_refuses_extra_arguments_wrong_rows_missing_fits_and_bad_weights(self):
        d = toy()

        def extra_kw(d_, cols, seed, threads, iters):
            onc.make_estimators("lgbm", 5)[2].fit(d_["MCgen"][:3], np.ones(3), sample_weight=np.ones(3))

        def wrong_rows(d_, cols, seed, threads, iters):
            onc.make_estimators("lgbm", 5)[2].fit(d_["MCgen"][:3], np.ones(3))

        for orig, msg in ((extra_kw, "beyond"), (wrong_rows, "rows")):
            with self.assertRaises(UF.WrapError) as cm:
                UF.instrument(orig, {}, True, False)(d, None, 42, 32, 2)
            self.assertIn(msg, str(cm.exception))
            self.assertIs(onc.make_estimators, stub_make)
            self.assertIs(onc._reweight, REWEIGHT)
        with self.assertRaises(UF.WrapError) as cm:
            UF.instrument(loop_unfold, {}, True, False)(toy(all_reco=True), None, 42, 32, 2)
        self.assertIn("0 instrumented regressor fits for 2", str(cm.exception))
        bad = toy()
        bad["w_truth"][np.flatnonzero(bad["pass_truth"] & bad["pass_reco"])[0]] = 0.0
        with self.assertRaises(UF.WrapError):
            UF.instrument(loop_unfold, {}, True, False)(bad, None, 42, 32, 2)
        with self.assertRaises(UF.WrapError):
            UF.instrument(lambda *a: onc.make_estimators("nn", 2), {}, True, False)(d, None, 42, 32, 1)
        with self.assertRaises(UF.WrapError):
            UF.instrument(loop_unfold, {}, False, True)(d, [0, 1], 42, 32, 1)

    def main_with(self, argv, body):
        """UF.main over a fake pvl_unfold.main that runs ``body`` and writes; returns the written meta."""
        written = {}

        def capture(out, arrays, meta):
            written["meta"] = meta
            return 0

        PU.unfold, s5n_pseudo.write_product = loop_unfold, capture

        def fake_main(rest):
            written["argv"] = rest
            written["wrapped"] = PU.unfold is not loop_unfold
            body()
            return s5n_pseudo.write_product(Path("x.npz"), {}, {"schema": "pvl-unfold/1"})

        PU.main = fake_main
        self.assertEqual(UF.main(argv), 0)
        self.assertIs(PU.unfold, loop_unfold)
        self.assertIs(s5n_pseudo.write_product, capture)
        return written

    def test_main_records_the_options_and_restores_every_patch(self):
        d = toy()
        for weight, transfer, calls in (("w_push_w_truth", False, 3), ("none", False, None), ("none", True, 3)):
            StubReg.fits = []
            argv = ["--regressor-weight", weight, "--rung", "L-5D-PV"] + (["--transfer"] if transfer else [])
            w = self.main_with(argv, lambda: PU.unfold(d, None, 42, 32, 3))
            self.assertEqual(w["argv"], ["--rung", "L-5D-PV"])
            self.assertEqual(w["wrapped"], weight != "none" or transfer)
            rsn = w["meta"]["rsn"]
            self.assertEqual((rsn["regressor_weight"], rsn["fit_calls"], rsn["truth"], rsn["transfer"]),
                             (weight, calls, "ratio", transfer))
            self.assertEqual(len(rsn.get("transfer_records", [])), 3 if transfer else 0)
            self.assertEqual(rsn.get("weight_sums") is not None, weight != "none")
            self.assertEqual(rsn["code_sha256"]["rsn_unfold.py"], L.sha256_path(HERE / "rsn_unfold.py"))

    def test_an_instrumented_step_refuses_to_write_when_the_regressor_never_ran(self):
        s5n_pseudo.write_product = lambda out, arrays, meta: 0
        PU.main = lambda argv: s5n_pseudo.write_product(Path("x.npz"), {}, {})
        for argv in (["--regressor-weight", "w_push_w_truth"], ["--regressor-weight", "none", "--transfer"]):
            with self.assertRaises(UF.WrapError):
                UF.main(argv)

    def truth_inputs(self):
        d = toy()
        d["edges"] = [np.asarray(L.FINE[a], float) for a in L.AXES5]
        identity = {"schema": L.RATIO_SCHEMA, "axes": list(L.AXES5), "r": [1.0] * NFINE, "identity": True}
        return d, identity

    def test_a_declared_truth_replaces_the_identity_reweight(self):
        d, identity = self.truth_inputs()
        fake_load = UF.s5c_unfold.load_inputs = lambda path: d
        got = {}

        def body():
            inputs = UF.s5c_unfold.load_inputs("x.npz")
            got["r"] = L.row_weight(inputs["MCgen"], L.AXES5, identity, inputs["pass_truth"])

        w = self.main_with(["--regressor-weight", "none", "--truth", "q3", "--closure"], body)
        want = UF.s5c_pseudo.truth_weight("q3_given_eavail_w", d["MCgen"], d["edges"], 0.3, w_truth=d["w_truth"])
        self.assertTrue(np.array_equal(got["r"], want))
        self.assertFalse(np.all(want == 1.0))
        self.assertEqual(w["meta"]["rsn"]["truth"], "q3")
        self.assertIs(UF.s5c_unfold.load_inputs, fake_load)
        self.assertIs(L.row_weight, self.saved[5])
        seen = {}

        def hyp(gen, edges, w_truth, ratio, amplitude):
            seen.update(ratio=ratio, amplitude=amplitude)
            return np.full(len(gen), 0.9)

        UF.s5c_unfold.load_inputs = lambda path: d
        UF.s5p_truths.hypothesis_weight = hyp
        w = self.main_with(["--regressor-weight", "none", "--truth", "a7_gibuu", "--closure"], body)
        self.assertEqual(seen["ratio"], json.loads(UF.A7_HYPOTHESIS.read_text()))
        self.assertEqual(seen["amplitude"], 1.0)
        self.assertTrue(np.all(got["r"] == 0.9))
        self.assertEqual(w["meta"]["rsn"]["a7_hypothesis_sha256"], UF.A7_HYPOTHESIS_SHA256)

    def test_a_declared_truth_refuses_off_a_closure_a_non_identity_ratio_and_a_changed_hypothesis(self):
        d, identity = self.truth_inputs()
        with self.assertRaises(UF.WrapError):
            UF.main(["--regressor-weight", "none", "--truth", "q3"])
        UF.s5c_unfold.load_inputs = lambda path: d
        bad = dict(identity, identity=False)
        PU.main = lambda rest: L.row_weight(UF.s5c_unfold.load_inputs("x")["MCgen"], L.AXES5, bad, d["pass_truth"])
        with self.assertRaises(UF.WrapError) as cm:
            UF.main(["--regressor-weight", "none", "--truth", "q3", "--closure"])
        self.assertIn("identity", str(cm.exception))
        UF.A7_HYPOTHESIS_SHA256 = "0" * 64
        PU.main = lambda rest: L.row_weight(UF.s5c_unfold.load_inputs("x")["MCgen"], L.AXES5, identity, d["pass_truth"])
        with self.assertRaises(UF.WrapError) as cm:
            UF.main(["--regressor-weight", "none", "--truth", "a7_gibuu", "--closure"])
        self.assertIn("pinned", str(cm.exception))


# ---------------------------------------------------------------- C_model variants


def frozen_meta(closure=False, ratio="13bb1eae4ce0db4023bb29a5b98ca8b7e1e22288a1547f6a31a735fa1445435b"):
    return {"schema": "pvl-unfold/1", "rung": "L-5D-PV", "arm": "e", "features": list(L.AXES5), "closure": closure,
            "ratio_sha256": ratio, "estimator_seed": 42, "iters": 5, "threads": 32, "input_npz_sha256": "n" * 64,
            "bkg_dump_sha256": "b" * 64, "estimator_params": [{"n_estimators": 100}] * 3,
            "refinement": ({"ran": False, "reason": "no negative weights (signal-only reference)"} if closure
                           else {"ran": True, "classifier_params": {"n_estimators": 400}})}


def save(path: Path, x, meta, xt=None):
    arrays = {"xsec_flat": np.asarray(x, float)}
    if xt is not None:
        arrays["xtrue_flat"] = np.asarray(xt, float)
    np.savez(path, meta=json.dumps(meta), **arrays)


class CModel(unittest.TestCase):
    PVL = CM.sums(ND / "pv-ladder" / "prep-SHA256SUMS")

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        rng = np.random.default_rng(11)
        self.rmap, self.n = reporting_map()
        x0 = rng.uniform(1.0, 2.0, NFINE)
        self.x0 = x0
        self.frozen_dir, self.rsn_dir = d / "frozen", d / "rsn"
        self.frozen_dir.mkdir()
        self.rsn_dir.mkdir()
        save(self.frozen_dir / "L-5D-PV_e_tune_v1.npz", x0, frozen_meta())
        self.prod = {"L-5D-PV_e_tune_v1": {"x": x0}}
        for v in B5.VERTICES:
            self.prod[f"L-5D-PV_e_{v}"] = {"x": x0 * rng.uniform(0.9, 1.1, NFINE)}
        for _, ref in CM.CLOSURES.values():
            if ref.startswith("frozen:"):
                self.prod[ref[7:]] = {"x": x0 * rng.uniform(0.99, 1.01, NFINE), "xtrue": x0 * rng.uniform(0.98, 1.02, NFINE)}
        self.S0 = B5.factor(self.prod, self.rmap, self.n)
        self.cmodel_json = d / "cmodel.json"
        self.cmodel_json.write_text(json.dumps({"S": self.S0.tolist()}))
        self.rsums = d / "rsn-prep-SHA256SUMS"
        self.ratio = {"G6/gibuu": "1" * 64, "SM/genie_mec": "2" * 64, "SM/nuwro": "3" * 64, "SM/gibuu": "4" * 64}
        self.rsums.write_text("".join(f"{s}  ./{k}.json\n" for k, s in self.ratio.items()))
        self.rsn_x, self.rsn_xt = {}, {}
        for task, spec in CM.tasks().items():
            want = CM.ratio_sha(spec["ratio"], self.PVL, CM.sums(self.rsums))
            m = dict(frozen_meta(spec["closure"], want), rsn=self.rsn_meta(spec, task))
            x = x0 if task in ("rsn_nc", "TR_data") else x0 * rng.uniform(0.95, 1.05, NFINE)
            xt = x0 * rng.uniform(0.98, 1.02, NFINE) if spec["closure"] else None
            self.rsn_x[task], self.rsn_xt[task] = x, xt
            save(self.rsn_dir / f"{task}.npz", x, m, xt)
        self.saved = CM.frozen
        CM.frozen = lambda a: (self.rmap, self.n, self.prod, x0)

    def tearDown(self):
        CM.frozen = self.saved
        self.tmp.cleanup()

    @staticmethod
    def rsn_meta(spec, task):
        inst = spec["regressor_weight"] != "none" or spec["transfer"]
        rec = {"regressor_weight": spec["regressor_weight"], "truth": spec["truth"], "transfer": spec["transfer"],
               "fit_calls": 5 if inst else None}
        if spec["transfer"]:
            rec["transfer_records"] = [{"iteration": k, "task": task} for k in range(5)]
        return rec

    def args(self, **kw):
        d = Path(self.tmp.name)
        a = dict(products=self.frozen_dir, p5=None, rsn_products=self.rsn_dir, rsn_prep_sums=self.rsums,
                 cmodel_json=self.cmodel_json, out_json=d / "out" / "c.json", out_npz=d / "c.npz")
        a.update(kw)
        return type("A", (), a)

    def X(self, x):
        return B5.integrals(x, self.rmap, self.n)

    def test_the_arms_are_built_from_the_declared_rows(self):
        out = quiet(CM.run_build, self.args())
        S = {k: np.asarray(v["S"]) for k, v in out["arms"].items()}
        X0 = self.X(self.x0)
        self.assertTrue(np.array_equal(S["nominal"], self.S0))
        self.assertTrue(np.array_equal(S["G6"][:2], self.S0[:2]))
        self.assertTrue(np.array_equal(S["G6"][2], self.X(self.rsn_x["G6_gibuu"]) / X0 - 1))
        for i, v in enumerate(B5.VERTICES):
            self.assertTrue(np.array_equal(S["SM"][i], self.X(self.rsn_x[f"SM_{v}"]) / X0 - 1))
        self.assertTrue(np.array_equal(out["wr"]["delta"], self.X(self.rsn_x["WR_data"]) / X0 - 1))
        b = out["wr"]["closures"]["nuwro"]
        self.assertTrue(np.array_equal(b["bias_weighted"], self.X(self.rsn_x["WR_closure_nuwro"])
                                       / self.X(self.rsn_xt["WR_closure_nuwro"]) - 1))
        fr = self.prod["L-5D-PV_e_closure_nuwro"]
        self.assertTrue(np.array_equal(b["bias_equal_weights"], self.X(fr["x"]) / self.X(fr["xtrue"]) - 1))
        for t in ("gibuu", "q3"):
            b = out["wr"]["closures"][t]
            self.assertEqual(b["reference"], f"rsn:WU_closure_{t}")
            self.assertTrue(np.array_equal(b["bias_weighted"], self.X(self.rsn_x[f"WR_closure_{t}"])
                                           / self.X(self.rsn_xt[f"WR_closure_{t}"]) - 1))
            self.assertTrue(np.array_equal(b["bias_equal_weights"], self.X(self.rsn_x[f"WU_closure_{t}"])
                                           / self.X(self.rsn_xt[f"WU_closure_{t}"]) - 1))
        self.assertEqual({k: v[0]["task"] for k, v in out["transfer"].items()},
                         {"data": "TR_data", "gibuu": "WU_closure_gibuu", "q3": "WU_closure_q3"})
        c = out["arms"]["G6"]
        C = S["G6"].T @ S["G6"]
        self.assertTrue(np.allclose(c["sqrt_diag"], np.sqrt(np.diag(C))))
        self.assertAlmostEqual(sum(c["trace_share_by_vertex"].values()), 1.0, places=12)
        with np.load(Path(self.tmp.name) / "c.npz") as z:
            self.assertEqual(sorted(z.files), ["S_G6", "S_SM", "S_nominal"])

    def test_without_sm_reweights_the_sm_arm_is_not_built(self):
        self.rsums.write_text(f"{self.ratio['G6/gibuu']}  ./G6/gibuu.json\n")
        for v in B5.VERTICES:
            (self.rsn_dir / f"SM_{v}.npz").unlink()
        out = quiet(CM.run_build, self.args())
        self.assertFalse(out["sm_built"])
        self.assertEqual(set(out["arms"]), {"nominal", "G6"})

    def test_the_nc_and_nc_s_refuse(self):
        x = self.x0.copy()
        x[17] = np.nextafter(x[17], 3.0)
        m = dict(frozen_meta(), rsn=self.rsn_meta(CM.tasks()["rsn_nc"], "rsn_nc"))
        save(self.rsn_dir / "rsn_nc.npz", x, m)
        with self.assertRaises(SystemExit) as cm:
            quiet(CM.run_build, self.args())
        self.assertIn("nominal control", str(cm.exception))
        save(self.rsn_dir / "rsn_nc.npz", self.x0, m)
        bad = Path(self.tmp.name) / "bad.json"
        S = self.S0.copy()
        S[1, 4] = np.nextafter(S[1, 4], 1.0)
        bad.write_text(json.dumps({"S": S.tolist()}))
        with self.assertRaises(SystemExit) as cm:
            quiet(CM.run_build, self.args(cmodel_json=bad))
        self.assertIn("NC-S", str(cm.exception))

    def test_a_transfer_step_that_moved_the_loop_refuses(self):
        spec = CM.tasks()["TR_data"]
        m = dict(frozen_meta(), rsn=self.rsn_meta(spec, "TR_data"))
        x = self.x0.copy()
        x[5] = np.nextafter(x[5], 0.0)
        save(self.rsn_dir / "TR_data.npz", x, m)
        with self.assertRaises(SystemExit) as cm:
            quiet(CM.run_build, self.args())
        self.assertIn("TR_data differs", str(cm.exception))

    def test_nc_alone_passes_and_refuses_a_differing_product(self):
        out = Path(self.tmp.name) / "nc.json"
        a = self.args(product=self.rsn_dir / "rsn_nc.npz", out=out)
        quiet(CM.run_nc, a)
        self.assertEqual(json.loads(out.read_text())["verdict"], "PASS")
        x = self.x0.copy()
        x[0] *= 1 + 1e-15
        save(self.rsn_dir / "other.npz", x, dict(frozen_meta(), rsn=self.rsn_meta(CM.tasks()["rsn_nc"], "rsn_nc")))
        with self.assertRaises(SystemExit):
            quiet(CM.run_nc, self.args(product=self.rsn_dir / "other.npz", out=Path(self.tmp.name) / "nc2.json"))

    def test_each_wrong_meta_field_refuses(self):
        ref = frozen_meta()
        spec = {"closure": False, "regressor_weight": "w_push_w_truth", "truth": "ratio", "transfer": False}
        good = dict(frozen_meta(), rsn=self.rsn_meta(spec, "x"))
        self.assertEqual(CM.meta_problems(good, spec, ref["ratio_sha256"], ref), [])
        r = good["rsn"]
        for k, v in (("rung", "L-4D"), ("arm", "c"), ("features", ["pt"]), ("closure", True), ("ratio_sha256", "x"),
                     ("estimator_seed", 43), ("iters", 4), ("threads", 16), ("input_npz_sha256", "x"),
                     ("bkg_dump_sha256", "x"), ("estimator_params", []), ("refinement", {"ran": True}),
                     ("rsn", dict(r, regressor_weight="none")), ("rsn", dict(r, fit_calls=4)),
                     ("rsn", dict(r, truth="q3")), ("rsn", dict(r, transfer=True))):
            self.assertTrue(CM.meta_problems(dict(good, **{k: v}), spec, ref["ratio_sha256"], ref), k)
        cspec = {"closure": True, "regressor_weight": "none", "truth": "q3", "transfer": True}
        cl = dict(frozen_meta(True), rsn=self.rsn_meta(cspec, "x"))
        self.assertEqual(CM.meta_problems(cl, cspec, ref["ratio_sha256"], ref), [])
        self.assertTrue(CM.meta_problems(dict(cl, refinement={"ran": True}), cspec, ref["ratio_sha256"], ref))
        short = dict(cl, rsn=dict(cl["rsn"], transfer_records=cl["rsn"]["transfer_records"][:4]))
        self.assertTrue(CM.meta_problems(short, cspec, ref["ratio_sha256"], ref))
        none = dict(cl, rsn=dict(cl["rsn"], fit_calls=None))
        self.assertTrue(CM.meta_problems(none, cspec, ref["ratio_sha256"], ref))

    def test_the_task_table(self):
        T = CM.tasks()
        self.assertEqual(list(T), ["rsn_nc", "G6_gibuu", "SM_genie_mec", "SM_nuwro", "SM_gibuu", "WR_data",
                                   "WR_closure_tune_v1", "WR_closure_nuwro", "TR_data", "WR_closure_gibuu",
                                   "WR_closure_q3", "WU_closure_gibuu", "WU_closure_q3"])
        self.assertEqual([t for t, s in T.items() if s["regressor_weight"] == "w_push_w_truth"],
                         ["WR_data", "WR_closure_tune_v1", "WR_closure_nuwro", "WR_closure_gibuu", "WR_closure_q3"])
        self.assertEqual([t for t, s in T.items() if s["closure"]],
                         ["WR_closure_tune_v1", "WR_closure_nuwro", "WR_closure_gibuu", "WR_closure_q3",
                          "WU_closure_gibuu", "WU_closure_q3"])
        self.assertEqual([t for t, s in T.items() if s["transfer"]], ["TR_data", "WU_closure_gibuu", "WU_closure_q3"])
        self.assertEqual({t: s["truth"] for t, s in T.items() if s["truth"] != "ratio"},
                         {"WR_closure_gibuu": "a7_gibuu", "WR_closure_q3": "q3", "WU_closure_gibuu": "a7_gibuu",
                          "WU_closure_q3": "q3"})
        self.assertTrue(all(s["ratio"] == "frozen:tune_v1" for s in T.values() if s["truth"] != "ratio"))
        self.assertEqual(T["WR_closure_nuwro"]["ratio"], "frozen:nuwro")
        jobs = {}
        for t, s in T.items():
            jobs.setdefault(s["job"], []).append(t)
        self.assertEqual({j: len(v) for j, v in jobs.items()}, {"J1": 1, "J2": 8, "J3": 4})
        rows = [ln.split("\t") for ln in (HERE / "rsn_tasks.tsv").read_text().splitlines() if ln and not ln.startswith("#")]
        j2 = [r[:1] + r[2:8] for r in rows if r[1] == "J2" and r[2] != "SM"]
        j2n = [r[:1] + r[2:8] for r in rows if r[1] == "J2n"]
        self.assertEqual(j2, j2n)


# ---------------------------------------------------------------- the regrade


class RegradeFixture:
    def __init__(self, d: Path, seed=13):
        rng = np.random.default_rng(seed)
        self.d = d
        self.TR = RG.truths(RG.F1_PREP_SUMS)
        table = {"names": np.array([t["name"] for t in self.TR])}
        sets = []
        for t in self.TR:
            sets.append(t["name"])
            if t["row"] == 4:
                sets.append("cal:" + t["name"])
        for name in sets:
            row = next((t["row"] for t in self.TR if t["name"] == name), 4)
            k = name.replace(":", "_")
            nexp = 1 if row in (3, 8) else 6
            table[f"r_{k}"] = rng.normal(0, 0.03, (nexp, 16))
            if name.startswith("cal:") or row == 6:
                table[f"flux_{k}"] = rng.integers(0, 100, nexp)
        self.table = d / "table.npz"
        np.savez(self.table, **table)
        self.w_all = rng.uniform(0.5, 1.5, 100)
        f = rng.uniform(1.0, 2.0, 16)
        A = rng.normal(size=(16, 16))
        Cstat = (A @ A.T / 16 + np.eye(16)) * 1e-4 * np.outer(f, f)
        B = rng.normal(size=(16, 16))
        Ce = Cstat + (B @ B.T / 16) * 1e-3 * np.outer(f, f)
        self.s1 = d / "s1.npz"
        np.savez(self.s1, meta=json.dumps({"blocks": ["stat", "flux"]}), f=f, C_e=Ce, C_stat=Cstat)
        Cx = np.diag(rng.uniform(1e-4, 4e-4, 16)) * np.outer(f, f)
        self.extra = d / "extra.npz"
        np.savez(self.extra, **{RG.EXTRA_KEY: Cx})
        self.S0 = rng.normal(0, 0.03, (3, 16))
        self.cmodel = d / "cmodel.json"
        self.cmodel.write_text(json.dumps({"S": self.S0.tolist()}))
        self.f, self.Ce_rel, self.Cstat_rel, self.Cx_rel = f, Ce / np.outer(f, f), Cstat / np.outer(f, f), Cx / np.outer(f, f)

    def arms(self, path: Path, **S):
        np.savez(path, S_nominal=self.S0, **{f"S_{k}": v for k, v in S.items()})
        return path

    def readout(self, path: Path, edit=None):
        """A committed-format F1 readout made from the nominal grade, optionally edited."""
        with np.load(self.table) as z:
            table = {k: z[k] for k in z.files}
        est, op = RG.estimates(self.TR, table, self.w_all)
        g = RG.grade_all(self.TR, est, op, self.S0, self.Ce_rel, self.Cstat_rel, self.Cx_rel)
        rec = {"truths": g["records"], "controls": {"offset_control_7": {"pass": op["pass"], "chi2": op["chi2"], "p": op["p"]}},
               "triggers": {"by_group": g["by_group"]}}
        rec = json.loads(json.dumps(rec))
        if edit:
            edit(rec)
        path.write_text(json.dumps(rec))
        return path


class Regrade(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.fx = RegradeFixture(Path(cls.tmp.name))
        with np.load(cls.fx.table) as z:
            cls.table = {k: z[k] for k in z.files}
        cls.est, cls.op = RG.estimates(cls.fx.TR, cls.table, cls.fx.w_all)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def setUp(self):
        self.saved = (dict(RG.PINS), R.sa.flux_weights)
        R.sa.flux_weights = lambda path: self.fx.w_all

    def tearDown(self):
        RG.PINS.clear()
        RG.PINS.update(self.saved[0])
        R.sa.flux_weights = self.saved[1]

    def test_the_estimates_are_fd_f0_regrade_s(self):
        r = lambda n: self.table[f"r_{n.replace(':', '_')}"]  # noqa: E731
        t1 = next(t for t in self.fx.TR if t["row"] == 1)
        b, N, B = R.unweighted(r(t1["name"]))
        self.assertTrue(np.array_equal(self.est[t1["name"]][0], b) and np.array_equal(self.est[t1["name"]][1], N))
        t3 = next(t for t in self.fx.TR if t["row"] == 3)
        self.assertTrue(np.array_equal(self.est[t3["name"]][0], r(t3["name"])[0]))
        self.assertFalse(self.est[t3["name"]][1].any())
        t6 = next(t for t in self.fx.TR if t["row"] == 6)
        ref = t6["ref"]
        bw4, Nw4, _ = R.weighted(r("cal:" + ref), self.fx.w_all[self.table[f"flux_cal_{ref}"]])
        b4, N4, _ = R.unweighted(r(ref))
        bw, Nw, _ = R.weighted(r(t6["name"]), self.fx.w_all[self.table[f"flux_{t6['name']}"]])
        self.assertTrue(np.allclose(self.est[t6["name"]][0], bw - (bw4 - b4), rtol=0, atol=1e-15))
        self.assertTrue(np.allclose(self.est[t6["name"]][1], Nw + Nw4 + N4, rtol=1e-14, atol=0))

    def test_each_grade_uses_the_arm_s_rows_with_the_own_vertex_left_out(self):
        rng = np.random.default_rng(3)
        S = rng.normal(0, 0.05, (3, 16))
        g = RG.grade_all(self.fx.TR, self.est, self.op, S, self.fx.Ce_rel, self.fx.Cstat_rel, self.fx.Cx_rel)
        recs = {r["name"]: r for r in g["records"]}
        for t in self.fx.TR:
            keep = [j for j, v in enumerate(R.VERTICES) if v != t["own"]]
            b, N = self.est[t["name"]][:2]
            C = self.fx.Ce_rel + S[keep].T @ S[keep] + self.fx.Cx_rel
            self.assertEqual(recs[t["name"]]["grade"], R.grade(b, N, C), t["name"])
            Cm = self.fx.Cstat_rel + S[keep].T @ S[keep]
            self.assertEqual(recs[t["name"]]["model_only"], R.grade(b, N, Cm), t["name"])
        sig = np.sqrt(np.diag(self.fx.Ce_rel + S.T @ S + self.fx.Cx_rel))
        self.assertTrue(np.allclose(g["reported_relative_sigma"], sig, rtol=1e-15, atol=0))
        self.assertEqual(g["listed"], [r["name"] for r in g["records"] if r["listed"]])

    def test_nc_r_reproduces_and_refuses_on_any_differing_field(self):
        nom = RG.grade_all(self.fx.TR, self.est, self.op, self.fx.S0, self.fx.Ce_rel, self.fx.Cstat_rel, self.fx.Cx_rel)
        d = Path(tempfile.mkdtemp(dir=self.tmp.name))
        RG.reproduce(nom, self.op, json.loads(self.fx.readout(d / "ok.json").read_text()))

        def e_bias(r): r["truths"][2]["bias"][4] += 1e-9  # noqa: E704
        def e_chi2(r): r["truths"][5]["grade"]["chi2"] *= 1 + 1e-8  # noqa: E704
        def e_flag(r): r["truths"][1]["grade"]["p_lt_0.01"] = not r["truths"][1]["grade"]["p_lt_0.01"]  # noqa: E704
        def e_cells(r): r["truths"][0]["grade"]["cells_abs_z_gt_2"].append("R15")  # noqa: E704
        def e_sub(r): r["truths"][0]["model_only"]["z"][0] += 1e-6  # noqa: E704
        def e_listed(r): r["truths"][3]["listed"] = not r["truths"][3]["listed"]  # noqa: E704
        def e_group(r): r["triggers"]["by_group"]["prior"]["cells_abs_z_gt_2"] += 1  # noqa: E704
        def e_order(r): r["truths"][0], r["truths"][1] = r["truths"][1], r["truths"][0]  # noqa: E704
        def e_ctrl(r): r["controls"]["offset_control_7"]["pass"] = not r["controls"]["offset_control_7"]["pass"]  # noqa: E704
        def e_c7chi2(r): r["controls"]["offset_control_7"]["chi2"] *= 1 + 1e-8  # noqa: E704
        def e_c7p(r): r["controls"]["offset_control_7"]["p"] = r["controls"]["offset_control_7"]["p"] * 1.01 + 1e-9  # noqa: E704
        def e_family(r): next(iter(r["triggers"]["by_group"]["prior"]["by_family"].values()))["truths"] += 1  # noqa: E704

        for i, e in enumerate((e_bias, e_chi2, e_flag, e_cells, e_sub, e_listed, e_group, e_order, e_ctrl,
                               e_c7chi2, e_c7p, e_family)):
            with self.assertRaises(SystemExit, msg=e.__name__) as cm:
                RG.reproduce(nom, self.op, json.loads(self.fx.readout(d / f"bad{i}.json", e).read_text()))
            self.assertIn("NC-R", str(cm.exception))

    def test_c_inv_holds_for_a_gibuu_only_change_and_catches_any_other(self):
        nom = RG.grade_all(self.fx.TR, self.est, self.op, self.fx.S0, self.fx.Ce_rel, self.fx.Cstat_rel, self.fx.Cx_rel)
        S = self.fx.S0.copy()
        S[2] *= 0.5
        g6 = RG.grade_all(self.fx.TR, self.est, self.op, S, self.fx.Ce_rel, self.fx.Cstat_rel, self.fx.Cx_rel)
        RG.invariant_g6(nom, g6, self.fx.S0, S)
        self.assertNotEqual([r["grade"] for r in nom["records"]], [r["grade"] for r in g6["records"]])
        own = [r for r in g6["records"] if r["own_vertex"] == "gibuu"]
        self.assertTrue(own and all("p_parallel_lt_4p5" in r for r in own))
        S2 = S.copy()
        S2[0, 3] += 0.01
        bad = RG.grade_all(self.fx.TR, self.est, self.op, S2, self.fx.Ce_rel, self.fx.Cstat_rel, self.fx.Cx_rel)
        with self.assertRaises(SystemExit) as cm:
            RG.invariant_g6(nom, bad, self.fx.S0, self.fx.S0)
        self.assertIn("C-INV", str(cm.exception))
        with self.assertRaises(SystemExit) as cm:
            RG.invariant_g6(nom, g6, self.fx.S0, S2)
        self.assertIn("rows are not", str(cm.exception))
        for k in ("model_only", "p_parallel_lt_4p5"):
            moved = json.loads(json.dumps(g6))
            r = next(r for r in moved["records"] if r["own_vertex"] == "gibuu")
            r[k]["chi2"] += 1.0
            with self.assertRaises(SystemExit, msg=k):
                RG.invariant_g6(nom, moved, self.fx.S0, S)

    def test_the_nominal_only_gate_needs_no_arm_file_and_refuses_a_mismatch(self):
        fx = self.fx
        d = Path(tempfile.mkdtemp(dir=self.tmp.name))
        ro = fx.readout(d / "ro.json")
        RG.PINS.update(table=R.sa.sha256(fx.table), f1_readout=R.sa.sha256(ro), s1_npz=R.sa.sha256(fx.s1),
                       extra_block=R.sa.sha256(fx.extra), cmodel_json=R.sa.sha256(fx.cmodel))
        argv = ["--nominal-only", "--table", str(fx.table), "--f1-readout", str(ro), "--s1-npz", str(fx.s1),
                "--extra-block", str(fx.extra), "--flux-constraint", "x", "--cmodel-json", str(fx.cmodel)]
        quiet(RG.main, argv + ["--out", str(d / "nc_r.json")])
        rec = json.loads((d / "nc_r.json").read_text())
        self.assertEqual((rec["schema"], rec["verdict"], rec["records"]), ("rsn-nc-r/1", "PASS", 22))

        def edit(r):
            r["truths"][7]["grade"]["chi2"] *= 1 + 1e-6
        bad = fx.readout(d / "bad.json", edit)
        RG.PINS["f1_readout"] = R.sa.sha256(bad)
        argv[argv.index(str(ro))] = str(bad)
        with self.assertRaises(SystemExit):
            quiet(RG.main, argv + ["--out", str(d / "nc_r2.json")])
        self.assertFalse((d / "nc_r2.json").exists())
        with self.assertRaises(SystemExit):
            quiet(RG.main, argv[1:] + ["--out", str(d / "nc_r3.json")])

    def cm_json(self, path, S=None):
        rng = np.random.default_rng(21)
        wr = {"delta": rng.normal(0, 0.01, 16).tolist(),
              "closures": {t: {"bias_weighted": rng.normal(0, 0.02, 16).tolist(),
                               "bias_equal_weights": rng.normal(0, 0.02, 16).tolist()}
                           for t in ("tune_v1", "nuwro", "gibuu", "q3")}}
        path.write_text(json.dumps({"arms": {"nominal": {"S": (self.fx.S0 if S is None else S).tolist()}}, "wr": wr}))
        return path

    def test_wr_directions_grade_each_vector_against_its_truth_s_matrix(self):
        cm = json.loads(self.cm_json(Path(tempfile.mkdtemp(dir=self.tmp.name)) / "cm.json").read_text())
        fx = self.fx
        out = RG.wr_directions(cm, fx.Ce_rel, fx.S0, fx.Cx_rel)
        Z = np.zeros((16, 16))
        own = {"tune_v1": None, "nuwro": "nuwro", "gibuu": "gibuu", "q3": None}
        for t, o in own.items():
            keep = [j for j, v in enumerate(R.VERTICES) if v != o]
            M = fx.Ce_rel + fx.S0[keep].T @ fx.S0[keep] + fx.Cx_rel
            bw, bu = (np.asarray(cm["wr"]["closures"][t][k]) for k in ("bias_weighted", "bias_equal_weights"))
            self.assertEqual(out[t]["weighted"], R.grade(bw, Z, M), t)
            self.assertEqual(out[t]["equal_weights"], R.grade(bu, Z, M), t)
            self.assertAlmostEqual(out[t]["change"]["chi2"], R.grade(bw - bu, Z, M)["chi2"], places=9)
            self.assertEqual(out[t]["own_vertex_left_out"], o)
        M0 = fx.Ce_rel + fx.S0.T @ fx.S0 + fx.Cx_rel
        d = np.asarray(cm["wr"]["delta"])
        self.assertEqual(out["data"]["grade"], R.grade(d, Z, M0))
        D = RG.directions(d, M0)
        self.assertAlmostEqual(D["chi2"], R.grade(d, Z, M0)["chi2"], places=9)
        self.assertEqual(len(D["top"]), 3)
        self.assertGreaterEqual(abs(D["top"][0]["component"]), abs(D["top"][2]["component"]))
        self.assertAlmostEqual(RG.along(d, d, M0), np.sqrt(R.grade(d, Z, M0)["chi2"]), places=9)
        self.assertAlmostEqual(RG.along(-d, d, M0), -np.sqrt(R.grade(d, Z, M0)["chi2"]), places=9)

    def run_rg(self, out, arms, readout, cm=None, **pins):
        fx = self.fx
        cm = cm or self.cm_json(out.with_suffix(".cm.json"))
        RG.PINS.update(table=R.sa.sha256(fx.table), f1_readout=R.sa.sha256(readout), s1_npz=R.sa.sha256(fx.s1),
                       extra_block=R.sa.sha256(fx.extra), cmodel_json=R.sa.sha256(fx.cmodel),
                       f1_prep_sums=self.saved[0]["f1_prep_sums"])
        RG.PINS.update(pins)
        argv = ["--table", str(fx.table), "--f1-readout", str(readout), "--s1-npz", str(fx.s1), "--extra-block",
                str(fx.extra), "--flux-constraint", "x", "--cmodel-json", str(fx.cmodel), "--rsn-cmodel", str(arms),
                "--rsn-cmodel-json", str(cm), "--out", str(out)]
        return quiet(RG.main, argv)

    def test_the_regrade_runs_end_to_end_and_refuses_a_wrong_pin_or_nominal_s(self):
        d = Path(tempfile.mkdtemp(dir=self.tmp.name))
        S6 = self.fx.S0.copy()
        S6[2] *= 0.3
        arms = self.fx.arms(d / "arms.npz", G6=S6, SM=self.fx.S0 * 0.7)
        ro = self.fx.readout(d / "ro.json")
        self.run_rg(d / "out.json", arms, ro)
        out = json.loads((d / "out.json").read_text())
        self.assertEqual(set(out["arms"]), {"nominal", "G6", "SM"})
        self.assertEqual(len(out["arms"]["G6"]["records"]), 22)
        self.assertIn("held-out", out["arms"]["SM"]["by_group"])
        self.assertEqual(set(out["wr_directions"]), {"data", "tune_v1", "nuwro", "gibuu", "q3"})
        with self.assertRaises(SystemExit) as cm:
            self.run_rg(d / "o4.json", arms, ro, cm=self.cm_json(d / "cm4.json", S=self.fx.S0 * 1.001))
        self.assertIn("rsn_cmodel.json's nominal S", str(cm.exception))
        with self.assertRaises(SystemExit) as cm:
            self.run_rg(d / "o2.json", arms, ro, f1_prep_sums="0" * 64)
        self.assertIn("sha256", str(cm.exception))
        bad = d / "bad.npz"
        np.savez(bad, S_nominal=self.fx.S0 * (1 + 1e-12), S_G6=S6)
        with self.assertRaises(SystemExit) as cm:
            self.run_rg(d / "o3.json", bad, ro)
        self.assertIn("nominal S", str(cm.exception))
        self.assertFalse((d / "o2.json").exists() or (d / "o3.json").exists() or (d / "o4.json").exists())


# ---------------------------------------------------------------- the readings


class Readings(unittest.TestCase):
    I0 = json.loads((RD.I0).read_text())
    CMJ = json.loads((RD.CMODEL_JSON).read_text())

    def test_the_sigma_classes_and_their_boundaries(self):
        self.assertEqual(RD.sigma_class(np.full(16, 0.79)), "C_model smaller")
        self.assertEqual(RD.sigma_class(np.full(16, 0.8)), "C_model similar")
        self.assertEqual(RD.sigma_class(np.full(16, 1.25)), "C_model similar")
        self.assertEqual(RD.sigma_class(np.full(16, 1.2501)), "C_model larger")
        q = np.ones(16)
        q[3] = 0.5
        self.assertEqual(RD.sigma_class(q), "C_model similar")
        q[3] = 0.4999
        self.assertEqual(RD.sigma_class(q), "C_model reshaped")
        q[3] = 2.0001
        self.assertEqual(RD.sigma_class(q), "C_model reshaped")

    def test_the_listed_classes(self):
        self.assertEqual(RD.listed_class(["a", "q3"], ["q3", "a"]), "unchanged")
        self.assertEqual(RD.listed_class(["a", "q3"], ["q3"]), "fewer flagged")
        self.assertEqual(RD.listed_class(["a"], ["a", "b"]), "more flagged")
        self.assertEqual(RD.listed_class(["a"], ["b"]), "different flagged")

    def test_the_held_out_reading(self):
        g = {"held-out": {"truths": 4, "cells_abs_z_gt_2": 0, "truths_p_lt_0.01": 0}}
        self.assertTrue(RD.held_out_met(g))
        for k, v in (("cells_abs_z_gt_2", 1), ("truths_p_lt_0.01", 1), ("truths", 3)):
            self.assertFalse(RD.held_out_met({"held-out": dict(g["held-out"], **{k: v})}), k)

    def test_the_wr_classes_and_their_boundaries(self):
        fl, sg = np.full(16, 0.001), np.full(16, 0.07)
        self.assertEqual(RD.wr_class(np.full(16, 0.002), fl, sg), ("W0", []))
        self.assertEqual(RD.wr_class(np.full(16, -0.002), fl, sg), ("W0", []))
        self.assertEqual(RD.wr_class(np.full(16, 0.0021), fl, sg), ("W1", []))
        d = np.full(16, 0.0021)
        d[6] = -0.035
        self.assertEqual(RD.wr_class(d, fl, sg), ("W1", []))
        d[6] = -0.0351
        self.assertEqual(RD.wr_class(d, fl, sg), ("W2", ["R06"]))

    def test_the_closure_classes(self):
        b0 = np.full(16, 0.01)
        self.assertEqual(RD.closure_class(b0 * 0.89, b0), "lower")
        self.assertEqual(RD.closure_class(b0 * 0.9, b0), "comparable")
        self.assertEqual(RD.closure_class(-b0 * 1.1, b0), "comparable")
        self.assertEqual(RD.closure_class(b0 * 1.11, b0), "higher")

    def test_the_rounding_floor_reproduces_the_printed_figures_and_refuses_otherwise(self):
        phi = RD.rounding_floor(self.I0, self.CMJ)
        self.assertEqual(phi.shape, (16,))
        bad = dict(self.I0, sigma_J_data=list(np.asarray(self.I0["sigma_J_data"]) * 1.01))
        with self.assertRaises(SystemExit):
            RD.rounding_floor(bad, self.CMJ)

    def test_the_deformed_truth_classes(self):
        g = lambda chi2, cells=(), p=False: {"chi2": chi2, "cells_abs_z_gt_2": list(cells), "p_lt_0.01": p}  # noqa: E731
        self.assertEqual(RD.deformed_class({"weighted": g(125.0), "equal_weights": g(100.0)}), "immaterial")
        self.assertEqual(RD.deformed_class({"weighted": g(75.0), "equal_weights": g(100.0)}), "immaterial")
        self.assertEqual(RD.deformed_class({"weighted": g(125.0001), "equal_weights": g(100.0)}), "material")
        self.assertEqual(RD.deformed_class({"weighted": g(74.999), "equal_weights": g(100.0)}), "material")
        self.assertEqual(RD.deformed_class({"weighted": g(100.0, p=True), "equal_weights": g(100.0)}), "material")
        self.assertEqual(RD.deformed_class({"weighted": g(100.0), "equal_weights": g(100.0, ("R02",))}), "material")

    def test_the_transfer_classes(self):
        fl, sg = np.full(16, 0.001), np.full(16, 0.07)
        self.assertEqual(RD.transfer_class([0.002] * 16, fl, sg), ("T0", []))
        self.assertEqual(RD.transfer_class([-0.0021] + [0.0] * 15, fl, sg), ("T1", []))
        self.assertEqual(RD.transfer_class([0.0] * 15 + [0.0351], fl, sg), ("T2", ["R15"]))
        self.assertEqual(RD.transfer_class([None] + [0.0] * 15, fl, sg), ("T2", ["R00"]))

    def inputs(self, sm=True, listed=("A7_gibuu", "q3"), held=0, delta=0.0, floor_bias=3e-5, chi2_w=100.0, tbias=0.0):
        sd0 = self.CMJ["sqrt_diag"]
        by = {"held-out": {"truths": 4, "cells": 64, "cells_abs_z_gt_2": held, "truths_p_lt_0.01": 0}}
        sig = np.full(16, 0.07)

        def arm(scale, lst):
            return {"records": [{"name": "q3", "grade": {"chi2": 30.0 * scale}}], "by_group": by, "listed": list(lst),
                    "reported_relative_sigma": (sig * scale).tolist()}

        rg = {"arms": {"nominal": arm(1.0, ("A7_gibuu", "q3")), "G6": arm(0.95, listed)}}
        share = {"genie_mec": 0.1, "nuwro": 0.2, "gibuu": 0.7}
        closures = {t: {"bias_weighted": [0.01] * 16, "bias_equal_weights": [0.01] * 16} for t in ("nuwro", "gibuu", "q3")}
        closures["tune_v1"] = {"bias_weighted": [floor_bias] * 16, "bias_equal_weights": [3e-5] * 16}
        tr = [{"iteration": k, "rel_bias": 0.001, "rel_rms": 0.1, "cell_bias": [tbias if k == 4 else 0.0] * 16,
               "acceptance_decile_rel_bias": [0.002] + [None] * 8 + [-0.001]} for k in range(5)]
        cm = {"arms": {"nominal": {"sqrt_diag": sd0, "trace": 1.0, "trace_share_by_vertex": dict(share, gibuu=0.89)},
                       "G6": {"sqrt_diag": (np.asarray(sd0) * 0.7).tolist(), "trace": 0.5, "trace_share_by_vertex": share}},
              "wr": {"delta": (np.full(16, delta)).tolist(), "closures": closures},
              "transfer": {pt: tr for pt in ("data", "gibuu", "q3")}}
        g = lambda chi2: {"chi2": chi2, "cells_abs_z_gt_2": [], "p_lt_0.01": False}  # noqa: E731
        rg["wr_directions"] = {"data": {"grade": g(3.0), "directions": {"top": []}}}
        for t in ("tune_v1", "nuwro", "gibuu", "q3"):
            rg["wr_directions"][t] = {"weighted": g(chi2_w if t == "gibuu" else 100.0), "equal_weights": g(100.0),
                                      "change": {"top": [{"rank": 0, "component": 1.0}]},
                                      "change_along_equal_weight_bias": -0.5}
        prep = {"sm": {"radius": 1 if sm else None, "status": "built" if sm else "not built: both radii failed"}}
        if sm:
            rg["arms"]["SM"] = arm(1.0, ("A7_gibuu", "q3"))
            cm["arms"]["SM"] = dict(cm["arms"]["nominal"])
        f1 = {RD.SIGMA_KEY: {"C_total": sig.tolist()}}
        return prep, cm, rg, self.I0, self.CMJ, f1

    def test_the_readout_applies_the_tables(self):
        out = RD.read(*self.inputs())
        g6, sm, wr, tr = out["arms"]["G6"], out["arms"]["SM"], out["arms"]["WR"], out["arms"]["TR"]
        self.assertEqual(g6["verdict"], "the fake-data conclusions survive G6")
        self.assertEqual(g6["P4"]["class"], "C_model smaller")
        self.assertAlmostEqual(g6["P4"]["trace_ratio"], 0.5)
        self.assertAlmostEqual(g6["P5"]["median"], 0.95)
        self.assertEqual(sm["P4"]["class"], "C_model similar")
        self.assertEqual(sm["radius"], 1)
        self.assertEqual(wr["P6"]["class"], "W0")
        self.assertFalse(wr["P7"]["floor"]["breaks_the_prior_closure"])
        self.assertEqual(wr["P7"]["nuwro"]["rms_class"], "comparable")
        self.assertEqual((wr["P7"]["gibuu"]["class"], wr["P7"]["q3"]["class"]), ("immaterial", "immaterial"))
        self.assertTrue(wr["verdict"].startswith("in pvl's noise-free signal-only closures, the equal-weight "
                                                 "regression is immaterial"))
        self.assertIn("T3's B0/MW", wr["scope"])
        self.assertIn("probe's own estimation noise", tr["scope"])
        self.assertEqual({k: v["class"] for k, v in tr["P8"].items()}, {"data": "T0", "gibuu": "T0", "q3": "T0"})
        self.assertEqual(tr["P8"]["q3"]["lowest_vs_highest_acceptance"], [0.002, -0.001])
        self.assertIn("not calibrated", out["label"])
        txt = RD.text(out)
        self.assertIn("survive G6", txt)
        self.assertIn("TR: P8", txt)
        out = RD.read(*self.inputs(held=1))
        self.assertEqual(out["arms"]["G6"]["P1"]["class"], "unchanged")
        self.assertEqual(out["arms"]["G6"]["verdict"], "a fake-data conclusion changes under G6")
        out = RD.read(*self.inputs(chi2_w=60.0))
        self.assertEqual(out["arms"]["WR"]["P7"]["gibuu"]["class"], "material")
        self.assertEqual(out["arms"]["WR"]["verdict"],
                         "in pvl's noise-free signal-only closures, the equal-weight regression is material: at gibuu")
        out = RD.read(*self.inputs(listed=("q3",), held=1, delta=0.05, floor_bias=2e-4, sm=False, tbias=0.05))
        g6 = out["arms"]["G6"]
        self.assertEqual(g6["P1"]["class"], "fewer flagged")
        self.assertFalse(g6["P3"]["both_criteria_met_at_the_four_held_out_records"])
        self.assertEqual(g6["verdict"], "a fake-data conclusion changes under G6")
        self.assertIn("not run", out["arms"]["SM"]["status"])
        self.assertEqual(out["arms"]["WR"]["P6"]["class"], "W2")
        self.assertIn("on data (W2", out["arms"]["WR"]["verdict"])
        self.assertEqual(len(out["arms"]["WR"]["P6"]["cells_at_half_sigma"]), 16)
        self.assertTrue(out["arms"]["WR"]["P7"]["floor"]["breaks_the_prior_closure"])
        self.assertEqual(out["arms"]["TR"]["P8"]["data"]["class"], "T2")

    def test_the_readout_refuses_a_nominal_that_is_not_the_committed_one(self):
        prep, cm, rg, i0, cmj, f1 = self.inputs()
        rg["arms"]["nominal"]["reported_relative_sigma"][0] *= 1 + 1e-9
        with self.assertRaises(SystemExit):
            RD.read(prep, cm, rg, i0, cmj, f1)
        prep, cm, rg, i0, cmj, f1 = self.inputs()
        cm["arms"]["nominal"]["sqrt_diag"] = [x * 1.001 for x in cm["arms"]["nominal"]["sqrt_diag"]]
        with self.assertRaises(SystemExit):
            RD.read(prep, cm, rg, i0, cmj, f1)


# ---------------------------------------------------------------- the launcher


class Launcher(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self.deploy, self.out, self.bin, self.pvl_prep = d / "deploy", d / "out", d / "bin", d / "pvlprep"
        for sub in ("nd-unfolding/rsn", "nd-unfolding/pv-ladder"):
            (self.deploy / sub).mkdir(parents=True)
        (self.deploy / "nd-unfolding/rsn/rsn_tasks.tsv").write_bytes((HERE / "rsn_tasks.tsv").read_bytes())
        (self.deploy / "nd-unfolding/pv-ladder/config.json").write_bytes((ND / "pv-ladder/config.json").read_bytes())
        rd = self.pvl_prep / "ratios" / "L-5D-PV"
        rd.mkdir(parents=True)
        lines = []
        for v in ("tune_v1", "nuwro"):
            (rd / f"{v}.json").write_text(json.dumps({"v": v}))
            lines.append(f"{L.sha256_path(rd / f'{v}.json')}  ./ratios/L-5D-PV/{v}.json\n")
        (self.deploy / "nd-unfolding/pv-ladder/prep-SHA256SUMS").write_text("".join(lines))
        self.out.mkdir()
        (self.out / "prep").mkdir()
        (self.out / "nc_r.json").write_text(json.dumps({"schema": "rsn-nc-r/1", "verdict": "PASS"}, indent=1))
        self.bin.mkdir()
        self.squeue("")
        self.commit()

    def tearDown(self):
        self.tmp.cleanup()

    def commit(self, sm=None):
        if sm is not None:
            lines = []
            for rel in ["G6/gibuu"] + ([f"SM/{v}" for v in ("genie_mec", "nuwro", "gibuu")] if sm else []):
                p = self.out / "prep" / f"{rel}.json"
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(json.dumps({"rel": rel}))
                lines.append(f"{L.sha256_path(p)}  ./{rel}.json\n")
            (self.deploy / "nd-unfolding/rsn/rsn-prep-SHA256SUMS").write_text("".join(lines))
        env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
               "GIT_COMMITTER_EMAIL": "t@t"}
        if not (self.deploy / ".git").exists():
            subprocess.run(["git", "-C", str(self.deploy), "init", "-q"], check=True, env=env, capture_output=True)
        for c in (["add", "-A"], ["commit", "-qm", "deploy", "--allow-empty"]):
            subprocess.run(["git", "-C", str(self.deploy), *c], check=True, env=env, capture_output=True)
        self.pin = subprocess.run(["git", "-C", str(self.deploy), "rev-parse", "HEAD"], capture_output=True,
                                  text=True, check=True).stdout.strip()

    def squeue(self, lines, rc=0):
        p = self.bin / "squeue"
        p.write_text(f"#!/bin/bash\nprintf '%s' '{lines}'\nexit {rc}\n")
        p.chmod(0o755)

    def gate(self, job, nc=True):
        (self.out / "gates").mkdir(exist_ok=True)
        (self.out / "gates" / f"{job}.ok").write_text(f"pin={self.pin}\n")
        if nc:
            (self.out / "nc.json").write_text(json.dumps({"verdict": "PASS"}, indent=1))

    def sh(self, job, pin=None, **env):
        e = {**os.environ, "RSN_SMOKE": "1", "RSN_PVL_PREP": str(self.pvl_prep),
             "PATH": f"{self.bin}:{os.environ['PATH']}", **env}
        e.pop("SLURM_JOB_ID", None)
        p = subprocess.run(["bash", str(HERE / "sbatch_rsn.sh"), str(self.deploy), pin or self.pin, str(self.out), job],
                           capture_output=True, text=True, env=e, timeout=120)
        return p.returncode, p.stdout, p.stderr

    def fence(self):
        (self.out / "fence.txt").write_text("ll5d_\nt3p_\n")

    def test_the_deploy_name_and_limit_checks(self):
        self.fence()
        rc, _, err = self.sh("J1", pin="0" * 40)
        self.assertEqual(rc, 2)
        self.assertIn("deploy HEAD", err)
        rc, _, err = self.sh("J4")
        self.assertIn("refusing: job J4", err)
        rc, _, err = self.sh("J1", RSN_NAME="rsn_J2")
        self.assertIn("job name rsn_J2 is not rsn_J1", err)
        rc, _, err = self.sh("J1", RSN_TIMELIMIT="19:01")
        self.assertIn("exceeds", err)
        rc, _, err = self.sh("J1", RSN_TIMELIMIT="abc")
        self.assertIn("could not read", err)
        for tl in ("19:00", "0:19:00", "0-0:19:00", "18"):
            rc, out, err = self.sh("J1", RSN_TIMELIMIT=tl)
            self.assertEqual(rc, 0, tl + err)
        for job, tl, over in (("J2", "22:00", False), ("J2n", "0:22:00", False), ("J2", "22:01", True),
                              ("J3", "19:00", False), ("J3", "19:01", True)):
            rc, _, err = self.sh(job, RSN_TIMELIMIT=tl)
            self.assertEqual("exceeds" in err, over, job + tl + err)
        (self.deploy / "nd-unfolding" / "stray.py").write_text("")
        rc, _, err = self.sh("J1")
        self.assertIn("1 untracked", err)

    def test_the_fence_fails_closed_and_matches_at_the_start_only(self):
        rc, _, err = self.sh("J1")
        self.assertEqual(rc, 2)
        self.assertIn("naming the fenced job-name prefixes", err)
        self.fence()
        self.squeue("ll5d_bulk_03|RUNNING")
        rc, _, err = self.sh("J1")
        self.assertIn("fenced jobs (ll5d_*)", err)
        self.squeue("", rc=1)
        rc, _, err = self.sh("J1")
        self.assertIn("squeue failed", err)
        self.squeue("my_ll5d_x|RUNNING")
        rc, _, err = self.sh("J1")
        self.assertEqual(rc, 0, err)

    def test_every_job_waits_on_the_nc_r_pass(self):
        self.fence()
        (self.out / "nc_r.json").unlink()
        for job in ("J1", "J2", "J3"):
            rc, _, err = self.sh(job)
            self.assertEqual(rc, 2, job)
            self.assertIn("no NC-R PASS", err, job)
        (self.out / "nc_r.json").write_text(json.dumps({"schema": "rsn-nc/1", "verdict": "PASS"}, indent=1))
        rc, _, err = self.sh("J1")
        self.assertIn("no NC-R PASS", err)

    def test_j1_is_the_nc_alone(self):
        self.fence()
        rc, out, err = self.sh("J1")
        self.assertEqual(rc, 0, err)
        steps = [ln for ln in out.splitlines() if ln.startswith("STEP ")]
        self.assertEqual(len(steps), 1)
        s = steps[0]
        self.assertTrue(s.startswith("STEP rsn_nc "))
        self.assertIn("--regressor-weight none", s)
        self.assertIn(str(self.pvl_prep / "ratios/L-5D-PV/tune_v1.json"), s)
        self.assertNotIn("--closure", s)
        for want in ("--estimator-seed 42", "--threads 32", "--iters 5", "--features all", "--arm e", "--rung L-5D-PV"):
            self.assertIn(want, s)

    def test_j2_needs_its_gate_the_nc_pass_and_the_committed_reweights(self):
        self.fence()
        rc, _, err = self.sh("J2")
        self.assertIn("gates/J2.ok is missing", err)
        self.gate("J2", nc=False)
        rc, _, err = self.sh("J2")
        self.assertIn("records no NC PASS", err)
        self.gate("J2")
        rc, _, err = self.sh("J2")
        self.assertIn("no committed", err)
        self.commit(sm=False)
        self.gate("J2")
        rc, _, err = self.sh("J2")
        self.assertIn("use J2n", err)
        self.gate("J2n")
        rc, out, err = self.sh("J2n")
        self.assertEqual(rc, 0, err)
        self.assertEqual(len([s for s in out.splitlines() if s.startswith("STEP ")]), 5)
        self.commit(sm=True)
        self.gate("J2")
        self.gate("J2n")
        rc, _, err = self.sh("J2n")
        self.assertIn("only for a prep that built no SM", err)

    def test_j2_runs_the_eight_declared_steps(self):
        self.fence()
        self.commit(sm=True)
        self.gate("J2")
        rc, out, err = self.sh("J2")
        self.assertEqual(rc, 0, err)
        steps = {ln.split()[1]: ln for ln in out.splitlines() if ln.startswith("STEP ")}
        self.assertEqual(list(steps), ["G6_gibuu", "SM_genie_mec", "SM_nuwro", "SM_gibuu", "WR_data",
                                       "WR_closure_tune_v1", "WR_closure_nuwro", "TR_data"])
        for t, s in steps.items():
            self.assertIn("--regressor-weight " + ("w_push_w_truth" if t.startswith("WR") else "none"), s, t)
            self.assertEqual("--closure" in s.split(), "closure" in t, t)
            self.assertEqual("--transfer" in s.split(), t == "TR_data", t)
            self.assertIn("--truth ratio", s, t)
        self.assertIn(str(self.out / "prep/G6/gibuu.json"), steps["G6_gibuu"])
        self.assertIn(str(self.out / "prep/SM/nuwro.json"), steps["SM_nuwro"])
        self.assertIn(str(self.pvl_prep / "ratios/L-5D-PV/nuwro.json"), steps["WR_closure_nuwro"])
        self.assertIn(str(self.pvl_prep / "ratios/L-5D-PV/tune_v1.json"), steps["WR_closure_tune_v1"])

    def test_j3_runs_the_four_f1_closures_after_the_nc(self):
        self.fence()
        rc, _, err = self.sh("J3")
        self.assertIn("gates/J3.ok is missing", err)
        self.gate("J3", nc=False)
        rc, _, err = self.sh("J3")
        self.assertIn("records no NC PASS", err)
        self.gate("J3")
        rc, out, err = self.sh("J3")
        self.assertEqual(rc, 0, err)
        steps = {ln.split()[1]: ln for ln in out.splitlines() if ln.startswith("STEP ")}
        self.assertEqual(list(steps), ["WR_closure_gibuu", "WR_closure_q3", "WU_closure_gibuu", "WU_closure_q3"])
        for t, s in steps.items():
            w = s.split()
            self.assertIn("--closure", w)
            self.assertEqual(w[w.index("--truth") + 1], "a7_gibuu" if t.endswith("gibuu") else "q3", t)
            self.assertEqual(w[w.index("--regressor-weight") + 1], "w_push_w_truth" if t.startswith("WR") else "none")
            self.assertEqual("--transfer" in w, t.startswith("WU"), t)
            self.assertIn(str(self.pvl_prep / "ratios/L-5D-PV/tune_v1.json"), s)

    def test_a_changed_reweight_or_an_existing_product_refuses(self):
        self.fence()
        self.commit(sm=True)
        self.gate("J2")
        (self.out / "prep/SM/gibuu.json").write_text("{}")
        rc, _, err = self.sh("J2")
        self.assertEqual(rc, 2)
        self.assertIn("SM_gibuu", err)
        (self.pvl_prep / "ratios/L-5D-PV/tune_v1.json").write_text("{}")
        rc, _, err = self.sh("J1")
        self.assertIn("rsn_nc", err)
        (self.pvl_prep / "ratios/L-5D-PV/tune_v1.json").write_text(json.dumps({"v": "tune_v1"}))
        (self.out / "products").mkdir()
        (self.out / "products/rsn_nc.npz").write_text("")
        rc, _, err = self.sh("J1")
        self.assertIn("rsn_nc.npz exists", err)


if __name__ == "__main__":
    unittest.main()
