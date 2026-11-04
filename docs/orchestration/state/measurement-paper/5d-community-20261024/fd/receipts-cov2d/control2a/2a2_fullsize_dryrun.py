"""Local full-size dry run of control (2a)'s three steps at M_A1, before the rerun connect's sha goes to the director:
a synthetic $CV of 4,119,797 rows built by test_cov2d_writer.write_cv (the writer tests' own fixture builder), then
control2a_split.py's read, write and check through a launcher that sets os.O_NOATIME = 0 (macOS lacks it). One
interpreter with ROOT and uproot runs every step; the cluster splits them across envs.

  python fullsize_dryrun.py <scratch dir> <repo> <M> <harness>
"""
import io
import os
import re
import subprocess
import sys
import tarfile
import time
from pathlib import Path

import numpy as np

D, REPO, M, HARNESS = Path(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4]
N = 4119797
EXPORT = ["2d-unfolding/cov2d",
          "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-cov2d/control1"]
LAUNCH = ("import os, runpy, sys; os.O_NOATIME = getattr(os, 'O_NOATIME', 0); sys.argv = sys.argv[1:]; "
          "runpy.run_path(sys.argv[0], run_name='__main__')")

deploy = D / "deploy"
deploy.mkdir(parents=True)
tar = subprocess.run(["git", "-C", REPO, "archive", M, *EXPORT], check=True, capture_output=True).stdout
with tarfile.open(fileobj=io.BytesIO(tar)) as t:
    t.extractall(deploy)
blob = subprocess.run(["git", "hash-object", str(deploy / "2d-unfolding/cov2d/cov2d_writer.py")],
                      capture_output=True, text=True).stdout.strip()
print(f"deploy at {M}: cov2d_writer blob {blob}")
sys.path[:0] = [str(deploy / "2d-unfolding/cov2d"), str(deploy / "2d-unfolding/cov2d/tests")]
import test_cov2d_writer  # noqa: E402

r = np.random.default_rng(7)
cols = {"measured": r.uniform(0, 3, N), "measured_pz": r.uniform(1, 30, N),
        "measured_pass": (r.uniform(size=N) < 0.8).astype(np.uint8)}
cols["measured"][7] = -0.0
cv = D / "cv.root"
t0 = time.time()
test_cov2d_writer.write_cv(cv, cols, 1.057394261158926e21)
os.utime(cv, (time.time() + 86400, os.stat(cv).st_mtime))
print(f"synthetic CV: {N} rows, {time.time() - t0:.0f}s")


def step(*args):
    r = subprocess.run([sys.executable, "-B", "-c", LAUNCH, HARNESS, "--deploy", str(deploy), *map(str, args)],
                       capture_output=True, text=True)
    print(r.stdout + r.stderr, end="")
    return r.returncode, r.stdout


def sha(text, key):
    return re.search(rf"{key}=([0-9a-f]{{64}})", text).group(1)


rc, t1 = step("read", "--cv", cv, "--npz", D / "cv.npz", "--manifest", D / "cv.json")
print(f"STEP1 rc={rc}")
rc, t2 = step("write", "--npz", D / "cv.npz", "--npz-sha", sha(t1, "npz_sha256"), "--manifest", D / "cv.json",
              "--manifest-sha", sha(t1, "manifest_sha256"), "--out", D / "writer_control.root")
print(f"STEP2 rc={rc}")
rc, t3 = step("check", "--cv", cv, "--out", D / "writer_control.root", "--out-sha", sha(t2, "out_sha256"))
print(f"STEP3 rc={rc}")
ok = rc == 0 and "WRITER-CONTROL PASS failures=0" in t3 and "CHECK rc=0 stub_calls=1" in t3
print(f"DRYRUN {'PASS' if ok else 'FAIL'}")
