#!/usr/bin/env python3
"""Synthetic integration controls for the Z assembly/spectrum pilot and the null bridge.

WHY THE BRIDGE'S CHECKS ARE TESTED OVER ARRAYS. Reached only through `z_build.Source`, every
refusal in the transcription would be exercisable only under PyROOT -- and this repository's
PyROOT-gated tests SKIP on the default interpreter, which is F1 in Z_BUILD.md: an assertion whose
only test skips is an assertion with no test. `validate_transcription` and `transcribe_identity`
are pure, so these run everywhere. The ROOT round trip is gated and skips; it adds the file
binding, not the logic.
"""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

import numpy as np

ND = Path(__file__).resolve().parents[1]
if str(ND) not in sys.path:
    sys.path.insert(0, str(ND))

import z_build as build              # noqa: E402
import z_contract as contract        # noqa: E402
import z_null_bridge as bridge       # noqa: E402
import z_pilot as pilot              # noqa: E402
import z_receipt as receipt          # noqa: E402
import z_statistics as statistics    # noqa: E402
from test_z_build import synthetic_fixture  # noqa: E402


def _head() -> str:
    """The executing checkout's HEAD, which `z_build._code_identity` requires the manifest to name.

    The launcher passes `git -C "$CODE_ROOT" rev-parse HEAD`; a test that invented a sha would
    exercise the refusal instead of the completion path, which is how the first version of this
    test failed.
    """
    import subprocess
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ND, text=True).strip()


def _counts(x_cv, mask):
    x = np.asarray(x_cv, float)
    m = np.asarray(mask, bool)
    return {
        "n_cv_bins_total": int(x.size),
        "n_cv_support": int(m.sum()),
        "n_cv_genuine_zero": int(np.count_nonzero(x == 0.0)),
        "n_cv_negative": int(np.count_nonzero(x < 0.0)),
    }


class NullBridgeTranscription(unittest.TestCase):
    """The transcription checks, in both directions."""

    def setUp(self) -> None:
        self.x_cv = np.array([2.0, 0.0, 4.0, 5.0, -1.0])
        self.x_cv2 = self.x_cv * (1.0 + 1e-14)
        self.mask = (self.x_cv > 0).astype(float)
        self.counts = _counts(self.x_cv, self.mask)

    def _run(self, **over):
        kw = {
            "x_cv": self.x_cv, "x_cv2": self.x_cv2, "mask_raw": self.mask,
            "recorded_counts": self.counts, "declared_predicate": bridge.EXPECTED_PREDICATE,
        }
        kw.update(over)
        return bridge.validate_transcription(
            kw["x_cv"], kw["x_cv2"], kw["mask_raw"],
            recorded_counts=kw["recorded_counts"],
            declared_predicate=kw["declared_predicate"],
        )

    # ---- healthy positive control --------------------------------------------------------
    def test_a_VALID_transcription_returns_the_predicate_and_the_measured_counts(self):
        mask, measured, agreement = self._run()
        np.testing.assert_array_equal(mask, self.x_cv > 0)
        self.assertEqual(measured, self.counts)
        self.assertEqual(measured["n_cv_support"], 3)
        self.assertEqual(measured["n_cv_genuine_zero"], 1)
        self.assertEqual(measured["n_cv_negative"], 1)
        # Recorded, never graded: an invented tolerance is exactly what is refused here.
        self.assertFalse(agreement["graded"])
        self.assertFalse(agreement["operands_bitwise_identical"])
        self.assertIsNone(agreement.get("verdict"))

    def test_bitwise_identical_operands_are_RECORDED_not_refused(self):
        """Two identical vectors are a producer finding for an approver, not a bridge refusal.

        The bridge has no approved B/S/epsilon, so refusing here would be an invented tolerance
        and passing silently would hide it. It is recorded as a flag instead.
        """
        _, _, agreement = self._run(x_cv2=self.x_cv.copy())
        self.assertTrue(agreement["operands_bitwise_identical"])
        self.assertEqual(agreement["max_abs_difference"], 0.0)

    # ---- the bool-cast hazard, with the quantity that DEFINES it -------------------------
    def test_a_mask_value_outside_zero_one_is_REFUSED_before_the_bool_cast(self):
        bad = np.array([1.0, 0.5, 1.0, 1.0, 0.0])
        x = np.array([1.0, 1.0, 1.0, 1.0, -1.0])
        # THE HAZARD, measured: the cast this check precedes would make 0.5 read as selected,
        # and the result would then AGREE with the recomputed predicate -- so without this
        # check the laundered mask passes every later gate.
        self.assertTrue(np.array_equal(bad.astype(bool), statistics.support_mask(x)))
        with self.assertRaisesRegex(contract.ZContractError, r"outside \{0, 1\}"):
            self._run(x_cv=x, x_cv2=x.copy(), mask_raw=bad, recorded_counts=_counts(x, bad))

    def test_a_mask_disagreeing_with_the_recomputed_predicate_is_REFUSED(self):
        wrong = np.array([1.0, 1.0, 1.0, 1.0, 0.0])  # claims the genuine zero is in support
        with self.assertRaisesRegex(contract.ZContractError, "disagrees with"):
            self._run(mask_raw=wrong, recorded_counts=_counts(self.x_cv, wrong))

    def test_a_DIFFERENT_declared_predicate_is_refused_not_assumed_equivalent(self):
        with self.assertRaisesRegex(contract.ZContractError, "transcribes only"):
            self._run(declared_predicate="x_cv >= 0")

    def test_a_recorded_count_disagreeing_with_its_array_is_REFUSED(self):
        bad = dict(self.counts, n_cv_support=99)
        with self.assertRaisesRegex(contract.ZContractError, "disagree with the arrays"):
            self._run(recorded_counts=bad)

    def test_recorded_counts_must_be_exactly_the_declared_set(self):
        with self.assertRaisesRegex(contract.ZContractError, "must be exactly"):
            self._run(recorded_counts={"n_cv_support": 3})

    def test_mismatched_operand_shapes_are_REFUSED(self):
        with self.assertRaisesRegex(contract.ZContractError, "shapes differ"):
            self._run(x_cv2=np.array([1.0, 2.0]))

    def test_non_finite_operands_are_REFUSED(self):
        bad = self.x_cv.copy(); bad[0] = np.nan
        with self.assertRaisesRegex(contract.ZContractError, "non-finite"):
            self._run(x_cv2=bad)

    def test_an_empty_support_is_REFUSED(self):
        x = np.array([-1.0, -2.0, 0.0])
        m = np.zeros(3)
        with self.assertRaisesRegex(contract.ZContractError, "empty"):
            self._run(x_cv=x, x_cv2=x.copy(), mask_raw=m, recorded_counts=_counts(x, m))


