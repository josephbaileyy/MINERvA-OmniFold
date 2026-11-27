#!/bin/bash
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --no-requeue
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
# geanttw C2 and P3 jobs (p2p3/AMENDMENT-P2P3.md A1, A3; cov2d's (C) grant and its amendments).
#   sbatch --job-name=NAME --time=LIMIT -c CPUS --mem=MEM geanttw_p3.sbatch MODE B DEPLOY [ARGS...]
# MODE and its job name, limit and request:
#   c2pre    geanttw_p2_c2pre     00:30:00   2 CPUs, 16G     c2_check.py pre: P0's pinned 1L dump vs UOMNI's 1L slice
#   c2       geanttw_p3_c2        01:00:00   2 CPUs, 16G     c2_check.py full: the 12 patched dumps vs UOMNI
#   slim     geanttw_p3_slim      01:00:00   2 CPUs, 16G     p3_slim.py select, build x3, slim_tparams.py, check,
#                                                            patchcheck
#   unf      geanttw_p3_unf_<s>_GEANT_<b>_<i>  00:30:00  128 CPUs, 243840M   Stage C's universe unfold, on a slim
#   extract  geanttw_p3_extract   00:30:00   2 CPUs, 16G     p3_readout.py extract: the 18 unfolds' cell vectors
# Every mode:
# - checks its job name and its Slurm TimeLimit (read from sacct, never squeue) against the mode's;
# - refuses while any ^(cov2d|t2a|covfix_) job is live, at start and again immediately before its work;
# - runs only the deploy's committed scripts, each checked against its blob at the deploy's HEAD.
# Every mode that reads UOMNI logs UOMNI's atime_ns and mtime_ns, with UTC, immediately before and after (cov2d's
# carried conditions), and refuses unless UOMNI's size by stat is Stage C's.
# GEANTTW_SMOKE=1 runs every check, then exits 0 before the work.
set -o pipefail
MODE="${1:?mode}"; B="${2:?B}"; DEPLOY="${3:?deploy}"; shift 3
say() { echo "[geanttw-p3] $*" >&2; }
refuse() { say "REFUSE: $*"; exit 2; }
CODE="${DEPLOY}/docs/orchestration/state/geanttw-20261124/code"
UOMNI=/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/runEventLoopOmniFold_MEFHC_universes_full.root
UOMNI_SIZE=171117087867
UPY=/global/homes/j/josephrb/.conda/envs/omnifold_py310/bin/python3
D2=/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding
SETUP=/pscratch/sd/j/josephrb/MINERvA-OmniFold/setup_salloc_env.sh
PROD_SHA=74a4ed69c3fa9c4ae5b6866f36343212b8d3f903fddde6c7bd40c382c1167d56   # Stage C's driver (sbatch_prod.sh:23)
HELPER=/pscratch/sd/j/josephrb/MINERvA-OmniFold/unbinned_unfolding/python/omnifold.py
HELPER_SHA=e96234124a31edd7a8dd61fdb16cb48a5b28cbd1b90202f59b0095868378227a
MCFILE="${D2}/baseline_flux/runEventLoopMC_MEFHC.root"
MCFILE_SHA=d40aea69235cdc98644e1bb3e622e579d6b81904c004c83fe50465079989f316
FLUXU="${D2}/baseline_flux/flux_integral_universes_MEFHC.root"
FLUXU_SHA=5eecae84509ba8ededbe8fdee63508d8e36cd057cc0547a940383f80248580eb
PLAYLISTS=(1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P)   # hadd order (sbatch_hadd_MEFHC_universes_full.sh:32-43)
if [[ -n "${GEANTTW_TEST_UOMNI:-}" ]]; then   # the tests' only door
  UOMNI="${GEANTTW_TEST_UOMNI}"; UOMNI_SIZE="${GEANTTW_TEST_UOMNI_SIZE:?}"; UPY="${GEANTTW_TEST_PY:-python3}"
  SETUP="${GEANTTW_TEST_SETUP:-${SETUP}}"
fi

# --- the mode's job name and limit ---
case "${MODE}" in
  c2pre)   WANT=geanttw_p2_c2pre; LIMIT=00:30:00; READS_UOMNI=1 ;;
  c2)      WANT=geanttw_p3_c2; LIMIT=01:00:00; READS_UOMNI=1 ;;
  slim)    WANT=geanttw_p3_slim; LIMIT=01:00:00; READS_UOMNI=1 ;;
  extract) WANT=geanttw_p3_extract; LIMIT=00:30:00; READS_UOMNI=0 ;;
  unf)     SLIM="${1:?slim pin|pinov|patov}"; UNI="${2:?universe GEANT_<b>:<i>}"
           [[ "${SLIM}" =~ ^(pin|pinov|patov)$ ]] || refuse "slim '${SLIM}' is not pin, pinov or patov"
           [[ "${UNI}" =~ ^GEANT_(Neutron|Pion|Proton):[01]$ ]] || refuse "universe '${UNI}' is not GEANT_<b>:<i>"
           WANT="geanttw_p3_unf_${SLIM}_${UNI/:/_}"; LIMIT=00:30:00; READS_UOMNI=0 ;;
  *) refuse "mode '${MODE}' is not c2pre, c2, slim, unf or extract" ;;
