#!/usr/bin/env python3
"""Execute every tool the launcher invokes, with the launcher's REAL argument combinations.

WHY THIS FILE EXISTS. Three pilot attempts died in startup, each on a fault no test reached:
58347943 on an apostrophe that voided two `${VAR:?}` guards, and 58354056 on
`mnv_env_provenance.py --compare` -- a flag that tool does not have, carried over from
`mnv_source_manifest.py` four lines above, which does. `tests/test_z_pilot_launcher_init.py`
stops at the environment-closure boundary by design, so the six invocations AFTER it -- source
manifest, executing-copy parity, environment provenance, null transcription, manifest creation,
pilot invocation -- were exercised by nothing.

WHAT THIS DELIBERATELY DOES NOT DO, because each was tried and each failed to catch `--compare`:
  * it does not grep sources for `add_argument`. A first cut of that audit reported a FALSE
    POSITIVE on `--pair` in `verify_executing_copy_is_committed.py`, which has no `add_argument`
    line for it and demonstrably accepts it -- the parity call in the failed job printed
    "15 of 15 CURRENT". A grep for one argparse idiom misses every tool not using it.
  * it does not read `--help`. A tool can list a flag it rejects in combination, and `--help`
    exits before any argument validation.
  * it does not check flags one at a time. `--compare` alone might be tolerated; what failed was
    the real combination, and argparse's complaint was about a MISSING required verb, not about
    `--compare` itself.
So every case below RUNS the command the launcher runs and reads its exit status and streams.

THE THREE OUTCOMES ARE KEPT APART, because conflating them is what made 58354056 hard to read:
  MALFORMED INVOCATION  -- the command was wrong. argparse exit 2 with a usage block.
  CANNOT INSPECT        -- the tool ran and could not look. Never "we looked and it was clean".
  MEASURED MISMATCH     -- the tool looked and the world disagreed with the record.
A test that accepted "non-zero" for any of these would have passed on 58354056.

FIXTURES ARE EXPLICITLY SYNTHETIC AND ARE NOT SCIENTIFIC INPUTS. Where a real operand is too
large or not present off-cluster, a small file is written under a temp directory and named
`FIXTURE-*`. None is a cross-section, a covariance or a null operand, none is digest-bound to any
record, and no production check is relaxed to accommodate them: the tools refuse them on their
merits, and that refusal is what several cases assert.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ND = Path(__file__).resolve().parents[1]
REPO = ND.parent
LAUNCHER = ND / "sbatch_z_pilot_5d.sh"

SRCMAN = ND / "mnv_source_manifest.py"
PARITY = ND / "pet" / "verify_executing_copy_is_committed.py"
ENVPROV = ND / "mnv_env_provenance.py"
GUARD = ND / "mnv_guarded_run.py"
BRIDGE = ND / "z_null_bridge.py"
MANIFEST_CLI = ND / "z_pilot_manifest_cli.py"
PILOT = ND / "z_pilot.py"

ARGPARSE_USAGE_RC = 2


def run(argv, **kw):
    return subprocess.run([sys.executable, *[str(a) for a in argv]],
                          capture_output=True, text=True, **kw)


def launcher_line(var: str) -> str:
    """The launcher's OWN invocation line for `python3 "$VAR" ...`, continuations joined.

    Extracted from the launcher rather than restated, because a test that retypes the argument
    list tests the retyping. Measured: with the arguments hardcoded, reverting the launcher to
    `--compare` left this file green -- the exact defect it exists to catch.
    """
    lines = LAUNCHER.read_text().splitlines()
    for i, ln in enumerate(lines):
        if re.match(rf'^\s*python3 "\${var}"', ln):
            chunk, j = [ln], i
            while chunk[-1].rstrip().endswith("\\") and j + 1 < len(lines):
                j += 1
                chunk.append(lines[j])
            joined = " ".join(c.rstrip().rstrip("\\").strip() for c in chunk)
            # CUT AT THE `||` HANDLER. Several invocations end `... || { echo ...; exit 3; }`,
            # whose brace block spans further lines, so joining only backslash-continuations
            # leaves `{` unterminated and bash reports a syntax error -- which would read as a
            # malformed invocation when it was a malformed EXTRACTION. The invocation proper is
            # everything before the handler.
            return re.split(r"\s\|\|\s", joined)[0].strip()
    raise AssertionError(f"no `python3 \"${var}\"` invocation found in the launcher")


def run_launcher_line(var: str, subs: dict):
    """Execute the launcher's own line for `var`, with its shell variables bound to fixtures.

    Run through bash so the SHELL does the word splitting and quote removal, exactly as it does
    in the job. Any variable the line references and `subs` does not define is a test error, not
    an empty expansion -- `set -u` makes that loud instead of silently passing an empty argument.
    """
    line = launcher_line(var)
    import shlex
    # shlex.quote, NOT repr: Python's repr is not shell quoting, and a path containing a quote
    # would be mis-split. Not reachable with temp paths, but the idiom should not be wrong.
    assigns = "".join(f"{k}={shlex.quote(str(v))}\n" for k, v in subs.items())
    script = "set -u\n" + assigns + line
    return subprocess.run(["bash", "-c", script], capture_output=True, text=True), line


def launcher_guard_line(payload_basename: str) -> str:
    """The launcher's `python3 "$GUARD" ... -- ...<payload>` line, selected BY ITS PAYLOAD.

    `launcher_line("GUARD")` returns only the FIRST of three guard invocations, so a test using it
    silently exercised one composition and claimed three. The guard-wraps-payload composition is
    where the "two different 2s" hazard actually lives.
    """
    lines = LAUNCHER.read_text().splitlines()
    for i, ln in enumerate(lines):
        if 'python3 "$GUARD"' in ln:
            chunk, j = [ln], i
            while chunk[-1].rstrip().endswith("\\") and j + 1 < len(lines):
                j += 1
                chunk.append(lines[j])
            joined = " ".join(c.rstrip().rstrip("\\").strip() for c in chunk)
            if payload_basename in joined:
                return re.split(r"\s\|\|\s", joined)[0].strip()
    raise AssertionError(f"no guarded invocation of {payload_basename} in the launcher")


def launcher_block(start_marker: str, end_marker: str) -> str:
    """The launcher's own text between two markers, for EXECUTING a block rather than reading it."""
    text = LAUNCHER.read_text()
    i, j = text.index(start_marker), text.index(end_marker)
    return text[i:j]


