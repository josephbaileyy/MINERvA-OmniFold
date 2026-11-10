"""Tests of E96-DATA (fd/e96-data-20261110/E96D-DECLARATION.md, draft): the data role's namespace, its three modes, the
rebindings in the direction they act and the other, the queue, and the analysis's controls and arithmetic.

Run: python3 -B nd-unfolding/tests/test_ensemble_estimator_data.py (no LightGBM, no ROOT). The runs use RS1's fixture
and stand-in estimators (tests/test_rounding_mechanism.py), through the real ``s5p_numerics.main`` with
``--construction data``.
"""
import contextlib
import hashlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

ND = Path(__file__).resolve().parents[1]
REPO = ND.parent
sys.path.insert(1, str(ND))
sys.path.insert(1, str(ND / "tests"))
import ensemble_estimator_data as eed  # noqa: E402
import ensemble_estimator_probe as eep  # noqa: E402
import s1_assemble as sa  # noqa: E402
import s5n_pseudo  # noqa: E402
import s5p_numerics  # noqa: E402
import test_rounding_mechanism as trm  # noqa: E402

DEFINITION = ND / "pv-ladder" / "readouts" / "h2_definition.json"


def data_args(d, shas, pairs, **over):
    a = {"--npz": str(d / "in.npz"), "--bkg": str(d / "bkg.npz"), "--expect-npz-sha256": shas[0],
         "--expect-bkg-sha256": shas[1], "--config": "R", "--iters": "5", "--threads": "1", "--construction": "data",
         "--tag": "x", "--out": str(d / "x")}
    a.update(over)
    out = []
    for k, v in a.items():
        if v is not None:
            out += [k, v]
    return out + [f"--pairs={pairs}"]


def run_mode(d, shas, mode, ks, pairs, **over):
    err = io.StringIO()
    with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
        try:
            rc = eed.run(mode, ks, data_args(d, shas, pairs, **over), d / "runs")
        except SystemExit as exc:
            rc = exc.code
    return rc, err.getvalue()


def product(d, mode, tag, j):
    with np.load(d / "runs" / mode / f"{tag}_b-_j{'-' if j is None else j}.npz", allow_pickle=False) as z:
        return np.asarray(z["xsec_flat"]), json.loads(str(z["meta"]))


