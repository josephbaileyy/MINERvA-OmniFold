#!/bin/bash
# PTMC's login-node steps (PTMC-DECLARATION.md sections 1, 2.3 and 7), run through ptmc_launch.sh as
# `bash <self> <self> MODE`, each on its own GO. Writes only under $R. Every gate fails closed: an unexpected state, or
# a failed command, is a STOP (exit 2-9), never an empty pass. The login-node steps run at nice 19 with one thread.
#   setup       fence; $R new; the tool clone at TOOLC; the O_NOATIME copies (CV, MC from CFS; r3's rows and join
#               record), each re-hashed against its pin; the deploy tree (make_tree.sh, clone); libRooUnfold's pin
#   pilot       fence; setup's digests re-checked; submit pilot.sbatch (2 nodes, the 8 pilot units)
#   post-pilot  the pilot's sacct, its units' markers and controls, t_R, o, the projection and L (ptmc_pilot_post.py);
#               writes pilot-post/PROCEED only if every rule of section 7 passes
#   replicas    fence; PROCEED re-checked; submit replicas.sbatch with -t L (5 nodes)
#   post        sacct of every PTMC job, the charge, the D4 baseline staged by O_NOATIME (ptmc_stage_d4.py), and the
#               records tarred: post.tar.gz (units and logs) and d4.tar.gz (the staged D4 copies)
set -u
export LC_ALL=C
umask 077
MODE=${2:-}
R=/pscratch/sd/j/josephrb/ptmc-20261128
TOOLC=__TOOL_COMMIT__
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
O=$R/tool/2d-unfolding/ptmc
stop() { echo "STOP: $*"; exit "${STOP_RC:-7}"; }
now() { date -u +%FT%TZ; }
case "$TOOLC" in *__*) stop "the tool commit is not filled in";; esac
case "$MODE" in setup|pilot|post-pilot|replicas|post) ;; *) stop "mode '$MODE'";; esac
me=$(id -un) && [ "$me" = josephrb ] || stop "user"
echo "node $(hostname) $(now) mode $MODE tool $TOOLC"

# fence: no live cov2d or t2a job (sacct, never squeue; a state outside the terminal set, or an empty one, is live)
fence_check() {
  local since out live
  since=$(date -u -d '14 days ago' +%F) || stop "date failed ($1)"
  out=$(sacct -X -n -P -S "$since" -o JobID,JobName,State 2>&1) || stop "sacct failed ($1)"
  live=$(printf '%s\n' "$out" | awk -F'|' '$2 ~ /^(cov2d|t2a)/ { split($3, s, " ");
    if (s[1] !~ /^(COMPLETED|FAILED|CANCELLED|TIMEOUT|OUT_OF_MEMORY|NODE_FAIL|PREEMPTED|BOOT_FAIL|DEADLINE)$/) print }')
  [ -z "$live" ] || stop "a fenced job is live ($1): $live"
  echo "fence check ($1): no live cov2d or t2a job $(now)"
}
# no PTMC job queued or running (a second submit, or a step run beside a live job, is refused)
no_ptmc_job() {
  local sq n
  sq=$(squeue -h -u "$USER" -o '%j') || stop "squeue failed"
  n=$(printf '%s\n' "$sq" | grep -c '^ptmc_' || true)
  [ "$n" = 0 ] || stop "a ptmc job is queued or running"
}
sha_of() { sha256sum < "$1" | cut -d' ' -f1; }
tool_ok() {
  [ "$(git -C "$R/tool" rev-parse HEAD)" = "$TOOLC" ] || stop "the tool clone is not at $TOOLC"
  [ -z "$(git -C "$R/tool" status --porcelain --ignored)" ] || stop "the tool clone is not clean"
}
stage_ok() {
  [ -e "$R/stage/ready" ] || stop "the stage is not ready"
  [ "$(sha_of "$R/stage/runEventLoopOmniFold_MEFHC.root")" = "$CV_SHA" ] || stop "the staged CV differs from its pin"
  [ "$(sha_of "$R/stage/runEventLoopMC_MEFHC.root")" = "$MC_SHA" ] || stop "the staged MC differs from its pin"
  [ "$(sha_of "$R/stage/oofvc_rows.npz")" = "$ROWS_SHA" ] || stop "the staged rows differ from their pin"
  [ "$(sha_of "$R/stage/join.json")" = "$JOIN_SHA" ] || stop "the staged join record differs from its pin"
  [ "$(cat "$R/stage/rows.sha256")" = "$ROWS_SHA" ] || stop "rows.sha256"
  (cd "$R/deploy" && sha256sum -c --quiet "$R/logs/deploy.sha256") || stop "the deploy tree differs from its digests"
}
copy_noatime() {  # copy_noatime SRC DEST PIN: one O_NOATIME read, then the copy re-hashed against the pin
  [ -f "$1" ] && [ ! -L "$1" ] || stop "$1 is absent or a symlink"
  [ ! -e "$2" ] || stop "$2 exists"
  echo "pre  $(stat -c '%n|atime=%x' "$1")"
  dd iflag=noatime if="$1" of="$2" bs=16M status=none || stop "dd $1"
  echo "post $(stat -c '%n|atime=%x' "$1")"
  [ "$(sha_of "$2")" = "$3" ] || stop "the copy of $1 is not $3"
  chmod a-w "$2" || stop "chmod $2"
  echo "copied $(basename "$2") $3"
}

