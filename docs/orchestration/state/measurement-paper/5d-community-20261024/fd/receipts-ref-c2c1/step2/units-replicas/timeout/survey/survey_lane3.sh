set -u
L=/pscratch/sd/j/josephrb/ref-c2c1-20261106/logs-replicas
rd() { dd if="$1" iflag=noatime status=none; }
for J in 0 1 2 3; do
  f=$(ls "$L"/fd_c2c1r_*.out | while read x; do rd "$x" | grep -q "^\[c2c1r$J\] start" && echo "$x"; done | head -1)
  echo "== j$J batch out: $f"; rd "$f" | grep -vE '^\[c2c1r[0-9]\]   ' | head -30
  for l in 0 1 2 3; do
    echo "-- j$J lane $l: first lines / srun msgs / time file"
    rd "$L/j$J-lane$l.log" | grep -nE 'srun|step creation|Step created|affinity|cpus|CPU' | head -5
    rd "$L/j$J-lane$l.log" | grep -oE '^\{"unit": "[^"]+", "seconds": [0-9.]+' | head -2
    rd "$L/j$J-lane$l.log" | grep -oE '^\{"unit": "[^"]+", "seconds": [0-9.]+' | tail -2
    rd "$L/j$J-lane$l.time" | grep -E 'Elapsed|Exit status|Percent of CPU' | tr -s ' \t' ' ' | tr '\n' ';'; echo
  done
done
sacct -j 60890529,60890530,60890531,60890532 -n -P -o JobID,JobName,State,Start,End,Elapsed,AllocCPUS
