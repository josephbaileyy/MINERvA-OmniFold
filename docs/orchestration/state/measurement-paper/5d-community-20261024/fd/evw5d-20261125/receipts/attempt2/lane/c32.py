import sys, numpy as np
z = np.load(sys.argv[1], allow_pickle=False)
print({k: (z[k].shape, z[k].dtype) for k in z.files})
d = z["denom_nd"].astype(np.float64).ravel(); o = z["ofin"].astype(np.float64).ravel(); c = z["completeness"].ravel()
shape = z["denom_nd"].shape
bad = np.flatnonzero((d > 0) & (np.abs(c - 1) > 1e-12))
print("n bad", bad.size, "shape", shape)
diff = o - d
print("sum diff over bad", diff[bad].sum(), "sum |diff| bad", np.abs(diff[bad]).sum(), "sum diff all", diff.sum())
for i in bad:
    idx = np.unravel_index(i, shape)
    print(idx, f"denom={d[i]:.6f} ofin={o[i]:.6f} diff={diff[i]:+.6e} c-1={c[i]-1:+.3e}")
