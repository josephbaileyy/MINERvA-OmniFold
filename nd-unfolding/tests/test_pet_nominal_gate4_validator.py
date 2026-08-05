"""Login-safe tests for the Gate-4 nominal validator (pet/validate_pet_nominal_gate4.py).

No GPU / no TF / no training. Synthetic nominal-result fixtures exercise the pure checks (finite/
coverage weights, strict MC index/order, marginal closure, cap-sensitivity, target provenance,
closure composition, and the FREEZE), the assembled verdict, the atomic WORK-only receipt roundtrip,
and tamper rejection. No real training is run and nothing is published.

EDITED AT THE 2026-07-31 GATE-4 RE-ISSUE (RESTORE-2026-08-03.md Step 2b). This file was byte-frozen
by `p3f-pet-gate4-launch-code-gate-20260721.json`, and the 07-29 B1 patch deliberately left it
untouched so its binding was not voided for no reason. The re-issue re-freezes it anyway, which is
the window Step 2b reserved for two things it had been blocking:

  * `check_normalization` -- the legacy truth-level `sum_w_push/sum_w ~ 1` primitive -- is RETIRED.
    It was kept alive purely because `test_normalization_pass` / `test_normalization_fail` here
    pinned its two-argument signature; it had no caller of its own and its target is
    acceptance-dependent, so it could never be the gate. The two tests now pin the real gate
    (`check_fold_forward_ratio`) and the arithmetic lives in `_ratio_dev`.
  * `check_freeze` now FAILS on an absent central vector or reported-bin mask instead of skipping
    those checks, so the helper below must supply them. Audit B2: the shipped CLI never populated
    either key, so the 266/285 reporting mask was untouched by the gate.

WHY THE HELPERS BUILD FULL EVIDENCE. `build_gate4_report` no longer skips a component whose argument
is None -- it emits a failing `<component>:evidence_supplied` check. That is the fix for audit B2
(four physics checks and three freeze checks silently not executing while the receipt read
`verdict PASS, n_failed 0` on `|N(1,0.3)|` noise), so `good_report()` has to hand over every piece
of evidence a real validation run would, and the tamper tests remove exactly one at a time."""
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


def reported_mask(n_true=266):
    m = np.zeros(g4.N_CELLS, bool)
    m[:n_true] = True
    return m


def central_vector(mask=None, seed=5):
    """A plausible 285-cell central vector: populated inside the mask, exactly zero outside."""
    mask = reported_mask() if mask is None else np.asarray(mask, bool)
    cv = np.zeros(g4.N_CELLS)
    cv[mask] = np.random.default_rng(seed).random(int(mask.sum())) + 0.1
    return cv / cv.sum()


def frozen_observed(**over):
    """The values a REAL artifact carries. Deliberately not built from FROZEN's own entries for the
    four that used to be: audit B2 found `check_freeze` comparing FROZEN to FROZEN for edges_pt,
    edges_pparallel, bin_order and seed_policy. They are retyped here so a drift in FROZEN shows up
    as a test failure rather than being absorbed."""
    m = reported_mask()
    o = {"estimator_fingerprint": "pet-fullevent-fps-v1", "bkg_mode": "negweight-refined",
         "edges_pt": [0, 0.07, 0.15, 0.25, 0.33, 0.4, 0.47, 0.55, 0.7, 0.85, 1.0, 1.25, 1.5,
                      2.5, 4.5, 30.0],
         "edges_pparallel": [0.0, 0.75, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 7.0, 8.0,
                             9.0, 10.0, 15.0, 20.0, 40.0, 60.0, 120.0],
         "bin_order": "pt-major row-major: cell = i_pt * n_pparallel_bins + i_pparallel",
         "seed_policy": {"estimator_seed": 42, "subsample_seed": 0, "niter": 2, "epochs": 8,
                         "train_events": 2000000},
         # J01: the event-feature schema the run was trained on, retyped for the same reason as
         # the edges above -- reading it out of FROZEN would make `freeze:event_features_reco` a
         # comparison of FROZEN with itself, which is the exact defect audit B2 found in four
         # other freeze checks. This literal IS the publication schema; if the loader's
         # DEFAULT_EVT_FEATURES moves, this test must fail rather than follow it.
         "event_features_reco": ["pt", "pparallel", "mu_px", "mu_py", "mu_pz", "mu_E",
                                 "mu_cos_phi", "mu_sin_phi", "mu_qp", "mu_minos_ok",
                                 "vtx_x", "vtx_y", "vtx_z"],
         "event_features_truth": ["pt", "pparallel"],
         "reco_cloud_cols": ["E", "pos", "z", "view", "time"],
         "central_vector": central_vector(m), "reported_bin_mask": m}
    o.update(over)
    return o


