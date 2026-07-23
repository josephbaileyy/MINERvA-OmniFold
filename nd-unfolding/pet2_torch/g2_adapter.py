"""Fail-closed adapter seam for the absent publication G2 and Gate-2 payloads."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any
import zipfile

import numpy as np

from .contracts import CanonicalDataset, MeasuredInventory, SignalInventory, TokenBatch
from .features import FeatureCapabilities, TYPE_GENERIC
from .utils import file_sha256

G2_SCHEMA_VERSION = "g2-fullevent-v1"
G2_ESTIMATOR_FINGERPRINT = "pet-fullevent-fps-v1"
REQUIRED_G2_KEYS = {
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
    "measured_pc",
    "measured_scalars",
    "data_muon",
    "data_vertex",
    "data_view",
    "data_time",
    "bkg_part_reco",
    "bkg_reco_scalars",
    "bkg_muon",
    "bkg_vertex",
    "bkg_view",
    "bkg_time",
    "w_bkg",
    "bkg_indices",
    "sig_identity_hash",
    "data_identity_hash",
    "bkg_identity_hash",
    "estimator_fingerprint",
    "data_pot",
    "petSchemaVersion",
    "hasFullEventSchema",
    "fullPhaseSpace",
}
G2_GLOBAL_NAMES = (
    "mu_pt",
    "mu_pparallel",
    "mu_energy",
    "mu_cos_phi",
    "mu_sin_phi",
    "eavail",
    "q3",
    "mu_charge",
    "minos_ok",
    "vertex_x",
    "vertex_y",
    "vertex_z",
)
MAX_G2_MINI_PACKET_BYTES = 1 << 30
MAX_G2_MINI_PACKET_ROWS = 1_000_000


def _require_file(path: str | Path, label: str) -> Path:
    resolved = Path(path).expanduser().resolve()
    if not resolved.is_file() or resolved.stat().st_size == 0:
        raise FileNotFoundError(
            f"{label} is absent: {resolved}. The publication G2/Gate-2 payload is "
            "not bundled; fail closed and do not claim G2 validation."
        )
    return resolved


def _scalar(value: Any) -> Any:
    return np.asarray(value).item()


def _legacy_order_hash(*arrays: np.ndarray) -> str:
    """Exact hash convention used by the frozen G2 producer."""
    digest = hashlib.sha256()
    for value in arrays:
        array = np.ascontiguousarray(np.asarray(value))
        digest.update(str(array.dtype).encode())
        digest.update(repr(array.shape).encode())
        digest.update(array.tobytes())
    return digest.hexdigest()


def _npz_member_header(archive: zipfile.ZipFile, key: str) -> dict[str, Any]:
    """Read only a compressed member's NPY header, never its array payload."""
    member = f"{key}.npy"
    if member not in archive.namelist():
        raise ValueError(f"G2 manifest missing required array: {key}")
    with archive.open(member) as handle:
        version = np.lib.format.read_magic(handle)
        if version == (1, 0):
            shape, fortran, dtype = np.lib.format.read_array_header_1_0(handle)
        else:
            shape, fortran, dtype = np.lib.format.read_array_header_2_0(handle)
    return {
        "shape": tuple(int(value) for value in shape),
        "fortran_order": bool(fortran),
        "dtype": str(dtype),
    }


def preflight_g2_mini_packet(path: str | Path) -> dict[str, Any]:
    """Reject production-sized compressed G2 before NumPy materializes arrays.

    Compressed NPZ is not a streaming format for NumPy.  This adapter is
    intentionally limited to bounded audit/fixture packets; the 40--50M-row
    publication archive must first be converted, out of band, to a reviewed
    streamable inventory.
    """
    packet = _require_file(path, "G2 mini-packet NPZ")
    if packet.stat().st_size > MAX_G2_MINI_PACKET_BYTES:
        raise ValueError(
            "compressed G2 exceeds the mini-packet byte bound; refusing before "
            "np.load because NPZ cannot stream 40--50M-row production arrays"
        )
    try:
        with zipfile.ZipFile(packet) as archive:
            members = {name[:-4] for name in archive.namelist() if name.endswith(".npy")}
            missing = sorted(REQUIRED_G2_KEYS - members)
            if missing:
                raise ValueError(f"G2 manifest missing required arrays: {missing}")
            headers = {
                key: _npz_member_header(archive, key)
                for key in (
                    "part_reco",
                    "part_gen",
                    "measured_pc",
                    "bkg_part_reco",
                )
            }
    except zipfile.BadZipFile as exc:
        raise ValueError("G2 mini-packet is not a valid NPZ archive") from exc
    largest = max(
        (header["shape"][0] if header["shape"] else 1)
        for header in headers.values()
    )
    if largest > MAX_G2_MINI_PACKET_ROWS:
        raise ValueError(
            "compressed G2 exceeds the mini-packet row bound; supply a bounded "
            "packet or a reviewed .npy/memmap inventory"
        )
    return {
        "mode": "compressed_npz_mini_packet_only",
        "bytes": packet.stat().st_size,
        "max_bytes": MAX_G2_MINI_PACKET_BYTES,
        "max_rows": MAX_G2_MINI_PACKET_ROWS,
        "headers": headers,
    }


