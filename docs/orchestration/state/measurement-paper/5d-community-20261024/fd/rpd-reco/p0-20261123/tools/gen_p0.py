"""Generate the P0 READY package (config, connect, runner, fetch, launcher, fence copy) from the flux3 package.

usage: python3 -I -B gen_p0.py REPO
  REPO  a checkout of this repository with S (6896e787, #1251's merge) in its history; pinned files are read at S
        through `git show`, never from the working tree.

P0 is login-only at 0 node-h (FD-RPD-RECO-DECLARATION section 5, binding 1 ruling 3). The director's rulings:
  2026-11-23 (first): 1. a new run root ROOT; the flux extract, custody record and factor products are read in place,
     O_NOATIME, after a sha256 check against committed records; 2. a fresh clone at S with the pinned files checked;
     3. pins --dry-run and p0 --dry-run, then the real pins and p0, in one connect, any failure a STOP; 4. detached, a
     2 h wall cap, peak RSS recorded and a STOP over 8e9 B; 5. S1's retention strings kept and a fresh stat recorded;
  2026-11-23 (ruling (A)): the chain from flux3 on runs on the sacct-only custody 634670b3, so P0 reads flux3's
     records (run-61861637, merged 1fdfe494) and products, whose 12 factor sha256s equal flux2's;
  the accepted P0 findings 1-9: the README states the factor load and its measured RSS (1); one monotonic deadline and
     a supervisor outside the worker's group (2); an explicit startup and cleanup handoff (3); the ack stays in the
     local session record (4); -B on every Python call (5); a terminal p0.rc is authoritative in the fetch, which binds
     the runner's identity to its start time and exact command line (6); the fd_rpd_reco_mutation.py pin (7); the
     tightened sacct fence (8); more tests (9). flux3's package already carries 4, 7 and 8, so P0 inherits them.
Blocks lifted from flux3's connect, fetch and launcher are asserted present there before counted replacements. The
config changes from flux3's at exactly flux_extract/sha256 and flux_custody/sha256.
"""

from __future__ import annotations

import base64
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
FLUX3 = OUT.parent / "flux3-20261123"
RUN3 = FLUX3 / "run-61861637"
S1_LOG = OUT.parent / "flux2-20261122" / "s1" / "survey.log.txt"
ROOT = "/pscratch/sd/j/josephrb/rpd-reco-p0-20261123"
OLD_ROOT = "/pscratch/sd/j/josephrb/rpd-reco-flux3-20261123"
S = "6896e7871421469ce72c6b93188d2d1a55c82ec6"
SHM = "/dev/shm/limres-rpd-flux1"
SHA = {
    "config": "d797183bb5d459285224e4ee4d3fc8a0cc6cd64b136745ebf182bd716800e229",
    "connect": "0a50f7db15df9bb31fe574c588a43c7f455609bb5f34e0e5acadd66aa062fbb4",
    "fetch": "40645b69f02ee67db830fc9f95e3c69bf79cf46a9db4fbada26ce9da7ccf0f2e",
    "launch": "91ae3a6a35c97040cfc444b4b91b29e63682ae80bd9221f1a2e71e85470459f6",
    "fence": "f6541713e2cd4c8b342da5b76f59eec0662555e1cbe97da9ad95a52995594b35",
    "extract": "90445ece147213fae5ffa08ed93d91f3e781e6983991a352241c2585b478a659",
    "custody": "226c7a68d4be002f17a0500c5452ca4521550cc0cfd725788bb16ebe59dcd266",
    "survey_log": "79a63325c0906444893ed91c2a2ca6d78d7246ee439f58d0f4cec55fb4f865e5",
    "custody_module": "634670b33af6900eb9feb2c01748b0f107950e110382780db37b874ab77160d8",
    "reco_module": "7302cc1df71758cfae6bdcfba031d37cc78902beaf454b29e12f3e053d44f141",
}
DIGEST = "75c2a1f4435494bf0e2c5bf4d27631781e65bd738c889c667183778e254792e8"
WALL_SECONDS = 7200
RSS_CAP = 8_000_000_000


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def dump(config: dict) -> bytes:
    return (json.dumps(config, indent=1, sort_keys=True, ensure_ascii=True) + "\n").encode()


def lift(text: str, start: str, end: str, starts: int = 1) -> str:
    """The exact block of TEXT from the first line starting START (which must start exactly STARTS lines) through the
    first line after it that starts with END."""
    lines = text.splitlines(keepends=True)
    first = [i for i, line in enumerate(lines) if line.startswith(start)]
    assert len(first) == starts, (start, first)
    last = [i for i, line in enumerate(lines) if i >= first[0] and line.startswith(end)]
    assert last, (start, end)
    return "".join(lines[first[0] : last[0] + 1])


def replace(text: str, old: str, new: str, count: int, what: str) -> str:
    found = text.count(old)
    assert found == count, f"{what}: {found} occurrences of {old[:60]!r}, expected {count}"
    return text.replace(old, new)


def git_show(repo: Path, path: str) -> bytes:
    return subprocess.run(["git", "-C", str(repo), "show", f"{S}:{path}"], check=True, capture_output=True).stdout


def leaves(value: object, path: str = "") -> dict[str, object]:
    if isinstance(value, dict):
        out: dict[str, object] = {}
        for key, item in value.items():
            out.update(leaves(item, f"{path}/{key}"))
        return out
    if isinstance(value, list):
        out = {}
        for index, item in enumerate(value):
            out.update(leaves(item, f"{path}/{index}"))
        return out
    return {path: value}


def b64(data: bytes) -> str:
    return base64.b64encode(data).decode()


