"""OOFVC's tests (OOFVC-DECLARATION.md). Pure tests run anywhere with numpy; the ROOT tests need PyROOT, LightGBM and
scikit-learn (locally an environment with ROOT 6.40). The deploy tree is built once by make_tree.sh (archive mode)
from this checkout's M.

  OOFVC_PY=/path/python python -B -m pytest -q -p no:cacheprovider test_oofvc.py
"""
from __future__ import annotations

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

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
import oofvc_lib as L  # noqa: E402

try:
    import ROOT  # noqa: F401
    import lightgbm  # noqa: F401
    import sklearn  # noqa: F401
    HAVE_ROOT = True
except Exception:  # pragma: no cover
    HAVE_ROOT = False

PAPER_PT = [0, 0.075, 0.15, 0.25, 0.325, 0.40, 0.475, 0.55, 0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50]
PZ = [1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 6, 7, 8, 9, 10, 15, 20, 40, 60]
TD = Path(tempfile.mkdtemp(prefix="oofvc-test-"))
_TREE = {}


def tree() -> Path:
    """The deploy tree (make_tree.sh, archive mode), built once per run."""
    if "t" not in _TREE:
        t = TD / "tree"
        subprocess.run(["bash", str(HERE / "make_tree.sh"), str(t), "archive", str(REPO), str(TD / "stage")],
                       check=True, capture_output=True, env=dict(os.environ, OOFVC_PY=sys.executable))
        _TREE["t"] = t
    return _TREE["t"]


def ref_c2c1():
    sys.path.insert(0, str(tree() / "2d-unfolding" / "ref_c2c1"))
    import ref_c2c1 as C
    return C


def random_problem(rng, n):
    M = rng.random((n, n)) * (rng.random((n, n)) < 0.4)
    M[:, rng.random(n) < 0.05] = 0
    T = M.sum(axis=0) / rng.uniform(0.3, 1.0, n)
    y = M @ rng.uniform(0.5, 1.5, n) * rng.uniform(0.8, 1.2, n)
    return M, T, y


class Identity(unittest.TestCase):
    """N's identity (section 2.1): REF-C2C1's IBU is IBU-to-selected divided by the efficiency, so N is the factor."""

    def test_ibu_is_unfold_selected_over_efficiency_and_n_is_the_factor(self):
        rng = np.random.default_rng(1)
        worst = 0.0
        for _ in range(200):
            n = int(rng.integers(3, 30))
            M, T, y = random_problem(rng, n)
            O = rng.random(n) * M.sum(axis=0) * 0.3
            sM = M.sum(axis=0)
            for K in (1, 5, 10, 20):
                u = L.dagostini(M, T, y, [K])[K]
                s = L.unfold_selected(M, y, K)
                eff = np.divide(sM, T, out=np.zeros(n), where=T > 0)
                effN = np.divide(sM + O, T, out=np.zeros(n), where=T > 0)
                ref0 = np.divide(s, eff, out=np.zeros(n), where=eff > 0)
                refN = np.divide(s, effN, out=np.zeros(n), where=effN > 0)
                uN = u * L.n_factor(sM, O)
                for a, b in ((u, ref0), (uN, refN)):
                    worst = max(worst, float(np.max(np.abs(a - b) / np.maximum(np.abs(b), 1e-300))))
        self.assertLess(worst, 1e-13)  # 7.5e-15 when first measured (OOFVC-DECLARATION.md rev 2)

    def test_t_cancels_from_the_cross_section(self):
        """The IBU result divided by c = T / D is s_K * D / sum_i M_ij for any T (section 2.1)."""
        rng = np.random.default_rng(2)
        M, T, y = random_problem(rng, 12)
        D = T * rng.uniform(0.9, 1.1, 12)
        a = L.dagostini(M, T, y, [10])[10] / (T / D)
        b = L.dagostini(M, T * 1.7 + 3.0, y, [10])[10] / ((T * 1.7 + 3.0) / D)
        np.testing.assert_allclose(a, b, rtol=1e-12)

    def test_n_factor_edges(self):
        np.testing.assert_array_equal(L.n_factor([0.0, 2.0, 3.0], [1.0, 0.0, 1.0]), [1.0, 1.0, 0.75])
        with self.assertRaises(ValueError):
            L.n_factor([1.0], [-1.0])


class MatchesRefC2C1(unittest.TestCase):
    """The lane's copies equal REF-C2C1's (the runner uses ref_c2c1's own; these are for the tests and the scorer)."""

    def test_dagostini_and_binning_equal(self):
        C = ref_c2c1()
        rng = np.random.default_rng(3)
        M, T, y = random_problem(rng, 20)
        a, b = L.dagostini(M, T, y, [1, 5, 10]), C.dagostini(M, T, y, [1, 5, 10])
        for k in a:
            np.testing.assert_array_equal(a[k], b[k])
        pt = np.concatenate([rng.uniform(-0.1, 4.6, 500), PAPER_PT])
        pz = np.concatenate([rng.uniform(1.4, 61, 500), PZ[:15]])
        np.testing.assert_array_equal(L.global_index(pt, pz, PAPER_PT, PZ), C.global_index(pt, pz, PAPER_PT, PZ))


def _join(left, right, ev=None, vals=None, w=None):
    n = len(right[0])
    ev = np.arange(n)[:, None] if ev is None else ev
    vals = np.column_stack(right) if vals is None else vals
    return L.exact_join(left, right, ev, vals, np.ones(len(left[0])) if w is None else w)


