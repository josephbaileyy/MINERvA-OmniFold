#!/usr/bin/env python3
"""Prepare or execute the separately authorized, bounded PET v2 source audit.

No ROOT import or source open occurs in --check-preparation mode. Execution
requires a digest-bound authorization file for this exact committed preparation.
The launcher has no source, branch, entry, retry, training or scheduler options.
"""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import importlib
import json
import os
from pathlib import Path
import platform
import resource
import signal
import subprocess
import sys
import time
from typing import Any

THREAD_ENV = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "TF_NUM_INTRAOP_THREADS",
    "TF_NUM_INTEROP_THREADS",
)
for variable in THREAD_ENV:
    os.environ[variable] = "1"
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

# Resolve imports against this checkout, never a deployment's hardcoded root.
PET_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PET_ROOT.parents[1]
BINDING_FILE = PET_ROOT / "SOURCE_AUDIT_BINDINGS.json"


def digest_file(path: Path) -> str:
    """Hash a local preparation artifact; never used for ROOT payload files."""
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def check_preparation() -> dict[str, Any]:
    """Verify committed code, schema, branch and manifest pins without ROOT."""
    import typed_descriptor_source_audit as audit
    import typed_descriptor_source_smoke as source
    import typed_descriptors as typed

    binding = json.loads(BINDING_FILE.read_bytes())
    for relative, expected in binding["files"].items():
        if digest_file(REPO_ROOT / relative) != expected:
            raise ValueError(f"preparation hash mismatch: {relative}")
    if binding["schema_sha256"] != typed.descriptor_schema_digest():
        raise ValueError("schema binding mismatch")
    if (
        binding["ordered_branches"] != list(source.REQUIRED_BRANCHES)
        or binding["branch_sha256"] != source.required_branch_digest()
    ):
        raise ValueError("branch binding mismatch")
    specs = [dataclasses.asdict(spec) for spec in source.FIXED_SOURCES]
    for spec in specs:
        spec["role_code"] = int(spec["role_code"])
    if (
        binding["sources"] != specs
        or binding["branch_contract"] != audit.branch_contract()
    ):
        raise ValueError("source/metadata contract binding mismatch")
    source.resolve_fixed_sources(REPO_ROOT)
    if binding["limits"] != audit.LIMITS or binding["entry_interval"] != [0, 4096]:
        raise ValueError("resource/range binding mismatch")
    gate = json.loads(
        (
            REPO_ROOT
            / "docs/orchestration/state/gate6-member-trajectories-result-56847059.json"
        ).read_bytes()
    )
    if gate["prohibitions_applied"] != list(audit.PROHIBITIONS):
        raise ValueError("Gate-6 prohibition binding mismatch")
    return binding


