set -u
echo "host=$(hostname) date=$(date -u +%FT%TZ)"
H=/home/j/josephrb
for d in mnv-5d-s1-inputs-20261024 mnv-5d-s1-products-20261024 mnv-5d-cresp-20261026 mnv-5d-stage0-inputs-20261023 mnv-5d-fd-f4-20261025 mnv-uplan-texts-20261026 prd-release-preservation-20261008 mnv-re2-2d-rebuild-20261024 mnv-re2-2d-rebuild-partc-20261024 mnv-5d-f1-20261028; do echo "== $d"; hsi -q "ls -l $H/$d" 2>&1 | tail -n +2; done
echo "== tar members matching mp1|w2b|lat_|universes|playlist_term (htar -t reads the index only)"
for t in $(hsi -q "ls -1 $H/mnv-5d-s1-inputs-20261024 $H/mnv-5d-s1-products-20261024 $H/mnv-5d-cresp-20261026 $H/mnv-5d-stage0-inputs-20261023 $H/mnv-5d-fd-f4-20261025 $H/prd-release-preservation-20261008 $H/mnv-re2-2d-rebuild-20261024 $H/mnv-re2-2d-rebuild-partc-20261024 $H/mnv-5d-f1-20261028" 2>&1 | grep -E '\.tar$'); do
  n=$(htar -tf "$t" 2>/dev/null | grep -c -i -E 'mp1|w2b|lat_|universes|playlist_term'); echo "$t matches=$n"
  htar -tf "$t" 2>/dev/null | grep -i -E 'mp1|w2b|lat_|universes|playlist_term' | head -5
done
