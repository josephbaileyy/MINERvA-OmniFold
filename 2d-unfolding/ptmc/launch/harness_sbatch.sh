#!/bin/bash
# Harness for pilot.sbatch and replicas.sbatch (a harmless-worker test, in debian:bookworm-slim). Copies with R, PY
# and the conda hook substituted run against stubs: srun records each step's --job-name and returns SRUN_FAIL_FOR's rc;
# squeue prints SQUEUE_L (the job's time limit) or fails; the conda hook prints a no-op conda or fails on CONDA_FAIL.
# One case per gate: every unit runs exactly once and is recorded, a failure propagates, and each script refuses every
# missing precondition (the node count, the stage, the rows pin, the conda hook, the record directory, the time limit).
set -u
H=/tmp/hs; rm -rf $H; mkdir -p $H/bin
pass=0; fail=0
ok() { if [ "$1" = 0 ]; then pass=$((pass+1)); echo "ok   $2"; else fail=$((fail+1)); echo "FAIL $2"; fi; }
cat > $H/bin/srun <<'S'
#!/bin/bash
for a in "$@"; do case "$a" in --job-name=*) n=${a#--job-name=};; esac; done
echo "$n" >> /tmp/hs/steps
[ "${SRUN_FAIL_FOR:-}" = "$n" ] && exit 1
exit 0
S
cat > $H/bin/squeue <<'S'
#!/bin/bash
[ "${SQUEUE_FAIL:-}" = 1 ] && exit 1
echo "${SQUEUE_L:-02:24:00}"
S
printf '#!/bin/bash\n"$@"\n' > $H/bin/time; chmod +x $H/bin/*
mkdir -p $H/global/conda/bin
printf '#!/bin/bash\n[ "${CONDA_FAIL:-}" = 1 ] && exit 1\necho "conda() { return 0; }"\n' > $H/global/conda/bin/conda
chmod +x $H/global/conda/bin/conda
export PATH=$H/bin:$PATH HOME=$H SLURM_JOB_ID=4242 SLURM_JOB_NODELIST=nid[1-5]
PIN=cbf34bd8cad0f4978dc1aea22713eb5057bf521118dc7ce8d10b93b30defcb03
mk() { sed -e "s#/pscratch/sd/j/josephrb/ptmc-20261128#$H/R#g" -e "s#/usr/bin/time#$H/bin/time#" \
          -e "s#/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda#$H/global/conda/bin/conda#" \
          /h/$1 > $H/$1; }
fresh() { rm -rf $H/R $H/steps; mkdir -p $H/R/stage $H/R/logs; echo $PIN > $H/R/stage/rows.sha256; }
ready() { fresh; touch $H/R/stage/ready; }
proceed() { fresh; mkdir -p $H/R/units $H/R/pilot-post; echo PROCEED > $H/R/pilot-post/PROCEED
            echo 144 > $H/R/pilot-post/time_limit_minutes; }
P() { out=$(SLURM_JOB_NUM_NODES=${NN:-2} bash $H/pilot.sbatch 2>&1); rc=$?; }
Q() { out=$(SLURM_JOB_NUM_NODES=${NN:-5} bash $H/replicas.sbatch 2>&1); rc=$?; }
refused() { [ "$rc" = 2 ] && printf '%s' "$out" | grep -q "REFUSED: $1" && [ ! -e $H/steps ]; }
# pilot
mk pilot.sbatch
ready; NN=3 P; refused "the allocation has '3' nodes"; ok $? "pilot: 3 nodes refuses"
fresh; P; refused "the stage is not ready"; ok $? "pilot: no ready refuses"
ready; mkdir $H/R/units; P; refused "units exists"; ok $? "pilot: an existing units dir refuses"
ready; echo abc > $H/R/stage/rows.sha256; P; refused "rows.sha256 is not the pinned rows"; ok $? "pilot: a wrong rows pin refuses"
ready; rm $H/R/stage/rows.sha256; P; refused "rows.sha256 unreadable"; ok $? "pilot: no rows.sha256 refuses"
ready; out=$(CONDA_FAIL=1 SLURM_JOB_NUM_NODES=2 bash $H/pilot.sbatch 2>&1); rc=$?
refused "the conda hook failed"; ok $? "pilot: a failed conda hook refuses"
ready; mkdir -p $H/R/logs/pilot-4242; P; refused "mkdir"; ok $? "pilot: an existing record dir refuses"
ready; P
want=$(printf '%s\n' p_off_c p_R_c p_off_b1 p_R_b1 p_off_b2 p_off_b3 p_off_b4 p_off_b5 | sort | tr '\n' ' ')
[ "$rc" = 0 ] && [ "$(sort $H/steps | tr '\n' ' ')" = "$want" ] && [ "$(awk '$2=="0"' $H/R/logs/pilot-4242/outcomes | wc -l)" = 8 ]
ok $? "pilot: the 8 units, once each, 8 outcomes recorded"
ready; out=$(SRUN_FAIL_FOR=p_off_b3 SLURM_JOB_NUM_NODES=2 bash $H/pilot.sbatch 2>&1); rc=$?
[ "$rc" = 6 ] && grep -qx 'p_off_b3 1' $H/R/logs/pilot-4242/outcomes && [ "$(wc -l < $H/R/logs/pilot-4242/outcomes)" = 8 ]
ok $? "pilot: a failed unit exits 6, every outcome recorded"
# replicas
mk replicas.sbatch
proceed; NN=4 Q; refused "the allocation has '4' nodes"; ok $? "replicas: 4 nodes refuses"
fresh; mkdir -p $H/R/units $H/R/pilot-post; Q; refused "no PROCEED"; ok $? "replicas: no PROCEED refuses"
proceed; rm $H/R/pilot-post/time_limit_minutes; Q; refused "no authorized time limit"; ok $? "replicas: no L refuses"
proceed; echo 1x > $H/R/pilot-post/time_limit_minutes; Q; refused "the authorized time limit"; ok $? "replicas: a malformed L refuses"
proceed; out=$(SQUEUE_FAIL=1 SLURM_JOB_NUM_NODES=5 bash $H/replicas.sbatch 2>&1); rc=$?
refused "squeue failed"; ok $? "replicas: a failed squeue refuses"
proceed; out=$(SQUEUE_L=UNLIMITED SLURM_JOB_NUM_NODES=5 bash $H/replicas.sbatch 2>&1); rc=$?
refused "the job's time limit 'UNLIMITED' does not parse"; ok $? "replicas: an UNLIMITED time limit refuses"
proceed; out=$(SQUEUE_L='1*1:00' SLURM_JOB_NUM_NODES=5 bash $H/replicas.sbatch 2>&1); rc=$?
refused "the job's time limit '1\*1:00' does not parse"; ok $? "replicas: a limit that bash arithmetic would evaluate refuses"
proceed; out=$(SQUEUE_L=02:24:01 SLURM_JOB_NUM_NODES=5 bash $H/replicas.sbatch 2>&1); rc=$?
refused "the job's time limit is 145 minutes"; ok $? "replicas: a limit one second over L refuses"
proceed; out=$(SQUEUE_L=1-00:00:00 SLURM_JOB_NUM_NODES=5 bash $H/replicas.sbatch 2>&1); rc=$?
refused "the job's time limit is 1440 minutes"; ok $? "replicas: a day-form limit over L refuses"
proceed; echo abc > $H/R/stage/rows.sha256; Q; refused "rows.sha256 is not the pinned rows"; ok $? "replicas: a wrong rows pin refuses"
proceed; out=$(CONDA_FAIL=1 SLURM_JOB_NUM_NODES=5 bash $H/replicas.sbatch 2>&1); rc=$?
refused "the conda hook failed"; ok $? "replicas: a failed conda hook refuses"
proceed; mkdir -p $H/R/logs/replicas-4242; Q; refused "mkdir"; ok $? "replicas: an existing record dir refuses"
proceed; out=$(SQUEUE_L=2:00:00 SLURM_JOB_NUM_NODES=5 bash $H/replicas.sbatch 2>&1); rc=$?
[ "$rc" = 0 ] && [ "$(sort -u $H/steps | wc -l)" = 199 ] && [ "$(wc -l < $H/steps)" = 199 ] && \
  ! grep -qx 'p_R_b1' $H/steps && grep -qx p_R_b2 $H/steps && grep -qx p_R_b200 $H/steps && \
  [ "$(cat $H/R/logs/replicas-4242/lane_* | awk '$2=="0"' | wc -l)" = 199 ] && grep -qx 'p_R_b22 0' $H/R/logs/replicas-4242/lane_0
ok $? "replicas: b = 2..200, 199 steps, each once, 199 outcomes, lane 0 takes b22"
proceed; out=$(SRUN_FAIL_FOR=p_R_b57 SLURM_JOB_NUM_NODES=5 bash $H/replicas.sbatch 2>&1); rc=$?
[ "$rc" = 6 ] && [ "$(wc -l < $H/steps)" = 199 ] && grep -qx 'p_R_b57 1' $H/R/logs/replicas-4242/lane_15 && \
  grep -qx 'p_R_b77 0' $H/R/logs/replicas-4242/lane_15
ok $? "replicas: a failed unit exits 6, its lane continues, its outcome recorded"
echo "pass $pass fail $fail"; [ "$fail" = 0 ]
