#!/bin/bash
#SBATCH --job-name=g5dotarg
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=03:00:00
#SBATCH --array=0-49%10
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_cstat_data_only_n50/logs/target_%A_%a.out
#SBATCH --error=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_cstat_data_only_n50/logs/target_%A_%a.err
set -eo pipefail

# C_stat^data STAGE 1 -- the data-only target family. Stage 2 is
# sbatch_gate5_data_only_train_array.sh, gated by Slurm aftercorr exactly as the three-stream pair is.
#
# WHY THIS IS A NEW FILE RATHER THAN A FLAG ON sbatch_gate5_replica_target_array.sh. That launcher is
# HASH-PINNED (measured: perturbing it takes verify_hash_bindings.py red), so threading a product
# flag through it purchases a pinned-file edit just to keep passing `three-stream-v1` -- the exact
# trade the whole data-only route exists to avoid. Adding a name satisfies CLAUDE.md's rename/delete
# prohibition; editing the pinned one would not (lane C, BEN-420).
#
# *** THIS PAIR MUST NEVER LATER BE UNIFIED INTO ONE PARAMETRISED LAUNCHER. *** The tidy-up arrives
# as a refactor and looks like a simplification. 115 `sbatch_*.sh` names are load-bearing provenance
# in RUN_LOGs, ledgers and receipt JSONs; this makes 117. Unifying them would rename two cited names
# out of existence and re-point every receipt that names either.
#
# L1 -- THE DISJOINT FAMILY ROOT IS THE MECHANISM, NOT A CONVENTION. `--cstat-product` defaults to
# three-stream, which is safe in isolation and became a silent failure the moment a run was
# authorized: no launcher passed the flag, so an sbatch would have spent 151 A100-hours rebuilding
# the product that already exists. A DEFAULT'S SAFETY IS A PROPERTY OF THE CALL GRAPH, NOT OF THE
# VALUE. This launcher writes to `fullevent_cstat_data_only_n50` and the driver ASSERTS TAG <=> ROOT
# (L2), so the tag cannot be wrong without the path being wrong, and the existing 50 artifacts
# occupy their own root under a no-clobber guard -- a wrong-launcher submission COLLIDES LOUDLY.
CODE_ROOT=${GATE5_CODE_ROOT:?submit controller must export GATE5_CODE_ROOT}
DATA_ROOT=${GATE5_DATA_ROOT:-/pscratch/sd/j/josephrb/MINERvA-OmniFold}
EXPECTED_HEAD=${GATE5_EXPECTED_HEAD:?submit controller must export GATE5_EXPECTED_HEAD}
EXPECTED_DRIVER_SHA=${GATE5_EXPECTED_TARGET_DRIVER_SHA:?missing target-driver pin}
EXPECTED_LOADER_SHA=${GATE5_EXPECTED_LOADER_SHA:?missing loader pin}
EXPECTED_PREDICATES_SHA=${GATE5_EXPECTED_PREDICATES_SHA:?missing cstat_data_only pin}
EXPECTED_INPUT_SHA=${GATE5_EXPECTED_INPUT_SHA:?missing input pin}

DRIVER=${CODE_ROOT}/nd-unfolding/pet/build_fullevent_replica_target.py
LOADER=${CODE_ROOT}/nd-unfolding/pet/fullevent_fps_dataloader.py
PREDICATES=${CODE_ROOT}/nd-unfolding/pet/cstat_data_only.py
INPUT=${DATA_ROOT}/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz
GATE3=${CODE_ROOT}/docs/orchestration/state/p3f-pet-gate3-source-manifest-56169838.json
INDEX=${SLURM_ARRAY_TASK_ID:?array task ID missing}
SEED=$((50000 + INDEX))
REPLICA=$(printf 'replica_%02d' "$INDEX")
OUTDIR=${DATA_ROOT}/nd-unfolding/pet/fullevent_cstat_data_only_n50/replicas/${REPLICA}/target
TARGET=${OUTDIR}/GATE5_REPLICA_TARGET.npy
RECEIPT=${OUTDIR}/GATE5_REPLICA_TARGET_RECEIPT.json

die() { echo "[gate5-do-target][FAIL] $*" >&2; exit "${2:-1}"; }
sha_of() { sha256sum "$1" | awk '{print $1}'; }
[[ -d "$CODE_ROOT/.git" || -f "$CODE_ROOT/.git" ]] || die "invalid code worktree $CODE_ROOT"
[[ "$(git -C "$CODE_ROOT" rev-parse HEAD)" == "$EXPECTED_HEAD" ]] || die "code HEAD drift"
[[ "$(sha_of "$DRIVER")" == "$EXPECTED_DRIVER_SHA" ]] || die "target driver hash drift"
[[ "$(sha_of "$LOADER")" == "$EXPECTED_LOADER_SHA" ]] || die "loader hash drift"
# The predicates are pinned too: T1-T5 and L2 live in one module, so a change there changes what
# "data-only" MEANS. A family built against a different predicate set is a different product.
[[ "$(sha_of "$PREDICATES")" == "$EXPECTED_PREDICATES_SHA" ]] || die "predicate module hash drift"
for f in "$INPUT" "$GATE3"; do [[ -s "$f" && ! -L "$f" ]] || die "missing/symlink $f"; done
for f in "$TARGET" "$TARGET.done" "$RECEIPT" "$RECEIPT.done"; do
  [[ ! -e "$f" && ! -L "$f" ]] || die "collision/no-clobber guard: $f"
done
mkdir -p "$OUTDIR"

