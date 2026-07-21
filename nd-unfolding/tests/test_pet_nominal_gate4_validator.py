"""Login-safe tests for the Gate-4 nominal validator (pet/validate_pet_nominal_gate4.py).

No GPU / no TF / no training. Synthetic nominal-result fixtures exercise the pure checks (finite/
coverage weights, strict MC index/order, marginal closure + normalization, cap-sensitivity, closure
composition, and the FREEZE), the assembled verdict, the atomic WORK-only receipt roundtrip, and
tamper rejection. No real training is run and nothing is published."""
import json
import os
import subprocess
import sys
import tempfile
import unittest

import numpy as np

ND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ND, "pet"))

import validate_pet_nominal_gate4 as g4  # noqa: E402  (login-safe)
import fullevent_fps_dataloader as fe    # noqa: E402


def frozen_observed(**over):
    o = {"estimator_fingerprint": g4.ESTIMATOR_FINGERPRINT, "bkg_mode": g4.BKG_MODE,
         "edges_pt": g4.FROZEN["edges_pt"], "edges_pparallel": g4.FROZEN["edges_pparallel"],
         "bin_order": g4.FROZEN["bin_order"], "seed_policy": g4.FROZEN["seed_policy"]}
    o.update(over)
    return o


def good_report(**over):
    rng = np.random.default_rng(0)
    n = 50
    h_truth = rng.random(g4.N_CELLS); h_rw = h_truth.copy()          # exact closure -> L1=0
    kw = dict(result_meta={"path": "/x/nom.npz", "sha256": "abc"},
              frozen_observed=frozen_observed(),
              weights_push=(rng.random(n) + 0.5), imc=np.arange(n), n_full=1000,
              marginal=(h_truth, h_rw), normalization=(100.0, 100.0), saturation_frac=0.0,
              closure=(True, True, True), observed_at_utc="2026-07-21T00:00:00Z")
    kw.update(over)
    return g4.build_gate4_report(**kw)


class FrozenContract(unittest.TestCase):
    def test_geometry_matches_edges(self):
        self.assertEqual(g4.N_PT_BINS, len(fe.CANONICAL_PT_EDGES) - 1)
        self.assertEqual(g4.N_PPAR_BINS, len(fe.CANONICAL_PPARALLEL_EDGES) - 1)
        self.assertEqual(g4.N_CELLS, g4.N_PT_BINS * g4.N_PPAR_BINS)
        self.assertEqual(g4.N_CELLS, 285)

    def test_freeze_pass(self):
        self.assertTrue(g4.check_freeze(frozen_observed())[0])

    def test_freeze_fingerprint_tamper(self):
        self.assertFalse(g4.check_freeze(frozen_observed(estimator_fingerprint="pet-reduced-fps-cross"))[0])

    def test_freeze_bkg_mode_tamper(self):
        self.assertFalse(g4.check_freeze(frozen_observed(bkg_mode="purity"))[0])

    def test_freeze_edges_tamper(self):
        self.assertFalse(g4.check_freeze(frozen_observed(edges_pt=[0.0, 1.0, 4.5]))[0])

    def test_freeze_seed_policy_tamper(self):
        sp = dict(g4.FROZEN["seed_policy"]); sp["estimator_seed"] = 7
        self.assertFalse(g4.check_freeze(frozen_observed(seed_policy=sp))[0])

    def test_freeze_central_vector_len(self):
        ok, _ = g4.check_freeze(frozen_observed(central_vector=np.ones(g4.N_CELLS)))
        self.assertTrue(ok)
        bad, _ = g4.check_freeze(frozen_observed(central_vector=np.ones(g4.N_CELLS - 1)))
        self.assertFalse(bad)

    def test_freeze_central_vector_nonfinite(self):
        cv = np.ones(g4.N_CELLS); cv[3] = np.inf
        self.assertFalse(g4.check_freeze(frozen_observed(central_vector=cv))[0])


class Weights(unittest.TestCase):
    def test_finite_coverage_pass(self):
        self.assertTrue(g4.check_weights_finite_coverage(np.array([1.0, 0.5, 2.0]), 3)[0])

    def test_nonfinite_fail(self):
        self.assertFalse(g4.check_weights_finite_coverage(np.array([1.0, np.nan]))[0])

    def test_negative_fail(self):
        self.assertFalse(g4.check_weights_finite_coverage(np.array([1.0, -0.1]))[0])

    def test_all_zero_fail(self):
        self.assertFalse(g4.check_weights_finite_coverage(np.zeros(4))[0])

    def test_coverage_mismatch_fail(self):
        self.assertFalse(g4.check_weights_finite_coverage(np.ones(3), 4)[0])


