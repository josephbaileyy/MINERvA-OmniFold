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


def write_trees(path: Path, trees: dict, params: dict | None = None) -> None:
    """A ROOT file holding each {tree: {column: array}} (uint8 as /b, int64 as /L, else /D) and TParameters
    ({name: (type, value)})."""
    import ROOT
    from array import array
    f = ROOT.TFile.Open(str(path), "RECREATE")
    for name, cols in trees.items():
        t = ROOT.TTree(name, name)
        bufs = {}
        for k, v in cols.items():
            code, leaf = (("B", "b") if v.dtype == np.uint8 else ("q", "L") if v.dtype == np.int64 else ("d", "D"))
            bufs[k] = array(code, [0])
            t.Branch(k, bufs[k], f"{k}/{leaf}")
        for i in range(next(iter(cols.values())).size):
            for k, v in cols.items():
                bufs[k][0] = v[i].item()
            t.Fill()
        t.Write()
    for name, (typ, val) in (params or {}).items():
        ROOT.TParameter(typ)(name, val).Write()
    f.Close()


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
        with self.assertRaisesRegex(RuntimeError, "needs mc_truth_denom"):
            self.new.g2r_miss_override(str(self.map), str(self.omni), self.t_sig, None, UNI, True)
        with self.assertRaisesRegex(RuntimeError, "missing from mc_truth_denom"):
            self.new.g2r_miss_override(str(self.map), str(self.omni), self.t_sig, self.t_den, ("Flux", 3), True)
        base = dict(np.load(self.map))
        for name, change, pat in (("rows of unequal length", {"truth_rows": base["truth_rows"][:-1]}, "one-dimensional"),
                                  ("another omnifile", {"omnifile": np.array("/elsewhere/fx.root")}, "built from"),
                                  ("another size", {"omnifile_size": np.array(1)}, "built from"),
                                  ("other entry counts", {"n_signal": np.array(5)}, "entry counts")):
            p = d / f"bad_{name.replace(' ', '_')}.npz"
            np.savez(p, **{**base, **change})
            with self.subTest(name), self.assertRaisesRegex(RuntimeError, pat):
                self.new.g2r_miss_override(str(p), str(self.omni), self.t_sig, self.t_den, UNI, True)


STUB_HELPER = """import inspect, json, os, sys
import numpy as np


def omnifold(*args, **kw):
    \"\"\"The test's stand-in for the OmniFold helper: it records main()'s provenance and the training weights it was
    handed, then exits 17, so main() runs through everything before training without LightGBM.\"\"\"
    for fr in inspect.stack():
        if fr.function == "main" and "provenance" in fr.frame.f_locals:
            print("STUB-PROVENANCE " + json.dumps(dict(fr.frame.f_locals["provenance"]).get("g2rMissMap")))
            break
    np.savez(os.environ["G2R_STUB_OUT"], MCgen_weights=np.asarray(kw["MCgen_weights"]),
             MCreco_weights=np.asarray(kw["MCreco_weights"]))
    print("STUB-OMNIFOLD-REACHED")
    sys.stdout.flush()
    raise SystemExit(17)
"""


def write_main_fixture(omni: Path, flux: Path):
    """An omnifile main() can run on (the four trees, POT and the flux file of test_re2_driver.write_fixture), with
    test_g2r's signal and truth trees: reco rows, then the appended misses, and MaRES:0 varied."""
    import test_g2r as tg
    S, T, blk, U = tg.synthetic(blocks=((300, 90), (200, 60)), seed=41)
    rng = np.random.default_rng(42)
    n = len(S["MC"])
    S["MC"] = np.minimum(S["MC"], 0.3 * S["MC_pz"])
    T["MC"] = np.minimum(T["MC"], 0.3 * T["MC_pz"])
    u = f"{UNI[0]}_{UNI[1]}"
    is_miss = S["sim"] == -9999.0
    sig = {"MC": S["MC"], "MC_pz": S["MC_pz"], "sim": np.where(is_miss, -9999.0, np.clip(S["MC"] * rng.normal(1, .06, n), .001, 4.4)),
           "sim_pz": np.where(is_miss, -9999.0, np.clip(S["MC_pz"] * rng.normal(1, .06, n), 1.51, 59.0)),
           "sim_pass": S["sim_pass"].astype(np.uint8), "w_truth": S["w_truth"], "w_reco": S["w_reco"],
           f"w_truth_{u}": U["varied"][0], f"w_reco_{u}": U["varied"][1]}
    den = {"MC": T["MC"], "MC_pz": T["MC_pz"], "w_truth": T["w_truth"], f"w_truth_{u}": U["varied"][2]}
    nb, nd = 800, 1500
    bw = rng.uniform(0.0, 2.0, nb)
    bkg = {"sim_background": rng.uniform(0.0, 2.2, nb), "sim_background_pz": rng.uniform(1.4, 18.0, nb),
           "sim_background_pass": (rng.uniform(size=nb) < 0.9).astype(np.uint8), "w_bkg": bw,
           f"w_bkg_{u}": bw * rng.uniform(0.8, 1.2, nb)}
    data = {"measured": rng.uniform(0.02, 2.0, nd), "measured_pz": rng.uniform(1.6, 18.0, nd),
            "measured_pass": np.ones(nd, np.uint8)}
    write_trees(omni, {"mc_signal_reco": sig, "mc_background": bkg, "data": data, "mc_truth_denom": den},
                {"dataPOTUsed": ("double", 1.0e20), "mcPOTUsed": ("double", 4.0e20), "hasTruthOnlyMisses": ("int", 1)})
    import ROOT
    g = ROOT.TFile.Open(str(flux), "RECREATE")
    edges = np.array([0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55, 0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50])
    h = ROOT.TH1D("pTmu_reweightedflux_integrated", "", 14, edges)
    for i in range(1, 15):
        h.SetBinContent(i, 1e-3 * i)
    h.Write()
    g.Close()
    return S, T, blk, U


