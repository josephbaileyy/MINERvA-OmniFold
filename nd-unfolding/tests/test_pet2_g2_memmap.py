"""Login-safe tests for receipt-bound chunked G2 conversion and loading."""

from __future__ import annotations

import json
import fcntl
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock
import zipfile

import numpy as np

ND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ND not in sys.path:
    sys.path.insert(0, ND)

from pet2_torch.g2_adapter import (  # noqa: E402
    G2_ESTIMATOR_FINGERPRINT,
    G2_SCHEMA_VERSION,
    _legacy_order_hash,
)
from pet2_torch.g2_memmap import (  # noqa: E402
    COMPLETE_NAME,
    MANIFEST_NAME,
    PROGRESS_NAME,
    convert_g2_npz_to_memmap,
    open_g2_memmap_inventory,
    preflight_streamable_g2_npz,
)
import pet2_torch.g2_memmap as g2_memmap_module  # noqa: E402
from pet2_torch.utils import file_sha256, fingerprint  # noqa: E402


def _tiny_g2_arrays(*, signal_rows=7, data_rows=5, background_rows=3, tokens=4):
    rng = np.random.default_rng(703)
    pass_truth = np.ones(signal_rows, dtype=bool)
    pass_reco = np.ones(signal_rows, dtype=bool)
    pass_reco[1] = False
    part_reco = rng.uniform(1, 20, (signal_rows, tokens, 3)).astype(np.float32)
    reco_view = rng.integers(1, 4, (signal_rows, tokens), dtype=np.int16)
    part_reco[~pass_reco] = 0
    reco_view[~pass_reco] = 0
    part_gen = rng.uniform(1, 20, (signal_rows, tokens, 5)).astype(np.float32)
    part_gen[:, :, 4] = 211
    measured_pc = rng.uniform(1, 20, (data_rows, tokens, 3)).astype(np.float32)
    data_view = rng.integers(1, 4, (data_rows, tokens), dtype=np.int16)
    bkg_part_reco = rng.uniform(
        1, 20, (background_rows, tokens, 3)
    ).astype(np.float32)
    bkg_view = rng.integers(1, 4, (background_rows, tokens), dtype=np.int16)
    w_truth = rng.uniform(0.5, 1.5, signal_rows).astype(np.float64)
    w_reco = rng.uniform(0.5, 1.5, signal_rows).astype(np.float64)
    w_bkg = rng.uniform(0.5, 1.5, background_rows).astype(np.float64)
    bkg_indices = np.arange(background_rows, dtype=np.int64)

    def scalars(rows):
        return rng.uniform(0.1, 4, (rows, 4)).astype(np.float32)

    def muon(rows):
        return rng.uniform(0.1, 50, (rows, 7)).astype(np.float32)

    def vertex(rows):
        return rng.uniform(-500, 500, (rows, 3)).astype(np.float32)

    arrays = {
        "part_reco": part_reco,
        "part_gen": part_gen,
        "reco_scalars": scalars(signal_rows),
        "truth_scalars": scalars(signal_rows),
        "reco_muon": muon(signal_rows),
        "reco_vertex": vertex(signal_rows),
        "reco_view": reco_view,
        "reco_time": rng.uniform(0, 10, (signal_rows, tokens)).astype(np.float32),
        "pass_reco": pass_reco,
        "pass_truth": pass_truth,
        "w_reco": w_reco,
        "w_truth": w_truth,
        "measured_pc": measured_pc,
        "measured_scalars": scalars(data_rows),
        "data_muon": muon(data_rows),
        "data_vertex": vertex(data_rows),
        "data_view": data_view,
        "data_time": rng.uniform(0, 10, (data_rows, tokens)).astype(np.float32),
        "bkg_part_reco": bkg_part_reco,
        "bkg_reco_scalars": scalars(background_rows),
        "bkg_muon": muon(background_rows),
        "bkg_vertex": vertex(background_rows),
        "bkg_view": bkg_view,
        "bkg_time": rng.uniform(0, 10, (background_rows, tokens)).astype(
            np.float32
        ),
        "w_bkg": w_bkg,
        "bkg_indices": bkg_indices,
        "sig_identity_hash": np.asarray(
            _legacy_order_hash(w_truth, pass_truth)
        ),
        "data_identity_hash": np.asarray(_legacy_order_hash(measured_pc)),
        "bkg_identity_hash": np.asarray(_legacy_order_hash(w_bkg, bkg_indices)),
        "estimator_fingerprint": np.asarray(G2_ESTIMATOR_FINGERPRINT),
        "data_pot": np.asarray(1.23e20, dtype=np.float64),
        "petSchemaVersion": np.asarray(G2_SCHEMA_VERSION),
        "hasFullEventSchema": np.asarray(1, dtype=np.int8),
        "fullPhaseSpace": np.asarray(1, dtype=np.int8),
    }
    return arrays


