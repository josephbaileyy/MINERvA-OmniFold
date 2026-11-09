#!/bin/bash
# FD-PRR dry run: the connect (FD-PRR-DECLARATION.md sections 10.3-10.4, under FD-PRR BINDING 1), on a Perlmutter login
# node, detached, after the director's go (2026-11-09: ENS1's stage 2 ended and its post-run done; fd1b_bdg_* jobs may
# still be queued, since they read the shared inputs through O_NOATIME and the staging's per-file stat check is fail-safe).
# Code pin M_A1 = 6727020a (the #966 merge: FD-PRR with Addendum A1, under BINDING 1 and its addendum A1). In order,
# any failure a final stop before anything is submitted:
#   preconditions: $OUT new; no prr_* or ens1_* job queued or running (squeue --me);
#   the balance from iris: the 27.0 node-h cap at most half of m3246's remaining CPU balance;
#   a fresh clone at M into $OUT/deploy, clean (porcelain --ignored 0), the six FD-PRR files at their declared sha256
#     and the declaration and Addendum A1 at their sha256;
#   the pins check (declaration 10.4): each of the six shared sources read once through dd iflag=noatime into
#     sha256sum, with its own stat (size, mtime, atime, inode) before and after; a digest off its pin, or any stat
#     field that moved, stops. No directory atime is read or compared, and no absolute atime is expected;
#   the environment pre-check (0 node-h): setup_salloc_env.sh sourced in a subshell; lightgbm, scipy, numpy import;
#   prr_probe.py manifest and tasks: queues dry 15, iter 44, cap 29, misc 93 (181);
#   the job's first python call, run after sourcing with root_6_28's python3 (the source's rc checked on its own): its
#     `prr_probe.py limit dry` must print the declared 5:15:00, and it is the --time submitted;
#   one sbatch, from the plain login environment: --job-name=prr_dry --time=05:15:00 sbatch_prr.sh dry; then
#     scontrol's TimeLimit must read 05:15:00 or the job is cancelled at once.
# The job itself (sbatch_prr.sh) re-checks the job name, the TimeLimit and the ens1_* queue, stages every source through
# O_NOATIME with per-file stat records, and writes DONE only after the 15 tasks, C-PAIR and C-MASK all pass.
# Writes only under $OUT. No set -u (it kills setup_salloc_env.sh). Launched from a /dev/shm copy of itself, whose path
# is $1; it deletes that copy at exit. The deploy stays: the job runs from it.
SELF=$1
M=6727020a7c58b00dd00806151c627c8a24f72402
OUT=/pscratch/sd/j/josephrb/fd-prr-20261108
D=$OUT/deploy
CAP=27.0
TLIMIT=                                             # set below from the bound code's `prr_probe.py limit dry` (5:15:00)
DECL_SHA=5be1e19cb8db67064cb0f90382ed7ac2365a2ed4841d9b498f323ed2761b64ce
A1_SHA=ca6b8457e74c9323fcb985766a88f404038f6f16c3e822a67bf2606af223f38b
bail() { rm -f -- "$SELF"; exit 9; }                # a precondition failed: nothing written
[ ! -e "$OUT" ] || bail
q=$(squeue --me -h -o '%j') || bail                 # fails closed: no answer from squeue, no connect
[ -z "$(printf '%s\n' "$q" | grep -E '^(prr_|ens1_)')" ] || bail
mkdir -p "$OUT/logs" || bail
LOG=$OUT/logs/connect-dry.log
exec > "$LOG" 2>&1
finish() { echo "prr dry submit rc=$1"; date -u +%FT%TZ; echo "$1" > "$OUT/logs/connect-dry.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$OUT/logs/prr_dry_submit.sh"
echo "squeue --me before:"; squeue --me -h -o "%i %j %T"

# ---- the balance (coverage-5b's method): iris's m3246 row, Allocated - Charged
echo "== iris"; row=$(timeout 120 iris < /dev/null 2>&1 | grep -E '^m3246 ' | head -1); echo "$row"
bal=$(echo "$row" | awk 'NF>=5 {printf "%.1f", $5-$4}')
[ -n "$bal" ] || { echo "STOP: could not read the m3246 balance"; finish 9; }
echo "balance_node_h=$bal half=$(awk -v b=$bal 'BEGIN{printf "%.1f", b/2}') cap=$CAP"
awk -v b=$bal -v c=$CAP 'BEGIN{exit !(c <= b/2)}' || { echo "STOP: the cap $CAP is above half the balance $bal: to the director"; finish 9; }

# ---- the deploy: a fresh clone at M, clean, the bound bytes
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$D" > "$OUT/logs/clone.log" 2>&1 || { echo "STOP: clone"; finish 3; }
git -C "$D" -c advice.detachedHead=false checkout -q "$M" || { echo "STOP: checkout"; finish 3; }
[ "$(git -C "$D" rev-parse HEAD)" = "$M" ] || { echo "STOP: HEAD is not M"; finish 9; }
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "HEAD $M; porcelain --ignored lines before: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy is not clean"; finish 9; }
( cd "$D/nd-unfolding/prior_retention" && sha256sum -c ) <<SUMS || { echo "STOP: the FD-PRR files are not the bound ones"; finish 9; }
f87ee90c58d2b8904fe881931edc61966a6adda8be7eb503da6644797a3d1232  prr_probe.py
17acad82bad7c43f45c423e41039eb81381f5acab15ecdf983ad0d023848d046  prr_ibu.py
f35bc3282b50215dd583b76b0d6a747f90185e4b96b6e3f5b693d42c01166372  prr_read.py
10290087cdd57d972a4df5289f1910161373e8def3f44c15ba0682f9d14a0b85  sbatch_prr.sh
44223143a6982fb876e742fd910c3de46e48fb419da351b9ad9693186f791746  test_prr.py
4666aa0654dccbe999972642090cfc18ccac8d14d7fa4c5057be6e745520ef25  prr_mutation.py
SUMS
decl=$(sha256sum "$D/docs/orchestration/state/measurement-paper/5d-community-20261024/FD-PRR-DECLARATION.md" | cut -d' ' -f1)
echo "declaration sha256 $decl"
[ "$decl" = "$DECL_SHA" ] || { echo "STOP: the declaration is not the bound one"; finish 9; }
a1=$(sha256sum "$D/docs/orchestration/state/measurement-paper/5d-community-20261024/FD-PRR-ADDENDUM-A1.md" | cut -d' ' -f1)
echo "addendum A1 sha256 $a1"
[ "$a1" = "$A1_SHA" ] || { echo "STOP: Addendum A1 is not the bound one"; finish 9; }

