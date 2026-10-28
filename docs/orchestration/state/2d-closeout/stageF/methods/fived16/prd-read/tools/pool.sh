#!/usr/bin/env bash
# usage: pool.sh <model> -- that model's jobs, at most 3 concurrent. Field 5 holds 1 or 2 paths.
set -u
X=/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/796e7ecc-51d8-4fd5-a926-09de706955fd/scratchpad/xmodel/prd5d; m=$1
awk -F'\t' -v m="$m" '$2==m {print $1"\t"$2"\t"$3"\t"$4"\t"$5}' $X/jobs.tsv | while IFS=$'\t' read -r a b c d e; do printf '%s\0' "bash $X/runjob.sh $a $b $c $d $e"; done | xargs -0 -n 1 -P 3 bash -c
echo "$m POOL-EXITED rc=$? $(date '+%H:%M:%S')"
