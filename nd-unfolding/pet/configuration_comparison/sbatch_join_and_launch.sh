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
    --output "$JOINDIR/join_${STREAM}.npz" \
    --report "$JOINDIR/join_${STREAM}.json"
done

# Refuse to launch on an incomplete join: an unmatched row cannot be trained on
# and must not be silently dropped for one arm only.
python3 - "$JOINDIR" <<'PY'
import json, sys
from pathlib import Path
bad = []
for stream in ("data", "sig"):
    r = json.loads((Path(sys.argv[1]) / f"join_{stream}.json").read_text())
    print(f"{stream}: {r['matched']:,}/{r['inventory_rows']:,} matched "
          f"({100*r['match_fraction']:.3f}%), {r['unmatched']:,} unmatched")
    if r["match_fraction"] < 0.999:
        bad.append(f"{stream} at {100*r['match_fraction']:.3f}%")
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
