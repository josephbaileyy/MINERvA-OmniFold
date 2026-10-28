# Step 1 (FD-F1-BINDING.md section 4.1): deploy, the section 8 digests, and the declared tests, on a login node.
P=/pscratch/sd/j/josephrb
OUT=$P/fd-f1-20261027
PIN=5015535e5567c42827e2b618b9b679d534ec47cf
D=$OUT/deploy/5015535e
PY="env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I -B"
if [ -e "$OUT" ]; then echo "STOP: $OUT exists"; exit 3; fi
mkdir -p $OUT/logs $OUT/tmp $OUT/deploy
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold $D && git -C $D checkout --quiet --detach $PIN
X=/cvmfs/larsoft.opensciencegrid.org/products/genie_xsec/v3_04_00/NULL
cat > $OUT/logs/expected-sha256.txt <<SUMS
bbcbade310d90e1ae487dde9d982e85cfe16fae35bba09dbde7db2dc99274ec5  $P/s5p-20260926/gen5d_fluxfix/phi_t.npz
5eecae84509ba8ededbe8fdee63508d8e36cd057cc0547a940383f80248580eb  $P/MINERvA-OmniFold/2d-unfolding/baseline_flux/flux_integral_universes_MEFHC.root
1b4b0b37fc8c11acbf00884a94d0a3bda519d9c458f2c916573ef3d673a3ee35  $X/G1810a0211b-k250-e1000/data/gxspl-NUsmall.xml
abfca258817a3f7d8169cdd2dbf9349a025ab38312435c718347598b53f16726  $X/G1810a0211b-k250-e1000/data/README
185d7d8a4674b5df445fcadea3d17232804390c8421d563aa402c6ee743a0bbb  $X/AR2320i00000-k250-e1000/data/gxspl-NUsmall.xml
744cba18f82cc5fe4805cd8be120e5f7e5f7b36f657f4cc9f2118e69c803bcb2  $X/AR2320i00000-k250-e1000/data/README
cfa42210dfe9cadc8e9460333316a639bd719c9ae52ab1144be900372a9adcc2  $P/s5p-20260926/gen5d_fluxfix/genie_cv_xsec5d_full.npz
078df3b6f361eca32c685374fc0b953024f69cf0bd49c1ebc25ea2b95f0f8310  $D/nd-unfolding/pv-ladder/config.json
07fccc1abc7204bc29349b4ba96850986fe91e909e83fc54e8d1a6b3922a649f  $P/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz
2addac8f26055c5ed69862e7afe29e12ac51dbe23a8d6eeed79d71bec9d82955  $P/s5c-20260924/runs/p2/bkg_dump.npz
e36f3b25459e068cec9dba941f7b3aea8f48c6e22c931fde7c9d315e7b1e8de2  $P/methods-paper/re1-20261022/out/5d/k1_p5_rerun.npz
4d8b579732b79cbbb8e6c9a4f6335c4bda4eae6dd4194241a0d8cd6e7ea8a20a  $P/cresp-20261026/out/cresp.npz
b9db935a3187646ba2accaf3865cf4aa26ad72676063c58e7f5e6220224ef17b  $D/docs/orchestration/state/measurement-paper/5d-community-20261024/fd/readout/fd_f0b_readout.json
SUMS
{ date -u +%FT%TZ; hostname; echo "HEAD $(git -C $D rev-parse HEAD)"
  echo "porcelain_ignored_lines $(git -C $D status --porcelain --ignored | wc -l)"
  sha256sum -c $OUT/logs/expected-sha256.txt; echo "digests rc=$?"
  echo "declaration $(sha256sum $D/docs/orchestration/state/measurement-paper/5d-community-20261024/FD-F1-DECLARATION.md | cut -c1-64)"
  echo "binding $(sha256sum $D/docs/orchestration/state/measurement-paper/5d-community-20261024/FD-F1-BINDING.md 2>/dev/null | cut -c1-64)"
} > $OUT/logs/deploy.log 2>&1
cd $D
for t in test_fd_f1 test_fd_f0_regrade; do
  TMPDIR=$OUT/tmp $PY nd-unfolding/tests/$t.py > $OUT/logs/deploy-$t.log 2>&1; echo "$t rc=$?" >> $OUT/logs/deploy.log
done
echo "porcelain_ignored_lines_after_tests $(git -C $D status --porcelain --ignored | wc -l)" >> $OUT/logs/deploy.log
date -u +%FT%TZ >> $OUT/logs/deploy.log
cat $OUT/logs/deploy.log; for t in test_fd_f1 test_fd_f0_regrade; do grep -E "^Ran |^OK|^FAILED" $OUT/logs/deploy-$t.log; done
