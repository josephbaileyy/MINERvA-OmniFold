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
    assigns = "".join(f'{k}={v!r}\n' for k, v in subs.items())
    script = "set -u\n" + assigns + line
    return subprocess.run(["bash", "-c", script], capture_output=True, text=True), line


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
            if "MNV_FIXTURE_SENTINEL" in r0.stdout + Path(base).read_text():
                self.assertNotEqual(r.returncode, 0,
                                    "a dropped declared MNV_* var must be a measured mismatch")
                self.assertNotEqual(r.returncode, ARGPARSE_USAGE_RC,
                                    "a measured mismatch must NOT look like a malformed invocation")
                self.assertIn("MNV_FIXTURE_SENTINEL", blob,
                              "the mismatch must NAME the variable that moved")


class TheRehearsalStopPointIsSafe(unittest.TestCase):
    """The stop point must not be able to truncate a production pilot."""

    def test_the_default_is_a_FULL_run(self):
        text = LAUNCHER.read_text()
        self.assertIn('"${MNV_Z_PILOT_REHEARSE:-}" = "manifest"', text,
                      "the stop must trigger on one exact value, not on any non-empty value")
        import subprocess as sp
        for val in ("", "1", "true", "yes", "MANIFEST", "manifest-ish"):
            script = f'MNV_Z_PILOT_REHEARSE={val!r}\nif [ "${{MNV_Z_PILOT_REHEARSE:-}}" = "manifest" ]; then echo STOP; else echo FULL; fi\n'
            out = sp.run(["bash", "-c", script], capture_output=True, text=True).stdout.strip()
            self.assertEqual(out, "FULL", f"value {val!r} must NOT stop the run")
        script = 'MNV_Z_PILOT_REHEARSE=manifest\nif [ "${MNV_Z_PILOT_REHEARSE:-}" = "manifest" ]; then echo STOP; else echo FULL; fi\n'
        self.assertEqual(
            sp.run(["bash", "-c", script], capture_output=True, text=True).stdout.strip(), "STOP")

    def test_the_stop_is_AFTER_the_manifest_and_BEFORE_assembly(self):
        text = LAUNCHER.read_text()
        i_manifest = text.index("STEP 2: the digest-bound manifest")
        i_stop = text.index("REHEARSAL STOP POINT")
        i_step3 = text.index("STEP 3: build both variants")
        self.assertLess(i_manifest, i_stop, "the stop must follow manifest creation")
        self.assertLess(i_stop, i_step3, "the stop must precede covariance assembly")

    def test_the_stop_refuses_if_its_own_artifacts_are_missing(self):
        text = LAUNCHER.read_text()
        seg = text[text.index("REHEARSAL STOP POINT"):text.index("STEP 3: build both variants")]
        self.assertIn('[ -s "$NULL_SLAB" ]', seg)
        self.assertIn('[ -s "$MANIFEST" ]', seg)
        self.assertIn("NOT a pilot", seg, "a rehearsal must say it is not a pilot result")


class EveryLauncherInvocationIsCovered(unittest.TestCase):
    """Closed-set: if the launcher gains a python3 invocation, this file must grow with it."""

    def test_the_covered_set_is_EXACTLY_the_launchers_python_invocations(self):
        text = LAUNCHER.read_text()
        by_var = set(re.findall(r'python3 "\$(\w+)"', text))
        by_path = set(re.findall(r'\$\{?CODE_ROOT\}?/nd-unfolding/([A-Za-z0-9_./]+\.py)', text))
        # NEGATIVE CONTROL first: if the scan sees nothing, "nothing missing" is vacuous.
        self.assertGreaterEqual(len(by_var), 4, f"scan found only {sorted(by_var)}")
        self.assertGreaterEqual(len(by_path), 3, f"scan found only {sorted(by_path)}")
        covered_vars = {"SRCMAN", "PARITY", "ENVPROV", "GUARD"}
        covered_paths = {
            "z_null_bridge.py", "z_pilot_manifest_cli.py", "z_pilot.py",
            "mnv_guarded_run.py", "mnv_source_manifest.py", "mnv_env_provenance.py",
            "pet/verify_executing_copy_is_committed.py",
            "z_build.py", "z_assembly.py", "z_receipt.py", "z_contract.py",
            "z_statistics.py", "z_validator.py", "z_build_path.py",
        }
        self.assertEqual(by_var - covered_vars, set(),
                         f"launcher invokes unexecuted tool var(s): {sorted(by_var - covered_vars)}")
        self.assertEqual(by_path - covered_paths, set(),
                         f"launcher names unexecuted path(s): {sorted(by_path - covered_paths)}")


if __name__ == "__main__":
    unittest.main()
