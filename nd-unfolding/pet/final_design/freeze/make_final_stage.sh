#!/bin/bash
# Generate the final-stage manifests after the freeze (PROTOCOL-20260925 sections 7-9 and the
# "FB release" amendment). Pseudodata from the final bank FB; priors from DEV; paired seeds.
#   usage: make_final_stage.sh "<finalist ID:K> [...]" "<anchor ID:K> [...]" <n_F> <n_S> <tag>
#   e.g.   make_final_stage.sh "H2S1:5 L128S1:5" "CTLref:3 Cref:3" 30 8 v1
# Writes runs/s4f_<tag>.tsv (FINAL: E0-E3 cases, finalists + anchors, n_F draws),
#        runs/s4s_<tag>.tsv (final library, finalists only: E4/E5 at n_F draws, the rest at n_S).
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); STUDY=$(dirname "$HERE")
FIN=$1; ANC=$2; NF=$3; NS=$4; TAG=$5
G() { PYTHONDONTWRITEBYTECODE=1 python3 "$HERE/make_stage_manifests.py" "$@"; }
last=$((NF - 1)); lastS=$((NS - 1))
# FINAL (E0, E1, E2 from the development tilt; E3 from D1 -0.35)
# shellcheck disable=SC2086
G --stage S4F --bank FB --replicates 0-$last --candidates $FIN $ANC --cases dev D1_m0.350 \
  --manifest "$STUDY/runs/s4f_$TAG.tsv"
# final library at n_F draws for the designated topology/joint endpoints (E4, E5)
# shellcheck disable=SC2086
G --stage S4S --bank FB --replicates 0-$last --candidates $FIN --cases D4c_p_up D3_p0.35 \
  --manifest "$STUDY/runs/s4s_${TAG}_nf.tsv"
# the rest of the final library at n_S draws (PROTOCOL section 7, final library)
# shellcheck disable=SC2086
G --stage S4S --bank FB --replicates 0-$lastS --candidates $FIN --cases \
  null D1_p0.350 D2_bump_c0.3 D4d_n_up D5_nuwro R1_x1.05+D1_p0.350 \
  D1_m0.700 D1_p0.175 D2_bump_c1.0 D3_m0.35 D4a_pipm_up D4b_pi0_up D4c_p_down D4d_n_down \
  D5_gibuu D5p_nuwro D1_p0.350*D4c_p_up R1_x0.95+D1_p0.350 R2_x1.01+D1_p0.350 \
  --manifest "$STUDY/runs/s4s_${TAG}_ns.tsv"
(cat "$STUDY/runs/s4s_${TAG}_nf.tsv"; grep -v '^#' "$STUDY/runs/s4s_${TAG}_ns.tsv") \
  > "$STUDY/runs/s4s_$TAG.tsv"
rm "$STUDY/runs/s4s_${TAG}_nf.tsv" "$STUDY/runs/s4s_${TAG}_ns.tsv"
wc -l "$STUDY/runs/s4f_$TAG.tsv" "$STUDY/runs/s4s_$TAG.tsv"
