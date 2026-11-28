#!/usr/bin/env bash
# Regenerate every output of tests A and B from the saved inputs (local, 0 node-hours).
set -euo pipefail
cd "$(dirname "$0")"
py="${PYTHON:-python3}"
export OPENBLAS_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
rm -f ../test1/.events-cache.pkl
"$py" -u test_a.py test-a.json > test-a.txt
"$py" -u test_b.py test-b.json > test-b.txt
"$py" scan.py > scan.txt
rm -f ../test1/.events-cache.pkl
"$py" -c "import sys, numpy, pandas, scipy; print(sys.version.split()[0], 'numpy', numpy.__version__, 'pandas', pandas.__version__, 'scipy', scipy.__version__)" > versions.txt
