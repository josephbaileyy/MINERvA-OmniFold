#!/bin/bash
# OOFVC step 2 (OOFVC-DECLARATION.md section 2.5), on a login node, through oofvc_launch.sh. Writes only under $R.
# Only after all twelve dump tasks are done:
#   1. stage the CV omnifile and the flux file from CFS by O_NOATIME copy (dd iflag=noatime), each re-hashed against its
#      pin, set a-w, with the sources' atime recorded before and after (Tier 1's stage.log form);
#   2. the deploy tree at M by make_tree.sh (clone mode), pointed at $R/stage;
#   3. libRooUnfold.so against its pin;
#   4. submit units.sbatch: one node, the join (C-ROUTE, C-JOIN, C-SIGW, C-LAB) and then the four units.
set -u
R=/pscratch/sd/j/josephrb/oofvc-20261126
TOOLC=__TOOL_COMMIT__
URL=https://github.com/josephbaileyy/MINERvA-OmniFold.git
CV_SRC=/global/cfs/cdirs/m3246/josephrb/two-d-followup-20261010/xr-input/runEventLoopOmniFold_MEFHC.root
MC_SRC=/global/cfs/cdirs/m3246/josephrb/minerva-shutdown-stage/fig_products/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root
CV_SHA=43f8cc16ab2688200d3e2e0ebb48012b23ada6d7882b8c68ecfc51c609aeb8df
MC_SHA=d40aea69235cdc98644e1bb3e622e579d6b81904c004c83fe50465079989f316
LIB=/pscratch/sd/j/josephrb/MINERvA-OmniFold/unbinned_unfolding/build/libRooUnfold.so
LIB_SHA=0b34e1e39102b0dddc5923dad7f69e59c70cd6a2fcbcef07728b72cf2933fefd
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

echo "node $(hostname) $(date -u +%FT%TZ) tool $TOOLC"
[ "$(git -C "$R/tool" rev-parse HEAD)" = "$TOOLC" ] && [ -z "$(git -C "$R/tool" status --porcelain --ignored)" ] \
  || { echo "STOP: the tool clone is not clean at $TOOLC"; exit 3; }
[ ! -e "$R/stage" ] && [ ! -e "$R/deploy" ] && [ ! -e "$R/logs/units.jobid" ] || { echo "STOP: step 2 has run"; exit 2; }
sq=$(squeue -h -u "$USER" -o '%j') || { echo "STOP: squeue failed"; exit 2; }
q=$(printf '%s\n' "$sq" | grep -c '^oofvc_' || true)
[ "$q" = 0 ] || { echo "STOP: an oofvc job is queued"; exit 2; }
for pl in 1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P; do
  [ -e "$R/dump/$pl.done" ] && (cd "$R/dump" && sha256sum -c "$pl.sha256" >/dev/null) \
    && grep -q ' routing_disagree 0$' "$R/dump/$pl.log" || { echo "STOP: dump $pl"; exit 4; }
done
echo "dumps: 12 done, routing_disagree 0, digests checked"
fence_check "before staging the CV omnifile (cov2d-protected; read with O_NOATIME)"
mkdir "$R/stage" || exit 2
{ date -u +%FT%TZ
  for s in "$CV_SRC" "$MC_SRC"; do echo "pre  $(stat -c '%n|atime=%x' "$s")"; done
  dd iflag=noatime if="$CV_SRC" of="$R/stage/runEventLoopOmniFold_MEFHC.root" bs=16M status=none || exit 5
  dd iflag=noatime if="$MC_SRC" of="$R/stage/runEventLoopMC_MEFHC.root" bs=16M status=none || exit 5
  for s in "$CV_SRC" "$MC_SRC"; do echo "post $(stat -c '%n|atime=%x' "$s")"; done
  (cd "$R/stage" && sha256sum runEventLoopOmniFold_MEFHC.root runEventLoopMC_MEFHC.root)
  chmod a-w "$R/stage"/*.root; ls -l "$R/stage"; date -u +%FT%TZ; } > "$R/logs/stage.log" 2>&1
cat "$R/logs/stage.log"
[ "$(sha256sum < "$R/stage/runEventLoopOmniFold_MEFHC.root" | cut -d' ' -f1)" = "$CV_SHA" ] \
  && [ "$(sha256sum < "$R/stage/runEventLoopMC_MEFHC.root" | cut -d' ' -f1)" = "$MC_SHA" ] \
  || { echo "STOP: a staged copy differs from its pin"; exit 5; }
OOFVC_PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3 \
  bash "$O/make_tree.sh" "$R/deploy" clone "$URL" "$R/stage" > "$R/logs/deploy.log" 2>&1 \
  || { echo "STOP: make_tree"; cat "$R/logs/deploy.log"; exit 6; }
cat "$R/logs/deploy.log"
[ "$(sha256sum < "$LIB" | cut -d' ' -f1)" = "$LIB_SHA" ] || { echo "STOP: libRooUnfold.so differs from its pin"; exit 6; }
echo "libRooUnfold.so $LIB_SHA"
fence_check "before the submit"
j=$(sbatch --parsable "$O/launch/units.sbatch") || { echo "STOP: sbatch"; exit 7; }
echo "$j" > "$R/logs/units.jobid"; echo "units job $j"
