"""The declared scope of the s5p reproduction harness: what is replayed, what is regenerated, what is not.

Everything here is DATA read by ``repro_s5p.py``; nothing is computed. The receipts listed in ``RECEIPTS`` are
the authority for every expected value and digest; this file only pins which receipt bytes the harness was
written against (source commit ``SOURCE_COMMIT``) and declares the few facts no receipt records.

CITABLE FOR: the harness's advertised scope and tolerances. NOT CITABLE FOR: any physics result, grade or
adoption; those live in the receipts and ``VALIDATION_LEDGER.md`` (VL156-VL160).
"""

# The commit whose committed receipts this scope was written against (origin/main, 2026-09-28). The harness
# refuses a checkout whose receipts differ from the pins below instead of silently comparing to new numbers.
SOURCE_COMMIT = "129917715b2c7bbf29b4fd48e59a2eca6b8440cb"
FROZEN_ADMISSION_COMMIT = "4f5a613f"

# Absolute path prefixes the receipts RECORD. They are identities, never read directly: every recorded path
# is re-rooted onto the configured root of the same name (``config["roots"][name]``).
RECORDED_ROOTS = {
    "s5p": "/pscratch/sd/j/josephrb/s5p-20260926",
    "analysis": "/pscratch/sd/j/josephrb/MINERvA-OmniFold",
    "s5e": "/pscratch/sd/j/josephrb/s5e-20260925",
    "cvmfs": "/cvmfs",
}