case "$MODE" in
setup)
  fence_check "before setup"
  no_ptmc_job
  [ ! -e "$R" ] || stop "$R exists"
  mkdir -p "$R/logs" "$R/stage" || stop "mkdir"
  git clone -q "$URL" "$R/tool" > "$R/logs/clone.log" 2>&1 || stop "git clone"
  git -C "$R/tool" -c advice.detachedHead=false checkout -q "$TOOLC" || stop "checkout $TOOLC"
  tool_ok
  fence_check "before the CV copy (cov2d-protected; O_NOATIME)"
  # the copies print to the session (the receipt); a STOP inside one exits here, in the open
  copy_noatime "$CV_SRC" "$R/stage/runEventLoopOmniFold_MEFHC.root" "$CV_SHA"
  copy_noatime "$MC_SRC" "$R/stage/runEventLoopMC_MEFHC.root" "$MC_SHA"
  copy_noatime "$ROWS_SRC" "$R/stage/oofvc_rows.npz" "$ROWS_SHA"
  copy_noatime "$JOIN_SRC" "$R/stage/join.json" "$JOIN_SHA"
  echo "staged $(now)"
  echo "$ROWS_SHA" > "$R/stage/rows.sha256"
  PTMC_PY=$PY nice -n 19 bash "$O/make_tree.sh" "$R/deploy" clone "$URL" "$R/stage" > "$R/logs/deploy.log" 2>&1 \
    || { cat "$R/logs/deploy.log"; stop "make_tree"; }
  cat "$R/logs/deploy.log"
  (cd "$R/deploy" && sha256sum 2d-unfolding/re2/re2_driver.py 2d-unfolding/ref_c2c1/config.json \
     2d-unfolding/ref_c2c1/ref_c2c1.py 2d-unfolding/ref_c2c1/ref_c2c1_read.py unbinned_unfolding/python/omnifold.py \
     2d-unfolding/compare_to_paper_fullcov.py 2d-unfolding/uq/reported_cells.py 2d-unfolding/oofvc/oofvc_lib.py) \
     > "$R/logs/deploy.sha256" || stop "deploy digests"
  [ "$(sha_of "$LIB")" = "$LIB_SHA" ] || stop "libRooUnfold.so differs from its pin"
  echo "libRooUnfold.so $LIB_SHA"
  touch "$R/stage/ready" || stop "ready"
  echo "setup done $(now)" ;;
pilot)
  tool_ok; stage_ok
  [ ! -e "$R/logs/pilot.jobid" ] && [ ! -e "$R/units" ] || stop "the pilot has been submitted"
  no_ptmc_job
  fence_check "before the pilot's submit"
  j=$(sbatch --parsable "$O/launch/pilot.sbatch") || stop "sbatch"
  case "$j" in *[!0-9]*|'') stop "sbatch printed '$j'";; esac
  echo "$j" > "$R/logs/pilot.jobid"; echo "pilot job $j $(now)" ;;
