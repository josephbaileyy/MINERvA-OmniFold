#!/usr/bin/env python3
"""C_stat^data predicates P1-P8, in ONE home, imported by both drivers.

WHY A SEPARATE MODULE. The training driver and the extraction driver must apply the same
predicates, and importing the training driver from the extraction driver would drag
`train_fullevent_nominal` -- and TensorFlow -- into a stage that does not need it. Two copies of one
predicate is the defect lane A filed as `OI-65` and this lane re-filed as `BEN-411`: the cheapest
defence is that there be only one. Dependencies here are numpy and the production loader, which has
no module-level TF import.

WHAT THESE REPLACE, and why the replacement is legitimate rather than a relaxation.
`fe.validate_coherent_bootstrap` (fullevent_fps_dataloader.py:750) is mandatory-key fail-closed on
`sig_bootstrap_factor` and raises at :768 unless it equals the canonical Poisson draw. A data-only
family HAS NO SIGNAL DRAW to be coherent with, so that guard checks the wrong proposition rather
than failing a true one. Lane C's rule (`BEN-407`): read the predicate before skipping an
unsatisfiable guard -- if the new product fails a TRUE claim, skipping is a relaxation and
forbidden; if the claim is INAPPLICABLE, the replacement can and must be STRONGER. P1-P8 are that
replacement, and the data-only path is verified more tightly than the three-stream path.
"""
import os
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import fullevent_fps_dataloader as fe  # noqa: E402

# ---------------------------------------------------------------------------------------------
# C_stat PRODUCTS. `data-only-v1` builds the COMPARABLE statistical covariance: the data stream
# alone is resampled, so the published sigma_stat is not ~88% MC statistics and is profileable
# against MINERvA's own, T2K, MicroBooNE and NOvA. The three-stream family is NOT superseded,
# NOT discarded and NOT re-verdicted (lane C, BEN-404).
#
# WHY THIS IS A SEPARATE NAMED PATH AND NOT A FLAG THREADED THROUGH THE OLD ONE. The data-only
# product does not read `meta["bootstrap"]` at all -- the loader publishes no such block when
# `bootstrap_seed is None` -- so the ~13 sites that read it are NOT REACHED rather than each
# branched. Thirteen `if data_only:` tests would have been their own defect (C, BEN-404 applied
# at the level of code structure). Dispatch happens ONCE, as early as possible, on the tag.
#
# THE FIFTH SITE, and it is why this path exists in this shape. `fe.validate_coherent_bootstrap`
# (fullevent_fps_dataloader.py:750) is mandatory-key fail-closed on `sig_bootstrap_factor` and
# raises at :768 unless it equals the canonical Poisson draw. A data-only family HAS NO SIGNAL
# DRAW TO BE COHERENT WITH, so that guard is checking the wrong proposition rather than failing a
# true one -- and per C's rule (BEN-407) an INAPPLICABLE claim may be replaced, by something
# STRONGER, while a FALSE one may not. P1-P8 below are that replacement. Skipping it without the
# replacement would be the forbidden relaxation.
CSTAT_THREE_STREAM = "three-stream-v1"
CSTAT_DATA_ONLY = "data-only-v1"
CSTAT_PRODUCTS = (CSTAT_THREE_STREAM, CSTAT_DATA_ONLY)

# P5b / measured-leg closure tolerance. Four float32 eps, as C specified: the claim on these
# arrays is that a SPECIFIC COMPUTATION HAPPENED (a scalar renormalization), and an arithmetic
# result carries rounding, so bit-exactness there would test the implementation path rather than
# the claim. Bit-exactness is reserved for P5a, whose claim is that NOTHING happened.
F32_EPS = float(np.finfo(np.float32).eps)
CLOSURE_TOL_EPS = 4.0


