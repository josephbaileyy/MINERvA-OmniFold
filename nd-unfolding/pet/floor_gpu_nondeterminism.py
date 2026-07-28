#!/usr/bin/env python3
"""GPU-nondeterminism floor for the recoil-only xps2 PET estimator: per-event AND per-bin.

Per-event floor answers "are the two trainings the same estimator". Per-bin floor answers
the question that actually propagates to an extraction: after summing w_truth*w_push into
the canonical extended FPS grid, does the 0.2% per-event spread stay 0.2% in every bin, or
amplify where the grid is sparse (the pT 4.5-30 and p|| 60-120 catch bins)?

NOT a covariance and NOT a publication number: recoil-only xps2 cross-check
(docs/OPEN_ITEMS.md line 30 bars promoting recoil-only covariance). This is a numerical
stability diagnostic of the training.

Run 2026-07-28 on the Delta login node, 6m14s wall, 4.13 GiB peak RSS. The weight NPZs
are Delta-local (/u/jbailey2), so --nominal/--repeat/--inputs must be supplied there;
the defaults below only resolve on a checkout that carries the products.
"""
import argparse
import hashlib
import json
import os
import zipfile

import numpy as np
import numpy.lib.format as npf

# Repo root from this file location (<repo>/nd-unfolding/pet/); MNV_REPO overrides.
_REPO = os.environ.get("MNV_REPO") or os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_PROD = os.path.join(_REPO, "nd-unfolding", "products", "pet")


def parse_args():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--nominal", default=os.path.join(
        _PROD, "pet_weights_fps_xps2_delta_s101.npz"))
    p.add_argument("--repeat", default=os.path.join(
        _PROD, "pet_weights_fps_xps2_delta_s101_rep.npz"))
    p.add_argument("--inputs", required=True,
                   help="of_inputs_pc_fps_xps2.npz (supplies truth_scalars, w_truth, edges)")
    p.add_argument("--out", default=os.path.join(
        _PROD, "pet_weights_fps_xps2_delta_s101_floor.json"))
    return p.parse_args()


_a = parse_args()
NOM, REP, INP, OUT = _a.nominal, _a.repeat, _a.inputs, _a.out


def sha(p, bs=1 << 22):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(bs), b""):
            h.update(b)
    return h.hexdigest()


def member(z, name):
    with z.open(name + ".npy") as fh:
        return npf.read_array(fh, allow_pickle=False)


zn, zr = np.load(NOM), np.load(REP)
if not np.array_equal(zn["mc_indices"], zr["mc_indices"]):
    raise SystemExit("ALIGNMENT FAIL - mc_indices differ; floor not computable")
wn = zn["w_push"].astype(np.float64)
wr = zr["w_push"].astype(np.float64)
pt_ok = np.asarray(zn["pass_truth"], dtype=bool)
del zn, zr

# ---- per-event floor -------------------------------------------------------
d = wr - wn
rel = np.abs(d / wn)
ev = {
    "std_diff": float(d.std()),
    "L1_over_sum_pct": float(np.abs(d).sum() / wn.sum() * 100.0),
    "pearson_r": float(np.corrcoef(wn, wr)[0, 1]),
    "total_ratio": float(wr.sum() / wn.sum()),
    "mean_abs_rel_pct": float(rel.mean() * 100.0),
    "median_abs_rel_pct": float(np.median(rel) * 100.0),
    "p99_abs_rel_pct": float(np.percentile(rel, 99) * 100.0),
    "max_abs_rel_pct": float(rel.max() * 100.0),
}
del d, rel

# ---- per-bin floor on the canonical extended FPS grid ----------------------
z = zipfile.ZipFile(INP)
e0 = member(z, "edges_0")          # pT  GeV, tops at 30.0
e1 = member(z, "edges_1")          # p|| GeV, spans 0-120.0
ts = member(z, "truth_scalars")    # (n,4) pt, pz, eavail, q3  [GeV]
wt = member(z, "w_truth").astype(np.float64)
z.close()

sel = pt_ok
pt = ts[:, 0].astype(np.float64)[sel]
pz = ts[:, 1].astype(np.float64)[sel]
del ts
wts = wt[sel]
del wt

