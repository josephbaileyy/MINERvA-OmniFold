#!/bin/bash
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --no-requeue
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
# geanttw C2's pre-check and the P3 jobs (p2p3/AMENDMENT-P2P3.md A3; cov2d's (C) grant and amendments 1-3).
#   sbatch --job-name=NAME --time=LIMIT -c CPUS --mem=MEM geanttw_p3.sbatch MODE B DEPLOY [ARGS...]
# MODE and its job name, limit and request:
#   c2pre    geanttw_p2_c2pre     00:30:00   2 CPUs, 16G     c2_check.py pre: P0's pinned 1L dump vs UOMNI's 1L slice
#   slim     geanttw_p3_slim      02:00:00   2 CPUs, 32G     p3_slim.py build (UOMNI's ONE open: C1-a, the full C2
#                                                            and the three slims), slim_tparams.py and verify, from
#                                                            build's record and the slims only -> slim.json
#   unf      geanttw_p3_unf_<s>_GEANT_<b>_<i>  00:30:00  128 CPUs, 243840M   Stage C's universe unfold, on a slim
#   extract  geanttw_p3_extract_<pin|all>  00:30:00  2 CPUs, 16G   p3_readout.py extract (pin: the 6 pinned
#            vectors and S5's July ones, then c3 -> run/p3/c3.json; all: the 18 vectors, only after C3 PASS)
# Every mode:
# - checks its job name and its Slurm TimeLimit (read from sacct, never squeue) against the mode's;
# - refuses while any ^(cov2d|t2a|covfix_) job is live, at start and again immediately before its work;
# - runs only the deploy's committed scripts, each checked against its blob at the deploy's HEAD.
# Every mode that reads UOMNI, MCFILE or the NuE file logs UOMNI's and the NuE file's atime_ns and mtime_ns (by stat,
# never an open), plus MCFILE's and the flux-universe file's in unf, with UTC, before and after (cov2d's carried
# conditions). A log that cannot be written stops the job.
# unf refuses unless slim.json is PASS, the slim's sha256 is the recorded one, and MCFILE's size and mtime are the
# recorded ones (MCFILE is hashed once, by slim; amendment 3). For pinov and patov it also refuses unless c3.json is
# PASS and each pinned output's sha256 is the one C3 recorded (the director's term 1); extract all needs the same.
# Every sourcing of the ROOT setup resets TMPDIR to B/run/tmp. The flux-universe file is
# never opened (the driver opens it only for the Flux band, unfold_2d_omnifold_unbinned.py:1709-1715, :148). If its
# atime or mtime moves, or MCFILE's mtime, the job exits 21.
# GEANTTW_SMOKE=1 runs every check, then exits 0 before the work.
set -o pipefail
MODE="${1:?mode}"; B="${2:?B}"; DEPLOY="${3:?deploy}"; shift 3
say() { echo "[geanttw-p3] $*" >&2; }
stop() { say "REFUSE: $*"; exit 2; }
CODE="${DEPLOY}/docs/orchestration/state/geanttw-20261124/code"
SYSPY=$(command -v python3) || stop "no python3"   # the helpers' python, fixed before unf sources the ROOT setup
UOMNI=/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/runEventLoopOmniFold_MEFHC_universes_full.root
UOMNI_SIZE=171117087867
NUE=/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt
UPY=/global/homes/j/josephrb/.conda/envs/omnifold_py310/bin/python3
D2=/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding
SETUP=/pscratch/sd/j/josephrb/MINERvA-OmniFold/setup_salloc_env.sh
PROD_SHA=74a4ed69c3fa9c4ae5b6866f36343212b8d3f903fddde6c7bd40c382c1167d56   # Stage C's driver (sbatch_prod.sh:23)
HELPER=/pscratch/sd/j/josephrb/MINERvA-OmniFold/unbinned_unfolding/python/omnifold.py
HELPER_SHA=e96234124a31edd7a8dd61fdb16cb48a5b28cbd1b90202f59b0095868378227a
MCFILE="${D2}/baseline_flux/runEventLoopMC_MEFHC.root"
MCFILE_SHA=d40aea69235cdc98644e1bb3e622e579d6b81904c004c83fe50465079989f316
FLUXU="${D2}/baseline_flux/flux_integral_universes_MEFHC.root"   # in the argv only; never read or hashed
PLAYLISTS=(1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P)   # hadd order (sbatch_hadd_MEFHC_universes_full.sh:32-43)
if [[ -n "${GEANTTW_TEST_UOMNI:-}" ]]; then   # the tests' only door
  UOMNI="${GEANTTW_TEST_UOMNI}"; UOMNI_SIZE="${GEANTTW_TEST_UOMNI_SIZE:?}"; UPY="${GEANTTW_TEST_PY:-python3}"
  SETUP="${GEANTTW_TEST_SETUP:-${SETUP}}"; NUE="${GEANTTW_TEST_NUE:?}"
  PROD_SHA="${GEANTTW_TEST_PROD_SHA:-${PROD_SHA}}"; HELPER="${GEANTTW_TEST_HELPER:-${HELPER}}"
  HELPER_SHA="${GEANTTW_TEST_HELPER_SHA:-${HELPER_SHA}}"; MCFILE="${GEANTTW_TEST_MCFILE:-${MCFILE}}"
  MCFILE_SHA="${GEANTTW_TEST_MCFILE_SHA:-${MCFILE_SHA}}"; FLUXU="${GEANTTW_TEST_FLUXU:-${FLUXU}}"
