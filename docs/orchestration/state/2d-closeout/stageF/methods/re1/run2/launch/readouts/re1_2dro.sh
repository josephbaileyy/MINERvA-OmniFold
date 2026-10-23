#!/bin/bash
# re1_2dro.sh <tag> [extra analyze args]: RE-1 2D readout on the login node, pinned, through the OI-136 guard
set -eo pipefail
C=/pscratch/sd/j/josephrb/methods-paper/re1-20261022/deploy-ec829e28
source $C/docs/orchestration/state/2d-closeout/stageF/methods/re1/run2/launch/re1_env.sh
source $A/setup_salloc_env.sh >/dev/null 2>&1
set -u
export TMPDIR=$B/tmp
tag=$1; shift
R=$O/readouts; mkdir -p $R
COV=/global/cfs/cdirs/m3246/josephrb/2d-closeout-stageC-production-20261015/results/s5/production_cov.npz
Q=/global/cfs/cdirs/m3246/josephrb/2d-closeout-playlist-combination-20261017/s5_plus_playlist.npz
EU=$A/2d-unfolding/uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root
taskset -c 8-11 python $C/nd-unfolding/mnv_guarded_run.py --expect-root $C --label ro2d_$tag --inventory $O/inventory/ro2d_$tag.jsonl -- \
  $C/2d-unfolding/re1/re1_2d_analyze.py --eu $EU --cov $COV --q $Q \
  --expect-eu-sha256 4f5a1b6d44b9e7212b233650bb00bfb626ae65461e3bf8033cd67866dbd7eb2c \
  --expect-cov-sha256 6689d2fc2a795a72e66ee953a32d94c7906dd81a866771979f379c5f163a9ddc \
  --expect-q-sha256 8ccb4d723c3dbf737a7fb1d5236e5e25409c41b42b64ac55dccbbc12f595600e \
  "$@" --out $R/readout_2d_$tag.json > $R/readout_2d_$tag.log 2>&1
echo rc=$?; tail -3 $R/readout_2d_$tag.log
