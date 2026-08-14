#!/usr/bin/env python3
"""OI-120(a) step 1: what is actually IN the Leg F weights npz?

Read-only. Determines whether a cross-section vector can be built with zero GPU time
(i.e. a push vector is already stored) or whether it needs a model-inference pass.
"""
import json
import os

import numpy as np

P = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet"
FILES = [
    ("draw1_member1", f"{P}/fullevent_ml_ensemble/member_1/pet_fullevent_ml_member1_weights.npz"),
    ("draw2", f"{P}/fullevent_floor_42_0/draw_2/pet_fullevent_floor_draw2_weights.npz"),
    ("draw3", f"{P}/fullevent_floor_42_0/draw_3/pet_fullevent_floor_draw3_weights.npz"),
    ("draw4", f"{P}/fullevent_floor_42_0/draw_4/pet_fullevent_floor_draw4_weights.npz"),
    ("draw5", f"{P}/fullevent_floor_42_0/draw_5/pet_fullevent_floor_draw5_weights.npz"),
]

out = {}
for tag, path in FILES:
    if not os.path.exists(path):
        out[tag] = {"present": False, "path": path}
        continue
    rec = {"present": True, "path": path, "bytes": os.path.getsize(path)}
    with np.load(path, allow_pickle=True) as z:
        rec["keys"] = sorted(z.files)
        det = {}
        for k in z.files:
            try:
                a = z[k]
            except Exception as e:                     # noqa: BLE001
                det[k] = f"<unreadable: {e}>"
                continue
            if isinstance(a, np.ndarray) and a.dtype == object:
                det[k] = {"dtype": "object", "shape": list(a.shape)}
            elif isinstance(a, np.ndarray) and a.ndim == 0:
                v = a.item()
                det[k] = {"scalar": (v.decode() if isinstance(v, bytes) else v)
                          if not isinstance(v, dict) else "<dict>"}
            else:
                det[k] = {"dtype": str(a.dtype), "shape": list(a.shape)}
                if a.size and np.issubdtype(a.dtype, np.number):
                    f = np.asarray(a, np.float64).ravel()
                    det[k]["finite_frac"] = float(np.isfinite(f).mean())
                    ff = f[np.isfinite(f)]
                    if ff.size:
                        det[k]["min"] = float(ff.min())
                        det[k]["max"] = float(ff.max())
                        det[k]["sum"] = float(ff.sum())
        rec["detail"] = det
    out[tag] = rec

print(json.dumps(out, indent=1, sort_keys=True))
