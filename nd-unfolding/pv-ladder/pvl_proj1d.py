#!/usr/bin/env python3
"""PV ladder, POST HOC and descriptive (Ben's question of 2026-10-26, after the ladder's declared readouts): on each
1D projection of the 5D grid, how much of a generator's truth-level difference reaches the unfolded result?

For rung X in (L-EW, L-5D-PV), vertex k and a bin b of a readout (a 1D axis, the other four summed; or an EW cell):
  d_kb = sum(w_truth r_Xk) / sum(w_truth) - 1 over the truth-passing in-grid rows: pvl_departure.py's departure;
  s_kb = x_k / x_0 - 1 from the cell-integrated data unfolds, prior k against the Tune v1 prior;
  leak = sum_b(s d) / sum_b(d^2): the least-squares slope of s on d. 0 = the data set the result, 1 = it follows the
         prior. rms = rms(s) / rms(d) also counts shifts unrelated to d.
NuWro closure (pseudo-data = the MC reweighted to NuWro, unfolded with the nominal prior):
  b = x / x_true - 1; dc = x_true(nuwro) / x_true(tune_v1) - 1; closure leak = -sum(b dc) / sum(dc^2).
Within-W cancellation, on the supported EW cells: sum_E |x_k - x_0| / |sum_E (x_k - x_0)| per W bin.

Checks, all required before anything is written (each a maximum absolute deviation against its bound):
  dc agrees with d_nuwro to TRUTH_TOL. The two are built on different truth bases (the closure's x_true goes
  through the nominal completeness and the binned denominator; d sums the npz's truth rows), so this is agreement,
  not an identity by construction;
  the tune_v1 closure's |b| stays within the closure floor <rung>_e.json records (controls.PC.closure_floor.max):
  the LightGBM path does not close to 0;
  s and d on the 39 EW cells reproduce <rung>_e.json's shifts and departure.json's departures to TOL.

MEASURES: arithmetic on the pinned products, the frozen reweights and the 5D npz. No unfold is rerun. CANNOT
AUTHORIZE: any claim, gate or reporting definition.
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
RUNGS = ("L-EW", "L-5D-PV")
TASKS = ("tune_v1",) + VERTICES + ("closure_nuwro", "closure_tune_v1")
RECEIPTS = _HERE.parents[1] / "docs" / "orchestration" / "state" / "measurement-scoping" / "pv-ladder" / "receipts" / "SHA256SUMS"
TOL = 1e-12
TRUTH_TOL = 1e-6


def read_sums(path):
    return dict(ln.split()[::-1] for ln in Path(path).read_text().splitlines() if ln.strip())


def verify_inputs(products, ratios, npz, expect_npz, receipts=RECEIPTS, prep_sums=_HERE / "prep-SHA256SUMS",
                  readouts=_HERE / "readouts", config=_HERE / "config.json"):
    """Refuse unless every input is the pinned one."""
    want_lib = L.load_json(readouts / "departure.json")["code"]["pvl_lib.py"]
    if L.sha256_path(L.__file__) != want_lib:
        raise SystemExit("[FAIL] pvl_lib.py is not the digest pvl_departure.py recorded")
    cfg = L.load_json(config)["rungs"]
    if any(cfg[r]["npz"]["sha256"] != expect_npz for r in RUNGS):
        raise SystemExit("[FAIL] --expect-npz-sha256 is not config.json's npz")
    rec = read_sums(receipts)
    for rung in RUNGS:
        for t in TASKS:
            if rec.get(f"products/{rung}_e_{t}.npz") != L.sha256_path(products / f"{rung}_e_{t}.npz"):
                raise SystemExit(f"[FAIL] {rung}_e_{t}.npz differs from receipts/SHA256SUMS")
    sums = read_sums(prep_sums)
    for rung in RUNGS:
        for v in VERTICES:
            if sums.get(f"./ratios/{rung}/{v}.json") != L.sha256_path(ratios / rung / f"{v}.json"):
                raise SystemExit(f"[FAIL] {rung}/{v}.json differs from prep-SHA256SUMS")
    if npz is not None and L.sha256_path(npz) != expect_npz:
        raise SystemExit("[FAIL] npz sha256 differs")


def truth_weights(z, ratios, rung):
    """The prior's truth weight and each vertex's reweighted truth weight on the fine grid."""
    names = L.npz_axes(z)
    if names != L.AXES5:
        raise SystemExit("[FAIL] not the 5D npz")
    gen = np.asarray(z["MCgen"], float)
    pt = np.asarray(z["pass_truth"], bool)
    w = np.asarray(z["w_truth"], float)
    f = L.flat_index(gen, names)
    ok = pt & (f >= 0)
    n = int(np.prod([len(L.FINE[a]) - 1 for a in names]))
    w0 = np.bincount(f[ok], weights=w[ok], minlength=n)
    w1 = {}
    for v in VERTICES:
        r = L.row_weight(gen, names, L.load_json(ratios / rung / f"{v}.json"), pt)
        w1[v] = np.bincount(f[ok], weights=(w * r)[ok], minlength=n)
    return w0, w1


def products(path, rung):
    """Cell-integrated data and closure results, and the closures' truth, on the fine grid."""
    out = {}
    for t in TASKS:
        z = np.load(path / f"{rung}_e_{t}.npz", allow_pickle=True)
        out[t] = L.integrated(z["xsec_flat"], L.AXES5)
        if t.startswith("closure_"):
            out[f"{t}_true"] = L.integrated(z["xtrue_flat"], L.AXES5)
    return out


