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
# --- PR-J5 / F-2(a), Joseph's ruling of 2026-08-22: VERIFY BEFORE SOURCE, NEVER BIND AFTER USE. ----
# The ruling, verbatim on the point that decides the shape: a file sourced before the parity check
# "can be bound afterward as historical provenance ... but that cannot establish the stronger claim
# needed here: unverified bytes were prevented from executing. The file has already executed and may
# already have changed the environment or exited before the check."
# So these two are verified HERE, before they are sourced, and they are deliberately NOT added to the
# late --pair set further down. Binding them there would record provenance and prove nothing.
#
# WHY PURE GIT AND NOT "$PARITY". MEASURED 2026-08-22 on saul.nersc.gov, not assumed: the pre-conda
# interpreter is /usr/bin/python3 == Python 3.6.15, and verify_executing_copy_is_committed.py opens
# with `from __future__ import annotations`, which is 3.7+ -- it dies with
# "SyntaxError: future feature annotations is not defined" on the frozen tree. And setup_salloc_env.sh
# is ITSELF what activates the conda env that provides a modern python, so no Python checker can
# precede it. git is 2.51.0 pre-conda. The failure mode here was a toolchain dependency, so this
# REMOVES one rather than relocating it.
#
# WHAT THIS DOES NOT COVER -- READ BEFORE RECORDING F-2(a) AS CLOSED. setup_salloc_env.sh itself
# sources ${SCRIPT_DIR}/unbinned_unfolding/build/setup.sh and ${SCRIPT_DIR}/MINERvA101/opt/bin/setup.sh.
# NEITHER IS TRACKED BY GIT (`git ls-files` returns nothing for either), so no git-based check can bind
# them -- and they are what activate conda and set up ROOT/MINERvA101. This gate proves the committed
# bytes of setup_salloc_env.sh and NOT what those bytes pull in: it moves the environment trust
# boundary ONE HOP, it does not close it. lib/resume_guard.sh sources nothing at all (311 lines) and is
# therefore fully bound here. The open half is the TRANSITIVE ENVIRONMENT TRUST BOUNDARY, and Gate 1
# must not be recorded closed on F-2(a) until it is settled and a fresh non-builder passes it.
for _mnv_pre in setup_salloc_env.sh lib/resume_guard.sh; do
  _mnv_head="$(git -C "$CODE_ROOT" rev-parse "HEAD:${_mnv_pre}" 2>/dev/null || true)"
  _mnv_work="$(git -C "$CODE_ROOT" hash-object "${CODE_ROOT}/${_mnv_pre}" 2>/dev/null || true)"
  if [[ -z "$_mnv_head" || -z "$_mnv_work" ]]; then
    echo "[preflight] FAIL: cannot compute git parity for ${_mnv_pre} under ${CODE_ROOT}" >&2
    echo "[preflight]   A check that could not run is not a check that passed." >&2
    exit 3
  fi
  if [[ "$_mnv_head" != "$_mnv_work" ]]; then
    echo "[preflight] FAIL: ${_mnv_pre} differs from HEAD in ${CODE_ROOT}" >&2
    echo "[preflight]   HEAD=${_mnv_head}  working=${_mnv_work}" >&2
    echo "[preflight]   It is SOURCED below. Refusing to execute unverified bytes." >&2
    exit 3
  fi
done
unset _mnv_pre _mnv_head _mnv_work
source "${CODE_ROOT}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${DATA_ROOT}/nd-unfolding"; mkdir -p uq_5d/block_slabs_5d
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
  --pair "${CODE_ROOT}/nd-unfolding/unified_throw_cov_5d.py=nd-unfolding/unified_throw_cov_5d.py" \
  --pair "${CODE_ROOT}/nd-unfolding/sbatch_uthrow_block_5d.sh=nd-unfolding/sbatch_uthrow_block_5d.sh" \
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
  python3 "$GUARD" --expect-root "$CODE_ROOT" --inventory "$(mnv_inv uthrow_block_knobs)" -- "${CODE_ROOT}/nd-unfolding/unified_throw_cov_5d.py" --blockunits --block-knobs all --draw-seed 1000 --estimator-seed ${EST_SEED} \
    --bank bank_uthrow_5d --iters 5 --invalid-ratio neutral \
    --out "${BLOCK_DIR}/block5d_knobs.npz"
else
  LO=$(( (T-1) * 5 )); HI=$(( LO + 4 ))
  python3 "$GUARD" --expect-root "$CODE_ROOT" --inventory "$(mnv_inv uthrow_block_flux)" -- "${CODE_ROOT}/nd-unfolding/unified_throw_cov_5d.py" --blockunits --block-knobs none --block-flux ${LO}-${HI} \
    --draw-seed 1000 --estimator-seed ${EST_SEED} --bank bank_uthrow_5d --iters 5 --invalid-ratio neutral \
    --out "${BLOCK_DIR}/block5d_flux_${T}.npz"
fi
