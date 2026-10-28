#!/bin/bash
#SBATCH --account=m3246
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
# F1b' in its single-wave layout (state/measurement-paper/5d-community-20261024/FD-F1-DECLARATION-AMENDMENT-2.md
# section 4): 14 gevgen tasks of 160,000 events (7 per tune, seeds 60001-60007 and 61001-61007), all at once, each timed
# by /usr/bin/time -v and bounded by budget3.json's per-task timeout; a failed task exits 255, so xargs starts no further
# task; the NOWIDTH flux-check on all 14; hadd; gen5d_v3.py convert; then fd_f1_prep.py. Runs only if
# <OUT>/gate3/budget3.json says GO, from a clean deploy at <pin>. Writes only under <OUT>/f1b3, refuses if that
# exists, and never reads <OUT>/f1b (F1b's STOP evidence) or <OUT>/f1b2.
# Submitted only by submit_fd_f1.sh f1b3, with --time from budget3.json.
set -o pipefail   # NOT set -u
D="${1:?deploy}"; PIN="${2:?pin}"; OUT="${3:?out}"
head_sha=$(git -C "$D" rev-parse HEAD 2>/dev/null)
dirty=$(git -C "$D" status --porcelain --untracked-files=no 2>/dev/null | wc -l)
if [ "$head_sha" != "$PIN" ] || [ "$dirty" -ne 0 ]; then
    echo "[f1b3] refusing: deploy HEAD=$head_sha (pinned $PIN), $dirty modified tracked files" >&2; exit 2
fi
A="$OUT/f1a"; A2="$OUT/f1a2"; B3="$OUT/gate3/budget3.json"; F="$OUT/f1b3"
grep -q '"decision": "GO"' "$B3" 2>/dev/null || { echo "[f1b3] refusing: $B3 is not GO" >&2; exit 2; }
P=$(sed -n 's/.*"concurrency": \([0-9]*\).*/\1/p' "$B3")
[ "$P" = 14 ] || { echo "[f1b3] refusing: concurrency $P is not the declared 14" >&2; exit 2; }
TO=$(sed -n 's/.*"f1b3_task_timeout_s": \([0-9]*\).*/\1/p' "$B3")
[ -n "$TO" ] && [ "$TO" -gt 0 ] || { echo "[f1b3] refusing: no per-task timeout in $B3" >&2; exit 2; }
[ ! -e "$F" ] || { echo "[f1b3] refusing: $F exists" >&2; exit 2; }
G="$D/3d-unfolding/genie"
( cd "$A" && sha256sum -c "$A2/reused.sha256" ) > /dev/null 2>&1 || { echo "[f1b3] refusing: F1a's products changed" >&2; exit 2; }
declare -A BASE=([G18_10a_02_11b]=60000 [AR23_20i_00_000]=61000)
declare -A NAME=([G18_10a_02_11b]=genie_v3_g18 [AR23_20i_00_000]=genie_v3_ar23)
TUNES="G18_10a_02_11b AR23_20i_00_000"; NT=7; NEV=160000
mkdir -p "$F/logs" "$F/gst" "$F/gen5d" "$F/runs"
echo "[f1b3] job=$SLURM_JOB_ID host=$(hostname) pin=$PIN P=$P timeout=$TO start=$(date -u +%FT%TZ)"
need() { [ "$1" -eq 0 ] || { echo "[f1b3] STOP: $2 rc=$1" >&2; exit 1; }; }
anaenv() { source "$D/setup_salloc_env.sh" > "$F/logs/env-$1.log" 2>&1; case "$(python3 -V 2>&1)" in *3.11*) ;; *) exit 7 ;; esac; }

for T in $TUNES; do for k in $(seq 1 $NT); do echo "$T $(( ${BASE[$T]} + k ))"; done; done > "$F/queue.txt"
export G A F NEV TO
xargs -P "$P" -L 1 bash -c 'mkdir -p "$F/runs/$0" && /usr/bin/time -v -o "$F/runs/$0/task_s$1.time" timeout "$TO" \
    bash "$G/run_gevgen_v3.sh" genie "$0" "$A/splines" "$NEV" "$1" "$F/work/$0/s$1" "$A/flux_phi_t_0_100.root" \
    > "$F/logs/gen_$0_s$1.log" 2>&1 || exit 255' < "$F/queue.txt"
need $? "generation"
echo "[f1b3] generation done $(date -u +%FT%TZ)"
( anaenv fc; python3 "$G/gen5d_v3.py" flux-check --flux "$A/flux_phi_t_0_100.root" --work "$F"/work/*/s* ) \
  > "$F/logs/flux_check.log" 2>&1
need $? "the sampled-spectrum check (NOWIDTH)"
for T in $TUNES; do
  n=$(ls "$F/work/$T"/s*/genie_v3.gst.root 2>/dev/null | wc -l)
  [ "$n" -eq "$NT" ] || { echo "[f1b3] STOP: $T has $n of $NT gst files" >&2; exit 1; }
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
( cd "$F" && find gst gen5d prep runs -type f -print0 | sort -z | xargs -0 sha256sum ) > "$F/f1b3-SHA256SUMS"
need $? "the sums file"
echo "[f1b3] done end=$(date -u +%FT%TZ)"
