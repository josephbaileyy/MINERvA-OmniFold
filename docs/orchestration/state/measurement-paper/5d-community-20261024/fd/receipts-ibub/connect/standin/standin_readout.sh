#!/bin/bash
# Stand-in of ibub_readout_connect.sh (connect O) in Debian, as standin.sh is for connect R. Stubs: sacct (the fence
# rows and the job's row from the variant), git clone's URL (a depth-1 bare repo of the commit, which is also the
# stand-in's JOB_M), the MAT pin check (PY310), and the shared checkout's setup_salloc_env.sh, which puts a stub
# `python` first on PATH: it answers the MAT preflight and stands in for ibub_readout.py (it writes the tune's two
# products and prints its verdict line). The real readout needs ROOT and MAT and is tested by test_ibub_readout.py;
# this tests the connect around it. The job's records are fake bytes at the real paths of $N.
# Variant ($1): ok | done_absent | tune_invalid | job_preempted | job_norow | root_exists | readout_exists |
#               cov2d_running | ibub_running | window | not_regular | readout_refused
V=${1:?variant}
git config --global --add safe.directory '*'
U=/pscratch/sd/j/josephrb; N=$U/ibub-20261124; JOB=61924744
mkdir -p /stub /stubpy /root/.conda/envs/root_6_28/bin /global/homes/j/josephrb/.conda/envs/omnifold_py310/bin
ln -sf /usr/local/bin/python3 /root/.conda/envs/root_6_28/bin/python3
cat > /stub/git <<'G'
#!/bin/bash
if [ "$1" = clone ]; then dest=${@: -1}; exec /usr/bin/git clone -q /hostgit "$dest"; fi
exec /usr/bin/git "$@"
G
JS=COMPLETED; C2=COMPLETED; IB=COMPLETED
[ "$V" = job_preempted ] && JS=PREEMPTED
[ "$V" = cov2d_running ] && C2=RUNNING
[ "$V" = ibub_running ] && IB=PENDING
JOBROW="$JOB|ibub_run|$JS|0:0"; [ "$V" = job_norow ] && JOBROW=""
cat > /stub/sacct <<S2
#!/bin/bash
for a in "\$@"; do [ "\$a" = -j ] && { echo "JobID|JobName|State|ExitCode"; [ -n "$JOBROW" ] && echo "$JOBROW"; exit 0; }; done
echo "$JOB|ibub_run|$JS"
echo "61000001|cov2d_g2r|$C2"
echo "61800000|rpd_flux2|COMPLETED"
echo "61850000|ibub_run|$IB"
echo "61870000|unrelated_lane|RUNNING"
S2
printf '#!/bin/bash\necho "MAT pin check (stand-in)"\n' > /global/homes/j/josephrb/.conda/envs/omnifold_py310/bin/python
mkdir -p $U/MINERvA-OmniFold
echo 'export PATH=/stubpy:$PATH' > $U/MINERvA-OmniFold/setup_salloc_env.sh
TRC=0; [ "$V" = tune_invalid ] && TRC=3; [ "$V" = readout_refused ] && TRC=4
cat > /stubpy/python <<P
#!/bin/bash
if [ "\$1" = - ]; then cat > /dev/null; echo "MAT preflight: MnvH1D PlotUtils::MnvH1D 10 bins (stand-in)"; exit 0; fi
if [ "\$1" = -c ]; then exec python3 "\$@"; fi
T=""; O=""; prev=""; for a in "\$@"; do [ "\$prev" = --truth ] && T=\$a; [ "\$prev" = --out ] && O=\$a; prev=\$a; done
echo "stand-in readout argv: \$*"
rc=$TRC; [ "\$T" = G18 ] && rc=0
if [ \$rc = 4 ]; then echo "IBUB-READOUT \$T REFUSED: stand-in"; exit 4; fi
mkdir "\$O" && echo "{\"verdict\": \"stand-in \$T\"}" > "\$O/ibub_\$T.json" && echo npz > "\$O/ibub_\$T"_errors.npz
v=PASS; [ \$rc = 3 ] && v=INVALID
echo "IBUB-READOUT \$T \$v reading=None controls_failed=0 stops=0"; exit \$rc
P
printf '#!/bin/bash\n[ "$1" = -v ] && shift\nexec "$@"\n' > /usr/bin/time; chmod +x /usr/bin/time   # the connect calls it by path; slim has none
printf '#!/bin/bash\n[ "$1" = -c ] && shift 2\nexec "$@"\n' > /stub/taskset   # a container has fewer CPUs than 8-11
chmod +x /stub/* /stubpy/python /global/homes/j/josephrb/.conda/envs/omnifold_py310/bin/python
export PATH=/stub:$PATH HOME=/root
# the job's records in $N (fake bytes at the real paths)
mkdir -p $N/units $N/logs $N/slurm $N/stage
echo '{"verdict": "PASS"}' > $N/units/refcheck.json; echo '{"verdict": "PASS"}' > $N/stage/stage.json
echo "JobId=$JOB JobName=ibub_run QOS=regular_1" > $N/logs/scontrol-batch-$JOB.txt; echo refcheck > $N/logs/refcheck.log
echo '{"verdict": "PASS"}' > $N/logs/complete.json; echo "[ibub] allocation: ..." > $N/slurm/ibub_run-$JOB.out; : > $N/slurm/ibub_run-$JOB.err
[ "$V" = done_absent ] || echo '{"job": "61924744", "stage": "toys", "rc": 0}' > $N/IBUB-DONE
[ "$V" = not_regular ] && { mv $N/units/refcheck.json $N/units/refcheck.real; ln -s refcheck.real $N/units/refcheck.json; }
[ "$V" = root_exists ] && mkdir -p /dev/shm/ibub-connect
[ "$V" = readout_exists ] && mkdir -p $N/readout
cp /connect/connect.sh /dev/shm/ibubc.1.sh
WEND=$(( $(date +%s) + 900 )); [ "$V" = window ] && WEND=$(( $(date +%s) - 10 ))
bash /dev/shm/ibubc.1.sh /dev/shm/ibubc.1.sh $WEND > /tmp/session.out 2>&1
rc=$?
echo "== variant $V: script rc=$rc; session: $(tr '\n' ' ' < /tmp/session.out | cut -c1-300)"
echo "== self copy left: $(ls /dev/shm/ibubc.1.sh 2>&1 | head -1); root left: $(ls -d /dev/shm/ibub-connect 2>&1)"
echo "== the connect log"; cat $N/logs/connect-readout.log 2>&1 | sed 's/^/  /'
echo "== done: $(cat $N/logs/connect-readout.done 2>&1)"
echo "== readout published: $(cd $N/readout 2>/dev/null && find . -type f | sort | tr '\n' ' ')"
echo "== records tar: $(ls -l $N/fetch-readout.tar 2>&1 | awk '{print $5}'); listed: $(tar -tf $N/fetch-readout.tar 2>/dev/null | grep -c .)"
echo "== job records unchanged: $(cat $N/units/refcheck.json 2>&1) $(ls $N/units | tr '\n' ' ')"
exit 0
