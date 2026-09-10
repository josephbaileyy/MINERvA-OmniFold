"""Exercise the file-to-artifact Z path with synthetic controls and mutations."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

ND = Path(__file__).resolve().parents[1]
if str(ND) not in sys.path:
    sys.path.insert(0, str(ND))

import p4_lib as p4
import z_build as build
import z_contract as contract
import z_receipt as receipt


def synthetic_fixture(directory: Path, scale: float = 1.0) -> tuple[Path, dict]:
    """Write declared synthetic files and return the manifest and output paths."""
    directory.mkdir(parents=True, exist_ok=True)
    revision = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ND, text=True
    ).strip()
    source_identity = {
        "revision": "synthetic-fixture",
        "import_closure_digests": {
            "test_z_build.py": receipt.sha256_file(Path(__file__))
        },
    }
    # Invented labels belong only to this explicitly synthetic support family.
    inventory = (
        *contract.VERT_BANDS,
        *contract.LATERAL_BANDS,
        *(f"synthetic_residual_{i}" for i in range(contract.N_RESIDUAL)),
    )
    support = {}
    for band in inventory:
        diagonal = [1, 2, 0] if band in contract.VERT_BANDS else [0.2, 0.3, 0.4]
        support[build.SUPPORT_PREFIX + band] = np.diag(diagonal) * scale
    np.savez(directory / "support.npz", **support)
    active = {
        p4.candidate_band_key(band): np.eye(3) * 0.5 * scale
        for band in contract.LATERAL_BANDS
    }
    active[p4.CANDIDATE_ACTIVE_TOTAL_KEY] = np.eye(3) * 2.5 * scale
    np.savez(directory / "active.npz", **active)
    np.savez(directory / "stat.npz", covariance=np.eye(3) * 0.7 * scale)
    np.savez(directory / "ml.npz", covariance=np.eye(3) * 0.1 * scale)
    # Bank diagonal deliberately differs from the sweep sum. They are not interchangeable.
    np.savez(
        directory / "throw.npz",
        C_unified=np.diag([4, 1, 0]) * scale,
        C_blocksum=np.diag([1, 2, 0]) * scale,
        hJointMeanShift=np.array([1, 2, 0]) * np.sqrt(scale),
    )
    central = np.array([2, 0, 4, 5, -1], dtype=float) * np.sqrt(scale)
    np.savez(directory / "central.npz", hXSecND_flat=central)
    receipt.persist_null_operands(
        directory / "null.npz",
        central,
        central.copy(),
        central > 0,
        code_identity=source_identity,
    )
    (directory / "parent.bin").write_bytes(
        b"synthetic parent; no scientific lineage asserted"
    )
    sources = {
        role: {
            "path": f"{role}.npz",
            "format": "npz",
            "sha256": receipt.sha256_file(directory / f"{role}.npz"),
        }
        for role in ("support", "active", "stat", "ml", "throw", "central", "null")
    }
    sources["parent"] = {
        "path": "parent.bin",
        "format": "opaque",
        "sha256": receipt.sha256_file(directory / "parent.bin"),
    }
    manifest = {
        "schema_version": 1,
        "input_kind": "synthetic",
        "run": {"id": "synthetic-control", "step": "assembly"},
        "producing_revision": revision,
        "sources": sources,
        "stat_key": "covariance",
        "ml_key": "covariance",
        "footing": {
            "mask_sha256": receipt.sha256_array(central > 0),
            "row_order_sha256": receipt.sha256_array(np.flatnonzero(central > 0)),
        },
    }
    path = directory / "manifest.json"
    path.write_text(json.dumps(manifest))
    outputs = {
        "out_cv": directory / "result-cv.npz",
        "out_mean": directory / "result-mean.npz",
        "receipt_cv": directory / "receipt-cv.json",
        "receipt_mean": directory / "receipt-mean.json",
        "out_null": directory / "result-null.npz",
    }
    return path, outputs


class ZBuildIntegration(unittest.TestCase):
    """All mutations start with an otherwise usable file-based control."""

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.manifest, self.outputs = synthetic_fixture(self.directory)

    def build(self) -> dict:
        return build.build_z(self.manifest, **self.outputs)

    def edit_manifest(self, change) -> None:
        manifest = json.loads(self.manifest.read_text())
        change(manifest)
        self.manifest.write_text(json.dumps(manifest))

    def mutate_source(self, role: str, change, *, rebind: bool = True) -> None:
        path = self.directory / f"{role}.npz"
        with np.load(path, allow_pickle=False) as store:
            arrays = {key: store[key] for key in store.files}
        change(arrays)
        np.savez(path, **arrays)
        if rebind:
            self.edit_manifest(
                lambda m: m["sources"][role].update(sha256=receipt.sha256_file(path))
            )

    def assert_no_outputs(self) -> None:
        self.assertFalse(any(path.exists() for path in self.outputs.values()))

    def test_complete_file_path_checks_both_variants_without_scientific_pass(
        self,
    ) -> None:
        order = []
        write_product, write_receipt = build._write_product, receipt.write_receipt

        def product(*args, **kwargs):
            order.append("product")
            return write_product(*args, **kwargs)

        def record(*args, **kwargs):
            order.append("receipt")
            self.assertTrue(self.outputs["out_cv"].exists())
            self.assertTrue(self.outputs["out_mean"].exists())
            self.assertTrue(self.outputs["out_null"].exists())
            return write_receipt(*args, **kwargs)

        with patch.object(build, "_write_product", side_effect=product), patch.object(
            receipt, "write_receipt", side_effect=record
        ):
            result = self.build()
        self.assertEqual(order, ["product", "product", "receipt", "receipt"])
        self.assertEqual(result["construction_status"], "CHECKED")
        self.assertEqual(result["scientific_acceptance"], "NON-PASSING")
        # Independent arithmetic: only the vertical sweep term is inflated.
        vert = np.array([13, 26, 0])
        remainder = np.array([5.4, 8.1, 10.8]) + 2.5 + 0.7 + 0.1
        for variant, g_squared in (
            ("mean", np.array([4, 1, 1])),
            ("cv", np.array([5, 2.5, 1])),
        ):
            with np.load(self.outputs[f"out_{variant}"]) as artifact:
                np.testing.assert_allclose(
                    artifact[build.TOTAL_KEY], np.diag(vert * g_squared + remainder)
                )
                np.testing.assert_array_equal(artifact["hRowIndex5D"], [0, 2, 3])
                self.assertEqual(artifact["hInflation_g"][-1], 1)
                # REVIEWER FINDING F1. The receipt assertions below already covered the
                # RECEIPT. Nothing covered the label embedded in the PRODUCT -- the bytes a
                # downstream consumer actually opens -- and the only assertion on it lived
                # in a test gated behind `skipUnless(find_spec("ROOT"))`. Measured: flipping
                # `adoptable` to True and `scientific_acceptance` to "PASSING" left the
                # documented test command fully green while both products advertised
                # themselves as adoptable. NPZ metadata needs no PyROOT, so this belongs in
                # the test that always runs.
                product_meta = json.loads(str(artifact["metadata_json"].item()))
                self.assertFalse(product_meta["adoptable"])
                self.assertEqual(product_meta["scientific_acceptance"], "NON-PASSING")
            rec = json.loads(self.outputs[f"receipt_{variant}"].read_text())
            self.assertFalse(rec["outcome"]["assessable"])
            self.assertIsNone(rec["outcome"]["branch"])
            self.assertFalse(rec["notes"]["adoptable"])
            self.assertEqual(
                set(rec["withheld_boundaries"]), set(contract.Z_BOUNDARIES)
            )
            self.assertEqual(
                rec["z"]["sha256"], receipt.sha256_file(self.outputs[f"out_{variant}"])
            )
            self.assertIn(receipt.RECONSTRUCTION_KEY, rec["inflation"])
            self.assertTrue(
                rec["inflation"][receipt.RECONSTRUCTION_KEY]["discriminating"]
            )
            self.assertEqual(rec["null"]["r_null"], 0)
            self.assertFalse(rec["null"]["assessment"]["assessable"])
            self.assertEqual(rec["parent"]["lineage_status"], "UNVERIFIED")
            self.assertTrue(
                all(c["status"] == "UNRESOLVED" for c in rec["causes"].values())
            )
            self.assertEqual(rec["negative_statement"], receipt.NEGATIVE_STATEMENT)

    def test_cross_section_scale_positive_control(self) -> None:
        self.manifest, self.outputs = synthetic_fixture(self.directory, scale=1e-76)
        self.assertEqual(self.build()["construction_status"], "CHECKED")

    def test_zero_shift_is_legal_and_reports_no_discrimination(self) -> None:
        self.mutate_source("throw", lambda a: a.update(hJointMeanShift=np.zeros(3)))
        self.build()
        rec = json.loads(self.outputs["receipt_cv"].read_text())
        self.assertFalse(rec["inflation"][receipt.RECONSTRUCTION_KEY]["discriminating"])
        with np.load(self.outputs["out_cv"]) as cv, np.load(
            self.outputs["out_mean"]
        ) as mean:
            np.testing.assert_array_equal(cv[build.TOTAL_KEY], mean[build.TOTAL_KEY])

    def test_internal_cv_mismatch_does_not_become_external_agreement(self) -> None:
        self.mutate_source(
            "central", lambda a: a.update(hXSecND_flat=a["hXSecND_flat"] * 1.01)
        )
        self.build()
        rec = json.loads(self.outputs["receipt_cv"].read_text())
        check = rec["null"]["declared_cv_crosscheck"]
        self.assertEqual(check["verdict"], "UNRESOLVED")
        # F4: the verdict must travel WITH the identity of what it was compared against
        # and WITH the statement that this is not the external check SS1.5 asks for.
        # Before the rename it was a bare string, and a reader had to go to
        # `notes.inputs` to learn what it meant -- if they knew to look.
        self.assertEqual(check["compared_against"]["role"], "central")
        self.assertEqual(check["compared_against"]["key"], "hXSecND_flat")
        self.assertEqual(
            check["compared_against"]["sha256"],
            receipt.sha256_file(self.directory / "central.npz"),
        )
        self.assertIn("NOT INDEPENDENT", check["independence"])
        self.assertEqual(check["external_crosscheck_status"], "UNPERFORMED")

    def test_an_agreeing_declared_crosscheck_still_disclaims_independence(self) -> None:
        """The PASSING direction, because F4's hazard is agreement that means nothing.

        `ELEMENTWISE_EQUAL` here is guaranteed by construction -- the fixture persists the
        same array the manifest declares as `central` -- so the field must not read as
        corroboration. The test above only covers the disagreeing direction, which is the
        one that was never in doubt.
        """
        self.build()
        rec = json.loads(self.outputs["receipt_cv"].read_text())
        check = rec["null"]["declared_cv_crosscheck"]
        self.assertEqual(check["verdict"], "ELEMENTWISE_EQUAL")
        self.assertIn("NOT INDEPENDENT", check["independence"])
        self.assertEqual(check["external_crosscheck_status"], "UNPERFORMED")
        self.assertNotIn("external_cv_crosscheck", rec["null"])

    def test_persisted_wrong_null_predicate_is_not_inherited(self) -> None:
        x1, x2, mask = receipt.load_null_operands(self.directory / "null.npz")
        mask[2] = False
        receipt.persist_null_operands(
            self.directory / "null.npz",
            x1,
            x2,
            mask,
            code_identity={
                "revision": "synthetic",
                "import_closure_digests": {"fixture": "synthetic"},
            },
        )
        self.edit_manifest(
            lambda m: m["sources"]["null"].update(
                sha256=receipt.sha256_file(self.directory / "null.npz")
            )
        )
        with self.assertRaisesRegex(
            contract.ZContractError, "persisted support predicate disagrees"
        ):
            self.build()
        self.assert_no_outputs()

    def test_forbidden_budget_keys_are_not_admitted_as_statistical_inputs(self) -> None:
        for key in ("C_unified", "C_seed"):
            self.edit_manifest(lambda m: m.update(stat_key=key))
            with self.assertRaisesRegex(
                contract.ZContractError, "cannot be a budget block"
            ):
                self.build()
            self.assert_no_outputs()

    def test_corrupted_receipt_cannot_be_reported_as_a_completed_build(self) -> None:
        def corrupt(path: Path, payload: dict) -> dict:
            path.write_text("{}")
            return receipt.stamp_file(path)

        with patch.object(receipt, "write_receipt", side_effect=corrupt):
            with self.assertRaisesRegex(
                contract.ZContractError, "receipt readback differs"
            ):
                self.build()
        self.assert_no_outputs()

    def test_uninflated_closed_object_is_rejected_by_existing_reconstruction(
        self,
    ) -> None:
        original = build._write_product

        def uninflated(path, arrays, metadata):
            arrays = dict(arrays)
            arrays["hInflation_g"] = np.ones(3)
            arrays[build.TOTAL_KEY] = np.diag(
                np.array([13, 26, 0]) + [5.4, 8.1, 10.8] + np.full(3, 3.3)
            )
            original(path, arrays, metadata)

        with patch.object(build, "_write_product", side_effect=uninflated):
            with self.assertRaisesRegex(contract.ZContractError, "g reconstruction"):
                self.build()
        self.assert_no_outputs()

    def test_dropped_shift_and_extra_budget_blocks_fail_closed(self) -> None:
        for mutation in ("dropped_shift", "added_unified", "inflated_residual"):
            with self.subTest(mutation=mutation):
                original = build._write_product

                def corrupt(path, arrays, metadata):
                    arrays = {key: value.copy() for key, value in arrays.items()}
                    if mutation == "dropped_shift" and metadata["variant"] == "cv":
                        arrays["hInflation_g"] = np.array([2, 1, 1])
                    elif mutation == "added_unified":
                        arrays[build.TOTAL_KEY] += np.diag([4, 1, 0])
                    elif mutation == "inflated_residual":
                        arrays[build.TOTAL_KEY] += np.diag([5.4, 8.1, 10.8])
                    original(path, arrays, metadata)

                with patch.object(build, "_write_product", side_effect=corrupt):
                    with self.assertRaisesRegex(
                        contract.ZContractError, "g reconstruction|closure identity"
                    ):
                        self.build()
                self.assert_no_outputs()

    def test_same_cardinality_wrong_rows_are_rejected_on_readback(self) -> None:
        original = build._write_product

        def corrupt(path, arrays, metadata):
            arrays = {**arrays, "hRowIndex5D": np.array([0, 3, 2])}
            original(path, arrays, metadata)

        with patch.object(build, "_write_product", side_effect=corrupt):
            with self.assertRaisesRegex(contract.ZContractError, "hRowIndex5D"):
                self.build()
        self.assert_no_outputs()

    def test_malformed_sources_fail_before_any_output(self) -> None:
        cases = [
            ("stat", lambda a: a.update(covariance=np.ones((2, 2))), "shape"),
            (
                "ml",
                lambda a: a.update(covariance=np.full((3, 3), np.nan)),
                "non-finite",
            ),
            (
                "stat",
                lambda a: a.update(covariance=np.full((3, 3), "1")),
                "real numeric",
            ),
            (
                "stat",
                lambda a: a.update(covariance=np.ones((3, 3), dtype=complex)),
                "real numeric",
            ),
            ("throw", lambda a: a.pop("hJointMeanShift"), "missing"),
            ("throw", lambda a: a.update(hJointMeanShift=np.ones((3, 1))), "shape"),
            ("null", lambda a: a.pop("schema_version"), "schema_version"),
            ("null", lambda a: a.update(schema_version=np.array(999)), "not supported"),
            (
                "active",
                lambda a: a.update({p4.CANDIDATE_ACTIVE_TOTAL_KEY: np.eye(3)}),
                "component sum",
            ),
            (
                "support",
                lambda a: a.pop(build.SUPPORT_PREFIX + contract.VERT_BANDS[0]),
                "absent from the support-family",
            ),
        ]
        for role, mutation, message in cases:
            with self.subTest(role=role, message=message):
                self.manifest, self.outputs = synthetic_fixture(self.directory)
                self.mutate_source(role, mutation)
                with self.assertRaisesRegex(contract.ZContractError, message):
                    self.build()
                self.assert_no_outputs()

    def test_non_psd_at_physical_scale_is_rejected(self) -> None:
        self.manifest, self.outputs = synthetic_fixture(self.directory, scale=1e-76)
        self.mutate_source(
            "ml",
            lambda a: a.update(
                covariance=np.array([[1, 500, 0], [500, 1, 0], [0, 0, 1]]) * 1e-76
            ),
        )
        with self.assertRaisesRegex(contract.ZContractError, "psd"):
            self.build()
        self.assert_no_outputs()

    def test_digest_drift_and_wrong_footing_are_rejected(self) -> None:
        self.mutate_source(
            "stat", lambda a: a.update(covariance=2 * a["covariance"]), rebind=False
        )
        with self.assertRaisesRegex(contract.ZContractError, "digest mismatch"):
            self.build()
        self.assert_no_outputs()
        self.manifest, self.outputs = synthetic_fixture(self.directory)
        self.edit_manifest(lambda m: m["footing"].update(row_order_sha256="a" * 64))
        with self.assertRaisesRegex(
            contract.ZContractError, "row_order_sha256 mismatch"
        ):
            self.build()

    def test_truncated_archive_has_an_explicit_contract_failure(self) -> None:
        path = self.directory / "stat.npz"
        path.write_bytes(path.read_bytes()[:20])
        self.edit_manifest(
            lambda m: m["sources"]["stat"].update(sha256=receipt.sha256_file(path))
        )
        with self.assertRaisesRegex(contract.ZContractError, "Z build refused"):
            self.build()
        self.assert_no_outputs()

    def test_existing_output_and_alias_are_never_overwritten(self) -> None:
        self.outputs["receipt_mean"].write_text("preserve me")
        with self.assertRaises(contract.ZContractError):
            self.build()
        self.assertEqual(self.outputs["receipt_mean"].read_text(), "preserve me")
        self.outputs["receipt_mean"].unlink()
        self.assert_no_outputs()
        self.outputs["out_cv"].symlink_to(self.directory / "support.npz")
        before = receipt.sha256_file(self.directory / "support.npz")
        with self.assertRaisesRegex(contract.ZContractError, "aliases an input"):
            self.build()
        self.assertEqual(before, receipt.sha256_file(self.directory / "support.npz"))

    def test_late_failure_removes_products_and_partial_receipts(self) -> None:
        original = receipt.write_receipt
        calls = []

        def fail_second(path, payload):
            calls.append(path)
            if len(calls) == 2:
                raise OSError("synthetic disk failure")
            return original(path, payload)

        with patch.object(receipt, "write_receipt", side_effect=fail_second):
            with self.assertRaisesRegex(
                contract.ZContractError, "synthetic disk failure"
            ):
                self.build()
        self.assertEqual(len(calls), 2)
        self.assert_no_outputs()

    def test_input_replacement_during_output_is_rejected(self) -> None:
        original = build._write_product

        def drift(*args):
            original(*args)
            (self.directory / "parent.bin").write_bytes(b"different parent")

        with patch.object(build, "_write_product", side_effect=drift):
            with self.assertRaisesRegex(contract.ZContractError, "source changed"):
                self.build()
        self.assert_no_outputs()

    def test_manifest_missing_unknown_duplicate_and_unapproved_fields(self) -> None:
        changes = [
            lambda m: m.update(schema_version=2),
            lambda m: m.update(schema_version=True),
            lambda m: m.pop("footing"),
            lambda m: m.update(boundaries={"null_epsilon": 1}),
            lambda m: m.update(producing_revision="main"),
            lambda m: m["run"].update(step=""),
        ]
        for mutation in changes:
            self.manifest, self.outputs = synthetic_fixture(self.directory)
            self.edit_manifest(mutation)
            with self.assertRaises(contract.ZContractError):
                self.build()
            self.assert_no_outputs()
        self.manifest.write_text('{"schema_version": 1, "schema_version": 1}')
        with self.assertRaisesRegex(contract.ZContractError, "duplicate key"):
            self.build()

    def test_a_usage_error_exits_1_with_the_envelope_not_2(self) -> None:
        """F2's fix needs a control, or it is one edit away from silently regressing.

        The confirming reviewer measured exactly that: reverting `_RefusingParser` to a plain
        `argparse.ArgumentParser` reinstates the original defect -- exit 2, no envelope, nothing
        written, indistinguishable by exit code from a finished non-passing build -- and the
        whole suite stays green. F1 was closed by ADDING A CONTROL; F2 was closed by changing
        behaviour and adding none, which is the same gap one level along.
        """
        with redirect_stderr(io.StringIO()) as error:
            with self.assertRaises(SystemExit) as raised:
                build.main([])
        self.assertEqual(raised.exception.code, 1)
        payload = json.loads(error.getvalue())
        self.assertEqual(payload["construction_status"], "FAILED")
        self.assertIn("usage:", payload["reason"])

    def test_an_unrecognized_argument_also_exits_1(self) -> None:
        """The other route into `error()`. argparse reports missing-required FIRST, so an
        unrecognized flag alone never reaches this branch -- it needs a complete valid argv."""
        args = ["--manifest", str(self.manifest)]
        for key, path in self.outputs.items():
            args.extend(["--" + key.replace("_", "-"), str(path)])
        with redirect_stderr(io.StringIO()) as error:
            with self.assertRaises(SystemExit) as raised:
                build.main([*args, "--bogus", "1"])
        self.assertEqual(raised.exception.code, 1)
        self.assertIn("unrecognized", json.loads(error.getvalue())["reason"])

    def test_cli_runs_and_returns_nonpassing_exit_code(self) -> None:
        args = ["--manifest", str(self.manifest)]
        for key, path in self.outputs.items():
            args.extend(["--" + key.replace("_", "-"), str(path)])
        with redirect_stdout(io.StringIO()) as output:
            self.assertEqual(build.main(args), 2)
        self.assertEqual(
            json.loads(output.getvalue())["scientific_acceptance"], "NON-PASSING"
        )
        with redirect_stderr(io.StringIO()) as error:
            self.assertEqual(build.main(args), 1)
        self.assertEqual(json.loads(error.getvalue())["construction_status"], "FAILED")

    @unittest.skipUnless(importlib.util.find_spec("ROOT"), "PyROOT unavailable")
    def test_root_sources_and_outputs_complete_the_same_path(self) -> None:
        manifest = json.loads(self.manifest.read_text())
        for role, declaration in manifest["sources"].items():
            if role in ("parent", "null"):
                continue
            source_path = self.directory / declaration["path"]
            with np.load(source_path) as store:
                arrays = {key: store[key] for key in store.files}
            root_path = source_path.with_suffix(".root")
            build._write_product(root_path, arrays, {"input_kind": "synthetic"})
            manifest["sources"][role] = {
                "path": root_path.name,
                "format": "root",
                "sha256": receipt.sha256_file(root_path),
            }
        self.manifest.write_text(json.dumps(manifest))
        for key in ("out_cv", "out_mean"):
            self.outputs[key] = self.outputs[key].with_suffix(".root")
        result = self.build()
        self.assertEqual(result["construction_status"], "CHECKED")
        for variant in ("cv", "mean"):
            path = self.outputs[f"out_{variant}"]
            with build.Source(
                {
                    "path": str(path),
                    "format": "root",
                    "sha256": receipt.sha256_file(path),
                },
                self.directory,
            ) as source:
                np.testing.assert_array_equal(source.read("hRowIndex5D"), [0, 2, 3])
                self.assertFalse(build._product_metadata(source)["adoptable"])
                expected = [73.7, 76.4, 14.1] if variant == "cv" else [60.7, 37.4, 14.1]
                np.testing.assert_allclose(
                    source.diagonal(build.TOTAL_KEY, 3), expected
                )

    @unittest.skipUnless(importlib.util.find_spec("ROOT"), "PyROOT unavailable")
    def test_root_matrix_orientation_and_missing_objects(self) -> None:
        path = self.directory / "orientation.root"
        matrix = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]])
        build._write_product(path, {"asymmetric": matrix}, {"input_kind": "synthetic"})
        with build.Source(
            {"path": str(path), "format": "root", "sha256": receipt.sha256_file(path)},
            self.directory,
        ) as source:
            np.testing.assert_array_equal(source.read("asymmetric"), matrix)
            np.testing.assert_array_equal(source.diagonal("asymmetric", 3), [1, 5, 9])
            with self.assertRaisesRegex(contract.ZContractError, "missing"):
                source.read("absent")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--write-fixture":
        manifest, outputs = synthetic_fixture(Path(sys.argv[2]).resolve())
        print(
            json.dumps(
                {
                    "manifest": str(manifest),
                    **{key: str(path) for key, path in outputs.items()},
                },
                indent=2,
            )
        )
    else:
        unittest.main()
