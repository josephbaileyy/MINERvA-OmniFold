#!/usr/bin/env python3
"""Diagnose non-finite reco-cluster energies without changing GAP-3 results."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import tempfile
from typing import Any, Iterable
import zipfile

import numpy as np


CONTRACT_ID = "PET-G6-GAP3-NONFINITE-DIAGNOSTIC-20260830"
SOURCE_RELATIVE_PATH = Path(
    "nd-unfolding/g2_fullevent/merged/"
    "runEventLoopOmniFold_G2_FPS_MEFHC.root"
)
NPZ_RELATIVE_PATH = Path(
    "nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz"
)
NPZ_RECEIPT_RELATIVE_PATH = Path(
    "nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12_RECEIPT.json"
)
EXPECTED_SOURCE_SHA256 = (
    "9a16331f1c02103e3b5de5e6c00139aa39393ee11eb34881bea0b9a890344e2f"
)
EXPECTED_SOURCE_SIZE = 113_496_440_965
EXPECTED_NPZ_SHA256 = (
    "fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625"
)
EXPECTED_NPZ_SIZE = 9_897_374_636
EXPECTED_NPZ_RECEIPT_SHA256 = (
    "d466a0c18deaafa2ae645002c8dbc9b9879476adb45a40a85c0bae9e0129d25e"
)
CAP = 12
K_NEIGHBORS = 3
EXPECTED_SELECTED_ROWS = {
    "signal": 20_573_521,
    "data": 4_116_128,
    "background": 564_591,
}
EXPECTED_NPZ_ROWS = {
    "signal": 49_152_885,
    "data": 4_116_128,
    "background": 564_591,
}
EXPECTED_NONFINITE_ENTRIES = {
    "signal": 1_687,
    "data": 456,
    "background": 223,
}
PT_EDGES = (0, 0.07, 0.15, 0.25, 0.33, 0.4, 0.47, 0.55, 0.7, 0.85,
            1.0, 1.25, 1.5, 2.5, 4.5, 30)
PPARALLEL_EDGES = (0, 0.75, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 6, 7,
                   8, 9, 10, 15, 20, 40, 60, 120)
EAVAIL_EDGES = (0, 0.1, 0.2, 0.4, 0.8, 1.5, 3, 100)
Q3_EDGES = (0, 0.2, 0.4, 0.6, 0.8, 1.2, 2, 100)
AXIS_EDGES = {
    "pt": PT_EDGES,
    "pparallel": PPARALLEL_EDGES,
    "eavail": EAVAIL_EDGES,
    "q3": Q3_EDGES,
}
NON_AUTHORIZATION = (
    "do_not_filter_or_repair_inputs",
    "do_not_change_representation_or_token_cap",
    "do_not_retrain",
    "do_not_move_or_adopt_central_value",
    "do_not_construct_covariance_or_uncertainty",
    "do_not_select_gate6_member_or_start_leg2",
    "do_not_authorize_further_compute",
    "do_not_make_publication_claim",
)
INVENTORIES = {
    "signal": {
        "tree": "mc_signal_reco",
        "selection": (
            "sim_pass != 0 && std::isfinite(sim) && std::isfinite(sim_pz) "
            "&& sim >= 0.0 && sim <= 30.0 && sim_pz >= 0.0 && sim_pz <= 120.0"
        ),
        "keep": (
            "__gap3_selected || (std::isfinite(MC) && std::isfinite(MC_pz) "
            "&& MC >= 0.0 && MC <= 30.0 && MC_pz >= 0.0 && MC_pz <= 120.0)"
        ),
        "axes": ("sim", "sim_pz", "sim_eavail", "sim_q3"),
        "npz": {
            "cloud": "part_reco",
            "view": "reco_view",
            "time": "reco_time",
            "scalars": "reco_scalars",
            "weight": "w_reco",
            "pass": "pass_reco",
        },
        "weight": "w_reco",
    },
    "data": {
        "tree": "data",
        "selection": (
            "measured_pass != 0 && std::isfinite(measured) "
            "&& std::isfinite(measured_pz) && measured >= 0.0 "
            "&& measured <= 30.0 && measured_pz >= 0.0 "
            "&& measured_pz <= 120.0"
        ),
        "keep": "__gap3_selected",
        "axes": ("measured", "measured_pz", "measured_eavail", "measured_q3"),
        "npz": {
            "cloud": "measured_pc",
            "view": "data_view",
            "time": "data_time",
            "scalars": "measured_scalars",
        },
        "weight": None,
    },
    "background": {
        "tree": "mc_background",
        "selection": (
            "sim_background_pass != 0 && std::isfinite(sim_background) "
            "&& std::isfinite(sim_background_pz) && sim_background >= 0.0 "
            "&& sim_background <= 30.0 && sim_background_pz >= 0.0 "
            "&& sim_background_pz <= 120.0"
        ),
        "keep": "__gap3_selected",
        "axes": (
            "sim_background",
            "sim_background_pz",
            "sim_background_eavail",
            "sim_background_q3",
        ),
        "npz": {
            "cloud": "bkg_part_reco",
            "view": "bkg_view",
            "time": "bkg_time",
            "scalars": "bkg_reco_scalars",
            "weight": "w_bkg",
        },
        "weight": "w_bkg",
    },
}

CPP_HELPERS = r"""
#include <cmath>
#include "ROOT/RVec.hxx"
namespace gap3diag {
bool has_nonfinite(const ROOT::VecOps::RVec<double>& values) {
  for (const double value : values) {
    if (!std::isfinite(value)) return true;
  }
  return false;
}
}
"""


def sha256_file(path: Path, chunk_size: int = 16 * 1024 * 1024) -> str:
    """Return a file SHA-256 using bounded memory."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def _git_output(code_root: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(code_root), *arguments],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _verify_hash(label: str, path: Path, expected: str) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"missing {label}: {path}")
    actual = sha256_file(path)
    if actual != expected:
        raise RuntimeError(f"{label} SHA-256 mismatch: {actual} != {expected}")
    return {"artifact": label, "digest": f"sha256:{actual}"}


