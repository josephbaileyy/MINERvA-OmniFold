"""Generate the d2-predict + step0 READY package (rpd_d2s0) from P0's bound package by counted replacements.

usage: python3 -I -B gen_d2s0.py

Inputs, each asserted at its sha256:
  - P0's bound package (binding 2 addendum 3, M_P0 13aee9c0): rpd_p0_connect.sh 6a1bed95 (with its runner 3ef4abad),
    rpd_p0_fetch.sh 12626af6, rpd_p0_launch.sh b70998ff, tools/fence_overlap.py 23d0ffc7, tools/p0_expected.json
    bb175e94, tools/p0_checks.py 93d0de8b, tools/p0_supervise.py 6ad0f68f, production-config.ready.json 3b2afde4;
  - P0's committed records (run-20261124, merged 055b9041 and 92652b97): records/run/p0.json 8ed2faf7 and
    records/run/pins.json.gz, which decompresses to 52fc41f4.

The director accepted (2026-11-24): a new root; P0's run/pins.json and run/p0.json read with O_NOATIME, sha-checked
against the committed records, then copied byte for byte into the new run directory; config 3b2afde4 unchanged
(require_predecessors needs it); P0's supervisor, runner and fetch carried over; an iris balance read in the connect
output only. The bound code allows no dry run for d2-predict or step0 (fd_rpd_reco.py DRY_RUN_SCOPE, :3058-3062), so the
chain is d2-predict then step0, each once, each with its own 7200 s deadline. Neither opens a measured key: step0 streams
samples(data=False) (:2272) and d2-predict calls aggregate(..., data=False) (:3108-3110), and no --prediction is passed,
so Inputs.key("measured") would STOP with PREDICTION_COMMITTED (:677-678, :689-693).
"""

from __future__ import annotations

