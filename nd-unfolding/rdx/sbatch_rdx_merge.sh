#!/bin/bash
#SBATCH --account=m3246
#SBATCH --constraint=cpu
#SBATCH --qos=regular
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
# RDX stage 2's merge and dump (RDX-DECLARATION.md §3), on one exclusive node, serially, as FD-CT-5B's ALL lane ran:
#   1 rdx_merge.py merge: the twelve RDX loops at the sha256s the stage-2 checks wrote (<B>/out/loops.sha256), through
#     hadd_universes_full.py, with the POT check against 5B's pinned ALL flux file;
#   2 nn_dump_inputs.py --axes eavail,q3,W on the merge (the lateral dump's --cv-npz, as 5B ran; of_inputs_5d.npz is
#     never read);
#   3 rdx_dump.py: s5p_input_dumps.py lateral, unchanged, then the truthx sidecar;
#   4 rdx_merge.py k1 (C-ALIGN-ALL) against the connect's O_NOATIME copies of lat_zero.npz and lat_zero_bkg.npz.
# C-TRUTHX-NPZ runs after, on a login node. Any failing step stops the job.
#   sbatch --job-name=rdx_s2_merge --time=<limit> --output=<B>/out/logs/%x_%j.out sbatch_rdx_merge.sh <deploy> <pin> <B> <limit>
# Refuses before any step unless: the deploy is clean at <pin>; the job's name is rdx_s2_merge and its TimeLimit is at
# most <limit>, which must equal the limit in <B>/out/gates/merge.ok (set from the z3 timing probe); no fenced job is
# queued or running; the gate names <pin>; loops.sha256 exists; the staged lat_zero copies exist; no output exists.
set -o pipefail
D="${1:?deploy}"; PIN="${2:?pin}"; B="${3:?B}"; LIMIT="${4:?limit}"
OUT="${B}/out"; H="${D}/nd-unfolding/rdx"
say() { echo "[rdx-merge] $*" >&2; }
head_sha=$(git -C "${D}" rev-parse HEAD 2>/dev/null)
dirty=$(git -C "${D}" status --porcelain --untracked-files=all -- . 2>/dev/null | wc -l)
[[ "${head_sha}" == "${PIN}" && "${dirty}" -eq 0 ]] || { say "refusing: deploy HEAD=${head_sha} (pinned ${PIN}), ${dirty} porcelain lines"; exit 2; }
G="${OUT}/gates/merge.ok"
[[ -f "${G}" ]] && grep -qx "pin=${PIN}" "${G}" && grep -qx "limit=${LIMIT}" "${G}" \
  || { say "refusing: ${G} is missing or does not name pin ${PIN} and limit ${LIMIT}"; exit 2; }
if [[ -n "${SLURM_JOB_ID}" ]]; then
  NAME="${SLURM_JOB_NAME}"; TL=$(squeue -h -j "${SLURM_JOB_ID}" -o %l 2>/dev/null)
elif [[ -n "${RDX_SMOKE}" ]]; then
  NAME="${RDX_NAME:-rdx_s2_merge}"; TL="${RDX_TIMELIMIT:-${LIMIT}}"
else
  say "refusing: not inside a Slurm job"; exit 2
fi
[[ "${NAME}" == rdx_s2_merge ]] || { say "refusing: job name ${NAME} is not rdx_s2_merge"; exit 2; }
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
[[ -s "${OUT}/loops.sha256" ]] || { say "refusing: no ${OUT}/loops.sha256 (the stage-2 checks did not pass)"; exit 2; }
for f in lat_zero.npz lat_zero_bkg.npz; do
  [[ -s "${OUT}/stage/${f}" ]] || { say "refusing: no staged ${OUT}/stage/${f}"; exit 2; }
done
FLUX="${D}/docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-ct/5b/flux/runEventLoopMC_ALL.root"
MERGED="${OUT}/merged/runEventLoopOmniFold_RDX_ALL.root"
NN="${OUT}/dumps/nn_RDX_ALL.npz"; LAT="${OUT}/dumps/lat_RDX_ALL.npz"; LATB="${OUT}/dumps/lat_RDX_ALL_bkg.npz"
SIDE="${OUT}/dumps/truthx_RDX_ALL.npz"; K1="${OUT}/checks/k1.json"
for f in "${MERGED}" "${NN}" "${LAT}" "${LATB}" "${SIDE}" "${K1}"; do
  [[ ! -e "${f}" ]] || { say "refusing: ${f} exists"; exit 2; }
done
PLS=""
for pl in 1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P; do PLS="${PLS:+${PLS},}${pl}=${OUT}/evloop/runEventLoopOmniFold_RDX_${pl}.root"; done
STEPS=(
  "merge|${H}/rdx_merge.py merge --loops-dir ${OUT}/evloop --sums ${OUT}/loops.sha256 --flux ${FLUX} --out ${MERGED}"
  "nndump|${D}/nd-unfolding/nn_dump_inputs.py --omnifile ${MERGED} --mcfile ${FLUX} --axes eavail,q3,W --out ${NN}"
  "dump|${H}/rdx_dump.py --playlists ${PLS} --sidecar ${SIDE} --omnifile ${MERGED} --cv-npz ${NN} --mcfile ${FLUX} --out ${LAT} --out-bkg ${LATB}"
  "k1|${H}/rdx_merge.py k1 --lat-npz ${LAT} --lat-bkg ${LATB} --mp1-lat-npz ${OUT}/stage/lat_zero.npz --mp1-lat-bkg ${OUT}/stage/lat_zero_bkg.npz --out ${K1}"
)
if [[ -n "${RDX_SMOKE}" ]]; then
  for s in "${STEPS[@]}"; do echo "STEP ${s%%|*} python ${s#*|}"; done
  echo "[rdx-merge] smoke: checks passed, ${#STEPS[@]} steps"; exit 0
fi
mkdir -p "${OUT}/merged" "${OUT}/dumps" "${OUT}/checks" "${OUT}/logs"
source "${D}/setup_salloc_env.sh" > "${OUT}/logs/merge-env-${SLURM_JOB_ID}.log" 2>&1
case "$(python -V 2>&1)" in *3.11*) ;; *) say "refusing: environment did not activate ($(python -V 2>&1))"; exit 2 ;; esac
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 TMPDIR="${OUT}/tmp"; mkdir -p "${TMPDIR}"
echo "[rdx-merge] slurm=${SLURM_JOB_ID} node=$(hostname) start=$(date -u +%FT%TZ)"
for s in "${STEPS[@]}"; do
  label="${s%%|*}"; t0=$(date +%s)
  # shellcheck disable=SC2086
  python ${s#*|} > "${OUT}/logs/merge-${label}.log" 2>&1; rc=$?
  echo "[rdx-merge] ${label} rc=${rc} $(( $(date +%s) - t0 ))s"; tail -3 "${OUT}/logs/merge-${label}.log"
  [[ ${rc} -eq 0 ]] || { say "step ${label} failed; stopping"; exit 5; }
done
sha256sum "${MERGED}" "${NN}" "${LAT}" "${LATB}" "${SIDE}"
echo "[rdx-merge] rc=0 end=$(date -u +%FT%TZ)"
