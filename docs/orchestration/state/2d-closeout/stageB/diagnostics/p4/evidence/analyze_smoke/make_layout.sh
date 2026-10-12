#!/bin/bash
# Smoke layout for analyze_p4.py from the one-file smoke run (smoke/): 1A <- patched_on, ctl1A <- unpatched.
# provenance.txt is RECONSTRUCTED from the smoke run (binary sha256 measured now; rc from run.log).
NS=/pscratch/sd/j/josephrb/2d-closeout-stageB-diag-20261012/p4
for pair in 1A:patched_on:patched ctl1A:unpatched:unpatched; do
  IFS=: read tag v b <<< "$pair"
  d=$NS/analyze_smoke/out/$tag
  ln -sf $NS/smoke/$v/runEventLoopOmniFold.root $d/
  [ -e $NS/smoke/$v/g1_census.root ] && ln -sf $NS/smoke/$v/g1_census.root $d/
  { echo "SMOKE LAYOUT (reconstructed from smoke/$v)"
    echo "bin=$NS/build/$b/runEventLoopOmniFold sha256=$(sha256sum $NS/build/$b/runEventLoopOmniFold | cut -c1-64)"
    echo "$(grep -a '^rc=' $NS/smoke/$v/run.log | tail -1) end=smoke"; } > $d/provenance.txt
done
