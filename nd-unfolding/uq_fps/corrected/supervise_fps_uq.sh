#!/bin/bash
# Detached login-node supervisor for the corrected FPS unified-throw sub-chain (Agent C).
# Survives Claude session restarts (launched via setsid). Loops: relaunch the packed
# orchestrator (alloc_run creates/reuses claude-hold; orchestrator preclean+skip-if-exists
# resumes) until 40 COMPLETE throw slabs (4 throws each) + 26 block slabs exist, then runs
# the unified-throw combine + adopt. Idempotent; safe to run a single instance.
#   setsid bash uq_fps/corrected/supervise_fps_uq.sh </dev/null >uq_fps/corrected/logs/supervise.log 2>&1 &
set -o pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; cd "$REPO"
ENVP='export ROOT628_PREFIX=/global/homes/j/josephrb/.conda/envs/root_6_28; source setup_salloc_env.sh 1>/dev/null 2>&1;'
UN="nd-unfolding/uq_fps/corrected/uthrow_slabs_fps_neutral"
say(){ echo "[supervise $(date -u '+%F %T UTC')] $*"; }

complete_counts(){ # -> "NTHROW_COMPLETE NBLOCK"
  "$REPO"/alloc_run.sh "$ENVP cd nd-unfolding && python3 - <<'PY'
import glob,os,numpy as np
un='uq_fps/corrected/uthrow_slabs_fps_neutral'; c=0
for f in glob.glob(os.path.join(un,'uthrowfps_slab_*.npz')):
    try: c+= (np.load(f,allow_pickle=True)['xs'].shape[0]==4)
    except: pass
nb=len(glob.glob(os.path.join(un,'blockfps_*.npz')))
print(f'COUNTS {c} {nb}')
PY" 2>/dev/null | grep '^COUNTS' | awk '{print $2, $3}'
}

relaunches=0; MAX_RELAUNCH=30
while true; do
  (( relaunches > MAX_RELAUNCH )) && { say "hit MAX_RELAUNCH=$MAX_RELAUNCH -> giving up"; break; }
  read -r nc nb < <(complete_counts); nc=${nc:-0}; nb=${nb:-0}
  say "relaunches=$relaunches complete_throws=$nc/40 blocks=$nb/26"
  if (( nc >= 40 && nb >= 26 )); then
    say "phase B COMPLETE -> combine"
    "$REPO"/alloc_run.sh "$ENVP cd nd-unfolding && python3 unified_throw_cov.py --combine 'uq_fps/corrected/uthrow_slabs_fps_neutral/uthrowfps_slab_*.npz' --expected-throws 0-159 --block-slabs 'uq_fps/corrected/uthrow_slabs_fps_neutral/blockfps_*.npz' --bank bank_uthrow_fps --iters 5 --invalid-ratio neutral --null --out-root uq_fps/corrected/unified_throw_cov_fps.root" 2>&1 | tail -20
    if [[ -s nd-unfolding/uq_fps/corrected/unified_throw_cov_fps.root ]]; then
      say "combine OK -> adopt"
      "$REPO"/alloc_run.sh "$ENVP cd nd-unfolding && python3 adopt_unified_4d.py --uthrow uq_fps/corrected/unified_throw_cov_fps.root --combined uq_fps/corrected/universe_stage2_fps/uq_universe_fps_covariance_combined.root --prod uq_fps/universe_sweep/fps2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root --out uq_fps/corrected/universe_stage2_fps/uq_universe_fps_covariance_combined_uthrow.root" 2>&1 | tail -15
      say "adopt done -> DONE"
    else
      say "combine did NOT write output (likely incomplete/partial) -> loop to regenerate"
      continue
    fi
    break
  fi
  # Guard against double-launch: if an orchestrator is already running in claude-hold, wait.
  NODE=$(squeue --me --name=claude-hold -h -o "%N" 2>/dev/null | head -1)
  if [[ -n "$NODE" ]] && ssh -o StrictHostKeyChecking=no -o ConnectTimeout=15 "$NODE" \
       'ps -u josephrb -o args= 2>/dev/null | grep -q "[r]un_fps_uq_packed"' 2>/dev/null; then
    say "orchestrator already running on $NODE -> wait (no double-launch)"; sleep 120; continue
  fi
  say "relaunch orchestrator chunk (#$((relaunches+1)))"
  relaunches=$((relaunches+1))
  "$REPO"/alloc_run.sh 'bash /pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/uq_fps/corrected/run_fps_uq_packed.sh' 2>&1 | tail -3
  sleep 20
done
say "supervisor exiting"
