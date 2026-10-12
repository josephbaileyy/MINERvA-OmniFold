#!/bin/bash
# XR submission:  [XR_DIAGNOSIS="..."] xr_submit.sh ADMISSION RUN [RUN ...]
#
# Re-verifies the admission (binding, clean HEAD, environment digests), then for each RUN takes the
# next attempt number from xr_admit.py next-attempt, which refuses a kind's total attempt cap in this
# amendment (the largest of the attempt directories, the submissions record and every
# <prefix>_* job sacct lists for this user since cumulative_since; failed and cancelled attempts
# count), sacct not showing exactly the prior grant's xr_* jobs, a run out of release order
# (preflight, then L0, then the rest), a planned cumulative ceiling over the cap, any rerun of a
# completed run, a spare attempt (a run's second) without a stated diagnosis in XR_DIAGNOSIS, and
# a job that could end past the stop (72 h after the first submission).
# The stop is also given to Slurm as --deadline, so a job that cannot finish before it is never
# started. A RUN that still has a queued or running job is refused. The attempt directory is
# created exclusively and the job submitted with the frozen kind's settings. Every submission is
# appended to <outroot>/submissions.jsonl. A failed or non-numeric sbatch reply cancels this
# invocation's queued jobs and exits non-zero; the operator then checks
# `squeue --me --name <prefix>_<RUN>_a<N>` for an orphan whose id was not returned.
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
[ "$HERE" = "$CHECKOUT/docs/orchestration/state/next-preparation-20261009/xr-linux/xr" ] || { echo "REFUSED: not the admitted checkout" >&2; exit 3; }
[ -d "$OUTROOT" ] && [ ! -L "$OUTROOT" ] || { echo "REFUSED: the admitted outroot $OUTROOT is missing" >&2; exit 3; }
SINCE=$(field "$ADM" cumulative_since)
PREFIX=$(field "$ADM" job_name_prefix)
SACCT=$(mktemp "${TMPDIR:-/tmp}/xr-sacct.XXXXXX")
trap 'rm -f "$SACCT"' EXIT
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
  sacct -u "$(id -un)" -X -n -P -S "$SINCE" -E now --format=JobID,JobName,State > "$SACCT"
  read -r ATT DEADLINE < <("$PY" "$HERE/xr_admit.py" next-attempt --admission "$ADM" --run "$RUN" --sacct "$SACCT" \
                               --diagnosis "${XR_DIAGNOSIS:-}")
  [[ "$ATT" =~ ^[0-9]+$ ]] && [ -n "$DEADLINE" ] || { echo "REFUSED: no attempt for $RUN" >&2; exit 3; }
  DIR="$OUTROOT/$RUN/a$ATT"
  mkdir -p "$OUTROOT/$RUN"
  mkdir "$DIR"
  REPLY=$(sbatch --parsable --account=m3246 --qos="$(k qos)" --constraint="$(k constraint)" --nodes=1 --ntasks=1 \
          --cpus-per-task="$(k cpus_per_task)" --mem="$(k mem_mb)M" --time="$(k time)" --deadline="$DEADLINE" \
          --job-name="${PREFIX}_${RUN}_a${ATT}" --output="$DIR/slurm-%j.out" --error="$DIR/slurm-%j.err" \
          "$HERE/launch/xr_job.sbatch" "$ADM" "$RUN" "$ATT")
  JID="${REPLY%%;*}"
  [[ "$JID" =~ ^[0-9]+$ ]] || { echo "non-numeric sbatch reply: $REPLY" >&2; false; }
  QUEUED+=("$JID")
  "$PY" -c 'import json,sys; print(json.dumps({"run": sys.argv[1], "kind": sys.argv[2], "attempt": int(sys.argv[3]),
      "job_id": int(sys.argv[4]), "submitted_utc": sys.argv[5], "dir": sys.argv[6], "diagnosis": sys.argv[7] or None}))' \
      "$RUN" "$KIND" "$ATT" "$JID" "$(date -u +%FT%TZ)" "$DIR" "${XR_DIAGNOSIS:-}" >> "$OUTROOT/submissions.jsonl"
  echo "[xr-submit] $RUN a$ATT -> job $JID"
done
trap - ERR
