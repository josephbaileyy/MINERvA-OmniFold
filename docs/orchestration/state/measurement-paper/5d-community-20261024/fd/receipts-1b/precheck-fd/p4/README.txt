1B pre-check Part 1, P4: the readout. Login27, 2026-11-08T08:42:56–08:43:16Z, 0 node-h. ssh rc 0, connect rc 0,
readout rc 0. Part 1 stays at 9.3523 of its 18.5 node-h.

The director pre-approved the connect, pfd_p4_login.sh (sha256 7716c9bd...), on four conditions:
  1. the P3 receipt merged on origin/main: #928 at d110d7a8, checked with git merge-base before launch;
  2. P3's probe comparison read ALL MATCH P2;
  3. P3's product check read 327 present, 0 missing, 0 extra;
  4. the line "P3 merged at d110d7a8" was sent to the director before launch.
All four held. The report under FD-1B-PRECHECK-FD-DECLARATION.md §4.6 went to coverage-5b-audit and the director. The
verdicts below are quoted by key path from records/readout.json. CITABLE / NOT CITABLE is §4.6's, and this receipt
adds no reading of causes.

FILES
  pfd_p4_login.sh        the readout connect, sha256 7716c9bd01d9d44f0e6dd567133da260b096a49aec7444081920a7f20945656a
  p4.out, p4.err         its stdout (readout.json printed in full in section 8), and its stderr (login banner and
                         host line only)
  fence-mac.out, survey.txt  the Mac-side COV2D fence (08:40:59Z, no cov2d-* job) and the login-load survey (login27,
                         load 1.75 on 244)
  records/readout.json   extracted from p4.out section 8; sha256 8e05ca9bc2d0f2142b5c8d2bff28f05176c48f27454218390f09658344cea7b0,
                         equal to the value the connect printed on the cluster

