#!/usr/bin/env python3
"""RE-1 C2 supplement: the director's descriptive additions to the declared C2 readout (no new unfolds).

    re1_c2_supplement.py --eu E_U.root --cov production_cov.npz --q s5_plus_playlist.npz \
        --expect-eu-sha256 S --expect-cov-sha256 S --expect-q-sha256 S \
        --pseudo-dir DIR --seeds 1:20 --readout readout_2d_full.json --cache cache.npz \
        --expect-cache-sha256 S --out supplement.json --tsv cells.tsv

On the same 205 cells and sigmas as ``re1_2d_analyze.py`` (whose loaders it reuses):

* each arm's mean residual against truth in sigma_total (Q) as well as sigma_stat;
* each arm's per-cell spread over the seeds (SD, ddof 1) against sigma_stat, so the yardstick for a
  20-seed mean can be judged (the SE of the mean is SD / sqrt(n));
* the purity background fraction B / D of each cell's reco bin, from the driver's own reco histograms
  stored in the cache (``h_data_driver``, ``h_bkg_driver``, with under/overflow), and how the flagged
  cells rank on it. Reco and truth cells share the (pT, p||) binning; the fraction is a reco-level property.

The flagged cells are read from the declared readout, never recomputed here. MEASURES: descriptive
numbers. CANNOT AUTHORIZE: any change to the adopted 2D result, or a verdict other than the declared one.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import re1_2d_analyze as A  # noqa: E402


def background_fraction(cache: Path, cells: np.ndarray) -> np.ndarray:
    z = np.load(cache, allow_pickle=False)
    d, b = z["h_data_driver"][1:-1, 1:-1], z["h_bkg_driver"][1:-1, 1:-1]
    if d.shape != (14, 16):
        raise RuntimeError(f"driver reco histograms have shape {d.shape}, not (14, 16) inside the flow bins")
    return (b / np.where(d > 0, d, np.nan)).ravel(order="C")[cells]


def seeds_arrays(pseudo_dir: Path, seeds: list[int], cells: np.ndarray) -> dict:
    rows = {"purity": [], "refined": [], "xtrue": []}
    for s in seeds:
        d = np.load(pseudo_dir / f"nominal_s{s}.npz", allow_pickle=False)
        if json.loads(str(d["meta"]))["pseudo_seed"] != s:
            raise RuntimeError(f"nominal_s{s}.npz records another seed")
        rows["purity"].append(d["xsec_purity"].ravel(order="C")[cells])
        rows["refined"].append(d["xsec_refined"].ravel(order="C")[cells])
        rows["xtrue"].append(d["xtrue"].ravel(order="C")[cells])
    return {k: np.array(v) for k, v in rows.items()}


def supplement(x: dict, ref: dict, frac: np.ndarray, flagged: list[int]) -> tuple[dict, list[dict]]:
    cells, ss, st = ref["cells"], ref["sigma_stat"], ref["sigma_total"]
    n = x["xtrue"].shape[0]
    out = {"n_experiments": n, "n_cells": int(cells.size), "flagged_globalids": flagged}
    per = {"globalid": cells, "bkg_fraction": frac}
    for arm in ("purity", "refined"):
        r = x[arm] - x["xtrue"]
        m, sd = r.mean(axis=0), r.std(axis=0, ddof=1)
        per[f"{arm}_resid_stat"], per[f"{arm}_resid_total"] = m / ss, m / st
        per[f"{arm}_sd_over_stat"] = sd / ss
        out[arm] = {"mean_residual_in_total_sigma": A.with_ids(A.summary(m / st), m / st, cells),
                    "mean_residual_in_stat_sigma": A.with_ids(A.summary(m / ss), m / ss, cells),
                    "sd_over_stat": {"median": float(np.median(sd / ss)), "min": float(np.min(sd / ss)),
                                     "max": float(np.max(sd / ss))}}
    is_f = np.isin(cells, flagged)
    rank = (-frac).argsort().argsort() + 1                    # 1 = largest background fraction
    out["bkg_fraction"] = {
        "all": {"median": float(np.nanmedian(frac)), "min": float(np.nanmin(frac)), "max": float(np.nanmax(frac))},
        "flagged": {"median": float(np.nanmedian(frac[is_f])), "min": float(np.nanmin(frac[is_f])),
                    "max": float(np.nanmax(frac[is_f]))},
        "unflagged": {"median": float(np.nanmedian(frac[~is_f])), "max": float(np.nanmax(frac[~is_f]))},
        "flagged_ranks_of_205": sorted(int(v) for v in rank[is_f]),
        "flagged_among_top_k": {"k": int(is_f.sum()), "n": int((rank[is_f] <= is_f.sum()).sum())},
        "spearman_bkg_fraction_vs_abs_purity_resid_stat": spearman(frac, np.abs(per["purity_resid_stat"])),
        "spearman_bkg_fraction_vs_abs_refined_resid_stat": spearman(frac, np.abs(per["refined_resid_stat"]))}
    per["bkg_fraction_rank"] = rank
    per["flagged"] = is_f
    keys = list(per)
    rows = [{k: (bool(per[k][i]) if k == "flagged" else int(per[k][i]) if k in ("globalid", "bkg_fraction_rank")
                 else float(per[k][i])) for k in keys} for i in range(cells.size)]
    return out, rows


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    ok = np.isfinite(a) & np.isfinite(b)
    ra, rb = a[ok].argsort().argsort(), b[ok].argsort().argsort()
    return float(np.corrcoef(ra, rb)[0, 1])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    for k in ("eu", "cov", "q", "cache"):
        ap.add_argument(f"--{k}", type=Path, required=True)
        ap.add_argument(f"--expect-{k}-sha256", required=True)
    ap.add_argument("--pseudo-dir", type=Path, required=True)
    ap.add_argument("--seeds", required=True, help="FIRST:LAST inclusive")
    ap.add_argument("--readout", type=Path, required=True, help="the declared readout's JSON (re1_2d_analyze.py)")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--tsv", type=Path, required=True)
    a = ap.parse_args(argv)
    for k in ("eu", "cov", "q", "cache"):
        got = A.sha256_path(getattr(a, k))
        if got != getattr(a, f"expect_{k}_sha256"):
            print(f"--{k} sha256 {got} differs from the expected one", file=sys.stderr)
            return 4
    ref = A.reference(A.read_eu(a.eu), dict(np.load(a.cov)), dict(np.load(a.q)))
    first, last = (int(v) for v in a.seeds.split(":"))
    seeds = list(range(first, last + 1))
    declared = json.loads(a.readout.read_text())["c2"]
    if declared["seeds"] != seeds:
        raise RuntimeError(f"the readout's seeds {declared['seeds']} are not {seeds}")
    flagged = sorted({g for f in declared["flags"] if "globalids" in f for g in f["globalids"]})
    out, rows = supplement(seeds_arrays(a.pseudo_dir, seeds, ref["cells"]), ref,
                           background_fraction(a.cache, ref["cells"]), flagged)
    out.update({"schema": "re1-c2-supplement/1", "declared_verdict": declared["verdict"],
                "readout_sha256": A.sha256_path(a.readout), "code_sha256": A.sha256_path(Path(__file__).resolve())})
    a.out.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    with open(a.tsv, "w") as fh:
        fh.write("\t".join(rows[0]) + "\n")
        for r in rows:
            fh.write("\t".join(f"{v:.6g}" if isinstance(v, float) else str(v) for v in r.values()) + "\n")
    print(json.dumps({"flagged": len(flagged), "among_top_k": out["bkg_fraction"]["flagged_among_top_k"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
