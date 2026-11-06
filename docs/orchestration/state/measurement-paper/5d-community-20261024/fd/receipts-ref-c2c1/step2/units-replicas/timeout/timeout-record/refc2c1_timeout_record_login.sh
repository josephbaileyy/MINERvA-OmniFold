#!/bin/bash
# REF-C2C1 step two, the replicas: the record of the four TIMEOUT jobs (60890529-32), on a login node, detached (the
# director's ruling of 2026-11-06: the timeouts are INVALID, not a control STOP; the 303 units with PASS markers stand;
# commit the four jobs' records, with the after-stats and porcelain they never took, taken now). Read-only except under
# $O/logs-replicas/timeout-record and the four $O/REPLICAS-TIMEOUT-j<J> records:
#   - each job is out of the queue and sacct reads TIMEOUT;
#   - lanes.tsv is the reviewed one (sha256 7b737d0c), so each job's declared unit set is the binding's;
#   - every unit's .done read by O_NOATIME: PASS units and missing units per job; a missing unit with any file under
#     units/ is a STOP (a half-written unit);
#   - the 303 COV2D inputs stat'd now (no read), compared with each job's own before-file;
#   - porcelain --ignored of $O/deploy-replicas (GIT_OPTIONAL_LOCKS=0);
#   - REPLICAS-TIMEOUT-j<J>: {"job", "index", "state", "units_declared", "pass_markers", "pass_units", "missing_units",
#     "watch_moved", "porcelain_after", "recorded"}, the PASS set being what the 3b read gate unions.
# The REF-C2C1 unit outputs are not opened; only the .done markers. No set -u. Launched from a /dev/shm copy ($1).
SELF=$1
O=/pscratch/sd/j/josephrb/ref-c2c1-20261106
L=$O/logs-replicas
T=$L/timeout-record
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
LANES_SHA=7b737d0c4bb5e547adae0376f9c50da00cc1ec9a08d7dc2c892804e0b968524c
bail() { rm -f -- "$SELF"; exit 9; }
case "$(hostname)" in login*) ;; *) bail ;; esac
[ -x "$PY" ] && [ -d "$O/deploy-replicas" ] && [ -s "$L/lanes.tsv" ] && [ ! -e "$T" ] || bail
for J in 0 1 2 3; do [ ! -e "$O/REPLICAS-TIMEOUT-j$J" ] && [ ! -e "$O/REPLICAS-DONE-j$J" ] && [ -s "$L/j$J-watch-before.txt" ] || bail; done
mkdir -p "$T" || bail
exec > "$T/record.log" 2>&1
finish() { echo "ref-c2c1 timeout record rc=$1"; date -u +%FT%TZ; echo "$1" > "$T/record.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ
echo "record script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$T/refc2c1_timeout_record_login.sh"
JOBS=60890529,60890530,60890531,60890532
echo "fence, recorded: squeue -u josephrb at $(date -u +%FT%TZ):"; squeue -u josephrb -h -o '%i|%j|%T|%M|%l' | sed 's/^/  /'
q=$(squeue -h -j $JOBS -o %i 2>/dev/null); [ -z "$q" ] || { echo "STOP: a replica job is still in the queue: $q"; finish 4; }
sacct -j $JOBS -X -n -P -o JobID,JobName,State,ExitCode,Timelimit,Start,End,Elapsed,NNodes > "$T/sacct.txt"; cat "$T/sacct.txt"
[ "$(cut -d'|' -f3 "$T/sacct.txt" | sort -u)" = TIMEOUT ] && [ "$(wc -l < "$T/sacct.txt")" -eq 4 ] || { echo "STOP: sacct is not four TIMEOUT rows"; finish 4; }
lt=$(dd if="$L/lanes.tsv" iflag=noatime status=none | sha256sum | cut -d' ' -f1); echo "lanes.tsv sha256 $lt (reviewed $LANES_SHA)"
[ "$lt" = "$LANES_SHA" ] || { echo "STOP: lanes.tsv is not the reviewed one"; finish 4; }
xargs -d '\n' stat -c '%X %n' < <(dd if="$L/cov2d-watch-paths.txt" iflag=noatime status=none) > "$T/watch-after-login.txt" 2>&1
echo "COV2D inputs stat'd now: $(wc -l < "$T/watch-after-login.txt") at $(date -u +%FT%TZ)"
na=$(GIT_OPTIONAL_LOCKS=0 git -C "$O/deploy-replicas" status --porcelain --ignored | wc -l)
echo "deploy-replicas porcelain --ignored lines now: $na"; GIT_OPTIONAL_LOCKS=0 git -C "$O/deploy-replicas" status --porcelain --ignored | head -10
for J in 0 1 2 3; do echo "tmp-replicas-j$J: $(find "$O/tmp-replicas-j$J" -mindepth 1 2>/dev/null | wc -l) entries"; done
"$PY" -B -I - "$O" "$T" "$na" <<'PYEOF'
import json, os, sys
O, T, na = sys.argv[1], sys.argv[2], int(sys.argv[3])
L = os.path.join(O, "logs-replicas")
def rd(p):
    fd = os.open(p, os.O_RDONLY | os.O_NOATIME)
    try:
        b = b""
        while True:
            c = os.read(fd, 1 << 16)
            if not c: return b
            b += c
    finally: os.close(fd)
jobs = {0: "60890529", 1: "60890530", 2: "60890531", 3: "60890532"}
decl = {J: [] for J in jobs}
for line in rd(os.path.join(L, "lanes.tsv")).decode().splitlines():
    if line.startswith("#") or not line.strip(): continue
    j, l, u = line.split("\t"); decl[int(j)].append(u)
assert sum(len(v) for v in decl.values()) == 350 and len({u for v in decl.values() for u in v}) == 350
after = rd(os.path.join(T, "watch-after-login.txt"))
units = set(os.listdir(os.path.join(O, "units")))
rc = 0
for J, job in jobs.items():
    p, m, half = [], [], []
    for u in decl[J]:
        name = u.replace(":", "_b")
        d = os.path.join(O, "units", name + ".done")
        ok = os.path.exists(d) and json.loads(rd(d)).get("verdict") == "PASS"
        (p if ok else m).append(name)
        if not ok and any(f == name or f.startswith(name + ".") for f in units): half.append(name)
    moved = 0 if rd(os.path.join(L, f"j{J}-watch-before.txt")) == after else 1
    rec = {"job": job, "index": J, "state": "TIMEOUT", "units_declared": len(decl[J]), "pass_markers": len(p),
           "pass_units": sorted(p), "missing_units": sorted(m), "watch_moved": moved, "porcelain_after": na,
           "recorded": "post hoc on a login node by refc2c1_timeout_record_login.sh; the job was killed before its own after-stat and porcelain"}
    with open(os.path.join(O, f"REPLICAS-TIMEOUT-j{J}"), "w") as f: f.write(json.dumps(rec) + "\n")
    print(f"j{J} job {job}: declared {len(decl[J])}, PASS {len(p)}, missing {len(m)}, half-written {half}, watch_moved {moved}")
    if half or moved: rc = 4
tot = sum(json.loads(open(os.path.join(O, f"REPLICAS-TIMEOUT-j{J}")).read())["pass_markers"] for J in jobs)
print(f"PASS total {tot} of 350")
sys.exit(rc)
PYEOF
prc=$?; echo "record writer rc=$prc"
for J in 0 1 2 3; do echo "REPLICAS-TIMEOUT-j$J sha256 $(sha256sum "$O/REPLICAS-TIMEOUT-j$J" | cut -d' ' -f1)"; done
[ "$prc" -eq 0 ] || { echo "STOP: a half-written unit or a moved COV2D atime"; finish 4; }
[ "$na" -eq 0 ] || { echo "STOP: deploy-replicas is not clean"; finish 4; }
finish 0
