#!/usr/bin/env python3
"""1B's CV denominator per row (FD-1B-STAGED-ADDENDUM-A2-1.md, S3 as the director ruled it, (d1)): the bank's cv.npz
holds the truth-denominator rows' coordinates but no CV weight, so C2's row clip of the denominator needs the CV's
w_truth read from the source tree, mc_truth_denom, as cov2d reads it (uproot, O_NOATIME).

Two row sets are rebuilt from the same entries, each with its writer's gate:
* the bank's (sweep_bank_5d.py's truth_denom loop): pT, p_par and w finite, 0 <= w < 1e4, in the truth phase space;
* the npz's (nn_dump_inputs.py through collect_truth_denom_nd): the same, and every extra axis finite.
The phase space is u2d.in_truth_phase_space: the analysis rectangle and atan2(pT, p_par) < 20 degrees (math.atan2,
row by row). Before the weights may be used, BOTH must hold, and either failure goes to the director:
(A) the bank row set's coordinates, as float32, equal cv.npz's td_* row by row;
(B) the histogram of cv.npz's td_* coordinates weighted by the CV weight (w x POT scale) equals the npz's denom_nd
    bitwise, which is what compose's per-row composite needs.
Also recorded: (C) the npz row set's float64 histogram against denom_nd (its writer reproduced), and (D) every
detector universe's denom_nd against the npz's, bitwise (the detector deltas must be zero).

  python fd_1b_cvdenom.py --root R --npz N --expect-npz-sha256 S --bank B --detector-dir D --pins P
      --expect-pins-sha256 S --out O.json      (writes O.json, and O.npy, the bank rows' CV weight, only on PASS)

MEASURES: row alignment and bitwise equalities. CANNOT AUTHORIZE: use of the weights when (A), (B) or (D) fail.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np

SCHEMA = "fd-1b-cvdenom/1"
TREE = "mc_truth_denom"
KEYS = ("MC", "MC_pz", "MC_eavail", "MC_q3", "MC_W", "w_truth")
TD = ("td_pt", "td_pz", "td_ea", "td_q3", "td_w")
W_MAX = 1e4
MAX_MUON_THETA_RAD = math.radians(20.0)              # unfold_2d_omnifold_unbinned.MAX_MUON_THETA_RAD
DETECTOR_BANDS = ("GEANT_Neutron", "GEANT_Pion", "GEANT_Proton", "MinosEfficiency")
NOATIME = getattr(os, "O_NOATIME", None)
OPENED: dict[str, int] = {}


class Refusal(RuntimeError):
    pass


def open_noatime(path) -> io.BufferedReader:
    if NOATIME is None:
        raise Refusal("O_NOATIME is not available on this platform: refusing a plain read")
    fd = os.open(path, os.O_RDONLY | NOATIME)
    OPENED.setdefault(str(path), os.fstat(fd).st_atime_ns)
    return os.fdopen(fd, "rb")


def read_noatime(path) -> tuple[bytes, str]:
    with open_noatime(path) as fh:
        raw = fh.read()
    return raw, hashlib.sha256(raw).hexdigest()


def in_phase_space(pt: np.ndarray, pz: np.ndarray, pt_lo, pt_hi, pz_lo, pz_hi) -> np.ndarray:
    """u2d.in_truth_phase_space row by row: finite, inside the rectangle, and math.atan2(pt, pz) < 20 degrees."""
    box = np.isfinite(pt) & np.isfinite(pz) & (pt >= pt_lo) & (pt <= pt_hi) & (pz >= pz_lo) & (pz <= pz_hi)
    out = np.zeros(pt.size, bool)
    idx = np.flatnonzero(box)
    out[idx] = [math.atan2(float(a), float(b)) < MAX_MUON_THETA_RAD for a, b in zip(pt[idx], pz[idx])]
    return out


def row_sets(a: dict, edges) -> tuple[np.ndarray, np.ndarray]:
    """(bank rows, npz rows) of mc_truth_denom by the two writers' gates."""
    pt, pz, w = a["MC"], a["MC_pz"], a["w_truth"]
    ps = in_phase_space(pt, pz, edges[0][0], edges[0][-1], edges[1][0], edges[1][-1])
    base = np.isfinite(pt) & np.isfinite(pz) & np.isfinite(w) & (w >= 0) & (w < W_MAX)
    extras = np.isfinite(a["MC_eavail"]) & np.isfinite(a["MC_q3"]) & np.isfinite(a["MC_W"])
    return base & ps, base & extras & ps


def histogram(cols: list[np.ndarray], w: np.ndarray, edges) -> np.ndarray:
    counts, _ = np.histogramdd(np.column_stack(cols), bins=[np.asarray(e, float) for e in edges], weights=w)
    return counts


