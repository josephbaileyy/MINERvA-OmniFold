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
import ctypes
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


def require(condition: bool, message: str, *, guard: str = "CUSTODY") -> None:
    """Refuse an incomplete or inconsistent boundary record."""
    if not condition:
        raise CustodyRefused(message, {"guard": guard})


def module_paths() -> Json:
    """Record every imported module with an on-disk origin."""
    return {
        name: str(Path(filename).resolve())
        for name, module in sorted(sys.modules.items())
        for filename in [getattr(module, "__file__", None)]
        if isinstance(filename, str)
    }


def environment_record(environ: dict[str, str] | None = None) -> Json:
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
        for key, value in sorted((os.environ if environ is None else environ).items())
    }


# POSIX shells update '_' to the last command; it is not interpreter configuration.
# A new exclusion requires a recorded worker diff and review of its setter.
# pymon-fetch-20261107/copies/sitecustomize__init__.py.txt:9-11 and
# nersc_pymon__init__.py.txt:128,150-151 @ d0d4cfd5: each interpreter
# draws and installs a new UUID, retaining the inherited one only as parent_uuid.
ENVIRONMENT_EXCLUSIONS = {
    "_": "shell-maintained last-command value",
    "NERSC_PYMON_UUID": "per-interpreter pymon UUID; inherited value is replaced",
}


def native_environment() -> dict[str, str]:
    """Read libc's live environ, including changes made by native ROOT code."""
    pointer = ctypes.POINTER(ctypes.c_char_p).in_dll(ctypes.CDLL(None), "environ")
    result = {}
    index = 0
    while pointer[index] is not None:
        item = os.fsdecode(pointer[index])
        key, separator, value = item.partition("=")
        require(bool(separator), "native environment entry is malformed")
        result[key] = value
        index += 1
    return result


def environment_snapshot(*, native: bool = False) -> Json:
    """Retain redacted display values and exact value fingerprints for comparison."""
    environ = native_environment() if native else dict(os.environ)
    return {
        "values": environment_record(environ),
        "fingerprints": {
            key: hashlib.sha256(value.encode()).hexdigest()
            for key, value in sorted(environ.items())
        },
    }


def environment_diff(
    prepared: Json, observed: Json, *, exclusions: dict[str, str] | None = None
) -> Json:
    """Compare every environment key except explicitly reviewed volatile fields."""
    ignored = ENVIRONMENT_EXCLUSIONS if exclusions is None else exclusions
    protected = ("LD_", "DYLD_", "PYTHON", "ROOT", "CLING", "CPPYY", "EXTRA_CLING")
    require(
        not any(key.startswith(protected) for key in ignored),
        "interpreter or loader key cannot be excluded",
        guard="ENVIRONMENT_EXCLUSIONS",
    )
    before = prepared["fingerprints"]
    after = observed["fingerprints"]
    old_keys = set(before) - ignored.keys()
    new_keys = set(after) - ignored.keys()
    return {
        "added": {key: observed["values"][key] for key in sorted(new_keys - old_keys)},
        "removed": {
            key: prepared["values"][key] for key in sorted(old_keys - new_keys)
        },
        "changed": {
            key: {
                "prepared": prepared["values"][key],
                "observed": observed["values"][key],
            }
            for key in sorted(old_keys & new_keys)
            if before[key] != after[key]
        },
    }


# ROOT v6-28-12: core/unix/src/TUnixSystem.cxx:453-460 and
# core/metacling/src/TCling.cxx:1468-1480. These are import effects,
# never exclusions from a subsequent native-environment comparison.
# ROOT/__init__.py:14-20 @ v6-28-12 assigns the three pinned values.
ROOT_IMPORT_KEYS = {
    "ROOTSYS",
    "CLING_PREBUILT_MODULE_PATH",
    "CLING_STANDARD_PCH",
    "CPPYY_API_PATH",
    "CPPYY_NO_ROOT_FILTER",
}
ROOT_IMPORT_VALUES = {
    "CLING_STANDARD_PCH": "none",
    "CPPYY_API_PATH": "none",
    "CPPYY_NO_ROOT_FILTER": "1",
}


def root_import_record(before: Json, after: Json) -> Json:
    """Bound ROOT initialization effects and verify the source-defined values."""
    diff = environment_diff(before, after, exclusions={})
    unexpected = {
        section: {
            key: value
            for key, value in values.items()
            if section == "removed" or key not in ROOT_IMPORT_KEYS
        }
        for section, values in diff.items()
    }
    invalid_values = {
        key: {"expected": value, "observed": after["values"].get(key)}
        for key, value in ROOT_IMPORT_VALUES.items()
        if after["values"].get(key) != value
    }
    root_before = before["values"].get("ROOTSYS")
    root_after = after["values"].get("ROOTSYS")
    expected_root = (
        str(Path(root_before).resolve()) if root_before is not None else None
    )
    root_valid = (
        root_after == expected_root
        if root_before is not None
        else isinstance(root_after, str) and Path(root_after).is_dir()
    )
    return {
        "diff": diff,
        "unexpected": unexpected,
        "allowed_import_keys": sorted(ROOT_IMPORT_KEYS),
        "invalid_pinned_values": invalid_values,
        "rootsys": {
            "prepared_present": root_before is not None,
            "prepared": root_before,
            "observed": root_after,
            "expected_realpath": expected_root,
            "valid": root_valid,
        },
        "pass": not any(unexpected.values()) and not invalid_values and root_valid,
    }


