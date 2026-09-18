#!/usr/bin/env python3
"""Locate the FIRST divergence between two repeated production CV executions.

Joseph, 2026-09-18: *"Make the next diagnostic production-faithful rather than merely larger: use
the actual relevant inputs, weights, estimator settings, and CV execution path, with checkpoints
sufficient to identify the first divergence between repeated executions. Choose the smallest
bounded test that can answer that question."*

THE QUESTION. `unified_throw_cov.py:1010-1018` runs the CV unfold a second time under `--null` and
reports `||CV2 - CV||`. On the preserved products that norm is `r_null = 4.4520002137582904e-14`,
relative, and P0 established the pair is like-for-like: `:840` and `:1011` pass **the same**
`args.estimator_seed`, the same `d`, `edges`, `w_truth`, `w_reco`, `td_cv` and `args.iters`. So two
identical calls disagree. **This probe asks WHERE.**

WHY THIS IS THE SMALLEST TEST THAT CAN ANSWER IT. The endpoint norm cannot say which stage diverged
-- a norm over the final cross-section is one number after five OmniFold iterations and ten
classifier fits. The OmniFold loop's only outputs are `w_pull, w_push` at the end
(`omnifold_nn_core.py:275`), so an endpoint comparison is all the production path offers. The
cheapest way to get stage resolution is to digest **every classifier evaluation** as it happens, in
both executions, and report the first index where the sequences differ.

NOTHING IN THE PRODUCTION PATH IS MODIFIED. `omnifold_nn_core._reweight` is a module-level function
called by the loop's inner `fit_reweight` closure, so it can be wrapped from here. The wrapper
**calls through and returns the original value** -- it is capture-only, so it cannot change what it
measures. This is the same discipline as `thread_environment_snapshot()`: capturing cannot alter a
result and setting can, so this captures.

PRODUCTION-FAITHFUL, ITEM BY ITEM:
  inputs             the real bank `cv.npz`, digest-bound to the precursor receipt's
                     `bank_cv_sha256` and verified before use (refusal, not a warning)
  weights            `w_truth`, `w_reco`, `td_w` straight out of that bank
  estimator settings whatever `make_estimators` constructs -- UNPINNED, as production is. No
                     overlay is applied; that would test a different estimator
  CV execution path  the kernel `unified_throw_cov.py:840` and `:1011` resolve AT RUNTIME, which
                     for a 5D bank is `unified_throw_cov_5d._xsec_for_weights_5d` -- installed by
                     importing the wrapper, then resolved through `base`'s globals. The call SITE
                     lines are in the base module; the FUNCTION they resolve to is not the one
                     bound to that name in the base module, and an assertion checks the patch
                     landed before anything is computed
  iterations         `--iters`, defaulting to 5, the production value

WHAT THIS PROBE OBSERVES, AND WHAT IT DOES NOT ESTABLISH.
⚠ REWRITTEN 2026-09-18. An earlier version of this section attached a CAUSE to each branch. All
three attributions were unsupported and are withdrawn; what follows is what the checkpoints can
actually carry. The probe reports TWO INDEPENDENT OBSERVABLES and no mechanism:

  (A) the first checkpoint index at which the two executions differ, if any;
  (B) whether the endpoints agree, reported SEPARATELY from (A).

  * FIRST DIVERGENCE AT THE FIRST CLASSIFIER EVALUATION establishes that these two executions
    disagreed, at that checkpoint, in this run. It does NOT establish threading as the cause.
    Thread scheduling, memory layout, library dispatch, an uninitialised read, or any other
    nondeterminism inside the fit are all consistent with it, and this probe separates none of
    them. Nor does a contrast with the synthetic fixture (58509947) isolate a cause: the two
    settings differ in data, size, feature count AND shape at once.
  * FIRST DIVERGENCE LATER, after N identical checkpoints, does NOT prove the estimator is
    reproducible and does NOT exclude pinning as a remedy. The later fits DO NOT HAVE THE SAME
    INPUTS: iteration `it`s step-1 training weights carry `w_push` from iteration `it-1`
    (`omnifold_nn_core.py:253-256`), so the first differing classifier output may reflect that
    fit, or an earlier operation this probe does not observe -- the regressor branch, which does
    not pass through `_reweight`, or the weight product `w_pull = w_push * new_w`. "First OBSERVED
    divergence" is a statement about the checkpoint set, not about the first arithmetic difference.
  * NO DIVERGENCE AT ALL means THE DISCREPANCY WAS NOT REPRODUCED in this pair. It does NOT prove
    the historical `r_null` arose outside this path, and it does NOT justify a documentation-only
    repair. A nondeterminism that appears in some executions and not others is fully consistent
    with both, and one pair cannot distinguish "does not happen here" from "did not happen this
    time".

  All three are decision-relevant for NARROWING candidate mechanisms. None of them licenses
  adoption, and none of them selects a remedy on its own. Causal explanations stay provisional.

⚠ WHAT THIS DOES NOT DO. It does not adopt anything, does not grade the pilot, does not compute a
significance, and does not establish cross-node behaviour. It reports where two executions on one
node first differ, and the magnitude at that point.
"""
import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