@unittest.skipUnless(HAVE, "needs PyROOT")
class MainWithMissMap(unittest.TestCase):
    """main() itself, with and without --miss-map, on a fixture with misses, through to the OmniFold helper (a stub that
    records the provenance and the training weights, then exits 17): the auditor's B1 and the director's
    requirement that the provenance line be run by a test."""

    @classmethod
    def setUpClass(cls):
        import g2r
        cls.td = tempfile.TemporaryDirectory()
        d = Path(cls.td.name)
        cls.omni, cls.flux = d / "fx.root", d / "flux.root"
        cls.S, cls.T, cls.blk, cls.U = write_main_fixture(cls.omni, cls.flux)
        cls.miss, cls.truth, _ = g2r.build_map(cls.S, cls.T, cls.blk)
        cls.map = d / "g2r_map.npz"
        np.savez(cls.map, miss_rows=cls.miss, truth_rows=cls.truth, n_signal=np.array(len(cls.S["MC"])),
                 n_truth=np.array(len(cls.T["MC"])), omnifile=np.array(str(cls.omni.resolve())),
                 omnifile_size=np.array(cls.omni.stat().st_size))
        stub = d / "stub" / "omnifold"
        stub.mkdir(parents=True)
        (stub / "__init__.py").write_text("")
        (stub / "OmniFold_helper_functions.py").write_text(STUB_HELPER)
        cls.stub = d / "stub"
        cls.n = 0
        cls.ov = g2r.override(cls.miss, cls.truth, cls.U["varied"][2], len(cls.S["MC"]))

    @classmethod
    def tearDownClass(cls):
        cls.td.cleanup()

    def run_main(self, *extra):
        import os
        type(self).n += 1
        d = Path(self.td.name)
        w = d / f"weights_{self.n}.npz"
        argv = ["re2_driver.py", "--omnifile", str(self.omni), "--mcfile", str(self.flux), "--iters", "2",
                "--use-weights", "--estimator", "lgbm", "--seed", "42", "--bkg-mode", "purity",
                "--universe", f"{UNI[0]}:{UNI[1]}", "--out", str(d / f"out_{self.n}.root"), *extra]
        code = (f"import sys, runpy; sys.path.insert(0, {str(self.stub)!r}); import omnifold; sys.argv = {argv!r}; "
                f"runpy.run_path({str(RE2)!r}, run_name='__main__')")
        r = subprocess.run([sys.executable, "-B", "-c", code], cwd=str(d), capture_output=True, text=True,
                           env=dict(os.environ, G2R_STUB_OUT=str(w), OMP_NUM_THREADS="1"))
        return r, w

    def provenance(self, r):
        line = [ln for ln in r.stdout.splitlines() if ln.startswith("STUB-PROVENANCE ")]
        self.assertEqual(len(line), 1, r.stdout[-2000:] + r.stderr[-3000:])
        import json
        v = json.loads(line[0][len("STUB-PROVENANCE "):])
        return json.loads(v) if isinstance(v, str) else v        # the driver records the TNamed title, a JSON string

    def test_a_miss_map_run_reaches_training_with_its_provenance(self):
        import hashlib
        r, _ = self.run_main("--miss-map", str(self.map))
        self.assertEqual(r.returncode, 17, r.stdout[-2000:] + r.stderr[-3000:])
        self.assertIn("STUB-OMNIFOLD-REACHED", r.stdout)
        prov = self.provenance(r)
        self.assertEqual(prov["sha256"], hashlib.sha256(self.map.read_bytes()).hexdigest())
        self.assertEqual((prov["universe"], prov["branch"], prov["n_miss"], prov["n_finite"]),
                         ("MaRES:0", "w_truth_MaRES_0", int(self.miss.size), int(self.miss.size)))

    def test_without_the_flag_no_g2r_record_and_the_override_reaches_training(self):
        r0, w0 = self.run_main()
        r1, w1 = self.run_main("--miss-map", str(self.map))
        for r in (r0, r1):
            self.assertEqual(r.returncode, 17, r.stdout[-2000:] + r.stderr[-3000:])
        self.assertIsNone(self.provenance(r0))
        a, b = np.load(w0), np.load(w1)
        pot = 1.0e20 / 4.0e20
        for k in ("MCgen_weights", "MCreco_weights"):
            self.assertEqual(a[k].shape, b[k].shape)
            n = len(self.S["MC"])
            changed = np.flatnonzero(a[k][:n] != b[k][:n])
            want = self.miss[self.U["varied"][2][self.truth] != self.S["w_truth"][self.miss]]
            np.testing.assert_array_equal(changed, want, err_msg=k)
            np.testing.assert_array_equal(b[k][self.miss], self.ov[self.miss] * pot, err_msg=k)
            np.testing.assert_array_equal(a[k][n:], b[k][n:], err_msg=k)


