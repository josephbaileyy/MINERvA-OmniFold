"""Synthetic controls for R10: each piece fires on its defect and is silent on the correct input.

Run from the repository root: ``python3 -m pytest -q docs/orchestration/state/measurement-scoping/r10/test_r10.py``.
No real input is read. D-ID's driver is loaded through ``r10.load_did`` (its digest checks run) for the
information-content tests, which use only its ``fisher``, ``widths_from_eig`` and ``ibu`` primitives.
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

import numpy as np
from scipy import sparse

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r10  # noqa: E402
import r10_extract as rx  # noqa: E402

CFG = json.loads((HERE / "config.json").read_text())
RULE = CFG["rule"]


class Binning(unittest.TestCase):
    def test_refinement_is_repeated_midpoint_halving(self):
        e = [np.array([0.0, 1.0, 3.0]), np.array([2.0, 5.0])]
        self.assertTrue(all(np.array_equal(a, b) for a, b in zip(r10.refined(e, 1), e)))
        self.assertEqual(r10.refined(e, 2)[0].tolist(), [0.0, 0.5, 1.0, 2.0, 3.0])
        self.assertEqual(r10.refined(e, 4)[0].tolist(), [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 2.5, 3.0])
        self.assertEqual(len(r10.refined(e, 4)[1]) - 1, 4)
        with self.assertRaises(ValueError):
            r10.refined(e, 3)

    def test_tertiles_are_weighted_and_keep_ties_together(self):
        v = np.array([1.0, 1.0, 1.0, 2.0, 3.0, 4.0, np.nan])
        w = np.ones(7)
        use = np.ones(7, bool)
        b, info = r10.tertile_bins(v, w, use)
        self.assertEqual(b[-1], 3)  # missing
        self.assertTrue(np.all(b[:3] == b[0]))  # ties never split
        self.assertEqual(info["n_missing_used"], 1)
        # weight moves the tertiles: all weight on the last value puts every other value in bin 0
        b2, _ = r10.tertile_bins(np.array([1.0, 2.0, 3.0]), np.array([0.01, 0.01, 100.0]), np.ones(3, bool))
        self.assertEqual(b2.tolist(), [0, 0, 0])

    def test_twin_permutes_labels_within_each_group_and_keeps_occupancy(self):
        rng = np.random.default_rng(1)
        group = rng.integers(-1, 50, 20000)
        label = np.where(group >= 0, group * 8 + rng.integers(0, 8, group.size), -1)
        twin = r10.permuted_within(group, label, [7, 1])
        self.assertTrue(np.all(twin[group < 0] == -1))
        for g in range(50):  # every group keeps exactly its multiset of labels
            m = group == g
            self.assertEqual(sorted(label[m].tolist()), sorted(twin[m].tolist()))
        self.assertTrue(np.array_equal(np.bincount(label[label >= 0]), np.bincount(twin[twin >= 0])))  # occupancy
        self.assertGreater(np.mean(twin[group >= 0] != label[group >= 0]), 0.5)  # actually shuffled
        self.assertTrue(np.array_equal(twin, r10.permuted_within(group, label, [7, 1])))  # seeded

    def test_twin_destroys_a_label_correlated_with_a_row_property(self):
        rng = np.random.default_rng(2)
        group = np.zeros(40000, np.int64)
        prop = rng.random(group.size)
        label = (prop > 0.5).astype(np.int64)  # the label is the property
        twin = r10.permuted_within(group, label, [7, 2])
        self.assertLess(abs(np.corrcoef(prop, twin)[0, 1]), 0.03)

    def test_derived_variables(self):
        raw = {k: np.array([2.0, -999.0, 0.0]) for k in CFG["extract"]["branches"]}
        c2 = r10.derived_variable("C2", raw)
        self.assertAlmostEqual(c2[0], 1 / 3)
        self.assertTrue(np.isnan(c2[1]) and np.isnan(c2[2]))  # a sentinel; an empty denominator
        self.assertEqual(r10.derived_variable("C1", raw)[0], 6.0)
        self.assertTrue(np.isnan(r10.derived_variable("C3", raw)[1]))
        with self.assertRaises(ValueError):
            r10.derived_variable("C5", raw)


class Statistics(unittest.TestCase):
    def test_quantile_inf_matches_numpy_and_carries_inf(self):
        v = np.random.default_rng(2).random(101)
        self.assertEqual(r10.quantile_inf(v, 0.9), float(np.quantile(v, 0.9)))
        self.assertEqual(r10.quantile_inf(np.array([1.0, 2.0, np.inf]), 0.9), np.inf)
        self.assertEqual(r10.quantile_inf(np.array([1.0, 2.0, 3.0, np.inf]), 0.5), 2.5)

    def test_width_stats_counts_holes_as_inf(self):
        s = r10.width_stats(np.array([0.05, np.nan, 0.2, np.inf]))
        self.assertEqual(s["n_inf"], 2)
        self.assertEqual(s["median"], np.inf)
        self.assertEqual(s["median_finite"], 0.125)
        self.assertEqual(s["n_le_10pct"], 1)


def cfgs(width_x, resid_x, width_t, resid_t, base_w=0.29, base_r=0.08):
    mk = lambda m, p90: {"median": m, "p90": p90}  # noqa: E731
    base = {d: base_r for d in r10.DEPARTURES}
    return {"f1": {"width": mk(base_w, 1.1), "resid": base, "twin": None, "decisive": False},
            "X": {"width": width_x, "resid": resid_x, "twin": "X~null", "decisive": True},
            "X~null": {"width": width_t, "resid": resid_t, "twin": None, "decisive": False}}


NULL_OK = {"pass": True}


class Rule(unittest.TestCase):
    good_r = {"gibuu": 0.04, "w1": 0.05, "w2": 0.05, "w3": 0.01}  # 3 of 4 below (2/3) x 0.08
    null_r = {d: 0.08 for d in r10.DEPARTURES}
    silent = {"median": 0.28, "p90": 1.0}

    def v(self, wx, rx, wt, rt, null=NULL_OK):
        return r10.verdict(cfgs(wx, rx, wt, rt), RULE, null)

    def test_pass_on_the_floor_with_a_silent_twin_and_margins_reported(self):
        v = self.v({"median": 0.09, "p90": 0.24}, self.good_r, self.silent, self.null_r)
        self.assertEqual((v["verdict"], v["passing"], v["n_decisive"]), ("PASS", ["X"], 1))
        m = v["per_config"]["X"]["margin"]
        self.assertAlmostEqual(m["width_median_x_over_twin"], 0.09 / 0.28)
        self.assertAlmostEqual(m["resid_x_over_twin"]["gibuu"], 0.5)

    def test_pass_by_halving(self):
        self.assertEqual(self.v({"median": 0.14, "p90": 0.6}, self.good_r, self.silent, self.null_r)["verdict"], "PASS")

    def test_width_alone_is_a_determinate_fail_and_stops(self):
        v = self.v({"median": 0.09, "p90": 0.2}, self.null_r, self.silent, self.null_r)
        self.assertEqual((v["per_config"]["X"]["state"], v["verdict"]), ("FAIL", "STOP"))

    def test_two_departures_are_not_enough(self):
        r = {"gibuu": 0.04, "w1": 0.05, "w2": 0.07, "w3": 0.08}
        v = self.v({"median": 0.09, "p90": 0.2}, r, self.silent, self.null_r)
        self.assertEqual((v["per_config"]["X"]["leg_b_departures"], v["verdict"]), (2, "STOP"))

    def test_a_twin_on_leg_a_makes_x_undetermined_and_r10_incomplete(self):
        v = self.v({"median": 0.09, "p90": 0.2}, self.good_r, {"median": 0.10, "p90": 0.25}, self.null_r)
        self.assertEqual((v["per_config"]["X"]["state"], v["verdict"]), ("UNDETERMINED", "INCOMPLETE"))

    def test_a_twin_on_leg_b_makes_x_undetermined_and_r10_incomplete(self):
        v = self.v({"median": 0.09, "p90": 0.2}, self.good_r, self.silent, self.good_r)
        self.assertEqual((v["per_config"]["X"]["state"], v["verdict"]), ("UNDETERMINED", "INCOMPLETE"))

    def test_x_must_beat_its_twin_on_the_residual(self):
        twin = {"gibuu": 0.03, "w1": 0.06, "w2": 0.04, "w3": 0.08}  # twin passes only 2 departures, but beats X at 2
        v = self.v({"median": 0.09, "p90": 0.2}, self.good_r, self.silent, twin)
        self.assertEqual(v["per_config"]["X"]["beats_twin_residual_departures"], 2)
        self.assertEqual(v["verdict"], "STOP")

    def test_a_failed_global_null_is_incomplete_even_with_a_pass(self):
        v = self.v({"median": 0.09, "p90": 0.24}, self.good_r, self.silent, self.null_r, null={"pass": False})
        self.assertEqual(v["verdict"], "INCOMPLETE")

    def test_one_pass_among_undetermined_is_still_a_pass(self):
        c = cfgs({"median": 0.09, "p90": 0.24}, self.good_r, self.silent, self.null_r)
        c["Y"] = {"width": {"median": 0.09, "p90": 0.2}, "resid": self.good_r, "twin": "Y~null", "decisive": True}
        c["Y~null"] = {"width": {"median": 0.05, "p90": 0.1}, "resid": self.null_r, "twin": None, "decisive": False}
        v = r10.verdict(c, RULE, NULL_OK)
        self.assertEqual((v["verdict"], v["passing"], v["undetermined"]), ("PASS", ["X"], ["Y"]))

    def test_cut_is_one_third_either_side_of_the_boundary(self):
        base = {d: 0.08 for d in r10.DEPARTURES}
        inside = {d: 0.08 * (2 / 3) * 0.999 for d in r10.DEPARTURES}
        outside = {d: 0.08 * (2 / 3) * 1.001 for d in r10.DEPARTURES}
        self.assertEqual(r10.leg_b(inside, base, RULE), 4)
        self.assertEqual(r10.leg_b(outside, base, RULE), 0)

    def test_global_null_band(self):
        f1 = {"width": {"median": 0.30}, "resid": {d: 0.08 for d in r10.DEPARTURES}}
        swap = {"width": {"median": 0.31}, "resid": {d: 0.081 for d in r10.DEPARTURES}}
        near = {"width": {"median": 0.315}, "resid": {d: 0.0805 for d in r10.DEPARTURES}}
        far = {"width": {"median": 0.40}, "resid": {d: 0.0805 for d in r10.DEPARTURES}}
        self.assertTrue(r10.global_null(f1, swap, near, RULE)["pass"])
        self.assertFalse(r10.global_null(f1, swap, far, RULE)["pass"])
        # a zero split-swap difference still leaves the 1% relative band
        self.assertTrue(r10.global_null(f1, f1, {"width": {"median": 0.302}, "resid": f1["resid"]}, RULE)["pass"])

    def test_ratio_guards_zero(self):
        self.assertEqual(r10.ratio(1.0, 0.0), float("inf"))
        self.assertTrue(np.isnan(r10.ratio(0.0, 0.0)))


class Information(unittest.TestCase):
    """The null twin's premise: an exact proportional split of reco cells adds no Fisher information and leaves IBU
    unchanged; a split with sampling noise adds spurious information (so a real variable must beat its twin)."""

    @classmethod
    def setUpClass(cls):
        cls.did = r10.load_did(CFG)
        rng = np.random.default_rng(3)
        cls.R = sparse.csr_matrix(rng.random((6, 4)) * (rng.random((6, 4)) > 0.3) + 0.01)
        cls.t = rng.random(4) * 100 + 10
        cls.b = rng.random(6)

    def split_exact(self, m):
        R = sparse.vstack([self.R / m] * m).tocsr()
        return R, np.tile(self.b / m, m)

    def test_exact_split_keeps_fisher_and_ibu(self):
        F0 = self.did.fisher(self.R, self.t, self.b)
        R3, b3 = self.split_exact(3)
        self.assertLess(np.max(np.abs(self.did.fisher(R3, self.t, b3) - F0)) / np.max(np.abs(F0)), 1e-12)
        y = self.R @ (self.t * 1.3) + self.b
        prior = np.full(4, self.t.mean())
        a = self.did.ibu(self.R, y, self.b, prior, 5).final
        c = self.did.ibu(R3, np.tile(y / 3, 3), b3, prior, 5).final
        self.assertLess(np.max(np.abs(a - c) / a), 1e-12)

    def test_noisy_split_inflates_fisher(self):
        """Each response element split into 3 random parts that sum to it exactly (no known term): the split's Fisher
        is at least the unsplit one's (Cauchy-Schwarz per reco row), strictly when the parts are unequal."""
        rng = np.random.default_rng(4)
        R = self.R.toarray()
        a = rng.dirichlet(np.ones(3), size=R.shape)  # (reco, truth, part), each element's parts sum to 1
        R3 = sparse.csr_matrix(np.vstack([R * a[:, :, k] for k in range(3)]))
        zero = np.zeros(6)
        F0 = self.did.fisher(self.R, self.t, zero)
        F3 = self.did.fisher(R3, self.t, np.zeros(18))
        self.assertTrue(np.allclose(np.asarray(R3.toarray()).reshape(3, 6, 4).sum(0), R))
        self.assertGreater(np.min(np.linalg.eigvalsh(F3 - F0)), -1e-9 * np.max(np.abs(F0)))
        self.assertGreater(np.trace(F3), np.trace(F0) * (1 + 1e-6))


