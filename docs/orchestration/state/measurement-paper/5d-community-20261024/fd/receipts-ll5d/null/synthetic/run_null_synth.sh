#!/bin/bash
# Runs test_null_order.py once on a Perlmutter login node (synthetic files only; no LL5D path is read or written).
# stdin is ONE tar holding code/{nd-unfolding,2d-unfolding,<the clip dir>} (git archive of 4231b14d; r1 STOPped on
# an import of 2d-unfolding/uq/coverage_fixed_truth/score_coverage.py, absent from its nd-unfolding-only tar) and
# test_null_order.py; this script is passed as
# an argument, so nothing else shares stdin. From the Mac:
#   git -C <checkout> archive --prefix=code/ -o synth.tar 4231b14de5ea693e92cb31b1358a816b5c2f6625 nd-unfolding 2d-unfolding \
#     docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-cov2d/clip
#   tar -rf synth.tar test_null_order.py
#   ssh saul.nersc.gov "bash -c \"\$(echo $(base64 < run_null_synth.sh | tr -d '\n') | base64 -d)\"" < synth.tar
# It refuses if $R exists, unpacks the tar under $R, checks ll5d_b.py/fd_1b_inv.py/s5n_pseudo.py and the test against
# their sums, activates the shared MAT environment as the jobs do, and runs the test with its work dir $R/work (which
# the test creates and removes itself). $R/code and $R/test_null_order.py stay in place, named, for removal by the user.
P=/pscratch/sd/j/josephrb; R=$P/ll5d-null-synth-r2; A=$P/MINERvA-OmniFold
echo "host=$(hostname) utc=$(date -u +%FT%TZ)"
[ -e "$R" ] && { echo "STOP $R exists"; exit 2; }
mkdir -p "$R" || exit 2
tar -x -C "$R" || { echo "STOP unpack"; exit 2; }
(cd "$R" && sha256sum -c - <<'SUMS') || { echo "STOP the code or the test is not the package's"; exit 2; }
24312ca86f9e70ed86699772d634c19d9bcacb2bb87bff5aaa8c9f7c2661f3cb  code/nd-unfolding/ll5d_b.py
71b3903aa1329807af7e48b29b4ffd3336ad637d4b8c7e43ae0a6cbe28bcdf1f  code/nd-unfolding/fd_1b_inv.py
8981f97b96b418cfe46f1e940cb120f174053d7d3429f3b0b01a229c6c02ee6c  code/nd-unfolding/s5n_pseudo.py
a2852a510ebb4a398295ea10d72fbc2a49654af43eba1726326d2f3d1e33c052  test_null_order.py
SUMS
source "$A/setup_salloc_env.sh" > /dev/null 2>&1
echo "python=$(command -v python3) $(python3 -V 2>&1)"
cd "$R" && python3 -I -B "$R/test_null_order.py" "$R/code" "$R/work"; rc=$?
echo "test rc=$rc"
echo "left in place for removal by the user: $R/code and $R/test_null_order.py"
echo "end=$(date -u +%FT%TZ)"
exit $rc
