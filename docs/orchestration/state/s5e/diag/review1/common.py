"""Reviewer's own helpers (independent of s5e_analyze_diag.py). U from s5c_coverage only."""
import json, sys, hashlib
import numpy as np
DEP = "/pscratch/sd/j/josephrb/s5e-20260925/deploy/700797e3"
RUNS = "/pscratch/sd/j/josephrb/s5e-20260925/runs/diag"
S5N = "/pscratch/sd/j/josephrb/s5n-20260925/runs"
sys.path.insert(0, DEP + "/nd-unfolding")
import s5c_coverage  # noqa
U, NAMES = s5c_coverage.reported_functionals(json.load(open(DEP + "/docs/orchestration/state/s5c/contract.json")))
SHAPE = (14, 16, 7, 7, 6)

def L(path):
    z = np.load(path, allow_pickle=False)
    d = {k: np.asarray(z[k]) for k in z.files if k != "meta"}
    d["meta"] = json.loads(str(z["meta"])) if "meta" in z.files else {}
    return d

def R(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    return (a - b) / b

def ew(r):  # median/max |.| over the 42 EW cells, percent
    a = np.abs(np.asarray(r)[:42])
    return round(100 * float(np.median(a)), 3), round(100 * float(a.max()), 3), "EW%d" % int(a.argmax())

def ewproj(h5):
    return np.asarray(h5, float).reshape(SHAPE).sum(axis=(0, 1, 3)).ravel()

def chi2(a, b, v):
    a, b, v = (np.asarray(x, float) for x in (a, b, v))
    ok = v > 0
    return float(((a[ok] - b[ok]) ** 2 / v[ok]).sum()), int(ok.sum())

def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 24), b""):
            h.update(blk)
    return h.hexdigest()
