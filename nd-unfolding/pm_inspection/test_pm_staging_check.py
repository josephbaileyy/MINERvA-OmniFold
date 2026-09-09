#!/usr/bin/env python3
"""Tests for the pre-approval check of a staged item.

THE POSITIVE FIXTURE IS A REAL STAGED ITEM.  It is not a dict this file wrote by hand: it is
built by calling ``campaignctl.stage`` itself, in an isolated temporary git repository holding
the real guard, the real shim, the real producer and validator, the real bindings and the
reviewed contract.  A hand-written fixture only ever encodes what the author believed staging
does -- and the first version of this checker was wrong about exactly that: it compared the
argv against RELATIVE paths, while ``command_bindings`` rewrites the guard target and the
script to absolute in place.  A fixture from the real construction path would have failed
immediately.

WHAT THE ISOLATION IS, EXACTLY.  ``stage`` runs inside ``queue_operation``, which refreshes
against the pinned origin, so staging is not a local operation and these tests cannot pretend
otherwise.  Each test therefore builds its own bare repository in its temp dir and commits an
origin pin naming it, so no test reaches the real origin, no test can write to the real
campaign ref, and no test contacts a scheduler.  The queue state directory is a throwaway temp
dir.

WHAT THAT ISOLATION DOES NOT PROVE.  The mock changes two things about the world: where the
origin lives, and the root the guard and validator are pinned to.  Everything else -- the
guard, the shim, the producer, the validator, the bindings and the reviewed contract -- is the
real file.  So these tests establish the CHECKER's behaviour against a really-staged item.
They say nothing about whether the production origin is reachable, whether its queue ref is in
the state staging expects, or whether the real execution checkout is pinned where the contract
says.  Those are integration facts and no test here substitutes for measuring them.
"""
from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))

import check_staged_item as checker  # noqa: E402
import pm_root_inspect as producer  # noqa: E402

#: Copied into every temporary repository. The guard shim is copied whole, because
#: GUARD_SHIM_PATHS binds each of its files and a missing one is a staging refusal.
COPIED_FILES = (
    "docs/orchestration/campaignctl.py",
    "nd-unfolding/mnv_guarded_run.py",
    "nd-unfolding/pm_inspection/pm_root_inspect.py",
    "nd-unfolding/pm_inspection/pm_root_validate.py",
    checker.BINDINGS_PATH,
)
COPIED_TREES = ("nd-unfolding/mnv_guard_shim",)

#: The ruling record the origin pin names. Copied because the pin's identity checks are
#: string comparisons against module constants and the pin itself must be committed.
ORIGIN_PIN_PATH = "docs/orchestration/control-plane/campaign-origin.json"


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                            text=True, timeout=120)
    if result.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout


def reviewed_contract_bytes() -> bytes:
    """The contract that was reviewed, found by digest rather than by branch name."""
    import hashlib
    candidates = [REPO / checker.CONTRACT_PATH]
    for revision in ("HEAD", "9f12c728", "origin/main", "main"):
        try:
            blob = subprocess.run(
                ["git", "-C", str(REPO), "show", f"{revision}:{checker.CONTRACT_PATH}"],
                capture_output=True, timeout=120)
        except OSError:
            continue
        if blob.returncode == 0:
            candidates.append(blob.stdout)
    for candidate in candidates:
        raw = candidate.read_bytes() if isinstance(candidate, Path) and candidate.is_file() \
            else candidate if isinstance(candidate, bytes) else None
        if raw is None:
            continue
        if hashlib.sha256(raw).hexdigest() == checker.REVIEWED_CONTRACT_SHA256:
            return raw
    raise AssertionError(
        f"the reviewed contract ({checker.REVIEWED_CONTRACT_SHA256}) is not reachable from "
        "this checkout, so this branch could not be staged from either")