def good_target(**over):
    t = {"target_mode": "negweight-refined", "refinement": "stay-positive (arXiv:2505.03724)",
         "refinement_is_learned_production": True, "signed_target_hash": "a" * 64,
         "pot_scale": 0.2166, "refined_sum": 3.9e6, "refined_min": 0.0}
    t.update(over)
    return t


def ordinary_report(**over):
    h = np.random.default_rng(0).random(g4.N_CELLS)
    r = {"report_schema": g4.ORDINARY_CLOSURE_SCHEMA, "verdict": "PASS", "pass": True,
         # D2 (2026-08-04): the ordinary closure defaults to mc-only and must SAY what it supports.
         # A report lacking these fields cannot be composed as evidence.
         "bkg_mode": "mc-only", "is_synthetic_fixture": False,
         "mc_only": True, "measured_target_constructed": False, "refinement_invoked": False,
         "closure_class": "mc-self-consistency-identity", "is_powered_closure": False,
         "marginal_l1": 0.0, "marginal_h_truth": [float(x) for x in h],
         "marginal_h_reweighted": [float(x) for x in h],
         "edges_pt": g4.FROZEN["edges_pt"], "edges_pparallel": g4.FROZEN["edges_pparallel"],
         # J01: which estimator this closure is evidence about.
         "event_features_reco": list(g4.FROZEN["event_features_reco"]),
         "event_features_truth": list(g4.FROZEN["event_features_truth"]),
         "push_median": 1.001, "push_finite": True, "l1_max": 0.10, "push_med_tol": 0.15}
    r.update(over)
    return r


def powered_vectors(gap=0.30, floor_frac=0.05, resid_frac=0.10):
    """Four unit-normalized 285-cell spectra with EXACTLY prescribed pairwise L1 distances.

    Built from zero-sum perturbations of a flat base so gap/floor/residual are known in closed form
    and the fixture cannot accidentally satisfy the criteria for the wrong reason.
    """
    n = g4.N_CELLS
    base = np.full(n, 1.0 / n)

    def pert(target_l1, offset, k=100):
        d = np.zeros(n)
        d[offset:offset + k] += target_l1 / (2 * k)
        d[offset + k:offset + 2 * k] -= target_l1 / (2 * k)
        return d                                    # sums to 0, |d|_1 == target_l1

    prior = base.copy()
    target = base + pert(gap, 0)
    untilted = base + pert(gap * floor_frac, 40)
    unfolded = target + pert(gap * resid_frac, 80)
    return prior, target, unfolded, untilted


def powered_report(**over):
    """The D2 injected truth-reweight RECOVERY closure. The identity closure cannot substitute for
    it: pseudo-data IS the MC there, so a constant estimator optimizes it.

    Carries real spectra, because Gate-4 recomputes every metric from them rather than reading the
    verdict. The `metrics` block is derived from the same vectors so it agrees by construction.
    """
    prior, target, unfolded, untilted = powered_vectors()
    gap = float(np.abs(prior - target).sum())
    floor = float(np.abs(prior - untilted).sum())
    resid = float(np.abs(unfolded - target).sum())
    P = g4.FROZEN["powered_closure"]
    sp = g4.FROZEN["seed_policy"]
    r = {"report_schema": P["report_schema"], "verdict": "PASS",
         "is_powered_closure": True, "recovery_criteria_met": True,
         "closure_class": "injected-truth-reweight-recovery",
         "h_prior": [float(x) for x in prior], "h_target": [float(x) for x in target],
         "h_unfolded": [float(x) for x in unfolded], "h_untilted": [float(x) for x in untilted],
         "bin_order": g4.FROZEN["bin_order"],
         "edges_pt": list(g4.FROZEN["edges_pt"]),
         "edges_pparallel": list(g4.FROZEN["edges_pparallel"]),
         "metrics": {"gap": gap, "floor": floor, "residual": resid,
                     "floor_over_gap": floor / gap, "residual_over_gap": resid / gap,
                     "recovery": 1.0 - resid / gap},
         "injection": {"form": "1 + A*tanh((pT - p50)/IQR), normalized to unit mean",
                       "amplitude": P["amplitude"], "rate_preserving": True},
         "samples": {"half_size": P["half_size"], "split_seed": P["split_seed"], "disjoint": True},
         "configuration": {k: sp[k] for k in ("niter", "epochs", "estimator_seed",
                                              "subsample_seed")},
         "estimator_fingerprint": "pet-fullevent-fps-v1",
         "event_features_reco": list(g4.FROZEN["event_features_reco"]),
         "event_features_truth": list(g4.FROZEN["event_features_truth"]),
         "reco_leg_weight_used": "w_reco", "mc_only": True,
         "input_identity_hashes": {"sig": "1" * 64}}
    r.update(over)
    return r


