"""The COV2D ``--data-file`` hook in ``2d-unfolding/re2/re2_driver.py``.

Needs PyROOT, numpy, LightGBM and scikit-learn, as ``test_re2_driver.py`` does, and a git checkout (the pre-hook
driver is read from its blob). Run pinned:
    taskset -c 8-11 python -m unittest 2d-unfolding/re2/tests/test_re2_data_file.py -v

On ``test_re2_driver``'s synthetic omnifile, in the production configuration (negweight-refined, 400/31), every
histogram is compared bit for bit:

* without the flag, the hooked driver equals the pre-hook blob on the CV, a universe and a three-stream replica, and
  every other record is equal except the driver's own path and digest and the new ``data_file`` key of runConfig;
* ``--data-file`` naming a file that holds the omnifile's own data tree equals the run without the flag;
* ``--data-file`` naming other data equals the pre-hook driver on an omnifile whose data tree is that data
  (CV, universe, three-stream replica), and differs from the CV result;
* the output records the data file's sha256 only when the flag is set;
* the guards refuse a missing or different dataPOTUsed, a missing data tree, and ``--closure``.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_re2_driver as t  # noqa: E402

# re2_driver.py as RE-2 part B ran it (deploy dbdad2f9), before the hook.
PRE_HOOK_BLOB = "4c7e9d75508fce8ec4bf26c3dd0f037c96af858f"
PROD = ("--bkg-mode", "negweight-refined", "--refine-n-estimators", "400", "--refine-num-leaves", "31")
UNIV = ("--universe", f"{t.UNIVERSE[0]}:{t.UNIVERSE[1]}")
THREE = ("--bootstrap-seed", "7", "--bootstrap-streams", "three")
SAME_EXCEPT = {"driverFile", "driverSha256", "runConfig", "runArgv", "dataFileSha256"}


def write_data(path: Path, cols: dict, pot: float | None, tree: str = "data") -> None:
    """A file holding one data-shaped tree and, unless pot is None, dataPOTUsed."""
    import ROOT
    from array import array
    f = ROOT.TFile.Open(str(path), "RECREATE")
    tr = ROOT.TTree(tree, tree)
    bufs = {}
    for k, v in cols.items():
        code, leaf = ("B", "b") if v.dtype == np.uint8 else ("d", "D")
        bufs[k] = array(code, [0])
        tr.Branch(k, bufs[k], f"{k}/{leaf}")
    for i in range(next(iter(cols.values())).size):
        for k, v in cols.items():
            bufs[k][0] = v[i].item()
        tr.Fill()
    tr.Write()
    if pot is not None:
        ROOT.TParameter("double")("dataPOTUsed", pot).Write()
    f.Close()


def read_data(path: Path) -> dict:
    import ROOT
    f = ROOT.TFile.Open(str(path))
    tr = f.Get("data")
    out = {k: [] for k in ("measured", "measured_pz", "measured_pass")}
    for e in tr:
        for k in out:
            out[k].append(getattr(e, k))
    f.Close()
    return {"measured": np.array(out["measured"], float), "measured_pz": np.array(out["measured_pz"], float),
            "measured_pass": np.array([ord(x) if isinstance(x, str) else int(x) for x in out["measured_pass"]], np.uint8)}


def swap_data(src: Path, dst: Path, cols: dict) -> None:
    """dst = src with its data tree replaced by cols: every other tree and parameter copied."""
    import ROOT
    from array import array
    fi = ROOT.TFile.Open(str(src))
    fo = ROOT.TFile.Open(str(dst), "RECREATE")
    for key in fi.GetListOfKeys():
        obj = key.ReadObj()
        if key.GetName() == "data":
            continue
        fo.cd()
        if obj.InheritsFrom("TTree"):
            obj.CloneTree(-1).Write()
        else:
            obj.Write(key.GetName())
    fo.Close()
    fi.Close()
    tmp = dst.with_suffix(".data.root")
    write_data(tmp, cols, None)
    fd = ROOT.TFile.Open(str(tmp))
    fo = ROOT.TFile.Open(str(dst), "UPDATE")
    fo.cd()
    fd.Get("data").CloneTree(-1).Write()
    fo.Close()
    fd.Close()


def records(path: Path) -> dict:
    import ROOT
    f = ROOT.TFile.Open(str(path))
    out = {}
    for key in f.GetListOfKeys():
        obj = key.ReadObj()
        if obj.InheritsFrom("TNamed") and not obj.InheritsFrom("TH1") and obj.ClassName() == "TNamed":
            out[key.GetName()] = obj.GetTitle()
        elif obj.ClassName().startswith("TParameter"):
            out[key.GetName()] = repr(obj.GetVal())
    f.Close()
    return out


@unittest.skipUnless(t.HAVE, "needs PyROOT, LightGBM and scikit-learn")
class DataFileHook(t.RE2Driver):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        d = Path(cls.td.name)
        cls.pre_hook = d / "re2_driver_prehook.py"
        blob = subprocess.run(["git", "-C", str(t.REPO), "cat-file", "blob", PRE_HOOK_BLOB], check=True,
                              capture_output=True).stdout
        cls.pre_hook.write_bytes(blob)
        cls.pre_hook.chmod(0o755)
        code = (f"import sys; sys.path.insert(0, {str(Path(__file__).resolve().parent)!r}); "
                f"import test_re2_data_file as m, numpy as np; from pathlib import Path; "
                f"own = m.read_data(Path({str(cls.omni)!r})); "
                f"m.write_data(Path({str(d / 'own_data.root')!r}), own, 1.0e20); "
                f"r = np.random.default_rng(2026); n = 3500; "
                f"alt = {{'measured': r.uniform(0.02, 2.0, n), 'measured_pz': r.uniform(1.6, 18.0, n), "
                f"'measured_pass': (r.uniform(size=n) < 0.95).astype(np.uint8)}}; "
                f"m.write_data(Path({str(d / 'alt_data.root')!r}), alt, 1.0e20); "
                f"m.swap_data(Path({str(cls.omni)!r}), Path({str(d / 'alt_omni.root')!r}), alt); "
                f"m.write_data(Path({str(d / 'pot_differs.root')!r}), alt, 1.1e20); "
                f"m.write_data(Path({str(d / 'pot_missing.root')!r}), alt, None); "
                f"m.write_data(Path({str(d / 'no_data_tree.root')!r}), alt, 1.0e20, tree='other')")
        subprocess.run([sys.executable, "-c", code], check=True, env=cls.env)
        cls.own_data, cls.alt_data = d / "own_data.root", d / "alt_data.root"
        cls.alt_omni = d / "alt_omni.root"

    def run_on(self, script: Path, omni: Path, *extra: str, check: bool = True):
        saved, type(self).omni = self.omni, omni
        try:
            return self.run_driver(script, *extra, check=check)
        finally:
            type(self).omni = saved

    def assert_records(self, a: Path, b: Path):
        ra, rb = records(a), records(b)
        self.assertEqual(sorted(set(ra) - SAME_EXCEPT), sorted(set(rb) - SAME_EXCEPT))
        for k in set(ra) - SAME_EXCEPT:
            self.assertEqual(ra[k], rb[k], k)
        ca, cb = json.loads(ra["runConfig"]), json.loads(rb["runConfig"])
        ca.pop("data_file", None), cb.pop("data_file", None), ca.pop("out"), cb.pop("out")
        self.assertEqual(ca, cb)

    # -------------------------------------------------------------- absent flag == the pre-hook blob
    def test_absent_flag_equals_pre_hook(self):
        for extra in ((), UNIV, THREE):
            with self.subTest(extra=extra):
                old, _ = self.run_driver(self.pre_hook, *PROD, *extra)
                new, _ = self.run_driver(t.RE2, *PROD, *extra)
                self.assert_same(old, new)
                self.assert_records(old, new)
                rn = records(new)
                self.assertNotIn("dataFileSha256", rn)
                self.assertIsNone(json.loads(rn["runConfig"])["data_file"])
                self.assertNotIn("data_file", json.loads(records(old)["runConfig"]))

    # -------------------------------------------------------------- own data through the hook == no hook
    def test_own_data_through_the_hook(self):
        plain, _ = self.run_driver(t.RE2, *PROD)
        hooked, r = self.run_driver(t.RE2, *PROD, "--data-file", str(self.own_data))
        self.assert_same(plain, hooked)
        self.assertIn("COV2D: data tree from", r.stdout)
        self.assertEqual(records(hooked)["dataFileSha256"],
                         hashlib.sha256(self.own_data.read_bytes()).hexdigest())

    # -------------------------------------------------------------- other data == pre-hook on a swapped omnifile
    def test_other_data_equals_a_swapped_omnifile(self):
        cv, _ = self.run_driver(t.RE2, *PROD)
        for extra in ((), UNIV, THREE):
            with self.subTest(extra=extra):
                swapped, _ = self.run_on(self.pre_hook, self.alt_omni, *PROD, *extra)
                hooked, _ = self.run_driver(t.RE2, *PROD, *extra, "--data-file", str(self.alt_data))
                self.assert_same(swapped, hooked)
        moved = t.hists(hooked)["hXSec2D"][0]
        self.assertFalse(np.array_equal(t.hists(cv)["hXSec2D"][0], moved))

    # -------------------------------------------------------------- guards
    def test_guards(self):
        d = Path(self.td.name)
        cases = (("pot_differs.root", (), "dataPOTUsed is missing or differs"),
                 ("pot_missing.root", (), "dataPOTUsed is missing or differs"),
                 ("no_data_tree.root", (), "Missing required TTrees"),
                 ("alt_data.root", ("--closure",), "--data-file and --closure cannot be combined"))
        for name, extra, needle in cases:
            with self.subTest(name=name, extra=extra):
                _, r = self.run_driver(t.RE2, *PROD, *extra, "--data-file", str(d / name), check=False)
                self.assertNotEqual(r.returncode, 0)
                self.assertIn(needle, r.stdout + r.stderr)

    # the parent class's own tests are not re-run here
    test_purity_cv = test_purity_three_stream_and_bkg_only = test_purity_universe_selective = None
    test_refined_without_size_equals_driver_p1 = test_size_reaches_the_classifier_and_moves_the_result = None
    test_refined_unit_factors_equal_the_refined_cv = test_background_stream_changes_exactly_the_injected_rows = None
    test_three_stream_signed_sum = None


if __name__ == "__main__":
    unittest.main()
