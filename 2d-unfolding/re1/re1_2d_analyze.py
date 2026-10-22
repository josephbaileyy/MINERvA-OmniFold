#!/usr/bin/env python3
"""RE-1 2D readouts: the K1 control, the C2 closure readout and the D2 data movement table.

    re1_2d_analyze.py --eu E_U.root --cov production_cov.npz --q s5_plus_playlist.npz \
        --expect-eu-sha256 S --expect-cov-sha256 S --expect-q-sha256 S \
        [--k1 data_purity.npz] [--d2 data_refined.npz] [--pseudo-dir DIR --seeds 1:20] --out readout.json

Cells are the adopted product's 205 reported cells: ``E_U``'s ``hXSec2D > 0`` in [ix, iy] order (paper
GlobalID ``ix * 16 + iy``), checked to reproduce the covariance file's ``cells_x_EU`` exactly. The
statistical sigma is ``sqrt(diag(stat))`` of the S5 production covariance; the total sigma is
``sqrt(diag(total_plus_C_PL))`` of Q, the adopted 2D uncertainty (DECISION-20261017). Both are absolute.

Fixed by the declaration before any product exists:

* K1 PASS: the purity data unfold equals ``E_U``'s ``hXSec2D`` on every reported cell to a relative
  difference of at most 1e-8 (bitwise is reported separately), and reports the same cell set.
* C2, per RE1-SPEC section 3: FLAG for Joseph if any cell's mean arm difference exceeds 1 statistical
  sigma, or the integrated mean arm difference exceeds 0.5 % of the integrated truth; otherwise
  NO-FLAG (the refinement does not change the 2D result at that level).
* D2 is a descriptive table: (refined - purity) on the real data, per cell, in total sigma.

MEASURES: the declared readouts. CANNOT AUTHORIZE: any change to the adopted 2D result.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

K1_REL_TOL = 1e-8
C2_CELL_STAT_SIGMA = 1.0
C2_INTEGRAL_FRACTION = 0.005


def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 24), b""):
            h.update(block)
    return h.hexdigest()


def read_eu(path: Path) -> np.ndarray:
    import ROOT
    f = ROOT.TFile.Open(str(path), "READ")
    h = f.Get("hXSec2D")
    if not h:
        raise RuntimeError(f"no hXSec2D in {path}")
    out = np.array([[h.GetBinContent(ix, iy) for iy in range(1, h.GetNbinsY() + 1)]
                    for ix in range(1, h.GetNbinsX() + 1)])
    f.Close()
    return out


def reference(eu: np.ndarray, cov: dict, q: dict) -> dict:
    flat = eu.ravel(order="C")
    cells = np.flatnonzero(flat > 0)
    for name, d in (("production_cov", cov), ("s5_plus_playlist", q)):
        if cells.size != d["cells_x_EU"].size or not np.array_equal(flat[cells], d["cells_x_EU"]):
            raise RuntimeError(f"E_U's reported cells do not reproduce {name}'s cells_x_EU")
    if not np.array_equal(cov["area"], q["area"]):
        raise RuntimeError("the two files' cell areas differ")
    return {"cells": cells, "x_eu": flat[cells], "area": cov["area"],
            "sigma_stat": np.sqrt(np.diag(cov["stat"])), "sigma_s5_total": np.sqrt(np.diag(cov["total"])),
            "sigma_total": np.sqrt(np.diag(q["total_plus_C_PL"]))}


def summary(z: np.ndarray) -> dict:
    a = np.abs(z)
    return {"median_abs": float(np.median(a)), "p84_abs": float(np.percentile(a, 84)), "max_abs": float(a.max()),
            "argmax_globalid": None, "n_over_0p5": int((a > 0.5).sum()), "n_over_1": int((a > 1).sum()),
            "mean_signed": float(z.mean())}


def with_ids(stats: dict, z: np.ndarray, cells: np.ndarray) -> dict:
    stats["argmax_globalid"] = int(cells[int(np.argmax(np.abs(z)))])
    return stats


def k1(product: Path, ref: dict, eu: np.ndarray) -> dict:
    x = np.load(product, allow_pickle=False)["xsec"].ravel(order="C")
    flat = eu.ravel(order="C")
    same_cells = np.array_equal(np.flatnonzero(x > 0), ref["cells"])
    rel = np.abs(x[ref["cells"]] / ref["x_eu"] - 1.0)
    return {"product_sha256": sha256_path(product), "same_cell_set": bool(same_cells),
            "bitwise_all_224": bool(np.array_equal(x, flat)), "max_rel": float(rel.max()),
            "median_rel": float(np.median(rel)), "tolerance": K1_REL_TOL,
            "verdict": "PASS" if same_cells and rel.max() <= K1_REL_TOL else "FAIL"}


def d2(purity: Path, refined: Path, ref: dict) -> dict:
    xp = np.load(purity, allow_pickle=False)["xsec"].ravel(order="C")[ref["cells"]]
    xr = np.load(refined, allow_pickle=False)["xsec"].ravel(order="C")[ref["cells"]]
    d = xr - xp
    z_tot, z_stat = d / ref["sigma_total"], d / ref["sigma_stat"]
    ip, ir = float(ref["area"] @ xp), float(ref["area"] @ xr)
    return {"purity_sha256": sha256_path(purity), "refined_sha256": sha256_path(refined),
            "in_total_sigma": with_ids(summary(z_tot), z_tot, ref["cells"]),
            "in_stat_sigma": with_ids(summary(z_stat), z_stat, ref["cells"]),
            "relative_percent": with_ids(summary(100 * d / xp), 100 * d / xp, ref["cells"]),
            "integral_purity": ip, "integral_refined": ir, "integral_change_percent": 100 * (ir / ip - 1),
            "per_cell": [{"globalid": int(g), "purity": float(a), "refined": float(b), "z_total": float(zt),
                          "z_stat": float(zs)} for g, a, b, zt, zs in zip(ref["cells"], xp, xr, z_tot, z_stat)]}


def c2(pseudo_dir: Path, seeds: list[int], ref: dict) -> dict:
    rows = {"purity": [], "refined": [], "xtrue": []}
    digests = {}
    for s in seeds:
        p = pseudo_dir / f"nominal_s{s}.npz"
        d = np.load(p, allow_pickle=False)
        meta = json.loads(str(d["meta"]))
        if meta["pseudo_seed"] != s:
            raise RuntimeError(f"{p} records seed {meta['pseudo_seed']}")
        digests[p.name] = sha256_path(p)
        for arm in ("purity", "refined"):
            rows[arm].append(d[f"xsec_{arm}"].ravel(order="C")[ref["cells"]])
        rows["xtrue"].append(d["xtrue"].ravel(order="C")[ref["cells"]])
    xp, xr, xt = (np.array(rows[k]) for k in ("purity", "refined", "xtrue"))
    n = len(seeds)
    se = lambda a: a.std(axis=0, ddof=1) / np.sqrt(n)  # noqa: E731
    out = {"n_experiments": n, "seeds": seeds, "products": digests,
           "xtrue_max_rel_spread": float(np.max(np.ptp(xt, axis=0) / np.abs(xt.mean(axis=0))))}
    for arm, x in (("purity", xp), ("refined", xr)):
        r = x - xt
        z = r.mean(axis=0) / ref["sigma_stat"]
        out[arm] = {"mean_residual_in_stat_sigma": with_ids(summary(z), z, ref["cells"]),
                    "se_in_stat_sigma_median": float(np.median(se(r) / ref["sigma_stat"])),
                    "per_cell_mean_residual": r.mean(axis=0).tolist(), "per_cell_se": se(r).tolist()}
    diff = xr - xp
    z_stat, z_tot = diff.mean(axis=0) / ref["sigma_stat"], diff.mean(axis=0) / ref["sigma_total"]
    i_t = (xt @ ref["area"]).mean()
    i_d = diff @ ref["area"]
    frac, frac_se = float(i_d.mean() / i_t), float(i_d.std(ddof=1) / np.sqrt(n) / i_t)
    flags = []
    over = np.flatnonzero(np.abs(z_stat) > C2_CELL_STAT_SIGMA)
    if over.size:
        flags.append({"rule": "a cell's mean arm difference exceeds 1 statistical sigma",
                      "globalids": [int(ref["cells"][i]) for i in over]})
    if abs(frac) > C2_INTEGRAL_FRACTION:
        flags.append({"rule": "the integrated mean arm difference exceeds 0.5 %", "fraction": frac})
    out["arm_difference"] = {
        "in_stat_sigma": with_ids(summary(z_stat), z_stat, ref["cells"]),
        "in_total_sigma": with_ids(summary(z_tot), z_tot, ref["cells"]),
        "se_in_stat_sigma_median": float(np.median(se(diff) / ref["sigma_stat"])),
        "integral_fraction": frac, "integral_fraction_se": frac_se,
        "per_cell_mean": diff.mean(axis=0).tolist(), "per_cell_se": se(diff).tolist()}
    out["verdict"] = "FLAG" if flags else "NO-FLAG"
    out["flags"] = flags
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--eu", type=Path, required=True)
    ap.add_argument("--cov", type=Path, required=True)
    ap.add_argument("--q", type=Path, required=True)
    ap.add_argument("--expect-eu-sha256", required=True)
    ap.add_argument("--expect-cov-sha256", required=True)
    ap.add_argument("--expect-q-sha256", required=True)
    ap.add_argument("--k1", type=Path)
    ap.add_argument("--d2", type=Path, help="the refined data product; needs --k1 (the purity data product)")
    ap.add_argument("--pseudo-dir", type=Path)
    ap.add_argument("--seeds", help="FIRST:LAST inclusive")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    got = {"eu": sha256_path(a.eu), "cov": sha256_path(a.cov), "q": sha256_path(a.q)}
    want = {"eu": a.expect_eu_sha256, "cov": a.expect_cov_sha256, "q": a.expect_q_sha256}
    if got != want:
        print(f"input digests {got} differ from {want}", file=sys.stderr)
        return 4
    if a.d2 and not a.k1:
        print("--d2 needs --k1", file=sys.stderr)
        return 2
    eu = read_eu(a.eu)
    cov = dict(np.load(a.cov, allow_pickle=False))
    q = dict(np.load(a.q, allow_pickle=False))
    ref = reference(eu, cov, q)
    out = {"schema": "re1-2d-readout/1", "inputs_sha256": got, "n_cells": int(ref["cells"].size),
           "code_sha256": sha256_path(Path(__file__).resolve())}
    if a.k1:
        out["k1"] = k1(a.k1, ref, eu)
    if a.d2:
        out["d2"] = d2(a.k1, a.d2, ref)
    if a.pseudo_dir:
        first, last = (int(v) for v in a.seeds.split(":"))
        out["c2"] = c2(a.pseudo_dir, list(range(first, last + 1)), ref)
    a.out.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: out[k].get("verdict") for k in ("k1", "c2") if k in out}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
