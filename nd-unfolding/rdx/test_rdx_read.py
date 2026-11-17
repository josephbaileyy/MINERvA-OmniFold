#!/usr/bin/env python3
"""Tests of rdx_read.py (RDX-DECLARATION.md §4), on synthetic products; each guard in the direction it acts and in
the other. The cell integrals are the identity on 16-cell arrays, so every reading is set by hand."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rdx_read as R  # noqa: E402

SPEC = R.tasks()
PINS = {k.lstrip("./"): v for k, v in R.sums(R.SUMS).items()}
PINS["ratio"] = R.sums(R.PVL_SUMS)[R.RATIO_KEY]
PHI = np.full(16, 0.001)
SIGMA = np.full(16, 0.02)
IDENT = lambda x: np.asarray(x, float)  # noqa: E731
BASE = np.linspace(1.0, 2.5, 16)


def meta_for(task: str) -> dict:
    s = SPEC[task]
    lat = s["inputs"] == "lat_zero"
    wide = s["features"] == "wide"
    instrumented = wide or s["weight"] != "none" or s["transfer"]
    rdx = {"regressor_features": s["features"], "regressor_weight": s["weight"], "truth": s["truth"],
           "transfer": s["transfer"], "truthx_permute": s["permute"],
           "truthx_sidecar_sha256": PINS["truthx_RDX_ALL.npz"] if wide else None,
           "fit_calls": R.ITERS if instrumented else None, "predict_calls": R.ITERS if wide else 0}
    if s["transfer"]:
        rdx["transfer_records"] = [{"iteration": k, "cell_bias": [0.0] * 16} for k in range(R.ITERS)]
    return {"schema": "pvl-unfold/1", "rung": "L-5D-PV", "arm": "e", "features": list(R.AXES5), "closure": s["closure"],
            "ratio_sha256": PINS["ratio"], "estimator_seed": 42, "iters": 5, "threads": 32,
            "input_npz_sha256": PINS["lat_zero.npz" if lat else "lat_RDX_ALL.npz"],
            "bkg_dump_sha256": PINS["lat_zero_bkg.npz" if lat else "lat_RDX_ALL_bkg.npz"],
            "estimator_params": {"n_estimators": 100}, "refinement": {"ran": not s["closure"],
                                                                         "classifier_params": {"a": 1}},
            "rdx": rdx}


def clean_prod() -> dict:
    """Every product at BASE (so every difference is 0), closures with truth BASE."""
    return {t: (meta_for(t), BASE.copy(), BASE.copy() if SPEC[t]["closure"] else None) for t in SPEC}


def write_all(d: Path, prod: dict, log_extra: str = "") -> list:
    lines = []
    for t, (meta, x, xt) in prod.items():
        arrays = {"meta": np.array(json.dumps(meta)), "xsec_flat": x}
        if xt is not None:
            arrays["xtrue_flat"] = xt
        np.savez(d / f"{t}.npz", **arrays)
        lines.append(f"{R.sha256(d / f'{t}.npz')}  /pscratch/sd/j/josephrb/rdx-20261112b/out/products/{t}.npz")
    a = d / "rdx_s3_a.out"
    b = d / "rdx_s3_b.out"
    a.write_text("[rdx-arms] start\n" + "\n".join(lines[:8]) + "\n" + log_extra)
    b.write_text("\n".join(lines[8:]) + "\n")
    return [a, b]


def bump(x, cells, by):
    y = np.array(x, float)
    y[list(cells)] *= 1.0 + by
    return y


class Guards(unittest.TestCase):
    def test_a_clean_set_is_checked_and_read(self):
        with tempfile.TemporaryDirectory() as d:
            logs = write_all(Path(d), clean_prod())
            prod, got = R.checked_products(Path(d), logs, SPEC, PINS)
        self.assertEqual(sorted(prod), sorted(SPEC))
        out = R.read(prod, IDENT, PHI, SIGMA)
        self.assertEqual(out["outcome"]["outcome"], "LICENSED")
        self.assertEqual(out["outcome"]["statement"], R.SENTENCE)

    def test_a_sha_that_is_not_the_jobs_refuses(self):
        prod = clean_prod()
        with tempfile.TemporaryDirectory() as d:
            logs = write_all(Path(d), prod)
            np.savez(Path(d) / "X1.npz", meta=np.array(json.dumps(prod["X1"][0])), xsec_flat=BASE * 1.01)
            with self.assertRaisesRegex(SystemExit, "X1: sha256 .* is not the .* its job printed"):
                R.checked_products(Path(d), logs, SPEC, PINS)

    def test_the_logs_must_print_each_task_exactly_once(self):
        with tempfile.TemporaryDirectory() as d:
            logs = write_all(Path(d), clean_prod())
            text = logs[1].read_text().splitlines()
            logs[1].write_text("\n".join(text[1:]) + "\n")
            with self.assertRaisesRegex(SystemExit, "print no sha256 for"):
                R.log_shas(logs, list(SPEC))
            logs[1].write_text("\n".join(text) + "\n" + text[0] + "\n")
            with self.assertRaisesRegex(SystemExit, "more than once"):
                R.log_shas(logs, list(SPEC))
            logs[1].write_text("\n".join(text) + "\n" + "0" * 64 + "  /x/products/X9.npz\n")
            with self.assertRaisesRegex(SystemExit, "not a declared task"):
                R.log_shas(logs, list(SPEC))
            logs[1].write_text("\n".join(text) + "\nnoise: 0123  products/X1.npz\n")
            self.assertEqual(sorted(R.log_shas(logs, list(SPEC))), sorted(SPEC))

    def test_a_product_that_is_not_its_declared_task_refuses(self):
        for task, key, value in (("X1w", ("rdx", "regressor_weight"), "none"), ("X1p", ("rdx", "truthx_permute"), None),
                                 ("X0_lat", ("bkg_dump_sha256",), PINS["lat_RDX_ALL_bkg.npz"]),
                                 ("X1c", ("closure",), False), ("X1", ("rdx", "truthx_sidecar_sha256"), None),
                                 ("X0t", ("rdx", "fit_calls"), None), ("X1", ("estimator_seed",), 7),
                                 ("X1q", ("rdx", "truth"), "a7_gibuu"), ("X0g", ("ratio_sha256",), "0" * 64)):
            prod = clean_prod()
            m = prod[task][0]
            tgt = m["rdx"] if key[0] == "rdx" else m
            tgt[key[-1]] = value
            with tempfile.TemporaryDirectory() as d:
                logs = write_all(Path(d), prod)
                with self.assertRaisesRegex(SystemExit, f"{task}: "):
                    R.checked_products(Path(d), logs, SPEC, PINS)

    def test_parameters_must_be_x0s(self):
        prod = clean_prod()
        prod["X1"][0]["estimator_params"] = {"n_estimators": 99}
        self.assertTrue(R.identity_problems(prod["X1"][0], SPEC["X1"], PINS, prod["X0"][0]))
        self.assertFalse(R.identity_problems(prod["X1p"][0], SPEC["X1p"], PINS, prod["X0"][0]))

    def test_a_transfer_step_needs_five_records(self):
        prod = clean_prod()
        prod["X1t"][0]["rdx"]["transfer_records"].pop()
        self.assertIn("a transfer step must carry one transfer record per iteration",
                      R.identity_problems(prod["X1t"][0], SPEC["X1t"], PINS, prod["X0"][0]))

    def test_nc_x_refuses_and_reads_nothing(self):
        prod = clean_prod()
        prod["X0_lat"] = (prod["X0_lat"][0], np.nextafter(BASE, 3.0), None)
        with self.assertRaisesRegex(SystemExit, "NC-X"):
            R.read(prod, IDENT, PHI, SIGMA)

    def test_phi_and_sigma_come_from_the_committed_records(self):
        self.assertEqual(R.RR.I0.name, "i0.json")
        self.assertEqual(R.RR.F1_READOUT.name, "fd_f1_readout.json")
        self.assertEqual(R.RR.CMODEL_JSON.name, "cmodel_5d.json")
        self.assertNotIn("--i0", Path(R.__file__).read_text())
        self.assertNotIn("--f1-readout", Path(R.__file__).read_text())
        with self.assertRaisesRegex(SystemExit, "16 positive values"):
            R.read(clean_prod(), IDENT, PHI, np.zeros(16))


class Readings(unittest.TestCase):
    def test_the_refit_null_at_w2_makes_r1_unattributable(self):
        prod = clean_prod()
        prod["X1p"] = (prod["X1p"][0], bump(BASE, [3], 0.02), None)
        out = R.read(prod, IDENT, PHI, SIGMA)
        self.assertEqual(out["R1p"]["class"], "W2")
        self.assertEqual(out["outcome"]["outcome"], "REFIT NULL W2")
        self.assertEqual(out["outcome"]["cells"], ["R03"])

    def test_an_excess_beyond_half_sigma_is_a_named_sensitivity(self):
        prod = clean_prod()
        prod["X1"] = (prod["X1"][0], bump(BASE, [5], 0.012), None)
        out = R.read(prod, IDENT, PHI, SIGMA)
        self.assertEqual(out["R1"]["cells_excess_beyond_half_sigma"], ["R05"])
        self.assertEqual(out["outcome"]["outcome"], "STATED SENSITIVITY")
        prod["X1"] = (prod["X1"][0], bump(BASE, [5], 0.009), None)
        self.assertEqual(R.read(prod, IDENT, PHI, SIGMA)["outcome"]["outcome"], "LICENSED")

    def test_the_excess_is_beyond_the_null(self):
        prod = clean_prod()
        prod["X1"] = (prod["X1"][0], bump(BASE, [5], 0.012), None)
        prod["X1p"] = (prod["X1p"][0], bump(BASE, [5], 0.008), None)
        out = R.read(prod, IDENT, PHI, SIGMA)
        self.assertEqual(out["R1p"]["class"], "W1")
        self.assertEqual(out["R1"]["cells_excess_beyond_half_sigma"], [])
        self.assertEqual(out["outcome"]["outcome"], "LICENSED")

    def test_r4_reads_each_closure_against_its_own_truth(self):
        prod = clean_prod()
        prod["X1g"] = (prod["X1g"][0], bump(BASE, [9], 0.02), BASE.copy())
        out = R.read(prod, IDENT, PHI, SIGMA)
        self.assertEqual(out["R4"]["gibuu"]["class"], "W2")
        self.assertEqual(out["outcome"]["outcome"], "STATED SENSITIVITY")
        self.assertEqual(out["outcome"]["cells"]["R4_gibuu"], ["R09"])
        prod = clean_prod()
        prod["X1g"] = (prod["X1g"][0], bump(BASE, [9], 0.02), bump(BASE, [9], 0.02))
        self.assertEqual(R.read(prod, IDENT, PHI, SIGMA)["R4"]["gibuu"]["class"], "W0")

    def test_r4_at_the_prior_subtracts_the_refit_null(self):
        prod = clean_prod()
        prod["X1c"] = (prod["X1c"][0], bump(BASE, [2], 0.02), BASE.copy())
        out = R.read(prod, IDENT, PHI, SIGMA)
        self.assertEqual(out["R4"]["prior"]["class"], "W2")
        prod["X1pc"] = (prod["X1pc"][0], bump(BASE, [2], 0.02), BASE.copy())
        out = R.read(prod, IDENT, PHI, SIGMA)
        self.assertEqual(out["R4"]["prior"]["class"], "W0")
        self.assertEqual(out["outcome"]["outcome"], "LICENSED")

    def test_r4_q3_and_the_weight_at_the_prior(self):
        prod = clean_prod()
        prod["X1q"] = (prod["X1q"][0], bump(BASE, [0], 0.02), BASE.copy())
        self.assertEqual(R.read(prod, IDENT, PHI, SIGMA)["outcome"]["cells"]["R4_q3"], ["R00"])
        prod = clean_prod()
        prod["X1wc"] = (prod["X1wc"][0], bump(BASE, [1], 0.02), BASE.copy())
        out = R.read(prod, IDENT, PHI, SIGMA)
        self.assertEqual(out["R4"]["weight_at_prior"]["class"], "W2")
        self.assertEqual(out["outcome"]["outcome"], "LICENSED", "the weight qualifies; it is not an outcome change")

    def test_r2_classes_x1w_against_x1(self):
        prod = clean_prod()
        prod["X1w"] = (prod["X1w"][0], bump(BASE, [4], 0.003), None)
        out = R.read(prod, IDENT, PHI, SIGMA)
        self.assertEqual(out["R2"]["class"], "W1")
        self.assertEqual(out["outcome"]["outcome"], "LICENSED")

    def test_r3_reads_the_last_iteration_and_the_difference(self):
        prod = clean_prod()
        recs = prod["X1t"][0]["rdx"]["transfer_records"]
        recs[0]["cell_bias"] = [0.5] * 16
        recs[-1]["cell_bias"] = [0.0] * 15 + [0.03]
        out = R.read(prod, IDENT, PHI, SIGMA)
        self.assertEqual(out["R3"]["X1t"]["class"], "T2")
        self.assertEqual(out["R3"]["X1t"]["cells_beyond_half_sigma"], ["R15"])
        self.assertEqual(out["R3"]["X0t"]["class"], "T0")
        self.assertEqual(out["R3"]["difference"]["class"], "T2")
        recs[-1]["cell_bias"] = [None] + [0.0] * 15
        diff = R.read(prod, IDENT, PHI, SIGMA)["R3"]["difference"]
        self.assertEqual((diff["class"], diff["cells_beyond_half_sigma"]), ("T2", ["R00"]))

    def test_r3_reports_whether_the_probe_left_the_loop_untouched(self):
        prod = clean_prod()
        self.assertTrue(R.read(prod, IDENT, PHI, SIGMA)["R3"]["loop_untouched"]["X1t_equals_X1"])
        prod["X1t"] = (prod["X1t"][0], np.nextafter(BASE, 3.0), None)
        self.assertFalse(R.read(prod, IDENT, PHI, SIGMA)["R3"]["loop_untouched"]["X1t_equals_X1"])

    def test_a_nonpositive_reference_refuses(self):
        prod = clean_prod()
        z = BASE.copy()
        z[7] = 0.0
        prod["X0"] = (prod["X0"][0], z, None)
        prod["X0_lat"] = (prod["X0_lat"][0], z.copy(), None)
        with self.assertRaisesRegex(SystemExit, "positive reference"):
            R.read(prod, IDENT, PHI, SIGMA)


if __name__ == "__main__":
    unittest.main()
