#!/bin/bash
# Login-node watcher for the PET final-design study: keeps the study's two 4-hour gpu_interactive
# allocations and two gpu_debug chains working on the highest-priority INCOMPLETE manifests, until
# STOP_UTC or the file $B/keep_busy.stop exists. It only submits jobs through the study launcher
# (pfd_worker_chain.sh, pinned clean checkout, guarded runs); it never cancels anything.
#   usage: nohup bash keep_busy.sh <pinned checkout> <commit> <stop, e.g. 2026-09-27T20:00Z> &
# Priorities (first incomplete wins; Amendment 3b: the N2 repair arm dev3N/s3n_* goes ahead of the
# final-bank rows, whose compact finalist may be re-frozen):
#   (interactive lanes are per GPU: each GPU runs its list in order, skipping complete stems)
#   interactive 1 : dev2Pa (PET2, 1 run/GPU) -> dev2Q (PET2, annealed step 1) -> s3n_slow -> s4s -> s4f
#   interactive 2 : GPUs 0-1 dev2Ta -> s3n_slow -> dev2Q (PET2, 1 run/GPU) -> s4s ; GPUs 2-3 dev3N ->
#                   s3n_fast -> s4f -> s4s   (2 runs/GPU)
#   debug chains  : dev3N -> s3n_fast -> s4f -> s4s   (one 24-epoch truth-step iteration per 30-min round)
# Final-bank manifests run with SCORE=0 (the launcher also forces it before an UNBLIND amendment).
set -u
M=$1; S=$2; STOP=$3
B=/pscratch/sd/j/josephrb/pet-final-design-20260925
R=../../final_design/runs
declare -A OUTS=([dev2Pa]=dev2P [dev2Q]=dev2Q [dev2Ta]=dev2T [s3p_all]=s3p [s4f_a2]=s4f [s4s_a2]=s4s
                 [dev3N]=dev3N [s3n_fast]=s3p [s3n_slow]=s3p)
declare -A ITER=([dev3N]=1500 [s3n_fast]=1500 [s3n_slow]=2900 [s4f_a2]=780 [s4s_a2]=780 [s3p_all]=780)
stop_epoch=$(date -d "$STOP" +%s)

