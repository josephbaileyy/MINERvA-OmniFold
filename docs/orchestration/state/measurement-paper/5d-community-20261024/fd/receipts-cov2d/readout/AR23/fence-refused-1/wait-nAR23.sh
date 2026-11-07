#!/bin/bash
# Wait (read-only squeue, every 300 s, up to 7 h) until josephrb's queue is empty, then run launch-s5.sh nAR23, which
# fences again itself. The ssh rc is read unpiped; a failed ssh is logged and retried.
H=/Users/josephbailey/cov2d-work
for i in $(seq 1 84); do
  echo 'squeue -u josephrb -h -o "%i %j %T"; echo "sq end"' | ssh -o ControlPath=none saul.nersc.gov "ssh -o BatchMode=yes -o LogLevel=QUIET login02 bash -s" > "$H/a4/wait-sq.txt" 2>&1; rc=$?
  echo "$(date -u +%FT%TZ) ssh rc=$rc $(grep -v '^sq end$' "$H/a4/wait-sq.txt" | tr '\n' ';')"
  if [ "$rc" = 0 ] && grep -q '^sq end$' "$H/a4/wait-sq.txt" && [ "$(grep -vc '^sq end$' "$H/a4/wait-sq.txt")" = 0 ]; then
    echo "queue empty: launching"; bash "$H/launch-s5.sh" nAR23 > "$H/a4/launch-nAR23.out" 2>&1; echo "launcher rc=$?" >> "$H/a4/launch-nAR23.out"; exit 0
  fi
  sleep 300
done
echo "gave up after 7 h"; exit 4
