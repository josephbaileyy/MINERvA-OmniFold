#!/bin/bash
# Build the per-period merged omnifiles and per-period flux files (login node; no Slurm).
#
#   bash build_inputs.sh            # builds PA, PB, PC and the control ALL; refuses to overwrite
#
# Merge: plain `hadd` of the May CV per-playlist files in production order, as the production CV merge
# (sbatch_hadd_MEFHC.sh:61). hadd concatenates the trees and sums mcPOTUsed/dataPOTUsed
# (and the hasTruthOnlyMisses/nTruthOnlyMisses parameters), so each period file carries its OWN POT ratio
# for get_pot_scales (unfold_2d_omnifold_unbinned.py:117-126).
# Flux: build_flux.py applies the pinned combine_flux_MEFHC.py reader and arithmetic to the period's playlists
# only; the combiner's own main() is also run for PA and ALL (it needs 1A) as an equivalence test.
# Every path is absolute. No `set -u` before the root_6_28 activation.
set -eo pipefail
NS=/pscratch/sd/j/josephrb/2d-closeout-period-unfold-20261014
D2=/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding
SCRIPTS=$NS/code/record/scripts   # this directory, copied from the record branch
source /pscratch/sd/j/josephrb/MINERvA-OmniFold/setup_salloc_env.sh   # root_6_28 + MAT (MnvH1D for the flux files)
export TMPDIR=$NS/tmp
mkdir -p "$NS/inputs" "$NS/flux" "$NS/results" "$TMPDIR"

declare -A PER=(
  [PA]="1A 1B 1C 1D 1E 1F"
  [PB]="1G 1L 1M"
  [PC]="1N 1O 1P"
  [ALL]="1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P"
)
for P in PA PB PC ALL; do
  OUT=$NS/inputs/runEventLoopOmniFold_${P}.root
  if [ -e "$OUT" ]; then echo "REFUSE: $OUT exists"; exit 3; fi
  IN=(); for pl in ${PER[$P]}; do IN+=("$D2/runEventLoopOmniFold_${pl}.root"); done
  echo "[build] $(date -u +%FT%TZ) hadd $OUT <- ${PER[$P]}"
  hadd "$OUT" "${IN[@]}" > "$NS/results/hadd_${P}.log" 2>&1
  chmod a-w "$OUT"
done
for P in PA PB PC ALL; do
  python3 "$SCRIPTS/build_flux.py" "$P"
done
for P in PA ALL; do
  [ -e "$NS/tmp/flux_viamain_${P}.root" ] && { echo "REFUSE: $NS/tmp/flux_viamain_${P}.root exists"; exit 3; }
  python3 "$SCRIPTS/build_flux.py" --via-main "$P" "$NS/tmp/flux_viamain_${P}.root" > "$NS/results/flux_viamain_${P}.log"
done
(cd "$NS" && sha256sum inputs/*.root flux/*.root > "$NS/results/SHA256SUMS.inputs")
cat "$NS/results/SHA256SUMS.inputs"