# Committed receipts, logs, designs and figures in scope, with their sha256 at SOURCE_COMMIT.
S5P = "docs/orchestration/state/s5p"
GC = f"{S5P}/stage7/generator-context"
RECEIPTS = {
    f"{S5P}/gen5d/gen5d-build.json": "0652b2bc99387f265223555d545f0b2e4ccf534db5a96e0d1464e74b99e57073",
    f"{S5P}/gen5d/gen5d-fluxfix.json": "6325a4e948bf2c9f38b7e68ecf42aa8f724f9ae0ea8c0fc95f6e904c0e790260",
    f"{S5P}/gen5d/gen5d-fluxfix-2.json": "48a6b024248f1a347e8ab1709c8d9e4b1f099bae79c1e10f68c1aab10741d7b1",
    f"{S5P}/gen5d/gen5d-fluxfix-3.json": "4b8370c5d972f15caa7e4b6a014710cb21a653dcbd9a3faa5a1af75d281e49b2",
    f"{GC}/compare_mec_eavail_before-log.txt": "b3e0546e0e092e61b83fd5896ef488a2f9d04aae2792aca0b8d009e283a0efb8",
    f"{GC}/compare_mec_eavail-log.txt": "af6cf1091e235ebf591f92f82166418af8c02252f78c981e4dcb85c057948dc5",
    f"{GC}/eavail-marginal-ratios.json": "a55dc92396606c0d67f8288e52a0f3b3e7410cf9497b0da35c9545477640a557",
    f"{GC}/eavailW_band_s5p_repaired-log.txt": "9ce5a2eba9e0bde0efa7af049f72b80f3ce3c1217231e99a90cefc4f6faff506",
    f"{GC}/fullcov3d_s5p_repaired-log.txt": "b40d44a247573786af6402c56d58eff8c444240f226ac344c5191c5cbdf1b871",
    f"{GC}/gen3d_band_s5p_repaired-log.txt": "c433252c335e6fefecceee5ff8fe7e59de91fa445fd3047068d6ece0c57297ed",
    f"{GC}/generator-context-receipt.json": "106ecfcb78d5af14034f28dc1740ab56571368bd18f8f25699a3a47f8b92deda",
    f"{GC}/genie_cv_xsec_eavailW.json": "762ca4ef4aec9f5edaa9e39dd891f1dc4cb28bf887f0bedd37ab9d997d7bcf38",
    f"{GC}/genie_cv_xsec3d.json": "ffff5870ccbb999275afff8daa599de8c20af21d6e028f3609d87d4cdf50e48e",
    f"{GC}/genie_mec_xsec_eavailW.json": "75769a93acaa271836ea03eea120f8384bede2755e8744d01713242598488243",
    f"{GC}/genie_mec_xsec3d.json": "300a21bf67f8f45fbf031f8cc71957cb35fd16957f57ebef63c8b44446049b18",
    f"{GC}/gibuu_cv_xsec_eavailW.json": "a07e39ce2f4e0dc05163993bd60caf65df4da818c3ad279934303151f0471b26",
    f"{GC}/gibuu_cv_xsec3d.json": "5a50d0a54e2cf42fbde18d76fc7e71ecda13c03aa5e61a19f224dac28b55d834",
    f"{GC}/mode_decomp_eavail_before-log.txt": "5cda4bf45525607d7d72dc2e2e6166bf7c9cf334164fb53a2940948f89a70c45",
    f"{GC}/mode_decomp_eavail-log.txt": "ef2ac8afdd77f8c676939872805b97d9f4ebbd929db77551384fce8a5486576b",
    f"{GC}/nuwro_cv_xsec_eavailW.json": "33d2197d700ca1b88794985843b03b5c6c684eee85770691d0c9fc389611200b",
    f"{GC}/nuwro_cv_xsec3d.json": "fe7b79fec97168eb5b19fd52bfa9f391773cdc17a6628b300253423e5918c386",
    f"{S5P}/stage3/f2/delta-genie_cv.json": "9b527f31f069667615e4f674901b7e6675025ee534713dae38d2473cd55e3f5c",
    f"{S5P}/stage3/f2/delta-genie_mec.json": "8b5313b9e437be620ea4f71d2658617f064279be9afce3f001181f3744a5f689",
    f"{S5P}/stage3/f2/delta-gibuu_cv.json": "cfa4a05cc25c362faa7ee08d89fa9485ffbb5c03dd15571328d84f94577de2e7",
    f"{S5P}/stage3/f2/delta-nuwro_cv.json": "7e7bf729a95630c9eb33f5255a58446acda2cd80ac845d7d746a29085794d59c",
    f"{S5P}/stage3/f4/D-genie_cv.json": "34d2b429dc7a8065b421113aca43a71cd3a48dc1def8f8022325d30467e80d44",
    f"{S5P}/stage3/f4/D-genie_mec.json": "88effbbd35876404b9da98444eca6af3c974cdbc996b14aa17c7b34cf04825f0",
    f"{S5P}/stage3/f4/D-gibuu_cv.json": "1b0996541a866aacbf86052c52e90567ed08d5d1a3e4bb612b82d56bd842e1ef",
    f"{S5P}/stage3/f4/D-mnvtune_v1.json": "9234cd7a61adbc0c1e686333d7110e805fa3429dc1200cca16fc88a4e76c3eb8",
    f"{S5P}/stage3/f4/D16-genie_cv.json": "bf6e34f206752431ae060fd6ff5a818e4a354c3e8a458aa3740661eab73f1d3f",
    f"{S5P}/stage3/f4/D16-genie_mec.json": "1826df9fbf699194594c49463c7b4572a941f8594545af48bc7b782279177709",
    f"{S5P}/stage3/f4/D16-gibuu_cv.json": "683cd4f1811e7c9894f9814563a7613aefeed0187f268eecc2ffb4de238e6247",
    f"{S5P}/stage3/f4/D16-mnvtune_v1.json": "0a618cf8f1cd28a9f77805a9f452a3e258697d857651faafe7790dd4c1e859ac",
    f"{S5P}/stage3/f4/D16-nuwro_cv.json": "08a0e46d7015446dbc3ecbe65eca06a017c5ec518ebd00a6b99e6d536b4236eb",
    f"{S5P}/stage3/m1/fine-minus-mid-genie_cv.json": "0fd7863c3fb0094fdfa550587de28aa868b1086e60525ecaf70b95dd2456147a",
    f"{S5P}/stage3/m1/fine-minus-mid-genie_mec.json": "83bf1b9aaf879de60c7d6e2e4230d5dc82dae59c941a5f2c646d9d8111b6980a",
    f"{S5P}/stage3/m1/fine-minus-mid-gibuu_cv.json": "cce31a03e6d947ba21579895802356cc556874e3d9964282558d86acb6e4d85a",
    f"{S5P}/stage3/m1/fine-minus-mid-nuwro_cv.json": "31d1dffa285a0a9266ba70acdf1b1793756782d10f79868f7d4edb3c4f145ab4",
    f"{S5P}/stage3/V/V-receipt.json": "001ce7f0e4bad45888d196c8329b1ac7e87fe5d13557fb360ba266e46107ffed",
    f"{S5P}/stage3/prefreeze/devpower.json": "41e455ba57f2f4d6d01b031a88ed9b89b5acfbefde2a3a15915bf99f50e39bd8",
    f"{S5P}/stage3/prefreeze/units.json": "2bafa9084be7925fa443fa2a63e45c556fee7bb8a4f709bb59a1972ce49186f3",
    f"{S5P}/stage3/envelope-receipt.json": "1b40940f705e36f0303671ebfd347dbdb159dd8585f07de037171ef13cd61a72",
    f"{S5P}/prod-draft/design.json": "2f44cfba8fd6b39e36916ec402fd8d80b0165d377e3f41da3e0aa80d3830990c",
    f"{S5P}/prod/design.json": "404446eb2a770dc4412012c5e182e57a77afa2edd332c75de399a9281f536285",
    f"{S5P}/stage1/stage1_inspect.json": "def4c67cfb59f5ae917f86d2745416b172be6aca3764eba11f3d116db4621d9d",
    "docs/orchestration/state/s5c/contract.json": "d54fd7c9641901736e58430e666db1ee782a54d9c95bf4439541872567c39c93",
    "docs/analysis-note/figures/compare_3d_fullcov.pdf": "5adf08606732cd4b077512aeebd8770164fae30fc45f759f64de9e003bbdfccd",
    "docs/analysis-note/figures/compare_mec_eavail.pdf": "254f49f5b085c65e0ad84ba91c8dc7323dd5b36952bdd3c95c6aec42441da8cb",
    "docs/analysis-note/figures/eavailW_band.pdf": "555c5f1e634ad3c5d9c91f6d2fe611197dad7d85bb5a87bae13303c6afed797f",
    "docs/analysis-note/figures/generators_vs_unfolded_band.pdf": "d60063bbeaed1383c33cc6c3bb77fe29903ff110fdcbdf521046c0f6e0bb4bf2",
    "docs/analysis-note/figures/mode_decomp_eavail.pdf": "27a4f879574ab226026469988f761cf3d7d598b06ddedde7371f8ce9a13a9d58",
    "docs/analysis-note/figures/paper_eavailW_generators.pdf": "db10ba4161c76839242241c124bea78f839551e4b4559cb2eb579f8e53ccf9ec",
}

