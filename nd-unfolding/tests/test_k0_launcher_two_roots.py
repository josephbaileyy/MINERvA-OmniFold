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
        (self.code / "lib" / "resume_guard.sh").write_text(
            'echo "[stub] resume_guard sourced from $BASH_SOURCE"\nrg_valid_npz(){ return 1; }\n')

        # ---- A REAL ACTIVATOR CLOSURE, IN ITS OWN ROOT ------------------------------------------
        # THIS IS THE ROUND-4 FINDING'S ACTUAL FIX. The previous fixture wrote a ONE-LINE
        # `setup_salloc_env.sh` into the code root that sourced nothing -- it replaced the single
        # file whose real content is the blocker, so twenty-nine green arms were silent about an
        # environment closure that does not exist in any A-2-satisfying tree. A fixture must agree
        # with the world, not with the code under test.
        #
        # So the fixture now builds a MULTI-HOP closure outside the code root: an activator that
        # sources two files, one of which sources three more, plus a conda-shaped `activate.d`
        # directory that activation globs. The transitivity is real, which is the only reason the
        # arms below can fail for the reason they claim.
        self.env = tmp / "env-root"
        (self.env / "unbinned_unfolding" / "build").mkdir(parents=True)
        (self.env / "MINERvA101" / "opt" / "bin").mkdir(parents=True)
        # THE ACTIVATOR LEAVES AN OBSERVABLE MARK. Without one, "the tools ran before activation"
        # is only assertable textually -- and a textual arm is exactly what let round 5 ship a
        # launcher whose Python preflight tools ran on the un-activated 3.6.15 interpreter. The
        # marker plus the python3 shim below make the ordering settleable BY RUNNING.
        (self.env / "activation-marker").write_text("")
        (self.env / "setup_salloc_env.sh").write_text(
            'SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"\n'
            'source "${SCRIPT_DIR}/unbinned_unfolding/build/setup.sh"\n'
            'export MINERVA_PREFIX="${SCRIPT_DIR}/MINERvA101/opt"\n'
            'source "${SCRIPT_DIR}/MINERvA101/opt/bin/setup.sh"\n'
            'export MNV_TEST_ACTIVATED=1\n')
        (self.env / "unbinned_unfolding" / "build" / "setup.sh").write_text(
            '_D="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"\n'
            'export PATH=${_D}:${PATH}\nexport PYTHONPATH=${_D}:${PYTHONPATH}\n'
            'export LD_LIBRARY_PATH=${_D}:${LD_LIBRARY_PATH}\nunset _D\n')
        (self.env / "MINERvA101" / "opt" / "bin" / "setup.sh").write_text(
            'INSTALL_DIR=${MINERVA_PREFIX:?set MINERVA_PREFIX}\n'
            'source ${INSTALL_DIR}/bin/setup_MAT.sh\n'
            'source ${INSTALL_DIR}/bin/setup_MAT-MINERvA.sh\n'
            'source ${INSTALL_DIR}/bin/setup_UnfoldUtils.sh\n')
        for leaf in ("setup_MAT.sh", "setup_MAT-MINERvA.sh", "setup_UnfoldUtils.sh"):
            (self.env / "MINERvA101" / "opt" / "bin" / leaf).write_text(
                'PREFIX=${MINERVA_PREFIX:?set MINERVA_PREFIX}\nexport PATH=${PREFIX}/bin:$PATH\n')
        # A shared `bin/` legitimately holds scripts the closure never sources; the EXTRA check must
        # not fire on them. This one exists so that arm is exercised rather than assumed.
        (self.env / "MINERvA101" / "opt" / "bin" / "unrelated_tool.sh").write_text("echo unrelated\n")

        self.conda = tmp / "conda-prefix"
        (self.conda / "etc" / "conda" / "activate.d").mkdir(parents=True)
        for n in ("activate-root.sh", "libglib_activate.sh"):
            (self.conda / "etc" / "conda" / "activate.d" / n).write_text(f"# {n}\n")

        self.envmanifest = tmp / "env-manifest.tsv"
        r = subprocess.run([sys.executable, str(ND / "mnv_env_manifest.py"),
                            "--env-root", str(self.env), "--conda-prefix", str(self.conda),
                            "--write-tsv", str(self.envmanifest)],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        (cnd / "lib_member_resume.sh").write_text(STUB_MR)
        (cnd / f"{SIBLING}.py").write_text("MARK = 'code root sibling'\n")

        # REAL tools, byte-copied. The launchers refuse a symlink here on purpose.
        for src, dst in ((ND / "mnv_guarded_run.py", cnd / "mnv_guarded_run.py"),
                         (ND / "mnv_source_manifest.py", cnd / "mnv_source_manifest.py"),
                         (ND / "lib_mnv_env_preflight.sh", cnd / "lib_mnv_env_preflight.sh"),
                         (ND / "lib_mnv_env_pathcheck.sh", cnd / "lib_mnv_env_pathcheck.sh"),
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

    @staticmethod
    def _ambient_prefixes():
        """Every directory this host already has on the three search paths, resolved."""
        out = []
        for var in ("PATH", "PYTHONPATH", "LD_LIBRARY_PATH"):
            for e in os.environ.get(var, "").split(":"):
                if not e:
                    continue
                try:
                    r = os.path.realpath(e)
                except OSError:
                    continue
                if r not in out:
                    out.append(r)
        out.append(os.path.realpath(tempfile.gettempdir()))
        return " ".join(out)

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
            # The three roots, all mandatory and none defaulted.
            "MNV_ENV_ROOT": str(self.env),
            "MNV_CONDA_PREFIX": str(self.conda),
            "MNV_ENV_MANIFEST": str(self.envmanifest),
            # DERIVED FROM THIS HOST, not hardcoded, and predeclared exactly the way a real
            # submitter predeclares theirs -- there is no special case for being a test. A fixed
            # list would pass on the author's laptop and refuse a correct configuration everywhere
            # else, which is the fixture-disagrees-with-the-world failure this whole round is about.
            # NOTE the contamination arm does NOT depend on this: the checkout check is absolute and
            # runs before the allowlist, so widening this cannot make a checkout path acceptable.
            "MNV_ENV_SYSTEM_PREFIXES": self._ambient_prefixes(),
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


class NoPythonRunsBeforeTheActivator(LauncherFixture):
    """ROUND-6: the ordering that round 5 got wrong in exactly one launcher, settled BY RUNNING.

    `sbatch_unfold_5d_detector_bkgaware_gpu.sh` invoked both Python preflight tools at :139/:148 and
    sourced its activator at :227 -- because that was where the activator already sat before the
    repair. Both tools open with `from __future__ import annotations`, so on the un-activated
    interpreter (`/usr/bin/python3` == 3.6.15 on saul) they die with a SyntaxError before any guard
    or science, and the launcher then reports "the execution tree is not the tree that was approved",
    MISATTRIBUTING the cause. The other seven were correct by accident of layout, not by design.

    IT SURVIVED 34 GREEN ARMS because `good_env()` inherits the runner's PATH, so the fixture handed
    the launcher the very interpreter the activator exists to supply. A fixture that supplies what
    the thing under test is supposed to supply cannot see the thing under test fail.
    """

    def test_TEXTUAL_the_activator_precedes_EVERY_python3_invocation(self):
        import re
        for sh, _e, _t in LAUNCHERS:
            with self.subTest(launcher=sh):
                lines = (ND / sh).read_text().splitlines()
                act = [i for i, l in enumerate(lines, 1)
                       if 'source "${ENV_ROOT}/setup_salloc_env.sh"' in l]
                py = [i for i, l in enumerate(lines, 1)
                      if re.search(r'(^|[^#\w])python3 ', l) and not l.lstrip().startswith("#")]
                self.assertEqual(len(act), 1, f"{sh}: expected exactly one activator source")
                self.assertGreater(len(py), 0, "power arm: there ARE python3 invocations to order")
                self.assertLess(act[0], min(py),
                                f"{sh}: python3 runs at line {min(py)}, before the activator at "
                                f"{act[0]} -- on the un-activated interpreter that is a SyntaxError")

    def test_DYNAMIC_a_python3_that_refuses_before_activation_still_lets_every_launcher_run(self):
        """The discriminator. A `python3` shim earlier on PATH than the real one exits 42 unless the
        activator has already run. If any launcher invoked Python first, it would die 42."""
        shim = pathlib.Path(self._tmp.name) / "shimbin"
        shim.mkdir()
        (shim / "python3").write_text(
            "#!/bin/bash\n"
            'if [[ -z "${MNV_TEST_ACTIVATED}" ]]; then\n'
            '  echo "[shim] python3 invoked BEFORE the activator" >&2; exit 42\n'
            "fi\n"
            'exec %s "$@"\n' % sys.executable)
        (shim / "python3").chmod(0o755)
        for sh, _e, _t in LAUNCHERS:
            with self.subTest(launcher=sh):
                env = self.good_env()
                env["PATH"] = f"{shim}:{env['PATH']}"
                cp = self.run_launcher(sh, env)
                self.assertNotEqual(cp.returncode, 42,
                                    f"{sh}: a Python tool ran before the activator\n{cp.stderr}")
                self.assertNotIn("invoked BEFORE the activator", cp.stderr)

    def test_the_DYNAMIC_arm_can_FAIL_negative_control(self):
        """A detector that cannot fire is not a detector. Re-point the marker so the shim refuses,
        and assert the arm above would have caught it."""
        shim = pathlib.Path(self._tmp.name) / "shimbin2"
        shim.mkdir()
        (shim / "python3").write_text(
            "#!/bin/bash\n"
            'echo "[shim] python3 invoked BEFORE the activator" >&2; exit 42\n')
        (shim / "python3").chmod(0o755)
        env = self.good_env()
        env["PATH"] = f"{shim}:{env['PATH']}"
        cp = self.run_launcher(LAUNCHERS[0][0], env)
        self.assertNotEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        self.assertIn("invoked BEFORE the activator", cp.stderr)

    def test_an_UNUSABLE_interpreter_is_reported_as_ITSELF_not_as_a_wrong_tree(self):
        """The misattribution the round-5 grader found, pinned. An interpreter that cannot run the
        preflight tools used to surface as '[oi136] FAIL: the execution tree is not the tree that
        was approved' -- a wrong diagnosis of a right refusal, which is worse than the refusal."""
        shim = pathlib.Path(self._tmp.name) / "oldpy"
        shim.mkdir()
        (shim / "python3").write_text('#!/bin/bash\nexit 9\n')
        (shim / "python3").chmod(0o755)
        env = self.good_env()
        env["PATH"] = f"{shim}:{env['PATH']}"
        cp = self.run_launcher(LAUNCHERS[0][0], env)
        self.assertEqual(cp.returncode, 3, cp.stdout + cp.stderr)
        self.assertIn("cannot run the preflight tools", cp.stderr)
        self.assertIn("ENVIRONMENT fault, not a wrong-tree fault", cp.stderr)
        self.assertNotIn("is not the tree that was approved", cp.stderr)


class TheENVIRONMENTIsItsOwnRootAndIsVerifiedBEFOREItIsSourced(LauncherFixture):
    """Round-5 repair of `F-2(a)`, authorized by Joseph 2026-08-23 after the round-4 verdict.

    WHAT ROUND 4 FOUND, and why the round-4 arms this class replaces were not enough: they proved a
    git parity gate fired on `setup_salloc_env.sh`, in a fixture that wrote a ONE-LINE activator
    sourcing nothing. The real activator sources files that are ABSENT from any A-2-satisfying tree
    (`.gitignore` excludes `unbinned_unfolding/**` and `MINERvA101/**`), so every launcher died at
    the activator with exit 1 and the gate was the last thing that happened. **A fixture must agree
    with the world, not with the code under test** -- so `LauncherFixture` now builds a REAL
    multi-hop closure in its own root, and these arms mutate it.

    THE POSITIVE CONTROL IS LISTED FIRST because the negatives are worthless without it: a valid
    three-root configuration must actually RUN.
    """

    def tamper_env(self, rel, text):
        (self.env / rel).write_text(text)

    # ---- POSITIVE CONTROLS -------------------------------------------------------------------
    def test_POSITIVE_a_valid_three_root_configuration_RUNS(self):
        for sh, _e, _t in LAUNCHERS:
            with self.subTest(launcher=sh):
                cp = self.run_launcher(sh, self.good_env())
                self.assertNotIn("[env-preflight] VIOLATION", cp.stderr)
                self.assertNotIn("[env-pathcheck] VIOLATION", cp.stderr)
                self.assertIn("[env-preflight] OK:", cp.stdout)

    def test_POSITIVE_the_complete_closure_passes_and_execution_REACHES_the_next_line(self):
        """The exact statement round 4 could not make: the activator is sourced and the line after
        it runs. `[env-pathcheck] OK` is only printed AFTER the source returns."""
        cp = self.run_launcher(LAUNCHERS[0][0], self.good_env())
        self.assertIn("[env-pathcheck] OK:", cp.stdout, cp.stdout + cp.stderr)

    def test_POSITIVE_an_unrelated_script_in_a_shared_bin_is_NOT_an_extra(self):
        """`MINERvA101/opt/bin` legitimately holds scripts the closure never sources. The first
        draft of the EXTRA check refused a correct environment over four of them."""
        self.assertTrue((self.env / "MINERvA101" / "opt" / "bin" / "unrelated_tool.sh").is_file())
        cp = self.run_launcher(LAUNCHERS[0][0], self.good_env())
        self.assertNotIn("EXTRA unbound", cp.stderr)

    # ---- THE CLOSURE ---------------------------------------------------------------------------
    def test_an_ABSENT_closure_member_fails_BEFORE_the_source(self):
        (self.env / "MINERvA101" / "opt" / "bin" / "setup_MAT.sh").unlink()
        for sh, _e, _t in LAUNCHERS:
            with self.subTest(launcher=sh):
                cp = self.run_launcher(sh, self.good_env())
                self.assertEqual(cp.returncode, 3, cp.stdout + cp.stderr)
                self.assertIn("MISSING closure member", cp.stderr)
                self.assertNotIn("[env-pathcheck]", cp.stdout)   # never reached the source

    def test_a_DIGEST_that_MOVED_fails_before_the_source(self):
        self.tamper_env("unbinned_unfolding/build/setup.sh", "echo tampered\n")
        cp = self.run_launcher(LAUNCHERS[0][0], self.good_env())
        self.assertEqual(cp.returncode, 3, cp.stdout + cp.stderr)
        self.assertIn("DIGEST MISMATCH", cp.stderr)
        self.assertNotIn("[env-pathcheck]", cp.stdout)

    def test_a_HOP_TWO_digest_move_is_caught_not_only_hop_one(self):
        """Binding the first hop was the round-4 half-fix. The closure is bound to its depth."""
        self.tamper_env("MINERvA101/opt/bin/setup_UnfoldUtils.sh", "echo tampered\n")
        cp = self.run_launcher(LAUNCHERS[0][0], self.good_env())
        self.assertEqual(cp.returncode, 3, cp.stdout + cp.stderr)
        self.assertIn("setup_UnfoldUtils.sh", cp.stderr)

    def test_an_EXTRA_activate_d_script_is_refused_because_conda_GLOBS_that_directory(self):
        (self.conda / "etc" / "conda" / "activate.d" / "zz_injected.sh").write_text("echo hi\n")
        cp = self.run_launcher(LAUNCHERS[0][0], self.good_env())
        self.assertEqual(cp.returncode, 3, cp.stdout + cp.stderr)
        self.assertIn("EXTRA unbound activate.d script", cp.stderr)

    # ---- THE ROOT ITSELF -----------------------------------------------------------------------
    def test_MNV_ENV_ROOT_is_MANDATORY_with_no_default(self):
        for sh, _e, _t in LAUNCHERS:
            for mode in ("unset", "empty"):
                with self.subTest(launcher=sh, mode=mode):
                    env = self.good_env()
                    if mode == "unset":
                        env.pop("MNV_ENV_ROOT")
                    else:
                        env["MNV_ENV_ROOT"] = ""
                    cp = self.run_launcher(sh, env)
                    self.assertNotEqual(cp.returncode, 0)
                    self.assertIn("MNV_ENV_ROOT", cp.stderr)

    def test_MNV_CONDA_PREFIX_is_MANDATORY_with_no_default(self):
        env = self.good_env(); env.pop("MNV_CONDA_PREFIX")
        cp = self.run_launcher(LAUNCHERS[0][0], env)
        self.assertNotEqual(cp.returncode, 0)
        self.assertIn("MNV_CONDA_PREFIX", cp.stderr)

    def test_an_env_root_INSIDE_the_code_root_is_refused(self):
        """A view onto a checkout resolves back into it; the separation is checked on the CANONICAL
        target, which is also why a directory symlink is permitted and a checkout is not."""
        env = self.good_env(MNV_ENV_ROOT=str(self.code))
        cp = self.run_launcher(LAUNCHERS[0][0], env)
        self.assertEqual(cp.returncode, 3, cp.stdout + cp.stderr)
        self.assertIn("inside a repository checkout", cp.stderr)

    def test_a_DIRECTORY_symlink_to_a_clean_target_is_ALLOWED(self):
        """Measured on saul: a FILE symlink breaks SCRIPT_DIR and a DIRECTORY symlink does not."""
        link = self.env.parent / "env-link"
        link.symlink_to(self.env, target_is_directory=True)
        cp = self.run_launcher(LAUNCHERS[0][0], self.good_env(MNV_ENV_ROOT=str(link)))
        self.assertNotIn("[env-preflight] VIOLATION", cp.stderr)
        self.assertIn("[env-preflight] OK:", cp.stdout)

    # ---- THE PATH CHANNELS ---------------------------------------------------------------------
    def test_canonical_checkout_contamination_is_refused_on_ALL_THREE_channels(self):
        """The guard sees only `sys.path`; PATH and LD_LIBRARY_PATH are invisible to it. This is
        the channel the round-4 verdict found the hop-1 activator poisoning BY CONTENT."""
        for var in ("PATH", "PYTHONPATH", "LD_LIBRARY_PATH"):
            with self.subTest(channel=var):
                self.tamper_env(
                    "unbinned_unfolding/build/setup.sh",
                    f'export {var}="{self.code}/nd-unfolding:${{{var}}}"\n')
                # re-bind the manifest so the DIGEST arm cannot be what fires here
                r = subprocess.run([sys.executable, str(ND / "mnv_env_manifest.py"),
                                    "--env-root", str(self.env), "--conda-prefix", str(self.conda),
                                    "--write-tsv", str(self.envmanifest)],
                                   capture_output=True, text=True)
                self.assertEqual(r.returncode, 0, r.stderr)
                cp = self.run_launcher(LAUNCHERS[0][0], self.good_env())
                self.assertEqual(cp.returncode, 3, cp.stdout + cp.stderr)
                self.assertIn("REPOSITORY CHECKOUT path", cp.stderr)

    # ---- THE MEMBER LIBRARY ----------------------------------------------------------------------
    def test_a_WRONG_TREE_member_library_fails_BEFORE_it_is_sourced(self):
        """Round 4: the containment check ran AFTER the source in all eight. It now precedes it."""
        for sh, _e, _t in LAUNCHERS:
            with self.subTest(launcher=sh):
                lines = (ND / sh).read_text().split("\n")
                chk = next(i for i, l in enumerate(lines) if "lib_member_resume.sh resolved to" in l)
                src = next(i for i, l in enumerate(lines)
                           if l.startswith('source "${_mr_lib}/lib_member_resume.sh"'))
                self.assertLess(chk, src, f"{sh}: containment still runs after the source")

    def test_the_member_library_containment_FIRES_from_a_rogue_tree(self):
        cp = self.run_launcher(LAUNCHERS[0][0], self.good_env(MNV_LAUNCHER_DIR=str(self.rogue)))
        self.assertNotEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        self.assertIn("lib_member_resume.sh", cp.stderr)

    # ---- THE DISCLOSURE IS GONE BECAUSE THE DEFECT IS ---------------------------------------------
    def test_no_launcher_still_sources_the_activator_from_the_CODE_ROOT(self):
        for sh, _e, _t in LAUNCHERS:
            with self.subTest(launcher=sh):
                t = (ND / sh).read_text()
                self.assertNotIn('source "${CODE_ROOT}/setup_salloc_env.sh"', t)
                self.assertIn('source "${ENV_ROOT}/setup_salloc_env.sh"', t)


# =================================================================================================
# ROUND-7 / F-2(a): PRE-USE GIT PARITY FOR EVERY TRACKED FILE THE PREAMBLE SOURCES
#
# Joseph's ruling 2026-08-23 (DECISION-20260823-joseph-a2f-does-not-substitute-for-a3.md):
# A-2(f) DOES NOT SUBSTITUTE FOR A-3 EXECUTING-FILE PARITY. Round 6 sourced two TRACKED libraries
# from the code root with no gate of their own, 77-193 lines before the source-manifest comparison
# that was supposed to cover them -- while the pure-git gate sat 17 lines above, naming only
# lib/resume_guard.sh.
#
# FOUR ARM DIRECTIONS, because a guard needs a test that it FIRES and a narrowing needs a test that
# it does NOT, and neither says anything about ORDER:
#   (1) SILENT ON GOOD      -- clean tree, no parity complaint, launcher proceeds
#   (2) FIRES ON BAD        -- each of the three mutated, refused by name, exit 3
#   (3) OPPOSITE DIRECTION  -- a file that cannot be hashed refuses too ("could not run" != "passed"),
#                              and a tracked file the preamble does NOT source is left alone
#   (4) BEFORE, NOT AFTER   -- dynamic: the mutation IS the marker, so marker absence proves the
#                              refusal beat the source. Round 5 shipped an ordering defect through
#                              34 green arms because every arm was textual.
# =================================================================================================
PARITY_LIBS = ("lib/resume_guard.sh",
               "nd-unfolding/lib_mnv_env_preflight.sh",
               "nd-unfolding/lib_mnv_env_pathcheck.sh")


class EveryTrackedSourcedFileIsGitBoundBEFOREAnyOfThemIsSourced(LauncherFixture):

    def _rewrite(self, rel, text):
        """Rewrite a protected tracked file in the code root, restoring protection after."""
        self.set_protection(False)
        (self.code / rel).write_text(text)
        self.set_protection(True)

    def _append(self, rel, extra):
        self.set_protection(False)
        p = self.code / rel
        p.write_text(p.read_text() + extra)
        self.set_protection(True)

    def _remove(self, rel):
        self.set_protection(False)
        (self.code / rel).unlink()
        self.set_protection(True)

    # ---- (1) SILENT ON GOOD ---------------------------------------------------------------------
    def test_the_parity_gate_is_SILENT_when_all_three_match_HEAD(self):
        """The arm that a guard-only test set cannot supply. If this ever fails, the gate refuses a
        correct tree -- a wrong refusal, which is worse than the defect it was added for."""
        for sh, _e, _t in LAUNCHERS:
            with self.subTest(launcher=sh):
                cp = self.run_launcher(sh, self.good_env())
                self.assertNotIn("cannot compute git parity", cp.stderr)
                self.assertNotIn("differs from HEAD", cp.stderr)
                self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)

    # ---- (2) FIRES ON BAD -----------------------------------------------------------------------
    def test_a_mutation_to_ANY_of_the_three_is_REFUSED_by_name(self):
        for rel in PARITY_LIBS:
            for sh, _e, _t in LAUNCHERS:
                with self.subTest(library=rel, launcher=sh):
                    self._append(rel, "\n# tampered\n")
                    try:
                        cp = self.run_launcher(sh, self.good_env())
                        self.assertEqual(cp.returncode, 3, cp.stdout + cp.stderr)
                        self.assertIn(rel, cp.stderr)
                        self.assertIn("differs from HEAD", cp.stderr)
                    finally:
                        self.set_protection(False)
                        subprocess.run(["git", "-C", str(self.code), "checkout", "--", rel],
                                       capture_output=True, text=True)
                        self.set_protection(True)

    # ---- (3) OPPOSITE DIRECTION -----------------------------------------------------------------
    def test_a_library_that_cannot_be_HASHED_is_refused_not_waved_through(self):
        """`hash-object` on a missing file yields the empty string. A one-directional check that
        only compares two values would treat empty == empty as agreement and pass."""
        for rel in PARITY_LIBS:
            with self.subTest(library=rel):
                self._remove(rel)
                try:
                    cp = self.run_launcher(LAUNCHERS[0][0], self.good_env())
                    self.assertEqual(cp.returncode, 3, cp.stdout + cp.stderr)
                    self.assertIn(rel, cp.stderr)
                    self.assertIn("could not run is not a check that passed", cp.stderr)
                finally:
                    self.set_protection(False)
                    subprocess.run(["git", "-C", str(self.code), "checkout", "--", rel],
                                   capture_output=True, text=True)
                    self.set_protection(True)

    def test_the_gate_does_NOT_fire_on_a_tracked_file_the_preamble_never_sources(self):
        """The narrowing arm. A blanket 'is the tree clean' check would pass every arm above and be
        a different, wrong gate -- A-2(g)'s job, not this one's."""
        self._append("VALIDATION_LEDGER.md", "\nnot a sourced file\n")
        cp = self.run_launcher(LAUNCHERS[0][0], self.good_env())
        # THE PARITY GATE IS SILENT. It is scoped to the three files the preamble sources, and a
        # dirty ledger is none of them.
        self.assertNotIn("differs from HEAD", cp.stderr)
        self.assertNotIn("cannot compute git parity", cp.stderr)
        # AND THE TREE IS STILL REFUSED -- by the LATER source-manifest gate, which is the one whose
        # job whole-tree cleanliness is. Asserting only silence would leave "the parity gate got
        # narrower and nothing else covers this" indistinguishable from a correct narrowing, so the
        # arm names the gate that DOES cover it.
        self.assertEqual(cp.returncode, 3, cp.stdout + cp.stderr)
        self.assertIn("[srcman] REFUSING", cp.stderr)
        # ...and it got there THROUGH a clean parity gate and a sourced resume_guard, which is the
        # positive half of this arm: the preamble ran to completion and the later gate caught it.
        self.assertIn("[env-preflight] OK", cp.stdout + cp.stderr)
        self.assertIn("VALIDATION_LEDGER.md", cp.stderr)

    # ---- (4) BEFORE, NOT AFTER ------------------------------------------------------------------
    def test_the_refusal_happens_BEFORE_the_library_is_sourced__dynamically(self):
        """THE MUTATION IS THE MARKER. Appending a line that writes a file both (a) changes the blob
        so the gate must refuse and (b) leaves physical evidence if the library was sourced anyway.
        An exit code alone cannot distinguish 'refused before' from 'sourced, then refused'."""
        for rel in PARITY_LIBS:
            with self.subTest(library=rel):
                marker = self.data / f"SOURCED-{rel.replace('/', '_')}"
                self.assertFalse(marker.exists())
                self._append(rel, f'\n: > "{marker}"\n')
                try:
                    cp = self.run_launcher(LAUNCHERS[0][0], self.good_env())
                    self.assertEqual(cp.returncode, 3, cp.stdout + cp.stderr)
                    self.assertFalse(marker.exists(),
                                     f"{rel} WAS SOURCED before/despite the parity refusal")
                finally:
                    self.set_protection(False)
                    subprocess.run(["git", "-C", str(self.code), "checkout", "--", rel],
                                   capture_output=True, text=True)
                    self.set_protection(True)
                    if marker.exists():
                        marker.unlink()

    def test_the_NEGATIVE_CONTROL_marker_DOES_appear_when_the_library_is_allowed_to_run(self):
        """Proves the marker mechanism can fire at all. Without this, every assertFalse above would
        also pass if the append silently never happened -- a fixture that cannot detect the thing it
        is asserting the absence of."""
        marker = self.data / "SOURCED-negative-control"
        self._append("nd-unfolding/lib_mnv_env_preflight.sh", f'\n: > "{marker}"\n')
        self.set_protection(False)
        subprocess.run(["git", "-C", str(self.code), "add", "-A"], capture_output=True, text=True)
        subprocess.run(["git", "-C", str(self.code), "-c", "user.name=f", "-c", "user.email=f@f",
                        "commit", "-qm", "accept the marker into HEAD"],
                       capture_output=True, text=True)
        self.set_protection(True)
        cp = self.run_launcher(LAUNCHERS[0][0], self.good_env())
        self.assertNotIn("differs from HEAD", cp.stderr)
        self.assertTrue(marker.exists(),
                        "the marker never appears even when parity HOLDS -- the arms above prove "
                        f"nothing. stdout+stderr: {cp.stdout + cp.stderr}")

    # ---- STRUCTURE: the loop is inline, identical, and ahead of every source --------------------
    def test_the_gate_covers_EXACTLY_the_three_and_names_them(self):
        for sh, _e, _t in LAUNCHERS:
            with self.subTest(launcher=sh):
                t = (ND / sh).read_text()
                for rel in PARITY_LIBS:
                    self.assertIn(rel, t.split("done\nunset _mnv_rel")[0])

    def test_the_parity_block_is_BYTE_IDENTICAL_in_all_eight(self):
        blocks = set()
        for sh, _e, _t in LAUNCHERS:
            t = (ND / sh).read_text()
            s = t.index("# (1) EVERY TRACKED FILE")
            e = t.index("unset _mnv_rel _mnv_head _mnv_work")
            blocks.add(t[s:e])
        self.assertEqual(len(blocks), 1, f"{len(blocks)} distinct parity blocks across eight launchers")

    def test_no_launcher_sources_ANY_of_the_three_before_the_parity_loop(self):
        for sh, _e, _t in LAUNCHERS:
            with self.subTest(launcher=sh):
                lines = (ND / sh).read_text().splitlines()
                gate = next(i for i, l in enumerate(lines) if l.startswith("for _mnv_rel in "))
                done = next(i for i, l in enumerate(lines)
                            if l.startswith("unset _mnv_rel _mnv_head _mnv_work"))
                for rel in PARITY_LIBS:
                    for i, l in enumerate(lines):
                        if l.strip().startswith("source ") and rel in l:
                            self.assertGreater(i, done,
                                               f"{sh}: {rel} sourced at :{i+1}, gate ends :{done+1}")
                self.assertLess(gate, done)

    def test_the_parity_check_is_INLINE_and_not_delegated_to_a_sourced_helper(self):
        """A helper doing this check would itself execute unbound -- F-2(a) one level down."""
        for sh, _e, _t in LAUNCHERS:
            with self.subTest(launcher=sh):
                lines = (ND / sh).read_text().splitlines()
                gate = next(i for i, l in enumerate(lines) if l.startswith("for _mnv_rel in "))
                head = [l for l in lines[:gate] if l.strip().startswith(("source ", ". "))]
                self.assertEqual(head, [], f"{sh}: sources something before the parity gate: {head}")
