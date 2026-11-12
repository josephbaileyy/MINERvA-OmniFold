#!/usr/bin/env python3
"""RSN prep (RSN-DECLARATION.md §2.1-2.2): the reweights of arms G6 (referee 3.1) and SM (referee 3.2), built from
L-5D-PV's frozen prep ratios, with their step shares and the SM manipulation check. Numpy only. It reads simulation
and generator predictions only and opens no unfold product.

G6  GiBUU's frozen gated ratio with every fine cell whose upper p_parallel edge exceeds 6 GeV/c set to r = 1 and
    labelled off, renormalized by pvl_lib.normalize over the assigned cells that remain. This is the addendum's option
    ii (H2-DEFINITION-ADDENDUM-GIBUU-DOMAIN.md §3), computed as gibuu_domain_cells.py computes it. GENIE+MEC and NuWro
    keep their frozen ratios.
SM  For each vertex: the prior-weighted moving average of the frozen reweight r over each region cell's radius-R
    neighbourhood (the region cells within R fine bins on every axis), renormalized over the region cells with prior
    weight. Off cells and region cells without prior weight keep r = 1. R = 1 is tried first, and R = 2 only if R = 1
    fails the manipulation check. If both fail, no SM reweight is written (§2.2).
The step share of a set of reweights, per reporting cell, is the prior's truth weight in fine cells that have an axis
neighbour whose r differs by more than pvl_lib.STEP (0.1), whatever the labels, taken as a union over the three
vertices, divided by the cell's prior weight. The manipulation check passes if SM's median share over the 16 cells is
at most half the frozen median AND SM's share is at most the frozen share in at least 12 of the 16 cells.

Refuses, writing nothing, unless:
  the frozen files match pv-ladder's committed prep-SHA256SUMS;
  normalize(rho, labels) reproduces every frozen r and k to 1e-12;
  the gate-or-cut share by pvl_lib.classify_cells reproduces h2_definition_describe.json's step_adjacent_share_union;
  G6's k and departures reproduce gibuu_domain_cells.json's option ii.

    rsn_prep.py --ratios <frozen prep/ratios/L-5D-PV> --out <OUT>/prep

MEASURES: arithmetic on frozen reweights. CANNOT AUTHORIZE: any unfold, any claim.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_PVL = _HERE.parent / "pv-ladder"
for _p in (str(_PVL), str(_HERE.parent)):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import pvl_lib as L  # noqa: E402
import s2_h2_scope as S2  # noqa: E402

VERTICES = ("genie_mec", "nuwro", "gibuu")
SHAPE = tuple(len(L.FINE[a]) - 1 for a in L.AXES5)
G6_PZ = 6.0
RADII = (1, 2)
MEDIAN_FRACTION = 0.5
MIN_CELLS_NOT_RAISED = 12
TOL = 1e-12


def box_sum(a: np.ndarray, radius: int) -> np.ndarray:
    """The sum of a (on SHAPE) over every cell's [-radius, radius] box on each axis, zero outside the grid."""
    out = np.asarray(a, float).reshape(SHAPE)
    for ax in range(out.ndim):
        n = out.shape[ax]
        c = np.cumsum(out, axis=ax)
        pad = [(0, 0)] * out.ndim
        pad[ax] = (1, 0)
        c = np.pad(c, pad)
        hi = np.minimum(np.arange(n) + radius + 1, n)
        lo = np.maximum(np.arange(n) - radius, 0)
        out = np.take(c, hi, axis=ax) - np.take(c, lo, axis=ax)
    return out.ravel()


def smooth(r: np.ndarray, label: np.ndarray, p: np.ndarray, radius: int) -> tuple[np.ndarray, float]:
    """SM's reweight for one vertex: the p-weighted mean of r over the region cells of each region cell's box, then
    normalize over the region cells with prior weight; every other cell keeps r = 1."""
    r, p = np.asarray(r, float), np.asarray(p, float)
    region = np.asarray(label, dtype=object) != "off"
    w = np.where(region, p, 0.0)
    num, den = box_sum(w * r, radius), box_sum(w, radius)
    assigned = region & (p > 0)
    raw = np.ones_like(r)
    raw[assigned] = num[assigned] / den[assigned]
    return L.normalize(raw, assigned, p)


def g6(rho: np.ndarray, label: np.ndarray, p: np.ndarray, pz_hi: np.ndarray) -> tuple[np.ndarray, float, np.ndarray]:
    """G6's GiBUU reweight: the frozen gate's rho and labels below 6 GeV/c, off above it, renormalized."""
    label = np.asarray(label, dtype=object)
    assigned = np.isin(label, ("fine", "coarse")) & (pz_hi <= G6_PZ)
    r, k = L.normalize(rho, assigned, p)
    lab = label.copy()
    lab[pz_hi > G6_PZ] = "off"
    return r, k, lab


