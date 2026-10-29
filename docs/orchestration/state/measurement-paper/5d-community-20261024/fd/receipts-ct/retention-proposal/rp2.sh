set -u
P=/pscratch/sd/j/josephrb
echo "host=$(hostname) date=$(date -u +%FT%TZ)"
for d in fd-flux-boot-20261027 fd-flux-boot-20261028 fd-f0-20261025 fd-f0b-20261026 fd-g-20261025 fd-g-diag-20261026 \
         fd-g-followup-20261026 fd-g-sens2-20261026 fd-g-figures-20261027 cresp-20261026 cmodel5d-20261024 h2def-20261024 \
         s1-20261024 pv-ladder-20261024 proj1d-20261027 r10-20261024 ibu1-20261022 fd-deposit-check-20261028; do
  echo "== $d"
  for c in $P/$d/*; do
    [ -e "$c" ] || continue
    printf '  %-14s %12s  %s\n' "$(du -s --apparent-size --block-size=1 "$c" 2>/dev/null | cut -f1)" "$(find "$c" -type f 2>/dev/null | wc -l)" "$(basename "$c")"
  done
  for dd in $P/$d/deploy/* $P/$d/clone $P/$d/scratch-clone; do [ -d "$dd/.git" ] && echo "  git clone: $dd HEAD=$(git -C "$dd" rev-parse HEAD 2>/dev/null)"; done
done
echo "== fd-f1-20261027/deploy clones"
for dd in $P/fd-f1-20261027/deploy/*; do [ -d "$dd/.git" ] && echo "  $dd HEAD=$(git -C "$dd" rev-parse HEAD 2>/dev/null)"; done
echo "== HPSS inventories (names only)"
for f in mnv-5d-cresp-20261026/INVENTORY.sha256 mnv-5d-fd-f4-20261025/INVENTORY.sha256; do echo "-- $f"; hsi -q "get - : /home/j/josephrb/$f" 2>/dev/null | awk '{print $2}' | sed 's#/pscratch/sd/j/josephrb/##' | awk -F/ '{print $1"/"$2"/"$3}' | sort | uniq -c | head; done
hsi -q "get - : /home/j/josephrb/mnv-5d-cresp-20261026/INVENTORY.sha256" 2>/dev/null