class NullBridgeIdentity(unittest.TestCase):
    """The producer's identity is transcribed, and it is NOT the assembling revision."""

    PROV = {
        "cv_code_revision": "e09513d842ad3acc1964c1af740696f02eaed7d9",
        "cv_producer_file": "unified_throw_cov.py",
        "cv_producer_sha256": "dbf423052e23854d61e8c420ad33a4ec33eae36edc215f8779119456d1cee884",
    }

    def test_the_identity_names_the_PRODUCER_revision_and_a_measured_digest(self):
        identity = bridge.transcribe_identity(self.PROV)
        self.assertEqual(identity["revision"], self.PROV["cv_code_revision"])
        self.assertEqual(
            identity["import_closure_digests"]["unified_throw_cov.py"],
            self.PROV["cv_producer_sha256"],
        )
        # It must satisfy the slab writer's own contract, not merely look like it.
        receipt._require_code_identity(identity, "test")

    def test_a_CONFLICTING_caller_digest_is_refused_rather_than_preferred(self):
        with self.assertRaisesRegex(contract.ZContractError, "conflict is refused"):
            bridge.transcribe_identity(
                self.PROV, {"unified_throw_cov.py": "0" * 64}
            )

    def test_an_additional_module_digest_is_merged(self):
        identity = bridge.transcribe_identity(self.PROV, {"z_statistics.py": "a" * 64})
        self.assertEqual(len(identity["import_closure_digests"]), 2)

    def test_incomplete_provenance_is_REFUSED(self):
        with self.assertRaisesRegex(contract.ZContractError, "must be exactly"):
            bridge.transcribe_identity({"cv_code_revision": "x" * 40})

    def test_the_persisted_slab_CARRIES_the_producer_identity_through_a_round_trip(self):
        """End to end on the slab: write with the producer's identity, read it back out."""
        identity = bridge.transcribe_identity(self.PROV)
        x = np.array([2.0, 0.0, 4.0])
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "null.npz"
            bridge.receipt.persist_null_operands(
                path, x, x * (1 + 1e-15), x > 0, code_identity=identity
            )
            with np.load(path, allow_pickle=False) as store:
                decl = json.loads(str(store["declaration_json"]))
            self.assertEqual(
                decl["writer"]["code_identity"]["revision"], self.PROV["cv_code_revision"]
            )
            # The assembling revision must NOT have replaced it.
            self.assertNotEqual(
                decl["writer"]["code_identity"]["revision"], "HEAD"
            )


