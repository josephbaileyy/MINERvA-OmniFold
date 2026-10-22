#!/usr/bin/env bash
# usage: pool.sh <model> <jobs.tsv>  -- runs that model's jobs through runjob.sh with xargs -P 3 (at most 3 concurrent).
# Field 5 holds two whitespace-separated input paths, so each job is 6 tokens. xargs exits only after every child exits.
set -u
NP=/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/ee772d13-75a3-4217-970c-8badb94dd2ba/scratchpad/xmodel/note-p2
m=$1; jobs=$2
awk -F'\t' -v m="$m" '$2==m {print $1, $2, $3, $4, $5}' "$jobs" | xargs -n 6 -P 3 bash $NP/tools/runjob.sh
echo "$m POOL-EXITED rc=$? $(date '+%H:%M:%S')"
