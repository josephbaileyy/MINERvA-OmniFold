#!/bin/bash
# COV2D-G2R connect ENVTEST-R3 (addendum J1 §4; COV2D-G2R-BINDING-1.md addendum J1): the envtest connect a third time.
# r1 (1b392259) STOPped on the open audit (the suites ran under /pscratch); r2 (2ef9ce12) fixed that (the suites from
# a shared clone of $C at M with TMPDIR beside it, all under /dev/shm) and STOPped on test_g2r_glue's PhaseTune: its
# record said STOP, "atime moved on 170 inputs" (diag-tune 84af1613, 2026-11-13T07:13Z), all of them the test's own
# stand-in products in its TMPDIR. The mechanism: the test patches os.O_NOATIME to 0 (test_g2r_glue.py, PhaseTune
# setUpClass, for macOS), so read_pinned's reads of its stand-ins are plain; on Linux tmpfs (relatime, coarse
# timestamps) the test's own sha256 read right after the write leaves atime <= mtime, and the read after Run.watch
# moves it. Probed on a login node with that pattern: /dev/shm moved 39 of 40, $HOME (GPFS, relatime) 0 of 40. The
# bound code is not affected (the real readout's O_NOATIME is real). Changes from r2, nothing else:
#   - the suites' place parent is $HOME/g2r-suites-place (GPFS, outside GUARDED) instead of /dev/shm; the block
#     between the >>> and <<< markers is r2's, byte for byte;
#   - before the suites, an atime probe in the place's TMPDIR does the test's pattern on 40 files (write; read; 10 ms;
#     stat; read; stat) and refuses (exit 10) if any atime moved, so a filesystem that would fail the test's ledger is
#     named before the suites run;
#   - its records go to $O/logs/envtest-r3/ and its log to /dev/shm/josephrb-g2r-envtest-r3.log.
# What r2 established stays: the deploys r1 made are reused, each clean at its commit, the bound sums re-checked; no
# envtest dir and no submissions.log may exist yet; the fence drops ll5d_ (ruling 4).
# On a login node it runs: the fence; iris (the cap at most half the balance; the balance printed); the independent
# recompute of the 110 node-h cap; the deploy checks; the four G2R suites under the jobs' root_6_28 environment (numpy
# 1.26) from the clone, each rc 0, the clone and the deploy clean after; then the bound g2r_submit.sh, once: envtest.
# Any refusal stops the connect. This log is fetched for the receipt, then it and this script are removed from
# /dev/shm (logged).
# Run: setsid nohup bash /dev/shm/josephrb-g2r-envtest-r3.sh >/dev/null 2>&1 </dev/null &
M=401733bce290ce122cfbf38f1526e120f174b3ec         # M_J1 (COV2D-G2R-BINDING-1.md:100, addendum J1, #1118): #1111's merge
PRE_M=a60547692df5f963e428cdfe4661fc51ab785b7b     # g2r_jobs.PRE_M: COV2D's deploy, the pre-patch driver
P=/pscratch/sd/j/josephrb; A=$P/MINERvA-OmniFold
O=$P/cov2d-g2r-20261112; C=$P/cov2d-g2r-deploy-j1; PRE=$O/deploy-pre
CAP=110.0; THIS=1.067                              # envtest's limit 01:04:00 (jobs_g2r.tsv)
LOG=/dev/shm/josephrb-g2r-envtest-r3.log
SHM_BASE=/global/homes/j/josephrb/g2r-suites-place  # the suites' place parent: $HOME's GPFS (outside GUARDED)
stop() { echo "STOP $*"; echo "end=$(date -u +%FT%TZ)"; echo DONE; exit 2; }
[[ $M =~ ^[0-9a-f]{40}$ ]] || { echo "STOP M is not filled"; exit 2; }
[ -e "$LOG" ] && { echo "STOP $LOG exists"; exit 2; }
exec >> "$LOG" 2>&1
echo "host=$(hostname) start=$(date -u +%FT%TZ) pid=$$ user=$(id -un) M=$M"
# --- the fence
echo "squeue: [$(squeue --me -h -o '%i %j %T %l %D' | tr '\n' ';')]"
[ "$(squeue --me -h -o %j | grep -cE '^(rsn_|e96data|rdx_|t2a|cov2d)')" = "0" ] \
    || stop "an rsn_, e96data, rdx_, t2a or cov2d job is queued or running"
