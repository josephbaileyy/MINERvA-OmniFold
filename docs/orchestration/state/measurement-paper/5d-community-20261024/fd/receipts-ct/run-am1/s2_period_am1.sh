#!/bin/bash
# FD-CT-READERS-BINDING-AMENDMENT-1.md section 3 condition 2: the declaration's section 2.2 period command, unchanged
# except for $B and $D, under its 75 s timeout. Nothing is rerun.
P=/pscratch/sd/j/josephrb
B=$P/fd-ct-readers-am1-20261029
D=$B/deploy/bb8dc101
PY="env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I -B"
grep -q "tests rc=0" $B/logs/deploy.log || { echo "STOP: deploy tests did not pass"; exit 9; }
stamp() { date -u +%FT%TZ; }
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