def _g2_globals(scalars, muon, vertex, valid):
    scalars = np.asarray(scalars, dtype=np.float32)
    muon = np.asarray(muon, dtype=np.float32)
    vertex = np.asarray(vertex, dtype=np.float32)
    if scalars.shape[1] < 4 or muon.shape[1] < 7 or vertex.shape[1] < 3:
        raise ValueError("G2 richer-global arrays have insufficient columns")
    muon_present = np.asarray(valid, bool) & (
        np.any(muon[:, :4] != 0.0, axis=1)
    )
    muon_energy = np.where(muon_present, muon[:, 3] / 1000.0, 0.0)
    muon_cos_phi = np.where(muon_present, np.cos(muon[:, 4]), 0.0)
    muon_sin_phi = np.where(muon_present, np.sin(muon[:, 4]), 0.0)
    output = np.column_stack(
        (
            scalars[:, 0],  # G2 scalar branches are already GeV
            scalars[:, 1],
            muon_energy,
            muon_cos_phi,
            muon_sin_phi,
            scalars[:, 2],
            scalars[:, 3],
            np.sign(muon[:, 5]),
            muon[:, 6],
            vertex[:, 0] / 1000.0,
            vertex[:, 1] / 1000.0,
            vertex[:, 2] / 1000.0,
        )
    ).astype(np.float32)
    output[~valid] = 0.0
    if not np.all(np.isfinite(output)):
        raise ValueError("G2 globals contain nonfinite values after sentinel masking")
    return output


def _reco_batch(cloud, scalars, muon, vertex, view, valid_rows, provenance):
    cloud = np.asarray(cloud, dtype=np.float32)
    view = np.asarray(view, dtype=np.int64)
    if cloud.ndim != 3 or cloud.shape[2] != 3 or view.shape != cloud.shape[:2]:
        raise ValueError("G2 reco cloud/view schema mismatch")
    # The explicit mask comes from the categorical detector-view array, never
    # from energy or another continuous physics feature.
    token_mask = (view != 0) & np.asarray(valid_rows, bool)[:, None]
    continuous = cloud / 1000.0  # G2 cloud E/position/z are MeV/mm
    type_id = np.where(token_mask, TYPE_GENERIC, 0).astype(np.int64)
    view = np.where(token_mask, view, 0).astype(np.int64)
    continuous[~token_mask] = 0.0
    coords = continuous[:, :, 1:3].copy()
    muon = np.asarray(muon, dtype=np.float32)
    muon_present = np.asarray(valid_rows, bool)
    muon_cont = np.zeros((len(muon), 3), dtype=np.float32)
    muon_cont[:, 0] = muon[:, 3] / 1000.0
    muon_cont[:, 1] = np.hypot(muon[:, 0], muon[:, 1]) / 1000.0
    muon_cont[:, 2] = muon[:, 2] / 1000.0
    muon_cont[~muon_present] = 0.0
    return TokenBatch(
        continuous=continuous,
        coords=coords,
        token_mask=token_mask,
        type_id=type_id,
        view_id=view,
        globals=_g2_globals(scalars, muon, vertex, muon_present),
        row_index=np.arange(cloud.shape[0], dtype=np.int64),
        global_names=G2_GLOBAL_NAMES,
        provenance=provenance,
        muon_continuous=muon_cont,
        muon_coords=np.zeros((cloud.shape[0], 2), dtype=np.float32),
        muon_present=muon_present,
    ).validated(max_view=4)


