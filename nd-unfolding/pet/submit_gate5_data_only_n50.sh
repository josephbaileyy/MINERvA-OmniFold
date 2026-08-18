#!/bin/bash
# Submit the C_stat^data N=50 campaign exactly once. Two stages, aftercorr-gated, disjoint root.
#
# WHY A NEW CONTROLLER RATHER THAN A FLAG ON submit_gate5_replica_n50.sh: that controller is not
# pinned, but both ARRAY launchers it submits are, and this one submits the new pair. Adding a name
# satisfies CLAUDE.md's rename/delete prohibition (lane C, BEN-420).
#
# *** THE TWO CONTROLLERS AND THE TWO ARRAY PAIRS MUST NEVER LATER BE UNIFIED. *** `sbatch_*.sh` and
# `submit_*.sh` names are load-bearing provenance in RUN_LOGs, ledgers and receipt JSONs.
#
# WHAT THIS PRODUCT IS, so a reader does not have to reconstruct it: the data stream alone is
# resampled, so the published sigma_stat is not dominated by MC statistics and is comparable to
# MINERvA's own and to T2K/MicroBooNE/NOvA, and profileable as a nuisance term in a global fit. The
# motivation is DEFINITIONAL rather than magnitude-based -- reducible-by-more-MC versus
# reducible-by-more-data is a category distinction at any ratio. THE THREE-STREAM FAMILY IS NOT
# SUPERSEDED, NOT DISCARDED AND NOT RE-VERDICTED (lane C, BEN-404).
set -eo pipefail

# STAGE SELECTION. `both` (default) preserves the original single-invocation behaviour exactly, so no
# existing caller changes meaning. `target` submits ONLY the target array and defers the training one to
# a later invocation against a LATER checkout -- see the deferral note beside the submission below.
#
# DELIBERATELY NOT a `train`-only mode yet: that needs a `--dependency=aftercorr:<job>` operand supplied
# from outside, and an unvalidated job id in a dependency is how a training array silently starts against
# a target family that is still being written. It gets added with its own validation or not at all.
STAGE=${1:-both}
# THE TRAINING ARRAY SPEC, OVERRIDABLE FOR A SINGLE-MEMBER SMOKE AND FOR NOTHING ELSE.
#
# WHY IT EXISTS: the fix for 57194055 works by SUBSTITUTING a module global inside
# `replica_build_data_only` so a new assertion runs in place of the pinned loader's `:742` guard. The
# predicates carry 170 unit controls; THE SUBSTITUTION MECHANISM CARRIES NONE, and 57194055 died inside
# that pinned loader in a real process. No real target-plus-train pair has ever run, and local TF cannot
# run PET, so the composition is testable only on the cluster. One member costs ~3 A100-h against the
# family's ~151 -- 2% to test the only thing left untested.
#
# THE TARGET ARRAY IS DELIBERATELY NOT PARAMETERISED. A partial target family is a trap: the training
# stage's `aftercorr` pairs task N with target task N, so a target array narrower than the training one
# leaves members permanently `DependencyNeverSatisfied` -- which is exactly how the last ten tasks of
# 57194055 ended up unrunnable and unremovable (`BEN-472`). Targets are all-or-nothing here.
TRAIN_ARRAY=${GATE5_TRAIN_ARRAY:-0-49%10}
case "$TRAIN_ARRAY" in
  *[!0-9,%-]*) echo "[gate5-do-submit][FAIL] GATE5_TRAIN_ARRAY '$TRAIN_ARRAY' is not an array spec" >&2
               exit 1 ;;
esac
case "$STAGE" in
  both|target) ;;
  # Plain quoting, not `${STAGE@Q}` -- that is bash 4.4+ and this is read on hosts with bash 3.2, where
  # it is a `bad substitution` that fires INSIDE the error path and replaces the diagnostic with noise.
  *) echo "[gate5-do-submit][FAIL] unknown stage '$STAGE'; expected 'both' or 'target'" >&2; exit 1 ;;
esac

