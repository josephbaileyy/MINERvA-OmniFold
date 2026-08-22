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
export PYTHONUNBUFFERED=1; cd "${DATA_ROOT}/nd-unfolding"
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
# NO BYTECODE INTO THE CODE ROOT. Every guarded science process imports repository modules from
# ${MNV_CODE_ROOT}, and CPython would write `__pycache__/*.pyc` beside them -- mutating the tree
# A-2(f) certifies and A-2(g) protects, and leaving the NEXT leg's --require-clean to refuse a tree
# the PREVIOUS leg dirtied. Under A-2(g) the write already fails, but CPython swallows that EACCES
# silently, so relying on it would make correctness depend on an absence. Set it explicitly.
export PYTHONDONTWRITEBYTECODE=1
mkdir -p "${INVDIR}"
# One record per guarded process. Array task and job id are in the name so nothing collides and so
# a missing record is attributable to a task rather than merely absent.
mnv_inv() { echo "${INVDIR}/${SLURM_JOB_NAME:-nojob}.${SLURM_JOB_ID:-nojid}.${SLURM_ARRAY_TASK_ID:-na}.$1.jsonl"; }

# A-2(f): has ANY source byte in the execution tree moved since the manifest was recorded? This is
# not what the parity check below answers -- that one asks "is the file at this named path the
# COMMITTED one", per pair, against git. This asks the whole-tree question, including files nobody
# thought to name, against a snapshot. Run 4 printed `5 of 5 CURRENT` honestly while the tree it
# was executing from was not the tree anyone meant.
# A-2(c)(d)(e)(g) RUN IN THE SAME CALL AND BEFORE ANYTHING ELSE. (d) and (e) are one hazard from
# two sides: `checkout_root_of` returns the INNERMOST match, so a checkout nested inside the code
# root resolves to ITSELF, is not --expect-root, and every module under it is refused on a tree that
# looks approved -- the recorded instance made the OI-136 ratchet read 369 instead of 58. (g) is
# enforced on the TREE's mode bits, not on what this uid happens to be able to write; see
# `writable_sources()` for why, and for what mode bits cannot do.
python3 "$SRCMAN" --repo "$CODE_ROOT" --compare "$SRCMAN_RECORD" \
  --require-clean --require-checkout --require-no-nested-checkout \
  --require-not-nested --require-readonly || {
  echo "[oi136] FAIL: the execution tree is not the tree that was approved (see above)." >&2
  exit 3; }

# A-3: bind what EXECUTES, in the shape the two Gate-5 launchers already use. NOT redundant with the
# guard and NOT sufficient: run 4 printed `5 of 5 CURRENT` honestly while the modules the
# interpreter loaded came from somewhere else entirely. The guard answers that second question.
python3 "$PARITY" --repo "$CODE_ROOT" \
  --pair "${CODE_ROOT}/nd-unfolding/combine_cov_nd.py=nd-unfolding/combine_cov_nd.py" \
  --pair "${CODE_ROOT}/nd-unfolding/analyze_universes_5d.py=nd-unfolding/analyze_universes_5d.py" \
  --pair "${CODE_ROOT}/nd-unfolding/mii_adopt_unified_5d_stamped.py=nd-unfolding/mii_adopt_unified_5d_stamped.py" \
  --pair "${CODE_ROOT}/nd-unfolding/adopt_unified_5d.py=nd-unfolding/adopt_unified_5d.py" \
  --pair "${CODE_ROOT}/nd-unfolding/sbatch_finalize_5d_bkgaware_gpu.sh=nd-unfolding/sbatch_finalize_5d_bkgaware_gpu.sh" \
  --pair "${CODE_ROOT}/nd-unfolding/lib_member_resume.sh=nd-unfolding/lib_member_resume.sh" \
  --pair "${GUARD}=nd-unfolding/mnv_guarded_run.py" \
  --pair "${PARITY}=nd-unfolding/pet/verify_executing_copy_is_committed.py" \
  --pair "${SRCMAN}=nd-unfolding/mnv_source_manifest.py"  || {
  echo "[oi136] FAIL: deployment parity -- the executing copies are not the committed ones in $CODE_ROOT" >&2
  exit 3; }
