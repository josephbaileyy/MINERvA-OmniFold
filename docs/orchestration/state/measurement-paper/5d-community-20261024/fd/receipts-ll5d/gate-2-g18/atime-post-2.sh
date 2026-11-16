# Stat-only atime-post for LL5D gate 2 (both truths), the same find as connect-gate-2.sh's atime-pre.
P=/pscratch/sd/j/josephrb; ND=$P/MINERvA-OmniFold/nd-unfolding
echo "host=$(hostname) utc=$(date -u +%FT%TZ)"
find "$ND/of_inputs_5d.npz" "$P/s5c-20260924/runs/p2/bkg_dump.npz" "$ND/bank_sweep_5d_bkgaware" "$P/s5p-20260926/bank_detector" \
  "$P/fd-1b-20261030/pins.json" "$P/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt" \
  "$P/fd-1b-staged-20261102/stage1/in/flux_universes.npz" "$P/fd-f1-20261027/f1b3/prep" "$P/fd-1b-inv-20261101/i0/in" \
  -type f -printf "%A@\t%p\n" | sort -k2
echo "find_rc=${PIPESTATUS[0]} end_utc=$(date -u +%FT%TZ)"
