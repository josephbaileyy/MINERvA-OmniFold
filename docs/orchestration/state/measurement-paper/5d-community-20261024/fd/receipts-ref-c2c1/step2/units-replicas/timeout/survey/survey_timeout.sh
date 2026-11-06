set -u
O=/pscratch/sd/j/josephrb/ref-c2c1-20261106; U=$O/units; L=$O/logs-replicas
rd() { dd if="$1" iflag=noatime status=none; }
echo "now $(date -u +%FT%TZ) host $(hostname)"
rd "$L/lanes.tsv" > /dev/shm/lanes.$$
for J in 0 1 2 3; do
  tot=0; pass=0; started=0
  for u in $(grep -v '^#' /dev/shm/lanes.$$ | awk -F'\t' -v j=$J '$1==j{print $3}'); do
    tot=$((tot+1)); name=$(echo "$u" | sed 's/:\(.*\)/_b\1/')
    if [ -e "$U/$name.done" ]; then rd "$U/$name.done" | grep -q '"verdict": "PASS"' && pass=$((pass+1)); fi
    ls "$U/$name"* >/dev/null 2>&1 && started=$((started+1))
  done
  echo "j$J: units $tot, PASS markers $pass, with any output $started"
  for l in 0 1 2 3; do
    t=$(grep -v '^#' /dev/shm/lanes.$$ | awk -F'\t' -v j=$J -v l=$l '$1==j&&$2==l' | wc -l)
    p=0; for u in $(grep -v '^#' /dev/shm/lanes.$$ | awk -F'\t' -v j=$J -v l=$l '$1==j&&$2==l{print $3}'); do
      name=$(echo "$u" | sed 's/:\(.*\)/_b\1/'); [ -e "$U/$name.done" ] && rd "$U/$name.done" | grep -q '"verdict": "PASS"' && p=$((p+1)); done
    echo "  lane $l: $p of $t PASS; log $(stat -c '%s bytes, mtime %y' "$L/j$J-lane$l.log" 2>&1); time file: $([ -e "$L/j$J-lane$l.time" ] && echo present || echo absent)"
    rd "$L/j$J-lane$l.log" | grep -vE '^\{"unit"' | tail -3 | sed 's/^/    | /'
  done
done
echo "unit seconds (from .done-adjacent log lines), by kind:"
for J in 0 1 2 3; do for l in 0 1 2 3; do rd "$L/j$J-lane$l.log"; done; done | grep -oE '^\{"unit": "[a-z0-9_]+", "seconds": [0-9.]+' | sed -E 's/.*"unit": "([a-z0-9]+_[a-z]+)_?[^"]*", "seconds": ([0-9.]+)/\1 \2/' | awk '{n[$1]++; s[$1]+=$2; if($2>mx[$1])mx[$1]=$2; if(!($1 in mn)||$2<mn[$1])mn[$1]=$2} END{for(k in n) printf "  %s n=%d mean=%.0f min=%.0f max=%.0f\n",k,n[k],s[k]/n[k],mn[k],mx[k]}'
echo "watch: now vs each job's before (stat only)"
xargs -d '\n' stat -c '%X %n' < <(rd "$L/cov2d-watch-paths.txt") > /dev/shm/watchnow.$$ 2>&1
for J in 0 1 2 3; do echo "  j$J before lines $(wc -l < "$L/j$J-watch-before.txt"); now vs before: $(cmp -s <(rd "$L/j$J-watch-before.txt") /dev/shm/watchnow.$$ && echo identical || echo DIFFERENT)"; done
echo "squeue josephrb:"; squeue -u josephrb -h -o '%i|%j|%T|%M|%l'
rm -f /dev/shm/lanes.$$ /dev/shm/watchnow.$$
