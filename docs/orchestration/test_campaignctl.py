import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from collections.abc import Callable
from pathlib import Path
from unittest import mock

import campaignctl


FIXTURE_DIR = Path(__file__).resolve().parent / "test_fixtures_campaign_contract"
CONTRACT_FIXTURE = FIXTURE_DIR / "validator-failed-after-jobs-complete.json"
R5_FIXTURES = {
    name: FIXTURE_DIR / f"r5-meter-{name}.json"
    for name in (
        "healthy",
        "stale",
        "fired",
        "headroom-exhausting",
        "malformed",
        "near-gpu-ceiling",
    )
}
#: The real OI-136 guard, copied into every fixture repository rather than restated.
#: A hand-written stand-in would be a second implementation of the rule under test,
#: and its refusals would only ever agree with whatever this suite assumed.
REAL_GUARD = campaignctl.REPO / campaignctl.GUARD_PATH


class CampaignQueueTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="campaign-queue-test.")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "-C", str(self.repo), "init", "-q"], check=True)
        subprocess.run(
            [
                "git",
                "-C",
                str(self.repo),
                "config",
                "user.email",
                "test@example.invalid",
            ],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(self.repo), "config", "user.name", "Test"],
            check=True,
        )
        self.script = self.repo / "work.py"
        self.script.write_text(
            "from pathlib import Path\n"
            "Path('ran').write_text('yes')\n"
            "output = Path('outputs/validator-failure-fixture')\n"
            "output.mkdir(parents=True, exist_ok=True)\n"
            "(output / 'jobs-complete').write_text('all complete')\n"
        )
        guard = self.repo / "nd-unfolding" / "mnv_guarded_run.py"
        guard.parent.mkdir()
        guard.write_bytes(REAL_GUARD.read_bytes())
        # The guard refuses to install (COULD NOT LOOK, exit 2) unless its tracked subprocess
        # shim sits beside it, so the fixture checkout carries the shim as the real one does.
        # It is COMMITTED like the guard below, because the shim is the guard's enforcing half
        # in every inheriting child and the queue binds it under the guard's own rules.
        shim_dir = guard.parent / "mnv_guard_shim"
        shim_dir.mkdir(parents=True, exist_ok=True)
        self.shim = shim_dir / "sitecustomize.py"
        self.shim.write_bytes(
            (REAL_GUARD.parent / "mnv_guard_shim" / "sitecustomize.py").read_bytes()
        )
        # `mnv_guarded_run.py` recognises a checkout by the marker PAIR, so the fixture
        # repository needs both markers before `--expect-root` can name it.
        (self.repo / "VALIDATION_LEDGER.md").write_text("fixture ledger\n")
        # A second checkout outside the fixture repository, holding the logic the
        # reviewer's mutated validator reaches for. This is the OI-136 shape: an
        # uncommitted tree whose module decides the terminal branch.
        self.outside = self.root / "outside-checkout"
        (self.outside / "nd-unfolding").mkdir(parents=True)
        (self.outside / "VALIDATION_LEDGER.md").write_text("other ledger\n")
        (self.outside / "decisive_criterion.py").write_text("VERDICT = 0\n")
        self.sneaky_validator = self.repo / "sneaky_validator.py"
        self.sneaky_validator.write_text(
            "import sys\n"
            f"sys.path.insert(0, {str(self.outside)!r})\n"
            "import decisive_criterion\n"
            "raise SystemExit(decisive_criterion.VERDICT)\n"
        )
        self.validator_success = self.repo / "validator_success.py"
        self.validator_success.write_text(
            "import os\n"
            "from pathlib import Path\n"
            "Path('validator-ran').write_text(\n"
            "    os.environ['CAMPAIGN_PRODUCER_RETURNCODE']\n"
            ")\n"
        )
        self.failure_script = self.repo / "validator_failure.py"
        self.failure_script.write_text(
            "import os\n"
            "from pathlib import Path\n"
            "output = Path('outputs/validator-failure-fixture')\n"
            "output.mkdir(parents=True, exist_ok=True)\n"
            "(output / 'validator-report').write_text('failed')\n"
            "(output / 'producer-returncode').write_text(\n"
            "    os.environ['CAMPAIGN_PRODUCER_RETURNCODE']\n"
            ")\n"
            "raise SystemExit(23)\n"
        )
        self.timeout_script = self.repo / "timeout.py"
        self.timeout_script.write_text("import time\ntime.sleep(2)\n")
        self.brief_script = self.repo / "brief_producer.py"
        self.brief_script.write_text("import time\ntime.sleep(0.4)\n")
        subprocess.run(
            [
                "git",
                "-C",
                str(self.repo),
                "add",
                "work.py",
                "validator_failure.py",
                "validator_success.py",
                "sneaky_validator.py",
                "timeout.py",
                "brief_producer.py",
                "VALIDATION_LEDGER.md",
                "nd-unfolding/mnv_guarded_run.py",
                "nd-unfolding/mnv_guard_shim/sitecustomize.py",
            ],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(self.repo), "commit", "-qm", "initial"],
            check=True,
        )
        # Compute is admissible only from the CANONICAL state directory of the queue's
        # own repository, so the fixture queue lives at the temporary checkout's
        # canonical path rather than at an arbitrary directory beside it.
        self.queue = campaignctl.Queue(
            repo=self.repo,
            state=self.repo / campaignctl.CANONICAL_STATE_RELATIVE,
            clock=lambda: "2026-09-29T12:00:00+00:00",
        )
        self.assertTrue(self.queue.state_is_canonical())
        self.receipts = 0
        # The R5 receipt is evidence, so it must be COMMITTED before it can admit
        # anything. Every test therefore commits its receipt into the fixture
        # repository first: a receipt commit moves HEAD, and an item staged
        # against an older HEAD is `stale` by the drift rule that already exists.
        self.healthy_receipt = self.install_receipt("healthy")

    def stage(
        self,
        item_id: str = "one",
        depends: list[str] | None = None,
        *,
        kind: str = "write",
        contract: str | None = None,
        script: str | None = None,
        timeout_seconds: int = 30,
        guarded: bool = True,
        argv: list[str] | None = None,
        queue: campaignctl.Queue | None = None,
    ) -> dict:
        target = script or "work.py"
        if argv is None:
            argv = [sys.executable, target]
            if kind == "compute" and guarded:
                argv = self.guarded_argv(target)
        return campaignctl.stage(
            queue or self.queue,
            item_id,
            "test item",
            kind,
            ".",
            depends or [],
            [],
            argv,
            timeout_seconds,
            contract,
        )

    def other_queue(self, name: str = "second-queue-state") -> campaignctl.Queue:
        """Return a queue on the SAME repository at a non-canonical state directory.

        This is the second half of the reviewer's mutation: one repository, one
        committed receipt, and a second "campaign-global" lock and inventory that
        the canonical queue cannot see. The helper asserts nothing about
        ``state_is_canonical``: a precondition check here would refuse the
        mutation before it reached the behaviour the test is about.
        """
        return campaignctl.Queue(
            repo=self.repo, state=self.root / name, clock=self.queue.clock
        )

    def finish_item(
        self, item_id: str, at_utc: str, status: str = "succeeded"
    ) -> dict:
        """Record a terminal outcome for a claimed item, stamped at ``at_utc``.

        ``write_outcome`` is campaignctl's only writer of an outcome record, so the
        fixture calls it rather than restating the record's shape -- a hand-written
        outcome could only ever agree with what this suite assumed.
        """
        previous = self.queue.clock
        self.queue.clock = lambda: at_utc
        try:
            return campaignctl.write_outcome(
                self.queue, self.queue.item(item_id), status, returncode=0
            )
        finally:
            self.queue.clock = previous

    def guarded_argv(
        self,
        target: str,
        *,
        expect_root: str | None = None,
        allow: str | None = None,
        extra: list[str] | None = None,
    ) -> list[str]:
        """Return the argv a compute command must have: routed through the guard.

        Parameters
        ----------
        target : str
            Script the guard runs after the mandatory ``--``.
        expect_root : str or None, optional
            Value for ``--expect-root``; the queue repository root by default.
        allow : str or None, optional
            Foreign checkout to pass as ``--allow``, which a production arm may
            never carry.
        extra : list[str] or None, optional
            Extra elements inserted before ``--``, for interpreter and
            environment escapes.

        Returns
        -------
        list[str]
            The complete guard argument vector.
        """
        argv = [
            sys.executable,
            "nd-unfolding/mnv_guarded_run.py",
            "--expect-root",
            expect_root if expect_root is not None else str(self.repo),
        ]
        if allow is not None:
            argv += ["--allow", allow]
        argv += list(extra or [])
        return argv + ["--", target]

    def write_contract(
        self,
        *,
        commit: bool = False,
        validator_script: str = "validator_failure.py",
        guarded_validator: bool = True,
        validator_argv: list[str] | None = None,
        name: str = "campaign-contract.json",
        mutate: Callable[[dict[str, object]], None] | None = None,
    ) -> str:
        contract = json.loads(CONTRACT_FIXTURE.read_text())
        terminal_validator = contract["terminal_validator"]
        assert isinstance(terminal_validator, dict)
        if validator_argv is not None:
            terminal_validator["argv"] = validator_argv
        else:
            terminal_validator["argv"] = (
                self.guarded_argv(validator_script)
                if guarded_validator
                else [sys.executable, validator_script]
            )
        if mutate is not None:
            mutate(contract)
        path = self.repo / name
        path.write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n")
        if commit:
            subprocess.run(
                ["git", "-C", str(self.repo), "add", path.name], check=True
            )
            subprocess.run(
                ["git", "-C", str(self.repo), "commit", "-qm", "add contract"],
                check=True,
            )
        return path.name

    def approve(
        self,
        item: dict[str, object],
        queue: campaignctl.Queue | None = None,
    ) -> dict:
        return campaignctl.approve(
            queue or self.queue,
            item["id"],
            item["proposal_digest"],
            interactive=False,
        )

    def run_ready(
        self, receipt: str | None = None
    ) -> tuple[int, dict[str, object]]:
        value = self.healthy_receipt if receipt is None else receipt
        with mock.patch.dict(os.environ, {"CAMPAIGN_R5_RECEIPT": value}):
            return campaignctl.run_ready(self.queue)

    def install_receipt(
        self,
        source: str = "healthy",
        *,
        commit: bool = True,
        **changes: object,
    ) -> str:
        """Commit a meter receipt into the fixture repository.

        Parameters
        ----------
        source : str, optional
            Name of the checked-in receipt fixture to copy.
        commit : bool, optional
            Commit the receipt. ``False`` leaves it untracked, which is one of
            the states an uncommitted measurement can be in.
        **changes : object
            Receipt fields to overwrite, named exactly as the meter writes them.
            The checked-in fixtures keep the ruled values.

        Returns
        -------
        str
            Repository-relative path of the receipt, the only form
            ``CAMPAIGN_R5_RECEIPT`` accepts.
        """
        text = R5_FIXTURES[source].read_text()
        if changes:
            receipt = json.loads(text)
            receipt.update(changes)
            text = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
        self.receipts += 1
        relative = f"docs/orchestration/state/r5-meter-{self.receipts}.json"
        path = self.repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        if commit:
            subprocess.run(
                ["git", "-C", str(self.repo), "add", relative], check=True
            )
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(self.repo),
                    "commit",
                    "-qm",
                    f"meter receipt {self.receipts}",
                ],
                check=True,
            )
        return relative

    def test_stage_approve_and_run_exactly_once(self):
        item = self.stage()
        self.approve(item)
        rc, outcome = campaignctl.run_ready(self.queue)
        self.assertEqual((rc, outcome["status"]), (0, "succeeded"))
        self.assertEqual((self.repo / "ran").read_text(), "yes")
        rc, value = campaignctl.run_ready(self.queue)
        self.assertEqual((rc, value["status"]), (0, "idle"))

    def test_requires_exact_approval_digest(self):
        item = self.stage()
        with self.assertRaisesRegex(campaignctl.QueueError, "does not match"):
            campaignctl.approve(self.queue, item["id"], "0" * 64, interactive=False)

    def test_noninteractive_cli_approval_is_rejected(self):
        item = self.stage()
        with mock.patch.object(campaignctl.sys.stdin, "isatty", return_value=False):
            with self.assertRaisesRegex(campaignctl.QueueError, "interactive TTY"):
                campaignctl.approve(self.queue, item["id"], item["proposal_digest"])

    def test_bound_file_drift_fails_closed(self):
        item = self.stage()
        self.approve(item)
        self.script.write_text("raise SystemExit('changed')\n")
        rc, outcome = campaignctl.run_ready(self.queue)
        self.assertEqual((rc, outcome["status"]), (4, "stale"))
        self.assertFalse((self.repo / "ran").exists())

    def test_head_drift_fails_closed(self):
        item = self.stage()
        self.approve(item)
        extra = self.repo / "extra"
        extra.write_text("x")
        os.system(f"git -C {self.repo} add extra && git -C {self.repo} commit -qm next")
        rc, outcome = campaignctl.run_ready(self.queue)
        self.assertEqual((rc, outcome["status"]), (4, "stale"))

    def test_dependency_must_succeed_first(self):
        first = self.stage("first")
        second = self.stage("second", ["first"])
        self.approve(first)
        self.approve(second)
        self.assertEqual(campaignctl.run_ready(self.queue)[1]["id"], "first")
        self.assertEqual(campaignctl.run_ready(self.queue)[1]["id"], "second")

    def test_shell_and_external_executables_are_rejected(self):
        with self.assertRaisesRegex(campaignctl.QueueError, "outside repository"):
            campaignctl.stage(
                self.queue, "bad", "bad", "write", ".", [], [],
                ["/bin/bash", "-c", "true"], 30,
            )

    def test_claim_without_outcome_is_never_retried(self):
        item = self.stage()
        self.approve(item)
        campaignctl.atomic_json(
            self.queue.path("claims", item["id"]), {"id": item["id"]}, exclusive=True
        )
        rc, value = campaignctl.run_ready(self.queue)
        self.assertEqual((rc, value["status"]), (5, "outcome-unknown"))
        self.assertFalse((self.repo / "ran").exists())

    def test_compute_requires_committed_campaign_contract(self) -> None:
        with self.assertRaisesRegex(campaignctl.QueueError, "require.*contract"):
            self.stage("compute-without-contract", kind="compute")

        contract = self.write_contract()
        with self.assertRaisesRegex(campaignctl.QueueError, "must be committed"):
            self.stage(
                "validator-failure-fixture", kind="compute", contract=contract
            )

    def test_legacy_compute_item_without_contract_is_refused(self) -> None:
        item = self.stage("legacy-item")
        item["kind"] = "compute"
        item["proposal_digest"] = campaignctl.digest(
            campaignctl.proposal_payload(item)
        )
        campaignctl.atomic_json(self.queue.path("items", item["id"]), item)

        with self.assertRaisesRegex(campaignctl.QueueError, "require.*contract"):
            self.approve(item)

    def test_contract_refuses_same_producer_and_validator(self) -> None:
        contract = self.write_contract(
            mutate=lambda value: value.update(
                independent_validator=value["producer"]
            )
        )
        with self.assertRaisesRegex(campaignctl.QueueError, "pairwise distinct"):
            self.stage(
                "validator-failure-fixture", kind="compute", contract=contract
            )

    def test_contract_refuses_same_producer_and_decision_authority(self) -> None:
        contract = self.write_contract(
            mutate=lambda value: value.update(
                decision_authority=str(value["producer"]).upper()
            )
        )
        with self.assertRaisesRegex(campaignctl.QueueError, "pairwise distinct"):
            self.stage(
                "validator-failure-fixture", kind="compute", contract=contract
            )

    def test_contract_requires_terminal_validator(self) -> None:
        def remove_validator(value: dict[str, object]) -> None:
            del value["terminal_validator"]

        contract = self.write_contract(mutate=remove_validator)
        with self.assertRaisesRegex(campaignctl.QueueError, "terminal_validator"):
            self.stage(
                "validator-failure-fixture", kind="compute", contract=contract
            )

    def test_contract_refuses_nonfinite_cost(self) -> None:
        def set_infinite_cost(value: dict[str, object]) -> None:
            maximum_cost = value["maximum_cost"]
            assert isinstance(maximum_cost, dict)
            maximum_cost["gpu_task_hours"] = float("inf")

        contract = self.write_contract(mutate=set_infinite_cost)
        with self.assertRaisesRegex(campaignctl.QueueError, "finite and nonnegative"):
            self.stage(
                "validator-failure-fixture", kind="compute", contract=contract
            )

    def test_contract_refuses_decisionless_or_uncovered_terminal_results(
        self,
    ) -> None:
        def remove_decision(value: dict[str, object]) -> None:
            branches = value["terminal_branches"]
            assert isinstance(branches, list)
            branch = branches[0]
            assert isinstance(branch, dict)
            branch["decision"] = ""

        contract = self.write_contract(mutate=remove_decision)
        with self.assertRaisesRegex(campaignctl.QueueError, "decision.*nonempty"):
            self.stage(
                "validator-failure-fixture", kind="compute", contract=contract
            )

        def remove_fallback(value: dict[str, object]) -> None:
            branches = value["terminal_branches"]
            assert isinstance(branches, list)
            value["terminal_branches"] = branches[:-1]

        contract = self.write_contract(mutate=remove_fallback)
        with self.assertRaisesRegex(campaignctl.QueueError, "exactly one 'otherwise'"):
            self.stage(
                "validator-failure-fixture", kind="compute", contract=contract
            )

    def test_unclassified_return_code_has_a_decision_consequence(self) -> None:
        contract = campaignctl.validate_campaign_contract(
            json.loads(CONTRACT_FIXTURE.read_text())
        )

        plan = campaignctl.terminal_plan(contract, 99)

        self.assertEqual(plan["terminal_branch"], "unexpected-terminal-result")
        self.assertEqual(
            plan["decision_consequence"],
            "Preserve available evidence and stop for terminal classification.",
        )

    def test_successful_compute_records_its_decision_consequence(self) -> None:
        contract = self.write_contract(
            commit=True,
            validator_script="validator_success.py",
            mutate=lambda value: value.update(campaign_id="successful-fixture"),
        )
        item = self.stage(
            "successful-fixture", kind="compute", contract=contract
        )
        self.approve(item)

        rc, outcome = self.run_ready()

        self.assertEqual((rc, outcome["status"]), (0, "succeeded"))
        self.assertEqual(outcome["terminal_branch"], "terminal-validator-passed")
        self.assertEqual(outcome["producer_returncode"], 0)
        self.assertEqual(outcome["validator_returncode"], 0)
        self.assertTrue(Path(outcome["producer_log"]).is_file())
        self.assertTrue(Path(outcome["validator_log"]).is_file())
        self.assertTrue(outcome["decision_consequence"])

    def test_validator_failure_preserves_first_and_does_not_retrain(self) -> None:
        contract = self.write_contract(commit=True)
        item = self.stage(
            "validator-failure-fixture",
            kind="compute",
            contract=contract,
        )
        self.approve(item)

        rc, outcome = self.run_ready()

        self.assertEqual((rc, outcome["status"]), (3, "failed"))
        self.assertEqual(outcome["producer_returncode"], 0)
        self.assertEqual(outcome["validator_returncode"], 23)
        self.assertEqual(outcome["terminal_branch"], "terminal-validator-failed")
        self.assertEqual(outcome["required_actions"][0]["action"], "preserve")
        self.assertFalse(outcome["automatic_retraining"])
        self.assertTrue(outcome["retry_requires_new_authorization"])
        output = self.repo / "outputs" / "validator-failure-fixture"
        self.assertEqual((output / "jobs-complete").read_text(), "all complete")
        self.assertEqual((output / "validator-report").read_text(), "failed")
        self.assertEqual((output / "producer-returncode").read_text(), "0")

        rc, value = self.run_ready()
        self.assertEqual((rc, value["status"]), (0, "idle"))

    def test_validator_runs_after_producer_timeout(self) -> None:
        contract = self.write_contract(
            commit=True,
            validator_script="validator_success.py",
            mutate=lambda value: value.update(campaign_id="timeout-fixture"),
        )
        item = self.stage(
            "timeout-fixture",
            kind="compute",
            contract=contract,
            script="timeout.py",
            timeout_seconds=1,
        )
        self.approve(item)

        rc, outcome = self.run_ready()

        self.assertEqual((rc, outcome["status"]), (0, "succeeded"))
        self.assertIsNone(outcome["producer_returncode"])
        self.assertEqual(outcome["validator_returncode"], 0)
        self.assertEqual(
            (self.repo / "validator-ran").read_text(),
            "TIMEOUT_OR_NOT_STARTED",
        )

    def test_validator_launch_failure_uses_otherwise_branch(self) -> None:
        contract = self.write_contract(
            commit=True,
            validator_script="validator_success.py",
        )
        item = self.stage(
            "validator-failure-fixture", kind="compute", contract=contract
        )
        self.approve(item)

        with mock.patch.object(
            campaignctl,
            "run_logged_command",
            side_effect=[(0, None), (None, "command could not be started")],
        ):
            rc, outcome = self.run_ready()

        self.assertEqual((rc, outcome["status"]), (3, "failed"))
        self.assertEqual(outcome["producer_returncode"], 0)
        self.assertIsNone(outcome["validator_returncode"])
        self.assertEqual(outcome["terminal_branch"], "unexpected-terminal-result")

    def test_unguarded_compute_producer_is_refused(self) -> None:
        contract = self.write_contract(commit=True)

        with self.assertRaisesRegex(campaignctl.QueueError, "must route through"):
            self.stage(
                "validator-failure-fixture",
                kind="compute",
                contract=contract,
                guarded=False,
            )

    def test_unguarded_terminal_validator_is_refused_at_stage(self) -> None:
        """The reviewer's mutation, at staging: the validator bypassed the guard."""
        contract = self.write_contract(
            commit=True,
            validator_script="sneaky_validator.py",
            guarded_validator=False,
        )

        with self.assertRaisesRegex(
            campaignctl.QueueError, "terminal validator must route through"
        ):
            self.stage(
                "validator-failure-fixture", kind="compute", contract=contract
            )

    def test_guarded_validator_refusal_resolves_to_the_otherwise_branch(self) -> None:
        """A validator importing decisive logic from another tree cannot pass.

        Unguarded, the mutated validator exits 0 and would select the pass branch
        with the outside tree's verdict. Guarded, the guard's own MEASURED
        VIOLATION is an unclassified terminal result, so it must land on
        ``otherwise`` and never on ``terminal-validator-passed``.
        """
        unguarded = subprocess.run(
            [sys.executable, "sneaky_validator.py"],
            cwd=self.repo,
            check=False,
        )
        self.assertEqual(unguarded.returncode, 0)

        contract = self.write_contract(
            commit=True, validator_script="sneaky_validator.py"
        )
        item = self.stage(
            "validator-failure-fixture", kind="compute", contract=contract
        )
        bound = {binding["path"] for binding in item["bindings"]}
        self.assertIn("sneaky_validator.py", bound)
        self.assertIn("nd-unfolding/mnv_guarded_run.py", bound)
        self.approve(item)

        rc, outcome = self.run_ready()

        self.assertEqual((rc, outcome["status"]), (3, "failed"))
        self.assertEqual(outcome["validator_returncode"], 3)
        self.assertEqual(outcome["terminal_branch"], "unexpected-terminal-result")
        self.assertEqual(outcome["required_actions"][0]["action"], "preserve")
        self.assertIn(
            "IMPORT TREE VIOLATION",
            Path(str(outcome["validator_log"])).read_text(),
        )

    def test_dirty_terminal_validator_is_refused_before_the_claim(self) -> None:
        """The validator target is bound, so it obeys the producer's drift rule."""
        contract = self.write_contract(
            commit=True, validator_script="validator_success.py"
        )
        item = self.stage(
            "validator-failure-fixture", kind="compute", contract=contract
        )
        self.assertIn(
            "validator_success.py",
            {binding["path"] for binding in item["bindings"]},
        )
        self.validator_success.write_text("raise SystemExit('dirty validator')\n")

        with self.assertRaisesRegex(campaignctl.QueueError, "changed after staging"):
            campaignctl.validate_unchanged(self.queue, item)

    def test_dirty_compute_binding_is_refused_at_stage_and_validation(self) -> None:
        contract = self.write_contract(commit=True)
        self.script.write_text("raise SystemExit('dirty before staging')\n")
        with self.assertRaisesRegex(campaignctl.QueueError, "committed at HEAD"):
            self.stage(
                "validator-failure-fixture", kind="compute", contract=contract
            )

        subprocess.run(
            ["git", "-C", str(self.repo), "restore", "work.py"], check=True
        )
        item = self.stage(
            "validator-failure-fixture", kind="compute", contract=contract
        )
        self.script.write_text("raise SystemExit('dirty after staging')\n")
        with self.assertRaisesRegex(campaignctl.QueueError, "changed after staging"):
            campaignctl.validate_unchanged(self.queue, item)

    def test_untracked_terminal_validator_is_refused_at_stage(self) -> None:
        untracked_validator = self.repo / "untracked_validator.py"
        untracked_validator.write_text("raise SystemExit(0)\n")
        contract = self.write_contract(
            commit=True,
            validator_script=untracked_validator.name,
        )

        with self.assertRaisesRegex(
            campaignctl.QueueError, "committed at repository HEAD"
        ):
            self.stage(
                "validator-failure-fixture", kind="compute", contract=contract
            )

    def test_compute_timeout_cannot_exceed_contract_wall_hours(self) -> None:
        def restrict_wall_time(value: dict[str, object]) -> None:
            maximum_cost = value["maximum_cost"]
            assert isinstance(maximum_cost, dict)
            maximum_cost["wall_hours"] = 1 / 3600

        contract = self.write_contract(commit=True, mutate=restrict_wall_time)
        with self.assertRaisesRegex(campaignctl.QueueError, "timeout exceeds"):
            self.stage(
                "validator-failure-fixture",
                kind="compute",
                contract=contract,
                timeout_seconds=2,
            )

    def test_one_wall_deadline_covers_producer_and_validator(self) -> None:
        """A 1 s wall spent entirely by the producer leaves no second allowance.

        The reviewer's mutation declared a 1 s wall and observed 2.09 s: the
        producer was allowed 1 s and the validator another 1 s. One deadline
        means the run must end inside the declared wall, and the validator that
        never started must resolve to ``otherwise`` with its reason recorded.
        """
        def one_second_wall(value: dict[str, object]) -> None:
            maximum_cost = value["maximum_cost"]
            assert isinstance(maximum_cost, dict)
            maximum_cost["wall_hours"] = 1 / 3600

        contract = self.write_contract(
            commit=True,
            validator_script="validator_success.py",
            mutate=one_second_wall,
        )
        item = self.stage(
            "validator-failure-fixture",
            kind="compute",
            contract=contract,
            script="timeout.py",
            timeout_seconds=1,
        )
        self.approve(item)

        started = time.monotonic()
        rc, outcome = self.run_ready()
        elapsed = time.monotonic() - started

        self.assertEqual((rc, outcome["status"]), (3, "failed"))
        self.assertIsNone(outcome["producer_returncode"])
        self.assertIsNone(outcome["validator_returncode"])
        self.assertTrue(outcome["wall_budget_exhausted"])
        self.assertEqual(
            outcome["validator_error"], "wall budget exhausted before validation"
        )
        self.assertEqual(outcome["terminal_branch"], "unexpected-terminal-result")
        self.assertEqual(outcome["required_actions"][0]["action"], "preserve")
        self.assertFalse(outcome["automatic_retraining"])
        self.assertFalse((self.repo / "validator-ran").exists())
        self.assertLess(elapsed, 1.5)

    def test_validator_receives_only_the_budget_the_producer_left(self) -> None:
        """0.4 s of a 1 s wall leaves the validator the remainder, not a fresh 1 s."""
        def one_second_wall(value: dict[str, object]) -> None:
            maximum_cost = value["maximum_cost"]
            assert isinstance(maximum_cost, dict)
            maximum_cost["wall_hours"] = 1 / 3600

        contract = self.write_contract(
            commit=True,
            validator_script="validator_success.py",
            mutate=one_second_wall,
        )
        item = self.stage(
            "validator-failure-fixture",
            kind="compute",
            contract=contract,
            script="brief_producer.py",
            timeout_seconds=1,
        )
        self.approve(item)

        rc, outcome = self.run_ready()

        self.assertEqual((rc, outcome["status"]), (0, "succeeded"))
        self.assertEqual(outcome["producer_returncode"], 0)
        self.assertEqual(outcome["validator_returncode"], 0)
        self.assertFalse(outcome["wall_budget_exhausted"])
        validator_budget = float(outcome["validator_timeout_seconds"])
        # The producer's 0.4 s sleep plus interpreter and guard start-up leaves
        # roughly 0.5 s. The bounds are wide because the machine is shared; what
        # they exclude is the defect, which handed the validator the full 1 s.
        self.assertLess(validator_budget, 0.8)
        self.assertGreater(validator_budget, 0.1)
        self.assertLess(validator_budget, float(item["timeout_seconds"]))

    def test_missing_or_malformed_r5_receipt_is_retryable_refusal(self) -> None:
        malformed = self.install_receipt("malformed")
        contract = self.write_contract(
            commit=True,
            validator_script="validator_success.py",
        )
        item = self.stage(
            "validator-failure-fixture", kind="compute", contract=contract
        )
        self.approve(item)

        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("CAMPAIGN_R5_RECEIPT", None)
            rc, outcome = campaignctl.run_ready(self.queue)
        self.assertEqual((rc, outcome["status"]), (6, "refused"))
        self.assertIn("R5 receipt missing", outcome["reason"])
        self.assertFalse(self.queue.path("claims", item["id"]).exists())
        self.assertFalse((self.repo / "ran").exists())

        rc, outcome = self.run_ready(malformed)
        self.assertEqual((rc, outcome["status"]), (6, "refused"))
        self.assertIn("R5 receipt malformed", outcome["reason"])
        self.assertFalse(self.queue.path("claims", item["id"]).exists())

        rc, outcome = self.run_ready()
        self.assertEqual((rc, outcome["status"]), (0, "succeeded"))
        self.assertTrue((self.repo / "ran").is_file())

    def test_stale_r5_receipt_refuses_compute(self) -> None:
        self._assert_r5_refusal(self.install_receipt("stale"), "R5 receipt stale")

    def test_fired_r5_receipt_refuses_compute(self) -> None:
        self._assert_r5_refusal(self.install_receipt("fired"), "R5 stop fired")

    def test_r5_stop_date_refuses_compute(self) -> None:
        self.queue.clock = lambda: "2026-09-30T00:00:00+00:00"
        self._assert_r5_refusal(self.healthy_receipt, "R5 stop date reached")

    def test_r5_projected_inclusive_ceiling_refuses_compute(self) -> None:
        self._assert_r5_refusal(
            self.install_receipt("headroom-exhausting"),
            "gpu_task_hours ceiling would be reached",
        )

    def test_r5_receipt_metered_from_another_t0_refuses_compute(self) -> None:
        """The reviewer's mutation: midnight instead of the ruled commit instant.

        ``r5_meter`` refuses that receipt and campaignctl accepted it, so the two
        modules disagreed about which interval had been metered.
        """
        self._assert_r5_refusal(
            self.install_receipt(t0_utc="2026-09-02T00:00:00+00:00"),
            "t0_utc does not match the ruled instant",
        )

    def test_r5_receipt_naming_another_decision_record_refuses_compute(self) -> None:
        self._assert_r5_refusal(
            # A plausibly shaped record that is not the ruling this stop comes
            # from. Deliberately not the path of any real document, so the
            # manifest does not read this mutation as a reference to one.
            self.install_receipt(
                decision_record=(
                    "docs/orchestration/DECISION-20260902-some-other-ruling.md"
                )
            ),
            "decision_record does not match the ruling record",
        )

    def test_future_dated_r5_receipt_refuses_compute(self) -> None:
        """A receipt dated one day after the queue clock was accepted as fresh."""
        self._assert_r5_refusal(
            self.install_receipt(measured_at_utc="2026-09-30T12:00:00+00:00"),
            "receipt is dated in the future",
        )

    def test_r5_receipt_inside_the_tolerated_skew_allows_compute(self) -> None:
        """The future check must stay silent on the skew a correct run can show."""
        receipt = self.install_receipt(measured_at_utc="2026-09-29T12:00:30+00:00")
        contract = self.write_contract(
            commit=True,
            validator_script="validator_success.py",
        )
        item = self.stage(
            "validator-failure-fixture", kind="compute", contract=contract
        )
        self.approve(item)

        rc, outcome = self.run_ready(receipt)

        self.assertEqual((rc, outcome["status"]), (0, "succeeded"))

    def test_committed_r5_receipt_allows_compute(self) -> None:
        """The accepting direction: a TRACKED, unmodified receipt admits compute."""
        contract = self.write_contract(
            commit=True,
            validator_script="validator_success.py",
        )
        item = self.stage(
            "validator-failure-fixture", kind="compute", contract=contract
        )
        self.approve(item)
        tracked = subprocess.run(
            ["git", "-C", str(self.repo), "ls-files", "--error-unmatch",
             self.healthy_receipt],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        self.assertEqual(tracked.returncode, 0)

        rc, outcome = self.run_ready(self.healthy_receipt)

        self.assertEqual((rc, outcome["status"]), (0, "succeeded"))

    def test_r5_receipt_copied_outside_the_repository_is_refused(self) -> None:
        """The reviewer's mutation: a valid receipt copied to a temporary path.

        The copy is byte-identical to the committed fixture and passes every
        schema and freshness check, so what is refused here is its PROVENANCE:
        nothing in the repository records that this measurement was ever taken.
        """
        copied = self.root / "r5-meter-receipt.json"
        copied.write_text((self.repo / self.healthy_receipt).read_text())
        self.assertTrue(copied.is_absolute())
        campaignctl.validate_r5_receipt(json.loads(copied.read_text()))

        self._assert_r5_refusal(str(copied), "receipt is not committed at HEAD")

    def test_untracked_r5_receipt_is_refused(self) -> None:
        self._assert_r5_refusal(
            self.install_receipt(commit=False),
            "receipt is not committed at HEAD",
        )

    def test_r5_receipt_edited_after_commit_is_refused(self) -> None:
        receipt = self.install_receipt()
        contract = self.write_contract(
            commit=True,
            validator_script="validator_success.py",
        )
        item = self.stage(
            "validator-failure-fixture", kind="compute", contract=contract
        )
        self.approve(item)
        # The committed receipt measured 100 GPU task-hours; the working tree now
        # says 1. Byte identity with the blob at HEAD is what makes the number in
        # the receipt the number somebody can re-read.
        edited = json.loads((self.repo / receipt).read_text())
        edited["spend"]["gpu_task_hours"] = 1.0
        edited["headroom"]["gpu_task_hours"] = 499.0
        (self.repo / receipt).write_text(
            json.dumps(edited, indent=2, sort_keys=True) + "\n"
        )

        rc, outcome = self.run_ready(receipt)

        self.assertEqual((rc, outcome["status"]), (6, "refused"))
        self.assertIn("receipt is not committed at HEAD", outcome["reason"])
        self.assertFalse(self.queue.path("claims", item["id"]).exists())
        self.assertFalse((self.repo / "ran").exists())

    def _assert_r5_refusal(self, receipt: str, reason: str) -> None:
        contract = self.write_contract(
            commit=True,
            validator_script="validator_success.py",
        )
        item = self.stage(
            "validator-failure-fixture", kind="compute", contract=contract
        )
        self.approve(item)

        rc, outcome = self.run_ready(receipt)

        self.assertEqual((rc, outcome["status"]), (6, "refused"))
        self.assertIn(reason, outcome["reason"])
        self.assertFalse(self.queue.path("claims", item["id"]).exists())
        self.assertFalse((self.repo / "ran").exists())

    def six_hour_contract(self, campaign_id: str) -> str:
        """Commit a contract declaring six GPU task-hours for ``campaign_id``."""
        def declare(value: dict[str, object]) -> None:
            value["campaign_id"] = campaign_id
            value["maximum_cost"] = {
                "cpu_task_hours": 1.0,
                "gpu_task_hours": 6.0,
                "wall_hours": 6.0,
            }

        return self.write_contract(
            commit=True,
            validator_script="validator_success.py",
            name=f"contract-{campaign_id}.json",
            mutate=declare,
        )

    def _alpha_in_flight_with_beta_ready(self, receipt: str) -> None:
        """Admit a six-hour item, leave it running, then make a second one ready.

        This is the two-ticker shape the reviewer's mutation had: the first item
        is claimed and has written no terminal receipt, so whatever it may
        already be spending is in no receipt yet.
        """
        alpha_contract = self.six_hour_contract("alpha")
        alpha = self.stage("alpha", kind="compute", contract=alpha_contract)
        self.approve(alpha)
        with mock.patch.object(
            campaignctl,
            "run_compute_item",
            side_effect=lambda queue, item, env: (
                0,
                {"status": "running", "id": item["id"]},
            ),
        ):
            rc, value = self.run_ready(receipt)
        self.assertEqual((rc, value["id"]), (0, "alpha"))
        self.assertTrue(self.queue.path("claims", "alpha").exists())
        self.assertEqual(
            campaignctl.state_of(self.queue, self.queue.item("alpha")),
            "outcome-unknown",
        )

        beta_contract = self.six_hour_contract("beta")
        beta = self.stage("beta", kind="compute", contract=beta_contract)
        self.approve(beta)

    def test_two_six_hour_items_cannot_both_be_admitted(self) -> None:
        """The reviewer's mutation: 490 GPU task-hours recorded, two six-hour items.

        Each item was checked against ``spend + its own maximum_cost`` alone --
        496 against a ceiling of 500 -- so neither was refused although their
        combined projection is 502. A ceiling belongs to the queue, not to an
        item, so the admitted item now holds a reservation and the second is
        refused with that reservation named.
        """
        receipt = self.install_receipt("near-gpu-ceiling")
        self._alpha_in_flight_with_beta_ready(receipt)

        rc, outcome = self.run_ready(receipt)

        self.assertEqual((rc, outcome["status"]), (6, "refused"))
        self.assertEqual(outcome["id"], "beta")
        self.assertIn("gpu_task_hours ceiling would be reached", outcome["reason"])
        self.assertIn("490 + 6 + 6 >= 500", outcome["reason"])
        self.assertIn("reserved by alpha", outcome["reason"])
        self.assertFalse((self.repo / "validator-ran").exists())
        # Exactly one of the two was admitted, and it is the one holding the
        # reservation the other was refused against.
        self.assertEqual(
            sorted(
                path.stem
                for path in (self.queue.state / "claims").glob("*.json")
            ),
            ["alpha"],
        )

    def test_a_ran_reservation_lives_until_a_receipt_remeasures_it(self) -> None:
        """The reviewer's mutation: 490 recorded, two six-hour items, alpha terminal.

        A terminal outcome released the reservation the instant it was written,
        while the same receipt stayed valid for 24 h -- so beta was admitted
        against accounting that had never looked at alpha, and actual spend can
        reach 502. R5 §3 counts a task in full however it ended and lets a job
        running at the stop finish with its spend counted, so what releases
        alpha's hours is the METER seeing them, not alpha stopping. Until a
        committed receipt is measured strictly after alpha's outcome, alpha keeps
        reserving its full declared maximum.
        """
        before = self.install_receipt(
            "near-gpu-ceiling", measured_at_utc="2026-09-29T06:00:00+00:00"
        )
        after = self.install_receipt(
            "near-gpu-ceiling", measured_at_utc="2026-09-29T10:00:00+00:00"
        )
        self._alpha_in_flight_with_beta_ready(before)
        self.finish_item("alpha", "2026-09-29T08:00:00+00:00")
        self.assertEqual(
            campaignctl.state_of(self.queue, self.queue.item("alpha")), "succeeded"
        )

        rc, outcome = self.run_ready(before)

        self.assertEqual(
            (rc, outcome["status"], outcome["id"]), (6, "refused", "beta")
        )
        self.assertIn("gpu_task_hours ceiling would be reached", outcome["reason"])
        self.assertIn("490 + 6 + 6 >= 500", outcome["reason"])
        self.assertIn(
            "reserved by alpha (terminal, not yet remeasured)", outcome["reason"]
        )
        self.assertFalse(self.queue.path("claims", "beta").exists())
        self.assertFalse((self.repo / "validator-ran").exists())

        # The reconciliation step: a receipt measured AFTER alpha's outcome is the
        # first accounting query that could have seen alpha's spend, so it -- and
        # only it -- releases the reservation.
        rc, outcome = self.run_ready(after)

        self.assertEqual(
            (rc, outcome["status"], outcome["id"]), (0, "succeeded", "beta")
        )
        self.assertTrue(self.queue.path("claims", "beta").exists())

    def test_an_item_that_never_ran_releases_its_reservation_at_once(self) -> None:
        """The opposite direction, or every reservation would be permanent.

        An item that never reached a claim has no spend for any receipt to
        account for, so revoked, refused, stale and never-claimed items release
        immediately. Only the run half waits for the meter.
        """
        receipt = self.install_receipt("near-gpu-ceiling")
        alpha_contract = self.six_hour_contract("alpha")
        beta_contract = self.six_hour_contract("beta")
        alpha = self.stage("alpha", kind="compute", contract=alpha_contract)
        self.approve(alpha)
        beta = self.stage("beta", kind="compute", contract=beta_contract)
        self.approve(beta)

        with mock.patch.dict(os.environ, {"CAMPAIGN_R5_RECEIPT": receipt}):
            held = campaignctl.r5_refusal_reason(
                self.queue, self.queue.item(beta["id"])
            )
        self.assertIn("reserved by alpha (approved)", str(held))

        campaignctl.revoke(self.queue, "alpha", interactive=False)
        self.assertEqual(
            campaignctl.state_of(self.queue, self.queue.item("alpha")), "revoked"
        )
        with mock.patch.dict(os.environ, {"CAMPAIGN_R5_RECEIPT": receipt}):
            self.assertIsNone(
                campaignctl.r5_refusal_reason(
                    self.queue, self.queue.item(beta["id"])
                )
            )

        rc, outcome = self.run_ready(receipt)

        self.assertEqual(
            (rc, outcome["status"], outcome["id"]), (0, "succeeded", "beta")
        )

    def test_a_refusal_before_the_claim_releases_its_reservation(self) -> None:
        """A refused item never spent, so it must not pin the ceiling for 24 h."""
        receipt = self.install_receipt("near-gpu-ceiling")
        alpha_contract = self.six_hour_contract("alpha")
        beta_contract = self.six_hour_contract("beta")
        alpha = self.stage("alpha", kind="compute", contract=alpha_contract)
        beta = self.stage("beta", kind="compute", contract=beta_contract)
        # `admit` refuses BEFORE the claim through exactly this call, so the fixture
        # is built by the producer of the record rather than restating its shape.
        campaignctl.write_outcome(
            self.queue, alpha, "refused", reason="fixture refusal", consumed=False
        )
        self.assertEqual(campaignctl.state_of(self.queue, alpha), "refused")
        self.assertFalse(self.queue.path("claims", "alpha").exists())

        with mock.patch.dict(os.environ, {"CAMPAIGN_R5_RECEIPT": receipt}):
            self.assertIsNone(
                campaignctl.r5_refusal_reason(
                    self.queue, self.queue.item(beta["id"])
                )
            )

    def test_only_the_canonical_state_dir_can_admit_compute(self) -> None:
        """The reviewer's mutation: two queues, one receipt, a six-hour item each.

        "Campaign-global" was scoped to whatever ``--state-dir`` named, so each
        queue took its own lock, scanned its own inventory, and admitted an item
        the other had never counted -- 490 recorded and 502 projected again, this
        time by splitting the queue instead of releasing a reservation. The
        canonical directory of the queue's own repository is the only one whose
        inventory can be complete, so it alone admits compute.
        """
        receipt = self.install_receipt("near-gpu-ceiling")
        alpha_contract = self.six_hour_contract("alpha")
        beta_contract = self.six_hour_contract("beta")
        other = self.other_queue()
        alpha = self.stage("alpha", kind="compute", contract=alpha_contract)
        self.approve(alpha)
        beta = self.stage(
            "beta", kind="compute", contract=beta_contract, queue=other
        )
        self.approve(beta, queue=other)

        rc, outcome = self.run_ready(receipt)

        self.assertEqual(
            (rc, outcome["status"], outcome["id"]), (0, "succeeded", "alpha")
        )

        with mock.patch.dict(os.environ, {"CAMPAIGN_R5_RECEIPT": receipt}):
            rc_other, outcome_other = campaignctl.run_ready(other)

        self.assertEqual((rc_other, outcome_other["status"]), (6, "refused"))
        self.assertEqual(outcome_other["id"], "beta")
        self.assertIn(
            "non-canonical state dir cannot admit compute", outcome_other["reason"]
        )
        self.assertFalse(other.path("claims", "beta").exists())
        # No lock is taken there either: a lock file in a second state directory
        # excludes nobody, so taking one would manufacture the appearance of an
        # exclusion it cannot provide.
        self.assertFalse((other.state / campaignctl.ADMISSION_LOCK_NAME).exists())

    def test_a_non_canonical_state_dir_still_runs_non_compute_items(self) -> None:
        """The refusal must act only where it was aimed: non-compute is unaffected."""
        other = self.other_queue()
        item = self.stage("one", queue=other)
        self.approve(item, queue=other)

        rc, outcome = campaignctl.run_ready(other)

        self.assertEqual((rc, outcome["status"]), (0, "succeeded"))
        self.assertEqual((self.repo / "ran").read_text(), "yes")
        self.assertTrue(other.path("claims", "one").exists())

    def test_two_canonical_queues_on_one_repo_share_the_admission_lock(self) -> None:
        """One repository has ONE campaign queue, so a second view of it is that queue.

        The state directory is compared after resolution, so a spelling with a
        ``..`` segment is the same queue and takes the same lock.
        """
        contract = self.write_contract(
            commit=True, validator_script="validator_success.py"
        )
        item = self.stage(
            "validator-failure-fixture", kind="compute", contract=contract
        )
        self.approve(item)
        twin = campaignctl.Queue(
            repo=self.repo,
            state=(
                self.repo
                / "docs"
                / "orchestration"
                / ".."
                / "orchestration"
                / "state"
                / "campaign-queue"
            ),
            clock=self.queue.clock,
        )
        self.assertTrue(twin.state_is_canonical())
        self.assertEqual(twin.state, self.queue.state)
        lock = twin.state / campaignctl.ADMISSION_LOCK_NAME
        lock.parent.mkdir(parents=True, exist_ok=True)
        lock.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "id": "another-item",
                    "owner": "twin-host:4242",
                    "acquired_at_utc": "2026-09-29T11:59:50+00:00",
                }
            )
        )

        rc, value = self.run_ready()

        self.assertEqual((rc, value["status"]), (5, "outcome-unknown"))
        self.assertIn("admission lock held by twin-host:4242", value["reason"])
        self.assertFalse(self.queue.path("claims", item["id"]).exists())
        self.assertFalse((self.repo / "ran").exists())

    def test_a_held_admission_lock_admits_nothing(self) -> None:
        """A concurrent lock holder means this ticker cannot know, so it claims nothing."""
        contract = self.write_contract(
            commit=True, validator_script="validator_success.py"
        )
        item = self.stage(
            "validator-failure-fixture", kind="compute", contract=contract
        )
        self.approve(item)
        lock = self.queue.state / campaignctl.ADMISSION_LOCK_NAME
        lock.parent.mkdir(parents=True, exist_ok=True)
        lock.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "id": "another-item",
                    "owner": "other-host:4242",
                    "acquired_at_utc": "2026-09-29T11:59:50+00:00",
                }
            )
        )

        rc, value = self.run_ready()

        self.assertEqual((rc, value["status"]), (5, "outcome-unknown"))
        self.assertIn("admission lock held by other-host:4242", value["reason"])
        self.assertFalse(self.queue.path("claims", item["id"]).exists())
        self.assertFalse(self.queue.path("outcomes", item["id"]).exists())
        self.assertFalse((self.repo / "ran").exists())
        self.assertTrue(lock.is_file())

    def test_an_undatable_admission_lock_is_treated_as_held(self) -> None:
        """A lock whose age cannot be read must not be resolved as old enough."""
        item = self.stage()
        self.approve(item)
        lock = self.queue.state / campaignctl.ADMISSION_LOCK_NAME
        lock.parent.mkdir(parents=True, exist_ok=True)
        lock.write_text("{ this is not json\n")

        rc, value = campaignctl.run_ready(self.queue)

        self.assertEqual((rc, value["status"]), (5, "outcome-unknown"))
        self.assertIn("cannot be dated", value["reason"])
        self.assertFalse(self.queue.path("claims", item["id"]).exists())
        self.assertTrue(lock.is_file())

    def test_a_stale_admission_lock_is_removed_after_logging(self) -> None:
        """The opposite direction: a lock no live run can still hold must not block."""
        contract = self.write_contract(
            commit=True, validator_script="validator_success.py"
        )
        item = self.stage(
            "validator-failure-fixture", kind="compute", contract=contract
        )
        self.approve(item)
        lock = self.queue.state / campaignctl.ADMISSION_LOCK_NAME
        lock.parent.mkdir(parents=True, exist_ok=True)
        # Six hours old against a 30 s timeout plus the contract's 2 h wall.
        lock.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "id": "abandoned-item",
                    "owner": "other-host:4242",
                    "acquired_at_utc": "2026-09-29T06:00:00+00:00",
                }
            )
        )

        rc, outcome = self.run_ready()

        self.assertEqual((rc, outcome["status"]), (0, "succeeded"))
        log = (
            self.queue.state / "logs" / campaignctl.ADMISSION_LOCK_LOG
        ).read_text()
        self.assertIn("stale-admission-lock-removed", log)
        self.assertIn("other-host:4242", log)
        self.assertFalse(lock.exists())

    def test_allow_in_the_producer_argv_is_refused_at_stage(self) -> None:
        """The reviewer's mutation, and why the guard cannot catch it itself.

        The control below is the guard's own positive control: given ``--allow``
        naming the outside checkout, the cross-tree import the guard exists to
        refuse resolves and the guard exits 0. A guarded arm carrying ``--allow``
        therefore establishes nothing, so the queue refuses the flag outright.
        """
        bypass = subprocess.run(
            [
                sys.executable,
                "nd-unfolding/mnv_guarded_run.py",
                "--expect-root",
                str(self.repo),
                "--allow",
                str(self.outside),
                "--",
                "sneaky_validator.py",
            ],
            cwd=self.repo,
            check=False,
        )
        self.assertEqual(bypass.returncode, 0)

        contract = self.write_contract(
            commit=True, validator_script="validator_success.py"
        )
        with self.assertRaisesRegex(
            campaignctl.QueueError,
            "compute producer command must not carry --allow",
        ):
            self.stage(
                "validator-failure-fixture",
                kind="compute",
                contract=contract,
                argv=self.guarded_argv("work.py", allow=str(self.outside)),
            )
        self.assertFalse(self.queue.path("items", "validator-failure-fixture").exists())

    def test_allow_in_the_validator_argv_is_refused_at_stage(self) -> None:
        contract = self.write_contract(
            commit=True,
            validator_argv=self.guarded_argv(
                "sneaky_validator.py", allow=str(self.outside)
            ),
        )

        with self.assertRaisesRegex(
            campaignctl.QueueError,
            "compute terminal validator command must not carry --allow",
        ):
            self.stage(
                "validator-failure-fixture", kind="compute", contract=contract
            )

    def test_allow_added_after_staging_is_refused_at_validate_unchanged(self) -> None:
        """The item JSON is state, not Git, so the argv is re-checked before the claim."""
        contract = self.write_contract(
            commit=True, validator_script="validator_success.py"
        )
        item = self.stage(
            "validator-failure-fixture", kind="compute", contract=contract
        )
        campaignctl.validate_unchanged(self.queue, item)

        producer_mutation = json.loads(json.dumps(item))
        argv = list(producer_mutation["argv"])
        argv[argv.index("--"): argv.index("--")] = ["--allow", str(self.outside)]
        producer_mutation["argv"] = argv
        producer_mutation["proposal_digest"] = campaignctl.digest(
            campaignctl.proposal_payload(producer_mutation)
        )
        campaignctl.atomic_json(
            self.queue.path("items", item["id"]), producer_mutation
        )
        with self.assertRaisesRegex(
            campaignctl.QueueError,
            "compute producer command must not carry --allow",
        ):
            campaignctl.validate_unchanged(
                self.queue, self.queue.item(item["id"])
            )
        with self.assertRaisesRegex(
            campaignctl.QueueError,
            "compute producer command must not carry --allow",
        ):
            self.approve(self.queue.item(item["id"]))

        validator_mutation = json.loads(json.dumps(item))
        terminal_validator = validator_mutation["campaign_contract"][
            "terminal_validator"
        ]
        validator_argv = list(terminal_validator["argv"])
        validator_argv[
            validator_argv.index("--"): validator_argv.index("--")
        ] = ["--allow", str(self.outside)]
        terminal_validator["argv"] = validator_argv
        validator_mutation["proposal_digest"] = campaignctl.digest(
            campaignctl.proposal_payload(validator_mutation)
        )
        campaignctl.atomic_json(
            self.queue.path("items", item["id"]), validator_mutation
        )
        with self.assertRaisesRegex(
            campaignctl.QueueError,
            "compute terminal validator command must not carry --allow",
        ):
            campaignctl.validate_unchanged(
                self.queue, self.queue.item(item["id"])
            )

    def named_contract(self, item_id: str, **kwargs: object) -> str:
        """Commit a contract whose ``campaign_id`` is ``item_id``.

        Each refusal test stages its own id, so a check that stops refusing
        fails on its own argv rather than on the item file a previous case left
        behind.
        """
        return self.write_contract(
            commit=True,
            name=f"contract-{item_id}.json",
            mutate=lambda value: value.update(campaign_id=item_id),
            **kwargs,
        )

    def test_a_foreign_expect_root_is_refused_on_both_arms(self) -> None:
        producer_contract = self.named_contract(
            "producer-arm", validator_script="validator_success.py"
        )
        with self.assertRaisesRegex(
            campaignctl.QueueError, "compute producer command must pass --expect-root"
        ):
            self.stage(
                "producer-arm",
                kind="compute",
                contract=producer_contract,
                argv=self.guarded_argv("work.py", expect_root=str(self.outside)),
            )

        validator_contract = self.named_contract(
            "validator-arm",
            validator_argv=self.guarded_argv(
                "validator_success.py", expect_root=str(self.outside)
            ),
        )
        with self.assertRaisesRegex(
            campaignctl.QueueError,
            "compute terminal validator command must pass --expect-root",
        ):
            self.stage(
                "validator-arm", kind="compute", contract=validator_contract
            )

    def test_interpreter_and_environment_escapes_are_refused(self) -> None:
        for index, (extra, expected) in enumerate(
            (
                (["-S"], "interpreter flag -S"),
                (["-I"], "interpreter flag -I"),
                (["-E"], "interpreter flag -E"),
                ([f"PYTHONPATH={self.outside}"], "PYTHON environment variable"),
                (["PYTHONSAFEPATH=0"], "PYTHON environment variable"),
                (["PYTHONNOUSERSITE=1"], "PYTHON environment variable"),
            )
        ):
            item_id = f"escape-{index}"
            contract = self.named_contract(
                item_id, validator_script="validator_success.py"
            )
            with self.subTest(extra=extra):
                with self.assertRaisesRegex(campaignctl.QueueError, expected):
                    self.stage(
                        item_id,
                        kind="compute",
                        contract=contract,
                        argv=self.guarded_argv("work.py", extra=extra),
                    )
                self.assertFalse(self.queue.path("items", item_id).exists())

    def test_the_guard_shim_is_bound_and_a_swap_refuses_before_execution(self) -> None:
        """The reviewer's mutation: replace ONLY the shim after staging.

        ``command_bindings`` bound the guard and the guarded target but not
        ``nd-unfolding/mnv_guard_shim/sitecustomize.py``, which is the file every
        inheriting Python child loads the guard through. Swapping it alone left the
        proposal digest, the guard and the target all intact, so a child could load
        the wrong tree and the run still returned 0. Bound, the shim obeys the
        guard's own rule and the item does not run at all.
        """
        contract = self.write_contract(
            commit=True, validator_script="validator_success.py"
        )
        item = self.stage(
            "validator-failure-fixture", kind="compute", contract=contract
        )
        self.approve(item)

        self.shim.write_text("import sys\nsys.path.insert(0, '/elsewhere')\n")

        # The observable consequence first, because that is what the mutation
        # produced: unbound, this tick returned 0 with the item run.
        rc, outcome = self.run_ready()

        self.assertEqual((rc, outcome["status"]), (4, "stale"))
        self.assertIn("mnv_guard_shim/sitecustomize.py", outcome["error"])
        self.assertFalse((self.repo / "ran").exists())
        self.assertFalse((self.repo / "validator-ran").exists())
        self.assertFalse(self.queue.path("claims", item["id"]).exists())

        with self.assertRaisesRegex(
            campaignctl.QueueError,
            r"bound file changed after staging: "
            r"nd-unfolding/mnv_guard_shim/sitecustomize\.py",
        ):
            campaignctl.validate_unchanged(self.queue, item)
        bound = {binding["path"] for binding in item["bindings"]}
        self.assertIn("nd-unfolding/mnv_guarded_run.py", bound)
        self.assertIn("nd-unfolding/mnv_guard_shim/sitecustomize.py", bound)

    def test_an_untracked_or_missing_guard_shim_is_refused_at_staging(self) -> None:
        """At staging the shim obeys the guard's rules too: tracked, then present."""
        subprocess.run(
            [
                "git",
                "-C",
                str(self.repo),
                "rm",
                "-q",
                "--cached",
                "nd-unfolding/mnv_guard_shim/sitecustomize.py",
            ],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(self.repo), "commit", "-qm", "untrack the shim"],
            check=True,
        )
        self.assertTrue(self.shim.is_file())
        untracked = self.named_contract(
            "untracked-shim", validator_script="validator_success.py"
        )

        with self.assertRaisesRegex(
            campaignctl.QueueError,
            r"must be committed at repository HEAD: "
            r"nd-unfolding/mnv_guard_shim/sitecustomize\.py",
        ):
            self.stage("untracked-shim", kind="compute", contract=untracked)
        self.assertFalse(self.queue.path("items", "untracked-shim").exists())

        self.shim.unlink()
        missing = self.named_contract(
            "missing-shim", validator_script="validator_success.py"
        )

        with self.assertRaisesRegex(
            campaignctl.QueueError, "requires the guard's subprocess shim"
        ):
            self.stage("missing-shim", kind="compute", contract=missing)
        self.assertFalse(self.queue.path("items", "missing-shim").exists())

    def test_a_clean_guarded_argv_is_accepted(self) -> None:
        """The refusals must stay silent on the argv a correct arm actually has."""
        contract = self.write_contract(
            commit=True, validator_script="validator_success.py"
        )
        item = self.stage(
            "validator-failure-fixture", kind="compute", contract=contract
        )
        self.assertIn("--expect-root", item["argv"])
        self.assertNotIn("--allow", item["argv"])
        campaignctl.validate_unchanged(self.queue, item)
        self.approve(item)

        rc, outcome = self.run_ready()

        self.assertEqual((rc, outcome["status"]), (0, "succeeded"))



