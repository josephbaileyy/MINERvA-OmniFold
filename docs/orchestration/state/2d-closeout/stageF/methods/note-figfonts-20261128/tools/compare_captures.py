#!/usr/bin/env python3
"""compare_captures.py: do two arms draw the same data? (note-figfonts-20261128)

usage: python3 -I compare_captures.py [--texts] <capture dir A> <capture dir B> <saved name> [<saved name> ...]

For each saved file name (e.g. tension_spectrum.pdf) it reads capture_palette.py's records in both directories:
  <name>.npz   the drawn arrays (fig-restyle-20261031/tools/artists.py write()): the same members in the same order,
               each with the same dtype, shape and bytes;
  <name>.json  the artist index (kind, axes, label, gid, hash, dhash, xhash, colours, style): equal as JSON.
With --texts, <name>.texts (canvas size, each drawn text's string and font size, text overlaps) must also be equal;
a font-embedding change leaves it unchanged, a size change does not, and without --texts only the strings are
compared (sizes and canvas may differ).
For each name it prints a data hash: sha256 over repr((key, dtype.str, shape)) and the bytes of every array, in npz
order (the method of FIGS-REPORT-20261127.txt), equal in both arms when the line reads EQUAL.
Exit 1 if any name differs or is missing.
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np


def npz_hash(p):
    h = hashlib.sha256(); members = []
    with np.load(p, allow_pickle=False) as z:
        for k in z.files:
            a = z[k]
            h.update(repr((k, a.dtype.str, a.shape)).encode("ascii")); h.update(a.tobytes())
            members.append((k, a.dtype.str, a.shape, hashlib.sha256(a.tobytes()).hexdigest()))
    return h.hexdigest(), members


def strings(t):
    """The drawn strings of a .texts record, whose "texts" is a list of [font size, string]."""
    return [x[1] for x in json.loads(t)["texts"]]


def main(argv):
    texts = argv[:1] == ["--texts"]
    if texts:
        argv = argv[1:]
    if len(argv) < 3:
        print(__doc__.split("\n\n")[1]); return 2
    a, b, names = Path(argv[0]), Path(argv[1]), argv[2:]
    bad = 0
    for n in names:
        try:
            ha, ma = npz_hash(a / f"{n}.npz"); hb, mb = npz_hash(b / f"{n}.npz")
            ja = json.loads((a / f"{n}.json").read_text()); jb = json.loads((b / f"{n}.json").read_text())
            ta = (a / f"{n}.texts").read_text(); tb = (b / f"{n}.texts").read_text()
        except FileNotFoundError as e:
            print(f"MISSING {n}: {e}"); bad += 1; continue
        why = []
        if ma != mb: why.append("arrays")
        if ja != jb: why.append("artist index")
        if texts and ta != tb: why.append("texts")
        if not texts and strings(ta) != strings(tb): why.append("drawn strings")
        bad += bool(why)
        print(f"{'EQUAL' if not why else 'DIFFER (' + ', '.join(why) + ')'} {n}: {len(ma)} arrays, "
              f"{len(ja) if isinstance(ja, list) else len(ja.get('items', ja))} index entries; data sha256 {ha}"
              + ("" if ha == hb else f" vs {hb}"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