class Join(unittest.TestCase):
    """exact_join and check_tie_bound: the director's rulings on ruling 1."""

    def test_one_to_one(self):
        a = (np.array([1.0, 2.0, 3.0]), np.array([4.0, 5.0, 6.0]))
        b = (np.array([3.0, 1.0, 2.0]), np.array([6.0, 4.0, 5.0]))
        j = _join(a, b)
        np.testing.assert_array_equal(j["right_of_left"], [1, 2, 0])
        self.assertEqual(j["n_tied_groups"], 0)

    def test_unmatched_and_count_mismatch_stop(self):
        a = (np.array([1.0, 2.0]),)
        for b in ((np.array([1.0, 2.5]),), (np.array([1.0]),), (np.array([1.0, 2.0, 2.0]),)):
            with self.assertRaises(L.JoinStop):
                _join(a, b)

    def test_exact_bits(self):
        with self.assertRaises(L.JoinStop):
            _join((np.array([0.1 + 0.2]),), (np.array([0.3]),))
        with self.assertRaises(L.JoinStop):
            _join((np.array([0.0]),), (np.array([-0.0]),))

    def test_tie_of_one_event_filled_twice_is_allowed(self):
        a = (np.array([1.0, 2.0, 2.0]),)
        b = (np.array([2.0, 1.0, 2.0]),)
        ev = np.array([[7], [8], [7]])
        j = _join(a, b, ev=ev, vals=np.array([[2.0, 9.0], [1.0, 9.0], [2.0, 9.0]]), w=np.array([1.0, 0.5, 0.5]))
        self.assertEqual((j["n_tied_groups"], j["n_tied_rows"], j["tied_weight"]), (1, 2, 1.0))

    def test_tie_between_events_or_values_stops(self):
        a = (np.array([2.0, 2.0]),)
        b = (np.array([2.0, 2.0]),)
        with self.assertRaises(L.JoinStop):
            _join(a, b, ev=np.array([[7], [8]]), vals=np.array([[1.0], [1.0]]))
        with self.assertRaises(L.JoinStop):
            _join(a, b, ev=np.array([[7], [7]]), vals=np.array([[1.0], [1.5]]))

    def test_three_copies_stop(self):
        a = (np.array([2.0, 2.0, 2.0]),)
        with self.assertRaises(L.JoinStop):
            _join(a, a, ev=np.array([[7], [7], [7]]), vals=np.array([[1.0], [1.0], [1.0]]))

    def test_tie_bound(self):
        L.check_tie_bound(1.0, 1000.0)
        L.check_tie_bound(0.0, 0.0)  # no tie needs no reference (codex-school r1 #9)
        with self.assertRaises(L.JoinStop):
            L.check_tie_bound(1.0001, 1000.0)
        with self.assertRaises(L.JoinStop):
            L.check_tie_bound(1.0, 0.0)
        with self.assertRaises(L.JoinStop):
            L.check_tie_bound(float("nan"), 1000.0)


class Moved(unittest.TestCase):
    def test_moved_mask(self):
        pdg = np.array([14, 14, 14, -14, 12, 14, 14])
        cur = np.array([1, 1, 2, 1, 1, 1, 1])
        pt = np.array([0.5, 4.5, 0.5, 0.5, 0.5, 4.4999999, 0.0, 0.5])
        pz = np.array([5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 1.5, 60.0])
        pdg = np.r_[pdg, 14]; cur = np.r_[cur, 1]
        # ROOT's cells: lower edges in, upper edges out (codex-school r1 #3)
        np.testing.assert_array_equal(L.moved_mask(pdg, cur, pt, pz, PAPER_PT, PZ),
                                      [True, False, False, False, False, True, True, False])


class Readings(unittest.TestCase):
    def test_bands(self):
        cases = {0.80: "LOWER", 0.5: "LOWER", 1.25: "HIGHER", 2.0: "HIGHER", 0.95: "LITTLE CHANGE",
                 1 / 0.95: "LITTLE CHANGE", 1.0: "LITTLE CHANGE", 0.9: "INTERMEDIATE", 1.1: "INTERMEDIATE",
                 0.8000001: "INTERMEDIATE", 1.2499999: "INTERMEDIATE"}
        for r, b in cases.items():
            self.assertEqual(L.band(r), b, r)
        for bad in (float("nan"), -0.1):
            with self.assertRaises(ValueError):
                L.band(bad)

    def test_statements(self):
        self.assertIn("both central values are closer", L.primary_statement("LOWER", "LOWER"))
        self.assertIn("does not move the OmniFold", L.primary_statement("LOWER", "INTERMEDIATE"))
        self.assertIn("does not move the OmniFold", L.primary_statement("LOWER", "LITTLE CHANGE"))
        self.assertIn("does not depend", L.primary_statement("LITTLE CHANGE", "LOWER"))
        self.assertIn("increases the OmniFold", L.primary_statement("LOWER", "HIGHER"))
        self.assertIn("increases the binned IBU's", L.primary_statement("HIGHER", "LOWER"))
        self.assertIn("No statement", L.primary_statement("INTERMEDIATE", "LOWER"))
        self.assertIn("moves the binned IBU's distance down", L.n_statement("LOWER"))
        self.assertIn("No statement", L.n_statement("INTERMEDIATE"))

    def test_distance_and_column(self):
        rng = np.random.default_rng(4)
        A = rng.random((224, 224))
        cov = A @ A.T + np.eye(224)
        cov[5, :] = cov[:, 5] = 0
        x, pub = rng.random(224), rng.random(224)
        d, ndf = L.distance(x, pub, cov)
        mask = np.arange(224) != 5
        self.assertEqual(ndf, 223)
        self.assertAlmostEqual(d, float((x - pub)[mask] @ np.linalg.inv(cov[np.ix_(mask, mask)]) @ (x - pub)[mask]) / 223,
                               places=9)
        x = np.ones(224); pub = np.full(224, 2.0)
        self.assertAlmostEqual(L.column_ratio(x, pub, PAPER_PT, PZ, 15), 0.5)


