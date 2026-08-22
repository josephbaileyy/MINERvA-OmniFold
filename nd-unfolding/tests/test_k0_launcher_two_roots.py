#!/usr/bin/env python3
"""The eight k=0 launchers take TWO MANDATORY ROOTS and select neither by default.

Joseph's ruling 17 (`DECISION-20260822-joseph-b1-lift-and-clause-c.md`) and
`REVIEW-CONTRACT-20260822-k0-execution-integrity.md` A-1/B-5. Every one of these files used to open
with an unconditional `REPO="<the canonical checkout>"`, which decides the executing tree before any
interpreter or guard starts -- "the wrong root is selected before Python or the guard starts". No
amount of Python-side work reaches that line, which is why the shell half is in scope at all.

BOTH DIRECTIONS ARE MEASURED BY RUNNING THE LAUNCHER, not by reading it. `bash -n` is not enough and
this repository has the receipt: on 2026-08-18 a hook inserted between a `\\`-continued command's
lines truncated the command to `bootstrap_nd.py --npz of_inputs_5d.npz` with no seed arguments at
all, and `bash -n` PASSED. Syntax valid, arguments destroyed. So:

  * with the roots UNSET (and, separately, EMPTY) each launcher must exit non-zero before it sources
    anything, naming the variable;
  * with the roots SET to stub trees each launcher must source `setup_salloc_env.sh` and
    `lib/resume_guard.sh` from the CODE root, `cd` into the DATA root, and invoke its entrypoint by
    ABSOLUTE path under the CODE root -- asserted on the observed argv, not on the source text;
  * with the member library resolving OUTSIDE the code root it must fail closed.

WHAT THIS CANNOT SAY. It runs bash locally (3.2.57 on macOS, 4.4 on Perlmutter) and never under
Slurm, so `BASH_SOURCE`-under-spool behaviour is untested here and remains ruling 14's business. The
stubs model the resolver's inputs, not Slurm.
"""
import os
import pathlib
import shutil
import subprocess
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
ND = HERE.parent

#: The eight. Re-derive, do not trust a count: `grep -nE '^\\s*(export\\s+)?REPO=' nd-unfolding/*.sh`
#: returned all eight assigning the canonical checkout unconditionally before this repair.
LAUNCHERS = (
    ("sbatch_bootstrap_5d_gpu.sh", "bootstrap_nd.py"),
    ("sbatch_seedscan_split_5d.sh", "seedscan_split.py"),
    ("sbatch_unfold_5d_detector_bkgaware_gpu.sh", "unfold_nd_omnifold_unbinned.py"),
    ("sbatch_sweep_bank_5d_run_bkgaware_gpu.sh", "sweep_bank_5d.py"),
    ("sbatch_uthrow_run_5d_fast.sh", "unified_throw_cov_5d.py"),
    ("sbatch_uthrow_block_5d.sh", "unified_throw_cov_5d.py"),
    ("sbatch_uthrow_combine_5d_fast.sh", "unified_throw_cov_5d.py"),
    ("sbatch_finalize_5d_bkgaware_gpu.sh", "combine_cov_nd.py"),
)

CLUSTER_ROOT = "/" + "/".join(("pscratch", "sd", "j", "josephrb", "MINERvA-OmniFold"))

STUB_ENV = '[stub] setup_salloc_env sourced from $BASH_SOURCE'
STUB_RG = '[stub] resume_guard sourced from $BASH_SOURCE'
STUB_MR = '''echo "[stub] lib_member_resume sourced from $BASH_SOURCE"
mr_require_valid_offset(){ :; }
mr_prefix(){ echo "$1"; }
mr_dir_prefix(){ echo "$1"; }
mr_skip_if_complete(){ return 1; }
mr_declared(){ [ -n "${MNV_EST_SEED_OFFSET:-}" ]; }
mr_member_root(){ echo member_k000000; }
mr_run(){ shift; echo "[stub] WOULD RUN: $*"; }
rg_valid_npz(){ return 1; }
rg_marker_path(){ echo "/dev/null"; }
rg_stat_size(){ echo 0; }
rg_stat_mtime(){ echo 0; }
rg__marker_field(){ echo ""; }
'''


