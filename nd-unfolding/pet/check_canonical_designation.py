#!/usr/bin/env python3
"""Fail-closed postcondition for the canonical-nominal DESIGNATION: every reference is accounted for.

WHY THIS EXISTS. Promoting a full-event PET nominal by DESIGNATION (rather than by moving bytes -- see
BEN-133 for why moving is unsafe here) means the string `fullevent_nominal` stops being a synonym for
"canonical". The safety of that choice rests entirely on the reference inventory being COMPLETE: a
consumer nobody retargeted keeps reading the old artifact under a name that now means something else,
which is the same silent defect the designation was chosen to avoid, one level up.

So this asserts completeness, not existence (BEN-023): every occurrence in the tree must appear in the
inventory below with an explicit disposition, and every inventory entry must still match something.

THE MATCHING IS THE HARD PART, AND A NAIVE GREP IS WRONG THREE WAYS. Measured 2026-08-11: the bare
string `fullevent_nominal` returns 78 hits in tracked .py/.sh, of which only 27 are the artifact
namespace.

  CLASS 1  literal slash-joined path      "fullevent_nominal/pet_fullevent_nominal_weights.npz"  # NS-EXEMPT: pattern literal, not a reference
  CLASS 2  segmented os.path.join         os.path.join(HERE, "fullevent_nominal", "pet_...npz")  # NS-EXEMPT: pattern literal, not a reference
           -- invisible to a class-1 grep, and it is where the two sites the first inventory
              DROPPED were hiding
  CLASS 3  shell composition across LINES OUT=".../fullevent_nominal" then NOM="${OUT}/pet_...npz"  # NS-EXEMPT: pattern literal, not a reference
           -- invisible to both of the above
  CLASS 4  FALSE POSITIVES, and the reason a broad exclusion is dangerous: `train_fullevent_nominal.py`,
           `sbatch_pet_fullevent_nominal.sh` and `test_pet_fullevent_nominal_launcher.py` all CONTAIN
           the namespace string in their own FILENAMES. 51 of the 78 hits are these. The tempting fix --
           a wide exclusion -- is exactly what would hide a real site.

  And the trap that bit an unrelated guard earlier the same night: **`fullevent_nominal_annealed`
  contains `fullevent_nominal`**, so the DESTINATION directory matches any naive pattern for the
  SOURCE. Excluded explicitly and covered by a negative control.

The pattern therefore matches the namespace as a PATH SEGMENT -- `fullevent_nominal` followed by `/`,
`"` or `'` -- with `_annealed` excluded and the three filenames excluded by name rather than by a
blanket rule.

CORPUS, STATED because the postcondition is only as broad as what it reads. `_tracked()` is
`git ls-files` over ALL tracked files (widened 2026-08-12 from `*.py`/`*.sh`). Untracked files, and
anything outside the git index, are NOT scanned. D's objection is the reason this line exists and it
was fair: a file whose entire subject is that implicit exclusions hide real sites was carrying an
implicit exclusion in its own corpus definition, while claiming "every occurrence in the tree".

CLASS 6 -- A MENTION IS NOT A CONSUMER, AND UNTIL 2026-08-15 THIS TOOL COULD NOT TELL THEM APART.
Diagnosed read-only by the propagation-correction lane as BEN-325, fixed here by lane C (the owner) as
BEN-237. The instrument was EXHAUSTIVE, HONEST AND UNRANKED: every occurrence was reported and a new
FINDING file mentioning the namespace failed RED identically to a new script opening it. Measured at
`6f9c67d^`: 74 files, 216 occurrences, 20 UNACCOUNTED. Measured at `a764a72`: 75 / 221 / 21 -- and the
whole delta is the commit that FILED BEN-325. Documenting the namespace turned its own guard redder,
which is why this sat RED from the 2026-08-13 designation instead of being fixed in an hour.

So occurrences are now classified, and PRESENCE IN THE INVENTORY IS REQUIRED ONLY OF OPERANDS:

  OPERAND    the match is in live code, so this file could open that path
  NARRATIVE  the match is in a comment, a docstring, or a non-code file -- it cannot open anything

  .py    tokenize for COMMENT spans, ast for docstring spans, both compared BY COLUMN so a trailing
         `# ...` on a real assignment does not launder the assignment
  .sh    a line whose first non-whitespace char is `#` is narrative -- EXCEPT `#SBATCH`, which is a
         comment to bash and a DIRECTIVE to Slurm, and `sbatch_pet_fullevent_nominal.sh:12,:13` are
         genuine namespace sites living in exactly that form
  data   .json .md .tsv .txt -- nothing in them executes; their READER is code that must match on its
         own line. (The extension list is grounded in a measurement, not guessed: the found set at
         `a764a72` is .json 28, .md 19, .py 13, .sh 12, .tsv 2, .txt 1, and zero extensionless files.)
  else   OPERAND. Unknown extension, unparseable Python, tokenizer error -- every one FAILS CLOSED,
         because misreading an operand as narrative HIDES A CONSUMER while the converse merely asks
         for a disposition that costs one line.

WHAT A GREEN RUN NOW CLAIMS, AND IT IS NARROWER THAN BEFORE -- state it rather than inherit it.
It claims: every occurrence IN CODE THAT COULD OPEN THE PATH has an explicit disposition, and every
inventory entry still matches something. It NO LONGER claims "every occurrence in the tree has a
disposition". Narrative-only unlisted files are COUNTED AND PRINTED on every run, never silent, so the
weakening is visible in the output and not only here. Every pre-existing INVENTORY entry keeps the
behaviour it had -- counts still enforced where they were enforced -- so no protection that existed on
2026-08-14 was given away; what changed is that NEW narrative-only files no longer have to be
hand-registered. The cost is stated in CLASS 5 below: a path literal in a NEW data file is no longer
demanded of the inventory, which widens an exposure that was already declared unfixable-by-grep.
A `state/*.json` pin belongs in verify_hash_bindings.py (BEN-322's territory), not in a path grep.

CLASS 5 -- WHAT NO SOURCE-TEXT MATCHER OVER ANY CORPUS CAN SEE, and it is not hypothetical.
The namespace also arrives from a DATA FILE at run time. `train_fullevent_nominal.py:529,534` stamps
`weights_folder` and `step2_checkpoint` as ABSOLUTE paths into the artifact's own
`inference_contract`, and `extract_fullevent_fps.py:243` reads `contract["step2_checkpoint"]` and
`:253` calls `model.load_weights(ckpt)`. The literal is WRITTEN at training time and READ BACK at
inference time, so it exists in no source file and this tool is blind to it by construction -- not by
an exclusion that could be removed. That is exactly the defect filed as **BEN-133**, where a moved
artifact's contract silently resolved to a DIFFERENT estimator's checkpoints; see also
`nd-unfolding/pet/fullevent_nominal/superseded-20260806/NOTE.md`, which documents a live instance.  # NS-EXEMPT: pattern literal, not a reference
Note the consumer above is the EXTRACTION path -- the operation prohibited without authorization.
A green run here says nothing about class 5. The mitigation for class 5 is a runtime identity guard
(assert the artifact's own fold-forward before use), not a grep.

Usage:
  python3 check_canonical_designation.py            # audit; exit 1 on any unaccounted occurrence
  python3 check_canonical_designation.py --self-test
  python3 check_canonical_designation.py --list     # print what was found, grouped
"""
import argparse
import ast
import io
import os
import re
import subprocess
import sys
import tokenize

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_HERE))

