#!/usr/bin/env python3
"""Read-back replacements for the pinned validator's UNEXECUTED-BY-CONSTRUCTION sites.

WHAT THIS FILE IS, AND WHAT IT IS NOT. It holds PREDICATES. It is not the data-only validator: nothing
here reads a campaign directory, iterates a family or renders a verdict, and the module that will do
those things does not exist yet -- `gen_divergence_manifest_cstat_data_only.py` refuses to run if it
does, and a control creates one to prove the refusal fires. The manifest's PREDICTIONS (bucket 3's
`got`/`want`) are frozen at the sha that committed them; what changes as predicates land here is the
REPLACEMENT BOOKKEEPING, which is a different field and is meant to track work.

    THE ORDERING ASSERTION PROTECTS THE PREDICTIONS, NOT THE BOOKKEEPING. Saying so explicitly because
    the two look alike in the same JSON, and an assertion that appears to freeze more than it does is
    worse than one that freezes less and says so.

=== THE THING THAT MAKES ALL OF THIS CHEAPER THAN THE RULING ASSUMED ===

The pinned validator IMPORTS CLEANLY and its expectations are MODULE-LEVEL constants:

    SEED_POLICY_STRING, FROZEN_POLICY, ESTIMATOR, BKG_MODE, SOURCE_SHA256, SEED_BASE, LR_POLICY

so every replacement below compares against THE SAME OBJECT the pinned check compares against, imported
rather than restated. Only `required_keys` is function-local and genuinely unavailable, which is why that
one alone is restated (and pinned to the pinned module's source by a control).

    SO THE DIVERGENCE IS IN THE EXECUTION, NOT IN THE VALUES. "71% reimplementation" is 71% of the
    CONTROL FLOW and 0% of the CONSTANTS -- which is a materially better position than the ruling
    assumed, and it means a drifted expectation cannot hide here: if the pinned module's constant moves,
    these move with it.

If that import ever breaks, these predicates must FAIL rather than fall back to a local copy. There is no
fallback in this file, deliberately.
"""
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

# NO try/except. A missing pinned module means the expectations are unknown, and a replacement that
# silently substitutes its own would be exactly the drift this arrangement exists to prevent.
from validate_gate5_training_artifacts import (  # noqa: E402
    BKG_MODE,
    ESTIMATOR,
    FROZEN_POLICY,
    SEED_POLICY_STRING,
    SOURCE_SHA256,
)


def _scalar(store, key, *, where):
    keys = set(store.files) if hasattr(store, "files") else set(store)
    if key not in keys:
        raise SystemExit(f"[gate5-dataonly] {where}: required key absent: {key}")
    return np.asarray(store[key]).item()


def assert_artifact_policy_scalars(store, *, where):
    """Replaces :225 / :227 / :228 / :229 / :230 / :231.

    Six scalar equalities the pinned validator makes and this product's read-back did not. Every `want`
    is IMPORTED from the pinned module, so these cannot drift apart from it.

    WHY THEY ARE NOT OPTIONAL EVEN THOUGH THEY LOOK LIKE BOOKKEEPING: `estimator_fingerprint` and
    `seed_policy` are what make two members of a family comparable at all. A data-only family whose
    members were trained under different estimator settings would produce a spread that is not a
    statistical uncertainty, and nothing else in the data-only path looks at these fields -- the
    coherent family got them for free from a validator this product cannot run.
    """
    for key, want, note in (
        ("replica_seed_policy", SEED_POLICY_STRING, "the per-replica seed policy string"),
        ("seed_policy", FROZEN_POLICY, "the frozen estimator policy dict"),
        ("estimator_fingerprint", ESTIMATOR, "the estimator identity"),
        ("bkg_mode", BKG_MODE, "the background treatment"),
        ("tag", "nominal", "the training tag"),
        ("inputs_sha256", SOURCE_SHA256, "the frozen source digest"),
    ):
        got = _scalar(store, key, where=where)
        if got != want:
            raise SystemExit(
                f"[gate5-dataonly] {where}: {key} is {got!r}, not {want!r} ({note}); this is imported "
                f"from the pinned validator, so a mismatch is a real disagreement and not a drifted "
                f"local copy")
    return {"checked": 6, "replaces_pinned_sites": [225, 227, 228, 229, 230, 231],
            "expectations_imported_from": "validate_gate5_training_artifacts"}


