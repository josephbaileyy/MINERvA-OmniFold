#!/bin/bash
# On-node packed orchestrator for the corrected FPS UQ chain (Agent C / P6-FPS).
# Runs INSIDE an alloc_run/salloc CPU node. LightGBM ignores OMP_NUM_THREADS and grabs
# all cores (5D thrash lesson: load 571 at CONC=12), so each worker is PINNED with
# `taskset` to a DISJOINT cpu subset -> LightGBM's OpenMP sees only those cores -> no
# oversubscription. Skip-if-exists, time-budgeted (exits before the 3h wall so a login
# supervisor can re-invoke and resume). Priority order: boot+split (block-sum milestone)
# then throws+blocks. NOT set -u (conda activate reads unbound ADDR2LINE).
set -o pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; ND="${REPO}/nd-unfolding"
export ROOT628_PREFIX="${ROOT628_PREFIX:-/global/homes/j/josephrb/.conda/envs/root_6_28}"
source "${REPO}/setup_salloc_env.sh" 1>&2 || true
cd "$ND"
CORES_PER="${FPS_CORES_PER:-12}"   # 128/12=10 slots: throws hold ~29GB (all 72 knob ratios);
                                   # 16-wide OOM'd the 503GB node (all partial). 10-wide ~290GB peak.
BUDGET_MIN="${FPS_BUDGET_MIN:-150}"
export PYTHONUNBUFFERED=1
BD="uq_fps/corrected/boot_nd_fps"; SD="uq_fps/corrected/seedscan_split_fps"; UD="uq_fps/corrected/uthrow_slabs_fps_neutral"
mkdir -p "$BD" "$SD" "$UD" uq_fps/corrected/logs
# Delete PARTIAL throw/block slabs from a wall-killed prior chunk so skip-if-exists redoes
# them (a killed multi-unit task leaves an incomplete slab that would otherwise be skipped).
python3 - "$UD" <<'PY' 1>&2 || true
import glob, os, sys, numpy as np
ud=sys.argv[1]
for f in glob.glob(os.path.join(ud,"uthrowfps_slab_*.npz")):
    try:
        n=np.load(f,allow_pickle=True)["xs"].shape[0]
    except Exception: n=-1
    if n!=4: print(f"[preclean] rm partial throw slab {os.path.basename(f)} (n={n})"); os.remove(f)
for f in glob.glob(os.path.join(ud,"blockfps_*.npz")):
    t=int(os.path.basename(f)[len("blockfps_"):-4]); exp=4 if t<=5 else 5
    try:
        n=np.load(f,allow_pickle=True)["xs"].shape[0]
    except Exception: n=-1
    if n!=exp: print(f"[preclean] rm partial block slab {os.path.basename(f)} (n={n} exp={exp})"); os.remove(f)
PY

emit() {  # print the shell command for one unit IFF its output is missing
  case "$1" in
    boot)  o="$BD/res_boot_$2.npz";  [[ -s "$o" ]] || echo "python3 bootstrap_nd.py --npz of_inputs_fps.npz --seed $2 --estimator-seed 42 --iters 5 --out $o";;
    split) o="$SD/res_split_$2.npz"; [[ -s "$o" ]] || echo "python3 seedscan_split.py --npz of_inputs_fps.npz --split-seed $2 --estimator-seed 42 --train-frac 0.8 --iters 5 --out $o";;
    throw) o="$UD/uthrowfps_slab_$2.npz"; off=$(( $2 * 4 )); [[ -s "$o" ]] || echo "python3 unified_throw_cov.py --throws 4 --throw-offset $off --seed 1000 --bank bank_uthrow_fps --iters 5 --invalid-ratio neutral --out $o";;
    knob)  o="$UD/blockfps_$2.npz"; K=(2p2h,CCQEPauliSupViaKF FrAbs_pi,FrElas_N HighQ2,LowQ2 MaCCQE,MaRES MFP_N,MvRES Rvn2pi,Rvp2pi); [[ -s "$o" ]] || echo "python3 unified_throw_cov.py --blockunits --bank bank_uthrow_fps --iters 5 --seed 1000 --invalid-ratio neutral --block-knobs ${K[$2]} --out $o";;
    flux)  t=$2; o="$UD/blockfps_$t.npz"; lo=$(( (t-6)*5 )); hi=$(( lo+4 )); [[ -s "$o" ]] || echo "python3 unified_throw_cov.py --blockunits --bank bank_uthrow_fps --iters 5 --seed 1000 --invalid-ratio neutral --block-knobs '' --block-flux ${lo}-${hi} --out $o";;
  esac
}

TODO="uq_fps/corrected/logs/.fps_uq_todo.$$"
{
  for n in $(seq 100 -1 1); do emit boot  "$n"; done
  for n in $(seq 24 -1 1);  do emit split "$n"; done
  for k in $(seq 0 39);     do emit throw "$k"; done
  for t in $(seq 0 5);      do emit knob  "$t"; done
  for t in $(seq 6 25);     do emit flux  "$t"; done
} > "$TODO"
NTODO=$(wc -l < "$TODO")

# CPU set actually allowed in this cgroup -> partition into disjoint slots.
AFF=$(taskset -cp $$ 2>/dev/null | sed 's/.*: //')
mapfile -t CPUS < <(python3 - "$AFF" <<'PY'
import sys
out=[]
for p in sys.argv[1].split(','):
    if '-' in p:
        a,b=p.split('-'); out+=list(range(int(a),int(b)+1))
    elif p.strip(): out.append(int(p))
print('\n'.join(map(str,out)))
PY
)
NCPU=${#CPUS[@]}; (( NCPU<CORES_PER )) && CORES_PER=$NCPU
NSLOTS=$(( NCPU / CORES_PER )); (( NSLOTS<1 )) && NSLOTS=1
declare -a SLOTCPUS SLOTPID
for ((s=0;s<NSLOTS;s++)); do
  ids=(); for ((c=0;c<CORES_PER;c++)); do ids+=("${CPUS[$((s*CORES_PER+c))]}"); done
  SLOTCPUS[$s]=$(IFS=,; echo "${ids[*]}"); SLOTPID[$s]=""
done
echo "[packed] $(date -u '+%F %T UTC') todo=${NTODO} ncpu=${NCPU} slots=${NSLOTS}x${CORES_PER}c budget=${BUDGET_MIN}min"
if (( NTODO == 0 )); then echo "[packed] ALL FPS UQ units complete"; rm -f "$TODO"; exit 0; fi

END=$(( $(date +%s) + BUDGET_MIN*60 )); done_n=0
while IFS= read -r cmd; do
  [[ -z "$cmd" ]] && continue
  (( $(date +%s) >= END )) && { echo "[packed] budget reached; stop launching (running finish)"; break; }
  placed=0
  while (( ! placed )); do
    for ((s=0;s<NSLOTS;s++)); do
      pid=${SLOTPID[$s]}
      if [[ -z "$pid" ]] || ! kill -0 "$pid" 2>/dev/null; then
        taskset -c "${SLOTCPUS[$s]}" bash -c "$cmd" >/dev/null 2>&1 & SLOTPID[$s]=$!
        placed=1; done_n=$((done_n+1)); break
      fi
    done
    (( placed )) || sleep 5
  done
done < "$TODO"
wait
rm -f "$TODO"
echo "[packed] $(date -u '+%F %T UTC') chunk done (launched ${done_n} units this chunk)"
