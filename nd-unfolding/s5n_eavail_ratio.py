#!/usr/bin/env python3
"""The s5n E_avail shape-departure anchor: per-bin ratio of two fixed generator E_avail shapes.

Contract control C4 (``docs/orchestration/state/s5n/contract.json``) needs a normalization-preserving
E_avail shape departure whose amplitude is anchored to traceable differences between fixed (untuned)
generator predictions. This reads the ``hXSec_eavail`` marginals that ``3d-unfolding/genie/*_to_xsec3d.py``
wrote for each generator on the analysis E_avail binning, converts each to per-bin cross-section
fractions (content x width, normalized), and writes ``shape_ratio = frac_numerator / frac_denominator``
per bin, with every input's SHA-256.

MEASURES: a shape ratio between two fixed predictions. CANNOT AUTHORIZE: any statement about which
generator describes nature; the ratio is an amplitude anchor for a known-truth departure only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


def fractions(path: Path) -> tuple[list[float], np.ndarray]:
    import ROOT

    f = ROOT.TFile.Open(str(path), "READ")
    h = f.Get("hXSec_eavail")
    if not h:
        raise SystemExit(f"{path}: no hXSec_eavail")
    n = h.GetNbinsX()
    edges = [h.GetBinLowEdge(i + 1) for i in range(n)] + [h.GetBinLowEdge(n) + h.GetBinWidth(n)]
    y = np.array([h.GetBinContent(i + 1) * h.GetBinWidth(i + 1) for i in range(n)])
    f.Close()
    if np.any(y <= 0):
        raise SystemExit(f"{path}: a non-positive E_avail bin")
    return edges, y / y.sum()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--numerator", type=Path, required=True)
    ap.add_argument("--denominator", type=Path, required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        raise SystemExit(f"refusing to overwrite {a.out}")
    en, fn = fractions(a.numerator)
    ed, fd = fractions(a.denominator)
    if not np.allclose(en, ed):
        raise SystemExit("the two predictions use different E_avail binning")
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()  # noqa: E731
    out = {
        "schema": "s5n-eavail-ratio/1",
        "label": a.label,
        "definition": "shape_ratio[k] = frac_numerator[k] / frac_denominator[k], frac = hXSec_eavail content x width, normalized over the bins",
        "eavail_edges": [float(x) for x in en],
        "shape_ratio": [float(x) for x in fn / fd],
        "frac_numerator": [float(x) for x in fn],
        "frac_denominator": [float(x) for x in fd],
        "numerator": {"path": str(a.numerator), "sha256": digest(a.numerator)},
        "denominator": {"path": str(a.denominator), "sha256": digest(a.denominator)},
        "code_sha256": digest(Path(__file__).resolve()),
    }
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({"label": a.label, "shape_ratio": [round(x, 4) for x in out["shape_ratio"]]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
