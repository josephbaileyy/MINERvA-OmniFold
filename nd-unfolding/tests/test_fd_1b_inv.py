"""Controls for 1B's gate-D investigation (state/measurement-paper/5d-community-20261024/FD-1B-INV-DECLARATION.md), each
rule in the direction it acts and in the other:

* the floor: chi2 against the closed form, the 95 % upper factor, the pure-noise block factors by simulation, the
  fallback's full-correlation bound;
* rule H2 cell by cell (SUPPORTED, REJECTED, OPEN; fallback SUPPORTED reads OPEN) and per step (any SUPPORTED or OPEN
  goes to I1); end to end on a staged synthetic world in which one band carries gate D's failure with both blocks under
  their floors (SUPPORTED), with the toys' block far above its floor while S1's is near zero (REJECTED: review B1's
  R00 MaRES case), between the two floors (OPEN), and under the fallback;
* I0's controls refuse: rho off gate D's by one ulp, S1 blocks not reproduced, S1_CV not the jitter base, a failing set
  other than the declared one;
* I2's modes: at CV every mode is the CV experiment bitwise; B is the derivation's own source factors; C's factor is
  the reciprocal of g_f and its builder matches prior_inputs; A is universe_inputs; the run's CV product equals the
  derivation's CV product;
* rule I2: the telescoping identity, each attribution and each refusal to attribute, F_truth only when it survives
  over S1-resolved bands (review B2), each mechanism's count read separately (review M3); end to end on staged mode
  products, with its CV and reproduction controls;
* the O_NOATIME loaders equal the path loaders, the flag's absence and an EPERM refuse, stage refuses a source whose
  atime moved, and an instrumented run of the unfold path and of stage opens no input without O_NOATIME (review M4),
  with a positive control that the instrument sees a plain read.

No real data are read: every fixture is synthetic."""
from __future__ import annotations

import json
import math
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

import fd_1b_diag as fdg  # noqa: E402
import fd_1b_inv as inv  # noqa: E402
import fd_1b_score as fs  # noqa: E402
import fd_1b_toys as toys  # noqa: E402
import s1_assemble as sa  # noqa: E402
import s5c_unfold  # noqa: E402
import s5n_pseudo  # noqa: E402
import s5p_nullexp as ne  # noqa: E402
import s5p_universe  # noqa: E402
from test_fd_1b import World as ToyWorld, digest, fake_unfold, toy_meta  # noqa: E402

CELLS = [f"R{c:02d}" for c in range(16)]
EYE = np.eye(16)


def plain_noatime():
    """The tests run where O_NOATIME may not exist: the flag is set to 0, a plain read with the same code path."""
    return mock.patch.object(inv, "NOATIME_FLAG", 0)


# ----------------------------------------------------------------------------------------------------- the floor


class Floor(unittest.TestCase):
    def test_chi2_matches_the_closed_form_and_the_table(self):
        for k in (2, 16, 20):
            for x in (3.0, 10.0, 26.296):
                self.assertAlmostEqual(inv.chi2_cdf(x, k), 1 - fs.chi2_sf(x, k), places=12)
        self.assertAlmostEqual(inv.chi2_ppf(0.05, 19), 10.117, places=3)
        self.assertAlmostEqual(inv.upper_factor(20), 19 / 10.117, places=3)

    def test_jitter_sigma_is_ddof_1_and_needs_two(self):
        X = np.array([[1.0] * 16, [3.0] * 16])
        np.testing.assert_allclose(inv.jitter_sigma(X), np.sqrt(2.0))
        with self.assertRaises(inv.Refusal):
            inv.jitter_sigma(X[:1])

    def test_noise_factors_are_the_estimators_pure_noise_expectation(self):
        rng = np.random.default_rng(1)
        w = rng.uniform(0.5, 4.0, 100)
        for band, n, wt in (("MaRES", 2, None), ("2p2h", 3, None), (sa.FLUX, 100, w)):
            blocks = [sa.mat_cov(rng.normal(0, 1.0, (n, 16)), wt)[0, 0] for _ in range(20000 if n < 100 else 2000)]
            self.assertAlmostEqual(np.mean(blocks), inv.noise_factor(band, w), delta=0.03)
        self.assertEqual(inv.noise_factor("MaRES", w), 0.5)
        self.assertAlmostEqual(inv.noise_factor("2p2h", w), 2 / 3)

    def test_fallback_bound_holds_for_any_correlation_and_is_tight_at_full(self):
        rng = np.random.default_rng(2)
        m = np.repeat(np.arange(16), 2)
        x = rng.uniform(1, 3, 32)
        s = rng.uniform(0.001, 0.005, 32)
        bound = inv.fallback_sigma(s, x, m)
        for rho in (0.0, 0.5, 1.0):
            shared = rng.normal(size=(20000, 16)).repeat(2, axis=1)
            Z = rho * shared + math.sqrt(1 - rho ** 2) * rng.normal(size=(20000, 32))
            cell = np.array([(Z[:, m == c] * (s * x)[m == c]).sum(axis=1) for c in range(16)]).T
            self.assertTrue(np.all(cell.std(axis=0) <= bound * 1.02))
        np.testing.assert_allclose(bound, [(s * x)[m == c].sum() for c in range(16)])


# ------------------------------------------------------------------------------------------------------- rule H2


