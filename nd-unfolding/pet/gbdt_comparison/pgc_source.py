"""The pinned PET source this comparison imports, verified before any module is loaded.

The estimator (`final_design/scalar/scalar_estimators.py`, the matched study's scalar OmniFold) and
the scorer (`final_design/analysis/score_design.py`, the final-design section-4 scorer) are used
UNCHANGED from the PET final-design closeout commit. They have not landed on `main`, so they are
imported from a checkout of that commit (`--pet-source`, e.g. a `git worktree add --detach <dir>
bc356b0c`) after two checks, both fail-closed:

* the checkout's HEAD is `PET_SOURCE_COMMIT`;
* every file in `PINNED_BLOBS` hashes (`git hash-object`) to its blob at that commit, so the bytes
  the interpreter loads are the committed ones (a dirty or different tree is refused).

The PET directories are APPENDED to `sys.path` (never inserted at position 0), and this package's
own modules are prefixed `pgc_` so no PET module can shadow them. After import, `loaded_files()`
re-hashes the files the interpreter actually loaded and refuses any that came from elsewhere.
"""
from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path
from typing import Any

PET_SOURCE_COMMIT = "bc356b0c0c5b56cb4877bdf2312d2d5dc6d1936d"

# `git rev-parse bc356b0c:<path>` for every PET file this package imports (directly or through the
# matched study's own imports). Recorded 2026-10-05 from the object store.
PINNED_BLOBS = {
    "nd-unfolding/pet/final_design/scalar/selection_data.py":
        "b681267009c82c11fb481cfcdd9f027ddfbf5914",
    "nd-unfolding/pet/final_design/scalar/scalar_estimators.py":
        "650b0f13cfe8fea3f2ec8d58ff53f7742389fab1",
    "nd-unfolding/pet/final_design/scalar/scalar_scoring.py":
        "0bdbb04b6e56beba63ad1bd6e12514027d154e82",
    "nd-unfolding/pet/final_design/scalar/matched_design.py":
        "9099c2523a7c8b51d116b7d3916c94d9a259654b",
    "nd-unfolding/pet/final_design/analysis/score_design.py":
        "551cc4039673114481b92767a307a87e37b6e0d2",
    "nd-unfolding/pet/improvement_campaign/phase_b/scalar/scalar_omnifold.py":
        "34735c20f1b3e43bedf8beb3dfd0c2cccd23aec1",
    "nd-unfolding/pet/improvement_campaign/phase_b/scalar/binned_unfolding.py":
        "4b253fc4063343ba21a12f3ada99f0abce9afca0",
    "nd-unfolding/pet/improvement_campaign/phase_b/scalar/features.py":
        "23209eca2966aa96944fa39bbf766f58963af8b6",
    "nd-unfolding/pet/improvement_campaign/phase_b/scalar/run_ibu.py":
        "5a998dec196b4cc4582cb08318ecb400e951cf8f",
    "nd-unfolding/pet/improvement_campaign/phase_b/scalar/scalar_common.py":
        "e57d1d2c172cf5548500b05a6ac8e79c578f752a",
    "nd-unfolding/pet/improvement_campaign/phase_e/common.py":
        "b427f2ac6a6601b065da7a60ab6d1e957342981d",
}

SEARCH_DIRS = (
    "nd-unfolding/pet/final_design/scalar",
    "nd-unfolding/pet/final_design/analysis",
)


def git_blob_sha1(path: Path | str) -> str:
    """The id git gives these bytes (`git hash-object`)."""
    data = Path(path).read_bytes()
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def verify_checkout(root: Path | str) -> dict[str, Any]:
    """Refuse unless ``root`` is a checkout of `PET_SOURCE_COMMIT` holding the pinned bytes."""
    root = Path(root).resolve()
    head = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True,
                          text=True, check=False).stdout.strip()
    if head != PET_SOURCE_COMMIT:
        raise SystemExit(f"--pet-source {root}: HEAD {head or '?'} != {PET_SOURCE_COMMIT}")
    bad = {rel: (git_blob_sha1(root / rel) if (root / rel).exists() else "missing", want)
           for rel, want in PINNED_BLOBS.items()
           if not (root / rel).exists() or git_blob_sha1(root / rel) != want}
    if bad:
        raise SystemExit(f"--pet-source {root}: files differ from the pinned blobs: {bad}")
    return {"root": str(root), "commit": head, "files": dict(PINNED_BLOBS)}


def activate(root: Path | str) -> dict[str, Any]:
    """Verify the checkout, then append its PET directories to `sys.path`."""
    record = verify_checkout(root)
    for rel in SEARCH_DIRS:
        p = str(Path(record["root"]) / rel)
        if p not in sys.path:
            sys.path.append(p)
    return record


def loaded_files(root: Path | str) -> dict[str, str]:
    """Blob ids of the pinned files the interpreter actually loaded; refuses a module loaded from
    outside ``root`` or with other bytes (the check that the path order did what it claims)."""
    root = Path(root).resolve()
    by_name = {Path(rel).stem: rel for rel in PINNED_BLOBS}
    out: dict[str, str] = {}
    for name, rel in by_name.items():
        mod = sys.modules.get(name)
        if mod is None or getattr(mod, "__file__", None) is None:
            continue
        got = Path(mod.__file__).resolve()
        if got != (root / rel).resolve():
            raise SystemExit(f"module {name} was loaded from {got}, not {root / rel}")
        blob = git_blob_sha1(got)
        if blob != PINNED_BLOBS[rel]:
            raise SystemExit(f"module {name}: loaded blob {blob} != pinned {PINNED_BLOBS[rel]}")
        out[rel] = blob
    return out
