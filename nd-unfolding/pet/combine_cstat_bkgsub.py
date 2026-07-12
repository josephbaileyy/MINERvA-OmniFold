#!/usr/bin/env python3
"""Phase 4: build the corrected PET C_stat from the coherent-Poisson replicas.

Strict-manifest combine of the 5D bootstrap replicas
(`bootstrap_replicas/5d/pet_bootstrap_5d_{RID}.npz`, each carrying `seed`=RID +
`xsec_flat`). Uses the shared `load_replica_manifest` (rejects missing /
duplicate / wrong-shape / non-finite / wrong-id replicas), masks on the
CORRECTED PET nominal CV>0 reported bins (same mask/order as C_ml), and centers
the covariance on the REPLICA MEAN. Compares the spread to the GPU floor.

npz-based (not combine_cov_nd, which reads a ROOT CV hist and applies the GBDT
mask); pure numpy -> runs on the login node.

  python3 pet/combine_cstat_bkgsub.py \
    --glob 'products/pet/bkgsub/bootstrap_replicas/5d/pet_bootstrap_5d_*.npz' \
    --cv products/pet/bkgsub/pet_nominal_bkgsub_5d_xsec.npz \
    --floor products/pet/bkgsub/pet_floor_bkgsub_5d_diagnostic.json \
    --expected-ids 1-6 \
    --out products/pet/bkgsub/pet_cstat_bkgsub_5d.npz
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

_ND = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding"
if _ND not in sys.path:
    sys.path.insert(0, _ND)
from replica_manifest import load_replica_manifest  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--glob", required=True)
    ap.add_argument("--cv", default="products/pet/bkgsub/pet_nominal_bkgsub_5d_xsec.npz")
    ap.add_argument("--floor", default="products/pet/bkgsub/pet_floor_bkgsub_5d_diagnostic.json")
    ap.add_argument("--expected-ids", required=True, help="inclusive LO-HI, e.g. 1-6")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    lo, hi = (int(v) for v in a.expected_ids.split("-", 1))
    if hi < lo:
        ap.error("--expected-ids must be LO-HI with HI>=LO")
    paths = sorted(glob.glob(a.glob))
    X, ids = load_replica_manifest(paths, set(range(lo, hi + 1)))   # strict

    cv = np.asarray(np.load(a.cv)["xsec_flat"], float)
    if X.shape[1] != cv.shape[0]:
        raise SystemExit(f"[FAIL] replica nbins {X.shape[1]} != cv {cv.shape[0]}")
    rep = cv > 0
    Xr = X[:, rep]; cvr = cv[rep]
    Z = Xr - Xr.mean(0)                                  # replica-mean-centered
    C = (Z.T @ Z) / (Xr.shape[0] - 1)
    sig = np.sqrt(np.clip(np.diag(C), 0, None))
    rel = sig / cvr
    sqrt_tr = float(np.sqrt(max(C.trace(), 0.0)))
    relmed = float(np.median(rel))

    floor_med = None
    if os.path.exists(a.floor):
        floor_med = json.load(open(a.floor)).get("per_bin_rel_floor", {}).get("median")

    np.savez_compressed(a.out, C_stat=C, reported_mask=rep, replica_ids=ids,
                        cv=cv, sigma=sig)
    summary = {
        "campaign": "PET bkgsub 5D corrected C_stat (Phase 4)",
        "n_replicas": int(Xr.shape[0]), "replica_ids": ids.tolist(),
        "expected_ids": f"{lo}-{hi}",
        "n_reported_bins": int(rep.sum()),
        "sqrt_trace": sqrt_tr,
        "per_bin_rel_median": relmed,
        "per_bin_rel_p90": float(np.percentile(rel, 90)),
        "per_bin_rel_max": float(rel.max()),
        "floor_per_bin_rel_median": floor_med,
        "cstat_over_floor_ratio": (relmed / floor_med) if floor_med else None,
        "out": os.path.abspath(a.out),
    }
    spath = os.path.splitext(a.out)[0] + ".summary.json"
    json.dump(summary, open(spath, "w"), indent=2)
    print(f"[cstat] {Xr.shape[0]} replicas (ids {ids.tolist()}), reported "
          f"{int(rep.sum())} bins, sqrt-trace={sqrt_tr:.3e}, per-bin rel "
          f"median={100*relmed:.3f}% p90={100*np.percentile(rel,90):.3f}%")
    if floor_med:
        print(f"[cstat] per-bin rel median {relmed:.3e} vs floor {floor_med:.3e} "
              f"(ratio {relmed/floor_med:.0f}x) -> {'PASS (spread >> floor)' if relmed>10*floor_med else 'CHECK'}")
    print(f"[cstat] wrote {a.out} + {spath}")


if __name__ == "__main__":
    main()