def build_repo(tmp: str) -> tuple[Path, object]:
    """An isolated git repo holding the real files, plus its own loaded controller."""
    repo = (Path(tmp) / "repo").resolve()
    repo.mkdir()
    for relative in COPIED_FILES:
        target = repo / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO / relative, target)
    for relative in COPIED_TREES:
        shutil.copytree(REPO / relative, repo / relative)

    # The guard requires --expect-root to name the queue repository root by absolute path,
    # so the contract's validator argv is repointed at this temporary repo. Nothing else in
    # the reviewed contract is touched.
    contract = reviewed_contract_bytes().decode()
    contract = contract.replace(checker.DEFAULT_EXPECT_ROOT, str(repo))
    contract_file = repo / checker.CONTRACT_PATH
    contract_file.parent.mkdir(parents=True, exist_ok=True)
    contract_file.write_text(contract)

    # An isolated MOCK REMOTE. campaignctl.stage runs inside queue_operation, which
    # refreshes against the pinned origin (campaignctl.py:2353, :2105), so staging is not a
    # local-only operation. The pin here names a bare repository in this temp dir, so no test
    # reaches the real origin and no test can write to the real campaign ref.
    origin = (Path(tmp) / "origin-remote").resolve()
    subprocess.run(["git", "init", "-q", "--bare", str(origin)], check=True, timeout=120)

    real_pin = json.loads((REPO / ORIGIN_PIN_PATH).read_text())
    real_pin["origin_url"] = str(origin)
    pin_file = repo / ORIGIN_PIN_PATH
    pin_file.parent.mkdir(parents=True, exist_ok=True)
    pin_file.write_text(json.dumps(real_pin, indent=2) + "\n")

    git(repo, "init", "-q")
    git(repo, "remote", "add", "origin", str(origin))
    git(repo, "add", "-A")
    git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "fixture")

    sys.path.insert(0, str(repo / "docs/orchestration"))
    ctl = checker.load_controller(repo)
    return repo, ctl


def stage_real_item(repo: Path, ctl, tmp: str, *, timeout_seconds: int | None = None) -> dict:
    """Call the controller's own stage() against the temp repo's own mock origin."""
    state = Path(tmp) / "queue-state"
    state.mkdir()
    queue = ctl.Queue(repo=repo, state=state)
    return ctl.stage(
        queue,
        checker.CAMPAIGN_ID,
        checker.DESCRIPTION,
        "compute",
        ".",
        [],
        [checker.BINDINGS_PATH],
        checker.literal_argv(str(repo)),
        int(producer.STAGED_TIMEOUT_SECONDS) if timeout_seconds is None else timeout_seconds,
        checker.CONTRACT_PATH,
    )