def classify_nonfinite(value: float) -> str | None:
    """Classify a scalar as NaN, positive infinity, or negative infinity."""
    if math.isnan(value):
        return "nan"
    if value == math.inf:
        return "positive_infinity"
    if value == -math.inf:
        return "negative_infinity"
    return None


def production_sort(columns: Iterable[Iterable[float]]) -> np.ndarray:
    """Reproduce the production float32 stable descending-energy sort."""
    array = np.array([list(column) for column in columns], np.float32).T
    if array.shape[0] > 1:
        array = array[np.argsort(-array[:, 0], kind="stable")]
    return array


def production_pad(columns: Iterable[Iterable[float]], cap: int = CAP) -> np.ndarray:
    """Reproduce production sorting, truncation, and zero padding."""
    columns_list = [list(column) for column in columns]
    output = np.zeros((cap, len(columns_list)), dtype=np.float32)
    if not columns_list or not columns_list[0]:
        return output
    ranked = production_sort(columns_list)
    kept = min(ranked.shape[0], cap)
    output[:kept] = ranked[:kept]
    return output


def npz_row_for_source_entry(kept_entries: np.ndarray, source_entry: int) -> int:
    """Map a ROOT entry to its filtered NPZ row and fail if it was not retained."""
    index = int(np.searchsorted(kept_entries, source_entry))
    if index >= kept_entries.size or int(kept_entries[index]) != source_entry:
        raise RuntimeError(f"selected source entry {source_entry} is absent from kept order")
    return index


def _array_equal(left: np.ndarray, right: np.ndarray) -> bool:
    return bool(np.array_equal(left, right, equal_nan=True))


def _load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def inspect_source_paths(code_root: Path) -> dict[str, Any]:
    """Verify the exact production sort, loader mask, and model mask path."""
    dumper = (code_root / "nd-unfolding/pet/dump_pointcloud_inputs.py").read_text()
    loader = (code_root / "nd-unfolding/pet/fullevent_fps_dataloader.py").read_text()
    model = (code_root / "omnifold_nn/omnifold/net.py").read_text()
    required = {
        "production_float32_conversion": "np.array([list(c) for c in cols], np.float32).T" in dumper,
        "production_stable_sort": 'np.argsort(-arr[:, 0], kind="stable")' in dumper,
        "loader_nonfinite_to_zero": (
            "nan=0.0, posinf=0.0, neginf=0.0" in loader
        ),
        "loader_energy_not_equal_zero_mask": "real = cloud[:, :, 0] != 0.0" in loader,
        "model_energy_not_equal_zero_mask": (
            "inputs_part[:, :, 0, None] != 0" in model
            and "inputs_part[:,:,0,None] != 0" in model
        ),
        "model_coordinate_shift": "tf.multiply(999." in model,
        "model_body_reapplies_mask": "encoded = layers.Add()([x3,x2])*inputs_mask" in model,
        "model_film_reapplies_mask": "encoded = encoded * token_mask" in model,
        "model_head_attention_mask": "attention_mask=attn_mask" in model,
    }
    if not all(required.values()):
        failed = [name for name, passed in required.items() if not passed]
        raise RuntimeError(f"production source-path checks failed: {failed}")
    body_prefix = model.split("def PET_head", maxsplit=1)[0]
    initial_attention_has_mask = "attention_mask=" in body_prefix.split(
        "def PET_body", maxsplit=1
    )[1]
    return {
        "checks": required,
        "energy_gt_zero_guard_present": False,
        "actual_energy_mask_predicate": "energy != 0 after loader nonfinite-to-zero sanitization",
        "token_removed_before_model_call": False,
        "initial_dense_encoding_precedes_body_mask": (
            model.index("encoded = get_encodding") < model.index("inputs_mask = tf.cast")
        ),
        "first_body_attention_has_padding_key_mask": initial_attention_has_mask,
    }