def private_prepare_path(run: Path, name: str, connect_id: str) -> Path:
    """Locate one canonical prepare outside the committable run directory."""
    require(
        name in {"prestage", "prologue-prepare"},
        "unknown prepare name",
        guard="PRIVATE_PREPARE",
    )
    token = hashlib.sha256(
        (str(run.resolve()) + "\0" + name + "\0" + connect_id).encode()
    ).hexdigest()
    return (run.resolve().parent / ".rpd-private" / token / (name + ".json")).resolve()


def write_private_prepare(
    r: Any, run: Path, name: str, prepared: Json, *, protected_roots: list[str]
) -> Path:
    """Write owner-only canonical data and a safe, digest-pinned reference."""
    r.require_output_root(run)
    path = private_prepare_path(run, name, prepared["connect_id"])
    r.require_output_root(path)
    require(
        run.resolve() not in path.parents,
        "private prepare overlaps run",
        guard="PRIVATE_PREPARE",
    )
    require(
        not any(_under(str(path), root) for root in protected_roots),
        "private prepare overlaps protected root",
        guard="PRIVATE_PREPARE",
    )
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    info = path.parent.stat()
    require(
        info.st_uid == os.getuid() and info.st_mode & 0o077 == 0,
        "private prepare directory is not owner-only",
        guard="PRIVATE_PREPARE",
    )
    prepared["private_prepare_path"] = str(path)
    prepared["prepare_name"] = name
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as stream:
        json.dump(prepared, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
    reference = run / (name + "-reference.json")
    r.write_json(
        reference,
        {
            "schema": "fd-rpd-reco-private-prepare-reference/1",
            "status": "PASS",
            "run": str(run.resolve()),
            "connect_id": prepared["connect_id"],
            "prepare_name": name,
            "private_prepare": {"path": str(path), "sha256": r.digest(path)},
        },
    )
    return reference


def read_private_prepare(r: Any, reference: Path, expected_sha: str, run: Path) -> Json:
    """Verify a public reference and read its canonical data without staging it."""
    require(
        r.digest(reference) == expected_sha,
        "prepare reference digest differs",
        guard="PRIVATE_PREPARE",
    )
    record = json.loads(reference.read_text())
    item = record["private_prepare"]
    path = Path(item["path"]).resolve()
    r.require_output_root(path)
    require(
        record["run"] == str(run.resolve())
        and path
        == private_prepare_path(run, record["prepare_name"], record["connect_id"])
        and run.resolve() not in path.parents,
        "private prepare identity or location differs",
        guard="PRIVATE_PREPARE",
    )
    info = path.stat()
    parent_info = path.parent.stat()
    require(
        info.st_uid == os.getuid()
        and info.st_mode & 0o077 == 0
        and parent_info.st_uid == os.getuid()
        and parent_info.st_mode & 0o077 == 0,
        "canonical prepare is not owner-only",
        guard="PRIVATE_PREPARE",
    )
    data = path.read_bytes()
    require(
        hashlib.sha256(data).hexdigest() == item["sha256"],
        "private prepare digest differs",
        guard="PRIVATE_PREPARE",
    )
    prepared: Json = json.loads(data)
    require(
        prepared.get("run") == record["run"]
        and prepared.get("connect_id") == record["connect_id"],
        "private prepare does not match its reference",
        guard="PRIVATE_PREPARE",
    )
    return prepared


def public_record(value: Any, before: Json, after: Json) -> Any:
    """Export comparison metadata without credential values or fingerprints."""
    keys = {
        key
        for snapshot in (before, after)
        for key, display in snapshot.get("values", {}).items()
        if isinstance(display, str)
        and (display == "<redacted credential field>" or "<redacted>@" in display)
    }
    summaries = {
        key: {
            "prepared_present": key in before.get("fingerprints", {}),
            "observed_present": key in after.get("fingerprints", {}),
            "state": (
                "equal"
                if (
                    key in before.get("fingerprints", {})
                    and key in after.get("fingerprints", {})
                    and before["fingerprints"][key] == after["fingerprints"][key]
                )
                else "changed"
            ),
        }
        for key in sorted(keys)
    }

    def export(item: Any) -> Any:
        if isinstance(item, dict):
            return {
                key: (
                    summaries[key]
                    if key in summaries
                    else (
                        [
                            {
                                "module_name_components": module.split("."),
                                "source_path": path,
                            }
                            for module, path in child.items()
                        ]
                        if key == "module_paths" and isinstance(child, dict)
                        else export(child)
                    )
                )
                for key, child in item.items()
                if key != "fingerprints"
            }
        if isinstance(item, list):
            return [export(child) for child in item]
        return item

    result = export(value)
    if isinstance(result, dict):
        result["redacted_environment"] = summaries
    return result


def publish_prepare_view(
    r: Any, run: Path, prepared: Json, observed: Json, *, stopped: bool
) -> None:
    """Produce the committable view after a worker has compared the environments."""
    if "private_prepare_path" not in prepared:
        return
    r.require_output_root(run)
    name = prepared["prepare_name"] + (".STOP.json" if stopped else ".json")
    path = run / name
    public = public_record(prepared, prepared.get("environment_snapshot", {}), observed)
    public["private_prepare_sha256"] = r.digest(Path(prepared["private_prepare_path"]))
    public["comparison_status"] = "STOP" if stopped else "PASS"
    if path.exists():
        require(
            json.loads(path.read_text()) == public,
            "public prepare view changed",
            guard="PRIVATE_PREPARE",
        )
    else:
        r.write_json(path, public)


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
    require(not (run / "prestage-reference.json").exists(), "fresh prestage required")
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
    before_root = environment_snapshot(native=True)
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
    require(
        fence.get("status") == "PASS" and fence.get("exit_code") == 0,
        "prepare requires a passing COV2D fence",
        guard="PREPARE_FENCE",
    )
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
            before == after,
            "source stat or atime changed during fresh stage: " + key,
            guard="STAGE_SOURCE_STAT",
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
        guard="MAT_INVENTORY",
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
                guard="NATIVE_SELECTION",
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
        "environment_after_setup": before_root["values"],
        "environment_snapshot": before_root,
        "module_paths": module_paths(),
    }
    manifest["private_prepare_path"] = str(
        private_prepare_path(run, "prestage", manifest["connect_id"])
    )
    manifest["platform_libraries"] = pin_platform_libraries(
        r, instrument.mapped_files(), build_trace_policy(config, manifest, run)
    )
    manifest["platform_mapped"] = platform_prepared_mappings(
        instrument.mapped_files(), build_trace_policy(config, manifest, run)
    )
    policy = build_trace_policy(config, manifest, run)
    r.write_json(run / "trace-policy.json", policy)
    manifest["trace_policy_sha256"] = r.digest(run / "trace-policy.json")
    reference = write_private_prepare(
        r, run, "prestage", manifest, protected_roots=policy["protected_roots"]
    )
    config["prestage"] = {
        "path": str(reference.resolve()),
        "sha256": r.digest(reference),
    }
    r.write_json(run / "extract-config.json", config)
    return manifest