class SpectrumDiagnostics(unittest.TestCase):
    def test_the_spectrum_is_reported_and_NOT_clipped(self):
        C = np.diag([3.0, 2.0, 1.0])
        d = pilot.spectrum_diagnostics(C, label="cv")
        self.assertFalse(d["clipped"])
        self.assertFalse(d["regularized"])
        self.assertAlmostEqual(d["lambda_min"], 1.0)
        self.assertAlmostEqual(d["lambda_max"], 3.0)
        self.assertEqual(d["n_negative"], 0)
        self.assertIsNone(d["verdict"])
        self.assertEqual(d["quantiles"]["q1"], 3.0)

    def test_a_NEGATIVE_eigenvalue_is_counted_and_measured_not_removed(self):
        C = np.diag([3.0, -1e-9])
        d = pilot.spectrum_diagnostics(C, label="mean")
        self.assertEqual(d["n_negative"], 1)
        self.assertLess(d["lambda_min"], 0.0)
        self.assertGreater(d["neg_fraction_of_max"], 0.0)

    def test_the_report_is_SCALE_FREE_in_the_ratio_the_psd_gate_uses(self):
        """Z's covariances live at ~1e-38; an absolute floor here would be this campaign's bug."""
        base = np.array([[1.0, 2.0], [2.0, 1.0]])
        a = pilot.spectrum_diagnostics(base, label="a")
        b = pilot.spectrum_diagnostics(base * 1e-76, label="b")
        self.assertAlmostEqual(a["neg_fraction_of_max"], b["neg_fraction_of_max"], places=12)

    def test_a_non_square_or_non_finite_matrix_is_REFUSED(self):
        with self.assertRaisesRegex(contract.ZContractError, "not square"):
            pilot.spectrum_diagnostics(np.zeros((2, 3)), label="x")
        with self.assertRaisesRegex(contract.ZContractError, "non-finite"):
            pilot.spectrum_diagnostics(np.array([[np.nan, 0.0], [0.0, 1.0]]), label="x")