fi

# --- the mode's job name and limit ---
case "${MODE}" in
  c2pre)   WANT=geanttw_p2_c2pre; LIMIT=00:30:00; READS_UOMNI=1; LOGS=("${UOMNI}" "${NUE}") ;;
  slim)    WANT=geanttw_p3_slim; LIMIT=02:00:00; READS_UOMNI=1; LOGS=("${UOMNI}" "${NUE}" "${MCFILE}") ;;
  extract) WHICH="${1:?pin|all}"; [[ "${WHICH}" =~ ^(pin|all)$ ]] || stop "extract takes pin or all, got '${WHICH}'"
           WANT="geanttw_p3_extract_${WHICH}"; LIMIT=00:30:00; READS_UOMNI=0; LOGS=("${UOMNI}" "${NUE}") ;;
  unf)     SLIM="${1:?slim pin|pinov|patov}"; UNI="${2:?universe GEANT_<b>:<i>}"
           [[ "${SLIM}" =~ ^(pin|pinov|patov)$ ]] || stop "slim '${SLIM}' is not pin, pinov or patov"
           [[ "${UNI}" =~ ^GEANT_(Neutron|Pion|Proton):[01]$ ]] || stop "universe '${UNI}' is not GEANT_<b>:<i>"
           WANT="geanttw_p3_unf_${SLIM}_${UNI/:/_}"; LIMIT=00:30:00; READS_UOMNI=0
           LOGS=("${UOMNI}" "${NUE}" "${MCFILE}" "${FLUXU}") ;;
  *) stop "mode '${MODE}' is not c2pre, slim, unf or extract" ;;
esac
if [[ -n "${SLURM_JOB_ID:-}" ]]; then
  NAME="${SLURM_JOB_NAME}"
  TL=$(sacct -j "${SLURM_JOB_ID}" -X -n -P -o Timelimit 2>/dev/null | head -1)
else
  [[ -n "${GEANTTW_SMOKE:-}" ]] || stop "not inside a Slurm job"
  NAME="${GEANTTW_NAME:-}"; TL="${GEANTTW_TIMELIMIT:-}"
