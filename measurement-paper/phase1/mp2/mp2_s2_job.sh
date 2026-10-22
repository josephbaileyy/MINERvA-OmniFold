#!/bin/bash
#SBATCH -A m3246
#SBATCH -C cpu
#SBATCH -N 1
#SBATCH -o /pscratch/sd/j/josephrb/measurement-paper/phase1/mp2/s2/logs/mp2s2-%x-%j.out
# MP-2 S2 (binding addendum 8: S2/S3 granted; frozen contract 98141c2f... with addendum 9). QOS and time limit are
# given on the sbatch command line, never premium.
#   dump        mp2_s2_dump.py (omnifold_py310: uproot) -> $D/dump
#   harm <only> mp2_s2_harmonize.py (root_6_28: ROOT) -> $D/harm_<tag>; controls H0, N, A, Z before any harmonized output
#   models G FSET 'k:h:f,..|k:h:f,..|..'  mp2_s2_fit.py models: each |-group is one concurrent srun step (256/n cpus)
#   gates G FSET                          mp2_s2_fit.py gates (V1, V4; V2/V3 statistics sealed, addendum 13)
#   modgates G FSET 'groups'              models, then (only if every model step exited 0) gates, on the same node
# CODE (an immutable snapshot directory under $D, passed with --export) is the code every stage runs; default $D/code.
# Writes only under $D. No set -u before the conda hook. sbatch runs a copy of this file, so $D is absolute.
set -o pipefail
D=/pscratch/sd/j/josephrb/measurement-paper/phase1/mp2/s2
P1=/pscratch/sd/j/josephrb/measurement-paper/phase1
CODE=${CODE:-$D/code}
FITDIR=${FITDIR:-$D/fit}           # the timing probe writes elsewhere (never read by gates)
CONTRACT=$CODE/feature_contract_draft.json
CONTRACT_SHA=98141c2f22f4fc3f2a7f5b30a0c509d6a29a37d145a72ea802623a2a2d6630cd
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 TMPDIR=$D/tmp
cd "$D/tmp" || exit 2
STAGE=${1:?usage: mp2_s2_job.sh dump | harm TAG ONLY}
echo "host $(hostname) start $(date -u +%FT%TZ) stage $STAGE"
read -r got _ < <(sha256sum "$CONTRACT")
[ "$got" = "$CONTRACT_SHA" ] || { echo "STOP: contract sha256 $got is not the frozen $CONTRACT_SHA"; exit 4; }
echo "code $CODE"; sha256sum "$CODE"/*.py "$CODE"/*.json "$CODE"/*.sh
if [ "$STAGE" = dump ]; then
  srun -n 1 -c 256 "$HOME/.conda/envs/omnifold_py310/bin/python" -I "$CODE/mp2_s2_dump.py" "$D/dump"
  rc=$?
  echo "dump rc=$rc end $(date -u +%FT%TZ)"
  exit $rc
fi
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/root_6_28"
unset PYTHONPATH
if [ "$STAGE" = models ] || [ "$STAGE" = gates ] || [ "$STAGE" = modgates ]; then
  GEN=${2:?gen}; FSET=${3:?fset}
  HARM="$D/harm_a $D/harm_b"
  run_gates() {
    srun -n 1 -c 256 python3 "$CODE/mp2_s2_fit.py" gates --gen "$GEN" --fset "$FSET" --harm $HARM \
      --contract "$P1/mp5/inputs/s5c_contract.json" --fcontract "$CONTRACT" --out "$FITDIR" --threads 128
    rc=$?
    echo "gates $GEN $FSET rc=$rc end $(date -u +%FT%TZ)"
    return $rc
  }
  if [ "$STAGE" = gates ]; then run_gates; exit $?; fi
  IFS='|' read -r -a GROUPS_ <<< "${4:?task groups}"
  NG=${#GROUPS_[@]}
  C=$((256 / NG)); TH=$((C / 2))
  pids=()
  for g in "${GROUPS_[@]}"; do
    srun -n 1 -c $C --exact --mem=$((480 / NG))G python3 "$CODE/mp2_s2_fit.py" models --gen "$GEN" --fset "$FSET" \
      --tasks "$g" --harm $HARM --fcontract "$CONTRACT" --out "$FITDIR" --threads $TH &
    pids+=($!)
  done
  rc=0
  for p in "${pids[@]}"; do wait "$p" || rc=$?; done
  echo "models $GEN $FSET groups=$NG cpus=$C threads=$TH rc=$rc end $(date -u +%FT%TZ)"
  if [ "$STAGE" = modgates ]; then
    [ $rc = 0 ] || { echo "STOP: a model step failed (rc=$rc); gates do not run"; exit $rc; }
    run_gates; exit $?
  fi
  exit $rc
fi
TAG=${2:?tag}
ONLY=${3:?only}
[ -f "$D/dump/s2_dump.json" ] && grep -q '"exit": 0' "$D/dump/s2_dump.json" || { echo "STOP: no complete dump"; exit 5; }
srun -n 1 -c 256 python3 "$CODE/mp2_s2_harmonize.py" --dump "$D/dump" --s1 "$P1/mp2/s1" --pool "$P1/mp5/run/pool" \
  --contract "$CONTRACT" --out "$D/harm_$TAG" --nproc 64 --only "$ONLY"
rc=$?
echo "harm $TAG rc=$rc end $(date -u +%FT%TZ)"
exit $rc
