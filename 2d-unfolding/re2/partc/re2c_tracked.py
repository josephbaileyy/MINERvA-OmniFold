#!/usr/bin/env python3
"""RE-2: every `run/` path a record names is tracked by git (RE2-BINDING-C, "Every file the report names is tracked").

    python3 -I re2c_tracked.py <record.md> [<record.md> ...]

A record's paths under `run/` (in backticks or link targets, relative to the record's directory) are each checked
against `git ls-files`: a file must be listed; a directory (ending in /) must have at least one listed file. The
repo ignores *.out and *.log, so `git add <dir>` can silently drop a record a document names (PR #320). Prints one
line per path and exits 1 if any is not tracked.
"""
import re
import subprocess
import sys
from pathlib import Path

PATH = re.compile(r"(?:`|\]\()((?:\.\./)*run/[^`)\s]*)")


def main(argv):
    bad = 0
    for rec in argv:
        rec = Path(rec).resolve()
        top = Path(subprocess.run(["git", "-C", str(rec.parent), "rev-parse", "--show-toplevel"], capture_output=True,
                                  text=True, check=True).stdout.strip())
        tracked = set(subprocess.run(["git", "-C", str(top), "ls-files"], capture_output=True, text=True,
                                     check=True).stdout.splitlines())
        seen = sorted(set(PATH.findall(rec.read_text())))
        print(f"{rec.relative_to(top)}: {len(seen)} run/ paths")
        for p in seen:
            rel = (rec.parent / p.rstrip("/")).resolve().relative_to(top).as_posix()
            ok = rel in tracked if not p.endswith("/") else any(t.startswith(rel + "/") for t in tracked)
            if not ok and not p.endswith("/") and any(t.startswith(rel + "/") for t in tracked):
                ok = True   # a directory named without its trailing slash
            bad += not ok
            print(f"  {'tracked' if ok else 'NOT TRACKED'}  {p}")
    print("all tracked" if not bad else f"{bad} path(s) not tracked")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