PYENV() { ( eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
            conda activate "$HOME/.conda/envs/root_6_28" && cd "$D" && \
            nice -n 19 env -u PYTHONPATH PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 python3 -B "$@" ); }

# ---- the manifest, from the bound code (prr_probe.SOURCES), then the pins check of every source
PYENV nd-unfolding/prior_retention/prr_probe.py manifest --out "$OUT/manifest.json" || { echo "STOP: manifest"; finish 5; }
sha256sum "$OUT/manifest.json"
PYENV - "$OUT/manifest.json" > "$OUT/logs/pins.tsv" <<'EOF' || { echo "STOP: the pins check did not pass (logs/pins.tsv)"; cat "$OUT/logs/pins.tsv"; finish 4; }
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

# ---- the environment the job will source: lightgbm, scipy and numpy must import (the job checks again)
( source "$D/setup_salloc_env.sh" > "$OUT/logs/env-precheck.log" 2>&1
  python3 -c "import lightgbm, scipy, numpy, sys; print('python', sys.version.split()[0], 'lightgbm', lightgbm.__version__, 'scipy', scipy.__version__, 'numpy', numpy.__version__)" ) \
  || { echo "STOP: the environment lacks lightgbm/scipy (see env-precheck.log)"; finish 7; }

# ---- the queues, from the probe's own tasks command, pointing into $OUT/stage
PYENV nd-unfolding/prior_retention/prr_probe.py tasks --out "$OUT/queues" --stage-dir "$OUT/stage" --runs "$OUT/runs" \
  || { echo "STOP: tasks"; finish 5; }
for j in dry:15 iter:44 cap:29 misc:93; do
  n=$(grep -vc '^#' "$OUT/queues/${j%%:*}.tsv"); echo "queue ${j%%:*}: $n tasks"
  [ "$n" -eq "${j##*:}" ] || { echo "STOP: queue ${j%%:*} is not ${j##*:} tasks"; finish 5; }
