set -u
echo "host=$(hostname) date=$(date -u +%FT%TZ)"
H=/home/j/josephrb
echo "== htar -t total member lines and rc (0 lines = could not look)"
for t in $H/prd-release-preservation-20261008/s5p-archive-20261006.tar $H/mnv-5d-s1-inputs-20261024/stage0-inputs.tar; do
  out=$(htar -tf "$t" 2>&1); rc=$?; echo "$t rc=$rc lines=$(printf '%s\n' "$out" | wc -l)"; printf '%s\n' "$out" | tail -2
done
echo "== inventories read to stdout (hsi get -), members matching mp1|w2b|lat_|universes|playlist_term, and total lines"
for f in mnv-5d-s1-inputs-20261024/INVENTORY.sha256 mnv-5d-s1-products-20261024/PRODUCTS-INVENTORY.sha256 mnv-5d-s1-products-20261024/ASSEMBLY-INVENTORY.sha256 mnv-5d-cresp-20261026/INVENTORY.sha256 mnv-5d-stage0-inputs-20261023/INVENTORY.sha256 mnv-5d-fd-f4-20261025/INVENTORY.sha256 mnv-re2-2d-rebuild-20261024/members.sha256 mnv-re2-2d-rebuild-partc-20261024/members.sha256 mnv-5d-f1-20261028/INVENTORY.sha256; do
  inv=$(hsi -q "get - : $H/$f" 2>/dev/null); echo "-- $f total=$(printf '%s\n' "$inv" | grep -c .) match=$(printf '%s\n' "$inv" | grep -c -i -E 'mp1|w2b|lat_|universes|playlist_term')"
  printf '%s\n' "$inv" | grep -i -E 'mp1|w2b|lat_|universes|playlist_term' | head -4
done