def _under(path: str, root: str) -> bool:
    return path == root or path.startswith(root.rstrip("/") + "/")


def classify_successful_open(
    paths: set[str], arguments: str, policy: Json
) -> list[str]:
    """Keep exact pinned files distinct from reviewed instrument-directory scans."""
    pinned = set(policy["allowed"].get("pinned_mat_libs", []))
    if paths & set(policy.get("private_prepare_files", [])):
        return ["private_prepare"]
    if paths & pinned:
        return ["pinned_mat_libs"]
    if paths & set(policy.get("platform_library_pins", {})):
        return ["pinned_platform_libs"]
    if any(
        _under(p, directory)
        for p in paths
        for directory in policy.get("instrument_directories", [])
    ):
        return ["instrument_directory"]
    if "O_DIRECTORY" in arguments and any(
        p == directory
        for p in paths
        for directory in policy.get("python_directories", [])
    ):
        return ["python_directory"]
    categories = [
        category
        for category, roots in policy["allowed"].items()
        if category not in {"pinned_mat_libs", "pinned_platform_libs"}
        and any(_under(p, root) for p in paths for root in roots)
        and not any(
            _under(p, root)
            for p in paths
            for root in policy.get("class_exclusions", {}).get(category, [])
        )
    ]
    return categories


def mapped_instrument_violations(mapped: set[str], policy: Json) -> list[str]:
    """A rootmap may be read without admitting a new mapped instrument library."""
    pinned = {
        str(Path(path).resolve())
        for path in policy["allowed"].get("pinned_mat_libs", [])
    }
    return sorted(
        path
        for path in mapped
        if re.search(r"\.so(?:\.\d+)*$|\.dylib$", path)
        and any(
            _under(path, directory)
            for directory in policy.get("instrument_directories", [])
        )
        and path not in pinned
    )


def _trace_pid_body(line: str) -> tuple[int | None, str]:
    """Separate both strace PID-prefix forms from the syscall text."""
    match = re.match(r"^\s*(?:\[pid\s+(\d+)\]|(\d+))\s+(.*)$", line)
    return (int(match[1] or match[2]), match[3]) if match else (None, line.strip())


def _trace_violation(record: Json, reason: str, *, category: str = "parse") -> Json:
    """Keep original trace evidence even when a pathname cannot be resolved."""
    request = re.search(r'"((?:[^"\\]|\\.)*)"', record["call"])
    path = None
    if request:
        try:
            path = ast.literal_eval('"' + request[1] + '"')
        except (ValueError, SyntaxError):
            pass
    return {
        "class": category,
        "reason": reason,
        "path": path,
        "pid": record["pid"],
        "raw_line": "\n".join(record["raw_lines"]),
        "raw_lines": record["raw_lines"],
        "line_numbers": record["line_numbers"],
    }


