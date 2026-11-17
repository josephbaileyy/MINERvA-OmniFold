#!/bin/bash
# RDX stage-3 probe (for the director's go): read-only; -B writes no .pyc; writes nothing on the cluster.
# 1. which python3 a non-interactive ssh shell on the login node finds (the connect's, and by sbatch --export=ALL the job's)
# 2. sbatch_rdx_arms.sh:72's pin read, verbatim except stderr is shown instead of discarded
# 3. stage 3's state: the gate files, deploy3, and the frozen tune_v1.json against pv-ladder's prep-SHA256SUMS pin
B=/pscratch/sd/j/josephrb/rdx-20261112b; D=$B/deploy
echo "node $(hostname) $(date -u +%FT%TZ)"
echo "deploy HEAD $(git -C "$D" rev-parse HEAD) porcelain $(git -C "$D" status --porcelain --untracked-files=all | wc -l)"
echo "fd_ct_period_inputs.py sha256 $(sha256sum "$D/nd-unfolding/fd_ct_period_inputs.py" | cut -d' ' -f1)"
echo "== 1. python3 on PATH"
echo "PATH=$PATH"
p=$(command -v python3); echo "command -v python3: ${p:-none}"; [ -n "$p" ] && echo "resolves to $(readlink -f "$p")"
python3 -V 2>&1; echo "rc=$?"
echo "== 2. sbatch_rdx_arms.sh:72's read"
python3 -B -c "import sys; sys.path.insert(0, sys.argv[1]); import fd_ct_period_inputs as C; print(C.MP1_ZERO['lat_npz'], C.MP1_ZERO['lat_bkg'])" "${D}/nd-unfolding" 2>&1; echo "rc=$?"
echo "== 3. stage 3's state"
ls -l "$B/out/gates/" 2>&1
[ -e "$B/deploy3" ] && echo "deploy3 EXISTS" || echo "deploy3 absent"
T=/pscratch/sd/j/josephrb/pv-ladder-20261024/prep/ratios/L-5D-PV/tune_v1.json
stat -c '%s B mtime %y' "$T" 2>&1; echo "tune_v1.json sha256 $(sha256sum "$T" 2>&1 | cut -d' ' -f1) (pin 13bb1eae4ce0db4023bb29a5b98ca8b7e1e22288a1547f6a31a735fa1445435b)"
ls -l "$B/out/products" 2>&1 | head -3
echo "deploy porcelain after $(git -C "$D" status --porcelain --untracked-files=all | wc -l)"