# ----------------------------------------------------------------------------------------------- ROOT tests


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
        raise AssertionError(p.stdout[-2000:] + p.stderr[-2000:])
    return p


def contents(path: Path) -> dict:
    import ROOT
    f = ROOT.TFile.Open(str(path))
    out = {}
    for k in f.GetListOfKeys():
        o = k.ReadObj()
        if o.InheritsFrom("TH1"):
            n = o.GetNcells()
            out[k.GetName()] = (np.array([o.GetBinContent(i) for i in range(n)]).tobytes(),
                                np.array([o.GetBinError(i) for i in range(n)]).tobytes())
        elif o.ClassName().startswith("TParameter"):
            out[k.GetName()] = o.GetVal()
        elif o.ClassName() == "TNamed":
            out[k.GetName()] = o.GetTitle()
    f.Close()
    return out


def th2v(path: Path, name: str) -> np.ndarray:
    import ROOT
    f = ROOT.TFile.Open(str(path))
    h = f.Get(name)
    v = np.array([h.GetBinContent(ix, iy) for ix in range(1, 15) for iy in range(1, 17)])
    f.Close()
    return v


def fixture_rows(n=300, seed=3, outside=True):
    """Mock moved rows: n selected mc_background entries with a true muon in the grid (some reco outside)."""
    import ROOT
    fx, _ = write_fixture()
    d = ROOT.RDataFrame("mc_background", str(fx)).AsNumpy(["sim_background", "sim_background_pz",
                                                           "sim_background_pass", "w_bkg"])
    rng = np.random.default_rng(seed)
    ok = np.flatnonzero(d["sim_background_pass"] != 0)
    e = np.sort(rng.choice(ok, n, replace=False)).astype(np.int64)
    rp, rz, w = (d[k][e].astype(np.float64) for k in ("sim_background", "sim_background_pz", "w_bkg"))
    tp = np.clip(rp * rng.normal(1, 0.05, n), 0.01, 4.4)
    tz = np.clip(rz * rng.normal(1, 0.05, n), 1.6, 59.0)
    if outside:
        assert np.any(~L.in_bins(rp, rz, PAPER_PT, PZ)), "the fixture rows need some reco outside the grid"
    return {"entry": e, "reco_pt": rp, "reco_pz": rz, "true_pt": tp, "true_pz": tz, "w_reco": w, "w_truth": w * 1.1}


def save_rows(rows, name) -> Path:
    p = TD / "stage" / name
    np.savez(p, **rows)
    return p


