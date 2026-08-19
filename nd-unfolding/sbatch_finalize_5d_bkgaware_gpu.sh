#!/bin/bash
#SBATCH --job-name=fin5dBKG
#SBATCH --account=m3246_g
#SBATCH --qos=shared --constraint=gpu --nodes=1 --ntasks=1 --gpus-per-task=1 --cpus-per-task=32 --time=01:30:00
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=uq_4d/fin5dBKG_%j.out --error=uq_4d/fin5dBKG_%j.err
# KNOWN_ISSUES #13 finalize (2026-07-14): assemble the bkgaware C_syst budget and
# adopt the unified-throw inflation (both mean- and CV-centered). C_stat/C_ML are
# #13-invariant -> reuse existing uq_cov_stat_5d.root / uq_cov_mlsplit_5d.root; only
# analyze_universes_5d is re-run on the bkgaware vertical sweep. NON-DESTRUCTIVE:
# distinct _bkgaware outputs; the baseline budget stays as the CV-background comparator.
set -eo pipefail
export HOME=/global/homes/j/josephrb
export ROOT628_PREFIX=/global/homes/j/josephrb/.conda/envs/root_6_28
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"
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

# ============================ B1: THE MEMBER-LOCAL CONSUMER CHAIN ==================================
# WHY THIS SCRIPT IS THE ONE THAT NEEDED IT, and the defect is written in its own header above:
#   "C_stat/C_ML are #13-invariant -> reuse existing uq_cov_stat_5d.root / uq_cov_mlsplit_5d.root"
# That reasoning is CORRECT for what this script was written for -- a background-treatment comparison in
# which only the vertical sweep changes. It is EXACTLY WRONG FOR A MEMBER, whose entire premise is a
# DIFFERENT ESTIMATOR SEED. Run unmodified inside a member, `--bootstrap-cov uq_cov_stat_5d.root` injects
# THE ARCHIVE'S C_stat into the member's combined covariance and the member's own 100 replicas are
# computed and then ignored -- the exact consumer defect the member axis exists to fix.
#
# STAGE 0 MADE THAT QUANTITATIVE RATHER THAN A WORRY: the estimator seed moves C_stat's replicas across
# essentially the whole reported support (three DISTINCT verdicts, 0/1200/2400, jobs 57252337-9). So the
# reuse substitutes a covariance MEASURED to differ, on the one leg it has been measured on.
#
# UNDECLARED BEHAVIOUR IS BYTE-IDENTICAL: every path below reduces to its original literal and the two
# combines do not run, so this remains the CV-background comparator it has always been.
# --cv IS MEMBER-SCOPED. C RULED **SUBSTITUTE**, REVERSING MY HOLD, AND THE REASON IS ABOUT SPREADS
# RATHER THAN VALUES (DETERMINATION-20260818-lanec-anchor-recompute-and-lateral-in-g1.md sections 17-18).
#
# I had proposed pinning to the archive's CV, documented as a choice. C's own earlier sentence --
# "substituting would inject a difference that is NOT estimator noise, which is worse than pinning" --
# is the right test for comparing VALUES. THE BAR COMPARES SPREADS, and there the arithmetic inverts:
#     PIN to cv_arch          sd_j(0.014 * ||cv_arch||) is EXACTLY 0
#                             -> the flat-norm term contributes NOTHING to either leg's spread
#     SUBSTITUTE cv_uni(j)    sd is driven by the seed response
#                             -> the term contributes its real sensitivity
# Whatever distinguishes the two CV products is COMMON-MODE across all fifty members and CANCELS IN sd
# to first order; it shifts the operating point (second order) and leg A's denominator by a measured
# 0.03%. IT DOES NOT ENTER THE SPREAD. So pinning zeroes this term's spread contribution at FIRST order,
# AND THE DIRECTION OF THE BIAS IS TOWARD *MET* -- a pass bought by omitting a term. That direction is
# why this is not a free choice, and C asked that the direction be recorded and not just the decision.
#
# THE EVIDENCE THAT THE TWO CVs ARE THE SAME QUANTITY: np.array_equal(a > 0, b > 0) is TRUE -- IDENTICAL
# SUPPORT MEMBERSHIP bin-for-bin across all 10,694 bins -- plus integrated totals agreeing to 0.03%. A
# different observable, binning or iteration count would not preserve support membership exactly.
#
# STILL TRUE AND STILL WORTH KNOWING: the cv CANCELS ALGEBRAICALLY in the 188-universe systematic
# covariance itself. `analyze_universes_5d.py:167-172` forms D_i = u_i - cv then subtracts the column
# mean, so Z_i = u_i - ubar and the covariance is BIT-IDENTICAL under any cv (verified, max abs diff
# exactly 0.0). So this substitution changes the FLAT-NORM BAND and the REPORTED MASK, and nothing else.
# 0.014 itself stays member-invariant; that was never in question.
#
# THE MASK REMAINS THE OPEN RISK AND MUST NOT BE CHECKED BY COUNTING. Two supports of EQUAL SIZE can
# differ in MEMBERSHIP, which shifts the flat ordering and makes a bit-exact comparison compare the
# WRONG PAIRS silently. Use `p4_lib.py:1196 mask_order_hash`, not a bin count -- C's instruction, and the
# archive's own two CVs are a ready-made positive control for it (same membership, not merely same count).
CV_ARCHIVE="products/5d/xsec_5d_MEFHC_5iter_lgbm.root"
if mr_declared; then
  CV="$(mr_prefix uq_5d/universe_sweep_bkgaware)/5d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root"
