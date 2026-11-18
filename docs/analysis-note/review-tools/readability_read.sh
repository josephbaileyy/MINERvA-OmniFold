#!/bin/bash
# Usage: readability_read.sh <pdf> <tag>
# Gemini-only readability reads of the note, in four page ranges plus a skim pass.
# Writes only under ~/codex-reports/note-measurement/readability/<tag>/ and prints one score line per part.
set -u
PDF=$1; TAG=$2
D=/Users/josephbailey/codex-reports/note-measurement/readability/$TAG
mkdir -p $D; cp -p "$PDF" $D/note.pdf
NP=$(pdfinfo "$PDF" | awk '/^Pages/{print $2}')
q=$((NP/4))
RANGES=("1-$q" "$((q+1))-$((2*q))" "$((2*q+1))-$((3*q))" "$((3*q+1))-$NP")
run(){ # name prompt
  local P=$D/$1; mkdir -p $P; printf '%s\n' "$2" > $P/prompt.txt
  ( cd $P && ~/.local/bin/agy -p "$(cat $P/prompt.txt)" --model gemini-3.8-flash-high --add-dir $D --dangerously-skip-permissions --output-format text > $P/out.txt 2> $P/err.txt </dev/null ) ; }
i=0
for r in "${RANGES[@]}"; do i=$((i+1))
run part$i "You are a demanding journal editor judging READABILITY only, not physics correctness. Read-only: write only your report. The file is $D/note.pdf, a physics analysis note (a cross-section measurement, MINERvA open data, unbinned OmniFold). Read ONLY pages $r. Use American spelling.
Report:
1. A first-pass readability score out of 10 for these pages. Calibrate: published physics analysis papers read at 6-7. Give one sentence of reason.
2. The 6 hardest passages: page, a short quote, why a first-pass reader stalls (jargon or unglossed labels, a long sentence, several caveats in one sentence, procedural history, an unclear antecedent), and a rewritten sentence that keeps every claim, number, caveat and pointer. Never drop or soften a caveat; you may move it into its own sentence.
3. Unglossed internal labels or symbols used before they are defined (e.g. configuration letters, R00-R15, D1/W1/W3, 'Estimator R'), with the page of first use.
4. Section and subsection titles in this range that a skimmer would not understand, each with a proposed title.
Do not judge or change physics content. Write the report to $D/part$i/report.md, then stop." &
done
run skim "You are a busy physicist SKIMMING. Read-only: write only your report. File: $D/note.pdf. Read ONLY the title, abstract, executive summary, table of contents, the what-is-measured table, every figure with its caption, and every table caption. Do NOT read body text.
Report: (1) in 3 sentences: what is measured, the main results, the main limitations; then what you could NOT work out. (2) The count of figure captions whose first sentence states the takeaway, out of the total. (3) The 5 changes that would most improve the skim layer. Use American spelling. Write the report to $D/skim/report.md, then stop." &
wait
# a part's score: the first N/10 once the prompt's calibration ("published papers read at 6-7/10") is removed; grep -o
# printed every match on the first line, so "3.5 / 10 (... 6–7 / 10)" gave two scores and a calibration-only line gave 7
for p in part1 part2 part3 part4; do printf '%s %s (pp %s): ' $TAG $p "${RANGES[$(( ${p#part} - 1 ))]}"; s=$(sed -E 's/\([^)]*([Cc]alibrat|[Pp]ublished|typical)[^)]*\)//g' $D/$p/report.md 2>/dev/null | grep -v -i -E '^\s*\*?\(?calibrat' | grep -o -m1 -E '[0-9]+(\.[0-9])? ?/ ?10|[0-9]+(\.[0-9])? out of 10' | head -1); [ -n "$s" ] && echo "$s" || echo "NO SCORE (see $D/$p/report.md)"; done
# the skim's number is its caption-takeaway count (item 2): take the first count on a line naming the takeaway, not the
# first "N of M" anywhere (50e1a368e printed "0 of 300" from the limitations summary; "Figure 33/34" also matches)
printf '%s skim: captions with the takeaway first ' $TAG; c=$(grep -i -E '[0-9]+ ?(out of|of|/) ?[0-9]+' $D/skim/report.md 2>/dev/null | grep -i -m1 'takeaway' | grep -o -m1 -E '[0-9]+ ?(out of|of|/) ?[0-9]+'); [ -n "$c" ] && echo "$c" || echo "(no count found; see $D/skim/report.md)"
echo "dir: $D"
