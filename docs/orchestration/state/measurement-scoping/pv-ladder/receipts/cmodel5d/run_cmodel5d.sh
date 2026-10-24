#!/bin/bash
# One run of the bound C_model,5D build (BUILD-BINDING.md). No retries.
R=/pscratch/sd/j/josephrb/cmodel5d-20261024
PIN=dfcbb2c6c1dcb3211b7c6c8c364a6c1f9f171a47
[ -e "$R" ] && { echo "[run] refusing: $R exists"; exit 2; }
mkdir -p "$R/logs" "$R/out"
LOG="$R/logs/deploy.log"
{
  date -u +"%Y-%m-%dT%H:%M:%SZ deploy start on $(hostname)"
  git clone --filter=blob:none https://github.com/josephbaileyy/MINERvA-OmniFold "$R/repo" 2>&1 | tail -3
  git -C "$R/repo" checkout --detach "$PIN" 2>&1 | tail -1
  head=$(git -C "$R/repo" rev-parse HEAD); echo "HEAD $head"
  st=$(git -C "$R/repo" status --porcelain); echo "status porcelain lines: $(printf '%s' "$st" | grep -c .)"
  sha256sum "$R/repo/nd-unfolding/pv-ladder/build_cmodel5d.py"
} > "$LOG" 2>&1
cat "$LOG"
[ "$(git -C "$R/repo" rev-parse HEAD)" = "$PIN" ] || { echo "[run] STOP: HEAD is not the pin"; exit 2; }
[ -z "$(git -C "$R/repo" status --porcelain)" ] || { echo "[run] STOP: deploy tree not clean"; exit 2; }
source /pscratch/sd/j/josephrb/MINERvA-OmniFold/setup_salloc_env.sh > "$R/logs/env.log" 2>&1
python -V
export PYTHONDONTWRITEBYTECODE=1
cd "$R/repo/nd-unfolding/pv-ladder" || exit 2
python - "$R/repo" > "$R/logs/modules.log" 2>&1 <<'PY'
import sys
from pathlib import Path
root = Path(sys.argv[1]).resolve()
sys.argv = sys.argv[:1]
import build_cmodel5d as B
bad = 0
for name, mod in (("build_cmodel5d", B), ("build_cmodel", B.B2), ("pv2d_lib", B.P), ("pvl_analyze", B.A),
                  ("pvl_lib", B.L), ("s5p_stage1_inspect", B.s1)):
    f = Path(mod.__file__).resolve()
    inside = root in f.parents
    bad += not inside
    print(f"{name}: {f} {'(inside deploy)' if inside else '(OUTSIDE DEPLOY)'}")
print("MODULES OK" if bad == 0 else "MODULES OUTSIDE DEPLOY")
sys.exit(0 if bad == 0 else 3)
PY
mrc=$?
cat "$R/logs/modules.log"
[ $mrc -eq 0 ] || { echo "[run] STOP: module resolution"; exit 3; }
python -W ignore -m unittest test_cmodel5d test_pvl > "$R/logs/tests.log" 2>&1
trc=$?
tail -4 "$R/logs/tests.log"
[ $trc -eq 0 ] || { echo "[run] STOP: tests failed (rc $trc)"; exit 4; }
/usr/bin/time -v python build_cmodel5d.py \
    --products /pscratch/sd/j/josephrb/pv-ladder-20261024/products \
    --p5 /pscratch/sd/j/josephrb/methods-paper/re1-20261022/out/5d/k1_p5_rerun.npz \
    --out-json "$R/out/cmodel_5d.json" \
    --out-npz "$R/out/cmodel_5d.npz" > "$R/logs/build.log" 2> "$R/logs/build.time"
brc=$?
echo "[run] build rc $brc"
cat "$R/logs/build.log"
grep -E "Elapsed|Maximum resident" "$R/logs/build.time"
[ $brc -eq 0 ] || sed -n 1,25p "$R/logs/build.time"
sha256sum "$R/out/"* 2>/dev/null
exit $brc
