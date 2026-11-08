"""Controls for the 1B pre-check band diagnosis (state/measurement-paper/5d-community-20261024/
FD-1B-BAND-DIAGNOSIS-DECLARATION.md), each rule in the direction it acts and in the other:

* the items: section 7's 126 (14 pilot, 112 bulk), and the job refuses anything else;
* the factor: f**eps, and f itself at eps = 1; each channel sets the other factor to exactly 1;
* the experiments on the toy world: E at eps 1 is the derivation's own experiment bitwise; B at eps 1 is Part 1's mode
  B bitwise; at CV both are the nominal experiment;
* the job: the seed reaches the estimator and the refinement; every guard fires; an atime move exits 8; every input
  is opened with O_NOATIME;
* section 4.3 reads EQUAL on the toy world, and DIFFER on one planted row in each channel;
* sections 4.2, 4.4 and 4.5 at their edges;
* on a staged synthetic world: Part 1's F_src and kappa reproduced bit for bit (and a tampered record refused); HK's
  SAME COMPARISON and DIFFERENT; the pilot's rebuild controls and walls; the readout end to end, where a planted
  constant mismatch reads CONSTANT, a planted quadratic departure SCALES and a planted seed jitter SEED-SENSITIVE;
  each readout control refuses.

No real data are read: every fixture is synthetic."""
from __future__ import annotations

import contextlib
import io
import json
import math
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

ND = Path(__file__).resolve().parents[1]
sys.path.insert(1, str(ND))
sys.path.insert(1, str(Path(__file__).resolve().parent))

import fd_1b_band_diag as bd  # noqa: E402
import fd_1b_inv as inv  # noqa: E402
import fd_1b_precheck_fd as pfd  # noqa: E402
import fd_1b_toys as toys  # noqa: E402
import s1_assemble as sa  # noqa: E402
import s5n_pseudo  # noqa: E402
from test_fd_1b import digest, fake_unfold  # noqa: E402
import test_fd_1b  # noqa: E402
import test_fd_1b_inv  # noqa: E402
from test_fd_1b_precheck_fd import Staged, ToyCase  # noqa: E402

QUIET = (contextlib.redirect_stdout, contextlib.redirect_stderr)


@contextlib.contextmanager
def quiet():
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        yield


# --------------------------------------------------------------------------------------------------------- the items


class Items(unittest.TestCase):
    def test_section_7s_126_items(self):
        p, b = bd.pilot_items(), bd.bulk_items()
        self.assertEqual((len(p), len(b), len(set(p + b))), (14, 112, 126))
        self.assertEqual(len({bd.product_name(*it) for it in p + b}), 126)
        self.assertEqual(sum(1 for it in b if it[2] != 42), 64)
        self.assertEqual(sum(1 for it in b if it[3] != 1.0), 32)
        self.assertEqual(sum(1 for it in b if it[4] != "both"), 16)
        self.assertEqual({it[1] for it in b if it[4] != "both"}, set(bd.subject_universes()))
        self.assertEqual(bd.SEEDS, (42, 45, 48, 51, 54))
        self.assertNotIn("estimator_seed", bd.ONE_CODE_KEYS)

    def test_the_departing_cells_are_part_1s(self):
        self.assertEqual(bd.DEPARTING["GEANT_Neutron"], ("R00", "R02", "R08", "R09", "R10", "R11"))
        self.assertEqual(bd.DEPARTING["GEANT_Proton"], ("R01", "R05", "R07", "R08"))


class Factors(unittest.TestCase):
    def test_eps_one_is_the_factor_itself(self):
        f = np.array([0.0, 0.3, 1.0, 1.7])
        self.assertIs(bd.scaled(f, 1.0), f)
        np.testing.assert_array_equal(bd.scaled(f, 0.5), np.power(f, 0.5))
        np.testing.assert_array_equal(bd.scaled(f, 2.0), np.power(f, 2.0))

    def test_each_channel_sets_the_other_factor_to_exactly_one(self):
        fs_, fb = np.array([0.5, 2.0]), np.array([3.0, 0.25, 1.5])
        a, b = bd.channel_factors(fs_, fb, "signal")
        self.assertIs(a, fs_)
        np.testing.assert_array_equal(b, np.ones(3))
        a, b = bd.channel_factors(fs_, fb, "background")
        np.testing.assert_array_equal(a, np.ones(2))
        self.assertIs(b, fb)
        self.assertEqual(bd.channel_factors(fs_, fb, "both"), (fs_, fb))
        with self.assertRaises(ValueError):
            bd.channel_factors(fs_, fb, "neither")


# ---------------------------------------------------------------------------------------------- the toy world