def run_block(block: str, subs: dict, extra: str = ""):
    """Execute a launcher block with its shell variables bound. shlex-quoted, not repr."""
    import shlex
    assigns = "".join(f"{k}={shlex.quote(str(v))}\n" for k, v in subs.items())
    return subprocess.run(["bash", "-c", "set -u\n" + assigns + extra + block],
                          capture_output=True, text=True)


class TheLauncherFlagsAreTheToolsFlags(unittest.TestCase):
    """Run each tool with the launcher's real combination and require it to PARSE.

    Parsing is the property under test -- not success. Several of these then fail on their merits
    against synthetic inputs, which is correct and asserted separately below.
    """

    def _assert_not_usage_error(self, r, tool: str):
        blob = r.stdout + r.stderr
        self.assertNotIn(
            "error: unrecognized arguments", blob,
            f"{tool}: the launcher passes a flag this tool does not accept:\n{blob[-600:]}")
        self.assertNotIn(
            "error: one of the arguments", blob,
            f"{tool}: the launcher's combination omits a required verb -- this is the exact "
            f"58354056 failure:\n{blob[-600:]}")
        self.assertFalse(
            r.returncode == ARGPARSE_USAGE_RC and "usage:" in blob,
            f"{tool}: MALFORMED INVOCATION (argparse exit 2):\n{blob[-600:]}")

    def test_env_provenance_THE_LAUNCHERS_OWN_LINE_parses_and_runs(self):
        """58354056 died here, and this executes the launcher's line rather than a copy of it."""
        with tempfile.TemporaryDirectory() as td:
            base = Path(td) / "FIXTURE-envprov-baseline.json"
            r0 = run([ENVPROV, "--emit", base])
            self.assertEqual(r0.returncode, 0, r0.stderr[-400:])
            inv = Path(td) / "inv"; inv.mkdir()
            r, line = run_launcher_line("ENVPROV", {
                "ENVPROV": str(ENVPROV), "ENVPROV_RECORD": str(base), "INVDIR": str(inv),
                "SLURM_JOB_NAME": "fixture", "SLURM_JOB_ID": "0",
            })
            self._assert_not_usage_error(r, f"launcher line: {line}")
            self.assertEqual(r.returncode, 0,
                             f"the launcher's own line must run:\n{line}\n"
                             f"{(r.stdout + r.stderr)[-600:]}")
            self.assertTrue(any(inv.iterdir()), "--record wrote nothing")

    def test_the_flag_the_launcher_USED_TO_pass_is_still_rejected(self):
        """The regression control: `--compare` must remain a MALFORMED INVOCATION, not silently
        acquire a meaning. If this tool ever grows a `--compare`, this test tells us before a
        launcher quietly starts using it again."""
        with tempfile.TemporaryDirectory() as td:
            base = Path(td) / "FIXTURE-b.json"
            run([ENVPROV, "--emit", base])
            r = run([ENVPROV, "--compare", base, "--record", Path(td) / "FIXTURE-r.json"])
            blob = r.stdout + r.stderr
            self.assertEqual(r.returncode, ARGPARSE_USAGE_RC, blob[-400:])
            self.assertIn("usage:", blob)
            self.assertIn("one of the arguments", blob,
                          "the 58354056 diagnostic must still be what this produces")

    def test_source_manifest_THE_LAUNCHERS_OWN_LINE_parses_and_runs(self):
        """`--compare` IS correct here -- the same word, a different tool, four lines apart."""
        with tempfile.TemporaryDirectory() as td:
            rec = Path(td) / "FIXTURE-srcman.json"
            r0 = run([SRCMAN, "--repo", REPO, "--write", rec])
            self.assertEqual(r0.returncode, 0, r0.stderr[-400:])
            r, line = run_launcher_line("SRCMAN", {
                "SRCMAN": str(SRCMAN), "CODE_ROOT": str(REPO), "SRCMAN_RECORD": str(rec),
            })
            self._assert_not_usage_error(r, f"launcher line: {line}")
            blob = r.stdout + r.stderr
            # It may legitimately REFUSE here: the launcher's line carries --require-readonly and
            # --require-clean, which a normal writable checkout does not satisfy. That is a
            # MEASURED verdict, not a malformed invocation, and the distinction is the point.
            self.assertIn("[srcman]", blob, f"the tool did not run:\n{line}\n{blob[-500:]}")
            if r.returncode != 0:
                self.assertTrue(
                    any(k in blob for k in ("readonly", "not clean", "porcelain", "writable")),
                    f"a non-zero exit must name the measured reason:\n{blob[-600:]}")

    def test_parity_THE_LAUNCHERS_OWN_LINE_parses_and_runs(self):
        """`--pair` has no `add_argument`; only executing the real line establishes it works."""
        r, line = run_launcher_line("PARITY", {
            "PARITY": str(PARITY), "CODE_ROOT": str(REPO), "GUARD": str(GUARD),
            "SRCMAN": str(SRCMAN), "ENVPROV": str(ENVPROV),
        })
        self._assert_not_usage_error(r, f"launcher line: {line}")
        blob = r.stdout + r.stderr
        self.assertIn("CURRENT", blob,
                      f"the parity tool did not run its comparison:\n{line}\n{blob[-500:]}")

    def test_guard_with_the_launchers_combination_parses(self):
        with tempfile.TemporaryDirectory() as td:
            r = run([GUARD, "--expect-root", REPO, "--inventory", Path(td) / "FIXTURE-inv.jsonl",
                     "--", PILOT, "--help"])
            self._assert_not_usage_error(r, "mnv_guarded_run.py")
            self.assertEqual(r.returncode, 0, (r.stdout + r.stderr)[-500:])

    def test_bridge_with_the_launchers_combination_parses(self):
        """Parses and then REFUSES a synthetic product on its merits -- both are asserted."""
        with tempfile.TemporaryDirectory() as td:
            fake = Path(td) / "FIXTURE-not-a-root-product.root"
            fake.write_bytes(b"FIXTURE: not a ROOT file")
            r = run([BRIDGE, "--product", fake, "--sha256", "0" * 64,
                     "--out-null", Path(td) / "FIXTURE-null.npz",
                     "--record", Path(td) / "FIXTURE-bridge.json"])
            self._assert_not_usage_error(r, "z_null_bridge.py")
            self.assertEqual(r.returncode, 1, "a synthetic product must be REFUSED, not accepted")
            self.assertIn("bridge_status", r.stderr, "the refusal must carry its envelope")
            self.assertIn("digest mismatch", r.stderr,
                          "and it must refuse on the DIGEST, before reading any object")

    def test_manifest_cli_with_the_launchers_combination_parses(self):
        with tempfile.TemporaryDirectory() as td:
            args = [MANIFEST_CLI, "--out", Path(td) / "FIXTURE-manifest.json",
                    "--provenance", Path(td) / "FIXTURE-prov.json",
                    "--producing-revision", "0" * 40,
                    "--run-id", "fixture-run", "--run-step", "assembly",
                    "--input-kind", "real",
                    "--stat-key", "hCov_stat5d_reported", "--ml-key", "hCov_mlsplit5d_reported",
                    "--throw-sha256", "0" * 64]
            for role in ("parent", "central", "support", "active", "stat", "ml", "throw", "null"):
                f = Path(td) / f"FIXTURE-{role}.npz"
                f.write_bytes(b"FIXTURE")
                args += [f"--{role}", f]
            r = run(args)
            self._assert_not_usage_error(r, "z_pilot_manifest_cli.py")
            self.assertEqual(r.returncode, 1, "synthetic roles must be REFUSED")
            self.assertIn("manifest_status", r.stderr)

    def test_pilot_with_the_launchers_combination_parses(self):
        with tempfile.TemporaryDirectory() as td:
            r = run([PILOT, "--manifest", Path(td) / "FIXTURE-absent.json",
                     "--out-dir", Path(td) / "out",
                     "--receipt", Path(td) / "out" / "z-pilot-receipt.json"])
            self._assert_not_usage_error(r, "z_pilot.py")
            self.assertEqual(r.returncode, 1, "an absent manifest must be REFUSED")
            self.assertIn("pilot_status", r.stderr)


