"""Calculation identity and complete, non-overwriting result directories."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from functools import lru_cache
from pathlib import Path
from types import ModuleType
from typing import Any

ROOT = Path(__file__).resolve().parents[2]


def read_json(path: Path) -> dict[str, Any]:
    """Read a JSON object, refusing non-object configurations."""
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return value


def digest(path: Path) -> str:
    """Hash a file in bounded chunks."""
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def fingerprint(value: Any) -> str:
    """Hash the canonical JSON representation of a contract."""
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, allow_nan=False).encode()
    ).hexdigest()


@lru_cache
def legacy_module(name: str) -> ModuleType:
    """Load a pure calculation from this checkout without changing import paths."""
    if name not in {
        "omnifold_nn_core",
        "xsec_nd",
        "uq_math",
        "mnv_guarded_run",
        "nominal_omnifold",
        "scalar_driver",
        "projection_driver",
    }:
        raise ValueError(f"unsupported calculation module: {name}")
    module_name = f"_production_{name}"
    source = ROOT / "nd-unfolding" / f"{name}.py"
    if name == "nominal_omnifold":
        source = ROOT / "unbinned_unfolding/python/omnifold.py"
    elif name == "scalar_driver":
        source = ROOT / "nd-unfolding/unfold_nd_omnifold_unbinned.py"
    elif name == "projection_driver":
        source = ROOT / "nd-unfolding/project_cov_nd.py"
    spec = importlib.util.spec_from_file_location(module_name, source)
    if spec is None or spec.loader is None:
        raise ImportError(name)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def code_identity(
    scope: str = "scalar", *, backend: str = "cached-lgbm-v1"
) -> dict[str, Any]:
    """Bind calculation dependencies, independently of repository revision.

    Parameters
    ----------
    scope : str
        Calculation family whose implementation and runtime must match.
    backend : str
        Scalar estimator implementation; irrelevant to projection.

    Returns
    -------
    dict
        Source digests, output protocol version and runtime dependencies.
        Documentation and unrelated calculation families are excluded.
    """
    from importlib.metadata import PackageNotFoundError, version

    shared = [
        "production/minerva_production/" + name + ".py"
        for name in ("__init__", "storage", "cli")
    ]
    families = {
        "scalar": [
            "production/minerva_production/scalar.py",
            "production/minerva_production/uncertainty.py",
            "production/unfold_gbdt.py",
            "production/uncertainties.py",
            "production/closure.py",
            "nd-unfolding/xsec_nd.py",
        ],
        "projection": [
            "production/minerva_production/projection.py",
            "production/minerva_production/scalar.py",
            "production/project.py",
            "nd-unfolding/uq_math.py",
        ],
    }
    if scope not in families:
        raise ValueError(f"unknown calculation scope: {scope}")
    paths = shared + families[scope] + ["nd-unfolding/mnv_guarded_run.py"]
    if scope == "scalar":
        engines = {
            "cached-lgbm-v1": "nd-unfolding/omnifold_nn_core.py",
            "nominal-lgbm-v1": "unbinned_unfolding/python/omnifold.py",
        }
        if backend not in engines:
            raise ValueError(f"unknown scalar backend: {backend}")
        paths.append(engines[backend])
    versions: dict[str, str | None] = {}
    packages = ["numpy"]
    if scope == "scalar":
        packages += ["lightgbm", "scikit-learn", "scipy", "joblib", "threadpoolctl"]
    for name in packages:
        try:
            versions[name] = version(name)
        except PackageNotFoundError:
            versions[name] = None
    return {
        "scope": scope,
        "output_schema": 2,
        "sources": {path: digest(ROOT / path) for path in sorted(paths)},
        "versions": versions,
        "python": sys.version,
    }


def provenance() -> dict[str, str]:
    """Record the full checkout revision without making it a resume constraint."""
    revision = subprocess.check_output(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
        text=True,
        env={key: value for key, value in os.environ.items() if key != "GIT_PAGER"},
    ).strip()
    return {"revision": revision}


def check_output(path: Path, identity: dict[str, Any], resume: bool) -> bool:
    """Return true only for a compatible, digest-checked complete result."""
    if not path.exists():
        return False
    if not resume:
        raise FileExistsError(
            f"{path}: output exists; use --resume for a complete match"
        )
    _, record = load_result(path)
    if record["identity"] != identity:
        raise ValueError(f"{path}: resume identity differs (config, input, or code)")
    return True


def save_result(path: Path, arrays: dict[str, Any], record: dict[str, Any]) -> None:
    """Write arrays first and the completion record last; never replace a run."""
    import numpy as np

    path.mkdir(parents=True, exist_ok=False)
    np.savez_compressed(path / "result.npz", **arrays)
    complete = {
        **record,
        "schema": 2,
        "provenance": provenance(),
        "status": "complete",
        "scientific_status": "diagnostic; no publication adoption",
        "result_sha256": digest(path / "result.npz"),
    }
    temporary = path / "record.json.tmp"
    temporary.write_text(
        json.dumps(complete, indent=2, sort_keys=True, allow_nan=False)
    )
    os.replace(temporary, path / "record.json")


def load_result(path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    """Load only complete products whose recorded payload digest still matches."""
    import numpy as np

    record = read_json(path / "record.json")
    if record.get("schema") != 2 or record.get("status") != "complete":
        raise ValueError(f"{path}: missing compatible completion record")
    if record.get("result_sha256") != digest(path / "result.npz"):
        raise ValueError(f"{path}: payload digest mismatch")
    with np.load(path / "result.npz", allow_pickle=False) as archive:
        arrays = {key: archive[key] for key in archive.files}
    return arrays, record
