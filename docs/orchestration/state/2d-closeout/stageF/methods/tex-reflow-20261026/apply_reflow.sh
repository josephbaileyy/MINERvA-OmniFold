#!/usr/bin/env bash
# Apply the TeX reflow to a fresh worktree at origin/main and prove it (DECISION-20261026 ... section 3).
#   bash apply_reflow.sh WT BRANCH
# Steps: baseline build + text; reflow; remap comment refs; code patches; registry re-cite; results index x2;
# manifest; gates; rebuild + compare. Stops at the first failure. Commits nothing.
set -euo pipefail
R=$(cd "$(dirname "$0")" && pwd)
S=$(cd "$R/.." && pwd)
WT=$1; BR=$2
export TMPDIR=$S/tmp; mkdir -p "$TMPDIR"
git -C "$S/wt-s1b" fetch -q origin
git -C "$S/wt-s1b" worktree add -q -B "$BR" "$WT" origin/main
cd "$WT"
echo "== base $(git rev-parse HEAD)"
OUT=$R/run-$(git rev-parse --short HEAD); rm -rf "$OUT"; mkdir -p "$OUT/base" "$OUT/new"
N=docs/analysis-note
FILES=$(cd $N && ls *.tex | grep -v -E '^(records_results_index|records_estimators|records_entry_numbers)\.tex$')
KEEP="app_provenance.tex app_release_records.tex app_codebase_records.tex app_history.tex main_records.tex"
(cd $N && bash build_all.sh > "$OUT/base-build.log" 2>&1) || { echo "BASE BUILD FAILED"; exit 1; }
for p in main_note main_paper main_primer main_records pet_note; do
  pdftotext -layout $N/$p.pdf "$OUT/base/$p.txt"; pdftotext $N/$p.pdf "$OUT/base/$p.raw.txt"; done
git clean -fdqX $N >/dev/null 2>&1 || true
git status --porcelain | grep -q . && { echo "TREE DIRTY AFTER BASE BUILD"; git status --porcelain | head; exit 1; }
mkdir -p "$OUT/base-src"; (cd $N && cp $FILES "$OUT/base-src/")
(cd $N && python3 "$R/reflow_tex.py" --map "$OUT/map.json" --keep-comments-in-place $KEEP -- $FILES > "$OUT/reflow.log")
(cd $N && python3 "$R/remap_comment_refs.py" "$OUT/map.json" "$OUT/base-src" $FILES > "$OUT/remap.log")
echo "== reflow: $(git diff --shortstat)"; echo "== remap: $(grep -c REMAP "$OUT/remap.log") remapped, $(grep -c KEEP "$OUT/remap.log") kept"
# the records self-test's newline anchors
python3 - <<'EOF'
p='docs/analysis-note/check_note_records.py'; s=open(p).read()
old='"\\n(Ref.~\\\\cite{NoteRecords2026}, superseded values)."'
new='" (Ref.~\\\\cite{NoteRecords2026}, superseded values)."'
n=s.count(old); print(f"== records anchors replaced: {n}"); s=s.replace(old,new); open(p,'w').write(s)
EOF
git apply --3way "$R/code.patch" && echo "== code patch applied"
git add -A $N tools/registry
python3 "$R/recite_registry.py" . "$OUT/base-src" "$OUT/map.json" > "$OUT/recite.log"; echo "== recited $(wc -l < "$OUT/recite.log") rows"
git add docs/orchestration/registry
python3 tools/registry/results_index.py --write > /dev/null 2>&1 || true
git add docs/orchestration/registry $N/records_results_index.tex $N/records_estimators.tex
python3 tools/registry/results_index.py --write | tail -1
git add docs/orchestration/registry $N/records_results_index.tex $N/records_estimators.tex
echo "== gates"
python3 tools/registry/check_registry.py | tail -1
python3 tools/registry/absence_claims.py | tail -1
python3 tools/registry/absence_claims.py --self-test | tail -1
python3 tools/registry/results_index.py --self-test | tail -1
(cd $N && python3 check_note_records.py probe records-inventory-base.json . | tail -1 \
  && python3 check_note_records.py --self-test records-inventory-base.json . | tail -1 \
  && python3 check_note_records.py pin | tail -1 && python3 check_note_records.py --self-test-pin | tail -1)
(cd $N && bash -c "python3 $R/reflow_tex.py --check --keep-comments-in-place $KEEP -- $FILES" > /dev/null) && echo "== idempotent"
python3 -m pytest -q -p no:cacheprovider $N/ 2>&1 | tail -1
(cd $N && bash build_all.sh > "$OUT/new-build.log" 2>&1) || { echo "NEW BUILD FAILED"; exit 1; }
for p in main_note main_paper main_primer main_records pet_note; do
  pdftotext -layout $N/$p.pdf "$OUT/new/$p.txt"; pdftotext $N/$p.pdf "$OUT/new/$p.raw.txt"
  if cmp -s "$OUT/base/$p.txt" "$OUT/new/$p.txt" && cmp -s "$OUT/base/$p.raw.txt" "$OUT/new/$p.raw.txt"; then echo "== $p IDENTICAL"
  else
    python3 - "$OUT/base/$p.raw.txt" "$OUT/new/$p.raw.txt" "$p" <<'EOF'
import sys,re,difflib
a=open(sys.argv[1]).read().split('\n'); b=open(sys.argv[2]).read().split('\n'); bad=0
for op,i1,i2,j1,j2 in difflib.SequenceMatcher(None,a,b,autojunk=False).get_opcodes():
    if op!='equal' and re.sub(r'\d+','N',' '.join(a[i1:i2]))!=re.sub(r'\d+','N',' '.join(b[j1:j2])): bad+=1
print(f"== {sys.argv[3]} DIFFERS: {bad} non-numeric hunk(s)")
EOF
  fi
done
git clean -fdqX $N >/dev/null 2>&1 || true
python3 docs/orchestration/generate_manifest.py --committed-only > /dev/null && git add docs/orchestration/MANIFEST.tsv
echo "== staged: $(git diff --cached --shortstat)"
echo "== out: $OUT"
