#!/usr/bin/env bash
# Regenerate every output in this directory from the saved inputs (local, no cluster).
set -euo pipefail
cd "$(dirname "$0")"
py="${PYTHON:-python3}"
export OPENBLAS_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
rm -f .events-cache.pkl
"$py" sectionc.py > sectionc.txt
"$py" evis_by_pz.py > evis-by-pz.txt
"$py" -u test1.py test1.json > test1.txt
"$py" summary.py > summary.txt
"$py" corrections.py > corrections.txt
rm -f .events-cache.pkl
"$py" --version > versions.txt
"$py" -c "import numpy, pandas, scipy; print('numpy', numpy.__version__, 'pandas', pandas.__version__, 'scipy', scipy.__version__)" >> versions.txt
