#!/usr/bin/env python3
"""Per group of the REF-G1 preconditions listing: how many atimes moved since the listing, when, and the exposed-from
date (oldest atime + 56 days) at the listing and now. Reads only committed files.

    python3 atime_groups.py LISTING_JSON STAT_TXT
"""
import datetime as dt
import json
import sys

utc = lambda t: dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
files = json.load(open(sys.argv[1]))["files"]
lines = open(sys.argv[2]).read().splitlines()
print("stat taken", lines[0])
now = {p: int(a) for a, _m, _s, p in (l.split(maxsplit=3) for l in lines[1:])}
assert set(now) == {e["path"] for v in files.values() for e in v}, "the stat and the listing name different files"
for g, v in files.items():
    mv = [now[e["path"]] for e in v if now[e["path"]] != int(e["atime"])]
    old0, old1 = min(int(e["atime"]) for e in v), min(now[e["path"]] for e in v)
    span = f"{utc(min(mv))}..{utc(max(mv))}" if mv else "-"
    print(f"{g}: {len(v)} files, {len(mv)} moved ({span}); exposed from {utc(old0 + 56 * 86400)} at the listing, "
          f"{utc(old1 + 56 * 86400)} now")
    if g == "ibu_inputs":
        for e in v:
            print(f"  {e['path']}: {e['atime_utc']} -> {utc(now[e['path']])}")
