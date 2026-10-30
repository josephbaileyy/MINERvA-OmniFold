"""Controls for 5B (FD-CT-5B-DECLARATION.md section 3): fd_ct_period_inputs.py, fd_ct_periods.py, the committed tables
and the submit stages, on synthetic trees and the committed H2 definition. The only real products read are MP-1's 25
committed jittered data unfolds, from which the K3 tolerance is fixed.

* Each refusing control refuses on a one-entry defect, by its message, with nothing written.
* Each deciding control decides in both directions: a planted value just inside the tolerance passes and one just
  outside fails.
* The readout is recomputed here by an independent route (explicit loops on the planted cell integrals).
* Nothing written carries f or an absolute cell value; an integral planted within LEAK_REL of f is not falsely
  refused (amendment 1's mode), and a planted leak is."""
import contextlib
import copy
import hashlib
import importlib.util
import io
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
sys.path.insert(1, str(ND / "tests"))
import fd_ct_period_inputs as pi  # noqa: E402
import fd_ct_periods as cp  # noqa: E402
import fd_ct_readers as ct  # noqa: E402
import fd_f0_regrade as F  # noqa: E402
import s1_assemble as sa  # noqa: E402
import test_fd_ct_readers as TR  # noqa: E402

REPO = ND.parent
DEFINITION = ND / "pv-ladder/readouts/h2_definition.json"
REL5 = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-ct/5b"
TWO_D = REPO / "docs/orchestration/state/2d-closeout/period-unfold-20261014"
digest = TR.digest
TAU = cp.TAU_K * np.asarray(cp.SIGMA_JITTER)


def quiet(fn, *a, **k):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            rc = fn(*a, **k)
        except SystemExit as e:
            rc = e.code
    return rc, out.getvalue(), err.getvalue() + out.getvalue()


# ================================================================ fd_ct_period_inputs


def nn_npz(path: Path, seed=0, n=50, **over):
    rng = np.random.default_rng(seed)
    arr = {"axes": np.array(["eavail", "q3", "W"], dtype=object),
           "MCgen": rng.normal(size=(n, 5)).astype(np.float32), "MCreco": rng.normal(size=(n, 5)).astype(np.float32),
           "measured": rng.normal(size=(20, 5)).astype(np.float32), "pass_reco": rng.random(n) > 0.2,
           "pass_truth": rng.random(n) > 0.1, "w_truth": rng.random(n), "w_reco": rng.random(n),
           "measured_weights": rng.random(20), "denom_nd": rng.random((2, 2, 2, 2, 2)),
           "flux": np.full(14, 3.5), "data_pot": 1.06e21, "n_nucleons": 3.2e30,
           **{f"edges_{i}": np.linspace(0, 1, 3) for i in range(5)}, "nedges": 5}
    arr.update(over)
    np.savez_compressed(path, **arr)
    return path


def bkg_npz(path: Path, lat: Path, merged: Path, seed=0, **over):
    rng = np.random.default_rng(seed + 7)
    arr = {"bkg_reco": rng.normal(size=(9, 5)), "bkg_w": rng.random(9), "bkg_nd": rng.random((2, 2, 2, 2, 2)),
           "meta": json.dumps({"npz_sha256": digest(lat), "omnifile": str(merged)})}
    arr.update(over)
    np.savez_compressed(path, **arr)
    return path


class InputsBase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="ct5b-in-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def run_pi(self, argv, extra=()):
        with contextlib.ExitStack() as st:
            for p in extra:
                st.enter_context(p)
            return quiet(pi.main, argv)


class Definitions(unittest.TestCase):
    """The periods, playlist order and flux pins against independent committed sources."""

    def test_periods_are_the_2d_period_unfolds(self):
        spec = importlib.util.spec_from_file_location("periods2d", TWO_D / "scripts/periods.py")
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        self.assertEqual({k: list(v) for k, v in pi.PERIODS.items()}, m.PERIODS)

    def test_all_is_mp1s_merge_order(self):
        text = (REPO / "measurement-paper/phase1/mp1/mp1_s1_pipeline.sh").read_text()
        pls = [ln for ln in text.splitlines() if ln.startswith("PLS=")][0].split('"')[1].split()
        self.assertEqual(list(pi.PERIODS["ALL"]), pls)

    def test_flux_pins_are_the_2d_records(self):
        rec = {ln.split()[1]: ln.split()[0] for ln in (TWO_D / "outputs/SHA256SUMS.inputs").read_text().splitlines()}
        self.assertEqual({P: rec[f"flux/runEventLoopMC_{P}.root"] for P in pi.FLUX}, pi.FLUX)

    def test_the_committed_flux_copies_are_at_their_pins(self):
        self.assertEqual({P: digest(pi.DEPLOY / pi.FLUX_REL / f"runEventLoopMC_{P}.root") for P in pi.FLUX}, pi.FLUX)

    def test_mp1_zero_pins_are_build_cresps(self):
        import build_cresp as bc
        self.assertEqual((pi.MP1_ZERO["unfold"], pi.MP1_ZERO["lat_npz"], pi.MP1_ZERO["lat_bkg"]), bc.PRODUCTS["zero"])
        self.assertEqual(digest(REPO / "docs/orchestration/state/measurement-paper/phase1/mp1/jitter-receipts/"
                                       "mp1s1_zero_b-_j-.npz"), pi.MP1_ZERO["unfold"])


try:
    import ROOT  # noqa: F401
    HAVE_ROOT = True
except ImportError:
    HAVE_ROOT = False


@unittest.skipUnless(HAVE_ROOT, "ROOT is not importable here; this runs in the cluster deploy tests")
class RootReaders(unittest.TestCase):
    def test_flux_data_pot_reads_the_2d_records_value(self):
        p = pi.DEPLOY / pi.FLUX_REL / "runEventLoopMC_ALL.root"
        self.assertEqual(pi.flux_data_pot(p), 1.057394261158926e+21)   # inputs_verify.json, ALL

    def test_merged_data_pot_reads_dataPOTUsed(self):
        import ROOT
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "m.root"
            f = ROOT.TFile.Open(str(p), "RECREATE")
            ROOT.TParameter("double")("dataPOTUsed", 1.25e20).Write()
            ROOT.TParameter("double")("mcPOTUsed", 5.0e20).Write()
            f.Close()
            self.assertEqual(pi.merged_data_pot(p), 1.25e20)


class StageFlux(InputsBase):
    def make_src(self):
        src = self.tmp / "src"
        src.mkdir()
        pins = {}
        for P in pi.FLUX:
            (src / f"runEventLoopMC_{P}.root").write_bytes(f"flux {P}".encode())
            pins[P] = digest(src / f"runEventLoopMC_{P}.root")
        return src, pins

    def test_copies_each_file_at_its_pin(self):
        src, pins = self.make_src()
        rc, _, err = self.run_pi(["stage-flux", "--src-dir", str(src), "--out-dir", str(self.tmp / "flux")],
                                 [mock.patch.dict(pi.FLUX, pins)])
        self.assertEqual(rc, 0, err)
        self.assertEqual({P: digest(self.tmp / "flux" / f"runEventLoopMC_{P}.root") for P in pins}, pins)

    def test_refuses_a_source_at_another_digest_before_creating_anything(self):
        src, pins = self.make_src()
        pins["PB"] = "0" * 64
        rc, _, err = self.run_pi(["stage-flux", "--src-dir", str(src), "--out-dir", str(self.tmp / "flux")],
                                 [mock.patch.dict(pi.FLUX, pins)])
        self.assertEqual(rc, 4)
        self.assertIn("PB flux source", err)
        self.assertFalse((self.tmp / "flux").exists())

    def test_refuses_a_copy_that_is_not_its_source(self):
        src, pins = self.make_src()
        bad = lambda a, b: Path(b).write_bytes(b"torn copy")  # noqa: E731
        rc, _, err = self.run_pi(["stage-flux", "--src-dir", str(src), "--out-dir", str(self.tmp / "flux")],
                                 [mock.patch.dict(pi.FLUX, pins), mock.patch.object(pi.shutil, "copyfile", bad)])
        self.assertEqual(rc, 4)
        self.assertIn("flux copy", err)

    def test_refuses_an_existing_directory(self):
        src, pins = self.make_src()
        (self.tmp / "flux").mkdir()
        rc, _, err = self.run_pi(["stage-flux", "--src-dir", str(src), "--out-dir", str(self.tmp / "flux")],
                                 [mock.patch.dict(pi.FLUX, pins)])
        self.assertEqual(rc, 3)


