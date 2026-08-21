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

# THE MISSING DEPENDENCY, restored 2026-08-21 under Joseph's amended ruling 1, ATOMICALLY WITH THE
# COMB GUARD BELOW AND NEVER WITHOUT IT. lib_member_resume.sh's own header says it "Requires
# lib/resume_guard.sh to be sourced first" and this launcher never did, while all three sibling
# launchers that call `mr_run` do. MEASURED, not inferred: with only lib_member_resume.sh sourced,
# every rg_* helper is undefined and `mr_run` dies at `rg_begin: command not found`
# (lib_member_resume.sh:217) under the `set -eo pipefail` above -- BEFORE it invokes its command. So
# both the declared and undeclared routes have been failing at the first mr_run, and the destructive
# undeclared re-run over the 41.44 GB intermediate was NOT reachable.
#
# RESTORING THIS LINE IS WHAT MAKES THAT RE-RUN REACHABLE. That is precisely why it may not land, be
# deployed, or be launched on its own: a source-only change re-arms the 2.087 TiB hazard with nothing
# in front of it. The guard below is the other half and they are one commit.
#
# Resolved from `_mr_lib`, NOT from `${REPO}` -- the block above exists because a candidate that can
# resolve to the CANONICAL library instead of the frozen one reintroduces the frozen-deployment defect
# invisibly. The sibling launchers use `${REPO}/lib/resume_guard.sh`; that is wrong here for the same
# reason this file resolves lib_member_resume.sh the way it does.
#
# WHY THIS SITS *AFTER* THE lib_member_resume.sh SOURCE AND NOT BEFORE IT, which is a deliberate
# deviation from the letter of the ruling and satisfies its substance. The resolver block above is
# PINNED BYTE-IDENTICAL across all eight launchers that carry it
# (test_uq_remediation.py::test_EVERY_launcher_carrying_the_resolver_carries_a_BYTE_IDENTICAL_copy),
# and it ENDS on the lib_member_resume.sh line -- so "before lib_member_resume.sh" is necessarily
# INSIDE the pinned region. Putting it there diverged this launcher's digest from the other seven, and
# the fail-closed check also broke
# test_a_DECOY_library_in_the_spool_would_be_used_and_that_is_CORRECT, whose docstring says the
# semantics are pinned so nobody "fixes" them. Both measured, not predicted.
#
# Sourcing here is equivalent because NOTHING between the two lines calls an rg_* helper:
# lib_member_resume.sh makes every rg_* call from INSIDE a function body (`:173,:190,:204,:217,:225`),
# and `mr_require_valid_offset` calls none at all. The requirement that actually matters -- BEFORE ANY
# mr_* CALL -- holds: the first is the guard below.
_mr_rg="${_mr_lib}/../lib/resume_guard.sh"
if [[ ! -r "$_mr_rg" ]]; then
  echo "[member] FAIL: cannot read ${_mr_rg}" >&2
  echo "[member]   lib_member_resume.sh requires it, and without it every mr_* call dies at" >&2
  echo "[member]   'rg_begin: command not found'. Failing closed rather than proceeding into a" >&2
  echo "[member]   launcher whose resume guards silently do not exist." >&2
  exit 2
