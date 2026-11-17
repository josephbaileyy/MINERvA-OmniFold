#!/usr/bin/env bash
# usage: make_note_rater_copy.sh <repo> <commit> <outdir>
# The analysis note's analogue of rater-calibration/make_rater_copy.sh (which builds main_paper only). It builds
# main_note from a `git archive` of <commit> into <outdir>/src (never a worktree, so no build directory or symlink lands
# in the repository), extracts the text with pdftotext, and blinds it with rater-calibration/tools/blind.py:
#   kept:    the abstract, the executive summary, the table of contents, the body and ALL appendices (A-H);
#   dropped: the title block (title, authors, affiliations, version and date, repository link), the e-mail footnotes,
#            the acknowledgments, and the reference list. In the note the reference list comes after the appendices,
#            so cutting from it to the end drops no appendix.
#   masked:  the repository URL github.com/josephbaileyy/MINERvA-OmniFold, wherever it survives, becomes [repository].
# Writes <outdir>/note.txt (the full text), <outdir>/note.blind.txt (the rater copy), <outdir>/blind.log and
# <outdir>/check.txt.
# Exit 0 only if the build succeeds with no unresolved reference, neither text contains "??" or "[HOLD", no identifying
# string survives blinding, and the blinded copy is complete: every figure and table caption the build's own .aux
# records (Figure 1..N:, Table 1..M:), every appendix heading A-H, the body's last section heading, and the last line
# of text before the reference list.
set -euo pipefail
REPO=$(cd "$1" && pwd); C=$2; OUT=$3
HERE=$(cd "$(dirname "$0")" && pwd); TOOLS=$HERE/../rater-calibration/tools
[ ! -e "$OUT" ] || { echo "FAIL: $OUT exists"; exit 1; }
mkdir -p "$OUT/src" "$OUT/par"
sha=$(git -C "$REPO" rev-parse "$C^{commit}")
echo "source: $REPO at $sha (git archive; the worktree is not read)"
git -C "$REPO" archive "$sha" docs/analysis-note | tar -x -C "$OUT/src"
D=$OUT/src/docs/analysis-note
rm -rf "$D/archive"
( cd "$D" && PAR_GLOBAL_TEMP=$OUT/par latexmk -pdf -g -interaction=nonstopmode -halt-on-error main_note.tex > "$OUT/build.log" 2>&1 ) \
  || { echo "FAIL: build, see $OUT/build.log"; tail -20 "$OUT/build.log"; exit 1; }
if grep -qE 'There were undefined (references|citations)' "$D/main_note.log"; then
  ( cd "$D" && PAR_GLOBAL_TEMP=$OUT/par latexmk -pdf -interaction=nonstopmode main_note.tex >> "$OUT/build.log" 2>&1 ) || true
  if grep -qE 'There were undefined (references|citations)' "$D/main_note.log"; then echo "FAIL: unresolved references"; exit 1; fi
fi
echo "build: $(pdfinfo "$D/main_note.pdf" | awk '/^Pages/{print $2}') pages; pdf sha256 $(shasum -a 256 "$D/main_note.pdf" | cut -d' ' -f1)"
pdftotext "$D/main_note.pdf" "$OUT/note.txt"
if grep -n '??' "$OUT/note.txt"; then echo "FAIL: text contains '??'"; exit 1; fi
if grep -n '\[HOLD' "$OUT/note.txt"; then echo "FAIL: text contains a hold"; exit 1; fi
python3 -I "$TOOLS/blind.py" "$OUT/note.txt" "$OUT/note.blind.txt" --start '^Abstract$' --refs '^References$' \
  --cut '^Acknowledgments$' '^Guide to the appendices$' --drop '^[∗†]$' --drop '^\S+@\S+\.edu$' > "$OUT/blind.log"
tail -1 "$OUT/blind.log"
python3 -I - "$OUT/note.blind.txt" <<'PY'
import sys
p = sys.argv[1]
t = open(p, encoding="utf-8").read()
n = t.count("github.com/josephbaileyy/MINERvA-OmniFold")
open(p, "w", encoding="utf-8").write(t.replace("github.com/josephbaileyy/MINERvA-OmniFold", "[repository]"))
print(f"repository URL masked: {n}")
PY
if grep -nE 'Bailey|Nachman|Stanford|stanford|SLAC|josephbaileyy|josephrb|HOLD|Version 1\.0' "$OUT/note.blind.txt"; then
  echo "FAIL: identifying text survives blinding"; exit 1; fi
rc=0
python3 -I - "$D/main_note.aux" "$OUT/note.txt" "$OUT/note.blind.txt" > "$OUT/check.txt" <<'PY' || rc=$?
import re, sys
aux, full, blind = (open(p, encoding="utf-8").read() for p in sys.argv[1:4])
nf = len(re.findall(r"\\@writefile\{lof\}\{\\contentsline \{figure\}", aux))
nt = len(re.findall(r"\\@writefile\{lot\}\{\\contentsline \{table\}", aux))
flat = " ".join(blind.split())
bad = [f"Figure {i}:" for i in range(1, nf + 1) if f"Figure {i}:" not in flat]
bad += [f"Table {i}:" for i in range(1, nt + 1) if f"Table {i}:" not in flat]
apps = re.findall(r"\\contentsline \{section\}\{\\numberline \{([A-H])\}([^}\\]*)", aux)
for letter, title in apps:
    head = f"{letter} " + " ".join(title.split()[:3])
    if not re.search(r"(?m)^" + re.escape(head), blind):
        bad.append(f"appendix heading {head!r}")
secs = re.findall(r"\\contentsline \{section\}\{\\numberline \{(\d+)\}([^}\\]*)", aux)
last_num, last_title = secs[-1]
if not re.search(r"(?m)^" + re.escape(f"{last_num} " + " ".join(last_title.split()[:2])), blind):
    bad.append(f"last body section {last_num} {last_title!r}")
lines = full.replace("\f", "\n").split("\n")
r = max(i for i, l in enumerate(lines) if l.strip() == "References")
tail = next(l for l in reversed(lines[:r]) if l.strip() and not l.strip().isdigit())
if " ".join(tail.split()) not in flat:
    bad.append(f"last line before the references {tail!r}")
print(f"figures {nf}, tables {nt}, appendices {len(apps)} ({''.join(a for a, _ in apps)}), body sections {len(secs)}")
print(f"last body section: {last_num} {last_title.strip()}; last line before the references: {tail.strip()!r}")
print(f"words: full text {len(full.split())}; blinded copy {len(blind.split())}")
print("MISSING: " + "; ".join(bad) if bad else "COMPLETE: every figure and table caption, every appendix heading, the last "
      "body section and the last line before the references are in the blinded copy")
sys.exit(1 if bad else 0)
PY
cat "$OUT/check.txt"
[ "$rc" -eq 0 ] || { echo "FAIL: blinded copy incomplete"; exit 1; }
echo "wrote $OUT/note.txt and $OUT/note.blind.txt"
