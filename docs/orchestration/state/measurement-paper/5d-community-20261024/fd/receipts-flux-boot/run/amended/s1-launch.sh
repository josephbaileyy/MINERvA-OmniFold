# Step 1 (FD-FLUX-BOOT-DECLARATION.md section 2.1 as amended by -AMENDMENT-1, bound by FD-FLUX-BOOT-BINDING-AMENDMENT-1.md
# section 3): deploy and tests, launched detached on a login node (nohup) and polled.
P=/pscratch/sd/j/josephrb
B=$P/fd-flux-boot-20261028
if [ -e "$B" ]; then echo "STOP: $B exists"; exit 3; fi
mkdir -p $B/logs $B/tmp
cat > $B/logs/s1-body.sh <<'BODY'
P=/pscratch/sd/j/josephrb
B=$P/fd-flux-boot-20261028
PIN=91312bc8f22b90e90724741e6edffdb1b15f0c72
D=$B/deploy/91312bc8
echo "s1 start $(date -u +%FT%TZ) $(hostname)" > $B/logs/s1.stamps
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold $D && git -C $D checkout --quiet --detach $PIN
{ date -u +%FT%TZ; hostname; git -C $D rev-parse HEAD
  echo "porcelain_ignored_lines $(git -C $D status --porcelain --ignored | wc -l)"
  cd $D && sha256sum nd-unfolding/fd_flux_boot.py nd-unfolding/tests/test_fd_flux_boot.py nd-unfolding/fd_g_followup.py \
    nd-unfolding/fd_g_diag.py nd-unfolding/fd_g_compare.py nd-unfolding/s1_assemble.py nd-unfolding/s5p_stage1_inspect.py \
    nd-unfolding/pv-ladder/readouts/h2_definition.json \
    docs/orchestration/state/measurement-paper/5d-community-20261024/fd/readout/fd_g_readout.json \
    docs/orchestration/state/measurement-paper/5d-community-20261024/s1/readout/s1_assembly.json \
    docs/orchestration/state/measurement-paper/5d-community-20261024/FD-FLUX-BOOT-DECLARATION.md \
    docs/orchestration/state/measurement-paper/5d-community-20261024/FD-FLUX-BOOT-DECLARATION-AMENDMENT-1.md; } > $B/logs/deploy.log 2>&1
cd $D/nd-unfolding/tests && TMPDIR=$B/tmp env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -B -m unittest \
  test_fd_flux_boot test_fd_g_followup test_fd_g_diag test_fd_g_compare test_s1_assemble test_s1_scripts_isolated \
  > $B/logs/deploy-tests.log 2>&1; echo "tests rc=$?" >> $B/logs/deploy.log
echo "porcelain_ignored_lines_after_tests $(git -C $D status --porcelain --ignored | wc -l)" >> $B/logs/deploy.log
echo "s1 end $(date -u +%FT%TZ) $(hostname)" >> $B/logs/s1.stamps
BODY
nohup bash $B/logs/s1-body.sh > $B/logs/s1.nohup 2>&1 < /dev/null &
echo "launched pid $! on $(hostname) at $(date -u +%FT%TZ)"