class Merge(InputsBase):
    def loops(self, period):
        d = self.tmp / "loops"
        d.mkdir(exist_ok=True)
        pins = {}
        for pl in pi.PLAYLISTS:
            p = d / f"runEventLoopOmniFold_5D_{pl}_zero.root"
            p.write_bytes(f"loop {pl}".encode())
            pins[pl] = digest(p)
        return d, pins

    def merge_argv(self, period, d, out, pot=(1.0e21, 1.0e21)):
        flux = self.tmp / f"flux_{period}.root"
        flux.write_bytes(f"flux {period}".encode())
        self.pot_patches = [mock.patch.dict(pi.FLUX, {period: digest(flux)}),
                            mock.patch.object(pi, "merged_data_pot", lambda p: pot[0]),
                            mock.patch.object(pi, "flux_data_pot", lambda p: pot[1])]
        return ["merge", "--period", period, "--loops-dir", str(d), "--flux", str(flux), "--out", str(out)]

    def fake_hadd(self, rc=0):
        calls = []

        def run(cmd, *a, **k):
            calls.append(cmd)
            if rc == 0:
                Path(cmd[2]).write_bytes(b"".join(Path(c).read_bytes() for c in cmd[3:]))
            return subprocess.CompletedProcess(cmd, rc)
        return calls, mock.patch.object(pi.subprocess, "run", run)

    def test_merges_the_period_in_production_order_with_mp1s_tool(self):
        d, pins = self.loops("PB")
        calls, patch = self.fake_hadd()
        out = self.tmp / "m" / "PB.root"
        argv = self.merge_argv("PB", d, out)
        rc, _, err = self.run_pi(argv, [mock.patch.dict(pi.ZERO_LOOPS, pins), patch, *self.pot_patches])
        self.assertEqual(rc, 0, err)
        self.assertEqual(Path(calls[0][1]).relative_to(pi.DEPLOY), Path("2d-unfolding/uq/hadd_universes_full.py"))
        self.assertEqual([Path(c).name for c in calls[0][3:]],
                         [f"runEventLoopOmniFold_5D_{pl}_zero.root" for pl in ("1G", "1L", "1M")])
        rec = json.loads(out.with_name("PB.root.json").read_text())
        self.assertEqual((rec["period"], rec["out_sha256"], [i["playlist"] for i in rec["inputs"]]),
                         ("PB", digest(out), ["1G", "1L", "1M"]))
        self.assertFalse(out.with_name("PB.root.partial").exists())

    def test_refuses_a_loop_at_another_digest_before_merging(self):
        d, pins = self.loops("PA")
        pins["1C"] = "1" * 64
        calls, patch = self.fake_hadd()
        out = self.tmp / "m" / "PA.root"
        argv = self.merge_argv("PA", d, out)
        rc, _, err = self.run_pi(argv, [mock.patch.dict(pi.ZERO_LOOPS, pins), patch, *self.pot_patches])
        self.assertEqual(rc, 4)
        self.assertIn("zero loop 1C", err)
        self.assertEqual(calls, [])
        self.assertFalse(out.exists())

    def test_refuses_to_overwrite(self):
        d, pins = self.loops("PC")
        out = self.tmp / "PC.root"
        out.write_bytes(b"x")
        calls, patch = self.fake_hadd()
        argv = self.merge_argv("PC", d, out)
        rc, _, _ = self.run_pi(argv, [mock.patch.dict(pi.ZERO_LOOPS, pins), patch, *self.pot_patches])
        self.assertEqual((rc, calls), (3, []))

    def test_a_failed_merge_leaves_nothing(self):
        d, pins = self.loops("PC")
        calls, patch = self.fake_hadd(rc=1)
        out = self.tmp / "PC.root"
        argv = self.merge_argv("PC", d, out)
        rc, _, err = self.run_pi(argv, [mock.patch.dict(pi.ZERO_LOOPS, pins), patch, *self.pot_patches])
        self.assertEqual(rc, 6)
        self.assertFalse(any(self.tmp.glob("PC.root*")))

    def test_refuses_a_merge_whose_pot_the_flux_was_not_weighted_with_before_any_dump(self):
        d, pins = self.loops("PB")
        calls, patch = self.fake_hadd()
        out = self.tmp / "PB.root"
        for pot, rc_want in (((1.0e21, 1.0e21 * (1 + 2e-12)), 5), ((1.0e21, 1.0e21 * (1 + 5e-13)), 0)):
            for p in self.tmp.glob("PB.root*"):
                p.unlink()
            argv = self.merge_argv("PB", d, out, pot)
            rc, _, err = self.run_pi(argv, [mock.patch.dict(pi.ZERO_LOOPS, pins), patch, *self.pot_patches])
            self.assertEqual(rc, rc_want, err)
            self.assertEqual(out.exists(), rc_want == 0)
            self.assertFalse(out.with_name("PB.root.partial").exists())


class Check(InputsBase):
    def build(self, period="PB", lat_over=None, bkg_over=None, mp1_over=None, mp1_bkg_over=None):
        T = self.tmp
        self.merged = T / f"merged_{period}.root"
        self.merged.write_bytes(b"merged")
        self.merged.with_name(self.merged.name + ".json").write_text(json.dumps(
            {"period": period, "out": str(self.merged), "out_sha256": digest(self.merged)}))
        self.flux = T / f"flux_{period}.root"
        self.flux.write_bytes(f"flux {period}".encode())
        self.nn = nn_npz(T / "nn.npz")
        self.lat = nn_npz(T / "lat.npz", **(lat_over or {}))
        self.bkg = bkg_npz(T / "lat_bkg.npz", self.lat, self.merged, **(bkg_over or {}))
        self.argv = ["check", "--period", period, "--merged", str(self.merged), "--nn-npz", str(self.nn), "--lat-npz",
                     str(self.lat), "--lat-bkg", str(self.bkg), "--flux", str(self.flux), "--truth-out",
                     str(T / "truth.npz"), "--out", str(T / "check.json")]
        self.mp1 = {}
        if period == "ALL":
            self.mp1_lat = nn_npz(T / "mp1_lat.npz", **(mp1_over or {}))
            self.mp1_bkg = bkg_npz(T / "mp1_bkg.npz", self.mp1_lat, self.merged, **(mp1_bkg_over or {}))
            self.argv += ["--mp1-lat-npz", str(self.mp1_lat), "--mp1-lat-bkg", str(self.mp1_bkg)]
            self.mp1 = {"lat_npz": digest(self.mp1_lat), "lat_bkg": digest(self.mp1_bkg)}
        self.pots = [1.06e21, 1.06e21]
        return self

    def patches(self, period="PB"):
        def run(cmd, *a, **k):
            self.truth_cmd = cmd
            Path(cmd[cmd.index("--out") + 1]).write_bytes(b"truth")
            return subprocess.CompletedProcess(cmd, 0)
        return [mock.patch.dict(pi.FLUX, {period: digest(self.flux)}), mock.patch.dict(pi.MP1_ZERO, self.mp1),
                mock.patch.object(pi, "merged_data_pot", lambda p: self.pots[0]),
                mock.patch.object(pi, "flux_data_pot", lambda p: self.pots[1]),
                mock.patch.object(pi.subprocess, "run", run)]

    def assertRefuses(self, msg, rc=5, period="PB"):
        r, _, err = self.run_pi(self.argv, self.patches(period))
        self.assertEqual(r, rc, err)
        self.assertIn(msg, err)
        self.assertFalse((self.tmp / "check.json").exists())

    def test_a_consistent_period_passes_and_writes_its_truth(self):
        self.build()
        rc, _, err = self.run_pi(self.argv, self.patches())
        self.assertEqual(rc, 0, err)
        rec = json.loads((self.tmp / "check.json").read_text())
        self.assertTrue(all(rec["nn_npz_equals_lat_npz"].values()))
        self.assertEqual(rec["files"]["lat_npz"][1], digest(self.lat))
        self.assertEqual(rec["files"]["truth"][1], digest(self.tmp / "truth.npz"))
        self.assertEqual(Path(self.truth_cmd[1]).name, "s5p_mc_truth_pred.py")
        self.assertEqual(self.truth_cmd[self.truth_cmd.index("--expect-npz-sha256") + 1], digest(self.lat))
        self.assertTrue(rec["flux_constant_over_pt"])
        self.assertNotIn("all_vs_mp1_zero", rec)

    def test_the_real_alls_last_digit_flux_spread_is_constant_and_a_larger_one_is_not(self):
        bins = np.array([0.0006243343376851218] * 12 + [0.0006243343376851219] * 2)   # inputs_verify.json, ALL
        for flux, want in ((bins, True), (bins * np.r_[np.ones(13), 1 + 1e-12], False)):
            self.build(lat_over={"flux": flux})
            self.nn = nn_npz(self.tmp / "nn.npz", flux=flux)
            self.argv[self.argv.index("--nn-npz") + 1] = str(self.nn)
            for p in (self.tmp / "check.json", self.tmp / "truth.npz"):
                p.unlink(missing_ok=True)
            rc, _, err = self.run_pi(self.argv, self.patches())
            self.assertEqual(rc, 0, err)
            self.assertEqual(json.loads((self.tmp / "check.json").read_text())["flux_constant_over_pt"], want)

    def test_creates_its_own_output_folders(self):
        self.build()
        i, j = self.argv.index("--out") + 1, self.argv.index("--truth-out") + 1
        self.argv[i], self.argv[j] = str(self.tmp / "inputs/check.json"), str(self.tmp / "truth/truth.npz")
        rc, _, err = self.run_pi(self.argv, self.patches())
        self.assertEqual(rc, 0, err)
        self.assertTrue((self.tmp / "inputs/check.json").is_file() and (self.tmp / "truth/truth.npz").is_file())

    def test_each_npz_key_is_compared(self):
        base = dict(np.load(nn_npz(self.tmp / "ref.npz"), allow_pickle=True))
        for k in pi.NPZ_KEYS:
            with self.subTest(k=k):
                v = np.array(base[k], copy=True)
                if v.dtype == object:
                    v = np.array(["eavail", "q3", "Q"], dtype=object)
                elif v.ndim == 0:
                    v = v * 2 if v.dtype.kind == "f" else v + 1
                elif v.dtype == bool:
                    v.flat[0] = not v.flat[0]
                else:
                    v.flat[0] = v.flat[0] + 1
                self.build(lat_over={k: v})
                self.assertRefuses(f"'{k}'")

    def test_a_dtype_change_alone_is_refused(self):
        # the same values in another dtype: the pass flags as 0/1 integers, and float32-exact weights as float32
        ref = dict(np.load(nn_npz(self.tmp / "ref.npz"), allow_pickle=True))
        exact = ref["w_truth"].astype(np.float32).astype(np.float64)
        for k, nn_v, lat_v in (("pass_reco", ref["pass_reco"], ref["pass_reco"].astype(np.int8)),
                               ("w_truth", exact, exact.astype(np.float32))):
            with self.subTest(k=k):
                self.assertTrue(np.array_equal(nn_v, lat_v))
                self.build(lat_over={k: lat_v})
                self.nn = nn_npz(self.tmp / "nn.npz", **{k: nn_v})
                self.argv[self.argv.index("--nn-npz") + 1] = str(self.nn)
                self.assertRefuses(f"'{k}'")

    def test_refuses_a_background_dump_of_another_npz(self):
        self.build(bkg_over={"meta": json.dumps({"npz_sha256": "0" * 64, "omnifile": "x"})})
        self.assertRefuses("background dump does not name")

    def test_refuses_a_data_pot_the_flux_was_not_weighted_with(self):
        self.build()
        self.pots = [1.06e21, 1.06e21 * (1 + 1e-11)]
        self.assertRefuses("data POT")

    def test_refuses_a_merge_its_receipt_does_not_name(self):
        self.build()
        self.merged.write_bytes(b"another merge")
        self.assertRefuses("receipt names")

    def test_refuses_another_flux_file(self):
        self.build()
        ps = self.patches()
        ps[0] = mock.patch.dict(pi.FLUX, {"PB": "2" * 64})
        r, _, err = self.run_pi(self.argv, ps)
        self.assertEqual(r, 4)
        self.assertIn("PB flux file", err)

    def test_all_requires_mp1s_dumps_and_only_all_takes_them(self):
        self.build("ALL")
        argv = self.argv[:self.argv.index("--mp1-lat-npz")]
        r, _, err = self.run_pi(argv, self.patches("ALL"))
        self.assertEqual(r, 2)
        self.build("PB")
        r, _, err = self.run_pi(self.argv + ["--mp1-lat-npz", str(self.lat), "--mp1-lat-bkg", str(self.bkg)],
                                self.patches())
        self.assertEqual(r, 2)

    def test_all_records_each_key_against_mp1_and_does_not_decide(self):
        ref = dict(np.load(nn_npz(self.tmp / "ref.npz"), allow_pickle=True))
        mc = ref["MCreco"].copy()
        mc[0, 0] += 1
        self.build("ALL", mp1_over={"MCreco": mc}, mp1_bkg_over={"bkg_reco": np.zeros((9, 5), np.float32)})
        rc, _, err = self.run_pi(self.argv, self.patches("ALL"))
        self.assertEqual(rc, 0, err)
        c = json.loads((self.tmp / "check.json").read_text())["all_vs_mp1_zero"]
        self.assertEqual(sorted(k for k, v in c["lat_npz"].items() if not v), ["MCreco"])
        self.assertEqual(sorted(k for k, v in c["lat_bkg"].items() if not v), ["bkg_reco"])
        self.assertEqual(set(c["lat_npz"]), set(pi.NPZ_KEYS) | {"_key_sets_equal"})

    def test_all_refuses_mp1_dumps_at_another_digest(self):
        self.build("ALL")
        ps = self.patches("ALL")
        ps[1] = mock.patch.dict(pi.MP1_ZERO, {"lat_npz": "3" * 64, "lat_bkg": self.mp1["lat_bkg"]})
        r, _, err = self.run_pi(self.argv, ps)
        self.assertEqual(r, 4)
        self.assertIn("MP-1 lat_zero.npz", err)


