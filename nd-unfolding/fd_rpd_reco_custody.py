#!/usr/bin/env python3
"""Fresh staging and syscall custody for the RPD-RECO MAT extraction.

The prepare operation runs before tracing, after the refusing COV2D fence. The
extract then uses only those checked copies. No operation submits a job or grants
permission for P0. The numerical environment consumes the pinned extract and a
separately pinned passing custody receipt.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

Json = dict[str, Any]


class CustodyRefused(ValueError):
    """The extraction's file custody has not been demonstrated."""

    def __init__(self, message: str, details: Json | None = None):
        self.details = details
        super().__init__(message)


def require(condition: bool, message: str) -> None:
    """Refuse an incomplete or inconsistent boundary record."""
    if not condition:
        raise CustodyRefused(message)


def module_paths() -> Json:
    """Record every imported module with an on-disk origin."""
    return {
        name: str(Path(filename).resolve())
        for name, module in sorted(sys.modules.items())
        for filename in [getattr(module, "__file__", None)]
        if isinstance(filename, str)
    }


def environment_record() -> Json:
    """Preserve setup's environment while redacting credential-bearing fields."""
    secret = re.compile(
        r"TOKEN|SECRET|PASSWORD|PASSWD|CREDENTIAL|COOKIE|AUTH|PRIVATE_KEY|ACCESS_KEY|API_KEY|BEARER|CONNECTION_STRING|SERVICE_ACCOUNT",
        re.I,
    )
    return {
        key: (
            "<redacted credential field>"
            if secret.search(key)
            else re.sub(r"(://)[^/@\s]+:[^/@\s]+@", r"\1<redacted>@", value)
        )
        for key, value in sorted(os.environ.items())
    }


def source_stat(path: Path) -> Json:
    """Record source metadata without opening the file."""
    info = path.stat()
    return {
        "device": info.st_dev,
        "inode": info.st_ino,
        "bytes": info.st_size,
        "mtime_ns": info.st_mtime_ns,
        "atime_ns": info.st_atime_ns,
    }


