#!/usr/bin/env python3
"""Verify every file-hash binding recorded in any receipt against the checkout.

WHY THIS EXISTS. Gate receipts freeze code by sha256: Gate-2's canonical runtime
receipt binds `fullevent_fps_dataloader.py` and `gate2_target_runtime.py`, the
Gate-3 and Gate-4 launch-code gates each bind a launcher/driver/validator/test
set. Those freezes are the evidence that a gate passed against specific code, and
an ordinary-looking refactor can silently void them.

On 2026-07-28 a repo-root de-rooting refactor (commit 2732304) did exactly that,
breaking six bindings at once -- including both Gate-4 entry points and the
Gate-2 dataloader -- while every test still passed. Nothing in the suite noticed,
because the edits were behaviourally inert on Perlmutter (the derived root equals
the old literal there). Only the hashes changed. Run this before and after any
sweeping edit.

PATH REMAPPING. Receipts written on Perlmutter record absolute
`/pscratch/sd/j/josephrb/MINERvA-OmniFold/...` paths. A naive existence check
skips those, which is how the Gate-2 dataloader binding was missed on a first
pass. Absolute paths under the known Perlmutter root are therefore remapped onto
the local checkout before hashing.

SHELL PINS. Receipts are not the only place code is frozen by hash. Launchers and
final-writers carry their own `EXPECTED_<ROLE>_SHA=` constants and abort on
mismatch, and until 2026-07-31 nothing walked them -- so when b3751cc and f6a9e8e
rewrote `gate2_target_runtime.py` and `fullevent_fps_dataloader.py`, the pins in
`run_gate2_target_validator.sh` went stale silently and made that route
unrunnable. The receipt-backed Gate-4 pair broke in the same commits and was
loud, because this file already covered it. Shell pins are now collected from the
comparison sites themselves, which is the only place the pin is unambiguously
tied to the file it pins (the constant names do not map to the variable names --
`EXPECTED_BASE_G2_VAL_SHA` guards `$BASE_G2_VALIDATOR`).

A stale pin is not repaired by editing the hash. The constant records what the
gate ran against; moving it to match the working tree converts the guard into a
no-op and destroys the evidence. Re-issue the owning gate and record the move.

FIELD PINS (OI-96, added 2026-08-17). A hash binding freezes CONTENT. It cannot
freeze a POINTER, and the canonical-nominal designation is a pointer: promotion
there moves no bytes, so the safety argument is entirely that the receipts naming
the protected artifacts keep naming them. That was enforced by
`check_canonical_designation.py`'s WHOLE-FILE occurrence count of the namespace --
a proxy for pinning a path field, and MEASURED WRONG IN BOTH DIRECTIONS by mutating
the receipt and running that guard:

    repoint `products/canonical_baseline/path` to a SIBLING inside the same
    protected directory   -> count stays 2, guard SILENT   <- the BEN-133 repoint
                                                              class it exists for
    delete the prose sentence at :245
                          -> count falls to 1, guard RED   <- a legitimate edit

Silent on the defect, loud on the innocent edit. So this file now also checks 44
declared FIELD values across the 22 RECORD-FROZEN JSON receipts, derived by
`state/regen_canonical_namespace_field_pins.py` and stored in
`state/canonical-namespace-field-pins-20260817.json`. A repoint is loud; prose is
invisible to them.

These pin the VALUE OF A FIELD, not the bytes of an artifact -- most targets are
cluster products under /pscratch and are absent from any checkout, so a digest pin
cannot run here at all. Green means the receipts still POINT where they pointed. It
says NOTHING about whether the artifacts changed, exactly as BEN-325 says of the
count this replaces.

Exit 0 if every resolvable binding matches, 1 otherwise.
"""
import argparse
import ast
import glob
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys

PERLMUTTER_ROOT = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/"

# Bindings known to have drifted before 2026-07-28 and deliberately not "fixed":
# these receipts record what ran at submit time, and rewriting their hashes would
# falsify history. Listed so real regressions stay visible above the noise.
#
# EXACT AND SOURCE-QUALIFIED (AUDIT-FINDINGS-20260731 J11; DECISION-20260804-B4-STEP3-RECEIPTS D3).
# Each entry is `(bound path, source receipt, expected sha256)`, so a NEW receipt drifting on the
# same file is not silently exempted, and an entry that no longer drifts FAILS the run: a red that
# silently disappears is as invisible as a new one, and a dead exemption would pre-waive the next
# binding to reach its path. The three path-only entries `wakerctl.py`, `test_wakerctl.py` and
# `gate2_queue_hedge_controller.sh` were pruned on 2026-09-23 because no live binding names them
# any more (their receipts left the checkout at the 2026-08-20 compaction).
KNOWN_PREEXISTING = {
    ("nd-unfolding/pet/sbatch_dump_g2_mefhc.sh",
     "docs/orchestration/state/g2-dump-submit-20260719.json",
     "324a40811669355bdd219d2b5f7988a80cea22e585cbab2e8d98f2bf178fc46e"),
    # KNOWN_ISSUES #33, 2026-09-23 (Joseph: "if something needs to be fixed, fix it now"): these
    # readers now take `step1_class_ratio_target` with a legacy fallback. The RUN receipts below
    # record the bytes those runs executed and are not edited; `git show` recovers them.
    ("nd-unfolding/pet/gate6_floor_statistics.py",
     "docs/orchestration/state/gate6-floor-replication-partial-56863958.json",
     "637ee33d2c36270ae084e17ebb8696f081f77bd7f9f6712738764a989904b7cc"),
    ("nd-unfolding/pet/evaluate_annealed_nominal_reproduction.py",
     "docs/orchestration/state/annealed-nominal-error-56563092.json",
     "077e43620fcfb1c12401b41e60f32e184ab0290b67a89bc55def0bfed2735149"),
}

# Minimum EXPECTED_*_SHA guards the shell collector must still resolve to files in
# the checkout. Raise it when launchers add pins; lowering it needs the same
# justification as deleting a guard, because that is what it does.
#
# COUNT ONLY PINS ON TRACKED FILES. This host resolves 17, but 5 of those are pins
# on artifacts that are NOT in git -- G2_FPS_MEFHC_P12.npz twice and the compiled
# MINERvA101/opt/bin/runEventLoopOmniFold three times -- which localize() resolves
# here only because this scratch checkout happens to hold them. A fresh clone, or
# this one after a scratch purge, resolves 12. Setting the floor to the observed 17
# would therefore make the guard fail on any checkout without a 9.9 GB dump and a
# built binary, and the obvious way out of THAT is lowering the floor, which is the
# one move the docstring forbids. 12 is the count every checkout can honour.
# Was 10, which was likewise exactly the tracked count before
# sbatch_powered_closure.sh started pinning its driver and preflight in the one-line
# idiom collect_shell can actually see (2026-08-05).
# Raised 12 -> 13 on 2026-08-06: the concurrent session's `sbatch_b1_niter4_scan48.sh`
# (committed in 82968d4) pins `closure_b1_rate_injection.py`, a tracked source file that
# every checkout holds, so the tracked count grew by one and
# test_powered_closure_preflight.py::test_pin_floor_covers_these_pins went red on
# `13 != 12`. Raising to match is what that test prescribes; verified locally that the
# verifier still resolves 13 and reports ALL BINDINGS INTACT rather than going BLIND.
# Raised 13 -> 15 on 2026-08-07: `sbatch_powered_closure_budget_probe.sh` (the D2 under-fitting
# probe) pins BOTH `closure_powered_truth_reweight.py` and `preflight_powered_closure.py` in the
# one-line idiom collect_shell can see, and both are tracked source files every checkout holds, so
# the tracked count grew by exactly two. Counted before raising, by running the collector over the
# same three globs the test uses against `git ls-files`: 15, itemised. Raising to match is what the
# test prescribes; the direction that is forbidden is lowering it to make a red test pass, which
# would be deleting a guard.
# Raised 15 -> 20 on 2026-09-23 (AUDIT-FINDINGS-20260731 J12/J13): `_VAR_DEF` now accepts a
# trailing `# comment`, which walks the three P3F -> domain -> base validator pins in
# `sbatch_p3f_pet_fullevent_evloop_array.sh:59-61` (+3), and `merge_g2_gate1_mefhc.sh` now pins the
# two validators it executes (+2). All five match the checkout. Counted, not argued: 20 tracked.
SHELL_PIN_FLOOR = 20

