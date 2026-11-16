#!/bin/bash
# The readout connect's place (connect-g2r-readout-<PH>.sh, the lines between its >>> and <<< markers), run verbatim
# in the CLUSTER'S LAYOUT: a local stand-in G for /pscratch holds $O and the deploy $C; the clone's URL is the local
# checkout at M (the connect's URL variable, outside the block). Inside the place, test_readout_place.py does
# g2r_readout's audit-sensitive operations (budget_Q at :285, TemporaryDirectory, the products TSV, np.savez,
# write_text, the modules check) under the open audit with G guarded. It does NOT run a phase (that needs the real
# products), and it does not test /dev/shm, Linux or Python 3.11. sha256sum and wc get macOS forms. Cases:
#   place     the block as written: clean clone at M, 19 bound sums OK; every operation OK from the place; the place
#             removed on exit, logged
#   ctl-dep   control, the readout from the deploy $C with TMPDIR, TSV and out under $O: every operation REFUSED
#   m-o, m-c  mutants SHM_BASE=$O and SHM_BASE=$C: refused, exit 6, nothing left
#   m-commit  mutant M = PRE_M: the bound sums fail, exit 7, the place removed
#   verdict   the verdict block on g2r_readout.main()'s own line and rc (only the phase function stood in): data PASS,
#             tune COVERS and UNDER-COVERS -> PASS with the graded verdict recorded; INVALID and STOP -> INVALID; an
#             atime move -> ATIME; the old "verdict=PASS only" classifier (mutant) calls a graded tune INVALID
#   copy-out  the place, a finished readout's files, the copy-out block: $O/readout writable -> copied, verified, W
#             removed; read-only -> exit 9, W KEPT with out/, readout.log and products.tsv (the clone and tmp gone);
#             the old trap (mutant) deletes them
#   static    the three connects differ only in PH; the readout runs from $DD with --products and --out in $W; every
#             TMPDIR is $W/tmp; the copy-out comes after the readout process
#     bash test_readout_place.sh [checkout at M]
set -u
H=$(cd "$(dirname "$0")" && pwd)
K=${1:-/Users/josephbailey/cov2d-work/wt-glue}; CN=$H/connect-g2r-readout-data.sh
PY=${PY:-/opt/homebrew/bin/python3.13}
M=401733bce290ce122cfbf38f1526e120f174b3ec; PRE_M=a60547692df5f963e428cdfe4661fc51ab785b7b
echo "connects $(for t in data G18 AR23; do printf '%s=%s ' $t "$(shasum -a 256 "$H/connect-g2r-readout-$t.sh" | cut -c1-8)"; done)checkout $(git -C "$K" rev-parse HEAD) porcelain=$(git -C "$K" status --porcelain | wc -l | tr -d ' ')"
BLK=$(sed -n '/# >>> the readout.s place/,/# <<< the readout.s place/p' "$CN" | sed 's/^    //')
VBLK=$(sed -n '/# >>> the verdict/,/# <<< the verdict/p' "$CN" | sed 's/^    //')
CBLK=$(sed -n '/# >>> the copy-out/,/# <<< the copy-out/p' "$CN" | sed 's/^    //')
[ "$(printf '%s\n' "$VBLK" | wc -l | tr -d ' ')" -ge 8 ] && [ "$(printf '%s\n' "$CBLK" | wc -l | tr -d ' ')" -ge 8 ] || { echo "FAIL the verdict or copy-out block was not found"; exit 1; }
[ "$(printf '%s\n' "$BLK" | wc -l | tr -d ' ')" -ge 30 ] || { echo "FAIL the block was not found"; exit 1; }
W0=$(mktemp -d "${TMPDIR:-/tmp}/rpt.XXXXXX"); W0=$(cd "$W0" && pwd -P)
G=$W0/pscratch; O=$G/cov2d-g2r-20261112; C=$G/cov2d-g2r-deploy-j1
mkdir -p "$O/out" "$W0/shm"
git clone --quiet --shared --no-checkout "$K" "$C" && git -C "$C" checkout --quiet --detach "$M" || { echo "FAIL the stand-in deploy"; exit 1; }
URL=$K PH=data; export O C M URL PH G
sha256sum() { shasum -a 256 "$@"; }; wc() { command wc "$@" | tr -d ' '; }; export -f sha256sum wc
ok=0
res() { local v=$1; shift; echo "$v $*"; [ "$v" = PASS ] || ok=1; }
TSVLINE=$(printf 'D_Ua_x\t%s\t%064d\tg2r\tFlux:0' "$O/out/D_Ua_x/xsec.root" 0)
# place
( SHM_BASE=$W0/shm; eval "$BLK"; echo "W=$W"
  printf '%s\n' "$TSVLINE" > "$W/products.tsv"
  G2R_GUARD=$G "$PY" -B "$H/test_readout_place.py" "$DD" "$W/products.tsv" "$W/out"; echo "harness_rc=$?"; exit 0 ) > "$W0/place.out" 2>&1; rc=$?
