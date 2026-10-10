"""The SB1 wrapper end to end: the real driver's ``main()`` under the real OI-136 guard, strict mode.

Each case runs in a throwaway git checkout holding the real driver, ``n2/``, the guard and its
shim, this package's ``sb1_run.py``/``branch_select.py``/``sb1_hash.py``, and a STUB OmniFold
helper whose ``omnifold`` returns unit weights, so nothing is trained. Inputs are a synthetic
omnifile and flux file outside the checkout. Covered:

* positive: both arms, strict, compare-digests, identical loader digests and histograms;
* refused before any input is read (exit 3): no guard, a wrong helper digest, a changed driver,
  an input changed after hashing, a wrong input digest, an uncommitted executed file, a reference
  receipt from different arguments;
* refused before training (exit 4): a reference whose digests differ;
* refused before the first read (exit 5): an omitted or extra activation on the real wrapper path.

    PYTHONPATH=$(root-config --libdir) python3.13 -m unittest test_sb1_guarded -v
"""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
sys.path.insert(0, str(HERE))
import make_fixture_omnifile as mk  # noqa: E402

REPO = PKG.parents[4]
PKG_REL = PKG.relative_to(REPO).as_posix()
N2 = "2d-unfolding/uq/coverage_fixed_truth/n2"
DRIVER = "2d-unfolding/unfold_2d_omnifold_unbinned.py"
HELPER = "unbinned_unfolding/python/omnifold.py"
GUARD = "nd-unfolding/mnv_guarded_run.py"
COPIED = (DRIVER, GUARD, f"{N2}/__init__.py", f"{N2}/execution.py",
          f"{PKG_REL}/sb1_run.py", f"{PKG_REL}/branch_select.py", f"{PKG_REL}/sb1_hash.py")
STUB_HELPER = '''import numpy as np


class OmniFold_helper_functions:
    def omnifold(MCgen, MCreco, measured, pass_reco, pass_truth, pass_measured, iters, **kw):
        n = int(np.count_nonzero(pass_truth))          # weights for the pass_truth events
        return np.ones(n), np.ones(n)
'''
LAT = "Muon_Energy_MINOS:0"


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), "-c", "core.hooksPath=/dev/null",
                           "-c", "user.name=fixture", "-c", "user.email=fixture@invalid", *args],
                          capture_output=True, text=True, check=True).stdout.strip()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def make_checkout(base, name, helper=STUB_HELPER):
    root = base / name
    (root / "nd-unfolding").mkdir(parents=True)
    (root / "VALIDATION_LEDGER.md").write_text("# fixture ledger\n")
    for rel in COPIED:
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO / rel, root / rel)
    shutil.copytree(REPO / "nd-unfolding/mnv_guard_shim", root / "nd-unfolding/mnv_guard_shim",
                    ignore=shutil.ignore_patterns("__pycache__"))
    (root / HELPER).parent.mkdir(parents=True, exist_ok=True)
    (root / HELPER).write_text(helper)
    git(root, "init", "-q")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "fixture")
    return root


def run(argv, cwd=None):
    env = dict(os.environ, OMP_NUM_THREADS="1", PYTHONDONTWRITEBYTECODE="1")
    for k in [k for k in env if k.startswith("MNV_GUARD")]:
        env.pop(k)
    return subprocess.run([sys.executable, *map(str, argv)], capture_output=True, text=True,
                          env=env, cwd=cwd)


def hist_bytes(path):
    """Every histogram in a driver output: contents and errors, under- and overflow included."""
    import ROOT
    import numpy as np
    f = ROOT.TFile.Open(str(path))
    out = {}
    for key in f.GetListOfKeys():
        h = key.ReadObj()
        if not h.InheritsFrom("TH1"):
            continue
        n = h.GetNcells()
        out[key.GetName()] = (np.array([h.GetBinContent(i) for i in range(n)]).tobytes(),
                              np.array([h.GetBinError(i) for i in range(n)]).tobytes())
    f.Close()
    return out