class TheThreeOutcomesStayApart(unittest.TestCase):
    """Malformed invocation, cannot-inspect, and measured mismatch must not collapse together."""

    def test_MALFORMED_is_argparse_exit_2_with_a_usage_block(self):
        r = run([ENVPROV, "--no-such-flag"])
        self.assertEqual(r.returncode, ARGPARSE_USAGE_RC)
        self.assertIn("usage:", r.stdout + r.stderr)

    def test_CANNOT_INSPECT_is_exit_2_and_says_it_is_not_a_clean_verdict(self):
        with tempfile.TemporaryDirectory() as td:
            r = run([GUARD, "--expect-root", td, "--inventory", Path(td) / "i.jsonl",
                     "--", PILOT, "--help"])
            self.assertEqual(r.returncode, 2, (r.stdout + r.stderr)[-400:])
            blob = r.stdout + r.stderr
            self.assertIn("COULD NOT LOOK", blob)
            self.assertNotIn("REFUSED --", blob.replace("COULD NOT LOOK", ""))

    def test_MEASURED_MISMATCH_is_distinguishable_from_both(self):
        """A real environment mismatch: a declared MNV_* variable dropped between record and check."""
        with tempfile.TemporaryDirectory() as td:
            base = Path(td) / "FIXTURE-base.json"
            env = dict(os.environ, MNV_FIXTURE_SENTINEL="present")
            r0 = subprocess.run([sys.executable, str(ENVPROV), "--emit", str(base)],
                                capture_output=True, text=True, env=env)
            self.assertEqual(r0.returncode, 0, r0.stderr[-300:])
            env2 = {k: v for k, v in env.items() if k != "MNV_FIXTURE_SENTINEL"}
            r = subprocess.run([sys.executable, str(ENVPROV), "--check-inherited", str(base),
                                "--record", str(Path(td) / "FIXTURE-rec.json")],
                               capture_output=True, text=True, env=env2)
            blob = r0.stdout + r.stdout + r.stderr
            # ASSERT the precondition rather than gating the assertions behind it. Gated, this
            # test passed green with ZERO assertions executed if the tool stopped recording the
            # fixture variable -- the fixture supplied the precondition it claimed to test.
            self.assertIn("MNV_FIXTURE_SENTINEL", Path(base).read_text(),
                          "the baseline must record the fixture variable, or this test is vacuous")
            if True:
                self.assertNotEqual(r.returncode, 0,
                                    "a dropped declared MNV_* var must be a measured mismatch")
                self.assertNotEqual(r.returncode, ARGPARSE_USAGE_RC,
                                    "a measured mismatch must NOT look like a malformed invocation")
                self.assertIn("MNV_FIXTURE_SENTINEL", blob,
                              "the mismatch must NAME the variable that moved")


