#!/bin/bash
#SBATCH --account=m3246
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
# F1b (state/measurement-paper/5d-community-20261024/FD-F1-DECLARATION.md section 2.2): per tune, 64 gevgen tasks of
# 17,500 events (seeds 60001-60064 and 61001-61064), 128 at once on the node's 128 cores; hadd; gen5d_v3.py convert
# (sampling test included); then fd_f1_prep.py on both predictions. Runs only if F1a's budget.json says GO, from a
# clean deploy at <pin>. Writes only under <OUT>/f1b, and refuses if that exists.
# Submitted only by submit_fd_f1.sh f1b, with --time from F1a's budget.json (at most 0:45).
set -o pipefail   # NOT set -u
D="${1:?deploy}"; PIN="${2:?pin}"; OUT="${3:?out}"
head_sha=$(git -C "$D" rev-parse HEAD 2>/dev/null)
dirty=$(git -C "$D" status --porcelain --untracked-files=no 2>/dev/null | wc -l)
if [ "$head_sha" != "$PIN" ] || [ "$dirty" -ne 0 ]; then
    echo "[f1b] refusing: deploy HEAD=$head_sha (pinned $PIN), $dirty modified tracked files" >&2; exit 2
fi
A="$OUT/f1a"; F="$OUT/f1b"
grep -q '"decision": "GO"' "$A/budget.json" 2>/dev/null || { echo "[f1b] refusing: F1a's budget is not GO" >&2; exit 2; }
[ ! -e "$F" ] || { echo "[f1b] refusing: $F exists" >&2; exit 2; }
G="$D/3d-unfolding/genie"
declare -A BASE=([G18_10a_02_11b]=60000 [AR23_20i_00_000]=61000)
declare -A NAME=([G18_10a_02_11b]=genie_v3_g18 [AR23_20i_00_000]=genie_v3_ar23)
TUNES="G18_10a_02_11b AR23_20i_00_000"; NT=64; NEV=17500
mkdir -p "$F/logs" "$F/gst" "$F/gen5d"
echo "[f1b] job=$SLURM_JOB_ID host=$(hostname) pin=$PIN start=$(date -u +%FT%TZ)"
need() { [ "$1" -eq 0 ] || { echo "[f1b] STOP: $2 rc=$1" >&2; exit 1; }; }
anaenv() { source "$D/setup_salloc_env.sh" > "$F/logs/env-$1.log" 2>&1; case "$(python3 -V 2>&1)" in *3.11*) ;; *) exit 7 ;; esac; }

pids=()
for T in $TUNES; do
  for k in $(seq 1 $NT); do
    s=$(( ${BASE[$T]} + k ))
    bash "$G/run_gevgen_v3.sh" genie "$T" "$A/splines" "$NEV" "$s" "$F/work/$T/s$s" "$A/flux_phi_t_0_100.root" \
      > "$F/logs/gen_${T}_s$s.log" 2>&1 & pids+=($!)
  done
done
for p in "${pids[@]}"; do wait "$p"; need $? "generation"; done
echo "[f1b] generation done $(date -u +%FT%TZ)"
( anaenv fc; python3 "$G/gen5d_v3.py" flux-check --flux "$A/flux_phi_t_0_100.root" --work "$F"/work/*/s* ) \
  > "$F/logs/flux_check.log" 2>&1
need $? "the sampled-spectrum check (NOWIDTH)"
for T in $TUNES; do
  n=$(ls "$F/work/$T"/s*/genie_v3.gst.root 2>/dev/null | wc -l)
  [ "$n" -eq "$NT" ] || { echo "[f1b] STOP: $T has $n of $NT gst files" >&2; exit 1; }
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
  for T in $TUNES; do P="$F/gen5d/${NAME[$T]}_xsec5d.npz"; args+=(--pred "${NAME[$T]}=$P=$(sha256sum "$P" | cut -d' ' -f1)"); done
  python3 "$D/nd-unfolding/fd_f1_prep.py" "${args[@]}" --out "$F/prep" ) > "$F/logs/prep.log" 2>&1
need $? "prep"
( cd "$F" && find gst gen5d prep -type f -print0 | sort -z | xargs -0 sha256sum ) > "$F/f1b-SHA256SUMS"
echo "[f1b] done end=$(date -u +%FT%TZ)"