incomplete() {   # MANIFEST_STEM -> 0 if some row of the manifest is not COMPLETE
  local stem=$1 out=$B/${OUTS[$1]} n
  while IFS=$'\t' read -r n _; do
    [[ -z "$n" || "$n" == \#* ]] && continue
    [[ "$(cat "$out/$n/status.txt" 2>/dev/null)" == COMPLETE ]] || return 0
  done < "$M/nd-unfolding/pet/final_design/runs/$stem.tsv"
  return 1
}
first_incomplete() { local s; for s in "$@"; do incomplete "$s" && { echo "$s"; return 0; }; done; return 1; }
# per-GPU lanes: each GPU walks its own priority list (rows are claimed per row, so lanes on the same
# manifest never collide), so a GPU whose manifest runs out moves on instead of idling until the
# allocation ends; PET2 stems run 1 worker per GPU (33 GB), the others 2
declare -A IT2=([dev2Pa]=2200 [dev2Q]=2200 [dev2Ta]=2900 [s3n_slow]=2900 [dev3N]=2000 [s3n_fast]=2000
                [s3p_all]=1300 [s4f_a2]=1300 [s4s_a2]=1300)
lane_seq() {   # GPU STEM... -> "( worker on STEM1 ; worker on STEM2 ; ... )" over the incomplete stems
  local g=$1; shift; local cmd="" st k sc
  for st in "$@"; do
    incomplete "$st" || continue
    k=2; [[ $st == dev2Pa || $st == dev2Q ]] && k=1
    sc=""; [[ $st == s4* ]] && sc="SCORE=0 "
    cmd+="CUDA_VISIBLE_DEVICES=$g OUT=$B/${OUTS[$st]} MANIFEST=$R/$st.tsv ${sc}SLOTS_PER_GPU=$k CHAIN=0 ITER_ESTIMATE=${IT2[$st]} bash $M/nd-unfolding/pet/final_design/jobs/pfd_worker_chain.sh; "
  done
  [[ -n "$cmd" ]] && echo "( $cmd) & "
}
INTER1=(dev2Pa dev2Q s3n_slow s4s_a2 s4f_a2)
INTER2_01=(dev2Ta s3n_slow dev2Q s4s_a2 s4f_a2)
INTER2_23=(dev3N s3n_fast s4f_a2 s4s_a2)
launch_inter() {   # NAME "lane1 & lane2 & ..." LOGDIR
  local name=$1 cmd=$2 log=$3
  mkdir -p "$log"
  ( cd "$log" && nohup srun -A m3246_g -q interactive -C gpu -N 1 --ntasks=1 -G 4 -c 128 -t 04:00:00 \
      -J "$name" --export=ALL,MINE="$M",MINE_COMMIT="$S" bash -c "$cmd wait" \
      > "$log/$name-$(date +%s).log" 2>&1 < /dev/null & )
  echo "$(date -u +%FT%TZ) $name: $cmd" >> "$B/keep_busy.log"
}
if [[ ${DRY:-0} == 1 ]]; then      # print the decisions and exit
  for st in dev2Pa dev2Q dev2Ta dev3N s3n_fast s3n_slow s4f_a2 s4s_a2; do incomplete "$st" && echo "$st incomplete" || echo "$st complete"; done
  echo "debug -> $(first_incomplete dev3N s3n_fast s4f_a2 s4s_a2)"
  echo "inter1 GPU0: $(lane_seq 0 "${INTER1[@]}")"; echo "inter2 GPU2: $(lane_seq 2 "${INTER2_23[@]}")"; exit 0
fi
while (( $(date +%s) < stop_epoch )) && [[ ! -e $B/keep_busy.stop ]]; do
  q=$(squeue --me -h -o '%j %q' 2>/dev/null) || { sleep 60; continue; }
  if ! grep -q '^pfd-inter1 ' <<<"$q"; then
    c=""; for g in 0 1 2 3; do c+="$(lane_seq $g "${INTER1[@]}")"; done
    [[ -n "$c" ]] && launch_inter pfd-inter1 "$c" "$B/dev2P"
  fi
  if ! grep -q '^pfd-inter2 ' <<<"$q"; then
    c=""; for g in 0 1; do c+="$(lane_seq $g "${INTER2_01[@]}")"; done
    for g in 2 3; do c+="$(lane_seq $g "${INTER2_23[@]}")"; done
    [[ -n "$c" ]] && launch_inter pfd-inter2 "$c" "$B/s4f"
  fi
  # a debug chain holds 2 submissions (running + queued successor); keep two chains (<= 4 of 5)
  nd=$(grep -c ' gpu_debug$' <<<"$q" || true)
  if (( nd <= 2 )); then
    st=$(first_incomplete dev3N s3n_fast s4f_a2 s4s_a2) && {
      O=$B/${OUTS[$st]}; mkdir -p "$O"; sc=1; [[ $st == s4* ]] && sc=0
      j=$(cd "$O" && sbatch --parsable -o "$O/slurm-%j.out" --export=ALL,MINE="$M",MINE_COMMIT="$S",OUT="$O",MANIFEST="$R/$st.tsv",SCORE=$sc,SLOTS_PER_GPU=1,CHAIN=1,MAX_ROUNDS=2000,DEADLINE_MARGIN=10,ITER_ESTIMATE=${ITER[$st]} "$M/nd-unfolding/pet/final_design/jobs/pfd_worker_chain.sh" 2>&1)
      echo "$(date -u +%FT%TZ) debug chain for $st: $j" >> "$B/keep_busy.log"; }
  fi
  sleep 120
done
echo "$(date -u +%FT%TZ) keep_busy stopped" >> "$B/keep_busy.log"
