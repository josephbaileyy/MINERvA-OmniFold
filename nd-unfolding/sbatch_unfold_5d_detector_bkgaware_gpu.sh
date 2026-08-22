#!/bin/bash
#SBATCH --job-name=det5dBKG
#SBATCH --account=m3246_g
#SBATCH --qos=shared --constraint=gpu --nodes=1 --ntasks=1 --gpus-per-task=1 --cpus-per-task=32 --time=04:00:00
#SBATCH --array=0-18%8
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=uq_5d/det5dBKG_%a_%A.out --error=uq_5d/det5dBKG_%a_%A.err
# KNOWN_ISSUES #13 LATERAL leg (2026-07-14), GPU variant. The bank sweep cannot
# carry the muon/beam bands' SHIFTED background kinematics (sim_background_<axis>_
# <band>_<idx>), so the 9 detector bands (6 muon/beam laterals + 3 GEANT = 18
# universes) + the matched CV re-run through the DIRECT driver, which threads
# --universe into collect_bkg_nd (per-universe background, unfold_nd:662). Reads the
# BKGAWARE omnifile. NON-DESTRUCTIVE outdir uq_5d/universe_sweep_bkgaware (same dir
# the 169 vertical bank-sweep universes land in -> analyze globs the union = 188).
# task 0 = matched CV (no --universe); 1-18 = detector_universes.txt. ~1h, <64GB.
set -eo pipefail
export HOME=/global/homes/j/josephrb
export ROOT628_PREFIX=/global/homes/j/josephrb/.conda/envs/root_6_28
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-32}
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
# `ND` is a DATA path here: it names the omnifile, the universe list and the output directory.
ND="${DATA_ROOT}/nd-unfolding"
source "${CODE_ROOT}/lib/resume_guard.sh"

# --- OI-136 ROUND 2, 2026-08-22: EVERY production Python invocation is GUARDED, and the record is
# --- REQUIRED. Authorized by Joseph: "every production Python invocation across the eight k=0
# --- launchers is to be routed through mnv_guarded_run.py, with a required inventory", plus the
# --- contract-required executing-file parity calls and source-manifest comparison.
#
# WHY THIS IS WORTH DOING NOW AND WAS NOT BEFORE. The contract's B-1 argued a wrapper "cannot help
# them and would block the run" -- true of the PRE-REPAIR bytes, where `import xsec_nd` resolved
# under the canonical checkout and the guard correctly exited 3. That argument EXPIRED with the
# six source repairs: post-repair these entrypoints resolve under ${MNV_CODE_ROOT}, so the wrapper
# now runs GREEN and NON-VACUOUSLY -- `checked > 0` and `repo_origin_count > 0` -- which is exactly
# the positive evidence a bare exit 0 could never be.
#
# THE INVENTORY IS ONE FILE PER PROCESS, NOT ONE PER RUN. An array of 169 tasks appending to a
# single file across nodes is a corruption risk with no upside; per-process files still give F-4
# its count (inventories == guarded processes) and `mnv_import_set_ratchet.py` reads the directory.
GUARD="${CODE_ROOT}/nd-unfolding/mnv_guarded_run.py"
PARITY="${CODE_ROOT}/nd-unfolding/pet/verify_executing_copy_is_committed.py"
SRCMAN="${CODE_ROOT}/nd-unfolding/mnv_source_manifest.py"
INVDIR="${MNV_GUARD_INVENTORY_DIR:?set MNV_GUARD_INVENTORY_DIR to a run-scoped directory for the OI-136 resolved-origin records. It has no default: a guarded run that emits no record establishes nothing, and a defaulted path would put one run over another.}"
SRCMAN_RECORD="${MNV_SOURCE_MANIFEST:?set MNV_SOURCE_MANIFEST to the A-2(f) source manifest recorded from MNV_CODE_ROOT before the first sbatch. It has no default: comparing against a manifest generated now would compare the tree to itself.}"
for _mnv_tool in "$GUARD" "$PARITY" "$SRCMAN"; do
  # `! -L` because a symlink can point out of the code root while every path check still passes.
  [[ -s "$_mnv_tool" && ! -L "$_mnv_tool" ]] || {
    echo "[oi136] FAIL: required tool missing or a symlink: $_mnv_tool" >&2
    echo "[oi136]   This deployment of MNV_CODE_ROOT predates the round-2 package; re-deploy it." >&2
    exit 2; }
done
mkdir -p "${INVDIR}"
# One record per guarded process. Array task and job id are in the name so nothing collides and so
# a missing record is attributable to a task rather than merely absent.
mnv_inv() { echo "${INVDIR}/${SLURM_JOB_NAME:-nojob}.${SLURM_JOB_ID:-nojid}.${SLURM_ARRAY_TASK_ID:-na}.$1.jsonl"; }

# A-2(f): has ANY source byte in the execution tree moved since the manifest was recorded? This is
# not what the parity check below answers -- that one asks "is the file at this named path the
# COMMITTED one", per pair, against git. This asks the whole-tree question, including files nobody
# thought to name, against a snapshot. Run 4 printed `5 of 5 CURRENT` honestly while the tree it
# was executing from was not the tree anyone meant.
python3 "$SRCMAN" --repo "$CODE_ROOT" --compare "$SRCMAN_RECORD" --require-clean || {
  echo "[oi136] FAIL: the execution tree is not the tree that was approved (see above)." >&2
  exit 3; }

