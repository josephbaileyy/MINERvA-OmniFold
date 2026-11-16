#!/bin/bash
# E96D under amendment 1 (M_A1 b438ab27): the declared readout, `ensemble_estimator_data.py analyze`
# (E96D-DECLARATION.md "Controls" and "The readout"; BINDING-1 ruling 5), on a login node at 0 node-h, from a
# /dev/shm copy of itself ($1), deleted at exit. It runs once: it refuses if $NEW/analysis exists.
# Writes only $NEW/analysis/ (the record, ANALYSIS.json or, on a failed control, ANALYSIS.STOP.json, and analyze.log),
# $NEW/logs/connect-analyze.log, $NEW/logs/e96d_a1_analyze.sh and $NEW/post-analyze.tar.gz.
# It never prints the record: only its name, size and sha256, and analyze's own one-line status (rc and the names of
# failed controls). The director reads the committed record once.
# Preconditions: log-full/DONE at the pin with 50 of 50 tasks ended and rc 0, no FAILED; the fence (our cov2d*, t2a*,
# e96data* or ll5d* jobs queued or running stop it, per the A1 fence-gap follow-up: ^ll5d, not ^ll5d_gate_); the
# deploy at M_A1, clean, with the module at 414f7d35. Stat-only atime readings of the three inputs before and after.
# No set -u.
SELF=$1
M=b438ab2710b2dcfd30238107187caa3628393b11
MOD_SHA=414f7d352560b1cd310666af8e363fe294fda6ebb13239309887cb96c5f0b33a
NEW=/pscratch/sd/j/josephrb/e96data-a1
D=$NEW/deploy
A=$NEW/analysis
EPROD=/pscratch/sd/j/josephrb/s5p-20260926/runs/s2/num/data/data_b-_j-.npz
DEF=$D/nd-unfolding/pv-ladder/readouts/h2_definition.json
DPROD=$D/docs/orchestration/state/measurement-paper/5d-community-20261024/fd/data-product/fd_data_product.json
[ -n "$SELF" ] && [ -f "$SELF" ] || exit 9
[ -d "$NEW/logs" ] && [ ! -e "$A" ] && [ ! -e "$NEW/post-analyze.tar.gz" ] || { echo "STOP: no logs dir, or an analysis exists"; rm -f -- "$SELF"; exit 9; }
LOG=$NEW/logs/connect-analyze.log
exec > >(tee -a "$LOG") 2>&1
finish() { echo "e96data analyze connect rc=$1"; date -u +%FT%TZ; rm -f -- "$SELF"; sleep 1; exit "$1"; }
atimes() {
  for f in /pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz /pscratch/sd/j/josephrb/s5c-20260924/runs/p2/bkg_dump.npz "$EPROD"; do
    echo "stat utc=$(date -u +%FT%TZ) $(stat -c 'atime=%X mtime=%Y size=%s %n' "$f")"
  done
}
echo "node $(hostname) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$NEW/logs/e96d_a1_analyze.sh"

echo "== the full run's receipts"
cat "$NEW/log-full/DONE" 2>/dev/null; echo
[ -s "$NEW/log-full/DONE" ] && [ ! -e "$NEW/log-full/FAILED" ] || { echo "STOP: no full DONE, or a FAILED"; finish 9; }
done_ok=$(awk -v m="$M" 'index($0, "\"mode\": \"full\"") && index($0, "\"tasks\": 50") && index($0, "\"ended\": 50") \
  && index($0, "\"rc\": 0") && index($0, "\"pin\": \"" m "\"") {print "yes"}' "$NEW/log-full/DONE")
echo "full DONE at the pin, 50 of 50, rc 0: ${done_ok:-no}"
[ "$done_ok" = yes ] || { echo "STOP: the full DONE"; finish 9; }

echo "== the fence (our cov2d*, t2a*, e96data* or ll5d* jobs stop it)"
squeue -u josephrb -h -o '%i|%j|%T|%M|%l' > "$NEW/logs/squeue-before-analyze.txt" 2>&1 || { echo "STOP: squeue failed"; finish 9; }
cat "$NEW/logs/squeue-before-analyze.txt"
hit=$(awk -F'|' '$2 ~ /^(cov2d|t2a|e96data|ll5d)/' "$NEW/logs/squeue-before-analyze.txt")
[ -z "$hit" ] || { echo "FENCE STOP:"; printf '%s\n' "$hit"; finish 9; }
echo "FENCE: pass"

echo "== the deploy"
[ "$(git -C "$D" rev-parse HEAD)" = "$M" ] || { echo "STOP: HEAD is not M_A1"; finish 9; }
n=$(git -C "$D" status --porcelain | wc -l); echo "HEAD $M; porcelain lines (ignored files excluded): $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy is not clean"; finish 9; }
h=$(sha256sum "$D/nd-unfolding/ensemble_estimator_data.py" | cut -d' ' -f1); echo "module sha256 $h"
[ "$h" = "$MOD_SHA" ] || { echo "STOP: the module is not 414f7d35"; finish 9; }

echo "== atime reading before (stat only)"; atimes
mkdir "$A" || { echo "STOP: mkdir $A"; finish 9; }
echo "== analyze ($(date -u +%FT%TZ))"
( cd "$D" && source "$D/setup_salloc_env.sh" > /dev/null 2>&1
  export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
  python3 -B nd-unfolding/ensemble_estimator_data.py analyze --runs "$NEW/runs" --e-product "$EPROD" \
    --definition "$DEF" --data-product "$DPROD" --out "$A/ANALYSIS.json" ) > "$A/analyze.log" 2>&1
rc=$?
echo "analyze rc=$rc ($(date -u +%FT%TZ))"
grep -E '^E96-DATA analysis ' "$A/analyze.log"
echo "analyze.log lines: $(wc -l < "$A/analyze.log")"
echo "== the record (name, size, sha256; not printed)"
ls "$A" | grep -E '^ANALYSIS(\.STOP)?\.json$' | while read -r f; do echo "$f size=$(stat -c %s "$A/$f") sha256=$(sha256sum "$A/$f" | cut -d' ' -f1)"; done
echo "== atime reading after (stat only)"; atimes
n=$(git -C "$D" status --porcelain | wc -l); echo "deploy porcelain lines after: $n"
( cd "$NEW" && tar czf post-analyze.tar.gz.tmp analysis logs/connect-analyze.log logs/e96d_a1_analyze.sh logs/squeue-before-analyze.txt \
  && mv post-analyze.tar.gz.tmp post-analyze.tar.gz ) || { echo "STOP: tar"; finish 9; }
sha256sum "$NEW/post-analyze.tar.gz"
[ "$n" -eq 0 ] || { echo "STOP: the deploy changed"; finish 9; }
finish "$rc"
