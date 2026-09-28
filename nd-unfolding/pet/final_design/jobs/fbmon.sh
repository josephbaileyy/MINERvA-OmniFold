#!/bin/bash
# FB look-1 monitor: exits when all look-1 rows are COMPLETE, when no new completion for 2 h, or when none of the
# watcher-managed allocations exists (the watcher may run on another login node, so ps cannot see it)
B=/pscratch/sd/j/josephrb/pet-final-design-20260925; R=$B/checkouts/04703b90/nd-unfolding/pet/final_design/runs
count() { local c=0 s; for m in s4f_a3 s4s_a3 s4f_a3e s4s_a3e_n40; do out=$B/s4f; [[ $m == s4s* ]] && out=$B/s4s
  for n in $(cut -f1 $R/$m.tsv | grep -v "^#"); do s=$(timeout 5 cat $out/$n/status.txt 2>/dev/null); [ "$s" = COMPLETE ] && c=$((c+1)); done; done; echo $c; }
last=$(count); t0=$(date +%s)
for i in $(seq 1 96); do
  sleep 300
  a=$(timeout 30 squeue --me -h -n pfd-inter1,pfd-inter2,pfd-sint1,pfd-sint2 2>/dev/null | wc -l)
  [ "$a" -eq 0 ] && { sleep 600; a=$(timeout 30 squeue --me -h -n pfd-inter1,pfd-inter2,pfd-sint1,pfd-sint2 | wc -l); [ "$a" -eq 0 ] && { echo "NO WATCHER ALLOCATIONS at $(date -u)"; break; }; }
  c=$(count)
  [ "$c" -ge 944 ] && { echo "ALL LOOK-1 COMPLETE at $(date -u)"; break; }
  if [ "$c" -gt "$last" ]; then last=$c; t0=$(date +%s); fi
  (( $(date +%s) - t0 > 7200 )) && { echo "STALL: no completion in 2 h at $(date -u)"; break; }
done
echo "look-1 complete $(count)/944 at $(date -u)"; timeout 30 squeue --me -h -o "%j %q %T" | grep -v s5p | sort | uniq -c
