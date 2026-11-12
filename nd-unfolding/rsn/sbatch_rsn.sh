#!/bin/bash
#SBATCH --account=m3246
#SBATCH --constraint=cpu
#SBATCH --qos=regular
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
# RSN (state/measurement-paper/5d-community-20261024/fd/referee-sensitivity-20261111/RSN-DECLARATION.md §5-6): every
# task of one declared job (rsn_tasks.tsv column 2) at once, one srun step each, through mnv_guarded_run.py from a clean
# deploy at <pin>, as pv-ladder/sbatch_pvl.sh runs L-5D-PV. Runs only on the director's go for each connect.
#   sbatch --job-name=rsn_<job> --time=<limit> --output=<OUT>/logs/%x_%j.out sbatch_rsn.sh <deploy> <pin> <OUT> <job>
#   J1   the NC alone (rsn_nc); limit 0:19:00. Every job waits on <OUT>/nc_r.json, the login-node NC-R PASS.
#   J2   G6, SM, WR and TR, eight steps; limit 0:22:00. Only after <OUT>/nc.json records the NC's PASS and
#        <OUT>/gates/J2.ok names <pin>.
#   J2n  J2 without SM, five steps; limit 0:22:00. Only if the committed rsn-prep-SHA256SUMS lists no SM reweight.
#   J3   the F1.1 closures at the A7 GiBUU hybrid and the q3 tilt, weighted and with equal weights, four steps;
#        limit 0:19:00. Only after the NC's PASS and <OUT>/gates/J3.ok names <pin>.
# Every job refuses before any step unless: the deploy is clean at <pin>; the job's name is rsn_<job> and its Slurm
# TimeLimit is at most the job's declared limit; <OUT>/fence.txt names the fenced job-name prefixes and none of them is
# queued or running; and every reweight matches its committed sha256 (pv-ladder's prep-SHA256SUMS for the frozen ones,
# nd-unfolding/rsn/rsn-prep-SHA256SUMS for RSN's). With RSN_SMOKE set it stops after these checks and prints the steps.
set -o pipefail   # NOT set -u (the environment's activation aborts under it)
D="${1:?deploy}"; PIN="${2:?pin}"; OUT="${3:?out}"; JOB="${4:?job}"
PVL_PREP="${RSN_PVL_PREP:-/pscratch/sd/j/josephrb/pv-ladder-20261024/prep}"
V="$D/nd-unfolding/pv-ladder"
H="$D/nd-unfolding/rsn"
say() { echo "[rsn] $*" >&2; }
head_sha=$(git -C "$D" rev-parse HEAD 2>/dev/null)
dirty=$(git -C "$D" status --porcelain --untracked-files=no 2>/dev/null | wc -l)
stray=$(git -C "$D" status --porcelain --untracked-files=all -- nd-unfolding 2>/dev/null | wc -l)
if [ "$head_sha" != "$PIN" ] || [ "$dirty" -ne 0 ] || [ "$stray" -ne 0 ]; then
    say "refusing: deploy HEAD=$head_sha (pinned $PIN), $dirty modified tracked files, $stray untracked"; exit 2
fi
case "$JOB" in
    J1|J3) LIMIT=0:19:00 ;;
    J2|J2n) LIMIT=0:22:00 ;;
    *) say "refusing: job $JOB"; exit 2 ;;
esac
if [ -n "$SLURM_JOB_ID" ]; then
    NAME="$SLURM_JOB_NAME"; TL=$(squeue -h -j "$SLURM_JOB_ID" -o %l 2>/dev/null)
elif [ -n "$RSN_SMOKE" ]; then
    NAME="${RSN_NAME:-rsn_$JOB}"; TL="${RSN_TIMELIMIT:-$LIMIT}"
else
    say "refusing: not inside a Slurm job"; exit 2
fi
[ "$NAME" = "rsn_$JOB" ] || { say "refusing: job name $NAME is not rsn_$JOB"; exit 2; }
# the limit in every form squeue prints it (M:SS below an hour, H:MM:SS, D-HH:MM:SS); 0 within, 4 above, 3 unreadable
python3 - "$TL" "$LIMIT" <<'EOF'
import sys
def sec(t):
    d, dash, rest = t.partition("-")
    f = rest.split(":") if dash else t.split(":")
    if (dash and not d.isdigit()) or not all(x.isdigit() for x in f) or not 1 <= len(f) <= 3:
        raise ValueError(t)
    f = [int(x) for x in f]
    if dash:
        h, m, s = f + [0] * (3 - len(f))
        return int(d) * 86400 + h * 3600 + m * 60 + s
    if len(f) == 1:
        return f[0] * 60
    if len(f) == 2:
        return f[0] * 60 + f[1]
    return f[0] * 3600 + f[1] * 60 + f[2]
