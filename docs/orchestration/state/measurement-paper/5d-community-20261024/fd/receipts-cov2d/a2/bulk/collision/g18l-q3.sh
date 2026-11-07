O=/pscratch/sd/j/josephrb/cov2d-run-20261104
M=a60547692df5f963e428cdfe4661fc51ab785b7b
date -u +%FT%TZ
sha256sum $O/tables/runs_G18.tsv $O/tables/runs_AR23.tsv
echo "== SACCT"
sacct -X -n -P -S 2026-11-06 -u josephrb -o JobID,JobName,State,Start | grep '|cov2d-'
echo "== SUBS"
grep "M=$M" $O/submissions.log
echo "== LABELS"
for t in G18 AR23; do
  tail -n +2 $O/tables/runs_$t.tsv | while IFS=$'\t' read -r job ln label rest; do
    if [ -e "$O/out/$label" ]; then printf '%s\t%s\t%s\t1\t%s\n' "$t" "$job" "$label" "$(stat -c %Y "$O/out/$label")"
    else printf '%s\t%s\t%s\t0\t-\n' "$t" "$job" "$label"; fi
  done
done
echo "== OUT-NOT-IN-TABLES"
ls $O/out | sort > /dev/shm/josephrb-labels-out.$$ 
for t in G18 AR23 pilot; do tail -n +2 $O/tables/runs_$t.tsv | cut -f3; done | sort -u | comm -23 /dev/shm/josephrb-labels-out.$$ - 
rm -f /dev/shm/josephrb-labels-out.$$ && echo "removed /dev/shm/josephrb-labels-out.$$ rc=$?"
