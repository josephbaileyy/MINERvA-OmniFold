#!/bin/bash
# COV2D connect COMPLETE: the director's ruling on G18_L (2026-11-06, item 3). The pilot (60857636, at cb31611c) wrote
# five products under labels the bulk tables reuse, in the same $O/out, so the bound sbatch skipped them and G18_L,
# G18_Ua, G18_Ba and G18_Ta each exited 1. The pilot's products do not count for the bulk. This connect, after all four
# have ended:
#   1. checks that each of the four ended as the ruling's collision and nothing else (the auditor's B1; A3 ruling 1's
#      evidence, logged): it maps to its job in submissions.log, sacct FAILED 1:0, every srun step COMPLETED 0:0, every
#      walls run_rc 0, no run-failure line in its log, its "exists; not overwritten" labels equal to its expected set, and
#      walls rows + skips equal to its runs_G18.tsv rows. Then G18_C must not be in submissions.log, and either none of
#      the G18C tables, $O/pseudo/G18C and the rename ledger exists (fresh), or all four do (resume: this connect's own
#      earlier run renamed and installed, then WAITed at step 7; steps 3-5 are verified against its ledger, not redone);
#   2. builds the completion job's tables in $W: the five rows of runs_G18.tsv verbatim (args, cpus and est_s byte-equal;
#      only the job and lane columns rewritten), as job G18_C of table-truth G18C, two lanes; its limit is the bound
#      cov2d_jobs.limit_of of the longest lane;
#   3. prices G18_C with cov2d_cap on a sacct snapshot: over the cap, it stops with nothing changed (a wait);
#   4. verifies all five pilot products (each $O/out/<label> holds xsec.root whose O_NOATIME sha256 equals its one
#      SHA256SUMS.pilot.* line, and <label>.pilot-60857636 does not exist), then renames each with mv -n, no deletion,
#      one B9-form ledger row per label (stat and sha before and after) in $O/renames-pilot-60857636.tsv;
#   5. installs the tables in $O/tables (the gate's jobs_*.tsv glob then prices cov2d-G18_C) and the relative symlink
#      $O/pseudo/G18C -> G18 (cov2d_submit.sh exports DATA_TRUTH=$TRUTH, so the job's $D is G18's step B directory and
#      its check hashes the data files against G18's pseudo_b.json);
#   6. stat-lists G18_C's labels against $O/out (the ruling's item 4): any hit refuses;
#   7. takes one sacct snapshot, prints the gate's total and cov2d_cap's, and submits through the bound cov2d_submit.sh
#      only if both are within the cap.
# Before step 1 it compares cov2d_cap.py and test_cov2d_cap.py against the literals below, and itself ($0) against the
# sha256 passed as $1, and runs the companion test, as connect-wave.sh does. Any refusal stops the connect.
# Run on login02: setsid nohup bash /dev/shm/josephrb-cov2d-complete/connect-complete.sh <its sha256> >/dev/null 2>&1 </dev/null &
M=a60547692df5f963e428cdfe4661fc51ab785b7b
C=/pscratch/sd/j/josephrb/cov2d-deploy-a6054769
W=/dev/shm/josephrb-cov2d-complete
LOG=/dev/shm/josephrb-cov2d-complete.log
IDS="60895948 60895562 60895949 60895956"
LAYOUT="L_G18_BeamAngleX_0:1:128 X_G18:1:128 B_G18_001:1:64 U_G18_Flux_0:2:128 T_G18_5720000:2:64"   # label:lane:cpus, in run order
CJOB=G18_C; CTRUTH=G18C; SUFFIX=.pilot-60857636
CAP_SHA=1ce76ea373f474e7c32520c69fbc90eae9419d5cbd901927df5a41fbe6973c5e
TEST_SHA=7a07c3acf7f361f1af89276064bc64c8ab60e4d6bc06c658f2dcd10422f9c324
WANT_SELF=$1
[ -e "$LOG" ] && { echo "REFUSED $LOG exists"; exit 2; }
exec >> "$LOG" 2>&1
refuse() { echo "REFUSED $*"; echo DONE; exit 2; }
echo "host=$(hostname) start=$(date -u +%FT%TZ) pid=$$ user=$(id -un)"
[ "$(git -C "$C" rev-parse HEAD)" = "$M" ] || refuse "the deploy is not at M"
echo "deploy=$C head=$(git -C "$C" rev-parse HEAD) plain=$(git -C "$C" status --porcelain | wc -l) ignored=$(git -C "$C" status --porcelain --ignored | wc -l)"
[ -z "$(git -C "$C" status --porcelain --ignored)" ] || refuse "the deploy is not clean (--ignored)"
self=$(sha256sum "$0" | cut -c1-64); cap=$(sha256sum "$W/cov2d_cap.py" | cut -c1-64); tst=$(sha256sum "$W/test_cov2d_cap.py" | cut -c1-64)
echo "sha256 $0=$self want=${WANT_SELF:-(none)}"
echo "sha256 $W/cov2d_cap.py=$cap want=$CAP_SHA"
echo "sha256 $W/test_cov2d_cap.py=$tst want=$TEST_SHA"
[ -n "$WANT_SELF" ] && [ "$self" = "$WANT_SELF" ] && [ "$cap" = "$CAP_SHA" ] && [ "$tst" = "$TEST_SHA" ] \
    || refuse "a file's sha256 is not the reviewed one"
