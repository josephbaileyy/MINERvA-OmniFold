#!/usr/bin/env python3
"""Execute the REAL launcher's initialization and assert every operand binds.

WHY THIS FILE EXISTS. Job 58347943 died in 4 s with `mkdir: cannot create directory ''`. On bash
4.4.23 an apostrophe inside `${VAR:?word}` within double quotes opens a single-quote context that
SPANS NEWLINES, so `PRODUCT_SHA`'s message swallowed the `PILOT_OUT` line whole and closed on
`Z_RUN_ID`'s message. Both assignments were consumed: their `:?` guards never evaluated, the
variables were unset rather than refused, and the first symptom appeared 47 lines downstream.

WHY THE OLD TEST MISSED IT, which is the transferable part. `test_every_pilot_operand_is_mandatory_with_no_default`
asserted that `${VAR:?` APPEARS IN THE TEXT for all eleven names. It passed while two of the
eleven guards were inert, because presence in source is not evaluation at runtime. An independent
reviewer had already flagged that exact class twice in this same file -- `--no-requeue` satisfied
by its own prose comment, the freshness guard asserted by its message -- and this one survived the
repair. So everything here RUNS the launcher and reads a trace or an exit code.

⚠ VERSION-GATED, AND THAT IS THE POINT. Under bash 3.2 the defect does not manifest at all: the
original launcher PASSES the positive control there. A test that ran on 3.2 and reported green
would be worse than no test. These skip unless a bash >= 4.4 is present, and
`test_the_interpreter_is_recorded` makes the version part of the evidence rather than an
assumption. The authoritative run is on Perlmutter (bash 4.4.23).
"""

from __future__ import annotations

import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

ND = Path(__file__).resolve().parents[1]
LAUNCHER = ND / "sbatch_z_pilot_5d.sh"

#: The eleven operands the launcher declares with no default, and a distinctive probe value each.
#: Values are deliberately unlike one another so a trace line cannot match the wrong assignment.
OPERANDS = {
    "MNV_Z_PRECURSOR_PRODUCT": ("PRODUCT", "/probe/precursor-product.root"),
    "MNV_Z_PRECURSOR_SHA256": ("PRODUCT_SHA", "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"),
    "MNV_Z_PILOT_OUT": ("PILOT_OUT", None),          # filled with a temp dir per test
    "MNV_Z_PILOT_RUN_ID": ("Z_RUN_ID", "probe-run-id-7788"),
    "MNV_Z_CENTRAL": ("Z_CENTRAL", "/probe/central.root"),
    "MNV_Z_SUPPORT": ("Z_SUPPORT", "/probe/support.root"),
    "MNV_Z_ACTIVE": ("Z_ACTIVE", "/probe/active.root"),
    "MNV_Z_STAT": ("Z_STAT", "/probe/stat.root"),
    "MNV_Z_ML": ("Z_ML", "/probe/ml.root"),
    "MNV_Z_PARENT": ("Z_PARENT", "/probe/parent.root"),
    "MNV_Z_STAT_KEY": ("Z_STAT_KEY", "hProbeStatKey"),
    "MNV_Z_ML_KEY": ("Z_ML_KEY", "hProbeMlKey"),
}
#: The launcher's other mandatory variables, supplied so initialization reaches the operand block.
FRAME = {
    "MNV_CODE_ROOT": str(ND.parent),
    "MNV_DATA_ROOT": "/probe/data-root",
    "MNV_ENV_ROOT": "/probe/env-root",
    "MNV_CONDA_PREFIX": "/probe/conda",
    "MNV_GUARD_INVENTORY_DIR": "/probe/inv",
    "MNV_SOURCE_MANIFEST": "/probe/srcman.json",
    "MNV_ENV_PROVENANCE": "/probe/envprov.json",
}

#: The boundary initialization must REACH once every operand is bound: the environment closure.
#: Named by the line the launcher actually executes, not by a line number.
NEXT_BOUNDARY = "lib_mnv_env_preflight.sh"


