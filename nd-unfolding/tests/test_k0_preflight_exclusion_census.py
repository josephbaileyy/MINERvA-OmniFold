#!/usr/bin/env python3
"""F-7(a): the preflight exclusion is now PINNED, and this proves the pin can fail.

Gate 1 refused a PASS on F-7(a) because sixteen preflight `python3` calls were excluded from the
import guard IMPLICITLY -- nothing named them, and nothing failed if a seventeenth appeared. The
suite's only `python3` regex SELECTS guarded calls, so `python3 whatever.py` matched nothing.

THE ARM THAT MATTERS MOST HERE IS THE SILENT ONE. A detector that fires on everything is not a
detector, and `a filter needs a test in the direction it acts`: the guard-widening check gets an arm
that it FIRES on a fifteenth unguarded call, and an arm that it is SILENT on the current thirty.
The mutations are applied to a COPY of the launchers, never to the tree under review.

WHAT THESE ARMS DO NOT COVER, stated so the Gate-1 record does not over-read them: this is a
byte-level census. It cannot see a guard defeated at runtime, and it says nothing about python
invoked as anything but the literal token `python3`. Those belong to the dynamic arms of
`test_k0_launcher_two_roots.py` and to `test_mnv_guarded_run.TheSubprocessBoundaryIsCovered`.
"""
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
ND = HERE.parent
CENSUS = ND / "mnv_preflight_census.py"
DECL = ND / "mnv_preflight_exclusions.json"

sys.path.insert(0, str(ND))
import mnv_preflight_census as mpc  # noqa: E402
import mnv_guarded_run  # noqa: E402

OK, CANNOT_LOOK, VIOLATION = 0, 2, 3


