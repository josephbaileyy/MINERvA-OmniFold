set -u
C=/global/cfs/cdirs/m3246/josephrb
echo "host=$(hostname) date=$(date -u +%FT%TZ)"
echo "== prd-release-preservation-20261008 top"; ls -la --time-style=+%F $C/prd-release-preservation-20261008/ 2>&1
echo "== every CFS file whose path matches w2b|mp1|lat_|universes_full_bkgaware (find over our CFS area, names only)"
find $C -xdev \( -path '*w2b*' -o -path '*mp1*' -o -name 'lat_*' -o -name '*universes_full_bkgaware*' \) -type f -printf '%s %p\n' 2>/dev/null | sort -k2 > /tmp/ret7.list; echo "find rc=$? matches=$(wc -l < /tmp/ret7.list)"
awk '{print $2}' /tmp/ret7.list | sed -E 's#/[^/]+$##' | sort | uniq -c
grep -E 'lat_|_b-_j-\.npz' /tmp/ret7.list
echo "== find errors (permission) count"; find $C -xdev -type d ! -readable 2>/dev/null | head -5
rm -f /tmp/ret7.list