WHAT RAN (p4.out)
  1. Fence: clear. One ens1_a1_dry job was RUNNING, which is an allowed name.
  2. A fresh clone at M_A1 8d7a40c2, porcelain 0. Every gated input matched its sha256:
     module a7fbbb58..., gate-d.json e1838c0a..., diag.json 6fd6669e..., i0.json 9a4142d3..., and
     h2_definition.json b6790761.... $V/p4 was absent and $V/unf held 327 products.
  3. Thread variables as inherited: all four unset, in bash and in Python. numpy 1.26.4; threadpoolctl reported one
     pool, openblas 0.3.30 at 128 threads on the login node.
  4. The stage was re-hashed with O_NOATIME against P1's record:
     - staged.json f2f06419... read with O_NOATIME;
     - 355 staged copies, 0 mismatches, 0 extra, 0 missing;
     - stage atime before vs after the rehash: 356 files, 0 moved.
  5. The originals (the spec's 355 sources), stat only, before the readout: stat-p4-before.txt (a14aeddf...) is
     byte-identical to P1's stat-before.txt and to P1's stat-after.txt.
  6. `fd_1b_precheck_fd.py readout`, rc 0. Its stdout:
       {"out": ".../p4/readout.json", "S": {"flux": "REPRODUCED", "detector": "REPRODUCED"},
        "K": {"flux": "PASS", "detector": "PASS"}}
     Its stderr was empty.
  7. Stage atime after the readout vs after the rehash: 356 files, 287 moved, through the bound module's reads. The
     originals after the readout: stat-p4-after.txt (a14aeddf...) is identical to stat-p4-before.txt, so they were
     unchanged through the readout.
     The digests the connect printed:
       stage-atime-before.tsv         ad7de880545aa54c7d7d066cfd3837ea45a4e922e2bf1cd46bf09635b8e5c2c9
       stage-atime-after-rehash.tsv   ad7de880545aa54c7d7d066cfd3837ea45a4e922e2bf1cd46bf09635b8e5c2c9
       stage-atime-after-readout.tsv  e0ed8e0fb9af5e0359266542b50b9e055dab6591097f8467498546cf9804e648
       stat-p4-before.txt             a14aeddf80d49fd7cb0d470e9296569e5f754d373dcd098800e828bbd20885a1
       stat-p4-after.txt              a14aeddf80d49fd7cb0d470e9296569e5f754d373dcd098800e828bbd20885a1
  8. readout.json printed with its sha256.

THE READINGS (records/readout.json; /window [0.9, 1.1], /resolve_k 4.0, 16 cells R00–R15, /label "DERIVATION")
  Rule S (§4.2):
    /groups/flux/rule_S/verdict "REPRODUCED" (16 resolved); /groups/detector/rule_S/verdict "REPRODUCED" (16)
    /bands/{Flux,GEANT_Pion,MinosEfficiency}/rule_S/verdict "REPRODUCED" (16 each)
    /bands/GEANT_Neutron/rule_S/verdict "DEPARTS" (14): cells_outside R00 R02 R08 R09 R10 R11
    /bands/GEANT_Proton/rule_S/verdict "DEPARTS" (14): cells_outside R01 R05 R07 R08
  Rule K (§4.4):
    /groups/flux/rule_K/verdict "PASS" (16); /groups/detector/rule_K/verdict "PASS" (16)
    /bands/{Flux,GEANT_Pion,MinosEfficiency}/rule_K/verdict "PASS" (16 each)
    /bands/GEANT_Neutron/rule_K/verdict "FAIL" (14): cells_outside R00 R02 R08 R09 R10 R11
    /bands/GEANT_Proton/rule_K/verdict "FAIL" (14): cells_outside R01 R05 R07 R08
    Recorded fact: in both FAIL bands, rule K's cells_outside are rule S's cells. The values_outside agree to about
    seven significant figures and are not equal.
  Rule F (§4.3):
    /groups/flux/rule_F and /bands/Flux/rule_F: n_cells 9; F_side 7, unresolved 2; level F_side "account",
      F_src and F_truth "refuted"
    /groups/detector/rule_F: n_cells 3; F_truth 3; F_truth "account"
    /bands/GEANT_Neutron/rule_F: n_cells 13; F_truth 13; F_truth "account"
    /bands/GEANT_Pion/rule_F: n_cells 13; F_truth 13; F_truth "account"
    /bands/GEANT_Proton/rule_F: n_cells 14; F_src 1, F_truth 13; F_truth "account"
    /bands/MinosEfficiency/rule_F: n_cells 4; F_truth 4; F_truth "account"
  Descriptive (§4.5, no verdict role): /descriptive/sqrt_A_phi_over_A_flux (16 values);
    /descriptive/detector_dump_equals_cv: wt_equals_cv false and denom_equals_cv true for all 8 detector universes.

WHAT EACH OUTCOME LICENSES (§4.6, verbatim)
  Rule S REPRODUCED for the flux and detector groups: with Part 0's interaction checks, "in all three drawn groups the
    pseudo-experiments reproduce, within 10 % in σ in every resolved cell, the block that the same weight factors give
    on the simulation side". NOT CITABLE FOR: coverage; that S1's flux or detector block is right; the laterals and
    normalization surrogates (29.0 % of the trace, gate-d.json:6), C_model and C_resp.
  Rule S DEPARTS for GEANT_Neutron and GEANT_Proton: "for band b the pseudo-experiments and the simulation side give
    blocks more than 10 % apart in σ in cells …", with the cells above. A finding for the director. NOT CITABLE FOR:
    which of a defect and a non-linearity causes it; any repair.
  Rule F, F_side the account (Flux): "gate D's departure for band b is mostly a comparison of unlike objects, the toys'
    factors against S1's whole universe at the same truth". NOT CITABLE FOR: why they differ (HF2 is descriptive);
    which object is right.
  Rule F, F_truth the account (the detector group, GEANT_Neutron, GEANT_Pion, GEANT_Proton and MinosEfficiency): "in
    the named cells, the dominant same-side factor is F_truth = √(A/M), the full universe at the nominal truth against
    S1's blocks". NOT CITABLE FOR: any study of the truth dependence, any mechanism for it, and any statement about
    which truth the intervals should use: all outside this study, as excluded item (c).
  Rule K PASS (bands Flux, GEANT_Pion and MinosEfficiency): "full-universe pseudo-data reproduce S1's universe
    block for band b at the nominal truth". NOT CITABLE FOR: that the toys realize S1's M; coverage.
  Rule K FAIL (GEANT_Neutron, GEANT_Proton): a finding for the director. NOT CITABLE FOR: a repair.
  In every outcome, Gate D's FAIL, Part 0 and every earlier record stand, and so does rule (iii).

ROUTING (§9)
  Rules read DEPARTS and FAIL, so the report goes through the director to Joseph. Part 0's §6 (a) is updated by a
  new record, under the director's routing. Nothing is submitted, deposited or tagged.
