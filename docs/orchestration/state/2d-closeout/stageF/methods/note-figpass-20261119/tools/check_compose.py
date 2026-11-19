#!/usr/bin/env python3
"""The composed Fig. 20/21 holds Fig. 20's items and Fig. 21's MEC items, bit for bit, and nothing else.

usage: python3 -I check_compose.py <composed capture .json> <Fig. 20 capture .json> <Fig. 21 capture .json> <MEC face hex>

Each capture is fig-restyle-20261031/tools/artists.py's index, as written by capture_palette.py, with each item's full
hash (data, colours, styles). The captures of Figs. 20 and 21 are the palette pass's committed arm-1 captures (the
installed files' recipe). Fig. 21's MEC items are those whose face colour is the hex given (with alpha). Its other
items, the GENIE CV bars and the data line, are left out: compose_family4.py checked that they are Fig. 20's (the stack
top and the data line). Passes only if the multiset of the composed figure's hashes equals Fig. 20's plus the MEC
items', and the MEC items are not empty.
"""
import json
import sys
from collections import Counter


def items(p):
    d = json.load(open(p))
    return d["items"] if isinstance(d, dict) and "items" in d else d


new, f20, f21, mec = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4].upper()
a, b, c = items(new), items(f20), items(f21)
m = [it for it in c if mec in [x.upper() for x in it.get("colours", {}).get("face", [])]]
want = Counter(it["hash"] for it in b) + Counter(it["hash"] for it in m)
got = Counter(it["hash"] for it in a)
left = [it for it in c if it not in m]
print(f"composed: {len(a)} items; Fig. 20: {len(b)}; Fig. 21: {len(c)}, of which MEC ({mec}): {len(m)}, left out: "
      f"{len(left)} ({sorted(Counter(it['kind'] for it in left).items())})")
ok = bool(m) and got == want
if not ok:
    print(f"  only in the composed figure: {sum((got - want).values())}; missing from it: {sum((want - got).values())}")
print(f"CHECK-COMPOSE :: {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