class PilotEndToEnd(unittest.TestCase):
    """The pilot over the explicitly synthetic family, including its refusals."""

    def setUp(self) -> None:
        self.td = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.td, ignore_errors=True)
        self.fixture_manifest, _ = synthetic_fixture(self.td / "fx")

    def _sources_from_fixture(self):
        decl = json.loads(self.fixture_manifest.read_text())["sources"]
        return {
            role: {
                "path": str((self.fixture_manifest.parent / spec["path"]).resolve()),
                "format": spec["format"],
            }
            for role, spec in decl.items()
        }

    def test_the_manifest_binds_every_source_by_MEASURED_digest(self):
        out = pilot.build_manifest(
            self.td / "m.json",
            sources=self._sources_from_fixture(),
            run={"id": "pilot-control", "step": "assembly"},
            producing_revision="0" * 40,
            stat_key="covariance", ml_key="covariance", input_kind="synthetic",
            provenance_path=self.td / "prov.json",
        )
        manifest = json.loads((self.td / "m.json").read_text())
        self.assertEqual(set(manifest["sources"]), set(pilot.SOURCE_ROLES))
        for role, spec in manifest["sources"].items():
            self.assertEqual(spec["sha256"], receipt.sha256_file(Path(spec["path"])), role)
        # Footing is DERIVED, and must be what build_z will recompute.
        central = np.load(manifest["sources"]["central"]["path"])["hXSecND_flat"]
        mask = statistics.support_mask(central)
        self.assertEqual(manifest["footing"]["mask_sha256"], receipt.sha256_array(mask))
        self.assertEqual(
            manifest["footing"]["row_order_sha256"],
            receipt.sha256_array(np.flatnonzero(mask).astype(np.int64)),
        )
        prov = json.loads((self.td / "prov.json").read_text())
        self.assertFalse(prov["adoptable"])
        self.assertEqual(prov["scientific_acceptance"], "NON-PASSING")
        self.assertEqual(
            set(prov["band_membership"]["bands_vert"]), set(contract.VERT_BANDS)
        )
        self.assertEqual(out["provenance"]["band_membership"]["partition"],
                         prov["band_membership"]["partition"])

    def test_a_WRONG_expected_digest_is_refused(self):
        sources = self._sources_from_fixture()
        sources["throw"]["expect_sha256"] = "0" * 64
        with self.assertRaisesRegex(contract.ZContractError, "not the one authorized"):
            pilot.build_manifest(
                self.td / "m2.json", sources=sources,
                run={"id": "r", "step": "s"}, producing_revision="0" * 40,
                stat_key="covariance", ml_key="covariance", input_kind="synthetic",
            )

    def test_a_ROOT_null_source_is_refused_with_the_bridge_named(self):
        sources = self._sources_from_fixture()
        sources["null"]["format"] = "root"
        with self.assertRaisesRegex(contract.ZContractError, "z_null_bridge"):
            pilot.build_manifest(
                self.td / "m3.json", sources=sources,
                run={"id": "r", "step": "s"}, producing_revision="0" * 40,
                stat_key="covariance", ml_key="covariance", input_kind="synthetic",
            )

    def test_an_existing_manifest_is_not_overwritten(self):
        (self.td / "m4.json").write_text("{}")
        with self.assertRaisesRegex(contract.ZContractError, "allow_overwrite"):
            pilot.build_manifest(
                self.td / "m4.json", sources=self._sources_from_fixture(),
                run={"id": "r", "step": "s"}, producing_revision="0" * 40,
                stat_key="covariance", ml_key="covariance", input_kind="synthetic",
            )

    # ---- the exit-2 contract -------------------------------------------------------------
    def test_a_COMPLETED_build_is_validated_and_exit_two_is_PRESERVED(self):
        result = pilot.run_pilot(self.fixture_manifest, out_dir=self.td / "out")
        self.assertEqual(result["build_returncode"], pilot.BUILD_COMPLETION_RC)
        self.assertEqual(result["scientific_acceptance"], "NON-PASSING")
        self.assertFalse(result["adoptable"])
        self.assertEqual(result["build_result"]["construction_status"], "CHECKED")
        self.assertEqual(set(result["spectra"]), {"cv", "mean"})
        for variant, spec in result["spectra"].items():
            self.assertFalse(spec["clipped"], variant)
            self.assertGreater(spec["lambda_max"], 0.0, variant)
        # RECEIPT LAST: it is newer than every artifact it describes.
        rpath = Path(result["receipt"])
        for stamp in result["artifacts"].values():
            self.assertLessEqual(
                Path(stamp["path"]).stat().st_mtime_ns, rpath.stat().st_mtime_ns
            )

    def test_the_cli_returns_TWO_and_never_converts_it_to_zero(self):
        rc = pilot.main([
            "--manifest", str(self.fixture_manifest), "--out-dir", str(self.td / "cli"),
        ])
        self.assertEqual(rc, pilot.BUILD_COMPLETION_RC)
        self.assertNotEqual(rc, 0)

    def test_a_MISSING_receipt_makes_exit_two_INCOMPLETE(self):
        out = self.td / "out2"
        result = pilot.run_pilot(self.fixture_manifest, out_dir=out)
        Path(result["artifacts"]["receipt_mean"]["path"]).unlink()
        artifacts = {k: v["path"] for k, v in result["artifacts"].items()}
        with self.assertRaisesRegex(contract.ZContractError, "absent"):
            pilot._validate_completion(
                pilot.BUILD_COMPLETION_RC, json.dumps(result["build_result"]), artifacts
            )

    def test_a_product_that_does_not_match_its_receipt_is_REFUSED(self):
        out = self.td / "out3"
        result = pilot.run_pilot(self.fixture_manifest, out_dir=out)
        product = Path(result["artifacts"]["out_cv"]["path"])
        product.write_bytes(product.read_bytes() + b"\x00")
        artifacts = {k: v["path"] for k, v in result["artifacts"].items()}
        with self.assertRaisesRegex(contract.ZContractError, "does not describe the file"):
            pilot._validate_completion(
                pilot.BUILD_COMPLETION_RC, json.dumps(result["build_result"]), artifacts
            )

    def test_exit_ONE_is_a_construction_failure_and_validates_nothing(self):
        with self.assertRaisesRegex(contract.ZContractError, "construction failed"):
            pilot._validate_completion(pilot.BUILD_FAILURE_RC, "{}", {})

    def test_exit_ZERO_is_not_accepted_as_completion(self):
        with self.assertRaisesRegex(contract.ZContractError, "only completion code"):
            pilot._validate_completion(0, "{}", {})

    def test_a_PASSING_claim_in_the_build_output_is_refused(self):
        """A build reporting adoptable or PASSING contradicts this construction's status."""
        out = self.td / "out4"
        result = pilot.run_pilot(self.fixture_manifest, out_dir=out)
        artifacts = {k: v["path"] for k, v in result["artifacts"].items()}
        forged = dict(result["build_result"], adoptable=True)
        with self.assertRaisesRegex(contract.ZContractError, "non-adoptable"):
            pilot._validate_completion(
                pilot.BUILD_COMPLETION_RC, json.dumps(forged), artifacts
            )
        forged2 = dict(result["build_result"], scientific_acceptance="PASSING")
        with self.assertRaisesRegex(contract.ZContractError, "scientific_acceptance"):
            pilot._validate_completion(
                pilot.BUILD_COMPLETION_RC, json.dumps(forged2), artifacts
            )

    def test_a_non_json_stdout_beside_exit_two_is_REFUSED(self):
        with self.assertRaisesRegex(contract.ZContractError, "not JSON"):
            pilot._validate_completion(pilot.BUILD_COMPLETION_RC, "built fine", {})

    def test_the_receipt_digest_is_matched_BY_PATH_not_by_position(self):
        """Selecting by order would compare cv against mean's digest and pass either way."""
        out = self.td / "out5"
        result = pilot.run_pilot(self.fixture_manifest, out_dir=out)
        record = json.loads(Path(result["artifacts"]["receipt_cv"]["path"]).read_text())
        cv = Path(result["artifacts"]["out_cv"]["path"])
        mean = Path(result["artifacts"]["out_mean"]["path"])
        self.assertNotEqual(
            pilot._find_product_sha(record, cv), pilot._find_product_sha(record, mean)
        )
        self.assertEqual(pilot._find_product_sha(record, cv), receipt.sha256_file(cv))

    def test_an_INPUT_SUPPORT_mismatch_refuses_the_build_and_the_pilot_reports_it(self):
        """A footing digest that does not describe the declared central must not build."""
        manifest = json.loads(self.fixture_manifest.read_text())
        manifest["footing"]["mask_sha256"] = "0" * 64
        bad = self.td / "bad-manifest.json"
        bad.write_text(json.dumps(manifest))
        with self.assertRaises(contract.ZContractError):
            pilot.run_pilot(bad, out_dir=self.td / "out6")
        rc = pilot.main(["--manifest", str(bad), "--out-dir", str(self.td / "out7")])
        self.assertEqual(rc, pilot.BUILD_FAILURE_RC)


