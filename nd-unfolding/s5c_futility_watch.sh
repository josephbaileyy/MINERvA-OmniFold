#!/bin/bash
# Contract amendment 3 futility rule (evaluated under amendment 4), run unattended: wait until the first <n> declared validation
# seeds of EVERY grid point exist, run the frozen evaluator with --interim <n> and the amendment-4
# bias correction, and on FUTILITY-FAIL write <stop_file> (s5c_queue.sh then skips validation
# launches) and cancel running validation allocations, so no further validation experiment runs.
#
# Usage (login node, under nohup):  s5c_futility_watch.sh <deploy_tree> <n> <stop_file>
# Result: $NS/runs/futility/interim_<n>.json. CONTINUE and INCOMPLETE change nothing. It never
# yields PASS (the evaluator's --interim cannot), and it gives up after 96 hours of waiting.

DEPLOY=${1:?deploy}; N=${2:?n}; STOP=${3:?stop file}
NS=${S5C_NS:-/pscratch/sd/j/josephrb/s5c-20260924}
PY=${S5C_PY:-/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3}
C="$DEPLOY/docs/orchestration/state/s5c"
stamp() { date -u +%FT%TZ; }
count() {
    /usr/bin/python3.11 - "$C/contract.json" "$NS/runs/s_valid" "$N" <<'EOF'
import json, sys
from pathlib import Path
cov = json.load(open(sys.argv[1]))["coverage"]
d, n = Path(sys.argv[2]), int(sys.argv[3])
have = need = 0
for g in cov["grid"]:
    s0 = g["validation_seeds"][0]
    tag = f"{g['truth']}_a{g['amplitude']:g}"
    need += n
    have += sum((d / f"{tag}_s{s}.npz").exists() for s in range(s0, s0 + n))
print(have, need)
EOF
}
t0=$(date +%s)
while :; do
    have=; need=
    read -r have need < <(count)
    echo "[futility] $(stamp) present ${have:-?} of ${need:-?}"
    # fail closed: an empty or failed count never reads as complete
    [[ "$have" =~ ^[0-9]+$ && "$need" =~ ^[1-9][0-9]*$ && "$have" -eq "$need" ]] && break
    [ $(( $(date +%s) - t0 )) -lt 345600 ] || { echo "[futility] $(stamp) gave up waiting"; exit 4; }
    sleep "${S5C_WATCH_POLL:-600}"
done
mkdir -p "$NS/runs/futility"
OUT="$NS/runs/futility/interim_$N.json"
rm -f "$OUT"   # a stale result must never be read as this look's
cd "$DEPLOY/nd-unfolding" || exit 2
$PY s5c_coverage.py --contract "$C/contract.json" --experiments "$NS/runs/s_valid" \
    --bootstrap "$NS/runs/s_sigma" --bias-correction "$C/d1/bias_correction.json" --interim "$N" --out "$OUT"
verdict=$(/usr/bin/python3.11 -c "import json,sys; print(json.load(open(sys.argv[1]))['verdict'])" "$OUT" 2>/dev/null)
echo "[futility] $(stamp) verdict=${verdict:-none} out=$OUT"
if [ "$verdict" = "FUTILITY-FAIL" ]; then
    echo "futility FAIL $(stamp) $OUT" > "$STOP"
    for j in $(squeue -h --me -o "%i %j" | awk '$2 ~ /^s5c-tier_s_valid_/ {print $1}'); do
        scancel "$j" && echo "[futility] $(stamp) cancelled validation allocation $j"
    done
fi
