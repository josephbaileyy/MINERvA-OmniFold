#!/usr/bin/env python3
"""OI-136 ratchet: no tracked `.py` may feed the canonical-root literal into `sys.path.insert(0, …)`.

WHY A RATCHET AND NOT A ONE-TIME SWEEP. An absolute `insert(0, …)` executes THAT tree's modules
whichever checkout launched the entrypoint, and `PYTHONPATH` cannot outrank position 0 — so a
deployment-parity check can report every pinned file CURRENT while the interpreter loads a different
file entirely. That is OI-136's measured cause on run `57266000_0`: 3 h 08 m of A100 against a tree
211 commits behind. A sweep fixes today's instances; only a ratchet stops them growing back.

THE COUNT THIS PINS IS NOT ZERO, AND SAYING SO IS THE POINT. Eight files remain, every one of them
named below with the reason it is still here. A ratchet asserting 0 would have to either fail on
commit or license someone to edit files outside the authorization that produced it.

**HOW THIS COUNTS, because three different numbers have been quoted for it and all three were about
different populations.** On `main`, 2026-08-23:

    111  tracked .py contain the canonical-root literal ANYWHERE
     61  ...AND also call sys.path.insert(0, ...) somewhere    <-- co-occurrence, NOT causation
     15  ...where the literal ACTUALLY REACHES a position-0 insert   <-- what this test counts

The 61 is the number previously circulated as OI-136's "59" and as a 72-file grep upper bound. Both
were right about co-occurrence. **Only the third population is the hazard**, and grep cannot compute
it — reaching requires resolving the argument expression, which is why this walks the AST.

**AN EARLIER VERSION OF THIS SCANNER RETURNED 9, AND 9 WAS WRONG.** It matched the insert argument
with an `elif` chain over `Name` / `Constant` / `JoinedStr` / `BinOp`, so it silently skipped `Call`
arguments — `sys.path.insert(0, os.path.join(_REPO, "x"))` and friends. Six files were invisible.
The argument walk below is deliberately unconditional for that reason: **enumerate the expression,
do not enumerate the shapes you thought of.**
"""
import ast
import pathlib
import subprocess
import unittest

CANONICAL = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
REPO = pathlib.Path(__file__).resolve().parents[2]

# Each entry MUST carry a reason. A bare path list decays into an allowlist nobody revisits.
KNOWN_UNREPAIRED = {
    "nd-unfolding/bootstrap_nd.py":
        "REPAIRED on build-k0-execution-integrity and executing in the k=0 rehearsal; awaiting merge to main.",
    "nd-unfolding/seedscan_split.py":
        "REPAIRED on build-k0-execution-integrity and executing in the k=0 rehearsal; awaiting merge to main.",
    "nd-unfolding/pet/d2_oracle.py":
        "PET lane's file. Not this lane's to edit; routed, not owned.",
    "nd-unfolding/pet/inversion_screen.py":
        "PET lane's file. Not this lane's to edit; routed, not owned.",
    "nd-unfolding/pet/push_vs_acceptance.py":
        "PET lane's file. Not this lane's to edit; routed, not owned.",
    "2d-unfolding/unfold_2d_omnifold_unbinned.py":
        "THE PUBLISHED 2D ARM, and it is HASH-BOUND by 7 artifacts including "
        "negweight-hpss-durability-20260821.json and G2_GATE2_TARGET_RUNTIME_RECEIPT.json. The "
        "repair was written and REVERTED: landing it changes the file's sha256, and re-pointing a "
        "receipt-bound file to make a check pass is a standing prohibition (OI-123). Needs Joseph "
        "to decide receipt re-issue vs. leaving it; not a thing a lane may work around.",
    "docs/orchestration/state/probe-oi120c-loader-purity-perturbation-20260814.py":
        "One-off probe artifact, 2026-08-14. A probe is a RECORD of what was run; editing it "
        "falsifies the record. Retire by classification, never by patching.",
    "docs/orchestration/state/probe-oi22-leakage-real-input-20260814.py":
        "One-off probe artifact, 2026-08-14. See above.",
    "docs/orchestration/state/probe-oi22-schema-parity-real-input-20260814.py":
        "One-off probe artifact, 2026-08-14. See above.",
}


def _canonical_form(value):
    """"exact" / "subpath" / None. Bounded at exact-or-separator: a bare startswith would match
    `…/MINERvA-OmniFold-Analysis-Note`, a different repository."""
    if not isinstance(value, str) or not value.startswith(CANONICAL):
        return None
    rest = value[len(CANONICAL):]
    if rest == "":
        return "exact"
    return "subpath" if rest.startswith("/") else None


