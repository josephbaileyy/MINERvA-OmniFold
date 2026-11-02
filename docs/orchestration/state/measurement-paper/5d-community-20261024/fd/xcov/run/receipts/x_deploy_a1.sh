#!/bin/bash
# GENCMP X addendum X-A1 (binding #672 ruling 1): a fresh clone at M' into $R/deploy-a1, the bound blobs verified, the
# bound tests run in both environments. Writes only under $R.
R=/pscratch/sd/j/josephrb/gencmp-x-20261102
M=f14119b11ccd151f910163455e575196be38b96a
[ -d "$R" ] || { echo "STOP: $R missing"; exit 2; }
[ -e "$R/deploy-a1" ] && { echo "STOP: $R/deploy-a1 exists"; exit 2; }
[ -e "$R/v0-a1" ] && { echo "STOP: $R/v0-a1 exists"; exit 2; }
{ hostname; date -u +%FT%TZ; } > "$R/receipts/deploy-a1-host.txt"
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$R/deploy-a1" > "$R/logs/clone-a1.log" 2>&1 || { echo clone failed; exit 3; }
cd "$R/deploy-a1" && git -c advice.detachedHead=false checkout -q --detach "$M" || exit 3
[ "$(git rev-parse HEAD)" = "$M" ] || { echo "HEAD not M'"; exit 9; }
[ -z "$(git status --porcelain)" ] || { echo "porcelain not empty"; exit 9; }
bad=0
while read -r h p; do g=$(git rev-parse "$M:$p"); echo "$g $p"; [ "$g" = "$h" ] || bad=1; done < /dev/shm/xa1_want.txt > "$R/receipts/deploy-a1-blobs.txt"; cp /dev/shm/xa1_want.txt "$R/receipts/want-a1-blobs.txt"
cut -c1-12 "$R/receipts/deploy-a1-blobs.txt"
[ $bad = 0 ] || { echo "STOP: a blob differs"; exit 9; }
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
cd nd-unfolding/tests
for e in omnifold_py310 root_6_28; do
  conda activate "$HOME/.conda/envs/$e"
  TMPDIR=$R/tmp env -u PYTHONPATH python -B -m unittest test_fd_xcov > "$R/logs/tests-a1-$e.log" 2>&1
  echo "$e rc=$? $(grep -E '^Ran|^OK|^FAILED' "$R/logs/tests-a1-$e.log" | tr '\n' ' ')"
done
cd "$R/deploy-a1" && [ -z "$(git status --porcelain)" ] && echo "porcelain after: empty"
echo "deploy-a1 ok at $M"
