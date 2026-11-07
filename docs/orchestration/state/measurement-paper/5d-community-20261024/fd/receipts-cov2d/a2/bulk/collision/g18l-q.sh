O=/pscratch/sd/j/josephrb/cov2d-run-20261104
L=$O/logs/cov2d-G18_L-60895948.out
wc -l "$L"; sha256sum "$L" "$O/logs/check-G18_L-60895948.json" "$O/logs/mat-60895948.json"
echo ==== LOG-FILTERED-TAIL
grep -nvE 'rootmap|TInterpreter|^$' "$L" | tail -60
echo ==== CHECK
cat "$O/logs/check-G18_L-60895948.json"; echo
echo ==== TMP
ls -la "$O/tmp/60895948" | head
echo ==== SUBMISSIONS
grep 'job=G18_L ' "$O/submissions.log"
