#!/bin/bash
# Delete the partial ENS1 A1 root that the dry-rerun SUBMIT connect (sha256 48805783..., FENCE STOP rc 9,
# 2026-11-08T07:13:52Z) left: four log files and an empty refs/ tree; no clone, no copy, no product (the director's
# ruling, item 3). Literal paths only. It refuses unless the root holds exactly what the stop left: the four files at
# their recorded sha256 and the five directories, nothing else; refuses if any ens1_* job is queued. It prints the
# before listing and every file's sha256, deletes, prints the after listing, and checks each path is gone. Prints to
# stdout (the receipt). Attempt 1's root /pscratch/sd/j/josephrb/ens1-20261107 is not touched (checked present).
# Run from the Mac: ssh -o ControlPath=none -o BatchMode=yes saul.nersc.gov bash -s < ens1_a1_delete_partial.sh
date -u +%FT%TZ; hostname
R=/pscratch/sd/j/josephrb/ens1-a1-20261108
[ -d "$R" ] || { echo "REFUSE: $R absent"; exit 2; }
q=$(squeue --me -h -o '%j') || { echo "REFUSE: squeue failed"; exit 2; }
[ -z "$(printf '%s\n' "$q" | grep -E '^ens1_')" ] || { echo "REFUSE: an ens1_* job is queued"; exit 2; }
echo "== before"
( cd "$R" && find . -printf '%y %s %p\n' | sort -k3 ) | tee /dev/shm/ens1_a1_del_before.$$
want="d 4096 .
d 4096 ./logs
f 2 ./logs/connect-a1-dry.done
f 21384 ./logs/ens1_a1_dry_submit.sh
f 322 ./logs/squeue-before.txt
f 967 ./logs/connect-a1-dry.log
d 4096 ./refs
d 4096 ./refs/runs
d 4096 ./refs/runs/control
d 4096 ./refs/runs/control/stability"
[ "$(sort -k3 /dev/shm/ens1_a1_del_before.$$)" = "$(printf '%s\n' "$want" | sort -k3)" ] || { echo "REFUSE: the root is not what the stop left"; rm -f /dev/shm/ens1_a1_del_before.$$; exit 2; }
rm -f /dev/shm/ens1_a1_del_before.$$
echo "== the files' sha256"
( cd "$R" && sha256sum logs/connect-a1-dry.done logs/connect-a1-dry.log logs/ens1_a1_dry_submit.sh logs/squeue-before.txt ) > /dev/shm/ens1_a1_del_sums.$$
cat /dev/shm/ens1_a1_del_sums.$$
cmp -s /dev/shm/ens1_a1_del_sums.$$ - <<SUMS || { echo "REFUSE: a file is not at its recorded sha256"; rm -f /dev/shm/ens1_a1_del_sums.$$; exit 2; }
2e6d31a5983a91251bfae5aefa1c0a19d8ba3cf601d0e8a706b4cfa9661a6b8a  logs/connect-a1-dry.done
c424f08a5e784ee41f7430c3f08593fd49c0e485629af627e457330bd5a80969  logs/connect-a1-dry.log
488057837438b79c745f53c3256107463fed04130f39c0f6d976bf2dd9faa20e  logs/ens1_a1_dry_submit.sh
9f91b0090d3b19e32049e6993525dc2f8dabf70abfa08fc65f33de8ede687fb3  logs/squeue-before.txt
SUMS
rm -f /dev/shm/ens1_a1_del_sums.$$
echo "== delete"
rm -f -- /pscratch/sd/j/josephrb/ens1-a1-20261108/logs/connect-a1-dry.done
rm -f -- /pscratch/sd/j/josephrb/ens1-a1-20261108/logs/connect-a1-dry.log
rm -f -- /pscratch/sd/j/josephrb/ens1-a1-20261108/logs/ens1_a1_dry_submit.sh
rm -f -- /pscratch/sd/j/josephrb/ens1-a1-20261108/logs/squeue-before.txt
rmdir -- /pscratch/sd/j/josephrb/ens1-a1-20261108/logs
rmdir -- /pscratch/sd/j/josephrb/ens1-a1-20261108/refs/runs/control/stability
rmdir -- /pscratch/sd/j/josephrb/ens1-a1-20261108/refs/runs/control
rmdir -- /pscratch/sd/j/josephrb/ens1-a1-20261108/refs/runs
rmdir -- /pscratch/sd/j/josephrb/ens1-a1-20261108/refs
rmdir -- /pscratch/sd/j/josephrb/ens1-a1-20261108
echo "== after"
ls -la /pscratch/sd/j/josephrb/ens1-a1-20261108 2>&1
echo "== gone?"
gone=0
for p in /pscratch/sd/j/josephrb/ens1-a1-20261108/logs/connect-a1-dry.done \
         /pscratch/sd/j/josephrb/ens1-a1-20261108/logs/connect-a1-dry.log \
         /pscratch/sd/j/josephrb/ens1-a1-20261108/logs/ens1_a1_dry_submit.sh \
         /pscratch/sd/j/josephrb/ens1-a1-20261108/logs/squeue-before.txt \
         /pscratch/sd/j/josephrb/ens1-a1-20261108/logs \
         /pscratch/sd/j/josephrb/ens1-a1-20261108/refs/runs/control/stability \
         /pscratch/sd/j/josephrb/ens1-a1-20261108/refs/runs/control \
         /pscratch/sd/j/josephrb/ens1-a1-20261108/refs/runs \
         /pscratch/sd/j/josephrb/ens1-a1-20261108/refs \
         /pscratch/sd/j/josephrb/ens1-a1-20261108; do
  if [ -e "$p" ]; then echo "STILL THERE: $p"; else echo "gone: $p"; gone=$((gone + 1)); fi
done
echo "attempt 1 root still present: $([ -d /pscratch/sd/j/josephrb/ens1-20261107/runs/F64 ] && echo yes || echo NO)"
date -u +%FT%TZ
[ "$gone" -eq 10 ] && { echo "DELETE: PASS"; exit 0; } || { echo "DELETE: INCOMPLETE"; exit 1; }
