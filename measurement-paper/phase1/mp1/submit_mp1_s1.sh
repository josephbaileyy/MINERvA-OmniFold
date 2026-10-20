#!/bin/bash
# MP1-A S1: submit every event-loop pass (12 playlists x 11 variants) as separate shared jobs. Perlmutter login node.
#   bash submit_mp1_s1.sh <S1 namespace> <tools dir> [--submit]
# Variants: zero (k = 0 control); proton, meson, em, other at -1/+1 sigma (the primary band); xtalk -1/+1 sigma (the
# R3 variant only). q0: F-propagation with the playlist's G0-passed table (s1/g0/F_<PL>.txt); fuzz: pro-rata (R2).
# --time per playlist = max(3 h, 1.8 x W2b's slowest 1A..1P pass, rounded up to 0.5 h): S0's species passes ran up to
# 1.38x W2's slowest 1A pass, and W2b's 1M took 12,697 s (W2 review C1). Without --submit it prints the plan.
# A pass whose output exists, or that is already in submitted.tsv, is not resubmitted.
set -o pipefail   # NOT set -u
NS="${1:?usage: submit_mp1_s1.sh <NS> <tools> [--submit]}"; TOOLS="${2:?tools}"; DO="${3:-}"
S0=/pscratch/sd/j/josephrb/measurement-paper/phase1/mp1/s0
BIN="${S0}/build/bld_mod/runEventLoopOmniFold"; MD5=15b4789fbd8e9c1fc5aeb14c1b4626b0
L="${TOOLS}/measurement-paper/phase1/mp1/sbatch_mp1_s1_evloop.sh"
SUB="${NS}/submitted.tsv"
(cd "${TOOLS}" && sha256sum --quiet -c TOOLS.sha256) || { echo "[s1] ABORT: tool digests"; exit 2; }
[[ "$(md5sum "${BIN}" | cut -d' ' -f1)" == "${MD5}" ]] || { echo "[s1] ABORT: binary md5"; exit 2; }
declare -A W2MAX=([1A]=4842 [1B]=1274 [1C]=2431 [1D]=7856 [1E]=6677 [1F]=9313 [1G]=7691 [1L]=566 [1M]=12697
                  [1N]=8515 [1O]=1822 [1P]=2534)   # LEDGER-w2.tsv: slowest of rr0/rr1/rrzero (1A: W2a cost pass)
VARIANTS="zero proton_m1 proton_p1 meson_m1 meson_p1 em_m1 em_p1 other_m1 other_p1 xtalk_m1 xtalk_p1"
mkdir -p "${NS}/logs"; touch "${SUB}"
tot_h=0; n=0
for pl in 1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P; do
  lim=$(python3 -c "import math;print(max(3.0, math.ceil(1.8*${W2MAX[$pl]}/1800.0)/2.0))")
  hh=${lim%.*}; mm=$([[ ${lim#*.} == 5 ]] && echo 30 || echo 00)
  T="${NS}/g0/F_${pl}.txt"
  python3 -c "import json,sys;sys.exit(0 if json.load(open('${NS}/g0/G0_${pl}.json'))['G0']=='PASS' else 1)" \
    || { echo "[s1] ABORT: G0 is not PASS for ${pl}"; exit 3; }
  for v in ${VARIANTS}; do
    label="mp1s1_${v}_${pl}"
    out="${NS}/evloop/${v}/runEventLoopOmniFold_5D_${pl}_${v}.root"
    [[ -e "${out}" ]] && continue
    awk -F'\t' -v l="${label}" '$2==l{f=1} END{exit !f}' "${SUB}" && continue
    tot_h=$(python3 -c "print(${tot_h}+${lim})"); n=$((n+1))
    cmd=(sbatch --parsable --time="${hh}:${mm}:00" --job-name="${label}" --output="${NS}/logs/%x_%j.out"
         "${L}" "${NS}" "${v}" "${pl}" "${BIN}" "${MD5}" fprop prorata "${T}")
    if [[ "${DO}" == "--submit" ]]; then
      SPECIES_ENV_CHECK_ONLY=1 bash "${L}" "${NS}" "${v}" "${pl}" "${BIN}" "${MD5}" fprop prorata "${T}" > /dev/null || exit 6
      jid=$("${cmd[@]}") || { echo "[s1] sbatch failed for ${label}"; exit 4; }
      printf '%s\t%s\t%s\t10\n' "${jid}" "${label}" "${lim}" >> "${SUB}"; echo "[s1] ${label} ${lim}h -> ${jid}"
    else
      echo "${cmd[*]}"
    fi
  done
done
echo "[s1] ${n} jobs; worst-case reservation $(python3 -c "print(round(${tot_h}*10/256,3))") node-h (sum of limits x billing 10/256)"
