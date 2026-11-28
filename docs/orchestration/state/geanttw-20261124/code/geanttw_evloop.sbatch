#!/bin/bash
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --no-requeue
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
# geanttw_evloop.sbatch: event-loop job for the geanttw campaign (DECLARATION.md §4).
#   sbatch --job-name=geanttw_p0_<build>_<PL> --time=<limit> --output=<B>/run/logs/%x_%j.out \
#          geanttw_evloop.sbatch <B> <build pin|pat> <PL> <binary-md5> <deploy> [<p2-limits-file> <its sha256>]
# P0: PL must be 1L, TimeLimit <= 01:00:00, runs under strace.
# P2: build must be pat; limit from the limits file, whose sha256 must match. Job names geanttw_p2_<PL> (traced:
#     openat/open and the stat family), geanttw_p2_pilot_<PL> (also read/pread64) and geanttw_p2_pilotref_<PL>
#     (untraced), per p2p3/AMENDMENT-P2P3.md A2.
# Refuses if any cov2d, t2a or covfix_ job is queued/running (checked twice: at start and before binary).
# The binary runs under env -u BASH_ENV -u ENV, and refuses unless that launch has neither set.
# Refuses if MNV101_DUMP_POINTCLOUD is set.
# GEANTTW_SMOKE=1 runs every check then exits 0 before the binary.
set -o pipefail

# GBUILD, not BUILD: the ROOT env's conda activation exports BUILD=x86_64-conda-linux-gnu, which overwrote RDX's
# own BUILD (fd/redump-f12i-20261112/RDX-BINDING-1.md:189-190).
B="${1:?B}"; GBUILD="${2:?build pin|pat}"; PL="${3:?playlist}"; EXPECT_MD5="${4:?md5}"; DEPLOY="${5:?deploy}"
P2_LIMITS="${6:-}"; P2_LIMITS_SHA="${7:-}"
say() { echo "[geanttw-evloop] $*" >&2; }

[[ "${GBUILD}" == pin || "${GBUILD}" == pat ]] || { say "REFUSE: build must be pin or pat, got '${GBUILD}'"; exit 2; }

# --- determine phase and job name ---
# Parse the job name to determine phase
if [[ -n "${SLURM_JOB_ID:-}" ]]; then
  NAME="${SLURM_JOB_NAME}"
  TL=$(sacct -j "${SLURM_JOB_ID}" -X -n -P -o Timelimit 2>/dev/null | head -1)   # sacct, never squeue
else
  [[ -n "${GEANTTW_SMOKE:-}" ]] || { say "REFUSE: not inside a Slurm job"; exit 2; }
  NAME="${GEANTTW_NAME:-}"
  TL="${GEANTTW_TIMELIMIT:-}"
fi

# Determine phase from job name
PHASE=""
if [[ "${NAME}" =~ ^geanttw_p0_ ]]; then
  PHASE=p0
elif [[ "${NAME}" =~ ^geanttw_p2_ ]]; then
  PHASE=p2
else
  say "REFUSE: job name '${NAME}' does not match geanttw_p0_* or geanttw_p2_*"
  exit 2
fi

# --- phase-specific validation ---
if [[ "${PHASE}" == p0 ]]; then
  WANT="geanttw_p0_${GBUILD}_${PL}"
  [[ "${PL}" == 1L ]] || { say "REFUSE: p0 requires PL=1L, got '${PL}'"; exit 2; }
  LIMIT=01:00:00