def complete_trace_calls(lines: list[str]) -> tuple[list[Json], list[Json], list[Json]]:
    """Join split syscalls only within one PID and preserve every input line."""
    pending: dict[int, Json] = {}
    calls: list[Json] = []
    violations: list[Json] = []
    retained: list[Json] = []
    names = r"open|openat|openat2|chdir|fchdir"
    for number, line in enumerate(lines, 1):
        pid, body = _trace_pid_body(line)
        record = {
            "pid": pid,
            "call": body,
            "raw_lines": [line],
            "line_numbers": [number],
        }
        if body.endswith("<unfinished ...>"):
            start = re.match(r"^(" + names + r")\(", body)
            if pid is None or start is None:
                violations.append(
                    _trace_violation(
                        record, "unfinished syscall has no PID or recognized name"
                    )
                )
                continue
            if pid in pending:
                violations.append(
                    _trace_violation(
                        pending.pop(pid), "second unfinished syscall for pending PID"
                    )
                )
            record["name"] = start[1]
            record["call"] = body.removesuffix("<unfinished ...>")
            pending[pid] = record
            continue
        resumed = re.match(r"^<\.\.\. (\w+) resumed>(.*)$", body)
        if resumed:
            pending_pid = pid
            if pending_pid is None or pending_pid not in pending:
                violations.append(
                    _trace_violation(
                        record, "resumed syscall has no unfinished call for its PID"
                    )
                )
                continue
            first = pending.pop(pending_pid)
            joined = {
                "pid": pid,
                "call": first["call"] + resumed[2],
                "raw_lines": first["raw_lines"] + record["raw_lines"],
                "line_numbers": first["line_numbers"] + record["line_numbers"],
            }
            if first["name"] != resumed[1]:
                violations.append(
                    _trace_violation(
                        joined, "resumed syscall name differs from unfinished call"
                    )
                )
            else:
                calls.append(joined)
            continue
        if re.match(r"^(?:" + names + r")\(", body):
            calls.append(record)
        else:
            retained.append({"pid": pid, "raw_line": line, "line_numbers": [number]})
    for record in pending.values():
        violations.append(
            _trace_violation(
                record, "unfinished syscall remains unpaired at end of trace"
            )
        )
    accounted = {
        n for record in [*calls, *violations, *retained] for n in record["line_numbers"]
    }
    for number in sorted(set(range(1, len(lines) + 1)) - accounted):
        pid, body = _trace_pid_body(lines[number - 1])
        violations.append(
            _trace_violation(
                {
                    "pid": pid,
                    "call": body,
                    "raw_lines": [lines[number - 1]],
                    "line_numbers": [number],
                },
                "trace line was not accounted for",
            )
        )
    return sorted(calls, key=lambda item: item["line_numbers"][0]), violations, retained