@unittest.skipUnless(HAVE_ROOT, "needs PyROOT, LightGBM and scikit-learn")
class Driver(unittest.TestCase):
    """The patched driver (oofvc_driver.diff) on RE-2's fixture."""

    @classmethod
    def setUpClass(cls):
        t = tree()
        cls.patched = t / "2d-unfolding" / "re2" / "re2_driver.py"
        plain = TD / "plain" / "2d-unfolding" / "re2"
        if not plain.exists():
            shutil.copytree(t / "2d-unfolding", TD / "plain" / "2d-unfolding")
            shutil.copytree(t / "unbinned_unfolding", TD / "plain" / "unbinned_unfolding")
            subprocess.run(["git", "apply", "-R", str(HERE / "oofvc_driver.diff")], cwd=str(TD / "plain"), check=True)
        cls.plain = plain / "re2_driver.py"
        cls.off = TD / "patched" / "out.root"  # the same file name as the plain run's, so runArgv compares
        if not cls.off.exists():
            cls.off.parent.mkdir(exist_ok=True)
            run_driver(cls.patched, cls.off)
        cls.rows = fixture_rows()
        cls.rows_path = save_rows(cls.rows, "rows.npz")
        cls.R = TD / "R.root"
        if not cls.R.exists():
            run_driver(cls.patched, cls.R, ["--signal-convention", "minerva", "--oofvc-rows", str(cls.rows_path)])

    def test_plain_is_tier1s_driver(self):
        import hashlib
        self.assertEqual(hashlib.sha256(self.plain.read_bytes()).hexdigest(),
                         "677ac75f1d171ca7d71223f62bf3426f056e41b1b6cc8bfd433d49528a1371e8")

    def test_flag_off_is_byte_identical(self):
        """--signal-convention production (the default): every histogram, parameter and record equals the unpatched
        driver's, bit for bit, apart from the driver's own path and digest, and runConfig's record of the two new
        options at their defaults (signal_convention "production", oofvc_rows null)."""
        plain = TD / "plain" / "out.root"
        plain.parent.mkdir(exist_ok=True)
        run_driver(self.plain, plain)
        a, b = contents(plain), contents(self.off)
        self.assertEqual(sorted(a), sorted(b))
        differ = sorted(k for k in a if a[k] != b[k])
        self.assertEqual([k for k in differ if k not in ("driverFile", "driverSha256", "omnifoldHelperFile",
                                                         "runConfig", "runArgv")], [])
        va, vb = json.loads(a["runArgv"]), json.loads(b["runArgv"])  # equal but for the output directory
        va[va.index("--out") + 1] = vb[vb.index("--out") + 1] = None
        va[0] = vb[0] = None  # argv[0], the driver's own path
        self.assertEqual(va, vb)
        self.assertIn("driverSha256", differ)
        ca, cb = json.loads(a["runConfig"]), json.loads(b["runConfig"])
        ca["out"] = cb["out"] = None
        self.assertEqual({k: cb.pop(k) for k in ("signal_convention", "oofvc_rows")},
                         {"signal_convention": "production", "oofvc_rows": None})
        self.assertEqual(ca, cb)

    def test_minerva_moves_the_rows(self):
        """C-MOVE and C-FIX on the fixture: the background loses exactly the moved rows reconstructed in the grid,
        the truth input gains their truth weight at their true cell, and the denominator, data, flux and exposure
        are unchanged."""
        r = self.rows
        a, b = contents(self.off), contents(self.R)
        for k in ("hOFTruthDenom2D", "hDataReco2D", "hFlux_pt", "dataPOT", "mcPOT", "potScale", "nNucleons"):
            self.assertEqual(a[k], b[k], k)
        pot = b["potScale"]
        g = L.global_index(r["reco_pt"], r["reco_pz"], PAPER_PT, PZ)
        moved = np.bincount(g[g >= 0], weights=r["w_reco"][g >= 0] * pot, minlength=224)
        db = th2v(self.off, "hBkgReco2D") - th2v(self.R, "hBkgReco2D")
        np.testing.assert_allclose(db, moved, rtol=0, atol=1e-12 * max(1.0, np.abs(th2v(self.off, "hBkgReco2D")).max()))
        inside = L.in_bins(r["reco_pt"], r["reco_pz"], PAPER_PT, PZ)
        t = L.global_index(r["true_pt"], r["true_pz"], PAPER_PT, PZ)
        sel = inside & (t >= 0)
        gained = np.bincount(t[sel], weights=r["w_truth"][sel] * pot, minlength=224)
        dt = th2v(self.R, "hOFInputTruth2D") - th2v(self.off, "hOFInputTruth2D")
        np.testing.assert_allclose(dt, gained, rtol=0, atol=1e-10)
        self.assertNotEqual(a["hXSec2D"], b["hXSec2D"])

    def test_refusals(self):
        """--oofvc-rows only with minerva, and minerva only on the central negweight-refined path."""
        rp = str(self.rows_path)
        for extra in (["--signal-convention", "minerva"], ["--oofvc-rows", rp],
                      ["--signal-convention", "minerva", "--oofvc-rows", rp, "--closure"]):
            p = run_driver(self.patched, TD / "refused.root", extra, check=False)
            self.assertNotEqual(p.returncode, 0, extra)
            self.assertIn("[FAIL]", p.stdout + p.stderr, extra)
        fx, flux = write_fixture()
        for argv in ([a if a != "negweight-refined" else "purity" for a in ARGV],
                     [a for a in ARGV if a != "--use-weights"]):
            p = subprocess.run([sys.executable, "-B", str(self.patched), "--omnifile", str(fx), "--mcfile", str(flux),
                                *argv, "--signal-convention", "minerva", "--oofvc-rows", rp, "--out",
                                str(TD / "refused.root")], capture_output=True, text=True, cwd=str(self.patched.parent))
            self.assertNotEqual(p.returncode, 0, argv)
            self.assertIn("central CV path only", p.stdout + p.stderr, argv)

    def test_weight_rules_drop_and_count(self):
        """A moved row with a truth weight outside the signal loader's rule is dropped and counted, as that loader
        drops its own, and the run goes on (codex-school r1 #8)."""
        r = {k: v.copy() for k, v in self.rows.items()}
        inside = np.flatnonzero(L.in_bins(r["reco_pt"], r["reco_pz"], PAPER_PT, PZ))
        r["w_truth"][inside[0]] = 2.0e4
        p = run_driver(self.patched, TD / "weights.root",
                       ["--signal-convention", "minerva", "--oofvc-rows", str(save_rows(r, "weights.npz"))])
        self.assertIn("'dropped_appended_weight': 1", p.stdout)
        self.assertIn(f"'appended': {inside.size - 1}", p.stdout)

    def test_bad_rows_fail(self):
        """A row whose reco values or weight differ from its entry's, a repeated entry, an entry the tree lacks, a true
        muon outside the grid, or a wrong key set: the driver fails before unfolding."""
        base = self.rows
        cases = {}
        r = {k: v.copy() for k, v in base.items()}; r["w_reco"][3] *= 1 + 1e-15; cases["weight"] = (r, "does not carry")
        r = {k: v.copy() for k, v in base.items()}; r["entry"][1] = r["entry"][0]; cases["repeat"] = (r, "distinct")
        r = {k: v.copy() for k, v in base.items()}; r["entry"][-1] = 10 ** 7; cases["absent"] = (r, "found in mc_background")
        r = {k: v.copy() for k, v in base.items()}; r["true_pz"][2] = 60.0; cases["truth"] = (r, "outside the grid")
        r = {k: v for k, v in base.items() if k != "w_truth"}; cases["keys"] = (r, "keys")
        for name, (rows, msg) in cases.items():
            p = run_driver(self.patched, TD / f"bad_{name}.root",
                           ["--signal-convention", "minerva", "--oofvc-rows", str(save_rows(rows, f"bad_{name}.npz"))],
                           check=False)
            self.assertNotEqual(p.returncode, 0, name)
            self.assertIn(msg, p.stdout + p.stderr, name)


