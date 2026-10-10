"""Strict KI-85 provenance with the real analyzer and its final dependency set.

``test_producer_provenance.py`` stubs ``analyze_uq``: its stub imports only ``technote_style``, the
dependency the real file had when the guard lane froze. The real ``analyze_uq.py`` now also imports
``2d-unfolding/uq/reported_cells.py`` (structure lane, 2026-10-09). This file puts the real analyzer,
``reported_cells.py`` and ``technote_style.py`` in the throwaway checkout, so it fails if strict mode
accepts expectations that omit a dependency, a changed dependency, a commit that predates the final
implementation, or a dependency added later that no expectation names.

Needs PyROOT and matplotlib, which the real analyzer imports. Locally:
  PYTHONPATH=$(root-config --libdir) <python3.13 with matplotlib> -m unittest discover -s \
      2d-unfolding/uq/coverage_fixed_truth/n2 -p 'test_producer*.py' -v
"""
import json
import shutil
import tempfile
import textwrap
import unittest
from pathlib import Path

import numpy as np

from test_producer_provenance import (ANALYZE, HAVE_ROOT, KI85, REPO, git, gx, make_checkout, run,
                                      sha)

try:
    import matplotlib  # noqa: F401
    HAVE_MPL = True
except Exception:  # pragma: no cover - depends on the host
    HAVE_MPL = False

CELLS = "2d-unfolding/uq/reported_cells.py"
STYLE = "technote_style.py"
RUNNER = "2d-unfolding/uq/coverage_fixed_truth/run_ki85_fixture.py"
EXTRA = "2d-unfolding/uq/cells_extra.py"
N_PT, N_PZ = 14, 16


def write_replicas(data, rng, T, rep):
    """The 50 + 50 + 200 replica files ``ki85_compare.main`` reads; returns the arrays it should."""
    import ROOT
    arrays = {}
    for arm, pattern, n, s in (("armB", "armB/boot{}.root", 50, 0.010),
                               ("armT", "armT/toy{}.root", 50, 0.012),
                               ("realboot", "boot_data/2d_xsec_MEFHC_5iter_lgbm_boot{}.root", 200,
                                0.02)):
        X = []
        for i in range(1, n + 1):
            v = T * (1 + s * rng.standard_normal(T.shape))
            p = data / pattern.format(i)
            p.parent.mkdir(parents=True, exist_ok=True)
            f = ROOT.TFile(str(p), "RECREATE")
            h = ROOT.TH2D("hXSec2D", "", N_PT, 0, 1, N_PZ, 0, 1)
            for ix in range(N_PT):
                for iy in range(N_PZ):
                    h.SetBinContent(ix + 1, iy + 1, v[ix, iy])
            h.Write()
            f.Close()
            if arm != "realboot":
                Path(str(p) + ".done").touch()
            X.append(v.ravel(order="C")[rep.ravel(order="C")])
        arrays[arm] = np.array(X)
    return arrays