elif [[ "${PHASE}" == p2 ]]; then
  VARIANT=""; TRACE=stat
  [[ "${NAME}" == "geanttw_p2_pilot_${PL}" ]] && { VARIANT=pilot_; TRACE=read; }
  [[ "${NAME}" == "geanttw_p2_pilotref_${PL}" ]] && { VARIANT=pilotref_; TRACE=none; }
  WANT="geanttw_p2_${VARIANT}${PL}"
  [[ -z "${VARIANT}" || "${PL}" == 1B ]] || { say "REFUSE: the pilot pair runs on 1B only, got '${PL}'"; exit 2; }
  [[ "${GBUILD}" == pat ]] || { say "REFUSE: p2 requires build=pat, got '${GBUILD}'"; exit 2; }
  [[ "${PL}" != 1L ]] || { say "REFUSE: p2 reuses P0's 1L output; it does not run 1L"; exit 2; }
  [[ -n "${P2_LIMITS}" && -n "${P2_LIMITS_SHA}" ]] || { say "REFUSE: p2 requires a limits file and its sha256"; exit 2; }
  actual_sha=$(sha256sum "${P2_LIMITS}" | cut -d' ' -f1)
  [[ "${actual_sha}" == "${P2_LIMITS_SHA}" ]] || { say "REFUSE: p2 limits file sha256 ${actual_sha} is not ${P2_LIMITS_SHA}"; exit 2; }
  # Read the limit for this playlist from the limits file (format: PL HH:MM:SS per line)
  LIMIT=$(awk -v p="${PL}" '$1 == p {print $2}' "${P2_LIMITS}")
  [[ -n "${LIMIT}" ]] || { say "REFUSE: no limit found for playlist ${PL} in ${P2_LIMITS}"; exit 2; }
fi

[[ "${NAME}" == "${WANT}" ]] || { say "REFUSE: job name '${NAME}' is not '${WANT}'"; exit 2; }

# --- TimeLimit check ---
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
[[ ${trc} -eq 0 ]] || { say "REFUSE: Slurm TimeLimit '${TL}' is not within ${LIMIT} (rc ${trc})"; exit 2; }

# --- fence check: no live cov2d or t2a job, read from sacct (never squeue: the standing rule). sbatch runs a copy of
# this file, so the reader is taken from the deploy. ---
CODE="${DEPLOY}/docs/orchestration/state/geanttw-20261124/code"
fence_check() {
  local label="$1" psv since rc
  psv=$(mktemp -p "${B}/run") || { say "REFUSE: mktemp failed (${label})"; exit 2; }   # its file stays under B
  since=$(python3 -c 'import datetime; print((datetime.date.today() - datetime.timedelta(14)).isoformat())')
  sacct -X -n -P -S "${since}" -o JobID,JobName,State,ElapsedRaw,NNodes,TimelimitRaw > "${psv}" 2>&1 \
    || { say "REFUSE: sacct failed (${label})"; rm -f "${psv}"; exit 2; }
  python3 -I "${CODE}/geanttw_sacct.py" fence --sacct "${psv}" --regex '^(cov2d|t2a|covfix_)' >&2; rc=$?
  rm -f "${psv}"
  [[ ${rc} -eq 0 ]] || { say "REFUSE: fenced jobs are live, or sacct is unreadable (${label}, rc ${rc})"; exit 2; }
}
mkdir -p "${B}/run" || { say "REFUSE: cannot make ${B}/run"; exit 2; }
fence_check "at start"

# --- refuse if MNV101_DUMP_POINTCLOUD is set ---
[[ -n "${MNV101_DUMP_POINTCLOUD+x}" ]] && { say "REFUSE: MNV101_DUMP_POINTCLOUD is set"; exit 2; }

# --- binary md5 check ---
BIN="${B}/prefix-${GBUILD}/bin/runEventLoopOmniFold"
actual_md5=$(md5sum "${BIN}" | cut -d' ' -f1)
[[ "${actual_md5}" == "${EXPECT_MD5}" ]] || { say "REFUSE: ${BIN} md5 ${actual_md5} is not ${EXPECT_MD5}"; exit 2; }

# --- manifest check: deploy's committed manifests must match ---
for suf in Data MC; do
  f="${DEPLOY}/2d-unfolding/playlist_manifests/${PL}_${suf}.txt"
  rel="2d-unfolding/playlist_manifests/${PL}_${suf}.txt"
  actual=$(sha256sum "${f}" | cut -d' ' -f1)
  committed=$(git -C "${DEPLOY}" show "HEAD:${rel}" | sha256sum | cut -d' ' -f1)
  [[ "${actual}" == "${committed}" ]] \
    || { say "REFUSE: ${f} is not the deploy's committed ${rel}"; exit 2; }
done

