#!/usr/bin/env python3
"""Run a frozen 2D driver with THIS checkout's OmniFold helper (RE-2 reference runs).

    re2_with_helper.py DRIVER.py [driver arguments ...]

``driver_p1.py`` and the production driver insert a fixed cluster path for the helper before importing it
(OI-136). Importing the helper from this checkout first makes that import reuse it (``sys.modules``), so a
reference run and an ``re2_driver.py`` run use the same helper bytes, and the OI-136 guard sees one checkout.
The driver itself runs unchanged, as ``__main__``. The helper's path and sha256 are in the driver's own output
(``omnifoldHelperFile``, ``omnifoldHelperSha256``).
"""
import runpy
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "unbinned_unfolding" / "python"))
import omnifold  # noqa: E402,F401

if len(sys.argv) < 2:
    sys.exit("usage: re2_with_helper.py DRIVER.py [driver arguments ...]")
driver = str(Path(sys.argv[1]).resolve())
sys.argv = [Path(driver).name] + sys.argv[2:]
runpy.run_path(driver, run_name="__main__")