class Guarded(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.tmp = Path(cls._tmp.name).resolve()
        cls.omni = cls.tmp / "inputs" / "omni.root"
        cls.omni.parent.mkdir()
        mk.write_fixture(str(cls.omni), rows=4000, extra=8)
        cls.flux = Path(mk.write_flux(str(cls.tmp / "inputs" / "flux.root")))
        cls.root = make_checkout(cls.tmp, "A")
        cls.hashes = cls.tmp / "H0.json"
        r = run([cls.root / PKG_REL / "sb1_hash.py", "--out", cls.hashes, cls.omni, cls.flux])
        assert r.returncode == 0, r.stderr

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def expect(self, root=None, **override):
        root = root or self.root
        mods = {rel: sha(root / rel) for rel in
                (f"{PKG_REL}/sb1_run.py", f"{PKG_REL}/branch_select.py", f"{N2}/__init__.py",
                 f"{N2}/execution.py", DRIVER, HELPER)}
        exp = {"commit": git(root, "rev-parse", "HEAD"), "modules": mods,
               "inputs": {"omnifile": sha(self.omni), "mcfile": sha(self.flux)}}
        exp.update(override)
        path = self.tmp / f"expect-{len(list(self.tmp.glob('expect-*')))}.json"
        path.write_text(json.dumps(exp))
        return path

    def unfold(self, arm, tag, root=None, guard=True, expect=None, extra=(), universe=LAT,
               hashes=None, omni=None):
        root = root or self.root
        omni = omni or self.omni
        out = self.tmp / f"{tag}.root"
        receipt = self.tmp / f"{tag}.json"
        cmd = [root / PKG_REL / "sb1_run.py", "unfold", "--arm", arm, "--receipt", receipt,
               "--expect", expect or self.expect(root), "--require-provenance",
               "--input-hashes", hashes or self.hashes, *extra, "--",
               "--omnifile", omni, "--mcfile", self.flux, "--iters", "5", "--use-weights",
               "--estimator", "lgbm", "--universe", universe, "--seed", "42", "--out", out]
        if guard:
            cmd = [root / GUARD, "--expect-root", root, "--inventory", self.tmp / f"{tag}.inv",
                   "--label", tag, "--", *cmd]
        r = run(cmd, cwd=self.tmp)
        rec = json.loads(receipt.read_text()) if receipt.exists() and receipt.stat().st_size else None
        return r, rec, out

    def test_both_arms_strict_and_identical(self):
        r1, a, out_a = self.unfold("all", "pos-all")
        self.assertEqual(r1.returncode, 0, r1.stderr[-3000:])
        r2, b, out_b = self.unfold("selective", "pos-sel", extra=("--compare-digests",
                                                                  self.tmp / "pos-all.json"))
        self.assertEqual(r2.returncode, 0, r2.stderr[-3000:])
        for rec in (a, b):
            self.assertEqual(rec["status"], "complete")
            self.assertTrue(rec["identity"]["strict"])
            self.assertTrue(rec["identity"]["guard"]["installed"])
            self.assertEqual(rec["identity"]["git"]["mismatched"], [])
            self.assertEqual(len(rec["loaders"]), 4)
            names = [e["name"] for e in rec["phases"]]
            self.assertIn("omnifold", names)
            self.assertIn("driver:main", names)
        self.assertEqual([x["digests"] for x in a["loaders"]], [x["digests"] for x in b["loaders"]])
        self.assertEqual([x["settings"] for x in a["loaders"]],
                         [x["settings"] for x in b["loaders"]])
        self.assertEqual({x["mode"] for x in a["loaders"]}, {"all"})
        sel = {x["tree"]: x["branches"] for x in b["loaders"]}
        self.assertEqual(sel["mc_truth_denom"], ["pT_truth_Muon_Energy_MINOS_0",
                                                 "pz_truth_Muon_Energy_MINOS_0",
                                                 "w_truth_Muon_Energy_MINOS_0"])
        hists = hist_bytes(out_a)
        self.assertIn("hXSec2D", hists)
        self.assertGreaterEqual(len(hists), 14)
        self.assertEqual(hists, hist_bytes(out_b))
        helper = [r for r in b["identity"]["executed"] if r["relpath"] == HELPER]
        self.assertEqual(helper[0]["path"], str(self.root / HELPER))
        inv = [json.loads(line) for line in (self.tmp / "pos-sel.inv").read_text().splitlines()]
        self.assertTrue(inv and all(i.get("repo_origin_count", 0) >= 1 for i in inv))

    def assertRefused(self, r, rec, code=3, why=None):
        self.assertEqual(r.returncode, code, r.stderr[-2000:])
        if why:
            self.assertIn(why, r.stderr)

    def test_strict_without_the_guard_is_refused(self):
        r, rec, out = self.unfold("selective", "noguard", guard=False)
        self.assertRefused(r, rec, why="not running under")
        self.assertFalse(out.exists())

    def test_a_wrong_helper_digest_is_refused(self):
        exp = json.loads(self.expect().read_text())
        exp["modules"][HELPER] = "0" * 64
        path = self.tmp / "expect-badhelper.json"
        path.write_text(json.dumps(exp))
        r, rec, out = self.unfold("selective", "badhelper", expect=path)
        self.assertRefused(r, rec, why=HELPER)

    def test_a_changed_driver_is_refused_even_when_committed_and_stated(self):
        root = make_checkout(self.tmp, "changed-driver")
        with open(root / DRIVER, "a") as fh:
            fh.write("\n# edited\n")
        git(root, "commit", "-qam", "edit")
        r, rec, out = self.unfold("selective", "drv", root=root)
        self.assertRefused(r, rec, why="pinned loaders")

    def test_an_uncommitted_executed_file_is_refused(self):
        root = make_checkout(self.tmp, "dirty")
        with open(root / PKG_REL / "branch_select.py", "a") as fh:
            fh.write("\n# dirty\n")
        r, rec, out = self.unfold("selective", "dirty", root=root)
        self.assertRefused(r, rec, why="differ from HEAD")

    def test_an_input_changed_after_hashing_is_refused(self):
        moved = self.tmp / "inputs" / "omni-copy.root"
        shutil.copy2(self.omni, moved)
        h = self.tmp / "H0-copy.json"
        self.assertEqual(run([self.root / PKG_REL / "sb1_hash.py", "--out", h, moved,
                              self.flux]).returncode, 0)
        st = moved.stat()
        os.utime(moved, ns=(st.st_atime_ns, st.st_mtime_ns + 1000))       # same bytes, touched
        r, rec, out = self.unfold("selective", "touched", hashes=h, omni=moved)
        self.assertRefused(r, rec, why="differs from its hash record")
        self.assertFalse(out.exists())

    def test_a_wrong_input_digest_is_refused(self):
        r, rec, out = self.unfold("selective", "badinput",
                                  expect=self.expect(inputs={"omnifile": "f" * 64,
                                                             "mcfile": sha(self.flux)}))
        self.assertRefused(r, rec, why="expected")

    def test_a_reference_from_other_arguments_is_refused(self):
        r1, _, _ = self.unfold("all", "ref-flux-args", universe="GEANT_Neutron:0")
        self.assertEqual(r1.returncode, 0, r1.stderr[-2000:])
        r, rec, out = self.unfold("selective", "otherargs",
                                  extra=("--compare-digests", self.tmp / "ref-flux-args.json"))
        self.assertRefused(r, rec, why="not")

    def test_a_reference_with_different_bytes_stops_before_training(self):
        r1, ref, _ = self.unfold("all", "ref-tamper")
        self.assertEqual(r1.returncode, 0, r1.stderr[-2000:])
        ref["loaders"][2]["digests"]["w_reco"] = "0" * 64      # collect_signal_arrays_2d
        bad = self.tmp / "ref-tampered.json"
        bad.write_text(json.dumps(ref))
        r, rec, out = self.unfold("selective", "tampered", extra=("--compare-digests", bad))
        self.assertRefused(r, rec, code=4)
        self.assertEqual(rec["status"], "input-mismatch")
        self.assertNotIn("omnifold", [e["name"] for e in rec["phases"]])

    def loaders(self, tag, control):
        receipt = self.tmp / f"{tag}.json"
        cmd = [self.root / GUARD, "--expect-root", self.root, "--", self.root / PKG_REL /
               "sb1_run.py", "loaders", "--arm", "selective", "--receipt", receipt,
               "--omnifile", self.omni, "--universe", LAT, "--trees", "mc_signal_reco",
               "--negative-control", control]
        r = run(cmd, cwd=self.tmp)
        return r, json.loads(receipt.read_text())

    def test_activation_controls_are_refused_on_the_wrapper_path(self):
        for tag, control, why in (("omit", "omit:w_reco_Muon_Energy_MINOS_0", "inactive"),
                                  ("extra", "extra:w_truth", "active")):
            with self.subTest(control=control):
                r, rec = self.loaders(f"nc-{tag}", control)
                self.assertEqual(r.returncode, 5, r.stderr[-2000:])
                self.assertEqual(rec["status"], "selection-refused")
                self.assertIn(why, rec["error"])
                self.assertEqual(rec["loaders"], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