source "${DATA_ROOT}/setup_salloc_env.sh"
export PYTHONPATH="${CODE_ROOT}/omnifold_nn:${CODE_ROOT}/2d-unfolding:${CODE_ROOT}/nd-unfolding:${CODE_ROOT}/nd-unfolding/pet:${PYTHONPATH:-}"
export PYTHONUNBUFFERED=1
PYTHON_BIN=$(command -v python3 || true)
[[ -n "$PYTHON_BIN" && -x "$PYTHON_BIN" ]] || die "ROOT environment python3 missing"
"$PYTHON_BIN" -c 'import numpy, sklearn' || die "ROOT target environment missing NumPy/sklearn"

# ---------------------------------------------------------------------------------------------
# DEPLOYMENT PARITY -- the first production caller this checker has ever had on an UNPINNED path.
#
# `verify_executing_copy_is_committed.py` has existed and worked since 2026-08-13 and its only
# production call site is `reconcile_gate5_family.py`, which is hash-pinned -- so `BEN-385` records
# it as effectively unwired: the one check that answers "is the file about to execute the committed
# one" was on no path anything took. These launchers are NEW and unpinned, and they are about to be
# the only consumer of a frozen deployment checkout, so this is the first opportunity to give it a
# caller without editing a pinned file.
#
# WHY IT IS NOT REDUNDANT WITH THE sha_of PINS ABOVE. Those compare each file against a constant the
# submit controller computed AT SUBMIT. This compares each file against the COMMITTED BLOB in the
# tree it sits in. The two fail on different things: a pin catches a change between submit and
# dispatch, and this catches a deployment that was edited after it was created -- or was never a
# faithful checkout in the first place. A deployment step that does not verify its own premise is
# exactly the defect this checker was written for, committed by the work that fixes it.
#
# EXIT SEMANTICS ARE THE TOOL'S, NOT REINTERPRETED HERE: 0 only if every pair is CURRENT, 3 if any
# pair is stale/uncommitted/missing, and 2 for "could not look" -- deliberately NOT 3, so an
# unreadable tree can never be misread as measured drift. Both non-zero cases die.
# ---------------------------------------------------------------------------------------------
# OI-136 IMPORT-TREE GUARD -- the fail-CLOSED half, and it is NOT redundant with the parity
# check above. That check answers "are the FILES AT THESE PATHS the committed ones" and on
# 57266000_0 it answered YES, five for five, honestly. This one answers "are the MODULES THE
# INTERPRETER LOADED from $CODE_ROOT", and on that same run the answer was NO: the drivers
# hardcode /pscratch/sd/j/josephrb/MINERvA-OmniFold and insert it at sys.path[0], which beats
# the PYTHONPATH set above -- position 0 cannot be outranked by an env var -- so 3 h 08 m of
# A100 ran 211-commit-behind predicates and failed on a contract already repaired here.
#
# THE GUARD MUST COME FROM $CODE_ROOT AND IS PARITY-CHECKED WITH EVERYTHING ELSE. A guard
# imported from the tree it is supposed to be policing is theatre. Frozen deployments cut
# before 2026-08-20 do not contain it, and that is the correct failure: re-deploy, because a
# re-deploy is required to get the fix anyway.
GUARD=${CODE_ROOT}/nd-unfolding/mnv_guarded_run.py
[[ -s "$GUARD" && ! -L "$GUARD" ]] || die "OI-136 import-tree guard missing at $GUARD -- this deployment predates it; re-deploy $CODE_ROOT" 2
PARITY=${CODE_ROOT}/nd-unfolding/pet/verify_executing_copy_is_committed.py
[[ -s "$PARITY" && ! -L "$PARITY" ]] || die "deployment parity checker missing at $PARITY"
"$PYTHON_BIN" "$PARITY" --repo "$CODE_ROOT" \
  --pair "${DRIVER}=nd-unfolding/pet/build_fullevent_replica_target.py" \
  --pair "${LOADER}=nd-unfolding/pet/fullevent_fps_dataloader.py" \
  --pair "${PREDICATES}=nd-unfolding/pet/cstat_data_only.py" \
  --pair "${PARITY}=nd-unfolding/pet/verify_executing_copy_is_committed.py" \
  --pair "${GUARD}=nd-unfolding/mnv_guarded_run.py" \
  || die "deployment parity: the executing copies are not the committed ones in $CODE_ROOT" $?
echo "[gate5-do-target] deployment parity CURRENT for all pinned executing copies in $CODE_ROOT"

echo "[gate5-do-target] index=$INDEX seed=$SEED job=${SLURM_ARRAY_JOB_ID}_${INDEX} head=$EXPECTED_HEAD product=data-only-v1"
# ROUTED THROUGH THE OI-136 GUARD. The `--` is MANDATORY: the wrapper splits on it and refuses
# bare positionals, so no child flag below can be silently eaten (remedy (A)'s wrapper learned
# this the expensive way). Child argv after `--` is forwarded verbatim; exit 3 means an import
# escaped $CODE_ROOT and NOTHING RAN.
"$PYTHON_BIN" "$GUARD" --expect-root "$CODE_ROOT" -- "$DRIVER" \
  --inputs "$INPUT" \
  --output "$TARGET" \
  --receipt "$RECEIPT" \
  --bootstrap-seed "$SEED" \
  --replica-index "$INDEX" \
  --expected-input-sha256 "$EXPECTED_INPUT_SHA" \
  --gate3-manifest "$GATE3" \
  --cstat-product data-only-v1
echo "[gate5-do-target] DONE index=$INDEX seed=$SEED $(date -u +%Y-%m-%dT%H:%M:%SZ)"
