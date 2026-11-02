#!/bin/bash
# GENCMP amendment E, step C-R (declaration section 5), on a login node in omnifold_py310 (director's ruling of
# 2026-11-01: root_6_28 has no uproot, which fd_gencmp.root_hist needs; a deviation from section 7 and ruling 1).
B=/pscratch/sd/j/josephrb/gencmp-e-20261101
M=6cd095d6773a45c8deef47d298245ea270a636ae
P=/pscratch/sd/j/josephrb
R=$P/2d-closeout-re2-20261023
FD=docs/orchestration/state/measurement-paper/5d-community-20261024
cd "$B/deploy" || exit 9
[ "$(git rev-parse HEAD)" = "$M" ] || { echo "HEAD not M"; exit 9; }
[ -z "$(git status --porcelain)" ] || { echo "porcelain not empty"; exit 9; }
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/omnifold_py310"
export TMPDIR=$B/tmp
mkdir -p "$B/c-r"
env -u PYTHONPATH python -B -c "import sys,numpy,uproot;print('python',sys.version.split()[0]);print('numpy',numpy.__version__);print('uproot',uproot.__version__);print('executable',sys.executable)" > "$B/c-r/environment.txt"
hostname >> "$B/c-r/environment.txt"; date -u +%FT%TZ >> "$B/c-r/environment.txt"
env -u PYTHONPATH python -B nd-unfolding/fd_gencmp.py overlap --arm refined \
  --inputs $FD/fd/gencmp/INPUTS.sha256 --inputs $FD/fd/gencmp-e/INPUTS.sha256 \
  --p5 $P/methods-paper/re1-20261022/out/5d/k1_p5_rerun.npz --mnvtune $P/s5p-20260926/gen5d/mnvtune_v1_xsec5d.npz \
  --cv2d $R/partb/out/ER/xsec.root --q2d $R/partc-r2/combination/s5_plus_playlist.npz \
  --playlist $R/partc-r2/playlist/playlist_term.npz \
  --cv3d $P/MINERvA-OmniFold/3d-unfolding/xsec_3d_MEFHC_5iter_lgbm.root \
  --proj3d $P/z2m-products/PROJ3D/cov_5d_to_ptpzeavail_from_adopted_trunk.root \
  --out "$B/c-r/overlap_refined.json"
echo "rc=$?"
[ -z "$(git status --porcelain)" ] && echo "porcelain after: empty"
date -u +%FT%TZ