def assert_data_only_streams(store, *, data_bootstrap_seed, n_data_full, n_sig_full, n_bkg_full):
    """P1-P4 and P6 over a data-only store. Shared by the train and extract paths.

    `store` is any mapping (an npz, or a dict during the negative controls). Every predicate is a
    POSITIVE assertion: absence raises, and unity is asserted EXPLICITLY rather than inferred from
    a missing key -- `BEN-405`, whose -1 sentinel collision is unreachable here because P6 puts the
    seed under its own name.
    """
    def get(key):
        keys = set(store.files) if hasattr(store, "files") else set(store)
        if key not in keys:
            raise SystemExit(f"[gate5-dataonly] required key absent: {key}")
        return store[key]

    # P1 -- the product tag. A three-stream artifact can never satisfy this path, and the
    # converse holds because the three-stream validator rejects this value when present.
    tag = str(np.asarray(get("cstat_product")).item())
    if tag != CSTAT_DATA_ONLY:
        raise SystemExit(f"[gate5-dataonly] P1 cstat_product is {tag!r}, not {CSTAT_DATA_ONLY!r}")

    # P6 -- the seed under its OWN key. Never `bootstrap_seed`: that name means the three-stream
    # coherent seed, and reusing it would make an absent-vs-empty distinction load-bearing again.
    seed = int(np.asarray(get("data_bootstrap_seed")).item())
    if seed != int(data_bootstrap_seed):
        raise SystemExit("[gate5-dataonly] P6 data_bootstrap_seed mismatch")

    # P2 / P3 -- the MC factors are persisted, full-length, and EXPLICITLY ones.
    for pred, key, n in (("P2", "sig_bootstrap_factor_full", int(n_sig_full)),
                         ("P3", "bkg_bootstrap_factor_full", int(n_bkg_full))):
        arr = np.asarray(get(key))
        if arr.shape != (n,):
            raise SystemExit(f"[gate5-dataonly] {pred} {key} shape {arr.shape} != {(n,)}")
        if not np.array_equal(arr, np.ones(n, dtype=arr.dtype)):
            raise SystemExit(f"[gate5-dataonly] {pred} {key} is not identically one")

    # P4 -- THE COHERENCE CHECK SURVIVING, re-pointed at the stream that actually varies. Same
    # predicate the loader's :768 applies to the signal stream, applied to the data stream, and
    # derived from the PRODUCTION function rather than a local reimplementation.
    df = np.asarray(get("data_bootstrap_factor"))
    if df.shape != (int(n_data_full),):
        raise SystemExit(f"[gate5-dataonly] P4 data_bootstrap_factor shape {df.shape} "
                         f"!= {(int(n_data_full),)}")
    canonical = fe.coherent_bootstrap_factors(
        int(n_data_full), int(n_sig_full), int(n_bkg_full), int(data_bootstrap_seed))[0]
    if not np.array_equal(df, canonical):
        raise SystemExit("[gate5-dataonly] P4 data factor != canonical draw at this seed "
                         "(post-hoc redraw or wrong seed) -- fail closed")
    return True