class LauncherCliSequence(unittest.TestCase):
    """The exact two commands `sbatch_z_pilot_5d.sh` runs, in order, end to end.

    The launcher's steps are tested as COMMANDS, not as functions: the manifest CLI's argument
    wiring and the pilot CLI's exit code are what the shell actually depends on, and a test that
    called `build_manifest` directly would leave both unexercised.
    """

    def setUp(self) -> None:
        self.td = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.td, ignore_errors=True)
        self.fx, _ = synthetic_fixture(self.td / "fx")
        self.decl = json.loads(self.fx.read_text())["sources"]

    def _arg(self, role):
        return str((self.fx.parent / self.decl[role]["path"]).resolve())

    def test_the_manifest_cli_then_the_pilot_cli_complete_with_exit_two(self):
        import z_pilot_manifest_cli as cli
        manifest = self.td / "m.json"
        argv = [
            "--out", str(manifest), "--provenance", str(self.td / "prov.json"),
            "--producing-revision", _head(),
            "--run-id", "pilot-cli-control", "--run-step", "assembly",
            "--input-kind", "synthetic",
            "--stat-key", "covariance", "--ml-key", "covariance",
            "--throw-sha256", receipt.sha256_file(Path(self._arg("throw"))),
        ]
        for role in pilot.SOURCE_ROLES:
            argv += [f"--{role}", self._arg(role)]
        self.assertEqual(cli.main(argv), 0)
        bound = json.loads(manifest.read_text())
        self.assertEqual(bound["run"]["id"], "pilot-cli-control")
        self.assertEqual(
            bound["sources"]["throw"]["sha256"],
            receipt.sha256_file(Path(self._arg("throw"))),
        )
        rc = pilot.main(["--manifest", str(manifest), "--out-dir", str(self.td / "out")])
        self.assertEqual(rc, pilot.BUILD_COMPLETION_RC)
        r = json.loads((self.td / "out" / "z-pilot-receipt.json").read_text())
        self.assertFalse(r["adoptable"])
        self.assertEqual(r["scientific_acceptance"], "NON-PASSING")

    def test_the_manifest_cli_refuses_a_wrong_authorized_digest(self):
        import z_pilot_manifest_cli as cli
        argv = [
            "--out", str(self.td / "m2.json"),
            "--producing-revision", "0" * 40,
            "--run-id", "r", "--run-step", "s", "--input-kind", "synthetic",
            "--stat-key", "covariance", "--ml-key", "covariance",
            "--throw-sha256", "0" * 64,
        ]
        for role in pilot.SOURCE_ROLES:
            argv += [f"--{role}", self._arg(role)]
        self.assertEqual(cli.main(argv), 1)
        self.assertFalse((self.td / "m2.json").exists())