class Experiments(ToyCase):
    def exp(self, mode, u, eps=1.0, ch="both"):
        exp_cv, xt_cv = inv.nominal_experiment(self.inputs, self.bkg)
        fs_, fb, _ = bd.item_factors(u, eps, ch, self.inputs, self.bkg, self.w.bank, self.w.det)
        return bd.experiment(mode, fs_, fb, self.inputs, self.bkg, exp_cv, xt_cv)

    def assert_exp_equal(self, a, b):
        self.assertEqual(sorted(a), sorted(b))
        for k in a:
            if isinstance(a[k], np.ndarray):
                np.testing.assert_array_equal(a[k], b[k], err_msg=k)

    def test_e_at_eps_one_is_the_derivations_experiment(self):
        for u in ("CV", "GEANT_Neutron_0", "GEANT_Proton_1", "MinosEfficiency_1"):
            exp, xt = self.exp("E", u)
            ref, xr, _, _ = toys.experiment("derivation", toys.single_universe(u), None, self.inputs, self.bkg,
                                            "nominal", None, self.w.bank, self.w.det, None)
            self.assert_exp_equal(exp, ref)
            np.testing.assert_array_equal(xt, xr)

    def test_b_at_eps_one_is_part_1s_mode_b(self):
        exp_cv, xt_cv = inv.nominal_experiment(self.inputs, self.bkg)
        for u in ("CV", "GEANT_Neutron_1", "GEANT_Pion_0"):
            ui, ub, _ = pfd.mode_inputs("B", u, self.inputs, self.bkg, self.w.bank, self.w.det, None, None)
            ref, xr = pfd.experiment("B", self.inputs, self.bkg, ui, ub, exp_cv, xt_cv)
            exp, xt = self.exp("B", u)
            self.assert_exp_equal(exp, ref)
            np.testing.assert_array_equal(xt, xr)

    def test_at_cv_both_modes_are_the_nominal_experiment(self):
        ref = fake_unfold(inv.nominal_experiment(self.inputs, self.bkg)[0], 42, 1, 5)[0]
        for mode in bd.MODES:
            np.testing.assert_array_equal(fake_unfold(self.exp(mode, "CV")[0], 42, 1, 5)[0], ref, err_msg=mode)

    def test_eps_scales_both_factors(self):
        for u in ("GEANT_Neutron_0", "MinosEfficiency_1"):
            fs_, fb, _ = pfd.toy_factors(u, self.inputs, self.bkg, self.w.bank, self.w.det)
            for eps in (0.5, 2.0):
                a, b, _ = bd.item_factors(u, eps, "both", self.inputs, self.bkg, self.w.bank, self.w.det)
                np.testing.assert_array_equal(a, np.power(fs_, eps))
                np.testing.assert_array_equal(b, np.power(fb, eps))
            a, b, _ = bd.item_factors(u, 1.0, "both", self.inputs, self.bkg, self.w.bank, self.w.det)
            np.testing.assert_array_equal(a, fs_)
            np.testing.assert_array_equal(b, fb)

    def test_eps_and_channel_reach_the_experiment(self):
        base = fake_unfold(self.exp("E", "GEANT_Neutron_0")[0], 42, 1, 5)[0]
        for eps, ch in ((2.0, "both"), (0.5, "both"), (1.0, "signal"), (1.0, "background")):
            x = fake_unfold(self.exp("E", "GEANT_Neutron_0", eps, ch)[0], 42, 1, 5)[0]
            self.assertFalse(np.array_equal(x, base), msg=(eps, ch))
        # signal only leaves the background as the CV's; background only leaves the signal reco weights as the CV's
        ui = self.exp("B", "GEANT_Neutron_0", 1.0, "signal")[0]
        np.testing.assert_array_equal(ui["tmpl_w"], self.exp("B", "CV")[0]["tmpl_w"])
        ub = self.exp("B", "GEANT_Neutron_0", 1.0, "background")[0]
        np.testing.assert_array_equal(ub["w_reco"], self.exp("B", "CV")[0]["w_reco"])


class Inputs(ToyCase):
    def check(self, u):
        exp_cv, xt_cv = inv.nominal_experiment(self.inputs, self.bkg)
        return bd.input_check(u, self.inputs, self.bkg, self.w.bank, self.w.det, exp_cv, xt_cv)

    def test_the_toy_world_reads_equal(self):
        for u in bd.detector_universes():
            r = self.check(u)
            self.assertTrue(r["signal"]["equal"] and r["background"]["equal"], msg=u)
            self.assertGreater(r["signal"]["n_rows"], 0)
            self.assertGreater(r["background"]["n_rows"], 0)
            self.assertIn("out_of_window_share", r["HW"])

    def planted(self, segment):
        real = toys.build_full

        def build(inputs, bkg, r, fs_, fb, seed, expectation):
            exp, xt, info = real(inputs, bkg, r, fs_, fb, seed, expectation)
            cnt = np.asarray(exp["obs_counts"], float).copy()
            cnt[0 if segment == "signal" else -1] *= 1.0 + 1e-12
            exp["obs_counts"] = cnt
            return exp, xt, info
        return mock.patch.object(toys, "build_full", build)

    def test_one_planted_row_reads_differ_in_each_channel(self):
        for seg in ("signal", "background"):
            with self.planted(seg):
                r = self.check("GEANT_Proton_0")
            other = "background" if seg == "signal" else "signal"
            self.assertFalse(r[seg]["equal"], msg=seg)
            self.assertEqual(r[seg]["n_differ"], 1)
            self.assertTrue(r[other]["equal"], msg=seg)

    def test_the_inputs_step_returns_differ_and_rc_1(self):
        argv = ["inputs", "--npz", str(self.w.inputs), "--bkg", str(self.w.bkg), "--bank", str(self.w.bank),
                "--detector-dir", str(self.w.det), "--pins", str(self.w.pins), "--expect-pins-sha256",
                digest(self.w.pins)]
        with quiet():
            self.assertEqual(bd.main(argv + ["--out", str(self.tmp / "in-ok.json")]), 0)
            with self.planted("signal"):
                self.assertEqual(bd.main(argv + ["--out", str(self.tmp / "in-bad.json")]), 1)
            with self.planted("background"):
                self.assertEqual(bd.main(argv + ["--out", str(self.tmp / "in-bad-b.json")]), 1)
        self.assertEqual(json.loads((self.tmp / "in-ok.json").read_text())["verdict"], "EQUAL")
        self.assertEqual(json.loads((self.tmp / "in-bad.json").read_text())["verdict"], "DIFFER")


