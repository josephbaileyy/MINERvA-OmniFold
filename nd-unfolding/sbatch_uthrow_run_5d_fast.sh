#!/bin/bash
#SBATCH --job-name=uthrow5d_runF
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=32 --mem=90G --time=06:00:00
#SBATCH --array=0-39%40
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=uq_5d/uthrow5d_runF_%a_%A.out --error=uq_5d/uthrow5d_runF_%a_%A.err
# FAST variant of sbatch_uthrow_run_5d.sh (school account, 2026-07-12).
# 40 tasks x 4 throws = 160 throws, offsets t*4..t*4+3 -> union 0-159. Fine-grained
# + %40 all-concurrent on `shared` QOS (backfills even with a jammed queue) to
# beat the 6-in-flight interactive path. Writes to a SEPARATE dir so the batch
# id-layout (4 throws/file) never collides with the interactive layout (1/file);
# do_combine hard-fails on duplicate throw ids, so the two must stay in separate
# globs. Atomic-save (os.replace) means a wall-kill re-runs the whole task cleanly.
set -eo pipefail
# --- OI-136 / Joseph's ruling 17, 2026-08-22: TWO ROOTS, BOTH MANDATORY, NEITHER DEFAULTED -------
# This line used to read `REPO="<the canonical checkout>"` unconditionally, and every `source`, every
# `cd` and every `python3` below hung off it. That decides the EXECUTING TREE before any interpreter
# or guard starts, so no amount of Python-side work can reach it -- "the wrong root is selected
# before Python or the guard starts" (Joseph, ruling 18).
#   MNV_CODE_ROOT  the approved clean execution tree. Every `.sh` sourced and every `.py` executed or
#                  imported must resolve under it; it is immutable and `git status --porcelain`-empty
#                  for the duration of the run, at a named sha recorded in the run receipt.
#   MNV_DATA_ROOT  the working directory for inputs and products. The canonical checkout is
#                  acceptable in THIS ROLE ONLY. Nothing is executed or imported from it.
# WHY TWO AND NOT ONE: a clean checkout cannot simultaneously host ~47.7 GB of gitignored member
# products and remain clean, and `of_inputs_5d.npz` is absent from a fresh clone, so a clean tree
# cannot serve as the working directory at all.
# NO `${VAR:-<hardcode>}` DEFAULT ANYWHERE: a default is the hardcode wearing a flag, and a silently
# empty defaulted variable makes every path below name a different subject without erroring. Same
# mandatory form, and the same reason, as `pet/sbatch_gate6_leg0_tier_calibration_array.sh:64`.
# The two roots MAY name the same directory; nothing here requires them to differ.
CODE_ROOT="${MNV_CODE_ROOT:?set MNV_CODE_ROOT to the approved clean execution tree -- a checkout at a named sha with git status --porcelain empty. It is NOT the data root.}"
DATA_ROOT="${MNV_DATA_ROOT:?set MNV_DATA_ROOT to the tree holding the inputs for this leg and receiving its products. Nothing is executed or imported from it.}"
source "${CODE_ROOT}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1 OMP_NUM_THREADS=32 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 \
       NUMEXPR_NUM_THREADS=2 VECLIB_MAXIMUM_THREADS=2
cd "${DATA_ROOT}/nd-unfolding"; mkdir -p uq_5d/uthrow_slabs_5d_sb
source "${CODE_ROOT}/lib/resume_guard.sh"
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
# RULING 17, THE SHELL HALF: `lib_member_resume.sh` is an EXECUTED repository file, so it must come
# from the code root. The resolver above may legitimately pick MNV_LAUNCHER_DIR, `dirname
# $BASH_SOURCE` or `scontrol Command`; this asserts that whichever it picked is
# ${MNV_CODE_ROOT}/nd-unfolding and FAILS CLOSED if it is not. Without it a launcher can be deployed
# in the code root and still source another tree's library with nothing saying so.
#
# IT IS PLACED AFTER THE `source`, NOT BEFORE, AND THAT IS A DELIBERATE AND DISCLOSED COMPROMISE.
# The resolver block above is extracted VERBATIM and pinned BYTE-IDENTICAL across all eight
# launchers by `tests/test_uq_remediation.py::LibraryResolverSurvivesSbatch`, whose window runs from
# `# --- M(ii) member axis: LOCATE` to this `source` line inclusive. A check inserted INSIDE that
# window would (a) silently change what that test extracts and (b) be executed by it as a fragment
# in which `CODE_ROOT` is not defined -- the same defect shape as an extracted tail losing the
# `set -eo pipefail` above its cut. Measured, not predicted: placing it inside turned three of that
# class's arms red. The residual exposure is therefore any side effect the wrong tree's library has
# AT SOURCE TIME; it defines functions, and nothing downstream of here runs before this exits 2.
if [[ "$(cd "$_mr_lib" 2>/dev/null && pwd -P)" != "$(cd "${CODE_ROOT}/nd-unfolding" 2>/dev/null && pwd -P)" ]]; then
  echo "[member] FAIL: lib_member_resume.sh resolved to '${_mr_lib}', which is not" >&2
  echo "[member]   \${MNV_CODE_ROOT}/nd-unfolding = '${CODE_ROOT}/nd-unfolding'." >&2
  echo "[member]   Refusing: the member axis would run from a tree this job did not approve." >&2
  exit 2
fi
SLAB_DIR="$(mr_dir_prefix uq_5d/uthrow_slabs_5d_sb)"
OFF=$(( SLURM_ARRAY_TASK_ID * 4 ))
# M(ii) OFFSET HOOK (spec (B) option (ii), BEN-461). The launcher keeps its OWN baseline
# literal, so MNV_EST_SEED_OFFSET=0 -- the default -- reproduces the archive EXACTLY and the
# two coherence groups are preserved BY CONSTRUCTION rather than by the driver getting it
# right: one offset in, each leg adds it to its own baseline. Do not replace this with an
# absolute-seed override; that hands the group structure back to the caller.
EST_SEED=$(( 1000 + ${MNV_EST_SEED_OFFSET:-0} ))
python3 "${CODE_ROOT}/nd-unfolding/unified_throw_cov_5d.py" --throws 4 --throw-offset ${OFF} --draw-seed 1000 --estimator-seed ${EST_SEED} \
  --bank bank_uthrow_5d --iters 5 --invalid-ratio neutral \
  --out "${SLAB_DIR}/uthrow5d_slab_${SLURM_ARRAY_TASK_ID}.npz"
