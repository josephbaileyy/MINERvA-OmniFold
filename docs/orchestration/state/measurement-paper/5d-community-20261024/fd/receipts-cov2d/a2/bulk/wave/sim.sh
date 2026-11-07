#!/bin/bash
# Local dry run of connect-wave.sh: a fake deploy (git repo with stub env/gate/submit), a fake sacct that lists a new
# job only after LAG polls, fake scontrol. Usage: sim.sh <scenario-dir> <lag> <tries> <spent_s>
set -u
S=$(cd "$(dirname "$0")/.." && pwd); T=$1; LAG=$2; TRIES=$3; SPENT=$4
rm -rf "$T"; mkdir -p "$T/bin" "$T/W" "$T/O/tables" "$T/O/out" "$T/C/2d-unfolding/cov2d/jobs"
cp "$S/wt-wave/cov2d_cap.py" "$S/wt-wave/test_cov2d_cap.py" "$T/W/"
for t in G18 AR23; do
  printf 'job\tlanes\tlane_cpus\truns\tlongest_lane_s\twall_s\tlimit\n' > "$T/O/tables/jobs_$t.tsv"
  printf '%s_L\t2\t128\t11\t1\t1\t03:20:00\n' $t >> "$T/O/tables/jobs_$t.tsv"
  for x in a b c; do printf '%s_B%s\t4\t64\t100\t1\t1\t08:06:00\n' $t $x >> "$T/O/tables/jobs_$t.tsv"; done
  for x in a b c; do printf '%s_T%s\t4\t64\t100\t1\t1\t07:38:00\n' $t $x >> "$T/O/tables/jobs_$t.tsv"; done
  printf 'job\tlane\tlabel\tcpus\tscript\targs\test_s\n' > "$T/O/tables/runs_$t.tsv"
  for j in L Ba Bb Bc Ta Tb Tc; do for k in 1 2 3; do printf '%s_%s\t%s_%s.1\tR_%s_%s_%d\t64\tre2\t--x\t1\n' $t $j $t $j $t $j $k >> "$T/O/tables/runs_$t.tsv"; done; done
done
for h in ${HIT:-}; do mkdir -p "$T/O/out/$h"; done
J=$T/C/2d-unfolding/cov2d/jobs
cat > $J/cov2d_env.sh <<EOS
O=$T/O
PY310=$(command -v python3)
CJ=\$C/2d-unfolding/cov2d/jobs/fake_gate.py
EOS
cat > $J/fake_gate.py <<'EOS'
import sys, json, pathlib
a = dict(zip(sys.argv[2::2], sys.argv[3::2]))
lim = {}
for f in pathlib.Path(a["--tables"]).glob("jobs_*.tsv"):
    for ln in f.read_text().splitlines()[1:]:
        r = ln.split("\t"); lim[r[0]] = r[6]
lim["U"] = "08:54:00"
hms = lambda t: sum(int(x) * k for x, k in zip(t.split(":"), (3600, 60, 1)))
spent = held = 0.0
for ln in open(a["--sacct"]).read().splitlines():
    _, name, state, el, n = ln.split("|")[:5]
    if not name.startswith("cov2d-"): continue
    if state in ("PENDING", "RUNNING"): held += hms(lim[name[6:]]) / 3600
    else: spent += int(el) / 3600
