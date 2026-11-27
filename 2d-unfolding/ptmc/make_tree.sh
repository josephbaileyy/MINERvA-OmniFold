#!/bin/bash
# PTMC: build the deploy tree at M = 77d76cfc (PTMC-DECLARATION.md sections 1 and 2.5: M's grid, no edge patch).
#   bash make_tree.sh DEST archive REPO STAGING_ROOT   local: git archive of M's paths from REPO (tests)
#   bash make_tree.sh DEST clone   URL  STAGING_ROOT   cluster: a fresh clone checked out at M, clean
# Then, and only then:
#   1. oofvc_driver.diff (from this commit's 2d-unfolding/oofvc/), which must give OOFVC_ON_M;
#   2. ptmc_driver.diff, which must give the pinned PTMC driver;
#   3. ref_c2c1/config.json re-pinned to that driver and pointed at STAGING_ROOT;
#   4. oofvc_lib.py copied into the tree at its pin (the runner imports its global_index).
# Every resulting sha is printed, and any mismatch is a refusal. DEST must not exist.
set -euo pipefail
DEST=${1:?dest}; MODE=${2:?archive|clone}; SRC=${3:?repo or url}; STAGE=${4:?staging root}
M=77d76cfc2d621f8faa010b75006811868494652a
M_DRIVER_SHA=938c53c5a018d20f5b148f6bdc2949e987a60085c5d0b7913ccdd5bb438b5a3b
OOFVC_ON_M_SHA=3ee2172b0a9f6ed54d8e429b189a2af2ece0a0480aa16b8fc96994a4b2379b4f
PTMC_SHA=019230872d2c3232a458cc8e3ec7218cb1721ef5afc9842aa18fead888cf7d16
OOFVC_DIFF_SHA=6e836e057d4b8a8cfe14b67bb89164f939a444f3b5cfeeb86aaad8038006fce6
OOFVC_LIB_SHA=a3df5569b3adfea06f544ae574238ab0d56123add2eb8d31a41a5b56558cb2b8
RUNNER_SHA=285dd138363d090a4ce5dea3361be81fada8680bd782b918e9d95198d1b5d6ea
HERE=$(cd "$(dirname "$0")" && pwd)
OOFVC_DIR="$HERE/../oofvc"
PY=${PTMC_PY:-python3}
sha() { "$PY" -c 'import hashlib,sys; print(hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest())' "$1"; }
case "$PTMC_SHA" in *__*) echo "REFUSED: the PTMC driver pin is not filled in"; exit 2;; esac
[ ! -e "$DEST" ] || { echo "REFUSED: $DEST exists"; exit 2; }
[ "$(sha "$OOFVC_DIR/oofvc_driver.diff")" = "$OOFVC_DIFF_SHA" ] || { echo "REFUSED: oofvc_driver.diff is not 6e836e05"; exit 3; }
[ "$(sha "$OOFVC_DIR/oofvc_lib.py")" = "$OOFVC_LIB_SHA" ] || { echo "REFUSED: oofvc_lib.py is not a3df5569"; exit 3; }
case "$MODE" in
  archive)
    mkdir -p "$DEST"
    git -C "$SRC" archive "$M" 2d-unfolding unbinned_unfolding/python nd-unfolding/s5c_unfold.py technote_style.py \
      | tar -x -C "$DEST" ;;
  clone)
    git clone -q "$SRC" "$DEST"
    git -C "$DEST" -c advice.detachedHead=false checkout -q "$M"
    [ "$(git -C "$DEST" rev-parse HEAD)" = "$M" ] || { echo "REFUSED: HEAD is not M"; exit 2; }
    [ -z "$(git -C "$DEST" status --porcelain --ignored)" ] || { echo "REFUSED: the clone is not clean"; exit 2; } ;;
  *) echo "REFUSED: mode $MODE"; exit 2 ;;
esac
D="$DEST/2d-unfolding/re2/re2_driver.py"; C="$DEST/2d-unfolding/ref_c2c1/config.json"
[ "$(sha "$DEST/2d-unfolding/ref_c2c1/ref_c2c1.py")" = "$RUNNER_SHA" ] || { echo "REFUSED: ref_c2c1.py is not 285dd138"; exit 3; }
[ "$(sha "$D")" = "$M_DRIVER_SHA" ] || { echo "REFUSED: M's driver is not 938c53c5"; exit 3; }
(cd "$DEST" && git apply "$OOFVC_DIR/oofvc_driver.diff")
[ "$(sha "$D")" = "$OOFVC_ON_M_SHA" ] || { echo "REFUSED: oofvc_driver.diff on M does not give 3ee2172b"; exit 3; }
(cd "$DEST" && git apply "$HERE/ptmc_driver.diff")
[ "$(sha "$D")" = "$PTMC_SHA" ] || { echo "REFUSED: ptmc_driver.diff does not give the pinned PTMC driver"; exit 3; }
mkdir -p "$DEST/2d-unfolding/oofvc"
cp "$OOFVC_DIR/oofvc_lib.py" "$DEST/2d-unfolding/oofvc/oofvc_lib.py"
"$PY" - "$C" "$PTMC_SHA" "$STAGE" <<'EOF'
import json, sys
p, new, stage = sys.argv[1:]
text = open(p).read()
old_pin = '"2d-unfolding/re2/re2_driver.py": "938c53c5a018d20f5b148f6bdc2949e987a60085c5d0b7913ccdd5bb438b5a3b"'
old_root = '"root": "/pscratch/sd/j/josephrb/ref-c2c1-20261106/stage"'
if text.count(old_pin) != 1 or text.count(old_root) != 1:
    sys.exit("REFUSED: config.json does not carry M's driver pin and staging root once each")
text = text.replace(old_pin, f'"2d-unfolding/re2/re2_driver.py": "{new}"').replace(old_root, f'"root": "{stage}"')
json.loads(text)
open(p, "w").write(text)
EOF
echo "tree $DEST ($MODE at $M)"
for f in "$D" "$C" "$DEST/2d-unfolding/ref_c2c1/ref_c2c1.py" "$DEST/2d-unfolding/ref_c2c1/ref_c2c1_read.py" \
         "$DEST/unbinned_unfolding/python/omnifold.py" "$DEST/2d-unfolding/compare_to_paper_fullcov.py" \
         "$DEST/2d-unfolding/uq/reported_cells.py" "$DEST/2d-unfolding/oofvc/oofvc_lib.py"; do
  echo "$(sha "$f")  ${f#$DEST/}"
done
