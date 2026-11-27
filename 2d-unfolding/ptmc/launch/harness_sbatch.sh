#!/bin/bash
# Harness for pilot.sbatch and replicas.sbatch (a harmless-worker test, in debian:bookworm-slim). Copies with R, PY
# and the conda hook substituted run against an srun stub that records each step's --job-name and returns
# SRUN_FAIL_FOR's rc. It checks every unit runs exactly once, that a failure propagates, and that each script refuses
# its missing precondition.
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
printf '#!/bin/bash\n"$@"\n' > $H/bin/time; chmod +x $H/bin/*
mkdir -p $H/global/conda/bin; printf '#!/bin/bash\necho "conda() { return 0; }"\n' > $H/global/conda/bin/conda; chmod +x $H/global/conda/bin/conda
export PATH=$H/bin:$PATH HOME=$H
mk() { sed -e "s#/pscratch/sd/j/josephrb/ptmc-20261128#$H/R#g" -e "s#/usr/bin/time#$H/bin/time#" \
          -e "s#/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda#$H/global/conda/bin/conda#" \
          /h/$1 > $H/$1; }
fresh() { rm -rf $H/R $H/steps; mkdir -p $H/R/stage $H/R/logs; echo abc > $H/R/stage/rows.sha256; }
# pilot
mk pilot.sbatch; fresh; out=$(bash $H/pilot.sbatch 2>&1); rc=$?
ok $([ "$rc" = 2 ] && echo 0 || echo 1) "pilot: no ready refuses (rc 2)"
fresh; touch $H/R/stage/ready; out=$(bash $H/pilot.sbatch 2>&1); rc=$?
[ "$rc" = 0 ] && [ "$(sort $H/steps | tr '\n' ' ')" = "p_R_b1 p_R_c p_off_b1 p_off_b2 p_off_b3 p_off_b4 p_off_c p_off_b5 " ] || \
  [ "$(sort $H/steps | tr '\n' ' ')" = "$(printf '%s\n' p_off_c p_R_c p_off_b1 p_R_b1 p_off_b2 p_off_b3 p_off_b4 p_off_b5 | sort | tr '\n' ' ')" ]
ok $? "pilot: the 8 units, once each"
fresh; touch $H/R/stage/ready; out=$(SRUN_FAIL_FOR=p_off_b3 bash $H/pilot.sbatch 2>&1); rc=$?
[ "$rc" = 6 ]; ok $? "pilot: a failed unit exits 6"
fresh; touch $H/R/stage/ready; mkdir $H/R/units; out=$(bash $H/pilot.sbatch 2>&1); rc=$?
[ "$rc" = 2 ]; ok $? "pilot: an existing units dir refuses"
# replicas
mk replicas.sbatch; fresh; mkdir -p $H/R/units $H/R/pilot-post; out=$(bash $H/replicas.sbatch 2>&1); rc=$?
[ "$rc" = 2 ]; ok $? "replicas: no PROCEED refuses (rc 2)"
fresh; mkdir -p $H/R/units $H/R/pilot-post; echo PROCEED > $H/R/pilot-post/PROCEED
out=$(bash $H/replicas.sbatch 2>&1); rc=$?
[ "$rc" = 0 ] && [ "$(sort -u $H/steps | wc -l)" = 199 ] && [ "$(wc -l < $H/steps)" = 199 ] && \
  [ "$(sort -t b -k2 -n $H/steps | head -1)" = p_R_b2 ] && ! grep -qx 'p_R_b1' $H/steps && grep -qx p_R_b200 $H/steps
ok $? "replicas: b = 2..200, 199 steps, each once"
fresh; mkdir -p $H/R/units $H/R/pilot-post; echo PROCEED > $H/R/pilot-post/PROCEED
out=$(SRUN_FAIL_FOR=p_R_b57 bash $H/replicas.sbatch 2>&1); rc=$?
[ "$rc" = 6 ] && [ "$(wc -l < $H/steps)" = 199 ] && grep -q 'b57:1' $H/R/logs/lane_15.rcs; ok $? "replicas: a failed unit exits 6, its lane continues, rc recorded"
echo "pass $pass fail $fail"; [ "$fail" = 0 ]
