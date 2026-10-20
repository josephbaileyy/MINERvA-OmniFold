#!/usr/bin/env python3
"""Read event-loop omnifiles by their LATEST TTree cycle, and compare two of them with the W2 rule.

Long event-loop outputs carry autosave cycles: e.g. W2b's rrzero_1A holds mc_signal_reco;9 (2,682,267 entries) and the
stale mc_signal_reco;8 (2,489,136). ``publication/w2/compare_omnifiles.py`` iterates ``GetListOfKeys()`` and keeps
the last key per name, which is the LOWER cycle (measured, S0 report). This module reads each tree's highest cycle
with uproot and returns the same structure as the W2 reader, so the W2 comparison logic can be reused unchanged:

    python -I omnifile_io.py equal A.root B.root [--out x.json]     # the W2 "equal" rule on the latest cycles
    python -I omnifile_io.py shifted BASE.root SHIFT.root --scale s   # the W2 "shifted" rule on the latest cycles
    python -I omnifile_io.py cycles A.root [B.root ...]             # list every TTree cycle and its entries
Exit 0 = PASS, 1 = FAIL, 2 = could not check.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import uproot

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "publication" / "w2"))
import compare_omnifiles as co  # noqa: E402  (the W2 comparer: same(), cmd_equal(), SHIFTED)


def cycles(path: str) -> dict:
    f = uproot.open(path)
    return {k: int(f[k].num_entries) for k, c in f.classnames().items() if c == "TTree"}


def read_latest(path: str) -> dict:
    """{tree: {"n", "cols", "skipped"}} from each tree's highest cycle; scalar branches only (as the W2 reader)."""
    f = uproot.open(path)
    names = sorted({k.split(";")[0] for k, c in f.classnames().items() if c == "TTree"})
    trees = {}
    for name in names:
        t = f[name]  # uproot resolves a bare name to the highest cycle
        scalars, skipped = [], []
        for b in t.keys():
            tn = t[b].typename
            (skipped if ("[" in tn or "vector" in tn) else scalars).append(b)
        cols = t.arrays(scalars, library="np") if scalars else {}
        trees[name] = {"n": int(t.num_entries), "cols": {k: np.asarray(v) for k, v in cols.items()}, "skipped": skipped}
    return trees


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("equal")
    e.add_argument("a")
    e.add_argument("b")
    sh = sub.add_parser("shifted")
    sh.add_argument("base")
    sh.add_argument("shift")
    sh.add_argument("--scale", type=float, required=True)
    c = sub.add_parser("cycles")
    c.add_argument("files", nargs="+")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "cycles":
            res = {p: cycles(p) for p in a.files}
            print(json.dumps(res, indent=1))
            return 0
        co.read = read_latest  # cmd_equal / cmd_shifted look the reader up at call time
        if a.cmd == "equal":
            res = co.cmd_equal(a.a, a.b)
            res["cycles"] = {"a": cycles(a.a), "b": cycles(a.b)}
        else:
            res = co.cmd_shifted(a.base, a.shift, a.scale)
            res["cycles"] = {"base": cycles(a.base), "shift": cycles(a.shift)}
        res["reader"] = "omnifile_io.read_latest (highest TTree cycle)"
    except Exception as exc:  # noqa: BLE001 - a check that could not run must not read as PASS
        print(json.dumps({"verdict": "COULD_NOT_CHECK", "error": repr(exc)}))
        return 2
    text = json.dumps(res, indent=1)
    print(text)
    if a.out:
        Path(a.out).write_text(text + "\n")
    return 0 if res["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