def near_step(r: np.ndarray) -> np.ndarray:
    """Fine cells with an axis neighbour whose r differs by more than STEP, whatever the labels."""
    a = np.asarray(r, float).reshape(SHAPE)
    near = np.zeros(SHAPE, bool)
    for ax in range(len(SHAPE)):
        lo = [slice(None)] * len(SHAPE)
        hi = [slice(None)] * len(SHAPE)
        lo[ax], hi[ax] = slice(0, SHAPE[ax] - 1), slice(1, SHAPE[ax])
        big = np.abs(a[tuple(lo)] - a[tuple(hi)]) > L.STEP
        near[tuple(lo)] |= big
        near[tuple(hi)] |= big
    return near.ravel()


def shares(mask: np.ndarray, p: np.ndarray, rmap: np.ndarray, n: int) -> np.ndarray:
    ok = rmap >= 0
    P = np.bincount(rmap[ok], weights=p[ok], minlength=n)
    return np.bincount(rmap[ok], weights=(p * mask)[ok], minlength=n) / P


def departures(r: np.ndarray, p: np.ndarray, rmap: np.ndarray, n: int) -> np.ndarray:
    ok = rmap >= 0
    P = np.bincount(rmap[ok], weights=p[ok], minlength=n)
    return np.bincount(rmap[ok], weights=(p * r)[ok], minlength=n) / P - 1.0


def manipulation_check(frozen: np.ndarray, smoothed: np.ndarray) -> dict:
    med0, med = float(np.median(frozen)), float(np.median(smoothed))
    not_raised = int(np.sum(smoothed <= frozen))
    ok = med <= MEDIAN_FRACTION * med0 and not_raised >= MIN_CELLS_NOT_RAISED
    return {"pass": bool(ok), "median_frozen": med0, "median_smoothed": med, "cells_not_raised": not_raised,
            "rule": f"median <= {MEDIAN_FRACTION} x the frozen median and not raised in >= {MIN_CELLS_NOT_RAISED} of 16"}


def ratio_record(vertex: str, label: str, r: np.ndarray, extra: dict) -> dict:
    rec = {"schema": L.RATIO_SCHEMA, "vertex": vertex, "label": label, "axes": list(L.AXES5),
           "edges": {a: list(L.FINE[a]) for a in L.AXES5}, "r": np.asarray(r, float).tolist()}
    rec.update(extra)
    return rec


def load_frozen(ratios: Path, prep_sums: Path) -> tuple[dict, dict, dict]:
    sums = dict(ln.split()[::-1] for ln in prep_sums.read_text().splitlines() if ln.strip())
    inputs = {}
    for f in ["ratios.json"] + [f"{v}.json" for v in VERTICES]:
        inputs[f] = S2.check(ratios / f, sums[f"./ratios/{S2.RUNG}/{f}"], f)
    R = L.load_json(ratios / "ratios.json")
    frozen = {}
    for v in VERTICES:
        rv = R["vertices"][v]
        rf = L.load_json(ratios / rv["ratio_file"])
        frozen[v] = {"rho": np.asarray(rv["rho"], float), "label": np.asarray(rv["label"], dtype=object),
                     "r": np.asarray(rf["r"], float), "k": float(rv["k"]), "sha256": inputs[f"{v}.json"]}
    return R, frozen, inputs


def check_frozen(frozen: dict, p: np.ndarray) -> None:
    for v, f in frozen.items():
        r, k = L.normalize(f["rho"], np.isin(f["label"], ("fine", "coarse")), p)
        if not np.allclose(r, f["r"], rtol=TOL, atol=0) or abs(k - f["k"]) > TOL * f["k"]:
            raise SystemExit(f"[FAIL] normalize(rho, labels) does not reproduce the frozen {v} reweight")


def check_describe(frozen: dict, p: np.ndarray, rmap: np.ndarray, n: int, describe: dict) -> np.ndarray:
    near = np.zeros(p.size, bool)
    for f in frozen.values():
        near |= np.isin(L.classify_cells(f["r"], f["label"], SHAPE), ("gate", "cut"))
    got = shares(near, p, rmap, n)
    want = np.asarray(describe["step_adjacent_share_union"], float)
    if got.shape != want.shape or not np.allclose(got, want, rtol=TOL, atol=1e-15):
        raise SystemExit("[FAIL] the gate-or-cut step share does not reproduce h2_definition_describe.json")
    return got


def check_domain(k6: float, d6: np.ndarray, domain: dict) -> None:
    if abs(k6 - float(domain["k"]["ii"])) > TOL * k6:
        raise SystemExit("[FAIL] G6's k is not gibuu_domain_cells.json's option ii")
    if not np.allclose(d6, np.asarray(domain["departure"]["ii"], float), rtol=0, atol=TOL):
        raise SystemExit("[FAIL] G6's departures are not gibuu_domain_cells.json's option ii")


