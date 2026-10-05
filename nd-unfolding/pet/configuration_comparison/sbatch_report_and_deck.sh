#!/bin/bash
# Produce the deliverable the moment the campaign lands.
#
# The chain ended at `final`, so the report and the deck waited on somebody
# running two commands. They do not need a person: every input is pinned --
# the reference is `frozen_design.REFERENCE["aggregate"]`, computed from the
# frozen endpoint before any comparative result existed -- and both steps have
# been run end to end on real weights.
#
# It writes the report, the deck source, the rendered PDF and the
# claim-to-evidence index into the campaign directory, commits them in the
# cluster checkout and leaves a git bundle, so adopting them is one fetch.
#
# It does NOT send anything. The goal says so in as many words: the deck is
# FOR Ben and must not be sent to him.
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --time=02:00:00
#SBATCH --job-name=pet-report-deck
set -eo pipefail

checkout=${CHECKOUT:?}; output=${OUTPUT:?}; commit=${COMMIT:?}; inputs=${INPUTS_NPZ:?}
cd "$checkout"
[[ "$(git rev-parse HEAD)" == "$commit" ]]

module load python
module load texlive

REF=$(python3 -c "import sys; sys.path.insert(0,'nd-unfolding/pet/configuration_comparison'); import frozen_design as fd; print(repr(fd.REFERENCE['aggregate']))")
echo "[deliver] reference $REF at niter $(python3 -c "import sys; sys.path.insert(0,'nd-unfolding/pet/configuration_comparison'); import frozen_design as fd; print(fd.REFERENCE['iterations'])")"

python3 nd-unfolding/pet/configuration_comparison/report_campaign.py \
  --campaign "$output" --closure-npz "$inputs" --reference "$REF" \
  --output "$output/campaign_report.json"

python3 nd-unfolding/pet/configuration_comparison/make_final_deck.py \
  --report "$output/campaign_report.json" \
  --outdir nd-unfolding/pet/configuration_comparison/slides \
  --stem final_comparison

cp "$output/campaign_report.json" nd-unfolding/pet/configuration_comparison/
git add -A nd-unfolding/pet/configuration_comparison
git -c user.name="MINERvA-OmniFold agent" -c user.email="noreply@anthropic.com" \
  commit -q -m "[pet] The matched comparison: report, deck and claim index

Produced by sbatch_report_and_deck.sh from campaign $output at $commit.
Reference $REF, pinned before any comparative result existed.

NOT SENT to anyone. PET remains diagnostic method development: this is not a
publication adoption, a covariance, a systematic, a central-value change or a
Gate-6 action." || echo "[deliver] nothing to commit"

git bundle create "$output/deliverable.bundle" "$commit..HEAD" || true
echo DELIVERED > "$output/terminal.txt"
ls -la nd-unfolding/pet/configuration_comparison/slides/final_comparison.pdf
