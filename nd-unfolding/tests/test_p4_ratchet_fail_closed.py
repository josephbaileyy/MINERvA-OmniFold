#!/usr/bin/env python3
"""P-2/P-3/P-4: the ratchet's FAIL-CLOSED behaviour, which is a Gate-1 requirement.

Joseph, round 3: *"Production P-4 pins are correctly a post-rehearsal artifact, but the mechanism
and its fail-closed behavior remain Gate-1 requirements."* So what must be provable now is that an
undeclared or mismatched import set is REFUSED — not that the real pins exist. **No pins are
manufactured here**: every record below is a synthetic inventory written by this file, and the
production pins remain a post-rehearsal artifact.

WHY SYNTHETIC RECORDS AND NOT LAUNCHER RUNS. The launcher suite already proves the ratchet passes on
records a real guarded run produced. What it cannot do is produce a record that is wrong in one
chosen way — a sha256 that disagrees with the manifest, an origin outside the code root, a refusal
that leaked into a production set. Each of those is one field, and constructing it directly is the
only way to test one variable at a time.

EVERY ARM ASSERTS THE EXIT CODE **AND** THE MESSAGE. Exit 3 is reachable from a dozen causes here;
an arm that only checked the code would pass while refusing for the wrong reason, which is precisely
the defect ruling 19 found in the contract's own N-2.
"""
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
ND = HERE.parent
TOOL = ND / "mnv_import_set_ratchet.py"

OK, CANNOT_CHECK, VIOLATION = 0, 2, 3

CODE = "/code-root"
PINS_SCHEMA = "mnv_import_set_pins/1"

#: ASSEMBLED FROM PARTS, NEVER WRITTEN OUT WHOLE -- the same rule the OI-136 probe and
#: `test_oi136_failopen_inventory_ratchet.py` both state and for the same reason: the probe counts
#: `.py` files containing this literal, so a test that spells it out ADDS ITSELF to the quantity it
#: is helping to guard. The first version of this file did exactly that and moved the probe's
#: candidate count 115 -> 116. It did not move the FAIL-OPEN set, so the ratchet stayed green and
#: nothing went red -- which is why it is worth fixing rather than shrugging at.
CLUSTER_ROOT = "/" + "/".join(("pscratch", "sd", "j", "josephrb", "MINERvA-OmniFold"))


def record(script="nd-unfolding/entry.py", modules=(("victim", "aa" * 32),), **over):
    """A well-formed P-1 inventory record. Every arm below perturbs exactly one field of it."""
    origins = [{"fullname": name,
                "origin": f"{CODE}/nd-unfolding/{name}.py",
                "checkout_root": CODE,
                "sha256": digest,
                "under_expect_root": True,
                "allowed": True} for name, digest in modules]
    rec = {
        "schema": "mnv_guard_inventory/1",
        "pid": 1234,
        "expect_root": CODE,
        "allow": [],
        "allow_is_empty": True,
        "script": f"{CODE}/{script}",
        "script_checkout_root": CODE,
        "checked": 7,
        "checked_provenance": "measured-by-installed-guard",
        "refusal_site": None,
        "label": "",
        "guard_installed": True,
        "repo_origin_count": len(origins),
        "repo_origin_inventory_is_empty": not origins,
        "repo_origins_outside_expect_root": 0,
        "repo_origins": origins,
        "outcome": "ok",
        "verdict": "REPOSITORY-ORIGINS-INSPECTED",
        "sys_path_final": [],
    }
    rec.update(over)
    return rec