class IndexOrder(unittest.TestCase):
    def test_sorted_unique_pass(self):
        self.assertTrue(g4.check_mc_index_order(np.array([0, 2, 5, 9]), 10)[0])

    def test_unsorted_fail(self):
        self.assertFalse(g4.check_mc_index_order(np.array([0, 5, 2]), 10)[0])

    def test_duplicate_fail(self):
        self.assertFalse(g4.check_mc_index_order(np.array([0, 2, 2, 5]), 10)[0])

    def test_out_of_range_fail(self):
        self.assertFalse(g4.check_mc_index_order(np.array([0, 2, 11]), 10)[0])


class MarginalNormCap(unittest.TestCase):
    def test_marginal_exact_pass(self):
        h = np.random.default_rng(1).random(20)
        self.assertTrue(g4.check_marginal_closure(h, h.copy())[0])

    def test_marginal_large_l1_fail(self):
        a = np.zeros(4); a[0] = 1.0; b = np.zeros(4); b[3] = 1.0
        self.assertFalse(g4.check_marginal_closure(a, b)[0])

    def test_normalization_pass(self):
        self.assertTrue(g4.check_normalization(100.0, 100.0)[0])

    def test_normalization_fail(self):
        self.assertFalse(g4.check_normalization(110.0, 100.0)[0])

    def test_cap_pass(self):
        self.assertTrue(g4.check_cap_sensitivity(0.0)[0])

    def test_cap_fail(self):
        self.assertFalse(g4.check_cap_sensitivity(0.05)[0])

    def test_cap_missing_fail(self):
        self.assertFalse(g4.check_cap_sensitivity(None)[0])


class ClosureComposition(unittest.TestCase):
    def test_all_pass(self):
        self.assertTrue(g4.check_closure_verdicts(True, True, True)[0])

    def test_ordinary_fail(self):
        self.assertFalse(g4.check_closure_verdicts(False, True, True)[0])

    def test_fullevent_no_recover_fail(self):
        self.assertFalse(g4.check_closure_verdicts(True, True, False)[0])

    def test_closure_scripts_frozen(self):
        self.assertTrue(g4.FROZEN["closure_scripts"]["ordinary"].endswith("closure_fullevent_fps.py"))
        self.assertTrue(g4.FROZEN["closure_scripts"]["omitted_muon_stress"]
                        .endswith("stress_closure_muon.py"))
        for rel in g4.FROZEN["closure_scripts"].values():
            self.assertTrue(os.path.exists(os.path.join(os.path.dirname(ND), rel)), rel)


class ReportVerdict(unittest.TestCase):
    def test_all_pass(self):
        payload, verdict = good_report()
        self.assertTrue(verdict)
        self.assertEqual(payload["verdict"], "PASS")
        self.assertFalse(payload["nominal_pet_training_allowed"])
        self.assertTrue(all(payload["component_verdicts"].values()))

    def test_freeze_failure_fails_verdict(self):
        _, verdict = good_report(frozen_observed=frozen_observed(bkg_mode="purity"))
        self.assertFalse(verdict)

    def test_weights_failure_fails_verdict(self):
        _, verdict = good_report(weights_push=np.array([1.0, np.nan, 2.0]), imc=np.arange(3),
                                 n_full=10)
        self.assertFalse(verdict)

    def test_index_failure_fails_verdict(self):
        _, verdict = good_report(imc=np.array([2, 1, 0]))
        self.assertFalse(verdict)

    def test_closure_failure_fails_verdict(self):
        _, verdict = good_report(closure=(False, True, True))
        self.assertFalse(verdict)

    def test_receipt_roundtrip_atomic(self):
        payload, _ = good_report()
        with tempfile.TemporaryDirectory() as td:
            work = os.path.join(td, "gate4_work.json")
            g4.write_work_receipt(work, payload)
            self.assertEqual(os.listdir(td), ["gate4_work.json"])       # WORK only; temp cleaned
            with open(work) as f:
                r = json.load(f)
            self.assertEqual(r["verdict"], "PASS")
            self.assertEqual(r["receipt_schema"], "pet-fullevent-gate4-nominal-validation-v1")
            self.assertFalse(r["nominal_pet_training_allowed"])
            self.assertEqual(r["frozen_contract"]["n_reported_cells"], 285)

    def test_no_publication_on_failure(self):
        payload, verdict = good_report(closure=(False, True, True))
        self.assertFalse(verdict)
        with tempfile.TemporaryDirectory() as td:
            work = os.path.join(td, "fail.json")
            g4.write_work_receipt(work, payload)
            self.assertEqual(os.listdir(td), ["fail.json"])
            with open(work) as f:
                self.assertEqual(json.load(f)["verdict"], "FAIL")


class SyntaxAndImport(unittest.TestCase):
    def test_byte_compiles(self):
        r = subprocess.run([sys.executable, "-m", "py_compile",
                            os.path.join(ND, "pet", "validate_pet_nominal_gate4.py")],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
