#!/bin/bash
# Join his built inputs to the inventory, then submit the campaign.
#
# Submitted with a dependency on the input-build array, so the whole chain runs
# unattended: build -> join -> tuning -> pilot -> final. Each stage depends on
# the previous one completing successfully, because tuning selects on the tuning
# split and the pilot sizes the final; concurrency there would leak.
#SBATCH --account=m3246
#SBATCH --constraint=cpu
#SBATCH --qos=shared
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=96G
#SBATCH --time=02:00:00
#SBATCH --job-name=pet-join-launch
set -eo pipefail

CHECKOUT=${CHECKOUT:?}
OUTPUT=${OUTPUT:?}
COMMIT=${COMMIT:?}
SIDECAR=/pscratch/sd/j/josephrb/event-identity-audit/G2_FPS_MEFHC_P12.identity.npz
INPUTS=/pscratch/sd/j/josephrb/theirs_inputs
INVENTORY=/global/cfs/cdirs/m3246/josephrb/minerva-shutdown-stage/g2_input/G2_FPS_MEFHC_P12.npz
JOINDIR="${OUTPUT}/join"

cd "$CHECKOUT"
[[ "$(git rev-parse HEAD)" == "$COMMIT" ]]
mkdir -p "$JOINDIR"
module load python

# Data joins on ev_*, signal on mc_* -- each stream's own fields, never crossed.
# `bkg` too: the measured leg is the SIGNED inventory, data rows followed by
# the aligned negative background rows, and his arm needs tokens for both. It
# is MC, so it joins on the mc_* fields from the MC directories.
for STREAM in data bkg sig; do
  if [[ "$STREAM" == "data" ]]; then DIRS=("$INPUTS"/*_Data); else DIRS=("$INPUTS"/*_MC); fi
  python3 nd-unfolding/pet/configuration_comparison/join_theirs_to_inventory.py \
    --sidecar "$SIDECAR" --stream "$STREAM" --input-dirs "${DIRS[@]}" \
    --target-npz "$INVENTORY" \
    --output "$JOINDIR/join_${STREAM}.npz" \
    --report "$JOINDIR/join_${STREAM}.json"
done

# Refuse to launch on an incomplete join: a pass_reco row his arm cannot see is
# an event ours can, and that asymmetry would read as a method effect.
#
# The gate is on PASS_RECO rows, not on all inventory rows. An event that failed
# reconstruction has no reconstructed object, so no token can be built from it;
# it lives only in the AnaTuple's Truth tree and enters through the truth leg.
# The first version demanded reco inputs for those events too and reported
# 59.5% for a join that in fact covered 100.0000% of what it can cover.
python3 - "$JOINDIR" <<'PY'
import json, sys
from pathlib import Path
bad = []
for stream in ("data", "bkg", "sig"):
    r = json.loads((Path(sys.argv[1]) / f"join_{stream}.json").read_text())
    c = r.get("reco_coverage")
    if c is None:
        bad.append(f"{stream} reported no pass_reco coverage")
        continue
    print(f"{stream}: pass_reco {c['pass_reco_matched']:,}/{c['pass_reco_rows']:,} "
          f"({100*c['pass_reco_fraction']:.4f}%); "
          f"{c['unmatched_without_reco']:,} unmatched rows have no reco; "
          f"{c['matched_without_reco']:,} matched rows have no reco and are zeroed")
    if c["pass_reco_unmatched"]:
        bad.append(f"{stream} missing {c['pass_reco_unmatched']:,} pass_reco rows")
if bad:
    raise SystemExit(
        "[join] incomplete: " + "; ".join(bad) +
        ". Launching would train the arms on different populations.")
PY

echo "JOIN COMPLETE" > "$JOINDIR/terminal.txt"

# A join that passes its gate does not oblige us to launch 32 tasks on the
# spot. `LAUNCH=0` stops here so the joined index can be smoke-tested first --
# every defect found today was in the path between a passing join and a
# training step, and each cost a queue wait to discover.
if [[ "${LAUNCH:-1}" == "0" ]]; then
  echo "[join] LAUNCH=0: stopping after the join, nothing submitted"
  exit 0
fi

# Gather his tokens ONCE PER STAGE before any training task starts. Each
# stage's tasks then memory-map it; the key refuses a cache from another
# stage or split.
PRE=$(sbatch --parsable \
  --export=ALL,CHECKOUT="$CHECKOUT",OUTPUT="$OUTPUT",COMMIT="$COMMIT",INPUTS_NPZ="$INVENTORY",THEIRS_INDEX="$JOINDIR" \
  nd-unfolding/pet/configuration_comparison/sbatch_prematerialize.sh)
echo "prematerialize=$PRE"

export STAGE CHECKOUT OUTPUT COMMIT INPUTS_NPZ THEIRS_INDEX
INPUTS_NPZ="$INVENTORY"
THEIRS_INDEX="$JOINDIR"
LAUNCHER=nd-unfolding/pet/configuration_comparison/sbatch_campaign.sh

TUNING=$(sbatch --parsable --array=1-8 --dependency=afterok:$PRE \
  --export=ALL,STAGE=tuning,CHECKOUT="$CHECKOUT",OUTPUT="$OUTPUT",COMMIT="$COMMIT",INPUTS_NPZ="$INVENTORY",THEIRS_INDEX="$JOINDIR",THEIRS_CACHE="$OUTPUT/cache/theirs-tuning.npz" \
  "$LAUNCHER")
# Select each arm's rate on the tuning split, before the pilot exists.
SELECT=$(sbatch --parsable --dependency=afterok:$TUNING \
  --export=ALL,CHECKOUT="$CHECKOUT",OUTPUT="$OUTPUT",COMMIT="$COMMIT",INPUTS_NPZ="$INVENTORY" \
  nd-unfolding/pet/configuration_comparison/sbatch_select_lr.sh)
echo "select=$SELECT"

PILOT=$(sbatch --parsable --array=1-8 --dependency=afterok:$SELECT \
  --export=ALL,STAGE=pilot,CHECKOUT="$CHECKOUT",OUTPUT="$OUTPUT",COMMIT="$COMMIT",INPUTS_NPZ="$INVENTORY",THEIRS_INDEX="$JOINDIR",THEIRS_CACHE="$OUTPUT/cache/theirs-pilot.npz" \
  "$LAUNCHER")
FINAL=$(sbatch --parsable --array=1-16 --dependency=afterok:$PILOT \
  --export=ALL,STAGE=final,CHECKOUT="$CHECKOUT",OUTPUT="$OUTPUT",COMMIT="$COMMIT",INPUTS_NPZ="$INVENTORY",THEIRS_INDEX="$JOINDIR",THEIRS_CACHE="$OUTPUT/cache/theirs-final.npz" \
  "$LAUNCHER")
# The deliverable, automatically, when the final stage lands.
DELIVER=$(sbatch --parsable --dependency=afterok:$FINAL \
  --export=ALL,CHECKOUT="$CHECKOUT",OUTPUT="$OUTPUT",COMMIT="$COMMIT",INPUTS_NPZ="$INVENTORY" \
  nd-unfolding/pet/configuration_comparison/sbatch_report_and_deck.sh)
echo "deliver=$DELIVER"

printf 'tuning=%s\npilot=%s\nfinal=%s\ndeliver=%s\n' "$TUNING" "$PILOT" "$FINAL" "$DELIVER" \
  > "$OUTPUT/campaign_jobs.txt"
cat "$OUTPUT/campaign_jobs.txt"
