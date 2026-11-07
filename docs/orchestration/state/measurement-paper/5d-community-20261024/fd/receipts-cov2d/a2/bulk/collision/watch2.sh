#!/bin/bash
# Watch the cov2d jobs (the director's ruling of 2026-11-06 on G18_L, item 5). Exits on:
#   BAD-END        a cov2d attempt since the AR23 rerun ends in any state but COMPLETED, unless it is one of the four
#                  known pilot-label collisions AND it matches exactly: sacct ExitCode 1:0, every srun step COMPLETED
#                  0:0, every walls row run_rc 0, its log's "exists; not overwritten" labels equal to its expected set,
#                  no "[cov2d] <label> rc=" line (a run failure), and walls rows + skips = the job's runs-table rows;
#   FITS <job>     the independent recompute says job $2 (limit $3; default AR23_Tb 07:38:00) fits under the cap
#                  (a job given as info:<name> is priced and printed only, never an exit);
#   KNOWN-ALL-ENDED all four known jobs have ended and matched (the remedy can start); not in final mode;
#   ALL-ENDED      final mode ($4 = final): no cov2d attempt since the AR23 rerun is unended;
#   RECOMPUTE-ERROR.
S=$1; WJ=${2:-AR23_Tb}; WL=${3:-07:38:00}; MODE=${4:-}; M=a60547692df5f963e428cdfe4661fc51ab785b7b; D=$S/wavefetch/watch2; mkdir -p $D
O=/pscratch/sd/j/josephrb/cov2d-run-20261104
expect() {  # expect <id>: "<job>:<its colliding labels, sorted, comma-joined>", or nothing (bash 3.2: no assoc arrays)
  case "$1" in
    60895948) echo "G18_L:L_G18_BeamAngleX_0,X_G18" ;; 60895562) echo "G18_Ua:U_G18_Flux_0" ;;
    60895949) echo "G18_Ba:B_G18_001" ;; 60895956) echo "G18_Ta:T_G18_5720000" ;;
  esac
}
r() { ssh -o ControlPath=none saul.nersc.gov "ssh -o BatchMode=yes -o LogLevel=QUIET login02 bash -s"; }
verify() {  # verify <id>: prints MATCH or the reason it does not
  local id=$1 e; e=${EXPECT_OVERRIDE:-$(expect $1)}; local job=${e%%:*} want=${e#*:}
  r > $D/v-$id.txt 2>&1 <<EOF
echo "EXIT \$(sacct -X -n -P -j $id -o ExitCode)"
sacct -n -P -j $id -o JobID,State,ExitCode | awk -F'|' '\$1 ~ /\.[0-9]+\$/ && (\$2 != "COMPLETED" || \$3 != "0:0") {print "BADSTEP " \$0}'
awk -F'\t' '\$4 != 0 {print "BADWALL " \$0}' $O/walls.$job.*.tsv
echo "WALLS \$(cat $O/walls.$job.*.tsv | wc -l) ROWS \$(awk -F'\\t' -v j=$job 'NR > 1 && \$1 == j' $O/tables/runs_${job%%_*}.tsv | wc -l)"
echo "SKIPS \$(grep -oP '^\[cov2d\] \K\S+(?= exists; not overwritten)' $O/logs/cov2d-$job-$id.out | sort | paste -sd,)"
grep -E '^\[cov2d\] \S+ rc=' $O/logs/cov2d-$job-$id.out | sed 's/^/RUNFAIL /'
grep -E '^\[cov2d\] end ' $O/logs/cov2d-$job-$id.out | sed 's/^/END /'
EOF
  local why=""
  grep -qx "EXIT 1:0" $D/v-$id.txt || why="$why exit!=1:0;"
  grep -q '^BADSTEP\|^BADWALL\|^RUNFAIL' $D/v-$id.txt && why="$why a step/wall/run failed;"
  grep -qx "SKIPS $want" $D/v-$id.txt || why="$why skips!=$want;"
  grep -q '^END .* rc=1$' $D/v-$id.txt || why="$why no end rc=1;"
  local w n; read -r w n <<< "$(awk '$1 == "WALLS" {print $2, $4}' $D/v-$id.txt)"
  [ -n "$w" ] && [ "$((w + $(echo "$want" | tr ',' '\n' | wc -l)))" = "$n" ] || why="$why walls+skips!=rows ($w,$n);"
  [ -z "$why" ] && echo MATCH || echo "$why"
}
touch $D/known.txt
for i in $(seq 1 80); do
  { echo 'sacct -X -n -P -S 2026-11-04 -u josephrb -o JobID,JobName,State,ElapsedRaw,NNodes,TimelimitRaw'; } | r > $D/s.psv 2>/dev/null \
    && echo "cat $O/submissions.log" | r > $D/sub.log 2>/dev/null || { echo "$(date -u +%FT%TZ) fetch failed"; sleep 600; continue; }
  bad=""
  for row in $(awk -F'|' '$2 ~ /^cov2d-/ && $1 > 60889690 && $3 !~ /^(PENDING|RUNNING|COMPLETED|COMPLETING|CONFIGURING)/ {print $1 "|" $3}' $D/s.psv | tr ' ' '_'); do
    id=${row%%|*}
    grep -qx "$id" $D/known.txt && continue
    if [ -n "$(expect $id)" ] && [ "${row#*|}" = FAILED ]; then
      v=$(verify $id)
      if [ "$v" = MATCH ]; then echo "$id" >> $D/known.txt; echo "$(date -u +%FT%TZ) known collision $id ($(expect $id)) MATCH"; continue; fi
      bad="$bad $row [$v]"
    else
      bad="$bad $row"
    fi
  done
  st=$(awk -F'|' '$2 ~ /^cov2d-/ && $1 > 60889690 {split($3,a," "); n[a[1]]++} END {for (k in n) printf "%s=%d ", k, n[k]}' $D/s.psv)
  rec=$(PYTHONDONTWRITEBYTECODE=1 python3 -I -B $S/wt-wave/cov2d_cap.py --sacct $D/s.psv --submissions $D/sub.log --M $M --limit $WL); rc=$?
  echo "$(date -u +%FT%TZ) $st| known=$(wc -l < $D/known.txt) | $WJ($WL): rc=$rc $(echo "$rec" | python3 -c 'import sys,json; r=json.load(sys.stdin); print("total=%.2f unlisted=%s" % (r["total"], r["unlisted_ids"]))' 2>&1)"
  [ -n "$bad" ] && { echo "BAD-END$bad"; exit 0; }
  [ "$rc" = 0 ] && [ "${WJ#info:}" = "$WJ" ] && { echo "FITS $WJ"; exit 0; }
  [ "$rc" = 2 ] && { echo "RECOMPUTE-ERROR $rec"; exit 0; }
  [ "$MODE" != final ] && [ "$(wc -l < $D/known.txt)" -ge 4 ] && { echo "KNOWN-ALL-ENDED"; exit 0; }
  [ "$MODE" = final ] && ! awk -F'|' '$2 ~ /^cov2d-/ && $1 > 60889690 && $3 ~ /^(PENDING|RUNNING|COMPLETING|CONFIGURING|REQUEUED|SUSPENDED)/' $D/s.psv | grep -q . && { echo "ALL-ENDED"; exit 0; }
  sleep 900
done
echo "watch expired"
