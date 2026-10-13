#!/bin/bash
#SBATCH --account=m3246
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --output=/pscratch/sd/j/josephrb/2d-closeout-stageC-pilot-20261013/logs/%x_%j.out
#SBATCH --error=/pscratch/sd/j/josephrb/2d-closeout-stageC-pilot-20261013/logs/%x_%j.err
# Stage C pilot job (AUTHORIZATION-20261013-2d-closeout-stageC-pilot.md and its binding addendum). Submitted only
# by launch.py, which applies the charge gate and passes --job-name/--qos/--cpus-per-task/--mem/--time from the
# frozen jobs.tsv. This script refuses unless its job name is one jobs.tsv row and the allocation Slurm granted
# (QOS, CPUs, TimeLimit) equals that row. Every path is absolute: sbatch runs a COPY of this script, so
# BASH_SOURCE/$0 do not name the package. No `set -u` before the root_6_28 activation.
set -eo pipefail
NS=/pscratch/sd/j/josephrb/2d-closeout-stageC-pilot-20261013
REPO=$NS/repo
PKG=$REPO/docs/orchestration/state/2d-closeout/stageC/pilot
D2=/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding
NAME=${SLURM_JOB_NAME:?no job name}

# ---- pins (DESIGN §2) --------------------------------------------------------------------------------------------
JOBS_SHA=54b0abcaff3da6256c3ba791ad55ab4c95a2c5b66bb88148f82c4fa522f4b9d8   # jobs.tsv
PROD_SHA=74a4ed69c3fa9c4ae5b6866f36343212b8d3f903fddde6c7bd40c382c1167d56     # production driver (main ec2088a6)
G2_SHA=eb258cadfc2b0ab7191e400eb13564a2866d393e18b830c3f2d5a7d12349cc99       # p2g2/driver_g2.py
P1_SHA=3056e625a22f2ee79621e515aa5a76a4685662ac6fc10ee7e832680dde087578     # p1/driver_p1.py
BUILD_SHA=7f346e1af1688b6a43be540ef2a8c6f8456d76a1ea965613abce17263739296b    # p2g2/build_miss_override.py (P5's)
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

# ---- this job's row and its allocation ---------------------------------------------------------------------------
echo "$JOBS_SHA  $PKG/jobs.tsv" | sha256sum -c -
ROW=$(awk -F'\t' -v n="$NAME" 'NR>1 && $1==n' "$PKG/jobs.tsv")
[ "$(printf '%s\n' "$ROW" | grep -c .)" = 1 ] || { echo "REFUSE: '$NAME' is not exactly one jobs.tsv row"; exit 4; }
IFS=$'\t' read -r R_NAME R_ITEM R_BATCH R_QOS R_CPUS R_MEM R_TIME R_BILL R_ENF R_AFTER R_WHAT <<< "$ROW"
JOBINFO=$(scontrol show job "$SLURM_JOB_ID")
G_QOS=$(grep -o 'QOS=[^ ]*' <<< "$JOBINFO" | head -1 | cut -d= -f2)
G_CPUS=$(grep -o 'NumCPUs=[^ ]*' <<< "$JOBINFO" | head -1 | cut -d= -f2)
G_TIME=$(grep -o 'TimeLimit=[^ ]*' <<< "$JOBINFO" | head -1 | cut -d= -f2)
[ "$G_QOS" = "$R_QOS" ] || { echo "REFUSE: QOS $G_QOS != $R_QOS"; exit 4; }
[ "$G_CPUS" = "$R_CPUS" ] || { echo "REFUSE: NumCPUs $G_CPUS != $R_CPUS"; exit 4; }
# The charge gate assumes billing = jobs.tsv billing (= CPUs at mem = 1905M x CPUs); refuse anything else.
G_BILL=$(grep -o 'AllocTRES=[^ ]*' <<< "$JOBINFO" | grep -o 'billing=[0-9]*' | head -1 | cut -d= -f2)
[ "$G_BILL" = "$R_BILL" ] || { echo "REFUSE: allocated billing '$G_BILL' != jobs.tsv billing $R_BILL"; exit 4; }
# A walltime retry carries its re-projected cap in $NS/retries/<name>.time (written by the executor, < 12 h).
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
echo "[pilot] $NAME item=$R_ITEM batch=$R_BATCH node=$(hostname) job=$SLURM_JOB_ID qos=$G_QOS cpus=$G_CPUS limit=$G_TIME start=$(date -u +%FT%TZ)"
echo "$PROD_SHA  $REPO/2d-unfolding/unfold_2d_omnifold_unbinned.py" | sha256sum -c -
echo "$HELPER_SHA  $HELPER" | sha256sum -c -
echo "$MCFILE_SHA  $MCFILE" | sha256sum -c -

