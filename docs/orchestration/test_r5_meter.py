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
        self.assertIn("tasks straddling t0 are clipped at t0", receipt["unit"])

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


if __name__ == "__main__":
    unittest.main()
