set -u
P=/pscratch/sd/j/josephrb
echo "host=$(hostname) date=$(date -u +%FT%TZ)"
summ() {  # dir: apparent size, file count, oldest and newest access time over regular files (stat only; no reads)
  local d=$1
  if [ ! -e "$d" ]; then echo "MISSING $d"; return; fi
  local sz n old new
  sz=$(du -s --apparent-size --block-size=1 "$d" 2>/dev/null | cut -f1)
  n=$(find "$d" -type f 2>/dev/null | wc -l)
  old=$(find "$d" -type f -printf '%A@ %AY-%Am-%Ad\n' 2>/dev/null | sort -n | head -1 | cut -d' ' -f2)
  new=$(find "$d" -type f -printf '%A@ %AY-%Am-%Ad\n' 2>/dev/null | sort -n | tail -1 | cut -d' ' -f2)
  echo "DIR $d bytes=$sz files=$n oldest_atime=$old newest_atime=$new"
}
echo "== fd-f1-20261027: children (f1b/ and f1b2/ not entered)"
ls -la --time-style=+%F $P/fd-f1-20261027/
for c in $P/fd-f1-20261027/*; do
  b=$(basename "$c")
  case "$b" in f1b|f1b2) echo "SKIPPED $c (forbidden: never read)";; *) summ "$c";; esac
done
echo "== the other directories"
for d in fd-flux-boot-20261027 fd-flux-boot-20261028 fd-f0-20261025 fd-f0b-20261026 fd-g-20261025 fd-g-diag-20261026 \
         fd-g-followup-20261026 fd-g-sens2-20261026 fd-g-figures-20261027 cresp-20261026 cmodel5d-20261024 h2def-20261024 \
         s1-20261024 pv-ladder-20261024 proj1d-20261027 r10-20261024 ibu1-20261022 measurement-paper/phase1/mp1/s1/unf \
         fd-ct-preserve-20261028 fd-deposit-check-20261028 fd-f0-testcheck-20261025 fd-g-testcheck-20261025 \
         fd-g-diag-testcheck-20261026 fd-cresp-testcheck-20261026; do summ $P/$d; done
echo "== RE-1 k1_p5_rerun.npz"
ls -la --time-style=+%F $P/methods-paper/re1-20261022/out/5d/k1_p5_rerun.npz 2>&1; stat -c '%x %s %n' $P/methods-paper/re1-20261022/out/5d/k1_p5_rerun.npz 2>&1
summ $P/methods-paper/re1-20261022/out
echo "== F0 per-experiment table"
ls -la --time-style=+%F $P/fd-f0-20261025/ 2>&1 | head -30
find $P/fd-f0-20261025 -maxdepth 3 -name '*.npz' -printf '%s %AY-%Am-%Ad %p\n' 2>/dev/null | head -20
echo "== cresp out"
ls -la --time-style=+%F $P/cresp-20261026/out/ 2>&1
