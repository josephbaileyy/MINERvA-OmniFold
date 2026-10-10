#!/bin/bash
# XR submission:  xr_submit.sh ADMISSION RUN [RUN ...]
#
# Re-verifies the admission (binding, clean HEAD, environment digest), then for each RUN takes the
# next attempt number from xr_admit.py next-attempt (refusing a kind's total attempt cap, which
# counts failed and cancelled attempts, and any rerun of a completed run), refuses a RUN that
# still has a queued or running job, creates its attempt directory exclusively and submits it with
# the frozen kind's settings. Every submission is appended to <outroot>/submissions.jsonl. A failed
# or non-numeric sbatch reply cancels this invocation's queued jobs and exits non-zero; the
# operator then checks `squeue --me --name xr_<RUN>_a<N>` for an orphan whose id was not returned.
set -eo pipefail
ADM="$1"; shift || true
[ -n "$ADM" ] && [ "$#" -gt 0 ] || { echo "usage: xr_submit.sh ADMISSION RUN [RUN ...]" >&2; exit 2; }
PY=/usr/bin/python3
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
"$PY" "$HERE/xr_admit.py" verify --admission "$ADM"
field() { "$PY" -c 'import json,sys
d=json.load(open(sys.argv[1]))
for k in sys.argv[2].split("."): d=d[k]
print(d)' "$@"; }
OUTROOT=$(field "$ADM" outroot)
CHECKOUT=$(field "$ADM" checkout)
[ "$HERE" = "$CHECKOUT/docs/orchestration/state/next-preparation-20261009/two-d-followup/xr" ] || { echo "REFUSED: not the admitted checkout" >&2; exit 3; }
mkdir -p "$OUTROOT"
touch "$OUTROOT/submissions.jsonl"
QUEUED=()
on_error() { for j in "${QUEUED[@]}"; do scancel "$j" || true; done; echo "[xr-submit] FAILED; cancelled: ${QUEUED[*]:-none}" >&2; }
trap on_error ERR
for RUN in "$@"; do
  KIND=$("$PY" -c 'import json,sys; print(json.load(open(sys.argv[1]))["runs"][sys.argv[2]]["kind"])' "$HERE/manifest/runs.json" "$RUN")
  k() { field "$HERE/manifest/runs.json" "kinds.$KIND.$1"; }
  PREV=$("$PY" -c 'import json,sys
ids=[str(json.loads(l)["job_id"]) for l in open(sys.argv[1]) if l.strip() and json.loads(l)["run"]==sys.argv[2]]
print(",".join(ids))' "$OUTROOT/submissions.jsonl" "$RUN")
  if [ -n "$PREV" ] && [ -n "$(squeue -h -j "$PREV" -o %i 2>/dev/null)" ]; then
    echo "REFUSED: $RUN still has a queued or running job ($PREV)" >&2; exit 3
  fi
  ATT=$("$PY" "$HERE/xr_admit.py" next-attempt --admission "$ADM" --run "$RUN")
  DIR="$OUTROOT/$RUN/a$ATT"
  mkdir -p "$OUTROOT/$RUN"
  mkdir "$DIR"
  REPLY=$(sbatch --parsable --account=m3246 --qos="$(k qos)" --constraint="$(k constraint)" --nodes=1 --ntasks=1 \
          --cpus-per-task="$(k cpus_per_task)" --mem="$(k mem_mb)M" --time="$(k time)" \
          --job-name="xr_${RUN}_a${ATT}" --output="$DIR/slurm-%j.out" --error="$DIR/slurm-%j.err" \
          "$HERE/launch/xr_job.sbatch" "$ADM" "$RUN" "$ATT")
  JID="${REPLY%%;*}"
  [[ "$JID" =~ ^[0-9]+$ ]] || { echo "non-numeric sbatch reply: $REPLY" >&2; false; }
  QUEUED+=("$JID")
  printf '{"run": "%s", "kind": "%s", "attempt": %s, "job_id": %s, "submitted_utc": "%s", "dir": "%s"}\n' \
      "$RUN" "$KIND" "$ATT" "$JID" "$(date -u +%FT%TZ)" "$DIR" >> "$OUTROOT/submissions.jsonl"
  echo "[xr-submit] $RUN a$ATT -> job $JID"
done
trap - ERR
