# Step 7 (FD-F1-BINDING-AMENDMENT-2.md section 4.1): amendment 2's deploy, the re-verifications and the declared tests,
# on a login node. Runs detached (nohup) and writes its log under $OUT/logs; never touches $OUT/f1b or $OUT/f1b2.
P=/pscratch/sd/j/josephrb
OUT=$P/fd-f1-20261027
PIN=5f5e392c4be9c6f8bb035a72d4a60f7dd8be8803
D3=$OUT/deploy/5f5e392c
PY="env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I -B"
for x in $D3 $OUT/f1b3 $OUT/gate3 $OUT/tmp3; do if [ -e "$x" ]; then echo "STOP: $x exists"; exit 3; fi; done
mkdir -p $OUT/tmp3
L=$OUT/logs/deploy3.log
{ date -u +%FT%TZ; hostname
  git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold $D3 && git -C $D3 checkout --quiet --detach $PIN
  echo "clone rc=$?"
  echo "HEAD $(git -C $D3 rev-parse HEAD)"
  echo "porcelain_ignored_lines $(git -C $D3 status --porcelain --ignored | wc -l)"
  sed "s#$OUT/deploy/5015535e#$D3#" $OUT/logs/expected-sha256.txt > $OUT/logs/expected-sha256-3.txt
  sha256sum -c $OUT/logs/expected-sha256-3.txt; echo "section 8 digests rc=$?"
  ( cd $OUT/f1a && sha256sum -c $OUT/f1a2/reused.sha256 ); echo "F1a reused products rc=$?"
  RC=$D3/docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-f1/run/cluster/f1a2
  grep -E '  \./runs/[A-Za-z0-9_]+/(long|short)_s[0-9]+\.time$' $RC/f1a2-SHA256SUMS > $OUT/logs/repilot-time-3.sha256
  echo "re-pilot .time lines $(wc -l < $OUT/logs/repilot-time-3.sha256)"
  ( cd $RC && sha256sum -c $OUT/logs/repilot-time-3.sha256 ); echo "re-pilot .time records, deployed copies rc=$?"
  ( cd $OUT/f1a2 && sha256sum -c $OUT/logs/repilot-time-3.sha256 ); echo "re-pilot .time records, cluster originals rc=$?"
  echo "amendment-2 declaration $(sha256sum $D3/docs/orchestration/state/measurement-paper/5d-community-20261024/FD-F1-DECLARATION-AMENDMENT-2.md | cut -c1-64)"
} > $L 2>&1
cd $D3
for t in test_fd_f1_amend2 test_fd_f1_amend test_fd_f1 test_fd_f0_regrade; do
  TMPDIR=$OUT/tmp3 $PY nd-unfolding/tests/$t.py > $OUT/logs/deploy3-$t.log 2>&1; echo "$t rc=$?" >> $L
done
echo "porcelain_ignored_lines_after_tests $(git -C $D3 status --porcelain --ignored | wc -l)" >> $L
for x in $OUT/f1b3 $OUT/gate3; do echo "$x exists=$([ -e $x ] && echo yes || echo no)" >> $L; done
echo "done: $(date -u +%FT%TZ)" >> $L
