#!/bin/bash
#SBATCH --account=m3246
#SBATCH --constraint=cpu
#SBATCH --qos=regular
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
# RDX stage 3 (RDX-DECLARATION.md rev 3 §4): every task of one job (rdx_tasks.tsv column 2) at once, one srun step
# each, through mnv_guarded_run.py and rdx_unfold.py from a clean deploy at <pin>, as RSN's sbatch_rsn.sh runs its jobs.
#   sbatch --job-name=rdx_s3_<a|b> --time=0:22:00 --output=<B>/out/logs/%x_%j.out sbatch_rdx_arms.sh <deploy> <pin> <B> <S3a|S3b>
# Refuses before any step unless: the deploy is clean at <pin>; the job's name is rdx_s3_a or rdx_s3_b and its Slurm
# TimeLimit is at most 0:22:00; no fenced job is queued or running; <B>/out/gates/<job>.ok names <pin>; the stage-2
# checks recorded PASS (<B>/out/checks/k1.json, truthx_npz.json); RDX's npz, background dump and sidecar match the
# deploy's committed nd-unfolding/rdx/rdx-inputs-SHA256SUMS; the staged copies of MP-1's lat_zero files match their pins; the frozen tune_v1
# reweight matches pv-ladder's prep-SHA256SUMS; and no product exists. With RDX_SMOKE set it stops after the checks.
set -o pipefail   # NOT set -u (the environment's activation aborts under it)
D="${1:?deploy}"; PIN="${2:?pin}"; B="${3:?B}"; JOB="${4:?job}"
OUT="${B}/out"
PVL_PREP="${RDX_PVL_PREP:-/pscratch/sd/j/josephrb/pv-ladder-20261024/prep}"
H="${D}/nd-unfolding/rdx"
say() { echo "[rdx-arms] $*" >&2; }
head_sha=$(git -C "${D}" rev-parse HEAD 2>/dev/null)
dirty=$(git -C "${D}" status --porcelain --untracked-files=all -- . 2>/dev/null | wc -l)
[[ "${head_sha}" == "${PIN}" && "${dirty}" -eq 0 ]] || { say "refusing: deploy HEAD=${head_sha} (pinned ${PIN}), ${dirty} porcelain lines"; exit 2; }
case "${JOB}" in S3a) WANT=rdx_s3_a ;; S3b) WANT=rdx_s3_b ;; *) say "refusing: job ${JOB}"; exit 2 ;; esac
LIMIT=0:22:00
if [[ -n "${SLURM_JOB_ID}" ]]; then
  NAME="${SLURM_JOB_NAME}"; TL=$(squeue -h -j "${SLURM_JOB_ID}" -o %l 2>/dev/null)
elif [[ -n "${RDX_SMOKE}" ]]; then
  NAME="${RDX_NAME:-${WANT}}"; TL="${RDX_TIMELIMIT:-${LIMIT}}"
else
  say "refusing: not inside a Slurm job"; exit 2
fi
[[ "${NAME}" == "${WANT}" ]] || { say "refusing: job name ${NAME} is not ${WANT}"; exit 2; }
python3 - "${TL}" "${LIMIT}" <<'EOF'
import sys
def sec(t):
    d, dash, rest = t.partition("-")
    f = rest.split(":") if dash else t.split(":")
    if (dash and not d.isdigit()) or not all(x.isdigit() for x in f) or not 1 <= len(f) <= 3:
        raise ValueError(t)
    f = [int(x) for x in f]
    if dash:
        h, m, s = f + [0] * (3 - len(f))
        return int(d) * 86400 + h * 3600 + m * 60 + s
    return {1: lambda: f[0] * 60, 2: lambda: f[0] * 60 + f[1], 3: lambda: f[0] * 3600 + f[1] * 60 + f[2]}[len(f)]()
try:
    sys.exit(0 if sec(sys.argv[1]) <= sec(sys.argv[2]) else 4)
except ValueError:
    sys.exit(3)
