#!/bin/bash
# RE-2 launcher test: run re2_j0.sbatch's lane() with a stub srun that READS ALL STDIN, as real srun forwards it
# (srun(1), IO Redirection). Usage: bash run/launch/test_lane_stdin.sh (bash >= 4). PASS when calls == rows.
set -eo pipefail
W=$(mktemp -d); trap 'rm -rf "$W"' EXIT
cd "$(dirname "$0")/.."; cp j0_runs.tsv "$W/"; RUNS=$W/j0_runs.tsv; O=$W/o; C=/deploy; mkdir -p "$O/out" "$O/logs"
export CV=/x/cv MC=/x/mc UNI=/x/uni FLUXU=/x/fu LATBAX0=/x/lat PUALL=/x/pa PUPA=/x/pp PUFALL=/x/pfa PUFPA=/x/pfp
srun() { cat > /dev/null; local a; for a in "$@"; do case "$a" in --out) echo "call" >> "$W/calls";; esac; done; }
eval "$(sed -n '/^lane() {/,/^}/p' launch/re2_j0.sbatch)"
set -u
for JOB in J0a J0b; do for l in a1 a2 b1 b2 b3 b4; do lane $l || true; done; done
n=$(wc -l < "$W/calls"); rows=$(($(wc -l < j0_runs.tsv) - 1)); echo "calls=$n rows=$rows"; [ "$n" -eq "$rows" ]
