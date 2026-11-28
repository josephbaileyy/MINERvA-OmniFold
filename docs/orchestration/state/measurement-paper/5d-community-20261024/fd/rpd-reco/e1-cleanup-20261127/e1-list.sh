#!/bin/bash
# e1 cleanup, step 1 of 2 (read-only): the listing of the three unused e1 roots, for the director's handshake.
#   ssh saul.nersc.gov "ssh -o BatchMode=yes login02 'bash -s'" < e1-list.sh > listing.txt 2> list.err
# Writes nothing. For each literal root: refuses unless it is a real directory (not a symlink); then prints one line per
# entry, "<type> <bytes> <root>/<relative path>", sorted in the C locale, and a summary. The sha256 of this stdout is
# the listing sha the director approves; e1-remove.sh regenerates the same lines and refuses unless they hash to it.
stop() { echo "STOP: $*" >&2; exit 2; }
ROOTS="/pscratch/sd/j/josephrb/rpd-reco-p0e1-20261126 /pscratch/sd/j/josephrb/rpd-reco-flux4-20261126 /pscratch/sd/j/josephrb/rpd-reco-d2s0e1-20261127"
listing() {
  for R in $ROOTS; do
    [ -d "$R" ] && [ ! -L "$R" ] || { echo "ROOT-NOT-A-DIRECTORY $R"; continue; }
    find "$R" -xdev -mindepth 1 -printf "%y %s $R/%P\n"
  done | LC_ALL=C sort
}
out=$(listing) || stop "listing failed"
printf '%s\n' "$out"
echo "== summary"
echo "listing_sha256 $(printf '%s\n' "$out" | sha256sum | cut -d' ' -f1)"
for R in $ROOTS; do
  n=$(printf '%s\n' "$out" | awk -v r="$R/" 'index($3, r) == 1' | wc -l)
  b=$(printf '%s\n' "$out" | awk -v r="$R/" 'index($3, r) == 1 && $1 == "f" {s += $2} END {printf "%d", s}')
  l=$(printf '%s\n' "$out" | awk -v r="$R/" 'index($3, r) == 1 && $1 == "l"' | wc -l)
  echo "$R entries $n file_bytes $b symlinks $l"
done
