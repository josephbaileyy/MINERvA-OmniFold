#!/bin/bash
# PTMC's login-node and DTN steps (PTMC-DECLARATION.md sections 1, 2.3 and 7; the director's binding rulings), run
# through ptmc_launch.sh as `bash <self> <self> MODE`, each on its own GO. Writes only under $R. Every gate fails
# closed: a failed command or an unexpected state is a STOP (exit 2-9), never an empty pass. Every phase is claimed
# atomically (mkdir) before it acts, so a second invocation refuses. Every non-compute step runs with one thread.
#   setup       (login) fence; $R new; the tool clone at TOOLC; the deploy tree (make_tree.sh, clone); its exact
#               digest inventory; the driver's and libRooUnfold's pins
#   prestage    (login) the fence for the copies, recorded with its time (repeatable until stage is claimed)
#   stage       (dtn01, the declaration's DTN copy) within 15 minutes of prestage: the O_NOATIME copies of CV and MC
#               (CFS) and of r3's rows and join record, each re-hashed against its pin; nothing else
#   pilot       (login) fence; the stage and deploy re-checked; submit pilot.sbatch on exactly 2 nodes
#   post-pilot  (login) the pilot's sacct, then ptmc_pilot_post.py; PROCEED only if every rule of section 7 passes
#   replicas    (login) PROCEED re-derived from fresh accounting (the same L); fence; submit -N 5 -t L replicas.sbatch
#   post        (login) sacct of each PTMC job, the charge, the D4 staging (ptmc_stage_d4.py), the two tars
set -u -o pipefail
export LC_ALL=C OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
umask 077
MODE=${2:-}
R=/pscratch/sd/j/josephrb/ptmc-20261128
TOOLC=ace6e5552c3b822dabedc22b16be5de1b04a0d68
DRIVER_SHA=b5c1c9f0cca0670bd33ca1000a42ecf6efcc7a2cdb47f14bc72b5f11d7ea4e55
URL=https://github.com/josephbaileyy/MINERvA-OmniFold.git
CV_SRC=/global/cfs/cdirs/m3246/josephrb/two-d-followup-20261010/xr-input/runEventLoopOmniFold_MEFHC.root
MC_SRC=/global/cfs/cdirs/m3246/josephrb/minerva-shutdown-stage/fig_products/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root
ROWS_SRC=/pscratch/sd/j/josephrb/oofvc-20261126-r3/stage/oofvc_rows.npz
JOIN_SRC=/pscratch/sd/j/josephrb/oofvc-20261126-r3/join/join.json
CV_SHA=43f8cc16ab2688200d3e2e0ebb48012b23ada6d7882b8c68ecfc51c609aeb8df
MC_SHA=d40aea69235cdc98644e1bb3e622e579d6b81904c004c83fe50465079989f316
ROWS_SHA=cbf34bd8cad0f4978dc1aea22713eb5057bf521118dc7ce8d10b93b30defcb03
JOIN_SHA=13674f6d0c12bbb7c7ba133346940976bada2c765585ecb4e78593ec63521a4b
LIB=/pscratch/sd/j/josephrb/MINERvA-OmniFold/unbinned_unfolding/build/libRooUnfold.so
LIB_SHA=0b34e1e39102b0dddc5923dad7f69e59c70cd6a2fcbcef07728b72cf2933fefd
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
CONDA_HOOK=/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda
DEPLOY_FILES="2d-unfolding/re2/re2_driver.py 2d-unfolding/ref_c2c1/config.json 2d-unfolding/ref_c2c1/ref_c2c1.py
2d-unfolding/ref_c2c1/ref_c2c1_read.py unbinned_unfolding/python/omnifold.py 2d-unfolding/compare_to_paper_fullcov.py
2d-unfolding/uq/reported_cells.py 2d-unfolding/oofvc/oofvc_lib.py"
O=$R/tool/2d-unfolding/ptmc
PILOT_MIN=60  # the pilot's time limit, given on the command line and checked by pilot.sbatch
stop() { echo "STOP: $*"; exit "${STOP_RC:-7}"; }
now() { date -u +%FT%TZ; }
case "$TOOLC$DRIVER_SHA" in *__*) stop "a pin is not filled in";; esac
case "$MODE" in setup|prestage|stage|pilot|post-pilot|replicas|post) ;; *) stop "mode '$MODE'";; esac
me=$(id -un) || stop "id failed"
[ "$me" = josephrb ] || stop "user"
host=$(hostname) || stop "hostname failed"
case "$MODE:$host" in stage:dtn*) ;; stage:*) stop "stage runs on a DTN, not $host";; *:dtn*) stop "$MODE runs on a login node";; esac
echo "node $host $(now) mode $MODE tool $TOOLC"