# --------------------------------------------------------------------------------------------- the data runs
class DataRun(trm.Fixture):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with trm.standins(cls.d):
            cls.rc = {"control": run_mode(cls.d, cls.shas, "control", [None], "-:-")[0],
                      "base": run_mode(cls.d, cls.shas, "base", [None], "-:0")[0],
                      "ensemble": run_mode(cls.d, cls.shas, "ensemble", [1, 2], "-:0")[0]}
            # (e)'s own path, run directly by the bound runner without any E96-DATA rebinding
            with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
                cls.rc_direct = s5p_numerics.main(data_args(cls.d, cls.shas, "-:-", **{"--tag": "direct",
                                                                                           "--out": str(cls.d / "direct")}))

    def test_every_call_ran(self):
        self.assertEqual(self.rc, {"control": 0, "base": 0, "ensemble": 0})
        self.assertEqual(self.rc_direct, 0)

    def test_the_control_is_es_own_path_bitwise(self):
        """REQUIRED: the control is the runner's float32 -:- path, bitwise the bound runner's own product."""
        x, m = product(self.d, "control", "e96data_E", None)
        with np.load(self.d / "direct" / "direct_b-_j-.npz", allow_pickle=False) as z:
            np.testing.assert_array_equal(x, np.asarray(z["xsec_flat"]))
        self.assertEqual((m["coords"], m["jitter_seed"], m["construction"]), ("float32", None, "data"))
        self.assertEqual((m["e96_data"]["mode"], m["e96_data"]["k"]), ("control", None))
        with trm.standins(self.d):
            self.assertEqual(eed.product_problems(m, "control", None), [])

    def test_the_base_is_float64_seed_zero_without_delta(self):
        """REQUIRED: F64 is -:0 in float64 with no internal jitter."""
        _, m = product(self.d, "base", "e96data_F64", 0)
        self.assertEqual((m["coords"], m["jitter_seed"], m["e96_data"]["mode"]), ("float64", 0, "base"))
        self.assertIsNone(m["e96_data"]["coord_sha256"])
        with trm.standins(self.d):
            self.assertEqual(eed.product_problems(m, "base", None), [])

    def test_the_ensemble_fits_carry_delta_k_and_differ_across_k(self):
        x1, m1 = product(self.d, "ensemble", "e96data_k001", 0)
        x2, m2 = product(self.d, "ensemble", "e96data_k002", 0)
        xb, _ = product(self.d, "base", "e96data_F64", 0)
        self.assertFalse(np.array_equal(x1, x2))
        self.assertFalse(np.array_equal(x1, xb))
        self.assertNotEqual(m1["e96_data"]["coord_sha256"], m2["e96_data"]["coord_sha256"])
        self.assertEqual((m1["e96_data"]["k"], m1["e96_data"]["internal_seed"]), (1, eep.INTERNAL_BASE + 1))
        for m, k in ((m1, 1), (m2, 2)):
            with trm.standins(self.d):
                self.assertEqual(eed.product_problems(m, "ensemble", k), [])
            self.assertEqual(m["e96_data"]["moved_rows"], {"MCgen": 0, "MCreco": 0, "measured": 0, "bkg_reco": 0})

    def test_the_jitter_is_enss_byte_for_byte(self):
        """The data role adds ENS1's own delta_k to the float64 copy, nothing else."""
        inputs = s5n_pseudo_inputs(self.d)
        with eed.install("ensemble", 5):
            ji, jb = s5p_numerics.jittered(inputs[0], inputs[1], 0)
        f64 = {k: np.asarray(v, np.float64) if k in eep.COORDS else v for k, v in inputs[0].items()}
        want, wantb, _ = eep.internal_jitter(f64, {"bkg_reco": np.asarray(inputs[1]["bkg_reco"], np.float64)}, 5)
        for key in eep.COORDS:
            np.testing.assert_array_equal(ji[key], want[key])
        np.testing.assert_array_equal(jb["bkg_reco"], wantb["bkg_reco"])

    def test_names_restored(self):
        self.assertEqual(s5p_numerics.jittered.__module__, "s5p_numerics")
        self.assertEqual(s5n_pseudo.write_product.__module__, "s5n_pseudo")


def s5n_pseudo_inputs(d):
    import s5c_unfold
    inputs = s5c_unfold.load_inputs(d / "in.npz")
    bz = np.load(d / "bkg.npz", allow_pickle=True)
    return inputs, {"bkg_reco": bz["bkg_reco"], "bkg_w": bz["bkg_w"], "bkg_nd": bz["bkg_nd"]}


