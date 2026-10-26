"""Controls for fd_g_diag (FD-G-DIAG-DECLARATION.md section 5), on synthetic matrices with a known decomposition, on a
synthetic Stage G tree, and on the committed records. No real prediction, covariance or data value is read.

* Analytic: a well-conditioned M built from a known orthonormal basis gives the declared spectrum, per-mode chi2,
  block shares and block-removed chi2 exactly; a near-singular M is flagged by the stability check.
* Planted defects: for each of the declaration's five items, a defective version of the tool's own function is
  patched in, and the test's validator for that item, silent on the correct output, reports it.
* End to end: Stage G is run on the synthetic tree, then G-DIAG as invoked (-I -B, cwd outside nd-unfolding);
  it reproduces Stage G's chi2 and its blocks rebuild M. Each control D0-D6 refuses with nothing written."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

ND = Path(__file__).resolve().parents[1]
sys.path.insert(1, str(ND))
sys.path.insert(1, str(Path(__file__).resolve().parent))
import fd_g_compare as G  # noqa: E402
import fd_g_diag as D  # noqa: E402
import s1_assemble as sa  # noqa: E402
from test_fd_g_compare import Tree, digest, run_isolated  # noqa: E402

REPO = ND.parent
FD = REPO / "docs/orchestration/state/measurement-paper/5d-community-20261024"


# ------------------------------------------------------------------------------------------------ analytic fixtures


def basis(n=16, seed=0):
    Q, _ = np.linalg.qr(np.random.default_rng(seed).normal(size=(n, n)))
    return Q


def analytic(seed=0, lam=None, a=None, split=(0.25, 0.75)):
    """M = Q diag(lam) Q^T split into two blocks in fixed proportion, and d = Q a."""
    Q = basis(seed=seed)
    lam = np.geomspace(4e-3, 2e-5, 16) if lam is None else np.asarray(lam, float)
    a = np.random.default_rng(seed + 1).normal(0, 0.01, 16) if a is None else np.asarray(a, float)
    M = (Q * lam) @ Q.T
    blocks = {"A": split[0] * M, "B": split[1] * M}
    return Q, lam, a, M, blocks, Q @ a


CELLS = [f"R{c:02d}" for c in range(16)]


def run_breakdown(blocks, d):
    return D.breakdown(d, blocks, CELLS)


# validators: each returns a list of problems; silent on the correct output (tests below), loud on a planted defect

def check_spectrum(out, lam):
    want = np.sort(lam)[::-1]
    bad = []
    if not np.allclose(out["eigen"]["lambda"], want, rtol=1e-9, atol=0):
        bad.append("eigenvalues are not the known spectrum, descending")
    if not np.allclose(out["eigen"]["sigma"], np.sqrt(want), rtol=1e-9):
        bad.append("sigma is not sqrt(lambda)")
    if not np.isclose(out["eigen"]["condition"], want[0] / want[-1], rtol=1e-8):
        bad.append("condition number")
    by = {m["mode"]: m for m in out["modes_by_chi2"]}
    if sorted(by) != list(range(len(lam))) or any(not np.isclose(by[k]["lambda"], want[k], rtol=1e-9) or
                                                    not np.isclose(by[k]["sigma"], np.sqrt(want[k]), rtol=1e-9)
                                                    for k in by):
        bad.append("modes_by_chi2 lambda or sigma")
    return bad


def check_modes(out, lam, a):
    c = a ** 2 / lam
    order = np.argsort(c)[::-1]
    bad = []
    got = [m["chi2"] for m in out["modes_by_chi2"]]
    if not np.allclose(got, c[order], rtol=1e-8):
        bad.append("per-mode chi2 is not (v^T d)^2 / lambda, sorted")
    if not np.allclose([m["fraction"] for m in out["modes_by_chi2"]], c[order] / c.sum(), rtol=1e-8):
        bad.append("fractions")
    if not np.allclose([abs(m["projection"]) for m in out["modes_by_chi2"]], np.abs(a[order]), rtol=1e-8):
        bad.append("projections")
    frac = np.cumsum(c[order]) / c.sum()
    if not np.allclose([m["cumulative"] for m in out["modes_by_chi2"]], frac, rtol=1e-8):
        bad.append("cumulative")
    want = {f"{int(round(100 * q))}%": int(np.argmax(frac >= q - 1e-12) + 1) for q in D.FRACTIONS}
    if out["modes_needed"] != want:
        bad.append(f"modes needed {out['modes_needed']} != {want}")
    if not np.isclose(out["chi2"], c.sum(), rtol=1e-9):
        bad.append("chi2")
    return bad


def check_shares(out, split):
    bad = []
    for t in out["top_modes"]:
        if not (np.isclose(t["block_shares"]["A"], split[0], rtol=1e-9) and np.isclose(t["block_shares"]["B"], split[1],
                                                                                       rtol=1e-9)):
            bad.append(f"mode {t['mode']}: shares {t['block_shares']}")
        if not np.isclose(t["share_sum"], 1.0, rtol=1e-9) or not np.isclose(t["share_sum"],
                                                                           sum(t["block_shares"].values())):
            bad.append(f"mode {t['mode']}: shares sum to {t['share_sum']}")
    return bad


def check_removed(out, chi2, split, cond):
    want = {"A": chi2 / split[1], "B": chi2 / split[0]}
    bad = [f"{r['removed']}: {r['chi2']} != {want[r['removed']]}" for r in out["removed"]
           if r["chi2"] is None or not np.isclose(r["chi2"], want[r["removed"]], rtol=1e-8)]
    for r in out["removed"]:
        if r["chi2"] is not None and r["ndf"] != 16:
            bad.append(f"{r['removed']}: ndf")
        if not np.isclose(r["condition"], cond, rtol=1e-6) or r["ill_conditioned"]:
            bad.append(f"{r['removed']}: condition {r['condition']}")
    return bad


def check_no_p(out):
    """Amendment 1: a block-removed record carries chi2, ndf and the condition number, and no p-value."""
    return [f"{r['removed']}: carries p" for r in out["removed"] if "p" in r]


def check_unstable(out, expect):
    st = out["stability"]
    return [] if st["unstable"] is expect else [f"unstable is {st['unstable']}, expected {expect} "
                                                f"(ridge change {st['rel_ridge_vs_cholesky']})"]


def near_singular():
    lam = np.geomspace(4e-3, 2e-5, 16)
    lam[-1] = 1e-19                                   # far below the ridge, 1e-10 * mean(diag M) ~ 5e-14
    a = np.zeros(16)
    a[:15] = 0.01
    a[-1] = 1e-8                                      # a small component along the near-null mode
    return analytic(seed=4, lam=lam, a=a)


class Analytic(unittest.TestCase):
    def test_well_conditioned_decomposition_is_analytic(self):
        Q, lam, a, M, blocks, d = analytic()
        out = run_breakdown(blocks, d)
        self.assertEqual(check_spectrum(out, lam), [])
        self.assertEqual(check_modes(out, lam, a), [])
        self.assertEqual(check_shares(out, (0.25, 0.75)), [])
        self.assertEqual(check_removed(out, float(np.sum(a ** 2 / lam)), (0.25, 0.75), lam.max() / lam.min()), [])
        self.assertEqual(check_unstable(out, False), [])
        self.assertFalse(out["stability"]["methods_disagree"] or out["stability"]["ridge_sensitive"])
        st = out["stability"]
        for k in ("rel_mode_sum_vs_cholesky", "rel_lstsq_vs_cholesky"):
            self.assertLess(st[k], 1e-9, k)
        self.assertLess(st["rel_ridge_vs_cholesky"], 1e-4)
        # every top mode's loadings are its known basis vector, signed so its largest-|loading| cell is positive
        for t in out["top_modes"]:
            q = Q[:, t["mode"]]
            q = q * np.sign(q[np.argmax(np.abs(q))])
            np.testing.assert_allclose(list(t["loadings"].values()), q, atol=1e-9)
            self.assertEqual(list(t["loadings"]), CELLS)
            self.assertAlmostEqual(t["sigma"], np.sqrt(lam[t["mode"]]), delta=1e-12)
        self.assertEqual([t["mode"] for t in out["top_modes"]], list(np.argsort(a ** 2 / lam)[::-1][:3]))
        self.assertEqual(out["eigen"]["rank"], 16)

    def test_disjoint_blocks_own_their_modes(self):
        Q = basis(seed=2)
        lam = np.geomspace(4e-3, 2e-5, 16)
        X = (Q[:, :8] * lam[:8]) @ Q[:, :8].T                      # the eight largest modes
        Y = (Q[:, 8:] * lam[8:]) @ Q[:, 8:].T
        a = np.zeros(16)
        a[[1, 12, 14]] = [0.05, 0.01, 0.002]
        out = run_breakdown({"X": X, "Y": Y}, Q @ a)
        want = {1: "X", 12: "Y", 14: "Y"}
        self.assertEqual(sorted(t["mode"] for t in out["top_modes"]), sorted(want))
        for t in out["top_modes"]:
            self.assertEqual(t["dominant"], want[t["mode"]])
            self.assertAlmostEqual(t["block_shares"][want[t["mode"]]], 1.0, places=9)
        # removing a block that a mode lives in leaves M singular there: reported, not computed
        self.assertEqual({r["removed"]: r["positive_definite"] for r in out["removed"]}, {"X": False, "Y": False})

    def test_near_singular_is_exposed_by_the_ridge(self):
        Q, lam, a, M, blocks, d = near_singular()
        out = run_breakdown(blocks, d)
        self.assertEqual(check_unstable(out, True), [])
        # an artefact, not only ridge sensitivity: float64 Cholesky misses the analytic chi2, and the methods disagree
        st = out["stability"]
        exact = float(np.sum(a ** 2 / lam))
        self.assertGreater(abs(st["chi2_cholesky"] - exact) / exact, 0.1)
        self.assertTrue(st["methods_disagree"] and st["ridge_sensitive"])
        self.assertGreater(out["stability"]["rel_ridge_vs_cholesky"], 0.9)    # the ridge removes the artefact
        self.assertGreater(out["eigen"]["condition"], 1e14)
        top = out["top_modes"][0]                              # and the chi2 sat in the near-null mode
        self.assertEqual(top["mode"], 15)
        self.assertGreater(top["fraction"], 0.9)

    def test_an_indefinite_matrix_is_unstable_and_carries_no_chi2(self):
        Q, lam, a, M, blocks, d = analytic(seed=5, lam=np.r_[np.geomspace(4e-3, 2e-5, 15), -1e-12])
        out = run_breakdown(blocks, d)
        self.assertIsNone(out["chi2"])
        self.assertTrue(out["stability"]["unstable"])
        self.assertEqual(out["modes_by_chi2"][0]["chi2"], float("inf"))

    def test_ridge_sensitivity_threshold_and_ridge_size_are_the_declared_ones(self):
        """A diagonal M with a known ridge response pins RIDGE (times the MEAN diagonal), UNSTABLE, and the change's
        denominator (the Cholesky chi2)."""
        self.assertEqual((D.RIDGE, D.UNSTABLE, D.METHODS), (1e-10, 1e-3, 1e-8))
        for target, flagged in ((2e-3, True), (5e-4, False)):
            lmin = 1e-8
            lam = np.r_[np.full(15, 1.0), lmin]
            eps = 1e-10 * lam.mean()                          # the declared ridge, on the MEAN diagonal
            d = np.ones(16)
            # chi2(eps) = sum_i d_i^2 / (lam_i + eps); choose d_15 so the relative change from the ridge is `target`
            others = np.sum(1 / lam[:15] - 1 / (lam[:15] + eps))
            k = 1 / lmin - 1 / (lmin + eps)
            d[-1] = np.sqrt((target * 15 - others) / (k - target / lmin))
            x2 = 15 + d[-1] ** 2 / lmin
            want = (others + d[-1] ** 2 * k) / x2
            self.assertAlmostEqual(want, target, delta=1e-9)
            st = D.chi2_ways(np.diag(lam), d, *D.eigen(np.diag(lam)))
            self.assertAlmostEqual(st["ridge"], eps, delta=1e-24)
            self.assertAlmostEqual(st["rel_ridge_vs_cholesky"], want, delta=1e-6 * want)
            self.assertEqual(st["ridge_sensitive"], flagged, target)
            self.assertFalse(st["methods_disagree"])

    def test_an_ill_conditioned_removal_is_flagged(self):
        Q = basis(seed=6)
        lam = np.geomspace(4e-3, 2e-5, 16)
        M = (Q * lam) @ Q.T
        X = M - 1e-18 * np.eye(16)                                 # removing X leaves 1e-18 * I: PD, cond 1
        Y = M - (Q[:, :1] * 1e-19) @ Q[:, :1].T - (Q[:, 1:] * 1e-5) @ Q[:, 1:].T   # leaves a cond-1e14 remainder
        out = run_breakdown({"X": X, "R": M - X}, Q @ np.full(16, 1e-3))
        self.assertFalse(next(r for r in out["removed"] if r["removed"] == "X")["ill_conditioned"])
        out = run_breakdown({"Y": Y, "R": M - Y}, Q @ np.full(16, 1e-3))
        r = next(r for r in out["removed"] if r["removed"] == "Y")
        self.assertTrue(r["ill_conditioned"])
        self.assertGreater(r["condition"], D.ILL)

    def test_the_stdout_line_carries_the_flags_and_the_dominant_block(self):
        Q, lam, a, M, blocks, d = near_singular()
        bad = run_breakdown(blocks, d)
        Q, lam, a, M, blocks, d = analytic()
        good = run_breakdown(blocks, d)
        c = {"comparison": "reported", "matrix": "M + V_g", "ndf": 16, "relative_to_f": bad, "absolute": good}
        line = D.summary_line("x", c)
        self.assertIn("UNSTABLE (ridge_sensitive, methods_disagree)", line)
        self.assertIn(f"dominant {bad['top_modes'][0]['dominant']}", line)
        self.assertIn(f"modes for 50/90/99 % {bad['modes_needed']['50%']}/{bad['modes_needed']['90%']}/"
                      f"{bad['modes_needed']['99%']}", line)
        c2 = dict(c, relative_to_f=good)
        self.assertNotIn("UNSTABLE", D.summary_line("x", c2))
        self.assertIn(f"chi2 {good['chi2']:.2f};", D.summary_line("x", c2))

    def test_non_finite_numbers_are_written_as_null_and_counted(self):
        n = [0]
        self.assertEqual(D.finite({"a": [1.0, float("inf"), {"b": float("nan")}], "c": 2}, n),
                         {"a": [1.0, None, {"b": None}], "c": 2})
        self.assertEqual(n, [2])

    def test_modes_needed(self):
        self.assertEqual(D.modes_needed(np.array([0.5, 0.3, 0.15, 0.05])), {"50%": 1, "90%": 3, "99%": 4})
        self.assertEqual(D.modes_needed(np.array([0.995, 0.005])), {"50%": 1, "90%": 1, "99%": 1})
        self.assertEqual(D.modes_needed(np.array([np.nan, 0.5])), {"50%": None, "90%": None, "99%": None})


# ------------------------------------------------------------------------------------------------ planted defects


class PlantedDefects(unittest.TestCase):
    """One per item of the declaration: the defect is patched into the tool, and that item's validator reports it."""

    def test_item_1_spectrum_ascending(self):
        Q, lam, a, M, blocks, d = analytic()
        self.assertEqual(check_spectrum(run_breakdown(blocks, d), lam), [])
        orig = D.eigen
        with mock.patch.object(D, "eigen", lambda M: tuple(x[..., ::-1] for x in orig(M))):
            self.assertNotEqual(check_spectrum(run_breakdown(blocks, d), lam), [])

    def test_item_2_per_mode_chi2_over_sqrt_lambda(self):
        Q, lam, a, M, blocks, d = analytic()
        self.assertEqual(check_modes(run_breakdown(blocks, d), lam, a), [])
        with mock.patch.object(D, "mode_chi2", lambda lam, V, d: ((V.T @ d), (V.T @ d) ** 2 / np.sqrt(lam))):
            self.assertNotEqual(check_modes(run_breakdown(blocks, d), lam, a), [])

    def test_item_2_modes_needed_off_by_one(self):
        Q, lam, a, M, blocks, d = analytic()
        orig = D.modes_needed
        with mock.patch.object(D, "modes_needed", lambda f: {k: v - 1 for k, v in orig(f).items()}):
            self.assertNotEqual(check_modes(run_breakdown(blocks, d), lam, a), [])

    def test_item_3_shares_not_divided_by_lambda(self):
        Q, lam, a, M, blocks, d = analytic()
        self.assertEqual(check_shares(run_breakdown(blocks, d), (0.25, 0.75)), [])
        with mock.patch.object(D, "block_shares", lambda v, l, b: {k: float(v @ B @ v) for k, B in b.items()}):
            self.assertNotEqual(check_shares(run_breakdown(blocks, d), (0.25, 0.75)), [])

    def test_item_4_block_added_instead_of_removed(self):
        Q, lam, a, M, blocks, d = analytic()
        chi2 = float(np.sum(a ** 2 / lam))
        cond = lam.max() / lam.min()
        self.assertEqual(check_removed(run_breakdown(blocks, d), chi2, (0.25, 0.75), cond), [])
        with mock.patch.object(D, "removed_chi2", lambda M, B, d: D.chol_chi2(M + B, d)):
            self.assertNotEqual(check_removed(run_breakdown(blocks, d), chi2, (0.25, 0.75), cond), [])

    def test_item_4_no_p_value_on_a_removal(self):
        """Amendment 1: a p-value planted back into the removal record is caught."""
        Q, lam, a, M, blocks, d = analytic()
        out = run_breakdown(blocks, d)
        self.assertEqual(check_no_p(out), [])
        self.assertEqual({k for r in out["removed"] for k in r},
                         {"removed", "positive_definite", "chi2", "ndf", "condition", "ill_conditioned", "label"})
        orig = D.removal_record
        with mock.patch.object(D, "removal_record",
                               lambda name, x2, cond, n: dict(orig(name, x2, cond, n), p=G.chi2_sf(x2, n))):
            self.assertNotEqual(check_no_p(run_breakdown(blocks, d)), [])

    def test_item_5_no_ridge_hides_the_artefact(self):
        Q, lam, a, M, blocks, d = near_singular()

        def check_ridge(out):
            return [] if out["stability"]["ridge_sensitive"] else ["the ridge did not move the near-singular chi2"]
        self.assertEqual(check_ridge(run_breakdown(blocks, d)), [])
        with mock.patch.object(D, "RIDGE", 0.0):
            self.assertNotEqual(check_ridge(run_breakdown(blocks, d)), [])

    def test_item_5_methods_compared_to_themselves(self):
        Q, lam, a, M, blocks, d = near_singular()

        def check_methods(out):
            return [] if out["stability"]["methods_disagree"] else ["the float64 methods were not seen to disagree"]
        self.assertEqual(check_methods(run_breakdown(blocks, d)), [])
        with mock.patch.object(D, "METHODS", float("inf")):
            self.assertNotEqual(check_methods(run_breakdown(blocks, d)), [])


