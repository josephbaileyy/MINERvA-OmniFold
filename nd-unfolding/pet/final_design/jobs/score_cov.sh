#!/bin/bash
# Score one coverage manifest (Amendment 5; after its UNBLIND coverage amendment is committed and deployed):
# analysis/score_design.py at the finalist's frozen K on every member run, with the FB population target of the
# manifest's case (report-only vs_population), into $B/scored/<stem>, in guarded CPU-debug jobs of <= 200 runs
# (~4 s per run). Refuses unless the deployed checkout's protocol carries an UNBLIND coverage heading.
#   usage (cluster): bash score_cov.sh <deployed checkout sha> <manifest stem> <K> <population target json>
set -euo pipefail
B=/pscratch/sd/j/josephrb/pet-final-design-20260925; S=$1; STEM=$2; K=$3; POP=$4; M=$B/checkouts/${S:0:8}
[[ "$(git -C "$M" rev-parse HEAD)" == "$S" ]] || { echo "checkout $M not at $S" >&2; exit 2; }
P=$M/nd-unfolding/pet/final_design/PROTOCOL-20260925.md
grep -qE '^### Amendment [^ ]+ .*\bUNBLIND coverage\b' "$P" || { echo "no UNBLIND coverage amendment in $P" >&2; exit 2; }
[[ -f "$POP" ]] || { echo "no population target $POP" >&2; exit 2; }
R=$M/nd-unfolding/pet/final_design/runs/$STEM.tsv; O=$B/scored/$STEM; mkdir -p "$O"; cd "$O"
runs=(); while IFS= read -r n; do runs+=("$B/s5/$n"); done < <(cut -f1 "$R" | grep -v '^#')
per=200; parts=$(( (${#runs[@]} + per - 1) / per ))
(( parts <= 5 )) || { echo "$parts jobs exceed the CPU-debug submit limit" >&2; exit 2; }
for (( p = 0; p < parts; p++ )); do
  chunk=("${runs[@]:$((p * per)):$per}")
  sbatch --parsable -A m3246 -C cpu -q debug -N 1 -t 00:30:00 -J pfd-score -o "$O/slurm-%j.out" \
    --export=ALL,MINE="$M",MINE_COMMIT="$S",OUT="$O",LABEL="score-$STEM-$p" \
    "$M/nd-unfolding/pet/final_design/jobs/sbatch_guarded_task.sh" \
    nd-unfolding/pet/final_design/analysis/score_design.py --k "$K" \
    --row-features "$B/rowfeatures/row_features.npz" --population-target "$POP" --out-dir "$O" --run "${chunk[@]}"
done
