#!/bin/bash
# Local adler32 of our MC AnaTuples on /pscratch, for the data transfer node (dtn01.nersc.gov), where
# /pscratch is /global/pscratch. Read-only on every input; at most 4 parallel streams; low I/O priority.
# The checksum comes from adler32_file.py (zlib, every byte read, O_NOATIME), NOT from `xrdadler32 <path>`,
# which writes a user.XrdCks.adler32 xattr into the input and answers later calls from that cache unread.
#
#   nohup bash local_adler.sh LIST OUT > /dev/null 2>&1 &
#
# LIST: one path per line relative to minerva_large_files/MC/StandardMC.
# OUT:  TSV, one row appended per file (under flock): relpath, adler32 (or -), status OK|ERR, start_utc,
#       end_utc, host, raw output (adler32, bytes_read, st_size, seconds, path). OK needs bytes_read == st_size. "#run-start" / "#run-end" rows bracket each invocation.
# Resumable: a relpath that already has an OK row is skipped; ERR rows are retried on the next run.
# Each file has a watchdog (timeout 3600 s, then KILL); a timeout is an ERR, never a checksum.
set -o pipefail
SRC=${SRC:-/global/pscratch/sd/j/josephrb/minerva/minerva_large_files/MC/StandardMC}
HERE=$(cd "$(dirname "$0")" && pwd)
ADLER=${ADLER:-$HERE/adler32_file.py}
PY=${PY:-/usr/bin/python3}
NSTREAM=${NSTREAM:-4}
[ "$NSTREAM" -le 4 ] || { echo "at most 4 streams" >&2; exit 2; }
LIST=$1; OUT=$2
export SRC ADLER PY OUT
H=$(hostname); export H

one() {
  rel=$1
  t0=$(date -u +%FT%TZ)
  o=$(timeout -k 60 3600 nice -n 19 ionice -c3 "$PY" -I "$ADLER" "$SRC/$rel" 2>&1); rc=$?
  t1=$(date -u +%FT%TZ)
  o=$(printf '%s' "$o" | tr '\t\n' ' |')
  if [ $rc -eq 0 ] && [[ $o =~ ^([0-9a-f]{8})\ ([0-9]+)\ ([0-9]+)\ [0-9.]+\ (.*)$ ]] \
     && [ "${BASH_REMATCH[2]}" = "${BASH_REMATCH[3]}" ] && [ "${BASH_REMATCH[4]}" = "$SRC/$rel" ]; then
    line=$(printf '%s\t%s\tOK\t%s\t%s\t%s\t%s' "$rel" "${BASH_REMATCH[1]}" "$t0" "$t1" "$H" "$o")
  else
    line=$(printf '%s\t-\tERR\t%s\t%s\t%s\trc=%s %s' "$rel" "$t0" "$t1" "$H" "$rc" "$o")
  fi
  flock "$OUT.lock" sh -c 'printf "%s\n" "$1" >> "$2"' _ "$line" "$OUT"
}
export -f one

touch "$OUT"
flock "$OUT.lock" sh -c 'printf "#run-start\t%s\t%s\t%s\tstreams=%s\n" "$(date -u +%FT%TZ)" "$1" "$2" "$3" >> "$4"' _ "$H" "$$" "$NSTREAM" "$OUT"
# the to-do list: LIST minus every relpath that already has an OK row
awk -F'\t' 'NR==FNR { if ($3=="OK") done[$1]=1; next } !($0 in done) && $0 != ""' "$OUT" "$LIST" > "$OUT.todo"
xargs -a "$OUT.todo" -d '\n' -n 1 -P "$NSTREAM" bash -c 'one "$1"' _
rc=$?
flock "$OUT.lock" sh -c 'printf "#run-end\t%s\t%s\t%s\txargs_rc=%s\n" "$(date -u +%FT%TZ)" "$1" "$2" "$3" >> "$4"' _ "$H" "$$" "$rc" "$OUT"
