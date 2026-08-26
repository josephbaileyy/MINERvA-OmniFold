#!/usr/bin/env python3
"""Arms for `compare_m1_m6.py`, one requirement at a time, both directions each.

WHAT A CONTROL MATRIX MEANS HERE. Every requirement gets an arm that FIRES on bad input and an arm
that stays SILENT on good input. A guard with only the firing arm waves the opposite direction
through at exit 0; a guard with only the silent arm is a green that cannot fail. The class names
below carry the requirement number so a rejection can be read off by number.

THE FIXTURES ARE NOT DERIVED FROM THE INSTRUMENT'S OWN RULES. The document shapes come from
`measure_m1_m6.py`'s actual `m1()`..`m6()` return dicts, and one arm (`R7`) builds a real tree, runs
the real `measure_m1_m6.py` on it twice, and compares the real documents -- so that at least one arm
cannot agree with this instrument by construction.

R5's FIXTURE IS THE INTERESTING ONE. Under exact equality "pairwise-consistent but jointly
inconsistent" cannot exist, because equality is an equivalence relation. It exists only for a
TOLERANCE rule, and the arm below pins the ordering that defeats a baseline-relative pass: values
3, 0, 6 with a tolerance of 4, where input 0 is within tolerance of both of the others and the joint
spread is 6.
"""
import contextlib
import hashlib
import importlib.util
import io
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

_HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("cm", _HERE / "compare_m1_m6.py")
cm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cm)

# The MEASURING tool, imported for its populations only -- M1_FILES and LAUNCHERS -- so the covering
# control builds its universe from the producer rather than from a list retyped here.
_mspec = importlib.util.spec_from_file_location("mm", _HERE / "measure_m1_m6.py")
mm = importlib.util.module_from_spec(_mspec)
_mspec.loader.exec_module(mm)

CITED_QUOTE = "the behind-count is a drifting quantity"


def base_document(label, tree):
    """The shape `measure_m1_m6.py --json` actually emits, trimmed to two M-1 rows."""
    return {
        "label": label,
        "tree": tree,
        "M-1": [
            {"file": "nd-unfolding/bootstrap_nd.py", "present": True,
             "literals": [{"name": "_ND", "line": 12, "form": "subpath",
                           "value": "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding"}],
             "first_insert": 13,
             "repo_modules_after": [{"module": "omnifold", "line": 20}], "n_after": 1},
            {"file": "nd-unfolding/adopt_unified_5d.py", "present": False},
        ],
        "M-2": {"importable": 118, "stdlib_collisions": [], "python": "3.13.15"},
        "M-3": {"present": True, "rc": 0, "all_intact": True},
        "M-4": {"is_git": True, "head": "a" * 40, "dirty": 0, "untracked": 0, "modified": 0,
                "behind": 3, "ahead": 0, "upstream": "origin/main"},
        "M-5": {"n": 8, "missing": [], "repo_assign": [], "activator_from_code_root": [],
                "activator_from_env_root": ["sbatch_uthrow_block_5d.sh"]},
        "M-6": {"present": True, "n_lines": 557, "counts_resolutions": True,
                "inventory_write_lines": [369], "else_zero_default_lines": [369],
                "state": "WRITTEN BUT DEFAULTED -- a containment-path zero is a default"},
    }


