"""Write deterministic synthetic ``mc_signal_reco``-shaped TTrees for the loader benchmarks.

Nothing here is trained or fitted. The trees carry the seven branches that
``collect_signal_arrays_2d`` reads, with the production names and types
(``double`` kinematics and weights, ``UChar_t`` ``sim_pass``), plus an optional
block of ``K`` extra ``double`` branches that stands in for the per-universe
weight columns of ``runEventLoopOmniFold_MEFHC_universes_full.root``.

About 1 % of rows are adversarial: non-finite values, weights at and beyond the
``[0, 1e4)`` window, kinematics exactly on the analysis-rectangle edges, rows
within a few ulps of the 20-degree muon-angle cut, and ``sim_pass`` values of 0,
1 and 2 (the driver tests ``!= 0``).

Usage::

    python3.13 make_synthetic_trees.py OUTDIR --rows N --extra K [--seed S]
"""

import argparse
import json
import math
import os
import sys

import numpy as np
import ROOT

PT_LO, PT_HI, PZ_LO, PZ_HI = 0.0, 4.5, 1.5, 60.0
THETA = math.radians(20.0)


def adversarial_rows(rng, n):
    """Return ``n`` rows that sit on every boundary the loader tests."""
    tan = math.tan(THETA)
    pz = rng.uniform(PZ_LO, 20.0, n)
    pt_edge = pz * tan
    k = np.arange(n) % 9 - 4                      # -4 .. +4 ulps around the cut
    pt = pt_edge + k * np.spacing(pt_edge)
    rows = {
        "MC": pt, "MC_pz": pz.copy(),
        "sim": rng.uniform(PT_LO, PT_HI, n), "sim_pz": rng.uniform(PZ_LO, PZ_HI, n),
        "sim_pass": (np.arange(n) % 3).astype(np.uint8),
        "w_truth": rng.uniform(0.5, 1.5, n), "w_reco": rng.uniform(0.5, 1.5, n),
    }
    special = [np.nan, np.inf, -np.inf, -0.0, 0.0, 1e4, np.nextafter(1e4, 0), -1e-300,
               PT_LO, PT_HI, PZ_LO, PZ_HI, np.nextafter(PT_HI, 10), np.nextafter(PZ_LO, 0)]
    for j, name in enumerate(("MC", "MC_pz", "sim", "sim_pz", "w_truth", "w_reco")):
        idx = np.arange(j, n, 7)
        rows[name][idx] = np.resize(np.array(special), idx.size)
    return rows


def bulk_rows(rng, n):
    pz = rng.gamma(3.0, 2.0, n) + 1.0
    pt = rng.exponential(0.45, n)
    smear = 1.0 + 0.05 * rng.standard_normal(n)
    passed = (rng.uniform(size=n) < 0.62).astype(np.uint8)   # ~ 20.4 M / 32.8 M pass_reco
    sim = np.where(passed == 1, pt * smear, -9999.0)
    sim_pz = np.where(passed == 1, pz * smear, -9999.0)
    return {"MC": pt, "MC_pz": pz, "sim": sim, "sim_pz": sim_pz, "sim_pass": passed,
            "w_truth": rng.lognormal(0.0, 0.3, n), "w_reco": rng.lognormal(0.0, 0.3, n)}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("outdir")
    ap.add_argument("--rows", type=int, required=True)
    ap.add_argument("--extra", type=int, default=0)
    ap.add_argument("--seed", type=int, default=20261009)
    args = ap.parse_args(argv)

    rng = np.random.default_rng(args.seed)
    n_adv = max(200, args.rows // 100)
    adv, bulk = adversarial_rows(rng, n_adv), bulk_rows(rng, args.rows - n_adv)
    cols = {k: np.concatenate([bulk[k], adv[k]]) for k in bulk}
    perm = rng.permutation(args.rows)
    cols = {k: np.ascontiguousarray(v[perm]) for k, v in cols.items()}
    # With K >= 8 the first eight extra columns use the driver's universe naming,
    # so a vertical universe (Flux:0, weights only) and a lateral one (GEANT:0,
    # weights plus shifted kinematics that keep the adversarial values) can be
    # exercised; the rest are universe-like weight columns near 1.
    named = []
    if args.extra >= 8:
        for band in ("Flux_0", "GEANT_0"):
            cols[f"w_truth_{band}"] = cols["w_truth"] * (1.0 + 0.05 * rng.standard_normal(args.rows))
            cols[f"w_reco_{band}"] = cols["w_reco"] * (1.0 + 0.05 * rng.standard_normal(args.rows))
            named += [f"w_truth_{band}", f"w_reco_{band}"]
        for src in ("MC", "MC_pz", "sim", "sim_pz"):
            cols[f"{src}_GEANT_0"] = cols[src] * (1.0 + 0.01 * rng.standard_normal(args.rows))
            named.append(f"{src}_GEANT_0")
    for u in range(args.extra - len(named)):
        cols[f"w_univ_{u:03d}"] = 1.0 + 0.05 * rng.standard_normal(args.rows)

    os.makedirs(args.outdir, exist_ok=True)
    path = os.path.join(args.outdir, f"synth_rows{args.rows}_extra{args.extra}.root")
    # FromNumpy has no uint8 column type, so sim_pass travels as int32 and is
    # narrowed to the production UChar_t before the snapshot.
    names = list(cols)
    cols["sim_pass_i32"] = cols.pop("sim_pass").astype(np.int32)
    df = ROOT.RDF.FromNumpy(cols).Define("sim_pass", "(UChar_t)sim_pass_i32")
    df.Snapshot("mc_signal_reco", path, names)
    f = ROOT.TFile.Open(path)
    meta = {"path": path, "rows": args.rows, "extra_branches": args.extra,
            "adversarial_rows": n_adv, "seed": args.seed, "bytes": os.path.getsize(path),
            "compression_settings": f.GetCompressionSettings(), "root": ROOT.gROOT.GetVersion()}
    f.Close()
    json.dump(meta, sys.stdout)
    print()


if __name__ == "__main__":
    main()
