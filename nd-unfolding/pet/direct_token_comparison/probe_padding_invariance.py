"""Test whether padded token slots change the computed gradients on one device.

Stage D1b of ``CROSSDEVICE_DIAGNOSTIC_SPECIFICATION-20260915.md``, reached under
its Branch B. D1 established that in ``variable/direct`` the CPU and GPU
*gradients* disagree (worst 1.34e-05) while identical-operand Adam replay agrees
across devices (2.98e-08), and that the disagreement grows with token geometry
across the four reached cases. Geometry conflates two things, though: that case
has both many more real objects and far more padded slots than the others.

A cross-device comparison cannot separate them, so this probe removes the device
from the question and varies padding alone. It appends token slots that
are masked off -- so the active object set, the counts and the enabled flags are
all bitwise unchanged -- and recomputes on the **same** device with the **same**
weights. In exact arithmetic the prediction and every gradient must be identical,
because a masked slot contributes nothing.

Any difference is therefore a padding-width effect, meaning the computation
depends on batch composition. The ``pooled`` route is run as a control: it
reduces each family to one token regardless of slot count, so it should be far
less sensitive, and a large pooled change would indicate a defect in this probe
rather than in the model.

CPU-only and tiny (four rows). It uses no allocation, trains nothing, reads no
detector source, and measures no learning performance.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
from typing import Any

import numpy as np


def _install_paths(checkout: Path) -> list[str]:
    """Put the named checkout's module directories on the import path.

    ``OI-136`` is about a hardcoded root silently winning ``sys.path[0]``. Here the
    root is supplied rather than hardcoded, and every resolved module file is
    reported in the receipt so the origin is evidence instead of an assumption.
    """
    roots = [
        checkout / "nd-unfolding" / "pet",
        checkout / "nd-unfolding" / "pet" / "direct_token_comparison",
    ]
    for root in reversed(roots):
        if not root.is_dir():
            raise ValueError(f"Not a directory: {root}")
        sys.path.insert(0, str(root))
    return [str(root) for root in roots]


def widen_padding(inputs: dict[str, Any], families: Any, extra: int) -> dict[str, Any]:
    """Append ``extra`` masked slots per event, leaving the active set unchanged.

    Slots are appended with ``token_mask=False`` and every field mask ``False``, so
    the family encoders treat them as absent. Segment ids stay nondecreasing, which
    ``packed_row_splits`` asserts.
    """
    rows = len(inputs["generic_mask"])
    widened = {key: value.copy() for key, value in inputs.items()}
    for family in families:
        prefix = family.name
        segment = widened[f"{prefix}_segment_ids"]
        values = widened[f"{prefix}_values"]
        masks = widened[f"{prefix}_masks"]
        token_mask = widened[f"{prefix}_token_mask"]
        added_segment = np.repeat(np.arange(rows, dtype=np.int32), extra)
        combined_segment = np.concatenate([segment, added_segment])
        order = np.argsort(combined_segment, kind="stable")
        pad_values = np.zeros((rows * extra, values.shape[1]), values.dtype)
        pad_masks = np.zeros((rows * extra, masks.shape[1]), masks.dtype)
        pad_token = np.zeros(rows * extra, token_mask.dtype)
        widened[f"{prefix}_values"] = np.concatenate([values, pad_values])[order]
        widened[f"{prefix}_masks"] = np.concatenate([masks, pad_masks])[order]
        widened[f"{prefix}_token_mask"] = np.concatenate([token_mask, pad_token])[order]
        widened[f"{prefix}_segment_ids"] = combined_segment[order]
        # counts and enabled are untouched: masked slots contribute no count.
    return widened


def evaluate(
    tf: Any, model: Any, inputs: dict[str, Any], target: Any
) -> dict[str, Any]:
    """Return the prediction and every weight gradient for one forward/backward."""
    tensors = {key: tf.convert_to_tensor(value) for key, value in inputs.items()}
    with tf.GradientTape() as tape:
        prediction = model(tensors, training=True)
        loss = tf.reduce_mean(
            tf.nn.sigmoid_cross_entropy_with_logits(
                labels=tf.convert_to_tensor(target), logits=prediction
            )
        )
    gradients = tape.gradient(loss, model.trainable_variables)
    if any(gradient is None for gradient in gradients):
        raise ValueError("Disconnected gradient")
    return {
        "prediction": np.asarray(prediction),
        "loss": float(loss),
        "gradients": [np.asarray(gradient) for gradient in gradients],
    }


def _token_width(tf: Any, model: Any, inputs: dict[str, Any]) -> list[int]:
    """Report the routed token geometry actually seen by attention."""
    tensors = {key: tf.convert_to_tensor(value) for key, value in inputs.items()}
    _, presence, _ = model.route_tokens(tensors)
    return [int(dimension) for dimension in np.asarray(presence).shape]


def run(checkout: Path, extra: int) -> dict[str, Any]:
    """Compare natural and widened padding for both routes on one device."""
    installed = _install_paths(checkout)
    os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")
    import compatibility_preflight as preflight
    import typed_descriptors as typed
    import typed_token_comparison as comparison

    tf = __import__("typed_descriptor_keras").require_tensorflow()
    tf.keras.utils.set_random_seed(2401)
    tf.config.experimental.enable_op_determinism()
    normalization, cases = preflight.fixtures()
    inputs = cases["variable"]
    rows = len(inputs["generic_mask"])
    rng = np.random.default_rng(99)
    target = rng.integers(0, 2, size=(rows, 1)).astype(np.float32)

    results: dict[str, Any] = {}
    for routing in ("pooled", "direct"):
        tf.keras.utils.set_random_seed(2401)
        model = comparison.build_comparison(normalization, routing=routing)
        model(  # build once so both evaluations share identical weights
            {key: tf.convert_to_tensor(value) for key, value in inputs.items()}
        )
        widened = widen_padding(inputs, typed.FAMILY_CONTRACTS, extra)
        base = evaluate(tf, model, inputs, target)
        wide = evaluate(tf, model, widened, target)
        gradient_errors = [
            float(np.max(np.abs(a.astype(float) - b.astype(float)), initial=0.0))
            for a, b in zip(base["gradients"], wide["gradients"])
        ]
        worst = int(np.argmax(gradient_errors))
        results[routing] = {
            "token_geometry_natural": _token_width(tf, model, inputs),
            "token_geometry_widened": _token_width(tf, model, widened),
            "prediction_max_abs": float(
                np.max(np.abs(base["prediction"] - wide["prediction"]), initial=0.0)
            ),
            "loss_abs_difference": abs(base["loss"] - wide["loss"]),
            "worst_gradient_index": worst,
            "worst_gradient_max_abs": gradient_errors[worst],
            "gradients_bitwise_identical": all(
                np.array_equal(a, b)
                for a, b in zip(base["gradients"], wide["gradients"])
            ),
            "gradient_max_abs_by_index": gradient_errors,
        }
    return {
        "scope": "single-device padding-invariance probe; no GPU, no training, no source",
        "checkout": str(checkout),
        "installed_paths": installed,
        "module_origins": {
            name: getattr(sys.modules[name], "__file__", None)
            for name in (
                "compatibility_preflight",
                "typed_descriptors",
                "typed_token_comparison",
            )
        },
        "device_policy": os.environ.get("CUDA_VISIBLE_DEVICES"),
        "extra_masked_slots_per_event": extra,
        "case": "variable",
        "routes": results,
        "interpretation": (
            "Masked slots must contribute nothing, so any nonzero difference is a "
            "padding-width effect on a single device: the computation depends on batch "
            "composition."
        ),
        "non_claim": (
            "Numerical reproducibility only. This measures no learning performance and "
            "is not evidence for or against any representation."
        ),
    }


def main() -> None:
    """Write the padding-invariance measurement for both routes."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkout", type=Path, required=True)
    parser.add_argument("--extra-slots", type=int, default=32)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.checkout, args.extra_slots)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    for routing, record in result["routes"].items():
        print(
            f"{routing}: geometry {record['token_geometry_natural']} ->"
            f" {record['token_geometry_widened']}"
            f" identical={record['gradients_bitwise_identical']}"
            f" worst_gradient={record['worst_gradient_max_abs']:.6g}"
            f" prediction={record['prediction_max_abs']:.6g}"
        )


if __name__ == "__main__":
    main()
