"""Receipt-bound streaming conversion for the unavailable production G2 NPZ.

The converter is intentionally format-only evidence.  It can be tested with a
generated mini-packet, but it must not be described as publication-G2
validation until the literal receipt-bound input has been converted.
"""

from __future__ import annotations

from dataclasses import dataclass
import fcntl
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
from typing import Any, Iterator, Mapping
import zipfile

import numpy as np

from .g2_adapter import (
    G2_ESTIMATOR_FINGERPRINT,
    G2_SCHEMA_VERSION,
    REQUIRED_G2_KEYS,
)
from .utils import canonical_json, file_sha256, fingerprint, git_state

FORMAT_VERSION = "g2-npy-memmap-v1"
MANIFEST_NAME = "manifest.json"
COMPLETE_NAME = "COMPLETE.json"
PROGRESS_NAME = "progress.json"
DEFAULT_CHUNK_BYTES = 8 << 20

ROW_FAMILY_KEYS: Mapping[str, tuple[str, ...]] = {
    "signal": (
        "part_reco",
        "part_gen",
        "reco_scalars",
        "truth_scalars",
        "reco_muon",
        "reco_vertex",
        "reco_view",
        "reco_time",
        "pass_reco",
        "pass_truth",
        "w_reco",
        "w_truth",
    ),
    "data": (
        "measured_pc",
        "measured_scalars",
        "data_muon",
        "data_vertex",
        "data_view",
        "data_time",
    ),
    "background": (
        "bkg_part_reco",
        "bkg_reco_scalars",
        "bkg_muon",
        "bkg_vertex",
        "bkg_view",
        "bkg_time",
        "w_bkg",
        "bkg_indices",
    ),
}

ARRAY_UNITS: Mapping[str, Any] = {
    "part_reco": ["MeV", "mm", "mm"],
    "part_gen": ["MeV", "MeV", "MeV", "MeV", "PDG"],
    "reco_scalars": ["GeV", "GeV", "GeV", "GeV"],
    "truth_scalars": ["GeV", "GeV", "GeV", "GeV"],
    "reco_muon": [
        "MeV",
        "MeV",
        "MeV",
        "MeV",
        "rad",
        "source_q_over_p_unit_unverified",
        "boolean",
    ],
    "reco_vertex": ["mm", "mm", "mm"],
    "reco_view": "categorical",
    "reco_time": "source_time_unit_unverified",
    "pass_reco": "boolean",
    "pass_truth": "boolean",
    "w_reco": "dimensionless",
    "w_truth": "dimensionless",
    "measured_pc": ["MeV", "mm", "mm"],
    "measured_scalars": ["GeV", "GeV", "GeV", "GeV"],
    "data_muon": [
        "MeV",
        "MeV",
        "MeV",
        "MeV",
        "rad",
        "source_q_over_p_unit_unverified",
        "boolean",
    ],
    "data_vertex": ["mm", "mm", "mm"],
    "data_view": "categorical",
    "data_time": "source_time_unit_unverified",
    "bkg_part_reco": ["MeV", "mm", "mm"],
    "bkg_reco_scalars": ["GeV", "GeV", "GeV", "GeV"],
    "bkg_muon": [
        "MeV",
        "MeV",
        "MeV",
        "MeV",
        "rad",
        "source_q_over_p_unit_unverified",
        "boolean",
    ],
    "bkg_vertex": ["mm", "mm", "mm"],
    "bkg_view": "categorical",
    "bkg_time": "source_time_unit_unverified",
    "w_bkg": "dimensionless",
    "bkg_indices": "integer_row_index",
    "sig_identity_hash": "sha256_text",
    "data_identity_hash": "sha256_text",
    "bkg_identity_hash": "sha256_text",
    "estimator_fingerprint": "text",
    "data_pot": "protons_on_target",
    "petSchemaVersion": "text",
    "hasFullEventSchema": "boolean_marker",
    "fullPhaseSpace": "boolean_marker",
}

KEY_TO_FAMILY = {
    key: family for family, keys in ROW_FAMILY_KEYS.items() for key in keys
}


