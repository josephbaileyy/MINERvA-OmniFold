#!/usr/bin/env python3
"""Mutants of custody's sacct-only COV2D fence, each run against the fence tests.

usage: python3 -B tests/fd_rpd_reco_fence_mutation.py --out MUTATIONS.json

Each mutant is a single-fragment change to a temporary copy of fd_rpd_reco_custody.py. The fence tests in
test_fd_rpd_reco.py (`-k cov2d_fence`) load that copy through FD_RPD_CUSTODY_MODULE. Every mutant must fail them.
The unmodified copy must pass them first. Every thread cap is 1.
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
    ("rc-ignored", "check(accounting.returncode == 0, ", "check(True, "),
    ("user-dropped", '"-u",\n        "josephrb",\n', ""),
    ("start-dropped", '"-S",\n        COV2D_FENCE_START,\n', ""),
    ("end-dropped", '"-E",\n        "now",\n', ""),
    (
        "blank-skip-broadened",
        "        if not line:\n",
        "        if not line.strip():\n",
    ),
    ("field-count-unchecked", "len(fields) == 3 and COV2D_JOB_ID", "COV2D_JOB_ID"),
    (
        "jobid-unchecked",
        "len(fields) == 3 and COV2D_JOB_ID.fullmatch(fields[0]) is not None,",
        "len(fields) == 3,",
    ),
    (
        "jobid-unanchored",
        "COV2D_JOB_ID.fullmatch(fields[0])",
        "COV2D_JOB_ID.search(fields[0])",
    ),
    ("state-whole-field", 'first = words[0] if words else ""', "first = state"),
    (
        "family-drops-t2a",
        'COV2D_FAMILIES = ("cov2d", "t2a")',
        'COV2D_FAMILIES = ("cov2d",)',
    ),
    (
        "family-check-skipped",
        "                first in COV2D_TERMINAL,\n",
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
    ("named-presence-skipped", "set(states) == COV2D_NAMED_JOBS\n        and ", ""),
    (
        "named-terminal-skipped",
        "\n        and all(s in COV2D_TERMINAL for s in states.values()),",
        ",",
    ),
    (
        "squeue-restored",
        '    command = [\n        "sacct",',
        '    subprocess.run(["squeue", "-u", "josephrb", "-h"], text=True, capture_output=True, check=False)\n'
        '    command = [\n        "sacct",',
    ),
)


def run_tests(module: Path) -> int:
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
        str(SUITE),
        "-k",
        SELECT,
    ]
    return subprocess.run(
        command, env=env, capture_output=True, text=True, check=False
    ).returncode


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
        control = run_tests(copy)
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
            rc = run_tests(copy)
            status = "KILLED" if rc != 0 else "SURVIVED"
            outcomes.append({"name": name, "status": status, "pytest_rc": rc})
            print(f"{status:9} {name} (pytest rc {rc})", flush=True)
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
