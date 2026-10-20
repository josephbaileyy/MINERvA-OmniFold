#!/usr/bin/env python3
"""MP4-A operand builder: D-ID's own T2 (and T3) nominal same-sample problem, rebuilt with D-ID's code.

Everything is imported from the frozen D-ID driver ``did.py`` (digest-checked against the value the
D-ID results record) and run through its own admission checks (A1 event digest, A2 records, A4 rows,
A7 reco cells, A8 pair rows, A9 edges, A11 reweight). Only the nominal weight set is built: it is the
only one MP4-A reads. Nothing here computes an interval.

Saved (scratch, not tracked):

* ``T2``/``T3``: the response ``R`` (reco x truth cell, CSR), the known out-of-grid reco term ``b``,
  the nominal reco data ``y``, the nominal truth ``t`` on the grid, the functional map ``H`` (185 rows,
  D-ID's ``functional_matrix``), the efficiency of each truth cell;
* ``T2`` D-ID widths recomputed by ``Diagnostic.widths`` (a machinery precheck against
  ``tables.npz``);
* ``R2X``: the descriptive refined-reco operands (every reco bin split in two at its midpoint along each
  axis), the same truth grid T2, built with D-ID's ``Pairs``/``response`` functions.

Run from the worktree root with two BLAS threads (D-ID's run record):

    OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 VECLIB_MAXIMUM_THREADS=2 python3 -I \
        measurement-paper/phase1/mp4a/build_problem.py --inputs <scratch>/inputs --out <scratch>/operands.npz
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy import sparse

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
DID_DIR = REPO / "docs/orchestration/state/next-preparation-20261009/d-id"
DID_SHA256 = "d918c816080a292eecaa0cc182a73906b868bb75189056862cf88d7152c4bbbd"  # outputs/results.json driver_sha256
CONFIG_SHA256 = "aebd8c8e378de8354e05fa905c5671506acf1428928da512e9b3d4ea1ef955ab"  # results.json config_sha256
TABLES_SHA256 = "2aab22703747bfbc33247fe015213c5d9d0a65dcfc0074f0e3c53a1de29327a4"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while block := fh.read(1 << 24):
            h.update(block)
    return h.hexdigest()


def load_did():
    path = DID_DIR / "did.py"
    if sha256(path) != DID_SHA256:
        raise RuntimeError("did.py differs from the driver D-ID's results record")
    if sha256(DID_DIR / "config.json") != CONFIG_SHA256:
        raise RuntimeError("D-ID config.json differs from the results record")
    spec = importlib.util.spec_from_file_location("did_driver", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def halved(edges) -> list:
    """Every bin split in two at its arithmetic midpoint (the descriptive refined-reco arm)."""
    e = np.asarray(edges, float)
    out = np.empty(2 * e.size - 1)
    out[0::2] = e
    out[1::2] = 0.5 * (e[:-1] + e[1:])
    return out.tolist()


def build(did, inputs: Path) -> dict:
    cfg = json.loads((DID_DIR / "config.json").read_text())
    cfg = copy.deepcopy(cfg)
    cfg["weight_sets"] = [w for w in cfg["weight_sets"] if w["name"] == "nominal"]

    class Builder(did.Diagnostic):
        def build_rows(self) -> None:
            d = self.d
            m = np.asarray(d["pass_truth"], bool)
            m_idx = np.flatnonzero(m)
            pr = np.asarray(d["pass_reco"], bool)[m]
            self.ref_edges = [halved(e) for e in self.edges]
            rf = -np.ones(m_idx.size, dtype=np.int64)
            rf[pr] = did.by_chunks(self.com.s5e_trace.flat_index, d["MCreco"], self.ref_edges, m_idx[pr])
            self.rf_ref = rf
            super().build_rows()
            if not np.array_equal(self.m_idx, m_idx) or not np.array_equal((rf >= 0), (self.rf_fine >= 0)):
                raise RuntimeError("refined reco rows differ from D-ID's reco rows")

        def histograms(self) -> None:
            keep = {k: getattr(self, k) for k in ("tf", "rf_fine", "wt", "wr", "pr", "m_idx")}
            ws = self.sets[0]
            r = self.weights(ws)
            super().histograms()
            in_t = keep["tf"] >= 0
            sig_reco = keep["pr"] & (keep["rf_fine"] >= 0)
            pair_rows = sig_reco & in_t
            bkg_rows = sig_reco & ~in_t
            wrr = keep["wr"] * r
            n_ref = int(np.prod([len(e) - 1 for e in self.ref_edges]))
            pairs = did.Pairs.build(self.rf_ref[pair_rows], keep["tf"][pair_rows], self.n_fine)
            y = np.bincount(self.rf_ref[sig_reco], weights=wrr[sig_reco], minlength=n_ref)
            b = np.bincount(self.rf_ref[bkg_rows], weights=wrr[bkg_rows], minlength=n_ref)
            cells = np.flatnonzero(y > 0)
            remap = -np.ones(n_ref, dtype=np.int64)
            remap[cells] = np.arange(cells.size)
            pairs.reco = remap[pairs.reco]
            if np.any(pairs.reco < 0):
                raise RuntimeError("a refined signal pair lies outside the occupied refined reco cells")
            self.ref = {"pairs": pairs, "P": pairs.sums(wrr[pair_rows]), "y": y[cells], "b": b[cells],
                        "cells": cells, "n_ref": n_ref}
            # the coarse (D-ID) fold must be the refined fold summed back: a consistency control
            del self.rf_ref

    budget = did.Budget(cfg["limits"]["owner_cpu_core_hours"], 0.0, cfg["limits"]["ram_bytes"])
    cmp = did.load_comparator(cfg["code"]["comparator.py"])
    com = did.load_committed(cfg["code"]["nd-unfolding"])
    run = Builder(cfg, inputs, Path("/nonexistent-not-written"), budget, cmp, com)
    run.checkpoint = lambda: None  # the builder writes no D-ID results file
    run.check_records()
    run.load_events()
    run.build_rows()
    run.histograms()
    run.grids()
    out: dict = {"admission": run.out["admission"], "events": run.out["events"], "grids": run.out["grids"]}
    arrays: dict = {"names": np.array(run.names), "f183": np.array(run.f183), "groups183": run.groups,
                    "reported183": run.reported, "reco_cells": run.reco_cells}
    for grid in ("T2", "T3"):
        pb = run.problem(grid, "nominal", "same", "nom")
        r = pb["R"].tocsr()
        arrays.update({f"{grid}/R_data": r.data, f"{grid}/R_indices": r.indices, f"{grid}/R_indptr": r.indptr,
                       f"{grid}/R_shape": np.array(r.shape), f"{grid}/y": pb["y"], f"{grid}/b": pb["b"],
                       f"{grid}/t": pb["t_bin"], f"{grid}/H": pb["maps"], f"{grid}/prior": pb["prior"],
                       f"{grid}/truth_f": pb["truth_f"],
                       f"{grid}/eff": np.asarray(r.sum(axis=0)).ravel()})
        # noise-free nominal: y must equal R t + b exactly up to rounding (D-ID's same-sample role)
        fold = r @ pb["t_bin"] + pb["b"]
        out[f"{grid}_fold_vs_y_max_rel"] = float(np.max(np.abs(fold - pb["y"]) / pb["y"]))
    w = run.widths("T2", "nominal", "nom")
    for q in ("sigma_rel", "sigma_abs", "null_fraction", "acceptance_hole"):
        arrays[f"T2/did_widths/{q}"] = np.asarray(w[q])
    out["T2_did_widths_scalars"] = {k: v for k, v in w.items() if not isinstance(v, np.ndarray)}
    # refined-reco arm (descriptive): same truth grid T2 and its nominal weighting
    g2 = run.G["T2"]
    h0 = run.h["nominal"]
    rr = did.response(g2, run.ref["pairs"], run.ref["P"], h0["u"], run.ref["cells"].size).tocsr()
    arrays.update({"R2X/R_data": rr.data, "R2X/R_indices": rr.indices, "R2X/R_indptr": rr.indptr,
                   "R2X/R_shape": np.array(rr.shape), "R2X/y": run.ref["y"], "R2X/b": run.ref["b"],
                   "R2X/cells": run.ref["cells"]})
    out["R2X"] = {"n_ref_cells_total": run.ref["n_ref"], "n_occupied": int(run.ref["cells"].size),
                  "edges": run.ref_edges,
                  "fold_vs_y_max_rel": float(np.max(np.abs(rr @ arrays["T2/t"] + run.ref["b"] - run.ref["y"])
                                                    / run.ref["y"])),
                  "y_total_vs_T2_y_total_rel": float(run.ref["y"].sum() / arrays["T2/y"].sum() - 1.0),
                  "b_total_vs_T2_b_total_rel": float(run.ref["b"].sum() / arrays["T2/b"].sum() - 1.0)
                  if arrays["T2/b"].sum() > 0 else None}
    out["resources"] = {"cpu_s": budget.used_s(), "peak_rss_bytes": budget.peak_rss_bytes(),
                        "wall_s": time.time() - budget.t0}
    return out, arrays


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--record", type=Path, required=True)
    a = ap.parse_args(argv)
    did = load_did()
    out, arrays = build(did, a.inputs)
    out["did_sha256"] = DID_SHA256
    out["builder_sha256"] = sha256(Path(__file__).resolve())
    np.savez(a.out, **arrays)
    out["operands_sha256"] = sha256(a.out)
    a.record.write_text(json.dumps(out, indent=1, sort_keys=True, default=did._jsonable) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
