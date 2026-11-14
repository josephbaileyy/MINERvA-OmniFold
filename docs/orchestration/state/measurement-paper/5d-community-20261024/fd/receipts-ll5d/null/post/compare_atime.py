"""Compare a stat-only atime-post (atime-post-2.sh's output: a host line, "atime<TAB>path" lines sorted by path with
sort -k2, then a find_rc line) with the rerun connect's W/atime-pre.tsv (connect :205-208, the same find and sort).
Requires the same path set; lists every path whose atime differs, with both times in UTC. Exit 0 only with the same
path set and no move.
    python3 -I compare_atime.py <atime-pre.tsv> <atime-post.raw.txt>
"""
import datetime
import sys

pre = [l.split("\t", 1) for l in open(sys.argv[1]).read().splitlines()]
raw = open(sys.argv[2]).read().splitlines()
assert raw[0].startswith("host=") and raw[-1].startswith("find_rc="), (raw[0], raw[-1])
post = [l.split("\t", 1) for l in raw[1:-1]]
print(raw[0]); print(raw[-1])
Z = lambda s: datetime.datetime.fromtimestamp(float(s), datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
pp, qp = {p: a for a, p in pre}, {p: a for a, p in post}
print(f"pre {len(pre)} lines ({len(pp)} paths), post {len(post)} lines ({len(qp)} paths)")
only_pre, only_post = sorted(set(pp) - set(qp)), sorted(set(qp) - set(pp))
print("only in pre:", only_pre); print("only in post:", only_post)
moved = [(p, pp[p], qp[p]) for p in sorted(set(pp) & set(qp)) if float(pp[p]) != float(qp[p])]
print("moved", len(moved))
for p, a, b in moved:
    print(f"MOVED {p} {Z(a)} -> {Z(b)}")
ok = raw[-1].startswith("find_rc=0 ") and not only_pre and not only_post and not moved and len(pre) == 1146
print("ATIME-POST", "SAME-SET-NONE-MOVED" if ok else "STOP")
sys.exit(0 if ok else 1)
