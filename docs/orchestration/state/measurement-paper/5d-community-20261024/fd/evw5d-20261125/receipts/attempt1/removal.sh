#!/bin/bash
# EVW5D: remove attempt 1's namespace (DECISION-20261125c; the director's GO for attempt 2, its removal paragraph).
# Run once, in its own login session:  ssh ... saul.nersc.gov 'bash -s' < removal.sh > removal.txt 2>&1
# Removes exactly T. Refuses if T is a link, not a real directory, not its own canonical path, or if any evw5d job
# is in the queue. Records ls -la and du -s of T before and T's absence after, and attempt 2's namespace K
# (stat only, never written) before and after.
set -u
T=/pscratch/sd/j/josephrb/evw5d-20261125
K=/pscratch/sd/j/josephrb/evw5d-20261125-r2
echo "removal host $(hostname) $(date -u +%FT%TZ) user $(id -un)"
echo "target $T"
echo "keep   $K"
[ "$T" != "$K" ] || { echo "REFUSE: target equals keep"; exit 3; }
if [ -L "$T" ]; then echo "REFUSE: $T is a symbolic link"; exit 3; fi
if [ ! -d "$T" ]; then echo "REFUSE: $T is not a directory (or absent)"; exit 3; fi
c=$(readlink -f -- "$T")
[ "$c" = "$T" ] || { echo "REFUSE: canonical path is $c, not $T"; exit 3; }
q=$(squeue -h -u "$(id -un)" -n evw5d -o '%i|%T' 2>&1); qrc=$?
echo "squeue evw5d rc=$qrc: [$q]"
[ $qrc = 0 ] && [ -z "$q" ] || { echo "REFUSE: an evw5d job is queued, or squeue failed"; exit 3; }
echo "## keep before"
stat -c '%n|%F|%i|%Y' -- "$K" "$K/evw5d/weights.npz" "$K/evw5d/SHA256SUMS"
echo "## ls -la before"
ls -la -- "$T"
echo "## du -s before"
du -s -- "$T"
echo "## files before: $(find "$T" -mindepth 1 | wc -l) entries"
rm -rf --one-file-system -- "$T"; rrc=$?
echo "rm rc=$rrc"
echo "## after"
if [ -e "$T" ] || [ -L "$T" ]; then echo "PRESENT: $T"; ls -la -- "$T"; exit 4; fi
echo "ABSENT: $T"
ls -la /pscratch/sd/j/josephrb/ | grep -F evw5d
echo "## keep after"
stat -c '%n|%F|%i|%Y' -- "$K" "$K/evw5d/weights.npz" "$K/evw5d/SHA256SUMS"
echo "removal rc=$rrc $(date -u +%FT%TZ)"
exit $rrc