esac
if [[ -n "${SLURM_JOB_ID:-}" ]]; then
  NAME="${SLURM_JOB_NAME}"
  TL=$(sacct -j "${SLURM_JOB_ID}" -X -n -P -o Timelimit 2>/dev/null | head -1)
else
  [[ -n "${GEANTTW_SMOKE:-}" ]] || refuse "not inside a Slurm job"
  NAME="${GEANTTW_NAME:-}"; TL="${GEANTTW_TIMELIMIT:-}"
fi
[[ "${NAME}" == "${WANT}" ]] || refuse "job name '${NAME}' is not '${WANT}'"
[[ "${TL}" == "${LIMIT}" ]] || refuse "Slurm TimeLimit '${TL}' is not ${LIMIT}"

# --- the fence: no live cov2d, t2a or covfix_ job, from sacct ---
fence() {
  local psv since rc
  psv=$(mktemp) || refuse "mktemp failed ($1)"
  since=$(python3 -c 'import datetime; print((datetime.date.today() - datetime.timedelta(14)).isoformat())')
  sacct -X -n -P -S "${since}" -o JobID,JobName,State,ElapsedRaw,NNodes,TimelimitRaw > "${psv}" 2>&1 \
    || { rm -f "${psv}"; refuse "sacct failed ($1)"; }
  python3 -I "${CODE}/geanttw_sacct.py" fence --sacct "${psv}" --regex '^(cov2d|t2a|covfix_)' >&2; rc=$?
  rm -f "${psv}"
  [[ ${rc} -eq 0 ]] || refuse "fenced jobs are live, or sacct is unreadable ($1, rc ${rc})"
}
fence "at start"

# --- the deploy's scripts are its committed blobs ---
for f in c2_check.py p3_slim.py slim_tparams.py p3_readout.py geanttw_sacct.py; do
  [[ "$(sha256sum "${CODE}/${f}" | cut -d' ' -f1)" == "$(git -C "${DEPLOY}" show "HEAD:docs/orchestration/state/geanttw-20261124/code/${f}" | sha256sum | cut -d' ' -f1)" ]] \
    || refuse "${CODE}/${f} is not the deploy's committed blob"
done

uomni_log() {   # cov2d's carried condition: UOMNI's atime and mtime, with UTC, before and after the read
  python3 -c "
import os, sys, time
s = os.stat(sys.argv[1])
print('[geanttw-p3] UOMNI %s utc=%s atime_ns=%d mtime_ns=%d size=%d' % (sys.argv[2],
      time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), s.st_atime_ns, s.st_mtime_ns, s.st_size))" "${UOMNI}" "$1" >&2
}
if [[ "${READS_UOMNI}" -eq 1 ]]; then
  [[ "$(stat -c %s "${UOMNI}")" == "${UOMNI_SIZE}" ]] || refuse "UOMNI's size is not ${UOMNI_SIZE} (C1-b)"
fi

[[ -n "${GEANTTW_SMOKE:-}" ]] && { echo "[geanttw-p3] smoke: checks passed for ${MODE} (${NAME}, ${TL})"; exit 0; }
fence "immediately before the work"
[[ "${READS_UOMNI}" -eq 1 ]] && uomni_log before
OUT="${B}/run/p3"; P3="${B}/p3"
mkdir -p "${OUT}" "${P3}" || exit 4
DUMPS=()
for pl in "${PLAYLISTS[@]}"; do   # P2's 11 outputs (1B's from its untraced pilot reference) and P0's patched 1L
  case "${pl}" in
    1L) DUMPS+=("${B}/run/p0/pat/runEventLoopOmniFold_GEANTTW_pat_1L.root") ;;
    1B) DUMPS+=("${B}/run/p2/pat/runEventLoopOmniFold_GEANTTW_pat_pilotref_1B.root") ;;
    *)  DUMPS+=("${B}/run/p2/pat/runEventLoopOmniFold_GEANTTW_pat_${pl}.root") ;;
  esac