@unittest.skipUnless(HAVE_ROOT and HAVE_MPL, "needs PyROOT and matplotlib (the real analyzer)")
class TheRealAnalyzer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.tmp = Path(cls._tmp.name).resolve()
        rng = np.random.default_rng(20261009)
        cls.T = rng.uniform(1, 2, (N_PT, N_PZ))
        cls.rep = np.zeros((N_PT, N_PZ), bool)
        cls.rep.flat[:40] = True
        cls.arrays = write_replicas(cls.tmp / "data", rng, cls.T, cls.rep)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def setUp(self):
        """Commit ``old``: the guard lane's stub layout. Commit ``final``: the real analyzer, its
        real dependencies, the two small inputs and a runner pointing at the replica fixture."""
        self.work = Path(tempfile.mkdtemp(dir=self.tmp))
        self.a = make_checkout(self.work, "A", 2)
        self.old = git(self.a, "rev-parse", "HEAD")
        for rel in (ANALYZE, CELLS, STYLE):
            shutil.copy2(REPO / rel, self.a / rel)
        state = self.a / "docs/orchestration/state"
        (state / "coverage-2d-20261005").mkdir(parents=True)
        (state / "ki84-adopt-20261006").mkdir(parents=True)
        np.savez(state / "coverage-2d-20261005/interim.npz", reported=self.rep, prod_mean=self.T,
                 T=self.T)
        (state / "ki84-adopt-20261006/purity_fdata.json").write_text(
            json.dumps({"purity_reco": np.ones((N_PT, N_PZ)).tolist()}))
        (self.a / RUNNER).write_text(textwrap.dedent(f'''\
            import sys
            import ki85_compare as kc
            kc.OUTROOT = {str(self.tmp / "data")!r}
            kc.REALBOOT = {str(self.tmp / "data/boot_data")!r}
            sys.argv = ["ki85_compare.py"] + sys.argv[1:]
            kc.main()
            '''))
        self.final = self.commit("real analyzer and its dependencies")
        self.out = self.work / "k.json"

    def commit(self, message):
        git(self.a, "add", "-A")
        git(self.a, "commit", "-q", "-m", message)
        return git(self.a, "rev-parse", "HEAD")

    def modules(self, *extra):
        return {rel: sha(self.a / rel) for rel in (
            RUNNER, KI85, ANALYZE, CELLS, STYLE,
            "2d-unfolding/uq/coverage_fixed_truth/n2/__init__.py",
            "2d-unfolding/uq/coverage_fixed_truth/n2/execution.py", *extra)}

    def expect(self, commit=None, modules=None):
        state = self.a / "docs/orchestration/state"
        return {"commit": commit or git(self.a, "rev-parse", "HEAD"),
                "modules": self.modules() if modules is None else modules,
                "inputs": {"interim": sha(state / "coverage-2d-20261005/interim.npz"),
                           "purity": sha(state / "ki84-adopt-20261006/purity_fdata.json")}}

    def strict(self, exp):
        path = self.work / "kexp.json"
        path.write_text(json.dumps(exp))
        return run([self.a / "nd-unfolding/mnv_guarded_run.py", "--expect-root", self.a, "--",
                    self.a / RUNNER, "--out", self.out, "--expect", path, "--require-provenance"])

    def assertRefused(self, cp, *needles):
        self.assertEqual(cp.returncode, gx.REFUSAL_EXIT, cp.stdout[-1500:] + cp.stderr[-3000:])
        for needle in needles:
            self.assertIn(needle, cp.stderr)
        self.assertFalse(self.out.exists(), "a refused strict run left an output")

    def test_strict_run_with_the_final_dependency_set_runs_and_records_it(self):
        """Positive control: every executed repository file is stated, at HEAD, and recorded."""
        exp = self.expect()
        cp = self.strict(exp)
        self.assertEqual(cp.returncode, 0, cp.stdout[-1500:] + cp.stderr[-3000:])
        res = json.loads(self.out.read_text())
        prov = res["provenance"]
        self.assertTrue(prov["strict"])
        self.assertEqual(prov["git"]["commit"], self.final)
        self.assertEqual(prov["git"]["mismatched"], [])
        executed = {r["relpath"]: r for r in prov["executed"]}
        self.assertEqual(set(executed), set(exp["modules"]))
        self.assertEqual(executed[CELLS]["loader"], "import")
        self.assertEqual(executed[CELLS]["sha256"], sha(REPO / CELLS))
        self.assertEqual(executed[ANALYZE]["sha256"], sha(REPO / ANALYZE))
        import ki85_compare as kc
        rho = kc.per_bin_ratios(self.arrays["armB"], self.arrays["armT"], self.arrays["realboot"],
                                np.ones(int(self.rep.sum())))
        self.assertAlmostEqual(res["sigma_B_over_sigma_T"]["median"],
                               float(np.median(rho["rho1"])), places=12)

    def test_an_unstated_dependency_is_refused(self):
        for rel in (CELLS, STYLE):
            with self.subTest(rel):
                exp = self.expect()
                del exp["modules"][rel]
                self.assertRefused(self.strict(exp), "every executed module", rel)

    def test_a_changed_dependency_is_refused(self):
        stated = self.modules()
        with open(self.a / CELLS, "a") as fh:
            fh.write("# edited after the commit\n")
        with self.subTest("old digest stated"):
            self.assertRefused(self.strict(self.expect(modules=stated)), CELLS, "expected")
        with self.subTest("new digest stated, not committed"):
            self.assertRefused(self.strict(self.expect()), "differ from HEAD", CELLS)

    def test_a_commit_before_the_final_implementation_is_refused(self):
        self.assertRefused(self.strict(self.expect(commit=self.old)), "expected " + self.old)

    def test_a_dependency_added_later_is_discovered_without_being_named(self):
        """Discovery is a sweep of the imported modules, not a list of known import patterns."""
        stated = self.modules()
        (self.a / EXTRA).write_text("MARK = 'added later'\n")
        with open(self.a / CELLS, "a") as fh:
            fh.write("import cells_extra  # noqa: E402,F401\n")
        self.commit("reported_cells gains a dependency")
        exp = self.expect(modules=dict(stated, **{CELLS: sha(self.a / CELLS)}))
        self.assertRefused(self.strict(exp), EXTRA)
        cp = self.strict(self.expect(modules=self.modules(EXTRA)))
        self.assertEqual(cp.returncode, 0, cp.stdout[-1500:] + cp.stderr[-3000:])


if __name__ == "__main__":
    unittest.main()
