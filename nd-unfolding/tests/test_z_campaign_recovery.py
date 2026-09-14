#!/usr/bin/env python3
"""Explicitly approved per-task recovery: a NEW attempt alongside a PRESERVED one, never a reset.

JOSEPH, 2026-09-13, authorizing this bounded extension, and the prohibition the whole design is
shaped by, verbatim:

    "Do not implement recovery by deleting a claim and pretending the first attempt never existed."

and *"This authorizes implementation and tests, not any actual retry. Each retry still requires my
explicit approval."*

THE THREE TEST DIRECTIONS HE NAMED, one class each, and what each catches:

  1. `TerminalFailureIsRecovered` -- terminal-failure recovery. Catches a recovery path that does
     not actually work: the campaign staying stuck, the new attempt refusing itself, the combine
     failing to see the recovered completion. Its `NOTHING_IS_DELETED` arm is the prohibition as an
     executable statement -- every file present before recovery is still present after it, byte for
     byte, with the single exception of the partial output, which MOVES into evidence.
  2. `RecoveryRefusesWhileLiveOrUncertain` -- refusal while the old attempt is live or uncertain.
     Catches the failure shape this campaign has paid for repeatedly: a can't-look reading as
     terminal. `sacct` emits a header and ZERO rows with rc=1 when slurmdbd is down, so an absent
     job and a dead accounting database look identical, and both must refuse.
  3. `CompletedSiblingOutputsAreProtected` -- protection of completed sibling outputs. Catches a
     recovery that repairs one task by damaging another, and a combine that consumes two
     completions for one logical task or none for a recovered one.

POSITIVE CONTROLS ARE FIRST-CLASS. Every refusal below is paired with a healthy input that passes
SILENTLY, and `RecoveryGuardsHaveAPositiveControlEach` walks the set in one place -- a guard that
refuses every input passes every negative arm in this file.

FIXTURES COME FROM THE PRODUCER AND FROM THE SHIPPED FILES. Products are written by
`unified_throw_cov._atomic_savez`; the accounting dumps are in `r5_meter.SACCT_FIELDS` order and go
through the meter's own parser; the log FILENAMES are derived from each launcher's own `#SBATCH
--output/--error`; and the launcher requeue block is EXTRACTED from the shipped launcher and
EXECUTED, not described.
"""
import glob as globmod
import json
import os
import shutil
import subprocess
import sys
import time
import unittest
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ND = Path(__file__).resolve().parents[1]
REPO = ND.parent
for _p in (str(ND), str(REPO / "2d-unfolding"), str(REPO / "docs" / "orchestration"),
           str(ND / "tests")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import r5_meter                                              # noqa: E402
import unified_throw_cov as U                                # noqa: E402
import z_precursor as ZP                                     # noqa: E402
import z_precursor_admission as ZPA                          # noqa: E402
from test_z_campaign_ownership import CampaignFixture        # noqa: E402
from test_z_precursor import sacct_rows                      # noqa: E402

LAUNCHER = {name: ND / Path(rel).name for name, rel in ZP.ARM_LAUNCHERS.items()}

#: Inside `r5_meter.T0_UTC` .. `NOW`, so the fixture rows are inside the accounting window rather
#: than clipped out of it -- a dump the meter silently drops would make every admission arm vacuous.
NOW = datetime(2026, 9, 13, 12, 0, 0, tzinfo=timezone.utc)
ARRAY_JOB = "57812345"


class RecoveryFixture(CampaignFixture):
    """A campaign with one task that STARTED, wrote a partial product, and died."""

    ARM = "block"
    TASK = 4

    def setUp(self):
        super().setUp()
        self.logs = self.work / "slurmlogs"
        self.logs.mkdir()
        self.job_id = f"{ARRAY_JOB}_{self.TASK}"

    # ------------------------------------------------------------------ fixture builders ----
    def start_attempt(self, task=None, *, attempt=None, restart_count="0", partial=True):
        """Run one attempt as far as the CLAIM, then optionally leave a PARTIAL product.

        This is what a wall-killed task leaves behind: a claim, a short-but-loadable slab at the
        declared name written by the producer's own `_atomic_savez`, and no completion record.
        """
        task = self.TASK if task is None else task
        env = self.task_env(task)
        env.update({"SLURM_ARRAY_JOB_ID": ARRAY_JOB, "SLURM_JOB_ID": ARRAY_JOB,
                    "SLURM_JOB_NAME": "uthrow5d_block",
                    "SLURM_RESTART_COUNT": restart_count})
        contract = ZP.verify_task_ownership(
            arm=self.ARM, plan=self.plan_for(), product=self.product_path(self.ARM, task),
            bank=str(self.bank.path), estimator_seed=1000, draw_seed=1000, environ=env)
        if attempt is not None:
            self.assertEqual(contract["attempt"], attempt)
        if partial:
            U._atomic_savez(self.product_path(self.ARM, task),
                            xs=np.arange(2, dtype=float))       # SHORT: it died after 2 units
        return contract

    def write_logs(self, task=None, *, array_job=ARRAY_JOB, body=b"slurm log bytes\n"):
        """The failed attempt's logs, at the names the LAUNCHER's own #SBATCH patterns give."""
        task = self.TASK if task is None else task
        names = ZP.resolve_log_names(LAUNCHER[self.ARM], array_job_id=array_job, task_id=task,
                                     job_id=array_job, job_name="uthrow5d_block")
        written = {}
        for flag, name in names.items():
            path = self.logs / os.path.basename(name)
            path.write_bytes(body + flag.encode())
            written[flag] = path
        return written

    def dump(self, *, state="TIMEOUT", job_id=None, extra_rows=(), elapsed=31100):
        """An sacct dump in the meter's own field order."""
        job_id = self.job_id if job_id is None else job_id
        rows = [(job_id, "uthrow5d_block", state, elapsed, "shared",
                 "2026-09-12T00:00:00", "2026-09-12T08:38:20", "cpu=32")]
        rows.extend(extra_rows)
        path = self.work / f"sacct-{state.replace(' ', '_')}-{len(rows)}.txt"
        path.write_text(sacct_rows(rows), encoding="utf-8")
        return path

    def authorization(self, *, attempt=2, arm=None, task=None, digest=None, extra=""):
        arm = self.ARM if arm is None else arm
        task = self.TASK if task is None else task
        digest = self.campaign["campaign_digest"] if digest is None else digest
        path = self.work / f"approval-{arm}-{task}-{attempt}.txt"
        path.write_text(
            "Joseph, 2026-09-13, per-task recovery approval.\n"
            f"z-campaign-recover {digest} {arm} task {int(task)} attempt {int(attempt)}\n"
            + extra, encoding="utf-8")
        return path

    def recover(self, *, dump=None, authorization=None, task=None, job_id=None, **kw):
        task = self.TASK if task is None else task
        fields = dict(
            data_root=str(self.data_root), namespace=self.namespace, arm=self.ARM,
            task_id=task, previous_job_id=self.job_id if job_id is None else job_id,
            sacct_dump=str(self.dump() if dump is None else dump),
            spend_basis="utc", max_retries=1, now=NOW,
            authorization=str(self.authorization(task=task) if authorization is None
                              else authorization),
            log_dir=str(self.logs), code_root=str(REPO),
            admitted_launchers=[])
        fields.update(kw)
        return ZP.recover_task(**fields)

    def snapshot(self, root):
        """`{relative path: sha256}` over a tree, for the nothing-was-deleted comparison."""
        out = {}
        for base, _dirs, files in os.walk(root):
            for name in files:
                full = os.path.join(base, name)
                out[os.path.relpath(full, root)] = ZP.sha256_file(full)
        return out


# ================================== DIRECTION 1: terminal-failure recovery =====================
class TerminalFailureIsRecovered(RecoveryFixture):
    """A task that died at the wall is recovered, and the campaign finishes."""

    def test_a_TERMINAL_failure_is_RECOVERED_and_the_NEXT_ATTEMPT_RUNS(self):
        self.start_attempt()
        self.write_logs()
        with self.assertRaises(ZP.PrecursorError) as blocked:
            self.start_attempt(partial=False)
        # ⚠ THE REFUSAL IS THE OVERWRITE CLAUSE, NOT THE DUPLICATE ONE, and my first version of
        # this arm asserted the wrong one. The killed attempt LEFT A PARTIAL PRODUCT, so the
        # overwrite clause is reached first -- which is correct, and is exactly why recovery has to
        # move that partial into evidence before a second attempt can run.
        self.assertIn("ALREADY EXISTS and is claimed", str(blocked.exception),
                      "without recovery the task is stuck, which is what recovery is for")

        started = self.recover()
        self.assertEqual(started["record"]["attempt"], 2)
        self.assertEqual(started["record"]["previous_attempt"], 1)

        contract = self.start_attempt(attempt=2, partial=False)
        self.assertEqual(contract["attempt"], 2)
        self.assertTrue(contract["claim"].endswith("block.task-4.attempt-2.claim.json"))
        receipt, _product = self.publish(contract)
        self.assertEqual(receipt["extra"]["attempt"], 2)

    def test_the_PROHIBITION_holds_NOTHING_IS_DELETED_by_recovery(self):
        """*"Do not implement recovery by deleting a claim and pretending the first attempt never
        existed."* Asserted over the WHOLE campaign directory, not over the claim alone: every file
        present before recovery is still present afterwards with the same bytes, and the ONE file
        that moves -- the partial output -- reappears in evidence with the same digest.
        """
        self.start_attempt()
        self.write_logs()
        before_campaign = self.snapshot(self.paths["root"])
        before_arm = self.snapshot(self.plan["arms"][self.ARM]["dir"])
        partial_digest = before_arm["block5d_flux_4.npz"]

        self.recover()

        after_campaign = self.snapshot(self.paths["root"])
        for relative, digest in before_campaign.items():
            self.assertIn(relative, after_campaign, f"recovery DELETED {relative}")
            self.assertEqual(after_campaign[relative], digest,
                             f"recovery REWROTE {relative}")
        after_arm = self.snapshot(self.plan["arms"][self.ARM]["dir"])
        self.assertNotIn("block5d_flux_4.npz", after_arm,
                         "the partial output must MOVE out of the arm directory, or the next "
                         "attempt's overwrite refusal refuses forever")
        preserved = Path(self.paths["evidence"]) / f"{self.ARM}.task-{self.TASK}.attempt-1" \
            / "block5d_flux_4.npz"
        self.assertTrue(preserved.is_file())
        self.assertEqual(ZP.sha256_file(str(preserved)), partial_digest,
                         "the partial output is preserved BYTE FOR BYTE, not summarised")

    def test_ALL_FOUR_of_requirement_2_are_PRESERVED_and_each_is_CHECKED_separately(self):
        """Claim, logs, partial-output evidence and charged expenditure -- all four, not just the
        claim. Each is asserted against the thing it describes rather than against the record."""
        contract = self.start_attempt()
        logs = self.write_logs()
        claim_before = Path(contract["claim"]).read_bytes()
        started = self.recover()
        preserved = started["record"]["preserved"]

        # (a) THE CLAIM, in place and unchanged.
        self.assertEqual(Path(contract["claim"]).read_bytes(), claim_before)
        self.assertEqual(preserved["claim"]["sha256"], ZP.sha256_file(contract["claim"]))
        self.assertIn("PRESERVED IN PLACE", preserved["claim"]["note"])

        # (b) THE LOGS, copied, digested, and identical to the originals.
        self.assertEqual(sorted(preserved["logs"]), ["error", "output"])
        for flag, entry in preserved["logs"].items():
            self.assertEqual(Path(entry["preserved"]).read_bytes(), logs[flag].read_bytes())
            self.assertEqual(entry["sha256"], ZP.sha256_file(str(logs[flag])))

        # (c) THE PARTIAL OUTPUT, moved and digested.
        self.assertTrue(os.path.isfile(preserved["partial_output"]["preserved"]))
        self.assertEqual(preserved["partial_output"]["sha256"],
                         ZP.sha256_file(preserved["partial_output"]["preserved"]))

        # (d) THE CHARGED EXPENDITURE, from the METER and not from my own arithmetic.
        self.assertAlmostEqual(preserved["charged_expenditure"]["cpu_task_hours"],
                               31100 / 3600.0, places=9)
        self.assertEqual(preserved["charged_expenditure"]["attempts"], 1)
        self.assertEqual(preserved["charged_expenditure"]["source"],
                         "z_precursor_admission.charged_task_hours_for")

    def test_the_CHARGED_figure_is_the_METERS_and_not_a_second_implementation(self):
        """Measured against the meter's own parser over the same dump, so a hand-rolled sum here
        would have to disagree with it."""
        self.start_attempt()
        self.write_logs()
        dump = self.dump(extra_rows=[
            (self.job_id, "uthrow5d_block", "REQUEUED", 900, "shared",
             "2026-09-11T00:00:00", "2026-09-11T00:15:00", "cpu=32")])
        started = self.recover(dump=dump)
        direct = ZPA.charged_task_hours_for(Path(dump).read_text(), self.job_id)
        self.assertEqual(started["record"]["preserved"]["charged_expenditure"]["cpu_task_hours"],
                         direct["cpu_task_hours"])
        self.assertEqual(direct["attempts"], 2, "both attempts of the id are charged")

    def test_the_new_attempt_INHERITS_the_campaign_binding_rather_than_re_deriving_it(self):
        """Requirement 3. The recovered attempt must not be able to drift onto different inputs or
        a different code revision, so the record carries the manifest's own values and the task
        path re-checks the LIVE ones against the manifest."""
        self.start_attempt()
        self.write_logs()
        record = self.recover()["record"]
        body = self.campaign["body"]
        self.assertEqual(record["campaign_digest"], self.campaign["campaign_digest"])
        self.assertEqual(record["inherited"]["code_listing_sha256"],
                         body["code"]["listing_sha256"])
        self.assertEqual(record["inherited"]["inputs_listing_sha256"],
                         body["inputs"]["listing_sha256"])
        self.assertEqual(record["inherited"]["seeds"], body["seeds"])
        # ...and the inheritance is ENFORCED, not merely recorded: move an input and attempt 2
        # refuses exactly as attempt 1 would have.
        np.save(self.bank.path / "flux_univ_ratio.npy",
                np.full((U.EXPECTED_FLUX_UNIVERSES, 2), 1.07))
        with self.assertRaises(ZP.PrecursorError) as caught:
            self.start_attempt(partial=False)
        self.assertIn("has CHANGED", str(caught.exception))

    def test_a_RECOVERY_RECORD_bound_to_ANOTHER_campaign_refuses_the_new_attempt(self):
        self.start_attempt()
        self.write_logs()
        self.recover()
        path = Path(self.paths["recovery"], ZP.recovery_name(self.ARM, self.TASK, 2))
        record = json.loads(path.read_text())
        record["campaign_digest"] = "9" * 64
        path.write_text(json.dumps(record, indent=2), encoding="utf-8")
        with self.assertRaises(ZP.PrecursorError) as caught:
            self.start_attempt(partial=False)
        self.assertIn("does not get to re-derive one", str(caught.exception))

    def test_a_GAP_in_the_attempt_history_refuses(self):
        """`{2, 4}` is not "attempt 5 is next" -- it is a removed or hand-made record, and the
        history this repair preserves is no longer intact."""
        self.start_attempt()
        self.write_logs()
        self.recover()
        Path(self.paths["recovery"], ZP.recovery_name(self.ARM, self.TASK, 4)).write_text("{}")
        with self.assertRaises(ZP.PrecursorError) as caught:
            ZP.authorized_attempt(self.paths, self.ARM, self.TASK)
        self.assertIn("contiguous", str(caught.exception))

    def test_a_task_that_NEVER_STARTED_is_not_recoverable(self):
        self.write_logs(task=7)
        with self.assertRaises(ZP.PrecursorError) as caught:
            self.recover(task=7, job_id=f"{ARRAY_JOB}_7")
        self.assertIn("never started", str(caught.exception))

    def test_recovering_TWICE_for_one_attempt_refuses_rather_than_re_preserving(self):
        self.start_attempt()
        self.write_logs()
        self.recover()
        # The second call is refused at the completion/claim stage, and even if it got past that
        # the evidence directory is created exclusively.
        with self.assertRaises(ZP.PrecursorError):
            self.recover(authorization=self.authorization(attempt=2))


# ============================ DIRECTION 2: live or uncertain must REFUSE ========================
class RecoveryRefusesWhileLiveOrUncertain(RecoveryFixture):
    """Requirement 1, and the hard half is the UNCERTAIN case rather than the live one."""

    def setUp(self):
        super().setUp()
        self.start_attempt()
        self.write_logs()

    def refuses(self, dump, needle):
        with self.assertRaises(ZP.PrecursorError) as caught:
            self.recover(dump=dump)
        self.assertIn(needle, str(caught.exception))
        return str(caught.exception)

    def test_a_LIVE_attempt_refuses_in_every_state_it_could_still_be_writing_in(self):
        for state in sorted(ZP.ATTEMPT_MAY_STILL_WRITE_STATES):
            with self.subTest(state=state):
                self.refuses(self.dump(state=state), "is NOT terminal")

    def test_COMPLETING_refuses_and_that_is_the_case_Joseph_NAMED(self):
        """A completing job still holds its allocation and its open file descriptors, so a new
        attempt would be a second concurrent writer to one product."""
        message = self.refuses(self.dump(state="COMPLETING"), "is NOT terminal")
        self.assertIn("COMPLETING", message)

    def test_ZERO_ROWS_refuses_as_a_CANNOT_LOOK_and_says_so(self):
        """`sacct` prints a header and ZERO rows with rc=1 when slurmdbd is down, and zero rows
        with rc=0 for an id that never existed. An absence is not evidence of termination."""
        empty = self.work / "sacct-empty.txt"
        empty.write_text("", encoding="utf-8")
        message = self.refuses(empty, "CANNOT-LOOK")
        self.assertIn("slurmdbd", message)

    def test_a_HEADER_ONLY_dump_refuses_too(self):
        """The other shape of the same failure: `sacct` without `--noheader` when the query itself
        failed. The header is not a row about this job."""
        header = self.work / "sacct-header.txt"
        header.write_text("|".join(r5_meter.SACCT_FIELDS) + "\n", encoding="utf-8")
        self.refuses(header, "CANNOT-LOOK")

    def test_a_dump_about_ANOTHER_JOB_refuses(self):
        """A well-formed check over the wrong object. The terminality evidence has to be about the
        job that actually ran this attempt."""
        self.refuses(self.dump(job_id="57899999_4"), "CANNOT-LOOK")

    def test_an_UNRECOGNISED_state_refuses_rather_than_being_tolerated(self):
        message = self.refuses(self.dump(state="QUANTUM_FOAM"), "does not classify")
        self.assertIn("QUANTUM_FOAM", message)

    def test_an_ALL_HISTORICAL_history_refuses_because_the_TASK_is_still_going(self):
        rows = [(self.job_id, "uthrow5d_block", "REQUEUED", 100, "shared",
                 f"2026-09-1{i}T00:00:00", f"2026-09-1{i}T00:01:40", "cpu=32")
                for i in (1, 2)]
        path = self.work / "sacct-all-requeued.txt"
        path.write_text(sacct_rows(rows), encoding="utf-8")
        self.refuses(path, "NONE of them is terminal")

    def test_SPECIAL_EXIT_refuses_here_although_ACCOUNTING_calls_it_terminal(self):
        """The deliberate divergence, asserted in BOTH modules so it cannot drift into an accident.
        A held requeue can be released; for accounting it is finished, for "can it still write" it
        is not."""
        self.assertIn("SPECIAL_EXIT", ZPA.TERMINAL_STATES)
        self.assertIn("SPECIAL_EXIT", ZP.ATTEMPT_MAY_STILL_WRITE_STATES)
        self.refuses(self.dump(state="SPECIAL_EXIT"), "is NOT terminal")

    def test_POSITIVE_CONTROL_every_TERMINAL_state_is_accepted_SILENTLY(self):
        """A guard that refused every state would pass every arm above. Each terminal state is run
        against a FRESH campaign, because recovery is one-shot per attempt by design."""
        for state in sorted(ZPA.TERMINAL_STATES - ZP.ATTEMPT_MAY_STILL_WRITE_STATES):
            with self.subTest(state=state):
                evidence = ZP.confirm_attempt_terminal(
                    Path(self.dump(state=state)).read_text(), self.job_id)
                self.assertEqual(evidence["terminal_states"], [state])
                self.assertEqual(evidence["n_rows"], 1)

    def test_POSITIVE_CONTROL_a_1882_REQUEUE_history_with_a_terminal_end_is_TERMINAL(self):
        """The measured state `z_precursor_admission` records a guard once firing on: a task whose
        dump is overwhelmingly REQUEUED but whose final row is CANCELLED IS finished. A guard that
        fires on a correct run is not a guard."""
        rows = [(self.job_id, "uthrow5d_block", "REQUEUED", 60, "shared",
                 "2026-09-11T00:00:00", "2026-09-11T00:01:00", "cpu=32")] * 1882
        rows.append((self.job_id, "uthrow5d_block", "CANCELLED by 12345", 120, "shared",
                     "2026-09-12T00:00:00", "2026-09-12T00:02:00", "cpu=32"))
        evidence = ZP.confirm_attempt_terminal(sacct_rows(rows), self.job_id)
        self.assertEqual(evidence["terminal_states"], ["CANCELLED by 12345"])
        self.assertEqual(evidence["historical_rows"], 1882)

    def test_a_DECORATED_cancel_state_is_read_on_its_FIRST_TOKEN(self):
        """Slurm writes `CANCELLED by 12345`; a whole-string comparison would call it unresolved."""
        evidence = ZP.confirm_attempt_terminal(
            Path(self.dump(state="CANCELLED by 12345")).read_text(), self.job_id)
        self.assertEqual(evidence["terminal_states"], ["CANCELLED by 12345"])

    def test_a_LIVE_row_ANYWHERE_refuses_even_beside_a_terminal_one(self):
        """The order of the rows must not decide the answer: one RUNNING row is enough."""
        rows = [(self.job_id, "uthrow5d_block", "TIMEOUT", 100, "shared",
                 "2026-09-11T00:00:00", "2026-09-11T00:01:40", "cpu=32"),
                (self.job_id, "uthrow5d_block", "RUNNING", 200, "shared",
                 "2026-09-12T00:00:00", "Unknown", "cpu=32")]
        path = self.work / "sacct-mixed.txt"
        path.write_text(sacct_rows(rows), encoding="utf-8")
        self.refuses(path, "is NOT terminal")

    def test_a_previous_job_id_the_CLAIM_never_recorded_refuses(self):
        """The evidence must be about the job the CLAIM says ran, or it is a right check over the
        wrong object -- the operator could otherwise show a terminal dump for any finished job."""
        with self.assertRaises(ZP.PrecursorError) as caught:
            self.recover(job_id="57800000_9", dump=self.dump(job_id="57800000_9"))
        self.assertIn("is not one of the identities the claim", str(caught.exception))

    def test_an_attempt_whose_claim_recorded_NO_SLURM_IDENTITY_refuses(self):
        """A local or hand-made claim cannot be pointed at a job, so its terminality cannot be
        established. Fail closed rather than assume."""
        claim = Path(self.paths["claims"], ZP.claim_name(self.ARM, 6))
        contract = ZP.verify_task_ownership(
            arm=self.ARM, plan=self.plan_for(), product=self.product_path(self.ARM, 6),
            bank=str(self.bank.path), estimator_seed=1000, draw_seed=1000,
            environ=self.task_env(6))
        self.assertTrue(Path(contract["claim"]).samefile(claim))
        self.write_logs(task=6)
        with self.assertRaises(ZP.PrecursorError) as caught:
            self.recover(task=6, job_id=f"{ARRAY_JOB}_6")
        self.assertIn("recorded NO Slurm identity", str(caught.exception))


# ===================== DIRECTION 3: completed sibling outputs are protected =====================
class CompletedSiblingOutputsAreProtected(RecoveryFixture):
    """Recovery of one task must not damage another, and the combine consumes one per task."""

    def complete_sibling(self, task):
        contract = self.own(self.ARM, task)
        return self.publish(contract)

    def test_a_completed_SIBLING_is_BYTE_IDENTICAL_across_a_recovery(self):
        _receipt, sibling_product = self.complete_sibling(1)
        sibling_receipt = Path(self.paths["receipts"], ZP.receipt_name(self.ARM, 1))
        before = (ZP.sha256_file(sibling_product), sibling_receipt.read_bytes())
        self.start_attempt()
        self.write_logs()
        self.recover()
        self.assertEqual(ZP.sha256_file(sibling_product), before[0])
        self.assertEqual(sibling_receipt.read_bytes(), before[1])

    def test_the_recovered_attempt_still_PERMITS_bound_siblings(self):
        for task in (0, 1, 2):
            self.complete_sibling(task)
        self.start_attempt()
        self.write_logs()
        self.recover()
        contract = self.start_attempt(attempt=2, partial=False)
        self.assertEqual(contract["n_sibling_products"], 3)

    def test_a_task_that_ALREADY_COMPLETED_cannot_be_recovered(self):
        """Requirement 4's other half. A completion record means the task completed; recovering it
        would overwrite a completed valid product."""
        self.complete_sibling(self.TASK)
        self.write_logs()
        with self.assertRaises(ZP.PrecursorError) as caught:
            self.recover()
        self.assertIn("already has completion record", str(caught.exception))

    def test_a_COMPLETED_task_whose_product_was_LATER_CHANGED_is_a_CORRUPTION_finding(self):
        """Not a retry, and the message says which. Recovering it would bury the evidence."""
        _receipt, product = self.complete_sibling(self.TASK)
        U._atomic_savez(product, xs=np.arange(77, dtype=float))
        self.write_logs()
        with self.assertRaises(ZP.PrecursorError) as caught:
            self.recover()
        self.assertIn("corruption finding, not a failed attempt", str(caught.exception))

    def test_the_new_attempt_cannot_start_while_the_PARTIAL_is_still_in_place(self):
        """The preservation step is what makes the arm directory ready, so a product still sitting
        there says it did not happen -- and writing over it would destroy the evidence."""
        self.start_attempt()
        self.write_logs()
        self.recover()
        # Put the partial BACK, simulating a hand-restored file, and the attempt must refuse.
        preserved = (Path(self.paths["evidence"]) / f"{self.ARM}.task-{self.TASK}.attempt-1"
                     / "block5d_flux_4.npz")
        shutil.copyfile(preserved, self.product_path(self.ARM, self.TASK))
        with self.assertRaises(ZP.PrecursorError) as caught:
            self.start_attempt(partial=False)
        self.assertIn("the evidence would be destroyed by this write", str(caught.exception))

    def test_CONCURRENT_second_attempts_leave_EXACTLY_ONE_winner(self):
        """Requirement 4. The `O_EXCL` claim is per ATTEMPT, so two processes running attempt 2 of
        one task race for one create -- real processes, one barrier, exactly one winner."""
        self.start_attempt()
        self.write_logs()
        self.recover()
        outcomes = self.spawn(self.ARM, [self.TASK] * 5, publish=False)
        codes = [code for code, _out, _err in outcomes]
        self.assertEqual(codes.count(0), 1, f"exactly one attempt-2 may proceed: {outcomes}")
        for code, _out, err in outcomes:
            if code != 0:
                self.assertIn("DUPLICATE EXECUTION", err)
        self.assertEqual(sorted(ZP.task_claims(self.paths, self.ARM, self.TASK)), [1, 2])

    def test_phase_3_consumes_EXACTLY_ONE_completion_for_a_RECOVERED_task(self):
        """Requirement 5, in the direction that must WORK: an attempt-blind phase 3 would report a
        recovered task as never completed and refuse a finished campaign forever."""
        for task in self.campaign["body"]["arms"][self.ARM]["task_ids"]:
            if task == self.TASK:
                continue
            self.complete_sibling(task)
        self.start_attempt()
        self.write_logs()
        self.recover()
        contract = self.start_attempt(attempt=2, partial=False)
        self.publish(contract)
        result = ZP.require_campaign_complete(
            self.campaign, self.ARM, self.plan["arms"][self.ARM]["product_glob"])
        self.assertEqual(result["n_tasks"], 21)
        self.assertEqual(result["n_recovered_tasks"], 1)
        row = next(r for r in result["attempts"] if r["task_id"] == self.TASK)
        self.assertEqual(row["consumed_attempt"], 2)
        self.assertEqual(row["recovered_attempts"], [2])

    def test_phase_3_refuses_TWO_validating_completions_for_ONE_logical_task(self):
        """The state recovery is designed never to create, MANUFACTURED so the clause is testable.
        An untestable precondition means manufacture it, not caveat it: a second attempt's record
        is written by hand over the same product, and both then validate."""
        # THE WHOLE ARM IS COMPLETED FIRST, because the identity clause runs before the completion
        # clause and would otherwise refuse for MISSING files -- a refusal from the wrong guard,
        # which is a test that passes while measuring nothing.
        for task in self.campaign["body"]["arms"][self.ARM]["task_ids"]:
            self.complete_sibling(task)
        product = self.product_path(self.ARM, self.TASK)
        first = Path(self.paths["receipts"], ZP.receipt_name(self.ARM, self.TASK))
        second = Path(self.paths["receipts"], ZP.receipt_name(self.ARM, self.TASK, 2))
        body = json.loads(first.read_text())
        body["extra"]["attempt"] = 2
        second.write_text(json.dumps(body, indent=2), encoding="utf-8")
        self.assertEqual(ZP.sha256_file(product), body["product"]["sha256"])
        with self.assertRaises(ZP.PrecursorError) as caught:
            ZP.require_campaign_complete(
                self.campaign, self.ARM, self.plan["arms"][self.ARM]["product_glob"])
        self.assertIn("EXACTLY ONE per", str(caught.exception))
        self.assertIn("2 validated completion", str(caught.exception))

    def test_phase_3_refuses_a_STALE_record_that_NOTHING_SUPERSEDES(self):
        """A superseded attempt's record is allowed to go stale; one that stopped matching on its
        own is a changed product, and calling it a spare would hide a corruption."""
        _receipt, product = self.complete_sibling(self.TASK)
        for task in self.campaign["body"]["arms"][self.ARM]["task_ids"]:
            if task != self.TASK:
                self.complete_sibling(task)
        second = Path(self.paths["receipts"], ZP.receipt_name(self.ARM, self.TASK, 2))
        body = json.loads(Path(self.paths["receipts"],
                               ZP.receipt_name(self.ARM, self.TASK)).read_text())
        body["extra"]["attempt"] = 2
        body["product"]["sha256"] = "4" * 64
        second.write_text(json.dumps(body, indent=2), encoding="utf-8")
        self.assertTrue(os.path.exists(product))
        with self.assertRaises(ZP.PrecursorError) as caught:
            ZP.require_campaign_complete(
                self.campaign, self.ARM, self.plan["arms"][self.ARM]["product_glob"])
        self.assertIn("no recovery record supersedes them", str(caught.exception))

    def test_a_completion_record_that_MISNAMES_its_attempt_refuses(self):
        self.complete_sibling(self.TASK)
        path = Path(self.paths["receipts"], ZP.receipt_name(self.ARM, self.TASK))
        body = json.loads(path.read_text())
        body["extra"]["attempt"] = 9
        path.write_text(json.dumps(body, indent=2), encoding="utf-8")
        with self.assertRaises(ZP.PrecursorError) as caught:
            ZP.check_task_completion(self.campaign, self.ARM, self.TASK, self.paths["receipts"])
        self.assertIn("records attempt 9", str(caught.exception))


# ================================ the approval, the admission, the launcher =====================
class EachRetryNeedsItsOwnExplicitApproval(RecoveryFixture):
    """*"Each retry still requires my explicit approval."* One approval cannot be recycled."""

    def setUp(self):
        super().setUp()
        self.start_attempt()
        self.write_logs()

    def test_POSITIVE_CONTROL_the_matching_approval_passes_and_is_DIGESTED_into_the_record(self):
        path = self.authorization()
        record = self.recover(authorization=path)["record"]
        self.assertEqual(record["authorization"]["sha256"], ZP.sha256_file(str(path)))
        self.assertIn("cannot establish who wrote it", record["authorization"]["attests_only"])

    def test_an_ABSENT_approval_refuses(self):
        with self.assertRaises(ZP.PrecursorError) as caught:
            self.recover(authorization=str(self.work / "nope.txt"))
        self.assertIn("explicit approval", str(caught.exception))

    def test_an_approval_for_ANOTHER_TASK_ANOTHER_ATTEMPT_or_ANOTHER_CAMPAIGN_refuses(self):
        for label, path in (("another task", self.authorization(task=9)),
                            ("another attempt", self.authorization(attempt=3)),
                            ("another campaign", self.authorization(digest="0" * 64)),
                            ("another arm", self.authorization(arm="run"))):
            with self.subTest(case=label):
                with self.assertRaises(ZP.PrecursorError) as caught:
                    self.recover(authorization=path)
                self.assertIn("does not authorize THIS retry", str(caught.exception))

    def test_an_approval_that_merely_MENTIONS_the_words_refuses(self):
        """The required line is machine-checkable precisely so prose cannot satisfy it."""
        path = self.work / "prose.txt"
        path.write_text(
            f"I approve recovering {self.ARM} task {self.TASK} in campaign "
            f"{self.campaign['campaign_digest']}.\n", encoding="utf-8")
        with self.assertRaises(ZP.PrecursorError) as caught:
            self.recover(authorization=str(path))
        self.assertIn("does not authorize THIS retry", str(caught.exception))


class RecoveryRepricesTheWholeCampaign(RecoveryFixture):
    """Requirement 6, and it is REUSED from `z_precursor_admission`, never retyped."""

    def setUp(self):
        super().setUp()
        self.start_attempt()
        self.write_logs()

    def test_POSITIVE_CONTROL_a_small_retry_is_PERMITTED_and_the_bound_is_RECORDED(self):
        record = self.recover()["record"]
        self.assertEqual(record["admission"]["decision"], "PERMITTED")
        self.assertEqual(record["admission"]["ceiling_cpu_task_hours"],
                         r5_meter.CPU_TASK_HOURS_CEILING)
        self.assertGreater(record["admission"]["bound_cpu_task_hours"], 0.0)

    def test_a_retry_that_would_BREACH_the_ceiling_REFUSES_and_MUTATES_NOTHING(self):
        """`--max-retries` is what makes the bound reachable in a test without inventing a number:
        the same arm at a large retry allowance prices past R5's ceiling."""
        before = self.snapshot(self.paths["root"])
        with self.assertRaises(ZP.PrecursorError) as caught:
            self.recover(max_retries=400)
        self.assertIn("admission REFUSED this retry", str(caught.exception))
        self.assertEqual(self.snapshot(self.paths["root"]), before,
                         "a refused admission must leave the campaign untouched -- every check "
                         "precedes every mutation")
        self.assertFalse(os.path.exists(
            Path(self.paths["evidence"]) / f"{self.ARM}.task-{self.TASK}.attempt-1"))

    def test_a_NAIVE_spend_basis_REFUSES_through_the_module_that_owns_that_rule(self):
        with self.assertRaises(ZP.PrecursorError) as caught:
            self.recover(spend_basis="naive")
        self.assertIn("REFUSED", str(caught.exception))

    def test_the_ADMISSION_call_is_the_MODULES_and_not_a_reimplementation(self):
        source = (ND / "z_precursor.py").read_text()
        body = source[source.index("def recover_task"):source.index("def _build_parser")]
        self.assertIn("admission.admission_report(", body)
        self.assertIn("admission.charged_task_hours_for(", body)
        self.assertNotIn("CPU_TASK_HOURS_CEILING", body,
                         "the ceiling belongs to the meter; naming it here would be a second copy")


class TheLauncherRefusesARequeuedZAttempt(unittest.TestCase):
    """The `--no-requeue` half, EXECUTED rather than read.

    THE TENSION IS RESOLVED IN THE FILE AND ASSERTED HERE. Joseph authorized `--no-requeue` on the
    four launchers AND preserving existing non-Z behaviour; an `#SBATCH --no-requeue` header
    applies to every submission of a shared script, so the two cannot both hold through a header.
    What is shipped is a Z-SCOPED runtime refusal, and the arm that matters most is the one showing
    a non-Z caller is untouched.
    """

    LAUNCHERS = ("block", "run", "combine", "dump")
    GUARD_HEAD = 'if [[ -n "${MNV_Z_PRECURSOR_NS:-}" && "${SLURM_RESTART_COUNT'

    def fragment(self, arm):
        """Extracted VERBATIM from the shipped launcher -- not a copy written in this test."""
        lines = LAUNCHER[arm].read_text().splitlines()
        start = next(i for i, l in enumerate(lines) if l.startswith(self.GUARD_HEAD))
        end = next(i for i in range(start, len(lines)) if lines[i] == "fi")
        return "\n".join(lines[start:end + 1]) + "\nexit 0\n"

    def run_guard(self, arm, env):
        return subprocess.run(["bash", "-c", self.fragment(arm)],
                              env={"PATH": "/bin:/usr/bin", **env},
                              capture_output=True, text=True)

    def test_a_REQUEUED_Z_attempt_REFUSES_in_every_named_launcher(self):
        for arm in self.LAUNCHERS:
            for count in ("1", "2", "17"):
                with self.subTest(arm=arm, restart=count):
                    out = self.run_guard(arm, {"MNV_Z_PRECURSOR_NS": "ns",
                                               "SLURM_RESTART_COUNT": count})
                    self.assertEqual(out.returncode, 3, out.stderr)
                    self.assertIn("campaign-recover", out.stderr)

    def test_NON_Z_BEHAVIOUR_IS_PRESERVED_which_is_the_whole_reason_for_the_reading(self):
        """The load-bearing arm. A requeued NON-Z run -- archive reproduction, the member-axis path
        -- must be untouched, which an `#SBATCH --no-requeue` header could not have delivered."""
        for arm in self.LAUNCHERS:
            for env in ({"SLURM_RESTART_COUNT": "9"},
                        {"SLURM_RESTART_COUNT": "1", "MNV_EST_SEED_OFFSET": "1200"},
                        {}):
                with self.subTest(arm=arm, env=tuple(sorted(env))):
                    out = self.run_guard(arm, env)
                    self.assertEqual(out.returncode, 0, out.stderr)
                    self.assertEqual(out.stderr, "")

    def test_POSITIVE_CONTROL_a_FIRST_Z_attempt_passes_SILENTLY(self):
        for arm in self.LAUNCHERS:
            for env in ({"MNV_Z_PRECURSOR_NS": "ns", "SLURM_RESTART_COUNT": "0"},
                        {"MNV_Z_PRECURSOR_NS": "ns"}):
                with self.subTest(arm=arm, env=tuple(sorted(env))):
                    out = self.run_guard(arm, env)
                    self.assertEqual(out.returncode, 0, out.stderr)
                    self.assertEqual(out.stderr, "")

    def test_a_NON_NUMERIC_restart_count_refuses_rather_than_erroring_the_test_itself(self):
        """`[[ -ne ]]` on a non-numeric value is a shell ERROR, not a false; the comparison is a
        STRING comparison so garbage fails closed."""
        out = self.run_guard("block", {"MNV_Z_PRECURSOR_NS": "ns",
                                       "SLURM_RESTART_COUNT": "not-a-number"})
        self.assertEqual(out.returncode, 3)

    def test_NO_LAUNCHER_GAINED_AN_SBATCH_NO_REQUEUE_HEADER(self):
        """The reading, pinned. If a future edit adds the header, this fails and the reader is sent
        to the paragraph in the launcher that prices it."""
        for arm in self.LAUNCHERS:
            with self.subTest(arm=arm):
                text = LAUNCHER[arm].read_text()
                for line in text.splitlines():
                    if line.startswith("#SBATCH"):
                        self.assertNotIn("--no-requeue", line)
                self.assertIn("THIS IS DELIBERATELY *NOT* AN `#SBATCH --no-requeue` HEADER", text)

    def test_the_guard_is_BEFORE_the_expensive_preamble(self):
        """Refusing in seconds is the point; refusing after the A-2(f) comparison would still have
        burned the allocation this exists to save."""
        for arm in self.LAUNCHERS:
            with self.subTest(arm=arm):
                text = LAUNCHER[arm].read_text()
                # ⚠ AGAINST THE ASSIGNMENT, NOT THE FIRST MENTION. `MNV_CODE_ROOT` appears in the
                # header prose long before the preamble that reads it, so the naive index is a
                # well-formed comparison against the wrong occurrence -- it failed exactly so.
                guard = text.index(self.GUARD_HEAD)
                self.assertLess(guard, text.index('CODE_ROOT="${MNV_CODE_ROOT:?'))

    def test_NO_NEW_INTERPRETER_LINE_was_added(self):
        """Ruling 21 again: the block is pure shell, so the preflight census is untouched."""
        for arm in self.LAUNCHERS:
            with self.subTest(arm=arm):
                self.assertNotIn("python3", self.fragment(arm))


class RecoveryGuardsHaveAPositiveControlEach(RecoveryFixture):
    """One place that walks the recovery guards in their PASSING direction and requires silence."""

    def test_the_WHOLE_RECOVERY_PATH_passes_on_healthy_input_and_leaves_the_expected_records(self):
        self.start_attempt()
        self.write_logs()
        started = self.recover()
        record = started["record"]
        self.assertEqual(record["schema_version"], ZP.RECOVERY_SCHEMA_VERSION)
        self.assertTrue(os.path.isfile(started["recovery_record"]))
        self.assertTrue(os.path.isdir(started["evidence_dir"]))
        self.assertEqual(ZP.authorized_attempt(self.paths, self.ARM, self.TASK), 2)
        self.assertIn("does not submit it", record["submits_nothing"])

    def cli_argv(self, **kw):
        fields = {"--data-root": str(self.data_root), "--namespace": self.namespace,
                  "--arm": self.ARM, "--task-id": str(self.TASK),
                  "--previous-job-id": self.job_id, "--sacct-dump": str(self.dump()),
                  "--log-dir": str(self.logs), "--authorization": str(self.authorization()),
                  "--code-root": str(REPO), "--spend-basis": "utc", "--max-retries": "1",
                  "--now": "2026-09-13T12:00:00+00:00"}
        fields.update(kw)
        argv = ["campaign-recover"]
        for flag, value in fields.items():
            argv.extend([flag, value])
        return argv

    def test_the_CLI_exits_0_on_a_healthy_recovery_and_2_on_a_repeat(self):
        self.start_attempt()
        self.write_logs()
        argv = self.cli_argv()
        self.assertEqual(ZP.main(argv), 0)
        self.assertEqual(ZP.main(argv), 2)

    def test_the_CLI_RUNS_AS_A_SUBPROCESS_the_way_an_operator_runs_it(self):
        """⚠ THE ARM THAT WOULD HAVE CAUGHT THE ONE REAL DEFECT IN THIS DELTA, and it is here
        because it did not exist and the defect shipped past every other arm.

        `z_precursor.py`'s rooted insert covers `2d-unfolding` and `nd-unfolding`; `r5_meter` lives
        in `docs/orchestration`. EVERY test module in this repository puts that directory on
        `sys.path` at import scope, so `ZP.main(argv)` above -- which runs IN THIS PROCESS and
        inherits this module's path -- passed while the shipped CLI died with
        `ModuleNotFoundError: No module named 'r5_meter'` on all three of its arms, before reaching
        a single guard. It was found by running the real CLI from a real deployment clone.

        So this arm executes `python3 nd-unfolding/z_precursor.py` as a CHILD, from a working
        directory that is not the repository, with `PYTHONPATH` explicitly EMPTIED so nothing the
        harness happens to export can supply the path for it. Both directions: a healthy recovery
        exits 0, and a live previous attempt exits 2 with the refusal on stderr.
        """
        self.start_attempt()
        self.write_logs()
        script = str(ND / "z_precursor.py")
        env = {"PATH": os.environ.get("PATH", "/bin:/usr/bin"),
               "TMPDIR": os.environ.get("TMPDIR", "/tmp"), "PYTHONPATH": ""}

        live = self.work / "sacct-live.txt"
        live.write_text(sacct_rows([(self.job_id, "uthrow5d_block", "RUNNING", 100, "shared",
                                     "2026-09-12T00:00:00", "Unknown", "cpu=32")]),
                        encoding="utf-8")
        refused = subprocess.run(
            [sys.executable, script] + self.cli_argv(**{"--sacct-dump": str(live)}),
            capture_output=True, text=True, cwd=str(self.work), env=env)
        self.assertEqual(refused.returncode, 2, refused.stderr)
        self.assertIn("is NOT terminal", refused.stderr)
        self.assertNotIn("ModuleNotFoundError", refused.stderr)

        ok = subprocess.run([sys.executable, script] + self.cli_argv(),
                            capture_output=True, text=True, cwd=str(self.work), env=env)
        self.assertEqual(ok.returncode, 0, ok.stderr)
        self.assertIn("AUTHORIZED", ok.stdout)
        self.assertIn("NOTHING WAS SUBMITTED", ok.stdout)

    def test_EVERY_operator_subcommand_runs_as_a_SUBPROCESS(self):
        """The same blind spot, swept across the whole operator surface rather than the one
        subcommand that happened to break: an in-process `main()` cannot see a missing path."""
        self.start_attempt()
        self.write_logs()
        script = str(ND / "z_precursor.py")
        env = {"PATH": os.environ.get("PATH", "/bin:/usr/bin"),
               "TMPDIR": os.environ.get("TMPDIR", "/tmp"), "PYTHONPATH": ""}
        for argv in (["campaign-show", "--data-root", str(self.data_root),
                      "--namespace", self.namespace],
                     ["campaign-status", "--data-root", str(self.data_root),
                      "--namespace", self.namespace, "--arm", self.ARM],
                     ["plan", "--data-root", str(self.data_root)],
                     self.cli_argv()):
            with self.subTest(command=argv[0]):
                out = subprocess.run([sys.executable, script] + argv, capture_output=True,
                                     text=True, cwd=str(self.work),
                                     env=dict(env, MNV_Z_PRECURSOR_NS=self.namespace))
                self.assertEqual(out.returncode, 0, out.stderr)
                self.assertNotIn("Traceback", out.stderr)

    def test_the_STATUS_view_reports_the_attempt_history(self):
        self.start_attempt()
        self.write_logs()
        self.recover()
        self.start_attempt(attempt=2, partial=False)
        row = next(r for r in ZP.campaign_arm_status(self.campaign, self.ARM)["tasks"]
                   if r["task_id"] == self.TASK)
        self.assertEqual(row["attempts"], [1, 2])
        self.assertEqual(row["recovered_attempts"], [2])

    def test_a_MISSING_LOG_refuses_and_names_the_DERIVED_filename(self):
        """Requirement 2 is that the logs are preserved; a recovery that cannot show them has not."""
        self.start_attempt()
        with self.assertRaises(ZP.PrecursorError) as caught:
            self.recover()
        message = str(caught.exception)
        self.assertIn("uthrow5d_block_4_57812345.out", message)
        self.assertIn("DERIVED", message)

    def test_the_LOG_NAMES_are_DERIVED_from_each_launchers_OWN_SBATCH_lines(self):
        """The four arms genuinely differ -- the array arms use `%a_%A`, the combine uses `%j` --
        so a retyped pattern would be a well-formed answer about the wrong file."""
        self.assertEqual(
            ZP.resolve_log_names(LAUNCHER["block"], array_job_id=577, task_id=3, job_id=999,
                                 job_name="uthrow5d_block")["output"],
            "uq_5d/uthrow5d_block_3_577.out")
        self.assertEqual(
            ZP.resolve_log_names(LAUNCHER["combine"], array_job_id=577, task_id=0, job_id=999,
                                 job_name="uthrow5d_combF")["error"],
            "uq_5d/uthrow5d_combF_999.err")

    def test_an_UNKNOWN_slurm_filename_token_refuses_rather_than_being_left_literal(self):
        fake = self.work / "fake_launcher.sh"
        fake.write_text("#!/bin/bash\n#SBATCH --output=a_%N.out --error=a_%N.err\n")
        with self.assertRaises(ZP.PrecursorError) as caught:
            ZP.resolve_log_names(fake, array_job_id=1, task_id=2, job_id=3, job_name="x")
        self.assertIn("%N", str(caught.exception))

    def test_an_ESCAPED_percent_is_not_re_expanded(self):
        fake = self.work / "escaped_launcher.sh"
        fake.write_text("#!/bin/bash\n#SBATCH --output=a%%a_%a.out --error=b_%a.err\n")
        names = ZP.resolve_log_names(fake, array_job_id=1, task_id=7, job_id=3, job_name="x")
        self.assertEqual(names["output"], "a%a_7.out")

    def test_a_launcher_declaring_NO_LOGS_refuses(self):
        fake = self.work / "nolog_launcher.sh"
        fake.write_text("#!/bin/bash\n#SBATCH --job-name=x\n")
        with self.assertRaises(ZP.PrecursorError) as caught:
            ZP.launcher_log_patterns(fake)
        self.assertIn("no #SBATCH --output", str(caught.exception))

    def test_BOTH_log_flags_are_found_on_ONE_line_which_is_how_all_four_write_them(self):
        """⚠ THE FIRST VERSION OF THIS DERIVATION FOUND ONLY `--output`. All four launchers put
        both flags on one `#SBATCH` line, and a `^#SBATCH`-anchored pattern cannot match twice in
        one line -- it reported "no #SBATCH --error" on a launcher that declares one."""
        for arm in ("block", "run", "combine", "dump"):
            with self.subTest(arm=arm):
                patterns = ZP.launcher_log_patterns(LAUNCHER[arm])
                self.assertEqual(sorted(patterns), ["error", "output"])
                line = next(l for l in LAUNCHER[arm].read_text().splitlines()
                            if l.startswith("#SBATCH") and "--output=" in l)
                self.assertIn("--error=", line, "both flags really are on one line")

    def test_the_TASK_PATH_still_imports_NO_new_repository_module(self):
        """`z_precursor_admission` and `r5_meter` are imported by `recover_task` and by the CLI --
        both operator paths. The GUARDED task path must not resolve them, or the P-4 import-set pin
        moves and can only be rewritten from a clean guarded run, which is cluster work."""
        probe = self.work / "importset.py"
        probe.write_text(
            "import sys\n"
            f"sys.path.insert(0, {str(ND)!r})\n"
            f"sys.path.insert(0, {str(REPO / '2d-unfolding')!r})\n"
            "import unified_throw_cov, z_precursor\n"
            "print(any(m in sys.modules for m in "
            "('z_precursor_admission', 'r5_meter', 'mnv_source_manifest')))\n",
            encoding="utf-8")
        out = subprocess.run([sys.executable, str(probe)], capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(out.stdout.strip(), "False")


class TheRecoveryDesignIsRecordedWhereItsReaderWillMeetIt(unittest.TestCase):
    """The prohibition, the divergence and the unmeasurable fact, stated in the files."""

    def test_the_PROHIBITION_is_quoted_at_the_design_it_shapes(self):
        text = (ND / "z_precursor.py").read_text()
        self.assertIn("Do not implement recovery by deleting a claim and pretending the first",
                      text)
        self.assertIn("SO RECOVERY IS ADDITIVE", text)

    def test_NOTHING_IN_THE_MODULE_UNLINKS_A_CLAIM(self):
        """The prohibition as a property of the code, not of my intention. `os.replace` on the
        PARTIAL OUTPUT is the one move, and it targets the evidence directory."""
        import ast

        # ⚠ SCOPED TO THE RECOVERY PATH, and the unscoped version was WRONG rather than strict:
        # `_atomic_write_json` unlinks ITS OWN temporary file on the failure path, which is correct
        # and predates this extension. A module-wide ban fired on it -- right rule, wrong operand,
        # for the sixth time in this suite's history.
        recovery_functions = {"recover_task", "check_recovery_authorization",
                              "confirm_attempt_terminal", "authorized_attempt",
                              "_load_recovery_record", "resolve_log_names",
                              "launcher_log_patterns"}
        tree = ast.parse((ND / "z_precursor.py").read_text())
        checked = set()
        for function in ast.walk(tree):
            if not isinstance(function, ast.FunctionDef) or function.name not in recovery_functions:
                continue
            checked.add(function.name)
            for node in ast.walk(function):
                if isinstance(node, ast.Call):
                    name = getattr(node.func, "attr", None) or getattr(node.func, "id", None)
                    self.assertNotIn(name, {"unlink", "remove", "rmtree", "removedirs", "rmdir"},
                                     f"{function.name} calls {name!r}; recovery is ADDITIVE and "
                                     f"nothing on this path may delete")
        self.assertEqual(checked, recovery_functions,
                         "every named recovery function must exist, or this ban covers less than "
                         "it claims to")

    def test_the_SPECIAL_EXIT_divergence_is_stated_at_BOTH_ends(self):
        text = (ND / "z_precursor.py").read_text()
        self.assertIn("`SPECIAL_EXIT` IS LIVE HERE AND TERMINAL THERE", text)

    def test_the_UNMEASURABLE_JobRequeue_default_is_disclosed_in_the_launchers(self):
        """The reading depends on a fact that could not be measured, and saying so is part of the
        reading. Every named launcher carries the disclosure, not just one."""
        for arm in ("block", "run", "combine", "dump"):
            with self.subTest(arm=arm):
                text = LAUNCHER[arm].read_text()
                self.assertIn("JobRequeue", text)
                self.assertIn("sshproxy certificate expired mid-session", text)

    def test_the_APPROVAL_gate_states_what_it_CANNOT_establish(self):
        text = (ND / "z_precursor.py").read_text()
        self.assertIn("It CANNOT establish that Joseph wrote it", text)


if __name__ == "__main__":
    unittest.main()
