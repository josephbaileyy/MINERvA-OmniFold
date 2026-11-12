#!/bin/bash
# COV2D-G2R: submit ONE named job, only after addendum J1, on origin/main, names the deploy's commit M (J1's M line).
# The director is told first.
#     bash g2r_submit.sh <deploy> <M> <job>      (a job of jobs_g2r.tsv)
# One job per call (the director's sacct-lag ruling). Before the sbatch: the order (each job once; the committed
# records it needs), and the charge gate at 110 node-h over cov2dg2r-* attempts, which counts submitted ids that sacct
# does not list yet; for an unfold job it projects the whole campaign and a projection over the cap is a STOP to the
# director (rc 9). After the sbatch: the id is logged, and the call returns only once sacct lists it (10 s polls, 10
# minutes, else rc 6). Exit codes: 0 submitted; 2 deploy, binding or table problem; 3 the order or the gate refuses;
# 6 sacct never listed the id; 9 the campaign's projection passes the cap (STOP).
set -eo pipefail
[ $# = 3 ] || { echo "usage: g2r_submit.sh <deploy> <M> <job> (one job per call)"; exit 2; }
C=$(cd "$1" && pwd); M=$2; JOB=$3
source "$C/2d-unfolding/cov2d/g2r/jobs/g2r_env.sh"
g2r_deploy_ok "$C" "$M" || { echo "deploy $C is not a clean checkout at $M"; exit 2; }
git -C "$C" fetch -q origin main || { echo "the fetch of origin main failed: J1 and the records are unread"; exit 2; }
BIND=docs/orchestration/state/measurement-paper/5d-community-20261024/COV2D-G2R-BINDING-1.md
bind=$(git -C "$C" show "origin/main:$BIND") || { echo "binding 1 is not on origin/main"; exit 2; }
grep -qE "^\*\*M_J1 = \`$M\`\*\*" <<<"$bind" || { echo "COV2D-G2R-BINDING-1 on origin/main does not name $M on its M_J1 line"; exit 2; }
mkdir -p "$O/logs" "$O/tables"
chk=$(mktemp -d)
"$PY310" -B "$GJ" tables --out "$chk" > /dev/null
for f in runs_g2r.tsv jobs_g2r.tsv; do   # written once; every later submission regenerates and compares them
    if [ -s "$O/tables/$f" ]; then cmp -s "$chk/$f" "$O/tables/$f" || { rm -rf "$chk"; echo "$O/tables/$f is not this deploy's"; exit 2; }
    else cp "$chk/$f" "$O/tables/"; fi
done
rm -rf "$chk"
lim=$(awk -F'\t' -v j="$JOB" 'NR > 1 && $1 == j {print $7}' "$O/tables/jobs_g2r.tsv")
[ -n "$lim" ] || { echo "$JOB is not a jobs_g2r.tsv row"; exit 2; }
LOG=$O/submissions.log
"$PY310" -B "$GJ" order --job "$JOB" --deploy "$C" --submissions "$LOG" --o "$O" > "$O/logs/order-$JOB.json" \
    || { cat "$O/logs/order-$JOB.json"; echo "the order refuses $JOB"; exit 3; }
psv=$O/logs/gate-$JOB-$(date -u +%Y%m%dT%H%M%SZ).psv
sacct -X -n -P -S 2026-11-12 -u "$(id -un)" -o JobID,JobName,State,ElapsedRaw,NNodes > "$psv"
grc=0
"$PY310" -B "$GJ" gate --sacct "$psv" --tables "$O/tables" --submissions "$LOG" --want "$JOB" > "$psv.gate.json" || grc=$?
cat "$psv.gate.json"
[ "$grc" = 9 ] && { echo "STOP: the campaign's projection passes the cap; to the director"; exit 9; }
[ "$grc" = 0 ] || { echo "the gate refuses $JOB"; exit 3; }
mapsha=""
case "$JOB" in
    envtest) script=g2r_envtest.sbatch ;;
    prepare) script=g2r_prepare.sbatch ;;
    *) script=g2r_job.sbatch
       mapsha=$("$PY310" -B "$GJ" map-sha --deploy "$C") || { echo "no committed prepare PASS with a map sha256"; exit 3; } ;;
esac
id=$(sbatch --parsable --job-name="cov2dg2r-$JOB" --time="$lim" \
    --export=ALL,C=$C,M=$M,JOB=$JOB,MAPSHA=$mapsha "$C/2d-unfolding/cov2d/g2r/jobs/$script")
id=${id%%;*}
[[ $id =~ ^[0-9]+$ ]] || { echo "sbatch returned no job id: '$id'"; exit 2; }
echo "$(date -u +%FT%TZ) M=$M job=$JOB id=$id limit=$lim" | tee -a "$LOG"
for _ in $(seq 60); do
    sacct -X -n -P -j "$id" -o JobID | grep -qx "$id" && { echo "sacct lists $id"; exit 0; }
    sleep 10
done
echo "sacct did not list $id within 10 minutes: report it before any other submission"
exit 6