def project(x, axis):
    """Sum the fine grid over every axis but ``axis`` ("EW" keeps the 42 (E_avail, W) cells)."""
    if axis == "EW":
        return L.readout_space(x, L.AXES5, "EW")
    shape = tuple(len(L.FINE[a]) - 1 for a in L.AXES5)
    return np.asarray(x, float).reshape(shape).sum(axis=tuple(i for i, a in enumerate(L.AXES5) if a != axis))


def readout(w0, w1, P, cells=None):
    """d, s and the NuWro closure on every 1D axis and on the EW cells (restricted to ``cells``)."""
    rec = {}
    for axis in L.AXES5 + ("EW",):
        sel = np.asarray(cells) if axis == "EW" else slice(None)
        P0, X0 = project(w0, axis)[sel], project(P["tune_v1"], axis)[sel]
        TN, TT = project(P["closure_nuwro_true"], axis)[sel], project(P["closure_tune_v1_true"], axis)[sel]
        with np.errstate(invalid="ignore", divide="ignore"):
            ax = {"prior_truth_weight": P0.tolist(), "x_nominal": X0.tolist(), "vertices": {},
                  "closure_nuwro": {"dc": (TN / TT - 1.0).tolist(),
                                    "b": (project(P["closure_nuwro"], axis)[sel] / TN - 1.0).tolist(),
                                    "control_b_tune_v1": (project(P["closure_tune_v1"], axis)[sel] / TT - 1.0).tolist()}}
            for v in VERTICES:
                ax["vertices"][v] = {"d": (project(w1[v], axis)[sel] / P0 - 1.0).tolist(),
                                     "s": (project(P[v], axis)[sel] / X0 - 1.0).tolist()}
        if axis == "EW":
            ax["cells"] = list(map(int, cells))
        rec[axis] = ax
    return rec


def leak(s, d):
    s, d = np.asarray(s, float), np.asarray(d, float)
    return float(np.dot(s, d) / np.dot(d, d))


def summary(rec):
    """The leak and rms ratio per axis and vertex, and the closure's, on the 1D axes and the EW cells."""
    out = {}
    for axis, ax in rec.items():
        row = {}
        for v in VERTICES:
            s, d = (np.asarray(ax["vertices"][v][k], float) for k in "sd")
            row[v] = {"rms_d": float(np.sqrt(np.mean(d ** 2))), "leak": leak(s, d),
                      "rms_ratio": float(np.sqrt(np.mean(s ** 2) / np.mean(d ** 2)))}
        c = ax["closure_nuwro"]
        b, dc = np.asarray(c["b"], float), np.asarray(c["dc"], float)
        row["closure_nuwro"] = {"rms_d": float(np.sqrt(np.mean(dc ** 2))), "leak": -leak(b, dc),
                                "rms_ratio": float(np.sqrt(np.mean(b ** 2) / np.mean(dc ** 2)))}
        out[axis] = row
    return out


def cancellation(P, cells):
    """Per vertex and W bin, sum_E |x_k - x_0| / |sum_E (x_k - x_0)| over the supported EW cells."""
    nE, nW = len(L.FINE["eavail"]) - 1, len(L.FINE["W"]) - 1
    keep = np.zeros(nE * nW, bool)
    keep[np.asarray(cells)] = True
    keep = keep.reshape(nE, nW)
    x0 = project(P["tune_v1"], "EW").reshape(nE, nW)
    out = {}
    for v in VERTICES:
        dx = np.where(keep, project(P[v], "EW").reshape(nE, nW) - x0, 0.0)
        out[v] = (np.abs(dx).sum(axis=0) / np.abs(dx.sum(axis=0))).tolist()
    return out


