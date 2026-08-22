#!/usr/bin/env python3
"""The eight k=0 launchers: two mandatory roots, and EVERY production Python invocation guarded.

Joseph's ruling 17 (two roots) and his round-2 authorization of 2026-08-22 ("every production
Python invocation across the eight k=0 launchers is to be routed through mnv_guarded_run.py, with a
required inventory ... including the contract-required executing-file parity calls, source-manifest
comparison, and P-4 import-set mechanism").

EVERY LAUNCHER IS EXECUTED, NOT READ. `bash -n` is not enough and this repository has the receipt:
on 2026-08-18 a hook inserted between a `\\`-continued command's lines truncated the command to
`bootstrap_nd.py --npz of_inputs_5d.npz` with no seed arguments at all, and `bash -n` PASSED --
syntax valid, arguments destroyed. So the fixture builds a REAL GIT TREE as the code root, with
real copies of `mnv_guarded_run.py`, `verify_executing_copy_is_committed.py` and
`mnv_source_manifest.py`, stub entrypoints that make a genuine repository-local import, and a real
source manifest; then it runs each launcher and reads the artifacts it produced.

WHAT IT STILL CANNOT SAY. It runs bash locally (3.2.57 on macOS, 4.4 on Perlmutter) and never under
Slurm, so `BASH_SOURCE`-under-spool behaviour is untested here and remains ruling 14's business.
The entrypoints are stubs: this measures the LAUNCHER's plumbing, never the science.
"""
import json
import os
import pathlib
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
ND = HERE.parent
REPO = HERE.parents[1]

#: (launcher, [entrypoint stubs it needs], [inventory tags it must emit])
#: The tags are the third field of `mnv_inv <tag>` and therefore enumerate EVERY production Python
#: invocation -- 14 of them across 8 launchers, which is why "one per launcher" would have been the
#: wrong count to assume.
LAUNCHERS = (
    ("sbatch_bootstrap_5d_gpu.sh", ["bootstrap_nd.py"], ["bootstrap_nd"]),
    ("sbatch_seedscan_split_5d.sh", ["seedscan_split.py"], ["seedscan_split"]),
    ("sbatch_unfold_5d_detector_bkgaware_gpu.sh", ["unfold_nd_omnifold_unbinned.py"],
     ["unfold_nd_universe"]),
    ("sbatch_sweep_bank_5d_run_bkgaware_gpu.sh", ["sweep_bank_5d.py"], ["sweep_bank_5d"]),
    ("sbatch_uthrow_run_5d_fast.sh", ["unified_throw_cov_5d.py"], ["uthrow_run"]),
    ("sbatch_uthrow_block_5d.sh", ["unified_throw_cov_5d.py"], ["uthrow_block_flux"]),
    ("sbatch_uthrow_combine_5d_fast.sh", ["unified_throw_cov_5d.py"], ["uthrow_combine"]),
    ("sbatch_finalize_5d_bkgaware_gpu.sh",
     # `adopt_unified_5d.py` is here because the finalize launcher PARITY-CHECKS it: it is an
     # executing file on this path even though the launcher never invokes it directly -- the
     # stamped wrapper does, as a guarded child. It has no inventory tag for that reason.
     ["combine_cov_nd.py", "analyze_universes_5d.py", "mii_adopt_unified_5d_stamped.py",
      "adopt_unified_5d.py"],
     # ONLY THE THREE THAT ARE REACHABLE. The two `adopt_stamped_*` invocations sit BELOW the
     # declared-member PAUSE branch, which ruling 13 defers removing, so a declared run exits 0
     # before reaching them -- measured here, not assumed. Their guarding is therefore verified
     # statically (`test_the_adopt_calls_pass_the_child_guard_operands`) and dynamically by
     # `test_remedy_a_adopt_wrapper.TheChildArgvIsGuarded` and `test_n2_child_boundary`, never by
     # running this launcher. That is a REAL LIMIT of this file and it is why it is written down.
     ["combine_cov_stat", "combine_cov_ml", "analyze_universes_5d"]),
)

#: The complete set of invocation tags, derived from the table above rather than restated.
ALL_TAGS = sorted({t for _l, _e, tags in LAUNCHERS for t in tags})

CLUSTER_ROOT = "/" + "/".join(("pscratch", "sd", "j", "josephrb", "MINERvA-OmniFold"))

