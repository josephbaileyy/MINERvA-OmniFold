#!/bin/bash
# Harness for ptmc_remote.sh (a harmless-worker test, run in debian:bookworm-slim). A copy of the script with only its
# path and pin constants substituted runs against stubs:
#   sacct, squeue, sbatch, git, id, the conda hook and python, all driven by environment variables.
# Real dd (iflag=noatime), sha256sum, stat, tar and date are used. Every gate is exercised: each STOP case must exit
# non-zero, print its STOP, and leave the state it must not change unchanged.
#   docker run --rm -v DIR:/h debian:bookworm-slim bash /h/harness_remote.sh
set -u
H=/tmp/hz; rm -rf $H; mkdir -p $H/bin $H/src
pass=0; fail=0
ok() { if [ "$1" = 0 ]; then pass=$((pass+1)); echo "ok   $2"; else fail=$((fail+1)); echo "FAIL $2"; fi; }
# sources and their pins
printf 'cv-bytes' > $H/src/cv; printf 'mc-bytes' > $H/src/mc; printf 'rows' > $H/src/rows; printf 'join' > $H/src/join
printf 'lib' > $H/src/lib
s() { /usr/bin/sha256sum < "$1" | cut -d' ' -f1; }
# stubs
cat > $H/bin/sacct <<'S'
#!/bin/bash
# the fence (-X -S ...) prints SACCT_OUT; a job's accounting (-j N) prints SACCT_J
case " $* " in
  *" -j "*) [ -n "${SACCT_J_FAIL:-}" ] && exit 1
            n=$(printf '%s\n' "$@" | grep -A1 -x -- -j | tail -1); v=SACCT_J_$n
            if [ -n "${!v+x}" ]; then printf '%b' "${!v}"; else printf '%b' "${SACCT_J-12345|ptmc_pilot|COMPLETED|0:0|1500|2|s|e\n}"; fi ;;
  *) [ -n "${SACCT_FAIL:-}" ] && exit 1; printf '%b' "${SACCT_OUT:-}" ;;
esac
S
cat > $H/bin/squeue <<'S'
#!/bin/bash
[ -n "${SQUEUE_FAIL:-}" ] && exit 1
printf '%b' "${SQUEUE_OUT:-}"
S
cat > $H/bin/sbatch <<'S'
#!/bin/bash
echo "$*" >> /tmp/hz/sbatch.args
[ -n "${SBATCH_FAIL:-}" ] && exit 1
[ -n "${SBATCH_BLOCK:-}" ] && mkdir -p "$SBATCH_BLOCK"
printf '%s\n' "${SBATCH_OUT:-12345}"
S
cat > $H/bin/id <<'S'
#!/bin/bash
echo "${ID_USER:-josephrb}"
S
cat > $H/bin/hostname <<'S'
#!/bin/bash
[ -n "${HOST_FAIL:-}" ] && exit 1
echo "${HOST:-login27}"
S
cat > $H/bin/awk <<'S'
#!/bin/bash
[ -n "${AWK_FAIL:-}" ] && exit 2
exec /usr/bin/awk "$@"
S
cat > $H/bin/sha256sum <<'S'
#!/bin/bash
[ -n "${SHA_FAIL:-}" ] && [ $# = 0 ] && exit 1
exec /usr/bin/sha256sum "$@"
S
cat > $H/bin/stat <<'S'
#!/bin/bash
[ -n "${STAT_FAIL:-}" ] && exit 1
exec /usr/bin/stat "$@"
S
cat > $H/bin/git <<'S'
#!/bin/bash
# clone URL DEST | -C DIR rev-parse HEAD | -C DIR status ... | -C DIR -c ... checkout -q REV
if [ "$1" = clone ]; then
  d=${@: -1}; mkdir -p "$d/2d-unfolding/ptmc/launch"
  cat > "$d/2d-unfolding/ptmc/make_tree.sh" <<'M'
#!/bin/bash
[ -n "${MAKE_TREE_FAIL:-}" ] && { echo "REFUSED: stub"; exit 3; }
env | grep -E '^(OMP|MKL|OPENBLAS|NUMEXPR)_NUM_THREADS=' | sort > /tmp/hz/env.make_tree
d=$1; mkdir -p $d/2d-unfolding/re2 $d/2d-unfolding/ref_c2c1 $d/unbinned_unfolding/python $d/2d-unfolding/uq $d/2d-unfolding/oofvc
for f in 2d-unfolding/re2/re2_driver.py 2d-unfolding/ref_c2c1/config.json 2d-unfolding/ref_c2c1/ref_c2c1.py \
  2d-unfolding/ref_c2c1/ref_c2c1_read.py unbinned_unfolding/python/omnifold.py 2d-unfolding/compare_to_paper_fullcov.py \
  2d-unfolding/uq/reported_cells.py 2d-unfolding/oofvc/oofvc_lib.py; do echo "$f" > $d/$f; done
[ -n "${MAKE_TREE_EXTRA:-}" ] && echo extra > $d/2d-unfolding/extra.py
echo "tree $d"
M
  : > "$d/2d-unfolding/ptmc/launch/pilot.sbatch"; : > "$d/2d-unfolding/ptmc/launch/replicas.sbatch"
  : > "$d/2d-unfolding/ptmc/launch/ptmc_pilot_post.py"; : > "$d/2d-unfolding/ptmc/launch/ptmc_stage_d4.py"
  exit 0
fi
case "$*" in
  *rev-parse*) [ -n "${GIT_REV_FAIL:-}" ] && exit 1; echo "${GIT_HEAD:-abc123}" ;;
  *status*) [ -n "${GIT_STATUS_FAIL:-}" ] && exit 1; printf '%s' "${GIT_STATUS:-}" ;;
  *checkout*) exit 0 ;;
  *) exit 1 ;;
