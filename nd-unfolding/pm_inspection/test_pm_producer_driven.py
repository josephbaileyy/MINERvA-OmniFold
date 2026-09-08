#!/usr/bin/env python3
"""Producer-driven tests: run the REAL producer against a controllable fake tree.

Review's objection to the first test suite was exact and correct: hand-written status
records only prove the validator classifies what the test author already believed. These
tests build a real file tree, real bindings with real digests, install a fake PyROOT, run
``pm_root_inspect.main`` end to end, and then classify the report the producer ACTUALLY
emitted. Mutations are applied to the tree or to the emitted report, not to a fixture
someone wrote by hand.
"""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import fake_root  # noqa: E402
import pm_root_inspect as producer  # noqa: E402
import pm_root_validate as validator  # noqa: E402

NBINS = 6
ATTEMPT = "producer-driven-attempt"


def flat_hist(nbins=NBINS):
    # Includes a negative bin, so `> 0` and `!= 0` cannot agree.
    return fake_root.FakeHist([1.0, 0.0, -2.0, 3.0, 0.0, 4.0][:nbins])


def g_objects(**overrides):
    """G's declared contents. `hRowIndex5D` is absent, which is the declared answer."""
    objects = {
        "combined_source": fake_root.FakeNamed("cs.root"),
        "centering_convention": fake_root.FakeNamed("mean"),
        "sqrt_tr_old": fake_root.FakeParameter(1.5),
        "sqrt_tr_new": fake_root.FakeParameter(1.25),
        "hInflation_g": fake_root.FakeHist([1.0] * 4),
    }
    objects.update(overrides)
    return objects


class FileThatRewritesItsOwnBytes(fake_root.FakeFile):
    """A file whose key listing mutates the file on disk.

    G's read-onlyness is MEASURED by a before/after digest precisely because nothing else
    would catch a read that writes. A fixture that cannot make G change cannot tell a
    measured read-onlyness from a hardcoded one, and review measured exactly that:
    hardcoding `unchanged = True` in the producer left all 44 tests green. This is the
    substrate that makes the mutation detectable.
    """

    def __init__(self, objects, path):
        super().__init__(objects)
        self._path = Path(path)

    def GetListOfKeys(self):
        with self._path.open("ab") as handle:
            handle.write(b"!")
        return super().GetListOfKeys()


def endpoint_objects(with_optional=False, missing=(), null=()):
    objects = {
        "hXSecND_flat": flat_hist(),
        "ndim": fake_root.FakeNamed("5"),
        "dataPOT": fake_root.FakeParameter(1.234e20),
        "globalCompleteness": fake_root.FakeParameter(0.97),
    }
    for axis in ("pt", "pz", "eavail", "q3", "W"):
        objects[f"hXSec_{axis}"] = fake_root.FakeHist([1.0, 2.0, 3.0])
    if with_optional:
        objects["estimator_seed"] = fake_root.FakeNamed("4242")
    for name in missing:
        objects.pop(name, None)
    for name in null:
        objects[name] = None
    return objects


class Tree:
    """A temporary data root, matching bindings, and a fake ROOT wired to both."""

    def __init__(self, tmp, g_objects=None, cv_objects=None, ep_overrides=None,
                 g_file_factory=None, data_root_binding=None, grid_nbins=NBINS):
        self.root = Path(tmp) / "data"
        self.root.mkdir()
        self.bands = ["BandA"]
        self.files = {}
        self.paths = {}
        self.objects = {}
        inputs = []

        def add(input_id, relpath, payload, objects):
            path = self.root / relpath
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
            inputs.append({
                "id": input_id, "relpath": relpath,
                "size_bytes": path.stat().st_size,
                "sha256": hashlib.sha256(payload).hexdigest(),
                "digest_provenance": "measured-current-test",
                "digest_source": "synthetic fixture",
                "verify_digest_at_runtime": input_id != "CS",
                "required": True,
            })
            if input_id == "CS":
                inputs[-1]["digest_limitation"] = "NOT re-hashed in the fixture either"
            self.paths[input_id] = path
            self.objects[input_id] = objects
            self.files[str(path)] = fake_root.FakeFile(objects)

        add("G", "g.root", b"G-bytes",
            g_objects if g_objects is not None else globals()["g_objects"]())
        add("CS", "cs.root", b"CS-bytes",
            {"hCov_universe5d_BandA": None, "hCov_universe5d_total": None})
        add("CV_central", "cv.root", b"CV-bytes",
            cv_objects if cv_objects is not None else {"hXSecND_flat": flat_hist()})
        for band in self.bands:
            for endpoint in (0, 1):
                key = f"EP_{band}_{endpoint}"
                override = (ep_overrides or {}).get(key)
                add(key, f"{key}.root", f"{key}-bytes".encode(),
                    override if override is not None else endpoint_objects())

        if g_file_factory is not None:
            self.files[str(self.paths["G"])] = g_file_factory(
                self.objects["G"], self.paths["G"])

        self.bindings = {
            "schema_version": 1, "measured_at_utc": "test",
            "data_root": data_root_binding if data_root_binding is not None
            else str(self.root),
            "bands": self.bands, "grid_nbins": grid_nbins,
            "what_these_digests_are": "synthetic",
            "what_these_digests_are_NOT": "not evidence of anything real",
            "optional_objects": {"G": ["hRowIndex5D"], "endpoint": ["estimator_seed"]},
            "inputs": inputs,
        }
        self.bindings_path = Path(tmp) / "bindings.json"
        self.bindings_path.write_text(json.dumps(self.bindings, indent=2) + "\n")
        self.out = Path(tmp) / "run"

    def run_producer(self):
        sys.modules["ROOT"] = fake_root.FakeROOT(self.files)
        try:
            code = producer.main(["--bindings", str(self.bindings_path),
                                  "--data-root", str(self.root),
                                  "--attempt-id", ATTEMPT, "--out", str(self.out)])
        finally:
            sys.modules.pop("ROOT", None)
        report = json.loads((self.out / "pm-inspection-report.json").read_text())
        return code, report

    def validate(self, report, attempt=ATTEMPT):
        digest = hashlib.sha256(self.bindings_path.read_bytes()).hexdigest()
        return validator.classify(report, self.bindings, attempt, bindings_sha256=digest)


