#!/bin/bash
# MP1-A partial S2 (DESCRIPTIVE; post hoc; proton + meson only). Login node. The S2/S3 code test's commands, with a
# control evaluate of the unmodified frozen design first.
set -o pipefail   # NOT set -u
NS=/pscratch/sd/j/josephrb/measurement-paper/phase1/mp1/s1; T=$NS/tools-v3; MP1=$T/measurement-paper/phase1/mp1
P=/pscratch/sd/j/josephrb/measurement-paper/phase1/mp1/partial; C=$P/run; mkdir -p $C
D=/pscratch/sd/j/josephrb/w2-recoil-20261006/deploy/e9372b75; S5P=/pscratch/sd/j/josephrb/s5p-20260926
FROZEN=$D/docs/orchestration/state/s5p/prod/design.json
(cd $T && sha256sum --quiet -c TOOLS.sha256) || { echo "ABORT tools-v3"; exit 2; }
(cd $P/tools && sha256sum --quiet -c TOOLS.sha256) || { echo "ABORT partial tools"; exit 2; }
[ "$(sha256sum < $FROZEN | cut -d' ' -f1)" = 404446eb2a770dc4412012c5e182e57a77afa2edd332c75de399a9281f536285 ] || { echo "ABORT design"; exit 2; }
[ "$(sha256sum < $P/tools/joint-evaluate-A7.json | cut -d' ' -f1)" = b9604502b1aa263508ba46f0be91846d7a2106f6f2fd0ba5c172b87ee256dd11 ] || { echo "ABORT A7 evaluate"; exit 2; }
cd $D && source ./setup_salloc_env.sh >/dev/null 2>&1; export PYTHONDONTWRITEBYTECODE=1
date -u
PYTHONPATH=$D/nd-unfolding:$MP1 python3 $P/tools/mp1_s2_partial.py design --ns $NS --frozen $FROZEN --out $C/design-mp1-partial_pm.json > $C/design.stdout 2>&1; echo "design rc=$?"
t0=$(date +%s); PYTHONPATH=$D/nd-unfolding python3 $MP1/s5p_joint_mp1.py evaluate --design $FROZEN --v $S5P/stage3/V/V-s3v.npz --out $C/control-evaluate.json > $C/control.stdout 2>&1; echo "control rc=$? $(( $(date +%s)-t0 ))s"
t0=$(date +%s); PYTHONPATH=$D/nd-unfolding python3 $MP1/s5p_joint_mp1.py evaluate --design $C/design-mp1-partial_pm.json --v $S5P/stage3/V/V-s3v.npz --out $C/joint-evaluate.json > $C/joint.stdout 2>&1; echo "joint rc=$? $(( $(date +%s)-t0 ))s"
t0=$(date +%s); PYTHONPATH=$D/nd-unfolding python3 $D/nd-unfolding/s5p_robust_labels.py --evaluate $C/joint-evaluate.json --design $C/design-mp1-partial_pm.json --out $C/robust-labels.json > $C/labels.stdout 2>&1; echo "labels rc=$? $(( $(date +%s)-t0 ))s"
cp $T/docs/orchestration/state/s5c/contract.json $C/s5c_contract.json
t0=$(date +%s); cd $C && PYTHONPATH=$T/nd-unfolding python3 $MP1/s5p_recompute_mp1.py evaluate --design $C/design-mp1-partial_pm.json --v $S5P/stage3/V/V-s3v.npz --s5c-contract s5c_contract.json --no-sequential --out $C/recompute.json > $C/recompute.stdout 2>&1; echo "recompute rc=$? $(( $(date +%s)-t0 ))s"
PYTHONPATH=$T/nd-unfolding python3 $MP1/s5p_recompute_mp1.py compare --mine $C/recompute.json --production $C/joint-evaluate.json --robust-labels $C/robust-labels.json --out $C/recompute-compare.json > $C/recompute-compare.stdout 2>&1; echo "recompute-compare rc=$?"
python3 -c "import json;c=json.load(open('$C/recompute-compare.json'));print('recompute compare',c['verdict'],c['agree'],'/',c['items'],'discrepancies',len(c['discrepancies']))"
cd $D && PYTHONPATH=$D/nd-unfolding:$MP1 python3 $P/tools/mp1_s2_partial.py compare --frozen-evaluate $P/tools/joint-evaluate-A7.json --control $C/control-evaluate.json --partial $C/joint-evaluate.json --out $C/partial-vs-A7.json > $C/compare.stdout 2>&1; echo "compare rc=$?"
cat $C/compare.stdout
date -u
