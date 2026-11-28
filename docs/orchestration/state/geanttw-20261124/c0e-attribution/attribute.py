"""Attribute C0e's 23 NOT ALLOWED paths in P0's strace -f -y logs (read-only, uses p0_check.py's own parser regexes).

usage: python3 -I attribute.py P0_CHECK_DIR FETCH_DIR
"""
import json
import re
import sys
from collections import OrderedDict, defaultdict
from pathlib import Path

code, fetch = Path(sys.argv[1]), Path(sys.argv[2])
sys.path.insert(0, str(code))
import p0_check as pc  # noqa: E402

bad = []
for line in (fetch / "check.txt").read_text().splitlines():
    m = re.match(r"\s*NOT ALLOWED (\S.*)$", line)
    if m:
        bad.append(m.group(1))
assert len(bad) == 23, len(bad)
BAD = set(bad)

FLAGS = re.compile(r'"[^"]+",\s*([A-Z_|]+)')
report = {}
for b in ("pin", "pat"):
    lines = (fetch / f"strace.{b}.1L").read_text(errors="replace").splitlines()
    main = None
    first5 = defaultdict(list)          # pid -> first five successful opens (placed path)
    hits = []                            # (lineno, pid, placed, arg, flags)
    pending = {}
    for i, raw in enumerate(lines, 1):
        s = raw.strip()
        m = pc.OPEN.match(s)
        if m:
            pid, path, rc, fdpath = m.group(1), m.group(2), m.group(3), m.group(4)
            if main is None:
                main = pid
            fl = FLAGS.search(s)
            flags = fl.group(1) if fl else "?"
            if rc is None:
                pending[pid] = (path, flags, i)
                continue
            if int(rc) < 0:
                continue
            placed = pc._opened(path, fdpath)
        else:
            r = pc.RESUMED.match(s)
            if not (r and r.group(1) in pending):
                continue
            pid = r.group(1)
            path, flags, i0 = pending.pop(pid)
            if int(r.group(2)) < 0:
                continue
            placed = pc._opened(path, r.group(3))
        if len(first5[pid]) < 5:
            first5[pid].append(placed)
        if placed in BAD:
            hits.append((i, pid, placed, path, flags))
    per_path = OrderedDict()
    for p in sorted(BAD):
        hs = [h for h in hits if h[2] == p]
        per_path[p] = [{"line": h[0], "pid": h[1], "main": h[1] == main, "arg": h[3], "flags": h[4],
                        "directory": "O_DIRECTORY" in h[4]} for h in hs]
    pids = sorted({h[1] for h in hits})
    report[b] = {"main_pid": main, "n_bad_seen": sum(1 for p in per_path if per_path[p]),
                 "paths": per_path,
                 "child_first5": {p: first5[p] for p in pids if p != main}}

# the (2) test: a regular (non-O_DIRECTORY) open by the main PID of any of the 23 other than cuda.h and the SSSD cache
EXEMPT = {p for p in BAD if p.endswith("/include/cuda.h") or p == "/var/lib/sss/mc/passwd"}
stop = [(b, p, h) for b in report for p, hs in report[b]["paths"].items() for h in hs
        if h["main"] and not h["directory"] and p not in EXEMPT]
report["test2_stop_hits"] = stop
print(json.dumps(report, indent=1))