def one(report, read_id):
    """The single record for a read id. Two records for one read is itself a defect."""
    matches = [entry for entry in report["reads"] if entry["read_id"] == read_id]
    assert len(matches) == 1, f"{read_id}: {len(matches)} records, expected 1"
    return matches[0]


class ProducerDrivenHappyPath(unittest.TestCase):
    def test_producer_emits_a_complete_capture_the_validator_accepts(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Tree(tmp)
            code, report = tree.run_producer()
            self.assertEqual(code, producer.EXIT_COMPLETE, report.get("traceback"))
            self.assertEqual(tree.validate(report)[0], validator.EXIT_COMPLETE)

    def test_the_payloads_are_actually_there(self):
        """A capture with no measurements in it must not read as a capture."""
        with tempfile.TemporaryDirectory() as tmp:
            _, report = Tree(tmp).run_producer()
            self.assertEqual(report["G"]["key_count"], 5)
            self.assertEqual(report["G"]["sqrt_tr_old"], 1.5)   # GetVal, not GetTitle
            self.assertEqual(report["CV_central"]["hXSecND_flat"]["count"], 3)
            self.assertTrue(report["G_read_onlyness"]["unchanged"])
            self.assertIn("modules_loaded_from_forbidden_root",
                          report["module_provenance"])

    def test_optional_absence_is_captured_as_a_measurement(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Tree(tmp)
            _, report = tree.run_producer()
            absent = [r for r in report["reads"] if r["read_id"] == "G:hRowIndex5D"]
            self.assertEqual(absent[0]["status"], "absent")
            self.assertEqual(tree.validate(report)[0], validator.EXIT_COMPLETE)


class ProducerDrivenMutations(unittest.TestCase):
    def test_missing_required_object_is_ERROR(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Tree(tmp, ep_overrides={
                "EP_BandA_0": endpoint_objects(missing=("hXSecND_flat",))})
            code, report = tree.run_producer()
            self.assertEqual(code, producer.EXIT_COMPLETE)  # producer still finishes
            exit_code, findings = tree.validate(report)
            self.assertEqual(exit_code, validator.EXIT_ERROR)
            self.assertIn("EP_BandA_0:hXSecND_flat", findings["required_read_failures"])

    def test_null_required_object_is_ERROR_not_a_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Tree(tmp, ep_overrides={
                "EP_BandA_1": endpoint_objects(null=("dataPOT",))})
            _, report = tree.run_producer()
            entry = [r for r in report["reads"]
                     if r["read_id"] == "EP_BandA_1:dataPOT"][0]
            self.assertEqual(entry["status"], "unreadable")
            self.assertEqual(tree.validate(report)[0], validator.EXIT_ERROR)

    def test_listed_but_null_hInflation_g_is_ERROR(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Tree(tmp, g_objects=g_objects(hInflation_g=None))
            _, report = tree.run_producer()
            entry = one(report, "G:hInflation_g_nbins")
            self.assertEqual(entry["status"], "unreadable")
            self.assertEqual(tree.validate(report)[0], validator.EXIT_ERROR)

    def test_kind_downgrade_in_the_report_cannot_buy_COMPLETE(self):
        """Relabel a required input as optional-absent: the bindings still govern."""
        with tempfile.TemporaryDirectory() as tmp:
            tree = Tree(tmp)
            _, report = tree.run_producer()
            for entry in report["reads"]:
                if entry["read_id"] == "input:G":
                    entry["kind"] = validator.OPTIONAL
                    entry["status"] = "absent"
            exit_code, findings = tree.validate(report)
            self.assertEqual(exit_code, validator.EXIT_ERROR)
            self.assertIn("input:G", findings["required_read_failures"])
            self.assertIn("input:G",
                          findings["records_whose_kind_contradicts_bindings"])

    def test_wrong_bindings_digest_is_ERROR(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Tree(tmp)
            _, report = tree.run_producer()
            exit_code, findings = validator.classify(
                report, tree.bindings, ATTEMPT, bindings_sha256="wrong")
            self.assertEqual(exit_code, validator.EXIT_ERROR)
            self.assertIn("different bindings bytes", findings["reason"])

    def test_digest_mismatch_on_an_input_is_ERROR(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Tree(tmp)
            (tree.root / "cv.root").write_bytes(b"CV-bytes-tampered")
            for entry in tree.bindings["inputs"]:
                if entry["id"] == "CV_central":
                    entry["size_bytes"] = (tree.root / "cv.root").stat().st_size
            tree.bindings_path.write_text(json.dumps(tree.bindings, indent=2) + "\n")
            code, report = tree.run_producer()
            self.assertEqual(code, producer.EXIT_ERROR)
            self.assertIn("CV_central", report["fatal"])
            # And the TERMINAL object has to agree: asserting on the producer's own exit
            # code stops one layer nearer to hand than the classifier that selects the
            # contract's branch.
            exit_code, findings = tree.validate(report)
            self.assertEqual(exit_code, validator.EXIT_ERROR)
            self.assertIn("CV_central", findings["producer_fatal"])
            self.assertIn("input:CV_central", findings["required_read_failures"])

    def test_attempt_id_cannot_be_reused_over_an_existing_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Tree(tmp)
            tree.run_producer()
            with self.assertRaises(SystemExit):
                tree.run_producer()


class PayloadsMustActuallyBeThere(unittest.TestCase):
    """Review's reproduction: strip the measurements, keep the shape, expect COMPLETE."""

    def test_stripped_records_and_sections_are_not_a_capture(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Tree(tmp)
            _, report = tree.run_producer()
            self.assertEqual(tree.validate(report)[0], validator.EXIT_COMPLETE)

            # Exactly the mutation review reproduced.
            for section in ("G", "CS", "CV_central", "endpoints", "G_read_onlyness"):
                report.pop(section, None)
            report["reads"] = [
                {"read_id": e["read_id"], "status": e["status"], "kind": e["kind"]}
                for e in report["reads"]]

            exit_code, findings = tree.validate(report)
            self.assertEqual(exit_code, validator.EXIT_ERROR)
            self.assertEqual(
                findings["missing_report_sections"],
                ["G", "CS", "CV_central", "endpoints", "G_read_onlyness"])
            self.assertTrue(findings["reads_missing_payload"])

    def test_one_nulled_payload_field_is_enough(self):
        """Not a threshold: the number must be present, never a particular value."""
        with tempfile.TemporaryDirectory() as tmp:
            tree = Tree(tmp)
            _, report = tree.run_producer()
            for entry in report["reads"]:
                if entry["read_id"] == "G:sqrt_tr_old":
                    entry["value"] = None
            exit_code, findings = tree.validate(report)
            self.assertEqual(exit_code, validator.EXIT_ERROR)
            self.assertIn("G:sqrt_tr_old:value", findings["reads_missing_payload"])

    def test_intact_capture_control_still_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Tree(tmp)
            _, report = tree.run_producer()
            exit_code, findings = tree.validate(report)
            self.assertEqual(exit_code, validator.EXIT_COMPLETE)
            self.assertEqual(findings["reads_missing_payload"], [])
            self.assertEqual(findings["missing_report_sections"], [])

    def test_expected_absence_control_needs_no_payload(self):
        """An absent optional has nothing to carry; it must not be a payload defect."""
        with tempfile.TemporaryDirectory() as tmp:
            tree = Tree(tmp)
            _, report = tree.run_producer()
            absent = [r for r in report["reads"] if r["read_id"] == "G:hRowIndex5D"][0]
            self.assertEqual(absent["status"], "absent")
            self.assertEqual(tree.validate(report)[0], validator.EXIT_COMPLETE)

    def test_malformed_records_are_ERROR_not_an_exception(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Tree(tmp)
            _, report = tree.run_producer()
            report["reads"] = ["not a record", {"no": "read_id"}]
            exit_code, findings = tree.validate(report)
            self.assertEqual(exit_code, validator.EXIT_ERROR)
            self.assertIn("malformed", findings["reason"])

    def test_non_object_report_is_ERROR_not_an_exception(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Tree(tmp)
            tree.run_producer()
            exit_code, findings = tree.validate(["not", "an", "object"])
            self.assertEqual(exit_code, validator.EXIT_ERROR)
            self.assertIn("not a JSON object", findings["reason"])


class OneBadObjectCostsOneRecord(unittest.TestCase):
    """A listed-but-null object used to abort the capture from inside the first endpoint.

    Review measured it: `AttributeError: 'NoneType' object has no attribute 'GetNbinsX'`,
    17 records emitted, 21 of the 38 declared reads never attempted, and the second
    endpoint never opened. The verdict class was right and the cost was not: with
    retry_policy.requires_new_authorization, a re-run is not free, so a fault has to be
    recorded and the remaining declared reads still performed.
    """

    def _assert_one_unreadable_and_the_rest_read(self, tree, read_id):
        code, report = tree.run_producer()
        self.assertIsNone(report.get("traceback"))
        self.assertEqual(code, producer.EXIT_COMPLETE)   # ran to the end
        self.assertEqual(one(report, read_id)["status"], "unreadable")
        exit_code, findings = tree.validate(report)
        self.assertEqual(exit_code, validator.EXIT_ERROR)
        self.assertEqual(findings["required_read_failures"], [read_id])
        self.assertEqual(findings["missing_read_records"], [])
        return report

    def test_a_null_flat_histogram_costs_one_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Tree(tmp, ep_overrides={
                "EP_BandA_0": endpoint_objects(null=("hXSecND_flat",))})
            report = self._assert_one_unreadable_and_the_rest_read(
                tree, "EP_BandA_0:hXSecND_flat")
            # The endpoint that used to be lost entirely.
            self.assertEqual(one(report, "EP_BandA_1:hXSecND_flat")["status"], "read")
            self.assertEqual(one(report, "EP_BandA_0:hXSec_W")["status"], "read")

    def test_a_null_axis_histogram_costs_one_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Tree(tmp, ep_overrides={
                "EP_BandA_0": endpoint_objects(null=("hXSec_pt",))})
            report = self._assert_one_unreadable_and_the_rest_read(
                tree, "EP_BandA_0:hXSec_pt")
            self.assertEqual(one(report, "EP_BandA_0:hXSec_pz")["status"], "read")

    def test_an_object_that_loads_as_the_wrong_thing_costs_one_record(self):
        """Not null, but not something these reads can be performed on either."""
        with tempfile.TemporaryDirectory() as tmp:
            objects = endpoint_objects()
            objects["hXSecND_flat"] = fake_root.FakeNamed("I am not a histogram")
            tree = Tree(tmp, ep_overrides={"EP_BandA_0": objects})
            report = self._assert_one_unreadable_and_the_rest_read(
                tree, "EP_BandA_0:hXSecND_flat")
            self.assertIn("exposes no", one(report, "EP_BandA_0:hXSecND_flat")["detail"])

    def test_a_null_central_flat_histogram_costs_one_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Tree(tmp, cv_objects={"hXSecND_flat": None})
            report = self._assert_one_unreadable_and_the_rest_read(
                tree, "CV_central:hXSecND_flat")
            self.assertEqual(one(report, "EP_BandA_0:hXSecND_flat")["status"], "read")


class ReadOnlynessOfGIsMeasuredNotAsserted(unittest.TestCase):
    """PREDECLARATION section 4 measures G's read-onlyness with a before/after digest, and
    the authorization forbids modifying source artifacts. Nothing tested the measurement:
    hardcoding `unchanged = True` in the producer left all 44 tests green."""

    def test_a_read_that_rewrites_G_is_caught_by_the_before_after_digest(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Tree(tmp, g_file_factory=FileThatRewritesItsOwnBytes)
            _, report = tree.run_producer()
            entry = one(report, "G:read_onlyness")
            self.assertNotEqual(entry["sha256_before"], entry["sha256_after"])
            self.assertFalse(entry["unchanged"])
            self.assertFalse(report["G_read_onlyness"]["unchanged"])
            self.assertEqual(entry["status"], "unreadable")
            exit_code, findings = tree.validate(report)
            self.assertEqual(exit_code, validator.EXIT_ERROR)
            self.assertTrue(findings["source_artifact_changed_during_the_inspection"])

    def test_a_read_that_does_not_write_is_measured_as_unchanged(self):
        """The control. A guard that fires on every correct run is not a guard."""
        with tempfile.TemporaryDirectory() as tmp:
            tree = Tree(tmp)
            _, report = tree.run_producer()
            entry = one(report, "G:read_onlyness")
            self.assertEqual(entry["sha256_before"], entry["sha256_after"])
            self.assertTrue(entry["unchanged"])
            self.assertEqual(entry["status"], "read")
            exit_code, findings = tree.validate(report)
            self.assertEqual(exit_code, validator.EXIT_COMPLETE)
            self.assertFalse(findings["source_artifact_changed_during_the_inspection"])


class TheMeasuredNumbersAreMeasured(unittest.TestCase):
    """Each of these is a number the producer could have restated instead of measuring.
    The validator faults none of their VALUES -- that would be an acceptance threshold --
    so only a producer-driven test can hold the producer to measuring them."""

    def test_a_declared_grid_size_is_not_reported_as_a_measured_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Tree(tmp, cv_objects={"hXSecND_flat": flat_hist(nbins=4)})
            _, report = tree.run_producer()
            entry = one(report, "CV_central:hXSecND_flat")
            self.assertEqual(entry["measured_nbins"], 4)      # what it IS
            self.assertEqual(entry["declared_nbins"], NBINS)  # what the bindings SAY
            self.assertFalse(entry["nbins_conforms"])
            # A measured grid non-conformance is a MEASUREMENT. PM-3's grid arm exists to
            # detect it; classifying it as a capture fault would be inventing a criterion.
            self.assertEqual(tree.validate(report)[0], validator.EXIT_COMPLETE)

    def test_a_non_finite_bin_is_measured_and_is_not_a_capture_fault(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Tree(tmp, cv_objects={
                "hXSecND_flat": fake_root.FakeHist([1.0, float("inf"), 2.0])})
            _, report = tree.run_producer()
            entry = one(report, "CV_central:hXSecND_flat")
            self.assertFalse(entry["all_finite"])
            self.assertEqual(tree.validate(report)[0], validator.EXIT_COMPLETE)

    def test_the_last_axis_edge_is_the_upper_edge_of_the_last_bin(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Tree(tmp)
            _, report = tree.run_producer()
            entry = one(report, "EP_BandA_0:hXSec_pt")
            self.assertEqual(entry["nbins"], 3)
            self.assertEqual(entry["first_edge"], 0.0)
            # Low edges 0,1,2 and a final bin of width 1. The last edge is the UPPER edge
            # of the last bin, so an axis of n bins has n+1 edges; dropping the final one
            # silently reports the last LOW edge as the range's end.
            self.assertEqual(entry["last_edge"], 3.0)
            self.assertEqual(report["endpoints"]["EP_BandA_0"]["hXSec_pt"]["edges"],
                             [0.0, 1.0, 2.0, 3.0])

    def test_a_present_row_index_is_captured_by_its_contents(self):
        """The present branch of the one read PM-4's premise turns on. A count is not a
        measurement of a row index: two different indices share a length."""
        with tempfile.TemporaryDirectory() as tmp:
            tree = Tree(tmp, g_objects=g_objects(
                hRowIndex5D=fake_root.FakeHist([0.0, 3.0, 5.0])))
            _, report = tree.run_producer()
            entry = one(report, "G:hRowIndex5D")
            self.assertEqual(entry["status"], "read")
            self.assertTrue(entry["contents_readable"])
            self.assertEqual(entry["count"], 3)
            import numpy as np
            raw = np.array([0, 3, 5], dtype=np.int64).tobytes()
            self.assertEqual(entry["row_index_sha256"],
                             hashlib.sha256(raw).hexdigest())
            self.assertEqual(entry["reported_mask_hash"],
                             hashlib.sha256(raw + b"|C").hexdigest())
            self.assertEqual(tree.validate(report)[0], validator.EXIT_COMPLETE)


class TheProducerIsNotAccusedOfWhatItDidNotDo(unittest.TestCase):
    """`status` carries the fault; `kind` carries the obligation. Stamping an unreadable
    OPTIONAL object `required` made the validator additionally report it as the producer
    reclassifying its own obligation, against a producer that did nothing wrong."""

    def test_an_unreadable_optional_keeps_the_kind_the_bindings_give_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Tree(tmp, ep_overrides={"EP_BandA_0": endpoint_objects(
                with_optional=True, null=("estimator_seed",))})
            _, report = tree.run_producer()
            entry = one(report, "EP_BandA_0:estimator_seed")
            self.assertEqual(entry["status"], "unreadable")
            self.assertEqual(entry["kind"], validator.OPTIONAL)
            exit_code, findings = tree.validate(report)
            self.assertEqual(exit_code, validator.EXIT_ERROR)
            self.assertEqual(findings["unreadable_optional_objects"],
                             ["EP_BandA_0:estimator_seed"])
            self.assertEqual(findings["records_whose_kind_contradicts_bindings"], [])

    def test_a_row_index_that_loads_but_cannot_be_digested_is_a_fault(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Tree(tmp, g_objects=g_objects(
                hRowIndex5D=fake_root.FakeNamed("I am not a histogram")))
            _, report = tree.run_producer()
            entry = one(report, "G:hRowIndex5D")
            self.assertEqual(entry["status"], "unreadable")
            self.assertEqual(entry["kind"], validator.OPTIONAL)
            self.assertFalse(entry["contents_readable"])
            exit_code, findings = tree.validate(report)
            self.assertEqual(exit_code, validator.EXIT_ERROR)
            self.assertEqual(findings["unreadable_optional_objects"], ["G:hRowIndex5D"])
            # Not the declared absence: we did not learn whether the row index is there.
            self.assertNotIn("G:hRowIndex5D", findings["expected_optional_absences"])
            self.assertEqual(findings["records_whose_kind_contradicts_bindings"], [])

    def test_an_unreadable_optional_G_object_keeps_its_kind_too(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Tree(tmp, g_objects=g_objects(hRowIndex5D=None))
            _, report = tree.run_producer()
            entry = one(report, "G:hRowIndex5D")
            self.assertEqual(entry["status"], "unreadable")
            self.assertEqual(entry["kind"], validator.OPTIONAL)
            exit_code, findings = tree.validate(report)
            self.assertEqual(exit_code, validator.EXIT_ERROR)
            self.assertEqual(findings["records_whose_kind_contradicts_bindings"], [])

    def test_an_empty_title_is_not_a_stored_value(self):
        """The round-4 class at the producer: `status=read, value=""` is the same hollow
        record with the null replaced by an empty value."""
        with tempfile.TemporaryDirectory() as tmp:
            tree = Tree(tmp, g_objects=g_objects(
                combined_source=fake_root.FakeNamed("")))
            _, report = tree.run_producer()
            entry = one(report, "G:combined_source")
            self.assertEqual(entry["status"], "unreadable")
            exit_code, findings = tree.validate(report)
            self.assertEqual(exit_code, validator.EXIT_ERROR)
            self.assertIn("G:combined_source", findings["required_read_failures"])

    def test_a_typed_zero_is_still_a_value(self):
        """The control for the rule above: 0.0 from GetVal is a measurement."""
        with tempfile.TemporaryDirectory() as tmp:
            tree = Tree(tmp, g_objects=g_objects(
                sqrt_tr_old=fake_root.FakeParameter(0.0)))
            _, report = tree.run_producer()
            entry = one(report, "G:sqrt_tr_old")
            self.assertEqual(entry["status"], "read")
            self.assertEqual(entry["value"], 0.0)
            self.assertEqual(tree.validate(report)[0], validator.EXIT_COMPLETE)


class TheCaptureIsBoundToTheDeclaredTree(unittest.TestCase):
    """bindings["data_root"] was committed and read by nobody: the producer took the root
    from argv and aimed the contamination measurement at that same argv value."""

    def test_the_contamination_measurement_is_aimed_at_the_declared_root(self):
        declared = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
        with tempfile.TemporaryDirectory() as tmp:
            tree = Tree(tmp, data_root_binding=declared)
            _, report = tree.run_producer()
            self.assertEqual(report["module_provenance"]["forbidden_root"], declared)
            exit_code, findings = tree.validate(report)
            self.assertEqual(exit_code, validator.EXIT_ERROR)
            self.assertTrue(findings["data_root_disagrees_with_bindings"])
            # Aimed correctly even though argv pointed elsewhere, which is the half of
            # the defect that silently disarmed the measurement.
            self.assertFalse(
                findings["contamination_measurement_aimed_at_the_wrong_tree"])

    def test_a_module_loaded_from_the_bound_tree_is_measured_as_an_offender(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Tree(tmp)
            stand_in = types.ModuleType("p4_lib_stand_in")
            stand_in.__file__ = str(tree.root / "nd-unfolding" / "p4_lib.py")
            sys.modules["p4_lib_stand_in"] = stand_in
            try:
                _, report = tree.run_producer()
            finally:
                sys.modules.pop("p4_lib_stand_in", None)
            self.assertEqual(
                report["module_provenance"]["modules_loaded_from_forbidden_root"],
                ["p4_lib_stand_in"])
            exit_code, findings = tree.validate(report)
            self.assertEqual(exit_code, validator.EXIT_ERROR)
            self.assertEqual(findings["modules_loaded_from_the_forbidden_root"],
                             ["p4_lib_stand_in"])

    def test_the_control_measures_no_offenders(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Tree(tmp)
            _, report = tree.run_producer()
            self.assertEqual(
                report["module_provenance"]["modules_loaded_from_forbidden_root"], [])
            self.assertEqual(tree.validate(report)[0], validator.EXIT_COMPLETE)


class TheReportMustPreserveWhatEachReadProduced(unittest.TestCase):
    """Round 5, class 1: shape satisfied, substance absent, one layer above the payload.

    Round 3 required a payload; round 4 required it non-empty and the sections to be
    non-empty mappings. ``{"lost": true}`` is a non-empty mapping, so every one of these
    returned COMPLETE. PREDECLARATION section 4 requires TKey names, classes and cycles
    for a listing and the edges INCLUDING the final upper edge for an axis; section 7
    requires the listings preserved. Each mutation below is applied alone to a report the
    REAL producer wrote.
    """

    def _mutated(self, mutate):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Tree(tmp)
            _, report = tree.run_producer()
            self.assertEqual(tree.validate(report)[0], validator.EXIT_COMPLETE,
                             "the control must be COMPLETE before it is mutated")
            mutate(report)
            return tree.validate(report)

    def test_a_deleted_key_listing_is_not_a_capture(self):
        def mutate(report):
            del report["CS"]["key_listing"]
        exit_code, findings = self._mutated(mutate)
        self.assertEqual(exit_code, validator.EXIT_ERROR)
        self.assertIn("CS:key_listing", findings["reads_missing_nested_capture"])

    def test_deleted_axis_edges_are_not_a_capture(self):
        def mutate(report):
            del report["endpoints"]["EP_BandA_0"]["hXSec_pt"]["edges"]
        exit_code, findings = self._mutated(mutate)
        self.assertEqual(exit_code, validator.EXIT_ERROR)
        self.assertIn("EP_BandA_0:hXSec_pt", findings["reads_missing_nested_capture"])

    def test_an_incomplete_edge_list_is_not_a_capture(self):
        """n bins have n+1 edges. Dropping the final upper edge leaves a well-formed list
        of numbers that silently reports the last LOW edge as the range's end."""
        def mutate(report):
            report["endpoints"]["EP_BandA_0"]["hXSec_pt"]["edges"].pop()
        exit_code, findings = self._mutated(mutate)
        self.assertEqual(exit_code, validator.EXIT_ERROR)
        self.assertIn("INCLUDING the final upper edge",
                      findings["reads_missing_nested_capture_why"][
                          "EP_BandA_0:hXSec_pt"])

    def test_a_listing_stripped_of_its_names_is_not_a_capture(self):
        """The declared read is names, classes AND cycles: each is separately required,
        and a revert of any one of the three has to fail a test here."""
        def mutate(report):
            for entry in report["endpoints"]["EP_BandA_1"]["key_listing"]:
                entry.pop("name")
        exit_code, findings = self._mutated(mutate)
        self.assertEqual(exit_code, validator.EXIT_ERROR)
        self.assertIn("EP_BandA_1:key_listing", findings["reads_missing_nested_capture"])

    def test_a_listing_stripped_of_its_classes_is_not_a_capture(self):
        def mutate(report):
            for entry in report["G"]["key_listing"]:
                entry.pop("class")
        exit_code, findings = self._mutated(mutate)
        self.assertEqual(exit_code, validator.EXIT_ERROR)
        self.assertIn("G:key_listing", findings["reads_missing_nested_capture"])

    def test_a_listing_stripped_of_its_cycles_is_not_a_capture(self):
        def mutate(report):
            for entry in report["CV_central"]["key_listing"]:
                entry.pop("cycle")
        exit_code, findings = self._mutated(mutate)
        self.assertEqual(exit_code, validator.EXIT_ERROR)
        self.assertIn("CV_central:key_listing", findings["reads_missing_nested_capture"])

    def test_a_nonempty_mapping_with_nothing_in_it_is_not_a_capture(self):
        """The exact reproducer: four sections replaced by `{"lost": true}`."""
        for section in ("G", "CS", "CV_central", "endpoints"):
            with self.subTest(section=section):
                def mutate(report, section=section):
                    report[section] = {"lost": True}
                exit_code, findings = self._mutated(mutate)
                self.assertEqual(exit_code, validator.EXIT_ERROR)
                self.assertEqual(findings["missing_report_sections"], [],
                                 "a non-empty mapping passes the outer shell rule")
                self.assertTrue(findings["reads_missing_nested_capture"])

    def test_a_section_that_disagrees_with_its_record_is_not_a_capture(self):
        """Record and section state the same measurement twice; they must agree."""
        def mutate(report):
            report["CV_central"]["hXSecND_flat"]["content_sha256"] = "f" * 64
        exit_code, findings = self._mutated(mutate)
        self.assertEqual(exit_code, validator.EXIT_ERROR)
        self.assertIn("CV_central:hXSecND_flat",
                      findings["reads_missing_nested_capture"])

    def test_the_intact_capture_control_still_preserves_everything(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Tree(tmp)
            _, report = tree.run_producer()
            exit_code, findings = tree.validate(report)
            self.assertEqual(exit_code, validator.EXIT_COMPLETE, findings)
            self.assertEqual(findings["reads_missing_nested_capture"], [])


class EachInputMustMatchItsOwnBinding(unittest.TestCase):
    """Round 5, class 2: `input:G`'s identity was never checked against the bindings.

    A wrong path, a negative size, a digest of all zeros and `digest_verified: false`
    each returned COMPLETE, because the fields were only checked for being non-empty and
    of the right type. CS's no-rehash branch is preserved: the bindings exclude it from
    runtime verification at 41.4 GB and that is a complete capture, not a fault.
    """

    def _mutated(self, mutate, read_id="input:G"):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Tree(tmp)
            _, report = tree.run_producer()
            self.assertEqual(tree.validate(report)[0], validator.EXIT_COMPLETE)
            mutate(one(report, read_id))
            return tree.validate(report)

    def _assert_identity_fault(self, mutate, needle, read_id="input:G"):
        exit_code, findings = self._mutated(mutate, read_id)
        self.assertEqual(exit_code, validator.EXIT_ERROR)
        self.assertTrue(
            any(needle in problem
                for problem in findings["inputs_that_disagree_with_their_binding"]),
            findings["inputs_that_disagree_with_their_binding"])

    def test_a_path_that_is_not_the_bound_one_is_a_fault(self):
        def mutate(entry):
            entry["path"] = "/somewhere/else/g.root"
        self._assert_identity_fault(mutate, "is not the bound")

    def test_a_size_that_is_not_the_bound_one_is_a_fault(self):
        def mutate(entry):
            entry["size_bytes"] = -7
        self._assert_identity_fault(mutate, "size_bytes")

    def test_a_digest_that_is_not_the_bound_one_is_a_fault(self):
        def mutate(entry):
            entry["sha256"] = "0" * 64
        self._assert_identity_fault(mutate, "sha256")

    def test_an_unverified_digest_where_the_binding_requires_one_is_a_fault(self):
        def mutate(entry):
            entry["digest_verified"] = False
        self._assert_identity_fault(mutate, "requires runtime digest verification")

    def test_a_removed_digest_is_a_fault(self):
        def mutate(entry):
            entry.pop("sha256")
        exit_code, findings = self._mutated(mutate)
        self.assertEqual(exit_code, validator.EXIT_ERROR)
        self.assertIn("input:G:sha256", findings["reads_missing_payload"])

    def test_a_removed_digest_verified_flag_is_a_fault(self):
        def mutate(entry):
            entry.pop("digest_verified")
        exit_code, findings = self._mutated(mutate)
        self.assertEqual(exit_code, validator.EXIT_ERROR)
        self.assertIn("input:G:digest_verified", findings["reads_missing_payload"])

    def test_a_wrong_digest_provenance_is_a_fault(self):
        def mutate(entry):
            entry["digest_provenance"] = "read_from_G"
        self._assert_identity_fault(mutate, "digest_provenance")

    def test_claiming_a_verification_the_bindings_exclude_is_a_fault(self):
        """CS is not re-hashed. A record saying it was is claiming work that never ran."""
        def mutate(entry):
            entry["digest_verified"] = True
        self._assert_identity_fault(mutate, "claims a verification that did not happen",
                                    read_id="input:CS")

    def test_the_CS_no_rehash_branch_is_a_COMPLETE_capture(self):
        """The positive control that must not be crossed: 41.4 GB is deliberately not
        re-hashed, so the historical digest carried unverified IS the capture."""
        with tempfile.TemporaryDirectory() as tmp:
            tree = Tree(tmp)
            _, report = tree.run_producer()
            entry = one(report, "input:CS")
            self.assertFalse(entry["digest_verified"])
            self.assertNotIn("sha256", entry)
            bound = next(e for e in tree.bindings["inputs"] if e["id"] == "CS")
            self.assertEqual(entry["sha256_bound_not_verified"], bound["sha256"])
            exit_code, findings = tree.validate(report)
            self.assertEqual(exit_code, validator.EXIT_COMPLETE, findings)
            self.assertEqual(findings["inputs_that_disagree_with_their_binding"], [])

    def test_every_input_the_producer_wrote_matches_its_binding(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Tree(tmp)
            _, report = tree.run_producer()
            self.assertEqual(
                tree.validate(report)[1]["inputs_that_disagree_with_their_binding"], [])


class ContaminationIsRecomputedNotBelieved(unittest.TestCase):
    """Round 5, class 3: the producer's summary of its own contamination was taken on
    trust. A module loaded from the bound tree, with an EMPTY offender list, was
    COMPLETE. The map is the measurement; the list is an account of it."""

    def test_a_hidden_offender_is_recomputed_from_the_module_map(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Tree(tmp)
            _, report = tree.run_producer()
            self.assertEqual(tree.validate(report)[0], validator.EXIT_COMPLETE)
            report["module_provenance"]["modules"]["bad"] = str(tree.root / "bad.py")
            report["module_provenance"]["module_count"] = len(
                report["module_provenance"]["modules"])
            self.assertEqual(
                report["module_provenance"]["modules_loaded_from_forbidden_root"], [])
            exit_code, findings = tree.validate(report)
            self.assertEqual(exit_code, validator.EXIT_ERROR)
            self.assertIn("bad", findings["modules_loaded_from_the_forbidden_root"])
            self.assertTrue(any(
                "recomputed from the module map" in problem
                for problem in findings["records_contradicting_their_own_measurement"]))

    def test_a_deleted_module_map_leaves_the_summary_unauditable(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Tree(tmp)
            _, report = tree.run_producer()
            del report["module_provenance"]["modules"]
            exit_code, findings = tree.validate(report)
            self.assertEqual(exit_code, validator.EXIT_ERROR)
            self.assertTrue(any(
                "no per-module file map" in problem
                for problem in findings["records_contradicting_their_own_measurement"]))

    def test_a_module_count_that_disagrees_with_the_map_is_a_fault(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Tree(tmp)
            _, report = tree.run_producer()
            report["module_provenance"]["module_count"] = 99999
            self.assertEqual(tree.validate(report)[0], validator.EXIT_ERROR)

    def test_the_honest_control_recomputes_to_no_offenders(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Tree(tmp)
            _, report = tree.run_producer()
            self.assertTrue(report["module_provenance"]["modules"])
            exit_code, findings = tree.validate(report)
            self.assertEqual(exit_code, validator.EXIT_COMPLETE, findings)
            self.assertEqual(findings["modules_loaded_from_the_forbidden_root"], [])

    def test_a_real_offender_is_still_measured_by_the_producer_too(self):
        """The recomputation must not replace the producer's own measurement: both the
        map and the summary have to name a genuine import from the bound tree."""
        with tempfile.TemporaryDirectory() as tmp:
            tree = Tree(tmp)
            stand_in = types.ModuleType("p4_lib_stand_in_round5")
            stand_in.__file__ = str(tree.root / "nd-unfolding" / "p4_lib.py")
            sys.modules["p4_lib_stand_in_round5"] = stand_in
            try:
                _, report = tree.run_producer()
            finally:
                sys.modules.pop("p4_lib_stand_in_round5", None)
            exit_code, findings = tree.validate(report)
            self.assertEqual(exit_code, validator.EXIT_ERROR)
            self.assertEqual(findings["modules_loaded_from_the_forbidden_root"],
                             ["p4_lib_stand_in_round5"])
            self.assertNotIn(
                "recomputed from the module map",
                " ".join(findings["records_contradicting_their_own_measurement"]))


class OneDeclaredReadIsOneRecord(unittest.TestCase):
    """Round 5, class 4: a second record for the same read id was COMPLETE. Two answers
    to one declared question is not a capture of it, and nothing downstream says which
    of the two the verdict was reached on."""

    def test_a_duplicate_read_record_is_a_fault(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Tree(tmp)
            _, report = tree.run_producer()
            self.assertEqual(tree.validate(report)[0], validator.EXIT_COMPLETE)
            duplicate = dict(one(report, "G:sqrt_tr_old"))
            duplicate["value"] = 999
            report["reads"].append(duplicate)
            exit_code, findings = tree.validate(report)
            self.assertEqual(exit_code, validator.EXIT_ERROR)
            self.assertEqual(findings["duplicate_read_records"], ["G:sqrt_tr_old"])

    def test_a_duplicated_input_record_is_a_fault(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Tree(tmp)
            _, report = tree.run_producer()
            report["reads"].append(dict(one(report, "input:CS")))
            exit_code, findings = tree.validate(report)
            self.assertEqual(exit_code, validator.EXIT_ERROR)
            self.assertEqual(findings["duplicate_read_records"], ["input:CS"])

    def test_the_control_records_each_declared_read_exactly_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Tree(tmp)
            _, report = tree.run_producer()
            ids = [entry["read_id"] for entry in report["reads"]]
            self.assertEqual(len(ids), len(set(ids)))
            exit_code, findings = tree.validate(report)
            self.assertEqual(exit_code, validator.EXIT_COMPLETE, findings)
            self.assertEqual(findings["duplicate_read_records"], [])


class MeasuredNonconformanceIsStillACompleteCapture(unittest.TestCase):
    """The line the validator must not cross, pinned against the REAL producer. Each of
    these is a scientific non-conformance the inspection exists to MEASURE; classifying
    any of them as a capture fault would be inventing an acceptance threshold."""

    def _flat(self, cv_objects):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Tree(tmp, cv_objects=cv_objects)
            _, report = tree.run_producer()
            exit_code, findings = tree.validate(report)
            self.assertEqual(exit_code, validator.EXIT_COMPLETE, findings)
            return one(report, "CV_central:hXSecND_flat")

    def test_nbins_conforms_false_is_COMPLETE(self):
        entry = self._flat({"hXSecND_flat": flat_hist(nbins=4)})
        self.assertFalse(entry["nbins_conforms"])

    def test_all_finite_false_is_COMPLETE(self):
        entry = self._flat({"hXSecND_flat": fake_root.FakeHist([1.0, float("inf"), 2.0])})
        self.assertFalse(entry["all_finite"])

    def test_row_index_matches_S_false_is_COMPLETE(self):
        entry = self._flat({"hXSecND_flat": flat_hist()})
        self.assertFalse(entry["row_index_matches_S"])
        self.assertFalse(entry["reported_mask_matches_S"])

    def test_count_matches_S_false_is_COMPLETE(self):
        entry = self._flat({"hXSecND_flat": flat_hist()})
        self.assertFalse(entry["count_matches_S"])
        self.assertNotEqual(entry["count"], producer.S_EXPECTED_COUNT)

    def test_any_scalar_value_is_COMPLETE(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Tree(tmp, g_objects=g_objects(
                sqrt_tr_old=fake_root.FakeParameter(-1234.5),
                centering_convention=fake_root.FakeNamed("something nobody expected")))
            _, report = tree.run_producer()
            self.assertEqual(one(report, "G:sqrt_tr_old")["value"], -1234.5)
            self.assertEqual(tree.validate(report)[0], validator.EXIT_COMPLETE)

    def test_the_expected_optional_absences_are_COMPLETE(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Tree(tmp)
            _, report = tree.run_producer()
            exit_code, findings = tree.validate(report)
            self.assertEqual(exit_code, validator.EXIT_COMPLETE, findings)
            self.assertIn("G:hRowIndex5D", findings["expected_optional_absences"])
            self.assertIn("EP_BandA_0:estimator_seed",
                          findings["expected_optional_absences"])
            self.assertIs(report["G"]["hRowIndex5D_present"], False)


if __name__ == "__main__":
    unittest.main(verbosity=2)
