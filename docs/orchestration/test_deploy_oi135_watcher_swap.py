#!/usr/bin/env python3
"""Rehearsal harness for `deploy_oi135_watcher_swap.sh` -- exercised WITHOUT a cluster.

WHY THIS EXISTS AND WHAT IT CAN HONESTLY CLAIM
----------------------------------------------
The deployment itself cannot run: `maintenance_20260819` started 2026-08-19T13:00Z and
`ssh` exits 255. What CAN be established today is that the script's decisions are right --
its refusals fire, its one all-or-nothing checkout cannot be split, and its add-then-retire
ordering cannot invert. So the transport is injected: `OI135_SSH` points at a fake `ssh`
that logs every remote command string and answers from an ordered scenario table.

The claim this harness makes is therefore precise: **the script's control flow is tested;
the cluster's behaviour is not.** The fake `ssh` is a stand-in for Slurm and git, and every
scenario line below is a HYPOTHESIS about what the login node would say. Two classes of
test escape that limitation, and they are the ones worth the most:

  * the script's three EMBEDDED python probes (`readback.py`, `argvchk.py`, `profchk.py`)
    are extracted from the shell source and run FOR REAL against fixtures -- including the
    repository's own `profiles.json` and `waker-config.json`, which is a fixture built from
    the PRODUCER rather than from my reading of the rule; and
  * `argvchk.py` is run against a REAL symlink pointing out of a REAL temp tree, which is
    the `.resolve()` case wakerctl.py:340-346 turns on.

A GUARD GETS A TEST THAT IT FIRES
---------------------------------
Every fail-closed branch below is asserted to REFUSE, and -- the half that actually matters
-- asserted to refuse WITHOUT having reached the mutation: a refusal that still armed a
watch is not a refusal. The `assert_no_mutation` helper reads the command log for
`fetch`/`checkout`/`watch-add`/`watch-disarm`/`prune`, so "it exited 2" is never the whole
assertion.

MUTATION RUN
------------
`python3 test_deploy_oi135_watcher_swap.py --mutate` applies six single-edit mutants to a
COPY of the script and requires the suite to fail on each. An unkilled mutant means the
corresponding test is decorative.
"""

import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
SCRIPT = HERE / "deploy_oi135_watcher_swap.sh"

CREPO = "/crepo"
PROG = CREPO + "/docs/orchestration/watch_report_train_run.py"
WATCHES = CREPO + "/docs/orchestration/state/waker/watches"

# The script under test is chosen by env var so the mutation runner can point the whole
# suite at a mutated copy without editing anything.
SCRIPT_UNDER_TEST = Path(os.environ.get("OI135_SCRIPT", str(SCRIPT)))

SCONTROL_HAPPY = (
    "JobId=57266000 ArrayJobId=57266000 ArrayTaskId=0 JobName=g5dotrain "
    "UserId=josephrb(12345) Priority=68110 QOS=shared_gp JobState=PENDING "
    "Reason=ReqNodeNotAvail,_Reserved_for_maintenance TimeLimit=02:00:00 "
    "NumNodes=1 NumCPUs=32 CPUs/Task=32 MinMemoryCPU=3G "
    "TresPerTask=gres/gpu:1 Partition=shared_gp"
)


def default_scenario():
    """Ordered, first-match-wins. Specific patterns FIRST -- the readback commands also
    contain the program path, so they must be matched before the argv[0] check."""
    return [
        {"match": "codex-waker", "rc": 0, "out":
            "waker-config root.profile='codex-waker'\n"
            "profiles.json defines=['codex-personal', 'codex-school', 'codex-waker']\n"
            "profile 'codex-waker' model='gpt-5.6-luna' reasoning_effort='low' yolo=True\n"
            "profile-pair-ok"},
        {"match": "array-active-57266000.json", "rc": 0, "out":
            "field cpus_per_task: 'NOT MEASURED' -> '32'\n"
            "field qos: 'NOT MEASURED' -> 'shared_gp'\n"
            "changed=5\nmeasured_at_utc=2026-08-26T14:00:00Z\n"
            "measured_by_command=scontrol show job 57266000\nreceipt-write-ok"},
        {"match": "-r4.json", "rc": 0, "out":
            "watch_id='gate5-do-train-57266000-r4'\nstate='armed'\nkind='slurm-array'\n"
            "params.job_id='57266000'\nparams.tasks='0-0'\naction.type='command'\n"
            "readback-ok"},
        # r3 is a root-resume watch, so everything except its state mismatches BY DESIGN.
        {"match": "-r3.json", "rc": 4, "out":
            "watch_id='gate5-do-train-57266000-r3'\nstate='disarmed'\n"
            "MISMATCH: action.type 'root-resume' != 'command'"},
        {"match": "watch_report_train_run.py " + CREPO, "rc": 0, "out":
            "argv0=" + PROG + "\nresolved=" + PROG + "\nis_absolute=True\n"
            "repo_in_resolved_parents=True\nis_symlink=False\n"
            "shebang='#!/usr/bin/python3.11'\nargv0-ok"},
        {"match": "stat -c %a", "rc": 0, "out": "755"},
        {"match": "watch-list", "rc": 0, "out":
            "gate5-do-train-57266000-r3\tslurm-array\tarmed"},
        {"match": "watch-add", "rc": 0, "out": "armed gate5-do-train-57266000-r4"},
        {"match": "watch-disarm", "rc": 0, "out": "disarmed gate5-do-train-57266000-r3"},
        {"match": "rev-parse --git-dir", "rc": 0, "out": ".git"},
        {"match": "remote get-url github", "rc": 0,
         "out": "https://github.com/josephrb/MINERvA-OmniFold.git"},
        {"match": "cat-file -e", "rc": 0, "out": ""},
        {"match": "fetch github", "rc": 0, "out": ""},
        {"match": "diff --exit-code", "rc": 0, "out": ""},
        {"match": "scontrol show job", "rc": 0, "out": SCONTROL_HAPPY},
        {"match": "sacct", "rc": 0, "out": "57266000_0 PENDING"},
        {"match": "worktree list", "rc": 0, "out": CREPO + "  abc1234 [main]"},
        {"match": "generate_live_state.py", "rc": 0, "out": "wrote LIVE-STATE.md"},
        {"match": "test -f", "rc": 0, "out": ""},
        {"match": "test -e", "rc": 0, "out": ""},
        {"match": "test -d", "rc": 1, "out": ""},
        {"match": "true", "rc": 0, "out": ""},
    ]


