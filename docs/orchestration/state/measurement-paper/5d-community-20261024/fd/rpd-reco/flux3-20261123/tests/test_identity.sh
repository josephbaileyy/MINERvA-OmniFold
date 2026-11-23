#!/bin/bash
# test_identity.sh: the fetch's step 2b, the recorded check that flux3's 12 factor products are byte-identical to
# flux2's (the director's ruling (A): a difference is a STOP to the director, not a reading). Local files only.
# usage: bash test_identity.sh
# 1. The block's 12 expected sha256s equal the factor_products of run-61806073's committed flux-extract.json.
# 2. The block is cut from rpd_flux3_fetch.sh, its table swapped for the digests of 12 stand-in files, and run in a temp
#    run/ directory: all equal (12/12, idbad 0), one changed (11/12, DIFFERS), one missing (11/12, DIFFERS).
# 3. The fetch exits 15 on idbad > 0, before its other exits. The mutants then weaken the block; each must fail a case.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
FETCH="$HERE/../rpd_flux3_fetch.sh"
EXTRACT="${FLUX2_EXTRACT:-$HERE/../../flux2-20261122/run-61806073/records/run/flux-extract.json}"  # override outside the repo
T=$(mktemp -d) || exit 9
trap 'rm -rf -- "$T"' EXIT
printf '#!/bin/bash\nexec shasum -a 256 "$@"\n' > "$T/sha256sum"; chmod +x "$T/sha256sum"; export PATH="$T:$PATH"
fails=0
ok() { echo "ok   $1"; }
bad() { echo "FAIL $1"; fails=$((fails + 1)); }

BLOCK=$(awk '/^echo "== 2b\. identity/ {f=1} f {print} f && /^echo "FLUX2 IDENTITY/ {exit}' "$FETCH")
TABLE=$(printf '%s\n' "$BLOCK" | awk '/^done <<.FLUX2.$/ {f=1; next} /^FLUX2$/ {f=0} f')
WANT=$(python3 -I -c 'import json,sys; p=json.load(open(sys.argv[1]))["factor_products"]; print("\n".join(p[k]["sha256"] + " " + k for k in sorted(p)))' "$EXTRACT")
[ "$TABLE" = "$WANT" ] && [ "$(printf '%s\n' "$TABLE" | wc -l | tr -d ' ')" = 12 ] && ok "the 12 expected sha256s equal run-61806073's records" || bad "expected table"
grep -qxF '[ "$idbad" -eq 0 ] || { echo "STOP: $idbad factor product(s) differ from flux2'"'"'s; a STOP to the director, not a reading; the records were sent"; finish 15; }' "$FETCH" \
  && ok "the fetch exits 15 on a difference" || bad "exit 15 line"
[ "$(grep -n 'finish 15' "$FETCH" | cut -d: -f1)" -lt "$(grep -n 'finish 0$' "$FETCH" | tail -1 | cut -d: -f1)" ] && ok "exit 15 comes before the success exit" || bad "exit order"

run_block() {  # run_block BLOCK_TEXT -> output; works in $T/w with stand-ins whose digests make the table
  rm -rf -- "$T/w"; mkdir -p "$T/w/run"
  local table=""
  for pl in 1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P; do
    printf 'product %s\n' "$pl" > "$T/w/run/flux-factors-$pl.npz"
    table+="$(shasum -a 256 "$T/w/run/flux-factors-$pl.npz" | cut -d' ' -f1) $pl"$'\n'
  done
  [ -n "${CHANGE:-}" ] && echo changed >> "$T/w/run/flux-factors-$CHANGE.npz"
  [ -n "${REMOVE:-}" ] && rm -f "$T/w/run/flux-factors-$REMOVE.npz"
  local script
  script=$(python3 -I -c 'import sys; b, t, new = sys.argv[1:]; assert b.count(t) == 1; print(b.replace(t, new.rstrip("\n")))' "$1" "$TABLE" "$table")
  (cd "$T/w" && bash -c "$script"$'\necho "idbad=$idbad"')
}

cases() {  # cases BLOCK_TEXT
  local out
  out=$(run_block "$1")
  printf '%s\n' "$out" | grep -qx 'FLUX2 IDENTITY: 12/12 byte-identical' && printf '%s\n' "$out" | grep -qx 'idbad=0' || { fails=$((fails + 1)); [ "$Q" = 1 ] || echo "FAIL all equal"; }
  out=$(CHANGE=1M run_block "$1")
  printf '%s\n' "$out" | grep -q '^DIFFERS FROM FLUX2 1M ' && printf '%s\n' "$out" | grep -qx 'idbad=1' && printf '%s\n' "$out" | grep -qx 'FLUX2 IDENTITY: 11/12 byte-identical' || { fails=$((fails + 1)); [ "$Q" = 1 ] || echo "FAIL one changed"; }
  out=$(REMOVE=1A run_block "$1")
  printf '%s\n' "$out" | grep -q '^DIFFERS FROM FLUX2 1A \[\]' && printf '%s\n' "$out" | grep -qx 'idbad=1' || { fails=$((fails + 1)); [ "$Q" = 1 ] || echo "FAIL one missing"; }
}

Q=0; before=$fails; cases "$BLOCK"
[ "$fails" -eq "$before" ] && ok "all equal: 12/12; one changed and one missing: 11/12, DIFFERS, idbad 1"
echo "IDENTITY-TESTS :: $([ "$fails" -eq 0 ] && echo PASS || echo "FAIL ($fails)")"
[ "$fails" -eq 0 ] || exit 1

TAB=$(printf '\t')
MUTANTS="count-dropped${TAB}idbad=\$((idbad + 1))${TAB}:
compare-inverted${TAB}if [ \"\$got\" = \"\$want\" ]; then${TAB}if [ \"\$got\" != \"\$want\" ]; then
total-hardcoded${TAB}\$((12 - idbad))/12${TAB}12/12"
Q=1; killed=0; total=0
while IFS="$TAB" read -r name old new; do
  total=$((total + 1))
  n=$(python3 -I -c 'import sys; print(sys.argv[1].count(sys.argv[2]))' "$BLOCK" "$old")
  [ "$n" = 1 ] || { echo "MUTANT $name: old text occurs $n times"; continue; }
  M=$(python3 -I -c 'import sys; t, a, b = sys.argv[1:]; print(t.replace(a, b, 1), end="")' "$BLOCK" "$old" "$new")
  fails=0; cases "$M"
  if [ "$fails" -gt 0 ]; then killed=$((killed + 1)); echo "KILLED   $name ($fails cases)"; else echo "SURVIVED $name"; fi
done <<< "$MUTANTS"
echo "IDENTITY-MUTANTS :: $killed/$total killed"
[ "$killed" -eq "$total" ]