# Receipts whose recorded (path, sha256) pairs are digest-checked in tier A. The J-partition definitions
# (stage1_inspect.json, the s5c contract) are pinned above but record other campaigns' products, not inputs here.
DIGEST_SOURCES = [p for p in RECEIPTS if p.endswith(".json")
                  and p not in (f"{S5P}/stage1/stage1_inspect.json", "docs/orchestration/state/s5c/contract.json")]

# Recorded digests that are KNOWN not to hold for the preserved bytes, each with the measurement that
# established it. They are still measured and reported (status DECLARED_DIFFERENCE), never skipped, and a
# match would be reported as a match.
DECLARED_DIFFERENCES = {
    "/pscratch/sd/j/josephrb/s5p-20260926/runs/s2/conv/k_b0_gibuu.npz.partial.npz": (
        "a running trace's checkpoint: the envelope receipt (committed 66cf3129, 2026-09-27 01:24 PDT) recorded "
        "sha256 1998b347...; the file now hashes to 1fbbdf95... with mtime 2026-09-27 02:12 PDT, after the receipt "
        "(measured 2026-09-28). The envelope reads only iteration 5 of the checkpoint, and its d1 linearity block "
        "regenerates exactly from the later file (tier B); only the recorded digest differs."),
    "/pscratch/sd/j/josephrb/s5p-20260926/runs/s2/conv/k_b0_w1.npz.partial.npz": (
        "a running trace's checkpoint: recorded dc39afb5...; the file now hashes to d06c46a1... with mtime "
        "2026-09-27 02:32 PDT, after the receipt (measured 2026-09-28). The d2 linearity block regenerates exactly "
        "from the later file (tier B); only the recorded digest differs."),
    "/pscratch/sd/j/josephrb/s5p-20260926/gen5d_fluxfix/code/run_gen5d_supplement.sh": (
        "gen5d-fluxfix-2.json records two digests for this copy: supplement_flux.code (6b925371...) and, in the "
        "top-level and every product's code, 9c208852... (the committed e13caf87 blob and the copy today). "
        "README-gen5d-fluxfix.md round 2 says of the supplement flux file: 'The file itself was written once, by an "
        "earlier version of the script, and is never overwritten'; "
        "that earlier version is in no commit. The flux file itself is digest-checked and matches."),
}
# Envelope receipt fields that record those checkpoints' digests (compared; a difference is DECLARED_DIFFERENCE).
_GIBUU_PARTIAL = "/pscratch/sd/j/josephrb/s5p-20260926/runs/s2/conv/k_b0_gibuu.npz.partial.npz"
_W1_PARTIAL = "/pscratch/sd/j/josephrb/s5p-20260926/runs/s2/conv/k_b0_w1.npz.partial.npz"
ENVELOPE_DECLARED_FIELDS = {("bias_sources", "d1"): _GIBUU_PARTIAL, ("bias_sources", "d2"): _W1_PARTIAL}