# The bank `cv.npz` digest recorded in `z_precursor_20260914/unified_throw_cov_5d.receipt.json`
# under `extra.bank_cv_sha256`. Verified before use, because an unverified input makes the whole
# comparison a statement about an unknown object.
EXPECTED_BANK_CV_SHA256 = "3c9bbd6283fcb157f3bc110a790ab45e9c499cb8c457dfcb9ad0193d951692bd"


def _sha256_file(path, chunk=1 << 22):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(chunk), b""):
            h.update(blk)
    return h.hexdigest()


def _digest(a):
    return hashlib.sha256(np.ascontiguousarray(np.asarray(a, np.float64)).tobytes()).hexdigest()


class Tap:
    """Capture-only wrapper around `omnifold_nn_core._reweight`.

    Records a digest and a scalar summary of every classifier evaluation, in call order, and
    returns the original array untouched. Call order is deterministic in the loop's structure:
    within iteration `it`, call `2*it` is step 1 (`clf1` on `MCreco[pass_reco]`) and call `2*it+1`
    is step 2 (`clf2` on `MCgen`) -- see `omnifold_nn_core.py:248-269`. The regressor branch does
    not pass through `_reweight`, so it is covered only indirectly; that limit is recorded.
    """

    def __init__(self, core):
        self.core = core
        self.original = core._reweight
        self.records = []

    def __enter__(self):
        tap = self

        def wrapped(events, clf):
            out = tap.original(events, clf)
            a = np.asarray(out, float)
            tap.records.append({
                "call": len(tap.records),
                "digest": _digest(a),
                "n": int(a.size),
                "sum": float(a.sum()),
                "min": float(a.min()) if a.size else None,
                "max": float(a.max()) if a.size else None,
            })
            return out

        self.core._reweight = wrapped
        return self

    def __exit__(self, *exc):
        self.core._reweight = self.original
        return False


