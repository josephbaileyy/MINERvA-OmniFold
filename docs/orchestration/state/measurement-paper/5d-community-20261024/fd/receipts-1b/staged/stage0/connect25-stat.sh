# 1B staged, stage 0, connect 25 (FD-1B-STAGED-BINDING-1 ruling 4): metadata only (find -printf), iris, hpssquota,
# squeue. find -printf reads inode metadata; no file content is opened, so no atime moves.
P=/pscratch/sd/j/josephrb; W=$P/fd-1b-staged-20261102; V=$P/fd-1b-inv-20261101
BANK=$P/MINERvA-OmniFold/nd-unfolding/bank_sweep_5d_bkgaware
echo "host=$(hostname) start=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
[ -e $W ] && echo "NOTE: $W already exists" || echo "W absent: $W"
grp() {
  name=$1; shift
  find "$@" -maxdepth 0 -type f -printf '%A@ %s %p\n' 2>/dev/null | sort -n > /tmp/s0-stat-$$.txt
  n=$(wc -l < /tmp/s0-stat-$$.txt)
  if [ "$n" = 0 ]; then echo "$name | MISSING"; return; fi
  bytes=$(awk '{s+=$2} END {print s}' /tmp/s0-stat-$$.txt)
  old=$(head -1 /tmp/s0-stat-$$.txt | awk '{print int($1)}'); new=$(tail -1 /tmp/s0-stat-$$.txt | awk '{print int($1)}')
  echo "$name | n=$n | bytes=$bytes | oldest_atime=$(date -u -d @$old +%Y-%m-%dT%H:%M:%SZ) | newest_atime=$(date -u -d @$new +%Y-%m-%dT%H:%M:%SZ) | exposed_from=$(date -u -d @$((old + 56*86400)) +%Y-%m-%d)"
  rm -f /tmp/s0-stat-$$.txt
}
INT="2p2h AGKYxF1pi AhtBY BhtBY CCQEPauliSupViaKF CV1uBY CV2uBY EtaNCEL FrAbs_N FrAbs_pi FrCEx_N FrCEx_pi FrElas_N FrElas_pi FrInel_N FrPiProd_N FrPiProd_pi HighQ2 LowQ2 MaCCQE MaNCEL MaRES MFP_N MFP_pi MvRES NormDISCC NormNCRES RDecBR1gamma Rvn1pi Rvn2pi Rvp2pi Theta_Delta2Npi VecFFCCQEshape"
grp inputs_npz $P/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz
grp bkg_dump $P/s5c-20260924/runs/p2/bkg_dump.npz
grp bank_cv $BANK/cv.npz
grp pins $P/fd-1b-20261030/pins.json
grp bank_interaction $(for b in $INT; do echo $BANK/${b}_[0-9]_wt.npy $BANK/${b}_[0-9]_wr.npy $BANK/${b}_[0-9]_tdw.npy $BANK/${b}_[0-9]_bkgw.npy; done)
grp detector_dump $P/s5p-20260926/bank_detector/*.npy
grp i0_staged $(find $V/i0/in -type f 2>/dev/null)
grp i2_unf $V/i2/unf/fd1b_inv_*.npz
echo "i2_unf count A/B/C: $(ls $V/i2/unf/fd1b_inv_A_*.npz | wc -l)/$(ls $V/i2/unf/fd1b_inv_B_*.npz | wc -l)/$(ls $V/i2/unf/fd1b_inv_C_*.npz | wc -l)"
ls -d $V/i0/in/s1 $V/i0/in/derivation 2>&1
echo "== iris"; iris 2>&1 | grep -E "^m3246 " | head -1
echo "== hpssquota"; hpssquota 2>&1 | tail -4
echo "== squeue"; squeue --me -h -o "%i %j %T %l %D %R" | head
echo "end=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