class Unfold(InputsBase):
    def build(self, period="PA"):
        self.lat, self.bkg = self.tmp / "lat.npz", self.tmp / "bkg.npz"
        self.lat.write_bytes(b"lat")
        self.bkg.write_bytes(b"bkg")
        self.rec = self.tmp / "check.json"
        self.rec.write_text(json.dumps({"schema": "fd-ct-5b-inputs/1", "period": period,
                                        "files": {"lat_npz": [str(self.lat), digest(self.lat)],
                                                  "lat_bkg": [str(self.bkg), digest(self.bkg)]}}))
        self.out = self.tmp / "unf"
        return ["unfold", "--period", "PA", "--receipt", str(self.rec), "--pairs=3:-", "--tag", "5b_PA", "--out",
                str(self.out)]

    def fake(self, write=True):
        calls = []

        def run(cmd, *a, **k):
            calls.append(cmd)
            if write:
                self.out.mkdir(exist_ok=True)
                (self.out / "5b_PA_b3_j-.npz").write_bytes(b"u")
            return subprocess.CompletedProcess(cmd, 0)
        return calls, mock.patch.object(pi.subprocess, "run", run)

    def test_runs_s5p_numerics_as_declared(self):
        argv = self.build()
        calls, p = self.fake()
        rc, _, err = self.run_pi(argv, [p])
        self.assertEqual(rc, 0, err)
        c = calls[0]
        self.assertEqual(Path(c[1]).name, "s5p_numerics.py")
        for flag, v in (("--expect-npz-sha256", digest(self.lat)), ("--expect-bkg-sha256", digest(self.bkg)),
                        ("--config", "R"), ("--iters", "5"), ("--construction", "data"), ("--estimator-seed", "42"),
                        ("--threads", "32"), ("--tag", "5b_PA")):
            self.assertEqual(c[c.index(flag) + 1], v, flag)
        self.assertIn("--pairs=3:-", c)

    def test_refuses_an_existing_product(self):
        argv = self.build()
        self.out.mkdir()
        (self.out / "5b_PA_b3_j-.npz").write_bytes(b"old")
        calls, p = self.fake()
        rc, _, _ = self.run_pi(argv, [p])
        self.assertEqual((rc, calls), (3, []))

    def test_refuses_another_periods_receipt_or_a_changed_dump(self):
        argv = self.build(period="PB")
        calls, p = self.fake()
        self.assertEqual(self.run_pi(argv, [p])[0], 4)
        argv = self.build()
        self.bkg.write_bytes(b"changed")
        self.assertEqual(self.run_pi(argv, [p])[0], 4)
        self.assertEqual(calls, [])

    def test_an_exit_0_without_the_product_is_refused(self):
        argv = self.build()
        calls, p = self.fake(write=False)
        rc, _, err = self.run_pi(argv, [p])
        self.assertEqual(rc, 6)
        self.assertIn("without", err)


# ================================================================ fd_ct_periods

E_RAW = {"PA": 0.533, "PB": 0.295, "PC": 0.172}       # exposure shares, planted as pot x phi