cv=$(sacct -X -n -P -S 2026-11-04 -u josephrb -o JobID,JobName,State | awk -F'|' '$2 ~ /^cov2d/ && $3 !~ /^(COMPLETED|FAILED|CANCELLED|TIMEOUT|OUT_OF_MEMORY|NODE_FAIL|PREEMPTED|BOOT_FAIL|DEADLINE)/')
[ -z "$cv" ] || stop "a cov2d job is unended: $cv"
# --- iris and the independent recompute
echo "== iris"; row=$(iris 2>&1 | grep -E '^m3246 ' | head -1); echo "$row"
bal=$(echo "$row" | awk 'NF>=5 {printf "%.1f", $5-$4}'); [ -n "$bal" ] || stop "could not read the m3246 balance"
echo "balance_node_h=$bal half=$(awk -v b=$bal 'BEGIN{printf "%.1f", b/2}') cap=$CAP"
awk -v b=$bal -v c=$CAP 'BEGIN{exit !(c <= b/2)}' || stop "the cap $CAP is above half the balance $bal: to Joseph"
spent=$(sacct -X -n -P -S 2026-11-12 -u josephrb -o JobName,State,ElapsedRaw,NNodes | awk -F'|' '$1 ~ /^cov2dg2r-/ && $2 !~ /^(PENDING|RUNNING|REQUEUED|SUSPENDED|CONFIGURING|COMPLETING|RESIZING)/ {s += $3 * $4} END {printf "%.3f", s / 3600}')
held=$(squeue --me -h -o '%j|%l|%D' | awk -F'|' '$1 ~ /^cov2dg2r-/ {split($2, t, /[-:]/); n = length(t); s = (n == 4 ? t[1]*86400 + t[2]*3600 + t[3]*60 + t[4] : n == 3 ? t[1]*3600 + t[2]*60 + t[3] : t[1]*60 + t[2]); h += s * $3} END {printf "%.3f", h / 3600}')
proj=$(awk -v a=$spent -v b=$held -v c=$THIS 'BEGIN{printf "%.3f", a + b + c}')
echo "recompute spent=$spent held=$held this=$THIS total=$proj cap=$CAP"
awk -v p=$proj -v c=$CAP 'BEGIN{exit !(p <= c)}' || stop "the recompute $proj passes the cap $CAP"
# --- the deploys r1 made, reused
R2=$O/logs/envtest-r3
mkdir -p "$SHM_BASE" || stop "mkdir $SHM_BASE"
[ -d "$O" ] && [ -d "$C" ] && [ -d "$PRE" ] || stop "$O, $C or $PRE is missing (r1 made them)"
[ -e "$R2" ] && stop "$R2 exists (this connect runs once)"
[ -e "$O/envtest" ] && stop "$O/envtest exists"
[ -e "$O/submissions.log" ] && stop "$O/submissions.log exists (r1 submitted nothing)"
n=$(git -C "$C" status --porcelain --ignored | wc -l); h=$(git -C "$C" rev-parse HEAD); echo "deploy porcelain_ignored=$n head=$h"
[ "$n" = "0" ] && [ "$h" = "$M" ] || stop "the deploy is not clean at M"
mkdir "$R2" || stop "mkdir $R2"
cat > "$R2/bound.sha256" <<'SUMS'
7542a68dd344b4cb6252082bfa46d62f512f3c44875bb7d43f17c6368b04f880  2d-unfolding/cov2d/g2r/jobs/g2r_jobs.py
b3ad1d04e6f665b79566fac43f520d2a0329c9d66026f7793f1ab4cf5eb52483  2d-unfolding/cov2d/g2r/jobs/g2r_env.sh
21e4f4ac7330250eb84af653c5a8a0cc8d7fb013489a36d7610025dd539351c8  2d-unfolding/cov2d/g2r/jobs/g2r_job.sbatch
3971fe8596574b4e2c479011a7de422aae3d4fea696a076d68a2dc9ce0189d3f  2d-unfolding/cov2d/g2r/jobs/g2r_envtest.sbatch
3c129b3dd7abb6d47f821f0d61266474a4151dad180c187b8ac43b8730b97433  2d-unfolding/cov2d/g2r/jobs/g2r_prepare.sbatch
a9b2a2ba2f8a902ac9914554e4508dd5dd4fd32ff9f6e291cfb74b3c767c3bc1  2d-unfolding/cov2d/g2r/jobs/g2r_submit.sh
e226daf3f51954c7079cc7b3ab509e464865502f5dbde4acf11876409971dd67  2d-unfolding/re2/re2_driver.py
dbcc416d35565c183d73d6ce03a9efa89dddf8cbda618fa3e6eb00bbe08d28ec  2d-unfolding/cov2d/g2r/g2r.py
bb97fba12034e39c4b6dd5679b93f8259bcc4fab2b69890931c95c1311c7eb57  2d-unfolding/cov2d/g2r/g2r_prepare.py
590ffba1cb8cb65410abee93cd8b3c679b05d4e77155591d619a2f24ba4a0cf1  2d-unfolding/cov2d/g2r/g2r_readout.py
09bcc7b9ca16fd4f7d802ea00d77e7720bc4777041194664911dd7440f9a4936  2d-unfolding/cov2d/jobs/cov2d_jobs.py
3809113878eebefd906155f09cc5ec17745654fc644e074b312590035f0ace5a  2d-unfolding/cov2d/jobs/cov2d_env.sh
76cbceba395bc6bbf8fc5cce9cf44fc0f21354dff8591cbdee578e0fddcaf8ed  2d-unfolding/cov2d/cov2d.py
c085b51f46afe3675077756aac982d5a7ebc87a5801dd7cbde79dd0f867bd7de  2d-unfolding/cov2d/cov2d_receipt.py
30162f57771c9d5a1206eae623a7eb3fc80ac3f0bb150c82fb561be7254b510b  nd-unfolding/mnv_guarded_run.py
6e4ed0f1d7f55b7bfe2f26752eeb28bb9cbe33325a9d91cc7c06d9494a0b0a70  nd-unfolding/fd_rpd_inputs.py
526b70e0cda78ef476f921d817ff264f67f1b8844b241ca4e65083a196a1127b  docs/orchestration/state/2d-closeout/stageF/methods/re2/run/partb_runs.tsv
ea3c6998d33f45c831b80da5e5228032a19fc392018ede54a7f52f2f283d1d48  setup_salloc_env.sh
e96234124a31edd7a8dd61fdb16cb48a5b28cbd1b90202f59b0095868378227a  unbinned_unfolding/python/omnifold.py
SUMS
(cd "$C" && sha256sum -c "$R2/bound.sha256") || stop "bound blobs differ at M"
n=$(git -C "$PRE" status --porcelain --ignored | wc -l); h=$(git -C "$PRE" rev-parse HEAD); echo "deploy-pre porcelain_ignored=$n head=$h"
[ "$n" = "0" ] && [ "$h" = "$PRE_M" ] || stop "the pre-patch deploy is not clean at PRE_M"
printf '%s\n' "938c53c5a018d20f5b148f6bdc2949e987a60085c5d0b7913ccdd5bb438b5a3b  2d-unfolding/re2/re2_driver.py" \
    "e96234124a31edd7a8dd61fdb16cb48a5b28cbd1b90202f59b0095868378227a  unbinned_unfolding/python/omnifold.py" > "$R2/pre.sha256"
