#!/usr/bin/env python3
"""Dump the reco-level background MC behind an npz's purity weights, for s5c pseudo-experiments.

Pilot P2 of ``docs/orchestration/state/s5c/pilot-contract.json``. Reads the omnifile's
``mc_background`` and ``data`` trees with the driver's own collectors
(``unfold_nd_omnifold_unbinned.collect_bkg_nd`` / ``collect_data_nd``), rebuilds the purity weights
with ``build_measured_training_nd`` and REFUSES to write unless they reproduce the npz's
``measured_weights`` and its measured coordinates exactly -- which is what makes the dumped background
the background those weights were built from.

MEASURES: the background events' reco coordinates and POT-scaled CV weights, and the binned
background prediction. CANNOT AUTHORIZE: any uncertainty, grade or adoption.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
for p in (str(_ND.parent / "2d-unfolding"), str(_ND)):
    if p not in sys.path:
        sys.path.insert(0, p)
import ROOT  # noqa: E402
import unfold_2d_omnifold_unbinned as u2d  # noqa: E402
import unfold_nd_omnifold_unbinned as und  # noqa: E402


def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 24), b""):
            h.update(block)
    return h.hexdigest()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--omnifile", type=Path, required=True)
    ap.add_argument("--npz", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        print(f"refusing to overwrite {a.out}", file=sys.stderr)
        return 3
    t0 = time.time()
    d = np.load(a.npz, allow_pickle=True)
    names = [str(x) for x in d["axes"]]
    edges = [np.asarray(d[f"edges_{i}"], float) for i in range(int(d["nedges"]))]
    extras = [dict(und.EXTRA_AXES[n], name=n) for n in names]
    pt_lo, pt_hi, pz_lo, pz_hi = edges[0][0], edges[0][-1], edges[1][0], edges[1][-1]

    f = ROOT.TFile.Open(str(a.omnifile), "READ")
    data_pot, mc_pot, pot_scale = u2d.get_pot_scales(f)
    meas_pt, meas_pz, meas_ex = und.collect_data_nd(f.Get("data"), extras, pt_lo, pt_hi, pz_lo, pz_hi)
    bkg_pt, bkg_pz, bkg_ex, bkg_w = und.collect_bkg_nd(f.Get("mc_background"), extras, pot_scale,
                                                        pt_lo, pt_hi, pz_lo, pz_hi)
    meas_cols = [meas_pt, meas_pz] + list(meas_ex)
    bkg_cols = [bkg_pt, bkg_pz] + list(bkg_ex)
    data_nd, _ = und.histnd(meas_cols, np.ones(meas_pt.size), edges)
    bkg_nd, _ = und.histnd(bkg_cols, bkg_w, edges)
    meas_w = und.build_measured_training_nd(meas_cols, data_nd, bkg_nd, edges)

    measured = np.column_stack(meas_cols).astype(np.float32)
    coords_equal = measured.shape == d["measured"].shape and bool(np.array_equal(measured, d["measured"]))
    weight_maxdiff = float(np.max(np.abs(meas_w - d["measured_weights"]))) if coords_equal else None
    import s5c_pseudo  # the pseudo-experiments' vectorized purity must equal the production loop

    vec = s5c_pseudo.purity_weights(measured.astype(float), np.ones(measured.shape[0]), bkg_nd, edges)
    vec_maxdiff = float(np.max(np.abs(vec - d["measured_weights"])))
    check = {
        "vectorized_purity_max_abs_diff": vec_maxdiff,
        "measured_coordinates_identical": coords_equal,
        "measured_weights_max_abs_diff": weight_maxdiff,
        "n_data": int(meas_pt.size),
        "n_bkg": int(bkg_pt.size),
        "sum_bkg_w": float(np.sum(bkg_w)),
        "data_pot": data_pot,
        "mc_pot": mc_pot,
    }
    print(json.dumps(check))
    if not coords_equal or weight_maxdiff != 0.0 or vec_maxdiff > 1e-12:
        print("refusing: the omnifile does not reproduce the npz's measured events and weights", file=sys.stderr)
        return 5
    meta = {
        "schema": "s5c-bkg-dump/1",
        "omnifile": str(a.omnifile),
        "omnifile_sha256": sha256_path(a.omnifile),
        "npz": str(a.npz),
        "npz_sha256": sha256_path(a.npz),
        "axes": names,
        "code_sha256": {"s5c_dump_bkg.py": sha256_path(Path(__file__).resolve())},
        "check": check,
        "seconds": round(time.time() - t0, 1),
    }
    tmp = a.out.with_name(a.out.name + ".partial.npz")
    np.savez_compressed(tmp, bkg_reco=np.column_stack(bkg_cols).astype(np.float32),
                        bkg_w=np.asarray(bkg_w, float), bkg_nd=bkg_nd, meta=json.dumps(meta))
    tmp.replace(a.out)
    print(json.dumps({k: meta[k] for k in ("omnifile_sha256", "npz_sha256", "seconds")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
