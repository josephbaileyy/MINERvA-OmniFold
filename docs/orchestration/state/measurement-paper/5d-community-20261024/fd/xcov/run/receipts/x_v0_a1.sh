#!/bin/bash
# GENCMP X addendum X-A1, V0-A1 on a login node in omnifold_py310 (binding #672 ruling 1): from $R/deploy-a1 at M',
# into $R/v0-a1/ (fd_xcov_steps.V0_DIR); $R/v0/ is not touched. Writes only under $R.
R=/pscratch/sd/j/josephrb/gencmp-x-20261102
M=f14119b11ccd151f910163455e575196be38b96a
cd "$R/deploy-a1" || exit 9
[ "$(git rev-parse HEAD)" = "$M" ] || { echo "HEAD not M'"; exit 9; }
[ -z "$(git status --porcelain)" ] || { echo "porcelain not empty"; exit 9; }
[ -e "$R/v0-a1" ] && { echo "STOP: $R/v0-a1 exists"; exit 2; }
sha256sum "$R/v0/v0.json" > "$R/receipts/v0-first-sha256-before-a1.txt"
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/omnifold_py310"
export TMPDIR=$R/tmp
date -u +%FT%TZ; hostname
/usr/bin/time -v env -u PYTHONPATH python -B nd-unfolding/fd_xcov.py v0 --run-dir "$R"
rc=$?; echo "rc=$rc"; date -u +%FT%TZ
sha256sum -c "$R/receipts/v0-first-sha256-before-a1.txt" && echo "first v0.json unchanged"
[ -z "$(git status --porcelain)" ] && echo "porcelain after: empty"
echo "end"
