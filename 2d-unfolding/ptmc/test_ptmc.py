"""PTMC's tests (PTMC-DECLARATION.md). The pure tests need numpy only; the ROOT tests need PyROOT, LightGBM and
scikit-learn. The deploy tree is built once by make_tree.sh (archive mode) from this checkout's M.

  PTMC_PY=/path/python OMP_NUM_THREADS=1 python -B -m pytest -q -p no:cacheprovider test_ptmc.py
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
import ptmc_lib as P  # noqa: E402

try:
    import ROOT  # noqa: F401
    import lightgbm  # noqa: F401
    import sklearn  # noqa: F401
    HAVE_ROOT = True
except Exception:  # pragma: no cover
    HAVE_ROOT = False

PT = [0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55, 0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50]
PZ = [1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 6, 7, 8, 9, 10, 15, 20, 40, 60]
TD = Path(tempfile.mkdtemp(prefix="ptmc-test-"))
_TREE = {}


# --------------------------------------------------------------------------------------------- pure tests


class Draws(unittest.TestCase):
    def setUp(self):
        self.b, self.n_data, self.n_entries = 7, 50, 40
        self.app = np.array([3, 9, 11, 30], np.int64)
        self.inj = np.array([0, 1, 2, 5, 8], np.int64)
        rng = np.random.default_rng(1)
        self.n_orig = 60
        n_sig = self.n_orig + self.app.size
        self.wt, self.wr = rng.random(n_sig), rng.random(n_sig)
        self.inj_cv = rng.random(self.inj.size)
        e = P.expected_factors(self.b, self.n_data, self.n_orig, self.n_entries, self.app)
        f = np.concatenate([e["signal"], e["appended"]])
        self.kw = dict(n_data=self.n_data, n_entries=self.n_entries, appended_entry=self.app, inj_entries=self.inj,
                       inj_cv=self.inj_cv, w_truth_cv=self.wt, w_reco_cv=self.wr,
                       signed_w=np.concatenate([e["data"], -(self.inj_cv * e["bkg"][self.inj])]),
                       w_truth_seen=self.wt * f, w_reco_seen=self.wr * f)

    def test_expected_factors_are_the_drivers_streams(self):
        e = P.expected_factors(self.b, self.n_data, self.n_orig, self.n_entries, self.app)
        np.testing.assert_array_equal(e["data"], np.random.default_rng(7).poisson(1.0, 50).astype(float))
        np.testing.assert_array_equal(e["signal"], np.random.default_rng(7 + 10_000_000).poisson(1.0, 60))
        bkg = np.random.default_rng(7 + 20_000_000).poisson(1.0, 40)
        np.testing.assert_array_equal(e["bkg"], bkg)
        np.testing.assert_array_equal(e["appended"], bkg[self.app])

    def test_draw_check_passes_and_catches_each_defect(self):
        self.assertTrue(P.draw_check(self.b, **self.kw)["pass"])
        perm = dict(self.kw, w_truth_seen=self.kw["w_truth_seen"][::-1])  # a row permutation, same sum
        self.assertFalse(P.draw_check(self.b, **perm)["pass"])
        appended_from_signal = dict(self.kw)
        e = P.expected_factors(self.b, self.n_data, self.n_orig + self.app.size, self.n_entries, [])
        appended_from_signal["w_truth_seen"] = self.wt * e["signal"]
        self.assertFalse(P.draw_check(self.b, **appended_from_signal)["pass"])
        wrong_seed = dict(self.kw)
        self.assertFalse(P.draw_check(self.b + 1, **wrong_seed)["pass"])
        short = dict(self.kw, signed_w=self.kw["signed_w"][:-1])
        self.assertFalse(P.draw_check(self.b, **short)["pass"])

    def test_central_has_unit_factors(self):
        kw = dict(self.kw, signed_w=np.concatenate([np.ones(self.n_data), -self.inj_cv]),
                  w_truth_seen=self.wt.copy(), w_reco_seen=self.wr.copy())
        self.assertTrue(P.draw_check(None, **kw)["pass"])

    def test_injected_entries_closed_rectangle(self):
        rows = {"entry": np.arange(6), "pt": np.array([0, 4.5, 4.6, 1, 1, 1.0]),
                "pz": np.array([1.5, 60, 2, 1.4, 60.0, 5])}
        np.testing.assert_array_equal(P.injected_entries(rows, 0, 4.5, 1.5, 60), [0, 1, 4, 5])


class Completeness(unittest.TestCase):
    def test_reduces_to_c_cv_with_nothing_moved_and_handles_cells(self):
        t_orig = np.array([10.0, 5, 0, 3, 0])
        d = np.array([10.0, 5, 0, 3, 0])
        t_all = t_orig + np.array([0, 2.0, 1.0, 0, 0])  # cell 2: moved weight on a structural zero
        c_cv = np.divide(t_all, d, out=np.zeros(5), where=d != 0)
        t_star_orig = np.array([12.0, 4, 0, 3, 0])
        r = P.c_star(t_star_orig + np.array([0, 2.5, 3.0, 0, 0]), t_star_orig, t_orig, d, c_cv)
        self.assertEqual(r["n_lost_support"], 0)
        np.testing.assert_allclose(r["c_star"][[0, 3]], [1.0, 1.0], rtol=1e-15)  # nothing moved: c_CV
        self.assertAlmostEqual(r["c_star"][1], (4 + 2.5) / (5 * 4 / 5))
        self.assertEqual(r["c_star"][2], 0.0)  # structural zero keeps ROOT's 0
        self.assertEqual(r["n_keep_cv"], 2)

    def test_lost_support_gives_zero(self):
        r = P.c_star([1.0], [0.0], [2.0], [2.0], [1.0])
        self.assertEqual(r["n_lost_support"], 1)
        self.assertEqual(r["c_star"][0], 0.0)

    def test_one_sided_and_negative_are_not_finite(self):
        """codex r1 #15: T_orig,CV = 0 with D_CV = 2 is a STOP (section 2.2's table), as is a negative operand."""
        self.assertFalse(P.c_star([1.0], [1.0], [0.0], [2.0], [0.5])["finite"])
        self.assertFalse(P.c_star([1.0], [1.0], [2.0], [0.0], [0.0])["finite"])
        self.assertFalse(P.c_star([1.0], [1.0], [-2.0], [2.0], [0.5])["finite"])
        # a negative operand that trips no other rule: T*_all < 0 would give a finite, negative c* (pre-flight mutant)
        self.assertFalse(P.c_star([-1.0], [1.0], [2.0], [2.0], [0.5])["finite"])
        self.assertFalse(P.coupling_exact([0], [.1], [2.], [-1.0], [0], [.1], [2.], [-1.0])["pass"])

    def test_a_live_denominator_must_be_finite_and_positive(self):
        """Confirm read B10: a live cell whose D* underflows to 0 or overflows to inf would give a finite c* (0); it
        fails instead."""
        under = P.c_star([1.0], [1e-200], [1e200], [1e-200], [0.5])
        self.assertFalse(under["live_denominators_ok"])
        self.assertFalse(under["finite"])
        over = P.c_star([1.0], [1e200], [1e-200], [1e200], [0.5])
        self.assertFalse(over["finite"])
        self.assertTrue(P.c_star([1.0], [1.0], [2.0], [2.0], [0.5])["finite"])

    def test_coupling(self):
        self.assertTrue(P.coupling([1.0, 0, 2], [1.0, 0, 2])["pass"])
        self.assertFalse(P.coupling([1.0, 1e-3], [1.0, 0])["pass"])  # one-sided
        self.assertFalse(P.coupling([1.0], [1.0 + 1e-6])["pass"])
        self.assertFalse(P.coupling([np.nan], [1.0])["pass"])

    def test_support(self):
        g = np.array([0, 0, 1, 2, 2])
        w = np.ones(5)
        m = np.array([1, 1, 1, 1, 0], bool)
        r = P.support(g, w, m, 4, range(1, 30), n=3)
        want = {}
        for b in range(1, 30):  # the expectation, drawn as the driver draws the original rows
            f = np.random.default_rng(b + 10_000_000).poisson(1.0, 4)
            t = np.bincount(g[:4], weights=f.astype(float), minlength=3)
            lost = [j for j in range(3) if t[j] == 0]
            if lost:
                want[b] = lost
        self.assertTrue(want)
        self.assertEqual(r["failures"], want)
        self.assertEqual(r["n_seed_cells"], sum(len(v) for v in want.values()))
        self.assertFalse(P.support(g, w, np.ones(5, bool), 4, [1], n=3)["pass"])  # the mask must end at n_orig
        # the trigger is the weighted sum: a zero-weight row drawing a positive factor does not keep a cell supported
        gz, wz = np.array([0, 0]), np.array([0.0, 1.0])
        lost = {b: [0] for b in range(1, 40)
                if np.random.default_rng(b + 10_000_000).poisson(1.0, 2)[1] == 0}
        self.assertTrue(lost)
        self.assertEqual(P.support(gz, wz, np.ones(2, bool), 2, range(1, 40), n=1)["failures"], lost)
        self.assertTrue(P.support(g, w, m, 4, [1], n=3)["pass"])


