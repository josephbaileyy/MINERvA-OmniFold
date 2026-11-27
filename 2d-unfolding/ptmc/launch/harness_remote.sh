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
s() { sha256sum < "$1" | cut -d' ' -f1; }
# stubs
cat > $H/bin/sacct <<'S'
#!/bin/bash
[ -n "${SACCT_FAIL:-}" ] && exit 1
printf '%b' "${SACCT_OUT:-}"
S
cat > $H/bin/squeue <<'S'
#!/bin/bash
[ -n "${SQUEUE_FAIL:-}" ] && exit 1
printf '%b' "${SQUEUE_OUT:-}"
S
cat > $H/bin/sbatch <<'S'
#!/bin/bash
echo "$*" >> /tmp/hz/sbatch.args
printf '%s\n' "${SBATCH_OUT:-12345}"
S
cat > $H/bin/id <<'S'
#!/bin/bash
echo "${ID_USER:-josephrb}"
S
cat > $H/bin/git <<'S'
#!/bin/bash
# clone URL DEST | -C DIR rev-parse HEAD | -C DIR status ... | -C DIR -c ... checkout -q REV
if [ "$1" = clone ]; then
  d=${@: -1}; mkdir -p "$d/2d-unfolding/ptmc/launch"
  cat > "$d/2d-unfolding/ptmc/make_tree.sh" <<'M'
#!/bin/bash
[ -n "${MAKE_TREE_FAIL:-}" ] && { echo "REFUSED: stub"; exit 3; }
d=$1; mkdir -p $d/2d-unfolding/re2 $d/2d-unfolding/ref_c2c1 $d/unbinned_unfolding/python $d/2d-unfolding/uq $d/2d-unfolding/oofvc
for f in 2d-unfolding/re2/re2_driver.py 2d-unfolding/ref_c2c1/config.json 2d-unfolding/ref_c2c1/ref_c2c1.py \
  2d-unfolding/ref_c2c1/ref_c2c1_read.py unbinned_unfolding/python/omnifold.py 2d-unfolding/compare_to_paper_fullcov.py \
  2d-unfolding/uq/reported_cells.py 2d-unfolding/oofvc/oofvc_lib.py; do echo "$f" > $d/$f; done
echo "tree $d"
M
  : > "$d/2d-unfolding/ptmc/launch/pilot.sbatch"; : > "$d/2d-unfolding/ptmc/launch/replicas.sbatch"
  : > "$d/2d-unfolding/ptmc/launch/ptmc_pilot_post.py"; : > "$d/2d-unfolding/ptmc/launch/ptmc_stage_d4.py"
  exit 0
