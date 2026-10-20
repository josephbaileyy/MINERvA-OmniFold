#!/bin/bash
#SBATCH -A m3246
#SBATCH -C cpu
#SBATCH -q shared
#SBATCH -c 8
#SBATCH -t 01:30:00
#SBATCH -J mp3b
#SBATCH -o /pscratch/sd/j/josephrb/measurement-paper/phase1/mp3b/logs/mp3b-%j.out
# MP3-B (PLAN.md §4.3, frozen by BINDING-PHASE1-20261019; D6: reported beside A7, never in place of it).
#  1. NuWro v21_09_1 (CVMFS e20:debug, via a COPY of setup_nuwro.sh so its symlinks land under $D) on a free
#     proton: H main = the production card (run_nuwro.sh) with only the target lines changed; H supp = the frozen
#     50-100 GeV supplement card (run_gen5d_supplement.sh nuwro) with only the target lines changed. Seeds and
#     counts from SEEDS.txt. Both converted with the frozen gen5d copy of nuwro_to_flat_5d.C. In parallel, the
#     same macro re-converts the frozen C12 p1 and supplement NuWro files (control C1).
#  2. mp3b_build.py: controls C0/C1, gates B1, B2, B3 (STOP on failure), then the H and CH fine products.
#  3. mp3b_eval.py: gate B4 (STOP on failure), then the readout and the descriptive replay.
# Writes only under $D. No set -u (it aborts the UPS and conda activations). sbatch runs a copy of this file,
# so every path is absolute and nothing is derived from BASH_SOURCE.
set -o pipefail
D=/pscratch/sd/j/josephrb/measurement-paper/phase1/mp3b
G=/pscratch/sd/j/josephrb/MINERvA-OmniFold/3d-unfolding/genie
S5P=/pscratch/sd/j/josephrb/s5p-20260926
FLAT=$S5P/gen5d/code/nuwro_to_flat_5d.C
FLUX_MAIN=$G/flux_mefhc_numu_nuwro.root
FLUX_SUPP=$S5P/gen5d_fluxfix/supp/flux_phi_t_50_100.root
seed() { sed -n "s/^$1=\([0-9][0-9]*\)$/\1/p" "$D/code/SEEDS.txt"; }
H_MAIN_SEED=$(seed H_MAIN_SEED); H_MAIN_N=$(seed H_MAIN_N); H_SUPP_SEED=$(seed H_SUPP_SEED); H_SUPP_N=$(seed H_SUPP_N)
for v in "$H_MAIN_SEED" "$H_MAIN_N" "$H_SUPP_SEED" "$H_SUPP_N"; do
  [ -n "$v" ] || { echo "STOP: SEEDS.txt incomplete"; exit 2; }
done
[ -e "$D/gen" ] || [ -e "$D/out" ] && { echo "STOP: $D/gen or $D/out exists; refusing to overwrite"; exit 2; }
mkdir -p "$D/gen/H_main" "$D/gen/H_supp" "$D/gen/parity" "$D/out" "$D/tmp" || exit 2
echo "host $(hostname) start $(date -u +%FT%TZ) job ${SLURM_JOB_ID:-none}"
echo "seeds H_main=$H_MAIN_SEED N=$H_MAIN_N  H_supp=$H_SUPP_SEED N=$H_SUPP_N"
# one COPY of setup_nuwro.sh per parallel task: each gets its own nuwro_home_dbg symlink dir under $D/env/<task>,
# so no task re-links a binary another task is about to execute
for t in H_main H_supp parity; do
  mkdir -p "$D/env/$t" && cp "$G/setup_nuwro.sh" "$D/env/$t/setup_nuwro.sh" || exit 2
