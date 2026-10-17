#!/bin/bash
NS=/pscratch/sd/j/josephrb/2d-closeout-stageC-production-20261015
C=/global/cfs/cdirs/m3246/josephrb/2d-closeout-stageC-production-20261015
P=docs/orchestration/state/2d-closeout/stageC/production
echo "== products and item JSONs: pscratch | CFS"
for f in s5/production_cov.npz s5/s5.json s5/uq_production_covariance.root c0.json s3.json s4ii.json s1.json s2.json s4i.json smoke_pack_s1.json; do
  a=$(sha256sum $NS/results/$f | cut -c1-64); b=$(sha256sum $C/results/$f 2>/dev/null | cut -c1-64)
  echo "$f $a $b $([ "$a" = "$b" ] && echo SAME || echo DIFF)"
done
echo "== repo_k bound files"
cd $NS/repo_k && sha256sum $P/manifest.json $P/sbatch_pack.sh $P/sbatch_prod.sh $P/launch.py $P/deploy_repo_k.sh $P/jobs.tsv $P/analyze_prod.py $P/s5_rollup.py 2d-unfolding/unfold_2d_omnifold_unbinned.py 2d-unfolding/driver_p1.py docs/orchestration/state/2d-closeout/c04-repair/scripts/build_repair.py docs/orchestration/state/2d-closeout/stageC/pilot/analyze_pilot.py docs/orchestration/state/2d-closeout/stageC/pilot/p1/analyze_p1.py docs/orchestration/state/2d-closeout/stageB/evidence/b-genie-truth/sweeps.json
cat .deployed_commit
echo "== repo (shared) bound files"
cd $NS/repo && sha256sum $P/manifest.json $P/jobs.tsv $P/launch.py $P/sbatch_prod.sh $P/analyze_prod.py $P/s5_rollup.py 2d-unfolding/unfold_2d_omnifold_unbinned.py 2d-unfolding/driver_p1.py; cat .deployed_commit
sha256sum /pscratch/sd/j/josephrb/MINERvA-OmniFold/unbinned_unfolding/python/omnifold.py
echo "== CFS SHA256SUMS identity and count"
sha256sum $C/SHA256SUMS.pscratch; wc -l < $C/SHA256SUMS.pscratch; find $C -type f | wc -l; ls $C/out | wc -l; ls $C/out/*/xsec.root | wc -l
echo "== s5 run log tail"; tail -5 $NS/gatelog/s5_rollup.txt; grep -c '^\[PASS\]' $NS/gatelog/s5_rollup.txt; grep -c '^\[FAIL\]' $NS/gatelog/s5_rollup.txt