# The namespace as a path segment.
#
# The lookBEHINDs were added after the first version FAILED ON ITSELF, and that is the best evidence in
# this file that the class-4 exclusion had to be per-OCCURRENCE and not per-FILE. Excluding files whose
# NAME contains the namespace is not enough: a module name appears as a STRING inside unrelated files
# too -- `mods = {"train_fullevent_nominal": T}` at sbatch_step1_trajectory_annealed.sh:93 is
# `fullevent_nominal` followed by a quote, in a file that is not a class-4 filename. The audit reported
# it as COUNT DRIFT on its first real run against the tree, which is the check working.
#
# lookAHEAD  requires a path/quote boundary, so the bare token in prose does not match
# lookBEHINDs reject the three module-name prefixes wherever they appear
# `_annealed`  keeps the DESTINATION directory out; it contains the source name as a substring
NS = re.compile(r'(?<!train_)(?<!sbatch_pet_)(?<!test_pet_)'
                r'fullevent_nominal(?!_annealed)(?=["\'/])')

# NO FILE-LEVEL EXCLUSIONS. There were two and both were the implicit-exclusion defect this tool
# exists to object to:
#   * a FILENAME_FALSE_POSITIVES skip, which discarded `sbatch_pet_fullevent_nominal.sh` WHOLESALE --
#     and that file holds FOUR genuine namespace sites (:12, :13 log paths; :46 OUTDIR; :96 the guard).
#     Its own name matching class 4 is no reason to stop reading it.
#   * a blanket `nd-unfolding/tests/` skip, which hid `test_pet_diagnostic_quarantine.py:56` -- the TEST
#     for the one site flagged for decision, encoding the same assumption as its code.
# Class 4 is handled per-OCCURRENCE by the lookbehinds in NS, which is where it belongs. The only
# exclusions left are line-level NS-EXEMPT markers, and those are counted and REPORTED.

