#!/usr/bin/env python3
"""Build ``references.npz``, the two hXSec2D vectors EVW2D's exactness controls compare against (EVW2D-DECLARATION.md
§4). Run once, locally, by the lane; the output is committed and pinned by digest in ``config.json``.

  er     E_R's hXSec2D on our edges, from E_R's central product ``xsec.root`` (sha256 a5c13fc3...). That file is not in
         the repository: it lives on pscratch (``2d-closeout-re2-20261023/partb/out/ER/xsec.root``) and in a local
         fetched copy, whose digest this script checks before reading it.
  paper  Tier 1's E_R rerun on the paper's pT edges, ``ibu-chi2-20261123/tier1/units/e/er.root`` (committed,
         sha256 5171c7b8...).

Each vector is the 14 x 16 cell contents in (pT bin) x 16 + (p|| bin) order, with the histogram's own axis edges.

    python3 -I make_references.py ER_XSEC_ROOT OUT_NPZ
"""
from __future__ import annotations

import hashlib
import io
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
ER_SHA256 = "a5c13fc38d64242bc9ee459fac87568a2f97fddf7a3ac97cc6f91eb4c2a31cef"
PAPER_REL = "docs/orchestration/state/ibu-chi2-20261123/tier1/units/e/er.root"
PAPER_SHA256 = "5171c7b8ecacda6090e242349dd622218c1c38885c60ef8b91027033a8c4b780"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


OUR_PT = [0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55, 0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50]  # re2_driver.py:44
PAPER_PT = [0, 0.075, 0.15, 0.25, 0.325, 0.40, 0.475, 0.55, 0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50]
PZ = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0, 40.0, 60.0]  # re2_driver.py:47


def require_axes(name: str, pt: np.ndarray, pz: np.ndarray, want_pt) -> None:
    if not (np.array_equal(pt, np.asarray(want_pt, np.float64)) and np.array_equal(pz, np.asarray(PZ, np.float64))):
        raise SystemExit(f"refusing: {name}'s axes {pt.tolist()} x {pz.tolist()} are not the expected grid")


NERSC = ("/pscratch", "/global")  # a plain read there would move a purge clock


def hxsec(path: Path, digest: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """hXSec2D of a verified local file: the bytes hashed are the bytes read."""
    if str(path.resolve()).startswith(NERSC):
        raise SystemExit(f"refusing: {path} is on NERSC storage; build from a verified local copy")
    data = path.read_bytes()
    got = hashlib.sha256(data).hexdigest()
    if got != digest:
        raise SystemExit(f"refusing: {path} has sha256 {got}, not {digest}")
    import uproot
    h = uproot.open(io.BytesIO(data))["hXSec2D"]
    v = np.asarray(h.values(flow=False), np.float64)
    if v.shape != (14, 16):
        raise SystemExit(f"refusing: {path} hXSec2D has shape {v.shape}")
    return v.reshape(-1), np.asarray(h.axis(0).edges(), np.float64), np.asarray(h.axis(1).edges(), np.float64)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    er_path, out = Path(argv[0]), Path(argv[1])
    paper_path = REPO / PAPER_REL
    for p in (er_path, paper_path):
        if str(p.resolve()).startswith(NERSC):
            print(f"refusing: {p} is on NERSC storage; build from a verified local copy", file=sys.stderr)
            return 2
    er, er_pt, er_pz = hxsec(er_path, ER_SHA256)
    pa, pa_pt, pa_pz = hxsec(paper_path, PAPER_SHA256)
    require_axes("E_R", er_pt, er_pz, OUR_PT)
    require_axes("Tier 1 E", pa_pt, pa_pz, PAPER_PT)
    meta = {"schema": "evw2d-references/1",
            "er": {"source": "/pscratch/sd/j/josephrb/2d-closeout-re2-20261023/partb/out/ER/xsec.root",
                   "read_from": str(er_path), "sha256": ER_SHA256, "histogram": "hXSec2D"},
            "paper": {"source": PAPER_REL, "sha256": PAPER_SHA256, "histogram": "hXSec2D"},
            "order": "(pT bin) x 16 + (p|| bin), cells without under- or overflow"}
    if out.exists():
        print(f"refusing: {out} exists", file=sys.stderr)
        return 2
    np.savez(out, er=er, er_pt_edges=er_pt, er_pz_edges=er_pz, paper=pa, paper_pt_edges=pa_pt,
             paper_pz_edges=pa_pz, meta=np.array(json.dumps(meta, sort_keys=True)))
    print(json.dumps({"out": str(out), "sha256": sha256(out)}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