class Coupling(unittest.TestCase):
    def test_exact_multiset(self):
        g = np.array([0, 0, 1, 2])
        pt, pz, w = np.array([.1, .2, .3, .4]), np.array([2.0, 2.1, 3.0, 4.0]), np.array([1.0, 2.0, 0.5, 0.0])
        perm = np.array([1, 0, 2, 3])
        self.assertTrue(P.coupling_exact(g, pt, pz, w, g[perm], pt[perm], pz[perm], w[perm])["pass"])
        # equal cell sums from different weights (codex r3 #1): fails
        self.assertFalse(P.coupling_exact(g, pt, pz, np.array([0.5, 2.5, 0.5, 0]), g, pt, pz, w)["pass"])
        # a zero-weight row on one side only is irrelevant
        self.assertTrue(P.coupling_exact(g[:3], pt[:3], pz[:3], w[:3], g, pt, pz, w)["pass"])
        # a missing row fails and is located
        r = P.coupling_exact(g[1:], pt[1:], pz[1:], w[1:], g, pt, pz, w)
        self.assertFalse(r["pass"])
        self.assertEqual(r["cells_with_count_mismatch"], [0])
        self.assertFalse(P.coupling_exact(g, pt, pz, np.array([1.0, np.nan, .5, 0]), g, pt, pz, w)["pass"])
        # a negative weight fails even when both sides carry it identically
        wn = np.array([1.0, -2.0, 0.5, 0.0])
        r = P.coupling_exact(g, pt, pz, wn, g, pt, pz, wn)
        self.assertFalse(r["pass"])
        self.assertEqual(r["why"], "a negative weight")

    def test_appended_identity(self):
        rows = {"entry": np.array([5, 9, 12], np.int64), "reco_pt": np.array([.1, .2, .3]),
                "reco_pz": np.array([2., 3., 4.]), "true_pt": np.array([.11, .21, .31]),
                "true_pz": np.array([2.1, 3.1, 4.1]), "w_reco": np.array([1., 2., 3.]), "w_truth": np.array([1.1, 2.2, 3.3])}
        app = np.array([12, 5], np.int64)
        pot = 0.25
        tail = {"reco_pt": np.array([.3, .1]), "reco_pz": np.array([4., 2.]), "truth_pt": np.array([.31, .11]),
                "truth_pz": np.array([4.1, 2.1]), "w_truth": np.array([3.3, 1.1]) * pot,
                "w_reco": np.array([3., 1.]) * pot, "pass_reco": np.array([True, True]),
                "pass_truth": np.array([True, True])}
        self.assertTrue(P.appended_identity(rows, app, pot, tail)["pass"])
        bad = dict(tail, w_reco=tail["w_reco"][::-1])
        self.assertFalse(P.appended_identity(rows, app, pot, bad)["pass"])
        self.assertFalse(P.appended_identity(rows, np.array([12, 6]), pot, tail)["pass"])
        self.assertFalse(P.appended_identity(rows, app, pot, dict(tail, pass_truth=np.array([True, False])))["pass"])