done
grep -q '^prr_B0_A7_gibuu_s991000	' "$OUT/queues/dry.tsv" && grep -q '^prr_O5_nominal_s991000	' "$OUT/queues/dry.tsv" \
  || { echo "STOP: C-PAIR's or C-MASK's task is not in the dry queue"; finish 5; }
sha256sum "$OUT"/queues/*.tsv

# ---- the job's first python calls, run as the job runs them under Addendum A1: in a subshell of this plain environment,
# after sourcing setup_salloc_env.sh (rc checked on its own), with root_6_28's python3. Its `prr_probe.py limit dry` is
# also the --time this connect submits with, so --time comes from the bound code, as the job's own check reads it.
echo "plain python3 (not used by any call below): $(command -v python3) $(python3 -V 2>&1)"
lim=$( source "$D/setup_salloc_env.sh" > "$OUT/logs/connect-source.log" 2>&1; rc=$?
       [ "$rc" -eq 0 ] || { echo "SOURCE_RC=$rc" >&2; exit 97; }
       echo "sourced python3: $(command -v python3) $(python3 -V 2>&1)" >&2
       [ "$(command -v python3)" = "$HOME/.conda/envs/root_6_28/bin/python3" ] || { echo "NOT_ROOT628" >&2; exit 98; }
       python3 "$D/nd-unfolding/prior_retention/prr_probe.py" limit dry ) 2> "$OUT/logs/sourced-python.err"
lrc=$?
cat "$OUT/logs/sourced-python.err"
[ "$lrc" -ne 97 ] || { echo "STOP: setup_salloc_env.sh failed to source ($(grep SOURCE_RC "$OUT/logs/sourced-python.err")); see logs/connect-source.log"; finish 7; }
[ "$lrc" -ne 98 ] || { echo "STOP: after sourcing, python3 is not root_6_28's"; finish 7; }
echo "root_6_28 python3 prr_probe.py limit dry -> '$lim' (rc $lrc)"
[ "$lrc" -eq 0 ] && [ "$lim" = "5:15:00" ] || { echo "STOP: the job's first python call fails after sourcing, or its limit is not the declared 5:15:00"; finish 7; }
TLIMIT=$(echo "$lim" | awk -F: '{printf "%02d:%02d:%02d", $1, $2, $3}')   # scontrol prints HH:MM:SS
echo "--time=$TLIMIT"

# ---- the submission, from the plain login environment (the job is --export=ALL, so no login-step setting reaches it)
q=$(squeue --me -h -o '%j') || { echo "STOP: squeue did not answer"; finish 9; }
[ -z "$(printf '%s\n' "$q" | grep -E '^(prr_|ens1_)')" ] || { echo "STOP: a prr_* or ens1_* job appeared"; finish 9; }
date -u +%FT%TZ
cd "$OUT" || finish 9
sbatch --time=$TLIMIT --job-name=prr_dry --output="$OUT/logs/%x_%j.out" \
  "$D/nd-unfolding/prior_retention/sbatch_prr.sh" dry "$D" "$M" "$OUT" > "$OUT/logs/submit-dry.out" 2>&1
rc=$?; echo "sbatch rc=$rc"; cat "$OUT/logs/submit-dry.out"
[ $rc = 0 ] || { echo "STOP at sbatch (final)"; finish $rc; }
job=$(sed -n 's/^Submitted batch job \([0-9][0-9]*\)$/\1/p' "$OUT/logs/submit-dry.out")
[ -n "$job" ] || { echo "STOP: no job id"; finish 9; }
echo "dry run job $job"; echo "$job" > "$OUT/logs/dry.jobid"
tl=$(scontrol show job "$job" | sed -n 's/.*TimeLimit=\([^ ]*\).*/\1/p' | head -1)
echo "scontrol TimeLimit=$tl (declared $TLIMIT)"
if [ "$tl" != "$TLIMIT" ]; then
  scancel "$job"; echo "STOP: TimeLimit $tl is not $TLIMIT; job $job cancelled (rc $?)"; sleep 5
  sacct -j "$job" -X -n -P -o JobID,State,Elapsed; finish 6
fi
sleep 5
squeue -j "$job" -h -o "%i %j %T %M %l %D %q %a"; scontrol show job "$job" | grep -E 'JobState|TimeLimit|NumNodes|QOS|Account|Partition'
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "porcelain --ignored lines after: $n"
[ "$n" -eq 0 ] || { echo "the deploy changed after the submission (the job is queued; reported, not cancelled)"; finish 8; }
finish 0
