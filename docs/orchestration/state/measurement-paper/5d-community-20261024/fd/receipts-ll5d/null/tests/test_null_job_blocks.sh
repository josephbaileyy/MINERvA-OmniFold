#!/bin/bash
# Stand-in test of sbatch-ll5d-null.sh's two new blocks, extracted verbatim from the job script:
#   EXPECT: run against the bound code (a git archive of 4231b14d) and $U's real name list (from the bulk evidence's
#           1662 product names); its output for each truth must hash to the job's fixed EXP_<T>_SHA256 with EXP_<T>_N
#           lines. A name list with one block product removed must make it exit 1 (an opened product absent).
#   CHECK:  fake records against the fixed g18 set. Only rc 8 + verdict PASS + moved == the set + the real record path
#           may print CLEAN; rc 0, an extra path, a missing path, verdict INVALID, only an .invalid.json, and no record
#           must each print NOT-CLEAN.
# Exit 0 only if every case behaves.
#     bash test_null_job_blocks.sh sbatch-ll5d-null.sh code4231b14d/nd-unfolding u-names.from-evidence.txt
set -u
JOB=$1; CODE=$2; NAMES=$3
PY=${PY:-/Users/josephbailey/miniconda3/bin/python3}
expect=$(awk '/<<.EXPECT. \|\| stop/ {on = 1; next} /^EXPECT$/ {on = 0} on' "$JOB")
check=$(awk '/<<.CHECK.$/ {on = 1; next} /^CHECK$/ {on = 0} on' "$JOB")
U=/pscratch/sd/j/josephrb/ll5d-unfolds-r2
T0=$(mktemp -d "${TMPDIR:-/tmp}/tnj.XXXXXX")
fail=0
ok() { echo "PASS $1"; }; bad() { echo "FAIL $1"; fail=1; }
for T in g18 ar23; do
  want=$(sed -n "s/^EXP_${T}_SHA256=\([0-9a-f]*\); EXP_${T}_N=\([0-9]*\)$/\1 \2/p" "$JOB")
  printf '%s\n' "$expect" | "$PY" -I -B - "$CODE" "$NAMES" "$U" "$T" "$T0/exp_$T.txt" > "$T0/e.out" 2>&1; rc=$?
  got="$(shasum -a 256 "$T0/exp_$T.txt" | cut -c1-64) $(awk 'END {print NR}' "$T0/exp_$T.txt")"
  [ "$rc" = 0 ] && [ "$got" = "$want" ] && ok "expect-$T reproduces the fixed set ($want)" || { bad "expect-$T rc=$rc got=$got want=$want"; cat "$T0/e.out"; }
done
grep -v '^ll5d_g18_block_Flux_7\.npz$' "$NAMES" > "$T0/names-short.txt"
printf '%s\n' "$expect" | "$PY" -I -B - "$CODE" "$T0/names-short.txt" "$U" g18 "$T0/exp_short.txt" > "$T0/e.out" 2>&1; rc=$?
[ "$rc" = 1 ] && ok "expect-absent-product exits 1" || bad "expect-absent-product rc=$rc"
mk() {  # $1 dir, $2 verdict, $3 moved-file, $4 which ("rec" or "inv")
  "$PY" -I -c 'import json, sys
moved = [l for l in open(sys.argv[3]).read().splitlines() if l]
json.dump({"verdict": sys.argv[2], "atime": {"moved": moved}}, open(sys.argv[1], "w"))' "$1" "$2" "$3"
}
run() {  # $1 label, $2 rc, $3 want (CLEAN|NOT-CLEAN); records already in $D
  printf '%s\n' "$check" | "$PY" -I -B - "$D/null-g18.json" "$D/null-g18.invalid.json" "$T0/exp_g18.txt" "$2" g18 > "$D/out" 2>&1
  if grep -q "^NULL-EXIT g18 $3" "$D/out" && { [ "$3" = NOT-CLEAN ] || ! grep -q NOT-CLEAN "$D/out"; }; then ok "check-$1"
  else bad "check-$1 (want $3)"; sed 's/^/    /' "$D/out"; fi
}
n=0; fresh() { n=$((n + 1)); D=$T0/c$n; mkdir "$D"; }
fresh; mk "$D/null-g18.json" PASS "$T0/exp_g18.txt"; run clean 8 CLEAN
fresh; : > "$D/empty"; mk "$D/null-g18.json" PASS "$D/empty"; run rc0-nothing-moved 0 NOT-CLEAN
fresh; { cat "$T0/exp_g18.txt"; echo "$U/ll5d_g18_toy_all_4751001.npz"; } > "$D/m"; mk "$D/null-g18.json" PASS "$D/m"; run extra-path 8 NOT-CLEAN
fresh; sed 1d "$T0/exp_g18.txt" > "$D/m"; mk "$D/null-g18.json" PASS "$D/m"; run missing-path 8 NOT-CLEAN
fresh; mk "$D/null-g18.json" INVALID "$T0/exp_g18.txt"; run verdict-invalid 8 NOT-CLEAN
fresh; mk "$D/null-g18.invalid.json" INVALID "$T0/exp_g18.txt"; run only-invalid-record 13 NOT-CLEAN
fresh; run no-record 5 NOT-CLEAN
find "$T0" -type f -exec rm -f {} +; find "$T0" -depth -type d -exec rmdir {} \;
[ -e "$T0" ] && echo "left: $T0"
[ "$fail" = 0 ] && echo "NULL-JOB BLOCK TEST PASS" || echo "NULL-JOB BLOCK TEST FAILED"
exit $fail