class RuleH2(unittest.TestCase):
    def test_cell_readings(self):
        self.assertEqual(inv.h2_cell(True, True, False), "SUPPORTED")
        self.assertEqual(inv.h2_cell(False, False, False), "REJECTED")
        self.assertEqual(inv.h2_cell(True, False, False), "OPEN")
        self.assertEqual(inv.h2_cell(False, True, False), "OPEN")
        self.assertEqual(inv.h2_cell(True, True, True), "OPEN")
        self.assertEqual(inv.h2_cell(False, False, True), "REJECTED")

    def test_step_readings(self):
        r = inv.h2_step({"R00": "SUPPORTED", "R01": "SUPPORTED"})
        self.assertEqual((r["verdict"], r["outcome"], r["next"]), ("SUPPORTED", "O3 pending I1", "I1"))
        self.assertEqual(inv.h2_step({"R00": "REJECTED", "R01": "OPEN"})["next"], "I1")
        r = inv.h2_step({"R00": "SUPPORTED", "R01": "REJECTED"})
        self.assertEqual((r["verdict"], r["o3_cells_pending_I1"], r["next"]), ("MIXED", ["R00"], "I1"))
        r = inv.h2_step({"R00": "REJECTED", "R01": "REJECTED"})
        self.assertEqual((r["verdict"], r["outcome"], r["next"]), ("REJECTED", None, "I2"))

    def test_a_term_is_noise_only_if_both_blocks_are_under_their_floors(self):
        N = np.ones(16)
        self.assertTrue(inv.noise_consistent(3.99 * N, 3.99 * N, N, N).all())
        self.assertFalse(inv.noise_consistent(4 * N, 0 * N, N, N).any())        # S1's block at 4x: kept
        self.assertFalse(inv.noise_consistent(0 * N, 1e6 * N, N, N).any())      # review B1: toys far above, S1 ~ 0
        self.assertFalse(inv.noise_consistent(1e6 * N, 0 * N, N, N).any())

    def test_rho_resolved_drops_only_noise_terms_and_a_negative_sum_is_out(self):
        terms = {"a": np.full(16, 0.5), "b": np.full(16, 0.1)}
        noise = {"a": np.ones(16, bool), "b": np.zeros(16, bool)}
        np.testing.assert_allclose(inv.rho_resolved(terms, noise), math.sqrt(1.1))
        neg = inv.rho_resolved({"a": np.full(16, -2.0)}, {"a": np.zeros(16, bool)})
        self.assertFalse(inv.in_window(neg).any())
        self.assertTrue(inv.in_window(np.array([0.9, 1.1])).all())


# -------------------------------------------------------------------------------------------- a staged synthetic world