fi
source "$_mr_rg"


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
# ========================= THE COMB GUARD -- Joseph's amended ruling 1, 2026-08-21 =================
# Authorized shape, verbatim from the ruling. NOT the proposed `mr_run` -> `mr_skip_if_complete`
# one-word substitution, which was withdrawn because `rg_skip_if_complete` can ADOPT an unmarked
# product on a bare size check and WRITE a marker -- an action the ruling forbids.
#
#   declared   + matching marker            -> reuse
#   declared   + incomplete                 -> generate
#   declared   + wrong-member marker         -> exit 3   (raised inside mr_skip_if_complete, untouched)
#   undeclared + marker bound to size+mtime  -> reuse
#   undeclared + absent/stale/malformed/unbound marker -> exit 5
#   RESUME_ADOPT_LEGACY=1 (either regime)    -> exit 5
#   undeclared + RESUME_FORCE=1              -> exit 5
#
# EXIT 5 IS NEW AND DELIBERATE. Exit 3 stays RESERVED for the wrong-member-marker condition that
# lib_member_resume.sh already raises; reusing it here would make two unrelated causes
# indistinguishable in the exit code.
if [[ "${RESUME_ADOPT_LEGACY:-0}" == "1" ]]; then
  echo "[fin-bkg] REFUSE (exit 5): RESUME_ADOPT_LEGACY=1 is FORBIDDEN for ${COMB}, both regimes." >&2
  echo "[fin-bkg]   It would adopt this product on a bare SIZE check and WRITE a completion marker." >&2
  echo "[fin-bkg]   resume_guard.sh names that branch the BEN-023 defect; on a 41.44 GB intermediate" >&2
  echo "[fin-bkg]   a partial file is indistinguishable from a complete one. Marker backfill is NOT" >&2
  echo "[fin-bkg]   authorized, and it must never be performed by setting this variable." >&2
  exit 5
fi
if mr_declared; then
  if mr_skip_if_complete "${COMB}"; then
    echo "[fin-bkg] MEMBER $(mr_member_root): reusing complete ${COMB} (marker matches this member)"
  else
    echo "[fin-bkg] analyze start $(date -u '+%F %T UTC') on $(hostname)"
    mr_run "${COMB}" python3 analyze_universes_5d.py \
      --cv "${CV}" \
      --glob "${SWEEP_GLOB}" \
      --add-norm 0.014 \
      --bootstrap-cov "${STAT_COV}:hCov_stat5d_reported" \
                      "${ML_COV}:hCov_mlsplit5d_reported" \
      --outdir "${OUTD}/" --out-root uq_universe_5d_covariance_combined_bkgaware.root
  fi
else
  # UNDECLARED: REUSE-OR-REFUSE. The analyzer is not reachable from this branch at all.
  if [[ "${RESUME_FORCE:-0}" == "1" ]]; then
    echo "[fin-bkg] REFUSE (exit 5): RESUME_FORCE=1 is forbidden on the undeclared route." >&2
    echo "[fin-bkg]   Forcing here means re-running the analyzer over the do-not-delete intermediate." >&2
    exit 5
  fi
  # DELIBERATELY NOT `rg_is_complete`: it RETURNS SUCCESS for a marker carrying NEITHER size nor
  # mtime (its legacy honour branch for run_p4_unfold_std.sh markers). The ruling requires a marker
  # EXPLICITLY BOUND to size and mtime, so both fields must be present AND match. An unbound legacy
  # marker is a refusal here, not a pass.
  _comb_marker="$(rg_marker_path "${COMB}")"
  _comb_msize=""; _comb_mmtime=""
  if [[ -s "$_comb_marker" ]]; then
    _comb_msize="$(rg__marker_field "$_comb_marker" size)"   || _comb_msize=""
    _comb_mmtime="$(rg__marker_field "$_comb_marker" mtime)" || _comb_mmtime=""
  fi
  if [[ -e "${COMB}" && -n "$_comb_msize" && -n "$_comb_mmtime" \
        && "$_comb_msize"  == "$(rg_stat_size  "${COMB}")" \
        && "$_comb_mmtime" == "$(rg_stat_mtime "${COMB}")" ]]; then
    echo "[fin-bkg] undeclared: reusing ${COMB} on a marker BOUND to size=${_comb_msize} mtime=${_comb_mmtime}"
  else
    echo "[fin-bkg] REFUSE (exit 5): the undeclared route may only REUSE ${COMB}, never produce it." >&2
    echo "[fin-bkg]   marker:        ${_comb_marker}" >&2
    echo "[fin-bkg]   product exists: $([[ -e "${COMB}" ]] && echo yes || echo NO)" >&2
    echo "[fin-bkg]   marker size:   ${_comb_msize:-<absent>}   file size:  $(rg_stat_size  "${COMB}" 2>/dev/null || echo '<unreadable>')" >&2
    echo "[fin-bkg]   marker mtime:  ${_comb_mmtime:-<absent>}  file mtime: $(rg_stat_mtime "${COMB}" 2>/dev/null || echo '<unreadable>')" >&2
    echo "[fin-bkg]   A marker that is absent, stale, malformed, or missing either binding is a" >&2
    echo "[fin-bkg]   REFUSAL. Running the analyzer here would re-derive the 41.44 GB intermediate" >&2
    echo "[fin-bkg]   in place (2.087 TiB to regenerate). Content-validating this product and" >&2
    echo "[fin-bkg]   backfilling its marker is a SEPARATE ruling and is NOT authorized here --" >&2
    echo "[fin-bkg]   and it must not be done by setting RESUME_ADOPT_LEGACY=1." >&2
    exit 5
  fi
