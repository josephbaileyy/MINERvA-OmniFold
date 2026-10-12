#!/bin/bash
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=128
#SBATCH --time=01:30:00
#SBATCH --output=/pscratch/sd/j/josephrb/2d-closeout-stageB-diag-20261012/p5/out/%x_%j.out
#SBATCH --error=/pscratch/sd/j/josephrb/2d-closeout-stageB-diag-20261012/p5/out/%x_%j.err
# P5 (G2 miss-row universe weights), grant AUTHORIZATION-20261012-2d-closeout-stageB-diagnostics.md.
# One vertical universe, MaRES:0, two runs on the July universe omnifile with identical options:
#   sbatch --job-name=2dc_B5_off                   sbatch_p5.sh off      production driver (6be77c51...)
#   sbatch --job-name=2dc_B5_on --time=02:00:00    sbatch_p5.sh on       build_miss_override.py, then driver_p5.py
# Caps re-priced 2026-10-12 before any P5 job ran (AUTHORIZATION-20261012-2d-closeout-stageB-p4-retry.md, P5 walltime
# check): 1.5 x a full-read universe unfold (max 2,738 s) -> off 1:30; plus the override build -> on 2:00.
# Conditional seed-43 pair (DESIGN §7: only if seed 42 routes MATERIAL or NOT RESOLVED, after a budget check and the
# director's go-ahead; it reuses the seed-42 override, verified by sha256):
#   sbatch --job-name=2dc_B5_off_s43                sbatch_p5.sh off 43
#   sbatch --job-name=2dc_B5_on_s43 --time=02:00:00 sbatch_p5.sh on 43
# Mode and seed are positional arguments (sbatch --export cannot carry commas). Every path is absolute: sbatch runs a
# COPY of this script, so BASH_SOURCE/$0 do not name the package. No `set -u` before the root_6_28 activation.
set -eo pipefail
MODE=${1:?mode off|on}
SEED=${2:-42}
case "$MODE" in off|on) ;; *) echo "REFUSE: mode $MODE"; exit 2;; esac
case "$SEED" in 42) TAG="";; 43) TAG="_s43";; *) echo "REFUSE: seed $SEED"; exit 2;; esac
[ "${SLURM_JOB_NAME:-}" = "2dc_B5_${MODE}${TAG}" ] || { echo "REFUSE: job name '${SLURM_JOB_NAME:-}' != 2dc_B5_${MODE}${TAG}"; exit 4; }
WANT_LIMIT=01:30:00; [ "$MODE" = on ] && WANT_LIMIT=02:00:00
LIMIT=$(scontrol show job "$SLURM_JOB_ID" | grep -o 'TimeLimit=[^ ]*' | cut -d= -f2)
[ "$LIMIT" = "$WANT_LIMIT" ] || { echo "REFUSE: TimeLimit $LIMIT != $WANT_LIMIT"; exit 4; }

NS=/pscratch/sd/j/josephrb/2d-closeout-stageB-diag-20261012/p5
REPO=$NS/repo
D2=/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding
OMNI=$D2/runEventLoopOmniFold_MEFHC_universes_full.root
FLUX=$D2/baseline_flux/runEventLoopMC_MEFHC.root
HELPER=/pscratch/sd/j/josephrb/MINERvA-OmniFold/unbinned_unfolding/python/omnifold.py
UNI=MaRES:0
OUT=$NS/out/xsec_MaRES_0_${MODE}${TAG}.root
OVN=$NS/out/override_MaRES_0.npz
OVJ=$NS/out/override_MaRES_0.json
PROD_SHA=6be77c51805547bac2d864ce77c7bc636607cf43194bd2f4ad1a7c14db621257
DIAG_SHA=f71b5759bf01422fa8c6b6e5432885b34d1f127653df1165a0adb7527bdb12d2   # driver_p5.py
BUILD_SHA=7f346e1af1688b6a43be540ef2a8c6f8456d76a1ea965613abce17263739296b  # build_miss_override.py
HELPER_SHA=e96234124a31edd7a8dd61fdb16cb48a5b28cbd1b90202f59b0095868378227a # omnifold.py, the driver's _OF_PY import
[ -e "$OUT" ] && { echo "REFUSE: $OUT exists"; exit 3; }
if [ "$MODE" = on ] && [ "$SEED" = 42 ]; then
  for f in "$OVN" "$OVJ" "$OVN.sha256"; do [ -e "$f" ] && { echo "REFUSE: $f exists"; exit 3; }; done
fi

source /pscratch/sd/j/josephrb/MINERvA-OmniFold/setup_salloc_env.sh
export TMPDIR=$NS/tmp; mkdir -p "$TMPDIR"
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=64      # L0's 64 LightGBM threads
echo "[p5] mode=$MODE seed=$SEED node=$(hostname) job=$SLURM_JOB_ID start=$(date -u +%FT%TZ)"
echo "$PROD_SHA  $REPO/2d-unfolding/unfold_2d_omnifold_unbinned.py" | sha256sum -c -
echo "$DIAG_SHA  $REPO/2d-unfolding/driver_p5.py" | sha256sum -c -
echo "$BUILD_SHA  $NS/scripts/build_miss_override.py" | sha256sum -c -
echo "$HELPER_SHA  $HELPER" | sha256sum -c -
ls -l "$OMNI"   # 171,117,087,867 B (sha256 220c479e..., Stage B); not re-hashed per job

COMMON=(--omnifile "$OMNI" --mcfile "$FLUX" --iters 5 --use-weights --estimator lgbm --seed "$SEED"
        --bkg-mode purity --universe "$UNI" --branch-select derived --verbose --out "$OUT")
cd "$REPO/2d-unfolding"
if [ "$MODE" = off ]; then
  python3 unfold_2d_omnifold_unbinned.py "${COMMON[@]}"
else
  if [ "$SEED" = 42 ]; then
    BLOCKS=()
    for p in 1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P; do BLOCKS+=("$D2/runEventLoopOmniFold_${p}_universes_full.root"); done
    python3 "$NS/scripts/build_miss_override.py" --omnifile "$OMNI" --blocks "${BLOCKS[@]}" --universe "$UNI" \
        --out "$OVN" --report "$OVJ"
    (cd "$NS/out" && sha256sum "$(basename "$OVN")" > "$(basename "$OVN").sha256")
  else
    (cd "$NS/out" && sha256sum -c "$(basename "$OVN").sha256")   # the seed-42 override, unchanged
  fi
  python3 driver_p5.py "${COMMON[@]}" --miss-weight-override "$OVN"
fi
sha256sum "$OUT"
echo "[p5] done $(date -u +%FT%TZ)"
