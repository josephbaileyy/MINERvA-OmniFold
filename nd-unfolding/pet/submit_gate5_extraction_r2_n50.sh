#!/bin/bash
# Changed continuation after 56935552 proved the immutable-worktree flux-path defect.
set -eo pipefail

CODE_ROOT=$(git rev-parse --show-toplevel)
DATA_ROOT=/pscratch/sd/j/josephrb/MINERvA-OmniFold
ROOT=${DATA_ROOT}/nd-unfolding/pet/fullevent_cstat_n50
PREDECESSOR_JOB=56935552
ARRAY_SCRIPT=${CODE_ROOT}/nd-unfolding/pet/sbatch_gate5_replica_extract_array.sh
VALIDATE_SCRIPT=${CODE_ROOT}/nd-unfolding/pet/sbatch_gate5_extraction_family_validate.sh
DRIVER=${CODE_ROOT}/nd-unfolding/pet/extract_fullevent_replica.py
VALIDATOR=${CODE_ROOT}/nd-unfolding/pet/validate_gate5_extraction_family.py
NOMINAL_EXTRACTOR=${CODE_ROOT}/nd-unfolding/pet/extract_fullevent_fps.py
LOADER=${CODE_ROOT}/nd-unfolding/pet/fullevent_fps_dataloader.py
INPUT=${DATA_ROOT}/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz
FLUX=${DATA_ROOT}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root
PROMOTION=${CODE_ROOT}/docs/orchestration/state/gate5-training-family-promotion-56933831.json
PROMOTED_REPORT=${CODE_ROOT}/docs/orchestration/state/gate5-training-family-promotion-evidence-56933831/GATE5_TRAINING_ARTIFACT_VALIDATION.slurm-56933831.json
EXPECTED_INPUT_SHA=fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625

die() { echo "[gate5-extract-r2-submit][FAIL] $*" >&2; exit "${2:-1}"; }
sha_of() { sha256sum "$1" | awk '{print $1}'; }
[[ -z "$(git -C "$CODE_ROOT" status --porcelain)" ]] || die "code worktree is dirty"
HEAD=$(git -C "$CODE_ROOT" rev-parse HEAD)
for f in "$ARRAY_SCRIPT" "$VALIDATE_SCRIPT" "$DRIVER" "$VALIDATOR" \
         "$NOMINAL_EXTRACTOR" "$LOADER" "$INPUT" "$FLUX" "$PROMOTION" "$PROMOTED_REPORT"; do
  [[ -s "$f" && ! -L "$f" ]] || die "missing/empty/symlink prerequisite $f"
done
/usr/bin/python3.11 - "$PROMOTION" "$PROMOTED_REPORT" <<'PY'
import json, sys
p, a = map(lambda x: json.load(open(x)), sys.argv[1:])
assert p["promotion_verdict"] == "GATE5_TRAINING_FAMILY_PROMOTION_PASS"
assert p["validators"]["training_artifacts"]["members_passing"] == 50
assert p["C_stat"] is None
assert a["verdict"] == "GATE5_TRAINING_ARTIFACTS_PASS"
assert a["declared_inventory"] == 50 and len(a["members"]) == 50
PY
if squeue -h -u "$USER" -n g5extractr2,g5xmanr2 | grep -q .; then
  squeue -h -u "$USER" -n g5extractr2,g5xmanr2 -o '%i|%j|%T|%R' >&2
  die "a changed Gate-5 extraction continuation is already active"
fi
/usr/bin/python3.11 - "$ROOT" <<'PY'
import json, os, pathlib, sys
root=pathlib.Path(sys.argv[1])
for index in range(50):
    base=root/'replicas'/f'replica_{index:02d}'/'extraction'
    push=base/'GATE5_REPLICA_FULL_PUSH.npz'; mark=pathlib.Path(str(push)+'.done')
    if push.exists() != mark.exists():
        raise SystemExit(f'partial push payload/marker for replica {index}')
    if push.exists():
        m=json.loads(mark.read_text()); st=push.stat()
        if m.get('size') != st.st_size or m.get('mtime') != int(st.st_mtime):
            raise SystemExit(f'invalid push completion marker for replica {index}')
    for name in ('GATE5_REPLICA_XSEC.npz','GATE5_REPLICA_XSEC.npz.done',
                 'GATE5_REPLICA_XSEC.summary.json','GATE5_REPLICA_XSEC.summary.json.done',
                 'GATE5_REPLICA_EXTRACTION_RECEIPT.json',
                 'GATE5_REPLICA_EXTRACTION_RECEIPT.json.done'):
        if (base/name).exists() or (base/name).is_symlink():
            raise SystemExit(f'collision/no-clobber guard: {base/name}')
PY
mkdir -p "${ROOT}/logs" "${ROOT}/validation"

EXPORTS="ALL,HOME=/global/homes/j/josephrb,GATE5_CODE_ROOT=$CODE_ROOT,GATE5_DATA_ROOT=$DATA_ROOT"
EXPORTS+=",GATE5_EXPECTED_HEAD=$HEAD,GATE5_EXPECTED_INPUT_SHA=$EXPECTED_INPUT_SHA"
EXPORTS+=",GATE5_EXPECTED_EXTRACT_DRIVER_SHA=$(sha_of "$DRIVER")"
EXPORTS+=",GATE5_EXPECTED_NOMINAL_EXTRACTOR_SHA=$(sha_of "$NOMINAL_EXTRACTOR")"
EXPORTS+=",GATE5_EXPECTED_LOADER_SHA=$(sha_of "$LOADER")"

ARRAY_JOB=$(sbatch --parsable --job-name=g5extractr2 --array=0-49%10 \
  --dependency="afterany:${PREDECESSOR_JOB}" --export="$EXPORTS" "$ARRAY_SCRIPT") \
  || die "changed extraction array submission failed"
[[ "$ARRAY_JOB" =~ ^[0-9]+$ ]] || die "unexpected extraction array job id $ARRAY_JOB"
if ! MANIFEST_JOB=$(sbatch --parsable --job-name=g5xmanr2 \
      --dependency="afterany:${ARRAY_JOB}" \
      --export="${EXPORTS},GATE5_EXTRACTION_ARRAY_JOB=${ARRAY_JOB}" "$VALIDATE_SCRIPT"); then
  scancel "$ARRAY_JOB" || true
  die "changed manifest job submission failed; exact extraction array $ARRAY_JOB cancelled"
fi
[[ "$MANIFEST_JOB" =~ ^[0-9]+$ ]] || die "unexpected manifest job id $MANIFEST_JOB"
echo "GATE5_EXTRACTION_R2_ARRAY_JOB=$ARRAY_JOB"
echo "GATE5_EXTRACTION_R2_MANIFEST_JOB=$MANIFEST_JOB"
echo "GATE5_R2_PREDECESSOR_DEPENDENCY=afterany:$PREDECESSOR_JOB"
echo "GATE5_R2_MANIFEST_DEPENDENCY=afterany:$ARRAY_JOB"
echo "GATE5_CODE_HEAD=$HEAD"
echo "GATE5_OUTPUT_ROOT=$ROOT"