def _find_bash():
    """A bash >= 4.4, or None. 3.2 cannot express the defect, so it is not a valid host."""
    for cand in ("/bin/bash", "/usr/local/bin/bash", "/opt/homebrew/bin/bash",
                 shutil.which("bash") or ""):
        if not cand or not os.access(cand, os.X_OK):
            continue
        try:
            out = subprocess.run([cand, "--version"], capture_output=True, text=True).stdout
        except OSError:
            continue
        m = re.search(r"version (\d+)\.(\d+)", out)
        if m and (int(m.group(1)), int(m.group(2))) >= (4, 4):
            return cand, f"{m.group(1)}.{m.group(2)}"
    return None, None


BASH, BASH_VER = _find_bash()


def _run(launcher: Path, env_overrides: dict, out_dir: str):
    """Run the REAL launcher under `bash -x` and return (rc, stdout, stderr)."""
    env = dict(os.environ)
    for k in list(env):
        if k.startswith("MNV_"):
            env.pop(k)
    env.update(FRAME)
    for name, (_var, val) in OPERANDS.items():
        env[name] = out_dir if name == "MNV_Z_PILOT_OUT" else val
    env.update(env_overrides)
    for k, v in list(env_overrides.items()):
        if v is None:
            env.pop(k, None)
    p = subprocess.run([BASH, "-x", str(launcher)], capture_output=True, text=True, env=env,
                       cwd=str(ND))
    return p.returncode, p.stdout, p.stderr


def _assigned(trace: str, var: str):
    """The value bash actually assigned to `var`, from the xtrace, or None if it never ran."""
    m = re.search(rf"^\+ {re.escape(var)}=(.*)$", trace, re.M)
    return None if m is None else m.group(1)


@unittest.skipUnless(BASH, "needs bash >= 4.4; bash 3.2 cannot express this defect")
class RealLauncherInitialization(unittest.TestCase):

    def test_the_interpreter_is_recorded(self):
        """The version is evidence, not an assumption -- a green run on 3.2 would be misleading."""
        self.assertIsNotNone(BASH_VER)
        major, minor = (int(x) for x in BASH_VER.split("."))
        self.assertGreaterEqual((major, minor), (4, 4), f"ran under bash {BASH_VER}")

    def test_ALL_ELEVEN_operands_bind_EXACTLY_and_initialization_reaches_the_next_boundary(self):
        with tempfile.TemporaryDirectory() as td:
            out = str(Path(td) / "fresh-out")
            rc, so, se = _run(LAUNCHER, {}, out)
            trace = so + se
            for name, (var, val) in OPERANDS.items():
                expected = out if name == "MNV_Z_PILOT_OUT" else val
                got = _assigned(trace, var)
                self.assertIsNotNone(
                    got, f"{var} was never assigned -- its line did not execute (this is the "
                         f"58347943 failure mode). Trace tail:\n{trace[-1500:]}")
                self.assertEqual(got, expected, f"{var} bound {got!r}, expected {expected!r}")
            # The two the apostrophe swallowed, asserted by name so a regression is unmissable.
            self.assertEqual(_assigned(trace, "PILOT_OUT"), out)
            self.assertEqual(_assigned(trace, "Z_RUN_ID"), "probe-run-id-7788")
            # The output directory is created, and initialization reaches the env closure.
            self.assertTrue(Path(out).is_dir(), "the fresh output directory was not created")
            self.assertIn(NEXT_BOUNDARY, trace,
                          "initialization did not reach the environment closure boundary")
            # It then fails there, because FRAME points at probe paths -- that is expected, and
            # asserted so this test cannot be read as a successful pilot run.
            self.assertNotEqual(rc, 0, "the probe frame must not produce a successful run")

    def test_each_operand_unset_REFUSES_attributably_and_creates_no_output(self):
        for name, (var, _v) in OPERANDS.items():
            with self.subTest(operand=name):
                with tempfile.TemporaryDirectory() as td:
                    out = str(Path(td) / "must-not-exist")
                    rc, so, se = _run(LAUNCHER, {name: None}, out)
                    blob = so + se
                    self.assertNotEqual(rc, 0, f"unsetting {name} must refuse")
                    self.assertIn(name, blob,
                                  f"the refusal must NAME {name} so it is attributable; got:\n"
                                  f"{blob[-800:]}")
                    if name != "MNV_Z_PILOT_OUT":
                        self.assertIsNone(
                            _assigned(blob, var),
                            f"{var} must not bind when {name} is unset")
                    self.assertFalse(
                        Path(out).exists(),
                        f"unsetting {name} created output before refusing -- the refusal must "
                        f"precede output creation")
                    self.assertNotIn(NEXT_BOUNDARY, blob,
                                     f"unsetting {name} still reached the environment closure")


