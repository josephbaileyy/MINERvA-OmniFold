#!/bin/bash
# Test of install_pin.py, on the laptop. A temp tree holds, copied from the worktree, every file check_ledger.py --figures
# reads (make_figures.sh, the ledger, each G row's installed figure, committed copy and SHA256SUMS, and Fig. 1's installed
# copy) and run-a2's SHA256SUMS; a stand-in run record under the package's run/ holds an "after" PDF and its listing.
#   1. before the install, check_ledger.py --figures passes on the temp tree;
#   2. install_pin.py runs; check_ledger.py --figures passes again, with the re-pointed row;
#   3. make_figures.sh parses (bash -n); its diff is the one line commented and the new block; and its restyle install
#      block, run as written (REPO = the temp tree), installs the eleven figures, the relabelled one with its new digest;
#   4. mutants: a committed copy that is not the pinned digest fails check_ledger.py; a run listing that is not the
#      after PDF's digest, and a second install on an installed tree, are refused by install_pin.py.
#   bash test_install_pin.sh <repo worktree> <python>
set -u
REPO=$(cd "$1" && pwd); PY=$2
H=$(cd "$(dirname "$0")" && pwd); T0=$(mktemp -d "${TMPDIR:-/tmp}/tip.XXXXXX"); fail=0
ok() { echo "PASS $1"; }; bad() { echo "FAIL $1"; fail=1; }
M=docs/orchestration/state/2d-closeout/stageF/methods; PS=$M/pull-sd-relabel-20261117
CL=$REPO/$M/re2-integration/check_ledger.py
tree() {  # tree <dir>: the minimal tree
  "$PY" -I - "$REPO" "$1" <<'PYT'
import shutil, sys
from pathlib import Path
R, T = Path(sys.argv[1]), Path(sys.argv[2])
M = "docs/orchestration/state/2d-closeout/stageF/methods"
need = {"docs/analysis-note/make_figures.sh", f"{M}/re2-integration/ledger.tsv",
        "docs/analysis-note/figures/paper_fig1_validation.pdf", f"{M}/fig-restyle-20261031/run-a2/after/SHA256SUMS"}
for ln in (R / M / "re2-integration/ledger.tsv").read_text().splitlines():
    c = ln.split("\t")
    if c[0] != "G":
        continue
    copydir = c[6] if len(c) == 7 else f"{M}/re2-integration/figs"
    need |= {f"docs/analysis-note/figures/{c[2]}", f"{copydir}/{c[2]}", c[4]}
for p in sorted(need):
    (T / p).parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(R / p, T / p)
print(len(need))
PYT
}
standin() {  # standin <tree> [listed digest]: run/after/out/<pdf> and run/SHA256SUMS
  local r=$1/$PS/run; mkdir -p "$r/after/out"
  printf '%%PDF-1.4 stand-in for the relabelled figure\n' > "$r/after/out/MEFHC_5iter_pull_full.pdf"
  local d=${2:-$(shasum -a 256 "$r/after/out/MEFHC_5iter_pull_full.pdf" | cut -d' ' -f1)}
  printf '%s  after/logs/pull_full.log\n%s  after/out/MEFHC_5iter_pull_full.pdf\n' "$(printf x | shasum -a 256 | cut -d' ' -f1)" "$d" > "$r/SHA256SUMS"
}
ledger() { "$PY" -I "$CL" "$1" --figures --ledger "$1/$M/re2-integration/ledger.tsv" 2>&1; }
T=$T0/t; mkdir -p "$T"; n=$(tree "$T"); standin "$T"
out=$(ledger "$T"); [ $? = 0 ] && ok "1. before the install: $(echo "$out" | tail -1) ($n files)" || { bad "1. before"; echo "$out" | tail -5; }
cp "$T/docs/analysis-note/make_figures.sh" "$T0/make_figures.before"
"$PY" -I "$H/install_pin.py" "$T" > "$T0/install.out" 2>&1 && ok "2. install_pin.py: $(tail -1 "$T0/install.out")" || { bad "2. install_pin.py"; cat "$T0/install.out"; }
NEW=$(shasum -a 256 "$T/$PS/run/after/out/MEFHC_5iter_pull_full.pdf" | cut -d' ' -f1)
out=$(ledger "$T"); [ $? = 0 ] && ok "2. after the install: $(echo "$out" | tail -1)" || { bad "2. after"; echo "$out" | tail -5; }
grep -q "^G	FIG-MEFHC_5iter_pull_full	MEFHC_5iter_pull_full.pdf	$NEW	$PS/run/SHA256SUMS	after/out/MEFHC_5iter_pull_full.pdf	$PS/figs$" "$T/$M/re2-integration/ledger.tsv" \
  && ok "2. the G row is re-pointed to $PS/figs and run/SHA256SUMS" || bad "2. the G row"
