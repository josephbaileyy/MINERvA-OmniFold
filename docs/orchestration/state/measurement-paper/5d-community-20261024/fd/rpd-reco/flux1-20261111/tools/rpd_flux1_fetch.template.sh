#!/bin/bash
# RPD-RECO flux connect 1, the fetch: reads what rpd_flux1_connect.sh's detached runner left under the literal root
# /pscratch/sd/j/josephrb/rpd-reco-flux-20261111, on any login node. DRAFT for coverage-5b-audit and the director's go.
#   0. If the runner has not finished (no connect.rc), it prints the log's size and this node's matching processes,
#      writes nothing and exits 10. It can be run again.
#   1. A listing of the whole root (mode, bytes, path), the private tree included by name only.
#   2. The send list: the root's runner.sh, connect.log, connect.rc and strace-probe.txt, every regular file directly
#      in run/ and every regular file directly in run/real-mnv-check/. Nothing in run/original-inputs, run/mat-data,
#      run/prepare-check, run/tmp or .rpd-private is sent; those directories hold the staged input and MAT copies.
#      Over 64 MiB in all refuses.
#   3. C3 (tools/c3_check.py, prologue 5's check for the prestage record) when custody wrote run/prestage-reference.json.
#      A .rpd-private without that reference refuses. With neither, C3 is recorded as not applicable.
#   4. The redaction check (tools/check_redaction.py, prologue 5's, byte-identical) against the private record, with
#      VIEW NONE: prepare writes no public view of the prestage. With no private record, the check is recorded as not
#      applicable, and any file on the send list with a key or string "fingerprints" refuses.
#   5. Only if those pass: connect.rc and connect.log printed, the sha256 of each file sent, and a base64 tar of the list.
# Writes: the two check outputs under the root, and the two tools under /dev/shm/limres-rpd-flux1-fetch (refused if it
# exists, removed at exit). Nothing is written to CFS. umask 077. No set -u.
# Launched from a /dev/shm copy of itself ($1), which it deletes.
umask 077
SELF=$1
C3_SHA=@@C3_SHA@@
CHECK_SHA=992be729a3604cf8bae7ea04dfab93aeae9e259b647d3a4d598fd287b2736316
MAT_PYTHON=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
finish() { echo "== rpd-flux1-fetch rc=$1 $(date -u +%FT%TZ)"; rm -f -- /dev/shm/limres-rpd-flux1-fetch/c3_check.py /dev/shm/limres-rpd-flux1-fetch/check_redaction.py; rmdir /dev/shm/limres-rpd-flux1-fetch 2>/dev/null; rm -f -- "$SELF"; exit "$1"; }
case "$(hostname)" in login*) ;; *) echo "STOP: not a login node: $(hostname)"; rm -f -- "$SELF"; exit 9 ;; esac
echo "node $(hostname) $(date -u +%FT%TZ); fetch script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
[ -d /pscratch/sd/j/josephrb/rpd-reco-flux-20261111 ] || { echo "STOP: no root /pscratch/sd/j/josephrb/rpd-reco-flux-20261111"; rm -f -- "$SELF"; exit 9; }
cd /pscratch/sd/j/josephrb/rpd-reco-flux-20261111 || { rm -f -- "$SELF"; exit 9; }
if [ ! -f connect.rc ]; then
  echo "NOT FINISHED: no connect.rc. connect.log $(wc -c < connect.log) bytes, $(wc -l < connect.log) lines, modified $(date -u -r connect.log +%FT%TZ)"
  echo "processes on $(hostname) naming the clone or the runner (the runner is visible only on the connect's node):"
  ps -o pid,etime,stat,args -u "$(id -un)" | grep -E 'limres-rpd-flux1/|rpd-reco-flux-20261111/runner' | grep -v grep
  rm -f -- "$SELF"; exit 10
