# RE-1 run 2, F: paths shared by the two F jobs (sourced after re1_env.sh). $C is the F deploy.
CUR3D=$A/3d-unfolding/xsec_3d_MEFHC_5iter_lgbm.root;           CUR3D_SHA=0dd94830821576a3b060fae2d4a20564610c535ed06046cd1eb05cd11885dd59
CUR4D=$A/nd-unfolding/products/4d/xsec_4d_MEFHC_5iter_lgbm.root; CUR4D_SHA=1fb8250820c00428fc547cb05aa95535023146723acdccb61f615f3fa763f9d2
EU=$A/2d-unfolding/uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root; EU_SHA=4f5a1b6d44b9e7212b233650bb00bfb626ae65461e3bf8033cd67866dbd7eb2c
EC=$A/2d-unfolding/2d_crossSection_omnifold_MEFHC_5iter.root;    EC_SHA=142a45b0efc753d91e95376c28ac3f6a477d582014a919e49d6d71079a127fd5
ANC=$A/2d-unfolding/minerva_paper_anc/cov_ptpl_minerva_inclusive_6GeV.root
S7G=/pscratch/sd/j/josephrb/s5p-20260926/stage7/genfig/3d-unfolding
SUPP=$A/3d-unfolding/genie/ascencio_2110.13372_supplemental.txt
FIGS=$C/docs/analysis-note/figures      # the current figures, read only
F=$O/f
