#!/bin/bash
# S2R: the submit connect (S2R-DECLARATION.md section 5; the director's approval in principle of 2026-11-24, then the
# director's GO with a window epoch). Derived from T3's reviewed t3p_submit.sh rev 2 (50e86da3), one mode.
# On a Perlmutter login node, from a /dev/shm copy of itself whose path is $1; it deletes that copy at exit.
#   usage: s2r_submit.sh <self> <window_end_epoch> <fence prefixes, comma-separated>
# In order, any failure a final stop before anything is submitted:
#   the window: now <= window_end (the epoch the launcher computed from date, never typed);
#   the fence: no job of this user whose name starts with a fenced prefix or s2r_ is in a non-terminal state, by sacct
#     (State classified in code; sacct, never squeue);
#   $OUT new; the balance from iris: the cap 1.0 node-h at most half of m3246's remaining balance;
#   a fresh clone at M, clean, the S2R files, T3's two imported files and the declaration at their sha256;
#   test_s2r.py (N OK) under root_6_28; the manifest (s2r_probe.py manifest, into logs/) and its pins check (each
#     source read once through dd iflag=noatime into sha256sum, stat unmoved); the environment; $OUT/fence.txt;
#   the job's own limit from the bound code (`s2r_probe.py limit`) is the --time; one sbatch from the plain login
#     environment; scontrol's TimeLimit must equal it, or scancel at once.
# Writes only under $OUT (and the launcher's /dev/shm copy of this script). No set -u (it kills setup_salloc_env.sh).
SELF=$1; WEND=$2; FENCE=$3
M=@@M@@
OUT=/pscratch/sd/j/josephrb/s2r-20261124
D=$OUT/deploy
CAP_TOTAL=1.0
NTESTS=@@NTESTS@@
DECL_SHA=@@DECL_SHA@@
bail() { echo "BAIL $*"; rm -f -- "$SELF"; exit 9; }
[[ "$WEND" =~ ^[0-9]{10}$ ]] || bail "window end '$WEND'"
now=$(date +%s); [ "$now" -le "$WEND" ] || bail "the window ended (now $now > $WEND)"
[[ "$FENCE" =~ ^[A-Za-z0-9_.-]+(,[A-Za-z0-9_.-]+)*$ ]] || bail "fence '$FENCE'"

