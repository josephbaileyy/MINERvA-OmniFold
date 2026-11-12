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
# RDX stages 1 and 2 (RDX-DECLARATION.md §3, §5): one playlist's event loop with the patched binary and
# MNV101_DUMP_TRUTHX=1, every other MNV101_* variable unset, over S0's manifests; the request is MP-1 S1's (2 CPUs,
# 16 GB, shared), whose billing gives the price rate. sbatch runs a copy of this file, so every path is an argument.
#   sbatch --job-name=rdx_s<1|2>_<PL> --time=<limit> --output=<B>/out/logs/%x_%j.out sbatch_rdx_evloop.sh \
#          <B> <deploy> <PL> <binary> <binary md5>
# The NuE flux-constraint file (cov2d-protected) is read by the binary plainly, once, at initialisation, under the
# director's exception of 2026-11-12 (cov2d's no-objection): the fence is checked here, immediately before the binary,
# and the file's atime_ns and mtime_ns are logged, with the UTC time, before and after the run.
# Refuses before reading any AnaTuple unless: the job's name is rdx_s1_1A or rdx_s2_<PL> (PL not 1A) and its Slurm
# TimeLimit is at most the playlist's declared limit (§5's rule); no fenced job is queued or running; the binary's md5
# is the build's; the manifests are S0's (their sha256 below); every listed AnaTuple has the size and mtime of its row
# in ANATUPLE-SHA256.tsv (its sha256 is not recomputed: 1A alone is about 0.7 TB of MC); the output does not exist.
set -o pipefail   # NOT set -u: setup_salloc_env.sh references unset variables under nounset
B="${1:?B}"; DEPLOY="${2:?deploy}"; PL="${3:?playlist}"; BIN="${4:?binary}"; EXPECT_MD5="${5:?md5}"
say() { echo "[rdx-evloop] $*" >&2; }
[[ "${B}" == /pscratch/sd/j/josephrb/rdx-20261112 || -n "${RDX_SMOKE}" ]] || { say "REFUSE: B is ${B}"; exit 2; }
case "${PL}" in
  1A) LIMIT=2:15:00 ;; 1B) LIMIT=1:00:00 ;; 1C) LIMIT=1:15:00 ;; 1D) LIMIT=3:30:00 ;; 1E) LIMIT=2:45:00 ;;
  1F) LIMIT=3:45:00 ;; 1G) LIMIT=3:15:00 ;; 1L) LIMIT=1:00:00 ;; 1M) LIMIT=4:45:00 ;; 1N) LIMIT=2:45:00 ;;
  1O) LIMIT=1:00:00 ;; 1P) LIMIT=1:00:00 ;;
  *) say "REFUSE: playlist '${PL}'"; exit 2 ;;
esac
WANT="rdx_s2_${PL}"; [[ "${PL}" == 1A ]] && WANT=rdx_s1_1A
if [[ -n "${SLURM_JOB_ID}" ]]; then
  NAME="${SLURM_JOB_NAME}"; TL=$(squeue -h -j "${SLURM_JOB_ID}" -o %l 2>/dev/null)
else
  [[ -n "${RDX_SMOKE}" ]] || { say "REFUSE: not inside a Slurm job"; exit 2; }
  NAME="${RDX_NAME:-${WANT}}"; TL="${RDX_TIMELIMIT:-${LIMIT}}"
fi
[[ "${NAME}" == "${WANT}" ]] || { say "REFUSE: job name ${NAME} is not ${WANT}"; exit 2; }
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
sq=$(squeue -h -u "${USER:-josephrb}" -o '%j|%T' 2>/dev/null) || { say "REFUSE: squeue failed"; exit 2; }
hit=$(printf '%s\n' "${sq}" | awk -F'|' '$1 ~ /^(cov2d|t2a|ll5d|e96data|rpd_|rsn_)/')
[[ -z "${hit}" ]] || { say "REFUSE: fenced jobs are queued or running: ${hit}"; exit 2; }
[[ -n "${MNV101_DUMP_POINTCLOUD+x}" || -n "${MNV101_DUMP_UNIVERSES+x}" ]] && { say "REFUSE: a point-cloud or universe dump is set"; exit 2; }
[[ "$(md5sum "${BIN}" | cut -d' ' -f1)" == "${EXPECT_MD5}" ]] || { say "REFUSE: ${BIN} md5 is not ${EXPECT_MD5}"; exit 2; }
CANON="${RDX_CANON:-/pscratch/sd/j/josephrb/MINERvA-OmniFold}"
DATA="${CANON}/2d-unfolding/playlist_manifests/${PL}_Data.txt"
MC="${CANON}/2d-unfolding/playlist_manifests/${PL}_MC.txt"
for f in "${DATA}" "${MC}"; do
  rel="2d-unfolding/playlist_manifests/$(basename "${f}")"
  [[ "$(sha256sum "${f}" | cut -d' ' -f1)" == "$(git -C "${DEPLOY}" show "HEAD:${rel}" | sha256sum | cut -d' ' -f1)" ]] \
    || { say "REFUSE: ${f} is not the deploy's committed ${rel}"; exit 2; }