class Jobs(ToyCase):
    def argv(self, mode, universes, out, seed=42, eps="1", ch="both"):
        return ["unfold", "--mode", mode, "--seed", str(seed), "--eps", eps, "--channel", ch, "--universes", universes,
                "--npz", str(self.w.inputs), "--bkg", str(self.w.bkg), "--bank", str(self.w.bank), "--detector-dir",
                str(self.w.det), "--pins", str(self.w.pins), "--expect-pins-sha256", digest(self.w.pins),
                "--threads", "1", "--out", str(out)]

    def run_job(self, *a, unfold=fake_unfold, **k):
        with mock.patch.object(s5n_pseudo, "unfold_negweight", unfold), quiet():
            return bd.main(self.argv(*a, **k))

    def test_products_record_their_item_and_the_seed_reaches_the_estimator(self):
        out = self.tmp / "unf-ok"
        test_fd_1b.CALLS.clear()
        self.assertEqual(self.run_job("B", "GEANT_Pion_1", out, seed=48), 0)
        self.assertEqual(test_fd_1b.CALLS[-1]["args"][0], 48)
        m = json.loads(str(np.load(out / bd.product_name("B", "GEANT_Pion_1", 48, 1.0, "both"))["meta"]))
        self.assertEqual((m["mode"], m["universe"], m["estimator_seed"], m["eps"], m["channel"]),
                         ("B", "GEANT_Pion_1", 48, 1.0, "both"))
        self.assertEqual(bd.check_estimator(m, 48), [])
        self.assertNotEqual(bd.check_estimator(m, 42), [])
        self.assertEqual(self.run_job("E", "GEANT_Proton_0", out, eps="2"), 0)
        self.assertEqual(self.run_job("E", "GEANT_Proton_0", out, ch="background"), 0)

    def test_anything_outside_section_7_refuses(self):
        for args in (("B", "GEANT_Pion_1", 42, "1", "signal"),     # channels are for the subjects only
                     ("E", "GEANT_Neutron_0", 45, "2", "both"),    # a seed and a scale together
                     ("B", "Flux_0", 42, "1", "both"),             # not a detector universe
                     ("E", "CV", 48, "1", "both")):                 # CV is a pilot control only
            out = self.tmp / f"unf-r-{'-'.join(map(str, args))}"
            self.assertEqual(self.run_job(args[0], args[1], out, seed=args[2], eps=args[3], ch=args[4]), 4, msg=args)
            self.assertFalse(out.exists() and any(out.glob("*.npz")), msg=args)

    def test_the_guards_fire(self):
        with mock.patch.object(sa, "INPUT_NPZ_SHA256", "0" * 64):
            self.assertEqual(self.run_job("B", "CV", self.tmp / "g-npz"), 4)
        with mock.patch.object(sa, "BKG_SHA256", "0" * 64):
            self.assertEqual(self.run_job("B", "CV", self.tmp / "g-bkg"), 4)
        argv = self.argv("B", "CV", self.tmp / "g-pins")
        argv[argv.index("--expect-pins-sha256") + 1] = "0" * 64
        with mock.patch.object(s5n_pseudo, "unfold_negweight", fake_unfold), quiet():
            self.assertEqual(bd.main(argv), 4)
        pins = json.loads(self.w.pins.read_text())
        pins["files"][str(self.w.det / "GEANT_Proton_1_wr.npy")]["sha256"] = "0" * 64
        bad = self.tmp / "pins-bad.json"
        bad.write_text(json.dumps(pins))
        argv = self.argv("E", "GEANT_Proton_1", self.tmp / "g-w")
        argv[argv.index("--pins") + 1] = str(bad)
        argv[argv.index("--expect-pins-sha256") + 1] = digest(bad)
        with mock.patch.object(s5n_pseudo, "unfold_negweight", fake_unfold), quiet():
            self.assertEqual(bd.main(argv), 4)

        def nan_unfold(exp, *a, **k):
            x, ev = fake_unfold(exp, *a, **k)
            x = np.asarray(x, float).copy()
            x.flat[0] = np.nan
            return x, ev
        self.assertEqual(self.run_job("E", "GEANT_Neutron_1", self.tmp / "g-nan", unfold=nan_unfold), 4)
        for d in ("g-npz", "g-bkg", "g-pins", "g-w", "g-nan"):
            self.assertFalse((self.tmp / d).exists() and any((self.tmp / d).glob("*.npz")), msg=d)

    def test_a_negative_factor_refuses(self):
        real = bd.item_factors

        def neg(*a, **k):
            fs_, fb, rec = real(*a, **k)
            fs_ = fs_.copy()
            fs_[0] = -1.0
            return fs_, fb, rec
        with mock.patch.object(bd, "item_factors", neg):
            self.assertEqual(self.run_job("B", "GEANT_Neutron_0", self.tmp / "g-neg"), 4)

    def test_a_product_unfolded_with_another_flux_refuses(self):
        real = bd.experiment

        def other(*a, **k):
            exp, xt = real(*a, **k)
            return dict(exp, flux=np.asarray(exp["flux"], float) * 1.1), xt
        with mock.patch.object(bd, "experiment", other):
            self.assertEqual(self.run_job("E", "GEANT_Neutron_0", self.tmp / "g-flux"), 4)
        self.assertFalse(any((self.tmp / "g-flux").glob("*.npz")))

    def test_a_moved_atime_exits_8(self):
        out = self.tmp / "unf-atime"

        def touching(exp, *a, **k):
            st = os.stat(self.w.inputs)
            os.utime(self.w.inputs, ns=(st.st_atime_ns + 10 ** 9, st.st_mtime_ns))
            return fake_unfold(exp, *a, **k)
        self.assertEqual(self.run_job("B", "CV", out, unfold=touching), 8)
        self.assertEqual(json.loads(next(out.glob("atime-*.json")).read_text())["moved"], [str(self.w.inputs)])


