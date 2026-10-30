# 5B step 4 (section 2.3, after the job): sacct, lane lines, products. Login node, read-only.
B=/pscratch/sd/j/josephrb/fd-ct-5b-20261030
{ date -u +%FT%TZ; hostname
  sacct -j 60537730 -X -o JobID,JobName%20,State,ExitCode,Elapsed,ElapsedRaw,NNodes,AllocTRES%60 -P
  echo "--- steps"; sacct -j 60537730 -o JobID,JobName%12,State,ExitCode,ElapsedRaw,MaxRSS -P
  for f in $B/lanes-inputs/line*-60537730.log; do echo "--- $(basename $f)"; grep -E "^\[f1-lane\]|^\[s5c\]|refusing|Traceback" $f; done
  echo "--- products"; ls -l $B/merged $B/dumps $B/truth $B/inputs $B/unf/ALL
} > $B/logs/after-a.out 2>&1
cat $B/logs/after-a.out