else
  CV="${CV_ARCHIVE}"
fi
OUTD="$(mr_dir_prefix uq_5d/universe_stage2_5d_bkgaware)"
COMB="${OUTD}/uq_universe_5d_covariance_combined_bkgaware.root"
SWEEP_GLOB="$(mr_prefix uq_5d/universe_sweep_bkgaware)/5d_xsec_*_uni_full_*.root"
UTHROW="$(mr_prefix uq_5d/unified_throw_cov_5d.root)"
STAT_COV="$(mr_prefix uq_cov_stat_5d.root)"
ML_COV="$(mr_prefix uq_cov_mlsplit_5d.root)"
mkdir -p "${OUTD}"

if mr_declared; then
  # THE TWO MEMBER-LOCAL COMBINES. `--expected-ids` is an EXACT-POPULATION validator and is kept at the
  # full ranges on purpose: a member with a partial replica set must REFUSE rather than quietly combine
  # what it has. That is the barrier that makes a member's C_stat comparable to the archive's at all.
  echo "[fin-bkg] MEMBER $(mr_member_root): building this member's OWN C_stat and C_ML"
  mr_run "${STAT_COV}" python3 combine_cov_nd.py     --glob "$(mr_prefix boot_nd_5d)/res_boot_*.npz" --expected-ids 1-100 --cv "${CV}"     --tag stat5d --out "${STAT_COV}"
  mr_run "${ML_COV}" python3 combine_cov_nd.py     --glob "$(mr_prefix seedscan_split_5d)/res_split_*.npz" --expected-ids 1-24 --cv "${CV}"     --tag mlsplit5d --out "${ML_COV}"
else
  echo "[fin-bkg] undeclared: reusing the archive's C_stat/C_ML, per this script's original contract"
fi
echo "[fin-bkg] analyze start $(date -u '+%F %T UTC') on $(hostname)"
mr_run "${COMB}" python3 analyze_universes_5d.py \
  --cv "${CV}" \
  --glob "${SWEEP_GLOB}" \
  --add-norm 0.014 \
  --bootstrap-cov "${STAT_COV}:hCov_stat5d_reported" \
                  "${ML_COV}:hCov_mlsplit5d_reported" \
  --outdir "${OUTD}/" --out-root uq_universe_5d_covariance_combined_bkgaware.root
