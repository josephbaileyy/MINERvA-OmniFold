"""Tests for mnv_guard_firing_census.py -- the guard firing distribution reader.

THE FIRST TEST IS THE ONE THAT MATTERS, and it is not an entropy test. The census duplicates one
string the guard does not export -- the record schema `mnv_guard_inventory/1` -- and derives its
declared reason set by importing the guard. Both couplings are silent when they break: a schema bump
makes every real record "foreign" and the census reports BLIND, which reads exactly like a guard that
has never fired. So the first test RUNS THE REAL GUARD, takes the record it actually writes, and
asserts the census counts it. A test that hand-authored that record would agree with my code and
disagree with the producer, which is the failure this file exists to avoid.

THE SECOND THING UNDER TEST IS THE ZERO. `not measured` and `measured zero` are different facts and
the census must never collapse them: an empty population exits CENSUS_BLIND_EXIT and prints no
distribution, while a population of clean runs reports zero refusals as a MEASURED zero. Both
directions are asserted, because a guard tested in only the direction it fires waves the other
through.
"""
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
GUARD = HERE.parent / "mnv_guarded_run.py"
CENSUS = HERE.parent / "mnv_guard_firing_census.py"
REPO = HERE.parents[1]

sys.path.insert(0, str(HERE.parent))
import mnv_guard_firing_census as census  # noqa: E402
import mnv_guarded_run as mgr  # noqa: E402


def run_census(*args):
    return subprocess.run([sys.executable, str(CENSUS), *args],
                          capture_output=True, text=True)


def write_records(path: pathlib.Path, records) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r) + "\n")


def a_record(**over) -> dict:
    rec = {"schema": census.SCHEMA, "outcome": "ok", "refusal_site": None, "launch_refusal": None}
    rec.update(over)
    return rec


def a_refusal(reason, site=None) -> dict:
    return a_record(outcome=f"refused:{reason}",
                    refusal_site=site if site is not None else mgr.SITE_LAUNCH,
                    launch_refusal={"reason": reason, "argv": [], "offending_flag": "-x",
                                    "executable": None})


class TheCensusAgreesWithTheProducer(unittest.TestCase):
    """The couplings to `mnv_guarded_run` are checked against a record the GUARD wrote."""

    def test_a_record_written_by_the_real_guard_is_counted_not_treated_as_foreign(self):
        with tempfile.TemporaryDirectory() as td:
            td = pathlib.Path(td)
            inv = td / "inv.jsonl"
            child = td / "child.py"
            #: A forbidden CPython startup flag in a child launch. This is the cheapest refusal to
            #: provoke that goes all the way through `_refuse_a_launch` and writes a `reason`.
            child.write_text("import subprocess, sys\n"
                             "subprocess.run([sys.executable, '-I', '-c', 'print(1)'])\n")
            proc = subprocess.run(
                [sys.executable, str(GUARD), "--expect-root", str(REPO),
                 "--inventory", str(inv), "--", str(child)],
                capture_output=True, text=True)
            self.assertEqual(proc.returncode, 3,
                             f"the fixture must actually refuse, else this tests nothing:\n"
                             f"{proc.stdout}\n{proc.stderr}")

            written = [json.loads(l) for l in inv.read_text().splitlines() if l.strip()]
            self.assertTrue(written, "the guard wrote no record")

            #: THE SCHEMA CHECK. `census.SCHEMA` is retyped from `write_inventory`; this is the
            #: assertion that makes the duplication checked rather than trusted.
            self.assertEqual(written[-1]["schema"], census.SCHEMA,
                             "the guard's record schema no longer matches the census's pinned "
                             "SCHEMA -- every real record would be counted as foreign and the "
                             "census would report BLIND")

            c = census.Census()
            c.add_file(inv)
            self.assertEqual(c.foreign_schema, {}, "a real record was rejected as foreign")
            self.assertEqual(c.reasons[mgr.LAUNCH_REASON_FLAGS], 1)
            self.assertNotIn(mgr.LAUNCH_REASON_FLAGS, c.never_fired_reasons())
            self.assertEqual(c.undeclared_reasons(), [],
                             "the guard emitted a reason the census does not know is declared")

    def test_the_declared_set_is_read_from_the_guard_not_retyped(self):
        declared = census.declared_reasons()
        self.assertEqual(set(declared.values()),
                         {getattr(mgr, n) for n in dir(mgr) if n.startswith("LAUNCH_REASON_")})
        self.assertEqual(len(declared), 8, "the guard's reason count changed; the census tracks it "
                                           "automatically but this number is worth noticing")
        self.assertNotIn(None, census.declared_sites().values(),
                         "SITE_NONE is the absence of a site and must not be a declared one")


