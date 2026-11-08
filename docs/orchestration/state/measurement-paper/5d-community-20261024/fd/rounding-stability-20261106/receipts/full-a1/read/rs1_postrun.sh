#!/bin/bash
# RS1 post-run connect (after the A1 resume, job 60982139): 0 node-h, login node, from a /dev/shm copy of itself ($1).
#   the run, from its own files: log-full/DONE 66/66 rc 0 at M with A1's pin, no FAILED and no .teardown or .failed;
#     log-dry/DONE at M; sacct 60982139 COMPLETED|10090|1;
#   the COV2D fence, recorded;
#   the deploy the job ran from ($NEW/deploy) at M, its tracked files clean, the analysis's blob;
#   V_02's bitwise comparison (the director's ruling 4): xsec_flat and xtrue_flat of runs/V/rs1_V_b-_j6..9.npz against
#     attempt 1's copies in runs-attempt1/rs1_V_02/, under the sourced environment;
#   the bound analysis, rounding_mechanism_analyze.py read at M, under the sourced environment, with FD-STAB's references
#     from attempt 1's $OLD/refs (each verified by the analysis against FD-STAB's pinned SHA256SUMS).
# Writes only $NEW/read/ (refused if it exists). Attempt 1's root is read, never written. No set -u.
SELF=$1
M=e306087e68fd497541d32b440848a40f7f29611e
MA1=1f747346519d75a680b5c67d644bae798eeb5f86
NEW=/pscratch/sd/j/josephrb/rs1-a1-20261107
OLD=/pscratch/sd/j/josephrb/rs1-20261106
D=$NEW/deploy
R=$NEW/read
S=docs/orchestration/state/measurement-paper/5d-community-20261024
bail() { rm -f -- "$SELF"; exit 9; }
[ -n "$SELF" ] && [ -f "$SELF" ] || exit 9
[ -d "$NEW/runs" ] && [ ! -e "$R" ] || bail
mkdir "$R" || bail
exec > "$R/connect-postrun.log" 2>&1
finish() { echo "rs1 postrun rc=$1"; date -u +%FT%TZ; echo "$1" > "$R/connect-postrun.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"; date -u +%FT%TZ
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$R/rs1_postrun.sh"

echo "== the run"
cat "$NEW/log-full/DONE"; echo
python3 -c '
import json, sys
d = json.load(open(sys.argv[1]))
ok = d.get("mode") == "full" and d.get("addendum") == "A1" and d.get("tasks") == 66 and d.get("ended") == 66 \
    and d.get("staged") == 20 and d.get("ran") == 46 and d.get("rc") == 0 and d.get("job") == "60982139" \
    and d.get("pin") == sys.argv[2] and d.get("a1_pin") == sys.argv[3] and d.get("teardown") == ""
sys.exit(0 if ok else 1)' "$NEW/log-full/DONE" "$M" "$MA1" || { echo "STOP: the DONE is not the run's"; finish 4; }
[ ! -e "$NEW/log-full/FAILED" ] && [ -z "$(ls "$NEW/log-full" | grep -E '\.(teardown|failed)$')" ] || { echo "STOP: a FAILED, teardown or failed record"; finish 4; }
dp=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("pin",""))' "$NEW/log-dry/DONE")
[ "$dp" = "$M" ] || { echo "STOP: the dry DONE is not at M"; finish 4; }
sa=$(sacct -j 60982139 -X -n -P -o State,ElapsedRaw,NNodes | head -1); echo "60982139 $sa"
[ "$sa" = "COMPLETED|10090|1" ] || { echo "STOP: sacct is not the run's"; finish 4; }

echo "== COV2D fence"
squeue -u josephrb -h -o '%i|%j|%T|%M|%l' > "$R/squeue-before.txt" 2>&1 || { echo "STOP: squeue failed"; finish 9; }
hits=$(awk -F'|' '$2 ~ /^cov2d-/' "$R/squeue-before.txt")
if [ -n "$hits" ]; then echo "FENCE: cov2d jobs present (recorded):"; printf '%s\n' "$hits"; else echo "FENCE: no cov2d-* job queued or running"; fi
cat "$R/squeue-before.txt"

echo "== the deploy"
[ "$(git -C "$D" rev-parse HEAD)" = "$M" ] || { echo "STOP: deploy HEAD is not M"; finish 9; }
n=$(git -C "$D" status --porcelain --untracked-files=no | wc -l); echo "HEAD $M; modified tracked files: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy has modified tracked files"; finish 9; }
[ "$(git -C "$D" hash-object nd-unfolding/rounding_mechanism_analyze.py)" = d58c241eff687a96bda94812d145a90d9f4790ed ] \
  && [ "$(git -C "$D" hash-object nd-unfolding/rounding_mechanism_probe.py)" = 8465d84f08e99ad12f2c4fb3afca2ea7efbe485b ] \
  || { echo "STOP: the analysis or probe blob"; finish 9; }

echo "== V_02 bitwise (sourced environment)"
( source "$D/setup_salloc_env.sh" > "$R/env-v02.log" 2>&1
  python3 -B -c '
import json, sys, numpy as np
new, old, out = sys.argv[1], sys.argv[2], sys.argv[3]
res = {}
for j in (6, 7, 8, 9):
    name = f"rs1_V_b-_j{j}.npz"
    a, b = np.load(f"{new}/runs/V/{name}"), np.load(f"{old}/{name}")
    res[name] = {k: bool(np.array_equal(a[k], b[k])) for k in ("xsec_flat", "xtrue_flat")}
json.dump({"schema": "rs1-v02-compare/1", "compare": res,
           "all_bitwise_identical": all(all(v.values()) for v in res.values())}, open(out, "w"), indent=1)
print(json.dumps(res))' "$NEW" "$NEW/runs-attempt1/rs1_V_02" "$R/v02-compare.json" ) || { echo "STOP: the V_02 comparison failed to run"; finish 5; }
cat "$R/v02-compare.json"

echo "== the analysis (bound, sourced environment)"
( source "$D/setup_salloc_env.sh" > "$R/env-read.log" 2>&1
  python3 --version
  cd "$D" && PYTHONDONTWRITEBYTECODE=1 nice -n 19 python3 -B nd-unfolding/rounding_mechanism_analyze.py read \
    --runs "$NEW/runs" --fdstab-refs "$OLD/refs" --fdstab-sums "$D/$S/fd/receipts-stab-a1r/full/SHA256SUMS" \
    --s5c-contract "$D/docs/orchestration/state/s5c/contract.json" \
    --h2-definition "$D/nd-unfolding/pv-ladder/readouts/h2_definition.json" \
    --sigma-receipt "$D/docs/orchestration/state/s5e/cand/assess_receipt.json" --out "$R/rs1_read.json" ); rc=$?
echo "analysis rc=$rc"
[ -s "$R/rs1_read.json" ] && sha256sum "$R/rs1_read.json"
( cd "$NEW" && find runs -type f ! -name '*.partial*' -print0 | sort -z | xargs -0 sha256sum ) > "$R/runs-SHA256SUMS"
echo "runs files pinned: $(wc -l < "$R/runs-SHA256SUMS")"
finish $rc