class CallGraph(ToyCase):
    SENTINEL = test_fd_1b_inv.CallGraph.SENTINEL
    instrument = test_fd_1b_inv.CallGraph.instrument

    def test_the_job_and_the_inputs_step_open_every_input_with_o_noatime(self):
        out = self.tmp / "cg"
        pins_sha = digest(self.w.pins)
        for p in reversed(self.ps):
            p.stop()
        rec, ps = self.instrument()
        for p in self.w.patches() + ps:
            p.start()
        try:
            with mock.patch.object(s5n_pseudo, "unfold_negweight", fake_unfold), quiet():
                common = ["--npz", str(self.w.inputs), "--bkg", str(self.w.bkg), "--bank", str(self.w.bank),
                          "--detector-dir", str(self.w.det), "--pins", str(self.w.pins), "--expect-pins-sha256",
                          pins_sha]
                for mode, seed, eps, us in (("E", "42", "1", "CV,GEANT_Neutron_0"), ("B", "51", "1", "GEANT_Pion_1"),
                                            ("E", "42", "0.5", "MinosEfficiency_0")):
                    self.assertEqual(bd.main(["unfold", "--mode", mode, "--seed", seed, "--eps", eps, "--channel",
                                              "both", "--universes", us, "--threads", "1", "--out", str(out)]
                                             + common), 0)
                self.assertEqual(bd.main(["inputs", "--out", str(self.tmp / "cg-inputs.json")] + common), 0)
        finally:
            mock.patch.stopall()
            for p in self.ps:
                p.start()
        ins = {str(p) for p in [self.w.inputs, self.w.bkg, self.w.pins, *self.w.bank.iterdir(), *self.w.det.iterdir()]}
        opened = {p for p, _ in rec["os"] if p in ins}
        for must in (self.w.inputs, self.w.bkg, self.w.pins, self.w.det / "GEANT_Neutron_0_wr.npy",
                     self.w.det / "GEANT_Proton_1_bkgw.npy", self.w.det / "MinosEfficiency_0_wr.npy"):
            self.assertIn(str(must), opened)
        self.assertEqual([p for p in rec["plain"] if p in ins], [])
        self.assertEqual([p for p, flag in rec["os"] if p in ins and not flag], [])


# ------------------------------------------------------------------------------------------------------- the rules


