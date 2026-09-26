#!/usr/bin/env python3
"""s5p Stage 1: support, resolution and development residuals of candidate reporting definitions.

Contract ``stages.1_use_case`` of ``docs/orchestration/state/s5p/contract.json``: inspect efficiency,
migration, resolution, background fraction and effective sample size over the existing domain, on
development MC only, for the candidate reporting partitions

* ``EW``  -- the 42 (E_avail, W) cells of the fine grid (7 x 6), the adopted reporting projection;
* ``J``   -- the s5c joint partition H3 (3 x 3 x 3 x 3 x 3), its 109 supported cells;
* ``H2``  -- the coarser joint partition 2 x 2 x 2 x 2 x 2 (s5c_partition.py level H2).

Per reporting cell it reports, from the npz MC arrays and the s5c background dump (``measured`` is
never opened): the truth denominator, the truth-selected weight, completeness, the reco-passing
fraction of truth-selected weight, joint purity and stability, the expected reco-level signal and
background at data POT and the background fraction, and the MC effective sample size.

It also summarizes, per cell, the committed s5e development evidence for candidate R (products under
``--s5e-runs``; all of them are development operands for this successor): the mean relative residual,
its standard error and the ensemble relative SD at each development truth point (nominal, GiBUU/GENIE
E_avail, q3 a = 0.3, W1-W3), the statistical sigma of the 100-replica bootstrap of development
experiment 700000, and the relative data-bootstrap sigma of R on the real data (a width, no central
value is read or reported).

MEASURES: development-MC support/resolution and development residuals per candidate reporting cell.
CANNOT AUTHORIZE: the choice of a reporting definition (amendment 1 applies its frozen rule), any
coverage or validation claim, or any statement about the observed cross section.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

AXES = ("pt", "pz", "eavail", "q3", "W")
FINE = {
    "pt": [0.0, 0.07, 0.15, 0.25, 0.33, 0.4, 0.47, 0.55, 0.7, 0.85, 1.0, 1.25, 1.5, 2.5, 4.5],
    "pz": [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0, 40.0, 60.0],
    "eavail": [0.0, 0.1, 0.2, 0.4, 0.8, 1.5, 3.0, 100.0],
    "q3": [0.0, 0.2, 0.4, 0.6, 0.8, 1.2, 2.0, 100.0],
    "W": [0.0, 1.1, 1.4, 1.8, 2.2, 3.0, 100.0],
}
J_EDGES = {"pt": [0.0, 0.55, 0.85, 4.5], "pz": [1.5, 3.5, 6.0, 60.0], "eavail": [0.0, 0.4, 1.5, 100.0],
           "q3": [0.0, 1.2, 2.0, 100.0], "W": [0.0, 1.4, 2.2, 100.0]}
H2_EDGES = {"pt": [0.0, 0.7, 4.5], "pz": [1.5, 4.5, 60.0], "eavail": [0.0, 0.8, 100.0],
            "q3": [0.0, 2.0, 100.0], "W": [0.0, 1.8, 100.0]}
SUPPORT_MIN = 1000.0
S5E_POINTS = {  # development operands for this successor (directory under --s5e-runs, glob)
    "nominal": [("cand/dev/k1_R", "nominal_a0_s*.npz"), ("cand/assess/nominal", "nominal_a0_s*.npz")],
    "eavail_gibuu": [("cand/dev/k2", "*.npz"), ("cand/assess/eavail_gibuu", "*.npz")],
    "q3": [("cand/dev/k3", "*.npz"), ("cand/assess/q3", "*.npz")],
    "W1": [("cand/assess/W1", "*.npz")],
    "W2": [("cand/assess/W2", "*.npz")],
    "W3": [("cand/assess/W3", "*.npz")],
}


def fine_shape() -> tuple[int, ...]:
    return tuple(len(FINE[a]) - 1 for a in AXES)


def fine_index(coords: np.ndarray) -> np.ndarray:
    """Flat fine-grid index (C order), -1 outside; histogramdd semantics (last edge closed)."""
    shape = fine_shape()
    idx, inside = [], np.ones(coords.shape[0], bool)
    for k, a in enumerate(AXES):
        e = np.asarray(FINE[a])
        i = np.searchsorted(e, coords[:, k], side="right") - 1
        i = np.where(coords[:, k] == e[-1], len(e) - 2, i)
        inside &= (i >= 0) & (i < len(e) - 1)
        idx.append(np.clip(i, 0, len(e) - 2))
    return np.where(inside, np.ravel_multi_index(idx, shape), -1)


def coarse_map(edges: dict, supported: list[int] | None = None) -> tuple[np.ndarray, int]:
    """Fine flat index -> reporting-cell index (-1 = not reported). Fine cells are assigned by centre."""
    shape = fine_shape()
    idx = np.unravel_index(np.arange(int(np.prod(shape))), shape)
    cidx, cshape = [], []
    for k, a in enumerate(AXES):
        f = np.asarray(FINE[a])
        c = np.asarray(edges[a])
        for x in c:
            if not np.any(np.isclose(f, x)):
                raise ValueError(f"coarse edge {x} of {a} is not a fine edge")
        centres = 0.5 * (f[:-1] + f[1:])[idx[k]]
        cidx.append(np.clip(np.searchsorted(c, centres, side="right") - 1, 0, len(c) - 2))
        cshape.append(len(c) - 1)
    cell = np.ravel_multi_index(cidx, cshape)
    if supported is None:
        return cell, int(np.prod(cshape))
    lut = -np.ones(int(np.prod(cshape)), int)
    lut[np.asarray(supported)] = np.arange(len(supported))
    return lut[cell], len(supported)


def ew_map() -> tuple[np.ndarray, int]:
    shape = fine_shape()
    idx = np.unravel_index(np.arange(int(np.prod(shape))), shape)
    return idx[2] * shape[4] + idx[4], shape[2] * shape[4]


def fine_volume() -> np.ndarray:
    shape = fine_shape()
    idx = np.unravel_index(np.arange(int(np.prod(shape))), shape)
    v = np.ones(idx[0].size)
    for k, a in enumerate(AXES):
        v *= np.diff(np.asarray(FINE[a]))[idx[k]]
    return v


def sums(cell_of_fine: np.ndarray, n: int, fine_idx: np.ndarray, w: np.ndarray, mask: np.ndarray) -> np.ndarray:
    sel = mask & (fine_idx >= 0)
    c = cell_of_fine[fine_idx[sel]]
    ok = c >= 0
    return np.bincount(c[ok], weights=w[sel][ok], minlength=n)


def mc_properties(d: dict, bkg: dict, cmap: np.ndarray, n: int) -> dict:
    ft, fr = d["ft"], d["fr"]
    pr, pt, wt, wr = d["pass_reco"], d["pass_truth"], d["w_truth"], d["w_reco"]
    ct = np.where(ft >= 0, cmap[np.maximum(ft, 0)], -1)
    cr = np.where(fr >= 0, cmap[np.maximum(fr, 0)], -1)
    denom = np.bincount(cmap[cmap >= 0], weights=d["denom_flat"][cmap >= 0], minlength=n)
    truth_sel = sums(cmap, n, ft, wt, pt)
    truth_sel_reco = sums(cmap, n, ft, wt, pt & pr)
    sw2 = sums(cmap, n, ft, wt * wt, pt)
    reco_all = sums(cmap, n, fr, wr, pr)
    same = pr & pt & (ct >= 0) & (ct == cr)
    reco_same = np.bincount(cr[same], weights=wr[same], minlength=n)
    truth_reco = sums(cmap, n, ft, wr, pt & pr)
    fb = fine_index(bkg["bkg_reco"].astype(float))
    b_reco = sums(cmap, n, fb, np.asarray(bkg["bkg_w"], float), np.ones(fb.size, bool))
    with np.errstate(divide="ignore", invalid="ignore"):
        out = {
            "truth_denominator": denom, "truth_selected": truth_sel,
            "completeness": truth_sel / denom,
            "reco_passing_fraction": truth_sel_reco / truth_sel,
            "purity": reco_same / reco_all, "stability": reco_same / truth_reco,
            "expected_reco_signal": reco_all, "expected_reco_background": b_reco,
            "background_fraction": b_reco / (reco_all + b_reco),
            "mc_neff_truth": truth_sel ** 2 / sw2,
        }
    return {k: np.nan_to_num(v, nan=0.0).tolist() for k, v in out.items()}


def cell_xsec(flat: np.ndarray, cmap: np.ndarray, n: int, vol: np.ndarray) -> np.ndarray:
    ok = cmap >= 0
    return np.bincount(cmap[ok], weights=(flat * vol)[ok], minlength=n)


def load_products(root: Path, specs: list) -> list[Path]:
    files = []
    for sub, pat in specs:
        files += sorted((root / sub).glob(pat))
    return files


def residual_summary(files: list[Path], maps: dict, vol: np.ndarray, reported: dict) -> dict:
    """Per reported cell: mean relative residual (f_hat - f_true) / f_true over the experiments, its SE and
    the ensemble relative SD; the mean truth per cell (for the departure size); summaries over the
    REPORTED cells only (cells without expected signal are carried with zeros and excluded)."""
    per = {name: {"rel": [], "truth": []} for name in maps}
    for f in files:
        z = np.load(f, allow_pickle=False)
        xs, xt = z["xsec_flat"], z["xtrue_flat"]
        for name, (cmap, n) in maps.items():
            a, t = cell_xsec(xs, cmap, n, vol), cell_xsec(xt, cmap, n, vol)
            with np.errstate(divide="ignore", invalid="ignore"):
                per[name]["rel"].append(np.where(t > 0, a / t - 1.0, 0.0))
            per[name]["truth"].append(t)
    out = {"n": len(files), "files_first_last": [files[0].name, files[-1].name] if files else []}
    for name in maps:
        R = np.array(per[name]["rel"])
        m, sd = R.mean(0), R.std(0, ddof=1)
        ok = reported[name]
        out[name] = {"mean_rel": m.tolist(), "se_rel": (sd / np.sqrt(R.shape[0])).tolist(), "rel_sd": sd.tolist(),
                     "mean_truth": np.array(per[name]["truth"]).mean(0).tolist(),
                     "median_abs_mean_pct": float(np.median(np.abs(m[ok])) * 100),
                     "max_abs_mean_pct": float(np.abs(m[ok]).max() * 100),
                     "argmax": int(np.flatnonzero(ok)[np.argmax(np.abs(m[ok]))])}
    return out


def departure_summary(points: dict, maps: dict, reported: dict) -> dict:
    """Departure size per cell: mean truth at the point over mean nominal truth, minus one (each point's
    truths are B-half truths of its own experiments, so this carries MC-half noise at the 0.1% level);
    and the recovered fraction 1 - |mean residual| / |departure| where the departure exceeds 1%."""
    out = {}
    for point, res in points.items():
        if point == "nominal":
            continue
        out[point] = {}
        for name in maps:
            t0 = np.asarray(points["nominal"][name]["mean_truth"])
            t1 = np.asarray(res[name]["mean_truth"])
            dep = np.where(t0 > 0, t1 / t0 - 1.0, 0.0)
            bias = np.abs(np.asarray(res[name]["mean_rel"]))
            ok = reported[name] & (np.abs(dep) > 0.01)
            rec = 1.0 - bias[ok] / np.abs(dep[ok])
            out[point][name] = {"departure_rel": dep.tolist(),
                                "median_abs_departure_pct": float(np.median(np.abs(dep[reported[name]])) * 100),
                                "max_abs_departure_pct": float(np.abs(dep[reported[name]]).max() * 100),
                                "n_cells_departure_gt_1pct": int(ok.sum()),
                                "recovered_fraction_median": float(np.median(rec)) if rec.size else None,
                                "recovered_fraction_p10": float(np.percentile(rec, 10)) if rec.size else None}
    return out


def sigma_rel(files: list[Path], maps: dict, vol: np.ndarray) -> dict:
    reps = {name: [] for name in maps}
    for f in files:
        xs = np.load(f, allow_pickle=False)["xsec_flat"]
        for name, (cmap, n) in maps.items():
            reps[name].append(cell_xsec(xs, cmap, n, vol))
    out = {"n": len(files)}
    for name in maps:
        R = np.array(reps[name])
        m = R.mean(0)
        out[name] = np.where(m > 0, R.std(0, ddof=1) / m, 0.0).tolist()
    return out


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 24), b""):
            h.update(block)
    return h.hexdigest()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--npz", type=Path, required=True)
    ap.add_argument("--bkg", type=Path, required=True)
    ap.add_argument("--s5c-contract", type=Path, required=True, help="for partition J's supported cells")
    ap.add_argument("--s5e-runs", type=Path, required=True)
    ap.add_argument("--expect-npz-sha256", required=True)
    ap.add_argument("--expect-bkg-sha256", required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        raise SystemExit(f"refusing to overwrite {a.out}")
    if sha256(a.npz) != a.expect_npz_sha256 or sha256(a.bkg) != a.expect_bkg_sha256:
        raise SystemExit("input digests differ from the expected ones")
    z = np.load(a.npz, allow_pickle=True)
    edges = [np.asarray(z[f"edges_{i}"], float) for i in range(int(z["nedges"]))]
    for k, ax in enumerate(AXES):
        if not np.allclose(edges[k], FINE[ax]):
            raise SystemExit(f"npz {ax} edges differ from the fine grid")
    d = {k: z[k] for k in ("MCgen", "MCreco", "pass_reco", "pass_truth", "w_truth", "w_reco")}
    d["pass_reco"], d["pass_truth"] = d["pass_reco"].astype(bool), d["pass_truth"].astype(bool)
    d["w_truth"], d["w_reco"] = d["w_truth"].astype(float), d["w_reco"].astype(float)
    d["ft"], d["fr"] = fine_index(d["MCgen"].astype(float)), fine_index(d["MCreco"].astype(float))
    d["denom_flat"] = np.asarray(z["denom_nd"], float).ravel(order="C")
    bz = np.load(a.bkg, allow_pickle=True)
    bkg = {"bkg_reco": bz["bkg_reco"], "bkg_w": bz["bkg_w"]}
    supported = json.loads(a.s5c_contract.read_text())["measurement"]["partition_J"]["supported_cells"]
    maps = {"EW": ew_map(), "J": coarse_map(J_EDGES, supported), "H2": coarse_map(H2_EDGES)}
    vol = fine_volume()
    receipt = {"schema": "s5p-stage1-inspect/1", "inputs": {"npz_sha256": a.expect_npz_sha256, "bkg_sha256": a.expect_bkg_sha256,
               "s5e_runs": str(a.s5e_runs)}, "partitions": {"EW": "7 E_avail x 6 W fine cells", "J": J_EDGES, "H2": H2_EDGES},
               "code_sha256": sha256(Path(__file__).resolve()), "mc": {}, "development_residuals": {}}
    for name, (cmap, n) in maps.items():
        receipt["mc"][name] = mc_properties(d, bkg, cmap, n)
        receipt["mc"][name]["n_cells"] = n
    reported = {}
    for name in maps:
        mc = receipt["mc"][name]
        sig, tru = np.asarray(mc["expected_reco_signal"]), np.asarray(mc["truth_selected"])
        reported[name] = (sig >= SUPPORT_MIN) & (tru >= SUPPORT_MIN)
        mc["reported"] = reported[name].tolist()
        mc["n_reported"] = int(reported[name].sum())
    receipt["support_rule"] = f"a cell is reported iff its expected reco-level signal and truth-selected weight at data POT are both >= {SUPPORT_MIN:g} (the s5c partition-J rule)"
    for point, specs in S5E_POINTS.items():
        files = load_products(a.s5e_runs, specs)
        receipt["development_residuals"][point] = residual_summary(files, maps, vol, reported)
    receipt["departures"] = departure_summary(receipt["development_residuals"], maps, reported)
    receipt["sigma_boot_dev_700000"] = sigma_rel(sorted((a.s5e_runs / "cand/dev/sigma").glob("boot_b*.npz")), maps, vol)
    data_boot = sorted((a.s5e_runs / "cand/assess/data/boot").glob("boot_b*.npz"))
    receipt["sigma_boot_data_R"] = sigma_rel(data_boot, maps, vol)
    a.out.write_text(json.dumps(receipt) + "\n")
    summary = {p: {n: (round(v[n]["median_abs_mean_pct"], 3), round(v[n]["max_abs_mean_pct"], 3)) for n in maps}
               for p, v in receipt["development_residuals"].items()}
    summary["recovered_fraction_median"] = {p: {n: v[n]["recovered_fraction_median"] for n in maps}
                                            for p, v in receipt["departures"].items()}
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