def main() -> int:
    repo = Path(sys.argv[1])
    old = {
        "config": (FLUX3 / "production-config.ready.json").read_bytes(),
        "connect": (FLUX3 / "rpd_flux3_connect.sh").read_bytes(),
        "fetch": (FLUX3 / "rpd_flux3_fetch.sh").read_bytes(),
        "launch": (FLUX3 / "rpd_flux3_launch.sh").read_bytes(),
        "fence": (FLUX3 / "tools" / "fence_overlap.py").read_bytes(),
    }
    for key, data in old.items():
        assert sha(data) == SHA[key], key
    extract = (RUN3 / "records/run/flux-extract.json").read_bytes()
    custody = (RUN3 / "records/run/flux-custody.json").read_bytes()
    assert sha(extract) == SHA["extract"] and sha(custody) == SHA["custody"]
    receipt = json.loads(custody)
    assert receipt["status"] == "PASS" and receipt["custody_code_sha256"] == SHA["custody_module"]
    assert receipt["code_sha256"] == SHA["reco_module"] and receipt["extract_sha256"] == SHA["extract"]
    survey = S1_LOG.read_bytes()
    assert sha(survey) == SHA["survey_log"]

    # 1. The config: flux3's, with the two record digests filled.
    config = json.loads(old["config"])
    assert dump(config) == old["config"], "the JSON format does not reproduce d797183b"
    new = json.loads(old["config"])
    assert new["flux_extract"]["sha256"] is None and new["flux_custody"]["sha256"] is None
    assert new["flux_extract"]["path"] == f"{OLD_ROOT}/run/flux-extract.json"
    assert new["flux_custody"]["path"] == f"{OLD_ROOT}/run/flux-custody.json"
    new["flux_extract"]["sha256"] = SHA["extract"]
    new["flux_custody"]["sha256"] = SHA["custody"]
    a, b = leaves(config), leaves(new)
    assert set(a) == set(b) and {k for k in a if a[k] != b[k]} == {"/flux_extract/sha256", "/flux_custody/sha256"}
    cfg = dump(new)
    module = git_show(repo, "nd-unfolding/fd_rpd_reco.py")
    assert sha(module) == SHA["reco_module"]
    with tempfile.TemporaryDirectory(prefix="gen-p0-") as temporary:
        bound = Path(temporary) / "fd_rpd_reco.py"
        bound.write_bytes(module)
        spec = importlib.util.spec_from_file_location("fd_rpd_reco_at_S", bound)
        assert spec is not None and spec.loader is not None
        reco = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = reco
        spec.loader.exec_module(reco)
    assert reco.flux_selection_digest(config) == reco.flux_selection_digest(new) == DIGEST
    assert json.loads(extract)["selection_sha256"] == DIGEST

    # 2. The expected inputs (flux3's records and products, in place) and S1's stat table.
    inputs = {new["flux_extract"]["path"]: SHA["extract"], new["flux_custody"]["path"]: SHA["custody"]}
    for playlist, product in sorted(json.loads(extract)["factor_products"].items()):
        assert product["path"] == f"{OLD_ROOT}/run/flux-factors-{playlist}.npz", product["path"]
        inputs[product["path"]] = product["sha256"]
    assert len(inputs) == 14
    stat = {}
    for line in survey.decode().splitlines():
        fields = line.split("|")
        if len(fields) == 5 and fields[1].isdigit():
            path = fields[0]
            if "/dumps/lat_" in path or "flux-gen2thin-pdg14-" in path:
                stat[path] = {"bytes": int(fields[1]), "inode": int(fields[4])}
    assert len(stat) == 27 and sum("/dumps/" in p for p in stat) == 24, len(stat)
    for group in ("1D", "1M", "1N"):
        selected = new["flux_selection"][group]["relative_path"]
        assert any(p.endswith(selected) for p in stat), group
    expected = dump({"inputs": inputs, "stat": stat})
    checks = (HERE / "p0_checks.py").read_bytes()
    supervise = (HERE / "p0_supervise.py").read_bytes()

    # 3. The pins: flux3's 14 (custody 634670b3 and fd_rpd_reco_mutation.py among them), each checked equal at S.
    connect_old = old["connect"].decode()
    pin_block = lift(connect_old, SHA["reco_module"], "f2612369", starts=2)
    rows = pin_block.splitlines()
    assert len(rows) == 14, len(rows)
    for row in rows:
        want, path = row.split(" ", 1)
        got = sha(git_show(repo, path))
        assert got == want, f"{path} at S is {got}, the flux3 pin is {want}"
    assert f"{SHA['custody_module']} nd-unfolding/fd_rpd_reco_custody.py" in rows
    assert any(r.endswith(" nd-unfolding/tests/fd_rpd_reco_mutation.py") for r in rows)
    assert connect_old.count(pin_block) == 2

    # 4. The fence copy: only its write root changes.
    fence = replace(
        old["fence"].decode(), f'WRITE_ROOTS = ("{OLD_ROOT}",', f'WRITE_ROOTS = ("{ROOT}",', 1, "fence root"
    ).encode()

    # 5. The connect.
    def rooted(block: str, count: int, what: str) -> str:
        return replace(block, OLD_ROOT, ROOT, count, what)

    host_and_root = rooted(lift(connect_old, 'case "$(hostname)" in login*)', "[ ! -e /pscratch"), 2, "root guard")
    sacct = lift(connect_old, 'echo "== 2. the fence', 'echo "FENCE: clear"')
    assert "tolower($2) ~ /^(cov2d|t2a|rpd)/" in sacct and '$2 == ""' in sacct, "flux3's tightened fence"
    clone = rooted(lift(connect_old, "mkdir -m 700 /pscratch", "done <<'PINS'"), 7, "clone")
    clone = replace(
        clone,
        f"mkdir -m 700 {ROOT} || finish 9\n",
        f"mkdir -m 700 {ROOT} || finish 9\nTMPDIR={ROOT}; export TMPDIR  # bash spools heredocs here, inside the root\n",
        1,
        "clone TMPDIR",
    )
    job_copy = lift(connect_old, f"[ ! -e {SHM} ] ||", "done <<'PINS'")
    job_copy = rooted(job_copy, 1, "shm copy")
    job_copy = replace(job_copy, "fin 9", "finish 9", 2, "shm copy fin 9")
    job_copy = replace(job_copy, "fin 5", "finish 5", 4, "shm copy fin 5")
    job_copy = replace(job_copy, f'[ "$head" = "{S}" ]', '[ "$head" = "$S" ]', 1, "shm copy head")
    job_copy = replace(job_copy, "made=1\n", "made=1\n", 1, "shm copy made")
    config_block = lift(connect_old, 'echo "== 4. the READY config"', '[ "$got" = "$CFG_SHA" ]')
    config_block = rooted(config_block, 2, "config block")
    config_block = replace(
        config_block,
        f"printf '%s' '{b64(old['config'])}' | base64 -d > {ROOT}/production-config.ready.json",
        f"printf '%s' '{b64(cfg)}' | base64 -d > {ROOT}/production-config.ready.json",
        1,
        "config blob",
    )
    overlap = lift(connect_old, 'echo "== 5. the overlap fence"', '[ "$frc" -eq 0 ]')
    overlap = rooted(overlap, 8, "overlap block")
    overlap = replace(
        overlap,
        f"printf '%s' '{b64(old['fence'])}' | base64 -d > {ROOT}/tools/fence_overlap.py",
        f"printf '%s' '{b64(fence)}' | base64 -d > {ROOT}/tools/fence_overlap.py",
        1,
        "fence blob",
    )
    overlap = replace(overlap, '"$MAT_PYTHON" -I ', '"$MAT_PYTHON" -I -B ', 1, "overlap -B")
    overlap = replace(overlap, "nothing is submitted", "nothing is started", 1, "overlap wording")
    overlap = replace(overlap, f"mkdir {ROOT}/tools || finish 9\n", "", 1, "overlap tools dir (made at step 5)")
    overlap = replace(overlap, 'echo "== 5. the overlap fence"', 'echo "== 7. the overlap fence"', 1, "overlap label")
    interpreter = new["expected_environment"]["interpreter"]
    runner = RUNNER.format(root=ROOT, shm=SHM, py=interpreter, cfg_sha=sha(cfg), wall=WALL_SECONDS, rss_cap=RSS_CAP)
    connect = CONNECT.format(
        root=ROOT,
        shm=SHM,
        s=S,
        cfg_sha=sha(cfg),
        fence_sha=sha(fence),
        checks_sha=sha(checks),
        expected_sha=sha(expected),
        supervise_sha=sha(supervise),
        py=interpreter,
        host_and_root=host_and_root,
        sacct=sacct,
        clone=clone,
        pins=pin_block,
        config_block=config_block,
        checks_b64=b64(checks),
        expected_b64=b64(expected),
        supervise_b64=b64(supervise),
        overlap=overlap,
        job_copy=job_copy,
        runner=runner,
        wall=WALL_SECONDS,
        rss_cap=RSS_CAP,
    )
    assert "squeue" not in connect and "sbatch" not in connect, "connect"
    assert OLD_ROOT not in connect.replace(f"{OLD_ROOT}/run/", ""), "connect: the flux3 root outside its run/ inputs"
    python_calls = [line for line in connect.splitlines() if '"$PY"' in line or '"$MAT_PYTHON"' in line]
    assert python_calls and all(" -B " in line for line in python_calls), python_calls

    # 6. The fetch.
    fetch_old = old["fetch"].decode()
    tar_block = lift(fetch_old, 'echo "== TAR BEGIN"', '[ "$trc" -eq 0 ] && [ "$brc" -eq 0 ]')
    fetch = FETCH.format(root=ROOT, shm=SHM, tar_block=tar_block)
    assert "squeue" not in fetch and "python" not in fetch

    # 7. The launcher: flux3's (its ack.txt guard included), renamed and re-pinned.
    launch = old["launch"].decode()
    assert launch.count("bad_ack()") == 1 and "ACK-UTC" in launch, "flux3's ack guard"
    launch = replace(launch, LAUNCH_HEADER_OLD, LAUNCH_HEADER_NEW, 1, "launch header")
    launch = replace(launch, LAUNCH_USAGE_CONNECT_OLD, LAUNCH_USAGE_CONNECT_NEW, 1, "launch usage connect")
    launch = replace(launch, "rpd_flux3_launch.sh", "rpd_p0_launch.sh", 4, "launch self name")
    launch = replace(launch, "rpd_flux3_connect.sh", "rpd_p0_connect.sh", 1, "launch connect name")
    launch = replace(launch, "rpd_flux3_fetch.sh", "rpd_p0_fetch.sh", 1, "launch fetch name")
    launch = replace(launch, SHA["connect"], sha(connect.encode()), 1, "launch connect sha")
    launch = replace(launch, SHA["fetch"], sha(fetch.encode()), 1, "launch fetch sha")
    launch = replace(launch, OLD_ROOT, ROOT, 1, "launch root")
    launch = replace(launch, "not used for rpd_flux3", "not used for rpd_p0", 2, "launch fence wording")
    launch = replace(launch, "/dev/shm/rpd-flux3-$MODE", "/dev/shm/rpd-p0-$MODE", 1, "launch staging")
    launch = replace(launch, "(any login node; exit 10 if unfinished)", LAUNCH_USAGE_FETCH_NEW, 1, "launch usage fetch")
    assert "flux3" not in launch.replace(LAUNCH_HEADER_NEW, "") and "squeue" not in launch, "launch"

    outputs = {
        "production-config.ready.json": cfg,
        "tools/p0_expected.json": expected,
        "tools/fence_overlap.py": fence,
        "rpd_p0_connect.sh": connect.encode(),
        "rpd_p0_fetch.sh": fetch.encode(),
        "rpd_p0_launch.sh": launch.encode(),
    }
    for name, data in outputs.items():
        (OUT / name).write_bytes(data)
        print(sha(data), name)
    print(sha(checks), "tools/p0_checks.py")
    print(sha(supervise), "tools/p0_supervise.py")
    print(sha(runner.encode()), "(runner, written by the connect)")
    print("flux_selection_digest", DIGEST, "(unchanged by the two digests)")
    return 0


