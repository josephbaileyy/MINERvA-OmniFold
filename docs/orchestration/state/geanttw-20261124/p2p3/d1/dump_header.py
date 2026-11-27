#!/usr/bin/env python3
"""geanttw P2-P3 D1: the production 2D universe dump's HEADER only, to settle C2's key (director's ruling D1).

    python3 -I dump_header.py      # on a Perlmutter login node; prints the header and one JSON line; writes nothing

It reads one file, the cov2d-protected production universe dump, through an O_NOATIME descriptor. uproot reads it
from that file object, never by path. Only the file's directory and each TTree's metadata are read: tree names,
entry counts, and branch names and types. No basket, so no event data, is ever read.

It refuses (exit 2) on any of these, before printing any header:
- a Python without O_NOATIME;
- a path that is not a regular file;
- the file's atime moving across the read;
- a missing tree mc_signal_reco or mc_truth_denom.
"""
import json
import os
import stat
import sys

PATH = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/runEventLoopOmniFold_MEFHC_universes_full.root"
TREES = ("mc_signal_reco", "mc_truth_denom")
KEYS = ("mc_run", "mc_subrun", "mc_nthEvtInFile")
NOATIME_OPTIONAL = False
if os.environ.get("D1_TEST_PATH"):   # the tests' only door
    PATH, NOATIME_OPTIONAL = os.environ["D1_TEST_PATH"], True


def stop(msg):
    print(f"STOP: {msg}")
    sys.exit(2)


def main():
    flag = getattr(os, "O_NOATIME", None)
    if flag is None and not NOATIME_OPTIONAL:
        stop("this Python has no O_NOATIME")
    st0 = os.stat(PATH)
    if not stat.S_ISREG(st0.st_mode):
        stop(f"{PATH} is not a regular file")
    import uproot
    fd = os.open(PATH, os.O_RDONLY | (flag or 0))
    with os.fdopen(fd, "rb") as fobj:
        f = uproot.open(fobj)
        names = sorted({k.split(";")[0] for k in f.keys(recursive=False)})
        classes = {k.split(";")[0]: v for k, v in f.classnames(recursive=False).items()}
        missing = [t for t in TREES if t not in names]
        if missing:
            stop(f"no tree {missing} in {PATH} (keys {names})")
        rep = {"path": PATH, "size": st0.st_size, "keys": {n: classes.get(n) for n in names}, "trees": {}}
        for t in names:
            if classes.get(t) != "TTree":
                continue
            tree = f[t]
            br = {b: tree[b].typename for b in tree.keys(recursive=True)}
            rep["trees"][t] = {"entries": int(tree.num_entries), "n_branches": len(br), "branches": br,
                               "event_keys_present": [k for k in KEYS if k in br]}
    st1 = os.stat(PATH)
    rep["atime_ns"] = [st0.st_atime_ns, st1.st_atime_ns]
    rep["mtime_ns"] = [st0.st_mtime_ns, st1.st_mtime_ns]
    if st1.st_atime_ns != st0.st_atime_ns or st1.st_mtime_ns != st0.st_mtime_ns:
        stop(f"atime or mtime moved across the read: {rep['atime_ns']} {rep['mtime_ns']}")
    for t in TREES:
        tr = rep["trees"][t]
        print(f"{t}: entries {tr['entries']}, branches {tr['n_branches']}, event keys present {tr['event_keys_present']}")
    both = all(set(rep["trees"][t]["event_keys_present"]) == set(KEYS) for t in TREES)
    rep["key_option"] = "POINTCLOUD-KEYS" if both else "ENTRY-ORDER"
    print(f"KEY {rep['key_option']}")
    print("JSON " + json.dumps(rep, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
