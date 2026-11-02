# 1B investigation, I2 bulk submission (FD-1B-INV-BINDING ruling 1: only after walls PASS)
P=/pscratch/sd/j/josephrb; V=$P/fd-1b-inv-20261101; DD=$V/deploy; M=b1c615f12fca5f8597d34750b2c074f1fd7b2cdd
BANK=$P/MINERvA-OmniFold/nd-unfolding/bank_sweep_5d_bkgaware
PY="env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I"
echo "host=$(hostname) start=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
stop() { echo "STOP: $*"; exit 2; }
[ -e $V/logs/submit-i2.out ] && stop "the bulk was already submitted"
[ "$(squeue --me -h -o %j | grep -c '^fd1b')" = "0" ] || stop "an fd1b job is queued"
$PY -c "import json,sys; v=json.load(open('$V/i2/walls-i2-0.json'))['verdict']; print('walls', v); sys.exit(0 if v=='PASS' else 1)" || stop "walls is not PASS"
n=$(git -C $DD status --porcelain | wc -l); h=$(git -C $DD rev-parse HEAD); echo "deploy porcelain_lines=$n head=$h"
[ "$n" = "0" ] && [ "$h" = "$M" ] || stop "deploy not clean at M"
cd $V/tables && sha256sum -c SHA256SUMS || stop "table digests"
INT="2p2h AGKYxF1pi AhtBY BhtBY CCQEPauliSupViaKF CV1uBY CV2uBY EtaNCEL FrAbs_N FrAbs_pi FrCEx_N FrCEx_pi FrElas_N FrElas_pi FrInel_N FrPiProd_N FrPiProd_pi HighQ2 LowQ2 MaCCQE MaNCEL MaRES MFP_N MFP_pi MvRES NormDISCC NormNCRES RDecBR1gamma Rvn1pi Rvn2pi Rvp2pi Theta_Delta2Npi VecFFCCQEshape"
{ ls $P/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz $P/s5c-20260924/runs/p2/bkg_dump.npz $BANK/cv.npz $P/fd-1b-20261030/pins.json
  for b in $INT; do ls $BANK/${b}_[0-9]_wt.npy $BANK/${b}_[0-9]_wr.npy $BANK/${b}_[0-9]_tdw.npy $BANK/${b}_[0-9]_bkgw.npy; done; } > $V/logs/i2-sources.txt || stop "a source is missing"
xargs -a $V/logs/i2-sources.txt stat -c '%X %Y %s %n' > $V/logs/i2-stat-before.txt; echo "stat-before lines=$(wc -l < $V/logs/i2-stat-before.txt)"
: > $V/logs/submit-i2.txt
for k in 0 1 2 3; do
  echo "sbatch -A m3246 -q regular -C cpu -t 03:30:00 -J fd1b_inv_i2n$k -o $V/logs/%x_%j.out $DD/docs/orchestration/state/gpu-timing-20261023/tools/sbatch_timing_packed.sh $DD $M $V/tables/tasks-i2.tsv $V/i2/lanes 32 56G $((8*k)) $((8*k+7)) inherit" >> $V/logs/submit-i2.txt
done
cat $V/logs/submit-i2.txt
bash $V/logs/submit-i2.txt > $V/logs/submit-i2.out 2>&1; echo "rc=$?" >> $V/logs/submit-i2.out
cat $V/logs/submit-i2.out
squeue --me -h -o "%i %j %T %l %D %R"
echo "end=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