# -------------------------------------------------------------------------------------------- the refusals
class Refusals(trm.Fixture):
    def test_a_pseudo_construction_is_refused(self):
        """REQUIRED: the data role never runs a pseudo construction."""
        with trm.standins(self.d):
            rc, err = run_mode(self.d, self.shas, "base", [None], "-:0", **{"--construction": "pseudo",
                                                                           "--pseudo-seed": "990000"})
        self.assertEqual(rc, 2, err)
        self.assertIn("runs only --construction data", err)

    def test_undeclared_pairs_are_refused_and_the_declared_ones_are_not(self):
        with trm.standins(self.d):
            for mode, ks, pairs in (("control", [None], "-:0"), ("base", [None], "-:1"), ("base", [None], "-:-"),
                                    ("ensemble", [1], "-:-"), ("ensemble", [1], "-:0,-:1"), ("base", [None], "1:0")):
                rc, err = run_mode(self.d, self.shas, mode, ks, pairs)
                self.assertEqual(rc, 2, (mode, pairs, err))
                self.assertIn("runs the single pair", err)
            self.assertEqual(run_mode(self.d, self.shas, "base", [None], "-:0")[0], 0)

    def test_each_namespace_check_refuses(self):
        cases = (({"--threads": "2"}, "--threads must be"), ({"--iters": "4"}, "--iters must be 5"),
                 ({"--estimator-seed": "7"}, "--estimator-seed must be 42"),
                 ({"--expect-npz-sha256": "0" * 64}, "expected input digests"),
                 ({"--capacity": "10,5"}, "--capacity is refused"),
                 ({"--eavail-ratio": str(self.d / "ratio.json")}, "--eavail-ratio is refused"),
                 ({"--truth": "W1"}, "--truth and --amplitude"), ({"--amplitude": "1.0"}, "--truth and --amplitude"))
        with trm.standins(self.d):
            for over, why in cases:
                rc, err = run_mode(self.d, self.shas, "base", [None], "-:0", **over)
                self.assertEqual(rc, 2, (over, err))
                self.assertIn(why, err, over)

    def test_a_write_without_the_namespace_check_is_refused(self):
        """REQUIRED."""
        with eed.install("base", None):
            with self.assertRaises(eed.Refusal):
                s5n_pseudo.write_product(self.d / "x.npz", {}, {})

    def test_the_control_takes_no_jitter_and_the_base_no_protocol_seed(self):
        inputs, bkg = s5n_pseudo_inputs(self.d)
        with eed.install("control", None):
            for seed in (0, None):          # 0 would pass the seed check: only the control's own refusal stops it
                with self.assertRaises(eed.Refusal):
                    s5p_numerics.jittered(inputs, bkg, seed)
        for mode, k in (("base", None), ("ensemble", 1)):
            with eed.install(mode, k):
                with self.assertRaises(eed.Refusal):
                    s5p_numerics.jittered(inputs, bkg, 1)

    def test_the_base_is_the_float64_copy(self):
        """REQUIRED: seed 0 is the float64 copy jittered(inputs, bkg, None), never a protocol jitter at seed 0."""
        inputs, bkg = s5n_pseudo_inputs(self.d)
        with eed.install("base", None):
            b, bb = s5p_numerics.jittered(inputs, bkg, 0)
        for key in eep.COORDS:
            np.testing.assert_array_equal(b[key], np.asarray(inputs[key], np.float64))
        np.testing.assert_array_equal(bb["bkg_reco"], np.asarray(bkg["bkg_reco"], np.float64))

    def test_install_arguments(self):
        for mode, k in (("base", 1), ("control", 1), ("ensemble", None), ("stability", 1)):
            with self.assertRaises(ValueError):
                with eed.install(mode, k):
                    pass

    def test_cli_refuses_an_undeclared_k_before_any_runner(self):
        called = []
        orig = eed.run
        eed.run = lambda *a: called.append(a) or 0
        try:
            for ks in ("0", "97", "3,3"):
                err = io.StringIO()
                with contextlib.redirect_stderr(err):
                    self.assertEqual(eed.main(["ensemble", "--k", ks, "--runs", str(self.d), "--", "--x"]), 2)
                self.assertIn("--k must be distinct values", err.getvalue())
            self.assertEqual(called, [])
            self.assertEqual(eed.main(["ensemble", "--k", "1,2", "--runs", str(self.d), "--", "--x"]), 0)
            self.assertEqual(eed.main(["stability", "--runs", str(self.d), "--", "--x"]), 2)
        finally:
            eed.run = orig