# J12: `EXPECTED_*_SHA` constants DEFINED in a walked shell script that no comparison line pairs
# to a file. Exact, keyed `(script, NAME)`: a new entry means a pin nothing here can see go stale;
# a vanished entry means the declaration is out of date.
#
# Every entry below is compared through a two-line temporary (`gs="$(sha_of "$X")"`, then
# `[[ "$gs" == "$EXPECTED_..." ]]` on a later line) or exported to a child job, which the one-line
# pairing rule cannot see. All bind untracked data products except the two powered-closure
# PRODUCER pins, which bind the tracked `G2_FPS_MEFHC_P12_RECEIPT.json` (matching, 2026-09-23).
SHELL_UNWALKED_PINS = {
    ("nd-unfolding/pet/sbatch_annealed_shape_validation.sh", "EXPECTED_INPUTS_SHA"),
    ("nd-unfolding/pet/sbatch_fullevent_diagnostic_extract.sh", "EXPECTED_INPUTS_SHA"),
    ("nd-unfolding/pet/sbatch_fullevent_diagnostic_xsec_resume.sh", "EXPECTED_INPUTS_SHA"),
    ("nd-unfolding/pet/sbatch_p5a_fullevent_nominal_extract.sh", "EXPECTED_INPUTS_SHA"),
    ("nd-unfolding/pet/sbatch_p5a_fullevent_nominal_extract.sh", "EXPECTED_WEIGHTS_SHA"),
    ("nd-unfolding/pet/sbatch_pet_fullevent_ml_ensemble.sh", "EXPECTED_TARGET_SHA"),
    ("nd-unfolding/pet/sbatch_pet_fullevent_nominal_annealed.sh", "EXPECTED_TARGET_SHA"),
    ("nd-unfolding/pet/sbatch_powered_closure.sh", "EXPECTED_INPUTS_SHA"),
    ("nd-unfolding/pet/sbatch_powered_closure.sh", "EXPECTED_PRODUCER_SHA"),
    ("nd-unfolding/pet/sbatch_powered_closure_budget_probe.sh", "EXPECTED_INPUTS_SHA"),
    ("nd-unfolding/pet/sbatch_powered_closure_budget_probe.sh", "EXPECTED_PRODUCER_SHA"),
    ("nd-unfolding/pet/sbatch_powered_closure_stability_repeat.sh", "EXPECTED_INPUTS_SHA"),
    ("nd-unfolding/pet/submit_gate5_extraction_n50.sh", "EXPECTED_INPUT_SHA"),
    ("nd-unfolding/pet/submit_gate5_extraction_r2_n50.sh", "EXPECTED_INPUT_SHA"),
}

# J14: floor for 64-hex pin constants in *.py resolved to TRACKED files, same device as
# SHELL_PIN_FLOOR. Count them with collect_python over py_files() against the tracked set.
# 3 on 2026-09-23: `validate_g2_gate1_pairs.py:85-91` pins the base and domain validators and the
# G2 production launcher (a fourth pin, on the compiled binary, is untracked). All three match.
PY_PIN_FLOOR = 3


def py_files(root):
    """Python sources the pin collector walks: the same three trees as the shell collector."""
    return (glob.glob(os.path.join(root, "docs/**/*.py"), recursive=True)
            + glob.glob(os.path.join(root, "nd-unfolding/**/*.py"), recursive=True)
            + glob.glob(os.path.join(root, "2d-unfolding/**/*.py"), recursive=True))


# Exact live receipt-binding inventory at the post-freeze compaction boundary.
# Historical receipts retired from the checkout remain recoverable at annotated tag
# `evidence/prepublication-2026-08-20-0b329e8a`; they must not force their redundant
# bindings to remain live forever. The former scalar floor (140) could detect a large
# collapse but was deliberately blind to gradual erosion. This identity check is
# stronger: it hashes every unique, resolvable (checkout-relative path, expected sha256)
# pair after the same localization and deduplication used by the verifier.
#
# Canonical serialization is UTF-8, sorted lexicographically, one
# `<path>\t<sha256>\n` record per unique binding. Any added, removed, or repointed live
# binding therefore requires an explicit count+digest update in the same reviewed
# commit. No second inventory file is added to the repository.
#: OI-143a. A JSON that declares this top-level key is a TEST FIXTURE and its bindings are held out
#: of the PRODUCTION verdict. `std_component_manifest.B1_E.json` pins a digest that is DELIBERATELY
#: DEAD -- its own `_fixture` block says `"must_be": "REJECTED by the B1 completeness check"` and
#: `tests/test_p4_repair.py` lists B1_E in MUST_REJECT -- so on the cluster, where the bound artifact
#: exists, this gate reported a deliberate negative control as provenance drift. Updating that digest
#: would have silently broken the control.
#: WHY A SEMANTIC DESIGNATION AND NOT `tests/fixtures/**`. Measured: 12 JSONs live under
#: nd-unfolding/tests/fixtures/ and 11 of them self-declare. A blanket path exclusion would
#: therefore ALSO have dropped one file that makes no such claim, untested and invisibly. A fixture
#: has to SAY it is one.
#: HELD OUT IS NOT UNCHECKED: `fixture_integrity` below pins the set and each file's own sha256, so a
#: fixture still cannot be edited silently -- what it no longer does is assert that the world matches
#: a digest it exists to contradict.
NEGATIVE_CONTROL_MARKER = "_fixture"

#: The self-declaring fixtures, pinned by count and by a digest over (path, sha256) pairs.
#: Counted by running the collector, not assumed.
#: MOVED 11 -> 12 ON 2026-08-21, DELIBERATELY, WITH THE REASON. `REFERENCE_real_manifest.json` now
#: self-declares. It was the ONLY JSON in packet_b1_adversarial/ that did not, and as a direct result
#: it was the file this gate resolved a binding through -- reporting MISMATCH on the 42.3 GB
#: `std_final5_candidate.root` off a `candidate_sha256` that all twelve fixtures there share for
#: historical reasons. Declaring it brings it under the SEMANTIC rule rather than widening the rule to
#: a path.
#: WHY THIS COSTS NO COVERAGE, measured on the cluster before acting rather than argued: the
#: artifact's on-disk sha256 is `950f8cb1...` and FIVE non-fixture files bind it at exactly that value
#: -- two committed receipts under state/ plus the three production manifests beside the artifact. The
#: production chain was already correct and self-consistent; the gate was reporting a FALSE POSITIVE
#: by consulting a test fixture as though it were a receipt.
#: WHY NOT INSTEAD REFRESH THE FIXTURE'S FIELD: no test reads it, so the sole effect would be to green
#: a check -- the OI-123 hazard -- and it would erase that the fixture records the state before
#: retraction-index row 72's documented authorized rewrite.
#: SAFE BECAUSE AN EXISTING PASSING TEST ALREADY PROVES IT: `B1_K` is the MUST_ACCEPT variant and it
#: already carries a `_fixture` block, so the accept path demonstrably tolerates the key. 129/129 in
#: tests/test_p4_repair.py after the change.
FIXTURE_COUNT = 12
FIXTURE_SET_SHA256 = "36355204b4b82fa4f901740b75667ee1efd0152864067196f17e23e3ed52a1e1"

