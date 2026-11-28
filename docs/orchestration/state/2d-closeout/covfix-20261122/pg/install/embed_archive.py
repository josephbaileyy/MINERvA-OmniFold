"""embed_archive.py <commit> -- carry a git archive of <commit> into pg-replay-g2111a.py (B3).

It runs `git archive --format=tar <commit> -- PATHS | gzip -n`, and takes `git ls-tree -r <commit> -- PATHS` as the
blob pins, refusing any link or submodule entry. It fills COMMIT, ARCHIVE_PATHS, ARCHIVE_SHA256, BLOBS_JSON and
ARCHIVE_B64 in place and prints the archive's sha256. The commit must already hold every file B3 runs; this file and
pg-replay-g2111a.py are committed after it.

Run: python3 -I -B embed_archive.py <commit>   (from this directory)
"""
import base64
import gzip
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[6]
REC = "docs/orchestration/state/2d-closeout/covfix-20261122/pg/record"
PATHS = ["3d-unfolding/genie", "setup_salloc_env.sh", f"{REC}/PG-RECORD.json", f"{REC}/genie-manifest.json",
         f"{REC}/G2111a-members.json"]


def build(commit, repo=REPO, paths=PATHS):
    tar = subprocess.run(["git", "-C", str(repo), "archive", "--format=tar", commit, "--"] + paths,
                         capture_output=True, check=True).stdout
    data = gzip.compress(tar, mtime=0)
    blobs = {}
    for ln in subprocess.run(["git", "-C", str(repo), "ls-tree", "-r", commit, "--"] + paths,
                             capture_output=True, text=True, check=True).stdout.splitlines():
        meta, path = ln.split("\t", 1)
        mode, kind, sha = meta.split()
        if kind != "blob" or mode not in ("100644", "100755"):
            raise SystemExit(f"{path}: mode {mode} {kind} is not a regular file")
        blobs[path] = sha
    return data, blobs


def embed(commit, script=HERE / "pg-replay-g2111a.py", repo=REPO, paths=PATHS):
    full = subprocess.run(["git", "-C", str(repo), "rev-parse", commit], capture_output=True, text=True,
                          check=True).stdout.strip()
    data, blobs = build(full, repo, paths)
    sha = hashlib.sha256(data).hexdigest()
    src = script.read_text()
    for name, value in (("COMMIT", repr(full)), ("ARCHIVE_PATHS", repr(paths)), ("ARCHIVE_SHA256", repr(sha))):
        src, n = re.subn(rf"^{name} = .*$", f"{name} = {value}", src, count=1, flags=re.M)
        assert n == 1, name
    src = re.sub(r"BLOBS_JSON = r'''.*?'''", lambda m: "BLOBS_JSON = r'''" + json.dumps(blobs, indent=0, sort_keys=True)
                 + "'''", src, count=1, flags=re.S)
    src = re.sub(r'^ARCHIVE_B64 = ".*"$', lambda m: 'ARCHIVE_B64 = "' + base64.b64encode(data).decode() + '"', src,
                 count=1, flags=re.M)
    script.write_text(src)
    return full, sha, len(blobs)


if __name__ == "__main__":
    print(*embed(sys.argv[1]))
