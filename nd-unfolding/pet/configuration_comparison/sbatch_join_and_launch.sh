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
for STREAM in data sig; do
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
for stream in ("data", "sig"):
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

export STAGE CHECKOUT OUTPUT COMMIT INPUTS_NPZ THEIRS_INDEX
INPUTS_NPZ="$INVENTORY"
THEIRS_INDEX="$JOINDIR"
LAUNCHER=nd-unfolding/pet/configuration_comparison/sbatch_campaign.sh

TUNING=$(sbatch --parsable --array=1-8 \
  --export=ALL,STAGE=tuning,CHECKOUT="$CHECKOUT",OUTPUT="$OUTPUT",COMMIT="$COMMIT",INPUTS_NPZ="$INVENTORY",THEIRS_INDEX="$JOINDIR" \
  "$LAUNCHER")
PILOT=$(sbatch --parsable --array=1-8 --dependency=afterok:$TUNING \
  --export=ALL,STAGE=pilot,CHECKOUT="$CHECKOUT",OUTPUT="$OUTPUT",COMMIT="$COMMIT",INPUTS_NPZ="$INVENTORY",THEIRS_INDEX="$JOINDIR" \
  "$LAUNCHER")
FINAL=$(sbatch --parsable --array=1-16 --dependency=afterok:$PILOT \
  --export=ALL,STAGE=final,CHECKOUT="$CHECKOUT",OUTPUT="$OUTPUT",COMMIT="$COMMIT",INPUTS_NPZ="$INVENTORY",THEIRS_INDEX="$JOINDIR" \
  "$LAUNCHER")
printf 'tuning=%s\npilot=%s\nfinal=%s\n' "$TUNING" "$PILOT" "$FINAL" \
  > "$OUTPUT/campaign_jobs.txt"
cat "$OUTPUT/campaign_jobs.txt"