# --- THE INVENTORY -------------------------------------------------------------------------------
# path -> (disposition, expected_occurrences). Dispositions are decisions and are written down as
# such; "STAYS" is not the absence of a decision.
#
#   RETARGET      follows canonical; updated at designation
#   STAYS-DIAG08  a diagnostic OF the 2026-08-08 artifact; retargeting it would silently change what
#                 the diagnostic measures while its name stayed the same
#   STAYS-PINNED  already names a specific historical artifact
#   STAYS-REF     the annealed validation's REFERENCE nominal; retargeting makes it self-comparing
#   STAYS-PROD    producer / output namespace / log dir -- a write, not a read of the artifact
#   STAYS-NAME    asserts the directory NAME, does not consume the artifact
#   STAYS-ANNEALED  added 2026-08-15 (BEN-237). Consumes the ANNEALED arm; every `fullevent_nominal/`
#                 occurrence is documentary. NOT the same claim as STAYS-DIAG08, which says the file
#                 reads the 08-08 artifact -- this one says it does NOT, and a future occurrence here
#                 would be the sibling-directory trap rather than a diagnostic's intent.
#   RECORD-APPEND files designed to ACCRUE (run logs, FINDINGS, OPEN_ITEMS, INDEX-*, FINDING-*).
#                 Count UNENFORCED; presence still enforced.
#   RECORD-FROZEN per-job artifacts written once. Count ENFORCED: a frozen receipt cannot cry wolf,
#                 so enforcement costs nothing and catches a committed receipt's content changing --
#                 BEN-091's dangling-pin class and BEN-133's repoint class, both live in this
#                 namespace. STEP1_DECOMPOSITION.slurm-56445883.json is json.load'ed at
#                 step1_increment_trajectory.py:120 as a gated run's reproduction anchor.
#   RECORD        (retired label; split into the two above 2026-08-12 on D's finding)
INVENTORY = {

    "nd-unfolding/pet/inversion_screen.py":                        ("STAYS-DIAG08", 1),
    "nd-unfolding/pet/push_vs_acceptance.py":                      ("STAYS-DIAG08", 1),
    "nd-unfolding/pet/leg_mismatch.py":                            ("STAYS-DIAG08", 1),
    "nd-unfolding/pet/sbatch_designA_diagnostic_reproduction.sh":  ("STAYS-DIAG08", 1),
    "nd-unfolding/pet/interactive_step1_trajectory_controller.sh": ("STAYS-DIAG08", 1),
    "nd-unfolding/pet/sbatch_step1_trajectory_annealed.sh":        ("STAYS-DIAG08", 1),

    "nd-unfolding/pet/preflight_final_checkpoint_save.py":         ("STAYS-PINNED", 1),

    "nd-unfolding/pet/sbatch_annealed_shape_validation.sh":        ("STAYS-REF", 1),
    "nd-unfolding/pet/sbatch_finalize_annealed_shape_validation.sh": ("STAYS-REF", 1),

    # extraction and cross section are PROHIBITED without authorization; these are pinned to the
    # already-quarantined 08-08 artifact and must not acquire a newly-canonical one by default.
    "nd-unfolding/pet/sbatch_fullevent_diagnostic_extract.sh":     ("STAYS-DIAG08", 1),
    "nd-unfolding/pet/sbatch_fullevent_diagnostic_xsec_resume.sh": ("STAYS-DIAG08", 1),

    "nd-unfolding/pet/sbatch_step1_trajectory.sh":                 ("STAYS-PROD", 7),
    "docs/orchestration/notify_nominal.sh":                        ("STAYS-PROD", 1),

    "nd-unfolding/pet/pet_diagnostic_quarantine.py":               ("STAYS-NAME", 1),

    # --- surfaced only after the two blanket exclusions were removed -----------------------------
    # The producer, whose own FILENAME matches class 4 and which the old file-level skip therefore
    # discarded wholesale. :12,:13 are #SBATCH log paths, :46 is OUTDIR, :96 is the `|| die` namespace
    # guard. Producer output location and canonical designation are DECOUPLED and recorded in the
    # registry rather than retargeted -- the no-clobber guard and :96 are what stopped job 56563092
    # from destroying a baseline.
    "nd-unfolding/pet/sbatch_pet_fullevent_nominal.sh":            ("STAYS-PROD", 4),

    # Swallowed by the SAME prefix skip, because `sbatch_pet_fullevent_nominal` is a prefix of
    # `sbatch_pet_fullevent_nominal_annealed.sh`. :48 BASELINE is the 08-08 artifact the annealed run
    # is compared against; :21 is prose about the no-clobber guard. Both must keep naming 08-08.
    "nd-unfolding/pet/sbatch_pet_fullevent_nominal_annealed.sh":   ("STAYS-DIAG08", 2),

    # The TEST for pet_diagnostic_quarantine.py:229, encoding the same assumption. Treated together
    # with its code so the two cannot diverge on it; gets the same comment.
    "nd-unfolding/tests/test_pet_diagnostic_quarantine.py":        ("STAYS-NAME", 1),

    # --- OI-81's SUBSTANTIVE HALF, dispositioned 2026-08-15 by lane C as the designated owner of this
    # script (BEN-237; BEN-325 diagnosed the RED read-only and explicitly left these to the owner).
    # These are the FOUR files whose occurrences are OPERANDS under CLASS 6. BEN-325 reported SEVEN
    # "code consumers"; it classified by FILE EXTENSION, and re-measured by occurrence three of the
    # seven carry no operand at all -- probe-vl100-own-run-foldforward-20260815.py:5,
    # test_closure_foldforward_recording.py:6 and test_pet_diagnostic_artifact_identity_guards.py
    # :5,:14,:95 are every one of them DOCSTRING PROSE, and those three files open the ANNEALED
    # artifact, a synthetic fixture, and nothing respectively. TWO of the four below actually np.load
    # the path; the other two only NAME it in emitted data.
    #
    # THE PRE-ANNEAL READ IS DELIBERATE IN BOTH LOADERS AND MUST NOT BE RETARGETED. `fullevent_nominal/`
    # still unambiguously names the 2026-08-08 directory -- the designation moved NO BYTES, so what it
    # retired is the WORD "nominal" as a synonym for canonical, not this path. Retargeting either probe
    # to the annealed sibling would change what a committed receipt's numbers mean while its name stayed
    # the same, which is STAYS-DIAG08's whole reason for existing.

    # BEN-311's line. Reads the PRE-ANNEAL arm at :46 and its result was cited against VL100, which is
    # the ANNEALED arm's recovery. CORRECT-BUT-UNDECLARED, and the undeclared thing is the ARM: per
    # BEN-312 the probe read exactly the artifact closure 56552326's own quarantine manifest names as
    # the source of its own rejection, so the mis-target is in the RECORD and not here. Frozen as the
    # evidence of that; superseded for physics by probe-vl100-own-run-foldforward-20260815.py, which
    # runs the same quantity on the closure's own artifact.
    "docs/orchestration/state/probe-vl100-foldforward-shape-20260814.py": ("STAYS-PINNED", 1),

    # CORRECT, and deliberately so: written 2026-08-15 AFTER BEN-311/BEN-312 were known, it reads the
    # pre-anneal arm ON PURPOSE because that arm carries the larger residual field (1.44% vs 0.52%),
    # making it the ADVERSARIAL input to the correction scan. :8 is the load; :32 is an output label
    # naming the directory it read, which is accurate.
    "docs/orchestration/state/probe-vl100-nominal-residual-field-20260815.py": ("STAYS-PINNED", 2),

    # NOT a loader of this path -- it opens four committed JSON operands only (:61-64). Its three
    # occurrences are receipt DATA LITERALS recording which arm lane D decomposed, each already labelled
    # `pre_anneal` / `PRE-ANNEAL arm` beside its sha256. They are OPERANDS by CLASS 6's fail-closed rule
    # (live dict literals, not comments) and that is the rule working, not a misfire.
    "docs/orchestration/state/probe-vl100-shape-correction-scan-20260815.py": ("STAYS-PINNED", 3),

    # CORRECT AS WRITTEN, and this is the one entry here that protects something live. It consumes the
    # ANNEALED arm -- ARM_DIR at :119, WEIGHTS at :125 -- so it is NOT a pre-anneal consumer; :20 and
    # :57 are comments (one a deliberate counter-example quoting sbatch_fullevent_diagnostic_extract.sh
    # :42, the trap this launcher was written fresh to avoid) and :584 is BEN-312's record inside the
    # receipt heredoc. COUNT ENFORCED DESPITE THE FILE BEING EDITED OFTEN, which is the opposite of the
    # BEN-084 cry-wolf calculus everywhere else in this inventory, and deliberately: BEN-311 names "the
    # P5A launcher" among the prior instances of the sibling-directory trap, so a new `fullevent_nominal/`
    # occurrence in THIS file is exactly the event worth a false alarm or two.
    "nd-unfolding/pet/sbatch_p5a_fullevent_nominal_extract.sh":     ("STAYS-ANNEALED", 3),

    # --- RECORD-APPEND: files DESIGNED TO ACCRUE. Count unenforced (None) because an enforced
    # count fires on every unrelated append and a check that cries wolf is ignored (BEN-084).
    "docs/OPEN_ITEMS.md":                                              ("RECORD-APPEND", None),  # NS-EXEMPT: inventory key
    "docs/orchestration/FINDING-20260807-checkpoint-is-not-the-trained-model.md": ("RECORD-APPEND", None),  # NS-EXEMPT: inventory key
    "docs/orchestration/FINDING-20260807-step1-under-achieves.md":     ("RECORD-APPEND", None),  # NS-EXEMPT: inventory key
    "docs/orchestration/FINDING-20260811-promotion-by-move-silently-repoints-artifacts.md": ("RECORD-APPEND", None),  # NS-EXEMPT: inventory key
    "docs/orchestration/FINDINGS.md":                                  ("RECORD-APPEND", None),  # NS-EXEMPT: inventory key
    # Created 2026-08-12 by the ledger split (0623619): FINDINGS.md became a one-line index and the full
    # rows moved here BYTE-VERBATIM. Its four occurrences are the archived long forms of BEN-095/096/091
    # and the 136/137/138 block -- historical citations, none live, none to be retargeted. Keyed
    # RECORD-APPEND on the PROPERTY: the file's own header forbids appending NEW findings, but it accrues
    # every time a row is retired out of the active ledger, which is the same accruing shape. Owned by
    # whoever owns the split; this entry unblocks the audit and may be re-keyed by them.
    "docs/orchestration/FINDINGS-ARCHIVE-2026-08.md":                  ("RECORD-APPEND", None),  # NS-EXEMPT: inventory key
    "docs/orchestration/INDEX-retracted-and-superseded-values.md":     ("RECORD-APPEND", None),  # NS-EXEMPT: inventory key
    # ANOTHER LANE'S FILE, dispositioned 2026-08-12 by the PET lane because leaving the audit RED
    # blocks every lane. The occurrence (`:450`, a mutation-test plan step naming
    # fullevent_nominal/STEP1_DECOMPOSITION.slurm-56445883.json) is a citation of the PRE-ANNEAL  # NS-EXEMPT: prose naming the anchor
    # control anchor and is CORRECT as written -- it must not be retargeted. Keyed RECORD-APPEND on
    # the PROPERTY, not the filename: it is a dated per-session verdicts log in the same accruing
    # family as FINDING-*, and it accrued a line in the hour before this entry. Session D owns the
    # file and may re-key it; this entry is a disposition, not a claim on the document.
    "docs/orchestration/VERDICTS-20260811-session-D.md":               ("RECORD-APPEND", None),  # NS-EXEMPT: inventory key
    "nd-unfolding/AUTONOMOUS_LOG_20260805.md":                         ("RECORD-APPEND", None),  # NS-EXEMPT: inventory key
    "nd-unfolding/ND_OMNIFOLD_RUN_LOG.md":                             ("RECORD-APPEND", None),  # NS-EXEMPT: inventory key
    "nd-unfolding/pet/AUTONOMOUS_LOG_20260805.md":                     ("RECORD-APPEND", None),  # NS-EXEMPT: inventory key

    # --- RECORD-FROZEN: per-job artifacts, written once, nothing appends. Counts ENFORCED --
    # a frozen receipt CANNOT cry wolf, so enforcement is free and it buys a check on the one
    # event that must never happen silently: a committed receipt's content changing.
    "docs/orchestration/PREDECLARATION-20260811-annealed-step1-trajectory.md": ("RECORD-FROZEN", 2),  # NS-EXEMPT: inventory key
    "docs/orchestration/runs/standard-p4-verifier/20260810T012645Z-repair7-transcript.txt": ("RECORD-FROZEN", 2),  # NS-EXEMPT: inventory key
    # COUNT 1 -> 2, 2026-08-15 (BEN-237), and the reclassification matters more than the number.
    # RECORD-FROZEN says "per-job artifacts written once, nothing appends". MEASURED, that is FALSE of
    # this file: `git log --follow` gives FOUR commits (32fcf64, 156d1d6, 49a4699, 043d572) -- it has
    # been superseded IN PLACE three times, so its label was asserting a property it does not have.
    # The second occurrence is :245, prose inside `scope_of_this_supersession` reading "fullevent_nominal/
    # IS NOT TOUCHED ...", i.e. this guard's ONLY enforced signal was firing on a sentence promising that
    # the thing it protects is untouched (BEN-325's sharpest item, and it is right).
    # COUNT ENFORCEMENT IS RETAINED ANYWAY, which is a choice and not an oversight: :63 is the actual
    # PATH PIN and a change there is the BEN-091/BEN-133 event this label exists to catch. Enforcing a
    # whole-file occurrence count is a crude proxy for pinning :63 and it WILL cry wolf again on the next
    # supersession. The right instrument is a per-field pin in verify_hash_bindings.py, not a count here;
    # that is OI-96 and is not built.
    "docs/orchestration/state/annealed-nominal-complete-56563761.json": ("RECORD-FROZEN", 2),  # NS-EXEMPT: inventory key
    "docs/orchestration/state/annealed-nominal-error-56563092.json":   ("RECORD-FROZEN", 2),  # NS-EXEMPT: inventory key
    "docs/orchestration/state/p3f-pet-gate4-launch-code-gate-20260721.json": ("RECORD-FROZEN", 1),  # NS-EXEMPT: inventory key
    "docs/orchestration/state/p3f-pet-gate4-launch-code-gate-20260731.json": ("RECORD-FROZEN", 1),  # NS-EXEMPT: inventory key
    "docs/orchestration/state/p3f-pet-gate4-launch-code-gate-20260801.json": ("RECORD-FROZEN", 1),  # NS-EXEMPT: inventory key
    "docs/orchestration/state/p3f-pet-gate4-launch-code-gate-20260807.json": ("RECORD-FROZEN", 1),  # NS-EXEMPT: inventory key
    "docs/orchestration/state/p3f-pet-gate4-launch-code-gate-20260812.json": ("RECORD-FROZEN", 1),  # NS-EXEMPT: inventory key
    "docs/orchestration/state/step1-dynamics-submit-56531057.json":    ("RECORD-FROZEN", 1),  # NS-EXEMPT: inventory key
    "docs/orchestration/state/step1-ihedge-launch-56525829.json":      ("RECORD-FROZEN", 2),  # NS-EXEMPT: inventory key
    "docs/orchestration/state/step1-trajectory-complete-56525829.json": ("RECORD-FROZEN", 4),  # NS-EXEMPT: inventory key
    "docs/orchestration/state/step1-trajectory-submit-56525829.json":  ("RECORD-FROZEN", 4),  # NS-EXEMPT: inventory key
    "nd-unfolding/pet/annealed_shape_validation/NONQUOTABLE-DIAGNOSTIC.manifest.slurm-56552326.json": ("RECORD-FROZEN", 1),  # NS-EXEMPT: inventory key
    "nd-unfolding/pet/fullevent_diagnostic_nonquotable/NONQUOTABLE-DIAGNOSTIC.manifest.slurm-56527676.json": ("RECORD-FROZEN", 1),  # NS-EXEMPT: inventory key
    "nd-unfolding/pet/fullevent_diagnostic_nonquotable/NONQUOTABLE-DIAGNOSTIC.xsec.slurm-56527676.summary.json": ("RECORD-FROZEN", 1),  # NS-EXEMPT: inventory key
    "nd-unfolding/pet/fullevent_nominal/GATE_AB_PUSH_PROVENANCE.floor-56445883.json": ("RECORD-FROZEN", 2),  # NS-EXEMPT: inventory key
    "nd-unfolding/pet/fullevent_nominal/GATE_AB_PUSH_PROVENANCE.json": ("RECORD-FROZEN", 3),  # NS-EXEMPT: inventory key
    "nd-unfolding/pet/fullevent_nominal/GATE_AB_PUSH_PROVENANCE.slurm-56445883.batch512.json": ("RECORD-FROZEN", 2),  # NS-EXEMPT: inventory key
    "nd-unfolding/pet/fullevent_nominal/GATE_AB_PUSH_PROVENANCE.slurm-56445883.json": ("RECORD-FROZEN", 2),  # NS-EXEMPT: inventory key
    "nd-unfolding/pet/fullevent_nominal/STEP1_DECOMPOSITION.json":     ("RECORD-FROZEN", 1),  # NS-EXEMPT: inventory key
    "nd-unfolding/pet/fullevent_nominal/STEP1_DECOMPOSITION.slurm-56445883.json": ("RECORD-FROZEN", 1),  # NS-EXEMPT: inventory key
    "nd-unfolding/pet/fullevent_nominal/STEP1_TRAJECTORY.slurm-56525829.json": ("RECORD-FROZEN", 8),  # NS-EXEMPT: inventory key
    "nd-unfolding/pet/fullevent_nominal/superseded-20260806/NOTE.md":  ("RECORD-FROZEN", 2),  # NS-EXEMPT: inventory key
    "nd-unfolding/pet/fullevent_nominal_annealed/STEP1_TRAJECTORY.control-prenneal.slurm-56691812.json": ("RECORD-FROZEN", 8),  # NS-EXEMPT: inventory key
    "nd-unfolding/pet/step1_increment_trajectory.py":                  ("RECORD-FROZEN", 3),  # NS-EXEMPT: inventory key

    # --- RECORD: historical artifacts, docs and logs -------------------------------------------
    # Surfaced 2026-08-12 by widening the corpus from *.py/*.sh to ALL tracked files. Every one is a
    # committed receipt, a finding, a run log or a status doc -- a record of what WAS, never rewritten.
    # COUNT IS NOT ENFORCED for these (`None`): run logs and findings are append-only, so a count would
    # fire on every unrelated append and a check that cries wolf is one people learn to ignore (BEN-084).
    # PRESENCE still is: a NEW unclassified file trips UNACCOUNTED, which is the point of widening --
    # it will catch the next promotion that rewrites a receipt.
}