class Rules(unittest.TestCase):
    def test_hk_thresholds(self):
        g = np.full(16, 2.0)
        E = np.full(16, 4.0)
        D = E / g ** 2
        A = np.full(16, 3.0)
        r = bd.hk_reading(E, A, A, D, g, list(range(16)))
        self.assertEqual(r["verdict"], "SAME COMPARISON")
        D2 = D.copy()
        D2[3] *= math.exp(2e-12)
        self.assertEqual(bd.hk_reading(E, A, A, D2, g, list(range(16)))["cells_outside"], ["R03"])
        self.assertEqual(bd.hk_reading(E, A, A, D2, g, [0, 1])["verdict"], "SAME COMPARISON")   # R03 unresolved
        B = A.copy()
        B[5] *= math.exp(0.9e-5)
        self.assertEqual(bd.hk_reading(E, B, A, D, g, list(range(16)))["verdict"], "SAME COMPARISON")
        B[5] = A[5] * math.exp(1.1e-5)
        self.assertEqual(bd.hk_reading(E, B, A, D, g, list(range(16)))["cells_outside"], ["R05"])

    @staticmethod
    def seeds(values, resolved=None):
        F = {s: np.array([v]) for s, v in zip(bd.SEEDS, values)}
        R = {s: np.array([True if resolved is None else resolved[i]]) for i, s in enumerate(bd.SEEDS)}
        return F, R

    def test_seed_reading(self):
        self.assertEqual(bd.seed_reading(*self.seeds([1.2, 1.15, 1.3, 1.11, 1.4]), 0), "SEED-STABLE")
        self.assertEqual(bd.seed_reading(*self.seeds([0.8, 0.85, 0.7, 0.89, 0.6]), 0), "SEED-STABLE")
        self.assertEqual(bd.seed_reading(*self.seeds([1.2, 1.15, 1.09, 1.11, 1.4]), 0), "SEED-SENSITIVE")  # inside
        self.assertEqual(bd.seed_reading(*self.seeds([1.2, 1.15, 0.8, 1.11, 1.4]), 0), "SEED-SENSITIVE")   # crosses 1
        self.assertEqual(bd.seed_reading(*self.seeds([1.2, 1.15, 1.3, 1.11, 1.4],
                                                     [True, True, False, True, True]), 0), "SEED-SENSITIVE")
        self.assertEqual(bd.seed_reading(*self.seeds([1.2, 1.15, float("nan"), 1.11, 1.4]), 0), "SEED-SENSITIVE")
        # the window's edges are inside it
        self.assertEqual(bd.seed_reading(*self.seeds([1.2, 1.15, 1.1, 1.11, 1.4]), 0), "SEED-SENSITIVE")
        self.assertEqual(bd.seed_reading(*self.seeds([0.8, 0.85, 0.9, 0.89, 0.6]), 0), "SEED-SENSITIVE")

    @staticmethod
    def scale(f_half, f1, f2, res=(True, True, True)):
        F = {0.5: np.array([f_half]), 1.0: np.array([f1]), 2.0: np.array([f2])}
        R = {e: np.array([r]) for e, r in zip(bd.EPS, res)}
        sl = bd.slopes(F, R, 0)
        return sl, bd.scale_reading(sl)

    def test_scale_reading_edges(self):
        L = math.log(1.2)
        f = lambda p_up, p_down: (math.exp(L / 2 ** p_down), 1.2, math.exp(L * 2 ** p_up))  # noqa: E731
        self.assertEqual(self.scale(*f(1.0, 1.0))[1], "SCALES")
        self.assertEqual(self.scale(*f(0.5 + 1e-9, 0.5 + 1e-9))[1], "SCALES")   # the edges, to rounding
        self.assertEqual(self.scale(*f(0.5 - 1e-6, 1.0))[1], "MIXED")
        self.assertEqual(self.scale(*f(1.0, 0.5 - 1e-6))[1], "MIXED")
        self.assertEqual(self.scale(*f(0.0, 0.0))[1], "CONSTANT")
        self.assertEqual(self.scale(*f(0.25 - 1e-9, -0.25 + 1e-9))[1], "CONSTANT")
        self.assertEqual(self.scale(*f(0.25 + 1e-6, 0.0))[1], "MIXED")
        self.assertEqual(self.scale(*f(0.0, -0.25 - 1e-6))[1], "MIXED")
        # the departure crosses 1 at eps 1/2 (p_down = +inf) or at eps 2 (p_up = -inf)
        sl, r = self.scale(0.98, 1.2, 1.44)
        self.assertEqual((sl["p_down"], r), (math.inf, "SCALES"))
        sl, r = self.scale(1.1, 1.2, 0.9)
        self.assertEqual((sl["p_up"], r), (-math.inf, "MIXED"))
        # unresolved eps 1/2: p_up alone; unresolved eps 2: not read
        sl, r = self.scale(1.2, 1.2, 1.44, res=(False, True, True))
        self.assertEqual((sl["p_down"], r), (None, "SCALES"))
        self.assertEqual(self.scale(1.1, 1.2, 1.44, res=(True, True, False))[1], "NOT READ")
        # a departure below 1 reads on its own side
        self.assertEqual(self.scale(1 / math.exp(L / 2), 1 / 1.2, 1 / 1.44)[1], "SCALES")

    def test_band_scale(self):
        self.assertEqual(bd.band_scale({"R00": "SCALES", "R01": "NOT READ"}), "SCALES")
        self.assertEqual(bd.band_scale({"R00": "CONSTANT", "R01": "CONSTANT"}), "CONSTANT")
        self.assertEqual(bd.band_scale({"R00": "SCALES", "R01": "CONSTANT"}), "MIXED")
        self.assertEqual(bd.band_scale({"R00": "NOT READ"}), "NOT READ")


# -------------------------------------------------------------------------------------------- the staged world


