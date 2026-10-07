#!/usr/bin/env python3
"""Build the lost-seed resolution's reading (b) -- the recovery-union calibration draws with the FROZEN variant
shifts -- from the two released extracts, for the W1 projected tests. Only the ``S__<null>`` arrays are taken from
the frozen extract; every other array is the union extract's. Checks that the shared inputs are identical and that
the frozen draws sit unchanged inside the union draws, matched by seed.

Usage: python3 make_reading_b.py --frozen data/frozen/inference_sufficient.npz \
           --union data/recovery-union/inference_sufficient.npz --out data/recovery-frozenS/inference_sufficient.npz
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--frozen", type=Path, required=True)
    ap.add_argument("--union", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    fz, un = np.load(a.frozen, allow_pickle=False), np.load(a.union, allow_pickle=False)
    man = json.loads(Path(str(a.union) + ".manifest.json").read_text())
    for k in ("V", "f_data", "jitters", "U", "supported_cells"):
        if not np.array_equal(un[k], fz[k]):
            raise SystemExit(f"{k} differs between the extracts")
    out = {k: un[k] for k in un.files}
    for key in man["nulls"]:
        for p in ("mu", "var", "dom") + (("d1",) if f"d1__{key}" in un.files else ()):
            if not np.array_equal(un[f"{p}__{key}"], fz[f"{p}__{key}"]):
                raise SystemExit(f"{p}__{key} differs between the extracts")
        fs = {int(s): i for i, s in enumerate(fz[f"seeds__{key}"])}
        for j, s in enumerate(un[f"seeds__{key}"]):
            if int(s) in fs and not np.array_equal(un[f"F__{key}"][j], fz[f"F__{key}"][fs[int(s)]]):
                raise SystemExit(f"{key}: frozen draw for seed {s} differs inside the union")
        if f"S__{key}" in fz.files:
            out[f"S__{key}"] = fz[f"S__{key}"]
    a.out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(a.out, **out)
    man["group"] = "recovery-union F with FROZEN S = reading (b), report-only"
    man["npz_sha256"] = hashlib.sha256(a.out.read_bytes()).hexdigest()
    Path(str(a.out) + ".manifest.json").write_text(json.dumps(man) + "\n")
    print(json.dumps({"out": str(a.out), "npz_sha256": man["npz_sha256"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