EXEMPTIONS = {}

# Files whose unlisted occurrences are all NARRATIVE. Reported every run; never a failure.
NARRATIVE_ONLY = {}


# --- CLASS 6: OPERAND vs NARRATIVE ---------------------------------------------------------------
# Nothing in a data file executes, so a path literal there cannot open anything -- the READER is code
# and the reader must match on its own line. Grounded in the measured found set (see the docstring),
# not in a guess about what extensions exist.
DATA_EXT = (".json", ".md", ".tsv", ".txt")
PY_EXT = (".py",)
SH_EXT = (".sh", ".bash", ".zsh")


def _in_region(row, col, reg):
    r0, c0, r1, c1 = reg
    if row < r0 or row > r1:
        return False
    if r0 == r1:
        return c0 <= col < c1
    if row == r0:
        return col >= c0
    if row == r1:
        return col < c1
    return True


def _py_narrative_regions(text):
    """(row0, col0, row1, col1) spans of comments and docstrings. None means FAIL CLOSED."""
    regions = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(text).readline):
            if tok.type == tokenize.COMMENT:
                regions.append((tok.start[0], tok.start[1], tok.end[0], tok.end[1]))
    except Exception:
        return None
    try:
        tree = ast.parse(text)
    except Exception:
        return None
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if not isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not body or not isinstance(body[0], ast.Expr):
            continue
        v = body[0].value
        if isinstance(v, ast.Constant) and isinstance(v.value, str):
            regions.append((v.lineno, v.col_offset, v.end_lineno, v.end_col_offset))
    return regions


