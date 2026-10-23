#!/bin/bash
set -eo pipefail
C=/pscratch/sd/j/josephrb/methods-paper/re1-20261022/deploy-ec829e28
source $C/docs/orchestration/state/2d-closeout/stageF/methods/re1/run2/launch/re1_env.sh
source $A/setup_salloc_env.sh >/dev/null 2>&1
set -u
export TMPDIR=$B/tmp
R=$O/readouts; mkdir -p $R $O/inventory
sha() { sha256sum "$1" | cut -d' ' -f1; }
[ "$(git -C $C rev-parse HEAD)" = ec829e28"$(git -C $C rev-parse HEAD | cut -c9-)" ] && [ -z "$(git -C $C status --porcelain)" ]
mv1() { local d=$1 e=$2 c=$3 cur=$4 cursha=$5 npz=$6; shift 6
  taskset -c 8-11 python $C/nd-unfolding/mnv_guarded_run.py --expect-root $C --label mv${d}d --inventory $O/inventory/mv${d}d.jsonl -- \
    $C/nd-unfolding/re1/re1_nd_movement.py --dim $d --e $e --c $c --current $cur --expect-e-sha256 $(sha $e) --expect-c-sha256 $(sha $c) \
    --expect-current-sha256 $cursha --edges-npz $npz "$@" --out $R/movement_${d}d.json --tsv $R/movement_${d}d.tsv > $R/movement_${d}d.log 2>&1
  echo "${d}D rc=$?"; }
mv1 3 $O/3d/p3.npz $O/3d/p3c.npz $A/3d-unfolding/xsec_3d_MEFHC_5iter_lgbm.root 0dd94830821576a3b060fae2d4a20564610c535ed06046cd1eb05cd11885dd59 $O/3d/of_inputs_3d.npz
mv1 4 $O/4d/p4.npz $O/4d/p4c.npz $A/nd-unfolding/products/4d/xsec_4d_MEFHC_5iter_lgbm.root 1fb8250820c00428fc547cb05aa95535023146723acdccb61f615f3fa763f9d2 $O/4d/of_inputs_4d.npz
mv1 5 $O/5d/k1_p5_rerun.npz $O/5d/p5c.npz $A/nd-unfolding/products/5d/xsec_5d_MEFHC_5iter_lgbm.root 630306e20e4e175bde8b459174842a58e4f4b5a694b8a5018e730a952820aec8 $NPZ5D \
   --trunk $A/nd-unfolding/uq_5d/z_pilot_20260916_a5/z-cv.npz --expect-trunk-sha256 3d7465f66fbe66b0dfcf09b6fc51249f227fb33e97ae40bc78dda90275e918c5
cd $O && sha256sum readouts/movement_* > readouts/SHA256SUMS.movement && cat readouts/SHA256SUMS.movement
