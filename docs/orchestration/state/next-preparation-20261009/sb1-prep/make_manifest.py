#!/usr/bin/env python3
"""Write ``manifest/expected-code.json``: the sha256 of every file an SB1 launch depends on.

    python3 make_manifest.py            # writes the manifest from the working tree
    python3 make_manifest.py --check    # exit 1 unless the committed manifest is current

Three groups, all checked at HEAD by ``sb1_admit.py``: ``modules``, exactly the files
``sb1_run.py`` executes (and strict mode requires ``--expect`` to state); ``guard``, the OI-136
wrapper and its shim; ``launch``, the scripts and the frozen plan. The manifest names contents,
not a commit, so the package commit that carries it can be named by the admission record.
"""

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
PKG = HERE.relative_to(REPO).as_posix()
N2 = "2d-unfolding/uq/coverage_fixed_truth/n2"
MODULES = (f"{PKG}/sb1_run.py", f"{PKG}/branch_select.py", f"{N2}/__init__.py", f"{N2}/execution.py",
           "2d-unfolding/unfold_2d_omnifold_unbinned.py", "unbinned_unfolding/python/omnifold.py")
GUARD = ("nd-unfolding/mnv_guarded_run.py", "nd-unfolding/mnv_guard_shim/sitecustomize.py",
         "nd-unfolding/mnv_guard_shim/scan_argv.py", "nd-unfolding/mnv_guard_shim/wrapper_exec.py")
LAUNCH = tuple(f"{PKG}/{p}" for p in (
    "sb1_admit.py", "sb1_hash.py", "sb1_verify.py", "launch/launch-spec.json",
    "launch/sb1_submit.sh", "launch/sb1_hash.sbatch", "launch/sb1_unfold.sbatch",
    "launch/sb1_identity.sbatch", "launch/sb1_cv.sbatch"))


def digests(paths):
    return {p: hashlib.sha256((REPO / p).read_bytes()).hexdigest() for p in paths}


def build():
    shim_bin = sorted(p.relative_to(REPO).as_posix()
                      for p in (REPO / "nd-unfolding/mnv_guard_shim/bin").rglob("*") if p.is_file())
    return {"schema": "sb1-expected-code/1",
            "note": "contents only; the admission record names the commit (sb1_admit.py)",
            "modules": digests(MODULES), "guard": digests(GUARD + tuple(shim_bin)),
            "launch": digests(LAUNCH)}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    out = HERE / "manifest" / "expected-code.json"
    text = json.dumps(build(), indent=1, sort_keys=True) + "\n"
    if "--check" in argv:
        current = out.read_text() if out.exists() else ""
        print("manifest current" if current == text else "manifest OUT OF DATE")
        return 0 if current == text else 1
    out.parent.mkdir(exist_ok=True)
    out.write_text(text)
    print(f"wrote {out.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
