"""COVFIX rev 12 §4.2: calibrate the u = 2 amplitude range [a_lo, a_hi] from the public build truths.

  python3 -B covfix_u2_calibrate.py --inputs DIR --out FILE.json

Reads the four pinned 5D predictions (refusing any sha256 that differs from its pin) and writes one JSON record.
It refuses to overwrite --out.

The rule (§4.2):
- On the FINE grid, s is a generator's integrated cross section per cell (xsec_flat times the cell's 5D volume).
- In each (pT, p_par, E_avail) cell, xi and eta are the q3 and W bin indices, standardized within the cell under the
  cell's (q3, W) distribution. The ordinal index is used because the top q3 and W bins are open-ended (to 100).
  A cell is valid when both variances are positive; elsewhere phi = 0 and r = 1.
- rho is the within-cell correlation of (xi, eta). D_g is the mean over cells valid for both g and the reference of
  |rho_g - rho_ref|, weighted by the reference's cell total.
- The tilt phi_1 = xi * eta (standardized under the reference). r0 = exp(c * phi_1), clipped to [0.5, 2], then
  raked by IPF so that s_ref * r reproduces s_ref's joint (pT, p_par, E_avail) totals and its global q3 and W marginals
  to 1e-9 relative within 1000 iterations.
- A(c) is the reference-weighted mean within-cell |rho(s_ref * r) - rho(s_ref)|. a_lo and a_hi solve
  A(a) = min_g D_g and A(a) = max_g D_g by bisection, on a scan that must show A increasing.

MEASURES: the calibration constants. CANNOT AUTHORIZE: a draw, or any validation reading.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np

SHAPE = (14, 16, 7, 7, 6)
AXES = ("pt", "pz", "eavail", "q3", "W")
REFERENCE = "genie_cv"
PINS = {
    "genie_cv": ("genie_cv_xsec5d_full.npz", "cfa42210dfe9cadc8e9460333316a639bd719c9ae52ab1144be900372a9adcc2"),
    "genie_mec": ("genie_mec_xsec5d_full.npz", "c179855df6e42a5b8bab1f839aae675c53a5150f132649c855356ad75f26790f"),
    "nuwro": ("nuwro_cv_xsec5d_full.npz", "475a2871304db23efedbd5ab42a32d91c7f1d295b6dd0c907c46aa6d81c48070"),
    "gibuu": ("gibuu_cv_xsec5d_fluxfix.npz", "48917692ee1295902db3bec34d6c80e368f020ae7924dabbda7e996c461cca18"),
}
BUILD_TRUTHS = ("genie_mec", "nuwro", "gibuu")
ORIGIN = "/pscratch/sd/j/josephrb/s5p-20260926/gen5d_fluxfix/"
CLIP = (0.5, 2.0)
RAKE_TOL = 1e-9
RAKE_MAXIT = 1000
BISECT_TOL = 1e-6
SCAN = np.linspace(0.0, 2.0, 41)
NOISE_SEED = 20261124
NOISE_REPS = 20


class Refusal(Exception):
    pass


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def load(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """The integrated cross section per FINE cell, shape SHAPE, and its statistical standard deviation."""
    z = np.load(path, allow_pickle=False)
    if tuple(int(v) for v in z["shape"]) != SHAPE:
        raise Refusal(f"{path.name}: shape {tuple(z['shape'])} is not {SHAPE}")
    widths = [np.diff(z[f"edges_{a}"]) for a in AXES]
    vol = np.einsum("a,b,c,d,e->abcde", *widths)
    x = z["xsec_flat"].reshape(SHAPE)
    if not np.all(np.isfinite(x)) or np.any(x < 0):
        raise Refusal(f"{path.name}: xsec_flat is not finite and non-negative")
    sd = np.sqrt(z["sumw2_flat"].reshape(SHAPE))
    return x * vol, sd * vol


def noise_diagnostic(tables: dict[str, np.ndarray], sds: dict[str, np.ndarray]) -> dict:
    """Reported only, deciding nothing: each table's self-noise N = mean over NOISE_REPS Gaussian resamplings (by its
    sumw2, clipped at 0) of the reference-weighted mean |rho(resampled) - rho(table)|, and the quadrature
    sqrt(N_g^2 + N_ref^2), an approximate scale of D_g from statistics alone."""
    rng = np.random.default_rng(NOISE_SEED)
    weight = tables[REFERENCE].sum(axis=(3, 4))
    selfn = {}
    for g in (REFERENCE, *BUILD_TRUTHS):
        vals = [mean_abs_drho(np.clip(tables[g] + rng.standard_normal(SHAPE) * sds[g], 0.0, None), tables[g],
                              weight)[0] for _ in range(NOISE_REPS)]
        selfn[g] = float(np.mean(vals))
    return {"seed": NOISE_SEED, "reps": NOISE_REPS, "self_noise": selfn,
            "quadrature_vs_reference": {g: float(np.hypot(selfn[g], selfn[REFERENCE])) for g in BUILD_TRUTHS}}


def _moments(s: np.ndarray):
    """Per (pT, p_par, E_avail) cell: total, means and variances of the q3 and W indices, and validity."""
    qi = np.arange(SHAPE[3], dtype=float)[:, None]
    wi = np.arange(SHAPE[4], dtype=float)[None, :]
    tot = s.sum(axis=(3, 4))
    with np.errstate(invalid="ignore", divide="ignore"):
        p = s / tot[..., None, None]
        mq = (p * qi).sum(axis=(3, 4))
        mw = (p * wi).sum(axis=(3, 4))
        vq = (p * (qi - mq[..., None, None]) ** 2).sum(axis=(3, 4))
        vw = (p * (wi - mw[..., None, None]) ** 2).sum(axis=(3, 4))
    valid = (tot > 0) & (vq > 1e-12) & (vw > 1e-12)
    return tot, p, mq, mw, vq, vw, valid


def standardized(s: np.ndarray):
    """xi, eta (broadcast to SHAPE) standardized within each cell under s; zero where the cell is invalid."""
    tot, p, mq, mw, vq, vw, valid = _moments(s)
    qi = np.arange(SHAPE[3], dtype=float)[:, None]
    wi = np.arange(SHAPE[4], dtype=float)[None, :]
    with np.errstate(invalid="ignore", divide="ignore"):
        xi = (qi - mq[..., None, None]) / np.sqrt(vq)[..., None, None]
        eta = (wi - mw[..., None, None]) / np.sqrt(vw)[..., None, None]
    m = valid[..., None, None]
    return np.where(m, xi, 0.0), np.where(m, eta, 0.0), valid


def cell_corr(s: np.ndarray):
    """The within-cell correlation of the q3 and W indices, and the cells where it is defined."""
    xi, eta, valid = standardized(s)
    tot = s.sum(axis=(3, 4))
    with np.errstate(invalid="ignore", divide="ignore"):
        rho = (s * xi * eta).sum(axis=(3, 4)) / tot
    return np.where(valid, rho, 0.0), valid


def mean_abs_drho(s_a: np.ndarray, s_b: np.ndarray, weight: np.ndarray) -> tuple[float, int]:
    ra, va = cell_corr(s_a)
    rb, vb = cell_corr(s_b)
    both = va & vb
    w = weight[both]
    if w.sum() <= 0:
        raise Refusal("no cell is valid for both tables")
    return float((w * np.abs(ra[both] - rb[both])).sum() / w.sum()), int(both.sum())


def rake(w: np.ndarray, r0: np.ndarray) -> tuple[np.ndarray, int]:
    """IPF on w * r: restore w's joint (pT, p_par, E_avail) totals and global q3 and W marginals."""
    t_joint = w.sum(axis=(3, 4))
    t_q = w.sum(axis=(0, 1, 2, 4))
    t_w = w.sum(axis=(0, 1, 2, 3))
    r = r0.astype(float).copy()

    def ratio(target, got):
        with np.errstate(invalid="ignore", divide="ignore"):
            return np.where(target > 0, target / np.where(got > 0, got, 1.0), 1.0)

    for it in range(1, RAKE_MAXIT + 1):
        r *= ratio(t_joint, (w * r).sum(axis=(3, 4)))[..., None, None]
        r *= ratio(t_q, (w * r).sum(axis=(0, 1, 2, 4)))[None, None, None, :, None]
        r *= ratio(t_w, (w * r).sum(axis=(0, 1, 2, 3)))[None, None, None, None, :]
        v = w * r
        dev = max(_rel(v.sum(axis=(3, 4)), t_joint), _rel(v.sum(axis=(0, 1, 2, 4)), t_q),
                  _rel(v.sum(axis=(0, 1, 2, 3)), t_w))
        if dev <= RAKE_TOL:
            return r, it
    raise Refusal(f"IPF did not converge to {RAKE_TOL} in {RAKE_MAXIT} iterations")