def stress_report(**over):
    r = {"report_schema": g4.STRESS_CLOSURE_SCHEMA, "verdict": "PASS", "pass": True,
         "recoil_only_fails_to_recover": True, "fullevent_recovers": True}
    r.update(over)
    return r


def good_report(**over):
    rng = np.random.default_rng(0)
    n = 50
    h_truth = rng.random(g4.N_CELLS); h_rw = h_truth.copy()          # exact closure -> L1=0
    m = reported_mask(); cv = central_vector(m)
    spectra = (cv, m, 0.0)
    kw = dict(result_meta={"path": "/x/nom.npz", "sha256": "abc"},
              frozen_observed=frozen_observed(central_vector=cv, reported_bin_mask=m),
              weights_push=(rng.random(n) + 0.5), imc=np.arange(n), n_full=1000,
              n_expected_subsample=n,
              marginal=(h_truth, h_rw), saturation_frac=0.0,
              fold_forward=(113.5, 100.0, 1.135), fold_forward_driver=(113.5, 100.0, 1.135),
              spectra=spectra, spectra_driver=spectra, target=good_target(),
              closure=(True, True, True),
              closure_reports=(ordinary_report(), stress_report(), powered_report()),
              observed_at_utc="2026-07-21T00:00:00Z")
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

    def test_freeze_niter_tamper(self):
        """Audit B2's headline failure scenario: `--niter 1 --epochs 2` validated PASS against a
        receipt that recorded niter 2 / epochs 8, because the validator compared its own constant to
        itself. The artifact now carries what the run did, so this must fail."""
        sp = dict(g4.FROZEN["seed_policy"]); sp["niter"] = 1; sp["epochs"] = 2
        ok, checks = g4.check_freeze(frozen_observed(seed_policy=sp))
        self.assertFalse(ok)
        self.assertFalse([c for c in checks if c["name"] == "freeze:seed_policy"][0]["ok"])

    def test_freeze_central_vector_len(self):
        ok, _ = g4.check_freeze(frozen_observed())
        self.assertTrue(ok)
        bad, _ = g4.check_freeze(frozen_observed(central_vector=np.ones(g4.N_CELLS - 1)))
        self.assertFalse(bad)

    def test_freeze_central_vector_nonfinite(self):
        cv = central_vector(); cv[3] = np.inf
        self.assertFalse(g4.check_freeze(frozen_observed(central_vector=cv))[0])

    def test_freeze_absent_central_vector_fails_not_skips(self):
        """Audit B2. main() never populated this key, so the check did not run -- and a check that
        does not run must not read as green."""
        ok, checks = g4.check_freeze(frozen_observed(central_vector=None))
        self.assertFalse(ok)
        names = {c["name"] for c in checks}
        self.assertIn("freeze:central_vector_present", names)
        self.assertNotIn("freeze:central_vector_len", names)

    def test_freeze_absent_reported_mask_fails_not_skips(self):
        ok, checks = g4.check_freeze(frozen_observed(reported_bin_mask=None))
        self.assertFalse(ok)
        self.assertIn("freeze:reported_mask_present", {c["name"] for c in checks})

    def test_freeze_reported_mask_len(self):
        self.assertFalse(g4.check_freeze(frozen_observed(reported_bin_mask=np.ones(10, bool)))[0])

    def test_freeze_reported_mask_empty_fails(self):
        self.assertFalse(
            g4.check_freeze(frozen_observed(reported_bin_mask=np.zeros(g4.N_CELLS, bool)))[0])

    def test_freeze_central_vector_must_be_zero_outside_the_mask(self):
        """Order agreement between the two 285-vectors: a reshuffled central vector populates cells
        the mask calls empty, which is exactly the silent reshape the freeze exists to catch."""
        m = reported_mask()
        cv = central_vector(m)
        cv[-1] = 0.5                                   # outside the mask
        ok, checks = g4.check_freeze(frozen_observed(central_vector=cv, reported_bin_mask=m))
        self.assertFalse(ok)
        self.assertFalse([c for c in checks
                          if c["name"] == "freeze:central_vector_zero_outside_mask"][0]["ok"])


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

    def test_subsample_size_must_match_the_frozen_policy(self):
        """§4 mutation table: `train_events 2_000_000 -> 1000` was caught by nothing. Coverage was
        only ever compared against the subsample's OWN length, which cannot detect a short run."""
        self.assertTrue(g4.check_mc_index_order(np.arange(1000), 10_000, 1000)[0])
        self.assertFalse(g4.check_mc_index_order(np.arange(1000), 10_000, 2_000_000)[0])

    def test_subsample_size_clamps_to_a_smaller_inventory(self):
        """The loader draws min(max_events, N), so a fixture with fewer rows than the policy asks
        for is legitimately short and must not be failed for it."""
        self.assertTrue(g4.check_mc_index_order(np.arange(60), 60, 2_000_000)[0])