esac
S
cat > $H/bin/conda <<'S'
#!/bin/bash
# `conda shell.bash hook` prints the function the script evals
[ "$1 $2" = "shell.bash hook" ] && echo 'conda() { return ${CONDA_RC:-0}; }'
S
cat > $H/bin/python3 <<'S'
#!/bin/bash
env | grep -E '^(OMP|MKL|OPENBLAS|NUMEXPR)_NUM_THREADS=' | sort > /tmp/hz/env.python
echo "$*" >> /tmp/hz/python.args
out=""; re=""; prev=""
for a in "$@"; do case "$prev" in --out) out=$a;; --recheck) re=$a;; esac; prev=$a; done
case "$*" in
  *ptmc_pilot_post.py*)
    if [ -n "$re" ]; then
      echo "{\"recheck\": \"${RECHECK:-SAME}\", \"time_limit_minutes\": ${RECHECK_L:-145}}"; exit ${RECHECK_RC:-0}
    fi
    [ "${POST_RC:-0}" = 0 ] && { echo PROCEED > $out/PROCEED; echo "${POST_L:-145}" > $out/time_limit_minutes; }
    if [ -n "${POST_DECISION_DIR:-}" ]; then mkdir $out/decision.json; else echo '{"verdict": "stub"}' > $out/decision.json; fi
    exit ${POST_RC:-0} ;;
  *ptmc_stage_d4.py*)
    [ "${D4_RC:-0}" = 0 ] || exit ${D4_RC}; mkdir -p $out; echo '{}' > $out/manifest.json; exit 0 ;;