def assert_mc_leg_unthinned(mc, *, w_truth_full, w_reco_full, imc, size):
    """P5a (bit-exact) and P5b (toleranced closure) over the MC leg.

    P5 CANNOT BE A SINGLE BIT-EXACT HASH COMPARISON, and the loader's own comment at
    fullevent_fps_dataloader.py:1344-1347 says so three lines above the call it describes: the MC
    DataLoader normalizes (`normalize=True`, `normalization_factor=1e6`), and the truth leg
    therefore lands at `1e6*sum(w_truth)/sum(w_reco)` BY CONSTRUCTION. So the identity
    `mc.weight == w_truth_full[imc]` is ruled out by the code next to it.

    Split along C's rule (`BEN-409`):
      P5a  the claim is that NOTHING happened -- no Poisson thinning -- and an absence has no
           rounding, so it takes the BIT-EXACT form. The zero PATTERN is the exact signature:
           Poisson(1) zeroes ~1/e of the rows and a positive scalar zeroes none.
      P5b  the claim is that a SPECIFIC COMPUTATION happened -- one scalar renormalization -- so it
           takes a toleranced closure, with the scalar DERIVED INDEPENDENTLY rather than read back.
           That makes P5b catch a WRONG normalization too, which a hash comparison could not.

    P5a MUST FAIL ON A FLUSH-TO-ZERO and that is correct: a subnormal weight destroyed by the
    rescale appears as a new zero and is a real defect. DO NOT "repair" P5a by excluding zero rows
    of `mc.weight` -- that exempts exactly the failure mode it exists to catch (C, BEN-409).
    """
    # (i) P5b's own precondition, asserted rather than inherited. `sumw` inside the DataLoader is
    # over the RANK-SLICED array, so under multi-rank the independently derived constant is a
    # different quantity. The launchers forbid multi-rank -- but a predicate that silently depends
    # on an external guard is `BEN-386`'s shape, so it checks its own.
    if int(size) != 1:
        raise SystemExit("[gate5-dataonly] P5b requires size == 1; the derived normalization "
                         "constant is not the loader's under multi-rank")

    imc = np.asarray(imc, dtype=np.int64)
    expect_truth = np.asarray(w_truth_full, dtype=np.float32)[imc]
    expect_reco = np.asarray(w_reco_full, dtype=np.float32)[imc]
    got_truth = np.asarray(mc.weight, dtype=np.float32)
    got_reco = np.asarray(mc.weight_reco, dtype=np.float32)

    for label, got, expect in (("w_truth", got_truth, expect_truth),
                               ("w_reco", got_reco, expect_reco)):
        if got.shape != expect.shape:
            raise SystemExit(f"[gate5-dataonly] P5a {label} shape {got.shape} != {expect.shape}")
        if not np.array_equal(got == 0, expect == 0):
            n_new = int(((got == 0) & (expect != 0)).sum())
            raise SystemExit(
                f"[gate5-dataonly] P5a {label}: {n_new} row(s) became zero. A Poisson factor was "
                f"applied to the MC leg, or a subnormal weight flushed to zero in the rescale. "
                f"Do NOT exempt zero rows to make this pass.")

    # (ii) the constant is set by the RECO leg, not the truth leg -- dataloader.py:148 selects
    # `_src = weight_reco` whenever a reco leg is supplied, per the B-4/D1 Option A decision at
    # :134-141. A truth-leg derivation would PASS ON A WRONG CONSTANT, so it has its own control.
    pr = np.asarray(mc.pass_reco).astype(bool)
    denom = float(np.sum(expect_reco[pr]))
    if not denom > 0:
        raise SystemExit("[gate5-dataonly] P5b cannot derive the normalization: empty reco leg")
    c = np.float32(fe.STEP1_MC_NORMALIZATION / denom)

    report = {}
    for label, got, expect in (("w_truth", got_truth, expect_truth),
                               ("w_reco", got_reco, expect_reco)):
        nz = expect != 0
        if not nz.any():
            raise SystemExit(f"[gate5-dataonly] P5b {label}: no nonzero reference rows")
        ratio = got[nz].astype(np.float64) / expect[nz].astype(np.float64)
        dev = float(np.max(np.abs(ratio - float(c))))
        tol = CLOSURE_TOL_EPS * F32_EPS * float(c)
        report[f"{label}_max_ratio_deviation"] = dev
        report[f"{label}_tolerance"] = tol
        if dev > tol:
            raise SystemExit(
                f"[gate5-dataonly] P5b {label}: ratio to the unthinned reference is not the single "
                f"expected scalar (max deviation {dev:.6e} > {tol:.6e}); a per-row factor was "
                f"applied, or the normalization constant is not the loader's")
    report["derived_normalization_constant"] = float(c)
    report["normalization_source_leg"] = "w_reco (dataloader.py:148 selects weight_reco)"
    report["sum_w_reco_pass_reco_unthinned"] = denom
    return report


def rescale_measured_to_data_only_R(data_loader, *, r_nominal, r_data_only):
    """Apply the data-stream fluctuation to the measured normalization, driver-side.

    WHY THIS IS NECESSARY AND NOT AN OPTIMISATION. `normalize` in the DataLoader forces
    `sum(weight[pass_reco]) == normalization_factor == 1e6 * R` whatever the pre-normalization sum
    was, so the data draw carried by the refined target is DIVIDED BACK OUT EXACTLY. R is therefore
    not one contribution among several -- it is the ONLY route by which the data-count fluctuation
    reaches the measured normalization. Freeze it and all fifty replicas share one measured
    normalization, the rate term removed by exact cancellation rather than attenuated, and the
    product becomes a SHAPE-ONLY statistical uncertainty under a name the field reads as
    total-rate (lane C, BEN-408).

    Driver-side because the loader's single `bootstrap_seed` switch controls all three streams:
    "data factor applied, signal factor not" is not reachable through it, and the loader is
    hash-pinned. Exact in real arithmetic -- normalization is purely multiplicative in
    `normalization_factor` -- so scaling by `R_data_only / R_nominal` is what passing the replica R
    would have produced, up to one extra float32 rounding. Identity to a one-shot construction is
    EXPLICITLY WAIVED: one-shot is not reachable driver-side, and identity to an unreachable
    construction is not a property of the product.
    """
    if not (r_nominal > 0 and r_data_only > 0):
        raise SystemExit("[gate5-dataonly] non-positive class ratio; refusing to rescale")
    factor = np.float32(float(r_data_only) / float(r_nominal))
    # In-place, matching dataloader.py:152-156, whose comment records that callers rely on seeing
    # the rescale through the shared view. NOTHING MAY HASH THE MEASURED WEIGHTS BEFORE THIS LINE.
    data_loader.weight *= factor
    pr = np.asarray(data_loader.pass_reco).astype(bool)
    got = float(np.sum(np.asarray(data_loader.weight, dtype=np.float64)[pr]))
    want = float(fe.STEP1_MC_NORMALIZATION * float(r_data_only))
    tol = CLOSURE_TOL_EPS * F32_EPS * abs(want)
    if abs(got - want) > tol:
        raise SystemExit(f"[gate5-dataonly] measured-leg closure failed: sum(weight[pass_reco]) "
                         f"{got!r} != 1e6*R_data_only {want!r} (tol {tol:.6e})")
    return {"rescale_factor": float(factor),
            "sum_weight_pass_reco_after": got,
            "target_1e6_times_R_data_only": want,
            "closure_abs_deviation": abs(got - want),
            "closure_tolerance": tol}


