#!/usr/bin/env python3
"""s5p (amendment 6, F1): the power alternatives' shape ratios rebuilt from the repaired 5D predictions.

P1 (W3, NuWro / GENIE CV in (pT, p_parallel, E_avail)) and P3 (W2, GENIE MEC / GENIE CV in (E_avail, W)) were
built by ``s5e_deform.py build`` from the committed 3D and (E_avail, W) ROOT predictions, which carry the
flux defect of ``KNOWN_ISSUES.md`` 83. This forms the same marginal from two 5D prediction npz files (the
kept axes' cell integrals: sum over the other axes of density x 5D volume), and applies
``s5e_deform.ratio_from_contents`` unchanged (densities on the kept axes, their volumes), writing the same
schema ``s5e-shape-ratio/1`` that ``s5e_deform.ratio_weight`` reads. With ``--compare`` it reports the change
against an existing ratio file of the same kind: the median over informative cells of |rho_new - rho_old| /
|rho_old - 1| (the change relative to the departure) and the correlation of (rho - 1).

MEASURES: a shape ratio between two fixed predictions. CANNOT AUTHORIZE: any statement about which generator
describes nature.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

import s5e_deform as sd

AXES = ("pt", "pz", "eavail", "q3", "W")


def marginal(path: Path, keep: tuple) -> tuple[np.ndarray, list, np.ndarray]:
    z = np.load(path, allow_pickle=True)
    edges = [np.asarray(z[f"edges_{a}"], float) for a in AXES]
    x = np.asarray(z["xsec_flat"], float).reshape([len(e) - 1 for e in edges])
    vol5 = np.einsum("a,b,c,d,e->abcde", *[np.diff(e) for e in edges])
    drop = tuple(i for i in range(5) if i not in keep)
    integ = (x * vol5).sum(axis=drop)
    vk = np.ones(integ.shape)
    for d, ax in enumerate(keep):
        vk = vk * np.diff(edges[ax]).reshape([-1 if i == d else 1 for i in range(len(keep))])
    return integ / vk, [edges[ax] for ax in keep], vk


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--kind", choices=sorted(sd.KINDS), required=True)
    ap.add_argument("--numerator", type=Path, required=True)
    ap.add_argument("--denominator", type=Path, required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--compare", type=Path, default=None)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        raise SystemExit(f"refusing to overwrite {a.out}")
    hname, axes = sd.KINDS[a.kind]
    cn, en, vol = marginal(a.numerator, axes)
    cd, ed, _ = marginal(a.denominator, axes)
    for x, y in zip(en, ed):
        if not np.allclose(x, y):
            raise SystemExit("the two predictions are on different grids")
    rho, stats = sd.ratio_from_contents(cn, cd, vol)
    digest = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()  # noqa: E731
    out = {"schema": "s5e-shape-ratio/1", "label": a.label, "kind": a.kind, "histogram": f"5D marginal ({hname} axes)",
           "axes": list(axes), "edges": [e.tolist() for e in en],
           "definition": "shape_ratio = frac_num / frac_den per cell (C order), frac = content x cell volume normalized over cells with both predictions positive; ratio 1 where either is non-positive; clipped to [0.25, 4] (s5e_deform.ratio_from_contents on the 5D predictions' marginals)",
           "shape_ratio": rho.ravel(order="C").tolist(), "stats": stats,
           "numerator": {"path": str(a.numerator), "sha256": digest(a.numerator)},
           "denominator": {"path": str(a.denominator), "sha256": digest(a.denominator)},
           "code_sha256": {"s5p_alt_ratios.py": digest(Path(__file__).resolve()), "s5e_deform.py": digest(Path(sd.__file__).resolve())}}
    if a.compare is not None:
        old = json.loads(a.compare.read_text())
        if old.get("kind") != a.kind:
            raise SystemExit("--compare is a different kind")
        r0 = np.asarray(old["shape_ratio"], float)
        r1 = rho.ravel(order="C")
        info = np.abs(r0 - 1) > 0.01
        out["change_against"] = {"path": str(a.compare), "sha256": digest(a.compare),
                                 "median_abs_change_over_departure": float(np.median(np.abs(r1 - r0)[info] / np.abs(r0 - 1)[info])) if info.any() else None,
                                 "corr_departures": float(np.corrcoef(r0 - 1, r1 - 1)[0, 1]), "cells_informative": int(info.sum())}
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({"label": a.label, **stats, **({"change": out["change_against"]} if a.compare else {})}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