# Recorded code digests with no copy on disk and no commit: {(producer name, sha256): the DECLARED_DIFFERENCES key}.
DECLARED_CODE = {("run_gen5d_supplement.sh", "6b92537160eb91a3f4c820da8a1a23b998c82d8a9721f4a2702a8355a2f52a75"):
                 "/pscratch/sd/j/josephrb/s5p-20260926/gen5d_fluxfix/code/run_gen5d_supplement.sh"}

# The figure producers ran from a scratch export of this commit (gen5d-fluxfix-3.json `code`); the export
# directory s5p:deploy/4e4b4f56 has since been removed, so its bytes are checked as the commit's git blobs.
FIGURE_DEPLOY_COMMIT = "4e4b4f56"

# Committed producers that must be byte-identical in the checkout to the copy that ran (recorded sha256 ->
# checkout path). The copies live under s5p/deploy/<sha>/ or s5p/gen5d_fluxfix/code/ on the cluster.
PRODUCER_FILES = {
    "gen5d_flux_reweight.py": "3d-unfolding/genie/gen5d_flux_reweight.py",
    "gen5d_flux_supplement.py": "3d-unfolding/genie/gen5d_flux_supplement.py",
    "run_gen5d_supplement.sh": "3d-unfolding/genie/run_gen5d_supplement.sh",
    "gen5d_mode_components.py": "3d-unfolding/genie/gen5d_mode_components.py",
    "gen5d_to_rootpreds.py": "3d-unfolding/genie/gen5d_to_rootpreds.py",
    "compare_mec_eavail.py": "3d-unfolding/genie/compare_mec_eavail.py",
    "mode_decomp_eavail.py": "3d-unfolding/genie/mode_decomp_eavail.py",
    "s5p_pairdiff.py": "nd-unfolding/s5p_pairdiff.py",
    "s5p_prefreeze.py": "nd-unfolding/s5p_prefreeze.py",
    "s5p_envelope.py": "nd-unfolding/s5p_envelope.py",
    "s5p_stage2_analyze.py": "nd-unfolding/s5p_stage2_analyze.py",
}
# Receipts that record a producer's sha256 without its path: (receipt glob, JSON key path, producer name).
PRODUCER_SHA_FIELDS = [
    (f"{GC}/*_xsec3d.json", ("code_sha256",), "gen5d_to_rootpreds.py"),
    (f"{GC}/*_xsec_eavailW.json", ("code_sha256",), "gen5d_to_rootpreds.py"),
    (f"{S5P}/stage3/f2/*.json", ("code_sha256",), "s5p_pairdiff.py"),
    (f"{S5P}/stage3/f4/*.json", ("code_sha256",), "s5p_pairdiff.py"),
    (f"{S5P}/stage3/m1/*.json", ("code_sha256",), "s5p_pairdiff.py"),
    (f"{S5P}/stage3/prefreeze/*.json", ("code_sha256",), "s5p_prefreeze.py"),
    (f"{S5P}/stage3/envelope-receipt.json", ("code_sha256", "s5p_envelope.py"), "s5p_envelope.py"),
    (f"{S5P}/stage3/envelope-receipt.json", ("code_sha256", "s5p_stage2_analyze.py"), "s5p_stage2_analyze.py"),
]