def _sh_narrative_regions(lines):
    """A `#`-leading line is a comment -- EXCEPT `#SBATCH`, a Slurm DIRECTIVE and a real site."""
    regions = []
    for i, l in enumerate(lines):
        s = l.lstrip()
        if s.startswith("#") and not s.startswith("#SBATCH"):
            regions.append((i + 1, 0, i + 1, len(l)))
    return regions


def classify(rel, lines):
    """Narrative regions for one file, or None to mean 'classify every match as OPERAND'."""
    ext = os.path.splitext(rel)[1].lower()
    if ext in DATA_EXT:
        return [(1, 0, len(lines) + 1, 0)]          # the whole file is narrative
    if ext in PY_EXT:
        return _py_narrative_regions("\n".join(lines) + "\n")
    if ext in SH_EXT:
        return _sh_narrative_regions(lines)
    return None                                     # unknown extension: FAIL CLOSED


def _tracked():
    # ALL tracked files, not just *.py/*.sh. Widened 2026-08-12: there are two ways to fix a claim
    # broader than its check -- narrow the claim or widen the check -- and the postcondition's whole
    # value is that it is broad. A checker that covers receipts will catch the next promotion that
    # rewrites one.
    out = subprocess.run(["git", "-C", _REPO, "ls-files"],
                         capture_output=True, text=True, check=True).stdout
    return [p for p in out.splitlines() if p]


