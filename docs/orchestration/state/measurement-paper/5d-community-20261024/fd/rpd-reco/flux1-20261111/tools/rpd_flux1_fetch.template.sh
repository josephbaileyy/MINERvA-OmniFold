#!/bin/bash
# RPD-RECO flux connect 1 (revision 2), the fetch: reads what job rpd_flux1 left under the literal root
# /pscratch/sd/j/josephrb/rpd-reco-flux-20261111, on any login node. DRAFT for coverage-5b-audit and the director's go.
#   0. The job is finished when job.rc exists, or when sacct gives its jobid a terminal state (a job killed at its
#      time limit or out of memory writes no job.rc). Otherwise it prints job.id, job-host.txt and squeue's row,
#      writes nothing and exits 10. It can be run again.
#   1. job.id, job-host.txt (jobid, host, start and end UTC), job.rc and sacct's row; a listing of the whole root (mode,
#      bytes, path), the private tree by name only.
#   2. The factor products run/flux-factors-<PL>.npz stay on pscratch (director, F1). Each one's sha256 is printed and
#      compared with the sha256 flux-extract.json records for it.
#   3. The protected read (tools/protected_read.py): from the private prestage record, the public record
#      protected-read.json of the one listed exception (stat_before, stat_after, the UTC staging window, both staged
#      copies' sha256) and of every staged original that overlaps a protected path. Not applicable with no record.
#   4. The send list: the root's records that exist (job.id, job-host.txt, job.rc, job.out, job.err, rpd_flux1_job.sh,
#      connect.log, strace-probe.txt, fence-overlap.txt, exception-stat-outer.txt, protected-read.json); every regular
#      file directly in run/ except flux-factors-*.npz; every regular file directly in run/real-mnv-check/. Nothing in
#      run/original-inputs, run/mat-data, run/prepare-check, run/tmp, clone, tools or .rpd-private. Over 64 MiB refuses.
#   5. C3 (tools/c3_check.py) when run/prestage-reference.json exists; a .rpd-private without it refuses.
#   6. The redaction check (tools/check_redaction.py, prologue 5's, byte-identical), VIEW NONE; with no private
#      record, any file on the send list holding the string "fingerprints" refuses.
#   7. Only if those pass: connect.log printed, the sha256 of each file sent, and a base64 tar of the list. A FAIL in
#      the protected read does not stop the send (it is the finding); the fetch then exits 11.
# Writes: protected-read.json and the two check outputs under the root, and three tools under
# /dev/shm/limres-rpd-flux1-fetch (refused if it exists, removed at exit). Nothing is written to CFS. umask 077.
# Launched from a /dev/shm copy of itself ($1), which it deletes.
umask 077
SELF=$1
C3_SHA=@@C3_SHA@@
CHECK_SHA=992be729a3604cf8bae7ea04dfab93aeae9e259b647d3a4d598fd287b2736316
PREAD_SHA=@@PREAD_SHA@@
MAT_PYTHON=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
finish() { echo "== rpd-flux1-fetch rc=$1 $(date -u +%FT%TZ)"; rm -f -- /dev/shm/limres-rpd-flux1-fetch/c3_check.py /dev/shm/limres-rpd-flux1-fetch/check_redaction.py /dev/shm/limres-rpd-flux1-fetch/protected_read.py; rmdir /dev/shm/limres-rpd-flux1-fetch 2>/dev/null; rm -f -- "$SELF"; exit "$1"; }
case "$(hostname)" in login*) ;; *) echo "STOP: not a login node: $(hostname)"; rm -f -- "$SELF"; exit 9 ;; esac
echo "node $(hostname) $(date -u +%FT%TZ); fetch script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
[ -d /pscratch/sd/j/josephrb/rpd-reco-flux-20261111 ] || { echo "STOP: no root /pscratch/sd/j/josephrb/rpd-reco-flux-20261111"; rm -f -- "$SELF"; exit 9; }
cd /pscratch/sd/j/josephrb/rpd-reco-flux-20261111 || { rm -f -- "$SELF"; exit 9; }
[ -f job.id ] || { echo "STOP: no job.id (the connect submitted no job)"; rm -f -- "$SELF"; exit 9; }
jid=$(cat job.id)
[[ "$jid" =~ ^[0-9]+$ ]] || { echo "STOP: job.id is not a jobid"; rm -f -- "$SELF"; exit 9; }
acct=$(sacct -X -n -P -j "$jid" -o JobID,JobName,State,ExitCode,Elapsed,Start,End,NodeList,MaxRSS,AllocCPUS,ReqMem,Timelimit)
arc=$?
state=$(printf '%s\n' "$acct" | awk -F'|' -v j="$jid" '$1 == j {print $3}' | cut -d' ' -f1)
echo "job $jid; sacct rc=$arc; state [$state]"
printf '%s\n' "$acct" | sed '/^$/d; s/^/sacct: /'
echo "== job-host.txt"; cat job-host.txt 2>/dev/null || echo "(absent)"
if [ ! -f job.rc ]; then
  case "$state" in
    COMPLETED|FAILED|CANCELLED|TIMEOUT|OUT_OF_MEMORY|NODE_FAIL|PREEMPTED|BOOT_FAIL|DEADLINE)
      echo "FINISHED WITHOUT job.rc: sacct state $state" ;;
    *)
      echo "NOT FINISHED: no job.rc; squeue:"; squeue -h -j "$jid" -o '%i|%j|%T|%M|%l|%N' 2>&1
      rm -f -- "$SELF"; exit 10 ;;
  esac
