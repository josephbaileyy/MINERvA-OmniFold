#!/usr/bin/env bash
# usage: make_supp_rater_copy.sh <worktree> <out.txt>
# The Supplemental Material's rater copy (round 5, 2026-11-08), built as make_rater_copy.sh builds the paper's:
# a scratch copy of <worktree>/docs/analysis-note (the worktree is never touched), main_note built first so that the
# Supplement's xr-hyper pointers into the note resolve, then main_supplement.
# Writes:
#   <out.txt>         pdftotext (default mode) of the Supplement
#   <out>.blind.txt   blinded copy: no title, authors or reference list
# The Supplement has no \pubhold, so there is one build. Exit 0 only if both builds succeed with no unresolved
# reference or citation, the text holds no "??" or "[HOLD", check_supp_pointers.py passes on the source, every table
# environment of the source prints its "Table S<n>:" caption somewhere in the text (pdftotext may not start a line with it), every figure
# environment its "Figure S<n>:" caption, both before and after blinding, and no identifying text survives blinding.
set -euo pipefail
WT=$(cd "$1" && pwd); OUT=$2
CAL=$(cd "$(dirname "$0")" && pwd); TOOLS=$CAL/tools
case "$OUT" in /*) ;; *) OUT=$PWD/$OUT ;; esac
SRC=$WT/docs/analysis-note
[ -f "$SRC/main_supplement.tex" ] || { echo "FAIL: no $SRC/main_supplement.tex"; exit 1; }
tag=$(basename "$OUT" .txt)
B=$CAL/build/$tag
rm -rf "$B"; mkdir -p "$B/docs/analysis-note"
echo "source: $WT ($(git -C "$WT" rev-parse --short HEAD 2>/dev/null || echo 'not a git tree'); dirty files in analysis-note: $(git -C "$WT" status --short -- docs/analysis-note 2>/dev/null | wc -l | tr -d ' '))"
( cd "$SRC" && python3 -I check_supp_pointers.py )
d=$B/docs/analysis-note
rsync -a --exclude archive/ --exclude '*.aux' --exclude '*.bbl' --exclude '*.fdb_latexmk' --exclude '*.fls' \
      --exclude 'main_*.pdf' --exclude '*.log' --exclude '*.blg' --exclude '*.out' "$SRC/" "$d/"
[ -d "$WT/docs/orchestration/state" ] && mkdir -p "$B/docs/orchestration" && ln -sfn "$WT/docs/orchestration/state" "$B/docs/orchestration/state"
# The symlink points back into the tree that holds build/: left in place, a recursive glob that follows symlinks
# (verify_hash_bindings.py's docs/**) loops through it and hangs the pre-commit hook. Remove it on every exit.
trap 'rm -f "$B/docs/orchestration/state"' EXIT
for t in main_note main_supplement; do
  ( cd "$d" && latexmk -pdf -g -interaction=nonstopmode -halt-on-error "$t.tex" > "$B/$t.build.log" 2>&1 ) \
    || { echo "FAIL: $t build, see $B/$t.build.log"; tail -20 "$B/$t.build.log"; exit 1; }
  if grep -qE 'There were undefined (references|citations)' "$d/$t.log"; then
    ( cd "$d" && latexmk -pdf -interaction=nonstopmode "$t.tex" >> "$B/$t.build.log" 2>&1 ) || true
    if grep -qE 'There were undefined (references|citations)' "$d/$t.log"; then
      echo "FAIL: $t build has unresolved references"; exit 1; fi
  fi
  echo "$t build: $(pdfinfo "$d/$t.pdf" | awk '/^Pages/{print $2}') pages"
done
pdftotext "$d/main_supplement.pdf" "$OUT"
if grep -n '??' "$OUT"; then echo "FAIL: text contains '??' (unresolved reference)"; exit 1; fi
if grep -n '\[HOLD' "$OUT"; then echo "FAIL: text contains '[HOLD'"; exit 1; fi
# a table that breaks across pages (xltabular, Tables S9 and S10 since 2026-11-12) is a table environment too
n_env=$(grep -v '^[[:space:]]*%' "$SRC/supplemental_body.tex" | grep -cE '\\begin\{(table|xltabular)\}' || true)
n_cap=$(grep -oE 'Table S[0-9]+:' "$OUT" | sort -u | wc -l | tr -d ' ')
[ "$n_env" = "$n_cap" ] || { echo "FAIL: $n_env table environments in the source, $n_cap 'Table S<n>:' captions in the text"; exit 1; }
echo "tables: $n_cap of $n_env captions present"
# Figures too (the referee recheck of 2026-11-11, RESPONSE.md m10): Figure S2's float printed after the references, and
# blinding, which cuts there, dropped its caption while the table count passed. Every figure environment must print its
# "Figure S<n>:" caption, before blinding and after it.
n_fenv=$(grep -v '^[[:space:]]*%' "$SRC/supplemental_body.tex" | grep -c '\\begin{figure' || true)
n_fcap=$(grep -oE 'Figure S[0-9]+:' "$OUT" | sort -u | wc -l | tr -d ' ')
[ "$n_fenv" = "$n_fcap" ] || { echo "FAIL: $n_fenv figure environments in the source, $n_fcap 'Figure S<n>:' captions in the text"; exit 1; }
echo "figures: $n_fcap of $n_fenv captions present"
python3 -I "$TOOLS/blind.py" "$OUT" "${OUT%.txt}.blind.txt" --start '^Joseph Bailey and Benjamin Nachman$' --start-after \
  --refs '^References$' > "${OUT%.txt}.blind.log"
tail -1 "${OUT%.txt}.blind.log"
grep -nE 'HOLD|Bailey|Nachman|Stanford|stanford\.edu|SLAC' "${OUT%.txt}.blind.txt" && { echo "FAIL: identifying text survives blinding"; exit 1; } || true
n_cap_b=$(grep -oE 'Table S[0-9]+:' "${OUT%.txt}.blind.txt" | sort -u | wc -l | tr -d ' ')
[ "$n_cap_b" = "$n_cap" ] || { echo "FAIL: blinding dropped a table: $n_cap_b of $n_cap captions left"; exit 1; }
n_fcap_b=$(grep -oE 'Figure S[0-9]+:' "${OUT%.txt}.blind.txt" | sort -u | wc -l | tr -d ' ')
[ "$n_fcap_b" = "$n_fcap" ] || { echo "FAIL: blinding dropped a figure: $n_fcap_b of $n_fcap captions left"; exit 1; }
echo "wrote $OUT and ${OUT%.txt}.blind.txt ($(wc -w < "${OUT%.txt}.blind.txt" | tr -d ' ') words)"