w=$(sed -n 's/^W=//p' "$W0/place.out")
if [ "$rc" = 0 ] && grep -q '^harness_rc=0$' "$W0/place.out" && grep -q "clone head=$M porcelain_ignored=0 bound sums 19 OK" "$W0/place.out" \
   && [ "$(grep -cE '^(budget|tempdir|products_tsv|out_npz|out_json|modules) OK$' "$W0/place.out")" = 6 ] \
   && grep -q "^removed the readout place $w rc=0 left=no$" "$W0/place.out" && [ -n "$w" ] && [ ! -e "$w" ] \
   && case $w in "$W0/shm/"*) true ;; *) false ;; esac
then res PASS "place: 6/6 operations OK from the /dev/shm stand-in clone (budget_Q at its digest); removed"
else res FAIL "place rc=$rc"; grep -vE '^Warning' "$W0/place.out" | tail -12; fi
# ctl-dep: the readout from the guarded deploy, TMPDIR/TSV/out under $O
mkdir -p "$O/tmpx" "$O/outx"; printf '%s\n' "$TSVLINE" > "$O/products.tsv"
TMPDIR=$O/tmpx G2R_GUARD=$G "$PY" -B "$H/test_readout_place.py" "$C" "$O/products.tsv" "$O/outx" > "$W0/ctl.out" 2>&1; rc=$?
if [ "$rc" = 1 ] && [ "$(grep -cE '^(budget|tempdir|products_tsv|out_npz|out_json|modules) REFUSED$' "$W0/ctl.out")" = 6 ]
then res PASS "ctl-dep: from the deploy under the guard, 6/6 operations REFUSED"
else res FAIL "ctl-dep rc=$rc"; cat "$W0/ctl.out"; fi
# m-o, m-c
for mm in O C; do
    base=$O; [ $mm = C ] && base=$C
    before=$(ls -A "$base" | wc -l)
    ( SHM_BASE=$base; eval "$BLK"; echo REACHED ) > "$W0/m$mm.out" 2>&1; rc=$?
    if [ "$rc" = 6 ] && grep -q 'is under a guarded tree' "$W0/m$mm.out" && ! grep -q REACHED "$W0/m$mm.out" && [ "$(ls -A "$base" | wc -l)" = "$before" ]
    then res PASS "m-$mm: killed (rc=6, nothing left)"; else res FAIL "m-$mm rc=$rc (survived)"; cat "$W0/m$mm.out"; fi
