#!/bin/bash
#SBATCH --job-name=uthrow5d_block
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=32 --mem=80G --time=12:00:00
#SBATCH --array=0-20%10
#SBATCH --output=uq_5d/uthrow5d_block_%a_%A.out --error=uq_5d/uthrow5d_block_%a_%A.err
# Jitter-matched block-sum units for the 5D unified/block comparison: each block
# universe (12 knob +1sigma + 100 Flux) is RE-UNFOLDED at the CV seed so its
# OmniFold jitter cancels in (x_b - x_cv). task 0 = all 12 knobs; tasks 1-20 = a
# 5-flux chunk each (5x20 = 100). Combine aggregates these into C_blocksum.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"; mkdir -p uq_5d/block_slabs_5d
source "${REPO}/lib/resume_guard.sh"
# SOURCED RELATIVE TO THIS SCRIPT, NOT THROUGH ${REPO}. A launcher frozen at a sha that sources its
# member-axis library from the MUTABLE canonical checkout is not frozen: at run time it picks up
# whatever is in /pscratch/.../MINERvA-OmniFold, which is on a divergent local main that does not
# contain this library at all. Demonstrated, not theorised -- the cluster probe failed 16/16 with
# exactly that error. Relative sourcing means a frozen deployment sources its OWN frozen library,
# and a git worktree resolves its own. The library lives beside this file, so no path arithmetic.
# The three PRE-EXISTING ${REPO} sources on the lines above have the same exposure across 244
# tracked .sh and are deliberately NOT touched here: that is a repo-wide migration, not a patch.
_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${_HERE}/lib_member_resume.sh"; mr_require_valid_offset   # M(ii) member axis
BLOCK_DIR="$(mr_dir_prefix uq_5d/block_slabs_5d)"
T=${SLURM_ARRAY_TASK_ID}
# --invalid-ratio neutral: hold the ~5e-5 GENIE negative-weight artifacts
# (HighQ2/LowQ2 +1sigma, one MFP_N zero) at CV for the affected knob -- the
# established prior handling (old _clip), now explicitly logged. See
# sbatch_uthrow_run_5d.sh for the full note.
# HOISTED ABOVE THE `if` ON 2026-08-18, and the bug it fixes is worth the line: this assignment
# sat at COLUMN 0 INSIDE the `then` block, so the `else` branch expanded ${EST_SEED} to NOTHING
# and every T != 0 task died with `argument --estimator-seed: expected one argument`. INDENTATION
# IS NOT SCOPE -- column 0 inside an indented block is legal bash and reads as top level, which
# is why a reachability heuristic keyed on indentation cleared it. Keep it before the `if`.
# M(ii) OFFSET HOOK (spec (B) option (ii), BEN-461). The launcher keeps its OWN baseline
# literal, so MNV_EST_SEED_OFFSET=0 -- the default -- reproduces the archive EXACTLY and the
# two coherence groups are preserved BY CONSTRUCTION rather than by the driver getting it
# right: one offset in, each leg adds it to its own baseline. Do not replace this with an
# absolute-seed override; that hands the group structure back to the caller.
EST_SEED=$(( 1000 + ${MNV_EST_SEED_OFFSET:-0} ))
if [[ "$T" -eq 0 ]]; then
  python3 unified_throw_cov_5d.py --blockunits --block-knobs all --draw-seed 1000 --estimator-seed ${EST_SEED} \
    --bank bank_uthrow_5d --iters 5 --invalid-ratio neutral \
    --out "${BLOCK_DIR}/block5d_knobs.npz"
else
  LO=$(( (T-1) * 5 )); HI=$(( LO + 4 ))
  python3 unified_throw_cov_5d.py --blockunits --block-knobs none --block-flux ${LO}-${HI} \
    --draw-seed 1000 --estimator-seed ${EST_SEED} --bank bank_uthrow_5d --iters 5 --invalid-ratio neutral \
    --out "${BLOCK_DIR}/block5d_flux_${T}.npz"
fi
