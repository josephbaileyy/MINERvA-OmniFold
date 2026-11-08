#!/bin/bash
# SCOPING.md section 6: the text searches, output masked by mask.py. Usage: bash search.sh <repo>
R=${1:?usage: search.sh <repo>}; M=$(cd "$(dirname "$0")" && pwd)/mask.py
g() { git -C "$R" grep -n -I -i -E "$1" -- "${@:2}" | python3 -I "$M" 240; }
echo "== S1 H2 near a comparison word";   g 'H2.{0,80}(tune|prior|data/|f/g|pull|departure from)|(tune|prior|data/|f/g|pull).{0,80}H2' '*.md' '*.tex' '*.txt' | grep -w H2
echo "== S2 extra axis by slice/quadrant"; g '(eavail|E_avail|q3|q_3|\bW\b).{0,60}(slice|per .?p_?T|in each .?p|by .?p_?T|pt.?bin|quadrant)|(slice|quadrant).{0,60}(eavail|E_avail|q_?3|hadronic)' '*.md' '*.tex' '*.py'
echo "== S3 factoriz family";             g 'factori[sz]|muon[- ]kinematic dependence|flat in p_?T|q3_vs_ascencio' '*.md' '*.tex' '*.txt'
echo "== S4 code reading P5";             git -C "$R" grep -l -I 'k1_p5' -- '*.py'
echo "== S5 committed figures";           git -C "$R" ls-files | grep -c -i -E '\.(png|pdf|svg)$'
