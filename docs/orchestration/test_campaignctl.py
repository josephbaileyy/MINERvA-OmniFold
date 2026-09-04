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
#: Where the checked-in fixture contract says the producer writes its scheduler task
#: identities. Read from the fixture rather than retyped, so a contract change cannot
#: leave the producer scripts writing to a path nothing reads.
TASK_IDS_RELATIVE = json.loads(CONTRACT_FIXTURE.read_text())["accounting"][
    "task_ids_file"
]
#: The identities the fixture producers declare. Deliberately absent from every
#: checked-in receipt fixture's `metered_task_ids`, so a receipt only counts them when
#: a test puts them there.
PRODUCER_TASK_IDS = ["7001_0"]
#: Producer prologue: the scheduler task identities an arm reports. The real producer
#: writes these from its sbatch output; here they are literal, and the file is what
#: campaignctl reads between the producer and the validator.
def write_task_ids(task_ids: list[str], *, relative: str = TASK_IDS_RELATIVE) -> str:
    """Return producer source that writes ``task_ids`` to the declared path."""
    return (
        "from pathlib import Path\n"
        f"_ids = Path({relative!r})\n"
        "_ids.parent.mkdir(parents=True, exist_ok=True)\n"
        f"_ids.write_text({json.dumps(json.dumps(task_ids))})\n"
    )


class CampaignQueueTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="campaign-queue-test.")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        # Production derives the canonical root from the passwd database. Patch the
        # one lookup seam so tests never read or write the operator's actual queue.
        self.passwd_home = self.root / "passwd-home"
        passwd_home = mock.patch.object(
            campaignctl, "_passwd_home", return_value=self.passwd_home
        )
        passwd_home.start()
        self.addCleanup(passwd_home.stop)
        self.state_root = self.passwd_home / campaignctl.CAMPAIGN_STATE_ROOT_NAME
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
            + write_task_ids(PRODUCER_TASK_IDS)
        )
        guard = self.repo / "nd-unfolding" / "mnv_guarded_run.py"
        guard.parent.mkdir()
        guard.write_bytes(REAL_GUARD.read_bytes())
        # The guard refuses to install (COULD NOT LOOK, exit 2) unless its tracked subprocess
        # shim sits beside it, so the fixture checkout carries the shim as the real one does.
        # It is COMMITTED like the guard below, because the shim is the guard's enforcing half
        # in every inheriting child and the queue binds it under the guard's own rules.
        shim_dir = guard.parent / "mnv_guard_shim"
        (shim_dir / "bin").mkdir(parents=True, exist_ok=True)
        real_shim_dir = REAL_GUARD.parent / "mnv_guard_shim"
        for rel in ("sitecustomize.py", "scan_argv.py", "bin/python3", "bin/python"):
            source = real_shim_dir / rel
            target = shim_dir / rel
            target.write_bytes(source.read_bytes())
            target.chmod(source.stat().st_mode & 0o777)
        self.shim = shim_dir / "sitecustomize.py"
        self.path_wrapper = shim_dir / "bin" / "python3"
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
        # Both slow producers declare their task ids BEFORE they sleep, which is what
        # a real arm does: `sbatch` returns the ids long before the tasks end. A
        # producer that is killed before writing them is a separate case, and it has
        # its own test.
        self.timeout_script = self.repo / "timeout.py"
        self.timeout_script.write_text(
            write_task_ids(PRODUCER_TASK_IDS) + "import time\ntime.sleep(2)\n"
        )
        self.brief_script = self.repo / "brief_producer.py"
        self.brief_script.write_text(
            write_task_ids(PRODUCER_TASK_IDS) + "import time\ntime.sleep(0.4)\n"
        )
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
                "nd-unfolding/mnv_guard_shim/scan_argv.py",
                "nd-unfolding/mnv_guard_shim/bin/python3",
                "nd-unfolding/mnv_guard_shim/bin/python",
            ],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(self.repo), "commit", "-qm", "initial"],
            check=True,
        )
        # Compute is admissible only from the CANONICAL state directory, which is now
        # outside every checkout: the queue takes its default state directory rather
        # than being pointed at one, exactly as a ticker does.
        self.queue = campaignctl.Queue(
            repo=self.repo,
            clock=lambda: "2026-09-29T12:00:00+00:00",
        )
        self.assertTrue(self.queue.state_is_canonical())
        self.assertFalse(
            str(self.queue.state).startswith(str(self.repo) + os.sep),
            "the canonical queue must not live inside a checkout",
        )
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
        queue = queue or self.queue
        target = script or "work.py"
        if argv is None:
            argv = [sys.executable, target]
            if kind == "compute" and guarded:
                # `--expect-root` names the QUEUE'S repository, which for a clone is
                # the clone: one campaign-global queue serves several checkouts.
                argv = self.guarded_argv(target, expect_root=str(queue.repo))
        return campaignctl.stage(
            queue,
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

        This is one half of the reviewer's mutation: one repository, one committed
        receipt, and a second "campaign-global" lock and inventory that the
        canonical queue cannot see. The helper asserts nothing about
        ``state_is_canonical``: a precondition check here would refuse the
        mutation before it reached the behaviour the test is about.
        """
        return campaignctl.Queue(
            repo=self.repo, state=self.root / name, clock=self.queue.clock
        )

    def clone_queue(self, name: str = "clone") -> campaignctl.Queue:
        """Clone the fixture repository and return a queue serving the clone.

        This is the other half of the reviewer's mutation, and the one a
        per-checkout queue could not survive: `git clone` gives a second checkout
        with the SAME commits -- the same receipt, the same contracts, the same
        `HEAD` -- and therefore, under the old rule, a second directory that its
        own ticker considered canonical. The returned queue takes the DEFAULT
        state directory, so if the canonical directory is still derived from the
        repository this queue silently gets one of its own.
        """
        target = self.root / name
        subprocess.run(
            ["git", "clone", "-q", str(self.repo), str(target)], check=True
        )
        for key, value in (("user.email", "test@example.invalid"), ("user.name", "Test")):
            subprocess.run(
                ["git", "-C", str(target), "config", key, value], check=True
            )
        return campaignctl.Queue(repo=target, clock=self.queue.clock)

    def commit_script(self, name: str, body: str) -> str:
        """Write and commit a producer script, returning its repository path.

        Committing moves `HEAD`, so call this BEFORE staging anything: an item
        staged against an earlier `HEAD` is `stale` by the drift rule.
        """
        path = self.repo / name
        path.write_text(body)
        subprocess.run(["git", "-C", str(self.repo), "add", name], check=True)
        subprocess.run(
            ["git", "-C", str(self.repo), "commit", "-qm", f"add {name}"], check=True
        )
        return name

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
        repo: Path | None = None,
    ) -> str:
        """Write, and optionally commit, a contract into ``repo``.

        ``repo`` defaults to the fixture checkout. A contract belongs to ONE
        checkout -- its guard argv names that checkout by absolute path -- so a
        second checkout gets its own contract rather than a copy of this one's,
        which is also what a real clone would need.
        """
        repo = repo or self.repo
        contract = json.loads(CONTRACT_FIXTURE.read_text())
        terminal_validator = contract["terminal_validator"]
        assert isinstance(terminal_validator, dict)
        if validator_argv is not None:
            terminal_validator["argv"] = validator_argv
        else:
            terminal_validator["argv"] = (
                self.guarded_argv(validator_script, expect_root=str(repo))
                if guarded_validator
                else [sys.executable, validator_script]
            )
        if mutate is not None:
            mutate(contract)
        path = repo / name
        path.write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n")
        if commit:
            subprocess.run(["git", "-C", str(repo), "add", path.name], check=True)
            subprocess.run(
                ["git", "-C", str(repo), "commit", "-qm", "add contract"],
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

    def install_counting_receipt(
        self, source: str, task_ids: list[str], **changes: object
    ) -> str:
        """Commit a receipt whose ``spend`` COUNTS ``task_ids``.

        Only the identity columns move: the metered hours stay exactly as the
        fixture recorded them, because the reviewer's mutation is a receipt that
        reports the SAME spend and still releases a reservation. What changes
        between the two receipts in those tests is only whether the item's tasks
        are among the rows the meter counted.
        """
        spend = dict(json.loads(R5_FIXTURES[source].read_text())["spend"])
        identities = sorted(set(spend["metered_task_ids"]) | set(task_ids))
        spend["metered_task_ids"] = identities
        spend["task_count"] = len(identities)
        spend["by_state"] = {"COMPLETED": len(identities)}
        return self.install_receipt(source, spend=spend, **changes)

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
        expected_identity = {
            "state_dir": str(self.queue.state),
            "uid": os.getuid(),
            "hostname": campaignctl.socket.gethostname(),
        }
        claim = campaignctl.read_object(self.queue.path("claims", item["id"]))
        for field, expected in expected_identity.items():
            self.assertEqual(claim[field], expected)
            self.assertEqual(outcome[field], expected)

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
        # Both commands are mocked, so the STAND-IN producer writes the task-ids
        # file the real one would: it is written inside the fake call rather than
        # beforehand, because the queue removes any earlier copy before the
        # producer starts, and without it the accounting refusal would preempt the
        # launch failure this test is about.
        declared = self.repo / TASK_IDS_RELATIVE
        calls: list[list[str]] = []

        def command(argv: list[str], **_: object) -> tuple[int | None, str | None]:
            calls.append(list(argv))
            if len(calls) == 1:
                declared.parent.mkdir(parents=True, exist_ok=True)
                declared.write_text(json.dumps(PRODUCER_TASK_IDS))
                return 0, None
            return None, "command could not be started"

        with mock.patch.object(
            campaignctl, "run_logged_command", side_effect=command
        ):
            rc, outcome = self.run_ready()

        self.assertEqual((rc, outcome["status"]), (3, "failed"))
        self.assertEqual(outcome["producer_returncode"], 0)
        self.assertIsNone(outcome["validator_returncode"])
        self.assertEqual(outcome["terminal_branch"], "unexpected-terminal-result")
        self.assertEqual(
            outcome[campaignctl.OUTCOME_TASK_IDS_FIELD], PRODUCER_TASK_IDS
        )

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

    def six_hour_contract(self, campaign_id: str, repo: Path | None = None) -> str:
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
            repo=repo,
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

    def _alpha_ran_with_beta_ready(self, receipt: str) -> None:
        """Run a six-hour item to a REAL terminal outcome, then ready a second one.

        Alpha is executed by the queue rather than handed a written outcome, so the
        ``scheduler_task_ids`` the release rule reads are the ids alpha's own
        producer declared and campaignctl actually recorded. Both contracts are
        committed before anything is staged, because a contract commit moves
        ``HEAD`` and an item staged against an earlier one is ``stale``.
        """
        alpha_contract = self.six_hour_contract("alpha")
        beta_contract = self.six_hour_contract("beta")
        alpha = self.stage("alpha", kind="compute", contract=alpha_contract)
        self.approve(alpha)

        rc, outcome = self.run_ready(receipt)

        self.assertEqual(
            (rc, outcome["status"], outcome["id"]), (0, "succeeded", "alpha")
        )
        self.assertEqual(
            outcome[campaignctl.OUTCOME_TASK_IDS_FIELD], PRODUCER_TASK_IDS
        )
        beta = self.stage("beta", kind="compute", contract=beta_contract)
        self.approve(beta)

    def test_a_ran_reservation_lives_until_a_receipt_remeasures_it(self) -> None:
        """490 recorded, two six-hour items, alpha terminal: the timestamp half.

        A terminal outcome released the reservation the instant it was written,
        while the same receipt stayed valid for 24 h -- so beta was admitted
        against accounting that had never looked at alpha, and actual spend can
        reach 502. R5 §3 counts a task in full however it ended and lets a job
        running at the stop finish with its spend counted, so what releases
        alpha's hours is the METER seeing them, not alpha stopping.
        """
        receipt = self.install_receipt("near-gpu-ceiling")
        self._alpha_ran_with_beta_ready(receipt)
        self.assertEqual(
            campaignctl.state_of(self.queue, self.queue.item("alpha")), "succeeded"
        )
        # The admitting receipt was measured at the same instant alpha's outcome was
        # recorded, so the meter cannot have seen alpha's final spend.
        self.assertEqual(
            campaignctl.terminal_outcome_instant(self.queue, "alpha"),
            campaignctl.parse_utc(
                json.loads((self.repo / receipt).read_text())["measured_at_utc"],
                field="fixture receipt",
            ),
        )

        rc, outcome = self.run_ready(receipt)

        self.assertEqual(
            (rc, outcome["status"], outcome["id"]), (6, "refused", "beta")
        )
        self.assertIn("gpu_task_hours ceiling would be reached", outcome["reason"])
        self.assertIn("490 + 6 + 6 >= 500", outcome["reason"])
        self.assertIn(
            "reserved by alpha (terminal, not yet remeasured)", outcome["reason"]
        )
        self.assertFalse(self.queue.path("claims", "beta").exists())

    def test_a_later_receipt_that_never_counted_the_item_releases_nothing(
        self,
    ) -> None:
        """The reviewer's mutation: a FRESH receipt still reporting 490 admitted beta.

        Release was decided by the timestamp alone, so a receipt taken after
        alpha's outcome -- still reporting 490 GPU task-hours, still listing only
        the three tasks it listed before -- released alpha's six hours and beta ran:
        502 against a ceiling of 500, under a measurement that had demonstrably not
        counted alpha. A later ``measured_at_utc`` proves the meter RAN; only
        ``spend.metered_task_ids`` proves it counted THESE tasks. So the receipt
        must list every identity alpha's outcome recorded, and the refusal names
        alpha with the ids that are missing.
        """
        admitting = self.install_receipt("near-gpu-ceiling")
        uncounted = self.install_receipt(
            "near-gpu-ceiling", measured_at_utc="2026-09-29T12:00:30+00:00"
        )
        counting = self.install_counting_receipt(
            "near-gpu-ceiling",
            PRODUCER_TASK_IDS,
            measured_at_utc="2026-09-29T12:00:30+00:00",
        )
        self._alpha_ran_with_beta_ready(admitting)
        # The timestamp clause is SATISFIED by the mutation's receipt, so what
        # refuses beta below can only be the inclusion clause.
        uncounted_receipt = json.loads((self.repo / uncounted).read_text())
        self.assertGreater(
            campaignctl.parse_utc(
                uncounted_receipt["measured_at_utc"], field="fixture receipt"
            ),
            campaignctl.terminal_outcome_instant(self.queue, "alpha"),
        )
        self.assertEqual(uncounted_receipt["spend"]["gpu_task_hours"], 490.0)
        self.assertNotIn(
            PRODUCER_TASK_IDS[0], uncounted_receipt["spend"]["metered_task_ids"]
        )

        rc, outcome = self.run_ready(uncounted)

        self.assertEqual(
            (rc, outcome["status"], outcome["id"]), (6, "refused", "beta")
        )
        self.assertIn("gpu_task_hours ceiling would be reached", outcome["reason"])
        self.assertIn("490 + 6 + 6 >= 500", outcome["reason"])
        self.assertIn(
            f"reserved by alpha (ran, task ids not yet in a receipt: "
            f"{PRODUCER_TASK_IDS[0]})",
            outcome["reason"],
        )
        self.assertFalse(self.queue.path("claims", "beta").exists())

        # The reconciliation step, and the direction that must NOT be refused: the
        # same hours, the same instant, alpha's ids among the metered identities.
        rc, outcome = self.run_ready(counting)

        self.assertEqual(
            (rc, outcome["status"], outcome["id"]), (0, "succeeded", "beta")
        )
        self.assertTrue(self.queue.path("claims", "beta").exists())

    def test_an_item_expecting_no_tasks_releases_on_the_timestamp_alone(self) -> None:
        """An arm that schedules nothing has no identity for a receipt to list.

        Requiring inclusion for every item would make ``expects_scheduler_tasks``
        false unsatisfiable: the producer correctly reports no tasks, no receipt can
        ever list them, and the item would reserve its declared maximum forever. So
        for a declared-no-tasks arm the timestamp is the whole test -- and the empty
        file is still REQUIRED, because "scheduled nothing" and "never wrote its
        ids" are different facts.
        """
        empty_producer = self.commit_script(
            "no_task_producer.py",
            write_task_ids([]) + "from pathlib import Path\n"
            "Path('ran').write_text('yes')\n",
        )
        admitting = self.install_receipt("near-gpu-ceiling")
        later = self.install_receipt(
            "near-gpu-ceiling", measured_at_utc="2026-09-29T12:00:30+00:00"
        )

        def declare_no_tasks(value: dict[str, object]) -> None:
            value["campaign_id"] = "alpha"
            value["maximum_cost"] = {
                "cpu_task_hours": 1.0,
                "gpu_task_hours": 6.0,
                "wall_hours": 6.0,
            }
            accounting = value["accounting"]
            assert isinstance(accounting, dict)
            accounting["expects_scheduler_tasks"] = False

        alpha_contract = self.write_contract(
            commit=True,
            validator_script="validator_success.py",
            name="contract-alpha.json",
            mutate=declare_no_tasks,
        )
        beta_contract = self.six_hour_contract("beta")
        alpha = self.stage(
            "alpha", kind="compute", contract=alpha_contract, script=empty_producer
        )
        self.approve(alpha)

        rc, outcome = self.run_ready(admitting)

        self.assertEqual((rc, outcome["status"]), (0, "succeeded"))
        self.assertEqual(outcome[campaignctl.OUTCOME_TASK_IDS_FIELD], [])
        beta = self.stage("beta", kind="compute", contract=beta_contract)
        self.approve(beta)

        rc, outcome = self.run_ready(later)

        self.assertEqual(
            (rc, outcome["status"], outcome["id"]), (0, "succeeded", "beta")
        )

    def test_a_missing_task_ids_file_refuses_and_reserves_permanently(self) -> None:
        """A producer whose ids were never written can never be accounted for.

        This is the reviewer's third case -- crashed before the file was read,
        launcher error, timeout. The validator is not started, the outcome resolves
        through the contract's own ``otherwise`` branch with the reason recorded,
        and because no identity was recorded no receipt can ever demonstrate that
        this item's spend was counted. The reservation is therefore PERMANENT, in
        both directions: a fresh receipt listing every other task does not clear it.
        """
        silent_producer = self.commit_script(
            "silent_producer.py",
            "from pathlib import Path\nPath('ran').write_text('yes')\n",
        )
        admitting = self.install_receipt("near-gpu-ceiling")
        counting = self.install_counting_receipt(
            "near-gpu-ceiling",
            PRODUCER_TASK_IDS,
            measured_at_utc="2026-09-29T12:00:30+00:00",
        )
        alpha_contract = self.six_hour_contract("alpha")
        beta_contract = self.six_hour_contract("beta")
        alpha = self.stage(
            "alpha", kind="compute", contract=alpha_contract, script=silent_producer
        )
        self.approve(alpha)

        rc, outcome = self.run_ready(admitting)

        self.assertEqual((rc, outcome["status"], outcome["id"]), (3, "failed", "alpha"))
        self.assertEqual(outcome["producer_returncode"], 0)
        self.assertIsNone(outcome["validator_returncode"])
        self.assertEqual(outcome["terminal_branch"], "unexpected-terminal-result")
        self.assertEqual(outcome["required_actions"][0]["action"], "preserve")
        self.assertIn(
            "was not written by the producer",
            outcome[campaignctl.OUTCOME_ACCOUNTING_ERROR_FIELD],
        )
        self.assertNotIn(campaignctl.OUTCOME_TASK_IDS_FIELD, outcome)
        self.assertFalse((self.repo / "validator-ran").exists())

        beta = self.stage("beta", kind="compute", contract=beta_contract)
        self.approve(beta)

        rc, outcome = self.run_ready(counting)

        self.assertEqual(
            (rc, outcome["status"], outcome["id"]), (6, "refused", "beta")
        )
        self.assertIn(
            "reserved by alpha (ran with no recorded task ids; operator release "
            "required)",
            outcome["reason"],
        )

    def test_an_operator_release_clears_an_unaccountable_reservation(self) -> None:
        """The only way out of a permanent hold, and it is a human act.

        ``release`` is refused without a TTY, refused for an item that never ran
        (that is ``revoke``'s job) and refused while an item may still be spending;
        it records the operator's reason and logs the release. Only then does the
        next item get the hours.
        """
        silent_producer = self.commit_script(
            "silent_producer.py",
            "from pathlib import Path\nPath('ran').write_text('yes')\n",
        )
        # Measured AFTER the outcome this run will write, so the timestamp clause is
        # satisfied and the hold under test is the unidentifiable-spend one.
        receipt = self.install_receipt(
            "near-gpu-ceiling", measured_at_utc="2026-09-29T12:00:30+00:00"
        )
        alpha_contract = self.six_hour_contract("alpha")
        beta_contract = self.six_hour_contract("beta")
        alpha = self.stage(
            "alpha", kind="compute", contract=alpha_contract, script=silent_producer
        )
        self.approve(alpha)
        self.assertEqual(self.run_ready(receipt)[0], 3)
        beta = self.stage("beta", kind="compute", contract=beta_contract)
        self.approve(beta)
        with mock.patch.dict(os.environ, {"CAMPAIGN_R5_RECEIPT": receipt}):
            self.assertIn(
                "operator release required",
                str(
                    campaignctl.r5_refusal_reason(
                        self.queue, self.queue.item(beta["id"])
                    )
                ),
            )

        with self.assertRaisesRegex(campaignctl.QueueError, "never claimed"):
            campaignctl.release(
                self.queue, "beta", "beta never ran", interactive=False
            )
        with self.assertRaisesRegex(campaignctl.QueueError, "release reason"):
            campaignctl.release(self.queue, "alpha", "   ", interactive=False)
        with mock.patch.object(
            campaignctl.sys.stdin, "isatty", return_value=False
        ):
            with self.assertRaisesRegex(
                campaignctl.QueueError, "release requires an interactive TTY"
            ):
                campaignctl.release(self.queue, "alpha", "carrying the spend")

        record = campaignctl.release(
            self.queue,
            "alpha",
            "sacct shows no tasks for this arm; carrying the six hours",
            interactive=False,
        )

        self.assertEqual(record["state_at_release"], "failed")
        self.assertIn("carrying the six hours", record["reason"])
        log = (
            self.queue.state / "logs" / campaignctl.ADMISSION_LOCK_LOG
        ).read_text()
        self.assertIn("reservation-released", log)
        self.assertIn("alpha", log)

        rc, outcome = self.run_ready(receipt)

        self.assertEqual(
            (rc, outcome["status"], outcome["id"]), (0, "succeeded", "beta")
        )

    def test_a_task_ids_file_disagreeing_with_the_declaration_is_refused(self) -> None:
        """Empty while tasks are expected, populated while they are not, malformed.

        Each is a refusal with the reason recorded, and none of them runs the
        validator: the ids are what makes the spend identifiable, so a run that
        cannot report them honestly must not be able to reach a pass branch.
        """
        cases = (
            ("empty-while-expected", write_task_ids([]), True, "is empty while"),
            (
                "tasks-while-none-expected",
                write_task_ids(PRODUCER_TASK_IDS),
                False,
                "lists scheduler tasks while",
            ),
            (
                "not-json",
                "from pathlib import Path\n"
                f"_ids = Path({TASK_IDS_RELATIVE!r})\n"
                "_ids.parent.mkdir(parents=True, exist_ok=True)\n"
                "_ids.write_text('{ not json')\n",
                True,
                "is not JSON",
            ),
            (
                "not-a-task-identity",
                write_task_ids(["not-a-task-id"]),
                True,
                "not a scheduler task identity",
            ),
        )
        for item_id, body, expects, expected in cases:
            with self.subTest(case=item_id):
                producer = self.commit_script(f"{item_id}_producer.py", body)

                def declare(value: dict[str, object], expects: bool = expects) -> None:
                    value["campaign_id"] = item_id
                    accounting = value["accounting"]
                    assert isinstance(accounting, dict)
                    accounting["expects_scheduler_tasks"] = expects

                contract = self.write_contract(
                    commit=True,
                    validator_script="validator_success.py",
                    name=f"contract-{item_id}.json",
                    mutate=declare,
                )
                item = self.stage(
                    item_id, kind="compute", contract=contract, script=producer
                )
                self.approve(item)

                rc, outcome = self.run_ready()

                self.assertEqual((rc, outcome["status"]), (3, "failed"))
                self.assertEqual(
                    outcome["terminal_branch"], "unexpected-terminal-result"
                )
                self.assertIn(
                    expected, outcome[campaignctl.OUTCOME_ACCOUNTING_ERROR_FIELD]
                )
                self.assertNotIn(campaignctl.OUTCOME_TASK_IDS_FIELD, outcome)
                self.assertFalse((self.repo / "validator-ran").exists())

    def test_an_earlier_runs_task_ids_are_never_credited_to_this_item(self) -> None:
        """A stale file at the declared path would release on somebody else's spend.

        The path is declared by the contract, so two items can name the same one --
        and the ids in it are what release a reservation. Left in place, an item
        whose producer wrote nothing would inherit the previous item's identities
        and release against spend that was never its own. The file is this run's
        output, so the queue removes any earlier copy before the producer starts.
        """
        silent_producer = self.commit_script(
            "silent_producer.py",
            "from pathlib import Path\nPath('ran').write_text('yes')\n",
        )
        receipt = self.install_receipt("near-gpu-ceiling")
        contract = self.named_contract(
            "stale-ids", validator_script="validator_success.py"
        )
        stale = self.repo / TASK_IDS_RELATIVE
        stale.parent.mkdir(parents=True, exist_ok=True)
        stale.write_text(json.dumps(PRODUCER_TASK_IDS))
        item = self.stage(
            "stale-ids", kind="compute", contract=contract, script=silent_producer
        )
        self.approve(item)

        rc, outcome = self.run_ready(receipt)

        self.assertEqual((rc, outcome["status"]), (3, "failed"))
        self.assertNotIn(campaignctl.OUTCOME_TASK_IDS_FIELD, outcome)
        self.assertIn(
            "was not written by the producer",
            outcome[campaignctl.OUTCOME_ACCOUNTING_ERROR_FIELD],
        )
        self.assertFalse(stale.exists())

    def test_an_unusable_task_ids_path_stops_the_run_before_the_producer(self) -> None:
        """If the ids can never be read, the producer must not spend at all.

        A directory at the declared path cannot be replaced by the producer's file,
        so this run could never be accounted for. Refusing after the producer had
        run would leave real spend with no identity; refusing before it means
        nothing was consumed but the item, and the outcome still resolves through
        the contract's own ``otherwise`` branch.
        """
        receipt = self.install_receipt("healthy")
        contract = self.named_contract(
            "blocked-ids", validator_script="validator_success.py"
        )
        (self.repo / TASK_IDS_RELATIVE).mkdir(parents=True, exist_ok=True)
        item = self.stage("blocked-ids", kind="compute", contract=contract)
        self.approve(item)

        rc, outcome = self.run_ready(receipt)

        self.assertEqual((rc, outcome["status"]), (3, "failed"))
        self.assertIsNone(outcome["producer_returncode"])
        self.assertIsNone(outcome["validator_returncode"])
        self.assertEqual(outcome["terminal_branch"], "unexpected-terminal-result")
        self.assertEqual(outcome["required_actions"][0]["action"], "preserve")
        self.assertIn(
            "is a directory", outcome[campaignctl.OUTCOME_ACCOUNTING_ERROR_FIELD]
        )
        self.assertNotIn(campaignctl.OUTCOME_TASK_IDS_FIELD, outcome)
        self.assertFalse((self.repo / "ran").exists())
        self.assertFalse((self.repo / "validator-ran").exists())

    def test_contract_requires_a_usable_accounting_declaration(self) -> None:
        """Without it a reservation could only ever be released by a timestamp."""
        def remove_accounting(value: dict[str, object]) -> None:
            del value["accounting"]

        contract = self.write_contract(commit=True, mutate=remove_accounting)
        with self.assertRaisesRegex(campaignctl.QueueError, "accounting"):
            self.stage(
                "validator-failure-fixture", kind="compute", contract=contract
            )

        def absolute_path(value: dict[str, object]) -> None:
            accounting = value["accounting"]
            assert isinstance(accounting, dict)
            accounting["task_ids_file"] = "/tmp/scheduler-task-ids.json"

        contract = self.write_contract(commit=True, mutate=absolute_path)
        with self.assertRaisesRegex(
            campaignctl.QueueError, "task_ids_file must be repository-relative"
        ):
            self.stage(
                "validator-failure-fixture", kind="compute", contract=contract
            )

        def unstated_expectation(value: dict[str, object]) -> None:
            accounting = value["accounting"]
            assert isinstance(accounting, dict)
            accounting["expects_scheduler_tasks"] = "yes"

        contract = self.write_contract(commit=True, mutate=unstated_expectation)
        with self.assertRaisesRegex(
            campaignctl.QueueError, "expects_scheduler_tasks must be a boolean"
        ):
            self.stage(
                "validator-failure-fixture", kind="compute", contract=contract
            )

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

    def test_two_clones_cannot_both_admit_against_one_receipt(self) -> None:
        """Two clones cannot split the queue with per-process root values."""
        receipt = self.install_receipt("near-gpu-ceiling")
        alpha_queue = self.clone_queue("alpha-clone")
        beta_queue = self.clone_queue("beta-clone")
        self.assertEqual(alpha_queue.state, beta_queue.state)
        self.assertTrue(alpha_queue.state_is_canonical())
        self.assertTrue(beta_queue.state_is_canonical())
        self.assertEqual(
            json.loads((alpha_queue.repo / receipt).read_text()),
            json.loads((beta_queue.repo / receipt).read_text()),
        )
        self.assertEqual(
            json.loads((alpha_queue.repo / receipt).read_text()),
            json.loads((self.repo / receipt).read_text()),
        )

        # Both values formerly made their process's queue look canonical. Their
        # presence now refuses operations on queues constructed before the value
        # appeared, so setting one cannot silently redirect either process.
        for queue, state_root in (
            (alpha_queue, self.root / "split-alpha"),
            (beta_queue, self.root / "split-beta"),
        ):
            with self.subTest(state_root=state_root):
                with mock.patch.dict(
                    os.environ,
                    {
                        campaignctl.PROHIBITED_CAMPAIGN_STATE_ROOT_ENV: str(
                            state_root
                        )
                    },
                ):
                    with self.assertRaisesRegex(
                        campaignctl.QueueError,
                        campaignctl.PROHIBITED_CAMPAIGN_STATE_ROOT_ENV,
                    ):
                        campaignctl.summary(queue)

        alpha_contract = self.six_hour_contract("alpha", repo=alpha_queue.repo)
        alpha = self.stage(
            "alpha", kind="compute", contract=alpha_contract, queue=alpha_queue
        )
        self.approve(alpha, queue=alpha_queue)

        with mock.patch.dict(os.environ, {"CAMPAIGN_R5_RECEIPT": receipt}):
            rc, outcome = campaignctl.run_ready(alpha_queue)

        self.assertEqual(
            (rc, outcome["status"], outcome["id"]), (0, "succeeded", "alpha")
        )

        beta_contract = self.six_hour_contract("beta", repo=beta_queue.repo)
        beta = self.stage(
            "beta", kind="compute", contract=beta_contract, queue=beta_queue
        )
        self.approve(beta, queue=beta_queue)

        with mock.patch.dict(os.environ, {"CAMPAIGN_R5_RECEIPT": receipt}):
            rc_beta, outcome_beta = campaignctl.run_ready(beta_queue)

        self.assertEqual((rc_beta, outcome_beta["status"]), (6, "refused"))
        self.assertEqual(outcome_beta["id"], "beta")
        self.assertIn(
            "gpu_task_hours ceiling would be reached", outcome_beta["reason"]
        )
        self.assertIn("490 + 6 + 6 >= 500", outcome_beta["reason"])
        self.assertIn("reserved by alpha", outcome_beta["reason"])
        self.assertFalse(beta_queue.path("claims", "beta").exists())
        self.assertFalse((beta_queue.repo / "validator-ran").exists())
        self.assertEqual(
            sorted(
                path.stem for path in (self.queue.state / "claims").glob("*.json")
            ),
            ["alpha"],
        )

    def test_two_clones_cannot_both_hold_the_admission_lock(self) -> None:
        """One campaign, one lock file, however many checkouts of the repository."""
        receipt = self.install_receipt("healthy")
        alpha_contract = self.six_hour_contract("alpha")
        clone = self.clone_queue()
        beta_contract = self.six_hour_contract("beta", repo=clone.repo)
        alpha = self.stage("alpha", kind="compute", contract=alpha_contract)
        self.approve(alpha)
        beta = self.stage(
            "beta", kind="compute", contract=beta_contract, queue=clone
        )
        self.approve(beta, queue=clone)

        # The lock is taken through campaignctl's own context manager in this
        # repository, then a ticker in the clone is asked to admit.
        with campaignctl.admission_lock(self.queue, alpha) as lock:
            self.assertEqual(lock, clone.state / campaignctl.ADMISSION_LOCK_NAME)
            with mock.patch.dict(os.environ, {"CAMPAIGN_R5_RECEIPT": receipt}):
                rc_clone, value_clone = campaignctl.run_ready(clone)

        self.assertEqual((rc_clone, value_clone["status"]), (5, "outcome-unknown"))
        self.assertIn("admission lock held by", value_clone["reason"])
        self.assertIn(str(os.getpid()), value_clone["reason"])
        self.assertFalse(clone.path("claims", "beta").exists())
        self.assertFalse(clone.path("outcomes", "beta").exists())

    def test_an_item_from_another_checkout_reserves_but_never_runs_here(self) -> None:
        """A shared queue holds other checkouts' items; a ticker must not run them.

        Their bindings, ``cwd`` and ``git_head`` are properties of the repository
        they were staged from, so validating them here would compare another
        checkout's hashes against this checkout's files -- and marking them
        ``stale`` on that comparison would consume items nobody misbehaved over.
        They are skipped, they stay listed, and they keep reserving.
        """
        receipt = self.install_receipt("healthy")
        clone = self.clone_queue()
        contract = self.six_hour_contract("alpha", repo=clone.repo)
        alpha = self.stage(
            "alpha", kind="compute", contract=contract, queue=clone
        )
        self.approve(alpha, queue=clone)

        rc, value = self.run_ready(receipt)

        self.assertEqual((rc, value["status"]), (0, "idle"))
        self.assertIsNone(campaignctl.ready_item(self.queue))
        self.assertFalse(self.queue.path("outcomes", "alpha").exists())
        rows = {row["id"]: row for row in campaignctl.summary(self.queue)["items"]}
        self.assertFalse(rows["alpha"]["runs_here"])
        self.assertEqual(rows["alpha"]["repo_path"], str(clone.repo))
        self.assertEqual(rows["alpha"]["state"], "approved")
        with self.assertRaisesRegex(
            campaignctl.QueueError, "staged from another checkout"
        ):
            campaignctl.validate_unchanged(self.queue, self.queue.item("alpha"))
        # And the clone's own ticker does run it, so the skip is about ownership
        # rather than about the item.
        self.assertEqual(campaignctl.ready_item(clone)["id"], "alpha")

    def test_an_item_with_no_recorded_checkout_never_runs_and_still_reserves(
        self,
    ) -> None:
        """An item from before the shared queue cannot be attributed to a checkout.

        Nothing records which tree its binding hashes were taken from, so no
        ticker may validate them. It fails closed: never runnable, still listed,
        still reserving, and its approval is refused rather than silently accepted.
        """
        contract = self.six_hour_contract("alpha")
        item = self.stage("alpha", kind="compute", contract=contract)
        legacy = json.loads(json.dumps(item))
        del legacy["repo_path"]
        campaignctl.atomic_json(self.queue.path("items", "alpha"), legacy)

        rc, value = self.run_ready()

        self.assertEqual((rc, value["status"]), (0, "idle"))
        rows = {row["id"]: row for row in campaignctl.summary(self.queue)["items"]}
        self.assertFalse(rows["alpha"]["runs_here"])
        self.assertEqual(rows["alpha"]["repo_path"], "")
        with self.assertRaisesRegex(
            campaignctl.QueueError, "does not record the checkout"
        ):
            self.approve(self.queue.item("alpha"))

    def test_home_environment_cannot_change_the_passwd_state_root(self) -> None:
        """A mutable process home must not be another spelling of a root override."""
        with mock.patch.dict(os.environ, {"HOME": str(self.root / "other-home")}):
            self.assertEqual(
                campaignctl.campaign_state_root(),
                self.passwd_home / campaignctl.CAMPAIGN_STATE_ROOT_NAME,
            )

    def test_only_the_canonical_state_dir_can_admit_compute(self) -> None:
        """The earlier reviewer's mutation: two ``--state-dir`` values, one receipt.

        "Campaign-global" was scoped to whatever ``--state-dir`` named, so each
        queue took its own lock, scanned its own inventory, and admitted an item
        the other had never counted -- 490 recorded and 502 projected, this time by
        splitting the queue instead of releasing a reservation. Only the canonical
        directory's inventory can be complete, so it alone admits compute.
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

    def test_two_canonical_queues_share_the_admission_lock(self) -> None:
        """One campaign has ONE queue, so a second spelling of it is that queue.

        The state directory is compared after resolution, so a path with a ``..``
        segment is the same queue and takes the same lock.
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
                self.state_root
                / ".."
                / self.state_root.name
                / campaignctl.CAMPAIGN_KEY
                / campaignctl.QUEUE_DIRECTORY_NAME
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

    def test_the_path_wrapper_and_scanner_are_bound_and_a_wrapper_swap_refuses(self) -> None:
        """The guard also executes the PATH interpreter wrappers and their scanner, so they
        are bound exactly like the sitecustomize shim: swapping only ``bin/python3`` after
        staging is a stale item that never runs."""
        contract = self.write_contract(
            commit=True, validator_script="validator_success.py"
        )
        item = self.stage(
            "validator-failure-fixture", kind="compute", contract=contract
        )
        bound = {binding["path"] for binding in item["bindings"]}
        for rel in (
            "nd-unfolding/mnv_guard_shim/scan_argv.py",
            "nd-unfolding/mnv_guard_shim/bin/python3",
            "nd-unfolding/mnv_guard_shim/bin/python",
        ):
            self.assertIn(rel, bound)
        self.approve(item)
        self.path_wrapper.write_text("#!/bin/sh\nexec \"$MNV_GUARD_REAL_PYTHON\" \"$@\"\n")
        rc, outcome = self.run_ready()
        self.assertEqual((rc, outcome["status"]), (4, "stale"))
        self.assertIn("mnv_guard_shim/bin/python3", outcome["error"])
        self.assertFalse((self.repo / "ran").exists())

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

    def test_both_modules_accept_the_same_task_identities(self) -> None:
        """The release rule compares two lists of ids, so one grammar governs both.

        A producer allowed to declare an identity ``r5_meter`` would never publish
        could never be released by any receipt; a producer allowed LESS than the
        meter publishes would silently drop tasks from its own accounting.
        """
        import r5_meter

        self.assertEqual(
            campaignctl.TASK_ID_RE.pattern, r5_meter.TASK_ID_RE.pattern
        )

    def test_a_metered_receipts_identities_are_what_the_queue_reads(self) -> None:
        """The ids campaignctl compares against come from a real metered receipt."""
        import r5_meter

        fixture = (
            Path(campaignctl.__file__).resolve().parent
            / "test_fixtures_r5_meter"
            / "mixed.sacct"
        )
        with tempfile.TemporaryDirectory() as directory:
            receipt_path = Path(directory) / "receipt.json"
            self.assertEqual(
                r5_meter.main(
                    [
                        "measure",
                        "--from-file", str(fixture),
                        "--now", "2026-09-10T00:00:00Z",
                        "--write", str(receipt_path),
                    ]
                ),
                0,
            )
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        validated = campaignctl.validate_r5_receipt(receipt)
        spend = validated["spend"]
        assert isinstance(spend, dict)
        metered = spend["metered_task_ids"]
        assert isinstance(metered, list) and metered
        for task_id in metered:
            self.assertTrue(campaignctl.TASK_ID_RE.fullmatch(str(task_id)))

if __name__ == "__main__":
    unittest.main()
