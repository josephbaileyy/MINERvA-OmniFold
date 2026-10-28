#!/bin/bash
#SBATCH --account=m3246
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
# F1b' (state/measurement-paper/5d-community-20261024/FD-F1-DECLARATION-AMENDMENT-1.md section 4): F1b's 128 gevgen
# tasks (64 per tune, 17,500 events, seeds 60001-60064 and 61001-61064), at most 14 at once (budget2.json's
# concurrency), each timed by /usr/bin/time -v and bounded by budget2.json's per-task timeout (3 x the re-pilot's
# full-task wall, so a stalled task becomes a STOP); a failed task exits 255, so xargs starts no further task; the NOWIDTH flux-check on all 128; hadd; gen5d_v3.py convert; then
# fd_f1_prep.py. Runs only if F1a''s budget2.json says GO, from a clean deploy at <pin>. Writes only under
# <OUT>/f1b2, refuses if that exists, and never reads F1b's <OUT>/f1b (the STOP's evidence).
# Submitted only by submit_fd_f1.sh f1b2, with --time from budget2.json (at most 0:57).
set -o pipefail   # NOT set -u
D="${1:?deploy}"; PIN="${2:?pin}"; OUT="${3:?out}"
head_sha=$(git -C "$D" rev-parse HEAD 2>/dev/null)
dirty=$(git -C "$D" status --porcelain --untracked-files=no 2>/dev/null | wc -l)
if [ "$head_sha" != "$PIN" ] || [ "$dirty" -ne 0 ]; then
    echo "[f1b2] refusing: deploy HEAD=$head_sha (pinned $PIN), $dirty modified tracked files" >&2; exit 2
fi
A="$OUT/f1a"; A2="$OUT/f1a2"; F="$OUT/f1b2"
grep -q '"decision": "GO"' "$A2/budget2.json" 2>/dev/null || { echo "[f1b2] refusing: F1a''s budget is not GO" >&2; exit 2; }
P=$(sed -n 's/.*"concurrency": \([0-9]*\).*/\1/p' "$A2/budget2.json")
[ "$P" = 14 ] || { echo "[f1b2] refusing: concurrency $P is not the declared 14" >&2; exit 2; }
TO=$(sed -n 's/.*"f1b2_task_timeout_s": \([0-9]*\).*/\1/p' "$A2/budget2.json")
[ -n "$TO" ] && [ "$TO" -gt 0 ] || { echo "[f1b2] refusing: no per-task timeout in budget2.json" >&2; exit 2; }
[ ! -e "$F" ] || { echo "[f1b2] refusing: $F exists" >&2; exit 2; }
G="$D/3d-unfolding/genie"
( cd "$A" && sha256sum -c "$A2/reused.sha256" ) > /dev/null 2>&1 || { echo "[f1b2] refusing: F1a's products changed" >&2; exit 2; }
declare -A BASE=([G18_10a_02_11b]=60000 [AR23_20i_00_000]=61000)
declare -A NAME=([G18_10a_02_11b]=genie_v3_g18 [AR23_20i_00_000]=genie_v3_ar23)
TUNES="G18_10a_02_11b AR23_20i_00_000"; NT=64; NEV=17500
mkdir -p "$F/logs" "$F/gst" "$F/gen5d" "$F/runs"
echo "[f1b2] job=$SLURM_JOB_ID host=$(hostname) pin=$PIN P=$P start=$(date -u +%FT%TZ)"
need() { [ "$1" -eq 0 ] || { echo "[f1b2] STOP: $2 rc=$1" >&2; exit 1; }; }
anaenv() { source "$D/setup_salloc_env.sh" > "$F/logs/env-$1.log" 2>&1; case "$(python3 -V 2>&1)" in *3.11*) ;; *) exit 7 ;; esac; }

for T in $TUNES; do for k in $(seq 1 $NT); do echo "$T $(( ${BASE[$T]} + k ))"; done; done > "$F/queue.txt"
export G A F NEV TO
xargs -P "$P" -L 1 bash -c 'mkdir -p "$F/runs/$0" && /usr/bin/time -v -o "$F/runs/$0/task_s$1.time" timeout "$TO" \
    bash "$G/run_gevgen_v3.sh" genie "$0" "$A/splines" "$NEV" "$1" "$F/work/$0/s$1" "$A/flux_phi_t_0_100.root" \
    > "$F/logs/gen_$0_s$1.log" 2>&1 || exit 255' < "$F/queue.txt"
need $? "generation"
echo "[f1b2] generation done $(date -u +%FT%TZ)"
( anaenv fc; python3 "$G/gen5d_v3.py" flux-check --flux "$A/flux_phi_t_0_100.root" --work "$F"/work/*/s* ) \
  > "$F/logs/flux_check.log" 2>&1
need $? "the sampled-spectrum check (NOWIDTH)"
for T in $TUNES; do
  n=$(ls "$F/work/$T"/s*/genie_v3.gst.root 2>/dev/null | wc -l)
  [ "$n" -eq "$NT" ] || { echo "[f1b2] STOP: $T has $n of $NT gst files" >&2; exit 1; }
done
pids=()
for T in $TUNES; do
  ( anaenv "c_$T"
    hadd "$F/gst/${NAME[$T]}_ALL.gst.root" "$F/work/$T"/s*/genie_v3.gst.root > "$F/logs/hadd_$T.log" 2>&1 || exit 1
    python3 "$G/gen5d_v3.py" convert --tune "$T" --gst "$F/gst/${NAME[$T]}_ALL.gst.root" --graphs "$A/graphs_$T.root" \
      --flux "$A/flux_phi_t_0_100.root" --out "$F/gen5d/${NAME[$T]}_xsec5d.npz" ) > "$F/logs/convert_$T.log" 2>&1 & pids+=($!)
done
for p in "${pids[@]}"; do wait "$p"; need $? "hadd or conversion"; done
( anaenv p
  args=()
  for T in $TUNES; do Q="$F/gen5d/${NAME[$T]}_xsec5d.npz"; args+=(--pred "${NAME[$T]}=$Q=$(sha256sum "$Q" | cut -d' ' -f1)"); done
  python3 "$D/nd-unfolding/fd_f1_prep.py" "${args[@]}" --out "$F/prep" ) > "$F/logs/prep.log" 2>&1
need $? "prep"
( cd "$F" && find gst gen5d prep runs -type f -print0 | sort -z | xargs -0 sha256sum ) > "$F/f1b2-SHA256SUMS"
echo "[f1b2] done end=$(date -u +%FT%TZ)"
