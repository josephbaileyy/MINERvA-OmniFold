#!/bin/bash
#SBATCH --account=m3246
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
# F1a' (state/measurement-paper/5d-community-20261024/FD-F1-DECLARATION-AMENDMENT-1.md section 3): the re-pilot at
# F1b''s concurrency, from a clean deploy at <pin>. F1a's splines, flux file and graphs are reused only after they
# re-verify against the committed f1a-SHA256SUMS. Per tune, 4 processes run one full F1b' task (17,500 events) and 4
# run 1,000 events twice in a row, so all 16 run together for about one task; every run is timed by /usr/bin/time -v.
# Then the NOWIDTH flux-check on every run and fd_f1_budget2.py's GO/STOP. Writes only under <OUT>/f1a2, and refuses
# if that exists.
# Submitted only by submit_fd_f1.sh f1a2 (regular QOS, --time=00:20:00).
set -o pipefail   # NOT set -u
D="${1:?deploy}"; PIN="${2:?pin}"; OUT="${3:?out}"; PRICED="${4:?priced node-h}"; CEIL="${5:?ceiling node-h}"
head_sha=$(git -C "$D" rev-parse HEAD 2>/dev/null)
dirty=$(git -C "$D" status --porcelain --untracked-files=no 2>/dev/null | wc -l)
if [ "$head_sha" != "$PIN" ] || [ "$dirty" -ne 0 ]; then
    echo "[f1a2] refusing: deploy HEAD=$head_sha (pinned $PIN), $dirty modified tracked files" >&2; exit 2
fi
A="$OUT/f1a"; F="$OUT/f1a2"
[ ! -e "$F" ] || { echo "[f1a2] refusing: $F exists" >&2; exit 2; }
G="$D/3d-unfolding/genie"; ND="$D/nd-unfolding"
SUMS="$D/docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-f1/amendment-1/f1a-SHA256SUMS"
SPENT=0.307500    # F1's charge before the re-pilot: F1a 0.104722 + F1b 0.202778 (fd/LEDGER.tsv)
TUNES="G18_10a_02_11b AR23_20i_00_000"
declare -A BASE2=([G18_10a_02_11b]=60100 [AR23_20i_00_000]=61100)
mkdir -p "$F/logs" "$F/runs" "$F/work"
T0=$(date +%s)
echo "[f1a2] job=$SLURM_JOB_ID host=$(hostname) pin=$PIN priced=$PRICED ceiling=$CEIL start=$(date -u +%FT%TZ)"
need() { [ "$1" -eq 0 ] || { echo "[f1a2] STOP: $2 rc=$1" >&2; exit 1; }; }
anaenv() { source "$D/setup_salloc_env.sh" > "$F/logs/env-$1.log" 2>&1; case "$(python3 -V 2>&1)" in *3.11*) ;; *) exit 7 ;; esac; }

# F1a's reused products: exactly the committed lines for splines, flux and graphs, each re-verified
grep -E '  \./(splines/[A-Za-z0-9_]+_CH\.xml\.gz|flux_phi_t_0_100\.root|graphs_[A-Za-z0-9_]+\.root)$' "$SUMS" > "$F/reused.sha256"
[ "$(wc -l < "$F/reused.sha256")" -eq 5 ] || { echo "[f1a2] STOP: expected 5 reused F1a products" >&2; exit 1; }
( cd "$A" && sha256sum -c "$F/reused.sha256" ) > "$F/logs/reused-check.log" 2>&1
need $? "F1a's reused products re-verify"

run() {  # run <tune> <role> <events> <seed>
  /usr/bin/time -v -o "$F/runs/$1/$2_s$4.time" \
    bash "$G/run_gevgen_v3.sh" genie "$1" "$A/splines" "$3" "$4" "$F/work/$1/s$4" "$A/flux_phi_t_0_100.root" \
    > "$F/logs/gen_$1_s$4.log" 2>&1
}
pids=()
for T in $TUNES; do
  mkdir -p "$F/runs/$T"
  b=${BASE2[$T]}                                # fd_f1_budget2.seeds: long b+1..b+4, short b+5..b+12
  L=($(seq $((b + 1)) $((b + 4)))); S=($(seq $((b + 5)) $((b + 12))))
  for s in "${L[@]}"; do run "$T" long 17500 "$s" & pids+=($!); done
  for k in $(seq 0 2 6); do ( run "$T" short 1000 "${S[$k]}" && run "$T" short 1000 "${S[$((k + 1))]}" ) & pids+=($!); done
done
for p in "${pids[@]}"; do wait "$p"; need $? "re-pilot generation"; done
( anaenv fc; python3 "$G/gen5d_v3.py" flux-check --flux "$A/flux_phi_t_0_100.root" --work "$F"/work/*/s* ) \
  > "$F/logs/flux_check.log" 2>&1
need $? "the sampled-spectrum check (NOWIDTH)"
NH=$(awk -v t0="$T0" -v t1="$(date +%s)" 'BEGIN{printf "%.6f", (t1 - t0) / 3600}')
( anaenv b; python3 "$ND/fd_f1_budget2.py" --runs "$F/runs" --spent-node-h "$SPENT" --repilot-node-h "$NH" \
    --priced-node-h "$PRICED" --ceiling-node-h "$CEIL" --job-id "$SLURM_JOB_ID" --out "$F/budget2.json" ) > "$F/logs/budget2.log" 2>&1
brc=$?
( cd "$F" && find . -type f ! -path './logs/*' ! -path './work/*' ! -name f1a2-SHA256SUMS -print0 | sort -z \
    | xargs -0 sha256sum ) > "$F/f1a2-SHA256SUMS"
cat "$F/logs/budget2.log"
echo "[f1a2] budget rc=$brc end=$(date -u +%FT%TZ)"
exit $brc
