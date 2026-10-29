#!/bin/bash
# FD-CT-READERS-BINDING.md section 3 condition 1: FD-CT-READERS-DECLARATION.md section 2.1, verbatim, at the bound pin.
P=/pscratch/sd/j/josephrb
B=$P/fd-ct-readers-20261028
PIN=28ea789edd8e0211ac95d57957ba01b06380c862
D=$B/deploy/28ea789e
if [ -e "$B" ]; then echo "STOP: $B exists"; exit 9; fi
mkdir -p $B/logs $B/tmp
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold $D && git -C $D checkout --quiet --detach $PIN
{ date -u +%FT%TZ; hostname; git -C $D rev-parse HEAD
  echo "porcelain_ignored_lines $(git -C $D status --porcelain --ignored | wc -l)"
  cd $D && sha256sum nd-unfolding/fd_ct_readers.py nd-unfolding/tests/test_fd_ct_readers.py nd-unfolding/fd_f0_regrade.py \
    nd-unfolding/s1_assemble.py nd-unfolding/s5p_stage1_inspect.py nd-unfolding/pv-ladder/readouts/h2_definition.json \
    docs/orchestration/state/measurement-paper/5d-community-20261024/FD-CT-READERS-DECLARATION.md; } > $B/logs/deploy.log 2>&1
cd $D/nd-unfolding/tests && TMPDIR=$B/tmp env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -B -m unittest \
  test_fd_ct_readers test_fd_f0_regrade test_build_cresp test_s1_assemble test_s1_scripts_isolated \
  > $B/logs/deploy-tests.log 2>&1; echo "tests rc=$?" >> $B/logs/deploy.log
echo "porcelain_ignored_lines_after_tests $(git -C $D status --porcelain --ignored | wc -l)" >> $B/logs/deploy.log
date -u +%FT%TZ >> $B/logs/deploy.log
echo DONE > $B/logs/deploy.done
