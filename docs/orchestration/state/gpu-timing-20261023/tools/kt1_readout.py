"""gpu-timing-20261023 readout: K-T1 (bitwise against the recorded product) and per-task timings, per arm.

Usage: python3 -I kt1_readout.py --recorded NPZ --runs DIR --out JSON
For every <runs>/<arm>/<task>/nom_b-_j-.npz: sha256; whether xsec_flat, xtrue_flat and shape equal the recorded product's
byte for byte; max |diff| and max relative |diff| of xsec_flat (non-zero recorded cells); seconds_load, seconds_unfold,
the SLURM job and step, and the code and input digests (each compared with the recorded product's)."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

NAME = "nom_b-_j-.npz"


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def load(p: Path):
    z = np.load(p, allow_pickle=False)
    return {k: z[k] for k in z.files if k != "meta"}, json.loads(str(z["meta"]))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--recorded", type=Path, required=True)
    ap.add_argument("--runs", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    ra, rm = load(a.recorded)
    res = {"schema": "gpu-timing-kt1/1", "recorded": {"path": str(a.recorded), "sha256": sha256(a.recorded),
           "seconds_unfold": rm["seconds_unfold"], "slurm_job": rm["slurm_job"]}, "arms": {}}
    nz = ra["xsec_flat"] != 0
    for arm_dir in sorted(p for p in a.runs.iterdir() if p.is_dir()):
        rows = []
        for p in sorted(arm_dir.glob(f"*/{NAME}")):
            xa, xm = load(p)
            d = np.abs(xa["xsec_flat"] - ra["xsec_flat"])
            rows.append({
                "task": p.parent.name, "sha256": sha256(p),
                "bitwise": {k: bool(xa[k].dtype == ra[k].dtype and xa[k].shape == ra[k].shape
                                    and xa[k].tobytes() == ra[k].tobytes()) for k in ("xsec_flat", "xtrue_flat", "shape")},
                "xsec_max_abs_diff": float(d.max()),
                "xsec_max_rel_diff": float((d[nz] / np.abs(ra["xsec_flat"][nz])).max()),
                "seconds_load": xm["seconds_load"], "seconds_unfold": xm["seconds_unfold"],
                "slurm_job": xm["slurm_job"], "slurm_step": xm["slurm_step"], "threads": xm["threads"],
                "code_sha256_equal": xm["code_sha256"] == rm["code_sha256"],
                "inputs_equal": (xm["input_npz_sha256"], xm["bkg_dump_sha256"]) == (rm["input_npz_sha256"], rm["bkg_dump_sha256"]),
                "experiment_equal": xm["experiment"] == rm["experiment"],
            })
        if not rows:
            continue
        su = np.array([r["seconds_unfold"] for r in rows])
        res["arms"][arm_dir.name] = {
            "n": len(rows), "all_bitwise": all(all(r["bitwise"].values()) for r in rows),
            "seconds_unfold_median_min_max": [float(np.median(su)), float(su.min()), float(su.max())], "tasks": rows}
        print(arm_dir.name, res["arms"][arm_dir.name]["n"], "bitwise", res["arms"][arm_dir.name]["all_bitwise"],
              "seconds_unfold med/min/max", res["arms"][arm_dir.name]["seconds_unfold_median_min_max"], flush=True)
    a.out.write_text(json.dumps(res, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
