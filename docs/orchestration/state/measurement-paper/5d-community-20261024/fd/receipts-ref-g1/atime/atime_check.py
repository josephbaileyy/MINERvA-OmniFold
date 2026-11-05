#!/usr/bin/env python3
"""REF-G1 atime check (the director's request of 2026-11-05): compare the bank's and the detector dump's atimes, from a
stat taken after the batch, with the preconditions listing's, and match each moved weight file to the universe unit
that read it, from the batch receipts' lane logs. Reads only committed files.

    python3 atime_check.py LISTING_JSON STAT_TXT BATCH_RECEIPTS_DIR
"""
import collections
import datetime as dt
import json
import os
import re
import sys

listing, stat_txt, batch = sys.argv[1:4]
utc = lambda t: dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
files = json.load(open(listing))["files"]
before = {e["path"]: (g, int(e["atime"])) for g in ("bank", "detector") for e in files[g]}
lines = open(stat_txt).read().splitlines()
print("stat taken", lines[0])
now = {p: int(a) for a, _m, _s, p in (l.split(maxsplit=3) for l in lines[1:])}
assert set(now) == set(before), "the stat and the listing name different files"
moved = collections.defaultdict(list)
for g in ("bank", "detector"):
    paths = [p for p, (gg, _) in before.items() if gg == g]
    mv = sorted((now[p], os.path.basename(p)) for p in paths if now[p] != before[p][1])
    oldest = min(now[p] for p in paths)
    print(f"{g}: {len(paths)} files, {len(mv)} moved since the listing; per minute "
          f"{dict(sorted(collections.Counter(utc(a)[:16] for a, _ in mv).items()))}")
    print(f"  unmoved: {sorted(os.path.basename(p) for p in paths if now[p] == before[p][1])}")
    print(f"  oldest atime now {utc(oldest)}; exposed from (+56 days) {utc(oldest + 56 * 86400)}; "
          f"oldest moved file exposed from {utc(mv[0][0] + 56 * 86400) if mv else None}")
    for a, b in mv:
        m = re.match(r"(.+?)_(wt|wr|tdw|bkgw|denom_nd)\.npy$", b)
        moved[m.group(1) if m else b].append(a)
start = dt.datetime(2026, 11, 5, 14, 42, 6, tzinfo=dt.timezone.utc).timestamp()  # fd_refg1_60857388.out "start"
rows, outside = 0, []
for i in range(8):
    units = [json.loads(l) for l in open(f"{batch}/lanes/lane{i}.log") if l.startswith("{")]
    el = re.search(r"Elapsed.*?: (\S+)", open(f"{batch}/lanes/lane{i}.time").read()).group(1).split(":")
    elapsed = sum(float(x) * 60 ** (len(el) - 1 - j) for j, x in enumerate(el))
    t = start + elapsed - sum(u["seconds"] for u in units)  # what the units' own seconds leave is set-up and overhead
    for u in units:
        t0, t = t, t + u["seconds"]
        if u["unit"].startswith("universe_") and u["unit"] != "universe_CV":
            rows += 1
            at = moved.get(u["unit"][len("universe_"):])
            if not at or not all(t0 - 60 <= a <= t + 60 for a in at):
                outside.append(u["unit"])
units_tags = {u for u in moved if re.search(r"_\d+$", u)}
print(f"universe units (not CV): {rows}; weight files outside their unit's predicted window (+-60 s): {outside}")
print(f"moved weight tags: {len(units_tags)}; other moved files: {sorted(set(moved) - units_tags)}")
