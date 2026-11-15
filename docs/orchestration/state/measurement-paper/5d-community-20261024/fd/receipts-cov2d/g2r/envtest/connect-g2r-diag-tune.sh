#!/bin/bash
# COV2D-G2R connect DIAG-TUNE (the director's approval, 2026-11-13, after envtest-r2's STOP): a diagnostic, no record
# used for a claim. envtest-r2 (2ef9ce12) STOPped because test_g2r_glue's PhaseTune record said STOP, not UNDER-COVERS
# (test_g2r_glue.py:283), on the cluster only; locally the same setUpClass gives UNDER-COVERS with stop [], atime_moved
# [] and no refusals. This runs ONLY PhaseTune.setUpClass, through diag_phasetune.py (sha256 4558b490..., embedded
# below and checked), in envtest-r2's suites' place (the block between the >>> and <<< markers, copied byte for byte:
# a shared clone of $C at M and TMPDIR under /dev/shm, removed on exit, logged), under the jobs' environment, and
# prints the record's verdict, its stop list (Run.finish's atime, open-audit and outside-the-clone stops and the
# phase's own), controls_failed, atime_moved with paths, atime_checked, the open audit's refusals and counts, and the
# modules' paths. Login node, 0 node-h, no submission. It reads $C only through git (the clone's objects) and its
# own records go to $O/logs/diag-tune/, refused if that exists.
# Run: setsid nohup bash /dev/shm/josephrb-g2r-diag-tune.sh >/dev/null 2>&1 </dev/null &
M=401733bce290ce122cfbf38f1526e120f174b3ec         # M_J1
P=/pscratch/sd/j/josephrb; A=$P/MINERvA-OmniFold
O=$P/cov2d-g2r-20261112; C=$P/cov2d-g2r-deploy-j1
DIAG_SHA=4558b4905c5104ec4d7b86a627105b4aa331d5184d4b4a379a5a184bd9b8a56c
LOG=/dev/shm/josephrb-g2r-diag-tune.log
SHM_BASE=/dev/shm                                  # the suites' place parent (outside GUARDED)
stop() { echo "STOP $*"; echo "end=$(date -u +%FT%TZ)"; echo DONE; exit 2; }
[ -e "$LOG" ] && { echo "STOP $LOG exists"; exit 2; }
exec >> "$LOG" 2>&1
echo "host=$(hostname) start=$(date -u +%FT%TZ) pid=$$ user=$(id -un) M=$M"
# --- the fence
echo "squeue: [$(squeue --me -h -o '%i %j %T %l %D' | tr '\n' ';')]"
[ "$(squeue --me -h -o %j | grep -cE '^(rsn_|e96data|rdx_|t2a|cov2d)')" = "0" ] \
    || stop "an rsn_, e96data, rdx_, t2a or cov2d job is queued or running"
cv=$(sacct -X -n -P -S 2026-11-04 -u josephrb -o JobID,JobName,State | awk -F'|' '$2 ~ /^cov2d/ && $3 !~ /^(COMPLETED|FAILED|CANCELLED|TIMEOUT|OUT_OF_MEMORY|NODE_FAIL|PREEMPTED|BOOT_FAIL|DEADLINE)/')
[ -z "$cv" ] || stop "a cov2d job is unended: $cv"
# --- the deploy, read only through git
R2=$O/logs/diag-tune
[ -d "$O" ] && [ -d "$C" ] || stop "$O or $C is missing"
[ -e "$R2" ] && stop "$R2 exists (this connect runs once)"
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
(cd "$C" && sha256sum -c "$R2/bound.sha256" > /dev/null) || stop "bound blobs differ at M"
# --- PhaseTune's setUpClass under the jobs' environment, from the place
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
    echo "env: python numpy ROOT = $v"
    cat > "$SR/diag_phasetune.py" <<'PYEOF'
"""Diagnostic for envtest-r2's STOP: run test_g2r_glue.PhaseTune's setUpClass only and print why its record says
what it says (stop, controls_failed, atime_moved, the open audit's refusals and counts). Read-only; writes only under
TMPDIR (the test's own TemporaryDirectory).    cd <clone>/2d-unfolding/cov2d/g2r/tests && python -B diag_phasetune.py"""
import json
import sys
sys.path.insert(0, ".")
import test_g2r_glue as t  # noqa: E402
C = t.PhaseTune
try:
    C.setUpClass()
    rec = C.rec
    print("DIAG", json.dumps({k: rec.get(k) for k in ("verdict", "verdict_graded", "stop", "controls_failed",
                                                      "atime_moved", "atime_checked", "open_audit", "modules")},
                             indent=1, default=str))
finally:
    try:
        C.tearDownClass()
    except Exception as exc:
        print("teardown", type(exc).__name__, exc)
PYEOF
    got=$(sha256sum "$SR/diag_phasetune.py" | cut -c1-64)
    [ "$got" = "$DIAG_SHA" ] && echo "DIAG-SHA OK $got" || { echo "diag_phasetune.py is $got"; exit 8; }
    (cd "$SC/2d-unfolding/cov2d/g2r/tests" && python -B "$SR/diag_phasetune.py" > "$R2/diag.log" 2>&1); r=$?
    echo "diag rc=$r"
    grep -v '^Warning in <TInterpreter::ReadRootmapFile>' "$R2/diag.log"
    n=$(git -C "$SC" status --porcelain --ignored | wc -l); echo "suites clone porcelain_ignored after=$n"
    exit $r
); drc=$?
echo "diag subshell rc=$drc"
n=$(git -C "$C" status --porcelain --ignored | wc -l); echo "deploy porcelain_ignored after=$n"
echo "end=$(date -u +%FT%TZ)"; echo DONE
