"""COV2D control (1), the director's scoping section 8 ruling 1(1): $UNI's CV columns equal $CV's, row for row, on
every shared branch of every shared tree. Login node, nice 19, 0 node-h. Both files are opened through O_NOATIME
descriptors and streamed in entry chunks; atime is checked before and after.

Exact means bitwise: equal dtype, equal entry count, and equal bytes in every row. A branch the CV file carries and
the universe file lacks is a failure, as is a declared branch either file lacks. Exit 0 and "CONTROL1 PASS" only when
nothing failed; exit 3 and "CONTROL1 FAIL" otherwise. Non-tree keys are printed for information and are not graded.

  nice -n 19 python control1_content_check.py [--cv PATH] [--uni PATH] [--step N]
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys
import time

import numpy as np

PATHS = {
    "CV": "/global/cfs/cdirs/m3246/josephrb/two-d-followup-20261010/xr-input/runEventLoopOmniFold_MEFHC.root",
    "UNI": "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/runEventLoopOmniFold_MEFHC_universes_full.root",
}
# Section 8 ruling 1(1) names the truth trees' branches; the data and background trees' are the CV file's own
# branches as the P1 probe listed them (p1p3_probe.out). Every shared branch is compared, declared or not.
DECLARED = {
    "mc_signal_reco": ("sim", "sim_pz", "sim_pass", "w_reco", "MC", "MC_pz", "w_truth"),
    "mc_truth_denom": ("MC", "MC_pz", "w_truth"),
    "data": ("measured", "measured_pz", "measured_pass"),
    "mc_background": ("sim_background", "sim_background_pz", "sim_background_pass", "w_bkg"),
}
STEP = 2_000_000


def stat_line(path):
    s = os.stat(path)
    return f"size={s.st_size} mtime={int(s.st_mtime)} atime={int(s.st_atime)}", int(s.st_atime)


def open_noatime(path):
    """A read-only file object on an O_NOATIME descriptor; raises AttributeError where the flag does not exist."""
    return os.fdopen(os.open(path, os.O_RDONLY | os.O_NOATIME), "rb")


def trees(f):
    return {k.split(";")[0] for k, c in f.classnames(recursive=False).items() if c == "TTree"}


def compare_chunk(a, b):
    """Row indices where two equal-dtype 1-D arrays differ in bytes."""
    if a.dtype.itemsize in (1, 2, 4, 8):
        u = np.dtype(f"u{a.dtype.itemsize}")
        return np.flatnonzero(a.view(u) != b.view(u))
    raw_a = a.view(np.uint8).reshape(len(a), -1)
    raw_b = b.view(np.uint8).reshape(len(b), -1)
    return np.flatnonzero((raw_a != raw_b).any(axis=1))


def value_unequal(a, b):
    """Rows unequal by value with NaN equal to NaN (diagnostic only; the verdict is bitwise)."""
    eq = a == b
    if a.dtype.kind == "f" and b.dtype.kind == "f":
        eq |= np.isnan(a) & np.isnan(b)
    return int(np.count_nonzero(~eq))


def compare_tree(fcv, funi, name, step, failures):
    tcv, tuni = fcv[name], funi[name]
    bcv, buni = set(tcv.keys()), set(tuni.keys())
    shared = sorted(bcv & buni)
    print(f"tree {name}: entries CV={tcv.num_entries} UNI={tuni.num_entries} branches CV={len(bcv)} UNI={len(buni)} "
          f"shared={len(shared)}")
    print(f"  shared: {shared}")
    for b in sorted(bcv - buni):
        failures.append(f"{name}.{b}: in CV, absent from UNI")
    for b in DECLARED.get(name, ()):
        if b not in bcv or b not in buni:
            failures.append(f"{name}.{b}: declared, absent from {'CV' if b not in bcv else 'UNI'}")
    if tcv.num_entries != tuni.num_entries:
        failures.append(f"{name}: entries CV={tcv.num_entries} UNI={tuni.num_entries}")
        return
    n = tcv.num_entries
    live = []
    for b in shared:
        dcv, duni = tcv[b].interpretation, tuni[b].interpretation
        if str(dcv) != str(duni):
            failures.append(f"{name}.{b}: interpretation CV={dcv} UNI={duni}")
        live.append(b)
    state = {b: {"diff": 0, "first": None, "valdiff": 0, "dtype": None, "h_cv": hashlib.sha256(),
                 "h_uni": hashlib.sha256()} for b in live}
    for start in range(0, n, step):
        stop = min(start + step, n)
        acv = tcv.arrays(live, entry_start=start, entry_stop=stop, library="np")
        auni = tuni.arrays(live, entry_start=start, entry_stop=stop, library="np")
        for b in live:
            a, u, s = acv[b], auni[b], state[b]
            if a.dtype == object or u.dtype == object or a.ndim != 1 or u.ndim != 1:
                s["dtype"] = f"not a flat numeric column (CV {a.dtype}, UNI {u.dtype})"
                live = [x for x in live if x != b]
                continue
            s["h_cv"].update(a.dtype.str.encode() + a.tobytes())
            s["h_uni"].update(u.dtype.str.encode() + u.tobytes())
            if a.dtype != u.dtype or len(a) != len(u) or len(a) != stop - start:
                s["dtype"] = f"CV {a.dtype}[{len(a)}] UNI {u.dtype}[{len(u)}] want [{stop - start}]"
                continue
            idx = compare_chunk(a, u)
            if len(idx):
                s["diff"] += len(idx)
                s["valdiff"] += value_unequal(a, u)
                if s["first"] is None:
                    r = int(idx[0])
                    s["first"] = (start + r, repr(a[r]), repr(u[r]))
        print(f"  rows {start}..{stop} of {n} done utc={time.strftime('%H:%M:%SZ', time.gmtime())}", flush=True)
    for b in sorted(state):
        s = state[b]
        hcv, huni = s["h_cv"].hexdigest(), s["h_uni"].hexdigest()
        ok = s["dtype"] is None and s["diff"] == 0 and hcv == huni
        print(f"  {'EQUAL ' if ok else 'DIFFER'} {name}.{b} rows={n} bitwise_diff={s['diff']} value_diff={s['valdiff']} "
              f"sha256 CV={hcv[:16]} UNI={huni[:16]}")
        if s["dtype"] is not None:
            failures.append(f"{name}.{b}: dtype/length {s['dtype']}")
        elif s["diff"]:
            row, x, y = s["first"]
            failures.append(f"{name}.{b}: {s['diff']} rows differ (value-unequal {s['valdiff']}); first row {row} "
                            f"CV={x} UNI={y}")
        elif hcv != huni:
            failures.append(f"{name}.{b}: digests differ with no row difference")


def info_keys(fcv, funi):
    for k, c in sorted(fcv.classnames(recursive=False).items()):
        if c == "TTree":
            continue
        try:
            vals = [f[k].member("fVal") if k in f else "absent" for f in (fcv, funi)]
        except Exception as e:  # informational only; never graded
            vals = [f"unreadable: {type(e).__name__}"]
        print(f"info {k} {c}: {vals}")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--cv", default=PATHS["CV"])
    ap.add_argument("--uni", default=PATHS["UNI"])
    ap.add_argument("--step", type=int, default=STEP)
    args = ap.parse_args(argv)
    import uproot

    print(f"host={os.uname().nodename} utc={time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} "
          f"uproot={uproot.__version__} numpy={np.__version__} nice={os.nice(0)} step={args.step}")
    failures = []
    before = {k: stat_line(p) for k, p in (("CV", args.cv), ("UNI", args.uni))}
    for k, (line, _) in before.items():
        print(f"stat before {k} {line}")
    with open_noatime(args.cv) as hcv, open_noatime(args.uni) as huni:
        fcv, funi = uproot.open(hcv), uproot.open(huni)
        tcv, tuni = trees(fcv), trees(funi)
        print(f"trees CV={sorted(tcv)} UNI={sorted(tuni)}")
        for t in sorted(tcv - tuni):
            failures.append(f"tree {t}: in CV, absent from UNI")
        for t in sorted(DECLARED):
            if t not in tcv or t not in tuni:
                failures.append(f"tree {t}: declared, absent from {'CV' if t not in tcv else 'UNI'}")
        for t in sorted(tcv & tuni):
            compare_tree(fcv, funi, t, args.step, failures)
        info_keys(fcv, funi)
    for k, p in (("CV", args.cv), ("UNI", args.uni)):
        line, atime = stat_line(p)
        print(f"stat after  {k} {line}")
        if atime != before[k][1]:
            failures.append(f"{k}: atime moved {before[k][1]} -> {atime}")
    for f in failures:
        print(f"FAILURE {f}")
    print(f"CONTROL1 {'FAIL' if failures else 'PASS'} failures={len(failures)}")
    return 3 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
