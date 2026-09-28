"""Checkout identity and private environment helpers for local developer tools."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import subprocess
from typing import Any


def git(root: Path, *args: str) -> str:
    """Read Git state without inheriting another checkout's Git environment."""
    env = {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }
    env["GIT_OPTIONAL_LOCKS"] = "0"
    return subprocess.check_output(
        ["git", "-C", str(root), *args], env=env, text=True
    ).strip()


def identity(root: Path) -> dict[str, Any]:
    """Describe a checkout and disclose staged, unstaged, and untracked paths."""
    status = git(root, "status", "--porcelain=v1", "--untracked-files=all")
    return {
        "checkout": str(root),
        "revision": git(root, "rev-parse", "HEAD"),
        "dirty": bool(status),
        "status": status.splitlines(),
    }


def digest(path: Path) -> str:
    """Return the SHA-256 of a file's current bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def private_environment(directory: Path) -> dict[str, str]:
    """Build a minimal environment for admitted local tests and their children."""
    import sys

    home = directory / "home"
    home.mkdir()
    return {
        "PATH": f"{Path(sys.executable).parent}:/usr/bin:/bin",
        "HOME": str(home),
        "TMPDIR": str(directory),
        "TMP": str(directory),
        "TEMP": str(directory),
        "XDG_CACHE_HOME": str(directory / "cache"),
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_TEMPLATE_DIR": str(home),
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
        "LC_ALL": "C",
        "TZ": "UTC",
    }
