#!/bin/bash
# Tests the completion job's lane-step guard (running_lane_steps, between the ">>> lane-step guard" markers of
# refc2c1_completion_job.sbatch), in both directions.
#   bash test_lane_step_guard.sh <job.sbatch> <fixtures dir>          fixture cases (any host)
#   bash test_lane_step_guard.sh <job.sbatch> <fixtures dir> --live   also live cases: read-only scontrol/sacct on the
#                                                                     lane's own running jobs (needs a Slurm login node)
# The fixtures are real `scontrol -o show step <job>` outputs, each captured beside the job's sacct.
# Prints one line per case and "N passed, M failed"; exits 1 on any failure.
JOB=${1:?job script}; FX=${2:?fixtures dir}; LIVE=$3
eval "$(sed -n '/^# >>> lane-step guard$/,/^# <<< lane-step guard$/p' "$JOB")"
type running_lane_steps > /dev/null 2>&1 || { echo "no running_lane_steps in $JOB"; exit 1; }
pass=0; fail=0
# case <label> <expect: silent|fires> <job> <expected-count> <input file> <indices...>
case_() {
  local label=$1 want=$2 job=$3 nexp=$4 f=$5; shift 5
  local got; got=$(running_lane_steps "$job" "$@" < "$f")
  local verdict=silent; [ "$got" -ne "$nexp" ] && verdict=fires
  if [ "$verdict" = "$want" ]; then pass=$((pass + 1)); r=ok; else fail=$((fail + 1)); r=FAIL; fi
  echo "$r  $label: counted $got of $nexp expected -> $verdict (want $want)"
}
A=$FX/scontrol-o-show-step-60895985.txt      # .8-.11 RUNNING (sacct-60895985.txt)
B=$FX/scontrol-o-show-step-60895983.txt      # .3, .4 RUNNING; .0-.2 COMPLETED and absent
T=$(mktemp -d "${TMPDIR:-/tmp}/lsg.XXXXXX")
grep -E 'StepId=[0-9]+\.(batch|extern) ' "$A" > "$T/batch-extern-only.txt"
cat "$A" "$A" > "$T/duplicated.txt"
sed 's/State=RUNNING/State=COMPLETING/' "$A" > "$T/completing.txt"
: > "$T/empty.txt"
case_ "4 running, expect 4"                    silent 60895985 4 "$A" 8 9 10 11
case_ "4 running, expect 5 (one more)"         fires  60895985 5 "$A" 8 9 10 11 12
case_ "2 running, expect 2"                    silent 60895983 2 "$B" 3 4
case_ "2 running, expect 3 (a COMPLETED step)" fires  60895983 3 "$B" 2 3 4
case_ "batch/extern only, expect 4"            fires  60895985 4 "$T/batch-extern-only.txt" 0 1 2 3
case_ "lanes 0-3 of a job running .8-.11"      fires  60895985 4 "$A" 0 1 2 3
case_ "index 1 does not match .10/.11"         fires  60895985 1 "$A" 1
case_ "job-id prefix 6089598 matches nothing"  fires  6089598  4 "$A" 8 9 10 11
case_ "each step counted once (duplicated)"    silent 60895985 4 "$T/duplicated.txt" 8 9 10 11
case_ "State=COMPLETING is not RUNNING"        fires  60895985 4 "$T/completing.txt" 8 9 10 11
case_ "empty scontrol output"                  fires  60895985 4 "$T/empty.txt" 0 1 2 3
if [ "$LIVE" = --live ]; then
  echo "live, $(date -u +%FT%TZ), $(hostname):"
  for j in $(squeue -u "$USER" -h -t R -o %i | head -4); do
    scontrol -o show step "$j" > "$T/live-$j.txt" 2>&1
    ids=$(sacct -j "$j" -n -P -o JobID,State | sed -n "s/^$j\.\([0-9][0-9]*\)|RUNNING$/\1/p" | tr '\n' ' ')
    done_ids=$(sacct -j "$j" -n -P -o JobID,State | sed -n "s/^$j\.\([0-9][0-9]*\)|COMPLETED$/\1/p" | tr '\n' ' ')
    n=$(echo $ids | wc -w); [ "$n" -gt 0 ] || { echo "skip $j: sacct shows no RUNNING step"; continue; }
    case_ "live $j, sacct RUNNING [$ids]"        silent "$j" "$n" "$T/live-$j.txt" $ids
    case_ "live $j, one more (index 999)"        fires  "$j" $((n + 1)) "$T/live-$j.txt" $ids 999
    [ -n "$done_ids" ] && case_ "live $j, its COMPLETED [$done_ids]" fires "$j" $(echo $done_ids | wc -w) "$T/live-$j.txt" $done_ids
  done
fi
rm -rf "$T"
echo "$pass passed, $fail failed"
[ "$fail" -eq 0 ]