def verify_static_inputs(args: argparse.Namespace) -> dict[str, Any]:
    """Verify checkout, source artifacts, NPZ, and all bound code artifacts."""
    code_root = args.code_root.resolve()
    data_root = args.data_root.resolve()
    if _git_output(code_root, "rev-parse", "HEAD") != args.expected_head:
        raise RuntimeError("code checkout HEAD mismatch")
    if _git_output(code_root, "status", "--porcelain"):
        raise RuntimeError("code checkout is dirty")

    bindings = {
        "diagnostic": (Path(__file__).resolve(), args.expected_diagnostic_sha256),
        "predeclaration": (
            code_root / args.predeclaration_relative_path,
            args.expected_predeclaration_sha256,
        ),
        "proposal": (code_root / args.proposal_relative_path, args.expected_proposal_sha256),
        "test": (code_root / args.test_relative_path, args.expected_test_sha256),
        "guard": (
            code_root / "nd-unfolding/mnv_guarded_run.py",
            args.expected_guard_sha256,
        ),
        "dumper": (
            code_root / "nd-unfolding/pet/dump_pointcloud_inputs.py",
            args.expected_dumper_sha256,
        ),
        "loader": (
            code_root / "nd-unfolding/pet/fullevent_fps_dataloader.py",
            args.expected_loader_sha256,
        ),
        "model": (
            code_root / "omnifold_nn/omnifold/net.py",
            args.expected_model_sha256,
        ),
        "gate6_receipt": (
            code_root
            / "docs/orchestration/state/gate6-member-trajectories-result-56847059.json",
            args.expected_gate6_receipt_sha256,
        ),
        "prior_predeclaration": (
            code_root
            / "docs/orchestration/"
            "PREDECLARATION-20260830-gate6-gap3-reco-truncation-changed-retry1.md",
            args.expected_prior_predeclaration_sha256,
        ),
        "prior_launcher": (
            code_root / "nd-unfolding/pet/sbatch_gap3_reco_truncation_changed_retry1.sh",
            args.expected_prior_launcher_sha256,
        ),
        "prior_launch_receipt": (
            code_root
            / "docs/orchestration/state/"
            "gate6-gap3-reco-truncation-changed-retry1-launch-57729539.json",
            args.expected_prior_launch_receipt_sha256,
        ),
        "prior_terminal_receipt": (
            code_root
            / "docs/orchestration/state/"
            "gate6-gap3-reco-truncation-changed-retry1-terminal-57729539.json",
            args.expected_prior_terminal_receipt_sha256,
        ),
        "prior_result": (
            code_root
            / "docs/orchestration/state/"
            "gate6-gap3-reco-truncation-changed-retry1-result-57729539.json.gz",
            args.expected_prior_result_sha256,
        ),
    }
    verified = {
        label: _verify_hash(label, path, digest)
        for label, (path, digest) in bindings.items()
    }

    source = data_root / SOURCE_RELATIVE_PATH
    npz_path = data_root / NPZ_RELATIVE_PATH
    receipt = data_root / NPZ_RECEIPT_RELATIVE_PATH
    for label, path, size, digest in (
        ("source_root", source, EXPECTED_SOURCE_SIZE, EXPECTED_SOURCE_SHA256),
        ("p12_npz", npz_path, EXPECTED_NPZ_SIZE, EXPECTED_NPZ_SHA256),
    ):
        if path.stat().st_size != size:
            raise RuntimeError(f"{label} size mismatch")
        verified[label] = _verify_hash(label, path, digest)
    verified["p12_npz_receipt"] = _verify_hash(
        "p12_npz_receipt", receipt, EXPECTED_NPZ_RECEIPT_SHA256
    )
    receipt_payload = json.loads(receipt.read_text(encoding="utf-8"))
    recorded_npz = receipt_payload.get("npz", {})
    if recorded_npz.get("sha256") != EXPECTED_NPZ_SHA256:
        raise RuntimeError("NPZ receipt does not bind expected NPZ digest")
    if int(recorded_npz.get("size_bytes", -1)) != EXPECTED_NPZ_SIZE:
        raise RuntimeError("NPZ receipt does not bind expected NPZ size")
    return {
        "verified_hashes": verified,
        "production_path": inspect_source_paths(code_root),
        "source": source,
        "npz": npz_path,
    }


def _declare_root_helpers(root: Any) -> None:
    if not root.gInterpreter.Declare(CPP_HELPERS):
        raise RuntimeError("ROOT helper JIT failed")