fi
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
  #   EXPIRY CONDITION: remedy (A) **VERIFIED BY C** -- NOT merely landed.
  #   (A) HAS NOW LANDED, BY MY HAND, on all three writers: adopt_unified_5d.py,
  #   unfold_nd_omnifold_unbinned.py (C's widening, on D's enumeration), and analyze_universes_5d.py --
  #   the third being the one NOBODY HAD ENUMERATED, whose silence blocked g1's seed from reaching adopt
  #   at all. So the original expiry, "remedy (A) landing", IS TECHNICALLY MET.
  #   I AM NOT LIFTING THE PAUSE ON THAT BASIS. C ruled (A) mandatory before admission; whether THIS
  #   implementation satisfies that ruling is C's judgement about my code, and letting the implementer
  #   declare their own work sufficient would make the blocker self-clearing. Same distinction as gate 2:
  #   a comparator existing is not a comparator being right, already proved once when the thing that
  #   existed read 0.00935% of the payload.
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
# REWIRED TO REMEDY (A)'s WRAPPER 2026-08-20 on Joseph's authorization, scoped by him to THESE TWO
# CALL SITES ONLY ("yes, those two lines only"). The other six scripts that invoke
# adopt_unified_5d.py directly are OUT OF SCOPE and deliberately unchanged: this is the only
# declared-member adoption path, so it is the only one D2 blocks. Widening it would be a
# frozen-provenance change nobody authorised.
#
# THE LITERAL `--` IS MANDATORY, NOT COSMETIC. mii_adopt_unified_5d_stamped.py:431-437 splits on
# `--` itself and REFUSES bare positionals; without it argparse exits 2. That loudness is the
# point -- a silently dropped `--cv-centered` would build the MEAN-centered product under the
# CV-centered product's NAME, which that file calls "the single worst outcome available here":
# two roots differing in nothing but payload and centering. Paths stay in the HEAD (one copy,
# forwarded verbatim); only child-specific flags go in the tail. Never put --out in the tail --
# argparse takes the LAST occurrence, so it would redirect the child while the wrapper stamps a
# file the child did not write, and report success.
python3 mii_adopt_unified_5d_stamped.py \
  --uthrow "${UTHROW}" \
  --combined "${COMB}" \
  --out "${OUTD}/uq_universe_5d_covariance_combined_bkgaware_uthrow.root"
echo "[fin-bkg] adopt (CV-centered, F7) $(date -u '+%F %T UTC')"
python3 mii_adopt_unified_5d_stamped.py \
  --uthrow "${UTHROW}" \
  --combined "${COMB}" \
  --out "${OUTD}/uq_universe_5d_covariance_combined_bkgaware_uthrow_cvcentered.root" \
  -- --cv-centered
echo "[fin-bkg] done $(date -u '+%F %T UTC')"
ls -la "${OUTD}"/*.root