CODE_ROOT=$(git rev-parse --show-toplevel)
# OVERRIDABLE, for generation-two rebuilds into a disjoint tree (lane D's route: keep the family
# DIRECTORY NAME so L2's path-COMPONENT test passes unmodified, and move the PREFIX). This used to be
# a bare assignment while both array scripts read `${GATE5_DATA_ROOT:-...}`, so exporting the variable
# was silently ignored here and the EXPORTS line below overwrote it for every task -- the failure mode being
# generation two landing in generation one's tree via a no-op, which is the one outcome the retention
# condition forbids.
#
# THE ORDER OF THESE TWO EDITS MATTERS AND IS DELIBERATE: L1's disjointness check below was VACUOUS
# (two literals from one prefix) and was made able to fail BEFORE this widening was made. Widening
# what a launcher accepts while its guard cannot fire is how a narrowing gets removed for free.
DATA_ROOT=${GATE5_DATA_ROOT:-/pscratch/sd/j/josephrb/MINERvA-OmniFold}
TARGET_SCRIPT=${CODE_ROOT}/nd-unfolding/pet/sbatch_gate5_data_only_target_array.sh
TRAIN_SCRIPT=${CODE_ROOT}/nd-unfolding/pet/sbatch_gate5_data_only_train_array.sh
TARGET_DRIVER=${CODE_ROOT}/nd-unfolding/pet/build_fullevent_replica_target.py
TRAIN_DRIVER=${CODE_ROOT}/nd-unfolding/pet/train_fullevent_replica.py
NOMINAL_DRIVER=${CODE_ROOT}/nd-unfolding/pet/train_fullevent_nominal.py
LOADER=${CODE_ROOT}/nd-unfolding/pet/fullevent_fps_dataloader.py
PREDICATES=${CODE_ROOT}/nd-unfolding/pet/cstat_data_only.py
INPUT=${DATA_ROOT}/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz
EXPECTED_INPUT_SHA=fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625
OUTPUT_ROOT=${DATA_ROOT}/nd-unfolding/pet/fullevent_cstat_data_only_n50
THREE_STREAM_ROOT=${DATA_ROOT}/nd-unfolding/pet/fullevent_cstat_n50

die() { echo "[gate5-do-submit][FAIL] $*" >&2; exit "${2:-1}"; }
sha_of() { sha256sum "$1" | awk '{print $1}'; }
[[ -z "$(git -C "$CODE_ROOT" status --porcelain)" ]] || die "code worktree is dirty"
HEAD=$(git -C "$CODE_ROOT" rev-parse HEAD)
for f in "$TARGET_SCRIPT" "$TRAIN_SCRIPT" "$TARGET_DRIVER" "$TRAIN_DRIVER" \
         "$NOMINAL_DRIVER" "$LOADER" "$PREDICATES" "$INPUT"; do
  [[ -s "$f" && ! -L "$f" ]] || die "missing/empty/symlink prerequisite $f"
done
[[ "$(sha_of "$INPUT")" == "$EXPECTED_INPUT_SHA" ]] || die "frozen G2 source hash mismatch"

# L1 -- THE ROOTS MUST BE DISJOINT, ASSERTED. If this ever resolved into the three-stream family the
# submission would overwrite or collide with the archived 50, which is the one outcome no guard
# downstream can undo.
#
# THE LINE THAT USED TO BE HERE WAS VACUOUS AND IS REPLACED:
#     [[ "$OUTPUT_ROOT" != "$THREE_STREAM_ROOT" ]] || die "L1 output root is the three-stream root"
# Both operands are assigned above from the same `${DATA_ROOT}` prefix and differ in a fixed literal
# substring, so the comparison could not fail for ANY value of DATA_ROOT, including a hostile one. It
# was a green check that proved nothing -- the same shape as the F2 tautology (two operands from one
# source), written into an L1 guard by the same hand, on the same day, as the finding about it. Found
# only because lane D's `GATE5_DATA_ROOT` override proposal forced these lines to be read.
#
# AND SO IS THE SUFFIX `case` THAT USED TO FOLLOW IT (lane D, extending the finding one line further
# than I took it):
#     case "$OUTPUT_ROOT" in *fullevent_cstat_data_only_n50) ;; *) die "L1 unexpected output root" ;;
# OUTPUT_ROOT is built by appending that exact literal, so it ends in it for EVERY value of DATA_ROOT.
# That line is a change-detector on the assignment above, which is real but is not what its `die`
# message claims -- so the L1 shell block was TWO vacuous guards, not one, and keeping "the suffix
# check is the whole of L1" would have left a second green check proving nothing.
#
# WHAT REPLACES BOTH IS GUARDED ON THE CALLER-SUPPLIED VALUE, and it is non-vacuous ONLY BECAUSE OF
# THE OVERRIDE ABOVE -- D's proposal is what gives this guard something to check. Until DATA_ROOT
# became caller-supplied, nothing about it could be wrong and no shell test on it could fail. The
# failure mode it now closes: `GATE5_DATA_ROOT` set to a path that itself contains a family-root
# component, e.g. one ending in `fullevent_cstat_n50`, which makes OUTPUT_ROOT
# `.../fullevent_cstat_n50/nd-unfolding/pet/fullevent_cstat_data_only_n50` -- caught today only by
# L2's `clash = parts & others` in Python at the builder's first call, which is later and quieter.
case "$DATA_ROOT" in
  *fullevent_cstat_data_only_n50*|*fullevent_cstat_n50*)
    die "L1 GATE5_DATA_ROOT contains a family-root component, so the output path would carry a "\
