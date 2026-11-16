#!/bin/bash
# Tests of the version-B' package, on the laptop (no cluster access):
#   stale pin  re2c_fig1.py pins the current make_figs.py, refuses make_figs.py 4e18c266 (7fc9ce93's) at its pin
#              check, and no longer holds 4e18c266 as a pin; the control arm's K1 is no longer 71a2ea48.
#   identity   fig1_identity.py on route A's arrays (the tmp/fig_arrays_q.npz re2c_fig1.py writes) PASSes with the
#              current make_figs.py, and each mutant of it (a copy with one exact substitution, asserted once) FAILs
#              the check named, with every other check left as it is not asserted.
#   bash test_bprime.sh <repo worktree> <route A run dir: tmp/fig_arrays_q.npz, in/uqmedian.tex> <python>
set -u
REPO=$(cd "$1" && pwd); RA=$(cd "$2" && pwd); PY=$3
H=$(cd "$(dirname "$0")" && pwd); MF=$REPO/publication/release/figs/make_figs.py; RF=$REPO/2d-unfolding/re2/partc/re2c_fig1.py
T0=$(mktemp -d "${TMPDIR:-/tmp}/tbp.XXXXXX"); fail=0
ok() { echo "PASS $1"; }; bad() { echo "FAIL $1"; fail=1; }
sha() { shasum -a 256 "$1" | cut -d' ' -f1; }
ARR=$RA/tmp/fig_arrays_q.npz; VAL=$RA/in/uqmedian.tex
[ "$(sha "$ARR")" = 28daab09b5a221d02d0f72fa2a595fafa42aa510083322bb25d2b4304c84a726 ] && [ "$(sha "$VAL")" = 536f0aaaac13c6502ec3454407912375234863c6f790298e6a7a9ba6fa6b4eb7 ] \
  && ok "inputs: route A's fig_arrays_q.npz (28daab09) and uqmedian.tex (536f0aaa)" || { bad "inputs"; exit 1; }
git -C "$REPO" show 7fc9ce93fcbcf4014055fb167fb0f04ab2a78b2c:publication/release/figs/make_figs.py > "$T0/old_make_figs.py"
[ "$(sha "$T0/old_make_figs.py")" = 4e18c26681fc86dcfef2861c7c0126aa2df4839376d967b18f08a7d77664ee67 ] || { bad "old make_figs.py"; exit 1; }
# --- stale pin
pin=$("$PY" -I -c "import re, sys; print(re.search(r'\"make_figs\": \"([0-9a-f]{64})\"', open(sys.argv[1]).read()).group(1))" "$RF")
[ "$pin" = "$(sha "$MF")" ] && ok "stale-pin: re2c_fig1.py pins the current make_figs.py (${pin:0:8})" || bad "stale-pin: re2c_fig1.py pins $pin, make_figs.py is $(sha "$MF")"
! grep -q 4e18c26681fc86dc "$RF" && ok "stale-pin: re2c_fig1.py holds no 4e18c266" || bad "stale-pin: re2c_fig1.py still holds 4e18c266"
# re2c_fig1.py checks its pins before reading any input but the hashed files; every other argument is a dummy file
for k in npz reduce values cov s5 pl comb budget sums; do : > "$T0/$k"; done
"$PY" -I "$RF" --npz "$T0/npz" --reduce "$T0/reduce" --make-figs "$T0/old_make_figs.py" --values "$T0/values" --tmp "$T0/tmp" \
  --outdir "$T0/out" --cov "$T0/cov" --s5-npz "$T0/s5" --playlist-npz "$T0/pl" --combination "$T0/comb" --budget "$T0/budget" \
  --step-a-sums "$T0/sums" > "$T0/stale.out" 2>&1; rc=$?
# the npz pin is checked first and the dummy npz fails it, so check make_figs alone with the npz pin removed
"$PY" -I - "$RF" "$T0/rf_mf_only.py" <<'PYS'
import re, sys
s = open(sys.argv[1]).read()
a = 'for k, want in PINS.items():'
assert s.count(a) == 1
open(sys.argv[2], "w").write(s.replace(a, 'for k, want in [("make_figs", PINS["make_figs"])]:'))
PYS
"$PY" -I "$T0/rf_mf_only.py" --npz "$T0/npz" --reduce "$T0/reduce" --make-figs "$T0/old_make_figs.py" --values "$T0/values" --tmp "$T0/tmp" \
  --outdir "$T0/out" --cov "$T0/cov" --s5-npz "$T0/s5" --playlist-npz "$T0/pl" --combination "$T0/comb" --budget "$T0/budget" \
  --step-a-sums "$T0/sums" > "$T0/stale2.out" 2>&1; rc2=$?
grep -q "^\[FAIL\] make_figs: sha256 4e18c26681fc86dcfef2861c7c0126aa2df4839376d967b18f08a7d77664ee67 != pinned $pin" "$T0/stale2.out" && [ "$rc2" = 1 ] \
  && ok "stale-pin: re2c_fig1.py refuses make_figs.py 4e18c266 (rc $rc2: $(head -1 "$T0/stale2.out" | cut -c1-60)...)" || { bad "stale-pin: refusal (rc $rc2)"; cat "$T0/stale2.out"; }
[ "$rc" = 1 ] && ok "stale-pin: the unmodified script also refuses (rc $rc, at its first pin)" || bad "stale-pin: unmodified rc $rc"
L=$REPO/2d-unfolding/re2/partc/re2c_fig1_local.sh
grep -q '^    want out/fig1_validation.pdf fee46c1a8b60a09701444373e9dbfbf106bffdd42759928b0979c8eeb57135d1$' "$L" && ! grep -q 'want out/fig1_validation.pdf 71a2ea48' "$L" \
  && ok "stale-pin: the control arm's K1 is fee46c1a, not 71a2ea48" || bad "stale-pin: control arm K1"