class Staged:
    """A staged I0 input set on 16 cells (U = I): toy derivation products, S1 universe unfolds whose blocks ARE the
    assembly's, data and nominal jitters. Every band's S1 shifts are its carried toy shifts (term 0), except band
    ``bad``, whose two toy universes are x_cv (1 +- bad_toy) and whose S1 universes are f (1 +- bad_s1): its blocks are
    (bad_toy f)^2 and (bad_s1 f)^2 to within x_cv / x_T, against floors of sigma^2 f^2 / 2 per side."""

    def __init__(self, tmp: Path, bad="MaRES", bad_toy=0.08, bad_s1=0.001, sigma_d=0.002, sigma_n=0.0002, jitters=True):
        rng = np.random.default_rng(7)
        self.tmp, self.root = tmp, tmp / "staged"
        for sub in ("derivation", "uni", "s1", "jitter-data", "jitter-nom"):
            (self.root / sub).mkdir(parents=True)
        self.f = rng.uniform(1.0, 3.0, 16)
        self.x_t = self.f / 1.2
        x_cv = self.x_t * rng.uniform(0.98, 1.02, 16)
        g = self.f / self.x_t
        w = rng.uniform(0.5, 4.0, 100)
        self.constraint = self.root / "flux_constraint.txt"
        self.constraint.write_text("".join(f"Flux {i} {w[i]!r}\n" for i in range(100)))
        xD, xS = {"CV": x_cv}, {"CV": self.f.copy()}
        for b in sorted(sa.EXPECT):
            for i in range(sa.EXPECT[b]):
                u = f"{b}_{i}"
                if b == bad:
                    xD[u] = x_cv * (1 + (1 - 2 * i) * bad_toy)
                    xS[u] = self.f * (1 + (1 - 2 * i) * bad_s1)
                else:
                    xD[u] = x_cv * (1 + rng.normal(0, 0.03, 16))
                    xS[u] = self.f + g * (xD[u] - x_cv)
        for u, v in xD.items():
            m = toy_meta("derivation", None, json.loads(json.dumps(toys.single_universe(u))), mode="derivation", universe=u)
            np.savez_compressed(self.root / "derivation" / f"{inv.DER_TAG}_{u}.npz", xsec_flat=v, xtrue_flat=self.x_t,
                                meta=json.dumps(m))
        for u, v in xS.items():
            np.savez_compressed(self.root / "uni" / f"{inv.S1_TAG}_{u}.npz", xsec_flat=v)
        blocks = {"stat": np.diag((0.005 * self.f) ** 2), "normalization": np.outer(0.014 * self.f, 0.014 * self.f),
                  "seed": np.zeros((16, 16))}
        for b in sa.LATERAL_BANDS:
            blocks[f"lat:{b}"] = np.diag((0.01 * self.f) ** 2)
        for b in sorted(sa.EXPECT):
            X = np.array([EYE @ xS[f"{b}_{i}"] for i in range(sa.EXPECT[b])])
            blocks[f"band:{b}"] = sa.mat_cov(X, w if b == sa.FLUX else None)
        self.s1 = self.root / "s1" / "s1_assembly.npz"
        np.savez_compressed(self.s1, f=self.f, U=np.eye(16, dtype=np.float32), C_e=sum(blocks.values()),
                            **{"C_" + k.replace(":", "_"): v for k, v in blocks.items()},
                            meta=json.dumps({"blocks": sorted(blocks)}))
        np.savez_compressed(self.root / "jitter-data" / "data_b-_j-.npz", xsec_flat=self.f.copy())
        np.savez_compressed(self.root / "jitter-nom" / "nom_b-_j-.npz", xsec_flat=x_cv)
        for j in range(1, 21):
            np.savez_compressed(self.root / "jitter-data" / f"data_b-_j{j}.npz",
                                xsec_flat=self.f * (1 + rng.normal(0, sigma_d, 16)))
            np.savez_compressed(self.root / "jitter-nom" / f"nom_b-_j{j}.npz",
                                xsec_flat=x_cv * (1 + rng.normal(0, sigma_n, 16)))
        missing = []
        if not jitters:
            shutil.rmtree(self.root / "jitter-data")
            shutil.rmtree(self.root / "jitter-nom")
            missing = [{"role": "jitter-data", "src": "x"}, {"role": "jitter-nom", "src": "y"}]
        (self.root / "staged.json").write_text(json.dumps({"staged": [], "missing": missing}))
        self.definition = tmp / "def.json"
        self.definition.write_text(json.dumps({"h2_to_reporting_cell": np.repeat(np.arange(16), 2).tolist()}))
        self.receipt = tmp / "receipt.json"
        rel = {"sigma_num_base_rel": [sigma_d] * 32}
        self.receipt.write_text(json.dumps({"study_N": {"N1_data": {"H2": rel},
                                                        "N2_nominal_930000": {"H2": {"sigma_num_base_rel": [sigma_n] * 32}}}}))

    def patches(self):
        box = np.repeat(np.eye(16), 2, axis=0) / 2.0
        return [mock.patch.object(fs, "S1_NPZ_SHA256", digest(self.s1)),
                mock.patch.object(sa, "CONSTRAINT_SHA256", digest(self.constraint)),
                mock.patch.object(sa, "fine_map", lambda d: None),
                mock.patch.object(sa, "functional_matrix", lambda fm: EYE),
                mock.patch.object(inv, "box_matrix", lambda: box),
                mock.patch.object(fs, "surrogate_share", lambda s1: 0.29)]

    def gate_d(self, perturb=False) -> Path:
        s1 = fs.load_s1(self.s1)
        d = fs.derivation_blocks(self.root / "derivation", inv.DER_TAG, s1, self.constraint)
        rho = fdg.diagnose(d, s1)["rho"]
        if perturb:
            rho[0] = float(np.nextafter(rho[0], 10.0))
        E = {**d["fixed"], **d["carried"]}
        e = sum(v for k, v in E.items() if k.startswith("band:") and sa.group_of(k) == "interaction")
        m = sum(v for k, v in s1["blocks"].items() if k.startswith("band:") and sa.group_of(k) == "interaction")
        p = self.tmp / ("gate-d-p.json" if perturb else "gate-d.json")
        self.int_ratio = np.sqrt(np.diag(e) / np.diag(m))
        p.write_text(json.dumps({"rho": rho, "per_group_sigma_ratio": {"interaction": self.int_ratio.tolist()}}))
        self.failing = tuple(c for c, r in zip(CELLS, rho) if not (0.9 <= r <= 1.1))
        self.d, self.s1v = d, s1
        return p

    def run_i0(self, perturb=False, cells=None):
        ps = self.patches()
        for p in ps:
            p.start()
        try:
            gd = self.gate_d(perturb)
            with mock.patch.object(fdg, "GATE_D_SHA256", digest(gd)), \
                    mock.patch.object(inv, "H2_CELLS", cells if cells is not None else self.failing):
                return inv.i0(self.root, self.definition, gd, self.receipt)
        finally:
            for p in reversed(ps):
                p.stop()

    def write_modes(self, a_scale=1.0, b_scale=1.0, c_scale=0.1, tamper=None):
        """Mode products for I2: A's and B's carried shifts are S1's shifts x a_scale, x b_scale; C's x c_scale."""
        u_dir = self.tmp / "unf"
        u_dir.mkdir(exist_ok=True)
        g, x_cv = self.d["g"], self.d["x"]["CV"]
        cvp = np.load(self.root / "derivation" / f"{inv.DER_TAG}_CV.npz")["xsec_flat"]
        f_s1 = np.load(self.root / "uni" / f"{inv.S1_TAG}_CV.npz")["xsec_flat"]
        for mode, k in (("A", a_scale), ("B", b_scale), ("C", c_scale)):
            np.savez_compressed(u_dir / f"t_{mode}_CV.npz", xsec_flat=cvp if tamper != ("cv", mode) else cvp * (1 + 1e-15),
                                meta=json.dumps({"schema": inv.SCHEMA, "mode": mode, "universe": "CV"}))
            for b in inv.INTERACTION:
                for i in range(sa.EXPECT[b]):
                    xs1 = np.load(self.root / "uni" / f"{inv.S1_TAG}_{b}_{i}.npz")["xsec_flat"]
                    x = x_cv + k * (xs1 - f_s1) / g
                    meta = {"schema": inv.SCHEMA, "mode": mode, "universe": f"{b}_{i}"}
                    if tamper == ("meta", mode):
                        meta["mode"] = "Z"
                    np.savez_compressed(u_dir / f"t_{mode}_{b}_{i}.npz", xsec_flat=x, meta=json.dumps(meta))
        return u_dir

    def run_i2(self, i0_json: Path, u_dir: Path, n_out=None, i1=None):
        ps = self.patches()
        for p in ps:
            p.start()
        try:
            gd = self.gate_d()
            n = n_out if n_out is not None else int(np.sum((self.int_ratio < 0.9) | (self.int_ratio > 1.1)))
            with mock.patch.object(fdg, "GATE_D_SHA256", digest(gd)), mock.patch.object(inv, "H2_CELLS", self.failing), \
                    mock.patch.object(inv, "N_INTERACTION_OUT", n):
                return inv.i2(self.root, u_dir, "t", gd, i0_json, i1)
        finally:
            for p in reversed(ps):
                p.stop()


