#!/bin/bash
# Generate coverage-stage manifests (PROTOCOL-20260925 section 9 as amended; stage S5) for one frozen
# finalist at its exact configuration: B = 6 bootstrap members per replicate, pseudodata from FB and
# prior from DEV (bank draws BANK:FB:S5:<r>, shared by every finalist -> paired replicates).
#   usage: make_coverage_stage.sh <ID:K> <tag> [dev replicates, default 0-119] [D4c replicates, default 0-59]
#   e.g.   make_coverage_stage.sh H2S1:5 a3            (look 1: N_cov = 120, D4c 60)
#          make_coverage_stage.sh H2S1:5 a3L2 120-239 60-119   (look 2 extension)
# Writes runs/s5c_<tag>_<ID>.tsv (development tilt, C1-C4) and runs/s5d_<tag>_<ID>.tsv (D4c up, C5).
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); STUDY=$(dirname "$HERE")
CK=$1; TAG=$2; RDEV=${3:-0-119}; RD4C=${4:-0-59}; ID=${CK%%:*}
G() { PYTHONDONTWRITEBYTECODE=1 python3 "$HERE/make_stage_manifests.py" "$@"; }
G --stage S5 --bank FB --replicates "$RDEV" --candidates "$CK" --cases dev --bootstrap-members 1-6 \
  --manifest "$STUDY/runs/s5c_${TAG}_$ID.tsv"
G --stage S5 --bank FB --replicates "$RD4C" --candidates "$CK" --cases D4c_p_up --bootstrap-members 1-6 \
  --manifest "$STUDY/runs/s5d_${TAG}_$ID.tsv"