CONNECT = """#!/bin/bash
# RPD-RECO P0 (rpd_p0): the login-node connect. P0 is login-only at 0 node-h, with no job (FD-RPD-RECO-DECLARATION
# section 5, BINDING-1 ruling 3). It reads flux3's records and products (run-61861637) in place. It runs only on the
# director's go for its exact sha256. In order, on one login node:
#   1. refuses unless on a login node with the literal root {root} absent;
#   2. the sacct fence (any unended cov2d*, t2a* or rpd* job refuses; flux3's tightened block, byte for byte);
#   3. a fresh clone at {s} into the root, HEAD and porcelain checked, and the 14 pinned sha256s;
#   4. the P0 READY config, written from this script and checked against its sha256;
#   5. P0's in-place inputs: flux3's extract, custody record and 12 factor products, read with O_NOATIME and checked
#      against the committed run-61861637 records (tools/p0_checks.py inputs);
#   6. a fresh stat (never an open) of the three gen2thin flux files and the 24 dumps, compared with S1's bytes and
#      inodes, with the earliest purge exposure printed (tools/p0_checks.py stat, recorded in stat-p0.txt);
#   7. the overlap fence (tools/fence_overlap.py, write roots {root} and {shm});
#   8. the clone copied to {shm}/repo (the path the config binds), HEAD, porcelain and pins rechecked, the config
#      copied beside it;
#   9. the runner started detached (setsid, nohup, nice 19, with SIGINT reset to its default so the runner can trap
#      it). The connect waits up to 30 s for runner.pid, checks that it names the started process and that it is
#      alive, then gives up ownership (started=1) and only then writes handoff.ok. The runner starts no step without
#      handoff.ok and cleans up itself if it is not there within 60 s, so a connect stopped in between leaves no gap.
# Until started=1, the connect owns {shm}: on any STOP or signal (TERM, INT, HUP) it stops a started runner, as a group
# and as a process (TERM, then KILL after 5 s), reaps it and removes {shm}, checked. Before the handoff the runner has
# started no supervisor or worker. TMPDIR is the root from step 3 on, so bash's heredoc spools stay inside it. The runner (rpd_p0_runner.sh) runs pins --dry-run and
# p0 --dry-run into {root}/dry, then pins and p0 into {root}/run, each under tools/p0_supervise.py with one monotonic
# deadline ({wall} s for the whole chain) and a STOP over {rss_cap} B peak RSS. The fetch reports RUNNING, DONE or STOP.
# Every Python call has -B. Writes only under the root and {shm}. Nothing is written to CFS. umask 077. No set -u.
# Launched from a /dev/shm copy of itself ($1), which it deletes.
umask 077
SELF=$1
S={s}
CFG_SHA={cfg_sha}
FENCE_SHA={fence_sha}
CHECKS_SHA={checks_sha}
EXPECTED_SHA={expected_sha}
SUPERVISE_SHA={supervise_sha}
MAT_PYTHON=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
PY={py}
made=0
started=0
spid=
launching=0
finish() {{
  trap '' TERM INT HUP
  local p=$spid
  [ -z "$p" ] && [ "$launching" -eq 1 ] && p=$!
  if [ -n "$p" ] && [ "$started" -eq 0 ]; then
    kill -TERM -- -"$p" 2>/dev/null; kill -TERM "$p" 2>/dev/null
    for _ in $(seq 1 25); do ps -o stat= -p "$p" 2>/dev/null | grep -qv Z || break; sleep 0.2; done
    kill -KILL -- -"$p" 2>/dev/null; kill -KILL "$p" 2>/dev/null
    wait "$p" 2>/dev/null
    echo "stopped the runner $p before the handoff"
  fi
  if [ "$made" -eq 1 ] && [ "$started" -eq 0 ]; then
    rm -rf -- {shm}
    if [ -e {shm} ]; then echo "STOP: {shm} could not be removed"; else echo "removed {shm}"; fi
  fi
  echo "== rpd-p0-connect rc=$1 $(date -u +%FT%TZ)"; rm -f -- "$SELF"; exit "$1"
}}
trap 'echo "STOP: the connect got SIGTERM"; finish 8' TERM
trap 'echo "STOP: the connect got SIGINT"; finish 8' INT
trap 'echo "STOP: the connect got SIGHUP"; finish 8' HUP
{host_and_root}echo "node $(hostname) $(date -u +%FT%TZ); connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
{sacct}{clone}{pins}PINS
{config_block}echo "== 5. P0's in-place inputs (flux3's records and factor products, O_NOATIME)"
mkdir {root}/tools || finish 9
printf '%s' '{checks_b64}' | base64 -d > {root}/tools/p0_checks.py
printf '%s' '{expected_b64}' | base64 -d > {root}/tools/p0_expected.json
printf '%s' '{supervise_b64}' | base64 -d > {root}/tools/p0_supervise.py
got=$(sha256sum {root}/tools/p0_checks.py | cut -d' ' -f1)
echo "sha256 $got (expected $CHECKS_SHA) tools/p0_checks.py"
[ "$got" = "$CHECKS_SHA" ] || {{ echo "STOP: checks tool digest"; finish 5; }}
got=$(sha256sum {root}/tools/p0_expected.json | cut -d' ' -f1)
echo "sha256 $got (expected $EXPECTED_SHA) tools/p0_expected.json"
[ "$got" = "$EXPECTED_SHA" ] || {{ echo "STOP: expected-values digest"; finish 5; }}
got=$(sha256sum {root}/tools/p0_supervise.py | cut -d' ' -f1)
echo "sha256 $got (expected $SUPERVISE_SHA) tools/p0_supervise.py"
[ "$got" = "$SUPERVISE_SHA" ] || {{ echo "STOP: supervisor digest"; finish 5; }}
nice -n 19 "$PY" -I -B {root}/tools/p0_checks.py inputs {root}/tools/p0_expected.json > {root}/flux3-inputs.txt 2>&1
irc=$?
cat {root}/flux3-inputs.txt; echo "inputs check rc=$irc"
[ "$irc" -eq 0 ] || {{ echo "STOP: an in-place input is missing or differs from the committed records"; finish 3; }}
echo "== 6. a fresh stat of the gen2thin flux files and the dumps (against S1)"
nice -n 19 "$PY" -I -B {root}/tools/p0_checks.py stat {root}/tools/p0_expected.json > {root}/stat-p0.txt 2>&1
src=$?
cat {root}/stat-p0.txt; echo "stat check rc=$src"
[ "$src" -eq 0 ] || {{ echo "STOP: a file is missing, or its bytes or inode differ from S1's"; finish 3; }}
{overlap}echo "== 8. the clone to {shm}/repo"
{job_copy}{pins}PINS
cp {root}/production-config.ready.json {shm}/production-config.ready.json || finish 5
got=$(sha256sum {shm}/production-config.ready.json | cut -d' ' -f1)
echo "config sha256 $got"
[ "$got" = "$CFG_SHA" ] || {{ echo "STOP: config digest"; finish 5; }}
echo "== 9. the runner"
cat > {root}/rpd_p0_runner.sh <<'RUNNER'
{runner}RUNNER
echo "runner script sha256 $(sha256sum {root}/rpd_p0_runner.sh | cut -d' ' -f1)"
launching=1
setsid nohup nice -n 19 "$PY" -I -B -c 'import os, signal, sys; signal.signal(signal.SIGINT, signal.SIG_DFL); os.execvp("bash", ["bash", sys.argv[1]])' {root}/rpd_p0_runner.sh > {root}/runner.out 2>&1 < /dev/null &
spid=$!
for _ in $(seq 1 150); do [ -s {root}/runner.pid ] && break; sleep 0.2; done
[ -s {root}/runner.pid ] || {{ echo "STOP: the runner wrote no pid within 30 s"; finish 8; }}
read -r rpid rhost rticks rstart < {root}/runner.pid
[ "$rpid" = "$spid" ] || {{ echo "STOP: runner.pid names $rpid, not the started process $spid"; finish 8; }}
kill -0 "$rpid" 2>/dev/null || {{ echo "STOP: runner pid $rpid is not alive"; finish 8; }}
# From here the runner owns {shm}: if handoff.ok is not written (a failure, or a signal to the connect now), the
# runner finds no handoff within 60 s and removes the tree itself.
started=1
echo "$rpid $(date -u +%FT%TZ)" > {root}/handoff.ok.partial && mv -- {root}/handoff.ok.partial {root}/handoff.ok || {{ echo "STOP: handoff.ok could not be written; the runner cleans up"; finish 8; }}
echo "runner pid $rpid on $rhost since $rstart (start ticks $rticks); {shm} handed over; the fetch reports it"
finish 0
"""

