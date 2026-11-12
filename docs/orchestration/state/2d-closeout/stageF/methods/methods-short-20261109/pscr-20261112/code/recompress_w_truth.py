"""Losslessly recompress the fetched w_truth.npz (stored, 52.7 MB) to w_truth.npz.zip-deflated (9 MB) for git.

Usage: python -I recompress_w_truth.py <fetched w_truth.npz> <out w_truth_z.npz>
Every array is written unchanged with np.savez_compressed, re-read, and compared bitwise (dtype, shape, bytes)
with the fetched member; any difference: the output is deleted, exit 3. Prints both files' sha256.
"""
import hashlib, os, sys
import numpy as np

src, out = sys.argv[1:3]
z = np.load(src, allow_pickle=False)
d = {k: z[k] for k in z.files}
np.savez_compressed(out, **d)
y = np.load(out, allow_pickle=False)
if sorted(y.files) != sorted(d) or any(y[k].dtype != d[k].dtype or y[k].shape != d[k].shape
                                       or y[k].tobytes() != d[k].tobytes() for k in d):
    os.unlink(out); print("STOP: recompressed arrays differ from the fetched member"); sys.exit(3)
for p in (src, out):
    print(hashlib.sha256(open(p, "rb").read()).hexdigest(), os.path.getsize(p), p.rsplit("/", 1)[-1])
print("RECOMPRESS OK: all", len(d), "arrays bitwise equal")
