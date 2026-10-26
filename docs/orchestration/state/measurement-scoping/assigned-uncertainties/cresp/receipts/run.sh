set -eu
set -x
hostname; date -u +%FT%TZ
P=/pscratch/sd/j/josephrb; R=$P/cresp-20261026
test ! -e $R
git clone --filter=blob:none https://github.com/josephbaileyy/MINERvA-OmniFold $R/repo
git -C $R/repo checkout --detach 973142a7fc150f2ceb9fd3530297ec1ddcbd0dc3
test "$(git -C $R/repo rev-parse HEAD)" = 973142a7fc150f2ceb9fd3530297ec1ddcbd0dc3
test -z "$(git -C $R/repo status --porcelain --ignored)"
mkdir $R/out $R/tmp
cd $R/repo/nd-unfolding/tests
TMPDIR=$R/tmp env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -B -m unittest test_build_cresp test_s1_assemble
cd $R/out
TMPDIR=$R/tmp env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I -B $R/repo/nd-unfolding/build_cresp.py \
    --definition $R/repo/nd-unfolding/pv-ladder/readouts/h2_definition.json \
    --products-dir $P/measurement-paper/phase1/mp1/s1/unf \
    --s1-assembly $P/s1-20261024/s1_assembly.npz \
    --out $R/out/cresp.npz
test -z "$(git -C $R/repo status --porcelain --ignored)"
sha256sum $R/out/cresp.npz $R/out/cresp.json $R/repo/nd-unfolding/build_cresp.py $R/repo/nd-unfolding/tests/test_build_cresp.py $R/repo/nd-unfolding/s1_assemble.py $R/repo/nd-unfolding/s5p_stage1_inspect.py
ls -la $R $R/out $R/tmp
date -u +%FT%TZ
echo RUN-OK
