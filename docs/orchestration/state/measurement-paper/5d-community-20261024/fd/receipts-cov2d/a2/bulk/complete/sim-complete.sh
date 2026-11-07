#!/bin/bash
# Local dry run of connect-complete.sh: a stub deploy (env, fake gate, stub submit, cov2d_jobs with M's limit_of
# verbatim and a plain-sha noatime_sha256), the real runs_G18.tsv, fake pilot products with their SHA256SUMS.pilot
# lines, a fake sacct (states per id; a listing for the cap), GNU-stat emulation.
# Usage: sim-complete.sh <scenario-dir> <spent_s>; env: STATE_UA (default FAILED|1:0), TAMPER_PROD, DST_EXISTS,
# ALREADY_SUBMITTED, TABLES_EXIST, SELF (good|none|bad), TAMPER_CAP, EXTRA_FILE; B1: RUNFAIL, BADSTEP, BADWALL,
# SHORTWALL, WRONGSKIP, UNMAPPED; RACE (the 2nd listing adds a held job), RESUME (a 2nd run), PARTIAL
set -u
S=$(cd "$(dirname "$0")/.." && pwd); T=$1; SPENT=$2
M_REAL=a60547692df5f963e428cdfe4661fc51ab785b7b
rm -rf "$T"; mkdir -p "$T/bin" "$T/W" "$T/O/tables" "$T/O/out" "$T/O/pseudo/G18/b" "$T/C/2d-unfolding/cov2d/jobs"
cp "$S/wt-wave/cov2d_cap.py" "$S/wt-wave/test_cov2d_cap.py" "$T/W/"
cp "$S/wavefetch/runs_G18.tsv" "$T/O/tables/runs_G18.tsv"
printf 'job\tlanes\tlane_cpus\truns\tlongest_lane_s\twall_s\tlimit\n%s\n' "G18_L	2	128	11	1	1	03:20:00" > "$T/O/tables/jobs_G18.tsv"
for j in Ba Ta; do printf 'G18_%s\t4\t64\t100\t1\t1\t08:06:00\n' $j >> "$T/O/tables/jobs_G18.tsv"; done
echo '{"verdict": "PASS"}' > "$T/O/pseudo/G18/b/pseudo_b.json"
: > "$T/O/SHA256SUMS.pilot.1"; : > "$T/O/SHA256SUMS.pilot.2"; : > "$T/O/SHA256SUMS.pilot.3"
k=0
for l in L_G18_BeamAngleX_0 X_G18 T_G18_5720000 B_G18_001 U_G18_Flux_0; do
  k=$((k % 3 + 1)); mkdir -p "$T/O/out/$l"; head -c 4096 /dev/urandom > "$T/O/out/$l/xsec.root"
  (cd "$T/O/out" && shasum -a 256 "$l/xsec.root") >> "$T/O/SHA256SUMS.pilot.$k"
done
mkdir -p "$T/O/out/P2b_ER" && echo x > "$T/O/out/P2b_ER/xsec.root"            # a pilot label no bulk job has
[ -n "${TAMPER_PROD:-}" ] && echo tampered >> "$T/O/out/$TAMPER_PROD/xsec.root"
[ -n "${DST_EXISTS:-}" ] && mkdir -p "$T/O/out/$DST_EXISTS.pilot-60857636"
[ -n "${EXTRA_FILE:-}" ] && echo x > "$T/O/out/$EXTRA_FILE/extra.txt"
[ -n "${TABLES_EXIST:-}" ] && : > "$T/O/tables/jobs_G18C.tsv"
[ -n "${PARTIAL:-}" ] && ln -s G18 "$T/O/pseudo/G18C"
J=$T/C/2d-unfolding/cov2d/jobs
cat > $J/cov2d_env.sh <<EOS
O=$T/O
PY310=$(command -v python3)
CJ=\$C/2d-unfolding/cov2d/jobs/fake_gate.py
EOS
{ echo "import hashlib, math"; echo "PREFLIGHT_S = 300"
  git -C "$S/wt-unirc" show $M_REAL:2d-unfolding/cov2d/jobs/cov2d_jobs.py | awk '/^def limit_of/{p=1} p&&/^$/{exit} p'
  printf 'def noatime_sha256(path):\n    return hashlib.sha256(open(path, "rb").read()).hexdigest()\n'; } > $J/cov2d_jobs.py
