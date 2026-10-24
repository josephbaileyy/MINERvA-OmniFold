#!/usr/bin/env python3
"""PV ladder, POST HOC and descriptive (the director's request of 2026-10-24, after the outputs): how strong a
prior departure each rung's reweight is on the 39 RD3 cells, and how much of it reaches the result.

L-EW applies each generator's (E_avail, W) shape; L-5D-PV applies the gated 5D shape. So the two differ in the
reweight's strength as well as in the classifier's features. For vertex k, rung X and EW cell c:
  d_Xkc = sum(w_truth r_Xk) / sum(w_truth) - 1 over truth-passing rows of the 5D npz whose truth lies in c (and inside
          the full 5D grid, as pvl_lib.row_weight): the truth-level EW-marginal departure the reweight induces;
  R_Xkc = |s_Xkc| / |d_Xkc|, with s the readout's shift: the response, on cells with |d_Xkc| > MIN_DEP.
Also h_X / D_X per cell, with D_X = max_k |d_Xkc|, and the per-cell ratio of that between the rungs beside the raw
ratio h_EW / h_5D.

MEASURES: arithmetic on the npz, the frozen reweights and the committed readouts. No unfold is rerun. CANNOT
AUTHORIZE: any claim.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
import pvl_lib as L  # noqa: E402

VERTICES = ("genie_mec", "nuwro", "gibuu")
MIN_DEP = 0.01


def departures(z, names, ratios_dir, rung):
    gen = np.asarray(z["MCgen"], float)
    pt = np.asarray(z["pass_truth"], bool)
    w = np.asarray(z["w_truth"], float)
    ew = L.flat_index(gen[:, [names.index("eavail"), names.index("W")]], ("eavail", "W"))
    ok = pt & (ew >= 0) & (L.flat_index(gen, names) >= 0)
    w0 = np.bincount(ew[ok], weights=w[ok], minlength=42)
    out = {}
    for v in VERTICES:
        R = L.load_json(ratios_dir / rung / f"{v}.json")
        r = L.row_weight(gen, names, R, pt)
        w1 = np.bincount(ew[ok], weights=(w * r)[ok], minlength=42)
        out[v] = w1 / w0 - 1.0
    return out


def q(a):
    a = np.asarray(a, float)
    return {"median": float(np.median(a)), "p90": float(np.percentile(a, 90)), "max": float(np.max(a))}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--npz", type=Path, required=True)
    ap.add_argument("--expect-npz-sha256", required=True)
    ap.add_argument("--ratios", type=Path, required=True, help="the frozen prep/ratios directory")
    ap.add_argument("--prep-sums", type=Path, default=_HERE / "prep-SHA256SUMS")
    ap.add_argument("--readouts", type=Path, default=_HERE / "readouts")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        raise SystemExit(f"[FAIL] refusing to overwrite {a.out}")
    if L.sha256_path(a.npz) != a.expect_npz_sha256:
        raise SystemExit("[FAIL] npz sha256 differs")
    sums = dict(ln.split()[::-1] for ln in a.prep_sums.read_text().splitlines() if ln.strip())
    for rung in ("L-EW", "L-5D-PV"):
        for v in VERTICES:
            if sums.get(f"./ratios/{rung}/{v}.json") != L.sha256_path(a.ratios / rung / f"{v}.json"):
                raise SystemExit(f"[FAIL] {rung}/{v}.json differs from prep-SHA256SUMS")
    z = np.load(a.npz, allow_pickle=True)
    names = L.npz_axes(z)
    if names != L.AXES5:
        raise SystemExit("[FAIL] not the 5D npz")
    out = {"schema": "pvl-departure/1", "post_hoc": True, "min_departure": MIN_DEP,
           "inputs": {"npz_sha256": a.expect_npz_sha256, "prep_sums_sha256": L.sha256_path(a.prep_sums)},
           "code": {"pvl_departure.py": L.sha256_path(__file__), "pvl_lib.py": L.sha256_path(L.__file__)},
           "rungs": {}}
    hd = {}
    for rung in ("L-EW", "L-5D-PV"):
        X = L.load_json(a.readouts / f"{rung}_e.json")
        cells = np.asarray(X["cells"]["EW"])
        sp = X["spaces"]["EW"]
        d = {v: dv[cells] for v, dv in departures(z, names, a.ratios, rung).items()}
        rec = {"cells": cells.tolist(), "vertices": {}}
        for v in VERTICES:
            s = np.abs(np.asarray(sp["vertices"][v]["shift"]))
            m = np.abs(d[v]) > MIN_DEP
            rec["vertices"][v] = {"departure": d[v].tolist(), "abs_departure": q(np.abs(d[v])),
                                  "n_cells_above_min": int(m.sum()),
                                  "response": q(s[m] / np.abs(d[v][m])) if m.any() else None}
        D = np.max(np.abs(np.vstack([d[v] for v in VERTICES])), axis=0)
        h = np.asarray(sp["envelope"]["h"])
        rec["D"] = q(D)
        keep = D > MIN_DEP
        rec["n_cells_D_above_min"] = int(keep.sum())
        rec["h_over_D"] = q(h[keep] / D[keep])
        hd[rung] = (h, D)
        out["rungs"][rung] = rec
    (h1, D1), (h5, D5) = hd["L-EW"], hd["L-5D-PV"]
    raw = h1 / h5
    both = (D1 > MIN_DEP) & (D5 > MIN_DEP)
    norm = (h1[both] / D1[both]) / (h5[both] / D5[both])
    out["comparison"] = {"raw_h_ratio": q(raw), "normalized_h_over_D_ratio": q(norm), "n_cells_normalized": int(both.sum()),
                         "cells_L_EW_lower_raw": int((raw < 1).sum()), "cells_L_EW_lower_normalized": int((norm < 1).sum()),
                         "D_ratio": q(D1[both] / D5[both])}
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    pc = lambda x: f"{100 * x:.2f} %"  # noqa: E731
    for rung, rec in out["rungs"].items():
        print(f"[pvl] {rung}: D = max_k |departure| median {pc(rec['D']['median'])}, p90 {pc(rec['D']['p90'])}, "
              f"max {pc(rec['D']['max'])}; h/D median {rec['h_over_D']['median']:.3f}")
        for v in VERTICES:
            vr = rec["vertices"][v]
            resp = vr["response"]
            print(f"[pvl]   {v}: |departure| median {pc(vr['abs_departure']['median'])}, max {pc(vr['abs_departure']['max'])}; "
                  f"response median {resp['median']:.3f} on {vr['n_cells_above_min']} cells" if resp else
                  f"[pvl]   {v}: no cell with |departure| > {MIN_DEP}")
    c = out["comparison"]
    print(f"[pvl] h(L-EW)/h(L-5D-PV) median {c['raw_h_ratio']['median']:.3f} (L-EW lower in {c['cells_L_EW_lower_raw']}); "
          f"normalized (h/D) median {c['normalized_h_over_D_ratio']['median']:.3f} on {c['n_cells_normalized']} cells "
          f"(L-EW lower in {c['cells_L_EW_lower_normalized']}); D(L-EW)/D(L-5D-PV) median {c['D_ratio']['median']:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
