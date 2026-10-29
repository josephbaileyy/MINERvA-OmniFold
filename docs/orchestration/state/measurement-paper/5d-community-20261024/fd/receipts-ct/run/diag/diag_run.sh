#!/bin/bash
# The director's ruling of 2026-10-29, option (a), once: diag_period.py on the deployed pin's code, with section 2.2's
# period argv except --out-json, which points at a path that is never written.
P=/pscratch/sd/j/josephrb
B=$P/fd-ct-readers-20261028
D=$B/deploy/28ea789e
cd $B/diag && TMPDIR=$B/tmp env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I -B $B/diag/diag_period.py $D period \
  --definition $D/nd-unfolding/pv-ladder/readouts/h2_definition.json \
  --s1-npz $P/s1-20261024/s1_assembly.npz --cresp $P/cresp-20261026/out/cresp.npz \
  --playlist-npz $P/tmp-playlist-term-20261016/out/playlist_term.npz \
  --playlist-json $D/docs/orchestration/state/2d-closeout/playlist-term/outputs/playlist_term.json \
  --central $P/s5p-20260926/runs/s2/num/data/data_b-_j-.npz --prior $P/s5p-20260926/gen5d/mnvtune_v1_xsec5d.npz \
  --out-json $B/diag/never-written.json > $B/diag/diag.out 2> $B/diag/diag.err; echo "rc=$?" >> $B/diag/diag.out
echo "host $(hostname) $(date -u +%FT%TZ)" >> $B/diag/diag.out
