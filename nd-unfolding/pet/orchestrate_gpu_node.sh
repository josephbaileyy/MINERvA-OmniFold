#!/bin/bash
# Runs INSIDE a GPU allocation (1 node, NGPU GPUs; via salloc+srun --gpus=NGPU).
# Processes a list of PET bootstrap replica IDs with GPU-parallel waves, one
# replica pinned per GPU (CUDA_VISIBLE_DEVICES), content-validated resume, each
# delegating to the committed, 1-20-validated single-replica payload. Idempotent: a
# replica whose 5D NPZ is COMPLETE is skipped, so a wall-clock kill mid-wave is safe
# (the incomplete ID is simply redone on the next launch).
#
# 2026-08-06: that idempotence claim was FALSE as written. The guard was a bare size
# test, the BEN-023 size-as-completion-proof defect, and this script is precisely the
# "wall-clock kill mid-wave" case its own comment describes -- a kill leaves a partial
# npz, which a bare size test then treats as done and skips forever. Converted to the
# content-validated guard in lib/resume_guard.sh: a complete npz is validated and
# adopted (no recompute), a truncated one is detected and redone, which is what makes
# the idempotence real. See FINDINGS.md BEN-023.
#
#   NGPU=4 STAGGER=150 bash pet/orchestrate_gpu_node.sh 100 99 98 97 ...
set -uo pipefail
export HOME=/global/homes/j/josephrb
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/lib/resume_guard.sh"
cd "${REPO}/nd-unfolding"
NGPU="${NGPU:-4}"
STAGGER="${STAGGER:-150}"          # desync memory peaks across GPUs within a wave
FIVE="products/pet/bkgsub/bootstrap_replicas/5d"
PAYLOAD="${REPO}/nd-unfolding/pet/sbatch_pet_bootstrap_replica.sh"
mkdir -p pet/logs
IDS=("$@")
# Multi-node aware: under `srun --ntasks=NNODES --nodes=NNODES`, each task runs
# this script on its own node and processes a disjoint round-robin share of IDS
# (global index % NNODES == NODEID). Single-node/direct run => NNODES=1 -> all.
NNODES="${SLURM_NNODES:-1}"
NODEID="${SLURM_NODEID:-0}"
echo "[orch] $(date -u +%FT%TZ) host=$(hostname) NODEID=${NODEID}/${NNODES} NGPU=$NGPU ids=${IDS[*]}"
nvidia-smi -L 2>/dev/null | sed "s/^/[orch n${NODEID}] gpu: /" || true

gidx=0
launched=0
for id in "${IDS[@]}"; do
  if (( gidx % NNODES != NODEID )); then gidx=$(( gidx + 1 )); continue; fi
  gidx=$(( gidx + 1 ))
  npz="${FIVE}/pet_bootstrap_5d_${id}.npz"
  if rg_skip_if_complete "$npz" rg_valid_npz; then
    echo "[orch n${NODEID}] skip id=${id} (5D NPZ complete)"; continue
  fi
  gpu=$(( launched % NGPU ))
  echo "[orch n${NODEID}] start id=${id} on GPU ${gpu} $(date -u +%FT%TZ)"
  # Subshell so the env prefix stays scoped to this replica: a bare `VAR=x func` sets
  # VAR in the CALLER for a shell function, which would leak CUDA_VISIBLE_DEVICES into
  # the next iteration and pin every later replica to the first GPU.
  (
    CUDA_VISIBLE_DEVICES="${gpu}" \
    REPLICA_ID="${id}" \
    PET_INPUTS="of_inputs_pc_fullcloud_bkgsub_5d.npz" \
    PET_W_SOURCE="of_inputs_5d.npz" \
    PET_BOOT_OUTDIR="products/pet/bkgsub/bootstrap_replicas" \
      rg_run "$npz" bash "${PAYLOAD}"
  ) > "pet/logs/orch_${id}.out" 2> "pet/logs/orch_${id}.err" &
  launched=$(( launched + 1 ))
  if (( launched % NGPU == 0 )); then
    echo "[orch n${NODEID}] wave full (${NGPU}); waiting $(date -u +%FT%TZ)"
    wait
  else
    sleep "${STAGGER}"
  fi
done
echo "[orch n${NODEID}] final wait $(date -u +%FT%TZ)"
wait
echo "[orch n${NODEID}] DONE $(date -u +%FT%TZ); present ids: $(ls ${FIVE} | grep -oE '_[0-9]+\.npz' | grep -oE '[0-9]+' | awk '$1>=21' | sort -n | tr '\n' ' ')"