#: MOVED 117 -> 118 ON 2026-08-21, DELIBERATELY, WITH THE REASON AND WITH THE DELTA NAMED.
#: The negweight durability step added ONE live binding, and it is the only row that changed:
#:
#:     2d-unfolding/HANDOFF_bkg_negweight/hpss_recover_negweight.sh
#:       e989051b7ff95bc0620f253e35ab5b8adf613d26c1adcdb403bad48e4b3bd970
#:
#: bound by `recovery.route_sha256` beside its `recovery.route` sibling in
#: state/negweight-hpss-durability-20260821.json. It is the committed HPSS recovery route, pinned
#: at the revision that was actually executed and power-tested, so the pin is the point of the
#: receipt rather than incidental to it.
#: THIS IS NOT THE FORBIDDEN MOVE, and the distinction is the one this message itself draws.
#: Bumping "merely to make this pass" is forbidden because it makes the gate agree with whatever
#: happens to be in the tree -- the OI-143b shape, where the count moved because untracked scratch
#: receipts resolve differently per checkout and NOTHING was reviewed. Here the delta was
#: enumerated before the constant moved (one row, printed above), the new binding VERIFIES rather
#: than mismatching, and it arrives with the receipt that owns it.
#: AND IT IS POWER-TESTED, so it is not a pin that cannot fail: changing one hex digit of
#: `route_sha256` makes this file report
#:   MISMATCH 2d-unfolding/HANDOFF_bkg_negweight/hpss_recover_negweight.sh ... rc 1
#: measured before the bump, not argued.
#: NOTE FOR ANYONE READING THIS ON THE CLUSTER: that checkout resolves untracked scratch receipts
#: and read 119 against the old 117 (OI-143b). It will now read 120 against 118. The divergence is
#: pre-existing and per-tree; this change does not create it and does not fix it.
#: MOVED 118 -> 119 ON 2026-08-22, DELIBERATELY, WITH THE REASON AND WITH THE DELTA NAMED.
#: PR-06 committed the P3S standard lateral packet, which added ONE live binding:
#:
#:     nd-unfolding/active_universe_5d/standard/candidate/std_component_manifest.json
#:       269232245870632884d6e589ac8d7aa9ba7fb4e07d0860e077cbd98fe6de04b5
#:
#: bound by `component_manifest_sha256` beside its `component_manifest` sibling in
#: candidate/p4_standard_validation.json. Both files arrive in the same commit, and the pin is the
#: point of that receipt: it is what lets a later reader tell the validated component manifest from
#: a substituted one after the 42.3 GB candidate itself is purged.
#: THE DELTA WAS ENUMERATED BEFORE THE CONSTANT MOVED, and enumerating it took bisection rather
#: than a read, which is worth recording: each of the three new candidate JSONs is CLEAN ON ITS OWN
#: (rc=0, ALL BINDINGS INTACT) and the count moves only when p4_standard_validation.json and
#: std_component_manifest.json are BOTH present. The binding is a PAIR -- a sha256 in one file
#: naming a path satisfied by another -- so "which file added it" has no single-file answer, and a
#: one-at-a-time check would have concluded that nothing did.
#: AND IT IS POWER-TESTED, so it is not a pin that cannot fail: flipping the last hex digit of
#: `component_manifest_sha256` makes this file report
#:   MISMATCH nd-unfolding/active_universe_5d/standard/candidate/std_component_manifest.json  rc 1
#: measured before the bump, then reverted, not argued.
#: THE OTHER HALF OF PR-06 MOVED NOTHING: the three updated evidence/*.json are clean on their own
#: (rc=0), which was checked separately so that one change could not be credited to the other.
#: CLUSTER NOTE, carried forward and re-based: that checkout resolves untracked scratch receipts and
#: read 120 against 118. It will now read 122 against 120. Pre-existing and per-tree; unchanged here.
#: 119 -> 120: `docs/orchestration/control-plane/campaign-origin.json` pins the ONE repository whose
#: refs namespace holds the R5 campaign queue, and it repeats the ruling record and that record's
#: sha256 so the pinned origin and the campaign key are demonstrably the same campaign's. That pair
#: has exactly the shape this collector harvests, so the pin's own claim about the ruling record is
#: now verified here rather than only inside campaignctl.
#: THE DELTA WAS ENUMERATED BEFORE THE CONSTANT MOVED, and it is one row and only one row:
#:   ADDED   docs/orchestration/DECISION-20260902-joseph-rules-cause7-cause3-and-the-stop.md
#:           0836139b1c9a057c194a81a94d45c9f979209a9ac293d4bc8434e6b43fc1a064
#:   REMOVED (none)
#: measured by recomputing `receipt_inventory` with the new file EXCLUDED, which reproduces
#: 119 / 09301df6 exactly -- so nothing else in this commit moved the inventory, and the new file is
#: the whole cause.
#: AND IT IS POWER-TESTED: flipping the last hex digit of the pin's `ruling_record_sha256` makes this
#: file report
#:   MISMATCH docs/orchestration/DECISION-20260902-joseph-rules-cause7-cause3-and-the-stop.md
#: and *** BINDINGS BROKEN ***, measured before the bump and then reverted, not argued.
#: 120 -> 120, digest 0b29b654 -> 23f68f4b (2026-09-23, ISSUE-55). This is a REPOINT, not an addition.
#: The pinned g1 validator `nd-unfolding/pet/validate_gate5_training_artifacts.py` was re-issued to fix
#: its dead "SystemExit:" fatal token, and its LIVE pin in
#: `state/DIVERGENCE-MANIFEST-20260818-cstat-data-only.json` (`pinned_module.sha256`) moved with it:
#:   REPOINTED nd-unfolding/pet/validate_gate5_training_artifacts.py
#:             1aea6f96fef54d0298d885998d5556f326fb273eba7aabbaf44dc4b922c59067
#:          -> 27801a97eb342cee30d3bc8c6a1ab0bca1e63c3e9100bbaa2afc611bdd200c38
#: The delta was enumerated before the constant moved. Swapping that one row back to its old want
#: reproduces 120 / 0b29b654 exactly. Power-tested: flipping the manifest pin's last hex digit makes
#: this file report `MISMATCH nd-unfolding/pet/validate_gate5_training_artifacts.py`. That was
#: measured, then reverted.
#: 120 -> 121, digest 23f68f4b -> 298eceb4 (2026-09-23, ISSUE-48). One binding was ADDED:
#:   ADDED   docs/orchestration/state/step1-traj-ihedge-56525829.salloc.log
#:           e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
#: The widened verify_receipt_artifacts.py (.log now in scope) found this 0-byte log. It is cited,
#: with its sha256, by state/step1-ihedge-launch-56525829.json, and git had never carried it. It is
#: now force-added, byte-identical to the cluster copy (0 bytes, the empty-file sha256, measured on
#: Perlmutter). Excluding that one row reproduces 120 / 23f68f4b exactly.
#: 121 -> 121, DIGEST 298eceb4 -> f447426d ON 2026-09-23: the Gate-4 launch-code re-issue
#: (p3f-pet-gate4-launch-code-gate-20260923.json supersedes 20260813, retired in place) for
#: KNOWN_ISSUES rows 28/38/33, under Joseph's 2026-09-23 ruling ("if something needs to be fixed,
#: fix it now"). The delta was enumerated before the constant moved, and it is FOUR REPOINTS, nothing
#: added or removed:
#:   omnifold_nn/omnifold/omnifold.py                3a2022b0 -> 3d95aae2
#:   nd-unfolding/pet/train_fullevent_nominal.py     91144bee -> ba939bd2
#:   nd-unfolding/pet/validate_pet_nominal_gate4.py  6d04a366 -> 8719b701
#:   nd-unfolding/pet/annealed_estimator.py          fdf6556c -> f6717968
#: Reconstructing the inventory with 20260813 at its pre-retirement bytes and 20260923 absent
#: reproduces 121 / 298eceb4 exactly. Power-tested: flipping the last hex of the successor's engine
#: pin makes this file report MISMATCH omnifold_nn/omnifold/omnifold.py, rc 1; then restored.
#: 121 -> 122, digest f447426d -> f5fc1a9e (2026-09-25, OI-190, the s5c campaign). One binding was
#: ADDED, by the campaign's frozen contract state/s5c/contract.json (identities.partition_scan):
#:   ADDED   docs/orchestration/state/s5c/b1/partition_scan_2.json
#:           7b49b52daec6d40171a9d82d6cfbb10f34130b96e2df43393555f5f5262a39c2
#: It pins the development-MC scan from which the contract's joint partition J was chosen. The delta
#: was enumerated before the constant moved: deleting that one entry reproduces 121 / f447426d
#: exactly (rc 0). Power-tested: flipping the pin's last hex digit makes this file report
#: `MISMATCH docs/orchestration/state/s5c/b1/partition_scan_2.json`, rc 1; then restored.
RECEIPT_BINDING_COUNT = 122
RECEIPT_BINDING_SHA256 = "f5fc1a9edc14d083ad95072c33eb7bae73e189c525a073be58f38ac26ede26b4"