class PTree:
    """A synthetic 5B run directory B: check receipts, dumps (data_pot, flux), MC truths, the 34 unfolds and MP-1's
    zero unfold, from planted cell integrals, over the readers' synthetic S1 assembly and C_resp."""

    def __init__(self, root: Path, seed=3):
        self.root = root
        self.t = TR.Tree(root / "s1", seed=seed).write_common()
        self.rng = np.random.default_rng(seed + 100)
        self.f = self.t.f
        self.B = root / "B"
        self.flux_pins, self.mp1 = {}, {}
        f = self.f
        self.T = {P: f * self.rng.uniform(0.9, 1.1, 16) * (1.0 if P == "ALL" else E_RAW[P]) for P in cp.PER + ("ALL",)}
        self.r = {"PA": 1.0 + self.rng.normal(0, 0.01, 16), "PB": 1.0 + self.rng.normal(0, 0.01, 16),
                  "PC": 1.0 + self.rng.normal(0, 0.01, 16)}
        self.X = {P: self.T[P] * self.r[P] for P in cp.PER}
        self.X["ALL"] = f * (1.0 + 0.3 * TAU * np.sign(self.rng.normal(size=16)))
        self.d = {P: [self.rng.normal(0, 0.004, 16) for _ in cp.BOOT[P]] for P in cp.PER}

    def write(self, receipt_over=None, meta_over=None):
        """Everything job A and the inputs make; the period unfolds come after the control (write_periods)."""
        B, t = self.B, self.t
        self.dumps = {}
        for d in ("inputs", "dumps", "truth", "flux"):
            (B / d).mkdir(parents=True, exist_ok=True)
        code_pi = sa.sha256(Path(pi.__file__).resolve())
        # each period its own flux; ALL's is the POT-weighted mean, so that POT_ALL Phi_ALL = sum_X POT_X Phi_X
        phis = {"PA": 2.0, "PB": 2.6, "PC": 1.7}
        pots = {P: E_RAW[P] / phis[P] * 1e21 for P in cp.PER}
        pots["ALL"] = sum(pots.values())
        phis["ALL"] = sum(pots[P] * phis[P] for P in cp.PER) / pots["ALL"]
        for P in cp.PER + ("ALL",):
            phi, pot = phis[P], pots[P]
            lat = B / "dumps" / f"lat_{P}.npz"
            np.savez(lat, data_pot=pot, flux=np.full(14, phi))
            bkg = B / "dumps" / f"lat_{P}_bkg.npz"
            np.savez(bkg, bkg_w=np.ones(3))
            flux = B / "flux" / f"runEventLoopMC_{P}.root"
            flux.write_bytes(f"flux {P}".encode())
            self.flux_pins[P] = digest(flux)
            truth = B / "truth" / f"truth_{P}.npz"
            np.savez(truth, xsec_flat=t.cellwise(self.T[P]), meta_json=json.dumps(
                {"schema": "s5p-mc-truth-pred/1", "npz_sha256": digest(lat),
                 "code_sha256": sa.sha256(ND / "s5p_mc_truth_pred.py")}))
            rec = {"schema": "fd-ct-5b-inputs/1", "period": P, "playlists": list(pi.PERIODS[P]),
                   "files": {k: [str(p), digest(p)] for k, p in (("lat_npz", lat), ("lat_bkg", bkg), ("truth", truth),
                                                                  ("flux", flux))},
                   "flux_constant_over_pt": True, "code_sha256": {"fd_ct_period_inputs.py": code_pi}}
            if P == "ALL":
                rec["all_vs_mp1_zero"] = {
                    "lat_npz": {**{k: True for k in pi.NPZ_KEYS}, "_key_sets_equal": True},
                    "lat_bkg": {**{k: True for k in pi.BKG_KEYS}, "_key_sets_equal": True},
                    "lat_npz_bytes_equal": True, "mp1_sha256": "MP1"}
            rec.update((receipt_over or {}).get(P, {}))
            (B / "inputs" / f"check_{P}.json").write_text(json.dumps(rec))
            self.dumps[P] = (lat, bkg)
        self.meta_over = meta_over
        self.write_unfolds("ALL")
        self.mp1_path = self.root / "mp1s1_zero_b-_j-.npz"
        np.savez(self.mp1_path, xsec_flat=self.fine("ALL", None), meta="{}")
        self.mp1 = {"unfold": digest(self.mp1_path), "lat_npz": "a" * 64, "lat_bkg": "b" * 64}
        for P in ("ALL",):
            p = B / "inputs" / f"check_{P}.json"
            rec = json.loads(p.read_text())
            if rec["all_vs_mp1_zero"].get("mp1_sha256") == "MP1":
                rec["all_vs_mp1_zero"]["mp1_sha256"] = {"lat_npz": "a" * 64, "lat_bkg": "b" * 64}
            p.write_text(json.dumps(rec))
        return self

    def fine(self, P, b):
        X = self.X[P] if b is None else self.X[P] * (1.0 + self.d[P][cp.BOOT[P].index(b)])
        return self.t.cellwise(X)

    def write_periods(self):
        for P in cp.PER:
            self.write_unfolds(P)
        return self

    def write_unfolds(self, P):
        lat, bkg = self.dumps[P]
        meta_over = self.meta_over
        for b in ((None,) if P == "ALL" else (None, *cp.BOOT[P])):
            p = cp.unf_path(self.B, P, b)
            p.parent.mkdir(parents=True, exist_ok=True)
            m = TR.data_meta(digest(lat), digest(bkg), bootstrap_seed=b,
                             code_sha256={"s5p_numerics.py": sa.sha256(ND / "s5p_numerics.py")})
            m.update((meta_over or {}).get((P, b), {}))
            np.savez(p, xsec_flat=self.fine(P, b), meta=json.dumps(m))

    def patches(self):
        return [mock.patch.dict(ct.PINS, self.t.pins), mock.patch.dict(pi.FLUX, self.flux_pins),
                mock.patch.dict(pi.MP1_ZERO, self.mp1)]

    def control_argv(self, out=None):
        return ["control", "--definition", str(DEFINITION), "--s1-npz", str(self.t.s1), "--cresp", str(self.t.cresp),
                "--b", str(self.B), "--mp1-zero", str(self.mp1_path), "--out-json",
                str(out or self.B / "control" / "fd_ct_5b_control.json")]

    def periods_argv(self, out=None):
        return ["periods", "--definition", str(DEFINITION), "--s1-npz", str(self.t.s1), "--cresp", str(self.t.cresp),
                "--b", str(self.B), "--control-json", str(self.B / "control" / "fd_ct_5b_control.json"),
                "--readout-5a", str(self.readout_5a), "--out-json", str(out or self.root / "out" / "periods.json")]

    def with_5a(self, g=None):
        self.readout_5a = self.root / "fd_ct_period.json"
        g = g or {P: np.zeros(16).tolist() for P in cp.PER}
        self.readout_5a.write_text(json.dumps({"variants": {"central": {"g": g}}}))
        return mock.patch.object(cp, "READOUT_5A_SHA256", digest(self.readout_5a))


class PeriodsBase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="ct5b-rd-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        (self.tmp / "out").mkdir()

    def tree(self, **kw):
        for p in list(self.tmp.iterdir()):
            shutil.rmtree(p) if p.is_dir() else p.unlink()
        (self.tmp / "out").mkdir()
        return PTree(self.tmp, **kw)

    def run_cp(self, t, argv, extra=()):
        with contextlib.ExitStack() as st:
            for p in [*t.patches(), *extra]:
                st.enter_context(p)
            (t.B / "control").mkdir(exist_ok=True)
            rc, self.stdout, self.stderr = quiet(cp.main, argv)
        return rc

    def control(self, t, extra=()):
        return self.run_cp(t, t.control_argv(), extra)

    def control_json(self, t):
        return json.loads((t.B / "control" / "fd_ct_5b_control.json").read_text())


class Jitter(unittest.TestCase):
    def test_the_declared_sigma_is_the_committed_receipts(self):
        U = sa.functional_matrix(sa.fine_map(DEFINITION))
        with contextlib.redirect_stdout(io.StringIO()):
            s = cp.jitter_sigma(REPO, U)
        np.testing.assert_allclose(s, cp.SIGMA_JITTER, rtol=1e-12, atol=0)
        # independently: five variants, five seeds, 20 dof, about each variant's own mean
        J = REPO / cp.JITTER_DIR
        dev = []
        for v in cp.JITTER_VARIANTS:
            X = np.array([U @ np.load(J / f"mp1nj_{v}_b-_j{k}.npz")["xsec_flat"] for k in range(1, 6)])
            dev += [x / X.mean(axis=0) - 1 for x in X]
        np.testing.assert_allclose(np.sqrt(np.sum(np.square(dev), axis=0) / 20), cp.SIGMA_JITTER, rtol=1e-12)
        self.assertAlmostEqual(cp.TAU_K, 5 * 2 ** 0.5)

    def test_a_jitter_product_at_another_digest_refuses(self):
        U = sa.functional_matrix(sa.fine_map(DEFINITION))
        with mock.patch.dict(cp.JITTER, {"em_p1_j4": "0" * 64}), self.assertRaises(F.Stop):
            cp.jitter_sigma(REPO, U)


