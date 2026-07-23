"""Atomic, portable artifacts and receipts."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, Mapping

import numpy as np

from .utils import canonical_json, environment_receipt, file_sha256, git_state


@contextmanager
def atomic_run_directory(path: os.PathLike[str] | str) -> Iterator[Path]:
    """Create a complete run in a sibling temp directory, then atomically publish it."""
    destination = Path(path).resolve()
    if destination.exists():
        raise FileExistsError(f"refusing to overwrite existing run directory: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(
        tempfile.mkdtemp(prefix=f".{destination.name}.tmp-", dir=destination.parent)
    )
    try:
        yield temporary
        os.replace(temporary, destination)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise


def write_json(path: os.PathLike[str] | str, payload: Mapping[str, Any]) -> None:
    path = Path(path)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    temporary.write_text(canonical_json(payload) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def write_npz_atomic(path: os.PathLike[str] | str, **arrays: np.ndarray) -> None:
    path = Path(path)
    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.tmp-", suffix=".npz", dir=path.parent
    )
    os.close(fd)
    try:
        np.savez_compressed(temporary_name, **arrays)
        os.replace(temporary_name, path)
    finally:
        if os.path.exists(temporary_name):
            os.unlink(temporary_name)


def _save_safetensors(path: Path, model) -> None:
    try:
        from safetensors.torch import save_file
    except ImportError as exc:
        raise RuntimeError(
            "safetensors is required for portable model artifacts; no pickle fallback is allowed"
        ) from exc
    state = {key: value.detach().cpu().contiguous() for key, value in model.state_dict().items()}
    save_file(state, str(path))


def save_iteration_result(
    path: os.PathLike[str] | str,
    result,
    *,
    config: Mapping[str, Any],
    arm_manifest: Mapping[str, Any],
    source_files: Mapping[str, str] | None = None,
) -> Path:
    """Write a complete one-iteration result and the existing extractor compatibility keys."""
    with atomic_run_directory(path) as temporary:
        write_json(temporary / "config.json", dict(config))
        write_json(temporary / "arm_manifest.json", dict(arm_manifest))
        write_json(temporary / "reco_preprocessing.json", result.reco_preprocessor.payload())
        write_json(temporary / "truth_preprocessing.json", result.truth_preprocessor.payload())
        _save_safetensors(temporary / "step1_model.safetensors", result.step1_model)
        _save_safetensors(temporary / "step2_model.safetensors", result.step2_model)
        np.save(temporary / "weights_push.npy", result.push, allow_pickle=False)
        np.save(temporary / "weights_pull.npy", result.pull, allow_pickle=False)
        np.save(temporary / "mc_indices.npy", result.row_index, allow_pickle=False)
        write_npz_atomic(
            temporary / "extraction_compat.npz",
            w_push=result.push,
            mc_indices=result.row_index,
            estimator_fingerprint=np.asarray(
                result.receipt["dataset_manifest"]["estimator_fingerprint"]
            ),
            recipe_fingerprint=np.asarray(result.receipt["recipe_fingerprint"]),
        )
        receipt = dict(result.receipt)
        receipt["environment"] = environment_receipt()
        package_dir = Path(__file__).resolve().parent
        automatic_sources = {
            str(source.relative_to(package_dir)): file_sha256(source)
            for source in sorted(package_dir.glob("*.py"))
        }
        automatic_sources.update(dict(source_files or {}))
        receipt["source_files"] = automatic_sources
        receipt["git"] = git_state(package_dir)
        receipt["outputs"] = {}
        for output in sorted(temporary.iterdir()):
            if output.is_file() and output.name != "receipt.json":
                receipt["outputs"][output.name] = {
                    "bytes": output.stat().st_size,
                    "sha256": file_sha256(output),
                }
        # The receipt is the final completeness marker.
        write_json(temporary / "receipt.json", receipt)
    return Path(path).resolve()


def load_model_strict(path: os.PathLike[str] | str, model) -> None:
    try:
        from safetensors.torch import load_file
    except ImportError as exc:
        raise RuntimeError("safetensors is required; pickle checkpoint loading is forbidden") from exc
    state = load_file(str(path), device="cpu")
    expected = model.state_dict()
    if set(state) != set(expected):
        missing = sorted(set(expected) - set(state))
        extra = sorted(set(state) - set(expected))
        raise ValueError(f"checkpoint tensor-key mismatch: missing={missing}, extra={extra}")
    wrong = {
        key: (tuple(state[key].shape), tuple(expected[key].shape))
        for key in state
        if tuple(state[key].shape) != tuple(expected[key].shape)
    }
    if wrong:
        raise ValueError(f"checkpoint tensor-shape mismatch: {wrong}")
    model.load_state_dict(state, strict=True)
