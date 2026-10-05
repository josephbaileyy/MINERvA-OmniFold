"""Pick the Keras that can build Keras-2 code, from what is installed.

Extracted from ``calibrate_cost.py`` so the two environments' opposite requirements
are decided in exactly one place. A second copy of this rule is a second
implementation of it, and they drift.
"""

from __future__ import annotations

import os
from typing import Any


def select_keras_backend() -> dict[str, Any]:
    """Set ``TF_USE_LEGACY_KERAS`` only where it is the right answer.

    The vendored PET -- and this port, which must run beside it -- is Keras-2 code.
    Two environments satisfy it and they need OPPOSITE settings, which an
    unconditional ``setdefault`` gets wrong in one of them:

    * TF 2.16 with Keras 3 plus the ``tf_keras`` shim (this Mac) -- the variable is
      REQUIRED, or ``tf.keras`` resolves to Keras 3 and the model cannot build;
    * TF 2.15 with Keras 2 bundled and no ``tf_keras`` (Perlmutter's
      ``tensorflow/2.15.0``) -- the variable is HARMFUL: TF then looks for a
      ``tf_keras`` package that is not there and ``tensorflow.keras`` disappears.

    Measured 2026-09-18: hardcoding it failed GPU job 58526592 in 18 s with
    ``ModuleNotFoundError: No module named 'tensorflow.keras'``, having passed every
    local check first. So the choice is made from what is installed, and returned for
    the receipt so the environment is attributable rather than assumed.
    """
    import importlib.util

    shim = importlib.util.find_spec("tf_keras") is not None
    if shim:
        os.environ.setdefault("TF_USE_LEGACY_KERAS", "1")
    return {
        "tf_keras_shim_available": shim,
        "tf_use_legacy_keras": os.environ.get("TF_USE_LEGACY_KERAS"),
        "reason": (
            "Keras-3 TensorFlow with the tf_keras shim: the shim is selected."
            if shim else
            "no tf_keras shim: assuming TensorFlow bundles Keras 2, which the vendored "
            "PET needs. If tf.keras turns out to be Keras 3 the model will fail to build "
            "and that is the documented, loud failure."
        ),
    }


def record_versions() -> dict[str, Any]:
    """Version strings for the receipt, after the backend choice is made.

    ``tf.keras.__version__`` is the one that matters and it is NOT ``keras.__version__``:
    under the shim this Mac reports a top-level ``keras`` of 3.15.0 while ``tf.keras`` is
    the 2.x ``tf_keras`` that actually builds the model. Recording the top-level number
    would attribute the run to a Keras that never touched it.
    """
    import tensorflow as tf

    import importlib

    # `tf.keras` is a re-export shim (`tf_keras.api._v2.keras` under the shim,
    # `keras.api._v2.keras` when TF bundles Keras 2) and carries no `__version__`
    # of its own, so the version is read off the ROOT package it re-exports.
    root_name = tf.keras.__name__.split(".")[0]
    try:
        root_version = getattr(importlib.import_module(root_name), "__version__", None)
    except Exception:  # pragma: no cover - environment-dependent
        root_version = None
    try:
        import keras as _standalone

        standalone = getattr(_standalone, "__version__", None)
    except Exception:  # pragma: no cover - environment-dependent
        standalone = None
    return {
        "tensorflow": tf.__version__,
        "tf_keras_module": tf.keras.__name__,
        "tf_keras_root": root_name,
        "tf_keras_version": root_version,
        "standalone_keras": standalone,
    }


# --------------------------------------------------------------------------- #
# The production precision policy, enforced rather than assumed.
# --------------------------------------------------------------------------- #
#
# `run_typed_token_comparison.PRECISION_POLICY` is the frozen policy for this
# project and requires `tf32_enabled: False`. NONE of this package's drivers
# enforced it, and on an A100 TensorFlow enables TF32 for matmuls by DEFAULT. So
# every GPU measurement this lane has taken -- the throughput, the memory, and
# the XLA-versus-eager comparisons -- ran with TF32 on, against a policy that
# forbids it.
#
# Two consequences, both measured rather than inferred once this landed:
#
#   * TF32 carries 10 explicit mantissa bits, so it perturbs a matmul at the 1e-3
#     level. That is the scale at which the production validation's forward and
#     gradient checks failed, and it is why they failed by thousands of times
#     their limit on GPU while failing by ~2x on a CPU, where there is no TF32.
#   * TF32 matmuls are several times faster than true FP32 on A100, so the
#     timings -- and the campaign cost derived from them -- were optimistic.
#
# A policy that is documented and not applied is not a policy.
PRODUCTION_PRECISION_POLICY = {
    "tf32_enabled": False,
    "determinism_enabled": True,
    "mixed_precision_policy": "float32",
    "floatx": "float32",
}


def observed_precision_policy() -> dict[str, Any]:
    """What the running process is ACTUALLY doing, not what it intended."""
    import importlib

    import tensorflow as tf

    config = importlib.import_module("tensorflow.python.framework.config")
    return {
        "tf32_enabled": bool(
            tf.config.experimental.tensor_float_32_execution_enabled()),
        "determinism_enabled": bool(config.is_op_determinism_enabled()),
        "mixed_precision_policy": tf.keras.mixed_precision.global_policy().name,
        "floatx": tf.keras.backend.floatx(),
    }


def configure_production_precision(strict: bool = True) -> dict[str, Any]:
    """Apply the frozen policy, then VERIFY it, and fail closed if it did not take.

    Applying and verifying are separate steps on purpose: `enable_..._execution`
    is a request, and a request that silently did nothing is exactly the failure
    that let TF32 into every measurement so far.
    """
    import tensorflow as tf

    tf.config.experimental.enable_tensor_float_32_execution(False)
    tf.config.experimental.enable_op_determinism()
    tf.keras.mixed_precision.set_global_policy("float32")
    tf.keras.backend.set_floatx("float32")
    observed = observed_precision_policy()
    if strict and observed != PRODUCTION_PRECISION_POLICY:
        raise RuntimeError(
            "precision policy did not take: wanted "
            f"{PRODUCTION_PRECISION_POLICY}, observing {observed}"
        )
    return observed
