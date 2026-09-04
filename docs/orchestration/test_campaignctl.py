import contextlib
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from collections.abc import Callable, Iterator
from concurrent.futures import ThreadPoolExecutor
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
#: The identities the fixture producers declare. Deliberately absent from every
#: checked-in receipt fixture's `metered_task_ids`, so a receipt only counts them when
#: a test puts them there.
PRODUCER_TASK_IDS = ["7001_0"]
#: Producer prologue: the scheduler task identities an arm reports. The real producer
#: writes these from its sbatch output; here they are literal, and the file is what
#: campaignctl reads between the producer and the validator.
def write_task_ids(task_ids: list[str]) -> str:
    """Return producer source that writes ids to the queue-owned claim path."""
    return (
        "import os\n"
        "from pathlib import Path\n"
        f"_ids = Path(os.environ[{campaignctl.CAMPAIGN_TASK_IDS_FILE_ENV!r}])\n"
        f"_ids.write_text({json.dumps(json.dumps(task_ids))})\n"
    )


class CampaignQueueTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="campaign-queue-test.")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        # Production derives the cache root from the passwd database. Patch the one
        # lookup seam so tests never read or write the operator's actual queue.
        self.passwd_home = self.root / "passwd-home"
        passwd_home = mock.patch.object(
            campaignctl, "_passwd_home", return_value=self.passwd_home
        )
        passwd_home.start()
        self.addCleanup(passwd_home.stop)
        self.state_root = self.passwd_home / campaignctl.CAMPAIGN_STATE_ROOT_NAME
        # The ADMISSION NAMESPACE is the origin remote, and every admission is a
        # compare-and-swap on one ref there, so every test needs a real origin. It
        # is a throwaway bare repository under the temporary root: the fixture's
        # pinned campaign-origin.json carries this path, while the file committed in
        # the real repository carries the real URL.
        self.origin = self.root / "campaign-origin"
        subprocess.run(
            ["git", "init", "--bare", "-q", str(self.origin)], check=True
        )
        self.repo = self.root / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "-C", str(self.repo), "init", "-q"], check=True)
        subprocess.run(
            [
                "git",
                "-C",
                str(self.repo),
                "remote",
                "add",
                "origin",
                str(self.origin),
            ],
            check=True,
        )
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
        )
        self.compute_script = self.repo / "compute_work.py"
        self.compute_script.write_text(
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
        self.origin_pin = self.repo / campaignctl.CAMPAIGN_ORIGIN_FILE
        self.origin_pin.parent.mkdir(parents=True, exist_ok=True)
        self.write_origin_pin()
        subprocess.run(
            [
                "git",
                "-C",
                str(self.repo),
                "add",
                campaignctl.CAMPAIGN_ORIGIN_FILE.as_posix(),
                "work.py",
                "compute_work.py",
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
        target = script or ("compute_work.py" if kind == "compute" else "work.py")
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

    def put_state(
        self,
        family: str,
        item_id: str,
        record: dict[str, object],
        *,
        queue: campaignctl.Queue | None = None,
        exclusive: bool = False,
    ) -> dict[str, object]:
        """Write one state record into the cache AND land it on the queue ref.

        A record that lives only in a host's cache is exactly what the ref model
        refuses to believe: the next operation fetches the ref and makes the cache
        equal to it, so a hand-written record would be deleted before the
        behaviour under test could see it. Every fixture that plants a claim, a
        mutated item or a legacy record therefore publishes it, which is also the
        migration path an operator has for a pre-ref queue.
        """
        queue = queue or self.queue
        campaignctl.atomic_json(
            queue.path(family, item_id), record, exclusive=exclusive
        )
        campaignctl.publish_cached_state(
            queue, f"fixture: {family} {item_id}"
        )
        return record

    def write_origin_pin(
        self,
        *,
        repo: Path | None = None,
        origin_url: str | None = None,
        commit: bool = False,
        **changes: object,
    ) -> Path:
        """Write the pinned campaign origin into a fixture checkout.

        The pin is what makes the origin remote the admission namespace, so it is
        a first-class fixture object rather than a detail: the reviewer's mutation
        needs two checkouts that pin the SAME origin, and the mismatch tests need
        one that pins another.

        Parameters
        ----------
        repo : Path or None, optional
            Checkout to write into; the fixture repository by default.
        origin_url : str or None, optional
            URL to pin; the throwaway bare origin by default.
        commit : bool, optional
            Commit it. The initial fixture commit already carries it, so this is
            for the tests that rewrite it.
        **changes : object
            Pin fields to overwrite, named exactly as campaignctl reads them.

        Returns
        -------
        Path
            The written file.
        """
        repo = repo or self.repo
        pin: dict[str, object] = {
            "schema_version": 1,
            "campaign_key": campaignctl.CAMPAIGN_KEY,
            "ruling_record": campaignctl.R5_DECISION_RECORD,
            "ruling_record_sha256": campaignctl.CAMPAIGN_RULING_RECORD_SHA256,
            "origin_url": (
                str(self.origin) if origin_url is None else origin_url
            ),
            "queue_ref": campaignctl.CAMPAIGN_QUEUE_REF,
        }
        pin.update(changes)
        path = repo / campaignctl.CAMPAIGN_ORIGIN_FILE
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(pin, indent=2, sort_keys=True) + "\n")
        if commit:
            relative = campaignctl.CAMPAIGN_ORIGIN_FILE.as_posix()
            subprocess.run(
                ["git", "-C", str(repo), "add", relative], check=True
            )
            subprocess.run(
                ["git", "-C", str(repo), "commit", "-qm", "repin origin"],
                check=True,
            )
        return path

    def queue_ref_sha(self) -> str | None:
        """Return the sha the throwaway origin's queue ref points at, or ``None``."""
        result = subprocess.run(
            [
                "git",
                "-C",
                str(self.origin),
                "rev-parse",
                "--verify",
                "--quiet",
                campaignctl.CAMPAIGN_QUEUE_REF,
            ],
            stdout=subprocess.PIPE,
            text=True,
            check=False,
        )
        sha = result.stdout.strip()
        return sha or None

    def queue_ref_paths(self) -> list[str]:
        """Return every path in the tree the origin's queue ref points at."""
        sha = self.queue_ref_sha()
        if sha is None:
            return []
        result = subprocess.run(
            ["git", "-C", str(self.origin), "ls-tree", "-r", "--name-only", sha],
            stdout=subprocess.PIPE,
            text=True,
            check=True,
        )
        return sorted(line for line in result.stdout.splitlines() if line)

    def queue_ref_record(self, path: str) -> dict[str, object]:
        """Return one record as the origin's queue ref actually holds it."""
        sha = self.queue_ref_sha()
        assert sha is not None, "the queue ref does not exist"
        result = subprocess.run(
            ["git", "-C", str(self.origin), "show", f"{sha}:{path}"],
            stdout=subprocess.PIPE,
            text=True,
            check=True,
        )
        return json.loads(result.stdout)

    def move_queue_ref_from_another_host(self, marker: str) -> str:
        """Move the origin's queue ref the way ANOTHER HOST would.

        A commit built in its own git directory and pushed straight into the bare
        origin, never through this process's queue. That is the only thing a lease
        can be lost to, and emulating it with a local mutation would exercise the
        wrong mechanism. It keeps the parent commit's whole tree and ADDS one
        item, so what the loser refetches afterwards is a complete state rather
        than an empty one.

        Parameters
        ----------
        marker : str
            Item id the foreign commit records, so the two states are
            distinguishable afterwards.

        Returns
        -------
        str
            The sha the ref now points at.
        """
        scratch = self.root / f"foreign-git-{marker}.git"
        if not (scratch / "HEAD").is_file():
            subprocess.run(
                ["git", "init", "--bare", "-q", str(scratch)], check=True
            )
        environment = dict(os.environ)
        environment["GIT_INDEX_FILE"] = str(scratch / f"index-{marker}")
        environment.update(
            GIT_AUTHOR_NAME="another-host",
            GIT_AUTHOR_EMAIL="another@host.invalid",
            GIT_COMMITTER_NAME="another-host",
            GIT_COMMITTER_EMAIL="another@host.invalid",
        )

        def git(*arguments: str) -> str:
            result = subprocess.run(
                ["git", "--git-dir", str(scratch), *arguments],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                check=True,
                env=environment,
            )
            return result.stdout.strip()

        parent = self.queue_ref_sha()
        if parent is not None:
            git(
                "fetch",
                "--no-tags",
                str(self.origin),
                f"+{campaignctl.CAMPAIGN_QUEUE_REF}:"
                f"{campaignctl.CAMPAIGN_QUEUE_REF}",
            )
            git("read-tree", parent)
        else:
            git("read-tree", "--empty")
        record = self.root / f"foreign-record-{marker}.json"
        record.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "id": marker,
                    "kind": "read-only",
                    "description": "written by another host",
                    "argv": ["/usr/bin/true"],
                    "cwd": ".",
                    "depends_on": [],
                    "bindings": [],
                    "repo_path": str(self.root / "another-host-checkout"),
                    "git_head": "0" * 40,
                    "timeout_seconds": 30,
                    "created_at_utc": "2026-09-29T11:00:00+00:00",
                    "created_by": "another-host",
                    "proposal_digest": "f" * 64,
                }
            )
            + "\n"
        )
        blob = git("hash-object", "-w", str(record))
        git(
            "update-index",
            "--add",
            "--cacheinfo",
            f"100644,{blob},items/{marker}.json",
        )
        tree = git("write-tree")
        arguments = ["commit-tree", tree]
        if parent is not None:
            arguments += ["-p", parent]
        commit = git(*arguments, "-m", f"another host wrote {marker}")
        git(
            "push",
            str(self.origin),
            f"{commit}:{campaignctl.CAMPAIGN_QUEUE_REF}",
            "--force",
        )
        return commit

    @contextlib.contextmanager
    def host(self, name: str) -> Iterator[campaignctl.Queue]:
        """Yield a queue on its OWN passwd home, serving its own clone.

        This is the reviewer's mutation, built from the implementation's sole test
        seam: `_passwd_home` is the one lookup that decides where the cache lives,
        so patching it differently for each queue emulates two hosts (or two
        uids) exactly as production would resolve them. The patch stays active for
        the whole block because `state_is_canonical` re-derives the directory on
        every call, so the queue must be USED under the same home it was built
        under.
        """
        home = self.root / f"passwd-home-{name}"
        with mock.patch.object(campaignctl, "_passwd_home", return_value=home):
            queue = campaignctl.Queue(
                repo=self.clone_repo(name), clock=self.queue.clock
            )
            self.assertTrue(queue.state_is_canonical())
            yield queue

    def clone_repo(self, name: str) -> Path:
        """Clone the fixture repository and point the clone at the SAME origin.

        `git clone` copies the fixture's remote configuration, which points at the
        fixture repository rather than at the bare origin, so the clone is
        repointed. That is what a real second host has: its own checkout of the
        same commits, its own passwd home, and the one origin they share.
        """
        target = self.root / name
        subprocess.run(
            ["git", "clone", "-q", str(self.repo), str(target)], check=True
        )
        subprocess.run(
            ["git", "-C", str(target), "remote", "set-url", "origin",
             str(self.origin)],
            check=True,
        )
        for key, value in (
            ("user.email", "test@example.invalid"),
            ("user.name", "Test"),
        ):
            subprocess.run(
                ["git", "-C", str(target), "config", key, value], check=True
            )
        return target

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
        return campaignctl.Queue(
            repo=self.clone_repo(name), clock=self.queue.clock
        )

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

    def write_release_record(
        self,
        name: str,
        *,
        item_id: str,
        outcome_sha256: str,
        commit: bool,
    ) -> str:
        """Write a ruling-family record bound to one canonical outcome digest."""
        relative = f"docs/orchestration/{name}"
        path = self.repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "# Continuation decision\n\n"
            f"RELEASE-RESERVATION {item_id} outcome-sha256 {outcome_sha256}\n"
        )
        if commit:
            subprocess.run(
                ["git", "-C", str(self.repo), "add", relative], check=True
            )
            subprocess.run(
                ["git", "-C", str(self.repo), "commit", "-qm", "add ruling"],
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
        self.put_state("claims", item["id"], {"id": item["id"]}, exclusive=True)
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
        self.put_state("items", item["id"], item)

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
        calls: list[list[str]] = []

        def command(
            argv: list[str], *, env: dict[str, str], **_: object
        ) -> tuple[int | None, str | None]:
            calls.append(list(argv))
            if len(calls) == 1:
                Path(env[campaignctl.CAMPAIGN_TASK_IDS_FILE_ENV]).write_text(
                    json.dumps(PRODUCER_TASK_IDS)
                )
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
        self.compute_script.write_text("raise SystemExit('dirty before staging')\n")
        with self.assertRaisesRegex(campaignctl.QueueError, "committed at HEAD"):
            self.stage(
                "validator-failure-fixture", kind="compute", contract=contract
            )

        subprocess.run(
            ["git", "-C", str(self.repo), "restore", "compute_work.py"], check=True
        )
        item = self.stage(
            "validator-failure-fixture", kind="compute", contract=contract
        )
        self.compute_script.write_text("raise SystemExit('dirty after staging')\n")
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

        rc, outcome = self.run_ready()

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
        # The span the wall governs is the producer plus the validator, which the
        # outcome records. The TICK is a different operand: it also fetches the
        # campaign queue ref and pushes the claim and this outcome to it, so a
        # stopwatch held around the invocation would measure those too and would
        # stop discriminating the two-deadline defect from queue latency.
        self.assertLess(
            outcome[campaignctl.OUTCOME_EXECUTION_SECONDS_FIELD], 1.5
        )

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

    def test_release_cannot_bypass_receipt_inclusion_for_recorded_ids(self) -> None:
        """Identifiable spend remains reserved until a receipt lists its task."""
        producer = self.commit_script(
            "alpha_producer.py", write_task_ids(["7101_0"])
        )
        receipt = self.install_receipt("near-gpu-ceiling")
        uncounted_receipt = self.install_receipt(
            "near-gpu-ceiling", measured_at_utc="2026-09-29T12:00:30+00:00"
        )
        alpha_contract = self.six_hour_contract("alpha")
        beta_contract = self.six_hour_contract("beta")
        alpha = self.stage(
            "alpha", kind="compute", contract=alpha_contract, script=producer
        )
        self.approve(alpha)
        rc, alpha_outcome = self.run_ready(receipt)
        self.assertEqual((rc, alpha_outcome["status"]), (0, "succeeded"))
        self.assertEqual(
            alpha_outcome[campaignctl.OUTCOME_TASK_IDS_FIELD], ["7101_0"]
        )

        beta = self.stage("beta", kind="compute", contract=beta_contract)
        self.approve(beta)
        with self.assertRaisesRegex(
            campaignctl.QueueError, "only a committed receipt.*can release"
        ):
            campaignctl.release(
                self.queue,
                "alpha",
                "docs/orchestration/AUTHORIZATION-unused.md",
                interactive=False,
            )

        rc, beta_outcome = self.run_ready(uncounted_receipt)
        self.assertEqual((rc, beta_outcome["status"]), (6, "refused"))
        self.assertIn("7101_0", beta_outcome["reason"])
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
        with self.assertRaisesRegex(
            campaignctl.QueueError, "expects_scheduler_tasks false.*nothing"
        ):
            campaignctl.release(
                self.queue,
                "alpha",
                "docs/orchestration/AUTHORIZATION-unused.md",
                interactive=False,
            )
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
        """Only a committed decision bound to the exact outcome carries the hold."""
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
        rc, outcome = self.run_ready(receipt)
        self.assertEqual(rc, 3)
        outcome_sha256 = campaignctl.digest(outcome)

        uncommitted = self.write_release_record(
            "AUTHORIZATION-uncommitted.md",
            item_id="alpha",
            outcome_sha256=outcome_sha256,
            commit=False,
        )
        with self.assertRaisesRegex(
            campaignctl.QueueError, "release record is not committed at HEAD"
        ):
            campaignctl.release(
                self.queue, "alpha", uncommitted, interactive=False
            )

        wrong = self.write_release_record(
            "DECISION-wrong-outcome.md",
            item_id="alpha",
            outcome_sha256="0" * 64,
            commit=True,
        )
        with self.assertRaisesRegex(
            campaignctl.QueueError, "does not bind this item.*outcome digest"
        ):
            campaignctl.release(self.queue, "alpha", wrong, interactive=False)

        correct = self.write_release_record(
            "AUTHORIZATION-continue-after-alpha.md",
            item_id="alpha",
            outcome_sha256=outcome_sha256,
            commit=True,
        )
        with mock.patch.object(
            campaignctl.sys.stdin, "isatty", return_value=False
        ):
            with self.assertRaisesRegex(
                campaignctl.QueueError, "release requires an interactive TTY"
            ):
                campaignctl.release(self.queue, "alpha", correct)

        record = campaignctl.release(
            self.queue, "alpha", correct, interactive=False
        )

        self.assertEqual(record["state_at_release"], "failed")
        self.assertEqual(record["record_path"], correct)
        self.assertEqual(
            record["record_sha256"], campaignctl.sha256_file(self.repo / correct)
        )
        self.assertEqual(record["git_head"], self.queue.git_head())
        self.assertEqual(record["outcome_sha256"], outcome_sha256)
        log = (
            self.queue.state / "logs" / campaignctl.ADMISSION_LOCK_LOG
        ).read_text()
        self.assertIn("reservation-released", log)
        self.assertIn("alpha", log)

        beta = self.stage("beta", kind="compute", contract=beta_contract)
        self.approve(beta)
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
                "import os\n"
                "from pathlib import Path\n"
                f"_ids = Path(os.environ[{campaignctl.CAMPAIGN_TASK_IDS_FILE_ENV!r}])\n"
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

    def test_concurrent_items_keep_task_ids_in_their_own_run_directories(self) -> None:
        """Concurrent producers cannot overwrite each other's task attribution."""
        receipt = self.install_receipt("healthy")
        alpha_contract = self.named_contract(
            "alpha", validator_script="validator_success.py"
        )
        beta_contract = self.named_contract(
            "beta", validator_script="validator_success.py"
        )
        alpha = self.stage("alpha", kind="compute", contract=alpha_contract)
        beta = self.stage("beta", kind="compute", contract=beta_contract)
        self.approve(alpha)
        self.approve(beta)
        with mock.patch.dict(os.environ, {"CAMPAIGN_R5_RECEIPT": receipt}):
            self.assertIsNone(campaignctl.admit(self.queue, alpha))
            self.assertIsNone(campaignctl.admit(self.queue, beta))
        (self.queue.state / "logs").mkdir(parents=True, exist_ok=True)

        both_producers_have_written = threading.Barrier(2)
        task_ids_by_item = {"alpha": ["7101_0"], "beta": ["8202_0"]}
        child_paths: dict[str, list[Path]] = {"alpha": [], "beta": []}

        def interleaved_command(
            _argv: list[str],
            *,
            env: dict[str, str],
            log_path: Path,
            **_: object,
        ) -> tuple[int, None]:
            item_id = log_path.name.split(".", 1)[0]
            task_ids_path = Path(env[campaignctl.CAMPAIGN_TASK_IDS_FILE_ENV])
            child_paths[item_id].append(task_ids_path)
            if ".producer." in log_path.name:
                task_ids_path.write_text(json.dumps(task_ids_by_item[item_id]))
                both_producers_have_written.wait(timeout=5)
            return 0, None

        child_env = os.environ.copy()
        with mock.patch.object(
            campaignctl, "run_logged_command", side_effect=interleaved_command
        ):
            with ThreadPoolExecutor(max_workers=2) as pool:
                futures = {
                    item["id"]: pool.submit(
                        campaignctl.run_compute_item, self.queue, item, child_env
                    )
                    for item in (alpha, beta)
                }
                outcomes = {
                    item_id: future.result()[1]
                    for item_id, future in futures.items()
                }

        for item_id, task_ids in task_ids_by_item.items():
            outcome = outcomes[item_id]
            expected_run_dir = self.queue.state / "runs" / item_id
            expected_task_ids_path = (
                expected_run_dir / campaignctl.TASK_IDS_FILE_NAME
            )
            self.assertEqual(
                outcome[campaignctl.OUTCOME_TASK_IDS_FIELD], task_ids
            )
            self.assertEqual(
                outcome[campaignctl.RUN_DIRECTORY_FIELD], str(expected_run_dir)
            )
            self.assertEqual(
                outcome[campaignctl.OUTCOME_TASK_IDS_PATH_FIELD],
                str(expected_task_ids_path),
            )
            self.assertEqual(child_paths[item_id], [expected_task_ids_path] * 2)
        self.assertNotEqual(
            outcomes["alpha"][campaignctl.OUTCOME_TASK_IDS_SHA256_FIELD],
            outcomes["beta"][campaignctl.OUTCOME_TASK_IDS_SHA256_FIELD],
        )

    def test_an_existing_run_directory_refuses_the_claim(self) -> None:
        """A claim cannot be exclusive when its queue-owned directory exists."""
        receipt = self.install_receipt("healthy")
        contract = self.named_contract(
            "blocked-ids", validator_script="validator_success.py"
        )
        (self.queue.state / "runs" / "blocked-ids").mkdir(parents=True)
        item = self.stage("blocked-ids", kind="compute", contract=contract)
        self.approve(item)

        rc, outcome = self.run_ready(receipt)

        self.assertEqual((rc, outcome["status"]), (6, "refused"))
        self.assertIn("claim run directory already exists", outcome["reason"])
        self.assertFalse(self.queue.path("claims", item["id"]).exists())
        self.assertFalse((self.repo / "ran").exists())

    def test_contract_requires_a_usable_accounting_declaration(self) -> None:
        """Without it a reservation could only ever be released by a timestamp."""
        def remove_accounting(value: dict[str, object]) -> None:
            del value["accounting"]

        contract = self.write_contract(commit=True, mutate=remove_accounting)
        with self.assertRaisesRegex(campaignctl.QueueError, "accounting"):
            self.stage(
                "validator-failure-fixture", kind="compute", contract=contract
            )

        def legacy_task_ids_path(value: dict[str, object]) -> None:
            accounting = value["accounting"]
            assert isinstance(accounting, dict)
            accounting["task_ids_file"] = "outputs/shared-task-ids.json"

        contract = self.write_contract(commit=True, mutate=legacy_task_ids_path)
        with self.assertRaisesRegex(
            campaignctl.QueueError,
            "accounting.task_ids_file is queue-owned since schema v2",
        ):
            self.stage(
                "validator-failure-fixture", kind="compute", contract=contract
            )

        contract = self.write_contract(
            commit=True,
            mutate=lambda value: value.update(schema_version=1),
        )
        with self.assertRaisesRegex(
            campaignctl.QueueError,
            "schema_version 1 is refused: accounting.task_ids_file is queue-owned "
            "since schema v2",
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
        self.put_state("items", "alpha", legacy)

        rc, value = self.run_ready()

        self.assertEqual((rc, value["status"]), (0, "idle"))
        rows = {row["id"]: row for row in campaignctl.summary(self.queue)["items"]}
        self.assertFalse(rows["alpha"]["runs_here"])
        self.assertEqual(rows["alpha"]["repo_path"], "")
        with self.assertRaisesRegex(
            campaignctl.QueueError, "does not record the checkout"
        ):
            self.approve(self.queue.item("alpha"))

    def test_two_passwd_homes_cannot_both_admit_against_one_receipt(self) -> None:
        """The round-7 mutation: two hosts, one origin, one 490-hour receipt.

        ``campaign_state_root`` is global only for processes that share a passwd
        home filesystem, so the declared ``(host, uid)`` residual let two hosts
        each admit six task-hours against one 490-hour receipt and project 502
        against a prohibition of 500. Built here from the implementation's sole
        test seam: two DIFFERENT ``_passwd_home`` values, hence two caches, two
        locks and two reservation inventories -- with one origin remote and the
        same receipt committed in both clones.

        Exactly one is admitted. The other refuses NAMING the reservation the
        winner holds, its producer never ran, and the claim that reserves those
        hours is one record in one tree at the origin, not one per host.
        """
        receipt = self.install_receipt("near-gpu-ceiling")

        with self.host("alpha") as alpha:
            alpha_contract = self.six_hour_contract("alpha", repo=alpha.repo)
            item = self.stage(
                "alpha", kind="compute", contract=alpha_contract, queue=alpha
            )
            self.approve(item, queue=alpha)
            with mock.patch.dict(os.environ, {"CAMPAIGN_R5_RECEIPT": receipt}):
                rc_alpha, outcome_alpha = campaignctl.run_ready(alpha)
            alpha_cache = alpha.state

        with self.host("beta") as beta:
            beta_contract = self.six_hour_contract("beta", repo=beta.repo)
            item = self.stage(
                "beta", kind="compute", contract=beta_contract, queue=beta
            )
            self.approve(item, queue=beta)
            with mock.patch.dict(os.environ, {"CAMPAIGN_R5_RECEIPT": receipt}):
                rc_beta, outcome_beta = campaignctl.run_ready(beta)
            beta_cache = beta.state

        # Two hosts really were emulated: two caches, so two locks and two
        # inventories. What they now share is the ref, not the directory.
        self.assertNotEqual(alpha_cache, beta_cache)
        self.assertEqual(
            (rc_alpha, outcome_alpha["status"], outcome_alpha["id"]),
            (0, "succeeded", "alpha"),
        )
        self.assertEqual((rc_beta, outcome_beta["status"]), (6, "refused"))
        self.assertEqual(outcome_beta["id"], "beta")
        self.assertIn(
            "gpu_task_hours ceiling would be reached", outcome_beta["reason"]
        )
        self.assertIn("490 + 6 + 6 >= 500", outcome_beta["reason"])
        self.assertIn("reserved by alpha", outcome_beta["reason"])
        # Beta's producer never ran, and beta never claimed.
        self.assertFalse((beta_cache / "runs" / "beta").exists())
        self.assertNotIn("claims/beta.json", self.queue_ref_paths())
        self.assertIn("claims/alpha.json", self.queue_ref_paths())
        # And the reservation that refused beta is ONE record, in the tree at the
        # origin, holding the state directory of the host that took it.
        claim = self.queue_ref_record("claims/alpha.json")
        self.assertEqual(claim["state_dir"], str(alpha_cache))

    def test_a_lost_lease_discards_the_claim_and_refuses_the_tick(self) -> None:
        """A ref moved between the fetch and the push is a refusal, never a merge.

        The admission window is one push, so the only way two hosts could both
        claim against one fetched sha is if a rejected push were resolved by
        merging. It is not: the mutation is discarded, the ref is re-read, the
        tick refuses with the race reason, and a later tick decides again against
        the state that actually won.
        """
        receipt = self.install_receipt("healthy")
        contract = self.named_contract(
            "validator-failure-fixture", validator_script="validator_success.py"
        )
        item = self.stage(
            "validator-failure-fixture", kind="compute", contract=contract
        )
        self.approve(item)
        fetched = self.queue_ref_sha()
        real_push = campaignctl.QueueSync.push
        interference: list[str] = []

        def push_after_another_host_moved_the_ref(sync, message):
            if message.startswith("claim ") and not interference:
                interference.append(
                    self.move_queue_ref_from_another_host("foreign-item")
                )
            return real_push(sync, message)

        with mock.patch.object(
            campaignctl.QueueSync,
            "push",
            autospec=True,
            side_effect=push_after_another_host_moved_the_ref,
        ):
            rc, value = self.run_ready(receipt)

        self.assertEqual((rc, value["status"]), (5, "race-lost"))
        self.assertIn(campaignctl.RACE_LOST_REASON, value["reason"])
        self.assertIn(fetched or "the empty value", value["reason"])
        # Discarded, not merged: no claim anywhere, no run directory, and the ref
        # is exactly where the other host left it.
        self.assertEqual(self.queue_ref_sha(), interference[0])
        self.assertNotIn(
            "claims/validator-failure-fixture.json", self.queue_ref_paths()
        )
        self.assertFalse(
            self.queue.path("claims", item["id"]).exists()
        )
        self.assertFalse(
            (self.queue.state / "runs" / item["id"]).exists()
        )
        self.assertFalse((self.repo / "validator-ran").exists())
        # The winner's tree is what this host now holds. Only the CLAIM was
        # discarded: the item and its approval had already landed, so they are
        # still there, beside the record the other host added, and the item is
        # approved rather than consumed -- which is what makes the retry possible.
        rows = {
            row["id"]: row
            for row in campaignctl.summary(self.queue)["items"]
        }
        self.assertEqual(
            sorted(rows), ["foreign-item", "validator-failure-fixture"]
        )
        self.assertEqual(rows["validator-failure-fixture"]["state"], "approved")
        self.assertFalse(rows["foreign-item"]["runs_here"])
        self.assertEqual(
            campaignctl.ready_item(self.queue)["id"], "validator-failure-fixture"
        )

    def test_a_retry_after_a_lost_lease_admits_from_the_winning_tree(self) -> None:
        """The refusal is retryable: the next tick decides against what won.

        The race is lost on the OUTCOME push here, so the item's own records
        survive in the winner's tree and the retry has something to admit. That
        is the whole difference between a refusal and a consumed item.
        """
        receipt = self.install_receipt("healthy")
        contract = self.named_contract(
            "validator-failure-fixture", validator_script="validator_success.py"
        )
        item = self.stage(
            "validator-failure-fixture", kind="compute", contract=contract
        )
        self.approve(item)
        real_push = campaignctl.QueueSync.push
        interference: list[str] = []

        def push_after_another_host_moved_the_ref(sync, message):
            if message.startswith("outcome ") and not interference:
                interference.append(
                    self.move_queue_ref_from_another_host("foreign-item")
                )
            return real_push(sync, message)

        with mock.patch.object(
            campaignctl.QueueSync,
            "push",
            autospec=True,
            side_effect=push_after_another_host_moved_the_ref,
        ):
            rc, outcome = self.run_ready(receipt)

        # The run happened and its outcome could not land, so the tick reports
        # UNRESOLVED rather than a terminal code, and the item stays claimed and
        # reserving in the ref.
        self.assertEqual(rc, 5)
        self.assertIn(campaignctl.QUEUE_PUSH_PENDING_FIELD, outcome)
        self.assertIn("claims/validator-failure-fixture.json", self.queue_ref_paths())
        self.assertNotIn(
            "outcomes/validator-failure-fixture.json", self.queue_ref_paths()
        )
        self.assertEqual(
            campaignctl.state_of(self.queue, self.queue.item(item["id"])),
            "outcome-unknown",
        )

        # The next tick retries the pending push from the top, against the tree
        # that won, and it lands.
        rc_retry, value_retry = self.run_ready(receipt)

        self.assertIn("outcomes/validator-failure-fixture.json", self.queue_ref_paths())
        self.assertEqual(
            self.queue_ref_record("outcomes/validator-failure-fixture.json")[
                "status"
            ],
            "succeeded",
        )
        self.assertEqual((rc_retry, value_retry["status"]), (0, "idle"))
        self.assertEqual(
            sorted(
                path.name
                for path in (
                    self.queue.state / campaignctl.QUEUE_PENDING_NAME
                ).glob("*.json")
            ),
            [],
        )

    def test_an_unpushed_outcome_keeps_the_item_claimed_and_reserving(self) -> None:
        """An outcome that never reached the ref releases nothing, anywhere.

        The origin disappears while the producer is running, so the claim is in
        the ref and the outcome cannot be. The hours were spent, so the honest
        state is the conservative one: the item stays claimed, keeps its full
        declared maximum reserved on every host, and the record waits to be
        retried rather than being dropped or believed.
        """
        receipt = self.install_receipt("near-gpu-ceiling")
        contract = self.six_hour_contract("alpha")
        item = self.stage("alpha", kind="compute", contract=contract)
        self.approve(item)
        moved = self.origin.with_name("campaign-origin.unreachable")
        real_command = campaignctl.run_logged_command

        def unplug_the_origin(*arguments: object, **keywords: object):
            if ".producer." in Path(str(keywords["log_path"])).name:
                self.origin.rename(moved)
            return real_command(*arguments, **keywords)

        with mock.patch.object(
            campaignctl, "run_logged_command", side_effect=unplug_the_origin
        ):
            rc, outcome = self.run_ready(receipt)

        self.assertEqual(rc, 5)
        self.assertIn(campaignctl.QUEUE_PUSH_PENDING_FIELD, outcome)
        pending = sorted(
            (self.queue.state / campaignctl.QUEUE_PENDING_NAME).glob("*.json")
        )
        self.assertEqual(
            [path.name for path in pending], ["000001-outcomes-alpha.json"]
        )
        self.assertEqual(
            campaignctl.read_object(pending[0])["record"]["status"], "succeeded"
        )
        # Nothing local claims the item is finished.
        self.assertFalse(self.queue.path("outcomes", "alpha").exists())

        moved.rename(self.origin)
        # It is still claimed in the ref, so it still reserves: a second
        # six-hour item is refused for alpha's hours even though alpha has in
        # fact finished, because nothing has metered them.
        other_contract = self.six_hour_contract("beta")
        beta = self.stage("beta", kind="compute", contract=other_contract)
        with mock.patch.dict(os.environ, {"CAMPAIGN_R5_RECEIPT": receipt}):
            campaignctl.refresh_queue(self.queue)
            self.assertIn("claims/alpha.json", self.queue_ref_paths())
            self.assertIn("outcomes/alpha.json", self.queue_ref_paths())
            self.assertEqual(
                campaignctl.state_of(self.queue, self.queue.item("alpha")),
                "succeeded",
            )
            reason = campaignctl.r5_refusal_reason(
                self.queue, self.queue.item("beta")
            )
        self.assertIsNotNone(reason)
        self.assertIn("490 + 6 + 6 >= 500", reason)
        self.assertIn(campaignctl.UNREMEASURED_HOLD, reason)
        self.assertEqual(
            sorted(
                path.name
                for path in (
                    self.queue.state / campaignctl.QUEUE_PENDING_NAME
                ).glob("*.json")
            ),
            [],
        )

    def test_an_unreachable_origin_refuses_every_operation(self) -> None:
        """No network is no admission, and no staging, approving or listing either.

        Every reservation that bounds the ceiling lives in the ref, so a queue
        that cannot read it cannot tell an empty campaign from a full one. It
        must not guess in the direction that spends.
        """
        contract = self.named_contract(
            "validator-failure-fixture", validator_script="validator_success.py"
        )
        item = self.stage(
            "validator-failure-fixture", kind="compute", contract=contract
        )
        self.approve(item)
        landed = self.queue_ref_sha()
        self.origin.rename(self.origin.with_name("campaign-origin.unreachable"))

        for description, operation in (
            ("list", lambda: campaignctl.summary(self.queue)),
            ("run-ready", lambda: campaignctl.run_ready(self.queue)),
            ("stage", lambda: self.stage("second")),
            (
                "approve",
                lambda: campaignctl.approve(
                    self.queue, item["id"], item["proposal_digest"],
                    interactive=False,
                ),
            ),
            ("revoke", lambda: campaignctl.revoke(
                self.queue, item["id"], interactive=False
            )),
        ):
            with self.subTest(operation=description):
                with self.assertRaisesRegex(
                    campaignctl.QueueError, campaignctl.ORIGIN_UNREACHABLE_REASON
                ):
                    operation()

        # Nothing was written: no claim, no outcome, no producer, and the ref is
        # exactly where the last successful operation left it.
        self.assertFalse(self.queue.path("claims", item["id"]).exists())
        self.assertFalse(self.queue.path("outcomes", item["id"]).exists())
        self.assertFalse(self.queue.path("items", "second").exists())
        self.assertFalse((self.repo / "ran").exists())
        self.origin.with_name("campaign-origin.unreachable").rename(self.origin)
        self.assertEqual(self.queue_ref_sha(), landed)

    def test_an_origin_that_is_not_the_pinned_one_refuses_every_operation(
        self,
    ) -> None:
        """A clone whose origin is a different repository is a different repository.

        Its receipts are its own, and admitting from it against this campaign's
        ceiling would count another campaign's spend as headroom. The comparison
        is on the NORMALISED URL, so a trailing ``.git`` or a differently-cased
        host is the same namespace and a different path is not.
        """
        elsewhere = self.root / "somewhere-else.git"
        subprocess.run(["git", "init", "--bare", "-q", str(elsewhere)], check=True)
        subprocess.run(
            ["git", "-C", str(self.repo), "remote", "set-url", "origin",
             str(elsewhere)],
            check=True,
        )

        with self.assertRaisesRegex(
            campaignctl.QueueError, campaignctl.ORIGIN_MISMATCH_REASON
        ):
            campaignctl.summary(self.queue)

        # A cosmetic difference git itself ignores is ignored here too, and the
        # spellings used live are ones that still RESOLVE, so the operation runs
        # rather than passing the comparison and then failing to reach anything.
        for spelling in (f"{self.origin}/", f"{self.origin}//", str(self.origin)):
            with self.subTest(spelling=spelling):
                subprocess.run(
                    ["git", "-C", str(self.repo), "remote", "set-url", "origin",
                     spelling],
                    check=True,
                )
                self.assertEqual(
                    campaignctl.summary(self.queue)["counts"]["staged"], 0
                )
        # The remaining cosmetic classes are asserted on the comparison itself,
        # because a `.git` suffix or a differently-cased host cannot be handed to
        # git as a local directory that exists.
        for pinned, configured in (
            ("https://GitHub.COM/Owner/Repo.git/", "https://github.com/Owner/Repo"),
            ("git@GITHUB.com:Owner/Repo.git", "git@github.com:Owner/Repo"),
            (f"{self.origin}.git", str(self.origin)),
        ):
            with self.subTest(pinned=pinned):
                self.assertEqual(
                    campaignctl.normalize_origin_url(pinned),
                    campaignctl.normalize_origin_url(configured),
                )
        # And the differences that are NOT cosmetic stay different: the path's
        # case, and a second `.git` that names another directory entirely.
        self.assertNotEqual(
            campaignctl.normalize_origin_url("https://github.com/Owner/Repo"),
            campaignctl.normalize_origin_url("https://github.com/owner/repo"),
        )
        self.assertNotEqual(
            campaignctl.normalize_origin_url(f"{self.origin}.git.git"),
            campaignctl.normalize_origin_url(str(self.origin)),
        )

    def test_a_checkout_with_no_origin_refuses_every_operation(self) -> None:
        """With no origin there is no admission namespace to reserve in."""
        subprocess.run(
            ["git", "-C", str(self.repo), "remote", "remove", "origin"], check=True
        )
        with self.assertRaisesRegex(
            campaignctl.QueueError, campaignctl.NO_ORIGIN_REASON
        ):
            campaignctl.summary(self.queue)

    def test_an_uncommitted_origin_pin_refuses_every_operation(self) -> None:
        """A working-tree edit must not be able to repoint the namespace.

        The pin is checked through the same identity check the R5 receipt uses,
        so an untracked pin, a working-tree edit at the same ``HEAD``, and a pin
        naming another campaign are all refusals rather than redirections.
        """
        elsewhere = self.root / "somewhere-else.git"
        subprocess.run(["git", "init", "--bare", "-q", str(elsewhere)], check=True)
        self.write_origin_pin(origin_url=str(elsewhere))
        subprocess.run(
            ["git", "-C", str(self.repo), "remote", "set-url", "origin",
             str(elsewhere)],
            check=True,
        )

        with self.assertRaisesRegex(
            campaignctl.QueueError, "differs from the blob committed at HEAD"
        ):
            campaignctl.summary(self.queue)

        # Committing it does not help: it now names a repository that is not this
        # campaign's, which the key and the ruling digest in the pin contradict.
        self.write_origin_pin(
            origin_url=str(elsewhere), commit=True, campaign_key="r5-other-0000"
        )
        with self.assertRaisesRegex(
            campaignctl.QueueError, "campaign origin pin campaign_key"
        ):
            campaignctl.summary(self.queue)

        # And an absent pin is a refusal, not a fallback to the passwd home.
        subprocess.run(
            ["git", "-C", str(self.repo), "rm", "-q",
             campaignctl.CAMPAIGN_ORIGIN_FILE.as_posix()],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(self.repo), "commit", "-qm", "drop the pin"],
            check=True,
        )
        with self.assertRaisesRegex(
            campaignctl.QueueError, "campaign origin pin missing"
        ):
            campaignctl.summary(self.queue)

    def test_the_pinned_origin_file_in_this_repository_is_this_campaigns(
        self,
    ) -> None:
        """The committed pin is the production one, checked against the module.

        The fixture writes its own pin, so nothing else in this suite would
        notice if the checked-in file drifted from the campaign key, the ruling
        record and the ref name campaignctl derives.
        """
        pin = json.loads(
            (campaignctl.REPO / campaignctl.CAMPAIGN_ORIGIN_FILE).read_text()
        )
        self.assertEqual(pin["campaign_key"], campaignctl.CAMPAIGN_KEY)
        self.assertEqual(pin["queue_ref"], campaignctl.CAMPAIGN_QUEUE_REF)
        self.assertEqual(pin["ruling_record"], campaignctl.R5_DECISION_RECORD)
        self.assertEqual(
            pin["ruling_record_sha256"], campaignctl.CAMPAIGN_RULING_RECORD_SHA256
        )
        self.assertEqual(
            sorted(pin), sorted(campaignctl.CAMPAIGN_ORIGIN_KEYS)
        )
        # The digest the campaign key is a NAME for is the ruling record's, and
        # the key's second component is its first eight hex digits.
        record = campaignctl.REPO / pin["ruling_record"]
        self.assertEqual(
            campaignctl.sha256_file(record), pin["ruling_record_sha256"]
        )
        self.assertTrue(
            campaignctl.CAMPAIGN_KEY.endswith(pin["ruling_record_sha256"][:8])
        )

    def test_home_environment_cannot_change_the_passwd_state_root(self) -> None:
        """A mutable process home must not be another spelling of a root override."""
        with mock.patch.dict(os.environ, {"HOME": str(self.root / "other-home")}):
            self.assertEqual(
                campaignctl.campaign_state_root(),
                self.passwd_home / campaignctl.CAMPAIGN_STATE_ROOT_NAME,
            )

    def test_only_the_canonical_state_dir_can_admit_compute(self) -> None:
        """The earlier reviewer's mutation: two ``--state-dir`` values, one receipt.

        "Campaign-global" was once scoped to whatever ``--state-dir`` named, so
        each queue took its own lock, scanned its own inventory, and admitted an
        item the other had never counted -- 490 recorded and 502 projected, this
        time by splitting the queue instead of releasing a reservation.

        The inventory is no longer what this test can vary: both directories are
        caches of ONE ref, so the second queue's item reserves in the first
        queue's headroom scan whatever directory it was staged from. The refusal
        under test here is the directory's own -- the LOCK and the run
        directories are still per-directory, and a lock file in a second one
        excludes nobody -- so the receipt is deliberately one with headroom to
        spare, or a shared-reservation refusal would mask it.
        """
        receipt = self.install_receipt("healthy")
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
        self.put_state("items", item["id"], producer_mutation)
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
        self.put_state("items", item["id"], validator_mutation)
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
