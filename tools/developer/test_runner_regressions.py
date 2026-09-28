"""Regressions for admitted source, package collection, and process lifecycle."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import py_compile
import shutil
import signal
import subprocess
import sys
import time
from typing import Any

import pytest

from common import private_environment

# An alternate committed checkout lets the same assertions measure the before case.
SOURCE = Path(
    os.environ.get("DEVELOPER_TOOLING_TEST_SOURCE", Path(__file__).parent)
).resolve()


@pytest.fixture
def checkout(tmp_path: Path) -> Path:
    """Create a private Git checkout containing the runner under test."""
    root = tmp_path / "repo"
    shutil.copytree(
        SOURCE, root / "tools/developer", ignore=shutil.ignore_patterns("__pycache__")
    )
    (root / ".gitignore").write_text("__pycache__/\n")
    return root


def _freeze(root: Path) -> None:
    environment = root.parent / "git-environment"
    environment.mkdir(exist_ok=True)
    home = environment / "home"
    if home.exists():
        shutil.rmtree(home)
    env = private_environment(environment)
    for args in (
        ["init", "-q"],
        ["add", "."],
        [
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.invalid",
            "commit",
            "-qm",
            "fixture",
        ],
    ):
        subprocess.run(
            ["git", *args], cwd=root, env=env, check=True, capture_output=True
        )


def _admit(root: Path, paths: list[str], origins: dict[str, str]) -> None:
    suite = {
        "file": paths[0],
        "origins": origins,
        "reviewed_sha256": {
            path: hashlib.sha256((root / path).read_bytes()).hexdigest()
            for path in paths
        },
    }
    (root / "tools/developer/suites.json").write_text(
        json.dumps(
            {
                "default_suites": ["fixture"],
                "suites": {"fixture": suite},
            }
        )
    )
    _freeze(root)


def _command(root: Path, output: Path) -> list[str]:
    return [
        sys.executable,
        "-B",
        str(root / "tools/developer/run_tests.py"),
        "--output",
        str(output),
    ]


def _run(root: Path, output: Path) -> tuple[int, dict[str, Any]]:
    completed = subprocess.run(
        _command(root, output), cwd=root, capture_output=True, text=True, timeout=15
    )
    assert (output / "report.json").exists(), completed.stdout + completed.stderr
    return completed.returncode, json.loads((output / "report.json").read_text())


@pytest.mark.parametrize("child_import", [False, True], ids=["worker", "python-child"])
def test_cached_bytecode_cannot_override_admitted_source(
    checkout: Path, tmp_path: Path, child_import: bool
) -> None:
    """Timestamp-valid stale bytecode must not replace the currently admitted bytes."""
    module = checkout / "local_module.py"
    module.write_text("VALUE = 1\n")
    stamp = module.stat().st_mtime_ns
    compiled = py_compile.compile(
        str(module),
        doraise=True,
        invalidation_mode=py_compile.PycInvalidationMode.TIMESTAMP,
    )
    assert compiled is not None
    cached = Path(compiled)
    cached_bytes = cached.read_bytes()
    module.write_text("VALUE = 2\n")
    os.utime(module, ns=(stamp, stamp))
    if child_import:
        source = "import subprocess, sys\ndef test_value():\n    result = subprocess.check_output([sys.executable, '-c', 'import local_module; print(local_module.VALUE)'], text=True)\n    assert result.strip() == '1'\n"
    else:
        source = "import local_module\ndef test_value():\n    assert local_module.VALUE == 1\n"
    test = checkout / "test_case.py"
    test.write_text(source)
    origins = {} if child_import else {"local_module": "local_module.py"}
    _admit(checkout, [test.name, module.name], origins)
    code, report = _run(checkout, tmp_path / "stale-report")
    assert code == 1 and not report["complete_pass"], report
    assert report["suites"]["fixture"]["failed"] == 1
    assert cached.read_bytes() == cached_bytes, "shared cache must remain untouched"
    # Positive control: an assertion about the admitted value must pass.
    test.write_text(source.replace("== '1'", "== '2'").replace("== 1", "== 2"))
    _admit(checkout, [test.name, module.name], origins)
    code, report = _run(checkout, tmp_path / "current-report")
    assert code == 0 and report["complete_pass"], report


def test_new_initializer_cannot_expand_default_admission(
    checkout: Path, tmp_path: Path
) -> None:
    """The unchanged default manifest refuses an added implicit package initializer."""
    manifest_bytes = (SOURCE / "suites.json").read_bytes()
    manifest = json.loads(manifest_bytes)
    for name in manifest["default_suites"]:
        for relative in manifest["suites"][name]["reviewed_sha256"]:
            target = checkout / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(SOURCE.parents[1] / relative, target)
    marker = tmp_path / "initializer-executed"
    initializer = checkout / "docs/orchestration/__init__.py"
    initializer.write_text(f"from pathlib import Path\nPath({str(marker)!r}).touch()\n")
    _freeze(checkout)
    code, report = _run(checkout, tmp_path / "report")
    assert not marker.exists(), "unreviewed initializer executed during collection"
    assert code != 0 and not report["complete_pass"], report
    assert (checkout / "tools/developer/suites.json").read_bytes() == manifest_bytes


def test_imported_package_initializer_requires_admission(
    checkout: Path, tmp_path: Path
) -> None:
    """Explicit package imports during collection use the same admission boundary."""
    package = checkout / "helper_package"
    package.mkdir()
    marker = tmp_path / "import-executed"
    initializer = package / "__init__.py"
    initializer.write_text(
        f"from pathlib import Path\nPath({str(marker)!r}).touch()\nVALUE = 2\n"
    )
    test = checkout / "test_case.py"
    test.write_text(
        "import helper_package\ndef test_value():\n    assert helper_package.VALUE == 2\n"
    )
    _admit(checkout, [test.name], {})
    code, report = _run(checkout, tmp_path / "unreviewed")
    assert not marker.exists(), "unreviewed imported initializer executed"
    assert code != 0 and not report["complete_pass"], report
    # Deliberately admitting the reviewed initializer permits its useful behavior.
    _admit(checkout, [test.name, "helper_package/__init__.py"], {})
    code, report = _run(checkout, tmp_path / "reviewed")
    assert code == 0 and report["complete_pass"] and marker.exists(), report
    marker.unlink()
    initializer.write_text(initializer.read_text() + "# changed\n")
    code, report = _run(checkout, tmp_path / "changed")
    assert code != 0 and not report["complete_pass"] and not marker.exists()


def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


@pytest.mark.parametrize(
    "termination", [signal.SIGTERM, signal.SIGHUP], ids=["SIGTERM", "SIGHUP"]
)
def test_parent_signal_stops_worker_and_child(
    checkout: Path, tmp_path: Path, termination: int
) -> None:
    """Catchable parent termination stops an ordinary worker group within a bound."""
    started = tmp_path / "started.json"
    release = tmp_path / "release-child"
    escaped = tmp_path / "escaped"
    child = f"import time\nfrom pathlib import Path\nwhile not Path({str(release)!r}).exists():\n    time.sleep(0.02)\nPath({str(escaped)!r}).touch()\n"
    (checkout / "test_case.py").write_text(
        "import json, os, subprocess, sys, time\nfrom pathlib import Path\ndef test_wait():\n"
        f"    child = subprocess.Popen([sys.executable, '-B', '-c', {child!r}])\n"
        f"    Path({str(started)!r}).write_text(json.dumps({{'worker': os.getpid(), 'child': child.pid}}))\n"
        "    time.sleep(30)\n"
    )
    _admit(checkout, ["test_case.py"], {})
    output = tmp_path / "report"
    pids: dict[str, int] = {}
    with (tmp_path / "cli.txt").open("w") as stream:
        parent = subprocess.Popen(
            _command(checkout, output), cwd=checkout, stdout=stream, stderr=stream
        )
        try:
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline:
                try:
                    pids = json.loads(started.read_text())
                    break
                except (FileNotFoundError, json.JSONDecodeError):
                    assert parent.poll() is None, (tmp_path / "cli.txt").read_text()
                    time.sleep(0.02)
            assert pids, "fixture must start both worker and child"
            parent.send_signal(termination)
            parent.wait(timeout=5)
            release.touch()
            deadline = time.monotonic() + 2
            while (
                any(_alive(pid) for pid in pids.values())
                and time.monotonic() < deadline
            ):
                time.sleep(0.02)
            assert not any(
                _alive(pid) for pid in pids.values()
            ), "ordinary worker/child survived parent termination"
            assert not escaped.exists(), "child executed after its parent stopped"
            assert parent.returncode == 128 + termination
            report = json.loads((output / "report.json").read_text())
            assert (
                not report["complete_pass"]
                and report["termination_signal"] == termination
            )
        finally:
            if pids:
                try:
                    os.killpg(pids["worker"], signal.SIGKILL)
                except ProcessLookupError:
                    pass
            if parent.poll() is None:
                parent.kill()
            parent.wait(timeout=5)


def test_initializer_outside_checkout_is_not_an_environment_dependency(
    checkout: Path, tmp_path: Path
) -> None:
    """A source path to another tree cannot admit that tree's package implicitly."""
    package = tmp_path / "external_package"
    package.mkdir()
    marker = tmp_path / "external-init-executed"
    (package / "__init__.py").write_text(
        f"from pathlib import Path\nPath({str(marker)!r}).touch()\n"
    )
    (checkout / "test_case.py").write_text(
        f"import sys\nsys.path.insert(0, {str(tmp_path)!r})\nimport external_package\ndef test_ok():\n    pass\n"
    )
    _admit(checkout, ["test_case.py"], {})
    code, report = _run(checkout, tmp_path / "report")
    assert code != 0 and not report["complete_pass"] and not marker.exists()