class Control(PeriodsBase):
    def test_passes_when_bitwise_and_within_tolerance(self):
        t = self.tree().write()
        self.assertEqual(self.control(t), 0, self.stderr)
        o = self.control_json(t)
        self.assertEqual(o["verdict"], "PASS")
        self.assertEqual(o["K3_within_tolerance_of_f"]["within_by_cell"], [True] * 16)
        self.assertTrue(o["K1_inputs_bitwise_mp1_zero"]["pass"] and o["K2_unfold_bitwise_mp1_zero"]["pass"])

    def test_the_record_does_not_give_f_back_with_the_public_x_all(self):
        # review H2: X_ALL is public once K2 holds; no written number may be |X/f - 1| or its ratio to tau
        t = self.tree().write()
        self.assertEqual(self.control(t), 0, self.stderr)
        text = (t.B / "control" / "fd_ct_5b_control.json").read_text() + self.stdout
        nums = np.array([abs(float(v)) for v in F._NUM.findall(text)])
        rel = np.abs(t.X["ALL"] / t.f - 1.0)
        for target in (*rel, *(rel / TAU)):
            self.assertFalse(np.any(np.abs(nums - target) <= 1e-9 * target), target)

    def test_refuses_while_a_period_unfold_exists(self):
        t = self.tree().write()
        (t.B / "unf" / "PB").mkdir(parents=True, exist_ok=True)
        self.assertRefuses(t, "period unfolds exist before the control")

    def test_k3_decides_in_both_directions(self):
        for factor, verdict, rc in ((0.99, "PASS", 0), (1.01, "FAIL", 1)):
            with self.subTest(factor=factor):
                t = self.tree()
                t.X["ALL"][5] = t.f[5] * (1.0 - factor * TAU[5])
                t.write()
                self.assertEqual(self.control(t), rc, self.stderr)
                o = self.control_json(t)
                self.assertEqual(o["verdict"], verdict)
                self.assertEqual(o["K3_within_tolerance_of_f"]["cells_over"], [] if rc == 0 else ["R05"])
                shutil.rmtree(self.tmp)
                (self.tmp / "out").mkdir(parents=True)

    def test_k2_fails_on_one_fine_cell(self):
        t = self.tree().write()
        x = np.load(t.mp1_path)["xsec_flat"].copy()
        x[12345] = np.nextafter(x[12345], 1.0)
        np.savez(t.mp1_path, xsec_flat=x, meta="{}")
        t.mp1["unfold"] = digest(t.mp1_path)
        self.assertEqual(self.control(t), 1)
        o = self.control_json(t)
        self.assertEqual((o["verdict"], o["K2_unfold_bitwise_mp1_zero"]["pass"]), ("FAIL", False))
        self.assertGreater(o["K2_unfold_bitwise_mp1_zero"]["max_rel_diff_fine_cells"], 0)

    def test_k1_fails_on_one_recorded_key(self):
        for d, k in (("lat_npz", "MCreco"), ("lat_bkg", "bkg_reco"), ("lat_npz", "_key_sets_equal")):
            with self.subTest(key=k):
                t = self.tree().write()
                p = t.B / "inputs/check_ALL.json"
                rec = json.loads(p.read_text())
                rec["all_vs_mp1_zero"][d][k] = False
                p.write_text(json.dumps(rec))
                self.assertEqual(self.control(t), 1)
                o = self.control_json(t)
                self.assertEqual(o["K1_inputs_bitwise_mp1_zero"]["failed_keys"], [f"{d}:{k}"])
                shutil.rmtree(self.tmp)
                (self.tmp / "out").mkdir(parents=True)

    def assertRefuses(self, t, msg, extra=()):
        self.assertEqual(self.control(t, extra), 1, self.stderr)
        self.assertIn(msg, self.stderr)
        self.assertFalse((t.B / "control" / "fd_ct_5b_control.json").exists())

    def test_refuses_a_comparison_missing_a_key(self):
        t = self.tree().write()
        p = t.B / "inputs/check_ALL.json"
        rec = json.loads(p.read_text())
        del rec["all_vs_mp1_zero"]["lat_npz"]["w_reco"]
        p.write_text(json.dumps(rec))
        self.assertRefuses(t, "every declared key")

    def test_refuses_a_receipt_of_other_code_or_a_moved_dump(self):
        t = self.tree().write()
        p = t.B / "inputs/check_ALL.json"
        rec = json.loads(p.read_text())
        rec["code_sha256"]["fd_ct_period_inputs.py"] = "0" * 64
        p.write_text(json.dumps(rec))
        self.assertRefuses(t, "not made by this deploy")
        t = self.tree().write()
        (t.B / "dumps/lat_ALL_bkg.npz").write_bytes(b"other")
        self.assertRefuses(t, "ALL lat_bkg")

    def test_refuses_an_all_unfold_not_made_as_declared(self):
        for over, msg in (({"bootstrap_seed": 1}, "bootstrap_seed"), ({"input_npz_sha256": "0" * 64}, "input_npz"),
                          ({"code_sha256": {"s5p_numerics.py": "0" * 64}}, "s5p_numerics.py"),
                          ({"estimator_seed": 43}, "config/capacity/iters/seed")):
            with self.subTest(over=over):
                t = self.tree().write(meta_over={("ALL", None): over})
                self.assertRefuses(t, msg)

    def test_refuses_another_mp1_zero(self):
        t = self.tree().write()
        t.mp1["unfold"] = "0" * 64
        self.assertRefuses(t, "MP-1 mp1s1_zero")

    def test_refuses_a_non_positive_all_integral(self):
        t = self.tree()
        t.X["ALL"][3] = -t.X["ALL"][3]
        t.write()
        self.assertRefuses(t, "every ALL cell integral is positive")

    def test_refuses_a_tolerance_not_the_declared_one(self):
        t = self.tree().write()
        bad = list(cp.SIGMA_JITTER)
        bad[3] *= 1.0 + 1e-9
        self.assertRefuses(t, "not the declared one", [mock.patch.object(cp, "SIGMA_JITTER", tuple(bad))])

    def test_reads_no_period_product(self):
        t = self.tree().write()
        for P in cp.PER:
            (t.B / "inputs" / f"check_{P}.json").write_text("not json")
        self.assertEqual(self.control(t), 0, self.stderr)

    def test_an_all_integral_within_leak_rel_of_f_is_not_falsely_refused(self):
        t = self.tree()
        t.X["ALL"][9] = t.f[9] * (1 + 3e-14)
        t.write()
        self.assertEqual(self.control(t), 0, self.stderr)
        # the mode amendment 1 repaired: passed to the guard unfiltered, it refuses every '1' in a string
        raw = mock.patch.object(cp, "guarded", lambda f, ints: F.LeakGuard(f, list(ints)))
        shutil.rmtree(t.B / "control")
        self.assertEqual(self.control(t, [raw]), 3)
        self.assertIn("REFUSED leak guard", self.stderr)

    def test_the_guard_refuses_a_planted_ratio_to_f(self):
        t = self.tree().write()
        planted = float(t.X["ALL"][2] / t.f[2] - 1.0)
        orig = ct.cells
        leak = mock.patch.object(cp.ct, "cells", lambda idx=None: [planted] if idx is not None else orig())
        self.assertEqual(self.control(t, [leak]), 3)
        self.assertFalse((t.B / "control" / "fd_ct_5b_control.json").exists())


class Precheck(PeriodsBase):
    def precheck(self, t, extra=()):
        argv = t.control_argv(t.B / "control" / "fd_ct_5b_precheck.json")
        argv[0] = "precheck"
        return self.run_cp(t, argv, extra)

    def test_decides_k3_on_mp1s_zero_in_both_directions_and_writes_flags_only(self):
        for factor, verdict, rc in ((0.99, "PASS", 0), (1.01, "FAIL", 1)):
            with self.subTest(factor=factor):
                t = self.tree()
                t.X["ALL"][11] = t.f[11] * (1.0 + factor * TAU[11])
                t.write()
                self.assertEqual(self.precheck(t), rc, self.stderr)
                o = json.loads((t.B / "control" / "fd_ct_5b_precheck.json").read_text())
                self.assertEqual((o["verdict"], o["K3_within_tolerance_of_f"]["cells_over"]),
                                 (verdict, [] if rc == 0 else ["R11"]))
                self.assertNotIn("q", o["K3_within_tolerance_of_f"])

    def test_refuses_another_mp1_zero(self):
        t = self.tree().write()
        t.mp1["unfold"] = "0" * 64
        self.assertEqual(self.precheck(t), 1)
        self.assertIn("MP-1 mp1s1_zero", self.stderr)


class Gate(PeriodsBase):
    def gate(self, t, stage):
        return self.run_cp(t, ["gate", "--stage", stage, "--b", str(t.B)])

    def precheck(self, t):
        argv = t.control_argv(t.B / "control" / "fd_ct_5b_precheck.json")
        argv[0] = "precheck"
        return self.run_cp(t, argv)

    def test_inputs_gate(self):
        t = self.tree().write()
        (t.B / "control").mkdir(exist_ok=True)
        self.assertEqual(self.gate(t, "inputs"), 1)
        self.assertEqual(self.precheck(t), 0, self.stderr)
        self.assertEqual(self.gate(t, "inputs"), 0, self.stderr)
        p = t.B / "control" / "fd_ct_5b_precheck.json"
        o = json.loads(p.read_text())
        for over, msg in (({"verdict": "FAIL"}, "does not record a PASS"), ({"schema": "fd-ct-5b-control/1"}, "PASS"),
                          ({"code_sha256": {"fd_ct_periods.py": "0" * 64}}, "this deploy")):
            with self.subTest(over=over):
                p.write_text(json.dumps({**o, **over}))
                self.assertEqual(self.gate(t, "inputs"), 1)
                self.assertIn(msg, self.stderr)

    def test_periods_gate(self):
        t = self.tree().write()
        self.assertEqual(self.gate(t, "periods"), 1)
        self.assertEqual(self.control(t), 0, self.stderr)
        self.assertEqual(self.gate(t, "periods"), 0, self.stderr)
        (t.B / "inputs" / "check_PC.json").unlink()
        self.assertEqual(self.gate(t, "periods"), 1)
        self.assertIn("no check receipt", self.stderr)
        t2 = self.tree().write()
        self.assertEqual(self.control(t2), 0, self.stderr)
        p = cp.unf_path(t2.B, "ALL", None)
        z = dict(np.load(p))
        z["meta"] = str(z["meta"]) + " "
        np.savez(p, **z)
        self.assertEqual(self.gate(t2, "periods"), 1)
        self.assertIn("not the one the control read", self.stderr)


