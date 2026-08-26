#!/usr/bin/env python3
"""Target-only bypass for an unnecessary TensorFlow package-initializer side effect.

The frozen full-event loader imports ``omnifold.dataloader``.  Python ordinarily executes
``omnifold/__init__.py`` first, which imports the TensorFlow training engine even though target
materialization uses only the NumPy-only DataLoader.  The ROOT worker has Python 3.11 and no
TensorFlow; the TensorFlow worker has Python 3.9 and no ROOT.  Retry 2 installs a package shell only
in the target process, then loads and hash-checks the unchanged dataloader module.  Training and
evaluation do not import this support file.
"""

import hashlib
import importlib
import importlib.machinery
import sys
import types
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
PACKAGE_DIR = REPO / "omnifold_nn/omnifold"
DATALOADER = PACKAGE_DIR / "dataloader.py"
EXPECTED_DATALOADER_SHA256 = (
    "bed9e0b39df54b465cb7e2a2600ff819ffb09350665603359bf12a52fdbd734a"
)


def _sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def install_target_dataloader():
    """Load the exact DataLoader module without executing the training package initializer."""
    if "tensorflow" in sys.modules:
        raise SystemExit("[pet-v2-target-import][FAIL] TensorFlow loaded in ROOT target process")
    if "omnifold" in sys.modules or "omnifold.dataloader" in sys.modules:
        raise SystemExit("[pet-v2-target-import][FAIL] omnifold imported before target bypass")
    observed = _sha256(DATALOADER)
    if observed != EXPECTED_DATALOADER_SHA256:
        raise SystemExit(
            f"[pet-v2-target-import][FAIL] dataloader hash {observed} "
            f"!= {EXPECTED_DATALOADER_SHA256}"
        )

    package = types.ModuleType("omnifold")
    package.__file__ = str(PACKAGE_DIR / "__init__.py")
    package.__package__ = "omnifold"
    package.__path__ = [str(PACKAGE_DIR)]
    spec = importlib.machinery.ModuleSpec("omnifold", loader=None, is_package=True)
    spec.submodule_search_locations = [str(PACKAGE_DIR)]
    package.__spec__ = spec
    sys.modules["omnifold"] = package
    module = importlib.import_module("omnifold.dataloader")
    resolved = Path(module.__file__).resolve()
    if resolved != DATALOADER.resolve() or _sha256(resolved) != EXPECTED_DATALOADER_SHA256:
        raise SystemExit(f"[pet-v2-target-import][FAIL] wrong dataloader module: {resolved}")
    if "tensorflow" in sys.modules:
        raise SystemExit("[pet-v2-target-import][FAIL] dataloader import pulled TensorFlow")
    print(
        "[pet-v2-target-import] PASS target-only package initializer bypass; "
        f"dataloader={resolved} sha256={observed}",
        file=sys.stderr,
        flush=True,
    )
    return module.DataLoader