# --------------------------------------------------------------------------------------------- the declared
class Declared(unittest.TestCase):
    def test_the_declared_call_is_es_own(self):
        """The production values are (e)'s data unfold's argv (s5p/s2-num-tasks.tsv:2) and the runner's defaults."""
        line = (REPO / "docs/orchestration/state/s5p/s2-num-tasks.tsv").read_text().splitlines()[1].split("\t")
        self.assertEqual(line[0], "n1_data_ctrl")
        arg = {line[i]: line[i + 1] for i in range(2, len(line) - 1) if line[i].startswith("--") and "=" not in line[i]}
        d = eed.declared()
        self.assertEqual((d["npz_sha256"], d["bkg_sha256"]), (arg["--expect-npz-sha256"], arg["--expect-bkg-sha256"]))
        self.assertEqual((str(d["iters"]), str(d["threads"]), d["config"]), (arg["--iters"], arg["--threads"], arg["--config"]))
        self.assertEqual(arg["--construction"], "data")
        self.assertIn("--pairs=-:-,1:-,2:-", line)     # (e)'s central product is the -:- pair of this line
        self.assertEqual(d["estimator_seed"], 42)

    def test_the_queue(self):
        a = type("A", (), {"runs": Path("/R"), "npz": Path("/n.npz"), "bkg": Path("/b.npz")})()
        lines = eed.task_lines(a)
        self.assertEqual(len(lines), 50)
        self.assertEqual(sum(int(l.split("\t")[1]) for l in lines), eed.N_ENS + 2)
        self.assertTrue(all(l.split("\t")[0].startswith(eed.FAMILY) for l in lines))
        ks = []
        for l in lines[2:]:
            cols = l.split("\t")
            ks += [int(v) for v in cols[cols.index("--k") + 1].split(",")]
        self.assertEqual(ks, list(range(1, eed.N_ENS + 1)))
        self.assertIn("--pairs=-:-", lines[0])
        self.assertIn("--pairs=-:0", lines[1])
        argv = lines[2].split("\t")[3:]
        self.assertEqual(eed.expected_outputs(argv), [Path("/R/ensemble/e96data_k001_b-_j0.npz"),
                                                      Path("/R/ensemble/e96data_k002_b-_j0.npz")])
        self.assertEqual(eed.expected_outputs(lines[0].split("\t")[3:]), [Path("/R/control/e96data_E_b-_j-.npz")])


# --------------------------------------------------------------------------------------------- the analysis
def fake_meta(mode, k, moved=0, coords=None, digest=None):
    d = eed.declared()
    j = eed.PAIR[mode][1]
    return {"construction": "data", "input_npz_sha256": d["npz_sha256"], "bkg_dump_sha256": d["bkg_sha256"],
            "bootstrap_seed": None, "jitter_seed": j, "coords": coords or ("float32" if mode == "control" else "float64"),
            "estimator_seed": d["estimator_seed"], "threads": d["threads"], "iters": d["iters"],
            "code_sha256": {"s5p_numerics.py": "c" * 64},
            "e96_data": {"schema": eed.SCHEMA, "mode": mode, "k": k, "code_sha256": "d" * 64, "ens1_probe_sha256": "e" * 64,
                         "moved_rows": {"MCgen": moved, "MCreco": 0, "measured": 0, "bkg_reco": 0},
                         "coord_sha256": digest if digest is not None else (None if k is None else {"MCgen": f"{k:064d}"})}}


