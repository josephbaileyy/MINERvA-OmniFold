"""Load the exported pretrained state into the Keras port, refusing partial coverage.

Stage two of the initialization. `export_pretrained_state.py` runs in the torch
environment and writes a hashed `.npz`; this runs in the TensorFlow environment and
copies it into `PET2Port` by name.

**It refuses rather than warns.** A silently partial initialization is the worst
available failure mode here: the arm would train, converge to something, and be
reported as "the pretrained arm" while some fraction of it started from Keras'
initializers instead of his checkpoint. Every variable must be covered, every array
must be consumed, and every shape must match, or this raises.

The one thing it does NOT do is decide which tensors were pretrained. That was
decided by his own filter in stage one and is recorded in the manifest; here every
exported tensor is copied, because the exported state already IS the state his
fine-tuning starts from.

NOT CITABLE FOR any performance claim.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from keras_backend import select_keras_backend

select_keras_backend()

import pet2_keras_port as port  # noqa: E402


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_state_into(model: Any, state_npz: Path,
                    manifest: Path | None = None) -> dict[str, Any]:
    """Copy every exported tensor into `model`, or raise saying exactly what failed."""
    with np.load(state_npz) as blob:
        arrays = {name: blob[name] for name in blob.files}

    inventory = dict(port.parameter_inventory(model))
    missing = sorted(set(inventory) - set(arrays))
    unused = sorted(set(arrays) - set(inventory))
    if missing or unused:
        raise ValueError(
            "pretrained state does not cover the model exactly. "
            f"{len(missing)} model variables have no array "
            f"(first: {missing[:4]}); {len(unused)} arrays match no variable "
            f"(first: {unused[:4]}). A partial initialization would train and be "
            "reported as the pretrained arm."
        )

    mismatched = [
        (name, tuple(inventory[name].shape), tuple(arrays[name].shape))
        for name in sorted(inventory)
        if tuple(inventory[name].shape) != tuple(arrays[name].shape)
    ]
    if mismatched:
        raise ValueError(f"shape mismatches on {len(mismatched)}: {mismatched[:4]}")

    for name, variable in inventory.items():
        variable.assign(arrays[name].astype(variable.dtype.as_numpy_dtype))

    # Verify the copy rather than trusting `assign`, in the dtype it landed in.
    worst = 0.0
    for name, variable in inventory.items():
        target = arrays[name].astype(variable.dtype.as_numpy_dtype)
        worst = max(worst, float(np.max(np.abs(variable.numpy() - target))))

    record: dict[str, Any] = {
        "state_npz": str(state_npz),
        "state_npz_sha256": sha256(state_npz),
        "tensors_loaded": len(inventory),
        "parameters_loaded": int(sum(int(np.prod(v.shape)) for v in inventory.values())),
        "worst_absolute_difference_after_assign": worst,
        "exact": worst == 0.0,
        "dtype": str(next(iter(inventory.values())).dtype.name),
    }
    if manifest is not None:
        record["manifest"] = json.loads(Path(manifest).read_text())
    return record


def build_pretrained_port(state_npz: Path, manifest: Path,
                          dtype: str = "float32") -> tuple[Any, dict[str, Any]]:
    """Build `PET2Port` at the manifest's own settings and initialize it.

    The settings come from the manifest rather than from a constant here, so the
    model that is initialized cannot drift from the model the state was exported
    for. A mismatch then shows up as a coverage failure, which is loud.
    """
    meta = json.loads(Path(manifest).read_text())
    settings = dict(meta["settings"])
    settings.pop("use_int", None)
    settings.pop("local_int", None)
    model = port.PET2Port(**settings, dtype=dtype, **meta["preset"])
    # Build the variables before transfer: an unbuilt Keras weight is not in the
    # inventory, and its absence would read as a coverage failure for the wrong
    # reason.
    record = load_state_into(model, state_npz, manifest)
    record["settings"] = settings
    record["preset"] = meta["preset"]
    record["checkpoint_sha256"] = meta["checkpoint_sha256"]
    return model, record