fi
[ ! -e /dev/shm/limres-rpd-flux1-fetch ] || { echo "STOP: /dev/shm/limres-rpd-flux1-fetch exists"; rm -f -- "$SELF"; exit 9; }
[ ! -e c3-check.txt ] && [ ! -e redaction-check.txt ] || { echo "STOP: a check output already exists"; rm -f -- "$SELF"; exit 9; }
echo "connect.rc present"
echo "== 1. listing of the root"
find . -printf '%M %s %P\n' | sort -k3
echo "== 2. the send list"
send=(runner.sh connect.log connect.rc strace-probe.txt)
while IFS= read -r f; do send+=("${f#./}"); done < <(find ./run ./run/real-mnv-check -maxdepth 1 -type f 2>/dev/null | sort -u)
total=0
for f in "${send[@]}"; do
  case "$f" in *.rpd-private*|run/original-inputs/*|run/mat-data/*|run/prepare-check/*|run/tmp/*) echo "STOP: $f may not be sent"; finish 7 ;; esac
  [ -f "$f" ] || { echo "STOP: $f is missing"; finish 7; }
  b=$(stat -c %s "$f"); total=$((total + b)); echo "send $b $f"
done
echo "send files ${#send[@]}, bytes $total"
[ "$total" -le 67108864 ] || { echo "STOP: over 64 MiB; nothing is sent"; finish 7; }
mkdir -m 700 /dev/shm/limres-rpd-flux1-fetch || finish 9
printf '%s' '@@C3_B64@@' | base64 -d > /dev/shm/limres-rpd-flux1-fetch/c3_check.py
printf '%s' '@@CHECK_B64@@' | base64 -d > /dev/shm/limres-rpd-flux1-fetch/check_redaction.py
for pair in "/dev/shm/limres-rpd-flux1-fetch/c3_check.py:$C3_SHA" "/dev/shm/limres-rpd-flux1-fetch/check_redaction.py:$CHECK_SHA"; do
  f=${pair%%:*}; want=${pair##*:}; got=$(sha256sum "$f" | cut -d' ' -f1)
  echo "sha256 $got (expected $want) $f"
  [ "$got" = "$want" ] || { echo "STOP: digest of $f"; finish 5; }
done
abs=(); for f in "${send[@]}"; do abs+=("/pscratch/sd/j/josephrb/rpd-reco-flux-20261111/$f"); done
echo "== 3. C3"
if [ -f run/prestage-reference.json ]; then
  "$MAT_PYTHON" -I -S /dev/shm/limres-rpd-flux1-fetch/c3_check.py /pscratch/sd/j/josephrb/rpd-reco-flux-20261111 \
    /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/run "${abs[@]}" > c3-check.txt 2>&1
  c3=$?
  cat c3-check.txt; echo "c3 check rc=$c3"
  [ "$c3" -eq 0 ] || { echo "STOP: the C3 check did not pass; nothing is sent"; finish 7; }
  raw=$("$MAT_PYTHON" -I -S -c 'import json,sys; print(json.load(open(sys.argv[1]))["private_prepare"]["path"])' run/prestage-reference.json)
elif [ -e .rpd-private ]; then
  echo "STOP: .rpd-private exists without run/prestage-reference.json; nothing is sent"; finish 7
else
  echo "C3 not applicable: custody wrote no private record (no .rpd-private, no run/prestage-reference.json)" > c3-check.txt
  cat c3-check.txt
  raw=NONE
fi
echo "== 4. the redaction check"
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
echo "== 5. connect.rc and connect.log (checked)"
cat connect.rc
echo "== connect.log"
cat connect.log
echo "== end connect.log"
send+=(c3-check.txt redaction-check.txt)
for f in "${send[@]}"; do echo "sha256 $(sha256sum "$f" | cut -d' ' -f1) $f"; done
echo "== TAR BEGIN"
tar -cf - "${send[@]}" | base64 -w 76
echo "== TAR END tar rc=${PIPESTATUS[0]}"
echo "left in place for the post-merge deletion: /pscratch/sd/j/josephrb/rpd-reco-flux-20261111 and, on the connect's node, /dev/shm/limres-rpd-flux1"
finish 0
