#!/usr/bin/env python3
"""V-HALF-R's first-build precondition (V-HALF-R-BINDING-1; AMENDMENT-1 A3.4's weights rule and A8.2 2a): w_truth is
finite and nonnegative on every row that a share or a tilt counts, in the pinned 5D MC npz.

Reads only MCgen, pass_truth and w_truth (allow_pickle=False), through an O_NOATIME descriptor, after the file's sha256
is checked against the pin. Ω (AMENDMENT-1 A2) is the set of fine cells whose H2 box is reported, built from the pinned
h2_definition.json and s5p_stage1_inspect's grid; the fine-cell -> reporting-cell map it implies must hash to that
record's fine_map_sha256_int32le.

Four row sets are counted:
  all        every row;
  pass_truth rows with pass_truth;
  shares     pass_truth rows whose true fine cell is in Ω (truth_sel within Ω: A2, A3.4);
  tilt       rows inside the fine grid on every axis whose true fine cell is in Ω, any pass_truth (A8.2 2a).
PASS needs no non-finite and no negative w_truth in `shares` and in `tilt`. The other two sets are descriptive.

Exit 0 PASS, 3 FAIL, 2 refusal (a pin, a key, a shape or the fine-map check). Writes one JSON record to --out.
MEASURES: counts and extrema of w_truth on the four sets. CANNOT AUTHORIZE: a build, a binning or any V-HALF quantity.
"""
import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[6]
sys.path.insert(0, str(REPO / "nd-unfolding"))
import s5p_stage1_inspect as s1  # noqa: E402

NPZ_SHA256 = "07fccc1abc7204bc29349b4ba96850986fe91e909e83fc54e8d1a6b3922a649f"
H2_DEF = REPO / "nd-unfolding/pv-ladder/readouts/h2_definition.json"
H2_DEF_SHA256 = "b67907615fe2e903e60ae6caa1c141fa007676c0a1b3ae9f42490d331bfdda89"
KEYS = ("MCgen", "pass_truth", "w_truth")
NOATIME = getattr(os, "O_NOATIME", 0)


class Refusal(Exception):
    pass


def require(ok, msg):
    if not ok:
        raise Refusal(msg)


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def omega_mask(h2def):
    """Ω as a boolean over the flat fine grid, and the sha256 of the implied fine -> reporting-cell map (int32 LE)."""
    h2_of_fine, n_h2 = s1.coarse_map(s1.H2_EDGES)
    require(n_h2 == 32, f"the H2 grid has {n_h2} boxes, not 32")
    lut = np.asarray(h2def["h2_to_reporting_cell"], dtype=np.int64)
    require(lut.shape == (32,), "h2_to_reporting_cell is not 32 long")
    unreported = sorted(b for grp in h2def["unreported_boxes"] for b in grp)
    require(unreported == sorted(np.flatnonzero(lut < 0).tolist()),
            "unreported_boxes and h2_to_reporting_cell's -1 entries differ")
    fine_to_cell = lut[h2_of_fine].astype("<i4")
    return fine_to_cell >= 0, hashlib.sha256(fine_to_cell.tobytes()).hexdigest()


def stats(w):
    finite = np.isfinite(w)
    wf = w[finite]
    return {"rows": int(w.size), "nonfinite": int((~finite).sum()), "negative": int((wf < 0).sum()),
            "zero": int((wf == 0).sum()), "min": float(wf.min()) if wf.size else None,
            "max": float(wf.max()) if wf.size else None, "sum": float(wf.sum())}


def check(npz_path, expect_npz_sha=NPZ_SHA256, h2def_path=H2_DEF, expect_h2def_sha=H2_DEF_SHA256):
    raw = Path(h2def_path).read_bytes()
    require(sha256_bytes(raw) == expect_h2def_sha, "h2_definition.json's sha256 differs from the pin")
    h2def = json.loads(raw)
    omega, map_sha = omega_mask(h2def)
    require(map_sha == h2def["fine_map_sha256_int32le"],
            f"the fine map built from the grid ({map_sha[:16]}) differs from h2_definition.json's")
    fd = os.open(npz_path, os.O_RDONLY | NOATIME)
    with os.fdopen(fd, "rb") as fh:
        h = hashlib.sha256()
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
        require(h.hexdigest() == expect_npz_sha, "the npz's sha256 differs from the pin")
        fh.seek(0)
        with np.load(fh, allow_pickle=False) as z:
            require(all(k in z.files for k in KEYS), f"the npz lacks one of {KEYS}")
            gen = np.asarray(z["MCgen"], dtype=float)
            pt = np.asarray(z["pass_truth"]).astype(bool)
            wt = np.asarray(z["w_truth"], dtype=float)
    require(gen.ndim == 2 and gen.shape[1] == len(s1.AXES), f"MCgen has shape {gen.shape}")
    require(pt.shape == wt.shape == (gen.shape[0],), "pass_truth, w_truth and MCgen differ in length")
    ft = s1.fine_index(gen)
    in_omega = (ft >= 0) & omega[np.maximum(ft, 0)]
    sets = {"all": np.ones(wt.size, bool), "pass_truth": pt, "shares": pt & in_omega, "tilt": in_omega}
    out = {name: stats(wt[m]) for name, m in sets.items()}
    gated = ("shares", "tilt")
    ok = all(out[k]["nonfinite"] == 0 and out[k]["negative"] == 0 for k in gated)
    return {"schema": "vhr-wtruth-check/1", "verdict": "PASS" if ok else "FAIL", "gated_sets": list(gated),
            "sets": out, "omega_fine_cells": int(omega.sum()), "fine_cells": int(omega.size),
            "inputs": {"npz_sha256": expect_npz_sha, "h2_definition_sha256": expect_h2def_sha,
                       "keys_read": list(KEYS), "fine_map_sha256_int32le": map_sha},
            "o_noatime": bool(NOATIME)}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--npz", required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if sys.platform.startswith("linux") and not NOATIME:
        print("REFUSED: O_NOATIME is unavailable on this Linux build")
        return 2
    try:
        rec = check(a.npz)
    except Refusal as e:
        print(f"REFUSED: {e}")
        return 2
    with a.out.open("x") as f:
        json.dump(rec, f, indent=2, sort_keys=True, allow_nan=False)
        f.write("\n")
    print(f"VHR-WTRUTH {rec['verdict']}: " + "; ".join(
        f"{k} rows {v['rows']} nonfinite {v['nonfinite']} negative {v['negative']}" for k, v in rec["sets"].items()))
    return 0 if rec["verdict"] == "PASS" else 3


if __name__ == "__main__":
    sys.exit(main())