echo "DIGESTS_MATCH"
(cd "$W" && PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B -m unittest test_cov2d_cap > "$W/test.out" 2>&1); trc=$?
echo "companion test ($(/usr/bin/python3 -V 2>&1)) rc=$trc: $(tail -1 "$W/test.out")"
[ "$trc" = 0 ] || { cat "$W/test.out"; refuse "the companion test failed"; }
source "$C/2d-unfolding/cov2d/jobs/cov2d_env.sh"
git -C "$C" fetch -q origin main || refuse "fetch"
echo "origin/main=$(git -C "$C" rev-parse origin/main)"
noatime() { "$PY310" -B -c "import sys; sys.path.insert(0, '$C/2d-unfolding/cov2d/jobs'); import cov2d_jobs as j; print(j.noatime_sha256(sys.argv[1]))" "$1"; }
# 1. the four ended as the ruling's collision and nothing else (the auditor's B1): the exit 1 of each comes only from
#    its expected "exists; not overwritten" labels; nothing of G18_C exists yet
expect() {  # expect <job>: its colliding labels, sorted, comma-joined
    case "$1" in G18_L) echo "L_G18_BeamAngleX_0,X_G18" ;; G18_Ua) echo U_G18_Flux_0 ;; G18_Ba) echo B_G18_001 ;;
        G18_Ta) echo T_G18_5720000 ;; esac
}
for id in $IDS; do
    job=$(awk -v m="M=$M" -v i="id=$id" '$2 == m && $NF ~ /^limit=/ && $4 == i {sub(/^job=/, "", $3); print $3}' "$O/submissions.log")
    want=$(expect "$job")
    echo "CHECK $id: job=${job:-(none)} expected skips=${want:-(none)}"
    [ -n "$want" ] && [ "$(echo "$job" | wc -w)" -eq 1 ] || refuse "$id does not map to one of the four jobs in submissions.log"
    s=$(sacct -X -n -P -j "$id" -o State,ExitCode); echo "  sacct $s"
    [ "$s" = "FAILED|1:0" ] || refuse "$id is not FAILED|1:0"
    bs=$(sacct -n -P -j "$id" -o JobID,State,ExitCode | awk -F'|' '$1 ~ /\.[0-9]+$/ && ($2 != "COMPLETED" || $3 != "0:0")')
    ns=$(sacct -n -P -j "$id" -o JobID | grep -cE '\.[0-9]+$')
    echo "  steps $ns, not COMPLETED 0:0: ${bs:-none}"
    [ -z "$bs" ] || refuse "$id has a step that is not COMPLETED 0:0"
    ls "$O"/walls.$job.*.tsv > /dev/null 2>&1 || refuse "$job has no walls file"
    bw=$(awk -F'\t' '$4 != 0' "$O"/walls.$job.*.tsv); w=$(cat "$O"/walls.$job.*.tsv | wc -l)
    echo "  walls rows $w, run_rc not 0: ${bw:-none}"
    [ -z "$bw" ] || refuse "$job has a run with run_rc not 0"
    jl=$O/logs/cov2d-$job-$id.out
    [ -f "$jl" ] || refuse "$jl is missing"
    rf=$(grep -E '^\[cov2d\] [^ ]+ rc=|unknown script' "$jl")
    echo "  run failures in the job log: ${rf:-none}"
    [ -z "$rf" ] || refuse "$job's log has a run failure"
    sk=$(sed -n 's/^\[cov2d\] \([^ ]*\) exists; not overwritten$/\1/p' "$jl" | sort | paste -sd, -)
    echo "  skips in the job log: ${sk:-none}"
    [ "$sk" = "$want" ] || refuse "$job's skips are not $want"
    rows=$(awk -F'\t' -v j="$job" 'NR > 1 && $1 == j' "$O/tables/runs_G18.tsv" | wc -l)
    nk=$(echo "$want" | tr ',' '\n' | wc -l)
    echo "  walls $w + skips $nk vs runs_G18.tsv rows $rows; end line: $(grep -E '^\[cov2d\] end ' "$jl")"
    [ "$((w + nk))" -eq "$rows" ] || refuse "$job: walls + skips != its runs_G18.tsv rows"
    grep -qE '^\[cov2d\] end .* rc=1$' "$jl" || refuse "$job's log has no end rc=1 line"
    echo "  MATCH the ruling's collision"