def assert_ratio_provenance_block(block):
    """P7. Both operands plus what the weights embody; absence of ANY of the three raises.

    `BEN-077`: a derived quantity ships its ingredients, so the numbers CAN contradict each other.
    A block carrying only the applied R would be unfalsifiable against the loader's stamp.
    """
    need = ("step1_class_ratio_loader_stamped", "step1_class_ratio_applied", "weights_embody")
    missing = [k for k in need if k not in block]
    if missing:
        raise SystemExit(f"[gate5-dataonly] P7 ratio provenance missing {missing}")
    if str(block["weights_embody"]) != "step1_class_ratio_applied":
        raise SystemExit("[gate5-dataonly] P7 weights_embody must name the applied ratio")
    if float(block["step1_class_ratio_applied"]) <= 0:
        raise SystemExit("[gate5-dataonly] P7 applied ratio is not positive")
    return True

# ---------------------------------------------------------------------------------------------
# L1 / L2 -- THE DEFAULT IS MADE IRRELEVANT BY CONSTRUCTION RATHER THAN FLIPPED.
#
# `--cstat-product` defaults to three-stream, which is the safe value in isolation and became the
# SILENT FAILURE the moment a run was authorized: no launcher passed the flag, so an sbatch would
# have spent 151 A100-hours rebuilding the product that already exists, with only a receipt field
# to say so. A DEFAULT'S SAFETY IS A PROPERTY OF THE CALL GRAPH, NOT OF THE VALUE (BEN-420).
#
# Lane C refused a REQUIRED flag, because that purchases edits to BOTH PINNED array launchers just
# to pass `three-stream-v1` -- the exact trade this whole route exists to avoid. Instead the
# data-only launchers write to a DISJOINT FAMILY ROOT (L1) and the drivers ASSERT TAG <=> ROOT (L2).
# L2 is what converts "a field nobody would think to read" into a check that reads it, and because
# the existing 50 artifacts occupy their root under overwrite=False, a wrong-launcher submission
# COLLIDES LOUDLY instead of quietly rebuilding.
FAMILY_ROOTS = {
    CSTAT_THREE_STREAM: "fullevent_cstat_n50",
    CSTAT_DATA_ONLY: "fullevent_cstat_data_only_n50",
}


def assert_tag_matches_root(product, *paths):
    """L2. The product tag and the family root must agree, BOTH WAYS.

    Two-way on purpose: a data-only run must not write into the three-stream root, AND a
    three-stream run must not write into the data-only root. A one-way check would leave the
    second direction to the collision guard alone, which fires only if a file is already there.
    """
    if product not in FAMILY_ROOTS:
        raise SystemExit(f"[gate5-family] unknown cstat_product {product!r}")
    want = FAMILY_ROOTS[product]
    others = {r for k, r in FAMILY_ROOTS.items() if k != product}
    for path in paths:
        if path is None:
            continue
        parts = set(str(path).split(os.sep))
        if want not in parts:
            raise SystemExit(
                f"[gate5-family] L2 product {product!r} requires the family root {want!r}; "
                f"path does not contain it: {path}")
        clash = parts & others
        if clash:
            raise SystemExit(
                f"[gate5-family] L2 path carries a FOREIGN family root {sorted(clash)} for "
                f"product {product!r}: {path}")
    return True