class I0(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="fd1b-inv-"))

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def world(self, **kw):
        return Staged(self.tmp, **kw)

    def test_both_blocks_under_their_floors_reads_supported(self):
        # the toys' block (0.08 f)^2 is half of 4 x (0.08 f)^2 / 2, S1's (0.001 f)^2 is far under 4 x (0.01 f)^2 / 2
        w = self.world(bad_toy=0.08, bad_s1=0.001, sigma_d=0.01, sigma_n=0.08)
        r = w.run_i0()
        self.assertTrue(w.failing)
        self.assertEqual(set(r["H2_cells"].values()), {"SUPPORTED"})
        self.assertEqual((r["H2"]["outcome"], r["H2"]["next"]), ("O3 pending I1", "I1"))
        self.assertEqual(len(r["per_band"]["MaRES"]["noise_consistent_upper"]), 16)

    def test_toys_far_above_their_floor_with_s1_near_zero_reads_rejected(self):
        # review B1's R00 MaRES case: S1's share ~0, the toys' block far above the nominal floor; the term stays
        w = self.world(bad_toy=0.08, bad_s1=0.001, sigma_d=0.01, sigma_n=0.0002)
        r = w.run_i0()
        self.assertTrue(w.failing)
        self.assertEqual(set(r["H2_cells"].values()), {"REJECTED"})
        self.assertEqual(r["H2"]["next"], "I2")
        self.assertEqual(r["per_band"]["MaRES"]["noise_consistent_point"], [])
        self.assertTrue(all(x > 0.2 for x in r["positive_terms_resolved_on_toy_side"]["point"]))

    def test_between_the_two_floors_reads_open(self):
        # the toys' block about 1.4 x 4 x its point floor: kept at the point floor, dropped at 1.878 x it
        w = self.world(bad_toy=0.08, bad_s1=0.001, sigma_d=0.01, sigma_n=0.0478)
        r = w.run_i0()
        self.assertIn("OPEN", r["H2_cells"].values())
        self.assertEqual(r["H2"]["next"], "I1")

    def test_fallback_cannot_support_but_can_reject(self):
        w = self.world(bad_toy=0.08, bad_s1=0.001, sigma_d=0.01, sigma_n=0.08, jitters=False)
        r = w.run_i0()
        self.assertTrue(r["floor"]["kind"].startswith("fallback"))
        self.assertEqual(set(r["H2_cells"].values()), {"OPEN"})
        shutil.rmtree(self.tmp)
        self.tmp.mkdir()
        w = self.world(bad_toy=0.08, bad_s1=0.001, sigma_d=0.0001, sigma_n=0.00001, jitters=False)
        self.assertEqual(set(w.run_i0()["H2_cells"].values()), {"REJECTED"})

    def test_rho_one_ulp_off_gate_d_refuses(self):
        with self.assertRaisesRegex(fs.Invalid, "bit for bit"):
            self.world().run_i0(perturb=True)

    def test_a_failing_set_other_than_declared_refuses(self):
        with self.assertRaisesRegex(fs.Invalid, "failing cells"):
            self.world().run_i0(cells=("R00",))

    def test_s1_blocks_not_reproduced_refuses(self):
        w = self.world()
        p = w.root / "uni" / f"{inv.S1_TAG}_MaCCQE_0.npz"
        x = np.load(p)["xsec_flat"]
        np.savez_compressed(p, xsec_flat=x * (1 + 1e-12))
        with self.assertRaisesRegex(fs.Invalid, "reproduce the assembly"):
            w.run_i0()

    def test_s1_cv_not_the_jitter_base_refuses(self):
        w = self.world()
        p = w.root / "jitter-data" / "data_b-_j-.npz"
        np.savez_compressed(p, xsec_flat=w.f * (1 + 1e-15))
        with self.assertRaisesRegex(fs.Invalid, "N1 base"):
            w.run_i0()

    def test_missing_required_input_refuses(self):
        w = self.world()
        (w.root / "staged.json").write_text(json.dumps({"staged": [], "missing": [{"role": "s1-uni", "src": "x"}]}))
        with self.assertRaisesRegex(inv.Refusal, "required inputs missing"):
            w.run_i0()


