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
from pathlib import Path

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
    TRAIN_ARTIFACT,
    TRAIN_RECEIPT,
    expected_checkpoints,
)

# Two more expectations the pinned validator states as FUNCTION-LOCAL literals, so they cannot be
# imported. Restated here and pinned to the pinned module's source by controls, the same arrangement as
# `required_keys`. Kept as module constants rather than inline so the controls have something to name.
CHECKPOINT_SEMANTICS = "final-epoch weights, round-trip verified (BEN-043)"
FATAL_LOG_TOKENS = ["Traceback (most recent call last)", "[gate5-train][FAIL]", "SystemExit:"]


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


def assert_target_binding(store, *, target_sha256, target_receipt_sha256, target_receipt_path,
                          where):
    """Replaces :275 / :276 / :278 -- the artifact's record of WHICH target and receipt it consumed.

    THE OPERANDS ARE THE CALLER'S, AND MUST COME FROM THE FILESYSTEM -- the digest of the receipt file
    as it sits on disk and its real path -- not from the artifact. A comparison of the artifact's own
    two fields against each other would be the F2 tautology again; the content here is that the files
    on disk still are what the artifact says it consumed.

    All three legs are checked together so a caller cannot pass one wrong member's operands and have
    only two of three notice.
    """
    got_sha = _scalar(store, "replica_target_receipt_sha256", where=where)
    if str(got_sha) != str(target_receipt_sha256):
        raise SystemExit(
            f"[gate5-dataonly] {where}: the artifact records target-receipt digest "
            f"{str(got_sha)[:16]}... but the file on disk digests to "
            f"{str(target_receipt_sha256)[:16]}...; the receipt has changed since training")
    got_path = os.path.realpath(str(_scalar(store, "replica_target_receipt_path", where=where)))
    want_path = os.path.realpath(str(target_receipt_path))
    if got_path != want_path:
        raise SystemExit(f"[gate5-dataonly] {where}: the artifact records target-receipt path "
                         f"{got_path} but this member's receipt is at {want_path}")
    art_target = _scalar(store, "replica_target_sha256", where=where)
    if str(art_target) != str(target_sha256):
        raise SystemExit(f"[gate5-dataonly] {where}: the artifact records target digest "
                         f"{str(art_target)[:16]}... but the target on disk digests to "
                         f"{str(target_sha256)[:16]}...")
    return {"checked": 3, "replaces_pinned_sites": [275, 276, 278],
            "operands": "filesystem digests/paths vs the artifact's record -- not the artifact "
                        "against itself"}


def assert_target_meta_fields(store, *, identities, where):
    """Replaces :282 / :284 / :285 -- the loader-published target block's mode, estimator and identity.

    DELIBERATELY NOT :283. That site compares the target block's `bootstrap_seed` against 50000+idx,
    which is the overloaded field whose two meanings killed 57194055, and it is replaced by F1/F3 in
    `cstat_data_only.assert_data_only_target_is_this_replicas` -- a different predicate with a different
    operand. Listing it here too would double-count it in the manifest and, worse, would suggest the seed
    question is settled by a field re-read.

    `identities` is the caller's, taken from the TARGET RECEIPT's bootstrap block, so this is
    cross-process like :239/:241 rather than a self-comparison.
    """
    meta = _scalar(store, "target", where=where)
    if not isinstance(meta, dict) or not meta:
        raise SystemExit(f"[gate5-dataonly] {where}: the artifact carries no target block; ABSENT IS "
                         f"NOT NOMINAL -- fail closed")
    if meta.get("target_mode") != BKG_MODE:
        raise SystemExit(f"[gate5-dataonly] {where}: target_mode is {meta.get('target_mode')!r}, "
                         f"not {BKG_MODE!r}")
    if meta.get("estimator_fingerprint") != ESTIMATOR:
        raise SystemExit(f"[gate5-dataonly] {where}: target estimator_fingerprint is "
                         f"{meta.get('estimator_fingerprint')!r}, not {ESTIMATOR!r}")
    if identities is None:
        raise SystemExit(f"[gate5-dataonly] {where}: no identity map supplied; the cross-process "
                         f"identity comparison has no second operand -- fail closed")
    if dict(meta.get("input_identity_hashes") or {}) != dict(identities):
        raise SystemExit(f"[gate5-dataonly] {where}: the target block's input_identity_hashes disagree "
                         f"with the target receipt's")
    return {"checked": 3, "replaces_pinned_sites": [282, 284, 285],
            "deliberately_excluded": {283: "the overloaded bootstrap_seed, replaced by F1/F3"}}


