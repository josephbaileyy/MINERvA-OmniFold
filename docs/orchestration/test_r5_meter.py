"""Tests for the R5 task-hour meter."""

from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path
from unittest import mock

from docs.orchestration import r5_meter


FIXTURES = Path(__file__).with_name("test_fixtures_r5_meter")
MIXED_FIXTURE = FIXTURES / "mixed.sacct"
PERLMUTTER_GPU_FIXTURE = FIXTURES / "perlmutter_regular_gpu.sacct"
ROW_INFLATION_FIXTURE = FIXTURES / "rows_vs_identities.sacct"
#: The preserved Perlmutter capture of one self-requeueing waker job, sanitized only by
#: replacing the real NERSC scratch path inside `JobName`. See
#: `FINDING-20260906-r5-meter-undercounted-requeue-attempts.md` for both digests and the
#: measurement that the totals are unchanged by that substitution.
WAKER_REQUEUE_FIXTURE = FIXTURES / "waker_requeue_attempts.sacct"


class R5MeterMeasurementTests(unittest.TestCase):
    """Exercise accounting identity, boundary, and state rules."""

    def build_fixture_receipt(
        self,
        fixture: Path = MIXED_FIXTURE,
        *,
        now: str = "2026-09-10T00:00:00Z",
    ) -> dict[str, object]:
        """Build a receipt from a checked-in accounting fixture."""
        return r5_meter.build_receipt(
            fixture.read_text(encoding="utf-8"),
            now=r5_meter.parse_iso_utc(now),
            source_kind="file",
            source_location=str(fixture),
        )

    def test_identity_deduplication_and_row_inflation_control(self) -> None:
        raw_text = ROW_INFLATION_FIXTURE.read_text(encoding="utf-8")
        receipt = r5_meter.build_receipt(
            raw_text,
            now=r5_meter.parse_iso_utc("2026-09-10T00:00:00Z"),
            source_kind="file",
            source_location=str(ROW_INFLATION_FIXTURE),
        )

        self.assertEqual(len(raw_text.splitlines()), 447)
        self.assertEqual(receipt["spend"]["task_count"], 374)
        self.assertAlmostEqual(
            receipt["spend"]["cpu_task_hours"], 374.0 / 3600.0
        )

    def test_steps_extern_and_array_bracket_rows_are_excluded(self) -> None:
        spend = self.build_fixture_receipt()["spend"]

        self.assertNotIn("20001.batch", spend["metered_task_ids"])
        self.assertNotIn("20001.extern", spend["metered_task_ids"])
        self.assertNotIn("20001.0", spend["metered_task_ids"])
        self.assertNotIn("20001_[1-100]", spend["metered_task_ids"])
        self.assertEqual(spend["metered_task_ids"].count("20001"), 1)

    def test_partition_prefix_remains_a_secondary_gpu_signal(self) -> None:
        spend = self.build_fixture_receipt()["spend"]

        self.assertAlmostEqual(spend["gpu_task_hours"], 3.5)
        self.assertAlmostEqual(spend["cpu_task_hours"], 8.5)

    def test_alloc_tres_typed_gpu_and_empty_value_classification(self) -> None:
        raw_text = "\n".join(
            (
                "23000|typed|COMPLETED|3600|shared|2026-09-02T13:44:27|"
                "2026-09-02T14:44:27| billing=1, gres/gpu:a100=1 ,cpu=32",
                "23001|cpu|COMPLETED|10800|regular|2026-09-02T13:44:27|"
                "2026-09-02T16:44:27|billing=1,cpu=32",
                "23002|empty|COMPLETED|7200|regular|2026-09-02T13:44:27|"
                "2026-09-02T15:44:27|",
                "23003|partition|COMPLETED|14400|gpu_shared|"
                "2026-09-02T13:44:27|2026-09-02T17:44:27|",
                "23004|zero-gpu|COMPLETED|18000|regular|"
                "2026-09-02T13:44:27|2026-09-02T18:44:27|"
                "cpu=32,gres/gpu=0",
            )
        )
        receipt = r5_meter.build_receipt(
            raw_text + "\n",
            now=r5_meter.parse_iso_utc("2026-09-10T00:00:00Z"),
            source_kind="file",
            source_location="alloc-tres.sacct",
        )

        self.assertEqual(receipt["spend"]["gpu_task_hours"], 5.0)
        self.assertEqual(receipt["spend"]["cpu_task_hours"], 10.0)

    def test_t0_straddling_and_boundary_elapsed_are_clipped(self) -> None:
        raw_text = "\n".join(
            (
                "24000|straddling|COMPLETED|3600|regular|"
                "2026-09-02T13:44:26|2026-09-02T14:44:26|cpu=1",
                "24001|ends-at-t0|COMPLETED|3600|regular|"
                "2026-09-02T12:44:27|2026-09-02T13:44:27|cpu=1",
                "24002|starts-at-t0|COMPLETED|3600|regular|"
                "2026-09-02T13:44:27|2026-09-02T14:44:27|cpu=1",
            )
        )
        receipt = r5_meter.build_receipt(
            raw_text + "\n",
            now=r5_meter.parse_iso_utc("2026-09-10T00:00:00Z"),
            source_kind="file",
            source_location="t0-boundaries.sacct",
        )
        spend = receipt["spend"]

        self.assertEqual(spend["cpu_task_hours"], (3599 + 3600) / 3600.0)
        self.assertEqual(spend["metered_task_ids"], ["24000", "24002"])
        self.assertTrue(receipt["unit"].startswith("task-hours:"))
        self.assertIn("attempts straddling t0 are clipped at t0", receipt["unit"])

    def test_failures_and_running_tasks_count_but_pending_does_not(self) -> None:
        spend = self.build_fixture_receipt()["spend"]

        self.assertEqual(
            spend["by_state"],
            {
                "CANCELLED": 1,
                "COMPLETED": 1,
                "FAILED": 1,
                "NODE_FAIL": 1,
                "OUT_OF_MEMORY": 1,
                "RUNNING": 2,
                "TIMEOUT": 1,
            },
        )
        self.assertNotIn("20008", spend["metered_task_ids"])

    def test_each_terminal_failure_and_running_state_counts_full_elapsed(self) -> None:
        spending_states = (
            "FAILED",
            "CANCELLED",
            "TIMEOUT",
            "OUT_OF_MEMORY",
            "NODE_FAIL",
            "RUNNING",
        )

        for index, state in enumerate(spending_states):
            raw_text = (
                f"{21000 + index}|state|{state}|3600|regular|"
                "2026-09-02T13:44:27|Unknown|cpu=1\n"
            )
            with self.subTest(state=state):
                receipt = r5_meter.build_receipt(
                    raw_text,
                    now=r5_meter.parse_iso_utc("2026-09-10T00:00:00Z"),
                    source_kind="file",
                    source_location="state.sacct",
                )
                self.assertEqual(receipt["spend"]["cpu_task_hours"], 1.0)
                self.assertEqual(receipt["spend"]["by_state"], {state: 1})

        pending = r5_meter.build_receipt(
            "22000|pending|PENDING|0|regular|Unknown|Unknown|cpu=1\n",
            now=r5_meter.parse_iso_utc("2026-09-10T00:00:00Z"),
            source_kind="file",
            source_location="pending.sacct",
        )
        self.assertEqual(pending["spend"]["task_count"], 0)

    def test_exact_ceiling_is_fired(self) -> None:
        raw_text = (
            "30000|ceiling|COMPLETED|1800000|gpu-main|"
            "2026-09-02T13:44:27|2026-09-23T09:44:27|gpu=1\n"
        )
        receipt = r5_meter.build_receipt(
            raw_text,
            now=r5_meter.parse_iso_utc("2026-09-10T00:00:00Z"),
            source_kind="file",
            source_location="ceiling.sacct",
        )

        self.assertEqual(receipt["spend"]["gpu_task_hours"], 500.0)
        self.assertEqual(receipt["headroom"]["gpu_task_hours"], 0.0)
        self.assertTrue(receipt["fired"]["gpu"])
        self.assertTrue(receipt["fired"]["any"])

    def test_date_fires_at_exact_boundary_not_one_second_before(self) -> None:
        before = self.build_fixture_receipt(now="2026-09-29T23:59:59Z")
        at_boundary = self.build_fixture_receipt(now="2026-09-30T00:00:00Z")

        self.assertFalse(before["fired"]["date"])
        self.assertTrue(at_boundary["fired"]["date"])

    def test_stop_uses_or_logic(self) -> None:
        before_stop = r5_meter.parse_iso_utc("2026-09-29T23:59:59Z")
        cases = (
            (before_stop, 500.0, 0.0),
            (before_stop, 0.0, 500.0),
            (r5_meter.parse_iso_utc("2026-09-30T00:00:00Z"), 0.0, 0.0),
        )

        for now, gpu_hours, cpu_hours in cases:
            with self.subTest(now=now, gpu=gpu_hours, cpu=cpu_hours):
                self.assertTrue(
                    r5_meter._fired_status(
                        now=now,
                        gpu_task_hours=gpu_hours,
                        cpu_task_hours=cpu_hours,
                    )["any"]
                )

    def test_receipt_has_exact_top_level_keys(self) -> None:
        self.assertEqual(
            list(self.build_fixture_receipt()),
            [
                "schema_version",
                "decision_record",
                "t0_utc",
                "stop_date_utc",
                "ceilings",
                "unit",
                "measured_at_utc",
                "measured_on_host",
                "source",
                "spend",
                "fired",
                "headroom",
            ],
        )

    @mock.patch("docs.orchestration.r5_meter.subprocess.run")
    def test_sacct_query_is_current_user_and_explicit_utc(
        self, run: mock.Mock
    ) -> None:
        run.return_value = mock.Mock(stdout=b"", stderr=b"")

        r5_meter._read_source(None)

        argv = run.call_args.args[0]
        environment = run.call_args.kwargs["env"]
        self.assertNotIn("--allusers", argv)
        self.assertIn("--user", argv)
        self.assertEqual(environment["TZ"], "UTC")
        self.assertEqual(
            environment["SLURM_TIME_FORMAT"], "%Y-%m-%dT%H:%M:%S"
        )
        self.assertIn("--parsable2", argv)
        self.assertIn("--noheader", argv)
        self.assertIn("--starttime", argv)
        self.assertIn("--endtime", argv)
        self.assertIn(f"--format={','.join(r5_meter.SACCT_FIELDS)}", argv)