class StagedFixture(unittest.TestCase):
    """Base case: one real staged item, and the checker run against it."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = self._tmp.name
        self.repo, self.ctl = build_repo(self.tmp)
        self.item = stage_real_item(self.repo, self.ctl, self.tmp)
        self.contract_sha = self.ctl.sha256_file(self.repo / checker.CONTRACT_PATH)

    def tearDown(self):
        self._tmp.cleanup()

    def check(self, item, **over):
        kwargs = dict(repo=self.repo, expect_root=str(self.repo), ctl=self.ctl,
                      expect_contract_sha256=self.contract_sha)
        kwargs.update(over)
        return checker.check_item(item, **kwargs)


class ThePositiveControl(StagedFixture):
    """A checker that refuses everything proves nothing."""

    def test_a_really_staged_item_passes(self):
        self.assertEqual(self.check(self.item), [])

    def test_the_real_argv_is_absolute_which_the_first_version_rejected(self):
        # The finding: command_bindings rewrites argv in place (campaignctl.py:2621, :2650).
        self.assertTrue(Path(self.item["argv"][1]).is_absolute())
        target = self.item["argv"][self.item["argv"].index("--") + 1]
        self.assertTrue(Path(target).is_absolute())

    def test_the_bindings_file_is_bound_not_merely_named(self):
        # The finding: --bindings is an argv VALUE; only --bind makes it a bound file.
        bound = {binding["path"] for binding in self.item["bindings"]}
        self.assertIn(checker.BINDINGS_PATH, bound)
        self.assertIn(checker.CONTRACT_PATH, bound)


class TheStageDefaultIsCaughtBeforeApproval(StagedFixture):
    def test_a_really_staged_600_second_item_is_refused_by_name(self):
        # Staged for real at the controller's own default rather than mutated, because the
        # danger is precisely that campaignctl ACCEPTS 600 -- which this also demonstrates.
        # It needs its own repository and its own mock origin: stage lands the item on the
        # queue ref, so re-staging the same id into the same origin is refused, as it should
        # be.
        with tempfile.TemporaryDirectory() as tmp:
            repo, ctl = build_repo(tmp)
            item = stage_real_item(repo, ctl, tmp, timeout_seconds=600)
            self.assertEqual(item["timeout_seconds"], 600)
            findings = checker.check_item(
                item, repo=repo, expect_root=str(repo), ctl=ctl,
                expect_contract_sha256=ctl.sha256_file(repo / checker.CONTRACT_PATH))
        self.assertIn("killed mid-wait", "\n".join(findings))

    def test_a_timeout_that_starves_the_validator_is_refused(self):
        item = copy.deepcopy(self.item)
        item["timeout_seconds"] = 1790
        item["proposal_digest"] = self.ctl.digest(self.ctl.proposal_payload(item))
        self.assertIn("validator would not be started", "\n".join(self.check(item)))


class AForgedDigestIsCaught(StagedFixture):
    def test_a_bogus_digest_is_refused_even_when_every_field_matches(self):
        item = copy.deepcopy(self.item)
        item["proposal_digest"] = "0" * 64
        findings = "\n".join(self.check(item))
        self.assertIn("payload digests to", findings)

    def test_a_digest_recomputed_over_a_tampered_payload_is_still_caught(self):
        # Consistent with itself, inconsistent with the committed tree.
        item = copy.deepcopy(self.item)
        item["timeout_seconds"] = 600
        item["proposal_digest"] = self.ctl.digest(self.ctl.proposal_payload(item))
        findings = self.check(item)
        self.assertTrue(findings)
        self.assertNotIn("payload digests to", "\n".join(findings))


class TheBindingsMustBeTheOnesTheTreeProduces(StagedFixture):
    def test_an_added_unrelated_binding_is_refused(self):
        item = copy.deepcopy(self.item)
        item["bindings"] = item["bindings"] + [{"path": "README.md", "sha256": "0" * 64}]
        item["proposal_digest"] = self.ctl.digest(self.ctl.proposal_payload(item))
        self.assertIn("bindings is not what the committed tree produces",
                      "\n".join(self.check(item)))

    def test_a_dropped_binding_is_refused(self):
        item = copy.deepcopy(self.item)
        item["bindings"] = [b for b in item["bindings"]
                            if b["path"] != checker.BINDINGS_PATH]
        item["proposal_digest"] = self.ctl.digest(self.ctl.proposal_payload(item))
        self.assertIn("bindings is not what the committed tree produces",
                      "\n".join(self.check(item)))

    def test_a_stale_binding_hash_is_refused_as_not_committed_and_identical(self):
        item = copy.deepcopy(self.item)
        item["bindings"] = copy.deepcopy(item["bindings"])
        item["bindings"][0]["sha256"] = "1" * 64
        item["proposal_digest"] = self.ctl.digest(self.ctl.proposal_payload(item))
        findings = "\n".join(self.check(item))
        self.assertIn("not committed-and-identical", findings)


class TheContractMustBeTheReviewedOne(StagedFixture):
    def test_a_different_contract_digest_is_refused(self):
        findings = "\n".join(self.check(self.item, expect_contract_sha256="9" * 64))
        self.assertIn("Re-review before changing this pin", findings)

    def test_a_raised_cpu_budget_is_refused(self):
        item = copy.deepcopy(self.item)
        item["campaign_contract"]["maximum_cost"]["cpu_task_hours"] = 4.0
        item["proposal_digest"] = self.ctl.digest(self.ctl.proposal_payload(item))
        findings = "\n".join(self.check(item))
        self.assertIn("not the reviewed", findings)

    def test_a_validator_pointed_at_another_script_is_refused(self):
        item = copy.deepcopy(self.item)
        argv = item["campaign_contract"]["terminal_validator"]["argv"]
        argv[argv.index("nd-unfolding/pm_inspection/pm_root_validate.py")] = \
            "nd-unfolding/pm_inspection/pm_root_inspect.py"
        item["proposal_digest"] = self.ctl.digest(self.ctl.proposal_payload(item))
        self.assertIn("campaign_contract is not what the committed tree produces",
                      "\n".join(self.check(item)))

    def test_standalone_with_required_elsewhere_is_refused(self):
        # The first version asked whether both strings appeared ANYWHERE in the argv.
        item = copy.deepcopy(self.item)
        argv = item["campaign_contract"]["terminal_validator"]["argv"]
        argv[argv.index("required")] = "standalone"
        argv.extend(["--label", "required"])
        item["proposal_digest"] = self.ctl.digest(self.ctl.proposal_payload(item))
        findings = "\n".join(self.check(item))
        self.assertIn("adjacent flag/value pair", findings)

    def test_the_adjacency_helper_is_not_a_substring_search(self):
        self.assertFalse(checker.adjacent(["--campaign-mode", "standalone", "required"],
                                          "--campaign-mode", "required"))
        self.assertTrue(checker.adjacent(["--campaign-mode", "required"],
                                         "--campaign-mode", "required"))


class TheArgvAndHeadMustBeTheReviewedOnes(StagedFixture):
    def test_a_changed_walltime_is_refused(self):
        item = copy.deepcopy(self.item)
        item["argv"][item["argv"].index("--minutes") + 1] = "25"
        item["proposal_digest"] = self.ctl.digest(self.ctl.proposal_payload(item))
        self.assertIn("argv is not what the committed tree produces",
                      "\n".join(self.check(item)))

    def test_a_head_that_is_not_the_checkouts_head_is_refused(self):
        item = copy.deepcopy(self.item)
        item["git_head"] = "f" * 40
        item["proposal_digest"] = self.ctl.digest(self.ctl.proposal_payload(item))
        self.assertIn("but the checkout under inspection is at",
                      "\n".join(self.check(item)))

    def test_a_head_that_is_not_the_reviewed_head_is_refused(self):
        findings = "\n".join(self.check(self.item, expect_head="e" * 40))
        self.assertIn("not the reviewed", findings)

    def test_the_walltime_tracks_the_launcher_and_cannot_drift(self):
        self.assertIn(str(producer.DEFAULT_MINUTES), checker.literal_argv("/x"))


class TheExitCodeIsTheGate(StagedFixture):
    def _run(self, item, extra=()):
        from contextlib import redirect_stdout
        from io import StringIO
        path = Path(self.tmp) / "item.json"
        path.write_text(json.dumps(item))
        buffer = StringIO()
        with redirect_stdout(buffer):
            code = checker.main(["--item", str(path), "--repo", str(self.repo),
                                 "--expect-root", str(self.repo),
                                 "--expect-contract-sha256", self.contract_sha, *extra])
        return code, buffer.getvalue()

    def test_a_good_item_exits_zero_and_says_it_is_not_an_approval(self):
        code, out = self._run(self.item)
        self.assertEqual(code, 0)
        self.assertIn("NOT an approval", out)
        self.assertIn("approve --id", out)

    def test_a_bad_item_exits_one_and_prints_no_approve_line(self):
        item = copy.deepcopy(self.item)
        item["timeout_seconds"] = 600
        code, out = self._run(item)
        self.assertEqual(code, 1)
        self.assertNotIn("approve --id", out)

    def test_a_checkout_with_no_controller_is_CANNOT_CHECK_not_a_pass(self):
        from contextlib import redirect_stdout
        from io import StringIO
        path = Path(self.tmp) / "item2.json"
        path.write_text(json.dumps(self.item))
        empty = Path(self.tmp) / "empty"
        empty.mkdir()
        buffer = StringIO()
        with redirect_stdout(buffer):
            code = checker.main(["--item", str(path), "--repo", str(empty)])
        self.assertEqual(code, 2)
        self.assertIn("NOT a pass", buffer.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