else
  echo "job.rc: $(cat job.rc)"
fi
[ ! -e /dev/shm/limres-rpd-flux1-fetch ] || { echo "STOP: /dev/shm/limres-rpd-flux1-fetch exists"; rm -f -- "$SELF"; exit 9; }
[ ! -e c3-check.txt ] && [ ! -e redaction-check.txt ] && [ ! -e protected-read.json ] || { echo "STOP: a fetch output already exists"; rm -f -- "$SELF"; exit 9; }
echo "== 1. listing of the root"
find . -path ./clone -prune -o -printf '%M %s %P\n' | sort -k3
mkdir -m 700 /dev/shm/limres-rpd-flux1-fetch || finish 9
printf '%s' '@@C3_B64@@' | base64 -d > /dev/shm/limres-rpd-flux1-fetch/c3_check.py
printf '%s' '@@CHECK_B64@@' | base64 -d > /dev/shm/limres-rpd-flux1-fetch/check_redaction.py
printf '%s' '@@PREAD_B64@@' | base64 -d > /dev/shm/limres-rpd-flux1-fetch/protected_read.py
for pair in "/dev/shm/limres-rpd-flux1-fetch/c3_check.py:$C3_SHA" "/dev/shm/limres-rpd-flux1-fetch/check_redaction.py:$CHECK_SHA" "/dev/shm/limres-rpd-flux1-fetch/protected_read.py:$PREAD_SHA"; do
  f=${pair%%:*}; want=${pair##*:}; got=$(sha256sum "$f" | cut -d' ' -f1)
  echo "sha256 $got (expected $want) $f"
  [ "$got" = "$want" ] || { echo "STOP: digest of $f"; finish 5; }
done
echo "== 2. the factor products (kept on pscratch)"
for f in run/flux-factors-*.npz; do
  [ -f "$f" ] || { echo "no factor products"; break; }
  echo "product $(stat -c %s "$f") bytes sha256 $(sha256sum "$f" | cut -d' ' -f1) $f"
done
if [ -f run/flux-extract.json ]; then
  "$MAT_PYTHON" -I -S -c '
import hashlib, json, sys
products = json.load(open(sys.argv[1])).get("factor_products", {})
bad = 0
for playlist, item in sorted(products.items()):
    try:
        got = hashlib.sha256(open(item["path"], "rb").read()).hexdigest()
    except OSError as error:
        got = "unreadable: " + str(error)
    ok = got == item.get("sha256")
    bad += not ok
    print("recorded", playlist, item.get("sha256"), "equal" if ok else "DIFFERS (" + got + ")", item.get("path"))
print("factor products recorded", len(products), "differing", bad)
' run/flux-extract.json
fi
echo "== 3. the protected read"
raw=NONE
prc=0
if [ -f run/prestage-reference.json ]; then
  raw=$("$MAT_PYTHON" -I -S -c 'import json,sys; print(json.load(open(sys.argv[1]))["private_prepare"]["path"])' run/prestage-reference.json)
  "$MAT_PYTHON" -I -S /dev/shm/limres-rpd-flux1-fetch/protected_read.py "$raw" production-config.ready.json protected-read.json
  prc=$?
  echo "protected read rc=$prc"
elif [ -e .rpd-private ]; then
  echo "STOP: .rpd-private exists without run/prestage-reference.json; nothing is sent"; finish 7
else
  printf '%s\n' '{"schema": "rpd-flux1-protected-read/1", "status": "NOT_APPLICABLE", "problems": ["no private prestage record: prepare did not complete"]}' > protected-read.json
  echo "PROTECTED READ: not applicable (no private record)"
fi
cat protected-read.json
echo "== 4. the send list"
send=()
for f in job.id job-host.txt job.rc job.out job.err rpd_flux1_job.sh connect.log strace-probe.txt fence-overlap.txt exception-stat-outer.txt protected-read.json; do
  if [ -f "$f" ]; then send+=("$f"); else echo "absent (not sent): $f"; fi
done
while IFS= read -r f; do send+=("${f#./}"); done < <(find ./run ./run/real-mnv-check -maxdepth 1 -type f ! -name 'flux-factors-*.npz' 2>/dev/null | sort -u)
total=0
for f in "${send[@]}"; do
  case "$f" in *.rpd-private*|run/original-inputs/*|run/mat-data/*|run/prepare-check/*|run/tmp/*|clone/*|tools/*|run/flux-factors-*) echo "STOP: $f may not be sent"; finish 7 ;; esac
  b=$(stat -c %s "$f"); total=$((total + b)); echo "send $b $f"
done
echo "send files ${#send[@]}, bytes $total"
[ "$total" -le 67108864 ] || { echo "STOP: over 64 MiB; nothing is sent"; finish 7; }
abs=(); for f in "${send[@]}"; do abs+=("/pscratch/sd/j/josephrb/rpd-reco-flux-20261111/$f"); done
echo "== 5. C3"
if [ "$raw" != NONE ]; then
  "$MAT_PYTHON" -I -S /dev/shm/limres-rpd-flux1-fetch/c3_check.py /pscratch/sd/j/josephrb/rpd-reco-flux-20261111 \
    /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/run "${abs[@]}" > c3-check.txt 2>&1
  c3=$?
  cat c3-check.txt; echo "c3 check rc=$c3"
  [ "$c3" -eq 0 ] || { echo "STOP: the C3 check did not pass; nothing is sent"; finish 7; }
else
  echo "C3 not applicable: custody wrote no private record (no .rpd-private, no run/prestage-reference.json)" > c3-check.txt
  cat c3-check.txt
fi
echo "== 6. the redaction check"
if [ "$raw" != NONE ]; then
  "$MAT_PYTHON" -I -S /dev/shm/limres-rpd-flux1-fetch/check_redaction.py "$raw" NONE "${abs[@]}" \
    /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/c3-check.txt > redaction-check.txt 2>&1
  crc=$?
else
  hits=$(grep -l -F fingerprints "${abs[@]}")
  { echo "REDACTION CHECK not applicable: no private record exists"; echo "files naming fingerprints: [$hits]"; } > redaction-check.txt
  [ -z "$hits" ]; crc=$?
fi
cat redaction-check.txt; echo "check rc=$crc"
[ "$crc" -eq 0 ] || { echo "STOP: the redaction check did not pass; nothing is sent"; finish 7; }
echo "== 7. connect.log (checked)"
[ -f connect.log ] && cat connect.log
echo "== end connect.log"
send+=(c3-check.txt redaction-check.txt)
for f in "${send[@]}"; do echo "sha256 $(sha256sum "$f" | cut -d' ' -f1) $f"; done
echo "== TAR BEGIN"
tar -cf - "${send[@]}" | base64 -w 76
echo "== TAR END tar rc=${PIPESTATUS[0]}"
echo "left in place for the post-merge deletion: /pscratch/sd/j/josephrb/rpd-reco-flux-20261111 (the factor products, the staged copies, the clone, the private record)"
[ "$prc" -eq 0 ] || { echo "PROTECTED READ FAILED: the records were sent; the failure is in protected-read.json"; finish 11; }
finish 0
