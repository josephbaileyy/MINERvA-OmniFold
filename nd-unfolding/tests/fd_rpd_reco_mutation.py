#!/usr/bin/env python3
"""Kill required RPD-RECO guard and reading-bar mutants in isolated copies.

The harness never changes the producer or tests in the checkout. A mutant is
killed only by an assertion failure; collection/import errors are not evidence.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PRODUCER = ROOT / "nd-unfolding/fd_rpd_reco.py"
TESTS = ROOT / "nd-unfolding/tests/test_fd_rpd_reco.py"

CUSTODY_GUARD_TESTS = {
    "PLATFORM_LATE_ROOT": "test_exit_inventory_refuses_before_plain_read and (protected or escape)",
    "PLATFORM_LATE_PRESENT": "test_exit_inventory_refuses_before_plain_read and missing",
    "PLATFORM_PREPARE_SUBSET": "test_prepare_mapped_subset_refuses",
    "PLATFORM_CONFIG": "test_platform_config_closed_roles_and_reasons",
    "PLATFORM_MAP_IDENTITY": "test_platform_executable_maps_identity",
    "PLATFORM_MAP_SET": "test_platform_prepare_pins_and_protected_first and set",
    "PLATFORM_PROTECTED": "test_platform_prepare_pins_and_protected_first and protected",
    "PLATFORM_MAP_FILE": "test_platform_prepare_pins_and_protected_first and inode",
    "PLATFORM_PIN_CHANGED": "test_platform_prepare_pins_and_protected_first and unstable",
    "TRACE_CWD": "test_trace_policy_disjoint_under_system_run",
    "TRACE_RECORD_NAME": "test_trace_stop_record_is_complete_public_and_cfs_first",
    "ENVIRONMENT_EXCLUSIONS": "test_environment_exclusions_reject_interpreter_keys",
    "MAT_INVENTORY": "test_prepare_firing_guards and inventory",
    "STAGE_SOURCE_STAT": "test_prepare_firing_guards and atime",
    "NATIVE_SELECTION": "test_prepare_firing_guards and native",
    "RUN_PROTECTED_OVERLAP": "test_run_overlaps_protected_guard",
    "NEGATIVE_EXPECTED_GUARD": "test_negative_expected_guard",
    "TRACE_EXTRACT_IDENTITY": "test_trace_extract_identity_guard",
    "PREPARE_FENCE": "test_prepare_firing_guards and fence_status",
    "INSTRUMENT_DIRECTORIES": "test_instrument_directories_required",
    # #1064, the director's before-READY requirements (2026-11-11)
    "PREPARE_PLACEHOLDER": "test_prepare_placeholder_refuses",
    "CUSTODY_ARGV_PLACEHOLDER": "test_custody_argv_placeholder_refuses",
}
GUARD_TESTS = {
    "MAT_PLATFORM_LIBRARIES": "test_platform_guard_on_production_path",
    "MAT_IMPORT_ENVIRONMENT": "test_import_diff_is_bounded or test_import_values_are_pinned",
    "MAT_RUNTIME_ENVIRONMENT": "test_worker_snapshot_before_root_and_runtime_recheck",
    "MAT_MAPPED_STAT": "test_prepared_mapped_stats_and_staged_digest and (size or inode)",
    "MAT_INSTRUMENT_DIGEST": "test_prepared_mapped_stats_and_staged_digest and staged_digest",
    "MAT_MAPPED_SET": "test_nonpinned_mapped_library_refuses",
    "FLUX_CONSTRUCTOR_SELECTION": "test_extract_selection_guard",
    "P_F_BINNING": "test_pf_common_binning_silent_and_firing",
    "P_F_UNITS": "test_pf_common_units_silent_and_firing",
    "FLUX_CUSTODY": "test_flux_custody_and_factor_guards",
    "FLUX_EXTRACT": "test_flux_extract_identity_guards",
    "FLUX_EXTRACT_IDENTITY": "test_flux_extract_identity_guards",
    "FLUX_FACTORS": "test_flux_custody_and_factor_guards",
    "MAT_DATA_STAGE": "test_staged_prefix_restore_and_missing or test_extract_missing_dependency_before_constructor",
    "MAT_ENVIRONMENT": "test_mat_environment_reuses_instrument",
    "MAT_MNVH1D": "test_pyroot_reader_protocol_guards",
    "MAT_PREPARE": "test_same_connect_prepare_receipt or test_legacy_prepare_presence_and_policy_guards",
    "MAT_PREPARE_PRESENT": "test_prepare_receipt_named_guards",
    "MAT_PREPARE_RUN": "test_prepare_receipt_named_guards",
    "MAT_PREPARE_CONNECT_PRESENT": "test_prepare_receipt_named_guards",
    "MAT_PREPARE_CONNECT": "test_prepare_receipt_named_guards",
    "MAT_PREPARE_AGE": "test_prepare_receipt_named_guards",
    "MAT_PREPARE_ENVIRONMENT": "test_prepare_receipt_named_guards",
    "MAT_ROOT_FILE": "test_pyroot_reader_protocol_guards",
    "MAT_TFILE_STAGE": "test_tfile_guard_both_entries",
    "CONFIG_READY": "test_draft_configuration_refuses",
    # #1064, the director's before-READY requirements (2026-11-11)
    "CONFIG_PLACEHOLDER": "test_config_placeholder_refuses",
    "ARGV_PLACEHOLDER": "test_argv_placeholder_refuses",
    "MAT_DEPENDENCY_RECEIPT": "test_mat_dependency_receipt_all_fifteen",
    "WALL_BUDGET": "test_priced_wall_budget_limits",
    "PRICED_TIMING_PAIR": "test_priced_timing_pair_refuses",
    "MEASURED_RATE": "test_measured_rate_refuses",
    "TIMING_SOURCE": "test_timing_record_guards",
    "TIMING_SHAPE": "test_timing_record_guards",
    "TIMING_ENVIRONMENT": "test_timing_record_guards",
    "ARRAY_SHAPE": "test_signal_guards",
    "BOOTSTRAP_VARIANCE": "test_leave_one_out_and_bootstrap_sigma_hand_calculation",
    "C0_CALIBRATION": "test_c0_calibration_both_sigma_directions_and_offset",
    "C0_COUNT": "test_c0_tail_count_and_family_guards",
    "C0_FAMILY": "test_c0_tail_count_and_family_guards",
    "C0_TAIL": "test_c0_tail_count_and_family_guards",
    "CELL_IDENTITY": "test_empty_support_flux_layout_and_cells",
    "CE_SUPPORT": "test_empty_support_flux_layout_and_cells",
    "C_E1": "test_energy_algebra_only_and_controls",
    "C_E3": "test_energy_controls_each_stratum_and_bars",
    "D2_FINITE": "test_swap_support_and_d2_finite_guards",
    "D2_VARIANCE": "test_step_and_d2_variance_guards",
    "DATA_PARTITION": "test_data_partition_exact_and_independent",
    "DIGEST_FORMAT": "test_staging_guards",
    "DRY_RUN_SCOPE": "test_step_output_and_dry_run_guards",
    "FINITE_DATA": "test_finite_data_refusal",
    "FINITE_MC": "test_signal_guards",
    "FLUX_HISTOGRAM": "test_p0_refusals",
    "FLUX_LAYOUT": "test_empty_support_flux_layout_and_cells",
    "FLUX_SELECTION": "test_p0_refusals",
    "FLUX_SIZE": "test_mass_and_flux_size_guards",
    "FLUX_SUPPORT": "test_empty_support_flux_layout_and_cells",
    "INPUT_CHANGED": "test_input_changed_guard",
    "INPUT_DIGEST": "test_pins_bad_and_good",
    "INPUT_EXISTS": "test_staging_guards",
    "KEY_ALLOWLIST": "test_key_allowlist_and_object_array",
    "KEY_EXISTS": "test_signal_guards",
    "MASS_CONSTANTS": "test_mass_and_flux_size_guards",
    "MC_SUPPORT": "test_empty_support_flux_layout_and_cells",
    "NICE": "test_runtime_estimate_and_resource_guards",
    "NOATIME": "test_native_noatime_absence_refuses",
    "OUTPUT_LOCATION": "test_output_location_before_any_write",
    "OUTPUT_EXISTS": "test_step_output_and_dry_run_guards",
    "OUTSIDE_RANGE": "test_flux_range_step_function_and_gate",
    "PASS_TRUTH": "test_signal_guards",
    "PIN_FORMAT": "test_pin_manifest_guards",
    "PIN_ROOT": "test_pin_manifest_guards",
    "PIN_SET": "test_pins_bad_and_good",
    "PLAIN_OPEN": "test_plain_open_refused_and_staging_allowed",
    "POT": "test_rate_per_pot_guard_and_arithmetic",
    "PREDECESSOR": "test_every_step_refuses_missing_predecessor",
    "PREDECESSOR_IDENTITY": "test_predecessor_pass_identity_and_chain",
    "PREDECESSOR_SHA": "test_predecessor_pass_identity_and_chain",
    "PREDICTION_COMMITTED": "test_prediction_required_committed_and_exact",
    "PREDICTION_CONTENT": "test_prediction_content_guard",
    "PREDICTION_REPRODUCED": "test_prediction_reproduction_guard",
    "PREDICTION_SHA": "test_prediction_required_committed_and_exact",
    "PRICE_REVIEW": "test_wall_clock_and_price_guards",
    "PRODUCT_DIGEST": "test_product_digest_guard",
    "P_F": "test_p0_refusals",
    "SOURCE_COMMIT": "test_p0_refusals",
    "STAGED_DIGEST": "test_staging_guards",
    "STAGE_LOCATION": "test_staging_guards",
    "STEP_NAME": "test_step_output_and_dry_run_guards",
    "STEP_VARIANCE": "test_step_and_d2_variance_guards",
    "SWAP_SUPPORT": "test_swap_support_and_d2_finite_guards",
    "THREADS": "test_runtime_estimate_and_resource_guards",
    "WALL_CLOCK": "test_wall_clock_and_price_guards",
    "WEIGHTS": "test_signal_guards",
}
BAR_MUTANTS = {
    "DEFAULT_WALL_SECONDS": (3600, "test_priced_wall_budget_limits"),
    "MAX_PRICED_WALL_SECONDS": (172800, "test_priced_wall_budget_limits"),
    "MEASURED_MARGIN": (1.0, "test_measured_plan_and_price_stop_receipt"),
    "DEFAULT_PLANNING_FACTOR": (1.0, "test_priced_wall_budget_admission_and_elapsed"),
    "MIN_PREDICTION": (0.0, "test_leave_one_out_and_bootstrap_sigma_hand_calculation"),
    "STEP_SIGMA": (0.0, "test_d2_negative_zero_and_bracket"),
    "FAMILY_ALPHA": (0.0, "test_hadronic_firing_bars"),
    "CONDITIONAL_ALPHA": (1.0, "test_hadronic_firing_bars"),
    "C0_LOW": (0.0, "test_c0_calibration_both_sigma_directions_and_offset"),
    "C0_HIGH": (1.0, "test_c0_calibration_both_sigma_directions_and_offset"),
    "C0_TAIL": (1.0, "test_c0_tail_count_and_family_guards"),
    "CE1_MIN": (0.0, "test_energy_algebra_only_and_controls"),
    "CE3_MEDIAN": (1.0, "test_energy_controls_each_stratum_and_bars"),
    "CE3_Q99": (1.0, "test_energy_controls_each_stratum_and_bars"),
    "OUTSIDE_MAX": (1.0, "test_flux_range_step_function_and_gate"),
    "NO_TRACK_MAX": (0.0, "test_d2_outcomes_and_revision_one_gap"),
    "TRACK_LOWER": (0.0, "test_d2_boundaries_and_signed_prediction_bar"),
    "TRACK_POINT": (0.0, "test_d2_boundaries_and_signed_prediction_bar"),
    "PARTIAL_LOWER": (0.0, "test_d2_outcomes_and_revision_one_gap"),
    "PREDICTION_P_MIN": (0.0, "test_d2_outcomes_and_revision_one_gap"),
    "CONFIDENCE_SIGMA": (1.0, "test_d2_boundaries_and_signed_prediction_bar"),
}


@dataclass(frozen=True)
class Mutation:
    """One required, independently executed mutation and its selecting tests."""

    name: str
    kind: str
    target: str
    selector: str
    replacement: float | None = None


RECORD_MUTATIONS = (
    Mutation(
        "REQUIRED_PREPARE_RUN_OBSERVED",
        "prepare_detail_side",
        "run.observed",
        "test_prepare_receipt_named_guards",
    ),
    Mutation(
        "REQUIRED_PREPARE_CONNECT_OBSERVED",
        "prepare_detail_side",
        "connect_id.observed",
        "test_prepare_receipt_named_guards",
    ),
    Mutation(
        "REQUIRED_PREPARE_CONNECT_PREPARED",
        "prepare_detail_none",
        "connect_id.prepared",
        "test_prepare_receipt_named_guards",
    ),
    Mutation(
        "REQUIRED_PREPARE_NOW_RECORDED",
        "prepare_detail_none",
        "age.now_ns",
        "test_prepare_receipt_named_guards",
    ),
    Mutation(
        "REQUIRED_PREPARE_AGE_RECORDED",
        "prepare_detail_none",
        "age.observed_age_ns",
        "test_prepare_receipt_named_guards",
    ),
    Mutation(
        "REQUIRED_DIFF_CHANGED_OBSERVED",
        "custody_diff_side",
        "changed.observed",
        "test_prepare_environment_whole_comparison",
    ),
    Mutation(
        "REQUIRED_DIFF_ADDED_VALUE",
        "custody_diff_none",
        "added",
        "test_prepare_environment_whole_comparison",
    ),
    Mutation(
        "REQUIRED_DIFF_REMOVED_VALUE",
        "custody_diff_none",
        "removed",
        "test_prepare_environment_whole_comparison",
    ),
    Mutation(
        "REQUIRED_DIFF_ADDED_NONPROTECTED",
        "custody_added_protected",
        "added",
        "test_prepare_environment_nonprotected_keys",
    ),
    Mutation(
        "REQUIRED_DIFF_NERSC_COVERED",
        "custody_env_filter",
        "nersc",
        "test_prepare_environment_nonprotected_keys",
    ),
    Mutation(
        "REQUIRED_DIFF_HOME_COVERED",
        "custody_env_filter",
        "home",
        "test_prepare_environment_nonprotected_keys",
    ),
    Mutation(
        "REQUIRED_PREPARE_LEGACY_SNAPSHOT_REQUIRED",
        "prepare_snapshot_optional",
        "MAT_PREPARE_PRESENT",
        "test_prepare_receipt_named_guards",
    ),
    Mutation(
        "REQUIRED_PREPARE_FIELDS_RECORDED",
        "prepare_detail_side",
        "presence.observed",
        "test_prepare_receipt_named_guards",
    ),
    Mutation(
        "REQUIRED_PREPARE_CONNECT_PRESENCE_RECORDED",
        "prepare_detail_side",
        "connect_presence.observed",
        "test_prepare_receipt_named_guards",
    ),
    Mutation(
        "REQUIRED_PREPARE_TIMESTAMP_RECORDED",
        "prepare_detail_none",
        "age.prepare_time_ns",
        "test_prepare_receipt_named_guards",
    ),
    Mutation(
        "REQUIRED_DIFF_CHANGED_PREPARED",
        "custody_diff_none",
        "changed.prepared",
        "test_prepare_environment_whole_comparison",
    ),
)


REQUIRED = tuple(
    [
        # #1069 follow-up (coverage-5b-audit g1, 2026-11-11): each receipt clause on its own
        Mutation(
            "REQUIRED_RECEIPT_ORIGINAL_IS_STR",
            "producer_r3",
            "mat_dependency_receipt",
            "test_mat_dependency_receipt_clauses",
            ("isinstance(entry['original'], str)", "True"),
        ),
        Mutation(
            "REQUIRED_RECEIPT_SHA_LENGTH",
            "producer_r3",
            "mat_dependency_receipt",
            "test_mat_dependency_receipt_clauses",
            ("len(entry['sha256']) == 64", "True"),
        ),
        Mutation(
            "REQUIRED_NEGATIVE_AFTER_EXIT_CHECK",
            "custody_r3",
            "missing_dependency_check",
            "test_negative_check_after_exit_library_custody and unpinned",
            (
                "classify_trace_with_stop(r, run, 'missing-dependency-trace', trace.read_text().splitlines(), trace_policy, {'policy_sha256': policy_sha, 'trace_sha256': r.digest(trace)})",
                "classify_trace(trace.read_text().splitlines(), trace_policy)",
            ),
        ),
        Mutation(
            "REQUIRED_EXIT_INSTRUMENT_PIN_ENFORCEMENT",
            "custody_r3",
            "classify_trace",
            "test_other_classes_cover_late_library_opens and instrument",
            (
                "any((_under(value, root) for value in paths for root in policy.get('instrument_directories', []))) and any((re.search('\\\\.so(?:\\\\.\\\\d+)*$|\\\\.dylib$', value) for value in paths)) and (endpoint not in policy['allowed'].get('pinned_mat_libs', []))",
                "False",
            ),
        ),
        Mutation(
            "REQUIRED_EXIT_OVIS_PIN_REQUIRED",
            "custody_r3",
            "pin_platform_libraries",
            "test_ovis_inventory_covers_committed_exit_loads",
            (
                "return pins",
                "return {name: pin for name, pin in pins.items() if Path(name).name != 'libldms.so.0.0.0'}",
            ),
        ),
        Mutation(
            "REQUIRED_EXIT_PLATFORM_PIN_ENFORCEMENT",
            "custody_r3",
            "classify_trace",
            "test_ovis_inventory_covers_committed_exit_loads",
            (
                "platform_library and endpoint not in policy.get('platform_library_pins', {})",
                "False",
            ),
        ),
        Mutation(
            "REQUIRED_EXIT_POST_CHECK_REQUIRED",
            "custody_r3",
            "classify_trace_with_stop",
            "test_real_atexit_library_load_is_checked_after_worker",
            ("check_trace_libraries(r, checked, policy)", "checked"),
        ),
        Mutation(
            "REQUIRED_EXIT_SUFFIXLESS_ELF_REQUIRED",
            "custody_r3",
            "check_trace_libraries",
            "test_post_exit_library_verification and suffixless",
            ("stream.read(4) == b'\\x7fELF'", "False"),
        ),
        Mutation(
            "REQUIRED_EXIT_PIN_CONTENT_REQUIRED",
            "custody_r3",
            "check_trace_libraries",
            "test_post_exit_library_verification and digest",
            ("observed != pins[endpoint]", "False"),
        ),
        Mutation(
            "REQUIRED_EXIT_INSTRUMENT_DIGEST_REQUIRED",
            "custody_r3",
            "check_trace_libraries",
            "test_instrument_post_exit_digest_refuses",
            ("observed['sha256'] != pins[endpoint]", "False"),
        ),
        Mutation(
            "REQUIRED_PREPARED_MAPPED_IDENTITY_REQUIRED",
            "custody_r3",
            "platform_library_record",
            "test_prepared_mapping_identity_refuses",
            ("mapping == expected_mapped[filename]", "True"),
        ),
        Mutation(
            "REQUIRED_PLATFORM_PREPARE_PINS",
            "custody_r3",
            "prepare",
            "test_fresh_prepare_stages_closed_inventory",
            (
                "pin_platform_libraries(r, instrument.mapped_files(), build_trace_policy(config, manifest, run))",
                "{}",
            ),
        ),
        Mutation(
            "REQUIRED_PLATFORM_PROLOGUE_PINS",
            "prologue_r3",
            "prepare",
            "test_prologue_prepare_opens_no_declared_data",
            (
                "custody.pin_platform_libraries(r, instrument.mapped_files(), custody.build_trace_policy(config, prepared, run))",
                "{}",
            ),
        ),
        Mutation(
            "REQUIRED_TRACE_UNFINISHED_RETAINED",
            "custody_r3",
            "complete_trace_calls",
            "test_trace_unpaired_calls_refuse and unfinished",
            (
                "pending[pid] = record",
                "retained.append({'pid': pid, 'raw_line': line, 'line_numbers': [number]})",
            ),
        ),
        Mutation(
            "REQUIRED_TRACE_PAIRS_SAME_PID",
            "custody_r3",
            "complete_trace_calls",
            "test_trace_interleaving_keeps_pid_and_every_line",
            (
                "pending_pid = pid",
                "pending_pid = next((candidate for candidate in pending if candidate != pid), pid)",
            ),
        ),
        Mutation(
            "REQUIRED_TRACE_DISJOINT_EXCLUSIONS",
            "custody_r3",
            "classify_successful_open",
            "test_trace_policy_disjoint_under_system_run",
            ("policy.get('class_exclusions', {}).get(category, [])", "[]"),
        ),
        Mutation(
            "REQUIRED_PLATFORM_WORKER_PIN_DIGEST",
            "custody_r3",
            "platform_library_record",
            "test_platform_worker_exact_pins",
            ("observed == expected[filename]", "True"),
        ),
        Mutation(
            "REQUIRED_PLATFORM_WORKER_EXACT_SET",
            "custody_r3",
            "platform_library_record",
            "test_platform_worker_exact_pins and (added or removed)",
            ("added or removed or inconsistent", "False"),
        ),
        Mutation(
            "REQUIRED_PLATFORM_WORKER_PROTECTED_FIRST",
            "custody_r3",
            "platform_library_record",
            "test_platform_worker_exact_pins and protected",
            (
                "any((_under(filename, root) for root in policy['protected_roots']))",
                "False",
            ),
        ),
        Mutation(
            "REQUIRED_TRACE_CLONE_CHDIR_ONLY",
            "custody_r3",
            "classify_trace",
            "test_trace_exact_clone_chdir_and_other_refusal",
            ("target is None or target != policy.get('clone_root')", "False"),
        ),
        Mutation(
            "REQUIRED_TRACE_STOP_PUBLIC_EXPORT",
            "custody_r3",
            "write_trace_record",
            "test_trace_stop_record_is_complete_public_and_cfs_first",
            ("public_record(record, {}, {})", "record"),
        ),
        Mutation(
            "REQUIRED_TRACE_STOP_WRITTEN",
            "custody_r3_stop",
            "classify_trace_with_stop",
            "test_trace_stop_record_is_complete_public_and_cfs_first",
            None,
        ),
        Mutation(
            "REQUIRED_TRACE_CHILD_CWD",
            "prologue_r3",
            "main",
            "test_prologue_child_environment_boundary",
            ("custody.trace_cwd(policy)", "None"),
        ),
        *RECORD_MUTATIONS,
        Mutation(
            "REQUIRED_IMPORT_PIN_CHANGED_ONLY",
            "custody_import_changed_only",
            "invalid_values",
            "test_import_pin_added_missing_and_unchanged",
        ),
        Mutation(
            "REQUIRED_PUBLIC_MODULE_NAME_NOT_ARTIFACT",
            "custody_module_name",
            "public_record",
            "test_public_module_names_are_not_artifacts",
        ),
        Mutation(
            "REQUIRED_NATIVE_ENVIRONMENT",
            "custody_native_copy",
            "native_environment",
            "test_native_runtime_changes_refuse",
        ),
        Mutation(
            "REQUIRED_RUNTIME_UUID_NOT_EXCLUDED",
            "runtime_uuid_exclusion",
            "checked_prepared_mat",
            "test_native_runtime_changes_refuse and NERSC_PYMON_UUID",
        ),
        Mutation(
            "REQUIRED_IMPORT_SIXTH_KEY",
            "custody_import_extra",
            "ROOT_IMPORT_KEYS",
            "test_import_diff_is_bounded",
        ),
        Mutation(
            "REQUIRED_IMPORT_ROOTSYS_REALPATH",
            "custody_import_root",
            "root_valid",
            "test_import_values_are_pinned and (ROOTSYS or unset_missing)",
        ),
        *[
            Mutation(
                "REQUIRED_IMPORT_PIN_" + key,
                "custody_import_pin",
                key,
                "test_import_values_are_pinned and " + key,
            )
            for key in ("CLING_STANDARD_PCH", "CPPYY_API_PATH", "CPPYY_NO_ROOT_FILTER")
        ],
        Mutation(
            "REQUIRED_PROLOGUE_EXPLICIT_ENVIRONMENT",
            "prologue_environment",
            "main",
            "test_prologue_child_environment_boundary",
        ),
        Mutation(
            "REQUIRED_WORKER_SNAPSHOT_BEFORE_ROOT",
            "root_import_first",
            "checked_prepared_mat",
            "test_worker_snapshot_before_root_and_runtime_recheck",
        ),
        Mutation(
            "REQUIRED_PRIVATE_PREPARE_LEAK",
            "custody_public_leak",
            "public_record",
            "test_private_prepare_public_outputs",
        ),
        *[
            Mutation(
                "REQUIRED_PRIVATE_" + name, "custody_guard_site", message, selector
            )
            for name, message, selector in (
                (
                    "PROTECTED",
                    "private prepare overlaps protected root",
                    "test_private_prepare_write_boundary and protected",
                ),
                (
                    "PERMISSIONS",
                    "private prepare directory is not owner-only",
                    "test_private_prepare_write_boundary and permissions",
                ),
                (
                    "RAW_SHA",
                    "private prepare digest differs",
                    "test_private_prepare_refuses and raw_sha",
                ),
                (
                    "REFERENCE_SHA",
                    "prepare reference digest differs",
                    "test_private_prepare_refuses and sha",
                ),
                (
                    "LOCATION",
                    "private prepare identity or location differs",
                    "test_private_prepare_refuses and location",
                ),
            )
        ],
        Mutation(
            "REQUIRED_ROOT_AUTODIRECTORY_OFF",
            "root_autodirectory",
            "histogram_directory_ownership",
            "test_root_reader_releases_before_close",
        ),
        Mutation(
            "REQUIRED_ROOT_PROXY_RELEASE",
            "root_release",
            "read_flux_histogram",
            "test_root_reader_releases_before_close",
        ),
        Mutation(
            "REQUIRED_REAL_WORKER_EXIT",
            "platform_check",
            "MAT_WORKER_EXIT",
            "test_real_mnv_worker_crash_cannot_publish_pass",
        ),
        *[
            Mutation(f"REQUIRED_CUSTODY_{guard}", "custody_guard", guard, selector)
            for guard, selector in CUSTODY_GUARD_TESTS.items()
        ],
        *[
            Mutation(
                f"REQUIRED_UNSAFE_EXCLUSION_{key}",
                "custody_unsafe_exclusion",
                key,
                "test_environment_exclusions_are_reviewed",
            )
            for key in (
                "LD_PRELOAD",
                "PYTHONPATH",
                "ROOT_INCLUDE_PATH",
                "ROOTSYS",
                "CLING_PREBUILT_MODULE_PATH",
            )
        ],
        Mutation(
            "REQUIRED_DICTIONARY_BEFORE_MAPS",
            "dictionary_order",
            "checked_prepared_mat",
            "test_lazy_dictionary_before_maps",
        ),
        Mutation(
            "REQUIRED_PREPARE_CALLS_FENCE",
            "custody_skip_fence",
            "prepare",
            "test_prepare_firing_guards and fence_call",
        ),
        Mutation(
            "REQUIRED_EXACT_PIN_PRECEDENCE",
            "custody_pin_priority",
            "classify_successful_open",
            "test_instrument_directory_scan_and_mapping",
        ),
        Mutation(
            "REQUIRED_NONPINNED_MAPPING",
            "custody_unmapped",
            "mapped_instrument_violations",
            "test_instrument_directory_scan_and_mapping",
        ),
        Mutation(
            "REQUIRED_ROOT_INTERPOLATION",
            "flux_step",
            "mat_flux_swap",
            "test_a1_root_interpolation_and_boundary",
        ),
        Mutation(
            "REQUIRED_ROOT_75_BOUNDARY",
            "flux_boundary",
            "mat_flux_swap",
            "test_a1_root_interpolation_and_boundary",
        ),
        Mutation(
            "REQUIRED_TIMING_FULL_AXES",
            "timing_axes",
            "TIMING_AXES",
            "test_timing_shape_matches_actual_aggregate_axes",
        ),
        Mutation(
            "REQUIRED_TRACE_PROTECTED_ATTEMPT",
            "custody_protected",
            "classify_trace",
            "test_custody_trace_directions",
        ),
        Mutation(
            "REQUIRED_TRACE_UNKNOWN_SUCCESS",
            "custody_unknown",
            "classify_trace",
            "test_custody_trace_directions",
        ),
        Mutation(
            "REQUIRED_TRACE_FAILED_SEARCH_ALLOWED",
            "custody_failed",
            "classify_trace",
            "test_custody_trace_directions",
        ),
        Mutation(
            "REQUIRED_COV2D_FENCE",
            "custody_fence",
            "cov2d_fence",
            "test_cov2d_fence_both_directions",
        ),
        *[
            Mutation(
                f"REQUIRED_ZERO_PATTERN_{i}",
                "flux_zero",
                "mat_flux_swap",
                "test_a1_every_zero_pattern",
                i,
            )
            for i in range(8)
        ],
        Mutation(
            "REQUIRED_CFS_ENTRY_ORDER",
            "output_order",
            "main",
            "test_cfs_precedes_other_refusals",
        ),
        Mutation(
            "REQUIRED_CFS_HANDLER_RECHECK",
            "handler_guard",
            "main",
            "test_cfs_handler_rechecks_before_stop_write",
        ),
        Mutation(
            "REQUIRED_PRICED_WALL_ROUTE",
            "priced_default",
            "wall_budget_seconds",
            "test_priced_wall_budget_admission_and_elapsed",
        ),
        Mutation(
            "REQUIRED_PRICED_WALL_ELAPSED",
            "clock_default",
            "check_wall_clock",
            "test_priced_wall_budget_admission_and_elapsed",
        ),
        Mutation(
            "REQUIRED_P0_ENVIRONMENT",
            "drop_environment",
            "p0",
            "test_p0_records_actual_environment",
        ),
        Mutation(
            "REQUIRED_KNOWN_SIBLING_ALLOWED",
            "sibling_empty",
            "known_sibling_names",
            "test_known_siblings_are_stat_only",
        ),
        Mutation(
            "REQUIRED_UNKNOWN_SIBLING_REFUSED",
            "sibling_extra",
            "known_sibling_names",
            "test_known_siblings_are_stat_only",
        ),
        Mutation(
            "REQUIRED_SIBLING_NEVER_OPENED",
            "sibling_open",
            "load_pins",
            "test_known_siblings_are_stat_only",
        ),
    ]
    + [
        Mutation(f"REQUIRED_GUARD_{name}", "guard", name, selector)
        for name, selector in GUARD_TESTS.items()
    ]
    + [
        Mutation(f"REQUIRED_BAR_{name}", "constant", name, selector, replacement)
        for name, (replacement, selector) in BAR_MUTANTS.items()
    ]
    + [
        Mutation(
            "REQUIRED_TWO_SIDED_STEP",
            "signed",
            "step_reading",
            "test_d2_negative_zero_and_bracket",
        ),
        Mutation(
            "REQUIRED_SHAPE_NDF",
            "ndf",
            "shape_score",
            "test_leave_one_out_and_bootstrap_sigma_hand_calculation",
        ),
        Mutation(
            "REQUIRED_LOO_REFERENCE",
            "loo",
            "leave_one_out",
            "test_leave_one_out_and_bootstrap_sigma_hand_calculation",
        ),
        Mutation(
            "REQUIRED_BACKGROUND_BRACKET",
            "bracket",
            "bracket_outcome",
            "test_d2_negative_zero_and_bracket",
        ),
        Mutation(
            "REQUIRED_BIN_EDGES",
            "edges",
            "bin_indices",
            "test_bins_deciles_and_reporting_cells",
        ),
        Mutation(
            "REQUIRED_BOOTSTRAP_SEEDS",
            "seed",
            "aggregate",
            "test_real_format_prediction_bins_readback_and_two_bootstrap_seeds",
        ),
        Mutation(
            "REQUIRED_RATE_POT",
            "pot",
            "_rate_summary",
            "test_rate_per_pot_guard_and_arithmetic",
        ),
        Mutation(
            "REQUIRED_PAIRED_SIZE_SIGMA",
            "paired_sigma",
            "_d2",
            "test_downstream_scoring_two_seeds",
        ),
    ]
)


class Mutator(ast.NodeTransformer):
    """Transform one named guard, constant or numerical expression."""

    def __init__(self, mutation: Mutation):
        self.mutation = mutation
        self.changed = 0
        self.function: str | None = None

    def visit(self, node: ast.AST) -> Any:
        mutation = self.mutation
        if (
            mutation.kind in {"custody_r3", "prologue_r3", "producer_r3"}
            and self.function == mutation.target
            and ast.unparse(node) == mutation.replacement[0]
        ):
            self.changed += 1
            replacement = ast.parse(mutation.replacement[1])
            return (
                replacement.body[0].value
                if isinstance(node, ast.expr)
                else replacement.body[0]
            )
        if (
            mutation.kind == "custody_r3_stop"
            and self.function == mutation.target
            and isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "write_trace_record"
        ):
            self.changed += 1
            return ast.Constant(None)
        return super().visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        previous = self.function
        self.function = node.name
        if (
            self.mutation.kind == "custody_native_copy"
            and node.name == self.mutation.target
        ):
            node.body = ast.parse("return dict(os.environ)").body
            self.changed += 1
            self.function = previous
            return node
        if (
            self.mutation.kind == "custody_public_leak"
            and node.name == self.mutation.target
        ):
            node.body = ast.parse("return value").body
            self.changed += 1
        elif (
            self.mutation.kind == "custody_unmapped"
            and node.name == self.mutation.target
        ):
            node.body = ast.parse("return []").body
            self.changed += 1
        elif (
            self.mutation.kind == "custody_fence" and node.name == self.mutation.target
        ):
            node.body = ast.parse("return {'status': 'PASS', 'exit_code': 0}").body
            self.changed += 1
        elif self.mutation.kind == "bracket" and node.name == self.mutation.target:
            node.body = [
                node.body[0],
                ast.Return(value=ast.Name(id="primary", ctx=ast.Load())),
            ]
            self.changed += 1
        else:
            self.generic_visit(node)
        if (
            self.mutation.kind == "root_import_first"
            and node.name == self.mutation.target
        ):
            index = next(
                i
                for i, statement in enumerate(node.body)
                if isinstance(statement, ast.Import)
                and any(alias.name == "ROOT" for alias in statement.names)
            )
            node.body.insert(1, node.body.pop(index))
            self.changed += 1
        if self.mutation.kind == "output_order" and node.name == self.mutation.target:
            for statement in node.body:
                if (
                    isinstance(statement, ast.Try)
                    and statement.body
                    and self._output_check(statement.body[0])
                ):
                    check = statement.body.pop(0)
                    statement.body.append(check)
                    self.changed += 1
                    break
        if self.mutation.kind == "priced_default" and node.name == self.mutation.target:
            for statement in node.body:
                if isinstance(statement, ast.Return):
                    statement.value = ast.Name(
                        id="DEFAULT_WALL_SECONDS", ctx=ast.Load()
                    )
                    self.changed += 1
        if (
            self.mutation.kind == "dictionary_order"
            and node.name == self.mutation.target
        ):
            indices = {
                statement.targets[0].id: i
                for i, statement in enumerate(node.body)
                if isinstance(statement, ast.Assign)
                and isinstance(statement.targets[0], ast.Name)
            }
            first, second = indices["dictionary"], indices["mapped"]
            node.body[first], node.body[second] = node.body[second], node.body[first]
            self.changed += 1
        if (
            self.mutation.kind == "custody_env_filter"
            and node.name == "environment_diff"
        ):
            condition = (
                "not key.startswith('NERSC_')"
                if self.mutation.target == "nersc"
                else "key != 'HOME'"
            )
            statement = ast.parse(
                "old_keys, new_keys = ({key for key in old_keys if "
                + condition
                + "}, {key for key in new_keys if "
                + condition
                + "})"
            ).body[0]
            index = next(
                i for i, item in enumerate(node.body) if isinstance(item, ast.Return)
            )
            node.body.insert(index, statement)
            self.changed += 1
        self.function = previous
        return node

    @staticmethod
    def _output_check(node: ast.AST) -> bool:
        return (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)
            and node.value.func.id == "require_output_root"
        )

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> ast.AST:
        if (
            self.mutation.kind == "handler_guard"
            and self.function == self.mutation.target
        ):
            for statement in node.body:
                if (
                    isinstance(statement, ast.Try)
                    and statement.body
                    and self._output_check(statement.body[0])
                ):
                    statement.body[0] = ast.Pass()
                    self.changed += 1
        return self.generic_visit(node)

    def visit_If(self, node: ast.If) -> ast.AST:
        mutation = self.mutation
        if (
            mutation.kind == "custody_pin_priority"
            and self.function == mutation.target
            and ast.unparse(node.test) == "paths & pinned"
        ):
            node.test = ast.Constant(False)
            self.changed += 1
        if self.function == mutation.target:
            if (
                mutation.kind == "custody_protected"
                and isinstance(node.test, ast.Name)
                and node.test.id == "protected"
            ):
                node.test = ast.Constant(False)
                self.changed += 1
            if (
                mutation.kind == "custody_failed"
                and isinstance(node.test, ast.Name)
                and node.test.id == "success"
            ):
                node.test = ast.Constant(True)
                self.changed += 1
            if (
                mutation.kind == "custody_unknown"
                and ast.unparse(node.test) == "len(categories) != 1"
            ):
                node.test = ast.Constant(False)
                self.changed += 1
        return self.generic_visit(node)

    def visit_Return(self, node: ast.Return) -> Any:
        if self.mutation.kind == "flux_zero" and self.function == self.mutation.target:
            self.changed += 1
            return [
                ast.parse(
                    f"factors[patterns == {int(self.mutation.replacement)}] = 0.123"
                ).body[0],
                node,
            ]
        return self.generic_visit(node)

    def visit_Compare(self, node: ast.Compare) -> ast.AST:
        if (
            self.mutation.kind == "flux_boundary"
            and self.function == self.mutation.target
            and ast.unparse(node) == "e > 75.0"
        ):
            node.ops = [ast.GtE()]
            self.changed += 1
        if (
            self.mutation.kind == "clock_default"
            and self.function == self.mutation.target
        ):
            for index, comparator in enumerate(node.comparators):
                if (
                    isinstance(comparator, ast.Attribute)
                    and comparator.attr == "wall_seconds"
                ):
                    node.comparators[index] = ast.Name(
                        id="DEFAULT_WALL_SECONDS", ctx=ast.Load()
                    )
                    self.changed += 1
        return self.generic_visit(node)

    def visit_Dict(self, node: ast.Dict) -> ast.AST:
        mutation = self.mutation
        if (
            mutation.kind in {"prepare_detail_side", "prepare_detail_none"}
            and self.function == "check_prepare_receipt"
        ):
            parent, field = mutation.target.split(".")
            for key, value in zip(node.keys, node.values):
                if (
                    isinstance(key, ast.Constant)
                    and key.value == parent
                    and isinstance(value, ast.Dict)
                ):
                    for index, child in enumerate(value.keys):
                        if isinstance(child, ast.Constant) and child.value == field:
                            expressions = {
                                "run.observed": "prepared['run']",
                                "connect_id.observed": "prepared['connect_id']",
                                "presence.observed": "sorted(required)",
                                "connect_presence.observed": "True",
                            }
                            value.values[index] = (
                                ast.Constant(None)
                                if mutation.kind == "prepare_detail_none"
                                else ast.parse(
                                    expressions[mutation.target], mode="eval"
                                ).body
                            )
                            self.changed += 1
        if (
            mutation.kind
            in {"custody_diff_side", "custody_diff_none", "custody_added_protected"}
            and self.function == "environment_diff"
        ):
            section, _, field = mutation.target.partition(".")
            for key, value in zip(node.keys, node.values):
                if (
                    isinstance(key, ast.Constant)
                    and key.value == section
                    and isinstance(value, ast.DictComp)
                ):
                    if mutation.kind == "custody_added_protected":
                        value.generators[0].ifs.append(
                            ast.parse("key.startswith(protected)", mode="eval").body
                        )
                        self.changed += 1
                    elif not field:
                        value.value = ast.Constant(None)
                        self.changed += 1
                    elif isinstance(value.value, ast.Dict):
                        for index, child in enumerate(value.value.keys):
                            if isinstance(child, ast.Constant) and child.value == field:
                                value.value.values[index] = (
                                    ast.Constant(None)
                                    if mutation.kind == "custody_diff_none"
                                    else ast.parse(
                                        "prepared['values'][key]", mode="eval"
                                    ).body
                                )
                                self.changed += 1
        if (
            self.mutation.kind == "drop_environment"
            and self.function == self.mutation.target
        ):
            for index, key in enumerate(node.keys):
                if isinstance(key, ast.Constant) and key.value == "environment":
                    del node.keys[index]
                    del node.values[index]
                    self.changed += 1
                    break
        return self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> ast.AST:
        mutation = self.mutation
        if (
            mutation.kind == "custody_import_changed_only"
            and any(
                isinstance(target, ast.Name) and target.id == "invalid_values"
                for target in node.targets
            )
            and isinstance(node.value, ast.DictComp)
        ):
            node.value.generators[0].ifs.append(
                ast.parse("key in diff['changed']", mode="eval").body
            )
            self.changed += 1
        if mutation.kind in {
            "custody_import_extra",
            "custody_import_root",
            "custody_import_pin",
        }:
            names = [
                target.id for target in node.targets if isinstance(target, ast.Name)
            ]
            if mutation.kind == "custody_import_extra" and "ROOT_IMPORT_KEYS" in names:
                node.value = ast.BinOp(
                    left=node.value,
                    op=ast.BitOr(),
                    right=ast.Set(elts=[ast.Constant("RPD_UNEXPECTED_IMPORT_KEY")]),
                )
                self.changed += 1
            elif mutation.kind == "custody_import_root" and "root_valid" in names:
                node.value = ast.Constant(True)
                self.changed += 1
            elif (
                mutation.kind == "custody_import_pin"
                and "ROOT_IMPORT_VALUES" in names
                and isinstance(node.value, ast.Dict)
            ):
                index = next(
                    i
                    for i, key in enumerate(node.value.keys)
                    if isinstance(key, ast.Constant) and key.value == mutation.target
                )
                del node.value.keys[index]
                del node.value.values[index]
                self.changed += 1
        if mutation.kind == "custody_unsafe_exclusion" and any(
            isinstance(target, ast.Name) and target.id == "ENVIRONMENT_EXCLUSIONS"
            for target in node.targets
        ):
            node.value = ast.parse(
                "{'_': 'shell', " + repr(mutation.target) + ": 'unsafe'}", mode="eval"
            ).body
            self.changed += 1
        if (
            mutation.kind == "custody_skip_fence"
            and self.function == "prepare"
            and any(isinstance(t, ast.Name) and t.id == "fence" for t in node.targets)
        ):
            node.value = ast.parse("{'status':'PASS','exit_code':0}", mode="eval").body
            self.changed += 1
        if mutation.kind == "timing_axes" and any(
            isinstance(t, ast.Name) and t.id == "TIMING_AXES" for t in node.targets
        ):
            self.changed += 1
            node.value = ast.parse(
                "tuple(x for x in " + ast.unparse(node.value) + " if x != 'rate@1')",
                mode="eval",
            ).body
        if mutation.kind in {"sibling_empty", "sibling_extra"} and any(
            isinstance(target, ast.Name) and target.id == mutation.target
            for target in node.targets
        ):
            node.value = (
                ast.Call(func=ast.Name(id="set", ctx=ast.Load()), args=[], keywords=[])
                if mutation.kind == "sibling_empty"
                else ast.BinOp(
                    left=node.value,
                    op=ast.BitOr(),
                    right=ast.Set(elts=[ast.Constant(value="nn_2A.npz")]),
                )
            )
            self.changed += 1
        if mutation.kind == "constant" and any(
            isinstance(target, ast.Name) and target.id == mutation.target
            for target in node.targets
        ):
            node.value = ast.Constant(value=mutation.replacement)
            self.changed += 1
        if (
            mutation.kind == "pot"
            and self.function == mutation.target
            and any(
                isinstance(target, ast.Name) and target.id == "exposure"
                for target in node.targets
            )
        ):
            node.value = ast.Constant(value=1.0)
            self.changed += 1
        if (
            mutation.kind == "paired_sigma"
            and self.function == mutation.target
            and any(
                isinstance(target, ast.Name) and target.id == "uncertainty"
                for target in node.targets
            )
        ):
            node.value = ast.Call(
                func=ast.Name(id="_sigma", ctx=ast.Load()),
                args=[ast.Name(id="by_playlist", ctx=ast.Load())],
                keywords=[],
            )
            self.changed += 1
        return self.generic_visit(node)

    def visit_For(self, node: ast.For) -> ast.AST:
        if (
            self.mutation.kind == "sibling_open"
            and self.function == self.mutation.target
            and isinstance(node.target, ast.Name)
            and node.target.id == "sibling_name"
        ):
            node.body.insert(
                1,
                ast.Expr(
                    value=ast.Call(
                        func=ast.Name(id="digest", ctx=ast.Load()),
                        args=[ast.Name(id="sibling_path", ctx=ast.Load())],
                        keywords=[],
                    )
                ),
            )
            self.changed += 1
        return self.generic_visit(node)

    def visit_Delete(self, node: ast.Delete) -> ast.AST:
        if (
            self.mutation.kind == "root_release"
            and self.function == self.mutation.target
        ):
            self.changed += 1
            return ast.Pass()
        return self.generic_visit(node)

    def visit_Raise(self, node: ast.Raise) -> ast.AST:
        """Disable an explicit refusal as well as predicate-based guards."""
        exception = node.exc
        if (
            self.mutation.kind == "guard"
            and isinstance(exception, ast.Call)
            and isinstance(exception.func, ast.Name)
            and exception.func.id == "Refused"
            and exception.args
            and isinstance(exception.args[0], ast.Constant)
            and exception.args[0].value == self.mutation.target
        ):
            self.changed += 1
            return ast.copy_location(ast.Pass(), node)
        return self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> ast.AST:
        if (
            self.mutation.kind == "prepare_snapshot_optional"
            and self.function == "check_prepare_receipt"
            and isinstance(node.func, ast.Name)
            and node.func.id == "require"
            and len(node.args) > 1
            and isinstance(node.args[1], ast.Constant)
            and node.args[1].value == "MAT_PREPARE_PRESENT"
        ):
            node.args[0] = ast.parse(
                "isinstance(prepared, dict) and {'run','connect_id','prepare_time_ns','environment_after_setup'} <= prepared.keys()",
                mode="eval",
            ).body
            self.changed += 1
        mutation = self.mutation
        if (
            mutation.kind == "custody_module_name"
            and self.function == "export"
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "split"
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "module"
        ):
            self.changed += 1
            return node.func.value
        if (
            mutation.kind == "runtime_uuid_exclusion"
            and self.function == "checked_prepared_mat"
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "environment_diff"
        ):
            for keyword in node.keywords:
                if keyword.arg == "exclusions":
                    keyword.value = ast.Constant(None)
                    self.changed += 1
        if (
            mutation.kind == "prologue_environment"
            and self.function == "main"
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "run"
        ):
            for keyword in node.keywords:
                if keyword.arg == "env":
                    keyword.value = ast.Constant(None)
                    self.changed += 1
        if (
            mutation.kind == "root_autodirectory"
            and self.function == mutation.target
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "AddDirectory"
            and node.args
            and isinstance(node.args[0], ast.Constant)
            and node.args[0].value is False
        ):
            node.args[0] = ast.Constant(True)
            self.changed += 1
        if (
            mutation.kind == "platform_check"
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "require"
            and len(node.args) > 1
            and isinstance(node.args[1], ast.Constant)
            and node.args[1].value == mutation.target
        ):
            node.args[0] = ast.Constant(True)
            self.changed += 1
        if (
            mutation.kind == "custody_guard_site"
            and isinstance(node.func, ast.Name)
            and node.func.id == "require"
            and len(node.args) > 1
            and isinstance(node.args[1], ast.Constant)
            and node.args[1].value == mutation.target
        ):
            node.args[0] = ast.Constant(True)
            self.changed += 1
        if (
            mutation.kind == "custody_guard"
            and isinstance(node.func, ast.Name)
            and node.func.id == "require"
        ):
            if any(
                k.arg == "guard"
                and isinstance(k.value, ast.Constant)
                and k.value.value == mutation.target
                for k in node.keywords
            ):
                node.args[0] = ast.Constant(True)
                self.changed += 1
        if (
            mutation.kind == "flux_step"
            and self.function == mutation.target
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "Interpolate"
        ):
            self.changed += 1
            return ast.Call(
                func=ast.Attribute(
                    value=node.func.value, attr="GetBinContent", ctx=ast.Load()
                ),
                args=[
                    ast.Call(
                        func=ast.Attribute(
                            value=node.func.value, attr="FindBin", ctx=ast.Load()
                        ),
                        args=node.args,
                        keywords=[],
                    )
                ],
                keywords=[],
            )
        if (
            mutation.kind == "guard"
            and isinstance(node.func, ast.Name)
            and node.func.id == "require"
            and len(node.args) > 1
            and isinstance(node.args[1], ast.Constant)
            and node.args[1].value == mutation.target
        ):
            node.args[0] = ast.Constant(value=True)
            self.changed += 1
        if (
            mutation.kind == "signed"
            and self.function == mutation.target
            and isinstance(node.func, ast.Name)
            and node.func.id == "abs"
        ):
            self.changed += 1
            return node.args[0]
        if (
            mutation.kind == "edges"
            and self.function == mutation.target
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "searchsorted"
        ):
            for keyword in node.keywords:
                if keyword.arg == "side":
                    keyword.value = ast.Constant(value="left")
                    self.changed += 1
        return self.generic_visit(node)

    def visit_BinOp(self, node: ast.BinOp) -> ast.AST:
        mutation = self.mutation
        if self.function == mutation.target and isinstance(node.op, ast.Sub):
            if (
                mutation.kind == "ndf"
                and isinstance(node.right, ast.Constant)
                and node.right.value == 1
            ):
                self.changed += 1
                return node.left
            if (
                mutation.kind == "loo"
                and isinstance(node.right, ast.Name)
                and node.right.id == "counts"
            ):
                self.changed += 1
                return node.left
        return self.generic_visit(node)

    def visit_List(self, node: ast.List) -> ast.AST:
        if (
            self.mutation.kind == "seed"
            and self.function == self.mutation.target
            and len(node.elts) == 3
            and isinstance(node.elts[0], ast.Constant)
            and node.elts[0].value == 20261104
            and isinstance(node.elts[1], ast.Constant)
            and node.elts[1].value == 11
        ):
            node.elts[1] = ast.Constant(value=12)
            self.changed += 1
        return self.generic_visit(node)


def run(output: Path, selected: set[str] | None = None) -> dict[str, Any]:
    """Run each required mutant; fail on survivors, errors, timeouts or missing guards."""
    source = PRODUCER.read_text()
    tree = ast.parse(source)
    guards = {
        node.args[1].value
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "require"
        and len(node.args) > 1
        and isinstance(node.args[1], ast.Constant)
    }
    if guards != set(GUARD_TESTS):
        raise RuntimeError(
            f"unmapped guards: {guards.symmetric_difference(GUARD_TESTS)}"
        )
    outcomes = []
    controls = []
    with tempfile.TemporaryDirectory(prefix="rpd-reco-mutants-") as temporary:
        shutil.copyfile(
            ROOT / "nd-unfolding/fd_rpd_inputs.py", Path(temporary) / "fd_rpd_inputs.py"
        )
        shutil.copyfile(
            ROOT / "nd-unfolding/fd_rpd_reco_custody.py",
            Path(temporary) / "fd_rpd_reco_custody.py",
        )
        control_dir = Path(temporary) / "comment-control"
        control_dir.mkdir()
        for filename in (
            "fd_rpd_inputs.py",
            "fd_ct_period_inputs.py",
            "fd_rpd_reco.py",
            "fd_rpd_reco_custody.py",
        ):
            shutil.copyfile(ROOT / "nd-unfolding" / filename, control_dir / filename)
        control_file = control_dir / "fd_rpd_reco_custody.py"
        control_file.write_text(
            control_file.read_text() + "\n# Byte-only custody control.\n"
        )
        control_command = [sys.executable, "-m", "pytest", "-q", str(TESTS)]
        if selected is not None:
            selectors = sorted({m.selector for m in REQUIRED if m.name in selected})
            control_command += [
                "-k",
                " or ".join(f"({selector})" for selector in selectors),
            ]
        control = subprocess.run(
            control_command,
            cwd=ROOT,
            env=os.environ
            | {
                "FD_RPD_RECO_MODULE": str(control_dir / "fd_rpd_reco.py"),
                "FD_RPD_CUSTODY_MODULE": str(control_file),
            },
            text=True,
            capture_output=True,
            check=False,
            timeout=600,
        )
        controls.append(
            {
                "name": "comment_only_custody",
                "returncode": control.returncode,
                "stdout": control.stdout,
                "stderr": control.stderr,
            }
        )
        if control.returncode != 0:
            output.write_text(
                json.dumps(
                    {"controls": controls, "all_killed": False, "complete": False},
                    indent=2,
                )
                + "\n"
            )
            raise RuntimeError(
                "comment-only custody control failed: "
                + control.stdout
                + control.stderr
            )
        print("PASS comment-only custody control", flush=True)
        for mutation in REQUIRED:
            if selected is not None and mutation.name not in selected:
                continue
            transformer = Mutator(mutation)
            custody_mutant = mutation.kind.startswith("custody_")
            platform_mutant = mutation.kind == "platform_check"
            prologue_mutant = mutation.kind in {"prologue_environment", "prologue_r3"}
            mutation_source = (
                (ROOT / "nd-unfolding/fd_rpd_reco_prologue.py").read_text()
                if prologue_mutant
                else (
                    (ROOT / "nd-unfolding/tests/fd_rpd_reco_mat_check.py").read_text()
                    if platform_mutant
                    else (
                        (ROOT / "nd-unfolding/fd_rpd_reco_custody.py").read_text()
                        if custody_mutant
                        else source
                    )
                )
            )
            changed = transformer.visit(ast.parse(mutation_source))
            if (
                mutation.kind
                in {
                    "custody_guard",
                    "custody_guard_site",
                    "custody_public_leak",
                    "custody_import_changed_only",
                    "custody_r3",
                    "custody_r3_stop",
                    "prologue_r3",
                    "producer_r3",
                }
                or mutation in RECORD_MUTATIONS
            ) and transformer.changed != 1:
                raise RuntimeError(
                    f"named custody mutation must change exactly one site: {mutation.name}, {transformer.changed}"
                )
            if transformer.changed == 0:
                raise RuntimeError(
                    f"mutation {mutation.name} did not change the producer"
                )
            directory = Path(temporary) / mutation.name
            directory.mkdir()
            for filename in (
                "fd_rpd_inputs.py",
                "fd_ct_period_inputs.py",
                "fd_rpd_reco.py",
                "fd_rpd_reco_custody.py",
            ):
                shutil.copyfile(ROOT / "nd-unfolding" / filename, directory / filename)
            (directory / "tests").mkdir()
            path = directory / (
                "tests/fd_rpd_reco_mat_check.py"
                if platform_mutant
                else (
                    "fd_rpd_reco_prologue.py"
                    if prologue_mutant
                    else (
                        "fd_rpd_reco_custody.py" if custody_mutant else "fd_rpd_reco.py"
                    )
                )
            )
            path.write_text(ast.unparse(ast.fix_missing_locations(changed)) + "\n")
            command = [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                str(TESTS),
                "-k",
                mutation.selector,
            ]
            completed = subprocess.run(
                command,
                cwd=ROOT,
                env=os.environ
                | {
                    **(
                        {"FD_RPD_PROLOGUE_MODULE": str(path)} if prologue_mutant else {}
                    ),
                    "FD_RPD_RECO_MODULE": str(directory / "fd_rpd_reco.py"),
                    "FD_RPD_CUSTODY_MODULE": str(directory / "fd_rpd_reco_custody.py"),
                    **(
                        {"FD_RPD_MAT_CHECK_MODULE": str(path)}
                        if platform_mutant
                        else {}
                    ),
                },
                text=True,
                capture_output=True,
                timeout=120,
                check=False,
            )
            killed = (
                completed.returncode == 1
                and " failed" in completed.stdout
                and "ERROR collecting" not in completed.stdout
            )
            outcome = {
                "name": mutation.name,
                "status": "KILLED" if killed else "SURVIVED_OR_ERROR",
                "selector": mutation.selector,
                "producer_mutant_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "returncode": completed.returncode,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
            }
            outcomes.append(outcome)
            print(f"{outcome['status']} {mutation.name}", flush=True)
    record = {
        "schema": "fd-rpd-reco-mutation/1",
        "producer_sha256": hashlib.sha256(PRODUCER.read_bytes()).hexdigest(),
        "tests_sha256": hashlib.sha256(TESTS.read_bytes()).hexdigest(),
        "prologue_sha256": hashlib.sha256(
            (ROOT / "nd-unfolding/fd_rpd_reco_prologue.py").read_bytes()
        ).hexdigest(),
        "custody_sha256": hashlib.sha256(
            (ROOT / "nd-unfolding/fd_rpd_reco_custody.py").read_bytes()
        ).hexdigest(),
        "required": [mutation.name for mutation in REQUIRED],
        "selected": sorted(selected) if selected else None,
        "controls": controls,
        "outcomes": outcomes,
        "complete": selected is None and len(outcomes) == len(REQUIRED),
        "all_killed": bool(outcomes)
        and all(outcome["status"] == "KILLED" for outcome in outcomes),
    }
    output.write_text(json.dumps(record, indent=2) + "\n")
    return record


def main() -> int:
    """Run the harness or print the immutable REQUIRED mutant names."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--only", action="append")
    parser.add_argument("--list", action="store_true")
    arguments = parser.parse_args()
    if arguments.list:
        print("\n".join(mutation.name for mutation in REQUIRED))
        return 0
    if arguments.out is None:
        parser.error("--out is required")
    result = run(arguments.out, set(arguments.only) if arguments.only else None)
    print(
        json.dumps(
            {
                "required": len(REQUIRED),
                "executed": len(result["outcomes"]),
                "killed": sum(
                    item["status"] == "KILLED" for item in result["outcomes"]
                ),
                "complete": result["complete"],
                "all_killed": result["all_killed"],
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return 0 if result["all_killed"] else 1


if __name__ == "__main__":
    sys.exit(main())