def scan(repo=_REPO, files=None):
    """path -> list of (lineno, text, kind). No file is excluded; class 4 is per-occurrence.

    `kind` is "OPERAND" or "NARRATIVE" per CLASS 6. A line carrying BOTH -- a real assignment with a
    trailing comment that also names the namespace -- is OPERAND: the fail-closed direction, because
    the assignment is what opens the path and the comment must not launder it.
    """
    found = {}
    for rel in (files if files is not None else _tracked()):
        try:
            lines = open(os.path.join(repo, rel), encoding="utf-8").read().splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        regions = classify(rel, lines)
        hits, exempt = [], 0
        for i, l in enumerate(lines):
            if not NS.search(l):
                continue
            # LINE-level exemption, never file-level. Joseph's rule, and it is the same objection the
            # class-4 case at :179 records: a file-wide skip is an IMPLICIT exclusion, and an implicit
            # exclusion is how a real site hides. This file matches its own pattern 8 times -- three
            # docstring class examples and five self-test literals -- and must STAY inside its own
            # sweep, so only those specific lines are marked and the tally is REPORTED below rather
            # than swallowed. A new, real reference added to this file trips UNACCOUNTED like any other.
            if "NS-EXEMPT" in l:
                exempt += 1
                continue
            if regions is None:
                kind = "OPERAND"                     # fail closed
            else:
                cols = [m.start() for m in NS.finditer(l)]
                kind = ("NARRATIVE"
                        if all(any(_in_region(i + 1, c, r) for r in regions) for c in cols)
                        else "OPERAND")
            hits.append((i + 1, l.strip()[:120], kind))
        if exempt:
            EXEMPTIONS[rel] = exempt
        if hits:
            found[rel] = hits
    return found


def audit(found):
    problems = []
    NARRATIVE_ONLY.clear()
    for rel, hits in sorted(found.items()):
        if rel not in INVENTORY:
            # CLASS 6 (BEN-237): presence is demanded of OPERANDS only. A file that merely MENTIONS
            # the namespace in prose cannot open it, and demanding its registration is what kept this
            # guard RED -- the accruing classes RECORD-APPEND already names are exactly the ones a
            # working lane creates all day, and 4 of the 20 unaccounted files on 2026-08-15 were that
            # day's findings ABOUT this namespace. Counted and printed, never silent.
            if not any(h[2] == "OPERAND" for h in hits):
                NARRATIVE_ONLY[rel] = len(hits)
                continue
            n_op = sum(1 for h in hits if h[2] == "OPERAND")
            first_op = next(h[0] for h in hits if h[2] == "OPERAND")
            problems.append(f"UNACCOUNTED FILE {rel}: {len(hits)} occurrence(s), {n_op} in CODE; "
                            f"first operand at :{first_op} -- this file could OPEN that path; give "
                            f"it a disposition in INVENTORY")
            continue
        disp, n = INVENTORY[rel]
        # D's finding: key the exemption on the PROPERTY that justifies it, not on the label that
        # usually accompanies it. My rationale was append-only-ness; my key was "RECORD". Those are
        # different sets, and 23 frozen per-job receipts were silently exempted by a label.
        if n is None and disp != "RECORD-APPEND":
            problems.append(f"EXEMPTION MISKEYED {rel} [{disp}]: only RECORD-APPEND may waive its "
                            f"count -- a frozen artifact cannot cry wolf, so exempting it is free "
                            f"protection given away")
            continue
        if n is not None and len(hits) != n:
            problems.append(f"COUNT DRIFT {rel} [{disp}]: expected {n}, found {len(hits)} "
                            f"(lines {[h[0] for h in hits]}) -- a NEW reference appeared in an "
                            f"already-listed file; give it its own disposition and update the count")
    # A stale entry is the gate-that-cannot-fail shape: it silently stops protecting anything.
    for rel in sorted(INVENTORY):
        if rel not in found:
            problems.append(f"STALE INVENTORY ENTRY {rel}: listed but no longer matches anything -- "
                            f"remove it, or the inventory is protecting a file that moved")
    return problems