# ------------------------------------------------------------------------------------------------ the synthetic tree


class DiagTree(Tree):
    """Stage G's synthetic tree, with S1's C_e written as named blocks (one per S1 group) and C_model as S^T S."""

    def __init__(self, root, seed=0, scale=1e-39):
        super().__init__(root, seed=seed, scale=scale)
        rng = np.random.default_rng(seed + 100)
        ff = np.outer(self.f, self.f)
        A = rng.normal(size=(40, 16))
        vecs = rng.normal(0, 0.03, (4, 16))
        rel = {"stat": 0.003 ** 2 * (np.cov(A, rowvar=False) + np.eye(16)), "band:Flux": np.outer(vecs[0], vecs[0]),
               "band:MaRES": np.outer(vecs[1], vecs[1]), "band:MaCCQE": 0.5 * np.outer(vecs[1][::-1], vecs[1][::-1]),
               "band:GEANT_Pion": np.outer(vecs[2], vecs[2]),
               "lat:BeamAngleX": np.outer(vecs[3], vecs[3]), "normalization": np.full((16, 16), 0.014 ** 2),
               "seed": 1e-8 * np.eye(16)}
        self.blocks = {k: v * ff for k, v in rel.items()}
        self.Ce = sum(self.blocks[k] for k in sorted(self.blocks))
        self.S = rng.normal(0, 0.02, (3, 16)) * np.array([[0.4], [1.0], [3.0]])
        self.Cmf = self.S.T @ self.S
        self.Cma = self.Cmf * ff
        self.Ct = self.Ce + self.Cma
        v = rng.normal(0, 0.02, (4, 16)) * self.f
        self.Cx = v.T @ v

    def write(self, mutate=None, role="adopted", g_mutate=None):
        super().write(mutate)
        R = self.root
        s1n = R / "s1_assembly.npz"
        np.savez_compressed(s1n, f=self.f, U=self.U.astype(np.float32), C_e=self.Ce, C_model_frac=self.Cmf,
                            C_model_abs=self.Cma, C_total=self.Ct,
                            **{"C_" + k.replace(":", "_"): v for k, v in self.blocks.items()},
                            meta=json.dumps({"blocks": sorted(self.blocks)}))
        s1j = R / "s1_assembly.json"
        s1j.write_text(json.dumps({"assembly_sha256": digest(s1n),
                                   "relative_sigma": {"C_total": (np.sqrt(np.diag(self.Ct)) / self.f).tolist()}}))
        cmj = R / "cmodel_5d.json"
        cmj.write_text(json.dumps({"x": self.f.tolist(), "S": self.S.tolist(), "vertices": list(D.VERTICES)}))
        self.pins.update(s1_npz=digest(s1n), s1_json=digest(s1j), cmodel_json=digest(cmj))
        self.xb = R / "cresp.npz"
        np.savez(self.xb, C_resp=self.Cx)
        self.extra = ["--extra-block", str(self.xb), "--extra-block-sha256", digest(self.xb), "--extra-block-key",
                      "C_resp", "--extra-block-name", "C_resp", "--extra-block-role", role]
        # Stage G on this tree, as bound: its readout is the one G-DIAG reproduces
        self.g_readout = R / "fd_g_readout.json"
        gargv = self.argv[:-2] + self.extra + ["--out-json", str(self.g_readout)]
        with mock.patch("sys.stdout"), mock.patch.object(sys, "argv", ["fd_g_compare.py"] + gargv):
            G.run(G.build_args(gargv), self.pins, self.predictions)
        if g_mutate:
            r = json.loads(self.g_readout.read_text())
            g_mutate(r)
            self.g_readout.write_text(json.dumps(r))
        self.dpins = {**self.pins, "g_readout": digest(self.g_readout)}
        self.dargv = self.argv[:-2] + ["--g-readout", str(self.g_readout)] + self.extra + \
            ["--out-json", str(self.out / "diag.json")]
        return self

    def config(self):
        return {"nd": str(ND), "pins": self.dpins, "predictions": self.predictions, "argv": self.dargv}