class TheSchemaPinHasATripwire(unittest.TestCase):
    """The pinned SCHEMA literal must fail loudly, never as a quiet BLIND."""

    def test_the_real_guard_still_contains_the_pinned_literal(self):
        #: THE POSITIVE CONTROL. If this ever fails, the census is stale against the guard and the
        #: next two tests would be asserting against a tripwire that is already tripped.
        self.assertIsNone(census.assert_schema_still_matches_the_guard())

    def test_a_guard_source_without_the_literal_trips_it(self):
        with tempfile.TemporaryDirectory() as td:
            fake = pathlib.Path(td) / "guard_without_the_schema.py"
            fake.write_text("# a guard that writes some other schema" + chr(10))
            real = mgr.__file__
            try:
                mgr.__file__ = str(fake)
                msg = census.assert_schema_still_matches_the_guard()
            finally:
                mgr.__file__ = real
        self.assertIsNotNone(msg, "the tripwire did not fire on a guard missing the literal")
        self.assertIn(census.SCHEMA, msg)
        #: The message must say what goes WRONG, not merely that something differs -- the whole
        #: point is that the operator would otherwise read a BLIND and believe it.
        self.assertIn("BLIND", msg)

    def test_drift_exits_distinctly_from_blind_so_the_two_are_never_confused(self):
        self.assertNotEqual(census.SCHEMA_DRIFT_EXIT, census.CENSUS_BLIND_EXIT)


class AZeroIsNotSelfExplanatory(unittest.TestCase):
    """`not measured` and `measured zero` must never print the same way."""

    def test_an_empty_population_is_BLIND_and_prints_no_distribution(self):
        with tempfile.TemporaryDirectory() as td:
            proc = run_census("--inventory-dir", td)
        self.assertEqual(proc.returncode, census.CENSUS_BLIND_EXIT)
        self.assertIn("BLIND", proc.stderr)
        self.assertNotIn("by launch reason", proc.stdout)
        self.assertNotIn("NEVER FIRED", proc.stdout)

    def test_a_named_file_that_does_not_exist_is_reported_not_silently_skipped(self):
        with tempfile.TemporaryDirectory() as td:
            proc = run_census("--inventory", str(pathlib.Path(td) / "absent.jsonl"))
        self.assertEqual(proc.returncode, census.CENSUS_BLIND_EXIT)
        self.assertIn("missing", proc.stderr)

    def test_clean_runs_are_a_MEASURED_zero_and_do_report_a_distribution(self):
        with tempfile.TemporaryDirectory() as td:
            inv = pathlib.Path(td) / "inv.jsonl"
            write_records(inv, [a_record(), a_record(), a_record()])
            proc = run_census("--inventory", str(inv))
        self.assertEqual(proc.returncode, 0, "records were read; this is not blind")
        self.assertIn("records           : 3", proc.stdout)
        self.assertIn("refusals          : 0", proc.stdout)
        self.assertIn("NEVER FIRED", proc.stdout,
                      "a measured zero must still name every reason that did not fire")


