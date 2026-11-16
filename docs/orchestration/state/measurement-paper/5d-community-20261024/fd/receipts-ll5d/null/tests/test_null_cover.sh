#!/bin/bash
# Stand-in test of connect-null.sh's COVER block (the declared-input coverage check), extracted verbatim.
# A temp tree holds the staged S1 assembly, the constraint, the deploy's definition and cmodel json, and a names file
# with 454 product names (227 per truth) plus a toy name. Cases: pass (protected two in atime-pre, nothing else);
# the constraint missing from atime-pre (exit 1); a product listed in atime-pre (exit 1); the cmodel json absent (exit 1).
#     bash test_null_cover.sh connect-null.sh <expected_moved_g18.txt> <expected_moved_ar23.txt>
set -u
CONN=$1; E1=$2; E2=$3
PY=${PY:-python3}
blk=$(awk '/<<.COVER. \|\| stop/ {on = 1; next} /^COVER$/ {on = 0} on' "$CONN")
T=$(mktemp -d "${TMPDIR:-/tmp}/tnc.XXXXXX"); fail=0; n=0
setup() {
  n=$((n + 1)); R=$T/c$n; mkdir -p "$R/staged/s1" "$R/dd/nd-unfolding/pv-ladder/readouts" "$R/u"
  : > "$R/staged/s1/s1_assembly.npz"; : > "$R/constraint.txt"
  : > "$R/dd/nd-unfolding/pv-ladder/readouts/h2_definition.json"; : > "$R/dd/nd-unfolding/pv-ladder/readouts/cmodel_5d.json"
  { sed 's|.*/||' "$E1" "$E2"; echo ll5d_g18_toy_all_4751001.npz; } > "$R/names.txt"
  printf '1.0\t%s\n1.0\t%s\n1.0\t%s/other.npz\n' "$R/staged/s1/s1_assembly.npz" "$R/constraint.txt" "$R/staged" > "$R/pre.tsv"
}
run() { printf '%s\n' "$blk" > "$R/c.py"; "$PY" "$R/c.py" "$R/pre.tsv" "$R/staged" "$R/constraint.txt" "$R/dd" "$R/u" "$R/names.txt" > "$R/out" 2>&1; echo $? > "$R/rc"; }
chk() { r=$(cat "$R/rc"); if [ "$r" = "$2" ]; then echo "PASS $1 rc=$r: $(head -1 "$R/out")"; else echo "FAIL $1 rc=$r (want $2)"; cat "$R/out"; fail=1; fi; }
setup; run; chk pass 0
grep -q 'products 454 (in atime-pre: 0)' "$R/out" && echo "PASS pass-counts (454 products, 0 in atime-pre)" || { echo "FAIL pass-counts"; fail=1; }
setup; grep -v constraint "$R/pre.tsv" > "$R/p2" && mv "$R/p2" "$R/pre.tsv"; run; chk constraint-not-in-pre 1
setup; printf '1.0\t%s/%s\n' "$R/u" "$(head -1 "$R/names.txt")" >> "$R/pre.tsv"; run; chk product-in-pre 1
setup; rm -f "$R/dd/nd-unfolding/pv-ladder/readouts/cmodel_5d.json"; run; chk cmodel-absent 1
find "$T" -type f -exec rm -f {} +; find "$T" -depth -type d -exec rmdir {} \;
[ -e "$T" ] && echo "left: $T"
[ "$fail" = 0 ] && echo "NULL-COVER TEST PASS" || echo "NULL-COVER TEST FAILED"
exit $fail
