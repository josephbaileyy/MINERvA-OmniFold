#!/usr/bin/env python3
"""MP1-A S0: sanity checks on a species-response event-loop pass against the k = 0 control.

G1 itself is ``publication/w2/compare_omnifiles.py equal <base_cv.root> <zero.root>`` (bit for bit). This
script checks a +-1 sigma pass SHIFT against the control BASE (``zero.root`` or ``base_cv.root``):
  - same trees, entries and branches; every branch other than reco E_avail, q3 and W identical, including the
    pass flags and the whole data tree (the data are never shifted);
  - on passing rows, the E_avail change has the sign of the shift and, under the pro-rata fuzz convention,
    |dE| <= delta_s * E (species s cannot carry more than the whole sum); for none/all it is reported;
  - the reco q0, recovered from q3^2 + W^2 = (q0 + M)^2 on rows with W > 0 in both files, moves with the sign of
    the shift; |dq0| <= delta_s * q0 is enforced for fractional and reported (as max |dq0|/(delta_s q0)) otherwise;
  - the fraction of passing rows that moved (it should be near the fraction of events carrying species s).
It reads each tree's LATEST cycle (omnifile_io.read_latest; the W2 reader keeps a stale autosave cycle) with uproot.
Prints a JSON verdict. Exit 0 = PASS, 1 = FAIL, 2 = could not check.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import omnifile_io  # noqa: E402  (read_latest(); it also puts publication/w2 on sys.path)
import compare_omnifiles as co  # noqa: E402  (the W2 comparer: same(), recovered_q0(), SHIFTED)

DELTA = {"proton": 0.035, "meson": 0.05, "em": 0.03, "other": 0.20, "xtalk": 0.20}
SHIFTED = co.SHIFTED


def as_flag(a: np.ndarray) -> np.ndarray:
    """Pass flags as integers; a UChar_t branch can arrive as an object array (W2 review F3)."""
    if a.dtype == object:
        return np.array([ord(v) if isinstance(v, (str, bytes)) else int(v) for v in a], dtype=int)
    return a.astype(int)


def check(base: str, shift: str, species: str, sign: int, q0conv: str, fuzzconv: str) -> dict:
    A, B = omnifile_io.read_latest(base), omnifile_io.read_latest(shift)
    d = DELTA[species]
    bad, stats = [], {}
    if set(A) != set(B):
        bad.append(f"trees differ: {sorted(set(A) ^ set(B))}")
    for t in sorted(set(A) & set(B)):
        if A[t]["n"] != B[t]["n"]:
            bad.append(f"{t}: entries {A[t]['n']} != {B[t]['n']}")
            continue
        ca, cb = A[t]["cols"], B[t]["cols"]
        if set(ca) != set(cb):
            bad.append(f"{t}: branches differ {sorted(set(ca) ^ set(cb))}")
        special = SHIFTED.get(t, ())
        for k in sorted((set(ca) & set(cb)) - set(special[:3])):
            if not co.same(ca[k], cb[k]):
                bad.append(f"{t}.{k}: differs (must be unshifted)")
        if not special:
            continue
        ea, qa, wa, pa = (ca[x] for x in special)
        eb, qb, wb, _ = (cb[x] for x in special)
        sel = (as_flag(pa) == 1) & np.isfinite(ea) & (ea > -9000) & np.isfinite(eb)
        de = sign * (eb[sel] - ea[sel])
        tol_e = 1e-12 * np.maximum(np.abs(ea[sel]), 1e-300)
        wrong_sign_e = int(np.sum(de < -tol_e))
        rel_e = np.abs(eb[sel] - ea[sel]) / np.maximum(d * np.abs(ea[sel]), 1e-300)
        over_e = int(np.sum(rel_e > 1 + 1e-12))
        q0a, q0b = co.recovered_q0(qa[sel], wa[sel]), co.recovered_q0(qb[sel], wb[sel])
        valid = (q0a > 1e-6) & np.isfinite(q0a) & np.isfinite(q0b) & (wa[sel] > 0) & (wb[sel] > 0)
        dq = sign * (q0b[valid] - q0a[valid])
        wrong_sign_q = int(np.sum(dq < -1e-9))
        bound = d * q0a[valid]
        over_q = int(np.sum(np.abs(dq) > bound * (1 + 1e-9) + 1e-9))
        rel_q = np.abs(dq) / np.maximum(bound, 1e-300)
        moved = float(np.mean(eb[sel] != ea[sel])) if sel.any() else 0.0
        stats[t] = {"passing_rows": int(sel.sum()), "frac_rows_eavail_moved": moved,
                    "eavail_wrong_sign": wrong_sign_e, "eavail_rows_over_delta_E": over_e,
                    "eavail_max_dE_over_deltaE": float(rel_e.max()) if rel_e.size else None,
                    "q0_rows_checked": int(valid.sum()), "q0_wrong_sign": wrong_sign_q,
                    "q0_rows_over_delta_q0": over_q, "q0_max_dq0_over_deltaq0": float(rel_q.max()) if rel_q.size else None}
        if sel.sum() == 0 or valid.sum() == 0:
            bad.append(f"{t}: no passing rows to check")
        if wrong_sign_e:
            bad.append(f"{t}: {wrong_sign_e} rows with E_avail moved against the shift")
        if wrong_sign_q:
            bad.append(f"{t}: {wrong_sign_q} rows with q0 moved against the shift")
        if fuzzconv == "prorata" and over_e:
            bad.append(f"{t}: {over_e} rows with |dE| > delta_s * E under the pro-rata fuzz convention")
        if q0conv == "fractional" and over_q:
            bad.append(f"{t}: {over_q} rows with |dq0| > delta_s * q0 under the fractional q0 convention")
    return {"mode": "species", "base": base, "shift": shift, "species": species, "sign": sign, "delta": d,
            "q0_convention": q0conv, "fuzz_convention": fuzzconv, "stats": stats, "failures": bad,
            "verdict": "PASS" if not bad else "FAIL"}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("base")
    ap.add_argument("shift")
    ap.add_argument("--species", required=True, choices=sorted(DELTA))
    ap.add_argument("--sign", required=True, type=int, choices=(-1, 1))
    ap.add_argument("--q0", required=True, choices=("fprop", "fractional", "legacy"))
    ap.add_argument("--fuzz", required=True, choices=("prorata", "none", "all"))
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    try:
        res = check(a.base, a.shift, a.species, a.sign, a.q0, a.fuzz)
    except Exception as exc:  # noqa: BLE001 - a check that could not run must not read as PASS
        print(json.dumps({"verdict": "COULD_NOT_CHECK", "error": repr(exc)}))
        return 2
    text = json.dumps(res, indent=1)
    print(text)
    if a.out:
        Path(a.out).write_text(text + "\n")
    return 0 if res["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