class AnUnreadablePopulationIsNotAnEmptyOne(unittest.TestCase):
    """A reader that degrades to BLIND on unfamiliar input reports an empty world.

    Raised by the integrator against the first version of this file, which did exactly that: an
    inventory written by a NEWER guard is well-formed, correctly located, and possibly nothing but
    firings -- and the census called it BLIND. These assert the three states stay separate.
    """

    def test_records_of_a_newer_schema_exit_DRIFT_and_not_BLIND(self):
        with tempfile.TemporaryDirectory() as td:
            inv = pathlib.Path(td) / "inv.jsonl"
            write_records(inv, [{"schema": "mnv_guard_inventory/2", "outcome": "refused:x",
                                 "launch_refusal": {"reason": "a-reason-from-a-newer-guard"}},
                                {"schema": "mnv_guard_inventory/2", "outcome": "ok"}])
            proc = run_census("--inventory", str(inv))
        self.assertEqual(proc.returncode, census.SCHEMA_DRIFT_EXIT,
                         "a population of unreadable records must not exit BLIND")
        self.assertIn("UNREADABLE", proc.stderr)
        self.assertIn("mnv_guard_inventory/2", proc.stderr,
                      "the operator must be told WHICH schema it could not read")
        #: The word BLIND appears in the message ON PURPOSE, contrasting the two states. What must
        #: be absent is the blind HEADER -- the claim itself, not the mention.
        self.assertNotIn("BLIND, NOT MEASURED", proc.stderr)

    def test_a_file_of_only_malformed_lines_is_unreadable_not_blind(self):
        with tempfile.TemporaryDirectory() as td:
            inv = pathlib.Path(td) / "inv.jsonl"
            inv.write_text("{ truncated" + chr(10) + "also not json" + chr(10))
            proc = run_census("--inventory", str(inv))
        self.assertEqual(proc.returncode, census.SCHEMA_DRIFT_EXIT)
        self.assertIn("UNREADABLE", proc.stderr)

    def test_a_genuinely_empty_population_is_still_BLIND(self):
        #: THE OPPOSITE DIRECTION. The fix above must not turn every empty run into drift.
        with tempfile.TemporaryDirectory() as td:
            proc = run_census("--inventory-dir", td)
        self.assertEqual(proc.returncode, census.CENSUS_BLIND_EXIT)
        self.assertIn("BLIND, NOT MEASURED", proc.stderr)
        self.assertNotIn("UNREADABLE", proc.stderr)

    def test_one_countable_record_beside_foreign_ones_still_reports(self):
        #: Partial readability is not drift: there is a real distribution to report, and the
        #: foreign count is disclosed in the report rather than being promoted to a refusal.
        with tempfile.TemporaryDirectory() as td:
            inv = pathlib.Path(td) / "inv.jsonl"
            write_records(inv, [a_refusal(mgr.LAUNCH_REASON_FLAGS),
                                {"schema": "mnv_guard_inventory/2", "outcome": "ok"}])
            proc = run_census("--inventory", str(inv))
        self.assertEqual(proc.returncode, 0)
        self.assertIn("NOT COUNTED", proc.stdout)

    def test_the_three_states_have_three_distinct_exits(self):
        self.assertEqual(len({0, census.CENSUS_BLIND_EXIT, census.SCHEMA_DRIFT_EXIT}), 3)