done
sha256sum "$G/setup_nuwro.sh" "$D"/env/*/setup_nuwro.sh "$S5P/gen5d/code/setup_nuwro.sh" "$FLAT" "$FLUX_MAIN" "$FLUX_SUPP" \
  "$G/work_nuwro_p1/nuwro_p1.root" "$S5P/gen5d_fluxfix/supp/nuwro/nuwro_supp.root" "$D"/code/* "$D"/inputs/* \
  > "$D/gen/input_sha256.txt"
cat "$D/gen/input_sha256.txt"

gen() {  # TAG N SEED FLUX -- run in a subshell
  local TAG=$1 N=$2 SEED=$3 FLUX=$4 W=$D/gen/$1 rc
  source "$D/env/$TAG/setup_nuwro.sh" > "$W/setup.log" 2>&1
  export NUWRO_FLUX=$FLUX
  cd "$W" || return 2
  cat > params.txt <<EOF
random_seed = $SEED
number_of_events = $N
number_of_test_events = 50000
beam_particle = 14
beam_type = 5
beam_inputroot = $FLUX
beam_inputroot_flux = flux_numu
target_type = 0
nucleus_p = 1
nucleus_n = 0
nucleus_target = 0
dyn_qel_cc = 1
dyn_res_cc = 1
dyn_dis_cc = 1
dyn_coh_cc = 1
dyn_mec_cc = 1
EOF
  readlink -f "$NUWRO_HOME/bin/nuwro" > nuwro_binary.txt
  echo "[$TAG] start $(date -u +%FT%TZ) binary $(cat nuwro_binary.txt)"
  /usr/bin/time -v "$NUWRO_HOME/bin/nuwro" -i params.txt -o "nuwro_$TAG.root" > "nuwro_$TAG.log" 2> "time_$TAG.txt"
  rc=$?
  echo "[$TAG] nuwro rc=$rc $(date -u +%FT%TZ)"
  [ $rc = 0 ] || return $rc
  root -l -b -q "$FLAT(\"nuwro_$TAG.root\",\"flat5d_$TAG.root\")" > "flat_$TAG.log" 2>&1
  rc=$?
  echo "[$TAG] flat rc=$rc $(date -u +%FT%TZ)"
  return $rc
}

parity() {  # control C1: the frozen macro re-run here on the frozen C12 NuWro files (read-only inputs)
  local rc1 rc2
  source "$D/env/parity/setup_nuwro.sh" > "$D/gen/parity/setup.log" 2>&1
  cd "$D/gen/parity" || return 2
  root -l -b -q "$FLAT(\"$G/work_nuwro_p1/nuwro_p1.root\",\"flat5d_C12_p1.root\")" > flat_p1.log 2>&1
  rc1=$?
  root -l -b -q "$FLAT(\"$S5P/gen5d_fluxfix/supp/nuwro/nuwro_supp.root\",\"flat5d_C12_supp.root\")" > flat_supp.log 2>&1
  rc2=$?
  echo "[parity] flat rc=$rc1/$rc2 $(date -u +%FT%TZ)"
  [ $rc1 = 0 ] && [ $rc2 = 0 ]
}

( gen H_main "$H_MAIN_N" "$H_MAIN_SEED" "$FLUX_MAIN" ) & pm=$!
( gen H_supp "$H_SUPP_N" "$H_SUPP_SEED" "$FLUX_SUPP" ) & ps=$!
( parity ) & pp=$!
wait $pm; rm_=$?
wait $ps; rs_=$?
wait $pp; rp_=$?
echo "GEN rc main=$rm_ supp=$rs_ parity=$rp_ $(date -u +%FT%TZ)"
[ $rm_ = 0 ] && [ $rs_ = 0 ] && [ $rp_ = 0 ] || { echo "STOP: generation or conversion failed"; exit 5; }
sha256sum "$D"/gen/H_main/*.root "$D"/gen/H_supp/*.root "$D"/gen/parity/*.root > "$D/gen/output_sha256.txt"
cat "$D/gen/output_sha256.txt"

eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/root_6_28"
unset PYTHONPATH
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 TMPDIR=$D/tmp
mkdir -p "$D/run"
cd "$D/run" || exit 2
echo "python $(command -v python3)"
python3 -c 'import sys, numpy, scipy; print(sys.version.split()[0], numpy.__version__, scipy.__version__)'
python3 "$D/code/mp3b_build.py" --out "$D/out/build" --gen "$D/gen" --seeds "$D/code/SEEDS.txt"
rc1=$?
echo "BUILD rc=$rc1 $(date -u +%FT%TZ)"
[ $rc1 = 0 ] || { echo "STOP: build control or gate B1-B3 failed (rc=$rc1); no evaluation"; exit $rc1; }
python3 "$D/code/mp3b_eval.py" --design "$D/inputs/design.json" --s5c-contract "$D/inputs/s5c_contract.json" \
  --v "$S5P/stage3/V/V-s3v.npz" --frozen-eval "$D/inputs/joint-evaluate.json" \
  --build-dir "$D/out/build" --out "$D/out/eval"
rc2=$?
echo "EVAL rc=$rc2 end $(date -u +%FT%TZ)"
exit $rc2