class ThePreflightExclusionIsPinnedAndCanFail(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.decl = json.loads(DECL.read_text())

    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="mnv-preflight-census-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.nd = self.tmp / "nd-unfolding"
        self.nd.mkdir(parents=True)
        for sh in self.decl["launchers"]:
            shutil.copy2(ND / sh, self.nd / sh)

    def run_census(self, decl=None):
        """Always via subprocess, so the EXIT CODE is measured and not inferred from a return."""
        dpath = self.tmp / "decl.json"
        dpath.write_text(json.dumps(decl if decl is not None else self.decl))
        p = subprocess.run([sys.executable, str(CENSUS), "--declaration", str(dpath),
                            "--nd-dir", str(self.nd)],
                           capture_output=True, text=True)
        return p

    def mutate(self, sh, old, new, count=1):
        p = self.nd / sh
        text = p.read_text()
        self.assertEqual(text.count(old), count,
                         f"fixture precondition: {old!r} appears {text.count(old)} times in {sh}, "
                         f"expected {count}. A mutation that did not apply is a FALSE GREEN.")
        p.write_text(text.replace(old, new))

    # ---- ARM 2: SILENT ON GOOD -------------------------------------------------------------
    def test_ARM_silent_on_the_current_tree(self):
        """The arm the other two are worthless without."""
        p = self.run_census()
        self.assertEqual(p.returncode, OK, f"stdout={p.stdout}\nstderr={p.stderr}")
        self.assertIn("14 guarded + 24 declared-preflight + 16 interpreter-probe + 0 unclassified",
                      p.stdout)

    def test_ARM_silent_on_the_REAL_tree_too_not_only_the_copy(self):
        """The copy could differ from the tree under review; assert against the real one as well."""
        p = subprocess.run([sys.executable, str(CENSUS)], capture_output=True, text=True)
        self.assertEqual(p.returncode, OK, f"stdout={p.stdout}\nstderr={p.stderr}")

    # ---- ARM 1: a FIFTEENTH unguarded call -------------------------------------------------
    def test_ARM_fires_on_an_added_unguarded_invocation(self):
        sh = self.decl["launchers"][0]
        p = self.nd / sh
        p.write_text(p.read_text() + '\npython3 "${CODE_ROOT}/nd-unfolding/whatever.py" --go\n')
        r = self.run_census()
        self.assertEqual(r.returncode, VIOLATION, f"stdout={r.stdout}\nstderr={r.stderr}")
        self.assertIn("UNCLASSIFIED python3 invocation", r.stderr)

    def test_ARM_fires_on_an_added_unguarded_invocation_in_EVERY_launcher(self):
        """One launcher passing is not eight. The gap was found in a set, so the arm covers the set."""
        for sh in self.decl["launchers"]:
            with self.subTest(launcher=sh):
                self.setUp()
                p = self.nd / sh
                p.write_text(p.read_text() + '\npython3 "${CODE_ROOT}/nd-unfolding/x.py"\n')
                r = self.run_census()
                self.assertEqual(r.returncode, VIOLATION, f"{sh}: {r.stdout}{r.stderr}")

    # ---- ARM 3: REMOVING a guard -----------------------------------------------------------
    def test_ARM_fires_on_removing_a_guard(self):
        """Strip the guard from a guarded call: it becomes an unclassified science invocation."""
        sh = "sbatch_bootstrap_5d_gpu.sh"
        self.mutate(sh, 'python3 "$GUARD" --expect-root "$CODE_ROOT" --inventory',
                    'python3 --inventory')
        r = self.run_census()
        self.assertEqual(r.returncode, VIOLATION, f"stdout={r.stdout}\nstderr={r.stderr}")
        self.assertIn("UNCLASSIFIED", r.stderr)
        self.assertIn("PIN guarded: measured 13, pinned 14", r.stderr)

    def test_ARM_fires_on_COMMENTING_OUT_a_guarded_call(self):
        """The sneaky removal: the line is still visible, and a naive census still counts it.

        This is why the declaration pins the commented-out count as well as the live one."""
        sh = "sbatch_bootstrap_5d_gpu.sh"
        p = self.nd / sh
        lines = p.read_text().splitlines()
        hit = [i for i, l in enumerate(lines)
               if mpc.GUARDED_RE.search(l) and not l.lstrip().startswith("#")]
        self.assertEqual(len(hit), 1, "fixture precondition: one guarded call in this launcher")
        lines[hit[0]] = "#" + lines[hit[0]]
        p.write_text("\n".join(lines) + "\n")
        r = self.run_census()
        self.assertEqual(r.returncode, VIOLATION, f"stdout={r.stdout}\nstderr={r.stderr}")
        self.assertIn("PIN guarded: measured 13, pinned 14", r.stderr)
        self.assertIn("PIN commented_out_python3_lines: measured 19, pinned 18", r.stderr)

    # ---- the declaration must point at something ------------------------------------------
    def test_ARM_fires_on_REPOINTING_a_declared_preflight_variable(self):
        """A declared exclusion is only as good as what its name resolves to."""
        sh = "sbatch_bootstrap_5d_gpu.sh"
        self.mutate(sh, 'SRCMAN="${CODE_ROOT}/nd-unfolding/mnv_source_manifest.py"',
                    'SRCMAN="${CODE_ROOT}/nd-unfolding/something_else.py"')
        r = self.run_census()
        self.assertEqual(r.returncode, VIOLATION, f"stdout={r.stdout}\nstderr={r.stderr}")
        self.assertIn("does not resolve to", r.stderr)

    def test_ARM_fires_on_a_SHRUNK_set_not_only_a_grown_one(self):
        """Identity, not a floor. Deleting a preflight call must fail exactly as adding one does."""
        sh = "sbatch_bootstrap_5d_gpu.sh"
        p = self.nd / sh
        lines = [l for l in p.read_text().splitlines()
                 if not (l.lstrip().startswith('python3 "$PARITY"'))]
        p.write_text("\n".join(lines) + "\n")
        r = self.run_census()
        self.assertEqual(r.returncode, VIOLATION, f"stdout={r.stdout}\nstderr={r.stderr}")
        self.assertIn("expected 1 $PARITY invocation(s), found 0", r.stderr)

    def test_ARM_fires_when_a_declared_launcher_is_ABSENT(self):
        """A missing launcher must be a failure, not a gap -- `ls | wc -l` gives 0 for both."""
        (self.nd / self.decl["launchers"][0]).unlink()
        r = self.run_census()
        self.assertEqual(r.returncode, VIOLATION, f"stdout={r.stdout}\nstderr={r.stderr}")
        self.assertIn("declared launcher is ABSENT", r.stderr)

    # ---- the instrument must be able to say I COULD NOT LOOK -------------------------------
    def test_a_missing_declaration_is_CANNOT_LOOK_not_a_pass(self):
        p = subprocess.run([sys.executable, str(CENSUS), "--declaration",
                            str(self.tmp / "nope.json"), "--nd-dir", str(self.nd)],
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, CANNOT_LOOK, p.stderr)

    def test_a_wrong_schema_is_CANNOT_LOOK_not_a_pass(self):
        bad = dict(self.decl, schema="something/9")
        r = self.run_census(bad)
        self.assertEqual(r.returncode, CANNOT_LOOK, r.stderr)

    # ---- the declaration's own numbers are DERIVED, not authored ---------------------------
    def test_the_pinned_counts_are_reproduced_from_the_launcher_bytes(self):
        """The three PINS. Everything else the census reports is derived, not authored."""
        violations, totals = mpc.census(self.decl, self.nd)
        self.assertEqual(violations, [])
        pins = self.decl["pinned_counts"]
        self.assertEqual(totals["guarded"], pins["guarded"])
        self.assertEqual(totals["unknown"], pins["unclassified"])
        self.assertEqual(totals["commented"], pins["commented_out_python3_lines"])

    def test_the_derived_totals_are_NOT_authored_anywhere_in_the_declaration(self):
        """OI-185: the four authored totals are GONE, not bumped.

        This is the arm that stops them coming back. A later lane re-adding
        `excluded_preflight: 24` would give the file two sources of truth that drift
        silently -- which is the state OI-185 removed.
        """
        blob = json.dumps(self.decl)
        for gone in ("excluded_preflight", "non_comment_python3_invocations",
                     "inline_interpreter_probes"):
            self.assertNotIn(f'"{gone}":', blob,
                             f"{gone} is authored again. OI-185 replaced it with a derived value.")
        self.assertNotIn("counts", self.decl,
                         "the v1 `counts` block is back; pinned_counts is the v2 shape")
        self.assertEqual(sorted(self.decl["pinned_counts"]),
                         ["commented_out_python3_lines", "guarded", "unclassified"],
                         "exactly three pins survive OI-185; a fourth needs a ruling")

    def test_ruling_21s_guarding_boundary_is_asserted_by_a_TEST(self):
        """F-7(a)'s finding was that no test asserted these numbers. This is that test.

        THE BOUNDARY MOVED 2026-09-01 from 14/30 to 14/38, and Joseph RATIFIED it at the new value
        under OI-185. Authority: `docs/orchestration/DECISION-20260901-joseph-ratifies-oi185-
        invariants.md`, which quotes his words and reproduces verbatim the recommendation they
        accept. `OI-179` defect-3 enforcement added one preflight tool invocation per launcher
        (`mnv_env_provenance.py`), so the declared exclusion set went 16 -> 24. **The GUARDED count
        is untouched at 14: no science invocation changed, which is the thing ruling 21 was
        actually about.**

        WHAT THIS ARM ASSERTS, AND WHAT IT DELIBERATELY NO LONGER DOES. It asserts guarded == 14,
        because that is a human decision and moving it needs another one. It asserts the boundary
        is 38 TODAY, as a recorded observation of the ratified state. It does NOT require the
        declaration to carry 38 anywhere: the boundary is DERIVED, and the next principled
        preflight tool moves it without a ruling. That is the OI-185 change, and
        test_a_PRINCIPLED_fourth_preflight_tool_needs_NO_ruling is what makes it falsifiable.
        """
        _, totals = mpc.census(self.decl, self.nd)
        self.assertEqual(totals["guarded"], 14, "the GUARDED count must not move without a ruling")
        self.assertEqual(totals["unknown"], 0)
        self.assertEqual(totals["guarded"] + totals["excluded"], 38,
                         "the ratified boundary, DERIVED -- not read out of the declaration")

    # ---- OI-185 criterion (4): excluded from the guard is NOT excluded from binding --------
    def test_ARM_fires_when_a_declared_preflight_tool_is_NOT_pair_bound(self):
        """True of all three tools before OI-185 and asserted by nobody -- exactly F-7(a)."""
        sh = "sbatch_bootstrap_5d_gpu.sh"
        self.mutate(sh, '--pair "${ENVPROV}=nd-unfolding/mnv_env_provenance.py"',
                    '--pair "${GUARD}=nd-unfolding/mnv_guarded_run.py"')
        r = self.run_census()
        self.assertEqual(r.returncode, VIOLATION, f"stdout={r.stdout}\nstderr={r.stderr}")
        self.assertIn("is NOT --pair bound", r.stderr)

    def test_ARM_the_pair_check_covers_EVERY_tool_in_EVERY_launcher(self):
        """One launcher passing is not eight, and one tool is not three."""
        for sh in self.decl["launchers"]:
            for tool in self.decl["excluded_tools"]:
                with self.subTest(launcher=sh, tool=tool["shell_var"]):
                    self.setUp()
                    pair = '--pair "${%s}=%s"' % (tool["shell_var"], tool["resolves_to"])
                    q = self.nd / sh
                    text = q.read_text()
                    self.assertIn(pair, text,
                                  "fixture precondition: the binding must be there to remove")
                    q.write_text(text.replace(pair, '--pair "${GUARD}=nd-unfolding/x.py"'))
                    r = self.run_census()
                    self.assertEqual(r.returncode, VIOLATION,
                                     f"{sh}/{tool['shell_var']}: {r.stderr}")
                    self.assertIn("is NOT --pair bound", r.stderr)

    # ---- OI-185 criterion (1): an entry must actually declare something --------------------
    def test_ARM_fires_on_a_STRUCTURALLY_INCOMPLETE_exclusion_entry(self):
        """An exclusion with no `resolves_to` is a hole with a name."""
        for key in ("resolves_to", "role", "shell_var"):
            with self.subTest(missing=key):
                bad = json.loads(json.dumps(self.decl))
                bad["excluded_tools"][2].pop(key)
                r = self.run_census(bad)
                self.assertEqual(r.returncode, VIOLATION, r.stderr)
                self.assertIn("is missing or empty", r.stderr)

    # ---- OI-185: a v1 declaration is REFUSED, not read under v2 semantics ------------------
    def test_a_v1_declaration_is_CANNOT_LOOK_not_a_silent_downgrade(self):
        """Reading a v1 file under v2 rules would drop four checks and still print OK."""
        v1 = json.loads(json.dumps(self.decl))
        v1["schema"] = "mnv_preflight_exclusions/1"
        v1["counts"] = {"launchers": 8, "guarded": 14, "excluded_preflight": 24,
                        "unclassified": 0, "inline_interpreter_probes": 16,
                        "non_comment_python3_invocations": 54}
        r = self.run_census(v1)
        self.assertEqual(r.returncode, CANNOT_LOOK, f"stdout={r.stdout}\nstderr={r.stderr}")

    # ---- OI-185's PROMISE, asserted in BOTH directions -------------------------------------
    def test_a_PRINCIPLED_fourth_preflight_tool_needs_NO_ruling(self):
        """The positive half of what Joseph ratified, made falsifiable.

        Under the old authored totals this exact change failed on three separate counts
        (excluded_preflight 24->32, non_comment_python3_invocations 54->62, and the boundary),
        and each would have cost a ruling. Under the invariants it passes -- because nothing a
        human decided actually moved.
        """
        decl = json.loads(json.dumps(self.decl))
        decl["excluded_tools"].append({
            "shell_var": "NEWTOOL", "per_launcher": 1,
            "resolves_to": "nd-unfolding/mnv_preflight_census.py",
            "role": "a principled preflight tool added without a ruling, per OI-185"})
        for sh in decl["launchers"]:
            q = self.nd / sh
            q.write_text(q.read_text()
                         + '\nNEWTOOL="${CODE_ROOT}/nd-unfolding/mnv_preflight_census.py"\n'
                         + 'python3 "$NEWTOOL" --declaration x\n'
                         + '  --pair "${NEWTOOL}=nd-unfolding/mnv_preflight_census.py"\n')
        r = self.run_census(decl)
        self.assertEqual(r.returncode, OK, f"stdout={r.stdout}\nstderr={r.stderr}")
        self.assertIn("14 guarded", r.stdout)
        self.assertIn("boundary (guarded + declared-preflight) = 46", r.stdout)

    def test_an_UNDECLARED_fourth_preflight_tool_STILL_FAILS(self):
        """The other half. Invariants are not a waiver: undeclared is still a violation.

        Identical launcher bytes to the arm above, with the declaration entry withheld."""
        decl = json.loads(json.dumps(self.decl))
        for sh in decl["launchers"]:
            q = self.nd / sh
            q.write_text(q.read_text()
                         + '\nNEWTOOL="${CODE_ROOT}/nd-unfolding/mnv_preflight_census.py"\n'
                         + 'python3 "$NEWTOOL" --declaration x\n')
        r = self.run_census(decl)
        self.assertEqual(r.returncode, VIOLATION, f"stdout={r.stdout}\nstderr={r.stderr}")
        self.assertIn("UNCLASSIFIED python3 invocation", r.stderr)

    def test_ARM_fires_when_the_derived_total_disagrees_with_the_structure(self):
        """The one hole the per-tool counts leave: a line naming TWO declared tool variables.

        Classified ONCE as `excluded`, counted once for each of the two tools, so both per-tool
        checks pass. Only the derived-consistency check sees it.
        """
        sh = "sbatch_bootstrap_5d_gpu.sh"
        q = self.nd / sh
        # BOTH real calls are removed and replaced by ONE line naming both variables. Removing only
        # one would leave the surviving tool at count 2 and the PER-TOOL check would refuse the
        # mutation before the derived check ever ran -- the mutation-refused-before-it-lands trap.
        # This way each per-tool count is still exactly 1 and only the derived total disagrees.
        lines = [l for l in q.read_text().splitlines()
                 if not (l.lstrip().startswith('python3 "$PARITY"')
                         or l.lstrip().startswith('python3 "$SRCMAN"'))]
        lines.append('python3 "$PARITY" --repo x --and-also "$SRCMAN"')
        q.write_text("\n".join(lines) + "\n")
        r = self.run_census()
        self.assertEqual(r.returncode, VIOLATION, f"stdout={r.stdout}\nstderr={r.stderr}")
        self.assertIn("DERIVED excluded_preflight", r.stderr)
        # and the per-tool checks must be SILENT, or this arm is not testing what it claims
        self.assertNotIn("invocation(s), found", r.stderr,
                         "the per-tool check fired, so the derived check was not the thing tested")


class TheExclusionCriterionIsMeasuredNotAsserted(unittest.TestCase):
    """OI-185 criterion (5): an excluded tool's repository imports must be a SUBSET of {the guard}.

    WHY THIS IS A SEPARATE CLASS AND NOT A CENSUS CHECK. The census is a byte-level instrument and
    says so in its docstring; this criterion requires EXECUTING each tool under `mnv_guarded_run.py`
    and reading the resolved-origin inventory it writes. Keeping it here leaves both instruments
    honest about what they measure.

    THE CRITERION WAS CORRECTED BY MEASUREMENT, WHICH IS WORTH STATING BECAUSE IT SUPERFICIALLY
    RESEMBLES RELAXING A RULE TO MAKE A TEST PASS. The departure was disclosed to Joseph before it was
    blessed, and he ruled on it 2026-09-01: "I don't think I meant it literally". So the criterion
    below is ratified, not merely shipped. OI-185 as filed gave the ground as `imports only
    the standard library`. Measured: mnv_env_provenance.py and verify_executing_copy_is_committed.py
    have repo_origin_count 0, but mnv_source_manifest.py has 1 -- it imports `MARKERS, is_checkout`
    from mnv_guarded_run itself (mnv_source_manifest.py:61). A stdlib-only rule would therefore have
    FIRED ON AN ENTRY RULING 21 ALREADY ACCEPTED, i.e. on every correct tree, which is the
    over-broad-guard failure. The scope was fixed by restating the question rather than loosening
    it: the ground the declaration always gave is CIRCULARITY -- routing these through the guard
    makes the check depend on the thing it is checking -- and `no repository import except the guard
    itself` is that ground made falsifiable.

    WHAT IT CANNOT SAY: it observes imports reached by `--help`, i.e. module-level imports. A
    repository import performed lazily inside a function body is outside its reach.
    """

    GUARD = ND / "mnv_guarded_run.py"

    @classmethod
    def setUpClass(cls):
        cls.decl = json.loads(DECL.read_text())
        cls.repo = ND.parent

    def origins(self, repo_root, guard, script, args=("--help",)):
        """Run `script` under the guard and return the set of repository module names it loaded."""
        tmp = pathlib.Path(tempfile.mkdtemp(prefix="mnv-crit5-"))
        self.addCleanup(shutil.rmtree, tmp, True)
        inv = tmp / "inv.jsonl"
        r = subprocess.run([sys.executable, str(guard), "--expect-root", str(repo_root),
                            "--inventory", str(inv), "--label", "oi185-criterion-5",
                            "--", str(script), *args],
                           capture_output=True, text=True)
        self.assertTrue(inv.is_file() and inv.read_text().strip(),
                        f"NO INVENTORY WRITTEN for {script}: that is COULD-NOT-LOOK, never a pass. "
                        f"rc={r.returncode} stderr={r.stderr[-800:]}")
        rec = json.loads(inv.read_text().strip().splitlines()[-1])
        return {o["fullname"] for o in rec.get("repo_origins", [])}, rec

    # ---- the real measurement, on the declared tools ---------------------------------------
    def test_every_declared_exclusion_imports_no_repository_module_but_the_guard(self):
        for tool in self.decl["excluded_tools"]:
            with self.subTest(tool=tool["shell_var"]):
                names, rec = self.origins(self.repo, self.GUARD, self.repo / tool["resolves_to"])
                extra = names - {"mnv_guarded_run"}
                self.assertEqual(
                    extra, set(),
                    f"{tool['resolves_to']} imports repository module(s) {sorted(extra)}. The guard "
                    f"would have something to contain, so this may not be a declared preflight "
                    f"exclusion -- route it through mnv_guarded_run.py or justify it to the owner "
                    f"of ruling 21. checked={rec.get('checked')}")

    def test_the_inventory_is_NON_VACUOUS_so_an_empty_set_is_not_a_free_pass(self):
        """An empty origin set must mean `looked and saw none`, not `imported nothing at all`.

        Without this, criterion (5) would be satisfied by a tool the guard never actually
        instrumented -- the tally-over-a-failed-fetch shape.
        """
        for tool in self.decl["excluded_tools"]:
            with self.subTest(tool=tool["shell_var"]):
                _, rec = self.origins(self.repo, self.GUARD, self.repo / tool["resolves_to"])
                self.assertTrue(rec.get("guard_installed"), "the guard did not install")
                self.assertGreater(rec.get("checked", 0), 0,
                                   "zero modules inspected means the guard never looked")

    # ---- POWER: the criterion must FIRE on a tool that imports a repository module ---------
    def _synthetic_checkout(self):
        """A real, self-consistent checkout in TMPDIR -- never the shared tree under review.

        The guard recognises a checkout by MARKERS, and refuses a script outside --expect-root, so
        the guard itself is copied in and run FROM the synthetic tree. That keeps every origin
        inside the expected root and isolates what the arm is actually testing.
        """
        tmp = pathlib.Path(tempfile.mkdtemp(prefix="mnv-crit5-power-"))
        self.addCleanup(shutil.rmtree, tmp, True)
        root = tmp / "checkout"
        nd = root / "nd-unfolding"
        nd.mkdir(parents=True)
        for m in mpc_markers():
            tgt = root / m
            if not tgt.exists():
                tgt.write_text("synthetic marker for the criterion-5 power arm\n")
        shutil.copy2(self.GUARD, nd / "mnv_guarded_run.py")
        (nd / "helper_mod.py").write_text("VALUE = 1\n")
        (nd / "clean_tool.py").write_text(
            "import argparse, json, sys\n"
            "argparse.ArgumentParser().parse_args()\n")
        (nd / "dirty_tool.py").write_text(
            "import argparse\n"
            "import helper_mod  # a REPOSITORY import that is not the guard\n"
            "argparse.ArgumentParser().parse_args()\n"
            "assert helper_mod.VALUE == 1\n")
        return root, nd

    def test_POWER_the_criterion_FIRES_on_a_tool_importing_a_repository_module(self):
        root, nd = self._synthetic_checkout()
        names, rec = self.origins(root, nd / "mnv_guarded_run.py", nd / "dirty_tool.py")
        self.assertIn("helper_mod", names,
                      f"the power arm did not reproduce the condition it exists to detect; "
                      f"repo_origins={sorted(names)} checked={rec.get('checked')}")
        self.assertNotEqual(names - {"mnv_guarded_run"}, set(),
                            "criterion (5) must REJECT this tool")

    def test_POWER_the_criterion_is_SILENT_on_a_stdlib_only_tool_in_the_same_fixture(self):
        """The arm the one above is worthless without: same fixture, opposite verdict."""
        root, nd = self._synthetic_checkout()
        names, rec = self.origins(root, nd / "mnv_guarded_run.py", nd / "clean_tool.py")
        self.assertEqual(names - {"mnv_guarded_run"}, set(),
                         f"fired on a clean tool: repo_origins={sorted(names)}")
        self.assertGreater(rec.get("checked", 0), 0, "and it must still have LOOKED")


def mpc_markers():
    """The guard's own checkout markers, read from the guard -- never retyped here.

    A fixture that hardcodes ("VALIDATION_LEDGER.md", "nd-unfolding") would silently stop building
    a recognisable checkout the day the guard's markers change, and the power arm would go quiet.
    """
    return [m for m in mnv_guarded_run.MARKERS if not m.endswith("nd-unfolding")] + ["nd-unfolding"]


if __name__ == "__main__":
    unittest.main()