def override(scenario, match, **kw):
    """Replace the first entry whose `match` equals `match`, or prepend a new one."""
    out = [dict(entry) for entry in scenario]
    for entry in out:
        if entry["match"] == match:
            entry.update(kw)
            return out
    entry = {"match": match, "rc": 0, "out": ""}
    entry.update(kw)
    return [entry] + out


FAKE_SSH = textwrap.dedent(
    """\
    #!%s
    import json, os, sys
    log = os.environ["OI135_TEST_LOG"]
    scenario = json.load(open(os.environ["OI135_TEST_SCENARIO"]))
    cmd = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
    with open(log, "a") as fh:
        fh.write(cmd + "\\n")
    for entry in scenario:
        if entry["match"] in cmd:
            if entry.get("out"):
                sys.stdout.write(entry["out"] + "\\n")
            sys.exit(int(entry["rc"]))
    sys.exit(0)
    """
) % sys.executable


class Harness(unittest.TestCase):
    """Runs the script with an injected transport and exposes the command log."""

    maxDiff = None

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="oi135-test-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.ssh = self.tmp / "fake-ssh"
        self.ssh.write_text(FAKE_SSH)
        self.ssh.chmod(0o755)
        self.log = self.tmp / "cmd.log"
        self.log.write_text("")
        self.scen = self.tmp / "scenario.json"

    def run_script(self, scenario=None, args=("--execute",)):
        self.scen.write_text(json.dumps(scenario if scenario is not None else default_scenario()))
        env = dict(os.environ)
        env.update({
            "OI135_SSH": str(self.ssh),
            "OI135_LOGIN": "fake-login",
            "OI135_CREPO": CREPO,
            "OI135_REMOTE_PY": "/usr/bin/python3.11",
            "OI135_TEST_LOG": str(self.log),
            "OI135_TEST_SCENARIO": str(self.scen),
            "TMPDIR": str(self.tmp),
        })
        proc = subprocess.run(
            ["bash", str(SCRIPT_UNDER_TEST)] + list(args),
            env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        self.cmds = [line for line in self.log.read_text().splitlines() if line]
        return proc

    # -- helpers ------------------------------------------------------------------
    def commands_matching(self, needle):
        return [c for c in self.cmds if needle in c]

    def assert_no_mutation(self, *, allow=()):
        """A refusal that still mutated is not a refusal."""
        for needle in ("fetch github", "checkout github/main", "watch-add",
                       "watch-disarm", "worktree prune", "generate_live_state.py"):
            if needle in allow:
                continue
            self.assertEqual(
                [], self.commands_matching(needle),
                "MUTATED after a refusal: %r ran. log=%s" % (needle, self.cmds))

    def assert_refused(self, proc):
        self.assertEqual(2, proc.returncode,
                         "expected REFUSE (rc=2); got rc=%s\nstdout=%s\nstderr=%s"
                         % (proc.returncode, proc.stdout, proc.stderr))
        self.assertIn("REFUSE", proc.stderr)


class TestFailClosedPreflight(Harness):
    """Each guard is asserted to FIRE, and to fire before any mutation."""

    def test_cluster_unreachable_refuses_and_attempts_nothing(self):
        proc = self.run_script(override(default_scenario(), "true", rc=255))
        self.assert_refused(proc)
        self.assertIn("cluster unreachable", proc.stderr)
        self.assert_no_mutation()

    def test_missing_git_checkout_refuses(self):
        proc = self.run_script(override(default_scenario(), "rev-parse --git-dir", rc=128))
        self.assert_refused(proc)
        self.assertIn("no git checkout", proc.stderr)
        self.assert_no_mutation()

    def test_missing_github_remote_refuses(self):
        proc = self.run_script(override(default_scenario(), "remote get-url github", rc=2))
        self.assert_refused(proc)
        self.assertIn("remote `github` is not configured", proc.stderr)
        self.assert_no_mutation()

    def test_any_one_of_the_three_blobs_missing_refuses(self):
        """All three or none. Each path is failed in turn: a check that only notices the
        first missing file would pass two thirds of this test."""
        for path in ("watch_report_train_run.py", "profiles.json", "waker-config.json"):
            with self.subTest(missing=path):
                scen = [{"match": "cat-file -e github/main:docs/orchestration/" + path,
                         "rc": 1, "out": ""}] + default_scenario()
                proc = self.run_script(scen)
                self.assert_refused(proc)
                self.assertIn(path, proc.stderr)
                self.assert_no_mutation()

    def test_unreadable_watch_store_refuses(self):
        proc = self.run_script(override(default_scenario(), "watch-list", rc=1,
                                        out="wakerctl: state dir unreadable"))
        self.assert_refused(proc)
        self.assertIn("watch store not readable", proc.stderr)
        self.assert_no_mutation()

    def test_predecessor_absent_from_store_refuses(self):
        proc = self.run_script(override(default_scenario(), "watch-list", rc=0,
                                        out="some-other-watch\tslurm-job\tarmed"))
        self.assert_refused(proc)
        self.assertIn("is not in the watch store", proc.stderr)
        self.assert_no_mutation()

    def test_wrong_mode_refuses(self):
        """The exec bit is load-bearing: wakerctl execs argv[0] directly."""
        proc = self.run_script(override(default_scenario(), "stat -c %a", rc=0, out="644"))
        self.assert_refused(proc)
        self.assertIn("not 755", proc.stderr)
        self.assert_no_mutation(allow=("fetch github", "checkout github/main"))

    def test_argv0_rejected_by_wakerctl_refuses(self):
        """The symlink-out-of-tree case: argvchk exits 6, so the deployment stops."""
        proc = self.run_script(
            override(default_scenario(), "watch_report_train_run.py " + CREPO, rc=6,
                     out="MISMATCH: wakerctl.py:340-346 would raise ..."))
        self.assert_refused(proc)
        self.assertIn("argv[0] would be REJECTED", proc.stderr)
        self.assert_no_mutation(allow=("fetch github", "checkout github/main"))

    def test_incoherent_profile_pair_refuses_before_arming(self):
        """waker-config naming a profile profiles.json does not define is the MEASURED
        failure: every dispatch raises AgentCtlError. It must stop the deployment."""
        proc = self.run_script(
            override(default_scenario(), "codex-waker", rc=10,
                     out="MISMATCH: profiles.json does NOT define 'codex-waker'"))
        self.assert_refused(proc)
        self.assertIn("INCOHERENT", proc.stderr)
        self.assertEqual([], self.commands_matching("watch-add"))
        self.assertEqual([], self.commands_matching("watch-disarm"))

    def test_unknown_argument_refuses(self):
        proc = self.run_script(args=("--yolo",))
        self.assertEqual(2, proc.returncode)
        self.assertIn("unknown argument", proc.stderr)
        self.assert_no_mutation()


class TestTheOneCheckout(Harness):
    def test_checkout_is_a_single_command_carrying_all_three_paths(self):
        proc = self.run_script()
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        checkouts = self.commands_matching("checkout github/main")
        self.assertEqual(1, len(checkouts),
                         "the checkout must be ONE command; got %d: %s" % (len(checkouts), checkouts))
        for path in ("docs/orchestration/watch_report_train_run.py",
                     "docs/orchestration/profiles.json",
                     "docs/orchestration/waker-config.json"):
            self.assertIn(path, checkouts[0],
                          "the single checkout omits %s -- it can be split, which is the "
                          "failure mode OI-135 (f) exists to prevent" % path)

    def test_checkout_never_resets_pulls_or_cleans_the_cluster_checkout(self):
        """OI-130: that checkout is 98 commits behind and must not be brought forward."""
        self.run_script()
        for forbidden in ("reset", "pull", "clean", "checkout github/main\n", "merge"):
            offenders = [c for c in self.cmds
                         if forbidden in c and "checkout github/main --" not in c]
            self.assertEqual([], offenders,
                             "issued a forbidden repo-wide operation: %s" % offenders)

    def test_deployment_is_verified_by_diff_not_by_exit_status(self):
        self.run_script()
        self.assertTrue(self.commands_matching("diff --exit-code github/main"),
                        "the checkout was accepted without diffing against the source ref")


class TestArmThenRetire(Harness):
    def test_add_happens_before_retire(self):
        proc = self.run_script()
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        adds = [i for i, c in enumerate(self.cmds) if "watch-add" in c]
        disarms = [i for i, c in enumerate(self.cmds) if "watch-disarm" in c]
        self.assertTrue(adds and disarms, "expected both an add and a disarm: %s" % self.cmds)
        self.assertLess(adds[0], disarms[0],
                        "ADD-THEN-RETIRE inverted: disarm at %d precedes add at %d (ISSUE-56)"
                        % (disarms[0], adds[0]))

    def test_readback_happens_between_the_add_and_the_retire(self):
        """The ordering that matters is not add-before-disarm but
        add -> VERIFY -> disarm: an unverified add is what ISSUE-56 actually was."""
        self.run_script()
        add = next(i for i, c in enumerate(self.cmds) if "watch-add" in c)
        readback = next(i for i, c in enumerate(self.cmds) if "-r4.json" in c)
        disarm = next(i for i, c in enumerate(self.cmds) if "watch-disarm" in c)
        self.assertLess(add, readback)
        self.assertLess(readback, disarm)

    def test_failed_readback_leaves_the_predecessor_armed(self):
        proc = self.run_script(override(default_scenario(), "-r4.json", rc=4,
                                        out="MISMATCH: params.tasks '1' != '0-0'"))
        self.assert_refused(proc)
        self.assertIn("still armed", proc.stderr)
        self.assertEqual([], self.commands_matching("watch-disarm"),
                         "retired the only working watch after a FAILED readback")

    def test_failed_add_leaves_the_predecessor_armed(self):
        proc = self.run_script(override(default_scenario(), "watch-add", rc=1,
                                        out="wakerctl: watch already exists"))
        self.assert_refused(proc)
        self.assertEqual([], self.commands_matching("watch-disarm"))

    def test_arm_command_is_a_complete_valid_watch_add(self):
        """wakerctl.py:320-331: kind slurm-array requires params job_id AND tasks. An arm
        carrying only `--action command --argv ...` -- as the briefing message stated it --
        would be REJECTED, so the script must supply the rest."""
        self.run_script()
        arm = self.commands_matching("watch-add")[0]
        for needle in ("--id gate5-do-train-57266000-r4", "--kind slurm-array",
                       "--param job_id=57266000", "--param tasks=0-0",
                       "--action command", "--argv " + PROG,
                       "--job-id 57266000", "--task-id 0", "--log-dir "):
            self.assertIn(needle, arm, "arm command lacks %r: %s" % (needle, arm))

    def test_tasks_is_a_spec_and_not_a_count(self):
        """r2 died of `tasks:"1"`: expand_spec("1") == [1], task index 1, which the array
        does not have. The spec for a single task 0 is "0-0"."""
        self.run_script()
        arm = self.commands_matching("watch-add")[0]
        self.assertIn("tasks=0-0", arm)
        self.assertNotRegex(arm, r"tasks=1(\s|$)")

    def test_argv_is_last_because_it_is_argparse_REMAINDER(self):
        self.run_script()
        arm = self.commands_matching("watch-add")[0]
        tail = arm.split("--argv ", 1)[1]
        for swallowed in (" --id ", " --kind ", " --param ", " --action ", " --max-retries "):
            self.assertNotIn(swallowed, tail,
                             "%r appears AFTER --argv, so argparse.REMAINDER swallows it "
                             "into the command's argv (wakerctl.py:1788)" % swallowed)

    def test_disarmed_predecessor_is_not_read_as_armed(self):
        """"disarmed" CONTAINS "armed". A substring test here has already reported two
        armed watches on a job that had one of each (wakerctl.py:724-735)."""
        scen = override(default_scenario(), "watch-list", rc=0, out=(
            "gate5-do-train-57266000-r3\tslurm-array\tdisarmed\n"
            "gate5-do-train-57266000-r4\tslurm-array\tdisarmed"))
        scen = override(scen, "-r4.json", rc=4, out=(
            "state='disarmed'\nMISMATCH: state 'disarmed' != 'armed'"))
        proc = self.run_script(scen)
        self.assert_refused(proc)
        self.assertEqual([], self.commands_matching("watch-disarm"),
                         "a disarmed r4 was accepted as armed and r3 was retired anyway")

    def test_idempotent_when_the_swap_has_already_happened(self):
        """Re-running after a successful deployment must be a no-op that VERIFIES."""
        scen = override(default_scenario(), "watch-list", rc=0, out=(
            "gate5-do-train-57266000-r3\tslurm-array\tdisarmed\n"
            "gate5-do-train-57266000-r4\tslurm-array\tarmed"))
        proc = self.run_script(scen)
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertEqual([], self.commands_matching("watch-add"),
                         "re-armed an existing watch; wakerctl would raise 'watch already exists'")
        self.assertEqual([], self.commands_matching("watch-disarm"),
                         "re-disarmed an already-disarmed watch")
        self.assertIn("already exists", proc.stdout)


class TestPlanMode(Harness):
    def test_plan_mode_is_the_default_and_mutates_nothing(self):
        proc = self.run_script(args=())
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assert_no_mutation()
        self.assertIn("PLAN COMPLETE", proc.stdout)

    def test_plan_mode_prints_the_exact_commands_it_would_run(self):
        proc = self.run_script(args=())
        for needle in ("checkout github/main --", "watch-add --id gate5-do-train-57266000-r4",
                       "watch-disarm --id gate5-do-train-57266000-r3"):
            self.assertIn(needle, proc.stdout)

    def test_plan_mode_still_refuses_when_unreachable(self):
        proc = self.run_script(override(default_scenario(), "true", rc=255), args=())
        self.assert_refused(proc)

    def test_live_state_regeneration_is_opt_in(self):
        proc = self.run_script()
        self.assertEqual([], self.commands_matching("generate_live_state.py"),
                         "step (e) ran without --regen-live-state")
        self.assertIn("OFF by default", proc.stdout)
        proc2 = self.run_script(args=("--execute", "--regen-live-state"))
        self.assertTrue(self.commands_matching("generate_live_state.py"))
        self.assertEqual(0, proc2.returncode, proc2.stdout + proc2.stderr)


class TestResourceRemeasurement(Harness):
    def test_five_fields_are_read_and_reported(self):
        proc = self.run_script()
        self.assertIn("cpus_per_task=[32]", proc.stdout)
        self.assertIn("memory_per_task=[3G]", proc.stdout)
        self.assertIn("time_limit=[02:00:00]", proc.stdout)
        self.assertIn("qos=[shared_gp]", proc.stdout)
        self.assertIn("gpus_per_task=[gres/gpu:1]", proc.stdout)
        self.assertIn("still queued (PENDING)", proc.stdout)

    def test_an_unmeasurable_field_is_recorded_honestly_and_does_not_fail_the_step(self):
        """CHANGED DIRECTION, 2026-08-19, on the mediator's instruction and with its reason:
        an honest `NOT MEASURED` is information and a failed step is not. Failing was right
        while the values had nowhere to go; now that the writer records them, recording the
        absence beats refusing. What still fails is a receipt that cannot be written."""
        trimmed = SCONTROL_HAPPY.replace("QOS=shared_gp ", "")
        proc = self.run_script(override(default_scenario(), "scontrol show job",
                                        rc=0, out=trimmed))
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertIn("scontrol printed no such token", proc.stdout)
        self.assertIn("never guessed and never downgraded", proc.stdout)
        # the sentinel, not an empty string, is what crosses to the writer
        write = [c for c in self.cmds if "array-active-57266000.json" in c][0]
        self.assertIn("@ABSENT@", write)

    def test_the_receipt_is_written_and_a_failed_write_fails_the_step(self):
        proc = self.run_script()
        writes = [c for c in self.cmds if "array-active-57266000.json" in c]
        self.assertEqual(1, len(writes), "expected exactly one receipt write: %s" % writes)
        self.assertIn("receipt-write-ok", proc.stdout)
        proc2 = self.run_script(override(default_scenario(), "array-active-57266000.json",
                                         rc=12, out="receipt-unreadable: ..."))
        self.assertEqual(1, proc2.returncode)
        self.assertIn("could NOT write the receipt", proc2.stderr)

    def test_plan_mode_does_not_write_the_receipt(self):
        proc = self.run_script(args=())
        self.assertEqual([], [c for c in self.cmds if "array-active-57266000.json" in c])
        self.assertIn("write cpus_per_task", proc.stdout)

    def test_a_started_job_is_reported_as_itself_not_forced_into_pending(self):
        proc = self.run_script(override(default_scenario(), "sacct", rc=0,
                                        out="57266000_0 RUNNING"))
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertIn("NOT pending any more", proc.stdout)


class TestWorktreeHygiene(Harness):
    DANGLING = "/pscratch/sd/j/josephrb/live-state-regen-e8c857f3"

    def test_absent_registration_is_reported_not_invented(self):
        proc = self.run_script()
        self.assertIn("never ran, as suspected", proc.stdout)
        self.assertEqual([], self.commands_matching("worktree prune"))

    def test_registered_but_missing_directory_is_pruned(self):
        scen = override(default_scenario(), "worktree list", rc=0,
                        out=CREPO + "  abc1234 [main]\n" + self.DANGLING + "  e8c857f3 (detached HEAD)")
        proc = self.run_script(scen)
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertTrue(self.commands_matching("worktree prune"))

    def test_a_dirty_worktree_is_never_removed(self):
        """Preserve the diff before reverting -- parts of it may be real findings."""
        scen = override(default_scenario(), "worktree list", rc=0,
                        out=CREPO + "  abc1234 [main]\n" + self.DANGLING + "  e8c857f3 (detached HEAD)")
        scen = override(scen, "test -d", rc=0)
        scen = [{"match": "status --porcelain", "rc": 0, "out": " M docs/orchestration/LIVE-STATE.md"}] + scen
        proc = self.run_script(scen)
        self.assertEqual(1, proc.returncode)
        self.assertIn("is DIRTY; NOT removing", proc.stderr)
        self.assertEqual([], self.commands_matching("worktree remove"))
        self.assertEqual([], self.commands_matching("worktree prune"))


# ============================================================================
# The script's EMBEDDED probes, run FOR REAL. No fake transport here.
# ============================================================================

def extract_heredoc(name):
    """Pull `cat > "$TMPD/<name>" <<'PYEOF' ... PYEOF` out of the shell source."""
    text = SCRIPT_UNDER_TEST.read_text()
    marker = '/%s" <<\'PYEOF\'\n' % name
    start = text.index(marker) + len(marker)
    end = text.index("\nPYEOF", start)
    return text[start:end] + "\n"


class TestEmbeddedProbes(unittest.TestCase):
    """These are the tests that do not depend on a hypothesis about the login node."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="oi135-probe-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def write(self, name, body):
        p = self.tmp / name
        p.write_text(body)
        return p

    def run_probe(self, name, *args):
        prog = self.write(name, extract_heredoc(name))
        return subprocess.run([sys.executable, str(prog)] + [str(a) for a in args],
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    def watch_json(self, **over):
        w = {
            "watch_id": "gate5-do-train-57266000-r4",
            "kind": "slurm-array",
            "state": "armed",
            "params": {"job_id": "57266000", "tasks": "0-0"},
            "action": {"type": "command", "argv": [PROG, "--job-id", "57266000"]},
        }
        w.update(over)
        p = self.tmp / "watch.json"
        p.write_text(json.dumps(w))
        return p

    # -- readback.py -------------------------------------------------------------
    def test_readback_accepts_the_correct_watch(self):
        proc = self.run_probe("readback.py", self.watch_json(),
                              "57266000", "0-0", "armed", PROG)
        self.assertEqual(0, proc.returncode, proc.stdout)
        self.assertIn("readback-ok", proc.stdout)

    def test_readback_rejects_a_disarmed_watch_although_disarmed_contains_armed(self):
        """THE substring trap, tested on the real code rather than on a fake rc."""
        proc = self.run_probe("readback.py", self.watch_json(state="disarmed"),
                              "57266000", "0-0", "armed", PROG)
        self.assertEqual(4, proc.returncode, proc.stdout)
        self.assertIn("MISMATCH", proc.stdout)
        self.assertIn("state", proc.stdout)

    def test_readback_rejects_the_r2_defect_tasks_as_a_count(self):
        p = self.watch_json(params={"job_id": "57266000", "tasks": "1"})
        proc = self.run_probe("readback.py", p, "57266000", "0-0", "armed", PROG)
        self.assertEqual(4, proc.returncode, proc.stdout)
        self.assertIn("a SPEC, not a count", proc.stdout)

    def test_readback_rejects_a_root_resume_action(self):
        p = self.watch_json(action={"type": "root-resume", "context": "..."})
        proc = self.run_probe("readback.py", p, "57266000", "0-0", "armed", PROG)
        self.assertEqual(4, proc.returncode, proc.stdout)
        self.assertIn("action.type", proc.stdout)

    def test_readback_rejects_the_wrong_program(self):
        p = self.watch_json(action={"type": "command", "argv": ["/elsewhere/other.py"]})
        proc = self.run_probe("readback.py", p, "57266000", "0-0", "armed", PROG)
        self.assertEqual(4, proc.returncode, proc.stdout)

    def test_readback_treats_an_unreadable_store_as_a_refusal_not_a_pass(self):
        proc = self.run_probe("readback.py", self.tmp / "absent.json",
                              "57266000", "0-0", "armed", PROG)
        self.assertEqual(3, proc.returncode, proc.stdout)
        self.assertIn("readback-error", proc.stdout)

    # -- argvchk.py --------------------------------------------------------------
    def test_argvchk_accepts_a_real_file_inside_the_repo(self):
        repo = self.tmp / "repo"
        (repo / "docs" / "orchestration").mkdir(parents=True)
        prog = repo / "docs" / "orchestration" / "watch_report_train_run.py"
        prog.write_text("#!/usr/bin/python3.11\nprint(1)\n")
        prog.chmod(0o755)
        proc = self.run_probe("argvchk.py", prog, repo)
        self.assertEqual(0, proc.returncode, proc.stdout)
        self.assertIn("argv0-ok", proc.stdout)

    def test_argvchk_rejects_a_symlink_pointing_out_of_the_repo(self):
        """`.resolve()` is why a symlink fails: wakerctl.py:340-346 tests the RESOLVED
        path's parents. Built here as a real symlink, not as a mocked return value."""
        repo = self.tmp / "repo2"
        (repo / "docs" / "orchestration").mkdir(parents=True)
        outside = self.tmp / "outside.py"
        outside.write_text("#!/usr/bin/python3.11\n")
        link = repo / "docs" / "orchestration" / "watch_report_train_run.py"
        link.symlink_to(outside)
        proc = self.run_probe("argvchk.py", link, repo)
        self.assertEqual(6, proc.returncode, proc.stdout)
        self.assertIn("wakerctl.py:340-346", proc.stdout)
        self.assertIn("is_symlink=True", proc.stdout)

    def test_argvchk_rejects_a_relative_path(self):
        repo = self.tmp / "repo3"
        (repo / "docs").mkdir(parents=True)
        prog = repo / "docs" / "p.py"
        prog.write_text("#!/usr/bin/python3.11\n")
        cwd_proc = subprocess.run(
            [sys.executable, str(self.write("argvchk.py", extract_heredoc("argvchk.py"))),
             "docs/p.py", str(repo)],
            cwd=str(repo), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        self.assertEqual(6, cwd_proc.returncode, cwd_proc.stdout)
        self.assertIn("is_absolute=False", cwd_proc.stdout)

    def test_argvchk_rejects_a_file_with_no_shebang(self):
        repo = self.tmp / "repo4"
        (repo / "docs").mkdir(parents=True)
        prog = repo / "docs" / "p.py"
        prog.write_text("print(1)\n")
        proc = self.run_probe("argvchk.py", prog, repo)
        self.assertEqual(7, proc.returncode, proc.stdout)

    # -- profchk.py: fixtures FROM THE PRODUCER ----------------------------------
    def test_profchk_accepts_the_repositorys_own_committed_pair(self):
        """The fixture is the repo's real profiles.json and waker-config.json -- the files
        the deployment will actually ship. A fixture derived from my reading of the rule
        could not disagree with the rule; this one can."""
        proc = self.run_probe("profchk.py",
                              REPO / "docs" / "orchestration" / "waker-config.json",
                              REPO / "docs" / "orchestration" / "profiles.json",
                              "codex-waker")
        self.assertEqual(0, proc.returncode,
                         "the COMMITTED pair does not satisfy the deployment's own "
                         "coherence check:\n" + proc.stdout)
        self.assertIn("profile-pair-ok", proc.stdout)
        self.assertIn("codex-waker", proc.stdout)

    def test_profchk_rejects_a_config_whose_profile_is_undefined(self):
        """The MEASURED failure: AgentCtlError: Unknown profile 'codex-waker'."""
        cfg = self.write("waker-config.json", json.dumps({"root": {"profile": "codex-waker"}}))
        prof = self.write("profiles.json", json.dumps({"profiles": {"codex-personal": {}}}))
        proc = self.run_probe("profchk.py", cfg, prof, "codex-waker")
        self.assertEqual(10, proc.returncode, proc.stdout)
        self.assertIn("does NOT define", proc.stdout)

    def test_profchk_rejects_a_config_naming_some_other_profile(self):
        cfg = self.write("waker-config.json", json.dumps({"root": {"profile": "codex-personal"}}))
        prof = self.write("profiles.json", json.dumps({"profiles": {"codex-personal": {}}}))
        proc = self.run_probe("profchk.py", cfg, prof, "codex-waker")
        self.assertEqual(9, proc.returncode, proc.stdout)

    def test_profchk_accepts_either_profiles_json_shape(self):
        """profiles.json is not this script's file; both a flat table and a `profiles`
        key are accepted rather than assuming a shape."""
        cfg = self.write("waker-config.json", json.dumps({"root": {"profile": "codex-waker"}}))
        flat = self.write("flat.json", json.dumps({"codex-waker": {"model": "gpt-5.6-luna"}}))
        proc = self.run_probe("profchk.py", cfg, flat, "codex-waker")
        self.assertEqual(0, proc.returncode, proc.stdout)


class TestReceiptWriter(unittest.TestCase):
    """receipt_write.py, run FOR REAL against a copy of the repository's own receipt.

    The fixture is the committed
    `state/gate5-do-train-array-active-57266000.json` -- the file the deployment will
    actually rewrite, with its 27 keys and its PROVENANCE block. A fixture I invented could
    not disagree with my reading of the rule; this one can.
    """

    FIELDS = ["cpus_per_task", "memory_per_task", "time_limit", "qos", "gpus_per_task"]
    MEASURED = ["32", "3G", "02:00:00", "shared_gp", "gres/gpu:1"]
    SOURCE = (REPO / "docs" / "orchestration" / "state" /
              "gate5-do-train-array-active-57266000.json")

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="oi135-receipt-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.prog = self.tmp / "receipt_write.py"
        self.prog.write_text(extract_heredoc("receipt_write.py"))
        self.receipt = self.tmp / self.SOURCE.name
        shutil.copyfile(str(self.SOURCE), str(self.receipt))
        self.original = json.loads(self.receipt.read_text())

    def write(self, values=None, job_id="57266000", receipt=None):
        args = [sys.executable, str(self.prog), str(receipt or self.receipt), job_id]
        args += list(values if values is not None else self.MEASURED)
        return subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    def current(self):
        return json.loads(self.receipt.read_text())

    def test_the_committed_receipt_still_has_the_five_keys_as_NOT_MEASURED(self):
        """If this fails, the receipt moved on and the writer's premise needs re-reading --
        which is the point of using the real file as the fixture."""
        for field in self.FIELDS:
            self.assertIn(field, self.original)
        self.assertEqual("57266000", str(self.original["job_id"]))

    def test_only_the_five_keys_change_and_the_other_keys_are_byte_identical(self):
        proc = self.write()
        self.assertEqual(0, proc.returncode, proc.stdout)
        after = self.current()
        for field, want in zip(self.FIELDS, self.MEASURED):
            self.assertEqual(want, after[field])
        untouched = set(self.original) - set(self.FIELDS)
        for key in untouched:
            self.assertEqual(
                json.dumps(self.original[key], sort_keys=True),
                json.dumps(after[key], sort_keys=True),
                "key %r was modified; only the five resource keys may change" % key)
        # exactly one key added, and it is the provenance key
        self.assertEqual({"resource_fields_remeasured"}, set(after) - set(self.original))

    def test_the_values_arrive_with_their_command_and_a_utc_timestamp(self):
        self.write()
        prov = self.current()["resource_fields_remeasured"]
        self.assertEqual("scontrol show job 57266000", prov["measured_by_command"])
        self.assertRegex(prov["measured_at_utc"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
        self.assertEqual(self.FIELDS, prov["fields"])
        self.assertIn("deploy_oi135_watcher_swap.sh", prov["written_by"])

    def test_an_absent_token_becomes_the_literal_NOT_MEASURED(self):
        """Never null, never "", never "?"."""
        values = list(self.MEASURED)
        values[3] = "@ABSENT@"
        proc = self.write(values)
        self.assertEqual(0, proc.returncode, proc.stdout)
        self.assertEqual("NOT MEASURED", self.current()["qos"])
        self.assertNotIn("?", str(self.current()["qos"]))

    def test_a_non_canonical_placeholder_is_normalised_not_preserved(self):
        """(iii) is a claim about the STRING in the file, so `?`/null/"" must become the
        literal `NOT MEASURED` -- preserving them would satisfy the rule only by accident of
        this receipt already holding the canonical form."""
        for placeholder in ("?", "", None, "unknown"):
            with self.subTest(placeholder=placeholder):
                doc = dict(self.original)
                doc["qos"] = placeholder
                self.receipt.write_text(json.dumps(doc, indent=2))
                values = list(self.MEASURED)
                values[3] = "@ABSENT@"
                proc = self.write(values)
                self.assertEqual(0, proc.returncode, proc.stdout)
                self.assertEqual("NOT MEASURED", self.current()["qos"])

    def test_a_measured_value_is_never_downgraded_to_NOT_MEASURED(self):
        """A second run with a thinner `scontrol` must not destroy the first run's evidence."""
        self.write()
        self.assertEqual("shared_gp", self.current()["qos"])
        values = list(self.MEASURED)
        values[3] = "@ABSENT@"
        proc = self.write(values)
        self.assertEqual(0, proc.returncode, proc.stdout)
        self.assertEqual("shared_gp", self.current()["qos"],
                         "overwrote a measured value with NOT MEASURED")
        self.assertIn("LEFT ALONE", proc.stdout)

    def test_a_second_identical_run_is_a_noop(self):
        self.write()
        first = self.receipt.read_text()
        proc = self.write()
        self.assertEqual(0, proc.returncode, proc.stdout)
        self.assertIn("receipt-write-noop", proc.stdout)
        self.assertEqual(first, self.receipt.read_text(),
                         "an idempotent re-run rewrote the file")

    def test_a_receipt_for_another_job_is_refused_and_left_alone(self):
        """The path is built from a variable, so the file's own declared subject is asked.
        A definite description is not a citation."""
        before = self.receipt.read_text()
        proc = self.write(job_id="57999999")
        self.assertEqual(13, proc.returncode, proc.stdout)
        self.assertIn("receipt-subject-mismatch", proc.stdout)
        self.assertEqual(before, self.receipt.read_text())

    def test_a_missing_receipt_fails_and_is_never_created(self):
        absent = self.tmp / "does-not-exist.json"
        proc = self.write(receipt=absent)
        self.assertEqual(12, proc.returncode, proc.stdout)
        self.assertIn("receipt-unreadable", proc.stdout)
        self.assertFalse(absent.exists(), "the writer CREATED a receipt out of nothing")

    def test_an_unparseable_receipt_fails_and_is_not_overwritten(self):
        broken = self.tmp / "broken.json"
        broken.write_text("{not json")
        proc = self.write(receipt=broken)
        self.assertEqual(12, proc.returncode, proc.stdout)
        self.assertEqual("{not json", broken.read_text())

    def test_a_receipt_missing_the_five_keys_is_refused(self):
        other = self.tmp / "other.json"
        other.write_text(json.dumps({"job_id": "57266000", "purpose": "something else"}))
        proc = self.write(receipt=other)
        self.assertEqual(14, proc.returncode, proc.stdout)
        self.assertIn("receipt-shape-mismatch", proc.stdout)

    def test_the_stale_prose_key_is_flagged_and_not_edited(self):
        self.write()
        after = self.current()
        self.assertEqual(self.original["why_resources_not_measured"],
                         after["why_resources_not_measured"])
        self.assertIn("STALE", " ".join(after["resource_fields_remeasured"].keys()))

    def test_the_receipt_stays_valid_json_with_the_repositorys_indentation(self):
        self.write()
        text = self.receipt.read_text()
        json.loads(text)
        self.assertTrue(text.endswith("\n"))
        self.assertIn('\n  "job_id"', text, "2-space indent was not preserved")


class TestScriptHygiene(unittest.TestCase):
    """Static properties of the script that the campaign has been bitten by."""

    def setUp(self):
        self.text = SCRIPT_UNDER_TEST.read_text()

    def test_is_executable_with_a_shebang(self):
        self.assertTrue(self.text.startswith("#!"))
        mode = stat.S_IMODE(SCRIPT.stat().st_mode)
        self.assertEqual(0o755, mode, "mode is %o" % mode)

    def test_bash_32_compatible_constructs_only(self):
        # CODE only. The first version of this test scanned the whole file and fired on the
        # script's own comment saying "no `mapfile`" -- an over-broad check whose cheapest
        # repair would have been deleting a true sentence from the documentation.
        code = "\n".join(line for line in self.text.splitlines()
                         if not line.lstrip().startswith("#"))
        for banned in ("mapfile", "declare -A", "${!", "readarray"):
            self.assertNotIn(banned, code,
                             "%r is bash 4+; the rehearsal host is 3.2.57 and the login "
                             "node is 4.4, and they have already disagreed once" % banned)

    def test_parses_under_bash(self):
        proc = subprocess.run(["bash", "-n", str(SCRIPT_UNDER_TEST)],
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        self.assertEqual(0, proc.returncode, proc.stdout)

    def test_no_status_is_read_after_a_pipe(self):
        """`$?` after a pipeline is the TAIL's status. Three of this campaign's wrong
        conclusions in one day came from that, so the script never does it."""
        for i, line in enumerate(self.text.splitlines(), 1):
            if re.search(r"\$\?", line) and "|" in line:
                self.fail("line %d reads $? on a line containing a pipe: %s" % (i, line))
        self.assertIn("R_RC=$?", self.text)

    def test_the_three_deploy_paths_are_one_variable_used_once_in_the_checkout(self):
        self.assertIn("DEPLOY_PATHS=\"$P_SCRIPT $P_PROFILES $P_WAKERCFG\"", self.text)
        self.assertIn("checkout github/main -- $DEPLOY_PATHS", self.text)
        self.assertEqual(3, int(re.search(r"DEPLOY_PATH_COUNT=(\d+)", self.text).group(1)))


# ============================================================================
# Mutation runner: an unkilled mutant means the matching test is decorative.
# ============================================================================

MUTANTS = [
    ("m1-drop-reachability-guard",
     'if ! remote "true"; then', 'if false; then'),
    ("m2-split-the-three-file-checkout",
     'CHECKOUT_CMD="git -C $CREPO checkout github/main -- $DEPLOY_PATHS"',
     'CHECKOUT_CMD="git -C $CREPO checkout github/main -- $P_SCRIPT"'),
    ("m3-make-the-disarm-reachable-after-a-failed-readback",
     'die "readback of $WATCH_NEW FAILED (rc=$R_RC). $WATCH_OLD is still armed; NOTHING was retired."',
     'fail "readback of $WATCH_NEW FAILED (rc=$R_RC). $WATCH_OLD is still armed; NOTHING was retired."'),
    ("m4-substring-state-comparison-in-readback",
     "if state != want_state:", "if want_state not in state:"),
    ("m5-tasks-as-a-count",
     'TASKS_SPEC="0-0"', 'TASKS_SPEC="1"'),
    ("m6-accept-an-undefined-profile",
     "if named not in keys:", "if False:"),
    ("m7-let-the-writer-downgrade-a-measured-value",
     "    if value is None:\n        return True",
     "    if value is None:\n        return True\n    return True"),
    ("m8-write-into-a-receipt-for-another-job",
     'if str(receipt.get("job_id", "")) != job_id:', "if False:"),
    ("m9-writer-touches-a-sixth-key",
     "    receipt[field] = raw\n    changes += 1",
     '    receipt[field] = raw\n    receipt["schema_version"] = 99\n    changes += 1'),
    ("m10-record-the-values-without-their-command",
     '"measured_by_command": command,', '"measured_by_command": "",'),
]


def run_mutations():
    src = SCRIPT.read_text()
    tmp = Path(tempfile.mkdtemp(prefix="oi135-mutants-"))
    print("=== mutation run: %d mutants against %s" % (len(MUTANTS), SCRIPT.name))
    caught = 0
    for name, old, new in MUTANTS:
        if old not in src:
            print("%-52s UNAPPLIED (anchor text not found -- this mutant is stale)" % name)
            continue
        target = tmp / (name + ".sh")
        target.write_text(src.replace(old, new, 1))
        target.chmod(0o755)
        env = dict(os.environ, OI135_SCRIPT=str(target))
        proc = subprocess.run([sys.executable, "-m", "unittest", "-q", Path(__file__).stem],
                              cwd=str(HERE), env=env,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        killed = proc.returncode != 0
        caught += 1 if killed else 0
        first = ""
        for line in proc.stdout.splitlines():
            if line.startswith("FAIL:") or line.startswith("ERROR:"):
                first = " <- " + line
                break
        print("%-52s %s%s" % (name, "CAUGHT" if killed else "SURVIVED (test is decorative)", first))
    print("=== %d/%d mutants caught" % (caught, len(MUTANTS)))
    shutil.rmtree(tmp, True)
    return 0 if caught == len(MUTANTS) else 1


if __name__ == "__main__":
    if "--mutate" in sys.argv:
        sys.exit(run_mutations())
    unittest.main()