esac
exit 1
S
chmod +x $H/bin/*
export PATH=$H/bin:$PATH USER=josephrb
mk() {  # the script with its constants substituted (nothing else changes)
  sed -e "s#^R=.*#R=$H/R#" -e "s#^TOOLC=.*#TOOLC=abc123#" -e "s#^URL=.*#URL=$H/repo#" \
      -e "s#^CV_SRC=.*#CV_SRC=$H/src/cv#" -e "s#^MC_SRC=.*#MC_SRC=$H/src/mc#" \
      -e "s#^ROWS_SRC=.*#ROWS_SRC=$H/src/rows#" -e "s#^JOIN_SRC=.*#JOIN_SRC=$H/src/join#" \
      -e "s#^CV_SHA=.*#CV_SHA=${CVPIN:-$(s $H/src/cv)}#" -e "s#^MC_SHA=.*#MC_SHA=$(s $H/src/mc)#" \
      -e "s#^ROWS_SHA=.*#ROWS_SHA=$(s $H/src/rows)#" -e "s#^JOIN_SHA=.*#JOIN_SHA=$(s $H/src/join)#" \
      -e "s#^LIB=.*#LIB=$H/src/lib#" -e "s#^LIB_SHA=.*#LIB_SHA=${LIBPIN:-$(s $H/src/lib)}#" \
      -e "s#^DRIVER_SHA=.*#DRIVER_SHA=${DRVPIN:-$(printf '2d-unfolding/re2/re2_driver.py\n' | /usr/bin/sha256sum | cut -d' ' -f1)}#" \
      -e "s#^PY=.*#PY=$H/bin/python3#" -e "s#^CONDA_HOOK=.*#CONDA_HOOK=$H/bin/conda#" /h/ptmc_remote.sh > $H/r.sh
}
run() { mk; out=$(bash $H/r.sh $H/r.sh "$@" 2>&1); rc=$?; }
has() { printf '%s\n' "$out" | grep -q -- "$1"; }
LIVE='1|cov2d-AR23|RUNNING\n'
J2='12345|ptmc_pilot|COMPLETED|0:0|1500|2|s|e\n12346|ptmc_reps|COMPLETED|0:0|8000|5|s|e\n'
fresh() { rm -rf $H/R $H/sbatch.args $H/python.args $H/env.*; }
setup_ok() { fresh; run setup; [ "$rc" = 0 ] || { echo "setup failed: $out"; exit 1; }; }
staged() { setup_ok; run prestage; HOST=dtn01 run stage; [ "$rc" = 0 ] || { echo "stage failed: $out"; exit 1; }; }
piloted() { staged; run pilot; mkdir -p $H/R/units; }
proceeded() { piloted; run post-pilot; [ "$rc" = 0 ] || { echo "post-pilot failed: $out"; exit 1; }; rm -f $H/sbatch.args; }
# --- every mode
fresh; run bogus; [ "$rc" != 0 ] && has "STOP: mode"; ok $? "unknown mode: STOP"
fresh; ID_USER=other run setup; [ "$rc" != 0 ] && has "STOP: user" && [ ! -e $H/R ]; ok $? "wrong user: STOP"
fresh; HOST_FAIL=1 run setup; [ "$rc" != 0 ] && has "hostname failed" && [ ! -e $H/R ]; ok $? "a failed hostname: STOP"
fresh; HOST=dtn01 run setup; [ "$rc" != 0 ] && has "runs on a login node" && [ ! -e $H/R ]; ok $? "setup on a DTN: STOP"
mk; sed -i 's#^TOOLC=.*#TOOLC=__TOOL_COMMIT__#' $H/r.sh; out=$(bash $H/r.sh $H/r.sh setup 2>&1); rc=$?
[ "$rc" != 0 ] && has "not filled in"; ok $? "an unfilled tool commit: STOP"
mk; sed -i 's#^DRIVER_SHA=.*#DRIVER_SHA=__DRIVER_SHA256__#' $H/r.sh; out=$(bash $H/r.sh $H/r.sh setup 2>&1); rc=$?
[ "$rc" != 0 ] && has "not filled in"; ok $? "an unfilled driver pin: STOP"
# --- setup (login): no copies
setup_ok; [ -e $H/R/logs/setup.done ] && [ -d $H/R/claims/setup ] && [ -z "$(ls -A $H/R/stage)" ]
ok $? "setup: rc 0, claimed, the stage left empty (no copy on a login node)"
[ "$(cat $H/env.make_tree)" = "$(printf 'MKL_NUM_THREADS=1\nNUMEXPR_NUM_THREADS=1\nOMP_NUM_THREADS=1\nOPENBLAS_NUM_THREADS=1')" ]
ok $? "setup: make_tree runs with one thread"
run setup; [ "$rc" != 0 ] && has "STOP: $H/R exists"; ok $? "setup again: STOP, R exists"
fresh; SACCT_OUT=$LIVE run setup; [ "$rc" != 0 ] && has "a fenced job is live" && [ ! -e $H/R ]; ok $? "setup: a live cov2d job STOPs before R is made"
fresh; SACCT_OUT='1|t2a_x|PENDING\n' run setup; [ "$rc" != 0 ] && has "a fenced job is live"; ok $? "setup: a pending t2a job STOPs"
fresh; SACCT_OUT='1|cov2d-x|\n' run setup; [ "$rc" != 0 ] && has "a fenced job is live"; ok $? "setup: an empty state is live"
fresh; SACCT_FAIL=1 run setup; [ "$rc" != 0 ] && has "sacct failed" && [ ! -e $H/R ]; ok $? "setup: a failed sacct STOPs"
fresh; AWK_FAIL=1 run setup; [ "$rc" != 0 ] && has "awk failed" && [ ! -e $H/R ]; ok $? "setup: a failed awk STOPs"
fresh; SQUEUE_OUT='ptmc_pilot\n' run setup; [ "$rc" != 0 ] && has "a ptmc job is queued" && [ ! -e $H/R ]; ok $? "setup: a queued ptmc job STOPs"
fresh; SQUEUE_FAIL=1 run setup; [ "$rc" != 0 ] && has "squeue failed"; ok $? "setup: a failed squeue STOPs"
fresh; LIBPIN=0000 run setup; [ "$rc" != 0 ] && has "libRooUnfold.so differs" && [ ! -e $H/R/logs/setup.done ]; ok $? "setup: a library pin mismatch STOPs"
fresh; DRVPIN=0000 run setup; [ "$rc" != 0 ] && has "the deployed driver is not 0000" && [ ! -e $H/R/logs/setup.done ]; ok $? "setup: a driver pin mismatch STOPs"
fresh; MAKE_TREE_FAIL=1 run setup; [ "$rc" != 0 ] && has "STOP: make_tree" && [ ! -e $H/R/logs/setup.done ]; ok $? "setup: make_tree's refusal STOPs"
fresh; GIT_HEAD=def456 run setup; [ "$rc" != 0 ] && has "not at abc123"; ok $? "setup: a clone at the wrong commit STOPs"
fresh; GIT_REV_FAIL=1 run setup; [ "$rc" != 0 ] && has "git rev-parse failed"; ok $? "setup: a failed rev-parse STOPs"
fresh; GIT_STATUS=' M x' run setup; [ "$rc" != 0 ] && has "not clean"; ok $? "setup: a dirty clone STOPs"
fresh; GIT_STATUS_FAIL=1 run setup; [ "$rc" != 0 ] && has "git status failed"; ok $? "setup: a failed git status STOPs"
fresh; SHA_FAIL=1 run setup; [ "$rc" != 0 ] && has "sha256 of libRooUnfold.so failed"; ok $? "setup: a failed hash STOPs"
# --- prestage (login) and stage (DTN)
fresh; mkdir -p $H/R/stage $H/R/logs; run prestage; [ "$rc" != 0 ] && has "setup has not run"; ok $? "prestage before setup: STOP"
setup_ok; rmdir $H/R/stage; run prestage; [ "$rc" != 0 ] && has "ls of the stage failed" && [ ! -e $H/R/logs/prestage.epoch ]; ok $? "prestage: a failed ls of the stage STOPs"
setup_ok; SACCT_OUT=$LIVE run prestage; [ "$rc" != 0 ] && has "fenced job is live" && [ ! -e $H/R/logs/prestage.epoch ]; ok $? "prestage: a live cov2d job STOPs, no fence record"
HOST=dtn01 run prestage; [ "$rc" != 0 ] && has "runs on a login node"; ok $? "prestage on a DTN: STOP"
run stage; [ "$rc" != 0 ] && has "stage runs on a DTN"; ok $? "stage on a login node: STOP"
HOST=dtn01 run stage; [ "$rc" != 0 ] && has "prestage has not run" && [ ! -e $H/R/claims/stage ]; ok $? "stage without prestage: STOP"
run prestage; [ "$rc" = 0 ] && [ -s $H/R/logs/prestage.epoch ]; ok $? "prestage: the fence recorded"
run prestage; [ "$rc" = 0 ] && [ "$(wc -l < $H/R/logs/prestage.record)" = 2 ]; ok $? "prestage: repeatable before stage, every fence recorded"
echo $(( $(date -u +%s) - 1000 )) > $H/R/logs/prestage.epoch; HOST=dtn01 run stage
[ "$rc" != 0 ] && has "s old (limit 900)" && [ ! -e $H/R/claims/stage ] && [ -z "$(ls -A $H/R/stage)" ]; ok $? "stage: a stale fence STOPs, nothing claimed or copied"
echo 12x > $H/R/logs/prestage.epoch; HOST=dtn01 run stage; [ "$rc" != 0 ] && has "prestage.epoch '12x'"; ok $? "stage: a malformed fence record STOPs"
echo $(( $(date -u +%s) + 100 )) > $H/R/logs/prestage.epoch; HOST=dtn01 run stage; [ "$rc" != 0 ] && has "limit 900"; ok $? "stage: a fence from the future STOPs"
run prestage; touch $H/R/stage/stray; HOST=dtn01 run stage; [ "$rc" != 0 ] && has "the stage is not empty" && [ ! -e $H/R/claims/stage ]; ok $? "stage: a non-empty stage STOPs"
rm $H/R/stage/stray
setup_ok; run prestage; CVPIN=0000 HOST=dtn01 run stage; [ "$rc" != 0 ] && has "is not 0000" && [ ! -e $H/R/stage/ready ]; ok $? "stage: a CV pin mismatch STOPs, no ready"
setup_ok; run prestage; mv $H/src/cv $H/src/cv.real; ln -s $H/src/cv.real $H/src/cv; HOST=dtn01 run stage
[ "$rc" != 0 ] && has "absent or a symlink" && [ ! -e $H/R/stage/ready ]; ok $? "stage: a symlinked source STOPs"
rm $H/src/cv; mv $H/src/cv.real $H/src/cv
setup_ok; run prestage; STAT_FAIL=1 HOST=dtn01 run stage; [ "$rc" != 0 ] && has "STOP: stat $H/src/cv (before the copy)" && [ ! -e $H/R/stage/ready ]; ok $? "stage: a failed stat of a source STOPs"
setup_ok; run prestage; SHA_FAIL=1 HOST=dtn01 run stage; [ "$rc" != 0 ] && has "sha256 of" && [ ! -e $H/R/stage/ready ]; ok $? "stage: a failed re-hash STOPs"
setup_ok; run prestage; HOST=dtn01 run stage; [ "$rc" = 0 ] && [ -e $H/R/stage/ready ] && cmp -s $H/R/stage/runEventLoopOmniFold_MEFHC.root $H/src/cv
ok $? "stage: rc 0, ready, the CV copy byte-identical"
has "pre  $H/src/cv|atime=" && has "post $H/src/cv|atime="; ok $? "stage: the source's atime is printed before and after"
[ "$(stat -c %a $H/R/stage/oofvc_rows.npz) $(stat -c %a $H/R/stage/runEventLoopOmniFold_MEFHC.root)" = "400 400" ]; ok $? "stage: the copies are read-only"
HOST=dtn01 run stage; [ "$rc" != 0 ] && has "already claimed\|not empty"; ok $? "stage again: STOP"
run prestage; [ "$rc" != 0 ] && has "stage is claimed"; ok $? "prestage after stage: STOP"
# --- pilot
staged; run pilot; [ "$rc" = 0 ] && [ "$(cat $H/R/logs/pilot.jobid)" = 12345 ] && grep -q -- '-N 2 -t 60 .*pilot.sbatch' $H/sbatch.args
ok $? "pilot: submitted on -N 2 -t 60, jobid recorded"
run pilot; [ "$rc" != 0 ] && has "has been submitted"; ok $? "pilot again: STOP"
staged; echo tampered >> $H/R/deploy/2d-unfolding/re2/re2_driver.py; run pilot
[ "$rc" != 0 ] && has "deploy tree differs" && [ ! -e $H/R/logs/pilot.jobid ]; ok $? "pilot: a changed deploy file STOPs"
staged; echo "$(printf x%.0s $(seq 64))  2d-unfolding/extra.py" >> $H/R/logs/deploy.sha256; run pilot
[ "$rc" != 0 ] && has "do not list exactly" && [ ! -e $H/R/logs/pilot.jobid ]; ok $? "pilot: an extra deploy digest STOPs"
staged; sed -i '/oofvc_lib.py$/d' $H/R/logs/deploy.sha256; run pilot; [ "$rc" != 0 ] && has "do not list exactly"; ok $? "pilot: a missing deploy digest STOPs"
staged; rm $H/R/stage/ready; run pilot; [ "$rc" != 0 ] && has "not ready"; ok $? "pilot: no ready STOPs"
staged; chmod u+w $H/R/stage/join.json; echo x >> $H/R/stage/join.json; run pilot; [ "$rc" != 0 ] && has "staged join.json differs"; ok $? "pilot: a changed staged file STOPs"
staged; SACCT_OUT=$LIVE run pilot; [ "$rc" != 0 ] && has "fenced job is live" && [ ! -e $H/R/claims/pilot ]; ok $? "pilot: a live cov2d job STOPs before the claim"
run pilot; [ "$rc" = 0 ]; ok $? "pilot: runs once the fence clears"
staged; SBATCH_OUT='Submitted batch job 1' run pilot; [ "$rc" != 0 ] && has "sbatch printed"; ok $? "pilot: an unparsable sbatch STOPs"
staged; SBATCH_FAIL=1 run pilot; [ "$rc" != 0 ] && has "STOP: sbatch"; ok $? "pilot: a failed sbatch STOPs"
run pilot; [ "$rc" != 0 ] && has "already claimed"; ok $? "pilot after a failed sbatch: the claim refuses a resubmit"
staged; SBATCH_BLOCK=$H/R/logs/pilot.jobid run pilot; [ "$rc" != 0 ] && has "was submitted but its id could not be recorded"; ok $? "pilot: an unrecordable job id STOPs and names the job"
# --- post-pilot
piloted; SACCT_J_FAIL=1 run post-pilot; [ "$rc" != 0 ] && has "STOP: sacct failed"; ok $? "post-pilot: a failed sacct STOPs, printed"
piloted; SACCT_J='' run post-pilot; [ "$rc" != 0 ] && has "sacct returned nothing"; ok $? "post-pilot: empty accounting STOPs"
piloted; POST_RC=6 run post-pilot; [ "$rc" = 6 ] && has "did not PROCEED" && [ ! -e $H/R/pilot-post/PROCEED ]; ok $? "post-pilot: a STOP decision exits 6, no PROCEED"
grep -q -- '--jobid 12345 .*--rows .*oofvc_rows.npz' $H/python.args; ok $? "post-pilot: passes --jobid and --rows"
[ "$(cat $H/env.python)" = "$(printf 'MKL_NUM_THREADS=1\nNUMEXPR_NUM_THREADS=1\nOMP_NUM_THREADS=1\nOPENBLAS_NUM_THREADS=1')" ]
ok $? "post-pilot: python runs with one thread"
piloted; POST_DECISION_DIR=1 run post-pilot; [ "$rc" != 0 ] && has "printing the decision (the C-SUPPORT table) failed"; ok $? "post-pilot: an unprintable decision STOPs before PROCEED is reported"
piloted; run post-pilot; [ "$rc" = 0 ] && [ -e $H/R/pilot-post/PROCEED ] && has '"verdict": "stub"'; ok $? "post-pilot: PROCEED, the decision printed"
run post-pilot; [ "$rc" != 0 ] && has "has run"; ok $? "post-pilot again: STOP"
piloted; CONDA_RC=1 run post-pilot; [ "$rc" != 0 ] && has "conda activate"; ok $? "post-pilot: a failed activation STOPs"
# --- replicas
for bad in 0 abc 700 ''; do
  proceeded; echo "$bad" > $H/R/pilot-post/time_limit_minutes; run replicas
  [ "$rc" != 0 ] && [ ! -e $H/R/logs/replicas.jobid ] && [ ! -e $H/R/claims/replicas ]; ok $? "replicas: time limit '$bad' STOPs"
done
proceeded; run replicas
[ "$rc" = 0 ] && grep -q -- '-N 5 -t 145 .*replicas.sbatch' $H/sbatch.args && [ "$(cat $H/R/logs/replicas.jobid)" = 12345 ]
ok $? "replicas: submitted with -N 5 -t 145"
grep -q -- '--recheck .*decision.json' $H/python.args && [ -s $H/R/replicas-check/sacct.txt ]; ok $? "replicas: the recheck ran on fresh accounting"
run replicas; [ "$rc" != 0 ] && has "have been submitted"; ok $? "replicas again: STOP"
proceeded; RECHECK=DIFFERS RECHECK_RC=6 run replicas; [ "$rc" = 6 ] && has "does not give the same" && [ ! -e $H/sbatch.args ]; ok $? "replicas: a DIFFERS recheck exits 6, no sbatch"
proceeded; RECHECK_L=144 run replicas; [ "$rc" != 0 ] && has "recheck's L is not 145" && [ ! -e $H/sbatch.args ]; ok $? "replicas: a recheck at another L STOPs"
proceeded; SACCT_J_FAIL=1 run replicas; [ "$rc" != 0 ] && has "STOP: sacct failed" && [ ! -e $H/sbatch.args ]; ok $? "replicas: a failed sacct STOPs"
proceeded; SACCT_OUT=$LIVE run replicas; [ "$rc" != 0 ] && has "fenced job is live" && [ ! -e $H/R/claims/replicas ]; ok $? "replicas: a live cov2d job STOPs before the claim"
proceeded; rm $H/R/pilot-post/PROCEED; run replicas; [ "$rc" != 0 ] && has "no PROCEED"; ok $? "replicas: no PROCEED STOPs"
proceeded; SQUEUE_OUT='ptmc_pilot\n' run replicas; [ "$rc" != 0 ] && has "a ptmc job is queued" && [ ! -e $H/sbatch.args ]; ok $? "replicas: a queued ptmc job STOPs"
# --- post
P1='12345|ptmc_pilot|COMPLETED|0:0|1500|2|s|e\n12345.batch|batch|COMPLETED|0:0|1500|1|s|e\n'
P2='12346|ptmc_reps|COMPLETED|0:0|8000|5|s|e\n12346.0|p_R_b2|COMPLETED|0:0|700|1|s|e\n'
mkpost() { proceeded; run replicas; echo 12346 > $H/R/logs/replicas.jobid; }
mkpost; SACCT_J_12345=$P1 SACCT_J_12346='12346.0|p_R_b2|COMPLETED|0:0|700|1|s|e\n' run post
[ "$rc" != 0 ] && has "sacct has no allocation line for the replicas job 12346" && [ ! -e $H/R/post.tar.gz ]; ok $? "post: accounting without the job's own line STOPs"
mkpost; SACCT_J_12345=$P1 SACCT_J_12346="$P2$P1" run post
[ "$rc" != 0 ] && has "has a row of another job" && [ ! -e $H/R/post.tar.gz ]; ok $? "post: a row of another job STOPs"
mkpost; SACCT_J_12345=$P1 SACCT_J_12346='' run post; [ "$rc" != 0 ] && has "sacct returned nothing for the replicas job"; ok $? "post: empty accounting STOPs"
mkpost; SACCT_J_FAIL=1 run post; [ "$rc" != 0 ] && has "STOP: sacct pilot"; ok $? "post: a failed sacct STOPs"
proceeded; run post; [ "$rc" != 0 ] && has "a PTMC job id is missing" && [ ! -e $H/R/post ]; ok $? "post: no replicas job id STOPs"
mkpost; SQUEUE_OUT='ptmc_reps\n' run post; [ "$rc" != 0 ] && [ ! -e $H/R/post ] && [ ! -e $H/R/claims/post ]; ok $? "post: a running ptmc job STOPs before the claim"
mkpost; D4_RC=5 SACCT_J_12345=$P1 SACCT_J_12346=$P2 run post; [ "$rc" != 0 ] && has "the D4 staging" && [ ! -e $H/R/post.tar.gz ]; ok $? "post: a failed D4 staging STOPs, no tar"
mkpost; SACCT_J_12345=$P1 SACCT_J_12346='12346|ptmc_reps|COMPLETED|0:0|8x00|5|s|e\n' run post
[ "$rc" != 0 ] && has "STOP: charge" && [ ! -e $H/R/post.tar.gz ]; ok $? "post: a malformed elapsed time STOPs the charge"
mkpost; SACCT_J_12345=$P1 SACCT_J_12346=$P2 run post
[ "$rc" = 0 ] && [ -s $H/R/post.tar.gz ] && [ -s $H/R/d4.tar.gz ] && grep -qx 'charged_node_h=11.9444' $H/R/post/charge.txt
ok $? "post: both tars written, the charge from both allocation lines"
(cd $H/R && /usr/bin/sha256sum -c --quiet tars.sha256) && [ "$(wc -l < $H/R/tars.sha256)" = 2 ]; ok $? "post: tars.sha256 holds both tars' digests"
tar -tzf $H/R/post.tar.gz | grep -q '^claims/' && tar -tzf $H/R/post.tar.gz | grep -q '^replicas-check/'; ok $? "post: the tar carries the claims and the recheck"
run post; [ "$rc" != 0 ] && has "post has run"; ok $? "post again: STOP"
echo "pass $pass fail $fail"
[ "$fail" = 0 ]