class Analysis(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.U = sa.functional_matrix(sa.fine_map(DEFINITION))

    def build(self, d: Path, defect=None):
        rng = np.random.default_rng(11)
        n = self.U.shape[1]
        x_e = rng.uniform(1.0, 2.0, n) * 1e-40
        np.savez(d / "e.npz", xsec_flat=x_e, meta=json.dumps({}))
        f = self.U @ x_e
        if defect == "f":
            f = f * (1 + 1e-9)
        (d / "dp.json").write_text(json.dumps({"f": f.tolist(), "cells": [f"R{i:02d}" for i in range(16)],
                                               "relative_sigma": {"C_e": [0.05] * 16}}))
        runs = d / "runs"
        for m in eed.MODES:
            (runs / m).mkdir(parents=True)
        x_c = x_e.copy()
        if defect == "ulp":
            x_c[123] = np.nextafter(x_c[123], 1.0)
        np.savez(runs / "control" / "e96data_E_b-_j-.npz", xsec_flat=x_c, meta=json.dumps(fake_meta("control", None)))
        x_b = x_e * (1 + 1e-3 * rng.normal(size=n))
        np.savez(runs / "base" / "e96data_F64_b-_j0.npz", xsec_flat=x_b, meta=json.dumps(fake_meta("base", None)))
        X = []
        for k in range(1, eed.N_ENS + 1):
            if defect == "missing" and k == 40:
                continue
            x = x_e * (1 + 2e-3 * rng.normal(size=n))
            X.append(x)
            meta = fake_meta("ensemble", k, moved=1 if (defect == "moved" and k == 7) else 0,
                             digest={"MCgen": "same"} if defect == "dup" else None)
            np.savez(runs / "ensemble" / f"e96data_k{k:03d}_b-_j0.npz", xsec_flat=x, meta=json.dumps(meta))
        return x_e, x_b, np.stack(X)

    def run_analysis(self, defect=None):
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            x_e, x_b, X = self.build(d, defect)
            a = type("A", (), {"runs": d / "runs", "e_product": d / "e.npz", "definition": DEFINITION,
                               "data_product": d / "dp.json", "out": d / "out.json"})()
            with contextlib.redirect_stdout(io.StringIO()):
                rc = eed.analyze(a, e_sha=hashlib.sha256((d / "e.npz").read_bytes()).hexdigest())
            rec = json.loads((d / ("out.json" if rc == 0 else "out.STOP.json")).read_text())
            return rc, rec, (x_e, x_b, X)

    def test_the_result_is_the_hand_computation(self):
        rc, rec, (x_e, x_b, X) = self.run_analysis()
        self.assertEqual(rc, 0, rec["controls"])
        f_e, f_b, F = self.U @ x_e, self.U @ x_b, X @ self.U.T
        f_E = self.U @ X.mean(axis=0)
        s = rec["sixteen"]
        np.testing.assert_allclose(s["E96_over_e_minus_1"], f_E / f_e - 1, rtol=1e-12, atol=1e-15)
        np.testing.assert_allclose(s["F64_over_e_minus_1"], f_b / f_e - 1, rtol=1e-12, atol=1e-15)
        np.testing.assert_allclose(s["E96_over_F64_minus_1"], f_E / f_b - 1, rtol=1e-12, atol=1e-15)
        np.testing.assert_allclose(s["E96_mean_sd_over_e"], F.std(axis=0, ddof=1) / np.sqrt(96) / f_e, rtol=1e-12)
        np.testing.assert_allclose(s["E96_minus_e_over_sigma_Ce"], (f_E / f_e - 1) / 0.05, rtol=1e-12, atol=1e-13)

    def test_a_control_one_ulp_off_stops(self):
        """REQUIRED: the control must equal (e)'s product bitwise; one ulp in one fine cell is a STOP."""
        rc, rec, _ = self.run_analysis("ulp")
        self.assertEqual(rc, 8)
        self.assertFalse(rec["controls"]["A-D1 the control equals (e)'s xsec_flat bitwise, and is the declared call"]["pass"])
        self.assertNotIn("sixteen", rec)

    def test_each_a_d2_defect_stops(self):
        for defect in ("missing", "moved", "dup"):
            rc, rec, _ = self.run_analysis(defect)
            self.assertEqual(rc, 8, defect)
            name = "A-D2 F64 and 96 fits, each the declared call, one code, 96 distinct jitters"
            self.assertFalse(rec["controls"][name]["pass"], defect)
            self.assertNotIn("sixteen", rec)

    def test_an_f_that_is_not_es_stops(self):
        rc, rec, _ = self.run_analysis("f")
        self.assertEqual(rc, 8)
        self.assertFalse(rec["controls"]["A-D0 U @ (e)'s xsec_flat equals the data product's f to 1e-12"]["pass"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
