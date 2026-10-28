# Step 9 (read-only, login node): F1b' job 60436278's records after COMPLETED 0:0, listed with sha256 for the
# receipt commit (cluster/f1b3/, cluster/logs/); the products themselves (gst, npz, prep JSONs) stay on pscratch,
# identified by f1b3-SHA256SUMS and f1-prep-SHA256SUMS. Writes nothing; never touches $OUT/f1b or $OUT/f1b2.
OUT=/pscratch/sd/j/josephrb/fd-f1-20261027
date -u +%FT%TZ; hostname
sacct -j 60436278 -P -o JobID,JobName,State,ExitCode,Start,End,Elapsed,MaxRSS,AllocTRES,NodeList
echo "--- fetched files"
cd $OUT && sha256sum logs/fd_f1b3_60436278.out f1b3/f1b3-SHA256SUMS f1b3/prep/f1-prep-SHA256SUMS f1b3/prep/config-f1.json \
  f1b3/queue.txt f1b3/gen5d/*.meta.json f1b3/runs/*/*.time f1b3/logs/*.log
