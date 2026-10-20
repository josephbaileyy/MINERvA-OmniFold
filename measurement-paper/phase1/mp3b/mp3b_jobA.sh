#!/bin/bash
#SBATCH -A m3246
#SBATCH -C cpu
#SBATCH -q debug
#SBATCH -N 1
#SBATCH -t 00:30:00
#SBATCH -J mp3bA
#SBATCH -o /pscratch/sd/j/josephrb/measurement-paper/phase1/mp3b/runA/logs/mp3bA-%j.out
# MP3-B run A, the kaskada_on check, and variant C (the director's rulings after the 60022605 abort).
#  1. Every CHUNK of SEEDS-chunked.txt runs under card k1 (the H card) into gen/ and under card k0 (the same card
#     plus kaskada_on = 0) into gen_k0/, the two concurrently, each with its own sequential abort/alternate chain:
#     an aborted attempt is DISCARDED WHOLE (.root/.part deleted, logs kept), then ALT1, then ALT2, then DROPPED.
#     Then, per chunk: the completed k1 attempt is compared event by event (compare_kaskada.C) with the k0 run of the
#     same seed; if k0's chain did not complete that seed, a k0 twin of that seed is run for the comparison only.
#     All chunks run concurrently on this node, one setup_nuwro.sh copy per chunk and card. No chunk runs twice
#     under the same card and seed. In parallel the frozen macro re-converts the frozen C12 files (control C1).
#  2. mp3b_build.py for k1 and for k0 (C0 on every attempt's .par; for k0 kaskada_on is the one extra allowed key),
#     C1, B1, B2, B3 (STOP per variant on failure); mp3b_kaskada.py applies the declared switch rule.
#  3. mp3b_eval.py: (A, k1), (A, k0) with B4 gating; variant (C) mixed with B4 reported only.
# Writes only under $D. No set -u (UPS/conda). Paths absolute (sbatch runs a copy).
set -o pipefail
D=/pscratch/sd/j/josephrb/measurement-paper/phase1/mp3b/runA
G=/pscratch/sd/j/josephrb/MINERvA-OmniFold/3d-unfolding/genie
S5P=/pscratch/sd/j/josephrb/s5p-20260926
FLAT=$S5P/gen5d/code/nuwro_to_flat_5d.C
CMP=$D/code/compare_kaskada.C
FLUX_MAIN=$G/flux_mefhc_numu_nuwro.root
FLUX_SUPP=$S5P/gen5d_fluxfix/supp/flux_phi_t_50_100.root
SEEDS=$D/code/SEEDS-chunked.txt
[ -e "$D/gen" ] || [ -e "$D/gen_k0" ] || [ -e "$D/out" ] && { echo "STOP: a run directory exists; refusing to overwrite"; exit 2; }
mkdir -p "$D/gen/H_main" "$D/gen/H_supp" "$D/gen/parity" "$D/gen/compare" "$D/gen_k0/H_main" "$D/gen_k0/H_supp" \
  "$D/out" "$D/tmp" "$D/env" || exit 2
