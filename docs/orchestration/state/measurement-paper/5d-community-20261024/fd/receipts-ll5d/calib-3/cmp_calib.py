"""Compare an LL5D calibration record and ratio file with run 2's: the npz bitwise (every array), the json field by
field with code_sha256, timing, seconds, peak_rss_kib and atime set aside (they record the code and the run)."""
import hashlib, json, sys
import numpy as np
a_json, a_npz, b_json, b_npz = sys.argv[1:5]
SKIP = {"code_sha256", "timing", "seconds", "peak_rss_kib", "atime"}
for p in (a_json, a_npz, b_json, b_npz):
    print(hashlib.sha256(open(p, "rb").read()).hexdigest(), p)
za, zb = np.load(a_npz), np.load(b_npz)
print("npz keys equal:", sorted(za.files) == sorted(zb.files), len(za.files))
diff = [k for k in sorted(set(za.files) | set(zb.files)) if k not in za.files or k not in zb.files
        or za[k].dtype != zb[k].dtype or za[k].shape != zb[k].shape or za[k].tobytes() != zb[k].tobytes()]
print("npz arrays differing bitwise:", diff)
ja, jb = json.load(open(a_json)), json.load(open(b_json))
keys = sorted(set(ja) | set(jb))
same, differ = [], []
for k in keys:
    if k in SKIP:
        continue
    (same if json.dumps(ja.get(k), sort_keys=True) == json.dumps(jb.get(k), sort_keys=True) else differ).append(k)
print("json fields identical:", same)
print("json fields differing:", differ)
print("set aside:", sorted(SKIP & set(keys)))
print("code_sha256 differs only in:", sorted(k for k in set(ja["code_sha256"]) | set(jb["code_sha256"])
                                             if ja["code_sha256"].get(k) != jb["code_sha256"].get(k)))