# --- AnaTuple size/mtime check ---
ANATUPLE_ROOT="${GEANTTW_ANATUPLE_ROOT:-/pscratch/sd/j/josephrb/minerva/minerva_large_files/}"
ANATUPLE_TSV="${DEPLOY}/publication/release/preservation/anatuple-checksums/ANATUPLE-SHA256.tsv"
DATA="${DEPLOY}/2d-unfolding/playlist_manifests/${PL}_Data.txt"
MC="${DEPLOY}/2d-unfolding/playlist_manifests/${PL}_MC.txt"
python3 - "${ANATUPLE_ROOT}" "${ANATUPLE_TSV}" "${DATA}" "${MC}" <<'EOF' || { say "REFUSE: an AnaTuple's size or mtime is not its manifest row's"; exit 2; }
import os, sys, time
root, tsv, lists = sys.argv[1].rstrip("/") + "/", sys.argv[2], sys.argv[3:]
rows = {}
for ln in open(tsv):
    f = ln.rstrip("\n").split("\t")
    if len(f) == 4 and len(f[0]) == 64:
        rows[f[3]] = (int(f[1]), f[2])
bad, n = [], 0
for lst in lists:
    for p in open(lst).read().split():
        n += 1
        rel = p[len(root):] if p.startswith(root) else None
        if rel is None or rel not in rows:
            bad.append(f"{p}: not under {root} or not in the manifest"); continue
        st = os.stat(p)
        want_bytes, want_mtime = rows[rel]
        mt = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(int(st.st_mtime)))
        if st.st_size != want_bytes or mt != want_mtime:
            bad.append(f"{p}: {st.st_size} B {mt}, manifest {want_bytes} B {want_mtime}")
print(f"[geanttw-evloop] {n} AnaTuples checked by size and mtime; {len(bad)} differ", file=sys.stderr)
for b in bad[:20]:
    print("  " + b, file=sys.stderr)
sys.exit(1 if bad else 0)
EOF

# --- output check ---
OUT="${B}/run/${PHASE}/${GBUILD}/runEventLoopOmniFold_GEANTTW_${GBUILD}_${VARIANT:-}${PL}.root"
[[ -e "${OUT}" ]] && { say "REFUSE: ${OUT} exists"; exit 3; }

# --- environment setup ---
# Activate conda root_6_28 the same way setup_salloc_env.sh does, but NEVER source setup_salloc_env.sh
ROOT628_PREFIX="${ROOT628_PREFIX:-$HOME/.conda/envs/root_6_28}"
ROOT628_CONDA="${ROOT628_CONDA:-/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda}"
[[ -x "${ROOT628_CONDA}" && -d "${ROOT628_PREFIX}" ]] \
  || { say "REFUSE: conda ${ROOT628_CONDA} or env ${ROOT628_PREFIX} is missing (no legacy module fallback)"; exit 2; }
eval "$("${ROOT628_CONDA}" shell.bash hook 2>/dev/null)"
conda activate "${ROOT628_PREFIX}"
[[ "${CONDA_PREFIX:-}" == "${ROOT628_PREFIX}" ]] \
  || { say "REFUSE: conda activation did not give CONDA_PREFIX=${ROOT628_PREFIX} (got '${CONDA_PREFIX:-}')"; exit 2; }

export MINERVA_PREFIX="${B}/prefix-${GBUILD}"
source "${B}/prefix-${GBUILD}/bin/setup.sh"

# --- ldd check: refuse if any libMAT*.so resolves outside our prefix ---
say "ldd of ${BIN}:"
ldd_out=$(ldd "${BIN}" 2>&1)
echo "${ldd_out}" >&2
# any library from the production opt, and any libMAT* not from this build's prefix (or not found), refuses
bad_libs=$(printf '%s\n' "${ldd_out}" | awk -v own="${B}/prefix-${GBUILD}/lib/" \
  '/=>/ { if ($3 ~ /\/MINERvA101\/opt\//) print; else if ($1 ~ /^libMAT/ && index($3, own) != 1) print }')
[[ -z "${bad_libs}" ]] || { say "REFUSE: libraries resolve outside ${B}/prefix-${GBUILD}/lib: ${bad_libs}"; exit 2; }

# --- unset every MNV101_* then set only what we need ---
while IFS='=' read -r var _; do unset "${var}"; done < <(env | grep '^MNV101_')
export MNV101_DUMP_UNIVERSES=GEANT_Neutron,GEANT_Pion,GEANT_Proton

