"""Run the campaign's pytest files as a guarded entrypoint (the guard takes a script, not -m).

NumPy's SVE probe is disabled first (see `numpy_probe.py`). Arguments are passed to pytest.
"""

from __future__ import annotations

import sys

from numpy_probe import disable_numpy_sve_probe

if __name__ == "__main__":
    print({"numpy_sve_probe": disable_numpy_sve_probe()}, flush=True)
    import pytest
    sys.exit(pytest.main(sys.argv[1:]))
