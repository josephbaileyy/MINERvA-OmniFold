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

  CLASS 1  literal slash-joined path      "fullevent_nominal/pet_fullevent_nominal_weights.npz"
  CLASS 2  segmented os.path.join         os.path.join(HERE, "fullevent_nominal", "pet_...npz")
           -- invisible to a class-1 grep, and it is where the two sites the first inventory
              DROPPED were hiding
  CLASS 3  shell composition across LINES OUT=".../fullevent_nominal" then NOM="${OUT}/pet_...npz"
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

# Files whose NAME contains the namespace string but which are not the namespace (class 4).
FILENAME_FALSE_POSITIVES = (
    "train_fullevent_nominal",
    "sbatch_pet_fullevent_nominal",
    "test_pet_fullevent_nominal",
)

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
#   RECORD        committed receipt or docstring; historical, never rewritten
INVENTORY = {
    "nd-unfolding/pet/gate_ab_push_provenance.py":                 ("RETARGET", 1),
    "nd-unfolding/pet/step1_pull_push_decomposition.py":           ("RETARGET", 1),

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

    "nd-unfolding/pet/step1_increment_trajectory.py":              ("RECORD", 3),
}


def _tracked():
    out = subprocess.run(["git", "-C", _REPO, "ls-files", "*.py", "*.sh"],
                         capture_output=True, text=True, check=True).stdout
    return [p for p in out.splitlines() if p]


def scan(repo=_REPO, files=None):
    """path -> list of (lineno, text). Class 4 filenames excluded by NAME, not by a blanket rule."""
    found = {}
    for rel in (files if files is not None else _tracked()):
        base = os.path.basename(rel)
        if any(base.startswith(fp) for fp in FILENAME_FALSE_POSITIVES):
            continue
        if rel.startswith("nd-unfolding/tests/"):
            continue
        try:
            lines = open(os.path.join(repo, rel), encoding="utf-8").read().splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        hits = [(i + 1, l.strip()[:120]) for i, l in enumerate(lines) if NS.search(l)]
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
        if len(hits) != n:
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
    case("class 1 literal path", 'ART = "pet/fullevent_nominal/pet_x.npz"', True)
    case("class 2 os.path.join segment", 'os.path.join(H, "fullevent_nominal", "p.npz")', True)
    case("class 3 shell dir assignment", 'OUT="${REPO}/nd-unfolding/pet/fullevent_nominal"', True)
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
        open(p, "w").write('A="${P}/fullevent_nominal/a.npz"\n')
        found = scan(repo=d, files=["sub/x.sh"])
        got = audit(found)
        unaccounted = any("UNACCOUNTED FILE" in g for g in got)
        print(f"  [self-test] {'unlisted file is reported':<52} {'PASS' if unaccounted else 'FAIL'}")
        if not unaccounted:
            fails.append("unlisted file not reported")

        # count drift must fire even though the file IS listed
        open(p, "w").write('A="${P}/fullevent_nominal/a.npz"\nB="${P}/fullevent_nominal/b.npz"\n')
        saved = INVENTORY.get("sub/x.sh")
        INVENTORY["sub/x.sh"] = ("STAYS-PROD", 1)
        try:
            got = audit(scan(repo=d, files=["sub/x.sh"]))
            drift = any("COUNT DRIFT" in g for g in got)
            print(f"  [self-test] {'a NEW ref in a LISTED file is reported':<52} "
                  f"{'PASS' if drift else 'FAIL'}")
            if not drift:
                fails.append("count drift not reported")
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
    if problems:
        print("[designation] FAIL -- the designation's safety depends on this being empty:")
        for p in problems:
            print("   " + p)
        return 1
    print("[designation] PASS -- every occurrence has an explicit disposition")
    return 0


if __name__ == "__main__":
    sys.exit(main())