class World:
    """Part 1's staged synthetic world (``Staged``, with GEANT_Neutron and GEANT_Proton departing at F_src = src)
    plus its staged.json, Part 1's readout as a committed file, and the 126 new products. Each new product's shift is
    the band's Part 1 B shift times ``F(mode, band, seed, eps, ch)`` for E and 1 for B, so F_src = F."""

    def __init__(self, tmp: Path, src=1.2, F=None, kap=None, side=None, sigma=1e-7):
        self.tmp = tmp
        self.st = Staged(tmp, src={b: src for b in bd.SUBJECTS}, side=side, sigma=sigma)
        root = self.st.root
        # Dnom as the weight-only detector bands make it at r = 1 (section 3, HK): the universe's own truth plus E's
        # shift, so g^2 Dnom = E up to rounding whatever F_src is; kap[b] scales it
        rng = np.random.default_rng(17)
        for u in bd.detector_universes():
            b = u.rpartition("_")[0]
            t_u = self.st.x_t * (1 + rng.normal(0, 0.05, 16))
            d = self.st.xD[u] - self.st.x_cv
            self.st.save("Dnom", u, t_u + (kap or {}).get(b, 1.0) * d, t_u, self.st.cv_flux)
        recs = [{"role": "derivation", "dest": f"derivation/{p.name}", "sha256": digest(p)}
                for p in sorted((root / "derivation").iterdir())]
        recs.append({"role": "s1", "dest": "s1/s1_assembly.npz", "sha256": digest(self.st.s1)})
        recs.append({"role": "flux-file", "sha256": self.st.flux_sha})
        (root / "staged.json").write_text(json.dumps({"staged": recs, "missing": []}))
        with self.st.patched():
            ro = pfd.readout(root, self.st.unf, self.st.gate_d, self.st.diag, self.st.i0, self.st.definition)
        self.readout = tmp / "readout.json"
        self.readout.write_text(json.dumps(ro))
        self.part1 = ro
        self.unf = tmp / "unf-bdg"
        self.unf.mkdir()
        self.F = F or (lambda b, seed, eps, ch: 1.0)
        self.write_new()

    def meta(self, mode, u, seed, eps, ch, **extra):
        m = {"schema": bd.SCHEMA, "mode": mode, "universe": u, "estimator_seed": seed, "eps": eps, "channel": ch,
             "config": "R", "capacity": None, "iters": 5,
             "estimator_params": [{"n_estimators": 100, "num_leaves": 8, "random_state": seed}] * 3,
             "refinement": {"classifier_params": {"n_estimators": 400, "num_leaves": 31, "random_state": seed + 3}},
             "code_sha256": {"x": "c" * 64}, "input_npz_sha256": "i" * 64, "bkg_dump_sha256": "b" * 64,
             "pins_sha256": "p" * 64, "seconds_unfold": 700.0, "peak_rss_kib": 2 * 10 ** 7}
        m.update(extra)
        return m

    def save(self, it, x, **extra):
        mode, u, seed, eps, ch = it
        np.savez(self.unf / bd.product_name(*it), xsec_flat=x, xtrue_flat=self.st.x_t,
                 meta=json.dumps(self.meta(*it, **extra)))

    def write_new(self):
        st = self.st
        for it in bd.items():
            mode, u, seed, eps, ch = it
            if (seed, eps, ch) == (42, 1.0, "both"):        # the pilot's rebuilds: the committed products exactly
                if mode == "E":
                    x = np.load(st.root / "derivation" / f"{inv.DER_TAG}_{u}.npz")["xsec_flat"]
                else:
                    x = np.load(st.unf / f"{pfd.TAG}_B_{u}.npz")["xsec_flat"]
                self.save(it, x)
                continue
            b = u.rpartition("_")[0]
            dB = np.load(st.unf / f"{pfd.TAG}_B_{u}.npz")["xsec_flat"] - st.x_cv
            self.save(it, st.x_cv + (self.F(b, seed, eps, ch) * dB if mode == "E" else dB))

    @contextlib.contextmanager
    def patched(self):
        with self.st.patched(gate=False):
            yield

    def same(self):
        with self.patched():
            return bd.same(self.st.root, self.st.unf, self.readout)

    def pilot(self):
        with self.patched():
            return bd.pilot(self.unf, self.st.root, self.st.unf)

    def run(self):
        with self.patched():
            return bd.readout(self.st.root, self.st.unf, self.unf, self.st.i0, self.readout)


class StagedCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="fd1b-bdg-"))

    def tearDown(self):
        shutil.rmtree(self.tmp)