class BlindNamesWhereItLooked(unittest.TestCase):
    """Exit 2 covers two worlds; the MESSAGE must separate them even though the exit does not.

    Raised by the integrator one level above the schema fix: "the guard never fired" and "this
    reader searched a path this deployment does not use" both produce zero files. On the cluster,
    whose layout differs from main's, the second is live. The remedy is provenance, not a fourth
    exit -- so what these assert is that the two messages DIFFER, not that the codes do.
    """

    def test_an_absent_root_and_an_empty_one_do_not_produce_the_same_message(self):
        with tempfile.TemporaryDirectory() as td:
            empty = pathlib.Path(td) / "exists-empty"
            empty.mkdir()
            absent = pathlib.Path(td) / "no-such-root"
            a = run_census("--inventory-dir", str(empty))
            b = run_census("--inventory-dir", str(absent))
        self.assertEqual(a.returncode, census.CENSUS_BLIND_EXIT)
        self.assertEqual(b.returncode, census.CENSUS_BLIND_EXIT,
                         "the exit is deliberately the same; the message is what must differ")
        self.assertIn("EXISTS, EMPTY", a.stderr)
        self.assertIn("ABSENT", b.stderr)
        self.assertNotEqual(a.stderr.replace(str(empty), "X"), b.stderr.replace(str(absent), "X"),
                            "the two worlds are still indistinguishable to a reader")

    def test_a_root_that_is_a_file_is_reported_as_not_a_directory(self):
        with tempfile.TemporaryDirectory() as td:
            f = pathlib.Path(td) / "notadir"
            f.write_text("")
            proc = run_census("--inventory-dir", str(f))
        self.assertEqual(proc.returncode, census.CENSUS_BLIND_EXIT)
        self.assertIn("NOT A DIRECTORY", proc.stderr)

    def test_giving_no_source_at_all_says_so_rather_than_implying_an_empty_world(self):
        proc = run_census()
        self.assertEqual(proc.returncode, census.CENSUS_BLIND_EXIT)
        self.assertIn("NOTHING", proc.stderr)

    def test_a_successful_report_also_names_the_root_it_searched(self):
        with tempfile.TemporaryDirectory() as td:
            d = pathlib.Path(td) / "inv"
            d.mkdir()
            write_records(d / "a.jsonl", [a_refusal(mgr.LAUNCH_REASON_FLAGS)])
            proc = run_census("--inventory-dir", str(d))
        self.assertEqual(proc.returncode, 0)
        self.assertIn("SEARCHED", proc.stdout)
        self.assertIn(str(d), proc.stdout)

    def test_json_carries_the_roots_searched(self):
        with tempfile.TemporaryDirectory() as td:
            d = pathlib.Path(td) / "inv"
            d.mkdir()
            write_records(d / "a.jsonl", [a_refusal(mgr.LAUNCH_REASON_FLAGS)])
            proc = run_census("--inventory-dir", str(d), "--json")
        roots = json.loads(proc.stdout)["roots_searched"]
        self.assertEqual(len(roots), 1)
        self.assertTrue(roots[0]["exists"])
        self.assertEqual(roots[0]["files"], 1)


class TheDistribution(unittest.TestCase):

    def test_entropy_of_k_uniform_reasons_is_log2_k(self):
        import collections
        import math
        for k in (1, 2, 4, 8):
            counts = collections.Counter({f"r{i}": 10 for i in range(k)})
            self.assertAlmostEqual(census.entropy_bits(counts), math.log2(k), places=9)
            self.assertAlmostEqual(census.effective_count(counts), float(k), places=9)

    def test_an_empty_distribution_is_zero_and_does_not_raise(self):
        import collections
        self.assertEqual(census.entropy_bits(collections.Counter()), 0.0)
        self.assertEqual(census.effective_count(collections.Counter()), 0.0)

    def test_a_skewed_distribution_has_fewer_effective_reasons_than_observed(self):
        import collections
        counts = collections.Counter({"a": 999, "b": 1})
        self.assertEqual(len(counts), 2)
        self.assertLess(census.effective_count(counts), 1.2,
                        "one reason carrying 999/1000 firings means ~1 effective reason")

    def test_never_fired_is_the_declared_set_minus_the_observed_set(self):
        c = census.Census()
        c.add_record(a_refusal(mgr.LAUNCH_REASON_FLAGS))
        never = c.never_fired_reasons()
        self.assertNotIn(mgr.LAUNCH_REASON_FLAGS, never)
        self.assertIn(mgr.LAUNCH_REASON_PREEXEC, never)
        self.assertEqual(len(never), len(census.declared_reasons()) - 1)

    def test_sites_and_reasons_are_counted_separately_because_one_site_covers_eight_reasons(self):
        #: SITE_LAUNCH is written for every LAUNCH_REASON_*, so a census that counted only sites
        #: could not distinguish them. This asserts the reason axis carries what the site loses.
        c = census.Census()
        c.add_record(a_refusal(mgr.LAUNCH_REASON_FLAGS))
        c.add_record(a_refusal(mgr.LAUNCH_REASON_UNMODELLED))
        self.assertEqual(c.sites[mgr.SITE_LAUNCH], 2)
        self.assertEqual(len(c.reasons), 2)


