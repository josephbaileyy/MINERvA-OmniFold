"""Controls for fd_xcov.py (FD-GENCMP-X-DECLARATION.md), on synthetic inputs. No real prediction, covariance or data
value is read; the only real file read is the H2 definition, for its geometry.

Every control is tested in the direction it acts and in the other: the joins (a subsequence, a non-subsequence, an
ambiguous row), the 2D data mask at each window edge, MC row identity (a differing row, a wrong sentinel count), the
draws against RE-2's and s5n_pseudo's own, the mapped replica, the cross blocks against each side's own rule, the bound
matrix's PSD joint, the chi2_4 survival function, the rule at each of its branches, route A's r*, and route B's
correlation."""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

ND = Path(__file__).resolve().parents[1]
sys.path.insert(1, str(ND))
import fd_gencmp as gc  # noqa: E402
import fd_xcov as X  # noqa: E402
import fd_xcov_steps as XS  # noqa: E402
import s1_assemble as sa  # noqa: E402
import s5n_pseudo  # noqa: E402

RNG = np.random.default_rng(20261102)


def spd(n, s=1.0):
    M = RNG.normal(size=(n, n))
    return (M @ M.T / n + np.eye(n)) * s


class Joins(unittest.TestCase):
    def setUp(self):
        self.big = RNG.uniform(0, 5, (500, 2)).astype(np.float32)
        self.keep = np.sort(RNG.choice(500, 470, replace=False))

    def test_a_subsequence_maps_back_to_its_rows(self):
        m, amb = X.subsequence_join(self.big, self.big[self.keep])
        self.assertTrue(np.array_equal(m, self.keep))
        self.assertEqual(amb, 0)

    def test_a_row_not_in_order_refuses(self):
        small = self.big[self.keep].copy()
        small[[10, 11]] = small[[11, 10]]
        with self.assertRaises(gc.Stop) as e:
            X.subsequence_join(self.big, small)
        self.assertIn("J", str(e.exception))

    def test_a_row_absent_from_2d_refuses(self):
        small = self.big[self.keep].copy()
        small[5, 0] = np.float32(99.0)
        with self.assertRaises(gc.Stop):
            X.subsequence_join(self.big, small)

    def test_an_ambiguous_row_is_counted(self):
        big = self.big.copy()
        big[101] = big[100]
        m, amb = X.subsequence_join(big, big[[100, 200]])
        self.assertEqual(m.tolist(), [100, 200])
        self.assertEqual(amb, 1)

    def test_float64_2d_values_match_their_float32_5d_copies(self):
        b64 = RNG.uniform(0, 5, (50, 2))
        m, _ = X.subsequence_join(b64.astype(np.float32), b64[::2].astype(np.float32))
        self.assertEqual(m.tolist(), list(range(0, 50, 2)))


class Mask(unittest.TestCase):
    def test_the_closed_window_and_each_rejection(self):
        pt = np.array([0.0, 4.5, 4.5000001, 1.0, 1.0, np.nan, 2e3, 1.0])
        pz = np.array([1.5, 60.0, 2.0, 1.4999999, 60.0000001, 2.0, 2.0, 2.0])
        ps = np.array([1, 1, 1, 1, 1, 1, 1, 0])
        self.assertEqual(X.mask_2d_data(pt, pz, ps).tolist(), [True, True, False, False, False, False, False, False])