# Inputs no s5p receipt records a digest for. They are pinned by the harness's own `pin` command
# (reproduction/s5p/pins/*.json, labelled as lane-measured); a later mismatch means the bytes changed since
# the pin, and a tier-B bitwise regeneration from them is what ties them to production.
UNRECORDED_INPUT_GLOBS = {
    "figure data (canonical analysis checkout, untracked)": [
        "analysis:3d-unfolding/xsec_3d_MEFHC_5iter_lgbm.root",
        "analysis:3d-unfolding/uq_3d/universe_stage2_3d/uq_universe_3d_covariance.root",
        "analysis:3d-unfolding/uq_3d/stat_band_3d.root",
        "analysis:3d-unfolding/genie/model_tunev1_xsec3d.root",
        "analysis:3d-unfolding/genie/genie_cv_xsec3d.root",
        "analysis:3d-unfolding/genie/genie_mec_cv_xsec3d.root",
        "analysis:3d-unfolding/genie/genie_mefhc_cv_ALL.gst.root",
        "analysis:nd-unfolding/products/5d/excess_eavail_W.root",
    ],
    "joint-design inputs (lateral endpoints, data jitters, data central)": [
        "s5p:runs/s3/latunf/lat_*_b-_j-.npz",
        "s5p:runs/s2/num/data/data_b-_j*.npz",
    ],
    "V ensemble and development-power pilot": [
        "s5p:runs/s3v/pilot/null_mnvtune/null_mnvtune_s*.npz",
        "s5p:runs/s3v/pilot/p1/p1_s*.npz",
        "s5p:runs/s3v/pilot/p2/p2_s*.npz",
        "s5p:runs/s3v/pilot/p3/p3_s*.npz",
    ],
    "M1 merged-x2 asimovs": ["s5p:runs/s3r/f2/s3v_m1_*_mid.npz"],
    "envelope d3 pseudo ensemble (s5e)": ["s5e:runs/cand/assess/W2/*.npz"],
    "MnvTune 5D prediction": ["s5p:gen5d/mnvtune_v1_xsec5d.npz"],
}

# Numerical tolerances (relative, |a - b| <= tol * max(|a|, |b|)).
TOL_SAME_CODE = 1e-12   # same producer, same interpreter/numpy: bitwise expected; 1e-12 admits BLAS/summation order
TOL_CROSS_CODE = 1e-12  # the same total computed by two committed producers with different summation order