if mr_declared; then
  # ================= B1 STOPS HERE, AND THE STOP IS DELIBERATE AND VISIBLE ==========================
  # C ruled remedy (A) -- identity stamps on the adopted roots -- MANDATORY rather than preferable, and
  # `mii_anchor_comparator` shows why in the direction that matters: `adopt_unified_5d.py` writes NO
  # identity key, so a member's adopted root FAILS `anchor_identity` UPSTREAM of every payload and
  # recomputation question. The gate is not unverified, it is UNREACHABLE. Producing these two 892 MB
  # artifacts now would build the member's citable products in a form stage 1 cannot admit, at ~0.9 GB
  # each, and they would have to be rebuilt after (A) lands.
  #
  # REFUSING LOUDLY RATHER THAN OMITTING SILENTLY: a script that quietly produced only the intermediate
  # would look complete, and the missing artifacts would be discovered by whatever consumed them next.
  # THE CUT IS A **PAUSE** WITH AN EXPIRY CONDITION, NOT A BOUNDARY -- C's correction, and it changes
  # how this must be reported rather than what it does.
  #   EXPIRY CONDITION: remedy (A) landing on adopt_unified_5d.py (identity stamps), which C has since
  #   WIDENED to cover unfold_nd_omnifold_unbinned.py / LATERAL_CV as well, on D's enumeration.
  # WHY IT CANNOT BE READ AS A BOUNDARY: `sqrt_tr_old` -- THE BAR'S OWN OPERAND -- is written at
  # adopt_unified_5d.py:177, INSIDE steps (4)/(5). So stopping here means stage 1 cannot compare the
  # quantity the bar is about. A STOP-AFTER-(3) MEMBER IS A STAGE 1 *NOT ATTEMPTED*, NOT ONE AWAITING
  # PAPERWORK, AND THE TWO READ IDENTICALLY IN A STATUS TABLE. That is the whole reason to record the
  # expiry rather than the rationale.
  # AND NOTHING IS DELETABLE DURING THE PAUSE. Section 11g gates deletion on MVFINAL_j, which needs
  # (4)/(5) -- so "stop after (3)" combined with "11g releases the 41 GB" would delete the ONLY INPUT to
  # the steps that have not run. The intermediate stays until MVFINAL_j exists and validates.
  echo "[fin-bkg] MEMBER PAUSE (not a boundary): intermediate built at ${COMB}" >&2
  echo "[fin-bkg]   EXPIRY: remedy (A) -- identity stamps on adopt_unified_5d.py AND" >&2
  echo "[fin-bkg]           unfold_nd_omnifold_unbinned.py. Until then this member is STAGE 1" >&2
  echo "[fin-bkg]           NOT ATTEMPTED, not stage 1 pending." >&2
  echo "[fin-bkg]   DO NOT DELETE ${COMB} -- 11g gates deletion on MVFINAL_j, which needs (4)/(5)." >&2
  echo "[fin-bkg]   ADOPTION IS NOT RUN FOR A MEMBER until remedy (A) lands -- adopt_unified_5d.py" >&2
  echo "[fin-bkg]   writes no estimator_seed/est_seed_offset, so the adopted roots cannot satisfy" >&2
  echo "[fin-bkg]   anchor_identity and stage 1 could not admit them. This is C's ruling, not a" >&2
  echo "[fin-bkg]   limitation of this script." >&2
  ls -la "${OUTD}"/*.root 2>/dev/null || true
  exit 0
fi
echo "[fin-bkg] adopt (mean-centered) $(date -u '+%F %T UTC')"
python3 adopt_unified_5d.py \
  --uthrow "${UTHROW}" \
  --combined "${COMB}" \
  --out "${OUTD}/uq_universe_5d_covariance_combined_bkgaware_uthrow.root"
echo "[fin-bkg] adopt (CV-centered, F7) $(date -u '+%F %T UTC')"
python3 adopt_unified_5d.py \
  --uthrow "${UTHROW}" \
  --combined "${COMB}" \
  --cv-centered \
  --out "${OUTD}/uq_universe_5d_covariance_combined_bkgaware_uthrow_cvcentered.root"
echo "[fin-bkg] done $(date -u '+%F %T UTC')"
ls -la "${OUTD}"/*.root