class LauncherStaticChecks(unittest.TestCase):
    """Properties of the launcher file itself that a synthetic run cannot reach."""

    LAUNCHER = ND / "sbatch_z_pilot_5d.sh"

    def setUp(self) -> None:
        self.text = self.LAUNCHER.read_text()

    def test_the_launcher_declares_no_requeue_and_explicit_limits(self):
        self.assertIn("#SBATCH --no-requeue", self.text)
        for flag in ("--time=", "--mem=", "--cpus-per-task="):
            self.assertIn(flag, self.text, flag)

    def test_every_module_the_pilot_executes_is_bound_by_a_parity_pair(self):
        """A module that does the work while unbound is the gap parity exists to close."""
        for module in ("z_pilot.py", "z_null_bridge.py", "z_pilot_manifest_cli.py",
                       "z_build.py", "z_assembly.py", "z_receipt.py", "z_contract.py",
                       "z_statistics.py", "z_validator.py", "z_build_path.py"):
            self.assertIn(f"=nd-unfolding/{module}", self.text, module)

    def test_the_launcher_does_not_convert_exit_two_to_zero(self):
        self.assertIn("2) echo \"[z-pilot] construction COMPLETE", self.text)
        self.assertNotIn("exit 0", self.text)

    def test_the_launcher_refuses_a_non_empty_output_directory_rather_than_cleaning_it(self):
        self.assertIn("is NOT empty", self.text)
        for destructive in ("rm -rf", "rm -r ", "shutil.rmtree"):
            self.assertNotIn(destructive, self.text, destructive)

    def test_every_pilot_operand_is_mandatory_with_no_default(self):
        for var in ("MNV_Z_PRECURSOR_PRODUCT", "MNV_Z_PRECURSOR_SHA256", "MNV_Z_PILOT_OUT",
                    "MNV_Z_CENTRAL", "MNV_Z_SUPPORT", "MNV_Z_ACTIVE", "MNV_Z_STAT",
                    "MNV_Z_ML", "MNV_Z_PARENT", "MNV_Z_STAT_KEY", "MNV_Z_ML_KEY"):
            self.assertIn(f"${{{var}:?", self.text, var)


try:  # pragma: no cover - environment probe
    import ROOT  # noqa: F401
    HAVE_ROOT = True
except Exception:  # pragma: no cover
    HAVE_ROOT = False