WRAPPER = r"""
import json, sys
cfg = json.load(open(sys.argv[1]))
sys.path.insert(0, cfg["nd"])
import fd_g_compare as g
import fd_g_diag as m
m.PINS = cfg["pins"]
g.PREDICTIONS = tuple(dict(p, meta=tuple(p["meta"])) for p in cfg["predictions"])
sys.argv = ["fd_g_diag.py"] + cfg["argv"]
raise SystemExit(m.main(cfg["argv"]))
"""


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="fd-gd-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def run_module(self, tree):
        cfg, w = self.tmp / "cfg.json", self.tmp / "wrapper.py"
        cfg.write_text(json.dumps(tree.config()))
        w.write_text(WRAPPER)
        return run_isolated([str(w), str(cfg)])

    def assertStops(self, tree, control, why=""):
        with self.assertRaises(SystemExit) as cm, mock.patch("sys.stdout"):
            D.run(D.build_args(tree.dargv), tree.dpins, tree.predictions)
        self.assertIn(f"FAIL control {control}:", str(cm.exception.code))
        self.assertIn(why, str(cm.exception.code))
        self.assertFalse((tree.out / "diag.json").exists(), "a refused run wrote its readout")


class EndToEnd(Base):
    def test_run_as_invoked_reproduces_stage_g_and_partitions_m(self):
        tree = DiagTree(self.tmp / "t").write()
        r = self.run_module(tree)
        self.assertEqual(r.returncode, 0, r.stderr[-3000:])
        for c in ("D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7"):
            self.assertIn(f"PASS control {c} ", r.stdout)
        out = json.loads((tree.out / "diag.json").read_text())
        g = json.loads(tree.g_readout.read_text())
        self.assertEqual(out["schema"], "fd-g-diag-readout/1")
        self.assertEqual(out["controls_passed"], ["D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7"])
        self.assertEqual(out["constants"], {"ridge": 1e-10, "unstable": 1e-3, "methods": 1e-8, "ill_conditioned": 1e12,
                                            "top": 3, "fractions": [0.5, 0.9, 0.99], "reproduction": 1e-10,
                                            "units": ["relative_to_f", "absolute"]})
        self.assertEqual(out["non_finite_written_as_null"], 0)
        self.assertEqual(out["blocks"]["s1_blocks_per_group"]["interaction"], ["band:MaCCQE", "band:MaRES"])
        gp = {p["name"]: p for p in g["predictions"]}
        names = set(D.GROUPS) | {f"C_model:{v}" for v in D.VERTICES} | {"V_g"}
        lines = [ln for ln in r.stdout.splitlines() if ln.startswith("[G-DIAG]")]
        self.assertEqual(len(lines), 10)
        k = 0
        for p in out["predictions"]:
            cells = list(G.GIBUU_CELLS) if p["name"] == "gibuu" else list(range(16))
            i = np.asarray(cells)
            n = len(cells)
            fi = tree.f[i]
            self.assertEqual(p["cells"], [f"R{c:02d}" for c in cells])
            self.assertEqual([c["comparison"] for c in p["comparisons"]], ["reported", "variant"])
            self.assertEqual([c["matrix"] for c in p["comparisons"]], ["C_total + C_resp + V_g", "C_total + V_g"])
            d = tree.preds[p["name"]]
            gc = d["g"][i]
            Vg = d["relvar"][i] * gc ** 2
            for c, ref, carries in zip(p["comparisons"], (gp[p["name"]], gp[p["name"]]["variant"]), (True, False)):
                self.assertEqual(c["ndf"], n)
                self.assertEqual(c["chi2_stage_g"], ref["total"]["chi2"])
                Mabs = (tree.Ct + (tree.Cx if carries else 0))[np.ix_(i, i)] + np.diag(Vg)
                for units, sc in (("relative_to_f", np.ones(n)), ("absolute", fi)):
                    b = c[units]
                    M = Mabs / np.outer(fi, fi) * np.outer(sc, sc)
                    dd = (tree.f[i] - gc) / fi * sc
                    self.assertAlmostEqual(b["chi2"], ref["total"]["chi2"], delta=1e-10 * ref["total"]["chi2"])
                    self.assertAlmostEqual(b["chi2_mode_sum"], b["chi2"], delta=1e-8 * b["chi2"])
                    ev = np.sort(np.linalg.eigvalsh(M))[::-1]
                    np.testing.assert_allclose(b["eigen"]["lambda"], ev, rtol=1e-9)
                    self.assertAlmostEqual(b["eigen"]["condition"], ev[0] / ev[-1], delta=1e-8 * ev[0] / ev[-1])
                    self.assertEqual(len(b["modes_by_chi2"]), n)
                    self.assertAlmostEqual(b["modes_by_chi2"][-1]["cumulative"], 1.0, places=9)
                    want = names | ({"C_resp"} if carries else set())
                    self.assertEqual(len(b["top_modes"]), 3)
                    for t in b["top_modes"]:
                        self.assertEqual(set(t["block_shares"]), want)
                        self.assertAlmostEqual(t["share_sum"], 1.0, places=9)
                        load = np.asarray(list(t["loadings"].values()))
                        self.assertEqual(list(t["loadings"]), p["cells"])
                        self.assertGreater(load[np.argmax(np.abs(load))], 0)          # the sign rule
                        self.assertAlmostEqual(float(load @ M @ load), t["sigma"] ** 2, delta=1e-9 * t["sigma"] ** 2)
                    self.assertEqual({x["removed"] for x in b["removed"]}, want)
                    self.assertFalse(b["stability"]["unstable"])
                    # V_g removed, by hand, in these units
                    rv = next(x for x in b["removed"] if x["removed"] == "V_g")
                    Mv = M - np.diag(Vg * (sc / fi) ** 2)
                    self.assertAlmostEqual(rv["chi2"], float(dd @ np.linalg.solve(Mv, dd)), delta=1e-8 * rv["chi2"])
                    self.assertEqual(rv["ndf"], n)
                    self.assertEqual(check_no_p(b), [])
                # the removal chi2 is unit-free; the two units agree on it
                for x, y in zip(c["relative_to_f"]["removed"], c["absolute"]["removed"]):
                    self.assertAlmostEqual(x["chi2"], y["chi2"], delta=1e-8 * x["chi2"])
                self.assertEqual(lines[k], D.summary_line(p["name"], c))
                k += 1
        self.assertEqual(sorted(x.name for x in tree.out.iterdir()), ["diag.json"])

    def test_sensitivity_role_swaps_which_comparison_is_reported(self):
        tree = DiagTree(self.tmp / "t").write(role="sensitivity")
        with mock.patch("sys.stdout"):
            self.assertEqual(D.run(D.build_args(tree.dargv), tree.dpins, tree.predictions), 0)
        out = json.loads((tree.out / "diag.json").read_text())
        g = {p["name"]: p for p in json.loads(tree.g_readout.read_text())["predictions"]}
        for p in out["predictions"]:
            self.assertEqual([c["matrix"] for c in p["comparisons"]], ["C_total + V_g", "C_total + C_resp + V_g"])
            self.assertEqual(p["comparisons"][0]["chi2_stage_g"], g[p["name"]]["total"]["chi2"])
            self.assertNotIn("C_resp", p["comparisons"][0]["relative_to_f"]["top_modes"][0]["block_shares"])

    def test_refuses_to_overwrite(self):
        tree = DiagTree(self.tmp / "t").write()
        (tree.out / "diag.json").write_text("{}")
        with self.assertRaises(SystemExit):
            D.run(D.build_args(tree.dargv), tree.dpins, tree.predictions)


