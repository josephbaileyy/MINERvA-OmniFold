#!/bin/bash
# usage: mp3_run.sh NAME 'remote cmd'
R=/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/d1f3ed7d-dde2-4ad5-a668-62662888e93c/scratchpad/receipts/mp3
out="$R/$1.txt"
{ echo "# command: ssh -o ControlPath=none -o BatchMode=yes saul.nersc.gov '$2'"; echo "# utc: $(date -u '+%F %T UTC')"; echo "# ---"; } > "$out"
ssh -o ControlPath=none -o BatchMode=yes saul.nersc.gov "$2" >> "$out" 2>&1
rc=$?
echo "# --- rc=$rc" >> "$out"
cat "$out"
