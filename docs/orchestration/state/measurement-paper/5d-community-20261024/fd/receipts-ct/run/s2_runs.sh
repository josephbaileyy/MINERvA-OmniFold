#!/bin/bash
# FD-CT-READERS-BINDING.md section 3 condition 2: FD-CT-READERS-DECLARATION.md section 2.2, verbatim, in its order and
# under its timeouts. A STOP in one reader does not stop the others. Nothing is rerun.
P=/pscratch/sd/j/josephrb
B=$P/fd-ct-readers-20261028
D=$B/deploy/28ea789e
PY="env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I -B"
grep -q "tests rc=0" $B/logs/deploy.log || { echo "STOP: deploy tests did not pass"; exit 9; }
stamp() { date -u +%FT%TZ; }
echo "recoil start $(stamp)" >> $B/logs/walls.txt
cd $B && TMPDIR=$B/tmp timeout 75 $PY $D/nd-unfolding/fd_ct_readers.py recoil \
  --definition $D/nd-unfolding/pv-ladder/readouts/h2_definition.json \
  --s1-npz $P/s1-20261024/s1_assembly.npz --cresp $P/cresp-20261026/out/cresp.npz \
  --w2b-unf $P/w2-recoil-20261006/w2b/unf \
  --out-json $B/fd_ct_recoil.json > $B/logs/recoil.out 2> $B/logs/recoil.err; echo "rc=$?" >> $B/logs/recoil.out
echo "recoil end $(stamp)" >> $B/logs/walls.txt
echo "chi2 start $(stamp)" >> $B/logs/walls.txt
cd $B && TMPDIR=$B/tmp timeout 375 $PY $D/nd-unfolding/fd_ct_readers.py chi2 \
  --definition $D/nd-unfolding/pv-ladder/readouts/h2_definition.json \
  --s1-npz $P/s1-20261024/s1_assembly.npz --cresp $P/cresp-20261026/out/cresp.npz \
  --s5p-sums $D/docs/orchestration/state/s5p/archive/SHA256SUMS-s5p-archive-20261006.txt --s5p-root $P/s5p-20260926 \
  --f0b-readout $D/docs/orchestration/state/measurement-paper/5d-community-20261024/fd/readout/fd_f0b_readout.json \
  --flux-constraint $P/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt \
  --out-json $B/fd_ct_chi2.json > $B/logs/chi2.out 2> $B/logs/chi2.err; echo "rc=$?" >> $B/logs/chi2.out
echo "chi2 end $(stamp)" >> $B/logs/walls.txt
echo "period start $(stamp)" >> $B/logs/walls.txt
cd $B && TMPDIR=$B/tmp timeout 75 $PY $D/nd-unfolding/fd_ct_readers.py period \
  --definition $D/nd-unfolding/pv-ladder/readouts/h2_definition.json \
  --s1-npz $P/s1-20261024/s1_assembly.npz --cresp $P/cresp-20261026/out/cresp.npz \
  --playlist-npz $P/tmp-playlist-term-20261016/out/playlist_term.npz \
  --playlist-json $D/docs/orchestration/state/2d-closeout/playlist-term/outputs/playlist_term.json \
  --central $P/s5p-20260926/runs/s2/num/data/data_b-_j-.npz --prior $P/s5p-20260926/gen5d/mnvtune_v1_xsec5d.npz \
  --out-json $B/fd_ct_period.json > $B/logs/period.out 2> $B/logs/period.err; echo "rc=$?" >> $B/logs/period.out
echo "period end $(stamp)" >> $B/logs/walls.txt
echo "host $(hostname)" >> $B/logs/walls.txt
echo DONE > $B/logs/runs.done