post-pilot)
  tool_ok
  [ -e "$R/logs/pilot.jobid" ] || stop "no pilot job"
  [ ! -e "$R/pilot-post" ] || stop "post-pilot has run"
  no_ptmc_job
  j=$(cat "$R/logs/pilot.jobid")
  mkdir "$R/pilot-post" || stop "mkdir"
  TZ=UTC sacct -j "$j" -n -P -o JobID,JobName,State,ExitCode,ElapsedRaw,NNodes,Start,End > "$R/pilot-post/sacct.txt" 2>&1 \
    || stop "sacct"
  cat "$R/pilot-post/sacct.txt"
  eval "$("$CONDA_HOOK" shell.bash hook)" && conda activate "$HOME/.conda/envs/root_6_28" || stop "conda activate"
  OMP_NUM_THREADS=1 nice -n 19 "$PY" -B "$O/launch/ptmc_pilot_post.py" --sacct "$R/pilot-post/sacct.txt" \
    --units "$R/units" --out "$R/pilot-post" ; r=$?
  cat "$R/pilot-post/decision.json" 2>/dev/null
  [ "$r" = 0 ] || STOP_RC=6 stop "the pilot's post did not PROCEED (rc $r)"
  [ -e "$R/pilot-post/PROCEED" ] || stop "no PROCEED file"
  echo "post-pilot PROCEED $(now)" ;;
replicas)
  tool_ok; stage_ok
  [ -e "$R/pilot-post/PROCEED" ] || stop "no PROCEED"
  [ ! -e "$R/logs/replicas.jobid" ] || stop "the replicas have been submitted"
  no_ptmc_job
  L=$(cat "$R/pilot-post/time_limit_minutes") || stop "no time limit"
  case "$L" in ''|*[!0-9]*) stop "time limit '$L'";; esac
  [ "$L" -ge 1 ] && [ "$L" -le 600 ] || stop "time limit $L minutes is outside 1..600"
  fence_check "before the replicas' submit"
  j=$(sbatch --parsable -t "$L" "$O/launch/replicas.sbatch") || stop "sbatch"
  case "$j" in *[!0-9]*|'') stop "sbatch printed '$j'";; esac
  echo "$j" > "$R/logs/replicas.jobid"; echo "replicas job $j, -t $L minutes $(now)" ;;
post)
  tool_ok
  [ ! -e "$R/post" ] && [ ! -e "$R/post.tar.gz" ] && [ ! -e "$R/d4" ] || stop "post has run"
  no_ptmc_job
  mkdir "$R/post" || stop "mkdir"
  for f in pilot replicas; do
    [ -e "$R/logs/$f.jobid" ] || continue
    TZ=UTC sacct -j "$(cat "$R/logs/$f.jobid")" -n -P -o JobID,JobName,State,ExitCode,ElapsedRaw,NNodes,Start,End
  done > "$R/post/sacct.txt" 2>&1 || stop "sacct"
  awk -F'|' '$1 !~ /\./ {s += $5 * $6 / 3600} END {printf "charged_node_h=%.4f\n", s}' "$R/post/sacct.txt" \
    > "$R/post/charge.txt" || stop "charge"
  cat "$R/post/sacct.txt" "$R/post/charge.txt"
  eval "$("$CONDA_HOOK" shell.bash hook)" && conda activate "$HOME/.conda/envs/root_6_28" || stop "conda activate"
  OMP_NUM_THREADS=1 nice -n 19 "$PY" -B "$O/launch/ptmc_stage_d4.py" --tree "$R/deploy" --out "$R/d4" \
    > "$R/post/d4.log" 2>&1 || { cat "$R/post/d4.log"; stop "the D4 staging"; }
  tail -5 "$R/post/d4.log"
  (cd "$R" && sha256sum stage/* > "$R/post/stage.sha256") || stop "stage digests"
  (cd "$R" && nice -n 19 tar -czf "$R/post.tar.gz" logs post pilot-post units) || stop "tar post"
  (cd "$R" && nice -n 19 tar -czf "$R/d4.tar.gz" d4) || stop "tar d4"
  sha256sum "$R/post.tar.gz" "$R/d4.tar.gz"
  echo "post done $(now)" ;;
esac
exit 0