RUNNER = """#!/bin/bash
# rpd_p0 runner, written by rpd_p0_connect.sh and started detached on the login node (setsid, nohup, nice 19). After
# the connect's handoff (handoff.ok, within 60 s, or it cleans up and stops), it runs pins --dry-run and p0 --dry-run
# into {root}/dry, then pins and p0 into {root}/run, with the config's expected interpreter and threads 1.
# Each step runs under tools/p0_supervise.py: the worker in its own session and group, the supervisor outside it, and
# one monotonic deadline, {wall} s after the handoff, for the whole chain (TERM to the group 30 s before it, KILL at
# it), checked again before each step and after the last. The supervisor's record (sup-<step>.json) gives the worker's
# rc, the ending signal, whether a deadline signal was delivered or the worker outlived the deadline, whether a group
# member was left over and whether the group is gone, and the peak RSS. A STOP follows a deadline (rc 7), an outside
# kill, a nonzero rc, a leftover, a surviving group, an unreadable RSS or one over {rss_cap} B (rc 4), before the next
# step starts. If the supervisor leaves no record (killed itself), the step's group, from sup-<step>.json.pgid, is
# killed and awaited before cleanup. A TERM or INT to the runner is forwarded as TERM to the supervisor (or, in the
# instant before its pid is recorded, to $!), which forwards it to the step's group and reaps it.
# On every exit it can catch, it kills a live step group and waits for it; it removes {shm} and checks that it is gone
# (rc 6 if a clean run cannot remove it), unless the group survived, when it keeps {shm}; and it publishes p0.rc (rc,
# cause and a checked UTC time), last; a failed publication is reported (rc 6 if clean). HUP is ignored. An uncatchable kill writes no p0.rc; the fetch then reports the
# runner gone and the /dev/shm cleanup unverified. runner.pid holds the pid, host, /proc start time and UTC time.
umask 077
R={root}
PY={py}
REPO={shm}/repo
CFG={shm}/production-config.ready.json
CFG_SHA={cfg_sha}
SUP={root}/tools/p0_supervise.py
WALL={wall}
RSS_CAP={rss_cap}
for k in OMP_NUM_THREADS OPENBLAS_NUM_THREADS MKL_NUM_THREADS NUMEXPR_NUM_THREADS VECLIB_MAXIMUM_THREADS; do export "$k=1"; done
cause=exit
finished=0
sup=
launching=0
cur=
group_alive() {{  # group_alive PGID: true if the group has a member. ESRCH: none. EPERM: a member that cannot be
  # signalled, so alive, except on macOS (Darwin), where EPERM is a zombie-only group (the supervisor's rule). Any
  # other error counts as alive everywhere, so /dev/shm is kept unless the group is confirmed absent.
  local err
  err=$(LC_ALL=C kill -0 -- -"$1" 2>&1) && return 0
  case $err in
    *"No such process"*) return 1 ;;
    *"Operation not permitted"*) [ "$(uname -s)" = Darwin ] && return 1 ;;
  esac
  return 0
}}
fin() {{
  [ "$finished" -eq 1 ] && exit "$1"
  finished=1
  trap '' TERM INT
  local rc=$1 pg survived=0 when
  if [ -n "$cur" ] && pg=$(cat "$cur" 2>/dev/null) && [[ $pg =~ ^[1-9][0-9]+$ ]]; then  # never 0 or 1 (own group, all)
    kill -KILL -- -"$pg" 2>/dev/null && echo "killed the step's group $pg"
    for _ in $(seq 1 50); do group_alive "$pg" || break; sleep 0.2; done
    if group_alive "$pg"; then
      survived=1
      echo "STOP: the step's group $pg survived; {shm} is kept, since a live member may still use it"
      [ "$rc" -eq 0 ] && {{ rc=6; cause=group-survived; }}
    fi
  fi
  if [ "$survived" -eq 0 ]; then
    rm -rf -- {shm}
    if [ -e {shm} ]; then
      echo "STOP: {shm} could not be removed"
      [ "$rc" -eq 0 ] && {{ rc=6; cause=cleanup-failed; }}
    else
      echo "removed {shm}"
    fi
  fi
  if ! {{ when=$(date -u +%FT%TZ) && [[ $when =~ ^[0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}}T[0-9]{{2}}:[0-9]{{2}}:[0-9]{{2}}Z$ ]] \
      && echo "rc=$rc cause=$cause end=$when" > "$R/p0.rc.partial" && mv -- "$R/p0.rc.partial" "$R/p0.rc"; }}; then
    echo "STOP: p0.rc could not be published (rc=$rc cause=$cause)"
    [ "$rc" -eq 0 ] && rc=6
  fi
  exit "$rc"
}}
on_signal() {{  # on_signal NAME RC: forward TERM to the supervisor (it forwards to the step's group and reaps it), stop
  # TERM for both: bash starts the supervisor with SIGINT ignored, so an INT sent before its handler exists is lost,
  # while a TERM then ends it before it has forked a worker. The runner still exits 130 for INT.
  cause=signal-$1
  local p=$sup
  [ -z "$p" ] && [ "$launching" -eq 1 ] && p=$!
  if [ -n "$p" ]; then kill -TERM "$p" 2>/dev/null; wait "$p" 2>/dev/null; fi
  fin "$2"
}}
trap '' HUP
trap 'on_signal TERM 143' TERM
trap 'on_signal INT 130' INT
trap 'r=$?; [ "$finished" -eq 1 ] || {{ cause=exit-trap; fin "$r"; }}' EXIT
st=$(cat /proc/$$/stat) || {{ cause=proc-stat; fin 9; }}
set -f; fields=(${{st##*) }}); set +f  # no here-string: it could spool to a temp file outside the root
echo "$$ $(hostname) ${{fields[19]}} $(date -u +%FT%TZ)" > "$R/runner.pid.partial" && mv -- "$R/runner.pid.partial" "$R/runner.pid"
echo "== rpd_p0 runner $$ on $(hostname) $(date -u +%FT%TZ), nice $(nice)"
[ "$(nice)" = 19 ] || {{ echo "STOP: the runner is not at nice 19"; cause=nice; fin 9; }}
for _ in $(seq 1 300); do [ -e "$R/handoff.ok" ] && break; sleep 0.2; done
[ -e "$R/handoff.ok" ] || {{ echo "STOP: no handoff.ok from the connect within 60 s"; cause=no-handoff; fin 8; }}
echo "handoff.ok: $(cat "$R/handoff.ok")"
DEADLINE=$("$PY" -I -B -c "import time; print(repr(time.monotonic() + $WALL))") || {{ cause=deadline; fin 9; }}
echo "deadline (monotonic) $DEADLINE, $WALL s from now"
past_deadline() {{  # rc 0 if the deadline has passed, 1 if not; a failed probe is its own STOP (rc 4), not a wall cap
  # The probe answers 10 (passed) or 11 (not passed), so a Python failure (rc 1 or 2) cannot pass for either.
  "$PY" -I -B -c "import sys, time; sys.exit(10 if time.monotonic() >= $DEADLINE else 11)"
  case $? in
    10) return 0 ;;
    11) return 1 ;;
    *) echo "STOP: the deadline check failed"; cause=clock-check; fin 4 ;;
  esac
}}
step() {{  # step LABEL RUNDIR [--dry-run]: LABEL is pins, p0, pins-dry or p0-dry
  local label=$1 dir=$2
  shift 2
  past_deadline && {{ echo "STOP: the wall cap was reached before $label"; cause=wall-cap; fin 7; }}
  echo "== $label start $(date -u +%FT%TZ)"
  cur="$R/sup-$label.json.pgid"
  launching=1
  ( cd "$REPO" && exec "$PY" -I -B "$SUP" "$DEADLINE" "$R/sup-$label.json" -- \\
      "$PY" -B nd-unfolding/fd_rpd_reco.py "${{label%%-*}}" --config "$CFG" --config-sha256 "$CFG_SHA" --run "$dir" "$@" ) &
  sup=$!
  launching=0
  wait "$sup"
  local src=$?
  sup=
  local v rc sig dl fw rss left gone
  v=$("$PY" -I -B -c 'import json, sys; d = json.load(open(sys.argv[1])); print(d["rc"], d["signal"] or "-", int(d["deadline_signalled"] or d["past_deadline"]), d["forwarded"] or "-", d["peak_rss_bytes"], int(d["leftover_group_killed"]), int(d["group_gone"]))' "$R/sup-$label.json" 2>/dev/null)
  read -r rc sig dl fw rss left gone <<< "$v"
  echo "$label supervisor_rc=$src rc=${{rc:-unknown}} signal=${{sig:-unknown}} deadline=${{dl:-unknown}} leftover_killed=${{left:-unknown}} group_gone=${{gone:-unknown}} peak_rss_bytes=${{rss:-unknown}} end=$(date -u +%FT%TZ)" | tee -a "$R/runner-steps.txt"
  if [ -z "$v" ] && past_deadline; then
    echo "STOP: $label left no supervisor record and the deadline has passed (supervisor rc $src)"; cause=wall-cap; fin 7
  fi
  [ -n "$v" ] || {{ echo "STOP: $label left no supervisor record (supervisor rc $src); its group is killed before cleanup"; cause=no-record-$label; fin 4; }}
  [ "$dl" = 0 ] || {{ echo "STOP: $label reached the deadline (a deadline signal was delivered, or the worker outlived it)"; cause=wall-cap; fin 7; }}
  [ "$gone" = 1 ] || {{ echo "STOP: $label's group was still alive after the supervisor's KILL"; cause=group-survived-$label; fin 4; }}
  [ "$sig" = - ] || {{ echo "STOP: $label was ended by $sig from outside the supervisor"; cause=killed-$label; fin 4; }}
  [ "$rc" = 0 ] || {{ echo "STOP: $label rc=$rc"; cause=step-$label; fin 4; }}
  [ "$left" = 0 ] || {{ echo "STOP: $label left processes in its group (killed)"; cause=leftover-$label; fin 4; }}
  [[ "$rss" =~ ^[0-9]+$ ]] || {{ echo "STOP: $label peak RSS unreadable"; cause=rss-unread; fin 4; }}
  [ "$rss" -le "$RSS_CAP" ] || {{ echo "STOP: $label peak RSS $rss B exceeds $RSS_CAP B"; cause=rss-cap; fin 4; }}
  [ "$src" -eq 0 ] || {{ echo "STOP: $label supervisor rc=$src"; cause=supervisor-$label; fin 4; }}
  cur=
}}
mkdir -m 700 "$R/dry" "$R/run" || {{ cause=mkdir; fin 9; }}
step pins-dry "$R/dry" --dry-run
step p0-dry "$R/dry" --dry-run
step pins "$R/run"
step p0 "$R/run"
past_deadline && {{ echo "STOP: the chain ended at or after the deadline"; cause=wall-cap; fin 7; }}
echo "== P0 DONE $(date -u +%FT%TZ)"
fin 0
"""

