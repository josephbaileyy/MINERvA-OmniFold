#!/bin/bash
# Login-node watcher for the PET final-design study: keeps the study's two 4-hour gpu_interactive
# allocations and two gpu_debug chains working on the highest-priority INCOMPLETE manifests, until
# STOP_UTC or the file $B/keep_busy.stop exists. It only submits jobs through the study launcher
# (pfd_worker_chain.sh, pinned clean checkout, guarded runs); it never cancels anything.
#   usage: nohup bash keep_busy.sh <pinned checkout> <commit> <stop, e.g. 2026-09-27T20:00Z> &
# Priorities (first incomplete wins):
#   interactive 1 : dev2Pa (PET2, 1 run/GPU)  -> s4s -> s4f
#   interactive 2 : GPU0 dev2Ta -> s4s ; GPU1 s3p_all -> s4s ; GPUs 2-3 s4f -> s4s   (2 runs/GPU)
#   debug chains  : s4f -> s4s   (both fit a 30-min round at ~760 s/iteration)
# Final-bank manifests run with SCORE=0 (the launcher also forces it before an UNBLIND amendment).
set -u
M=$1; S=$2; STOP=$3
B=/pscratch/sd/j/josephrb/pet-final-design-20260925
R=../../final_design/runs
declare -A OUTS=([dev2Pa]=dev2P [dev2Ta]=dev2T [s3p_all]=s3p [s4f_a2]=s4f [s4s_a2]=s4s)
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
lane() {   # GPUS SLOTS STEM ITER -> one launcher command string
  local g=$1 k=$2 stem=$3 it=$4 sc=""
  [[ "$stem" == s4* ]] && sc="SCORE=0 "
  echo "CUDA_VISIBLE_DEVICES=$g OUT=$B/${OUTS[$stem]} MANIFEST=$R/$stem.tsv ${sc}SLOTS_PER_GPU=$k CHAIN=0 ITER_ESTIMATE=$it bash $M/nd-unfolding/pet/final_design/jobs/pfd_worker_chain.sh"
}
launch_inter() {   # NAME "lane1 & lane2 & ..." LOGDIR
  local name=$1 cmd=$2 log=$3
  mkdir -p "$log"
  ( cd "$log" && nohup srun -A m3246_g -q interactive -C gpu -N 1 --ntasks=1 -G 4 -c 128 -t 04:00:00 \
      -J "$name" --export=ALL,MINE="$M",MINE_COMMIT="$S" bash -c "$cmd wait" \
      > "$log/$name-$(date +%s).log" 2>&1 < /dev/null & )
  echo "$(date -u +%FT%TZ) $name: $cmd" >> "$B/keep_busy.log"
}
if [[ ${DRY:-0} == 1 ]]; then      # print the decisions and exit
  for st in dev2Pa dev2Ta s3p_all s4f_a2 s4s_a2; do incomplete "$st" && echo "$st incomplete" || echo "$st complete"; done
  echo "inter1 -> $(first_incomplete dev2Pa s4s_a2 s4f_a2)"; echo "debug -> $(first_incomplete s4f_a2 s4s_a2)"
  lane 2,3 2 s4f_a2 1300; exit 0
fi
while (( $(date +%s) < stop_epoch )) && [[ ! -e $B/keep_busy.stop ]]; do
  q=$(squeue --me -h -o '%j %q' 2>/dev/null) || { sleep 60; continue; }
  if ! grep -q '^pfd-inter1 ' <<<"$q"; then
    st=$(first_incomplete dev2Pa s4s_a2 s4f_a2) && {
      if [[ $st == dev2Pa ]]; then c="$(lane 0,1,2,3 1 dev2Pa 2200) & "
      else c="$(lane 0,1,2,3 2 "$st" 1300) & "; fi
      launch_inter pfd-inter1 "$c" "$B/${OUTS[$st]}"; }
  fi
  if ! grep -q '^pfd-inter2 ' <<<"$q"; then
    g0=$(first_incomplete dev2Ta s4s_a2 s4f_a2); g1=$(first_incomplete s3p_all s4s_a2 s4f_a2)
    g23=$(first_incomplete s4f_a2 s4s_a2)
    c=""
    [[ -n "$g0" ]] && c+="$(lane 0 2 "$g0" $([[ $g0 == dev2Ta ]] && echo 2800 || echo 1300)) & "
    [[ -n "$g1" ]] && c+="$(lane 1 2 "$g1" 1300) & "
    [[ -n "$g23" ]] && c+="$(lane 2,3 2 "$g23" 1300) & "
    [[ -n "$c" ]] && launch_inter pfd-inter2 "$c" "$B/s4f"
  fi
  # a debug chain holds 2 submissions (running + queued successor); keep two chains (<= 4 of 5)
  nd=$(grep -c ' gpu_debug$' <<<"$q" || true)
  if (( nd <= 2 )); then
    st=$(first_incomplete s4f_a2 s4s_a2) && {
      O=$B/${OUTS[$st]}; mkdir -p "$O"
      j=$(cd "$O" && sbatch --parsable -o "$O/slurm-%j.out" --export=ALL,MINE="$M",MINE_COMMIT="$S",OUT="$O",MANIFEST="$R/$st.tsv",SCORE=0,SLOTS_PER_GPU=1,CHAIN=1,MAX_ROUNDS=2000,DEADLINE_MARGIN=30,ITER_ESTIMATE=800 "$M/nd-unfolding/pet/final_design/jobs/pfd_worker_chain.sh" 2>&1)
      echo "$(date -u +%FT%TZ) debug chain for $st: $j" >> "$B/keep_busy.log"; }
  fi
  sleep 120
done
echo "$(date -u +%FT%TZ) keep_busy stopped" >> "$B/keep_busy.log"