class R5MeterCheckTests(unittest.TestCase):
    """Exercise fail-closed receipt checks and declared-cost headroom."""

    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.receipt_path = Path(self.temporary_directory.name) / "receipt.json"
        self.now = r5_meter.parse_iso_utc("2026-09-10T00:00:00Z")

    def write_receipt(
        self,
        *,
        gpu_seconds: int = 0,
        cpu_seconds: int = 0,
        measured_at: str = "2026-09-10T00:00:00Z",
    ) -> None:
        """Write a valid receipt with requested GPU and CPU elapsed time."""
        rows = []
        if gpu_seconds:
            rows.append(
                f"40000|gpu|RUNNING|{gpu_seconds}|gpu-main|"
                "2026-09-02T13:44:27|Unknown|gpu=1"
            )
        if cpu_seconds:
            rows.append(
                f"40001|cpu|RUNNING|{cpu_seconds}|regular|"
                "2026-09-02T13:44:27|Unknown|cpu=1"
            )
        receipt = r5_meter.build_receipt(
            "\n".join(rows) + ("\n" if rows else ""),
            now=r5_meter.parse_iso_utc(measured_at),
            source_kind="file",
            source_location="test.sacct",
        )
        self.receipt_path.write_text(json.dumps(receipt), encoding="utf-8")

    def run_check(self, *extra_arguments: str) -> int:
        """Run the check CLI while suppressing its diagnostic stream."""
        arguments = [
            "check",
            "--receipt",
            str(self.receipt_path),
            "--now",
            r5_meter.format_iso_utc(self.now),
            *extra_arguments,
        ]
        with contextlib.redirect_stderr(io.StringIO()):
            return r5_meter.main(arguments)

    def test_exit_zero_when_stop_has_not_fired(self) -> None:
        self.write_receipt(gpu_seconds=3600, cpu_seconds=7200)

        self.assertEqual(self.run_check(), 0)

    def test_exit_three_when_stop_has_fired(self) -> None:
        self.write_receipt(gpu_seconds=1_800_000)

        self.assertEqual(self.run_check(), 3)

    def test_exit_four_for_missing_stale_and_malformed_receipts(self) -> None:
        self.assertEqual(self.run_check(), 4)

        self.write_receipt(
            measured_at=r5_meter.format_iso_utc(self.now - timedelta(hours=25))
        )
        self.assertEqual(self.run_check(), 4)

        self.receipt_path.write_text("{not json}\n", encoding="utf-8")
        self.assertEqual(self.run_check(), 4)

    def test_exit_five_when_proposal_reaches_ceiling(self) -> None:
        self.write_receipt(gpu_seconds=495 * 3600)

        self.assertEqual(
            self.run_check("--gpu-task-hours", "5"),
            5,
        )

    def test_alloc_tres_gpu_on_regular_partition_blocks_proposal(self) -> None:
        receipt = r5_meter.build_receipt(
            PERLMUTTER_GPU_FIXTURE.read_text(encoding="utf-8"),
            now=self.now,
            source_kind="file",
            source_location=str(PERLMUTTER_GPU_FIXTURE),
        )
        self.receipt_path.write_text(json.dumps(receipt), encoding="utf-8")

        self.assertEqual(receipt["spend"]["gpu_task_hours"], 499.0)
        self.assertEqual(receipt["spend"]["cpu_task_hours"], 0.0)
        self.assertEqual(
            self.run_check("--gpu-task-hours", "2"),
            5,
        )

    def test_atomic_measure_write_matches_printed_receipt(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exit_code = r5_meter.main(
                [
                    "measure",
                    "--from-file",
                    str(MIXED_FIXTURE),
                    "--now",
                    "2026-09-10T00:00:00Z",
                    "--write",
                    str(self.receipt_path),
                ]
            )

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            json.loads(output.getvalue()),
            json.loads(self.receipt_path.read_text(encoding="utf-8")),
        )


