#!/bin/bash
# Run locally, only after the director's GO: create a fresh scratch directory on
# Perlmutter, copy the staged sources there and build. Submission is separate
# (DECLARATION.md, "Cluster request").
set -eo pipefail
cd "$(dirname "$0")"
host=perlmutter.nersc.gov
root=/pscratch/sd/j/josephrb/precharge-testC-20261126
shasum -a 256 -c staged.sha256
ssh "$host" "test ! -e $root && mkdir -p $root/logs"
scp measure.cpp truth.cpp build.sh run.sh batch.sh axes.txt staged.sha256 "$host:$root/"
ssh "$host" "cd $root && bash build.sh"
