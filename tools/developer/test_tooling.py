"""Acceptance checks for source navigation and complete lightweight test execution."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any

import pytest

from common import digest, private_environment
from navigate import query
from run_tests import run_suite


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """Create a private committed source fixture without inheriting Git hooks."""
    root = tmp_path / "repo"
    root.mkdir()
    env = private_environment(tmp_path)
    (root / "a.py").write_text("def target():\n    return 1\n")
    (root / "b.py").write_text("from a import target as alias\nalias()\n")
    (root / "duplicate.py").write_text("def target():\n    return 2\ntarget()\n")
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
    return root


def test_navigation_alias_duplicate_edit_delete_rename(repo: Path) -> None:
    """Resolve real bindings and refresh edited, renamed, deleted and untracked files."""
    original = query(repo, Path("a.py"), "target", [Path(".")])
    locations = original["semantic_locations"]
    assert any(
        r["file"] == "b.py" and r["line"] == 2 and r["name"] == "alias"
        for r in locations
    )
    assert not any(r["file"] == "duplicate.py" for r in locations)
    assert any(
        r["file"] == "duplicate.py" for r in original["unresolved_text_occurrences"]
    )
    (repo / "b.py").write_text("from a import target as alias\n\nalias()\n")
    edited = query(repo, Path("a.py"), "target", [Path(".")])
    assert edited["dirty"] and edited["source_sha256"] != original["source_sha256"]
    assert any(
        r["file"] == "b.py" and r["line"] == 3 for r in edited["semantic_locations"]
    )
    (repo / "b.py").rename(repo / "renamed.py")
    renamed = query(repo, Path("a.py"), "target", [Path(".")])
    assert any(r["file"] == "renamed.py" for r in renamed["semantic_locations"])
    assert not any(r["file"] == "b.py" for r in renamed["semantic_locations"])
    (repo / "renamed.py").unlink()
    deleted = query(repo, Path("a.py"), "target", [Path(".")])
    assert not any(
        r["file"] in {"b.py", "renamed.py"} for r in deleted["semantic_locations"]
    )
    (repo / "a.py").unlink()
    with pytest.raises(ValueError, match="absent"):
        query(repo, Path("a.py"), "target", [Path(".")])


def test_navigation_is_static_and_excludes_artifacts(repo: Path) -> None:
    """Navigation cannot execute fixture imports or index excluded source copies."""
    marker = repo / "executed"
    (repo / "a.py").write_text(
        f"open({str(marker)!r}, 'w').write('bad')\ndef target():\n    pass\n"
    )
    for folder in ("weights", "state", ".other", "nested"):
        (repo / folder).mkdir()
        (repo / folder / "copy.py").write_text("from a import target\ntarget()\n")
    (repo / "nested" / ".git").mkdir()
    (repo / "linked.py").symlink_to(repo / "b.py")
    result = query(repo, Path("a.py"), "target", [Path(".")])
    assert result["source_files"] == 3
    assert not marker.exists()


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (
            "def test_ok():\n    assert True\n",
            {"collected": 1, "passed": 1, "complete_pass": True},
        ),
        ("def test_bad():\n    assert False\n", {"failed": 1, "complete_pass": False}),
        ("VALUE = 1\n", {"collected": 0, "complete_pass": False}),
        (
            "import pytest\n@pytest.mark.skip(reason='fixture')\ndef test_skip():\n    pass\n",
            {"skipped": 1, "complete_pass": False},
        ),
        (
            "import pytest\npytest.skip('module skip', allow_module_level=True)\n",
            {"skipped": 1, "complete_pass": False},
        ),
        (
            "import nonexistent_developer_fixture\n",
            {"collection_errors": 1, "complete_pass": False},
        ),
        (
            "import pytest\n@pytest.fixture\ndef broken():\n    raise RuntimeError('setup')\ndef test_error(broken):\n    pass\n",
            {"errored": 1, "complete_pass": False},
        ),
        (
            "import pytest\n@pytest.fixture\ndef broken():\n    yield\n    raise RuntimeError('teardown')\ndef test_error(broken):\n    pass\n",
            {"errored": 1, "passed": 0, "complete_pass": False},
        ),
        (
            "import pytest\n@pytest.mark.xfail\ndef test_xpass():\n    assert True\n",
            {"skipped": 1, "complete_pass": False},
        ),
        (
            "import pytest\n@pytest.mark.xfail\ndef test_xfail():\n    assert False\n",
            {"skipped": 1, "complete_pass": False},
        ),
    ],
)
def test_runner_outcomes(tmp_path: Path, source: str, expected: dict[str, Any]) -> None:
    """Exercise actual pytest collection and execution, including misleading zero exits."""
    (tmp_path / "test_case.py").write_text(source)
    result = run_suite(
        tmp_path,
        {
            "file": "test_case.py",
            "origins": {},
            "reviewed_sha256": {"test_case.py": digest(tmp_path / "test_case.py")},
        },
        tmp_path / "report",
        10,
    )
    for key, value in expected.items():
        assert result[key] == value, result
    assert (tmp_path / "report" / "stdout.txt").exists()
    assert (tmp_path / "report" / "stderr.txt").exists()


def test_timeout_kills_children(tmp_path: Path) -> None:
    """A child that would outlive its pytest parent cannot write after timeout."""
    marker = tmp_path / "escaped"
    child = f"import time; from pathlib import Path; time.sleep(2); Path({str(marker)!r}).touch()"
    (tmp_path / "test_slow.py").write_text(
        "import subprocess, sys, time\ndef test_slow():\n"
        f"    subprocess.Popen([sys.executable, '-c', {child!r}])\n"
        f"    open({str(tmp_path / 'started')!r}, 'w').write('started')\n    time.sleep(30)\n"
    )
    result = run_suite(
        tmp_path,
        {
            "file": "test_slow.py",
            "origins": {},
            "reviewed_sha256": {"test_slow.py": digest(tmp_path / "test_slow.py")},
        },
        tmp_path / "report",
        1,
    )
    assert (
        result["timed_out"]
        and result["exit_status"] == 124
        and not result["complete_pass"]
    )
    assert (tmp_path / "started").exists(), "fixture must actually spawn its child"
    time.sleep(2)
    assert not marker.exists()


def test_environment_and_wrong_import_origin(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Ambient pytest/Python/Git settings cannot change admission or import identity."""
    monkeypatch.setenv("PYTEST_ADDOPTS", "--collect-only")
    monkeypatch.setenv("PYTHONPATH", "/another/checkout")
    monkeypatch.setenv("GIT_DIR", "/another/checkout/.git")
    (tmp_path / "local_module.py").write_text("VALUE = 1\n")
    (tmp_path / "test_case.py").write_text(
        "import local_module\ndef test_ok():\n    assert local_module.VALUE == 1\n"
    )
    suite = {
        "file": "test_case.py",
        "origins": {"local_module": "local_module.py"},
        "reviewed_sha256": {
            name: digest(tmp_path / name)
            for name in ("test_case.py", "local_module.py")
        },
    }
    good = run_suite(tmp_path, suite, tmp_path / "good", 10)
    assert good["complete_pass"]
    suite["origins"] = {"local_module": "other.py"}
    bad = run_suite(tmp_path, suite, tmp_path / "bad", 10)
    assert bad["passed"] == 1 and not bad["complete_pass"]


