#!/bin/bash
# Login node, no Slurm. Makes deploy_old and deploy_e under the lane root at M, applies only the declared edits,
# and prints every resulting sha and diff. Writes only under $R/tier1.
set -eo pipefail
R=/pscratch/sd/j/josephrb/ibuchi-evloop-20261123; T=$R/tier1; M=77d76cfc2d621f8faa010b75006811868494652a
for d in deploy_old deploy_e; do
  [ ! -e $T/$d ] || { echo "REFUSED: $T/$d exists"; exit 2; }
  git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git $T/$d
  git -C $T/$d -c advice.detachedHead=false checkout -q $M
  [ "$(git -C $T/$d rev-parse HEAD)" = $M ] || { echo "REFUSED: HEAD"; exit 2; }
  [ "$(git -C $T/$d status --porcelain --ignored | wc -l)" = 0 ] || { echo "REFUSED: not clean"; exit 2; }
  sed -i 's#"root": "/pscratch/sd/j/josephrb/ref-c2c1-20261106/stage"#"root": "/pscratch/sd/j/josephrb/ibuchi-evloop-20261123/tier1/stage"#' $T/$d/2d-unfolding/ref_c2c1/config.json
done
D=$T/deploy_e
sed -i '44s/^PT_EDGES = \[0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55,$/PT_EDGES = [0, 0.075, 0.15, 0.25, 0.325, 0.40, 0.475, 0.55,/' $D/2d-unfolding/re2/re2_driver.py
NEW=$(sha256sum $D/2d-unfolding/re2/re2_driver.py | cut -d' ' -f1)
sed -i "s#\"2d-unfolding/re2/re2_driver.py\": \"938c53c5a018d20f5b148f6bdc2949e987a60085c5d0b7913ccdd5bb438b5a3b\"#\"2d-unfolding/re2/re2_driver.py\": \"$NEW\"#" $D/2d-unfolding/ref_c2c1/config.json
for d in deploy_old deploy_e; do
  echo "== $d HEAD $(git -C $T/$d rev-parse HEAD)"; git -C $T/$d diff --stat; git -C $T/$d diff > $T/$d.diff
  sha256sum $T/$d.diff $T/$d/2d-unfolding/re2/re2_driver.py $T/$d/2d-unfolding/ref_c2c1/config.json $T/$d/2d-unfolding/ref_c2c1/ref_c2c1.py
done
