#!/usr/bin/env python3
"""s5p Stage 3 (review round 1 F2/F4): the mean paired difference of two sets of unfolds on the J cells.

``--a`` and ``--b`` are globs of products carrying ``xsec_flat`` (s5p_nullexp products, paired by
``pseudo_seed``, or s5e_trace/s5p_converge traces, paired by sorted order). For each pair the J-cell integrals
(the joint test's cells, ``s5p_joint.j_matrix``) are differenced, d = f_A - f_B; the output npz holds the mean
``D_J``, its standard error ``se_J`` (None-safe for one pair) and the per-pair differences, with a JSON summary
(median |D| / f_B, median |D| / se, the pair count, every input's sha256).

Uses: F4, A = the expectation pseudo process with half the MC, B = the same with a quarter, at the same seeds:
D is the pseudo-process mean's change from a quarter to a half of the unfolding MC. F2, A = the noise-free
asimov at the fine-ratio null truth, B = at the coarse-ratio null truth (the same J integrals).

MEASURES: a paired mean difference. CANNOT AUTHORIZE: a shift coefficient or a design choice by itself.
"""
from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path

import numpy as np

import s5p_joint as sj


def key_of(path: str) -> str | int:
    z = np.load(path, allow_pickle=False)
    if "meta" in z.files:
        m = json.loads(str(z["meta"]))
        if m.get("pseudo_seed") is not None:  # traces record pseudo_seed: null and pair by order
            return int(m["pseudo_seed"])
    return path


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--a", required=True)
    ap.add_argument("--b", required=True)
    ap.add_argument("--stage1", type=Path, required=True)
    ap.add_argument("--s5c-contract", type=Path, required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--out", type=Path, required=True, help="npz; a .json summary is written beside it")
    a = ap.parse_args(argv)
    if a.out.exists():
        raise SystemExit(f"refusing to overwrite {a.out}")
    fa, fb = sorted(glob.glob(a.a)), sorted(glob.glob(a.b))
    if not fa or len(fa) != len(fb):
        raise SystemExit(f"{len(fa)} A and {len(fb)} B products")
    ka, kb = {key_of(p): p for p in fa}, {key_of(p): p for p in fb}
    if all(isinstance(k, int) for k in ka) and set(ka) == set(kb):
        pairs = [(ka[k], kb[k]) for k in sorted(ka)]
    elif not any(isinstance(k, int) for k in ka) and not any(isinstance(k, int) for k in kb):
        pairs = list(zip(fa, fb))
    else:
        raise SystemExit("A and B are not pairable (seed sets differ)")
    stage1 = json.loads(a.stage1.read_text())
    supported = json.loads(a.s5c_contract.read_text())["measurement"]["partition_J"]["supported_cells"]
    U, names, _ = sj.j_matrix(stage1, supported)
    d = np.array([U @ sj.xs(x) - U @ sj.xs(y) for x, y in pairs])
    fB = np.mean([U @ sj.xs(y) for _, y in pairs], axis=0)
    D = d.mean(0)
    se = d.std(0, ddof=1) / np.sqrt(len(pairs)) if len(pairs) > 1 else np.full(D.size, np.nan)
    np.savez(a.out, D_J=D, se_J=se, d_pairs=d, f_B_mean=fB, names=np.array(names))
    ok = fB > 0
    summary = {"schema": "s5p-pairdiff/1", "label": a.label, "n_pairs": len(pairs), "cells": len(names),
               "median_abs_D_over_fB": float(np.median(np.abs(D[ok]) / fB[ok])),
               "max_abs_D_over_fB": float(np.max(np.abs(D[ok]) / fB[ok])),
               "median_abs_D_over_se": None if len(pairs) < 2 else float(np.median(np.abs(D) / np.where(se > 0, se, np.inf))),
               "out": {"path": str(a.out.resolve()), "sha256": sj.sha256(a.out)},
               "inputs": [{"a": x, "a_sha256": sj.sha256(x), "b": y, "b_sha256": sj.sha256(y)} for x, y in pairs],
               "code_sha256": sj.sha256(Path(__file__).resolve())}
    a.out.with_suffix(".json").write_text(json.dumps(summary, indent=1) + "\n")
    print(json.dumps({k: summary[k] for k in ("label", "n_pairs", "median_abs_D_over_fB", "median_abs_D_over_se")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
