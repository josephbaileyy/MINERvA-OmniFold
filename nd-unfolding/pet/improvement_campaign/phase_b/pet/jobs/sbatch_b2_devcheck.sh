#!/bin/bash
# Task B2 mechanics check on one debug node (4 GPUs), tuning stage, 100k events:
#   GPU0 unfold 2 it x 2 ep, continuous          GPU1 the same, stopped after it 0, then resumed
#   GPU2 unfold with every B2 input transform    GPU3 truth-only mode, raw PDG then T2 transforms
# then checks that the resumed run's iteration files equal the continuous run's, bit for bit.
#SBATCH --account=m3246_g
#SBATCH --constraint=gpu
#SBATCH --qos=debug
#SBATCH --nodes=1
#SBATCH --gpus=4
#SBATCH --time=00:30:00
#SBATCH --job-name=pb2-dev
set -eo pipefail
: "${MINE:?}" ; : "${MINE_COMMIT:?}" ; : "${OUT:?}"
INPUTS=/global/cfs/cdirs/m3246/josephrb/minerva-shutdown-stage/g2_input/G2_FPS_MEFHC_P12.npz
SIDECAR=/pscratch/sd/j/josephrb/event-identity-audit/G2_FPS_MEFHC_P12.identity.npz
[[ "$(git -C "$MINE" rev-parse HEAD)" == "$MINE_COMMIT" ]]
[[ -z "$(git -C "$MINE" status --porcelain)" ]]
mkdir -p "$OUT"
export PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 TF_FORCE_GPU_ALLOW_GROWTH=true
export TF_DETERMINISTIC_OPS=1 CUBLAS_WORKSPACE_CONFIG=:4096:8 NVIDIA_TF32_OVERRIDE=0
module load tensorflow/2.15.0
B="$MINE/nd-unfolding/pet/improvement_campaign/phase_b/pet"
drv() {  # $1 gpu, $2 config, $3 out, rest = extra args
  local g=$1 cfg=$2 run=$3; shift 3; mkdir -p "$run"
  CUDA_VISIBLE_DEVICES=$g python "$MINE/nd-unfolding/mnv_guarded_run.py" --expect-root "$MINE" \
    --inventory "$run/guard-$SLURM_JOB_ID-$RANDOM.json" --label "B2-dev" \
    -- "$B/b2_driver.py" --config "$B/configs/$cfg" --repo "$MINE" --out "$run" \
    --inputs-npz "$INPUTS" --identity-sidecar "$SIDECAR" --first-iteration-estimate-s 60 "$@" \
    >> "$run/run.log" 2>&1
}
( drv 0 b2dev-unfold.json "$OUT/cont" ) & p0=$!
( drv 1 b2dev-unfold.json "$OUT/resume" --stop-after-iteration 0 && \
  drv 1 b2dev-unfold.json "$OUT/resume" ) & p1=$!
( drv 2 b2dev-unfold-arm.json "$OUT/arm" ) & p2=$!
( drv 3 b2dev-truth-baseline.json "$OUT/truth-T0" --mode truth_only && \
  drv 3 b2dev-truth-pdg_onehot_truthglobals.json "$OUT/truth-T2" --mode truth_only ) & p3=$!
status=0
for p in $p0 $p1 $p2 $p3; do wait $p || status=1; done
python - "$OUT" <<'PY' >> "$OUT/resume-check.txt" 2>&1 || status=1
import sys, numpy as np, pathlib
out = pathlib.Path(sys.argv[1])
for k in (0, 1):
    a = np.load(out / "cont" / "iterations" / f"iter{k:02d}.npz")
    b = np.load(out / "resume" / "iterations" / f"iter{k:02d}.npz")
    for f in ("pull", "push"):
        eq = np.array_equal(a[f], b[f])
        print(f"iter{k} {f} bit-equal={eq} max|d|={float(np.max(np.abs(a[f] - b[f]))):.3e}")
PY
python -m pytest -q -p no:cacheprovider "$B/test_b2_arms.py" > "$OUT/tests.txt" 2>&1 || echo "pytest exit $?" >> "$OUT/tests.txt"
[[ -z "$(git -C "$MINE" status --porcelain)" ]] || status=1
echo "status $status" > "$OUT/terminal-$SLURM_JOB_ID.txt"
exit $status