import base64
import gzip
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
P0 = OUT.parent / "p0-20261123"
P0_RECORDS = P0 / "run-20261124" / "records" / "run"
ROOT = "/pscratch/sd/j/josephrb/rpd-reco-d2s0-20261124"
P0_ROOT = "/pscratch/sd/j/josephrb/rpd-reco-p0-20261123"
SHM = "/dev/shm/limres-rpd-flux1"
SHA = {
    "connect": "6a1bed9547b7a462b3ccdbbe05c34f322a27980be085d2996eb89950a25da678",
    "fetch": "12626af6f6ff5d765b602ebd0f012f2e3d6f8d3f1fa60969b0f8bd4d4e022b6a",
    "launch": "b70998fffa5de0f585ef3e60e24b17c7ba166bc10e718d13187e424928e4e366",
    "fence": "23d0ffc7bf89a4b81a33b081fa7377401dec33634372d5ed5b106bee6c4fd22b",
    "expected": "bb175e948fff89fc1e3097b0aaf5107e5e796bc05e1f4892e0d00b07b2a5b6b6",
    "checks": "93d0de8bda48a00eeba4edab306590146f5c1d807bed701be021bdfb0b864fcc",
    "supervise": "6ad0f68fb309a7b83adc0f65ed709e5e2412e650e115075fe41ebbc7a070134f",
    "config": "3b2afde495d630cc44df730e3e1acf12e0c332953e9fa298fa979f2e2e39b057",
    "p0_record": "8ed2faf71a3966ed832831ba669c093235aa39c00fda515edecfd6b60a34be10",
    "pins_record": "52fc41f41cf17954ceddab8c581aa327a62d160c059cbee8bf2941c1880e5c8a",
    "runner": "3ef4abad4f05a8ef9fb5319c6d463d72e5ecabb3bed75defa74c712a28df07c4",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def b64(data: bytes) -> str:
    return base64.b64encode(data).decode()


def dump(value: dict) -> bytes:
    return (json.dumps(value, indent=1, sort_keys=True, ensure_ascii=True) + "\n").encode()


def replace(text: str, old: str, new: str, count: int, what: str) -> str:
    found = text.count(old)
    assert found == count, f"{what}: {found} occurrences of {old[:70]!r}, expected {count}"
    return text.replace(old, new)


def block(text: str, start: str, end: str) -> str:
    """The exact text from the first line equal to START up to (not including) the first later line equal to END."""
    lines = text.splitlines(keepends=True)
    first = [i for i, line in enumerate(lines) if line == start + "\n"]
    assert first and first[0] == 0, (start, first)  # the file's own first line
    last = [i for i, line in enumerate(lines) if i > first[0] and line == end + "\n"]
    assert last, (start, end)
    return "".join(lines[first[0] : last[0]])


def runner_of(connect: str) -> str:
    lines = connect.splitlines(keepends=True)
    i = next(n for n, line in enumerate(lines) if line.startswith("cat > ") and line.endswith("<<'RUNNER'\n"))
    j = next(n for n, line in enumerate(lines) if n > i and line == "RUNNER\n")
    return "".join(lines[i + 1 : j])


def main() -> int:
    files = {
        "connect": P0 / "rpd_p0_connect.sh",
        "fetch": P0 / "rpd_p0_fetch.sh",
        "launch": P0 / "rpd_p0_launch.sh",
        "fence": P0 / "tools" / "fence_overlap.py",
        "expected": P0 / "tools" / "p0_expected.json",
        "checks": P0 / "tools" / "p0_checks.py",
        "supervise": P0 / "tools" / "p0_supervise.py",
        "config": P0 / "production-config.ready.json",
        "p0_record": P0_RECORDS / "p0.json",
    }
    old = {key: path.read_bytes() for key, path in files.items()}
    for key, data in old.items():
        assert sha(data) == SHA[key], key
    pins_record = gzip.decompress((P0_RECORDS / "pins.json.gz").read_bytes())
    assert sha(pins_record) == SHA["pins_record"]
    assert json.loads(old["p0_record"])["predecessor_sha256"] == SHA["pins_record"]
    connect = old["connect"].decode()
    assert sha(runner_of(connect).encode()) == SHA["runner"]
    supervise = old["supervise"]  # carried over unchanged
    checks = (HERE / "d2s0_checks.py").read_bytes()

    # 1. The expected values: P0's 14 in-place inputs and 27 stat entries, plus P0's two run records.
    expected_old = json.loads(old["expected"])
    assert dump(expected_old) == old["expected"], "P0's expected values do not reproduce"
    inputs = dict(expected_old["inputs"])
    pins_path, p0_path = f"{P0_ROOT}/run/pins.json", f"{P0_ROOT}/run/p0.json"
    assert pins_path not in inputs and p0_path not in inputs and len(inputs) == 14
    inputs[pins_path] = SHA["pins_record"]
    inputs[p0_path] = SHA["p0_record"]
    expected = dump({"inputs": inputs, "stat": expected_old["stat"]})

    # 2. The fence copy: only its write root changes.
    fence = replace(
        old["fence"].decode(), f'WRITE_ROOTS = ("{P0_ROOT}",', f'WRITE_ROOTS = ("{ROOT}",', 1, "fence root"
    ).encode()

    # 3. The connect (and its runner).
    connect = replace(connect, block(connect, "#!/bin/bash", "umask 077"), CONNECT_HEADER, 1, "connect header")
    runner_old = runner_of(connect)
    runner = replace(runner_old, block(runner_old, "#!/bin/bash", "umask 077"), RUNNER_HEADER, 1, "runner header")
    runner = replace(runner, RUNNER_DEADLINE_OLD, RUNNER_DEADLINE_NEW, 1, "runner deadline (now per step)")
    runner = replace(runner, RUNNER_STEP_HEAD_OLD, RUNNER_STEP_HEAD_NEW, 1, "runner step: own deadline")
    runner = replace(runner, '"${label%%-*}"', '"$label"', 1, "runner step name (d2-predict keeps its hyphen)")
    runner = replace(runner, RUNNER_STEPS_OLD, RUNNER_STEPS_NEW, 1, "runner steps")
    runner = replace(runner, 'echo "== P0 DONE', 'echo "== D2S0 DONE', 1, "runner done line")
    runner = replace(runner, "== rpd_p0 runner", "== rpd_d2s0 runner", 1, "runner banner")
    connect = replace(connect, runner_old, runner, 1, "runner body")
    connect = replace(connect, b64(old["checks"]), b64(checks), 1, "checks blob")
    connect = replace(connect, b64(old["expected"]), b64(expected), 1, "expected blob")
    connect = replace(connect, b64(old["fence"]), b64(fence), 1, "fence blob")
    connect = replace(connect, f"CHECKS_SHA={SHA['checks']}", f"CHECKS_SHA={sha(checks)}", 1, "checks sha")
    connect = replace(connect, f"EXPECTED_SHA={SHA['expected']}", f"EXPECTED_SHA={sha(expected)}", 1, "expected sha")
    connect = replace(connect, f"FENCE_SHA={SHA['fence']}", f"FENCE_SHA={sha(fence)}", 1, "fence sha")
    connect = replace(connect, CONNECT_STEP5_LABEL_OLD, CONNECT_STEP5_LABEL_NEW, 1, "step 5 label")
    connect = replace(connect, CONNECT_INPUTS_STOP, CONNECT_INPUTS_STOP + CONNECT_STAGE, 1, "stage P0's records")
    connect = replace(connect, 'echo "FENCE: clear"\n', 'echo "FENCE: clear"\n' + CONNECT_IRIS, 1, "iris read")
    connect = replace(connect, "tools/p0_checks.py", "tools/d2s0_checks.py", 6, "checks name")
    connect = replace(connect, "tools/p0_expected.json", "tools/d2s0_expected.json", 5, "expected name")
    connect = replace(connect, "flux3-inputs.txt", "inputs-check.txt", 2, "inputs record name")
    connect = replace(connect, "stat-p0.txt", "stat-d2s0.txt", 2, "stat record name")
    connect = replace(connect, "rpd_p0_runner.sh", "rpd_d2s0_runner.sh", 3, "runner name")
    connect = replace(connect, "rpd-p0-connect", "rpd-d2s0-connect", 1, "connect label")
    connect = replace(connect, "p0.rc", "chain.rc", 4, "terminal record name")
    connect = replace(connect, P0_ROOT, ROOT, 51, "root")
    connect = connect.replace(STAGE_MARK, P0_ROOT)  # the stage sources are P0's root, written after the root move
    for gone in ("rpd_p0", "rpd-p0", "p0_checks", "p0_expected", "p0.rc", "squeue", "sbatch"):
        assert gone not in connect, gone
    assert connect.count(P0_ROOT) == 1, "P0's root appears only as the stage source (one loop over both records)"
    python_calls = [line for line in connect.splitlines() if '"$PY"' in line or '"$MAT_PYTHON"' in line]
    assert python_calls and all(" -B " in line for line in python_calls), python_calls
    runner = runner_of(connect)  # the runner as finally written, after the connect-wide renames
    assert "chain.rc" in runner and ROOT in runner and P0_ROOT not in runner

    # 4. The fetch.
    fetch = old["fetch"].decode()
    fetch = replace(fetch, FETCH_TITLE_OLD, FETCH_TITLE_NEW, 1, "fetch title")
    fetch = replace(fetch, "flux3-inputs.txt", "inputs-check.txt", 2, "fetch inputs record name")
    fetch = replace(fetch, "stat-p0.txt", "stat-d2s0.txt", 2, "fetch stat record name")
    fetch = replace(fetch, "rpd_p0_runner.sh", "rpd_d2s0_runner.sh", 5, "fetch runner name")
    fetch = replace(fetch, "rpd-p0-fetch", "rpd-d2s0-fetch", 1, "fetch label")
    fetch = replace(fetch, "p0.rc", "chain.rc", 26, "fetch terminal record name")
    fetch = replace(fetch, P0_ROOT, ROOT, 3, "fetch root")
    for gone in ("rpd_p0", "rpd-p0", "p0.rc", "squeue", "python"):
        assert gone not in fetch, gone

    # 5. The launcher.
    launch = old["launch"].decode()
    launch = replace(launch, LAUNCH_HEADER_OLD, LAUNCH_HEADER_NEW, 1, "launch header")
    launch = replace(launch, "(P0, detached on the node)", "(d2-predict + step0, detached on the node)", 1, "usage")
    launch = replace(launch, "rpd_p0_launch.sh", "rpd_d2s0_launch.sh", 4, "launch self name")
    launch = replace(launch, "rpd_p0_connect.sh", "rpd_d2s0_connect.sh", 1, "launch connect name")
    launch = replace(launch, "rpd_p0_fetch.sh", "rpd_d2s0_fetch.sh", 1, "launch fetch name")
    launch = replace(launch, SHA["connect"], sha(connect.encode()), 1, "launch connect sha")
    launch = replace(launch, SHA["fetch"], sha(fetch.encode()), 1, "launch fetch sha")
    launch = replace(launch, "not used for rpd_p0", "not used for rpd_d2s0", 2, "launch fence wording")
    launch = replace(launch, "/dev/shm/rpd-p0-$MODE", "/dev/shm/rpd-d2s0-$MODE", 1, "launch staging")
    launch = replace(launch, P0_ROOT, ROOT, 1, "launch root")
    for gone in ("rpd_p0", "rpd-p0", "squeue"):
        assert gone not in launch, gone

    outputs = {
        "production-config.ready.json": old["config"],
        "tools/d2s0_expected.json": expected,
        "tools/fence_overlap.py": fence,
        "tools/p0_supervise.py": supervise,
        "rpd_d2s0_connect.sh": connect.encode(),
        "rpd_d2s0_fetch.sh": fetch.encode(),
        "rpd_d2s0_launch.sh": launch.encode(),
    }
    for name, data in outputs.items():
        (OUT / name).write_bytes(data)
        print(sha(data), name)
    print(sha(checks), "tools/d2s0_checks.py")
    print(sha(runner.encode()), "(runner, written by the connect)")
    return 0


STAGE_MARK = "@@P0_ROOT@@"
CONNECT_HEADER = """#!/bin/bash
# RPD-RECO d2-predict and step0 (rpd_d2s0): the login-node connect, generated from P0's bound connect (6a1bed95) by
# tools/gen_d2s0.py. Login-only at 0 node-h, with no job. It runs only on the director's go for its exact sha256. In
# order, on one login node:
#   1. refuses unless on a login node with the literal root absent;
#   2. the sacct fence (P0's block, flux3's tightened one, byte for byte); then a read-only iris balance read, recorded
#      in this output only and never a gate;
#   3. a fresh clone at the bound sha into the root, HEAD and porcelain checked, and the 14 pinned sha256s;
#   4. the READY config (P0's, unchanged), written from this script and checked against its sha256;
#   5. the in-place inputs, read with O_NOATIME and checked against the committed records (tools/d2s0_checks.py
#      inputs): flux3's extract, custody record and 12 factor products, and P0's run/pins.json and run/p0.json. Then
#      P0's two records are staged byte for byte into the new run directory (tools/d2s0_checks.py stage: O_NOATIME
#      read, sha256 checked, created exclusively, re-read), so the bound CLI sees the pins -> p0 chain;
#   6. a fresh stat (never an open) of the three gen2thin flux files and the 24 dumps against S1 (stat-d2s0.txt);
#   7. the overlap fence (tools/fence_overlap.py, write roots the new root and /dev/shm/limres-rpd-flux1);
#   8. the clone copied to /dev/shm/limres-rpd-flux1/repo, HEAD, porcelain and pins rechecked, the config beside it;
#   9. the runner started detached and handed /dev/shm over, exactly as P0's connect does (P0's handoff: started=1,
#      then handoff.ok; a STOP or signal before that stops the runner's group and removes /dev/shm, checked).
# The runner (rpd_d2s0_runner.sh) runs d2-predict, then step0, in the new run directory. Neither can run dry
# (fd_rpd_reco.py DRY_RUN_SCOPE, :3058-3062), so each runs once, under tools/p0_supervise.py, with its own monotonic
# deadline (7200 s) and a STOP over 8000000000 B peak RSS. No --prediction is passed, so no measured key can be read.
# The fetch reports RUNNING, DONE or STOP. Every Python call has -B. Writes only under the root and
# /dev/shm/limres-rpd-flux1. Nothing is written to CFS. TMPDIR is the root from step 3 on. umask 077. No set -u.
# Launched from a /dev/shm copy of itself ($1), which it deletes.
"""
RUNNER_HEADER = """#!/bin/bash
# rpd_d2s0 runner, written by rpd_d2s0_connect.sh and started detached on the login node (setsid, nohup, nice 19), as
# P0's runner is. After the connect's handoff (handoff.ok, within 60 s, or it cleans up and stops), it runs d2-predict
# and then step0 in the run directory the connect prepared (with P0's pins.json and p0.json in it), with the config's
# expected interpreter and threads 1. Neither step can run dry (fd_rpd_reco.py DRY_RUN_SCOPE).
# Each step runs under tools/p0_supervise.py (the worker in its own session and group, the supervisor outside it) with
# its own monotonic deadline, 7200 s from the step's start (TERM to the group 30 s before it, KILL at it), checked
# again after the last step. A STOP follows a deadline (rc 7), an outside kill, a nonzero rc, a leftover, a surviving
# group, an unreadable RSS or one over the cap (rc 4), before the next step starts. If the supervisor leaves no
# record, the step's group, from sup-<step>.json.pgid, is killed and awaited before cleanup. A TERM or INT to the
# runner is forwarded as TERM to the supervisor (or, before its pid is recorded, to $!).
# On every exit it can catch, it kills a live step group and waits for it; it removes /dev/shm/limres-rpd-flux1 and
# checks that it is gone (rc 6 if a clean run cannot remove it), unless the group survived, when it keeps it; and it
# publishes chain.rc (rc, cause and a checked UTC time), last. HUP is ignored. An uncatchable kill writes no
# chain.rc; the fetch then reports the runner gone. runner.pid holds the pid, host, /proc start time and UTC time.
"""
RUNNER_DEADLINE_OLD = """DEADLINE=$("$PY" -I -B -c "import time; print(repr(time.monotonic() + $WALL))") || { cause=deadline; fin 9; }
echo "deadline (monotonic) $DEADLINE, $WALL s from now"
"""
RUNNER_DEADLINE_NEW = """# Each step sets its own deadline, $WALL s from its start (step(), below).
"""
RUNNER_STEP_HEAD_OLD = """step() {  # step LABEL RUNDIR [--dry-run]: LABEL is pins, p0, pins-dry or p0-dry
  local label=$1 dir=$2
  shift 2
"""
RUNNER_STEP_HEAD_NEW = """step() {  # step LABEL RUNDIR: LABEL is the bound CLI's step name, d2-predict or step0
  local label=$1 dir=$2
  shift 2
  DEADLINE=$("$PY" -I -B -c "import time; print(repr(time.monotonic() + $WALL))") || { cause=deadline; fin 9; }
  echo "deadline for $label (monotonic) $DEADLINE, $WALL s from now"
"""
RUNNER_STEPS_OLD = """mkdir -m 700 "$R/dry" "$R/run" || { cause=mkdir; fin 9; }
step pins-dry "$R/dry" --dry-run
step p0-dry "$R/dry" --dry-run
step pins "$R/run"
step p0 "$R/run"
"""
RUNNER_STEPS_NEW = """[ -f "$R/run/pins.json" ] && [ -f "$R/run/p0.json" ] || { echo "STOP: P0's records are not in $R/run"; cause=predecessors; fin 9; }
step d2-predict "$R/run"
step step0 "$R/run"
"""
CONNECT_STEP5_LABEL_OLD = """echo "== 5. P0's in-place inputs (flux3's records and factor products, O_NOATIME)"
"""
CONNECT_STEP5_LABEL_NEW = """echo "== 5. the in-place inputs (flux3's records and products, P0's two records, O_NOATIME); P0's records staged"
"""
CONNECT_INPUTS_STOP = """[ "$irc" -eq 0 ] || { echo "STOP: an in-place input is missing or differs from the committed records"; finish 3; }
"""
CONNECT_STAGE = f"""mkdir -m 700 /pscratch/sd/j/josephrb/rpd-reco-p0-20261123/run || finish 9
for f in pins.json p0.json; do
  case $f in pins.json) want={SHA["pins_record"]} ;; *) want={SHA["p0_record"]} ;; esac
  nice -n 19 "$PY" -I -B /pscratch/sd/j/josephrb/rpd-reco-p0-20261123/tools/p0_checks.py stage {STAGE_MARK}/run/$f "$want" /pscratch/sd/j/josephrb/rpd-reco-p0-20261123/run/$f
  [ $? -eq 0 ] || {{ echo "STOP: P0's $f could not be staged byte for byte"; finish 3; }}
done
"""
CONNECT_IRIS = """echo "== 2b. iris (read-only balance; recorded here only, not a gate)"
timeout 120 iris < /dev/null 2>&1 | sed 's/^/iris: /'
echo "iris rc=${PIPESTATUS[0]}"
"""
FETCH_TITLE_OLD = "# RPD-RECO P0 (rpd_p0), the fetch:"
FETCH_TITLE_NEW = "# RPD-RECO d2-predict and step0 (rpd_d2s0, generated from P0's fetch), the fetch:"
LAUNCH_HEADER_OLD = "# RPD-RECO P0 (rpd_p0, generated from the flux3 launcher):"
LAUNCH_HEADER_NEW = "# RPD-RECO d2-predict and step0 (rpd_d2s0, generated from P0's launcher):"


if __name__ == "__main__":
    sys.exit(main())
