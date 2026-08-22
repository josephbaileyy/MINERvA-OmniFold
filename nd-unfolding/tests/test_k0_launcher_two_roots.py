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
        for sh, _e, _t in LAUNCHERS:
            with self.subTest(launcher=sh):
                shutil.rmtree(self.invdir, ignore_errors=True)
                cp = self.run_launcher(sh, self.good_env())
                self.assertNotEqual(cp.returncode, 0, cp.stdout + cp.stderr)
                self.assertIn("SOURCE MANIFEST MOVED", cp.stderr + cp.stdout)
                self.assertEqual(self.inventories(), [],
                                 "it must stop BEFORE any guarded process runs")

    def test_a_missing_guard_in_the_code_root_is_refused_rather_than_skipped(self):
        (self.code / "nd-unfolding" / "mnv_guarded_run.py").unlink()
        cp = self.run_launcher(LAUNCHERS[0][0], self.good_env())
        self.assertEqual(cp.returncode, 2, cp.stdout + cp.stderr)
        self.assertIn("required tool missing", cp.stderr)

    def test_a_SYMLINKED_guard_is_refused_because_a_link_can_leave_the_code_root(self):
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