def _truth_batch(part_gen, truth_scalars):
    part_gen = np.asarray(part_gen, dtype=np.float32)
    if part_gen.ndim != 3 or part_gen.shape[2] < 5:
        raise ValueError("G2 truth cloud must be (N,P,>=5)")
    pdg = part_gen[:, :, 4].astype(np.int64)
    mask = pdg != 0
    energy = part_gen[:, :, 0] / 1000.0
    px = part_gen[:, :, 1] / 1000.0
    py = part_gen[:, :, 2] / 1000.0
    pz = part_gen[:, :, 3] / 1000.0
    continuous = np.stack((energy, np.hypot(px, py), pz), axis=-1).astype(np.float32)
    theta = np.arctan2(np.hypot(px, py), pz)
    phi = np.arctan2(py, px)
    # Phi is periodic.  Embedding it on the unit circle prevents an artificial
    # KNN discontinuity for otherwise adjacent objects across +/-pi.
    coords = np.stack((theta, np.cos(phi), np.sin(phi)), axis=-1).astype(np.float32)
    continuous[~mask] = 0.0
    coords[~mask] = 0.0
    # Raw truth PDG is generator-only.  C maps all valid tokens to generic;
    # D/E remain unavailable for G2 because reco object types do not exist.
    type_id = np.where(mask, TYPE_GENERIC, 0).astype(np.int64)
    zeros_muon = np.zeros((part_gen.shape[0], 7), dtype=np.float32)
    zeros_vertex = np.zeros((part_gen.shape[0], 3), dtype=np.float32)
    valid = np.ones(part_gen.shape[0], dtype=bool)
    return TokenBatch(
        continuous=continuous,
        coords=coords,
        token_mask=mask,
        type_id=type_id,
        view_id=np.zeros(mask.shape, dtype=np.int64),
        globals=_g2_globals(truth_scalars, zeros_muon, zeros_vertex, valid),
        row_index=np.arange(part_gen.shape[0], dtype=np.int64),
        global_names=G2_GLOBAL_NAMES,
        provenance="g2_truth_generator_only",
    ).validated()


