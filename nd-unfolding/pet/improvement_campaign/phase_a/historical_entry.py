"""Call a historical module's `main()` under the OI-136 guard, unmodified.

The guard's entrypoint must live in `--expect-root` (the campaign checkout); the historical
module is IMPORTED from the pinned 68cf9d29 checkout, which the launcher passes as `--allow`.
This reproduces `python <that script> <args>` -- the script's directory first on `sys.path`,
`sys.argv` as the script would see it -- except that NumPy's optional SVE probe is disabled first
(`numpy_probe.py`), because the guard refuses the `lscpu` it launches. What was disabled is
printed as one JSON line so it lands in the job log.
"""

from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path

from numpy_probe import disable_numpy_sve_probe


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--module-dir", type=Path, required=True)
    parser.add_argument("--module", required=True)
    parser.add_argument("rest", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    rest = args.rest[1:] if args.rest[:1] == ["--"] else args.rest
    probe = disable_numpy_sve_probe()
    module_dir = args.module_dir.resolve()
    sys.path.insert(0, str(module_dir))
    sys.argv = [str(module_dir / f"{args.module}.py"), *rest]
    module = importlib.import_module(args.module)
    print(json.dumps({"historical_entry": {"module": args.module, "file": module.__file__,
                                           "numpy_sve_probe": probe}}), flush=True)
    result = module.main()
    return int(result or 0)


if __name__ == "__main__":
    sys.exit(main())
