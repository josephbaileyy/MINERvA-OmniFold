#!/bin/bash
#SBATCH --job-name=re1-f1b
#SBATCH --account=m3246
#SBATCH --qos=debug
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --time=00:10:00
#SBATCH --output=/pscratch/sd/j/josephrb/methods-paper/re1-20261022/logs/%x-%j.out
# RE-1 run 2, F1b: the steps F1 (60143725) did not reach before its time limit, unchanged: the P3/P4 container
# conversion and the printed numbers. F1's K3 outputs and logs in $O/f/k3 (with its cancelled conv3.log) are kept.
set -eo pipefail
source "$C/docs/orchestration/state/2d-closeout/stageF/methods/re1/run2/launch/re1_env.sh"
source "$C/docs/orchestration/state/2d-closeout/stageF/methods/re1/run2/launch/re1_f_env.sh"
re1_preflight
for p in "$CUR3D $CUR3D_SHA" "$CUR4D $CUR4D_SHA" "$EU $EU_SHA" "$EC $EC_SHA"; do re1_check $p; done
(cd "$O" && sha256sum -c SHA256SUMS.nd)
for p in "$F/new/xsec_3d_p3.root" "$F/new/xsec_4d_p4.root" "$F/numbers.json"; do [ ! -e "$p" ] || { echo "[re1] $p exists"; exit 3; }; done
cd "$F/new"
export OMP_NUM_THREADS=4
rc=0
run() { local label=$1; shift; srun -n1 -c 4 --exact --cpu-bind=cores bash -c "$(declare -f re1_py); C=$C O=$O; re1_py $label $*" > "$F/new/$label.log" 2>&1 || { echo "[re1] $label rc=$?"; rc=1; }; }
sha() { sha256sum "$1" | cut -d' ' -f1; }
run conv3 nd-unfolding/re1/re1_to_root.py --dim 3 --product "$O/3d/p3.npz" --expect-product-sha256 "$(sha $O/3d/p3.npz)" \
    --current "$CUR3D" --expect-current-sha256 "$CUR3D_SHA" --out "$F/new/xsec_3d_p3.root" --json "$F/new/conv3.json"
run conv4 nd-unfolding/re1/re1_to_root.py --dim 4 --product "$O/4d/p4.npz" --expect-product-sha256 "$(sha $O/4d/p4.npz)" \
    --current "$CUR4D" --expect-current-sha256 "$CUR4D_SHA" --out "$F/new/xsec_4d_p4.root" --json "$F/new/conv4.json"
run k3_numbers nd-unfolding/re1/re1_f_numbers.py --current "$CUR3D" --p3 "$F/new/xsec_3d_p3.root" --eu "$EU" --ec "$EC" \
    --anc "$ANC" --out "$F/numbers.json"
(cd "$F" && sha256sum k3/*.pdf k3/*.png new/*.root numbers.json > SHA256SUMS.f1) || rc=1
echo "[re1] end $(date -u +%FT%TZ) rc=$rc"
exit $rc
