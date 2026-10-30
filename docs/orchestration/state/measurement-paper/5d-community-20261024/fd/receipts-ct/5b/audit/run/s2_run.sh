# 5B audit step 2 (FD-CT-5B-AUDIT-DECLARATION.md section 10.2; FD-CT-5B-AUDIT-BINDING.md condition 2): the reader, once, login node.
# Run only after s1_deploy.sh shows HEAD = pin, 0/0 porcelain lines, 19/19 pins and "OK" with no skip.
P=/pscratch/sd/j/josephrb; BA=$P/fd-ct-5b-audit-20261030; D=$BA/deploy/6dd41539
[ -e "$BA/fd_ct_5b_audit.json" ] && { echo "STOP: readout exists"; exit 2; }
[ -e "$BA/logs/audit.out" ] && { echo "STOP: already run"; exit 2; }
mkdir -p $BA/tmp $BA/logs && cd $BA && eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)" \
  && conda activate $HOME/.conda/envs/root_6_28 && TMPDIR=$BA/tmp timeout 1200 env -u PYTHONPATH python3 -I -B \
  $D/nd-unfolding/fd_ct_5b_audit.py \
  --definition $D/nd-unfolding/pv-ladder/readouts/h2_definition.json \
  --s1-npz $P/s1-20261024/s1_assembly.npz --cresp $P/cresp-20261026/out/cresp.npz \
  --cmodel-json $D/nd-unfolding/pv-ladder/readouts/cmodel_5d.json --b5 $P/fd-ct-5b-20261030 \
  --readout-5b $D/docs/orchestration/state/measurement-paper/5d-community-20261024/fd/readout/fd_ct_5b_periods.json \
  --readout-5a $D/docs/orchestration/state/measurement-paper/5d-community-20261024/fd/readout/fd_ct_period.json \
  --playlist-npz $P/tmp-playlist-term-20261016/out/playlist_term.npz \
  --playlist-json $D/docs/orchestration/state/2d-closeout/playlist-term/outputs/playlist_term.json \
  --analysis-2d $D/docs/orchestration/state/2d-closeout/period-unfold-20261014/outputs/analysis.json \
  --central $P/s5p-20260926/runs/s2/num/data/data_b-_j-.npz \
  --out-json $BA/fd_ct_5b_audit.json > $BA/logs/audit.out 2> $BA/logs/audit.err; echo "rc=$?" >> $BA/logs/audit.out
{ date -u +%FT%TZ; hostname; tail -n 1 $BA/logs/audit.out
  [ -e $BA/fd_ct_5b_audit.json ] && sha256sum $BA/fd_ct_5b_audit.json; } > $BA/logs/run.log
cat $BA/logs/run.log
