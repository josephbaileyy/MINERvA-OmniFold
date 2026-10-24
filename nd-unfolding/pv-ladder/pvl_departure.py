#!/usr/bin/env python3
"""PV ladder, POST HOC and descriptive (the director's request of 2026-10-24, after the outputs): how strong a
prior departure each rung's reweight is on a readout space, and how much of it reaches the result.

L-EW applies each generator's (E_avail, W) shape; L-5D-PV applies the gated 5D shape. So the two differ in the
reweight's strength as well as in the classifier's features. For vertex k, rung X and readout cell c:
  d_Xkc = sum(w_truth r_Xk) / sum(w_truth) - 1 over the truth-passing rows whose truth lies in c: the truth-level
          marginal departure the reweight induces on c;
  on cells with |d| > MIN_DEP: the response |s| / |d| and the signed response s / d (s the readout's shift), and
          whether s and d have the same sign;
  the same-vertex response s_k* / d_k* with k* = argmax_k |d_kc| (h and D below may come from different vertices);
  h / D with D = max_k |d_kc|, at several departure thresholds, and the per-cell ratio of h/D between two rungs.

Spaces:
  EW    on the 39 RD3 cells, from the 5D npz's rows (L-EW's GiBUU truth cut needs the rows), for L-EW and L-5D-PV;
  PTPZ  on L-2D's 205 (p_T, p_parallel) cells, from each rung's ratios.json prior truth weight per reweight cell
        (exact because r is constant on each reweight cell), for L-3D, L-4D and L-5D-PV.

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
THRESHOLDS = (0.01, 0.03, 0.05, 0.10)


def departures(z, names, ratios_dir, rung):
    """Per vertex, the EW-marginal departure on the 42 EW cells, from the npz's rows."""
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
        with np.errstate(invalid="ignore", divide="ignore"):  # an empty cell is NaN, not 0
            out[v] = w1 / w0 - 1.0
    return out


def departures_from_weights(ratios_dir, rung, space):
    """Per vertex, the marginal departure on a readout space from the reweight cells' prior truth weight."""
    R = L.load_json(ratios_dir / rung / "ratios.json")
    axes = tuple(R["axes"])
    p = np.asarray(R["prior_truth_weight"], float)
    p0 = L.readout_space(p, axes, space)
    out = {}
    for v in VERTICES:
        r = np.asarray(L.load_json(ratios_dir / rung / f"{v}.json")["r"], float)
        out[v] = L.readout_space(p * r, axes, space) / np.where(p0 > 0, p0, np.nan) - 1.0
    return out


def q(a):
    a = np.asarray(a, float)
    if a.size == 0:
        return None
    return {"median": float(np.median(a)), "p25": float(np.percentile(a, 25)), "p75": float(np.percentile(a, 75)),
            "p90": float(np.percentile(a, 90)), "max": float(np.max(a)), "n": int(a.size)}