done
python3 - "${RDX_ANATUPLE_ROOT:-/pscratch/sd/j/josephrb/minerva/minerva_large_files/}" "${DEPLOY}/publication/release/preservation/anatuple-checksums/ANATUPLE-SHA256.tsv" "${DATA}" "${MC}" <<'EOF' || { say "REFUSE: an AnaTuple's size or mtime is not its manifest row's"; exit 2; }
import os, sys, time
root, tsv, lists = sys.argv[1], sys.argv[2], sys.argv[3:]
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
print(f"[rdx-evloop] {n} AnaTuples checked by size and mtime; {len(bad)} differ", file=sys.stderr)
for b in bad[:20]:
    print("  " + b, file=sys.stderr)
sys.exit(1 if bad else 0)
EOF
OUT="${B}/out/evloop/runEventLoopOmniFold_RDX_${PL}.root"
[[ -e "${OUT}" ]] && { say "REFUSE: ${OUT} exists"; exit 3; }
[[ -n "${RDX_SMOKE}" ]] && { echo "[rdx-evloop] smoke: checks passed for ${PL} (${NAME}, ${TL})"; exit 0; }
source "${CANON}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1
unset MNV101_DUMP_UNIVERSES MNV101_DUMP_POINTCLOUD MNV101_FULL_PHASE_SPACE MNV101_SKIP_SYST MNV101_TRUTH_ONLY \
      MNV101_DISABLE_TRUTH_MISSES MNV101_DUMP_COMPONENTS MNV101_ACTIVE_UNIVERSE MNV101_RECOIL_RESPONSE_DELTA \
      MNV101_SPECIES_RESPONSE_Q0 MNV101_SPECIES_RESPONSE_FUZZ MNV101_SPECIES_RESPONSE_FTABLE
export MNV101_DUMP_TRUTHX=1
WORK="${B}/work/${PL}_${SLURM_JOB_ID}_$$"
mkdir -p "${WORK}" "$(dirname "${OUT}")" && cd "${WORK}" || exit 4
echo "[rdx-evloop] ${PL} job=${SLURM_JOB_ID} host=$(hostname) bin=${BIN} md5=${EXPECT_MD5} start=$(date -u +%FT%TZ)"
echo "[rdx-evloop] env: $(env | grep '^MNV101_' | sort | tr '\n' ' ')"
# the NuE exception (the director's ruling with cov2d's no-objection, 2026-11-12, term 3 and condition c): this
# file is read plainly, once, at the loop's initialisation; its atime_ns and mtime_ns are logged before and after
NUE="${CANON}/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt"
nue() { python3 -c "import os,sys,time; s=os.stat(sys.argv[1]); print('[rdx-evloop] NUE %s utc=%s atime_ns=%d mtime_ns=%d size=%d' % (sys.argv[2], time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), s.st_atime_ns, s.st_mtime_ns, s.st_size))" "${NUE}" "$1"; }
sq=$(squeue -h -u "${USER:-josephrb}" -o '%j|%T' 2>/dev/null) || { say "REFUSE: squeue failed"; exit 2; }
hit=$(printf '%s\n' "${sq}" | awk -F'|' '$1 ~ /^(cov2d|t2a|ll5d|e96data|rpd_|rsn_)/')
[[ -z "${hit}" ]] || { say "REFUSE: fenced jobs are queued or running (immediately before the binary): ${hit}"; exit 2; }
nue before
t0=$(date +%s)
"${BIN}" "${DATA}" "${MC}"; rc=$?
nue after
echo "[rdx-evloop] rc=${rc} elapsed=$(( $(date +%s) - t0 ))s"
[[ ${rc} -eq 0 && -s runEventLoopOmniFold.root ]] || exit 5
mv runEventLoopOmniFold.root "${OUT}.partial" && mv "${OUT}.partial" "${OUT}" && chmod 0440 "${OUT}"
echo "[rdx-evloop] wrote ${OUT} ($(stat -c '%s' "${OUT}") bytes) sha256 $(sha256sum "${OUT}" | cut -d' ' -f1)"
cd "${B}" && rm -rf -- "${WORK}"