uomni_check() {   # the 171 GB universe omnifile: hashed once on a DTN (preflight); the job checks it is that file
  [ -s "$UOMNI_STAT" ] || { echo "REFUSE: no preflight record $UOMNI_STAT"; exit 5; }
  [ "$(stat -c '%s %Y %i' "$UOMNI")" = "$(cat "$UOMNI_STAT")" ] || { echo "REFUSE: $UOMNI changed since preflight"; exit 5; }
  echo "$FLUXU_SHA  $FLUXU" | sha256sum -c -
}
# L0's argv (P0, P1 and P3 use it as is; --bkg-mode purity is its default, stated explicitly). Universe jobs add
# --verbose, as P5's runs did.
BASE=(--mcfile "$MCFILE" --iters 5 --use-weights --estimator lgbm --bkg-mode purity --out "$OUT/xsec.root")
UNIV=(--omnifile "$UOMNI" --flux-universe-file "$FLUXU" --verbose)
cd "$REPO/2d-unfolding"
case "$NAME" in
  2dc_C_P0_default) echo "$CVOMNI_SHA  $CVOMNI" | sha256sum -c -
    python3 unfold_2d_omnifold_unbinned.py --omnifile "$CVOMNI" "${BASE[@]}" --seed 42 --branch-select all ;;
  2dc_C_P0_derived) echo "$CVOMNI_SHA  $CVOMNI" | sha256sum -c -
    python3 unfold_2d_omnifold_unbinned.py --omnifile "$CVOMNI" "${BASE[@]}" --seed 42 --branch-select derived ;;
  2dc_C_P2_NormDISCC0|2dc_C_P2_MaRES0|2dc_C_P2_Flux23|2dc_C_P2_MINOS0|2dc_C_P2_MINOS0def|2dc_C_G2_off_s43)
    uomni_check
    case "$NAME" in
      *NormDISCC0) U=NormDISCC:0;; *MaRES0) U=MaRES:0;; *Flux23|*G2_off_s43) U=Flux:23;; *) U=Muon_Energy_MINOS:0;;
    esac
    SEED=42; [ "$NAME" = 2dc_C_G2_off_s43 ] && SEED=43
    SEL=derived; [ "$NAME" = 2dc_C_P2_MINOS0def ] && SEL=all
    python3 unfold_2d_omnifold_unbinned.py "${UNIV[@]}" "${BASE[@]}" --universe "$U" --seed "$SEED" --branch-select "$SEL" ;;
  2dc_C_G2_on|2dc_C_G2_on_s43)
    uomni_check
    echo "$G2_SHA  $REPO/2d-unfolding/driver_g2.py" | sha256sum -c -
    OVN=$NS/out/2dc_C_G2_override/override_Flux_23.npz; OVJ=$NS/out/2dc_C_G2_override/override_Flux_23.json
    SEED=42
    if [ "$NAME" = 2dc_C_G2_on ]; then
      # A G2_on retry rebuilds the override: the executor moves out/2dc_C_G2_override/ aside (sha-verified) with
      # out/2dc_C_G2_on/ before resubmitting (DESIGN §9), so an existing override here is a refusal.
      for f in "$OVN" "$OVJ"; do [ -e "$f" ] && { echo "REFUSE: $f exists"; exit 3; }; done
      mkdir -p "$(dirname "$OVN")"
      echo "$BUILD_SHA  $PKG/p2g2/build_miss_override.py" | sha256sum -c -
      BLOCKS=(); for p in 1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P; do BLOCKS+=("$D2/runEventLoopOmniFold_${p}_universes_full.root"); done
      python3 "$PKG/p2g2/build_miss_override.py" --omnifile "$UOMNI" --blocks "${BLOCKS[@]}" --universe Flux:23 \
          --out "$OVN" --report "$OVJ"
      (cd "$(dirname "$OVN")" && sha256sum "$(basename "$OVN")" > "$(basename "$OVN").sha256")
    else
      SEED=43
      (cd "$(dirname "$OVN")" && sha256sum -c "$(basename "$OVN").sha256")   # the seed-42 override, unchanged
    fi
    python3 driver_g2.py "${UNIV[@]}" "${BASE[@]}" --universe Flux:23 --seed "$SEED" --branch-select derived \
        --miss-weight-override "$OVN" ;;
  2dc_C_P3_BeamAngleX0|2dc_C_P3_MINOS0)
    case "$NAME" in *BeamAngleX0) U=BeamAngleX_0;; *) U=Muon_Energy_MINOS_0;; esac
    F=$ACT/runEventLoopOmniFold_5D_MEFHC_active_${U}.root
    WANT=$(awk -v f="runEventLoopOmniFold_5D_MEFHC_active_${U}.root" '$2==f{print $1}' "$ACT/SHA256SUMS")
    [ ${#WANT} = 64 ] || { echo "REFUSE: no SHA256SUMS row for $U"; exit 5; }
    echo "$WANT  $F" | sha256sum -c -
    python3 unfold_2d_omnifold_unbinned.py --omnifile "$F" "${BASE[@]}" --seed 42 --branch-select all ;;
  2dc_C_P1_unit|2dc_C_P1_fixed_*|2dc_C_P1_joint_*|2dc_C_P1_bkg_*)
    echo "$CVOMNI_SHA  $CVOMNI" | sha256sum -c -
    if [ "$NAME" = 2dc_C_P1_unit ]; then
      echo "$P1_SHA  $REPO/2d-unfolding/driver_p1.py" | sha256sum -c -
      python3 driver_p1.py --omnifile "$CVOMNI" "${BASE[@]}" --seed 42 --bootstrap-seed 1 --bootstrap-streams three --unit-factors
    else
      ARM=$(cut -d_ -f4 <<< "$NAME"); N=$((10#$(cut -d_ -f5 <<< "$NAME")))
      case "$ARM" in
        fixed) python3 unfold_2d_omnifold_unbinned.py --omnifile "$CVOMNI" "${BASE[@]}" --seed 42 --bootstrap-seed "$N" ;;
        joint|bkg) echo "$P1_SHA  $REPO/2d-unfolding/driver_p1.py" | sha256sum -c -
          STREAMS=three; [ "$ARM" = bkg ] && STREAMS=bkg
          python3 driver_p1.py --omnifile "$CVOMNI" "${BASE[@]}" --seed 42 --bootstrap-seed "$N" --bootstrap-streams "$STREAMS" ;;
        *) echo "REFUSE: arm $ARM"; exit 4;;
      esac
    fi ;;
  *) echo "REFUSE: no command for $NAME"; exit 4;;
esac
sha256sum "$OUT/xsec.root"
echo "[pilot] done $NAME $(date -u +%FT%TZ)"