def expected_lr_schedule():
    """The 6-fit schedule DERIVED from the imported policy, not restated.

    The pinned validator hardcodes `expected_rates`, `expected_iterations`, `n_fits_base_lr = 2`,
    `n_fits_annealed = 4` and `fit_count = 6` as FUNCTION-LOCAL literals -- so unlike the policy scalars
    they cannot be imported. They are not arbitrary: they follow from `FROZEN_POLICY["niter"] = 3` (two
    fits per iteration, step 1 and step 2) and the lr policy's base/annealed rates with
    `applies_from_iteration = 1`.

    SO THEY ARE DERIVED HERE AND THE DERIVATION IS PROVED AGAINST THE PINNED LITERALS BY A CONTROL that
    extracts them from the pinned module's source. Strictly better than restating: a restatement is true
    when written and silent afterwards, while a derivation plus an equality control fails the moment
    either side moves -- and says which side.
    """
    lr = dict(FROZEN_POLICY["lr_policy"])
    niter = int(FROZEN_POLICY["niter"])
    fits_per_iteration = 2                      # step 1 and step 2
    from_iter = int(lr["applies_from_iteration"])
    iterations, rates = [], []
    for it in range(niter):
        for _ in range(fits_per_iteration):
            iterations.append(it)
            rates.append(float(lr["annealed_lr"] if it >= from_iter else lr["base_lr"]))
    return {
        "iterations": iterations,
        "rates": rates,
        "n_fits_base_lr": sum(1 for it in iterations if it < from_iter),
        "n_fits_annealed": sum(1 for it in iterations if it >= from_iter),
        "fit_count": len(iterations),
    }


def assert_lr_policy_realized(store, *, where, atol=3e-12):
    """Replaces :292 / :293 / :294 / :295 / :298 / :300.

    WHY THIS IS NOT BOOKKEEPING: the learning-rate schedule is part of the ESTIMATOR. Two members
    trained under different schedules are two different estimators, and their disagreement is not a
    statistical fluctuation -- which is the entire quantity this product publishes. Nothing else on the
    data-only path reads these fields.

    `atol=3e-12` is the pinned tolerance, carried deliberately: the claim is that a SPECIFIC RATE WAS
    APPLIED -- an arithmetic value round-tripped through JSON -- so a toleranced comparison is right and
    bit-exactness would test the serializer (`BEN-409`).
    """
    realized = _scalar(store, "lr_policy_realized", where=where)
    if not isinstance(realized, dict) or not realized:
        raise SystemExit(f"[gate5-dataonly] {where}: no lr_policy_realized block -- fail closed")
    if realized.get("verified_from_optimizer") is not True:
        raise SystemExit(
            f"[gate5-dataonly] {where}: verified_from_optimizer is "
            f"{realized.get('verified_from_optimizer')!r}, not True; a DECLARED schedule is not a "
            f"realized one, and this field is the only thing distinguishing them")
    exp = expected_lr_schedule()
    fits = realized.get("fits") or []
    if len(fits) != exp["fit_count"]:
        raise SystemExit(f"[gate5-dataonly] {where}: {len(fits)} fits, expected {exp['fit_count']} "
                         f"(derived from niter={FROZEN_POLICY['niter']}, two fits per iteration)")
    for key in ("n_fits_base_lr", "n_fits_annealed"):
        if int(realized.get(key, -1)) != int(exp[key]):
            raise SystemExit(f"[gate5-dataonly] {where}: {key} is {realized.get(key)!r}, expected "
                             f"{exp[key]}")
    got_iters = [f.get("iteration") for f in fits]
    if got_iters != exp["iterations"]:
        raise SystemExit(f"[gate5-dataonly] {where}: fit iterations {got_iters} != "
                         f"{exp['iterations']}")
    for i, (fit, want) in enumerate(zip(fits, exp["rates"])):
        got = fit.get("learning_rate")
        if got is None or abs(float(got) - want) > atol:
            raise SystemExit(f"[gate5-dataonly] {where}: fit[{i}] learning_rate {got!r} != {want!r} "
                             f"within {atol}")
    return {"checked": 6, "replaces_pinned_sites": [292, 293, 294, 295, 298, 300],
            "schedule": "DERIVED from the imported policy, proved against the pinned literals by a "
                        "control"}