@unittest.skipUnless(HAVE_ROOT, "PyROOT unavailable")
class NullBridgeRootRoundTrip(unittest.TestCase):
    """The ROOT half of the bridge, against a file carrying the PRODUCER's exact object names.

    ⚠ THIS CLASS SKIPS ON THE DEFAULT INTERPRETER, so on a machine without PyROOT the ROOT
    reading, the `TParameter`/`TNamed` accessors and the real round trip are UNVERIFIED. That is
    stated rather than left to be discovered: `validate_transcription` and `transcribe_identity`
    carry every refusal and run everywhere, but the file binding only runs here. Quote the
    interpreter with the result.

    The fixture is built from the PRODUCER's names and classes -- `hCvExecution0/1` as TH1D,
    `hCvSupportMask` as TH1I, the four counts as `TParameter<int>`, the provenance as `TNamed` --
    so it agrees with the world rather than with this module.
    """

    def _write_product(self, directory, x_cv, x_cv2, mask, *, counts=None,
                       predicate=bridge.EXPECTED_PREDICATE, revision="a" * 40):
        import ROOT
        path = Path(directory) / "unified_throw_cov_5d.root"
        f = ROOT.TFile.Open(str(path), "RECREATE")
        n = len(x_cv)
        h1 = ROOT.TH1D(bridge.KEY_CV1, "", n, 0, n)
        h2 = ROOT.TH1D(bridge.KEY_CV2, "", n, 0, n)
        hm = ROOT.TH1I(bridge.KEY_MASK, "", n, 0, n)
        for i in range(n):
            h1.SetBinContent(i + 1, float(x_cv[i]))
            h2.SetBinContent(i + 1, float(x_cv2[i]))
            hm.SetBinContent(i + 1, int(mask[i]))
        for h in (h1, h2, hm):
            h.Write()
        use = counts if counts is not None else _counts(x_cv, mask)
        for key in bridge.COUNT_KEYS:
            ROOT.TParameter(int)(key, int(use[key])).Write()
        ROOT.TNamed(bridge.PREDICATE_KEY, predicate).Write()
        ROOT.TNamed("cv_code_revision", revision).Write()
        ROOT.TNamed("cv_producer_file", "unified_throw_cov.py").Write()
        ROOT.TNamed("cv_producer_sha256", "d" * 64).Write()
        f.Close()
        return path

    def test_a_REAL_root_product_transcribes_and_reloads_through_the_build_reader(self):
        x = np.array([2.0, 0.0, 4.0, 5.0, -1.0])
        x2 = x * (1.0 + 1e-14)
        mask = (x > 0).astype(int)
        with tempfile.TemporaryDirectory() as td:
            product = self._write_product(td, x, x2, mask)
            out = Path(td) / "null.npz"
            result = bridge.bridge_null_operands(
                product, out, expect_sha256=receipt.sha256_file(product)
            )
            self.assertEqual(result["measured_counts"]["n_cv_support"], 3)
            self.assertEqual(result["producer_identity"]["revision"], "a" * 40)
            # It must be loadable by the reader the BUILD uses, not merely by this module.
            x_cv, x_cv2, m = receipt.load_null_operands(out)
            np.testing.assert_allclose(x_cv, x)
            np.testing.assert_array_equal(m, x > 0)
            self.assertTrue(np.isfinite(result["reconstructed_null"]["r_null"]))

    def test_a_WRONG_declared_digest_refuses_before_any_object_is_read(self):
        x = np.array([1.0, 2.0, 3.0])
        with tempfile.TemporaryDirectory() as td:
            product = self._write_product(td, x, x, (x > 0).astype(int))
            with self.assertRaisesRegex(contract.ZContractError, "digest mismatch"):
                bridge.bridge_null_operands(
                    product, Path(td) / "n.npz", expect_sha256="0" * 64
                )

    def test_a_count_recorded_in_the_ROOT_that_disagrees_is_refused(self):
        x = np.array([2.0, 0.0, 4.0])
        mask = (x > 0).astype(int)
        with tempfile.TemporaryDirectory() as td:
            bad = dict(_counts(x, mask), n_cv_support=99)
            product = self._write_product(td, x, x, mask, counts=bad)
            with self.assertRaisesRegex(contract.ZContractError, "disagree with the arrays"):
                bridge.bridge_null_operands(
                    product, Path(td) / "n.npz", expect_sha256=receipt.sha256_file(product)
                )

    def test_an_existing_output_is_not_overwritten(self):
        x = np.array([1.0, 2.0])
        with tempfile.TemporaryDirectory() as td:
            product = self._write_product(td, x, x, (x > 0).astype(int))
            out = Path(td) / "n.npz"
            out.write_bytes(b"prior")
            with self.assertRaisesRegex(contract.ZContractError, "allow_overwrite"):
                bridge.bridge_null_operands(
                    product, out, expect_sha256=receipt.sha256_file(product)
                )


if __name__ == "__main__":
    unittest.main()
