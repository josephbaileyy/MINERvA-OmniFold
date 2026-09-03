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
    for name in ("healthy", "stale", "fired", "headroom-exhausting", "malformed")
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
            ],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(self.repo), "commit", "-qm", "initial"],
            check=True,
        )
        self.queue = campaignctl.Queue(
            repo=self.repo,
            state=self.root / "state",
            clock=lambda: "2026-09-29T12:00:00+00:00",
        )

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
    ) -> dict:
        target = script or "work.py"
        argv = [sys.executable, target]
        if kind == "compute" and guarded:
            argv = self.guarded_argv(target)
        return campaignctl.stage(
            self.queue,
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

    def guarded_argv(self, target: str) -> list[str]:
        """Return the argv a compute command must have: routed through the guard."""
        return [
            sys.executable,
            "nd-unfolding/mnv_guarded_run.py",
            "--expect-root",
            str(self.repo),
            "--",
            target,
        ]

    def write_contract(
        self,
        *,
        commit: bool = False,
        validator_script: str = "validator_failure.py",
        guarded_validator: bool = True,
        mutate: Callable[[dict[str, object]], None] | None = None,
    ) -> str:
        contract = json.loads(CONTRACT_FIXTURE.read_text())
        terminal_validator = contract["terminal_validator"]
        assert isinstance(terminal_validator, dict)
        terminal_validator["argv"] = (
            self.guarded_argv(validator_script)
            if guarded_validator
            else [sys.executable, validator_script]
        )
        if mutate is not None:
            mutate(contract)
        path = self.repo / "campaign-contract.json"
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

    def approve(self, item: dict[str, object]) -> dict:
        return campaignctl.approve(
            self.queue, item["id"], item["proposal_digest"], interactive=False
        )

    def run_ready(
        self, receipt: str = "healthy"
    ) -> tuple[int, dict[str, object]]:
        path = R5_FIXTURES.get(receipt, Path(receipt))
        with mock.patch.dict(os.environ, {"CAMPAIGN_R5_RECEIPT": str(path)}):
            return campaignctl.run_ready(self.queue)

    def mutated_receipt(self, **changes: object) -> str:
        """Write the healthy receipt with fields replaced, and return its path.

        Parameters
        ----------
        **changes : object
            Receipt fields to overwrite, named exactly as the meter writes them.

        Returns
        -------
        str
            Path to the mutated receipt, outside the fixture directory so the
            checked-in receipts keep the ruled values.
        """
        receipt = json.loads(R5_FIXTURES["healthy"].read_text())
        receipt.update(changes)
        path = self.root / f"receipt-{len(list(self.root.glob('receipt-*.json')))}.json"
        path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
        return str(path)

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

        rc, outcome = self.run_ready("malformed")
        self.assertEqual((rc, outcome["status"]), (6, "refused"))
        self.assertIn("R5 receipt malformed", outcome["reason"])
        self.assertFalse(self.queue.path("claims", item["id"]).exists())

        rc, outcome = self.run_ready("healthy")
        self.assertEqual((rc, outcome["status"]), (0, "succeeded"))
        self.assertTrue((self.repo / "ran").is_file())

    def test_stale_r5_receipt_refuses_compute(self) -> None:
        self._assert_r5_refusal("stale", "R5 receipt stale")

    def test_fired_r5_receipt_refuses_compute(self) -> None:
        self._assert_r5_refusal("fired", "R5 stop fired")

    def test_r5_stop_date_refuses_compute(self) -> None:
        self.queue.clock = lambda: "2026-09-30T00:00:00+00:00"
        self._assert_r5_refusal("healthy", "R5 stop date reached")

    def test_r5_projected_inclusive_ceiling_refuses_compute(self) -> None:
        self._assert_r5_refusal(
            "headroom-exhausting", "gpu_task_hours ceiling would be reached"
        )

    def test_r5_receipt_metered_from_another_t0_refuses_compute(self) -> None:
        """The reviewer's mutation: midnight instead of the ruled commit instant.

        ``r5_meter`` refuses that receipt and campaignctl accepted it, so the two
        modules disagreed about which interval had been metered.
        """
        self._assert_r5_refusal(
            self.mutated_receipt(t0_utc="2026-09-02T00:00:00+00:00"),
            "t0_utc does not match the ruled instant",
        )

    def test_r5_receipt_naming_another_decision_record_refuses_compute(self) -> None:
        self._assert_r5_refusal(
            # A plausibly shaped record that is not the ruling this stop comes
            # from. Deliberately not the path of any real document, so the
            # manifest does not read this mutation as a reference to one.
            self.mutated_receipt(
                decision_record=(
                    "docs/orchestration/DECISION-20260902-some-other-ruling.md"
                )
            ),
            "decision_record does not match the ruling record",
        )

    def test_future_dated_r5_receipt_refuses_compute(self) -> None:
        """A receipt dated one day after the queue clock was accepted as fresh."""
        self._assert_r5_refusal(
            self.mutated_receipt(measured_at_utc="2026-09-30T12:00:00+00:00"),
            "receipt is dated in the future",
        )

    def test_r5_receipt_inside_the_tolerated_skew_allows_compute(self) -> None:
        """The future check must stay silent on the skew a correct run can show."""
        contract = self.write_contract(
            commit=True,
            validator_script="validator_success.py",
        )
        item = self.stage(
            "validator-failure-fixture", kind="compute", contract=contract
        )
        self.approve(item)

        rc, outcome = self.run_ready(
            self.mutated_receipt(measured_at_utc="2026-09-29T12:00:30+00:00")
        )

        self.assertEqual((rc, outcome["status"]), (0, "succeeded"))

    def test_healthy_r5_receipt_allows_compute(self) -> None:
        contract = self.write_contract(
            commit=True,
            validator_script="validator_success.py",
        )
        item = self.stage(
            "validator-failure-fixture", kind="compute", contract=contract
        )
        self.approve(item)

        rc, outcome = self.run_ready("healthy")

        self.assertEqual((rc, outcome["status"]), (0, "succeeded"))

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