def _payload_nbytes(shape: tuple[int, ...], dtype: np.dtype) -> int:
    elements = 1
    for dimension in shape:
        if dimension < 0:
            raise ValueError("NPY shapes must be nonnegative")
        elements *= dimension
    return int(elements * dtype.itemsize)


def _write_json_fsync(path: Path, payload: Mapping[str, Any]) -> None:
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    with temporary.open("w", encoding="utf-8") as handle:
        handle.write(canonical_json(payload) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def _write_progress(path: Path, progress: Mapping[str, Any]) -> dict[str, Any]:
    payload = dict(progress)
    payload.pop("fingerprint", None)
    payload["fingerprint"] = fingerprint(payload)
    _write_json_fsync(path, payload)
    return payload


def _validated_progress(
    progress: Mapping[str, Any],
    *,
    source_sha256: str,
    source_size_bytes: int,
) -> dict[str, Any]:
    payload = dict(progress)
    recorded_fingerprint = payload.pop("fingerprint", None)
    if recorded_fingerprint != fingerprint(payload):
        raise ValueError("partial conversion progress journal fingerprint mismatch")
    if (
        payload.get("format_version") != FORMAT_VERSION
        or payload.get("status") != "partial"
        or payload.get("input", {}).get("sha256") != source_sha256
        or int(payload.get("input", {}).get("size_bytes", -1))
        != source_size_bytes
        or not isinstance(payload.get("arrays"), dict)
    ):
        raise ValueError("partial conversion progress journal is stale or malformed")
    payload["fingerprint"] = recorded_fingerprint
    return payload


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _read_member_header(handle) -> tuple[tuple[int, ...], bool, np.dtype]:
    version = np.lib.format.read_magic(handle)
    if version == (1, 0):
        shape, fortran_order, dtype = np.lib.format.read_array_header_1_0(handle)
    elif version in {(2, 0), (3, 0)}:
        shape, fortran_order, dtype = np.lib.format.read_array_header_2_0(handle)
    else:
        raise ValueError(f"unsupported NPY member version: {version}")
    dtype = np.dtype(dtype)
    if dtype.hasobject:
        raise ValueError("object-dtype NPY members are forbidden")
    return tuple(int(value) for value in shape), bool(fortran_order), dtype


def _header_from_archive(archive: zipfile.ZipFile, key: str) -> dict[str, Any]:
    member = f"{key}.npy"
    if archive.namelist().count(member) != 1:
        raise ValueError(f"G2 member must occur exactly once: {member}")
    with archive.open(member, "r") as handle:
        shape, fortran_order, dtype = _read_member_header(handle)
    return {
        "shape": list(shape),
        "fortran_order": fortran_order,
        "dtype": dtype.str,
        "uncompressed_nbytes": _payload_nbytes(shape, dtype),
    }


def _read_small_scalar(archive: zipfile.ZipFile, key: str) -> Any:
    member = f"{key}.npy"
    info = archive.getinfo(member)
    if info.file_size > (1 << 20):
        raise ValueError(f"metadata marker is unexpectedly large: {key}")
    with archive.open(member, "r") as handle:
        payload = handle.read()
    value = np.load(io.BytesIO(payload), allow_pickle=False)
    if np.asarray(value).shape != ():
        raise ValueError(f"metadata marker must be scalar: {key}")
    return np.asarray(value).item()


def preflight_streamable_g2_npz(path: str | Path) -> dict[str, Any]:
    source = Path(path).expanduser().resolve()
    if not source.is_file() or source.stat().st_size == 0:
        raise FileNotFoundError(f"G2 NPZ is absent: {source}")
    try:
        with zipfile.ZipFile(source, "r") as archive:
            members = {
                name[:-4] for name in archive.namelist() if name.endswith(".npy")
            }
            missing = sorted(REQUIRED_G2_KEYS - members)
            if missing:
                raise ValueError(f"G2 manifest missing required arrays: {missing}")
            headers = {
                key: _header_from_archive(archive, key)
                for key in sorted(REQUIRED_G2_KEYS)
            }
            markers = {
                "petSchemaVersion": str(_read_small_scalar(archive, "petSchemaVersion")),
                "estimator_fingerprint": str(
                    _read_small_scalar(archive, "estimator_fingerprint")
                ),
                "hasFullEventSchema": int(
                    _read_small_scalar(archive, "hasFullEventSchema")
                ),
                "fullPhaseSpace": int(_read_small_scalar(archive, "fullPhaseSpace")),
            }
    except zipfile.BadZipFile as exc:
        raise ValueError("G2 input is not a valid NPZ archive") from exc
    expected_markers = {
        "petSchemaVersion": G2_SCHEMA_VERSION,
        "estimator_fingerprint": G2_ESTIMATOR_FINGERPRINT,
        "hasFullEventSchema": 1,
        "fullPhaseSpace": 1,
    }
    if markers != expected_markers:
        raise ValueError(
            f"G2 schema/fingerprint markers disagree: {markers} != {expected_markers}"
        )
    return {
        "path": str(source),
        "size_bytes": source.stat().st_size,
        "markers": markers,
        "headers": headers,
    }


def _stream_member(
    archive: zipfile.ZipFile,
    key: str,
    output: Path,
    *,
    chunk_bytes: int,
) -> dict[str, Any]:
    if chunk_bytes < 4096:
        raise ValueError("chunk_bytes must be at least 4096")
    member = f"{key}.npy"
    temporary = output.with_name(f".{output.name}.partial")
    if temporary.exists():
        temporary.unlink()
    payload_digest = hashlib.sha256()
    with archive.open(member, "r") as source, temporary.open("wb") as target:
        shape, fortran_order, dtype = _read_member_header(source)
        np.lib.format.write_array_header_2_0(
            target,
            {
                "descr": np.lib.format.dtype_to_descr(dtype),
                "fortran_order": fortran_order,
                "shape": shape,
            },
        )
        remaining = _payload_nbytes(shape, dtype)
        while remaining:
            payload = source.read(min(chunk_bytes, remaining))
            if not payload:
                raise ValueError(f"truncated NPY payload for {key}")
            target.write(payload)
            payload_digest.update(payload)
            remaining -= len(payload)
        if source.read(1):
            raise ValueError(f"NPY member contains trailing data: {key}")
        target.flush()
        os.fsync(target.fileno())
    os.replace(temporary, output)
    array = np.load(output, mmap_mode="r", allow_pickle=False)
    record = {
        "name": key,
        "path": output.name,
        "dtype": array.dtype.str,
        "shape": list(array.shape),
        # Preserve the header bit exactly.  np.isfortran() is false for
        # one-dimensional arrays because they are both C- and F-contiguous.
        "fortran_order": fortran_order,
        "row_family": KEY_TO_FAMILY.get(key, "metadata"),
        "units": ARRAY_UNITS[key],
        "bytes": output.stat().st_size,
        "sha256": file_sha256(output, chunk_bytes=chunk_bytes),
        "payload_sha256": payload_digest.hexdigest(),
    }
    del array
    return record


def _payload_hash_from_npy_stream(handle, *, chunk_bytes: int) -> tuple[dict[str, Any], str]:
    shape, fortran_order, dtype = _read_member_header(handle)
    remaining = _payload_nbytes(shape, dtype)
    digest = hashlib.sha256()
    while remaining:
        payload = handle.read(min(chunk_bytes, remaining))
        if not payload:
            raise ValueError("truncated NPY payload during resume verification")
        digest.update(payload)
        remaining -= len(payload)
    if handle.read(1):
        raise ValueError("NPY payload has trailing bytes during resume verification")
    return {
        "dtype": dtype.str,
        "shape": list(shape),
        "fortran_order": fortran_order,
    }, digest.hexdigest()


def _completed_member_is_valid(
    archive: zipfile.ZipFile,
    key: str,
    output: Path,
    record: Mapping[str, Any],
    *,
    chunk_bytes: int,
) -> bool:
    if not output.is_file():
        return False
    if (
        record.get("name") != key
        or record.get("path") != output.name
        or record.get("row_family") != KEY_TO_FAMILY.get(key, "metadata")
        or record.get("units") != ARRAY_UNITS[key]
        or int(record.get("bytes", -1)) != output.stat().st_size
    ):
        return False
    try:
        if file_sha256(output, chunk_bytes=chunk_bytes) != record.get("sha256"):
            return False
        with output.open("rb") as handle:
            output_header, output_payload = _payload_hash_from_npy_stream(
                handle, chunk_bytes=chunk_bytes
            )
        with archive.open(f"{key}.npy", "r") as handle:
            source_header, source_payload = _payload_hash_from_npy_stream(
                handle, chunk_bytes=chunk_bytes
            )
    except (OSError, ValueError, KeyError):
        return False
    expected_header = {
        name: record.get(name) for name in ("dtype", "shape", "fortran_order")
    }
    return (
        output_header == expected_header
        and source_header == expected_header
        and output_payload == source_payload == record.get("payload_sha256")
    )


def _streaming_array_hash(
    arrays: tuple[np.ndarray, ...], *, chunk_bytes: int = DEFAULT_CHUNK_BYTES
) -> str:
    digest = hashlib.sha256()
    for value in arrays:
        array = np.asarray(value)
        if not array.flags.c_contiguous:
            raise ValueError("legacy inventory hash requires C-contiguous arrays")
        # Match g2_adapter._legacy_order_hash byte-for-byte.  The frozen G2
        # producer used str(dtype), not NumPy's endian-explicit dtype.str.
        digest.update(str(array.dtype).encode())
        digest.update(repr(array.shape).encode())
        raw = array.view(np.uint8).reshape(-1)
        for start in range(0, raw.size, chunk_bytes):
            digest.update(memoryview(raw[start : start + chunk_bytes]))
    return digest.hexdigest()


def _row_counts(arrays: Mapping[str, np.ndarray]) -> dict[str, int]:
    result: dict[str, int] = {}
    for family, keys in ROW_FAMILY_KEYS.items():
        counts = {int(arrays[key].shape[0]) for key in keys}
        if len(counts) != 1:
            raise ValueError(f"{family} array row counts disagree: {sorted(counts)}")
        result[family] = counts.pop()
    return result


def _identity_hashes(
    arrays: Mapping[str, np.ndarray], *, chunk_bytes: int
) -> dict[str, str]:
    return {
        "sig_identity_hash": _streaming_array_hash(
            (arrays["w_truth"], arrays["pass_truth"]), chunk_bytes=chunk_bytes
        ),
        "data_identity_hash": _streaming_array_hash(
            (arrays["measured_pc"],), chunk_bytes=chunk_bytes
        ),
        "bkg_identity_hash": _streaming_array_hash(
            (arrays["w_bkg"], arrays["bkg_indices"]), chunk_bytes=chunk_bytes
        ),
    }


def _scalar_text(array: np.ndarray) -> str:
    return str(np.asarray(array).item())


@dataclass
class G2MemmapInventory:
    root: Path
    manifest: Mapping[str, Any]
    arrays: Mapping[str, np.ndarray]

    @property
    def row_counts(self) -> Mapping[str, int]:
        return self.manifest["row_counts"]

    def window(self, family: str, start: int, stop: int) -> dict[str, np.ndarray]:
        if family not in ROW_FAMILY_KEYS:
            raise ValueError(f"unknown row family: {family}")
        count = int(self.row_counts[family])
        if not (0 <= start <= stop <= count):
            raise ValueError(f"invalid {family} window [{start},{stop}) for {count} rows")
        return {key: self.arrays[key][start:stop] for key in ROW_FAMILY_KEYS[family]}

    def iter_windows(
        self, family: str, chunk_rows: int
    ) -> Iterator[tuple[int, int, dict[str, np.ndarray]]]:
        if chunk_rows < 1:
            raise ValueError("chunk_rows must be positive")
        count = int(self.row_counts[family])
        for start in range(0, count, chunk_rows):
            stop = min(count, start + chunk_rows)
            yield start, stop, self.window(family, start, stop)

    def close(self) -> None:
        for value in self.arrays.values():
            mmap = getattr(value, "_mmap", None)
            if mmap is not None:
                mmap.close()


def open_g2_memmap_inventory(
    directory: str | Path,
    *,
    source_npz: str | Path,
    chunk_bytes: int = DEFAULT_CHUNK_BYTES,
) -> G2MemmapInventory:
    root = Path(directory).expanduser().resolve()
    manifest_path = root / MANIFEST_NAME
    complete_path = root / COMPLETE_NAME
    if not root.is_dir() or not manifest_path.is_file() or not complete_path.is_file():
        raise FileNotFoundError("G2 memmap inventory is partial or lacks completion markers")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    complete = json.loads(complete_path.read_text(encoding="utf-8"))
    if manifest.get("format_version") != FORMAT_VERSION:
        raise ValueError("wrong G2 memmap format version")
    if complete.get("format_version") != FORMAT_VERSION:
        raise ValueError("wrong G2 completion-marker format version")
    if complete.get("manifest_sha256") != file_sha256(manifest_path):
        raise ValueError("G2 completion marker does not bind the manifest")
    if complete.get("input_sha256") != manifest.get("input", {}).get("sha256"):
        raise ValueError("G2 completion marker does not bind the input receipt")
    manifest_for_fingerprint = dict(manifest)
    recorded_fingerprint = manifest_for_fingerprint.pop("fingerprint", None)
    if recorded_fingerprint != fingerprint(manifest_for_fingerprint):
        raise ValueError("G2 manifest fingerprint mismatch")
    if (
        manifest.get("status") != "complete_code_contract_only"
        or manifest.get("evidence_class") != "code-contract"
        or manifest.get("g2_validation_claim") is not False
        or manifest.get("publication_promotion_permitted") is not False
    ):
        raise ValueError("G2 manifest carries an invalid evidence status")
    source = Path(source_npz).expanduser().resolve()
    if (
        not source.is_file()
        or source.stat().st_size != int(manifest["input"]["size_bytes"])
        or file_sha256(source, chunk_bytes=chunk_bytes)
        != manifest["input"]["sha256"]
    ):
        raise ValueError("G2 source is stale, absent, or disagrees with the manifest")
    arrays: dict[str, np.ndarray] = {}
    records = manifest.get("arrays", {})
    if set(records) != set(REQUIRED_G2_KEYS):
        raise ValueError("G2 manifest array inventory is incomplete")
    try:
        for key in sorted(REQUIRED_G2_KEYS):
            record = records[key]
            if (
                record.get("name") != key
                or record.get("path") != f"{key}.npy"
                or record.get("row_family") != KEY_TO_FAMILY.get(key, "metadata")
                or record.get("units") != ARRAY_UNITS[key]
            ):
                raise ValueError(f"G2 manifest record semantics mismatch for {key}")
            path = root / record["path"]
            if not path.is_file():
                raise FileNotFoundError(f"G2 memmap array is absent: {key}")
            if file_sha256(path, chunk_bytes=chunk_bytes) != record["sha256"]:
                raise ValueError(f"G2 memmap array content hash mismatch: {key}")
            value = np.load(path, mmap_mode="r", allow_pickle=False)
            if not isinstance(value, np.memmap):
                raise ValueError(f"G2 array is not memmap-backed: {key}")
            if value.flags.writeable:
                raise ValueError(f"G2 memmap unexpectedly opened writable: {key}")
            with path.open("rb") as handle:
                header_shape, header_fortran, header_dtype = _read_member_header(
                    handle
                )
            actual = {
                "dtype": header_dtype.str,
                "shape": list(header_shape),
                "fortran_order": header_fortran,
            }
            expected = {
                name: record[name] for name in ("dtype", "shape", "fortran_order")
            }
            if actual != expected:
                raise ValueError(f"G2 memmap schema mismatch for {key}")
            arrays[key] = value
        counts = _row_counts(arrays)
        if counts != {key: int(value) for key, value in manifest["row_counts"].items()}:
            raise ValueError("G2 row-family counts disagree with the manifest")
        identities = _identity_hashes(arrays, chunk_bytes=chunk_bytes)
        if identities != manifest["identity_hashes"]:
            raise ValueError("G2 ordered-inventory hashes disagree with the manifest")
        for key, computed in identities.items():
            if _scalar_text(arrays[key]) != computed:
                raise ValueError(f"G2 embedded ordered-inventory hash disagrees: {key}")
    except Exception:
        for value in arrays.values():
            mmap = getattr(value, "_mmap", None)
            if mmap is not None:
                mmap.close()
        raise
    return G2MemmapInventory(root=root, manifest=manifest, arrays=arrays)


def convert_g2_npz_to_memmap(
    source_npz: str | Path,
    output_directory: str | Path,
    *,
    expected_sha256: str,
    expected_size_bytes: int,
    timestamp_utc: str,
    chunk_bytes: int = DEFAULT_CHUNK_BYTES,
    resume: bool = True,
) -> Mapping[str, Any]:
    """Stream a receipt-bound NPZ into an atomically published memmap inventory."""
    source = Path(source_npz).expanduser().resolve()
    output = Path(output_directory).expanduser().resolve()
    if not timestamp_utc:
        raise ValueError("timestamp_utc must be injected explicitly")
    if chunk_bytes < 4096:
        raise ValueError("chunk_bytes must be at least 4096")
    if not source.is_file():
        raise FileNotFoundError(f"G2 NPZ is absent: {source}")
    actual_size = source.stat().st_size
    actual_sha = file_sha256(source, chunk_bytes=chunk_bytes)
    if actual_size != int(expected_size_bytes) or actual_sha != expected_sha256:
        raise ValueError("G2 input size/SHA-256 disagrees with the bound receipt")
    if output.exists():
        inventory = open_g2_memmap_inventory(
            output, source_npz=source, chunk_bytes=chunk_bytes
        )
        try:
            return inventory.manifest
        finally:
            inventory.close()
    preflight = preflight_streamable_g2_npz(source)
    stage = output.with_name(f".{output.name}.partial")
    lock = output.with_name(f".{output.name}.lock")
    output.parent.mkdir(parents=True, exist_ok=True)
    lock_fd = os.open(lock, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError(f"G2 conversion is already active: {lock}") from exc
        os.ftruncate(lock_fd, 0)
        os.write(
            lock_fd,
            (
                f"pid={os.getpid()} host={os.uname().nodename} "
                f"source_sha256={actual_sha}\n"
            ).encode("ascii"),
        )
        os.fsync(lock_fd)
    except Exception:
        os.close(lock_fd)
        raise
    try:
        # Close the check-before-lock race with a converter that published
        # between the initial output test and our lock acquisition.
        if output.exists():
            inventory = open_g2_memmap_inventory(
                output,
                source_npz=source,
                chunk_bytes=chunk_bytes,
            )
            try:
                return inventory.manifest
            finally:
                inventory.close()
        if stage.exists() and not resume:
            raise FileExistsError(f"partial G2 conversion exists: {stage}")
        stage.mkdir(exist_ok=True)
        progress_path = stage / PROGRESS_NAME
        if progress_path.is_file():
            progress = _validated_progress(
                json.loads(progress_path.read_text(encoding="utf-8")),
                source_sha256=actual_sha,
                source_size_bytes=actual_size,
            )
        else:
            progress = {
                "format_version": FORMAT_VERSION,
                "status": "partial",
                "timestamp_utc": timestamp_utc,
                "input": {
                    "path": str(source),
                    "size_bytes": actual_size,
                    "sha256": actual_sha,
                },
                "arrays": {},
            }
            progress = _write_progress(progress_path, progress)
        with zipfile.ZipFile(source, "r") as archive:
            for key in sorted(REQUIRED_G2_KEYS):
                output_path = stage / f"{key}.npy"
                prior = progress["arrays"].get(key)
                if prior and _completed_member_is_valid(
                    archive,
                    key,
                    output_path,
                    prior,
                    chunk_bytes=chunk_bytes,
                ):
                    continue
                if output_path.exists():
                    output_path.unlink()
                record = _stream_member(
                    archive, key, output_path, chunk_bytes=chunk_bytes
                )
                progress["arrays"][key] = record
                progress = _write_progress(progress_path, progress)
        arrays = {
            key: np.load(stage / f"{key}.npy", mmap_mode="r", allow_pickle=False)
            for key in sorted(REQUIRED_G2_KEYS)
        }
        try:
            counts = _row_counts(arrays)
            identities = _identity_hashes(arrays, chunk_bytes=chunk_bytes)
            for key, computed in identities.items():
                if _scalar_text(arrays[key]) != computed:
                    raise ValueError(f"G2 embedded ordered-inventory hash mismatch: {key}")
            markers = {
                "petSchemaVersion": _scalar_text(arrays["petSchemaVersion"]),
                "estimator_fingerprint": _scalar_text(
                    arrays["estimator_fingerprint"]
                ),
                "hasFullEventSchema": int(
                    np.asarray(arrays["hasFullEventSchema"]).item()
                ),
                "fullPhaseSpace": int(np.asarray(arrays["fullPhaseSpace"]).item()),
            }
            if markers != preflight["markers"]:
                raise ValueError("converted G2 markers disagree with preflight")
        finally:
            for value in arrays.values():
                mmap = getattr(value, "_mmap", None)
                if mmap is not None:
                    mmap.close()
        if (
            source.stat().st_size != actual_size
            or file_sha256(source, chunk_bytes=chunk_bytes) != actual_sha
        ):
            raise ValueError("G2 source changed during conversion")
        manifest = {
            "format_version": FORMAT_VERSION,
            "status": "complete_code_contract_only",
            "evidence_class": "code-contract",
            "g2_validation_claim": False,
            "publication_promotion_permitted": False,
            "timestamp_utc": timestamp_utc,
            "input": {
                "path": str(source),
                "size_bytes": actual_size,
                "sha256": actual_sha,
            },
            "schema_markers": preflight["markers"],
            "arrays": progress["arrays"],
            "row_counts": counts,
            "identity_hashes": identities,
            "chunk_bytes": chunk_bytes,
            "source_code": {
                "path": str(Path(__file__).resolve()),
                "sha256": file_sha256(Path(__file__).resolve()),
                "git": git_state(Path(__file__).resolve().parent),
            },
        }
        manifest["fingerprint"] = fingerprint(manifest)
        manifest_path = stage / MANIFEST_NAME
        _write_json_fsync(manifest_path, manifest)
        complete = {
            "format_version": FORMAT_VERSION,
            "manifest_sha256": file_sha256(manifest_path),
            "input_sha256": actual_sha,
            "timestamp_utc": timestamp_utc,
        }
        _write_json_fsync(stage / COMPLETE_NAME, complete)
        progress_path.unlink()
        for key in REQUIRED_G2_KEYS:
            os.chmod(stage / f"{key}.npy", 0o444)
        _fsync_directory(stage)
        verified_stage = open_g2_memmap_inventory(
            stage, source_npz=source, chunk_bytes=chunk_bytes
        )
        verified_stage.close()
        if (
            source.stat().st_size != actual_size
            or file_sha256(source, chunk_bytes=chunk_bytes) != actual_sha
        ):
            raise ValueError("G2 source changed before atomic publication")
        if output.exists():
            raise FileExistsError(f"refusing to replace G2 output: {output}")
        os.replace(stage, output)
        _fsync_directory(output.parent)
        try:
            verified = open_g2_memmap_inventory(
                output, source_npz=source, chunk_bytes=chunk_bytes
            )
            try:
                return verified.manifest
            finally:
                verified.close()
        except Exception:
            # Never leave a source-raced or otherwise unverifiable directory at
            # the canonical completed path.
            if output.exists() and not stage.exists():
                os.replace(output, stage)
                _fsync_directory(output.parent)
            raise
    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        os.close(lock_fd)


def remove_partial_conversion(output_directory: str | Path) -> None:
    """Remove only this converter's explicit partial sibling.

    This helper is intentionally narrow and is not called automatically after
    failure because a verified partial directory is resumable evidence.
    """
    output = Path(output_directory).expanduser().resolve()
    stage = output.with_name(f".{output.name}.partial")
    if stage.is_dir():
        shutil.rmtree(stage)
