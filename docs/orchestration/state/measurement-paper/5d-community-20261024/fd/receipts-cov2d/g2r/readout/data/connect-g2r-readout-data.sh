#!/bin/bash
# COV2D-G2R connect READOUT-<PH> (amendment 1 §3-§5; addendum J1 §6 "the readout runs on a login node and reads each
# product at its digest"; the director's ruling 4 of 2026-11-13): `g2r_readout.py data` (PH=data) or `g2r_readout.py
# tune --truth PH` (PH=G18 | AR23), one phase per connect (noatime_inputs repoints the rollup's globals: one phase per
# process). Login node, 0 node-h. connect-g2r-readout-{data,G18,AR23}.sh are this file with PH set; nothing else
# differs. DRAFT for coverage-5b-audit: not yet given a go.
# COV2D's readout pattern (connect-n-AR23.sh 47728db0, receipted): cov2d_blocks' open audit refuses every plain open
# under /global/cfs and /pscratch, so everything the readout opens plainly is put in one fresh directory W under
# /dev/shm: a fresh clone at M (REPO, so OUTA/budget_Q.json.gz at g2r_readout.py:285 and every committed record),
# TMPDIR (TemporaryDirectory at :203, :266), the products TSV (open at :161) and --out (np.savez and write_text at
# :249-251, :315 and Run.finish). Run.finish also STOPs on modules imported from outside the clone. The products
# themselves stay in $O/out and are read through O_NOATIME at their digests (read_pinned). After the process exits,
# the outputs are copied to $O/readout/<PH>/ and checked there, and only then is W removed (logged); if the copy-out
# fails, W keeps the outputs, readout.log and products.tsv and the log names it (coverage-5b-audit M2). The verdict
# accepts, per phase, exactly the verdicts main() returns 0 for and records the graded one (M1). The blocks between
# the >>> and <<< markers (the place, the verdict, the copy-out) are run verbatim by test_readout_place.sh.
# Before the readout: the fence (no rsn_, e96data, rdx_, t2a or cov2d* job queued or running, and no cov2d* job
# unended: every G2R job has ended); the clone clean at M with the 19 bound sums; the map sha256 from the committed
# prepare PASS on origin/main (g2r_jobs.py map-sha); the tables regenerated from the clone equal to $O/tables; the
# products TSV from the jobs' SHA256SUMS (g2r_jobs.py products refuses a run with no digest); the MAT pin and a MAT
# preflight on one real MnvH1D. Then the readout, nice 19, taskset -c 8-11, threads 1.
# Verdict: PASS (rc 0 and "G2R-<PHASE> verdict=PASS"); ATIME (rc 8: an input's atime moved: a STOP to the director);
# INVALID otherwise (rc 5, or a crash): to the director unrepaired, with the mechanism named.
# Run: setsid nohup bash /dev/shm/josephrb-g2r-readout-<PH>.sh >/dev/null 2>&1 </dev/null &
M=401733bce290ce122cfbf38f1526e120f174b3ec         # M_J1 (COV2D-G2R-BINDING-1.md:100, addendum J1, #1118)
PH=data
P=/pscratch/sd/j/josephrb; A=$P/MINERvA-OmniFold
O=$P/cov2d-g2r-20261112; C=$P/cov2d-g2r-deploy-j1
URL=https://github.com/josephbaileyy/MINERvA-OmniFold
PY310=/global/homes/j/josephrb/.conda/envs/omnifold_py310/bin/python
SHM_BASE=/dev/shm
LOG=/dev/shm/josephrb-g2r-readout-$PH.log
RUN="nice -n 19 taskset -c 8-11"
RD=$O/readout/$PH
stop() { echo "STOP $*"; echo "READOUT-$PH INVALID (connect)"; echo "end=$(date -u +%FT%TZ)"; echo DONE; exit 2; }
case "$PH" in data) PHASE=DATA; ARGS="data" ;; G18|AR23) PHASE=TUNE; ARGS="tune --truth $PH" ;; *) echo "STOP PH is not set"; exit 2 ;; esac
[ -e "$LOG" ] && { echo "STOP $LOG exists"; exit 2; }
exec >> "$LOG" 2>&1
echo "host=$(hostname) start=$(date -u +%FT%TZ) pid=$$ user=$(id -un) M=$M PH=$PH"
# --- the fence
echo "squeue: [$(squeue --me -h -o '%i %j %T %l %D' | tr '\n' ';')]"
[ "$(squeue --me -h -o %j | grep -cE '^(rsn_|e96data|rdx_|t2a|cov2d)')" = "0" ] \
    || stop "an rsn_, e96data, rdx_, t2a or cov2d job is queued or running"