bash -n "$T/docs/analysis-note/make_figures.sh" && ok "3. make_figures.sh parses" || bad "3. make_figures.sh syntax"
d=$(diff "$T0/make_figures.before" "$T/docs/analysis-note/make_figures.sh" | grep -E '^[<>]')
[ "$(echo "$d" | grep -c '^<')" = 1 ] && [ "$(echo "$d" | grep -c '^>')" = 7 ] \
  && echo "$d" | grep -q "^< install_restyle_fig MEFHC_5iter_pull_full.pdf  *fd84d992f3b212be" \
  && echo "$d" | grep -q "^> # install_restyle_fig MEFHC_5iter_pull_full.pdf  *fd84d992f3b212be" \
  && echo "$d" | grep -q "^> install_restyle_fig MEFHC_5iter_pull_full.pdf  *$NEW$" \
  && ok "3. make_figures.sh diff: the old line commented, the new block (1 line out, 7 in)" || { bad "3. make_figures.sh diff"; echo "$d"; }
# the restyle install block as written, from its RSG line through the new install line
mk=$T/docs/analysis-note/make_figures.sh
a=$(grep -n '^RSG="$REPO/docs/orchestration/state/2d-closeout/stageF/methods/fig-restyle-20261031/figs-a2"$' "$mk" | cut -d: -f1)
b=$(grep -n "^install_restyle_fig MEFHC_5iter_pull_full.pdf  *$NEW$" "$mk" | cut -d: -f1)
mkdir -p "$T0/figdir"
{ echo "set -u; REPO=$T; FIGDIR=$T0/figdir; sha256_of() { shasum -a 256 \"\$1\" | cut -d' ' -f1; }"; sed -n "${a},${b}p" "$mk"; } > "$T0/block.sh"
bash "$T0/block.sh" > "$T0/block.out" 2>&1; rc=$?
[ "$rc" = 0 ] && [ "$(grep -c '^  installed ' "$T0/block.out")" = 11 ] \
  && [ "$(shasum -a 256 "$T0/figdir/MEFHC_5iter_pull_full.pdf" | cut -d' ' -f1)" = "$NEW" ] \
  && [ "$(shasum -a 256 "$T0/figdir/MEFHC_5iter_fig13.pdf" | cut -d' ' -f1)" = a5530bfc0c3220a0a522dfcaa52f143752dd67465c525237acb0ad8cf722237f ] \
  && ok "3. the install block runs: 11 installed, pull_full ${NEW:0:12}, fig13 still figs-a2's a5530bfc" || { bad "3. install block (rc $rc)"; cat "$T0/block.out"; }
# mutants
cp "$T/$PS/figs/MEFHC_5iter_pull_full.pdf" "$T0/keep.pdf"; printf 'x' >> "$T/$PS/figs/MEFHC_5iter_pull_full.pdf"
out=$(ledger "$T"); rc=$?
[ "$rc" = 1 ] && echo "$out" | grep -q "FIG-MEFHC_5iter_pull_full" && ok "4. a tampered committed copy fails check_ledger.py" || { bad "4. tampered copy (rc $rc)"; echo "$out" | tail -3; }
cp "$T0/keep.pdf" "$T/$PS/figs/MEFHC_5iter_pull_full.pdf"
cp "$mk" "$T0/mk.installed"; cp "$T/$M/re2-integration/ledger.tsv" "$T0/ledger.installed"
"$PY" -I "$H/install_pin.py" "$T" > "$T0/again.out" 2>&1 && bad "4. a second install was not refused" \
  || { cmp -s "$mk" "$T0/mk.installed" && cmp -s "$T/$M/re2-integration/ledger.tsv" "$T0/ledger.installed" \
       && ok "4. a second install is refused, writing nothing: $(grep -m1 -o 'AssertionError.*' "$T0/again.out" | cut -c1-60)" \
       || bad "4. a refused second install changed a file"; }
U=$T0/u; mkdir -p "$U"; tree "$U" > /dev/null; standin "$U" 0000000000000000000000000000000000000000000000000000000000000000
"$PY" -I "$H/install_pin.py" "$U" > "$T0/wrong.out" 2>&1 && bad "4. a wrong listing was not refused" \
  || ok "4. a run listing that is not the PDF's digest is refused: $(grep -m1 -o 'AssertionError.*' "$T0/wrong.out" | cut -c1-80)"
find "$T0" -type f -exec rm -f {} + 2>/dev/null; find "$T0" -type l -exec rm -f {} + 2>/dev/null; find "$T0" -depth -type d -exec rmdir {} \; 2>/dev/null
[ -e "$T0" ] && echo "left: $T0"
[ "$fail" = 0 ] && echo "INSTALL PIN TEST PASS" || echo "INSTALL PIN TEST FAILED"
exit $fail