def assert_inventory_identity_agree_with_target(store, target_bootstrap, *, where):
    """Replaces :239 / :241, and it is a CROSS-PROCESS comparison rather than a self-check.

    Both operands exist: the artifact carries `inventory_hashes` and `input_identity_hashes` written by
    the TRAINING stage, and the target receipt's `bootstrap` block carries the values the TARGET stage
    computed. Comparing them is admissible under `BEN-423` because the two were produced by different
    processes -- unlike a comparison of the artifact against itself, which is the tautology class that
    cost four parties three rounds on F2.
    """
    tb = dict(target_bootstrap or {})
    if not tb:
        raise SystemExit(f"[gate5-dataonly] {where}: no target bootstrap block; the cross-process "
                         f"inventory comparison has no second operand -- fail closed")
    inv_got = _scalar(store, "inventory_hashes", where=where)
    inv_want = tb.get("inventory_hashes")
    if inv_want is None:
        raise SystemExit(f"[gate5-dataonly] {where}: target receipt carries no inventory_hashes")
    if str(inv_got) != str(inv_want):
        raise SystemExit(f"[gate5-dataonly] {where}: inventory_hashes disagree between the training "
                         f"artifact and the target receipt: {str(inv_got)[:16]}... vs "
                         f"{str(inv_want)[:16]}...")
    id_got = _scalar(store, "input_identity_hashes", where=where)
    id_want = tb.get("input_identity_hashes")
    if id_want is None:
        raise SystemExit(f"[gate5-dataonly] {where}: target receipt carries no input_identity_hashes")
    if dict(id_got) != dict(id_want):
        raise SystemExit(f"[gate5-dataonly] {where}: input_identity_hashes disagree between the "
                         f"training artifact and the target receipt")
    return {"checked": 2, "replaces_pinned_sites": [239, 241],
            "operands": "training artifact vs target receipt -- different processes (BEN-423)"}


def assert_subsample_geometry(store, *, expected_mc_indices, where):
    """Replaces :248 / :252 / :255.

    `expected_mc_indices` MUST be independently regenerated by the caller from `default_rng(0).choice`,
    exactly as the pinned validator does before its member loop -- the comment there says
    "independently regenerated ... before this loop" and that independence is the whole content. This
    function will not regenerate it, because a predicate that derives its own expectation from the same
    seed the artifact used is comparing a value to itself.
    """
    exp = np.asarray(expected_mc_indices, dtype=np.int64)
    if exp.size == 0:
        raise SystemExit(f"[gate5-dataonly] {where}: expected mc_indices is empty; an equality against "
                         f"an empty array is vacuously satisfiable and must not be reported as a pass")
    mc = np.asarray(store["mc_indices"], dtype=np.int64)
    if not np.array_equal(mc, exp):
        raise SystemExit(f"[gate5-dataonly] {where}: mc_indices is not the frozen subsample "
                         f"(size {mc.size} vs {exp.size})")
    sub = np.asarray(store["sig_bootstrap_factor"], dtype=np.uint8)
    want_rows = int(FROZEN_POLICY["train_events"])
    if list(sub.shape) != [want_rows]:
        raise SystemExit(f"[gate5-dataonly] {where}: signal subset shape {list(sub.shape)} != "
                         f"[{want_rows}] (train_events, imported from the pinned policy)")
    n_bkg = int(_scalar(store, "n_bkg_full", where=where))
    bkg_idx = np.asarray(store["bkg_indices"], dtype=np.int64)
    if not np.array_equal(bkg_idx, np.arange(n_bkg, dtype=np.int64)):
        raise SystemExit(f"[gate5-dataonly] {where}: bkg_indices is not the complete ordered inventory "
                         f"0..{n_bkg - 1}")
    return {"checked": 3, "replaces_pinned_sites": [248, 252, 255],
            "independence": "expected_mc_indices is supplied by the caller, never regenerated here"}


def assert_weights_push_sane(store, *, where):
    """Replaces :304 / :305 / :306 -- shape, finiteness, non-negativity of the pushed weights.

    THE SHAPE OPERAND IS IMPORTED, not restated: `FROZEN_POLICY["train_events"]`. And non-negativity is
    checked on the ARRAY rather than on a summary, because a single negative weight in 2,000,000 rows
    cannot move a mean enough to notice and is exactly the defect this asserts against.
    """
    w = np.asarray(store["weights_push"])
    want_rows = int(FROZEN_POLICY["train_events"])
    if list(w.shape) != [want_rows]:
        raise SystemExit(f"[gate5-dataonly] {where}: weights_push shape {list(w.shape)} != "
                         f"[{want_rows}]")
    if not np.all(np.isfinite(w)):
        n = int(np.count_nonzero(~np.isfinite(w)))
        raise SystemExit(f"[gate5-dataonly] {where}: weights_push has {n} non-finite entries")
    if not np.all(w >= 0):
        n = int(np.count_nonzero(w < 0))
        raise SystemExit(f"[gate5-dataonly] {where}: weights_push has {n} negative entries; checked "
                         f"elementwise because one negative row in {want_rows} cannot move a summary")
    return {"checked": 3, "replaces_pinned_sites": [304, 305, 306]}
