#!/usr/bin/env python3
"""Connect for one explicitly approved IBUKT action; never advance stages automatically.

The local entry point requires action-specific approval and fence records naming
these exact script bytes. Remote execution writes only a new scratch campaign.
Importing this module performs no connection, submission, staging or fit.

Before each SSH connection, notify cov2d and tier3-design: name the action,
campaign and script SHA-256, specify the intended CPU-only window and the
protected E_R, CV and ancillary inputs, and ask each lane to acknowledge the
fence. The operator records the actual notices and replies and confirms that
the director has cleared any additional overlapping lanes. The approval JSON
contains action, script_sha256, host, run_name, director_go and joseph_go
(each with action, script_sha256 and reference), and fences keyed by lane
(each with action, script_sha256, notice_id, ack_id and time_unix). Actions
after envstage also require previous_sha256 from the reviewed PASS receipt.
These references record human decisions; creating the JSON cannot grant them.

The lane owns this launcher and the director reviews its frozen hash. A refused
gate or failed allocation is terminal for this attempt and returns to review.
No changes to the estimators or science thresholds follow from a refusal.
"""

from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
import os
import pwd
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import time
from typing import Any

BOUND = "d93ab9ad8be8d68fe4337d4b2edf7d730a39344e"
RUN_NAME = "ibukt-20261119-c"
DECLARATION = "8511925449d3d0b4826da4bd099dfd5b2d079cb92a47381552fe47f6602a3c14"
BINDING = "df5cdaa88994ac1cafd255b556ef0ae53a42d10860bbf24a9df8c1dfa26aa25c"
ACTIONS = ("envstage", "prepare", "screen", "score")
STEP_MEM_MIB = 121920
LIMITS = {
    "prepare": ("00:30:00", 0.5),
    "screen": ("05:15:00", 5.25),
    "score": ("00:06:00", 0.1),
}
PRIOR_PREPARE_JOB = "61556304"
PRIOR_PREPARE_SACCT = "61556304|ibukt-prepare|FAILED|638|1"
TERMINAL = {
    "COMPLETED",
    "FAILED",
    "CANCELLED",
    "TIMEOUT",
    "OUT_OF_MEMORY",
    "NODE_FAIL",
    "PREEMPTED",
    "BOOT_FAIL",
    "DEADLINE",
}
FAMILIES = ("cov2d", "t2a", "ll5d", "e96data", "rpd_", "rsn_", "rdx_", "pfb_", "ibukt-")
PINS = {
    "ibukt.py": "f98fc9930e4bbdcb60328553d9e0b9ce267be14542f84b3ecafa0f5ff642a7c0",
    "run_ibukt.py": "ff1b0c35ccc0ff2c71c9001e049e5efdba555f9dba11fd3def858e14c333a00f",
    "jobs.py": "85a11ceafb4308d94ca40134d7af8dac99a28b395011520e23986beca425edb7",
    "screen.sbatch": "469881a2846666dfebd8b62cd41c0982e5d5b8d1cb553c3537a49c80f583396d",
    "config.json": "35f344676d83b93ecdf458d8683263f869d7f66522b58950ea3db3faebaf4206",
}


def checked_sha(value: str) -> str:
    """Require a complete SHA-256 identity."""
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise ValueError("a full SHA-256 is required")
    return value


def read_bytes(path: Path) -> bytes:
    """Use O_NOATIME for every remote file read; never fall back on failure."""
    flag = getattr(os, "O_NOATIME", None)
    if flag is None:
        raise RuntimeError("remote reads require O_NOATIME")
    with os.fdopen(os.open(path, os.O_RDONLY | flag), "rb") as stream:
        return stream.read()


