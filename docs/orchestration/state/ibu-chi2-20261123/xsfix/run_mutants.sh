#!/usr/bin/env bash
# Apply each mutant in turn to the worktree, run the test class, restore. Reports KILLED / SURVIVED.
set -u
W=/Users/josephbailey/local-research/wt-ibu-chi2; S=$(dirname "$0")
PY=$HOME/cov2d-work/figenv/rootmpl3108/bin/python
export PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$S/../pytestlib
cd "$W" || exit 2
before=$(shasum -a 256 2d-unfolding/plot_2d_cross_section.py 2d-unfolding/uq/reported_cells.py 2d-unfolding/plot_2d_paper_comparison.py)
n=$(python3 -c "exec(open('$S/mutants.py').read()); print(len(M))")
for i in $(seq 0 $((n-1))); do
  label=$(python3 - "$i" "$S" <<'PY'
import sys; exec(open(sys.argv[2]+"/mutants.py").read()); f,o,nw,l=M[int(sys.argv[1])]
s=open(f).read(); assert s.count(o)==1, ("mutant anchor not unique", l); open(f+".mutbak","w").write(s); open(f,"w").write(s.replace(o,nw)); print(l)
PY
) || { echo "ANCHOR-FAIL $i"; exit 3; }
  "$PY" -m pytest 2d-unfolding/tests/test_published_axis_widths.py -q -x -p no:cacheprovider -k "CrossSectionPlotEdges" > "$S/mut_$i.log" 2>&1
  rc=$?
  for f in 2d-unfolding/plot_2d_cross_section.py 2d-unfolding/uq/reported_cells.py 2d-unfolding/plot_2d_paper_comparison.py; do [ -f "$f.mutbak" ] && mv "$f.mutbak" "$f"; done
  if [ $rc -ne 0 ]; then echo "KILLED   $label ($(grep -m1 -oE 'FAILED [^ ]+' "$S/mut_$i.log"))"; else echo "SURVIVED $label"; fi
done
after=$(shasum -a 256 2d-unfolding/plot_2d_cross_section.py 2d-unfolding/uq/reported_cells.py 2d-unfolding/plot_2d_paper_comparison.py)
[ "$before" = "$after" ] && echo "RESTORED: shas equal" || echo "RESTORE MISMATCH"
