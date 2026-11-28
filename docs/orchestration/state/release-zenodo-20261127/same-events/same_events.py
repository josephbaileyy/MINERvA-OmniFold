#!/usr/bin/env python3
"""Do the EVW2D and EVW5D per-event weights cover the same simulated rows? (PLAN.md, T0-T5.)

    python3 -I same_events.py        # on a Perlmutter login node; prints a report and one JSON line; writes nothing

Rows are matched by POSITION. The two files' `entry` keys index different files (EVW5D: the row's index in
of_inputs_5d.npz's MCgen; EVW2D: the ROOT entry in the 2D omnifile's mc_signal_reco), so equal entries are reported
but are not the test. Every read is through an O_NOATIME descriptor, and a Python without O_NOATIME refuses. Any sha256
mismatch, missing column, wrong dtype or wrong shape stops the check (exit 2) before anything is compared.
"""
import hashlib
import json
import os
import sys

import numpy as np

N_DECLARED = 32849103
FILES = {   # the sha256s are the committed receipts' SHA256SUMS rows (PLAN.md)
    "evw5d_weights": ("/pscratch/sd/j/josephrb/evw5d-20261125-r2/evw5d/weights.npz", "0fceefcdcfcd5c48070453707b55f40e55787909f98481dadcdc82dd0897aba6"),
    "evw5d_constants": ("/pscratch/sd/j/josephrb/evw5d-20261125-r2/evw5d/constants.json", "8f009d828163161418e94997428c80a8c723fa3a015fcb63165861aa3312c3aa"),
    "evw2d_weights": ("/pscratch/sd/j/josephrb/evw2d-20261126/out/weights.npz", "bf452352da52f12a2788f76c4caf9e8402600ba06d352fc99e9344d87367b108"),
    "evw2d_constants": ("/pscratch/sd/j/josephrb/evw2d-20261126/out/constants.json", "1fe4449ee7ec34067f5d2a20aa841f2c97fd2f678eaa7f554ab583ad75daf2ba"),
}
COLS = {"evw5d": {"entry": np.uint32, "truth_pt": np.float32, "truth_pz": np.float32},
        "evw2d": {"entry": np.uint32, "truth_pt": np.float64, "truth_pz": np.float64}}
NOATIME_OPTIONAL = False
if os.environ.get("SAME_EVENTS_TEST_ROOT"):   # the tests' only door: fixture files and shas, no O_NOATIME needed
    root = os.environ["SAME_EVENTS_TEST_ROOT"]
    FILES = {k: (os.path.join(root, os.path.basename(os.path.dirname(p)) + "-" + os.path.basename(p)),
                 os.environ["SAME_EVENTS_TEST_SHA_" + k.upper()]) for k, (p, _) in FILES.items()}
    N_DECLARED = int(os.environ["SAME_EVENTS_TEST_N"])
    NOATIME_OPTIONAL = True


def stop(msg):
    print(f"STOP: {msg}")
    sys.exit(2)


def open_noatime(path):
    flag = getattr(os, "O_NOATIME", None)
    if flag is None and not NOATIME_OPTIONAL:
        stop("this Python has no O_NOATIME")
    return os.fdopen(os.open(path, os.O_RDONLY | (flag or 0)), "rb")


def sha256(path):
    h = hashlib.sha256()
    with open_noatime(path) as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def load_columns(path, cols):
    """Only the named members of the npz, each checked for dtype and 1-D shape."""
    out = {}
    with open_noatime(path) as f:
        with np.load(f, allow_pickle=False) as z:
            missing = [c for c in cols if c not in z.files]
            if missing:
                stop(f"{path} lacks {missing} (has {sorted(z.files)})")
            for c, dt in cols.items():
                a = z[c]
                if a.dtype != np.dtype(dt) or a.ndim != 1:
                    stop(f"{path}:{c} is {a.dtype} {a.shape}, not {np.dtype(dt)} 1-D")
                out[c] = a
    n = {len(a) for a in out.values()}
    if len(n) != 1:
        stop(f"{path}: columns differ in length {sorted(n)}")
    return out


def increasing(a):
    return bool(np.all(a[1:] > a[:-1])) if len(a) > 1 else True


