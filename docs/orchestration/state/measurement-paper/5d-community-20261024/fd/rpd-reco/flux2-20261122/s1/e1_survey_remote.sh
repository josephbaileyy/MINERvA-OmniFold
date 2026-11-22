#!/bin/bash
# e1_survey_remote.sh: RPD-RECO e1, survey 1 (limitation-resolver, 2026-11-22). Runs on a Perlmutter login node and
# writes nothing. It uses stat, sacct and iris. It opens no file's contents, so no file's atime moves.
# - the epoch and host, computed on the node;
# - our unended jobs over 14 days, from sacct (never squeue), with every job name, so any fenced family shows;
# - the iris row for m3246 (the balance is $5 - $4);
# - a stat (size, atime, mtime, inode) of e1's inputs: RPD job A's 24 dumps, flux connect 1's 12 factor products with
#   their extract and custody records, and the six MAT flux files the extract staged (numerator and generation, 1D/1M/1N);
# No directory is listed: flux connect 1's custody policy names the dumps directory as a protected root, so no entry
# read touches it (director, 2026-11-22). A missing file shows in its stat line; an extra file is refused by P0's pins.
echo "== host $(hostname) utc $(date -u +%FT%TZ) epoch $(date -u +%s)"
echo "== sacct (14 days, unended)"
s=$(sacct -X -n -P -S "$(date -u -d '14 days ago' +%F)" -o JobID,JobName,State,Elapsed) || echo "SACCT FAILED rc=$?"
printf '%s\n' "$s" | awk -F'|' '$3 !~ /^(COMPLETED|FAILED|CANCELLED|TIMEOUT|OUT_OF_MEMORY|NODE_FAIL|PREEMPTED|BOOT_FAIL|DEADLINE)/' | sed '/^$/d; s/^/unended: /'
echo "sacct rows (14 days): $(printf '%s\n' "$s" | sed '/^$/d' | wc -l)"
echo "== iris"
iris 2>&1 | grep -E '^m3246 ' | head -1
D=/pscratch/sd/j/josephrb/fd-rpd-20261103/dumps
R=/pscratch/sd/j/josephrb/rpd-reco-flux-20261111/run
F=/pscratch/sd/j/josephrb/minerva/minerva_large_files/MATFluxAndReweightFiles/flux
echo "== stat: name|bytes|atime|mtime|inode"
for pl in 1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P; do
  for f in "$D/lat_${pl}.npz" "$D/lat_${pl}_bkg.npz" "$R/flux-factors-${pl}.npz"; do
    stat -c '%n|%s|%X|%Y|%i' -- "$f" 2>&1
  done
done
for f in "$R/flux-extract.json" "$R/flux-custody.json"; do stat -c '%n|%s|%X|%Y|%i' -- "$f" 2>&1; done
for pl in 1D 1M 1N; do
  for fam in gen2thin g4numiv6; do
    stat -c '%n|%s|%X|%Y|%i' -- "$F/flux-${fam}-pdg14-minervame${pl}_rearrangedUniverses.root" 2>&1
  done
done
echo "== end utc $(date -u +%FT%TZ)"