class TheRehearsalStopPointIsSafe(unittest.TestCase):
    """EXECUTE the launcher's own rehearsal block.

    ⚠ THE FIRST VERSION OF THIS CLASS WAS SATISFIABLE BY COMMENTS. A reviewer commented out the
    entire executable block, leaving only the banners and the condition text, and all 15 tests
    stayed green -- and changing the rehearsal's exit code was likewise uncaught. That is the exact
    decoy this file's own docstring cites (a prose mention of `#SBATCH --no-requeue` satisfying a
    test for the directive), recommitted inside the commit that documents it. Everything below runs
    the launcher's real text.
    """

    START = "if [ \"${MNV_Z_PILOT_REHEARSE:-}\" = \"manifest\" ]; then"
    END = "# --- STEP 3: build both variants"

    def _run(self, rehearse, out_name, slab=True, manifest=True):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / out_name
            out.mkdir()
            ns = out / "z-null-source.npz"
            mf = out / "z-manifest.json"
            if slab:
                ns.write_bytes(b"FIXTURE-slab")
            if manifest:
                mf.write_text("{}")
            subs = {"PILOT_OUT": str(out), "NULL_SLAB": str(ns), "MANIFEST": str(mf)}
            if rehearse is not None:
                subs["MNV_Z_PILOT_REHEARSE"] = rehearse
            extra = "" if rehearse is not None else "unset MNV_Z_PILOT_REHEARSE || true\n"
            blk = launcher_block(self.START, self.END) + '\necho REACHED_STEP3\n'
            return run_block(blk, subs, extra)

    def test_the_rehearsal_STOPS_and_exits_12_not_0(self):
        r = self._run("manifest", "z_pilot_rehearsal_x")
        self.assertIn("REHEARSAL STOP", r.stdout, r.stdout + r.stderr)
        self.assertNotIn("REACHED_STEP3", r.stdout, "the rehearsal did not stop")
        self.assertEqual(r.returncode, 12,
                         "a rehearsal must exit non-zero and distinctly -- exit 0 would let "
                         "sacct record COMPLETED 0:0 for a run that built no covariance")
        self.assertIn("NOT a pilot", r.stdout)

    def test_a_STALE_variable_in_a_PILOT_namespace_REFUSES_rather_than_truncating(self):
        """`--export=ALL` carries the submitter's environment; this is the real hazard."""
        r = self._run("manifest", "z_pilot_20260915_a3")
        self.assertNotIn("REHEARSAL STOP", r.stdout)
        self.assertNotIn("REACHED_STEP3", r.stdout, "it must not silently continue either")
        self.assertEqual(r.returncode, 13, r.stdout + r.stderr)
        self.assertIn("not named for a rehearsal", r.stderr)

    def test_every_other_value_runs_in_FULL(self):
        for val in ("", "1", "true", "yes", "MANIFEST", "manifest-ish"):
            with self.subTest(value=val):
                r = self._run(val, "z_pilot_rehearsal_x")
                self.assertIn("REACHED_STEP3", r.stdout,
                              f"value {val!r} must NOT stop the run")
                self.assertNotIn("REHEARSAL STOP", r.stdout)

    def test_UNSET_runs_in_FULL(self):
        r = self._run(None, "z_pilot_rehearsal_x")
        self.assertIn("REACHED_STEP3", r.stdout, r.stdout + r.stderr)

    def test_the_rehearsal_REFUSES_if_its_own_artifacts_are_missing(self):
        r = self._run("manifest", "z_pilot_rehearsal_x", slab=False)
        self.assertEqual(r.returncode, 4, r.stdout + r.stderr)
        self.assertNotIn("REHEARSAL STOP", r.stdout,
                         "the refusal must precede the success banner, not follow it")
        r = self._run("manifest", "z_pilot_rehearsal_x", manifest=False)
        self.assertEqual(r.returncode, 5, r.stdout + r.stderr)

    def test_the_stop_sits_AFTER_the_manifest_and_BEFORE_assembly(self):
        text = LAUNCHER.read_text()
        self.assertLess(text.index("STEP 2: the digest-bound manifest"), text.index(self.START))
        self.assertLess(text.index(self.START), text.index("STEP 3: build both variants"))


