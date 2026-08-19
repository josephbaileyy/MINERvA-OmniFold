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
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; ND="${REPO}/nd-unfolding"
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
source "${REPO}/setup_salloc_env.sh"; cd "${ND}"
OMNIFILE="${ND}/runEventLoopOmniFold_5D_MEFHC_universes_full_bkgaware.root"
FLUX_MC="${REPO}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root"
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
  mr_run "${XSEC_OUT}" python3 unfold_nd_omnifold_unbinned.py \
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
mr_run "${XSEC_OUT}" python3 unfold_nd_omnifold_unbinned.py \
    --omnifile "${OMNIFILE}" --mcfile "${FLUX_MC}" \
    --axes eavail,q3,W --iters 5 --use-weights --estimator lgbm --seed ${EST_SEED} \
    --closure-slack 5000 \
    --universe "${UNIVERSE}" --out "${XSEC_OUT}"
echo "[det-bkg] done ${UNIVERSE} $(date -u '+%F %T UTC')"