def configure_tree_for_fixture():
    """Tests only: point the deploy tree's config.json at the fixture (its digests, this machine's CPUs and thread
    environment, two iterations), as test_ref_c2c1.py does in memory."""
    import hashlib
    C = ref_c2c1()
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
    """oofvc_run.py's four units on the fixture (numpy unfolder: no libRooUnfold here)."""

    @classmethod
    def setUpClass(cls):
        configure_tree_for_fixture()
        cls.rows = fixture_rows(seed=5)
        cls.rows_path = save_rows(cls.rows, "oofvc_rows.npz")  # the production file name, which the scorer requires
        import hashlib
        cls.out = TD / "units"
        # in-process, with O_NOATIME substituted as test_ref_c2c1.py does (macOS has none; O_NONBLOCK is inert on a
        # regular file's open)
        import oofvc_run
        cls.run_main = staticmethod(oofvc_run.main)
        with mock.patch.object(os, "O_NOATIME", os.O_NONBLOCK, create=True):
            cls.rc = oofvc_run.main(["--tree", str(tree()), "--rows", str(cls.rows_path), "--rows-sha256",
                                     hashlib.sha256(cls.rows_path.read_bytes()).hexdigest(), "--out", str(cls.out),
                                     "--numpy-unfolder"])

    def test_units_pass(self):
        self.assertEqual(self.rc, 0)
        for conv in ("off", "R"):
            for kind in ("er", "c2_central"):
                self.assertEqual(json.loads((self.out / conv / f"{kind}.done").read_text())["verdict"], "PASS")
            n = json.loads((self.out / conv / "c2_central.oofvc.json").read_text())
            self.assertTrue(all(c["pass"] for c in n["n_controls"].values()), n)
        pins = [json.loads(p.read_text()) for p in self.out.glob("pins_*.json")]
        self.assertTrue(pins and all(p["pass"] for p in pins))

    def test_r_units_carry_the_option(self):
        rec = json.loads((self.out / "R" / "er.oofvc.json").read_text())
        self.assertEqual(rec["argv"][-4:], ["--signal-convention", "minerva", "--oofvc-rows", str(self.rows_path)])
        self.assertEqual(rec["argv"][rec["argv"].index("--oofvc-rows") + 1], str(self.rows_path))
        off = json.loads((self.out / "off" / "er.oofvc.json").read_text())
        self.assertNotIn("--signal-convention", off["argv"])
        inside = L.in_bins(self.rows["reco_pt"], self.rows["reco_pz"], PAPER_PT, PZ)
        self.assertEqual(rec["n_signal_rows"] - off["n_signal_rows"], int(inside.sum()))
        self.assertEqual(rec["oofvc_counts"], {"appended": int(inside.sum()), "outside": int((~inside).sum()),
                                               "dropped_appended_weight": 0, "dropped_outside_weight": 0})
        self.assertIsNone(off["oofvc_counts"])
        n = json.loads((self.out / "R" / "c2_central.oofvc.json").read_text())["n_controls"]
        self.assertTrue(n["C-NMOVED"]["pass"] and n["C-NMOVED"]["sum"] > 0, n)

    def test_n_is_the_factor_on_the_units_trajectory(self):
        """N's saved trajectory is the unit's trajectory times sum M / (sum M + O), and O's moved part is the rows
        reconstructed outside the grid, at their true cell, POT-scaled."""
        for conv in ("off", "R"):
            z = np.load(self.out / conv / "c2_central.npz", allow_pickle=True)
            n = np.load(self.out / conv / "n.npz", allow_pickle=True)
            np.testing.assert_array_equal(n["ks"], z["ks"])
            np.testing.assert_allclose(n["unfolded_N"], z["unfolded"] * n["factor"][None, :], rtol=0, atol=0)
            self.assertTrue(np.all(n["factor"] <= 1) and np.all(n["factor"] > 0))
        n = np.load(self.out / "R" / "n.npz")
        r = self.rows
        out = ~L.in_bins(r["reco_pt"], r["reco_pz"], PAPER_PT, PZ)
        pot = contents(self.out / "R" / "er.root")["potScale"]
        np.testing.assert_allclose(n["O_moved"], L.o_vector(r["true_pt"][out], r["true_pz"][out],
                                                            r["w_reco"][out] * pot, PAPER_PT, PZ), rtol=1e-15)
        self.assertGreater(n["O_moved"].sum(), 0)
        np.testing.assert_array_equal(np.load(self.out / "off" / "n.npz")["O_moved"], 0)

    def test_wrong_rows_sha_refused(self):
        import contextlib, io
        err = io.StringIO()
        with mock.patch.object(os, "O_NOATIME", os.O_NONBLOCK, create=True), contextlib.redirect_stderr(err):
            rc = self.run_main(["--tree", str(tree()), "--rows", str(self.rows_path), "--rows-sha256", "0" * 64,
                                "--out", str(TD / "units_refused")])
        self.assertEqual(rc, 4)
        self.assertIn("not the join's", err.getvalue())
        self.assertFalse((TD / "units_refused").exists())


    def test_scorer_controls_on_the_fixture_units(self):
        """oofvc_score.py on the fixture's units: C-FIX, C-MOVE and C-KS pass, and every unit's digests, argv and
        convention check out (properties of these units). C-BASE fails (the fixture is not Tier 1's input), and the
        numpy-unfolder units fail the unfolder checks and C-PINS (no RooUnfold digest), so the reading is STOP and no
        operand is printed."""
        import hashlib
        join = TD / "score_join.json"
        join.write_text(json.dumps({"verdict": "PASS", "rows_sha256": hashlib.sha256(self.rows_path.read_bytes()).hexdigest(),
                                    "pot_scale": contents(self.out / "R" / "er.root")["potScale"], "classes": {}}))
        p = subprocess.run([sys.executable, "-B", str(HERE / "oofvc_score.py"), "--units", str(self.out), "--join",
                            str(join), "--rows", str(self.rows_path), "--tree", str(tree()), "--repo", str(REPO),
                            "--tool-commit", "HEAD"],
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 8, p.stderr[-2000:])
        rec = json.loads(p.stdout)
        c = rec["controls"]
        self.assertTrue(c["C-FIX"]["pass"], c["C-FIX"])
        self.assertTrue(c["C-MOVE"]["pass"], c["C-MOVE"])
        self.assertTrue(c["C-KS"]["pass"])
        self.assertTrue(c["C-IN"]["pass"])
        self.assertFalse(c["C-BASE"]["pass"])
        self.assertFalse(c["C-PINS"]["pass"])
        for u, chk in c["C-UNITS"]["checks"].items():
            for k in ("verdict", "npz_digest", "root_digest", "argv_recorded", "convention"):
                self.assertTrue(chk[k], (u, k))
            self.assertFalse(chk["not_numpy_unfolder"], u)
            self.assertFalse(chk["argv_is_E_R"], u)  # the fixture runs two iterations on fixture files
        self.assertFalse(c["C-UNITS"]["checks"]["R/c2_central"]["C-ROO_ran"])
        # every unit file is covered by its process's recorded digests, and a changed n.npz is caught
        pins = [json.loads(p.read_text()) for p in self.out.glob("pins_*.json")]
        self.assertTrue(all("n.npz" in p["outputs"][u] for p in pins for u in p["units"] if u.endswith("c2_central")))
        self.assertEqual(rec["reading"], "STOP")
        self.assertNotIn("operands", rec)


