#!/bin/bash
# run_gen5d_supplement.sh MODE ... -- the E_nu 50-100 GeV supplement samples for the
# gen5d flux fix (KNOWN_ISSUES 83), generated with the main samples' generator setup.
#
#   run_gen5d_supplement.sh genie  {cv|mec} N SEED WORKDIR FLUXFILE
#   run_gen5d_supplement.sh nuwro  N SEED WORKDIR FLUXFILE
#   run_gen5d_supplement.sh graphs EMAX OUTFILE
#
# genie: the gevgen/gntpc lines of run_gevgen.sh verbatim (same setup_genie.sh, so the same
#   GENIE v2_12_10c, gxspl_CH.xml.gz splines, CH target mix, laconic messenger), except
#   -n, -e 50,100, -f FLUXFILE,flux_numu, the seed, and the work dir. mec adds
#   --event-generator-list Default+CCMEC exactly as sbatch_gevgen_mec.sh does.
#   (run_gevgen.sh itself cannot be reused: setup_genie.sh hard-sets GENIE_FLUX and the
#   script hard-codes -e 0,50.)
# nuwro: run_nuwro.sh's params.txt verbatim (same setup_nuwro.sh, NuWro 21.09.1 e20:debug,
#   C12, all CC dynamics, 50000 test events) except random_seed, number_of_events and
#   beam_inputroot; then nuwro_to_flat_5d.C (the gen5d copy) instead of nuwro_to_flat.C.
# graphs: gspl2root of the same splines for C12 and H1 up to EMAX GeV.
set -eo pipefail
G=/pscratch/sd/j/josephrb/MINERvA-OmniFold/3d-unfolding/genie
GEN5D_CODE=/pscratch/sd/j/josephrb/s5p-20260926/gen5d/code
MODE=$1; shift

case "$MODE" in
  genie)
    VAR=$1; N=$2; SEED=$3; WORK=$4; FLUX=$5
    set +e; source "$G/setup_genie.sh"; RC=$?; set -e
    [ $RC -eq 0 ] || { echo "setup_genie.sh failed rc=$RC" >&2; exit 1; }
    LIST=""; [ "$VAR" = mec ] && LIST="Default+CCMEC"
    mkdir -p "$WORK"; cd "$WORK"
    MSG="$GENIE/config/Messenger_laconic.xml"
    echo "[supp] genie $VAR N=$N seed=$SEED flux=$FLUX start $(date -u '+%F %T UTC')"
    gevgen \
      -n "$N" \
      -e 50,100 \
      -p 14 \
      -t '1000060120[0.9225],1000010010[0.0775]' \
      -f "${FLUX},flux_numu" \
      --cross-sections "$GENIE_SPLINES" \
      ${LIST:+--event-generator-list "$LIST"} \
      --seed "$SEED" \
      -r "$SEED" \
      ${MSG:+--message-thresholds "$MSG"} \
      > "gevgen_supp_${VAR}.log" 2>&1
    echo "[supp] gevgen rc=$? $(date -u '+%F %T UTC')"
    # gntpc prints ~8 kB per event; keep the tail (run_gevgen.sh pipes it to tail -3)
    gntpc -i "gntp.${SEED}.ghep.root" -f gst -o "genie_supp_${VAR}.gst.root" 2>&1 | tail -200 > gntpc.log
    echo "[supp] gntpc done $(date -u '+%F %T UTC')"
    ;;
  nuwro)
    N=$1; SEED=$2; WORK=$3; FLUX=$4
    set +e; source "$GEN5D_CODE/setup_nuwro.sh"; RC=$?; set -e
    [ $RC -eq 0 ] || { echo "setup_nuwro.sh failed rc=$RC" >&2; exit 1; }
    mkdir -p "$WORK"; cd "$WORK"
    cat > params.txt <<EOF
random_seed = $SEED
number_of_events = $N
number_of_test_events = 50000
beam_particle = 14
beam_type = 5
beam_inputroot = $FLUX
beam_inputroot_flux = flux_numu
target_type = 0
nucleus_p = 6
nucleus_n = 6
dyn_qel_cc = 1
dyn_res_cc = 1
dyn_dis_cc = 1
dyn_coh_cc = 1
dyn_mec_cc = 1
EOF
    echo "[supp] nuwro N=$N seed=$SEED start $(date -u '+%F %T UTC')"
    set +e
    "$NUWRO_HOME/bin/nuwro" -i params.txt -o nuwro_supp.root > nuwro_supp.log 2>&1
    RC=$?
    set -e
    echo "[supp] nuwro rc=$RC $(date -u '+%F %T UTC')"
    [ $RC -eq 0 ] || exit $RC
    root -l -b -q "$GEN5D_CODE/nuwro_to_flat_5d.C(\"nuwro_supp.root\",\"nuwro_supp_flat5d.root\")" \
      > flat5d.log 2>&1
    echo "[supp] flat5d done $(date -u '+%F %T UTC')"
    ;;
  graphs)
    EMAX=$1; OUT=$2
    set +e; source "$G/setup_genie.sh"; RC=$?; set -e
    [ $RC -eq 0 ] || exit 1
    rm -f "$OUT"
    gspl2root -f "$GENIE_SPLINES" -p 14 -t 1000060120,1000010010 -e "$EMAX" -o "$OUT" \
      > "${OUT%.root}.log" 2>&1
    echo "[supp] gspl2root rc=$? -> $OUT"
    ;;
  *) echo "unknown mode $MODE" >&2; exit 2 ;;
esac