class RequeuedExecutionAttemptTests(unittest.TestCase):
    """A requeued job id carries many execution attempts, and each one spends.

    The landed meter keyed spend by ``JobID`` alone, kept the single largest
    ``ElapsedRaw`` for a repeated id, and raised on two rows of one id with
    different starts. On the real capture that was 0.0016667 CPU task-hours where
    45 325 s had been burned, or an outright refusal once ``--duplicates`` was in
    the query. Every test here asserts a NUMBER, because "does not crash" was
    already true of the defect.
    """

    def spend(self, *rows: str) -> dict[str, object]:
        """Meter the given `sacct` rows and return the receipt's ``spend``."""
        receipt = r5_meter.build_receipt(
            "\n".join(rows) + "\n",
            now=r5_meter.parse_iso_utc("2026-09-10T00:00:00Z"),
            source_kind="file",
            source_location="attempts.sacct",
        )
        spend = receipt["spend"]
        assert isinstance(spend, dict)
        return spend

    def test_the_real_waker_capture_meters_every_requeue_attempt(self) -> None:
        """The preserved capture: 952 attempts of ONE job id, summing to 45 325 s.

        The measurement that fixes the magnitude of the defect. The plain query
        returned one row of 6 s; this is what ``sacct -X -D`` over the same window
        actually holds. The 953rd row is the PENDING record whose ``Start`` is
        ``Unknown``, and it is not an attempt.
        """
        raw_text = WAKER_REQUEUE_FIXTURE.read_text(encoding="utf-8")
        receipt = r5_meter.build_receipt(
            raw_text,
            now=r5_meter.parse_iso_utc("2026-09-10T00:00:00Z"),
            source_kind="file",
            source_location=str(WAKER_REQUEUE_FIXTURE),
        )
        spend = receipt["spend"]
        assert isinstance(spend, dict)

        self.assertEqual(len(raw_text.splitlines()), 953)
        self.assertEqual(spend["metered_task_ids"], ["57712764"])
        self.assertEqual(spend["task_count"], 1)
        self.assertEqual(spend["attempt_count"], 952)
        self.assertEqual(spend["attempts_by_task_id"], {"57712764": 952})
        self.assertEqual(spend["cpu_task_hours"], 45325 / 3600.0)
        self.assertEqual(round(float(spend["cpu_task_hours"]), 6), 12.590278)
        self.assertEqual(spend["gpu_task_hours"], 0.0)
        self.assertEqual(spend["by_state"], {"NODE_FAIL": 2, "REQUEUED": 950})
        # The under-count the repair closes, stated as the number it must not be.
        self.assertNotEqual(round(float(spend["cpu_task_hours"]), 7), 0.0016667)

    def test_distinct_requeues_of_one_id_are_summed(self) -> None:
        spend = self.spend(
            "70000|first|REQUEUED|600|regular|2026-09-03T00:00:00|"
            "2026-09-03T00:10:00|cpu=2",
            "70000|second|REQUEUED|1200|regular|2026-09-03T01:00:00|"
            "2026-09-03T01:20:00|cpu=2",
            "70000|third|FAILED|1800|regular|2026-09-03T02:00:00|"
            "2026-09-03T02:30:00|cpu=2",
        )

        self.assertEqual(spend["cpu_task_hours"], (600 + 1200 + 1800) / 3600.0)
        self.assertEqual(spend["task_count"], 1)
        self.assertEqual(spend["attempt_count"], 3)
        self.assertEqual(spend["attempts_by_task_id"], {"70000": 3})
        self.assertEqual(spend["by_state"], {"FAILED": 1, "REQUEUED": 2})

    def test_a_byte_repeated_row_is_one_observation_of_one_attempt(self) -> None:
        """``mixed.sacct``'s ``20001|duplicate`` row keeps its original meaning.

        It agrees with ``20001|at-t0`` on ``(JobID, Start, End)``, so it is the same
        execution observed twice and is charged once. Summing attempts must not turn
        a repeated row into a second execution.
        """
        raw_text = MIXED_FIXTURE.read_text(encoding="utf-8")
        receipt = r5_meter.build_receipt(
            raw_text,
            now=r5_meter.parse_iso_utc("2026-09-10T00:00:00Z"),
            source_kind="file",
            source_location=str(MIXED_FIXTURE),
        )
        spend = receipt["spend"]
        assert isinstance(spend, dict)

        self.assertIn("20001|duplicate", raw_text)
        self.assertEqual(spend["attempts_by_task_id"]["20001"], 1)
        self.assertEqual(spend["gpu_task_hours"], 3.5)

    def test_an_ordinary_non_requeued_job_is_charged_exactly_once(self) -> None:
        """The control that proves the fix does not inflate the common case.

        Every figure here is the figure the pre-repair meter produced for
        ``mixed.sacct``: no id has more than one attempt, so summing changes nothing.
        """
        receipt = r5_meter.build_receipt(
            MIXED_FIXTURE.read_text(encoding="utf-8"),
            now=r5_meter.parse_iso_utc("2026-09-10T00:00:00Z"),
            source_kind="file",
            source_location=str(MIXED_FIXTURE),
        )
        spend = receipt["spend"]
        assert isinstance(spend, dict)
        attempts_by_task_id = spend["attempts_by_task_id"]
        assert isinstance(attempts_by_task_id, dict)

        self.assertEqual(spend["gpu_task_hours"], 3.5)
        self.assertEqual(spend["cpu_task_hours"], 8.5)
        self.assertEqual(spend["task_count"], 8)
        self.assertEqual(spend["attempt_count"], 8)
        self.assertEqual(sorted(set(attempts_by_task_id.values())), [1])

    def test_conflicting_elapsed_for_one_attempt_fails_closed(self) -> None:
        with self.assertRaises(r5_meter.MeterError) as raised:
            self.spend(
                "70100|a|COMPLETED|600|regular|2026-09-03T00:00:00|"
                "2026-09-03T00:10:00|cpu=2",
                "70100|b|COMPLETED|900|regular|2026-09-03T00:00:00|"
                "2026-09-03T00:10:00|cpu=2",
            )

        self.assertIn("conflicting ElapsedRaw", str(raised.exception))
        self.assertIn("70100", str(raised.exception))

    def test_conflicting_gpu_classification_for_one_attempt_fails_closed(
        self,
    ) -> None:
        with self.assertRaises(r5_meter.MeterError) as raised:
            self.spend(
                "70101|a|COMPLETED|600|regular|2026-09-03T00:00:00|"
                "2026-09-03T00:10:00|cpu=2,gres/gpu=1",
                "70101|b|COMPLETED|600|regular|2026-09-03T00:00:00|"
                "2026-09-03T00:10:00|cpu=2",
            )

        self.assertIn("conflicting GPU classification", str(raised.exception))
        self.assertIn("70101", str(raised.exception))

    def test_the_same_start_with_a_different_end_is_a_distinct_attempt(self) -> None:
        """``End`` is part of the attempt identity, so it cannot collapse a pair."""
        spend = self.spend(
            "70102|a|COMPLETED|600|regular|2026-09-03T00:00:00|"
            "2026-09-03T00:10:00|cpu=2",
            "70102|b|COMPLETED|1200|regular|2026-09-03T00:00:00|"
            "2026-09-03T00:20:00|cpu=2",
        )

        self.assertEqual(spend["attempt_count"], 2)
        self.assertEqual(spend["cpu_task_hours"], (600 + 1200) / 3600.0)

    def test_t0_is_clipped_per_attempt_not_per_job(self) -> None:
        """A straddling attempt is clipped; its siblings after t0 are charged whole."""
        spend = self.spend(
            "70200|straddles-t0|REQUEUED|3600|regular|2026-09-02T13:44:26|"
            "2026-09-02T14:44:26|cpu=2",
            "70200|after-t0|REQUEUED|3600|regular|2026-09-02T15:00:00|"
            "2026-09-02T16:00:00|cpu=2",
            "70200|also-after-t0|FAILED|1800|regular|2026-09-02T17:00:00|"
            "2026-09-02T17:30:00|cpu=2",
        )

        self.assertEqual(
            spend["cpu_task_hours"], (3599 + 3600 + 1800) / 3600.0
        )
        self.assertEqual(spend["attempt_count"], 3)
        self.assertEqual(spend["attempts_by_task_id"], {"70200": 3})

    def test_an_attempt_ending_at_t0_is_excluded_but_its_siblings_count(
        self,
    ) -> None:
        """The case a per-JOB clip gets wrong in both directions.

        Clipping the job by its first attempt would either discard the whole id --
        the attempt that ended at t0 spent nothing R5 meters -- or charge the later
        attempts a clip they never straddled.
        """
        spend = self.spend(
            "70300|before-t0|REQUEUED|3600|regular|2026-09-02T12:44:27|"
            "2026-09-02T13:44:27|cpu=2",
            "70300|after-t0|REQUEUED|900|regular|2026-09-02T14:00:00|"
            "2026-09-02T14:15:00|cpu=2",
        )

        self.assertEqual(spend["cpu_task_hours"], 900 / 3600.0)
        self.assertEqual(spend["metered_task_ids"], ["70300"])
        self.assertEqual(spend["attempt_count"], 1)
        self.assertEqual(spend["attempts_by_task_id"], {"70300": 1})

    def test_every_failed_attempt_state_spends_and_pending_does_not(self) -> None:
        """R5 §3: a failed task spends, and retried time counts in full."""
        states = ("FAILED", "CANCELLED", "TIMEOUT", "NODE_FAIL", "REQUEUED")
        rows = [
            f"70400|attempt-{index}|{state}|600|regular|"
            f"2026-09-03T0{index}:00:00|2026-09-03T0{index}:10:00|cpu=2"
            for index, state in enumerate(states)
        ]
        rows.append(
            "70400|still-queued|PENDING|0|regular|Unknown|Unknown|cpu=2"
        )

        spend = self.spend(*rows)

        self.assertEqual(spend["attempt_count"], len(states))
        self.assertEqual(spend["cpu_task_hours"], len(states) * 600 / 3600.0)
        self.assertEqual(
            spend["by_state"], {state: 1 for state in states}
        )
        self.assertNotIn("PENDING", spend["by_state"])

    def test_steps_and_array_brackets_are_excluded_per_attempt(self) -> None:
        """A step row is a representation of an execution, never an attempt.

        Both attempts below carry a full set of step representations, so an
        attempt-summing meter that stopped excluding them would charge each
        execution four times over.
        """
        spend = self.spend(
            "70500_3|first|REQUEUED|600|regular|2026-09-03T00:00:00|"
            "2026-09-03T00:10:00|cpu=2",
            "70500_3.batch|batch|REQUEUED|600|regular|2026-09-03T00:00:00|"
            "2026-09-03T00:10:00|cpu=2",
            "70500_3.extern|extern|REQUEUED|600|regular|2026-09-03T00:00:00|"
            "2026-09-03T00:10:00|cpu=2",
            "70500_3.0|step|REQUEUED|600|regular|2026-09-03T00:00:00|"
            "2026-09-03T00:10:00|cpu=2",
            "70500_3|second|COMPLETED|900|regular|2026-09-03T01:00:00|"
            "2026-09-03T01:15:00|cpu=2",
            "70500_3.batch|batch|COMPLETED|900|regular|2026-09-03T01:00:00|"
            "2026-09-03T01:15:00|cpu=2",
            "70500_[1-100]|bracket|COMPLETED|90000|regular|"
            "2026-09-03T00:00:00|2026-09-04T01:00:00|cpu=2",
        )

        self.assertEqual(spend["metered_task_ids"], ["70500_3"])
        self.assertEqual(spend["attempt_count"], 2)
        self.assertEqual(spend["cpu_task_hours"], (600 + 900) / 3600.0)

    def test_an_array_job_sums_attempts_per_task_and_keeps_bare_ids(self) -> None:
        spend = self.spend(
            "70600_1|a1|REQUEUED|600|regular|2026-09-03T00:00:00|"
            "2026-09-03T00:10:00|cpu=2",
            "70600_1|a2|COMPLETED|1200|regular|2026-09-03T01:00:00|"
            "2026-09-03T01:20:00|cpu=2",
            "70600_2|b1|REQUEUED|300|regular|2026-09-03T00:00:00|"
            "2026-09-03T00:05:00|cpu=2",
            "70600_2|b2|REQUEUED|300|regular|2026-09-03T02:00:00|"
            "2026-09-03T02:05:00|cpu=2",
            "70600_2|b3|FAILED|1800|regular|2026-09-03T03:00:00|"
            "2026-09-03T03:30:00|cpu=2",
        )
        metered = spend["metered_task_ids"]
        assert isinstance(metered, list)

        self.assertEqual(metered, ["70600_1", "70600_2"])
        self.assertEqual(
            spend["attempts_by_task_id"], {"70600_1": 2, "70600_2": 3}
        )
        self.assertEqual(spend["attempt_count"], 5)
        self.assertEqual(
            spend["cpu_task_hours"],
            (600 + 1200 + 300 + 300 + 1800) / 3600.0,
        )
        # D3: the ids stay BARE, because campaignctl's release path matches a
        # producer's declared ids against exactly this list.
        for task_id in metered:
            self.assertIsNotNone(r5_meter.TASK_ID_RE.fullmatch(str(task_id)))

    def test_a_gpu_job_with_several_attempts_is_charged_to_gpu_hours_only(
        self,
    ) -> None:
        """CPU cores inside a GPU allocation are not also charged as CPU."""
        spend = self.spend(
            "70700|a|REQUEUED|1800|regular|2026-09-03T00:00:00|"
            "2026-09-03T00:30:00|billing=1,cpu=32,gres/gpu=4,mem=256G",
            "70700|b|NODE_FAIL|3600|regular|2026-09-03T01:00:00|"
            "2026-09-03T02:00:00|billing=1,cpu=32,gres/gpu=4,mem=256G",
            "70700|c|COMPLETED|1800|regular|2026-09-03T03:00:00|"
            "2026-09-03T03:30:00|billing=1,cpu=32,gres/gpu=4,mem=256G",
        )

        self.assertEqual(spend["gpu_task_hours"], (1800 + 3600 + 1800) / 3600.0)
        self.assertEqual(spend["cpu_task_hours"], 0.0)
        self.assertEqual(spend["attempt_count"], 3)

    def test_the_query_asks_for_allocations_and_duplicates(self) -> None:
        """Without ``-D`` a requeued job's earlier attempts are never returned."""
        with mock.patch(
            "docs.orchestration.r5_meter.subprocess.run"
        ) as run:
            run.return_value = mock.Mock(stdout=b"", stderr=b"")
            r5_meter._read_source(None)

        argv = run.call_args.args[0]
        self.assertIn("-X", argv)
        self.assertIn("-D", argv)


