#!/bin/bash
#SBATCH --job-name=uthrow5d_combF
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=16 --mem=90G --time=03:00:00
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=uq_5d/uthrow5d_combF_%j.out --error=uq_5d/uthrow5d_combF_%j.err
# FAST-path combine (school account, 2026-07-12): aggregate the batch-dir throws
# (union 0-159, fixed seed 1000) + matched block endpoints into the headline ROOT.
# --null repeats CV at the identical seed and must be zero (no jitter subtraction).
# Submit with --dependency=afterok:<throwjob>:<blockjob>. Writes the SAME target
# the interactive supervisor watches, so producing it here auto-stops that loop.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"
# M(ii) OFFSET HOOK (spec (B) option (ii), BEN-461). The launcher keeps its OWN baseline
# literal, so MNV_EST_SEED_OFFSET=0 -- the default -- reproduces the archive EXACTLY and the
# two coherence groups are preserved BY CONSTRUCTION rather than by the driver getting it
# right: one offset in, each leg adds it to its own baseline. Do not replace this with an
# absolute-seed override; that hands the group structure back to the caller.
# MEMBER AXIS. THE _sb LITERALS BELOW ARE DELIBERATELY UNCHANGED. This combine reads
# block_slabs_5d_sb/ while sbatch_uthrow_block_5d.sh WRITES block_slabs_5d/ -- a real, pre-existing
# mismatch (both namespaces hold separately populated old products, 8 and 36 npz). Repointing the
# literal would change what a NON-SCAN run reads, which is archive behaviour and not mine to move.
# WHAT NAMESPACING DOES TO IT, reported as a SIDE EFFECT rather than presented as a fix: inside a
# member the block glob resolves to block_slabs_5d_sb/member_kNNNNNN/, which the block leg never
# writes, so the combine hits unified_throw_cov.py's "no block-unit slabs match" SystemExit instead
# of silently consuming ARCHIVED _sb blocks. The mismatch becomes LOUD inside a member and is
# unchanged outside one. Which namespace is intended is still an open decision.
EST_SEED=$(( 1000 + ${MNV_EST_SEED_OFFSET:-0} ))
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
THROW_DIR="$(mr_dir_prefix uq_5d/uthrow_slabs_5d_sb)"
# THE BLOCK/COMBINE EDGE, RESOLVED FOR MEMBERS ONLY AND THE ARCHIVE PATH LEFT ALONE.
# Pre-existing: this combine globs block_slabs_5d_sb/ while sbatch_uthrow_block_5d.sh WRITES
# block_slabs_5d/, and BOTH namespaces hold separately populated old products (36 and 8 npz). I
# reported earlier that namespacing "may resolve it as a side effect" -- IT DOES NOT. Two independent
# reviewers confirmed it makes the mismatch FATAL FOR EVERY MEMBER: the member glob resolves to
# block_slabs_5d_sb/member_kNNNNNN/, which the block leg never writes, so every member dies on
# "no block-unit slabs match". Loud, but a total scan failure.
# So: a DECLARED member reads the namespace its own block leg writes; an UNDECLARED run reads exactly
# what it read before. Repointing the literal unconditionally would move archive behaviour, which is
# C's decision and not mine -- WHICH NAMESPACE IS CANONICAL IS STILL OPEN.
# REVERTED to the plain namespaced form once R1 ruled _sb canonical. I had made this conditional so a
# member's combine would read the block leg's non-_sb namespace -- correct as a way to make the two
# agree, wrong about WHICH one to agree on. The consumer was never the misaligned side.
BLOCK_DIR_SB="$(mr_dir_prefix uq_5d/block_slabs_5d_sb)"
ROOT_OUT="$(mr_prefix uq_5d/unified_throw_cov_5d.root)"
python3 unified_throw_cov_5d.py --draw-seed 1000 --estimator-seed ${EST_SEED} \
  --combine "${THROW_DIR}/uthrow5d_slab_*.npz" \
  --expected-throws 0-159 \
  --block-slabs "${BLOCK_DIR_SB}/block5d_*.npz" \
  --bank bank_uthrow_5d --iters 5 --null \
  --out-root "${ROOT_OUT}"
