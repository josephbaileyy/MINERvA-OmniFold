#!/bin/bash
# OOFVC step 1A (OOFVC-DECLARATION.md section 2.5), on a login node, through oofvc_launch.sh. Writes only under $R.
#   pilot: a fresh lane root; a clean clone of the lane at TOOLC; the dump built in the archived MAT environment of
#          Test C (precharge-20261125/testC/build.sh, the same compiler, flags, headers and libraries); one array task
#          on 1L (the smallest MC playlist), -t 01:00:00
#   rest:  only after the pilot's task is COMPLETED with routing_disagree 0. The other eleven tasks' times are projected
#          as the pilot's elapsed time x (MC reco entries / 1L's), from precharge-20261125/file-counts.txt. If any
#          projection exceeds 1.75 h, nothing is submitted (a resized request goes back to the director). Otherwise
#          the eleven tasks go at -t 02:00:00
set -u
MODE=${2:-}; POST=${3:-}
R=/pscratch/sd/j/josephrb/oofvc-20261126-r2
TOOLC=__TOOL_COMMIT__
URL=https://github.com/josephbaileyy/MINERvA-OmniFold.git
SRC=/pscratch/sd/j/josephrb/ibuchi-evloop-20261123/src
MAN=/pscratch/sd/j/josephrb/ibuchi-evloop-20261123/manifests
ENVSH=/pscratch/sd/j/josephrb/MINERvA-OmniFold/setup_salloc_env.sh
O=$R/tool/2d-unfolding/oofvc
case "$TOOLC" in *__*) echo "STOP: the tool commit is not filled in"; exit 9;; esac
# fence check (RDX-BINDING-1's terms, as geanttw applied them): no live cov2d or t2a job, read from sacct (never
# squeue); a state outside the terminal set, or an empty one, counts as live
fence_check() {
  local since out live
  since=$(date -u -d '14 days ago' +%F) || { echo "STOP: date failed ($1)"; exit 2; }
  out=$(sacct -X -n -P -S "$since" -o JobID,JobName,State 2>&1) || { echo "STOP: sacct failed ($1)"; exit 2; }
  live=$(printf '%s\n' "$out" | awk -F'|' '$2 ~ /^(cov2d|t2a)/ { split($3, s, " ");
    if (s[1] !~ /^(COMPLETED|FAILED|CANCELLED|TIMEOUT|OUT_OF_MEMORY|NODE_FAIL|PREEMPTED|BOOT_FAIL|DEADLINE)$/) print }')
  [ -z "$live" ] || { echo "STOP: a fenced job is live ($1): $live"; exit 2; }
  echo "fence check ($1): no live cov2d or t2a job $(date -u +%FT%TZ)"
}

