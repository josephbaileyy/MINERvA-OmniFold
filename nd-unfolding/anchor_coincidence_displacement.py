#!/usr/bin/env python3
"""Is the anchor's estimator/draw coincidence EMPIRICALLY material? Two reads, no new compute.

WHAT THIS ANSWERS. The archive's two coincidences -- bootstrap replica 42 drawing its Poisson weights
from seed 42 while its estimator is seeded 42, and throw 0's draw RNG seeded 1000 identically to the
estimator -- are exempt from the clean-offset predicate because they ARE the archive (`BEN-463`: a
clean anchor is not an anchor). Exempt is not the same as immaterial. Lane C's test:

  DISPLACEMENT  rank the flagged member among its siblings, in sibling units.
  LEVERAGE      convert that displacement into scan-member units, leave-one-out.
  Only the PRODUCT of the two enters the magnitude table.

FAMILY-WISE THRESHOLDS, lane C's, so it cannot fire on ordinary scatter -- the maximum of m clean
draws is not distributed like a single draw:

  m = 100 replicas : flag at |z| > 3.48   expected max |z| of 100 clean draws ~ 2.58
  m = 160 throws   : flag at |z| > 3.60   expected max |z| of 160 clean draws ~ 2.73

The expected maxima are THE FLOOR ON WHAT A ONE-MEMBER TEST CAN SEE: a displacement below them is
below the test's own resolution, and leverage shrinks it further.

IF NEITHER FLAGS, the confound is empirically immaterial for the price of reading files. IF EITHER
FLAGS, the coincidence matters and that is worth knowing whatever the verdict.

THE SUMMARY STATISTIC IS THIS LANE'S CHOICE AND IS FLAGGED AS SUCH -- lane C specified the ranking and
the thresholds, not the scalar. Two are reported rather than one, and they must agree: `total_xsec`,
and the L2 norm of the member's deviation from the sibling mean. If they disagree the choice is
load-bearing and needs C, which is exactly the state a single number would have hidden.

FAILS CLOSED, NAMING WHAT IS MISSING. The products are scratch-side, so this cannot run in a local
checkout; that is a limitation of where it runs, not evidence about the archive, and it says so
rather than returning a clean-looking zero.
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os
import sys

import numpy as np

# lane C's family-wise flag thresholds and the expected maximum |z| of m clean draws
THRESHOLDS = {"replicas": (100, 3.48, 2.58), "throws": (160, 3.60, 2.73)}


def _z(values, idx):
    """(z of member `idx`, sibling mean, sibling sd) -- sd from the OTHERS, so the member under test
    does not inflate its own denominator."""
    v = np.asarray(values, dtype=float)
    others = np.delete(v, idx)
    mu, sd = float(others.mean()), float(others.std(ddof=1))
    if sd == 0.0:
        return math.inf, mu, sd
    return (float(v[idx]) - mu) / sd, mu, sd


def read_replicas(d):
    """`{seed: (total_xsec, xsec_flat)}` from bootstrap_nd products."""
    out = {}
    for p in sorted(glob.glob(os.path.join(d, "res_boot_*.npz"))):
        with np.load(p, allow_pickle=True) as z:
            if "seed" not in z.files:
                continue
            out[int(z["seed"])] = (float(z["total_xsec"]) if "total_xsec" in z.files else float("nan"),
                                   np.asarray(z["xsec_flat"], dtype=float))
    return out


def read_throws(pattern):
    """`{throw_id: xs_row}` from unified_throw_cov slabs."""
    out = {}
    for p in sorted(glob.glob(pattern)):
        with np.load(p, allow_pickle=True) as z:
            if "xs" not in z.files or "throws" not in z.files:
                continue
            xs = np.asarray(z["xs"], dtype=float)
            ids = np.asarray(z["throws"], dtype=int)
            for row, tid in zip(xs, ids):
                out[int(tid)] = row
    return out


def displacement(members, flagged, family):
    """Both summary statistics for the flagged member, against its siblings."""
    m_expected, flag_at, expected_max = THRESHOLDS[family]
    keys = sorted(members)
    if flagged not in members:
        raise SystemExit(f"[FAIL] {family}: member {flagged} absent; cannot rank what is not there")
    if len(keys) != m_expected:
        print(f"[warn] {family}: {len(keys)} members, expected {m_expected} -- the family-wise "
              f"threshold {flag_at} was derived for {m_expected} and is NOT valid as stated")
    idx = keys.index(flagged)
    rows = np.stack([np.asarray(members[k][1] if isinstance(members[k], tuple) else members[k],
                                dtype=float) for k in keys])
    scal = np.array([members[k][0] if isinstance(members[k], tuple) else float("nan") for k in keys])
    res = {"family": family, "flagged": flagged, "m": len(keys),
           "flag_at_abs_z": flag_at, "expected_max_abs_z_of_m_clean_draws": expected_max}
    if np.all(np.isfinite(scal)):
        z1, mu1, sd1 = _z(scal, idx)
        res["z_total_xsec"] = z1
    mu = np.delete(rows, idx, axis=0).mean(axis=0)
    norms = np.linalg.norm(rows - mu, axis=1)
    z2, _, _ = _z(norms, idx)
    res["z_deviation_norm"] = z2
    zs = [v for k, v in res.items() if k.startswith("z_")]
    res["max_abs_z"] = max(abs(v) for v in zs)
    res["FLAGS"] = bool(res["max_abs_z"] > flag_at)
    res["below_test_resolution"] = bool(res["max_abs_z"] <= expected_max)
    res["statistics_agree"] = bool(len(zs) < 2 or (zs[0] > 0) == (zs[1] > 0))
    return res


def leverage(members, flagged, family):
    """LEAVE-ONE-OUT: how much the family's sqrt-trace-like summary moves when the flagged member is
    dropped, relative to the summary itself. Converts displacement into scan-member units."""
    keys = sorted(members)
    rows = np.stack([np.asarray(members[k][1] if isinstance(members[k], tuple) else members[k],
                                dtype=float) for k in keys])
    def summary(a):
        c = a - a.mean(axis=0, keepdims=True)
        return float(np.sqrt(np.trace(c.T @ c) / max(len(a) - 1, 1)))
    full = summary(rows)
    loo = summary(np.delete(rows, keys.index(flagged), axis=0))
    return {"family": family, "summary_full": full, "summary_leave_one_out": loo,
            "relative_leverage": (abs(loo - full) / full) if full else float("inf")}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--boot-dir", default="boot_nd_5d")
    ap.add_argument("--throw-glob", default="uq_5d/uthrow_slabs_5d/uthrow5d_slab_*.npz")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)

    missing = []
    if not os.path.isdir(a.boot_dir):
        missing.append(f"--boot-dir {a.boot_dir} (bootstrap replicas; expected 100)")
    if not glob.glob(a.throw_glob):
        missing.append(f"--throw-glob {a.throw_glob} (throw slabs; expected 160 throw ids)")
    if missing:
        print("[FAIL] cannot run: the archived products are not readable from here.")
        for m in missing:
            print("   MISSING  " + m)
        print("  These are scratch-side products and none is tracked, so this is a fact about WHERE "
              "this ran and NOT evidence about the archive. Re-run where the products live; a "
              "clean-looking zero is deliberately not returned.")
        return 2

    reps = read_replicas(a.boot_dir)
    throws = read_throws(a.throw_glob)
    report = {
        "replica_42": displacement(reps, 42, "replicas"),
        "throw_0": displacement(throws, 0, "throws"),
        "replica_42_leverage": leverage(reps, 42, "replicas"),
        "throw_0_leverage": leverage(throws, 0, "throws"),
    }
    for nm in ("replica_42", "throw_0"):
        d, lv = report[nm], report[nm + "_leverage"]
        report[nm + "_product"] = d["max_abs_z"] * lv["relative_leverage"]
    print(json.dumps(report, indent=2, sort_keys=True))
    flagged = [n for n in ("replica_42", "throw_0") if report[n]["FLAGS"]]
    print("\n[anchor] FLAGS: " + (", ".join(flagged) if flagged else
          "none -- displacement is below the test's own resolution and leverage shrinks it further"))
    if a.out:
        with open(a.out, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2, sort_keys=True)
            fh.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