class RuntimeBudget:
    """Enforce Linux process ceilings and observe wall time, RSS, and threads."""

    def __init__(self) -> None:
        import typed_descriptor_source_audit as audit

        self.limits = audit.LIMITS
        self.started = time.monotonic()
        self.peak_threads = 0
        self.peak_rss = 0
        self._audit = audit

    def check(self) -> None:
        """Stop on any measured ceiling; never retry or reduce the sample."""
        status = Path("/proc/self/status").read_text()
        fields = dict(line.split(":", 1) for line in status.splitlines())
        threads = int(fields["Threads"])
        rss = int(fields["VmRSS"].split()[0]) * 1024
        self.peak_threads = max(self.peak_threads, threads)
        self.peak_rss = max(self.peak_rss, rss)
        measurements = {
            "wall_seconds": time.monotonic() - self.started,
            "memory_bytes": rss,
            "threads": threads,
        }
        usage = resource.getrusage(resource.RUSAGE_SELF)
        measurements["cpu_seconds"] = usage.ru_utime + usage.ru_stime
        for name, observed in measurements.items():
            if observed > self.limits[name]:
                raise self._audit.ResourceLimit(
                    f"{name}: {observed} > {self.limits[name]}"
                )

    def install(self) -> None:
        """Install non-widening OS limits; fail if this platform cannot enforce them."""
        if platform.system() != "Linux":
            raise RuntimeError(
                "real launcher requires Linux process limits and /proc accounting"
            )
        for kind, ceiling in (
            (resource.RLIMIT_AS, self.limits["memory_bytes"]),
            (resource.RLIMIT_CPU, self.limits["cpu_seconds"]),
            (resource.RLIMIT_FSIZE, self._audit.FILE_LIMIT),
        ):
            soft, hard = resource.getrlimit(kind)
            bound = min(
                value
                for value in (soft, hard, ceiling)
                if value != resource.RLIM_INFINITY
            )
            soft_bound = (
                bound - 1 if kind == resource.RLIMIT_CPU and bound == ceiling else bound
            )
            resource.setrlimit(kind, (soft_bound, bound))
        signal.signal(signal.SIGALRM, self._alarm)
        signal.setitimer(signal.ITIMER_REAL, self.limits["wall_seconds"])
        signal.signal(signal.SIGXCPU, self._alarm)
        signal.signal(signal.SIGXFSZ, self._alarm)
        self.check()

    def _alarm(self, signum: int, _frame: Any) -> None:
        raise self._audit.ResourceLimit(f"OS resource signal {signum}")


ROOT_DTYPES = {
    "Bool_t": "?",
    "bool": "?",
    "Int_t": "i4",
    "int": "i4",
    "UInt_t": "u4",
    "unsigned int": "u4",
    "Long64_t": "i8",
    "long long": "i8",
    "ULong64_t": "u8",
    "unsigned long long": "u8",
    "Float_t": "f4",
    "float": "f4",
    "Double_t": "f8",
    "double": "f8",
    "Short_t": "i2",
    "UShort_t": "u2",
    "Char_t": "i1",
    "UChar_t": "u1",
}


