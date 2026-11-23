#!/bin/bash
# Usage: quality_grade.sh <pdf> <tag> <n_figures> <n_tables>
# Gemini-only CHECKLIST graders (no 1-10 scores): per section, per figure group, per table group, and structure.
# Each grader writes issues as JSON lines; the counts are comparable across builds.
# Output: ~/codex-reports/note-measurement/quality/<tag>/
set -u
PDF=$1; TAG=$2; NF=$3; NT=$4
D=/Users/josephbailey/codex-reports/note-measurement/quality/$TAG
mkdir -p $D; cp -p "$PDF" $D/note.pdf
SCHEMA='Write ONLY a JSON Lines file, one issue per line: {"grader":"<name>","kind":"<rubric key>","where":"<section/figure/table and page>","severity":"high|medium|low","quote":"<short exact quote or description>","problem":"<one sentence>","fix":"<concrete fix that adds or drops no claim, number or caveat>"}. If there are no issues for a rubric key, write nothing for it. Never invent; quote what is on the page.'
run(){ # name prompt
  local P=$D/$1; mkdir -p $P; printf '%s\n' "$2" > $P/prompt.txt
  ( cd $P && ~/.local/bin/agy -p "$(cat $P/prompt.txt)" --model gemini-3.8-flash-high --add-dir $D --dangerously-skip-permissions --output-format text > $P/out.txt 2> $P/err.txt </dev/null ) ; }
# Sections: top-level sections 1..13 and appendices A..J.
for s in 1 2 3 4 5 6 7 8 9 10 11 12 13 A B C D E F G H I J; do
run sec-$s "You are a strict physics-journal editor applying a CHECKLIST to one section of $D/note.pdf (a cross-section measurement note). Read ONLY section $s (or Appendix $s) and anything it points to. Rubric keys:
R1 result-first: a paragraph opens with procedure or history instead of its result.
R2 caveat-once: a caveat is restated here although section 12 states it; it should be a short scope label plus a pointer.
R3 stacked: a sentence carries two or more caveats or conditions.
R4 gloss: a label, symbol or code name used before it is defined or pointed to (check the definitions table and the configuration key, Tables 3-4).
R5 history: procedural history (stops, reruns, dates, run IDs, superseded variants) in the body.
R6 duplicate: text that repeats another section's text (name the other section).
R7 pointer: a cross-reference or 'this/these' that lands on the wrong thing.
$SCHEMA Use grader name sec-$s. Write the file to $D/sec-$s/issues.jsonl, then stop." &
done
wait
# Figures, in groups of 6, each grader seeing every figure for the duplication check.
g=1; while [ $g -le $NF ]; do e=$((g+5)); [ $e -gt $NF ] && e=$NF
run fig-$g "You are a strict figure editor. File: $D/note.pdf. Grade Figures $g to $e (look at each figure image and its caption), comparing each with ALL other figures in the note for duplication. Rubric keys:
F1 duplicate: the figure shows substantially the same data or comparison as another figure (name it and say what overlaps).
F2 legible: text in the figure is too small to read at print size, or the figure is too small for its content.
F3 compressed: the panels are crammed or the aspect is squashed; suggest a layout.
F4 caption-match: the caption does not match what is drawn (colors, markers, labels, panels).
F5 takeaway: the caption's first sentence is not the takeaway.
F6 consistency: the size, fonts or palette are inconsistent with the other figures.
$SCHEMA Use grader name fig-$g. Write the file to $D/fig-$g/issues.jsonl, then stop." &
g=$((e+1)); done
# Tables, in groups of 8.
t=1; while [ $t -le $NT ]; do e=$((t+7)); [ $e -gt $NT ] && e=$NT
run tab-$t "You are a strict table editor. File: $D/note.pdf. Grade Tables $t to $e, comparing each with ALL other tables and figures. Rubric keys: T1 duplicate (repeats another table's or figure's numbers; name it), T2 format (inconsistent number formats, units or significant figures), T3 caption (the caption doesn't say what the table shows, or isn't takeaway-first), T4 layout (too wide, cramped, or needs splitting). $SCHEMA Use grader name tab-$t. Write the file to $D/tab-$t/issues.jsonl, then stop." &
t=$((e+1)); done
run structure "You are a first-time reader testing NAVIGATION of $D/note.pdf. For each task, try to find the answer using only the contents list, the reader's guide, the definitions table and the cross-references, and record the pages you visited. Tasks: (1) what quantity is measured, and in which cells; (2) the 2D result's uncertainty and its coverage limit; (3) the sixteen-cell result and its limits; (4) which estimator configuration produced each result; (5) what the joint generator tests found; (6) every choice made after a result was seen; (7) where the analysis history is; (8) what is NOT measured. For each task write one JSON line: {\"grader\":\"structure\",\"kind\":\"N<task#>\",\"where\":\"pages visited\",\"severity\":\"high if not found, medium if found after more than 3 pages, low otherwise\",\"quote\":\"what you found\",\"problem\":\"what made it hard\",\"fix\":\"a navigation fix\"}. Write to $D/structure/issues.jsonl, then stop." &
wait
# Summary counts, by grader and rubric key.
python3 - "$D" <<'EOF'
import json,sys,glob,collections,os
D=sys.argv[1]; c=collections.Counter(); sev=collections.Counter(); n=0; bad=[]
for f in sorted(glob.glob(D+'/*/issues.jsonl')):
    for line in open(f):
        line=line.strip()
        if not line: continue
        try: o=json.loads(line)
        except Exception: bad.append(f); continue
        n+=1; c[o.get('kind','?')]+=1; sev[o.get('severity','?')]+=1
missing=[os.path.basename(p) for p in sorted(glob.glob(D+'/*/')) if not os.path.exists(p+'issues.jsonl')]
print('issues',n,'by severity',dict(sev)); print('by rubric key',dict(sorted(c.items())))
print('graders with no issues file:',missing); print('unparsable lines in:',sorted(set(bad)))
EOF
echo "dir: $D"
