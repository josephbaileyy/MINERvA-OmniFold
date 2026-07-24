#!/usr/bin/env python3
"""Aggregate the frozen feature-conditional stress matrix without selection."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean, pstdev
from typing import Any

from .artifacts import write_json
from .conditional_fixtures import FAMILIES, MODES
from .utils import file_sha256, fingerprint

SEEDS = (101, 202, 303)


def _load(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _summary(values: list[float]) -> dict[str, float]:
    return {
        "mean": float(mean(values)),
        "population_std": float(pstdev(values)) if len(values) > 1 else 0.0,
        "min": float(min(values)),
        "max": float(max(values)),
    }


def _cap_telemetry(iterations: list[dict[str, Any]]) -> dict[str, float | int]:
    counts = {10: 0, 30: 0}
    weight_masses = {10: 0.0, 30: 0.0}
    shifts = []
    for iteration in iterations:
        for step in ("step1_inference", "step2_inference"):
            inference = iteration[step]
            sensitivity = inference["cap_sensitivity"]
            cap10 = sensitivity["cap_10"]
            cap30 = sensitivity["cap_30"]
            counts[10] += int(cap10["saturated_count"])
            counts[30] += int(cap30["saturated_count"])
            weight_masses[10] += float(
                cap10["saturated_reference_weight_mass"]
            )
            weight_masses[30] += float(
                cap30["saturated_reference_weight_mass"]
            )
            ess10 = float(cap10["reweighted_ess"])
            ess30 = float(cap30["reweighted_ess"])
            shifts.append(abs(ess10 - ess30) / max(abs(ess30), 1e-12))
    return {
        "cap10_saturated_count": counts[10],
        "cap30_saturated_count": counts[30],
        "cap10_saturated_reference_weight_mass": weight_masses[10],
        "cap30_saturated_reference_weight_mass": weight_masses[30],
        "cap10_vs_cap30_max_relative_ess_shift": float(
            max(shifts, default=0.0)
        ),
    }


def _extract_result(
    summary_path: Path,
    summary: dict[str, Any],
    label: str,
    result: dict[str, Any],
) -> dict[str, Any]:
    receipt_path = summary_path.parent / result["relative_path"] / "receipt.json"
    receipt = _load(receipt_path)
    iterations = receipt["omnifold_iterations"]["complete_iteration_receipts"]
    cap_telemetry = _cap_telemetry(iterations)
    peak_memory = max(
        int(step.get("peak_gpu_memory_bytes", 0))
        for iteration in iterations
        for step in (iteration["step1_fit"], iteration["step2_fit"])
    )
    throughput = [
        float(step["throughput_rows_per_second"])
        for iteration in iterations
        for step in (iteration["step1_fit"], iteration["step2_fit"])
    ]
    push = result["push_metrics"]
    pull = result["pull_metrics"]
    projections = result["projection_metrics"]
    global_expected = float(push["ess"]["global_expected"])
    tail_expected = float(push["ess"]["tail_expected"])
    return {
        "label": label,
        "role": result["role"],
        "summary_path": str(summary_path),
        "summary_sha256": file_sha256(summary_path),
        "receipt_path": str(receipt_path),
        "receipt_sha256": file_sha256(receipt_path),
        "source_commit": receipt["git"]["commit"],
        "source_dirty": bool(receipt["git"]["dirty"]),
        "truth_arm_fingerprint": receipt["truth_arm_manifest"]["fingerprint"],
        "truth_model_config_fingerprint": receipt["model_step2"]["fingerprint"],
        "truth_preprocessing_fingerprint": receipt["preprocessing_step2"][
            "fingerprint"
        ],
        "reco_model_config_fingerprint": receipt["model_step1"]["fingerprint"],
        "reco_arm_fingerprint": receipt["arm_manifest"]["fingerprint"],
        "recipe_fingerprint": result["recipe_fingerprint"],
        "push_log_ratio_rmse": float(push["log_ratio_residual"]["rmse"]),
        "push_log_ratio_bias": float(push["log_ratio_residual"]["bias"]),
        "pull_log_ratio_rmse": float(pull["log_ratio_residual"]["rmse"]),
        "pull_log_ratio_bias": float(pull["log_ratio_residual"]["bias"]),
        "global_ess_expected": global_expected,
        "global_ess_predicted": float(push["ess"]["global_predicted"]),
        "global_ess_fidelity_percent": 100.0
        * abs(float(push["ess"]["global_predicted"]) - global_expected)
        / max(global_expected, 1e-12),
        "tail_ess_expected": tail_expected,
        "tail_ess_predicted": float(push["ess"]["tail_predicted"]),
        "tail_ess_fidelity_percent": 100.0
        * abs(float(push["ess"]["tail_predicted"]) - tail_expected)
        / max(tail_expected, 1e-12),
        "predicted_ratio_q99": float(push["predicted_ratio"]["quantiles"]["q99"]),
        "predicted_ratio_max": float(push["predicted_ratio"]["quantiles"]["q100"]),
        "predicted_weight_q99": float(push["predicted_weight"]["quantiles"]["q99"]),
        "predicted_weight_max": float(push["predicted_weight"]["quantiles"]["q100"]),
        "max_projection_relative_l1": float(
            max(record["relative_l1"] for record in projections.values())
        ),
        **cap_telemetry,
        "runtime_seconds": float(result["runtime_seconds"]),
        "peak_gpu_memory_bytes": peak_memory,
        "mean_step_throughput_rows_per_second": float(mean(throughput)),
        "hidden_sign_groups": push["hidden_sign_groups"],
    }


def _extract_run(summary_path: Path) -> dict[str, Any]:
    summary = _load(summary_path)
    if summary.get("status") != "complete_feature_conditional_stress":
        raise ValueError(f"incomplete conditional stress summary: {summary_path}")
    if summary.get("evidence_class") != "synthetic-fixture":
        raise ValueError(f"wrong evidence label: {summary_path}")
    if summary.get("g2_validation_claim") or summary.get(
        "publication_promotion_permitted"
    ):
        raise ValueError(f"forbidden G2/publication claim: {summary_path}")
    if not summary["recipe"]["comparison_claim_permitted"]:
        raise ValueError(f"non-matched recipe in aggregate: {summary_path}")
    family = summary["family"]
    mode = summary["mode"]
    if family not in FAMILIES or mode not in MODES:
        raise ValueError(f"unknown family/mode: {summary_path}")
    certificate = summary["exclusivity_certificate"]
    if certificate.get("status") != "pass":
        raise ValueError(f"failed exclusivity certificate: {summary_path}")
    certificate_for_hash = dict(certificate)
    certificate_for_hash["fingerprint"] = ""
    if certificate.get("fingerprint") != fingerprint(certificate_for_hash):
        raise ValueError(f"mutated exclusivity certificate: {summary_path}")
    required_certificate_checks = {
        "parent_pair_fields": all(
            certificate.get("parent_tensor_fields_pair_identical", {}).values()
        ),
        "pair_members_same_partition": (
            certificate.get("pair_members_same_partition") is True
        ),
        "parent_chance_auc": (
            certificate.get("parent_analytic_carrier_auc") == 0.5
            and set(
                certificate.get(
                    "parent_analytic_carrier_auc_by_partition", {}
                )
            )
            == {"0", "1", "2"}
            and all(
                value == 0.5
                for value in certificate[
                    "parent_analytic_carrier_auc_by_partition"
                ].values()
            )
        ),
        "truth_tensor_bytes_unchanged": (
            certificate.get("truth_modified_by_carrier") is False
            and certificate.get("truth_tensor_sha256")
            == certificate.get("base_truth_tensor_sha256")
        ),
        "bookkeeping_excluded": (
            certificate.get("bookkeeping_excluded_from_model_tensors") is True
        ),
        "pair_mass_exact": certificate.get("pair_target_weighted_mean_exact") is True,
        "refinement_unchanged": (
            certificate.get("refinement_carrier_dependence_unchanged") is True
        ),
        "target_ratio_values": certificate.get("target_ratio_values")
        == ([1.0] if mode == "unity-sham" else [0.5, 1.5]),
    }
    if mode != "carrier-shuffle":
        required_certificate_checks["carrier_decodes_hidden_sign"] = (
            certificate.get("enriched_carrier_auc") == 1.0
            and set(
                certificate.get("enriched_carrier_auc_by_partition", {})
            )
            == {"0", "1", "2"}
            and all(
                value == 1.0
                for value in certificate.get(
                    "enriched_carrier_auc_by_partition", {}
                ).values()
            )
        )
    else:
        required_certificate_checks["carrier_shuffled_within_each_split"] = (
            abs(float(certificate.get("enriched_carrier_auc", -1.0)) - 0.5)
            <= 0.02
            and set(
                certificate.get("enriched_carrier_auc_by_partition", {})
            )
            == {"0", "1", "2"}
            and all(
                abs(float(value) - 0.5) <= 0.02
                for value in certificate.get(
                    "enriched_carrier_auc_by_partition", {}
                ).values()
            )
        )
    if family == "muon-token":
        muon_contract = certificate.get("muon_knn_contract") or {}
        required_certificate_checks["muon_knn_relation_expressible"] = (
            muon_contract.get("relation_decodes_assigned_carrier") is True
            and muon_contract.get("nonzero_finite_muon_coordinates") is True
        )
    if not all(required_certificate_checks.values()):
        raise ValueError(
            f"conditional certificate facts failed for {summary_path}: "
            f"{required_certificate_checks}"
        )
    pair = summary["arm_pair"]
    expected_labels = {pair["parent_label"], pair["child_label"]}
    if set(summary["results"]) != expected_labels:
        raise ValueError(f"parent/enriched inventory mismatch: {summary_path}")
    seed = int(summary["control_footing"]["estimator_seed"])
    return {
        "family": family,
        "mode": mode,
        "seed": seed,
        "summary_path": str(summary_path),
        "summary_sha256": file_sha256(summary_path),
        "dataset_fingerprint": summary["dataset_manifest"]["fingerprint"],
        "parameter_footing_fingerprint": summary["parameter_footing"]["fingerprint"],
        "control_footing_without_seed": fingerprint(
            {
                key: value
                for key, value in summary["control_footing"].items()
                if key not in {"fingerprint", "estimator_seed"}
            }
        ),
        "truth_tensor_sha256": certificate["truth_tensor_sha256"],
        "truth_inventory_sha256": certificate["truth_inventory_sha256"],
        "row_footing_fingerprint": fingerprint(certificate["row_footing"]),
        "certificate_fingerprint": certificate["fingerprint"],
        "certificate": certificate,
        "parent_label": pair["parent_label"],
        "child_label": pair["child_label"],
        "parent": _extract_result(
            summary_path,
            summary,
            pair["parent_label"],
            summary["results"][pair["parent_label"]],
        ),
        "enriched": _extract_result(
            summary_path,
            summary,
            pair["child_label"],
            summary["results"][pair["child_label"]],
        ),
    }


def _role_summary(runs: list[dict[str, Any]], role: str) -> dict[str, Any]:
    fields = (
        "push_log_ratio_rmse",
        "push_log_ratio_bias",
        "pull_log_ratio_rmse",
        "pull_log_ratio_bias",
        "global_ess_expected",
        "global_ess_predicted",
        "global_ess_fidelity_percent",
        "tail_ess_expected",
        "tail_ess_predicted",
        "tail_ess_fidelity_percent",
        "predicted_ratio_q99",
        "predicted_ratio_max",
        "predicted_weight_q99",
        "predicted_weight_max",
        "max_projection_relative_l1",
        "cap10_saturated_count",
        "cap30_saturated_count",
        "cap10_saturated_reference_weight_mass",
        "cap30_saturated_reference_weight_mass",
        "cap10_vs_cap30_max_relative_ess_shift",
        "runtime_seconds",
        "peak_gpu_memory_bytes",
        "mean_step_throughput_rows_per_second",
    )
    return {
        "label": (
            runs[0]["parent_label"] if role == "parent" else runs[0]["child_label"]
        ),
        "metrics": {
            field: _summary([float(run[role][field]) for run in runs])
            for field in fields
        },
    }


def _comparison(
    runs: list[dict[str, Any]],
    parent: dict[str, Any],
    enriched: dict[str, Any],
) -> dict[str, Any]:
    parent_mean = parent["metrics"]["push_log_ratio_rmse"]["mean"]
    child_mean = enriched["metrics"]["push_log_ratio_rmse"]["mean"]
    improvements = [
        100.0
        * (
            run["parent"]["push_log_ratio_rmse"]
            - run["enriched"]["push_log_ratio_rmse"]
        )
        / max(run["parent"]["push_log_ratio_rmse"], 1e-12)
        for run in runs
    ]
    return {
        "push_log_ratio_rmse_improvement_percent": 100.0
        * (parent_mean - child_mean)
        / max(parent_mean, 1e-12),
        "per_seed_push_rmse_improvement_percent": improvements,
        "direction_favorable_all_seeds": all(value > 0 for value in improvements),
    }


def _mode_gates(
    mode: str,
    runs: list[dict[str, Any]],
    parent: dict[str, Any],
    enriched: dict[str, Any],
    comparison: dict[str, Any],
) -> dict[str, Any]:
    if mode == "signal":
        checks = {
            "enriched_each_seed_rmse_at_most_0p30": all(
                run["enriched"]["push_log_ratio_rmse"] <= 0.30 for run in runs
            ),
            "enriched_mean_rmse_at_most_0p25": enriched["metrics"][
                "push_log_ratio_rmse"
            ]["mean"]
            <= 0.25,
            "mean_improvement_at_least_30_percent": comparison[
                "push_log_ratio_rmse_improvement_percent"
            ]
            >= 30.0,
            "direction_favorable_all_seeds": comparison[
                "direction_favorable_all_seeds"
            ],
            "parent_mean_rmse_at_least_0p35": parent["metrics"][
                "push_log_ratio_rmse"
            ]["mean"]
            >= 0.35,
            "global_ess_fidelity_each_seed_at_most_10_percent": all(
                run["enriched"]["global_ess_fidelity_percent"] <= 10.0
                for run in runs
            ),
            "tail_ess_fidelity_each_seed_at_most_10_percent": all(
                run["enriched"]["tail_ess_fidelity_percent"] <= 10.0
                for run in runs
            ),
            "projection_l1_each_seed_at_most_0p25": all(
                run["enriched"]["max_projection_relative_l1"] <= 0.25
                for run in runs
            ),
            "no_cap_saturation": all(
                run["enriched"]["cap10_saturated_count"] == 0
                and run["enriched"]["cap30_saturated_count"] == 0
                and run["enriched"][
                    "cap10_saturated_reference_weight_mass"
                ]
                == 0.0
                and run["enriched"][
                    "cap30_saturated_reference_weight_mass"
                ]
                == 0.0
                for run in runs
            ),
            "cap_ess_shift_each_seed_below_1_percent": all(
                run["enriched"]["cap10_vs_cap30_max_relative_ess_shift"] < 0.01
                for run in runs
            ),
        }
    elif mode == "unity-sham":
        checks = {
            "both_mean_rmse_at_most_0p15": (
                parent["metrics"]["push_log_ratio_rmse"]["mean"] <= 0.15
                and enriched["metrics"]["push_log_ratio_rmse"]["mean"] <= 0.15
            ),
            "both_global_and_tail_ess_fidelity_at_most_10_percent": all(
                run[role]["global_ess_fidelity_percent"] <= 10.0
                and run[role]["tail_ess_fidelity_percent"] <= 10.0
                for run in runs
                for role in ("parent", "enriched")
            ),
            "no_cap_saturation": all(
                run[role]["cap10_saturated_count"] == 0
                and run[role]["cap30_saturated_count"] == 0
                and run[role]["cap10_saturated_reference_weight_mass"] == 0.0
                and run[role]["cap30_saturated_reference_weight_mass"] == 0.0
                for run in runs
                for role in ("parent", "enriched")
            ),
        }
    else:
        checks = {
            "enriched_improvement_below_15_percent": comparison[
                "push_log_ratio_rmse_improvement_percent"
            ]
            < 15.0,
            "carrier_auc_within_0p02_of_chance": all(
                abs(run["certificate"]["enriched_carrier_auc"] - 0.5) <= 0.02
                and all(
                    abs(value - 0.5) <= 0.02
                    for value in run["certificate"][
                        "enriched_carrier_auc_by_partition"
                    ].values()
                )
                for run in runs
            ),
        }
    return {"checks": checks, "pass": bool(all(checks.values()))}


def aggregate(summary_paths: list[Path]) -> dict[str, Any]:
    runs = [_extract_run(path.resolve()) for path in summary_paths]
    keyed = {(run["family"], run["mode"], run["seed"]): run for run in runs}
    if len(keyed) != len(runs):
        raise ValueError("duplicate family/mode/seed conditional result")
    expected = {
        (family, mode, seed)
        for family in FAMILIES
        for mode in MODES
        for seed in SEEDS
    }
    if set(keyed) != expected:
        raise ValueError(
            f"conditional matrix inventory mismatch: "
            f"missing={sorted(expected-set(keyed))}, extra={sorted(set(keyed)-expected)}"
        )
    commits = {
        run[role]["source_commit"] for run in runs for role in ("parent", "enriched")
    }
    dirty = [
        (run["family"], run["mode"], run["seed"], role)
        for run in runs
        for role in ("parent", "enriched")
        if run[role]["source_dirty"]
    ]
    truths = {run["truth_tensor_sha256"] for run in runs}
    truth_inventories = {run["truth_inventory_sha256"] for run in runs}
    row_footings = {run["row_footing_fingerprint"] for run in runs}
    parameters = {run["parameter_footing_fingerprint"] for run in runs}
    truth_arms = {
        run[role]["truth_arm_fingerprint"]
        for run in runs
        for role in ("parent", "enriched")
    }
    truth_models = {
        run[role]["truth_model_config_fingerprint"]
        for run in runs
        for role in ("parent", "enriched")
    }
    truth_preprocessing = {
        run[role]["truth_preprocessing_fingerprint"]
        for run in runs
        for role in ("parent", "enriched")
    }
    reco_models = {
        run[role]["reco_model_config_fingerprint"]
        for run in runs
        for role in ("parent", "enriched")
    }
    if (
        len(commits) != 1
        or not commits
        or next(iter(commits)) in {"", "unavailable"}
        or dirty
        or len(truths) != 1
        or len(truth_inventories) != 1
        or len(row_footings) != 1
        or len(parameters) != 1
        or len(truth_arms) != 1
        or len(truth_models) != 1
        or len(truth_preprocessing) != 1
        or len(reco_models) != 1
    ):
        raise ValueError(
            "conditional common footing failed: "
            f"commits={commits}, dirty={dirty}, truths={truths}, "
            f"truth_inventories={truth_inventories}, "
            f"row_footings={row_footings}, "
            f"parameters={parameters}, truth_arms={truth_arms}, "
            f"truth_models={truth_models}, truth_preprocessing={truth_preprocessing}"
            f", reco_models={reco_models}"
        )
    families: dict[str, Any] = {}
    for family in FAMILIES:
        family_modes = {}
        for mode in MODES:
            selected = [keyed[(family, mode, seed)] for seed in SEEDS]
            datasets = {run["dataset_fingerprint"] for run in selected}
            controls = {run["control_footing_without_seed"] for run in selected}
            certificates = {run["certificate_fingerprint"] for run in selected}
            if len(datasets) != 1 or len(controls) != 1 or len(certificates) != 1:
                raise ValueError(f"{family}/{mode} seed footing differs")
            parent = _role_summary(selected, "parent")
            enriched = _role_summary(selected, "enriched")
            comparison = _comparison(selected, parent, enriched)
            gates = _mode_gates(mode, selected, parent, enriched, comparison)
            family_modes[mode] = {
                "seeds": list(SEEDS),
                "parent": parent,
                "enriched": enriched,
                "comparison": comparison,
                "gates": gates,
                "certificate": selected[0]["certificate"],
                "runs": selected,
            }
        family_pass = all(
            family_modes[mode]["gates"]["pass"] for mode in MODES
        )
        families[family] = {
            "modes": family_modes,
            "channel_capacity_decision": (
                "pass-synthetic-channel-capacity"
                if family_pass
                else "fail-synthetic-channel-or-control"
            ),
            "all_signal_and_negative_control_gates_pass": family_pass,
            "real_minerva_benefit_claim_permitted": False,
        }
    payload = {
        "status": "complete_feature_conditional_stress_aggregate",
        "evidence_class": "synthetic-fixture",
        "source_commit": next(iter(commits)),
        "expected_families": list(FAMILIES),
        "expected_modes": list(MODES),
        "expected_seeds": list(SEEDS),
        "run_count": len(runs),
        "arm_result_count": 2 * len(runs),
        "common_footing": {
            "truth_tensor_sha256": next(iter(truths)),
            "truth_inventory_sha256": next(iter(truth_inventories)),
            "row_footing_fingerprint": next(iter(row_footings)),
            "parameter_footing_fingerprint": next(iter(parameters)),
            "truth_arm_fingerprint": next(iter(truth_arms)),
            "truth_model_config_fingerprint": next(iter(truth_models)),
            "truth_preprocessing_fingerprint": next(iter(truth_preprocessing)),
            "reco_model_config_fingerprint": next(iter(reco_models)),
        },
        "families": families,
        "g2_validation_claim": False,
        "publication_promotion_permitted": False,
        "interpretation": (
            "channel-capacity harness evidence only; a pass does not show that "
            "MINERvA data contains a beneficial conditional"
        ),
    }
    payload["fingerprint"] = fingerprint(payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    base = Path(args.base).expanduser().resolve()
    paths = sorted(base.glob("pet2cs_*_seed*_job*/summary.json"))
    if not paths:
        raise FileNotFoundError(f"no conditional stress summaries under {base}")
    payload = aggregate(paths)
    write_json(args.out, payload)
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