echo "[oi136] executing-copy parity CURRENT, source manifest identical, inventories -> ${INVDIR}"



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
  mr_run "${STAT_COV}" python3 "$GUARD" --expect-root "$CODE_ROOT" --inventory "$(mnv_inv combine_cov_stat)" -- "${CODE_ROOT}/nd-unfolding/combine_cov_nd.py"     --glob "$(mr_prefix boot_nd_5d)/res_boot_*.npz" --expected-ids 1-100 --cv "${CV}"     --tag stat5d --out "${STAT_COV}"
  mr_run "${ML_COV}" python3 "$GUARD" --expect-root "$CODE_ROOT" --inventory "$(mnv_inv combine_cov_ml)" -- "${CODE_ROOT}/nd-unfolding/combine_cov_nd.py"     --glob "$(mr_prefix seedscan_split_5d)/res_split_*.npz" --expected-ids 1-24 --cv "${CV}"     --tag mlsplit5d --out "${ML_COV}"
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
    mr_run "${COMB}" python3 "$GUARD" --expect-root "$CODE_ROOT" --inventory "$(mnv_inv analyze_universes_5d)" -- "${CODE_ROOT}/nd-unfolding/analyze_universes_5d.py" \
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
  # DELIBERATELY NOT `rg_is_complete`, AND STILL DELIBERATE NOW THAT THE TWO AGREE.
  #
  # The original reason was factual: rg_is_complete RETURNED SUCCESS for a marker carrying neither
  # size nor mtime (its legacy honour branch for run_p4_unfold_std.sh receipts), while the ruling
  # here requires a marker EXPLICITLY BOUND to size and mtime, both present AND matching. That
  # honour branch is GONE as of OI-142 -- rg_is_complete now refuses an unbound marker itself -- so
  # THAT SENTENCE NO LONGER DESCRIBES THE LIBRARY, and it is corrected rather than left to be read
  # as current. This route was never exposed to the defect; it is recorded here as the reason the
  # code does not change.
  #
  # THE CHECK STAYS INLINE ANYWAY, and the reason is now the ruling rather than a library bug: what
  # the undeclared route may reuse is decided by Joseph's amended ruling, not by whatever the shared
  # default happens to be this week. Routing it through rg_is_complete would silently re-delegate
  # that decision to a function other callers are free to change. Two functions agreeing today is
  # not a reason to make one depend on the other -- so do NOT "simplify" this into rg_is_complete.
  # An unbound legacy marker is a refusal here, not a pass.
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
  #   EXPIRY CONDITION, REWRITTEN 2026-08-21 AS A **PROPERTY** RATHER THAN A **PARTY**.
  #   It used to read "remedy (A) **VERIFIED BY C** -- NOT merely landed", and that wording became
  #   unsatisfiable in a way nobody intended: lane C the SESSION went unreachable (BEN-324), so a
  #   condition naming it could never be met no matter how much verification happened. The ROLE was
  #   re-designated and filled as recently as 2026-08-20, so the intent survives; only the addressing
  #   was broken. It now reads:
  #
  #     THE PAUSE EXPIRES WHEN ALL THREE HOLD:
  #       (a) OI-141 has landed -- the gate's verdict is derived from STRUCTURED data, not by parsing
  #           another module's message prose. Until then a reworded diagnostic can silently turn the
  #           FAIL this pause depends on into an INCOMPLETE, or into a PASS with
  #           --acknowledge-unrecomputable. Measured: that mutation was caught by 0 of ~1992 tests.
  #       (b) The selected OI-140 verification has landed -- the upstream-seed identity is RECOMPUTED
  #           from the member's own scalars against the pinned per-leg baselines, NOT merely declared
  #           unverified. Both were on the table; declaring would have greened the gate while leaving
  #           remedy (A)'s central identity claim unchecked.
  #       (c) A FRESH NON-BUILDER has verified the REAL steps (4)/(5) path on a PRESENT-SEED artifact,
  #           INCLUDING A NEGATIVE CONTROL. "Fresh non-builder" is a property of the verifier, not a
  #           name: whoever it is must not have written the code under review and must not be the
  #           author of the governing ruling. "Present-seed" matters because the identity check has
  #           never once run against a seed that exists -- every available leg records
  #           upstream_estimator_seed_g{1,2}_checked=0, which is ABSENCE, not a pass. "Real path"
  #           excludes invoking the wrapper directly: job 57294218 did that and never ran stage 1.
  #
  #   WHY A PROPERTY AND NOT A PARTY: a condition naming a session expires with the session, and this
  #   one outlived its addressee by days while everyone kept treating it as open. A condition naming
  #   properties can be checked by whoever is here.
  #   NOTHING ABOUT (c) IS SATISFIED BY THIS SCRIPT RUNNING SUCCESSFULLY. Only Joseph lifts the pause.
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
  echo "[fin-bkg]   EXPIRY (a PROPERTY, not a party -- rewritten 2026-08-21): all three of" >&2
  echo "[fin-bkg]     (a) OI-141 landed: the gate verdict is structured, not parsed from prose;" >&2
  echo "[fin-bkg]     (b) the OI-140 verification landed: upstream-seed identity RECOMPUTED from" >&2
  echo "[fin-bkg]         the member's own scalars vs the pinned per-leg baselines, not declared;" >&2
  echo "[fin-bkg]     (c) a FRESH NON-BUILDER verified the REAL steps (4)/(5) path on a" >&2
  echo "[fin-bkg]         PRESENT-SEED artifact, including a negative control." >&2
  echo "[fin-bkg]   The previous wording named lane C, whose session is gone (BEN-324), so it was" >&2
  echo "[fin-bkg]   unsatisfiable by addressing rather than by merit. Until all three hold this" >&2
  echo "[fin-bkg]   member is STAGE 1 NOT ATTEMPTED, not stage 1 pending. Only Joseph lifts it." >&2
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
python3 "$GUARD" --expect-root "$CODE_ROOT" --inventory "$(mnv_inv adopt_stamped_mean)" -- "${CODE_ROOT}/nd-unfolding/mii_adopt_unified_5d_stamped.py" \
  --uthrow "${UTHROW}" \
  --combined "${COMB}" \
  --out "${OUTD}/uq_universe_5d_covariance_combined_bkgaware_uthrow.root" \
  --guard-expect-root "${CODE_ROOT}" --guard-inventory "$(mnv_inv adopt_child_mean)"
echo "[fin-bkg] adopt (CV-centered, F7) $(date -u '+%F %T UTC')"
python3 "$GUARD" --expect-root "$CODE_ROOT" --inventory "$(mnv_inv adopt_stamped_cvcentered)" -- "${CODE_ROOT}/nd-unfolding/mii_adopt_unified_5d_stamped.py" \
  --uthrow "${UTHROW}" \
  --combined "${COMB}" \
  --out "${OUTD}/uq_universe_5d_covariance_combined_bkgaware_uthrow_cvcentered.root" \
  --guard-expect-root "${CODE_ROOT}" --guard-inventory "$(mnv_inv adopt_child_cvcentered)" \
  -- --cv-centered
echo "[fin-bkg] done $(date -u '+%F %T UTC')"
ls -la "${OUTD}"/*.root