# fence: no live cov2d or t2a job (sacct, never squeue; a state outside the terminal set, or an empty one, is live)
fence_check() {
  local since out live
  since=$(date -u -d '14 days ago' +%F) || stop "date failed ($1)"
  out=$(sacct -X -n -P -S "$since" -o JobID,JobName,State 2>&1) || stop "sacct failed ($1)"
  live=$(printf '%s\n' "$out" | awk -F'|' '$2 ~ /^(cov2d|t2a)/ { split($3, s, " ");
    if (s[1] !~ /^(COMPLETED|FAILED|CANCELLED|TIMEOUT|OUT_OF_MEMORY|NODE_FAIL|PREEMPTED|BOOT_FAIL|DEADLINE)$/) print }') \
    || stop "awk failed ($1)"
  [ -z "$live" ] || stop "a fenced job is live ($1): $live"
  echo "fence check ($1): no live cov2d or t2a job $(now)"
}
no_ptmc_job() {
  local sq n
  sq=$(squeue -h -u "$USER" -o '%j') || stop "squeue failed"
  n=$(printf '%s\n' "$sq" | grep -c '^ptmc_') ; [ "$?" -le 1 ] || stop "grep failed"
  [ "$n" = 0 ] || stop "a ptmc job is queued or running"
}
claim() { mkdir "$R/claims/$1" 2>/dev/null || stop "phase $1 is already claimed (a second invocation, or it ran)"; }
stage_empty() { local st; st=$(ls -A "$R/stage") || stop "ls of the stage failed"; [ -z "$st" ] || stop "the stage is not empty"; }
sha_of() { local h; h=$(sha256sum < "$1" | cut -d' ' -f1) || return 1; [ ${#h} = 64 ] || return 1; echo "$h"; }
tool_ok() {
  local head st
  head=$(git -C "$R/tool" rev-parse HEAD) || stop "git rev-parse failed"
  [ "$head" = "$TOOLC" ] || stop "the tool clone is not at $TOOLC"
  st=$(git -C "$R/tool" status --porcelain --ignored) || stop "git status failed"
  [ -z "$st" ] || stop "the tool clone is not clean"
}
deploy_ok() {
  local want have
  want=$(printf '%s\n' $DEPLOY_FILES | sort) || stop "inventory"
  have=$(cut -c67- "$R/logs/deploy.sha256" | sort) || stop "deploy.sha256 unreadable"
  [ "$have" = "$want" ] || stop "the deploy digests do not list exactly the declared files"
  (cd "$R/deploy" && sha256sum -c --quiet "$R/logs/deploy.sha256") || stop "the deploy tree differs from its digests"
  [ "$(grep ' 2d-unfolding/re2/re2_driver.py$' "$R/logs/deploy.sha256" | cut -c1-64)" = "$DRIVER_SHA" ] \
    || stop "the deployed driver is not $DRIVER_SHA"
}
stage_ok() {
  [ -e "$R/stage/ready" ] || stop "the stage is not ready"
  local f h
  for f in "runEventLoopOmniFold_MEFHC.root:$CV_SHA" "runEventLoopMC_MEFHC.root:$MC_SHA" "oofvc_rows.npz:$ROWS_SHA" \
           "join.json:$JOIN_SHA"; do
    h=$(sha_of "$R/stage/${f%%:*}") || stop "sha256 of ${f%%:*} failed"
    [ "$h" = "${f#*:}" ] || stop "the staged ${f%%:*} differs from its pin"
  done
  [ "$(cat "$R/stage/rows.sha256")" = "$ROWS_SHA" ] || stop "rows.sha256"
}
copy_noatime() {  # copy_noatime SRC DEST PIN: one O_NOATIME read, then the copy re-hashed against the pin
  local h st
  [ -f "$1" ] && [ ! -L "$1" ] || stop "$1 is absent or a symlink"
  [ ! -e "$2" ] || stop "$2 exists"
  st=$(stat -c '%n|atime=%x' "$1") && [ -n "$st" ] || stop "stat $1 (before the copy)"
  echo "pre  $st"
  dd iflag=noatime if="$1" of="$2" bs=16M status=none || stop "dd $1"
  st=$(stat -c '%n|atime=%x' "$1") && [ -n "$st" ] || stop "stat $1 (after the copy)"
  echo "post $st"
  h=$(sha_of "$2") || stop "sha256 of $2 failed"
  [ "$h" = "$3" ] || stop "the copy of $1 is not $3"
  chmod a-w "$2" || stop "chmod $2"
  echo "copied $(basename "$2") $3"
}
activate() { eval "$("$CONDA_HOOK" shell.bash hook)" && conda activate "$HOME/.conda/envs/root_6_28" || stop "conda activate"; }
submitted() {  # submitted NAME JOBID: persist the job id; a failure prints it and STOPs (the job exists)
  case "$2" in *[!0-9]*|'') stop "sbatch printed '$2'";; esac
  echo "$2" > "$R/logs/$1.jobid" || stop "the $1 job $2 was submitted but its id could not be recorded"
  echo "$1 job $2 $(now)"
}
pilot_sacct() {  # pilot_sacct FILE: the pilot's accounting, non-empty, from a successful sacct
  local j out
  j=$(cat "$R/logs/pilot.jobid") || stop "no pilot job id"
  case "$j" in *[!0-9]*|'') stop "pilot job id '$j'";; esac
  out=$(TZ=UTC sacct -j "$j" -n -P -o JobID,JobName,State,ExitCode,ElapsedRaw,NNodes,Start,End) || stop "sacct failed"
  [ -n "$out" ] || stop "sacct returned nothing for job $j"
  printf '%s\n' "$out" > "$1" || stop "write $1"
  echo "$j"
}

case "$MODE" in
setup)
  fence_check "before setup"
  no_ptmc_job
  [ ! -e "$R" ] || stop "$R exists"
  mkdir -p "$R/logs" "$R/stage" "$R/claims" || stop "mkdir"
  claim setup
  git clone -q "$URL" "$R/tool" > "$R/logs/clone.log" 2>&1 || stop "git clone"
  git -C "$R/tool" -c advice.detachedHead=false checkout -q "$TOOLC" || stop "checkout $TOOLC"
  tool_ok
  PTMC_PY=$PY nice -n 19 bash "$O/make_tree.sh" "$R/deploy" clone "$URL" "$R/stage" > "$R/logs/deploy.log" 2>&1 \
    || { cat "$R/logs/deploy.log"; stop "make_tree"; }
  cat "$R/logs/deploy.log"
  (cd "$R/deploy" && sha256sum $DEPLOY_FILES) > "$R/logs/deploy.sha256" || stop "deploy digests"
  deploy_ok
  h=$(sha_of "$LIB") || stop "sha256 of libRooUnfold.so failed"
  [ "$h" = "$LIB_SHA" ] || stop "libRooUnfold.so differs from its pin"
  echo "libRooUnfold.so $LIB_SHA"
  date -u +%FT%T > "$R/logs/setup.done" || stop "setup.done"  # the window post counts replica allocations from
  echo "setup done $(now)" ;;