class RecordsTheCensusCannotUse(unittest.TestCase):
    """Anything not counted must be REPORTED, because a silently dropped record is a lost firing."""

    def test_a_malformed_line_is_counted_and_does_not_abort_the_file(self):
        with tempfile.TemporaryDirectory() as td:
            inv = pathlib.Path(td) / "inv.jsonl"
            with open(inv, "w", encoding="utf-8") as fh:
                fh.write(json.dumps(a_refusal(mgr.LAUNCH_REASON_FLAGS)) + "\n")
                fh.write("{ truncated\n")
                fh.write(json.dumps(a_refusal(mgr.LAUNCH_REASON_UNPARSED)) + "\n")
            c = census.Census()
            c.add_file(inv)
        self.assertEqual(c.malformed, 1)
        self.assertEqual(c.records, 2, "a bad line must not stop the records after it")

    def test_a_foreign_schema_is_counted_separately_and_never_mixed_in(self):
        with tempfile.TemporaryDirectory() as td:
            inv = pathlib.Path(td) / "inv.jsonl"
            write_records(inv, [a_refusal(mgr.LAUNCH_REASON_FLAGS),
                                {"schema": "other/9", "outcome": "ok",
                                 "launch_refusal": {"reason": "not-ours"}}])
            c = census.Census()
            c.add_file(inv)
        self.assertEqual(c.records, 1)
        self.assertEqual(c.foreign_schema["other/9"], 1)
        self.assertNotIn("not-ours", c.reasons, "a foreign record leaked into the distribution")

    def test_a_reason_the_current_guard_does_not_declare_is_surfaced(self):
        c = census.Census()
        c.add_record(a_refusal("a-reason-from-an-older-guard"))
        self.assertEqual(c.undeclared_reasons(), ["a-reason-from-an-older-guard"])


class TheReportNamesItsOwnPopulation(unittest.TestCase):

    def test_every_file_read_is_listed_so_a_count_is_never_unscoped(self):
        with tempfile.TemporaryDirectory() as td:
            inv = pathlib.Path(td) / "inv.jsonl"
            write_records(inv, [a_refusal(mgr.LAUNCH_REASON_FLAGS)])
            proc = run_census("--inventory", str(inv))
        self.assertEqual(proc.returncode, 0)
        self.assertIn("POPULATION", proc.stdout)
        self.assertIn(str(inv), proc.stdout)

    def test_json_output_carries_the_same_numbers_as_the_text_report(self):
        with tempfile.TemporaryDirectory() as td:
            inv = pathlib.Path(td) / "inv.jsonl"
            write_records(inv, [a_refusal(mgr.LAUNCH_REASON_FLAGS),
                                a_refusal(mgr.LAUNCH_REASON_UNPARSED)])
            proc = run_census("--inventory", str(inv), "--json")
        self.assertEqual(proc.returncode, 0)
        d = json.loads(proc.stdout)
        self.assertEqual(d["records"], 2)
        self.assertEqual(d["refusals"], 2)
        self.assertAlmostEqual(d["entropy_bits"], 1.0, places=9)
        self.assertEqual(len(d["never_fired_reasons"]), len(census.declared_reasons()) - 2)


if __name__ == "__main__":
    unittest.main()
