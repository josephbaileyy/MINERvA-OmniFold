#!/usr/bin/env python3
"""Writes ibub_run_connect.sh (IBUB connect R) from ibub_run_connect.template.sh, embedding three things:
- cov2d_fence.sh rev 3 (sha256 7e81a721...) as base64, so the node runs those exact bytes before anything else;
- M;
- the sha256 of every ibub file the node runs.

Each of those files at M must equal the working file. Run from anywhere with the repository's git; prints the
script's sha256.

    python3 gen_run_connect.py M [OUT]      (OUT defaults to ibub_run_connect.sh beside this file)
"""
import base64
import hashlib
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[7]
FENCE = ROOT / "docs/orchestration/state/2d-closeout/cov2d-fence-20261122/cov2d_fence.sh"
FENCE_SHA = "7e81a721476da987a0e1262ab2054132bd8440cd49b0dc7a5c4f01d50a310738"
IBUB = ROOT / "2d-unfolding/ibub"
FILES = ("ibub_unit.py", "ibub_readout.py", "ibub_lanes.py", "ibub_overlap.py", "config.json", "jobs/ibub_job.sbatch")


def main(argv) -> int:
    M = argv[0]
    out = Path(argv[1]) if len(argv) > 1 else HERE / "ibub_run_connect.sh"
    fence = FENCE.read_bytes()
    assert hashlib.sha256(fence).hexdigest() == FENCE_SHA, "cov2d_fence.sh is not rev 3"
    for n in FILES:
        blob = subprocess.run(["git", "-C", str(ROOT), "show", f"{M}:2d-unfolding/ibub/{n}"], capture_output=True,
                              check=True).stdout
        assert blob == (IBUB / n).read_bytes(), f"{n} at {M} differs from the working file"
    sums = "\n".join(f"{hashlib.sha256((IBUB / n).read_bytes()).hexdigest()}  {n}" for n in FILES)
    text = ((HERE / "ibub_run_connect.template.sh").read_text()
            .replace("@@FENCE_B64@@", base64.encodebytes(fence).decode().rstrip("\n"))
            .replace("@@M@@", M).replace("@@IBUB_SUMS@@", sums))
    assert "@@" not in text
    out.write_text(text)
    print(hashlib.sha256(out.read_bytes()).hexdigest(), out.name)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
