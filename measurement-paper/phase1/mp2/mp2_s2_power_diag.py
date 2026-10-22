#!/usr/bin/env python3
"""MP-2 S2 power diagnostic (DESCRIPTIVE, 0 node-h; the director's approval of 2026-10-22 under addendum 14). It
tests the HYPOTHESIS that the GENIE classifiers stop early because the attainable validation-logloss gain is below
its own noise. It changes no verdict, no F_fallback specification and no declared step.

Per generator and feature set, from what the S2 jobs already wrote:
  achieved   ln 2 - best validation logloss of each model (the validation weights are class-balanced, so a constant
             predictor scores ln 2), with the best iteration and the validation counts
  binned     the Jensen-Shannon divergence between Tune C+H (in G's support, w_truth) and G (c, tgt != 0) over the
             5D fine cells: a lower bound on the gain a perfect classifier of (pt, pz, eavail, q3, W) attains. Its
             statistical bias is estimated from half-sample splits (JSD(T_even, T_odd) and JSD(G_even, G_odd), each
             about 4x its side's bias) and subtracted: an approximation, labelled so
  after      the same binned JSD with Tune reweighted by each replica's stored w_G (weights_<G>_<fset>.npz, the gates'
             weights), debiased the same way: how much of the binned 5D discrepancy the reweighting removed
  noise      the order of the standard error of a validation gain near that size, sqrt(2 JSD / n_eff), with
             n_eff = 1 / (1/n_T,val + 1/n_G,val): an order of magnitude, not a test

Usage: python3 mp2_s2_power_diag.py --fit DIR --harm DIR [DIR] --out JSON --gen G [G ...] --fset primary|fallback
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import math
from pathlib import Path

import numpy as np

SUPPORT = {"genie_cv": (0.0, 100.0), "genie_mec": (0.0, 100.0), "nuwro_ch": (0.5, 100.0), "gibuu_ch": (0.0, 20.0)}


def sha256(p) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def jsd(a, b):
    """JSD of two histograms (normalized here), nats."""
    p, q = a / a.sum(), b / b.sum()
    m = 0.5 * (p + q)
    with np.errstate(divide="ignore", invalid="ignore"):
        t1 = np.where(p > 0, p * np.log(p / m), 0.0)
        t2 = np.where(q > 0, q * np.log(q / m), 0.0)
    return float(0.5 * (t1.sum() + t2.sum()))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fit", type=Path, required=True)
    ap.add_argument("--harm", nargs="+", required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--gen", nargs="+", required=True)
    ap.add_argument("--fset", default="primary")
    a = ap.parse_args(argv)
    td = next(Path(d) for d in a.harm if (Path(d) / "tune_CH.npz").exists())
    tz = np.load(td / "tune_CH.npz")
    res = {"schema": "mp2-s2-power-diag/1", "status": "DESCRIPTIVE: a test of a hypothesis; changes no verdict",
           "tune": {"path": str(td / "tune_CH.npz"), "sha256": sha256(td / "tune_CH.npz")}, "generators": {}}
    for gen in a.gen:
        hd = next(Path(d) for d in a.harm if (Path(d) / f"events_{gen}.npz").exists())
        ev = np.load(hd / f"events_{gen}.npz")
        lo, hi = SUPPORT[gen]
        ins = (tz["enu"] >= lo) & (tz["enu"] <= hi)
        tf, tw, ti = tz["fine"][ins], tz["w_truth"][ins], tz["i"][ins]
        gm = ev["tgt"] != 0
        gf, gw, gj = ev["fine"][gm], ev["c"][gm], ev["j"][gm]
        nf = int(max(tf.max(), gf.max())) + 1
        T, Gh = np.bincount(tf, tw, nf), np.bincount(gf, gw, nf)
        te, to = np.bincount(tf[ti % 2 == 0], tw[ti % 2 == 0], nf), np.bincount(tf[ti % 2 == 1], tw[ti % 2 == 1], nf)
        ge, go = np.bincount(gf[gj % 2 == 0], gw[gj % 2 == 0], nf), np.bincount(gf[gj % 2 == 1], gw[gj % 2 == 1], nf)
        j_tg, j_tt, j_gg = jsd(T, Gh), jsd(te, to), jsd(ge, go)
        j_deb = j_tg - 0.25 * (j_tt + j_gg)
        wz = np.load(a.fit / f"weights_{gen}_{a.fset}.npz")
        if not np.array_equal(wz["i"], ti):
            raise SystemExit(f"{gen}: the weights file's rows are not the in-support Tune rows")
        after = []
        for k in range(5):
            w2 = tw * wz[f"wG_k{k}"]
            a2, ae, ao = np.bincount(tf, w2, nf), np.bincount(tf[ti % 2 == 0], w2[ti % 2 == 0], nf), np.bincount(tf[ti % 2 == 1], w2[ti % 2 == 1], nf)
            after.append(jsd(a2, Gh) - 0.25 * (jsd(ae, ao) + j_gg))
        metas = []
        for p in sorted(glob.glob(str(a.fit / f"model_{gen}_{a.fset}_k*h*f*.npz"))):
            m = json.loads(np.load(p)["meta_json"].item())
            metas.append(m)
        gain = np.array([math.log(2.0) - m["valid_logloss"] for m in metas])
        best = np.array([m["best_iteration"] for m in metas])
        nv = np.array([m["n_valid"] for m in metas], float)
        n_eff = 1.0 / (1.0 / nv[:, 0] + 1.0 / nv[:, 1])
        noise = np.sqrt(2.0 * max(j_deb, 0.0) / n_eff)
        res["generators"][gen] = {
            "events": {"path": str(hd / f"events_{gen}.npz"), "sha256": sha256(hd / f"events_{gen}.npz")},
            "n_models": len(metas), "fset": a.fset,
            "best_iteration_min_median_max": [int(best.min()), int(np.median(best)), int(best.max())],
            "achieved_gain_nats_min_median_max": [float(gain.min()), float(np.median(gain)), float(gain.max())],
            "binned_5D_JSD_nats": {"T_vs_G": j_tg, "T_even_vs_odd": j_tt, "G_even_vs_odd": j_gg,
                                   "T_vs_G_debiased_approx": j_deb, "n_cells_T": int((T > 0).sum()), "n_cells_G": int((Gh > 0).sum())},
            "binned_5D_JSD_after_reweighting_debiased_approx_replicas": after,
            "weights": {"path": str(a.fit / f"weights_{gen}_{a.fset}.npz"), "sha256": sha256(a.fit / f"weights_{gen}_{a.fset}.npz")},
            "validation_counts_median": [float(np.median(nv[:, 0])), float(np.median(nv[:, 1]))],
            "gain_noise_scale_nats_median": float(np.median(noise)),
            "achieved_over_binned_debiased_median": float(np.median(gain) / j_deb) if j_deb > 0 else None,
            "binned_debiased_over_noise_median": float(j_deb / np.median(noise)) if np.median(noise) > 0 else None,
        }
        print(gen, json.dumps(res["generators"][gen]["binned_5D_JSD_nats"]), "after", [round(x, 6) for x in after], "achieved", res["generators"][gen]["achieved_gain_nats_min_median_max"],
              "noise", res["generators"][gen]["gain_noise_scale_nats_median"], flush=True)
    a.out.write_text(json.dumps(res, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