def load_publication_g2(
    g2_path: str | Path,
    target_path: str | Path,
    target_receipt_path: str | Path,
    *,
    target_key: str = "measured_weights",
) -> tuple[CanonicalDataset, FeatureCapabilities]:
    """Load a bounded G2 mini-packet when every immutable payload is valid.

    This function deliberately refuses the production compressed NPZ.  It is a
    schema/contract seam, not an advertised eager full-G2 loader.
    """
    g2_file = _require_file(g2_path, "publication G2 NPZ")
    target_file = _require_file(target_path, "Gate-2 Stay-Positive target payload")
    receipt_file = _require_file(target_receipt_path, "Gate-2 target receipt")
    mini_packet = preflight_g2_mini_packet(g2_file)
    receipt = json.loads(receipt_file.read_text(encoding="utf-8"))
    expected_g2_sha = receipt.get("input_preflight", {}).get("sha256")
    actual_g2_sha = file_sha256(g2_file)
    if expected_g2_sha and expected_g2_sha != actual_g2_sha:
        raise ValueError("publication G2 SHA-256 disagrees with the Gate-2 receipt")
    expected_target_sha = (
        receipt.get("step1_feed", {}).get("weights", {}).get("sha256")
    )
    actual_target_sha = file_sha256(target_file)
    if expected_target_sha and expected_target_sha != actual_target_sha:
        raise ValueError("Gate-2 target SHA-256 disagrees with its receipt")
    with np.load(g2_file, allow_pickle=False) as source:
        missing = sorted(REQUIRED_G2_KEYS - set(source.files))
        if missing:
            raise ValueError(f"G2 manifest missing required arrays: {missing}")
        if str(_scalar(source["petSchemaVersion"])) != G2_SCHEMA_VERSION:
            raise ValueError("wrong G2 schema version")
        if str(_scalar(source["estimator_fingerprint"])) != G2_ESTIMATOR_FINGERPRINT:
            raise ValueError("wrong G2 estimator fingerprint")
        if int(_scalar(source["hasFullEventSchema"])) != 1 or int(
            _scalar(source["fullPhaseSpace"])
        ) != 1:
            raise ValueError("G2 full-event/full-phase-space markers are absent")
        arrays = {key: np.asarray(source[key]) for key in REQUIRED_G2_KEYS}
        source_hashes = {
            key: str(_scalar(source[key]))
            for key in ("sig_identity_hash", "data_identity_hash", "bkg_identity_hash")
            if key in source.files
        }
    identity_checks = {
        "sig_identity_hash": _legacy_order_hash(
            arrays["w_truth"], arrays["pass_truth"]
        ),
        "data_identity_hash": _legacy_order_hash(arrays["measured_pc"]),
        "bkg_identity_hash": _legacy_order_hash(
            arrays["w_bkg"], arrays["bkg_indices"]
        ),
    }
    for key, expected in identity_checks.items():
        if str(_scalar(arrays[key])) != expected:
            raise ValueError(f"G2 {key} does not match ordered inventory evidence")
    if target_file.suffix == ".npy":
        refined = np.load(target_file, allow_pickle=False)
    else:
        with np.load(target_file, allow_pickle=False) as target:
            if target_key not in target.files:
                raise ValueError(f"Gate-2 payload lacks '{target_key}'")
            refined = np.asarray(target[target_key])
    runtime_target = receipt.get("runtime_target", {})
    step1_feed = receipt.get("step1_feed", {})
    expected_rows = runtime_target.get("n_measured_rows")
    if expected_rows is not None and int(expected_rows) != int(refined.size):
        raise ValueError("Gate-2 target row count disagrees with runtime receipt")
    raw_refined_sum = runtime_target.get("refined_sum")
    normalized_sum = step1_feed.get("normalized_sum")
    if raw_refined_sum is None or normalized_sum is None:
        raise ValueError("Gate-2 receipt lacks raw and normalized target masses")
    actual_normalized_sum = float(np.asarray(refined, np.float64).sum())
    if not np.isclose(actual_normalized_sum, float(normalized_sum), rtol=2e-6):
        raise ValueError("Gate-2 normalized target mass disagrees with runtime receipt")
    # Recover the physical refined target mass before class-prior calibration.
    refined = (
        np.asarray(refined, np.float64)
        * float(raw_refined_sum)
        / actual_normalized_sum
    )
    pass_reco = np.asarray(arrays["pass_reco"], bool)
    pass_truth = np.asarray(arrays["pass_truth"], bool)
    reco = _reco_batch(
        arrays["part_reco"],
        arrays["reco_scalars"],
        arrays["reco_muon"],
        arrays["reco_vertex"],
        arrays["reco_view"],
        pass_reco,
        "g2_signal_reco",
    )
    truth = _truth_batch(arrays["part_gen"], arrays["truth_scalars"])
    data = _reco_batch(
        arrays["measured_pc"],
        arrays["measured_scalars"],
        arrays["data_muon"],
        arrays["data_vertex"],
        arrays["data_view"],
        np.ones(len(arrays["measured_pc"]), bool),
        "g2_data",
    )
    background = _reco_batch(
        arrays["bkg_part_reco"],
        arrays["bkg_reco_scalars"],
        arrays["bkg_muon"],
        arrays["bkg_vertex"],
        arrays["bkg_view"],
        np.ones(len(arrays["bkg_part_reco"]), bool),
        "g2_literal_background",
    )
    n_data = data.n_rows
    n_bkg = background.n_rows
    if runtime_target.get("pot_scale") is None:
        raise ValueError("Gate-2 receipt lacks the G2 POT scale")
    pot_scale = float(runtime_target["pot_scale"])
    if not np.isfinite(pot_scale) or pot_scale <= 0:
        raise ValueError("Gate-2 receipt POT scale must be finite and positive")
    raw_signed = np.concatenate(
        (np.ones(n_data), -pot_scale * np.asarray(arrays["w_bkg"], np.float64))
    )
    dataset = CanonicalDataset(
        signal=SignalInventory(
            reco=reco,
            truth=truth,
            pass_reco=pass_reco,
            pass_truth=pass_truth,
            w_reco=arrays["w_reco"],
            w_truth=arrays["w_truth"],
            identity_hash="",
            event_key=None,
        ),
        measured=MeasuredInventory(
            data=data,
            background=background,
            refined_weights=refined,
            raw_signed_weights=raw_signed,
            data_identity_hash="",
            background_identity_hash="",
            target_receipt=receipt,
        ),
        estimator_fingerprint=G2_ESTIMATOR_FINGERPRINT,
        schema={
            "source": "publication_g2",
            "g2_sha256": actual_g2_sha,
            "target_sha256": actual_target_sha,
            "target_receipt_sha256": file_sha256(receipt_file),
            "source_identity_hashes": source_hashes,
            "event_identity": "stable_row_and_inventory_hash_only",
            "g2_validation_claim": False,
            "adapter_mode": mini_packet["mode"],
            "g2_units_assumption": (
                "absent-publication-G2 contract assumption: clouds/muons/vertices "
                "are MeV/mm while reco/truth scalar columns are already GeV; "
                "not independently validated against a locally absent minerva-ml payload"
            ),
            "target_scale": {
                "input_normalized_sum": actual_normalized_sum,
                "recovered_raw_refined_sum": float(refined.sum()),
            },
        },
        pot_scale=pot_scale,
        pot_scale_source="gate2_receipt.runtime_target.pot_scale",
    ).validated()
    capabilities = FeatureCapabilities(
        real_object_types=False,
        object_type_source="unavailable in G2",
        detector_view=True,
        muon_token=True,
        muon_token_coordinates_audited=False,
        overflow_aggregate=False,
        audited_globals=(
            "mu_pt",
            "mu_pparallel",
            "mu_energy",
            "mu_cos_phi",
            "mu_sin_phi",
            "eavail",
            "q3",
            "minos_ok",
            "vertex_x",
            "vertex_y",
            "vertex_z",
        ),
        unsupported_reasons={
            "photon_blob_prong_type": "not dumped in G2",
            "dedx": "not dumped in G2",
            "overflow_aggregate": "pre-truncation counts and discarded energy absent",
            "time": "unit/reference not audited for this backend",
            "mu_charge": "q/p unit and zero convention not yet audited",
            "muon_token_coordinates": (
                "G2 adapter has no audited muon KNN coordinate convention"
            ),
        },
        source_kind="g2_mini_packet",
    )
    return dataset, capabilities
