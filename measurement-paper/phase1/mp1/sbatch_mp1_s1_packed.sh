#!/bin/bash
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
# MP1-A S1, packed: every not-yet-done (variant, playlist) pass of the given playlists, run concurrently on ONE node,
# each through the per-pass launcher sbatch_mp1_s1_evloop.sh (unique work directory per process, refuse-to-overwrite).
#   sbatch --time=<limit> --job-name=mp1s1_pack_<tag> --output=<NS>/logs/%x_%j.out sbatch_mp1_s1_packed.sh \
#          <NS> <tools> <mem per pass, e.g. 14G> <variants: comma list or "all"> <PL> [<PL> ...]
# A pass is skipped if its output exists or a shared copy is still PENDING/RUNNING under its job name (cancel the
# shared copy first to move it). Each pass is one `srun --exclusive -n1 -c1 --mem=<mem>` step, so sacct records
# per-pass ElapsedRaw and MaxRSS.
set -o pipefail   # NOT set -u
NS="${1:?ns}"; TOOLS="${2:?tools}"; MEM="${3:?mem per pass}"; VLIST="${4:?variants}"; shift 4
[[ $# -ge 1 ]] || { echo "[pack] no playlists"; exit 2; }
L="${TOOLS}/measurement-paper/phase1/mp1/sbatch_mp1_s1_evloop.sh"
BIN=/pscratch/sd/j/josephrb/measurement-paper/phase1/mp1/s0/build/bld_mod/runEventLoopOmniFold
MD5=15b4789fbd8e9c1fc5aeb14c1b4626b0
(cd "${TOOLS}" && sha256sum --quiet -c TOOLS.sha256) || { echo "[pack] ABORT: tool digests"; exit 2; }
[[ "${VLIST}" == all ]] && VLIST="zero,proton_m1,proton_p1,meson_m1,meson_p1,em_m1,em_p1,other_m1,other_p1,xtalk_m1,xtalk_p1"
pids=()
for pl in "$@"; do
  for v in ${VLIST//,/ }; do
    out="${NS}/evloop/${v}/runEventLoopOmniFold_5D_${pl}_${v}.root"
    [[ -e "${out}" ]] && { echo "[pack] ${v} ${pl}: output exists, skip"; continue; }
    if squeue -u "$USER" -h -o "%j %T" | grep -q "^mp1s1_${v}_${pl} \(PENDING\|RUNNING\)"; then
      echo "[pack] ${v} ${pl}: a shared copy is queued or running, skip"; continue; fi
    srun --exclusive -n1 -c1 --mem="${MEM}" --job-name="mp1s1_${v}_${pl}" \
      bash "${L}" "${NS}" "${v}" "${pl}" "${BIN}" "${MD5}" fprop prorata "${NS}/g0/F_${pl}.txt" \
      > "${NS}/logs/pack_${SLURM_JOB_ID}_${v}_${pl}.out" 2>&1 &
    pids+=($!); echo "[pack] started ${v} ${pl} (pid $!)"
  done
done
rc=0; for p in "${pids[@]}"; do wait "$p" || rc=1; done
echo "[pack] ${#pids[@]} passes done, rc=${rc}"
exit ${rc}