class MarginalNormCap(unittest.TestCase):
    def test_marginal_exact_pass(self):
        h = np.random.default_rng(1).random(20)
        self.assertTrue(g4.check_marginal_closure(h, h.copy())[0])

    def test_marginal_large_l1_fail(self):
        a = np.zeros(4); a[0] = 1.0; b = np.zeros(4); b[3] = 1.0
        self.assertFalse(g4.check_marginal_closure(a, b)[0])

    def test_normalization_pass(self):
        """Was `check_normalization(100.0, 100.0)`. The truth-level `ratio ~ 1` primitive is retired
        (it had no caller and its target is acceptance-dependent); the real normalization gate is the
        reco-level fold-forward ratio against R."""
        self.assertTrue(g4.check_fold_forward_ratio(113.5, 100.0, 1.135)[0])

    def test_normalization_fail(self):
        # overshoot: inside neither the tolerance nor (1.30 vs R=1.135) a defensible rate
        self.assertFalse(g4.check_fold_forward_ratio(130.0, 100.0, 1.135)[0])
        # and the defect the gate exists for: the rate erased back to 1
        self.assertFalse(g4.check_fold_forward_ratio(100.0, 100.0, 1.135)[0])

    def test_retired_primitive_is_gone(self):
        """Pin the retirement, so the shim cannot quietly come back and be wired by mistake."""
        self.assertFalse(hasattr(g4, "check_normalization"))
        self.assertNotIn("normalization_dev_max", g4.FROZEN["tolerances"])

    def test_cap_pass(self):
        self.assertTrue(g4.check_cap_sensitivity(0.0)[0])

    def test_cap_fail(self):
        self.assertFalse(g4.check_cap_sensitivity(0.05)[0])

    def test_cap_missing_fail(self):
        self.assertFalse(g4.check_cap_sensitivity(None)[0])

    def test_cap_nan_fail(self):
        self.assertFalse(g4.check_cap_sensitivity(float("nan"))[0])