FETCH = """#!/bin/bash
# RPD-RECO P0 (rpd_p0), the fetch: reads what the detached runner left under the literal root {root}, on a login
# node. It writes nothing on the cluster beyond its own /dev/shm copy, which it deletes.
#   - a well-formed p0.rc (no NUL byte, one line "rc=N cause=C end=T", C of [A-Za-z0-9_.-], T a real UTC time) is
#     authoritative,
#     from any login node, with or without runner.pid: DONE if rc 0, otherwise STOP. A malformed p0.rc: exit 9,
#     nothing sent;
#   - no p0.rc, on the runner's node: RUNNING (exit 10, run it again later) only if /proc/<pid> shows the start time
#     recorded in runner.pid and /proc/<pid>/cmdline is byte for byte "bash\\0{root}/rpd_p0_runner.sh\\0", and p0.rc
#     is still absent after the probe. Otherwise p0.rc is read again (the runner may have finished in between) and, if
#     still absent, the runner is gone without p0.rc (an uncatchable kill): exit 11, with the cleanup of {shm} reported
#     as unverified;
#   - no p0.rc and no runner.pid, or no p0.rc on another node: exit 9 (cannot tell).
# When DONE, STOP or gone, it prints the records and sends a base64 tar of them: runner.pid, runner.out,
# runner-steps.txt, p0.rc, handoff.ok, stat-p0.txt, flux3-inputs.txt, fence-overlap.txt, rpd_p0_runner.sh,
# production-config.ready.json, sup-*.json and every *.json directly in dry/ and run/ (the step records and any
# refusal record). The staged copies stay. Exits 0 (DONE), 12 (STOP), 11 (gone), 10 (running), 9 (cannot tell), 14 (the
# tar failed). umask 077. Launched from a /dev/shm copy of itself ($1), which it deletes.
umask 077
SELF=$1
R={root}
finish() {{ echo "== rpd-p0-fetch rc=$1 $(date -u +%FT%TZ)"; rm -f -- "$SELF"; exit "$1"; }}
[ -d "$R" ] || {{ echo "STOP: $R does not exist"; rm -f -- "$SELF"; exit 9; }}
cd "$R" || finish 9
echo "node $(hostname) $(date -u +%FT%TZ); fetch script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
terminal() {{  # sets state from a well-formed p0.rc; returns 1 if there is no p0.rc
  [ -f p0.rc ] || return 1
  LC_ALL=C tr -d '\\000' < p0.rc | cmp -s - p0.rc || {{ echo "CANNOT TELL: p0.rc contains NUL bytes"; finish 9; }}
  local line lines code end
  lines=$(wc -l < p0.rc | tr -d ' ')
  line=$(cat p0.rc)
  echo "p0.rc: $line"
  [ "$lines" = 1 ] && [[ $line =~ ^rc=([0-9]+)\\ cause=[A-Za-z0-9_.-]+\\ end=([0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}}T[0-9]{{2}}:[0-9]{{2}}:[0-9]{{2}}Z)$ ]] || {{ echo "CANNOT TELL: p0.rc is malformed"; finish 9; }}
  code=${{BASH_REMATCH[1]}}
  end=${{BASH_REMATCH[2]}}
  [ "$(date -u -d "$end" +%Y-%m-%dT%H:%M:%SZ 2>/dev/null)" = "$end" ] || {{ echo "CANNOT TELL: p0.rc's end time $end is not a real UTC time"; finish 9; }}
  [ "$code" = 0 ] && state=DONE || state=STOP
  return 0
}}
rpid=
if [ -s runner.pid ]; then
  read -r rpid rhost rticks rstart < runner.pid
  echo "runner pid $rpid host $rhost start ticks $rticks start $rstart"
else
  echo "no runner.pid"
fi
if ! terminal; then
  [ -n "$rpid" ] || {{ echo "CANNOT TELL: no p0.rc and no runner.pid (the connect did not start the runner)"; finish 9; }}
  [ "$(hostname)" = "$rhost" ] || {{ echo "CANNOT TELL: no p0.rc, and the runner ran on $rhost; fetch from $rhost"; finish 9; }}
  alive=0
  if st=$(cat "/proc/$rpid/stat" 2>/dev/null); then
    set -f; fields=(${{st##*) }}); set +f  # no here-string: it could spool to a temp file outside the root
    [ "${{fields[19]}}" = "$rticks" ] && cmp -s "/proc/$rpid/cmdline" <(printf 'bash\\0%s\\0' "$R/rpd_p0_runner.sh") && alive=1
  fi
  if [ "$alive" -eq 1 ] && [ ! -f p0.rc ]; then
    echo "RUNNING: runner $rpid is alive (start ticks $rticks, bash $R/rpd_p0_runner.sh)"
    [ -f runner-steps.txt ] && sed 's/^/step: /' runner-steps.txt
    finish 10
  fi
  if ! terminal; then
    echo "STOP: the runner $rpid is gone and wrote no p0.rc (an uncatchable kill); the cleanup is unverified"
    [ -e {shm} ] && echo "{shm} still exists on $(hostname)"
    state=GONE
  fi
fi
echo "== state $state"
echo "== the root (mode, bytes, path), staged copies by count only"
find . -path ./dry/staged -prune -o -path ./run/staged -prune -o -path ./clone -prune -o -printf '%M %s %P\\n' | sort -k3
for d in dry/staged run/staged; do [ -d "$d" ] && echo "$d: $(find "$d" -type f | wc -l | tr -d ' ') files"; done
send=()
for f in runner.pid runner.out runner-steps.txt p0.rc handoff.ok stat-p0.txt flux3-inputs.txt fence-overlap.txt rpd_p0_runner.sh production-config.ready.json sup-*.json dry/*.json run/*.json; do
  [ -f "$f" ] && send+=("$f")
done
total=0
for f in "${{send[@]}}"; do total=$(( total + $(stat -c %s "$f") )); done
echo "send files ${{#send[@]}}, bytes $total"
[ "$total" -le 67108864 ] || {{ echo "STOP: the send list exceeds 64 MiB"; finish 9; }}
for f in runner-steps.txt p0.rc; do [ -f "$f" ] && {{ echo "== $f"; cat "$f"; }}; done
for f in "${{send[@]}}"; do echo "sha256 $(sha256sum "$f" | cut -d' ' -f1) $f"; done
{tar_block}case $state in DONE) finish 0 ;; STOP) finish 12 ;; *) finish 11 ;; esac
"""

LAUNCH_HEADER_OLD = (
    "# RPD-RECO flux rerun rpd_flux3 (generated from rpd_flux2 at 6896e787, the director's ruling (A), 2026-11-23): the "
    "Mac-side launcher, in rpd_mnv_check2_launch.sh's pattern."
)
LAUNCH_HEADER_NEW = (
    "# RPD-RECO P0 (rpd_p0, generated from the flux3 launcher): the Mac-side launcher, in rpd_mnv_check2_launch.sh's"
    " pattern. connect requires cov2d's fresh ack file, kept byte for byte in the local session record."
)
LAUNCH_USAGE_CONNECT_OLD = (
    "#        bash rpd_flux3_launch.sh connect <new empty session dir> <login node> <ack.txt>   (submits job rpd_flux3)"
)
LAUNCH_USAGE_CONNECT_NEW = (
    "#        bash rpd_flux3_launch.sh connect <new empty session dir> <login node> <ack.txt>   (P0, detached on the"
    " node)"
)
LAUNCH_USAGE_FETCH_NEW = "(the runner's node while it runs; exit 10 if running)"


if __name__ == "__main__":
    sys.exit(main())