# A-3: bind what EXECUTES, in the shape the two Gate-5 launchers already use. NOT redundant with the
# guard and NOT sufficient: run 4 printed `5 of 5 CURRENT` honestly while the modules the
# interpreter loaded came from somewhere else entirely. The guard answers that second question.
python3 "$PARITY" --repo "$CODE_ROOT" \
  --pair "${CODE_ROOT}/nd-unfolding/unfold_nd_omnifold_unbinned.py=nd-unfolding/unfold_nd_omnifold_unbinned.py" \
  --pair "${CODE_ROOT}/nd-unfolding/sbatch_unfold_5d_detector_bkgaware_gpu.sh=nd-unfolding/sbatch_unfold_5d_detector_bkgaware_gpu.sh" \
  --pair "${CODE_ROOT}/nd-unfolding/lib_member_resume.sh=nd-unfolding/lib_member_resume.sh" \
  --pair "${GUARD}=nd-unfolding/mnv_guarded_run.py" \
  --pair "${PARITY}=nd-unfolding/pet/verify_executing_copy_is_committed.py" \
  --pair "${SRCMAN}=nd-unfolding/mnv_source_manifest.py"  || {
  echo "[oi136] FAIL: deployment parity -- the executing copies are not the committed ones in $CODE_ROOT" >&2
  exit 3; }
echo "[oi136] executing-copy parity CURRENT, source manifest identical, inventories -> ${INVDIR}"

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
source "${CODE_ROOT}/setup_salloc_env.sh"; cd "${ND}"
OMNIFILE="${ND}/runEventLoopOmniFold_5D_MEFHC_universes_full_bkgaware.root"
FLUX_MC="${DATA_ROOT}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root"
LIST="${ND}/uq_5d/detector_universes.txt"
# ITEM 7 RULING (a): THE LATERAL LEG JOINS g1 AT 42+k. Holding laterals at 42 while verticals move
# is exactly the condition unified_throw_cov.py:450-455 fails closed on ("else C_uni/C_block would
# mix estimator jitter across slabs"), reached through the one leg that has no such guard.
EST_SEED=$(( 42 + ${MNV_EST_SEED_OFFSET:-0} ))
OUTDIR="$(mr_dir_prefix "${ND}/uq_5d/universe_sweep_bkgaware")"
mkdir -p "${OUTDIR}"
[[ -s "${OMNIFILE}" ]] || { echo "[det-bkg] FAIL: bkgaware omnifile missing" >&2; exit 2; }

if [[ "${SLURM_ARRAY_TASK_ID}" -eq 0 ]]; then
  XSEC_OUT="${OUTDIR}/5d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root"
  mr_skip_if_complete "${XSEC_OUT}" && exit 0
  echo "[det-bkg] MATCHED CV node=$(hostname) $(date -u '+%F %T UTC')"
  mr_run "${XSEC_OUT}" python3 "$GUARD" --expect-root "$CODE_ROOT" --inventory "$(mnv_inv unfold_nd_cv)" -- "${CODE_ROOT}/nd-unfolding/unfold_nd_omnifold_unbinned.py" \
      --omnifile "${OMNIFILE}" --mcfile "${FLUX_MC}" \
      --axes eavail,q3,W --iters 5 --use-weights --estimator lgbm --seed ${EST_SEED} \
      --closure-slack 5000 \
      --out "${XSEC_OUT}"
  echo "[det-bkg] done CV $(date -u '+%F %T UTC')"; exit 0
fi

UNIVERSE=$(sed -n "${SLURM_ARRAY_TASK_ID}p" "${LIST}")
[[ -z "${UNIVERSE}" ]] && { echo "[det-bkg] SKIP: index ${SLURM_ARRAY_TASK_ID} beyond list"; exit 0; }
BAND="${UNIVERSE%:*}"; UIDX="${UNIVERSE#*:}"; TAG="${BAND}_${UIDX}"
XSEC_OUT="${OUTDIR}/5d_xsec_MEFHC_5iter_lgbm_uni_full_${TAG}.root"
mr_skip_if_complete "${XSEC_OUT}" && exit 0
echo "[det-bkg] universe=${UNIVERSE} node=$(hostname) task=${SLURM_ARRAY_TASK_ID} $(date -u '+%F %T UTC')"
mr_run "${XSEC_OUT}" python3 "$GUARD" --expect-root "$CODE_ROOT" --inventory "$(mnv_inv unfold_nd_universe)" -- "${CODE_ROOT}/nd-unfolding/unfold_nd_omnifold_unbinned.py" \
    --omnifile "${OMNIFILE}" --mcfile "${FLUX_MC}" \
    --axes eavail,q3,W --iters 5 --use-weights --estimator lgbm --seed ${EST_SEED} \
    --closure-slack 5000 \
    --universe "${UNIVERSE}" --out "${XSEC_OUT}"
echo "[det-bkg] done ${UNIVERSE} $(date -u '+%F %T UTC')"