class TargetProvenance(unittest.TestCase):
    """Audit B2: `z['target']` -- the sole carrier of refinement_is_learned_production, refined_sum,
    pot_scale and signed_target_hash -- was never read, though the driver writes it."""

    def test_good_target_passes(self):
        self.assertTrue(g4.check_target_provenance(good_target())[0])

    def test_purity_control_target_fails(self):
        self.assertFalse(g4.check_target_provenance(
            good_target(target_mode="purity-control"))[0])

    def test_injected_refinement_fails(self):
        """RESTORE Step 4: Delta has no ROOT, so u2d.refine_stay_positive cannot import there and a
        Delta run can only inject an sklearn refinement, which self-reports False. Nothing stopped
        such a result being validated as the publication nominal."""
        ok, checks = g4.check_target_provenance(
            good_target(refinement_is_learned_production=False))
        self.assertFalse(ok)
        self.assertFalse([c for c in checks
                          if c["name"] == "target:refinement_is_learned_production"][0]["ok"])

    def test_missing_signed_target_hash_fails(self):
        self.assertFalse(g4.check_target_provenance(good_target(signed_target_hash=None))[0])

    def test_bad_pot_scale_fails(self):
        self.assertFalse(g4.check_target_provenance(good_target(pot_scale=0.0))[0])

    def test_negative_refined_weight_fails(self):
        self.assertFalse(g4.check_target_provenance(good_target(refined_min=-1e-9))[0])

    def test_absent_target_block_fails(self):
        self.assertFalse(g4.check_target_provenance(None)[0])


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

    def test_provenance_pass(self):
        self.assertTrue(g4.check_closure_provenance(
            ordinary_report(), stress_report(), powered_report())[0])

    def test_purity_control_closure_refused(self):
        """RESTORE Step 3 refuses `--bkg-mode purity` as the closure in prose; refuse it in code."""
        self.assertFalse(
            g4.check_closure_provenance(ordinary_report(bkg_mode="purity"), stress_report(),
                                        powered_report())[0])

    def test_synthetic_fixture_closure_refused(self):
        """The 2026-07-26 Delta run (20489224) passed on random data, where the pseudo-data IS the
        MC and push ~ 1 is nearly guaranteed regardless of estimator correctness."""
        ok, checks = g4.check_closure_provenance(
            ordinary_report(is_synthetic_fixture=True), stress_report())
        self.assertFalse(ok)
        self.assertFalse([c for c in checks
                          if c["name"] == "closure:ordinary_not_synthetic_fixture"][0]["ok"])

    def test_loosened_closure_thresholds_refused(self):
        self.assertFalse(
            g4.check_closure_provenance(ordinary_report(l1_max=0.9), stress_report())[0])
        self.assertFalse(
            g4.check_closure_provenance(ordinary_report(push_med_tol=5.0), stress_report())[0])

    def test_closure_on_the_wrong_grid_refused(self):
        self.assertFalse(g4.check_closure_provenance(
            ordinary_report(edges_pt=[0.0, 1.0, 4.5]), stress_report())[0])

    def test_wrong_report_schema_refused(self):
        self.assertFalse(
            g4.check_closure_provenance(ordinary_report(report_schema="something-else"),
                                        stress_report())[0])
        self.assertFalse(
            g4.check_closure_provenance(ordinary_report(),
                                        stress_report(report_schema="something-else"))[0])