FIELD_PIN_FILE = "docs/orchestration/state/canonical-namespace-field-pins-20260817.json"

# Minimum FIELD pins that must resolve. Same device as the two floors above and for the
# same reason: the pin file is DATA, so a truncation, a bad merge, or a regeneration that
# parsed nothing yields `pins: []`, and a loop over an empty list reports success. Zero
# pins is the state this check exists to make impossible, not a quiet pass.
#
# BELOW the current count on purpose, like RECEIPT_BINDING_FLOOR and unlike
# SHELL_PIN_FLOOR: field pins legitimately SHRINK when a receipt leaves the RECORD-FROZEN
# inventory, and an exact floor would go red on a lane doing the documented right thing,
# whose only remedy would be lowering it. 44 resolve today across 22 receipts; 30 leaves
# room for real retirements while a collector that has gone blind resolves ~0 and trips it.
FIELD_PIN_FLOOR = 30


FIELD_PIN_GENERATOR = "docs/orchestration/state/regen_canonical_namespace_field_pins.py"
# Minimum RECORD-FROZEN JSON entries the coverage parse must find. Without this, a
# reformat of that INVENTORY makes the regex match nothing, the "uncovered receipts" set
# is empty, and the coverage check reports success by seeing no receipts at all -- the
# same shape as the two collector floors above, in the guard that was added to fix that
# shape. 22 parse today; 15 leaves room for legitimate retirement.
FROZEN_JSON_FLOOR = 15


def _pin_rules(root):
    """Load the GENERATOR's rules rather than re-implementing them.

    The first version of the coverage check below re-implemented "does this receipt carry a
    namespace path" as a regex over the raw file, and immediately produced FIVE false
    positives on receipts whose only occurrence is a SENTENCE -- the prose-versus-field
    confusion this whole check exists to fix, reproduced inside it within the hour. Two
    predicates for one concept is exactly what `OI-65` (lane A's) is about; importing makes
    divergence impossible instead of merely unlikely.
    """
    path = os.path.join(root, FIELD_PIN_GENERATOR)
    spec = importlib.util.spec_from_file_location("_cnfp", path)
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def check_field_pins(root):
    """Verify each declared FIELD value still reads as declared. Returns (ok, bad, missing).

    Three distinguishable failures, kept separate because they need different remedies:
      MISMATCH      the field moved -- a repoint. Do NOT regenerate the pin file to match.
      UNRESOLVED    the pointer no longer exists in the receipt (a rename or a deletion).
      NO RECEIPT    the receipt itself is gone.
    A pointer that resolves to a non-string is UNRESOLVED, not a silent skip: `if the key is
    present, check it` is the vacuous form (PB2), and absence is what this check is about.
    """
    pin_path = os.path.join(root, FIELD_PIN_FILE)
    try:
        doc = json.load(open(pin_path))
    except (OSError, json.JSONDecodeError) as e:
        return 0, [(FIELD_PIN_FILE, "", f"pin file unreadable: {e}", "")], 0
    ok, bad, missing = 0, [], 0
    for pin in doc.get("pins", []):
        rel, ptr, want = pin.get("receipt"), pin.get("pointer"), pin.get("expected")
        full = os.path.join(root, rel or "")
        if not rel or not os.path.isfile(full):
            bad.append((rel, "", "NO RECEIPT", want))
            continue
        try:
            node = json.load(open(full))
        except (OSError, json.JSONDecodeError) as e:
            bad.append((rel, "", f"receipt unreadable: {e}", want))
            continue
        cur = node
        for key in ptr or []:
            try:
                cur = cur[key]
            except (KeyError, IndexError, TypeError):
                cur = None
                break
        loc = "/".join(str(x) for x in (ptr or []))
        if not isinstance(cur, str):
            bad.append((rel, loc, "UNRESOLVED", want))
            missing += 1
        elif cur != want:
            bad.append((rel, loc, cur, want))
        else:
            ok += 1
    return ok, bad, missing


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


# OI-127. Role-name prefixes whose UNPAIRED hash plausibly freezes repo CODE rather than a
# data product or a content digest of the receipt itself. This BOUNDS the reported subset; it
# does NOT adjudicate membership, and it is deliberately never used to guess a path. Inferring
# `loader_ -> .../fullevent_fps_dataloader.py` inside the checker would make the guard assert a
# target THE RECEIPT NEVER NAMED and then compare rigorously against the wrong file, which is
# BEN-312 exactly. If a role key is ever to be resolved, the mapping must be declared
# RECEIPT-SIDE and reviewed, never inferred here.
CODE_ROLE_PREFIXES = ("launcher_", "validator_", "script_", "engine_net_", "driver_",
                      "loader_", "preflight_", "runner_", "tool_", "generator_",
                      "module_", "reconciler_", "wrapper_", "adopter_")