class MeterReceiptInteroperability(unittest.TestCase):
    """The receipt r5_meter.py actually writes is the receipt campaignctl reads."""

    def test_a_receipt_measured_by_r5_meter_is_accepted(self) -> None:
        import r5_meter

        fixture = Path(campaignctl.__file__).resolve().parent / "test_fixtures_r5_meter" / "mixed.sacct"
        with tempfile.TemporaryDirectory() as directory:
            receipt_path = Path(directory) / "receipt.json"
            rc = r5_meter.main(
                [
                    "measure",
                    "--from-file", str(fixture),
                    "--now", "2026-09-10T00:00:00Z",
                    "--write", str(receipt_path),
                ]
            )
            self.assertEqual(rc, 0)
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        validated = campaignctl.validate_r5_receipt(receipt)
        self.assertEqual(validated["fired"]["any"], False)
        self.assertTrue(str(validated["unit"]).startswith("task-hours"))

    def test_both_modules_pin_the_same_ruled_instant_and_record(self) -> None:
        """The pinned R5 constants are one ruling, so they must not drift apart."""
        import r5_meter

        self.assertEqual(campaignctl.R5_T0, r5_meter.T0_UTC)
        self.assertEqual(campaignctl.R5_STOP_DATE, r5_meter.STOP_DATE_UTC)
        self.assertEqual(campaignctl.R5_DECISION_RECORD, r5_meter.DECISION_RECORD)

if __name__ == "__main__":
    unittest.main()
