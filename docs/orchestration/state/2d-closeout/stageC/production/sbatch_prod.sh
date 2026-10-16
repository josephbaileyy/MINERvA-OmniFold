#!/bin/bash
# Stage C production member runner (AUTHORIZATION-20261015-2d-closeout-stageC-production.md, its binding addendum,
# and AUTHORIZATION-20261016-2d-closeout-stageC-regular-packing.md; DESIGN §14). Runs ONE jobs.tsv row ("member")
# as an `srun --exact` step of a regular-QOS pack started by sbatch_pack.sh; never submitted with sbatch itself.
# The member's identity is its explicit `--member <name>` argument, never SLURM_JOB_NAME (the pack's name). It
# refuses unless that name is one jobs.tsv row, the step got exactly the row's CPUs and memory, and the pack's
# allocation is QOS regular with billing 256 and TimeLimit = the row's cap (or its retry record). Every path is
# absolute. No `set -u` before the root_6_28 activation. The command lines are the shared-QOS path's, unchanged
# (adapted from the pilot's sbatch_pilot.sh, stageC/pilot v2 a2ea0d6a).
set -eo pipefail
NS=/pscratch/sd/j/josephrb/2d-closeout-stageC-production-20261015
REPO=$NS/repo_k
PKG=$REPO/docs/orchestration/state/2d-closeout/stageC/production
D2=/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding
[ "${1:-}" = --member ] && [ -n "${2:-}" ] || { echo "REFUSE: usage: sbatch_prod.sh --member <jobs.tsv name>"; exit 4; }
NAME=$2
case "${SLURM_STEP_ID:-}" in ''|batch|extern) echo "REFUSE: run only as an srun step of sbatch_pack.sh"; exit 4;; esac
PACK_BILLING=256   # QOS: `--qos=regular` is recorded as regular_1 (or regular_0)

# ---- pins (DESIGN §2) --------------------------------------------------------------------------------------------
JOBS_SHA=c4f1b7082fac3635be78622cb9b9a5f71103789337bbc29e7dd29684e9b4d3a4   # jobs.tsv
PROD_SHA=74a4ed69c3fa9c4ae5b6866f36343212b8d3f903fddde6c7bd40c382c1167d56     # production driver (grant §1)
P1_SHA=3056e625a22f2ee79621e515aa5a76a4685662ac6fc10ee7e832680dde087578       # stageC/pilot/p1/driver_p1.py
HELPER=/pscratch/sd/j/josephrb/MINERvA-OmniFold/unbinned_unfolding/python/omnifold.py
HELPER_SHA=e96234124a31edd7a8dd61fdb16cb48a5b28cbd1b90202f59b0095868378227a
CVOMNI=/global/cfs/cdirs/m3246/josephrb/two-d-followup-20261010/xr-input/runEventLoopOmniFold_MEFHC.root
CVOMNI_SHA=43f8cc16ab2688200d3e2e0ebb48012b23ada6d7882b8c68ecfc51c609aeb8df
MCFILE=$D2/baseline_flux/runEventLoopMC_MEFHC.root
MCFILE_SHA=d40aea69235cdc98644e1bb3e622e579d6b81904c004c83fe50465079989f316
FLUXU=$D2/baseline_flux/flux_integral_universes_MEFHC.root
FLUXU_SHA=5eecae84509ba8ededbe8fdee63508d8e36cd057cc0547a940383f80248580eb
UOMNI=$D2/runEventLoopOmniFold_MEFHC_universes_full.root                     # 171,117,087,867 B, sha256 220c479e...
UOMNI_STAT=$NS/preflight/uomni.stat                                           # size+mtime+inode from the DTN hash
ACT=/global/cfs/cdirs/m3246/josephrb/2d-closeout-stageC-inputs-20261012/active_universe_5d_standard_merged
ACT_SUMS_SHA=73775251f377a35b86c5d9433d1db63d65267525b9261f773064a1e9d17764f6  # $ACT/SHA256SUMS