class Fixture(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(
            dir="/private/tmp" if os.path.isdir("/private/tmp") else None)
        self.addCleanup(self._tmp.cleanup)
        self.tmp = pathlib.Path(self._tmp.name)
        self.invdir = self.tmp / "inv"
        self.invdir.mkdir()
        self.pins = self.tmp / "pins.json"
        self.manifest = self.tmp / "srcman.json"
        self.manifest.write_text(json.dumps({
            "schema": "mnv_source_manifest/1",
            "files": {"nd-unfolding/victim.py": "aa" * 32,
                      "nd-unfolding/other.py": "bb" * 32}}))

    def write_records(self, *recs, name="run.jsonl"):
        (self.invdir / name).write_text("".join(json.dumps(r) + "\n" for r in recs))

    def write_pins(self, entrypoints):
        self.pins.write_text(json.dumps({"schema": PINS_SCHEMA, "entrypoints": entrypoints}))

    def run_tool(self, *extra, manifest=True):
        argv = [sys.executable, str(TOOL), "--inventory-dir", str(self.invdir),
                "--pins", str(self.pins), *extra]
        if manifest:
            argv += ["--source-manifest", str(self.manifest)]
        return subprocess.run(argv, capture_output=True, text=True)

    def assertRefused(self, cp, needle, code=VIOLATION):
        self.assertEqual(cp.returncode, code, cp.stdout + cp.stderr)
        self.assertIn(needle, cp.stderr, cp.stdout + cp.stderr)


class TheHappyPathReallyPasses(Fixture):
    """The silent arm, first. Without it every refusal below could come from a broken harness."""

    def test_a_well_formed_record_against_its_own_pin_is_GREEN(self):
        self.write_records(record())
        self.write_pins({"nd-unfolding/entry.py": {"modules": ["victim"]}})
        cp = self.run_tool()
        self.assertEqual(cp.returncode, OK, cp.stdout + cp.stderr)
        self.assertIn("P-2, P-3 and P-4 HOLD", cp.stdout)


class P4_IdentityNotAFloor(Fixture):
    def test_a_set_that_GREW_is_refused(self):
        self.write_records(record(modules=(("victim", "aa" * 32), ("other", "bb" * 32))))
        self.write_pins({"nd-unfolding/entry.py": {"modules": ["victim"]}})
        cp = self.run_tool()
        self.assertRefused(cp, "import set MOVED")
        self.assertIn("unexpected=['other']", cp.stderr)

    def test_a_set_that_SHRANK_is_refused_TOO_and_that_is_the_whole_point(self):
        """A floor catches collapse but permits erosion. An import that silently stopped happening
        is as much a change to what executed as one that started."""
        self.write_records(record(modules=(("victim", "aa" * 32),)))
        self.write_pins({"nd-unfolding/entry.py": {"modules": ["victim", "other"]}})
        cp = self.run_tool()
        self.assertRefused(cp, "import set MOVED")
        self.assertIn("missing=['other']", cp.stderr)

    def test_an_UNDECLARED_entrypoint_is_refused_rather_than_absorbed(self):
        self.write_records(record(script="nd-unfolding/brand_new.py"))
        self.write_pins({"nd-unfolding/entry.py": {"modules": ["victim"]}})
        cp = self.run_tool()
        self.assertRefused(cp, "no pinned import set")
        self.assertIn("brand_new.py", cp.stderr)

    def test_a_PINNED_entrypoint_with_no_inventory_is_refused(self):
        """"A missing inventory is a FAIL, not a gap" -- F-4, applied to the reader."""
        self.write_records(record())
        self.write_pins({"nd-unfolding/entry.py": {"modules": ["victim"]},
                         "nd-unfolding/never_ran.py": {"modules": ["victim"]}})
        cp = self.run_tool()
        self.assertRefused(cp, "pinned but NO inventory was produced")

    def test_the_key_is_RELATIVE_to_the_code_root_so_pins_survive_a_moved_tree(self):
        """MNV_CODE_ROOT is constituted fresh at a named sha, so an absolute key would make every
        pin single-use and a basename would collide across directories."""
        self.write_records(record(expect_root="/somewhere/else",
                                  script="nd-unfolding/entry.py",
                                  script_checkout_root="/somewhere/else"))
        # rewrite the origins to match the moved root so ONLY the key question is under test
        recs = json.loads((self.invdir / "run.jsonl").read_text().strip())
        for o in recs["repo_origins"]:
            o["origin"] = "/somewhere/else/nd-unfolding/victim.py"
            o["checkout_root"] = "/somewhere/else"
        recs["script"] = "/somewhere/else/nd-unfolding/entry.py"
        self.write_records(recs)
        self.write_pins({"nd-unfolding/entry.py": {"modules": ["victim"]}})
        cp = self.run_tool(manifest=False)
        self.assertEqual(cp.returncode, OK, cp.stdout + cp.stderr)


class P3_AZeroIsAReportableStateNeverAPass(Fixture):
    def test_an_UNDECLARED_empty_import_set_is_refused(self):
        self.write_records(record(modules=()))
        self.write_pins({"nd-unfolding/entry.py": {"modules": []}})
        cp = self.run_tool()
        self.assertRefused(cp, "is not a DECLARED empty entrypoint")

    def test_a_DECLARED_empty_import_set_passes_and_its_disclosure_is_PRINTED(self):
        self.write_records(record(modules=()))
        self.write_pins({"nd-unfolding/entry.py": {
            "modules": [], "declared_empty": True,
            "disclosure": "imports no repository code; its exit 0 is a structural fact"}})
        cp = self.run_tool()
        self.assertEqual(cp.returncode, OK, cp.stdout + cp.stderr)
        self.assertIn("DECLARED EMPTY: imports no repository code", cp.stdout)

    def test_a_record_MISSING_the_emptiness_flags_is_refused(self):
        r = record()
        del r["repo_origin_count"]
        del r["repo_origin_inventory_is_empty"]
        self.write_records(r)
        self.write_pins({"nd-unfolding/entry.py": {"modules": ["victim"]}})
        cp = self.run_tool()
        self.assertRefused(cp, "emptiness flags are ABSENT")

    def test_write_pins_REFUSES_a_declared_empty_without_its_disclosure(self):
        """A declared empty set with no disclosure sentence is the silent zero P-3 forbids."""
        self.write_records(record(modules=()))
        cp = self.run_tool("--write-pins", "--declare-empty", "nd-unfolding/entry.py")
        self.assertRefused(cp, "without --empty-disclosure", code=CANNOT_CHECK)


class P2_TheOriginsThemselves(Fixture):
    def test_an_origin_OUTSIDE_the_expected_root_is_refused(self):
        r = record()
        r["repo_origins"][0]["checkout_root"] = "/pscratch/elsewhere"
        self.write_records(r)
        self.write_pins({"nd-unfolding/entry.py": {"modules": ["victim"]}})
        cp = self.run_tool()
        self.assertRefused(cp, "not the expected")

    def test_a_sha256_that_disagrees_with_the_source_manifest_is_refused(self):
        r = record(modules=(("victim", "cc" * 32),))
        self.write_records(r)
        self.write_pins({"nd-unfolding/entry.py": {"modules": ["victim"]}})
        cp = self.run_tool()
        self.assertRefused(cp, "!= manifest")

    def test_an_origin_absent_from_the_source_manifest_is_refused(self):
        r = record(modules=(("ghost", "dd" * 32),))
        self.write_records(r)
        self.write_pins({"nd-unfolding/entry.py": {"modules": ["ghost"]}})
        cp = self.run_tool()
        self.assertRefused(cp, "not in the A-2(f) source manifest")

    def test_WITHOUT_a_source_manifest_the_sha256_half_is_OFF_and_says_so(self):
        """A check that silently degrades is worse than one that refuses. It must announce it."""
        self.write_records(record(modules=(("victim", "cc" * 32),)))
        self.write_pins({"nd-unfolding/entry.py": {"modules": ["victim"]}})
        cp = self.run_tool(manifest=False)
        self.assertEqual(cp.returncode, OK, cp.stdout + cp.stderr)
        self.assertIn("sha256 half of P-2 is OFF", cp.stdout)

    def test_checked_equal_zero_is_refused_even_when_the_import_set_matches(self):
        self.write_records(record(checked=0))
        self.write_pins({"nd-unfolding/entry.py": {"modules": ["victim"]}})
        cp = self.run_tool()
        self.assertRefused(cp, "the guard resolved no absolute origin at all")

    def test_a_DEFAULTED_zero_is_refused_where_a_MEASURED_zero_would_be_reportable(self):
        """Ruling 20 makes checked==0 the expected value on the containment path, which is exactly
        when a defaulted zero slips through. The provenance is what separates the two."""
        self.write_records(record(checked=0, guard_installed=False,
                                  checked_provenance="not-measured-no-guard-was-installed",
                                  modules=()))
        self.write_pins({"nd-unfolding/entry.py": {"modules": [], "declared_empty": True,
                                                   "disclosure": "d"}})
        cp = self.run_tool()
        self.assertRefused(cp, "the count was never measured")

    def test_a_record_with_NO_provenance_field_at_all_is_refused(self):
        r = record()
        del r["checked_provenance"]
        self.write_records(r)
        self.write_pins({"nd-unfolding/entry.py": {"modules": ["victim"]}})
        cp = self.run_tool()
        self.assertRefused(cp, "no `checked_provenance`")

    def test_a_record_carrying_a_REFUSAL_SITE_is_refused(self):
        self.write_records(record(refusal_site="b4-script-containment"))
        self.write_pins({"nd-unfolding/entry.py": {"modules": ["victim"]}})
        cp = self.run_tool()
        self.assertRefused(cp, "refusal_site is")

    def test_a_guard_that_was_never_installed_is_refused(self):
        self.write_records(record(guard_installed=False))
        self.write_pins({"nd-unfolding/entry.py": {"modules": ["victim"]}})
        cp = self.run_tool()
        self.assertRefused(cp, "no guard was installed")

    def test_a_script_outside_the_expected_root_is_refused(self):
        self.write_records(record(script_checkout_root="/pscratch/elsewhere"))
        self.write_pins({"nd-unfolding/entry.py": {"modules": ["victim"]}})
        cp = self.run_tool()
        self.assertRefused(cp, "the SCRIPT resolves under")

    def test_ANY_allow_in_a_production_record_is_refused(self):
        self.write_records(record(allow=[CLUSTER_ROOT]))
        self.write_pins({"nd-unfolding/entry.py": {"modules": ["victim"]}})
        cp = self.run_tool()
        self.assertRefused(cp, "--allow was used")


class ARefusalRecordMustNotSitInAProductionSet(Fixture):
    def test_a_B4_refusal_record_is_refused(self):
        self.write_records(record(outcome="refused:script-outside-expect-root",
                                  verdict="REFUSED -- THE SCRIPT ITSELF LIES IN A CHECKOUT",
                                  modules=(), checked=0))
        self.write_pins({"nd-unfolding/entry.py": {"modules": []}})
        cp = self.run_tool()
        self.assertRefused(cp, "is a REFUSAL or a CANNOT-LOOK")

    def test_a_cannot_look_record_is_refused(self):
        self.write_records(record(outcome="cannot-check:no-such-script",
                                  verdict="COULD NOT LOOK -- cannot-check:no-such-script",
                                  modules=(), checked=0))
        self.write_pins({"nd-unfolding/entry.py": {"modules": []}})
        cp = self.run_tool()
        self.assertRefused(cp, "is a REFUSAL or a CANNOT-LOOK")

    def test_outcome_AND_verdict_are_both_read_because_they_disagreed_once(self):
        """A B-4 refusal recorded itself as an empty GREEN verdict until 2026-08-22, found by
        running the real N-1 arm. Either field alone would have missed it then."""
        self.write_records(record(outcome="refused:script-outside-expect-root",
                                  verdict="EMPTY-REPOSITORY-ORIGIN-SET -- THE GUARD REFUSED NOTHING",
                                  modules=(), checked=0))
        self.write_pins({"nd-unfolding/entry.py": {"modules": []}})
        self.assertRefused(self.run_tool(), "is a REFUSAL or a CANNOT-LOOK")
        self.write_records(record(outcome="ok", verdict="REFUSED -- something",
                                  modules=(), checked=0))
        self.assertRefused(self.run_tool(), "is a REFUSAL or a CANNOT-LOOK")


class CannotLookIsNeverAPass(Fixture):
    def test_an_empty_inventory_directory_is_2_not_0(self):
        self.write_pins({})
        cp = self.run_tool()
        self.assertRefused(cp, "zero inventory records", code=CANNOT_CHECK)

    def test_a_missing_inventory_directory_is_2(self):
        self.write_pins({})
        cp = subprocess.run([sys.executable, str(TOOL), "--inventory-dir",
                             str(self.tmp / "nope"), "--pins", str(self.pins)],
                            capture_output=True, text=True)
        self.assertRefused(cp, "no inventory directory", code=CANNOT_CHECK)

    def test_a_MALFORMED_line_raises_rather_than_being_skipped(self):
        """Skipping is how a half-written inventory becomes indistinguishable from a quiet one."""
        (self.invdir / "run.jsonl").write_text(json.dumps(record()) + "\nnot json\n")
        self.write_pins({"nd-unfolding/entry.py": {"modules": ["victim"]}})
        cp = self.run_tool()
        self.assertRefused(cp, "is not JSON", code=CANNOT_CHECK)

    def test_a_FOREIGN_schema_record_is_refused_rather_than_parsed(self):
        self.write_records(record(schema="something/else"))
        self.write_pins({"nd-unfolding/entry.py": {"modules": ["victim"]}})
        cp = self.run_tool()
        self.assertRefused(cp, "is not a mnv_guard_inventory/1 record", code=CANNOT_CHECK)

    def test_foreign_pins_are_refused(self):
        self.write_records(record())
        self.pins.write_text(json.dumps({"schema": "other/1", "entrypoints": {}}))
        cp = self.run_tool()
        self.assertRefused(cp, "is not a mnv_import_set_pins/1 record", code=CANNOT_CHECK)


class EveryViolationIsReportedNotJustTheFirst(Fixture):
    def test_two_independent_defects_both_appear(self):
        """A reviewer who fixes the first refusal and re-runs should not find a second behind it."""
        r = record(checked=0, allow=["/elsewhere"])
        self.write_records(r)
        self.write_pins({"nd-unfolding/entry.py": {"modules": ["victim"]}})
        cp = self.run_tool()
        self.assertEqual(cp.returncode, VIOLATION, cp.stdout + cp.stderr)
        self.assertIn("--allow was used", cp.stderr)
        self.assertIn("the guard resolved no absolute origin at all", cp.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
