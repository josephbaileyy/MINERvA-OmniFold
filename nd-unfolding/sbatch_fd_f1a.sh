#!/bin/bash
#SBATCH --account=m3246
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
# F1a (state/measurement-paper/5d-community-20261024/FD-F1-DECLARATION.md section 2.1): the GENIE v3 pilot, from a
# clean deploy at <pin>. Per tune: the reduced CH splines and their header check, gspl2root graphs, a 10,000-event
# pilot whose wall is timed, and its conversion through gen5d_v3.py convert (the sampling test included); once: the
# phi_t flux file and its hFluxCV check. Then fd_f1_budget.py's GO/STOP. Every step's rc is checked; the job exits 0
# only on GO. Writes only under <OUT>/f1a, and refuses if that exists.
# Submitted only by submit_fd_f1.sh f1a (regular QOS, --time=00:20:00).
set -o pipefail   # NOT set -u (the environment's activation aborts under it)
D="${1:?deploy}"; PIN="${2:?pin}"; OUT="${3:?out}"
head_sha=$(git -C "$D" rev-parse HEAD 2>/dev/null)
dirty=$(git -C "$D" status --porcelain --untracked-files=no 2>/dev/null | wc -l)
if [ "$head_sha" != "$PIN" ] || [ "$dirty" -ne 0 ]; then
    echo "[f1a] refusing: deploy HEAD=$head_sha (pinned $PIN), $dirty modified tracked files" >&2; exit 2
fi
F="$OUT/f1a"
[ ! -e "$F" ] || { echo "[f1a] refusing: $F exists" >&2; exit 2; }
G="$D/3d-unfolding/genie"; X=/cvmfs/larsoft.opensciencegrid.org/products/genie_xsec/v3_04_00/NULL
PHIT=/pscratch/sd/j/josephrb/s5p-20260926/gen5d_fluxfix
declare -A Q=([G18_10a_02_11b]=G1810a0211b-k250-e1000 [AR23_20i_00_000]=AR2320i00000-k250-e1000)
declare -A SEED=([G18_10a_02_11b]=60000 [AR23_20i_00_000]=61000)
TUNES="G18_10a_02_11b AR23_20i_00_000"
mkdir -p "$F/logs" "$F/splines" "$F/pilot"
T0=$(date +%s)
echo "[f1a] job=$SLURM_JOB_ID host=$(hostname) pin=$PIN start=$(date -u +%FT%TZ)"
need() { [ "$1" -eq 0 ] || { echo "[f1a] STOP: $2 rc=$1" >&2; exit 1; }; }
anaenv() { source "$D/setup_salloc_env.sh" > "$F/logs/env-$1.log" 2>&1; case "$(python3 -V 2>&1)" in *3.11*) ;; *) exit 7 ;; esac; }

pids=(); for T in $TUNES; do bash "$G/run_gevgen_v3.sh" reduce "$T" "$F/splines" > "$F/logs/reduce_$T.log" 2>&1 & pids+=($!); done
for p in "${pids[@]}"; do wait "$p"; need $? "spline reduce"; done
( anaenv a1
  python3 "$G/gen5d_v3.py" make-flux --phi-t-dir "$PHIT" --out "$F/flux_phi_t_0_100.root" || exit 1
  for T in $TUNES; do
    python3 "$G/gen5d_v3.py" spline-check --tune "$T" --source "$X/${Q[$T]}/data/gxspl-NUsmall.xml" \
      --reduced "$F/splines/${T}_CH.xml.gz" --readme "$X/${Q[$T]}/data/README" --out "$F/spline_check_$T.json" || exit 1
  done ) > "$F/logs/flux_and_splines.log" 2>&1
need $? "flux file or spline check"
pids=(); for T in $TUNES; do bash "$G/run_gevgen_v3.sh" graphs "$T" "$F/splines" "$F/graphs_$T.root" > "$F/logs/graphs_$T.log" 2>&1 & pids+=($!); done
for p in "${pids[@]}"; do wait "$p"; need $? "gspl2root"; done
pids=()
for T in $TUNES; do
  ( s=$(date +%s.%N)
    bash "$G/run_gevgen_v3.sh" genie "$T" "$F/splines" 10000 "${SEED[$T]}" "$F/pilot/$T" "$F/flux_phi_t_0_100.root" || exit 1
    e=$(date +%s.%N); echo "$s $e" > "$F/pilot/wall_$T.txt" ) > "$F/logs/pilot_$T.log" 2>&1 & pids+=($!)
done
for p in "${pids[@]}"; do wait "$p"; need $? "pilot generation"; done
( anaenv fc; python3 "$G/gen5d_v3.py" flux-check --flux "$F/flux_phi_t_0_100.root" \
    --work $(for T in $TUNES; do echo "$F/pilot/$T"; done) ) > "$F/logs/flux_check.log" 2>&1
need $? "the sampled-spectrum check (NOWIDTH)"
pids=()
for T in $TUNES; do
  ( anaenv "c_$T"; python3 "$G/gen5d_v3.py" convert --tune "$T" --gst "$F/pilot/$T/genie_v3.gst.root" \
      --graphs "$F/graphs_$T.root" --flux "$F/flux_phi_t_0_100.root" --out "$F/pilot/$T/pilot_xsec5d.npz" ) \
    > "$F/logs/convert_$T.log" 2>&1 & pids+=($!)
done
for p in "${pids[@]}"; do wait "$p"; need $? "pilot conversion"; done
W=(); for T in $TUNES; do read -r s e < "$F/pilot/wall_$T.txt"; W+=(--wall "$T=$(awk -v s="$s" -v e="$e" 'BEGIN{printf "%.3f", e - s}')"); done
NH=$(awk -v t0="$T0" -v t1="$(date +%s)" 'BEGIN{printf "%.6f", (t1 - t0) / 3600}')
( anaenv b; python3 "$D/nd-unfolding/fd_f1_budget.py" "${W[@]}" --f1a-node-h "$NH" --out "$F/budget.json" ) > "$F/logs/budget.log" 2>&1
brc=$?
( cd "$F" && find . -type f ! -path './logs/*' ! -name f1a-SHA256SUMS -print0 | sort -z | xargs -0 sha256sum ) > "$F/f1a-SHA256SUMS"
cat "$F/logs/budget.log"
echo "[f1a] budget rc=$brc end=$(date -u +%FT%TZ)"
exit $brc
