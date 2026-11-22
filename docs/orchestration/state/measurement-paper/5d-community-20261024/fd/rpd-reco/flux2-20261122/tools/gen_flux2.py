"""Generate the flux rerun (rpd_flux2) config and scripts from flux connect 1's committed files.

usage: python3 -I gen_flux2.py SURVEY_DIR REPO
  SURVEY_DIR  e1 survey 1's output directory (remote 1a9e244a, ssh rc 0): survey.log holds the stat lines of the three
              selected MAT flux files
  REPO        a checkout whose nd-unfolding/ holds the bound RPD-RECO modules (sha256-checked against flux1's pins)

Director's ruling (c) with ruling (a), 2026-11-22. The config is flux1's (cde8d029), changed only at:
  - premise/cv_numerator_is_selected_spectrum and premise/generation_denominator_is_common: null -> true;
  - flux_selection/{1D,1M,1N}/retention: the placeholder -> a string built here from the survey's stat line;
  - flux_custody/path and flux_extract/path: flux1's run root -> ROOT;
  - cov2d_protected_paths: flux1's 30 paths followed by the six cov2d roots in COV2D_ADDED (36).
Any other changed key is refused. The bytes are json.dumps(indent=1, sort_keys=True, ensure_ascii=True) + "\n", the
format that reproduces cde8d029 exactly (checked here).

The scripts are flux1's committed scripts with counted replacements: the run root, the job name (rpd_flux1 ->
rpd_flux2), the config (base64 and sha256), the overlap fence tool (its write root), the squeue fences -> sacct, the
time limit (03:00:00 -> 01:00:00: 0.039 node-h, priced at 10 of 256 CPUs), and the launcher's pinned shas.
From the reads of 2026-11-22: the scripts' flux1 labels and the fetch's /dev/shm tool directory are renamed for
rpd_flux2 (the bound clone path /dev/shm/limres-rpd-flux1 is kept); the fetch refuses a failed tar (exit 14); the
launcher returns the remote script's rc rather than the trailing echo's, and refuses a cert ending within 30 minutes.
From Grok's read: the launcher's fence mode (cov2d_fence.sh rev 1, which calls squeue) refuses; both porcelain checks
refuse a failed git status; the fetch refuses a grep error and a failed base64; the sacct terminal set is cov2d rev 2's
(REVOKED refuses); survey.log is pinned by sha256.
Every replacement must match the stated number of times.
"""

from __future__ import annotations

import base64
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
FLUX1 = OUT.parent / "flux1-20261111"
OLD_ROOT = "/pscratch/sd/j/josephrb/rpd-reco-flux-20261111"
ROOT = "/pscratch/sd/j/josephrb/rpd-reco-flux2-20261122"
FLUX_DIR = "/pscratch/sd/j/josephrb/minerva/minerva_large_files/MATFluxAndReweightFiles/flux"
SHA = {
    "config": "cde8d02904b0257d82745b03fd61c1aef1a50270f14f36ad7f38c8b3f235f50b",
    "connect": "34694c0d90fa09b4d93c123cdd191043216dc02261b8de5d3076af1eeda0cb6a",
    "fetch": "dfade48a535e722cc5febdbe7749f9d4435d3a83403d8158b74beefb797f67ea",
    "launch": "8354aece1061e783c4d970cfc86b298f5be956c1b3cec319cc250040ef316b35",
    "fence": "baa7630936db399abf57aa6edf9af1ffc053a3ee80c3730981a806fd8598a202",
    "survey_remote": "1a9e244ad648cf60d64ada45ab62f5d6703ba14c7376225e1e08e300d6cf670b",
    "survey_log": "79a63325c0906444893ed91c2a2ca6d78d7246ee439f58d0f4cec55fb4f865e5",  # S1, 2026-11-22T22:01:53Z
}
# The six cov2d roots (ruling (a)), each with the committed fd/receipts-cov2d/ line that names it.
COV2D_ADDED = (
    ("/pscratch/sd/j/josephrb/cov2d-g2r-20261112", "g2r/AR23_Ua/README.md:22"),
    ("/pscratch/sd/j/josephrb/cov2d-g2r-deploy-j1", "g2r/envtest/job_E_post_MaRES_0.log.txt:98"),
    ("/pscratch/sd/j/josephrb/cov2d-re2shapes-20261114", "g2r/re2shapes/package/README.md:45"),
    ("/pscratch/sd/j/josephrb/cov2d-re2shapes-20261115", "g2r/cr/INPUTS-g2r.sha256:4"),
    ("/pscratch/sd/j/josephrb/cov2d-cr-g2r-20261116", "g2r/cr/README.md:48"),
    ("/pscratch/sd/j/josephrb/cov2d-xk-g2r-20261116", "g2r/xk/README.md:72"),
)
RECEIPTS = OUT.parent.parent / "receipts-cov2d"
PURGE_DAYS = 56  # pscratch purges files unread for 8 weeks
ALLOWED = {
    "/premise/cv_numerator_is_selected_spectrum",
    "/premise/generation_denominator_is_common",
    "/flux_selection/1D/retention",
    "/flux_selection/1M/retention",
    "/flux_selection/1N/retention",
    "/flux_custody/path",
    "/flux_extract/path",
    "/cov2d_protected_paths",
}