class TheGuardWrappedInvocationsAreExecutedAsTheLauncherRunsThem(unittest.TestCase):
    """The launcher wraps bridge/manifest/pilot in `mnv_guarded_run.py --expect-root ... --`.

    Calling those tools bare -- as the first version of this file did -- leaves the guard-wraps-
    payload composition unexercised, and a reviewer proved it blind: breaking the launcher's
    `--out`, `--out-null` or `--receipt` flags left all 15 tests green.
    """

    def _subs(self, td):
        return {
            "GUARD": str(GUARD), "CODE_ROOT": str(REPO), "INVDIR": str(td),
            "PRODUCT": str(Path(td) / "FIXTURE-product.root"),
            "PRODUCT_SHA": "0" * 64,
            "NULL_SLAB": str(Path(td) / "FIXTURE-null.npz"),
            "PILOT_OUT": str(td), "MANIFEST": str(Path(td) / "FIXTURE-manifest.json"),
            "Z_RUN_ID": "fixture-run",
            "Z_PARENT": str(Path(td) / "FIXTURE-parent.npz"),
            "Z_CENTRAL": str(Path(td) / "FIXTURE-central.npz"),
            "Z_SUPPORT": str(Path(td) / "FIXTURE-support.npz"),
            "Z_ACTIVE": str(Path(td) / "FIXTURE-active.npz"),
            "Z_STAT": str(Path(td) / "FIXTURE-stat.npz"),
            "Z_ML": str(Path(td) / "FIXTURE-ml.npz"),
            "Z_STAT_KEY": "hCov_stat5d_reported", "Z_ML_KEY": "hCov_mlsplit5d_reported",
            "SLURM_JOB_NAME": "fixture", "SLURM_JOB_ID": "0", "SLURM_ARRAY_TASK_ID": "na",
        }

    def _run_guarded(self, payload):
        import shlex
        line = launcher_guard_line(payload)
        with tempfile.TemporaryDirectory() as td:
            for f in ("FIXTURE-product.root", "FIXTURE-parent.npz", "FIXTURE-central.npz",
                      "FIXTURE-support.npz", "FIXTURE-active.npz", "FIXTURE-stat.npz",
                      "FIXTURE-ml.npz"):
                (Path(td) / f).write_bytes(b"FIXTURE")
            subs = self._subs(td)
            assigns = "".join(f"{k}={shlex.quote(v)}\n" for k, v in subs.items())
            # the launcher defines mnv_inv(); the guarded lines call it
            fn = 'mnv_inv() { echo "$INVDIR/inv.$1.jsonl"; }\n'
            r = subprocess.run(["bash", "-c", "set -u\n" + assigns + fn + line],
                               capture_output=True, text=True)
            return r, line

    def _assert_payload_ran(self, r, line, envelope_key):
        """The payload must emit ITS OWN envelope.

        ⚠ THE FIRST VERSION ASSERTED THE ABSENCE OF ERROR STRINGS, and a reviewer's mutation
        (`--out-null` -> `--out-nulls`) satisfied it: absence-of-error is a weak negative that a
        broken invocation can meet. An envelope is positive proof the payload parsed its arguments
        and reached its own refusal logic, which is the property under test.
        """
        blob = r.stdout + r.stderr
        for bad in ("unbound variable", "syntax error"):
            self.assertNotIn(bad, blob, f"{bad} in:\n{line}\n{blob[-500:]}")
        self.assertIn(
            envelope_key, blob,
            f"the payload never emitted its {envelope_key!r} envelope, so it did not parse the "
            f"launcher's arguments:\n{line}\n{blob[-700:]}")
        self.assertNotIn("error: unrecognized arguments", blob, blob[-400:])
        self.assertNotIn("the following arguments are required", blob, blob[-400:])

    def test_the_guarded_BRIDGE_line_parses_and_the_payload_refuses_on_its_merits(self):
        r, line = self._run_guarded("z_null_bridge.py")
        self._assert_payload_ran(r, line, "bridge_status")
        self.assertNotEqual(r.returncode, 0, "a FIXTURE product must be refused")

    def test_the_guarded_MANIFEST_line_parses_and_the_payload_refuses_on_its_merits(self):
        r, line = self._run_guarded("z_pilot_manifest_cli.py")
        self._assert_payload_ran(r, line, "manifest_status")
        self.assertNotEqual(r.returncode, 0, "FIXTURE roles must be refused")

    def test_the_guarded_PILOT_line_parses_and_the_payload_refuses_on_its_merits(self):
        r, line = self._run_guarded("z_pilot.py")
        self._assert_payload_ran(r, line, "pilot_status")
        self.assertNotEqual(r.returncode, 0, "a FIXTURE manifest must be refused")


