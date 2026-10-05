"""Regression controls for the full-matrix launcher's storage meter.

Array task ``58396676_0`` failed six seconds in, killing its payload before it
could write a single log line. The cause was this launcher's own storage meter:
under ``set -e`` with ``pipefail``, ``own_kib=$(du -ck <glob> | tail -1 | cut
-f1)`` dies when the glob matches nothing, and the glob matches nothing on the
first iteration of every correct run. A ``${own_kib:-0}`` default was already
present and was unreachable, because it defaults the *value* while the failure
is in the *status*.

That is a guard which fires on every correct run, so these controls execute the
launcher's real metering lines -- extracted from the script text, not retyped --
in both directions: the empty directory that broke it, and a populated one where
it must still measure correctly.

Retyping the lines here would test a copy and let the launcher drift, so the
extraction is deliberate and is itself asserted.
"""

from __future__ import annotations

from pathlib import Path
import re
import subprocess
import tempfile
import unittest

LAUNCHER = Path(__file__).resolve().with_name("sbatch_full_matrix.sh")
PER_JOB_KIB = 4194304
SHARED_KIB = 83886080


def metering_lines() -> str:
    """Extract the launcher's own storage-measurement lines."""
    text = LAUNCHER.read_text()
    lines = [
        line.strip()
        for line in text.splitlines()
        if re.match(r"^\s*(own_kib|shared_kib)=", line)
    ]
    if len(lines) != 4:
        raise AssertionError(f"expected 4 metering assignments, found {len(lines)}")
    return "\n".join(lines)


def run_meter(output: Path, stem: str) -> subprocess.CompletedProcess[str]:
    """Run the extracted metering under the launcher's own shell options."""
    script = "\n".join(
        [
            "set -euo pipefail",
            f"output={output!s}",
            f"stem={stem}",
            metering_lines(),
            'echo "MEASURED own=$own_kib shared=$shared_kib"',
        ]
    )
    return subprocess.run(
        ["bash", "-c", script], capture_output=True, text=True, check=False
    )


class StorageMeter(unittest.TestCase):
    """The meter must survive an empty directory and still measure a full one."""

    def test_survives_the_first_iteration_with_no_artifacts(self) -> None:
        """The exact condition that killed 58396676_0."""
        with tempfile.TemporaryDirectory() as raw:
            output = Path(raw)
            (output / "logs").mkdir()
            result = run_meter(output, "ordinary-17")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("MEASURED own=0", result.stdout)

    def test_measures_a_populated_directory(self) -> None:
        """Having survived, it must still report a nonzero own size."""
        with tempfile.TemporaryDirectory() as raw:
            output = Path(raw)
            (output / "logs").mkdir()
            (output / "ordinary-17.json").write_bytes(b"x" * 200_000)
            (output / "ordinary-17.pooled.npz").write_bytes(b"y" * 200_000)
            result = run_meter(output, "ordinary-17")
        self.assertEqual(result.returncode, 0, result.stderr)
        match = re.search(r"MEASURED own=(\d+) shared=(\d+)", result.stdout)
        assert match is not None, result.stdout
        own, shared = int(match.group(1)), int(match.group(2))
        self.assertGreater(own, 0)
        self.assertGreaterEqual(shared, own)

    def test_another_task_products_are_not_counted_as_own(self) -> None:
        """Own size must be stem-scoped, or one task would trip another's cap."""
        with tempfile.TemporaryDirectory() as raw:
            output = Path(raw)
            (output / "logs").mkdir()
            (output / "injected-29.pooled.npz").write_bytes(b"z" * 400_000)
            result = run_meter(output, "ordinary-17")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("MEASURED own=0", result.stdout)

    def test_the_caps_the_launcher_enforces_are_the_declared_ones(self) -> None:
        """Pin the thresholds so a silent widening is visible in review."""
        text = LAUNCHER.read_text()
        self.assertIn(f"own_kib > {PER_JOB_KIB}", text)
        self.assertIn(f"shared_kib > {SHARED_KIB}", text)


class LauncherContract(unittest.TestCase):
    """The grant's limits must stay expressed where Slurm enforces them."""

    def test_concurrency_and_time_limits_are_declared(self) -> None:
        """Two concurrent jobs and twelve hours, in the array specification."""
        text = LAUNCHER.read_text()
        self.assertIn("#SBATCH --array=0-23%2", text)
        self.assertIn("#SBATCH --time=12:00:00", text)
        self.assertIn("#SBATCH --gpus=1", text)
        self.assertIn("#SBATCH --cpus-per-task=32", text)
        self.assertIn("#SBATCH --mem=56G", text)

    def test_launcher_cannot_submit_or_retry(self) -> None:
        """No sbatch inside the launcher: it must not extend or retry itself."""
        body = [
            line
            for line in LAUNCHER.read_text().splitlines()
            if not line.lstrip().startswith("#")
        ]
        self.assertFalse([line for line in body if "sbatch" in line])

    def test_index_mapping_covers_the_frozen_population(self) -> None:
        """All 24 indices must map to distinct mode/seed pairs."""
        script = (
            "modes=(ordinary injected shuffle)\n"
            "seeds=(17 29 43 59 71 89 101 113)\n"
            "for index in $(seq 0 23); do\n"
            '  echo "${modes[$((index / 8))]}-${seeds[$((index % 8))]}"\n'
            "done"
        )
        out = subprocess.run(
            ["bash", "-c", script], capture_output=True, text=True, check=True
        ).stdout.split()
        self.assertEqual(len(out), 24)
        self.assertEqual(len(set(out)), 24)


class CloseoutContract(unittest.TestCase):
    """The durable closeout must record and verify without deciding anything."""

    CLOSEOUT = Path(__file__).resolve().with_name("sbatch_matrix_closeout.sh")

    def test_it_cannot_submit_anything(self) -> None:
        """A recorder that could resubmit would be a retry path."""
        body = [
            line
            for line in self.CLOSEOUT.read_text().splitlines()
            if not line.lstrip().startswith("#")
        ]
        self.assertFalse([line for line in body if "sbatch" in line])

    def test_it_requests_no_gpu(self) -> None:
        """Closeout is accounting; it must not hold an A100."""
        text = self.CLOSEOUT.read_text()
        self.assertNotIn("--gpus", text)
        self.assertIn("#SBATCH --constraint=cpu", text)

    def test_it_takes_the_array_as_an_argument(self) -> None:
        """No hardcoded array id, so the route is reusable and auditable."""
        text = self.CLOSEOUT.read_text()
        self.assertIn("array=$4", text)
        self.assertNotIn("58397664", text)

    def test_it_writes_a_single_marker_that_demands_review(self) -> None:
        """A future session must find one file that says 'not a decision'."""
        text = self.CLOSEOUT.read_text()
        self.assertIn("CLOSEOUT.json", text)
        self.assertIn('"review_required": True', text)
        self.assertIn("non_claim", text)

    def test_it_verifies_the_covered_geometry_condition(self) -> None:
        """The runtime half of the gate-scope decision must be checked here."""
        text = self.CLOSEOUT.read_text()
        self.assertIn("padded_positions", text)
        self.assertIn("typed_tokens_per_row", text)

    def test_it_never_reports_a_bare_pass(self) -> None:
        """The reducer's own words must carry the qualification, not a summary."""
        text = self.CLOSEOUT.read_text()
        self.assertIn("never a statement of inferiority", text)


if __name__ == "__main__":
    unittest.main()
