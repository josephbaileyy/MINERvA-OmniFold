"""make_pins.py -- the pins pg-probe.py embeds, derived from the offline record and F1's spline pins.

Run: python3 -I -B make_pins.py   (prints the JSON; embed_pins() rewrites pg-probe.py's PINS_JSON block in place)
The probe compares the node's bytes with these. Nothing is interpreted on the node.
"""
import hashlib
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = Path(os.environ.get("PG_REPO_ROOT") or HERE.parents[6])
RECORD = HERE.parent / "record" / "PG-RECORD.json"
TUNES = ("G18_10a_02_11b", "AR23_20i_00_000", "G18_02a_00_000", "G21_11a_00_000")   # spent, then slots 2 and 1
CVMFS_SPLINES = ("G18_10a_02_11b", "AR23_20i_00_000", "G18_02a_00_000")           # slot 1's is a private copy
LIBS = re.compile(r"^Linux64bit\+3\.10-2\.17-e20-prof/lib/")


def qualifier(t):
    return t.replace("_", "") + "-k250-e1000"


def pins():
    raw = RECORD.read_bytes()
    r = json.loads(raw)
    files = {}
    for t in TUNES:
        files.update(r["tunes"][t]["files"])
    files.update({k: v for k, v in r["pins"]["files"].items() if LIBS.match(k) or k == "ups/genie.table"})
    listings = {d: v for t in TUNES for d, v in r["tunes"][t]["listings"].items()}
    xsec = {}
    for t in CVMFS_SPLINES:
        s = r["splines"][t]
        xsec[f"{qualifier(t)}/data/gxspl-NUsmall.xml"] = s["spline_sha256"]
        xsec[f"{qualifier(t)}/data/README"] = s["readme_sha256"]
    return {"record_sha256": hashlib.sha256(raw).hexdigest(), "genie_files": dict(sorted(files.items())),
            "genie_links": r["pins"]["links"], "genie_listings": dict(sorted(listings.items())),
            "xsec_files": dict(sorted(xsec.items())), "required_qualifiers": sorted(qualifier(t) for t in CVMFS_SPLINES)}


def block(p):
    return "PINS_JSON = r'''" + json.dumps(p, indent=1, sort_keys=True) + "'''"


def embed_pins(probe=HERE / "pg-probe.py"):
    src = probe.read_text()
    new = re.sub(r"PINS_JSON = r'''.*?'''", lambda m: block(pins()), src, count=1, flags=re.S)
    probe.write_text(new)
    return new != src


if __name__ == "__main__":
    if sys.argv[1:] == ["--embed"]:
        print("changed" if embed_pins() else "unchanged")
    else:
        print(json.dumps(pins(), indent=1, sort_keys=True))