# ---- this job's row and its allocation ---------------------------------------------------------------------------
echo "$JOBS_SHA  $PKG/jobs.tsv" | sha256sum -c -
ROW=$(awk -F'\t' -v n="$NAME" 'NR>1 && $1==n' "$PKG/jobs.tsv")
[ "$(printf '%s\n' "$ROW" | grep -c .)" = 1 ] || { echo "REFUSE: '$NAME' is not exactly one jobs.tsv row"; exit 4; }
IFS=$'\t' read -r R_NAME R_ITEM R_BATCH R_QOS R_CPUS R_MEM R_TIME R_BILL R_ENF R_AFTER R_WHAT <<< "$ROW"
JOBINFO=$(scontrol show job "$SLURM_JOB_ID")
G_QOS=$(grep -o 'QOS=[^ ]*' <<< "$JOBINFO" | head -1 | cut -d= -f2)
G_TIME=$(grep -o 'TimeLimit=[^ ]*' <<< "$JOBINFO" | head -1 | cut -d= -f2)
case "$G_QOS" in regular|regular_0|regular_1) ;; *) echo "REFUSE: QOS $G_QOS is not regular (regular, regular_0, regular_1)"; exit 4;; esac
# The charge gate counts the pack at billing 256 (one node); refuse anything else.
G_BILL=$(grep -o 'AllocTRES=[^ ]*' <<< "$JOBINFO" | grep -o 'billing=[0-9]*' | head -1 | cut -d= -f2)
[ "$G_BILL" = "$PACK_BILLING" ] || { echo "REFUSE: allocated billing '$G_BILL' != pack billing $PACK_BILLING"; exit 4; }
# The step must hold exactly this row's CPUs (srun --exact -c <cpus> --mem <mem>); the step's TRES is logged.
[ "${SLURM_CPUS_PER_TASK:-}" = "$R_CPUS" ] || { echo "REFUSE: step CPUs '${SLURM_CPUS_PER_TASK:-}' != $R_CPUS"; exit 4; }
G_CPUS=$SLURM_CPUS_PER_TASK
echo "[prod] step $SLURM_JOB_ID.$SLURM_STEP_ID $(scontrol show step "$SLURM_JOB_ID.$SLURM_STEP_ID" 2>/dev/null | grep -o 'TRES=[^ ]*' | head -1) row mem=$R_MEM"
# A walltime retry carries its re-projected cap in $NS/retries/<name>.time (written by launch.py, < 12 h).
WANT_TIME=$R_TIME; [ -f "$NS/retries/$NAME.time" ] && WANT_TIME=$(cat "$NS/retries/$NAME.time")
[ "$G_TIME" = "$WANT_TIME" ] || { echo "REFUSE: TimeLimit $G_TIME != $WANT_TIME"; exit 4; }

OUT=$NS/out/$NAME
if [ -e "$OUT/xsec.root" ]; then echo "REFUSE: $OUT/xsec.root exists"; exit 3; fi
mkdir -p "$OUT"
# A retry starts clean: any partial output of the failed attempt was moved aside by the executor.
[ -z "$(ls -A "$OUT")" ] || { echo "REFUSE: $OUT is not empty"; exit 3; }

source /pscratch/sd/j/josephrb/MINERvA-OmniFold/setup_salloc_env.sh
export TMPDIR=$NS/tmp; mkdir -p "$TMPDIR"
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=64 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
unset LOKY_MAX_CPU_COUNT
echo "[prod] $NAME item=$R_ITEM batch=$R_BATCH node=$(hostname) job=$SLURM_JOB_ID step=$SLURM_STEP_ID pack=${SLURM_JOB_NAME:-} qos=$G_QOS cpus=$G_CPUS limit=$G_TIME start=$(date -u +%FT%TZ)"
echo "$PROD_SHA  $REPO/2d-unfolding/unfold_2d_omnifold_unbinned.py" | sha256sum -c -
echo "$HELPER_SHA  $HELPER" | sha256sum -c -
echo "$MCFILE_SHA  $MCFILE" | sha256sum -c -