class ReportVerdict(unittest.TestCase):
    def test_all_pass(self):
        payload, verdict = good_report()
        self.assertTrue(verdict, [c for c in payload["checks"] if not c["ok"]])
        self.assertEqual(payload["verdict"], "PASS")
        self.assertFalse(payload["nominal_pet_training_allowed"])
        self.assertTrue(all(payload["component_verdicts"].values()))

    def test_freeze_failure_fails_verdict(self):
        _, verdict = good_report(frozen_observed=frozen_observed(bkg_mode="purity"))
        self.assertFalse(verdict)

    def test_weights_failure_fails_verdict(self):
        _, verdict = good_report(weights_push=np.array([1.0, np.nan, 2.0]), imc=np.arange(3),
                                 n_full=10, n_expected_subsample=3)
        self.assertFalse(verdict)

    def test_index_failure_fails_verdict(self):
        _, verdict = good_report(imc=np.array([2, 1, 0]))
        self.assertFalse(verdict)

    def test_closure_failure_fails_verdict(self):
        _, verdict = good_report(closure=(False, True, True))
        self.assertFalse(verdict)

    def test_target_failure_fails_verdict(self):
        _, verdict = good_report(target=good_target(refinement_is_learned_production=False))
        self.assertFalse(verdict)

    def test_absent_evidence_fails_every_component(self):
        """THE audit-B2 regression. Each of these arguments used to make the report builder DROP its
        component, and the receipt then reported PASS with n_failed 0 while embedding the tolerances
        the dropped checks would have used. Absent evidence is now a named failing check."""
        for kwargs, component in (
                ({"marginal": None}, "marginal"),
                ({"saturation_frac": None}, "cap"),
                ({"closure": None}, "closure"),
                ({"closure_reports": None}, "closure_provenance"),
                ({"target": None}, "target"),
                ({"weights_push": None}, "weights"),
                ({"imc": None}, "index_order"),
                ({"fold_forward": None, "fold_forward_driver": None}, "fold_forward"),
                ({"fold_forward_driver": None}, "fold_forward_independence"),
                ({"spectra_driver": None}, "spectra_independence")):
            with self.subTest(component=component):
                payload, verdict = good_report(**kwargs)
                self.assertFalse(verdict)
                self.assertFalse(payload["component_verdicts"][component])
                self.assertGreater(payload["n_failed"], 0)
                self.assertIn(f"{component}:evidence_supplied",
                              {c["name"] for c in payload["checks"]})

    def test_noise_weights_do_not_pass(self):
        """Audit B2 reproduced `15 checks, 0 failed, verdict PASS` on an npz whose weights_push was
        |N(1,0.3)| noise. Noise cannot satisfy the fold-forward ratio, so build the same shape of
        submission and require a FAIL."""
        rng = np.random.default_rng(7)
        noise = np.abs(rng.normal(1.0, 0.3, 50))
        payload, verdict = good_report(
            weights_push=noise, imc=np.arange(50), n_expected_subsample=50,
            fold_forward=(float(noise.sum()), float(noise.size), 1.135),
            fold_forward_driver=(float(noise.sum()), float(noise.size), 1.135))
        self.assertFalse(verdict)
        self.assertFalse(payload["component_verdicts"]["fold_forward"])

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