done
grep -qE " job=$CJOB id=" "$O/submissions.log" && refuse "$CJOB is already in submissions.log"
# fresh: none of the four exists. resume (the director's A3 low): all four exist, left by this connect's own earlier run
# that renamed and installed, then WAITed at step 7; steps 3-5 are then verified against its ledger, not redone
L=$O/renames-pilot-60857636.tsv
n_have=0
for f in "$O/tables/runs_$CTRUTH.tsv" "$O/tables/jobs_$CTRUTH.tsv" "$O/pseudo/$CTRUTH" "$L"; do
    { [ -e "$f" ] || [ -L "$f" ]; } && { n_have=$((n_have + 1)); echo "exists: $f"; }
done
case $n_have in 0) mode=fresh ;; 4) mode=resume ;; *) refuse "a partial state: $n_have of the tables, the symlink and the ledger exist" ;; esac
echo "MODE $mode"
# 2. the completion tables, in $W
"$PY310" -B - "$C" "$O/tables/runs_G18.tsv" "$W" $LAYOUT <<'EOF' || refuse "the completion tables"
import sys
C, src, W, layout = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
sys.path.insert(0, C + "/2d-unfolding/cov2d/jobs")
import cov2d_jobs as j
lines = open(src).read().splitlines()
rows = {}
for ln in lines[1:]:
    f = ln.split("\t")
    if f[2] in rows:
        sys.exit("a duplicate label in runs_G18.tsv: " + f[2])
    rows[f[2]] = f
out, lane_s = [lines[0]], {}
for item in layout:
    label, lane, cpus = item.split(":")
    f = rows[label]
    if f[3] != cpus:
        sys.exit("%s runs at %s CPUs in runs_G18.tsv, not the ruling's %s" % (label, f[3], cpus))
    new = ["G18_C", "G18_C." + lane] + f[2:]
    assert new[2:] == f[2:] and len(new) == 7
    out.append("\t".join(new))
    lane_s[lane] = lane_s.get(lane, 0) + int(f[6])
    print("row %s from %s/%s -> G18_C/G18_C.%s, cpus %s, est_s %s" % (label, f[0], f[1], lane, f[3], f[6]))