def collect(obj, src, out, unpaired=None, revision_pinned=None):
    """Harvest (path, sha256) pairs from the two shapes receipts actually use.

    A PAIR THAT CARRIES A `revision` IS NOT A WORKTREE BINDING and is routed away from `out`.
    `{path, revision, sha256}` pins the digest of a file AT A GIT REVISION -- its readers
    fetch it with `git show <revision>:<path>` and never touch the working tree -- so the
    digest is a property of an immutable git object and comparing it against the checkout is
    a category error. Left in, it would report MISMATCH every time the live file legitimately
    moved on: the first record of this shape to arrive bound `VALIDATION_LEDGER.md`, which
    takes 74 commits in 60 days, so the gate would have gone red daily and for no actionable
    reason -- the OI-123 hazard, a check that cries wolf until nobody reads it.

    THIS NARROWS THE COLLECTOR, so it was measured before it was written rather than argued:
    the tree today contains ZERO pairs carrying a `revision`, and the tracked inventory is 120
    with them counted and 120 with them excluded. Existing coverage loses nothing; every past
    `ALL BINDINGS INTACT` means exactly what it meant. What changes is only what a FUTURE
    revision-pinned record does.
    (Superseded 2026-09-23: "ZERO" was true at `ab341cc4` only. `f71ad116`, a minute later, added
    12 revision-pinned pairs in the Sep-09 talk's measurement tables. Those pairs are now
    reviewed and verified at their own revision by `test_hash_bindings.py`'s
    `test_every_revision_pinned_pair_verifies_at_its_revision`.)

    They are counted and PRINTED rather than dropped, for the reason `unpaired` exists: a
    collector that quietly stops seeing a shape reports ALL BINDINGS INTACT and is indis-
    tinguishable from one that looked.

    OI-127 / BEN-322. A `<role>_sha256` whose dict carries no `<role>`/`<role>_path`/
    `<role>_file` sibling -- and a dict carrying `sha256` with no `path`/`file`/`script` --
    is BOUND TO NOTHING, and it was in NEITHER accounting cell. It never entered `pairs`, so
    it could not be counted as "unresolvable" either: that cell counts only pairs this
    function DID harvest whose path then failed to localize. A reader asking *did it account
    for everything it saw?* got a ledger that balanced while the Gate-5 implementation pins
    were invisible to it. They are now recorded in `unpaired` and PRINTED.

    Purely additive: `out` is unchanged, so `RECEIPT_BINDING_COUNT`/`_SHA256` and every past
    `ALL BINDINGS INTACT` mean exactly what they meant. This is the before/after baseline any
    later widening of this collector needs -- it is NOT that widening, and it is not a fix.
    """
    if isinstance(obj, dict):
        pinned = isinstance(obj.get("revision"), str)
        sink = out if not pinned else (revision_pinned
                                       if revision_pinned is not None else [])
        p = obj.get("path") or obj.get("file") or obj.get("script")
        s = obj.get("sha256") or obj.get("sha")
        if isinstance(s, str) and len(s) == 64:
            if isinstance(p, str):
                sink.append((p, s, src))
            elif unpaired is not None and not pinned:
                unpaired.append(("sha256" if isinstance(obj.get("sha256"), str) else "sha",
                                 src))
        for k, v in obj.items():
            if k.endswith("_sha256") and isinstance(v, str) and len(v) == 64:
                base = k[:-len("_sha256")]
                for cand in (base, base + "_path", base + "_file"):
                    if isinstance(obj.get(cand), str):
                        sink.append((obj[cand], v, src))
                        break
                else:
                    if unpaired is not None and not pinned:
                        unpaired.append((k, src))
        for v in obj.values():
            collect(v, src, out, unpaired, revision_pinned)
    elif isinstance(obj, list):
        for v in obj:
            collect(v, src, out, unpaired, revision_pinned)


# A pin is only credible where it is USED, so pairing is read off the comparison
# line rather than from the constant's name. Both hashing idioms in the tree are
# accepted, and the indirection through a temporary (`g=$(sha_of "$BIN"); [[ "$g"
# == ... ]]`) stays on one line in every current site.
_SHA_OF = re.compile(r'(?:sha_of|sha256sum)\s+"\$\{?(\w+)\}?"')
_PIN_USE = re.compile(r'\$\{?(EXPECTED_[A-Z0-9_]*_SHA)\}?')
_PIN_DEF = re.compile(r'^\s*(EXPECTED_[A-Z0-9_]*_SHA)=["\']?([0-9a-f]{64})["\']?\s*$', re.M)
# A trailing `# comment` is allowed (J12): `sbatch_p3f_pet_fullevent_evloop_array.sh:59-61`
# annotates all three validator paths that way, and anchoring on `\s*$` alone dropped them, so the
# P3F -> domain -> base validator pins were defined, used, and never walked.
_VAR_DEF = re.compile(r'^\s*(\w+)=["\']?([^"\'\s|;]+)["\']?(?:\s+#[^\n]*)?\s*$', re.M)


def _expand(value, env, depth=0):
    """Resolve ${REPO}/... style assignments against the script's own constants."""
    if depth > 5:
        return value
    out = re.sub(r'\$\{(\w+)\}|\$(\w+)',
                 lambda m: env.get(m.group(1) or m.group(2), m.group(0)), value)
    return _expand(out, env, depth + 1) if out != value else out


def collect_shell(text, src, out, unwalked=None):
    """Harvest (path, sha256, src) from `EXPECTED_*_SHA` guards in a shell script.

    `unwalked`, if given, receives `(src, NAME)` for every `EXPECTED_*_SHA` DEFINED here that no
    comparison line paired to a file. The shell floor cannot see such a pin -- both sides of its
    ratio come from this parser -- so the definition count is the independent side (J12).
    """
    pins = dict(_PIN_DEF.findall(text))
    if not pins:
        return
    paired = set()
    env = {k: v for k, v in _VAR_DEF.findall(text) if not k.startswith("EXPECTED_")}
    for line in text.splitlines():
        # Deduped, because the guards restate both operands in their failure text
        # (`[[ "$g" == "$EXPECTED_BIN_SHA" ]] || die "drift: $g != $EXPECTED_BIN_SHA"`).
        # Counting raw occurrences reads that as two pins and drops the line, which
        # silently cost the entire evloop launcher family on the first pass -- the
        # collector reported a clean 6 while walking none of them.
        files, used = set(_SHA_OF.findall(line)), set(_PIN_USE.findall(line))
        # One file against one pin is what a real comparison looks like. Anything
        # else is an echo, an argv splat, or a self-comparison of two staged
        # copies -- none of which bind a pin to a file.
        if len(files) != 1 or len(used) != 1 or not used <= set(pins):
            continue
        target = _expand(env.get(next(iter(files)), ""), env)
        if target:
            out.append((target, pins[next(iter(used))], src))
            paired.add(next(iter(used)))
    if unwalked is not None:
        unwalked.extend((src, name) for name in sorted(set(pins) - paired))


# PYTHON PINS (J14). A module-level `NAME = "<64 hex>"` is a pin only where it is COMPARED against
# the digest of a file the source names, so pairing is read off the comparison, as for shell:
#     sha256(repo / "nd-unfolding/pet/x.py") == NAME        (either side, `==` or `!=`)
#     d = sha256(repo / "nd-unfolding/pet/x.py"); ... d != NAME   (one hop, same scope)
# The hashing call is any call whose function name contains `sha`; the path is the LAST string
# literal inside its first argument, which covers `repo / "p"`, `os.path.join(ROOT, "p")`,
# `Path("p")` and a bare `"p"`. A pin compared against a runtime argument or a receipt field names
# no file here and is reported as unwalked, never guessed.
_HEX64 = re.compile(r'^[0-9a-f]{64}$')


