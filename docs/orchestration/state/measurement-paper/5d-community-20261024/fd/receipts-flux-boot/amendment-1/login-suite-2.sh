# Amendment 1 (review round), constraint 3: the full declared suite and a B2 measurement on a Perlmutter login node (root_6_28,
# the cluster BLAS), in a scratch clone at the amendment head outside both $B roots; removed afterwards.
P=/pscratch/sd/j/josephrb
HEAD=a7b288ea51df2d4be7f1dfe7b0cc2453c070f4a7
S=$P/scratch-3d-amend-$(date -u +%Y%m%dT%H%M%SZ)
if [ -e "$S" ]; then echo "STOP: $S exists"; exit 3; fi
PYB="env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3"
echo "start $(date -u +%FT%TZ) $(hostname) $S"
mkdir -p $S/tmp && git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold $S/repo && git -C $S/repo checkout --quiet --detach $HEAD
git -C $S/repo rev-parse HEAD; echo "porcelain_ignored_lines $(git -C $S/repo status --porcelain --ignored | wc -l)"
cd $S/repo && sha256sum nd-unfolding/fd_flux_boot.py nd-unfolding/tests/test_fd_flux_boot.py
$PYB -I -B -c "import numpy as np; c=np.show_config(mode='dicts'); print('numpy', np.__version__, 'blas', c['Build Dependencies']['blas']['name'], c['Build Dependencies']['blas'].get('version'), 'lapack', c['Build Dependencies']['lapack']['name'])"
for f in libblas.so.3 libcblas.so.3 liblapack.so.3; do echo "$f -> $(readlink -f $HOME/.conda/envs/root_6_28/lib/$f)"; done
cd $S/repo/nd-unfolding/tests && TMPDIR=$S/tmp $PYB -B -m unittest test_fd_flux_boot test_fd_g_followup test_fd_g_diag \
  test_fd_g_compare test_s1_assemble test_s1_scripts_isolated > $S/suite.log 2>&1; echo "tests rc=$?"
grep -E "^Ran |^OK|^FAILED|^FAIL:|^ERROR:" $S/suite.log
cat > $S/b2.py <<'PY'
import sys, json, tempfile
from pathlib import Path
from unittest import mock
sys.path.insert(1, "."); sys.path.insert(1, "..")
import test_fd_flux_boot as T, fd_flux_boot as FB, s1_assemble as sa
d = Path(tempfile.mkdtemp())
tree = T.BootTree(d / "t").write()
with mock.patch.object(sa, "CONSTRAINT_SHA256", tree.bpins["constraint"]):
    FB.run(FB.build_args(tree.bargv), tree.bpins, tree.predictions)
out = json.loads((tree.out / "boot.json").read_text())
print("B2 identity relative_difference", {k: v["relative_difference"] for k, v in out["identity"].items()})
PY
TMPDIR=$S/tmp $PYB -B $S/b2.py 2>&1 | grep -E "control B1|control B2|control B6|B2 identity"
echo "porcelain_ignored_lines_after $(git -C $S/repo status --porcelain --ignored | wc -l)"
echo "===== suite.log ====="; cat $S/suite.log
cd $P && rm -rf "$S" && echo "removed $S: $([ -e "$S" ] && echo still-there || echo gone)"
echo "end $(date -u +%FT%TZ)"