# --- identity
idrun() {  # idrun <name> <make_figs> [extra args]; output in $T0/<name>.out, rc in $T0/<name>.rc
  local name=$1 mf=$2; shift 2
  "$PY" -I "$H/fig1_identity.py" --arrays "$ARR" --values "$VAL" --old "$T0/old_make_figs.py" --new "$mf" --outdir "$T0/$name" \
    --old-fig1 1ead58a2223ecf88f3de505d7cbcca76ab306af49814ea7c9d50ec0f2c373e0c \
    --fig2 57f3cc601281950cf9251b04a627efa3e0d803eca6620178839c48f9d4b0782a \
    --fig3 e9d1bb01fc79e061b95b6e058a2aa2a03275429db5c4531b5e3d9ec63d65fa93 "$@" > "$T0/$name.out" 2>&1; echo $? > "$T0/$name.rc"
}
idrun clean "$MF"
[ "$(cat "$T0/clean.rc")" = 0 ] && [ "$(grep -c '^PASS F' "$T0/clean.out")" = 10 ] && ! grep -q '^FAIL' "$T0/clean.out" \
  && ok "identity clean: 10 checks PASS, rc 0" || { bad "identity clean"; grep -v timestamp "$T0/clean.out"; }
idrun wrong-old "$MF" --new-fig1 0000000000000000000000000000000000000000000000000000000000000000
grep -q '^FAIL F1 ' "$T0/wrong-old.out" && [ "$(cat "$T0/wrong-old.rc")" = 1 ] && ok "identity F1: a wrong --new-fig1 digest FAILs F1" || bad "identity F1"
mutant() {  # mutant <name> <check that must FAIL> <regex its FAIL line must show: the detector> <old string> <new string>
  local name=$1 chk=$2 why=$3; shift
  "$PY" -I - "$MF" "$T0/mf_$name.py" "$3" "$4" <<'PYM'
import sys
s = open(sys.argv[1]).read(); a, b = sys.argv[3], sys.argv[4]
assert s.count(a) == 1, a
open(sys.argv[2], "w").write(s.replace(a, b))
PYM
  [ $? = 0 ] || { bad "mutant $name: substitution"; return; }
  idrun "$name" "$T0/mf_$name.py"
  grep "^FAIL $chk" "$T0/$name.out" | grep -qE "$why" && [ "$(cat "$T0/$name.rc")" = 1 ] && ok "mutant $name: $chk FAILs, showing /$why/" \
    || { bad "mutant $name: $chk did not FAIL"; grep -E '^(PASS|FAIL)' "$T0/$name.out"; }
}
mutant top-colour "F3b" 'differing axes \[0, 2\]' 'top.stairs(ours / unit, edges, color="#c0392b"' 'top.stairs(ours / unit, edges, color="#c0392c"'
mutant ratio-label "F4" 'other axes differing \[1, 3\]' 'bot.set_ylabel("ratio to\npublished", fontsize=7.5)' 'bot.set_ylabel("ratio to\nPublished", fontsize=7.5)'
mutant hist-values "F5" 'values == r_i: False' 'hx.hist(p, bins=bins' 'hx.hist(p * (1 + 1e-12), bins=bins'
mutant hist-clipped "F5" 'bins -1.875\.\.1.875 cover r_i -2.572' 'bins = np.arange(min(lo, -3 - w / 2), max(hi, 3 + w / 2) + 1e-9, w)' 'bins = np.arange(-1.875, 1.875 + 1e-9, w)'
mutant hist-width "F5" 'width 0.2\.\.0.2;' '    w = 0.25' '    w = 0.2'
mutant hist-off-zero "F5" 'min \|centre\| 0.1;' 'bins = np.arange(min(lo, -3 - w / 2), max(hi' 'bins = 0.1 + np.arange(min(lo, -3 - w / 2), max(hi'
mutant ref-curve "F5" 'lines 2 ' '    hx.axvline(0, color="k", lw=0.6)' '    hx.axvline(0, color="k", lw=0.6); hx.plot(bins, 0 * bins + 1)'
mutant sd-is-rms "F6" "new \\('205', '0.060', '0.539'\\)" 'SD {p.std():.3f}' 'SD {np.sqrt((p ** 2).mean()):.3f}'
mutant cb-side-label "F4" "colour bar old .*, new \\{'label': '\\\$r_i\\\$', 'title': ''\\}" '    cb.ax.set_title(r"$r_i$", fontsize=8)' '    cb.set_label(r"$r_i$", fontsize=8)'
mutant fig-text "F7" '; [1-9][0-9]* outside' '    fig.savefig(out / "fig1_validation.pdf", metadata=PDF_META)' '    fig.text(0.3, 0.7, "x"); fig.savefig(out / "fig1_validation.pdf", metadata=PDF_META)'
mutant fig2-text "F2 fig2" 'PDF bae0383f' 'fontsize=6.3,' 'fontsize=6.4,'
find "$T0" -type f -exec rm -f {} + 2>/dev/null; find "$T0" -type l -exec rm -f {} + 2>/dev/null; find "$T0" -depth -type d -exec rmdir {} \; 2>/dev/null
[ -e "$T0" ] && echo "left: $T0"
[ "$fail" = 0 ] && echo "BPRIME TEST PASS" || echo "BPRIME TEST FAILED"
exit $fail