#: Every stub entrypoint imports this, so the guard has something real to resolve and the inventory
#: is NON-EMPTY. A guarded run whose inventory is empty proves nothing about the tree.
SIBLING = "k0_fixture_sibling"

STUB_ENTRY = f'''#!/usr/bin/env python3
import sys
from pathlib import Path
_ND = str(Path(__file__).resolve().parents[0])
if _ND not in sys.path:
    sys.path.insert(0, _ND)
import {SIBLING}
print("[stub-entry] ran", __file__, "loaded", {SIBLING}.__file__)
'''

STUB_MR = '''echo "[stub] lib_member_resume sourced from $BASH_SOURCE"
mr_require_valid_offset(){ :; }
mr_prefix(){ echo "$1"; }
mr_dir_prefix(){ echo "$1"; }
mr_skip_if_complete(){ return 1; }
mr_declared(){ [ -n "${MNV_EST_SEED_OFFSET:-}" ]; }
mr_member_root(){ echo member_k000000; }
mr_run(){ shift; "$@"; }
rg_valid_npz(){ return 1; }
rg_marker_path(){ echo "/dev/null"; }
rg_stat_size(){ echo 0; }
rg_stat_mtime(){ echo 0; }
rg__marker_field(){ echo ""; }
'''


class LauncherFixture(unittest.TestCase):
    """A real git code root, a real data root, real tools, real source manifest."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        tmp = pathlib.Path(self._tmp.name)
        self.code = tmp / "code-root"
        self.data = tmp / "data-root"
        self.invdir = tmp / "inventories"
        cnd = self.code / "nd-unfolding"
        (cnd / "pet").mkdir(parents=True)
        (self.code / "lib").mkdir(parents=True)
        (self.data / "nd-unfolding").mkdir(parents=True)

        (self.code / "VALIDATION_LEDGER.md").write_text("# fixture ledger\n")
        (self.code / "setup_salloc_env.sh").write_text(
            'echo "[stub] setup_salloc_env sourced from $BASH_SOURCE"\n')
        (self.code / "lib" / "resume_guard.sh").write_text(
            'echo "[stub] resume_guard sourced from $BASH_SOURCE"\nrg_valid_npz(){ return 1; }\n')
        (cnd / "lib_member_resume.sh").write_text(STUB_MR)
        (cnd / f"{SIBLING}.py").write_text("MARK = 'code root sibling'\n")

        # REAL tools, byte-copied. The launchers refuse a symlink here on purpose.
        for src, dst in ((ND / "mnv_guarded_run.py", cnd / "mnv_guarded_run.py"),
                         (ND / "mnv_source_manifest.py", cnd / "mnv_source_manifest.py"),
                         (ND / "pet" / "verify_executing_copy_is_committed.py",
                          cnd / "pet" / "verify_executing_copy_is_committed.py")):
            shutil.copy2(src, dst)

        for launcher, entries, _tags in LAUNCHERS:
            shutil.copy2(ND / launcher, cnd / launcher)
            for e in entries:
                (cnd / e).write_text(STUB_ENTRY)

        dnd = self.data / "nd-unfolding"
        (dnd / "uq_4d").mkdir(parents=True)
        (dnd / "uq_5d").mkdir(parents=True)
        (dnd / "runEventLoopOmniFold_5D_MEFHC_universes_full_bkgaware.root").write_text("stub\n")
        (dnd / "uq_4d" / "vertical_run_bkgaware.txt").write_text("Flux:0\n")
        (dnd / "uq_5d" / "detector_universes.txt").write_text("Flux:0\n")

        env = dict(os.environ, GIT_AUTHOR_NAME="f", GIT_AUTHOR_EMAIL="f@f",
                   GIT_COMMITTER_NAME="f", GIT_COMMITTER_EMAIL="f@f")
        for args in (["init", "-q"], ["add", "-A"], ["commit", "-qm", "fixture"]):
            r = subprocess.run(["git", "-C", str(self.code), *args],
                               capture_output=True, text=True, env=env)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

        self.manifest = tmp / "source-manifest.json"
        r = subprocess.run([sys.executable, str(cnd / "mnv_source_manifest.py"),
                            "--repo", str(self.code), "--write", str(self.manifest),
                            "--require-clean"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

        self.rogue = tmp / "rogue-lib"
        self.rogue.mkdir()
        shutil.copy2(cnd / "lib_member_resume.sh", self.rogue)

        # A-2(g) APPLIED, not asserted. The launchers now pass --require-readonly, so a writable
        # fixture would refuse before reaching anything this file is about. Cleanup undoes it first
        # or the whole suite leaks read-only temp trees.
        self.addCleanup(lambda: self.set_protection(False))
        self.set_protection(True)

    def set_protection(self, on):
        """Apply or undo A-2(g) over the fixture's SOURCE. `.git` is skipped for the same reason the
        real procedure skips it: git must keep writing there, and a protection that breaks the tools
        which verify it protects nothing."""
        for dirpath, dirnames, filenames in os.walk(self.code):
            dirnames[:] = [d for d in dirnames if d != ".git"]
            for name in filenames:
                f = pathlib.Path(dirpath) / name
                m = stat.S_IMODE(os.stat(f).st_mode)
                os.chmod(f, m & ~0o222 if on else m | 0o200)
            if pathlib.Path(dirpath) != self.code:
                m = stat.S_IMODE(os.stat(dirpath).st_mode)
                os.chmod(dirpath, m & ~0o222 if on else m | 0o200)

    def good_env(self, **over):
        env = dict(os.environ, SLURM_ARRAY_TASK_ID="1", SLURM_JOB_NAME="fx", SLURM_JOB_ID="1",
                   PYTHONDONTWRITEBYTECODE="1")
        for k in ("MNV_CODE_ROOT", "MNV_DATA_ROOT", "MNV_LAUNCHER_DIR", "MNV_EST_SEED_OFFSET",
                  "MNV_GUARD_INVENTORY_DIR", "MNV_SOURCE_MANIFEST", "MNV_GUARD_INVENTORY"):
            env.pop(k, None)
        env.update({
            "MNV_CODE_ROOT": str(self.code), "MNV_DATA_ROOT": str(self.data),
            "MNV_LAUNCHER_DIR": str(self.code / "nd-unfolding"),
            "MNV_GUARD_INVENTORY_DIR": str(self.invdir),
            "MNV_SOURCE_MANIFEST": str(self.manifest),
            "MNV_EST_SEED_OFFSET": "0",
        })
        env.update(over)
        return env

    def run_launcher(self, sh, env):
        cp = subprocess.run(["bash", str(self.code / "nd-unfolding" / sh)],
                            capture_output=True, text=True, env=env, cwd=str(self.code))
        return cp

    def inventories(self):
        return sorted(self.invdir.glob("*.jsonl")) if self.invdir.is_dir() else []


class RootsAreMandatory(LauncherFixture):
    def test_no_launcher_still_assigns_the_cluster_root_unconditionally(self):
        for sh, _e, _t in LAUNCHERS:
            with self.subTest(launcher=sh):
                text = (ND / sh).read_text()
                self.assertNotIn(f'REPO="{CLUSTER_ROOT}"', text)
                self.assertNotIn(f"REPO={CLUSTER_ROOT}", text)
                for var in ("MNV_CODE_ROOT", "MNV_DATA_ROOT", "MNV_GUARD_INVENTORY_DIR",
                            "MNV_SOURCE_MANIFEST"):
                    self.assertIn(f"{var}:?", text, f"{sh} must take {var} mandatorily")
                    self.assertNotIn(f"{var}:-", text, "a default is the hardcode wearing a flag")

    def test_each_mandatory_variable_refuses_when_UNSET_and_when_EMPTY(self):
        """`${VAR:?}` and not `${VAR?}`: an exported-but-empty variable is the silent case."""
        for sh, _e, _t in LAUNCHERS:
            for var in ("MNV_CODE_ROOT", "MNV_DATA_ROOT", "MNV_GUARD_INVENTORY_DIR",
                        "MNV_SOURCE_MANIFEST"):
                for mode in ("unset", "empty"):
                    with self.subTest(launcher=sh, var=var, mode=mode):
                        env = self.good_env()
                        if mode == "unset":
                            env.pop(var)
                        else:
                            env[var] = ""
                        cp = self.run_launcher(sh, env)
                        self.assertNotEqual(cp.returncode, 0, cp.stdout + cp.stderr)
                        self.assertIn(var, cp.stderr)

    def test_a_member_library_outside_the_code_root_fails_closed(self):
        for sh, _e, _t in LAUNCHERS:
            with self.subTest(launcher=sh):
                cp = self.run_launcher(sh, self.good_env(MNV_LAUNCHER_DIR=str(self.rogue)))
                self.assertEqual(cp.returncode, 2, cp.stdout + cp.stderr)
                self.assertIn("lib_member_resume.sh resolved to", cp.stderr)


class EveryInvocationIsGuarded(LauncherFixture):
    def test_each_launcher_runs_green_and_emits_one_inventory_per_invocation(self):
        for sh, _e, tags in LAUNCHERS:
            with self.subTest(launcher=sh):
                shutil.rmtree(self.invdir, ignore_errors=True)
                cp = self.run_launcher(sh, self.good_env())
                self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
                self.assertIn("executing-copy parity CURRENT", cp.stdout)
                self.assertIn("SOURCE MANIFEST IDENTICAL", cp.stdout)
                got = {p.name.split(".")[-2] for p in self.inventories()}
                self.assertEqual(got, set(tags), f"{sh}: {sorted(got)}\n{cp.stdout}{cp.stderr}")

    def test_the_inventories_are_NON_VACUOUS_and_all_origins_are_in_the_code_root(self):
        """P-2. A green guarded run that resolved nothing is not evidence about any tree."""
        for sh, _e, tags in LAUNCHERS:
            with self.subTest(launcher=sh):
                shutil.rmtree(self.invdir, ignore_errors=True)
                cp = self.run_launcher(sh, self.good_env())
                self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
                for p in self.inventories():
                    rec = json.loads(p.read_text().strip().splitlines()[0])
                    tag = p.name.split(".")[-2]
                    self.assertGreater(rec["checked"], 0, p.name)
                    self.assertEqual(rec["expect_root"], str(self.code))
                    self.assertEqual(rec["script_checkout_root"], str(self.code))
                    self.assertEqual(rec["allow"], [])
                    for o in rec["repo_origins"]:
                        self.assertEqual(o["checkout_root"], str(self.code))
                    if tag.startswith("adopt_stamped"):
                        continue      # stubbed writer; its own child plumbing is tested elsewhere
                    self.assertGreater(rec["repo_origin_count"], 0, p.name)
                    self.assertIn(SIBLING, [o["fullname"] for o in rec["repo_origins"]])

    def test_a_source_manifest_that_has_MOVED_stops_the_launcher_before_any_python(self):
        """The direction the check acts. Mutate one byte of a tracked source in the code root."""
        self.set_protection(False)
        victim = self.code / "nd-unfolding" / f"{SIBLING}.py"
        victim.write_text("MARK = 'code root sibling'\n# one byte more\n")
        # COMMITTED, so the tree is CLEAN and the only thing that differs is the manifest. Left
        # uncommitted, `--require-clean` fires first and this would be measuring that check
        # instead -- two real refusals, but only one of them is this test's subject.
        env = dict(os.environ, GIT_AUTHOR_NAME="f", GIT_AUTHOR_EMAIL="f@f",
                   GIT_COMMITTER_NAME="f", GIT_COMMITTER_EMAIL="f@f")
        for args in (["add", "-A"], ["commit", "-qm", "one byte"]):
            r = subprocess.run(["git", "-C", str(self.code), *args],
                               capture_output=True, text=True, env=env)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        # RE-PROTECTED before the arms run. Left writable, --require-readonly refuses FIRST and this
        # test would be measuring A-2(g) instead of the manifest comparison -- two real refusals,
        # only one of them this test's subject.
        self.set_protection(True)
        for sh, _e, _t in LAUNCHERS:
            with self.subTest(launcher=sh):
                shutil.rmtree(self.invdir, ignore_errors=True)
                cp = self.run_launcher(sh, self.good_env())
                self.assertNotEqual(cp.returncode, 0, cp.stdout + cp.stderr)
                self.assertIn("SOURCE MANIFEST MOVED", cp.stderr + cp.stdout)
                self.assertEqual(self.inventories(), [],
                                 "it must stop BEFORE any guarded process runs")

    def test_a_missing_guard_in_the_code_root_is_refused_rather_than_skipped(self):
        self.set_protection(False)
        (self.code / "nd-unfolding" / "mnv_guarded_run.py").unlink()
        cp = self.run_launcher(LAUNCHERS[0][0], self.good_env())
        self.assertEqual(cp.returncode, 2, cp.stdout + cp.stderr)
        self.assertIn("required tool missing", cp.stderr)

    def test_a_SYMLINKED_guard_is_refused_because_a_link_can_leave_the_code_root(self):
        self.set_protection(False)
        g = self.code / "nd-unfolding" / "mnv_guarded_run.py"
        real = pathlib.Path(self._tmp.name) / "elsewhere_guard.py"
        shutil.move(str(g), str(real))
        g.symlink_to(real)
        cp = self.run_launcher(LAUNCHERS[0][0], self.good_env())
        self.assertEqual(cp.returncode, 2, cp.stdout + cp.stderr)
        self.assertIn("required tool missing", cp.stderr)

    def test_the_adopt_calls_pass_the_child_guard_operands(self):
        """Item 2's launcher half: the wrapper is told where to guard its child and where to put
        the child's explicitly empty record."""
        text = (ND / "sbatch_finalize_5d_bkgaware_gpu.sh").read_text()
        self.assertEqual(text.count('--guard-expect-root "${CODE_ROOT}"'), 2)
        self.assertIn('--guard-inventory "$(mnv_inv adopt_child_mean)"', text)
        self.assertIn('--guard-inventory "$(mnv_inv adopt_child_cvcentered)"', text)

    def test_the_two_adopt_invocations_are_UNREACHABLE_while_the_pause_branch_stands(self):
        """Recorded as a measurement so nobody reads their absence above as an oversight.

        A declared member (`MNV_EST_SEED_OFFSET` set) enters the pause branch and exits 0 before
        the adopt calls. That is the launcher behaving as ruling 1 describes and ruling 13 defers
        changing -- and it means no end-to-end run of this launcher can exercise the child-guard
        plumbing today.
        """
        shutil.rmtree(self.invdir, ignore_errors=True)
        cp = self.run_launcher("sbatch_finalize_5d_bkgaware_gpu.sh", self.good_env())
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        self.assertIn("MEMBER PAUSE", cp.stderr + cp.stdout)
        tags = {p.name.split(".")[-2] for p in self.inventories()}
        self.assertNotIn("adopt_stamped_mean", tags)
        self.assertNotIn("adopt_child_mean", tags)

    def test_no_allow_FLAG_appears_on_any_command_line_in_any_launcher(self):
        """A TOKEN, not a substring, and not in a comment.

        The first version of this asserted `"--allow" not in text` and went red on
        `sbatch_sweep_bank_5d_run_bkgaware_gpu.sh:11`, a pre-existing COMMENT reading
        "FAIL-CLOSED: no --allow-cv-background". A substring cannot express "appears as an argument
        on an executed line", which is the requirement -- the same defect this package has now hit
        three times, and the reason the bypass-flag check next door parses instead of greps.
        """
        import re
        pat = re.compile(r"(^|\s)--allow(\s|=|$)")
        for sh, _e, _t in LAUNCHERS:
            with self.subTest(launcher=sh):
                offenders = [(i, l) for i, l in enumerate((ND / sh).read_text().splitlines(), 1)
                             if not l.lstrip().startswith("#") and pat.search(l)]
                self.assertEqual(offenders, [], f"{sh}: {offenders}")
                # The power arm: this pattern DOES find an --allow that is really there.
                self.assertTrue(pat.search('python3 x.py --allow /tmp/tree -- y.py'))


