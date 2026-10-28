# Poll step 2 (read-only); when it has ended: stdout, stderr, the deploy's porcelain and the output digests.
B=/pscratch/sd/j/josephrb/fd-flux-boot-20261028
D=$B/deploy/91312bc8
cat $B/logs/s2.stamps 2>&1
if grep -q "s2 end" $B/logs/s2.stamps 2>/dev/null; then
  cat $B/logs/boot.out; echo "--- stderr"; cat $B/logs/boot.err
  echo "porcelain_ignored_lines_after_run $(git -C $D status --porcelain --ignored | wc -l)"
  cd $B && sha256sum fd_flux_boot_readout.json logs/*.log logs/*.out logs/*.err logs/*.stamps logs/*.sh 2>&1 | tee $B/logs/outputs-sha256.txt; du -sh $B
fi
