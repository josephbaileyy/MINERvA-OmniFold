#!/usr/bin/env python3
"""Reconcile the Gate-5 C_stat replica family (P5B item 1) from its own artifacts.

WHY THIS EXISTS, and the one thing it must never do
---------------------------------------------------
Gate 5's own rule: *a missing unit invalidates the replica; a missing replica invalidates the
declared ensemble manifest.* 49 of 50 is not a 49-replica ensemble, it is an invalid manifest.
So this tool REPORTS COMPLETENESS and never constructs, centres or summarises C_stat. It has no
covariance code in it at all -- that is deliberate, so it cannot be talked into producing a
number from a partial family.

WHAT IT VERIFIES BY MEASUREMENT rather than by reading a claim
--------------------------------------------------------------
The per-replica receipts are rich, but a receipt is a claim about a file. Three checks here are
INDEPENDENT of the receipt's own assertions:

  1. The target `.npy` is re-hashed from disk and compared to the sha the receipt records for it.
     (`train_fullevent_replica.py:112` writes a COPIED sha into a field named `_verified_`; that
     is BEN-149, and it is the reason nothing here trusts a `_verified_*` name.)

  2. All THREE coherent Poisson factor streams are re-drawn from the declared seed and the
     declared full inventory sizes, then hashed under the receipt's own stated contract, and
     compared to the recorded factor hashes.

     This matters most for the DATA stream. The target builder replays and array-compares the
     signal and background factors (`build_fullevent_replica_target.py:219-222`) and the training
     stage re-hashes the persisted signal and background factors
     (`train_fullevent_replica.py` validate_artifact) -- but the data factors are persisted
     nowhere and array-compared nowhere, at either stage, because the loader's bootstrap
     telemetry dict (`fullevent_fps_dataloader.py:1328-1330`) exposes `sig_bootstrap_factor` and
     `bkg_bootstrap_factor` and no data equivalent. The data factors are precisely what generate
     the measured-side statistical variance C_stat is meant to capture, so the one unverified
     stream is the one that matters most. Re-drawing it here does not prove the LOADER used it
     (only loader-side persistence could), but it does prove the recorded hash is the canonical
     draw for the declared (seed, n_data) -- and `n_data` is separately cross-checked below
     against the loader's own reported row count.

  3. `R` (step1_class_ratio) is re-derived from the operands published beside it. A verdict-only
     receipt is unfalsifiable; this is the check that lets the reported numbers contradict each
     other (CONVENTION-receipt-ingredients, BEN-077).

CAUTION ON ONE FIELD NAME, because it will mislead anyone re-deriving R by hand:
`runtime_target.step1_class_ratio_telemetry` contains `sum_w_reco_pass_reco_raw` at the OUTER
level, and `b4_w_reco_vs_w_truth` nested inside it contains a key of the SAME NAME with a
DIFFERENT value. The outer one carries the replica-SCALED sum (it equals the nested block's
`sum_w_reco_pass_reco_replica_scaled`); the nested one carries the genuinely unscaled sum. R is
built from the scaled one. This tool tries both and reports which reproduces R, rather than
assuming.

USAGE
-----
Run it from anywhere with numpy; it only reads the campaign tree.

  python3 reconcile_gate5_family.py --root <campaign_dir> --out family.json

Add `--skip-replay` to drop check 2 (the signal draw is ~49M variates per replica); the family
verdict then downgrades to reflect the weaker evidence rather than silently claiming the same
thing.

THE INVENTORY SIZE IS NOT AN ARGUMENT (BEN-157, R1)
---------------------------------------------------
`DECLARED_INVENTORY` is pinned in this file and bound by assertion to `SEED_POLICY`, which already
names it (`gate5-cstat-n50-v1`). `--n` survives only as an *assertion*: passing a value that
disagrees is a usage error and no report is written at all.

Until this repair `--n` was an unconstrained int and every completeness comparison was against it,
so `--n 0` on an empty directory returned rc=0 and the exact `FAMILY_COMPLETE_PASS`. The verdict was
not wrong so much as UNFALSIFIABLE: a pass at 50/50 and a pass at a caller-chosen size produced
reports that looked alike. `declared_inventory_is_pinned_in_tool` in the report exists so a reader
can tell those apart.

Exit codes:  0 complete  |  2 measured and NOT complete  |  3 usage / bad declaration.
`2` and `3` are distinct on purpose -- "looked and found it short" must never be confusable with
"could not look". The remaining items of the BEN-157 audit (receipt-supplied artifact paths, marker
`mtime`, driver digests, checks that vanish when their input is absent) are tracked in `OI-65` and
are NOT yet repaired.
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import sys

import numpy as np

# BEN-157 R2: the completion primitive is IMPORTED, never re-implemented.
#
# This tool used to compare a `.done` sentinel's recorded `size` to the file on disk by hand, and
# omitted `mtime` -- which `atomic_write.is_complete` checks. The reconciler was therefore strictly
# MORE PERMISSIVE than the primitive it stood in for, and nothing said so. Calling the primitive makes
# that class of divergence impossible rather than merely unlikely: there is one implementation.
#
# The import is FAIL-LOUD on purpose. This file is deployed to scratch as a single script, so the
# tempting fallback is "if atomic_write is missing, do the size-only check". That fallback is the
# defect. A missing primitive means the tool CANNOT perform the check it claims, and it must refuse to
# run rather than quietly downgrade. Deployment must copy atomic_write.py alongside this file.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import atomic_write as _aw
except ImportError as _exc:  # pragma: no cover - exercised by test_missing_atomic_write_is_fatal
    sys.stderr.write(
        "reconcile: cannot import atomic_write, which owns the completion-marker contract "
        f"({_exc}).\n"
        "           This tool will NOT fall back to a weaker marker check -- that divergence is\n"
        "           exactly the defect BEN-157 item 4 recorded. Copy atomic_write.py next to this\n"
        "           script (both live in nd-unfolding/pet/) and re-run.\n"
    )
    raise SystemExit(3)

# ---------------------------------------------------------------------------
# Contracts copied from the producing code, with their sources named so a
# reader can diff them rather than trust this file.
# ---------------------------------------------------------------------------

# build_fullevent_replica_target.py:35
SEED_POLICY = "gate5-cstat-n50-v1: bootstrap_seed=50000+replica_index"
SEED_BASE = 50000

# THE DECLARED INVENTORY SIZE, PINNED HERE AND NOT SUPPLIED BY THE CALLER.
#
# Until BEN-157 this was `--n`, an unconstrained int defaulting to 50, and every completeness
# comparison was against it. `--n 0` on an empty directory therefore returned rc=0 and the exact
# FAMILY_COMPLETE_PASS, and a real 3-member family passed at `--n 3` while being PARTIAL at `--n 50`
# with the artifacts unchanged. The file's own docstring states the principle its parser did not
# enforce: 49 of 50 is not a 49-replica ensemble.
#
# The number was already declared in this file -- SEED_POLICY reads `n50` -- and simply unenforced,
# so the assertion below binds the two rather than introducing a second source of truth. If the
# campaign's declared size ever changes, BOTH must change, and the mismatch is a hard error at
# import rather than a silently different gate.
DECLARED_INVENTORY = 50
assert f"n{DECLARED_INVENTORY}" in SEED_POLICY, (
    f"DECLARED_INVENTORY={DECLARED_INVENTORY} disagrees with SEED_POLICY={SEED_POLICY!r}; "
    "the inventory size is declared in two places and they have drifted"
)

# Exit codes. `2` already meant "the family is not complete" before BEN-157 and is left alone, so
# EXIT_USAGE is a THIRD code rather than a reuse of it: a caller asking the wrong question must
# never be confusable with a family that was measured and found short. (The sibling tool
# verify_executing_copy_is_committed.py uses 2 for usage and 3 for its bad finding -- the opposite
# assignment. Deliberate: preserving this tool's existing contract with its launcher outranks
# cosmetic consistency between tools, and both are documented where they are used.)
EXIT_COMPLETE = 0
EXIT_NOT_COMPLETE = 2
EXIT_USAGE = 3

# The nominal target this family is centred ON, and must never equal. Deliberately NOT hardcoded:
# it is supplied via --nominal-target-sha, measured from the Gate-2 promoted receipt at call time.
# A truncated prefix baked in here would be worse than nothing -- a 20-char constant compared with
# == against a 64-char digest silently never matches, so the check would pass by construction.

EXPECTED_HEAD = "b82ac63f9c5685c9cc05df059d2bbb4ae42d3258"
EXPECTED_INPUT_SHA = "fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625"
EXPECTED_LOADER_SHA = "e1402370cdb8bd6349419ba6fbefa68817b799b3699cc97b673933f1f0220ce1"
EXPECTED_GATE3_MANIFEST_SHA = "306e54596802623693cab3657164851b3880563ef8fb59ce3d2627062480cd2f"
EXPECTED_TARGET_BUILDER_SHA = "e3cd94d4f3983a628e34de4d852ce7ca93940be63c1cdfe28844a5a57f558234"
EXPECTED_NUMPY_DATALOADER_SHA = "bed9e0b39df54b465cb7e2a2600ff819ffb09350665603359bf12a52fdbd734a"
EXPECTED_CANONICAL_U2D_SHA = "8ebe0277ee4c277f6f697712a901b14d6ba24ed5dcadfc3c66b29276acf81b5e"

TARGET_VERDICT = "GATE5_REPLICA_TARGET_PASS_TRAINING_PENDING"
TRAIN_VERDICT = "GATE5_REPLICA_TRAINING_PASS_EXTRACTION_PENDING"

# Artifact names, TAKEN FROM THE LAUNCHER rather than guessed. Read from the Slurm-captured batch
# script of a live task (`scontrol write batch_script 56857233_0 -`), lines 36-37:
#     OUTPUT=${OUTDIR}/GATE5_REPLICA_WEIGHTS.npz
#     TRAIN_RECEIPT=${OUTDIR}/GATE5_REPLICA_TRAINING_RECEIPT.json
#
# THIS WAS WRONG IN THE FIRST VERSION OF THIS FILE and the way it was wrong is the point. It said
# GATE5_REPLICA_TRAIN_RECEIPT.json -- "TRAIN", not "TRAINING" -- an inferred name that never existed.
# A missing file at an inferred path is indistinguishable from a stage that has not run, so the
# reconciler would have reported `trainings_present: 0` and verdict PARTIAL *forever*, including at
# 50/50, and the family would never have been promotable. It happened to report the right count only
# because no training had finished yet: the verdict was accidentally right while the instrument was
# broken. Hence TRAINING_RECEIPT_GLOBS below -- a name mismatch must STOP the tool, not read as absence.
TRAIN_RECEIPT_NAME = "GATE5_REPLICA_TRAINING_RECEIPT.json"
TRAIN_ARTIFACT_NAME = "GATE5_REPLICA_WEIGHTS.npz"
# Anything matching these but NOT named above means this tool's expectations have drifted from the
# producer's. That is a fail-loud condition, never an "absent" one.
TRAINING_RECEIPT_GLOBS = ("*RECEIPT*.json", "*receipt*.json")
TRAINING_ARTIFACT_GLOBS = ("*.npz",)

# Tolerance for re-deriving a float64 quantity from its published float64 operands.
# Not a physics tolerance: it is the round-trip error of decimal JSON serialisation.
REL_TOL = 1e-12


def hash_array(value):
    """EXACT copy of build_fullevent_replica_target.py:47 hash_array.

    Contract as the receipts state it: sha256(dtype || JSON(shape) || contiguous raw bytes).
    Reproduced rather than imported because the producing tree is a private code root that this
    tool must not depend on being present.
    """
    a = np.ascontiguousarray(value)
    h = hashlib.sha256()
    h.update(str(a.dtype).encode("ascii"))
    h.update(json.dumps(list(a.shape), separators=(",", ":")).encode("ascii"))
    h.update(memoryview(a).cast("B"))
    return h.hexdigest()


def sha256_file(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def coherent_bootstrap_factors(n_data, n_sig, n_bkg, seed):
    """EXACT copy of fullevent_fps_dataloader.py:614 coherent_bootstrap_factors.

    Three INDEPENDENT streams -- data at rng(seed), signal at rng(seed+10_000_000) (the canonical
    pet_bootstrap.mc_poisson_factor), background at rng(seed+20_000_000). Independence is why a
    passing signal/background replay does NOT imply the data factors agree: it pins the seed and
    n_sig/n_bkg, and says nothing about n_data.
    """
    data_factor = np.random.default_rng(int(seed)).poisson(1.0, int(n_data)).astype(np.uint8)
    sig_factor = np.random.default_rng(int(seed) + 10_000_000).poisson(
        1.0, int(n_sig)).astype(np.uint8)
    bkg_factor = np.random.default_rng(int(seed) + 20_000_000).poisson(
        1.0, int(n_bkg)).astype(np.uint8)
    return data_factor, sig_factor, bkg_factor


def close(a, b, rel_tol=REL_TOL):
    a = float(a)
    b = float(b)
    scale = max(abs(a), abs(b), 1.0)
    return abs(a - b) <= rel_tol * scale


class Checks:
    """A check list that records operands, not just verdicts.

    Every failure carries the two values that disagree, so the report can be contradicted by
    someone who never runs this tool.
    """

    def __init__(self):
        self.passed = []
        self.failed = []

    def eq(self, name, got, want, note=None):
        ok = got == want
        row = {"check": name, "got": got, "want": want}
        if note:
            row["note"] = note
        (self.passed if ok else self.failed).append(row)
        return ok

    def near(self, name, got, want, note=None):
        ok = close(got, want)
        row = {"check": name, "got": got, "want": want,
               "abs_diff": abs(float(got) - float(want))}
        if note:
            row["note"] = note
        (self.passed if ok else self.failed).append(row)
        return ok

    def truth(self, name, value, note=None):
        ok = bool(value)
        row = {"check": name, "got": bool(value), "want": True}
        if note:
            row["note"] = note
        (self.passed if ok else self.failed).append(row)
        return ok

    def summary(self):
        return {"n_passed": len(self.passed), "n_failed": len(self.failed),
                "failures": self.failed}


def load_done(path):
    """Read a `.done` sentinel, and establish its write condition before believing it.

    The sentinel is written AFTER its subject and records the subject's size and mtime, so a
    sentinel whose recorded size disagrees with the file on disk means the file changed after
    being marked complete. That is the only thing this sentinel can prove, and it is worth
    checking rather than treating presence as success.
    """
    if not os.path.exists(path):
        return None
    with open(path) as fh:
        return json.load(fh)


def check_marker(c, label, subject):
    """Validate `subject`'s completion marker by CALLING the canonical primitive, plus one extra.

    Two checks, and the split is the point:

      `..._marker_is_complete` is `atomic_write.is_complete`, unmodified. It compares the marker's
      recorded size AND mtime to the file on disk. Before BEN-157 R2 this tool compared size only, so
      it accepted post-marker mutations the primitive rejects. Delegating removes the possibility of
      divergence rather than fixing one instance of it.

      `..._marker_names_current_subject` is the one thing `is_complete` does NOT do: it reads the
      marker's `output` field and requires it to name THIS replica's file. `is_complete` derives the
      marker path from the subject path, so a marker copied from another replica -- same size, same
      mtime, wrong `output` -- would satisfy it. That is why this check stays hand-rolled: it adds
      evidence the primitive does not carry, rather than restating it.

    KNOWN RESIDUAL, recorded rather than papered over: `is_complete` compares `int(st_mtime)`, i.e.
    WHOLE SECONDS. A same-size rewrite inside the same second is invisible to it, and therefore to
    this check. Closing that would mean changing the primitive, which is a separate decision with
    other callers (`lib/resume_guard.sh` mirrors it).
    """
    marker = _aw.completion_marker_path(subject)
    c.truth(f"{label}_marker_present", os.path.exists(marker), note=marker)
    if not os.path.exists(marker):
        return
    c.truth(f"{label}_marker_is_complete", _aw.is_complete(subject),
            note="atomic_write.is_complete: marker's recorded size AND mtime still describe the "
                 "file. Called, not re-implemented, so this tool cannot be more permissive than "
                 "the primitive (BEN-157 item 4)")
    dj = load_done(marker)
    if dj is not None:
        c.eq(f"{label}_marker_names_current_subject", os.path.realpath(dj.get("output", "")),
             os.path.realpath(subject),
             note="the one thing is_complete does not check: a marker copied from another replica "
                  "with matching size and mtime would satisfy the primitive")


def reconcile_target(idx, root, replay, cache):
    d = os.path.join(root, "replicas", f"replica_{idx:02d}", "target")
    npy = os.path.join(d, "GATE5_REPLICA_TARGET.npy")
    rec = os.path.join(d, "GATE5_REPLICA_TARGET_RECEIPT.json")

    present = {p: os.path.exists(p) for p in (npy, rec, npy + ".done", rec + ".done")}
    if not all(present.values()):
        return {"stage": "target", "replica_index": idx, "state": "ABSENT_OR_PARTIAL",
                "present": {os.path.basename(k): v for k, v in present.items()}}

    with open(rec) as fh:
        r = json.load(fh)
    c = Checks()

    seed = int(r.get("bootstrap_seed", -1))
    c.eq("seed_policy_string", r.get("seed_policy"), SEED_POLICY)
    c.eq("seed_equals_base_plus_index", seed, SEED_BASE + idx)
    c.eq("receipt_replica_index", int(r.get("replica_index", -1)), idx)
    c.eq("slurm_array_task_id", str(r.get("execution", {}).get("slurm_array_task_id")), str(idx))
    c.eq("status", r.get("status"), "PASS")
    c.eq("verdict", r.get("verdict"), TARGET_VERDICT)
    c.eq("head_at_runtime", r.get("execution", {}).get("head_at_runtime"), EXPECTED_HEAD)

    feed = r.get("step1_feed", {})
    w = feed.get("weights", {})
    rt = r.get("runtime_target", {})
    bs = r.get("bootstrap", {})

    # --- INDEPENDENT: re-hash the target from disk. Nothing here trusts a recorded sha. ---
    measured_sha = sha256_file(npy)
    measured_size = os.path.getsize(npy)
    c.eq("target_npy_sha256_RECOMPUTED_vs_receipt", measured_sha, w.get("sha256"),
         note="hashed from disk this run; the receipt's value is the claim being tested")
    c.eq("target_npy_size_on_disk", measured_size, w.get("size_bytes"))

    # --- .done sentinels: delegate to the primitive, then add what it does not do. ---
    for label, subject in (("npy", npy), ("receipt", rec)):
        check_marker(c, label, subject)

    # --- Pins and shared inputs. ---
    c.eq("input_sha256", r.get("input_preflight", {}).get("sha256"), EXPECTED_INPUT_SHA)
    c.eq("gate3_manifest_sha256", r.get("gate3_manifest", {}).get("sha256"),
         EXPECTED_GATE3_MANIFEST_SHA)
    c.eq("loader_sha256", r.get("code", {}).get("loader", {}).get("sha256"), EXPECTED_LOADER_SHA)
    c.eq("target_builder_sha256", r.get("code", {}).get("target_builder", {}).get("sha256"),
         EXPECTED_TARGET_BUILDER_SHA,
         note="this exact producer contains the fail-closed assert_refined_target_is_replica call")
    c.eq("numpy_dataloader_sha256",
         r.get("code", {}).get("numpy_dataloader", {}).get("sha256"),
         EXPECTED_NUMPY_DATALOADER_SHA)
    c.eq("canonical_u2d_sha256", r.get("code", {}).get("canonical_u2d", {}).get("sha256"),
         EXPECTED_CANONICAL_U2D_SHA)
    c.truth("canonical_replay_verified",
            bs.get("canonical_replay_verified") is True,
            note="literal True in the receipt, but reached only past the fail-closed replay at "
                 "build_fullevent_replica_target.py:219-222 -- guarded, unlike BEN-149's copied sha")
    c.eq("pet_training_started_at_target_stage", r.get("pet_training_started"), False)

    # --- Internal coherence: the same fact recorded in several places must agree. ---
    ident_b = bs.get("input_identity_hashes")
    ident_p = r.get("input_preflight", {}).get("input_identity_hashes")
    ident_r = rt.get("input_identity_hashes")
    c.eq("input_identity_hashes_have_all_source_families",
         sorted(ident_b) if isinstance(ident_b, dict) else None, ["bkg", "data", "sig"])
    c.truth("input_identity_hashes_agree_in_all_three_blocks",
            ident_b == ident_p == ident_r,
            note="bootstrap / input_preflight / runtime_target")

    # The pinned builder calls assert_refined_target_is_replica before publication. Validate the
    # operands left by that call, plus the complete learned-production refinement contract.
    config = r.get("configuration", {})
    c.eq("configuration_target_mode", config.get("target_mode"), "negweight-refined")
    c.eq("configuration_refinement_estimator", config.get("refinement_estimator"), "exact")
    c.eq("configuration_refinement_device", config.get("refinement_device"), "cpu")
    c.eq("configuration_refinement_random_state", config.get("refinement_random_state"), 45)
    c.eq("configuration_full_measured_inventory", config.get("full_measured_inventory"), True)
    c.eq("runtime_target_mode", rt.get("target_mode"), "negweight-refined")
    c.eq("runtime_refinement_is_learned_production",
         rt.get("refinement_is_learned_production"), True)
    c.eq("runtime_refinement_backend", rt.get("refinement_backend"),
         "u2d.refine_stay_positive")
    c.eq("runtime_refinement_protocol", rt.get("refinement"),
         "stay-positive (arXiv:2505.03724)")
    c.eq("runtime_estimator_fingerprint", rt.get("estimator_fingerprint"),
         "pet-fullevent-fps-v1")
    c.eq("runtime_bootstrap_seed_matches_receipt", rt.get("bootstrap_seed"), seed)
    c.eq("step1_telemetry_marks_bootstrap_replica",
         rt.get("step1_class_ratio_telemetry", {}).get("is_bootstrap_replica"), True)
    c.truth(
        "assert_refined_target_is_replica_evidence",
        r.get("code", {}).get("target_builder", {}).get("sha256") == EXPECTED_TARGET_BUILDER_SHA
        and rt.get("bootstrap_seed") == seed
        and rt.get("step1_class_ratio_telemetry", {}).get("is_bootstrap_replica") is True,
        note=("the pinned builder contains the assertion; runtime seed and replica telemetry "
              "independently bind the asserted operands"),
    )
    c.eq("step1_feed_path_is_this_replica_target", os.path.realpath(w.get("path", "")),
         os.path.realpath(npy))

    n_data_full = bs.get("n_data_full")
    n_sig_full = bs.get("n_sig_full")
    n_bkg_full = bs.get("n_bkg_full")

    # THE n_data CROSS-CHECK. The data-factor stream depends only on (seed, n_data), and no stage
    # array-compares it, so builder-side n_data must equal the loader's own reported data rows.
    c.eq("n_data_full_builder_vs_loader_n_data_rows", n_data_full, rt.get("n_data_rows"),
         note="closes the only free parameter of the unverified data-factor stream")
    c.eq("n_bkg_full_builder_vs_loader_n_bkg_rows", n_bkg_full, rt.get("n_bkg_rows"))
    if isinstance(n_data_full, int) and isinstance(n_bkg_full, int):
        c.eq("n_measured_rows_equals_data_plus_bkg", rt.get("n_measured_rows"),
             n_data_full + n_bkg_full)
    c.eq("step1_feed_rows_equals_n_measured_rows", feed.get("rows"), rt.get("n_measured_rows"))
    c.eq("step1_feed_zero_rows_equals_n_floored_zero", feed.get("zero_rows"),
         rt.get("n_floored_zero"))
    c.eq("mc_subset_not_larger_than_full_signal",
         bool(isinstance(bs.get("mc_subset_rows"), int) and isinstance(n_sig_full, int)
              and bs["mc_subset_rows"] <= n_sig_full), True)

    # --- R re-derived from its published operands (BEN-077). ---
    tel = rt.get("step1_class_ratio_telemetry", {})
    b4 = tel.get("b4_w_reco_vs_w_truth", {})
    R = rt.get("step1_class_ratio")
    num_parts = (tel.get("n_data_effective"), tel.get("bkg_pot_scaled_sum"))
    r_derivation = {"R_recorded": R}

    # BEN-157 R3, fail-closed half. Every R check below is guarded by isinstance(), so a receipt with
    # a null R silently dropped FOUR checks and the row still reported clean -- measured: 43 passed,
    # 0 failed, r_derivation {"R_recorded": null}. R and its operands are REQUIRED receipt fields, not
    # optional tool inputs, so their absence is a defect in the artifact and fails the member. A
    # verdict downgrade would be the wrong instrument here: it would tell the reader the TOOL ran
    # weakly, when in fact the RECEIPT is incomplete.
    c.truth("R_published_by_receipt", isinstance(R, (int, float)),
            note="step1_class_ratio is required; absent, the whole R re-derivation below silently "
                 "does not run and its absence was previously invisible")
    for field in ("pot_scale", "numerator_signed_data", "n_data_effective", "bkg_pot_scaled_sum"):
        c.truth(f"R_operand_published[{field}]", isinstance(tel.get(field), (int, float)),
                note="an operand the receipt must publish for R to be falsifiable at all (BEN-077)")
    if all(isinstance(v, (int, float)) for v in num_parts):
        num = float(num_parts[0]) - float(num_parts[1])
        r_derivation["numerator_derived"] = num
        c.near("R_numerator_from_operands", num, tel.get("numerator_signed_data"),
               note="n_data_effective - bkg_pot_scaled_sum")
    pot = tel.get("pot_scale")
    # The name collision: try BOTH candidates and report which one reproduces R.
    candidates = {
        "outer_sum_w_reco_pass_reco_raw": tel.get("sum_w_reco_pass_reco_raw"),
        "nested_sum_w_reco_pass_reco_raw": b4.get("sum_w_reco_pass_reco_raw"),
        "nested_sum_w_reco_pass_reco_replica_scaled": b4.get("sum_w_reco_pass_reco_replica_scaled"),
    }
    reproduced_by = []
    if isinstance(pot, (int, float)) and isinstance(R, (int, float)) \
            and isinstance(tel.get("numerator_signed_data"), (int, float)):
        for label, val in candidates.items():
            if not isinstance(val, (int, float)):
                continue
            den = float(pot) * float(val)
            if den and close(float(tel["numerator_signed_data"]) / den, float(R)):
                reproduced_by.append(label)
        r_derivation["denominator_candidates"] = {
            k: (float(pot) * float(v)) for k, v in candidates.items()
            if isinstance(v, (int, float))
        }
        r_derivation["R_reproduced_by"] = reproduced_by
        c.truth("R_reproducible_from_published_operands", bool(reproduced_by),
                note="pot_scale * one of the published pass_reco sums; see the field-name "
                     "collision documented at the top of this file")

    # R also drives the measured normalisation, so that is a second independent route to it.
    if isinstance(R, (int, float)):
        c.near("step1_measured_normalization_equals_R_times_mc_norm",
               rt.get("step1_measured_normalization"),
               float(R) * float(rt.get("step1_mc_normalization", 0.0)))

    # float32 target vs float64 telemetry: the sums must agree to float32 precision, not exactly.
    ns = feed.get("normalized_sum")
    mn = rt.get("step1_measured_normalization")
    if isinstance(ns, (int, float)) and isinstance(mn, (int, float)) and mn:
        rel = abs(float(ns) - float(mn)) / abs(float(mn))
        c.truth("float32_target_sum_matches_telemetry_to_float32_precision", rel < 1e-6,
                note=f"relative difference {rel:.3e}; the .npy is float32 and the telemetry "
                     f"float64, so exact equality is NOT expected and would itself be suspicious")
        r_derivation["target_sum_vs_telemetry_rel_diff"] = rel

    # --- INDEPENDENT: re-draw all three factor streams from the declared seed/inventory. ---
    replay_result = {"performed": False}
    if replay and all(isinstance(v, int) for v in (n_data_full, n_sig_full, n_bkg_full)):
        key = (n_data_full, n_sig_full, n_bkg_full, seed)
        if key not in cache:
            cache.clear()  # one entry: these arrays are ~49 MB
            cache[key] = coherent_bootstrap_factors(*key)
        df, sf, bf = cache[key]
        replay_result = {
            "performed": True,
            "data_factor_sha256_REDRAWN": hash_array(df),
            "signal_factor_sha256_REDRAWN": hash_array(sf),
            "background_factor_sha256_REDRAWN": hash_array(bf),
        }
        c.eq("data_factor_sha256_REDRAWN_vs_receipt", replay_result["data_factor_sha256_REDRAWN"],
             bs.get("data_factor_sha256"),
             note="THE STREAM NOTHING ELSE CHECKS -- no stage persists or array-compares it")
        c.eq("signal_factor_sha256_REDRAWN_vs_receipt",
             replay_result["signal_factor_sha256_REDRAWN"], bs.get("signal_factor_sha256"))
        c.eq("background_factor_sha256_REDRAWN_vs_receipt",
             replay_result["background_factor_sha256_REDRAWN"], bs.get("background_factor_sha256"))

    return {
        "stage": "target", "replica_index": idx, "state": "PRESENT",
        "bootstrap_seed": seed,
        "target_sha256_measured": measured_sha,
        "target_size_bytes_measured": measured_size,
        "factor_sha256": {
            "data": bs.get("data_factor_sha256"),
            "signal": bs.get("signal_factor_sha256"),
            "background": bs.get("background_factor_sha256"),
        },
        "invariants": {
            "n_data_full": n_data_full, "n_sig_full": n_sig_full, "n_bkg_full": n_bkg_full,
            "n_measured_rows": rt.get("n_measured_rows"),
            "inventory_hashes": bs.get("inventory_hashes"),
            "input_identity_hashes": ident_b,
            "pot_scale": tel.get("pot_scale"),
            "gate3_manifest_sha256": r.get("gate3_manifest", {}).get("sha256"),
            "code": {k: v.get("sha256") for k, v in (r.get("code") or {}).items()},
        },
        "R": R,
        "r_derivation": r_derivation,
        "replay": replay_result,
        "timing_seconds": r.get("timing", {}).get("total_seconds"),
        "checks": c.summary(),
        "verdict": "PASS" if not c.failed else "FAIL",
    }


def reconcile_training(idx, root, target_row):
    d = os.path.join(root, "replicas", f"replica_{idx:02d}", "training")
    rec = os.path.join(d, TRAIN_RECEIPT_NAME)
    if not os.path.exists(rec):
        # BEFORE calling this "absent", check that absence is not just this tool looking in the
        # wrong place. An inferred filename that never existed reads exactly like a stage that
        # never ran, and it reads that way permanently.
        strays = []
        for pattern in TRAINING_RECEIPT_GLOBS + TRAINING_ARTIFACT_GLOBS:
            for hit in glob.glob(os.path.join(d, pattern)):
                if os.path.basename(hit) not in (TRAIN_RECEIPT_NAME, TRAIN_ARTIFACT_NAME):
                    strays.append(os.path.basename(hit))
        if strays:
            return {"stage": "training", "replica_index": idx, "state": "NAME_MISMATCH",
                    "unexpected_files": sorted(set(strays)),
                    "expected_receipt": TRAIN_RECEIPT_NAME,
                    "note": "receipt-like or artifact-like files exist under names this tool does "
                            "not expect. This is a FAIL-LOUD condition, not absence: the producer's "
                            "naming and this tool's expectations have drifted, and treating it as "
                            "'not started' would report a permanent PARTIAL at full confidence."}
        # Genuine absence. Distinguish "not started" from "started and unfinished": the receipt is
        # written last, so its absence means incomplete and never failed.
        started = os.path.isdir(os.path.join(d, "w_nominal"))
        return {"stage": "training", "replica_index": idx,
                "state": "IN_PROGRESS" if started else "NOT_STARTED",
                "note": "receipt is written last, so its absence means incomplete, never failed"}

    with open(rec) as fh:
        r = json.load(fh)
    c = Checks()
    c.eq("status", r.get("status"), "PASS")
    c.eq("verdict", r.get("verdict"), TRAIN_VERDICT)
    c.eq("replica_index", int(r.get("replica_index", -1)), idx)
    c.eq("bootstrap_seed", int(r.get("bootstrap_seed", -1)), SEED_BASE + idx)
    c.eq("seed_policy_string", r.get("seed_policy"), SEED_POLICY)
    c.eq("head_at_runtime", r.get("execution", {}).get("head_at_runtime"), EXPECTED_HEAD)
    c.eq("slurm_array_task_id", str(r.get("execution", {}).get("slurm_array_task_id")), str(idx))

    # --- All THREE code digests the producer records, not just the loader. -----------------------
    #
    # BEN-157 item 5. `train_fullevent_replica.py:367-374` records replica_driver,
    # nominal_driver_unmodified and loader. `sbatch_gate5_replica_train_array.sh:41-44` checks all
    # three plus HEAD. This tool checked `head_at_runtime` and the loader only -- and
    # `head_at_runtime` is ITSELF a claim in the receipt, not a measurement, so the verifier's whole
    # provenance rested on two self-reported strings, one standing in for two digests recorded right
    # beside it. "The launcher checks them" is not a defence: BEN-156 established that the executing
    # copy can differ from the committed one, which is the class an independent verifier exists for.
    #
    # Only the loader has a pinned expectation. The two driver digests FLOAT BY DESIGN -- they ride the
    # next launch with a CODE_ROOT sync (OI-57/OI-58) -- so pinning a value here would be wrong. What
    # is checkable without a pin: re-hash each recorded path from disk, and require constancy across
    # the family (family-level, below). Named so neither claims more than it does: `..._matches_disk`
    # is deliberately not `..._is_the_right_driver`.
    code = r.get("code", {})
    c.eq("loader_sha256", code.get("loader", {}).get("sha256"), EXPECTED_LOADER_SHA)
    for role in ("replica_driver", "nominal_driver_unmodified", "loader"):
        info = code.get(role) or {}
        claimed, cpath = info.get("sha256"), info.get("path")
        c.truth(f"code_{role}_digest_recorded",
                isinstance(claimed, str) and len(claimed) == 64,
                note="a digest the producer records but this tool never reads is a digest nobody "
                     "checks; an absent one cannot be checked at all")
        if isinstance(cpath, str) and os.path.isfile(cpath):
            c.eq(f"code_{role}_matches_disk", sha256_file(cpath), claimed,
                 note="re-hashed from the path the receipt names. Proves the file THERE now matches "
                      "what was recorded; does NOT prove the path is the right one, which is what "
                      "the family-constancy check adds")

    # --- The artifact, at the CANONICAL path rather than the one the receipt names. -------------
    #
    # BEN-157 item 3. This used to hash `art["path"]` straight from the receipt, compared against
    # nothing. Codex moved the weights to UNEXPECTED_WEIGHTS.npz, updated the receipt to match, and
    # got an exact pass with trainings_name_mismatch=0 -- because the NAME_MISMATCH stray scan is
    # reachable only when the receipt is ABSENT, so a receipt at the correct name never enters it.
    # The guard catches a file that disagrees with the launcher; it could not catch a receipt that
    # AGREES with a wrong file.
    #
    # The fix is the R2 invariant: hash the canonical path, and treat the receipt's path as a CLAIM
    # to be tested against it. The target stage already did exactly this at
    # `step1_feed_path_is_this_replica_target`; the training stage did not, in the same file.
    art = r.get("artifact", {})
    canonical = os.path.join(d, TRAIN_ARTIFACT_NAME)
    c.eq("artifact_path_is_canonical", os.path.realpath(str(art.get("path", ""))),
         os.path.realpath(canonical),
         note="the receipt's own path claim, tested against the launcher's name rather than "
              "trusted; a receipt agreeing with a wrongly-named file fails here")
    if os.path.exists(canonical):
        c.eq("artifact_sha256_RECOMPUTED_vs_receipt", sha256_file(canonical), art.get("sha256"),
             note="hashed from the CANONICAL path this run, not from the path the receipt names")
        c.eq("artifact_size_on_disk", os.path.getsize(canonical), art.get("size_bytes"))
        check_marker(c, "weights", canonical)
    else:
        c.truth("artifact_present_at_canonical_path", False, note=f"{canonical} missing")

    # `artifact.completion_marker_valid` is deliberately NOT read as evidence.
    # `train_fullevent_replica.py:358` writes the Python literal `True`, so it is a decoration rather
    # than a measurement and REQUIRING IT WOULD BE A CHECK THAT CANNOT FAIL -- which is the class this
    # whole repair is about, and adding one here would be a self-inflicted example. The measurement it
    # gestures at is `weights_marker_is_complete` above. Vocabulary defect filed as OI-66.
    #
    # (Codex reported this as "a receipt declaring itself invalid passes". True, but the sharper form
    # is that no receipt from this producer CAN declare itself invalid: the field is a constant.)

    # The receipt's own marker, at the training stage. The target stage checked two markers; this
    # stage checked none (BEN-157 item 2).
    check_marker(c, "train_receipt", rec)

    # THE BINDING THAT MATTERS: this training must have consumed THIS replica's target.
    tgt = r.get("target", {})
    c.eq("training_target_sha_equals_measured_target_sha", tgt.get("sha256"),
         target_row.get("target_sha256_measured"),
         note="binds the training to the target this tool re-hashed from disk, not to the "
              "target receipt's own claim about itself")

    return {"stage": "training", "replica_index": idx, "state": "PRESENT",
            "artifact_sha256": art.get("sha256"),
            "target_sha256": tgt.get("sha256"),
            # Under "invariants" because that is where constant_across_family() looks. Exposed so the
            # family stage can require these constant across members: per-member re-hashing proves the
            # file at a recorded path matches its record, but only cross-member constancy catches a
            # driver that changed MID-FLIGHT, which is the risk a floating pin leaves open (item 5).
            "invariants": {
                "code": {role: (code.get(role) or {}).get("sha256")
                         for role in ("replica_driver", "nominal_driver_unmodified", "loader")},
                "code_paths": {role: (code.get(role) or {}).get("path")
                               for role in ("replica_driver", "nominal_driver_unmodified", "loader")},
            },
            "evidence": r.get("evidence"),
            "timing_seconds": r.get("timing", {}).get("total_seconds"),
            "checks": c.summary(),
            "verdict": "PASS" if not c.failed else "FAIL"}


def constant_across_family(rows, path):
    """Group replicas by the value of a nested key under `row["invariants"]`.

    Anything the family shares MUST be constant; returning the grouping rather than a boolean means a
    violation names its members.

    A MISSPELLED OR MISPLACED PATH USED TO CERTIFY THE FAMILY. Every row resolved to None, so the
    result was a single group and the check passed -- indistinguishable from genuine agreement. That
    is how the R2 training invariants shipped broken in their first draft: the values were put at the
    row's top level instead of under `invariants`, every member resolved to None, and the check could
    not fail. Caught by its own power test, which is the argument for having one.

    `resolves` is therefore returned alongside the grouping: False when the path is absent from every
    row, so the caller can fail loudly instead of reading a vacuous pass as a result.
    """
    groups, resolved_any = {}, False
    for row in rows:
        cur = row.get("invariants", {})
        for part in path:
            cur = (cur or {}).get(part) if isinstance(cur, dict) else None
        if cur is not None:
            resolved_any = True
        groups.setdefault(json.dumps(cur, sort_keys=True), []).append(row["replica_index"])
    return groups, (resolved_any or not rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", required=True, help="campaign dir containing replicas/")
    ap.add_argument("--n", type=int, default=DECLARED_INVENTORY,
                    help=f"ASSERTION ONLY: must equal the pinned DECLARED_INVENTORY "
                         f"({DECLARED_INVENTORY}). It cannot change the gate; it exists so a "
                         f"caller who believes the inventory is some other size finds out here "
                         f"instead of getting a pass measured against their own belief (BEN-157).")
    ap.add_argument("--nominal-target-sha", default=None,
                    help="sha256 of the promoted nominal target; every replica must differ from it")
    ap.add_argument("--out", default=None, help="write the full JSON report here")
    ap.add_argument("--stage", choices=("family", "target"), default="family",
                    help="target validates the terminal target family without requiring training")
    ap.add_argument("--source-npz", default=None,
                    help="independently hash the immutable full-input NPZ once")
    ap.add_argument("--skip-replay", action="store_true",
                    help="skip the three-stream factor re-draw (weakens the verdict, and says so)")
    args = ap.parse_args()

    # BEN-157 R1: the declaration is pinned, and --n may only agree with it. Checked BEFORE any
    # artifact is read, so a caller who asked the wrong question gets no report at all rather than
    # a well-formed one measured against their own premise.
    if args.n != DECLARED_INVENTORY:
        print(
            f"reconcile: --n {args.n} does not match the pinned declared inventory "
            f"{DECLARED_INVENTORY} ({SEED_POLICY}).\n"
            f"           --n is an assertion, not a parameter: completeness is measured against "
            f"the predeclaration, never against the caller.\n"
            f"           If the campaign's declared size really changed, change "
            f"DECLARED_INVENTORY and SEED_POLICY together and re-run the tests.",
            file=sys.stderr,
        )
        return EXIT_USAGE

    replay = not args.skip_replay
    cache = {}
    targets, trainings = [], []
    for idx in range(DECLARED_INVENTORY):
        t = reconcile_target(idx, args.root, replay, cache)
        targets.append(t)
        trainings.append(reconcile_training(idx, args.root, t))

    present_t = [t for t in targets if t["state"] == "PRESENT"]
    present_r = [r for r in trainings if r["state"] == "PRESENT"]

    # --- Family-level checks that no single replica can make. ---
    family = Checks()

    # NAME_MISMATCH first: it means this tool's expectations have drifted from the producer's, so
    # every other count below is suspect. It must BLOCK, never be absorbed into a completeness gap.
    mismatched = sorted(r["replica_index"] for r in trainings if r["state"] == "NAME_MISMATCH")
    if args.stage == "family":
        family.eq("no_training_artifact_name_mismatches", mismatched, [],
                  note="unexpected receipt/artifact filenames mean the reconciler is looking in "
                       "the wrong place; a count of 0 present would then be a statement about the "
                       "SEARCH, not about the campaign")

    family.eq("targets_present", len(present_t), DECLARED_INVENTORY)
    family.eq("target_replicas_failing_own_checks",
              sorted(t["replica_index"] for t in present_t if t["verdict"] != "PASS"), [])
    if args.stage == "family":
        family.eq("trainings_present", len(present_r), DECLARED_INVENTORY)
        family.eq("training_replicas_failing_own_checks",
                  sorted(r["replica_index"] for r in present_r if r["verdict"] != "PASS"), [])

    source_measurement = {"performed": False}
    if args.source_npz:
        source_path = os.path.realpath(args.source_npz)
        source_measurement = {"performed": True, "path": source_path}
        if os.path.isfile(source_path):
            source_measurement.update({
                "sha256_RECOMPUTED": sha256_file(source_path),
                "size_bytes_RECOMPUTED": os.path.getsize(source_path),
            })
            family.eq("source_npz_sha256_RECOMPUTED",
                      source_measurement["sha256_RECOMPUTED"], EXPECTED_INPUT_SHA,
                      note="hashed from the immutable full-input file during this validation")
        else:
            family.truth("source_npz_present", False, note=source_path)

    # DISTINCTNESS is the check that catches the reassuring failure: identical targets would
    # collapse the measured-side variance and read as a SMALL C_stat, not as a broken draw.
    for label, get in (("target", lambda t: t["target_sha256_measured"]),
                       ("data_factor", lambda t: t["factor_sha256"]["data"]),
                       ("signal_factor", lambda t: t["factor_sha256"]["signal"]),
                       ("background_factor", lambda t: t["factor_sha256"]["background"])):
        vals = [get(t) for t in present_t]
        dupes = sorted({v for v in vals if vals.count(v) > 1})
        family.eq(f"{label}_sha_all_distinct_across_family", dupes, [],
                  note="identical values here would look like a small statistical component "
                       "rather than a failed draw")

    if args.nominal_target_sha:
        clashes = sorted(t["replica_index"] for t in present_t
                         if t["target_sha256_measured"] == args.nominal_target_sha)
        family.eq("no_replica_target_equals_the_nominal_target", clashes, [])

    # Anything shared by construction must be identical across the family.
    invariant_paths = [
        ("n_data_full",), ("n_sig_full",), ("n_bkg_full",), ("n_measured_rows",),
        ("inventory_hashes",), ("input_identity_hashes",), ("pot_scale",),
        ("gate3_manifest_sha256",), ("code", "loader"), ("code", "target_builder"),
        ("code", "numpy_dataloader"), ("code", "canonical_u2d"),
    ]
    invariants_report = {}
    for path in invariant_paths:
        groups, resolves = constant_across_family(present_t, list(path))
        name = ".".join(path)
        invariants_report[name] = {json.loads(k): v for k, v in groups.items()} \
            if len(groups) > 1 else json.loads(next(iter(groups))) if groups else None
        # A path absent from every row groups into ONE null bucket and would otherwise read as
        # unanimous agreement. Assert it resolves before believing the grouping.
        family.truth(f"invariant_path_resolves[{name}]", resolves,
                     note="absent from every replica: the check below would pass vacuously")
        family.eq(f"invariant_constant_across_family[{name}]", len(groups), 1 if present_t else 0,
                  note="more than one group means the family is not one inventory")

    # Training-side invariants: the three code digests and their paths must be identical across every
    # member. Per-member re-hashing proves each recorded path still matches its record; only this
    # catches a driver or loader that changed MID-FLIGHT, which is precisely what a floating pin
    # (OI-57/OI-58) leaves open and what no pinned constant could detect. Runs only at the family
    # stage, where trainings are expected at all.
    if args.stage == "family":
        for role in ("replica_driver", "nominal_driver_unmodified", "loader"):
            for block in ("code", "code_paths"):
                groups, resolves = constant_across_family(present_r, [block, role])
                name = f"training.{block}.{role}"
                invariants_report[name] = (
                    {json.loads(k): v for k, v in groups.items()} if len(groups) > 1
                    else json.loads(next(iter(groups))) if groups else None
                )
                family.truth(f"invariant_path_resolves[{name}]", resolves,
                             note="absent from every replica: the check below would pass vacuously")
                family.eq(f"invariant_constant_across_family[{name}]", len(groups),
                          1 if present_r else 0,
                          note="more than one group means the training code changed mid-family; a "
                               "floating pin cannot catch this and a pinned constant would not "
                               "either, because it would match every member equally")

    seeds = sorted(t["bootstrap_seed"] for t in present_t)
    family.eq("seeds_are_contiguous_from_base",
              seeds, [SEED_BASE + t["replica_index"] for t in
                      sorted(present_t, key=lambda x: x["replica_index"])])

    # --- BEN-157 R3: a weaker run must not be able to emit a stronger verdict. ------------------
    #
    # `--skip-replay` already did this correctly, downgrading to a NAMED suffix so the artifact says
    # which evidence is missing. `--source-npz` and `--nominal-target-sha` did not: absent, their
    # checks simply never ran and the verdict was the full-strength one. The R derivation was worse
    # still -- with a null `R` four checks silently disappeared and the row reported 43 of 43 clean.
    #
    # Two different treatments, because they are two different things:
    #   * A missing TOOL INPUT is the caller's choice, so it downgrades the verdict and names itself.
    #   * A missing RECEIPT FIELD is a defect in the artifact, so it FAILS the member (see
    #     `R_published_by_receipt` in reconcile_target). Fail closed, not downgrade.
    weakened = []
    if not replay:
        weakened.append("REPLAY_SKIPPED")
    if not args.source_npz:
        weakened.append("SOURCE_UNHASHED")
    if not args.nominal_target_sha:
        weakened.append("NOMINAL_UNCHECKED")
    suffix = "".join("_" + w for w in weakened)

    target_complete = len(present_t) == DECLARED_INVENTORY and not family.failed
    family_complete = target_complete and len(present_r) == DECLARED_INVENTORY
    if args.stage == "target" and target_complete:
        verdict = "TARGETS_COMPLETE_PASS" + suffix
    elif args.stage == "family" and family_complete:
        verdict = "FAMILY_COMPLETE_PASS" + suffix
    elif args.stage == "family" and mismatched:
        # Blocks even with nothing else present: the search itself is unreliable.
        verdict = "BLOCK"
    elif family.failed and (len(present_t) or len(present_r)):
        verdict = "BLOCK" if any(
            f["check"].startswith(("target_replicas_failing", "training_replicas_failing"))
            or "distinct" in f["check"] or "invariant" in f["check"]
            or "name_mismatch" in f["check"]
            for f in family.failed) else "PARTIAL"
    else:
        verdict = "PARTIAL"
    # A completeness shortfall alone is PARTIAL, never BLOCK; a coherence failure is BLOCK even
    # when the family is still filling, because more replicas cannot repair it.
    if verdict == "PARTIAL" and (len(present_t) < DECLARED_INVENTORY or len(present_r) < DECLARED_INVENTORY):
        pass

    report = {
        "tool": "reconcile_gate5_family.py",
        "root": os.path.abspath(args.root),
        "stage": args.stage,
        "declared_inventory": DECLARED_INVENTORY,
        # The artifact must record WHERE the declaration came from, not just its value. Before
        # BEN-157 a pass at 50/50 and a pass at a caller-chosen n produced byte-identical-looking
        # reports, so the artifact could not contradict a wrong verdict -- which made the verdict
        # unfalsifiable rather than wrong. These two fields are what let a reader check that.
        "declared_inventory_is_pinned_in_tool": True,
        "declared_inventory_policy_string": SEED_POLICY,
        "replay_performed": replay,
        # The axes are listed as data as well as encoded in the verdict suffix: a reader should not
        # have to parse a string to learn which evidence is missing, and a downstream check should
        # not have to either (CONVENTION-receipt-ingredients).
        "weakened_axes": weakened,
        "is_full_strength": not weakened,
        "source_input_measurement": source_measurement,
        "verdict": verdict,
        "C_stat": None,
        "why_C_stat_is_null": (
            "This tool never constructs, centres or summarises C_stat. Gate 5's own rule: a "
            "missing replica invalidates the declared ensemble manifest, so a partial family has "
            "no covariance to report. Only a verified 50/50 advances to extraction and centering."
        ),
        "counts": {
            "targets_present": len(present_t),
            "targets_passing": sum(1 for t in present_t if t["verdict"] == "PASS"),
            "trainings_present": len(present_r),
            "trainings_passing": sum(1 for r in present_r if r["verdict"] == "PASS"),
            "trainings_in_progress": sum(1 for r in trainings if r["state"] == "IN_PROGRESS"),
            "trainings_not_started": sum(1 for r in trainings if r["state"] == "NOT_STARTED"),
            "trainings_name_mismatch": len(mismatched),
            "targets_absent": sum(1 for t in targets if t["state"] != "PRESENT"),
        },
        "family_checks": family.summary(),
        "family_invariants": invariants_report,
        "targets": targets,
        "trainings": trainings,
    }

    text = json.dumps(report, indent=2, sort_keys=True, default=str)
    if args.out:
        with open(args.out, "w") as fh:
            fh.write(text + "\n")
    print(json.dumps({
        "verdict": verdict,
        "counts": report["counts"],
        "family_failures": family.failed,
        "C_stat": None,
    }, indent=2, sort_keys=True, default=str))
    if verdict.startswith(("FAMILY_COMPLETE", "TARGETS_COMPLETE")):
        return EXIT_COMPLETE
    return EXIT_NOT_COMPLETE


if __name__ == "__main__":
    sys.exit(main())