def digest(path: Path) -> str:
    """Hash a protected file without advancing its access time."""
    flag = getattr(os, "O_NOATIME", None)
    if flag is None:
        raise RuntimeError("remote hashes require O_NOATIME")
    result = hashlib.sha256()
    with os.fdopen(os.open(path, os.O_RDONLY | flag), "rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 24), b""):
            result.update(chunk)
    return result.hexdigest()


def read_json(path: Path) -> Any:
    """Read a protected JSON receipt."""
    return json.loads(read_bytes(path))


def write_json(path: Path, record: Any) -> None:
    """Create an immutable receipt without replacing an earlier attempt."""
    with path.open("x") as stream:
        json.dump(record, stream, indent=2, allow_nan=False)
        stream.write("\n")


def validate_approval(action: str, pin: str, approval: dict[str, Any]) -> None:
    """Require recorded human goes and both acknowledged pre-connect notices."""
    checked_sha(pin)
    if (
        action not in ACTIONS
        or approval["action"] != action
        or approval["script_sha256"] != pin
    ):
        raise ValueError("approval action or script identity differs")
    for owner in ("director", "joseph"):
        record = approval[f"{owner}_go"]
        if (
            record["action"] != action
            or record["script_sha256"] != pin
            or not record["reference"]
        ):
            raise ValueError(f"missing action-specific {owner} go")
    for lane in ("cov2d", "tier3-design"):
        notice = approval["fences"][lane]
        if (notice["action"], notice["script_sha256"]) != (action, pin) or not all(
            notice[k] for k in ("notice_id", "ack_id")
        ):
            raise ValueError(f"missing acknowledged fence notice: {lane}")
        age = datetime.now(timezone.utc).timestamp() - float(notice["time_unix"])
        if not 0 <= age <= 900:
            raise ValueError(
                "fence acknowledgment is older than 15 minutes or in the future"
            )
    if approval["run_name"] != RUN_NAME:
        raise ValueError(f"approval must name campaign {RUN_NAME}")
    if not re.fullmatch(r"[A-Za-z0-9_.@-]+", approval["host"]) or approval[
        "host"
    ].startswith("-"):
        raise ValueError("invalid explicitly approved SSH destination")
    if action != "envstage":
        checked_sha(approval["previous_sha256"])


def command(argv: list[str], *, cwd: Path | None = None) -> str:
    """Run a checked operational command without a shell."""
    return subprocess.run(
        argv, cwd=cwd, check=True, text=True, capture_output=True
    ).stdout


def scratch_path(path: Path) -> Path:
    """Refuse symlinks or paths that escape the scratch filesystem."""
    resolved = path.resolve()
    if not resolved.is_relative_to(Path("/pscratch")):
        raise ValueError("all remote writes must stay on /pscratch")
    return resolved


def verify_previous(root: Path, action: str, expected: str, pin: str) -> dict[str, Any]:
    """Verify the previous stage's PASS receipt and every recorded artifact."""
    previous = ACTIONS[ACTIONS.index(action) - 1]
    path = root / previous / "PASS.json"
    if digest(path) != checked_sha(expected):
        raise ValueError("previous PASS receipt digest differs")
    record = read_json(path)
    if (record["status"], record["action"], record["bound_commit"]) != (
        "PASS",
        previous,
        BOUND,
    ):
        raise ValueError("previous stage did not pass the bound experiment")
    if (record["run_root"], record["script_sha256"]) != (str(root), pin):
        raise ValueError("previous receipt belongs to another run")
    for rel, pin in record["artifacts"].items():
        target = scratch_path(root / rel)
        if not target.is_relative_to(root) or digest(target) != pin:
            raise ValueError(f"previous artifact changed: {rel}")
    return dict(record)


def sacct(root: Path, label: str, *, report: bool = False) -> str:
    """Capture all allocations since declaration; refuse active protected families."""
    text = command(
        [
            "sacct",
            "-X",
            "-n",
            "-P",
            "-S",
            "2026-11-17",
            "-u",
            pwd.getpwuid(os.getuid()).pw_name,
            "--format=JobIDRaw,JobName%100,State%40,ElapsedRaw,NNodes",
        ]
    )
    snapshot = root / f"{label}.sacct.txt"
    with snapshot.open("xb") as stream:
        stream.write(text.encode("utf-8"))
    if report:
        print(
            json.dumps(
                {"path": snapshot.name, "sha256": digest(snapshot), "sacct": text}
            ),
            flush=True,
        )
    if not text.strip():
        raise ValueError("empty scheduler fence snapshot")
    for line in text.splitlines():
        job, name, state, elapsed, nodes = line.split("|")
        if not job or not state or not elapsed.isdigit() or not nodes.isdigit():
            raise ValueError("malformed sacct fence")
        if name.startswith(FAMILIES) and state.split()[0].rstrip("+") not in TERMINAL:
            raise ValueError(f"protected allocation is unended: {job} {name} {state}")
    return text


def verify_deploy(root: Path) -> dict[str, Any]:
    """Require the clean frozen deployment, binding and imported code pins."""
    deploy = root / "deploy"
    if (
        command(["git", "rev-parse", "HEAD"], cwd=deploy).strip() != BOUND
        or command(["git", "status", "--porcelain"], cwd=deploy).strip()
    ):
        raise ValueError("deployment is not clean at the bound commit")
    prefix = deploy / "2d-unfolding/ibukt"
    for rel, pin in PINS.items():
        if digest(prefix / rel) != pin:
            raise ValueError(f"bound source changed: {rel}")
    records = deploy / "docs/orchestration/state/2d-closeout"
    for name, pin in (
        ("IBUKT-DECLARATION.md", DECLARATION),
        ("IBUKT-BINDING-1.md", BINDING),
    ):
        if digest(records / name) != pin:
            raise ValueError("governing record changed")
    cfg = read_json(prefix / "config.json")
    for rel, pin in cfg["code_sha256"].items():
        if digest(deploy / rel) != pin:
            raise ValueError(f"imported code changed: {rel}")
    if (
        digest(deploy / "nd-unfolding/mnv_guarded_run.py")
        != "30162f57771c9d5a1206eae623a7eb3fc80ac3f0bb150c82fb561be7254b510b"
    ):
        raise ValueError("import guard changed")
    return dict(cfg)


def guarded(root: Path, label: str, script: str, args: list[str]) -> list[str]:
    """Build a producer command with the rooted import guard and its own inventory."""
    deploy = root / "deploy"
    return [
        sys.executable,
        "-B",
        str(deploy / "nd-unfolding/mnv_guarded_run.py"),
        "--expect-root",
        str(deploy),
        "--inventory",
        str(root / f"{label}.imports.jsonl"),
        "--label",
        f"ibukt-{label}",
        "--",
        str(deploy / f"2d-unfolding/ibukt/{script}"),
        *args,
    ]


def environment(root: Path) -> dict[str, Any]:
    """Measure the explicit ROOT environment; subsequent stages pin this record."""
    expected = Path.home() / ".conda/envs/root_6_28/bin/python3"
    if Path(sys.executable).resolve() != expected.resolve() or sys.version_info[:2] != (
        3,
        11,
    ):
        raise ValueError("requires the named root_6_28 Python 3.11 interpreter")
    prefix = os.environ.get("CONDA_PREFIX")
    if not prefix or Path(prefix).resolve() != expected.parent.parent.resolve():
        raise ValueError("requires an activated root_6_28 conda environment")

    import ROOT
    import lightgbm
    import numpy
    import sklearn

    if not ROOT.gROOT.GetVersion().startswith("6.28/"):
        raise ValueError("requires ROOT 6.28")
    if ROOT.gSystem.Load(str(root / "stage/libRooUnfold.so")) < 0:
        raise ValueError("staged RooUnfold library failed to load")
    return {
        "conda_prefix": str(Path(prefix).resolve()),
        "compiler": shutil.which("x86_64-conda-linux-gnu-c++"),
        "python": sys.version,
        "python_sha256": digest(Path(sys.executable)),
        "ROOT": ROOT.gROOT.GetVersion(),
        "numpy": numpy.__version__,
        "lightgbm": lightgbm.__version__,
        "sklearn": sklearn.__version__,
    }


def quota_check(root: Path, needed: int) -> None:
    """Require scratch headroom and project quota below 90 percent before staging."""
    quotas = json.loads(command(["showquota", "--json", "m3246"]))
    write_json(root / "quota.json", quotas)
    for fs in ("pscratch", "m3246"):
        rows = [row for row in quotas if row["fs"] == fs]
        if len(rows) != 1 or any(
            not 0 <= float(str(rows[0][key]).rstrip("%")) < 90
            for key in ("space_perc", "inode_perc")
        ):
            raise ValueError(
                f"quota missing or above the 90 percent headroom gate: {fs}"
            )
    stat = os.statvfs(root)
    if stat.f_bavail * stat.f_frsize < max(4 * needed, 32 << 30):
        raise ValueError("insufficient scratch filesystem headroom")


def envstage(root: Path) -> list[Path]:
    """Clone frozen code and stage the six protected inputs without a Slurm job."""
    command(
        [
            "git",
            "clone",
            "--no-checkout",
            "https://github.com/josephbaileyy/MINERvA-OmniFold.git",
            str(root / "deploy"),
        ]
    )
    command(["git", "checkout", "--detach", BOUND], cwd=root / "deploy")
    cfg = verify_deploy(root)
    comparison = read_json(root / "deploy/2d-unfolding/ref_c2c1/config.json")
    scratch = Path(os.environ["SCRATCH"]).resolve()
    sources = {
        "cv": comparison["inputs"]["CV_source"],
        "flux": comparison["inputs"]["MC_source"],
        "er": comparison["e_r"]["central"],
        "library": comparison["inputs"]["roounfold_lib"],
        "paper": comparison["publication"]["path"],
        "c2": str(scratch / "ref-c2c1-20261106/units/c2_central.npz"),
    }
    quota_check(root, sum(Path(path).stat().st_size for path in sources.values()))
    write_json(root / "sources.json", sources)
    command(
        guarded(
            root,
            "envstage-stage",
            "jobs.py",
            [
                "stage",
                "--sources",
                str(root / "sources.json"),
                "--out",
                str(root / "stage"),
            ],
        ),
        cwd=root / "deploy",
    )
    env = environment(root)
    write_json(root / "environment.json", env)
    return [
        root / "stage/stage.json",
        root / "environment.json",
        root / "sources.json",
        *[root / "stage" / pin["filename"] for pin in cfg["inputs"].values()],
    ]


def verify_inputs(root: Path, cfg: dict[str, Any]) -> None:
    """Recheck staged bytes and the exact environment before any producer starts."""
    for pin in cfg["inputs"].values():
        if digest(root / "stage" / pin["filename"]) != pin["sha256"]:
            raise ValueError("staged input changed")
    if environment(root) != read_json(root / "environment.json"):
        raise ValueError("environment differs from envstage")


def pass_receipt(root: Path, action: str, pin: str, artifacts: list[Path]) -> None:
    """Write PASS only after the named action and its output checks complete."""
    record = {
        "status": "PASS",
        "action": action,
        "script_sha256": pin,
        "bound_commit": BOUND,
        "run_root": str(root),
        "artifacts": {str(path.relative_to(root)): digest(path) for path in artifacts},
    }
    path = root / action / "PASS.json"
    write_json(path, record)
    print(json.dumps({"receipt": str(path), "sha256": digest(path)}), flush=True)


def accounting(root: Path, action: str, rows: str) -> Path:
    """Reconcile every immutable submission, including failures and missing jobs."""
    prior = [
        line for line in rows.splitlines() if line.startswith(f"{PRIOR_PREPARE_JOB}|")
    ]
    if prior != [PRIOR_PREPARE_SACCT]:
        raise ValueError(
            "previous prepare allocation is missing or differs from its recorded terminal charge"
        )
    reservations = {PRIOR_PREPARE_JOB: LIMITS["prepare"][1]}
    for stage in ("prepare", "screen", "score"):
        directory = root / stage
        if (directory / "submit-intent.json").exists():
            record = read_json(directory / "submission.json")
            reservations[record["job_id"]] = LIMITS[stage][1]
    ledger = root / action / "reservations.json"
    write_json(ledger, reservations)
    snapshot = root / action / "accounting.sacct.txt"
    snapshot.write_text(rows)
    argv = guarded(
        root,
        f"{action}-admit",
        "jobs.py",
        [
            "gate",
            "--sacct",
            str(snapshot),
            "--reservations",
            str(ledger),
            "--request",
            action,
        ],
    )
    admission = json.loads(command(argv, cwd=root / "deploy"))
    output = root / action / "admission.json"
    write_json(output, admission)
    return output


def allocation_check(root: Path, action: str) -> None:
    """Check actual submitted CPU allocation through sacct before producer work."""
    job = os.environ["SLURM_JOB_ID"]
    text = command(
        [
            "sacct",
            "-X",
            "-n",
            "-P",
            "-j",
            job,
            "--noconvert",
            "--format=JobIDRaw,JobName%100,State,TimelimitRaw,NNodes,ReqCPUS,AllocCPUS,ReqMem,Constraints%100,AllocTRES%200,Restarts",
        ]
    )
    (root / action / "allocation.sacct.txt").write_text(text)
    rows = [line.split("|") for line in text.splitlines() if line.split("|")[0] == job]
    if len(rows) != 1:
        raise ValueError(
            "allocation settings not yet visible in sacct; stop without retry"
        )
    (
        _,
        name,
        state,
        minutes,
        nodes,
        requested,
        allocated,
        memory,
        constraint,
        tres,
        restarts,
    ) = rows[0]
    minimum = 128 if action == "screen" else 64
    expected_mem = STEP_MEM_MIB * (2 if action == "screen" else 1)
    if (
        (name, state, int(minutes), int(nodes))
        != (f"ibukt-{action}", "RUNNING", int(LIMITS[action][1] * 60), 1)
        or int(requested) != minimum
        or not minimum <= int(allocated) <= 256
        or constraint != "cpu"
        or memory not in {f"{expected_mem}M", f"{expected_mem}Mn"}
        or "gres/gpu" in tres
        or restarts != "0"
    ):
        raise ValueError(
            "actual allocation differs from CPU-only time/CPU/memory binding"
        )


def producer(root: Path, action: str, admission: Path) -> list[Path]:
    """Run exactly the named bound producer and preserve all of its output identities."""
    deploy = root / "deploy"
    out = root / action / "out"
    if action == "screen":
        os.environ.update(
            IBUKT_DEPLOY=str(deploy),
            IBUKT_STAGE=str(root / "stage"),
            IBUKT_PREPARE=str(root / "prepare/out"),
            IBUKT_PRODUCTS=str(out),
            IBUKT_PYTHON=sys.executable,
            IBUKT_DEPLOY_SHA=BOUND,
            IBUKT_ADMISSION=str(admission),
        )
        # Execute the frozen launcher unchanged: C-NOM, timed nominal-0, forecast, remaining 34.
        subprocess.run(
            ["bash", str(deploy / "2d-unfolding/ibukt/screen.sbatch")],
            cwd=deploy,
            check=True,
        )
        products = [out / name for name in ("admission.json", "forecast.json")]
        for truth in (
            "nominal-control",
            *[
                f"{name}-{trial}"
                for name in read_json(deploy / "2d-unfolding/ibukt/config.json")[
                    "truths"
                ]
                for trial in range(5)
            ],
        ):
            record = read_json(out / truth / "pair.json")
            if record["status"] != "PASS" or record["product_sha256"] != digest(
                out / truth / "pair.npz"
            ):
                raise ValueError("incomplete or changed paired screen")
            products.extend([out / truth / "pair.json", out / truth / "pair.npz"])
        return products
    args = [action, "--stage", str(root / "stage"), "--out", str(out)]
    if action == "score":
        args += [
            "--bank",
            str(root / "prepare/out/bank.npz"),
            "--identity",
            str(root / "prepare/out/identity.json"),
            "--products",
            str(root / "screen/out"),
            "--control",
            str(root / "screen/out/nominal-control/pair.json"),
        ]
    argv = guarded(root, f"{action}-produce", "run_ibukt.py", args)
    subprocess.run(
        [
            "srun",
            "-n1",
            "-c",
            "64",
            "--exact",
            f"--mem={STEP_MEM_MIB}M",
            "--mem-bind=local",
            *argv,
        ],
        cwd=deploy,
        check=True,
    )
    return (
        [out / "bank.npz", out / "identity.json"]
        if action == "prepare"
        else [out / "readout.json"]
    )


def worker(root: Path, action: str, pin: str) -> None:
    """Verify the submitted job and run one producer; failed attempts leave no PASS."""
    root = scratch_path(root)
    directory = root / action
    # The allocation can start before sbatch returns to the submitter.
    submission = directory / "submission.json"
    for _ in range(15):
        if submission.is_file():
            break
        time.sleep(2)
    if read_json(submission)["job_id"] != os.environ["SLURM_JOB_ID"]:
        raise ValueError("worker does not own the recorded submission")
    approval = read_json(directory / "approval.json")
    verify_previous(root, action, approval["previous_sha256"], pin)
    allocation_check(root, action)
    cfg = verify_deploy(root)
    verify_inputs(root, cfg)
    admission = root / action / "admission.json"
    if (
        digest(admission)
        != read_json(root / action / "submit-intent.json")["admission_sha256"]
    ):
        raise ValueError("SHA-pinned admission changed")
    artifacts = producer(root, action, admission)
    pass_receipt(root, action, pin, artifacts)


def submit(root: Path, action: str, pin: str, admission: Path) -> None:
    """Submit once, persisting intent before submission and the job reservation after."""
    directory = root / action
    script = directory / "job.sbatch"
    connect = root / "connect.py"
    body = (
        "#!/bin/bash\nset -euo pipefail\n"
        + "exec "
        + shlex.join(
            [sys.executable, "-B", str(connect), "--worker", action, str(root), pin]
        )
        + "\n"
    )
    script.write_text(body)
    write_json(
        directory / "submit-intent.json",
        {
            "action": action,
            "limit_node_h": LIMITS[action][1],
            "admission_sha256": digest(admission),
            "job_script_sha256": digest(script),
        },
    )
    argv = [
        "sbatch",
        "--parsable",
        "--account=m3246",
        "--qos=regular",
        "--constraint=cpu",
        "--nodes=1",
        "--exclusive",
        f"--ntasks={2 if action == 'screen' else 1}",
        "--cpus-per-task=64",
        f"--mem={STEP_MEM_MIB * (2 if action == 'screen' else 1)}M",
        f"--time={LIMITS[action][0]}",
        "--no-requeue",
        f"--job-name=ibukt-{action}",
        f"--chdir={root / 'deploy'}",
        f"--output={directory / '%x_%j.out'}",
        f"--error={directory / '%x_%j.err'}",
        str(script),
    ]
    job = command(argv).strip().split(";")[0]
    if not job.isdigit():
        raise ValueError("ambiguous submission; retain intent, stop, never retry")
    pending = directory / "submission.pending.json"
    write_json(
        pending, {"job_id": job, "reservation_node_h": LIMITS[action][1], "argv": argv}
    )
    pending.rename(directory / "submission.json")
    print(
        json.dumps(
            {
                "status": "SUBMITTED",
                "action": action,
                "job_id": job,
                "reservation_node_h": LIMITS[action][1],
            }
        ),
        flush=True,
    )


def remote(action: str, approval: dict[str, Any], source: bytes) -> None:
    """Apply one approved connect inside a fresh, exclusively owned scratch run."""
    pin = hashlib.sha256(source).hexdigest()
    validate_approval(action, pin, approval)
    requested_root = Path(os.environ["SCRATCH"]).resolve() / approval["run_name"]
    root = scratch_path(requested_root)
    if root != requested_root:
        raise ValueError("run must be directly under the current user's SCRATCH")
    os.umask(0o077)
    if action == "envstage":
        root.mkdir(exist_ok=False)
        (root / "connect.py").write_bytes(source)
    elif digest(root / "connect.py") != pin:
        raise ValueError("stored connect script changed")
    directory = root / action
    if action != "envstage":
        verify_previous(root, action, approval["previous_sha256"], pin)
    directory.mkdir(exist_ok=False)
    os.chdir(root)
    for variable, suffix in (
        ("TMPDIR", "tmp"),
        ("MPLCONFIGDIR", "mpl"),
        ("XDG_CACHE_HOME", "cache"),
    ):
        path = scratch_path(directory / suffix)
        path.mkdir()
        os.environ[variable] = str(path)
    for key in list(os.environ):
        if key.startswith(("SBATCH_", "SRUN_", "SLURM_", "SACCT_")) or key in {
            "PYTHONPATH",
            "PYTHONHOME",
            "BASH_ENV",
        }:
            del os.environ[key]
    os.environ.update(
        PYTHONDONTWRITEBYTECODE="1",
        PYTHONUNBUFFERED="1",
        PYTHONNOUSERSITE="1",
        GIT_OPTIONAL_LOCKS="0",
        OMP_NUM_THREADS="64",
        MKL_NUM_THREADS="1",
        OPENBLAS_NUM_THREADS="1",
        NUMEXPR_NUM_THREADS="1",
        CUDA_VISIBLE_DEVICES="",
    )
    write_json(directory / "approval.json", approval)
    sacct(directory, "before", report=action == "envstage")
    if action == "envstage":
        pass_receipt(root, action, pin, envstage(root))
        return
    cfg = verify_deploy(root)
    verify_inputs(root, cfg)
    rows = sacct(directory, "presubmit")
    if action in ("screen", "score"):
        previous = ACTIONS[ACTIONS.index(action) - 1]
        job = read_json(root / previous / "submission.json")["job_id"]
        completed = [
            line.split("|") for line in rows.splitlines() if line.split("|")[0] == job
        ]
        if len(completed) != 1 or completed[0][2] != "COMPLETED":
            raise ValueError("prior job is not recorded COMPLETED in fresh sacct")
    admission = accounting(root, action, rows)
    submit(root, action, pin, admission)


def main() -> None:
    """Require explicit local approvals before making the single SSH connection."""
    if len(sys.argv) == 5 and sys.argv[1] == "--worker":
        action, root, pin = sys.argv[2:]
        if action not in LIMITS or digest(Path(__file__)) != checked_sha(pin):
            raise ValueError("worker action or script identity differs")
        worker(Path(root), action, pin)
        return
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=ACTIONS)
    parser.add_argument("--approval", type=Path, required=True)
    parser.add_argument("--sha256", required=True)
    args = parser.parse_args()
    source = Path(__file__).read_bytes()
    pin = hashlib.sha256(source).hexdigest()
    if pin != checked_sha(args.sha256):
        parser.error("connect script is not the approved SHA-256")
    approval = json.loads(args.approval.read_text())
    validate_approval(args.action, pin, approval)
    packet = base64.b64encode(
        json.dumps(
            {
                "action": args.action,
                "approval": approval,
                "source": base64.b64encode(source).decode(),
            }
        ).encode()
    ).decode()
    bootstrap = (
        "import base64,json,sys\n"
        "p=json.loads(base64.b64decode(sys.stdin.buffer.read()))\n"
        "if p['approval']['run_name'] != sys.argv[1]: raise SystemExit('campaign mismatch')\n"
        "s=base64.b64decode(p['source'])\n"
        "ns={'__name__':'ibukt_connect_remote'}\n"
        "exec(compile(s,'<ibukt-connect>','exec'),ns)\n"
        "ns['remote'](p['action'],p['approval'],s)"
    )
    # Match the Miniforge hook and prefix used by the per-period remote2.sh.
    shell = (
        "hook=$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook) || exit 16\n"
        'eval "$hook" || exit 16\n'
        'conda activate "$HOME/.conda/envs/root_6_28" || exit 16\n'
        'exec "$HOME/.conda/envs/root_6_28/bin/python3" -B -c '
        + shlex.quote(bootstrap)
        + " "
        + shlex.quote(RUN_NAME)
    )
    remote_command = shlex.join(["bash", "-c", shell])
    subprocess.run(
        ["ssh", "-T", "-o", "BatchMode=yes", approval["host"], remote_command],
        input=packet,
        text=True,
        check=True,
    )


if __name__ == "__main__":
    main()
