"""A clean one-commit git checkout: the stand-in for the job's deploy at M, for the writers' "M" (cov2d.deploy_head)."""
from __future__ import annotations

import subprocess
from pathlib import Path

GIT = ["git", "-c", "user.name=cov2d-test", "-c", "user.email=cov2d-test@invalid", "-c", "core.hooksPath=/dev/null",
       "-c", "commit.gpgsign=false"]


def clean_checkout(d: Path) -> tuple[Path, str]:
    """A git checkout under ``d`` with one commit and nothing else in it, and its HEAD."""
    d.mkdir(parents=True, exist_ok=True)
    subprocess.run(GIT + ["init", "-q", str(d)], check=True)
    (d / "f").write_text("deploy\n")
    subprocess.run(GIT + ["-C", str(d), "add", "f"], check=True)
    subprocess.run(GIT + ["-C", str(d), "commit", "-q", "-m", "deploy"], check=True)
    head = subprocess.run(["git", "-C", str(d), "rev-parse", "HEAD"], capture_output=True, text=True, check=True)
    return d, head.stdout.strip()