EOF
trc=$?
[[ ${trc} -eq 0 ]] || { say "refusing: Slurm TimeLimit '${TL}' is not within ${LIMIT} (rc ${trc})"; exit 2; }
sq=$(squeue -h -u "${USER:-josephrb}" -o '%j|%T' 2>/dev/null) || { say "refusing: squeue failed"; exit 2; }
hit=$(printf '%s\n' "${sq}" | awk -F'|' '$1 ~ /^(cov2d|t2a|ll5d|e96data|rpd_|rsn_)/')
[[ -z "${hit}" ]] || { say "refusing: fenced jobs are queued or running: ${hit}"; exit 2; }
G="${OUT}/gates/${JOB}.ok"
[[ -f "${G}" ]] && grep -qx "pin=${PIN}" "${G}" || { say "refusing: ${G} is missing or does not name pin ${PIN}"; exit 2; }
for c in k1 truthx_npz; do
  grep -q '"verdict": "PASS"' "${OUT}/checks/${c}.json" 2>/dev/null || { say "refusing: ${OUT}/checks/${c}.json records no PASS"; exit 2; }
done
SUMS="${H}/rdx-inputs-SHA256SUMS"
[[ -s "${SUMS}" ]] || { say "refusing: no committed ${SUMS}"; exit 2; }
sum_of() { awk -v f="./$1" '$2 == f {print $1}' "${SUMS}"; }
# inputs as P_<key> (path) and S_<key> (sha256); read with ${!var} (bash 3.2 has no associative arrays)
P_rdx_npz="${OUT}/dumps/lat_RDX_ALL.npz"; S_rdx_npz=$(sum_of lat_RDX_ALL.npz)
P_rdx_bkg="${OUT}/dumps/lat_RDX_ALL_bkg.npz"; S_rdx_bkg=$(sum_of lat_RDX_ALL_bkg.npz)
P_sidecar="${OUT}/dumps/truthx_RDX_ALL.npz"; S_sidecar=$(sum_of truthx_RDX_ALL.npz)
MP1="${RDX_MP1_LATERAL:-${OUT}/stage}"   # the connect's O_NOATIME copies of MP-1's lat_zero files (step m), never the originals
P_lat_npz="${MP1}/lat_zero.npz"; P_lat_bkg="${MP1}/lat_zero_bkg.npz"
read -r S_lat_npz S_lat_bkg < <(python3 -B -c "import sys; sys.path.insert(0, sys.argv[1]); import fd_ct_period_inputs as C; print(C.MP1_ZERO['lat_npz'], C.MP1_ZERO['lat_bkg'])" "${D}/nd-unfolding" 2>/dev/null)
[[ "${S_lat_npz}" =~ ^[0-9a-f]{64}$ && "${S_lat_bkg}" =~ ^[0-9a-f]{64}$ ]] || { say "refusing: could not read MP-1's lat_zero pins"; exit 2; }
P_ratio="${PVL_PREP}/ratios/L-5D-PV/tune_v1.json"
S_ratio=$(awk '$2 == "./ratios/L-5D-PV/tune_v1.json" {print $1}' "${D}/nd-unfolding/pv-ladder/prep-SHA256SUMS")
for k in rdx_npz rdx_bkg sidecar lat_npz lat_bkg ratio; do
  pv="P_${k}"; sv="S_${k}"
  [[ -n "${!sv}" && -f "${!pv}" && "$(sha256sum "${!pv}" | cut -d' ' -f1)" == "${!sv}" ]] \
    || { say "refusing: ${k} (${!pv}) is missing or not at its pinned sha256"; exit 2; }
