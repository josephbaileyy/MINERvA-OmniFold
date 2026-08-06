#!/bin/bash
# Fired by wakerctl when the D2 powered-closure slurm job leaves the queue.
#
# usage: notify_pwclosure.sh <job_id>
# The job id is a PARAMETER, not a constant. It was hardcoded to 56355818 until 2026-08-06, when that
# job was cancelled and re-submitted at niter=3 -- at which point a hardcoded notifier would have
# reported sacct for a dead job and mailed the wrong id. Re-runs are expected here; do not inline it.
#
# WHY THIS EXISTS: a Claude session cron loop is in-memory and dies with the session. wakerctl runs as
# a Slurm cron job (qos=cron) and its mail path is proven, so this reports the campaign critical-path
# verdict to Joseph even if nothing else is alive.
#
# It reports the OUTCOME, not merely that the job ended. A notifier that says only "job finished" is
# the vacuous-pass defect wearing a different hat.
set -uo pipefail
JOB="${1:?usage: notify_pwclosure.sh <job_id>}"
REPO=/pscratch/sd/j/josephrb/MINERvA-OmniFold
OUT="$REPO/nd-unfolding/pet/powered_closure"
BODY=/pscratch/sd/j/josephrb/.pwclosure_notify_body.txt

{
  echo "The D2 powered truth-reweight closure (job ${JOB}) has left the queue."
  echo "Fired by wakerctl on $(hostname) at $(date -u +%Y-%m-%dT%H:%M:%SZ), independent of any Claude session."
  echo
  echo "This run is at niter=3 (NOMINAL_SEED_POLICY changed 2026-08-06). A niter=2 report would be"
  echo "rejected by powered:nominal_configuration, which is why 56355818 was cancelled and re-run."
  echo
  echo "=== sacct ==="
  sacct -j "$JOB" --format=JobID,State,Elapsed,ExitCode,MaxRSS -P 2>/dev/null | head -6
  echo
  echo "=== sentinel (records the verdict, not just completion) ==="
  s=$(ls -1t "$OUT"/DONE.*.txt 2>/dev/null | head -1)
  if [[ -n "${s:-}" ]]; then cat "$s"; else echo "NO SENTINEL -- the job died before writing one."; fi
  echo
  echo "=== acceptance criteria ==="
  r=$(ls -1t "$OUT"/POWERED_CLOSURE_REPORT.*.json 2>/dev/null | head -1)
  if [[ -n "${r:-}" ]]; then
    /usr/bin/python3.11 - "$r" <<"PY"
import json, sys
d = json.load(open(sys.argv[1]))
for k in ("verdict", "gap", "floor", "residual", "floor_over_gap", "residual_over_gap", "recovery"):
    if k in d:
        print(f"  {k} = {d[k]}")
cfg = d.get("configuration") or {}
print(f"  configuration.niter = {cfg.get(\"niter\")}  (must be 3, or the gate rejects it)")
print("  thresholds: gap>=0.15  floor/gap<=0.10  residual/gap<=0.20")
PY
  else
    echo "  NO REPORT -- gap/floor were already receipted at 0.2343 / 0.0459, so the missing number is residual."
  fi
  echo
  echo "Preflight receipts already on disk (training-independent, so they stand regardless):"
  echo "  PREFLIGHT_GAP_FLOOR.json (gap 0.2343, floor/gap 0.0459)"
  echo
  echo "Log: nd-unfolding/pet/AUTONOMOUS_LOG_20260805.md"
} > "$BODY" 2>&1

/usr/bin/python3.11 /pscratch/sd/j/josephrb/send_channel_mail.py \
  "[MNV-AUTO] powered closure ${JOB} left the queue (wakerctl)" "$BODY"