def repin_prediction(tree, name, change):
    """Rewrite one prediction file after Stage G ran, and re-pin it in the predictions and the manifest."""
    spec = next(p for p in tree.predictions if p["name"] == name)
    path = tree.root / "s5p" / spec["path"]
    with np.load(path) as z:
        arrs = {k: z[k] for k in z.files}
    change(arrs)
    np.savez_compressed(path, **arrs)
    tree.predictions = tuple(dict(p, sha256=digest(path)) if p["name"] == name else p for p in tree.predictions)
    P = tree.root / "s5p"
    tree.sums.write_text("".join(f"{digest(P / p['path'])}  {p['path']}\n" for p in tree.predictions))
    tree.dpins["s5p_sums"] = digest(tree.sums)


def resave_s1(tree, change):
    s1n = tree.root / "s1_assembly.npz"
    with np.load(s1n) as z:
        arrs = {k: z[k] for k in z.files}
    change(arrs)
    np.savez_compressed(s1n, **arrs)
    s1j = tree.root / "s1_assembly.json"
    j = json.loads(s1j.read_text())
    j["assembly_sha256"] = digest(s1n)
    s1j.write_text(json.dumps(j))
    tree.dpins.update(s1_npz=digest(s1n), s1_json=digest(s1j))


def resave_block(tree, C):
    np.savez(tree.xb, C_resp=C)
    tree.dargv[tree.dargv.index("--extra-block-sha256") + 1] = digest(tree.xb)