class Rows(unittest.TestCase):
    def setUp(self):
        n = 3000
        self.mc = RNG.uniform(0, 5, (n, 5)).astype(np.float32)
        self.mc[:X.SENTINEL_ROWS, :] = -9999.0
        self.pt, self.pz = self.mc[:, 0].astype(float), self.mc[:, 1].astype(float)
        self.w2 = RNG.uniform(0.5, 2, n)

    def test_the_same_rows_pass_and_record_the_weight_scale(self):
        r = X.mc_positional(self.pt, self.pz, self.mc, self.w2, 3.0 * self.w2)
        self.assertTrue(r["pass"])
        self.assertAlmostEqual(r["weight_scale"], 3.0)

    def test_one_differing_row_refuses(self):
        pt = self.pt.copy()
        pt[-1] += 0.25
        self.assertFalse(X.mc_positional(pt, self.pz, self.mc)["pass"])

    def test_a_wrong_sentinel_count_refuses(self):
        mc = self.mc.copy()
        mc[0, :] = 1.0
        self.assertFalse(X.mc_positional(self.pt, self.pz, mc)["pass"])

    def test_a_different_row_count_refuses(self):
        self.assertFalse(X.mc_positional(self.pt[:-1], self.pz[:-1], self.mc)["pass"])


class Draws(unittest.TestCase):
    def exp(self, n_obs=40, n_mc=60, n_t=20):
        return {"obs_counts": np.ones(n_obs), "w_truth": RNG.uniform(0.5, 2, n_mc), "w_reco": RNG.uniform(0.5, 2, n_mc),
                "tmpl_w": RNG.uniform(0.5, 2, n_t), "obs": np.zeros((n_obs, 5))}

    def test_draws_are_re2s_streams(self):
        d, m, g = X.draws_2d(7, 50, 60, 30)
        self.assertTrue(np.array_equal(d, np.random.default_rng(7).poisson(1.0, size=50).astype(float)))
        self.assertTrue(np.array_equal(m, np.random.default_rng(7 + 10_000_000).poisson(1.0, size=60).astype(float)))
        self.assertTrue(np.array_equal(g, np.random.default_rng(7 + 20_000_000).poisson(1.0, size=30).astype(float)))

    def test_native_draws_reproduce_s5n_pseudo_bitwise(self):
        exp = self.exp()
        a, b = X.replica_external(exp, *X.native_draws(exp, 3)), s5n_pseudo.bootstrap_replica(exp, 3)
        for k in ("obs_counts", "w_truth", "w_reco", "tmpl_w"):
            self.assertTrue(np.array_equal(a[k], b[k]), k)

    def test_the_mapped_replica_carries_each_2d_draw_to_its_5d_row(self):
        exp = self.exp(40, 60, 20)
        j, entry = np.sort(RNG.choice(50, 40, replace=False)), np.sort(RNG.choice(30, 20, replace=False))
        rep = X.make_mapped_replica(j, entry, (50, 60, 30))(exp, 5)
        d, m, g = X.draws_2d(5, 50, 60, 30)
        self.assertTrue(np.array_equal(rep["obs_counts"], d[j]))
        self.assertTrue(np.array_equal(rep["w_truth"], exp["w_truth"] * m))
        self.assertTrue(np.array_equal(rep["tmpl_w"], exp["tmpl_w"] * g[entry]))

    def test_a_map_of_the_wrong_length_refuses(self):
        exp = self.exp(40, 60, 20)
        with self.assertRaises(gc.Stop):
            X.make_mapped_replica(np.arange(39), np.arange(20), (50, 60, 30))(exp, 1)

    def test_the_draw_check_prints_re2s_format(self):
        line = X.draw_sums_line(2, (50, 60, 30))
        d = np.random.default_rng(2).poisson(1.0, size=50).astype(float)
        self.assertEqual(line["data"], f"data factor sum={d.sum():.6g} (n=50")