def noatime_digest(r: Any, path: Path) -> str:
    """Measure a newly inventoried MAT dependency without changing access time."""
    descriptor = os.open(path, os.O_RDONLY | r.noatime_flag())
    checksum = hashlib.sha256()
    with os.fdopen(descriptor, "rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            checksum.update(block)
    return checksum.hexdigest()


def cov2d_fence() -> Json:
    """Require an empty cov2d queue and both named jobs in a terminal state.

    This is run locally on the run lane's cluster login, never over an implicit
    SSH connection. The connect records output and exit status before staging.
    """
    queue = subprocess.run(
        ["squeue", "-u", "josephrb", "-h", "-o", "%i|%j|%T|%M|%l"],
        text=True,
        capture_output=True,
        check=False,
    )
    record: Json = {
        "queue_exit_code": queue.returncode,
        "queue_stdout": queue.stdout,
        "queue_stderr": queue.stderr,
    }

    def check(condition: bool, message: str) -> None:
        if not condition:
            raise CustodyRefused(
                message,
                {**record, "status": "STOP", "exit_code": 3, "message": message},
            )

    check(queue.returncode == 0, "COV2D fence: squeue failed; treat as RUNNING")
    hits = [
        line
        for line in queue.stdout.splitlines()
        if len(line.split("|")) > 1 and line.split("|")[1].startswith("cov2d-")
    ]
    check(not hits, "COV2D fence: cov2d jobs queued or running: " + repr(hits))
    accounting = subprocess.run(
        [
            "sacct",
            "-X",
            "-n",
            "-P",
            "-j",
            "60909280,60911676",
            "--format=JobIDRaw,State",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    record.update(
        {
            "sacct_exit_code": accounting.returncode,
            "sacct_stdout": accounting.stdout,
            "sacct_stderr": accounting.stderr,
        }
    )
    check(accounting.returncode == 0, "COV2D fence: sacct failed")
    states = {}
    for line in accounting.stdout.splitlines():
        fields = line.split("|")
        if len(fields) >= 2 and fields[0] in {"60909280", "60911676"}:
            states[fields[0]] = fields[1].split()[0]
    terminal = {
        "COMPLETED",
        "FAILED",
        "CANCELLED",
        "TIMEOUT",
        "OUT_OF_MEMORY",
        "NODE_FAIL",
        "PREEMPTED",
        "BOOT_FAIL",
        "DEADLINE",
        "REVOKED",
    }
    check(
        set(states) == {"60909280", "60911676"}
        and all(s in terminal for s in states.values()),
        "COV2D fence: missing or nonterminal named job",
    )
    return {**record, "status": "PASS", "exit_code": 0, "terminal_states": states}


def prepare(r: Any, config_path: Path, config_sha: str, run: Path) -> Json:
    """Freshly stage all bound inputs and the fifteen static MAT dependencies."""
    r.require_output_root(run)
    require(not (run / "prestage.json").exists(), "fresh prestage required")
    run.mkdir(parents=True, exist_ok=True)
    config_copy = r.stage_copy(config_path, run / "original-config.json", config_sha)
    config = json.loads(config_copy.read_text())
    require(
        config.get("configuration_status") == "READY",
        "production config is still DRAFT",
    )
    require(
        bool(os.environ.get("FD_RPD_RECO_CONNECT_ID")), "explicit connect ID required"
    )
    _, mat_environment = r.checked_mat_environment()
    instrument = r.load_mat_instrument()
    try:
        fence = cov2d_fence()
    except (CustodyRefused, OSError) as error:
        r.write_json(
            run / "cov2d-fence.STOP.json",
            getattr(error, "details", None)
            or {
                "status": "STOP",
                "exit_code": 3,
                "message": str(error),
            },
        )
        raise
    r.write_json(run / "cov2d-fence.json", fence)
    files: Json = {}

    def copy(path: Path, expected: str | None, destination: Path | None = None) -> Json:
        key = str(path.resolve())
        if key in files:
            require(
                expected is None or files[key]["sha256"] == expected,
                "conflicting source pin",
            )
            result: Json = files[key]
            return result
        before = source_stat(path)
        checksum = expected if expected is not None else noatime_digest(r, path)
        label = hashlib.sha256(key.encode()).hexdigest()[:16]
        target = destination or run / "original-inputs" / f"{label}-{path.name}"
        r.stage_copy(path, target, checksum)
        after = source_stat(path)
        require(
            before == after, "source stat or atime changed during fresh stage: " + key
        )
        item = {
            "original": key,
            "staged": str(target.resolve()),
            "sha256": checksum,
            "stat_before": before,
            "stat_after": after,
        }
        files[key] = item
        return item

    for key in (
        "pins",
        "h2",
        "inventory",
        "constants",
        "flux_source",
        "mat_dependencies",
    ):
        spec = config[key]
        copy(Path(spec["path"]), spec["sha256"])
    probe = r.Inputs(config_path, config_sha, run / "prepare-check")
    probe.load_pins()
    for path, checksum in probe.pins.values():
        copy(path, checksum)
    selected = r.selected_flux_files(probe)
    for spec in selected.values():
        copy(Path(spec["original_path"]), spec["sha256"])
    inventory = json.loads(
        Path(
            files[str(Path(config["mat_dependencies"]["path"]).resolve())]["staged"]
        ).read_text()
    )
    expected = {
        (
            "PLOTUTILSROOT",
            f"data/flux/flux-{family}-pdg{pdg}-minervame{group}_rearrangedUniverses.root",
        )
        for group in ("1D", "1M", "1N")
        for pdg in (14, -14)
        for family in ("gen2thin", "g4numiv6")
    } | {
        ("PLOTUTILSROOT", "data/lowNuReweight/lowNuReweight.root"),
        ("PLOTUTILSROOT", "data/flux/sys/Muon_Energy_MnvH1D.root"),
        ("MPARAMFILES", "FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt"),
    }
    entries = inventory["entries"]
    require(
        len(entries) == 15
        and {(e["environment_key"], e["relative_path"]) for e in entries} == expected,
        "MAT static inventory differs from the closed fifteen-path set",
    )
    prefixes = {
        key: str((run / "mat-data" / key).resolve())
        for key in ("PLOTUTILSROOT", "MPARAMFILES")
    }
    original_prefixes = {key: os.environ[key] for key in prefixes}
    dependencies = []
    for item in entries:
        key, relative = item["environment_key"], item["relative_path"]
        source = Path(original_prefixes[key]) / relative
        require(
            not Path(relative).is_absolute() and ".." not in Path(relative).parts,
            "MAT dependency escapes its declared lookup root",
        )
        # If selected source was staged earlier, create the required native lookup path too.
        target = Path(prefixes[key]) / relative
        staged = copy(source, None)
        r.stage_copy(Path(staged["staged"]), target, staged["sha256"])
        if item.get("role") == "constrained-numerator-input" and item.get("pdg") == 14:
            require(
                staged["sha256"] == selected[item["playlist_group"]]["sha256"],
                "native constructor input differs from C-N inventory selection",
            )
        dependencies.append({**item, **staged, "staged": str(target.resolve())})
    instrument_files = []
    for filename, checksum in {**instrument.MAT_SETUP, **instrument.MAT_FILES}.items():
        instrument_files.append(copy(Path(filename), checksum))
    mapped_mat_stats = {}
    for filename in mat_environment["mapped_mat_files"]:
        info = Path(filename).stat()
        mapped_mat_stats[filename] = [info.st_dev, info.st_ino, info.st_size]
    listing = {}
    for path in Path(config["dump_root"]).iterdir():
        if path.is_file():
            info = path.stat()
            listing[path.name] = {
                "name": path.name,
                "bytes": info.st_size,
                "mtime_ns": info.st_mtime_ns,
            }
    manifest = {
        "schema": "fd-rpd-reco-prestage/1",
        "status": "PASS",
        "files": files,
        "run": str(run.resolve()),
        "connect_id": os.environ["FD_RPD_RECO_CONNECT_ID"],
        "prepare_time_ns": time.time_ns(),
        "mat_environment": mat_environment,
        "instrument_files": instrument_files,
        "mapped_mat_stats": mapped_mat_stats,
        "dump_listing": listing,
        "mat_prefixes": prefixes,
        "original_mat_prefixes": original_prefixes,
        "mat_dependencies": dependencies,
        "fence": fence,
        "original_config_sha256": config_sha,
        "environment_after_setup": environment_record(),
        "module_paths": module_paths(),
    }
    r.write_json(run / "trace-policy.json", build_trace_policy(config, manifest, run))
    r.write_json(run / "prestage.json", manifest)
    config["prestage"] = {
        "path": str((run / "prestage.json").resolve()),
        "sha256": r.digest(run / "prestage.json"),
    }
    r.write_json(run / "extract-config.json", config)
    return manifest


def _under(path: str, root: str) -> bool:
    return path == root or path.startswith(root.rstrip("/") + "/")


def classify_trace(lines: list[str], policy: Json) -> Json:
    """Classify strace -f -yy opens; any protected attempt refuses, even ENOENT.

    Successful opens must have one explicit disposition. Relative requests require
    an annotated directory fd or AT_FDCWD path. We refuse incomplete/resumed calls
    rather than guess their origin. Failed nonprotected searches remain counted.
    """
    counts: Counter[str] = Counter()
    failed: Counter[str] = Counter()
    violations: list[Json] = []
    events = []
    for line in lines:
        if re.search(r"\b(?:chdir|fchdir)\(", line):
            violations.append(
                {"line": line, "reason": "cwd changed inside extraction trace"}
            )
            continue
        if not re.search(r"\b(?:open|openat|openat2)\(", line):
            continue
        call = re.search(r"\b(open|openat|openat2)\((.*)\)\s+=\s+(.+)$", line)
        if call is None:
            violations.append({"line": line, "reason": "unparsed open syscall"})
            continue
        name, arguments, result = call.groups()
        request = re.search(r'"((?:[^"\\]|\\.)*)"', arguments)
        if request is None:
            violations.append({"line": line, "reason": "missing pathname"})
            continue
        try:
            path = ast.literal_eval('"' + request[1] + '"')
        except (ValueError, SyntaxError):
            violations.append({"line": line, "reason": "invalid quoted path"})
            continue
        success = re.match(r"\d+(?:<.*>)?(?:\s|$)", result) is not None
        if not path.startswith("/"):
            directory = (
                re.search(r"^[^,]*<(/[^>]*)>", arguments) if name != "open" else None
            )
            if directory is not None:
                base = directory[1]
            else:
                base = (
                    policy.get("cwd")
                    if name == "open" or arguments.startswith("AT_FDCWD,")
                    else None
                )
            if base is None:
                violations.append({"line": line, "reason": "unresolved relative path"})
                continue
            path = os.path.normpath(os.path.join(base, path))
        else:
            path = os.path.normpath(path)
        resolved = re.search(r"^\d+<(/[^>]*)>", result)
        paths = {path, resolved[1]} if resolved else {path}
        protected = any(
            _under(p, root) for p in paths for root in policy["protected_roots"]
        )
        event: Json = {
            "request": path,
            "resolved": resolved[1] if resolved else None,
            "success": success,
        }
        if protected:
            violations.append({**event, "reason": "protected root attempt"})
        elif success:
            categories = [
                category
                for category, roots in policy["allowed"].items()
                if any(_under(p, root) for p in paths for root in roots)
            ]
            # Nested explicit stage roots belong to staged_data, not the enclosing run.
            if "staged_data" in categories and "run" in categories:
                categories.remove("run")
            if len(categories) != 1:
                violations.append(
                    {
                        **event,
                        "reason": "unclassified or ambiguous successful open",
                        "categories": categories,
                    }
                )
            else:
                counts[categories[0]] += 1
                event["category"] = categories[0]
        else:
            prefix = next(
                (p for p in policy.get("failed_prefixes", []) if _under(path, p)),
                str(Path(path).parent),
            )
            failed[prefix] += 1
        events.append(event)
    require(bool(events), "trace contains no classified open events")
    if violations:
        raise CustodyRefused(
            "syscall custody violations: " + json.dumps(violations),
            {
                "status": "STOP",
                "violations": violations,
                "successful_open_counts": dict(counts),
                "failed_nonprotected_counts": dict(failed),
                "events": events,
            },
        )
    return {
        "status": "PASS",
        "successful_open_counts": dict(counts),
        "failed_nonprotected_counts": dict(failed),
        "events": events,
        "violations": [],
    }


def build_trace_policy(config: Json, prepared: Json, run: Path) -> Json:
    """Derive protected originals and retain only explicitly reviewed environment roots."""
    extra = config["trace_environment_roots"]
    require(
        isinstance(extra, list)
        and bool(extra)
        and all(Path(p).is_absolute() for p in extra),
        "reviewed environment/ROOT prefixes required",
    )
    cov2d = config["cov2d_protected_paths"]
    require(isinstance(cov2d, list) and bool(cov2d), "COV2D input paths required")
    roots = [
        config["dump_root"],
        str(Path(prepared["original_mat_prefixes"]["PLOTUTILSROOT"]) / "data"),
        prepared["original_mat_prefixes"]["MPARAMFILES"],
        *cov2d,
    ]
    roots += [
        item["original"]
        for item in prepared["files"].values()
        if item["original"] not in prepared["mat_environment"]["mat_sha256"]
    ]
    roots = sorted(
        {
            str(value)
            for path in roots
            for value in (Path(path).absolute(), Path(path).resolve())
        }
    )
    require(
        not any(_under(str(run.resolve()), root) for root in roots),
        "run overlaps protected root",
    )
    modules = list(prepared["module_paths"].values())
    # Import machinery can inspect only the matching cached Python code directory.
    cache = [
        str(Path(path).parent / "__pycache__")
        for path in modules
        if path.endswith(".py")
    ]
    return {
        "schema": "fd-rpd-reco-trace-policy/1",
        "cwd": str(Path.cwd()),
        "protected_roots": roots,
        "allowed": {
            "staged_data": [
                str((run / "original-inputs").resolve()),
                *prepared["mat_prefixes"].values(),
            ],
            "pinned_mat_libs": list(prepared["mat_environment"]["mat_sha256"]),
            "environment": sorted(set(extra + modules + cache)),
            "system": ["/etc", "/lib", "/lib64", "/usr", "/proc", "/sys", "/dev"],
            "run": [str(run.resolve())],
        },
        "failed_prefixes": (
            os.environ.get("LD_LIBRARY_PATH", "").split(":")
            if os.environ.get("LD_LIBRARY_PATH")
            else []
        ),
        "connect_id": prepared["connect_id"],
    }


def check_trace(
    r: Any, run: Path, trace: Path, policy_path: Path, policy_sha: str
) -> Json:
    """Bind a passing syscall audit to this exact extract and producer."""
    r.require_output_root(run)
    policy_copy = r.stage_copy(
        policy_path, run / "trace-policy.checked.json", policy_sha
    )
    policy = json.loads(policy_copy.read_text())
    trace_bytes = trace.read_bytes()
    try:
        checked = classify_trace(trace_bytes.decode().splitlines(), policy)
    except CustodyRefused as error:
        r.write_json(
            run / "flux-custody.STOP.json",
            {
                **(error.details or {}),
                "status": "STOP",
                "message": str(error),
                "policy_sha256": policy_sha,
                "trace_sha256": hashlib.sha256(trace_bytes).hexdigest(),
                "readings": None,
            },
        )
        raise
    extract = run / "flux-extract.json"
    record = json.loads(extract.read_text())
    require(
        record.get("status") == "PASS"
        and record.get("code_sha256") == r.digest(Path(r.__file__)),
        "extract did not pass under this producer",
    )
    receipt = {
        "schema": "fd-rpd-reco-flux-custody/1",
        **checked,
        "extract_sha256": r.digest(extract),
        "trace_sha256": hashlib.sha256(trace_bytes).hexdigest(),
        "policy_sha256": policy_sha,
        "policy": policy,
        "code_sha256": r.digest(Path(r.__file__)),
        "custody_code_sha256": r.digest(Path(__file__)),
    }
    r.write_json(run / "flux-custody.json", receipt)
    return receipt


def missing_dependency_check(
    r: Any, config: Path, config_sha: str, run: Path, policy_sha: str
) -> Json:
    """Temporarily withhold one own staged dependency and require a traced refusal."""
    r.require_output_root(run)
    require(
        not (run / "flux-extract.json").exists(),
        "negative check must precede extraction",
    )
    prepared = json.loads((run / "prestage.json").read_text())
    item = next(
        entry
        for entry in prepared["mat_dependencies"]
        if entry["environment_key"] == "MPARAMFILES"
    )
    path = Path(item["staged"])
    require(
        path.is_relative_to(run.resolve()) and path.is_file(),
        "negative check is limited to an own staged file",
    )
    held = path.with_name(path.name + ".negative-check-held")
    require(not held.exists(), "negative-check holding file already exists")
    trace = run / "missing-dependency.strace"
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
        str(Path(r.__file__)),
        "flux-extract",
        "--config",
        str(config),
        "--config-sha256",
        config_sha,
        "--run",
        str(run),
    ]
    path.rename(held)
    try:
        result = subprocess.run(command, text=True, capture_output=True, check=False)
    finally:
        held.rename(path)
    stop = run / "flux-extract.STOP.json"
    require(
        result.returncode == 4 and stop.is_file(),
        "missing dependency did not refuse cleanly: " + result.stderr,
    )
    refusal = json.loads(stop.read_text())
    require(
        refusal.get("guard") == "MAT_DATA_STAGE",
        "missing dependency refused at a different boundary",
    )
    policy = r.stage_copy(
        run / "trace-policy.json", run / "negative-policy.checked.json", policy_sha
    )
    checked = classify_trace(
        trace.read_text().splitlines(), json.loads(policy.read_text())
    )
    stop.rename(run / "missing-dependency.STOP.json")
    receipt = {
        "schema": "fd-rpd-reco-missing-dependency-check/1",
        "status": "PASS",
        "expected_guard": "MAT_DATA_STAGE",
        "returncode": result.returncode,
        "withheld_staged_path": str(path),
        "stdout": result.stdout,
        "stderr": result.stderr,
        "trace_check": checked,
        "trace_sha256": r.digest(trace),
        "code_sha256": r.digest(Path(r.__file__)),
        "prestage_sha256": r.digest(run / "prestage.json"),
    }
    r.write_json(run / "missing-dependency-check.json", receipt)
    return receipt


def main() -> int:
    """Run a local custody operation; failure never creates a PASS receipt."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "step", choices=("prepare", "trace-check", "missing-dependency-check")
    )
    parser.add_argument("--config", type=Path)
    parser.add_argument("--config-sha256")
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--trace", type=Path)
    parser.add_argument("--policy", type=Path)
    parser.add_argument("--policy-sha256")
    a = parser.parse_args()
    import fd_rpd_reco as r

    try:
        r.require_output_root(a.run)
        if a.step == "prepare":
            require(
                a.config is not None and a.config_sha256 is not None,
                "config pin required",
            )
            prepare(r, a.config, a.config_sha256, a.run)
        elif a.step == "missing-dependency-check":
            require(
                a.config is not None
                and a.config_sha256 is not None
                and a.policy_sha256 is not None,
                "extract config and policy pins required",
            )
            missing_dependency_check(
                r, a.config, a.config_sha256, a.run, a.policy_sha256
            )
        else:
            require(
                a.trace is not None
                and a.policy is not None
                and a.policy_sha256 is not None,
                "trace and policy pin required",
            )
            check_trace(r, a.run, a.trace, a.policy, a.policy_sha256)
    except (CustodyRefused, r.Refused, OSError, ValueError, KeyError) as error:
        print(f"STOP CUSTODY: {error}", file=sys.stderr)
        return 4
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
