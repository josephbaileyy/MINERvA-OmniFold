#!/bin/bash
# MP1-A S1 after the event loops (the W2b chain; publication/w2/submit_w2b.sh stages merge/dump/unfold). Login node.
#   bash mp1_s1_pipeline.sh <NS> <tools> status
#   bash mp1_s1_pipeline.sh <NS> <tools> g1     <PL...>     # zero_<PL> vs W2b rrzero_<PL>, W2 "equal", latest cycles
#   bash mp1_s1_pipeline.sh <NS> <tools> merge  <variant...> # hadd_universes_full.py, 1A..1P order (W2b's)
#   bash mp1_s1_pipeline.sh <NS> <tools> dump   <variant...> [--submit]   # one s5c_array job, shared
#   bash mp1_s1_pipeline.sh <NS> <tools> unfold <variant...> [--submit]   # one s5c_array job, shared
# A merged file, dump or unfold product that exists is never redone; a submitted dump/unfold batch is recorded in
# <NS>/submitted.tsv (jobid_task, label, limit_h, billing).
set -o pipefail   # NOT set -u (conda activation)
NS="${1:?ns}"; TOOLS="${2:?tools}"; STAGE="${3:?stage}"; shift 3
MP1="${TOOLS}/measurement-paper/phase1/mp1"
W2=/pscratch/sd/j/josephrb/w2-recoil-20261006
D_DUMP="${W2}/deploy/c1cba7bf"; D_UNF="${W2}/deploy/4e4b4f56"; D_EVAL="${W2}/deploy/e9372b75"
PLS="1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P"
PYU=/global/homes/j/josephrb/.conda/envs/omnifold_py310/bin/python
(cd "${TOOLS}" && sha256sum --quiet -c TOOLS.sha256) || { echo "[s1p] ABORT: tool digests"; exit 2; }
deploy_ok () { [[ "$(git -C "$1" rev-parse HEAD)" == "$2" && -z "$(git -C "$1" status --porcelain --untracked-files=no)" ]]; }
DO=""; ARGS=()
for x in "$@"; do [[ "$x" == --submit ]] && DO=--submit || ARGS+=("$x"); done
mkdir -p "${NS}/logs" "${NS}/merged" "${NS}/lateral" "${NS}/unf" "${NS}/tables" "${NS}/checks/g1"
case "${STAGE}" in
status)
  for v in zero proton_m1 proton_p1 meson_m1 meson_p1 em_m1 em_p1 other_m1 other_p1 xtalk_m1 xtalk_p1; do
    n=0; for pl in ${PLS}; do [[ -s "${NS}/evloop/${v}/runEventLoopOmniFold_5D_${pl}_${v}.root" ]] && n=$((n+1)); done
    m=$([[ -s "${NS}/merged/runEventLoopOmniFold_5D_MEFHC_${v}.root" ]] && echo M || echo -)
    d=$([[ -s "${NS}/lateral/lat_${v}.npz" ]] && echo D || echo -)
    u=$([[ -s "${NS}/unf/mp1s1_${v}_b-_j-.npz" ]] && echo U || echo -)
    echo "${v} evloop ${n}/12 ${m}${d}${u}"
  done ;;
g1)
  for pl in "${ARGS[@]}"; do
    o="${NS}/checks/g1/g1_zero_${pl}_vs_w2b_rrzero.json"; [[ -e "$o" ]] && { echo "[s1p] g1 ${pl}: exists"; continue; }
    "${PYU}" -I "${MP1}/omnifile_io.py" --out "$o" equal "${W2}/w2b/evloop/rrzero/runEventLoopOmniFold_5D_${pl}_w2b_rrzero.root" \
      "${NS}/evloop/zero/runEventLoopOmniFold_5D_${pl}_zero.root" > "${o%.json}.log" 2>&1
    echo "[s1p] g1 ${pl}: rc=$? $(grep -m1 -o '"verdict": "[A-Z_]*"' "$o")"
  done ;;
