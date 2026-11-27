#!/usr/bin/env python3
"""Build ce3_diag_remote.py (ce3_diag.py with PINS filled) and ce3-diag.sh (the node wrapper) from committed records.

usage: python3 -I -B build_diag.py REPO [--check]
  REPO is a checkout of this repository; the pins are read at origin/main through `git show`:
    - the 12 S1 dumps' sha256 from fd/rpd-reco/INPUTS.sha256 (the file P0's and d2s0e1's pins name);
    - flux4's 12 factor products' paths and sha256 from p0e1's committed run/p0.json (run-20261127).
  --check rebuilds in memory and requires both files on disk to be byte-identical.
"""

import base64
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FD = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/rpd-reco"
PY = "/global/homes/j/josephrb/.conda/envs/omnifold_py310/bin/python3"  # d2-predict's interpreter (the config's)


def git(repo, path):
    return subprocess.run(["git", "-C", repo, "show", f"origin/main:{path}"], check=True, capture_output=True).stdout


def build(repo):
    lat = {}
    for line in git(repo, f"{FD}/INPUTS.sha256").decode().splitlines():
        h, p = line.split()
        if p.endswith(".npz") and "_bkg" not in p:
            lat[p.rsplit("lat_", 1)[1][:2]] = [p, h]
    p0 = json.loads(git(repo, f"{FD}/p0e1-20261126/run-20261127/records/run/p0.json"))
    assert p0["status"] == "PASS" and p0["dry_run"] is False
    products = {pl: [v["path"], v["sha256"]] for pl, v in p0["result"]["factor_products"].items()}
    assert len(lat) == 12 and len(products) == 12
    pins = {"lat": dict(sorted(lat.items())), "products": dict(sorted(products.items()))}
    src = (HERE / "ce3_diag.py").read_text()
    marker = "PINS = {}  # filled by build_diag.py"
    assert src.count(marker) == 1
    remote = src.replace(marker, "PINS = " + json.dumps(pins, sort_keys=True) + "  # filled by build_diag.py", 1).encode()
    sha = hashlib.sha256(remote).hexdigest()
    b64 = base64.b64encode(remote).decode()
    wrapper = f"""#!/bin/bash
# RPD-RECO e1's C-E3 tail diagnostic (read-only, MC-only; DECLARATION.md), one login02 session:
#   ssh saul.nersc.gov "ssh -o BatchMode=yes login02 'bash -s'" < ce3-diag.sh > diag.json 2> diag.err
# The script (ce3_diag_remote.py, sha256 {sha}) is embedded below as base64 and checked against its sha256 on the
# node, then run once at nice 19 with one thread by d2-predict's interpreter. It reads 12 S1 dumps and 12 flux4 products
# by O_NOATIME, checks each sha256, opens no measured key, and writes nothing on the cluster (JSON on stdout).
# Exit 2: refused before any read; 9: an input or the self-check failed (report still written); 0: report written.
stop() {{ echo "STOP: $*" >&2; exit 2; }}
h=$(hostname) && [ "$h" = login02 ] || stop "not login02 (${{h:-hostname failed}})"
PYB='{b64}'
s1=$(printf '%s' "$PYB" | base64 -d | sha256sum) && [ "${{s1%% *}}" = {sha} ] || stop "script sha ${{s1%% *}}"
py=$(printf '%s' "$PYB" | base64 -d) && [ -n "$py" ] || stop "decode script"
[ -x {PY} ] || stop "no interpreter {PY}"
for k in OMP_NUM_THREADS OPENBLAS_NUM_THREADS MKL_NUM_THREADS NUMEXPR_NUM_THREADS VECLIB_MAXIMUM_THREADS; do export "$k=1"; done
echo "ce3-diag start $(date -u +%FT%TZ) on $h; script {sha}" >&2
nice -n 19 {PY} -I -B -c "$py" < /dev/null
rc=$?
echo "ce3-diag end $(date -u +%FT%TZ) rc=$rc" >&2
exit $rc
"""
    return remote, wrapper.encode(), sha, pins


def main():
    repo = sys.argv[1]
    remote, wrapper, sha, _ = build(repo)
    targets = {"ce3_diag_remote.py": remote, "ce3-diag.sh": wrapper}
    if "--check" in sys.argv[2:]:
        bad = [n for n, b in targets.items() if (HERE / n).read_bytes() != b]
        print("CHECK:", "PASS" if not bad else f"FAIL {bad}")
        return 0 if not bad else 1
    for n, b in targets.items():
        (HERE / n).write_bytes(b)
    subprocess.run(["bash", "-n", str(HERE / "ce3-diag.sh")], check=True)
    print("ce3_diag_remote.py", sha)
    print("ce3-diag.sh       ", hashlib.sha256(wrapper).hexdigest())
    return 0


if __name__ == "__main__":
    sys.exit(main())
