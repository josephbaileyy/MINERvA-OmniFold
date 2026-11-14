"""Informational (the director, 2026-11-13; gates nothing): A_2p2h_0 (G2R D_Ua, --miss-map) against part B's U_2p2h_0
(the same row without the map), cell by cell. Usage: python3 -I dua-vs-partb-2p2h0.py <partb xsec.root> <G2R xsec.root>"""
import sys, json, hashlib, uproot, numpy as np
b_path, a_path = sys.argv[1], sys.argv[2]
for p in (b_path, a_path):
    print("sha256", hashlib.sha256(open(p, "rb").read()).hexdigest(), p)
fb, fa = uproot.open(b_path), uproot.open(a_path)
cb, ca = json.loads(fb["runConfig"].member("fTitle")), json.loads(fa["runConfig"].member("fTitle"))
print("runConfig keys that differ:", sorted(k for k in set(cb) | set(ca) if cb.get(k) != ca.get(k)))
for name in ("hXSec2D", "hUnfold2D"):
    b, a = fb[name].values(), fa[name].values()
    nz = b != 0
    rel = np.abs(a[nz] / b[nz] - 1)
    print(f"{name}: cells b!=0 {int(nz.sum())}; cells changed {int((a != b).sum())}; max|a/b-1| {rel.max():.6e}; "
          f"median {np.median(rel):.3e}; >1e-3 {int((rel > 1e-3).sum())}; >1e-2 {int((rel > 1e-2).sum())}; "
          f"a!=0 where b==0 {int(((a != 0) & ~nz).sum())}")
