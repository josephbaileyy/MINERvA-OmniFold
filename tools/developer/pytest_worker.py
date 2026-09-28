"""Run one admitted suite and record collection and all test phases."""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import sys
from typing import Any

import pytest


class Report:
    """Collect pytest outcomes without treating skips or partial execution as passes."""

    def __init__(self, output: Path, root: Path, origins: dict[str, str]) -> None:
        self.output = output
        self.root = root
        self.origins = origins
        self.collected = 0
        self.deselected = 0
        self.collection_errors = 0
        self.phases: dict[str, list[Any]] = {}

    def pytest_collection_finish(self, session: Any) -> None:
        """Record the actual selected item count."""
        self.collected = len(session.items)

    def pytest_deselected(self, items: list[Any]) -> None:
        """Record explicitly deselected items as incomplete execution."""
        self.deselected += len(items)

    def pytest_collectreport(self, report: Any) -> None:
        """Count collection failures and module-level skips."""
        if report.failed:
            self.collection_errors += 1
        if report.skipped:
            self.phases[report.nodeid] = [report]

    def pytest_runtest_logreport(self, report: Any) -> None:
        """Retain setup, call, and teardown outcomes per test."""
        self.phases.setdefault(report.nodeid, []).append(report)

    def pytest_sessionfinish(self, session: Any, exitstatus: int) -> None:
        """Write final counts and verify the admitted modules' actual import origins."""
        counts = Counter({key: 0 for key in ("passed", "failed", "errored", "skipped")})
        for phases in self.phases.values():
            if any(r.failed and r.when != "call" for r in phases):
                counts["errored"] += 1
            elif any(r.failed for r in phases):
                counts["failed"] += 1
            elif any(r.skipped or hasattr(r, "wasxfail") for r in phases):
                counts["skipped"] += 1
            elif {r.when for r in phases} == {"setup", "call", "teardown"}:
                counts["passed"] += 1
        actual = {
            name: getattr(sys.modules.get(name), "__file__", None)
            for name in self.origins
        }
        origins_ok = all(
            actual[name] is not None
            and Path(str(actual[name])).resolve() == (self.root / path).resolve()
            for name, path in self.origins.items()
        )
        self.output.write_text(
            json.dumps(
                {
                    "collected": self.collected,
                    "deselected": self.deselected,
                    "collection_errors": self.collection_errors,
                    **counts,
                    "pytest_exit_status": int(exitstatus),
                    "import_origins": actual,
                    "origins_ok": origins_ok,
                },
                indent=2,
            )
            + "\n"
        )


def main() -> int:
    """Load only the named suite, with no repository conftests or ambient plugins."""
    root, suite_file, output, temporary, origin_json = sys.argv[1:]
    suite = Path(root) / suite_file
    sys.path.insert(0, str(suite.parent))
    plugin = Report(Path(output), Path(root), json.loads(origin_json))
    return int(
        pytest.main(
            [
                str(suite),
                "-q",
                "-rA",
                "--noconftest",
                "-p",
                "no:cacheprovider",
                "-c",
                str(Path(__file__).with_name("pytest.ini")),
                "--rootdir",
                root,
                "--basetemp",
                str(Path(temporary) / "pytest"),
            ],
            plugins=[plugin],
        )
    )


if __name__ == "__main__":
    raise SystemExit(main())
