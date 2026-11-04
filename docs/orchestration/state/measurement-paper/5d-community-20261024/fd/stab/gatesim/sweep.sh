#!/bin/bash
# The timing-noise sweep of FD-STAB-DECLARATION.md §7: 40 seeds per (noise, alpha, B2 factor), through gatesim2.py and
# the real gate. Run from the repository root; writes sweep.txt here (about 45 min), then summarize.py prints the table.
set -o pipefail
H="$(cd "$(dirname "$0")" && pwd)"; W=$(mktemp -d)
cd nd-unfolding || exit 2
for nz in 0.02 0.1; do for a in 0.8 0.9 1.0 1.1; do for f in 1.0 1.3 1.5 1.6 1.7 1.75 1.8 1.85 2.0; do
    for s in $(seq 0 39); do
        echo "$nz $a $f $s $(PYTHONDONTWRITEBYTECODE=1 python3 -B "$H/gatesim2.py" "$a" "$f" "$W" "$nz" "$s" | tail -1)"
    done
done; done; done > "$H/sweep.txt"
python3 -I "$H/summarize.py" "$H/sweep.txt"
