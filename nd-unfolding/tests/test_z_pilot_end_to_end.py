"""Run the WHOLE guarded assembly chain on explicitly synthetic inputs, and both its controls.

WHAT THIS COVERS THAT NOTHING ELSE DID. `test_z_build.py` calls `build.main` IN-PROCESS and
`test_z_pilot.py` drives `run_pilot` against manifests that refuse before construction, so the
sequence

    mnv_guarded_run.py -> z_pilot.py -> z_build.py -> `git rev-parse` / `git show` -> both
    covariance products -> spectrum diagnostics -> pilot receipt validation

had never been executed end to end in one process tree. Job 58358282 died inside it: `z_build`'s
`_code_identity` launched a bare `git show`, the guard refused the launch, `z_build` exited 3, and
the pilot reported the number without the reason. Both halves of that failure are regressions here.

EXPLICITLY SYNTHETIC, AND NOT REPRESENTED OTHERWISE. The inputs come from
`test_z_build.synthetic_fixture` -- a 3-bin, 5-row declaration whose manifest carries
`input_kind: "synthetic"`, whose support-band labels are invented, and whose parent is a text file
that says it asserts no lineage. NOTHING here licenses any scientific reading. What it does
establish is that the CODE PATH closes, which is the only thing the production attempts had not
shown.

NOTHING IS MOCKED. Real `mnv_guarded_run.py`, real `git`, real subprocesses, real digests, real
receipts. The negative control removes one token from a copy of `z_build.py` and lets the guard
refuse for real; it does not patch the guard, stub `subprocess`, or assert on source text.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import numpy as np

ND = Path(__file__).resolve().parents[1]
REPO = ND.parent
if str(ND) not in sys.path:
    sys.path.insert(0, str(ND))

import mnv_guarded_run as guard
import z_pilot as pilot
import z_receipt as receipt

from test_z_build import synthetic_fixture

GUARD = ND / "mnv_guarded_run.py"

#: The guard's own words for the two refusals this file reproduces, quoted from
#: `mnv_guarded_run.py` (`_GIT_NO_EXT_DIFF_SUBCOMMANDS` and `_GIT_PROGRAM_ENV`). Matching the
#: MESSAGE and not merely a nonzero exit is the point: attempt 3 already had the nonzero exit.
REFUSAL_NO_EXT_DIFF = "git show without --no-ext-diff can run the configured diff.external program"
REFUSAL_GIT_EDITOR = "$GIT_EDITOR makes git run a program of the caller's choosing"

#: `GIT_EDITOR`, `GIT_EXTERNAL_DIFF` and their siblings turn a read-only `git` argv into a program
#: launcher, so the guard refuses any `git` while one is visible. An interactive shell may export
#: them (this developer's does: `GIT_EDITOR=true`); Perlmutter's batch environment did not, which
#: is why job 58358282 got past `git rev-parse` and died at `git show`. The positive controls here
#: therefore run with them REMOVED -- that is reproducing the target environment, not relaxing a
#: check -- and `test_a_git_program_environment_variable_is_refused_and_surfaced` keeps the
#: opposite direction covered so the removal cannot hide a live hazard.
#
# TAKEN FROM THE GUARD, NOT RETYPED. The first draft of this file hand-copied the list and got 9
# of the 11 names, omitting `GIT_CONFIG_GLOBAL` and `GIT_CONFIG_SYSTEM`, and cited a symbol
# (`_GIT_PROGRAM_ENV`) that does not exist in `mnv_guarded_run.py` at all. The drift was
# fail-closed -- an unremoved variable makes the positive arms refuse -- but a second copy of a
# guard's table is a second implementation of it, and it had already diverged before this file was
# reviewed once. Reading the tuple means the next name the guard gains is covered here for free.
GIT_PROGRAM_ENV = guard._GIT_EXTERNAL_PROGRAM_ENV_VARS


def batch_like_env(**overrides: str) -> dict:
    """The ambient environment with git's program-injection variables removed."""
    env = dict(os.environ)
    for name in GIT_PROGRAM_ENV:
        env.pop(name, None)
    env.update(overrides)
    return env


