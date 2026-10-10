#!/bin/bash
# Compare every tracked file of the standalone note at $2 with canonical $1:docs/analysis-note/.
# Usage: STANDALONE=<standalone checkout> source_equivalence.sh CANON_REV STANDALONE_REV
# (run from inside the canonical checkout; read-only)
set -u
C=$(git rev-parse --show-toplevel)
N=${STANDALONE:?set STANDALONE to the standalone note checkout}
git -C "$C" ls-tree -r "$1" docs/analysis-note/ | awk -F'\t' '{split($1,a," "); sub("^docs/analysis-note/","",$2); print $2"\t"a[3]}' | sort > /tmp/.c.$$
git -C "$N" ls-tree -r "$2" | awk -F'\t' '{split($1,a," "); print $2"\t"a[3]}' | sort > /tmp/.n.$$
echo "canonical $1 docs/analysis-note files: $(wc -l < /tmp/.c.$$); standalone $2 files: $(wc -l < /tmp/.n.$$)"
join -t $'\t' -a1 -a2 -e MISSING -o 0,1.2,2.2 /tmp/.c.$$ /tmp/.n.$$ | awk -F'\t' '$2!=$3{print "DIFF\t"$0}' > /tmp/.d.$$
echo "identical paths: $(join -t $'\t' /tmp/.c.$$ /tmp/.n.$$ | awk -F'\t' '$2==$3' | wc -l)"
echo "differing or one-sided paths: $(wc -l < /tmp/.d.$$)"; cat /tmp/.d.$$
rm -f /tmp/.c.$$ /tmp/.n.$$ /tmp/.d.$$
