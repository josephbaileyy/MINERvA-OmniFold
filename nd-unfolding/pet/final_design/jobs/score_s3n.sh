#!/bin/bash
# score every COMPLETE S3P seed/pilot run of the N2 arm designs at k = 2..5 (CS1: 2..6) into scored/s3n
B=/pscratch/sd/j/josephrb/pet-final-design-20260925; F=$(git -C $B/repo rev-parse FETCH_HEAD 2>/dev/null)
M=$(ls -td $B/checkouts/*/ | head -1); M=${M%/}; S=$(git -C $M rev-parse HEAD)
O=$B/scored/s3n; mkdir -p $O; cd $O
for c in H2S1T24K5 L128S1T24K5 H2S1E16K5 L128S1E16K5 CS1K6 L64S1K5 H2S1X4K5 L128S1X4K5; do
  runs=$(ls $B/s3p/S3P-$c-DEV*/status.txt 2>/dev/null | xargs grep -lx COMPLETE 2>/dev/null | xargs -r -n1 dirname)
  [ -z "$runs" ] && continue
  ks="2 3 4 5"; [ $c = CS1K6 ] && ks="2 3 4 5 6"
  sbatch --parsable -A m3246 -C cpu -q debug -N 1 -t 00:20:00 -J pfd-score -o $O/slurm-%j.out \
    --export=ALL,MINE=$M,MINE_COMMIT=$S,OUT=$O,LABEL=score-s3n-$c \
    $M/nd-unfolding/pet/final_design/jobs/sbatch_guarded_task.sh nd-unfolding/pet/final_design/analysis/score_design.py \
    --k $ks --row-features $B/rowfeatures/row_features.npz --out-dir $O --run $runs
done
