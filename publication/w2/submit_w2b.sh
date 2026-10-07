#!/bin/bash
# W2b driver (publication packet W2; Joseph 2026-10-06 item 4; W2a review C1-C3). Perlmutter login node.
#   bash submit_w2b.sh <stage> [--submit]
# Stages, in order:
#   deploys   clean clones of the three frozen deploys (dump c1cba7bf, unfold 4e4b4f56, evaluate e9372b75)
#   evloop    36 event-loop jobs (rr0, rr1, rrzero x 12 playlists), per-playlist --time (C1)
#   merge     login node: hadd_universes_full.py in the 1A..1P order of run_p4_merge_audit_std.sh
#   dump      s5p_input_dumps.py lateral, 3-task array through the dump deploy's s5c_array.sh
#   unfold    s5p_numerics.py R/5/data, 3-task array through the unfold deploy's s5c_array.sh
#   evaluate  login node: design copies (C3 key-diff must PASS), frozen s5p_joint.py evaluate x3, then decide
#   sync      append terminal jobs to the ledger (also run before every billable stage)
# Without --submit a billable stage prints its commands and runs only the budget check. Every billable
# stage first syncs the ledger and refuses unless spend + in-flight + new reservations <= 8.0 (C1).
set -o pipefail   # NOT set -u (conda activation)
STAGE="${1:?stage}"; DO="${2:-}"
NS=/pscratch/sd/j/josephrb/w2-recoil-20261006
REPO="${NS}/repo"; W2="${REPO}/publication/w2"
# The working ledger lives in the namespace (seeded from the committed W2a ledger) so the clone stays clean;
# it is copied back into the repository and committed after each stage.
LEDGER="${NS}/w2b/LEDGER-w2.tsv"; SUBMITTED="${NS}/w2b/submitted.tsv"
BIN="${NS}/build/bld_mod/runEventLoopOmniFold"
S5P=/pscratch/sd/j/josephrb/s5p-20260926
D_DUMP="${NS}/deploy/c1cba7bf"; D_UNF="${NS}/deploy/4e4b4f56"; D_EVAL="${NS}/deploy/e9372b75"
PY=/usr/bin/python3.11
mkdir -p "${NS}/w2b/logs" "${NS}/w2b/tables"
[[ -z "$(git -C "${REPO}" status --porcelain --untracked-files=no)" ]] || { echo "[w2b] ABORT: ${REPO} has modified tracked files"; exit 2; }

[[ -e "${LEDGER}" ]] || cp "${W2}/LEDGER-w2.tsv" "${LEDGER}"
budget () {   # $1 = stage, $2 = comma-separated labels about to be submitted
  ${PY} "${W2}/w2b.py" ledger-sync --ledger "${LEDGER}" --submitted "${SUBMITTED}" || return 2
  ${PY} "${W2}/w2b.py" check-budget --stage "$1" --labels "$2" --ledger "${LEDGER}" --submitted "${SUBMITTED}"
}
in_flight_or_done () {   # $1 = label: submitted and (not yet terminal, or terminal COMPLETED)
  local jid; jid=$(awk -F'\t' -v l="$1" '$2==l{j=$1} END{print j}' "${SUBMITTED}" 2>/dev/null)
  [[ -z "${jid}" ]] && return 1
  local st; st=$(awk -F'\t' -v j="${jid}" '$2==j{print $4}' "${LEDGER}")
  [[ -z "${st}" || "${st}" == COMPLETED ]]
}
record () { printf '%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$4" >> "${SUBMITTED}"; }   # jobid label limit_h billing
deploy_ok () { [[ "$(git -C "$1" rev-parse HEAD)" == "$2" && -z "$(git -C "$1" status --porcelain --untracked-files=no)" ]]; }

case "${STAGE}" in
deploys)
  for pair in "c1cba7bf:c1cba7bfb214a82abde5580c72c9ef3c4704e73f" "4e4b4f56:4e4b4f56bb0c4715dcf567829ac0449bfac745de" \
              "e9372b75:e9372b757250e9607f52e471d9b0c447b08e65d5"; do
    d="${NS}/deploy/${pair%%:*}"; sha="${pair#*:}"
    if [[ ! -e "${d}" ]]; then git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "${d}" && git -C "${d}" checkout -q "${sha}"; fi
    deploy_ok "${d}" "${sha}" && echo "[w2b] deploy ${d} OK at ${sha}" || { echo "[w2b] ABORT: ${d} not clean at ${sha}"; exit 2; }
  done ;;