class TheEnvProvenanceOutcomesAreAttributedCorrectly(unittest.TestCase):
    """EXECUTE the launcher's env-provenance block against each outcome the tool can produce.

    ⚠ A REVIEWER BLOCKED THE FIRST VERSION OF THIS BLOCK FOR GETTING TWO OF THREE WRONG.
    `mnv_env_provenance.py:65` declares `EXIT_OK, EXIT_CANNOT_LOOK, EXIT_DRIFT = 0, 2, 3`. The
    first version mapped rc=2 to MALFORMED INVOCATION -- but 2 is ALSO the tool's CANNOT-LOOK,
    returned when the baseline is absent or unreadable, which is the single most likely real fault
    here because the baseline is emitted on a login node and read from a compute node. And its
    catch-all announced "This IS a measured mismatch" for any other code, asserting a comparison
    that never ran. argparse's 2 and the tool's 2 are the SAME INTEGER; only what was printed
    separates them, so the block now reads stderr instead of guessing.
    """

    START = "set +e\n_envprov_err=$(mktemp)"
    END = "# --- STEP 1: transcribe"

    def _run(self, record_path, envprov=None):
        with tempfile.TemporaryDirectory() as td:
            inv = Path(td) / "inv"; inv.mkdir()
            blk = launcher_block(self.START, self.END)
            return run_block(blk, {
                "ENVPROV": str(envprov or ENVPROV),
                "ENVPROV_RECORD": str(record_path),
                "INVDIR": str(inv),
                "SLURM_JOB_NAME": "fixture", "SLURM_JOB_ID": "0",
            })

    def test_SUCCESS_continues(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td) / "FIXTURE-base.json"
            self.assertEqual(run([ENVPROV, "--emit", base]).returncode, 0)
            r = self._run(base)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_CANNOT_LOOK_is_exit_10_and_is_NOT_called_malformed(self):
        """The most likely real fault: an absent baseline. The flags are correct."""
        with tempfile.TemporaryDirectory() as td:
            r = self._run(Path(td) / "ABSENT-BASELINE.json")
            self.assertEqual(r.returncode, 10,
                             f"an absent baseline must be COULD-NOT-LOOK (10), not malformed (9) "
                             f"nor a measured mismatch (3):\n{r.stderr[-700:]}")
            self.assertIn("COULD NOT LOOK", r.stderr)
            self.assertIn("NOT a measured mismatch", r.stderr)
            self.assertNotIn("MALFORMED INVOCATION", r.stderr,
                             "correct flags must never be reported as a malformed invocation")

    def test_MALFORMED_is_exit_9_and_says_it_is_not_an_environment_problem(self):
        """A stub that emits an argparse usage block on stderr and exits 2."""
        with tempfile.TemporaryDirectory() as td:
            stub = Path(td) / "FIXTURE-usage-stub.py"
            stub.write_text(
                "import sys\n"
                "sys.stderr.write('usage: FIXTURE-usage-stub.py [-h]\\n"
                "FIXTURE: error: one of the arguments --emit --check is required\\n')\n"
                "sys.exit(2)\n")
            r = self._run(Path(td) / "b.json", envprov=stub)
            self.assertEqual(r.returncode, 9, r.stderr[-600:])
            self.assertIn("MALFORMED INVOCATION", r.stderr)
            self.assertIn("NOT an environment mismatch", r.stderr)

    def test_DRIFT_is_exit_3_and_IS_called_a_measured_mismatch(self):
        with tempfile.TemporaryDirectory() as td:
            stub = Path(td) / "FIXTURE-drift-stub.py"
            stub.write_text(
                "import sys\n"
                "sys.stderr.write('[env-provenance] DRIFT: 1 difference(s)\\n')\n"
                "sys.exit(3)\n")
            r = self._run(Path(td) / "b.json", envprov=stub)
            self.assertEqual(r.returncode, 3, r.stderr[-600:])
            self.assertIn("MEASURED ENVIRONMENT MISMATCH", r.stderr)

    def test_A_CRASH_is_exit_11_and_claims_NOTHING_about_the_environment(self):
        """The tool's contract is 0/2/3. Anything else means it did not complete."""
        with tempfile.TemporaryDirectory() as td:
            stub = Path(td) / "FIXTURE-crash-stub.py"
            stub.write_text("raise SystemExit(1)\n")
            r = self._run(Path(td) / "b.json", envprov=stub)
            self.assertEqual(r.returncode, 11, r.stderr[-600:])
            self.assertIn("DID NOT COMPLETE", r.stderr)
            self.assertIn("No claim is made about the environment", r.stderr)
            self.assertNotIn("IS a measured mismatch", r.stderr,
                             "a crash must not be reported as a measurement")

    def test_an_INDETERMINATE_two_is_reported_as_indeterminate(self):
        """rc=2 with neither marker: reported as unknown rather than assigned to a branch."""
        with tempfile.TemporaryDirectory() as td:
            stub = Path(td) / "FIXTURE-silent2-stub.py"
            stub.write_text("raise SystemExit(2)\n")
            r = self._run(Path(td) / "b.json", envprov=stub)
            self.assertEqual(r.returncode, 11, r.stderr[-600:])
            self.assertIn("INDETERMINATE", r.stderr)


