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
# R1 RULED (C, db5b3931 §12): _sb IS THE CANONICAL NAMESPACE FOR BOTH LEGS.
# receipt_construction_contract_5d.py:313-314 binds throw_slabs_sb AND block_slabs_sb, corroborated by
# the digest-bearing slab manifest, the fast combine's globs and the fast run's writes. So the CONSUMER
# was right all along and THIS launcher's literal is the single misaligned one in the chain.
#
# A MEMBER therefore writes into the _sb namespace, matching its own combine -- which makes the
# zero-slab SystemExit unreachable per member instead of certain.
#
# THE UNSET PATH IS DELIBERATELY LEFT ON THE NON-_sb LITERAL, and my earlier reason for that was WRONG.
# I said repointing it would move archive behaviour. It would not -- the archive IS _sb. What it would
# actually do is let a NON-SCAN run write INTO THE LIVE ARCHIVE DIRECTORY, a destructive edge on 124
# receipt-bound slabs. Right action, wrong reason, and the real reason is worse than the one I gave.
# The tracked producer's wrong literal is a PRE-EXISTING defect needing its own change and its own
# authorization; it is not folded into the scan.
if mr_declared; then
  BLOCK_DIR="$(mr_dir_prefix uq_5d/block_slabs_5d_sb)"
else
  BLOCK_DIR="uq_5d/block_slabs_5d"
fi
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