(cd "$PRE" && sha256sum -c "$R2/pre.sha256") || stop "the pre-patch deploy's driver or helper differs"
# --- the four suites under the jobs' environment (root_6_28 + MAT): numpy 1.26
(
    source "$A/setup_salloc_env.sh" > /dev/null 2>&1
    export PYTHONHASHSEED=0 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
    # >>> the suites' place (run verbatim by test_envtest_r2_tmpdir.sh): the open audit refuses plain opens under
    # /global/cfs and /pscratch, so the suites run from a shared clone of $C at M, with their TMPDIR, both in one
    # fresh directory under /dev/shm, removed on exit (logged)
    SR=$(mktemp -d "$SHM_BASE/josephrb-g2r-suites.XXXXXX") || exit 3
    case "$(realpath "$SR")/" in
        /global/cfs/*|/pscratch/*|"$(realpath "$O")"/*|"$(realpath "$C")"/*)
            echo "the suites' place $SR is under a guarded tree, \$O or \$C"; rm -rf "$SR"; exit 6 ;;
    esac
    trap 'rm -rf "$SR"; echo "removed the suites place $SR rc=$? left=$([ -e "$SR" ] && echo yes || echo no)"' EXIT
    export TMPDIR=$SR/tmp; mkdir "$TMPDIR" || exit 3
    SC=$SR/repo
    git clone --quiet --shared --no-checkout "$C" "$SC" && git -C "$SC" checkout --quiet --detach "$M" || exit 7
    n=$(git -C "$SC" status --porcelain --ignored | wc -l); h=$(git -C "$SC" rev-parse HEAD)
    [ "$n" = "0" ] && [ "$h" = "$M" ] || { echo "the suites' clone is not clean at M ($n, $h)"; exit 7; }
    (cd "$SC" && sha256sum -c "$R2/bound.sha256" > "$SR/bound-check.txt" 2>&1) || { cat "$SR/bound-check.txt"; exit 7; }
    echo "suites place=$SR clone head=$h porcelain_ignored=$n bound sums $(grep -c ': OK$' "$SR/bound-check.txt") OK TMPDIR=$TMPDIR"
    # <<< the suites' place
    v=$(python -c 'import sys, numpy, ROOT; print(sys.version.split()[0], numpy.__version__, ROOT.gROOT.GetVersion())') || exit 3
    echo "suites env: python numpy ROOT = $v"
    # the atime probe: the glue tests' own pattern (their O_NOATIME patched to 0) must not move an atime here
    mkdir "$TMPDIR/atprobe" || exit 10
    python - "$TMPDIR/atprobe" <<'PROBE' || exit 10
import os, sys, time
d, moved, n = sys.argv[1], 0, 40
for i in range(n):
    p = os.path.join(d, f"f{i}")
    with open(p, "wb") as f:
        f.write(b"x" * 4096)
    with open(p, "rb") as f:
        f.read()
    time.sleep(0.01)
    a0 = os.stat(p).st_atime_ns
    with open(p, "rb") as f:
        f.read()
    moved += os.stat(p).st_atime_ns != a0
    os.remove(p)
print(f"atime probe: moved {moved} of {n} in {d}")
sys.exit(1 if moved else 0)
PROBE
    rmdir "$TMPDIR/atprobe" || exit 10
    case "$(echo "$v" | awk '{print $2}')" in 1.26.*) ;; *) echo "numpy is not 1.26"; exit 4 ;; esac
    rc=0
    for t in "2d-unfolding/cov2d/g2r/tests test_g2r" "2d-unfolding/re2/tests test_re2_miss_map" \
             "2d-unfolding/cov2d/g2r/tests test_g2r_glue" "2d-unfolding/cov2d/g2r/tests test_g2r_jobs"; do
        set -- $t
        (cd "$SC/$1" && python -B -m unittest "$2" > "$R2/suite-$2.log" 2>&1); r=$?
        echo "suite $2 rc=$r $(grep -E '^(Ran|OK|FAILED)' "$R2/suite-$2.log" | tr '\n' ' ')"
        grep -q 'skipped' "$R2/suite-$2.log" && { echo "suite $2 skipped tests"; r=5; }
        [ "$r" = 0 ] || rc=1
    done
    n=$(git -C "$SC" status --porcelain --ignored | wc -l); echo "suites clone porcelain_ignored after the suites=$n"
    [ "$n" = "0" ] || { git -C "$SC" status --porcelain --ignored | head; rc=1; }
    exit $rc
); src=$?
[ "$src" = 0 ] || stop "the suites under the jobs' environment (rc $src)"
n=$(git -C "$C" status --porcelain --ignored | wc -l); echo "deploy porcelain_ignored after the suites=$n"
[ "$n" = "0" ] || { git -C "$C" status --porcelain --ignored | head; stop "the suites left files in the deploy"; }
# --- the one submission
bash "$C/2d-unfolding/cov2d/g2r/jobs/g2r_submit.sh" "$C" "$M" envtest; rc=$?; echo "submit envtest rc=$rc"
[ -s "$O/submissions.log" ] && cat "$O/submissions.log"
id=$(awk '/ job=envtest / {for (i = 1; i <= NF; i++) if ($i ~ /^id=/) print substr($i, 4)}' "$O/submissions.log" 2>/dev/null | tail -1)
[ -n "$id" ] && { scontrol show job "$id" | grep -oE "(JobId|JobName|JobState|TimeLimit|Partition|QOS|NumNodes|Account|OverSubscribe)=[^ ]*" | tr '\n' ' '; echo; }
echo "end=$(date -u +%FT%TZ)"; echo DONE