try:
    tl, lim = sec(sys.argv[1]), sec(sys.argv[2])
except ValueError:
    sys.exit(3)
sys.exit(0 if tl <= lim else 4)
EOF
trc=$?
[ "$trc" -ne 3 ] || { say "refusing: could not read the Slurm TimeLimit '$TL'"; exit 2; }
[ "$trc" -ne 4 ] || { say "refusing: Slurm TimeLimit $TL exceeds the declared $LIMIT"; exit 2; }
[ "$trc" -eq 0 ] || { say "refusing: the TimeLimit check failed (rc $trc)"; exit 2; }
# the fence (§6): fails closed on no fence file, an empty one, or a squeue that cannot answer
[ -s "$OUT/fence.txt" ] || { say "refusing: no $OUT/fence.txt naming the fenced job-name prefixes"; exit 2; }
sq=$(squeue -h -u "${USER:-josephrb}" -o '%j|%T' 2>/dev/null) || { say "refusing: squeue failed"; exit 2; }
while IFS= read -r pre; do
    [ -n "$pre" ] || continue
    hit=$(printf '%s\n' "$sq" | awk -F'|' -v p="$pre" 'index($1, p) == 1')
    [ -z "$hit" ] || { say "refusing: fenced jobs ($pre*) are queued or running: $hit"; exit 2; }
done < "$OUT/fence.txt"
# NC-R (§6): every job waits on the login-node regrade's reproduction of the committed F1 readout
grep -q '"schema": "rsn-nc-r/1"' "$OUT/nc_r.json" 2>/dev/null && grep -q '"verdict": "PASS"' "$OUT/nc_r.json" \
    || { say "refusing: $OUT/nc_r.json records no NC-R PASS"; exit 2; }
RSUMS="$H/rsn-prep-SHA256SUMS"
if [ "$JOB" != J1 ]; then
    G="$OUT/gates/$JOB.ok"
    [ -f "$G" ] && grep -qx "pin=$PIN" "$G" || { say "refusing: $G is missing or does not name pin $PIN"; exit 2; }
    grep -q '"verdict": "PASS"' "$OUT/nc.json" 2>/dev/null || { say "refusing: $OUT/nc.json records no NC PASS"; exit 2; }
fi
if [ "$JOB" = J2 ] || [ "$JOB" = J2n ]; then
    [ -s "$RSUMS" ] || { say "refusing: no committed $RSUMS"; exit 2; }
    n_sm=$(grep -c ' \./SM/' "$RSUMS")
    if [ "$JOB" = J2 ] && [ "$n_sm" -ne 3 ]; then say "refusing: J2 needs the three SM reweights ($n_sm listed); use J2n"; exit 2; fi
    if [ "$JOB" = J2n ] && [ "$n_sm" -ne 0 ]; then say "refusing: J2n is only for a prep that built no SM reweight"; exit 2; fi
fi
LINES=()
while IFS= read -r ln; do LINES+=("$ln"); done < <(grep -v '^#' "$H/rsn_tasks.tsv" | awk -F'\t' -v j="$JOB" '$2 == j')
[ "${#LINES[@]}" -gt 0 ] || { say "refusing: no tasks for job $JOB"; exit 2; }
ratio_of() {  # ratio_of <spec>: "<path> <sha256>" from the committed sums, or nothing
    local src="${1%%:*}" rel="${1#*:}"
    case "$src" in
        frozen) awk -v f="./ratios/L-5D-PV/$rel.json" -v d="$PVL_PREP/ratios/L-5D-PV/$rel.json" '$2 == f {print d, $1}' "$V/prep-SHA256SUMS" ;;
        rsn) awk -v f="./$rel.json" -v d="$OUT/prep/$rel.json" '$2 == f {print d, $1}' "$RSUMS" ;;
    esac
}
cfg() {  # cfg <key: npz|bkg> <field: path|sha256>
    python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['rungs']['L-5D-PV'][sys.argv[2]][sys.argv[3]])" \
        "$V/config.json" "$1" "$2"
}
# validate every task first, so a refusal never leaves steps running
for line in "${LINES[@]}"; do
    IFS=$'\t' read -r task _ _ ratio _ _ _ _ _ <<< "$line"
    read -r RF SHA <<< "$(ratio_of "$ratio")"
    [ -n "$SHA" ] && [ -f "$RF" ] && [ "$(sha256sum "$RF" | cut -d' ' -f1)" = "$SHA" ] \
        || { say "refusing: the reweight of $task ($ratio) is missing or differs from its committed sha256"; exit 2; }
    [ ! -e "$OUT/products/$task.npz" ] || { say "refusing: $OUT/products/$task.npz exists"; exit 2; }
