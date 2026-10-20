#!/bin/bash
# MP1-A S0 post-run checks, on a login node (as W2's comparisons and evaluation were), after the event-loop passes:
#   bash <tools>/measurement-paper/phase1/mp1/s0_postrun_checks.sh <NS> <tools>
# Writes JSON under <NS>/checks/ and prints one verdict line per check. Reads only; never overwrites a result.
#   G1 primary   base_cv vs zero, "equal": (a) publication/w2/compare_omnifiles.py as named by R4 (its reader keeps
#                the stale autosave cycle of each tree), (b) omnifile_io.py equal on the LATEST cycles;
#   G1 secondary the same two against W2b's rrzero_1A;
#   R4           CV-selected subset of the full-universe production file vs base_cv (event level);
#   species      check_species_pass.py on every +1 sigma pass against zero;
#   J cells      s0_jcell_shifts.py, every pass against zero.
set -o pipefail   # NOT set -u: conda activation references unset variables under nounset
NS="${1:?usage: s0_postrun_checks.sh <NS> <tools>}"; TOOLS="${2:?usage: s0_postrun_checks.sh <NS> <tools>}"
MP1="${TOOLS}/measurement-paper/phase1/mp1"; EV="${NS}/evloop"; OUT="${NS}/checks"
W2B=/pscratch/sd/j/josephrb/w2-recoil-20261006/w2b/evloop/rrzero/runEventLoopOmniFold_5D_1A_w2b_rrzero.root
PROD=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/runEventLoopOmniFold_5D_1A_universes_full_bkgaware.root
PYU=/global/homes/j/josephrb/.conda/envs/omnifold_py310/bin/python
(cd "${TOOLS}" && sha256sum --quiet -c TOOLS.sha256) || { echo "[post] ABORT: tool digests do not match"; exit 2; }
mkdir -p "${OUT}" || exit 2
run () {  # $1 = result json, rest = command; refuses to overwrite
  local res="$1"; shift
  [[ -e "${res}" ]] && { echo "[post] skip (exists) ${res}"; return 0; }
  "$@" > "${res}.log" 2>&1; local rc=$?
  echo "[post] rc=${rc} $(basename "${res}")"
}
# (a) the W2 comparer needs ROOT: run it in the ROOT environment, in a subshell.
( source /pscratch/sd/j/josephrb/MINERvA-OmniFold/setup_salloc_env.sh >/dev/null 2>&1
  run "${OUT}/g1_primary_w2comparer.json" python "${TOOLS}/publication/w2/compare_omnifiles.py" \
      --out "${OUT}/g1_primary_w2comparer.json" equal "${EV}/base_cv.root" "${EV}/zero.root"
  run "${OUT}/g1_secondary_w2comparer.json" python "${TOOLS}/publication/w2/compare_omnifiles.py" \
      --out "${OUT}/g1_secondary_w2comparer.json" equal "${W2B}" "${EV}/zero.root" )
run "${OUT}/g1_primary_latest.json" "${PYU}" -I "${MP1}/omnifile_io.py" --out "${OUT}/g1_primary_latest.json" \
    equal "${EV}/base_cv.root" "${EV}/zero.root"
run "${OUT}/g1_secondary_latest.json" "${PYU}" -I "${MP1}/omnifile_io.py" --out "${OUT}/g1_secondary_latest.json" \
    equal "${W2B}" "${EV}/zero.root"
run "${OUT}/r4_prod_vs_base_cv.json" "${PYU}" -I "${MP1}/s0_r4_event_check.py" "${PROD}" "${EV}/base_cv.root" \
    --out "${OUT}/r4_prod_vs_base_cv.json"
PASSES=()
for f in "${EV}"/*_p1_fprop_*.root; do
  [[ -e "$f" ]] || continue
  b=$(basename "$f" .root); sp=${b%%_p1_*}; fz=${b##*_fprop_}
  run "${OUT}/species_${b}.json" "${PYU}" -I "${MP1}/check_species_pass.py" "${EV}/zero.root" "$f" \
      --species "${sp}" --sign 1 --q0 fprop --fuzz "${fz}" --out "${OUT}/species_${b}.json"
  PASSES+=(--pass "${b}=${f}")
done
run "${OUT}/jcell_shifts.json" "${PYU}" -I "${MP1}/s0_jcell_shifts.py" --repo "${TOOLS}" --control "${EV}/zero.root" \
    "${PASSES[@]}" --pass "base_cv=${EV}/base_cv.root" --out "${OUT}/jcell_shifts.json"
for j in "${OUT}"/*.json; do
  v=$(grep -m1 -o '"\(verdict\|cv_selected_identical\)": *[A-Za-z"_]*' "$j")
  echo "[post] $(basename "$j"): ${v:-see file}"
done