@unittest.skipUnless(BASH, "needs bash >= 4.4; bash 3.2 cannot express this defect")
class TheOriginalLauncherFailsThePositiveControl(unittest.TestCase):
    """The discriminating control: reconstruct the pre-repair messages and show they break it.

    Without this pair the positive control above proves only that the launcher works today, not
    that it was broken yesterday for the reason claimed.
    """

    def _with_apostrophes(self, td):
        src = LAUNCHER.read_text()
        a = "to that product authorized sha256."
        b = "to this pilot run identifier, recorded in the manifest."
        self.assertEqual(src.count(a), 1, "repaired message A not found; retarget this control")
        self.assertEqual(src.count(b), 1, "repaired message B not found; retarget this control")
        broken = src.replace(a, "to that product's authorized sha256.", 1) \
                    .replace(b, "to this pilot run's identifier, recorded in the manifest.", 1)
        p = Path(td) / "sbatch_z_pilot_5d_ORIGINAL.sh"
        p.write_text(broken)
        p.chmod(0o755)
        return p

    def test_the_ORIGINAL_swallows_two_assignments_and_the_REPAIRED_does_not(self):
        with tempfile.TemporaryDirectory() as td:
            original = self._with_apostrophes(td)
            out_bad = str(Path(td) / "bad-out")
            rc_b, so_b, se_b = _run(original, {}, out_bad)
            trace_b = so_b + se_b
            # THE DEFECT: both lines vanish, with no error of their own.
            self.assertIsNone(_assigned(trace_b, "PILOT_OUT"),
                              "the original must NOT assign PILOT_OUT")
            self.assertIsNone(_assigned(trace_b, "Z_RUN_ID"),
                              "the original must NOT assign Z_RUN_ID")
            self.assertIn("mkdir -p ''", trace_b.replace('"', "'"),
                          "the original must reach mkdir with an empty operand")
            self.assertFalse(Path(out_bad).exists())

            out_good = str(Path(td) / "good-out")
            rc_g, so_g, se_g = _run(LAUNCHER, {}, out_good)
            trace_g = so_g + se_g
            self.assertEqual(_assigned(trace_g, "PILOT_OUT"), out_good)
            self.assertEqual(_assigned(trace_g, "Z_RUN_ID"), "probe-run-id-7788")
            self.assertTrue(Path(out_good).is_dir())

    def test_the_two_launchers_differ_ONLY_in_those_two_messages(self):
        """Fixture control: otherwise the paired verdicts would not isolate the apostrophes."""
        with tempfile.TemporaryDirectory() as td:
            original = self._with_apostrophes(td)
            a, b = LAUNCHER.read_text(), original.read_text()
            self.assertNotEqual(a, b)
            self.assertEqual(
                b.replace("to that product's authorized sha256.",
                          "to that product authorized sha256.", 1)
                 .replace("to this pilot run's identifier, recorded in the manifest.",
                          "to this pilot run identifier, recorded in the manifest.", 1),
                a, "the two launchers differ somewhere other than the two messages")


class NoApostropheSurvivesInAnyGuardMessage(unittest.TestCase):
    """A cheap ratchet that runs everywhere, INCLUDING bash 3.2 where the defect is invisible.

    Deliberately a source check, and deliberately not the only one: the executed controls above
    are the evidence, this is the tripwire that still fires on a host that cannot run them.
    """

    def test_no_guard_message_contains_an_apostrophe(self):
        offenders = [
            (i, ln) for i, ln in enumerate(LAUNCHER.read_text().splitlines(), 1)
            if re.search(r":\?[^}]*'", ln)
        ]
        self.assertEqual(
            offenders, [],
            "an apostrophe inside a ${VAR:?...} message spans newlines on bash >= 4.4 and "
            f"silently consumes the following line(s): {offenders}")


if __name__ == "__main__":
    unittest.main()