longest = max(lane_s.values())
job = ["G18_C", str(len(lane_s)), "128", str(len(layout)), str(longest), str(longest + j.PREFLIGHT_S), j.limit_of(longest)]
open(W + "/runs_G18C.tsv", "w").write("\n".join(out) + "\n")
open(W + "/jobs_G18C.tsv", "w").write("job\tlanes\tlane_cpus\truns\tlongest_lane_s\twall_s\tlimit\n" + "\t".join(job) + "\n")
print("lanes %s longest %d limit %s" % (lane_s, longest, job[6]))
EOF
lim=$(awk -F'\t' -v j="$CJOB" 'NR > 1 && $1 == j {print $7}' "$W/jobs_$CTRUTH.tsv")
[ -n "$lim" ] || refuse "no limit for $CJOB"
sha256sum "$W/runs_$CTRUTH.tsv" "$W/jobs_$CTRUTH.tsv"
if [ "$mode" = resume ]; then
    # the earlier run's state, checked: the installed tables are this run's, the symlink is G18, and the ledger has one
    # stat_match row per label, each source gone and each destination holding only the pilot's xsec.root
    cmp "$W/runs_$CTRUTH.tsv" "$O/tables/runs_$CTRUTH.tsv" && cmp "$W/jobs_$CTRUTH.tsv" "$O/tables/jobs_$CTRUTH.tsv" \
        || refuse "resume: the installed tables are not this connect's"
    [ "$(readlink "$O/pseudo/$CTRUTH")" = G18 ] && [ -f "$O/pseudo/$CTRUTH/b/pseudo_b.json" ] || refuse "resume: the symlink"
    [ "$(head -1 "$L")" = "$(printf 'utc\tpath\tsha256\tsize\tmtime\tinode\tstat_match\tcondition\tto')" ] \
        && [ "$(tail -n +2 "$L" | wc -l)" -eq 5 ] || refuse "resume: the ledger is not one header and five rows"
    for item in $LAYOUT; do
        label=${item%%:*}; src=$O/out/$label; dst=$src$SUFFIX
        row=$(awk -F'\t' -v p="$src/xsec.root" -v t="$dst/xsec.root" 'NR > 1 && $2 == p && $9 == t && $7 == "yes"' "$L")
        [ "$(printf '%s\n' "$row" | grep -c .)" -eq 1 ] || refuse "resume: no single stat_match row for $label"
        want=$(cat "$O"/SHA256SUMS.pilot.* | awk -v r="$label/xsec.root" '$2 == r {print $1}')
        [ ! -e "$src" ] && [ -d "$dst" ] && [ "$(ls -A "$dst")" = xsec.root ] || refuse "resume: $label's source or destination"
        got=$(noatime "$dst/xsec.root")
        echo "RESUME $label: $dst/xsec.root sha256=$got ledger=$(cut -f3 <<<"$row") pilot=$want"
        [ "$got" = "$want" ] && [ "$got" = "$(cut -f3 <<<"$row")" ] || refuse "resume: $label's sha256"
    done
fi
if [ "$mode" = fresh ]; then
# 3. the price, before anything changes: over the cap is a wait
sacct -X -n -P -S 2026-11-04 -u "$(id -un)" -o JobID,JobName,State,ElapsedRaw,NNodes,TimelimitRaw > "$W/s.psv" || refuse "sacct"
k=$(/usr/bin/python3 -I -B "$W/cov2d_cap.py" --sacct "$W/s.psv" --submissions "$O/submissions.log" --M "$M" --limit "$lim" 2>&1); crc=$?
echo "PRECHECK $CJOB limit=$lim connect(rc=$crc)=$k"
[ "$crc" = 3 ] && { echo "WAIT $CJOB is over the cap of 165.8: nothing renamed, installed or submitted"; echo DONE; exit 0; }
[ "$crc" = 0 ] || refuse "the pre-check total could not be computed"
# 4. the rename: verify all five, then move each
for item in $LAYOUT; do
    label=${item%%:*}; src=$O/out/$label; dst=$src$SUFFIX
    [ -d "$src" ] && [ ! -L "$src" ] || refuse "$src is not a directory"
    { [ -e "$dst" ] || [ -L "$dst" ]; } && refuse "$dst exists"
    [ "$(ls -A "$src")" = xsec.root ] || refuse "$src holds more than xsec.root: $(ls -A "$src" | tr '\n' ' ')"
    n=$(cat "$O"/SHA256SUMS.pilot.* | awk -v r="$label/xsec.root" '$2 == r' | wc -l)
    [ "$n" -eq 1 ] || refuse "$label/xsec.root has $n SHA256SUMS.pilot lines"
    want=$(cat "$O"/SHA256SUMS.pilot.* | awk -v r="$label/xsec.root" '$2 == r {print $1}')
    got=$(noatime "$src/xsec.root")
    echo "VERIFY $label: $(stat -c '%n size=%s mtime=%y inode=%i' "$src/xsec.root") sha256=$got pilot=$want"
    [ "$got" = "$want" ] || refuse "$label/xsec.root is not the pilot's product"
done
printf 'utc\tpath\tsha256\tsize\tmtime\tinode\tstat_match\tcondition\tto\n' > "$L"
for item in $LAYOUT; do
    label=${item%%:*}; src=$O/out/$label; dst=$src$SUFFIX
    before=$(stat -c '%s %Y %i' "$src/xsec.root"); sb=$(noatime "$src/xsec.root")
    t=$(date -u +%FT%TZ); mv -n -v "$src" "$dst"; mrc=$?
    echo "MV $t rc=$mrc $src -> $dst"
    [ "$mrc" = 0 ] && [ ! -e "$src" ] && [ -d "$dst" ] || refuse "the rename of $label"
    after=$(stat -c '%s %Y %i' "$dst/xsec.root"); sa=$(noatime "$dst/xsec.root")
    m=no; [ "$before" = "$after" ] && [ "$sb" = "$sa" ] && m=yes
    set -- $before
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$t" "$src/xsec.root" "$sa" "$1" "$2" "$3" "$m" \
        "the director's ruling on G18_L, 2026-11-06, item 3(a): the pilot's products do not count for the bulk" "$dst/xsec.root" >> "$L"
    [ "$m" = yes ] || refuse "$label's stat or sha256 changed across the rename (before $before $sb, after $after $sa)"