class Join(unittest.TestCase):
    def setUp(self):
        self.key = np.array([10, 11, 12, 13, 14], np.uint64)
        self.fidx = np.array([0, 0, 1, 1, 1])
        self.vtx = np.arange(15, dtype=float).reshape(5, 3)
        self.tree = {0: {"key": np.array([11, 10], np.uint64), "vtx": self.vtx[[1, 0]], "B": np.array([1.0, 0.0]), "n": 2},
                     1: {"key": np.array([14, 12, 13], np.uint64), "vtx": self.vtx[[4, 2, 3]], "B": np.array([4.0, 2.0, 3.0]), "n": 3}}

    def test_joins_by_identity_within_file(self):
        out, ctl = rx.join_rows(5, np.arange(5), self.key, self.fidx, self.vtx, self.tree, ["B"], 1e-6)
        self.assertTrue(ctl["pass"])
        self.assertEqual(out["B"].tolist(), [0.0, 1.0, 2.0, 3.0, 4.0])

    def test_missing_entry_fails(self):
        t = dict(self.tree)
        t[1] = {k: (v[:2] if k != "n" else 2) for k, v in t[1].items()}
        _, ctl = rx.join_rows(5, np.arange(5), self.key, self.fidx, self.vtx, t, ["B"], 1e-6)
        self.assertFalse(ctl["pass"])
        self.assertEqual(ctl["rows_joined"], 4)

    def test_vertex_mismatch_fails(self):
        v = self.vtx.copy()
        v[3, 2] += 0.01
        _, ctl = rx.join_rows(5, np.arange(5), self.key, self.fidx, v, self.tree, ["B"], 1e-6)
        self.assertFalse(ctl["pass"])

    def test_duplicate_key_resolved_by_the_vertex(self):
        """The 1E case: two entries share an identity but are different events; the G2 vertex picks one."""
        t = dict(self.tree)
        far = self.vtx[0] + 1665.0
        t[0] = {"key": np.array([11, 10, 10], np.uint64), "vtx": np.vstack([self.vtx[1], far, self.vtx[0]]),
                "B": np.array([1.0, 9.0, 0.0]), "n": 3}
        out, ctl = rx.join_rows(5, np.arange(5), self.key, self.fidx, self.vtx, t, ["B"], 1e-6)
        self.assertEqual((ctl["joined_rows_with_a_duplicated_key"], ctl["duplicated_rows_unresolved_by_vertex"]), (1, 0))
        self.assertTrue(ctl["pass"])
        self.assertEqual(out["B"][0], 0.0)  # the entry with the row's vertex, not the first in tree order

    def test_duplicate_key_with_no_or_two_vertex_matches_fails(self):
        for vt in (np.vstack([self.vtx[1], self.vtx[0] + 5, self.vtx[0] + 9]),   # none matches
                   np.vstack([self.vtx[1], self.vtx[0], self.vtx[0]])):           # both match
            t = dict(self.tree)
            t[0] = {"key": np.array([11, 10, 10], np.uint64), "vtx": vt, "B": np.array([1.0, 0.0, 9.0]), "n": 3}
            _, ctl = rx.join_rows(5, np.arange(5), self.key, self.fidx, self.vtx, t, ["B"], 1e-6)
            self.assertEqual(ctl["duplicated_rows_unresolved_by_vertex"], 1)
            self.assertFalse(ctl["pass"])

    def test_a_duplicate_key_no_row_needs_does_not_fail(self):
        t = dict(self.tree)
        t[0] = {"key": np.array([11, 10, 99, 99], np.uint64), "vtx": self.vtx[[1, 0, 0, 0]],
                "B": np.array([1.0, 0.0, 9.0, 9.0]), "n": 4}
        _, ctl = rx.join_rows(5, np.arange(5), self.key, self.fidx, self.vtx, t, ["B"], 1e-6)
        self.assertEqual((ctl["duplicate_keys_within_file_all"], ctl["pass"]), (1, True))

    def test_wrong_file_is_not_joined(self):
        f = self.fidx.copy()
        f[0] = 1  # row 0's identity exists only in file 0
        _, ctl = rx.join_rows(5, np.arange(5), self.key, f, self.vtx, self.tree, ["B"], 1e-6)
        self.assertFalse(ctl["pass"])


