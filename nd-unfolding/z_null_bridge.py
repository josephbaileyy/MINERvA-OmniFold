#!/usr/bin/env python3
"""Transcribe a member's OWN two internal CV executions into the versioned null-operand slab.

WHAT THIS IS FOR. `SPEC` §3.7a's null is `r_null = ‖x_cv2 − x_cv‖ / ‖x_cv‖` over **two genuine CV
executions of the SAME RUN at the SAME fixed estimator seed**. `unified_throw_cov.py`'s combine
computes both and writes them into the throw product as `hCvExecution0`, `hCvExecution1` and
`hCvSupportMask` (`:1214-1229`). `z_build` requires them as a versioned NPZ `null` source. Nothing
on `main` moved one into the other -- the pilot's bridge lives on a lane branch that was never
merged -- so this is that step, written where the campaign can use it.

WHY THE OPERANDS MAY NOT BE RE-DERIVED SEPARATELY. `SPEC` §3.6d item 5: a separately produced
denominator *"presumes the determinism the null tests."* So this module TRANSCRIBES; it never
recomputes a CV. If the throw product does not carry both executions, there is no null for that
member and this refuses rather than manufacturing one.

WHAT IT CHECKS, AND WHY EACH IS NOT DECORATION.

* **Two executions, not one.** `n_cv_executions` must be >= 2. A product written without `--null`
  carries one, and one execution cannot make a difference.
* **The predicate is RE-DERIVED, not believed.** `§3.3` condition `11b` requires an INDEPENDENT
  reconstruction of the support, so the persisted mask is recomputed here as `x_cv > 0` and
  compared elementwise with the one the producer wrote. A disagreement is a refusal, not a note --
  it would mean the reported support and the CV disagree about which bins exist.
* **The recorded counts are re-derived too.** `n_cv_bins_total`, `n_cv_support`, and
  `n_cv_genuine_zero` are checked against the arrays rather than copied.
* **Finiteness before anything else**, on the full grid, because `reconstruct_null_ratio` divides.

IT GRADES NOTHING. `r_null` is reported in the bridge record as a measurement. The grade is
`z_validator.assess_null`'s, from `z_grade`, against the declared `null_epsilon`.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np

import z_contract as contract
import z_receipt as receipt
import z_statistics as statistics

BRIDGE_SCHEMA_VERSION = 1
EXEC_KEYS = ("hCvExecution0", "hCvExecution1")
MASK_KEY = "hCvSupportMask"
DECLARED_PREDICATE = "x_cv > 0"


def read_throw_operands(throw_root: Path) -> tuple[dict, dict]:
    """The ONLY part that needs ROOT. Returns `(arrays, recorded)`; validates nothing."""
    import ROOT

    ROOT.gROOT.SetBatch(True)
    path = str(Path(throw_root).resolve())
    handle = ROOT.TFile.Open(path, "READ")
    contract.require(handle and not handle.IsZombie(), f"cannot open {path}")
    try:
        keys = {k.GetName() for k in handle.GetListOfKeys()}
        missing = [k for k in (*EXEC_KEYS, MASK_KEY) if k not in keys]
        contract.require(
            not missing,
            f"{path}: missing {missing}. A throw product written before the `11b` remedy "
            f"(commit d3b6ae2b) carries no CV executions, and they cannot be recovered without "
            f"re-running the combine -- SPEC 3.6d item 5 forbids producing them separately.")

        def scalar(name):
            obj = handle.Get(name)
            contract.require(obj is not None, f"{path}: missing scalar {name}")
            return int(obj.GetVal())

        def vector(name):
            hist = handle.Get(name)
            contract.require(hist is not None and hist.InheritsFrom("TH1"),
                             f"{path}: {name} is not a TH1")
            n = hist.GetNbinsX()
            return np.array([hist.GetBinContent(i + 1) for i in range(n)], dtype=float)

        recorded = {k: scalar(k) for k in
                    ("n_cv_executions", "n_cv_bins_total", "n_cv_support", "n_cv_genuine_zero")}
        named = handle.Get("cv_support_predicate")
        recorded["cv_support_predicate"] = None if named is None else str(named.GetTitle())
        arrays = {"x_cv": vector(EXEC_KEYS[0]), "x_cv2": vector(EXEC_KEYS[1]),
                  "producer_mask": vector(MASK_KEY)}
    finally:
        handle.Close()
    return arrays, recorded


def validate(arrays: dict, recorded: dict) -> dict:
    """Every check, over plain arrays, so it is testable without ROOT."""
    x_cv = np.asarray(arrays["x_cv"], float)
    x_cv2 = np.asarray(arrays["x_cv2"], float)
    producer_mask = np.asarray(arrays["producer_mask"], float)

    contract.require(
        int(recorded.get("n_cv_executions", 0)) >= 2,
        f"the throw product records n_cv_executions = {recorded.get('n_cv_executions')!r}. The "
        f"null is a difference between TWO genuine CV executions of one run; one is not a null.")
    contract.require(
        recorded.get("cv_support_predicate") == DECLARED_PREDICATE,
        f"the producer declares predicate {recorded.get('cv_support_predicate')!r}, not "
        f"{DECLARED_PREDICATE!r}. The mask reconstructed below is only an independent check of "
        f"the predicate the producer actually used.")
    contract.require(x_cv.shape == x_cv2.shape == producer_mask.shape,
                     f"operand shapes differ: {x_cv.shape}, {x_cv2.shape}, {producer_mask.shape}")
    contract.require(x_cv.ndim == 1 and x_cv.size > 0, "operands must be non-empty flat vectors")
    contract.require(np.all(np.isfinite(x_cv)) and np.all(np.isfinite(x_cv2)),
                     "non-finite CV execution on the full grid")

    # §3.3 condition 11b: reconstruct the support INDEPENDENTLY and compare.
    reconstructed = x_cv > 0
    from_producer = producer_mask != 0
    contract.require(
        np.array_equal(reconstructed, from_producer),
        f"the reconstructed support `x_cv > 0` ({int(reconstructed.sum())} bins) is not the mask "
        f"the producer wrote ({int(from_producer.sum())} bins). 11b exists to catch exactly this, "
        f"and a disagreement means the reported support and the CV disagree about which bins "
        f"exist -- it is not a tolerance question.")

    n_total, n_support = int(x_cv.size), int(reconstructed.sum())
    n_zero = int(np.sum(x_cv == 0.0))
    for name, measured in (("n_cv_bins_total", n_total), ("n_cv_support", n_support),
                           ("n_cv_genuine_zero", n_zero)):
        contract.require(
            int(recorded[name]) == measured,
            f"{name}: the product records {recorded[name]!r}, the arrays give {measured}. A "
            f"recorded count that the arrays do not reproduce is not provenance.")
    contract.require(n_support > 0, "the reconstructed support is empty")
    return {"x_cv": x_cv, "x_cv2": x_cv2, "mask": reconstructed,
            "n_grid": n_total, "n_support": n_support, "n_genuine_zero": n_zero}


def bridge(throw_root: Path, out_npz: Path, *, code_identity: dict) -> dict:
    arrays, recorded = read_throw_operands(throw_root)
    v = validate(arrays, recorded)
    out_npz = Path(out_npz)
    contract.require(out_npz.suffix == ".npz", "--out must be .npz")
    contract.require(not out_npz.exists(), f"--out exists: {out_npz}. Operands are written once.")
    out_npz.parent.mkdir(parents=True, exist_ok=True)

    persisted = receipt.persist_null_operands(out_npz, v["x_cv"], v["x_cv2"], v["mask"],
                                              code_identity=code_identity)
    back = receipt.load_null_operands(out_npz)
    contract.require(all(np.array_equal(a, b) for a, b in
                         zip(back, (v["x_cv"], v["x_cv2"], v["mask"]))),
                     "the persisted slab does not read back as it was written")
    measured = statistics.reconstruct_null_ratio(*back)
    return {
        "bridge_schema_version": BRIDGE_SCHEMA_VERSION,
        "bridge_status": "TRANSCRIBED",
        "declared_predicate": DECLARED_PREDICATE,
        "source": {"path": str(Path(throw_root).resolve()),
                   **receipt.stamp_file(Path(throw_root)),
                   "recorded": recorded},
        "measured_counts": {"n_grid": v["n_grid"], "n_support": v["n_support"],
                            "n_genuine_zero": v["n_genuine_zero"]},
        "persisted": persisted,
        "reconstructed_null": measured,
        "grades_nothing": ("r_null is reported here as a measurement. The grade is "
                           "z_validator.assess_null's, against the declared null_epsilon."),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--throw", required=True, help="the member's combined throw ROOT")
    ap.add_argument("--out", required=True, help="the null-operand NPZ to write (must not exist)")
    ap.add_argument("--record", required=True, help="the bridge record JSON to write")
    ap.add_argument("--revision", required=True,
                    help="the revision of the checkout running this bridge; recorded, not graded")
    args = ap.parse_args(argv)

    here = Path(__file__).resolve()
    code_identity = {
        "revision": args.revision,
        "import_closure_digests": {
            here.name: receipt.sha256_file(here),
            "z_receipt.py": receipt.sha256_file(here.with_name("z_receipt.py")),
            "z_statistics.py": receipt.sha256_file(here.with_name("z_statistics.py")),
        },
    }
    record = bridge(Path(args.throw), Path(args.out), code_identity=code_identity)
    rec = Path(args.record)
    rec.parent.mkdir(parents=True, exist_ok=True)
    receipt.atomic_write_json(rec, record)
    print(json.dumps({"out": str(Path(args.out).resolve()),
                      "record": str(rec.resolve()),
                      "r_null": record["reconstructed_null"]["r_null"],
                      "n_support": record["measured_counts"]["n_support"]}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