"foreign family root: $DATA_ROOT" ;;
esac
# The suffix invariant is KEPT, with a message that says what it actually tests.
case "$OUTPUT_ROOT" in
  *fullevent_cstat_data_only_n50) ;;
  *) die "L1 construction invariant broken: OUTPUT_ROOT no longer ends in the data-only family "\
"component, so the assignment above was edited: $OUTPUT_ROOT" ;;
esac
# SYMLINK-AWARE, because the two `case` tests above read the STRING and a symlinked prefix can carry a
# clean-looking path into the three-stream tree. Only checked if the parent already exists; a
# not-yet-created root has no resolution to test and the string tests are then the whole of L1.
PARENT_REAL=""
if [[ -d "$(dirname "$OUTPUT_ROOT")" ]]; then
  PARENT_REAL=$(cd "$(dirname "$OUTPUT_ROOT")" && pwd -P)
fi
case "$PARENT_REAL" in
  *fullevent_cstat_n50*) die "L1 output root's parent RESOLVES into the three-stream family: $PARENT_REAL" ;;
esac

# === CAN THE JOB BECOME ITS ENVIRONMENT? ADDED BECAUSE EVERY GUARD ABOVE ASKED A DIFFERENT QUESTION. ===
#
# 57232522 died 50/50 in 7-11 seconds with an EMPTY `.out`, on the first line of the environment activation,
# after a pre-submit dry run that went green through every check above INCLUDING the full 9.9 GB input
# sha256. All of those inspect the DATA ROOT'S CONTENTS; none resolves what the activator sources. The
# guards answered "are the inputs right?" and the job died on "can I become the environment that reads
# them?"
#
# The activator computes SCRIPT_DIR from its OWN location, so symlinking it into a bare data root makes it
# look for software trees that root does not contain -- and the reference list is THREE long, so fixing the
# one path that appeared in the .err would have failed again at the next.
"${CODE_ROOT}/nd-unfolding/pet/check_activator_paths.sh" "$DATA_ROOT" \
  || die "the activator resolves a path that does not exist from $DATA_ROOT -- see above" 4

# Both name sets are checked, because a live three-stream array shares the cluster and the input.
if squeue -h -u "$USER" -n g5dotarg,g5dotrain | grep -q .; then
  squeue -h -u "$USER" -n g5dotarg,g5dotrain -o '%i|%j|%T|%R' >&2
  die "an existing C_stat^data array is already active"
fi
if squeue -h -u "$USER" -n g5targ,g5train | grep -q .; then
  squeue -h -u "$USER" -n g5targ,g5train -o '%i|%j|%T|%R' >&2
  die "a three-stream Gate-5 array is active; refusing to interleave two families on one input"
fi
for index in $(seq 0 49); do
  replica=$(printf 'replica_%02d' "$index")
  base=${OUTPUT_ROOT}/replicas/${replica}
  for f in \
    "$base/target/GATE5_REPLICA_TARGET.npy" \
    "$base/target/GATE5_REPLICA_TARGET.npy.done" \
    "$base/target/GATE5_REPLICA_TARGET_RECEIPT.json" \
    "$base/target/GATE5_REPLICA_TARGET_RECEIPT.json.done" \
    "$base/training/GATE5_REPLICA_WEIGHTS.npz" \
    "$base/training/GATE5_REPLICA_WEIGHTS.npz.done" \
    "$base/training/GATE5_REPLICA_TRAINING_RECEIPT.json" \
    "$base/training/GATE5_REPLICA_TRAINING_RECEIPT.json.done"; do
    [[ ! -e "$f" && ! -L "$f" ]] || die "collision/no-clobber guard: $f"
  done
done
mkdir -p "$OUTPUT_ROOT/logs"

EXPORTS="ALL,HOME=/global/homes/j/josephrb,GATE5_CODE_ROOT=$CODE_ROOT,GATE5_DATA_ROOT=$DATA_ROOT"
EXPORTS+=",GATE5_EXPECTED_HEAD=$HEAD,GATE5_EXPECTED_INPUT_SHA=$EXPECTED_INPUT_SHA"
EXPORTS+=",GATE5_EXPECTED_TARGET_DRIVER_SHA=$(sha_of "$TARGET_DRIVER")"
EXPORTS+=",GATE5_EXPECTED_TRAIN_DRIVER_SHA=$(sha_of "$TRAIN_DRIVER")"
EXPORTS+=",GATE5_EXPECTED_NOMINAL_DRIVER_SHA=$(sha_of "$NOMINAL_DRIVER")"
EXPORTS+=",GATE5_EXPECTED_LOADER_SHA=$(sha_of "$LOADER")"
# The predicate module is pinned at submit like the drivers: T1-T5 and L2 live in it, so a change
# there changes what "data-only" MEANS, and a family built against a different set is a different
# product wearing the same name.
EXPORTS+=",GATE5_EXPECTED_PREDICATES_SHA=$(sha_of "$PREDICATES")"

