#!/usr/bin/env python3
"""The MINERvA Tune v1 5D truth prediction of the analysis MC, in the gen5d npz form.

The analysis MC's truth weights already carry the full Tune v1 (``3d-unfolding/genie/README.md`` Stage B), so
its truth-level cross section is the MnvTune v1 prediction on the analysis's own signal definition. This
extracts it exactly as the unfold extracts a cross section (``xsec_nd.extract_cross_section_nd`` with the
truth histogram of the truth-passing rows at w_truth, the completeness from the npz's truth denominator, the
npz flux, POT and nucleon count), and writes ``xsec_flat`` with its finite-MC variance ``sumw2_flat`` (the
w_truth^2 sum through the same extraction) and the fine edges under the gen5d names ``edges_<axis>``.

MEASURES: the MC truth prediction and its finite-sample variance. CANNOT AUTHORIZE: any comparison.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

import s5c_unfold
from xsec_nd import extract_cross_section_nd

AXES = ("pt", "pz", "eavail", "q3", "W")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--npz", type=Path, required=True)
    ap.add_argument("--expect-npz-sha256", required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        raise SystemExit(f"refusing to overwrite {a.out}")
    sha = s5c_unfold.sha256_path(a.npz)
    if sha != a.expect_npz_sha256:
        raise SystemExit("npz digest differs")
    d = s5c_unfold.load_inputs(a.npz)
    m = np.asarray(d["pass_truth"], bool)
    edges = d["edges"]
    samp = np.column_stack([d["MCgen"][m, i] for i in range(5)]).astype(float)
    w = np.asarray(d["w_truth"], float)[m]
    unf, _ = np.histogramdd(samp, bins=edges, weights=w)
    unf2, _ = np.histogramdd(samp, bins=edges, weights=w * w)
    dn = d["denom_nd"]
    comp = np.zeros_like(unf)
    comp[dn > 0] = unf[dn > 0] / dn[dn > 0]
    args = (d["flux"], float(d["data_pot"]), float(d["n_nucleons"]), edges)
    xs, _ = extract_cross_section_nd(unf, comp, *args)
    scale = np.where(unf > 0, xs / np.where(unf > 0, unf, 1), 0.0)  # the extraction is linear in the counts per cell
    var = unf2 * scale ** 2
    meta = {"schema": "s5p-mc-truth-pred/1", "prediction": "MINERvA Tune v1 (analysis MC truth, w_truth)", "npz": str(a.npz),
            "npz_sha256": sha, "code_sha256": hashlib.sha256(Path(__file__).resolve().read_bytes()).hexdigest(),
            "definition": "extract_cross_section_nd of the truth-passing rows at w_truth with completeness truth/denominator; variance = sum w^2 through the same per-cell scale"}
    np.savez_compressed(a.out, xsec_flat=xs.ravel(order="C"), sumw2_flat=var.ravel(order="C"),
                        nevt_flat=np.histogramdd(samp, bins=edges)[0].ravel(order="C"), shape=np.array(xs.shape),
                        **{f"edges_{ax}": np.asarray(e, float) for ax, e in zip(AXES, edges)}, meta_json=json.dumps(meta))
    print(json.dumps({"out": str(a.out), "total_in_grid": float((xs * np.einsum("a,b,c,d,e->abcde", *[np.diff(e) for e in edges])).sum())}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