class Periods(PeriodsBase):
    def ready(self, **kw):
        t = self.tree(**kw).write()
        p5a = t.with_5a()
        self.assertEqual(self.control(t), 0, self.stderr)
        return t.write_periods(), p5a

    def periods(self, t, p5a, extra=()):
        return self.run_cp(t, t.periods_argv(), [p5a, *extra])

    def readout(self, t):
        return json.loads((t.root / "out" / "periods.json").read_text())

    def test_the_readout_recomputed_by_hand(self):
        t, p5a = self.ready()
        self.assertEqual(self.periods(t, p5a), 0, self.stderr)
        o = self.readout(t)
        M = (t.t.Ct + t.t.Cr) / np.outer(t.f, t.f)
        r = {P: t.X[P] / t.T[P] for P in cp.PER}
        e = {P: E_RAW[P] / sum(E_RAW.values()) for P in cp.PER}
        for n, d in (("PB", "PA"), ("PC", "PA"), ("PC", "PB")):
            c = o["comparisons"][f"dr_{n}/{d}"]
            v = r[n] / r[d] - 1
            np.testing.assert_allclose(c["shift"], v, rtol=1e-10, atol=1e-15)
            self.assertAlmostEqual(c["chi2_M"], float(v @ np.linalg.solve(M, v)), places=6)
            N = np.zeros((16, 16))
            for X, a in ((n, 1.0), (d, -1.0)):
                for k in range(10):
                    N += a * a * np.outer(t.d[X][k], t.d[X][k]) / 10
            self.assertAlmostEqual(c["noise"]["expected_chi2_M"], float(np.trace(np.linalg.solve(M, N))), places=6)
            draws = [float((t.d[n][k] - t.d[d][k]) @ np.linalg.solve(M, t.d[n][k] - t.d[d][k])) for k in range(10)]
            np.testing.assert_allclose(c["noise"]["draw_chi2_M"], draws, rtol=1e-6)
            hi, lo = list(cp.PZ_HI), list(cp.PZ_LO)
            q = lambda s: (t.X[n][s].sum() / t.T[n][s].sum()) / (t.X[d][s].sum() / t.T[d][s].sum())  # noqa: E731
            self.assertAlmostEqual(c["pz_contrast"], q(hi) / q(lo) - 1, places=12)
        raw = o["comparisons"]["raw_PB/PA"]["shift"]
        np.testing.assert_allclose(raw, t.X["PB"] / t.X["PA"] - 1, rtol=1e-10)
        np.testing.assert_allclose(o["comparisons"]["mc_PC/PA"]["shift"], t.T["PC"] / t.T["PA"] - 1, rtol=1e-10)
        for P in cp.PER:
            self.assertAlmostEqual(o["constants"]["exposure_share"][P], e[P], places=12)
        m = sum(e[P] * r[P] for P in cp.PER)
        V2 = sum(v * v for v in e.values())
        C = np.zeros((16, 16))
        for P in cp.PER:
            g = r[P] / m - 1
            C += V2 / (1 - V2) * e[P] * np.outer(g, g)
        np.testing.assert_allclose(o["C_PL5D"]["C_PL5D_rel"], C, rtol=1e-9, atol=1e-18)
        self.assertLessEqual(o["C_PL5D"]["rank"], 2)
        # review H2: nothing relative to ALL, whose committed integrals would make a ratio absolute
        self.assertFalse([k for k in o["comparisons"] if "ALL" in k or "J36" in k])
        self.assertIn("[5B] dr_PB/PA", self.stdout)

    def test_consistent_periods_read_as_zero(self):
        t = self.tree()
        # agreeing to 1e-9 (exact agreement leaves rounding residue below the guard's 1e-30 floor, which it refuses
        # as an absolute value; real offsets are many orders above it)
        for k, P in enumerate(cp.PER):
            t.r[P] = np.full(16, 1.02 * (1 + 1e-9 * k))
            t.X[P] = t.T[P] * t.r[P]
        t.write()
        p5a = t.with_5a()
        self.assertEqual(self.control(t), 0, self.stderr)
        t.write_periods()
        self.assertEqual(self.periods(t, p5a), 0, self.stderr)
        o = self.readout(t)
        for nm in ("dr_PB/PA", "dr_PC/PA", "dr_PC/PB"):
            self.assertLess(max(abs(v) for v in o["comparisons"][nm]["shift"]), 3e-9)
        self.assertLess(o["C_PL5D"]["sigma_rel_summary"]["max"], 1e-8)
        self.assertLess(max(abs(v) for P in cp.PER for v in o["g_vs_5A"]["periods"][P]["difference"]), 3e-9)

    def test_a_planted_pz_step_is_read_where_it_was_planted(self):
        t = self.tree()
        for P in cp.PER:
            t.r[P] = np.ones(16)
        t.r["PB"] = np.where(np.isin(np.arange(16), cp.PZ_HI), 1.07, 1.0)
        for P in cp.PER:
            t.X[P] = t.T[P] * t.r[P]
        t.write()
        p5a = t.with_5a()
        self.assertEqual(self.control(t), 0, self.stderr)
        t.write_periods()
        self.assertEqual(self.periods(t, p5a), 0, self.stderr)
        c = self.readout(t)["comparisons"]["dr_PB/PA"]
        self.assertAlmostEqual(c["pz_contrast"], 0.07, places=12)
        self.assertTrue(c["noise"]["exceeds_every_draw"])
        self.assertGreater(c["noise"]["pz_contrast_z"], 3)

    def test_g_against_5a(self):
        t, _ = self.ready()
        e = {P: E_RAW[P] / sum(E_RAW.values()) for P in cp.PER}
        r = {P: t.X[P] / t.T[P] for P in cp.PER}
        m = sum(e[P] * r[P] for P in cp.PER)
        g5a = {P: (r[P] / m - 1 + 0.001).tolist() for P in cp.PER}
        p5a = t.with_5a(g5a)
        self.assertEqual(self.periods(t, p5a), 0, self.stderr)
        for P in cp.PER:
            np.testing.assert_allclose(self.readout(t)["g_vs_5A"]["periods"][P]["difference"], -0.001, atol=1e-12)

    def assertRefuses(self, t, p5a, msg, extra=()):
        self.assertEqual(self.periods(t, p5a, extra), 1, self.stderr)
        self.assertIn(msg, self.stderr)
        self.assertFalse((t.root / "out" / "periods.json").exists())

    def test_refuses_without_a_passing_control(self):
        t = self.tree()
        t.X["ALL"][0] = t.f[0] * (1 + 2 * TAU[0])
        t.write()
        p5a = t.with_5a()
        self.assertEqual(self.control(t), 1)
        t.write_periods()
        self.assertRefuses(t, p5a, "did not PASS")

    def test_refuses_an_all_unfold_changed_after_the_control(self):
        t, p5a = self.ready()
        p = cp.unf_path(t.B, "ALL", None)
        z = dict(np.load(p))
        np.savez(p, **z)
        os.utime(p)
        z["meta"] = str(z["meta"]).replace('"construction"', '"construction" ')
        np.savez(p, **z)
        self.assertRefuses(t, p5a, "not the one the control read")

    def test_refuses_a_missing_or_extra_replica(self):
        t, p5a = self.ready()
        cp.unf_path(t.B, "PC", 3007).unlink()
        self.assertRefuses(t, p5a, "PC: the unfold directory")
        t, p5a = self.ready()
        shutil.copy(cp.unf_path(t.B, "PB", 2001), t.B / "unf/PB/5b_PB_b2011_j-.npz")
        self.assertRefuses(t, p5a, "PB: the unfold directory")

    def test_refuses_a_replica_not_made_as_declared(self):
        for key, over, msg in ((("PA", 1004), {"bootstrap_seed": 2004}, "bootstrap_seed"),
                               (("PB", None), {"jitter_seed": 1}, "jitter_seed"),
                               (("PC", 3002), {"code_sha256": {"s5p_numerics.py": "0" * 64}}, "s5p_numerics.py")):
            with self.subTest(key=key):
                t = self.tree().write(meta_over={key: over})
                p5a = t.with_5a()
                self.assertEqual(self.control(t), 0, self.stderr)
                t.write_periods()
                self.assertRefuses(t, p5a, msg)
                shutil.rmtree(self.tmp)
                (self.tmp / "out").mkdir(parents=True)

    def test_refuses_a_truth_of_another_npz_or_another_5a_readout(self):
        t, p5a = self.ready()
        tp = t.B / "truth/truth_PB.npz"
        z = dict(np.load(tp))
        z["meta_json"] = json.dumps({**json.loads(str(z["meta_json"])), "npz_sha256": "0" * 64})
        np.savez(tp, **z)
        p = t.B / "inputs/check_PB.json"
        rec = json.loads(p.read_text())
        rec["files"]["truth"][1] = digest(tp)
        p.write_text(json.dumps(rec))
        self.assertRefuses(t, p5a, "not the MC truth of PB")
        t, _ = self.ready()
        self.assertRefuses(t, mock.patch.object(cp, "READOUT_5A_SHA256", "0" * 64), "5A readout")

    def test_refuses_a_non_positive_integral(self):
        t, p5a = self.ready()
        tp = t.B / "truth/truth_PB.npz"
        z = dict(np.load(tp))
        x = z["xsec_flat"].copy()
        x[t.t.fm == 6] *= -1.0
        z["xsec_flat"] = x
        np.savez(tp, **z)
        p = t.B / "inputs/check_PB.json"
        rec = json.loads(p.read_text())
        rec["files"]["truth"][1] = digest(tp)
        p.write_text(json.dumps(rec))
        self.assertRefuses(t, p5a, "positive on all 16 cells")

    def test_refuses_another_cell_definition(self):
        t, p5a = self.ready()
        self.assertRefuses(t, p5a, "p_parallel cell sets", [mock.patch.object(cp, "PZ_LO", (0, 1, 2, 3, 8, 9, 10, 12))])

    def test_refuses_a_truth_of_other_code(self):
        t, p5a = self.ready()
        tp = t.B / "truth/truth_PA.npz"
        z = dict(np.load(tp))
        z["meta_json"] = json.dumps({**json.loads(str(z["meta_json"])), "code_sha256": "0" * 64})
        np.savez(tp, **z)
        p = t.B / "inputs/check_PA.json"
        rec = json.loads(p.read_text())
        rec["files"]["truth"][1] = digest(tp)
        p.write_text(json.dumps(rec))
        self.assertRefuses(t, p5a, "code or shape")

    def test_refuses_a_flux_that_is_not_pt_constant(self):
        t = self.tree().write(receipt_over={"PC": {"flux_constant_over_pt": False}})
        p5a = t.with_5a()
        self.assertEqual(self.control(t), 0, self.stderr)
        t.write_periods()
        self.assertRefuses(t, p5a, "not constant over p_T")

    def test_an_integral_within_leak_rel_of_f_is_dropped_from_the_guard(self):
        t = self.tree()
        x = t.f * 1.03
        x[4] = t.f[4] * (1 + 2e-14)
        g = cp.guarded(t.f, [x])
        self.assertEqual(g.count("1 period, 1.0 and 1"), 0)
        self.assertEqual(g.count(float(x[7] / t.f[7] - 1.0)), 1)
        self.assertGreater(F.LeakGuard(t.f, [x]).count("1 period, 1.0 and 1"), 0)   # the mode amendment 1 repaired

    def test_a_ratio_against_a_near_f_integral_is_refused_as_relative_to_f(self):
        # declared (section 3): such a ratio IS X/f - 1 to LEAK_REL; the run stops rather than write it
        t = self.tree()
        t.X["PA"][4] = t.f[4] * (1 + 2e-14)
        t.T["PA"][4] = t.X["PA"][4] / t.r["PA"][4]
        t.write()
        p5a = t.with_5a()
        self.assertEqual(self.control(t), 0, self.stderr)
        t.write_periods()
        self.assertEqual(self.periods(t, p5a), 3)
        self.assertFalse((t.root / "out" / "periods.json").exists())

    def test_the_guard_refuses_a_planted_absolute_value(self):
        t, p5a = self.ready()
        planted = float(t.X["PB"][3])
        leak = mock.patch.object(cp.ct, "summary", lambda v, x=planted: {"median": x, "min": x, "max": x})
        self.assertEqual(self.periods(t, p5a, [leak]), 3)
        self.assertIn("REFUSED leak guard", self.stderr)
        self.assertFalse((t.root / "out" / "periods.json").exists())

    def test_the_guard_refuses_a_planted_mc_truth_integral(self):
        t, p5a = self.ready()
        planted = float(t.T["PB"][3] / t.f[3] - 1.0)   # relative, so only the truths in the table can catch it
        leak = mock.patch.object(cp.ct, "summary", lambda v, x=planted: {"median": x, "min": x, "max": x})
        self.assertEqual(self.periods(t, p5a, [leak]), 3)

    def test_the_guard_refuses_a_planted_ratio_of_a_period_to_f(self):
        t, p5a = self.ready()
        planted = float(t.X["PC"][11] / t.f[11])
        leak = mock.patch.object(cp.ct, "summary", lambda v, x=planted: {"median": x, "min": x, "max": x})
        self.assertEqual(self.periods(t, p5a, [leak]), 3)


