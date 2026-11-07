O=/pscratch/sd/j/josephrb/cov2d-run-20261104
echo "NOW $(date -u +%FT%TZ)"
echo "== SACCT"
sacct -X -n -P -S 2026-11-04 -u josephrb -o JobID,JobName,State,ElapsedRaw,NNodes,TimelimitRaw,Submit,Start,End
echo "== WALLS"
for f in $O/walls.*.tsv; do b=${f##*/}; awk -F'\t' -v b="$b" '{print b "\t" $0}' "$f"; done
echo "== RUNS"
for T in G18 AR23; do awk -F'\t' -v T=$T 'NR>1 {print T "\t" $0}' $O/tables/runs_$T.tsv; done
echo "== JOBS"
for T in G18 AR23; do cat $O/tables/jobs_$T.tsv; done