done
cat "$L"
# 5. the tables and the symlink
cp -n "$W/runs_$CTRUTH.tsv" "$W/jobs_$CTRUTH.tsv" "$O/tables/" && cmp "$W/runs_$CTRUTH.tsv" "$O/tables/runs_$CTRUTH.tsv" \
    && cmp "$W/jobs_$CTRUTH.tsv" "$O/tables/jobs_$CTRUTH.tsv" || refuse "installing the tables"
ln -s G18 "$O/pseudo/$CTRUTH" && [ "$(readlink "$O/pseudo/$CTRUTH")" = G18 ] && [ -f "$O/pseudo/$CTRUTH/b/pseudo_b.json" ] \
    || refuse "the symlink $O/pseudo/$CTRUTH"
echo "installed $O/tables/runs_$CTRUTH.tsv, $O/tables/jobs_$CTRUTH.tsv; $O/pseudo/$CTRUTH -> $(readlink "$O/pseudo/$CTRUTH")"
fi
# 6. the labels (the ruling's item 4)
labs=$(awk -F'\t' -v j="$CJOB" 'NR > 1 && $1 == j {print $3}' "$O/tables/runs_$CTRUTH.tsv")
[ -n "$labs" ] || refuse "$CJOB has no runs_$CTRUTH.tsv rows"
hits=""; for l in $labs; do [ -e "$O/out/$l" ] && hits="$hits $l"; done
echo "LABELS $CJOB: $(echo $labs | wc -w) in runs_$CTRUTH.tsv, existing in $O/out:${hits:- none}"
[ -z "$hits" ] || refuse "$CJOB: its labels already exist in $O/out:$hits"
# 7. both totals on one snapshot, then the bound submit
sacct -X -n -P -S 2026-11-04 -u "$(id -un)" -o JobID,JobName,State,ElapsedRaw,NNodes,TimelimitRaw > "$W/s.psv" || refuse "sacct"
g=$("$PY310" -B "$CJ" gate --sacct "$W/s.psv" --tables "$O/tables" --want "$CJOB" 2>&1); grc=$?
k=$(/usr/bin/python3 -I -B "$W/cov2d_cap.py" --sacct "$W/s.psv" --submissions "$O/submissions.log" --M "$M" --limit "$lim" 2>&1); crc=$?
echo "TOTALS $CJOB limit=$lim gate(rc=$grc)=$g connect(rc=$crc)=$k"
{ [ "$grc" = 0 ] || [ "$grc" = 3 ]; } && { [ "$crc" = 0 ] || [ "$crc" = 3 ]; } || refuse "$CJOB: a total could not be computed"
if [ "$grc" = 3 ] || [ "$crc" = 3 ]; then
    echo "WAIT $CJOB is over the cap of 165.8 after the rename (gate rc=$grc, connect rc=$crc): renamed and installed, not submitted; a relaunch resumes"
else
    bash "$C/2d-unfolding/cov2d/jobs/cov2d_submit.sh" "$C" "$M" "$CTRUTH" "$CJOB"; src=$?
    echo "submit $CJOB rc=$src"
    id=$(awk -v m="M=$M" -v j="job=$CJOB" '$2 == m && $3 == j {for (i = 1; i <= NF; i++) if ($i ~ /^id=/) print substr($i, 4)}' "$O/submissions.log" | tail -1)
    echo "id=${id:-(none)}"
    [ -n "$id" ] && scontrol show job "$id" 2>/dev/null | grep -E "JobId|QOS|TimeLimit|NumNodes|JobState" | tr -s ' \n' ' '; echo
fi
rm -f "$W/s.psv"
echo "plain-after=$(git -C "$C" status --porcelain | wc -l) ignored-after=$(git -C "$C" status --porcelain --ignored | wc -l)"
tail -3 "$O/submissions.log"
echo "end=$(date -u +%FT%TZ)"; echo DONE