uomni_check() {   # the 171 GB universe omnifile: hashed once on a DTN (preflight); the job checks it is that file
  [ -s "$UOMNI_STAT" ] || { echo "REFUSE: no preflight record $UOMNI_STAT"; exit 5; }
  [ "$(stat -c '%s %Y %i' "$UOMNI")" = "$(cat "$UOMNI_STAT")" ] || { echo "REFUSE: $UOMNI changed since preflight"; exit 5; }
  echo "$FLUXU_SHA  $FLUXU" | sha256sum -c -
}
p1_check() { echo "$P1_SHA  $REPO/2d-unfolding/driver_p1.py" | sha256sum -c -; }
cv_check() { echo "$CVOMNI_SHA  $CVOMNI" | sha256sum -c -; }
# L0's argv (--bkg-mode purity is its default, stated explicitly), as the pilot ran it. Universe jobs add
# --verbose, as the pilot's P2 runs did.
BASE=(--mcfile "$MCFILE" --iters 5 --use-weights --estimator lgbm --bkg-mode purity --out "$OUT/xsec.root")
UNIV=(--omnifile "$UOMNI" --flux-universe-file "$FLUXU" --verbose)
cd "$REPO/2d-unfolding"
case "$NAME" in
  2dc_P_C0_unit) cv_check; p1_check
    python3 driver_p1.py --omnifile "$CVOMNI" "${BASE[@]}" --seed 42 --bootstrap-seed 1 --bootstrap-streams three --unit-factors ;;
  2dc_P_C0_cv) cv_check
    python3 unfold_2d_omnifold_unbinned.py --omnifile "$CVOMNI" "${BASE[@]}" --seed 42 --branch-select all ;;
  2dc_P_S4CV_s*) cv_check
    SEED=${NAME##*_s}
    python3 unfold_2d_omnifold_unbinned.py --omnifile "$CVOMNI" "${BASE[@]}" --seed "$SEED" --branch-select all ;;
  2dc_P_S3_*)
    case "${NAME#2dc_P_S3_}" in
      BeamAngleX0) U=BeamAngleX_0;; BeamAngleX1) U=BeamAngleX_1;; BeamAngleY0) U=BeamAngleY_0;; BeamAngleY1) U=BeamAngleY_1;;
      MuonResolution0) U=MuonResolution_0;; MuonResolution1) U=MuonResolution_1;;
      MuonEnergyMINERvA0) U=Muon_Energy_MINERvA_0;; MuonEnergyMINERvA1) U=Muon_Energy_MINERvA_1;;
      MuonEnergyMINOS0) U=Muon_Energy_MINOS_0;; MuonEnergyMINOS1) U=Muon_Energy_MINOS_1;;
      *) echo "REFUSE: no lateral for $NAME"; exit 4;;
    esac
    echo "$ACT_SUMS_SHA  $ACT/SHA256SUMS" | sha256sum -c -
    F=$ACT/runEventLoopOmniFold_5D_MEFHC_active_${U}.root
    WANT=$(awk -v f="runEventLoopOmniFold_5D_MEFHC_active_${U}.root" '$2==f{print $1}' "$ACT/SHA256SUMS")
    [ ${#WANT} = 64 ] || { echo "REFUSE: no SHA256SUMS row for $U"; exit 5; }
    echo "$WANT  $F" | sha256sum -c -
    python3 unfold_2d_omnifold_unbinned.py --omnifile "$F" "${BASE[@]}" --seed 42 --branch-select all ;;
  2dc_P_S4U_*)
    uomni_check
    T=${NAME#2dc_P_S4U_}; SEED=${T##*_s}; T=${T%_s*}
    case "$T" in
      NormDISCC0) U=NormDISCC:0;; Flux23) U=Flux:23;; MaRES0) U=MaRES:0;; MaCCQE0) U=MaCCQE:0;; 2p2h0) U=2p2h:0;;
      MinosEfficiency0) U=MinosEfficiency:0;; Muon_Energy_MINOS0) U=Muon_Energy_MINOS:0;;
      *) echo "REFUSE: no universe for $NAME"; exit 4;;
    esac
    python3 unfold_2d_omnifold_unbinned.py "${UNIV[@]}" "${BASE[@]}" --universe "$U" --seed "$SEED" --branch-select derived ;;
  2dc_P_S1_*|2dc_P_S2_*)
    cv_check; p1_check
    N=$((10#${NAME##*_})); STREAMS=three; [ "${NAME:0:9}" = 2dc_P_S2_ ] && STREAMS=bkg
    python3 driver_p1.py --omnifile "$CVOMNI" "${BASE[@]}" --seed 42 --bootstrap-seed "$N" --bootstrap-streams "$STREAMS" ;;
  2dc_P_S4B_s*)
    cv_check; p1_check
    T=${NAME#2dc_P_S4B_s}; SEED=${T%%_*}; N=$((10#${T##*_}))
    python3 driver_p1.py --omnifile "$CVOMNI" "${BASE[@]}" --seed "$SEED" --bootstrap-seed "$N" --bootstrap-streams three ;;
  *) echo "REFUSE: no command for $NAME"; exit 4;;
esac
sha256sum "$OUT/xsec.root"
echo "[prod] done $NAME $(date -u +%FT%TZ)"