class Same(StagedCase):
    def test_part_1_is_reproduced_and_hk_reads_same(self):
        w = World(self.tmp)
        self.assertEqual(w.part1["bands"]["GEANT_Neutron"]["rule_S"]["verdict"], "DEPARTS")
        r = w.same()
        for b in bd.DETECTOR:
            self.assertEqual(r["bands"][b]["HK"]["verdict"], "SAME COMPARISON", msg=b)
        self.assertTrue(r["reproduced"]["F_src_kappa_bitwise"])

    def test_g_is_f_over_the_mapped_truth(self):
        import test_fd_1b_precheck_fd as t1
        U2 = np.diag(np.linspace(1.5, 2.5, 16))
        with mock.patch.object(t1, "U64", U2):
            w = World(self.tmp)
            with w.patched():
                digests = bd.staged_digests(w.st.root)
                s1 = bd.load_s1(w.st.root, digests, {})
                d = bd.derivation(w.st.root, digests, {}, s1)
        U = U2.astype(np.float32).astype(float)
        np.testing.assert_array_equal(d["g"], w.st.f / (U @ w.st.x_t))
        self.assertFalse(np.allclose(d["g"], w.st.f / w.st.x_t))

    def test_kappa_off_reads_different(self):
        r = World(self.tmp, kap={"GEANT_Proton": 1.2}).same()
        self.assertEqual(r["bands"]["GEANT_Proton"]["HK"]["verdict"], "DIFFERENT")
        self.assertEqual(r["bands"]["GEANT_Neutron"]["HK"]["verdict"], "SAME COMPARISON")

    def test_b_against_a_reads_different(self):
        r = World(self.tmp, side={"GEANT_Pion": 1 + 1e-5}).same()
        self.assertEqual(r["bands"]["GEANT_Pion"]["HK"]["verdict"], "DIFFERENT")

    def test_a_tampered_part_1_record_refuses(self):
        w = World(self.tmp)
        ro = json.loads(w.readout.read_text())
        ro["bands"]["GEANT_Pion"]["factors"]["F_src"][4] *= 1 + 1e-15
        w.readout.write_text(json.dumps(ro))
        with self.assertRaisesRegex(bd.Invalid, "not reproduced bit for bit"):
            w.same()

    def test_a_tampered_part_1_kappa_refuses(self):
        w = World(self.tmp)
        ro = json.loads(w.readout.read_text())
        ro["bands"]["GEANT_Proton"]["factors"]["kappa"][2] *= 1 + 1e-15
        w.readout.write_text(json.dumps(ro))
        with self.assertRaisesRegex(bd.Invalid, "not reproduced bit for bit"):
            w.same()

    def test_the_s1_digest_is_checked(self):
        w = World(self.tmp)
        with w.patched(), mock.patch.object(bd.fs, "S1_NPZ_SHA256", "0" * 64):
            with self.assertRaisesRegex(bd.Invalid, "not S1's"):
                bd.same(w.st.root, w.st.unf, w.readout)

    def test_a_derivation_product_of_another_draw_refuses(self):
        w = World(self.tmp)
        p = w.st.root / "derivation" / f"{inv.DER_TAG}_GEANT_Pion_1.npz"
        z = dict(np.load(p))
        m = json.loads(str(z["meta"]))
        m["draw"] = json.loads(json.dumps(toys.single_universe("GEANT_Pion_0")))
        z["meta"] = json.dumps(m)
        np.savez_compressed(p, **z)
        rec = json.loads((w.st.root / "staged.json").read_text())
        next(r for r in rec["staged"] if r.get("dest") == f"derivation/{p.name}")["sha256"] = digest(p)
        (w.st.root / "staged.json").write_text(json.dumps(rec))
        with self.assertRaisesRegex(bd.Invalid, "alone"):
            w.same()

    def test_a_part_1_product_of_another_universe_refuses(self):
        w = World(self.tmp)
        shutil.copy(w.st.unf / f"{pfd.TAG}_B_GEANT_Pion_0.npz", w.st.unf / f"{pfd.TAG}_B_GEANT_Pion_1.npz")
        with self.assertRaisesRegex(bd.Invalid, "not Part 1's mode B"):
            w.same()

    def test_a_staged_copy_off_its_digest_refuses(self):
        w = World(self.tmp)
        rec = json.loads((w.st.root / "staged.json").read_text())
        cv = next(r for r in rec["staged"] if r.get("dest") == f"derivation/{inv.DER_TAG}_CV.npz")
        cv["sha256"] = "0" * 64
        (w.st.root / "staged.json").write_text(json.dumps(rec))
        with self.assertRaisesRegex(bd.Invalid, "is not the staged"):
            w.same()

    def test_a_part_1_cv_product_off_the_derivation_refuses(self):
        w = World(self.tmp)
        p = w.st.unf / f"{pfd.TAG}_Dnom_CV.npz"
        z = dict(np.load(p))
        z["xsec_flat"] = z["xsec_flat"] * (1 + 1e-15)
        np.savez(p, **z)
        with self.assertRaisesRegex(bd.Invalid, "at CV"):
            w.same()


class Pilot(StagedCase):
    def test_the_rebuilds_pass(self):
        r = World(self.tmp).pilot()
        self.assertEqual((r["verdict"], r["rebuild_not_bitwise"]), ("PASS", []))

    def test_a_rebuild_off_by_one_ulp_is_invalid(self):
        w = World(self.tmp)
        it = ("E", "GEANT_Neutron_1", 42, 1.0, "both")
        x = np.load(w.unf / bd.product_name(*it))["xsec_flat"]
        w.save(it, np.nextafter(x, np.inf))
        r = w.pilot()
        self.assertEqual((r["verdict"], r["rebuild_not_bitwise"]), ("INVALID", ["E_GEANT_Neutron_1"]))

    def test_the_walls(self):
        w = World(self.tmp)
        it = ("B", "CV", 42, 1.0, "both")
        x = np.load(w.unf / bd.product_name(*it))["xsec_flat"]
        w.save(it, x, seconds_unfold=bd.UNIT_SECONDS)
        self.assertEqual(w.pilot()["verdict"], "PASS")
        w.save(it, x, seconds_unfold=bd.UNIT_SECONDS + 0.001)
        self.assertEqual(w.pilot()["verdict"], "REPRICE")
        w.save(it, x, peak_rss_kib=bd.RSS_LIMIT_KIB + 1)
        self.assertEqual(w.pilot()["verdict"], "REPRICE")

    def test_a_missing_or_foreign_pilot_product_refuses(self):
        w = World(self.tmp)
        it = ("E", "GEANT_Pion_0", 42, 1.0, "both")
        x = np.load(w.unf / bd.product_name(*it))["xsec_flat"]
        w.save(it, x, estimator_seed=45)
        with self.assertRaisesRegex(bd.Invalid, "not pilot item"):
            w.pilot()
        (w.unf / bd.product_name(*it)).unlink()
        with self.assertRaisesRegex(bd.Refusal, "missing"):
            w.pilot()


