# 1B investigation, ruling 7 first step: stat-only (no content read) of every input in the declaration's sections 4
# and 8, and the iris balance. stat and find -printf read metadata only; atime is unchanged by them.
P=/pscratch/sd/j/josephrb
B=$P/fd-1b-20261030
BANK=$P/MINERvA-OmniFold/nd-unfolding/bank_sweep_5d_bkgaware
echo "host=$(hostname) start=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
grp() {  # name, then paths or globs: count, total bytes, oldest and newest atime (UTC)
  name=$1; shift
  find "$@" -maxdepth 0 -type f -printf '%A@ %s %p\n' 2>/dev/null | sort -n > /tmp/inv-stat-$$.txt
  n=$(wc -l < /tmp/inv-stat-$$.txt)
  if [ "$n" = 0 ]; then echo "$name | MISSING | $*"; return; fi
  bytes=$(awk '{s+=$2} END {print s}' /tmp/inv-stat-$$.txt)
  old=$(head -1 /tmp/inv-stat-$$.txt | awk '{print int($1)}'); new=$(tail -1 /tmp/inv-stat-$$.txt | awk '{print int($1)}')
  echo "$name | n=$n | bytes=$bytes | oldest_atime=$(date -u -d @$old +%Y-%m-%dT%H:%M:%SZ) ($(head -1 /tmp/inv-stat-$$.txt | awk '{print $3}')) | newest_atime=$(date -u -d @$new +%Y-%m-%dT%H:%M:%SZ) | exposed_from=$(date -u -d @$((old + 56*86400)) +%Y-%m-%d)"
  rm -f /tmp/inv-stat-$$.txt
}
echo "== section 4 (I0)"
grp derivation $B/runs/derivation/fd1b_derivation_*.npz
grp s1_uni $P/s1-20261024/runs/uni/S1_*.npz
grp s1_assembly $P/s1-20261024/s1_assembly.npz
grp jitter_data_base $P/s5p-20260926/runs/s2/num/data/data_b-_j-.npz
grp jitter_data $(for j in $(seq 1 20); do echo $P/s5p-20260926/runs/s2/num/data/data_b-_j$j.npz; done)
grp jitter_nom_base $P/s5p-20260926/runs/s2/num/nom/nom_b-_j-.npz
grp jitter_nom $(for j in $(seq 1 20); do echo $P/s5p-20260926/runs/s2/num/nom/nom_b-_j$j.npz; done)
grp flux_constraint $P/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt
echo "== section 8 (I1, I2)"
grp inputs_npz $P/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz
grp bkg_dump $P/s5c-20260924/runs/p2/bkg_dump.npz
grp bank_cv $BANK/cv.npz
INT="2p2h AGKYxF1pi AhtBY BhtBY CCQEPauliSupViaKF CV1uBY CV2uBY EtaNCEL FrAbs_N FrAbs_pi FrCEx_N FrCEx_pi FrElas_N FrElas_pi FrInel_N FrPiProd_N FrPiProd_pi HighQ2 LowQ2 MaCCQE MaNCEL MaRES MFP_N MFP_pi MvRES NormDISCC NormNCRES RDecBR1gamma Rvn1pi Rvn2pi Rvp2pi Theta_Delta2Npi VecFFCCQEshape"
files=""; for b in $INT; do for f in $BANK/${b}_[0-9]_wt.npy $BANK/${b}_[0-9]_wr.npy $BANK/${b}_[0-9]_tdw.npy $BANK/${b}_[0-9]_bkgw.npy; do files="$files $f"; done; done
grp bank_interaction $files
grp detector_dump $P/s5p-20260926/bank_detector/*.npy
grp pins $B/pins.json
echo "== the investigation directory"
ls -ld $P/fd-1b-inv-20261101 2>&1
echo "== iris"
iris 2>&1 | grep -i -E "m3246|charged|remaining|allocation" | head -8
echo "end=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
