#!/usr/bin/env bash
# usage: make_rater_copy.sh <worktree> <out.txt>
# Builds main_paper from <worktree>/docs/analysis-note TWICE in scratch copies (the worktree is never touched):
#   normal: as the repository builds it (holds render as red [HOLD: ...]);
#   rater:  \pubhold redefined to render nothing (\unskip), after check_holds.py has proved that every
#           \pubhold is a sentence of its own (so dropping it removes exactly that sentence). If any hold
#           shares a sentence with other text the script FAILS: handle that sentence by hand.
# Writes:
#   <out.txt>              pdftotext (default mode) of the hold-free build  -- the full rater copy
#   <out>.normal.txt       pdftotext of the normal build
#   <out>.holddiff.txt     word-level diff normal vs rater; must end "VERDICT: PASS" or the script fails
#   <out>.blind.txt        blinded rater copy (no title/authors/date/acknowledgments/references),
#                          the form scored in the 2026-10-21 calibration (cal/REPORT.md)
# If main_paper.tex (outside comments) contains \externaldocument (xr-hyper pointers into the note), main_note is
# built first in the same scratch copy, so that main_note.aux exists and the pointers resolve.
# Exit 0 only if both builds succeed with no unresolved references, the rater text contains neither "??" nor
# "[HOLD", the normal text contains no "??", and the diff check passes.
set -euo pipefail
WT=$(cd "$1" && pwd); OUT=$2
CAL=$(cd "$(dirname "$0")" && pwd); TOOLS=$CAL/tools
case "$OUT" in /*) ;; *) OUT=$PWD/$OUT ;; esac
SRC=$WT/docs/analysis-note
[ -f "$SRC/main_paper.tex" ] || { echo "FAIL: no $SRC/main_paper.tex"; exit 1; }
tag=$(basename "$OUT" .txt)
B=$CAL/build/$tag
rm -rf "$B"; mkdir -p "$B"
echo "source: $WT ($(git -C "$WT" rev-parse --short HEAD 2>/dev/null || echo 'not a git tree'); dirty files in analysis-note: $(git -C "$WT" status --short -- docs/analysis-note 2>/dev/null | wc -l | tr -d ' '))"

python3 -I "$TOOLS/check_holds.py" "$SRC"/*.tex

DEF='\newcommand{\pubhold}[1]{\textcolor{red}{[HOLD: #1]}}'
n=$(grep -cF "$DEF" "$SRC/main_paper.tex" || true)
[ "$n" = 1 ] || { echo "FAIL: expected exactly one line '$DEF' in main_paper.tex, found $n"; exit 1; }

build() {  # $1 = variant dir name
  local d=$B/$1/docs/analysis-note
  mkdir -p "$d"
  rsync -a --exclude archive/ --exclude '*.aux' --exclude '*.bbl' --exclude '*.fdb_latexmk' --exclude '*.fls' \
        --exclude 'main_*.pdf' --exclude '*.log' --exclude '*.blg' --exclude '*.out' "$SRC/" "$d/"
  if [ "$1" = rater ]; then
    python3 -I - "$d/main_paper.tex" "$DEF" <<'PY'
import sys
p, d = sys.argv[1], sys.argv[2]
s = open(p, encoding="utf-8").read()
assert s.count(d) == 1, "definition not found exactly once"
open(p, "w", encoding="utf-8").write(s.replace(d, r"\newcommand{\pubhold}[1]{\unskip}% rater copy: holds render nothing"))
PY
  fi
  if grep -qE '^[^%]*\\externaldocument' "$d/main_paper.tex"; then
    [ -d "$WT/docs/orchestration/state" ] && mkdir -p "$B/$1/docs/orchestration" && ln -sfn "$WT/docs/orchestration/state" "$B/$1/docs/orchestration/state"
    ( cd "$d" && latexmk -pdf -g -interaction=nonstopmode -halt-on-error main_note.tex > "$B/$1.note-build.log" 2>&1 ) \
      || { echo "FAIL: $1 main_note build (needed for \externaldocument), see $B/$1.note-build.log"; tail -20 "$B/$1.note-build.log"; exit 1; }
    [ -s "$d/main_note.aux" ] || { echo "FAIL: $1 main_note build left no main_note.aux"; exit 1; }
    echo "$1: main_paper uses \externaldocument; built main_note first ($(pdfinfo "$d/main_note.pdf" | awk '/^Pages/{print $2}') pages)"
  fi
  ( cd "$d" && latexmk -pdf -g -interaction=nonstopmode -halt-on-error main_paper.tex > "$B/$1.build.log" 2>&1 ) \
    || { echo "FAIL: $1 build, see $B/$1.build.log"; tail -20 "$B/$1.build.log"; exit 1; }
  if grep -qE 'There were undefined (references|citations)|Citation .* undefined|Reference .* undefined' "$d/main_paper.log"; then
    ( cd "$d" && latexmk -pdf -interaction=nonstopmode main_paper.tex >> "$B/$1.build.log" 2>&1 ) || true
    if grep -qE 'There were undefined (references|citations)' "$d/main_paper.log"; then
      echo "FAIL: $1 build has unresolved references"; exit 1; fi
  fi
  echo "$1 build: $(pdfinfo "$d/main_paper.pdf" | awk '/^Pages/{print $2}') pages"
  pdftotext "$d/main_paper.pdf" "$B/$1.txt"
  if grep -n '??' "$B/$1.txt"; then echo "FAIL: $1 text contains '??' (unresolved reference)"; exit 1; fi
  if [ "$1" = rater ] && grep -n '\[HOLD' "$B/$1.txt"; then echo "FAIL: rater text contains '[HOLD'"; exit 1; fi
}
build normal
build rater

cp "$B/rater.txt" "$OUT"
cp "$B/normal.txt" "${OUT%.txt}.normal.txt"
if ! python3 -I "$TOOLS/holddiff.py" "$B/normal.txt" "$B/rater.txt" > "${OUT%.txt}.holddiff.txt"; then
  # Dropping a hold can reflow the last page so pdftotext emits blocks in another ORDER. Accept that only if the
  # two texts are equal as word multisets after removing hold spans and hyphen joins (added 2026-10-21, r12).
  if python3 -I "$TOOLS/multiset_check.py" "$B/normal.txt" "$B/rater.txt" >> "${OUT%.txt}.holddiff.txt"; then
    echo "holddiff: order differs (layout reflow) but word multisets are equal: PASS (order-insensitive)"
  else
    cat "${OUT%.txt}.holddiff.txt"; echo "FAIL: rater copy differs from the normal build in more than hold text"; exit 1; fi
fi
tail -2 "${OUT%.txt}.holddiff.txt"

# pdftotext can emit the "DATA AVAILABILITY" heading after the reference list although it prints above its text
# (seen in r12). Then the ACKNOWLEDGMENTS..DATA AVAILABILITY cut would also remove the data-availability text, which
# the calibration's documents kept. Put the heading back before the section's first sentence (Joseph's protected
# text), or fail.
# The rater text is the NORMAL build's text with the hold spans removed (check_holds.py proved each hold is a sentence
# of its own), not the rater build's text: dropping a hold reflows the last page, and in r12 the reflow put half of
# the data-availability text after the first reference line, where blinding drops it. The rater build above stays as
# the proof that a hold-free build compiles and differs only in hold text.
python3 -I - "$B/normal.txt" "$OUT" <<'PY'
import re, sys
t = open(sys.argv[1], encoding="utf-8").read()
t2 = re.sub(r"\s*\[HOLD:[^\]]*\]", "", t, flags=re.S)
assert "[HOLD" not in t2
open(sys.argv[2], "w", encoding="utf-8").write(t2)
print("rater text = normal text minus %d hold spans" % len(re.findall(r"\[HOLD:", t)))
PY
python3 -I "$TOOLS/fix_da_order.py" "$OUT"
python3 -I "$TOOLS/blind.py" "$OUT" "${OUT%.txt}.blind.txt" --start '^\(Dated:' --start-after \
  --refs '^\[1\] ' --cut '^ACKNOWLEDGMENTS$' '^DATA AVAILABILITY$' --drop '^[∗†] \S+@\S+$' > "${OUT%.txt}.blind.log"
tail -1 "${OUT%.txt}.blind.log"
grep -nE 'HOLD|Bailey|Nachman|Stanford|stanford\.edu|SLAC|Dated' "${OUT%.txt}.blind.txt" && { echo "FAIL: identifying text survives blinding"; exit 1; } || true
grep -q '^DATA AVAILABILITY$' "${OUT%.txt}.blind.txt" || { echo "FAIL: blinded text lost the data-availability heading"; exit 1; }
# last sentence of the data-availability text (Joseph's protected text, 2026-10-21); if he rewrites it, update this
grep -q 'does not reproduce\.' "${OUT%.txt}.blind.txt" || { echo "FAIL: blinded text lost the end of the data-availability section"; exit 1; }
# and its first sentence, which the acknowledgments cut removes if the heading lands after it (the P1 re-score of #413
# at a55e2686 was scored on such a copy, 2026-10-27); same protected text, same update rule
awk '/^DATA AVAILABILITY$/{h=1; next} h && /^The input data and simulation are the MINERvA open/{ok=1} END{exit !ok}' "${OUT%.txt}.blind.txt" \
  || { echo "FAIL: blinded text lost the first sentence of the data-availability section, or it precedes its heading"; exit 1; }
echo "wrote $OUT and ${OUT%.txt}.{normal,holddiff,blind}.txt"