done
# m-commit
( SHM_BASE=$W0/shm; M=$PRE_M; eval "$BLK"; echo REACHED ) > "$W0/mcommit.out" 2>&1; rc=$?
w=$(grep -oE "removed the readout place [^ ]+" "$W0/mcommit.out" | awk '{print $NF}')
if [ "$rc" = 7 ] && grep -q 'FAILED' "$W0/mcommit.out" && ! grep -q REACHED "$W0/mcommit.out" && [ -n "$w" ] && [ ! -e "$w" ]
then res PASS "m-commit: killed (rc=7, the bound sums fail at PRE_M, removed)"; else res FAIL "m-commit rc=$rc (survived)"; tail -5 "$W0/mcommit.out"; fi
# verdict: main()'s own line and rc through the verdict block
vrun() {  # vrun <phase> <verdict> <atime> <block>: prints V and graded
    local ph=$1 v=$2 at=$3 blk=$4 Wv; Wv=$(mktemp -d "$W0/v.XXXX"); mkdir -p "$Wv/out"
    "$PY" -B "$H/test_readout_verdict.py" "$K" "$ph" "$v" "$at" "$Wv/out" > "$Wv/readout.log" 2>&1; local rcv=$?
    ( W=$Wv; rc=$rcv; PH=X; PHASE=$(echo "$ph" | tr a-z A-Z); eval "$blk"; echo "V=$V graded=${graded:-} rc=$rc" )
}
bad=""
for c in "data PASS 0 PASS" "data INVALID 0 INVALID" "data STOP 0 INVALID" "tune COVERS 0 PASS" "tune UNDER-COVERS 0 PASS" \
         "tune INVALID 0 INVALID" "tune STOP 0 INVALID" "tune STOP 1 ATIME" "data PASS 1 ATIME"; do
    set -- $c; got=$(vrun "$1" "$2" "$3" "$VBLK" | sed -n 's/^V=\([A-Z]*\) .*/\1/p')
    want=$4; [ "$got" = "$want" ] || bad="$bad [$1 $2 atime=$3: $got, want $want]"
done
gr=$(vrun tune UNDER-COVERS 0 "$VBLK" | grep -o 'verdict=UNDER-COVERS')
OLD=$(printf '%s\n' "$VBLK" | sed -e '/^case "\$PHASE" in DATA/d' -e '/^graded=/d' -e 's#^if \[ "\$rc" = 0 \] && printf .*then V=PASS#if [ "$rc" = 0 ] \&\& grep -q "^G2R-$PHASE verdict=PASS" "$W/readout.log"; then V=PASS#')
mo=$(vrun tune UNDER-COVERS 0 "$OLD" | sed -n 's/^V=\([A-Z]*\) .*/\1/p')
if [ -z "$bad" ] && [ -n "$gr" ] && [ "$mo" = INVALID ]; then res PASS "verdict: 9/9 phase x verdict cases as main() returns; graded verdict recorded; old classifier killed (UNDER-COVERS -> $mo)"
else res FAIL "verdict:$bad graded='$gr' old-classifier='$mo'"; fi
# copy-out: writable and read-only $O/readout
crun() {  # crun <tag> <trap-mutant 0|1> <readonly 0|1>
    local tag=$1 mut=$2 ro=$3 b=$BLK O2=$W0/O-$1; mkdir -p "$O2/out"
    [ "$mut" = 1 ] && b=$(printf '%s\n' "$BLK" | sed "s#^trap .*EXIT\$#trap 'rm -rf \"\$W\"; echo \"removed the readout place \$W\"' EXIT#")
    if [ "$ro" = 1 ]; then mkdir -p "$O2/readout"; chmod 555 "$O2/readout"; fi
    ( SHM_BASE=$W0/shm; O=$O2; RD=$O2/readout/data; eval "$b"; echo "W=$W"
      : > "$W/.protect"; echo '{"v":1}' > "$W/out/data_g2r.json"; echo npz > "$W/out/data_g2r.npz"
      echo "G2R-DATA verdict=PASS controls_failed=[] stop=[]" > "$W/readout.log"; echo "row" > "$W/products.tsv"
      (cd "$W/out" && sha256sum -- * > "$W/out.sha256")
      eval "$CBLK"; echo "COPY-OK"; exit 0 ) > "$W0/c-$tag.out" 2>&1; echo $?
}
r=$(crun ok 0 0); w=$(sed -n 's/^W=//p' "$W0/c-ok.out")
okc=0; [ "$r" = 0 ] && grep -q '^COPY-OK$' "$W0/c-ok.out" && grep -q "^removed the readout place $w rc=0 left=no$" "$W0/c-ok.out" && [ ! -e "$w" ] \
   && [ -s "$W0/O-ok/readout/data/data_g2r.npz" ] && [ -s "$W0/O-ok/readout/data/readout.log" ] || okc=1
