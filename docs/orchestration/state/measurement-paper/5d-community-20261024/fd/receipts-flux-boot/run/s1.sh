# Step 1 (FD-FLUX-BOOT-DECLARATION.md section 2.1, bound by FD-FLUX-BOOT-BINDING.md condition 1): deploy and tests.
P=/pscratch/sd/j/josephrb
B=$P/fd-flux-boot-20261027
PIN=f370da5bef042c47573a8348f51a94e43de5c432
D=$B/deploy/f370da5b
if [ -e "$B" ]; then echo "STOP: $B exists"; exit 3; fi
mkdir -p $B/logs $B/tmp
{ echo "s1 start $(date -u +%FT%TZ) $(hostname)"; } > $B/logs/s1.stamps
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold $D && git -C $D checkout --quiet --detach $PIN
{ date -u +%FT%TZ; hostname; git -C $D rev-parse HEAD
  echo "porcelain_ignored_lines $(git -C $D status --porcelain --ignored | wc -l)"
  cd $D && sha256sum nd-unfolding/fd_flux_boot.py nd-unfolding/tests/test_fd_flux_boot.py nd-unfolding/fd_g_followup.py \
    nd-unfolding/fd_g_diag.py nd-unfolding/fd_g_compare.py nd-unfolding/s1_assemble.py nd-unfolding/s5p_stage1_inspect.py \
    nd-unfolding/pv-ladder/readouts/h2_definition.json \
    docs/orchestration/state/measurement-paper/5d-community-20261024/fd/readout/fd_g_readout.json \
    docs/orchestration/state/measurement-paper/5d-community-20261024/s1/readout/s1_assembly.json \
    docs/orchestration/state/measurement-paper/5d-community-20261024/FD-FLUX-BOOT-DECLARATION.md; } > $B/logs/deploy.log 2>&1
cd $D/nd-unfolding/tests && TMPDIR=$B/tmp env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -B -m unittest \
  test_fd_flux_boot test_fd_g_followup test_fd_g_diag test_fd_g_compare test_s1_assemble test_s1_scripts_isolated \
  > $B/logs/deploy-tests.log 2>&1; echo "tests rc=$?" >> $B/logs/deploy.log
echo "porcelain_ignored_lines_after_tests $(git -C $D status --porcelain --ignored | wc -l)" >> $B/logs/deploy.log
echo "s1 end $(date -u +%FT%TZ) $(hostname)" >> $B/logs/s1.stamps
cat $B/logs/s1.stamps $B/logs/deploy.log; grep -E "^Ran |^OK|^FAILED" $B/logs/deploy-tests.log