fence_sacct() {
  local rows bad
  rows=$(sacct -X -n -P -S now-14days -o JobID,JobName,State 2>&1) || { echo "sacct failed: $rows"; return 2; }
  bad=$(printf '%s\n' "$rows" | awk -F'|' -v pre="$FENCE,s2r_" '
    BEGIN { n = split(pre, P, ",") }
    NF >= 3 {
      st = $3; sub(/ by [0-9]+$/, "", st)
      term = (st ~ /^(COMPLETED|FAILED|CANCELLED|TIMEOUT|OUT_OF_MEMORY|NODE_FAIL|PREEMPTED|BOOT_FAIL|DEADLINE)$/)
      if (term) next
      for (i = 1; i <= n; i++) if (P[i] != "" && index($2, P[i]) == 1) { print; break }
    }')
  [ -z "$bad" ] || { echo "fenced or s2r_ jobs not terminal: $bad"; return 1; }
  return 0
}
fence_sacct > /dev/null 2>&1 || bail "fence (sacct) not clear"
[ ! -e "$OUT" ] || bail "$OUT exists"
mkdir -p "$OUT/logs" || bail "mkdir"
LOG=$OUT/logs/connect-submit.log
exec > "$LOG" 2>&1
finish() { echo "s2r submit rc=$1"; date -u +%FT%TZ; echo "$1" > "$OUT/logs/connect-submit.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ; echo "window_end_epoch $WEND (now $now); fence prefixes $FENCE"
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$OUT/logs/s2r_submit.sh"
echo "== fence (sacct)"; fence_sacct || { echo "STOP: fence"; finish 9; }; echo "fence clear"

echo "== iris"; row=$(timeout 120 iris < /dev/null 2>&1 | grep -E '^m3246 ' | head -1); echo "$row"
bal=$(echo "$row" | awk 'NF>=5 {printf "%.1f", $5-$4}')
[ -n "$bal" ] || { echo "STOP: could not read the m3246 balance"; finish 9; }
echo "balance_node_h=$bal half=$(awk -v b=$bal 'BEGIN{printf "%.1f", b/2}') cap_total=$CAP_TOTAL"
awk -v b=$bal -v c=$CAP_TOTAL 'BEGIN{exit !(c <= b/2)}' || { echo "STOP: the cap $CAP_TOTAL is above half the balance $bal"; finish 9; }

mkdir -p "$OUT/tmp-connect" || { echo "STOP: mkdir tmp-connect"; finish 9; }
PYENV() { ( eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
            conda activate "$HOME/.conda/envs/root_6_28" && cd "$D" && \
            nice -n 19 env -u PYTHONPATH TMPDIR="$OUT/tmp-connect" PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 python3 -B "$@" ); }
bound_check() {
  ( cd "$D/nd-unfolding" && sha256sum -c ) <<SUMS
@@BOUND_SUMS@@
SUMS
}
S2RDIR="$D/docs/orchestration/state/measurement-paper/5d-community-20261024/fd/s2r-20261124"
clean_check() {
  local n bad
  n=$(git -C "$D" status --porcelain --untracked-files=all | wc -l)
  bad=$(git -C "$D" status --porcelain --ignored --untracked-files=all | grep '^!! ' | grep -vc '__pycache__/')
  echo "porcelain lines (tracked+untracked) $n; ignored entries other than __pycache__/ $bad"
  [ "$n" -eq 0 ] && [ "$bad" -eq 0 ]
}

git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$D" > "$OUT/logs/clone.log" 2>&1 || { echo "STOP: clone"; finish 3; }
git -C "$D" -c advice.detachedHead=false checkout -q "$M" || { echo "STOP: checkout"; finish 3; }
[ "$(git -C "$D" rev-parse HEAD)" = "$M" ] || { echo "STOP: HEAD is not M"; finish 9; }
echo "HEAD $M"; clean_check || { echo "STOP: the deploy is not clean"; finish 9; }
bound_check || { echo "STOP: the S2R or T3 files are not the bound ones"; finish 9; }
decl=$(sha256sum "$S2RDIR/S2R-DECLARATION.md" | cut -d' ' -f1); echo "declaration sha256 $decl"
[ "$decl" = "$DECL_SHA" ] || { echo "STOP: the declaration is not the bound one"; finish 9; }

PYENV -m unittest nd-unfolding/s2r/test_s2r.py > "$OUT/logs/tests.log" 2>&1; trc=$?
tail -3 "$OUT/logs/tests.log"
[ "$trc" -eq 0 ] && grep -q "^Ran $NTESTS tests" "$OUT/logs/tests.log" && tail -1 "$OUT/logs/tests.log" | grep -q '^OK' \
  || { echo "STOP: test_s2r.py did not run $NTESTS OK (rc $trc)"; finish 5; }
clean_check || { echo "STOP: the tests left files in the deploy"; git -C "$D" status --porcelain --ignored | head; finish 5; }

PYENV nd-unfolding/s2r/s2r_probe.py manifest --out "$OUT/logs/manifest-connect.json" || { echo "STOP: manifest"; finish 5; }
sha256sum "$OUT/logs/manifest-connect.json"
PYENV - "$OUT/logs/manifest-connect.json" > "$OUT/logs/pins.tsv" <<'EOF' || { echo "STOP: the pins check did not pass (logs/pins.tsv)"; cat "$OUT/logs/pins.tsv"; finish 4; }
import json, os, subprocess, sys
ok = True
print("role\tsha256_ok\tstat_unmoved\tsize\tatime_before_ns\tatime_after_ns\tsrc")
for e in json.load(open(sys.argv[1])):
    st = lambda: (lambda s: (s.st_size, s.st_mtime_ns, s.st_atime_ns, s.st_ino))(os.stat(e["src"]))
    before = st()
    dd = subprocess.Popen(["dd", f"if={e['src']}", "iflag=noatime", "bs=16M", "status=none"], stdout=subprocess.PIPE)
    got = subprocess.run(["sha256sum"], stdin=dd.stdout, capture_output=True, text=True).stdout.split()[0]
    rc = dd.wait()
    after = st()
    good, still = rc == 0 and got == e["sha256"], before == after
    ok &= good and still
    print(f"{e['role']}\t{good}\t{still}\t{before[0]}\t{before[2]}\t{after[2]}\t{e['src']}")
sys.exit(0 if ok else 1)
EOF
cat "$OUT/logs/pins.tsv"

( source "$D/setup_salloc_env.sh" > "$OUT/logs/env-precheck.log" 2>&1
  python3 -c "import lightgbm, scipy, numpy, sys; print('python', sys.version.split()[0], 'lightgbm', lightgbm.__version__, 'scipy', scipy.__version__, 'numpy', numpy.__version__)" ) \
  || { echo "STOP: the environment lacks lightgbm/scipy (see env-precheck.log)"; finish 7; }

printf '%s\n' "${FENCE//,/$'\n'}" > "$OUT/fence.txt"; echo "fence.txt:"; cat "$OUT/fence.txt"

lim=$( source "$D/setup_salloc_env.sh" > "$OUT/logs/connect-source.log" 2>&1; rc=$?
       [ "$rc" -eq 0 ] || { echo "SOURCE_RC=$rc" >&2; exit 97; }
       [ "$(command -v python3)" = "$HOME/.conda/envs/root_6_28/bin/python3" ] || { echo "NOT_ROOT628" >&2; exit 98; }
       python3 -B "$D/nd-unfolding/s2r/s2r_probe.py" limit ) 2> "$OUT/logs/sourced-python.err"
lrc=$?
cat "$OUT/logs/sourced-python.err"
want=1:00:00
echo "s2r_probe.py limit -> '$lim' (rc $lrc), declared $want"
[ "$lrc" -eq 0 ] && [ "$lim" = "$want" ] || { echo "STOP: the limit is not the declared $want"; finish 7; }
TLIMIT=$(echo "$lim" | awk -F: '{printf "%02d:%02d:%02d", $1, $2, $3}')

echo "== fence again (sacct)"; fence_sacct || { echo "STOP: fence at submission"; finish 9; }
now=$(date +%s); [ "$now" -le "$WEND" ] || { echo "STOP: the window ended before sbatch"; finish 9; }
date -u +%FT%TZ
cd "$OUT" || finish 9
for v in $(compgen -e | grep -E '^(SBATCH_|SLURM_|SALLOC_)'); do unset "$v"; done
echo "Slurm option variables left: $(compgen -e | grep -cE '^(SBATCH_|SLURM_|SALLOC_)')"
sbatch --time=$TLIMIT --job-name=s2r_run --output="$OUT/logs/%x_%j.out" \
  "$D/nd-unfolding/s2r/sbatch_s2r.sh" "$D" "$M" "$OUT" > "$OUT/logs/submit.out" 2>&1
rc=$?; echo "sbatch rc=$rc"; cat "$OUT/logs/submit.out"
[ $rc = 0 ] || { echo "STOP at sbatch (final)"; finish $rc; }
job=$(sed -n 's/^Submitted batch job \([0-9][0-9]*\)$/\1/p' "$OUT/logs/submit.out")
[ -n "$job" ] || { echo "STOP: no job id"; finish 9; }
echo "s2r_run job $job"; echo "$job" > "$OUT/logs/run.jobid"
sc=$(scontrol show job "$job")
tl=$(printf '%s\n' "$sc" | sed -n 's/.*TimeLimit=\([^ ]*\).*/\1/p' | head -1)
arr=$(printf '%s\n' "$sc" | grep -c 'ArrayJobId=')
echo "scontrol TimeLimit=$tl (declared $TLIMIT); array fields $arr"
if [ "$tl" != "$TLIMIT" ] || [ "$arr" -ne 0 ]; then
  scancel "$job"; echo "STOP: TimeLimit $tl is not $TLIMIT, or the job is an array ($arr); job $job cancelled (rc $?)"; sleep 5
  sacct -j "$job" -X -n -P -o JobID,State,Elapsed; finish 6
fi
sleep 5
sacct -j "$job" -X -n -P -o JobID,JobName,State,Timelimit,NNodes,QOS,Account
clean_check || { echo "the deploy changed after the submission (the job is queued; reported, not cancelled)"; finish 8; }
finish 0
