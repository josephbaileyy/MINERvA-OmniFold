#!/usr/bin/env python3
"""Run one extracted bootstrap_nd.py with its repository imports taken from a pinned directory.

Both versions of `bootstrap_nd.py` under test put the canonical cluster checkout at sys.path[0]
(`_ND = "/pscratch/.../MINERvA-OmniFold/nd-unfolding"`; OI-136). Run as they stand from a clean clone,
they would import `omnifold_nn_core` and `xsec_nd` from that checkout, and the reproduction would
test whatever the checkout holds today. This wrapper imports both modules from `--lib` first, so the
script's later `sys.path.insert(0, _ND)` finds them already loaded. It then runs the script unchanged,
with `runpy`, as `__main__`.

After the run it writes a provenance record and exits 3 if any loaded module's file is under
`--forbidden-root`. The script's own exit status is kept. Exit 0 means the script returned and no
module came from the forbidden root.
"""
import argparse
import json
import os
import runpy
import sys
from pathlib import Path


def loaded_under(root):
    root = os.path.realpath(root) + os.sep
    hits = []
    for name, mod in list(sys.modules.items()):
        path = getattr(mod, "__file__", None)
        if path and os.path.realpath(path).startswith(root):
            hits.append(f"{name}={path}")
    return sorted(hits)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", required=True)
    ap.add_argument("--lib", required=True)
    ap.add_argument("--forbidden-root", required=True)
    ap.add_argument("--provenance", required=True)
    ap.add_argument("script_args", nargs=argparse.REMAINDER)
    a = ap.parse_args(argv)
    args = a.script_args[1:] if a.script_args[:1] == ["--"] else a.script_args

    lib = os.path.realpath(a.lib)
    sys.path.insert(0, lib)
    import omnifold_nn_core  # noqa: F401  (pre-import: the script's own insert cannot re-import)
    import xsec_nd  # noqa: F401
    pre = {m: os.path.realpath(sys.modules[m].__file__) for m in ("omnifold_nn_core", "xsec_nd")}

    sys.argv = [a.script, *args]
    code, error = 0, None
    try:
        runpy.run_path(a.script, run_name="__main__")
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else (0 if exc.code is None else 1)
    except Exception as exc:  # recorded, not hidden
        code, error = 1, f"{type(exc).__name__}: {exc}"

    forbidden = loaded_under(a.forbidden_root)
    try:
        import lightgbm
        lgbm = lightgbm.__version__
    except Exception as exc:
        lgbm = f"unavailable: {exc}"
    import numpy
    record = {
        "schema": "oi160-repro-provenance/1",
        "script": os.path.realpath(a.script),
        "script_args": args,
        "preimported_from": pre,
        "preimported_under_lib": all(p.startswith(lib + os.sep) for p in pre.values()),
        "modules_under_forbidden_root": forbidden,
        "lightgbm": lgbm,
        "numpy": numpy.__version__,
        "python": sys.version.split()[0],
        "affinity_cpus": len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else None,
        "omp_num_threads_env": os.environ.get("OMP_NUM_THREADS"),
        "script_exit": code,
        "script_error": error,
    }
    Path(a.provenance).write_text(json.dumps(record, indent=2) + "\n")
    if forbidden or not record["preimported_under_lib"]:
        print(f"[repro_run] REFUSED: modules from the forbidden root or outside --lib: {forbidden or pre}")
        return 3
    return code


if __name__ == "__main__":
    sys.exit(main())
