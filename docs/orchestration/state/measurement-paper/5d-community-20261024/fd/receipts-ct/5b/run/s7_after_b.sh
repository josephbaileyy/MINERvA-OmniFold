# 5B step 7 (section 2.5, after the job): sacct, lane lines, products. Login node, read-only.
B=/pscratch/sd/j/josephrb/fd-ct-5b-20261030
{ date -u +%FT%TZ; hostname
  sacct -j 60549044 -X -o JobID,JobName%20,State,ExitCode,Elapsed,ElapsedRaw,NNodes,AllocTRES%60 -P
  echo "--- steps"; sacct -j 60549044 -o JobID,JobName%12,State,ExitCode,ElapsedRaw,MaxRSS -P
  for f in $B/lanes-periods/line*-60549044.log; do echo "--- $(basename $f)"; grep -E "^\[f1-lane\]|^\[s5c\]|refusing|Traceback" $f; done
  echo "--- products"; for P in PA PB PC; do echo "$P $(ls $B/unf/$P | wc -l)"; ls $B/unf/$P; done
} > $B/logs/after-b.out 2>&1
cat $B/logs/after-b.out