# ----------------------------------------------------------------------------------------------- the join


PT_OLD = [0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55, 0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50]


def write_tree(f, name, cols):
    import ROOT
    from array import array
    t = ROOT.TTree(name, name)
    bufs = {}
    for k, v in cols.items():
        code, leaf = {"f": ("d", "D"), "i": ("q", "L"), "u": ("B", "b")}[v.dtype.kind]
        if v.dtype.kind == "i" and v.dtype.itemsize == 4:
            code, leaf = "i", "I"
        bufs[k] = array(code, [0])
        t.Branch(k, bufs[k], f"{k}/{leaf}")
    for i in range(next(iter(cols.values())).size):
        for k, v in cols.items():
            bufs[k][0] = v[i].item()
        t.Fill()
    t.Write()


def oflow_split(omni_bkg, labels, pot_scale) -> dict:
    """oflow/remote3.sh's categories, reimplemented here from that script (not from oofvc_join), for C-LAB's
    reference."""
    pt, pz, w = (omni_bkg[k].astype(float) for k in ("sim_background", "sim_background_pz", "w_bkg"))
    ok = (omni_bkg["sim_background_pass"] != 0) & np.isfinite(pt) & np.isfinite(pz) & np.isfinite(w) & (w >= 0) & (w < 1e6)
    x, y, z = labels["vtx_x"], labels["vtx_y"], labels["vtx_z"]
    ap = 850.0; side = ap * 2 / np.sqrt(3)
    fid = (np.abs(x) <= ap) & ((np.abs(y) < side / 2) | (np.abs(y) < side - np.abs(x) * (side / 2) / ap)) & (z >= 5980) & (z <= 8422)
    cc = (labels["nu_pdg"] == 14) & (labels["current"] == 1)
    PT = np.array(PT_OLD); PZa = np.array(PZ)
    ip = np.searchsorted(PT, pt, side="right") - 1; iz = np.searchsorted(PZa, pz, side="right") - 1
    g = np.where((ip >= 0) & (ip < 14) & (iz >= 0) & (iz < 16), ip * 16 + iz, -1)
    out = {}
    for name, sel in [("FAKE_PS", cc & fid), ("FAKE_VTX", cc & ~fid), ("OTHER", ~cc)]:
        m = ok & sel & (g >= 0)
        out[name] = np.bincount(g[m], weights=w[m] * pot_scale, minlength=224).tolist(); out[name + "_n"] = int(m.sum())
    return out