merge)
  deploy_ok "${D_EVAL}" e9372b757250e9607f52e471d9b0c447b08e65d5 || { echo "[s1p] ABORT: evaluate deploy"; exit 2; }
  source "${D_EVAL}/setup_salloc_env.sh" >/dev/null 2>&1
  for v in "${ARGS[@]}"; do
    out="${NS}/merged/runEventLoopOmniFold_5D_MEFHC_${v}.root"
    [[ -e "${out}" ]] && { echo "[s1p] ${out} exists; skip"; continue; }
    ins=(); for pl in ${PLS}; do f="${NS}/evloop/${v}/runEventLoopOmniFold_5D_${pl}_${v}.root"; [[ -s "$f" ]] && ins+=("$f"); done
    [[ ${#ins[@]} -eq 12 ]] || { echo "[s1p] skip merge ${v}: ${#ins[@]}/12 playlists"; continue; }
    python3 "${D_EVAL}/2d-unfolding/uq/hadd_universes_full.py" "${out}.partial" "${ins[@]}" > "${NS}/logs/merge_${v}.log" 2>&1 \
      && mv "${out}.partial" "${out}" && echo "[s1p] merged ${v} $(stat -c %s "${out}") B" \
      || { echo "[s1p] merge ${v} FAILED (see ${NS}/logs/merge_${v}.log)"; rm -f "${out}.partial"; }
  done ;;
dump|unfold)
  if [[ "${STAGE}" == dump ]]; then D="${D_DUMP}"; PIN=c1cba7bfb214a82abde5580c72c9ef3c4704e73f; CPU=16; MEM=110G; BILL=62
  else D="${D_UNF}"; PIN=4e4b4f56bb0c4715dcf567829ac0449bfac745de; CPU=32; MEM=56G; BILL=32; fi
  deploy_ok "${D}" "${PIN}" || { echo "[s1p] ABORT: deploy ${D}"; exit 2; }
  VS=()
  for v in "${ARGS[@]}"; do
    if [[ "${STAGE}" == dump ]]; then [[ -e "${NS}/lateral/lat_${v}.npz" ]] && continue
    else [[ -e "${NS}/unf/mp1s1_${v}_b-_j-.npz" ]] && continue; fi
    awk -F'\t' -v l="mp1s1_${STAGE}_${v}" '$2==l{f=1} END{exit !f}' "${NS}/submitted.tsv" && { echo "[s1p] ${STAGE} ${v} already submitted"; continue; }
    VS+=("$v")
  done
  [[ ${#VS[@]} -eq 0 ]] && { echo "[s1p] nothing to ${STAGE}"; exit 0; }
  TABLE="${NS}/tables/${STAGE}-$(date -u +%Y%m%dT%H%M%S).tsv"
  /usr/bin/python3 "${MP1}/mp1_s1_tables.py" --ns "${NS}" --stage "${STAGE}" --variants "$(IFS=,; echo "${VS[*]}")" --out "${TABLE}" || exit 3
  cmd=(sbatch --parsable --no-requeue --account=m3246 --qos=shared -C cpu --time=60 --array=0-$((${#VS[@]}-1))
       --cpus-per-task="${CPU}" --mem="${MEM}" --job-name="mp1s1_${STAGE}" --output="${NS}/logs/%x-%A_%a.out"
       "${D}/nd-unfolding/s5c_array.sh" "${D}" "${PIN}" "${TABLE}" "${NS}/${STAGE}-run")
  if [[ "${DO}" == --submit ]]; then
    jid=$("${cmd[@]}") || { echo "[s1p] sbatch failed"; exit 4; }
    for i in "${!VS[@]}"; do printf '%s\t%s\t1.0\t%s\n' "${jid}_${i}" "mp1s1_${STAGE}_${VS[$i]}" "${BILL}" >> "${NS}/submitted.tsv"; done
    echo "[s1p] ${STAGE} ${VS[*]} -> ${jid}"
  else echo "${cmd[*]}"; fi ;;
*) echo "unknown stage ${STAGE}"; exit 2 ;;
esac