def _verify_root_schema(root: Any, source: Path) -> dict[str, Any]:
    handle = root.TFile.Open(str(source), "READ")
    if not handle or handle.IsZombie():
        raise RuntimeError("cannot open source ROOT")
    schema: dict[str, Any] = {}
    common = {
        "part_reco_E",
        "part_reco_pos",
        "part_reco_z",
        "part_reco_view",
        "part_reco_time",
    }
    for name, config in INVENTORIES.items():
        tree = handle.Get(config["tree"])
        if not tree:
            raise RuntimeError(f"missing ROOT tree {config['tree']}")
        required = common | set(config["axes"])
        if config["weight"]:
            required.add(config["weight"])
        if name == "signal":
            required |= {"MC", "MC_pz", "sim_pass"}
        elif name == "data":
            required.add("measured_pass")
        else:
            required.add("sim_background_pass")
        missing = sorted(branch for branch in required if not tree.GetBranch(branch))
        if missing:
            raise RuntimeError(f"{name} missing branches: {missing}")
        schema[name] = {
            "entries": int(tree.GetEntries()),
            "branches_verified": sorted(required),
        }
    handle.Close()
    return schema


def _npy_shape(archive: zipfile.ZipFile, key: str) -> list[int]:
    with archive.open(f"{key}.npy") as stream:
        version = np.lib.format.read_magic(stream)
        if version == (1, 0):
            shape, _fortran, _dtype = np.lib.format.read_array_header_1_0(stream)
        elif version in {(2, 0), (3, 0)}:
            shape, _fortran, _dtype = np.lib.format.read_array_header_2_0(stream)
        else:
            raise RuntimeError(f"unsupported NPY header version for {key}: {version}")
    return [int(value) for value in shape]


def _npz_header(npz_path: Path) -> dict[str, Any]:
    with zipfile.ZipFile(npz_path) as archive:
        if _npy_shape(archive, "num_part") != []:
            raise RuntimeError("NPZ num_part marker is not scalar")
        payload: dict[str, Any] = {"arrays": {}}
        for name, config in INVENTORIES.items():
            shapes = {
                role: _npy_shape(archive, key)
                for role, key in config["npz"].items()
            }
            if shapes["cloud"] != [EXPECTED_NPZ_ROWS[name], CAP, 3]:
                raise RuntimeError(f"{name} NPZ cloud shape mismatch: {shapes['cloud']}")
            payload["arrays"][name] = shapes
    with np.load(npz_path, allow_pickle=False) as npz:
        payload["num_part"] = int(npz["num_part"])
    if payload["num_part"] != CAP:
        raise RuntimeError("NPZ num_part is not 12")
    return payload


def run_preflight(args: argparse.Namespace) -> dict[str, Any]:
    """Run full hash, ROOT/JIT, schema, NPZ, and pure semantic preflight."""
    static = verify_static_inputs(args)
    import ROOT  # type: ignore[import-not-found]

    _declare_root_helpers(ROOT)
    schema = _verify_root_schema(ROOT, static["source"])
    header = _npz_header(static["npz"])
    run_self_tests()
    return {
        "status": "PASS",
        "hashes": static["verified_hashes"],
        "production_path": static["production_path"],
        "root_version": str(ROOT.gROOT.GetVersion()),
        "root_helper_jit": True,
        "schema": schema,
        "npz_header": header,
    }


def _to_vector_list(values: np.ndarray) -> list[list[float]]:
    return [list(value) for value in values]


def _scan_source_inventory(
    root: Any, source: Path, name: str, config: dict[str, Any]
) -> tuple[np.ndarray, int, dict[str, np.ndarray]]:
    dataframe = root.RDataFrame(config["tree"], str(source)).Define(
        "__gap3_selected", config["selection"]
    )
    kept_payload = dataframe.Filter(config["keep"]).AsNumpy(
        ["rdfentry_", "__gap3_selected"]
    )
    kept_entries = np.asarray(kept_payload["rdfentry_"], dtype=np.uint64)
    selected_count = int(np.count_nonzero(kept_payload["__gap3_selected"]))
    kept_entries.sort()

    branches = [
        "rdfentry_",
        "part_reco_E",
        "part_reco_pos",
        "part_reco_z",
        "part_reco_view",
        "part_reco_time",
        *config["axes"],
    ]
    if config["weight"]:
        branches.append(config["weight"])
    affected = dataframe.Filter("__gap3_selected").Filter(
        "gap3diag::has_nonfinite(part_reco_E)"
    ).AsNumpy(branches)
    order = np.argsort(affected["rdfentry_"], kind="stable")
    sorted_affected = {
        key: np.asarray(values, dtype=object)[order]
        if np.asarray(values).dtype == object
        else np.asarray(values)[order]
        for key, values in affected.items()
    }
    return kept_entries, selected_count, sorted_affected


def _read_npz_rows(
    npz_path: Path, config: dict[str, Any], indices: np.ndarray
) -> dict[str, np.ndarray]:
    selected: dict[str, np.ndarray] = {}
    with np.load(npz_path, allow_pickle=False) as archive:
        for role, key in config["npz"].items():
            full = archive[key]
            selected[role] = np.asarray(full[indices]).copy()
            del full
    return selected


