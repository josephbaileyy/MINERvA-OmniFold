# run as: ssh saul.nersc.gov "<this loop>" (2026-10-29, login28); names only, from each HPSS archive's own inventory
for f in mnv-5d-s1-inputs-20261024/INVENTORY.sha256 mnv-5d-s1-products-20261024/ASSEMBLY-INVENTORY.sha256 mnv-5d-s1-products-20261024/PRODUCTS-INVENTORY.sha256 mnv-5d-stage0-inputs-20261023/INVENTORY.sha256; do
  echo "-- $f"; hsi -q "get - : /home/j/josephrb/$f" 2>/dev/null | grep -E 'cmodel|experiments|pv-ladder|h2def|ibu1|r10|proj1d' | head -8
done
