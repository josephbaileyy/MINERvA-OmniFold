#!/bin/bash
#SBATCH -q regular
#SBATCH -C cpu
#SBATCH -N 1
#SBATCH -t 00:15:00
#SBATCH -A m3246
#SBATCH -J gencmp-dprobe
#SBATCH -o /pscratch/sd/j/josephrb/gencmp-20261101/logs/dprobe-%j.out
# Step D probe: 64 concurrent CH-mixture chunks of 2000 events (PROBE lines of d_SEEDS.txt), each converted with the
# frozen flat macro; measures the per-event wall cost for the projection. Writes only under $B/d/probe.
B=/pscratch/sd/j/josephrb/gencmp-20261101
G=/pscratch/sd/j/josephrb/MINERvA-OmniFold/3d-unfolding/genie
FLAT=/pscratch/sd/j/josephrb/s5p-20260926/gen5d/code/nuwro_to_flat_5d.C
FLUX=$G/flux_mefhc_numu_nuwro.root
source $B/receipts/d_card.sh
mkdir -p $B/d/probe || exit 2
echo "host $(hostname) start $(date -u +%FT%TZ) nproc $(nproc)"
sha256sum $G/setup_nuwro.sh $FLAT $FLUX $B/receipts/d_SEEDS.txt $B/receipts/d_card.sh
run() {
  local i=$1 s=$2 n=$3 W=$B/d/probe/c$1 t0 t1 rc
  mkdir -p $W && cd $W && cp $G/setup_nuwro.sh . && source ./setup_nuwro.sh > setup.log 2>&1
  write_card $s $n $FLUX
  t0=$(date +%s.%N)
  "$NUWRO_HOME/bin/nuwro" -i params.txt -o nuwro.root > nuwro.log 2>&1; rc=$?
  t1=$(date +%s.%N)
  frc=-1; [ $rc = 0 ] && { root -l -b -q "$FLAT(\"nuwro.root\",\"flat5d.root\")" > flat.log 2>&1; frc=$?; }
  echo "$i $s $n rc=$rc flat=$frc wall=$(echo "$t1 - $t0" | bc)" > RESULT
}
while read -r tag i s n; do [ "$tag" = PROBE ] && run $i $s $n & done < $B/receipts/d_SEEDS.txt
wait
cat $B/d/probe/c*/RESULT | sort -n
grep -h "target_content\|nucleus_target\|target_type" $B/d/probe/c1/nuwro.root.par
echo "end $(date -u +%FT%TZ)"
