#!/usr/bin/env python3
"""Writes msr_probe_connect.sh from the template below, embedding cov2d_fence.sh rev 2 (sha256 3fbc9cbd...) as base64 so
the node runs those exact bytes before anything else is written. Run from the repository root; prints the sha256."""
import base64
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
FENCE = ROOT / "docs/orchestration/state/2d-closeout/cov2d-fence-20261122/cov2d_fence.sh"
FENCE_SHA = "3fbc9cbd6c08d4c86c71aeeccf28b0b3d8a77393121ef23787c1d421b682171e"
OUT = Path(__file__).resolve().parent / "msr_probe_connect.sh"

fence = FENCE.read_bytes()
assert hashlib.sha256(fence).hexdigest() == FENCE_SHA
b64 = base64.encodebytes(fence).decode()
TEMPLATE = Path(__file__).resolve().parent / "msr_probe_connect.template.sh"
import subprocess, sys
M = sys.argv[1]  # the code commit the node clones (must hold these msr files)
msr = ROOT / "nd-unfolding/msr"
sums = "\n".join(f"{hashlib.sha256((msr / n).read_bytes()).hexdigest()}  {n}" for n in ("msr_build.py", "msr_overlap.py"))
for n in ("msr_build.py", "msr_overlap.py"):  # the committed bytes at M must equal the working files
    blob = subprocess.run(["git", "-C", str(ROOT), "show", f"{M}:nd-unfolding/msr/{n}"], capture_output=True, check=True).stdout
    assert blob == (msr / n).read_bytes(), f"{n} at {M} differs from the working file"
text = (TEMPLATE.read_text().replace("@@FENCE_B64@@", b64.rstrip("\n")).replace("@@M@@", M)
        .replace("@@MSR_SUMS@@", sums))
assert "@@" not in text
OUT.write_text(text)
print(hashlib.sha256(OUT.read_bytes()).hexdigest(), OUT.name)
