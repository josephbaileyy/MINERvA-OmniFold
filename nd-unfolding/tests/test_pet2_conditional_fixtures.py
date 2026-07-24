"""Contract tests for feature-specific conditional-information fixtures."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import numpy as np

ND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ND not in sys.path:
    sys.path.insert(0, ND)

from pet2_torch.conditional_fixtures import (  # noqa: E402
    FAMILIES,
    MODES,
    make_feature_conditional_stress_dataset,
)
from pet2_torch.aggregate_conditional_stress import (  # noqa: E402
    _comparison,
    _mode_gates,
    _role_summary,
)
import pet2_torch.aggregate_conditional_stress as aggregate_module  # noqa: E402
from pet2_torch.features import materialize_feature_view  # noqa: E402
from pet2_torch.model import ModelConfig  # noqa: E402


class FeatureConditionalFixtureContract(unittest.TestCase):
    @staticmethod
    def _aggregate_role(rmse):
        return {
            "push_log_ratio_rmse": rmse,
            "push_log_ratio_bias": 0.0,
            "pull_log_ratio_rmse": rmse,
            "pull_log_ratio_bias": 0.0,
            "global_ess_expected": 100.0,
            "global_ess_predicted": 100.0,
            "global_ess_fidelity_percent": 0.0,
            "tail_ess_expected": 30.0,
            "tail_ess_predicted": 30.0,
            "tail_ess_fidelity_percent": 0.0,
            "predicted_ratio_q99": 1.5,
            "predicted_ratio_max": 1.5,
            "predicted_weight_q99": 2.0,
            "predicted_weight_max": 2.0,
            "max_projection_relative_l1": 0.1,
            "cap10_saturated_count": 0,
            "cap30_saturated_count": 0,
            "cap10_saturated_reference_weight_mass": 0.0,
            "cap30_saturated_reference_weight_mass": 0.0,
            "cap10_vs_cap30_max_relative_ess_shift": 0.0,
            "runtime_seconds": 1.0,
            "peak_gpu_memory_bytes": 100,
            "mean_step_throughput_rows_per_second": 1000.0,
        }

    def test_all_families_have_exact_parent_pairs_and_one_truth_inventory(self):
        truth_hashes = set()
        truth_inventory_hashes = set()
        row_footings = set()
        for family in FAMILIES:
            fixture = make_feature_conditional_stress_dataset(
                family,
                "signal",
                n_signal=800,
                n_background=40,
                seed=424242,
            )
            certificate = fixture.exclusivity_certificate
            self.assertEqual(certificate["status"], "pass")
            self.assertTrue(
                all(certificate["parent_tensor_fields_pair_identical"].values())
            )
            self.assertTrue(certificate["pair_members_same_partition"])
            self.assertEqual(certificate["parent_analytic_carrier_auc"], 0.5)
            self.assertEqual(
                certificate["parent_analytic_carrier_auc_by_partition"],
                {"0": 0.5, "1": 0.5, "2": 0.5},
            )
            self.assertEqual(certificate["enriched_carrier_auc"], 1.0)
            self.assertTrue(
                all(
                    value == 1.0
                    for value in certificate[
                        "enriched_carrier_auc_by_partition"
                    ].values()
                )
            )
            self.assertEqual(certificate["target_ratio_values"], [0.5, 1.5])
            self.assertTrue(certificate["pair_target_weighted_mean_exact"])
            self.assertFalse(certificate["truth_modified_by_carrier"])
            self.assertEqual(
                certificate["base_truth_tensor_sha256"],
                certificate["truth_tensor_sha256"],
            )
            self.assertTrue(
                certificate["bookkeeping_excluded_from_model_tensors"]
            )
            self.assertTrue(
                certificate["refinement_carrier_dependence_unchanged"]
            )
            for counts in certificate[
                "hidden_sign_counts_by_partition"
            ].values():
                self.assertEqual(counts["-1"], counts["1"])
            if family == "overflow":
                self.assertTrue(
                    certificate[
                        "synthetic_declared_overflow_energy_matches_aggregate_token"
                    ]
                )
            if family == "muon-token":
                relation = certificate["muon_knn_contract"]
                self.assertEqual(relation["k_neighbors"], 3)
                self.assertGreaterEqual(relation["minimum_recoil_tokens"], 6)
                self.assertTrue(relation["nonzero_finite_muon_coordinates"])
                self.assertTrue(relation["relation_decodes_assigned_carrier"])
                self.assertFalse(
                    certificate[
                        "real_pretruncation_overflow_conservation_claim"
                    ]
                )
            truth_hashes.add(certificate["truth_tensor_sha256"])
            truth_inventory_hashes.add(certificate["truth_inventory_sha256"])
            row_footings.add(
                __import__("json").dumps(
                    certificate["row_footing"], sort_keys=True
                )
            )
            for mode in MODES:
                if mode == "signal":
                    continue
                control = make_feature_conditional_stress_dataset(
                    family,
                    mode,
                    n_signal=800,
                    n_background=40,
                    seed=424242,
                )
                control_certificate = control.exclusivity_certificate
                self.assertEqual(
                    control_certificate["base_truth_tensor_sha256"],
                    control_certificate["truth_tensor_sha256"],
                )
                truth_hashes.add(control_certificate["truth_tensor_sha256"])
                truth_inventory_hashes.add(
                    control_certificate["truth_inventory_sha256"]
                )
                row_footings.add(
                    __import__("json").dumps(
                        control_certificate["row_footing"], sort_keys=True
                    )
                )
        self.assertEqual(len(truth_hashes), 1)
        self.assertEqual(len(truth_inventory_hashes), 1)
        self.assertEqual(len(row_footings), 1)

    def test_target_alignment_pair_mass_and_native_misses(self):
        fixture = make_feature_conditional_stress_dataset(
            "type", "signal", n_signal=800, n_background=40
        )
        signal = fixture.dataset.signal
        measured = fixture.dataset.measured
        rows = fixture.data_to_signal_row
        np.testing.assert_allclose(
            measured.data.continuous, signal.reco.continuous[rows]
        )
        np.testing.assert_allclose(
            measured.refined_weights[: len(rows)],
            signal.w_reco[rows] * fixture.expected_truth_ratio[rows],
        )
        self.assertTrue(np.all(measured.refined_weights[len(rows) :] == 0))
        self.assertTrue(np.all(measured.raw_signed_weights[len(rows) :] <= 0))
        self.assertTrue(np.any(signal.pass_truth & ~signal.pass_reco))
        self.assertFalse(np.any(signal.pass_reco & ~signal.pass_truth))
        self.assertFalse(np.any(signal.reco.token_mask[~signal.pass_reco]))
        pairs = fixture.pair_rows
        np.testing.assert_allclose(
            signal.w_reco[pairs[:, 0]], signal.w_reco[pairs[:, 1]]
        )
        np.testing.assert_array_equal(
            fixture.expected_truth_ratio[pairs],
            np.tile(np.asarray([0.5, 1.5]), (len(pairs), 1)),
        )
        np.testing.assert_allclose(
            np.sum(
                signal.w_reco[pairs] * fixture.expected_truth_ratio[pairs],
                axis=1,
            ),
            np.sum(signal.w_reco[pairs], axis=1),
            rtol=0.0,
            atol=1e-12,
        )

    def test_enriched_changes_carrier_while_parent_model_tensors_tie(self):
        for family in FAMILIES:
            fixture = make_feature_conditional_stress_dataset(
                family, "signal", n_signal=800, n_background=40
            )
            rows0, rows1 = fixture.pair_rows.T
            parent = materialize_feature_view(
                fixture.dataset.signal.reco, fixture.arm_pair.parent
            )
            child = materialize_feature_view(
                fixture.dataset.signal.reco, fixture.arm_pair.child
            )
            for name in (
                "continuous",
                "coords",
                "token_mask",
                "type_id",
                "view_id",
                "globals",
            ):
                np.testing.assert_array_equal(
                    getattr(parent, name)[rows0], getattr(parent, name)[rows1]
                )
            child_difference = any(
                not np.array_equal(
                    getattr(child, name)[rows0], getattr(child, name)[rows1]
                )
                for name in (
                    "continuous",
                    "coords",
                    "token_mask",
                    "type_id",
                    "view_id",
                    "globals",
                )
            )
            self.assertTrue(child_difference, family)

    def test_muon_token_is_additive_and_keeps_parent_globals(self):
        fixture = make_feature_conditional_stress_dataset(
            "muon-token", "signal", n_signal=800, n_background=40
        )
        parent = materialize_feature_view(
            fixture.dataset.signal.reco, fixture.arm_pair.parent
        )
        child = materialize_feature_view(
            fixture.dataset.signal.reco, fixture.arm_pair.child
        )
        np.testing.assert_allclose(parent.globals, child.globals)
        self.assertEqual(child.continuous.shape[1], parent.continuous.shape[1] + 1)
        self.assertTrue(np.any(child.coords[:, 0] != 0))
        misses = ~fixture.dataset.signal.pass_reco
        self.assertFalse(np.any(child.token_mask[misses, 0]))
        self.assertTrue(np.all(child.continuous[misses, 0] == 0))
        relation = fixture.exclusivity_certificate["muon_knn_contract"]
        self.assertTrue(relation["relation_decodes_assigned_carrier"])

    def test_every_conditional_arm_has_one_model_parameter_configuration(self):
        fingerprints = set()
        for family in FAMILIES:
            fixture = make_feature_conditional_stress_dataset(
                family, "signal", n_signal=800, n_background=40
            )
            for arm in (fixture.arm_pair.parent, fixture.arm_pair.child):
                batch = materialize_feature_view(
                    fixture.dataset.signal.reco, arm
                )
                fingerprints.add(
                    ModelConfig(
                        continuous_dim=batch.continuous.shape[2],
                        coord_dim=batch.coords.shape[2],
                        global_dim=batch.globals.shape[1],
                        hidden_dim=128,
                        num_heads=8,
                        transformer_layers=8,
                        edge_layers=2,
                        k_neighbors=3,
                    ).payload()["fingerprint"]
                )
        self.assertEqual(len(fingerprints), 1)

    def test_unity_sham_and_carrier_shuffle_are_frozen_negative_controls(self):
        for family in FAMILIES:
            unity = make_feature_conditional_stress_dataset(
                family, "unity-sham", n_signal=800, n_background=40
            )
            self.assertEqual(
                unity.exclusivity_certificate["target_ratio_values"], [1.0]
            )
            self.assertEqual(
                unity.exclusivity_certificate["enriched_carrier_auc"], 1.0
            )
            shuffled = make_feature_conditional_stress_dataset(
                family, "carrier-shuffle", n_signal=800, n_background=40
            )
            self.assertLessEqual(
                abs(
                    shuffled.exclusivity_certificate["shuffled_carrier_auc"]
                    - 0.5
                ),
                0.02,
            )
            self.assertTrue(
                all(
                    abs(value - 0.5) <= 0.02
                    for value in shuffled.exclusivity_certificate[
                        "shuffled_carrier_auc_by_partition"
                    ].values()
                )
            )
            self.assertEqual(
                shuffled.exclusivity_certificate["target_ratio_values"],
                [0.5, 1.5],
            )

    def test_contract_only_cli_is_receipted_and_never_claims_g2(self):
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "stress"
            command = [
                sys.executable,
                "-m",
                "pet2_torch.conditional_stress_cli",
                "--out",
                str(output),
                "--family",
                "view",
                "--mode",
                "signal",
                "--recipe",
                "smoke",
                "--events",
                "800",
                "--background-events",
                "40",
                "--contract-only",
            ]
            completed = subprocess.run(
                command,
                env={**os.environ, "PYTHONPATH": ND},
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn('"status": "contract_only"', completed.stdout)
            summary = __import__("json").loads((output / "summary.json").read_text())
            self.assertFalse(summary["g2_validation_claim"])
            self.assertFalse(summary["publication_promotion_permitted"])
            self.assertEqual(summary["exclusivity_certificate"]["status"], "pass")
            evidence = np.load(output / "fixture_evidence.npz", allow_pickle=False)
            self.assertIn("pair_rows", evidence.files)

    def test_frozen_aggregate_signal_and_negative_control_gates(self):
        signal_runs = []
        for _seed in (101, 202, 303):
            signal_runs.append(
                {
                    "parent_label": "parent",
                    "child_label": "child",
                    "parent": self._aggregate_role(0.57),
                    "enriched": self._aggregate_role(0.20),
                    "certificate": {"enriched_carrier_auc": 1.0},
                }
            )
        parent = _role_summary(signal_runs, "parent")
        child = _role_summary(signal_runs, "enriched")
        comparison = _comparison(signal_runs, parent, child)
        self.assertTrue(
            _mode_gates("signal", signal_runs, parent, child, comparison)["pass"]
        )

        sham_runs = []
        for _seed in (101, 202, 303):
            sham_runs.append(
                {
                    "parent_label": "parent",
                    "child_label": "child",
                    "parent": self._aggregate_role(0.08),
                    "enriched": self._aggregate_role(0.09),
                    "certificate": {"enriched_carrier_auc": 1.0},
                }
            )
        parent = _role_summary(sham_runs, "parent")
        child = _role_summary(sham_runs, "enriched")
        comparison = _comparison(sham_runs, parent, child)
        self.assertTrue(
            _mode_gates(
                "unity-sham", sham_runs, parent, child, comparison
            )["pass"]
        )

        shuffled_runs = []
        for _seed in (101, 202, 303):
            shuffled_runs.append(
                {
                    "parent_label": "parent",
                    "child_label": "child",
                    "parent": self._aggregate_role(0.57),
                    "enriched": self._aggregate_role(0.55),
                    "certificate": {
                        "enriched_carrier_auc": 0.5,
                        "enriched_carrier_auc_by_partition": {
                            "0": 0.5,
                            "1": 0.5,
                            "2": 0.5,
                        },
                    },
                }
            )
        parent = _role_summary(shuffled_runs, "parent")
        child = _role_summary(shuffled_runs, "enriched")
        comparison = _comparison(shuffled_runs, parent, child)
        self.assertTrue(
            _mode_gates(
                "carrier-shuffle", shuffled_runs, parent, child, comparison
            )["pass"]
        )
        shuffle_gates = _mode_gates(
            "carrier-shuffle", shuffled_runs, parent, child, comparison
        )
        self.assertEqual(
            set(shuffle_gates["checks"]),
            {
                "enriched_improvement_below_15_percent",
                "carrier_auc_within_0p02_of_chance",
            },
        )
        # Cap telemetry is still reported for the shuffle control, but the
        # frozen preregistration did not make it an outcome gate.
        shuffled_runs[0]["enriched"]["cap10_saturated_count"] = 1
        self.assertTrue(
            _mode_gates(
                "carrier-shuffle", shuffled_runs, parent, child, comparison
            )["pass"]
        )

    def test_conditional_delta_launcher_isolated_selftest_and_rejects_bad_seed(self):
        script = Path(ND) / "pet2_torch" / "sbatch_pet2_conditional_delta.sh"
        repository = Path(ND).parent
        with tempfile.TemporaryDirectory() as td:
            environment = {
                **os.environ,
                "PET2_REPO": str(repository),
                "PET2_OUT_BASE": td,
                "PET2_FAMILY": "muon-token",
                "PET2_CONTROL_MODE": "carrier-shuffle",
                "PET2_ESTIMATOR_SEED": "202",
                "PET2_DELTA_SELFTEST": "1",
            }
            completed = subprocess.run(
                ["bash", str(script)],
                env=environment,
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn("no submit, module load, or training", completed.stdout)
            bad = subprocess.run(
                ["bash", str(script)],
                env={**environment, "PET2_ESTIMATOR_SEED": "999"},
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn("must be 101, 202, or 303", bad.stderr)

    def test_aggregate_requires_exact_45_job_90_arm_inventory(self):
        runs = []
        for family in FAMILIES:
            for mode in MODES:
                for seed in (101, 202, 303):
                    if mode == "signal":
                        parent_rmse, child_rmse, auc = 0.57, 0.20, 1.0
                    elif mode == "unity-sham":
                        parent_rmse, child_rmse, auc = 0.08, 0.09, 1.0
                    else:
                        parent_rmse, child_rmse, auc = 0.57, 0.55, 0.5
                    certificate = {
                        "enriched_carrier_auc": auc,
                        "enriched_carrier_auc_by_partition": {
                            "0": auc,
                            "1": auc,
                            "2": auc,
                        },
                    }
                    common_role = {
                        "source_commit": "a" * 40,
                        "source_dirty": False,
                        "truth_arm_fingerprint": "truth-arm",
                        "truth_model_config_fingerprint": "truth-model",
                        "truth_preprocessing_fingerprint": "truth-pre",
                        "reco_model_config_fingerprint": "one-reco-model",
                    }
                    runs.append(
                        {
                            "family": family,
                            "mode": mode,
                            "seed": seed,
                            "dataset_fingerprint": f"{family}-{mode}-dataset",
                            "parameter_footing_fingerprint": "one-parameter-footing",
                            "control_footing_without_seed": (
                                f"{family}-{mode}-control"
                            ),
                            "truth_tensor_sha256": "truth-tensors",
                            "truth_inventory_sha256": "truth-inventory",
                            "row_footing_fingerprint": "one-row-footing",
                            "certificate_fingerprint": f"{family}-{mode}-certificate",
                            "certificate": certificate,
                            "parent_label": "parent",
                            "child_label": "child",
                            "parent": {
                                **common_role,
                                **self._aggregate_role(parent_rmse),
                            },
                            "enriched": {
                                **common_role,
                                **self._aggregate_role(child_rmse),
                            },
                        }
                    )
        paths = [Path(f"/synthetic/run-{index}.json") for index in range(45)]
        with mock.patch.object(
            aggregate_module, "_extract_run", side_effect=runs
        ):
            payload = aggregate_module.aggregate(paths)
        self.assertEqual(payload["run_count"], 45)
        self.assertEqual(payload["arm_result_count"], 90)
        self.assertEqual(
            set(payload["families"]), set(FAMILIES)
        )
        self.assertTrue(
            all(
                record["all_signal_and_negative_control_gates_pass"]
                for record in payload["families"].values()
            )
        )
        with mock.patch.object(
            aggregate_module, "_extract_run", side_effect=runs[:-1]
        ):
            with self.assertRaisesRegex(ValueError, "inventory mismatch"):
                aggregate_module.aggregate(paths[:-1])


if __name__ == "__main__":
    unittest.main()
