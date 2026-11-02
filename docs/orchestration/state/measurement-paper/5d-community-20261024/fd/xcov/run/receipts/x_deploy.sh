#!/bin/bash
# GENCMP X: deploy at M (binding ruling 5), verify the six bound blobs, run the bound tests. Writes only under $R.
R=/pscratch/sd/j/josephrb/gencmp-x-20261102
M=260e299b37e2a82deaeef165b79d0757115e8887
[ -e "$R" ] && { echo "STOP: $R exists"; exit 2; }
mkdir -p "$R"/{receipts,logs,tmp} || exit 2
{ hostname; date -u +%FT%TZ; } > "$R/receipts/deploy-host.txt"
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$R/deploy" > "$R/logs/clone.log" 2>&1 || { echo clone failed; exit 3; }
cd "$R/deploy" && git -c advice.detachedHead=false checkout -q --detach "$M" || exit 3
[ "$(git rev-parse HEAD)" = "$M" ] || { echo "HEAD not M"; exit 9; }
[ -z "$(git status --porcelain)" ] || { echo "porcelain not empty"; exit 9; }
bad=0
while read -r h p; do g=$(git rev-parse "$M:$p"); echo "$g $p"; [ "$g" = "$h" ] || bad=1; done < /dev/shm/x_want.txt > "$R/receipts/deploy-blobs.txt"; cp /dev/shm/x_want.txt "$R/receipts/want-blobs.txt"
cat "$R/receipts/deploy-blobs.txt" | cut -c1-12
[ $bad = 0 ] || { echo "STOP: a blob differs"; exit 9; }
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
cd nd-unfolding/tests
for e in omnifold_py310 root_6_28; do
  conda activate "$HOME/.conda/envs/$e"
  TMPDIR=$R/tmp env -u PYTHONPATH python -B -m unittest test_fd_xcov > "$R/logs/tests-$e.log" 2>&1
  echo "$e rc=$? $(grep -E '^Ran|^OK|^FAILED' "$R/logs/tests-$e.log" | tr '\n' ' ')"
done
cd "$R/deploy" && [ -z "$(git status --porcelain)" ] && echo "porcelain after: empty"
echo "deploy ok at $M"