cat > $J/fake_gate.py <<'EOS'
import sys, json, pathlib
a = dict(zip(sys.argv[2::2], sys.argv[3::2]))
lim = {"U": "08:54:00", "G18_Ua": "08:54:00", "pseudo_G18": "03:00:00"}
for f in pathlib.Path(a["--tables"]).glob("jobs_*.tsv"):
    for ln in f.read_text().splitlines()[1:]:
        r = ln.split("\t"); lim[r[0]] = r[6]
hms = lambda t: sum(int(x) * k for x, k in zip(t.split(":"), (3600, 60, 1)))
spent = held = 0.0
for ln in open(a["--sacct"]).read().splitlines():
    _, name, state, el, n = ln.split("|")[:5]
    if not name.startswith("cov2d-"): continue
    if name[6:] not in lim: print("unknown " + name); sys.exit(2)
    if state in ("PENDING", "RUNNING"): held += hms(lim[name[6:]]) / 3600
    else: spent += int(el) / 3600
t = spent + held + hms(lim[a["--want"]]) / 3600
print(json.dumps({"spent": spent, "held": held, "total": t, "pass": t <= 165.8})); sys.exit(0 if t <= 165.8 else 3)
EOS
cat > $J/cov2d_submit.sh <<EOS
#!/bin/bash
C=\$1; M=\$2; TRUTH=\$3; job=\$4
lim=\$(awk -F'\t' -v j="\$job" 'NR > 1 && \$1 == j {print \$7}' $T/O/tables/jobs_\$TRUTH.tsv)
[ -n "\$lim" ] || { echo "stub submit: \$job is not a jobs_\$TRUTH.tsv row"; exit 2; }
[ -f $T/O/pseudo/\$TRUTH/b/pseudo_b.json ] || { echo "stub submit: no pseudo_b.json for DATA_TRUTH=\$TRUTH"; exit 2; }
echo "stub submit: runs rows \$(awk -F'\t' -v j="\$job" 'NR > 1 && \$1 == j' $T/O/tables/runs_\$TRUTH.tsv | wc -l)"
echo "\$(date -u +%FT%TZ) M=\$M job=\$job id=7777 limit=\$lim" | tee -a $T/O/submissions.log
EOS
(cd $T/C && git init -q && git add -A && git -c user.email=x@y -c user.name=x commit -qm stub && git init -q --bare ../origin.git && git remote add origin ../origin.git && git push -q origin HEAD:main)
M=$(git -C $T/C rev-parse HEAD)
: > $T/O/submissions.log
mkdir -p $T/O/logs
for e in G18_L:60895948:L_G18_BeamAngleX_0,X_G18 G18_Ua:60895562:U_G18_Flux_0 G18_Ba:60895949:B_G18_001 G18_Ta:60895956:T_G18_5720000; do
  IFS=: read -r job id sk <<<"$e"
  [ "${UNMAPPED:-}" = "$job" ] || echo "2026-11-06T09:10:00Z M=$M job=$job id=$id limit=08:00:00" >> $T/O/submissions.log
  { echo "[cov2d] start 2026-11-06T10:00:00Z job=$id JOB=$job node=nid0"
    for l in $(tr ',' ' ' <<<"$sk"); do echo "[cov2d] $l exists; not overwritten"; done
    [ "${WRONGSKIP:-}" = "$job" ] && echo "[cov2d] B_G18_099 exists; not overwritten"
    [ "${RUNFAIL:-}" = "$job" ] && echo "[cov2d] B_G18_050 rc=1"
    echo "[cov2d] end 2026-11-06T12:00:00Z rc=1"; } > $T/O/logs/cov2d-$job-$id.out
  awk -F'\t' -v j="$job" -v sk=",$sk," 'NR > 1 && $1 == j && index(sk, "," $3 ",") == 0 {print $3 "\t1\t2\t0"}' $T/O/tables/runs_G18.tsv > $T/O/walls.$job.1.tsv
  [ "${BADWALL:-}" = "$job" ] && sed -i '' '1s/\t0$/\t1/' $T/O/walls.$job.1.tsv
  [ "${SHORTWALL:-}" = "$job" ] && sed -i '' '1d' $T/O/walls.$job.1.tsv
  { echo "$id.batch|FAILED|1:0"; echo "$id.extern|COMPLETED|0:0"
    for k in 0 1 2; do echo "$id.$k|COMPLETED|0:0"; done
    [ "${BADSTEP:-}" = "$job" ] && echo "$id.3|FAILED|1:0"; } > $T/steps.$id
