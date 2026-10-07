"""Disable NumPy's optional SVE probe, which launches `lscpu`, before anything imports it.

`numpy.testing._private.utils` runs `check_support_sve()` at import time, and that calls
`subprocess.run('lscpu', ...)`. On Perlmutter's tensorflow/2.15.0 the chain is
`omnifold` -> Horovod / `tensorflow.python.keras` -> `scipy.sparse` -> `numpy.testing`, so every
run of the historical engine launches it. The OI-136 guard (`mnv_guarded_run.py`) refuses the
launch because `lscpu` is not on its leaf-tool list, and the guard says explicitly not to widen
that list to make a launcher pass.

This follows the precedent of `direct_token_comparison/calibration_measure.py` (2026-09-10,
`SOURCE_AUDIT_INTERRUPTION-20260910.md`): take NumPy's own `OSError` fallback without launching
the tool. SVE is an ARM extension, so on x86_64 the fallback's answer (`False`) is the answer the
probe would have given; on any other machine this refuses instead.
"""

from __future__ import annotations

import platform
import shutil
import subprocess
import sys
from typing import Any
from unittest.mock import patch


def disable_numpy_sve_probe() -> dict[str, Any]:
    """Import `numpy.testing` with the `lscpu` launch replaced by NumPy's own fallback."""
    if "numpy.testing" in sys.modules:
        utils = sys.modules.get("numpy.testing._private.utils")
        return {"already_imported": True,
                "supports_sve": getattr(utils, "_SUPPORTS_SVE", None)}
    if platform.machine() != "x86_64" and shutil.which("lscpu") is not None:
        raise RuntimeError("the optional SVE probe cannot be disabled on this platform")
    real_run = subprocess.run
    refused: list[Any] = []

    def without_optional_probe(command: Any, *args: Any, **kwargs: Any) -> Any:
        if command == "lscpu" or (isinstance(command, (list, tuple)) and command[:1] == ["lscpu"]):
            refused.append(command)
            raise FileNotFoundError("numpy's optional SVE probe disabled (x86_64 has no SVE)")
        return real_run(command, *args, **kwargs)

    with patch("subprocess.run", side_effect=without_optional_probe):
        import numpy.testing  # noqa: F401
    utils = sys.modules.get("numpy.testing._private.utils")
    return {"already_imported": False, "machine": platform.machine(),
            "probe_launches_refused": [repr(c) for c in refused],
            "supports_sve": getattr(utils, "_SUPPORTS_SVE", None),
            "precedent": "direct_token_comparison/calibration_measure.py (2026-09-10)"}