class Controls(Base):
    def test_d0_stage_g_readout_pin(self):
        tree = DiagTree(self.tmp / "t").write()
        tree.dpins["g_readout"] = "0" * 64
        self.assertStops(tree, "D0", "g_readout")

    def test_d0_extra_block_digest(self):
        tree = DiagTree(self.tmp / "t").write()
        tree.dargv[tree.dargv.index("--extra-block-sha256") + 1] = "a" * 64
        self.assertStops(tree, "D0", "extra block")

    def test_d1_prediction_structure(self):
        tree = DiagTree(self.tmp / "t").write()
        repin_prediction(tree, "nuwro", lambda z: z.update(edges_pt=z["edges_pt"][:-1]))
        self.assertStops(tree, "D1", "edges_pt")

    def test_d2_a_missing_block(self):
        tree = DiagTree(self.tmp / "t").write()
        resave_s1(tree, lambda z: z.pop("C_band_MaRES"))
        self.assertStops(tree, "D2", "S1's blocks are all present")

    def test_d2_no_block_list(self):
        tree = DiagTree(self.tmp / "t").write()
        resave_s1(tree, lambda z: z.update(meta=json.dumps({})))
        self.assertStops(tree, "D2", "S1's blocks are all present")

    def test_d2_c_e_is_not_the_sum_of_the_blocks(self):
        tree = DiagTree(self.tmp / "t").write()
        resave_s1(tree, lambda z: z.update(C_band_MaCCQE=z["C_band_MaCCQE"] * (1 + 1e-9)))
        self.assertStops(tree, "D2", "C_e is the sum of S1's blocks")

    def test_d2_s_not_c_model(self):
        tree = DiagTree(self.tmp / "t").write()
        cmj = tree.root / "cmodel_5d.json"
        j = json.loads(cmj.read_text())
        j["S"][1][4] *= 1 + 1e-9
        cmj.write_text(json.dumps(j))
        tree.dpins["cmodel_json"] = digest(cmj)
        self.assertStops(tree, "D2", "C_model = S^T S")

    def test_d2_vertices_in_another_order(self):
        tree = DiagTree(self.tmp / "t").write()
        cmj = tree.root / "cmodel_5d.json"
        j = json.loads(cmj.read_text())
        j["vertices"] = ["nuwro", "genie_mec", "gibuu"]
        cmj.write_text(json.dumps(j))
        tree.dpins["cmodel_json"] = digest(cmj)
        self.assertStops(tree, "D2", "C_model's vertices are GENIE+MEC, NuWro, GiBUU")

    def test_d2_an_unknown_group(self):
        tree = DiagTree(self.tmp / "t").write()
        with mock.patch.object(D, "GROUPS", tuple(g for g in D.GROUPS if g != "detector")):
            self.assertStops(tree, "D2", "every block maps to one of S1's seven groups")

    def test_d2_the_extra_block(self):
        for k, (C, why) in enumerate(((lambda C: C + np.triu(np.full((16, 16), 1e-3 * C.max()), 1)
                                       - np.triu(np.full((16, 16), 1e-3 * C.max()), 1).T, "C_resp is symmetric"),
                                      (lambda C: C - 2 * abs(C[0, 0]) * np.eye(16)[[0]].T @ np.eye(16)[[0]],
                                       "C_resp is positive semidefinite"),
                                      (lambda C: C[:15, :15], "C_resp is a finite 16 x 16 matrix"))):
            tree = DiagTree(self.tmp / f"t{k}").write()
            resave_block(tree, C(tree.Cx))
            # the Stage G readout names the old digest, so D5 would refuse too; D2 must come first
            self.assertStops(tree, "D2", why)

    def test_d3_gibuu_cells(self):
        tree = DiagTree(self.tmp / "t").write()
        with mock.patch.object(G, "GIBUU_CELLS", (0, 1, 2, 3, 8, 9, 10, 12)):
            self.assertStops(tree, "D3", "p_parallel < 4.5")

    def test_d4_a_non_positive_integral(self):
        tree = DiagTree(self.tmp / "t").write()
        fm = tree.fm

        def neg(z):
            x = z["xsec_flat"].copy()
            x[fm == 5] = -abs(x[fm == 5])
            z["xsec_flat"] = x
        repin_prediction(tree, "genie_mec", neg)
        self.assertStops(tree, "D4", "genie_mec")

    def test_d5_each_sub_check(self):
        def argv_set(k, v):
            def f(r):
                r["argv"][r["argv"].index(k) + 1] = v
            return f
        cases = {
            "extra-block role": argv_set("--extra-block-role", "sensitivity"),
            "extra-block name": argv_set("--extra-block-name", "C_other"),
            "extra-block key": argv_set("--extra-block-key", "C_other"),
            "extra-block sha256": argv_set("--extra-block-sha256", "b" * 64),
            "schema fd-g-readout/2": lambda r: r.update(schema="fd-g-readout/1"),
        }
        for k, (why, m) in enumerate(cases.items()):
            tree = DiagTree(self.tmp / f"t{k}").write(g_mutate=m)
            self.assertStops(tree, "D5", why)

    def test_d5_numbers_to_1e_10(self):
        def bump(path, factor):
            def f(r):
                o = r["predictions"][2]
                for key in path[:-1]:
                    o = o[key]
                if isinstance(o[path[-1]], list):
                    o[path[-1]][3] *= factor
                else:
                    o[path[-1]] *= factor
            return f
        for k, path in enumerate((("variant", "total", "chi2"), ("shape_only", "chi2"), ("variant", "shape_only", "chi2"),
                                  ("pulls",), ("variant", "pulls"))):
            tree = DiagTree(self.tmp / f"t{k}").write(g_mutate=bump(path, 1 + 1e-8))
            self.assertStops(tree, "D5", "reproduce")
        tree = DiagTree(self.tmp / "ok").write(g_mutate=bump(("total", "chi2"), 1 + 1e-12))   # inside tolerance
        with mock.patch("sys.stdout"):
            self.assertEqual(D.run(D.build_args(tree.dargv), tree.dpins, tree.predictions), 0)

    def test_d5_another_cell_set(self):
        def cut(r):
            r["predictions"][3]["cells"] = r["predictions"][3]["cells"][:-1]
        tree = DiagTree(self.tmp / "t").write(g_mutate=cut)
        self.assertStops(tree, "D5", "another cell set")

    def test_d6_a_block_left_out_or_off_by_1e_9(self):
        orig = D.comparison_blocks
        for k, how in enumerate(("drop", "scale")):
            tree = DiagTree(self.tmp / f"t{k}").write()

            def wrong(*a, how=how):
                B = orig(*a)
                if how == "drop":
                    B.pop("V_g")
                else:
                    B["V_g"] = B["V_g"] * (1 + 1e-9)
                return B
            with mock.patch.object(D, "comparison_blocks", wrong):
                self.assertStops(tree, "D6", "rebuild")

    def test_d7_the_breakdowns_residual_is_not_stage_gs(self):
        tree = DiagTree(self.tmp / "t").write()
        with mock.patch.object(D, "residual", lambda f, g, i, sc: ((f - g) / g * sc)[i]):
            self.assertStops(tree, "D7", "Stage G's committed total chi2")


