#!/bin/bash
# PILOT-FB code receipts at a committed head, in a clean clone: the tests and the mutation check under a venv with
# LightGBM 4.6.0 (the declared local tests, §8), the tests under the laptop python (LightGBM tests skipped there), and
# the job script's syntax.
S=/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a2dcbe62-b017-4025-a124-a6659ca362f5/scratchpad
C=$S/pfb-rcpt7/clone; O=$S/pfb-rcpt7/out; HEADSHA=${1:?head}; V=$S/pfb-venv/bin/python
mkdir -p "$O"
git clone -q --no-hardlinks /Users/josephbailey/tier3-wt "$C" || exit 2
git -C "$C" -c advice.detachedHead=false checkout -q "$HEADSHA" || exit 2
cd "$C" || exit 2
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
hdr() { echo "# HEAD $(git -C "$C" rev-parse HEAD)"; echo "# clean clone, $1, $(date -u +%FT%TZ)"
  (cd "$C/nd-unfolding" && shasum -a 256 fb_pilot_edges.py fb_pilot_gates.py fb_pilot_probe.py fb_pilot_analyze.py sbatch_pfb.sh pfb_smoke_prep.sh tests/test_fb_pilot.py tests/fb_pilot_mutation.py | sed 's/^/# /'); }
VV="$($V -c 'import sys, numpy, lightgbm, sklearn; print("Python %s, numpy %s, lightgbm %s, scikit-learn %s" % (sys.version.split()[0], numpy.__version__, lightgbm.__version__, sklearn.__version__))')"
{ hdr "$VV"; echo "# command: python -B -W ignore -m unittest -v nd-unfolding/tests/test_fb_pilot.py"
  "$V" -B -W ignore -m unittest -v nd-unfolding/tests/test_fb_pilot.py 2>&1; echo "# exit $?"; } > "$O/tests_lightgbm.txt"
{ hdr "$VV"; echo "# command: python -B nd-unfolding/tests/fb_pilot_mutation.py --jobs 6"
  "$V" -B nd-unfolding/tests/fb_pilot_mutation.py --jobs 6 2>&1; echo "# exit $?"; } > "$O/mutation.txt"
PYV="Python $(python3 -c 'import sys; print(sys.version.split()[0])'), numpy $(python3 -c 'import numpy; print(numpy.__version__)'), no lightgbm"
{ hdr "$PYV"; echo "# command: python3 -B -W ignore -m unittest -v nd-unfolding/tests/test_fb_pilot.py"
  python3 -B -W ignore -m unittest -v nd-unfolding/tests/test_fb_pilot.py 2>&1; echo "# exit $?"; } > "$O/tests_laptop.txt"
{ hdr "bash $(bash --version | head -1)"; echo "# command: bash -n nd-unfolding/sbatch_pfb.sh && bash -n nd-unfolding/pfb_smoke_prep.sh"
  bash -n nd-unfolding/sbatch_pfb.sh && bash -n nd-unfolding/pfb_smoke_prep.sh 2>&1; echo "# exit $?"
  echo "# clone status: $(git status --porcelain --untracked-files=all | wc -l | tr -d ' ') lines"; } > "$O/syntax.txt"
echo done