def measures(shifts, h, d):
    """Per vertex and same-vertex responses, sign agreement, vertex matching and h/D at each threshold."""
    S = np.vstack([np.asarray(shifts[v], float) for v in VERTICES])
    Dv = np.vstack([np.asarray(d[v], float) for v in VERTICES])
    rec = {"vertices": {}}
    for i, v in enumerate(VERTICES):
        s, dv = S[i], Dv[i]
        m = np.abs(dv) > MIN_DEP
        rec["vertices"][v] = {"departure": dv.tolist(), "abs_departure": q(np.abs(dv)), "n_cells_above_min": int(m.sum()),
                              "response": q(np.abs(s[m]) / np.abs(dv[m])), "signed_response": q(s[m] / dv[m]),
                              "same_sign": int((np.sign(s[m]) == np.sign(dv[m])).sum())}
    D = np.max(np.abs(Dv), axis=0)
    ks = np.argmax(np.abs(Dv), axis=0)
    kh = np.argmax(np.abs(S), axis=0)
    cols = np.arange(S.shape[1])
    keep = D > MIN_DEP
    rec["D"] = q(D)
    rec["h_vertex_is_D_vertex"] = int((ks == kh).sum())
    rec["same_vertex_signed_response"] = q(S[ks, cols][keep] / Dv[ks, cols][keep])
    rec["h_over_D"] = {f"D>{t:g}": q(h[D > t] / D[D > t]) for t in THRESHOLDS}
    return rec, D


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--npz", type=Path, required=True, help="the 5D npz")
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
    for rung in ("L-EW", "L-3D", "L-4D", "L-5D-PV"):
        for f in [f"{v}.json" for v in VERTICES] + ["ratios.json"]:
            if sums.get(f"./ratios/{rung}/{f}") != L.sha256_path(a.ratios / rung / f):
                raise SystemExit(f"[FAIL] {rung}/{f} differs from prep-SHA256SUMS")
    readouts = {r: a.readouts / f"{r}_e.json" for r in ("L-EW", "L-3D", "L-4D", "L-5D-PV")}
    z = np.load(a.npz, allow_pickle=True)
    names = L.npz_axes(z)
    if names != L.AXES5:
        raise SystemExit("[FAIL] not the 5D npz")
    out = {"schema": "pvl-departure/2", "post_hoc": True, "min_departure": MIN_DEP,
           "inputs": {"npz_sha256": a.expect_npz_sha256, "prep_sums_sha256": L.sha256_path(a.prep_sums),
                      "readouts_sha256": {r: L.sha256_path(p) for r, p in readouts.items()}},
           "code": {"pvl_departure.py": L.sha256_path(__file__), "pvl_lib.py": L.sha256_path(L.__file__)},
           "spaces": {"EW": {}, "PTPZ": {}}}
    keep = {}
    for space, rungs in (("EW", ("L-EW", "L-5D-PV")), ("PTPZ", ("L-3D", "L-4D", "L-5D-PV"))):
        for rung in rungs:
            X = L.load_json(readouts[rung])
            cells = np.asarray(X["cells"][space])
            sp = X["spaces"][space]
            dd = departures(z, names, a.ratios, rung) if space == "EW" else departures_from_weights(a.ratios, rung, space)
            d = {v: dv[cells] for v, dv in dd.items()}
            h = np.asarray(sp["envelope"]["h"])
            rec, D = measures({v: sp["vertices"][v]["shift"] for v in VERTICES}, h, d)
            rec["cells"] = cells.tolist()
            out["spaces"][space][rung] = rec
            keep[(space, rung)] = (h, D, {v: np.asarray(sp["vertices"][v]["shift"]) for v in VERTICES}, d)
    (h1, D1, s1, d1), (h5, D5, s5, d5) = keep[("EW", "L-EW")], keep[("EW", "L-5D-PV")]
    raw = h1 / h5
    comp = {"raw_h_ratio": q(raw), "cells_L_EW_lower_raw": int((raw < 1).sum()), "ratio_of_median_h": float(np.median(h1) / np.median(h5)),
            "normalized": {}}
    for t in THRESHOLDS:
        both = (D1 > t) & (D5 > t)
        norm = (h1[both] / D1[both]) / (h5[both] / D5[both])
        comp["normalized"][f"D>{t:g}"] = {"ratio": q(norm), "cells_L_EW_lower": int((norm < 1).sum()),
                                          "within_0.8_1.25": int(((norm >= 0.8) & (norm <= 1.25)).sum()),
                                          "D_ratio": q(D1[both] / D5[both]),
                                          "log_corr_h_ratio_D_ratio": float(np.corrcoef(np.log(h1[both] / h5[both]),
                                                                                        np.log(D1[both] / D5[both]))[0, 1])}
    comp["per_vertex_response_ratio"] = {}
    for v in VERTICES:
        r1, r5 = (out["spaces"]["EW"][r]["vertices"][v]["response"] for r in ("L-EW", "L-5D-PV"))
        comp["per_vertex_response_ratio"][v] = r1["median"] / r5["median"] if r1 and r5 else None
    out["comparison_EW"] = comp
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    for space, rr in out["spaces"].items():
        for rung, rec in rr.items():
            hd = rec["h_over_D"]
            print(f"[pvl] {space} {rung}: D median {100 * rec['D']['median']:.2f} %; h/D median " +
                  ", ".join(f"{k} {v['median']:.3f} ({v['n']})" for k, v in hd.items() if v) +
                  f"; same-vertex signed response median {rec['same_vertex_signed_response']['median']:.3f} "
                  f"(IQR {rec['same_vertex_signed_response']['p25']:.2f}-{rec['same_vertex_signed_response']['p75']:.2f}); "
                  f"h vertex = D vertex in {rec['h_vertex_is_D_vertex']} of {len(rec['cells'])}")
            for v in VERTICES:
                x = rec["vertices"][v]
                if x["response"]:
                    print(f"[pvl]   {v}: |d| median {100 * x['abs_departure']['median']:.2f} %; response {x['response']['median']:.3f}, "
                          f"signed {x['signed_response']['median']:.3f}, same sign {x['same_sign']} of {x['n_cells_above_min']}")
    c = out["comparison_EW"]
    print(f"[pvl] EW raw h ratio median {c['raw_h_ratio']['median']:.3f} (L-EW lower in {c['cells_L_EW_lower_raw']}); "
          f"ratio of medians {c['ratio_of_median_h']:.3f}")
    for k, v in c["normalized"].items():
        print(f"[pvl]   normalized {k}: median {v['ratio']['median']:.3f} (IQR {v['ratio']['p25']:.2f}-{v['ratio']['p75']:.2f}) "
              f"on {v['ratio']['n']}; within [0.8,1.25] {v['within_0.8_1.25']}; D ratio {v['D_ratio']['median']:.3f}; "
              f"log-corr {v['log_corr_h_ratio_D_ratio']:.2f}")
    print("[pvl]   per-vertex response ratio L-EW/L-5D-PV: " +
          ", ".join(f"{v} {x:.2f}" for v, x in c["per_vertex_response_ratio"].items() if x is not None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
