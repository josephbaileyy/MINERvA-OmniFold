# 1B investigation, I2-0 submission (FD-1B-INV-BINDING rulings 1 and 7)
P=/pscratch/sd/j/josephrb; V=$P/fd-1b-inv-20261101; DD=$V/deploy; M=b1c615f12fca5f8597d34750b2c074f1fd7b2cdd
BANK=$P/MINERvA-OmniFold/nd-unfolding/bank_sweep_5d_bkgaware
echo "host=$(hostname) start=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
stop() { echo "STOP: $*"; exit 2; }
[ -e $V/logs/submit-i2-0.out ] && stop "I2-0 was already submitted"
[ "$(squeue --me -h -o %j | grep -c '^fd1b')" = "0" ] || stop "an fd1b job is queued"
n=$(git -C $DD status --porcelain | wc -l); h=$(git -C $DD rev-parse HEAD); echo "deploy porcelain_lines=$n head=$h"
[ "$n" = "0" ] && [ "$h" = "$M" ] || stop "deploy not clean at M"
cd $V/tables && sha256sum -c SHA256SUMS || stop "table digests"
mkdir -p $V/i2/unf $V/i2/lanes
ls $V/i2/unf | head -3
ls $P/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz $P/s5c-20260924/runs/p2/bkg_dump.npz $BANK/cv.npz $P/fd-1b-20261030/pins.json \
   $BANK/MaRES_0_*.npy $BANK/2p2h_0_*.npy $BANK/LowQ2_1_*.npy > $V/logs/i2-0-sources.txt || stop "a source is missing"
xargs -a $V/logs/i2-0-sources.txt stat -c '%X %Y %s %n' > $V/logs/i2-0-stat-before.txt; echo "stat-before lines=$(wc -l < $V/logs/i2-0-stat-before.txt)"
echo "== hpssquota"; hpssquota 2>&1 | tail -4
echo "== iris"; iris 2>&1 | grep -E "^m3246 " | head -1
cat > $V/logs/submit-i2-0.txt <<SUB
sbatch -A m3246 -q regular -C cpu -t 01:00:00 -J fd1b_inv_i20 -o $V/logs/%x_%j.out $DD/docs/orchestration/state/gpu-timing-20261023/tools/sbatch_timing_packed.sh $DD $M $V/tables/tasks-i2-0.tsv $V/i2/lanes 32 56G 0 7 inherit
SUB
cat $V/logs/submit-i2-0.txt
bash $V/logs/submit-i2-0.txt > $V/logs/submit-i2-0.out 2>&1; echo "rc=$?" >> $V/logs/submit-i2-0.out
cat $V/logs/submit-i2-0.out
squeue --me -h -o "%i %j %T %l %D %R"
echo "end=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