def self_test():
    """Positive AND negative controls. A matcher that cannot be made to miss is not evidence."""
    import tempfile
    fails = []

    def case(name, text, expect_hit):
        got = bool(NS.search(text))
        ok = got == expect_hit
        print(f"  [self-test] {name:<52} hit={got!s:<5} expect={expect_hit!s:<5} "
              f"{'PASS' if ok else 'FAIL'}")
        if not ok:
            fails.append(name)

    print("[self-test] the matcher, both directions:")
    case("class 1 literal path", 'ART = "pet/fullevent_nominal/pet_x.npz"', True)  # NS-EXEMPT: pattern literal, not a reference
    case("class 2 os.path.join segment", 'os.path.join(H, "fullevent_nominal", "p.npz")', True)  # NS-EXEMPT: pattern literal, not a reference
    case("class 3 shell dir assignment", 'OUT="${REPO}/nd-unfolding/pet/fullevent_nominal"', True)  # NS-EXEMPT: pattern literal, not a reference
    case("class 4 driver FILENAME must not match", 'DRIVER="${PET}/train_fullevent_nominal.py"', False)
    # the case that made the first version fail on itself: a module NAME as a string, inside a file
    # whose own name is innocent. Per-file exclusion could never have caught this.
    case("class 4 module NAME in an unrelated file", 'mods = {"train_fullevent_nominal": T}', False)
    case("class 4 module name, import form", 'import train_fullevent_nominal as T', False)
    case("_annealed sibling must NOT match", 'ANN="${PET}/fullevent_nominal_annealed/w.npz"', False)
    case("_annealed with trailing slash", 'x = "pet/fullevent_nominal_annealed/p.npz"', False)
    case("bare token, no path context", '# the fullevent_nominal campaign', False)

    # CLASS 6 (BEN-237). A classifier that cannot be made to say NARRATIVE about a comment, and
    # OPERAND about the code beside it, is not evidence either. `#SBATCH` gets its own case because it
    # is the one `#`-leading line in this repo that IS a real site.
    print("[self-test] the OPERAND/NARRATIVE classifier, both directions:")

    def kcase(name, rel, text, lineno, expect):
        lines = text.splitlines()
        regions = classify(rel, lines)
        l = lines[lineno - 1]
        cols = [m.start() for m in NS.finditer(l)]
        got = ("OPERAND" if regions is None or
               not all(any(_in_region(lineno, c, r) for r in regions) for c in cols)
               else "NARRATIVE")
        ok = got == expect and bool(cols)
        print(f"  [self-test] {name:<52} kind={got:<9} expect={expect:<9} "
              f"{'PASS' if ok else 'FAIL'}")
        if not ok:
            fails.append(name)

    kcase("py: os.path.join operand", "a.py",
          'W = os.path.join(R, "pet/fullevent_nominal/w.npz")\n', 1, "OPERAND")  # NS-EXEMPT: pattern literal, not a reference
    kcase("py: whole-line # comment", "a.py",
          '# reads pet/fullevent_nominal/w.npz one day\n', 1, "NARRATIVE")  # NS-EXEMPT: pattern literal, not a reference
    kcase("py: module docstring", "a.py",
          '"""notes about\npet/fullevent_nominal/w.npz here\n"""\nx = 1\n', 2, "NARRATIVE")  # NS-EXEMPT: pattern literal, not a reference
    kcase("py: func docstring", "a.py",
          'def f():\n    """about pet/fullevent_nominal/w.npz"""\n    return 1\n', 2, "NARRATIVE")  # NS-EXEMPT: pattern literal, not a reference
    # THE LAUNDERING CASE, and it is why classification is BY COLUMN and not by line: a real
    # assignment with a trailing comment that also names the namespace must stay OPERAND.
    kcase("py: assignment + trailing comment is OPERAND", "a.py",
          'W = "pet/fullevent_nominal/w.npz"  # see pet/fullevent_nominal/w.npz\n', 1, "OPERAND")  # NS-EXEMPT: pattern literal, not a reference
    kcase("py: unparseable file FAILS CLOSED", "a.py",
          'def (((:\nW = "pet/fullevent_nominal/w.npz"\n', 2, "OPERAND")  # NS-EXEMPT: pattern literal, not a reference
    kcase("sh: code line operand", "a.sh",
          'OUT="${P}/fullevent_nominal"\n', 1, "OPERAND")  # NS-EXEMPT: pattern literal, not a reference
    kcase("sh: leading-# comment", "a.sh",
          '#   WEIGHTS="${P}/fullevent_nominal/w.npz"   # a counter-example\n', 1, "NARRATIVE")  # NS-EXEMPT: pattern literal, not a reference
    # #SBATCH is a comment to bash and a DIRECTIVE to Slurm. sbatch_pet_fullevent_nominal.sh:12,:13
    # are genuine namespace sites in exactly this form -- treating them as prose would hide a write.
    kcase("sh: #SBATCH directive is OPERAND", "a.sh",
          '#SBATCH --output=/p/pet/fullevent_nominal/logs/x_%j.out\n', 1, "OPERAND")  # NS-EXEMPT: pattern literal, not a reference
    kcase("json data file is NARRATIVE", "a.json",
          '{"path": "pet/fullevent_nominal/w.npz"}\n', 1, "NARRATIVE")  # NS-EXEMPT: pattern literal, not a reference
    kcase("md data file is NARRATIVE", "a.md",
          'the `pet/fullevent_nominal/w.npz` baseline\n', 1, "NARRATIVE")  # NS-EXEMPT: pattern literal, not a reference
    kcase("unknown extension FAILS CLOSED", "a.pl",
          '# even a comment counts here\nmy $w = "pet/fullevent_nominal/w.npz";\n', 2, "OPERAND")  # NS-EXEMPT: pattern literal, not a reference

    print("[self-test] the auditor, both directions:")
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "sub"), exist_ok=True)
        p = os.path.join(d, "sub", "x.sh")
        open(p, "w").write('A="${P}/fullevent_nominal/a.npz"\n')  # NS-EXEMPT: pattern literal, not a reference
        found = scan(repo=d, files=["sub/x.sh"])
        got = audit(found)
        unaccounted = any("UNACCOUNTED FILE" in g for g in got)
        print(f"  [self-test] {'unlisted file with an OPERAND is reported':<52} "
              f"{'PASS' if unaccounted else 'FAIL'}")
        if not unaccounted:
            fails.append("unlisted file not reported")

        # CLASS 6, BOTH DIRECTIONS AT THE AUDITOR LEVEL -- the assertion that this change is a
        # NARROWING and not a hole: an unlisted PROSE-only file must not FAIL, and must still be
        # PRINTED. A silent waiver would be the implicit-exclusion defect this whole file objects to.
        q = os.path.join(d, "sub", "y.md")
        open(q, "w").write('mentions pet/fullevent_nominal/a.npz in prose\n')  # NS-EXEMPT: pattern literal, not a reference
        got = audit(scan(repo=d, files=["sub/y.md"]))
        quiet = not any("UNACCOUNTED FILE sub/y.md" in g for g in got)
        listed = NARRATIVE_ONLY.get("sub/y.md") == 1
        print(f"  [self-test] {'unlisted PROSE-only file does NOT fail':<52} "
              f"{'PASS' if quiet else 'FAIL'}")
        print(f"  [self-test] {'...and IS reported as narrative-only':<52} "
              f"{'PASS' if listed else 'FAIL'}")
        if not quiet:
            fails.append("prose-only file wrongly failed")
        if not listed:
            fails.append("prose-only file not reported")

        # count drift must fire even though the file IS listed
        open(p, "w").write('A="${P}/fullevent_nominal/a.npz"\nB="${P}/fullevent_nominal/b.npz"\n')  # NS-EXEMPT: pattern literal, not a reference
        saved = INVENTORY.get("sub/x.sh")
        INVENTORY["sub/x.sh"] = ("STAYS-PROD", 1)
        try:
            got = audit(scan(repo=d, files=["sub/x.sh"]))
            drift = any("COUNT DRIFT" in g for g in got)
            print(f"  [self-test] {'a NEW ref in a LISTED file is reported':<52} "
                  f"{'PASS' if drift else 'FAIL'}")
            if not drift:
                fails.append("count drift not reported")
            # MISKEYED EXEMPTION: a non-RECORD-APPEND entry waiving its count must be reported.
            # D's finding was that nothing structurally confined the exemption to the property that
            # justified it; this is the assertion that now does, so it gets a control.
            INVENTORY["sub/x.sh"] = ("STAYS-PROD", None)
            got = audit(scan(repo=d, files=["sub/x.sh"]))
            mis = any("EXEMPTION MISKEYED" in g for g in got)
            print(f"  [self-test] {'a non-APPEND entry waiving its count':<52} "
                  f"{'PASS' if mis else 'FAIL'}")
            if not mis:
                fails.append("miskeyed exemption not reported")
            INVENTORY["sub/x.sh"] = ("RECORD-APPEND", None)
            got = audit(scan(repo=d, files=["sub/x.sh"]))
            okd = not any("EXEMPTION MISKEYED" in g for g in got)
            print(f"  [self-test] {'a RECORD-APPEND entry waiving its count':<52} "
                  f"{'PASS' if okd else 'FAIL'}")
            if not okd:
                fails.append("RECORD-APPEND wrongly reported as miskeyed")
            INVENTORY["sub/x.sh"] = ("STAYS-PROD", 1)

            # stale entry
            got = audit(scan(repo=d, files=[]))
            stale = any("STALE INVENTORY ENTRY" in g for g in got)
            print(f"  [self-test] {'a STALE inventory entry is reported':<52} "
                  f"{'PASS' if stale else 'FAIL'}")
            if not stale:
                fails.append("stale entry not reported")
        finally:
            if saved is None:
                INVENTORY.pop("sub/x.sh", None)
            else:
                INVENTORY["sub/x.sh"] = saved

    if fails:
        print("[self-test] FAILURES: " + ", ".join(fails))
        return 1
    print("[self-test] PASS (all directions)")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()

    found = scan()
    total = sum(len(v) for v in found.values())
    if a.list:
        for rel, hits in sorted(found.items()):
            disp = INVENTORY.get(rel, ("<UNACCOUNTED>", None))[0]
            print(f"{disp:<14} {rel}")
            for ln, txt, kind in hits:
                print(f"   {kind:<9}  :{ln}  {txt}")
        print(f"\n{len(found)} files, {total} occurrences "
              f"({sum(1 for v in found.values() for h in v if h[2] == 'OPERAND')} in code)")
        return 0

    problems = audit(found)
    n_op = sum(1 for v in found.values() for h in v if h[2] == "OPERAND")
    print(f"[designation] {len(found)} files, {total} namespace occurrences "
          f"({n_op} OPERAND / {total - n_op} NARRATIVE), {len(INVENTORY)} inventory entries")
    for rel, n in sorted(EXEMPTIONS.items()):
        print(f"[designation] {n} line-level NS-EXEMPT literal(s) in {rel} "
              f"(exempted lines are reported, never silent)")
    if NARRATIVE_ONLY:
        print(f"[designation] {len(NARRATIVE_ONLY)} unlisted file(s) mention the namespace in PROSE "
              f"only and are not required to be dispositioned (CLASS 6 / BEN-237) -- listed so the "
              f"narrowing of what a PASS claims is visible in the output:")
        for rel, n in sorted(NARRATIVE_ONLY.items()):
            print(f"   NARRATIVE-ONLY {rel}: {n} occurrence(s)")
    if problems:
        print("[designation] FAIL -- the designation's safety depends on this being empty:")
        for p in problems:
            print("   " + p)
        return 1
    # THE PASS LINE STATES THE CLAIM IT CAN SUPPORT AND NOT THE ONE IT USED TO MAKE. Until 2026-08-15
    # this read "every occurrence has an explicit disposition", which after CLASS 6 would be false --
    # 192 of 225 occurrences are prose and are deliberately not dispositioned. A green tick whose
    # wording outruns its check is the whole BEN-321/322/323/325 family, and this file must not join it.
    print(f"[designation] PASS -- every namespace occurrence IN CODE ({n_op} of {total}) has an "
          f"explicit disposition, and every inventory entry still matches. This does NOT say the "
          f"designated artifact is unchanged: a byte change in the weights appears here NOWHERE "
          f"(BEN-325). Class 5 is unaddressed by construction; see the module docstring.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
