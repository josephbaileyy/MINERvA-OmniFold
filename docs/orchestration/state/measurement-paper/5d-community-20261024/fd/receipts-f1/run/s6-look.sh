# Step 6 (read-only, login node): F1a' job 60425719's records after its FAILED 3:0 (the budget2 gate's STOP, exit 3).
# Lists what is fetched into cluster/f1a2/ and cluster/logs/, with sha256 for the receipt check; counts each
# re-pilot gevgen log's DFRKinematics retries; writes nothing on the cluster.
OUT=/pscratch/sd/j/josephrb/fd-f1-20261027
date -u +%FT%TZ; hostname
sacct -j 60425719 -P -o JobID,JobName,State,ExitCode,Start,End,Elapsed,MaxRSS,AllocTRES,NodeList
echo "--- per-phase stamps of every re-pilot run (start, gevgen rc, gntpc done)"
for f in $OUT/f1a2/logs/gen_*_s6*.log; do
  printf '%s ' "$(basename $f)"; grep -E ' start | rc=|gntpc done' $f | sed -E 's/.*(start|rc=[0-9]+|gntpc done) ([0-9-]+ [0-9:]+) UTC/\1 \2/' | tr '\n' ';'; echo
done
echo "--- DFRKinematics 'Trying' lines per gevgen log: total, and longest run before a 'Selected x,y'"
for d in $OUT/f1a2/work/*/s*; do
  awk -v n="${d#$OUT/f1a2/work/}" '/DFRKinematicsGenerator.*Trying:/{c++; if(c>m)m=c; t++; next} /Selected x,y/{c=0}
    END{printf "%s trying_total=%d max_consecutive=%d lines=%d\n", n, t, m, NR}' $d/gevgen.log
done
echo "--- fetched files"
cd $OUT && sha256sum f1a2/budget2.json f1a2/f1a2-SHA256SUMS f1a2/reused.sha256 f1a2/logs/* f1a2/runs/*/*.time \
  logs/fd_f1a2_60425719.out logs/deploy2.log logs/deploy2-*.log logs/expected-sha256-2.txt logs/reused-2.sha256