class Algebra(unittest.TestCase):
    def test_cross_cov_is_each_sides_own_rule_on_the_diagonal(self):
        X16 = RNG.normal(size=(100, 4))
        w = RNG.uniform(0, 1, 100)
        self.assertTrue(np.allclose(X.cross_cov(X16, X16, w), sa.mat_cov(X16, w)))
        self.assertTrue(np.allclose(X.cross_cov(X16[:2], X16[:2]), sa.mat_cov(X16[:2])))

    def test_cross_cov_transposes_with_its_arguments(self):
        A, B = RNG.normal(size=(30, 4)), RNG.normal(size=(30, 4))
        self.assertTrue(np.allclose(X.cross_cov(A, B), X.cross_cov(B, A).T))
        with self.assertRaises(gc.Stop):
            X.cross_cov(A, B[:-1])

    def test_paired_universes_keep_the_joint_matrix_psd(self):
        X16, X2 = RNG.normal(size=(100, 4)), RNG.normal(size=(100, 4))
        J = X.cross_cov(np.hstack([X16, X2]), np.hstack([X16, X2]))
        self.assertTrue(np.allclose(J[:4, 4:], X.cross_cov(X16, X2)))
        self.assertGreaterEqual(np.linalg.eigvalsh(J).min(), -1e-12)

    def test_outer_pairs(self):
        v = [RNG.normal(size=4) for _ in range(3)]
        u = [RNG.normal(size=4) for _ in range(3)]
        self.assertTrue(np.allclose(X.outer_pairs(v, u), sum(np.outer(a, b) for a, b in zip(v, u))))
        with self.assertRaises(gc.Stop):
            X.outer_pairs(v, u[:2])

    def test_the_bound_matrix_keeps_the_joint_psd_at_every_r(self):
        S16, S2 = spd(4), spd(4, 3.0)
        M = X.bound_matrix(S16, S2)
        for r in (0.0, 0.5, 1.0):
            J = np.block([[S16, r * M], [r * M.T, S2]])
            self.assertGreaterEqual(np.linalg.eigvalsh(J).min(), -1e-10, r)

    def test_chi2_sf4(self):
        self.assertAlmostEqual(X.chi2_sf4(9.487729036781154), 0.05, places=10)
        self.assertAlmostEqual(X.chi2_sf4(0.0), 1.0)

    def test_quadrant_vectors_on_the_definition(self):
        e_pt, e_pz = (np.asarray(sa.s1.FINE[k], float) for k in ("pt", "pz"))
        ncell = (len(e_pt) - 1) * (len(e_pz) - 1)
        cells = np.arange(ncell)
        area = np.ones(ncell)
        import json
        A, B = X.quadrant_vectors(json.loads(gc.DEFINITION.read_text()), cells, area, e_pt, e_pz)
        self.assertEqual(A.sum(axis=1).tolist(), [4.0] * 4)
        self.assertTrue(np.all((B > 0).sum(axis=0) <= 1))       # no 2D bin in two quadrants


class Rule(unittest.TestCase):
    V = np.diag([1.0, 1.0, 1.0, 1.0])

    def test_agree(self):
        r = X.verdict(np.array([0.5, -0.5, 1.0, 0.2]), self.V)
        self.assertEqual((r["outcome"], r["named"]), ("agree", []))

    def test_a_quadrant_over_2_5_is_a_named_differ(self):
        r = X.verdict(np.array([0.1, 2.6, 0.0, 0.0]), self.V)
        self.assertEqual((r["outcome"], r["named"]), ("differ", ["QB"]))

    def test_exactly_2_5_is_not_over(self):
        self.assertEqual(X.verdict(np.array([2.5, 0.0, 0.0, 0.0]), self.V)["quadrants_over"], [])

    def test_a_joint_p_below_0_05_with_no_quadrant_over_is_a_joint_differ(self):
        r = X.verdict(np.array([2.2, 2.2, 0.0, 0.0]), self.V)          # chi2 9.68 > 9.488
        self.assertEqual((r["outcome"], r["named"]), ("differ", ["joint"]))
        self.assertLess(r["p"], 0.05)

    def test_a_non_positive_definite_vd_refuses(self):
        with self.assertRaises(gc.Stop):
            X.verdict(np.zeros(4), np.diag([1.0, 1.0, 1.0, 0.0]))

    def test_vd_subtracts_the_cross_term_twice(self):
        C16, C2, K = spd(4), spd(4), 0.1 * RNG.normal(size=(4, 4))
        self.assertTrue(np.allclose(X.Vd_of(C16, C2, K), C16 + C2 - K - K.T))

    def test_route_a_reports_r_star_where_the_reading_changes(self):
        C = np.eye(4)
        M = 0.9 * np.eye(4)
        d = np.array([0.0, 1.5, 0.0, 0.0])            # V_d = 2 - 1.8 r, so z = 1.5/sqrt(2 - 1.8 r) passes 2.5 at r = 0.9111
        r = X.route_a(d, C, C, np.zeros((4, 4)), M, grid=1001)
        self.assertEqual((r["r0"]["outcome"], r["r1"]["outcome"]), ("agree", "differ"))
        self.assertAlmostEqual(r["r_star"], (2 - 0.36) / 1.8, delta=0.002)
        same = X.route_a(np.zeros(4), C, C, np.zeros((4, 4)), M)
        self.assertEqual((same["outcome"], same["r_star"]), ("agree", None))


