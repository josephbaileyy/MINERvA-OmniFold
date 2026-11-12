"""COV2D-G2R's ``--miss-map`` in ``2d-unfolding/re2/re2_driver.py``, at the loader (PyROOT and numpy; no LightGBM).

    python3 -B 2d-unfolding/re2/tests/test_re2_miss_map.py

On a synthetic omnifile in the event loop's layout (reco rows, then the appended truth-only misses with sim = -9999 and
every universe weight the CV w_truth), in universe mode, with every row inside the phase space so the loader keeps all:

* C1, no-op: with no override, the patched loader's arrays equal the pre-patch driver's (its blob at PRE_PATCH_BLOB)
  bitwise, under --branch-select all and derived;
* C2, identity plumbing: an override equal to the stored proxy gives arrays bitwise equal to no override;
* C3, effect only on miss rows: the real override changes w_truth and w_reco exactly on the miss rows whose universe
  weight differs, to that weight times the POT scale, and every kinematic and pass array is bitwise equal;
* the loader's guards: a finite override on a passing row, a length mismatch;
* g2r_miss_override builds g2r.override's array from the map and the truth tree's column, carries no state from one
  universe to the next (MaRES:0, the last universe, MaRES:0 again in one process), and refuses a map from another
  omnifile (realpath or size), other entry counts, or a run without --universe or --use-weights.

The end-to-end controls (the whole driver against the pre-patch blob, every histogram bit for bit, as
test_re2_data_file.py does) need LightGBM and run in the cluster-environment test.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
RE2 = REPO / "2d-unfolding" / "re2" / "re2_driver.py"
G2R = REPO / "2d-unfolding" / "cov2d" / "g2r"
sys.path[:0] = [str(G2R), str(G2R / "tests"), str(REPO / "2d-unfolding" / "cov2d")]
PRE_PATCH_REF = "05a74e7cece590efdafeb537a2ce9e882f22d32e"     # origin/main when the patch was made
UNI = ("MaRES", 0)
LAST = ("VecFFCCQEshape", 1)          # the last of the 175 in cov2d's draw order
POT = 0.25
EDGES = (0.0, 4.5, 1.5, 60.0)

try:
    import ROOT  # noqa: F401
    HAVE = True
except Exception:  # pragma: no cover
    HAVE = False


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def write_omnifile(path: Path):
    import ROOT
    from array import array
    import test_g2r as tg
    S, T, blk, U = tg.synthetic(blocks=((60, 18), (50, 15)), seed=21)
    rng = np.random.default_rng(22)
    n = len(S["MC"])
    S["MC"] = np.minimum(S["MC"], 0.3 * S["MC_pz"])          # inside the truth phase space
    T["MC"] = np.minimum(T["MC"], 0.3 * T["MC_pz"])
    sig = {"MC": S["MC"], "MC_pz": S["MC_pz"], "sim": S["sim"], "sim_pz": np.where(S["sim"] == -9999.0, -9999.0,
                                                                                   rng.uniform(2, 20, n)),
           "sim_pass": S["sim_pass"].astype(np.uint8), "w_truth": S["w_truth"], "w_reco": S["w_reco"],
           f"w_truth_{UNI[0]}_{UNI[1]}": U["varied"][0], f"w_reco_{UNI[0]}_{UNI[1]}": U["varied"][1],
           f"w_truth_{LAST[0]}_{LAST[1]}": U["last"][0], f"w_reco_{LAST[0]}_{LAST[1]}": U["last"][1]}
    den = {"MC": T["MC"], "MC_pz": T["MC_pz"], "w_truth": T["w_truth"], f"w_truth_{UNI[0]}_{UNI[1]}": U["varied"][2],
           f"w_truth_{LAST[0]}_{LAST[1]}": U["last"][2]}
    f = ROOT.TFile.Open(str(path), "RECREATE")
    for name, cols in (("mc_signal_reco", sig), ("mc_truth_denom", den)):
        t = ROOT.TTree(name, name)
        bufs = {}
        for k, v in cols.items():
            code, leaf = ("B", "b") if v.dtype == np.uint8 else ("d", "D")
            bufs[k] = array(code, [0])
            t.Branch(k, bufs[k], f"{k}/{leaf}")
        for i in range(next(iter(cols.values())).size):
            for k, v in cols.items():
                bufs[k][0] = v[i].item()
            t.Fill()
        t.Write()
    f.Close()
    # the S dict as the map needs it (the file's own values)
    S2 = dict(S, MC=S["MC"])
    return S2, T, blk, U


@unittest.skipUnless(HAVE, "needs PyROOT")
class MissMapLoader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import ROOT
        import g2r
        cls.g2r = g2r
        cls.td = tempfile.TemporaryDirectory()
        d = Path(cls.td.name)
        cls.omni = d / "fx.root"
        cls.S, cls.T, cls.blk, cls.U = write_omnifile(cls.omni)
        cls.miss, cls.truth, _ = g2r.build_map(cls.S, cls.T, cls.blk)
        cls.map = d / "g2r_map.npz"
        np.savez(cls.map, miss_rows=cls.miss, truth_rows=cls.truth, n_signal=np.array(len(cls.S["MC"])),
                 n_truth=np.array(len(cls.T["MC"])), omnifile=np.array(str(cls.omni.resolve())),
                 omnifile_size=np.array(cls.omni.stat().st_size))
        pre = d / "re2_driver_pre.py"
        pre.write_bytes(subprocess.run(["git", "-C", str(REPO), "show", f"{PRE_PATCH_REF}:2d-unfolding/re2/re2_driver.py"],
                                       check=True, capture_output=True).stdout)
        cls.new = load(RE2, "re2_driver_g2r")
        cls.pre = load(pre, "re2_driver_pre")
        cls.f = ROOT.TFile.Open(str(cls.omni))
        cls.t_sig, cls.t_den = cls.f.Get("mc_signal_reco"), cls.f.Get("mc_truth_denom")

    @classmethod
    def tearDownClass(cls):
        cls.f.Close()
        cls.td.cleanup()

    def load_sig(self, mod, select="all", **kw):
        return mod.call_loader(mod.collect_signal_arrays_2d, self.t_sig, *EDGES, POT, use_weights=True,
                               universe_branch=UNI, branch_select=select, **kw)

    def assert_arrays_equal(self, a, b, keys=None):
        self.assertEqual(sorted(a), sorted(b))
        for k in keys or a:
            np.testing.assert_array_equal(a[k], b[k], err_msg=k)

    def test_c1_no_override_equals_the_pre_patch_loader(self):
        for select in ("all", "derived"):
            with self.subTest(select):
                self.assert_arrays_equal(self.load_sig(self.new, select), self.load_sig(self.pre, select))

    def test_every_row_is_kept(self):
        self.assertEqual(self.load_sig(self.new)["w_truth"].size, len(self.S["MC"]))

    def test_c2_an_override_equal_to_the_proxy_changes_nothing(self):
        ov = np.full(len(self.S["MC"]), np.nan)
        ov[self.miss] = self.S["w_truth"][self.miss]
        for select in ("all", "derived"):
            with self.subTest(select):
                self.assert_arrays_equal(self.load_sig(self.new, select, miss_weight_override=ov),
                                         self.load_sig(self.new, select))

    def test_c3_the_override_changes_only_the_miss_rows(self):
        ov = self.g2r.override(self.miss, self.truth, self.U["varied"][2], len(self.S["MC"]))
        a = self.load_sig(self.new, "derived", miss_weight_override=ov)
        b = self.load_sig(self.new, "derived")
        for k in ("truth_pt", "truth_pz", "reco_pt", "reco_pz", "pass_reco", "pass_truth"):
            np.testing.assert_array_equal(a[k], b[k], err_msg=k)
        for k in ("w_truth", "w_reco"):
            changed = np.flatnonzero(a[k] != b[k])
            want = self.miss[self.U["varied"][2][self.truth] != self.S["w_truth"][self.miss]]
            np.testing.assert_array_equal(changed, want, err_msg=k)
            np.testing.assert_array_equal(a[k][self.miss], ov[self.miss] * POT, err_msg=k)

    def test_loader_guards(self):
        ov = np.full(len(self.S["MC"]), np.nan)
        passing = int(np.flatnonzero(self.S["sim_pass"] == 1)[0])
        ov[passing] = 1.0
        with self.assertRaisesRegex(RuntimeError, "sim_pass=1"):
            self.load_sig(self.new, miss_weight_override=ov)
        with self.assertRaisesRegex(RuntimeError, "entries"):
            self.load_sig(self.new, miss_weight_override=np.full(3, np.nan))

    def test_the_override_from_the_map(self):
        ov, prov = self.new.g2r_miss_override(str(self.map), str(self.omni), self.t_sig, self.t_den, UNI, True)
        want = self.g2r.override(self.miss, self.truth, self.U["varied"][2], len(self.S["MC"]))
        np.testing.assert_array_equal(np.isnan(ov), np.isnan(want))
        np.testing.assert_array_equal(ov[self.miss], want[self.miss])
        self.assertEqual((prov["universe"], prov["n_miss"], prov["n_finite"]), ("MaRES:0", self.miss.size,
                                                                                self.miss.size))

    def test_no_state_is_carried_between_universes(self):
        """The director's condition on amendment 1 §2: in one process, the override for MaRES:0, then the last universe,
        then MaRES:0 again, each equals its own g2r.override, and the two universes' differ."""
        N = len(self.S["MC"])
        want = {UNI: self.g2r.override(self.miss, self.truth, self.U["varied"][2], N),
                LAST: self.g2r.override(self.miss, self.truth, self.U["last"][2], N)}
        got = []
        for u in (UNI, LAST, UNI):
            ov, prov = self.new.g2r_miss_override(str(self.map), str(self.omni), self.t_sig, self.t_den, u, True)
            got.append(ov)
            self.assertEqual(prov["universe"], f"{u[0]}:{u[1]}")
            np.testing.assert_array_equal(ov[self.miss], want[u][self.miss], err_msg=str(u))
            self.assertTrue(np.all(np.isnan(np.delete(ov, self.miss))))
        self.assertFalse(np.array_equal(got[0][self.miss], got[1][self.miss]))
        np.testing.assert_array_equal(got[0], got[2])

    def test_map_guards(self):
        d = Path(self.td.name)
        cases = {"needs --universe": dict(universe_branch=None), "needs --use-weights": dict(use_weights=False)}
        for name, kw in cases.items():
            args = dict(map_path=str(self.map), omnifile=str(self.omni), t_sig=self.t_sig,
                        t_truth_denom=self.t_den, universe_branch=UNI, use_weights=True)
            args.update(kw)
            with self.subTest(name), self.assertRaisesRegex(RuntimeError, "needs --universe and --use-weights"):
                self.new.g2r_miss_override(**args)
        base = dict(np.load(self.map))
        for name, change, pat in (("another omnifile", {"omnifile": np.array("/elsewhere/fx.root")}, "built from"),
                                  ("another size", {"omnifile_size": np.array(1)}, "built from"),
                                  ("other entry counts", {"n_signal": np.array(5)}, "entry counts")):
            p = d / f"bad_{name.replace(' ', '_')}.npz"
            np.savez(p, **{**base, **change})
            with self.subTest(name), self.assertRaisesRegex(RuntimeError, pat):
                self.new.g2r_miss_override(str(p), str(self.omni), self.t_sig, self.t_den, UNI, True)


if __name__ == "__main__":
    unittest.main(verbosity=1)