done
[ -n "${ALREADY_SUBMITTED:-}" ] && echo "2026 M=$M job=G18_C id=7000 limit=01:19:00" >> $T/O/submissions.log
cat > $T/states <<EOS
60895948|FAILED|1:0
60895562|${STATE_UA:-FAILED|1:0}
60895949|FAILED|1:0
60895956|FAILED|1:0
EOS
{ echo "1|cov2d-pseudo_G18|COMPLETED|$SPENT|1|180"
  echo "60895948|cov2d-G18_L|FAILED|6506|1|200"; echo "60895562|cov2d-G18_Ua|$(cut -d'|' -f1 <<<"${STATE_UA:-FAILED|1:0}")|25000|1|534"
  echo "60895949|cov2d-G18_Ba|FAILED|22000|1|486"; echo "60895956|cov2d-G18_Ta|FAILED|21000|1|458"; } > $T/listed
cat > $T/bin/sacct <<EOS
#!/bin/bash
if [[ " \$* " == *" -o JobID,State,ExitCode"* ]]; then id=\$(echo "\$*" | sed -E 's/.*-j ([0-9]+).*/\1/'); cat $T/steps.\$id; exit 0; fi
if [[ " \$* " == *" -o JobID "* ]]; then id=\$(echo "\$*" | sed -E 's/.*-j ([0-9]+).*/\1/'); cut -d'|' -f1 $T/steps.\$id; exit 0; fi
if [[ " \$* " == *" -o State,ExitCode"* ]]; then id=\$(echo "\$*" | sed -E 's/.*-j ([0-9]+).*/\1/'); grep "^\$id|" $T/states | cut -d'|' -f2-; exit 0; fi
n=\$((\$(cat $T/nlist 2>/dev/null || echo 0) + 1)); echo \$n > $T/nlist
cat $T/listed
[ -n "${RACE:-}" ] && [ "\$n" = 2 ] && echo "999|cov2d-G18_Ba|RUNNING|0|1|486"
exit 0
EOS
printf '#!/bin/bash\necho "JobId=$3 QOS=fake TimeLimit=fake"\n' > $T/bin/scontrol
printf '#!/bin/bash\nshasum -a 256 "$@"\n' > $T/bin/sha256sum
cat > $T/bin/stat <<'EOS'
#!/usr/bin/env python3
import os, sys, datetime
assert sys.argv[1] == "-c"
fmt, path = sys.argv[2], sys.argv[3]
s = os.stat(path)
out = fmt.replace("%n", path).replace("%s", str(s.st_size)).replace("%Y", str(int(s.st_mtime))).replace("%i", str(s.st_ino))
print(out.replace("%y", datetime.datetime.fromtimestamp(s.st_mtime).isoformat()))
EOS
chmod +x $T/bin/*
sed -e "s|^M=.*|M=$M|" -e "s|^C=.*|C=$T/C|" -e "s|^W=.*|W=$T/W|" -e "s|^LOG=.*|LOG=$T/complete.log|" \
    -e "s|/usr/bin/python3|$(command -v python3)|g" "$S/wt-wave/connect-complete.sh" > $T/connect.sh
[ -n "${TAMPER_CAP:-}" ] && echo "# x" >> $T/W/cov2d_cap.py
case "${SELF:-good}" in good) A1=$(shasum -a 256 $T/connect.sh | cut -c1-64) ;; none) A1="" ;; bad) A1=0000 ;; esac
PATH=$T/bin:$PATH bash $T/connect.sh $A1
if [ -n "${RESUME:-}" ]; then mv $T/complete.log $T/complete1.log; grep -E "MODE|WAIT|REFUSED" $T/complete1.log | sed "s/^/run1: /"; PATH=$T/bin:$PATH bash $T/connect.sh $A1; fi
grep -E "MODE|RESUME |MATCH the|REFUSED|WAIT|PRECHECK|TOTALS|LABELS|MV |submit |id=|lanes |stub submit|DIGESTS" $T/complete.log | cut -c1-220
echo "renamed: $(ls $T/O/out | grep -c 'pilot-60857636$') | originals left: $(for l in L_G18_BeamAngleX_0 X_G18 T_G18_5720000 B_G18_001 U_G18_Flux_0; do [ -e $T/O/out/$l ] && echo $l; done | wc -l | tr -d ' ') | tables: $(ls $T/O/tables | grep -c G18C) | symlink: $(readlink $T/O/pseudo/G18C || echo none) | ledger rows: $( [ -f $T/O/renames-pilot-60857636.tsv ] && tail -n +2 $T/O/renames-pilot-60857636.tsv | wc -l | tr -d ' ' || echo none) | G18_C submitted: $(grep -c 'job=G18_C id=7777' $T/O/submissions.log)"