class Stat(unittest.TestCase):
    def test_fully_paired_replicas_give_rho_one_and_k_sigma_sigma(self):
        S = RNG.normal(size=(100, 4))
        out = X.stat_cross(S, 2.0 * S + 1.0, np.ones(4), 3.0 * np.ones(4))
        self.assertTrue(np.allclose(out["rho_diag"], 1.0))
        self.assertTrue(np.allclose(np.diag(out["K"]), 3.0))
        self.assertTrue(np.allclose(out["rho_diag_jackknife_se"], 0.0, atol=1e-12))

    def test_independent_replicas_give_rho_near_zero(self):
        out = X.stat_cross(RNG.normal(size=(400, 4)), RNG.normal(size=(400, 4)), np.ones(4), np.ones(4))
        self.assertTrue(np.all(np.abs(out["rho_diag"]) < 0.2))


class Shares(unittest.TestCase):
    def test_the_shares_sum_to_one(self):
        a, b, k = spd(4), spd(4), 0.05 * spd(4)
        Vd = X.Vd_of(a, b, k)
        sh = X.shares({"a": a}, {"b": b}, {"k": k}, Vd)
        self.assertTrue(np.allclose(np.sum(list(sh.values()), axis=0), 1.0))


class AuditFixes(unittest.TestCase):
    """The review's findings (FD-GENCMP-X-REVIEW-ANSWER.txt), each control both ways."""

    def test_same_block_refuses_a_scaled_block_at_1e_80(self):
        a = spd(4) * 1e-80
        self.assertTrue(X.same_block(a, a * (1 + 1e-12)))
        self.assertFalse(X.same_block(a, a * 1.5))
        self.assertFalse(X.same_block(a, a * (1 + 1e-9)))
        self.assertTrue(np.allclose(a, a * 1.5, rtol=1e-10))                   # numpy's default atol passes it (B1)

    def test_same_block_on_zero_blocks(self):
        z, a = np.zeros((4, 4)), np.full((4, 4), 1e-84)
        self.assertTrue(X.same_block(z, z.copy()))          # NormDISCC: identical universes on both sides (X-A2)
        self.assertFalse(X.same_block(z, a))
        self.assertFalse(X.same_block(a, z))
        self.assertFalse(X.same_block(z, np.zeros((4, 5))))

    def test_ratio_test_passes_a_constant_scale_and_refuses_one_row(self):
        n = 1000
        w2c, w2u = RNG.uniform(0.5, 2, n), RNG.uniform(0.5, 2, n)
        sent = np.zeros(n, bool)
        w5c, w5u = 7.0 * w2c, 7.0 * w2u
        r = X.ratio_test(w2u, w2c, w5u, w5c, sent)
        self.assertTrue(r["pass"])
        self.assertAlmostEqual(r["scale"], 1.0)
        w5u2 = w5u.copy()
        w5u2[500] *= 1 + 1e-5
        self.assertFalse(X.ratio_test(w2u, w2c, w5u2, w5c, sent)["pass"])
        w2u0 = w2u.copy()
        w2u0[3] = 0.0                                                        # a non-finite quotient
        self.assertFalse(X.ratio_test(w2u0, w2c, w5u, w5c, sent)["pass"])

    def test_joint_psd_both_ways(self):
        S16, S2 = spd(4), spd(4)
        self.assertTrue(X.joint_psd(S16, S2, 0.5 * X.bound_matrix(S16, S2)))
        self.assertFalse(X.joint_psd(S16, S2, 3.0 * X.bound_matrix(S16, S2)))

    def test_route_a_reads_the_whole_grid_and_lists_every_change(self):
        C, M = np.eye(4), np.eye(4) * 0.9
        out = X.route_a(np.array([0.0, 1.5, 0.0, 0.0]), C, C, np.zeros((4, 4)), M, grid=1001)
        self.assertEqual(len(out["changes_at"]), 1)
        self.assertEqual(out["r_star"], out["changes_at"][0])
        same = X.route_a(np.array([0.0, 4.0, 0.0, 0.0]), C, C, np.zeros((4, 4)), M, grid=101)   # z = 2.83 at r = 0
        self.assertEqual((same["outcome"], same["changes_at"]), ("differ", []))     # differ at both ends and between

    def test_a_badly_conditioned_vd_refuses(self):
        with self.assertRaises(gc.Stop):
            X.verdict(np.zeros(4), np.diag([1e-80, 1e-80, 1e-80, 1e-97]))

    def test_the_ambiguity_count_sees_a_non_adjacent_duplicate(self):
        big = RNG.uniform(0, 5, (100, 2)).astype(np.float32)
        big[90] = big[10]
        _, amb = X.subsequence_join(big, big[[10, 50]])
        self.assertEqual(amb, 1)

    def test_mc_positional_takes_a_float64_mcgen(self):
        mc = RNG.uniform(0, 5, (3000, 5)).astype(np.float32)
        mc[:X.SENTINEL_ROWS] = -9999.0
        self.assertTrue(X.mc_positional(mc[:, 0].astype(float), mc[:, 1].astype(float), mc.astype(float))["pass"])

    def test_the_r_band_reports_both_sides(self):
        out = X.r_band(np.array([0.1, 0.1, 0.1, 0.1]), np.eye(4), np.eye(4), np.zeros((4, 4)), 0.5 * np.eye(4),
                       0.1 * np.ones(4), np.ones(4), np.ones(4))
        self.assertEqual(set(out), {"minus_se", "plus_se"})


