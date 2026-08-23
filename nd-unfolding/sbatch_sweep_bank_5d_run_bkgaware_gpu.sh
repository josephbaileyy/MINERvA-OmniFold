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
# --- F-2(a) ROUND-5 REPAIR: THREE ROOTS, AND THE ENVIRONMENT CLOSURE IS DIGEST-BOUND BEFORE USE ---
# Authorized by Joseph 2026-08-23 after the round-4 verdict (16 PASS / 2 FAIL). What round 4 found,
# and it was not a filing gap: `setup_salloc_env.sh` sources files that are ABSENT from any tree
# satisfying A-2 -- `.gitignore` excludes `unbinned_unfolding/**` and `MINERvA101/**`, so a clone or
# worktree at a named sha NECESSARILY lacks them. Measured on saul (bash 4.4.23): every launcher
# died at `line 18: ... No such file or directory`, exit 1, before any preflight tool, guard or
# science invocation. The round-4 gate passed and was the last thing that happened.
#
# THE ENVIRONMENT IS NOW ITS OWN ROOT, because git structurally cannot bind those bytes -- so the
# MECHANISM is substituted rather than the check relocated, the same move PR-02 made for the
# interpreter. `MNV_ENV_ROOT` is mandatory with NO default: a default is the hardcode wearing a flag.
# Its resolved target must sit outside every checkout, which `lib_mnv_env_preflight.sh` verifies on the
# CANONICAL path -- a directory symlink is permitted, a view onto the canonical checkout is not.
#
# WHAT IS BOUND: the COMPLETE transitive closure, 14 members -- the activator, the two scripts it
# sources, the three MAT scripts below them, and the eight conda `activate.d/*.sh` that activation
# GLOBS and executes. Hop 3 is empty, measured. `lib/resume_guard.sh` stays on the git check below
# because it IS tracked and git CAN bind it; only what git cannot reach moved to the manifest.
#
# NO `set -u`. The closure reaches conda's activate-binutils_linux-64.sh, which references ADDR2LINE
# unbound; under `set -u` that is fatal to this shell and it killed job 57235710 in ten seconds.
ENV_ROOT="${MNV_ENV_ROOT:?set MNV_ENV_ROOT to the verified environment tree -- a real directory OUTSIDE every repository checkout, holding the activation closure named by nd-unfolding/mnv_env_manifest.tsv. It has NO default: the round-4 failure was an environment resolved relative to the code root.}"
ENV_MANIFEST="${MNV_ENV_MANIFEST:-${CODE_ROOT}/nd-unfolding/mnv_env_manifest.tsv}"
: "${MNV_CONDA_PREFIX:?set MNV_CONDA_PREFIX to the conda env whose activate.d scripts the manifest binds. It has no default: ROOT628_PREFIX used to be env-overridable, so verifying the activator bytes did not determine which conda executed.}"

# (1) EVERY TRACKED FILE THIS PREAMBLE SOURCES IS GIT-BOUND BEFORE ANY OF THEM IS SOURCED.
#     Round-6 F-2(a) and Joseph's ruling 2026-08-23 (DECISION-20260823-joseph-a2f-does-not-substitute
#     -for-a3.md): A-2(f) DOES NOT SUBSTITUTE FOR A-3 executing-file parity. A tracked file that
#     EXECUTES before the later source-manifest comparison requires PRE-USE parity -- and that
#     comparison runs far below, which is too late for bytes that have already run. Round 6 shipped
#     the two environment libraries sourced from the code root with no gate of their own while this
#     very block sat 17 lines above them, naming only lib/resume_guard.sh. All three are TRACKED, so
#     git binds them; the closure files under ENV_ROOT are NOT tracked, which is why they get the
#     digest manifest in (2) instead and cannot use this route.
#     NO SOURCED HELPER, DELIBERATELY. A helper performing this check would itself execute before
#     anything bound ITS bytes -- F-2(a) reproduced exactly, one level down. The loop is inline in
#     all eight launchers for that reason; the duplication is the point, and a test asserts the eight
#     copies are identical.
#     THE LOOP VERIFIES ALL THREE BEFORE IT SOURCES ANY. Verifying each immediately before its own
#     source would still leave file 2 unverified while file 1 executes.
for _mnv_rel in lib/resume_guard.sh \
                nd-unfolding/lib_mnv_env_preflight.sh \
                nd-unfolding/lib_mnv_env_pathcheck.sh; do
  _mnv_head="$(git -C "$CODE_ROOT" rev-parse "HEAD:${_mnv_rel}" 2>/dev/null || true)"
  _mnv_work="$(git -C "$CODE_ROOT" hash-object "${CODE_ROOT}/${_mnv_rel}" 2>/dev/null || true)"
  if [[ -z "$_mnv_head" || -z "$_mnv_work" ]]; then
    echo "[preflight] FAIL: cannot compute git parity for ${_mnv_rel} under ${CODE_ROOT}" >&2
    echo "[preflight]   A check that could not run is not a check that passed." >&2
    exit 3
  fi
  if [[ "$_mnv_head" != "$_mnv_work" ]]; then
    echo "[preflight] FAIL: ${_mnv_rel} differs from HEAD in ${CODE_ROOT}" >&2
    echo "[preflight]   HEAD=${_mnv_head}  working=${_mnv_work}" >&2
    echo "[preflight]   It is SOURCED below. Refusing to execute unverified bytes." >&2
    exit 3
  fi
