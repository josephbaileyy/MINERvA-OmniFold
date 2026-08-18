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

echo "[gate5-do-target] index=$INDEX seed=$SEED job=${SLURM_ARRAY_JOB_ID}_${INDEX} head=$EXPECTED_HEAD product=data-only-v1"
"$PYTHON_BIN" "$DRIVER" \
  --inputs "$INPUT" \
  --output "$TARGET" \
  --receipt "$RECEIPT" \
  --bootstrap-seed "$SEED" \
  --replica-index "$INDEX" \
  --expected-input-sha256 "$EXPECTED_INPUT_SHA" \
  --gate3-manifest "$GATE3" \
  --cstat-product data-only-v1
echo "[gate5-do-target] DONE index=$INDEX seed=$SEED $(date -u +%Y-%m-%dT%H:%M:%SZ)"
