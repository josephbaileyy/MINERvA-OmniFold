set -u
P=/pscratch/sd/j/josephrb
echo "host=$(hostname) date=$(date -u +%FT%TZ)"
stat -c '%x  %s  %n' $P/MINERvA-OmniFold/nd-unfolding/runEventLoopOmniFold_5D_*_universes_full_bkgaware.root
echo "== CFS copies?"
ls -la --time-style=+%F /global/cfs/cdirs/m3246/josephrb/ 2>&1 | head -80
ls -la /global/cfs/cdirs/m3246/josephrb/*/runEventLoopOmniFold_5D_*bkgaware* /global/cfs/cdirs/m3246/josephrb/*/*/runEventLoopOmniFold_5D_*bkgaware* 2>&1 | head