class RootAuditReader:
    """Copy only allowlisted raw branches, retaining nested lengths and dtypes.

    Parameters
    ----------
    resolved : ResolvedSource
        Manifest-validated identity. ROOT is imported only here.
    """

    def __init__(self, resolved: Any) -> None:
        ROOT = importlib.import_module("ROOT")
        import typed_descriptor_source_smoke as source

        self.source = source
        self.next_entry = 0
        self.file = ROOT.TFile.Open(resolved.path, "READ")
        self.tree: Any = None
        if not self.file or self.file.IsZombie():
            if self.file:
                self.file.Close()
            raise OSError("ROOT source open failed")
        try:
            self.metadata: dict[str, Any] = {
                "uuid": str(self.file.GetUUID().AsString()),
                "tree": source.TREE_NAME,
                "entries": None,
                "branches": {},
                "file_title": str(self.file.GetTitle()),
                "keys": [
                    {
                        "name": str(key.GetName()),
                        "title": str(key.GetTitle()),
                        "class": str(key.GetClassName()),
                    }
                    for key in self.file.GetListOfKeys()
                ],
                "publisher_checksum": None,
                "release_applicability": "RELEASE_UNVERIFIED",
            }
            if self.metadata["uuid"] != resolved.spec.expected_uuid:
                return
            self.tree = self.file.Get(source.TREE_NAME)
            if not self.tree:
                self.metadata["tree"] = None
                return
            self.metadata["entries"] = int(self.tree.GetEntries())
            self.metadata["tree_title"] = str(self.tree.GetTitle())
            self.metadata["producer_markers_verbatim"] = [
                {
                    "name": str(item.GetName()),
                    "title": str(item.GetTitle()),
                    "class": str(item.ClassName()),
                }
                for item in self.tree.GetUserInfo()
            ]
            for name in source.REQUIRED_BRANCHES:
                branch = self.tree.GetBranch(name)
                if not branch:
                    continue
                self.metadata["branches"][name] = self._branch_metadata(branch)
            self.tree.SetBranchStatus("*", 0)
            for name in source.REQUIRED_BRANCHES:
                self.tree.SetBranchStatus(name, 1)
        except Exception:
            self.file.Close()
            raise

    def _branch_metadata(self, branch: Any) -> dict[str, Any]:
        declaration = str(branch.GetClassName())
        leaves: list[dict[str, Any]] = [
            {
                "name": str(leaf.GetName()),
                "type": str(leaf.GetTypeName()),
                "length": int(leaf.GetLenStatic()),
                "count": (
                    str(leaf.GetLeafCount().GetName()) if leaf.GetLeafCount() else None
                ),
            }
            for leaf in branch.GetListOfLeaves()
        ]
        if declaration:
            cleaned = declaration.replace("std::", "").replace(" ", "")
            rank = cleaned.count("vector<")
            primitive = cleaned.replace("vector<", "").replace(">", "")
            dtype = {
                name.replace(" ", ""): dtype for name, dtype in ROOT_DTYPES.items()
            }.get(primitive, "O")
            shape: list[int | None] = [None] * rank
        elif len(leaves) == 1:
            leaf = leaves[0]
            dtype = ROOT_DTYPES.get(leaf["type"], "O")
            shape = (
                [None]
                if leaf["count"]
                else [leaf["length"]] if leaf["length"] > 1 else []
            )
            declaration = str(branch.GetTitle())
        else:
            dtype, shape = "O", []
        return {
            "dtype": dtype,
            "shape": shape,
            "declaration": declaration,
            "title": str(branch.GetTitle()),
            "leaves": leaves,
            "unapproved_count_dependencies": [
                leaf["count"]
                for leaf in leaves
                if leaf["count"] and leaf["count"] not in self.source.REQUIRED_BRANCHES
            ],
        }

    def read_entry(self, entry: int) -> dict[str, Any]:
        """Read each entry once in order; preserve branch-level extraction errors."""
        import numpy as np
        from typed_descriptor_source_audit import ResourceLimit

        if type(entry) is not int or entry != self.next_entry or not 0 <= entry < 4096:
            raise ValueError("out-of-scope, duplicate or out-of-order entry")
        self.next_entry += 1
        if int(self.tree.GetEntry(entry)) <= 0:
            raise OSError(f"ROOT GetEntry failed at {entry}")
        raw: dict[str, Any] = {}
        for name in self.source.REQUIRED_BRANCHES:
            try:
                metadata = self.metadata["branches"][name]
                value = getattr(self.tree, name)
                rank = len(metadata["shape"])
                if rank == 2:
                    raw[name] = [
                        np.asarray(list(child), dtype=metadata["dtype"])
                        for child in value
                    ]
                elif rank == 1:
                    raw[name] = np.asarray(list(value), dtype=metadata["dtype"])
                else:
                    raw[name] = np.asarray(value, dtype=metadata["dtype"])
            except (MemoryError, ResourceLimit):
                raise
            except Exception as error:
                raw[name] = {
                    "extraction_exception": type(error).__name__,
                    "message": str(error),
                }
        return raw

    def close(self) -> None:
        """Close exactly this source handle."""
        self.file.Close()


def validate_authorization(
    path: Path, expected_hash: str, commit: str
) -> dict[str, Any]:
    """Require explicit external authorization for the exact preparation digest."""
    if digest_file(path) != expected_hash:
        raise ValueError("authorization SHA-256 mismatch")
    authorization = json.loads(path.read_bytes())
    expected = {
        "action": "pet-v2-bounded-source-audit",
        "execution_authorized": True,
        "code_commit": commit,
        "bindings_sha256": digest_file(BINDING_FILE),
        "entry_interval": [0, 4096],
        "source_roles": ["data", "mc"],
        "branch_count": 75,
    }
    if any(
        type(authorization.get(key)) is not type(value)
        or authorization.get(key) != value
        for key, value in expected.items()
    ):
        raise ValueError("authorization does not match this bounded source audit")
    if not authorization.get("authority_reference"):
        raise ValueError("authorization needs a governing decision reference")
    return authorization


