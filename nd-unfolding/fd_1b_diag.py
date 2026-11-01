#!/usr/bin/env python3
"""1B's gate-D diagnosis (state/measurement-paper/5d-community-20261024/FD-1B-DIAG-DECLARATION.md, under
DECISION-20261031-joseph-three-covariance-files-and-1b-diagnosis.md item 2): from the 176 noise-free derivation
unfolds and S1's assembly, the readouts the declaration fixes and its two localization rules, at 0 node-h.

Readouts, all DERIVATION:
* per band b (all 38: Flux, the 33 interaction bands, the 4 detector bands) and cell c: the carried sigma ratio
  sqrt(E_b,cc / M_b,cc); the raw ratio, the same without the diag(f / x_T) carry; and the band's share of the
  diagonal, S1's M_b,cc / M_d,cc and the toys' E_b,cc / E_d,cc;
* per cell: g_c = f_c / x_T,c, rho_c (gate D's, recomputed and held to the committed readout bit for bit) and
  rho_raw,c, rho with every band's block uncarried.

Rules (the declaration's section 2), each PASS or FAIL:
* L1, named bands: the minimal sets B (|B| <= K_MAX, searched by size) for which rho with S1's diagonal in place of
  the toys' for the bands in B lies in GATE_D_WINDOW (inclusive) in every cell. L1 PASS iff such sets exist and the
  union of ALL of them names at most K_MAX bands; those are the named bands. Their intersection is reported too.
* L2, the carry: rho_raw lies in GATE_D_WINDOW in every cell. A PASS means removing the carry closes the gap, not
  that the carry is wrong.
LOCALIZED iff L1 or L2 passes; otherwise NOT LOCALIZED. The window is gate D's, unrelaxed.

    fd_1b_diag.py --derivation D --tag fd1b_derivation --s1-npz S --flux-constraint C --gate-d G --out O

MEASURES: the readouts above. CANNOT AUTHORIZE: an amendment, a toy redesign, a rerun, or any claim.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
import fd_1b_score as fs  # noqa: E402
import s1_assemble as sa  # noqa: E402

K_MAX = 3           # the most bands a localized cause may name (declaration section 2)
WINDOW = fs.GATE_D_WINDOW
LISTED_MAX = 200    # minimal sets listed up to this many; the count, union and intersection always cover all of them
GATE_D_SHA256 = "e1838c0ae2e66c1a0dffd505c41da44381a2d2b798cfc17d353e2d1260542c63"  # receipts-1b/stage2/run/score


def ratio(num: np.ndarray, den: np.ndarray) -> list:
    """sqrt(num / den) per cell; where S1's diagonal is zero, "inf" if the toys' is not and None if both are."""
    return [float(np.sqrt(n / d)) if d > 0 else ("inf" if n > 0 else None) for n, d in zip(num, den)]


def in_window(rho: np.ndarray) -> bool:
    return bool(np.all((rho >= WINDOW[0]) & (rho <= WINDOW[1])))


def localized_bands(e: dict, m: dict, Ed: np.ndarray, Md: np.ndarray, k_max: int = K_MAX) -> dict:
    """L1: the smallest sets B (|B| <= k_max) for which rho with S1's diagonal in place of the toys' for B is in the
    window in every cell; e and m map each band to its diagonal (toys', carried; S1's). The numerator is a sum of
    covariance diagonals (fixed, toys' outside B, S1's inside), so it is never negative. PASS iff such sets exist and
    their union, over all of them, has at most k_max bands."""
    bands = sorted(e)
    for k in range(1, k_max + 1):
        hits = [[x.removeprefix("band:") for x in B] for B in itertools.combinations(bands, k)
                if in_window(np.sqrt((Ed - sum(e[b] - m[b] for b in B)) / Md))]
        if hits:
            union = sorted(set().union(*hits))
            inter = sorted(set(hits[0]).intersection(*hits))
            return {"verdict": "PASS" if len(union) <= k_max else "FAIL", "size": k, "n_sets": len(hits),
                    "named": union if len(union) <= k_max else [], "union": union, "intersection": inter,
                    "sets": hits[:LISTED_MAX]}
    return {"verdict": "FAIL", "size": None, "n_sets": 0, "named": [], "union": [], "intersection": [], "sets": []}


def diagnose(d: dict, s1: dict) -> dict:
    blocks = s1["blocks"]
    M_d = fs.drawn_matrix(s1)
    Md = np.diag(M_d)
    e = {b: np.diag(v) for b, v in d["carried"].items()}
    r = {b: np.diag(v) for b, v in d["raw"].items()}
    m = {b: np.diag(blocks[b]) for b in d["carried"]}
    # summed in gate D's order (fixed blocks, then bands), so rho reproduces its readout bit for bit
    Ed = sum([np.diag(v) for v in d["fixed"].values()] + list(e.values()))
    Ed_raw = sum([np.diag(v) for v in d["fixed"].values()] + list(r.values()))
    rho, rho_raw = np.sqrt(Ed / Md), np.sqrt(Ed_raw / Md)
    per_band = {b[5:]: {"group": sa.group_of(b), "sigma_ratio": ratio(e[b], m[b]), "sigma_ratio_raw": ratio(r[b], m[b]),
                        "share_s1": (m[b] / Md).tolist(), "share_toys": (e[b] / Ed).tolist()} for b in sorted(e)}
    L1 = localized_bands(e, m, Ed, Md)
    L2 = {"verdict": "PASS" if in_window(rho_raw) else "FAIL", "rho_raw": rho_raw.tolist()}
    return {"label": "DERIVATION", "cells": [f"R{c:02d}" for c in range(sa.N_CELLS)], "window": list(WINDOW),
            "k_max": K_MAX, "g": d["g"].tolist(), "rho": rho.tolist(), "rho_raw": rho_raw.tolist(),
            "per_band": per_band, "L1_named_bands": L1, "L2_carry": L2,
            "verdict": "LOCALIZED" if "PASS" in (L1["verdict"], L2["verdict"]) else "NOT LOCALIZED"}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--derivation", type=Path, required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--s1-npz", type=Path, required=True)
    ap.add_argument("--flux-constraint", type=Path, required=True)
    ap.add_argument("--gate-d", type=Path, required=True, help="gate D's committed readout, the consistency control")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        print(f"[fd-1b-diag] refusing to overwrite {a.out}", file=sys.stderr)
        return 4
    try:
        if sa.sha256(a.gate_d) != GATE_D_SHA256:
            raise fs.Invalid(f"{a.gate_d} is not gate D's committed readout ({GATE_D_SHA256[:16]}...)")
        s1 = fs.load_s1(a.s1_npz)
        d = fs.derivation_blocks(a.derivation, a.tag, s1, a.flux_constraint)
        out = {**fs.header(s1, "DERIVATION"), **diagnose(d, s1)}
        out["code_sha256"]["fd_1b_diag.py"] = hashlib.sha256(Path(__file__).resolve().read_bytes()).hexdigest()
        gd = json.loads(a.gate_d.read_text())
        if gd.get("rho") != out["rho"]:
            raise fs.Invalid("rho does not reproduce gate D's committed readout bit for bit")
    except (SystemExit, OSError, ValueError) as e:
        if isinstance(e, SystemExit) and not isinstance(e.code, str):
            raise
        print(f"[fd-1b-diag] refusing: {type(e).__name__}: {e}", file=sys.stderr)
        return 4
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({"out": str(a.out), "verdict": out["verdict"], "L1": out["L1_named_bands"]["verdict"],
                      "L2": out["L2_carry"]["verdict"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