class BareInterpreter(PeriodsBase):
    """The declared recipe (section 2) runs stage-flux, precheck, control, gate and periods with root_6_28's bare
    interpreter, which segfaults on `import ROOT` without the env active (section 11). So each of those paths runs
    here with ROOT unimportable: any import of it, at module load or inside a function, fails loudly."""

    def test_the_bare_recipes_modules_load_without_root(self):
        code = (f"import sys; sys.modules['ROOT'] = None; sys.path.insert(0, {str(ND)!r}); "
                "import fd_ct_periods, fd_ct_period_inputs; print('ROOT' in sys.modules and sys.modules['ROOT'])")
        r = subprocess.run([sys.executable, "-I", "-B", "-c", code], capture_output=True, text=True,
                           env={k: v for k, v in os.environ.items() if k != "PYTHONPATH"})
        self.assertEqual((r.returncode, r.stdout.strip()), (0, "None"), r.stderr)

    def test_the_bare_recipes_paths_run_without_root(self):
        with mock.patch.dict(sys.modules, {"ROOT": None}):
            src = self.tmp / "src"
            src.mkdir()
            pins = {}
            for P in pi.FLUX:
                (src / f"runEventLoopMC_{P}.root").write_bytes(P.encode())
                pins[P] = digest(src / f"runEventLoopMC_{P}.root")
            with mock.patch.dict(pi.FLUX, pins):
                rc, _, err = quiet(pi.main, ["stage-flux", "--src-dir", str(src), "--out-dir", str(self.tmp / "fx")])
            self.assertEqual(rc, 0, err)
            t = self.tree().write()
            p5a = t.with_5a()
            argv = t.control_argv(t.B / "control" / "fd_ct_5b_precheck.json")
            argv[0] = "precheck"
            self.assertEqual(self.run_cp(t, argv), 0, self.stderr)
            self.assertEqual(self.run_cp(t, ["gate", "--stage", "inputs", "--b", str(t.B)]), 0, self.stderr)
            self.assertEqual(self.control(t), 0, self.stderr)
            t.write_periods()
            self.assertEqual(self.run_cp(t, ["gate", "--stage", "periods", "--b", str(t.B)]), 0, self.stderr)
            self.assertEqual(self.run_cp(t, t.periods_argv(), [p5a]), 0, self.stderr)

    def test_the_root_readers_do_need_root(self):
        # the direction the check acts in: a path that imports ROOT does fail with ROOT blocked
        with mock.patch.dict(sys.modules, {"ROOT": None}), self.assertRaises(ImportError):
            pi.flux_data_pot(self.tmp / "x.root")


# ================================================================ tables and submit


