#!/bin/bash
# Usage: meaning_read.sh <lane-tag> <base-sha> <head-sha> [manifest-path-in-repo]
# Runs independent Grok and Gemini meaning reads of a note diff. It writes only under
# ~/codex-reports/note-measurement/reads/<tag>-<head>/ and prints the verdict lines.
set -u
TAG=$1; BASE=$2; HEAD=$3; MAN=${4:-}
REPO=/Users/josephbailey/local-research/MINERvA-OmniFold
git -C $REPO fetch -q origin
H=$(git -C $REPO rev-parse --short=9 $HEAD) || exit 2
D=/Users/josephbailey/codex-reports/note-measurement/reads/$TAG-$H
mkdir -p $D/grok/inputs $D/gemini/inputs $D/opus46/inputs
git -C $REPO diff $BASE $HEAD -- docs/analysis-note > $D/diff.patch
n=$(grep -c '^[+-][^+-]' $D/diff.patch)
for side in grok gemini opus46; do
  cp $D/diff.patch $D/$side/inputs/diff.patch
  for f in $(git -C $REPO diff --name-only $BASE $HEAD -- docs/analysis-note); do
    mkdir -p $D/$side/inputs/pre/$(dirname $f) $D/$side/inputs/post/$(dirname $f)
    git -C $REPO show $BASE:$f > $D/$side/inputs/pre/$f 2>/dev/null || true
    git -C $REPO show $HEAD:$f > $D/$side/inputs/post/$f 2>/dev/null || true
  done
  [ -n "$MAN" ] && git -C $REPO show $HEAD:$MAN > $D/$side/inputs/move-manifest.tsv 2>/dev/null
  # Moves can cross lanes: include every lane manifest present at HEAD.
  for m in $(git -C $REPO ls-tree --name-only $HEAD docs/analysis-note/history-cuts/ 2>/dev/null | grep move-manifest); do
    git -C $REPO show $HEAD:$m > $D/$side/inputs/$(basename $m); done
  cat > $D/$side/prompt.txt <<EOF
You are an independent MEANING reviewer of an edit to a physics analysis note. Read-only: write only your report file.
Your inputs are all under $D/$side/inputs/: diff.patch (unified diff, $n changed lines), pre/ (files before),
post/ (files after), and move-manifest*.tsv (rows of text deliberately moved to another file). Read nothing else.

The authors' rule: an edit may move, merge, reorder or reword text, but must not add, drop or weaken any claim,
number, limitation, qualifier, caveat, or pointer. Text moved out must appear in a manifest row; its destination may
be in another lane's later commit, so a manifest row with an id counts as accounted for.
The note is being reframed from a "methods study" to a "measurement"; that reframing of self-description is allowed,
but must not claim validated coverage, bias within criteria, or fitness for fitting that the pre-image did not claim.

For EVERY hunk give one verdict: OK, DROPPED (content removed with no manifest row), WEAKENED (limitation softened,
qualifier lost, scope widened), ADDED (new claim or number), POINTER (a reference, \\ref, "this"/"these" antecedent, or
section pointer now lands on the wrong thing), with the exact old and new quote for every non-OK verdict.
Check every number in removed lines reappears identically in added lines or in a manifest row.
Do not flag style. Do not invent problems; most hunks should be OK.
End with one line exactly: VERDICT: PASS or VERDICT: FAIL (n findings).
Write the report to $D/$side/report.md, then stop. American spelling.
EOF
done
( cd $D/grok && ~/.grok/bin/grok --cwd $D/grok --prompt-file $D/grok/prompt.txt --permission-mode bypassPermissions --no-subagents --output-format plain > $D/grok/out.txt 2> $D/grok/err.txt </dev/null ) &
( cd $D/gemini && ~/.local/bin/agy -p "$(cat $D/gemini/prompt.txt)" --model gemini-3.8-flash-high --add-dir $D/gemini --dangerously-skip-permissions --output-format text > $D/gemini/out.txt 2> $D/gemini/err.txt </dev/null ) &
( cd $D/opus46 && ~/.local/bin/agy -p "$(cat $D/opus46/prompt.txt)" --model claude-opus-4-6-thinking --add-dir $D/opus46 --dangerously-skip-permissions --output-format text > $D/opus46/out.txt 2> $D/opus46/err.txt </dev/null ) &
wait
for side in grok gemini opus46; do printf '%s %s: ' $TAG $side; grep -h 'VERDICT:' $D/$side/report.md 2>/dev/null | tail -1 || echo "NO REPORT (see $D/$side/err.txt)"; done
echo "dir: $D"