echo "node $(hostname) $(date -u +%FT%TZ) mode $MODE tool $TOOLC"
sq=$(squeue -h -u "$USER" -o '%j') || { echo "STOP: squeue failed"; exit 2; }
q=$(printf '%s\n' "$sq" | grep -c '^oofvc_' || true)
case "$MODE" in
  pilot)
    [ ! -e "$R" ] || { echo "STOP: $R exists"; exit 2; }
    [ "$q" = 0 ] || { echo "STOP: an oofvc job is queued"; exit 2; }
    # cov2d's condition (a): the first oofvc_dump job starts only after cov2d's LL5D atime-post, a UTC time the
    # director passes on; refused unless given, well formed and already past
    case "$POST" in [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9]Z) ;;
      *) echo "STOP: the LL5D atime-post time is missing or malformed: '$POST'"; exit 2;; esac
    [ "$(date -u -d "$POST" +%s 2>/dev/null || echo 0)" -gt 0 ] && [ "$(date -u -d "$POST" +%s)" -lt "$(date -u +%s)" ] \
      || { echo "STOP: the LL5D atime-post $POST is not yet past"; exit 2; }
    fence_check "pilot, before any write"
    mkdir -p "$R/logs" "$R/dump" "$R/gates" || exit 2
    echo "$POST" > "$R/gates/ll5d_atime_post.txt"
    git clone -q "$URL" "$R/tool" && git -C "$R/tool" -c advice.detachedHead=false checkout -q "$TOOLC" || exit 3
    [ "$(git -C "$R/tool" rev-parse HEAD)" = "$TOOLC" ] || { echo "STOP: tool HEAD"; exit 3; }
    [ -z "$(git -C "$R/tool" status --porcelain --ignored)" ] || { echo "STOP: tool clone not clean"; exit 3; }
    sha256sum "$MAN"/*_MC.txt > "$R/dump/manifests.sha256" || exit 4
    [ "$(wc -l < "$R/dump/manifests.sha256")" = 12 ] || { echo "STOP: not 12 MC manifests"; exit 4; }
    ( set +u; source "$ENVSH" >/dev/null
      "$CXX" -O2 -std=c++17 $(root-config --cflags) -I"$SRC" -I"$MINERVA_PREFIX/include" "$O/oofvc_dump.cpp" \
        -o "$R/dump/oofvc_dump" -L"$MINERVA_PREFIX/lib" -lMAT-MINERvA -lMAT $(root-config --libs) -lGeom -lGenVector \
    ) > "$R/logs/build.log" 2>&1 || { echo "STOP: build failed"; tail -20 "$R/logs/build.log"; exit 5; }
    (cd "$R/dump" && sha256sum oofvc_dump > built.sha256); cat "$R/dump/built.sha256"
    fence_check "pilot, before the submit"
    j=$(sbatch --parsable --array=7 -t 01:00:00 "$O/launch/dump_array.sbatch") || { echo "STOP: sbatch"; exit 6; }
    echo "$j" > "$R/logs/pilot.jobid"; echo "pilot job $j" ;;
  rest)
    [ -e "$R/logs/pilot.jobid" ] && [ ! -e "$R/logs/rest.jobid" ] || { echo "STOP: no pilot, or rest submitted"; exit 2; }
    [ "$q" = 0 ] || { echo "STOP: an oofvc job is queued"; exit 2; }
    [ -s "$R/gates/ll5d_atime_post.txt" ] || { echo "STOP: no LL5D atime-post record"; exit 2; }
    j=$(cat "$R/logs/pilot.jobid")
    line=$(sacct -X -n -P -j "${j}_7" -o State,ElapsedRaw)
    echo "pilot sacct: $line"
    [ "${line%%|*}" = COMPLETED ] || { echo "STOP: the pilot is not COMPLETED"; exit 7; }
    grep -q ' routing_disagree 0$' "$R/dump/1L.log" && [ -e "$R/dump/1L.done" ] || { echo "STOP: the pilot's routing"; exit 7; }
    el=${line##*|}
    FC=$R/tool/docs/orchestration/state/precharge-20261125/file-counts.txt
    np_=$(awk -F'[ ,]+' '/_MC.log:/ {split($1,a,"_"); n[a[1]]=1} END {c=0; for (p in n) c++; print c}' "$FC")
    [ "$np_" = 12 ] || { echo "STOP: file-counts.txt lists $np_ MC playlists, not 12"; exit 7; }
    for p in 1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P; do  # each playlist the array runs has a projection (codex-school r2 #5)
      [ "$(grep -c "^${p}_MC.log:" "$FC")" = 1 ] && grep -q "^${p}_MC.log:complete [0-9]* files, [0-9]* entries\$" "$FC" \
        || { echo "STOP: not exactly one complete entry count for $p"; exit 7; }  # codex-school r3 #4
    done
    proj=$(awk -v el="$el" -F'[ ,]+' '/_MC.log:/ {split($1,a,"_"); n[a[1]]=$(NF-1)} END {m=0; for (p in n) { t=el*n[p]/n["1L"]; printf "%s %.0f\n", p, t > "/dev/stderr"; if (t>m) m=t }; printf "%.0f", m}' "$FC")
    echo "largest projection ${proj} s"
    [ "$proj" -le 6300 ] || { echo "STOP: a projection exceeds 1.75 h; back to the director"; exit 7; }
    fence_check "rest, before the submit"
    j2=$(sbatch --parsable --array=0-6,8-11 -t 02:00:00 "$O/launch/dump_array.sbatch") || { echo "STOP: sbatch"; exit 6; }
    echo "$j2" > "$R/logs/rest.jobid"; echo "rest job $j2" ;;
  *) echo "STOP: mode $MODE"; exit 9 ;;
esac