def rooted_insert_files(read):
    """Tracked .py where a canonical-root literal REACHES sys.path.insert(0, ...)."""
    listed = subprocess.run(["git", "-C", str(REPO), "ls-files", "*.py"],
                            capture_output=True, text=True, check=True).stdout.split()
    hazard = []
    for rel in listed:
        try:
            tree = ast.parse(read(rel))
        except (SyntaxError, ValueError, OSError):
            continue
        rooted_names, inline, inserted = set(), False, []
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant):
                if _canonical_form(node.value.value):
                    rooted_names.update(t.id for t in node.targets if isinstance(t, ast.Name))
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "insert"):
                continue
            base = node.func.value
            if not (isinstance(base, ast.Attribute) and base.attr == "path"
                    and isinstance(base.value, ast.Name) and base.value.id == "sys"):
                continue
            if not (node.args and isinstance(node.args[0], ast.Constant)
                    and node.args[0].value == 0):
                continue
            arg = node.args[1] if len(node.args) > 1 else None
            if isinstance(arg, ast.Constant) and _canonical_form(arg.value):
                inline = True
            elif arg is not None:
                # UNCONDITIONAL. Enumerate the expression, not the shapes you thought of.
                inserted.extend(n.id for n in ast.walk(arg) if isinstance(n, ast.Name))
        if inline or any(n in rooted_names for n in inserted):
            hazard.append(rel)
    return sorted(hazard)


class TheCanonicalRootMustNotReachPositionZero(unittest.TestCase):

    def setUp(self):
        self.found = rooted_insert_files(
            lambda rel: (REPO / rel).read_text(encoding="utf-8", errors="replace"))

    def test_no_file_outside_the_named_set_feeds_a_rooted_insert(self):
        """FIRES on a new instance. This is the ratchet."""
        new = [f for f in self.found if f not in KNOWN_UNREPAIRED]
        self.assertEqual(new, [], "a NEW rooted sys.path.insert(0, ...) appeared:\n  " +
                         "\n  ".join(new) + "\nDerive the root from __file__; do not add it here.")

    def test_the_known_set_only_shrinks(self):
        """FIRES when a listed file is repaired but not delisted — so the list cannot rot into an
        allowlist that outlives its reasons."""
        stale = [f for f in KNOWN_UNREPAIRED if f not in self.found]
        self.assertEqual(stale, [], "these are listed as unrepaired but are now clean — delete "
                                    "their entries:\n  " + "\n  ".join(stale))

    def test_every_listed_file_carries_a_reason(self):
        for path, why in KNOWN_UNREPAIRED.items():
            with self.subTest(path=path):
                self.assertGreater(len(why), 40, f"{path} needs a real reason, not a placeholder")

    def test_the_scanner_FIRES_on_a_synthetic_rooted_insert(self):
        """Power. Without this the two arms above pass on a scanner that returns [] for everything."""
        src = f'import sys\n_R = "{CANONICAL}"\nsys.path.insert(0, _R)\n'
        self.assertTrue(rooted_insert_files(lambda rel: src),
                        "scanner found nothing in a file that is nothing but the defect")

    def test_the_scanner_FIRES_through_a_CALL_argument(self):
        """The exact shape the first version of this scanner missed, which made 15 look like 9."""
        src = (f'import os, sys\n_R = "{CANONICAL}"\n'
               'sys.path.insert(0, os.path.join(_R, "nd-unfolding"))\n')
        self.assertTrue(rooted_insert_files(lambda rel: src),
                        "scanner is blind to Call arguments again")

    def test_the_scanner_is_SILENT_on_a_derived_root(self):
        """The repair's own shape. If this fires, the fix reports as the defect."""
        src = ('import sys\nfrom pathlib import Path\n'
               '_R = str(Path(__file__).resolve().parents[1])\nsys.path.insert(0, _R)\n')
        self.assertEqual(rooted_insert_files(lambda rel: src), [])

    def test_the_scanner_is_SILENT_on_a_SIBLING_repository(self):
        """Over-broad is not the safe direction: it would report a hazard in a tree that has none."""
        src = (f'import sys\n_R = "{CANONICAL}-Analysis-Note"\nsys.path.insert(0, _R)\n')
        self.assertEqual(rooted_insert_files(lambda rel: src), [])

    def test_the_scanner_is_SILENT_on_a_rooted_literal_that_never_reaches_an_insert(self):
        """The 61-vs-15 distinction. A literal used as an OUTPUT path is not this hazard, and
        counting it is what produced the '59' and '72' figures."""
        src = (f'import sys\n_OUT = "{CANONICAL}/products"\n'
               'sys.path.insert(0, "/somewhere/else")\nopen(_OUT)\n')
        self.assertEqual(rooted_insert_files(lambda rel: src), [])


if __name__ == "__main__":
    unittest.main()