class Gates(unittest.TestCase):
    def test_module_pins_are_make_trees(self):
        """B8: the runner's pre-import pins are make_tree.sh's RUNNER_SHA and OOFVC_LIB_SHA, not a second copy that
        could drift."""
        import re
        import ptmc_run
        mt = (HERE / "make_tree.sh").read_text()
        want = {"2d-unfolding/ref_c2c1/ref_c2c1.py": re.search(r"^RUNNER_SHA=([0-9a-f]{64})$", mt, re.M).group(1),
                "2d-unfolding/oofvc/oofvc_lib.py": re.search(r"^OOFVC_LIB_SHA=([0-9a-f]{64})$", mt, re.M).group(1)}
        self.assertEqual(ptmc_run.MODULE_PINS, want)

    def test_rel_close_zero_and_nan(self):
        self.assertTrue(P.rel_close([0.0, 2.0], [0.0, 2.0 * (1 + 1e-12)], 1e-9)["pass"])
        self.assertFalse(P.rel_close([1e-300, 2.0], [0.0, 2.0], 1e-9)["pass"])
        self.assertFalse(P.rel_close([np.nan, 2.0], [1.0, 2.0], 1e-9)["pass"])
        self.assertFalse(P.rel_close([1.0, 2.0], [1.0, np.inf], 1e-9)["pass"])

    def test_shape_gate(self):
        rng = np.random.default_rng(0)
        D = rng.normal(size=(200, 224))
        self.assertTrue(P.shape_gate(D[0], D)["pass"])
        self.assertFalse(P.shape_gate(D[0][:205], D[:, :205])["pass"])
        bad = D.copy()
        bad[3, 4] = np.nan
        self.assertFalse(P.shape_gate(D[0], bad)["pass"])
        # full rank 50, but one leave-one-out drops to 49: the 50th mode lives in replica 0 alone
        X = np.zeros((200, 224))
        X[:, :49] = rng.normal(size=(200, 49))
        X[0, 49] = 5.0
        r = P.shape_gate(X[0], X)
        self.assertTrue(r["full"])
        self.assertFalse(r["pass"])
        self.assertIn(0, r["loo_failures"])
        low = D.copy()
        low[:, 10:] = 0.0  # exact zero variance beyond 10 cells: the 50 leading eigenvalues include exact zeros
        self.assertFalse(P.shape_gate(low[0], low)["pass"])
        # roundoff-level positive modes pass pinv_rank's criterion, as declared; the conditioning is printed instead
        num = rng.normal(size=(200, 10)) @ rng.normal(size=(10, 224))
        r = P.shape_gate(num[0], num)
        self.assertLess(r["lambda_ratio_rank_over_top"], 1e-10)

    def test_conditioning_guard(self):
        """The binding's guard (the director, 2026-11-27): lambda_r / lambda_1 at 1e-13 STOPs, at 1e-6 passes."""
        rng = np.random.default_rng(3)
        for ratio, want in ((1e-13, False), (1e-6, True)):
            scales = np.geomspace(1.0, ratio, 50)
            D = np.zeros((200, 224))
            D[:, :50] = rng.normal(size=(200, 50)) * np.sqrt(scales)
            D[:, 50:] = rng.normal(size=(200, 174)) * np.sqrt(ratio * 1e-3)
            c = P.conditioning(D, rank=50)
            self.assertEqual(c["pass"], want, c)
        self.assertFalse(P.conditioning(np.full((200, 224), np.nan))["pass"])

    def test_finite_t(self):
        self.assertTrue(P.finite_t({"T": 1.0, "q95": 2.0, "max": 3.0}))
        self.assertFalse(P.finite_t({"T": float("nan"), "q95": 2.0, "max": 3.0}))

    def test_proto_eps(self):
        c = np.array([4.0, 1.0, 0.0])
        r = P.proto_eps(np.array([[0.002, 0.0, 0.0]]), np.zeros((1, 3)), c)
        self.assertAlmostEqual(r["eps"], 0.001)
        # codex's probe: a difference [10, 1] over the diagonal [4, 0] is eps = 5 plus one zero-variance discrepancy
        r = P.proto_eps(np.array([[10.0, 1.0]]), np.zeros((1, 2)), np.array([4.0, 0.0]))
        self.assertAlmostEqual(r["eps"], 5.0)
        self.assertEqual(r["zero_variance_cells_differing"], 1)
        r = P.proto_eps(np.zeros((1, 3)), np.zeros((1, 3)), c, delta_paired=np.array([0.0, 0.5, 0.0]),
                        delta_B=np.zeros(3))
        self.assertAlmostEqual(r["eps"], 0.5)
        self.assertEqual(len(r["eps_per_row"]), 2)

    def test_staged_index(self):
        self.assertEqual(P.staged_index(1), "002_xsec.root")
        self.assertEqual(P.staged_index(200), "201_xsec.root")
        with self.assertRaises(ValueError):
            P.staged_index(0)