class EndToEnd(unittest.TestCase):
    """The whole driver on D-ID's synthetic world (real 5D grid, real functional rows, real reweight code) with
    synthetic tuple variables. K1 runs against D-ID tables and summaries written by D-ID's machinery on the same world
    in the committed 183-entry layout."""

    @classmethod
    def setUpClass(cls):
        import importlib.util
        import os
        import tempfile
        spec = importlib.util.spec_from_file_location(
            "r10_test_did", r10.REPO / "docs/orchestration/state/next-preparation-20261009/d-id/test_did.py")
        T = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(T)
        cls.T = T
        cls.root = root = Path(tempfile.mkdtemp())
        n = 30000
        world = T._world(root, n=n)
        dcfg = T._config(root, world)
        dcfg["weight_sets"] = [w for w in dcfg["weight_sets"] if w["name"] in CFG["weight_sets"]]
        d = T.did.Diagnostic(dcfg, root, root / "probe", T.did.Budget(10.0), T.cmp, T.com)
        d.load_events()
        d.build_rows()
        sig = d.pr & (d.rf_fine >= 0)
        dcfg["events"]["pair_rows_expected"] = d.out["events"]["rows_eligible_s5e_rule"]
        y = np.bincount(d.rf_fine[sig], weights=d.wr[sig], minlength=d.n_fine)
        dcfg["reco_cells_expected"] = int(np.sum(y > 0))
        cls.dcfg = dcfg
        # D-ID's committed-table layout, produced by D-ID's machinery on this world (K1's reference)
        p = T.did.Diagnostic(dcfg, root, root / "probe2", T.did.Budget(10.0), T.cmp, T.com)
        p.load_events()
        p.build_rows()
        p.histograms()
        p.grids()
        f183 = np.asarray(p.f183)
        tab, summ = {}, {}
        for grid in ("T1", "T2"):
            tab[f"{grid}/nominal/widths_nom/sigma_rel"] = p.widths(grid, "nominal", "nom")["sigma_rel"][f183]
        J = p.reported_positions("J")
        for ws in CFG["weight_sets"]:
            tr = p.run_trajectory("T2", ws, "same", "nom", keep_all=True)
            tab[f"traj/T2/same/nom/{ws}/K"] = np.asarray(tr["K"])
            tab[f"traj/T2/same/nom/{ws}/r"] = tr["r"][:, f183].astype(np.float64)
            summ[ws] = {"J": {"r_ibu_T2_nom_K5": {"median": r10.resid_stats(tr["r"][tr["K"].index(5)][J])["median"]}}}
        np.savez(root / "tables.npz", **tab)
        (root / "results.json").write_text(json.dumps({"summaries": summ}))
        cls.tab = tab
        rng = np.random.default_rng(5)
        extra = {b: rng.integers(0, 6, n).astype(float) for b in CFG["extract"]["branches"]}
        extra["MasterAnaDev_BlobNClusters_sz"][:50] = -999.0  # a sentinel
        extra["E_nu_MeV"] = rng.uniform(1e3, 4e4, n)
        np.savez(root / "extra.npz", **extra)
        cls.env = {v: os.environ.get(v) for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS")}
        os.environ.update({v: "2" for v in cls.env})
        cls.res = cls.go("clean")

    @classmethod
    def tearDownClass(cls):
        import os
        for v, x in cls.env.items():
            os.environ.pop(v, None) if x is None else os.environ.__setitem__(v, x)

    @classmethod
    def go(cls, out, tables=None, patch=None):
        run = r10.R10(json.loads(json.dumps(CFG)), cls.root, cls.root / "extra.npz", cls.root / out, did_cfg=cls.dcfg,
                      did_tables=tables or cls.root / "tables.npz", did_results=cls.root / "results.json")
        if patch:
            patch(run)
        rc = run.go()
        return rc, json.loads((cls.root / out / "r10_results.json").read_text())

    def test_clean_run_passes_every_control_and_records_everything(self):
        rc, res = self.res
        self.assertEqual((rc, res["status"]), (0, "complete"))
        for k in ("K0_rows", "K1_did_reproduced", "K2_generic_equals_did_at_f1"):
            self.assertTrue(res["controls"][k]["pass"], k)
        self.assertEqual(sorted(res["configs"]), sorted(CFG["order"]))
        self.assertIn(res["verdict"]["verdict"], ("PASS", "STOP", "INCOMPLETE"))
        self.assertEqual(res["verdict"]["n_decisive"], 11)
        self.assertIn("per_quantity", res["verdict"]["global_null"])
        for name, c in res["configs"].items():
            self.assertIn("enu_lt20_descriptive", c)
            if c["decisive"]:  # the permutation twin has exactly X's occupancy
                self.assertEqual(c["n_reco_cells"], res["configs"][c["twin"]]["n_reco_cells"], name)
                self.assertIn("margin", res["verdict"]["per_config"][name])
        self.assertIn("swap", res["configs"]["f1"]["roles"])
        self.assertGreaterEqual(res["configs"]["f2"]["n_reco_cells"], res["configs"]["f1"]["n_reco_cells"])

    def test_k1_fires_on_one_changed_table_entry(self):
        tab = dict(self.tab)
        r = tab["traj/T2/same/nom/gibuu/r"].copy()
        r[4, 0] = np.nextafter(r[4, 0], np.inf)  # one ulp, one functional, K = 5
        tab["traj/T2/same/nom/gibuu/r"] = r
        np.savez(self.root / "tables_bad.npz", **tab)
        rc, res = self.go("k1bad", tables=self.root / "tables_bad.npz")
        self.assertEqual((rc, res["status"]), (4, "INCOMPLETE"))
        self.assertIn("K1", res["exception"]["message"])
        self.assertNotIn("verdict", res)

    def test_k2_fires_on_a_wrong_prior_in_the_generic_path(self):
        def patch(run):
            orig = run.problem

            def wrong(H, grid, ws, role):
                pb = orig(H, grid, ws, role)
                if role == "same":
                    pb["prior"] = run.did.coarse_sum(run.run.G[grid], H["h"][ws]["u"])  # the departure's truth
                return pb
            run.problem = wrong
        rc, res = self.go("k2bad", patch=patch)
        self.assertEqual((rc, res["status"]), (4, "INCOMPLETE"))
        self.assertIn("K2", res["exception"]["message"])

    def make(self):
        return r10.R10(json.loads(json.dumps(CFG)), self.root, self.root / "extra.npz", self.root / "unused",
                       did_cfg=self.dcfg, did_tables=self.root / "tables.npz", did_results=self.root / "results.json")

    def test_swap_equals_split_with_the_halves_exchanged(self):
        """The noise band's swap role is the split role with the half mask negated, bitwise."""
        run = self.make()
        run._build_did()
        cell = run.rf[1]
        everyone = np.ones(cell.size, bool)  # forces the truth histograms from the rows, under the current mask
        H = run.hist(cell, everyone, ["nominal", "gibuu"], swap=True)
        sw = {ws: run.residuals(run.problem(H, "T2", ws, "swap"))[5] for ws in ("nominal", "gibuu")}
        w_sw = run.widths(run.problem(H, "T2", "nominal", "swap"))
        run.rows["is_b"] = ~run.rows["is_b"]
        H2 = run.hist(cell, everyone, ["nominal", "gibuu"], swap=False)
        for ws in ("nominal", "gibuu"):
            self.assertTrue(np.array_equal(sw[ws], run.residuals(run.problem(H2, "T2", ws, "split"))[5], equal_nan=True))
        self.assertTrue(np.array_equal(w_sw, run.widths(run.problem(H2, "T2", "nominal", "split")), equal_nan=True))

    def test_controls_only_records_controls_and_no_readout(self):
        run = r10.R10(json.loads(json.dumps(CFG)), self.root, None, self.root / "ctl", did_cfg=self.dcfg,
                      did_tables=self.root / "tables.npz", did_results=self.root / "results.json")
        self.assertEqual(run.controls_only(), 0)
        res = json.loads((self.root / "ctl" / "r10_results.json").read_text())
        self.assertEqual(res["status"], "controls-only: pass")
        self.assertNotIn("configs", res)
        self.assertNotIn("verdict", res)
        self.assertFalse((self.root / "ctl" / "r10_tables.npz").exists())
        for k in ("K0_rows", "K1_did_reproduced", "K2_generic_equals_did_at_f1"):
            self.assertTrue(res["controls"][k]["pass"], k)

    def test_extraction_receipt_check(self):
        extra = self.root / "extra.npz"
        code = HERE / "r10_extract.py"
        good = {"exit": 0, "rows": {"complete": True},
                "playlists": {p: {"pass": True} for p in CFG["extract"]["playlists"]},
                "code": {"r10_extract.py": r10.sha256(code)},
                "inputs": {CFG["extract"]["inputs"]["of_inputs"]: {"sha256": CFG["extract"]["of_inputs_sha256"]}},
                "output": {"sha256": r10.sha256(extra)}}
        self.assertEqual(r10.check_extract_receipt(good, extra, CFG, code), [])
        for mutate in (lambda r: r.update(exit=7), lambda r: r["rows"].update(complete=None),
                       lambda r: r["playlists"].pop("1L"), lambda r: r["playlists"]["1A"].update({"pass": False}),
                       lambda r: r["code"].update({"r10_extract.py": "0" * 64}),
                       lambda r: r["output"].update(sha256="0" * 64),
                       lambda r: r["inputs"][CFG["extract"]["inputs"]["of_inputs"]].update(sha256="0" * 64)):
            bad = json.loads(json.dumps(good))
            mutate(bad)
            self.assertTrue(r10.check_extract_receipt(bad, extra, CFG, code))


class Config(unittest.TestCase):
    def test_every_decisive_configuration_has_its_twin_in_order(self):
        order = CFG["order"]
        self.assertEqual(order[:2], ["f1", "null3@f1"])
        decisive = [n for n in order[2:] if not n.endswith("~null")]
        self.assertEqual(len(decisive), 11)
        for n in decisive:
            self.assertIn(f"{n}~null", order)
        self.assertEqual(len(order), 24)
        self.assertEqual(order[-2:], ["f4", "f4~null"])  # the heaviest last (memory)

    def test_rule_constants_are_the_declared_ones(self):
        self.assertEqual((RULE["width_median_max"], RULE["width_p90_max"], RULE["width_halving"]), (0.10, 0.25, 0.5))
        self.assertAlmostEqual(RULE["cut_keep_fraction"], 2 / 3)
        self.assertEqual(RULE["min_departures"], 3)
        self.assertEqual((RULE["null_band_k"], RULE["null_band_rel"]), (2.0, 0.01))


if __name__ == "__main__":
    unittest.main()
