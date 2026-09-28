"""Run the reviewed lightweight suite manifest in isolated subprocesses (POSIX)."""

from __future__ import annotations

import argparse
from collections.abc import Iterator
from contextlib import contextmanager
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
import signal
import subprocess
import sys
import tempfile
import time
from types import FrameType
from typing import Any

from common import digest, git, identity, private_environment

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


@contextmanager
def _termination_requests() -> Iterator[list[int]]:
    received: list[int] = []

    def record(signum: int, frame: FrameType | None) -> None:
        # Defer cleanup until Popen has returned its process handle. Raising in a
        # handler could interrupt process creation before the handle is assigned.
        if not received:
            received.append(signum)

    previous = {sig: signal.getsignal(sig) for sig in (signal.SIGTERM, signal.SIGHUP)}
    try:
        for sig in previous:
            signal.signal(sig, record)
        yield received
    finally:
        for sig, handler in previous.items():
            signal.signal(sig, handler)


def dependencies() -> dict[str, str]:
    """Verify every runtime pin before starting test collection."""
    versions = {}
    for line in (HERE / "requirements.lock").read_text().splitlines():
        if not line or line.startswith("#"):
            continue
        name, wanted = line.split("==")
        found = importlib.metadata.version(name)
        versions[name] = found
        if found != wanted:
            raise ValueError(f"{name}: installed {found}, required {wanted}")
    return versions


def complete(result: dict[str, Any]) -> bool:
    """Accept only a positive collection with every test fully passed."""
    return bool(
        result.get("exit_status") == 0
        and result.get("pytest_exit_status") == 0
        and result.get("collected", 0) > 0
        and result.get("passed") == result.get("collected")
        and result.get("origins_ok")
        and not any(
            result.get(k, 0)
            for k in (
                "failed",
                "errored",
                "skipped",
                "deselected",
                "collection_errors",
                "timed_out",
            )
        )
    )


def run_suite(
    root: Path, suite: dict[str, Any], output: Path, timeout: float
) -> dict[str, Any]:
    """Execute one suite, saving streams and terminating its process group on exit.

    Parameters
    ----------
    root : Path
        Checkout containing the reviewed suite.
    suite : dict
        Manifest entry with file and expected module origins.
    output : Path
        New, private report directory.
    timeout : float
        Maximum wall time in seconds.

    Returns
    -------
    dict
        Counts, exit status, elapsed time, and complete-pass status.
    """
    output.mkdir(mode=0o700)
    started = time.monotonic()
    result: dict[str, Any] = {"file": suite["file"], "complete_pass": False}
    with tempfile.TemporaryDirectory(prefix="minerva-tests-") as temp:
        temporary = Path(temp)
        env = private_environment(temporary)
        command = [
            sys.executable,
            "-I",
            "-B",
            "-X",
            f"pycache_prefix={temporary / 'bytecode'}",
            str(HERE / "pytest_worker.py"),
            str(root),
            suite["file"],
            str(output / "counts.json"),
            temp,
            json.dumps(
                {
                    "origins": suite["origins"],
                    "reviewed_sha256": suite.get("reviewed_sha256", {}),
                }
            ),
        ]
        with _termination_requests() as received, (output / "stdout.txt").open(
            "w"
        ) as stdout, (output / "stderr.txt").open("w") as stderr:
            process = subprocess.Popen(
                command,
                cwd=root / Path(suite["file"]).parent,
                env=env,
                stdout=stdout,
                stderr=stderr,
                start_new_session=True,
            )
            try:
                deadline = time.monotonic() + timeout
                while True:
                    if received:
                        result.update(
                            termination_signal=received[0],
                            exit_status=128 + received[0],
                        )
                        break
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        result.update(timed_out=True, exit_status=124)
                        break
                    try:
                        result["exit_status"] = process.wait(
                            timeout=min(0.1, remaining)
                        )
                        break
                    except subprocess.TimeoutExpired:
                        continue
            finally:
                # Reap children even if the worker exited while a child was still alive.
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.wait(timeout=5)
            if received:
                result.update(
                    termination_signal=received[0], exit_status=128 + received[0]
                )
    counts = output / "counts.json"
    if counts.exists():
        result.update(json.loads(counts.read_text()))
    else:
        result["error"] = "Worker did not produce final counts; execution is incomplete"
    result["elapsed_seconds"] = round(time.monotonic() - started, 3)
    result["complete_pass"] = complete(result)
    return result


