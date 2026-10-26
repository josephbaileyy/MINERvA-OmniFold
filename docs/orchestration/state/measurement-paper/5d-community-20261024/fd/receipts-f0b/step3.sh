set -u
P=/pscratch/sd/j/josephrb; B=$P/fd-f0b-20261026; D=$B/deploy/c4396756
T=$D/docs/orchestration/state/measurement-paper/5d-community-20261024
PY="env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I -B"
XB="--extra-block $P/cresp-20261026/out/cresp.npz --extra-block-sha256 4d8b579732b79cbbb8e6c9a4f6335c4bda4eae6dd4194241a0d8cd6e7ea8a20a --extra-block-key C_resp --extra-block-name C_resp"
[ "$(tail -1 $B/logs/preserve.out)" = "rc=0" ] || { echo "STOP: step 2 not rc=0"; exit 9; }
test ! -e $B/fd_f0b_readout.json || { echo "STOP: readout exists"; exit 9; }
echo "f0b start $(date -u +%FT%TZ) $(hostname)" > $B/logs/f0b-start.txt
cd $B && TMPDIR=$B/tmp timeout 375 $PY $D/nd-unfolding/fd_f0_regrade.py \
  --definition $D/nd-unfolding/pv-ladder/readouts/h2_definition.json \
  --s1-npz $P/s1-20261024/s1_assembly.npz --s1-json $T/s1/readout/s1_assembly.json \
  --cmodel-npz $P/cmodel5d-20261024/out/cmodel_5d.npz --cmodel-json $D/nd-unfolding/pv-ladder/readouts/cmodel_5d.json \
  --flux-constraint $P/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt \
  --d16-dir $D/docs/orchestration/state/s5p/stage3/f4 --f4-root $P/s5p-20260926/runs/s3r/f4 \
  --stage0-inventory $D/docs/orchestration/state/measurement-paper/5d-design-20261023/stage0/INVENTORY.sha256 \
  --s5e-assess $P/s5e-20260925/runs/cand/assess \
  --stage0c-sums $D/docs/orchestration/state/measurement-paper/5d-design-20261023/stage0/receipts-A/products.sha256 \
  --stage0c-root $P/5d-stage0-20261023 --pvl-products $P/pv-ladder-20261024/products \
  --s5p-sums $D/docs/orchestration/state/s5p/archive/SHA256SUMS-s5p-archive-20261006.txt --s5p-root $P/s5p-20260926 \
  $XB \
  --out-json $B/fd_f0b_readout.json --out-npz $B/fd_f0b_experiments.npz \
  > $B/logs/f0b.out 2> $B/logs/f0b.err; echo "rc=$?" >> $B/logs/f0b.out
echo "f0b end $(date -u +%FT%TZ)" >> $B/logs/f0b-start.txt
tail -8 $B/logs/f0b.out; cat $B/logs/f0b.err | tail -5
