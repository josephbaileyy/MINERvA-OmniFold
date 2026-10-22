#!/usr/bin/env python3
"""KI 98 arm (c) input: the s5c background dump with its background scaled by a constant.

Reads the dump that every s5c Tier-S experiment used (runs/p2/bkg_dump.npz, sha256 2addac8f...), checks its
digest, and writes a copy whose bkg_w (the per-row Poisson means of the drawn background) and bkg_nd (the nominal
background prediction that the purity subtraction removes) are both multiplied by --scale. bkg_reco is copied
unchanged, and so is the meta, with the scaling recorded beside it; meta.npz_sha256 is kept so s5c_pseudo.py's
refusal (a dump made against a different npz) still applies. No s5c code changes.

Also reports, without acting on it, how closely bkg_nd matches the histogram of bkg_reco weighted by bkg_w on
project_cov_nd's edges (informative only: the scaling multiplies both by the same constant whatever their relation).
    mk_bkg_scaled.py --bkg <dump> --expect-sha256 <hex> --scale 0.9 --out <new dump>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

import project_cov_nd as pc

AXES = ["pt", "pz", "eavail", "q3", "W"]


def sha256(p) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--bkg", type=Path, required=True)
    ap.add_argument("--expect-sha256", required=True)
    ap.add_argument("--scale", type=float, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    got = sha256(a.bkg)
    if got != a.expect_sha256:
        print(f"refusing: {a.bkg} sha256 {got} != {a.expect_sha256}", file=sys.stderr)
        return 4
    if a.out.exists():
        print(f"refusing to overwrite {a.out}", file=sys.stderr)
        return 3
    z = np.load(a.bkg, allow_pickle=True)
    if sorted(z.files) != ["bkg_nd", "bkg_reco", "bkg_w", "meta"]:
        print(f"refusing: unexpected keys {sorted(z.files)}", file=sys.stderr)
        return 4
    reco, w, nd = z["bkg_reco"], z["bkg_w"], z["bkg_nd"]
    meta = json.loads(str(z["meta"]))
    hist, _ = np.histogramdd(reco.astype(float), bins=[pc.AXIS_EDGES[ax] for ax in AXES], weights=w)
    info = {"bkg_nd_vs_hist_max_abs_diff": float(np.max(np.abs(hist - nd))),
            "bkg_nd_total": float(nd.sum()), "bkg_w_total": float(w.sum())}
    meta_out = dict(meta)
    meta_out["ki98_scaled"] = {"from": str(a.bkg), "from_sha256": got, "scale": a.scale,
                               "scaled_keys": ["bkg_w", "bkg_nd"], "unchanged_keys": ["bkg_reco", "meta (plus this field)"],
                               "check": info}
    a.out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(a.out, bkg_reco=reco, bkg_w=w * a.scale, bkg_nd=nd * a.scale, meta=json.dumps(meta_out))
    rep = {"out": str(a.out), "sha256": sha256(a.out), "scale": a.scale, "from_sha256": got, **info,
           "scaled_bkg_w_total": float((w * a.scale).sum()), "scaled_bkg_nd_total": float((nd * a.scale).sum())}
    Path(str(a.out) + ".receipt.json").write_text(json.dumps(rep, indent=1) + "\n")
    print(json.dumps(rep, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
