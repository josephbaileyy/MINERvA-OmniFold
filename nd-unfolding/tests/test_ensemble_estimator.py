"""Tests of ENS1 (ENS1-DECLARATION.md §2, §4, §5, §8, §9): the internal jitter and its scale, the three float32 traps,
every refusal in the direction it acts and the other, the analysis's gates and verdicts, and the job script.

Run: python3 -B nd-unfolding/tests/test_ensemble_estimator.py (no LightGBM, no ROOT). The fits use RS1's histogram
stand-in (tests/test_rounding_mechanism.py ``Hist``): a row reaches a fit only through bins over the sorted distinct
values, so a sub-float32 move of tied values changes the fit. That is the "sensitive fixture" of §2.2.
"""
import contextlib
import io
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

ND = Path(__file__).resolve().parents[1]
REPO = ND.parent
sys.path.insert(1, str(ND))
sys.path.insert(1, str(ND / "tests"))
import ensemble_estimator_analyze as eea  # noqa: E402
import ensemble_estimator_probe as eep  # noqa: E402
import estimator_stability_analyze as esa  # noqa: E402
import estimator_stability_probe as esp  # noqa: E402
import s5e_trace  # noqa: E402
import s5n_pseudo  # noqa: E402
import s5p_numerics  # noqa: E402
import test_rounding_mechanism as trm  # noqa: E402  (RS1's stand-ins and fixture)


def run_stability(d, shas, k, s, mode="stability", **over):
    rest = trm.runner_args(d, shas, f"-:{s}", "x", **over)
    err = io.StringIO()
    with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
        try:
            rc = eep.run(mode, [k], None, rest, d / "runs")
        except SystemExit as exc:
            rc = exc.code
    return rc, err.getvalue()


def stab_product(d, k, s):
    return esa.load(d / "runs" / "stability" / f"ens1_k{k:03d}_b-_j{s}.npz")


