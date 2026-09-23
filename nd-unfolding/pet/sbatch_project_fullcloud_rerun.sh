#!/bin/bash
#SBATCH --job-name=pcproj_fc_i30
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=32 --mem=120G --time=00:45:00
# ISSUE-30 / ISSUE-59 re-run of the full-cloud truth-cloud projection from a CODE checkout that
# is not the canonical one, reading the (gitignored, /pscratch-only) inputs from DATA_ROOT.
#
# sbatch runs a COPY of this file, so nothing here is derived from BASH_SOURCE or $0: both roots
# arrive through --export, and --output/--error are given on the sbatch command line.
#
#   sbatch --output=<rundir>/pcproj_%j.out --error=<rundir>/pcproj_%j.err \
#     --export=ALL,CODE_ROOT=<fresh checkout>,DATA_ROOT=<canonical checkout>,RUN_DIR=<rundir> \
#     <CODE_ROOT>/nd-unfolding/pet/sbatch_project_fullcloud_rerun.sh
#
# Writes products to $CODE_ROOT/nd-unfolding/products/pet/fullcloud and a receipt
# $RUN_DIR/receipt.json (jobid, code sha, sha256 of every input and output).
set -eo pipefail
: "${CODE_ROOT:?CODE_ROOT is required}"
: "${DATA_ROOT:?DATA_ROOT is required}"
: "${RUN_DIR:?RUN_DIR is required}"
mkdir -p "$RUN_DIR"

# Environment only (ROOT + numpy + matplotlib, no TensorFlow) from the canonical checkout's
# build products; the guard below refuses any module imported from a tree other than CODE_ROOT.
source "${DATA_ROOT}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1
export MNV_REPO="$CODE_ROOT"

export PCPROJ_PC="${DATA_ROOT}/nd-unfolding/of_inputs_pc_fullcloud.npz"
export PCPROJ_WEIGHTS="${DATA_ROOT}/nd-unfolding/products/pet/pet_weights_fullcloud.npz"
export PCPROJ_OMNI="${DATA_ROOT}/nd-unfolding/runEventLoopOmniFold_PC_MEFHC_fullcloud.root"
export PCPROJ_OUTDIR="${CODE_ROOT}/nd-unfolding/products/pet/fullcloud"
# Not env-overridable in pointcloud_projection.py (derived from _REPO): read through symlinks.
MCFILE_REL="2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root"
GBDT_REL="nd-unfolding/products/5d/xsec_5d_MEFHC_5iter_lgbm.root"
for rel in "$MCFILE_REL" "$GBDT_REL"; do
  mkdir -p "$(dirname "${CODE_ROOT}/${rel}")"
  [ -e "${CODE_ROOT}/${rel}" ] || ln -s "${DATA_ROOT}/${rel}" "${CODE_ROOT}/${rel}"
done
mkdir -p "$PCPROJ_OUTDIR"
INPUTS=("$PCPROJ_PC" "$PCPROJ_WEIGHTS" "$PCPROJ_OMNI" "${DATA_ROOT}/${MCFILE_REL}" "${DATA_ROOT}/${GBDT_REL}")
for f in "${INPUTS[@]}"; do
  [ -s "$f" ] || { echo "[proj] MISSING $f"; exit 1; }
done

sha256sum "${INPUTS[@]}" > "${RUN_DIR}/inputs.sha256" &
HASH_PID=$!

cd "${CODE_ROOT}/nd-unfolding"
echo "[proj] code $(git -C "$CODE_ROOT" rev-parse HEAD) start $(date -u +%FT%TZ)"
set +e
python3 mnv_guarded_run.py --expect-root "$CODE_ROOT" --inventory "${RUN_DIR}/guard_inventory.jsonl" \
  -- pet/pointcloud_projection.py
RC=$?
set -e
wait "$HASH_PID"
echo "[proj] exit ${RC} end $(date -u +%FT%TZ)"

OUTS=()
for f in pointcloud_projection_summary.json pointcloud_projection.root \
         pet_cloud_projection_xsec.png pet_cloud_projection_xsec.pdf \
         pet_cloud_projection_validation.png pet_cloud_projection_validation.pdf; do
  [ -e "${PCPROJ_OUTDIR}/${f}" ] && OUTS+=("${PCPROJ_OUTDIR}/${f}")
done
[ ${#OUTS[@]} -gt 0 ] && sha256sum "${OUTS[@]}" > "${RUN_DIR}/outputs.sha256"

python3 - "$RUN_DIR" "$RC" <<'PY'
import json, os, subprocess, sys
run_dir, rc = sys.argv[1], int(sys.argv[2])
def digests(name):
    p = os.path.join(run_dir, name)
    if not os.path.exists(p):
        return {}
    return {line.split(None, 1)[1].strip(): line.split(None, 1)[0]
            for line in open(p) if line.strip()}
code = os.environ["CODE_ROOT"]
json.dump({
    "jobid": os.environ.get("SLURM_JOB_ID"),
    "code_root": code,
    "code_sha": subprocess.check_output(["git", "-C", code, "rev-parse", "HEAD"], text=True).strip(),
    "data_root": os.environ["DATA_ROOT"],
    "entrypoint": "nd-unfolding/pet/pointcloud_projection.py (via mnv_guarded_run.py)",
    "exit_code": rc,
    "inputs_sha256": digests("inputs.sha256"),
    "outputs_sha256": digests("outputs.sha256"),
}, open(os.path.join(run_dir, "receipt.json"), "w"), indent=2)
PY
exit "$RC"