class R5ReceiptSchemaVersionTests(unittest.TestCase):
    """A schema-version-1 receipt is not valid accounting and is refused."""

    def version_one_receipt(self) -> dict[str, object]:
        """Return a receipt relabelled to the superseded schema version."""
        receipt = r5_meter.build_receipt(
            MIXED_FIXTURE.read_text(encoding="utf-8"),
            now=r5_meter.parse_iso_utc("2026-09-10T00:00:00Z"),
            source_kind="file",
            source_location=str(MIXED_FIXTURE),
        )
        receipt["schema_version"] = 1
        return receipt

    def test_build_receipt_publishes_schema_version_two(self) -> None:
        receipt = r5_meter.build_receipt(
            MIXED_FIXTURE.read_text(encoding="utf-8"),
            now=r5_meter.parse_iso_utc("2026-09-10T00:00:00Z"),
            source_kind="file",
            source_location=str(MIXED_FIXTURE),
        )

        self.assertEqual(receipt["schema_version"], 2)

    def test_validate_receipt_refuses_schema_version_one_and_says_why(
        self,
    ) -> None:
        with self.assertRaises(r5_meter.MeterError) as raised:
            r5_meter._validate_receipt(self.version_one_receipt())

        self.assertEqual(
            str(raised.exception),
            "receipt schema_version 1 is refused: it counted at most one "
            "execution attempt per job id, so it under-counts every requeued job "
            "and is not valid R5 accounting; re-measure with this version of the "
            "meter",
        )

    def test_check_receipt_exits_four_on_a_schema_version_one_receipt(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            receipt_path = Path(directory) / "receipt.json"
            receipt_path.write_text(
                json.dumps(self.version_one_receipt()), encoding="utf-8"
            )
            errors = io.StringIO()
            with contextlib.redirect_stderr(errors):
                exit_code = r5_meter.main(
                    [
                        "check",
                        "--receipt",
                        str(receipt_path),
                        "--now",
                        "2026-09-10T00:00:00Z",
                    ]
                )

        self.assertEqual(exit_code, 4)
        self.assertIn(
            "R5 check failed closed: receipt schema_version 1 is refused: it "
            "counted at most one execution attempt per job id",
            errors.getvalue(),
        )


if __name__ == "__main__":
    unittest.main()