# LOG PATHS OVERRIDDEN ON THE COMMAND LINE, because `#SBATCH --output=` in the launcher is an ABSOLUTE path
# into the generation-one tree and sbatch parses those directives BEFORE the script runs -- so they cannot
# see `$DATA_ROOT` and a g2 run's logs land in g1's log directory, interleaved and distinguishable only by
# job id. Found by looking for 57235710's logs in the g2 tree and finding none. A command-line `--output`
# wins over the directive, so the launcher's default is left intact for the generation-one reproduction.
mkdir -p "$OUTPUT_ROOT/logs"
TARGET_JOB=$(sbatch --parsable --array=0-49%10 --export="$EXPORTS" \
  --output="$OUTPUT_ROOT/logs/target_%A_%a.out" --error="$OUTPUT_ROOT/logs/target_%A_%a.err" \
  "$TARGET_SCRIPT") \
  || die "target-array submission failed"
[[ "$TARGET_JOB" =~ ^[0-9]+$ ]] || die "unexpected target job id $TARGET_JOB"
if [[ "$STAGE" == "target" ]]; then
  # TWO DEPLOYMENTS, CUT AT DIFFERENT TIMES, WHICH IS THE SHAPE THE FAMILY CHECKS ALREADY ASSUME.
  # `reconcile_gate5_family.py` grades the target-side invariants over the TARGET RECEIPTS (:852-870)
  # and the training-side ones over the TRAINING ARTIFACTS (:872-892), and neither block compares one
  # stage's digests against the other's -- so one deployment per stage gives one group in each block.
  # Cutting a single checkout for both is what COUPLES them: a later training-writer change would then
  # force a second checkout anyway, or waste the target rebuild.
  #
  # THE DEPENDENCY IS NOT LOST, IT IS DEFERRED: the training stage is submitted by a later
  # `--stage train --after <this job id>` invocation, which re-derives its own pins from ITS checkout.
  TRAIN_JOB="DEFERRED"
else
  if ! TRAIN_JOB=$(sbatch --parsable --array="$TRAIN_ARRAY" --dependency="aftercorr:${TARGET_JOB}" \
        --export="$EXPORTS" \
        --output="$OUTPUT_ROOT/logs/train_%A_%a.out" --error="$OUTPUT_ROOT/logs/train_%A_%a.err" \
        "$TRAIN_SCRIPT"); then
    scancel "$TARGET_JOB" || true
    die "training-array submission failed; exact target array $TARGET_JOB cancelled"
  fi
  [[ "$TRAIN_JOB" =~ ^[0-9]+$ ]] || die "unexpected training job id $TRAIN_JOB"
fi
echo "GATE5_DATAONLY_TARGET_JOB=$TARGET_JOB"
echo "GATE5_DATAONLY_TRAIN_JOB=$TRAIN_JOB"
echo "GATE5_DATAONLY_DEPENDENCY=aftercorr:$TARGET_JOB"
echo "GATE5_DATAONLY_CODE_HEAD=$HEAD"
echo "GATE5_DATAONLY_OUTPUT_ROOT=$OUTPUT_ROOT"
echo "GATE5_DATAONLY_PRODUCT=data-only-v1"
echo "GATE5_DATAONLY_STAGE=$STAGE"
# Echoed because a family built from a NARROWED training array is not the 50-member family,
# and the only durable record of which members were trained is this line plus sacct.
echo "GATE5_DATAONLY_TRAIN_ARRAY=$TRAIN_ARRAY"
# THE DATA ROOT IS PROVENANCE NOW THAT IT IS OVERRIDABLE. The training stage must run under the SAME
# value or F2's family-position operand disagrees on every member -- safe and loud, but it would read
# as a mysterious family-wide failure rather than a launcher-env mismatch (lane D).
echo "GATE5_DATAONLY_DATA_ROOT=$DATA_ROOT"
# THE LOADER DIGEST, RECORDED BECAUSE NO CHECK COMPARES THE TWO DEPLOYMENTS' LOADERS.
# reconcile_gate5_family.py grades `loader` in BOTH invariant blocks -- target-side over the target
# receipts (:852-870) and training-side over the training artifacts (:872-892) -- and NOTHING compares
# one block's digest against the other's. So two deployments cut at different times could carry
# DIFFERENT loaders with each block internally uniform and the discrepancy invisible. Nobody is
# proposing a loader change and the file is pinned at 25 digest sites, so this is cheap to guarantee;
# it is recorded because it must be STATED rather than assumed, there being no check that would say so.
echo "GATE5_DATAONLY_LOADER_SHA256=$(sha_of "$LOADER")"
