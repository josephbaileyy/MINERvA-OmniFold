import json
import os
import subprocess
import sys
import tempfile
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
        guard.write_text(
            "import runpy\n"
            "import sys\n"
            "separator = sys.argv.index('--')\n"
            "script = sys.argv[separator + 1]\n"
            "sys.argv = [script, *sys.argv[separator + 2:]]\n"
            "runpy.run_path(script, run_name='__main__')\n"
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
        subprocess.run(
            [
                "git",
                "-C",
                str(self.repo),
                "add",
                "work.py",
                "validator_failure.py",
                "validator_success.py",
                "timeout.py",
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
            argv = [
                sys.executable,
                "nd-unfolding/mnv_guarded_run.py",
                "--expect-root",
                str(self.repo),
                "--",
                target,
            ]
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

    def write_contract(
        self,
        *,
        commit: bool = False,
        validator_script: str = "validator_failure.py",
        mutate: Callable[[dict[str, object]], None] | None = None,
    ) -> str:
        contract = json.loads(CONTRACT_FIXTURE.read_text())
        terminal_validator = contract["terminal_validator"]
        assert isinstance(terminal_validator, dict)
        terminal_validator["argv"] = [sys.executable, validator_script]
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
        with mock.patch.dict(
            os.environ,
            {"CAMPAIGN_R5_RECEIPT": str(R5_FIXTURES[receipt])},
        ):
            return campaignctl.run_ready(self.queue)

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

if __name__ == "__main__":
    unittest.main()