def _py_hash_target(node):
    if not isinstance(node, ast.Call) or not node.args:
        return None
    fn = node.func
    name = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", "")
    if "sha" not in name.lower():
        return None
    lits = [n.value for n in ast.walk(node.args[0])
            if isinstance(n, ast.Constant) and isinstance(n.value, str)]
    lits = [s for s in lits if "/" in s or "." in s]
    return lits[-1] if lits else None


def collect_python(text, src, out, unwalked=None):
    """Harvest (path, sha256, src) from module-level 64-hex constants compared to a file digest."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return
    pins = {}
    for node in tree.body:
        targets = (node.targets if isinstance(node, ast.Assign)
                   else [node.target] if isinstance(node, ast.AnnAssign) else [])
        v = getattr(node, "value", None)
        if isinstance(v, ast.Constant) and isinstance(v.value, str) and _HEX64.match(v.value):
            for t in targets:
                if isinstance(t, ast.Name):
                    pins[t.id] = v.value
    if not pins:
        return
    scopes = [tree] + [n for n in ast.walk(tree)
                       if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    paired, seen = set(), set()
    for scope in scopes:
        local = {}
        for n in ast.walk(scope):
            if (isinstance(n, ast.Assign) and len(n.targets) == 1
                    and isinstance(n.targets[0], ast.Name)):
                t = _py_hash_target(n.value)
                if t:
                    local[n.targets[0].id] = t
        for n in ast.walk(scope):
            if not isinstance(n, ast.Compare) or len(n.ops) != 1 \
                    or not isinstance(n.ops[0], (ast.Eq, ast.NotEq)):
                continue
            a, b = n.left, n.comparators[0]
            for pin_side, other in ((a, b), (b, a)):
                if not (isinstance(pin_side, ast.Name) and pin_side.id in pins):
                    continue
                target = _py_hash_target(other)
                if target is None and isinstance(other, ast.Name):
                    target = local.get(other.id)
                if target and (target, pin_side.id) not in seen:
                    seen.add((target, pin_side.id))
                    out.append((target, pins[pin_side.id], src))
                    paired.add(pin_side.id)
    if unwalked is not None:
        unwalked.extend((src, name) for name in sorted(set(pins) - paired))


def localize(p, root):
    if p.startswith(PERLMUTTER_ROOT):
        p = p[len(PERLMUTTER_ROOT):]
    cand = os.path.join(root, p.lstrip("/"))
    return cand if os.path.isfile(cand) else None


def fixture_integrity(root, fixture_files):
    """OI-143a. `(count, digest, problems)` over the SELF-DECLARED fixtures.

    Held out of the production verdict is NOT unchecked. A fixture's whole job can be to carry a
    value the world contradicts -- `std_component_manifest.B1_E.json` pins a deliberately dead
    digest and `test_p4_repair.py` requires it to be REJECTED -- so asserting that its digests match
    live artifacts is exactly wrong. What CAN be asserted is that the fixture set has not changed
    under us: the file list and each file's own sha256. That catches a silent edit, which is the real
    risk once these stop entering the main verdict.
    """
    rows = []
    for rel in sorted(fixture_files):
        h = hashlib.sha256()
        try:
            with open(os.path.join(root, rel), "rb") as fh:
                for chunk in iter(lambda: fh.read(1 << 20), b""):
                    h.update(chunk)
        except OSError as e:
            return len(fixture_files), None, [f"{rel}: unreadable ({e})"]
        rows.append(f"{rel} {h.hexdigest()}")
    digest = hashlib.sha256(("\n".join(rows) + "\n").encode()).hexdigest()
    problems = []
    if len(rows) != FIXTURE_COUNT:
        problems.append(
            f"self-declared fixture count is {len(rows)}, pinned at {FIXTURE_COUNT}. A fixture "
            f"appearing or vanishing changes what the production verdict does NOT cover, so it is "
            f"a deliberate change: update FIXTURE_COUNT/FIXTURE_SET_SHA256 with the reason.")
    if FIXTURE_SET_SHA256 != "PENDING" and digest != FIXTURE_SET_SHA256:
        problems.append(
            f"self-declared fixture set digest is {digest}, pinned {FIXTURE_SET_SHA256}. One of the "
            f"held-out fixtures was EDITED. These are negative controls; an edit is how a control "
            f"stops controlling.")
    return len(rows), digest, problems


def tracked_paths(root):
    """Checkout-relative paths git actually tracks at `root`.

    OI-70. The inventory below claims to describe COMMITTED REPOSITORY INVENTORY, but
    `localize()` answers a question about the FILESYSTEM: it resolves any path that
    happens to exist. Those are not the same question, and the gap is not hypothetical.
    Receipts bind data products as well as code, and data products are gitignored
    (`.gitignore` carries a bare `*.npz`), so a bound artifact sitting untracked in a
    working tree silently ADDS a live binding and trips the identity check -- while the
    same commit is green in a clean checkout. Measured 2026-08-20: 320 receipt-bound
    paths are gitignored, so on Perlmutter, where those products actually exist, this
    gate was systematically red for reasons that had nothing to do with any edit.

    Restricting the INVENTORY to tracked paths makes the constant a property of the
    commit rather than of whoever's disk it ran on. It is deliberately not applied to
    verification: an untracked-but-present bound file is still hashed and still reported
    below, so this narrows what counts as inventory without reducing what gets checked.

    Fails closed. A non-repository `--root`, or any git failure, raises rather than
    returning an empty set -- an empty tracked set would silently drop every binding and
    render the inventory 0/e3b0c442..., which is precisely the quiet pass this file
    exists to make impossible.
    """
    r = subprocess.run(["git", "-C", root, "ls-files", "-z"],
                       capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(
            f"cannot enumerate tracked files under {root!r} (git exited "
            f"{r.returncode}): {r.stderr.decode('utf-8', 'replace').strip()}. "
            "The receipt-binding inventory is defined over committed content, so it "
            "cannot be computed here; run the verifier inside the checkout.")
    names = [n for n in r.stdout.decode("utf-8", "surrogateescape").split("\0") if n]
    if not names:
        raise RuntimeError(
            f"git reports ZERO tracked files under {root!r}. Refusing to compute an "
            "inventory that would be empty by construction.")
    return set(names)


def receipt_inventory(pairs, root, tracked):
    """Return the canonical resolved receipt-binding rows and their digest.

    Only TRACKED bound paths are inventoried; see `tracked_paths` for why.
    """
    rows = sorted({(rel, want)
                   for p, want, _src in pairs
                   for lp in [localize(p, root)] if lp is not None
                   for rel in [os.path.relpath(lp, root)] if rel in tracked})
    payload = "".join(f"{rel}\t{want}\n" for rel, want in rows).encode("utf-8")
    return rows, hashlib.sha256(payload).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))))
    ap.add_argument("--strict", action="store_true",
                    help="also fail on the known pre-existing drift")
    a = ap.parse_args()

    receipt_pairs = []
    receipt_unpaired = []
    receipt_revision_pinned = []
    fixture_pairs = []
    fixture_files = []
    for f in (glob.glob(os.path.join(a.root, "docs/**/*.json"), recursive=True)
              + glob.glob(os.path.join(a.root, "nd-unfolding/**/*.json"), recursive=True)):
        try:
            doc = json.load(open(f))
        except (json.JSONDecodeError, OSError):
            continue
        rel = os.path.relpath(f, a.root)
        # OI-143a: a SELF-DECLARED fixture's bindings do not enter the production verdict.
        if isinstance(doc, dict) and NEGATIVE_CONTROL_MARKER in doc:
            fixture_files.append(rel)
            collect(doc, rel, fixture_pairs, None)
            continue
        try:
            collect(doc, rel, receipt_pairs, receipt_unpaired, receipt_revision_pinned)
        except OSError:
            continue

    shell_pairs, shell_unwalked = [], []
    for f in (glob.glob(os.path.join(a.root, "docs/**/*.sh"), recursive=True)
              + glob.glob(os.path.join(a.root, "nd-unfolding/**/*.sh"), recursive=True)
              + glob.glob(os.path.join(a.root, "2d-unfolding/**/*.sh"), recursive=True)):
        try:
            collect_shell(open(f).read(), os.path.relpath(f, a.root), shell_pairs,
                          shell_unwalked)
        except OSError:
            continue
    py_pairs, py_unwalked = [], []
    for f in py_files(a.root):
        try:
            collect_python(open(f).read(), os.path.relpath(f, a.root), py_pairs, py_unwalked)
        except (OSError, UnicodeDecodeError):
            continue
    pairs = receipt_pairs + shell_pairs + py_pairs

    seen, ok, new_bad, known_bad, unresolved = set(), 0, [], [], 0
    receipt_resolved = 0
    for p, want, src in pairs:
        lp = localize(p, a.root)
        if lp is None:
            unresolved += 1
            continue
        rel = os.path.relpath(lp, a.root)
        # Receipts that pin the same file to the same hash are deduped as noise,
        # but a shell pin is a SEPARATE remediation site: repairing the receipt
        # leaves the launcher's constant stale, and collapsing them would hide
        # exactly that. Dedupe within a source kind, never across.
        # ...and never across shell SITES either: two launchers pinning the same
        # runner are two constants to edit, so collapsing them hides half the
        # remediation. Receipts still dedupe, where repeats are genuinely noise.
        code_site = src.endswith((".sh", ".py"))
        key = (rel, want, src if code_site else "")
        if key in seen:
            continue
        seen.add(key)
        if not code_site:
            receipt_resolved += 1
        if sha256(lp) == want:
            ok += 1
        elif (rel, src, want) in KNOWN_PREEXISTING:
            known_bad.append((rel, src, want))
        else:
            new_bad.append((rel, want, sha256(lp), src))
    # J11: the expected-red set is EXACT. An exemption that no longer drifts is a dead waiver.
    stale_exemptions = sorted(KNOWN_PREEXISTING - set(known_bad))
    # J12: every DEFINED shell pin must be paired, or be in the declared unwalked set.
    unwalked_now = set(shell_unwalked)
    unwalked_new = sorted(unwalked_now - SHELL_UNWALKED_PINS)
    unwalked_gone = sorted(SHELL_UNWALKED_PINS - unwalked_now)

    # The shell collector parses source rather than reading a schema, so it can go
    # blind if the launchers change idiom -- and a collector that silently matches
    # nothing reports ALL BINDINGS INTACT, which is the failure mode this whole
    # file exists to catch. Resolving zero shell pins is therefore an error, not a
    # quiet zero. The floor is deliberately the count that exists today.
    shell_resolved = sum(1 for p, _, _ in shell_pairs if localize(p, a.root))
    blind = shell_resolved < SHELL_PIN_FLOOR
    py_resolved = sum(1 for p, _, _ in py_pairs if localize(p, a.root))
    py_blind = py_resolved < PY_PIN_FLOOR

    # Identity, not a scalar floor: a floor catches collapse but permits erosion.
    # Derive this from receipt_pairs only; shell pins are separate remediation sites.
    receipt_rows, receipt_digest = receipt_inventory(
        receipt_pairs, a.root, tracked_paths(a.root))
    receipt_inventory_changed = (
        len(receipt_rows) != RECEIPT_BINDING_COUNT
        or receipt_digest != RECEIPT_BINDING_SHA256
    )

    print(f"resolved {ok + len(new_bad) + len(known_bad)} bindings "
          f"({unresolved} unresolvable: data files, off-repo artifacts, binaries)")
    # OI-127, THE THIRD CELL. Neither number above can see a hash that names no file. Role-keyed
    # pins never enter `pairs`, so they were not "resolved" and could not become "unresolvable"
    # either, and the two-cell ledger BALANCED while `gate5-target-array-active-56857232`'s whole
    # `implementation` block was invisible to it. Printed and NOT gated: no floor, no exit-code
    # contribution, nothing about what is verified changes -- so this reclassifies no past
    # `ALL BINDINGS INTACT`. The achievable goal is that the output stop implying a coverage it
    # never had; historical coverage of immutable, largely terminal receipts is UNRECOVERABLE.
    # NOT MEASURED HERE, and left explicit rather than silent: `collect_shell()` was not examined
    # for the same hole, so this cell speaks only for the receipt-side collector.
    _code_unpaired = [(k, s) for k, s in receipt_unpaired if k.startswith(CODE_ROLE_PREFIXES)]
    print(f"  {len(receipt_unpaired)} receipt hash keys are UNPAIRED across "
          f"{len({s for _, s in receipt_unpaired})} receipts -- a `<role>_sha256` with no "
          f"sibling path key, so they name no file, are in NEITHER cell above, and were "
          f"never compared against anything")
    print(f"    {len(_code_unpaired)} of those, across "
          f"{len({s for _, s in _code_unpaired})} receipts, carry a role name that denotes "
          f"repo CODE: {', '.join(sorted({k for k, _ in _code_unpaired}))}")
    print("    this is COVERAGE, not drift: no binding is shown broken. Resolving a role key "
          "needs a RECEIPT-SIDE declared mapping, never one inferred here (BEN-312)")
    # PRINTED EVEN AT ZERO, because the point of the line is that a reader can tell a
    # collector that saw none from one that stopped looking. Same reasoning as `unpaired`.
    print(f"  {len(receipt_revision_pinned)} pair(s) across "
          f"{len({s for _, _, s in receipt_revision_pinned})} receipt(s) carry a `revision` "
          f"and were NOT compared against the worktree: they pin a git object, which "
          f"`git show <revision>:<path>` reads and the checkout cannot contradict")
    print(f"  {ok} OK")
    print(f"  {shell_resolved} of them from EXPECTED_*_SHA guards in *.sh "
          f"({len(shell_pairs)} pins seen, floor {SHELL_PIN_FLOOR}; "
          f"{len(shell_unwalked)} defined but unpaired, declared {len(SHELL_UNWALKED_PINS)})")
    print(f"  {py_resolved} of them from 64-hex pin constants in *.py "
          f"({len(py_pairs)} pins seen, floor {PY_PIN_FLOOR}; {len(py_unwalked)} module-level "
          f"64-hex constants compared to no file digest -- printed, not gated)")
    # These two numbers are DIFFERENT QUESTIONS and may legitimately differ: the first
    # is how many bound files were hashed, the second is how many of those are tracked
    # and therefore inventoried (OI-70). An untracked bound product present on disk is
    # verified but not inventoried, so `verified > inventory` means exactly that -- it is
    # not a discrepancy. Printed with the gap named so nobody reads it as one.
    _untracked_verified = receipt_resolved - len(receipt_rows)
    print(f"  {receipt_resolved} of them from receipt bindings "
          f"(inventory {len(receipt_rows)} tracked, sha256 {receipt_digest}"
          + (f"; {_untracked_verified} verified but untracked, so not inventoried"
             if _untracked_verified else "") + ")")

    field_ok, field_bad, _field_missing = check_field_pins(a.root)
    field_blind = (field_ok + len(field_bad)) < FIELD_PIN_FLOOR

    # COVERAGE, not just correctness. A receipt ADDED to the RECORD-FROZEN inventory and
    # never pinned is invisible to the loop above -- it checks the pins it has, so
    # under-coverage reports as a clean pass. That is BEN-322's shape reproduced inside the
    # guard written to fix it, so it is checked rather than trusted.
    rules = _pin_rules(a.root)
    frozen = rules.frozen_json_receipts(a.root) if rules else []
    try:
        covered = {p.get("receipt") for p in json.load(
            open(os.path.join(a.root, FIELD_PIN_FILE))).get("pins", [])}
    except (OSError, json.JSONDecodeError):
        covered = set()
    # A receipt with NO namespace path FIELD legitimately contributes no pins, so absence
    # from `covered` is a defect only for receipts that DO carry one -- re-derived with the
    # generator's own rule, not with a cheaper proxy.
    uncovered = []
    for rel in frozen:
        full = os.path.join(a.root, rel)
        if rel in covered or not os.path.isfile(full):
            continue
        try:
            if rules.namespace_path_fields(json.load(open(full))):
                uncovered.append(rel)
        except (OSError, json.JSONDecodeError):
            continue
    frozen_blind = len(frozen) < FROZEN_JSON_FLOOR

    print(f"{field_ok} canonical-namespace FIELD pins verified "
          f"(floor {FIELD_PIN_FLOOR}) over {len(covered)} of {len(frozen)} RECORD-FROZEN "
          f"JSON receipts -- these pin a POINTER, not bytes; "
          f"green says the receipts still point where they pointed")
    if frozen_blind:
        print(f"\n*** RECORD-FROZEN INVENTORY PARSE WENT BLIND ***\n"
              f"  parsed {len(frozen)} JSON entries from {DESIGNATION_INVENTORY}, expected\n"
              f"  at least {FROZEN_JSON_FLOOR}. The label or its formatting changed, and an\n"
              f"  empty parse makes the coverage check below pass by seeing nothing.")
    if uncovered:
        print("\n*** RECORD-FROZEN RECEIPTS CARRY NAMESPACE PATHS AND ARE NOT PINNED ***")
        for rel in uncovered:
            print(f"      {rel}")
        print("  Regenerate with state/regen_canonical_namespace_field_pins.py -- this is\n"
              "  the ONE case where regenerating is the correct remedy, because the pin set\n"
              "  grew. It is NOT the remedy for a FIELD PIN mismatch below.")
    if field_blind:
        print(f"\n*** FIELD PIN COLLECTOR WENT BLIND ***\n"
              f"  saw {field_ok + len(field_bad)}, expected at least {FIELD_PIN_FLOOR}.\n"
              f"  The pin file is data: a truncation or a regeneration that parsed nothing\n"
              f"  yields an empty list, and a loop over it reports success. Do NOT lower\n"
              f"  this floor -- regenerate only for a real inventory change (OI-96).")
    for rel, loc, got, want in field_bad:
        print(f"\nFIELD PIN {rel}  {loc}\n  want {want}\n  got  {got}\n"
              f"  A repoint is NOT repaired by regenerating the pin file -- that adopts\n"
              f"  whatever the receipt now says, which is this file's own forbidden move\n"
              f"  one level out. Re-issue the receipt, or justify the move in the commit.")
    if receipt_inventory_changed:
        print(f"\n*** RECEIPT BINDING INVENTORY CHANGED ***\n"
              f"  expected {RECEIPT_BINDING_COUNT} bindings / {RECEIPT_BINDING_SHA256}\n"
              f"  observed {len(receipt_rows)} bindings / {receipt_digest}\n"
              f"  A live binding was added, removed, or repointed, or collect() no longer\n"
              f"  sees its shape. Do not update these constants merely to make this pass;\n"
              f"  inspect the inventory delta and review it with the owning receipt change.\n"
              f"  Pre-freeze retired receipts remain at evidence/prepublication-2026-08-20-0b329e8a.")
    if blind:
        print(f"\n*** SHELL PIN COLLECTOR WENT BLIND ***\n"
              f"  resolved {shell_resolved}, expected at least {SHELL_PIN_FLOOR}.\n"
              f"  Either pins were deleted, or a launcher changed hashing idiom and\n"
              f"  the parser no longer sees its guards. Do NOT lower the floor to\n"
              f"  make this pass -- an unwalked pin is how the Gate-2 pair went stale.")
    if py_blind:
        print(f"\n*** PYTHON PIN COLLECTOR WENT BLIND ***\n"
              f"  resolved {py_resolved}, expected at least {PY_PIN_FLOOR}.\n"
              f"  Either pins were deleted, or a module changed hashing idiom and\n"
              f"  collect_python no longer sees its comparison. Do NOT lower the floor.")
    for src, name in unwalked_new:
        print(f"\nUNWALKED SHELL PIN {name} in {src}\n"
              f"  defined, but no single comparison line pairs it to a file, so nothing here\n"
              f"  can tell when it goes stale. Use the one-line idiom\n"
              f"  `[[ \"$(sha_of \"$VAR\")\" == \"$EXPECTED_X_SHA\" ]]`, or declare it in\n"
              f"  SHELL_UNWALKED_PINS with the reason.")
    for src, name in unwalked_gone:
        print(f"\nDECLARED-UNWALKED SHELL PIN {name} in {src} is no longer unwalked\n"
              f"  (now paired, renamed, or deleted). Remove it from SHELL_UNWALKED_PINS.")
    if known_bad:
        print(f"  {len(known_bad)} known pre-existing drift (submit-time provenance):")
        for rel, src, _want in known_bad:
            print(f"      {rel}  <- {os.path.basename(src)}")
    for rel, src, want in stale_exemptions:
        print(f"\nSTALE EXEMPTION {rel}  <- {src}\n  want {want}\n"
              f"  KNOWN_PREEXISTING waives this drift, and it is no longer observed (the file\n"
              f"  now matches, or no live binding names it). Remove the entry.")
    for rel, want, got, src in new_bad:
        print(f"\nMISMATCH {rel}\n  want {want}\n  got  {got}\n  from {src}")

    failed = (bool(new_bad) or blind or py_blind or receipt_inventory_changed
              or bool(stale_exemptions) or bool(unwalked_new) or bool(unwalked_gone)
              or bool(field_bad) or field_blind
              or bool(uncovered) or frozen_blind
              or (a.strict and bool(known_bad)))
    # OI-143a: what the production verdict deliberately does NOT cover, and its own integrity.
    fx_n, fx_digest, fx_problems = fixture_integrity(a.root, fixture_files)
    print(f"\n{len(fixture_pairs)} binding(s) in {fx_n} SELF-DECLARED fixture(s) held out of the "
          f"production verdict (semantic `{NEGATIVE_CONTROL_MARKER}` marker, not a path rule)")
    print(f"  fixture-set integrity digest: {fx_digest}")
    print("  these pin values the world may CONTRADICT on purpose; their integrity is the set and "
          "each file's own sha256, never a match against a live artifact")
    for pb in fx_problems:
        print(f"  FIXTURE-INTEGRITY FAIL {pb}")
    failed = failed or bool(fx_problems)

    print("\n" + ("*** BINDINGS BROKEN ***" if failed else "ALL BINDINGS INTACT"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