prestage)  # repeatable until stage is claimed: a stale fence is refreshed, never reused
  [ -e "$R/logs/setup.done" ] || stop "setup has not run"
  [ ! -e "$R/claims/stage" ] || stop "stage is claimed"
  stage_empty
  fence_check "before the DTN copies (the CV is cov2d-protected; O_NOATIME)"
  e=$(date -u +%s) || stop "date"
  echo "$e" > "$R/logs/prestage.epoch" || stop "prestage.epoch"
  echo "$e $host" >> "$R/logs/prestage.record" || stop "prestage.record"
  echo "prestage done $(now)" ;;
stage)
  [ -e "$R/logs/setup.done" ] && [ -e "$R/logs/prestage.epoch" ] || stop "setup or prestage has not run"
  t0=$(cat "$R/logs/prestage.epoch") || stop "prestage.epoch"
  case "$t0" in *[!0-9]*|'') stop "prestage.epoch '$t0'";; esac
  t1=$(date -u +%s) || stop "date"
  [ $((t1 - t0)) -ge 0 ] && [ $((t1 - t0)) -le 900 ] || stop "the prestage fence is $((t1 - t0)) s old (limit 900)"
  stage_empty
  claim stage
  copy_noatime "$CV_SRC" "$R/stage/runEventLoopOmniFold_MEFHC.root" "$CV_SHA"
  copy_noatime "$MC_SRC" "$R/stage/runEventLoopMC_MEFHC.root" "$MC_SHA"
  copy_noatime "$ROWS_SRC" "$R/stage/oofvc_rows.npz" "$ROWS_SHA"
  copy_noatime "$JOIN_SRC" "$R/stage/join.json" "$JOIN_SHA"
  echo "$ROWS_SHA" > "$R/stage/rows.sha256" || stop "rows.sha256"
  touch "$R/stage/ready" || stop "ready"
  echo "stage done $(now)" ;;
