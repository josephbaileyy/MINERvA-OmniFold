#!/bin/bash
#SBATCH -A m3246
#SBATCH -C cpu
#SBATCH -N 1
#SBATCH -o /pscratch/sd/j/josephrb/measurement-paper/phase1/mp2/s2/logs/mp2s2-%x-%j.out
# MP-2 S2 tranche A step 0 (director-approved): do 4 concurrent model-step shapes, with the memory split that
# mp2_s2_job.sh computes (the same sourced reader from $CODE), all start together? sleep only.
# Pass = all four steps' sacct Start within 5 s. The first attempt (60112440) stopped: SLURM_MEM_PER_NODE unset.
CODE=${CODE:?CODE snapshot}
source "$CODE/mp2_s2_slurm_mem.sh"
NG=4
MEMN=$(alloc_mem_mib) || { echo "STOP: no job memory allocation"; exit 4; }
MSTEP=$(( MEMN * 95 / 100 / NG ))
echo "host $(hostname) start $(date -u +%FT%TZ) code $CODE steps $NG x ${MSTEP}M of ${MEMN}M (SLURM_MEM_PER_NODE='${SLURM_MEM_PER_NODE}')"
for i in 0 1 2 3; do srun -n 1 -c $((256 / NG)) --exact --mem=${MSTEP}M bash -c 'echo step $SLURM_STEP_ID begin $(date -u +%T.%N); sleep 60' & done
wait
echo "end $(date -u +%FT%TZ)"
