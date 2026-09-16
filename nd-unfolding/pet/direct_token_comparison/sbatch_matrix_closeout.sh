#!/bin/bash
# Durable closeout for the frozen matrix. Submitted with
# --dependency=afterany:<array>, so Slurm runs it when the array closes whether or
# not this session still exists. A long-lived watcher process would die with the
# session; a scheduler dependency does not.
#
# It RECORDS and VERIFIES. It decides nothing: the reducer applies the unchanged
# frozen criteria and fails closed on an incomplete matrix, and adoption is not a
# thing any job here can confer. CPU-only, no GPU, no retry, no resubmission.
#SBATCH --account=m3246
#SBATCH --constraint=cpu
#SBATCH --qos=shared
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=00:30:00
#SBATCH --job-name=pet-matrix-closeout
set -uo pipefail

checkout=$1
runtime=$2
output=$3
array=$4
status=$5

mkdir -p "$status"
exec > >(tee -a "$status/closeout.log") 2>&1
echo "closeout started $(date -u +%FT%TZ) for array $array"

# 1. Scheduler truth, per task. Never the bracket: sacct rewrites an array's
#    bracket and throttling truncates its low end.
sacct -j "$array" -X --format=JobID%22,State%16,ElapsedRaw,ExitCode -P > "$status/sacct-tasks.psv"
sacct -j "$array" --format=JobID%22,State%16,ElapsedRaw,ExitCode,MaxRSS -P > "$status/sacct-all-rows.psv"
completed=$(grep -c 'COMPLETED' "$status/sacct-tasks.psv" || true)
failed=$(grep -cE 'FAILED|TIMEOUT|CANCELLED|NODE_FAIL|OUT_OF_MEMORY|BOOT_FAIL|DEADLINE|PREEMPTED' "$status/sacct-tasks.psv" || true)
echo "tasks COMPLETED=$completed  non-completed=$failed"

# 2. Per-task launcher markers, independent of the scheduler's own view.
{
  for mode in ordinary injected shuffle; do
    for seed in 17 29 43 59 71 89 101 113; do
      stem="$mode-$seed"
      t="missing"; e="missing"
      [[ -f "$output/logs/$stem.terminal" ]] && t=$(tr -d '\n' < "$output/logs/$stem.terminal")
      [[ -f "$output/logs/$stem.exit" ]] && e=$(tr -d '\n' < "$output/logs/$stem.exit")
      r="absent"; [[ -f "$output/$stem.json" ]] && r="present"
      printf '%s|%s|%s|%s\n' "$stem" "$t" "$e" "$r"
    done
  done
} > "$status/task-markers.psv"
echo "receipts present: $(grep -c '|present$' "$status/task-markers.psv" || true) of 24"

# 3. Covered geometry per receipt, and the frozen criteria. Both fail closed.
cd "$checkout"
"$runtime/bin/python" - "$output" "$status" <<'PY'
import json, pathlib, sys

output, status = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
modes = ("ordinary", "injected", "shuffle")
seeds = (17, 29, 43, 59, 71, 89, 101, 113)
report = {"receipts": {}, "geometry_ok": True, "missing": []}
for mode in modes:
    for seed in seeds:
        stem = f"{mode}-{seed}"
        path = output / f"{stem}.json"
        if not path.exists():
            report["missing"].append(stem)
            report["geometry_ok"] = False
            continue
        receipt = json.loads(path.read_text())
        geometry = receipt.get("covered_geometry")
        ok = bool(geometry) and all(
            split.get("padded_positions") == 0
            and split.get("typed_tokens_per_row") == 4
            for split in geometry.values()
        )
        report["receipts"][stem] = {
            "terminal": receipt.get("terminal"),
            "covered_geometry": geometry,
            "geometry_ok": ok,
        }
        if not ok:
            report["geometry_ok"] = False
(status / "geometry.json").write_text(json.dumps(report, indent=2) + "\n")
print("geometry verified for", len(report["receipts"]), "receipts; ok =", report["geometry_ok"])
if report["missing"]:
    print("MISSING receipts:", ", ".join(report["missing"]))
PY

# 4. The unchanged frozen criteria, plus the reported compute block. The reducer
#    refuses an incomplete matrix, so a partial run cannot yield a verdict here.
"$runtime/bin/python" nd-unfolding/pet/direct_token_comparison/summarize_runs.py \
  "$output" > "$status/summary.json" 2> "$status/summary.err"
echo "reducer exit=$? (nonzero is expected and correct for an incomplete matrix)"

# 5. A single machine-readable marker a future session can read first.
"$runtime/bin/python" - "$status" "$array" <<'PY'
import json, pathlib, sys
status, array = pathlib.Path(sys.argv[1]), sys.argv[2]
summary = status / "summary.json"
decision = None
if summary.exists() and summary.stat().st_size:
    try:
        decision = json.loads(summary.read_text()).get("decision")
    except json.JSONDecodeError:
        decision = None
geometry = json.loads((status / "geometry.json").read_text())
marker = {
    "array": array,
    "closeout_complete": True,
    "receipts_found": len(geometry["receipts"]),
    "receipts_expected": 24,
    "missing_receipts": geometry["missing"],
    "covered_geometry_ok": geometry["geometry_ok"],
    "reducer_decision": decision,
    "reducer_ran": decision is not None,
    "review_required": True,
    "non_claim": "A recorder, not a decision. The reducer applies the unchanged frozen criteria; NO_PASS may be inconclusive or a safeguard failure and is never a statement of inferiority. Nothing here authorizes adoption.",
}
(status / "CLOSEOUT.json").write_text(json.dumps(marker, indent=2) + "\n")
print("CLOSEOUT:", json.dumps(marker))
PY
echo "closeout finished $(date -u +%FT%TZ)"