def run_chain(tree: Path, work: Path, *, env: dict | None = None) -> dict:
    """Run guard -> z_pilot against a synthetic fixture generated inside `tree`.

    `tree` is a repository root: the fixture's `producing_revision` is read from ITS `HEAD`, so a
    tree and its fixture are always self-consistent and the isolated arms need no revision
    bookkeeping.
    """
    nd = tree / "nd-unfolding"
    inputs = work / "in"
    out = work / "out"
    env = env if env is not None else batch_like_env()
    # The fixture is written by a child interpreter rooted in `tree`, so `synthetic_fixture`'s
    # module-level ND -- and therefore the `git rev-parse HEAD` it records -- is THAT tree's.
    made = subprocess.run(
        [sys.executable, "-c",
         "import sys; sys.path.insert(0, sys.argv[1]);\n"
         "from pathlib import Path;\n"
         "from test_z_build import synthetic_fixture;\n"
         "synthetic_fixture(Path(sys.argv[2]))",
         str(nd / "tests"), str(inputs)],
        capture_output=True, text=True, cwd=str(nd), env=env,
    )
    assert made.returncode == 0, f"fixture generation failed:\n{made.stdout}\n{made.stderr}"
    proc = subprocess.run(
        [sys.executable, str(nd / "mnv_guarded_run.py"),
         "--expect-root", str(tree),
         "--inventory", str(work / "inventory.jsonl"),
         "--label", work.name,
         "--", str(nd / "z_pilot.py"),
         "--manifest", str(inputs / "manifest.json"),
         "--out-dir", str(out),
         "--receipt", str(out / "z-pilot-receipt.json")],
        capture_output=True, text=True, cwd=str(nd), env=env,
    )
    inventory = []
    inventory_path = work / "inventory.jsonl"
    if inventory_path.is_file():
        inventory = [json.loads(line) for line in
                     inventory_path.read_text().splitlines() if line.strip()]
    return {"rc": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr,
            "out": out, "inputs": inputs, "inventory": inventory, "tree": tree}


def isolated_tree(destination: Path, *, drop_no_ext_diff: bool) -> Path:
    """Copy this WORKING TREE's python and guard shim into a standalone git repository.

    Standalone rather than a `git worktree add`: a worktree writes into the shared `.git`
    administrative directory that other sessions read, and this test must not put state there.
    A fresh repository also makes `_code_identity`'s `git show <HEAD>:<path>` compare against blobs
    committed FROM THE SAME BYTES, so the negative arm's only difference from the positive arm is
    the one token, not an incidental dirty-file report.
    """
    # `VALIDATION_LEDGER.md` IS NOT OPTIONAL BALLAST. `mnv_guarded_run.MARKERS` is
    # `("VALIDATION_LEDGER.md", "nd-unfolding")`, and an `--expect-root` missing either is not a
    # checkout: the guard then exits 2 = CANNOT-LOOK *without running the payload*. That is the
    # same integer the pilot uses for "completed, NON-PASSING", which is why
    # `assert_chain_completed` requires the guard's INSPECTED verdict and not just the 2.
    tracked = subprocess.check_output(
        ["git", "ls-files", "-z", "VALIDATION_LEDGER.md",
         "nd-unfolding/*.py", "nd-unfolding/mnv_guard_shim/*"],
        cwd=REPO, text=True,
    ).split("\0")
    destination.mkdir(parents=True, exist_ok=True)
    for rel in (p for p in tracked if p):
        src = REPO / rel
        if not src.is_file():          # a path staged by another session but not materialised here
            continue
        dst = destination / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    target = destination / "nd-unfolding" / "z_build.py"
    if drop_no_ext_diff:
        text = target.read_text()
        token = '["git", "show", "--no-ext-diff", f"{head}:{path}"],'
        assert text.count(token) == 1, (
            f"the negative control could not find the repaired invocation to revert "
            f"(found {text.count(token)} occurrences). If z_build.py's `git show` was respelled, "
            f"this control is measuring nothing and must be updated deliberately."
        )
        target.write_text(text.replace(token, '["git", "show", f"{head}:{path}"],'))
    env = dict(os.environ, GIT_AUTHOR_NAME="control", GIT_AUTHOR_EMAIL="control@invalid",
               GIT_COMMITTER_NAME="control", GIT_COMMITTER_EMAIL="control@invalid")
    # `-c core.hooksPath=` : this repository sets `core.hooksPath` to an absolute path, and a
    # fresh `git init` elsewhere must not run the project's hooks against a partial copy.
    for argv in (["git", "-c", "init.defaultBranch=control", "init", "-q"],
                 ["git", "-c", "core.hooksPath=", "add", "-A"],
                 ["git", "-c", "core.hooksPath=", "commit", "-q", "-m", "synthetic control tree"]):
        subprocess.run(argv, cwd=destination, check=True, capture_output=True, env=env)
    return destination


