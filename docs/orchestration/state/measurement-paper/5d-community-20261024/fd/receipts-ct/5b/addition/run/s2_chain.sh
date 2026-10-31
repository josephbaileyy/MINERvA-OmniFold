# 5B addition step 2 (FD-CT-5B-ADDITION-DECLARATION.md section 6, the chain's command; FD-CT-5B-ADDITION-BINDING.md section 3): once, login node.
# Run only after s1_deploy.sh shows HEAD = pin, 0/0 porcelain lines, 15/15 pins and "Ran 419 tests ... OK" with no skip.
BA=/pscratch/sd/j/josephrb/fd-ct-5b-addition-20261031; D=$BA/deploy/3b12c451
[ -e "$BA/logs/chain.out" ] && { echo "STOP: already run"; exit 2; }
grep -q "^tests rc=0$" $BA/logs/deploy.log && grep -q "^pins 15 mismatches 0$" $BA/logs/deploy.log \
  && grep -q "^skipped_lines 0$" $BA/logs/deploy.log || { echo "STOP: deploy not clean"; exit 2; }
date -u +%FT%TZ > $BA/logs/chain.start; hostname >> $BA/logs/chain.start
mkdir -p $BA/tmp && cd $BA && eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)" \
  && conda activate $HOME/.conda/envs/root_6_28 && TMPDIR=$BA/tmp timeout 1800 env -u PYTHONPATH python3 -I -B \
  $D/nd-unfolding/fd_cpl_addition.py chain --scratch /pscratch/sd/j/josephrb --run-dir $BA \
  > $BA/logs/chain.out 2> $BA/logs/chain.err; echo "rc=$?" >> $BA/logs/chain.out
date -u +%FT%TZ >> $BA/logs/chain.start
cat $BA/logs/chain.start; tail -n 3 $BA/logs/chain.out; tail -n 5 $BA/logs/chain.err
echo "porcelain_ignored_lines_after_chain $(git -C $D status --porcelain --ignored | wc -l)"
