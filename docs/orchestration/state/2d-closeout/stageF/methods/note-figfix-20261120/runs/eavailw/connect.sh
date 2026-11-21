#!/bin/bash
# read-only fetch of the 4 repaired (E_avail, W) generator files (director's GO, 2026-11-21, window to 1795229332)
set -o pipefail
S=/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/eaw
END=$(date -j -u -f '%Y-%m-%dT%H:%M:%SZ' '2026-11-21T02:48:52Z' +%s)
ACK=$(date -j -u -f '%Y-%m-%dT%H:%M:%SZ' '2026-11-21T01:19:09Z' +%s)
NOW=$(date -u +%s)
echo "now $NOW end $END ack $ACK (ack age $((NOW-ACK)) s)"
[ "$NOW" -lt "$END" ] || { echo "REFUSE: outside the window"; exit 2; }
[ $((NOW-ACK)) -lt 900 ] || { echo "REFUSE: tier3-design ack older than 15 min"; exit 2; }
if pgrep -fl 'ssh .*nersc|ssh .*saul|sbatch|rsync .*nersc|scp .*nersc'; then echo "REFUSE: own fence (a cluster process is running)"; exit 2; fi
ssh -o ControlPath=none -o BatchMode=yes -o ConnectTimeout=30 saul.nersc.gov 'python3 -' < $S/remote_read.py > $S/fetch.jsonl 2> $S/fetch.stderr
rc=$?
echo "ssh rc=$rc at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
exit $rc
