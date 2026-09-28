#!/bin/bash
# Score the look-1 FB rows (after the UNBLIND amendment is committed and deployed): one guarded CPU-debug job
# per frozen K, analysis/score_design.py at each run's frozen K, into $B/scored/fb. score_design.py itself
# refuses final-bank runs while the protocol carries no UNBLIND heading (Amendment 2c item 9).
#   usage (cluster, from any dir): bash score_fb.sh <deployed checkout sha>
set -euo pipefail
B=/pscratch/sd/j/josephrb/pet-final-design-20260925; S=$1; M=$B/checkouts/${S:0:8}
[[ "$(git -C "$M" rev-parse HEAD)" == "$S" ]] || { echo "checkout $M not at $S" >&2; exit 2; }
R=$M/nd-unfolding/pet/final_design/runs; O=$B/scored/fb; mkdir -p "$O"; cd "$O"
# five jobs (the CPU-debug submit limit): K3 (anchors, 240 runs) and K4/K5 (352 runs each) split in halves;
# scoring takes ~4 s per run, so each job stays well inside 30 min
for K in 3 4 5; do
  runs=()
  for spec in s4f_a3:s4f s4f_a3e:s4f s4s_a3:s4s s4s_a3e_n40:s4s; do
    stem=${spec%%:*}; out=$B/${spec##*:}
    while IFS= read -r n; do runs+=("$out/$n"); done < <(cut -f1 "$R/$stem.tsv" | grep -v '^#' | grep -E "K${K}-FB" || true)
  done
  (( ${#runs[@]} )) || continue
  parts=2; [[ $K == 3 ]] && parts=1
  per=$(( (${#runs[@]} + parts - 1) / parts ))
  for (( p = 0; p < parts; p++ )); do
    chunk=("${runs[@]:$((p * per)):$per}")
    (( ${#chunk[@]} )) || continue
    sbatch --parsable -A m3246 -C cpu -q debug -N 1 -t 00:30:00 -J pfd-score -o "$O/slurm-%j.out" \
      --export=ALL,MINE="$M",MINE_COMMIT="$S",OUT="$O",LABEL="score-fb-K$K-$p" \
      "$M/nd-unfolding/pet/final_design/jobs/sbatch_guarded_task.sh" \
      nd-unfolding/pet/final_design/analysis/score_design.py --k "$K" \
      --row-features "$B/rowfeatures/row_features.npz" --out-dir "$O" --run "${chunk[@]}"
  done
done
