#!/usr/bin/env python3
"""Start Codex MCP with a named account home, independent of overridden HOME."""

import os
from pathlib import Path
import pwd
import sys


if len(sys.argv) < 2 or sys.argv[1] not in {"personal", "school"}:
    raise SystemExit("usage: codex-mcp-account.py <personal|school> [codex options]")

account = sys.argv[1]
login_home = Path(pwd.getpwuid(os.getuid()).pw_dir)
environment = os.environ.copy()
environment["CODEX_HOME"] = str(login_home / "codex-homes" / account)
os.execvpe(
    "codex",
    ["codex", "mcp-server", *sys.argv[2:]],
    environment,
)
