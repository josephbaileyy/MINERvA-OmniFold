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

    def __init__(self, tmp, g_objects=None, ep_overrides=None):
        self.root = Path(tmp) / "data"
        self.root.mkdir()
        self.bands = ["BandA"]
        self.files = {}
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
            self.files[str(path)] = fake_root.FakeFile(objects)

        add("G", "g.root", b"G-bytes", g_objects if g_objects is not None else {
            "combined_source": fake_root.FakeNamed("cs.root"),
            "centering_convention": fake_root.FakeNamed("mean"),
            "sqrt_tr_old": fake_root.FakeParameter(1.5),
            "sqrt_tr_new": fake_root.FakeParameter(1.25),
            "hInflation_g": fake_root.FakeHist([1.0] * 4),
        })
        add("CS", "cs.root", b"CS-bytes",
            {"hCov_universe5d_BandA": None, "hCov_universe5d_total": None})
        add("CV_central", "cv.root", b"CV-bytes", {"hXSecND_flat": flat_hist()})
        for band in self.bands:
            for endpoint in (0, 1):
                key = f"EP_{band}_{endpoint}"
                override = (ep_overrides or {}).get(key)
                add(key, f"{key}.root", f"{key}-bytes".encode(),
                    override if override is not None else endpoint_objects())

        self.bindings = {
            "schema_version": 1, "measured_at_utc": "test",
            "data_root": str(self.root), "bands": self.bands, "grid_nbins": NBINS,
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
            tree = Tree(tmp, g_objects={
                "combined_source": fake_root.FakeNamed("cs.root"),
                "centering_convention": fake_root.FakeNamed("mean"),
                "sqrt_tr_old": fake_root.FakeParameter(1.5),
                "sqrt_tr_new": fake_root.FakeParameter(1.25),
                "hInflation_g": None,
            })
            _, report = tree.run_producer()
            entry = [r for r in report["reads"]
                     if r["read_id"] == "G:hInflation_g_nbins"][0]
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

    def test_attempt_id_cannot_be_reused_over_an_existing_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Tree(tmp)
            tree.run_producer()
            with self.assertRaises(SystemExit):
                tree.run_producer()


if __name__ == "__main__":
    unittest.main(verbosity=2)