class Readout(StagedCase):
    L = math.log(1.2)

    def test_a_planted_quadratic_departure_scales(self):
        r = World(self.tmp, F=lambda b, s, e, c: math.exp(self.L * e ** 2) if b in bd.SUBJECTS else 1.0).run()
        for b in bd.SUBJECTS:
            rb = r["bands"][b]
            self.assertEqual(rb["scale_band"], "SCALES", msg=b)
            for cell, v in rb["departing"].items():
                self.assertEqual(v["seed"], "SEED-STABLE")
                self.assertAlmostEqual(v["p_up"], 2.0, places=6)
                self.assertAlmostEqual(v["p_down"], 2.0, places=6)
        self.assertNotIn("departing", r["bands"]["GEANT_Pion"])

    def test_a_planted_constant_mismatch_reads_constant(self):
        r = World(self.tmp, F=lambda b, s, e, c: 1.2 if b in bd.SUBJECTS else 1.0).run()
        for b in bd.SUBJECTS:
            self.assertEqual(r["bands"][b]["scale_band"], "CONSTANT", msg=b)
            np.testing.assert_allclose(r["bands"][b]["eps_values"]["e200"], 1.2, rtol=1e-9)

    def test_a_planted_seed_jitter_reads_seed_sensitive(self):
        def F(b, s, e, c):
            if b == "GEANT_Proton" and s == 51:
                return 1.05
            return 1.2 if b in bd.SUBJECTS else 1.0
        r = World(self.tmp, F=F).run()
        pr = r["bands"]["GEANT_Proton"]
        self.assertTrue(all(v == {"seed": "SEED-SENSITIVE", "scale": "NOT READ"} for v in pr["departing"].values()))
        self.assertEqual(pr["scale_band"], "NOT READ")
        self.assertEqual(r["bands"]["GEANT_Neutron"]["scale_band"], "CONSTANT")
        np.testing.assert_allclose(pr["seed_values"]["s51"], 1.05, rtol=1e-9)

    def test_the_channels_are_reported(self):
        r = World(self.tmp, F=lambda b, s, e, c: {"signal": 1.3, "background": 1.0}.get(c, 1.2)).run()
        ch = r["bands"]["GEANT_Neutron"]["channels"]
        np.testing.assert_allclose(ch["signal"]["F_src"], 1.3, rtol=1e-9)
        np.testing.assert_allclose(ch["background"]["F_src"], 1.0, rtol=1e-9)
        self.assertEqual(len(ch["signal"]["resolved"]), 16)

    def test_seed_42_is_part_1s(self):
        r = World(self.tmp).run()
        np.testing.assert_array_equal(r["bands"]["GEANT_Neutron"]["seed_values"]["s42"],
                                      json.loads((self.tmp / "readout.json").read_text())
                                      ["bands"]["GEANT_Neutron"]["factors"]["F_src"])

    def test_the_readout_controls_refuse(self):
        w = World(self.tmp)
        it = ("B", "GEANT_Pion_1", 48, 1.0, "both")
        x = np.load(w.unf / bd.product_name(*it))["xsec_flat"]
        w.save(it, x, code_sha256={"x": "d" * 64})
        with self.assertRaisesRegex(bd.Invalid, "one code and one input set"):
            w.run()
        w.save(it, x, estimator_params=[{"n_estimators": 100, "num_leaves": 8, "random_state": 42}] * 3)
        with self.assertRaisesRegex(bd.Invalid, "not item"):
            w.run()
        w.save(it, x, channel="signal")
        with self.assertRaisesRegex(bd.Invalid, "not item"):
            w.run()
        (w.unf / bd.product_name(*it)).unlink()
        with self.assertRaisesRegex(bd.Invalid, "missing"):
            w.run()

    def test_a_tampered_part_1_resolution_refuses(self):
        w = World(self.tmp)
        ro = json.loads(w.readout.read_text())
        ro["bands"]["GEANT_Neutron"]["resolved"]["F_src"] = ro["bands"]["GEANT_Neutron"]["resolved"]["F_src"][1:]
        w.readout.write_text(json.dumps(ro))
        with self.assertRaisesRegex(bd.Invalid, "seed 42"):
            w.run()

    def test_a_tampered_part_1_f_src_refuses(self):
        w = World(self.tmp)
        ro = json.loads(w.readout.read_text())
        ro["bands"]["MinosEfficiency"]["factors"]["F_src"][7] *= 1 + 1e-15
        w.readout.write_text(json.dumps(ro))
        with self.assertRaisesRegex(bd.Invalid, "seed 42"):
            w.run()

    def test_unresolved_cells_are_not_read(self):
        # every block under its floor: nothing is resolved, so no departing cell is seed-stable
        r = World(self.tmp, sigma=1.0, F=lambda b, s, e, c: 1.2 if b in bd.SUBJECTS else 1.0).run()
        for b in bd.SUBJECTS:
            self.assertEqual(r["bands"][b]["scale_band"], "NOT READ", msg=b)
            self.assertEqual(r["bands"][b]["seed_resolved"]["s45"], [])
            self.assertTrue(all(v["seed"] == "SEED-SENSITIVE" for v in r["bands"][b]["departing"].values()))

    def test_i0s_floor_kind_is_checked(self):
        w = World(self.tmp)
        z = json.loads(w.st.i0.read_text())
        z["floor"]["kind"] = "point"
        w.st.i0.write_text(json.dumps(z))
        with self.assertRaisesRegex(bd.Invalid, "measured"):
            w.run()

    def test_a_product_read_twice_must_keep_its_digest(self):
        w = World(self.tmp)
        seen = {}
        p = w.unf / bd.product_name("B", "GEANT_Pion_1", 48, 1.0, "both")
        with w.patched():
            bd.load_checked(p, None, seen)
            z = dict(np.load(p))
            z["xsec_flat"] = z["xsec_flat"] + 1.0
            np.savez(p.with_suffix(""), **z)
            with self.assertRaisesRegex(bd.Invalid, "changed since"):
                bd.load_checked(p, None, seen)


if __name__ == "__main__":
    unittest.main()