def compare(name, a5, a2):
    """a5 is EVW5D's float32 column, a2 EVW2D's float64 column, row by row."""
    a2_32 = a2.astype(np.float32)
    nan5, nan2 = int(np.isnan(a5).sum()), int(np.isnan(a2).sum())
    eq32 = int(np.sum(a5 == a2_32))
    d32 = np.abs(a5.astype(np.float64) - a2_32.astype(np.float64))   # exact difference of the two float32 values
    d64 = np.abs(a5.astype(np.float64) - a2)
    ulp = np.spacing(np.abs(a5)).astype(np.float64)
    over1 = int(np.sum(d32 > ulp))
    nz = d32[d32 > 0]
    dist = {}
    if nz.size:
        q = np.quantile(nz, [0.5, 0.9, 0.99, 1.0])
        dist = {"n_nonzero": int(nz.size), "median": float(q[0]), "p90": float(q[1]), "p99": float(q[2]),
                "max": float(q[3]), "in_ulps_max": float(np.max(d32[d32 > 0] / ulp[d32 > 0]))}
    r = {"rows": int(len(a5)), "nan_evw5d": nan5, "nan_evw2d": nan2, "exact_equal_float32": eq32,
         "max_abs_delta_float32": float(np.nanmax(d32)) if len(d32) else 0.0,
         "max_abs_delta_float64": float(np.nanmax(d64)) if len(d64) else 0.0,
         "rows_over_1_ulp": over1, "nonzero_delta_distribution": dist}
    print(f"T4 {name}: exact {eq32}/{len(a5)} after float32 cast; max|d| float32 {r['max_abs_delta_float32']:.9g}, "
          f"float64 {r['max_abs_delta_float64']:.9g}; rows over 1 ulp {over1}; NaN 5d {nan5} 2d {nan2}")
    if dist:
        print(f"    nonzero |d|: {dist}")
    return r


def main():
    rep = {"files": {}}
    for k, (p, want) in FILES.items():   # T0
        got = sha256(p)
        rep["files"][k] = {"path": p, "sha256": got, "expected": want}
        print(f"T0 {k} {p} {got} {'==' if got == want else '!='} {want}")
        if got != want:
            stop(f"{p} sha256 {got} is not the receipt's {want}")
    for side in ("evw5d", "evw2d"):   # constants: the key text and the declared row count
        with open_noatime(FILES[f"{side}_constants"][0]) as f:
            c = json.load(f)
        n = c.get("n_rows", c.get("rows"))
        key = c.get("key")
        rep[f"{side}_constants"] = {"key": key, "rows": n}
        print(f"T1 {side} constants.json key {json.dumps(key)}; rows {n}")
        if n != N_DECLARED:
            stop(f"{side} constants.json declares {n} rows, not {N_DECLARED}")
    w5 = load_columns(FILES["evw5d_weights"][0], COLS["evw5d"])   # T1
    w2 = load_columns(FILES["evw2d_weights"][0], COLS["evw2d"])
    n5, n2 = len(w5["entry"]), len(w2["entry"])
    rep["T2"] = {"n_evw5d": n5, "n_evw2d": n2, "declared": N_DECLARED, "pass": n5 == n2 == N_DECLARED}
    print(f"T2 rows evw5d {n5} evw2d {n2} declared {N_DECLARED}: {'PASS' if rep['T2']['pass'] else 'FAIL'}")
    if not rep["T2"]["pass"]:
        stop("row counts differ; no positional comparison is possible")
    e5, e2 = w5["entry"], w2["entry"]   # T3
    diff = np.flatnonzero(e5 != e2)
    rep["T3"] = {"evw5d_strictly_increasing": increasing(e5), "evw2d_strictly_increasing": increasing(e2),
                 "entries_equal": int(diff.size) == 0, "rows_differing": int(diff.size),
                 "first_differing_row": int(diff[0]) if diff.size else None,
                 "evw5d_entry_min_max": [int(e5.min()), int(e5.max())], "evw2d_entry_min_max": [int(e2.min()), int(e2.max())]}
    print(f"T3 entries: evw5d increasing {rep['T3']['evw5d_strictly_increasing']}, evw2d increasing "
          f"{rep['T3']['evw2d_strictly_increasing']}; equal {rep['T3']['entries_equal']} "
          f"(differing rows {diff.size}, first {rep['T3']['first_differing_row']}); "
          f"ranges {rep['T3']['evw5d_entry_min_max']} {rep['T3']['evw2d_entry_min_max']}")
    rep["T4"] = {c: compare(c, w5[c], w2[c]) for c in ("truth_pt", "truth_pz")}   # T4
    exact = all(rep["T4"][c]["exact_equal_float32"] == n5 for c in ("truth_pt", "truth_pz"))
    rep["T4"]["all_rows_exact_float32"] = exact
    if exact:
        rep["T5"] = "not run (T4 exact on every row)"
    else:   # T5: order-free, the sorted (pT, p||) float32 pairs
        p5 = np.lexsort((w5["truth_pz"], w5["truth_pt"]))
        p2 = np.lexsort((w2["truth_pz"].astype(np.float32), w2["truth_pt"].astype(np.float32)))
        same = (np.array_equal(w5["truth_pt"][p5], w2["truth_pt"].astype(np.float32)[p2])
                and np.array_equal(w5["truth_pz"][p5], w2["truth_pz"].astype(np.float32)[p2]))
        rep["T5"] = {"same_multiset_float32": bool(same)}
    print(f"T4 all rows exact in float32 (pT and p||): {exact}")
    print(f"T5 {rep['T5']}")
    verdict = "SAME-ROWS-SAME-ORDER" if exact else (
        "SAME-SET-DIFFERENT-ORDER" if isinstance(rep["T5"], dict) and rep["T5"]["same_multiset_float32"]
        else "NOT-EXACT")
    rep["verdict"] = verdict
    print(f"VERDICT {verdict}")
    print("JSON " + json.dumps(rep, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