def main() -> int:
    """Validate admission, execute explicit suites, and save a compact run report."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--suite",
        action="append",
        help="manifest suite name (default: manifest default_suites)",
    )
    parser.add_argument(
        "--output", type=Path, required=True, help="new directory outside checkout"
    )
    parser.add_argument("--timeout", type=float, default=60)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.is_relative_to(ROOT) or output.exists():
        parser.error("output must be a new directory outside the checkout")
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error("timeout must be finite and positive")
    output.mkdir(mode=0o700, parents=True)
    started = time.monotonic()
    report: dict[str, Any] = {
        "complete_pass": False,
        "exit_status": 1,
        "suites": {},
        "interpreter": sys.executable,
        "python": sys.version,
        "platform": platform.platform(),
    }
    try:
        report["source_before"] = identity(ROOT)
        report["git_version"] = git(ROOT, "--version")
        if (
            os.name != "posix"
            or sys.version_info[:2] != (3, 11)
            or sys.prefix == sys.base_prefix
        ):
            raise ValueError(
                "Requires a private CPython 3.11 virtual environment on POSIX"
            )
        report["installed_distributions"] = {
            d.metadata["Name"]: d.version for d in importlib.metadata.distributions()
        }
        report["dependencies"] = dependencies()
        manifest = json.loads((HERE / "suites.json").read_text())
        report["manifest_sha256"] = digest(HERE / "suites.json")
        selected = args.suite if args.suite is not None else manifest["default_suites"]
        report["selected_suites"] = selected
        if not selected or len(set(selected)) != len(selected):
            raise ValueError("Selection must be nonempty and contain no duplicates")
        for name in selected:
            if name not in manifest["suites"]:
                raise ValueError(f"Unknown suite: {name}")
            suite = manifest["suites"][name]
            for relative, wanted in suite["reviewed_sha256"].items():
                path = ROOT / relative
                if (
                    path.is_symlink()
                    or not path.resolve().is_relative_to(ROOT)
                    or digest(path) != wanted
                ):
                    raise ValueError(
                        f"Admission changed: {relative}; review effects before updating manifest"
                    )
        inputs = {
            path
            for name in selected
            for path in [
                *manifest["suites"][name]["reviewed_sha256"],
                *manifest["suites"][name].get("read_only_inputs", []),
            ]
        }
        report["input_sha256"] = {path: digest(ROOT / path) for path in sorted(inputs)}
        # If the parent is interrupted, the surviving report remains explicitly incomplete.
        (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
        for name in selected:
            report["suites"][name] = run_suite(
                ROOT, manifest["suites"][name], output / name, args.timeout
            )
            if report["suites"][name].get("termination_signal"):
                report["termination_signal"] = report["suites"][name][
                    "termination_signal"
                ]
                break
        report["source_after"] = identity(ROOT)
        report["source_status_unchanged"] = (
            report["source_before"] == report["source_after"]
        )
        report["inputs_unchanged"] = all(
            (ROOT / path).is_file() and digest(ROOT / path) == wanted
            for path, wanted in report["input_sha256"].items()
        )
        report["complete_pass"] = (
            report["source_status_unchanged"]
            and report["inputs_unchanged"]
            and len(report["suites"]) == len(selected)
            and all(r["complete_pass"] for r in report["suites"].values())
        )
        report["exit_status"] = 0 if report["complete_pass"] else 1
        if report.get("termination_signal"):
            report["exit_status"] = 128 + report["termination_signal"]
    except (
        OSError,
        ValueError,
        importlib.metadata.PackageNotFoundError,
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
    ) as exc:
        report["error"] = str(exc)
    report["elapsed_seconds"] = round(time.monotonic() - started, 3)
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return int(report["exit_status"])


if __name__ == "__main__":
    raise SystemExit(main())
