#!/bin/bash
# COV2D connect WAVE: A2's sequence, stage 4 (COV2D-BINDING-2.md, addendum A2, revision 2): the rest of the bulk, the
# 14 jobs after the eight universe jobs, in the amendment's waves (COV2D-AMENDMENT-1.md §5: a job the cap cannot take
# yet waits for earlier jobs to end; that is a wait, not a STOP). Relaunched for each wave: a job already submitted at
# M is skipped. Under the director's ruling on the gate's sacct lag (2026-11-06), with no change to A2's code:
#   1. one job per cov2d_submit.sh call;
#   2. before each next call, sacct must list the previous job's id: polled every 10 s, refused after 10 minutes;
#   3. before each submission, the gate's total (cov2d_jobs.py gate) and an independent recompute (cov2d_cap.py: sacct
#      plus the submissions.log ids at M that sacct does not list yet) on the same sacct snapshot, both printed. The
#      stricter governs: either over the cap ends the wave;
#   4. cov2d_cap.py's companion test (test_cov2d_cap.py) runs first, under the login node's python3, or nothing is
#      submitted.
# The three files sit in $W. Before the companion test the connect compares, in this log (the auditor's B1):
# cov2d_cap.py and test_cov2d_cap.py against the literals below, and itself ($0) against the sha256 the launch passes
# as $1 (a script cannot hold its own digest), refusing on any mismatch. Any other refusal stops the connect. This
# log is fetched for the receipt, then it and $W are removed (logged).
# Run on login02: setsid nohup bash /dev/shm/josephrb-cov2d-wave/connect-wave.sh <its sha256> >/dev/null 2>&1 </dev/null &
M=a60547692df5f963e428cdfe4661fc51ab785b7b
C=/pscratch/sd/j/josephrb/cov2d-deploy-a6054769
W=/dev/shm/josephrb-cov2d-wave
LOG=/dev/shm/josephrb-cov2d-wave.log
JOBS="G18_L G18_Ba G18_Bb G18_Bc G18_Ta G18_Tb G18_Tc AR23_L AR23_Ba AR23_Bb AR23_Bc AR23_Ta AR23_Tb AR23_Tc"
WAIT_POLL=10; WAIT_TRIES=60
CAP_SHA=1ce76ea373f474e7c32520c69fbc90eae9419d5cbd901927df5a41fbe6973c5e
TEST_SHA=7a07c3acf7f361f1af89276064bc64c8ab60e4d6bc06c658f2dcd10422f9c324
WANT_SELF=$1
[ -e "$LOG" ] && { echo "REFUSED $LOG exists"; exit 2; }
exec >> "$LOG" 2>&1
echo "host=$(hostname) start=$(date -u +%FT%TZ) pid=$$ user=$(id -un)"
[ "$(git -C "$C" rev-parse HEAD)" = "$M" ] || { echo "REFUSED the deploy is not at M"; echo DONE; exit 2; }
echo "deploy=$C head=$(git -C "$C" rev-parse HEAD) plain=$(git -C "$C" status --porcelain | wc -l) ignored=$(git -C "$C" status --porcelain --ignored | wc -l)"
[ -z "$(git -C "$C" status --porcelain --ignored)" ] || { git -C "$C" status --porcelain --ignored | head; echo "REFUSED the deploy is not clean (--ignored)"; echo DONE; exit 2; }
self=$(sha256sum "$0" | cut -c1-64); cap=$(sha256sum "$W/cov2d_cap.py" | cut -c1-64); tst=$(sha256sum "$W/test_cov2d_cap.py" | cut -c1-64)
echo "sha256 $0=$self want=${WANT_SELF:-(none)}"
echo "sha256 $W/cov2d_cap.py=$cap want=$CAP_SHA"
echo "sha256 $W/test_cov2d_cap.py=$tst want=$TEST_SHA"
[ -n "$WANT_SELF" ] && [ "$self" = "$WANT_SELF" ] && [ "$cap" = "$CAP_SHA" ] && [ "$tst" = "$TEST_SHA" ] \
    || { echo "REFUSED a file's sha256 is not the reviewed one"; echo DONE; exit 2; }