def optimizer_proof_line():
    """The log line the pinned validator counts, DERIVED from the imported policy.

    `:340` asserts exactly one occurrence of a hardcoded string containing "2 fit(s) at 0.0001, 4 at
    1e-05". Those four values are the same ones `expected_lr_schedule()` derives, so the STRING is
    derived here too rather than copied -- and a control proves the derivation reproduces the pinned
    literal character for character. Copying it would give a check that is true when written and silent
    if the policy changes; deriving it gives one that fails and says which side moved.
    """
    exp = expected_lr_schedule()
    lr = dict(FROZEN_POLICY["lr_policy"])
    return (f"LR anneal VERIFIED from the optimizer: {exp['n_fits_base_lr']} fit(s) at "
            f"{lr['base_lr']}, {exp['n_fits_annealed']} at {lr['annealed_lr']}")


def assert_checkpoints_and_contract(train_dir, contract, *, where):
    """Replaces :315 / :318 / :320 / :324 / :326.

    `expected_checkpoints()` and `TRAIN_ARTIFACT` / `TRAIN_RECEIPT` are IMPORTED from the pinned module,
    so the file-set and namespace expectations are the pinned ones rather than a copy. The two final
    checkpoint paths are derived from `FROZEN_POLICY["niter"]` -- the pinned validator writes `iter2`
    literally, and 2 is `niter - 1`.

    WHY THE NAMESPACE CHECK MATTERS AND IS NOT TIDINESS: `training_namespace_root_entries` is an EXACT
    set equality, so a stray file in a member's training directory fails it. That is what catches a
    partial rerun leaving debris beside a complete artifact -- the shape of `BEN-023`, where a resume
    guard let 7 partial slabs block their own repair.
    """
    train_dir = Path(train_dir)
    niter = int(FROZEN_POLICY["niter"])
    last = niter - 1
    if contract.get("checkpoint_semantics") != CHECKPOINT_SEMANTICS:
        raise SystemExit(f"[gate5-dataonly] {where}: checkpoint_semantics is "
                         f"{contract.get('checkpoint_semantics')!r}, not {CHECKPOINT_SEMANTICS!r}")
    ckpt_dir = train_dir / "w_nominal"
    expected_final = {
        f"step{step}_checkpoint":
            ckpt_dir / f"OmniFold_fe_nominal_nominal_iter{last}_step{step}_final.weights.h5"
        for step in (1, 2)
    }
    for key, path in expected_final.items():
        got = os.path.realpath(str(contract.get(key, "")))
        if got != os.path.realpath(str(path)):
            raise SystemExit(f"[gate5-dataonly] {where}: inference contract {key} points at {got!r}, "
                             f"not this member's {os.path.realpath(str(path))!r}")
        if not (path.is_file() and not path.is_symlink()):
            raise SystemExit(f"[gate5-dataonly] {where}: {key} is missing, or is a symlink, at {path}")
    if not ckpt_dir.is_dir():
        raise SystemExit(f"[gate5-dataonly] {where}: no checkpoint directory at {ckpt_dir}")
    got_ckpts = sorted(p.name for p in ckpt_dir.iterdir() if p.is_file())
    want_ckpts = sorted(expected_checkpoints())
    if got_ckpts != want_ckpts:
        missing = sorted(set(want_ckpts) - set(got_ckpts))
        extra = sorted(set(got_ckpts) - set(want_ckpts))
        raise SystemExit(f"[gate5-dataonly] {where}: checkpoint file set differs -- missing {missing}, "
                         f"unexpected {extra}")
    got_root = sorted(p.name for p in train_dir.iterdir())
    want_root = sorted({TRAIN_ARTIFACT, TRAIN_ARTIFACT + ".done", TRAIN_RECEIPT,
                        TRAIN_RECEIPT + ".done", "w_nominal"})
    if got_root != want_root:
        extra = sorted(set(got_root) - set(want_root))
        missing = sorted(set(want_root) - set(got_root))
        raise SystemExit(f"[gate5-dataonly] {where}: training namespace differs -- missing {missing}, "
                         f"unexpected {extra}; an EXACT set is asserted so a partial rerun's debris "
                         f"beside a complete artifact fails rather than passing (BEN-023's shape)")
    return {"checked": 5, "replaces_pinned_sites": [315, 318, 320, 324, 326],
            "imported": ["expected_checkpoints", "TRAIN_ARTIFACT", "TRAIN_RECEIPT"]}


