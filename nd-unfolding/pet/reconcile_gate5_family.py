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
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import sys

import numpy as np

# ---------------------------------------------------------------------------
# Contracts copied from the producing code, with their sources named so a
# reader can diff them rather than trust this file.
# ---------------------------------------------------------------------------

# build_fullevent_replica_target.py:35
SEED_POLICY = "gate5-cstat-n50-v1: bootstrap_seed=50000+replica_index"
SEED_BASE = 50000

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

    # --- .done sentinels: check what they can actually prove. ---
    for label, path, subject in (("npy", npy + ".done", npy), ("receipt", rec + ".done", rec)):
        dj = load_done(path)
        if dj is not None:
            c.eq(f"done_{label}_names_current_subject", os.path.realpath(dj.get("output", "")),
                 os.path.realpath(subject),
                 note="binds the marker to this replica's file rather than presence alone")
            c.eq(f"done_{label}_records_current_size", dj.get("size"), os.path.getsize(subject),
                 note="a sentinel size differing from disk means the file changed after completion")

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
    c.eq("loader_sha256", r.get("code", {}).get("loader", {}).get("sha256"), EXPECTED_LOADER_SHA)

    art = r.get("artifact", {})
    path = art.get("path")
    if path and os.path.exists(path):
        c.eq("artifact_sha256_RECOMPUTED_vs_receipt", sha256_file(path), art.get("sha256"),
             note="hashed from disk this run")
        c.eq("artifact_size_on_disk", os.path.getsize(path), art.get("size_bytes"))
    else:
        c.truth("artifact_present_on_disk", False, note=f"{path} missing")

    # THE BINDING THAT MATTERS: this training must have consumed THIS replica's target.
    tgt = r.get("target", {})
    c.eq("training_target_sha_equals_measured_target_sha", tgt.get("sha256"),
         target_row.get("target_sha256_measured"),
         note="binds the training to the target this tool re-hashed from disk, not to the "
              "target receipt's own claim about itself")

    return {"stage": "training", "replica_index": idx, "state": "PRESENT",
            "artifact_sha256": art.get("sha256"),
            "target_sha256": tgt.get("sha256"),
            "evidence": r.get("evidence"),
            "timing_seconds": r.get("timing", {}).get("total_seconds"),
            "checks": c.summary(),
            "verdict": "PASS" if not c.failed else "FAIL"}


def constant_across_family(rows, path):
    """Group replicas by the value of a nested key. Anything the family shares MUST be constant;
    returning the grouping (not a boolean) means a violation names its members."""
    groups = {}
    for row in rows:
        cur = row.get("invariants", {})
        for part in path:
            cur = (cur or {}).get(part) if isinstance(cur, dict) else None
        groups.setdefault(json.dumps(cur, sort_keys=True), []).append(row["replica_index"])
    return groups


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", required=True, help="campaign dir containing replicas/")
    ap.add_argument("--n", type=int, default=50, help="declared inventory size (predeclared)")
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

    replay = not args.skip_replay
    cache = {}
    targets, trainings = [], []
    for idx in range(args.n):
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

    family.eq("targets_present", len(present_t), args.n)
    family.eq("target_replicas_failing_own_checks",
              sorted(t["replica_index"] for t in present_t if t["verdict"] != "PASS"), [])
    if args.stage == "family":
        family.eq("trainings_present", len(present_r), args.n)
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
        groups = constant_across_family(present_t, list(path))
        name = ".".join(path)
        invariants_report[name] = {json.loads(k): v for k, v in groups.items()} \
            if len(groups) > 1 else json.loads(next(iter(groups))) if groups else None
        family.eq(f"invariant_constant_across_family[{name}]", len(groups), 1 if present_t else 0,
                  note="more than one group means the family is not one inventory")

    seeds = sorted(t["bootstrap_seed"] for t in present_t)
    family.eq("seeds_are_contiguous_from_base",
              seeds, [SEED_BASE + t["replica_index"] for t in
                      sorted(present_t, key=lambda x: x["replica_index"])])

    target_complete = len(present_t) == args.n and not family.failed
    family_complete = target_complete and len(present_r) == args.n
    if args.stage == "target" and target_complete:
        verdict = "TARGETS_COMPLETE_PASS" if replay else "TARGETS_COMPLETE_PASS_REPLAY_SKIPPED"
    elif args.stage == "family" and family_complete:
        verdict = "FAMILY_COMPLETE_PASS" if replay else "FAMILY_COMPLETE_PASS_REPLAY_SKIPPED"
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
    if verdict == "PARTIAL" and (len(present_t) < args.n or len(present_r) < args.n):
        pass

    report = {
        "tool": "reconcile_gate5_family.py",
        "root": os.path.abspath(args.root),
        "stage": args.stage,
        "declared_inventory": args.n,
        "replay_performed": replay,
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
    return 0 if verdict.startswith(("FAMILY_COMPLETE", "TARGETS_COMPLETE")) else 2


if __name__ == "__main__":
    sys.exit(main())
