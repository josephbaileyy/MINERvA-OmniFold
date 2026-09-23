#!/usr/bin/env python3
"""Every flag/identity TParameter the event loop writes must pass the 'f' merge mode (KNOWN_ISSUES #8).

`hadd` merges same-named TParameters with the object's merge mode, and the default is '+'. That is
right for EXTENSIVE fields (POT, event counts, migration census) and wrong for a FLAG or IDENTITY
field, which a 12-playlist merge turns from 0/1 into a count in [0, 12].

`hasTruthOnlyMisses` is the one flag still written with the default mode. The one-character fix
(`'f'`) is not applied yet: `nd-unfolding/pet/sbatch_p3f_pet_fullevent_evloop_array.sh` pins this
source's sha256 as the source of the installed binary `61d7dfbf...`, and a true re-pin needs a
cluster rebuild. It is held in PENDING_DEFAULT_MODE. That entry is a ratchet: the test fails once
the source passes 'f', so the entry has to be removed when the fix lands.

Source-level only: this reads `runEventLoopOmniFold.cpp` and does not compile or run ROOT. Every
TParameter construction in the file must be declared in exactly one class below, so a new field
fails this test until someone classifies it.
"""
import os
import re
import unittest

ND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(ND)
CPP = os.path.join(REPO, "MINERvA101", "MINERvA-101-Cross-Section", "runEventLoopOmniFold.cpp")

EXTENSIVE = {  # sums across playlists are the correct merged value: default '+' mode
    "mcPOTUsed", "dataPOTUsed", "nTruthOnlyMisses",
    "activeUniverseTruthEntrants", "activeUniverseTruthExits",
    "activeUniverseRecoEntrants", "activeUniverseRecoExits",
}
FIRST = {  # per-run flags / identities: must pass 'f'
    "activeUniverseIndex", "hasActiveUniverse", "activeUniverseIsLateral",
    "hasFullEventSchema", "fullPhaseSpace", "hasTruthOnlyMisses",
}
# Flags known to still use the default mode, with the reason. Nothing else may join this set.
PENDING_DEFAULT_MODE = {
    "hasTruthOnlyMisses": "source pinned by the P3F launcher to binary 61d7dfbf; needs a rebuild",
}

_COMMENT_OR_LITERAL = re.compile(
    r'("(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')|//[^\n]*|/\*.*?\*/', re.S)
_CTOR = re.compile(r'TParameter\s*<\s*(\w+)\s*>\s*\(\s*"(\w+)"\s*,(.*?)\)\s*;', re.S)
_MODE = re.compile(r",\s*'(.)'\s*$", re.S)


def strip_comments(src):
    return _COMMENT_OR_LITERAL.sub(lambda m: m.group(1) or "", src)


def constructions(src):
    """[(type, name, mode)] for every `TParameter<T>("name", ...);` in comment-stripped source."""
    code = strip_comments(src)
    out = []
    for m in _CTOR.finditer(code):
        mm = _MODE.search(m.group(3))
        out.append((m.group(1), m.group(2), mm.group(1) if mm else "+"))
    n_mentions = len(re.findall(r"TParameter\s*<", code))
    return out, n_mentions


def violations(src):
    rows, n_mentions = constructions(src)
    bad = []
    if len(rows) != n_mentions:
        bad.append(f"parsed {len(rows)} constructions but {n_mentions} TParameter< mentions")
    for typ, name, mode in rows:
        if (name in EXTENSIVE) == (name in FIRST):
            bad.append(f"{name}: not declared in exactly one class")
        elif name in FIRST and mode != "f" and name not in PENDING_DEFAULT_MODE:
            bad.append(f"{name}: flag/identity written with merge mode {mode!r}, needs 'f'")
        elif name in EXTENSIVE and mode != "+":
            bad.append(f"{name}: extensive field written with merge mode {mode!r}, needs '+'")
    return rows, bad


class EventLoopTParameterMergeModes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CPP, encoding="utf-8", errors="replace") as f:
            cls.src = f.read()

    def test_every_tparameter_is_classified_and_uses_its_class_mode(self):
        rows, bad = violations(self.src)
        self.assertEqual(bad, [])
        self.assertEqual({n for _, n, _ in rows}, EXTENSIVE | FIRST)  # no stale declarations

    def test_pending_entries_are_still_pending(self):
        """Ratchet: once a pending flag passes 'f', its PENDING_DEFAULT_MODE entry must go."""
        rows, _ = violations(self.src)
        modes = {n: m for _, n, m in rows}
        self.assertLessEqual(set(PENDING_DEFAULT_MODE), FIRST)
        for name in PENDING_DEFAULT_MODE:
            self.assertEqual(modes.get(name), "+",
                             f"{name} now passes {modes.get(name)!r}: remove it from PENDING_DEFAULT_MODE")

    def test_checker_fires_when_a_flag_drops_its_first_mode(self):
        mutated, n = re.subn(r'("hasFullEventSchema", 1), \'f\'\)', r"\1)", self.src)
        self.assertEqual(n, 1, "mutation did not reach the write site")
        _, bad = violations(mutated)
        self.assertTrue(any("hasFullEventSchema" in b and "needs 'f'" in b for b in bad), bad)

    def test_the_pending_fix_passes_the_classifier(self):
        """Apply the one-character fix in memory: the classifier accepts it."""
        fixed, n = re.subn(r'("hasTruthOnlyMisses",\s*appendTruthMisses \? 1 : 0)\)',
                           r"\1, 'f')", self.src)
        self.assertEqual(n, 1, "fix did not reach the write site")
        rows, bad = violations(fixed)
        self.assertEqual(bad, [])
        self.assertIn(("int", "hasTruthOnlyMisses", "f"), rows)

    def test_checker_fires_on_an_unclassified_new_field(self):
        mutated = self.src + '\nauto x = new TParameter<int>("isSomethingNew", 1);\n'
        _, bad = violations(mutated)
        self.assertTrue(any("isSomethingNew" in b for b in bad), bad)

    def test_a_commented_out_construction_is_not_counted(self):
        rows0, _ = constructions(self.src)
        rows1, _ = constructions(self.src + '\n// new TParameter<int>("ghost", 1);\n')
        self.assertEqual(rows0, rows1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