@pytest.mark.parametrize("tracked", [False, True], ids=["untracked", "tracked"])
def test_stdlib_shadow_cannot_execute(
    checkout: Path, tmp_path: Path, tracked: bool
) -> None:
    """An unlisted secrets module is refused before its import-time marker write."""
    manifest = json.loads((SOURCE / "suites.json").read_text())
    for name in manifest["default_suites"]:
        for relative in manifest["suites"][name]["reviewed_sha256"]:
            target = checkout / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(SOURCE.parents[1] / relative, target)
    _freeze(checkout)
    marker = tmp_path / "shadow-executed"
    (checkout / "docs/orchestration/secrets.py").write_text(
        f"from pathlib import Path\nPath({str(marker)!r}).touch()\n"
    )
    if tracked:
        _freeze(checkout)
    code, report = _run(checkout, tmp_path / "report")
    assert not marker.exists(), "unreviewed checkout module executed"
    assert code != 0 and not report["complete_pass"]


def test_runner_common_cache_is_ignored(checkout: Path, tmp_path: Path) -> None:
    """The documented -B launch reads current common.py despite valid old bytecode."""
    helper = checkout / "tools/developer/common.py"
    source = helper.read_text()
    marker = tmp_path / "cached-helper-executed"
    stale = source + f"\nPath({str(marker)!r}).touch()\n"
    helper.write_text(stale)
    stamp = helper.stat().st_mtime_ns
    py_compile.compile(
        str(helper),
        doraise=True,
        invalidation_mode=py_compile.PycInvalidationMode.TIMESTAMP,
    )
    helper.write_text(
        source + "\n#" + " " * (len(stale.encode()) - len(source.encode()) - 3) + "\n"
    )
    assert helper.stat().st_size == len(stale.encode())
    os.utime(helper, ns=(stamp, stamp))
    (checkout / "test_case.py").write_text("def test_ok():\n    pass\n")
    _admit(checkout, ["test_case.py"], {})
    code, report = _run(checkout, tmp_path / "report")
    assert not marker.exists(), "runner executed cached common.py"
    assert code == 0 and report["complete_pass"]