t = spent + held + hms(lim[a["--want"]]) / 3600
print(json.dumps({"spent": spent, "held": held, "total": t, "pass": t <= 165.8})); sys.exit(0 if t <= 165.8 else 3)
EOS
cat > $J/cov2d_submit.sh <<EOS
#!/bin/bash
C=\$1; M=\$2; TRUTH=\$3; job=\$4
id=\$((1000 + \$(wc -l < $T/O/submissions.log)))
lim=\$(awk -F'\t' -v j="\$job" 'NR > 1 && \$1 == j {print \$7}' $T/O/tables/jobs_\$TRUTH.tsv)
echo "\$(date -u +%FT%TZ) M=\$M job=\$job id=\$id limit=\$lim" | tee -a $T/O/submissions.log
echo "\$id|cov2d-\$job|PENDING|0|1|\$(( 10#\$(echo \$lim | cut -d: -f1)*60 + 10#\$(echo \$lim | cut -d: -f2) ))|0" >> $T/pendingq
EOS
(cd $T/C && git init -q && git add -A && git -c user.email=x@y -c user.name=x commit -qm stub && git init -q --bare ../origin.git && git remote add origin ../origin.git && git push -q origin HEAD:main)
M=$(git -C $T/C rev-parse HEAD)
# eight universe jobs at M (pending, already listed by sacct) and the spent attempts
: > $T/O/submissions.log; : > $T/listed; : > $T/pendingq
echo "1|cov2d-pseudo_G18|COMPLETED|$SPENT|1|180" >> $T/listed
for i in 1 2 3 4 5 6 7 8; do echo "2026 M=$M job=U id=90$i limit=08:54:00" >> $T/O/submissions.log; [ -n "${U_HIDDEN:-}" ] || echo "90$i|cov2d-U|PENDING|0|1|534" >> $T/listed; done
cat > $T/bin/sacct <<EOS
#!/bin/bash
# promote queued rows whose poll count reached LAG
: > $T/pq2
while IFS='|' read -r id n st el nn tl c; do
  [ -z "\$id" ] && continue
  c=\$((c + 1)); if [ "\$c" -ge $LAG ] && [ $LAG -ge 0 ]; then echo "\$id|\$n|\$st|\$el|\$nn|\$tl" >> $T/listed; else echo "\$id|\$n|\$st|\$el|\$nn|\$tl|\$c" >> $T/pq2; fi
done < $T/pendingq; mv $T/pq2 $T/pendingq
if [[ " \$* " == *" -j "* ]]; then id=\$(echo "\$*" | sed -E 's/.*-j ([0-9]+).*/\1/'); grep -q "^\$id|" $T/listed && echo "\$id"; exit 0; fi
cat $T/listed
EOS
printf '#!/bin/bash\necho "JobId=$3 QOS=fake"\n' > $T/bin/scontrol
printf '#!/bin/bash\nshasum -a 256 "$@"\n' > $T/bin/sha256sum
chmod +x $T/bin/*
sed -e "s|^M=.*|M=$M|" -e "s|^C=.*|C=$T/C|" -e "s|^W=.*|W=$T/W|" -e "s|^LOG=.*|LOG=$T/wave.log|" \
    -e "s|^WAIT_POLL=10; WAIT_TRIES=60|WAIT_POLL=0; WAIT_TRIES=$TRIES|" -e "s|/usr/bin/python3|$(command -v python3)|g" \
    "$S/wt-wave/connect-wave.sh" > $T/connect.sh
diff <(sed -n '19,26p' "$S/wt-wave/connect-wave.sh") <(sed -n '19,26p' $T/connect.sh) | grep '^[<>]' | cut -c1-90
[ -n "${TAMPER:-}" ] && sed -i '' 's/        if kv\["id"\] not in listed:/        if False:/' $T/W/cov2d_cap.py
case "${SELF:-good}" in good) A1=$(shasum -a 256 $T/connect.sh | cut -c1-64) ;; none) A1="" ;; bad) A1=0000 ;; esac
PATH=$T/bin:$PATH bash $T/connect.sh $A1
if [ -n "${RERUN:-}" ]; then mv $T/wave.log $T/wave1.log; PATH=$T/bin:$PATH bash $T/connect.sh $A1; fi
grep -E "LABELS|TOTALS|WAVE-END|REFUSED|sacct lists|skip|submit .* rc|companion|sha256|DIGESTS" $T/wave.log | cut -c1-260
echo "submitted at M (non-U): $(grep -c -v 'job=U ' $T/O/submissions.log)"