def _bin_index(value: float, edges: tuple[float, ...]) -> int | None:
    if not math.isfinite(value) or value < edges[0] or value > edges[-1]:
        return None
    if value == edges[-1]:
        return len(edges) - 2
    index = int(np.searchsorted(np.asarray(edges), value, side="right") - 1)
    return index if 0 <= index < len(edges) - 1 else None


def _empty_counts() -> dict[str, int]:
    return {
        "affected_events": 0,
        "nonfinite_entries": 0,
        "nan": 0,
        "positive_infinity": 0,
        "negative_infinity": 0,
        "inside_rank_12": 0,
        "beyond_rank_12": 0,
        "stored_nonfinite_tokens": 0,
    }


def _add_counts(target: dict[str, int], source: dict[str, int]) -> None:
    for key in target:
        target[key] += int(source[key])


def _kinematic_template() -> dict[str, Any]:
    axes = {
        axis: [
            {"low": float(edges[index]), "high": float(edges[index + 1]), **_empty_counts()}
            for index in range(len(edges) - 1)
        ]
        for axis, edges in AXIS_EDGES.items()
    }
    axes["pt_pparallel"] = [
        {
            "pt_low": float(PT_EDGES[pt]),
            "pt_high": float(PT_EDGES[pt + 1]),
            "pparallel_low": float(PPARALLEL_EDGES[ppar]),
            "pparallel_high": float(PPARALLEL_EDGES[ppar + 1]),
            **_empty_counts(),
        }
        for pt in range(len(PT_EDGES) - 1)
        for ppar in range(len(PPARALLEL_EDGES) - 1)
    ]
    return axes


def _update_kinematics(
    kinematics: dict[str, Any], axes: tuple[float, ...], counts: dict[str, int]
) -> None:
    indices = {
        axis: _bin_index(float(value), AXIS_EDGES[axis])
        for axis, value in zip(("pt", "pparallel", "eavail", "q3"), axes)
    }
    for axis in ("pt", "pparallel", "eavail", "q3"):
        index = indices[axis]
        if index is not None:
            _add_counts(kinematics[axis][index], counts)
    if indices["pt"] is not None and indices["pparallel"] is not None:
        flat = indices["pt"] * (len(PPARALLEL_EDGES) - 1) + indices["pparallel"]
        _add_counts(kinematics["pt_pparallel"][flat], counts)


def _conservative_masked_knn_risk(cloud: np.ndarray) -> bool:
    mask = cloud[:, 0] != 0.0
    real_indices = np.flatnonzero(mask)
    masked_indices = np.flatnonzero(~mask)
    if not masked_indices.size:
        return False
    points = cloud[:, (1, 2)].astype(np.float32)
    shifted = points + (~mask)[:, None].astype(np.float32) * np.float32(999.0)
    for query in real_indices:
        distances = np.abs(
            np.sum(shifted * shifted, axis=1)
            - np.float32(2.0) * np.sum(shifted * shifted[query], axis=1)
            + np.sum(shifted[query] * shifted[query])
        )
        other_real = np.delete(distances[real_indices], np.where(real_indices == query))
        if other_real.size < K_NEIGHBORS:
            return True
        threshold = np.partition(other_real, K_NEIGHBORS - 1)[K_NEIGHBORS - 1]
        if float(np.min(distances[masked_indices])) <= float(threshold):
            return True
    return False


def _summarize_distribution(values: list[int]) -> dict[str, Any]:
    counter = Counter(values)
    return {
        "minimum": min(values) if values else None,
        "maximum": max(values) if values else None,
        "sum": int(sum(values)),
        "histogram": {str(key): int(counter[key]) for key in sorted(counter)},
    }