class Readings(unittest.TestCase):
    def test_disposition_order(self):
        self.assertEqual(P.disposition(False, True, False, False, True), "stop")      # an R control failed
        self.assertEqual(P.disposition(True, False, False, False, True), "stop")      # the mandatory E_R central
        self.assertEqual(P.disposition(True, True, True, True, None), "stop")         # a present product mismatched
        self.assertEqual(P.disposition(True, True, False, False, False), "stop")      # C-REPOFF failed
        self.assertEqual(P.disposition(True, True, True, False, None), "unavailable")
        self.assertEqual(P.disposition(True, True, False, False, True), "formed")
        self.assertEqual(P.disposition(True, True, False, False, None), "stop")

    def test_row3_names_b_as_section_5_requires(self):
        """codex 23 (class a): when B is read, it is named as the production convention in REF-C2C1's separate-refit
        protocol, never only as "the matched baseline"."""
        t = P.statement("agree", "formed", "marginal")
        self.assertEqual(t["row"], 3)
        self.assertIn("the production convention in REF-C2C1's separate-refit protocol", t["text"])
        self.assertNotIn("the matched baseline reads", t["text"])
        self.assertIn("no change of reading is stated", t["text"])

    def test_statement_partition(self):
        rows = {}
        for r1 in P.WORDS:
            for b in P.WORDS:
                t = P.statement(r1, "formed", b)
                rows[(r1, b)] = t["row"]
                self.assertNotIn("held fixed", t["text"])
            rows[(r1, None)] = P.statement(r1, "unavailable", None)["row"]
        self.assertEqual(len(rows), 12)
        self.assertEqual(rows[("differ", "differ")], 1)
        self.assertEqual({rows[("marginal", "differ")], rows[("agree", "differ")]}, {2})
        self.assertEqual({rows[(r, b)] for r in P.WORDS for b in ("agree", "marginal")}, {3})
        self.assertEqual({rows[(r, None)] for r in P.WORDS}, {4})
        with self.assertRaises(ValueError):
            P.statement("differ", "stop", "differ")


# ----------------------------------------------------------------------------------------------- ROOT tests


def tree() -> Path:
    if "t" not in _TREE:
        t = TD / "tree"
        p = subprocess.run(["bash", str(HERE / "make_tree.sh"), str(t), "archive", str(REPO), str(TD / "stage")],
                           capture_output=True, text=True, env=dict(os.environ, PTMC_PY=sys.executable))
        if p.returncode:
            raise AssertionError(p.stdout + p.stderr)
        _TREE["t"] = t
    return _TREE["t"]


def write_fixture():
    if "fx" not in _TREE:
        stage = TD / "stage"
        stage.mkdir(exist_ok=True)
        code = (f"import sys; sys.path.insert(0, {str(tree() / '2d-unfolding' / 're2' / 'tests')!r}); "
                f"import test_re2_driver as t; from pathlib import Path; "
                f"t.write_fixture(Path({str(stage / 'fx.root')!r}), Path({str(stage / 'flux.root')!r}))")
        subprocess.run([sys.executable, "-B", "-c", code], check=True, env=dict(os.environ, OMP_NUM_THREADS="1"))
        _TREE["fx"] = (stage / "fx.root", stage / "flux.root")
    return _TREE["fx"]


ARGV = ["--iters", "2", "--use-weights", "--estimator", "lgbm", "--seed", "42", "--branch-select", "all",
        "--bkg-mode", "negweight-refined", "--refine-n-estimators", "400", "--refine-num-leaves", "31"]


def run_driver(driver: Path, out: Path, extra=(), check=True):
    fx, flux = write_fixture()
    p = subprocess.run([sys.executable, "-B", str(driver), "--omnifile", str(fx), "--mcfile", str(flux), *ARGV,
                        *extra, "--out", str(out)], capture_output=True, text=True,
                       env=dict(os.environ, OMP_NUM_THREADS="1"), cwd=str(driver.parent))
    if check and p.returncode:
        raise AssertionError(p.stdout[-3000:] + p.stderr[-3000:])
    return p


def th2v(path: Path, name: str) -> np.ndarray:
    import ROOT
    f = ROOT.TFile.Open(str(path))
    h = f.Get(name)
    v = np.array([h.GetBinContent(ix, iy) for ix in range(1, 15) for iy in range(1, 17)])
    f.Close()
    return v


def fixture_rows(n=300, seed=3):
    """Mock moved rows: n selected mc_background entries with a true muon in the grid (some reco outside)."""
    import ROOT
    sys.path.insert(0, str(REPO / "2d-unfolding" / "oofvc"))
    import oofvc_lib as L
    fx, _ = write_fixture()
    d = ROOT.RDataFrame("mc_background", str(fx)).AsNumpy(["sim_background", "sim_background_pz",
                                                           "sim_background_pass", "w_bkg"])
    rng = np.random.default_rng(seed)
    ok = np.flatnonzero(d["sim_background_pass"] != 0)
    e = np.sort(rng.choice(ok, n, replace=False)).astype(np.int64)
    rp, rz, w = (d[k][e].astype(np.float64) for k in ("sim_background", "sim_background_pz", "w_bkg"))
    tp = np.clip(rp * rng.normal(1, 0.05, n), 0.01, 4.4)
    tz = np.clip(rz * rng.normal(1, 0.05, n), 1.6, 59.0)
    assert np.any(~L.in_bins(rp, rz, PT, PZ)), "the fixture rows need some reco outside the grid"
    return {"entry": e, "reco_pt": rp, "reco_pz": rz, "true_pt": tp, "true_pz": tz, "w_reco": w, "w_truth": w * 1.1}


def save_rows(rows, name) -> Path:
    p = TD / "stage" / name
    np.savez(p, **rows)
    return p


def oofvc_driver_on_m() -> Path:
    """M's driver with only oofvc_driver.diff (the reference PTMC's hunk is compared with)."""
    if "oofvc" not in _TREE:
        d = TD / "oofvc-only"
        (d / "2d-unfolding" / "re2").mkdir(parents=True)
        src = subprocess.run(["git", "-C", str(REPO), "show", "77d76cfc:2d-unfolding/re2/re2_driver.py"],
                             capture_output=True, check=True).stdout
        (d / "2d-unfolding" / "re2" / "re2_driver.py").write_bytes(src)
        subprocess.run(["git", "apply", str(REPO / "2d-unfolding" / "oofvc" / "oofvc_driver.diff")], cwd=d, check=True)
        # the driver imports its siblings: link the tree's re2 directory contents beside it
        for f in (tree() / "2d-unfolding" / "re2").iterdir():
            if f.name != "re2_driver.py" and not (d / "2d-unfolding" / "re2" / f.name).exists():
                (d / "2d-unfolding" / "re2" / f.name).symlink_to(f)
        for top in ("unbinned_unfolding", "nd-unfolding"):
            (d / top).symlink_to(tree() / top)
        _TREE["oofvc"] = d / "2d-unfolding" / "re2" / "re2_driver.py"
    return _TREE["oofvc"]


