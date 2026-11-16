#!/bin/bash
# Mutants of the xk code change: each replaces one line of fd_xcov_steps.py in a copy of nd-unfolding and runs the
# XkProducts tests there; each must show a failure.   bash run_xk_mutants.sh <wt>
WT=$1; T=$(mktemp -d "${TMPDIR:-/tmp}/xkm.XXXXXX"); PY=/Users/josephbailey/miniconda3/bin/python3
for m in 'G2R_OUT / f"A_{b}_{i}/xsec.root"|RE2 / f"partb/out/U_{b}_{i}/xsec.root"' \
         '"re2": {"q_r": Q_R,|"re2": {"q_r": ROUTE_A / "combination/s5_plus_playlist.npz",' \
         '"cr": CR_G2R,|"cr": CR,' \
         '"cmodel_r": CMODEL_R_G2R,|"cmodel_r": CMODEL_R,' \
         'if prod != "re2":|if True:'; do
  d=$(mktemp -d "$T/m.XXXX"); cp -R "$WT/nd-unfolding" "$d/"; mkdir -p "$d/docs"; ln -s "$WT/docs/orchestration" "$d/docs/orchestration"
  "$PY" - "$m" "$d/nd-unfolding/fd_xcov_steps.py" <<'PY'
import sys
a, b = sys.argv[1].split("|", 1); p = sys.argv[2]; s = open(p).read(); assert s.count(a) == 1, a; open(p, "w").write(s.replace(a, b))
PY
  out=$(cd "$d/nd-unfolding" && "$PY" -m pytest -q -p no:cacheprovider tests/test_fd_xcov.py -k XkProducts 2>&1 | tail -1)
  echo "MUTANT [$m] -> $out"
done
find "$T" -type l -delete; find "$T" -type f -exec rm -f {} +; find "$T" -depth -type d -exec rmdir {} \;