class ThePreflightRunsBeforeAnyScience(LauncherFixture):
    """VERIFIED, NOT ARRANGED (Joseph, round 3): *"verify that ordering rather than arranging it --
    if a launcher can reach a science invocation without the preflight having run, that is a
    finding."*

    Three independent instruments, because each alone has a hole:
      * TEXTUAL ORDER -- necessary, and the only one that covers all eight cheaply, but blind to a
        science call hidden in a shell function that could be invoked earlier;
      * NO UNEXPECTED FUNCTION DEFINITIONS -- closes exactly that hole, since a bash script executes
        top to bottom and the only way to run a later line earlier is to have put it in a function;
      * DYNAMIC -- break each preflight precondition in turn and assert ZERO inventories exist,
        which is a statement about what ran rather than about what is written down.
    """

    #: The only shell function any of these launchers may define. `mnv_inv` builds an inventory
    #: path and runs nothing. Anything else could carry a science invocation to an earlier line.
    ALLOWED_FUNCS = {"mnv_inv"}

    @staticmethod
    def _lines(sh):
        return (ND / sh).read_text().splitlines()

    def test_the_preflight_is_textually_BEFORE_every_guarded_science_invocation(self):
        import re
        for sh, _e, _t in LAUNCHERS:
            with self.subTest(launcher=sh):
                lines = self._lines(sh)
                parity_ok = [i for i, l in enumerate(lines, 1)
                             if "executing-copy parity CURRENT" in l and not l.lstrip().startswith("#")]
                science = [i for i, l in enumerate(lines, 1)
                           if re.search(r'python3 "\$GUARD" --expect-root', l)
                           and not l.lstrip().startswith("#")]
                self.assertEqual(len(parity_ok), 1, sh)
                self.assertGreater(len(science), 0, "the power arm: there ARE science invocations "
                                                    "to be ordered against")
                self.assertLess(parity_ok[0], min(science),
                                f"{sh}: a guarded science invocation precedes the preflight")

    def test_no_launcher_defines_a_shell_function_that_could_hoist_a_later_line(self):
        import re
        pat = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*\(\)\s*\{")
        for sh, _e, _t in LAUNCHERS:
            with self.subTest(launcher=sh):
                found = {m.group(1) for m in (pat.match(l) for l in self._lines(sh)) if m}
                self.assertEqual(found, self.ALLOWED_FUNCS, f"{sh} defines {sorted(found)}")

    def test_BOTH_preflight_tools_are_in_the_parity_pair_set_of_every_launcher(self):
        """They are excluded from the GUARD by ruling; they are not excluded from binding."""
        for sh, _e, _t in LAUNCHERS:
            with self.subTest(launcher=sh):
                text = (ND / sh).read_text()
                for rel in ("nd-unfolding/pet/verify_executing_copy_is_committed.py",
                            "nd-unfolding/mnv_source_manifest.py",
                            "nd-unfolding/mnv_guarded_run.py"):
                    self.assertIn(f'={rel}"', text, f"{sh} does not --pair {rel}")

    def test_BOTH_preflight_tools_are_covered_by_the_source_manifest(self):
        man = json.loads(self.manifest.read_text())
        for rel in ("nd-unfolding/pet/verify_executing_copy_is_committed.py",
                    "nd-unfolding/mnv_source_manifest.py",
                    "nd-unfolding/mnv_guarded_run.py"):
            self.assertIn(rel, man["files"], rel)

    def test_EVERY_preflight_refusal_mode_leaves_ZERO_inventories(self):
        """The dynamic half. One launcher, five preconditions broken one at a time; the byte-level
        sameness of the preamble across all eight is what carries this to the other seven, and that
        is asserted separately below."""
        sh = LAUNCHERS[0][0]

        def arm(name, mutate, restore):
            shutil.rmtree(self.invdir, ignore_errors=True)
            mutate()
            cp = self.run_launcher(sh, self.good_env())
            restore()
            self.assertNotEqual(cp.returncode, 0, f"{name}: {cp.stdout}{cp.stderr}")
            self.assertEqual(self.inventories(), [],
                             f"{name}: a guarded process ran despite the preflight refusing")

        arm("A-2(g) writable", lambda: self.set_protection(False),
            lambda: self.set_protection(True))

        def nest():
            self.set_protection(False)
            n = self.code / "nested-checkout"
            (n / "nd-unfolding").mkdir(parents=True)
            (n / "VALIDATION_LEDGER.md").write_text("x\n")
        def unnest():
            shutil.rmtree(self.code / "nested-checkout", ignore_errors=True)
            self.set_protection(True)
        arm("A-2(d) nested checkout", nest, unnest)

        def unmark():
            self.set_protection(False)
            (self.code / "VALIDATION_LEDGER.md").rename(self.code / "LEDGER.bak")
        def remark():
            (self.code / "LEDGER.bak").rename(self.code / "VALIDATION_LEDGER.md")
            self.set_protection(True)
        arm("A-2(c) not a checkout", unmark, remark)

        # MY FIRST MUTATION HERE WAS INERT AND THE ARM PASSED VACUOUSLY: renaming `file_count` in
        # the recorded manifest changes nothing `compare()` reads, so the launcher correctly ran on.
        # Recorded rather than quietly replaced -- a control that does not perturb the thing under
        # test is the defect this whole package keeps finding in other people's fixtures.
        saved = self.manifest.read_text()
        arm("A-2(f) manifest is not valid JSON",
            lambda: self.manifest.write_text(saved[: len(saved) // 2]),
            lambda: self.manifest.write_text(saved))
        arm("A-2(f) manifest is a foreign schema",
            lambda: self.manifest.write_text(saved.replace("mnv_source_manifest/1", "other/9")),
            lambda: self.manifest.write_text(saved))
        arm("A-2(f) manifest describes a DIFFERENT tree",
            lambda: self.manifest.write_text(
                json.dumps({**json.loads(saved),
                            "files": {"nd-unfolding/ghost.py": "0" * 64}})),
            lambda: self.manifest.write_text(saved))

        env_missing = self.good_env()
        env_missing.pop("MNV_SOURCE_MANIFEST")
        shutil.rmtree(self.invdir, ignore_errors=True)
        cp = self.run_launcher(sh, env_missing)
        self.assertNotEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        self.assertEqual(self.inventories(), [])

    def test_the_preflight_block_is_BYTE_IDENTICAL_across_all_eight_except_its_pair_list(self):
        """What carries the dynamic arm above from one launcher to the other seven. The `--pair`
        lines legitimately differ -- each launcher binds the entrypoints it runs -- so they are
        excluded by name and everything else must match exactly."""
        import hashlib
        digests = {}
        for sh, _e, _t in LAUNCHERS:
            lines = self._lines(sh)
            a = next(i for i, l in enumerate(lines) if l.startswith("# --- OI-136 ROUND 2"))
            b = next(i for i, l in enumerate(lines) if "executing-copy parity CURRENT" in l)
            block = [l for l in lines[a:b + 1] if "--pair" not in l]
            digests[sh] = hashlib.sha256("\n".join(block).encode()).hexdigest()
        self.assertEqual(len(set(digests.values())), 1, f"the preambles have diverged: {digests}")


class TheP4RatchetReadsWhatTheRunProduced(LauncherFixture):
    def test_pins_are_written_from_a_real_run_and_then_hold_identically(self):
        for sh, _e, _t in LAUNCHERS:
            cp = self.run_launcher(sh, self.good_env())
            self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        pins = pathlib.Path(self._tmp.name) / "pins.json"
        ratchet = [sys.executable, str(ND / "mnv_import_set_ratchet.py"),
                   "--inventory-dir", str(self.invdir), "--pins", str(pins),
                   "--source-manifest", str(self.manifest)]
        w = subprocess.run(ratchet + ["--write-pins", "--declare-empty",
                                      "nd-unfolding/mii_adopt_unified_5d_stamped.py",
                                      "--empty-disclosure", "fixture stub, not the real writer"],
                           capture_output=True, text=True)
        self.assertEqual(w.returncode, 0, w.stdout + w.stderr)
        c = subprocess.run(ratchet, capture_output=True, text=True)
        self.assertEqual(c.returncode, 0, c.stdout + c.stderr)
        self.assertIn("P-2, P-3 and P-4 HOLD", c.stdout)

        # IDENTITY, NOT A FLOOR: a set that SHRANK is as much a finding as one that grew.
        data = json.loads(pins.read_text())
        key = "nd-unfolding/bootstrap_nd.py"
        self.assertIn(key, data["entrypoints"])
        data["entrypoints"][key]["modules"] = sorted(
            set(data["entrypoints"][key]["modules"]) | {"a_module_that_never_loaded"})
        pins.write_text(json.dumps(data))
        grew = subprocess.run(ratchet, capture_output=True, text=True)
        self.assertEqual(grew.returncode, 3, grew.stdout + grew.stderr)
        self.assertIn("import set MOVED", grew.stderr)
        self.assertIn("missing=['a_module_that_never_loaded']", grew.stderr)

    def test_an_EMPTY_inventory_directory_is_CANNOT_CHECK_not_a_pass(self):
        empty = pathlib.Path(self._tmp.name) / "no-records"
        empty.mkdir()
        pins = pathlib.Path(self._tmp.name) / "p.json"
        pins.write_text(json.dumps({"schema": "mnv_import_set_pins/1", "entrypoints": {}}))
        r = subprocess.run([sys.executable, str(ND / "mnv_import_set_ratchet.py"),
                            "--inventory-dir", str(empty), "--pins", str(pins)],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("zero inventory records", r.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