cv=$(sacct -X -n -P -S 2026-11-04 -u josephrb -o JobID,JobName,State | awk -F'|' '$2 ~ /^cov2d/ && $3 !~ /^(COMPLETED|FAILED|CANCELLED|TIMEOUT|OUT_OF_MEMORY|NODE_FAIL|PREEMPTED|BOOT_FAIL|DEADLINE)/')
[ -z "$cv" ] || stop "a cov2d job is unended: $cv"
[ -e "$RD" ] && stop "$RD exists (this connect runs once)"
[ -d "$O/out" ] && [ -s "$O/tables/runs_g2r.tsv" ] || stop "$O/out or $O/tables/runs_g2r.tsv is missing"
(
    # >>> the readout's place (run verbatim by test_readout_place.sh)
    W=$(mktemp -d "$SHM_BASE/josephrb-g2r-readout-$PH.XXXXXX") || exit 3
    case "$(realpath "$W")/" in
        /global/cfs/*|/pscratch/*|"$(realpath "$O")"/*|"$(realpath "$C")"/*)
            echo "the readout's place $W is under a guarded tree, \$O or \$C"; rm -rf "$W"; exit 6 ;;
    esac
    # the trap: the clone and TMPDIR always go; the rest of W (the outputs, readout.log, products.tsv) goes only if the
    # readout never started (.protect absent) or its copy-out verified (.copied); otherwise W stays and is named
    trap 'rm -rf "$W/deploy" "$W/tmp"; if [ ! -e "$W/.protect" ] || [ -e "$W/.copied" ]; then rm -rf "$W"; echo "removed the readout place $W rc=$? left=$([ -e "$W" ] && echo yes || echo no)"; else echo "KEPT the readout place $W (the copy-out did not verify): $(ls -A "$W" | tr "\n" " ")"; fi' EXIT
    mkdir "$W/tmp" "$W/out" || exit 3
    export TMPDIR=$W/tmp PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
    DD=$W/deploy
    git clone --quiet "$URL" "$DD" && git -C "$DD" -c advice.detachedHead=false checkout --quiet --detach "$M" || exit 7
    n=$(git -C "$DD" status --porcelain --ignored | wc -l); h=$(git -C "$DD" rev-parse HEAD)
    [ "$n" = "0" ] && [ "$h" = "$M" ] || { echo "the clone is not clean at M ($n, $h)"; exit 7; }
    cat > "$W/bound.sha256" <<'SUMS'
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
    (cd "$DD" && sha256sum -c "$W/bound.sha256" > "$W/bound-check.txt" 2>&1) || { cat "$W/bound-check.txt"; exit 7; }
    echo "readout place=$W clone head=$h porcelain_ignored=$n bound sums $(grep -c ': OK$' "$W/bound-check.txt") OK TMPDIR=$TMPDIR"
    # <<< the readout's place
    GJ=$DD/2d-unfolding/cov2d/g2r/jobs/g2r_jobs.py
    mapsha=$("$PY310" -B "$GJ" map-sha --deploy "$DD") || { echo "no committed prepare PASS with a map sha256: $mapsha"; exit 7; }
    [[ $mapsha =~ ^[0-9a-f]{64}$ ]] || { echo "map-sha printed '$mapsha'"; exit 7; }
    echo "map_sha256=$mapsha"
    "$PY310" -B "$GJ" tables --out "$W/tables" > /dev/null || exit 7
    for f in runs_g2r.tsv jobs_g2r.tsv; do cmp -s "$W/tables/$f" "$O/tables/$f" || { echo "$O/tables/$f is not the clone's"; exit 7; }; done
    "$PY310" -B "$GJ" products --runs "$W/tables/runs_g2r.tsv" --o "$O" --point "$PH" --out "$W/products.tsv" || exit 7
    echo "products.tsv $(wc -l < "$W/products.tsv" | tr -d ' ') rows sha256 $(sha256sum "$W/products.tsv" | cut -c1-64)"
    (cd "$DD" && git ls-tree -r HEAD 2d-unfolding/cov2d | grep -v __pycache__) > "$W/blobs.before"
    : > "$W/.protect"                              # from here, W's outputs are kept unless the copy-out verifies
    (
        "$PY310" -B -c "import sys; sys.path.insert(0, '$DD/nd-unfolding'); import fd_rpd_inputs as r; r.run_check_mat_setup(None)" || exit 7
        source "$A/setup_salloc_env.sh" > /dev/null 2>&1 || exit 3
        export TMPDIR=$W/tmp PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
        echo "python=$(command -v python) TMPDIR=$TMPDIR"
        python -c "import sys, numpy, ROOT; print(sys.version.split()[0], 'numpy', numpy.__version__, 'ROOT', ROOT.gROOT.GetVersion())" || exit 4
        python - <<'PYEOF' || exit 5
import hashlib, os, ROOT
src = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/baseline_flux/runEventLoopMC_1A.root"
fd = os.open(src, os.O_RDONLY | os.O_NOATIME); data = b""
while True:
  b = os.read(fd, 1 << 24)
  if not b: break
  data += b
os.close(fd)
print("MAT preflight file:", src, "sha256", hashlib.sha256(data).hexdigest())
dst = os.path.join(os.environ["TMPDIR"], "mat_preflight.root"); open(dst, "wb").write(data)
f = ROOT.TFile.Open(dst); h = f.Get("pTmu_reweightedflux_integrated")
print("MAT preflight:", type(h).__name__, h.ClassName(), h.GetNbinsX(), "bins")
assert h.ClassName().startswith("PlotUtils::MnvH1D"), h.ClassName()
os.remove(dst)
PYEOF
        cd "$DD/2d-unfolding/cov2d/g2r" && $RUN /usr/bin/time -v python -B g2r_readout.py $ARGS \
            --products "$W/products.tsv" --map-sha "$mapsha" --out "$W/out"
    ) > "$W/readout.log" 2>&1; rc=$?
    grep -v '^Warning in <TInterpreter::ReadRootmapFile>' "$W/readout.log" | tail -40
    # >>> the verdict (run by test_readout_place.sh on g2r_readout.main()'s own printed line and rc): main() returns 0
    # for any verdict but INVALID and STOP (g2r_readout.py:339): data's is PASS (:318), a tune's the grade's COVERS or
    # UNDER-COVERS (:257; fd_1b_mc.py:693), as COV2D's readout accepts (cov2d_readout.py:630); 8 if an atime moved
    case "$PHASE" in DATA) ok_re='PASS' ;; TUNE) ok_re='COVERS|UNDER-COVERS' ;; *) echo "PHASE '$PHASE' is unknown"; exit 7 ;; esac
    graded=$(sed -nE "s/^G2R-$PHASE verdict=([A-Z-]+) .*/\1/p" "$W/readout.log" | tail -1)
    if [ "$rc" = 0 ] && printf '%s\n' "$graded" | grep -qxE "$ok_re"; then V=PASS
    elif [ "$rc" = 8 ]; then V=ATIME
    else V=INVALID; fi
    echo "READOUT-$PH $V rc=$rc verdict=${graded:-none}"
    # <<< the verdict
    : > "$W/out.sha256"; if [ -n "$(ls -A "$W/out")" ]; then (cd "$W/out" && sha256sum -- * > "$W/out.sha256"); fi
    echo "outputs: $(wc -l < "$W/out.sha256" | tr -d ' ')"; cat "$W/out.sha256"
    n=$(git -C "$DD" status --porcelain --ignored | wc -l); echo "clone porcelain_ignored after=$n head=$(git -C "$DD" rev-parse HEAD)"
    (cd "$DD" && git ls-tree -r HEAD 2d-unfolding/cov2d | grep -v __pycache__) > "$W/blobs.after"
    cmp -s "$W/blobs.before" "$W/blobs.after" && echo "blobs unchanged" || echo "blobs CHANGED"
    # >>> the copy-out (run by test_readout_place.sh), after the process has exited: the outputs, the products TSV,
    # the readout log and the sums; .copied only once they verify in $RD
    mkdir -p "$O/readout" && mkdir "$RD" || { echo "mkdir $RD failed"; exit 9; }
    cp -p "$W/products.tsv" "$W/readout.log" "$W/out.sha256" "$RD/" || { echo "the copy-out failed"; exit 9; }
    if [ -n "$(ls -A "$W/out")" ]; then cp -p "$W"/out/* "$RD/" || { echo "the copy-out failed"; exit 9; }; fi
    if [ -s "$RD/out.sha256" ]; then (cd "$RD" && sha256sum -c out.sha256) || { echo "the copy-out differs"; exit 9; }; fi
    : > "$W/.copied"
    echo "copied to $RD: $(ls "$RD" | tr '\n' ' ')"
    # <<< the copy-out
    case $V in PASS) exit 0 ;; ATIME) exit 8 ;; *) exit 5 ;; esac
); xrc=$?
echo "readout subshell rc=$xrc"
case $xrc in
    0) echo "READOUT-$PH PASS" ;;
    8) echo "READOUT-$PH ATIME: a STOP to the director" ;;
    5) echo "READOUT-$PH INVALID: to the director unrepaired" ;;
    *) echo "READOUT-$PH INVALID (connect rc $xrc)" ;;
esac
echo "end=$(date -u +%FT%TZ)"; echo DONE