echo "DIGESTS_MATCH"
(cd "$W" && PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B -m unittest test_cov2d_cap > "$W/test.out" 2>&1); trc=$?
echo "companion test ($(/usr/bin/python3 -V 2>&1)) rc=$trc: $(tail -1 "$W/test.out")"
[ "$trc" = 0 ] || { cat "$W/test.out"; echo "REFUSED the companion test failed"; echo DONE; exit 2; }
source "$C/2d-unfolding/cov2d/jobs/cov2d_env.sh"
git -C "$C" fetch -q origin main || { echo "REFUSED fetch"; echo DONE; exit 2; }
echo "origin/main=$(git -C "$C" rev-parse origin/main)"
prev=""
for job in $JOBS; do
    grep -qE "M=$M job=$job id=" "$O/submissions.log" && { echo "skip $job: already submitted at M"; continue; }
    truth=${job%%_*}
    if [ -n "$prev" ]; then
        k=0
        until sacct -X -n -P -j "$prev" -o JobID | grep -qx "$prev"; do
            k=$((k + 1)); [ "$k" -le "$WAIT_TRIES" ] || { echo "REFUSED sacct did not list $prev within $((WAIT_POLL * WAIT_TRIES)) s"; break 2; }
            sleep "$WAIT_POLL"
        done
        echo "sacct lists $prev after $k polls of $WAIT_POLL s"
    fi
    lim=$(awk -F'\t' -v j="$job" 'NR > 1 && $1 == j {print $7}' "$O/tables/jobs_$truth.tsv")
    [ -n "$lim" ] || { echo "REFUSED $job is not a jobs_$truth.tsv row"; break; }
    sacct -X -n -P -S 2026-11-04 -u "$(id -un)" -o JobID,JobName,State,ElapsedRaw,NNodes,TimelimitRaw > "$W/s.psv" \
        || { echo "REFUSED sacct"; break; }
    g=$("$PY310" -B "$CJ" gate --sacct "$W/s.psv" --tables "$O/tables" --want "$job" 2>&1); grc=$?
    k2=$(/usr/bin/python3 -I -B "$W/cov2d_cap.py" --sacct "$W/s.psv" --submissions "$O/submissions.log" --M "$M" --limit "$lim" 2>&1); crc=$?
    echo "TOTALS $job limit=$lim gate(rc=$grc)=$g connect(rc=$crc)=$k2"
    { [ "$grc" = 0 ] || [ "$grc" = 3 ]; } && { [ "$crc" = 0 ] || [ "$crc" = 3 ]; } \
        || { echo "REFUSED $job: a total could not be computed"; break; }
    if [ "$grc" = 3 ] || [ "$crc" = 3 ]; then
        echo "WAVE-END at $job: over the cap of 165.8 (gate rc=$grc, connect rc=$crc); it waits for earlier jobs to end"
        break
    fi
    bash "$C/2d-unfolding/cov2d/jobs/cov2d_submit.sh" "$C" "$M" "$truth" "$job"; src=$?
    echo "submit $job rc=$src"
    [ "$src" = 0 ] || { echo "REFUSED $job: cov2d_submit.sh rc=$src"; break; }
    prev=$(awk -v m="M=$M" -v j="job=$job" '$2 == m && $3 == j {for (i = 1; i <= NF; i++) if ($i ~ /^id=/) print substr($i, 4)}' "$O/submissions.log" | tail -1)
    [ -n "$prev" ] || { echo "REFUSED $job: no id in submissions.log"; break; }
done
rm -f "$W/s.psv"
echo "plain-after=$(git -C "$C" status --porcelain | wc -l) ignored-after=$(git -C "$C" status --porcelain --ignored | wc -l)"
tail -16 "$O/submissions.log"
for id in $(awk -v m="M=$M" '$2 == m && $3 ~ /^job=(G18|AR23)_(L|B|T)/ {for (i = 1; i <= NF; i++) if ($i ~ /^id=/) print substr($i, 4)}' "$O/submissions.log"); do
    scontrol show job "$id" 2>/dev/null | grep -E "JobId|QOS|TimeLimit|NumNodes|JobState" | tr -s ' \n' ' '; echo
done
echo "end=$(date -u +%FT%TZ)"; echo DONE
