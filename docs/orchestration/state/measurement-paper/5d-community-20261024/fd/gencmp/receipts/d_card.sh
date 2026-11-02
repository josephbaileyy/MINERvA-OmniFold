# write_card SEED N FLUX: the production C12 card (work_nuwro_p1/params.txt) with only the target keys changed to a CH
# mixture: carbon as production (E_b 34, kF 220, nucleus_target 2), hydrogen as MP3-B (free proton, nucleus_target 0)
write_card() {
cat > params.txt <<CARD
random_seed = $1
number_of_events = $2
number_of_test_events = 50000
beam_particle = 14
beam_type = 5
beam_inputroot = $3
beam_inputroot_flux = flux_numu
target_type = 1
target_content = 6 6 1x 34 220 2
target_content += 1 0 1x 0 0 0
dyn_qel_cc = 1
dyn_res_cc = 1
dyn_dis_cc = 1
dyn_coh_cc = 1
dyn_mec_cc = 1
CARD
}