class EveryLauncherInvocationIsCovered(unittest.TestCase):
    """Closed-set: if the launcher gains a python3 invocation, this file must grow with it."""

    def test_the_covered_set_is_EXACTLY_the_launchers_python_invocations(self):
        text = LAUNCHER.read_text()
        by_var = set(re.findall(r'python3 "\$(\w+)"', text))
        # INVOCATION POSITIONS ONLY. Matching every mention of a filename let a reviewer add a
        # REAL `python3 "${CODE_ROOT}/nd-unfolding/z_build.py" --unreviewed-flag` and pass, because
        # subtracting the `--pair` operands removed z_build.py globally -- its parity-operand
        # status masked a genuine new invocation. Two forms count as an invocation: directly after
        # `python3`, and after the guard's `--` separator.
        by_path = set(re.findall(
            r'python3 "?\$\{?CODE_ROOT\}?/nd-unfolding/([A-Za-z0-9_./]+\.py)', text))
        # The guard's separator and its payload are on DIFFERENT LINES:
        #     python3 "$GUARD" ... -- \
        #       "${CODE_ROOT}/nd-unfolding/z_null_bridge.py" \
        # so the pattern must cross a backslash continuation. Without that it matched nothing and
        # `by_path` was empty -- caught by the length control below, which is why that control is
        # there rather than being an ornament.
        by_path |= set(re.findall(
            r'--\s*\\?\s*"?\$\{?CODE_ROOT\}?/nd-unfolding/([A-Za-z0-9_./]+\.py)', text))
        # NEGATIVE CONTROL first: if the scan sees nothing, "nothing missing" is vacuous.
        self.assertGreaterEqual(len(by_var), 4, f"scan found only {sorted(by_var)}")
        self.assertGreaterEqual(len(by_path), 3, f"scan found only {sorted(by_path)}")
        covered_vars = {"SRCMAN", "PARITY", "ENVPROV", "GUARD"}
        # ⚠ SPLIT INVOKED FROM MERELY NAMED. The first version lumped them, so the seven modules
        # that appear ONLY as `--pair` digest-parity operands sat in the "covered" set and a real
        # new invocation of `z_build.py` with an unreviewed flag passed 15/15. Parity operands are
        # not invocations and must not buy coverage.
        parity_operands = set(re.findall(
            r'--pair "\$\{?CODE_ROOT\}?/nd-unfolding/([A-Za-z0-9_./]+\.py)=', text))
        self.assertGreaterEqual(len(parity_operands), 7,
                                f"the parity scan found only {sorted(parity_operands)}")
        # NO SUBTRACTION: `by_path` now holds only invocation positions, so a module that is both
        # a parity operand AND invoked still appears -- which is the case the subtraction hid.
        covered_paths = {
            "z_null_bridge.py", "z_pilot_manifest_cli.py", "z_pilot.py",
            "mnv_guarded_run.py", "mnv_source_manifest.py", "mnv_env_provenance.py",
            "pet/verify_executing_copy_is_committed.py",
        }
        self.assertEqual(by_var - covered_vars, set(),
                         f"launcher invokes unexecuted tool var(s): {sorted(by_var - covered_vars)}")
        self.assertEqual(by_path - covered_paths, set(),
                         f"launcher names unexecuted path(s): {sorted(by_path - covered_paths)}")


if __name__ == "__main__":
    unittest.main()
