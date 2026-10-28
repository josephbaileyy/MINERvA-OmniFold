# Step 4 (FD-F1-BINDING-AMENDMENT-1.md section 4.1): the amendment's deploy, F1a's reused products, the original
# section 8 digests and the declared tests, on a login node.
P=/pscratch/sd/j/josephrb
OUT=$P/fd-f1-20261027
PIN=4b7a9892ef4d739afc45f6bfb6cc5f8d7a36fe54
D2=$OUT/deploy/4b7a9892
PY="env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I -B"
for x in $D2 $OUT/f1a2 $OUT/f1b2; do if [ -e "$x" ]; then echo "STOP: $x exists"; exit 3; fi; done
mkdir -p $OUT/tmp2
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold $D2 && git -C $D2 checkout --quiet --detach $PIN
L=$OUT/logs/deploy2.log
sed "s#$OUT/deploy/5015535e#$D2#" $OUT/logs/expected-sha256.txt > $OUT/logs/expected-sha256-2.txt
{ date -u +%FT%TZ; hostname; echo "HEAD $(git -C $D2 rev-parse HEAD)"
  echo "porcelain_ignored_lines $(git -C $D2 status --porcelain --ignored | wc -l)"
  sha256sum -c $OUT/logs/expected-sha256-2.txt; echo "section 8 digests rc=$?"
  SUMS=$D2/docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-f1/amendment-1/f1a-SHA256SUMS
  grep -E '  \./(splines/[A-Za-z0-9_]+_CH\.xml\.gz|flux_phi_t_0_100\.root|graphs_[A-Za-z0-9_]+\.root)$' $SUMS > $OUT/logs/reused-2.sha256
  echo "reused lines $(wc -l < $OUT/logs/reused-2.sha256)"
  ( cd $OUT/f1a && sha256sum -c $OUT/logs/reused-2.sha256 ); echo "reused products rc=$?"
  echo "amendment $(sha256sum $D2/docs/orchestration/state/measurement-paper/5d-community-20261024/FD-F1-DECLARATION-AMENDMENT-1.md | cut -c1-64)"
} > $L 2>&1
cd $D2
for t in test_fd_f1_amend test_fd_f1 test_fd_f0_regrade; do
  TMPDIR=$OUT/tmp2 $PY nd-unfolding/tests/$t.py > $OUT/logs/deploy2-$t.log 2>&1; echo "$t rc=$?" >> $L
done
echo "porcelain_ignored_lines_after_tests $(git -C $D2 status --porcelain --ignored | wc -l)" >> $L
for x in $OUT/f1a2 $OUT/f1b2; do echo "$x exists=$([ -e $x ] && echo yes || echo no)" >> $L; done
date -u +%FT%TZ >> $L
cat $L; for t in test_fd_f1_amend test_fd_f1 test_fd_f0_regrade; do grep -E "^Ran |^OK|^FAILED" $OUT/logs/deploy2-$t.log; done