done
if [ -z "$RSN_SMOKE" ]; then
    mkdir -p "$OUT/logs" "$OUT/inventory" "$OUT/products"
    source "$D/setup_salloc_env.sh" > "$OUT/logs/env-${SLURM_JOB_ID}.log" 2>&1
    case "$(python -V 2>&1)" in
        *3.11*) ;;
        *) say "refusing: environment did not activate ($(python -V 2>&1))"; exit 2 ;;
    esac
    export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
    export TMPDIR="$OUT/tmp"; mkdir -p "$TMPDIR"
    JOBMEM=${SLURM_MEM_PER_NODE:-$(scontrol show job "$SLURM_JOB_ID" | grep -o 'AllocTRES=[^ ]*' \
            | sed -n 's/.*mem=\([0-9]*\)\([MG]\).*/\1 \2/p' | awk '{print ($2 == "G") ? $1 * 1024 : $1}')}
    [ -n "$JOBMEM" ] && [ "$JOBMEM" -gt 0 ] || { say "refusing: cannot read the job's memory allocation"; exit 2; }
    MEM=$(( JOBMEM * 95 / 100 / ${#LINES[@]} ))
    CPS=$(( ${SLURM_CPUS_ON_NODE:-$(nproc)} / ${#LINES[@]} )); [ "$CPS" -gt 42 ] && CPS=42
    [ "$CPS" -ge 32 ] || { say "refusing: $CPS CPUs per step is below LightGBM's 32 threads"; exit 2; }
    echo "[rsn] job=$JOB slurm=$SLURM_JOB_ID node=$(hostname) tasks=${#LINES[@]} mem_per_step=${MEM}M cpus_per_step=$CPS start=$(date -u +%FT%TZ)"
fi
pids=(); names=()
for line in "${LINES[@]}"; do
    IFS=$'\t' read -r task _ _ ratio closure weight truth transfer _ <<< "$line"
    read -r RF SHA <<< "$(ratio_of "$ratio")"
    extra=(); [ "$closure" = yes ] && extra=(--closure)
    [ "$transfer" = yes ] && extra+=(--transfer)
    cmd=(python "$D/nd-unfolding/mnv_guarded_run.py" --expect-root "$D" --inventory "$OUT/inventory/$task.jsonl"
         --label "rsn:$task" -- "$H/rsn_unfold.py" --regressor-weight "$weight" --truth "$truth"
         --rung L-5D-PV --arm e --features all --ratio "$RF" --expect-ratio-sha256 "$SHA" "${extra[@]}"
         --npz "$(cfg npz path)" --expect-npz-sha256 "$(cfg npz sha256)"
         --bkg "$(cfg bkg path)" --expect-bkg-sha256 "$(cfg bkg sha256)"
         --estimator-seed 42 --threads 32 --iters 5 --out "$OUT/products/$task.npz")
    if [ -n "$RSN_SMOKE" ]; then
        printf '%s\n' "STEP $task ${cmd[*]}"
        continue
    fi
    srun -n1 -c "$CPS" --mem="${MEM}M" --exact --cpu-bind=cores "${cmd[@]}" > "$OUT/logs/$task.log" 2>&1 &
    pids+=("$!"); names+=("$task")
done
[ -n "$RSN_SMOKE" ] && { echo "[rsn] smoke: checks passed, ${#LINES[@]} steps"; exit 0; }
rc=0
for i in "${!pids[@]}"; do
    if wait "${pids[$i]}"; then
        sha256sum "$OUT/products/${names[$i]}.npz"
    else
        say "task ${names[$i]} failed; see $OUT/logs/${names[$i]}.log"; rc=1
    fi
done
echo "[rsn] job=$JOB rc=$rc end=$(date -u +%FT%TZ)"
exit $rc
