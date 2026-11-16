#!/bin/bash
# V-HALF read (BINDING 1 rulings 2 and R1): local, 0 node-h, a fresh clone at main (after 28a59eed), empty porcelain
# before and after; v_half.py at 8a1cdbe7 as bound; one serial process, nice 19, thread caps 1, no bytecode.
set -o pipefail
W=$1; HEAD=$2; C=$W/clone; O=$W/out
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git $C && git -C $C -c advice.detachedHead=false checkout -q "$HEAD" || exit 3
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0
V=docs/orchestration/state/2d-closeout/valid-region-20261107/v-half
{
echo "V-HALF read: date_utc $(date -u +%FT%TZ) host $(hostname -s)"
echo "clone HEAD $(git -C $C rev-parse HEAD); 28a59eed an ancestor: $(git -C $C merge-base --is-ancestor 28a59eed3 HEAD && echo yes || echo NO)"
echo "porcelain --ignored lines before: $(git -C $C status --porcelain --ignored | wc -l | tr -d ' ')"
echo "python $(python3 -c 'import sys;print(sys.version.split()[0])') numpy $(python3 -c 'import numpy;print(numpy.__version__)'); threads 1; nice 19; PYTHONHASHSEED=0"
( cd $C && shasum -a 256 $V/DECLARATION.md $V/v_half.py $V/test_v_half.py $V/mutate_v_half.py $V/mutants.txt $V/INPUTS.sha256 $V/PRR-READOUT.sha256 nd-unfolding/pv-ladder/readouts/h2_definition.json docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-prr/read/cluster/readout.json docs/orchestration/state/measurement-paper/5d-community-20261024/fd/with-cpl/readout/fd_f0b_readout.json )
echo "INPUTS.sha256:"; cat $C/$V/INPUTS.sha256
echo "PRR-READOUT.sha256:"; cat $C/$V/PRR-READOUT.sha256
echo "command: nice -n 19 python3 -B v_half.py read --repo <clone> --out <out>"
echo "----"
( cd $W && nice -n 19 python3 -B $C/$V/v_half.py read --repo $C --out $O ); rc=$?
echo "----"
echo "rc=$rc"
ls -la $O 2>&1
( cd $O 2>/dev/null && shasum -a 256 * )
echo "porcelain --ignored lines after: $(git -C $C status --porcelain --ignored | wc -l | tr -d ' ')"
echo "date_utc $(date -u +%FT%TZ)"
} > $W/read.log 2>&1
