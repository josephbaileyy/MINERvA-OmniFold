#!/bin/bash
# Director throughput watch (2026-10-17 msg after a27bcedb). Production K-packs = 2dc_P_K* submitted >= 2026-10-16T21:00Z.
# Exits (each = report to the director; none is a STOP, none authorizes a change):
#  21 NOSTART   no K-pack STARTED for 8 h while some are still PENDING (clock from max(latest Start, 21:08:56Z launch))
#  22 LOW24     fewer than 30 K-packs COMPLETED in the last 24 h while some are not terminal (checked from 10-17T21:09Z)
#  23 C_1019    at/after 2026-10-19T00:00Z more than 45 K-packs not terminal (fires once; skipped if $SEEN_C set)
#  24 DLPEND    a PENDING K-pack with squeue Reason DeadLine (State DEADLINE is caught by pack_watch.sh ABNORMAL)
#  20 DONE      no K-pack left non-terminal
#  25 READFAIL any poll where ssh, sacct or squeue fails (rc != 0 or error text), or the sacct K-pack total != $NTOTAL
#               (136): exits at once, never counted as a quiet queue (director addition (e)). TU/TS override the sacct
#               user/starttime for the one-off firing test only.
SLEEP=${SLEEP:-900}; NTOTAL=${NTOTAL:-136}; TU=${TU:-josephrb}; TS=${TS:-2026-10-16T21:00:00}
while :; do
  out=$(ssh -o ConnectTimeout=30 -o BatchMode=yes saul.nersc.gov "TU=$TU TS=$TS NTOTAL=$NTOTAL"' TZ=UTC python3 - <<"PY"
import os
import subprocess, datetime as D
U=D.timezone.utc
def P(s):
    try: return D.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=U)
    except Exception: return None
r = subprocess.run(["sacct","-X","-n","-P","-S",os.environ["TS"],"-E","now","-u",os.environ["TU"],
                    "-o","JobID,JobName,State,Submit,Start,End"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True,
                   env={"TZ":"UTC","PATH":"/usr/bin:/bin:/opt/slurm/default/bin"})
if r.returncode or "error" in r.stderr.lower(): print("FAIL sacct rc=%d %s" % (r.returncode, r.stderr.strip()[:200])); raise SystemExit
q = subprocess.run(["squeue","-h","-u","josephrb","-o","%i|%j|%T|%r"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
if q.returncode or "error" in q.stderr.lower(): print("FAIL squeue rc=%d %s" % (q.returncode, q.stderr.strip()[:200])); raise SystemExit
now = D.datetime.now(U)
rows = [l.split("|") for l in r.stdout.splitlines() if "|2dc_P_K" in l]
rows = [x for x in rows if P(x[3]) and P(x[3]) >= D.datetime(2026,10,16,21,0,tzinfo=U)]
if len(rows) != int(os.environ["NTOTAL"]): print("FAIL total=%d expected %s" % (len(rows), os.environ["NTOTAL"])); raise SystemExit
st = lambda x: x[2].split()[0]
nonterm = [x for x in rows if st(x) in ("PENDING","RUNNING","COMPLETING","CONFIGURING","REQUEUED","SUSPENDED")]
pend = [x for x in rows if st(x) == "PENDING"]
starts = [P(x[4]) for x in rows if P(x[4])]
last = max(starts + [D.datetime(2026,10,16,21,8,56,tzinfo=U)])
c24 = sum(1 for x in rows if st(x) == "COMPLETED" and P(x[5]) and (now - P(x[5])).total_seconds() <= 86400)
dl = [l for l in q.stdout.splitlines() if "|2dc_P_K" in l and l.split("|")[2] == "PENDING" and "deadline" in l.split("|")[3].lower()]
print("OK now=%s total=%d nonterm=%d pending=%d running=%d last_start=%s idle_h=%.2f c24=%d dlpend=%d" % (
    now.strftime("%FT%TZ"), len(rows), len(nonterm), len(pend), sum(1 for x in rows if st(x)=="RUNNING"),
    last.strftime("%FT%TZ"), (now-last).total_seconds()/3600, c24, len(dl)))
for l in dl: print("DL", l)
PY' 2>&1); rc=$?
  if [ $rc -ne 0 ] || ! printf '%s' "$out" | grep -q '^OK '; then
    echo "READFAIL $(date -u +%FT%TZ) ssh_rc=$rc"; printf '%s\n' "$out" | tail -5; exit 25
  fi
  line=$(printf '%s\n' "$out" | grep '^OK ')
  v(){ printf '%s\n' "$line" | tr ' ' '\n' | grep "^$1=" | cut -d= -f2; }
  now=$(v now); nonterm=$(v nonterm); pend=$(v pending); idle=$(v idle_h); c24=$(v c24); dlp=$(v dlpend)
  [ "$nonterm" -eq 0 ] && { echo "DONE $line"; exit 20; }
  [ "$dlp" -gt 0 ] && { echo "DLPEND $line"; printf '%s\n' "$out" | grep '^DL '; exit 24; }
  awk -v i="$idle" 'BEGIN{exit !(i>=8)}' && [ "$pend" -gt 0 ] && { echo "NOSTART $line"; exit 21; }
  [[ "$now" > "2026-10-17T21:09:00Z" ]] && [ "$c24" -lt 30 ] && { echo "LOW24 $line"; exit 22; }
  [ -z "${SEEN_C:-}" ] && [[ "$now" > "2026-10-19T00:00:00Z" || "$now" == "2026-10-19T00:00:00Z" ]] && [ "$nonterm" -gt 45 ] && { echo "C_1019 $line"; exit 23; }
  echo "$line" >> "${LOG:-/dev/null}"
  sleep "$SLEEP"
done
