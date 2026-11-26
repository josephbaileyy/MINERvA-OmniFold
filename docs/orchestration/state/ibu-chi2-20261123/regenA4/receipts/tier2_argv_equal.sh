#!/usr/bin/env bash
# A4's tension step equals tier2.sh's (40e7b0fa) tension arm 1, as arms.sh launches it: same argv, environment and
# working directory once the run-specific roots are named (OUT, CAP, HOME, MPL). Nothing is drawn: both run against a
# stub venv named rootmpl3108 whose python3 records its cwd, argv and environment and exits 0.
#   bash tier2_argv_equal.sh <repo tree at the A4 commit> <scratch dir, must not exist>
set -u
REPO=$1; TMP=$2
[ -e "$TMP" ] && { echo "REFUSE: $TMP exists"; exit 2; }
HERE=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$TMP/rootmpl3108/bin" "$TMP/calls" "$TMP/w2" "$TMP/figrun"
cat > "$TMP/rootmpl3108/bin/python3" <<STUB
#!/bin/bash
f=\$(mktemp "$TMP/calls/call.XXXXXX")
{ echo "CWD \$PWD"; for a in "\$@"; do echo "ARG \$a"; done; env | LC_ALL=C sort | sed 's/^/ENV /'; } > "\$f"
exit 0
STUB
chmod +x "$TMP/rootmpl3108/bin/python3"
# The methods tree both scripts read, from the repository (arms.sh deletes and writes captures in it: a copy).
git -C "$REPO" archive HEAD docs/orchestration/state/2d-closeout/stageF/methods/note-figstyle-20261117 | tar -x -C "$TMP/w2"
X=/Users/josephbailey/cov2d-work/figfetch/er-anc/xsec.root
# tier2.sh, unchanged apart from its two roots (W, V), run with FIGRUN in the scratch dir (arms.sh's default is the
# real ~/cov2d-work/figrun, whose arm directories it empties).
sed -e "s#^W=/Users/josephbailey/cov2d-work/wt-figs;#W=$TMP/w2;#" -e "s#^V=/Users/josephbailey/cov2d-work/figenv/rootmpl3108;#V=$TMP/rootmpl3108;#" \
  "$HERE/tier2.sh" > "$TMP/tier2_stub.sh"
diff <(sed -e "s#$TMP/w2#/Users/josephbailey/cov2d-work/wt-figs#" -e "s#$TMP/rootmpl3108#/Users/josephbailey/cov2d-work/figenv/rootmpl3108#" "$TMP/tier2_stub.sh") "$HERE/tier2.sh" \
  > /dev/null || { echo "FAIL: the stub copy of tier2.sh differs beyond its two roots"; exit 1; }
( export FIGRUN="$TMP/figrun"; bash "$TMP/tier2_stub.sh" > "$TMP/tier2.out" 2>&1 )
mkdir -p "$TMP/calls_t2" && mv "$TMP"/calls/call.* "$TMP/calls_t2/"
A4_VENV="$TMP/rootmpl3108" bash "$HERE/regenA4_run.sh" "$TMP/w2" old "$X" "$TMP/fr" > "$TMP/a4.out" 2>&1
mkdir -p "$TMP/calls_a4" && mv "$TMP"/calls/call.* "$TMP/calls_a4/"
pick() {  # the one call that runs palette_run.py over diagnose_tension.py
  local hit=(); for f in "$1"/call.*; do grep -q 'palette_run.py$' "$f" && grep -q 'diagnose_tension.py$' "$f" && hit+=("$f"); done
  [ ${#hit[@]} = 1 ] || { echo "FAIL: $1 has ${#hit[@]} tension arm-1 calls" >&2; return 1; }; echo "${hit[0]}"; }
t2=$(pick "$TMP/calls_t2") || exit 1; a4=$(pick "$TMP/calls_a4") || exit 1
norm_t2() { sed -e "s#$TMP/figrun/tension/arm1#OUT#g" -e "s#$TMP/w2/docs/orchestration/state/2d-closeout/stageF/methods/note-figstyle-20261117/runs/tension/arm1/capture/tension#CAP#g" \
  -e "s#$TMP/figrun/home#HOME#g" -e "s#$TMP/figrun/mplcfg-rootmpl3108#MPL#g" -e "s#$TMP/w2#W#g" -e "s#$TMP#T#g" "$1"; }
norm_a4() { sed -e "s#$TMP/fr/tn/o#OUT#g" -e "s#$TMP/fr/cap/tn#CAP#g" -e "s#$TMP/fr/home#HOME#g" -e "s#$TMP/fr/mplcfg-rootmpl3108#MPL#g" \
  -e "s#$TMP/w2#W#g" -e "s#$TMP#T#g" "$1"; }
grep -v -E '^ENV (SHLVL|_|OLDPWD)=' <(norm_t2 "$t2") > "$TMP/t2.norm"; grep -v -E '^ENV (SHLVL|_|OLDPWD)=' <(norm_a4 "$a4") > "$TMP/a4.norm"
echo "== tier2.sh tension arm 1 (normalized)"; cat "$TMP/t2.norm"
if diff "$TMP/t2.norm" "$TMP/a4.norm"; then echo "TIER2-ARGV-EQUAL :: PASS"; else echo "TIER2-ARGV-EQUAL :: FAIL"; exit 1; fi
