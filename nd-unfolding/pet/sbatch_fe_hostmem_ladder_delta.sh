#!/bin/bash
#SBATCH --job-name=fe_hostmem
#SBATCH --account=bhvk-delta-cpu
#SBATCH --partition=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=220g
#SBATCH --time=04:00:00
#SBATCH --output=fe_hostmem_%j.out
#SBATCH --error=fe_hostmem_%j.err
# ============================================================================
# HOST-MEMORY LADDER for build_fullevent_loaders (Gate-4 / P5A launch risk).
#
# WHY: fullevent_fps_dataloader.py:520-521 materializes the FULL signal array
# before [imc] subsamples it, build_truth_cloud stacks to (n,12,8) through
# several full-size temporaries, and rank/size only reach the DataLoader at
# :612 -- AFTER the clouds are built. So under -np 4 every rank holds a full
# copy. A hand estimate put the per-rank peak near 78 GiB at max_events=40M
# => ~310 GiB across 4 ranks against a 251.6 GiB node. If that is right, P5A
# OOMs on launch and the fix is a code change (shard before build / chunked
# construction / a full-event memmap builder that does not exist yet).
#
# MEASURED (Delta 20558496, 2026-07-28): that hand estimate was ~25% HIGH --
# the full-size temporaries in build_truth_cloud do not all coexist. Fit was
# peak_GiB = 1.238e-6*rows + 0.239 => ~61 GiB/rank, ~246 GiB over 4 ranks
# against 251.6 GiB (~98% of the node). Hard OOM refuted; the margin is ~2-3%.
# This was a CPU node, so it EXCLUDES the host memory each rank pins for its
# CUDA context and TF's allocator: treat ~246 GiB as a LOWER BOUND.
#
# This measures it instead of arguing about it, on CPU hours, so the 814
# remaining GPU-hours are not spent extrapolating wall-clock for a
# configuration that cannot run.
#
# TOKENS=12 ON PURPOSE. make_synthetic_g2_fullevent.py defaults --tokens 40,
# but the real dump's part_gen/part_reco carry 12 slots (verified from
# G2_FPS_MEFHC_P12_RECEIPT.json member_headers). A 40-token fixture is ~3.3x
# too wide per event and would badly overstate the memory.
#
# NOT A PHYSICS RUN. Random fixtures, and the container has no ROOT so the
# canonical Stay-Positive refiner is unavailable -- the ROOT-free sklearn shim
# is injected and the telemetry self-reports
# refinement_is_learned_production=False. Memory only; never publication
# evidence.
# ============================================================================
set -eo pipefail

REPO="${REPO:-$HOME/MINERvA-OmniFold}"
source "${REPO}/lib/resume_guard.sh"   # BEN-023: resume on a completion marker, not on size
SIF="${SIF:-$HOME/tf215.sif}"                  # NOTE: filename says 215, contents are TF 2.14.0
WORK="${WORK:-/work/nvme/bhvk/$USER/hostmem}"
# First rung is a deliberately tiny self-validation: the whole path (fixture ->
# schema gates -> clouds -> refinement -> DataLoader) either works in ~2 minutes or
# the job tells you so before it spends hours. Do not drop it.
RUNGS="${RUNGS:-200000 2000000 5000000 10000000 20000000}"
TOKENS="${TOKENS:-12}"
KEEP_FIXTURES="${KEEP_FIXTURES:-0}"            # 1 = keep (tens of GB); 0 = delete after each rung

mkdir -p "${WORK}"
cd "${REPO}/nd-unfolding/pet"
# UCX_LOG_LEVEL: omnifold pulls in horovod, whose UCX/IB init emits hundreds of
# "GID table change" WARN lines that bury the actual measurement output.
# THREAD PINNING is not cosmetic here. The 2026-07-28 login-node attempt burned
# 2h35m of CPU in 10 minutes of wall on a 60k-row fixture before NCSA's watchdog
# killed it -- the signature of TF sizing its intra-op pool to the visible core
# count (128) and spin-waiting on tiny arrays, not of a starved process. Without
# these the ladder can burn its whole time limit making no progress.
NTHREADS="${SLURM_CPUS_PER_TASK:-16}"
RUN="apptainer exec --bind ${REPO},${WORK} \
     --env PYTHONPATH=${REPO}/omnifold_nn \
     --env UCX_LOG_LEVEL=error \
     --env TF_CPP_MIN_LOG_LEVEL=2 \
     --env OMPI_MCA_btl_base_warn_component_unused=0 \
     --env OMP_NUM_THREADS=${NTHREADS} \
     --env OPENBLAS_NUM_THREADS=${NTHREADS} \
     --env MKL_NUM_THREADS=${NTHREADS} \
     --env TF_NUM_INTRAOP_THREADS=${NTHREADS} \
     --env TF_NUM_INTEROP_THREADS=2 ${SIF}"

