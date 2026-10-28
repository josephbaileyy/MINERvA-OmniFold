set -u
P=/pscratch/sd/j/josephrb
echo "host=$(hostname) date=$(date -u +%FT%TZ)"
for d in $P/measurement-paper/phase1/mp1/s1/evloop $P/measurement-paper/phase1/mp1/s1/lateral $P/measurement-paper/phase1/mp1/s1/unf $P/measurement-paper/phase1/mp1/s1/merged $P/w2-recoil-20261006/w2b; do
  echo "== $d"; ls -la --time-style=+%F "$d" 2>&1 | head -60
done
echo "== evloop subdirs"
for v in $P/measurement-paper/phase1/mp1/s1/evloop/*/; do echo "-- $v"; ls -la --time-style=+%F "$v" 2>&1 | head -20; done
echo "== universes_full_bkgaware"
ls -la --time-style=+%F $P/MINERvA-OmniFold/nd-unfolding/runEventLoopOmniFold_5D_*_universes_full_bkgaware.root 2>&1
echo "== playlist_term"
ls -la --time-style=+%F $P/*/playlist_term.npz $P/*/*/playlist_term.npz 2>&1 | head
echo "== lfs atime sample (purge uses atime)"
stat -c '%n atime=%x mtime=%y' $P/measurement-paper/phase1/mp1/s1/lateral/* 2>&1 | head -20