class LauncherRoots(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        tmp = pathlib.Path(self._tmp.name)
        self.code = tmp / "code-root"
        self.data = tmp / "data-root"
        (self.code / "nd-unfolding").mkdir(parents=True)
        (self.code / "lib").mkdir(parents=True)
        (self.data / "nd-unfolding").mkdir(parents=True)
        (self.code / "VALIDATION_LEDGER.md").write_text("# fixture ledger\n")
        (self.code / "setup_salloc_env.sh").write_text(f'echo "{STUB_ENV}"\n')
        (self.code / "lib" / "resume_guard.sh").write_text(
            f'echo "{STUB_RG}"\nrg_valid_npz(){{ return 1; }}\n')
        (self.code / "nd-unfolding" / "lib_member_resume.sh").write_text(STUB_MR)
        # DATA-side stubs. That they belong under the DATA root and not the CODE root is itself
        # the two-root split working: none of these is code, and none is in a clean checkout.
        dnd = self.data / "nd-unfolding"
        (dnd / "uq_4d").mkdir(parents=True)
        (dnd / "uq_5d").mkdir(parents=True)
        (dnd / "runEventLoopOmniFold_5D_MEFHC_universes_full_bkgaware.root").write_text("stub\n")
        (dnd / "uq_4d" / "vertical_run_bkgaware.txt").write_text("Flux:0\n")
        (dnd / "uq_5d" / "detector_universes.txt").write_text("Flux:0\n")
        self.rogue = tmp / "rogue-lib"
        self.rogue.mkdir()
        shutil.copy2(self.code / "nd-unfolding" / "lib_member_resume.sh", self.rogue)

    def _run(self, sh, env_over):
        env = dict(os.environ, SLURM_ARRAY_TASK_ID="1", PYTHONDONTWRITEBYTECODE="1")
        for k in ("MNV_CODE_ROOT", "MNV_DATA_ROOT", "MNV_LAUNCHER_DIR", "MNV_EST_SEED_OFFSET"):
            env.pop(k, None)
        env.update(env_over)
        cp = subprocess.run(["bash", str(ND / sh)], capture_output=True, text=True,
                            env=env, cwd=str(ND))
        return cp

    def _good_env(self):
        return {"MNV_CODE_ROOT": str(self.code), "MNV_DATA_ROOT": str(self.data),
                "MNV_LAUNCHER_DIR": str(self.code / "nd-unfolding"),
                # k=0, canonical integer, no leading zeros. Needed so the finalize launcher takes
                # its DECLARED branch, which is the one the M(ii) member path uses.
                "MNV_EST_SEED_OFFSET": "0"}

    def test_no_launcher_still_assigns_the_cluster_root_unconditionally(self):
        for sh, _e in LAUNCHERS:
            with self.subTest(launcher=sh):
                text = (ND / sh).read_text()
                self.assertNotIn(f'REPO="{CLUSTER_ROOT}"', text)
                self.assertNotIn(f"REPO={CLUSTER_ROOT}", text)
                self.assertIn("MNV_CODE_ROOT:?", text)
                self.assertIn("MNV_DATA_ROOT:?", text)
                # A default is the hardcode wearing a flag.
                self.assertNotIn("MNV_CODE_ROOT:-", text)
                self.assertNotIn("MNV_DATA_ROOT:-", text)

    def test_an_UNSET_root_refuses_before_anything_is_sourced(self):
        for sh, _e in LAUNCHERS:
            with self.subTest(launcher=sh):
                cp = self._run(sh, {})
                self.assertNotEqual(cp.returncode, 0, cp.stdout + cp.stderr)
                self.assertIn("MNV_CODE_ROOT", cp.stderr)
                self.assertNotIn("[stub]", cp.stdout)

    def test_an_EMPTY_root_refuses_too_because_colon_question_covers_null(self):
        """`${VAR:?}` and not `${VAR?}`: an exported-but-empty variable is the silent case."""
        for sh, _e in LAUNCHERS:
            with self.subTest(launcher=sh):
                cp = self._run(sh, {"MNV_CODE_ROOT": "", "MNV_DATA_ROOT": ""})
                self.assertNotEqual(cp.returncode, 0, cp.stdout + cp.stderr)
                self.assertIn("MNV_CODE_ROOT", cp.stderr)

    def test_with_both_roots_set_it_sources_from_CODE_and_runs_from_CODE(self):
        """The silent direction, and the substantive one: observed behaviour, not source text."""
        for sh, entry in LAUNCHERS:
            with self.subTest(launcher=sh):
                cp = self._run(sh, self._good_env())
                merged = cp.stdout + cp.stderr
                self.assertIn(f"[stub] setup_salloc_env sourced from {self.code}/", merged, merged)
                self.assertIn(f"[stub] lib_member_resume sourced from {self.code}/", merged, merged)
                self.assertNotIn("set MNV_CODE_ROOT", merged)
                # The entrypoint is named by ABSOLUTE path under the code root. Some launchers
                # reach it through `mr_run` (stubbed to echo argv), others invoke python3 directly
                # and then fail on the absent stub file -- both surface the same absolute path.
                self.assertIn(f"{self.code}/nd-unfolding/{entry}", merged, merged)
                self.assertNotIn(CLUSTER_ROOT, merged)

    def test_a_member_library_outside_the_code_root_fails_closed(self):
        env = self._good_env()
        env["MNV_LAUNCHER_DIR"] = str(self.rogue)
        for sh, _e in LAUNCHERS:
            with self.subTest(launcher=sh):
                cp = self._run(sh, env)
                self.assertEqual(cp.returncode, 2, cp.stdout + cp.stderr)
                self.assertIn("lib_member_resume.sh resolved to", cp.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
