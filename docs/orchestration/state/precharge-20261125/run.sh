#!/bin/bash
set -eo pipefail
source /pscratch/sd/j/josephrb/MINERvA-OmniFold/setup_salloc_env.sh >/dev/null
export OPENBLAS_NUM_THREADS=1
base=/pscratch/sd/j/josephrb/ibuchi-evloop-20261123/manifests
pl=$1
for sample in Data MC; do
    stem=${pl}_${sample}
    ./measure "$pl" "$sample" "$base/$stem.txt" "$stem.tmp" > "$stem.log" 2>&1
    gzip -c "$stem.tmp" > "$stem.csv.gz"
done
touch "$pl.done"
