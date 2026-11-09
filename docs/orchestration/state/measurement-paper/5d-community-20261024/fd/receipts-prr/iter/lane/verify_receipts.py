"""Check the committed copy of $OUT/post-dry against the job's own SHA256SUMS (cluster/SHA256SUMS).

Files git ignores (*.log, *.out, *.err) are committed with ".txt" appended; RENAMES.tsv maps each back to its name in
post-dry with its sha256. Prints one line per file and a summary; exits 1 on any mismatch or missing file.
Usage: python3 -I verify_receipts.py <the dry/ receipt directory>
"""
import hashlib
import sys
from pathlib import Path

root = Path(sys.argv[1])
renamed = {}
for line in (root / "RENAMES.tsv").read_text().splitlines()[1:]:
    committed, original, sha = line.split("\t")
    renamed[original.removeprefix("post-iter/")] = (committed.removeprefix("cluster/"), sha)
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
print(f"{n} files in cluster/SHA256SUMS, {n - bad} match, {len(renamed)} renamed")
sys.exit(1 if bad else 0)