def _rel(got: np.ndarray, target: np.ndarray) -> float:
    m = target > 0
    return float(np.max(np.abs(got[m] - target[m]) / target[m])) if m.any() else 0.0


def tilt(w: np.ndarray, c: float) -> np.ndarray:
    xi, eta, _ = standardized(w)
    return np.exp(np.clip(c * xi * eta, np.log(CLIP[0]), np.log(CLIP[1])))


def amplitude(w: np.ndarray, c: float) -> tuple[float, np.ndarray, int]:
    r, it = rake(w, tilt(w, c))
    a, _ = mean_abs_drho(w * r, w, w.sum(axis=(3, 4)))
    return a, r, it


def solve(w: np.ndarray, target: float, lo: float, hi: float) -> float:
    a_lo, _, _ = amplitude(w, lo)
    a_hi, _, _ = amplitude(w, hi)
    if not a_lo <= target <= a_hi:
        raise Refusal(f"target {target:.6g} outside A on [{lo}, {hi}] = [{a_lo:.6g}, {a_hi:.6g}]")
    while hi - lo > BISECT_TOL:
        mid = 0.5 * (lo + hi)
        if amplitude(w, mid)[0] < target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def calibrate(tables: dict[str, np.ndarray]) -> dict:
    w = tables[REFERENCE]
    weight = w.sum(axis=(3, 4))
    D = {}
    for g in BUILD_TRUTHS:
        d, n = mean_abs_drho(tables[g], w, weight)
        D[g] = {"D": d, "cells_valid_both": n}
    scan = []
    for c in SCAN:
        a, r, it = amplitude(w, float(c))
        scan.append({"c": float(c), "A": a, "ipf_iterations": it})
    As = [row["A"] for row in scan]
    if any(b <= a for a, b in zip(As[1:], As[2:])) or As[1] <= As[0]:
        raise Refusal("A(c) is not increasing on the scan")
    dmin = min(v["D"] for v in D.values())
    dmax = max(v["D"] for v in D.values())

    def bracket(t):
        for a, b in zip(scan, scan[1:]):
            if a["A"] <= t <= b["A"]:
                return a["c"], b["c"]
        raise Refusal(f"target {t:.6g} is outside the scan's A range [{As[0]:.6g}, {As[-1]:.6g}]")

    a_lo = solve(w, dmin, *bracket(dmin))
    a_hi = solve(w, dmax, *bracket(dmax))
    out = {"D": D, "D_min": dmin, "D_max": dmax, "scan": scan, "a_lo": a_lo, "a_hi": a_hi}
    for name, c in (("at_a_lo", a_lo), ("at_a_hi", a_hi)):
        a, r, it = amplitude(w, c)
        r0 = tilt(w, c)
        pop = w > 0
        out[name] = {"A": a, "ipf_iterations": it,
                     "clipped_fraction_of_populated_cells": float(np.mean((r0[pop] <= CLIP[0]) | (r0[pop] >= CLIP[1]))),
                     "raked_r_min": float(r[pop].min()), "raked_r_max": float(r[pop].max())}
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--inputs", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    a = ap.parse_args(argv)
    if a.out.exists():
        print(f"refused: {a.out} exists", file=sys.stderr)
        return 2
    try:
        tables, sds, inputs = {}, {}, {}
        for g, (name, pin) in PINS.items():
            path = a.inputs / name
            got = sha256_file(path)
            if got != pin:
                raise Refusal(f"{name}: sha256 {got} is not the pin {pin}")
            tables[g], sds[g] = load(path)
            inputs[g] = {"origin_path": ORIGIN + name, "sha256": got}
        result = calibrate(tables)
        result["noise_diagnostic"] = noise_diagnostic(tables, sds)
    except Refusal as e:
        print(f"refused: {e}", file=sys.stderr)
        return 3
    rec = {"schema": "covfix-u2-calibration/1", "inputs": inputs, "reference": REFERENCE,
           "rule": {"coordinates": "q3 and W bin indices, standardized within each (pT, p_par, E_avail) cell",
                    "weight": "the reference's integrated cross section per (pT, p_par, E_avail) cell",
                    "clip": list(CLIP), "rake_tol": RAKE_TOL, "rake_maxit": RAKE_MAXIT, "bisect_tol": BISECT_TOL},
           "code_sha256": sha256_file(Path(__file__).resolve()), **result}
    fd = os.open(a.out, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(fd, "w") as fh:
        json.dump(rec, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(f"a_lo {rec['a_lo']:.6f} a_hi {rec['a_hi']:.6f} D {json.dumps({g: v['D'] for g, v in rec['D'].items()})}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
