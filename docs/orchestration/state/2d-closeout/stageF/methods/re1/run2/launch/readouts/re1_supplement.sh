#!/bin/bash
# RE-1 run 2: the C2 supplement as it was run on the login node (2026-10-22, deploy 651163e9), recorded here
# from the session. The one difference: the cache digest was read at run time from out/SHA256SUMS.inputs
# ($(grep cache.npz ...)); its value, eb1e3477..., is written out here.
set -eo pipefail
B=/pscratch/sd/j/josephrb/methods-paper/re1-20261022; C=$B/deploy-651163e9
source $C/docs/orchestration/state/2d-closeout/stageF/methods/re1/run2/launch/re1_env.sh
source $A/setup_salloc_env.sh >/dev/null 2>&1
export TMPDIR=$B/tmp; R=$O/readouts
COV=/global/cfs/cdirs/m3246/josephrb/2d-closeout-stageC-production-20261015/results/s5/production_cov.npz
Q=/global/cfs/cdirs/m3246/josephrb/2d-closeout-playlist-combination-20261017/s5_plus_playlist.npz
EU=$A/2d-unfolding/uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root
taskset -c 8-11 python $C/nd-unfolding/mnv_guarded_run.py --expect-root $C --label c2supp --inventory $O/inventory/c2supp.jsonl -- \
  $C/2d-unfolding/re1/re1_c2_supplement.py --eu $EU --cov $COV --q $Q --cache $O/2d/cache.npz \
  --expect-eu-sha256 4f5a1b6d44b9e7212b233650bb00bfb626ae65461e3bf8033cd67866dbd7eb2c \
  --expect-cov-sha256 6689d2fc2a795a72e66ee953a32d94c7906dd81a866771979f379c5f163a9ddc \
  --expect-q-sha256 8ccb4d723c3dbf737a7fb1d5236e5e25409c41b42b64ac55dccbbc12f595600e \
  --expect-cache-sha256 eb1e3477ac84a92d2498c2df6aad25e745f7f439a4cea3f784f6ef5a412d0652 \
  --pseudo-dir $O/2d/c2 --seeds 1:20 --readout $R/readout_2d_full.json --out $R/c2_supplement.json --tsv $R/c2_supplement.tsv > $R/c2_supplement.log 2>&1
