#!/usr/bin/env bash
# usage: bash make_redline.sh <worktree> <scratch-dir>
# The paper's redline against the pre-integration base 8b0f83fd, for the final draft (d). It runs after build_all.sh
# has built the worktree's note and paper, because the redline reads main_note.aux (the paper's xr pointers) and the
# paper's bibliography from the built tree.
#   - both trees are flattened with latexpand: the base from `git archive 8b0f83fd`, the current tree from the worktree;
#   - latexdiff marks deletions and insertions (UNDERLINE). Tables are shown whole, without markup inside, because
#     latexdiff's markup inside tabular breaks them;
#   - it is compiled in a copy of the built docs/analysis-note.
# Labels that r19 removed (r19/check_ledger.py REMOVABLE) print as ?? inside deleted text only.
set -euo pipefail
W=$1; T=$2
rm -rf "$T"; mkdir -p "$T/old" "$T/new"
git -C "$W" archive 8b0f83fd docs/analysis-note | tar -x -C "$T/old"
cp -R "$W/docs/analysis-note/." "$T/new/"
(cd "$T/old/docs/analysis-note" && latexpand main_paper.tex > "$T/old_flat.tex")
(cd "$T/new" && latexpand main_paper.tex > "$T/new_flat.tex")
latexdiff --type=UNDERLINE --math-markup=whole -c "PICTUREENV=(?:picture|DIFnomarkup|tabular|table)[\w\d*@]*" \
  "$T/old_flat.tex" "$T/new_flat.tex" > "$T/new/redline-paper.tex"
(cd "$T/new" && rm -f redline-paper.aux redline-paper.bbl && latexmk -g -pdf -interaction=nonstopmode redline-paper.tex > /dev/null)
echo "built $T/new/redline-paper.pdf"