BOOT = ["--bootstrap-seed", "3", "--bootstrap-streams", "three"]


@unittest.skipUnless(HAVE_ROOT, "needs PyROOT, LightGBM and scikit-learn")
class Driver(unittest.TestCase):
    """PTMC's hunk on RE-2's fixture."""

    @classmethod
    def setUpClass(cls):
        cls.drv = tree() / "2d-unfolding" / "re2" / "re2_driver.py"
        cls.rows = fixture_rows()
        cls.rows_path = save_rows(cls.rows, "rows.npz")
        cls.R = ["--signal-convention", "minerva", "--oofvc-rows", str(cls.rows_path)]

    def test_production_paths_are_byte_identical_to_oofvcs(self):
        """The hunk leaves production untouched: a production central and a production three-stream replica give
        the same hXSec2D bit for bit with PTMC's driver and with OOFVC's alone (LightGBM at one thread is
        deterministic here)."""
        for extra, tag in (((), "c"), (BOOT, "b")):
            a, b = TD / f"prod_ptmc_{tag}.root", TD / f"prod_oofvc_{tag}.root"
            run_driver(self.drv, a, extra)
            run_driver(oofvc_driver_on_m(), b, extra)
            for h in ("hXSec2D", "hOFCompleteness2D"):
                np.testing.assert_array_equal(th2v(a, h), th2v(b, h), err_msg=f"{tag} {h}")

    def test_r_central_is_oofvcs(self):
        a, b = TD / "r_ptmc_c.root", TD / "r_oofvc_c.root"
        run_driver(self.drv, a, self.R)
        run_driver(oofvc_driver_on_m(), b, self.R)
        for h in ("hXSec2D", "hOFCompleteness2D"):
            np.testing.assert_array_equal(th2v(a, h), th2v(b, h), err_msg=h)

    def test_r_replica_runs_and_oofvc_alone_refuses(self):
        run_driver(self.drv, TD / "r_ptmc_b.root", self.R + BOOT)
        p = run_driver(oofvc_driver_on_m(), TD / "r_oofvc_b.root", self.R + BOOT, check=False)
        self.assertNotEqual(p.returncode, 0)

    def test_refusals(self):
        """The argument check itself refuses (its own message), before any input is read."""
        for extra in (self.R + ["--bootstrap-seed", "3"],  # default streams
                      self.R + ["--bootstrap-seed", "3", "--bootstrap-streams", "both"],
                      self.R + BOOT + ["--unit-factors"]):
            p = run_driver(self.drv, TD / "refused.root", extra, check=False)
            self.assertNotEqual(p.returncode, 0, extra)
            self.assertIn("runs on the central CV path or its three-stream bootstrap only", p.stdout + p.stderr)


def configure_tree_for_fixture():
    """Tests only: point the deploy tree's config.json at the fixture, this machine's CPUs and thread environment."""
    sys.path.insert(0, str(tree() / "2d-unfolding" / "ref_c2c1"))
    import ref_c2c1 as C
    fx, flux = write_fixture()
    cfg_path = tree() / "2d-unfolding" / "ref_c2c1" / "config.json"
    cfg = json.loads(cfg_path.read_text())
    cfg["inputs"]["staging"].update(root=str(TD / "stage"), CV=fx.name, MC=flux.name)
    cfg["inputs"]["CV_sha256"] = hashlib.sha256(fx.read_bytes()).hexdigest()
    cfg["inputs"]["MC_sha256"] = hashlib.sha256(flux.read_bytes()).hexdigest()
    cfg["e_r"]["argv"] = ["--omnifile", "$CV", "--mcfile", "$MC"] + ARGV
    cfg["e_r"]["cpus"] = C.cpu_count()
    cfg["e_r"]["thread_env"] = {k: os.environ.get(k) for k in cfg["e_r"]["thread_env"]}
    cfg_path.write_text(json.dumps(cfg, indent=1))