# ------------------------------------------------------------------------------------------------------- I2's modes


class Modes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="fd1b-inv-modes-"))
        cls.w = ToyWorld(cls.tmp)
        cls.inputs = s5c_unfold.load_inputs(cls.w.inputs)
        bz = np.load(cls.w.bkg, allow_pickle=True)
        cls.bkg = {"bkg_reco": bz["bkg_reco"], "bkg_w": bz["bkg_w"], "bkg_nd": bz["bkg_nd"]}
        z = dict(np.load(cls.w.bank / "cv.npz", allow_pickle=True))
        rng = np.random.default_rng(3)
        for k, e in zip(("td_pt", "td_pz", "td_ea", "td_q3", "td_w"), cls.inputs["edges"]):
            z[k] = rng.uniform(e[0], e[-1], 50)
        cls.bank_cv = z

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def setUp(self):
        self.ps = self.w.patches() + [plain_noatime()]
        for p in self.ps:
            p.start()

    def tearDown(self):
        for p in reversed(self.ps):
            p.stop()

    def test_every_mode_at_cv_is_the_cv_experiment_bitwise(self):
        exp_cv, _ = inv.nominal_experiment(self.inputs, self.bkg)
        for mode in inv.MODES:
            exp = inv.with_mc(exp_cv, *inv.mode_inputs(mode, "CV", self.inputs, self.bkg, self.w.bank, self.bank_cv)[:2])
            for k in exp_cv:
                if k == "edges":
                    self.assertTrue(all(np.array_equal(x, y) for x, y in zip(exp[k], exp_cv[k])))
                else:
                    self.assertTrue(np.array_equal(np.asarray(exp[k]), np.asarray(exp_cv[k])), (mode, k))

    def test_b_is_the_derivations_own_source_factors(self):
        for u in ("MaRES_1", "2p2h_2", "LowQ2_1"):
            d = toys.single_universe(u)
            fs_d, fb_d, _ = toys.source_factors(d, self.inputs, self.bkg, self.w.bank, self.w.det,
                                                np.ones(self.inputs["MCgen"].shape[0], bool), None)
            ui, ub, _ = inv.mode_inputs("B", u, self.inputs, self.bkg, self.w.bank, self.bank_cv)
            np.testing.assert_array_equal(ui["w_reco"], np.asarray(self.inputs["w_reco"], float) * fs_d)
            np.testing.assert_array_equal(ub["bkg_w"], np.asarray(self.bkg["bkg_w"], float) * fb_d)
            self.assertIs(ui["w_truth"], self.inputs["w_truth"])
            self.assertIs(ui["denom_nd"], self.inputs["denom_nd"])
            # the experiment unfolds with the mode's template weights, not the CV's
            exp_cv, _ = inv.nominal_experiment(self.inputs, self.bkg)
            exp = inv.with_mc(exp_cv, ui, ub)
            np.testing.assert_array_equal(exp["tmpl_w"], s5n_pseudo.build_data(ui, ub)["tmpl_w"])
            self.assertFalse(np.array_equal(exp["tmpl_w"], exp_cv["tmpl_w"]))

    def test_c_factor_is_the_reciprocal_of_g_and_its_builder_matches_prior_inputs(self):
        w = inv.universe_weights(self.w.bank, "MaRES_0", "keep")
        _, _, k_wt, _ = inv.response_factors(w, self.inputs, self.bkg, "MaRES_0")
        r = inv.cell_mean_factor(k_wt, self.inputs)
        g = ne.truth_preserving(k_wt, self.inputs, np.ones(self.inputs["MCgen"].shape[0], bool))
        np.testing.assert_allclose(r * g, 1.0, rtol=1e-13)
        mine, ref = inv.prior_mc(self.inputs, r), s5p_universe.prior_inputs(self.inputs, r)
        for k in ("w_truth", "w_reco"):
            np.testing.assert_array_equal(mine[k], ref[k])
        np.testing.assert_allclose(mine["denom_nd"], ref["denom_nd"], rtol=1e-13)
        one = inv.prior_mc(self.inputs, np.ones_like(r))
        for k in ("w_truth", "w_reco", "denom_nd"):
            self.assertTrue(np.array_equal(one[k], np.asarray(self.inputs[k], float)), k)

    def test_a_is_universe_inputs(self):
        # a non-finite weight is zeroed, as the universe unfolds' loader does (on a private copy: the shared bank is pinned)
        bank = self.tmp / "bank-nan"
        bank.mkdir(exist_ok=True)
        for k in ("wt", "wr", "tdw", "bkgw"):
            shutil.copy(self.w.bank / f"MaCCQE_1_{k}.npy", bank / f"MaCCQE_1_{k}.npy")
        x = np.load(bank / "MaCCQE_1_wt.npy")
        x[5] = np.nan
        np.save(bank / "MaCCQE_1_wt.npy", x)
        ui, ub, _ = inv.mode_inputs("A", "MaCCQE_1", self.inputs, self.bkg, bank, self.bank_cv)
        w = s5p_universe.weights(bank, "MaCCQE_1", nonfinite="zero")
        ri, rb, _ = s5p_universe.universe_inputs(self.inputs, self.bkg, self.bank_cv, w, "MaCCQE", "1", None)
        for k in ("w_truth", "w_reco", "denom_nd"):
            np.testing.assert_array_equal(ui[k], ri[k])
        np.testing.assert_array_equal(ub["bkg_w"], rb["bkg_w"])

    def test_the_runs_cv_product_is_the_derivations_cv_product(self):
        out_d, out_i = self.tmp / "der", self.tmp / "inv"
        with mock.patch.object(s5n_pseudo, "unfold_negweight", fake_unfold):
            self.assertEqual(toys.main(self.w.run_argv("derivation", "derivation", out_d, universes="CV")), 0)
            argv = ["unfold", "--mode", "B", "--universes", "CV,MaRES_0", "--npz", str(self.w.inputs), "--bkg",
                    str(self.w.bkg), "--bank", str(self.w.bank), "--detector-dir", str(self.w.det), "--pins",
                    str(self.w.pins), "--expect-pins-sha256", digest(self.w.pins), "--out", str(out_i), "--tag", "t"]
            self.assertEqual(inv.main(argv), 0)
        a = np.load(out_d / "t_CV.npz")["xsec_flat"]
        b = np.load(out_i / "t_B_CV.npz")["xsec_flat"]
        self.assertTrue(np.array_equal(a, b))
        self.assertFalse(np.array_equal(np.load(out_i / "t_B_MaRES_0.npz")["xsec_flat"], b))

    def test_a_universe_outside_the_interaction_set_refuses(self):
        argv = ["unfold", "--mode", "A", "--universes", "Flux_3", "--npz", str(self.w.inputs), "--bkg", str(self.w.bkg),
                "--bank", str(self.w.bank), "--detector-dir", str(self.w.det), "--pins", str(self.w.pins),
                "--expect-pins-sha256", digest(self.w.pins), "--out", str(self.tmp / "x")]
        with mock.patch.object(s5n_pseudo, "unfold_negweight", fake_unfold):
            self.assertEqual(inv.main(argv), 4)


