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
