"""Load the pinned 2D driver's functions (never its ``main``) and the prototypes.

The driver is imported from this worktree's file after checking that its git
blob equals the blob at the lane's base commit, so a benchmark can never time
or verify against an edited copy. Importing the module runs only its top-level
imports (``argparse``, ``math``, ``array``, ``numpy``, ``ROOT``) and constants.
"""

import importlib.util
import os
import subprocess
import sys

BASE = "5ac9706a21e8a5ac8863a65fd7623d8ab8d22269"
DRIVER_REL = "2d-unfolding/unfold_2d_omnifold_unbinned.py"
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = subprocess.run(["git", "-C", HERE, "rev-parse", "--show-toplevel"],
                      capture_output=True, text=True, check=True).stdout.strip()


def _blob(spec):
    return subprocess.run(["git", "-C", REPO] + spec, capture_output=True, text=True,
                          check=True).stdout.strip()


def load_driver():
    path = os.path.join(REPO, DRIVER_REL)
    pinned = _blob(["rev-parse", f"{BASE}:{DRIVER_REL}"])
    actual = _blob(["hash-object", path])
    if pinned != actual:
        raise RuntimeError(f"{DRIVER_REL} blob {actual} != pinned {pinned} at {BASE}")
    spec = importlib.util.spec_from_file_location("pinned_unfold_2d", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.__pinned_blob__ = pinned
    return mod


def load_proto(name):
    proto_dir = os.path.join(os.path.dirname(HERE), "proto")
    if proto_dir not in sys.path:
        sys.path.append(proto_dir)
    return importlib.import_module(name)
