#!/bin/bash
# OOFVC: build the deploy tree at M = 77d76cfc (OOFVC-DECLARATION.md sections 1.3 and 2.1).
#   bash make_tree.sh DEST archive REPO STAGING_ROOT   local: git archive of M's three paths from REPO (tests)
#   bash make_tree.sh DEST clone   URL  STAGING_ROOT   cluster: a fresh clone checked out at M, clean
# Then, and only then:
#   1. Tier 1's edge edit on re2_driver.py:44 (tier1/prepare.sh), which must give 677ac75f;
#   2. oofvc_driver.diff, which must give the pinned OOFVC driver;
#   3. ref_c2c1/config.json re-pinned to that driver and pointed at STAGING_ROOT.
# Every resulting sha is printed, and any mismatch is a refusal. DEST must not exist.
set -euo pipefail
DEST=${1:?dest}; MODE=${2:?archive|clone}; SRC=${3:?repo or url}; STAGE=${4:?staging root}
M=77d76cfc2d621f8faa010b75006811868494652a
EDGES_SHA=677ac75f1d171ca7d71223f62bf3426f056e41b1b6cc8bfd433d49528a1371e8
OOFVC_SHA=dade280b395a0c899601c08736baf0af6f49a1314b5eb77f9ba55f9f2f3cb703
RUNNER_SHA=285dd138363d090a4ce5dea3361be81fada8680bd782b918e9d95198d1b5d6ea
HERE=$(cd "$(dirname "$0")" && pwd)
PY=${OOFVC_PY:-python3}
sha() { "$PY" -c 'import hashlib,sys; print(hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest())' "$1"; }
[ ! -e "$DEST" ] || { echo "REFUSED: $DEST exists"; exit 2; }
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
"$PY" - "$D" <<'EOF'
import sys
p = sys.argv[1]; lines = open(p).read().split("\n")
old = "PT_EDGES = [0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55,"
if lines[43] != old:
    sys.exit("REFUSED: re2_driver.py:44 is not the OLD pT edge line")
lines[43] = "PT_EDGES = [0, 0.075, 0.15, 0.25, 0.325, 0.40, 0.475, 0.55,"
open(p, "w").write("\n".join(lines))
EOF
[ "$(sha "$D")" = "$EDGES_SHA" ] || { echo "REFUSED: the edge edit does not give 677ac75f"; exit 3; }
(cd "$DEST" && git apply "$HERE/oofvc_driver.diff")
[ "$(sha "$D")" = "$OOFVC_SHA" ] || { echo "REFUSED: oofvc_driver.diff does not give the pinned driver"; exit 3; }
"$PY" - "$C" "$OOFVC_SHA" "$STAGE" <<'EOF'
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
for f in "$D" "$C" "$DEST/2d-unfolding/ref_c2c1/ref_c2c1.py" "$DEST/unbinned_unfolding/python/omnifold.py" \
         "$DEST/2d-unfolding/compare_to_paper_fullcov.py" "$DEST/nd-unfolding/s5c_unfold.py"; do
  echo "$(sha "$f")  ${f#$DEST/}"
done
