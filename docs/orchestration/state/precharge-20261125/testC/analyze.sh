#!/usr/bin/env bash
# Regenerate every local test C output from committed inputs (0 node-hours).
# run.sh is the cluster task; this is the local analysis. controls.py runs once on the
# fetched outputs (python3 controls.py <dir>); its record is controls.json.
set -euo pipefail
cd "$(dirname "$0")"
py="${PYTHON:-python3}"
export OPENBLAS_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
rm -f ../test1/.events-cache.pkl
"$py" -u test_c.py --closure closure.json > closure.txt
if [[ -f controls.json ]] && "$py" -c "import json, sys; sys.exit(0 if json.load(open('controls.json'))['all_pass'] else 1)"; then
    "$py" -u test_c.py test-c.json > test-c.txt
else
    echo "controls.json absent or not all_pass: the declared test is not run" >&2
fi
rm -f ../test1/.events-cache.pkl
"$py" -c "import sys, numpy, pandas, scipy; print(sys.version.split()[0], 'numpy', numpy.__version__, 'pandas', pandas.__version__, 'scipy', scipy.__version__)" > versions.txt