class JoinFixture:
    """A small omnifile (mc_background, mc_signal_reco, the POT parameters) and its 12 dumps, consistent by
    construction; `mutate` edits the dump rows before they are written."""

    def __init__(self, d: Path, mutate=None, seed=7, dup_weight=0.01):
        import ROOT
        self.d = d
        d.mkdir(parents=True)
        rng = np.random.default_rng(seed)
        nb, ns = 900, 1200
        bkg = {"sim_background": rng.uniform(0, 4.6, nb), "sim_background_pz": rng.uniform(1.4, 30, nb),
               "sim_background_pass": np.ones(nb, np.uint8), "w_bkg": rng.uniform(0.1, 2, nb)}
        bkg["sim_background"][:5] = 5.0  # some reco outside the grid
        # one event filled twice (identical background rows), light enough for the 0.1% bound
        bkg["w_bkg"][nb - 2] = dup_weight
        for k in bkg:
            bkg[k][nb - 1] = bkg[k][nb - 2]
        lab = {"nu_pdg": rng.choice([14, 14, 14, -14, 12], nb).astype(np.int32),
               "current": rng.choice([1, 1, 1, 2], nb).astype(np.int32),
               "vtx_x": rng.uniform(-1000, 1000, nb), "vtx_y": rng.uniform(-1000, 1000, nb),
               "vtx_z": rng.uniform(5000, 9000, nb)}
        tpt, tpz = rng.uniform(0, 5.0, nb), rng.uniform(1.4, 40, nb)
        for k in lab:
            lab[k][nb - 1] = lab[k][nb - 2]
        tpt[nb - 1], tpz[nb - 1] = tpt[nb - 2], tpz[nb - 2]
        sel = (rng.uniform(size=ns) < 0.8).astype(np.uint8)
        sig = {"sim": np.where(sel == 1, rng.uniform(0, 4.5, ns), -9999.0),
               "sim_pz": np.where(sel == 1, rng.uniform(1.5, 30, ns), -9999.0), "sim_pass": sel,
               "w_reco": rng.uniform(0.1, 2, ns), "MC": rng.uniform(0, 4.5, ns), "MC_pz": rng.uniform(1.5, 30, ns),
               "w_truth": rng.uniform(0.1, 2, ns)}
        f = ROOT.TFile.Open(str(d / "cv.root"), "RECREATE")
        write_tree(f, "mc_background", bkg)
        write_tree(f, "mc_signal_reco", sig)
        ROOT.TParameter("double")("dataPOTUsed", 1.0e20).Write()
        ROOT.TParameter("double")("mcPOTUsed", 4.0e20).Write()
        f.Close()
        self.pot = 0.25
        self.bkg, self.lab, self.tpt, self.tpz, self.sig = bkg, lab, tpt, tpz, sig
        # the dump: every background row (to_bkg) and every selected signal row (to_sig), plus one to_sig duplicate
        sidx = np.flatnonzero(sel == 1)
        rows = {"entry": np.arange(nb + sidx.size + 1, dtype=np.int64),
                "to_bkg": np.r_[np.ones(nb), np.zeros(sidx.size + 1)].astype(np.uint8),
                "to_sig": np.r_[np.zeros(nb), np.ones(sidx.size + 1)].astype(np.uint8),
                "dup_sig": np.r_[np.zeros(nb + sidx.size), 1].astype(np.uint8),
                "mc_run": np.r_[np.arange(nb), 100000 + sidx, 100000 + sidx[0]].astype(np.int32),
                "mc_subrun": np.ones(nb + sidx.size + 1, np.int32),
                "mc_nthEvtInFile": np.ones(nb + sidx.size + 1, np.int32),
                "reco_pt": np.r_[bkg["sim_background"], sig["sim"][sidx], sig["sim"][sidx[0]]],
                "reco_pz": np.r_[bkg["sim_background_pz"], sig["sim_pz"][sidx], sig["sim_pz"][sidx[0]]],
                "w_reco": np.r_[bkg["w_bkg"], sig["w_reco"][sidx], sig["w_reco"][sidx[0]]],
                "true_pt": np.r_[tpt, sig["MC"][sidx], sig["MC"][sidx[0]]],
                "true_pz": np.r_[tpz, sig["MC_pz"][sidx], sig["MC_pz"][sidx[0]]],
                "w_truth": np.r_[bkg["w_bkg"] * 1.1, sig["w_truth"][sidx], sig["w_truth"][sidx[0]]],
                "theta_true": np.zeros(nb + sidx.size + 1),
                "nu_pdg": np.r_[lab["nu_pdg"], np.full(sidx.size + 1, 14)].astype(np.int32),
                "current": np.r_[lab["current"], np.ones(sidx.size + 1)].astype(np.int32),
                "vtx_x": np.r_[lab["vtx_x"], np.zeros(sidx.size + 1)],
                "vtx_y": np.r_[lab["vtx_y"], np.zeros(sidx.size + 1)],
                "vtx_z": np.r_[lab["vtx_z"], np.full(sidx.size + 1, 7000.0)]}
        rows["mc_run"][nb - 1] = rows["mc_run"][nb - 2]  # the duplicated background event: one key
        ap = 850.0
        x, y, z = rows["vtx_x"], rows["vtx_y"], rows["vtx_z"]
        rows["fid"] = ((np.abs(y) < -np.abs(x) / np.sqrt(3) + 2 * ap / np.sqrt(3)) & (np.abs(x) < ap)
                       & (z >= 5980) & (z <= 8422)).astype(np.uint8)
        if mutate:
            mutate(rows)
        self.rows = rows
        dd = d / "dumps"
        dd.mkdir()
        part = np.arange(rows["entry"].size) % 12
        part[nb - 1] = part[nb - 2]  # an AnaTuple double-fill lies within one playlist
        for i, pl in enumerate(("1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P")):
            g = ROOT.TFile.Open(str(dd / f"{pl}.root"), "RECREATE")
            write_tree(g, "rows", {k: v[part == i] for k, v in rows.items()})
            g.Close()
        (d / "split.json").write_text(json.dumps(oflow_split(bkg, lab, self.pot)))

    def run(self):
        out = self.d / "join"
        p = subprocess.run([sys.executable, "-B", str(HERE / "oofvc_join.py"), "--omnifile", str(self.d / "cv.root"),
                            "--dump-dir", str(self.d / "dumps"), "--split", str(self.d / "split.json"), "--out",
                            str(out)], capture_output=True, text=True)
        rec = json.loads((out / "join.json").read_text()) if (out / "join.json").exists() else None
        return p, rec, out


