#!/usr/bin/env python3
"""G-stab-F2 (contract amendment 2): row-order sensitivity of every F2 arm type.

Compares each permuted re-run (``construction/stab/``) with the construction's own product, bin by
bin on the F2 central value's positive cells: gate ``max |x_perm - x_ref| / |x_ref| <= 1e-6`` for
every pair. Also requires each permuted run's evidence file to show a permuted loop call and the
F2 parameters (no problems), so a probe whose permutation never happened cannot pass.

MEASURES: order sensitivity per code path. CANNOT AUTHORIZE: coverage, or insensitivity to choices
F2 fixes by definition.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

import s5c_assemble

C = "/pscratch/sd/j/josephrb/s5c-20260924/runs/construction"
PAIRS = {
    "boot_1": (f"{C}/boot/res_boot_1.npz", f"{C}/stab/res_boot_1.npz", f"{C}/stab/ev_boot_1.json"),
    "sweep_Flux_0": (f"{C}/sweep/5d_xsec_MEFHC_5iter_lgbm_uni_full_Flux_0.root",
                     f"{C}/stab/5d_xsec_MEFHC_5iter_lgbm_uni_full_Flux_0.root", f"{C}/stab/ev_sweep_Flux_0.json"),
    "throw_0": (f"{C}/throw/uthrow5d_slab_0.npz", f"{C}/stab/uthrow5d_slab_0.npz", f"{C}/stab/ev_throw_0.json"),
    "split_1": (f"{C}/split/res_split_1.npz", f"{C}/stab/res_split_1.npz", f"{C}/stab/ev_split_1.json"),
    "det_GEANT_Pion_0": (f"{C}/det/5d_det_GEANT_Pion_0.root", f"{C}/stab/5d_det_GEANT_Pion_0.root", f"{C}/stab/ev_GEANT_Pion_0.json"),
    "lat_BeamAngleX_0": (f"{C}/lat/5d_lat_BeamAngleX_0.root", f"{C}/stab/5d_lat_BeamAngleX_0.root", f"{C}/stab/ev_BeamAngleX_0.json"),
}


def vectors(path: str) -> np.ndarray:
    if path.endswith(".npz"):
        z = np.load(path, allow_pickle=True)
        if "xs" in z.files:  # throw slab: one row per throw, already on the throw support
            return np.asarray(z["xs"], float)
        return np.asarray(z["xsec_flat"], float)[None, :]
    return s5c_assemble.read_flat(path)[None, :]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--central", required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    rows = np.flatnonzero(s5c_assemble.read_flat(a.central) > 0)
    res = {"schema": "s5c-gstab/1", "threshold": 1e-6, "pairs": {}}
    ok = True
    for name, (ref, perm, ev) in PAIRS.items():
        if not (Path(ref).exists() and Path(perm).exists() and Path(ev).exists()):
            res["pairs"][name] = {"status": "MISSING", "ref": Path(ref).exists(), "perm": Path(perm).exists()}
            ok = False
            continue
        e = json.loads(Path(ev).read_text())
        permuted = any(c.get("kind") == "permutation" for c in e["calls"])
        R, P = vectors(ref), vectors(perm)
        if R.shape[1] != rows.size and R.shape[1] > rows.size:
            R, P = R[:, rows], P[:, rows]
        pos = np.abs(R) > 0
        d = float(np.max(np.abs(P[pos] - R[pos]) / np.abs(R[pos])))
        good = permuted and not e["problems"] and d <= 1e-6
        ok &= good
        res["pairs"][name] = {"status": "PASS" if good else "FAIL", "max_rel_diff": d, "permuted": permuted,
                              "evidence_problems": e["problems"], "shape": list(R.shape)}
    res["verdict"] = "PASS" if ok else ("INCOMPLETE" if any(p["status"] == "MISSING" for p in res["pairs"].values()) else "FAIL")
    a.out.write_text(json.dumps(res, indent=1))
    print(json.dumps({k: (v.get("status"), v.get("max_rel_diff")) for k, v in res["pairs"].items()} | {"verdict": res["verdict"]}))
    return {"PASS": 0, "FAIL": 1, "INCOMPLETE": 4}[res["verdict"]]


if __name__ == "__main__":
    raise SystemExit(main())