SQUEUE_FENCE = """q=$(squeue --me -h -o '%i|%j|%T') || { echo "STOP: squeue failed"; finish 3; }
printf '%s\\n' "$q" | sed '/^$/d; s/^/squeue: /'
printf '%s\\n' "$q" | awk -F'|' '$2 ~ /^(cov2d|t2a|rpd)/ {f=1} END {exit !f}' && { echo "STOP: a cov2d/t2a/rpd job is queued or running"; finish 3; }
"""
# The sacct fence fails closed, in cov2d_fence.sh rev 2's pattern (3fbc9cbd, merged 7d5a98361): stdout and stderr are
# read together, so any line that is not a 3-field row with a numeric JobID refuses (an error sacct prints while
# exiting 0, a truncated row); a cov2d*/t2a*/rpd* row refuses unless the first word of its State is in the closed
# terminal set ("CANCELLED by N" counts as CANCELLED). The set is rev 2's exactly (REVOKED refuses). The window is the
# director's 14 days. Known gaps, sacct-only by rule: a job that has stayed non-terminal since before the window can be
# omitted, as can a pending job with no EligibleTime; cov2d's fresh ack (no older than 6 h) covers them.
SACCT_FENCE = """start=$(date -u -d '14 days ago' +%F) || { echo "STOP: start date failed"; finish 3; }
[[ $start =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]] || { echo "STOP: start date malformed: '$start'"; finish 3; }
q=$(sacct -X -n -P -u josephrb -S "$start" -o JobID,JobName,State 2>&1) || { echo "STOP: sacct failed"; printf '%s\\n' "$q" | sed 's/^/sacct: /'; finish 3; }
v=$(printf '%s\\n' "$q" | awk -F'|' '
  BEGIN { split("BOOT_FAIL CANCELLED COMPLETED DEADLINE FAILED NODE_FAIL OUT_OF_MEMORY PREEMPTED TIMEOUT", t, " ")
          for (i in t) term[t[i]] = 1 }
  /^$/ { next }
  { rows++ }
  NF != 3 || $1 !~ /^[0-9]+([_+].*)?$/ { print "malformed: " $0; bad = 1; next }
  { split($3, w, " "); if (!(w[1] in term)) print "unended: " $0 }
  $2 ~ /^(cov2d|t2a|rpd)/ { n++; if (!(w[1] in term)) bad = 1 }
  END { print "sacct rows (14 days): " rows + 0 "; cov2d/t2a/rpd rows: " n + 0; exit bad }')
rc=$?
printf '%s\\n' "$v" | sed '/^$/d'
[ "$rc" -eq 0 ] || { echo "STOP: a cov2d/t2a/rpd job is unended, or a sacct line is malformed"; finish 3; }
"""
FETCH_SQUEUE = """      echo "NOT FINISHED: no job.rc; squeue:"; squeue -h -j "$jid" -o '%i|%j|%T|%M|%l|%N' 2>&1"""
FETCH_SACCT = """      echo "NOT FINISHED: no job.rc; sacct state [$state]\""""
# Fixes from the reads of 2026-11-22 (agy): the run's own labels, the fetch's tar status, and the launcher's exit status
# and cert check.
HEADER_OLD = "RPD-RECO flux connect 1 (revision 2)"
HEADER_NEW = "RPD-RECO flux rerun rpd_flux2 (generated from flux connect 1 revision 2)"
FETCH_TAR_OLD = 'echo "== TAR END tar rc=${PIPESTATUS[0]}"\n'
FETCH_TAR_NEW = (
    'ps=("${PIPESTATUS[@]}"); trc=${ps[0]}; brc=${ps[1]}\n'
    'echo "== TAR END tar rc=$trc base64 rc=$brc"\n'
    '[ "$trc" -eq 0 ] && [ "$brc" -eq 0 ] || { echo "TAR FAILED: tar rc=$trc, base64 rc=$brc; the record stream is incomplete"; finish 14; }\n'
)
FETCH_EXITS_OLD = "the fetch then exits 11 (protected read), 12 (product mismatch) or 13 (both)."
FETCH_EXITS_NEW = (
    "the fetch then exits 11 (protected read), 12 (product mismatch) or 13 (both). A failed tar or base64 exits 14."
)
# Grok: grep exits 2 on an error with empty output, which read as "no file names fingerprints".
FETCH_GREP_OLD = (
    '  hits=$(grep -l -F fingerprints "${abs[@]}")\n'
    '  { echo "REDACTION CHECK not applicable: no private record exists"; echo "files naming fingerprints: [$hits]"; } > redaction-check.txt\n'
    '  [ -z "$hits" ]; crc=$?\n'
)
FETCH_GREP_NEW = (
    '  hits=$(grep -l -F fingerprints "${abs[@]}"); grc=$?\n'
    '  { echo "REDACTION CHECK not applicable: no private record exists"; echo "grep rc=$grc; files naming fingerprints: [$hits]"; } > redaction-check.txt\n'
    '  [ "$grc" -eq 1 ] && [ -z "$hits" ]; crc=$?\n'
)
# Grok: fence mode pinned cov2d_fence.sh rev 1 (16a2a5cd), which calls squeue. The rerun does not use fence mode (the
# connect's step-2 sacct fence replaces it), so the mode refuses.
LAUNCH_FENCE_OLD = (
    '  fence)   S="$TOP/docs/orchestration/state/measurement-paper/5d-community-20261024/fd/tier2-20261110/t2a/code/cov2d_fence.sh"\n'
    "           SHA=16a2a5cd5e36f0a3d48577afd3c4b1d4adebe6baf72fcf228d7c85275739754a ;;\n"
)
LAUNCH_FENCE_NEW = (
    '  fence)   echo "STOP: fence mode is not used for rpd_flux2 (the connect\'s step-2 sacct fence replaces it)"; exit 9 ;;\n'
)
LAUNCH_FENCE_USAGE_OLD = "(the committed cov2d_fence.sh)"
LAUNCH_FENCE_USAGE_NEW = "(refused: not used for rpd_flux2)"
# The remote shell's last command was the echo, so ssh returned 0 whatever the script returned.
LAUNCH_RC_OLD = r'bash \"\$f\" \"\$f\"; echo \"script rc=\$?\"'
LAUNCH_RC_NEW = r'bash \"\$f\" \"\$f\"; rc=\$?; echo \"script rc=\$rc\"; exit \$rc'
LAUNCH_SSH_LINE = 'SSH="ssh -o ControlPath=none'
# e1_survey_launch.sh's cert check (24dddd72): the public cert's end time, read in UTC, at least 30 minutes away.
LAUNCH_CERT = """to=$(TZ=UTC ssh-keygen -L -f "$HOME/.ssh/nersc-cert.pub" 2>/dev/null | awk '/Valid:/ {print $NF}')
to_s=$(TZ=UTC date -j -f '%Y-%m-%dT%H:%M:%S' "$to" +%s 2>/dev/null) || { echo "STOP: cannot read the cert's end time"; exit 9; }
[ $((to_s - $(date -u +%s))) -ge 1800 ] || { echo "STOP: the cert ends within 30 minutes (valid to ${to}Z)"; exit 9; }
echo "cert valid to ${to}Z (UTC)"
"""


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def dump(config: dict) -> bytes:
    return (json.dumps(config, indent=1, sort_keys=True, ensure_ascii=True) + "\n").encode()