# ------------------------------------------------------------------------------------------------------- rule I2


def F_of(src, prior, truth):
    t = np.array([src * prior * truth])
    return {"total": t, "F_src": np.array([src]), "F_prior": np.array([prior]), "F_truth": np.array([truth])}


class RuleI2(unittest.TestCase):
    def test_the_factors_telescope_exactly(self):
        rng = np.random.default_rng(4)
        E, B, A, M = (rng.uniform(0.5, 5, 16) for _ in range(4))
        F = inv.factors(E, B, A, M)
        np.testing.assert_allclose(F["F_src"] * F["F_prior"] * F["F_truth"], F["total"], rtol=1e-14)

    def test_each_factor_attributes_to_its_outcome(self):
        a = inv.attribute(F_of(1.0, 1.6, 1.02), 0)
        self.assertEqual((a["factor"], a["mechanism"], a["outcome"]), ("F_prior", "H1", "O1"))
        a = inv.attribute(F_of(1.02, 1.0, 1.6), 0, np.array([1.5]))
        self.assertEqual((a["factor"], a["mechanism"], a["outcome"]), ("F_truth", "H3", "O1"))
        a = inv.attribute(F_of(1.6, 1.02, 1.0), 0)
        self.assertEqual((a["factor"], a["mechanism"], a["outcome"]), ("F_src", "H4", "O2"))
        self.assertEqual(inv.attribute(F_of(0.6, 1.0, 0.98), 0)["outcome"], "O2")

    def test_f_truth_needs_to_survive_over_s1_resolved_bands(self):
        # review B2: F_truth is the one factor made on the data; without S1-resolved support it reads O4
        for tr in (None, np.array([1.05]), np.array([0.7]), np.array([np.nan])):
            a = inv.attribute(F_of(1.02, 1.0, 1.6), 0, tr)
            self.assertEqual((a["outcome"], a["why"]), ("O4", "F_truth not separated from S1-side noise"), tr)

    def test_no_attribution_inside_the_window_below_half_or_against_the_side(self):
        self.assertEqual(inv.attribute(F_of(1.09, 1.09, 1.09), 0)["outcome"], "O4")       # each inside
        self.assertEqual(inv.attribute(F_of(1.15, 1.15, 1.15), 0)["outcome"], "O4")       # each a third
        self.assertEqual(inv.attribute(F_of(1.2, 1.15, 1.15), 0)["outcome"], "O4")        # 0.18 of a 0.46 log
        self.assertEqual(inv.attribute(F_of(1.5, 0.95, 1.0), 0)["factor"], "F_src")       # opposite side ignored
        # the largest factor overall (F_prior, 0.4) is on the other side: the same-side largest, F_truth, decides
        self.assertEqual(inv.attribute(F_of(1.6, 0.4, 2.0), 0, np.array([1.5]))["mechanism"], "H3")

    def test_each_mechanism_is_counted_on_its_own(self):
        h1, h3, h4, un = ({"mechanism": m} for m in ("H1", "H3", "H4", None))
        # review M3: four H1 and four H3 cells do not make an O1 headline
        h = inv.headline({f"R{i:02d}": v for i, v in enumerate([h1] * 4 + [h3] * 4 + [h4] * 7)})
        self.assertEqual((h["outcome"], h["mixed"], h["level"]), ("O4", True, {"H1": "partial", "H3": "partial", "H4": "partial"}))
        h = inv.headline({f"R{i:02d}": v for i, v in enumerate([h1] * 8 + [h4] * 3 + [un] * 4)})
        self.assertEqual((h["headline"], h["outcome"], h["level"]["H4"], h["level"]["H3"]), ("H1", "O1", "refuted", "refuted"))
        h = inv.headline({f"R{i:02d}": v for i, v in enumerate([h4] * 8 + [h1] * 7)})
        self.assertEqual((h["headline"], h["outcome"], h["level"]["H1"]), ("H4", "O2", "partial"))