@unittest.skipUnless(HAVE_ROOT, "needs PyROOT")
class JoinTool(unittest.TestCase):
    """oofvc_join.py on a consistent fixture, then with one defect at a time."""

    _n = [0]

    def fixture(self, mutate=None, **kw):
        self._n[0] += 1
        return JoinFixture(TD / f"join{self._n[0]}", mutate, **kw)

    def test_pass_and_rows(self):
        fx = self.fixture()
        p, rec, out = fx.run()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertEqual(rec["verdict"], "PASS")
        self.assertEqual(rec["controls"]["C-JOIN"]["n_tied_groups"], 1)
        self.assertEqual(rec["controls"]["C-SIGW"]["n_dump_dup_sig"], 1)
        rows = dict(np.load(out / "oofvc_rows.npz"))
        cc = (fx.lab["nu_pdg"] == 14) & (fx.lab["current"] == 1)
        want = np.flatnonzero(cc & L.in_bins(fx.tpt, fx.tpz, PT_OLD, PZ))
        np.testing.assert_array_equal(rows["entry"], want)
        np.testing.assert_array_equal(rows["w_reco"], fx.bkg["w_bkg"][want])
        np.testing.assert_array_equal(rows["true_pt"], fx.tpt[want])
        np.testing.assert_array_equal(rows["w_truth"], fx.bkg["w_bkg"][want] * 1.1)
        self.assertEqual(rec["controls"]["C-LAB"]["max_rel"], 0.0)
        cls = rec["classes"]
        self.assertEqual(cls["moved_out_of_fiducial"]["rows"] + cls["moved_fiducial"]["rows"], want.size)
        self.assertEqual(cls["other"]["rows"], int((~cc).sum()))

    def _stop(self, mutate, control):
        p, rec, out = self.fixture(mutate).run()
        self.assertEqual(p.returncode, 8, p.stdout + p.stderr)
        self.assertEqual(rec["verdict"], "STOP")
        self.assertFalse(rec["controls"][control]["pass"])
        self.assertFalse((out / "oofvc_rows.npz").exists())

    def test_weight_off_by_one_ulp_stops(self):
        self._stop(lambda r: r["w_reco"].__setitem__(10, np.nextafter(r["w_reco"][10], 9.0)), "C-JOIN")

    def test_missing_background_row_stops(self):
        def m(r):
            r["to_bkg"][20] = 0; r["to_sig"][20] = 1; r["dup_sig"][20] = 1
        self._stop(m, "C-JOIN")

    def test_routing_disagreement_stops(self):
        self._stop(lambda r: r["to_sig"].__setitem__(30, 1), "C-ROUTE")

    def test_signal_truth_mismatch_stops(self):
        def m(r):
            i = int(np.flatnonzero(r["to_sig"] == 1)[3]); r["w_truth"][i] = np.nextafter(r["w_truth"][i], 9.0)
        self._stop(m, "C-SIGW")

    def test_tie_between_two_events_stops(self):
        def m(r):
            r["mc_run"][899] = 12345  # the duplicated background rows now claim two events
        self._stop(m, "C-JOIN")

    def test_tie_above_the_bound_stops(self):
        """The duplicated event weighing more than 0.1% of the moved weight: STOP (the director's bound)."""
        p, rec, out = self.fixture(dup_weight=1.9).run()
        self.assertEqual(p.returncode, 8, p.stdout + p.stderr)
        self.assertFalse(rec["controls"]["C-JOIN"]["pass"])
        self.assertIn("more than", rec["controls"]["C-JOIN"]["why"])

    def test_nan_in_split_stops(self):
        """A non-finite reference cell is a STOP, not a pass hidden by max() (codex-school r1 #9)."""
        fx = self.fixture()
        ref = json.loads((fx.d / "split.json").read_text())
        ref["FAKE_VTX"][17] = float("nan")
        (fx.d / "split.json").write_text(json.dumps(ref))
        p, rec, out = fx.run()
        self.assertEqual(p.returncode, 8)
        self.assertFalse(rec["controls"]["C-LAB"]["pass"])
        self.assertFalse(rec["controls"]["C-LAB"]["finite"])

    def test_labels_against_oflow(self):
        def m(r):
            r["nu_pdg"][50] = 14 if r["nu_pdg"][50] != 14 else -14
        p, rec, out = self.fixture(m).run()
        self.assertEqual(p.returncode, 8)
        self.assertFalse(rec["controls"]["C-LAB"]["pass"])


def tearDownModule():
    shutil.rmtree(TD, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
