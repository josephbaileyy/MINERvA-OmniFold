#!/bin/bash
# Stand-in test of connect-readout.sh's two new blocks, extracted verbatim:
#   CHECK (from the job script): only rc 0 + readout-<T>.json + atime.moved [] + "evaluations" prints CLEAN; rc 8 with
#     moves, rc 5 with only an .invalid.json, rc 0 with a moved path, a record without evaluations, and no record each
#     print NOT-CLEAN.
#   COVER (from the connect): the protected two in atime-pre and nothing else passes, with 454+1200 products and the
#     null, clipcheck and gate records counted as unprotected; a null record listed in atime-pre fails, and so does a
#     missing gate record.
#     bash test_readout_blocks.sh connect-readout.sh ../null/u-names.from-evidence.txt
set -u
CONN=$1; NAMES=$2; PY=${PY:-python3}
job=$(awk '/^cat > "\$W\/sbatch-ll5d-readout.sh" <<.JOB.$/{on=1;next} /^JOB$/{on=0} on' "$CONN")
check=$(printf '%s\n' "$job" | awk '/<<.CHECK.$/ {on = 1; next} /^CHECK$/ {on = 0} on')
cover=$(awk '/<<.COVER. \|\| stop/ {on = 1; next} /^COVER$/ {on = 0} on' "$CONN")
T0=$(mktemp -d "${TMPDIR:-/tmp}/trb.XXXXXX"); fail=0; n=0
ok() { echo "PASS $1"; }; bad() { echo "FAIL $1"; fail=1; }
mk() { "$PY" -c 'import json, sys
d = {"verdicts": {"g18/all": "UNDER-COVERS"}, "atime": {"moved": sys.argv[2].split(",") if sys.argv[2] else []}}
if sys.argv[3] == "1": d["evaluations"] = {}
json.dump(d, open(sys.argv[1], "w"))' "$1" "$2" "$3"; }
runc() { printf '%s\n' "$check" | "$PY" - "$D/readout-g18.json" "$D/readout-g18.invalid.json" "$2" g18 > "$D/out" 2>&1
  if grep -q "^READOUT-EXIT g18 $3" "$D/out" && { [ "$3" = NOT-CLEAN ] || ! grep -q NOT-CLEAN "$D/out"; }; then ok "check-$1"; else bad "check-$1 (want $3)"; cat "$D/out"; fi; }
fresh() { n=$((n + 1)); D=$T0/c$n; mkdir "$D"; }
fresh; mk "$D/readout-g18.json" "" 1; runc clean 0 CLEAN
fresh; mk "$D/readout-g18.json" "/p/x.npz" 1; runc rc8-moved 8 NOT-CLEAN
fresh; mk "$D/readout-g18.json" "/p/x.npz" 1; runc rc0-but-moved 0 NOT-CLEAN
fresh; mk "$D/readout-g18.invalid.json" "" 1; runc only-invalid 5 NOT-CLEAN
fresh; mk "$D/readout-g18.json" "" 0; runc no-evaluations 0 NOT-CLEAN
fresh; runc no-record 5 NOT-CLEAN
setupc() {
  fresh; R=$D; mkdir -p "$R/staged/s1" "$R/dd/nd-unfolding/pv-ladder/readouts" "$R/u" "$R/nw" "$R/pw" "$R/g18w" "$R/ar23w"
  : > "$R/staged/s1/s1_assembly.npz"; : > "$R/constraint.txt"
  : > "$R/dd/nd-unfolding/pv-ladder/readouts/h2_definition.json"; : > "$R/dd/nd-unfolding/pv-ladder/readouts/cmodel_5d.json"
  : > "$R/nw/null-g18.json"; : > "$R/nw/null-ar23.json"; : > "$R/pw/clipcheck.json"; : > "$R/g18w/gate-g18.json"; : > "$R/ar23w/gate-ar23.json"
  cp "$NAMES" "$R/names.txt"
  printf '1.0\t%s\n1.0\t%s\n' "$R/staged/s1/s1_assembly.npz" "$R/constraint.txt" > "$R/pre.tsv"
}
runv() { printf '%s\n' "$cover" > "$R/c.py"; "$PY" "$R/c.py" "$R/pre.tsv" "$R/staged" "$R/constraint.txt" "$R/dd" "$R/u" "$R/names.txt" "$R/nw" "$R/pw" "$R/g18w" "$R/ar23w" > "$R/out" 2>&1; r=$?
  [ "$r" = "$2" ] && ok "cover-$1 rc=$r: $(head -1 "$R/out")" || { bad "cover-$1 rc=$r (want $2)"; cat "$R/out"; }; }
setupc; runv pass 0
grep -q 'products 1654 (in atime-pre: 0)' "$R/out" && ok "cover-counts (454 + 1200 products; deploy 7)" || { bad "cover-counts"; cat "$R/out"; }
setupc; printf '1.0\t%s\n' "$R/nw/null-g18.json" >> "$R/pre.tsv"; runv null-record-in-pre 1
setupc; rm -f "$R/ar23w/gate-ar23.json"; runv gate-missing 1
find "$T0" -type f -exec rm -f {} +; find "$T0" -depth -type d -exec rmdir {} \;
[ -e "$T0" ] && echo "left: $T0"
[ "$fail" = 0 ] && echo "READOUT BLOCK TEST PASS" || echo "READOUT BLOCK TEST FAILED"
exit $fail
