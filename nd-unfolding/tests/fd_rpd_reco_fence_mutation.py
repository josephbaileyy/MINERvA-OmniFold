#!/usr/bin/env python3
"""Mutants of custody's sacct-only COV2D fence, each run against the fence tests.

usage: python3 -B tests/fd_rpd_reco_fence_mutation.py --out MUTATIONS.json

Each mutant is a single-fragment change to a temporary copy of fd_rpd_reco_custody.py. The fence tests in
test_fd_rpd_reco.py (`-k cov2d_fence`) load that copy through FD_RPD_CUSTODY_MODULE. Every mutant must fail them.
The unmodified copy must pass them first. Only pytest exit 1 (tests failed) counts as KILLED; any other non-zero exit
(collection error, interrupt, usage) is ERROR and fails the run. The failing test names are recorded. Every thread cap
is 1.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODULE = HERE.parent / "fd_rpd_reco_custody.py"
SUITE = HERE / "test_fd_rpd_reco.py"
SELECT = "cov2d_fence"

MUTANTS = (
    ("stderr-not-merged", "stderr=subprocess.STDOUT,", "stderr=subprocess.PIPE,"),
    ("rc-ignored", "check(result.returncode == 0, ", "check(True, "),
    ("user-dropped", '"-u",\n        "josephrb",\n', ""),
    (
        "named-window-dropped",
        '"-S",\n        COV2D_NAMED_WINDOW[0],\n        "-E",\n        COV2D_NAMED_WINDOW[1],\n',
        "",
    ),
    ("family-start-dropped", '"-S",\n        cov2d_family_start(),\n', ""),
    ("family-end-dropped", '"-E",\n        "now",\n', ""),
    ("family-days-widened", "COV2D_FAMILY_DAYS = 14", "COV2D_FAMILY_DAYS = 60"),
    (
        "blank-skip-broadened",
        "            if not line:\n",
        "            if not line.strip():\n",
    ),
    (
        "field-count-unchecked",
        "len(parts) == 3\n                and COV2D_JOB_ID",
        "COV2D_JOB_ID",
    ),
    (
        "jobid-unchecked",
        "\n                and COV2D_JOB_ID.fullmatch(parts[0]) is not None",
        "",
    ),
    (
        "name-unchecked",
        "\n                and bool(parts[1])\n                and parts[1] == parts[1].strip()",
        "",
    ),
    (
        "family-case-sensitive",
        "name.lower().startswith(COV2D_FAMILIES)",
        "name.startswith(COV2D_FAMILIES)",
    ),
    (
        "launch-error-uncaught",
        "except (OSError, UnicodeDecodeError) as error:",
        "except ImportError as error:",
    ),
    (
        "jobid-unanchored",
        "COV2D_JOB_ID.fullmatch(parts[0])",
        "COV2D_JOB_ID.search(parts[0])",
    ),
    ("state-whole-field", 'words[0] if words else ""', "parts[2]"),
    (
        "family-drops-t2a",
        'COV2D_FAMILIES = ("cov2d", "t2a")',
        'COV2D_FAMILIES = ("cov2d",)',
    ),
    (
        "family-check-skipped",
        "                state in COV2D_TERMINAL,\n",
        "                True,\n",
    ),
    (
        "terminal-adds-pending",
        '        "PREEMPTED",\n',
        '        "PREEMPTED",\n        "PENDING",\n',
    ),
    (
        "terminal-adds-revoked",
        '        "PREEMPTED",\n',
        '        "PREEMPTED",\n        "REVOKED",\n',
    ),
    ("terminal-drops-timeout", '        "TIMEOUT",\n    }\n', "    }\n"),
    ("named-count-skipped", "len(named) == len(COV2D_NAMED_JOBS)\n        and ", ""),
    ("named-presence-skipped", "\n        and set(states) == COV2D_NAMED_JOBS", ""),
    (
        "named-terminal-skipped",
        "\n        and all(s in COV2D_TERMINAL for s in states.values()),",
        ",",
    ),
    (
        "squeue-restored",
        "    named_command = [\n",
        '    subprocess.run(["squeue", "-u", "josephrb", "-h"], text=True, capture_output=True, check=False)\n'
        "    named_command = [\n",
    ),
)


def run_tests(module: Path) -> tuple[int, list[str]]:
    env = {**os.environ, "FD_RPD_CUSTODY_MODULE": str(module)}
    for cap in (
        "OMP_NUM_THREADS",
        "OPENBLAS_NUM_THREADS",
        "MKL_NUM_THREADS",
        "NUMEXPR_NUM_THREADS",
        "VECLIB_MAXIMUM_THREADS",
    ):
        env[cap] = "1"
    command = [
        sys.executable,
        "-B",
        "-m",
        "pytest",
        "-x",
        "-q",
        "-p",
        "no:cacheprovider",
        "--color=no",
        "-rf",
        str(SUITE),
        "-k",
        SELECT,
    ]
    result = subprocess.run(
        command, env=env, capture_output=True, text=True, check=False
    )
    failed = [line for line in result.stdout.splitlines() if line.startswith("FAILED ")]
    return result.returncode, failed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    out = parser.parse_args().out
    source = MODULE.read_text()
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()  # noqa: E731
    outcomes = []
    with tempfile.TemporaryDirectory(prefix="rpd-fence-mutants-") as temporary:
        copy = Path(temporary) / "fd_rpd_reco_custody.py"
        copy.write_text(source)
        control, _ = run_tests(copy)
        print(f"CONTROL   unmodified copy rc={control}", flush=True)
        if control != 0:
            print("FENCE-MUTATION :: the unmodified copy fails the fence tests")
            return 2
        for name, old, new in MUTANTS:
            count = source.count(old)
            if count != 1:
                outcomes.append(
                    {"name": name, "status": "NOT_APPLIED", "occurrences": count}
                )
                print(f"NOT_APPLIED {name} ({count} occurrences)", flush=True)
                continue
            copy.write_text(source.replace(old, new, 1))
            rc, failed = run_tests(copy)
            status = {0: "SURVIVED", 1: "KILLED"}.get(rc, "ERROR")
            outcomes.append(
                {"name": name, "status": status, "pytest_rc": rc, "failed": failed}
            )
            first = failed[0].split(" - ")[0] if failed else ""
            print(f"{status:9} {name} (pytest rc {rc}) {first}", flush=True)
    killed = sum(o["status"] == "KILLED" for o in outcomes)
    record = {
        "schema": "rpd-reco-fence-mutation/1",
        "module_sha256": digest(MODULE),
        "suite_sha256": digest(SUITE),
        "harness_sha256": digest(Path(__file__)),
        "selector": SELECT,
        "required": len(MUTANTS),
        "killed": killed,
        "all_killed": killed == len(MUTANTS),
        "outcomes": outcomes,
    }
    out.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n")
    print(f"FENCE-MUTATION :: {killed}/{len(MUTANTS)} killed")
    return 0 if record["all_killed"] else 1


if __name__ == "__main__":
    sys.exit(main())