def _write_packet(path: Path, arrays=None):
    np.savez_compressed(path, **(_tiny_g2_arrays() if arrays is None else arrays))
    return file_sha256(path), path.stat().st_size


def _rewrite_member(path: Path, key: str, transform):
    member = f"{key}.npy"
    with zipfile.ZipFile(path, "r") as archive:
        payloads = {
            info.filename: archive.read(info.filename)
            for info in archive.infolist()
        }
    payloads[member] = transform(payloads[member])
    replacement = path.with_suffix(".replacement.npz")
    with zipfile.ZipFile(
        replacement, "w", compression=zipfile.ZIP_DEFLATED
    ) as archive:
        for name, payload in payloads.items():
            archive.writestr(name, payload)
    replacement.replace(path)
    return file_sha256(path), path.stat().st_size


def _interrupt_stream_after(array_count: int):
    original = g2_memmap_module._stream_member
    completed = 0

    def stream_then_interrupt(*args, **kwargs):
        nonlocal completed
        record = original(*args, **kwargs)
        completed += 1
        if completed >= array_count:
            raise RuntimeError("injected conversion interruption")
        return record

    return mock.patch.object(
        g2_memmap_module, "_stream_member", side_effect=stream_then_interrupt
    )


class G2MemmapConversionContract(unittest.TestCase):
    def test_success_read_only_windows_and_idempotence(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "g2.npz"
            digest, size = _write_packet(source)
            output = root / "converted"
            manifest = convert_g2_npz_to_memmap(
                source,
                output,
                expected_sha256=digest,
                expected_size_bytes=size,
                timestamp_utc="2026-07-23T00:00:00Z",
                chunk_bytes=4096,
            )
            self.assertFalse(manifest["g2_validation_claim"])
            self.assertFalse(manifest["publication_promotion_permitted"])
            self.assertTrue((output / MANIFEST_NAME).is_file())
            self.assertTrue((output / COMPLETE_NAME).is_file())
            inventory = open_g2_memmap_inventory(
                output, source_npz=source, chunk_bytes=4096
            )
            try:
                self.assertEqual(inventory.row_counts["signal"], 7)
                self.assertIsInstance(inventory.arrays["part_reco"], np.memmap)
                self.assertFalse(inventory.arrays["part_reco"].flags.writeable)
                window = inventory.window("signal", 1, 4)
                self.assertEqual(window["part_reco"].shape[0], 3)
                chunks = list(inventory.iter_windows("background", 2))
                self.assertEqual([(a, b) for a, b, _ in chunks], [(0, 2), (2, 3)])
            finally:
                inventory.close()
            repeated = convert_g2_npz_to_memmap(
                source,
                output,
                expected_sha256=digest,
                expected_size_bytes=size,
                timestamp_utc="ignored-on-idempotent-verify",
                chunk_bytes=4096,
            )
            self.assertEqual(repeated["fingerprint"], manifest["fingerprint"])

    def test_interrupted_and_content_verified_resume(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "g2.npz"
            digest, size = _write_packet(source)
            output = root / "converted"
            with _interrupt_stream_after(3):
                with self.assertRaisesRegex(RuntimeError, "injected"):
                    convert_g2_npz_to_memmap(
                        source,
                        output,
                        expected_sha256=digest,
                        expected_size_bytes=size,
                        timestamp_utc="2026-07-23T00:00:00Z",
                        chunk_bytes=4096,
                    )
            stage = root / ".converted.partial"
            progress = json.loads((stage / PROGRESS_NAME).read_text())
            first = next(iter(progress["arrays"].values()))
            completed = stage / first["path"]
            with completed.open("ab") as handle:
                handle.write(b"mutation")
            manifest = convert_g2_npz_to_memmap(
                source,
                output,
                expected_sha256=digest,
                expected_size_bytes=size,
                timestamp_utc="2026-07-23T00:00:00Z",
                chunk_bytes=4096,
                resume=True,
            )
            self.assertEqual(manifest["status"], "complete_code_contract_only")
            self.assertFalse(stage.exists())
            # The persistent lock inode is harmless: the advisory lock is
            # released by normal exit and by an ungraceful process death.
            lock_path = root / ".converted.lock"
            with lock_path.open("r+") as handle:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

    def test_resume_revalidates_record_semantics_and_progress_status(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "g2.npz"
            digest, size = _write_packet(source)
            output = root / "converted"
            with _interrupt_stream_after(3):
                with self.assertRaisesRegex(RuntimeError, "injected"):
                    convert_g2_npz_to_memmap(
                        source,
                        output,
                        expected_sha256=digest,
                        expected_size_bytes=size,
                        timestamp_utc="2026-07-23T00:00:00Z",
                        chunk_bytes=4096,
                    )
            progress_path = root / ".converted.partial" / PROGRESS_NAME
            progress = json.loads(progress_path.read_text())
            key = next(iter(progress["arrays"]))
            progress["arrays"][key]["units"] = "mutated"
            clean = dict(progress)
            clean.pop("fingerprint")
            progress["fingerprint"] = fingerprint(clean)
            progress_path.write_text(json.dumps(progress))
            manifest = convert_g2_npz_to_memmap(
                source,
                output,
                expected_sha256=digest,
                expected_size_bytes=size,
                timestamp_utc="2026-07-23T00:00:00Z",
                chunk_bytes=4096,
                resume=True,
            )
            self.assertNotEqual(manifest["arrays"][key]["units"], "mutated")

            output2 = root / "converted2"
            with _interrupt_stream_after(1):
                with self.assertRaisesRegex(RuntimeError, "injected"):
                    convert_g2_npz_to_memmap(
                        source,
                        output2,
                        expected_sha256=digest,
                        expected_size_bytes=size,
                        timestamp_utc="2026-07-23T00:00:00Z",
                        chunk_bytes=4096,
                    )
            progress_path2 = root / ".converted2.partial" / PROGRESS_NAME
            progress2 = json.loads(progress_path2.read_text())
            progress2["status"] = "complete"
            clean2 = dict(progress2)
            clean2.pop("fingerprint")
            progress2["fingerprint"] = fingerprint(clean2)
            progress_path2.write_text(json.dumps(progress2))
            with self.assertRaisesRegex(ValueError, "stale or malformed"):
                convert_g2_npz_to_memmap(
                    source,
                    output2,
                    expected_sha256=digest,
                    expected_size_bytes=size,
                    timestamp_utc="2026-07-23T00:00:00Z",
                    chunk_bytes=4096,
                    resume=True,
                )
            self.assertFalse(output2.exists())

    def test_source_mutation_during_conversion_never_publishes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "g2.npz"
            digest, size = _write_packet(source)
            output = root / "converted"
            original = g2_memmap_module._stream_member
            mutated = False

            def stream_and_mutate(*args, **kwargs):
                nonlocal mutated
                record = original(*args, **kwargs)
                if not mutated:
                    with source.open("ab") as handle:
                        handle.write(b"source-race")
                    mutated = True
                return record

            with mock.patch.object(
                g2_memmap_module, "_stream_member", side_effect=stream_and_mutate
            ):
                with self.assertRaisesRegex(ValueError, "changed during conversion"):
                    convert_g2_npz_to_memmap(
                        source,
                        output,
                        expected_sha256=digest,
                        expected_size_bytes=size,
                        timestamp_utc="2026-07-23T00:00:00Z",
                        chunk_bytes=4096,
                    )
            self.assertFalse(output.exists())

    def test_concurrent_converter_lock_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "g2.npz"
            digest, size = _write_packet(source)
            lock_path = root / ".converted.lock"
            with lock_path.open("w+") as handle:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                with self.assertRaisesRegex(RuntimeError, "already active"):
                    convert_g2_npz_to_memmap(
                        source,
                        root / "converted",
                        expected_sha256=digest,
                        expected_size_bytes=size,
                        timestamp_utc="2026-07-23T00:00:00Z",
                        chunk_bytes=4096,
                    )

    def test_bound_input_rejects_wrong_hash_or_size(self):
        with tempfile.TemporaryDirectory() as td:
            source = Path(td) / "g2.npz"
            digest, size = _write_packet(source)
            with self.assertRaisesRegex(ValueError, "size/SHA"):
                convert_g2_npz_to_memmap(
                    source,
                    Path(td) / "converted",
                    expected_sha256="0" * 64,
                    expected_size_bytes=size,
                    timestamp_utc="2026-07-23T00:00:00Z",
                )
            with self.assertRaisesRegex(ValueError, "size/SHA"):
                convert_g2_npz_to_memmap(
                    source,
                    Path(td) / "converted",
                    expected_sha256=digest,
                    expected_size_bytes=size + 1,
                    timestamp_utc="2026-07-23T00:00:00Z",
                )

    def test_fortran_order_is_preserved_from_npy_header(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "g2.npz"
            arrays = _tiny_g2_arrays()
            arrays["reco_scalars"] = np.asfortranarray(arrays["reco_scalars"])
            digest, size = _write_packet(source, arrays)
            manifest = convert_g2_npz_to_memmap(
                source,
                root / "converted",
                expected_sha256=digest,
                expected_size_bytes=size,
                timestamp_utc="2026-07-23T00:00:00Z",
                chunk_bytes=4096,
            )
            self.assertTrue(
                manifest["arrays"]["reco_scalars"]["fortran_order"]
            )
            inventory = open_g2_memmap_inventory(
                root / "converted", source_npz=source, chunk_bytes=4096
            )
            try:
                self.assertTrue(inventory.arrays["reco_scalars"].flags.f_contiguous)
            finally:
                inventory.close()

    def test_truncated_or_trailing_member_payload_fails_conversion(self):
        for suffix, transform, message in (
            ("truncated", lambda payload: payload[:-1], "truncated NPY payload"),
            ("trailing", lambda payload: payload + b"x", "trailing data"),
        ):
            with self.subTest(suffix=suffix), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                source = root / f"{suffix}.npz"
                _write_packet(source)
                digest, size = _rewrite_member(source, "reco_time", transform)
                with self.assertRaisesRegex(ValueError, message):
                    convert_g2_npz_to_memmap(
                        source,
                        root / "converted",
                        expected_sha256=digest,
                        expected_size_bytes=size,
                        timestamp_utc="2026-07-23T00:00:00Z",
                        chunk_bytes=4096,
                    )

    def test_stale_input_missing_array_and_mutated_array_fail(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "g2.npz"
            digest, size = _write_packet(source)
            output = root / "converted"
            convert_g2_npz_to_memmap(
                source,
                output,
                expected_sha256=digest,
                expected_size_bytes=size,
                timestamp_utc="2026-07-23T00:00:00Z",
            )
            part = output / "part_reco.npy"
            os.chmod(part, 0o644)
            with part.open("ab") as handle:
                handle.write(b"x")
            with self.assertRaisesRegex(ValueError, "content hash"):
                open_g2_memmap_inventory(output, source_npz=source)
            part.unlink()
            with self.assertRaisesRegex(FileNotFoundError, "absent"):
                open_g2_memmap_inventory(output, source_npz=source)

    def test_manifest_mutation_and_stale_source_fail(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "g2.npz"
            digest, size = _write_packet(source)
            output = root / "converted"
            convert_g2_npz_to_memmap(
                source,
                output,
                expected_sha256=digest,
                expected_size_bytes=size,
                timestamp_utc="2026-07-23T00:00:00Z",
            )
            manifest_path = output / MANIFEST_NAME
            manifest = json.loads(manifest_path.read_text())
            manifest["status"] = "mutated"
            manifest_path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "completion marker"):
                open_g2_memmap_inventory(output, source_npz=source)

            # Rebuild separately, then mutate the still-required bound source.
            source2 = root / "g2b.npz"
            digest2, size2 = _write_packet(source2)
            output2 = root / "converted2"
            convert_g2_npz_to_memmap(
                source2,
                output2,
                expected_sha256=digest2,
                expected_size_bytes=size2,
                timestamp_utc="2026-07-23T00:00:00Z",
            )
            with source2.open("ab") as handle:
                handle.write(b"stale")
            with self.assertRaisesRegex(ValueError, "stale"):
                open_g2_memmap_inventory(output2, source_npz=source2)

    def test_completion_input_binding_and_record_paths_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "g2.npz"
            digest, size = _write_packet(source)

            output = root / "converted"
            convert_g2_npz_to_memmap(
                source,
                output,
                expected_sha256=digest,
                expected_size_bytes=size,
                timestamp_utc="2026-07-23T00:00:00Z",
            )
            complete_path = output / COMPLETE_NAME
            complete = json.loads(complete_path.read_text())
            complete["input_sha256"] = "0" * 64
            complete_path.write_text(json.dumps(complete))
            with self.assertRaisesRegex(ValueError, "bind the input"):
                open_g2_memmap_inventory(output, source_npz=source)

            output2 = root / "converted2"
            convert_g2_npz_to_memmap(
                source,
                output2,
                expected_sha256=digest,
                expected_size_bytes=size,
                timestamp_utc="2026-07-23T00:00:00Z",
            )
            manifest_path = output2 / MANIFEST_NAME
            complete_path = output2 / COMPLETE_NAME
            manifest = json.loads(manifest_path.read_text())
            manifest["arrays"]["part_reco"]["path"] = "../part_reco.npy"
            clean_manifest = dict(manifest)
            clean_manifest.pop("fingerprint")
            manifest["fingerprint"] = fingerprint(clean_manifest)
            manifest_path.write_text(json.dumps(manifest))
            complete = json.loads(complete_path.read_text())
            complete["manifest_sha256"] = file_sha256(manifest_path)
            complete_path.write_text(json.dumps(complete))
            with self.assertRaisesRegex(ValueError, "record semantics"):
                open_g2_memmap_inventory(output2, source_npz=source)

    def test_row_family_mismatch_fails_before_publish(self):
        with tempfile.TemporaryDirectory() as td:
            source = Path(td) / "g2.npz"
            arrays = _tiny_g2_arrays()
            arrays["reco_time"] = arrays["reco_time"][:-1]
            digest, size = _write_packet(source, arrays)
            with self.assertRaisesRegex(ValueError, "row counts"):
                convert_g2_npz_to_memmap(
                    source,
                    Path(td) / "converted",
                    expected_sha256=digest,
                    expected_size_bytes=size,
                    timestamp_utc="2026-07-23T00:00:00Z",
                )

    def test_object_dtype_and_missing_member_fail_preflight(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            object_source = root / "object.npz"
            arrays = _tiny_g2_arrays()
            arrays["reco_time"] = np.asarray([{"unsafe": True}], dtype=object)
            _write_packet(object_source, arrays)
            with self.assertRaisesRegex(ValueError, "object-dtype"):
                preflight_streamable_g2_npz(object_source)

            missing_source = root / "missing.npz"
            arrays = _tiny_g2_arrays()
            del arrays["data_time"]
            _write_packet(missing_source, arrays)
            with self.assertRaisesRegex(ValueError, "missing required"):
                preflight_streamable_g2_npz(missing_source)


if __name__ == "__main__":
    unittest.main()
