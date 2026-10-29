#!/bin/bash
# FD-CT-3B-BINDING.md section 3 condition 3: FD-CT-3B-DECLARATION.md section 2.3, verbatim.
P=/pscratch/sd/j/josephrb
B=$P/fd-ct-3b-20261029
D=$B/deploy/e904d635
PY="env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I -B"
echo "mismatch start $(date -u +%FT%TZ) host $(hostname)" >> $B/logs/walls.txt
cd $B && TMPDIR=$B/tmp timeout 120 $PY $D/nd-unfolding/fd_ct_readers.py mismatch \
  --definition $D/nd-unfolding/pv-ladder/readouts/h2_definition.json \
  --s1-npz $P/s1-20261024/s1_assembly.npz --cresp $P/cresp-20261026/out/cresp.npz \
  --closures-dir $B/closures --mp1-unf $P/measurement-paper/phase1/mp1/s1/unf \
  --recoil-readout $D/docs/orchestration/state/measurement-paper/5d-community-20261024/fd/readout/fd_ct_recoil.json \
  --out-json $B/fd_ct_mismatch.json > $B/logs/mismatch.out 2> $B/logs/mismatch.err; echo "rc=$?" >> $B/logs/mismatch.out
echo "mismatch end $(date -u +%FT%TZ)" >> $B/logs/walls.txt