def classify_trace(lines: list[str], policy: Json) -> Json:
    """Classify complete calls, refusing protected attempts and every ambiguity."""
    counts: Counter[str] = Counter()
    failed: Counter[str] = Counter()
    calls, violations, retained = complete_trace_calls(lines)
    events: list[Json] = []
    cwd_by_pid: dict[int | None, str] = {}
    for record in calls:
        line = record["call"]
        call = re.match(r"(open|openat|openat2|chdir|fchdir)\((.*)\)\s+=\s+(.+)$", line)
        if call is None:
            violations.append(_trace_violation(record, "unparsed syscall"))
            continue
        name, arguments, result = call.groups()
        cwd = cwd_by_pid.get(record["pid"], policy.get("cwd"))
        if name in {"chdir", "fchdir"}:
            try:
                directory = ast.literal_eval(arguments) if name == "chdir" else None
            except (ValueError, SyntaxError):
                directory = None
            if name == "fchdir":
                annotated = re.search(r"^\d+<(/[^>]*)>$", arguments)
                directory = annotated[1] if annotated else None
            target = (
                os.path.normpath(os.path.join(cwd, directory))
                if isinstance(directory, str) and isinstance(cwd, str)
                else None
            )
            event = {
                **_trace_violation(record, "cwd operation", category="cwd"),
                "path": target,
                "result": result,
                "success": result.startswith("0"),
            }
            if target is None or target != policy.get("clone_root"):
                violations.append(
                    {**event, "reason": "cwd changed outside declared clone"}
                )
            else:
                event["category"] = "declared_clone_cwd"
            if event["success"] and target is not None:
                cwd_by_pid[record["pid"]] = target
            events.append(event)
            continue
        request = re.search(r'"((?:[^"\\]|\\.)*)"', arguments)
        if request is None:
            violations.append(_trace_violation(record, "missing pathname"))
            continue
        try:
            path = ast.literal_eval('"' + request[1] + '"')
        except (ValueError, SyntaxError):
            violations.append(_trace_violation(record, "invalid quoted path"))
            continue
        success = re.match(r"\d+(?:<.*>)?(?:\s|$)", result) is not None
        if not success and re.match(r"-1\s+\w+", result) is None:
            violations.append(_trace_violation(record, "unresolved open result"))
            continue
        if not path.startswith("/"):
            directory_fd = (
                re.search(r"^[^,]*<(/[^>]*)>", arguments) if name != "open" else None
            )
            base = (
                directory_fd[1]
                if directory_fd is not None
                else (
                    cwd if name == "open" or arguments.startswith("AT_FDCWD,") else None
                )
            )
            if base is None:
                violations.append(_trace_violation(record, "unresolved relative path"))
                continue
            path = os.path.normpath(os.path.join(base, path))
        else:
            path = os.path.normpath(path)
        resolved = re.search(r"^\d+<(/[^>]*)>", result)
        paths = {path, resolved[1]} if resolved else {path}
        protected = any(
            _under(p, root) for p in paths for root in policy["protected_roots"]
        )
        event = {
            "pid": record["pid"],
            "path": path,
            "request": path,
            "resolved": resolved[1] if resolved else None,
            "success": success,
            "raw_line": "\n".join(record["raw_lines"]),
            "raw_lines": record["raw_lines"],
            "line_numbers": record["line_numbers"],
        }
        if protected:
            violations.append(
                {**event, "class": "protected_root", "reason": "protected root attempt"}
            )
        elif success:
            categories = classify_successful_open(paths, arguments, policy)
            endpoint = resolved[1] if resolved else path
            platform_library = any(
                _under(value, root)
                for value in paths
                for root in policy["allowed"].get("platform_system", [])
            ) and any(re.search(r"\.so(?:\.\d+)*$|\.dylib$", value) for value in paths)
            if platform_library and endpoint not in policy.get(
                "platform_library_pins", {}
            ):
                violations.append(
                    {
                        **event,
                        "class": "platform_library",
                        "reason": "platform library open has no prepare pin",
                    }
                )
            elif (
                any(
                    _under(value, root)
                    for value in paths
                    for root in policy.get("instrument_directories", [])
                )
                and any(
                    re.search(r"\.so(?:\.\d+)*$|\.dylib$", value) for value in paths
                )
                and endpoint not in policy["allowed"].get("pinned_mat_libs", [])
            ):
                violations.append(
                    {
                        **event,
                        "class": "instrument_library",
                        "reason": "instrument library open has no prepare pin",
                    }
                )
            elif len(categories) != 1:
                violations.append(
                    {
                        **event,
                        "class": "classification",
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
    if not any("request" in event for event in events):
        violations.append(
            {
                "class": "trace",
                "reason": "trace contains no open events",
                "path": None,
                "pid": None,
                "raw_line": None,
                "raw_lines": [],
                "line_numbers": [],
            }
        )
    checked = {
        "status": "STOP" if violations else "PASS",
        "violations": violations,
        "successful_open_counts": dict(counts),
        "failed_nonprotected_counts": dict(failed),
        "events": events,
        "retained_noncall_lines": retained,
        "trace_line_count": len(lines),
    }
    if violations:
        raise CustodyRefused("syscall custody violations", checked)
    return checked


PLATFORM_ROLES = {
    "cray_pe",
    "ovis_ldms",
    "nvidia_hpc",
    "nersc_pymon",
    "nerscjson_client",
    "sss_cache",
    "darshan",
    "libfabric",
}


def platform_settings(config: Json) -> list[Json]:
    """Require the reviewed platform namespaces and their stated reasons."""
    entries = config.get("trace_platform_roots")
    valid = (
        isinstance(entries, list)
        and len(entries) == len(PLATFORM_ROLES)
        and all(
            isinstance(item, dict) and isinstance(item.get("role"), str)
            for item in entries
        )
        and {item.get("role") for item in entries} == PLATFORM_ROLES
        and config.get("trace_platform_library_digest")
        == "ordinary_instrument_code_only"
        and all(
            isinstance(item.get("path"), str)
            and Path(item["path"]).is_absolute()
            and not any(token in item["path"] for token in ("${", "*", "?", "[", "]"))
            and isinstance(item.get("reason"), str)
            and bool(item["reason"].strip())
            for item in entries
        )
    )
    require(
        valid,
        "reviewed platform roots/reasons and instrument digest mode required",
        guard="PLATFORM_CONFIG",
    )
    assert isinstance(entries, list)
    return entries


def parse_executable_maps(lines: list[str]) -> Json:
    """Retain native executable file mappings, without assuming a .so suffix."""
    records: Json = {}
    for line in lines:
        fields = line.split(None, 5)
        if len(fields) != 6 or "x" not in fields[1] or not fields[5].startswith("/"):
            continue
        major, minor = fields[3].split(":")
        identity = {
            "device": os.makedev(int(major, 16), int(minor, 16)),
            "inode": int(fields[4]),
        }
        path = str(Path(fields[5].strip()).resolve())
        require(
            path not in records or records[path] == identity,
            "inconsistent executable mapping identity",
            guard="PLATFORM_MAP_IDENTITY",
        )
        records[path] = identity
    return records


def executable_mapped_files() -> Json:
    """Read Linux's current executable mappings; non-library caches are not pinned."""
    return parse_executable_maps(Path("/proc/self/maps").read_text().splitlines())


def platform_identity(path: Path) -> Json:
    """Record code identity; loader/library atime is not custody evidence."""
    info = path.stat()
    return {
        "device": info.st_dev,
        "inode": info.st_ino,
        "bytes": info.st_size,
        "mtime_ns": info.st_mtime_ns,
    }


def platform_mapping_snapshot(
    mapped: set[str], policy: Json
) -> tuple[Json, list[str], list[str]]:
    """Separate mapped platform code from non-executable platform data."""
    roots = policy["allowed"].get("platform_system", [])
    if not roots:
        return {}, [], []
    executable = {
        path: identity
        for path, identity in executable_mapped_files().items()
        if any(_under(path, root) for root in roots)
    }
    nonexecutable = sorted(
        path
        for path in mapped
        if any(_under(path, root) for root in roots) and path not in executable
    )
    return executable, sorted(set(executable) - mapped), nonexecutable


# prologue4/run/prologue.strace:2562-2692 @ 68a36cf8 records these loads.
# pymon-fetch/copies/nersc_pymon__init__.py.txt:260-267 @ d0d4cfd5 registers
# the exit hooks; nersc_pymon_vendor_nerscjson.py.txt:22-23 loads libldms.
OVIS_EXIT_LIBRARIES = (
    "lib/libldms.so",
    "lib/libovis_json.so.0",
    "lib/libovis_event.so.0",
    "lib/libmmalloc.so.0",
    "lib/libzap.so.0",
    "lib/libovis_thrstats.so.0",
    "lib/libovis_log.so.0",
    "lib/libovis_ev.so.0",
    "lib/libcoll.so.0",
    "lib/libovis_third.so.0",
    "lib/libovis_util.so.0",
    "lib/ovis-ldms/libzap_sock.so",
    "lib/libldms_auth_munge.so",
)


def platform_late_library_paths(policy: Json) -> list[str]:
    """Resolve the declared exit-hook libraries without loading or disabling pymon."""
    roots = [
        item["path"]
        for item in policy.get("platform_root_reasons", [])
        if item["role"] == "ovis_ldms"
    ]
    paths = []
    for root in roots:
        for relative in OVIS_EXIT_LIBRARIES:
            path = Path(root) / relative
            resolved = str(path.resolve())
            require(
                not any(
                    _under(value, protected)
                    for value in (str(path), resolved)
                    for protected in policy["protected_roots"]
                )
                and _under(resolved, str(Path(root).resolve())),
                "exit-hook library escapes reviewed code root or overlaps protected input",
                guard="PLATFORM_LATE_ROOT",
            )
            require(
                path.is_file(),
                "required exit-hook library missing",
                guard="PLATFORM_LATE_PRESENT",
            )
            paths.append(resolved)
    return sorted(set(paths))


def platform_prepared_mappings(mapped: set[str], policy: Json) -> Json:
    """Keep the instantaneous mapped subset separate from the fixed library inventory."""
    executable, missing, _ = platform_mapping_snapshot(mapped, policy)
    require(
        not missing, "incomplete prepare mapped subset", guard="PLATFORM_PREPARE_SUBSET"
    )
    return executable


def pin_platform_libraries(r: Any, mapped: set[str], policy: Json) -> Json:
    """Pin mapped and declared exit-hook code, refusing protected inputs first."""
    executable, missing, _nonexecutable = platform_mapping_snapshot(mapped, policy)
    require(
        not missing,
        "executable platform mappings differ from process snapshot",
        guard="PLATFORM_MAP_SET",
    )
    pins = {}
    for filename in sorted(set(executable) | set(platform_late_library_paths(policy))):
        mapping = executable.get(filename)
        require(
            not any(_under(filename, root) for root in policy["protected_roots"]),
            "protected input cannot use ordinary platform digest",
            guard="PLATFORM_PROTECTED",
        )
        path = Path(filename)
        before = platform_identity(path)
        require(
            mapping is None
            or all(before[key] == mapping[key] for key in ("device", "inode")),
            "mapped code differs from on-disk identity",
            guard="PLATFORM_MAP_FILE",
        )
        checksum = r.digest(path)
        require(
            before == platform_identity(path),
            "platform library changed while pinning",
            guard="PLATFORM_PIN_CHANGED",
        )
        pins[filename] = {**before, "sha256": checksum}
    return pins


def platform_library_record(
    r: Any, prepared: Json, mapped: set[str], policy: Json
) -> Json:
    """Compare the mapped subset and every pin in the fixed library inventory."""
    expected = prepared.get("platform_libraries")
    expected_mapped = prepared.get("platform_mapped")
    executable, inconsistent, nonexecutable = platform_mapping_snapshot(mapped, policy)
    record: Json = {
        "status": "STOP",
        "digest_mode": "ordinary_instrument_code_only",
        "expected_mapped": (
            sorted(expected_mapped) if isinstance(expected_mapped, dict) else None
        ),
        "inventory_paths": sorted(expected) if isinstance(expected, dict) else None,
        "observed_mapped": sorted(executable),
        "missing_from_process_snapshot": inconsistent,
        "nonexecutable_platform_mappings": nonexecutable,
        "libraries": {},
        "violations": [],
    }
    if not isinstance(expected, dict) or not isinstance(expected_mapped, dict):
        record["violations"].append({"reason": "platform prepare pins missing"})
        return record
    added, removed = sorted(set(executable) - set(expected_mapped)), sorted(
        set(expected_mapped) - set(executable)
    )
    inconsistent += sorted(set(executable) - set(expected))
    record.update(unexpected_mapped=added, missing_mapped=removed)
    if added or removed or inconsistent:
        record["violations"].append({"reason": "platform mapped set differs"})
        return record
    for filename in expected:
        mapping = executable.get(filename)
        if any(_under(filename, root) for root in policy["protected_roots"]):
            record["violations"].append(
                {
                    "reason": "protected input cannot use ordinary platform digest",
                    "path": filename,
                }
            )
            continue
        try:
            path = Path(filename)
            before = platform_identity(path)
            observed = {**before, "sha256": r.digest(path)}
            stable = before == platform_identity(path)
            valid = (
                stable
                and observed == expected[filename]
                and (
                    mapping is None
                    or (
                        all(
                            observed[key] == mapping[key] for key in ("device", "inode")
                        )
                        and mapping == expected_mapped[filename]
                    )
                )
            )
            record["libraries"][filename] = {
                "prepared": expected[filename],
                "observed": observed,
                "mapped_identity": mapping,
                "prepared_mapped_identity": expected_mapped.get(filename),
                "stable": stable,
            }
            if not valid:
                record["violations"].append(
                    {
                        "reason": "platform library identity or digest differs",
                        "path": filename,
                    }
                )
        except OSError as error:
            record["violations"].append(
                {
                    "reason": "platform library unavailable",
                    "path": filename,
                    "errno": error.errno,
                }
            )
    record["status"] = "STOP" if record["violations"] else "PASS"
    return record


def build_trace_policy(config: Json, prepared: Json, run: Path) -> Json:
    """Derive protected originals and retain only explicitly reviewed environment roots."""
    extra = config["trace_environment_roots"]
    require(
        isinstance(extra, list)
        and bool(extra)
        and all(Path(p).is_absolute() for p in extra),
        "reviewed environment/ROOT prefixes required",
    )
    directories = config["trace_instrument_directories"]
    require(
        isinstance(directories, list)
        and bool(directories)
        and all(Path(p).is_absolute() for p in directories),
        "reviewed instrument directories required",
        guard="INSTRUMENT_DIRECTORIES",
    )
    platform = platform_settings(config)
    cov2d = config["cov2d_protected_paths"]
    require(isinstance(cov2d, list) and bool(cov2d), "COV2D input paths required")
    roots = [
        config["dump_root"],
        config["flux_root"],
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
        guard="RUN_PROTECTED_OVERLAP",
    )
    private_files = (
        [prepared["private_prepare_path"]] if "private_prepare_path" in prepared else []
    )
    require(
        not any(_under(path, root) for path in private_files for root in roots),
        "planned private prepare overlaps protected root",
        guard="PRIVATE_PREPARE",
    )
    owned_sources = [
        str(Path(__file__).with_name(name).resolve())
        for name in (
            "fd_rpd_reco.py",
            "fd_rpd_reco_custody.py",
            "fd_rpd_reco_prologue.py",
            "fd_rpd_inputs.py",
            "fd_ct_period_inputs.py",
        )
    ]
    modules = list(prepared["module_paths"].values()) + owned_sources
    # Import machinery can inspect only the matching cached Python code directory.
    cache = [
        str(Path(path).parent / "__pycache__")
        for path in modules
        if path.endswith(".py")
    ]
    clone = str(Path(__file__).resolve().parents[1])
    platform_roots = sorted(
        {
            str(value)
            for item in platform
            for value in (Path(item["path"]).absolute(), Path(item["path"]).resolve())
        }
    )
    staged_roots = [
        str((run / "original-inputs").resolve()),
        *prepared["mat_prefixes"].values(),
    ]
    environment_roots = sorted(set(extra + modules + cache))
    instrument_roots = sorted(
        {
            str(value)
            for path in directories
            for value in (Path(path).absolute(), Path(path).resolve())
        }
    )
    pinned_platform = list(prepared.get("platform_libraries", {}))
    return {
        "schema": "fd-rpd-reco-trace-policy/3",
        "platform_library_pins": prepared.get("platform_libraries", {}),
        "mat_library_sha256": prepared["mat_environment"]["mat_sha256"],
        "cwd": clone,
        "clone_root": clone,
        "protected_roots": roots,
        "private_prepare_files": private_files,
        "instrument_directories": instrument_roots,
        "python_directories": sorted(
            {clone, *[str(Path(path or os.getcwd()).resolve()) for path in sys.path]}
        ),
        "platform_root_reasons": platform,
        "platform_library_digest": "ordinary_instrument_code_only",
        "allowed": {
            "staged_data": staged_roots,
            "pinned_mat_libs": list(prepared["mat_environment"]["mat_sha256"]),
            "pinned_platform_libs": pinned_platform,
            "platform_system": platform_roots,
            "environment": environment_roots,
            "system": ["/etc", "/lib", "/lib64", "/usr", "/proc", "/sys", "/dev"],
            "run": [str(run.resolve())],
        },
        "class_exclusions": {
            "system": sorted(
                set(
                    [
                        str(run.resolve()),
                        clone,
                        *staged_roots,
                        *environment_roots,
                        *platform_roots,
                        *instrument_roots,
                        *private_files,
                    ]
                )
            ),
            "environment": sorted(
                set(
                    [
                        str(run.resolve()),
                        *staged_roots,
                        *platform_roots,
                        *instrument_roots,
                        *private_files,
                    ]
                )
            ),
            "platform_system": sorted(
                set(
                    [
                        str(run.resolve()),
                        *staged_roots,
                        *pinned_platform,
                        *instrument_roots,
                        *private_files,
                    ]
                )
            ),
            "run": staged_roots,
        },
        "failed_prefixes": (
            os.environ.get("LD_LIBRARY_PATH", "").split(":")
            if os.environ.get("LD_LIBRARY_PATH")
            else []
        ),
        "connect_id": prepared["connect_id"],
    }


def trace_cwd(policy: Json) -> str:
    """Keep the traced child in the frozen checkout, before strace starts."""
    expected = str(Path(__file__).resolve().parents[1])
    require(
        policy.get("cwd") == expected and policy.get("clone_root") == expected,
        "trace cwd is not the declared source clone",
        guard="TRACE_CWD",
    )
    return expected


def write_trace_record(r: Any, run: Path, stage: str, record: Json) -> Json:
    """Write the trace disposition through the existing public export boundary."""
    r.require_output_root(run)
    require(
        stage in {"data-free-trace", "flux-custody", "missing-dependency-trace"},
        "unknown trace record stage",
        guard="TRACE_RECORD_NAME",
    )
    suffix = ".STOP.json" if record["status"] == "STOP" else ".json"
    public: Json = public_record(record, {}, {})
    r.write_json(run / (stage + suffix), public)
    return public


def check_trace_libraries(r: Any, checked: Json, policy: Json) -> Json:
    """Verify opened instrument libraries after every traced process exits.

    Protected roots refuse before any read. Metadata receives only a four-byte
    file-kind probe; hashes are computed only for prepared instrument-library pins.
    No content from the probe is exported.
    """
    records: Json = {}
    violations = []
    for event in checked["events"]:
        if not event.get("success") or "request" not in event:
            continue
        names = {event["request"], event.get("resolved") or event["request"]}
        platform = any(
            _under(name, root)
            for name in names
            for root in policy["allowed"].get("platform_system", [])
        )
        instrument = any(
            _under(name, root)
            for name in names
            for root in policy.get("instrument_directories", [])
        )
        if not platform and not instrument:
            continue
        pins = (
            policy.get("platform_library_pins", {})
            if platform
            else policy.get("mat_library_sha256", {})
        )
        category = "platform_library" if platform else "instrument_library"
        endpoint = event.get("resolved") or event["request"]
        path = Path(endpoint)
        resolved = str(path.resolve())
        item: Json = {"prepared": pins.get(endpoint)}
        try:
            if any(
                _under(name, root)
                for name in names | {resolved}
                for root in policy["protected_roots"]
            ):
                raise ValueError("instrument-code open resolves into protected input")
            if resolved != endpoint:
                raise ValueError("library descriptor path changed after trace")
            if path.is_dir():
                records[endpoint] = {"kind": "directory"}
                continue
            before = platform_identity(path)
            with path.open("rb") as stream:
                elf = stream.read(4) == b"\x7fELF"
            library = (
                elf or re.search(r"\.so(?:\.\d+)*$|\.dylib$", endpoint) is not None
            )
            item.update(kind="library" if library else "metadata", stat=before)
            if library or endpoint in pins:
                if endpoint not in pins:
                    raise ValueError("library open has no prepare pin")
                observed = {**before, "sha256": r.digest(path)}
                item.update(prepared=pins[endpoint], observed=observed)
                if (
                    (observed != pins[endpoint])
                    if platform
                    else (observed["sha256"] != pins[endpoint])
                ):
                    raise ValueError("opened library differs from prepare pin")
            if before != platform_identity(path):
                raise ValueError("file changed during post-exit verification")
            records[endpoint] = item
        except (OSError, ValueError) as error:
            violations.append(
                {
                    **event,
                    "class": category,
                    "reason": str(error),
                    "comparison": item,
                }
            )
    result = {
        **checked,
        "library_open_checks": records,
        "violations": checked["violations"] + violations,
    }
    if violations:
        result["status"] = "STOP"
        raise CustodyRefused("library custody violations", result)
    return result


def classify_trace_with_stop(
    r: Any, run: Path, stage: str, lines: list[str], policy: Json, provenance: Json
) -> Json:
    """Persist every classified violation before propagating a trace refusal."""
    r.require_output_root(run)
    try:
        checked = classify_trace(lines, policy)
        return check_trace_libraries(r, checked, policy)
    except CustodyRefused as error:
        write_trace_record(
            r, run, stage, {**provenance, **(error.details or {}), "status": "STOP"}
        )
        raise


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
    checked = classify_trace_with_stop(
        r,
        run,
        "flux-custody",
        trace_bytes.decode().splitlines(),
        policy,
        {
            "policy_sha256": policy_sha,
            "trace_sha256": hashlib.sha256(trace_bytes).hexdigest(),
            "readings": None,
        },
    )
    extract = run / "flux-extract.json"
    record = json.loads(extract.read_text())
    require(
        record.get("status") == "PASS"
        and record.get("code_sha256") == r.digest(Path(r.__file__)),
        "extract did not pass under this producer",
        guard="TRACE_EXTRACT_IDENTITY",
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
    reference = run / "prestage-reference.json"
    prepared = read_private_prepare(r, reference, r.digest(reference), run)
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
    policy = r.stage_copy(
        run / "trace-policy.json", run / "negative-policy.checked.json", policy_sha
    )
    trace_policy = json.loads(policy.read_text())
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
        result = subprocess.run(
            command,
            text=True,
            capture_output=True,
            check=False,
            cwd=trace_cwd(trace_policy),
        )
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
        guard="NEGATIVE_EXPECTED_GUARD",
    )
    checked = classify_trace_with_stop(
        r,
        run,
        "missing-dependency-trace",
        trace.read_text().splitlines(),
        trace_policy,
        {"policy_sha256": policy_sha, "trace_sha256": r.digest(trace)},
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
        "prestage_sha256": r.digest(reference),
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
