"""FD-PRR addendum A2: compare prr_read's fixture outputs at M_A1 and at A2.
PASS only if readout.txt is byte-identical; the M_A1 readout.json has no "d" key anywhere; the A2 readout.json, with
the "d" key deleted from every table entry and nothing else, is byte-identical to M_A1's (as main writes it:
json.dumps(indent=1) plus a newline); and every table entry at A2 carries "d" (16 values), the only key A2 adds.
Usage: python3 -I compare.py <M_A1 out dir> <A2 out dir>
"""
import json
import sys
from pathlib import Path

a1, a2 = Path(sys.argv[1]), Path(sys.argv[2])
ok = True


def keys_named(x, name, path=""):
    if isinstance(x, dict):
        for k, v in x.items():
            if k == name:
                yield path + "/" + k
            yield from keys_named(v, name, path + "/" + k)
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from keys_named(v, name, f"{path}[{i}]")


t1, t2 = (a1 / "readout.txt").read_bytes(), (a2 / "readout.txt").read_bytes()
print(f"readout.txt: M_A1 {len(t1)} bytes, A2 {len(t2)} bytes, identical {t1 == t2}")
ok &= t1 == t2
j1b, j2b = (a1 / "readout.json").read_bytes(), (a2 / "readout.json").read_bytes()
j1, j2 = json.loads(j1b), json.loads(j2b)
d1 = list(keys_named(j1, "d"))
print(f"M_A1 readout.json: {len(j1b)} bytes, verdict {j1.get('verdict')}, 'd' keys {len(d1)}")
ok &= not d1 and j1.get("verdict") == "COMPLETE"
d2 = list(keys_named(j2, "d"))
table = j2["table"]
with_d = [k for k, v in table.items() if isinstance(v.get("d"), list) and len(v["d"]) == 16]
for v in table.values():
    v.pop("d", None)
outside = list(keys_named(j2, "d"))  # any "d" left once each table entry's own is deleted
print(f"A2 readout.json: {len(j2b)} bytes, 'd' keys {len(d2)}, table entries {len(table)}, with 16-value d "
      f"{len(with_d)}, 'd' keys outside table entries {len(outside)}")
ok &= len(with_d) == len(table) == len(d2) and not outside
stripped = (json.dumps(j2, indent=1) + "\n").encode()
print(f"A2 readout.json with each table entry's 'd' deleted: {len(stripped)} bytes, identical to M_A1's {stripped == j1b}")
ok &= stripped == j1b
print("A2 FIXTURE COMPARISON ::", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
