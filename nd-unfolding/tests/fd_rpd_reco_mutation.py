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
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PRODUCER = ROOT / "nd-unfolding/fd_rpd_reco.py"
TESTS = ROOT / "nd-unfolding/tests/test_fd_rpd_reco.py"

GUARD_TESTS = {
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


REQUIRED = tuple(
    [
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

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        previous = self.function
        self.function = node.name
        if self.mutation.kind == "bracket" and node.name == self.mutation.target:
            node.body = [
                node.body[0],
                ast.Return(value=ast.Name(id="primary", ctx=ast.Load())),
            ]
            self.changed += 1
        else:
            self.generic_visit(node)
        self.function = previous
        return node

    def visit_Assign(self, node: ast.Assign) -> ast.AST:
        mutation = self.mutation
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
        mutation = self.mutation
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
    with tempfile.TemporaryDirectory(prefix="rpd-reco-mutants-") as temporary:
        for mutation in REQUIRED:
            if selected is not None and mutation.name not in selected:
                continue
            transformer = Mutator(mutation)
            changed = transformer.visit(ast.parse(source))
            if transformer.changed == 0:
                raise RuntimeError(
                    f"mutation {mutation.name} did not change the producer"
                )
            path = Path(temporary) / f"{mutation.name}.py"
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
                env=os.environ | {"FD_RPD_RECO_MODULE": str(path)},
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
        "required": [mutation.name for mutation in REQUIRED],
        "selected": sorted(selected) if selected else None,
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
    return 0 if result["all_killed"] else 1


if __name__ == "__main__":
    sys.exit(main())