def _diagnose_population(
    name: str,
    config: dict[str, Any],
    kept_entries: np.ndarray,
    source_rows: dict[str, np.ndarray],
    stored_rows: dict[str, np.ndarray],
    loader: Any,
) -> dict[str, Any]:
    source_entries = np.asarray(source_rows["rdfentry_"], dtype=np.uint64)
    npz_indices = np.asarray(
        [npz_row_for_source_entry(kept_entries, int(entry)) for entry in source_entries],
        dtype=np.int64,
    )
    aggregate = _empty_counts()
    kinematics = _kinematic_template()
    records: list[dict[str, Any]] = []
    raw_lengths: list[int] = []
    finite_positive_counts: list[int] = []
    capped_finite_positive_counts: list[int] = []
    stored_positive_counts: list[int] = []
    pet_mask_counts: list[int] = []
    alignment_failures = 0
    conservative_knn_risk_events = 0
    initial_attention_risk_events = 0

    loaded_cloud, coord_idx = loader.build_reco_cloud(
        stored_rows["cloud"], stored_rows["view"], stored_rows["time"]
    )
    if tuple(coord_idx) != (1, 2):
        raise RuntimeError(f"{name} loader coord_idx changed: {coord_idx}")
    if not np.all(np.isfinite(loaded_cloud)):
        raise RuntimeError(f"{name} loader output remains non-finite")

    for row, source_entry in enumerate(source_entries):
        energy = np.asarray(source_rows["part_reco_E"][row], dtype=np.float64)
        pos = np.asarray(source_rows["part_reco_pos"][row], dtype=np.float64)
        z = np.asarray(source_rows["part_reco_z"][row], dtype=np.float64)
        view = np.asarray(source_rows["part_reco_view"][row], dtype=np.float64)
        time = np.asarray(source_rows["part_reco_time"][row], dtype=np.float64)
        lengths = {len(energy), len(pos), len(z), len(view), len(time)}
        if len(lengths) != 1:
            raise RuntimeError(f"{name} entry {source_entry} has unaligned raw vectors")

        ranked = production_sort((energy, pos, z, view, time))
        expected = production_pad((energy, pos, z, view, time))
        source_axes = tuple(float(source_rows[axis][row]) for axis in config["axes"])
        event_counts = _empty_counts()
        event_counts["affected_events"] = 1
        nonfinite_records = []
        energy32 = np.asarray(energy, dtype=np.float32)
        order = np.argsort(-energy32, kind="stable")
        ranks = np.empty(len(order), dtype=np.int64)
        ranks[order] = np.arange(1, len(order) + 1)
        for raw_index, value in enumerate(energy):
            classification = classify_nonfinite(float(value))
            if classification is None:
                continue
            rank = int(ranks[raw_index])
            inside = rank <= CAP
            event_counts["nonfinite_entries"] += 1
            event_counts[classification] += 1
            event_counts["inside_rank_12" if inside else "beyond_rank_12"] += 1
            nonfinite_records.append(
                {
                    "raw_index": raw_index,
                    "classification": classification,
                    "production_rank_1_based": rank,
                    "inside_rank_12": inside,
                }
            )

        stored_cloud = stored_rows["cloud"][row]
        stored_view = stored_rows["view"][row]
        stored_time = stored_rows["time"][row]
        stored_energy = stored_cloud[:, 0]
        stored_nonfinite = int(np.count_nonzero(~np.isfinite(stored_energy)))
        event_counts["stored_nonfinite_tokens"] = stored_nonfinite
        _add_counts(aggregate, event_counts)
        _update_kinematics(kinematics, source_axes, event_counts)

        cloud_match = _array_equal(expected[:, :3], stored_cloud)
        view_match = _array_equal(expected[:, 3], stored_view)
        time_match = _array_equal(expected[:, 4], stored_time)
        scalar_expected = np.asarray(source_axes, dtype=np.float32)
        scalar_match = _array_equal(scalar_expected, stored_rows["scalars"][row])
        weight_match = True
        if config["weight"]:
            weight_expected = np.float32(source_rows[config["weight"]][row])
            weight_match = bool(
                np.array_equal(weight_expected, stored_rows["weight"][row], equal_nan=True)
            )
        pass_match = True
        if "pass" in stored_rows:
            pass_match = bool(stored_rows["pass"][row])
        aligned = cloud_match and view_match and time_match and scalar_match and weight_match and pass_match
        alignment_failures += int(not aligned)

        raw_length = len(energy)
        finite_positive = int(np.count_nonzero(np.isfinite(energy) & (energy > 0.0)))
        capped_finite_positive = min(finite_positive, CAP)
        stored_positive = int(np.count_nonzero(np.isfinite(stored_energy) & (stored_energy > 0.0)))
        pet_mask = loaded_cloud[row, :, 0] != 0.0
        pet_mask_count = int(np.count_nonzero(pet_mask))
        raw_lengths.append(raw_length)
        finite_positive_counts.append(finite_positive)
        capped_finite_positive_counts.append(capped_finite_positive)
        stored_positive_counts.append(stored_positive)
        pet_mask_counts.append(pet_mask_count)
        stored_nonfinite_mask = ~np.isfinite(stored_energy)
        structurally_distinct = bool(
            stored_nonfinite > 0
            and np.any(loaded_cloud[row][stored_nonfinite_mask] != 0.0)
        )
        knn_risk = structurally_distinct and _conservative_masked_knn_risk(
            loaded_cloud[row]
        )
        conservative_knn_risk_events += int(knn_risk)
        initial_attention_risk = structurally_distinct
        initial_attention_risk_events += int(initial_attention_risk)

        records.append(
            {
                "source_entry": int(source_entry),
                "npz_row": int(npz_indices[row]),
                "raw_vector_length": raw_length,
                "finite_positive_multiplicity": finite_positive,
                "capped_finite_positive_multiplicity": capped_finite_positive,
                "stored_finite_positive_multiplicity": stored_positive,
                "pet_energy_not_equal_zero_mask_multiplicity": pet_mask_count,
                "nonfinite_entries": nonfinite_records,
                "stored_nonfinite_energy_tokens": stored_nonfinite,
                "sanitized_token_differs_from_zero_padding": structurally_distinct,
                "stored_nonfinite_tokens_sanitized_to_zero_and_mask_false": bool(
                    stored_nonfinite == 0
                    or np.all(~pet_mask[~np.isfinite(stored_energy)])
                ),
                "source_to_npz_alignment": {
                    "cloud": cloud_match,
                    "view": view_match,
                    "time": time_match,
                    "scalars": scalar_match,
                    "weight": weight_match,
                    "pass_reco": pass_match,
                },
                "masked_token_can_enter_first_knn_conservative": knn_risk,
                "masked_token_can_enter_first_unmasked_body_attention": initial_attention_risk,
                "kinematics": {
                    axis: value if math.isfinite(value) else None
                    for axis, value in zip(
                        ("pt", "pparallel", "eavail", "q3"), source_axes
                    )
                },
                "ranked_row_count": int(ranked.shape[0]),
            }
        )

    return {
        "kept_npz_rows": int(kept_entries.size),
        "aggregate": aggregate,
        "multiplicity_distributions": {
            "raw_vector_length": _summarize_distribution(raw_lengths),
            "finite_positive": _summarize_distribution(finite_positive_counts),
            "capped_finite_positive": _summarize_distribution(capped_finite_positive_counts),
            "stored_finite_positive": _summarize_distribution(stored_positive_counts),
            "pet_energy_not_equal_zero_mask": _summarize_distribution(pet_mask_counts),
        },
        "source_to_npz_alignment_failures": alignment_failures,
        "conservative_first_knn_risk_events": conservative_knn_risk_events,
        "first_unmasked_body_attention_risk_events": initial_attention_risk_events,
        "kinematics": kinematics,
        "events": records,
    }


