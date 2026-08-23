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
`test_k0_launcher_two_roots.py` and to `test_mnv_guarded_run.TheSubprocessBoundaryIsNotCovered`.
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
        self.assertIn("14 guarded + 16 declared-preflight + 0 unclassified", p.stdout)

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
        self.assertIn("COUNT guarded: measured 13, declared 14", r.stderr)

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
        self.assertIn("COUNT guarded: measured 13, declared 14", r.stderr)
        self.assertIn("COUNT commented_out_python3_lines: measured 18, declared 17", r.stderr)

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
    def test_the_declared_counts_are_reproduced_from_the_launcher_bytes(self):
        violations, totals = mpc.census(self.decl, self.nd)
        self.assertEqual(violations, [])
        c = self.decl["counts"]
        self.assertEqual(totals["guarded"], c["guarded"])
        self.assertEqual(totals["excluded"], c["excluded_preflight"])
        self.assertEqual(totals["unknown"], 0)
        self.assertEqual(totals["guarded"] + totals["excluded"],
                         c["non_comment_python3_invocations"])

    def test_ruling_21s_14_of_30_boundary_is_asserted_by_a_TEST_for_the_first_time(self):
        """F-7(a)'s finding was that no test asserted 14, 30 or 16. This is that test."""
        _, totals = mpc.census(self.decl, self.nd)
        self.assertEqual(totals["guarded"], 14)
        self.assertEqual(totals["excluded"], 16)
        self.assertEqual(totals["guarded"] + totals["excluded"] + totals["unknown"], 30)


if __name__ == "__main__":
    unittest.main()
