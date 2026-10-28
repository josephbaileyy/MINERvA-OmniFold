# Step 12 (FD-F1-BINDING.md section 4.6; FD-F1-DECLARATION.md section 5): the F1 grade on a login node at 0 node-h,
# in F0b's environment (root_6_28, Python 3.11.14, numpy 1.26.4, env -u PYTHONPATH ... -I -B). The command is F0b's
# recorded argv (fd/receipts-f0b/step3.sh: every input path in F0b's own deploy c4396756, the same C_resp extra
# block), with the program from a deploy of the second receipt commit (which carries the committed product
# manifest) and the declared F1 options added. Control 9 checks F0b's 18 truths grade exactly as fd_f0b_readout.json
# records them. Runs detached (nohup); writes only $OUT/deploy/grade, $OUT/grade and $OUT/tmp-grade. Never touches
# $OUT/f1b or $OUT/f1b2.
set -u
P=/pscratch/sd/j/josephrb; OUT=$P/fd-f1-20261027
GPIN=da5f157f4a4780eaefddb0ac8536138fd35ddfb2
DG=$OUT/deploy/grade; G=$OUT/grade
B=$P/fd-f0b-20261026; D=$B/deploy/c4396756
T=$D/docs/orchestration/state/measurement-paper/5d-community-20261024
TG=$DG/docs/orchestration/state/measurement-paper/5d-community-20261024
RC=$TG/fd/receipts-f1/run/cluster
PY="env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I -B"
L=$OUT/logs/grade.log
for x in $DG $G $OUT/tmp-grade; do [ -e "$x" ] && { echo "STOP: $x exists" > $L; exit 3; }; done
{ date -u +%FT%TZ; hostname
  git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold $DG && git -C $DG checkout --quiet --detach $GPIN; echo "clone rc=$?"
  echo "HEAD $(git -C $DG rev-parse HEAD)"; echo "porcelain_ignored_lines $(git -C $DG status --porcelain --ignored | wc -l)"
  echo "F0b deploy HEAD $(git -C $D rev-parse HEAD), porcelain_ignored_lines $(git -C $D status --porcelain --ignored | wc -l)"
  $PY -c "import sys, numpy; print('python', sys.version.split()[0], 'numpy', numpy.__version__)"
  echo "manifest committed vs cluster: $(sha256sum $RC/manifest/f1-products-SHA256SUMS | cut -c1-64) $(sha256sum $OUT/manifest/f1-products-SHA256SUMS | cut -c1-64)"
} > $L 2>&1
[ "$(git -C $DG rev-parse HEAD)" = "$GPIN" ] && [ "$(git -C $DG status --porcelain --ignored | wc -l)" -eq 0 ] || { echo "STOP: grade deploy checks" >> $L; exit 3; }
mkdir -p $G $OUT/tmp-grade
XB="--extra-block $P/cresp-20261026/out/cresp.npz --extra-block-sha256 4d8b579732b79cbbb8e6c9a4f6335c4bda4eae6dd4194241a0d8cd6e7ea8a20a --extra-block-key C_resp --extra-block-name C_resp"
F1="--f1-prep-sums $RC/f1b3/prep/f1-prep-SHA256SUMS --f1-prep-sums-sha256 981b188b03a7e75b904489fa1bf15bd818ef4b72f93a8beba4a906eb3122a480 \
 --f1-products-sums $RC/manifest/f1-products-SHA256SUMS --f1-products-sums-sha256 fdb0274053e9946177376913f6145c024c24582f94607d1f5fd05271642fec09 \
 --f1-root $OUT/f1c --f0b-readout $TG/fd/readout/fd_f0b_readout.json --f0b-readout-sha256 b9db935a3187646ba2accaf3865cf4aa26ad72676063c58e7f5e6220224ef17b"
echo "grade start $(date -u +%FT%TZ)" >> $L
cd $G && TMPDIR=$OUT/tmp-grade timeout 900 $PY $DG/nd-unfolding/fd_f0_regrade.py \
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
  $XB $F1 \
  --out-json $G/fd_f1_readout.json --out-npz $G/fd_f1_experiments.npz \
  > $OUT/logs/grade.out 2> $OUT/logs/grade.err; echo "grade rc=$?" >> $L
echo "grade end $(date -u +%FT%TZ)" >> $L
echo "porcelain_ignored_lines_after $(git -C $DG status --porcelain --ignored | wc -l)" >> $L
echo "done: $(date -u +%FT%TZ)" >> $L