done
unset _mnv_rel _mnv_head _mnv_work

# (2) The environment closure is digest-verified BEFORE the activator is sourced. Pure bash: this
#     runs before conda exists, and the pre-conda /usr/bin/python3 on saul is 3.6.15.
source "${CODE_ROOT}/nd-unfolding/lib_mnv_env_preflight.sh"
mnv_env_preflight "$ENV_MANIFEST" "$ENV_ROOT" "$CODE_ROOT" "$DATA_ROOT" || exit $?
source "${CODE_ROOT}/nd-unfolding/lib_mnv_env_pathcheck.sh"
source "${ENV_ROOT}/setup_salloc_env.sh"

# (3) AFTER activation: refuse any PATH/PYTHONPATH/LD_LIBRARY_PATH entry that resolves inside a
#     repository checkout, or outside the declared environment except for predeclared system
#     prefixes. Binding the BYTES is not enough -- the round-4 verdict found the hop-1 activator
#     injecting the canonical checkout into all three channels BY CONTENT, and the OI-136 Python
#     import guard sees only the sys.path consequence, never PATH and never LD_LIBRARY_PATH.
mnv_env_pathcheck "$ENV_ROOT" "$CODE_ROOT" "$DATA_ROOT" || exit $?

# (4) THE INTERPRETER MUST BE ABLE TO RUN THE PREFLIGHT TOOLS, checked HERE so a failure is reported
#     as ITSELF. Round 5 shipped one launcher whose Python tools ran BEFORE the activator; on the
#     un-activated 3.6.15 interpreter they die with a SyntaxError and the launcher reported
#     "[oi136] FAIL: the execution tree is not the tree that was approved" -- a WRONG DIAGNOSIS of a
#     right refusal, which is worse than the refusal. Both tools open with
#     `from __future__ import annotations` (3.7+), so that is the floor asserted.
if ! python3 -c 'import sys; sys.exit(0 if sys.version_info[:2] >= (3, 7) else 9)' 2>/dev/null; then
  echo "[preflight] FAIL: the active interpreter cannot run the preflight tools." >&2
  echo "[preflight]   $(command -v python3 || echo '<none on PATH>'): $(python3 -V 2>&1 || true)" >&2
  echo "[preflight]   mnv_source_manifest.py and verify_executing_copy_is_committed.py both open" >&2
  echo "[preflight]   with 'from __future__ import annotations', which requires 3.7+." >&2
  echo "[preflight]   This is an ENVIRONMENT fault, not a wrong-tree fault. Do not read it as one." >&2
  exit 3
fi
export PYTHONUNBUFFERED=1; cd "${DATA_ROOT}/nd-unfolding"
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
  --pair "${CODE_ROOT}/nd-unfolding/sweep_bank_5d.py=nd-unfolding/sweep_bank_5d.py" \
  --pair "${CODE_ROOT}/nd-unfolding/sbatch_sweep_bank_5d_run_bkgaware_gpu.sh=nd-unfolding/sbatch_sweep_bank_5d_run_bkgaware_gpu.sh" \
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
# --- M(ii) member axis: END RESOLVER ----------------------------------------------------------
# The byte-identity extraction window for `LibraryResolverSurvivesSbatch` ends HERE, at the end of
# the RESOLVER, not at the `source` below. It was moved 2026-08-23 so that the containment check can
# precede the source; the test was updated rather than the check left after use, on Joseph's
# instruction ("update affected extraction/identity tests rather than retaining bind-after-use to
# keep an old fixture green").
#
# RULING 17, THE SHELL HALF, NOW BIND-BEFORE-USE. `lib_member_resume.sh` is an EXECUTED repository
# file, so it must come from the code root. The resolver above may legitimately pick
# MNV_LAUNCHER_DIR, `dirname $BASH_SOURCE` or `scontrol Command`; this asserts that whichever it
# picked resolves to ${MNV_CODE_ROOT}/nd-unfolding and FAILS CLOSED if it is not -- BEFORE the file
# executes. Round 4 found this check running AFTER the source in all eight launchers, the same shape
# PR-02 had already fixed for `_mr_rg` in the finalize launcher and left standing here.
if [[ "$(cd "$_mr_lib" 2>/dev/null && pwd -P)" != "$(cd "${CODE_ROOT}/nd-unfolding" 2>/dev/null && pwd -P)" ]]; then
  echo "[member] FAIL: lib_member_resume.sh resolved to '${_mr_lib}', which is not" >&2
  echo "[member]   \${MNV_CODE_ROOT}/nd-unfolding = '${CODE_ROOT}/nd-unfolding'." >&2
  echo "[member]   Refusing: the member axis would run from a tree this job did not approve." >&2
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
SWEEP_OUTDIR="$(mr_dir_prefix "${DATA_ROOT}/nd-unfolding/uq_5d/universe_sweep_bkgaware")"
python3 "$GUARD" --expect-root "$CODE_ROOT" --inventory "$(mnv_inv sweep_bank_5d)" -- "${CODE_ROOT}/nd-unfolding/sweep_bank_5d.py" --run --estimator-seed ${EST_SEED} --universe "$U" \
  --bankdir "${DATA_ROOT}/nd-unfolding/bank_sweep_5d_bkgaware" \
  --outdir "${SWEEP_OUTDIR}" --iters 5
echo "[sweep-run-bkg] task=${SLURM_ARRAY_TASK_ID} done $(date -u '+%F %T UTC')"