# the extraction-relevant spectrum is sum(w_truth * w_push) per bin
S_nom, _, _ = np.histogram2d(pt, pz, [e0, e1], weights=wts * wn[sel])
S_rep, _, _ = np.histogram2d(pt, pz, [e0, e1], weights=wts * wr[sel])
N_bin, _, _ = np.histogram2d(pt, pz, [e0, e1])
W_bin, _, _ = np.histogram2d(pt, pz, [e0, e1], weights=wts)
del pt, pz, wts, wn, wr

occ = S_nom > 0
relbin = np.zeros_like(S_nom)
relbin[occ] = S_rep[occ] / S_nom[occ] - 1.0
arel = np.abs(relbin)

# worst bins, with their grid coordinates
order = np.argsort(arel, axis=None)[::-1][:12]
worst = []
for f in order:
    i, j = np.unravel_index(f, arel.shape)
    worst.append({
        "pt_bin": [float(e0[i]), float(e0[i + 1])],
        "ppar_bin": [float(e1[j]), float(e1[j + 1])],
        "n_events": int(N_bin[i, j]),
        "sum_w_truth": float(W_bin[i, j]),
        "S_nom": float(S_nom[i, j]),
        "rel_pct": float(relbin[i, j] * 100.0),
    })

# is the outer catch corner special?
catch = {
    "pt_top_bin_4.5_30": {
        "n_events": int(N_bin[-1, :].sum()),
        "max_abs_rel_pct": float(arel[-1, :].max() * 100.0),
    },
    "ppar_top_bin_60_120": {
        "n_events": int(N_bin[:, -1].sum()),
        "max_abs_rel_pct": float(arel[:, -1].max() * 100.0),
    },
    "outer_corner_pt4.5_30_x_ppar60_120": {
        "n_events": int(N_bin[-1, -1]),
        "rel_pct": float(relbin[-1, -1] * 100.0),
    },
}

binm = {
    "grid": {"pt_edges": [float(x) for x in e0], "ppar_edges": [float(x) for x in e1],
             "n_bins": int(S_nom.size), "n_occupied": int(occ.sum())},
    "spectrum_definition": "sum(w_truth * w_push) over pass_truth events",
    "binned_L1_over_sum_pct": float(np.abs(S_rep - S_nom).sum() / S_nom.sum() * 100.0),
    "max_abs_rel_pct": float(arel[occ].max() * 100.0),
    "p99_abs_rel_pct": float(np.percentile(arel[occ], 99) * 100.0),
    "median_abs_rel_pct": float(np.median(arel[occ]) * 100.0),
    "mean_abs_rel_pct": float(arel[occ].mean() * 100.0),
    "n_bins_over_1pct": int((arel[occ] > 0.01).sum()),
    "n_bins_over_0.5pct": int((arel[occ] > 0.005).sum()),
    "min_events_in_occupied_bin": int(N_bin[occ].min()),
    "worst_bins": worst,
    "catch_bins": catch,
}

receipt = {
    "schema": "pet-gpu-nondeterminism-floor-v1",
    "scope_and_limits": {
        "estimator": "recoil-only extended-phase-space (xps2) PET",
        "is_publication_result": False,
        "is_gate4_or_p5a": False,
        "is_covariance_component": False,
        "reason": "recoil-only xps2 cross-check; docs/OPEN_ITEMS.md bars promoting or "
                  "extending recoil-only covariance as a full-event estimator product",
        "what_this_bounds": "GPU/parallel nondeterminism PLUS node-to-node variation "
                            "(nominal gpua012, repeat gpua072), not kernel-level "
                            "nondeterminism alone",
    },
    "nominal": {"job": 20445933, "node": "gpua012", "elapsed": "09:32:32",
                "sha256": sha(NOM)},
    "repeat": {"job": 20488861, "node": "gpua072", "elapsed": "09:38:51",
               "sha256": sha(REP), "size_bytes": os.path.getsize(REP)},
    "recipe_matched": "np=4 niter=5 epochs=8 train=40000000 seed=101 estimator_seed=42, "
                      "same input of_inputs_pc_fps_xps2.npz",
    "n_aligned_rows": int(pt_ok.size),
    "n_pass_truth": int(pt_ok.sum()),
    "mc_indices_identical": True,
    "per_event_floor": ev,
    "per_bin_floor": binm,
    "credibility_bar_10M_vs_40M_L1_over_sum_pct": 4.4833,
    "per_event_ratio_to_bar": ev["L1_over_sum_pct"] / 4.4833,
}
with open(OUT, "w") as f:
    json.dump(receipt, f, indent=2)
print(json.dumps(receipt, indent=2))