pilot)
  tool_ok; deploy_ok; stage_ok
  [ ! -e "$R/logs/pilot.jobid" ] && [ ! -e "$R/units" ] || stop "the pilot has been submitted"
  no_ptmc_job
  fence_check "before the pilot's submit"
  claim pilot
  j=$(sbatch --parsable -N 2 -t "$PILOT_MIN" "$O/launch/pilot.sbatch") || stop "sbatch"
  submitted pilot "$j" ;;
post-pilot)
  tool_ok
  [ -e "$R/logs/pilot.jobid" ] || stop "no pilot job"
  [ ! -e "$R/pilot-post" ] || stop "post-pilot has run"
  no_ptmc_job
  claim post-pilot
  mkdir "$R/pilot-post" || stop "mkdir"
  j=$(pilot_sacct "$R/pilot-post/sacct.txt") || { r=$?; echo "$j"; exit $r; }
  cat "$R/pilot-post/sacct.txt"
  activate
  nice -n 19 "$PY" -B "$O/launch/ptmc_pilot_post.py" --sacct "$R/pilot-post/sacct.txt" --jobid "$j" \
    --units "$R/units" --rows "$R/stage/oofvc_rows.npz" --lib-sha "$LIB_SHA" --out "$R/pilot-post" ; r=$?
  if [ -e "$R/pilot-post/decision.json" ]; then
    cat "$R/pilot-post/decision.json" || stop "printing the decision (the C-SUPPORT table) failed"
  fi
  [ "$r" = 0 ] || STOP_RC=6 stop "the pilot's post did not PROCEED (rc $r)"
  [ -e "$R/pilot-post/PROCEED" ] || stop "no PROCEED file"
  echo "post-pilot PROCEED $(now)" ;;
replicas)
  tool_ok; deploy_ok; stage_ok
  [ -e "$R/pilot-post/PROCEED" ] || stop "no PROCEED"
  [ ! -e "$R/logs/replicas.jobid" ] || stop "the replicas have been submitted"
  L=$(cat "$R/pilot-post/time_limit_minutes") || stop "no time limit"
  case "$L" in ''|*[!0-9]*) stop "time limit '$L'";; esac
  [ "$L" -ge 1 ] && [ "$L" -le 600 ] || stop "time limit $L minutes is outside 1..600"
  no_ptmc_job
  fence_check "before the replicas' claim"
  claim replicas
  mkdir "$R/replicas-check" || stop "mkdir"
  j=$(pilot_sacct "$R/replicas-check/sacct.txt") || { r=$?; echo "$j"; exit $r; }
  activate
  chk=$(nice -n 19 "$PY" -B "$O/launch/ptmc_pilot_post.py" --sacct "$R/replicas-check/sacct.txt" --jobid "$j" \
    --units "$R/units" --rows "$R/stage/oofvc_rows.npz" --lib-sha "$LIB_SHA" --out "$R/replicas-check" \
    --recheck "$R/pilot-post/decision.json") || STOP_RC=6 stop "the recheck does not give the same PROCEED and L: $chk"
  echo "recheck $chk"
  printf '%s' "$chk" | grep -q "\"time_limit_minutes\": $L}" || stop "the recheck's L is not $L"
  printf '%s\n' "$chk" > "$R/replicas-check/recheck.json" || stop "recording the recheck"  # replicas.sbatch reads it (B1)
  fence_check "before the replicas' submit"
  j=$(sbatch --parsable -N 5 -t "$L" "$O/launch/replicas.sbatch") || stop "sbatch"
  submitted replicas "$j"
  echo "-t $L minutes, -N 5" ;;
