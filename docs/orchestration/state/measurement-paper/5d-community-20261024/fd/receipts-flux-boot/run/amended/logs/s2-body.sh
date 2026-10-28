P=/pscratch/sd/j/josephrb
B=$P/fd-flux-boot-20261028
D=$B/deploy/91312bc8
T=$D/docs/orchestration/state/measurement-paper/5d-community-20261024
PY="env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I -B"
echo "s2 start $(date -u +%FT%TZ) $(hostname)" > $B/logs/s2.stamps
cd $B && TMPDIR=$B/tmp timeout 375 $PY $D/nd-unfolding/fd_flux_boot.py \
  --definition $D/nd-unfolding/pv-ladder/readouts/h2_definition.json \
  --s1-npz $P/s1-20261024/s1_assembly.npz --s1-json $T/s1/readout/s1_assembly.json \
  --cmodel-json $D/nd-unfolding/pv-ladder/readouts/cmodel_5d.json \
  --s5p-sums $D/docs/orchestration/state/s5p/archive/SHA256SUMS-s5p-archive-20261006.txt --s5p-root $P/s5p-20260926 \
  --g-readout $T/fd/readout/fd_g_readout.json \
  --extra-block $P/cresp-20261026/out/cresp.npz \
  --extra-block-sha256 4d8b579732b79cbbb8e6c9a4f6335c4bda4eae6dd4194241a0d8cd6e7ea8a20a \
  --extra-block-key C_resp --extra-block-name C_resp --extra-block-role adopted \
  --flux-dir $T/s1/readout/s1_assembly \
  --flux-constraint $P/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt \
  --out-json $B/fd_flux_boot_readout.json > $B/logs/boot.out 2> $B/logs/boot.err; echo "rc=$?" >> $B/logs/boot.out
echo "s2 end $(date -u +%FT%TZ) $(hostname)" >> $B/logs/s2.stamps