def sha256_bytes(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


class Bench:
    """A scratch directory holding documents, an expected list, and a citable document."""

    def __init__(self, stack):
        self._serial = 0
        self.root = pathlib.Path(stack.enter_context(tempfile.TemporaryDirectory()))
        self.repo = self.root / "repo"
        (self.repo / "docs" / "orchestration").mkdir(parents=True)
        self.cited_rel = "docs/orchestration/CITED.md"
        # LONG ENOUGH TO EXHIBIT THE DEFECT. A three-line fixture cannot show that a one-character
        # quote matches everywhere: "a" hit 2 of 3 lines, under the bound, so the arm passed against
        # a document too small to carry the failure. The real cited document is 146 lines and "a"
        # matches 96. These filler lines all contain "a" and none contains the quote, so the
        # legitimate citation still resolves to exactly one line.
        filler = "\n".join(f"a filler paragraph, line {n}, that mentions almost anything"
                            for n in range(8))
        (self.repo / self.cited_rel).write_text(
            "# a citable document\n\n" + filler + "\n\nSomething, and " + CITED_QUOTE
            + " so it moves.\n", encoding="utf-8")

    def write_doc(self, name, doc):
        """Unique per call, for the reason in `write_expected`: a case list built eagerly over a
        REUSED filename is a set of queries over one row, and R8's matrix silently ran five codes
        against one pair of documents."""
        self._serial += 1
        path = self.root / f"{self._serial}-{name}"
        path.write_text(json.dumps(doc, indent=2), encoding="utf-8")
        return str(path)

    def write_expected(self, entries, name=None, schema=cm.EXPECTED_SCHEMA):
        """EVERY list gets its OWN file, and that is a fix, not a tidiness.

        With a single default filename, a dict of cases built eagerly left every case pointing at
        one path holding the LAST list written -- so `test_a_malformed_list_is_refused_in_every
        shape` was seven subtests over one row, and R8's whole matrix ran against an over-broad
        list and reported exit 5 for all five codes. A well-formed query over the wrong rows does
        not fail; it agrees.
        """
        self._serial += 1
        # INSIDE self.repo: `--expected` must resolve inside `--repo`, because a whitelist from
        # outside the tree is not the reviewable in-tree diff the design claims it is.
        path = self.repo / (name or f"expected-{self._serial}.json")
        path.write_text(json.dumps({"schema": schema, "entries": entries}, indent=2),
                        encoding="utf-8")
        return str(path)

    def citation(self, **overrides):
        base = {"doc": self.cited_rel, "quote": CITED_QUOTE}
        base.update(overrides)
        return base

    def may_differ(self, fields, entry_id="E-test", **citation_overrides):
        return [{"id": entry_id, "fields": list(fields), "rule": {"kind": "may-differ"},
                 "citation": self.citation(**citation_overrides), "why": "a test fixture"}]

    def run(self, inputs, expected, extra=()):
        argv = []
        for item in inputs:
            argv += ["--input", item]
        argv += ["--expected", expected, "--repo", str(self.repo), "--json", *extra]
        out = io.StringIO()
        err = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cm.main(argv)
        record = json.loads(out.getvalue()) if out.getvalue().strip() else None
        return code, record, err.getvalue()


class BenchCase(unittest.TestCase):

    def setUp(self):
        self._stack = contextlib.ExitStack()
        self.addCleanup(self._stack.close)
        self.bench = Bench(self._stack)
        self.expected_ok = self.bench.write_expected(self.bench.may_differ(["M-4.behind"]))

    def two(self, mutate=None):
        """Two documents from two trees; `mutate` edits the second in place."""
        first = base_document("CANDIDATE", "/trees/candidate")
        second = base_document("CANONICAL", "/trees/canonical")
        if mutate is not None:
            mutate(second)
        return (self.bench.write_doc("a.json", first),
                self.bench.write_doc("b.json", second))


# --------------------------------------------------------------------------------------------- R1

class R1_ItConsumesDocumentsAndImplementsNoMeasurement(BenchCase):

    def test_the_module_imports_nothing_that_could_measure_a_tree__by_inspection(self):
        """SILENT ON GOOD, and the arm that would FIRE if a measurement were retyped in here."""
        import ast
        tree = ast.parse((_HERE / "compare_m1_m6.py").read_text(encoding="utf-8"))
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported |= {alias.name.split(".")[0] for alias in node.names}
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        self.assertEqual(imported,
                         {"argparse", "datetime", "hashlib", "json", "pathlib", "sys"})
        for forbidden in ("subprocess", "ast", "glob", "os", "re", "fnmatch"):
            self.assertNotIn(forbidden, imported)
        # fnmatch is on that list DELIBERATELY: the field paths contain brackets, and to fnmatch
        # `M-1[*].first_insert` reads `[*]` as a character class. See field_matches().

    def test_no_measurement_vocabulary_appears_in_the_CODE(self):
        """The operand is the CODE, not the prose.

        A raw substring sweep over the file would fire on the docstrings and the UNITS table, which
        describe the measurements on purpose -- naming a population is the point of R3. So every
        string literal and comment is blanked by `tokenize` first, and what remains is what would
        execute.
        """
        import io as _io
        import tokenize
        source = (_HERE / "compare_m1_m6.py").read_text(encoding="utf-8")
        kept = []
        for token in tokenize.generate_tokens(_io.StringIO(source).readline):
            name = tokenize.tok_name.get(token.type, "")
            if token.type in (tokenize.STRING, tokenize.COMMENT) or name.startswith("FSTRING"):
                continue
            kept.append(token.string)
        code = " ".join(kept)
        self.assertIn("field_matches", code)                # the blanking did not eat the code
        self.assertIn("EXIT_REFUSAL_EXPECTED_LIST", code)
        self.assertIn("stdlib_module_names", source)        # the prose really is in the file
        self.assertNotIn("stdlib_module_names", code)       # and really was blanked
        for name in ("stdlib_module_names", "subprocess", "Popen", "check_output", "ast",
                     "glob", "iglob", "listdir", "scandir", "popen", "system"):
            with self.subTest(name=name):
                self.assertNotIn(name, code, f"{name} would be a second implementation")

    def test_a_HAND_EDITED_document_changes_the_verdict__it_reads_the_document_not_the_world(self):
        """FIRES: the only way the verdict can move is the document, so editing one moves it."""
        same = self.two()
        code_same, record_same, _ = self.bench.run(same, self.expected_ok)
        self.assertEqual(code_same, cm.EXIT_NO_DIFFERENCES)
        self.assertTrue(record_same["summary"]["all_agree"])
        edited = self.two(lambda d: d["M-6"].__setitem__("n_lines", 281))
        code_edit, record_edit, _ = self.bench.run(edited, self.expected_ok)
        self.assertEqual(code_edit, cm.EXIT_DIFFERENCES_SOME_UNEXPECTED)
        self.assertEqual([f["field"] for f in record_edit["findings"]], ["M-6.n_lines"])


# --------------------------------------------------------------------------------------------- R2

class R2_NoDefaultsAndItFailsClosedOnAbsence(BenchCase):

    def test_an_ABSENT_input_is_a_refusal(self):
        good, _ = self.two()
        code, record, err = self.bench.run([good, str(self.bench.root / "nope.json")],
                                          self.expected_ok)
        self.assertEqual(code, cm.EXIT_REFUSAL_INPUT)
        self.assertIsNone(record)
        self.assertIn("does not exist", err)

    def test_an_EMPTY_input_is_a_refusal_and_not_no_differences(self):
        good, _ = self.two()
        empty = self.bench.root / "empty.json"
        empty.write_text("", encoding="utf-8")
        code, _, err = self.bench.run([good, str(empty)], self.expected_ok)
        self.assertEqual(code, cm.EXIT_REFUSAL_INPUT)
        self.assertIn("not 'no differences'", err)

    def test_valid_json_MISSING_THE_M4_KEY_is_a_refusal(self):
        good, _ = self.two()
        maimed = base_document("CANONICAL", "/trees/canonical")
        del maimed["M-4"]
        code, _, err = self.bench.run([good, self.bench.write_doc("m.json", maimed)],
                                      self.expected_ok)
        self.assertEqual(code, cm.EXIT_REFUSAL_INPUT)
        self.assertIn("missing M-4", err)

    def test_unreadable_json_and_a_json_list_are_both_refusals(self):
        good, _ = self.two()
        broken = self.bench.root / "broken.json"
        broken.write_text("{not json", encoding="utf-8")
        listy = self.bench.root / "listy.json"
        listy.write_text("[]", encoding="utf-8")
        for path in (broken, listy):
            with self.subTest(path=path.name):
                code, _, _ = self.bench.run([good, str(path)], self.expected_ok)
                self.assertEqual(code, cm.EXIT_REFUSAL_INPUT)

    def test_ONE_input_is_a_refusal__a_comparison_needs_two(self):
        good, _ = self.two()
        code, _, err = self.bench.run([good], self.expected_ok)
        self.assertEqual(code, cm.EXIT_REFUSAL_INPUT)
        self.assertIn("needs two or more", err)

    def test_the_refusal_code_is_DISTINGUISHABLE_from_differences_found(self):
        self.assertNotIn(cm.EXIT_REFUSAL_INPUT,
                         (cm.EXIT_NO_DIFFERENCES, cm.EXIT_DIFFERENCES_ALL_EXPECTED,
                          cm.EXIT_DIFFERENCES_SOME_UNEXPECTED))

    def test_two_valid_documents_are_NOT_refused__silent_on_good(self):
        code, record, err = self.bench.run(self.two(), self.expected_ok)
        self.assertEqual(code, cm.EXIT_NO_DIFFERENCES)
        self.assertEqual(err, "")
        self.assertEqual(record["n_inputs"], 2)


# --------------------------------------------------------------------------------------------- R3

class R3_EveryFindingNamesBothSidesTheUnitAndThePopulation(BenchCase):

    def test_a_finding_carries_unit_population_and_each_side_s_identity(self):
        code, record, _ = self.bench.run(self.two(lambda d: d["M-3"].__setitem__("rc", 1)),
                                         self.expected_ok)
        self.assertEqual(code, cm.EXIT_DIFFERENCES_SOME_UNEXPECTED)
        finding, = record["findings"]
        self.assertEqual(finding["field"], "M-3.rc")
        self.assertTrue(finding["unit"].startswith("process exit status"))
        self.assertIn("cwd set to that tree", finding["population"])
        # M-3 is a property of the MEASURING interpreter too, and the population must say so.
        self.assertIn("NOT a property of the tree alone", finding["population"])
        self.assertEqual([s["label"] for s in finding["sides"]], ["CANDIDATE", "CANONICAL"])
        for side in finding["sides"]:
            self.assertTrue(side["tree_resolved_path"])
            self.assertEqual(len(side["input_sha256"]), 64)
            self.assertEqual(side["head"], "a" * 40)
        self.assertEqual([s["value"] for s in finding["sides"]], [0, 1])

    def test_SWAPPING_THE_INPUTS_gives_the_same_findings_with_the_sides_relabelled(self):
        first, second = self.two(lambda d: d["M-5"].__setitem__("repo_assign",
                                                                ["sbatch_uthrow_block_5d.sh"]))
        forward_code, forward, _ = self.bench.run([first, second], self.expected_ok)
        reverse_code, reverse, _ = self.bench.run([second, first], self.expected_ok)
        self.assertEqual(forward_code, reverse_code)

        def keyed(record):
            return {f["field"]: (f["classification"],
                                 frozenset((s["input_sha256"], json.dumps(s["value"],
                                                                         sort_keys=True))
                                           for s in f["sides"]))
                    for f in record["findings"]}

        self.assertEqual(keyed(forward), keyed(reverse))
        self.assertEqual({f["field"] for f in forward["findings"]}, {"M-5.repo_assign"})
        self.assertEqual([s["label"] for s in forward["findings"][0]["sides"]],
                         ["CANDIDATE", "CANONICAL"])
        self.assertEqual([s["label"] for s in reverse["findings"][0]["sides"]],
                         ["CANONICAL", "CANDIDATE"])

    def test_the_LABEL_and_TREE_are_identity_and_are_never_compared_fields(self):
        """SILENT ON GOOD: two trees at different paths with equal measurements agree."""
        code, record, _ = self.bench.run(self.two(), self.expected_ok)
        self.assertEqual(code, cm.EXIT_NO_DIFFERENCES)
        self.assertNotEqual(record["inputs"][0]["tree_resolved_path"],
                            record["inputs"][1]["tree_resolved_path"])

    def test_ORDER_ALONE_IS_NOT_A_DIFFERENCE__the_documented_guarantee(self):
        """G-7: `canon`'s docstring promises this and nothing tested it.

        Removing the sort produced spurious findings -- the safe direction, which is exactly why it
        went unnoticed: a guarantee whose only failure mode is over-reporting still has to hold, or
        the reviewer learns to discount the findings.
        """
        def shuffle(doc):
            doc["M-5"]["activator_from_env_root"] = list(
                reversed(doc["M-5"]["activator_from_env_root"]))
            doc["M-6"]["inventory_write_lines"] = list(
                reversed(doc["M-6"]["inventory_write_lines"]))
            doc["M-1"][0]["literals"] = list(reversed(doc["M-1"][0]["literals"]))

        first = base_document("A", "/trees/A")
        first["M-5"]["activator_from_env_root"] = ["b.sh", "a.sh", "c.sh"]
        first["M-6"]["inventory_write_lines"] = [369, 12, 40]
        first["M-1"][0]["literals"] = [
            {"name": "_ND", "line": 12, "form": "subpath", "value": "/x"},
            {"name": "_REPO", "line": 3, "form": "exact", "value": "/y"}]
        second = json.loads(json.dumps(first))
        second["label"], second["tree"] = "B", "/trees/B"
        shuffle(second)
        self.assertNotEqual(first["M-5"]["activator_from_env_root"],
                            second["M-5"]["activator_from_env_root"])
        code, record, _ = self.bench.run(
            (self.bench.write_doc("a.json", first), self.bench.write_doc("b.json", second)),
            self.expected_ok)
        self.assertEqual(code, cm.EXIT_NO_DIFFERENCES, [f["field"] for f in record["findings"]])
        self.assertTrue(record["summary"]["all_agree"])

    def test_a_field_with_NO_DECLARED_UNIT_is_reported_as_undeclared_and_counted(self):
        """FIRES: a new field in measure_m1_m6.py cannot arrive silently unitless."""
        code, record, _ = self.bench.run(self.two(lambda d: d["M-4"].__setitem__("worktrees", 3)),
                                         self.expected_ok)
        self.assertEqual(code, cm.EXIT_DIFFERENCES_SOME_UNEXPECTED)
        finding, = [f for f in record["findings"] if f["field"] == "M-4.worktrees"]
        self.assertFalse(finding["unit_declared"])
        self.assertEqual(finding["unit"], "UNDECLARED")
        self.assertEqual(record["summary"]["n_findings_with_undeclared_unit"], 1)
        self.assertTrue(record["field_set_differs"])
        self.assertEqual([s["value"] for s in finding["sides"]], [cm.ABSENT, 3])

    def test_the_two_identity_fields_the_input_schema_CANNOT_supply_are_named_unavailable(self):
        _, record, _ = self.bench.run(self.two(), self.expected_ok)
        for side in record["inputs"]:
            self.assertEqual(side["branch_or_detached"], cm.UNAVAILABLE)
            self.assertEqual(side["measurement_wall_clock"], cm.UNAVAILABLE)
        self.assertIn("symbolic-ref", record["input_schema_gaps"]["branch_or_detached"])
        self.assertIn("no timestamp", record["input_schema_gaps"]["measurement_wall_clock"])


# --------------------------------------------------------------------------------------------- R4

class R4_TheExpectedListIsDeclaredCitedAndCanFail(BenchCase):

    def test_a_declared_difference_is_classified_expected__silent_on_good(self):
        code, record, _ = self.bench.run(self.two(lambda d: d["M-4"].__setitem__("behind", 168)),
                                         self.expected_ok)
        self.assertEqual(code, cm.EXIT_DIFFERENCES_ALL_EXPECTED)
        finding, = record["findings"]
        self.assertEqual(finding["classification"], "EXPECTED-BY-RULING")
        self.assertEqual(finding["expected_entries_matched"][0]["id"], "E-test")
        citation = finding["expected_entries_matched"][0]["citation"]
        self.assertEqual(citation["matched_lines"], [12])   # the one line carrying the quote
        self.assertEqual(len(citation["doc_sha256_measured"]), 64)

    def test_an_UNDECLARED_difference_stays_unexpected(self):
        code, record, _ = self.bench.run(self.two(lambda d: d["M-4"].__setitem__("dirty", 722)),
                                         self.expected_ok)
        self.assertEqual(code, cm.EXIT_DIFFERENCES_SOME_UNEXPECTED)
        self.assertEqual(record["findings"][0]["classification"], "UNEXPECTED")
        self.assertIn("no entry", record["findings"][0]["reason"])

    def test_a_citation_whose_DOCUMENT_is_absent_is_a_hard_error(self):
        expected = self.bench.write_expected(
            self.bench.may_differ(["M-4.behind"], doc="docs/orchestration/NOT-THERE.md"))
        code, _, err = self.bench.run(self.two(), expected)
        self.assertEqual(code, cm.EXIT_REFUSAL_EXPECTED_LIST)
        self.assertIn("does not exist under --repo", err)

    def test_a_citation_whose_QUOTE_is_absent_is_a_hard_error(self):
        expected = self.bench.write_expected(
            self.bench.may_differ(["M-4.behind"], quote="a sentence nobody wrote"))
        code, _, err = self.bench.run(self.two(), expected)
        self.assertEqual(code, cm.EXIT_REFUSAL_EXPECTED_LIST)
        self.assertIn("silent", err)

    def test_a_DECLARED_DIGEST_that_no_longer_matches_is_a_hard_error(self):
        expected = self.bench.write_expected(
            self.bench.may_differ(["M-4.behind"], doc_sha256="0" * 64))
        code, _, err = self.bench.run(self.two(), expected)
        self.assertEqual(code, cm.EXIT_REFUSAL_EXPECTED_LIST)
        self.assertIn("moved; re-read it", err)

    def test_a_MATCHING_declared_digest_is_accepted__the_opposite_direction(self):
        digest = sha256_bytes(self.bench.repo / self.bench.cited_rel)
        expected = self.bench.write_expected(
            self.bench.may_differ(["M-4.behind"], doc_sha256=digest))
        code, record, _ = self.bench.run(self.two(lambda d: d["M-4"].__setitem__("behind", 9)),
                                         expected)
        self.assertEqual(code, cm.EXIT_DIFFERENCES_ALL_EXPECTED)
        entry = record["expected_list"]["entries"][0]
        self.assertEqual(entry["citations"]["M-4.behind"]["doc_sha256_declared"], digest)

    def test_an_OVER_BROAD_pattern_is_refused_so_the_list_cannot_swallow_a_measurement(self):
        """A REGRESSION PIN OVER REMEMBERED SPELLINGS. It is NOT the guard, and it is why D-3 shipped.

        The first six are the spellings this arm was written with. `M-1[*` was fail-open and is not
        among them: the arm and the rule it guards were enumerated from one intuition, so it could
        not disagree with the rule. `M-6[*`, `M-4.*e*` and `M-4.head*` were fail-open too, in the
        same class and in spellings nobody had listed either -- which is the measurement that says
        a seventh entry would not have closed it. The covering control is
        `R4_ThePatternGrammarIsPositiveNotADenyList`, whose candidates are generated from the
        producer; these rows stay only so a named historical hole cannot silently reopen.
        """
        for pattern in ("M-4", "M-4.*", "M-1[*].*", "*", "M-4behind", "behind",
                        "M-1[*", "M-6[*", "M-4.*e*", "M-4.head*", "M-1[", "M-1.present"):
            with self.subTest(pattern=pattern):
                expected = self.bench.write_expected(self.bench.may_differ([pattern]))
                code, _, err = self.bench.run(self.two(), expected)
                self.assertEqual(code, cm.EXIT_REFUSAL_EXPECTED_LIST)

    def test_a_PER_FILE_wildcard_is_still_allowed__the_narrowing_direction(self):
        expected = self.bench.write_expected(self.bench.may_differ(["M-1[*].first_insert"]))
        code, record, _ = self.bench.run(
            self.two(lambda d: d["M-1"][0].__setitem__("first_insert", 99)), expected)
        self.assertEqual(code, cm.EXIT_DIFFERENCES_ALL_EXPECTED)
        self.assertEqual(record["findings"][0]["field"],
                         "M-1[nd-unfolding/bootstrap_nd.py].first_insert")

    def test_a_malformed_list_is_refused_in_every_shape(self):
        cases = {
            "wrong schema": self.bench.write_expected(self.bench.may_differ(["M-4.behind"]),
                                                      schema="nope/1"),
            "no citation": self.bench.write_expected(
                [{"id": "E", "fields": ["M-4.behind"], "rule": {"kind": "may-differ"}}]),
            "no id": self.bench.write_expected(
                [{"fields": ["M-4.behind"], "rule": {"kind": "may-differ"},
                  "citation": self.bench.citation()}]),
            "bad rule": self.bench.write_expected(
                [{"id": "E", "fields": ["M-4.behind"], "rule": {"kind": "close-enough"},
                  "citation": self.bench.citation()}]),
            "tolerance without a number": self.bench.write_expected(
                [{"id": "E", "fields": ["M-4.behind"], "rule": {"kind": "max-abs-delta"},
                  "citation": self.bench.citation()}]),
            "duplicate id": self.bench.write_expected(
                self.bench.may_differ(["M-4.behind"]) + self.bench.may_differ(["M-4.ahead"])),
            "empty fields": self.bench.write_expected(
                [{"id": "E", "fields": [], "rule": {"kind": "may-differ"},
                  "citation": self.bench.citation()}]),
        }
        for name, expected in cases.items():
            with self.subTest(case=name):
                code, _, _ = self.bench.run(self.two(), expected)
                self.assertEqual(code, cm.EXIT_REFUSAL_EXPECTED_LIST)

    def test_an_ABSENT_expected_list_is_a_refusal_not_an_empty_whitelist(self):
        # INSIDE the repo, or the containment refusal fires first and this arm stops testing absence.
        code, _, err = self.bench.run(self.two(), str(self.bench.repo / "no-list.json"))
        self.assertEqual(code, cm.EXIT_REFUSAL_EXPECTED_LIST)
        self.assertIn("no expected-differences file", err)

    def test_an_expected_list_OUTSIDE_the_repo_is_refused(self):
        """A whitelist from outside the tree cannot be the reviewable in-tree diff it claims to be,
        and every audit-after story told about this file assumes a committed digest."""
        outside = self.bench.root / "outside.json"
        outside.write_text((self.bench.repo / pathlib.Path(self.expected_ok).name).read_text(),
                           encoding="utf-8")
        code, _, err = self.bench.run(self.two(), str(outside))
        self.assertEqual(code, cm.EXIT_REFUSAL_EXPECTED_LIST)
        self.assertIn("must resolve INSIDE --repo", err)

    def test_a_citation_that_LOCATES_NOTHING_is_refused(self):
        """G-2: the guard used to require only that a quote was non-blank and PRESENT. A grader used
        `{"quote": "a"}`, which resolves against any English document -- measured, 96 of the 146
        lines of the document the shipped list cites -- and suppressed four measurements at exit 10
        with every arm green. A citation must locate a passage."""
        code, _, err = self.bench.run(self.two(),
                                      self.bench.write_expected(
                                          self.bench.may_differ(["M-4.behind"], quote="a")))
        self.assertEqual(code, cm.EXIT_REFUSAL_EXPECTED_LIST)
        self.assertIn("locates nothing", err)
        self.assertIn("the limit is 3", err)

    def test_a_quote_SPANNING_A_LINE_BREAK_is_refused_even_though_it_resolves(self):
        """It is `in` the document and on no single line, so `matched_lines` was empty and the
        citation pointed at nothing recoverable."""
        spanning = "citable document\n\na filler paragraph, line 0"
        self.assertIn(spanning, (self.bench.repo / self.bench.cited_rel).read_text())
        code, _, err = self.bench.run(self.two(), self.bench.write_expected(
            self.bench.may_differ(["M-4.behind"], quote=spanning)))
        self.assertEqual(code, cm.EXIT_REFUSAL_EXPECTED_LIST)
        self.assertIn("no single LINE", err)

    def test_a_quote_matching_a_HANDFUL_of_lines_is_still_accepted__the_narrowing_direction(self):
        """The bound must not refuse a real citation. The shipped one matches exactly 1 line."""
        loaded = cm.load_expected(str(_HERE / "m1m6_expected_differences.json"), _HERE.parents[1])
        for entry in loaded["entries"]:
            for pattern, citation in entry["citations"].items():
                with self.subTest(pattern=pattern):
                    self.assertEqual(len(citation["matched_lines"]), 1)
                    self.assertLessEqual(len(citation["matched_lines"]), cm.MAX_CITATION_LINES)

    def test_a_NON_OBJECT_citation_is_refused_rather_than_crashing(self):
        """G-7: the type check existed and no arm fed it. Removing it turned a refusal into an
        uncaught traceback at exit 1, which this file reserves as never a verdict."""
        for bad in ("a string", 42, ["a", "list"], None):
            with self.subTest(citation=repr(bad)):
                entry = {"id": "E", "fields": ["M-4.behind"], "rule": {"kind": "may-differ"},
                         "citation": bad}
                code, _, _ = self.bench.run(self.two(), self.bench.write_expected([entry]))
                self.assertEqual(code, cm.EXIT_REFUSAL_EXPECTED_LIST)

    def test_a_WHITESPACE_ONLY_quote_is_refused(self):
        code, _, err = self.bench.run(self.two(), self.bench.write_expected(
            self.bench.may_differ(["M-4.behind"], quote="   ")))
        self.assertEqual(code, cm.EXIT_REFUSAL_EXPECTED_LIST)
        self.assertIn("no 'quote'", err)

    def test_a_matched_but_UNSATISFIED_entry_is_not_reported_as_unused(self):
        """G-7: `expected_entries_unused` was one-directional. An entry that matched a field but
        whose rule failed would have read as 'matched nothing', which is the opposite of the truth."""
        expected = self.bench.write_expected([{
            "id": "E-tight", "fields": ["M-4.behind"],
            "rule": {"kind": "max-abs-delta", "value": 1},
            "citation": self.bench.citation(), "why": "a tolerance that will be exceeded"}])
        code, record, _ = self.bench.run(
            self.two(lambda d: d["M-4"].__setitem__("behind", 99)), expected)
        self.assertEqual(code, cm.EXIT_DIFFERENCES_SOME_UNEXPECTED)
        self.assertEqual(record["findings"][0]["classification"], "UNEXPECTED")
        self.assertEqual(record["summary"]["expected_entries_unused"], [])


    def test_ONE_QUOTE_MAY_NOT_LICENSE_A_FIELD_LIST__the_defect_in_the_shipped_entry(self):
        """FIRES. The first entry ever shipped here was wrong in exactly this way.

        `E1-m4-behind-and-ahead-drift` claimed `M-4.behind` AND `M-4.ahead` under one citation whose
        heading is "the BEHIND-COUNT has moved twice" and whose only mention of ahead is
        `ahead = 0 ; --is-ancestor rc=0`. The citation did not merely fail to support the second
        field, it recorded the opposite -- and the guard passed, because resolving is not supporting.
        A single citation now licenses exactly ONE pattern.
        """
        expected = self.bench.write_expected(
            self.bench.may_differ(["M-4.behind", "M-4.ahead"]))
        code, _, err = self.bench.run(self.two(), expected)
        self.assertEqual(code, cm.EXIT_REFUSAL_EXPECTED_LIST)
        self.assertIn("exactly ONE field pattern", err)
        self.assertIn("2", err)

    def test_a_multi_field_entry_with_ONE_CITATION_PER_FIELD_is_accepted(self):
        """SILENT on good: the shape is not banned, only the unsupported licence."""
        expected = self.bench.write_expected([{
            "id": "E-multi", "fields": ["M-4.behind", "M-4.ahead"],
            "rule": {"kind": "may-differ"},
            "citations": {"M-4.behind": self.bench.citation(),
                          "M-4.ahead": self.bench.citation()},
            "why": "two fields, two quotes"}])
        code, record, _ = self.bench.run(
            self.two(lambda d: d["M-4"].update({"behind": 168, "ahead": 3})), expected)
        self.assertEqual(code, cm.EXIT_DIFFERENCES_ALL_EXPECTED)
        self.assertEqual({f["field"] for f in record["findings"]}, {"M-4.behind", "M-4.ahead"})
        for finding in record["findings"]:
            match, = finding["expected_entries_matched"]
            self.assertEqual(match["matched_pattern"], finding["field"])
            self.assertTrue(match["citation"]["matched_lines"])

    def test_a_citations_MAPPING_is_checked_in_BOTH_directions(self):
        cases = {
            "a field with no citation": {
                "id": "E", "fields": ["M-4.behind", "M-4.ahead"],
                "rule": {"kind": "may-differ"},
                "citations": {"M-4.behind": self.bench.citation()}},
            "a citation for a field not claimed": {
                "id": "E", "fields": ["M-4.behind"], "rule": {"kind": "may-differ"},
                "citations": {"M-4.behind": self.bench.citation(),
                              "M-4.dirty": self.bench.citation()}},
            "both citation and citations": {
                "id": "E", "fields": ["M-4.behind"], "rule": {"kind": "may-differ"},
                "citation": self.bench.citation(),
                "citations": {"M-4.behind": self.bench.citation()}},
            "an empty citations mapping": {
                "id": "E", "fields": ["M-4.behind"], "rule": {"kind": "may-differ"},
                "citations": {}},
            "a per-field citation that does not resolve": {
                "id": "E", "fields": ["M-4.behind", "M-4.ahead"],
                "rule": {"kind": "may-differ"},
                "citations": {"M-4.behind": self.bench.citation(),
                              "M-4.ahead": self.bench.citation(quote="nobody wrote this")}},
        }
        for name, entry in cases.items():
            with self.subTest(case=name):
                code, _, err = self.bench.run(self.two(),
                                              self.bench.write_expected([entry]))
                self.assertEqual(code, cm.EXIT_REFUSAL_EXPECTED_LIST, err)

    def test_the_refusal_NAMES_the_field_whose_citation_failed(self):
        """A refusal that cannot say WHICH field is a refusal a reviewer cannot act on."""
        expected = self.bench.write_expected([{
            "id": "E", "fields": ["M-4.behind", "M-4.ahead"], "rule": {"kind": "may-differ"},
            "citations": {"M-4.behind": self.bench.citation(),
                          "M-4.ahead": self.bench.citation(doc="docs/orchestration/GONE.md")}}])
        code, _, err = self.bench.run(self.two(), expected)
        self.assertEqual(code, cm.EXIT_REFUSAL_EXPECTED_LIST)
        self.assertIn("'M-4.ahead'", err)
        self.assertNotIn("'M-4.behind'", err)

    def test_an_entry_that_matched_nothing_is_reported_as_unused(self):
        _, record, _ = self.bench.run(self.two(), self.expected_ok)
        self.assertEqual(record["summary"]["expected_entries_unused"], ["E-test"])


def _terminal_name(field):
    """The FIELD-NAME segment of an emitted field path: `y` in `M-1[x].y` and in `M-4.y` alike."""
    if field.startswith(cm.ROW_MEASUREMENT_ID + "["):
        return field.split("].", 1)[-1]
    return field.split(".", 1)[1]


def _candidate_patterns(universe):
    """Candidate patterns MECHANICALLY DERIVED from the field paths `flatten` really emits.

    Nothing here is typed. Every prefix of every emitted field, each with and without a trailing
    `*`, plus the two structural substitutions a person would actually write. `M-1[*` -- the exact
    spelling D-3 was fail-open on -- falls out as the four-character prefix of any M-1 field plus a
    star, so this fixture GENERATES the known failure rather than remembering it.

    That is the whole reason for building it this way: the deny-list arm above was enumerated from
    the same intuition as the rule it guarded, and a fixture derived from the rule cannot disagree
    with the rule.
    """
    out = set()
    row = cm.ROW_MEASUREMENT_ID
    for field in universe:
        for i in range(1, len(field) + 1):
            out.add(field[:i])
            out.add(field[:i] + cm.WILDCARD)
        if field.startswith(row + "["):
            inner = field[len(row) + 1:field.index("]")]
            tail = field[field.index("]") + 1:]
            out.add(f"{row}[{cm.WILDCARD}]{tail}")
            out.add(f"{row}[{inner}].{cm.WILDCARD}")
        else:
            out.add(field[:3] + "." + cm.WILDCARD)
    return sorted(out)


class R4_ThePatternGrammarIsPositiveNotADenyList(BenchCase):
    """D-3. The expected-list guard was FAIL-OPEN on `M-1[*`, the per-file form missing its `]`.

    The breadth test was `pattern.rsplit(".", 1)[-1] in ("*", "**")`. A dotless pattern has no last
    segment, so the whole of `M-1[*` was compared against `"*"`, passed the guard, and reached
    `field_matches`, which reads it as prefix `M-1[` with an empty suffix and matches EVERY M-1
    field. Measured on the real far-end inputs with a genuine one-line citation: all 19 M-1
    findings suppressed as EXPECTED-BY-RULING, expected 0 -> 19, with no warning and no refusal.
    See section 8.3 of `DECISION-20260825-joseph-gate2-fail-and-four-rulings.md`.

    THE REPAIR IS A GRAMMAR, NOT A SEVENTH SPELLING, so the arms below are a sweep over generated
    candidates and a converse sweep over the producer's own output -- not a longer list.
    """

    def setUp(self):
        super().setUp()
        # THE PRODUCER, not a retyped universe: the field paths `flatten` emits for a real document.
        self.universe = sorted(cm.flatten(base_document("X", "/t"), 0))

    def reach(self, pattern):
        """What `field_matches` -- the component that would exploit a hole -- actually matches."""
        return [f for f in self.universe if cm.field_matches(pattern, f)]

    def over_broad(self, pattern):
        """Over-broad is a property of what a pattern REACHES, never of how it is spelled.

        Two fields with different field NAMES means the entry swallows more than one field of an
        object; any M-2 reach means it touches the perishable claim. Both come from the design's
        stated purpose, not from `bad_pattern`'s text, so this predicate can disagree with the
        guard.
        """
        reached = self.reach(pattern)
        return (len({_terminal_name(f) for f in reached}) > 1
                or any(f.startswith(cm.PERISHABLE_ID) for f in reached))

    def test_the_D3_pattern_is_REFUSED_end_to_end__fires_on_bad(self):
        """Through `main`, because a guard that refuses only in-process refuses nobody."""
        expected = self.bench.write_expected(self.bench.may_differ(["M-1[*"]))
        code, record, err = self.bench.run(
            self.two(lambda d: d["M-1"][0].__setitem__("first_insert", 99)), expected)
        self.assertEqual(code, cm.EXIT_REFUSAL_EXPECTED_LIST)
        self.assertIsNone(record, "a refused list must emit no record at all")
        self.assertIn("never closed", err)

    def test_the_D3_pattern_really_WOULD_have_swallowed_M1__the_power_control(self):
        """Without this the arm above proves only that SOMETHING was refused.

        A control that shows the instrument works leaves the claim untested. This one shows the
        FIXTURE can carry the failure: unguarded, `M-1[*` reaches several M-1 fields with distinct
        field names and nothing outside M-1 -- the shape of the real 19-finding suppression.
        """
        reached = self.reach("M-1[*")
        self.assertGreaterEqual(len(reached), 2)
        self.assertGreater(len({_terminal_name(f) for f in reached}), 1)
        self.assertEqual({f[:3] for f in reached}, {cm.ROW_MEASUREMENT_ID})
        self.assertTrue(self.over_broad("M-1[*"))

    def test_every_OVER_BROAD_candidate_the_PRODUCER_generates_is_refused(self):
        """The covering control. Measured 2026-08-25: 721 candidates, 96 over-broad, 0 accepted.

        The population is stated beside the count because a sweep that swept nothing also reports
        zero escapes.
        """
        candidates = _candidate_patterns(self.universe)
        self.assertIn("M-1[*", candidates)          # the fixture contains the known failure
        broad = [p for p in candidates if self.over_broad(p)]
        self.assertGreaterEqual(len(broad), 50,
                                f"only {len(broad)} over-broad candidates of {len(candidates)}: "
                                f"this sweep would pass vacuously")
        escaped = [p for p in broad if cm.bad_pattern(p) is None]
        self.assertEqual(escaped, [], f"{len(escaped)} of {len(broad)} over-broad patterns accepted")

    def test_every_field_the_PRODUCER_emits_is_accepted_verbatim__silent_on_good(self):
        """The converse sweep, and the arm that fails if the repair over-tightens.

        A guard that rejected everything would pass every firing arm above. Each field the
        instrument can actually report must be nameable as its own whitelist pattern -- except
        M-2's, which must stay refused.
        """
        self.assertGreaterEqual(len(self.universe), 20)
        for field in self.universe:
            with self.subTest(field=field):
                why = cm.bad_pattern(field)
                if field.startswith(cm.PERISHABLE_ID):
                    self.assertIsNotNone(why)
                else:
                    self.assertIsNone(why, why)

    def test_the_PER_FILE_wildcard_form_is_accepted_for_every_row_field__silent_on_good(self):
        """`M-1[*].<field>` is the documented per-file form and must survive the repair."""
        widened = {f"{cm.ROW_MEASUREMENT_ID}[{cm.WILDCARD}].{_terminal_name(f)}"
                   for f in self.universe if f.startswith(cm.ROW_MEASUREMENT_ID + "[")}
        self.assertGreaterEqual(len(widened), 3)
        for pattern in sorted(widened):
            with self.subTest(pattern=pattern):
                self.assertIsNone(cm.bad_pattern(pattern), cm.bad_pattern(pattern))

    def test_a_PARTIAL_selector_wildcard_still_narrows_end_to_end__silent_on_good(self):
        """The wildcard stays legal in SELECTOR space, where it ranges over files.

        It cannot widen past the already-legal bare `*`, so allowing it costs nothing in the
        direction that loses information.
        """
        expected = self.bench.write_expected(
            self.bench.may_differ([f"{cm.ROW_MEASUREMENT_ID}[nd-unfolding/boot*].first_insert"]))
        code, record, err = self.bench.run(
            self.two(lambda d: d["M-1"][0].__setitem__("first_insert", 99)), expected)
        self.assertEqual(code, cm.EXIT_DIFFERENCES_ALL_EXPECTED, err)
        self.assertEqual(record["findings"][0]["classification"], "EXPECTED-BY-RULING")
        self.assertEqual(record["findings"][0]["field"],
                         "M-1[nd-unfolding/bootstrap_nd.py].first_insert")

    def test_a_pattern_that_can_match_NOTHING_is_refused__the_opposite_direction(self):
        """The other direction a whitelist fails in: a row that reads as cover and never applies.

        Each of these was ACCEPTED by the predecessor guard and reaches nothing. That is the
        F-17(a) failure `field_matches` exists to fix, arriving through the guard instead of
        through `fnmatch`. Note the narrower claim this arm makes: it is about patterns that cannot
        match the field they NAME, not about patterns whose field is merely absent today -- the
        latter is legitimate and is surfaced by `expected_entries_unused`, not refused.
        """
        for pattern in ("M-1[", "M-1[*]", "M-1[].present", "M-1.present", "M-3[rc].x", "M-1[*]."):
            with self.subTest(pattern=pattern):
                self.assertEqual(self.reach(pattern), [], "fixture: this must reach nothing")
                self.assertIsNotNone(cm.bad_pattern(pattern))

    def test_a_wildcard_in_the_FIELD_NAME_is_refused_even_when_it_narrows_today(self):
        """A STATED BEHAVIOUR CHANGE, deliberate and not an edge case.

        `M-4.behin*` reaches exactly one field name in today's documents, so a breadth-measuring
        guard would pass it -- and it silently widens the day `measure_m1_m6.py` adds a field
        beginning `behin`. The class is made unreachable instead of checked for: the wildcard is a
        selector-space device and the terminal field name is always literal. Measured 2026-08-25:
        265 of 721 generated candidates are refused although they reach exactly one field name.
        """
        pattern = "M-4.behin*"
        self.assertEqual({_terminal_name(f) for f in self.reach(pattern)}, {"behind"})
        why = cm.bad_pattern(pattern)
        self.assertIsNotNone(why)
        self.assertIn("SELECTOR-space", why)

    def test_the_matcher_BACKSTOP_fires_where_bad_pattern_cannot_reach_it(self):
        """The inner guard, exercised directly, because through `bad_pattern` it is unreachable.

        `parse_pattern` refuses `M-1[*` before `matcher_disagreement` ever sees it. Scoring the
        backstop 'covered' through `bad_pattern` would be scoring the grammar twice -- the same
        mistake this file records at `evaluate_rule`, where deleting an inner guard changed no test
        result and the survey called it caught. So this arm hands `matcher_disagreement` the parse
        a HOLE in the grammar would produce, which is exactly D-3, and checks it fires in both
        directions and stays silent on a sound pattern.
        """
        hole = {"measurement": "M-1", "selector": "*", "field": "first_insert"}
        why = cm.matcher_disagreement("M-1[*", hole)
        self.assertIsNotNone(why, "the backstop did not catch a re-introduced D-3")
        self.assertIn("OVER-BROAD", why)

        dead = {"measurement": "M-4", "selector": None, "field": "behind"}
        why = cm.matcher_disagreement("M-4.nothing_like_it", dead)
        self.assertIsNotNone(why)
        self.assertIn("matches NOTHING", why)

        sound = {"measurement": "M-1", "selector": "*", "field": "first_insert"}
        self.assertIsNone(cm.matcher_disagreement("M-1[*].first_insert", sound))

    def test_the_UNITS_TABLE_and_the_grammar_are_the_same_language(self):
        """`UNITS` is the other in-tree producer of patterns in this language, and it is matched by
        the same `field_matches`. If the grammar could not parse a shipped UNITS pattern, the guard
        and the units table would be describing two different languages again."""
        self.assertTrue(cm.UNITS)
        for pattern, _unit, _population in cm.UNITS:
            with self.subTest(pattern=pattern):
                parsed, why = cm.parse_pattern(pattern)
                self.assertIsNone(why, why)
                self.assertIn(parsed["measurement"], cm.MEASUREMENT_IDS)
                self.assertNotIn(cm.WILDCARD, parsed["field"])


class R4_TheShippedListInThisRepository(unittest.TestCase):
    """The shipped whitelist is itself under test, in both directions."""

    LIST = _HERE / "m1m6_expected_differences.json"
    REPO = _HERE.parents[1]
    # The filed F-17(b) record. READ ONLY: it is digest-bound and immutable, and its content
    # sha256 is pinned in section 11 of DECISION-20260825-joseph-gate2-fail-and-four-rulings.md.
    FILED_RECORD = _HERE / "state" / "f17b-k0-aa67c426-20260824T145751Z.json"
    FILED_RECORD_SHA256_8 = "9109f371"

    def test_the_D3_pattern_over_the_REAL_FILED_RECORD_is_refused(self):
        """The defect was demonstrated on real far-end inputs, so the repair is measured there too.

        This reads the filed record and never writes it; the digest arm below is what says so. The
        19 is not retyped from the decision record -- it is recounted here from the record's own
        findings, and it is the measured blast radius: `M-1[*` reaches exactly the M-1 findings and
        nothing else, which is how 19 differences became EXPECTED-BY-RULING with expected 0 -> 19.
        """
        self.assertTrue(self.FILED_RECORD.is_file(), self.FILED_RECORD)
        self.assertTrue(sha256_bytes(self.FILED_RECORD).startswith(self.FILED_RECORD_SHA256_8),
                        "the filed record has MOVED; it is immutable and this arm is read-only")
        findings = json.loads(self.FILED_RECORD.read_text(encoding="utf-8"))["findings"]
        fields = [f["field"] for f in findings]
        m1 = [f for f in fields if f.startswith(cm.ROW_MEASUREMENT_ID)]
        reached = [f for f in fields if cm.field_matches("M-1[*", f)]
        self.assertEqual(reached, m1)
        self.assertEqual(len(reached), 19)
        self.assertLess(len(reached), len(fields))
        self.assertIsNotNone(cm.bad_pattern("M-1[*"),
                             "D-3 is open again against the artifact it was measured on")

    def test_every_field_in_the_FILED_RECORD_is_nameable_one_at_a_time__silent_on_good(self):
        """The converse against real data: closing D-3 must not cost the ability to declare a real
        difference. Every field the filed record reports is accepted as its own pattern, and only
        M-2's are refused."""
        findings = json.loads(self.FILED_RECORD.read_text(encoding="utf-8"))["findings"]
        fields = [f["field"] for f in findings]
        self.assertEqual(len(fields), 32)
        for field in fields:
            with self.subTest(field=field):
                accepted = cm.bad_pattern(field) is None
                self.assertEqual(accepted, not field.startswith(cm.PERISHABLE_ID))

    def test_every_shipped_entry_RESOLVES_against_this_repository(self):
        loaded = cm.load_expected(str(self.LIST), self.REPO)
        self.assertTrue(loaded["entries"])
        for entry in loaded["entries"]:
            with self.subTest(entry=entry["id"]):
                self.assertEqual(sorted(entry["citations"]), sorted(entry["fields"]))
                for pattern, citation in entry["citations"].items():
                    self.assertTrue(citation["matched_lines"], pattern)
                    self.assertEqual(len(citation["doc_sha256_measured"]), 64)

    def test_the_shipped_list_does_NOT_whitelist_M1_M5_or_M6__the_rejected_bullet(self):
        """A DENY-LIST over remembered spellings. Kept, but it is NOT the guard -- see the covering
        control below, which is.

        THIS ARM WAS BLIND IN THE M-1 DIRECTION AND ITS DOCSTRING CLAIMED OTHERWISE. It matched with
        `fnmatch.fnmatchcase`, and M-1 field paths contain brackets, so `M-1[*].literals` read as a
        character class and matched nothing: the rejected bullet, re-added in per-file wildcard form
        with well-formed citations, suppressed four M-1 findings at exit 10 with all 53 arms green.
        That is the exact bug `compare_m1_m6.py`'s `field_matches` was written to fix, retyped in the
        test that guards the whitelist -- and `fnmatch` is on the forbidden-import list nine lines
        into this same file. A rule retyped is a second implementation of it, written from the rule's
        summary, and the summary is the naive reading. It now CALLS `cm.field_matches`.

        Measured 2026-08-25 at 49dbdf8f: 10 of the 46 commits in
        8c156a37..build-k0-execution-integrity touch any file in the M-1, M-5 or M-6 populations,
        so 'falsified by any commit' is false -- and as a whitelist entry it would have suppressed
        M-1's dropped tenth entrypoint and M-5's 0-of-8 against 8-of-8, which are the F-17(a)
        findings against the builder.
        """
        loaded = cm.load_expected(str(self.LIST), self.REPO)
        patterns = [p for entry in loaded["entries"] for p in entry["fields"]]
        for field in ("M-1[nd-unfolding/bootstrap_nd.py].literals",
                      "M-1[nd-unfolding/unified_throw_cov.py].present",
                      "M-1[nd-unfolding/seedscan_split.py].n_after",
                      "M-5.repo_assign", "M-5.activator_from_env_root", "M-5.missing",
                      "M-6.state", "M-6.inventory_write_lines", "M-6.n_lines",
                      "M-4.head", "M-4.dirty", "M-4.upstream",
                      # REMOVED from the shipped entry 2026-08-25: its citation recorded
                      # `ahead = 0 ; --is-ancestor rc=0`, a stable zero, so the quote licensing it
                      # said the OPPOSITE of the field. Re-adding it needs a citation about ahead.
                      "M-4.ahead"):
            with self.subTest(field=field):
                self.assertFalse([p for p in patterns if cm.field_matches(p, field)],
                                 f"{field} must never be pre-declared expected")

    def test_an_M4_ahead_difference_SURFACES_as_a_finding_under_the_shipped_list(self):
        """The removal, pinned behaviourally rather than by reading the file.

        Pattern-coverage arms check the list's SHAPE. This one runs the instrument against the real
        shipped file and asserts the consequence: a tree whose `ahead` differs produces an
        UNEXPECTED finding and the some-unexpected exit. Re-adding `M-4.ahead` to the whitelist
        without a citation about ahead turns this red.
        """
        import subprocess
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            tmp = pathlib.Path(tmp)
            paths = []
            for label, ahead in (("CANDIDATE", 0), ("CANONICAL", 4)):
                doc = base_document(label, f"/trees/{label}")
                doc["M-4"]["ahead"] = ahead
                path = tmp / f"{label}.json"
                path.write_text(json.dumps(doc), encoding="utf-8")
                paths.append(str(path))
            proc = subprocess.run(
                [sys.executable, str(_HERE / "compare_m1_m6.py"),
                 "--input", paths[0], "--input", paths[1],
                 "--expected", str(self.LIST), "--repo", str(self.REPO), "--json"],
                capture_output=True, text=True)
        self.assertEqual(proc.returncode, 20, proc.stderr)
        record = json.loads(proc.stdout)
        finding, = record["findings"]
        self.assertEqual(finding["field"], "M-4.ahead")
        self.assertEqual(finding["classification"], "UNEXPECTED")
        self.assertEqual(finding["expected_entries_matched"], [])
        self.assertEqual([side["value"] for side in finding["sides"]], [0, 4])
        self.assertIn("commits, DRIFTING", finding["unit"])

    @unittest.skipIf(sys.version_info < (3, 10), "measure_m1_m6.py refuses below 3.10")
    def test_ONLY_M4_BEHIND_IS_SUPPRESSIBLE_over_a_MEASURED_field_universe(self):
        """The covering control, and the reason a deny-list could not be it.

        A deny-list fails on the widenings someone thought to type. This one takes the field universe
        from a REAL `measure_m1_m6.py --json` document -- a tree built to populate every measurement,
        including a git repo with an upstream ref so M-4 is whole -- matches it with the instrument's
        own `field_matches`, and asserts that the set of fields the shipped whitelist can suppress is
        EXACTLY {M-4.behind}. Any widening fires it, in any spelling, however well cited: the M-1
        wildcard form that walked through the deny-list, and the one-character-quote form, are both
        caught here as well as by their own guards.
        """
        import subprocess
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            tree = pathlib.Path(tmp) / "tree"
            (tree / "nd-unfolding").mkdir(parents=True)
            (tree / "2d-unfolding").mkdir(parents=True)
            for rel in mm.M1_FILES:
                (tree / rel).write_text("import sys\nsys.path.insert(0, '/x')\n", encoding="utf-8")
            for name in mm.LAUNCHERS:
                (tree / "nd-unfolding" / name).write_text(
                    'REPO=/x\nsource "${ENV_ROOT}/setup_salloc_env.sh"\n', encoding="utf-8")
            (tree / "nd-unfolding" / "mnv_guarded_run.py").write_text(
                'self.checked = 0\nrec = {"checked": guard.checked if guard else 0}\n',
                encoding="utf-8")
            # M-3's PRECONDITION. Without this file `m3()` returns {"present": false} alone, so
            # M-3.rc and M-3.all_intact never enter the universe -- and a widening of the shipped
            # list over M-3.rc survived this very control until the omission was measured. A
            # covering control that does not populate every conditional field does not cover.
            (tree / "docs" / "orchestration").mkdir(parents=True)
            (tree / "docs" / "orchestration" / "verify_hash_bindings.py").write_text(
                'print("ALL BINDINGS INTACT")\n', encoding="utf-8")
            git = ["git", "-C", str(tree)]
            subprocess.run(git + ["init", "-q"], check=True, capture_output=True)
            subprocess.run(git + ["-c", "user.name=t", "-c", "user.email=t@t",
                                  "commit", "-q", "--allow-empty", "-m", "t"],
                           check=True, capture_output=True)
            subprocess.run(git + ["update-ref", "refs/remotes/origin/main", "HEAD"],
                           check=True, capture_output=True)
            proc = subprocess.run([sys.executable, str(_HERE / "measure_m1_m6.py"),
                                   "--tree", str(tree), "--label", "universe", "--json"],
                                  capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            document = json.loads(proc.stdout)

        universe = sorted(cm.flatten(document, 0))
        # The universe must actually be populated, or this control passes by being empty.
        self.assertGreater(len(universe), 50)
        # EVERY CONDITIONALLY-PRESENT FIELD, named. These are the fields `measure_m1_m6.py` omits
        # rather than reports as false when a precondition fails, so they are exactly the ones a
        # universe can silently lack. The residual, stated: a NEW conditional field added to the
        # measuring tool would not appear here, and this list would not notice.
        for required in ("M-1[nd-unfolding/bootstrap_nd.py].present",
                         "M-1[nd-unfolding/bootstrap_nd.py].literals",
                         "M-1[nd-unfolding/bootstrap_nd.py].first_insert",
                         "M-1[nd-unfolding/bootstrap_nd.py].repo_modules_after",
                         "M-1[nd-unfolding/bootstrap_nd.py].n_after",
                         "M-2.importable", "M-2.stdlib_collisions", "M-2.python",
                         "M-3.present", "M-3.rc", "M-3.all_intact",
                         "M-4.is_git", "M-4.head", "M-4.dirty", "M-4.untracked", "M-4.modified",
                         "M-4.behind", "M-4.ahead", "M-4.upstream",
                         "M-5.n", "M-5.missing", "M-5.repo_assign",
                         "M-5.activator_from_code_root", "M-5.activator_from_env_root",
                         "M-6.present", "M-6.n_lines", "M-6.counts_resolutions",
                         "M-6.inventory_write_lines", "M-6.else_zero_default_lines", "M-6.state"):
            self.assertIn(required, universe, "the universe does not cover this field, so a "
                                              "widening over it would pass unseen")
        for measurement in cm.MEASUREMENT_IDS:
            self.assertTrue([f for f in universe if f.startswith(measurement)], measurement)

        patterns = [p for entry in cm.load_expected(str(self.LIST), self.REPO)["entries"]
                    for p in entry["fields"]]
        suppressible = {field for field in universe
                        if any(cm.field_matches(pattern, field) for pattern in patterns)}
        self.assertEqual(suppressible, {"M-4.behind"},
                         "the shipped whitelist may suppress exactly one field of the measured "
                         "universe; anything else is a widening")

    def test_the_shipped_list_DOES_cover_the_drifting_counts__silent_on_good(self):
        loaded = cm.load_expected(str(self.LIST), self.REPO)
        patterns = [p for entry in loaded["entries"] for p in entry["fields"]]
        for field in ("M-4.behind",):
            with self.subTest(field=field):
                self.assertTrue([p for p in patterns if cm.field_matches(p, field)])


# --------------------------------------------------------------------------------------------- R5

class R5_AgreementIsJointAndIsNeverComposedFromPairs(BenchCase):

    def three(self, behinds):
        paths = []
        for index, (label, behind) in enumerate(zip(("A", "B", "C"), behinds)):
            doc = base_document(label, f"/trees/{label}")
            doc["M-4"]["behind"] = behind
            paths.append(self.bench.write_doc(f"t{index}.json", doc))
        return paths

    def tolerant(self, value):
        return self.bench.write_expected(
            [{"id": "E-tol", "fields": ["M-4.behind"],
              "rule": {"kind": "max-abs-delta", "value": value},
              "citation": self.bench.citation(), "why": "a tolerance fixture"}])

    def test_pairwise_CONSISTENT_but_jointly_INCONSISTENT_does_not_get_a_global_agreement(self):
        """FIRES. The ordering is the point: a baseline-relative pass sees nothing here."""
        values = [3, 0, 6]
        self.assertLessEqual(abs(values[0] - values[1]), 4)     # negative control on the fixture:
        self.assertLessEqual(abs(values[0] - values[2]), 4)     # input 0 is inside tolerance of both
        self.assertGreater(abs(values[1] - values[2]), 4)       # while the joint spread is not
        code, record, _ = self.bench.run(self.three(values), self.tolerant(4))
        self.assertEqual(code, cm.EXIT_DIFFERENCES_SOME_UNEXPECTED)
        self.assertFalse(record["summary"]["all_agree"])
        self.assertFalse(record["global_agreement_inferred_from_pairs"])
        finding, = record["findings"]
        self.assertEqual(finding["classification"], "UNEXPECTED")
        detail = finding["expected_entries_matched"][0]["rule_detail"]
        self.assertEqual(detail["joint_spread"], 6)
        self.assertIn("never composed from pairs", detail["note"])

    def test_a_joint_spread_INSIDE_the_tolerance_is_expected__silent_on_good(self):
        code, record, _ = self.bench.run(self.three([3, 4, 5]), self.tolerant(4))
        self.assertEqual(code, cm.EXIT_DIFFERENCES_ALL_EXPECTED)
        self.assertEqual(record["findings"][0]["classification"], "EXPECTED-BY-RULING")
        self.assertEqual(record["findings"][0]["expected_entries_matched"][0]
                         ["rule_detail"]["joint_spread"], 2)

    def test_MAY_DIFFER_ITSELF_fails_closed_on_ABSENT__the_unreachable_second_mechanism(self):
        """Called DIRECTLY, because `compare` short-circuits absence before any rule is consulted.

        Deleting this check changed no test result until this arm existed -- the same shape as the
        M-2 classify-time guard, and the same lesson: a guard behind a guard needs an arm that calls
        it, or the survey scores it caught on the outer one's evidence.
        """
        satisfied, detail = cm.evaluate_rule({"kind": "may-differ"}, [5, cm.ABSENT])
        self.assertFalse(satisfied)
        self.assertIn("never about it being missing", detail["reason"])
        satisfied, _ = cm.evaluate_rule({"kind": "may-differ"}, [5, 9])
        self.assertTrue(satisfied)
        satisfied, _ = cm.evaluate_rule({"kind": "max-abs-delta", "value": 100}, [5, cm.ABSENT])
        self.assertFalse(satisfied)

    def test_three_identical_documents_DO_agree_and_the_mode_says_it_was_joint(self):
        code, record, _ = self.bench.run(self.three([3, 3, 3]), self.tolerant(4))
        self.assertEqual(code, cm.EXIT_NO_DIFFERENCES)
        self.assertTrue(record["summary"]["all_agree"])
        self.assertEqual(record["n_inputs"], 3)
        self.assertIn("JOINT over all n inputs", record["comparison_mode"])

    def test_a_tolerance_over_a_NON_NUMERIC_value_fails_closed(self):
        first = base_document("A", "/trees/A")
        second = base_document("B", "/trees/B")
        second["M-4"]["behind"] = "many"
        paths = (self.bench.write_doc("x.json", first), self.bench.write_doc("y.json", second))
        code, record, _ = self.bench.run(paths, self.tolerant(1000))
        self.assertEqual(code, cm.EXIT_DIFFERENCES_SOME_UNEXPECTED)
        finding, = [f for f in record["findings"] if f["field"] == "M-4.behind"]
        self.assertEqual(finding["classification"], "UNEXPECTED")
        self.assertIn("failing closed",
                      finding["expected_entries_matched"][0]["rule_detail"]["reason"])

    def test_an_ABSENT_value_is_classified_before_the_rule_is_even_consulted(self):
        """G-3, at the tolerance surface: absence short-circuits, so no rule can license it."""
        first = base_document("A", "/trees/A")
        second = base_document("B", "/trees/B")
        del second["M-4"]["behind"]
        paths = (self.bench.write_doc("x.json", first), self.bench.write_doc("y.json", second))
        code, record, _ = self.bench.run(paths, self.tolerant(1000))
        self.assertEqual(code, cm.EXIT_DIFFERENCES_SOME_UNEXPECTED)
        finding, = [f for f in record["findings"] if f["field"] == "M-4.behind"]
        self.assertEqual(finding["classification"], "UNEXPECTED")
        self.assertTrue(finding["absent_from_some_input"])
        self.assertEqual(finding["expected_entries_matched"], [])
        self.assertIn("MISSING from at least one document", finding["reason"])


# --------------------------------------------------------------------------------------------- R6

class R6_TheRecordCarriesItsOwnOperands(BenchCase):

    def test_the_record_lets_a_reader_reconstruct_WHICH_files_were_compared(self):
        first, second = self.two(lambda d: d["M-6"].__setitem__("state", "NO INVENTORY WRITE"))
        out = self.bench.root / "record.json"
        code, _, _ = self.bench.run([first, second], self.expected_ok,
                                    extra=("--record", str(out)))
        self.assertEqual(code, cm.EXIT_DIFFERENCES_SOME_UNEXPECTED)
        record = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual([side["input_sha256"] for side in record["inputs"]],
                         [sha256_bytes(first), sha256_bytes(second)])
        self.assertEqual([side["input_path"] for side in record["inputs"]],
                         [str(pathlib.Path(first).resolve()), str(pathlib.Path(second).resolve())])
        self.assertEqual(record["instrument"]["self_sha256"],
                         sha256_bytes(_HERE / "compare_m1_m6.py"))
        self.assertEqual(record["instrument"]["version"], cm.INSTRUMENT_VERSION)
        self.assertEqual(record["expected_list"]["sha256"], sha256_bytes(self.expected_ok))
        self.assertRegex(record["generated_utc"], r"^20\d\d-\d\d-\d\dT\d\d:\d\d:\d\dZ$")
        for side in record["inputs"]:
            self.assertRegex(side["input_file_mtime_utc"], r"^20\d\d-\d\d-\d\dT\d\d:\d\d:\d\dZ$")

    def test_the_record_pins_the_OPERAND_and_not_merely_its_PATH(self):
        """FIRES: two runs over the same paths with different contents are distinguishable."""
        first, second = self.two()
        _, before, _ = self.bench.run([first, second], self.expected_ok)
        edited = base_document("CANONICAL", "/trees/canonical")
        edited["M-4"]["dirty"] = 722
        pathlib.Path(second).write_text(json.dumps(edited, indent=2), encoding="utf-8")
        _, after, _ = self.bench.run([first, second], self.expected_ok)
        self.assertEqual(before["inputs"][1]["input_path"], after["inputs"][1]["input_path"])
        self.assertNotEqual(before["inputs"][1]["input_sha256"],
                            after["inputs"][1]["input_sha256"])
        self.assertEqual(after["inputs"][1]["input_sha256"], sha256_bytes(second))


# --------------------------------------------------------------------------------------------- R7

class R7_M2IsThePerishableClaimAndIsFlaggedApart(BenchCase):

    def test_an_M2_difference_is_flagged_distinctly_and_is_not_absorbed_into_a_count(self):
        code, record, _ = self.bench.run(
            self.two(lambda d: d["M-2"].__setitem__("importable", 119)), self.expected_ok)
        self.assertEqual(code, cm.EXIT_DIFFERENCES_SOME_UNEXPECTED)
        self.assertEqual(record["m2_perishable"]["status"], "DIFFERS")
        self.assertEqual(record["m2_perishable"]["fields"], ["M-2.importable"])
        self.assertEqual(record["summary"]["n_m2_findings"], 1)
        self.assertEqual(record["summary"]["n_unexpected"], 1)
        self.assertEqual(record["summary"]["n_unexpected_excluding_m2"], 0)

    def test_M2_CANNOT_BE_WHITELISTED_at_all(self):
        for pattern in ("M-2.importable", "M-2.stdlib_collisions", "M-2.python"):
            with self.subTest(pattern=pattern):
                expected = self.bench.write_expected(self.bench.may_differ([pattern]))
                code, _, err = self.bench.run(self.two(), expected)
                self.assertEqual(code, cm.EXIT_REFUSAL_EXPECTED_LIST)
                self.assertIn("perishable claim", err)

    def test_M2_STAYS_UNEXPECTED_even_if_a_list_somehow_covers_it__the_second_mechanism(self):
        """The arm a mutation survived, and why it was added.

        Two independent things keep an M-2 difference unsuppressible: `bad_pattern` refuses an M-2
        pattern at LOAD time, and `compare` refuses to consult the list for M-2 at CLASSIFY time.
        Deleting the second one changed no test result, because the first already blocked every
        route a fixture could take through `main`. So this arm goes around the loader and hands
        `compare` an expected list that a future loader might have let through.
        """
        first = base_document("A", "/trees/A")
        second = base_document("B", "/trees/B")
        second["M-2"]["importable"] = 119
        records = [cm.load_document(self.bench.write_doc("a.json", first), 0),
                   cm.load_document(self.bench.write_doc("b.json", second), 1)]
        smuggled = {"path": "/dev/null", "sha256": "0" * 64,
                    "entries": [{"id": "E-smuggled", "fields": ["M-2.importable"],
                                 "rule": {"kind": "may-differ"}, "why": "",
                                 "citation": {"doc": "x", "quote": "y", "matched_lines": [1],
                                              "doc_sha256_measured": "0" * 64,
                                              "doc_sha256_declared": None},
                                 "used": False}]}
        record = cm.compare(records, smuggled)
        finding, = record["findings"]
        self.assertEqual(finding["field"], "M-2.importable")
        self.assertEqual(finding["classification"], "UNEXPECTED")
        self.assertEqual(finding["expected_entries_matched"], [])
        self.assertIn("never expected and never suppressible", finding["reason"])
        self.assertEqual(record["exit_code"], cm.EXIT_DIFFERENCES_SOME_UNEXPECTED)

    def test_an_unchanged_M2_reports_IDENTICAL__silent_on_good(self):
        code, record, _ = self.bench.run(self.two(lambda d: d["M-3"].__setitem__("rc", 1)),
                                         self.expected_ok)
        self.assertEqual(code, cm.EXIT_DIFFERENCES_SOME_UNEXPECTED)
        self.assertEqual(record["m2_perishable"]["status"], "IDENTICAL-ACROSS-ALL-INPUTS")
        self.assertEqual(record["m2_perishable"]["fields"], [])


@unittest.skipIf(sys.version_info < (3, 10),
                 "measure_m1_m6.py refuses below 3.10, and correctly")
class R7_AgainstRealDocumentsFromTheRealMeasuringTool(unittest.TestCase):
    """The one arm whose fixtures the instrument cannot have shaped.

    It builds a tree, runs the REAL `measure_m1_m6.py` on it, drops one untracked `.py` whose stem
    collides with a stdlib name, runs it again, and compares the two real documents. This also
    independently re-derives the SPEC's one held finding: M-2's zero rests on an UNTRACKED
    population, because `repo_modules()` globs and a glob does not consult git.
    """

    def setUp(self):
        self._stack = contextlib.ExitStack()
        self.addCleanup(self._stack.close)
        self.bench = Bench(self._stack)
        self.tree = self.bench.root / "measured"
        (self.tree / "nd-unfolding").mkdir(parents=True)
        (self.tree / "2d-unfolding").mkdir(parents=True)
        (self.tree / "nd-unfolding" / "omnifold.py").write_text("x = 1\n", encoding="utf-8")

    def measure(self, name):
        out = self.bench.root / name
        proc = subprocess.run([sys.executable, str(_HERE / "measure_m1_m6.py"),
                               "--tree", str(self.tree), "--label", name, "--json"],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        out.write_text(proc.stdout, encoding="utf-8")
        return str(out)

    def test_dropping_an_UNTRACKED_stdlib_colliding_py_flips_M2_and_the_flag_fires(self):
        before = self.measure("before")
        (self.tree / "nd-unfolding" / "json.py").write_text("y = 2\n", encoding="utf-8")
        after = self.measure("after")
        self.assertEqual(json.loads(pathlib.Path(before).read_text())["M-2"]["stdlib_collisions"],
                         [])
        self.assertEqual(json.loads(pathlib.Path(after).read_text())["M-2"]["stdlib_collisions"],
                         ["json"])
        expected = self.bench.write_expected(self.bench.may_differ(["M-4.behind"]))
        code, record, _ = self.bench.run([before, after], expected)
        self.assertEqual(code, cm.EXIT_DIFFERENCES_SOME_UNEXPECTED)
        self.assertEqual(record["m2_perishable"]["status"], "DIFFERS")
        self.assertEqual(sorted(record["m2_perishable"]["fields"]),
                         ["M-2.importable", "M-2.stdlib_collisions"])
        self.assertEqual(record["summary"]["n_unexpected_excluding_m2"], 0)

    def test_the_same_tree_measured_twice_UNCHANGED_agrees__silent_on_good(self):
        first, second = self.measure("first"), self.measure("second")
        expected = self.bench.write_expected(self.bench.may_differ(["M-4.behind"]))
        code, record, _ = self.bench.run([first, second], expected)
        self.assertEqual(code, cm.EXIT_NO_DIFFERENCES)
        self.assertEqual(record["m2_perishable"]["status"], "IDENTICAL-ACROSS-ALL-INPUTS")
        self.assertGreater(record["fields_compared"], 10)


# --------------------------------------------------------------------------------------------- R8

class R8_TheExitVocabularyIsDisjointAndDocumented(BenchCase):

    def test_each_code_is_produced_by_exactly_the_condition_it_names(self):
        cases = []
        cases.append((cm.EXIT_NO_DIFFERENCES, self.two(), self.expected_ok))
        cases.append((cm.EXIT_DIFFERENCES_ALL_EXPECTED,
                      self.two(lambda d: d["M-4"].__setitem__("behind", 168)), self.expected_ok))
        cases.append((cm.EXIT_DIFFERENCES_SOME_UNEXPECTED,
                      self.two(lambda d: d["M-4"].__setitem__("head", "b" * 40)),
                      self.expected_ok))
        cases.append((cm.EXIT_REFUSAL_INPUT,
                      (self.two()[0], str(self.bench.root / "gone.json")), self.expected_ok))
        cases.append((cm.EXIT_REFUSAL_EXPECTED_LIST, self.two(),
                      self.bench.write_expected(self.bench.may_differ(["M-4.*"]))))
        for want, inputs, expected in cases:
            with self.subTest(code=want):
                code, _, _ = self.bench.run(inputs, expected)
                self.assertEqual(code, want)
                self.assertIsInstance(code, int)

    def test_a_usage_error_is_argparse_s_own_2_and_nothing_else(self):
        for argv in ([], ["--input", "a.json"], ["--expected", "e.json"]):
            with self.subTest(argv=argv):
                with contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit) as caught:
                        cm.main(argv)
                self.assertEqual(caught.exception.code, 2)

    def test_the_FIVE_VERDICTS_ARE_THE_LITERAL_INTEGERS__an_oracle_that_cannot_move(self):
        """The arm the first version of this suite did not have, and the hole it left.

        A peer mutated `EXIT_DIFFERENCES_SOME_UNEXPECTED` to 10, collapsing "some unexpected" onto
        "all expected". Measured: 13 references to that constant in this file and ZERO assertions
        against the literal 20 -- so every behavioural arm compared the observed exit against the
        constant under test, the oracle moved with the mutation, and the only arm that caught it
        caught it through the help TEXT. A fixture derived from the rule cannot disagree with the
        rule. These five assertions are LITERALS on purpose and must never be re-expressed as
        module constants.

        AND THE HELP-TEXT ARM WAS LUCK, not a backstop. Measured against the pre-repair suite at
        74c25c3c with the bytecode cache purged: collapsing ALL-EXPECTED onto 20 instead -- the same
        defect in the other direction -- passed the whole suite, OK, zero arms. Whether that arm
        notices depends on WHICH of the two names survives the dict's silent dedup, because it
        iterates the deduped dict; the surviving pair there was one the epilog documents. Five
        vocabulary mutations, five behavioural survivors, one of them total.
        """
        self.assertEqual(self.bench.run(self.two(), self.expected_ok)[0], 0)
        self.assertEqual(self.bench.run(self.two(lambda d: d["M-4"].__setitem__("behind", 168)),
                                        self.expected_ok)[0], 10)
        self.assertEqual(self.bench.run(self.two(lambda d: d["M-4"].__setitem__("head", "b" * 40)),
                                        self.expected_ok)[0], 20)
        self.assertEqual(self.bench.run((self.two()[0], str(self.bench.root / "gone.json")),
                                        self.expected_ok)[0], 4)
        self.assertEqual(self.bench.run(self.two(), self.bench.write_expected(
            self.bench.may_differ(["M-4.*"])))[0], 5)

    def test_the_vocabulary_is_PINNED_to_literal_integers_and_names(self):
        """The table, once, as literals. A vocabulary pin whose expected values are the constants
        under test pins nothing."""
        self.assertEqual(tuple(cm.EXIT_VOCABULARY),
                         ((0, "NO-DIFFERENCES"),
                          (10, "DIFFERENCES-ALL-EXPECTED"),
                          (20, "DIFFERENCES-SOME-UNEXPECTED"),
                          (4, "REFUSAL-INPUT"),
                          (5, "REFUSAL-EXPECTED-LIST")))
        self.assertEqual(cm.EXIT_CODES, dict(cm.EXIT_VOCABULARY))
        self.assertEqual(cm.RESERVED_EXIT_CODES.keys(), {1: "", 2: ""}.keys())

    def test_a_COLLISION_is_REPRESENTABLE_in_the_sequence_and_is_refused(self):
        """FIRES on each collapsed vocabulary, SILENT on a sound one.

        The assertion this replaces was `len(set(cm.EXIT_CODES)) == len(cm.EXIT_CODES)`, which is
        TRUE OF EVERY DICT: a dict literal had already deduped 20 onto 10 before the test ran, so it
        compared 4 against 4 and had zero power in either direction. Over a sequence of pairs the
        collision exists to be found.
        """
        for bad, why in ((((0, "A"), (10, "B"), (10, "C")), "two verdicts on one code"),
                         (((0, "A"), (10, "A")), "one name on two codes"),
                         (((0, "A"), (1, "B")), "claiming reserved 1"),
                         (((0, "A"), (2, "B")), "claiming reserved 2")):
            with self.subTest(case=why):
                with self.assertRaises(RuntimeError):
                    cm.check_vocabulary(bad, cm.RESERVED_EXIT_CODES)
        self.assertEqual(cm.check_vocabulary(((0, "A"), (10, "B")), cm.RESERVED_EXIT_CODES),
                         {0: "A", 10: "B"})
        codes = [code for code, _ in cm.EXIT_VOCABULARY]
        names = [name for _, name in cm.EXIT_VOCABULARY]
        self.assertEqual(len(codes), 5)
        self.assertEqual(len(set(codes)), 5)
        self.assertEqual(len(set(names)), 5)
        self.assertFalse(set(codes) & set(cm.RESERVED_EXIT_CODES))

    def test_every_code_is_documented_in_help(self):
        for code, name in cm.EXIT_CODES.items():
            with self.subTest(code=code):
                self.assertIn(name, cm.EPILOG)
                self.assertIn(f"{code:>4}  {name}", cm.EPILOG)
        self.assertIn("RESERVED", cm.EPILOG)
        self.assertIn("REFUSAL-USAGE", cm.EPILOG)

    def test_the_human_output_ends_with_the_same_verdict_the_exit_code_names(self):
        first, second = self.two(lambda d: d["M-4"].__setitem__("behind", 168))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = cm.main(["--input", first, "--input", second,
                            "--expected", self.expected_ok, "--repo", str(self.bench.repo)])
        text = out.getvalue()
        self.assertEqual(code, cm.EXIT_DIFFERENCES_ALL_EXPECTED)
        self.assertIn(f"VERDICT {cm.EXIT_CODES[code]}  exit {code}", text)
        self.assertIn("unexpected_excluding_M2=0", text)
        self.assertIn("M-2 PERISHABILITY", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
