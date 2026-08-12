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
import os
import re
import subprocess
import sys

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

    # --- RECORD-APPEND: files DESIGNED TO ACCRUE. Count unenforced (None) because an enforced
    # count fires on every unrelated append and a check that cries wolf is ignored (BEN-084).
    "docs/OPEN_ITEMS.md":                                              ("RECORD-APPEND", None),  # NS-EXEMPT: inventory key
    "docs/orchestration/FINDING-20260807-checkpoint-is-not-the-trained-model.md": ("RECORD-APPEND", None),  # NS-EXEMPT: inventory key
    "docs/orchestration/FINDING-20260807-step1-under-achieves.md":     ("RECORD-APPEND", None),  # NS-EXEMPT: inventory key
    "docs/orchestration/FINDING-20260811-promotion-by-move-silently-repoints-artifacts.md": ("RECORD-APPEND", None),  # NS-EXEMPT: inventory key
    "docs/orchestration/FINDINGS.md":                                  ("RECORD-APPEND", None),  # NS-EXEMPT: inventory key
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
    "docs/orchestration/state/annealed-nominal-complete-56563761.json": ("RECORD-FROZEN", 1),  # NS-EXEMPT: inventory key
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


def _tracked():
    # ALL tracked files, not just *.py/*.sh. Widened 2026-08-12: there are two ways to fix a claim
    # broader than its check -- narrow the claim or widen the check -- and the postcondition's whole
    # value is that it is broad. A checker that covers receipts will catch the next promotion that
    # rewrites one.
    out = subprocess.run(["git", "-C", _REPO, "ls-files"],
                         capture_output=True, text=True, check=True).stdout
    return [p for p in out.splitlines() if p]


def scan(repo=_REPO, files=None):
    """path -> list of (lineno, text). No file is excluded; class 4 is handled per-occurrence."""
    found = {}
    for rel in (files if files is not None else _tracked()):
        try:
            lines = open(os.path.join(repo, rel), encoding="utf-8").read().splitlines()
        except (OSError, UnicodeDecodeError):
            continue
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
            hits.append((i + 1, l.strip()[:120]))
        if exempt:
            EXEMPTIONS[rel] = exempt
        if hits:
            found[rel] = hits
    return found


def audit(found):
    problems = []
    for rel, hits in sorted(found.items()):
        if rel not in INVENTORY:
            problems.append(f"UNACCOUNTED FILE {rel}: {len(hits)} occurrence(s); first at "
                            f":{hits[0][0]} -- give it a disposition in INVENTORY")
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

    print("[self-test] the auditor, both directions:")
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "sub"), exist_ok=True)
        p = os.path.join(d, "sub", "x.sh")
        open(p, "w").write('A="${P}/fullevent_nominal/a.npz"\n')  # NS-EXEMPT: pattern literal, not a reference
        found = scan(repo=d, files=["sub/x.sh"])
        got = audit(found)
        unaccounted = any("UNACCOUNTED FILE" in g for g in got)
        print(f"  [self-test] {'unlisted file is reported':<52} {'PASS' if unaccounted else 'FAIL'}")
        if not unaccounted:
            fails.append("unlisted file not reported")

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
            for ln, txt in hits:
                print(f"               :{ln}  {txt}")
        print(f"\n{len(found)} files, {total} occurrences")
        return 0

    problems = audit(found)
    print(f"[designation] {len(found)} files, {total} namespace occurrences, "
          f"{len(INVENTORY)} inventory entries")
    for rel, n in sorted(EXEMPTIONS.items()):
        print(f"[designation] {n} line-level NS-EXEMPT literal(s) in {rel} "
              f"(exempted lines are reported, never silent)")
    if problems:
        print("[designation] FAIL -- the designation's safety depends on this being empty:")
        for p in problems:
            print("   " + p)
        return 1
    print("[designation] PASS -- every occurrence has an explicit disposition")
    return 0


if __name__ == "__main__":
    sys.exit(main())