fi
[[ "${NAME}" == "${WANT}" ]] || stop "job name '${NAME}' is not '${WANT}'"
[[ "${TL}" == "${LIMIT}" ]] || stop "Slurm TimeLimit '${TL}' is not ${LIMIT}"
OUT="${B}/run/p3"; P3="${B}/p3"
mkdir -p "${OUT}" "${P3}" || stop "cannot make ${OUT} and ${P3}"

# --- the fence: no live cov2d, t2a or covfix_ job, from sacct; its file stays under B ---
fence() {
  local psv since rc
  psv=$(mktemp -p "${B}/run") || stop "mktemp failed ($1)"
  since=$("${SYSPY}" -c 'import datetime; print((datetime.date.today() - datetime.timedelta(14)).isoformat())')
  sacct -X -n -P -S "${since}" -o JobID,JobName,State,ElapsedRaw,NNodes,TimelimitRaw > "${psv}" 2>&1 \
    || { rm -f "${psv}"; stop "sacct failed ($1)"; }
  "${SYSPY}" -I "${CODE}/geanttw_sacct.py" fence --sacct "${psv}" --regex '^(cov2d|t2a|covfix_)' >&2; rc=$?
  rm -f "${psv}"
  [[ ${rc} -eq 0 ]] || stop "fenced jobs are live, or sacct is unreadable ($1, rc ${rc})"
}
fence "at start"

# --- the deploy's scripts are its committed blobs ---
for f in c2_check.py p3_slim.py slim_tparams.py p3_readout.py geanttw_sacct.py; do
  [[ "$(sha256sum "${CODE}/${f}" | cut -d' ' -f1)" == "$(git -C "${DEPLOY}" show "HEAD:docs/orchestration/state/geanttw-20261124/code/${f}" | sha256sum | cut -d' ' -f1)" ]] \
    || stop "${CODE}/${f} is not the deploy's committed blob"
done

stamps() {   # stamps LABEL FILE...: logs atime_ns and mtime_ns by stat (never an open), with UTC, one line per file,
             # to stderr, and prints the same values as atime_ns:mtime_ns pairs, so what is compared is what is logged
  "${SYSPY}" -c "
import os, sys, time
utc = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
st = [(p, os.stat(p)) for p in sys.argv[2:]]
for p, s in st:
    sys.stderr.write('[geanttw-p3] STAMP %s %s utc=%s atime_ns=%d mtime_ns=%d size=%d\\n' % (sys.argv[1], p, utc, s.st_atime_ns, s.st_mtime_ns, s.st_size))
print(' '.join('%d:%d' % (s.st_atime_ns, s.st_mtime_ns) for p, s in st))
" "$@"
}
json_get() {   # json_get FILE KEY...: a value from a JSON record, or nothing
  "${SYSPY}" -c "
import json, sys
v = json.load(open(sys.argv[1]))
for k in sys.argv[2:]:
    v = v[k]
print(v)" "$@" 2>/dev/null
}
mc_same() {   # mc_same SLIM.json: MCFILE's size and mtime_ns are the ones the slim job recorded with its sha256
  "${SYSPY}" -c "
import json, os, sys
m = json.load(open(sys.argv[1]))['mcfile']; s = os.stat(sys.argv[2])
sys.exit(0 if (m['size'], m['mtime_ns']) == (s.st_size, s.st_mtime_ns) else 1)" "$1" "${MCFILE}" 2>/dev/null
}
sha_is() {   # sha_is FILE WANT: FILE is a regular file and WANT is a 64-hex sha256 equal to FILE's (never "" == "")
  local got
  [[ -f "$1" && "$2" =~ ^[0-9a-f]{64}$ ]] || return 1
  got=$(sha256sum "$1" | cut -d' ' -f1) || return 1
  [[ "${got}" == "$2" ]]
}
c3_bound() {   # C3 PASS, and each of the six pinned outputs still hashes to the sha256 C3 recorded
  local u
  [[ "$(json_get "${OUT}/c3.json" verdict)" == PASS ]] || stop "C3 is not PASS: $1"
  for u in GEANT_Neutron_0 GEANT_Neutron_1 GEANT_Pion_0 GEANT_Pion_1 GEANT_Proton_0 GEANT_Proton_1; do
    sha_is "${P3}/out/pin/${u}/xsec.root" "$(json_get "${OUT}/c3.json" pin_xsec_sha256 "pin:${u#GEANT_}")" \
      || stop "the pinned output ${u} is not the one C3 passed"
  done
}
rootenv() {   # the ROOT setup, with TMPDIR kept under B (setup_salloc_env.sh:24 sets it to $SCRATCH/tmp)
  source "${SETUP}" >/dev/null 2>&1
  export TMPDIR="${B}/run/tmp"
  mkdir -p "${TMPDIR}" || stop "cannot make ${TMPDIR}"
}
if [[ "${READS_UOMNI}" -eq 1 ]]; then
  [[ "$(stat -c %s "${UOMNI}")" == "${UOMNI_SIZE}" ]] || stop "UOMNI's size is not ${UOMNI_SIZE} (C1-b)"
fi

if [[ "${MODE}" == unf ]]; then
  case "${SLIM}" in pin) SLIMFILE=slim-pinned.root ;; pinov) SLIMFILE=slim-pinned-override.root ;;
    patov) SLIMFILE=slim-patched.root ;; esac
  [[ "$(json_get "${OUT}/slim.json" verdict)" == PASS ]] || stop "slim.json is not PASS"
  sha_is "${P3}/${SLIMFILE}" "$(json_get "${OUT}/slim.json" slims "${SLIM}" sha256)" \
    || stop "${P3}/${SLIMFILE} is not the slim slim.json recorded"
  mc_same "${OUT}/slim.json" || stop "MCFILE's size or mtime is not slim.json's"
  if [[ "${SLIM}" != pin ]]; then
    c3_bound "no override unfold runs"
  fi
