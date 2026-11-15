#!/bin/bash
# The envtest-r2 connect's suites' place (the lines between its >>> and <<< markers), run verbatim in the CLUSTER'S
# LAYOUT: a local stand-in G for /pscratch holds both $O and the deploy $C (a shared clone of the checkout at M), and
# the open audit's guarded trees are cov2d_blocks.GUARDED plus G. sha256sum and wc get macOS forms; nothing else is
# stood in. This tests the block and the suites under it, NOT /dev/shm, Linux or Python 3.11. Cases:
#   place     the block as written: a clean clone at M in the shm stand-in, the bound sums OK; the four suites from it,
#             test_g2r_glue under the audit (Ran 18, OK), the clone clean after; the place removed on exit, logged
#   ctl-c     control, r2-0bb5de1e's layout: TMPDIR outside, the suites' cwd in $C: glue FAILS (Ran 14, errors=11)
#   ctl-r1    control, r1's layout: TMPDIR under $O, cwd in $C: glue FAILS as r1 did (Ran 11, errors=13)
#   early     the block, then an early exit 4: the place is still removed
#   m-o, m-c  mutants SHM_BASE=$O and SHM_BASE=$C: refused, exit 6, nothing left
#   m-commit  mutant M = PRE_M: the clone's bound sums fail, exit 7, the place removed
#   static    every cov2d_blocks.GUARDED entry at M is refused in the block; the suites cd into $SC, never $C; one
#             TMPDIR assignment
#     bash test_envtest_r2_tmpdir.sh [checkout at M] [connect]
set -u
H=$(cd "$(dirname "$0")" && pwd)
K=${1:-/Users/josephbailey/cov2d-work/wt-glue}; CN=${2:-$H/connect-g2r-envtest-r2.sh}
PY=${PY:-/opt/homebrew/bin/python3.13}
M=401733bce290ce122cfbf38f1526e120f174b3ec; PRE_M=a60547692df5f963e428cdfe4661fc51ab785b7b
echo "connect $(shasum -a 256 "$CN" | cut -c1-64) checkout $(git -C "$K" rev-parse HEAD) porcelain=$(git -C "$K" status --porcelain | wc -l | tr -d ' ')"
BLK=$(sed -n '/# >>> the suites. place/,/# <<< the suites. place/p' "$CN" | sed 's/^    //')
[ "$(printf '%s\n' "$BLK" | wc -l | tr -d ' ')" -ge 12 ] || { echo "FAIL the block was not found"; exit 1; }
SUMS=$(sed -n '/^cat > "\$R2\/bound.sha256" <<.SUMS.$/,/^SUMS$/p' "$CN" | sed '1d;$d')
[ "$(printf '%s\n' "$SUMS" | wc -l | tr -d ' ')" = 19 ] || { echo "FAIL the 19 bound sums were not found"; exit 1; }
W=$(mktemp -d "${TMPDIR:-/tmp}/r2t.XXXXXX"); W=$(cd "$W" && pwd -P)
G=$W/pscratch; O=$G/cov2d-g2r-20261112; C=$G/cov2d-g2r-deploy-j1; R2=$O/logs/envtest-r2
mkdir -p "$R2" "$W/shm"; printf '%s\n' "$SUMS" > "$R2/bound.sha256"
git clone --quiet --shared --no-checkout "$K" "$C" && git -C "$C" checkout --quiet --detach "$M" || { echo "FAIL the stand-in deploy"; exit 1; }
export O C R2 M G
sha256sum() { shasum -a 256 "$@"; }; wc() { command wc "$@" | tr -d ' '; }; export -f sha256sum wc
ok=0
res() { local v=$1; shift; echo "$v $*"; [ "$v" = PASS ] || ok=1; }
SUITES="2d-unfolding/cov2d/g2r/tests:test_g2r 2d-unfolding/re2/tests:test_re2_miss_map 2d-unfolding/cov2d/g2r/tests:test_g2r_glue 2d-unfolding/cov2d/g2r/tests:test_g2r_jobs"
suites() {  # suites <root> <tag>: the four, glue under the audit with G guarded
    local root=$1 tag=$2 d m r all=0
    for t in $SUITES; do d=${t%%:*}; m=${t##*:}
        if [ "$m" = test_g2r_glue ]; then (cd "$root/$d" && G2R_GUARD=$G "$PY" -B "$H/test_envtest_r2_tmpdir.py" "$root/$d" "$m") > "$W/$tag.$m" 2>&1
        else (cd "$root/$d" && "$PY" -B -m unittest "$m") > "$W/$tag.$m" 2>&1; fi
        r=$?; echo "suite $m rc=$r $(grep -E '^(Ran|OK|FAILED)' "$W/$tag.$m" | tr '\n' ' ')"; [ "$r" = 0 ] || all=1
    done; return $all
}
# place
( SHM_BASE=$W/shm; eval "$BLK"; echo "SR=$SR"; suites "$SC" place; echo "suites_rc=$?"
  echo "clone porcelain after=$(git -C "$SC" status --porcelain --ignored | wc -l)"; exit 0 ) > "$W/place.out" 2>&1; rc=$?
sr=$(sed -n 's/^SR=//p' "$W/place.out")
if [ "$rc" = 0 ] && grep -q '^suites_rc=0$' "$W/place.out" && grep -q "clone head=$M porcelain_ignored=0 bound sums 19 OK" "$W/place.out" \
   && grep -q '^suite test_g2r_glue rc=0 Ran 18 tests' "$W/place.out" && grep -q '^clone porcelain after=0$' "$W/place.out" \
   && grep -q "^removed the suites place $sr rc=0 left=no$" "$W/place.out" && [ -n "$sr" ] && [ ! -e "$sr" ] \
   && case $sr in "$W/shm/"*) true ;; *) false ;; esac