def replace(text: str, old: str, new: str, count: int, what: str) -> str:
    found = text.count(old)
    assert found == count, f"{what}: {old[:60]!r} occurs {found} times, expected {count}"
    return text.replace(old, new)


def leaves(value: object, path: str = "") -> dict[str, object]:
    if isinstance(value, dict):
        out: dict[str, object] = {}
        for key, item in value.items():
            out.update(leaves(item, f"{path}/{key}"))
        return out
    if isinstance(value, list) and path == "/cov2d_protected_paths":
        return {path: value}
    if isinstance(value, list):
        out = {}
        for index, item in enumerate(value):
            out.update(leaves(item, f"{path}/{index}"))
        return out
    return {path: value}


def utc(epoch: int) -> str:
    return dt.datetime.fromtimestamp(epoch, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def survey_stats(log: str) -> tuple[str, dict[str, dict]]:
    header = re.search(r"^== host (\S+) utc (\S+) epoch (\d+)$", log, re.M)
    assert header, "survey log has no host/utc/epoch line"
    host, when, epoch = header.group(1), header.group(2), int(header.group(3))
    assert utc(epoch) == when, (utc(epoch), when)
    stats = {}
    for group in ("1D", "1M", "1N"):
        name = f"{FLUX_DIR}/flux-gen2thin-pdg14-minervame{group}_rearrangedUniverses.root"
        lines = [line for line in log.splitlines() if line.startswith(name + "|")]
        assert len(lines) == 1, f"{group}: {len(lines)} stat lines"
        fields = lines[0].split("|")
        assert len(fields) == 5 and all(f.isdigit() for f in fields[1:]), lines[0]
        size, atime, mtime, inode = (int(f) for f in fields[1:])
        assert atime <= epoch and mtime <= epoch, f"{group}: a stat time is after the survey's epoch"
        stats[group] = {"bytes": size, "atime": atime, "mtime": mtime, "inode": inode}
    return f"stat on {host} at {when} (epoch {epoch})", stats


def retention(when: str, stat: dict) -> str:
    return (
        f"pscratch, purged when unread {PURGE_DAYS} days: {when}: atime {utc(stat['atime'])}, "
        f"mtime {utc(stat['mtime'])}, {stat['bytes']} bytes, inode {stat['inode']}; "
        f"earliest purge exposure {utc(stat['atime'] + PURGE_DAYS * 86400)}"
    )


def build_config(old: dict, survey: str, repo: Path) -> dict:
    when, stats = survey_stats(survey)
    inventory = (repo / old["inventory"]["path"].split("/repo/", 1)[1]).read_bytes()
    assert sha(inventory) == old["inventory"]["sha256"], "inventory digest"
    rows = [line.split("\t") for line in inventory.decode().splitlines()]
    head = rows[0]
    new = json.loads(json.dumps(old))
    new["premise"]["cv_numerator_is_selected_spectrum"] = True
    new["premise"]["generation_denominator_is_common"] = True
    for group, spec in new["flux_selection"].items():
        matches = [r for r in rows[1:] if r[head.index("playlist_label")] == group
                   and r[head.index("relative_path")] == spec["relative_path"]]
        assert len(matches) == 1, group
        assert int(matches[0][head.index("bytes")]) == stats[group]["bytes"], f"{group}: stat bytes differ from inventory"
        assert spec["retention"] == "AWAITING_RUNTIME_STAT_AND_STAGED_RETENTION_RECORD", group
        spec["retention"] = retention(when, stats[group])
    for key in ("flux_custody", "flux_extract"):
        assert new[key]["path"].startswith(OLD_ROOT + "/") and new[key]["sha256"] is None, key
        new[key]["path"] = ROOT + new[key]["path"][len(OLD_ROOT):]
    assert len(old["cov2d_protected_paths"]) == 30
    for path, receipt in COV2D_ADDED:
        file, line = receipt.rsplit(":", 1)
        assert path in (RECEIPTS / file).read_text().splitlines()[int(line) - 1], receipt
        assert path not in old["cov2d_protected_paths"], path
    new["cov2d_protected_paths"] = old["cov2d_protected_paths"] + [path for path, _ in COV2D_ADDED]
    a, b = leaves(old), leaves(new)
    assert set(a) == set(b), "the key set changed"
    changed = {key for key in a if a[key] != b[key]}
    assert changed == ALLOWED, sorted(changed ^ ALLOWED)
    return new


def bound_digest(repo: Path, config: dict) -> str:
    pins = (FLUX1 / "rpd_flux1_connect.sh").read_text()
    module = repo / "nd-unfolding" / "fd_rpd_reco.py"
    assert f"{sha(module.read_bytes())} nd-unfolding/fd_rpd_reco.py" in pins, "REPO's fd_rpd_reco.py is not the bound one"
    sys.path.insert(0, str(module.parent))
    import fd_rpd_reco  # noqa: E402

    return fd_rpd_reco.flux_selection_digest(config)


def main() -> int:
    survey_dir, repo = Path(sys.argv[1]), Path(sys.argv[2])
    assert (survey_dir / "remote.sha256").read_text().split()[0] == SHA["survey_remote"], "survey remote script"
    assert sha((survey_dir / "e1_survey_remote.sh").read_bytes()) == SHA["survey_remote"], "survey remote copy"
    assert (survey_dir / "ssh_rc.txt").read_text().strip() == "0", "survey ssh rc"
    # The launcher writes survey.log; the committed copy is survey.log.txt (*.log is gitignored). Same bytes.
    log_path = survey_dir / "survey.log"
    if not log_path.exists():
        log_path = survey_dir / "survey.log.txt"
    assert sha(log_path.read_bytes()) == SHA["survey_log"], "survey log"
    files = {name: (FLUX1 / name).read_bytes() for name in
             ("production-config.ready.json", "rpd_flux1_connect.sh", "rpd_flux1_fetch.sh", "rpd_flux1_launch.sh")}
    fence_old = (FLUX1 / "tools" / "fence_overlap.py").read_bytes()
    for key, name in (("config", "production-config.ready.json"), ("connect", "rpd_flux1_connect.sh"),
                      ("fetch", "rpd_flux1_fetch.sh"), ("launch", "rpd_flux1_launch.sh")):
        assert sha(files[name]) == SHA[key], name
    assert sha(fence_old) == SHA["fence"]
    old = json.loads(files["production-config.ready.json"])
    assert dump(old) == files["production-config.ready.json"], "the JSON format does not reproduce cde8d029"

    new = build_config(old, log_path.read_text(), repo)
    cfg = dump(new)
    p0_form = json.loads(cfg)
    p0_form["flux_extract"]["sha256"] = p0_form["flux_custody"]["sha256"] = "0" * 64
    digests = {
        "flux1": bound_digest(repo, old),
        "rerun": bound_digest(repo, new),
        "p0_form": bound_digest(repo, p0_form),
    }
    assert digests["rerun"] == digests["p0_form"] != digests["flux1"], digests

    fence = replace(fence_old.decode(), f'WRITE_ROOTS = ("{OLD_ROOT}",', f'WRITE_ROOTS = ("{ROOT}",', 1, "fence").encode()
    b64 = lambda data: base64.b64encode(data).decode()  # noqa: E731

    connect = files["rpd_flux1_connect.sh"].decode()
    connect = replace(connect, b64(files["production-config.ready.json"]), b64(cfg), 1, "connect config")
    connect = replace(connect, b64(fence_old), b64(fence), 1, "connect fence tool")
    connect = replace(connect, SHA["config"], sha(cfg), 3, "connect config sha")
    connect = replace(connect, "cde8d029...", sha(cfg)[:8] + "...", 1, "connect config label")
    connect = replace(connect, '"20261111" a fixed label', '"20261122" a fixed label', 1, "connect root label")
    connect = replace(connect, SHA["fence"], sha(fence), 1, "connect fence sha")
    connect = replace(connect, OLD_ROOT, ROOT, 38, "connect root")
    connect = replace(connect, "rpd_flux1", "rpd_flux2", 12, "connect job name")
    connect = replace(connect, SQUEUE_FENCE, SACCT_FENCE, 1, "connect fence")
    connect = replace(connect, "--time=03:00:00", "--time=01:00:00", 1, "connect time")
    connect = replace(connect, "TimeLimit=03:00:00", "TimeLimit=01:00:00", 1, "connect time check")
    connect = replace(connect, "--time 03:00:00", "--time 01:00:00", 1, "connect time comment")
    connect = replace(connect, HEADER_OLD, HEADER_NEW, 1, "connect header")
    connect = replace(connect, "RPD-RECO flux connect 1, the job half", "RPD-RECO flux rerun, the job half", 1, "job header")
    connect = replace(connect, "== rpd-flux1-connect", "== rpd-flux2-connect", 1, "connect finish label")
    connect = replace(connect, "cov2d's 30 protected paths", "cov2d's 36 protected paths", 1, "connect path count")
    for repo_dir, stop in ((f"{ROOT}/clone", "finish 5"), ("/dev/shm/limres-rpd-flux1/repo", "fin 5")):
        connect = replace(
            connect,
            f"porc=$(git -C {repo_dir} status --porcelain | wc -l)\n",
            f'st=$(git -C {repo_dir} status --porcelain) || {{ echo "STOP: git status failed"; {stop}; }}\n'
            f"porc=$(printf '%s' \"$st\" | grep -c '^')\n",
            1,
            f"porcelain status {repo_dir}",
        )
    assert "squeue" not in connect and "03:00:00" not in connect and "--porcelain | wc -l" not in connect

    fetch = files["rpd_flux1_fetch.sh"].decode()
    fetch = replace(fetch, OLD_ROOT, ROOT, 9, "fetch root")
    fetch = replace(fetch, "rpd_flux1", "rpd_flux2", 3, "fetch job name")
    fetch = replace(fetch, FETCH_SQUEUE, FETCH_SACCT, 1, "fetch squeue row")
    fetch = replace(fetch, "and squeue's row", "and sacct's state", 1, "fetch comment")
    fetch = replace(fetch, HEADER_OLD, HEADER_NEW, 1, "fetch header")
    fetch = replace(fetch, "/dev/shm/limres-rpd-flux1-fetch", "/dev/shm/limres-rpd-flux2-fetch", 17, "fetch tool dir")
    fetch = replace(fetch, "== rpd-flux1-fetch", "== rpd-flux2-fetch", 1, "fetch finish label")
    fetch = replace(fetch, FETCH_TAR_OLD, FETCH_TAR_NEW, 1, "fetch tar rc")
    fetch = replace(fetch, FETCH_EXITS_OLD, FETCH_EXITS_NEW, 1, "fetch exit list")
    fetch = replace(fetch, FETCH_GREP_OLD, FETCH_GREP_NEW, 1, "fetch fingerprint grep rc")
    assert "squeue" not in fetch and "limres-rpd-flux1-fetch" not in fetch

    launch = files["rpd_flux1_launch.sh"].decode()
    launch = replace(launch, SHA["connect"], sha(connect.encode()), 1, "launch connect sha")
    launch = replace(launch, SHA["fetch"], sha(fetch.encode()), 1, "launch fetch sha")
    launch = replace(launch, OLD_ROOT, ROOT, 1, "launch root")
    launch = replace(launch, "rpd_flux1", "rpd_flux2", 7, "launch names")
    launch = replace(launch, HEADER_OLD, HEADER_NEW, 1, "launch header")
    launch = replace(launch, "/dev/shm/rpd-flux1-$MODE", "/dev/shm/rpd-flux2-$MODE", 1, "launch staging name")
    launch = replace(launch, LAUNCH_RC_OLD, LAUNCH_RC_NEW, 1, "launch remote rc")
    launch = replace(launch, LAUNCH_SSH_LINE, LAUNCH_CERT + LAUNCH_SSH_LINE, 1, "launch cert check")
    launch = replace(launch, LAUNCH_FENCE_OLD, LAUNCH_FENCE_NEW, 1, "launch fence mode refused")
    launch = replace(launch, LAUNCH_FENCE_USAGE_OLD, LAUNCH_FENCE_USAGE_NEW, 1, "launch fence usage")
    assert "16a2a5cd" not in launch

    outputs = {
        "production-config.ready.json": cfg,
        "tools/fence_overlap.py": fence,
        "rpd_flux2_connect.sh": connect.encode(),
        "rpd_flux2_fetch.sh": fetch.encode(),
        "rpd_flux2_launch.sh": launch.encode(),
    }
    for name, data in outputs.items():
        (OUT / name).write_bytes(data)
        print(sha(data), name)
    print("flux_selection_digest flux1", digests["flux1"])
    print("flux_selection_digest rerun", digests["rerun"], "(P0 form, extract and custody sha256 filled: equal)")
    for path, receipt in COV2D_ADDED:
        print("added", path, "fd/receipts-cov2d/" + receipt)
    return 0


if __name__ == "__main__":
    sys.exit(main())
