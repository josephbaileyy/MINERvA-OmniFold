#!/bin/bash
# regenA A2 (AMENDMENT-A2.txt): projection-ratio readout. login02, plain Python, nice 19, 900 s timeouts. Writes only under $R2.
set -o pipefail
R=/pscratch/sd/j/josephrb/ibuchi-evloop-20261123/regenA; R2=/pscratch/sd/j/josephrb/ibuchi-evloop-20261123/regenA2
OLDC=903fb78b941a2f889bfcc5092e41ce27f5add898; NEWC=e766ee5290de9dfc81b490b6165565daee6fa8d5
ANC=/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/minerva_paper_anc
E=/pscratch/sd/j/josephrb/ibuchi-evloop-20261123/tier1/units_e/er.root; OLDIN=$R/stage/er_old.root
echo "[A2] start $(date -u +%FT%TZ) host $(hostname)"
for p in $R2/repo_903 $R2/out; do [ ! -e $p ] || { echo "REFUSED: $p exists"; exit 2; }; done
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git $R2/repo_903 && git -C $R2/repo_903 -c advice.detachedHead=false checkout -q $OLDC
[ "$(git -C $R2/repo_903 rev-parse HEAD)" = $OLDC ] && [ "$(git -C $R/repo rev-parse HEAD)" = $NEWC ] || { echo "REFUSED: heads"; exit 2; }
echo "[A2] C-CLONE before: 903 $(git -C $R2/repo_903 status --porcelain --ignored | wc -l)  e766 $(git -C $R/repo status --porcelain --ignored | wc -l)"
mkdir -p $R2/out
echo "[A2] C-PINS before:"; sha256sum $OLDIN $E $ANC/cov_ptpl_minerva_inclusive_6GeV.root $R2/projratio.py
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"; set +u; conda activate $HOME/.conda/envs/root_6_28
export MPLBACKEND=Agg PYTHONDONTWRITEBYTECODE=1
cd $R2/out
echo "[A2] OLD (903fb78b):"; timeout 900 nice -n 19 python3 $R2/projratio.py --module-dir $R2/repo_903/2d-unfolding --ours $OLDIN --paper $ANC/cov_ptpl_minerva_inclusive_6GeV.root --out $R2/out/old_projratio.json > $R2/out/old.log 2>&1; echo "rc=$?"; grep -v -E 'Warning|^$' $R2/out/old.log | tail -16
echo "[A2] E (e766ee52):"; timeout 900 nice -n 19 python3 $R2/projratio.py --module-dir $R/repo/2d-unfolding --ours $E --paper $ANC/cov_ptpl_minerva_inclusive_6GeV.root --out $R2/out/e_projratio.json > $R2/out/e.log 2>&1; echo "rc=$?"; grep -v -E 'Warning|^$' $R2/out/e.log | tail -16
echo "[A2] C-PINS after:"; sha256sum $OLDIN $E $ANC/cov_ptpl_minerva_inclusive_6GeV.root
echo "[A2] C-CLONE after: 903 $(git -C $R2/repo_903 status --porcelain --ignored | wc -l)  e766 $(git -C $R/repo status --porcelain --ignored | wc -l)"
sha256sum $R2/out/*; echo "[A2] end $(date -u +%FT%TZ)"
