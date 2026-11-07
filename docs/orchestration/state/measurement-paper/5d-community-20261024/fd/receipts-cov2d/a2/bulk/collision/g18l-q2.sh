O=/pscratch/sd/j/josephrb/cov2d-run-20261104
for d in X_G18 L_G18_BeamAngleX_0; do echo "== $d"; stat -c '%n %y %s' "$O/out/$d" "$O/out/$d"/* 2>&1; done
echo "== SHA256SUMS lines naming them"; grep -H -E 'X_G18/|L_G18_BeamAngleX_0/' "$O"/SHA256SUMS.* 2>&1
echo "== walls naming them"; grep -H -E '^(X_G18|L_G18_BeamAngleX_0)	' "$O"/walls.*.tsv 2>&1
echo "== exists-not-overwritten in any cov2d log"; grep -c 'exists; not overwritten' "$O"/logs/cov2d-*.out 2>&1 | grep -v ':0$'
echo "== G18_L walls"; cat "$O"/walls.G18_L.*.tsv
echo "== pilot entries"; grep -E 'job=pilot' "$O/submissions.log"
echo "== pilot runs table"; ls "$O/tables"; grep -h -P '^pilot\t' "$O"/tables/runs_*.tsv | cut -f1-4