def assert_data_only_target_streams(store, *, data_bootstrap_seed, n_data_full, n_sig_full,
                                    n_bkg_full):
    """T1-T5 over a data-only TARGET receipt block.

    The target stage is where the product becomes honest or does not: the background fluctuation
    lives in the MEASURED TARGET, so a data-only family built on three-stream targets would carry
    the 21.7% background variance share it exists to exclude -- while its training artifact asserted
    unity. T2 is the predicate that prevents that.

    T5 requires the signal factor to be stated as unity EVEN THOUGH the refinement never consumes
    signal MC, because `build_fullevent_replica_target.py:218-220` already reads it as evidence:
    THE ARTIFACT MUST BE SELF-DESCRIBING ON ALL THREE STREAMS RATHER THAN SILENT ON ONE (lane C).
    """
    def get(key):
        keys = set(store.files) if hasattr(store, "files") else set(store)
        if key not in keys:
            raise SystemExit(f"[gate5-target-dataonly] required key absent: {key}")
        return store[key]

    tag = str(np.asarray(get("cstat_product")).item())          # T1
    if tag != CSTAT_DATA_ONLY:
        raise SystemExit(f"[gate5-target-dataonly] T1 cstat_product is {tag!r}")
    seed = int(np.asarray(get("data_bootstrap_seed")).item())   # T4
    if seed != int(data_bootstrap_seed):
        raise SystemExit("[gate5-target-dataonly] T4 data_bootstrap_seed mismatch")
    for pred, key, n in (("T2", "bkg_bootstrap_factor", int(n_bkg_full)),
                         ("T5", "sig_bootstrap_factor_full", int(n_sig_full))):
        arr = np.asarray(get(key))
        if arr.shape != (n,):
            raise SystemExit(f"[gate5-target-dataonly] {pred} {key} shape {arr.shape} != {(n,)}")
        if not np.array_equal(arr, np.ones(n, dtype=arr.dtype)):
            raise SystemExit(f"[gate5-target-dataonly] {pred} {key} is not identically one")
    df = np.asarray(get("data_bootstrap_factor"))               # T3
    if df.shape != (int(n_data_full),):
        raise SystemExit(f"[gate5-target-dataonly] T3 data factor shape {df.shape}")
    canonical = fe.coherent_bootstrap_factors(
        int(n_data_full), int(n_sig_full), int(n_bkg_full), int(data_bootstrap_seed))[0]
    if not np.array_equal(df, canonical):
        raise SystemExit("[gate5-target-dataonly] T3 data factor != canonical draw -- fail closed")
    return True


def unity_mc_factor_patch(seed, n_data, n_sig, n_bkg):
    """The data-only target's mechanism: data Poisson, MC streams UNITY.

    WHY A PATCH AND NOT A KEYWORD. The loader has ONE `bootstrap_seed` switch controlling all three
    streams, and the target stage genuinely NEEDS the data factor applied -- so
    `bootstrap_seed=None`, which works for the training stage, would remove the data variation the
    target exists to carry. "Data Poisson, background unity" is not reachable through the loader's
    interface, and the loader is hash-pinned 25 ways.

    So the driver substitutes the module-global the loader calls. This is the SAME IDIOM both
    replica drivers already use (`nominal.fe.build_fullevent_loaders`,
    `install_target_only_dataloader`), it touches no pinned file, and it makes T2/T5 true BY
    CONSTRUCTION rather than by assertion -- with T2/T5 still asserted, because a mechanism that is
    correct by construction and unchecked is one refactor from being neither.

    RESTORE IT BEFORE THE VERIFICATION BLOCK. The target driver's own replay must see the CANONICAL
    function, or T3 would compare a patched draw against itself.
    """
    canonical = fe.coherent_bootstrap_factors(int(n_data), int(n_sig), int(n_bkg), int(seed))

    def patched(nd, ns, nb, sd):
        if (int(nd), int(ns), int(nb), int(sd)) != (int(n_data), int(n_sig), int(n_bkg), int(seed)):
            raise SystemExit("[gate5-target-dataonly] loader asked for factors with unexpected "
                             "inventory sizes or seed; refusing to substitute")
        return (canonical[0],
                np.ones(int(n_sig), dtype=np.uint8),
                np.ones(int(n_bkg), dtype=np.uint8))

    return patched, canonical[0]