# Tier-B figure runs: producer (checkout-relative), argv template, the committed log it must reproduce, and the
# campaign's output figure it is compared with. {rp} = this run's regenerated prediction dir; {a:...} {s:...}
# re-root a path onto the configured analysis / s5p root. Argv mirror docs/analysis-note/make_figures.sh and
# the recorded argv of gen5d-fluxfix-3.json `runs`.
GENFIG = "s5p:stage7/genfig/3d-unfolding/genie"
FIGURE_RUNS = {
    "eavailW_band": {
        "producer": "3d-unfolding/genie/overlay_eavailW_band.py",
        "argv": ["--data", "{a:nd-unfolding/products/5d/excess_eavail_W.root}",
                 "--gen", "GENIE-CV:{rp}/genie_cv_xsec_eavailW.root", "--gen", "GENIE+MEC:{rp}/genie_mec_xsec_eavailW.root",
                 "--gen", "NuWro:{rp}/nuwro_cv_xsec_eavailW.root", "--gen", "GiBUU:{rp}/gibuu_cv_xsec_eavailW.root",
                 "--png", "eavailW_band.png", "--out", "eavailW_band.root"],
        "log": f"{GC}/eavailW_band_s5p_repaired-log.txt",
        "figures": {"eavailW_band.pdf": "docs/analysis-note/figures/eavailW_band.pdf"},
    },
    "generators_vs_unfolded_band": {
        "producer": "3d-unfolding/genie/overlay_generators_band.py",
        "argv": ["--unfolded", "{a:3d-unfolding/xsec_3d_MEFHC_5iter_lgbm.root}",
                 "--cov", "{a:3d-unfolding/uq_3d/universe_stage2_3d/uq_universe_3d_covariance.root}:hCov_combined3d_total",
                 "--syst-cov", "{a:3d-unfolding/uq_3d/universe_stage2_3d/uq_universe_3d_covariance.root}:hCov_universe3d_total",
                 "--band", "{a:3d-unfolding/uq_3d/stat_band_3d.root}",
                 "--generator", "GENIE-CV:{rp}/genie_cv_xsec3d.root",
                 "--generator", "Tune-v1:{a:3d-unfolding/genie/model_tunev1_xsec3d.root}",
                 "--generator", "NuWro:{rp}/nuwro_cv_xsec3d.root", "--generator", "GiBUU:{rp}/gibuu_cv_xsec3d.root",
                 "--out", "generators_vs_unfolded_band"],
        "log": f"{GC}/gen3d_band_s5p_repaired-log.txt",
        "figures": {"generators_vs_unfolded_band.pdf": "docs/analysis-note/figures/generators_vs_unfolded_band.pdf"},
    },
    "compare_3d_fullcov": {
        "producer": "3d-unfolding/genie/compare_3d_fullcov.py",
        "argv": ["--data", "{a:3d-unfolding/xsec_3d_MEFHC_5iter_lgbm.root}",
                 "--cov", "{a:3d-unfolding/uq_3d/universe_stage2_3d/uq_universe_3d_covariance.root}:hCov_combined3d_total",
                 "--generator", "GENIE-CV:{rp}/genie_cv_xsec3d.root",
                 "--generator", "Tune-v1:{a:3d-unfolding/genie/model_tunev1_xsec3d.root}",
                 "--generator", "NuWro:{rp}/nuwro_cv_xsec3d.root", "--generator", "GiBUU:{rp}/gibuu_cv_xsec3d.root",
                 "--out", "compare_3d_fullcov"],
        "log": f"{GC}/fullcov3d_s5p_repaired-log.txt",
        "figures": {"compare_3d_fullcov.pdf": "docs/analysis-note/figures/compare_3d_fullcov.pdf"},
    },
    "compare_mec_eavail": {
        "producer": "3d-unfolding/genie/compare_mec_eavail.py",
        "argv": ["--data", "{a:3d-unfolding/xsec_3d_MEFHC_5iter_lgbm.root}",
                 "--cv", "{s:stage7/genfig/3d-unfolding/genie/genie_cv_xsec3d_modes.root}",
                 "--mec", "{s:stage7/genfig/3d-unfolding/genie/genie_mec_cv_xsec3d.root}",
                 "--cov", "{a:3d-unfolding/uq_3d/universe_stage2_3d/uq_universe_3d_covariance.root}",
                 "--plot", "{out}/compare_mec_eavail.png"],
        "log": f"{GC}/compare_mec_eavail-log.txt",
        "figures": {"compare_mec_eavail.pdf": "docs/analysis-note/figures/compare_mec_eavail.pdf"},
        "note": "inputs are the campaign's stored mode files (not regenerated here; see NOT_REGENERATED 'mode-components')",
    },
    "compare_mec_eavail_before": {
        "producer": "3d-unfolding/genie/compare_mec_eavail.py",
        "argv": ["--data", "{a:3d-unfolding/xsec_3d_MEFHC_5iter_lgbm.root}",
                 "--cv", "{a:3d-unfolding/genie/genie_cv_xsec3d.root}",
                 "--mec", "{a:3d-unfolding/genie/genie_mec_cv_xsec3d.root}",
                 "--cov", "{a:3d-unfolding/uq_3d/universe_stage2_3d/uq_universe_3d_covariance.root}",
                 "--plot", "{out}/compare_mec_eavail_before.png"],
        "log": f"{GC}/compare_mec_eavail_before-log.txt",
        "figures": {},
    },
    "mode_decomp_eavail_before": {
        "producer": "3d-unfolding/genie/mode_decomp_eavail.py",
        "argv": ["--gst", "{a:3d-unfolding/genie/genie_mefhc_cv_ALL.gst.root}",
                 "--cv", "{a:3d-unfolding/genie/genie_cv_xsec3d.root}",
                 "--data", "{a:3d-unfolding/xsec_3d_MEFHC_5iter_lgbm.root}",
                 "--cov", "{a:3d-unfolding/uq_3d/universe_stage2_3d/uq_universe_3d_covariance.root}",
                 "--plot", "{out}/mode_decomp_eavail_before.png"],
        "log": f"{GC}/mode_decomp_eavail_before-log.txt",
        "figures": {},
    },
}

