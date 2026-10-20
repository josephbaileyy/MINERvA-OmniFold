#!/bin/bash
# SF-1 input manifest: sha256 of every input file the quarter runs and the statistics read.
S=/pscratch/sd/j/josephrb/methods-paper/sf1-20261019
D=$S/deploy-4f5a613f
NS=/pscratch/sd/j/josephrb/s5p-20260926
OUT=$S/manifest/inputs-sha256.txt
mkdir -p $S/manifest
{
  for f in /pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz \
           /pscratch/sd/j/josephrb/s5c-20260924/runs/p2/bkg_dump.npz \
           $NS/stage3/V/V-s3v.npz \
           $NS/gen5d_fluxfix/nuwro_cv_xsec5d_full.npz $NS/gen5d_fluxfix/genie_cv_xsec5d_full.npz $NS/gen5d_fluxfix/genie_mec_xsec5d_full.npz \
           $NS/stage3/f4/D16-nuwro_cv.npz $NS/stage3/f4/D16-genie_cv.npz $NS/stage3/f4/D16-genie_mec.npz \
           $NS/stage3/m1/fine-minus-mid-nuwro_cv.npz $NS/stage3/m1/fine-minus-mid-genie_cv.npz $NS/stage3/m1/fine-minus-mid-genie_mec.npz \
           $NS/runs/s2/num/data/data_b-_j-.npz $NS/runs/s2/num/data/data_b-_j{1..20}.npz \
           $NS/runs/s3/latunf/lat_*_[01]_b-_j-.npz \
           $D/docs/orchestration/state/s5p/ratios/nullsF/null-nuwro_cv-F.json \
           $D/docs/orchestration/state/s5p/ratios/nullsF/null-genie_cv-F.json \
           $D/docs/orchestration/state/s5p/ratios/nullsF/null-genie_mec-F.json \
           $D/docs/orchestration/state/s5p/prod/design.json \
           $D/docs/orchestration/state/s5p/stage1/stage1_inspect.json \
           $D/docs/orchestration/state/s5c/contract.json ; do
    sha256sum "$f"
  done
  find /pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/bank_sweep_5d_bkgaware/ $NS/bank_detector/ -maxdepth 1 -type f | sort | xargs -n 20 sha256sum
} > $OUT.partial 2> $S/manifest/inputs-sha256.err
mv $OUT.partial $OUT
echo done > $S/manifest/inputs-sha256.done