post)
  tool_ok
  [ ! -e "$R/post" ] && [ ! -e "$R/post.tar.gz" ] && [ ! -e "$R/d4" ] || stop "post has run"
  [ -e "$R/logs/pilot.jobid" ] && [ -e "$R/logs/replicas.jobid" ] || stop "a PTMC job id is missing"
  no_ptmc_job
  claim post
  mkdir "$R/post" || stop "mkdir"
  : > "$R/post/sacct.txt" || stop "sacct.txt"
  jp=$(cat "$R/logs/pilot.jobid") && jr=$(cat "$R/logs/replicas.jobid") || stop "a job id is unreadable"
  [ "$jp" != "$jr" ] || stop "the pilot and replicas job ids are both '$jp'"
  for f in pilot replicas; do
    j=$(cat "$R/logs/$f.jobid") || stop "$f job id"
    case "$j" in *[!0-9]*|'') stop "$f job id '$j'";; esac
    case "$f" in pilot) jn=ptmc_pilot; nn=2;; replicas) jn=ptmc_reps; nn=5;; esac
    out=$(TZ=UTC sacct -j "$j" -n -P -o JobID,JobName,State,ExitCode,ElapsedRaw,NNodes,Start,End) || stop "sacct $f"
    [ -n "$out" ] || stop "sacct returned nothing for the $f job $j"
    printf '%s\n' "$out" | awk -F'|' -v j="$j" '{split($1, a, "."); if ((a[1] "") != (j "")) bad = 1} END {exit bad}' \
      || stop "sacct for the $f job $j has a row of another job"
    printf '%s\n' "$out" | grep -q "^$j|" || stop "sacct has no allocation line for the $f job $j"
    printf '%s\n' "$out" | awk -F'|' -v j="$j" -v n="$jn" -v nn="$nn" '($1 "") == (j "") {c++; if ($2 != n || $6 != nn) bad = 1}
      END {exit (c != 1 || bad)}' || stop "the $f job $j has no single allocation named $jn on $nn nodes"
    printf '%s\n' "$out" >> "$R/post/sacct.txt" || stop "write sacct.txt"
  done
  # the recheck's claim names the replicas job charged, and no other replica allocation exists since setup (B1)
  cl=$(cat "$R/replicas-check/recheck.claim") || stop "no recheck claim"
  [ "$cl" = "$jr" ] || stop "the recheck was claimed by job '$cl', not the replicas job $jr"
  since=$(cat "$R/logs/setup.done") || stop "setup.done unreadable"
  case "$since" in [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9]) ;; *) stop "setup.done '$since'";; esac
  reps=$(TZ=UTC sacct -X -n -P -S "$since" --name=ptmc_reps -o JobID,JobName) || stop "sacct of the replica allocations"
  nr=$(printf '%s\n' "$reps" | awk -F'|' '$2 == "ptmc_reps"' | wc -l) || stop "counting the replica allocations"
  [ "$nr" = 1 ] && printf '%s\n' "$reps" | awk -F'|' -v j="$jr" '$2 == "ptmc_reps" && ($1 "") == (j "") {f = 1} END {exit !f}' \
    || stop "sacct shows $nr ptmc_reps allocations since setup, not exactly the replicas job $jr"
  awk -F'|' '$1 !~ /\./ {if ($5 !~ /^[0-9]+$/ || $6 !~ /^[0-9]+$/ || $5 == 0 || $6 == 0) bad = 1; s += $5 * $6 / 3600; n++}
    END {if (n != 2 || bad) exit 1; printf "charged_node_h=%.4f\n", s}' \
    "$R/post/sacct.txt" > "$R/post/charge.txt" || stop "charge"
  cat "$R/post/sacct.txt" "$R/post/charge.txt"
  activate
  nice -n 19 "$PY" -B "$O/launch/ptmc_stage_d4.py" --tree "$R/deploy" --out "$R/d4" > "$R/post/d4.log" 2>&1 \
    || { cat "$R/post/d4.log"; stop "the D4 staging"; }
  tail -5 "$R/post/d4.log"
  (cd "$R" && sha256sum stage/* > "$R/post/stage.sha256") || stop "stage digests"
  (cd "$R" && nice -n 19 tar -czf "$R/post.tar.gz" logs post pilot-post replicas-check claims units) || stop "tar post"
  (cd "$R" && nice -n 19 tar -czf "$R/d4.tar.gz" d4) || stop "tar d4"
  (cd "$R" && sha256sum post.tar.gz d4.tar.gz > tars.sha256) || stop "the tars' digests"
  cat "$R/tars.sha256" || stop "printing the tars' digests"
  echo "post done $(now)" ;;
esac
exit 0