# Tier C: full scientific regeneration. Declared with its dependency; the harness never runs it. Each entry is
# reported NOT_RUN so the report cannot be read as covering it.
NOT_REGENERATED = {
    "gen5d-flux-reweight": {
        "what": "the <50 GeV flux-repaired 5D predictions (genie_cv/genie_mec/nuwro_cv_xsec5d.npz) and phi_t",
        "producer": "3d-unfolding/genie/gen5d_flux_reweight.py (argv in gen5d-fluxfix.json `argv`)",
        "needs": "the generator event samples of gen5d-build.json, the sha-pinned export s5p:gen5d/code/tree (81d94a95), "
                 "PlotUtils (MINERvA101/opt/lib) and the cvmfs flux files named in gen5d-fluxfix.json `inputs`",
        "why_not_run": "regenerates a final product from events; the producer hardcodes its output root "
                       "(S5P/REPO constants), so a run would write into the campaign namespace",
    },
    "gen5d-flux-supplement": {
        "what": "the 50-100 GeV supplements, the *_xsec5d_full.npz merges and the GiBUU flux-convention product",
        "producer": "3d-unfolding/genie/gen5d_flux_supplement.py and run_gen5d_supplement.sh (gevgen/gntpc, NuWro)",
        "needs": "GENIE v2_12_10c and NuWro 21.09.1 on cvmfs, the supplement flux, new event generation",
        "why_not_run": "event generation is new scientific compute; hardcoded output root as above",
    },
    "mode-components": {
        "what": "genie_cv_xsec3d_modes.root, genie_mec_cv_xsec3d.root and the sigma-weighted mode_decomp_eavail run "
                "(the note's mode_decomp_eavail.pdf)",
        "producer": "3d-unfolding/genie/gen5d_mode_components.py files|mode-decomp",
        "needs": "the GENIE gst event samples and the supplement events",
        "why_not_run": "the producer writes only to its hardcoded GENFIG (the campaign's stage7 directory); making it "
                       "redirectable is a producer change. Its stored outputs are digest-checked in tier A and the "
                       "compare_mec_eavail figure is regenerated from them in tier B",
    },
    "generator-events": {
        "what": "the GENIE CV / GENIE+MEC / NuWro / GiBUU event samples themselves",
        "producer": "gen5d-build.json `code` (run_gevgen.sh, run_nuwro.sh, GiBUU jobcards)",
        "needs": "generator installations on cvmfs and CPU time",
        "why_not_run": "new event generation",
    },
    "unfolding-runs": {
        "what": "the GBDT unfolds feeding the pre-freeze numbers: F2 fine/coarse and M1 mid asimovs (runs/s3r/f2), "
                "F4 half/quarter pseudo experiments (runs/s3r/f4), the s3v pilot ensembles (V, devpower), the "
                "s2 prior and trace unfolds (envelope), the lateral endpoint unfolds and the data jitters",
        "producer": "nd-unfolding/s5p_nullexp.py, s5p_converge.py, s5e/s5c runners via the campaign queues",
        "needs": "production CPU allocation under the campaign's admission",
        "why_not_run": "production compute; not authorized for this task",
    },
    "paper-crop": {
        "what": "docs/analysis-note/figures/paper_eavailW_generators.pdf",
        "producer": "docs/analysis-note/make_figures.sh: pdfcrop --margins '4 4 4 4' eavailW_band.pdf",
        "needs": "pdfcrop (TeX Live), absent on Perlmutter login nodes",
        "why_not_run": "tool absent where the inputs are; the committed file's digest is checked in tier A",
    },
}

# Tier D: the final joint result. Reported PENDING until the terminal products exist and are committed.
JOINT = {
    "committed_result": f"{S5P}/stage7/joint/joint-evaluate.json",
    "design": f"{S5P}/prod/design.json",
    "v_receipt": f"{S5P}/stage3/V/V-receipt.json",
    "terminal_condition": "all five s5p:runs/prod/status/<null>-final.json exist, no Slurm job named s5p-s5p_cal_* "
                          "or s5p-s5p_pow_* is queued, the campaign has committed stage7/joint/joint-evaluate.json, and "
                          "an independent recomputation (task 1 of HANDOFF-20260928-s5p-parallel-tasks.md) has "
                          "reported agreement",
    "nulls": ["MnvTune_v1", "GENIE_2_12_10_CV", "GENIE_2_12_10_MEC", "NuWro_21_09", "GiBUU_2019"],
}
