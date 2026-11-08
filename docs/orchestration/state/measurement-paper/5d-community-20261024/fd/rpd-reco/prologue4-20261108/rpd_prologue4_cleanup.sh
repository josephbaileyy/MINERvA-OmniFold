#!/bin/bash
# RPD-RECO #848 prologue rerun 4: post-merge deletion of the canonical (private) prepare record and its root on the
# cluster (the director's condition: unsalted SHA-256 fingerprints of every environment value never reach the repo,
# and the private record and the root are deleted after the receipt merges, under the receipt's ledger row
# delete-copies/row1-dev-shm-private-prepare). Runs only on login27, where /dev/shm/limres-rpd-prologue4-20261108
# was written. In order:
#   1. the COV2D fence (rs1_* and ens1_* allowed; anything else refuses);
#   2. the private record's sha256 must equal the declared 7f12fdfd...; otherwise STOP and nothing is deleted;
#   3. a listing of the whole root (type, size, relative path), then removal of the literal root
#      /dev/shm/limres-rpd-prologue4-20261108 (the clone, the policy config, the tools, the run directory and
#      .rpd-private), then a check that it is gone. The ledger is printed as JSON between markers.
# Launched from a /dev/shm copy of itself ($1), which it deletes.
SELF=$1
finish() { echo "== rpd-prologue4-cleanup rc=$1 $(date -u +%FT%TZ)"; rm -f -- "$SELF"; exit "$1"; }
[ "$(hostname)" = login27 ] || { echo "STOP: not login27: $(hostname)"; finish 9; }
echo "node $(hostname) $(date -u +%FT%TZ)"
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
echo "== 1. COV2D fence (allowed names: rs1_* and ens1_*; anything else refuses)"
fence=$(squeue -u josephrb -h -o '%i|%j|%T|%M|%l'); frc=$?
echo "squeue rc=$frc; rows:"
printf '%s\n' "$fence"
echo "-- end rows"
bad=$(printf '%s\n' "$fence" | awk -F'|' 'NF && $2 !~ /^(rs1_|ens1_)/')
echo "refusing rows: [$bad]"
[ "$frc" -eq 0 ] && [ -z "$bad" ] || { echo "STOP: the fence is not clear"; finish 3; }
echo "FENCE: clear"
echo "== 2 and 3. verify, list, remove"
/usr/bin/python3 -I -S - <<'PY'
import datetime, hashlib, json, os, shutil, socket, sys
ROOT = "/dev/shm/limres-rpd-prologue4-20261108"
RAW = ".rpd-private/3cdf27c8d29fe5d5407acb8ca456ade8a1df23de41ce5930c70a2a3bcb5cc522/prologue-prepare.json"
DECLARED = {RAW: "7f12fdfdd14bf82ff1e9ba72324b9269bba183984f41cc6fdf5b4383573a0afb"}
now = lambda: datetime.datetime.utcnow().isoformat(timespec="milliseconds") + "Z"
ledger = {"host": socket.gethostname(), "python": sys.version.split()[0], "start": now(), "roots": {}}
entry = {"declared": DECLARED}
ledger["roots"][ROOT] = entry
rc = 0
if not os.path.isdir(ROOT):
    entry["error"] = "root absent before deletion"
    rc = 5
else:
    before = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames.sort()
        for name in sorted(filenames):
            path = os.path.join(dirpath, name)
            st = os.lstat(path)
            before.append(["f", st.st_size, os.path.relpath(path, ROOT)])
    entry["before_file_count"] = len(before)
    entry["before_run"] = [row for row in before if row[2].startswith("run/") or row[2].startswith(".rpd-private/")]
    with open(os.path.join(ROOT, RAW), "rb") as fh:
        measured = hashlib.sha256(fh.read()).hexdigest()
    entry["measured"] = {RAW: measured}
    if measured != DECLARED[RAW]:
        entry["error"] = "private record digest differs from the declared value; nothing deleted"
        rc = 6
    else:
        shutil.rmtree(ROOT)
        entry["rmtree"] = [now(), ROOT]
ledger["still_present"] = [ROOT] if os.path.exists(ROOT) else []
if rc == 0 and ledger["still_present"]:
    rc = 7
ledger["rc"] = rc
ledger["end"] = now()
print("== LEDGER BEGIN")
print(json.dumps(ledger, indent=1, sort_keys=False))
print("== LEDGER END")
sys.exit(rc)
PY
prc=$?
echo "cleanup python rc=$prc"
finish "$prc"