class Invocation(Base):
    def test_help_and_argparse_under_isolation(self):
        r = run_isolated([str(ND / "fd_g_diag.py"), "--help"])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("--extra-block-role", r.stdout)
        tree = DiagTree(self.tmp / "t").write()
        no_role = [x for x in tree.dargv if x not in ("--extra-block-role", "adopted")]
        r = run_isolated([str(ND / "fd_g_diag.py"), *no_role])
        self.assertEqual(r.returncode, 2, r.stderr)

    def test_the_real_script_reaches_d0_and_refuses_synthetic_records(self):
        tree = DiagTree(self.tmp / "t").write()
        r = run_isolated([str(ND / "fd_g_diag.py"), *tree.dargv])
        self.assertEqual(r.returncode, 1, r.stderr[-2000:])
        self.assertIn("FAIL control D0:", r.stderr)
        self.assertNotIn("Traceback", r.stderr)
        self.assertFalse((tree.out / "diag.json").exists())


class CommittedPins(unittest.TestCase):
    def test_the_stage_g_readout_pin_and_its_extra_block(self):
        p = FD / "fd/readout/fd_g_readout.json"
        self.assertEqual(digest(p), D.PINS["g_readout"])
        r = json.loads(p.read_text())
        a = r["argv"]
        self.assertEqual([a[a.index(k) + 1] for k in ("--extra-block-sha256", "--extra-block-key", "--extra-block-name",
                                                      "--extra-block-role")],
                         ["4d8b579732b79cbbb8e6c9a4f6335c4bda4eae6dd4194241a0d8cd6e7ea8a20a", "C_resp", "C_resp",
                          "adopted"])
        self.assertEqual({k: D.PINS[k] for k in G.PINS}, G.PINS)

    def test_every_committed_s1_block_maps_to_the_seven_groups(self):
        j = json.loads((FD / "s1/readout/s1_assembly.json").read_text())
        blocks = j["meta"]["blocks"]
        self.assertEqual(len(blocks), 46)
        self.assertEqual({sa.group_of(b) for b in blocks}, set(D.GROUPS))
        self.assertEqual(set(j["relative_sigma"]) - {"C_e", "C_model", "C_total"}, set(D.GROUPS))
        c = json.loads((ND / "pv-ladder/readouts/cmodel_5d.json").read_text())
        self.assertEqual(tuple(c["vertices"]), D.VERTICES)


if __name__ == "__main__":
    unittest.main()