evloop)
  [[ "$(md5sum "${BIN}" | cut -d' ' -f1)" == f3e9c97b82456d3fc7e898ea1d0579ee ]] || { echo "[w2b] ABORT: binary md5"; exit 7; }
  ${PY} "${W2}/w2b.py" ledger-sync --ledger "${LEDGER}" --submitted "${SUBMITTED}" || exit 2
  TODO=()   # a task whose output exists or that is in flight/completed is not resubmitted; a failed one is (a retry)
  while IFS=$'\t' read -r label limit billing; do
    v=$(echo "${label}" | cut -d_ -f3); pl=$(echo "${label}" | cut -d_ -f4)
    [[ -e "${NS}/w2b/evloop/${v}/runEventLoopOmniFold_5D_${pl}_w2b_${v}.root" ]] && continue
    in_flight_or_done "${label}" && continue
    TODO+=("${label}:${limit}:${billing}")
  done < <(${PY} "${W2}/w2b.py" plan | awk -F'\t' '/^   w2b_ev_/{sub(/^   /,"",$1); sub(/ h$/,"",$2); sub(/^billing /,"",$3); print $1"\t"$2"\t"$3}')
  [[ ${#TODO[@]} -eq 0 ]] && { echo "[w2b] nothing to submit"; exit 0; }
  labels=$(printf '%s\n' "${TODO[@]}" | cut -d: -f1 | paste -sd, -)
  budget evloop "${labels}" || { echo "[w2b] REFUSED by the budget check"; exit 3; }
  for t in "${TODO[@]}"; do
    label=${t%%:*}; rest=${t#*:}; limit=${rest%%:*}; billing=${rest#*:}
    v=$(echo "${label}" | cut -d_ -f3); pl=$(echo "${label}" | cut -d_ -f4)
    cmd=(sbatch --parsable --time="$(printf '%d:00:00' "${limit%.*}")" --job-name="${label}"
         --output="${NS}/w2b/logs/%x_%j.out" "${W2}/sbatch_w2b_evloop.sh" "${NS}" "${v}" "${BIN}" "${pl}")
    if [[ "${DO}" == "--submit" ]]; then
      W2B_ENV_CHECK_ONLY=1 bash "${W2}/sbatch_w2b_evloop.sh" "${NS}" "${v}" "${BIN}" "${pl}" >/dev/null || exit 6   # C2, submitting env
      jid=$("${cmd[@]}") || { echo "[w2b] sbatch failed for ${label}"; exit 4; }
      record "${jid}" "${label}" "${limit}" "${billing}"; echo "[w2b] ${label} -> ${jid}"
    else
      echo "${cmd[*]}"
    fi
  done ;;
merge)
  source "${D_EVAL}/setup_salloc_env.sh" >/dev/null 2>&1
  mkdir -p "${NS}/w2b/merged"
  for v in rr0 rr1 rrzero; do
    out="${NS}/w2b/merged/runEventLoopOmniFold_5D_MEFHC_w2b_${v}.root"
    [[ -e "${out}" ]] && { echo "[w2b] ${out} exists; skip"; continue; }
    ins=(); for pl in 1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P; do
      f="${NS}/w2b/evloop/${v}/runEventLoopOmniFold_5D_${pl}_w2b_${v}.root"; [[ -s "${f}" ]] && ins+=("${f}"); done
    [[ ${#ins[@]} -eq 12 ]] || { echo "[w2b] ABORT merge ${v}: ${#ins[@]}/12 playlists"; exit 3; }
    python3 "${D_EVAL}/2d-unfolding/uq/hadd_universes_full.py" "${out}.partial" "${ins[@]}" > "${NS}/w2b/logs/merge_${v}.log" 2>&1 \
      && mv "${out}.partial" "${out}" && echo "[w2b] merged ${v}" || { echo "[w2b] merge ${v} FAILED"; rm -f "${out}.partial"; exit 5; }
  done ;;
dump|unfold)
  if [[ "${STAGE}" == dump ]]; then D="${D_DUMP}"; PIN=c1cba7bfb214a82abde5580c72c9ef3c4704e73f; CPU=16; MEM=110G; BILL=62; mkdir -p "${NS}/w2b/lateral"
    ${PY} "${W2}/w2b.py" tables --ns "${NS}" --outdir "${NS}/w2b/tables" || exit 2; TABLE="${NS}/w2b/tables/w2b-dump-tasks.tsv"
  else D="${D_UNF}"; PIN=4e4b4f56bb0c4715dcf567829ac0449bfac745de; CPU=32; MEM=56G; BILL=32; mkdir -p "${NS}/w2b/unf"
    ${PY} "${W2}/w2b.py" tables --ns "${NS}" --outdir "${NS}/w2b/tables" --with-unfold || exit 2; TABLE="${NS}/w2b/tables/w2b-unfold-tasks.tsv"; fi
  deploy_ok "${D}" "${PIN}" || { echo "[w2b] ABORT: deploy ${D}"; exit 2; }
  grep -q -P "\tw2b_${STAGE}_" "${SUBMITTED}" 2>/dev/null && { echo "[w2b] ABORT: ${STAGE} already submitted (a retry is a deliberate, recorded act)"; exit 3; }
  budget "${STAGE}" "w2b_${STAGE}_rr0,w2b_${STAGE}_rr1,w2b_${STAGE}_rrzero" || { echo "[w2b] REFUSED by the budget check"; exit 3; }
  cmd=(sbatch --parsable --no-requeue --account=m3246 --qos=shared -C cpu --time=60 --array=0-2
       --cpus-per-task="${CPU}" --mem="${MEM}" --job-name="w2b_${STAGE}" --output="${NS}/w2b/logs/%x-%A_%a.out"
       "${D}/nd-unfolding/s5c_array.sh" "${D}" "${PIN}" "${TABLE}" "${NS}/w2b/${STAGE}-run")
  if [[ "${DO}" == "--submit" ]]; then
    jid=$("${cmd[@]}") || { echo "[w2b] sbatch failed"; exit 4; }
    for i in 0 1 2; do v=$(echo rr0 rr1 rrzero | cut -d' ' -f$((i+1))); record "${jid}_${i}" "w2b_${STAGE}_${v}" 1.0 "${BILL}"; done
    echo "[w2b] ${STAGE} -> ${jid}"
  else echo "${cmd[*]}"; fi ;;
evaluate)
  deploy_ok "${D_EVAL}" e9372b757250e9607f52e471d9b0c447b08e65d5 || { echo "[w2b] ABORT: evaluate deploy"; exit 2; }
  FROZEN_EVAL="${REPO}/docs/orchestration/state/s5p/stage7/joint/joint-evaluate.json"   # committed byte-identical copy
  [[ "$(sha256sum "${FROZEN_EVAL}" | cut -d' ' -f1)" == b9604502b1aa263508ba46f0be91846d7a2106f6f2fd0ba5c172b87ee256dd11 ]] || { echo "[w2b] ABORT: joint-evaluate digest"; exit 2; }
  [[ "$(sha256sum "${D_EVAL}/docs/orchestration/state/s5p/prod/design.json" | cut -d' ' -f1)" == 404446eb2a770dc4412012c5e182e57a77afa2edd332c75de399a9281f536285 ]] || { echo "[w2b] ABORT: frozen design digest"; exit 2; }
  DC="${NS}/w2b/design"; mkdir -p "${DC}" "${NS}/w2b/eval"
  ${PY} "${W2}/w2b.py" design-copies --frozen "${D_EVAL}/docs/orchestration/state/s5p/prod/design.json" --ns "${NS}" --outdir "${DC}" > "${DC}/keydiff.log" \
    || { echo "[w2b] ABORT: design key-diff FAILED (see ${DC}/design-keydiff.json)"; exit 3; }
  cd "${D_EVAL}" && source ./setup_salloc_env.sh >/dev/null 2>&1
  export PYTHONDONTWRITEBYTECODE=1
  DEC=(--deploy "${D_EVAL}" --frozen-design "${D_EVAL}/docs/orchestration/state/s5p/prod/design.json"
       --frozen-evaluate "${FROZEN_EVAL}" --evaldir "${NS}/w2b/eval" --zero-product "${NS}/w2b/unf/w2b_rrzero_b-_j-.npz")
  run_copy () {   # frozen evaluate + frozen labels (as stage7) + manifest, for one design copy
    local v="$1" C="${NS}/w2b/eval/$1"
    [[ -s "${NS}/w2b/unf/w2b_${v}_b-_j-.npz" ]] || { echo "[w2b] ABORT: no unfold product for ${v}"; return 3; }
    mkdir -p "${C}"
    PYTHONPATH=nd-unfolding python3 nd-unfolding/s5p_joint.py evaluate --design "${DC}/design-w2b-${v}.json" \
      --v "${S5P}/stage3/V/V-s3v.npz" --out "${C}/joint-evaluate.json" > "${C}/joint-evaluate.stdout" 2>&1 \
      || { echo "[w2b] evaluate ${v} FAILED"; return 5; }
    PYTHONPATH=nd-unfolding python3 nd-unfolding/s5p_robust_labels.py --evaluate "${C}/joint-evaluate.json" \
      --design "${DC}/design-w2b-${v}.json" --out "${C}/robust-labels.json" > "${C}/robust-labels.stdout" 2>&1 \
      || { echo "[w2b] labels ${v} FAILED"; return 5; }
    python3 "${W2}/w2b.py" manifest --variant "${v}" --design-copy "${DC}/design-w2b-${v}.json" --copydir "${C}" \
      --deploy-sha e9372b757250e9607f52e471d9b0c447b08e65d5 > /dev/null || return 5
  }
  run_copy rrzero || exit $?
  python3 "${W2}/w2b.py" decide "${DEC[@]}" --control-only --out "${NS}/w2b/eval/w2b-control.json" > /dev/null
  rc=$?; echo "[w2b] delta=0 control rc=${rc} ($(python3 -c "import json;print(json.load(open('${NS}/w2b/eval/w2b-control.json'))['verdict'])"))"
  [[ ${rc} -eq 0 ]] || { echo "[w2b] STOP: the delta = 0 control did not PASS; the signs are not evaluated"; exit 1; }
  run_copy rr0 || exit $?
  run_copy rr1 || exit $?
  python3 "${W2}/w2b.py" decide "${DEC[@]}" --out "${NS}/w2b/eval/w2b-decision.json" > /dev/null; echo "[w2b] decide rc=$?" ;;
sync) ${PY} "${W2}/w2b.py" ledger-sync --ledger "${LEDGER}" --submitted "${SUBMITTED}" ;;
*) echo "unknown stage ${STAGE}"; exit 2 ;;
esac