# --- NuE file logging ---
NUE="${B}/prefix-${GBUILD}/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt"
[[ -f "${NUE}" ]] || { say "REFUSE: the NuE file ${NUE} is missing"; exit 2; }
UOMNI="${GEANTTW_TEST_UOMNI:-/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/runEventLoopOmniFold_MEFHC_universes_full.root}"
stamps() {   # cov2d's carried conditions, fail-closed (amendment 3): the NuE file's and UOMNI's atime_ns and mtime_ns,
             # by stat (never an open), with UTC; ino shows which file a symlinked path reached
  python3 -c "
import os,sys,time
utc = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
st = [(n, os.stat(p)) for n, p in (('NUE', sys.argv[1]), ('UOMNI', sys.argv[2]))]
for n, s in st:
    print('[geanttw-evloop] %s %s utc=%s atime_ns=%d mtime_ns=%d size=%d ino=%d' % (
        n, sys.argv[3], utc, s.st_atime_ns, s.st_mtime_ns, s.st_size, s.st_ino))" "${NUE}" "${UOMNI}" "$1"
}

say "env: $(env | grep '^MNV101_' | sort | tr '\n' ' ')"

# --- the binary's launch environment: no BASH_ENV and no ENV, so no child bash sources Lmod (C0e's attribution) ---
LAUNCH=(env -u BASH_ENV -u ENV)
"${LAUNCH[@]}" python3 -c 'import os, sys; sys.exit(1 if {"BASH_ENV", "ENV"} & set(os.environ) else 0)' \
  || { say "REFUSE: BASH_ENV or ENV is still set under the binary's launch"; exit 2; }
say "launch env: BASH_ENV and ENV unset"

# --- smoke mode: every check above passed (environment, ldd and MNV101_ included); stop before the binary ---
[[ -n "${GEANTTW_SMOKE:-}" ]] && { echo "[geanttw-evloop] smoke: checks passed for ${GBUILD} ${PL} (${NAME}, ${TL})"; exit 0; }

# --- second fence check immediately before the binary ---
fence_check "immediately before the binary"

stamps before || { say "REFUSE: cannot log the stamps before the binary"; exit 2; }

mkdir -p "$(dirname "${OUT}")"
WORK="${B}/run/${PHASE}/${GBUILD}/work_${VARIANT:-}${PL}_$$"
mkdir -p "${WORK}" && cd "${WORK}" || exit 4

say "${GBUILD} ${PL} job=${SLURM_JOB_ID:-smoke} host=$(hostname) bin=${BIN} md5=${EXPECT_MD5} start=$(date -u +%FT%TZ)"
t0=$(date +%s)
STAT_SET=openat,open,stat,lstat,newfstatat,statx,access
if [[ "${PHASE}" == p0 ]]; then
  STRACE_OUT="${B}/run/p0/${GBUILD}/strace.${GBUILD}.${PL}"
  "${LAUNCH[@]}" strace -f -y -e trace=openat,open -o "${STRACE_OUT}" "${BIN}" "${DATA}" "${MC}"; rc=$?
elif [[ "${TRACE}" == stat ]]; then
  STRACE_OUT="${B}/run/p2/${GBUILD}/strace.${GBUILD}.${PL}"
  "${LAUNCH[@]}" strace -f -y -e trace="${STAT_SET}" -o "${STRACE_OUT}" "${BIN}" "${DATA}" "${MC}"; rc=$?
elif [[ "${TRACE}" == read ]]; then
  STRACE_OUT="${B}/run/p2/${GBUILD}/strace.${GBUILD}.pilot_${PL}"
  "${LAUNCH[@]}" strace -f -y -s 0 -e trace="${STAT_SET},read,pread64" -o "${STRACE_OUT}" "${BIN}" "${DATA}" "${MC}"; rc=$?
else
  "${LAUNCH[@]}" "${BIN}" "${DATA}" "${MC}"; rc=$?
fi

stamps after || { say "the stamps after the binary cannot be written"; exit 20; }

say "rc=${rc} elapsed=$(( $(date +%s) - t0 ))s"
[[ ${rc} -eq 0 && -s runEventLoopOmniFold.root ]] || exit 5
mv runEventLoopOmniFold.root "${OUT}.partial" && mv "${OUT}.partial" "${OUT}" && chmod 0440 "${OUT}"
say "wrote ${OUT} ($(python3 -c 'import os,sys; print(os.path.getsize(sys.argv[1]))' "${OUT}") bytes) sha256 $(sha256sum "${OUT}" | cut -d' ' -f1)"
cd "${B}" && rm -rf -- "${WORK}"