fi
case "$*" in
  *rev-parse*) echo "${GIT_HEAD:-abc123}" ;;
  *status*) printf '%s' "${GIT_STATUS:-}" ;;
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
case "$*" in
  *ptmc_pilot_post.py*)
    out=${@: -1}
    [ "${POST_RC:-0}" = 0 ] && { echo PROCEED > $out/PROCEED; echo "${POST_L:-145}" > $out/time_limit_minutes; }
    echo '{"verdict": "stub"}' > $out/decision.json; exit ${POST_RC:-0} ;;
  *ptmc_stage_d4.py*)
    out=${@: -1}; [ "${D4_RC:-0}" = 0 ] || exit ${D4_RC}; mkdir -p $out; echo '{}' > $out/manifest.json; exit 0 ;;
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
      -e "s#^PY=.*#PY=$H/bin/python3#" -e "s#^CONDA_HOOK=.*#CONDA_HOOK=$H/bin/conda#" /h/ptmc_remote.sh > $H/r.sh
}
run() { mk; out=$(bash $H/r.sh $H/r.sh "$@" 2>&1); rc=$?; }
has() { printf '%s\n' "$out" | grep -q -- "$1"; }
LIVE='1|cov2d-AR23|RUNNING\n'
# --- setup
run setup; ok $? "setup: runs"; [ "$rc" = 0 ] && [ -e $H/R/stage/ready ]; ok $? "setup: rc 0 and ready"
cmp -s $H/R/stage/runEventLoopOmniFold_MEFHC.root $H/src/cv; ok $? "setup: the CV copy is byte-identical"
has "pre  $H/src/cv|atime="; ok $? "setup: the source's atime is printed before and after"
run setup; [ "$rc" != 0 ] && has "STOP: $H/R exists"; ok $? "setup again: STOP, R exists"
rm -rf $H/R; SACCT_OUT=$LIVE run setup; [ "$rc" != 0 ] && has "a fenced job is live" && [ ! -e $H/R ]; ok $? "setup: a live cov2d job STOPs before R is made"
rm -rf $H/R; SACCT_FAIL=1 run setup; [ "$rc" != 0 ] && has "sacct failed" && [ ! -e $H/R ]; ok $? "setup: a failed sacct STOPs"
rm -rf $H/R; SQUEUE_OUT='ptmc_pilot\n' run setup; [ "$rc" != 0 ] && has "a ptmc job is queued" && [ ! -e $H/R ]; ok $? "setup: a queued ptmc job STOPs"
rm -rf $H/R; SQUEUE_FAIL=1 run setup; [ "$rc" != 0 ] && has "squeue failed"; ok $? "setup: a failed squeue STOPs"
rm -rf $H/R; CVPIN=0000 run setup; [ "$rc" != 0 ] && has "is not 0000" && [ ! -e $H/R/stage/ready ]; ok $? "setup: a CV pin mismatch STOPs, no ready"
rm -rf $H/R; mv $H/src/cv $H/src/cv.real; ln -s $H/src/cv.real $H/src/cv; run setup
[ "$rc" != 0 ] && has "absent or a symlink" && [ ! -e $H/R/stage/ready ]; ok $? "setup: a symlinked source STOPs"
rm $H/src/cv; mv $H/src/cv.real $H/src/cv
rm -rf $H/R; LIBPIN=0000 run setup; [ "$rc" != 0 ] && has "libRooUnfold.so differs" && [ ! -e $H/R/stage/ready ]; ok $? "setup: a library pin mismatch STOPs, no ready"
rm -rf $H/R; MAKE_TREE_FAIL=1 run setup; [ "$rc" != 0 ] && has "STOP: make_tree" && [ ! -e $H/R/stage/ready ]; ok $? "setup: make_tree's refusal STOPs"
rm -rf $H/R; GIT_HEAD=def456 run setup; [ "$rc" != 0 ] && has "not at abc123"; ok $? "setup: a clone at the wrong commit STOPs"
rm -rf $H/R; GIT_STATUS=' M x' run setup; [ "$rc" != 0 ] && has "not clean"; ok $? "setup: a dirty clone STOPs"
rm -rf $H/R; ID_USER=other run setup; [ "$rc" != 0 ] && has "STOP: user" && [ ! -e $H/R ]; ok $? "wrong user: STOP"
run bogus; [ "$rc" != 0 ] && has "STOP: mode"; ok $? "unknown mode: STOP"
mk; sed -i 's#^TOOLC=.*#TOOLC=__TOOL_COMMIT__#' $H/r.sh; out=$(bash $H/r.sh $H/r.sh setup 2>&1); rc=$?
[ "$rc" != 0 ] && has "not filled in"; ok $? "an unfilled tool commit: STOP"
# --- pilot
rm -rf $H/R; run setup; rm -f $H/sbatch.args
run pilot; [ "$rc" = 0 ] && [ "$(cat $H/R/logs/pilot.jobid)" = 12345 ]; ok $? "pilot: submitted, jobid recorded"
grep -q 'pilot.sbatch' $H/sbatch.args; ok $? "pilot: sbatch got pilot.sbatch"
run pilot; [ "$rc" != 0 ] && has "has been submitted"; ok $? "pilot again: STOP"
rm $H/R/logs/pilot.jobid; echo tampered >> $H/R/deploy/2d-unfolding/re2/re2_driver.py; run pilot
[ "$rc" != 0 ] && has "deploy tree differs" && [ ! -e $H/R/logs/pilot.jobid ]; ok $? "pilot: a changed deploy file STOPs"
rm -rf $H/R; run setup; SBATCH_OUT='Submitted batch job 1' run pilot; [ "$rc" != 0 ] && has "sbatch printed"; ok $? "pilot: an unparsable sbatch STOPs"
rm -rf $H/R; run setup; rm $H/R/stage/ready; run pilot; [ "$rc" != 0 ] && has "not ready"; ok $? "pilot: no ready STOPs"
rm -rf $H/R; run setup; SACCT_OUT=$LIVE run pilot; [ "$rc" != 0 ] && has "fenced job is live" && [ ! -e $H/R/logs/pilot.jobid ]; ok $? "pilot: a live cov2d job STOPs"
# --- post-pilot
rm -rf $H/R; run setup; run pilot; mkdir -p $H/R/units
POST_RC=6 run post-pilot; [ "$rc" = 6 ] && has "did not PROCEED" && [ ! -e $H/R/pilot-post/PROCEED ]; ok $? "post-pilot: a STOP decision exits 6, no PROCEED"
rm -rf $H/R/pilot-post; run post-pilot; [ "$rc" = 0 ] && [ -e $H/R/pilot-post/PROCEED ]; ok $? "post-pilot: PROCEED"
run post-pilot; [ "$rc" != 0 ] && has "has run"; ok $? "post-pilot again: STOP"
rm -rf $H/R/pilot-post; CONDA_RC=1 run post-pilot; [ "$rc" != 0 ] && has "conda activate"; ok $? "post-pilot: a failed activation STOPs"
# --- replicas
rm -rf $H/R/pilot-post; run post-pilot; rm -f $H/sbatch.args
for bad in 0 abc 700 ''; do
  echo "$bad" > $H/R/pilot-post/time_limit_minutes; run replicas
  [ "$rc" != 0 ] && [ ! -e $H/R/logs/replicas.jobid ]; ok $? "replicas: time limit '$bad' STOPs"
done
echo 145 > $H/R/pilot-post/time_limit_minutes; run replicas
[ "$rc" = 0 ] && grep -q -- '-t 145 .*replicas.sbatch' $H/sbatch.args; ok $? "replicas: submitted with -t 145"
run replicas; [ "$rc" != 0 ] && has "have been submitted"; ok $? "replicas again: STOP"
rm $H/R/logs/replicas.jobid; rm $H/R/pilot-post/PROCEED; run replicas; [ "$rc" != 0 ] && has "no PROCEED"; ok $? "replicas: no PROCEED STOPs"
# --- post
echo PROCEED > $H/R/pilot-post/PROCEED
SQUEUE_OUT='ptmc_reps\n' run post; [ "$rc" != 0 ] && [ ! -e $H/R/post ]; ok $? "post: a running ptmc job STOPs"
D4_RC=5 run post; [ "$rc" != 0 ] && has "the D4 staging" && [ ! -e $H/R/post.tar.gz ]; ok $? "post: a failed D4 staging STOPs, no tar"
rm -rf $H/R/post $H/R/d4; run post; [ "$rc" = 0 ] && [ -s $H/R/post.tar.gz ] && [ -s $H/R/d4.tar.gz ]; ok $? "post: both tars written"
run post; [ "$rc" != 0 ] && has "post has run"; ok $? "post again: STOP"
echo "pass $pass fail $fail"
[ "$fail" = 0 ]