def main() -> int:
    """Verify preparation by default; execute only with all explicit bindings."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-preparation", action="store_true")
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--authorization-sha256")
    parser.add_argument("--expected-commit")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    binding = check_preparation()
    if args.check_preparation:
        print(
            json.dumps(
                {
                    "preparation": "PASS",
                    "execution_authorized": False,
                    "bindings_sha256": digest_file(BINDING_FILE),
                }
            )
        )
        return 0
    if not all(
        (
            args.authorization,
            args.authorization_sha256,
            args.expected_commit,
            args.output,
        )
    ):
        parser.error(
            "execution requires authorization, its digest, expected commit, and new output"
        )
    commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True
    ).strip()
    if commit != args.expected_commit:
        raise ValueError("checkout HEAD mismatch")
    dirty = subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=REPO_ROOT,
        text=True,
    )
    if dirty:
        raise ValueError("execution requires a clean committed checkout")
    authorization = validate_authorization(
        args.authorization, args.authorization_sha256, commit
    )
    import typed_descriptor_source_audit as audit

    budget = RuntimeBudget()
    bindings = {
        "preparation": binding,
        "bindings_sha256": digest_file(BINDING_FILE),
        "authorization": authorization,
        "authorization_sha256": args.authorization_sha256,
        "code_commit": commit,
        "execution_mode": "authorized_root",
        "python": sys.version,
        "platform": platform.platform(),
        "argv": sys.argv,
        "thread_environment": {key: os.environ[key] for key in THREAD_ENV},
    }
    # Installation and lazy dependency initialization occur inside the receipt boundary.
    initialized = False
    forward = None
    saved_streams: list[int] = []

    def resources() -> None:
        nonlocal initialized
        if not initialized:
            initialized = True
            for descriptor, name in ((1, "stdout.log"), (2, "stderr.log")):
                saved_streams.append(os.dup(descriptor))
                with (args.output / name).open("xb", buffering=0) as stream:
                    os.dup2(stream.fileno(), descriptor)
            budget.install()
        budget.check()

    def check_forward(batch: Any) -> None:
        nonlocal forward
        if forward is None:
            forward = audit.ForwardCheck()
        forward(batch)

    receipt = audit.run_audit(
        REPO_ROOT,
        args.output,
        reader_factory=RootAuditReader,
        forward_check=check_forward,
        check_resources=resources,
        bindings=bindings,
    )
    signal.setitimer(signal.ITIMER_REAL, 0)
    sys.stdout.flush()
    sys.stderr.flush()
    for descriptor, saved in zip((1, 2), saved_streams):
        os.dup2(saved, descriptor)
        os.close(saved)
    accounting = {
        "peak_observed_threads": budget.peak_threads,
        "peak_observed_rss_bytes": budget.peak_rss,
        "getrusage": list(resource.getrusage(resource.RUSAGE_SELF)),
        "receipt_sha256": digest_file(args.output / "receipt.json"),
        "closed_auxiliary_artifacts": {
            name: {
                "sha256": digest_file(args.output / name),
                "bytes": (args.output / name).stat().st_size,
            }
            for name in (
                "stdout.log",
                "stderr.log",
                "interrupted.json",
                "progress.jsonl",
            )
            if (args.output / name).exists()
        },
        "output_bytes_before_accounting": sum(
            path.stat().st_size for path in args.output.rglob("*") if path.is_file()
        ),
    }
    (args.output / "accounting.json").write_bytes(audit.canonical_json(accounting))
    print(
        json.dumps(
            {
                "terminal": receipt["terminal"],
                "mapping": receipt["mapping"],
                "semantic": receipt["semantic"],
                "release": receipt["release"],
            }
        )
    )
    return 0 if receipt["mapping"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