def checks(rungs, readouts=_HERE / "readouts"):
    """The run's controls: each a maximum absolute deviation, required <= TOL."""
    dep = L.load_json(readouts / "departure.json")["spaces"]["EW"]
    out = {}
    for rung, rec in rungs.items():
        X = L.load_json(readouts / f"{rung}_e.json")["spaces"]["EW"]["vertices"]
        dev = {"closure_truth_equals_npz_departure": 0.0, "tune_v1_closure_bias": 0.0,
               "ew_shift_reproduces_readout": 0.0, "ew_departure_reproduces_departure_json": 0.0}
        for axis, ax in rec.items():
            c = ax["closure_nuwro"]
            m = np.isfinite(np.asarray(c["dc"], float))
            dev["closure_truth_equals_npz_departure"] = max(dev["closure_truth_equals_npz_departure"], float(np.max(
                np.abs(np.asarray(c["dc"], float)[m] - np.asarray(ax["vertices"]["nuwro"]["d"], float)[m]))))
            dev["tune_v1_closure_bias"] = max(dev["tune_v1_closure_bias"],
                                              float(np.nanmax(np.abs(np.asarray(c["control_b_tune_v1"], float)))))
        ew = rec["EW"]
        if ew["cells"] != dep[rung]["cells"]:
            raise SystemExit(f"[FAIL] {rung}: EW cells differ from departure.json")
        for v in VERTICES:
            dev["ew_shift_reproduces_readout"] = max(dev["ew_shift_reproduces_readout"], float(np.max(np.abs(
                np.asarray(ew["vertices"][v]["s"]) - np.asarray(X[v]["shift"])))))
            dev["ew_departure_reproduces_departure_json"] = max(dev["ew_departure_reproduces_departure_json"], float(
                np.max(np.abs(np.asarray(ew["vertices"][v]["d"]) - np.asarray(dep[rung]["vertices"][v]["departure"])))))
        bound = {"closure_truth_equals_npz_departure": TRUTH_TOL,
                 "tune_v1_closure_bias": L.load_json(readouts / f"{rung}_e.json")["controls"]["PC"]["closure_floor"]["max"],
                 "ew_shift_reproduces_readout": TOL, "ew_departure_reproduces_departure_json": TOL}
        out[rung] = {"max_abs_deviation": dev, "bound": bound, "pass": all(dev[k] <= bound[k] for k in dev)}
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--npz", type=Path, required=True, help="the 5D npz")
    ap.add_argument("--expect-npz-sha256", required=True)
    ap.add_argument("--products", type=Path, required=True, help="the campaign's products directory")
    ap.add_argument("--ratios", type=Path, required=True, help="the frozen prep/ratios directory")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        raise SystemExit(f"[FAIL] refusing to overwrite {a.out}")
    verify_inputs(a.products, a.ratios, a.npz, a.expect_npz_sha256)
    z = np.load(a.npz, allow_pickle=True)  # the npz's axis names are an object array
    rungs, canc = {}, {}
    for rung in RUNGS:
        cells = L.load_json(_HERE / "readouts" / f"{rung}_e.json")["cells"]["EW"]
        P = products(a.products, rung)
        rungs[rung] = readout(*truth_weights(z, a.ratios, rung), P, cells)
        canc[rung] = cancellation(P, cells)
    chk = checks(rungs)
    for rung, c in chk.items():
        print(f"[proj1d] {rung} checks: " + ", ".join(f"{k} {v:.1e}" for k, v in c["max_abs_deviation"].items()))
    if not all(c["pass"] for c in chk.values()):
        raise SystemExit("[FAIL] a check failed; nothing written")
    out = {"schema": "pvl-proj1d/1", "post_hoc": True, "axes": list(L.AXES5),
           "edges": {x: list(L.FINE[x]) for x in L.AXES5},
           "inputs": {"npz_sha256": a.expect_npz_sha256, "receipts_sha256": L.sha256_path(RECEIPTS),
                      "prep_sums_sha256": L.sha256_path(_HERE / "prep-SHA256SUMS"),
                      "readouts_sha256": {f.name: L.sha256_path(f) for f in
                                          [_HERE / "readouts" / "departure.json"] +
                                          [_HERE / "readouts" / f"{r}_e.json" for r in RUNGS]}},
           "code": {"pvl_proj1d.py": L.sha256_path(__file__), "pvl_lib.py": L.sha256_path(L.__file__)},
           "checks": chk, "summary": {r: summary(rec) for r, rec in rungs.items()},
           "within_W_cancellation": canc, "rungs": rungs}
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    for rung in RUNGS:
        for axis, row in out["summary"][rung].items():
            print(f"[proj1d] {rung} {axis}: " + ", ".join(f"{k} leak {x['leak']:.2f} (rms d {100 * x['rms_d']:.1f} %)"
                                                         for k, x in row.items()))
        print(f"[proj1d] {rung} within-W cancellation: " +
              "; ".join(f"{v} " + " ".join(f"{t:.1f}" for t in c) for v, c in canc[rung].items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
