"""Check the committed copy of $OUT/post-misc against the post's own SHA256SUMS (cluster/SHA256SUMS).

Files git ignores (*.log, *.out, *.err) are committed with ".txt" appended; RENAMES.tsv maps each back to its name in
post-misc with its sha256. The post's SHA256SUMS leaves out every file named SHA256SUMS (prr_misc_post.sh:55), so
log-misc/SHA256SUMS is checked against the sha256 given as the second argument. Prints one line per file and a summary;
exits 1 on any mismatch or missing file.
Usage: python3 -I verify_receipts.py <the misc/ receipt directory> <sha256 of $OUT/log-misc/SHA256SUMS>
"""
import hashlib
import sys
from pathlib import Path

root, log_sums_sha = Path(sys.argv[1]), sys.argv[2]
renamed = {}
for line in (root / "RENAMES.tsv").read_text().splitlines()[1:]:
    committed, original, sha = line.split("\t")
    renamed[original.removeprefix("post-misc/")] = (committed.removeprefix("cluster/"), sha)
bad = 0
n = 0
for line in (root / "cluster/SHA256SUMS").read_text().splitlines():
    sha, name = line.split(None, 1)
    name = name.removeprefix("./")
    committed, map_sha = renamed.get(name, (name, sha))
    path = root / "cluster" / committed
    got = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "MISSING"
    ok = got == sha == map_sha
    bad += not ok
    n += 1
    print(f"{'OK ' if ok else 'BAD'} {name} -> cluster/{committed}")
missing = [c for c, _ in renamed.values() if not (root / "cluster" / c).is_file()]
got = hashlib.sha256((root / "cluster/log-misc/SHA256SUMS").read_bytes()).hexdigest()
sums_ok = got == log_sums_sha
print(f"{'OK ' if sums_ok else 'BAD'} log-misc/SHA256SUMS {got}")
print(f"{n} files in cluster/SHA256SUMS, {n - bad} match, {len(renamed)} renamed, {len(missing)} renamed files missing; "
      f"log-misc/SHA256SUMS {'matches' if sums_ok else 'DIFFERS'}")
sys.exit(1 if bad or missing or not sums_ok else 0)
