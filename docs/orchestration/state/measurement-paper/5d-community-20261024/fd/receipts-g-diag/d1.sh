set -u
P=/pscratch/sd/j/josephrb
B=$P/fd-g-diag-20261026
PIN=d02ce2f21818963fca5836e4dc4462dd81ad6175
D=$B/deploy/d02ce2f2
test ! -e $B || { echo "STOP: $B exists"; exit 9; }
mkdir -p $B/logs $B/tmp
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold $D && git -C $D checkout --quiet --detach $PIN
{ date -u +%FT%TZ; hostname; git -C $D rev-parse HEAD
  echo "porcelain_ignored_lines $(git -C $D status --porcelain --ignored | wc -l)"
  cd $D && sha256sum nd-unfolding/fd_g_diag.py nd-unfolding/tests/test_fd_g_diag.py nd-unfolding/fd_g_compare.py \
    nd-unfolding/tests/test_fd_g_compare.py nd-unfolding/s1_assemble.py nd-unfolding/s5p_stage1_inspect.py \
    nd-unfolding/pv-ladder/readouts/h2_definition.json \
    docs/orchestration/state/measurement-paper/5d-community-20261024/fd/readout/fd_g_readout.json \
    docs/orchestration/state/measurement-paper/5d-community-20261024/FD-G-DIAG-DECLARATION.md; } > $B/logs/deploy.log 2>&1
cd $D/nd-unfolding/tests && TMPDIR=$B/tmp env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -B -m unittest \
  test_fd_g_diag test_fd_g_compare test_s1_assemble test_s1_scripts_isolated > $B/logs/deploy-tests.log 2>&1; echo "tests rc=$?" >> $B/logs/deploy.log
echo "porcelain_ignored_lines_after_tests $(git -C $D status --porcelain --ignored | wc -l)" >> $B/logs/deploy.log
date -u +%FT%TZ >> $B/logs/deploy.log
cat $B/logs/deploy.log; grep -E '^Ran|^OK|^FAILED|skipped' $B/logs/deploy-tests.log