def _stage_label(call_index):
    return {"iteration": call_index // 2, "step": 1 + (call_index % 2)}


def first_divergence(rec_a, rec_b):
    """`(index, detail)` of the first differing evaluation, or `(None, ...)` if all agree."""
    n = min(len(rec_a), len(rec_b))
    for i in range(n):
        if rec_a[i]["digest"] != rec_b[i]["digest"]:
            a, b = rec_a[i], rec_b[i]
            rel = (abs(a["sum"] - b["sum"]) / abs(a["sum"])) if a["sum"] else float("nan")
            return i, {
                "call": i, **_stage_label(i),
                "n_elements": a["n"],
                "sum_a": a["sum"], "sum_b": b["sum"],
                "relative_sum_difference": rel,
                "identical_evaluations_before": i,
            }
    if len(rec_a) != len(rec_b):
        return n, {"call": n, **_stage_label(n),
                   "note": "the two executions made DIFFERENT NUMBERS of evaluations",
                   "n_calls_a": len(rec_a), "n_calls_b": len(rec_b)}
    return None, {"identical_evaluations": n}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bank", required=True, help="the bank DIRECTORY holding cv.npz")
    ap.add_argument("--iters", type=int, default=5, help="production value is 5")
    ap.add_argument("--estimator-seed", type=int, required=True,
                    help="the SAME seed for both executions, as unified_throw_cov.py does")
    ap.add_argument("--out", required=True)
    ap.add_argument("--allow-unverified-bank", action="store_true",
                    help="for tests only; the record says the input was unverified")
    a = ap.parse_args()

    cv_path = os.path.join(a.bank, "cv.npz")
    if not os.path.exists(cv_path):
        raise SystemExit(f"[FAIL] no cv.npz in {a.bank}. `--bank` is a DIRECTORY, not a file.")
    measured = _sha256_file(cv_path)
    if measured != EXPECTED_BANK_CV_SHA256 and not a.allow_unverified_bank:
        raise SystemExit(
            f"[FAIL] {cv_path} sha256 {measured} != the precursor receipt's bank_cv_sha256 "
            f"{EXPECTED_BANK_CV_SHA256}. A comparison on an unverified input is a statement about "
            f"an unknown object, so this refuses rather than proceeding.")

    # THE 5D CV KERNEL IS INSTALLED BY A MONKEYPATCH, AND A `from`-IMPORT MISSES IT.
    # `unified_throw_cov_5d.py:88` does `base._xsec_for_weights = _xsec_for_weights_5d`, with the
    # comment that "do_throws/blockunits/combine all resolve _xsec_for_weights from base's
    # globals". The base kernel in `compare_unified_throw` stops at `td_q3` and has no `td_W`, so
    # on a 5-edge bank it feeds 4 denominator coordinates to a 5-edge `histogramdd`.
    #
    # ⚠ THAT IS EXACTLY HOW JOB 58510551 FAILED, and the wrapper module's own docstring predicts
    # it verbatim: "for len(edges)==5 it would feed 4 denom coords to a 5-edge histogramdd". I had
    # taken `from compare_unified_throw import _xsec_for_weights`, which binds the UNPATCHED name
    # -- a separate binding the patch never reaches. The inverse of the usual defect, where a
    # `from`-import makes a patch decorative; here the `from`-import made the patch invisible.
    #
    # So: import the 5D wrapper FIRST, so the patch is installed, then resolve the kernel through
    # `base`'s globals at call time, which is what production does.
    import unified_throw_cov_5d as u5           # installs base._xsec_for_weights
    import unified_throw_cov as U
    import omnifold_nn_core as core
    if U._xsec_for_weights is not u5._xsec_for_weights_5d:
        raise SystemExit(
            "[FAIL] the 5D kernel is not installed: unified_throw_cov._xsec_for_weights is not "
            "unified_throw_cov_5d._xsec_for_weights_5d. Importing the wrapper is what installs "
            "it, and without it a 5-edge bank feeds 4 denominator coordinates to histogramdd.")

    d, _bands, _n_flux = U._load_bank(a.bank)
    edges = d["edges"]
    w_truth, w_reco, td_cv = d["w_truth"], d["w_reco"], d["td_w"]

    runs = []
    for _ in range(2):
        with Tap(core) as tap:
            # Resolved through base's globals at CALL time, exactly as the production combine
            # does at `unified_throw_cov.py:840` and `:1011`.
            x = U._xsec_for_weights(d, edges, w_truth, w_reco, td_cv,
                                    a.iters, a.estimator_seed).ravel(order="C")
        runs.append({"x": x, "records": tap.records})

    xa, xb = runs[0]["x"], runs[1]["x"]
    rep = xa > 0
    base = xa[rep]
    num = float(np.linalg.norm(xb[rep] - base))
    den = float(np.linalg.norm(base))
    idx, detail = first_divergence(runs[0]["records"], runs[1]["records"])

    record = {
        "probe": "z_cv_divergence_probe",
        "bank": os.path.abspath(a.bank),
        "bank_cv_sha256": measured,
        "bank_cv_sha256_verified": measured == EXPECTED_BANK_CV_SHA256,
        "iters": a.iters, "estimator_seed": a.estimator_seed,
        "both_executions_used_the_same_seed": True,
        "n_evaluations_per_execution": [len(r["records"]) for r in runs],
        "endpoint": {
            "x_cv_sha256": _digest(xa), "x_cv2_sha256": _digest(xb),
            "bitwise_identical": _digest(xa) == _digest(xb),
            "n_support": int(rep.sum()), "n_total": int(xa.size),
            "null_norm": num, "cv_norm": den,
            "r_null": (num / den) if den else float("nan"),
        },
        "first_divergence_call_index": idx,
        "first_divergence": detail,
        "per_call": {
            "a": runs[0]["records"], "b": runs[1]["records"],
        },
        "call_order_basis": (
            "within iteration `it`, call 2*it is step 1 (clf1 on MCreco[pass_reco]) and call "
            "2*it+1 is step 2 (clf2 on MCgen) -- omnifold_nn_core.py:248-269"),
        "reported_separately": {
            "checkpoint_divergence": (
                "`first_divergence_call_index` / `first_divergence` -- the first checkpoint at "
                "which the two executions differ. This is a statement about the CHECKPOINT SET, "
                "not about the first arithmetic difference."),
            "endpoint_agreement": (
                "`endpoint.bitwise_identical` and `endpoint.r_null` -- whether the final "
                "cross-sections agree. Reported independently: checkpoints may differ while "
                "endpoints agree, and the two answer different questions."),
            "causal_attribution": (
                "NONE IS OFFERED. This probe does not separate thread scheduling from memory "
                "layout, library dispatch, or any other source of nondeterminism inside a fit. "
                "Any mechanism named on the basis of this record is provisional."),
        },
        "tested_scope": {
            "production_faithful": (
                "real bank cv.npz (digest-verified against the precursor receipt), real weights, "
                "the production estimator settings UNPINNED as production leaves them, and "
                "`_xsec_for_weights` -- the same function unified_throw_cov.py calls at :840 and "
                ":1011"),
            "what_is_localised": (
                "the first CLASSIFIER EVALUATION at which the two executions differ, by call "
                "index and (iteration, step). Not the first floating-point operation."),
            "not_covered": (
                "the regressor branch does not pass through `_reweight`, so a divergence "
                "originating there is seen only at the NEXT evaluation; the histogram fill is "
                "covered only by the endpoint; and cross-NODE behaviour is not measured at all. "
                "ALSO: later fits do not share inputs with earlier ones -- iteration `it`s step-1 "
                "weights carry `w_push` from `it-1` -- so a late first-divergence does not "
                "localise the ORIGIN of the difference, only the first place it became visible."),
            "one_pair_only": (
                "two executions. A nondeterminism that manifests intermittently is consistent "
                "with agreement here, so agreement means NOT REPRODUCED rather than absent."),
            "adopts_nothing": (
                "this grades nothing, adopts nothing, and computes no significance."),
        },
    }
    Path(a.out).write_text(json.dumps(record, indent=2, sort_keys=True))
    slim = {k: v for k, v in record.items() if k != "per_call"}
    print(json.dumps(slim, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
