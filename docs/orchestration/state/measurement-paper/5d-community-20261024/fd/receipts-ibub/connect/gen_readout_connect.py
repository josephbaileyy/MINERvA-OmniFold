#!/usr/bin/env python3
"""Writes ibub_readout_connect.sh (IBUB connect O, the readout) from ibub_readout_connect.template.sh, and
ibub_readout_launch.sh from its template with that script's sha256 bound in. It embeds what connect R's generator
embeds (cov2d_fence.sh rev 3 as base64, and the sha256 of every ibub file at M, which must equal the working files),
and also the job's id and commit (--job, --job-m).

    python3 gen_readout_connect.py M JOB JOB_M [OUT]   (M: the readout's commit; JOB_M: the job's, IBUB-DONE's M)
"""
import base64
import hashlib
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import gen_run_connect as g  # noqa: E402  (the same fence, root and file list as connect R)


def main(argv) -> int:
    if len(argv) not in (3, 4) or not (re.fullmatch(r"[0-9a-f]{40}", argv[0]) and re.fullmatch(r"[0-9]+", argv[1])
                                       and re.fullmatch(r"[0-9a-f]{40}", argv[2])):
        print("usage: gen_readout_connect.py M JOB JOB_M [OUT]", file=sys.stderr)
        return 2
    M, job, job_m = argv[:3]
    out = Path(argv[3]) if len(argv) > 3 else HERE / "ibub_readout_connect.sh"
    fence = g.FENCE.read_bytes()
    assert hashlib.sha256(fence).hexdigest() == g.FENCE_SHA, "cov2d_fence.sh is not rev 3"
    anc = subprocess.run(["git", "-C", str(g.ROOT), "merge-base", "--is-ancestor", job_m, M])
    assert anc.returncode == 0, f"the job's commit {job_m} is not an ancestor of M {M}"
    for n in g.FILES:
        blob = subprocess.run(["git", "-C", str(g.ROOT), "show", f"{M}:2d-unfolding/ibub/{n}"], capture_output=True,
                              check=True).stdout
        assert blob == (g.IBUB / n).read_bytes(), f"{n} at {M} differs from the working file"
    sums = "\n".join(f"{hashlib.sha256((g.IBUB / n).read_bytes()).hexdigest()}  {n}" for n in g.FILES)
    text = ((HERE / "ibub_readout_connect.template.sh").read_text()
            .replace("@@FENCE_B64@@", base64.encodebytes(fence).decode().rstrip("\n"))
            .replace("@@M@@", M).replace("@@JOB@@", job).replace("@@JOB_M@@", job_m).replace("@@IBUB_SUMS@@", sums))
    assert "@@" not in text
    out.write_text(text)
    sha = hashlib.sha256(out.read_bytes()).hexdigest()
    launch = out.with_name("ibub_readout_launch.sh")
    lt = (HERE / "ibub_readout_launch.template.sh").read_text().replace("@@CONNECT_SHA@@", sha)
    assert "@@" not in lt
    launch.write_text(lt)
    print(sha, out.name)
    print(hashlib.sha256(launch.read_bytes()).hexdigest(), launch.name)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