# ------------------------------------------------------------------------------------------ the internal jitter
class InternalJitter(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(5)
        self.x = trm.lattice(rng, 4000)
        self.inputs = {"MCgen": self.x, "MCreco": self.x[::-1].copy(), "measured": self.x[:500].copy(),
                       "edges": trm.EDGES}
        self.bkg = {"bkg_reco": self.x[:300].copy()}

    def test_the_scale_is_plus_or_minus_half_the_float32_spacing_in_both_directions(self):
        """ENS-2: every |delta| / spacing32 <= 1/2, and the maximum exceeds 0.49 (a +-1/4 scale fails the second)."""
        ji, _, _ = eep.internal_jitter(self.inputs, self.bkg, 7)
        y = np.asarray(self.x, np.float64)
        step = ji["MCgen"] - y
        sp = np.spacing(np.abs(self.x)).astype(np.float64)
        moved = step != 0
        r = np.abs(step[moved]) / sp[moved]
        self.assertTrue(np.all(r <= 0.5))
        self.assertGreater(r.max(), 0.49)

    def test_grid_edges_are_not_moved_and_other_values_are(self):
        ji, _, _ = eep.internal_jitter(self.inputs, self.bkg, 3)
        y = np.asarray(self.x, np.float64)
        on_edge = np.isin(y, trm.EDGES[0])
        self.assertTrue(np.all(ji["MCgen"][on_edge] == y[on_edge]))
        self.assertGreater(np.mean(ji["MCgen"][~on_edge & (y != 0)] != y[~on_edge & (y != 0)]), 0.99)

    def test_it_acts_on_y_at_full_precision_not_after_a_float32_cast(self):
        """The trap of §2.2: delta_k on x_s must keep the protocol's step, so J_k(x_s) - J_k(x) = x_s - x."""
        xs = s5e_trace.jitter_coords(self.x, 1, trm.EDGES)
        a, _, _ = eep.internal_jitter(dict(self.inputs, MCgen=xs), self.bkg, 9)
        b, _, _ = eep.internal_jitter(self.inputs, self.bkg, 9)
        same32 = xs.astype(np.float32) == self.x
        diff = (a["MCgen"] - b["MCgen"])[same32]
        want = (xs - np.asarray(self.x, np.float64))[same32]
        self.assertGreater(np.count_nonzero(want), 1000)
        np.testing.assert_allclose(diff, want, rtol=0, atol=1e-12 * np.abs(self.x).max())

    def test_fixed_per_k_and_distinct_across_k(self):
        a = eep.internal_jitter(self.inputs, self.bkg, 4)
        b = eep.internal_jitter(self.inputs, self.bkg, 4)
        c = eep.internal_jitter(self.inputs, self.bkg, 5)
        self.assertEqual(a[2], b[2])
        self.assertNotEqual(a[2], c[2])
        for key in eep.COORDS:
            np.testing.assert_array_equal(a[0][key], b[0][key])

    def test_seed_zero_is_the_float64_copy_and_then_delta_k(self):
        """The base input is jittered(inputs, bkg, None), never a protocol jitter at seed 0: alone in mode 'base',
        plus exactly delta_k in mode 'stability'."""
        with eep.install("base", None):
            b, bb = s5p_numerics.jittered(self.inputs, self.bkg, 0)
        np.testing.assert_array_equal(b["MCgen"], np.asarray(self.x, np.float64))
        np.testing.assert_array_equal(bb["bkg_reco"], np.asarray(self.bkg["bkg_reco"], np.float64))
        with eep.install("stability", 6):
            j, _ = s5p_numerics.jittered(self.inputs, self.bkg, 0)
        want, _, _ = eep.internal_jitter(dict(self.inputs, MCgen=np.asarray(self.x, np.float64)), self.bkg, 6)
        np.testing.assert_array_equal(j["MCgen"], want["MCgen"])

    def test_an_undeclared_k_is_refused(self):
        for k in (0, eep.N_ENS + 1):
            with self.assertRaises(eep.Refusal):
                eep.internal_jitter(self.inputs, self.bkg, k)


# ------------------------------------------------------------------------------------- the stability path
class Stability(trm.Fixture):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with trm.standins(cls.d):
            cls.rc = {(k, s): run_stability(cls.d, cls.shas, k, s)[0] for k in (1, 2) for s in (0, 1)}
            cls.rc_base = run_stability(cls.d, cls.shas, None, 0, mode="base")[0]
            shutil.copytree(cls.d / "runs" / "stability", cls.d / "first")
            cls.rc_again = run_stability(cls.d, cls.shas, 1, 1)  # exists: skipped by the runner
            (cls.d / "runs" / "stability" / "ens1_k001_b-_j1.npz").unlink()
            cls.rc_again = run_stability(cls.d, cls.shas, 1, 1)[0]

    def test_every_call_ran(self):
        self.assertEqual(set(self.rc.values()), {0})
        self.assertEqual(self.rc_base, 0)

    def test_E_of_x_s_differs_from_E_of_x_and_their_inputs_differ_at_every_k(self):
        """REQUIRED (§2.2): on the sensitive fixture E_N(x_1) != E_N(x), and the coordinates differ at every k."""
        e0 = np.mean([stab_product(self.d, k, 0)[0] for k in (1, 2)], axis=0)
        e1 = np.mean([stab_product(self.d, k, 1)[0] for k in (1, 2)], axis=0)
        self.assertFalse(np.array_equal(e0, e1))
        for k in (1, 2):
            m0, m1 = stab_product(self.d, k, 0)[2]["ens1"], stab_product(self.d, k, 1)[2]["ens1"]
            for key in m0["coord_sha256"]:
                self.assertNotEqual(m0["coord_sha256"][key], m1["coord_sha256"][key])

    def test_the_fits_differ_across_k(self):
        self.assertFalse(np.array_equal(stab_product(self.d, 1, 0)[0], stab_product(self.d, 2, 0)[0]))

    def test_a_fit_is_deterministic(self):
        self.assertEqual(self.rc_again, 0)
        np.testing.assert_array_equal(stab_product(self.d, 1, 1)[0],
                                      esa.load(self.d / "first" / "ens1_k001_b-_j1.npz")[0])

    def test_products_carry_their_s_k_float64_and_the_control_path(self):
        x, _, m = stab_product(self.d, 2, 1)
        e = m["ens1"]
        self.assertEqual((e["schema"], e["mode"], e["k"], e["internal_seed"], e["protocol_seed"]),
                         (eep.SCHEMA, "stability", 2, 10002, 1))
        self.assertEqual((m["coords"], m["jitter_seed"]), ("float64", 1))
        self.assertEqual(m["stability_probe"]["candidate"], "control")
        _, _, m0 = stab_product(self.d, 1, 0)
        self.assertEqual((m0["coords"], m0["jitter_seed"]), ("float64", 0))

    def test_the_base_is_float64_seed_zero_without_internal_jitter(self):
        """REQUIRED (§2.2, ENS-1): the base runs -:0 in float64, never the float32 -:- pair, and adds no delta."""
        x, _, m = esa.load(self.d / "runs" / "F64" / "ens1_F64_b-_j0.npz")
        self.assertEqual((m["coords"], m["jitter_seed"], m["ens1"]["mode"], m["ens1"]["k"]), ("float64", 0, "base", None))
        self.assertIsNone(m["ens1"]["coord_sha256"])
        eea.check_float64_base(m, "F64")

    def test_names_restored(self):
        self.assertIs(s5p_numerics.jittered.__module__, "s5p_numerics")
        self.assertEqual(s5n_pseudo.write_product.__module__, "s5n_pseudo")


class Refusals(trm.Fixture):
    def test_undeclared_pairs_and_inputs_are_refused_and_the_declared_call_is_not(self):
        with trm.standins(self.d):
            for s, over, mode in ((21, {}, "stability"), ("-", {}, "stability"), (1, {}, "base"),
                                  (0, {"--threads": "2"}, "stability"), (0, {"--truth": "eavail_shape"}, "stability")):
                rc, err = run_stability(self.d, self.shas, None if mode == "base" else 1, s, mode=mode, **over)
                self.assertEqual(rc, 2, (s, over, mode, err))
                self.assertIn("refusing", err)
            self.assertEqual(run_stability(self.d, self.shas, 1, 0)[0], 0)

    def test_two_pairs_in_one_call_are_refused(self):
        ns = type("NS", (), {})()
        st = eep.STABILITY
        for k_, v in {"truth": st["truth"], "amplitude": st["amplitude"], "eavail_ratio": None, "pairs": "-:1,-:2"}.items():
            setattr(ns, k_, v)
        self.assertIsNotNone(eep.check_stability_namespace(ns, "stability"))

    def test_a_write_without_the_namespace_check_is_refused(self):
        with eep.install("stability", 1):
            with self.assertRaises(eep.Refusal):
                s5n_pseudo.write_product(self.d / "x.npz", {}, {})

    def test_install_arguments(self):
        with self.assertRaises(ValueError):
            with eep.install("base", 1):
                pass
        with self.assertRaises(ValueError):
            with eep.install("stability", None):
                pass

    def test_cli_refuses_an_undeclared_k(self):
        """Refused by the CLI's own check, before any runner is called (not by a later parse)."""
        called = []
        orig = eep.run
        eep.run = lambda *a: called.append(a) or 0
        try:
            for ks in ("0", "97", "3,3"):
                err = io.StringIO()
                with contextlib.redirect_stderr(err):
                    self.assertEqual(eep.main(["stability", "--k", ks, "--runs", str(self.d), "--", "--x"]), 2)
                self.assertIn("--k must be distinct values", err.getvalue())
            self.assertEqual(called, [])
            self.assertEqual(eep.main(["stability", "--k", "1,2", "--runs", str(self.d), "--", "--x"]), 0)
            self.assertEqual(len(called), 1)
        finally:
            eep.run = orig


# --------------------------------------------------------------------------------------- the closure path
class ClosurePath(unittest.TestCase):
    def setUp(self):
        import s5p_nullexp
        self.nx = s5p_nullexp
        rng = np.random.default_rng(11)
        self.x = trm.lattice(rng, 600)
        self.ui = {"MCgen": self.x, "MCreco": self.x.copy(), "measured": self.x[:50].copy(), "edges": trm.EDGES}
        self.ub = {"bkg_reco": self.x[:40].copy()}
        self.seen = {}
        self.saved = (s5p_nullexp.build, s5p_numerics.unfold_one)

        def build(ui, ub, *a):
            self.seen["ui"], self.seen["ub"] = ui, ub
            return "exp", None, {}

        def unfold_one(exp, dtype, *a, **kw):
            self.seen["dtype"] = dtype
            return np.zeros(1), {}
        s5p_nullexp.build, s5p_numerics.unfold_one = build, unfold_one

    def tearDown(self):
        self.nx.build, s5p_numerics.unfold_one = self.saved

    def test_the_closure_unfolds_in_float64_whatever_the_runner_asks(self):
        """REQUIRED (§2.2): s5p_nullexp.py:342 asks float32; the closure fit must run in float64."""
        with eep.install("closure", 1, "nominal"):
            s5p_numerics.unfold_one("exp", np.float32, 42, 1, 5)
        self.assertIs(self.seen["dtype"], np.float64)

    def test_the_closure_inputs_carry_delta_k_and_differ_across_k(self):
        got = []
        for k in (1, 2):
            with eep.install("closure", k, "nominal"):
                self.nx.build(self.ui, self.ub, 1, 991000, True, "half")
            got.append(self.seen["ui"]["MCgen"].copy())
            self.assertEqual(self.seen["ui"]["MCgen"].dtype, np.float64)
            self.assertFalse(np.array_equal(self.seen["ub"]["bkg_reco"], np.asarray(self.ub["bkg_reco"], np.float64)))
        self.assertFalse(np.array_equal(got[0], got[1]))
        self.assertFalse(np.array_equal(got[0], np.asarray(self.x, np.float64)))

    def test_a_move_across_the_grid_is_refused_before_the_build(self):
        orig = eep.internal_step
        eep.internal_step = lambda y, rng, edges: np.full(np.shape(y), 0.3)
        try:
            with eep.install("closure", 1, "nominal"):
                with self.assertRaises(eep.Refusal):
                    self.nx.build(self.ui, self.ub, 1, 991000, True, "half")
        finally:
            eep.internal_step = orig
        self.assertNotIn("ui", self.seen)

    def test_closure_namespace(self):
        a = type("A", (), {})()
        for k, v in {"npz": "n", "bkg": "b", "expect_npz_sha256": eep.STABILITY["npz_sha256"],
                     "expect_bkg_sha256": eep.STABILITY["bkg_sha256"], "bank": "B", "detector_dir": "D",
                     "closure_ratio_dir": "/pvl", "runs": "R"}.items():
            setattr(a, k, v)
        for truth in ("nominal", "W1", "closure_nuwro"):
            argv = eep.closure_argv(truth, a)
            ns = argparse_like(argv)
            self.assertIsNone(eep.check_closure_namespace(ns, truth), truth)
        ns = argparse_like(eep.closure_argv("A7_genie_cv", a))
        self.assertIsNotNone(eep.check_closure_namespace(ns, "nominal"))      # another hypothesis
        ns = argparse_like(eep.closure_argv("W1", a))
        self.assertIsNotNone(eep.check_closure_namespace(ns, "W2"))           # another alternative
        ns.expectation = False
        self.assertIsNotNone(eep.check_closure_namespace(ns, "W1"))


def argparse_like(argv):
    ns = type("NS", (), {"expectation": False, "no_nuisance": False, "alternative": None,
                         "alternative_amplitude": 1.0, "estimator_seed": 42})()
    i = 0
    while i < len(argv):
        key = argv[i][2:].replace("-", "_")
        if key in ("expectation", "no_nuisance"):
            setattr(ns, key, True)
            i += 1
            continue
        v = argv[i + 1]
        setattr(ns, key, int(v) if key in ("iters", "threads") else (float(v) if key == "alternative_amplitude" else v))
        i += 2
    return ns


# ---------------------------------------------------------------------------------------------- the queue
class Queue(unittest.TestCase):
    def build(self, stage):
        tmp = tempfile.TemporaryDirectory()
        d = Path(tmp.name)
        with contextlib.redirect_stdout(io.StringIO()):
            eep.main(["tasks", "--stage", str(stage), "--out-dir", str(d), "--runs", "/R", "--npz", "/n", "--bkg", "/b",
                      "--bank", "/B", "--detector-dir", "/D", "--closure-ratio-dir", "/P",
                      "--expect-npz-sha256", eep.STABILITY["npz_sha256"], "--expect-bkg-sha256", eep.STABILITY["bkg_sha256"]])
        rows = {f.name: [l.split("\t") for l in f.read_text().splitlines() if l and not l.startswith("#")]
                for f in d.glob("*.tsv")}
        tmp.cleanup()
        return rows

    def test_the_declared_counts(self):
        r1, r2 = self.build(1), self.build(2)
        n = lambda rows: sum(int(x[1]) for x in rows)  # noqa: E731
        self.assertEqual((len(r1["dry.tsv"]), n(r1["dry.tsv"])), (9, 9))
        self.assertEqual(sum(n(v) for k, v in r1.items() if k != "dry.tsv"), 2008)
        self.assertEqual(sorted(len(v) for k, v in r1.items() if k != "dry.tsv"), [167, 167, 167, 167, 168, 168])
        self.assertEqual((len(r2["dry.tsv"]), n(r2["dry.tsv"])), (7, 7))
        self.assertEqual(sum(n(v) for k, v in r2.items() if k != "dry.tsv"), 1626)
        cells = set()
        for v in r1.values():
            for row in v:
                if row[3] == "stability":
                    s = int(row[row.index("--") + 1:][-1].split(":")[1])
                    cells |= {(s, int(k)) for k in row[5].split(",")}
        self.assertEqual(cells, {(s, k) for s in range(21) for k in range(1, 97)})
        self.assertEqual(sum(1 for v in r1.values() for row in v if row[3] == "base"), 1)
        truths = {}
        for v in r2.values():
            for row in v:
                t = row[row.index("--truth") + 1]
                truths.setdefault(t, set()).update(int(k) for k in row[5].split(","))
        self.assertEqual(truths.pop("A7_mnvtune"), {1})
        self.assertEqual(len(truths), 17)
        self.assertTrue(all(v == set(range(1, 97)) for v in truths.values()))


# ------------------------------------------------------------------------------------------------ statistics
class Statistics(unittest.TestCase):
    def test_the_rebound_statistic_is_the_hand_computation_and_the_bound_one_at_25(self):
        rng = np.random.default_rng(1)
        rel, sig = rng.normal(0, 1e-3, (20, 30)), np.full(30, 1e-3)
        got = eea.stats_at_p(rel, sig)
        z = np.abs(rel) / sig
        m = np.maximum(z[0::2], z[1::2])
        self.assertAlmostEqual(got["mean_median"], float(np.median(m, axis=1).mean()), 12)
        self.assertAlmostEqual(got["mean_max"], float(m.max(axis=1).mean()), 12)
        rel51 = rng.normal(0, 1e-3, (51, 30))
        self.assertEqual(eea.stats_at_p(rel51, sig, 25), esa.stability_stats(rel51, sig))
        self.assertEqual(esa.N_PAIRS, 25)

    def test_n_pairs_is_restored_after_a_raise(self):
        with self.assertRaises(ValueError):
            eea.stats_at_p(np.zeros((3, 4)), np.ones(4))
        self.assertEqual(esa.N_PAIRS, 25)

    def test_c_hat_recovers_c(self):
        rng = np.random.default_rng(2)
        for c in (0.0, 0.2):
            f = 400
            g = rng.normal(size=(21, 1, f)) * math.sqrt(c)
            e = rng.normal(size=(21, eep.N_ENS, f)) * math.sqrt(1 - c)
            F = 1.0 + 1e-3 * (g + e)
            ch = eea.c_hat(F[0], F.mean(axis=1))
            self.assertLess(abs(float(np.median(ch)) - c), 0.02)

    def test_the_c_hat_reading_in_each_direction(self):
        self.assertIn("does not remove", eea.c_hat_reading("STAB_FAIL", 0.02))
        self.assertIn("no input-dependent", eea.c_hat_reading("STAB_FAIL", 0.001))
        self.assertIsNone(eea.c_hat_reading("STAB_FAIL", 0.006))
        self.assertIsNone(eea.c_hat_reading("STAB_PASS", 0.02))

    def test_the_stage2_factor_identity(self):
        """§5.2: s_E scaled by 1.358/1.20 into no_worse gives 3 sqrt((1.358 n_E)^2 + (1.20 n_F)^2)."""
        b, s_e, s_f = np.array([0.01, -0.02, 0.005]), np.array([1e-3, 2e-3, 1e-3]), np.array([2e-3, 1e-3, 1e-3])
        out = esa.no_worse(b, s_e * eea.SD_UPPER_E / esa.SD_UPPER, b, s_f)
        ne, nf = esa.metric_noise(b, s_e), esa.metric_noise(b, s_f)
        self.assertAlmostEqual(out["delta_rms"], 3 * math.hypot(eea.SD_UPPER_E * ne[0], esa.SD_UPPER * nf[0]), 14)
        self.assertAlmostEqual(out["delta_max"], 3 * math.hypot(eea.SD_UPPER_E * ne[1], esa.SD_UPPER * nf[1]), 14)


# -------------------------------------------------------------------------------------------- the analysis
F_DIM = 6   # fake functionals: 4 "s5e functionals" and 2 "cells", over a fine grid of 8


class FakeRun:
    """A fake ENS1 root: 21 x 96 stability products, the F64 base, FD-STAB references and SHA256SUMS, receipts."""

    def __init__(self, d: Path, spread_E=1e-6, spread_F=1e-2, tamper=None):
        self.d, self.refs = d / "root", d / "refs"
        rng = np.random.default_rng(4)
        self.pin = "p" * 40
        code = {"a.py": "1"}
        base = np.linspace(1.0, 2.0, 8)
        meta0 = {"construction": "pseudo", "truth": eep.STABILITY["truth"], "eavail_ratio_sha256": eep.STABILITY["ratio_sha256"],
                 "pseudo_seed": eep.STABILITY["pseudo_seed"], "input_npz_sha256": eep.STABILITY["npz_sha256"],
                 "bkg_dump_sha256": eep.STABILITY["bkg_sha256"], "bootstrap_seed": None, "code_sha256": code,
                 "stability_probe": {"candidate": "control", "code_sha256": "esp"}}
        st = self.d / "runs" / "stability"
        st.mkdir(parents=True)
        for s in range(21):
            for k in range(1, eep.N_ENS + 1):
                x = base * (1 + spread_E * rng.normal(size=8) * math.sqrt(eep.N_ENS))
                e = {"schema": eep.SCHEMA, "mode": "stability", "k": k, "internal_seed": 10000 + k, "protocol_seed": s,
                     "coord_sha256": {"MCgen": f"{s}-{k}"}, "code_sha256": "ens1"}
                m = {**meta0, "jitter_seed": s, "coords": "float64", "ens1": e}
                if tamper == "code" and (s, k) == (3, 3):
                    m["code_sha256"] = {"a.py": "2"}
                if tamper == "digest" and s == 2:
                    e["coord_sha256"] = {"MCgen": f"1-{k}"}
                self.write(st / f"ens1_k{k:03d}_b-_j{s}.npz", x, base, m)
        f64m = {**meta0, "jitter_seed": 0, "coords": "float32" if tamper == "f32base" else "float64",
                "ens1": {"mode": "base", "k": None, "code_sha256": "ens1"}}
        (self.d / "runs" / "F64").mkdir()
        self.write(self.d / "runs" / "F64" / "ens1_F64_b-_j0.npz", base, base, f64m)
        sums = []
        for s in range(1, 21):
            name = eea.STAB_REF.format(s)
            p = self.refs / name
            p.parent.mkdir(parents=True, exist_ok=True)
            m = {**meta0, "jitter_seed": s, "coords": "float64"}
            if tamper == "refcode" and s == 5:
                m["code_sha256"] = {"a.py": "other"}
            self.write(p, base * (1 + spread_F * rng.normal(size=8)), None, m)
            sums.append(f"{eea.sha256_path(p)}  {name}")
        if tamper == "refsum":
            sums[0] = "0" * 64 + sums[0][64:]
        self.sums = d / "SHA256SUMS"
        self.sums.write_text("\n".join(sums) + "\n")
        for name in ["log-dry"] + [f"log-shard{i}" for i in range(6)]:
            ld = self.d / "stage1" / name
            ld.mkdir(parents=True)
            (ld / "DONE").write_text(json.dumps({"stage": 1, "rc": 0, "tasks": 3, "ended": 3, "pin": self.pin}))

    @staticmethod
    def write(p, x, xt, meta):
        arrays = {"xsec_flat": np.asarray(x, float), "meta": json.dumps(meta)}
        if xt is not None:
            arrays["xtrue_flat"] = np.asarray(xt, float)
        np.savez(p, **arrays)


@contextlib.contextmanager
def fake_matrices(sigma=1e-3):
    U, M16 = np.eye(8)[:4], np.eye(8)[4:6]
    saved = (eea.functional_matrices, eea.sigma_rel, esa.N_FUNCTIONALS)
    eea.functional_matrices = lambda c, h: (U, [f"f{i}" for i in range(4)], M16)
    eea.sigma_rel = lambda r, names: np.full(4, sigma)
    esa.N_FUNCTIONALS = 4
    try:
        yield
    finally:
        eea.functional_matrices, eea.sigma_rel, esa.N_FUNCTIONALS = saved


class Analysis(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.t = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def read(self, run, stage=1):
        out = self.t / "out.json"
        with fake_matrices(), contextlib.redirect_stdout(io.StringIO()):
            rc = eea.main(["--stage", str(stage), "--root", str(run.d), "--pin", run.pin, "--refs", str(run.refs),
                           "--fdstab-sums", str(run.sums), "--s5c-contract", "c", "--sigma-receipt", "s",
                           "--h2-definition", "h", "--out", str(out)])
        return rc, json.loads(out.read_text())

    def test_a_small_ensemble_spread_passes_and_a_large_one_fails(self):
        rc, out = self.read(FakeRun(self.t / "a", spread_E=1e-6))
        self.assertEqual((rc, out["verdict"], out["g0_informative"]), (0, "STAB_PASS", True))
        rc, out = self.read(FakeRun(self.t / "b", spread_E=2e-3))
        self.assertEqual((rc, out["verdict"]), (0, "STAB_FAIL"))
        self.assertIn("median_all", out["c_hat"])

    def test_g0_reads_uninformative_when_the_control_passes(self):
        rc, out = self.read(FakeRun(self.t / "a", spread_F=1e-7))
        self.assertEqual(out["verdict"], "UNINFORMATIVE")

    def test_g0_refuses_a_float32_base(self):
        """REQUIRED (ENS-1): FD-STAB's float32 base cannot stand in for F64(x)."""
        rc, out = self.read(FakeRun(self.t / "a", tamper="f32base"))
        self.assertEqual((rc, out["verdict"]), (eea.STOP_RC, "STOP"))
        self.assertIn("G0", out["why"])

    def test_one_code_and_distinct_digests_are_required(self):
        rc, out = self.read(FakeRun(self.t / "a", tamper="code"))
        self.assertEqual(out["verdict"], "STOP")
        self.assertIn("E1", out["why"])
        rc, out = self.read(FakeRun(self.t / "b", tamper="digest"))
        self.assertIn("E2", out["why"])

    def test_references_must_be_pinned_and_from_the_same_estimator_code(self):
        rc, out = self.read(FakeRun(self.t / "a", tamper="refsum"))
        self.assertIn("E3", out["why"])
        rc, out = self.read(FakeRun(self.t / "b", tamper="refcode"))
        self.assertIn("other estimator code", out["why"])

    def test_an_incomplete_stage_grades_nothing(self):
        run = FakeRun(self.t / "a")
        (run.d / "stage1" / "log-shard3" / "DONE").unlink()
        rc, out = self.read(run)
        self.assertEqual((rc, out["verdict"]), (eea.INCOMPLETE_RC, "INCOMPLETE"))
        run2 = FakeRun(self.t / "b")
        (run2.d / "stage1" / "log-shard1" / "FAILED").write_text("rc=1")
        self.assertEqual(self.read(run2)[1]["verdict"], "INCOMPLETE")
        run3 = FakeRun(self.t / "c")
        (run3.d / "stage1" / "log-shard0" / "DONE").write_text(json.dumps({"stage": 1, "rc": 0, "tasks": 3, "ended": 3,
                                                                           "pin": "q" * 40}))
        self.assertEqual(self.read(run3)[1]["verdict"], "INCOMPLETE")

    def test_stage2_refuses_without_stab_pass(self):
        with self.assertRaises(eea.Stop):
            eea.stage2(None, {"verdict": "STAB_FAIL"})


class Stage2(unittest.TestCase):
    """The bias stage on fake closures: PASS, BIAS_WORSE, INVALID, and its stops."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.t = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def make(self, worse=None, det_differs=False, xt_differs=False, zero_floor=False, sf_off=False, det_xt=False,
             hyp_differs=False, split_differs=False):
        root, refs = self.t / "root", self.t / "refs"
        cells_true = np.array([1.0, 1.0])
        M16 = np.eye(8)[4:6]
        sums, rng = [], np.random.default_rng(8)
        stab_names = [eea.STAB_REF.format("-")] + [eea.STAB_REF.format(j) for j in range(1, 52)]
        base = np.ones(8)
        for i, n in enumerate(stab_names):
            p = refs / n
            p.parent.mkdir(parents=True, exist_ok=True)
            x = base if i == 0 else base * (1 + (0.0 if zero_floor else 1e-3) * rng.normal(size=8))
            FakeRun.write(p, x, None, {})
            sums.append(f"{eea.sha256_path(p)}  {n}")
        cells = [M16 @ esa.load(refs / n)[0] for n in stab_names]
        s_F = esa.cell_sd(cells[0], cells[1:])
        readout = self.t / "fd_stab.json"
        readout.write_text(json.dumps({"cell_sd": {"control": (np.round(s_F, 8) + (1e-6 if sf_off else 0)).tolist()}}))
        for t in eep.CLOSURE_TRUTHS:
            d = root / "runs" / "closure" / t
            d.mkdir(parents=True)
            ks = [1] if t == "A7_mnvtune" else range(1, eep.N_ENS + 1)
            for k in ks:
                xt = np.ones(8) * (1.001 if (xt_differs and k == 2) else 1.0)
                if det_xt and t == "A7_mnvtune":
                    xt = xt * 1.0000001
                b = 0.05 if t == worse else 0.01
                x = np.ones(8) * (1 + b)
                if det_differs and t == "A7_mnvtune":
                    x = x * 1.0000001
                m = {"ens1": {"mode": "closure", "truth": t, "k": k},
                     "hypothesis": {"sha256": "h2" if (hyp_differs and t == "W3") else "h"},
                     "alternative": None, "split_key": 8 if (split_differs and t == "q3") else 7}
                FakeRun.write(d / f"ens1_{t}_k{k:03d}_s991000.npz", x, xt, m)
            if t != "A7_mnvtune":
                n = eea.CLOSURE_REF.format(t=t)
                p = refs / n
                p.parent.mkdir(parents=True, exist_ok=True)
                FakeRun.write(p, np.ones(8) * 1.01, np.ones(8), {"hypothesis": {"sha256": "h"}, "alternative": None,
                                                                 "split_key": 7})
                sums.append(f"{eea.sha256_path(p)}  {n}")
        (self.t / "SHA256SUMS").write_text("\n".join(sums) + "\n")
        s1 = {"verdict": "STAB_PASS", "cell_sd_E96": [0.0, 0.0] if zero_floor else [1e-3, 1e-3]}
        a = type("A", (), {"root": str(root), "refs": str(refs), "fdstab_sums": str(self.t / "SHA256SUMS"),
                           "fdstab_readout": str(readout), "s5c_contract": "c", "h2_definition": "h"})()
        return a, s1, cells_true

    def run2(self, **kw):
        a, s1, _ = self.make(**kw)
        with fake_matrices():
            return eea.stage2(a, s1)

    def test_pass_and_bias_worse(self):
        self.assertEqual(self.run2()["verdict"], "PASS")
        self.tmp.cleanup()
        self.tmp = tempfile.TemporaryDirectory()
        self.t = Path(self.tmp.name)
        out = self.run2(worse="W2")
        self.assertEqual((out["verdict"], out["worse"]), ("BIAS_WORSE", ["W2"]))

    def test_s_e_carries_its_own_upper_factor(self):
        out = self.run2()
        np.testing.assert_allclose(out["s_E_scaled"], np.array([1e-3, 1e-3]) * 1.357637703528655 / esa.SD_UPPER,
                                   rtol=1e-12)

    def test_a_zero_floor_is_invalid(self):
        self.assertEqual(self.run2(zero_floor=True)["verdict"], "INVALID")

    def test_the_stops(self):
        for kw, why in (({"det_differs": True}, "determinism"), ({"det_xt": True}, "determinism"),
                        ({"xt_differs": True}, "truth vector"), ({"sf_off": True}, "s_F"),
                        ({"hyp_differs": True}, "hypothesis digest"), ({"split_differs": True}, "MC split")):
            self.tmp.cleanup()
            self.tmp = tempfile.TemporaryDirectory()
            self.t = Path(self.tmp.name)
            with self.assertRaises(eea.Stop) as cm:
                self.run2(**kw)
            self.assertIn(why, str(cm.exception))


# ---------------------------------------------------------------------------------------------- job script
class JobScript(unittest.TestCase):
    """sbatch_ens1.sh run locally on a stand-in deploy whose runner writes one product per task."""

    def setUp(self):
        trm.JobScript.setUp(self)
        (self.OUT / "stage1").mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def queue(self, name, ids, fail=()):
        rows = ["# id\tunfolds\tscript\targv"]
        for i in ids:
            argv = [i, "--out", str(self.OUT / "runs" / "stability")] + (["FAIL"] if i in fail else [])
            rows.append("\t".join([i, "1", "runner.py", *argv]))
        (self.OUT / "stage1" / name).write_text("\n".join(rows) + "\n")

    def job(self, *args, pin=None):
        env = dict(os.environ, ENS1_TIME_BIN=str(self.time))
        script = os.environ.get("ENS1_SBATCH", str(ND / "sbatch_ens1.sh"))
        return subprocess.run(["bash", script, *args, str(self.D), pin or self.pin, str(self.OUT)],
                              capture_output=True, text=True, env=env)

    def test_dry_then_a_shard_writes_done(self):
        self.queue("dry.tsv", ["a", "b"])
        self.queue("shard0.tsv", ["c", "d"])
        self.assertEqual(self.job("dry", "1").returncode, 0)
        r = self.job("shard", "1", "0")
        self.assertEqual(r.returncode, 0, r.stderr)
        d = json.loads((self.OUT / "stage1" / "log-shard0" / "DONE").read_text())
        self.assertEqual((d["stage"], d["shard"], d["pin"], d["tasks"]), (1, "0", self.pin, 2))
        self.assertIn("runs/stability/c.npz", (self.OUT / "stage1" / "log-shard0" / "SHA256SUMS").read_text())

    def test_a_shard_refuses_without_the_dry_done_or_at_another_pin(self):
        self.queue("dry.tsv", ["a"])
        self.queue("shard0.tsv", ["c"])
        r = self.job("shard", "1", "0")
        self.assertEqual(r.returncode, 2)
        self.assertIn("no DONE receipt", r.stderr)
        self.assertFalse((self.OUT / "stage1" / "log-shard0").exists())
        (self.OUT / "stage1" / "log-dry").mkdir()
        (self.OUT / "stage1" / "log-dry" / "DONE").write_text(json.dumps({"pin": "0" * 40}))
        r = self.job("shard", "1", "0")
        self.assertEqual(r.returncode, 2)
        self.assertIn("ran at pin", r.stderr)

    def test_a_failed_task_leaves_no_receipt(self):
        self.queue("dry.tsv", ["a", "b"], fail=("b",))
        self.assertEqual(self.job("dry", "1").returncode, 1)
        self.assertTrue((self.OUT / "stage1" / "log-dry" / "FAILED").read_text().startswith("rc="))
        self.assertFalse((self.OUT / "stage1" / "log-dry" / "DONE").exists())

    def test_refusals_existing_log_wrong_pin_bad_stage_or_shard_dirty_deploy(self):
        self.queue("dry.tsv", ["a"])
        (self.OUT / "stage1" / "log-dry").mkdir()
        self.assertEqual(self.job("dry", "1").returncode, 2)
        shutil.rmtree(self.OUT / "stage1" / "log-dry")
        self.assertEqual(self.job("dry", "1", pin="0" * 40).returncode, 2)
        (self.OUT / "stage3").mkdir()
        shutil.copy(self.OUT / "stage1" / "dry.tsv", self.OUT / "stage3" / "dry.tsv")
        r = self.job("dry", "3")
        self.assertEqual(r.returncode, 2)
        self.assertIn("refusing: stage 3", r.stderr)
        self.queue("shard6.tsv", ["c"])
        r = self.job("shard", "1", "6")
        self.assertEqual(r.returncode, 2)
        self.assertIn("refusing: shard 6", r.stderr)
        (self.D / "nd-unfolding" / "runner.py").write_text("changed\n")
        self.assertEqual(self.job("dry", "1").returncode, 2)
        subprocess.run(["git", "-C", str(self.D), "checkout", "-q", "--", "."], check=True)
        self.assertEqual(self.job("dry", "1").returncode, 0)

    def test_an_environment_without_lightgbm_is_refused(self):
        self.queue("dry.tsv", ["a"])
        (self.stub / "lightgbm.py").unlink()
        self.assertEqual(self.job("dry", "1").returncode, 7)


class DeclaredConstants(unittest.TestCase):
    def test_constants_match_the_declaration(self):
        self.assertEqual((eep.N_ENS, eea.P, eep.CHUNK, eep.SHARDS), (96, 10, 2, 6))
        self.assertEqual(eep.INTERNAL_SEEDS, tuple(range(10001, 10097)))
        used = set(esp.JITTER_SEEDS) | {0, 990000, 991000} | set(eep.PROTOCOL_SEEDS)
        self.assertFalse(used & set(eep.INTERNAL_SEEDS))
        self.assertEqual(eep.PROTOCOL_SEEDS, tuple(range(1, 21)))
        self.assertEqual((eea.BOUND_MEDIAN, eea.BOUND_MAX), (0.3, 1.0))
        from scipy.stats import chi2
        self.assertAlmostEqual(eea.SD_UPPER_E, math.sqrt(20 / chi2.ppf(0.05, 20)), 12)
        self.assertAlmostEqual(eea.C_STAR, 0.0110, 4)
        self.assertAlmostEqual(eea.EPS, 0.0033, 4)
        self.assertEqual(len(eep.CLOSURE_TRUTHS), 18)


if __name__ == "__main__":
    unittest.main()