class I2(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="fd1b-inv-i2-"))
        self.w = Staged(self.tmp, bad_toy=0.08, bad_s1=0.001, sigma_d=0.0001, sigma_n=0.00001)
        self.i0 = self.tmp / "i0.json"
        self.i0.write_text(json.dumps(self.w.run_i0()))

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_modes_equal_to_s1_attribute_the_gap_to_the_source_side(self):
        r = self.w.run_i2(self.i0, self.w.write_modes(a_scale=1.0, b_scale=1.0))
        np.testing.assert_allclose(r["factors"]["F_truth"], 1.0, rtol=1e-9)
        np.testing.assert_allclose(r["factors"]["F_prior"], 1.0, rtol=1e-9)
        self.assertTrue(r["attribution"])
        self.assertEqual({v["mechanism"] for v in r["attribution"].values()}, {"H4"})
        self.assertEqual(r["headline"]["outcome"], "O2")
        self.assertIn("R00", r["interaction_share_of_rho2_minus_1"])

    def test_b_equal_to_e_attributes_the_gap_to_the_prior(self):
        # B's carried shifts reproduce the toys' (B = E), A's reproduce S1's (A = M): sqrt(E/M) is all F_prior
        u = self.w.write_modes(a_scale=1.0, b_scale=1.0)
        g, x_cv = self.w.d["g"], self.w.d["x"]["CV"]
        for b in inv.INTERACTION:
            for i in range(sa.EXPECT[b]):
                xD = np.load(self.w.root / "derivation" / f"{inv.DER_TAG}_{b}_{i}.npz")["xsec_flat"]
                np.savez_compressed(u / f"t_B_{b}_{i}.npz", xsec_flat=xD,
                                    meta=json.dumps({"schema": inv.SCHEMA, "mode": "B", "universe": f"{b}_{i}"}))
        r = self.w.run_i2(self.i0, u)
        self.assertEqual({v["mechanism"] for v in r["attribution"].values()}, {"H1"})
        self.assertEqual(r["headline"]["headline"], "H1")

    def test_controls_refuse(self):
        for tamper, msg in ((("cv", "B"), "bitwise"), (("meta", "C"), "not mode")):
            shutil.rmtree(self.tmp / "unf", ignore_errors=True)
            with self.assertRaisesRegex(fs.Invalid, msg):
                self.w.run_i2(self.i0, self.w.write_modes(tamper=tamper))
        with self.assertRaisesRegex(fs.Invalid, "interaction cells outside"):
            self.w.run_i2(self.i0, self.w.write_modes(), n_out=99)

    def test_i2_waits_for_i1_when_i0_sent_the_run_there(self):
        r0 = json.loads(self.i0.read_text())
        r0["H2"]["next"] = "I1"
        self.i0.write_text(json.dumps(r0))
        with self.assertRaisesRegex(inv.Refusal, "needs I1"):
            self.w.run_i2(self.i0, self.w.write_modes())
        i1 = self.tmp / "i1.json"
        i1.write_text(json.dumps({"H2": {"verdict": "SUPPORTED"}}))
        with self.assertRaisesRegex(inv.Refusal, "does not run"):
            self.w.run_i2(self.i0, self.w.write_modes(), i1=i1)


# ----------------------------------------------------------------------------------------------- O_NOATIME reads


class NoAtime(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="fd1b-inv-io-"))

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_absent_flag_refuses_rather_than_read_plainly(self):
        p = self.tmp / "a"
        p.write_bytes(b"x")
        with mock.patch.object(inv, "NOATIME_FLAG", None), self.assertRaisesRegex(inv.Refusal, "O_NOATIME"):
            inv.sha256_noatime(p)

    def test_eperm_is_raised_not_retried_plainly(self):
        p = self.tmp / "a"
        p.write_bytes(b"x")
        with plain_noatime(), mock.patch.object(inv.os, "open", side_effect=PermissionError(1, "EPERM")), \
                self.assertRaises(PermissionError):
            inv.sha256_noatime(p)

    def test_loaders_equal_the_path_loaders(self):
        w = ToyWorld(self.tmp)
        with plain_noatime():
            a, b = inv.load_inputs(w.inputs), s5c_unfold.load_inputs(w.inputs)
            self.assertEqual(sorted(a), sorted(b))
            for k in a:
                if k == "edges":
                    for x, y in zip(a[k], b[k]):
                        np.testing.assert_array_equal(x, y)
                else:
                    np.testing.assert_array_equal(a[k], b[k])
            p = w.bank / "MaRES_0_wt.npy"
            x = np.load(p)
            x[3] = np.nan
            np.save(p, x)
            for mode in ("zero", "keep"):
                mine, ref = inv.universe_weights(w.bank, "MaRES_0", mode), s5p_universe.weights(w.bank, "MaRES_0", mode)
                for k in ref:
                    np.testing.assert_array_equal(mine[k], ref[k])
            self.assertEqual(inv.sha256_noatime(w.inputs), digest(w.inputs))

    def test_stage_copies_verifies_and_lists_missing(self):
        src = self.tmp / "s.bin"
        src.write_bytes(os.urandom(5000))
        with plain_noatime():
            rec = inv.stage([{"role": "r", "src": str(src), "dest": "d/s.bin", "sha256": digest(src)},
                             {"role": "gone", "src": str(self.tmp / "nope"), "dest": "n"}], self.tmp / "out")
        self.assertEqual((self.tmp / "out/d/s.bin").read_bytes(), src.read_bytes())
        self.assertEqual(rec["missing"], [{"role": "gone", "src": str(self.tmp / "nope")}])
        with plain_noatime(), self.assertRaisesRegex(inv.Refusal, "declared"):
            inv.stage([{"role": "r", "src": str(src), "dest": "e", "sha256": "0" * 64}], self.tmp / "out2")

    def test_stage_refuses_a_source_whose_atime_moved(self):
        src = self.tmp / "s.bin"
        src.write_bytes(b"abc" * 100)
        real = inv.open_noatime

        def touching(path):
            fh = real(path)
            os.utime(path, ns=(os.stat(path).st_atime_ns + 10 ** 9, os.stat(path).st_mtime_ns))
            return fh

        with plain_noatime(), mock.patch.object(inv, "open_noatime", touching), \
                self.assertRaisesRegex(inv.Refusal, "atime"):
            inv.stage([{"role": "r", "src": str(src), "dest": "s.bin"}], self.tmp / "out")