fi
if [[ "${MODE}" == extract && "${WHICH}" == all ]]; then
  c3_bound "no patched number is read"
fi

[[ -n "${GEANTTW_SMOKE:-}" ]] && { echo "[geanttw-p3] smoke: checks passed for ${MODE} (${NAME}, ${TL})"; exit 0; }
fence "immediately before the work"
BEFORE=$(stamps before "${LOGS[@]}") || stop "cannot log the stamps before the read"
DUMPS=()
for pl in "${PLAYLISTS[@]}"; do   # P2's 11 outputs (1B's from its untraced pilot reference) and P0's patched 1L
  case "${pl}" in
    1L) DUMPS+=("${B}/run/p0/pat/runEventLoopOmniFold_GEANTTW_pat_1L.root") ;;
    1B) DUMPS+=("${B}/run/p2/pat/runEventLoopOmniFold_GEANTTW_pat_pilotref_1B.root") ;;
    *)  DUMPS+=("${B}/run/p2/pat/runEventLoopOmniFold_GEANTTW_pat_${pl}.root") ;;
  esac
done
DRIVER="${DEPLOY}/2d-unfolding/unfold_2d_omnifold_unbinned.py"
rc=0
case "${MODE}" in
  c2pre) "${UPY}" -I "${CODE}/c2_check.py" pre --uomni "${UOMNI}" \
           --dump "${B}/run/p0/pin/runEventLoopOmniFold_GEANTTW_pin_1L.root" --json "${OUT}/c2pre.json"; rc=$? ;;
  slim)
    "${UPY}" -I "${CODE}/p3_slim.py" build --uomni "${UOMNI}" --driver "${DRIVER}" --dumps "${DUMPS[@]}" \
      --outdir "${P3}" --record "${OUT}/slim_build.json" --c2 "${OUT}/c2.json" || rc=11
    if [[ ${rc} -eq 0 ]]; then
      ( rootenv; python3 "${CODE}/slim_tparams.py" "${OUT}/slim_build.json" "${P3}/slim-pinned.root" \
        "${P3}/slim-pinned-override.root" "${P3}/slim-patched.root" ) || rc=14
    fi
    [[ ${rc} -eq 0 ]] && { "${UPY}" -I "${CODE}/p3_slim.py" verify --driver "${DRIVER}" \
      --outdir "${P3}" --record "${OUT}/slim_build.json" --mcfile "${MCFILE}" --mcfile-sha "${MCFILE_SHA}" \
      --out "${OUT}/slim.json" || rc=15; }
    ls -l "${P3}"/slim-*.root >&2 ;;
  unf)
    U_OUT="${P3}/out/${SLIM}/${UNI/:/_}"
    [[ -e "${U_OUT}/xsec.root" ]] && stop "${U_OUT}/xsec.root exists"
    mkdir -p "${U_OUT}" || stop "cannot make ${U_OUT}"
    cd "${DEPLOY}/2d-unfolding" || stop "no ${DEPLOY}/2d-unfolding"
    [[ "$(sha256sum "${SETUP}" | cut -d' ' -f1)" == "$(git -C "${DEPLOY}" show HEAD:setup_salloc_env.sh | sha256sum | cut -d' ' -f1)" ]] \
      || stop "${SETUP} is not the deploy's committed setup_salloc_env.sh"
    rootenv
    export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=64 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
      NUMEXPR_NUM_THREADS=1
    unset LOKY_MAX_CPU_COUNT
    for pair in "${PROD_SHA}:unfold_2d_omnifold_unbinned.py" "${HELPER_SHA}:${HELPER}"; do
      echo "${pair%%:*}  ${pair#*:}" | sha256sum -c - >&2 || stop "${pair#*:} is not its pinned sha256"
    done
    env -u BASH_ENV -u ENV python3 unfold_2d_omnifold_unbinned.py --omnifile "${P3}/${SLIMFILE}" \
      --flux-universe-file "${FLUXU}" --verbose --mcfile "${MCFILE}" --iters 5 --use-weights --estimator lgbm \
      --bkg-mode purity --out "${U_OUT}/xsec.root" --universe "${UNI}" --seed 42 --branch-select derived; rc=$? ;;
  extract)
    SL=(pin pinov patov); C3A=(--c3 "${OUT}/c3.json"); [[ "${WHICH}" == pin ]] && { SL=(pin); C3A=(); }
    ( rootenv; python3 "${CODE}/p3_readout.py" extract --repo "${DEPLOY}" --outs "${P3}/out" \
      --out "${OUT}/p3_vectors_${WHICH}.npz" --slims "${SL[@]}" "${C3A[@]}" ) || rc=$?
    if [[ ${rc} -eq 0 && "${WHICH}" == pin ]]; then
      "${UPY}" -I "${CODE}/p3_readout.py" c3 --repo "${DEPLOY}" --vectors "${OUT}/p3_vectors_pin.npz" \
        --json "${OUT}/c3.json" || rc=$?
    fi ;;
esac
AFTER=$(stamps after "${LOGS[@]}") || { say "the stamps after the read cannot be written"; exit 20; }
if [[ "${MODE}" == unf ]]; then   # amendment 3 (1-a), as cov2d clarified it: FLUXU untouched, MCFILE not rewritten
  read -r -a b4 <<< "${BEFORE}"; read -r -a af <<< "${AFTER}"
  [[ "${b4[3]}" == "${af[3]}" ]] || { say "DEVIATION: ${FLUXU}'s atime or mtime moved (${b4[3]} -> ${af[3]})"; exit 21; }
  [[ "${b4[2]#*:}" == "${af[2]#*:}" ]] || { say "DEVIATION: ${MCFILE}'s mtime moved"; exit 21; }
fi
say "${MODE} ${NAME} rc=${rc} end=$(date -u +%FT%TZ)"
exit ${rc}