echo "[hostmem] $(date -u +%FT%TZ) start on $(hostname)"
echo "[hostmem] commit $(cd ${REPO} && git rev-parse --short HEAD)"
echo "[hostmem] node memory: $(free -g | awk '/^Mem:/{print $2" GiB"}')"
echo "[hostmem] rungs: ${RUNGS} tokens=${TOKENS}"

for N_SIG in ${RUNGS}; do
    # data/bkg scaled to the real G2 inventory ratios (4116128 and 564591 of 49152885)
    N_DATA=$(python3 -c "print(int(round(${N_SIG}*4116128/49152885)))")
    N_BKG=$(python3 -c "print(int(round(${N_SIG}*564591/49152885)))")
    TAG="n${N_SIG}"
    FIX="${WORK}/G2_SYNTH_${TAG}_t${TOKENS}.npz"
    OUT="${WORK}/rung_${TAG}.json"

    echo "[hostmem] ---- rung ${TAG}: sig=${N_SIG} data=${N_DATA} bkg=${N_BKG} ----"

    if rg_is_complete "${FIX}"; then
        echo "[hostmem] fixture exists, reusing: ${FIX}"
    else
        echo "[hostmem] generating fixture (compressed npz; this is the slow part)"
        rg_run "${FIX}" /usr/bin/time -v ${RUN} python3 make_synthetic_g2_fullevent.py \
            --out "${FIX}" --n-sig "${N_SIG}" --n-data "${N_DATA}" --n-bkg "${N_BKG}" \
            --tokens "${TOKENS}" --seed 0 \
            --receipt "${FIX%.npz}_RECEIPT.json" 2>&1 | grep -E "Maximum resident|Elapsed|^\[" || true
    fi
    ls -l "${FIX}" || true

    echo "[hostmem] measuring peak RSS"
    # Do not abort the ladder on one rung: an OOM/guard failure at a big rung IS a result.
    ${RUN} python3 measure_fullevent_host_memory.py \
        --fixture "${FIX}" --rows "${N_SIG}" --out "${OUT}" || \
        echo "[hostmem] rung ${TAG} exited nonzero (see ${OUT})"

    if [ "${KEEP_FIXTURES}" != "1" ]; then
        rm -f "${FIX}" "${FIX%.npz}_RECEIPT.json"
        echo "[hostmem] fixture deleted (KEEP_FIXTURES=1 to retain)"
    fi
done

echo "[hostmem] ---- ladder summary ----"
${RUN} python3 - "${WORK}" <<'PY'
import glob, json, os, sys
rows, peaks = [], []
for p in sorted(glob.glob(os.path.join(sys.argv[1], "rung_n*.json")),
                key=lambda p: json.load(open(p))["rows_signal"]):
    r = json.load(open(p))
    flag = "" if not r["error"] else f"  ERROR: {r['error'][:70]}"
    print(f"  rows={r['rows_signal']:>10,}  max_events={r['max_events']:>10,}  "
          f"peak={r['peak_rss_gib']:7.2f} GiB  4-rank={r['projected_4rank_node_gib']:7.1f} GiB{flag}")
    if not r["error"]:
        rows.append(r["rows_signal"]); peaks.append(r["peak_rss_gib"])

if len(rows) >= 2:
    # least-squares straight line; memory should be affine in rows
    n = len(rows); sx = sum(rows); sy = sum(peaks)
    sxx = sum(x * x for x in rows); sxy = sum(x * y for x, y in zip(rows, peaks))
    slope = (n * sxy - sx * sy) / (n * sxx - sx * sx)
    icept = (sy - slope * sx) / n
    cap = 257630.0 / 1024.0
    print(f"\n  fit: peak_GiB = {slope:.6e} * rows + {icept:.3f}")
    # The fit's x-axis is rows_signal, so these targets are ROW counts, not
    # max_events. The production point is the full dump (49,152,885 rows), which
    # is max_events = 40M via the 0.8138 pass-reco ratio -- the two are the same
    # point, so do not read the first line as "the 40M-max_events case".
    for target, label in ((40_000_000, "rows=40M"), (49_152_885, "full dump, 49.15M rows")):
        one = slope * target + icept
        print(f"  extrapolated {label:22s}: 1 rank {one:7.2f} GiB | "
              f"4 ranks {4*one:7.1f} GiB | node {cap:.1f} GiB | "
              f"{'EXCEEDS -- P5A OOMs at -np 4' if 4*one > cap else 'fits'}")
    print("\n  Extrapolation, not measurement. Confirm the 4x factor with a real "
          "4-rank run at a small rung before acting on it.")
else:
    print("\n  too few successful rungs to fit")
PY

echo "[hostmem] done $(date -u +%FT%TZ)"
