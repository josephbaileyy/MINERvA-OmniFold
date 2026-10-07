"""Validate the approved Adam gate without changing model or optimizer math."""

from __future__ import annotations

from typing import Any

import numpy as np

from compatibility_preflight import compare


def key_bias_index(model: Any) -> int:
    """Identify only the structurally bound four-head attention key bias."""
    from typed_descriptor_keras import require_tensorflow

    tf = require_tensorflow()
    if not isinstance(model.attention, tf.keras.layers.MultiHeadAttention):
        raise ValueError("Expected the frozen attention layer")
    bias = model.attention.key_dense.bias
    if tuple(bias.shape) != (4, 8) or model.count_params() != 17329:
        raise ValueError("Unexpected key bias shape or model parameter inventory")
    if len(model.weights) != 42 or len(model.trainable_variables) != 42:
        raise ValueError("Unexpected model variable inventory")
    if any(a is not b for a, b in zip(model.weights, model.trainable_variables)):
        raise ValueError("Weight and gradient order differ")
    indices = [i for i, variable in enumerate(model.weights) if variable is bias]
    if len(indices) != 1 or indices[0] != 27:
        raise ValueError("Key bias is absent or ambiguous")
    return indices[0]


def compare_named(
    left: dict[str, Any],
    right: dict[str, Any],
    *,
    exact: bool = False,
    excluded: str | None = None,
) -> float:
    """Check complete tensor inventories, allowing one explicit weight exception."""
    if left.keys() != right.keys():
        raise ValueError("Tensor inventory differs")
    errors = []
    for name in left:
        # Even the redundant coordinate must have finite equal-shaped values.
        a, b = np.asarray(left[name]), np.asarray(right[name])
        if a.shape != b.shape or not np.isfinite(a).all() or not np.isfinite(b).all():
            raise ValueError("Nonfinite tensor or shape mismatch")
        if name != excluded:
            errors.append(compare(a, b, exact=exact))
    return max(errors, default=0.0)


def validate(
    model: Any,
    traces: list[dict[str, Any]],
    replays: list[dict[str, Any]],
    *,
    exact_cpu: bool,
) -> dict[str, Any]:
    """Require native parity, gradient agreement and common-operand Adam replay.

    The caller constructs replay operands directly from the captured derivatives;
    their values are also bound here, so substituting an operand fails closed.
    """
    index = key_bias_index(model)
    if len(traces) != 2 or len(replays) != 2:
        raise ValueError("Both native trajectories are required")
    initial_keys = {f"weight_{i}" for i in range(42)} | {f"slot_{i}" for i in range(86)}
    for trace in traces:
        if len(trace["states"]) != 3 or any(
            set(s) != initial_keys for s in trace["states"]
        ):
            raise ValueError("Incomplete native optimizer state")
        if trace["instrumentation_exact"] is not True:
            raise ValueError("Instrumentation differs from unchanged execution")
        compare_named(trace["initial"], trace["repeated"], exact=True)
        compare_named(trace["initial"], trace["graph"])
    compare_named(traces[0]["states"][0], traces[1]["states"][0], exact=True)
    for phase in ("initial", "second"):
        compare_named(traces[0][phase], traces[1][phase], exact=exact_cpu)
    compare(traces[0]["prediction"], traces[1]["prediction"], exact=exact_cpu)
    raw_bias_errors = []
    for step in (1, 2):
        a, b = (t["states"][step] for t in traces)
        compare_named(
            a, b, exact=exact_cpu, excluded=None if exact_cpu else f"weight_{index}"
        )
        raw_bias_errors.append(
            float(
                np.max(
                    np.abs(
                        np.asarray(a[f"weight_{index}"], dtype=float)
                        - b[f"weight_{index}"]
                    )
                )
            )
        )
    common_error = 0.0
    for origin, replay in enumerate(replays):
        native = traces[origin]
        if any(
            len(replay[name]) != 2
            for name in ("cpu", "candidate", "float64", "gradients")
        ):
            raise ValueError("Incomplete two-step replay")
        if any(
            set(state) != {f"weight_{i}" for i in range(42)}
            for state in replay["float64"]
        ):
            raise ValueError("Incomplete float64 replay")
        compare_named(
            replay["initial"],
            {f"weight_{i}": native["states"][0][f"weight_{i}"] for i in range(42)},
            exact=True,
        )
        for step, phase in enumerate(("initial", "second")):
            compare_named(
                replay["gradients"][step],
                {f"gradient_{i}": native[phase][f"gradient_{i}"] for i in range(42)},
                exact=True,
            )
            a, b = replay["cpu"][step], replay["candidate"][step]
            if set(a) != initial_keys or set(b) != initial_keys:
                raise ValueError("Incomplete replay optimizer state")
            common_error = max(common_error, compare_named(a, b, exact=exact_cpu))
            compare_named(native["states"][step + 1], (a, b)[origin], exact=True)
            compare(
                native["states"][step + 1][f"weight_{index}"],
                replay["float64"][step][f"weight_{index}"],
            )
    return {
        "terminal": "PASS",
        "key_bias_index": index,
        "key_bias_shape": [4, 8],
        "raw_key_bias_max_abs_by_step": raw_bias_errors,
        "common_operand_max_abs": common_error,
    }