@pytest.mark.parametrize("fault", ["empty", "missing-dependency", "admission-drift"])
def test_cli_refuses_incomplete_setup(repo: Path, tmp_path: Path, fault: str) -> None:
    """The public CLI returns failure and a report before unsafe collection can start."""
    import shutil

    here = Path(__file__).resolve().parent
    copied = repo / "tools" / "developer"
    shutil.copytree(here, copied, ignore=shutil.ignore_patterns("__pycache__"))
    manifest = json.loads((copied / "suites.json").read_text())
    if fault == "empty":
        manifest["default_suites"] = []
        (copied / "suites.json").write_text(json.dumps(manifest))
    elif fault == "missing-dependency":
        with (copied / "requirements.lock").open("a") as stream:
            stream.write("missing-developer-test-dependency==0.0.0\n")
    # The fixture lacks admitted source, which must be refused before collection.
    output = tmp_path / "report"
    completed = subprocess.run(
        [sys.executable, "-B", str(copied / "run_tests.py"), "--output", str(output)],
        cwd=repo,
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert completed.returncode == 1, completed.stderr
    report = json.loads((output / "report.json").read_text())
    assert not report["complete_pass"] and report["error"] and not report["suites"]


def test_run_detects_changed_input_even_with_unchanged_dirty_status(
    repo: Path, tmp_path: Path
) -> None:
    """A green suite that rewrites an already untracked input is still incomplete."""
    import hashlib
    import shutil

    copied = repo / "tools" / "developer"
    shutil.copytree(
        Path(__file__).resolve().parent,
        copied,
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    test_file = repo / "test_mutates.py"
    test_file.write_text(
        "from pathlib import Path\ndef test_mutates():\n"
        "    p = Path(__file__)\n    p.write_text(p.read_text() + '# changed\\n')\n"
    )
    manifest = {
        "default_suites": ["fixture"],
        "suites": {
            "fixture": {
                "file": test_file.name,
                "origins": {},
                "reviewed_sha256": {
                    test_file.name: hashlib.sha256(test_file.read_bytes()).hexdigest()
                },
            }
        },
    }
    (copied / "suites.json").write_text(json.dumps(manifest))
    output = tmp_path / "report"
    completed = subprocess.run(
        [sys.executable, "-B", str(copied / "run_tests.py"), "--output", str(output)],
        cwd=repo,
        capture_output=True,
        text=True,
        timeout=15,
    )
    report = json.loads((output / "report.json").read_text())
    assert completed.returncode == 1 and not report["complete_pass"]
    assert report["source_status_unchanged"] and not report["inputs_unchanged"]
    assert report["suites"]["fixture"]["passed"] == 1