@pytest.mark.parametrize("termination", [signal.SIGTERM, signal.SIGHUP])
def test_reap_timeout_retains_signal_report(
    checkout: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, termination: int
) -> None:
    """A controlled failed reap retains the suite, signal exit and worker diagnostic."""
    import importlib.util

    (checkout / "test_case.py").write_text("def test_ok():\n    pass\n")
    _admit(checkout, ["test_case.py"], {})
    spec = importlib.util.spec_from_file_location(
        "runner_probe", checkout / "tools/developer/run_tests.py"
    )
    assert spec is not None and spec.loader is not None
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    output = tmp_path / "report"
    killed: list[tuple[int, int]] = []

    class Worker:
        pid = 12345

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            kwargs["stderr"].write("controlled worker diagnostic\n")

        def wait(self, timeout: float) -> int:
            if timeout != 5:
                handler = signal.getsignal(termination)
                assert callable(handler)
                handler(termination, None)
            raise subprocess.TimeoutExpired("controlled-worker", timeout)

    monkeypatch.setattr(runner.platform, "platform", lambda: "controlled-platform")
    monkeypatch.setattr(runner, "identity", lambda root: {})
    monkeypatch.setattr(runner, "git", lambda *args: "test-git")
    monkeypatch.setattr(runner.subprocess, "Popen", Worker)
    monkeypatch.setattr(runner.os, "killpg", lambda pid, sig: killed.append((pid, sig)))
    monkeypatch.setattr(sys, "argv", ["run_tests.py", "--output", str(output)])
    assert runner.main() == 128 + termination
    report = json.loads((output / "report.json").read_text())
    suite = report["suites"]["fixture"]
    assert suite["termination_signal"] == termination
    assert suite["exit_status"] == 128 + termination
    assert suite["cleanup_timed_out"] and suite["cleanup_error"]
    assert not suite["complete_pass"] and not report["complete_pass"]
    assert killed == [(12345, signal.SIGKILL)]
    assert (
        output / "fixture/stderr.txt"
    ).read_text() == "controlled worker diagnostic\n"