r2=$(crun ro 0 1); w2=$(sed -n 's/^W=//p' "$W0/c-ro.out")
roc=0; [ "$r2" = 9 ] && grep -q "^KEPT the readout place $w2" "$W0/c-ro.out" && [ -s "$w2/out/data_g2r.npz" ] && [ -s "$w2/readout.log" ] \
   && [ -s "$w2/products.tsv" ] && [ ! -e "$w2/deploy" ] && [ ! -e "$w2/tmp" ] || roc=1
r3=$(crun mut 1 1); w3=$(sed -n 's/^W=//p' "$W0/c-mut.out")
mc=1; [ "$r3" = 9 ] && [ ! -e "$w3" ] && mc=0
chmod 755 "$W0/O-ro/readout" "$W0/O-mut/readout" 2>/dev/null
if [ "$okc" = 0 ] && [ "$roc" = 0 ] && [ "$mc" = 0 ]; then res PASS "copy-out: writable -> copied, verified, removed; read-only -> rc 9, W KEPT with outputs, log, TSV; old trap (mutant) deletes them (killed)"
else res FAIL "copy-out ok=$okc (rc $r) ro=$roc (rc $r2) mutant_deleted=$mc (rc $r3)"; tail -4 "$W0/c-ok.out" "$W0/c-ro.out" "$W0/c-mut.out"; fi
# static
d1=$(diff "$CN" "$H/connect-g2r-readout-G18.sh" | grep -c '^[<>]'); d2=$(diff "$CN" "$H/connect-g2r-readout-AR23.sh" | grep -c '^[<>]')
p1=$(diff "$CN" "$H/connect-g2r-readout-G18.sh" | grep -cE '^[<>] PH=(data|G18)$'); p2=$(diff "$CN" "$H/connect-g2r-readout-AR23.sh" | grep -cE '^[<>] PH=(data|AR23)$')
inv=$(grep -n 'g2r_readout.py \$ARGS' "$CN" | cut -d: -f1); cpo=$(grep -n 'mkdir "\$RD"' "$CN" | cut -d: -f1)
ta=$(grep -E '^[[:space:]]*(export[[:space:]]+)?TMPDIR=' "$CN" | grep -vc 'TMPDIR=\$W/tmp ')
if [ "$d1" = 2 ] && [ "$p1" = 2 ] && [ "$d2" = 2 ] && [ "$p2" = 2 ] && grep -q 'cd "\$DD/2d-unfolding/cov2d/g2r" && \$RUN' "$CN" \
   && grep -q -- '--products "\$W/products.tsv" --map-sha "\$mapsha" --out "\$W/out"' "$CN" && [ "$ta" = 0 ] \
   && [ -n "$inv" ] && [ -n "$cpo" ] && [ "$inv" -lt "$cpo" ]
then res PASS "static: the three differ only in PH; readout from \$DD, TSV and out in \$W; TMPDIR=\$W/tmp; copy-out after"
else res FAIL "static d1=$d1 p1=$p1 d2=$d2 p2=$p2 tmpdir_other=$ta inv=$inv copyout=$cpo"; fi
rm -rf "$W0"
[ "$ok" = 0 ] && echo "READOUT PLACE TEST PASS" || echo "READOUT PLACE TEST FAILED"
exit $ok