class Tables(unittest.TestCase):
    def test_the_committed_tables_are_the_generators(self):
        with tempfile.TemporaryDirectory() as d:
            r = subprocess.run([sys.executable, "-I", "-B", str(REPO / REL5 / "make_5b_tables.py"), str(REPO), d],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            for n in ("5b-inputs-steps.tsv", "tasks-5b-inputs.tsv", "5b-periods-steps.tsv", "tasks-5b-periods.tsv"):
                self.assertEqual((Path(d) / n).read_bytes(), (REPO / REL5 / n).read_bytes(), n)

    def rows(self, name):
        return [ln.split("\t") for ln in (REPO / REL5 / name).read_text().splitlines() if ln and not ln.startswith("#")]

    def test_job_a(self):
        rows = self.rows("5b-inputs-steps.tsv")
        self.assertEqual(len(rows), 17)
        for lane, P in enumerate(("ALL", "PA", "PB", "PC")):
            names = [r[1] for r in rows if r[0] == str(lane)]
            want = [f"ct5b_{s}_{P}" for s in ("merge", "nndump", "lateral", "check")]
            self.assertEqual(names, want + (["ct5b_unfold_ALL_s42"] if P == "ALL" else []))
        for r in (r for r in rows if r[1].startswith("ct5b_merge")):
            self.assertTrue(r[r.index("--flux") + 1].endswith(f"/flux/runEventLoopMC_{r[1].split('_')[-1]}.root"))
        nn = [r for r in rows if r[1].startswith("ct5b_nndump")]
        for r in nn:
            self.assertEqual(r[r.index("--axes") + 1], "eavail,q3,W")
            self.assertTrue(r[r.index("--mcfile") + 1].endswith(f"/flux/runEventLoopMC_{r[1].split('_')[-1]}.root"))
        lat = [r for r in rows if r[1].startswith("ct5b_lateral")]
        for r in lat:
            P = r[1].split("_")[-1]
            self.assertTrue(r[r.index("--cv-npz") + 1].endswith(f"/dumps/nn_{P}.npz"))
        u = [r for r in rows if r[1] == "ct5b_unfold_ALL_s42"][0]
        self.assertIn("--pairs=-:-", u)

    def test_each_period_has_its_own_seed_block(self):
        seeds = [b for P in cp.PER for b in cp.BOOT[P]]
        self.assertEqual(len(seeds), len(set(seeds)))
        self.assertEqual({P: (min(cp.BOOT[P]), max(cp.BOOT[P])) for P in cp.PER},
                         {"PA": (1001, 1010), "PB": (2001, 2010), "PC": (3001, 3010)})   # 2D's blocks
        # and s5n_pseudo's three streams of one replica (seeds b, b + 1e7, b + 2e7) do not overlap another's
        streams = {b + o for b in seeds for o in (0, 10_000_000, 20_000_000)}
        self.assertEqual(len(streams), 3 * len(seeds))

    def test_job_b_runs_each_declared_unfold_once(self):
        rows = self.rows("5b-periods-steps.tsv")
        got = sorted((r[r.index("--period") + 1], [a for a in r if a.startswith("--pairs=")][0]) for r in rows)
        want = sorted((P, f"--pairs={b}:-") for P in cp.PER for b in ("-", *map(str, cp.BOOT[P])))
        self.assertEqual(got, want)
        self.assertEqual(sorted({r[0] for r in rows}), [str(k) for k in range(8)])
        for r in rows:
            self.assertEqual(r[r.index("--estimator-seed") + 1], "42")
            P = r[r.index("--period") + 1]
            self.assertTrue(r[r.index("--out") + 1].endswith(f"/unf/{P}"))


class Submit(unittest.TestCase):
    """submit_fd_ct.sh 5b-* in a throwaway git repo whose tables write under a temporary B, with a stub sbatch and a
    stub login-node interpreter (FD_CT_PY) that records the flux staging and answers the verdict check."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="ct5b-submit-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.B, self.D = self.tmp / "B", self.tmp / "deploy"
        (self.D / REL5).mkdir(parents=True)
        real_b = "/pscratch/sd/j/josephrb/fd-ct-5b-20261030"
        for n in ("5b-inputs-steps.tsv", "tasks-5b-inputs.tsv", "5b-periods-steps.tsv", "tasks-5b-periods.tsv"):
            (self.D / REL5 / n).write_text((REPO / REL5 / n).read_text().replace(real_b, str(self.B)))
        run = lambda *a: subprocess.run(["git", "-C", str(self.D), *a], check=True, capture_output=True)  # noqa: E731
        run("init", "-q"); run("add", "-A")
        run("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "t")
        self.pin = subprocess.run(["git", "-C", str(self.D), "rev-parse", "HEAD"], capture_output=True,
                                  text=True).stdout.strip()
        b = self.tmp / "bin"
        b.mkdir()
        (b / "sbatch").write_text(f"#!/bin/bash\nprintf '%s\\n' \"$@\" > {self.tmp}/sbatch.args\necho Submitted\n")
        # the stub records the flux staging and the gate call; the gate passes only where the test put gate-ok
        (b / "py").write_text(
            "#!/bin/bash\n"
            f"if [ \"$2\" = stage-flux ]; then echo \"$@\" > {self.tmp}/stage.args; mkdir -p \"$4\"; exit 0; fi\n"
            f"if [ \"$2\" = gate ]; then echo \"$@\" >> {self.tmp}/gate.args; [ -e \"$6/control/gate-ok-$4\" ]; exit; fi\n"
            "exit 9\n")
        for x in ("sbatch", "py"):
            (b / x).chmod(0o755)
        self.env = {**os.environ, "PATH": f"{b}:{os.environ['PATH']}", "FD_CT_PY": str(b / "py")}

    def submit(self, *args):
        return subprocess.run(["bash", str(ND / "submit_fd_ct.sh"), *args], capture_output=True, text=True,
                              env=self.env)

    def gate_ok(self, stage):
        (self.B / "control").mkdir(parents=True, exist_ok=True)
        (self.B / "control" / f"gate-ok-{stage}").write_text("")

    def args(self):
        return (self.tmp / "sbatch.args").read_text().splitlines()

    def test_the_committed_inputs_submission(self):
        self.gate_ok("inputs")
        r = self.submit("5b-inputs", str(self.D), self.pin, str(self.B))
        self.assertEqual(r.returncode, 0, r.stderr)
        a = self.args()
        for want in ("--account=m3246", "--qos=regular", "--constraint=cpu", "--nodes=1", "--exclusive",
                     "--no-requeue", "--time=01:00:00", "--job-name=fd_ct_5b_inputs", "32", "56G", "0", "3", "none",
                     str(self.B / "lanes-inputs")):
            self.assertIn(want, a)
        self.assertFalse([x for x in a if "gpu" in x.lower() and "gpu-timing" not in x], "a GPU request")
        self.assertEqual([x for x in a if x.startswith(("--qos", "--time"))], ["--qos=regular", "--time=01:00:00"])
        self.assertIn(f"stage-flux --out-dir {self.B}/flux", (self.tmp / "stage.args").read_text())
        self.assertIn(f"gate --stage inputs --b {self.B}", (self.tmp / "gate.args").read_text())
        for d in ("dumps", "truth", "inputs"):   # review H1: the steps' output folders exist before the job
            self.assertTrue((self.B / d).is_dir(), d)

    def test_inputs_refuse_without_the_precheck_gate(self):
        (self.B / "control").mkdir(parents=True)
        r = self.submit("5b-inputs", str(self.D), self.pin, str(self.B))
        self.assertEqual(r.returncode, 2)
        self.assertIn("the gate did not pass", r.stderr)
        self.assertFalse((self.tmp / "sbatch.args").exists() or (self.B / "flux").exists() or (self.B / "dumps").exists())

    def test_the_lanes_fit_one_node(self):
        # review M4: an exclusive node through this launcher is allocated 487,802M (sacct, job 60439400) and 256 CPUs
        for stage, lanes in (("5b-inputs", 4), ("5b-periods", 8)):
            text = (ND / "submit_fd_ct.sh").read_text()
            block = text[text.index(f'if [ "$STAGE" = 5b-inputs ]; then' if stage == "5b-inputs" else "    else\n      TABLE"):]
            cpt = int(block.split("CPT=")[1].split(";")[0])
            mem = int(block.split("MEM=")[1].split("G")[0])
            self.assertLessEqual(lanes * cpt, 256, stage)
            self.assertLessEqual(lanes * mem * 1024, 487802, stage)

    def test_inputs_refuse_an_existing_run_directory(self):
        for d in ("merged", "dumps", "unf", "flux"):
            with self.subTest(d=d):
                (self.B / d).mkdir(parents=True)
                r = self.submit("5b-inputs", str(self.D), self.pin, str(self.B))
                self.assertEqual(r.returncode, 2)
                self.assertIn("exists", r.stderr)
                self.assertFalse((self.tmp / "sbatch.args").exists())
                shutil.rmtree(self.B)

    def test_refuses_a_deploy_not_at_the_pin_or_a_B_the_tables_do_not_write_under(self):
        for stage in ("inputs", "periods"):
            self.gate_ok(stage)   # so that only the pin can refuse
            r = self.submit(f"5b-{stage}", str(self.D), "0" * 40, str(self.B))
            self.assertEqual(r.returncode, 2)
            self.assertIn("is not at", r.stderr)
            self.assertFalse((self.tmp / "sbatch.args").exists())
        other = self.tmp / "other"
        r = self.submit("5b-inputs", str(self.D), self.pin, str(other))
        self.assertEqual(r.returncode, 2)
        self.assertIn("0 of them writing under", r.stderr)
        self.assertFalse(other.exists())

    def test_periods_only_after_the_control_gate(self):
        (self.B / "control").mkdir(parents=True)
        r = self.submit("5b-periods", str(self.D), self.pin, str(self.B))
        self.assertEqual(r.returncode, 2)
        self.assertIn("the gate did not pass", r.stderr)
        self.assertFalse((self.tmp / "sbatch.args").exists())
        self.gate_ok("periods")
        r = self.submit("5b-periods", str(self.D), self.pin, str(self.B))
        self.assertEqual(r.returncode, 0, r.stderr)
        a = self.args()
        for want in ("--qos=regular", "--constraint=cpu", "--exclusive", "--no-requeue", "--time=01:30:00",
                     "--job-name=fd_ct_5b_periods", "32", "56G", "0", "7", "none", str(self.B / "lanes-periods")):
            self.assertIn(want, a)
        self.assertEqual([x for x in a if x.startswith(("--qos", "--time"))], ["--qos=regular", "--time=01:30:00"])

    def test_periods_refuse_existing_period_unfolds(self):
        self.gate_ok("periods")
        (self.B / "unf/PB").mkdir(parents=True)
        r = self.submit("5b-periods", str(self.D), self.pin, str(self.B))
        self.assertEqual(r.returncode, 2)
        self.assertIn("unf/PB exists", r.stderr)


if __name__ == "__main__":
    unittest.main()
