#!/bin/bash
# RDX c2 pin-lookup probe (the director's go, 2026-11-16): read-only; -B writes no .pyc; writes nothing on the cluster.
# 1. /usr/bin/python3 -V   2. connect line 192's import under SYSPY (expected SyntaxError)   3. the same under CHKPY
D=/pscratch/sd/j/josephrb/rdx-20261112b/deploy
SYSPY=/usr/bin/python3
CHKPY=/global/homes/j/josephrb/.conda/envs/omnifold_py310/bin/python
echo "node $(hostname) $(date -u +%FT%TZ)"
echo "deploy HEAD $(git -C "$D" rev-parse HEAD) porcelain $(git -C "$D" status --porcelain --untracked-files=all | wc -l)"
echo "fd_ct_period_inputs.py sha256 $(sha256sum "$D/nd-unfolding/fd_ct_period_inputs.py" | cut -d' ' -f1)"
echo "== 1. $SYSPY -V"
$SYSPY -V 2>&1; echo "rc=$?"
pl=1A
echo "== 2. line 192 under SYSPY"
$SYSPY -I -B -c "import sys; sys.path.insert(0, sys.argv[1]); import fd_ct_period_inputs as C; print(C.ZERO_LOOPS[sys.argv[2]])" "$D/nd-unfolding" "$pl" 2>&1; echo "rc=$?"
echo "== 3. line 192 under CHKPY"
$CHKPY -I -B -c "import sys; sys.path.insert(0, sys.argv[1]); import fd_ct_period_inputs as C; print(C.ZERO_LOOPS[sys.argv[2]])" "$D/nd-unfolding" "$pl" 2>&1; echo "rc=$?"
echo "deploy porcelain after $(git -C "$D" status --porcelain --untracked-files=all | wc -l)"