P5_BUILDER = REPO / "docs/orchestration/state/2d-closeout/stageB/diagnostics/p5/build_miss_override.py"
P5_BUILDER_SHA = "7f346e1af1688b6a43be540ef2a8c6f8456d76a1ea965613abce17263739296b"


@unittest.skipUnless(HAVE, "needs PyROOT")
class P5Builder(unittest.TestCase):
    """The auditor's n2, made permanent: P5's COMMITTED builder (unmodified, with all its checks) on per-playlist ROOT
    fixtures and their merge, including a block with no misses and one that is all misses, against the map's
    override, bitwise, for two universe columns (one varied, one named for the last universe)."""

    def test_p5s_committed_builder_equals_the_map(self):
        import hashlib
        import json
        import g2r
        import test_g2r as tg
        self.assertEqual(hashlib.sha256(P5_BUILDER.read_bytes()).hexdigest(), P5_BUILDER_SHA)
        blocks = ((60, 18), (50, 15), (25, 0), (33, 33))
        S, T, blk, U = tg.synthetic(blocks=blocks, seed=21)
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            paths, o = [], 0
            cols_s = lambda sl: {"MC": S["MC"][sl], "MC_pz": S["MC_pz"][sl], "w_truth": S["w_truth"][sl],
                                 "w_reco": S["w_reco"][sl], "sim": S["sim"][sl],
                                 "sim_pass": S["sim_pass"][sl].astype(np.uint8),
                                 f"w_truth_{UNI[0]}_{UNI[1]}": U["varied"][0][sl],
                                 f"w_truth_{LAST[0]}_{LAST[1]}": U["last"][0][sl]}
            cols_t = lambda sl: {"MC": T["MC"][sl], "MC_pz": T["MC_pz"][sl], "w_truth": T["w_truth"][sl],
                                 f"w_truth_{UNI[0]}_{UNI[1]}": U["varied"][2][sl],
                                 f"w_truth_{LAST[0]}_{LAST[1]}": U["last"][2][sl]}
            for k, (name, n, m) in enumerate(blk):
                p = d / f"{k}_{name}.root"
                write_trees(p, {"mc_signal_reco": cols_s(slice(o, o + n)), "mc_truth_denom": cols_t(slice(o, o + n))},
                            {"nTruthOnlyMisses": ("int", m)})
                paths.append(p)
                o += n
            merged = d / "merged.root"
            write_trees(merged, {"mc_signal_reco": cols_s(slice(None)), "mc_truth_denom": cols_t(slice(None))},
                        {"nTruthOnlyMisses": ("int", sum(m for _, _, m in blk))})
            miss, truth, _ = g2r.build_map(S, T, blk)
            for uni, col in ((UNI, U["varied"][2]), (LAST, U["last"][2])):
                with self.subTest(uni):
                    out, rep = d / f"ov_{uni[0]}.npz", d / f"ov_{uni[0]}.json"
                    r = subprocess.run([sys.executable, "-B", str(P5_BUILDER), "--omnifile", str(merged), "--blocks",
                                        *map(str, paths), "--universe", f"{uni[0]}:{uni[1]}", "--out", str(out),
                                        "--report", str(rep)], capture_output=True, text=True, cwd=td)
                    self.assertEqual(r.returncode, 0, r.stdout[-2000:] + r.stderr[-2000:])
                    self.assertTrue(json.loads(rep.read_text())["ALL_PASS"])
                    want = np.load(out)["w_override"]
                    got = g2r.override(miss, truth, col, len(S["MC"]))
                    np.testing.assert_array_equal(np.isnan(got), np.isnan(want))
                    np.testing.assert_array_equal(got[~np.isnan(got)], want[~np.isnan(want)])


if __name__ == "__main__":
    unittest.main(verbosity=1)
