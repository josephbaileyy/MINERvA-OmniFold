#!/bin/bash
#SBATCH --job-name=sweep5dBKGrun
#SBATCH --account=m3246_g
#SBATCH --qos=shared --constraint=gpu --nodes=1 --ntasks=1 --gpus-per-task=1 --cpus-per-task=32 --time=01:30:00
#SBATCH --array=1-169%48
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=uq_4d/sweep5dBKGrun_%a_%A.out --error=uq_4d/sweep5dBKGrun_%a_%A.err
# KNOWN_ISSUES #13 closing step (run), GPU-allocation variant (2026-07-14).
# Stage-2 5D re-unfold of each VERTICAL universe from bank_sweep_5d_bkgaware, now
# rebinning the CV background with that universe's w_bkg to recompute the measured
# purity down-weight (per-universe background). FAIL-CLOSED: no --allow-cv-background,
# so any universe whose bank lacks bkgw aborts (guards against a silent CV fallback).
# NON-DESTRUCTIVE outdir uq_5d/universe_sweep_bkgaware. ~15 min, ~15GB -> 1-GPU slot.
set -eo pipefail
export HOME=/global/homes/j/josephrb
export ROOT628_PREFIX=/global/homes/j/josephrb/.conda/envs/root_6_28
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"
source "${REPO}/lib/resume_guard.sh"
# SOURCED RELATIVE TO THIS SCRIPT, NOT THROUGH ${REPO}. A launcher frozen at a sha that sources its
# member-axis library from the MUTABLE canonical checkout is not frozen: at run time it picks up
# whatever is in /pscratch/.../MINERvA-OmniFold, which is on a divergent local main that does not
# contain this library at all. Demonstrated, not theorised -- the cluster probe failed 16/16 with
# exactly that error. Relative sourcing means a frozen deployment sources its OWN frozen library,
# and a git worktree resolves its own. The library lives beside this file, so no path arithmetic.
# The three PRE-EXISTING ${REPO} sources on the lines above have the same exposure across 244
# tracked .sh and are deliberately NOT touched here: that is a repo-wide migration, not a patch.
# --- M(ii) member axis: LOCATE lib_member_resume.sh, then source it -------------------------------
# `${BASH_SOURCE[0]}` IS THE SPOOL PATH UNDER sbatch. Slurm copies the batch script to
# /var/spool/slurmd/job<N>/slurm_script and executes the COPY, so `dirname "${BASH_SOURCE[0]}"` is the
# spool directory and the library was never staged there. Measured, not theorised: stage 0's first three
# arrays died in 12 s at exactly this line with
#   /var/spool/slurmd/job57250483/lib_member_resume.sh: No such file or directory
# while the library sat correctly at 13,845 bytes in the frozen tree.
#
# WHY FOUR PROBE RUNS AND A GATE PASSED OVER IT. Direct execution and the argv probe (which `source`s
# launchers from a parent shell) BOTH preserve BASH_SOURCE as the real path. sbatch is the only
# invocation that stages the script, and it is the only one production uses. The go-line was verified
# twice in environments that share the property it depends on.
#
# EACH CANDIDATE IS VALIDATED BY THE LIBRARY'S PRESENCE, NOT BY TRUSTING ITS MECHANISM. That is the
# actual lesson: a resolver that assumes cannot detect the environment where its assumption is false.
#
# SLURM_SUBMIT_DIR IS DELIBERATELY NOT A CANDIDATE. It would have worked here, but it is the SUBMIT
# directory rather than the script's, so submitting from the canonical checkout -- which also contains a
# lib_member_resume.sh -- would silently source the CANONICAL library instead of the frozen one. That
# reintroduces the exact frozen-deployment defect the relative source was written to close, and it does
# so INVISIBLY. A candidate that can resolve to the wrong tree is worse than failing closed.
_mr_lib=""
for _mr_c in "${MNV_LAUNCHER_DIR:-}" "$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"; do
  if [[ -n "$_mr_c" && -r "$_mr_c/lib_member_resume.sh" ]]; then _mr_lib="$_mr_c"; break; fi
done
if [[ -z "$_mr_lib" && -n "${SLURM_JOB_ID:-}" ]]; then
  # The only source of the REAL script path inside a batch job. One control-plane call per job.
  _mr_c="$(scontrol show job "$SLURM_JOB_ID" 2>/dev/null \
           | tr ' ' '\n' | sed -n 's/^Command=//p' | head -1)"
  _mr_c="${_mr_c:+$(dirname "$_mr_c")}"
  if [[ -n "$_mr_c" && -r "$_mr_c/lib_member_resume.sh" ]]; then _mr_lib="$_mr_c"; fi
fi
if [[ -z "$_mr_lib" ]]; then
  echo "[member] FAIL: cannot locate lib_member_resume.sh beside this launcher." >&2
  echo "[member]   tried: MNV_LAUNCHER_DIR, dirname \$BASH_SOURCE, scontrol Command" >&2
  echo "[member]   BASH_SOURCE=${BASH_SOURCE[0]:-<unset>}  SLURM_JOB_ID=${SLURM_JOB_ID:-<unset>}" >&2
  echo "[member]   Under sbatch the script runs from the spool, so BASH_SOURCE is NOT its home." >&2
  echo "[member]   Set MNV_LAUNCHER_DIR to the launcher's directory to resolve this explicitly." >&2
  exit 2
fi
source "${_mr_lib}/lib_member_resume.sh"; mr_require_valid_offset   # M(ii) member axis
# GEANT bands are owned by the detector direct-driver leg (matches validated
# methodology); this vertical bank-sweep leg runs the other 169 (GEANT filtered).
U=$(sed -n "${SLURM_ARRAY_TASK_ID}p" uq_4d/vertical_run_bkgaware.txt)
[[ -z "$U" ]] && exit 0
echo "[sweep-run-bkg] node=$(hostname) task=${SLURM_ARRAY_TASK_ID} universe=${U} start $(date -u '+%F %T UTC')"
# M(ii) OFFSET HOOK (spec (B) option (ii), BEN-461). The launcher keeps its OWN baseline
# literal, so MNV_EST_SEED_OFFSET=0 -- the default -- reproduces the archive EXACTLY and the
# two coherence groups are preserved BY CONSTRUCTION rather than by the driver getting it
# right: one offset in, each leg adds it to its own baseline. Do not replace this with an
# absolute-seed override; that hands the group structure back to the caller.
EST_SEED=$(( 42 + ${MNV_EST_SEED_OFFSET:-0} ))
# MEMBER AXIS: outputs move into member_kNNNNNN/ when an offset is DECLARED, and are byte-identical
# to the archive paths when it is not. Assigned BEFORE the python3 line, never inside its
# continuation -- an assignment between a \-continued command and its continuation makes bash
# swallow the continuation as a comment, which is the defect that cost this diff a review round.
SWEEP_OUTDIR="$(mr_dir_prefix "${REPO}/nd-unfolding/uq_5d/universe_sweep_bkgaware")"
python3 sweep_bank_5d.py --run --estimator-seed ${EST_SEED} --universe "$U" \
  --bankdir "${REPO}/nd-unfolding/bank_sweep_5d_bkgaware" \
  --outdir "${SWEEP_OUTDIR}" --iters 5
echo "[sweep-run-bkg] task=${SLURM_ARRAY_TASK_ID} done $(date -u '+%F %T UTC')"