if __name__ == "__main__":
    unittest.main()


class CallGraph(unittest.TestCase):
    """Review M4: run the composed unfold path and stage on fixtures and fail if any input is opened by anything but
    open_noatime (os.open with the flag). The flag is a sentinel bit the os.open wrapper strips."""
    SENTINEL = 1 << 29

    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="fd1b-inv-cg-"))
        cls.w = ToyWorld(cls.tmp)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def instrument(self):
        import builtins
        import io
        rec = {"os": [], "plain": []}
        real_os, real_b, real_io = os.open, builtins.open, io.open

        def os_open(path, flags, *a, **k):
            rec["os"].append((str(path), bool(flags & self.SENTINEL)))
            return real_os(path, flags & ~self.SENTINEL, *a, **k)

        def plain(file, mode="r", *a, **k):
            if isinstance(file, (str, os.PathLike)) and "r" in mode:
                rec["plain"].append(str(file))
            return real_b(file, mode, *a, **k)

        def plain_io(file, mode="r", *a, **k):
            if isinstance(file, (str, os.PathLike)) and "r" in mode:
                rec["plain"].append(str(file))
            return real_io(file, mode, *a, **k)

        ps = [mock.patch.object(inv, "NOATIME_FLAG", self.SENTINEL), mock.patch.object(os, "open", os_open),
              mock.patch.object(builtins, "open", plain), mock.patch.object(io, "open", plain_io)]
        return rec, ps

    def inputs(self):
        w = self.w
        return {str(p) for p in [w.inputs, w.bkg, w.pins, *w.bank.iterdir(), *w.det.iterdir()]}

    def run_with(self, fn):
        rec, ps = self.instrument()
        for p in self.w.patches() + ps:
            p.start()
        try:
            fn()
        finally:
            mock.patch.stopall()
        return rec

    def test_the_unfold_path_opens_every_input_with_o_noatime(self):
        out = self.tmp / "u"
        pins_sha = digest(self.w.pins)  # outside the instrument: the test's own read is not the code's

        def go():
            with mock.patch.object(s5n_pseudo, "unfold_negweight", fake_unfold):
                for mode, us in (("B", "CV,MaRES_0"), ("C", "LowQ2_1"), ("A", "CV")):
                    argv = ["unfold", "--mode", mode, "--universes", us, "--npz", str(self.w.inputs), "--bkg",
                            str(self.w.bkg), "--bank", str(self.w.bank), "--detector-dir", str(self.w.det), "--pins",
                            str(self.w.pins), "--expect-pins-sha256", pins_sha, "--out", str(out)]
                    self.assertEqual(inv.main(argv), 0)
        rec = self.run_with(go)
        ins = self.inputs()
        opened = {p for p, _ in rec["os"] if p in ins}
        # the instrument must see the reads it guards: the inputs, the background, the pins, the CV bank file and a
        # universe's weights were all opened
        for must in (self.w.inputs, self.w.bkg, self.w.pins, self.w.bank / "cv.npz", self.w.bank / "MaRES_0_wr.npy"):
            self.assertIn(str(must), opened)
        self.assertEqual([p for p in rec["plain"] if p in ins], [])
        self.assertEqual([p for p, flag in rec["os"] if p in ins and not flag], [])
        side = list(out.glob("atime-*.json"))
        self.assertTrue(side)
        self.assertEqual(json.loads(side[0].read_text())["moved"], [])

    def test_stage_opens_its_sources_with_o_noatime(self):
        def go():
            inv.stage([{"role": "r", "src": str(self.w.inputs), "dest": "i.npz"}], self.tmp / "st")
        rec = self.run_with(go)
        self.assertIn((str(self.w.inputs), True), rec["os"])
        self.assertNotIn(str(self.w.inputs), rec["plain"])

    def test_positive_control_the_instrument_sees_a_plain_read(self):
        rec = self.run_with(lambda: s5p_universe.weights(self.w.bank, "MaRES_0", "keep"))
        self.assertIn(str(self.w.bank / "MaRES_0_wt.npy"), rec["plain"] + [p for p, f in rec["os"] if not f])