done
rc=0
case "${MODE}" in
  c2pre) "${UPY}" -I "${CODE}/c2_check.py" pre --uomni "${UOMNI}" \
           --dump "${B}/run/p0/pin/runEventLoopOmniFold_GEANTTW_pin_1L.root" --json "${OUT}/c2pre.json"; rc=$? ;;
  c2)    "${UPY}" -I "${CODE}/c2_check.py" full --uomni "${UOMNI}" --dumps "${DUMPS[@]}" --json "${OUT}/c2.json"; rc=$? ;;
  slim)
    "${UPY}" -I "${CODE}/p3_slim.py" select --driver "${DEPLOY}/2d-unfolding/unfold_2d_omnifold_unbinned.py" \
      --uomni "${UOMNI}" || { rc=10; }
    [[ ${rc} -eq 0 ]] && { "${UPY}" -I "${CODE}/p3_slim.py" build --uomni "${UOMNI}" --out "${P3}/slim-pinned.root" || rc=11; }
    [[ ${rc} -eq 0 ]] && { "${UPY}" -I "${CODE}/p3_slim.py" build --uomni "${UOMNI}" --out "${P3}/slim-pinned-override.root" \
      --dumps "${DUMPS[@]}" --pinned-override || rc=12; }
    [[ ${rc} -eq 0 ]] && { "${UPY}" -I "${CODE}/p3_slim.py" build --uomni "${UOMNI}" --out "${P3}/slim-patched-override.root" \
      --dumps "${DUMPS[@]}" --override || rc=13; }
    if [[ ${rc} -eq 0 ]]; then
      ( source "${SETUP}" >/dev/null 2>&1; python3 "${CODE}/slim_tparams.py" "${UOMNI}" "${P3}/slim-pinned.root" \
        "${P3}/slim-pinned-override.root" "${P3}/slim-patched-override.root" ) || rc=14
    fi
    [[ ${rc} -eq 0 ]] && { "${UPY}" -I "${CODE}/p3_slim.py" check --uomni "${UOMNI}" --slim "${P3}/slim-pinned.root" || rc=15; }
    [[ ${rc} -eq 0 ]] && { "${UPY}" -I "${CODE}/p3_slim.py" patchcheck --pinned "${P3}/slim-pinned.root" \
      --patched "${P3}/slim-patched-override.root" --dumps "${DUMPS[@]}" --override || rc=16; }
    ls -l "${P3}"/slim-*.root >&2 ;;
  unf)
    case "${SLIM}" in pin) SLIMFILE=slim-pinned.root ;; pinov) SLIMFILE=slim-pinned-override.root ;;
      patov) SLIMFILE=slim-patched-override.root ;; esac
    U_OUT="${P3}/out/${SLIM}/${UNI/:/_}"
    [[ -e "${U_OUT}/xsec.root" ]] && refuse "${U_OUT}/xsec.root exists"
    mkdir -p "${U_OUT}" || exit 4
    [[ "$(sha256sum "${SETUP}" | cut -d' ' -f1)" == "$(git -C "${DEPLOY}" show HEAD:setup_salloc_env.sh | sha256sum | cut -d' ' -f1)" ]] \
      || refuse "${SETUP} is not the deploy's committed setup_salloc_env.sh"
    source "${SETUP}" >/dev/null 2>&1
    export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=64 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
      NUMEXPR_NUM_THREADS=1
    unset LOKY_MAX_CPU_COUNT
    for pair in "${PROD_SHA}:${DEPLOY}/2d-unfolding/unfold_2d_omnifold_unbinned.py" "${HELPER_SHA}:${HELPER}" \
                "${MCFILE_SHA}:${MCFILE}" "${FLUXU_SHA}:${FLUXU}"; do
      echo "${pair%%:*}  ${pair#*:}" | sha256sum -c - >&2 || refuse "${pair#*:} is not its pinned sha256"
    done
    cd "${DEPLOY}/2d-unfolding" || exit 4
    env -u BASH_ENV -u ENV python3 unfold_2d_omnifold_unbinned.py --omnifile "${P3}/${SLIMFILE}" \
      --flux-universe-file "${FLUXU}" --verbose --mcfile "${MCFILE}" --iters 5 --use-weights --estimator lgbm \
      --bkg-mode purity --out "${U_OUT}/xsec.root" --universe "${UNI}" --seed 42 --branch-select derived; rc=$? ;;
  extract)
    ( source "${SETUP}" >/dev/null 2>&1; python3 "${CODE}/p3_readout.py" extract --repo "${DEPLOY}" --outs "${P3}/out" \
      --out "${OUT}/p3_vectors.npz" ) || rc=$? ;;
esac
[[ "${READS_UOMNI}" -eq 1 ]] && uomni_log after
say "${MODE} ${NAME} rc=${rc} end=$(date -u +%FT%TZ)"
exit ${rc}