def assert_member_logs(logs_dir, *, array_job_id, replica_index, bootstrap_seed, where):
    """Replaces :333 / :334 / :337 / :339 / :340 / :342 / :343 / :345.

    `array_job_id` IS A CALLER-SUPPLIED OPERAND, deliberately. The pinned validator takes it from a
    module-level literal naming one campaign run, which is the mis-scoping this product's manifest
    records: a pin naming a CODE STATE is reusable across runs, a pin naming a RUN is not. Passing it in
    is what makes this predicate usable by any family, and it is the one difference from the pinned form
    that is an improvement rather than an accommodation.

    THE ZERO-COUNT DIRECTION IS THE LOAD-BEARING ONE. Each count is asserted `== 1`, not `>= 1`: two
    DONE lines mean the task ran twice into the same namespace, and one is the only correct answer. And
    `fatal_log_tokens` is asserted EMPTY across BOTH streams, because a Traceback in stderr with a clean
    stdout is exactly how 57194055 failed while its logs looked short rather than wrong.
    """
    logs_dir = Path(logs_dir)
    idx, seed = int(replica_index), int(bootstrap_seed)
    out_p = logs_dir / f"train_{array_job_id}_{idx}.out"
    err_p = logs_dir / f"train_{array_job_id}_{idx}.err"
    for label, p in (("stdout", out_p), ("stderr", err_p)):
        if not (p.is_file() and not p.is_symlink()):
            raise SystemExit(f"[gate5-dataonly] {where}: {label} is missing, or is a symlink, at {p}")
    out_text = out_p.read_text(errors="replace")
    err_text = err_p.read_text(errors="replace")
    exact_one = (
        ("log_start_line", f"[gate5-train] index={idx} seed={seed} job={array_job_id}_{idx}"),
        ("log_config_gate_pass", '"config_gate": "PASS"'),
        ("log_optimizer_proof", optimizer_proof_line()),
        ("log_pass_receipt", '"status": "PASS"'),
        ("log_done", f"[gate5-train] DONE index={idx} seed={seed}"),
    )
    for name, needle in exact_one:
        n = out_text.count(needle)
        if n != 1:
            raise SystemExit(
                f"[gate5-dataonly] {where}: {name} appears {n} times in stdout, expected exactly 1 "
                f"({needle!r}); 0 means it did not happen and 2 means the task ran twice into one "
                f"namespace -- both are failures and only 1 is correct")
    fatal = [t for t in FATAL_LOG_TOKENS if t in out_text or t in err_text]
    if fatal:
        raise SystemExit(f"[gate5-dataonly] {where}: fatal tokens present across the two streams: "
                         f"{fatal}; checked in BOTH because a Traceback in stderr with a clean stdout "
                         f"is how 57194055 failed while its logs looked short rather than wrong")
    return {"checked": 8, "replaces_pinned_sites": [333, 334, 337, 339, 340, 342, 343, 345],
            "array_job_id": "caller-supplied, NOT a module literal naming one run"}