@unittest.skipUnless(HAVE_ROOT, "needs PyROOT, LightGBM and scikit-learn")
class Runner(unittest.TestCase):
    """ptmc_run.py's units on the fixture (numpy unfolder: no libRooUnfold here)."""

    UNITS = ["p_off_c", "p_off_b1", "p_R_c", "p_R_b1"]

    @classmethod
    def setUpClass(cls):
        configure_tree_for_fixture()
        cls.rows = fixture_rows(seed=5)
        cls.rows_path = save_rows(cls.rows, "oofvc_rows.npz")
        cls.out = TD / "units"
        cls.join = TD / "join.json"
        cls.join.write_text(json.dumps({"verdict": "PASS"}))
        import ptmc_run
        argv = ["--tree", str(tree()), "--rows", str(cls.rows_path), "--rows-sha256",
                hashlib.sha256(cls.rows_path.read_bytes()).hexdigest(), "--join-record", str(cls.join),
                "--out", str(cls.out), "--numpy-unfolder"] + sum((["--unit", u] for u in cls.UNITS), [])
        cls.pins = {"rows": hashlib.sha256(cls.rows_path.read_bytes()).hexdigest(),
                    "join": hashlib.sha256(cls.join.read_bytes()).hexdigest()}
        with mock.patch.object(os, "O_NOATIME", os.O_NONBLOCK, create=True), mock.patch.dict(ptmc_run.PINS, cls.pins):
            cls.rc = ptmc_run.main(argv)

    def meta(self, u):
        return json.loads(str(np.load(self.out / f"{u}.npz", allow_pickle=False)["meta"]))

    def test_units_pass_with_every_control(self):
        for u in self.UNITS:
            m = self.meta(u)
            failed = {k: v for k, v in m["controls"].items() if not v["pass"]}
            self.assertFalse(failed, f"{u}: {failed}")
        self.assertEqual(self.rc, 0)

    def test_controls_present(self):
        want = {"C-FILL-IBU", "C-PAIR", "C-ROO", "C-DRAW-R", "C-REFINE", "C-COMP"}
        for u in self.UNITS:
            m = self.meta(u)
            got = set(m["controls"])
            self.assertTrue(want <= got, f"{u}: {got}")
            if u.endswith("_c"):
                self.assertIn("C-COUPLE", got)
                self.assertIn("C-SIM", got)
        self.assertIsNotNone(self.meta("p_R_c")["support"])
        self.assertEqual(self.meta("p_R_b1")["controls"]["C-COMP"]["mode"], "resampled")
        self.assertEqual(self.meta("p_off_b1")["controls"]["C-COMP"]["mode"], "cv")
        self.assertIsInstance(self.meta("p_R_b1")["suppressed_moved_support_cells"], int)  # agy 8: per replica

    def test_hxsec_is_the_plain_drivers_omnifold(self):
        """The unit's hXSec2D is OmniFold's: a plain run of the same driver with the unit's argv (no seam) gives it bit
        for bit (LightGBM at one thread is deterministic here), for a central and a replica, in both conventions."""
        drv = tree() / "2d-unfolding" / "re2" / "re2_driver.py"
        for u in ("p_R_c", "p_R_b1", "p_off_b1"):
            argv = self.meta(u)["argv"]
            out = TD / f"plain_{u}.root"
            p = subprocess.run([sys.executable, "-B", str(drv), *argv, "--out", str(out)], capture_output=True,
                               text=True, env=dict(os.environ, OMP_NUM_THREADS="1"), cwd=str(drv.parent))
            self.assertEqual(p.returncode, 0, p.stdout[-2000:] + p.stderr[-2000:])
            np.testing.assert_array_equal(th2v(out, "hXSec2D"), th2v(self.out / f"{u}.root", "hXSec2D"), err_msg=u)

    def test_r_replica_appended_factors_are_background_streams(self):
        m = self.meta("p_R_b1")["controls"]["C-DRAW-R"]
        self.assertTrue(m["appended_list"] and m["n_appended"] > 0, m)
        self.assertEqual(self.meta("p_off_b1")["controls"]["C-DRAW-R"]["n_appended"], 0)
        # D2: the original rows draw the same in both conventions
        self.assertEqual(self.meta("p_R_b1")["controls"]["C-DRAW-R"]["original_sum"],
                         self.meta("p_off_b1")["controls"]["C-DRAW-R"]["original_sum"])
        self.assertEqual(self.meta("p_R_b1")["controls"]["C-DRAW-R"]["data_sum"],
                         self.meta("p_off_b1")["controls"]["C-DRAW-R"]["data_sum"])

    def test_r_replica_fill_records_are_the_filtered_production_ones(self):
        """C-MOVE in every R replica (the confirm read's finding 3): the ordered fill records are p_off_b1's with the
        rows file's entries removed, multiplicity kept, and the injection is the fiducial rule on that reference."""
        off, r = np.load(self.out / "p_off_b1.npz"), np.load(self.out / "p_R_b1.npz")
        keep = ~np.isin(off["fill_entry"], self.rows["entry"])
        self.assertTrue(keep.any() and (~keep).any())
        for k in ("fill_entry", "fill_pt", "fill_pz", "fill_w"):
            np.testing.assert_array_equal(r[k], off[k][keep], err_msg=k)
        want_inj = P.injected_entries({"entry": off["fill_entry"][keep], "pt": off["fill_pt"][keep],
                                       "pz": off["fill_pz"][keep]}, PT[0], PT[-1], PZ[0], PZ[-1])
        np.testing.assert_array_equal(r["inj_entries"], want_inj)

    def test_rerun_skips_pass_and_refuses_unknown(self):
        import ptmc_run
        with mock.patch.object(os, "O_NOATIME", os.O_NONBLOCK, create=True), mock.patch.dict(ptmc_run.PINS, self.pins):
            rc = ptmc_run.main(["--tree", str(tree()), "--rows", str(self.rows_path), "--rows-sha256",
                                hashlib.sha256(self.rows_path.read_bytes()).hexdigest(), "--join-record",
                                str(self.join), "--out", str(self.out), "--numpy-unfolder", "--unit", "p_off_c"])
        self.assertEqual(rc, 0)
        self.assertEqual(ptmc_run.main(["--tree", str(tree()), "--rows", "x", "--rows-sha256", "0", "--join-record",
                                        "x", "--out", str(self.out), "--unit", "p_off_b6"]), 2)
        self.assertEqual(ptmc_run.main(["--tree", str(tree()), "--rows", "x", "--rows-sha256", "0", "--join-record",
                                        "x", "--out", str(self.out), "--unit", "p_R_b201"]), 2)
        self.assertEqual(ptmc_run.main(["--tree", str(tree()), "--rows", "x", "--rows-sha256", "0", "--join-record",
                                        "x", "--out", str(self.out), "--unit", "p_R_b3", "--unit", "p_R_b3"]), 2)

    def test_reuse_requires_both_products_to_match(self):
        """codex r1 #2: a PASS marker with a missing or altered product is refused, never reused."""
        import ptmc_run
        tmp = Path(tempfile.mkdtemp())
        for f in ("p_off_c.npz", "p_off_c.root", "p_off_c.done"):
            (tmp / f).write_bytes((self.out / f).read_bytes())
        (tmp / "p_off_c.root").write_bytes(b"altered")
        args = ["--tree", str(tree()), "--rows", str(self.rows_path), "--rows-sha256", self.pins["rows"],
                "--join-record", str(self.join), "--out", str(tmp), "--numpy-unfolder", "--unit", "p_off_c"]
        with mock.patch.object(os, "O_NOATIME", os.O_NONBLOCK, create=True), mock.patch.dict(ptmc_run.PINS, self.pins):
            self.assertEqual(ptmc_run.main(args), ptmc_run.RC_CONTROL)
            (tmp / "p_off_c.root").unlink()
            self.assertEqual(ptmc_run.main(args), ptmc_run.RC_CONTROL)

    def test_reuse_requires_this_bindings_code(self):
        """Confirm read B2: a PASS unit made by other code (its marker's runner digest differs) is refused, never
        reused."""
        import ptmc_run
        tmp = Path(tempfile.mkdtemp())
        for f in ("p_off_c.npz", "p_off_c.root", "p_off_c.done"):
            (tmp / f).write_bytes((self.out / f).read_bytes())
        mk = json.loads((tmp / "p_off_c.done").read_text())
        self.assertEqual(mk["verdict"], "PASS")
        args = ["--tree", str(tree()), "--rows", str(self.rows_path), "--rows-sha256", self.pins["rows"],
                "--join-record", str(self.join), "--out", str(tmp), "--numpy-unfolder", "--unit", "p_off_c"]
        with mock.patch.object(os, "O_NOATIME", os.O_NONBLOCK, create=True), mock.patch.dict(ptmc_run.PINS, self.pins):
            self.assertEqual(ptmc_run.main(args), 0)  # the same code: reused
            mk["runner_sha256"] = "0" * 64
            (tmp / "p_off_c.done").write_text(json.dumps(mk))
            self.assertEqual(ptmc_run.main(args), ptmc_run.RC_CONTROL)
            # B2: nor one made by another unfolder
            mk = json.loads((self.out / "p_off_c.done").read_text())
            mk["unfolder"] = "f" * 64
            (tmp / "p_off_c.done").write_text(json.dumps(mk))
            self.assertEqual(ptmc_run.main(args), ptmc_run.RC_CONTROL)

    def test_a_running_unit_holds_its_claim(self):
        """Confirm read B2: the unit's marker is created exclusively (RUNNING) before the driver runs, so a second
        run of the same unit refuses instead of racing it."""
        seen = {}
        import ptmc_run
        out = Path(tempfile.mkdtemp())
        orig = ptmc_run.run_paired

        def wrapped(*a, **k):
            seen["marker"] = json.loads((out / "p_off_b2.done").read_text())
            return orig(*a, **k)
        argv = ["--tree", str(tree()), "--rows", str(self.rows_path), "--rows-sha256", self.pins["rows"],
                "--join-record", str(self.join), "--out", str(out), "--numpy-unfolder", "--unit", "p_off_b2"]
        with mock.patch.object(os, "O_NOATIME", os.O_NONBLOCK, create=True), \
                mock.patch.dict(ptmc_run.PINS, self.pins), mock.patch.object(ptmc_run, "run_paired", wrapped):
            self.assertEqual(ptmc_run.main(argv), 0)
        self.assertEqual(seen["marker"], {"unit": "p_off_b2", "verdict": "RUNNING"})
        self.assertEqual(json.loads((out / "p_off_b2.done").read_text())["verdict"], "PASS")

    def test_coupling_sums_are_part_of_c_couple(self):
        """Confirm read B10: the central's C-COUPLE requires the driver's D_CV to agree with the independently summed
        T_orig,CV (the sums record), not only the multiset identity."""
        import ptmc_run
        orig = ptmc_run.read_hist

        def shifted(C, driver, root, name, allowed):
            h = orig(C, driver, root, name, allowed)
            return h * 1.01 if name == "hOFTruthDenom2D" else h
        with mock.patch.object(ptmc_run, "read_hist", shifted):
            rc, meta, verdict = self.corrupted_unit("p_off_c", lambda cap: None)
        self.assertFalse(meta["controls"]["C-COUPLE"]["sums"]["pass"])
        self.assertFalse(meta["controls"]["C-COUPLE"]["pass"])
        self.assertEqual(verdict, "FAIL")

    def test_the_denominator_is_the_same_in_every_unit(self):
        """The scorer's C-DEN premise on the real driver: hOFTruthDenom2D is bit-identical across conventions, centrals
        and replicas."""
        ref = th2v(self.out / "p_off_c.root", "hOFTruthDenom2D")
        for u in self.UNITS[1:]:
            np.testing.assert_array_equal(th2v(self.out / f"{u}.root", "hOFTruthDenom2D"), ref, err_msg=u)
        # and C-FIX's class and grid rules (B9) hold on the real driver's objects
        import ptmc_score as S
        for u in self.UNITS:
            ro = S.root_objects(self.out / f"{u}.root")
            self.assertTrue(all(S.fix_equal(ro, ro).values()), (u, S.fix_equal(ro, ro)))

    def test_deploy_modules_are_checked_before_import(self):
        """B8: ref_c2c1.py and oofvc_lib.py are hashed against their pins before the runner imports them."""
        import ptmc_run
        for rel in ptmc_run.MODULE_PINS:
            with mock.patch.dict(ptmc_run.MODULE_PINS, {rel: "0" * 64}), \
                    mock.patch.object(os, "O_NOATIME", os.O_NONBLOCK, create=True), \
                    mock.patch.dict(ptmc_run.PINS, self.pins):
                rc = ptmc_run.main(["--tree", str(tree()), "--rows", str(self.rows_path), "--rows-sha256",
                                    self.pins["rows"], "--join-record", str(self.join), "--out",
                                    str(Path(tempfile.mkdtemp())), "--numpy-unfolder", "--unit", "p_off_b3"])
            self.assertEqual(rc, ptmc_run.RC_GATE, rel)

    def test_one_spelling_per_unit(self):
        """codex 11: p_R_b01 is not a second name for p_R_b1."""
        import ptmc_run
        self.assertEqual(ptmc_run.main(["--tree", str(tree()), "--rows", "x", "--rows-sha256", "0", "--join-record",
                                        "x", "--out", str(self.out), "--unit", "p_R_b01"]), 2)
        self.assertEqual(ptmc_run.parse_unit("p_R_b1"), ("R", 1))

    def test_a_replicas_suppressed_count_uses_its_own_weights(self):
        """agy 8: an R replica's suppressed-moved-support count is taken on its own resampled weights. With every
        moved row's draw zeroed, no structural-zero cell keeps surviving moved weight, whatever the CV count is."""
        central = self.meta("p_R_c")["suppressed_moved_support_cells"]
        self.assertGreater(central, 0, "the fixture has no structural-zero cell with moved weight: the case is vacuous")

        def corrupt(cap):
            n_app = len(cap["sig_cv"]["oofvc_outside"]["appended_entry"])
            ws = np.array(cap["w_truth_seen"], float, copy=True)
            ws[ws.size - n_app:] = 0.0
            cap["w_truth_seen"] = ws
        rc, meta, verdict = self.corrupted_unit("p_R_b1", corrupt)
        self.assertEqual(meta["suppressed_moved_support_cells"], 0)

    def test_wrong_rows_pin_refuses(self):
        import ptmc_run
        with mock.patch.object(os, "O_NOATIME", os.O_NONBLOCK, create=True):
            rc = ptmc_run.main(["--tree", str(tree()), "--rows", str(self.rows_path), "--rows-sha256",
                                self.pins["rows"], "--join-record", str(self.join), "--out", str(Path(tempfile.mkdtemp())),
                                "--numpy-unfolder", "--unit", "p_off_c"])
        self.assertEqual(rc, ptmc_run.RC_GATE)  # the module's pins are r3's, not the fixture's

    def test_rows_file_not_its_pin_refuses(self):
        """The rows file's own bytes are checked against the pin, not only the --rows-sha256 argument."""
        import ptmc_run
        alt = self.rows_path.with_name("oofvc_rows_altered.npz")
        alt.write_bytes(self.rows_path.read_bytes() + b"\0")
        with mock.patch.object(os, "O_NOATIME", os.O_NONBLOCK, create=True), mock.patch.dict(ptmc_run.PINS, self.pins):
            rc = ptmc_run.main(["--tree", str(tree()), "--rows", str(alt), "--rows-sha256", self.pins["rows"],
                                "--join-record", str(self.join), "--out", str(Path(tempfile.mkdtemp())),
                                "--numpy-unfolder", "--unit", "p_off_b2"])
        self.assertEqual(rc, ptmc_run.RC_GATE)

    def corrupted_unit(self, unit, corrupt):
        """One unit on a fresh output with `corrupt` applied to the capture before the controls run."""
        import ptmc_run
        out = Path(tempfile.mkdtemp())
        orig = ptmc_run.run_paired

        def wrapped(*a, **k):
            cap = orig(*a, **k)
            corrupt(cap)
            return cap
        argv = ["--tree", str(tree()), "--rows", str(self.rows_path), "--rows-sha256", self.pins["rows"],
                "--join-record", str(self.join), "--out", str(out), "--numpy-unfolder", "--unit", unit]
        with mock.patch.object(os, "O_NOATIME", os.O_NONBLOCK, create=True), \
                mock.patch.dict(ptmc_run.PINS, self.pins), mock.patch.object(ptmc_run, "run_paired", wrapped):
            rc = ptmc_run.main(argv)
        meta = json.loads(str(np.load(out / f"{unit}.npz", allow_pickle=False)["meta"]))
        verdict = json.loads((out / f"{unit}.done").read_text())["verdict"]
        return rc, meta, verdict

    def assert_only_failure(self, rc, meta, verdict, control):
        import ptmc_run
        failed = sorted(k for k, v in meta["controls"].items() if v["pass"] is not True)
        self.assertEqual(failed, [control] if control else [])
        self.assertEqual((rc, verdict), (ptmc_run.RC_CONTROL, "FAIL"))

    def test_pair_measured_mask_defect_fails(self):
        def corrupt(cap):
            m = np.array(cap["seam"]["measured_pass_reco"], copy=True)
            m[0] = False
            cap["seam"]["measured_pass_reco"] = m
        rc, meta, verdict = self.corrupted_unit("p_off_b1", corrupt)
        self.assertFalse(meta["controls"]["C-PAIR"]["measured_mask_all_true"])
        self.assert_only_failure(rc, meta, verdict, "C-PAIR")

    def test_refined_weight_not_the_measured_weight_fails(self):
        def corrupt(cap):
            w = np.array(cap["refined_w"], copy=True)
            w[0] = np.nextafter(w[0], np.inf)
            cap["refined_w"] = w
        self.assert_only_failure(*self.corrupted_unit("p_off_b1", corrupt), "C-REFINE")

    def test_completeness_axes_not_the_grid_fail(self):
        def corrupt(cap):
            from array import array
            a, k = cap["extract"]
            h = a[0].Clone("ptmc_test_shifted_axes")
            h.SetDirectory(0)
            edges = [float(e) for e in PT]
            edges[-1] *= 1.01
            h.GetXaxis().Set(len(edges) - 1, array("d", edges))
            cap["extract"] = ((h,) + tuple(a[1:]), k)
        rc, meta, verdict = self.corrupted_unit("p_off_b1", corrupt)
        self.assertFalse(meta["controls"]["C-COMP"]["axes"])
        self.assert_only_failure(rc, meta, verdict, "C-COMP")

    def test_non_finite_extraction_argument_fails(self):
        """An infinite nucleon count zeroes every cell, so every rel_close control passes on exact zeros; only the
        finiteness of the extraction's arguments fails the unit."""
        def corrupt(cap):
            a, k = cap["extract"]
            cap["extract"] = (tuple(a[:3]) + (float("inf"),) + tuple(a[4:]), k)
        rc, meta, verdict = self.corrupted_unit("p_off_b1", corrupt)
        self.assertIs(meta["extract_args_finite"], False)
        self.assert_only_failure(rc, meta, verdict, None)


if __name__ == "__main__":
    unittest.main()