echo "host $(hostname) start $(date -u +%FT%TZ) job ${SLURM_JOB_ID:-none} nproc $(nproc)"
mapfile -t CHUNKS < <(grep '^CHUNK ' "$SEEDS")
echo "chunks declared: ${#CHUNKS[@]}  SEEDS sha256 $(sha256sum "$SEEDS" | cut -c1-64)"
[ ${#CHUNKS[@]} -gt 0 ] || { echo "STOP: no CHUNK lines"; exit 2; }
for line in "${CHUNKS[@]}"; do
  read -r _ s i _rest <<< "$line"
  for c in k1 k0; do
    mkdir -p "$D/env/${c}_${s}_c$i" && cp "$G/setup_nuwro.sh" "$D/env/${c}_${s}_c$i/setup_nuwro.sh" || exit 2
  done
done
mkdir -p "$D/env/parity" && cp "$G/setup_nuwro.sh" "$D/env/parity/setup_nuwro.sh" || exit 2
sha256sum "$G/setup_nuwro.sh" "$S5P/gen5d/code/setup_nuwro.sh" "$FLAT" "$FLUX_MAIN" "$FLUX_SUPP" \
  "$G/work_nuwro_p1/nuwro_p1.root" "$S5P/gen5d_fluxfix/supp/nuwro/nuwro_supp.root" "$D"/code/* "$D"/inputs/* \
  > "$D/gen/input_sha256.txt"
cat "$D/gen/input_sha256.txt"
sha256sum "$D"/env/*/setup_nuwro.sh | cut -c1-64 | sort -u | sed 's/^/setup copies sha256 (unique): /'

attempt() {  # CARD W SEED N FLUX -> 0 ok (flat written), 5 flat failure, else NuWro's rc (outputs discarded)
  local CARD=$1 W=$2 SEED=$3 N=$4 FLUX=$5 rc
  mkdir -p "$W" && cd "$W" || return 2
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
  [ "$CARD" = k0 ] && echo "kaskada_on = 0" >> params.txt
  readlink -f "$NUWRO_HOME/bin/nuwro" > nuwro_binary.txt
  /usr/bin/time -v "$NUWRO_HOME/bin/nuwro" -i params.txt -o nuwro.root > nuwro.log 2> stderr_time.txt
  rc=$?
  if [ $rc = 0 ]; then
    root -l -b -q "$FLAT(\"nuwro.root\",\"flat5d.root\")" > flat.log 2>&1 || return 5
    return 0
  fi
  rm -f nuwro.root nuwro.root.*.part      # an aborted attempt is discarded whole; its logs stay
  return $rc
}

chain() {  # CARD ROOT S I N FLUX S0 S1 S2 -- in a subshell
  local CARD=$1 C=$2/$3/c$4 S=$3 I=$4 N=$5 FLUX=$6 k rc
  local seeds=("$7" "$8" "$9")
  mkdir -p "$C"
  source "$D/env/${CARD}_${S}_c$I/setup_nuwro.sh" > "$C/setup.log" 2>&1
  for k in 0 1 2; do
    attempt "$CARD" "$C/a$k" "${seeds[$k]}" "$N" "$FLUX"
    rc=$?
    printf '%s\t%s\t%s\n' "$k" "${seeds[$k]}" "$rc" >> "$C/attempts.tsv"
    [ $rc = 0 ] && { echo "ok $k ${seeds[$k]}" > "$C/RESULT"; return 0; }
    [ $rc = 5 ] && { echo "flatfail $k ${seeds[$k]}" > "$C/RESULT"; return 5; }
  done
  echo "dropped" > "$C/RESULT"
  return 0
}

pair() {  # S I N FLUX S0 S1 S2 -- both cards, then the matched comparison
  local S=$1 I=$2 N=$3 FLUX=$4 p1 p0 r1 r0 res1 res0 f1 f0 rc
  local OUTC=$D/gen/compare/${S}_c$I.txt
  ( chain k1 "$D/gen" "$S" "$I" "$N" "$FLUX" "$5" "$6" "$7" ) & p1=$!
  ( chain k0 "$D/gen_k0" "$S" "$I" "$N" "$FLUX" "$5" "$6" "$7" ) & p0=$!
  wait $p1; r1=$?
  wait $p0; r0=$?
  [ $r1 = 0 ] && [ $r0 = 0 ] || return 5
  read -r -a res1 < "$D/gen/$S/c$I/RESULT"
  read -r -a res0 < "$D/gen_k0/$S/c$I/RESULT"
  if [ "${res1[0]}" != ok ]; then echo "NO_COMPARISON k1_dropped (no completed k1 event)" > "$OUTC"; return 0; fi
  f1=$D/gen/$S/c$I/a${res1[1]}/nuwro.root
  f0=""
  if [ "${res0[0]}" = ok ] && [ "${res0[2]}" = "${res1[2]}" ]; then
    f0=$D/gen_k0/$S/c$I/a${res0[1]}/nuwro.root
  elif awk -F'\t' -v s="${res1[2]}" '$2==s && $3!=0 {f=1} END {exit !f}' "$D/gen_k0/$S/c$I/attempts.tsv"; then
    echo "NO_COMPARISON k0_aborted_at_seed ${res1[2]} (k1 completed it)" > "$OUTC"; return 0
  else
    source "$D/env/k0_${S}_c$I/setup_nuwro.sh" > "$D/gen_k0/$S/c$I/twin_setup.log" 2>&1
    attempt k0 "$D/gen_k0/$S/c$I/twin_s${res1[2]}" "${res1[2]}" "$N" "$FLUX"
    rc=$?
    printf 'twin\t%s\t%s\n' "${res1[2]}" "$rc" >> "$D/gen_k0/$S/c$I/twin.tsv"
    [ $rc = 0 ] || { echo "NO_COMPARISON k0_twin_failed_at_seed ${res1[2]} rc=$rc" > "$OUTC"; return 0; }
    f0=$D/gen_k0/$S/c$I/twin_s${res1[2]}/nuwro.root
  fi
  source "$D/env/k0_${S}_c$I/setup_nuwro.sh" > /dev/null 2>&1
  root -l -b -q "$CMP(\"$f1\",\"$f0\",\"$OUTC\")" > "${OUTC%.txt}.log" 2>&1 || { echo "NO_COMPARISON compare_macro_failed" >> "$OUTC"; return 5; }
  return 0
}

parity() {  # control C1
  local rc1 rc2
  source "$D/env/parity/setup_nuwro.sh" > "$D/gen/parity/setup.log" 2>&1
  cd "$D/gen/parity" || return 2
  root -l -b -q "$FLAT(\"$G/work_nuwro_p1/nuwro_p1.root\",\"flat5d_C12_p1.root\")" > flat_p1.log 2>&1
  rc1=$?
  root -l -b -q "$FLAT(\"$S5P/gen5d_fluxfix/supp/nuwro/nuwro_supp.root\",\"flat5d_C12_supp.root\")" > flat_supp.log 2>&1
  rc2=$?
  [ $rc1 = 0 ] && [ $rc2 = 0 ]
}

pids=(); tags=()
for line in "${CHUNKS[@]}"; do
  read -r _ s i n s0 s1 s2 <<< "$line"
  if [ "$s" = H_main ]; then fl=$FLUX_MAIN; elif [ "$s" = H_supp ]; then fl=$FLUX_SUPP; else echo "STOP: sample $s"; exit 2; fi
  ( pair "$s" "$i" "$n" "$fl" "$s0" "$s1" "$s2" ) & pids+=($!); tags+=("$s/c$i")
done
( parity ) & pp=$!
bad=0
for j in "${!pids[@]}"; do
  wait "${pids[$j]}"; rc=$?
  t=${tags[$j]}
  echo "[$t] rc=$rc k1: $(cat "$D/gen/$t/RESULT" 2>/dev/null) ($(wc -l < "$D/gen/$t/attempts.tsv" 2>/dev/null) attempts)  k0: $(cat "$D/gen_k0/$t/RESULT" 2>/dev/null) ($(wc -l < "$D/gen_k0/$t/attempts.tsv" 2>/dev/null) attempts)  cmp: $(grep -E '^(RNG_ALIGNED|N_POST_WITHIN_TOL|N_COMPARED|NO_COMPARISON)' "$D/gen/compare/${t%/*}_${t#*/}.txt" 2>/dev/null | tr '\n' ' ')"
  [ $rc = 0 ] || bad=1
done
wait $pp; rp=$?
echo "GEN done $(date -u +%FT%TZ) chunk_failure=$bad parity_rc=$rp"
genok=1
[ $bad = 0 ] && [ $rp = 0 ] || { genok=0; echo "STOP (A): a chunk could not be run, converted or compared, or C1 conversion failed; (C) still runs"; }
sha256sum "$D"/gen/H_*/c*/a*/flat5d.root "$D"/gen_k0/H_*/c*/a*/flat5d.root "$D"/gen/parity/*.root > "$D/gen/output_sha256.txt" 2>/dev/null

eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/root_6_28"
unset PYTHONPATH
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 TMPDIR=$D/tmp
mkdir -p "$D/run"
cd "$D/run" || exit 2
echo "python $(command -v python3)"
python3 -c 'import sys, numpy, scipy; print(sys.version.split()[0], numpy.__version__, scipy.__version__)'
EV=(--design "$D/inputs/design.json" --s5c-contract "$D/inputs/s5c_contract.json" --v "$S5P/stage3/V/V-s3v.npz"
    --frozen-eval "$D/inputs/joint-evaluate.json")
python3 "$D/code/mp3b_kaskada.py" --compare-dir "$D/gen/compare" --out "$D/out/kaskada_decision.json"
echo "KASKADA rc=$? $(date -u +%FT%TZ)"
declare -A RC
for c in k1 k0; do
  g=$D/gen; [ $c = k0 ] && g=$D/gen_k0
  RC[b$c]=5; RC[e$c]=skipped
  if [ $genok = 1 ]; then
    python3 "$D/code/mp3b_build.py" --out "$D/out/build_$c" --gen "$g" --seeds "$SEEDS" --card $c --parity-dir "$D/gen/parity"
    RC[b$c]=$?
  fi
  echo "BUILD_$c rc=${RC[b$c]} $(date -u +%FT%TZ)"
  if [ "${RC[b$c]}" = 0 ]; then
    python3 "$D/code/mp3b_eval.py" "${EV[@]}" --build-dir "$D/out/build_$c" --out "$D/out/eval_$c" \
      --fine mp3b_fine_nuwro.npz --variant "NuWro-on-CH, H card $c (kaskada_on $([ $c = k0 ] && echo 0 || echo 1)), chunked" --b4-gating yes
    RC[e$c]=$?
  fi
  echo "EVAL_$c rc=${RC[e$c]} $(date -u +%FT%TZ)"
done
python3 "$D/code/mp3b_mixed.py" --out "$D/out/mixed_build"
rcC1=$?
rcC2=skipped
if [ $rcC1 = 0 ]; then
  python3 "$D/code/mp3b_eval.py" "${EV[@]}" --build-dir "$D/out/mixed_build" --out "$D/out/eval_mixed" \
    --fine mp3b_fine_mixed.npz --variant "mixed: NuWro carbon + GENIE hydrogen; not NuWro-on-CH" --b4-gating no
  rcC2=$?
fi
echo "BUILD_C rc=$rcC1 EVAL_C rc=$rcC2 end $(date -u +%FT%TZ)"
[ "${RC[bk1]}" = 0 ] && [ "${RC[ek1]}" = 0 ] && [ "${RC[bk0]}" = 0 ] && [ "${RC[ek0]}" = 0 ] && [ "$rcC1" = 0 ] && [ "$rcC2" = 0 ] && exit 0
exit 6
