# Step 1 (FD-G-FIGURES-DECLARATION.md section 2.1, bound by FD-G-FIGURES-AND-DATA-PRODUCT-BINDING.md): deploy and tests.
P=/pscratch/sd/j/josephrb
B=$P/fd-g-figures-20261027
PIN=933cfe354ba6a3505c5b232df33d3d905de1de40
D=$B/deploy/933cfe35
T=$D/docs/orchestration/state/measurement-paper/5d-community-20261024
if [ -e "$B" ]; then echo "STOP: $B exists"; exit 3; fi
mkdir -p $B/logs $B/tmp
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold $D && git -C $D checkout --quiet --detach $PIN
{ date -u +%FT%TZ; hostname; git -C $D rev-parse HEAD
  echo "porcelain_ignored_lines $(git -C $D status --porcelain --ignored | wc -l)"
  cd $D && sha256sum nd-unfolding/fd_g_figures.py nd-unfolding/fd_g_figures_check.py nd-unfolding/fd_data_product.py \
    nd-unfolding/tests/test_fd_g_figures.py nd-unfolding/tests/test_fd_data_product.py \
    publication/release/figs/make_figs.py nd-unfolding/fd_g_compare.py nd-unfolding/s1_assemble.py \
    nd-unfolding/s5p_stage1_inspect.py nd-unfolding/pv-ladder/readouts/h2_definition.json \
    $T/fd/readout/fd_g_readout.json $T/fd/readout/fd_g_diag_readout.json $T/fd/readout/fd_g_followup_readout.json \
    $T/fd/readout/fd_g_sens2_readout.json $T/fd/readout/fd_f0b_readout.json $T/s1/readout/s1_assembly.json \
    docs/orchestration/state/measurement-scoping/assigned-uncertainties/cresp/cresp.json \
    docs/orchestration/state/measurement-scoping/assigned-uncertainties/cresp/CRESP-REPORT.md \
    docs/orchestration/state/s5p/stage1/stage1_inspect.json nd-unfolding/tests/test_fd_g_compare.py \
    $T/FD-G-FIGURES-DECLARATION.md $T/FD-DATA-PRODUCT-DECLARATION.md; } > $B/logs/deploy.log 2>&1
cd $D/nd-unfolding/tests && TMPDIR=$B/tmp env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -B -m unittest \
  test_fd_g_figures test_fd_data_product test_fd_g_compare > $B/logs/deploy-tests.log 2>&1; echo "tests rc=$?" >> $B/logs/deploy.log
echo "porcelain_ignored_lines_after_tests $(git -C $D status --porcelain --ignored | wc -l)" >> $B/logs/deploy.log
cat $B/logs/deploy.log; grep -E "^Ran |^OK|^FAILED" $B/logs/deploy-tests.log
