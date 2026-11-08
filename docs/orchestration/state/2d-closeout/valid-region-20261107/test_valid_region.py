"""Tests for valid_region.py (DECLARATION.md section 9). Every guard and every class boundary is tested in both
directions on synthetic fixtures with the inputs' schema. No real input is read.

Run from this directory: python3 -B -m unittest test_valid_region
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"

import copy  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import sys  # noqa: E402
import tempfile  # noqa: E402
import unittest  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import valid_region as vr  # noqa: E402

# The declared boxes (DECLARATION.md section 3; the definition's cells, fd_data_product_cells.csv).
BOXES = [
    ((0.0, 0.7), (1.5, 4.5), (0.0, 0.8), (0.0, 2.0), (0.0, 100.0)),
    ((0.0, 0.7), (1.5, 4.5), (0.0, 100.0), (2.0, 100.0), (1.8, 100.0)),
    ((0.0, 0.7), (1.5, 4.5), (0.8, 100.0), (0.0, 2.0), (0.0, 1.8)),
    ((0.0, 0.7), (1.5, 4.5), (0.8, 100.0), (0.0, 2.0), (1.8, 100.0)),
    ((0.0, 0.7), (4.5, 60.0), (0.0, 0.8), (0.0, 2.0), (0.0, 100.0)),
    ((0.0, 0.7), (4.5, 60.0), (0.0, 100.0), (2.0, 100.0), (1.8, 100.0)),
    ((0.0, 0.7), (4.5, 60.0), (0.8, 100.0), (0.0, 2.0), (0.0, 1.8)),
    ((0.0, 0.7), (4.5, 60.0), (0.8, 100.0), (0.0, 2.0), (1.8, 100.0)),
    ((0.7, 4.5), (1.5, 4.5), (0.0, 0.8), (0.0, 100.0), (0.0, 1.8)),
    ((0.7, 4.5), (1.5, 4.5), (0.0, 100.0), (0.0, 100.0), (1.8, 100.0)),
    ((0.7, 4.5), (1.5, 4.5), (0.8, 100.0), (0.0, 2.0), (0.0, 1.8)),
    ((0.7, 4.5), (1.5, 4.5), (0.8, 100.0), (2.0, 100.0), (0.0, 1.8)),
    ((0.7, 4.5), (4.5, 60.0), (0.0, 0.8), (0.0, 2.0), (0.0, 100.0)),
    ((0.7, 4.5), (4.5, 60.0), (0.0, 100.0), (2.0, 100.0), (0.0, 1.8)),
    ((0.7, 4.5), (4.5, 60.0), (0.0, 100.0), (2.0, 100.0), (1.8, 100.0)),
    ((0.7, 4.5), (4.5, 60.0), (0.8, 100.0), (0.0, 2.0), (0.0, 100.0)),
]
AXES = ("pt", "pz", "eavail", "q3", "W")
LOW = [c for c, b in zip(vr.CELLS, BOXES) if b[1][1] <= 4.5]
TRUTHS = [  # name, row, group, own_vertex, graded
    ("nominal", 1, "prior", None, True), ("W1", 1, "vertex-family", "nuwro", True),
    ("W2", 1, "vertex-family", "genie_mec", True), ("W3", 1, "vertex-family", "nuwro", True),
    ("q3", 1, "non-vertex", None, True), ("stage0c_gibuu", 2, "vertex-family", "gibuu", True),
    ("closure_nuwro", 3, "vertex-family", "nuwro", True), ("A7_mnvtune", 4, "prior", None, True),
    ("A7_genie_cv", 4, "non-vertex", None, True), ("A7_genie_mec", 4, "vertex-family", "genie_mec", True),
    ("A7_nuwro", 4, "vertex-family", "nuwro", True), ("A7_gibuu", 4, "vertex-family", "gibuu", True),
    ("P1r", 6, "vertex-family", "nuwro", False), ("P3g", 6, "vertex-family", "genie_mec", False),
]


def box(i):
    return {a: list(v) for a, v in zip(AXES, BOXES[i])}


def make_inputs(seed=1):
    rng = np.random.default_rng(seed)
    f = 1e-39 * rng.uniform(0.3, 5.0, 16)
    A = rng.normal(size=(16, 16))
    corr = A @ A.T + 16 * np.eye(16)
    dsd = np.sqrt(np.diag(corr))
    corr = corr / np.outer(dsd, dsd)
    rel = rng.uniform(0.04, 0.14, 16)
    C = corr * np.outer(rel * f, rel * f)
    truths = []
    for name, row, group, own, graded in TRUTHS:
        t = {"name": name, "row": row, "group": group, "own_vertex": own, "graded": graded,
             "bias": rng.normal(0, 0.01, 16).tolist(), "noise_sigma": rng.uniform(0, 0.002, 16).tolist(),
             "grade": {"z": rng.uniform(-1.5, 1.5, 16).tolist(), "p": 0.5, "p_lt_0.01": False}}
        if name == "closure_nuwro":
            t["noise_sigma"] = [0.0] * 16
        if own == "gibuu":
            t["p_parallel_lt_4p5"] = {"cells": list(LOW)}
        truths.append(t)
    i1 = {"cells": list(vr.CELLS), "truths": truths}
    i2 = {"cells": list(vr.CELLS), "truths": copy.deepcopy(truths)}
    preds = []
    for name in ("genie_cv", "genie_mec", "nuwro", "gibuu", "mnvtune_v1"):
        cells = list(LOW) if name == "gibuu" else list(vr.CELLS)
        idx = [vr.CELLS.index(c) for c in cells]
        g = f[idx] * rng.uniform(0.8, 1.2, len(idx))
        preds.append({"name": name, "cells": cells, "f": f[idx].tolist(), "g": g.tolist(),
                      "sigma_Vg_over_f": rng.uniform(0.002, 0.01, len(idx)).tolist(),
                      "g_over_f_minus_1": (g / f[idx] - 1.0).tolist()})
    i3 = {"predictions": preds}
    i4 = {"cells": [{"cell": c, "box": box(k)} for k, c in enumerate(vr.CELLS)], "f": f.tolist(),
          "matrices": {vr.COV_KEY: C.tolist()},
          "relative_sigma": {vr.COV_KEY: (np.sqrt(np.diag(C)) / f).tolist(),
                             "C_model_abs": rng.uniform(0.0, 0.1, 16).tolist()}}
    i5 = {"reporting_cells": [{"id": k, "reported": True, "box": box(k),
                               "mc_neff_truth": float(rng.uniform(1e5, 3e6))} for k in range(16)]}
    i6 = {"cells": list(vr.CELLS), "relative_sigma": {"stat": rng.uniform(0.001, 0.004, 16).tolist()}}
    return {"I1": i1, "I2": i2, "I3": i3, "I4": i4, "I5": i5, "I6": i6}


def write_repo(root, d, pin=True):
    for k, rel in vr.INPUTS.items():
        p = Path(root) / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(d[k]))
    if pin:
        lines = [f"{hashlib.sha256((Path(root) / rel).read_bytes()).hexdigest()}  {rel}" for rel in vr.INPUTS.values()]
        pp = Path(root) / vr.DECL_DIR / "INPUTS.sha256"
        pp.parent.mkdir(parents=True, exist_ok=True)
        pp.write_text("\n".join(lines) + "\n")


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "repo"
        self.d = make_inputs()

    def tearDown(self):
        self.tmp.cleanup()

    def run_read(self, d=None, pin=True):
        write_repo(self.root, d if d is not None else self.d, pin=pin)
        out = Path(self.tmp.name) / f"out{np.random.randint(1 << 30)}"
        rc = vr.do_read(self.root, out)
        return rc, json.loads((out / "readout.json").read_text())

    def failed(self, readout):
        return [c["control"] for c in readout["controls"] if not c["pass"]]

    def assert_stop(self, d, control):
        rc, ro = self.run_read(d)
        self.assertEqual(rc, 3)
        self.assertIn(control, self.failed(ro))
        self.assertNotIn("readings", ro)


class TestEndToEnd(Fixture):
    def test_clean_fixture_reads(self):
        rc, ro = self.run_read()
        self.assertEqual(rc, 0)
        self.assertEqual(self.failed(ro), [])
        self.assertIn("readings", ro)
        self.assertEqual(len(ro["controls"]), 11)

    def test_out_exists_refused(self):
        write_repo(self.root, self.d)
        out = Path(self.tmp.name) / "exists"
        out.mkdir()
        self.assertEqual(vr.main(["read", "--repo", str(self.root), "--out", str(out)]), 4)

    def test_missing_input_refused(self):
        write_repo(self.root, self.d)
        (self.root / vr.INPUTS["I6"]).unlink()
        self.assertEqual(vr.main(["read", "--repo", str(self.root), "--out", str(Path(self.tmp.name) / "o")]), 4)

    def test_main_exit_0_and_3(self):
        write_repo(self.root, self.d)
        self.assertEqual(vr.main(["read", "--repo", str(self.root), "--out", str(Path(self.tmp.name) / "a")]), 0)
        (self.root / vr.INPUTS["I2"]).write_text(json.dumps(self.d["I2"]) + " ")
        self.assertEqual(vr.main(["read", "--repo", str(self.root), "--out", str(Path(self.tmp.name) / "b")]), 3)

    def test_text_summary(self):
        rc, ro = self.run_read()
        txt = vr.text_summary(ro)
        self.assertIn("descriptive only", txt)
        self.assertIn("V-PRIOR", txt)


class TestControls(Fixture):
    def test_pin(self):
        write_repo(self.root, self.d)
        (self.root / vr.INPUTS["I4"]).write_text(json.dumps(self.d["I4"]) + "\n")
        out = Path(self.tmp.name) / "o"
        self.assertEqual(vr.do_read(self.root, out), 3)
        ro = json.loads((out / "readout.json").read_text())
        self.assertEqual(self.failed(ro), ["C-PIN"])
        self.assertNotIn("readings", ro)

    def test_cells_order(self):
        d = copy.deepcopy(self.d)
        d["I6"]["cells"] = d["I6"]["cells"][::-1]
        self.assert_stop(d, "C-CELLS")

    def test_cells_unreported(self):
        d = copy.deepcopy(self.d)
        d["I5"]["reporting_cells"][3]["reported"] = False
        self.assert_stop(d, "C-CELLS")

    def test_box_mismatch(self):
        d = copy.deepcopy(self.d)
        d["I5"]["reporting_cells"][5]["box"]["q3"] = [0.0, 3.0]
        self.assert_stop(d, "C-BOX")

    def test_box_quadrant(self):
        d = copy.deepcopy(self.d)
        for k in (0,):
            d["I4"]["cells"][k]["box"]["pz"] = [4.5, 60.0]
            d["I5"]["reporting_cells"][k]["box"]["pz"] = [4.5, 60.0]
        self.assert_stop(d, "C-BOX")

    def test_box_siblings_identical(self):
        d = copy.deepcopy(self.d)
        for src in (d["I4"]["cells"][1]["box"], d["I5"]["reporting_cells"][1]["box"]):
            src.update(copy.deepcopy(box(0)))
        self.assert_stop(d, "C-BOX")

    def test_domain(self):
        d = copy.deepcopy(self.d)
        d["I1"]["truths"][5]["p_parallel_lt_4p5"]["cells"] = LOW[:7]
        d["I2"]["truths"][5]["p_parallel_lt_4p5"]["cells"] = LOW[:7]
        self.assert_stop(d, "C-DOMAIN")

    def test_truths(self):
        d = copy.deepcopy(self.d)
        d["I1"]["truths"][12]["graded"] = True
        self.assert_stop(d, "C-TRUTHS")

    def test_truths_names_with_twelve_graded(self):
        """Twelve graded truths, but W1 moved to the prior group: only the name check catches it."""
        d = copy.deepcopy(self.d)
        d["I1"]["truths"][1]["group"] = "prior"
        self.assertEqual(sum(1 for t in d["I1"]["truths"] if t["graded"]), 12)
        self.assert_stop(d, "C-TRUTHS")

    def test_bias_exact(self):
        d = copy.deepcopy(self.d)
        d["I2"]["truths"][2]["bias"][4] += 1e-15
        self.assert_stop(d, "C-BIAS")

    def test_bias_noise(self):
        d = copy.deepcopy(self.d)
        d["I2"]["truths"][2]["noise_sigma"][4] *= 1.0000001
        self.assert_stop(d, "C-BIAS")

    def test_f_tolerance_both_directions(self):
        d = copy.deepcopy(self.d)
        d["I3"]["predictions"][1]["f"][3] *= 1 + 1e-13
        self.assertTrue(vr.ctl_f(d)["pass"])
        d["I3"]["predictions"][1]["f"][3] *= 1 + 1e-11
        self.assertFalse(vr.ctl_f(d)["pass"])

    def test_gf_tolerance_both_directions(self):
        d = copy.deepcopy(self.d)
        d["I3"]["predictions"][2]["g_over_f_minus_1"][6] += 1e-13
        self.assertTrue(vr.ctl_gf(d)["pass"])
        d["I3"]["predictions"][2]["g_over_f_minus_1"][6] += 1e-11
        self.assertFalse(vr.ctl_gf(d)["pass"])

    def test_cov_asymmetric(self):
        d = copy.deepcopy(self.d)
        C = np.asarray(d["I4"]["matrices"][vr.COV_KEY])
        C[0, 1] *= 1 + 1e-9
        d["I4"]["matrices"][vr.COV_KEY] = C.tolist()
        self.assert_stop(d, "C-COV")

    def test_cov_not_pd(self):
        """Symmetric, with the declared diagonal, but not positive definite: only the Cholesky check catches it."""
        d = copy.deepcopy(self.d)
        C = np.asarray(d["I4"]["matrices"][vr.COV_KEY])
        C[0, 1] = C[1, 0] = 1.5 * math.sqrt(C[0, 0] * C[1, 1])
        d["I4"]["matrices"][vr.COV_KEY] = C.tolist()
        det = vr.ctl_cov(d)["detail"]
        self.assertEqual((det["asym_rel"], det["sigma_rel_dev"]), (0.0, 0.0))
        self.assertFalse(det["cholesky"])
        self.assert_stop(d, "C-COV")

    def test_cov_sigma_both_directions(self):
        d = copy.deepcopy(self.d)
        d["I4"]["relative_sigma"][vr.COV_KEY][2] *= 1 + 1e-13
        self.assertTrue(vr.ctl_cov(d)["pass"])
        d["I4"]["relative_sigma"][vr.COV_KEY][2] *= 1 + 1e-11
        self.assertFalse(vr.ctl_cov(d)["pass"])

    def test_finite_nan(self):
        d = copy.deepcopy(self.d)
        d["I1"]["truths"][3]["grade"]["z"][0] = float("nan")
        self.assertFalse(vr.ctl_finite(d)["pass"])

    def test_finite_zero_stat(self):
        d = copy.deepcopy(self.d)
        d["I6"]["relative_sigma"]["stat"][9] = 0.0
        self.assert_stop(d, "C-FINITE")

    def test_finite_clean(self):
        self.assertTrue(vr.ctl_finite(self.d)["pass"])

    def test_rho_control(self):
        c = vr.ctl_rho()
        self.assertTrue(c["pass"])
        self.assertEqual(c["detail"], {"returned_prior": vr.NOT_VALID, "recovered_truth": vr.VALID})

    def test_rho_control_fails_on_a_broken_classifier(self):
        orig = vr.cls_prior
        try:
            vr.cls_prior = lambda rhos, tau: vr.VALID
            self.assertFalse(vr.ctl_rho()["pass"])
            vr.cls_prior = lambda rhos, tau: vr.NOT_VALID
            self.assertFalse(vr.ctl_rho()["pass"])
        finally:
            vr.cls_prior = orig
        self.assertTrue(vr.ctl_rho()["pass"])

    def test_malformed_input_is_a_failed_control(self):
        d = copy.deepcopy(self.d)
        del d["I1"]["truths"][5]["p_parallel_lt_4p5"]
        rc, ro = self.run_read(d)
        self.assertEqual(rc, 3)
        self.assertNotIn("readings", ro)


class TestVPrior(unittest.TestCase):
    def test_spread_raw_and_sub(self):
        raw, sub = vr.spread([0.3, -0.4], [0.01, 0.03])
        self.assertAlmostEqual(raw, math.sqrt(0.125))
        self.assertAlmostEqual(sub, math.sqrt(0.105))

    def test_spread_sub_floor(self):
        self.assertEqual(vr.spread([0.01], [1.0])[1], 0.0)

    def test_rho4_undefined(self):
        r = vr.rho4((0.1, 0.1), (0.2, 0.0))
        self.assertIsNone(r["b_raw/g_sub"])
        self.assertAlmostEqual(r["b_raw/g_raw"], 0.5)
        self.assertEqual(vr.cls_prior(r, vr.TAU), vr.UNRES_NOISE)

    def test_rho4_pairs(self):
        r = vr.rho4((1.0, 2.0), (4.0, 8.0))
        self.assertEqual(r, {"b_raw/g_raw": 0.25, "b_raw/g_sub": 0.125, "b_sub/g_raw": 0.5, "b_sub/g_sub": 0.25})

    def test_tau_boundary(self):
        just_in = {k: 0.4999999 for k in ("a", "b", "c", "d")}
        at = {k: 0.5 for k in ("a", "b", "c", "d")}
        self.assertEqual(vr.cls_prior(just_in, 0.5), vr.VALID)
        self.assertEqual(vr.cls_prior(at, 0.5), vr.NOT_VALID)

    def test_mixed_is_unresolved(self):
        self.assertEqual(vr.cls_prior({"a": 0.49, "b": 0.51, "c": 0.4, "d": 0.4}, 0.5), vr.UNRES_NOISE)

    def test_tau_value_and_direction(self):
        self.assertEqual(vr.TAU, 0.5)
        self.assertEqual(vr.TAU_SENS, (1.0 / 3.0, 1.0))
        self.assertEqual(vr.cls_prior({"a": 1.0}, vr.TAU), vr.NOT_VALID)   # the result is the prior: not valid
        self.assertEqual(vr.cls_prior({"a": 0.0}, vr.TAU), vr.VALID)

    def test_returned_prior_is_not_valid_through_the_spreads(self):
        preds = {vr.PRIOR: {"R00": (1.0, 1.0, 0.0, 0.0)},
                 "genie_cv": {"R00": (1.0, 1.1, 0.0, 0.1)}, "nuwro": {"R00": (1.0, 0.95, 0.0, -0.05)}}
        sg, names = vr.prior_spread(preds, "R00")
        truths = [{"name": "a", "bias": [-0.1] + [0] * 15, "noise_sigma": [0] * 16, "own_vertex": None},
                  {"name": "b", "bias": [0.05] + [0] * 15, "noise_sigma": [0] * 16, "own_vertex": None}]
        sb, _ = vr.bias_spread(truths, "R00")
        r = vr.rho4(sb, sg)
        self.assertTrue(all(abs(v - 1.0) < 1e-9 for v in r.values()))
        self.assertEqual(vr.cls_prior(r, vr.TAU), vr.NOT_VALID)

    def test_prior_spread_variance(self):
        preds = {vr.PRIOR: {"R00": (2.0, 1.0, 0.01, 1.0)}, "genie_cv": {"R00": (2.0, 1.2, 0.03, -0.4)}}
        (raw, sub), names = vr.prior_spread(preds, "R00")
        dlt = 0.2
        sP, sG = 0.01 * 2.0 / 1.0, 0.03 * 2.0 / 1.2
        v = (1 + dlt) ** 2 * (sG ** 2 + sP ** 2)
        self.assertAlmostEqual(raw, dlt)
        self.assertAlmostEqual(sub, math.sqrt(dlt ** 2 - v))
        self.assertEqual(names, ["genie_cv"])

    def test_gibuu_generator_domain(self):
        preds = {vr.PRIOR: {"R00": (1, 1, 0, 0), "R04": (1, 1, 0, 0)},
                 "genie_cv": {"R00": (1, 1.1, 0, 0), "R04": (1, 1.1, 0, 0)}, "gibuu": {"R00": (1, 0.7, 0, 0)}}
        self.assertEqual(vr.prior_spread(preds, "R00")[1], ["genie_cv", "gibuu"])
        self.assertEqual(vr.prior_spread(preds, "R04")[1], ["genie_cv"])

    def test_gibuu_truth_domain(self):
        t = [{"name": "g", "own_vertex": "gibuu", "bias": [0.2] * 16, "noise_sigma": [0] * 16,
              "p_parallel_lt_4p5": {"cells": ["R00"]}},
             {"name": "n", "own_vertex": "nuwro", "bias": [0.1] * 16, "noise_sigma": [0] * 16}]
        self.assertEqual(vr.bias_spread(t, "R00")[1], ["g", "n"])
        self.assertEqual(vr.bias_spread(t, "R04")[1], ["n"])
        self.assertEqual(vr.bias_spread(t, "R04", gibuu_domain=False)[1], ["g", "n"])

    def test_bias_noise_subtracted(self):
        t = [{"name": "a", "own_vertex": None, "bias": [0.3] * 16, "noise_sigma": [0.1] * 16}]
        (raw, sub), _ = vr.bias_spread(t, "R02")
        self.assertAlmostEqual(raw, 0.3)
        self.assertAlmostEqual(sub, math.sqrt(0.09 - 0.01))

    def test_selection(self):
        d = make_inputs()
        self.assertEqual(sorted(t["name"] for t in vr.select_truths(d["I1"])), vr.TRUTH_NAMES)

    def test_v_prior_on_fixture(self):
        d = make_inputs()
        rows = vr.v_prior(d)
        self.assertEqual(len(rows["R00"]["truths"]), 10)
        self.assertEqual(len(rows["R04"]["truths"]), 8)
        self.assertEqual(rows["R00"]["generators"], ["genie_cv", "genie_mec", "nuwro", "gibuu"])
        self.assertEqual(rows["R04"]["generators"], ["genie_cv", "genie_mec", "nuwro"])
        self.assertEqual(len(rows["R04"]["print_only"]["gibuu_truths_on_all_cells"]["truths"]), 10)


class TestVAtlas(unittest.TestCase):
    def test_a1_boundary(self):
        self.assertTrue(vr.cls_atlas(5000.0, 0.01, {"a": 0.0})["A1"])
        self.assertFalse(vr.cls_atlas(4999.999, 0.01, {"a": 0.0})["A1"])

    def test_a2_boundary(self):
        self.assertTrue(vr.cls_atlas(1e6, 0.149999, {"a": 0.0})["A2"])
        self.assertFalse(vr.cls_atlas(1e6, 0.15, {"a": 0.0})["A2"])

    def test_a3_boundary_and_sign(self):
        self.assertTrue(vr.cls_atlas(1e6, 0.01, {"a": 2.0, "b": -2.0})["A3"])
        self.assertFalse(vr.cls_atlas(1e6, 0.01, {"a": 2.0000001})["A3"])
        self.assertFalse(vr.cls_atlas(1e6, 0.01, {"a": -2.0000001})["A3"])

    def test_class_needs_all_three(self):
        self.assertEqual(vr.cls_atlas(1e6, 0.01, {"a": 0.0})["class"], vr.VALID)
        for args in ((1e3, 0.01, {"a": 0.0}), (1e6, 0.2, {"a": 0.0}), (1e6, 0.01, {"a": 3.0})):
            self.assertEqual(vr.cls_atlas(*args)["class"], vr.NOT_VALID)

    def test_constants(self):
        self.assertEqual((vr.NEFF_MIN, vr.STAT_MAX, vr.Z_CLOSURE), (5000.0, 0.15, 2.0))

    def test_prior_truths_count_ungraded_do_not(self):
        d = make_inputs()
        d["I1"]["truths"][0]["grade"]["z"][1] = 2.5      # nominal (prior group, graded): counts
        d["I1"]["truths"][12]["grade"]["z"][2] = 9.0     # P1r (row 6, ungraded): does not count
        rows, per_truth = vr.v_atlas(d)
        self.assertFalse(rows["R01"]["A3"])
        self.assertTrue(rows["R02"]["A3"])
        self.assertEqual(len(rows["R02"]["z"]), 12)
        self.assertNotIn("P1r", per_truth)

    def test_gibuu_truths_graded_on_all_cells(self):
        d = make_inputs()
        d["I1"]["truths"][11]["grade"]["z"][4] = 2.5     # A7_gibuu on R04 (p_par >= 4.5): counts in A3
        rows, _ = vr.v_atlas(d)
        self.assertFalse(rows["R04"]["A3"])
        self.assertTrue(rows["R04"]["print_only"]["A3_without_gibuu_family_above_pz_4.5"])


class TestReading3(unittest.TestCase):
    def setUp(self):
        self.d = make_inputs(3)

    def test_departure_covariance(self):
        f, gP, VP, C, r, R = vr.departure(self.d)
        k = 5
        want = C[k, k] / gP[k] ** 2 + f[k] ** 2 * VP[k] / gP[k] ** 4
        self.assertAlmostEqual(R[k, k] / want, 1.0, places=12)
        self.assertAlmostEqual(R[2, 7] / (C[2, 7] / (gP[2] * gP[7])), 1.0, places=12)
        self.assertAlmostEqual(r[k], f[k] / gP[k] - 1.0)

    def test_quadrant_departure_linearization(self):
        f, gP, VP, C, r, R = vr.departure(self.d)
        idx = np.asarray([0, 1, 2, 3])
        rq, sq = vr.quadrant_departure(f, gP, VP, C, idx)
        F, G = f[idx].sum(), gP[idx].sum()
        self.assertAlmostEqual(rq, F / G - 1.0)
        J = np.full(4, 1.0 / G)
        var = J @ C[np.ix_(idx, idx)] @ J + (F / G ** 2) ** 2 * VP[idx].sum()
        self.assertAlmostEqual(sq / math.sqrt(var), 1.0, places=12)

    def test_contrast_uses_correlation(self):
        r = np.array([0.1, 0.0])
        R = np.array([[1.0, 0.8], [0.8, 1.0]])
        dl, s = vr.contrast(r, R, 0, 1)
        self.assertAlmostEqual(s, math.sqrt(0.4))
        self.assertAlmostEqual(dl, 0.1)

    def test_contrasts_only_valid_and_within_quadrant(self):
        valid = {"V-ATLAS": {"R00", "R01", "R03", "R08"}, "V-PRIOR": set()}
        out = vr.reading3(self.d, valid)
        qa = out["rules"]["V-ATLAS"]["quadrants"]
        self.assertEqual([p["pair"] for p in qa["Q1"]["contrasts"]], [["R00", "R01"], ["R00", "R03"], ["R01", "R03"]])
        self.assertEqual(qa["Q3"]["contrasts"], [])
        self.assertEqual(out["rules"]["V-ATLAS"]["n_contrasts"], 3)
        self.assertEqual(out["rules"]["V-PRIOR"]["n_contrasts"], 0)
        p = qa["Q1"]["contrasts"][0]
        self.assertEqual(p["axes"], ["eavail", "q3", "W"])
        self.assertAlmostEqual(p["resolved_3sigma"], 3.0 * p["sigma"])

    def test_vr1_no_class_no_sentence(self):
        out = vr.reading3(self.d, {"V-ATLAS": set(vr.CELLS), "V-PRIOR": set(vr.CELLS)})

        def keys(o):
            if isinstance(o, dict):
                for k, v in o.items():
                    yield k
                    yield from keys(v)
            elif isinstance(o, list):
                for v in o:
                    yield from keys(v)
        bad = {"class", "status", "statement", "sentence", "localized"}
        self.assertFalse(bad & set(keys(out)))
        self.assertNotIn("localized", json.dumps(out).replace("descriptive", ""))
        self.assertIn("descriptive only", out["label"])
        self.assertEqual(out["rules"]["V-ATLAS"]["n_contrasts"], 24)

    def test_zscore(self):
        self.assertEqual(vr.zscore(0.0, 0.0), 0.0)
        self.assertEqual(vr.zscore(-1.0, 0.0), -math.inf)
        self.assertEqual(vr.zscore(1.0, 0.5), 2.0)

    def test_differing_axes(self):
        self.assertEqual(vr.differing_axes(box(2), box(3)), ["W"])
        self.assertEqual(vr.differing_axes(box(13), box(14)), ["W"])

    def test_quadrant_of(self):
        self.assertEqual([vr.quadrant_of(box(k)) for k in (0, 4, 8, 12)], ["Q1", "Q2", "Q3", "Q4"])


if __name__ == "__main__":
    unittest.main()