def run_diagnostic(args: argparse.Namespace) -> dict[str, Any]:
    """Run the bounded ROOT-to-NPZ non-finite-energy diagnostic."""
    static = verify_static_inputs(args)
    import ROOT  # type: ignore[import-not-found]

    ROOT.EnableImplicitMT(args.threads)
    _declare_root_helpers(ROOT)
    schema = _verify_root_schema(ROOT, static["source"])
    header = _npz_header(static["npz"])
    loader_path = args.code_root / "nd-unfolding/pet/fullevent_fps_dataloader.py"
    loader = _load_module(loader_path, "gap3_nonfinite_bound_loader")

    populations: dict[str, Any] = {}
    checks: dict[str, bool] = {}
    for name, config in INVENTORIES.items():
        kept, selected_count, source_rows = _scan_source_inventory(
            ROOT, static["source"], name, config
        )
        indices = np.asarray(
            [npz_row_for_source_entry(kept, int(entry)) for entry in source_rows["rdfentry_"]],
            dtype=np.int64,
        )
        stored = _read_npz_rows(static["npz"], config, indices)
        population = _diagnose_population(
            name, config, kept, source_rows, stored, loader
        )
        population["selected_rows"] = selected_count
        population["affected_selected_events"] = int(len(source_rows["rdfentry_"]))
        populations[name] = population
        checks[f"{name}:npz_rows"] = int(kept.size) == EXPECTED_NPZ_ROWS[name]
        checks[f"{name}:selected_rows"] = selected_count == EXPECTED_SELECTED_ROWS[name]
        checks[f"{name}:nonfinite_entries"] = (
            population["aggregate"]["nonfinite_entries"]
            == EXPECTED_NONFINITE_ENTRIES[name]
        )
        checks[f"{name}:alignment"] = population["source_to_npz_alignment_failures"] == 0
        checks[f"{name}:stored_sanitized"] = all(
            event["stored_nonfinite_tokens_sanitized_to_zero_and_mask_false"]
            for event in population["events"]
        )

    total_nonfinite = sum(
        population["aggregate"]["nonfinite_entries"]
        for population in populations.values()
    )
    total_stored_nonfinite = sum(
        population["aggregate"]["stored_nonfinite_tokens"]
        for population in populations.values()
    )
    potential_influence_events = sum(
        population["first_unmasked_body_attention_risk_events"]
        for population in populations.values()
    )
    checks["total_nonfinite_entries"] = total_nonfinite == 2_366
    checks["source_path"] = all(static["production_path"]["checks"].values())
    status = "PASS" if all(checks.values()) else "INVALID_OR_INCOMPLETE"
    if total_stored_nonfinite == 0:
        influence = "NO_NONFINITE_TOKEN_REACHES_STORED_P12_MODEL_INPUT"
    elif potential_influence_events:
        influence = "POTENTIAL_INFLUENCE_VIA_PRE_MASK_ENCODING_OR_FIRST_BODY_ATTENTION"
    else:
        influence = "STRUCTURALLY_PRESENT_BUT_MASKED_WITH_NO_IDENTIFIED_INFLUENCE_PATH"

    recommendation = (
        "FINITE_POSITIVE_PET_ELIGIBLE_CLUSTERS"
        if status == "PASS"
        else "NO_DENOMINATOR_RECOMMENDATION_FROM_INCOMPLETE_DIAGNOSTIC"
    )
    return {
        "schema_version": 1,
        "contract_id": CONTRACT_ID,
        "status": status,
        "nonquotable_diagnostic": True,
        "provenance": {
            "head": args.expected_head,
            "source_sha256": EXPECTED_SOURCE_SHA256,
            "npz_sha256": EXPECTED_NPZ_SHA256,
            "verified_hashes": static["verified_hashes"],
        },
        "runtime": {"root_threads": args.threads, "root_version": str(ROOT.gROOT.GetVersion())},
        "schema": schema,
        "npz_header": header,
        "production_path": static["production_path"],
        "checks": checks,
        "populations": populations,
        "combined": {
            "nonfinite_entries": total_nonfinite,
            "stored_p12_nonfinite_energy_tokens": total_stored_nonfinite,
            "events_with_potential_model_influence": potential_influence_events,
            "model_input_conclusion": influence,
            "scientifically_correct_denominator_recommendation": recommendation,
            "denominator_reason": (
                "The PET representation is defined by finite positive energy tokens; all raw "
                "entries remains a source-record census and includes values with undefined "
                "energy arithmetic. This recommendation does not alter the prior invalid result."
            ),
        },
        "non_authorization": list(NON_AUTHORIZATION),
        "prior_gap3_result_remains": "INVALID_OR_INCOMPLETE",
    }


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() or path.is_symlink():
        raise FileExistsError(f"refuse occupied output: {path}")
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=path.parent, delete=False
    ) as stream:
        json.dump(payload, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
        temporary = Path(stream.name)
    temporary.replace(path)


def run_self_tests() -> None:
    """Exercise stable sort, non-finite classes, mapping, and padding semantics."""
    energies = [2.0, math.nan, math.inf, 2.0, -math.inf, 1.0]
    marker = list(range(len(energies)))
    ranked = production_sort((energies, marker))
    assert ranked[:, 1].astype(int).tolist() == [2, 0, 3, 5, 4, 1]
    assert classify_nonfinite(math.nan) == "nan"
    assert classify_nonfinite(math.inf) == "positive_infinity"
    assert classify_nonfinite(-math.inf) == "negative_infinity"
    assert classify_nonfinite(0.0) is None
    kept = np.asarray([1, 3, 8, 11], dtype=np.uint64)
    assert npz_row_for_source_entry(kept, 8) == 2
    padded = production_pad(([2.0, 1.0], [20.0, 10.0]), cap=3)
    assert padded.tolist() == [[2.0, 20.0], [1.0, 10.0], [0.0, 0.0]]


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--code-root", type=Path)
    parser.add_argument("--data-root", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--expected-head")
    parser.add_argument("--threads", type=int, choices=(18,), default=18)
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    for name in (
        "diagnostic",
        "predeclaration",
        "proposal",
        "test",
        "guard",
        "dumper",
        "loader",
        "model",
        "gate6_receipt",
        "prior_predeclaration",
        "prior_launcher",
        "prior_launch_receipt",
        "prior_terminal_receipt",
        "prior_result",
    ):
        parser.add_argument(f"--expected-{name.replace('_', '-')}-sha256")
    parser.add_argument(
        "--predeclaration-relative-path",
        type=Path,
        default=Path(
            "docs/orchestration/"
            "PREDECLARATION-20260830-gate6-gap3-nonfinite-diagnostic.md"
        ),
    )
    parser.add_argument(
        "--proposal-relative-path",
        type=Path,
        default=Path(
            "docs/orchestration/state/"
            "gate6-gap3-nonfinite-diagnostic-proposal-20260830.json"
        ),
    )
    parser.add_argument(
        "--test-relative-path",
        type=Path,
        default=Path("nd-unfolding/pet/test_gap3_nonfinite_diagnostic.py"),
    )
    return parser


def main() -> int:
    args = _parser().parse_args()
    if args.self_test:
        run_self_tests()
        print("PASS: GAP-3 non-finite diagnostic self-tests")
        return 0
    required = {
        "code_root": args.code_root,
        "data_root": args.data_root,
        "expected_head": args.expected_head,
    }
    for name in (
        "diagnostic",
        "predeclaration",
        "proposal",
        "test",
        "guard",
        "dumper",
        "loader",
        "model",
        "gate6_receipt",
        "prior_predeclaration",
        "prior_launcher",
        "prior_launch_receipt",
        "prior_terminal_receipt",
        "prior_result",
    ):
        required[f"expected_{name}_sha256"] = getattr(
            args, f"expected_{name}_sha256"
        )
    missing = sorted(name for name, value in required.items() if value is None)
    if missing:
        raise SystemExit(f"missing required runtime arguments: {', '.join(missing)}")
    if args.preflight_only:
        print(json.dumps(run_preflight(args), indent=2, sort_keys=True))
        return 0
    if args.output is None:
        raise SystemExit("--output is required outside preflight mode")
    payload = run_diagnostic(args)
    _atomic_write_json(args.output, payload)
    print(f"[{CONTRACT_ID}] {payload['status']} output={args.output}")
    return 0 if payload["status"] == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