def build(a) -> dict:
    if a.out.exists():
        raise SystemExit(f"[FAIL] refusing to write into the existing {a.out}")
    R, frozen, inputs = load_frozen(a.ratios, a.prep_sums)
    for key, path in (("definition", a.definition), ("describe", a.describe), ("domain", a.domain)):
        inputs[key] = L.sha256_path(path)
    p = np.asarray(R["prior_truth_weight"], float)
    if p.size != int(np.prod(SHAPE)):
        raise SystemExit("[FAIL] the prior truth weight is not on the 5D fine grid")
    D = L.load_json(a.definition)
    cell, _ = S2.h2_of_fine()
    rmap = np.asarray(D["h2_to_reporting_cell"])[cell]
    n = int(D["n_reporting_cells"])
    pz_hi = np.asarray(L.FINE["pz"][1:])[np.unravel_index(np.arange(p.size), SHAPE)[1]]

    check_frozen(frozen, p)
    gate_cut = check_describe(frozen, p, rmap, n, L.load_json(a.describe))
    gb = frozen["gibuu"]
    r6, k6, lab6 = g6(gb["rho"], gb["label"], p, pz_hi)
    d6 = departures(r6, p, rmap, n)
    check_domain(k6, d6, L.load_json(a.domain))

    blind = {"frozen": shares(np.logical_or.reduce([near_step(f["r"]) for f in frozen.values()]), p, rmap, n)}
    blind["G6"] = shares(np.logical_or.reduce([near_step(frozen["genie_mec"]["r"]), near_step(frozen["nuwro"]["r"]),
                                               near_step(r6)]), p, rmap, n)
    sm, checks, radius = {}, {}, None
    for rad in RADII:
        cand = {v: smooth(f["r"], f["label"], p, rad) for v, f in frozen.items()}
        s = shares(np.logical_or.reduce([near_step(c[0]) for c in cand.values()]), p, rmap, n)
        blind[f"SM_R{rad}"] = s
        checks[f"R{rad}"] = manipulation_check(blind["frozen"], s)
        if checks[f"R{rad}"]["pass"]:
            sm, radius = cand, rad
            break

    a.out.mkdir(parents=True)
    files = {}

    def write(rel: str, rec: dict) -> None:
        path = a.out / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(rec, indent=1) + "\n")
        files[rel] = L.sha256_path(path)

    write("G6/gibuu.json", ratio_record("gibuu", "GiBUU on p_parallel < 6 GeV/c (G6, RSN-DECLARATION.md §2.1)", r6,
                                        {"k": k6, "construction": "G6", "pz_max_cells": G6_PZ,
                                         "base_ratio_sha256": gb["sha256"]}))
    for v, (r, k) in sm.items():
        write(f"SM/{v}.json", ratio_record(v, f"{v}, frozen reweight smoothed at radius {radius} (SM, §2.2)", r,
                                           {"k": k, "construction": "SM", "radius": radius,
                                            "base_ratio_sha256": frozen[v]["sha256"]}))
    out = {"schema": "rsn-prep/1", "inputs": inputs,
           "code": {"rsn_prep.py": L.sha256_path(__file__), "pvl_lib.py": L.sha256_path(L.__file__),
                    "s2_h2_scope.py": L.sha256_path(S2.__file__)},
           "controls": {"frozen_reweights_reproduced": True, "gate_or_cut_share_reproduced": True,
                        "g6_reproduces_option_ii": True},
           "g6": {"k": k6, "k_frozen": gb["k"], "departure": d6.tolist(),
                  "departure_frozen": departures(gb["r"], p, rmap, n).tolist()},
           "sm": {"radius": radius, "status": "built" if sm else "not built: both radii failed the manipulation check",
                  "checks": checks,
                  "k": {v: k for v, (_, k) in sm.items()},
                  "departure": {v: departures(r, p, rmap, n).tolist() for v, (r, _) in sm.items()},
                  "departure_frozen": {v: departures(f["r"], p, rmap, n).tolist() for v, f in frozen.items()}},
           "step_share": {"gate_or_cut_frozen": gate_cut.tolist(), **{k: v.tolist() for k, v in blind.items()}},
           "files": files}
    (a.out / "prep.json").write_text(json.dumps(out, indent=1) + "\n")
    for rel, sha in sorted(files.items()):
        print(f"{sha}  ./{rel}")
    print(f"[rsn] G6 k {k6:.6f}; SM {out['sm']['status']}" + (f" at radius {radius}" if sm else ""), file=sys.stderr)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ratios", type=Path, required=True, help="the frozen prep/ratios/L-5D-PV directory")
    ap.add_argument("--prep-sums", type=Path, default=_PVL / "prep-SHA256SUMS")
    ap.add_argument("--definition", type=Path, default=_PVL / "readouts" / "h2_definition.json")
    ap.add_argument("--describe", type=Path, default=_PVL / "readouts" / "h2_definition_describe.json")
    ap.add_argument("--domain", type=Path, default=_PVL / "readouts" / "gibuu_domain_cells.json")
    ap.add_argument("--out", type=Path, required=True)
    build(ap.parse_args(argv))
    return 0


if __name__ == "__main__":
    sys.exit(main())
