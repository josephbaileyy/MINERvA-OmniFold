#!/bin/bash
#SBATCH -A m3246
#SBATCH -q debug
#SBATCH -C cpu
#SBATCH -N 1
#SBATCH -t 00:25:00
#SBATCH -J mp3_nuwro_h_probe
#SBATCH -o /pscratch/sd/j/josephrb/measurement-paper/phase0/mp3/%x_%j.out
# Phase-0 probe P-MP3 (measurement-paper PLAN.md): does NuWro v21_09_1 run numu CC
# on a free proton with the ME-FHC flux, which channels fire, and what does an
# event cost? A paired C12 control uses the production card of work_nuwro_p*.
# Descriptive only: no cell-level target effect is computed here.
set -eo pipefail                      # no -u: the UPS setup reads unset variables
G=/pscratch/sd/j/josephrb/MINERvA-OmniFold/3d-unfolding/genie
OUT=/pscratch/sd/j/josephrb/measurement-paper/phase0/mp3
N=${N:-20000}

# Source a copy so the nuwro_home symlink dir lands under OUT, not under G.
cp "$G/setup_nuwro.sh" "$OUT/setup_nuwro.sh"
set +e
source "$OUT/setup_nuwro.sh"
rc=$?
set -e
[ $rc -eq 0 ] || { echo "[probe] setup failed rc=$rc" >&2; exit 1; }
export NUWRO_FLUX="$G/flux_mefhc_numu_nuwro.root"
FLAT=/pscratch/sd/j/josephrb/s5p-20260926/gen5d/code/nuwro_to_flat_5d.C
sha256sum "$G/setup_nuwro.sh" "$NUWRO_FLUX" "$FLAT" "$NUWRO_HOME/bin/nuwro"

for T in H C12; do
  mkdir -p "$OUT/$T"
  if [ "$T" = H ]; then
    # verbatim from the shipped data/target/proton.txt
    TGT=$'nucleus_p = 1\nnucleus_n = 0\nnucleus_target = 0'
  else
    TGT=$'nucleus_p = 6\nnucleus_n = 6'
  fi
  cat > "$OUT/$T/params.txt" <<EOF
random_seed = 9101
number_of_events = $N
number_of_test_events = 50000
beam_particle = 14
beam_type = 5
beam_inputroot = $NUWRO_FLUX
beam_inputroot_flux = $NUWRO_FLUX_HIST
target_type = 0
$TGT
dyn_qel_cc = 1
dyn_res_cc = 1
dyn_dis_cc = 1
dyn_coh_cc = 1
dyn_mec_cc = 1
EOF
  (
    cd "$OUT/$T"
    echo "[probe] $T start $(date -u '+%F %T UTC')"
    rc=0; /usr/bin/time -v "$NUWRO_HOME/bin/nuwro" -i params.txt -o "nuwro_$T.root" > "nuwro_$T.log" 2> "time_$T.txt" || rc=$?
    echo "[probe] $T nuwro rc=$rc end $(date -u '+%F %T UTC')"
    rc=0; root -l -b -q "$FLAT(\"nuwro_$T.root\",\"flat5d_$T.root\")" > "flat_$T.log" 2>&1 || rc=$?
    echo "[probe] $T flat rc=$rc"
  ) &
done
wait
echo "[probe] done $(date -u '+%F %T UTC')"
