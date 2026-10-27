# Step 2 (FD-DATA-PRODUCT-DECLARATION.md section 2.2, bound): the data-product readout.
P=/pscratch/sd/j/josephrb
B=$P/fd-g-figures-20261027
D=$B/deploy/933cfe35
T=$D/docs/orchestration/state/measurement-paper/5d-community-20261024
PY="env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I -B"
date -u +%FT%TZ > $B/logs/data-product.start; hostname >> $B/logs/data-product.start
cd $B && TMPDIR=$B/tmp timeout 75 $PY $D/nd-unfolding/fd_data_product.py \
  --s1-npz $P/s1-20261024/s1_assembly.npz --s1-json $T/s1/readout/s1_assembly.json \
  --cresp-npz $P/cresp-20261026/out/cresp.npz \
  --cresp-json $D/docs/orchestration/state/measurement-scoping/assigned-uncertainties/cresp/cresp.json \
  --cresp-report $D/docs/orchestration/state/measurement-scoping/assigned-uncertainties/cresp/CRESP-REPORT.md \
  --g-readout $T/fd/readout/fd_g_readout.json --definition $D/nd-unfolding/pv-ladder/readouts/h2_definition.json \
  --stage1 $D/docs/orchestration/state/s5p/stage1/stage1_inspect.json \
  --out-dir $B/data-product > $B/logs/data-product.out 2> $B/logs/data-product.err; echo "rc=$?" >> $B/logs/data-product.out
date -u +%FT%TZ >> $B/logs/data-product.start
cat $B/logs/data-product.start; grep -v "^PASS" $B/logs/data-product.out; grep -c "^PASS" $B/logs/data-product.out; cat $B/logs/data-product.err | head -5
