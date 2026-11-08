#!/usr/bin/env python3
"""Data-free MAT/ROOT trace: interpreter, module imports and MnvH1D dictionary only.

Prepare checks instrument code before tracing. No declared data, MAT data or
COV2D input is opened. PASS requires the traced child to exit normally and every
open to satisfy the drafted policy. The full flux connect is a separate gate.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import fd_rpd_reco as r
import fd_rpd_reco_custody as custody


def prepare(config_path: Path, checksum: str, run: Path) -> str:
    """Prepare instrument provenance and a policy without opening declared data."""
    r.require_output_root(run)
    run.mkdir(parents=True, exist_ok=True)
    r.require(
        not (run / "prologue-prepare-reference.json").exists(),
        "OUTPUT_EXISTS",
        "fresh prologue run required",
    )
    copied = r.stage_copy(config_path, run / "policy-config.json", checksum)
    config = json.loads(copied.read_text())
    policy_paths = [
        config["dump_root"],
        config["flux_root"],
        *config["trace_environment_roots"],
        *config["trace_instrument_directories"],
        *config["cov2d_protected_paths"],
    ]
    policy_paths += [
        config[key]["path"]
        for key in (
            "pins",
            "h2",
            "inventory",
            "constants",
            "flux_source",
            "mat_dependencies",
        )
    ]
    r.require(
        all(
            isinstance(path, str) and Path(path).is_absolute() and "${" not in path
            for path in policy_paths
        ),
        "MAT_PREPARE",
        "resolve every policy path before the data-free trace; source/physics fields may remain DRAFT",
    )
    _, environment = r.checked_mat_environment()
    instrument = r.load_mat_instrument()
    files = {}
    # Declared identities are policy metadata only; none of these paths is opened.
    for key in (
        "pins",
        "h2",
        "inventory",
        "constants",
        "flux_source",
        "mat_dependencies",
    ):
        path = str(Path(config[key]["path"]).resolve())
        files[path] = {"original": path}
    prepared: r.Json = {
        "status": "PASS",
        "run": str(run.resolve()),
        "connect_id": os.environ["FD_RPD_RECO_CONNECT_ID"],
        "prepare_time_ns": time.time_ns(),
        "environment_after_setup": custody.environment_record(),
        "environment_snapshot": custody.environment_snapshot(),
        "mat_environment": environment,
        "mapped_mat_stats": {},
        "instrument_files": [],
        "original_mat_prefixes": {
            key: os.environ[key] for key in ("PLOTUTILSROOT", "MPARAMFILES")
        },
        "mat_prefixes": {},
        "files": files,
        "module_paths": custody.module_paths(),
    }
    for filename in environment["mapped_mat_files"]:
        info = Path(filename).stat()
        prepared["mapped_mat_stats"][filename] = [
            info.st_dev,
            info.st_ino,
            info.st_size,
        ]
    for index, (filename, digest) in enumerate(
        {**instrument.MAT_SETUP, **instrument.MAT_FILES}.items()
    ):
        source = Path(filename)
        before = custody.source_stat(source)
        copy = r.stage_copy(
            source, run / "instrument" / f"{index}-{source.name}", digest
        )
        r.require(
            before == custody.source_stat(source),
            "MAT_PREPARE",
            "instrument source stat/atime changed",
        )
        prepared["instrument_files"].append(
            {"staged": str(copy), "sha256": digest, "stat_before": before}
        )
    prepared["private_prepare_path"] = str(
        custody.private_prepare_path(run, "prologue-prepare", prepared["connect_id"])
    )
    policy = custody.build_trace_policy(config, prepared, run)
    r.write_json(run / "trace-policy.json", policy)
    prepared["trace_policy_sha256"] = r.digest(run / "trace-policy.json")
    reference = custody.write_private_prepare(
        r, run, "prologue-prepare", prepared, protected_roots=policy["protected_roots"]
    )
    return r.digest(reference)


def main() -> int:
    """Keep a crashing or refusing prologue from publishing a passing receipt."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--config-sha256")
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--prepare-sha256", help=argparse.SUPPRESS)
    args = parser.parse_args()
    prepared: r.Json | None = None
    try:
        r.require_output_root(args.run)
        if args.worker:
            path = args.run / "prologue-prepare-reference.json"
            r.require(
                r.digest(path) == args.prepare_sha256,
                "MAT_PREPARE",
                "prologue prepare changed",
            )
            prepared = custody.read_private_prepare(
                r, path, args.prepare_sha256, args.run
            )
            environment = r.checked_prepared_mat(
                SimpleNamespace(run=args.run.resolve(), prestage=prepared)
            )[1]
            r.write_json(
                args.run / "prologue-worker.json",
                {
                    "status": "PASS",
                    "environment": environment,
                    "code_sha256": r.digest(Path(r.__file__)),
                    "data_keys_read": [],
                },
            )
            return 0
        r.require(
            args.config is not None and args.config_sha256 is not None,
            "MAT_PREPARE",
            "pinned draft policy config required",
        )
        checksum = prepare(args.config, args.config_sha256, args.run)
        trace = args.run / "prologue.strace"
        command = [
            "/usr/bin/strace",
            "-f",
            "-yy",
            "-s",
            "4096",
            "-e",
            "trace=open,openat,openat2,chdir,fchdir",
            "-o",
            str(trace),
            sys.executable,
            str(Path(__file__)),
            "--worker",
            "--run",
            str(args.run),
            "--prepare-sha256",
            checksum,
        ]
        child = subprocess.run(command, text=True, capture_output=True, check=False)
        (args.run / "worker.stdout.txt").write_text(child.stdout)
        (args.run / "worker.stderr.txt").write_text(child.stderr)
        r.require(
            child.returncode == 0,
            "MAT_WORKER_EXIT",
            f"prologue worker exited {child.returncode}",
        )
        policy = json.loads((args.run / "trace-policy.json").read_text())
        result = custody.classify_trace(trace.read_text().splitlines(), policy)
        worker = json.loads((args.run / "prologue-worker.json").read_text())
        r.require(
            worker.get("status") == "PASS" and worker.get("data_keys_read") == [],
            "MAT_WORKER_EXIT",
            "invalid prologue worker record",
        )
        r.write_json(
            args.run / "data-free-trace.json",
            {
                **result,
                "scope": "data-free prologue only; no full-connect permission",
                "worker_exit_code": child.returncode,
                "prepare_sha256": checksum,
                "policy_sha256": r.digest(args.run / "trace-policy.json"),
                "trace_sha256": r.digest(trace),
                "producer_sha256": r.digest(Path(r.__file__)),
                "custody_sha256": r.digest(Path(custody.__file__)),
            },
        )
    except (
        r.Refused,
        custody.CustodyRefused,
        OSError,
        ValueError,
        KeyError,
        ImportError,
    ) as error:
        print(f"STOP DATA_FREE_TRACE: {error}", file=sys.stderr)
        if args.worker and isinstance(error, r.Refused):
            if prepared is not None:
                error.details = custody.public_record(
                    error.details,
                    prepared.get("environment_snapshot", {}),
                    custody.environment_snapshot(),
                )
            print(json.dumps(error.details, sort_keys=True), file=sys.stderr)
            try:
                r.require_output_root(args.run)
            except (r.Refused, OSError, ValueError):
                return 4
            r.write_json(
                args.run / "prologue-worker.STOP.json",
                {
                    "status": "STOP",
                    "guard": error.guard,
                    "details": error.details,
                },
            )
        return 4
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
