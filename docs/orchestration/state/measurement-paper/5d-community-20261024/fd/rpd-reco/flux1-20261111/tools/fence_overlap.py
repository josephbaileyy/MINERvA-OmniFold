#!/usr/bin/env python3
"""The flux connect's overlap fence (director's rulings (b) and (c), 2026-11-11), run before the job is submitted.

STOP (exit 3) if any of cov2d's protected paths (the READY config's cov2d_protected_paths) overlaps
  (b) either write root of the run, in either direction; or
  (c) any original that custody prepare stages, except the single listed exception EXCEPTION below.
Two paths overlap when they are equal or one lies under the other, compared both as written and after
os.path.realpath (which reads symlinks, never file contents).

The originals prepare stages (fd_rpd_reco_custody.prepare at the pinned head): the config's bound files and
flux_source; every path in the pins file; the three selected C-N flux files under flux_root; the closed
fifteen-path MAT set (closed_mat_inventory) under the MAT prefixes below; and the MAT setup and library
files that fd_rpd_inputs pins (MAT_SETUP, MAT_FILES). The config's bound files live in the clone, which is
read here at CLONE in place of /dev/shm/limres-rpd-flux1/repo.

usage: fence_overlap.py CONFIG CLONE        (MAT_PYTHON -I; imports the clone's own modules)
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

EXCEPTION = (
    "/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/"
    "sorted_NuEConstraint_FHC_RHC_IMD.txt"
)
WRITE_ROOTS = ("/pscratch/sd/j/josephrb/rpd-reco-flux-20261111", "/dev/shm/limres-rpd-flux1")
BOUND_CLONE = "/dev/shm/limres-rpd-flux1/repo"
# The MAT environment's prefixes, as prologue 5's trace policy recorded them after setup_salloc_env.sh.
MAT_PREFIXES = {
    "PLOTUTILSROOT": "/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/lib",
    "MPARAMFILES": "/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data",
}


def forms(path: str) -> set[str]:
    return {os.path.normpath(path), os.path.realpath(path)}


def overlaps(a: str, b: str) -> bool:
    for x in forms(a):
        for y in forms(b):
            if x == y or x.startswith(y.rstrip("/") + "/") or y.startswith(x.rstrip("/") + "/"):
                return True
    return False


def staged_originals(config: dict, clone: Path) -> list[tuple[str, str]]:
    sys.path.insert(0, str(clone / "nd-unfolding"))
    import fd_rpd_inputs  # noqa: E402
    import fd_rpd_reco_custody as custody  # noqa: E402

    def local(path: str) -> Path:
        return clone / path[len(BOUND_CLONE) + 1 :] if path.startswith(BOUND_CLONE + "/") else Path(path)

    reads = []
    for key in ("pins", "h2", "inventory", "constants", "mat_dependencies", "flux_source"):
        reads.append((key, config[key]["path"]))
    for line in local(config["pins"]["path"]).read_text().splitlines():
        if line.strip():
            reads.append(("pin", line.split(None, 1)[1].strip()))
    for group, spec in sorted(config["flux_selection"].items()):
        reads.append((f"flux_selection {group}", str(Path(config["flux_root"]) / spec["relative_path"])))
    for key, relative in sorted(custody.closed_mat_inventory()):
        reads.append((f"MAT {key}", str(Path(MAT_PREFIXES[key]) / relative)))
    for name in sorted({**fd_rpd_inputs.MAT_SETUP, **fd_rpd_inputs.MAT_FILES}):
        reads.append(("MAT instrument", name))
    return reads


def main() -> int:
    config = json.loads(Path(sys.argv[1]).read_text())
    clone = Path(sys.argv[2])
    protected = config["cov2d_protected_paths"]
    print(f"FENCE protected paths {len(protected)}; exception {EXCEPTION}")
    stops = []
    for root in WRITE_ROOTS:
        for path in protected:
            if overlaps(root, path):
                stops.append(f"(b) write root {root} overlaps protected {path}")
    reads = staged_originals(config, clone)
    print(f"FENCE staged originals {len(reads)}")
    allowed = []
    for label, read in reads:
        for path in protected:
            if not overlaps(read, path):
                continue
            if os.path.normpath(read) == EXCEPTION and os.path.normpath(path) == EXCEPTION:
                allowed.append(f"{label} {read}")
            else:
                stops.append(f"(c) {label} {read} overlaps protected {path}")
    for line in allowed:
        print(f"FENCE allowed exception: {line}")
    for line in stops:
        print(f"FENCE STOP: {line}")
    if len(allowed) > 1:
        print("FENCE STOP: the exception matched more than once")
        return 3
    verdict = "CLEAR" if not stops else "STOP"
    print(f"FENCE OVERLAP: {verdict} (allowed {len(allowed)}, stops {len(stops)})")
    return 0 if not stops else 3


if __name__ == "__main__":
    sys.exit(main())
