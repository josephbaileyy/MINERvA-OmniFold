"""IBU-1 control K-B1 (BINDING-C.md ruling 2): compare a recomputed product with the kept B1 product.

Reading fixed with the director before any result: the array names and the meta keys must be the same sets in
both files; every array must match in dtype, shape, bytes and ``np.array_equal``; every meta field must be equal
except exactly ``seconds_build`` and ``seconds_ibu`` (wall-clock timings), which must be present in both. Prints one JSON line per pair and exits non-zero on any mismatch.
"""
import json
import sys

import numpy as np

TIMINGS = ("seconds_build", "seconds_ibu")


def compare(kept_path: str, new_path: str) -> dict:
    kept, new = np.load(kept_path, allow_pickle=False), np.load(new_path, allow_pickle=False)
    same_array_names = set(kept.files) == set(new.files)
    arrays = {}
    for k in sorted(set(kept.files) & set(new.files) - {"meta"}):
        a, b = kept[k], new[k]
        arrays[k] = bool(a.dtype == b.dtype and a.shape == b.shape and a.tobytes() == b.tobytes()
                         and np.array_equal(a, b, equal_nan=a.dtype.kind in "fc"))
    mk, mn = json.loads(str(kept["meta"])), json.loads(str(new["meta"]))
    same_meta_keys = set(mk) == set(mn) and all(t in mk for t in TIMINGS)
    timings = {t: (mk.pop(t, None), mn.pop(t, None)) for t in TIMINGS}
    differing_meta = sorted(k for k in set(mk) | set(mn) if mk.get(k) != mn.get(k))
    ok = same_array_names and all(arrays.values()) and same_meta_keys and not differing_meta
    return {"kept": kept_path, "new": new_path, "pass": ok, "same_array_names": same_array_names,
            "arrays_identical": arrays, "same_meta_keys": same_meta_keys, "differing_meta": differing_meta,
            "timings_kept_new": timings}


if __name__ == "__main__":
    pairs = sys.argv[1:]
    results = [compare(pairs[i], pairs[i + 1]) for i in range(0, len(pairs), 2)]
    for r in results:
        print(json.dumps(r, default=str))
    sys.exit(0 if all(r["pass"] for r in results) else 1)