then res PASS "place: $(grep -c '^suite .* rc=0 ' "$W/place.out") suites rc 0, glue $(grep -oE 'Ran 18 tests' "$W/place.test_g2r_glue") OK under the guard; clone clean; removed"
else res FAIL "place rc=$rc"; grep -E '^(suite|removed|clone|the suites|suites place)' "$W/place.out"; fi
# ctl-c: r2-0bb5de1e's layout (TMPDIR outside, cwd in $C)
d=2d-unfolding/cov2d/g2r/tests; td=$(mktemp -d "$W/shm/c.XXXX")
(cd "$C/$d" && TMPDIR=$td G2R_GUARD=$G "$PY" -B "$H/test_envtest_r2_tmpdir.py" "$C/$d" test_g2r_glue) > "$W/ctlc" 2>&1; rc=$?
if [ "$rc" = 1 ] && grep -q '^Ran 14 tests' "$W/ctlc" && grep -q 'FAILED (errors=11)' "$W/ctlc" && grep -q "open($C/docs/" "$W/ctlc"
then res PASS "ctl-c: the cluster layout with only TMPDIR moved fails: Ran 14, errors=11, refusals in \$C/docs"
else res FAIL "ctl-c rc=$rc $(grep -E '^(Ran|OK|FAILED)' "$W/ctlc" | tr '\n' ' ')"; fi
# ctl-r1: r1's layout (TMPDIR under $O, cwd in $C)
td=$(mktemp -d "$O/tmp-suites.XXXXXX")
(cd "$C/$d" && TMPDIR=$td G2R_GUARD=$G "$PY" -B "$H/test_envtest_r2_tmpdir.py" "$C/$d" test_g2r_glue) > "$W/ctlr1" 2>&1; rc=$?; rm -rf "$td"
if [ "$rc" = 1 ] && grep -q '^Ran 11 tests' "$W/ctlr1" && grep -q 'FAILED (errors=13)' "$W/ctlr1"
then res PASS "ctl-r1: r1's layout fails as r1 did: Ran 11, errors=13"
else res FAIL "ctl-r1 rc=$rc $(grep -E '^(Ran|OK|FAILED)' "$W/ctlr1" | tr '\n' ' ')"; fi
# early
( SHM_BASE=$W/shm; eval "$BLK"; echo "SR=$SR"; exit 4 ) > "$W/early.out" 2>&1; rc=$?
sr=$(sed -n 's/^SR=//p' "$W/early.out")
if [ "$rc" = 4 ] && [ -n "$sr" ] && [ ! -e "$sr" ] && grep -q 'left=no$' "$W/early.out"; then res PASS "early: rc=4, removed"
else res FAIL "early rc=$rc"; cat "$W/early.out"; fi
# m-o, m-c
for mm in O C; do
    base=$O; [ $mm = C ] && base=$C
    before=$(ls -A "$base" | wc -l)
    ( SHM_BASE=$base; eval "$BLK"; echo REACHED ) > "$W/m$mm.out" 2>&1; rc=$?
    if [ "$rc" = 6 ] && grep -q 'is under a guarded tree' "$W/m$mm.out" && ! grep -q REACHED "$W/m$mm.out" && [ "$(ls -A "$base" | wc -l)" = "$before" ]
    then res PASS "m-$mm: killed (rc=6, nothing left)"; else res FAIL "m-$mm rc=$rc (survived)"; cat "$W/m$mm.out"; fi
done
# m-commit
( SHM_BASE=$W/shm; M=$PRE_M; eval "$BLK"; echo "SR=$SR"; echo REACHED ) > "$W/mcommit.out" 2>&1; rc=$?
sr=$(sed -n 's/^SR=//p' "$W/mcommit.out"); [ -n "$sr" ] || sr=$(grep -oE "removed the suites place [^ ]+" "$W/mcommit.out" | awk '{print $NF}')
if [ "$rc" = 7 ] && grep -q 'FAILED' "$W/mcommit.out" && ! grep -q REACHED "$W/mcommit.out" && [ -n "$sr" ] && [ ! -e "$sr" ]
then res PASS "m-commit: killed (rc=7, the bound sums fail at PRE_M, removed)"; else res FAIL "m-commit rc=$rc (survived)"; tail -5 "$W/mcommit.out"; fi
# static
gd=$(git -C "$K" show HEAD:2d-unfolding/cov2d/cov2d_blocks.py | sed -n 's/^GUARDED = (\(.*\))$/\1/p' | tr -d '" ' | tr ',' ' ')
cs=$(printf '%s\n' "$BLK" | sed -n '/^case /,/^esac/p'); miss=""
for x in $gd; do printf '%s' "$cs" | grep -qF "$x/*" || miss="$miss $x"; done
na=$(grep -cE '^[[:space:]]*(export[[:space:]]+)?TMPDIR=' "$CN")
cdc=$(grep -cE 'cd "\$C/\$1"' "$CN"); cds=$(grep -cE 'cd "\$SC/\$1"' "$CN")
if [ -n "$gd" ] && [ -z "$miss" ] && [ "$na" = 1 ] && [ "$cdc" = 0 ] && [ "$cds" = 1 ] && ! grep -q 'tmp-suites' "$CN"
then res PASS "static: GUARDED ($gd) refused; suites cd \$SC; one TMPDIR assignment"
else res FAIL "static gd='$gd' missing='$miss' tmpdir_assignments=$na cd_C=$cdc cd_SC=$cds"; fi
rm -rf "$W"
[ "$ok" = 0 ] && echo "ENVTEST-R2 SUITES-PLACE TEST PASS" || echo "ENVTEST-R2 SUITES-PLACE TEST FAILED"
exit $ok
