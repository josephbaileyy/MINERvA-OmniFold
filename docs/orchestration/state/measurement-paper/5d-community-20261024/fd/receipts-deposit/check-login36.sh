# Read-only check of the deposit candidate on a login node, in Stage G's environment (0 node-h). The directory
# /pscratch/sd/j/josephrb/fd-deposit-check-20261028/v5 holds only copies of committed files (hashed below) and the check's output; it needs no retention.
cd /pscratch/sd/j/josephrb/fd-deposit-check-20261028/v5; echo "start $(date -u +%FT%TZ) $(hostname)"
sha256sum fd_data_product.json fd_g_readout.json nd/*.py pkg/*
PY="env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I -B"
$PY -c "import numpy, sys; print('python', sys.version.split()[0], 'numpy', numpy.__version__)"
$PY nd/fd_deposit_candidate.py check --package pkg --data-product fd_data_product.json --g-readout fd_g_readout.json > check2.out 2> check2.err
echo "check rc=$?"; cat check2.err; cat check2.out
mkdir pkg-m && cp pkg/cells.csv pkg/covariance.csv pkg/correlation.csv pkg/deposit.json pkg-m/ && echo "pkg-m holds: $(ls pkg-m | tr '\n' ' ')"
$PY nd/fd_deposit_candidate.py check --package pkg-m --data-product fd_data_product.json --measurement-only > check3.out 2> check3.err
echo "measurement-only check rc=$?"; cat check3.err; grep '"controls_passed"\|"mode"' -A7 check3.out; echo "end $(date -u +%FT%TZ)"
