"""Bounded audit acceptance/failure tests using only synthetic and fake readers."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import sys
from unittest import mock
from typing import Any, Callable

import numpy as np
import pytest

PET_ROOT = Path(__file__).resolve().parents[1] / "pet"
sys.path.insert(0, str(PET_ROOT))
import launch_typed_descriptor_source_audit as launcher  # noqa: E402
import typed_descriptor_source_audit as audit  # noqa: E402
import typed_descriptor_source_smoke as source  # noqa: E402
import typed_descriptors as typed  # noqa: E402
from test_typed_descriptor_source_smoke import _raw_entry  # noqa: E402

REPO_ROOT = PET_ROOT.parents[1]


class RuntimeNumpy:
    """Reject testing utilities in the audit without modifying NumPy itself."""

    def __getattr__(self, name: str) -> Any:
        if name == "testing":
            raise AssertionError("Runtime audit must not import numpy.testing")
        return getattr(np, name)


def metadata(spec: source.FixedSourceSpec) -> dict:
    """Provide synthetic numeric declarations, not measured ROOT metadata."""
    return {
        "uuid": spec.expected_uuid,
        "tree": source.TREE_NAME,
        "entries": 4096,
        "branches": {
            name: {
                "dtype": "f8",
                "shape": rule["shape"],
                "declaration": "SYNTHETIC float64",
            }
            for name, rule in audit.branch_contract().items()
        },
        "producer_markers_verbatim": [],
        "publisher_checksum": None,
    }


class FakeReader:
    """Return a fresh fake row and record all access and closure."""

    def __init__(
        self,
        resolved: source.ResolvedSource,
        *,
        mutate: Callable[[dict[str, Any]], None] | None = None,
        empty: bool = False,
    ) -> None:
        self.metadata = metadata(resolved.spec)
        self.entries = []
        self.closed = False
        self.mutate = mutate
        self.empty = empty

    def read_entry(self, entry: int) -> dict:
        self.entries.append(entry)
        raw = _raw_entry(entry)
        if self.empty:
            raw["n_prongs"] = 0
            for name in (
                source.PRONG_VECTOR_BRANCHES
                + source.PRONG_NESTED_BRANCHES
                + source.BLOB_BASES
            ):
                raw[name] = []
            for name in source.BLOB_COUNT_BRANCHES:
                raw[name] = 0
            raw["gamma1_E"] = raw["gamma2_E"] = 0
        if self.mutate:
            self.mutate(raw)
        return raw

    def close(self) -> None:
        self.closed = True


def run_fake(
    tmp_path: Path,
    *,
    mutate: Callable[[dict[str, Any]], None] | None = None,
    metadata_mutate: Any = None,
    check_resources: Any = lambda: None,
    empty: bool = False,
    forward: Any = lambda batch: None,
) -> tuple:
    readers = []

    def factory(resolved: source.ResolvedSource) -> Any:
        reader = FakeReader(resolved, mutate=mutate, empty=empty)
        readers.append(reader)
        if metadata_mutate:
            metadata_mutate(reader.metadata)
        return reader

    receipt = audit.run_audit(
        REPO_ROOT,
        tmp_path / "audit",
        reader_factory=factory,
        forward_check=forward,
        check_resources=check_resources,
        bindings={"execution_mode": "SYNTHETIC_FAKE_READER_NOT_SOURCE_EVIDENCE"},
    )
    return receipt, readers


@pytest.mark.parametrize(
    "alter",
    [
        lambda item: item.update(uuid="wrong"),
        lambda item: item.update(tree="wrong"),
        lambda item: item.update(entries=4095),
        lambda item: item.update(entries=4096.0),
        lambda item: item["branches"].pop("n_prongs"),
        lambda item: item["branches"].update(extra={}),
        lambda item: item["branches"]["ev_run"].update(dtype="O"),
        lambda item: item["branches"]["ev_run"].update(shape=[None]),
        lambda item: item["branches"]["prong_part_E"].update(shape=[None, 3]),
        lambda item: item["branches"]["ev_run"].update(declaration=""),
    ],
)
def test_metadata_failure_precedes_payload(
    tmp_path: Path, alter: Callable[[dict[str, Any]], None]
) -> None:
    receipt, readers = run_fake(tmp_path, metadata_mutate=alter)
    assert receipt["mapping"] == "FAIL"
    assert receipt["terminal"] == "INCOMPLETE"
    assert len(readers) == 1 and readers[0].entries == [] and readers[0].closed
    assert (tmp_path / "audit/data/metadata.json").is_file()
    assert receipt["exceptions"][0]["phase"] == "metadata"
    assert receipt["release"] == "RELEASE_UNVERIFIED"


@pytest.mark.parametrize(
    "branch,value",
    [
        ("ev_run", 1.5),
        ("ev_gate", np.nan),
        ("n_prongs", -1),
        ("n_prongs", 2.5),
        ("cluster_energy_sz", 14),
        ("prong_part_score", [1]),
        ("prong_part_E", [[1, 2, 3]] * 3),
        ("gamma1_direction", [0, 1]),
        ("gamma1_E", np.nan),
        ("vtx", [np.nan, 0, 0, 0]),
        ("prong_part_pid", [1e30, 8, 13]),
        ("prong_part_mass", [1e100, 0, 0]),
        ("cluster_view", [1] * 14),
        ("MasterAnaDev_BlobY_sz", 1),
        ("prong_part_score", "bad"),
    ],
)
def test_malformed_rows_remain_archived(
    tmp_path: Path, branch: str, value: Any
) -> None:
    receipt, readers = run_fake(
        tmp_path, mutate=lambda raw: raw.update({branch: value})
    )
    assert receipt["mapping"] == "FAIL"
    assert receipt["sources"][0]["captured_entries"] == [0]
    assert receipt["sources"][0]["completed_entries"] == []
    assert all(reader.closed for reader in readers)
    raw = json.loads((tmp_path / "audit/data/raw/0000.json").read_bytes())
    frame = next(frame for frame in raw if frame["branch"] == branch)
    assert frame["raw"] == audit.raw_encoding(value)
    assert receipt["exceptions"]


def test_missing_and_extra_raw_branches_are_preserved(tmp_path: Path) -> None:
    def mutate(raw: dict[str, Any]) -> None:
        del raw["n_prongs"]
        raw["unexpected"] = [17]

    receipt, _ = run_fake(tmp_path, mutate=mutate)
    assert receipt["mapping"] == "FAIL"
    frames = json.loads((tmp_path / "audit/data/raw/0000.json").read_bytes())
    assert frames[-1]["branch"] == "unexpected"


def test_raw_nonfinite_bits_and_ragged_shapes() -> None:
    values = np.array([0x7FF8000000001234, 0xFFF0000000000000], dtype=np.uint64).view(
        np.float64
    )
    encoded = audit.raw_encoding(values)
    import base64

    assert base64.b64decode(encoded["bytes_base64"]) == values.tobytes()
    encoded = audit.raw_encoding(
        [np.array([1], dtype=np.int16), np.array([2, 3], dtype=np.float32)]
    )
    assert [item["dtype"] for item in encoded["sequence"]] == ["<i2", "<f4"]
    assert [item["shape"] for item in encoded["sequence"]] == [[1], [2]]


def test_independent_mapping_detects_corrupt_value_mask_and_membership() -> None:
    raw = _raw_entry(1)
    batch = audit.map_row(raw, source.FIXED_SOURCES[0], 0)
    audit.check_mapping(raw, batch)
    changed = copy.deepcopy(batch)
    changed.descriptors.families["prongs"].values["score"][0] = 7
    with pytest.raises(AssertionError, match="storage mismatch"):
        audit.check_mapping(raw, changed)
    changed = copy.deepcopy(batch)
    changed.descriptors.families["prongs"].masks["charge"][0] = True
    with pytest.raises(AssertionError):
        audit.check_mapping(raw, changed)
    changed = copy.deepcopy(batch)
    changed.descriptors.families["prongs"].token_mask[0] = False
    with pytest.raises(AssertionError, match="structural"):
        audit.check_mapping(raw, changed)


@pytest.mark.parametrize(
    "pid,charge,score,mass,charge_valid",
    [
        (3, 0, 1, 105.658, True),
        (3, 2, 1, 105.658, True),
        (3, 7, 1, 105.658, True),
        (0, 0, 0, -1, False),
        (-999, -999, -1, -1, False),
        (13, 0, 0.25, -1, False),
        (8, 0, 0.75, 938.272, False),
        (np.nan, 2, np.nan, np.inf, False),
        (3.5, 2, 0, 0, False),
    ],
)
def test_v2_masks_keep_every_raw_prong(
    pid: float, charge: float, score: float, mass: float, charge_valid: bool
) -> None:
    raw = _raw_entry(1)
    for name, value in (
        ("pid", pid),
        ("charge", charge),
        ("score", score),
        ("mass", mass),
    ):
        raw[f"prong_part_{name}"][0] = value
    batch = audit.map_row(raw, source.FIXED_SOURCES[0], 0)
    audit.check_mapping(raw, batch)
    prongs = batch.descriptors.families["prongs"]
    assert prongs.counts.tolist() == [3]
    assert bool(prongs.masks["charge"][0, 0]) == charge_valid
    assert bool(prongs.masks["score"][0, 0]) == (np.isfinite(score) and score != -1)
    assert bool(prongs.masks["mass"][0, 0]) == (np.isfinite(mass) and mass != -1)


def test_simultaneous_semantic_discrepancies_and_anchor_partition() -> None:
    raw = _raw_entry(0)
    raw["prong_part_pid"][0] = 3
    raw["prong_part_score"][0] = 0.4
    raw["prong_part_mass"][0] = -1
    raw["prong_part_charge"][0] = 9
    raw["prong_part_pos"][0][3] = 10001
    telemetry = audit.Telemetry()
    observed = telemetry.observe(raw, "data", 0)
    failed = {
        check["check"]
        for check in observed["checks"]
        if check["token"] == 0 and check["verdict"] == "DISCREPANCY"
    }
    assert {"sentinel_score", "sentinel_mass", "charge_support", "prong_time"} <= failed
    telemetry.observe(raw, "mc", 16)
    assert set(telemetry.verdicts()) == {"data/anchor_0_16", "mc/extension_16_4096"}
    assert len(observed["photons"]) == 2
    assert observed["prongs"][0]["masks"]["charge"] == [True]


@pytest.mark.parametrize(
    "limit", ["wall_seconds", "memory_bytes", "threads", "cpu_seconds"]
)
def test_resource_stop_preserves_partial_receipt(tmp_path: Path, limit: str) -> None:
    calls = 0

    def check() -> None:
        nonlocal calls
        calls += 1
        if calls == 6:
            raise audit.ResourceLimit(limit)

    receipt, readers = run_fake(tmp_path, check_resources=check)
    assert receipt["mapping"] == "FAIL"
    assert receipt["exceptions"][0]["type"] == "ResourceLimit"
    assert all(reader.closed for reader in readers)
    assert (tmp_path / "audit/receipt.json").is_file()


def test_output_limit_does_not_write_or_truncate_raw(tmp_path: Path) -> None:
    with mock.patch.object(audit, "FILE_LIMIT", 1):
        # The reserve for a terminal receipt is tested separately from artifact limits.
        output = audit.AuditOutput(tmp_path / "out", lambda: None)
        with pytest.raises(audit.ResourceLimit):
            output.write("raw.json", b"too large")
    assert not list((tmp_path / "out").iterdir())


@mock.patch.object(audit, "np", RuntimeNumpy())
def test_exact_two_sources_and_full_range_with_fake_readers(tmp_path: Path) -> None:
    calls = []
    receipt, readers = run_fake(
        tmp_path,
        empty=True,
        forward=lambda batch: calls.append(batch.descriptors.row_count),
    )
    assert receipt["mapping"] == "PASS", receipt["exceptions"]
    assert receipt["terminal"] == "COMPLETE"
    assert len(readers) == 2
    assert all(
        reader.entries == list(range(4096)) and reader.closed for reader in readers
    )
    assert calls == [16] * 512
    assert len(receipt["ordered_source_rows"]) == 8192
    assert all(
        item["completed_entries"] == list(range(4096)) for item in receipt["sources"]
    )
    assert receipt["semantic"] == "UNRESOLVED"
    assert receipt["release"] == "RELEASE_UNVERIFIED"
    assert set(receipt["object_families"].values()) == {"UNRESOLVED"}
    for table in receipt["correspondence_checks"].values():
        assert table["photon_direction"]["verdict"] == "NOT_TESTED"
    assert len(receipt["per_branch_sha256"]) == 75
    first = tmp_path / "audit/data/raw/0000.json"
    assert (
        hashlib.sha256(first.read_bytes()).hexdigest()
        == receipt["artifacts"]["data/raw/0000.json"]["sha256"]
    )


@mock.patch.object(audit, "np", RuntimeNumpy())
def test_real_forward_with_identity_statistics_only() -> None:
    pytest.importorskip("tensorflow")
    raw = _raw_entry(1)
    batch = audit.map_row(raw, source.FIXED_SOURCES[0], 0)
    with mock.patch.object(
        typed,
        "fit_frozen_normalization_for_smoke",
        side_effect=AssertionError("fit forbidden"),
    ):
        forward = audit.ForwardCheck()
        forward(batch)
    assert (
        forward.normalization.fitting_policy
        == "SOURCE_AUDIT_IDENTITY_NOT_FITTED_NOT_FOR_TRAINING"
    )


def test_launcher_requires_authorization_and_rejects_hash_mismatch(
    tmp_path: Path,
) -> None:
    path = tmp_path / "authorization.json"
    path.write_text("{}")
    with pytest.raises(ValueError, match="SHA-256"):
        launcher.validate_authorization(path, "0" * 64, "a" * 40)
    with pytest.raises(ValueError, match="does not match"):
        launcher.validate_authorization(path, launcher.digest_file(path), "a" * 40)


def test_root_reader_rejects_repeated_extended_or_reordered_entries() -> None:
    reader = object.__new__(launcher.RootAuditReader)
    reader.next_entry = 0
    for entry in (-1, 4096, 1, 0.0, True):
        with pytest.raises(ValueError, match="out-of-scope"):
            reader.read_entry(entry)


@pytest.mark.parametrize("name,observed", [("Threads", "3"), ("VmRSS", "9000000 kB")])
def test_runtime_budget_observes_native_thread_and_memory_limits(
    name: str, observed: str
) -> None:
    fields = {"Threads": "1", "VmRSS": "100 kB"}
    fields[name] = observed
    status = "\n".join(f"{key}: {value}" for key, value in fields.items())
    budget = launcher.RuntimeBudget()
    with mock.patch.object(Path, "read_text", return_value=status):
        with pytest.raises(audit.ResourceLimit):
            budget.check()


def test_runtime_wall_limit_and_linux_requirement() -> None:
    budget = launcher.RuntimeBudget()
    with mock.patch.object(
        launcher.time, "monotonic", return_value=budget.started + 1801
    ), mock.patch.object(Path, "read_text", return_value="Threads: 1\nVmRSS: 100 kB"):
        with pytest.raises(audit.ResourceLimit, match="wall_seconds"):
            budget.check()
    with mock.patch.object(launcher.platform, "system", return_value="unsupported"):
        with pytest.raises(RuntimeError, match="Linux"):
            budget.install()


def test_runtime_installs_hard_limits_without_widening_existing_limits() -> None:
    budget = launcher.RuntimeBudget()
    with mock.patch.object(
        launcher.platform, "system", return_value="Linux"
    ), mock.patch.object(
        launcher.resource, "getrlimit", return_value=(100, 200)
    ), mock.patch.object(
        launcher.resource, "setrlimit"
    ) as limits, mock.patch.object(
        launcher.signal, "signal"
    ), mock.patch.object(
        launcher.signal, "setitimer"
    ), mock.patch.object(
        budget, "check"
    ):
        budget.install()
    assert len(limits.call_args_list) == 3
    assert all(call.args[1] == (100, 100) for call in limits.call_args_list)


def test_closed_shard_rejects_v1_and_retains_row_arrays() -> None:
    import io

    raw = _raw_entry(0)
    batch = audit.map_row(raw, source.FIXED_SOURCES[0], 0)
    provenance = typed.ShardProvenance(
        "a" * 64,
        "synthetic",
        (("purpose", "test"),),
        (typed.SourceFileMetadata(1, "fake.root", "fake-uuid"),),
    )
    payload = audit._shard_bytes(batch, provenance)
    with np.load(io.BytesIO(payload), allow_pickle=False) as loaded:
        arrays = dict(loaded)
        np.testing.assert_array_equal(
            arrays["audit.event_keys"], batch.tuple_event_keys
        )
        schema_keys = [key for key in arrays if "schema_version" in key]
    assert schema_keys
    for key in schema_keys:
        arrays[key] = np.asarray("pet-typed-descriptors-v1")
    with pytest.raises(ValueError):
        typed.descriptor_batch_from_arrays(arrays)


def test_duplicate_event_groups_are_recorded_without_dropping_rows(
    tmp_path: Path,
) -> None:
    def mutate(raw: dict[str, Any]) -> None:
        raw["ev_gate"] = 12

    def stop_after_chunk(batch: source.SourceContractBatch) -> None:
        raise RuntimeError("synthetic bounded stop after checking duplicate groups")

    receipt, _ = run_fake(tmp_path, mutate=mutate, forward=stop_after_chunk)
    assert receipt["duplicate_event_groups"][0]["entries"] == list(range(16))
    assert receipt["sources"][0]["mapped_entries"] == list(range(16))
    assert receipt["sources"][0]["completed_entries"] == []


def test_output_aggregate_limit_leaves_no_extra_file(tmp_path: Path) -> None:
    output = audit.AuditOutput(tmp_path / "out", lambda: None)
    output.total_bytes = audit.LIMITS["output_bytes"] - audit.OUTPUT_RESERVE
    with pytest.raises(audit.ResourceLimit):
        output.write("extra", b"x")
    assert not list((tmp_path / "out").iterdir())


def test_manifest_failure_opens_no_sources(tmp_path: Path) -> None:
    with mock.patch.object(
        source,
        "resolve_fixed_sources",
        side_effect=ValueError("manifest SHA-256 mismatch"),
    ):
        receipt, readers = run_fake(tmp_path)
    assert readers == [] and receipt["sources"] == []
    assert receipt["mapping"] == "FAIL"


def test_raw_read_failure_is_not_retried(tmp_path: Path) -> None:
    with mock.patch.object(
        FakeReader, "read_entry", side_effect=OSError("fake source read error")
    ) as read:
        receipt, readers = run_fake(tmp_path)
    assert read.call_count == 1 and all(reader.closed for reader in readers)
    assert receipt["sources"][0]["attempted_entries"] == [0]
    assert receipt["sources"][0]["captured_entries"] == []


def test_native_reader_preserves_branch_errors_and_unexpected_shapes() -> None:
    import types

    reader = object.__new__(launcher.RootAuditReader)
    reader.next_entry = 0
    reader.source = source
    spec = source.FIXED_SOURCES[0]
    reader.metadata = metadata(spec)
    raw = _raw_entry(0)
    raw["prong_part_E"] = [[1.0], [2.0, 3.0]]
    del raw["gamma1_E"]
    reader.tree = types.SimpleNamespace(GetEntry=lambda entry: 1, **raw)
    captured = reader.read_entry(0)
    assert captured["gamma1_E"]["extraction_exception"] == "AttributeError"
    assert [len(vector) for vector in captured["prong_part_E"]] == [1, 2]
    with pytest.raises(ValueError, match="out-of-scope"):
        reader.read_entry(0)


def test_launcher_captures_logs_and_binds_terminal_accounting(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    commit = "a" * 40
    output = tmp_path / "launched"
    monkeypatch.setattr(launcher, "check_preparation", lambda: {})
    monkeypatch.setattr(
        launcher,
        "validate_authorization",
        lambda *args: {"authority_reference": "SYNTHETIC ONLY"},
    )
    monkeypatch.setattr(
        launcher.subprocess,
        "check_output",
        lambda command, **kwargs: commit + "\n" if command[1] == "rev-parse" else "",
    )
    monkeypatch.setattr(launcher.RuntimeBudget, "install", lambda self: None)
    monkeypatch.setattr(launcher.RuntimeBudget, "check", lambda self: None)
    readers = []

    def factory(resolved: source.ResolvedSource) -> Any:
        reader = FakeReader(resolved)
        readers.append(reader)
        reader.metadata["uuid"] = "synthetic identity failure"
        return reader

    monkeypatch.setattr(launcher, "RootAuditReader", factory)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "audit",
            "--authorization",
            "unused.json",
            "--authorization-sha256",
            "b" * 64,
            "--expected-commit",
            commit,
            "--output",
            str(output),
        ],
    )
    assert launcher.main() == 1
    assert len(readers) == 1 and readers[0].entries == [] and readers[0].closed
    accounting = json.loads((output / "accounting.json").read_bytes())
    assert accounting["receipt_sha256"] == launcher.digest_file(output / "receipt.json")
    assert set(accounting["closed_auxiliary_artifacts"]) == {
        "stdout.log",
        "stderr.log",
        "interrupted.json",
        "progress.jsonl",
    }


def test_preparation_hashes_and_no_root_import() -> None:
    with mock.patch.dict(sys.modules, {"ROOT": None}):
        binding = launcher.check_preparation()
    assert binding["execution_authorized"] is False
    assert len(binding["ordered_branches"]) == 75


def test_output_namespace_cannot_overwrite_evidence(tmp_path: Path) -> None:
    destination = tmp_path / "audit"
    destination.mkdir()
    marker = destination / "original"
    marker.write_text("retain")
    with pytest.raises(FileExistsError):
        run_fake(tmp_path)
    assert marker.read_text() == "retain"