done
LINES=()
while IFS= read -r ln; do LINES+=("$ln"); done < <(grep -v '^#' "${H}/rdx_tasks.tsv" | awk -F'\t' -v j="${JOB}" '$2 == j')
[[ ${#LINES[@]} -gt 0 ]] || { say "refusing: no tasks for ${JOB}"; exit 2; }
for line in "${LINES[@]}"; do
  IFS=$'\t' read -r task _ _ _ _ _ _ _ _ _ <<< "${line}"
  [[ ! -e "${OUT}/products/${task}.npz" ]] || { say "refusing: ${OUT}/products/${task}.npz exists"; exit 2; }
done
if [[ -z "${RDX_SMOKE}" ]]; then
  mkdir -p "${OUT}/logs" "${OUT}/inventory" "${OUT}/products"
  source "${D}/setup_salloc_env.sh" > "${OUT}/logs/env-${SLURM_JOB_ID}.log" 2>&1
  case "$(python -V 2>&1)" in *3.11*) ;; *) say "refusing: environment did not activate ($(python -V 2>&1))"; exit 2 ;; esac
  export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
  export TMPDIR="${OUT}/tmp"; mkdir -p "${TMPDIR}"
  JOBMEM=${SLURM_MEM_PER_NODE:-$(scontrol show job "${SLURM_JOB_ID}" | grep -o 'AllocTRES=[^ ]*' \
          | sed -n 's/.*mem=\([0-9]*\)\([MG]\).*/\1 \2/p' | awk '{print ($2 == "G") ? $1 * 1024 : $1}')}
  [[ -n "${JOBMEM}" && "${JOBMEM}" -gt 0 ]] || { say "refusing: cannot read the job's memory allocation"; exit 2; }
  MEM=$(( JOBMEM * 95 / 100 / ${#LINES[@]} ))
  CPS=$(( ${SLURM_CPUS_ON_NODE:-$(nproc)} / ${#LINES[@]} )); [[ ${CPS} -gt 42 ]] && CPS=42
  [[ ${CPS} -ge 32 ]] || { say "refusing: ${CPS} CPUs per step is below LightGBM's 32 threads"; exit 2; }
  echo "[rdx-arms] job=${JOB} slurm=${SLURM_JOB_ID} node=$(hostname) tasks=${#LINES[@]} mem_per_step=${MEM}M cpus_per_step=${CPS} start=$(date -u +%FT%TZ)"
fi
pids=(); names=()
for line in "${LINES[@]}"; do
  IFS=$'\t' read -r task _ features permute weight truth transfer closure inputs _ <<< "${line}"
  if [[ "${inputs}" == lat_zero ]]; then NPZ=lat_npz; BKG=lat_bkg; else NPZ=rdx_npz; BKG=rdx_bkg; fi
  pn="P_${NPZ}"; sn="S_${NPZ}"; pb="P_${BKG}"; sb="S_${BKG}"
  extra=(--regressor-features "${features}" --regressor-weight "${weight}" --truth "${truth}")
  [[ "${features}" == wide ]] && extra+=(--truthx-sidecar "${P_sidecar}" --expect-truthx-sha256 "${S_sidecar}")
  [[ "${permute}" != "-" ]] && extra+=(--truthx-permute "${permute}")
  [[ "${transfer}" == yes ]] && extra+=(--transfer)
  [[ "${closure}" == yes ]] && extra+=(--closure)
  cmd=(python "${D}/nd-unfolding/mnv_guarded_run.py" --expect-root "${D}" --inventory "${OUT}/inventory/${task}.jsonl"
       --label "rdx:${task}" -- "${H}/rdx_unfold.py" "${extra[@]}"
       --rung L-5D-PV --arm e --features all --ratio "${P_ratio}" --expect-ratio-sha256 "${S_ratio}"
       --npz "${!pn}" --expect-npz-sha256 "${!sn}" --bkg "${!pb}" --expect-bkg-sha256 "${!sb}"
       --estimator-seed 42 --threads 32 --iters 5 --out "${OUT}/products/${task}.npz")
  if [[ -n "${RDX_SMOKE}" ]]; then printf '%s\n' "STEP ${task} ${cmd[*]}"; continue; fi
  srun -n1 -c "${CPS}" --mem="${MEM}M" --exact --cpu-bind=cores "${cmd[@]}" > "${OUT}/logs/${task}.log" 2>&1 &
  pids+=("$!"); names+=("${task}")
done
[[ -n "${RDX_SMOKE}" ]] && { echo "[rdx-arms] smoke: checks passed, ${#LINES[@]} steps"; exit 0; }
rc=0
for i in "${!pids[@]}"; do
  if wait "${pids[$i]}"; then sha256sum "${OUT}/products/${names[$i]}.npz"; else say "task ${names[$i]} failed; see ${OUT}/logs/${names[$i]}.log"; rc=1; fi
done
echo "[rdx-arms] job=${JOB} rc=${rc} end=$(date -u +%FT%TZ)"
exit ${rc}