class GuardedAssemblyEndToEnd(unittest.TestCase):
    """The executed chain, its two refusal controls, and the properties exit 2 does not carry."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory(prefix="z-e2e-")
        cls.root = Path(cls._tmp.name)

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def work(self, name: str) -> Path:
        path = self.root / name
        path.mkdir(parents=True, exist_ok=True)
        return path

    # ---------------------------------------------------------------- the positive control ---
    def assert_chain_completed(self, result: dict) -> dict:
        """Every property the authorization names, from the CLOSED files rather than the exit."""
        self.assertEqual(
            result["rc"], 2,
            f"expected the pilot's completion code 2, got {result['rc']}.\n"
            f"stdout:\n{result['stdout']}\nstderr:\n{result['stderr']}",
        )
        out = result["out"]
        expected = ("z-cv.npz", "z-mean.npz", "z-null.npz",
                    "z-receipt-cv.json", "z-receipt-mean.json", "z-pilot-receipt.json")
        for name in expected:
            self.assertTrue((out / name).is_file(), f"{name} was not written")

        # ⚠ THE GUARD MUST HAVE ACTUALLY LOOKED, AND THIS ARM CAUGHT ME NOT CHECKING IT.
        # `mnv_guarded_run.py` exits 2 for CANNOT-LOOK -- "never 'we checked and it was clean'" --
        # and can do so WITHOUT RUNNING THE PAYLOAD. The first draft of the isolated arm did
        # exactly that (no VALIDATION_LEDGER.md in the copy), so `rc == 2` was true while nothing
        # had been assembled. The launcher models this collision at its `2)` arm; a test that
        # reads only the integer does not.
        # The record's own field name is `verdict`; `outcome` is a DIFFERENT field carrying the
        # child's exit disposition ("child-systemexit:2"), and reading it here would have made
        # this assertion unsatisfiable rather than merely weak.
        verdicts = [r.get("verdict", "") for r in result["inventory"]]
        self.assertTrue(verdicts, "the guard wrote no inventory record at all")
        # ITERATE OVER RECORDS, NOT OVER VERDICT STRINGS. The first draft looped over `verdicts`
        # and then re-selected `[r for r in inventory if r["verdict"] == verdict][0]` -- which is
        # `inventory[0]` on every pass, because every verdict on the completing path is the same
        # string. One record was checked twice and the other never, and which one that was
        # depended on write order.
        for record in result["inventory"]:
            self.assertEqual(
                record.get("verdict"), "REPOSITORY-ORIGINS-INSPECTED",
                f"a guarded process did not inspect: {verdicts}. The guard exits 2 for "
                f"CANNOT-LOOK -- the same integer the pilot uses for completion -- so a 2 with a "
                f"COULD NOT LOOK verdict means nothing was assembled.",
            )
            self.assertIsNone(
                record.get("launch_refusal"),
                f"guarded process pid {record.get('pid')} (depth {record.get('depth')}, script "
                f"{record.get('script')}) recorded a launch refusal on the completing path",
            )
        for record in result["inventory"]:
            self.assertEqual(record.get("repo_origins_outside_expect_root", 0), 0)
            self.assertIs(record.get("guard_installed"), True)
            self.assertEqual(record.get("static_scan"), "enabled",
                             "the static argv scan was disabled; provenance was not checked")

        # ⚠ THE CLAIM THIS WHOLE FILE EXISTS FOR, read from the guard's own record rather than
        # inferred from the exit code: `z_build.py` RAN AS A GUARDED CHILD (depth 1) and the guard
        # inspected it without refusing a launch. Job 58358282 has a depth-1 record for the same
        # script with `verdict` refused and `launch_refusal.offending_flag` naming `git show`.
        children = [r for r in result["inventory"]
                    if r.get("depth") == 1 and str(r.get("script", "")).endswith("z_build.py")]
        self.assertEqual(
            len(children), 1,
            f"expected exactly one depth-1 guarded z_build child; got "
            f"{[(r.get('depth'), r.get('script')) for r in result['inventory']]}",
        )
        self.assertEqual(children[0]["verdict"], "REPOSITORY-ORIGINS-INSPECTED")
        self.assertIsNone(children[0]["launch_refusal"])
        self.assertIsNone(children[0]["refusal_site"])

        envelope = json.loads(result["stdout"])
        self.assertEqual(envelope["pilot_status"], "CHECKED")
        self.assertEqual(envelope["scientific_acceptance"], "NON-PASSING")
        self.assertIs(envelope["adoptable"], False)

        pilot_receipt = json.loads((out / "z-pilot-receipt.json").read_text())
        self.assertEqual(pilot_receipt["build_returncode"], 2)
        self.assertEqual(pilot_receipt["scientific_acceptance"], "NON-PASSING")
        self.assertIs(pilot_receipt["adoptable"], False)
        self.assertIs(pilot_receipt["revisions_distinct"], True)
        self.assertNotEqual(pilot_receipt["producer_revision"],
                            pilot_receipt["assembling_revision"])

        # DIGEST BINDINGS, re-measured against the files on disk rather than read back from the
        # receipt's own copy of its own claim.
        for role, stamp in pilot_receipt["artifacts"].items():
            path = Path(stamp["path"])
            self.assertEqual(
                receipt.sha256_file(path), stamp["sha256"],
                f"pilot receipt's recorded digest for {role} does not match the file",
            )
        for variant, record in pilot_receipt["verified_products"].items():
            self.assertEqual(receipt.sha256_file(Path(record["product"])), record["sha256"])

        # RECEIPT-LAST. The granularity-free form of the claim: the pilot receipt names, and
        # correctly digests, all six artifacts -- so all six existed and were readable before it
        # was written. The mtime comparison is the weaker corroboration and is asserted second.
        named = {Path(s["path"]).name for s in pilot_receipt["artifacts"].values()}
        self.assertEqual(named, set(expected) - {"z-pilot-receipt.json"})
        newest_artifact = max((out / n).stat().st_mtime_ns
                              for n in expected if n != "z-pilot-receipt.json")
        self.assertGreaterEqual((out / "z-pilot-receipt.json").stat().st_mtime_ns,
                                newest_artifact)

        # SPECTRUM DIAGNOSTICS, bound to the product they were computed from.
        for variant in ("cv", "mean"):
            spectrum = pilot_receipt["spectra"][variant]
            self.assertEqual(spectrum["product"]["sha256"],
                             receipt.sha256_file(out / f"z-{variant}.npz"))
            for field in ("lambda_min", "lambda_max", "n_negative", "eigensolve_seconds"):
                self.assertIn(field, spectrum)
            self.assertTrue(np.isfinite(spectrum["lambda_min"]))
            self.assertTrue(np.isfinite(spectrum["lambda_max"]))
            self.assertGreaterEqual(spectrum["lambda_max"], spectrum["lambda_min"])
            # The build owns the PSD verdict; this file records what was measured and does not
            # restate a threshold.
            self.assertIsNone(spectrum["verdict"])
        return pilot_receipt

    def assert_code_identity_ran(self, result: dict, *, expect_dirty: list[str] | None) -> None:
        """The `git show` subprocesses ran, and their OUTPUT was used -- not just their exit.

        A launch that succeeds proves the guard admitted the argv. That the returned blob was
        COMPARED is a separate claim, and `[]` cannot carry it -- an empty dirty list is exactly
        what "no comparison happened" produces, so pinning `[]` is one-sided. The claim needs a
        tree where a named file IS expected to differ; see
        `test_a_file_edited_after_the_commit_is_named_in_the_dirty_list`, which is the arm that
        kills the mutation discarding `blob.stdout`.
        """
        for variant in ("cv", "mean"):
            record = json.loads((result["out"] / f"z-receipt-{variant}.json").read_text())
            identity = record["code_identity"]
            closure = identity["import_closure_digests"]
            self.assertGreater(
                len(closure), 5,
                "the import closure is implausibly small; `git show` ran for too few modules",
            )
            head = subprocess.check_output(["git", "rev-parse", "HEAD"],
                                           cwd=result["tree"], text=True).strip()
            self.assertEqual(identity["revision"], head)
            if expect_dirty is not None:
                self.assertEqual(identity["worktree_files_differing_from_revision"],
                                 expect_dirty)

    def test_the_whole_chain_closes_in_this_working_tree(self) -> None:
        """The production tree, the production guard invocation, the production exit contract."""
        result = run_chain(REPO, self.work("live"))
        self.assert_chain_completed(result)
        # This tree may legitimately be dirty (that is what a lane worktree is for), so the dirty
        # LIST is not pinned here -- only that the comparison ran. The isolated arm below pins it.
        self.assert_code_identity_ran(result, expect_dirty=None)

    def test_the_isolated_control_tree_also_closes(self) -> None:
        """The positive control that licenses the negative one.

        Without this, a refusal in the isolated tree could be caused by the ISOLATION -- a missing
        file, a partial copy -- rather than by the token the negative arm removes.
        """
        tree = isolated_tree(self.work("iso-ok") / "tree", drop_no_ext_diff=False)
        result = run_chain(tree, self.work("iso-ok"))
        self.assert_chain_completed(result)
        # Committed from the same bytes it runs, so NOTHING differs from the revision. This pins
        # the dirty list exactly, which the live tree cannot.
        self.assert_code_identity_ran(result, expect_dirty=[])

    def test_a_file_edited_after_the_commit_is_named_in_the_dirty_list(self) -> None:
        """`git show`'s OUTPUT is read, not merely its exit code.

        REVIEW FINDING R1, AND IT WAS A REAL HOLE. Every other arm of this file pins
        `worktree_files_differing_from_revision` to `[]` or not at all, and `[]` is what a build
        that never looks at `blob.stdout` also produces. Mutating z_build.py's

            if blob.returncode or hashlib.sha256(blob.stdout).hexdigest() != digest:

        to `if False and (...)` left 8 of 8 arms green, and 110 more across three sibling suites.
        A provenance field that always reports a clean worktree would have shipped.

        So: build the control tree, THEN edit one module that is in the build's import closure,
        and require the build to name exactly that path. The edit is an appended comment -- the
        module still imports, the build still completes with exit 2, and the only thing that
        changes is the digest `git show`'s stdout is compared against.
        """
        work = self.work("iso-dirty")
        tree = isolated_tree(work / "tree", drop_no_ext_diff=False)
        # z_statistics.py is imported by z_build (it computes the null ratio), so it is in the
        # closure `_code_identity` walks. A trailing comment cannot change its behaviour.
        edited = tree / "nd-unfolding" / "z_statistics.py"
        edited.write_text(
            edited.read_text()
            + "\n# R1 two-sided control: one line differing from the committed revision.\n"
        )
        result = run_chain(tree, work)
        self.assert_chain_completed(result)
        self.assert_code_identity_ran(
            result, expect_dirty=["nd-unfolding/z_statistics.py"]
        )

    # ---------------------------------------------------------------- the negative controls ---
    def test_the_original_git_invocation_is_refused_and_the_reason_survives(self) -> None:
        """Remove one token and the chain reproduces job 58358282 -- with the reason attached."""
        tree = isolated_tree(self.work("iso-bare") / "tree", drop_no_ext_diff=True)
        result = run_chain(tree, self.work("iso-bare"))

        self.assertEqual(result["rc"], 1,
                         f"expected the pilot's refusal code 1\nstderr:\n{result['stderr']}")
        envelope = json.loads(result["stderr"].splitlines()[0])
        self.assertEqual(envelope["pilot_status"], "FAILED")
        reason = envelope["reason"]

        # (a) The historical symptom is still reported: an exit outside the CLI's contract.
        self.assertIn("the build exited 3", reason)
        # (b) AND THE CAUSE IS NOW IN IT. This is the whole delta. Attempt 3's message stopped at
        #     (a); recovering (b) took a read of the guard's inventory JSONL.
        self.assertIn(REFUSAL_NO_EXT_DIFF, reason)
        self.assertIn("git show", reason)
        # (c) The verbatim re-emission, because json.dumps escapes the newlines that make a
        #     multi-line guard refusal readable in a job's .err file.
        self.assertIn("[z-pilot] FAILED -- verbatim reason follows", result["stderr"])
        self.assertIn(REFUSAL_NO_EXT_DIFF,
                      result["stderr"].split("verbatim reason follows", 1)[1])

        # (d) The refusal is the GUARD's, at LAUNCH, on the argv this repair changed -- not some
        #     other failure that happens to be nonzero. Read from the guard's own inventory.
        refusals = [r for r in result["inventory"]
                    if r.get("launch_refusal")
                    or "REFUS" in str(r.get("verdict", "")).upper()
                    or "REFUS" in str(r.get("outcome", "")).upper()]
        self.assertTrue(refusals, "the guard recorded no refusal; something else failed")
        offending = [r.get("launch_refusal", {}).get("offending_flag", "") for r in refusals]
        self.assertTrue(any(REFUSAL_NO_EXT_DIFF in text for text in offending),
                        f"the guard refused for a different reason: {offending}")
        argvs = [r.get("launch_refusal", {}).get("argv") for r in refusals]
        self.assertTrue(
            any(argv and argv[:2] == ["git", "show"] and "--no-ext-diff" not in argv
                for argv in argvs),
            f"no refused argv matches the historical bare `git show`: {argvs}",
        )
        # (e) The OI-136 containment is unaffected by the refusal: no module came from outside.
        for record in result["inventory"]:
            self.assertEqual(record.get("repo_origins_outside_expect_root", 0), 0)

        # (f) NO PRODUCTS. A refusal that had already written a covariance would be worse than
        #     the refusal.
        for name in ("z-cv.npz", "z-mean.npz", "z-pilot-receipt.json"):
            self.assertFalse((result["out"] / name).exists(),
                             f"{name} exists after a refused build")

    def test_a_git_program_environment_variable_is_refused_and_surfaced(self) -> None:
        """The other direction: a clean argv, a hostile environment, same surfacing.

        `batch_like_env` REMOVES these variables from the positive controls. A removal with no
        test in the opposite direction is exactly the shape that waves a live hazard through, so
        this arm puts one back and requires the refusal AND its reason. It also documents the
        standing exposure: `sbatch_z_pilot_5d.sh` does not unset them, so a login profile that
        exported `GIT_EDITOR` would fail the pilot this way -- reported, not repaired here.
        """
        result = run_chain(REPO, self.work("giteditor"),
                           env=batch_like_env(GIT_EDITOR="true"))
        self.assertEqual(result["rc"], 1, f"stderr:\n{result['stderr'][:2000]}")
        reason = json.loads(result["stderr"].splitlines()[0])["reason"]
        self.assertIn(REFUSAL_GIT_EDITOR, reason)
        # Refused at `git rev-parse`, which runs BEFORE `git show` -- so this arm cannot be
        # passing for the `--no-ext-diff` reason by accident.
        self.assertIn("'rev-parse'", reason)
        self.assertNotIn(REFUSAL_NO_EXT_DIFF, reason)

    # ------------------------------------------------- the surfacing itself, as a unit ---
    def test_an_absent_diagnostic_is_reported_as_absent_not_as_an_explanation(self) -> None:
        """A silent child must not read as a diagnosed one.

        The failure mode this guards against is the fix itself becoming decorative: if the child
        writes nothing, the message must SAY that the exit code is all there is, rather than
        presenting an empty quotation as a cause.
        """
        message = pilot.format_diagnostic("")
        self.assertIn("NOTHING to stderr", message)
        self.assertIn("uninformative", message)
        self.assertEqual(pilot.format_diagnostic(None), message)

    def test_the_exit_code_alone_would_not_have_carried_the_cause(self) -> None:
        """The mutation that shows the delta is load-bearing, at the unit that formats it."""
        stderr = (
            "[oi136 launch] THIS CHILD CANNOT BE PROVEN ...\n"
            f"[oi136 launch]   offending flag {REFUSAL_NO_EXT_DIFF}\n"
        )
        with self.assertRaises(Exception) as caught:
            pilot._validate_completion(3, "", {}, stderr)
        with_cause = str(caught.exception)
        self.assertIn(REFUSAL_NO_EXT_DIFF, with_cause)

        # The pre-repair behaviour, reproduced by withholding what the repair supplies.
        with self.assertRaises(Exception) as caught:
            pilot._validate_completion(3, "", {})
        without = str(caught.exception)
        self.assertIn("the build exited 3", without)
        self.assertNotIn(REFUSAL_NO_EXT_DIFF, without)

    def test_a_long_diagnostic_is_abridged_with_its_loss_measured(self) -> None:
        """An abridged quote with no measure of what was dropped is the same defect, smaller."""
        text = "HEAD-MARKER\n" + ("x" * 20000) + "\nTAIL-MARKER"
        record = pilot.child_diagnostic(text)
        self.assertTrue(record["abridged"])
        self.assertEqual(record["chars"], len(text))
        self.assertEqual(record["omitted_chars"],
                         len(text) - 2 * pilot.DIAGNOSTIC_KEEP_CHARS)
        self.assertNotIn("text", record)
        message = pilot.format_diagnostic(text)
        # BOTH ENDS SURVIVE, and the REASON IS NOT THE ONE THIS FILE FIRST GAVE. Review measured
        # the executed negative control: the refusal envelope begins at offset 197 of a 2475-char
        # child stderr -- 8% in, i.e. in the HEAD -- because `z_build` writes nothing to stderr
        # before `_code_identity`, and the guard's inventory is flushed at child EXIT, after it.
        # So a head-only abridgement would have kept job 58358282's refusal, and the comment that
        # used to sit here claimed the opposite. Both ends are kept because a refusal can land at
        # either: at startup (head, the measured case) or after a long-running payload's own
        # progress output (tail). This fixture is synthetic and derived from the rule, so it can
        # only show that both ends survive -- it cannot tell us which end a real refusal lands in.
        # That came from measuring the real one.
        self.assertIn("HEAD-MARKER", message)
        self.assertIn("TAIL-MARKER", message)
        self.assertIn(str(record["omitted_chars"]), message)

    def test_the_completing_path_preserves_the_childs_stderr_too(self) -> None:
        """Recorded on success, not only on failure -- a NON-PASSING build still warns."""
        result = run_chain(REPO, self.work("preserve"))
        pilot_receipt = self.assert_chain_completed(result)
        record = pilot_receipt["build_stderr"]
        self.assertIn("sha256", record)
        self.assertIn("chars", record)
        text = record.get("text", record.get("head", "") + record.get("tail", ""))
        self.assertIn("oi136", text,
                      "the build ran under the guard, so its stderr must carry the guard's own "
                      "inventory line; an empty record here means the capture is decorative")


if __name__ == "__main__":
    unittest.main()
