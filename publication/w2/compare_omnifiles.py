#!/usr/bin/env python3
"""W2a checks on event-loop omnifiles (publication packet W2).

``equal A B``: every tree in A has the same entries and every scalar branch is identical (NaN-aware,
exact) in B, and B has no extra tree or branch. Used for the no-op proof (base binary versus W2 binary
without the W2 environment) and for the identity-scale lateral path (delta = 0).

``shifted BASE SHIFT --scale s``: SHIFT is a RecoilResponse universe at reco-recoil scale s. Rows must align
one to one: same selection, truth, weights and event keys. Where a reco row passes selection:
  sim_eavail and sim_background_eavail are s times BASE (relative 1e-12);
  the reco energy transfer, recovered without the muon energy from q3^2 + W^2 = (q0 + M)^2, is s times
  BASE's (absolute 1e-9 GeV + relative 1e-9). The identity fails where the producer clipped W^2 < 0 to
  W = 0, so rows with W = 0 in either file are excluded from this check and counted;
  every other branch is identical.
The data tree must be identical, since the shift is applied to the simulation only.

Prints a JSON verdict. Exit 0 = PASS, 1 = FAIL, 2 = could not check.
"""
from __future__ import annotations

import argparse
import json
import sys

import numpy as np

M_NUCLEON_GEV = ((1.5 * 939.56536 + 938.272013) / 2.5) / 1000.0
SHIFTED = {
    "mc_signal_reco": ("sim_eavail", "sim_q3", "sim_W", "sim_pass"),
    "mc_background": ("sim_background_eavail", "sim_background_q3", "sim_background_W", "sim_background_pass"),
}


def read(path: str) -> dict:
    import ROOT
    f = ROOT.TFile.Open(path, "READ")
    if not f or f.IsZombie():
        raise RuntimeError(f"cannot open {path}")
    trees = {}
    for key in f.GetListOfKeys():
        obj = key.ReadObj()
        if not obj.InheritsFrom("TTree"):
            continue
        name = obj.GetName()
        scalars, skipped = [], []
        for br in obj.GetListOfBranches():
            leaves = br.GetListOfLeaves()
            if leaves.GetEntries() == 1 and leaves.At(0).GetLenStatic() == 1 and not leaves.At(0).GetLeafCount():
                scalars.append(br.GetName())
            else:
                skipped.append(br.GetName())
        cols = ROOT.RDataFrame(obj).AsNumpy(scalars) if scalars else {}
        trees[name] = {"n": int(obj.GetEntries()), "cols": {k: np.asarray(v) for k, v in cols.items()},
                       "skipped": skipped}
    f.Close()
    return trees


def same(a: np.ndarray, b: np.ndarray) -> bool:
    if a.shape != b.shape:
        return False
    if np.issubdtype(a.dtype, np.floating):
        return bool(np.array_equal(a, b, equal_nan=True))
    return bool(np.array_equal(a, b))


def cmd_equal(a_path: str, b_path: str) -> dict:
    A, B = read(a_path), read(b_path)
    bad = []
    if set(A) != set(B):
        bad.append(f"trees differ: {sorted(set(A) ^ set(B))}")
    for t in sorted(set(A) & set(B)):
        if A[t]["n"] != B[t]["n"]:
            bad.append(f"{t}: entries {A[t]['n']} != {B[t]['n']}")
            continue
        ca, cb = A[t]["cols"], B[t]["cols"]
        if set(ca) != set(cb):
            bad.append(f"{t}: branches differ {sorted(set(ca) ^ set(cb))}")
        for k in sorted(set(ca) & set(cb)):
            if not same(ca[k], cb[k]):
                bad.append(f"{t}.{k}: values differ")
    skipped = {t: A[t]["skipped"] for t in A if A[t]["skipped"]}
    return {"mode": "equal", "a": a_path, "b": b_path, "trees": {t: A[t]["n"] for t in A},
            "nonscalar_branches_not_compared": skipped, "failures": bad, "verdict": "PASS" if not bad else "FAIL"}


def recovered_q0(q3: np.ndarray, w: np.ndarray) -> np.ndarray:
    return np.sqrt(q3 * q3 + w * w) - M_NUCLEON_GEV


def cmd_shifted(base_path: str, shift_path: str, s: float) -> dict:
    A, B = read(base_path), read(shift_path)
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
            if not same(ca[k], cb[k]):
                bad.append(f"{t}.{k}: differs (must be unshifted)")
        if not special:
            continue
        ea, qa, wa, pa = (ca[x] for x in special)
        eb, qb, wb, pb = (cb[x] for x in special)
        if not same(pa, pb):
            bad.append(f"{t}: pass flags differ")
        sel = (pa.astype(bool)) & np.isfinite(ea) & (ea > -9000)
        r_e = np.abs(eb[sel] - s * ea[sel]) / np.maximum(np.abs(s * ea[sel]), 1e-300)
        ok_e = r_e <= 1e-12
        q0a, q0b = recovered_q0(qa[sel], wa[sel]), recovered_q0(qb[sel], wb[sel])
        # The identity holds only where the producer did not clip W^2 < 0 to W = 0; scaling q0 can move a
        # row across that clip, so a row clipped in EITHER file is excluded (and counted).
        valid = (q0a > 1e-6) & np.isfinite(q0a) & np.isfinite(q0b) & (wa[sel] > 0) & (wb[sel] > 0)
        dq = np.abs(q0b[valid] - s * q0a[valid])
        ok_q = dq <= 1e-9 + 1e-9 * np.abs(s * q0a[valid])
        stats[t] = {"passing_rows": int(sel.sum()), "eavail_max_rel_dev": float(r_e.max()) if r_e.size else None,
                    "eavail_rows_failing": int((~ok_e).sum()), "q0_rows_checked": int(valid.sum()),
                    "q0_rows_excluded_clipped_or_zero": int((~valid).sum()),
                    "q0_max_abs_dev_gev": float(dq.max()) if dq.size else None, "q0_rows_failing": int((~ok_q).sum())}
        if (~ok_e).any():
            bad.append(f"{t}: {int((~ok_e).sum())} rows with E_avail not scaled by {s}")
        if (~ok_q).any():
            bad.append(f"{t}: {int((~ok_q).sum())} rows with q0 not scaled by {s}")
        if sel.sum() == 0:
            bad.append(f"{t}: no passing rows to check")
    return {"mode": "shifted", "base": base_path, "shift": shift_path, "scale": s, "stats": stats,
            "failures": bad, "verdict": "PASS" if not bad else "FAIL"}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("equal"); e.add_argument("a"); e.add_argument("b")
    sh = sub.add_parser("shifted"); sh.add_argument("base"); sh.add_argument("shift")
    sh.add_argument("--scale", type=float, required=True)
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    try:
        res = cmd_equal(a.a, a.b) if a.cmd == "equal" else cmd_shifted(a.base, a.shift, a.scale)
    except Exception as exc:  # noqa: BLE001 - a check that could not run must not read as PASS
        print(json.dumps({"verdict": "COULD_NOT_CHECK", "error": repr(exc)}))
        return 2
    text = json.dumps(res, indent=1)
    print(text)
    if a.out:
        with open(a.out, "w") as fh:
            fh.write(text + "\n")
    return 0 if res["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
