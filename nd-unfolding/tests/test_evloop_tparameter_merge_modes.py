#!/usr/bin/env python3
"""Every flag/identity TParameter the event loop writes must pass the 'f' merge mode (KNOWN_ISSUES #8).

`hadd` merges same-named TParameters with the object's merge mode, and the default is '+'. That is
right for EXTENSIVE fields (POT, event counts, migration census) and wrong for a FLAG or IDENTITY
field, which a 12-playlist merge turns from 0/1 into a count in [0, 12].

`hasTruthOnlyMisses` is written per playlist as 0/1 and keeps the default mode ON PURPOSE. After
`hadd` it is the number of playlists with truth-only misses, and two consumers read it as that
count (cited in EXTENSIVE_BY_DESIGN). So it is extensive by design, and only its name, which reads
like a flag, is misleading. A test below goes red if either consumer stops treating it as a count.

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

# Per-playlist 0/1 values whose merged SUM is the quantity consumers read. Default '+' mode.
#   hasTruthOnlyMisses -> count of playlists with truth-only misses, in [0, 12]:
#     nd-unfolding/p4_evidence.py:253 records it as `native_miss_playlists_with_misses`
#       (bounded <= N_MERGED_PLAYLISTS at :268);
#     nd-unfolding/pet/merge_g2_gate1_mefhc.sh:88 asserts the merged value `before == 12`
#       before normalizing it.
EXTENSIVE_BY_DESIGN = {"hasTruthOnlyMisses"}
EXTENSIVE = {  # sums across playlists are the correct merged value: default '+' mode
    "mcPOTUsed", "dataPOTUsed", "nTruthOnlyMisses",
    "activeUniverseTruthEntrants", "activeUniverseTruthExits",
    "activeUniverseRecoEntrants", "activeUniverseRecoExits",
} | EXTENSIVE_BY_DESIGN
FIRST = {  # per-run flags / identities: must pass 'f'
    "activeUniverseIndex", "hasActiveUniverse", "activeUniverseIsLateral",
    "hasFullEventSchema", "fullPhaseSpace",
}

# (path, pattern) pairs: each consumer must still read hasTruthOnlyMisses as a merged count.
COUNT_CONSUMERS = (
    ("nd-unfolding/p4_evidence.py",
     r'rec\["native_miss_playlists_with_misses"\]\s*=\s*_hm_i\b'),
    ("nd-unfolding/pet/merge_g2_gate1_mefhc.sh",
     r'flag\s*=\s*f\.Get\("hasTruthOnlyMisses"\)[\s\S]*?assert before == 12\b'),
)

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
        elif name in FIRST and mode != "f":
            bad.append(f"{name}: flag/identity written with merge mode {mode!r}, needs 'f'")
        elif name in EXTENSIVE and mode != "+":
            bad.append(f"{name}: extensive field written with merge mode {mode!r}, needs '+'")
    return rows, bad


def consumer_breaks(read=lambda rel: open(os.path.join(REPO, rel), encoding="utf-8").read()):
    return [rel for rel, pat in COUNT_CONSUMERS if not re.search(pat, read(rel))]


class EventLoopTParameterMergeModes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CPP, encoding="utf-8", errors="replace") as f:
            cls.src = f.read()

    def test_every_tparameter_is_classified_and_uses_its_class_mode(self):
        rows, bad = violations(self.src)
        self.assertEqual(bad, [])
        self.assertEqual({n for _, n, _ in rows}, EXTENSIVE | FIRST)  # no stale declarations

    def test_has_truth_only_misses_keeps_the_summing_mode(self):
        rows, _ = violations(self.src)
        self.assertIn(("int", "hasTruthOnlyMisses", "+"), rows)

    def test_consumers_still_read_the_merged_value_as_a_count(self):
        self.assertEqual(consumer_breaks(), [])

    def test_consumer_check_fires_if_a_consumer_reads_it_as_a_boolean(self):
        real = {rel: open(os.path.join(REPO, rel), encoding="utf-8").read()
                for rel, _ in COUNT_CONSUMERS}
        as_bool = {
            "nd-unfolding/pet/merge_g2_gate1_mefhc.sh":
                real["nd-unfolding/pet/merge_g2_gate1_mefhc.sh"].replace(
                    "assert before == 12", "assert before == 1"),
            "nd-unfolding/p4_evidence.py":
                real["nd-unfolding/p4_evidence.py"].replace(
                    'rec["native_miss_playlists_with_misses"] = _hm_i',
                    'rec["native_miss_flag"] = bool(_hm_i)'),
        }
        for rel in as_bool:
            self.assertNotEqual(as_bool[rel], real[rel], f"mutation did not reach {rel}")
            mixed = dict(real, **{rel: as_bool[rel]})
            self.assertEqual(consumer_breaks(mixed.__getitem__), [rel])

    def test_checker_fires_when_a_flag_drops_its_first_mode(self):
        mutated, n = re.subn(r'("hasFullEventSchema", 1), \'f\'\)', r"\1)", self.src)
        self.assertEqual(n, 1, "mutation did not reach the write site")
        _, bad = violations(mutated)
        self.assertTrue(any("hasFullEventSchema" in b and "needs 'f'" in b for b in bad), bad)

    def test_checker_fires_if_the_count_field_is_switched_to_first_mode(self):
        mutated, n = re.subn(r'("hasTruthOnlyMisses",\s*appendTruthMisses \? 1 : 0)\)',
                             r"\1, 'f')", self.src)
        self.assertEqual(n, 1, "mutation did not reach the write site")
        _, bad = violations(mutated)
        self.assertTrue(any("hasTruthOnlyMisses" in b and "needs '+'" in b for b in bad), bad)

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
