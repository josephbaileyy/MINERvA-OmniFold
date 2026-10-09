#!/usr/bin/env python3
"""Compare a regenerated sufficient-input npz (and its manifest) with the preserved release copy (G12).

Reports, separately: (1) file digests; (2) every array: key set, dtype, shape, exact equality, max |difference|;
(3) the manifests field by field, listing every differing JSON path. A digest difference is attributed to
serialization only when every array is exactly equal and the manifests differ only in fields that record the npz
digest itself. A last-bit difference is reported as NOT BIT-IDENTICAL, never as identity, and only when every
differing array is floating point with the same dtype and shape and a finite relative difference below 1e-9, and
every other manifest difference is a floating-point `/nulls/*/shift/*` statistic within the same bound. Anything
else (an integer, boolean or shape difference, a changed count or digest) is NOT REPRODUCED. Exit 0 only if every array is exactly equal and every manifest difference is so attributed.

  python3 compare_sufficient.py <regenerated.npz> <preserved.npz>
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


LAST_BITS = 1e-9  # relative bound for "differs in the last bits"
DIFFS: list[tuple[str, object, object]] = []  # (path, regenerated, preserved) for every differing JSON leaf


def last_bits_stat(path: str, a, b) -> bool:
    """A /nulls/<model>/shift/<field> float pair that differs by less than LAST_BITS relative."""
    parts = path.split("/")
    if not (len(parts) == 5 and parts[1] == "nulls" and parts[3] == "shift"):
        return False
    if not (isinstance(a, float) and isinstance(b, float)) or not np.isfinite([a, b]).all():
        return False
    return abs(a - b) <= LAST_BITS * max(abs(a), abs(b))


def diff_json(a, b, path="") -> list[str]:
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                DIFFS.append((f"{path}/{k}", a.get(k), b.get(k)))
                out.append(f"{path}/{k}: present in only one")
            else:
                out += diff_json(a[k], b[k], f"{path}/{k}")
        return out
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            DIFFS.append((path, a, b))
            return [f"{path}: list lengths {len(a)} vs {len(b)}"]
        out = []
        for i, (x, y) in enumerate(zip(a, b)):
            out += diff_json(x, y, f"{path}[{i}]")
        return out
    if a == b:
        return []
    DIFFS.append((path, a, b))
    return [f"{path}: {a!r} vs {b!r}"]


def main(argv) -> int:
    new, old = Path(argv[0]), Path(argv[1])
    dn, do = sha(new), sha(old)
    print(f"npz sha256: regenerated {dn} | preserved {do} | {'IDENTICAL' if dn == do else 'DIFFERENT'}")
    zn, zo = np.load(new, allow_pickle=False), np.load(old, allow_pickle=False)
    kn, ko = set(zn.files), set(zo.files)
    arrays_ok = kn == ko
    if kn != ko:
        print(f"key sets differ: only regenerated {sorted(kn - ko)}; only preserved {sorted(ko - kn)}")
    n_exact, worst_rel, worst_ulp = 0, 0.0, 0
    all_float_last_bits = True  # every differing array is float, same dtype and shape, finite, below LAST_BITS
    for k in sorted(kn & ko):
        a, b = zn[k], zo[k]
        same = a.dtype == b.dtype and a.shape == b.shape and np.array_equal(a, b, equal_nan=a.dtype.kind == "f")
        n_exact += same
        if not same:
            arrays_ok = False
            md = rel = float("nan"); ulp = -1
            all_float_last_bits = all_float_last_bits and a.shape == b.shape and a.dtype == b.dtype and a.dtype.kind == "f"
            if a.shape == b.shape and a.dtype == b.dtype and a.dtype.kind == "f":
                d = np.abs(a - b)
                md = float(np.nanmax(d))
                scale = float(np.nanmax(np.abs(b))) or 1.0
                rel = md / scale                                  # relative to the array's largest magnitude
                ai, bi = a.view(np.int64), b.view(np.int64)      # ULP distance (same-sign float64)
                ulp = int(np.max(np.abs(ai - bi)[np.sign(a) == np.sign(b)])) if np.any(np.sign(a) == np.sign(b)) else -1
                worst_rel, worst_ulp = max(worst_rel, rel), max(worst_ulp, ulp)
                if not (np.isfinite(rel) and rel < LAST_BITS and np.array_equal(np.isnan(a), np.isnan(b))):
                    all_float_last_bits = False
            print(f"ARRAY DIFFERS {k}: dtype {a.dtype}/{b.dtype} shape {a.shape}/{b.shape} max|diff| {md:.3g} "
                  f"(relative to max|value| {rel:.3g}; max ULP distance {ulp})")
    print(f"arrays: {n_exact} of {len(kn & ko)} exactly equal (dtype, shape, values); worst relative difference "
          f"{worst_rel:.3g}, worst ULP distance {worst_ulp}")
    mn = json.loads(Path(str(new) + ".manifest.json").read_text())
    mo = json.loads(Path(str(old) + ".manifest.json").read_text())
    d = diff_json(mn, mo)
    digest_only = [x for x in d if x.startswith("/npz_sha256:")]
    # fields that record WHERE inputs were read from (paths, the code root), not what they contained
    layout = [x for x in d if x not in digest_only and (x.split(":")[0].endswith("/path") or x.startswith("/code_root:"))]
    other = [x for x in d if x not in digest_only and x not in layout]
    print(f"manifest: {len(d)} differing field(s); npz_sha256 only: {len(digest_only)}; input-location fields: "
          f"{len(layout)}; other: {len(other)}")
    for x in layout:
        print("  LOCATION", x)
    for x in other[:40]:
        print("  MANIFEST", x)
    ms = sha(Path(str(new) + ".manifest.json")) == sha(Path(str(old) + ".manifest.json"))
    print(f"manifest sha256 {'IDENTICAL' if ms else 'DIFFERENT'}")
    where = " (the manifest differs only in where the inputs were read from)" if layout else ""
    if dn != do and arrays_ok and not other:
        print("VERDICT: every array exactly equal; the npz digest differs by serialization only" + where)
    elif dn == do and arrays_ok and not other:
        print("VERDICT: npz byte-identical" + where)
    elif (kn == ko and all_float_last_bits and
          all(last_bits_stat(p, x, y) for p, x, y in DIFFS if p != "/npz_sha256" and not
              (p.endswith("/path") or p == "/code_root"))):
        print(f"VERDICT: NOT BIT-IDENTICAL -- {len(kn & ko) - n_exact} array(s) differ in the last bits (worst relative "
              f"difference {worst_rel:.2g}); the manifests differ only in floating-point statistics derived from them")
    else:
        print("VERDICT: NOT REPRODUCED (see differences above)")
    return 0 if arrays_ok and not other else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
