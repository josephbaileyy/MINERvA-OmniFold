#!/usr/bin/env python3
"""Run one committed producer as a script and record which module files it imported.

    python3 _launch.py --record R.json -- <producer.py> [producer args...]

The producer runs exactly as ``python3 <producer.py> ...`` would (``__main__``, ``sys.argv``, ``sys.path[0]`` =
its directory); afterwards the realpath of every imported module file is written to ``R.json`` so the harness
can refuse a run that imported project code from outside the checkout under test (OI-136). Nothing is printed,
so the producer's own stdout/stderr stay byte-for-byte its own.
"""
import json
import os
import runpy
import site
import sys


def main() -> int:
    split = sys.argv.index("--")
    opts, rest = sys.argv[1:split], sys.argv[split + 1:]
    record = opts[opts.index("--record") + 1]
    script = os.path.abspath(rest[0])
    sys.argv = [script] + rest[1:]
    sys.path[0] = os.path.dirname(script)
    code = 0
    try:
        runpy.run_path(script, run_name="__main__")
    except SystemExit as exc:
        if exc.code is None:
            code = 0
        elif isinstance(exc.code, int):
            code = exc.code
        else:
            print(exc.code, file=sys.stderr)
            code = 1
    finally:
        files = sorted({os.path.realpath(m.__file__) for m in list(sys.modules.values())
                        if isinstance(getattr(m, "__file__", None), str)})
        user_site = site.getusersitepackages() if hasattr(site, "getusersitepackages") else None
        with open(record, "w") as fh:
            json.dump({"script": script, "modules": files, "prefix": sys.prefix, "base_prefix": sys.base_prefix,
                       "user_site": user_site, "executable": sys.executable}, fh, indent=1)
    sys.stdout.flush()
    sys.stderr.flush()
    return code


if __name__ == "__main__":
    raise SystemExit(main())
