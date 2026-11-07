#!/usr/bin/env python3
"""Tests for per_period_benchmark.py (DECLARATION.md section 9). Every control is tested in both directions.

The fixture world is the publication's own rounded TEXT release in 2d-unfolding/minerva_paper_anc/ (cross section and
TotalCovariance on the 205 StatOnly cells), so the conditioning is the real one. Expected values are built from the
declared formulas in this file, never from the script's outputs. Without PyROOT a stub `ROOT` module is installed:
nothing tested here calls ROOT (load_all is exercised on the cluster by the ROOT receipt).

Run: python3 -B -m unittest test_per_period_benchmark  (from this directory). BLAS is pinned to one thread below,
before numpy loads: the suite's many small products ran 50x slower under thread oversubscription.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"
import importlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import sys  # noqa: E402
import tempfile  # noqa: E402
import types  # noqa: E402
import unittest  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
try:
    import ROOT  # noqa: F401
    HAVE_ROOT = True
except ImportError:
    sys.modules["ROOT"] = types.ModuleType("ROOT")
    HAVE_ROOT = False

P = importlib.import_module("per_period_benchmark")
M = P.import_reused()
ANC = P.REPO / "2d-unfolding/minerva_paper_anc"


def _load_txt_cov(kind):
    m = np.zeros((224, 224))
    with open(ANC / f"cov_ptpl_minerva_inclusive_6GeV_{kind}.txt") as fh:
        next(fh)
        for line in fh:
            if line.strip():
                i, j, v = line.split(",")
                m[int(i), int(j)] = float(v)
    return m


def _load_txt_xsec():
    v = np.zeros(224)
    with open(ANC / "data_result_ptpl_2D_minerva_inclusive_6GeV.txt") as fh:
        next(fh)
        for line in fh:
            if line.strip():
                pz, pt, xs = line.split(",")[:3]
                v[(int(pt) - 1) * 16 + (int(pz) - 1)] = float(xs)
    return v


TOT, STAT, P224 = _load_txt_cov("total"), _load_txt_cov("stat"), _load_txt_xsec()
MASK = np.diag(STAT) > 0
CELLS = np.flatnonzero(MASK)
PRED = P224[MASK]
V = TOT[np.ix_(MASK, MASK)]
LAM, U = np.linalg.eigh(V)
PZ_E = np.array([1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0, 40.0, 60.0])
PT_E = np.array([0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55, 0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50])
IPT, IPZ = CELLS // 16, CELLS % 16
HI_CELLS = (PZ_E[IPZ] >= 8.0) & (PZ_E[IPZ + 1] <= 15.0)
SHARES = {X: json.loads(P.PARTC_ANALYSIS.read_text())["exposure_share_by_pt_row"][X] for X in P.GROUPS}  # full precision


def quad_matrix(d, idx):
    """Independent form of S_K: d^T (U_K diag(1/lam_K) U_K^T) d."""
    A = U[:, idx] @ np.diag(1.0 / LAM[idx]) @ U[:, idx].T
    return float(d @ A @ d)


def group(x, eps, seed):
    rng = np.random.default_rng(seed)
    return {"x": x, "seed": x * (1 + eps * rng.standard_normal(x.size)),
            "reps": [x * (1 + eps * rng.standard_normal(x.size)) for _ in range(P.N_REPLICAS)]}


class TestImports(unittest.TestCase):
    def test_reused_modules_resolve_in_repo(self):
        root = os.path.realpath(P.REPO)
        for k in vars(M):
            self.assertTrue(os.path.realpath(getattr(M, k).__file__).startswith(root + os.sep), k)
        self.assertIs(M.analyze_periods.C, M.common)

    def test_provenance_fires_on_foreign_module(self):
        fake = types.ModuleType("common")
        fake.__file__ = "/pscratch/sd/j/josephrb/elsewhere/common.py"
        mods = dict(vars(M), common=fake)
        with self.assertRaises(P.Refused):
            P.check_provenance(mods, M.analyze_periods)

    def test_provenance_fires_on_foreign_module_only_the_path_check_sees(self):
        fake = types.ModuleType("compare_to_paper_fullcov")             # the `common` binding stays the repo's
        fake.__file__ = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/compare_to_paper_fullcov.py"
        with self.assertRaises(P.Refused):
            P.check_provenance(dict(vars(M), compare_to_paper_fullcov=fake), M.analyze_periods)
        P.check_provenance(dict(vars(M)), M.analyze_periods)            # silent on the real set

    def test_provenance_fires_when_analyze_periods_binds_another_common(self):
        ap = types.SimpleNamespace(C=types.ModuleType("other"))
        with self.assertRaises(P.Refused):
            P.check_provenance(dict(vars(M)), ap)

    def test_cluster_path_removed(self):
        self.assertNotIn(M.periods.COVERAGE_SCRIPTS, sys.path)


class TestDigests(unittest.TestCase):
    def test_inputs_file_has_39_distinct_operands(self):
        rows = P.read_inputs()
        self.assertEqual(len(rows), 39)
        self.assertEqual(rows[1][0], "a5c13fc38d64242bc9ee459fac87568a2f97fddf7a3ac97cc6f91eb4c2a31cef")

    def test_inputs_file_refused_when_short_or_malformed(self):
        rows = P.INPUTS.read_text().splitlines()
        with tempfile.TemporaryDirectory() as t:
            short = Path(t) / "short"
            short.write_text("\n".join(rows[:38]) + "\n")
            with self.assertRaises(P.Refused):
                P.read_inputs(short)
            bad = Path(t) / "bad"
            bad.write_text("\n".join(["XYZ" + rows[0][3:]] + rows[1:]) + "\n")
            with self.assertRaises(P.Refused):
                P.read_inputs(bad)

    def _fixture(self, t):
        rows = []
        for i, src in enumerate(["/x/cov_ptpl_minerva_inclusive_6GeV.root", "/x/ER/xsec.root", "/x/pu_PA_b01/xsec.root"]):
            dst = Path(t) / P.copy_name(src)
            dst.write_bytes(bytes([i]) * 1000)
            rows.append((P.sha256(dst), src))
        return rows

    def test_verify_silent_on_true_copies(self):
        with tempfile.TemporaryDirectory() as t:
            rec = P.verify_copies(t, self._fixture(t))
            self.assertEqual(rec["verdict"], "PASS")
            self.assertTrue(all(f["equal"] for f in rec["files"]))

    def test_verify_fires_on_one_flipped_byte(self):
        with tempfile.TemporaryDirectory() as t:
            rows = self._fixture(t)
            f = Path(t) / P.copy_name(rows[2][1])
            b = bytearray(f.read_bytes())
            b[500] ^= 1
            f.write_bytes(bytes(b))
            rec = P.verify_copies(t, rows)
            self.assertEqual(rec["verdict"], "REFUSE")
            self.assertEqual(rec["refused"], [rows[2][1]])
            bad = [x for x in rec["files"] if not x["equal"]][0]
            self.assertNotEqual(bad["declared"], bad["measured"])   # both values are in the record

    def test_verify_fires_on_missing_copy(self):
        with tempfile.TemporaryDirectory() as t:
            rows = self._fixture(t)
            (Path(t) / P.copy_name(rows[0][1])).unlink()
            self.assertEqual(P.verify_copies(t, rows)["verdict"], "REFUSE")

    def test_noatime_copy(self):
        with tempfile.TemporaryDirectory() as t:
            src, dst = Path(t) / "a", Path(t) / "b"
            src.write_bytes(b"abc" * 100)
            if getattr(os, "O_NOATIME", None) is None:
                with self.assertRaises(P.Refused):
                    P.noatime_copy(src, dst)
            else:
                P.noatime_copy(src, dst)
                self.assertEqual(src.read_bytes(), dst.read_bytes())
                with self.assertRaises(FileExistsError):     # never overwrites
                    P.noatime_copy(src, dst)

    def test_copy_names_unique(self):
        names = [P.copy_name(s) for _, s in P.read_inputs()]
        self.assertEqual(len(set(names)), 39)

    def test_main_refusal_exit_is_not_python_crash_exit(self):
        with tempfile.TemporaryDirectory() as t:
            rc = P.main(["verify", "--dest", t])
        self.assertEqual(rc, P.EXIT_REFUSE)
        self.assertNotEqual(P.EXIT_REFUSE, 1)
        self.assertNotEqual(P.EXIT_STOP, 1)


class TestRoles(unittest.TestCase):
    def test_roles_from_declared_inputs(self):
        r = P.roles_of(P.read_inputs(), "/d")
        self.assertEqual(r["E_R"], "/d/ER__xsec.root")
        self.assertEqual(r["CTRL"], "/d/pu_CTRL_s42__xsec.root")
        for g in P.GROUPS:
            self.assertEqual(sorted(r["groups"][g]["boot"]), list(range(1, 11)))
            self.assertTrue(r["groups"][g]["s43"].endswith(f"pu_{g}_s43__xsec.root"))

    def test_roles_refused_when_a_replica_is_missing(self):
        rows = [x for x in P.read_inputs() if "pu_PB_b07" not in x[1]]
        with self.assertRaises(P.Refused):
            P.roles_of(rows, "/d")


class TestAlgebra(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(7)
        self.d = PRED * 0.03 * rng.standard_normal(PRED.size)

    def test_eigen_sum_equals_chi2_with_cov(self):
        full = M.compare_to_paper_fullcov.chi2_with_cov(np.where(MASK, 0.0, 0.0) + self._d224(), TOT, "t", report=False)[0]
        s = P.quad(self.d, LAM, U, np.arange(PRED.size))
        self.assertLess(abs(s - full) / full, 1e-6)

    def _d224(self):
        d = np.zeros(224)
        d[MASK] = self.d
        return d

    def test_quad_equals_matrix_form_on_k73(self):
        idx = P.top_modes(LAM, 73)
        self.assertEqual(len(idx), 73)
        self.assertTrue(np.all(LAM[idx] >= np.sort(LAM)[-73]))
        self.assertAlmostEqual(P.quad(self.d, LAM, U, idx) / quad_matrix(self.d, idx), 1.0, places=9)

    def test_complement_partitions(self):
        idx = P.top_modes(LAM, 73)
        bar = P.complement(PRED.size, idx)
        self.assertEqual(len(bar), 132)
        s = P.quad(self.d, LAM, U, idx) + P.quad(self.d, LAM, U, bar)
        self.assertAlmostEqual(s / P.quad(self.d, LAM, U, np.arange(205)), 1.0, places=9)

    def test_noise_var_models(self):
        fr, f0, fs = [1.1, 0.9, 1.3], 1.0, 1.2
        v_rep = float(np.sum((np.array(fr) - 1.1) ** 2) / 2)          # centred on the replica mean, ddof 1
        self.assertAlmostEqual(P.noise_var(fr, f0, fs, "replica"), v_rep, places=12)
        self.assertAlmostEqual(P.noise_var(fr, f0, fs, "replica+seed"), v_rep + 0.04 / 2, places=12)
        with self.assertRaises(ValueError):
            P.noise_var(fr, f0, fs, "135")

    def test_distance_debias(self):
        g = group(PRED + self.d, 0.01, 3)
        idx = P.top_modes(LAM, 73)
        r = P.distance(g, PRED, (LAM, U), idx, "replica+seed")
        xb = np.mean(g["reps"], axis=0)
        n = (sum(quad_matrix(x - xb, idx) for x in g["reps"]) / 9 + quad_matrix(g["seed"] - g["x"], idx) / 2) / 73
        self.assertAlmostEqual(r["T"], quad_matrix(self.d, idx) / 73, delta=1e-9 * r["T"])
        self.assertAlmostEqual(r["n"], n, delta=1e-9 * n)
        self.assertAlmostEqual(r["T_debiased"], r["T"] - r["n"], places=12)

    def _mc_noise(self, regime, model, n_mc=300, sb=1.0, ss=1.0):
        """Mean of noise_term over n_mc synthetic fits whose true noise of x is sb^2 + ss^2 per mode (on K73).

        regime "fixed": the seed's effect is the same in every replica (x_r = mu + b_r + s_0);
        regime "fresh": it re-randomizes with the data (x_r = mu + b_r + s_r)."""
        idx = P.top_modes(LAM, 73)
        rng = np.random.default_rng(101)
        B = U[:, idx] * np.sqrt(LAM[idx])
        draw = lambda sc: B @ (sc * rng.standard_normal(73))  # noqa: E731
        mu = PRED
        vals = []
        for _ in range(n_mc):
            s0, s1 = draw(ss), draw(ss)
            reps = [mu + draw(sb) + (s0 if regime == "fixed" else draw(ss)) for _ in range(P.N_REPLICAS)]
            g = {"x": mu + s0, "seed": mu + s1, "reps": reps}
            vals.append(P.noise_term(g, (LAM, U), idx, model))
        return float(np.mean(vals)), float(np.std(vals, ddof=1) / math.sqrt(n_mc))

    def test_n1_seed_term_is_unbiased_when_the_seed_is_fixed_in_replicas(self):
        mean, se = self._mc_noise("fixed", "replica+seed")
        self.assertLess(abs(mean - 2.0), max(4 * se, 0.05))           # truth sb^2 + ss^2 = 2
        self.assertLess(4 * se, 0.5)                                    # the undivided term would give 3

    def test_n1_replica_model_is_unbiased_when_the_seed_rerandomizes(self):
        mean, se = self._mc_noise("fresh", "replica")
        self.assertLess(abs(mean - 2.0), max(4 * se, 0.05))           # centring on x (#135) would give 3
        self.assertLess(4 * se, 0.5)

    def test_n1_each_model_is_biased_in_the_other_regime(self):
        """Why the classes are read only where both models agree: neither model is right in both regimes."""
        m1, _ = self._mc_noise("fresh", "replica+seed")
        m2, _ = self._mc_noise("fixed", "replica")
        self.assertGreater(m1, 2.5)
        self.assertLess(m2, 1.5)

    def test_zscore_edges(self):
        self.assertEqual(P.zscore(0.0, 0.0), 0.0)
        self.assertEqual(P.zscore(1.0, 0.0), math.inf)
        self.assertEqual(P.zscore(-1.0, 0.0), -math.inf)
        self.assertEqual(P.zscore(3.0, 1.5), 2.0)

    def test_exposure_weights(self):
        w = P.exposure_weights(SHARES, CELLS, 16, ("PA", "PC"))
        self.assertAlmostEqual(float(w["PA"][0]), SHARES["PA"][0] / (SHARES["PA"][0] + SHARES["PC"][0]), places=14)
        self.assertLess(float(np.max(np.abs(w["PA"] + w["PC"] - 1))), 1e-15)
        w3 = P.exposure_weights(SHARES, CELLS, 16, P.GROUPS)
        self.assertAlmostEqual(float(w3["PB"][5]), SHARES["PB"][5], places=14)          # full shares sum to 1

    def test_combine_indexwise(self):
        gs = {X: group(PRED * (1 + 0.01 * i), 0.01, 10 + i) for i, X in enumerate(P.GROUPS)}
        w = P.exposure_weights(SHARES, CELLS, 16, P.GROUPS)
        c = P.combine(gs, w)
        r = 4
        want = sum(w[X] * gs[X]["reps"][r] for X in P.GROUPS)
        self.assertTrue(np.array_equal(c["reps"][r], want))
        self.assertTrue(np.array_equal(c["seed"], sum(w[X] * gs[X]["seed"] for X in P.GROUPS)))
        self.assertTrue(np.array_equal(c["x"], sum(w[X] * gs[X]["x"] for X in P.GROUPS)))
        gs["PC"]["reps"] = gs["PC"]["reps"][:9]
        with self.assertRaises(P.Refused):
            P.combine(gs, w)


class TestControls(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(11)
        self.d = PRED * 0.03 * rng.standard_normal(PRED.size)

    def test_c_pub(self):
        d224 = np.zeros(224)
        d224[MASK] = self.d
        chi = M.compare_to_paper_fullcov.chi2_with_cov(d224, TOT, "t", report=False)[0]
        self.assertEqual(P.ctl_pub(chi, want=chi)["verdict"], "PASS")
        self.assertEqual(P.ctl_pub(chi * (1 + 3e-8), want=chi)["verdict"], "FAIL")
        self.assertEqual(P.ctl_pub(chi * (1 + 5e-9), want=chi)["verdict"], "PASS")

    def test_c_sum(self):
        all_ = np.arange(205)
        s = P.quad(self.d, LAM, U, all_)
        self.assertEqual(P.ctl_sum(s, s * (1 + 5e-7))["verdict"], "PASS")
        self.assertEqual(P.ctl_sum(s * (1 + 5e-6), s)["verdict"], "FAIL")
        top = int(np.argmax([P.quad(self.d, LAM, U, [i]) for i in all_]))
        s204 = P.quad(self.d, LAM, U, np.delete(all_, top))
        self.assertEqual(P.ctl_sum(s204, s)["verdict"], "FAIL")

    def test_c_k(self):
        self.assertEqual(int(np.sum(LAM > 1e-4 * LAM.max())), 73)     # the text release, measured
        s73 = 0.662 * 205
        self.assertEqual(P.ctl_k(LAM, s73, 205)["verdict"], "PASS")
        self.assertEqual(P.ctl_k(LAM, s73, 205, want_k=72)["verdict"], "FAIL")
        self.assertEqual(P.ctl_k(LAM, s73 + 0.001 * 205, 205)["verdict"], "FAIL")
        self.assertEqual(P.ctl_k(LAM, s73 + 0.0004 * 205, 205)["verdict"], "PASS")

    def _expect(self, d):
        lm = LAM.max()
        return {r: (f"{LAM[r] / lm:.3e}", round(abs(float(U[:, r] @ d) / math.sqrt(LAM[r])), 2))
                for r in (23, 9, 118, 2, 79, 121)}

    def test_c_m_silent_on_true_modes(self):
        self.assertEqual(P.ctl_modes(LAM, U, self.d, expect=self._expect(self.d))["verdict"], "PASS")

    def test_c_m_fires_on_swapped_entries(self):
        e = self._expect(self.d)
        e[118], e[121] = e[121], e[118]
        self.assertEqual(P.ctl_modes(LAM, U, self.d, expect=e)["verdict"], "FAIL")

    def test_c_m_fires_on_rotated_pair(self):
        d = U[:, 118] * 5 * math.sqrt(LAM[118])          # all weight on mode 118
        e = self._expect(d)
        U2 = U.copy()
        c, s = math.cos(math.pi / 4), math.sin(math.pi / 4)
        U2[:, 118], U2[:, 119] = c * U[:, 118] + s * U[:, 119], -s * U[:, 118] + c * U[:, 119]
        self.assertEqual(P.ctl_modes(LAM, U2, d, expect=e)["verdict"], "FAIL")

    def test_c_ctrl(self):
        x = PRED + self.d
        idx73, all_ = P.top_modes(LAM, 73), np.arange(205)
        self.assertEqual(P.ctl_ctrl(x * (1 + 1e-12), x, PRED, (LAM, U), idx73, all_)["verdict"], "PASS")
        y = x.copy()
        y[100] *= 1 + 1e-7
        self.assertEqual(P.ctl_ctrl(y, x, PRED, (LAM, U), idx73, all_)["verdict"], "FAIL")

    def test_c_step(self):
        self.assertEqual(P.ctl_step(P.STEP_PBPA)["verdict"], "PASS")
        self.assertEqual(P.ctl_step(P.STEP_PBPA * (1 + 1e-9))["verdict"], "FAIL")

    def test_c_grad_silent_and_fires_on_off_by_one_range(self):
        met, w_lo, w_hi = P.step_ops(M, CELLS, PRED)
        x = PRED * (1 + 0.05 * HI_CELLS)
        self.assertEqual(P.ctl_grad(M, met, w_lo, w_hi, x, PRED)["verdict"], "PASS")
        w = np.diff(PZ_E)
        hi_plus = ((PZ_E[:-1] >= 8.0) & (PZ_E[1:] <= 20.0)).astype(float)      # one bin too many
        self.assertEqual(P.ctl_grad(M, met, w_lo, (w * hi_plus) @ met.P["pz"], x, PRED)["verdict"], "FAIL")

    def test_c_comb(self):
        area = M.common.area(CELLS)
        w = P.exposure_weights(SHARES, CELLS, 16, P.GROUPS)
        self.assertEqual(P.ctl_comb(w, PRED, PRED * (1 + 1e-3), area)["verdict"], "PASS")
        self.assertEqual(P.ctl_comb(w, PRED * 1.01, PRED, area)["verdict"], "FAIL")
        w_bad = dict(w, PB=w["PB"] * 0.97)
        self.assertEqual(P.ctl_comb(w_bad, PRED, PRED, area)["verdict"], "FAIL")

    def test_c_partc(self):
        rec = P.load_partc()
        self.assertEqual(P.ctl_partc(rec)["verdict"], "PASS")
        bad = json.loads(json.dumps(rec))
        bad["exposure_share_by_pt_row"]["PB"][3] += 1e-3
        self.assertEqual(P.ctl_partc(bad)["verdict"], "FAIL")
        bad = json.loads(json.dumps(rec))
        bad["comparisons"]["raw_PB/PA"]["step"]["value"] += 1e-15
        self.assertEqual(P.ctl_partc(bad)["verdict"], "FAIL")
        bad = json.loads(json.dumps(rec))
        bad["exposure_share_by_pt_row"]["PB"] = [v + 1e-9 for v in bad["exposure_share_by_pt_row"]["PB"]]
        r = P.ctl_partc(bad)                                             # constant rows, within 1e-6, sum != 1
        self.assertEqual(r["verdict"], "FAIL")
        self.assertGreater(r["max_row_sum_dev"], 1e-12)
        bad = json.loads(json.dumps(rec))
        bad["n_boot_pairs"] = 9
        self.assertEqual(P.ctl_partc(bad)["verdict"], "FAIL")

    def test_partc_digest_refused(self):
        with tempfile.TemporaryDirectory() as t:
            f = Path(t) / "a.json"
            f.write_text(P.PARTC_ANALYSIS.read_text() + " ")
            old = P.PARTC_ANALYSIS
            try:
                P.PARTC_ANALYSIS = f
                with self.assertRaises(P.Refused):
                    P.load_partc()
            finally:
                P.PARTC_ANALYSIS = old

    def test_c_in_cells(self):
        x = np.where(MASK, 1.0, 0.0)
        self.assertEqual(P.ctl_cells(M.reported_cells, CELLS, {"a": x})["verdict"], "PASS")
        extra = x.copy()
        extra[np.flatnonzero(~MASK)[0]] = 1e-40
        self.assertEqual(P.ctl_cells(M.reported_cells, CELLS, {"a": x, "b": extra})["verdict"], "FAIL")
        miss = x.copy()
        miss[CELLS[17]] = 0.0
        r = P.ctl_cells(M.reported_cells, CELLS, {"c": miss})
        self.assertEqual(r["verdict"], "FAIL")
        self.assertIn("c", r["mismatches"])


class TestClasses(unittest.TestCase):
    def test_r5_boundaries(self):
        self.assertEqual(P.cls_r5(3.0), "closer without 1G-1M")
        self.assertEqual(P.cls_r5(2.9999), "unresolved")
        self.assertEqual(P.cls_r5(2.5), "unresolved")
        self.assertEqual(P.cls_r5(2.0), "no change")
        self.assertEqual(P.cls_r5(-2.0), "no change")
        self.assertEqual(P.cls_r5(-2.0001), "unresolved")
        self.assertEqual(P.cls_r5(-3.0), "farther without 1G-1M")
        self.assertEqual(P.cls_r5(math.inf), "closer without 1G-1M")

    def test_r4_boundaries(self):
        self.assertEqual(P.cls_r4(-2.0), "matches the published p_par high/low ratio")
        self.assertEqual(P.cls_r4(2.5), "unresolved")
        self.assertEqual(P.cls_r4(-3.0), "differs")

    def test_r3(self):
        self.assertEqual(P.cls_r3({"a": 3.1, "b": 0.0}, False), "group-dependent")
        self.assertEqual(P.cls_r3({"a": 1.9, "b": -2.0}, False), "group-independent at this resolution")
        self.assertEqual(P.cls_r3({"a": 2.5}, False), "unresolved")
        self.assertEqual(P.cls_r3({"a": 9.0}, True), "not resolved by the period groups")

    def test_r2_patterns(self):
        z = {("PB", "PA"): 3.5, ("PB", "PC"): 3.1, ("PC", "PA"): 0.4}
        self.assertEqual(P.cls_r2(z), "PB farther")
        z = {("PB", "PA"): -3.5, ("PB", "PC"): 0.1, ("PC", "PA"): -3.2}
        self.assertEqual(P.cls_r2(z), "PA farther")
        z = {("PB", "PA"): 1.0, ("PB", "PC"): -2.0, ("PC", "PA"): 0.0}
        self.assertEqual(P.cls_r2(z), "no group separates")
        z = {("PB", "PA"): 3.5, ("PB", "PC"): 3.1, ("PC", "PA"): 2.5}      # the other two are not within 2
        self.assertEqual(P.cls_r2(z), "other pattern")
        z = {("PB", "PA"): 3.5, ("PB", "PC"): 2.9, ("PC", "PA"): 0.0}
        self.assertEqual(P.cls_r2(z), "other pattern")

    def test_merge_class(self):
        self.assertEqual(P.merge_class("no change", "no change"), "no change")
        self.assertEqual(P.merge_class("no change", "unresolved"), "unresolved (noise model)")
        self.assertEqual(P.merge_class("closer without 1G-1M", "no change"), "unresolved (noise model)")

    def test_combined_statement(self):
        m, d = "matches the published p_par high/low ratio", "differs"
        c = P.SENTENCE_CLOSER
        self.assertEqual(P.combined_statement("closer without 1G-1M", {"PA": m, "PB": d, "PC": m}),
                         c + " " + P.CLAUSE_R4_SEPARATES)
        self.assertEqual(P.combined_statement("closer without 1G-1M", {"PA": m, "PB": m, "PC": m}),
                         c + " " + P.CLAUSE_R4_WIDE)
        self.assertEqual(P.combined_statement("closer without 1G-1M", {"PA": "unresolved", "PB": d, "PC": m}), c)
        self.assertEqual(P.combined_statement("closer without 1G-1M", {"PA": m, "PB": "unresolved (noise model)",
                                                                       "PC": m}), c)
        self.assertIsNone(P.combined_statement("unresolved (noise model)", {"PA": m, "PB": d, "PC": m}))
        self.assertEqual(P.combined_statement("no change", {"PA": d, "PB": d, "PC": d}), P.SENTENCE_NOCHANGE)
        self.assertIsNone(P.combined_statement("unresolved", {"PA": m, "PB": d, "PC": m}))
        self.assertIsNone(P.combined_statement("farther without 1G-1M", {"PA": m, "PB": d, "PC": m}))


class TestReadingsEndToEnd(unittest.TestCase):
    """Known-answer fixtures through readings(), on the real published covariance."""

    def _er(self):
        rng = np.random.default_rng(5)
        return PRED * (1 + 0.04 * rng.standard_normal(PRED.size))

    def test_identical_groups(self):
        x = self._er()
        g = group(x, 1e-4, 21)
        gs = {X: {"x": g["x"], "seed": g["seed"], "reps": list(g["reps"])} for X in P.GROUPS}
        r = P.readings(M, gs, x, PRED, V, CELLS, SHARES)
        self.assertEqual(r["classes"]["R2"], "no group separates")
        self.assertEqual(r["classes"]["R5"], "no change")
        for md in P.NOISE_MODELS:
            y = r["by_model"][md]
            self.assertTrue(all(v == 0.0 for v in y["R2"]["z"].values()))
            self.assertLess(abs(y["R5"]["delta"]), 1e-9)
            for row in y["R3"].values():
                self.assertTrue(all(v == 0.0 for v in row["delta"].values()))
        for c in r["classes"]["R3"].values():
            self.assertIn(c, ("group-independent at this resolution", "not resolved by the period groups"))
        self.assertEqual(r["combined_statement"], P.SENTENCE_NOCHANGE)

    def _inject(self, a):
        xb = PRED * (1 + a * HI_CELLS)
        gs = {"PA": group(PRED.copy(), 1e-9, 31), "PB": group(xb, 1e-9, 32), "PC": group(PRED.copy(), 1e-9, 33)}
        w = P.exposure_weights(SHARES, CELLS, 16, P.GROUPS)
        x_er = sum(w[X] * gs[X]["x"] for X in P.GROUPS)
        r = P.readings(M, gs, x_er, PRED, V, CELLS, SHARES)
        y = r["by_model"]["replica+seed"]
        # by construction: st_B = a exactly, st_A = st_C = 0, and the A+C combination is the published result
        self.assertAlmostEqual(y["R4"]["PB"]["st"], a, places=12)
        self.assertAlmostEqual(y["R4"]["PA"]["st"], 0.0, places=12)
        self.assertLess(abs(y["R5"]["AC"]["T"]), 1e-9)
        want_abc = quad_matrix(x_er - PRED, P.top_modes(LAM, 73)) / 73
        self.assertAlmostEqual(y["R5"]["ABC"]["T"] / want_abc, 1.0, places=6)
        self.assertEqual(r["classes"]["R5"], "closer without 1G-1M")
        self.assertEqual(r["classes"]["R2"], "PB farther")
        self.assertEqual(r["classes"]["R4"]["PA"], "matches the published p_par high/low ratio")
        return r

    def test_injected_b_only_step_at_7pct(self):
        """A 7% step is inside the published ratio's own uncertainty (sigma_pub ~ 4.3%), so R4 cannot separate."""
        r = self._inject(0.07)
        self.assertEqual(r["classes"]["R4"]["PB"], "matches the published p_par high/low ratio")
        self.assertEqual(r["combined_statement"], P.SENTENCE_CLOSER + " " + P.CLAUSE_R4_WIDE)

    def test_injected_b_only_step_at_20pct(self):
        r = self._inject(0.20)
        self.assertEqual(r["classes"]["R4"]["PB"], "differs")
        self.assertEqual(r["combined_statement"], P.SENTENCE_CLOSER + " " + P.CLAUSE_R4_SEPARATES)

    def test_r4_injection_at_z_2p5_reads_unresolved(self):
        met, w_lo, w_hi = P.step_ops(M, CELLS, PRED)
        # independent gradient factor G: sigma_pub = (1 + st) G
        area_w = np.diff(PZ_E)[IPZ] * np.diff(PT_E)[IPT]
        lo = (PZ_E[IPZ] >= 1.5) & (PZ_E[IPZ + 1] <= 8.0)
        h = area_w * HI_CELLS / float(area_w[HI_CELLS] @ PRED[HI_CELLS]) - area_w * lo / float(area_w[lo] @ PRED[lo])
        G = math.sqrt(float(h @ V @ h))
        self.assertLess(2.5 * G, 1.0)
        a = 2.5 * G / (1 - 2.5 * G)
        x = PRED * (1 + a * HI_CELLS)
        st = P.step_value(M, met, x, PRED)
        self.assertAlmostEqual(st, a, places=12)
        z = P.zscore(st, math.hypot(P.noise_sigma(lambda y: P.step_value(M, met, y, PRED), x, [x] * 10, x,
                                                  "replica+seed"),
                                    P.step_sigma_pub(st, w_lo, w_hi, PRED, V)))
        self.assertAlmostEqual(z, 2.5, places=9)
        self.assertEqual(P.cls_r4(z), "unresolved")

    def test_r5_sigma_is_the_paired_difference(self):
        rng = np.random.default_rng(41)
        gs = {X: group(PRED * (1 + 0.03 * rng.standard_normal(PRED.size)), 0.002, 50 + i)
              for i, X in enumerate(P.GROUPS)}
        y = P.readings_one(M, gs, gs["PA"]["x"], PRED, V, CELLS, SHARES, "replica+seed")
        idx = P.top_modes(LAM, 73)
        wa = P.exposure_weights(SHARES, CELLS, 16, P.GROUPS)
        wc = P.exposure_weights(SHARES, CELLS, 16, ("PA", "PC"))
        T = lambda x: quad_matrix(x - PRED, idx) / 73  # noqa: E731
        comb = lambda w, key, r=None: sum(w[X] * (gs[X][key] if r is None else gs[X][key][r]) for X in w)  # noqa: E731
        f = [T(comb(wa, "reps", r)) - T(comb(wc, "reps", r)) for r in range(10)]
        f0 = T(comb(wa, "x")) - T(comb(wc, "x"))
        fs = T(comb(wa, "seed")) - T(comb(wc, "seed"))
        want = math.sqrt(float(np.var(f, ddof=1)) + (fs - f0) ** 2 / 2)
        self.assertAlmostEqual(y["R5"]["sigma"] / want, 1.0, places=7)

    def test_r4_ratio_identity(self):
        """(1 + st_B)/(1 + st_A) - 1 equals step_stat(x_B, x_A): the published result cancels (C-STEP's basis)."""
        met, _, _ = P.step_ops(M, CELLS, PRED)
        rng = np.random.default_rng(9)
        xa = PRED * (1 + 0.02 * rng.standard_normal(PRED.size))
        xb = PRED * (1 + 0.06 * HI_CELLS + 0.02 * rng.standard_normal(PRED.size))
        sa, sb = P.step_value(M, met, xa, PRED), P.step_value(M, met, xb, PRED)
        self.assertAlmostEqual((1 + sb) / (1 + sa) - 1, P.step_value(M, met, xb, xa), places=13)


if __name__ == "__main__":
    unittest.main()