def checks(a: dict, pot_scale: float, cv: dict, denom_nd: np.ndarray, edges) -> tuple[dict, np.ndarray]:
    """(A)-(C) on the arrays read; returns the record and the bank rows' CV weight (w x POT scale, float64)."""
    bank, npz = row_sets(a, edges)
    coords = [a[k] for k in KEYS[:5]]
    tdw_cv = a["w_truth"][bank] * pot_scale
    td = [np.asarray(cv[k]) for k in TD]
    n_cv = td[0].size
    aligned = bool(int(bank.sum()) == n_cv and all(
        np.array_equal(np.asarray(c[bank], np.float32), np.asarray(t, np.float32), equal_nan=True)
        for c, t in zip(coords, td)))                 # the bank keeps rows whose extra axes are NaN, as NaN
    rec = {"entries": int(a["w_truth"].size), "bank_rows": int(bank.sum()), "cv_npz_rows": n_cv,
           "npz_rows": int(npz.sum()), "bank_rows_not_npz": int(np.sum(bank & ~npz)),
           "A_coordinates_equal_row_by_row": aligned}
    if aligned:
        h = histogram([np.asarray(t, np.float64) for t in td], tdw_cv, edges)
        rec["B_histogram_equals_denom_nd"] = bool(np.array_equal(h, denom_nd))
        rec["B_max_abs_difference"] = float(np.max(np.abs(h - denom_nd)))
    else:
        rec["B_histogram_equals_denom_nd"] = False
        rec["B_max_abs_difference"] = None
    hc = histogram([c[npz] for c in coords], a["w_truth"][npz] * pot_scale, edges)
    rec["C_npz_writer_reproduced"] = bool(np.array_equal(hc, denom_nd))
    rec["C_max_abs_difference"] = float(np.max(np.abs(hc - denom_nd)))
    return rec, tdw_cv


def detector_check(det_dir: Path, pins: dict, denom_nd: np.ndarray) -> dict:
    """(D): each detector universe's denom_nd (its pinned digest checked on the bytes read) against the npz's."""
    out = {}
    for b in DETECTOR_BANDS:
        for i in (0, 1):
            p = det_dir / f"{b}_{i}_denom_nd.npy"
            raw, sha = read_noatime(p)
            if sha != pins["files"][str(p)]["sha256"]:
                raise Refusal(f"{p}: the bytes read are not the pinned file")
            d = np.load(io.BytesIO(raw), allow_pickle=False).astype(np.float64)
            out[f"{b}_{i}"] = {"equal": bool(np.array_equal(d, denom_nd)),
                               "max_abs_difference": float(np.max(np.abs(d - denom_nd)))}
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    for k in ("root", "npz", "bank", "detector-dir", "pins", "out"):
        ap.add_argument(f"--{k}", type=Path, required=True)
    ap.add_argument("--expect-pins-sha256", required=True)
    ap.add_argument("--expect-npz-sha256", required=True)
    a = ap.parse_args(argv)
    import uproot

    t0 = time.time()
    raw, sha = read_noatime(a.pins)
    if sha != a.expect_pins_sha256:
        raise Refusal("pins file digest differs")
    pins = json.loads(raw.decode())
    h = hashlib.sha256()
    with open_noatime(a.npz) as fh:
        for block in iter(lambda: fh.read(1 << 24), b""):
            h.update(block)
    if h.hexdigest() != a.expect_npz_sha256:
        raise Refusal("input npz digest differs")
    with open_noatime(a.npz) as fh:
        z = np.load(fh, allow_pickle=False)
        denom_nd = np.asarray(z["denom_nd"], np.float64)
        edges = [np.asarray(z[f"edges_{k}"], float) for k in range(int(z["nedges"]))]   # s5c_unfold.load_inputs
    p = a.bank / "cv.npz"
    raw, sha = read_noatime(p)
    if sha != pins["files"][str(p)]["sha256"]:
        raise Refusal(f"{p}: the bytes read are not the pinned file")
    cv = {k: np.load(io.BytesIO(raw), allow_pickle=True)[k] for k in TD}
    del raw
    st = a.root.stat()
    with open_noatime(a.root) as fh:
        f = uproot.open(fh)
        pot_scale = float(f["dataPOTUsed"].member("fVal")) / float(f["mcPOTUsed"].member("fVal"))
        arr = f[TREE].arrays(list(KEYS), library="np")
    arr = {k: np.asarray(arr[k], np.float64) for k in KEYS}
    h = hashlib.sha256()
    for k in KEYS:
        h.update(arr[k].tobytes())
    rec, tdw_cv = checks(arr, pot_scale, cv, denom_nd, edges)
    rec["D_detector_denominators"] = detector_check(a.detector_dir, pins, denom_nd)
    rec["D_all_equal"] = all(v["equal"] for v in rec["D_detector_denominators"].values())
    usable = rec["A_coordinates_equal_row_by_row"] and rec["B_histogram_equals_denom_nd"] and rec["D_all_equal"]
    weights = a.out.with_suffix(".npy")
    if usable:
        np.save(weights, tdw_cv)
    atime = {q: os.stat(q).st_atime_ns != v for q, v in OPENED.items()}
    rec = {"schema": SCHEMA, "step": "cv-denominator", "verdict": "PASS" if usable else "TO_DIRECTOR",
           "pot_scale": pot_scale, "numpy": np.__version__, "uproot": uproot.__version__, "root": {"path": str(a.root), "size": st.st_size, "mtime_ns": st.st_mtime_ns,
                                            "tree": TREE, "branches": list(KEYS), "arrays_sha256": h.hexdigest()},
           "checks": rec, "tdw_cv_file": weights.name if usable else None,
           "tdw_cv_file_sha256": hashlib.sha256(weights.read_bytes()).hexdigest() if usable else None,
           "atime_moved": sorted(q for q, m in atime.items() if m), "seconds": round(time.time() - t0, 1),
           "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    a.out.write_text(json.dumps(rec, indent=1, sort_keys=True))
    print(f"FD-1B-CVDENOM verdict={rec['verdict']} " + json.dumps(
        {k: v for k, v in rec["checks"].items() if k != "D_detector_denominators"}, sort_keys=True))
    return 0 if usable else 3


if __name__ == "__main__":
    sys.exit(main())
