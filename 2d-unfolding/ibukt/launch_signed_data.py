"""Run the pinned signed-data study with a bounded Linux login-node envelope."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
from contextlib import suppress
import signal
import sys
import time

import rehearse

SCRIPT = Path(__file__).resolve()
REPO = SCRIPT.parents[2]
REFERENCE_COMMIT = "77d76cfc2d621f8faa010b75006811868494652a"
WALL_SECONDS = 480
ADDRESS_SPACE_BYTES = 16 * 1024**3
PINS = {
    "signed_data.py": "0d11502f74b18b09fcae7fa8082c1fa622332bb3c9787622fedac230a17c6170",
    "run_ibukt.py": "f2b4c017e1a2e84c2cb30b43a8824b95c3f7e022f5fca23b0ceac2a750c33683",
    "ibukt.py": "ef8590cf6d6d025b6db1fb8fdd100f76114390ac78eded62274b2c077c290789",
    "config.json": "60d6c4d747596137423a869ac315c484ef65ad69f3ec209d6fd73d6e573c716c",
    "rehearse.py": "ced65b568c23e5fa64ca4750f556cd9bc50de5e0301748cc58143b7012cca1f9",
}


def _run_measured_child(
    command: list[str], out: Path, env: dict[str, str], timeout: float
) -> tuple[int, int]:
    """Measure this child tree and enforce a process-group wall deadline."""
    deadline = time.monotonic() + timeout
    with (out / "study.log").open("x") as log:
        child = subprocess.Popen(
            command,
            cwd=out,
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
        )
        try:
            while time.monotonic() < deadline:
                pid, status, usage = os.wait4(child.pid, os.WNOHANG)
                if pid:
                    child.returncode = os.waitstatus_to_exitcode(status)
                    return child.returncode, int(usage.ru_maxrss)
                time.sleep(min(0.1, max(0, deadline - time.monotonic())))
        finally:
            if child.returncode is None:
                with suppress(ProcessLookupError):
                    os.killpg(child.pid, signal.SIGKILL)
                _, status, usage = os.wait4(child.pid, 0)
                child.returncode = os.waitstatus_to_exitcode(status)
        return 124, int(usage.ru_maxrss)


def launch(stage: Path, reference: Path, out: Path, expected_sha: str) -> int:
    """Verify code and reference identities, then publish one measured receipt."""
    if sys.platform != "linux" or "SLURM_JOB_ID" in os.environ:
        raise ValueError("the study requires a Linux login node")
    expected_python = Path.home() / ".conda/envs/root_6_28/bin/python3"
    if Path(sys.executable).resolve() != expected_python.resolve():
        raise ValueError("activate the pinned ROOT environment")
    scratch = rehearse.scratch_directory()
    if not all(
        path.is_relative_to(scratch) and path != scratch
        for path in (stage, reference, out)
    ):
        raise ValueError("study paths must be below the private scratch root")
    if reference == REPO or out.is_relative_to(stage) or out.is_relative_to(reference):
        raise ValueError("use the historical checkout and a separate fresh output")
    if (
        rehearse.digest(SCRIPT) != expected_sha
        or rehearse.digest(rehearse.GUARD) != rehearse.GUARD_SHA
    ):
        raise ValueError("signed-data launcher or import guard changed")
    for name, pin in PINS.items():
        if rehearse.digest(SCRIPT.with_name(name)) != pin:
            raise ValueError(f"signed-data source changed: {name}")

    env = {
        key: value
        for key, value in os.environ.items()
        if key not in {"PYTHONPATH", "PYTHONHOME", "BASH_ENV", "ENV"}
    }
    env.update(
        GIT_OPTIONAL_LOCKS="0",
        OMP_NUM_THREADS="1",
        MKL_NUM_THREADS="1",
        OPENBLAS_NUM_THREADS="1",
        NUMEXPR_NUM_THREADS="1",
        CUDA_VISIBLE_DEVICES="",
        PYTHONNOUSERSITE="1",
        PYTHONDONTWRITEBYTECODE="1",
    )

    def git(*args: str) -> str:
        return subprocess.check_output(
            ["git", "-C", str(reference), *args], text=True, env=env, timeout=10
        ).strip()

    if git("rev-parse", "--show-toplevel", "HEAD").splitlines() != [
        str(reference),
        REFERENCE_COMMIT,
    ] or git("status", "--porcelain"):
        raise ValueError(
            "historical REF-C2C1 checkout is not clean at the declared commit"
        )

    os.umask(0o077)
    out.mkdir(mode=0o700, exist_ok=False)
    work = out / "study"
    mpl = out / "mpl"
    mpl.mkdir()
    env["MPLCONFIGDIR"] = str(mpl)
    command = [
        "/usr/bin/prlimit",
        f"--as={ADDRESS_SPACE_BYTES}",
        "--",
        sys.executable,
        "-B",
        str(rehearse.GUARD),
        "--expect-root",
        str(REPO),
        "--allow",
        str(reference),
        "--inventory",
        str(out / "imports.jsonl"),
        "--label",
        "ibu-signed-data",
        "--",
        str(SCRIPT.with_name("signed_data.py")),
        "--stage",
        str(stage),
        "--out",
        str(work),
        "--reference",
        str(reference),
    ]
    started = time.monotonic()
    # exec prlimit via the bounded helper. Collect its direct child's RSS through
    # wait4 so earlier git checks cannot contaminate the high-water measurement.
    max_rss = None
    try:
        status, max_rss = _run_measured_child(command, out, env, WALL_SECONDS)
        physics = work / ("readout.json" if status == 0 else "STOP.json")
        receipt = json.loads(physics.read_text()) if physics.is_file() else {}
        if not isinstance(receipt, dict):
            raise ValueError("child receipt must be an object")
    except OSError as exc:
        status, max_rss, receipt = 125, None, {"reason": str(exc)}
    except (ValueError, TypeError) as exc:
        status, receipt = 125, {"reason": f"invalid child receipt: {exc}"}
    elapsed = time.monotonic() - started
    receipt_name = "readout.json" if status == 0 else "STOP.json"
    if status == 0 and receipt.get("status") != "PASS":
        status = 125
        receipt_name = "STOP.json"
        receipt = {"reason": "guarded child exited without a PASS receipt"}
    if status:
        receipt.setdefault("reason", f"guarded child exited with status {status}")
    receipt.update(
        status="STOP" if status else "PASS",
        child_status=status,
        reference_commit=REFERENCE_COMMIT,
        launcher_sha256=expected_sha,
        node_hours=0,
        wall_seconds=elapsed,
        max_rss_kib=max_rss,
        time_limit_seconds=WALL_SECONDS,
        address_space_limit_bytes=ADDRESS_SPACE_BYTES,
    )
    with (out / receipt_name).open("x") as stream:
        json.dump(receipt, stream, indent=2, allow_nan=False)
        stream.write("\n")
    return status


def main() -> None:
    """Parse the explicitly pinned launcher and staged operands."""
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("stage", "reference", "out"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--sha256", required=True)
    args = parser.parse_args()
    raise SystemExit(
        launch(
            args.stage.resolve(),
            args.reference.resolve(),
            args.out.resolve(),
            args.sha256,
        )
    )


if __name__ == "__main__":
    main()