class PoweredClosureIsRecomputed(unittest.TestCase):
    """D2's powered closure, and the point that it is RECOMPUTED.

    The first version of this gate read `is_powered_closure` and `recovery_criteria_met` -- two
    booleans the report asserts about itself, which is the self-agreeing shape this repo's audits
    keep finding. Every case below breaks exactly ONE thing, so each criterion is shown to bite on
    its own rather than only in company.
    """

    def _ok(self, **over):
        return g4.check_powered_closure(powered_report(**over))

    def test_matching_report_passes(self):
        ok, checks = self._ok()
        self.assertTrue(ok, [c for c in checks if not c["ok"]])

    def test_absent_report_fails_and_names_evidence(self):
        ok, checks = g4.check_powered_closure(None)
        self.assertFalse(ok)
        self.assertEqual([c["name"] for c in checks], ["powered:evidence_supplied"])

    def test_a_complete_report_emits_no_evidence_supplied_check(self):
        """Audit B2's shape: `:evidence_supplied` exists only where evidence is MISSING."""
        _ok, checks = self._ok()
        self.assertEqual([c for c in checks if c["name"].endswith(":evidence_supplied")], [])

    # ---- the three acceptance numbers, each broken alone ----------------------------------------
    def _vectors_report(self, **kw):
        prior, target, unfolded, untilted = powered_vectors(**kw)
        gap = float(np.abs(prior - target).sum())
        floor = float(np.abs(prior - untilted).sum())
        resid = float(np.abs(unfolded - target).sum())
        return powered_report(
            h_prior=[float(x) for x in prior], h_target=[float(x) for x in target],
            h_unfolded=[float(x) for x in unfolded], h_untilted=[float(x) for x in untilted],
            metrics={"gap": gap, "floor": floor, "residual": resid,
                     "floor_over_gap": floor / gap, "residual_over_gap": resid / gap,
                     "recovery": 1.0 - resid / gap})

    def _failing(self, report):
        ok, checks = g4.check_powered_closure(report)
        self.assertFalse(ok)
        return {c["name"] for c in checks if not c["ok"]}

    def test_too_small_a_gap_fails(self):
        """Nothing injected means nothing to recover, and a pass would be vacuous."""
        bad = self._failing(self._vectors_report(gap=0.10))
        self.assertIn("powered:gap_is_large_enough", bad)

    def test_floor_comparable_to_gap_fails(self):
        """If sample-split noise is the same size as the injection, the test has no power."""
        bad = self._failing(self._vectors_report(gap=0.30, floor_frac=0.5))
        self.assertIn("powered:floor_small_against_gap", bad)

    def test_recovery_below_eighty_percent_fails(self):
        bad = self._failing(self._vectors_report(gap=0.30, resid_frac=0.5))
        self.assertIn("powered:recovery_meets_criterion", bad)

    def test_recovery_just_inside_the_criterion_passes(self):
        """Sensitivity for the test above: 0.20 is a boundary, not a wall the fixture never reaches."""
        ok, checks = g4.check_powered_closure(self._vectors_report(gap=0.30, resid_frac=0.19))
        self.assertTrue(ok, [c for c in checks if not c["ok"]])

    # ---- the one that proves it recomputes -----------------------------------------------------
    def test_a_doctored_metrics_block_cannot_launder_bad_spectra(self):
        """THE point of the rewrite. The report claims criteria met and carries a metrics block that
        agrees with the claim; only the SPECTRA disagree. A gate that read either the verdict or the
        metrics would pass this."""
        honest = powered_report()
        bad = self._vectors_report(gap=0.30, resid_frac=0.6)
        bad["metrics"] = honest["metrics"]              # keep the healthy-looking numbers
        bad["verdict"] = "PASS"
        bad["recovery_criteria_met"] = True
        failing = self._failing(bad)
        self.assertIn("powered:recovery_meets_criterion", failing)
        self.assertIn("powered:reported_metrics_match_recomputation", failing)

    def test_asserted_booleans_alone_do_not_pass(self):
        """The exact shape the first implementation accepted."""
        self.assertFalse(g4.check_powered_closure(
            {"is_powered_closure": True, "recovery_criteria_met": True})[0])

    # ---- protocol, because criteria only mean something for the declared experiment -------------
    def test_wrong_injection_amplitude_fails(self):
        self.assertIn("powered:injection_amplitude",
                      self._failing(powered_report(
                          injection={"amplitude": 0.05, "rate_preserving": True, "form": "x"})))

    def test_a_rate_changing_injection_fails(self):
        self.assertIn("powered:injection_rate_preserving",
                      self._failing(powered_report(
                          injection={"amplitude": 0.35, "rate_preserving": False, "form": "x"})))

    def test_overlapping_split_fails(self):
        self.assertIn("powered:samples_disjoint_as_declared",
                      self._failing(powered_report(
                          samples={"half_size": 2000000, "split_seed": 7, "disjoint": False})))

    def test_off_protocol_split_seed_fails(self):
        self.assertIn("powered:samples_disjoint_as_declared",
                      self._failing(powered_report(
                          samples={"half_size": 2000000, "split_seed": 99, "disjoint": True})))

    def test_non_nominal_configuration_fails(self):
        self.assertIn("powered:nominal_configuration",
                      self._failing(powered_report(
                          configuration={"niter": 1, "epochs": 2, "estimator_seed": 42,
                                         "subsample_seed": 0})))

    def test_wrong_schema_fails(self):
        self.assertIn("powered:report_schema",
                      self._failing(powered_report(report_schema="ordinary-closure-v9")))

    def test_truth_leg_reco_weight_fails(self):
        self.assertIn("powered:reco_leg_is_w_reco",
                      self._failing(powered_report(reco_leg_weight_used="w_truth")))

    def test_off_grid_histogram_fails(self):
        self.assertIn("powered:grid_is_frozen",
                      self._failing(powered_report(edges_pt=[0.0, 1.0, 2.0])))

    def test_a_denormalized_spectrum_fails(self):
        bad = powered_report()
        bad["h_unfolded"] = [2.0 * x for x in bad["h_unfolded"]]
        failing = self._failing(bad)
        self.assertIn("powered:vector_h_unfolded", failing)

    def test_a_truncated_spectrum_fails(self):
        bad = powered_report()
        bad["h_target"] = bad["h_target"][:-1]
        self.assertIn("powered:vector_h_target", self._failing(bad))

    def test_unusable_spectra_do_not_fall_back_to_reported_metrics(self):
        bad = powered_report()
        bad["h_prior"] = bad["h_prior"][:10]
        failing = self._failing(bad)
        self.assertIn("powered:recomputed_metrics", failing)