class Order(unittest.TestCase):
    """Rulings A1 and A2: K runs once, after BOOT has ended; V1's full readout or an over-cap probe."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def lane(self, tag, name, rec):
        p = self.d / "boot" / tag
        p.mkdir(parents=True, exist_ok=True)
        (p / name).write_text(json.dumps(rec))

    def test_boot_is_not_due_when_v0_failed(self):
        self.assertTrue(XS.boot_state(self.d, False)["ended"])

    def test_boot_has_not_ended_without_its_native_lane(self):
        self.assertFalse(XS.boot_state(self.d, True)["ended"])

    def test_boot_has_ended_after_a_failed_b0(self):
        self.lane("native", "lane_1_1.json", {"B0_bitwise": False})
        self.assertEqual(XS.boot_state(self.d, True), {"due": True, "ended": True, "b0": False, "lanes": 0})

    def test_boot_needs_all_eight_lanes_after_b0(self):
        self.lane("native", "lane_1_1.json", {"B0_bitwise": True})
        for i in range(7):
            self.lane("xcov", f"lane_{i}.json", {})
        self.assertFalse(XS.boot_state(self.d, True)["ended"])
        self.lane("xcov", "lane_7.json", {})
        self.assertTrue(XS.boot_state(self.d, True)["ended"])

    def test_v1_state(self):
        with self.assertRaises(gc.Stop):
            XS.v1_state(self.d)
        (self.d / "v1-probe").mkdir()
        (self.d / "v1-probe" / "v1.json").write_text(json.dumps({"within_full_cap": True}))
        with self.assertRaises(gc.Stop):                                    # a probe within the cap needs the full run
            XS.v1_state(self.d)
        (self.d / "v1-probe" / "v1.json").write_text(json.dumps({"within_full_cap": False}))
        self.assertEqual(XS.v1_state(self.d)["bands_pass"], {})            # every band bounded
        (self.d / XS.V1_DIR).mkdir()
        (self.d / XS.V1_DIR / "v1.json").write_text(json.dumps({"bands_pass": {"MaRES": True}}))
        self.assertEqual(XS.v1_state(self.d)["bands_pass"], {"MaRES": True})

    def test_the_committed_pins_are_the_committed_bytes(self):
        for path, h in XS.COMMITTED.items():
            self.assertEqual(XS.committed_sha(path, h, "test"), path.read_bytes())

    def test_the_draw_check_formats_mc_and_bkg_as_re2_prints_them(self):
        line = X.draw_sums_line(4, (50, 60, 30))
        _, m, g = X.draws_2d(4, 50, 60, 30)
        self.assertEqual(line["mc"], f"mc factor sum={m.sum():.6g} (n=60")
        self.assertEqual(line["bkg"], f"bkg factor sum={g.sum():.6g} (n=30")


P1 = ND / "tests/fixtures/xcov_p1streams"     # PROVENANCE.tsv there: replica 1's real p1Streams record, in a ROOT file


def p1_record():
    return X.p1_streams_record((P1 / "p1streams_present.root").read_bytes())


def _mutate(path, value):
    def f(rec):
        rec = json.loads(json.dumps(rec))
        *head, last = path
        d = rec
        for k in head:
            d = d[k]
        d[last] = value(d[last])
        return rec
    return f


# addendum X-A1 condition 2: each mutant of replica 1's real record must fail the background leg
BKG_MUTANTS = {
    "seed offset 20,000,001": _mutate(("seed_offsets", "bkg"), lambda v: v + 1),
    "stream size n - 1": _mutate(("n", "bkg"), lambda v: v - 1),
    "stream size n + 1": _mutate(("n", "bkg"), lambda v: v + 1),
    "sum + 1": _mutate(("sum", "bkg"), lambda v: v + 1.0),
    "sum - 1": _mutate(("sum", "bkg"), lambda v: v - 1.0),
    "bootstrap seed 2": _mutate(("bootstrap_seed",), lambda v: 2),
    "sum.bkg key absent": lambda rec: {k: v for k, v in rec.items() if k != "sum"},
}


@unittest.skipUnless(importlib.util.find_spec("uproot"), "the record is read with uproot (omnifold_py310)")
class BkgLeg(unittest.TestCase):
    def test_the_real_record_is_read_from_its_tnamed(self):
        rec = p1_record()
        self.assertEqual(rec["seed_offsets"], {"bkg": 20_000_000, "data": 0, "mc": 10_000_000})
        self.assertEqual(rec["bootstrap_seed"], 1)

    def test_replica_1s_real_record_passes_against_the_regenerated_stream(self):
        self.assertEqual(X.bkg_stream_check(p1_record(), 1), [])

    def test_every_mutant_of_the_real_record_fails(self):
        rec = p1_record()
        for name, mutant in BKG_MUTANTS.items():
            with self.subTest(name):
                self.assertTrue(X.bkg_stream_check(mutant(rec), 1))

    def test_the_real_record_fails_for_another_replica(self):
        self.assertTrue(X.bkg_stream_check(p1_record(), 2))

    def test_a_regeneration_at_the_wrong_offset_or_size_fails(self):
        rec = p1_record()
        self.assertTrue(X.bkg_stream_check(rec, 1, X.N_2D_BKG - 1))
        old = X.SEED_BKG
        try:
            X.SEED_BKG = old + 1
            self.assertTrue(X.bkg_stream_check(dict(rec, seed_offsets=dict(rec["seed_offsets"], bkg=old + 1)), 1))
        finally:
            X.SEED_BKG = old

    def test_a_file_without_p1streams_fails(self):
        rec = X.p1_streams_record((P1 / "p1streams_absent.root").read_bytes())
        self.assertIsNone(rec)
        self.assertEqual(X.bkg_stream_check(rec, 1), ["no p1Streams record"])


LOOKUP = ND / "tests/fixtures/xcov_v1_lookup"   # PROVENANCE.tsv there: the detector receipt's digest map, verbatim


def digest_maps():
    sf1 = {p: h for h, p in (ln.split(None, 1) for ln in XS.SF1.read_text().splitlines() if ln.strip())}
    sf1 = {p.strip(): h for p, h in sf1.items()}
    d = json.loads((LOOKUP / "detector_files_sha256.json").read_text())
    return sf1, {str(XS.DET_RECEIPT.parent / Path(p).name): h for p, h in d["files_sha256"].items()}


class V1Lookup(unittest.TestCase):
    """Addendum X-A2: weight_files on the real digest maps (the committed SF1 manifest, the detector receipt)."""

    def test_every_class_resolves_to_its_sorted_first_with_its_count(self):
        sf1, det = digest_maps()
        for (b, i, k), n in {("2p2h", 0, "wt"): 1, ("EtaNCEL", 0, "wt"): 22, ("EtaNCEL", 0, "wr"): 8,
                             ("Rvn1pi", 0, "wt"): 2}.items():
            with self.subTest(f"{b}:{i}:{k}"):
                path, h, nm = XS.weight_files(b, i, sf1, det)[k]
                hits = sorted(p for p, v in {**sf1, **det}.items() if v == h and p.endswith(f"_{k}.npy"))
                self.assertEqual((nm, str(path)), (n, hits[0]))

    def test_the_full_lookup_resolves_every_universe(self):
        sf1, det = digest_maps()
        hist = {}
        for b, i in XS.universe_list():
            for k, (_, _, nm) in XS.weight_files(b, i, sf1, det).items():
                hist[nm] = hist.get(nm, 0) + 1
        self.assertEqual(hist, {1: 322, 22: 16, 8: 8, 2: 4})

    def test_a_digest_no_pinned_file_carries_stops(self):
        sf1, det = digest_maps()
        _, h, _ = XS.weight_files("EtaNCEL", 0, sf1, det)["wt"]
        sf1 = {p: v for p, v in sf1.items() if v != h}
        det = {p: v for p, v in det.items() if v != h}
        with self.assertRaises(gc.Stop):
            XS.weight_files("EtaNCEL", 0, sf1, det)

    def test_multi_match_classes_name_the_bands_they_span(self):
        c = XS.multi_match_classes({"EtaNCEL:0:wt": ("h", 22), "MaNCEL:1:wt": ("h", 22), "MaRES:0:wt": ("g", 1),
                                    "Rvn1pi:0:wr": ("r", 2)})
        self.assertEqual(c["h"]["bands"], ["EtaNCEL", "MaNCEL"])
        self.assertEqual(c["h"]["n_files"], 22)
        self.assertNotIn("g", c)
        self.assertEqual(c["r"]["lookups"], ["Rvn1pi:0:wr"])

    def test_npy_shape_reads_the_header_only(self):
        with tempfile.TemporaryDirectory() as td:
            for ver in ((1, 0), (2, 0)):
                p = Path(td) / f"a{ver[0]}.npy"
                with open(p, "wb") as fh:
                    np.lib.format.write_array(fh, np.zeros(37, np.float32), version=ver)
                self.assertEqual(XS.npy_shape(p), (37,))


if __name__ == "__main__":
    unittest.main()
