#!/bin/bash
# FD-CT-3B-BINDING.md section 3 condition 1: FD-CT-3B-DECLARATION.md section 2.1 at the bound pin.
P=/pscratch/sd/j/josephrb
B=$P/fd-ct-3b-20261029
PIN=e904d635d8769fae9f8cebbb9174ca081a5b214c
D=$B/deploy/e904d635
R3=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-ct/3b
if [ -e "$B" ]; then echo "STOP: $B exists"; exit 9; fi
mkdir -p $B/logs $B/tmp $B/tables
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold $D && git -C $D checkout --quiet --detach $PIN
{ date -u +%FT%TZ; hostname; git -C $D rev-parse HEAD
  echo "porcelain_ignored_lines $(git -C $D status --porcelain --ignored | wc -l)"
  cd $D && sha256sum nd-unfolding/fd_ct_closure.py nd-unfolding/tests/test_fd_ct_closure.py nd-unfolding/fd_ct_readers.py \
    nd-unfolding/tests/test_fd_ct_readers.py nd-unfolding/submit_fd_ct.sh nd-unfolding/fd_f1_lane.py nd-unfolding/s5c_array.sh \
    docs/orchestration/state/gpu-timing-20261023/tools/sbatch_timing_packed.sh nd-unfolding/pv-ladder/pvl_unfold.py \
    nd-unfolding/pv-ladder/pvl_lib.py nd-unfolding/build_cresp.py $R3/make_3b_tables.py $R3/3b-steps.tsv $R3/tasks-3b.tsv \
    nd-unfolding/fd_f0_regrade.py nd-unfolding/s1_assemble.py nd-unfolding/s5p_stage1_inspect.py \
    docs/orchestration/state/measurement-paper/5d-community-20261024/FD-CT-3B-DECLARATION.md; } > $B/logs/deploy.log 2>&1
cd $D/nd-unfolding/tests && TMPDIR=$B/tmp env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -B -m unittest \
  test_fd_ct_closure test_fd_ct_readers test_fd_f0_regrade test_build_cresp test_s1_assemble test_s1_scripts_isolated \
  > $B/logs/deploy-tests.log 2>&1; echo "tests rc=$?" >> $B/logs/deploy.log
cd $B && env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I -B $D/$R3/make_3b_tables.py $D $B/tables >> $B/logs/deploy.log 2>&1
for t in 3b-steps.tsv tasks-3b.tsv; do cmp $B/tables/$t $D/$R3/$t && echo "table $t identical" >> $B/logs/deploy.log || echo "table $t DIFFERS" >> $B/logs/deploy.log; done
echo "porcelain_ignored_lines_after_tests $(git -C $D status --porcelain --ignored | wc -l)" >> $B/logs/deploy.log
date -u +%FT%TZ >> $B/logs/deploy.log
echo DONE > $B/logs/deploy.done
