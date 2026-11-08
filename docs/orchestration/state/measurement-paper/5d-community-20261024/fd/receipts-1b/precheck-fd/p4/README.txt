1B pre-check Part 1, P4: the readout. Login27, 2026-11-08T08:42:56–08:43:16Z, 0 node-h. ssh rc 0, connect rc 0,
readout rc 0. Part 1 stays at 9.3523 of its 18.5 node-h.

The director pre-approved the connect, pfd_p4_login.sh (sha256 7716c9bd...), on four conditions:
  1. the P3 receipt merged on origin/main: #928 at d110d7a8, checked with git merge-base before launch;
  2. P3's probe comparison read ALL MATCH P2;
  3. P3's product check read 327 present, 0 missing, 0 extra;
  4. the line "P3 merged at d110d7a8" was sent to the director before launch.
All four held. The report under FD-1B-PRECHECK-FD-DECLARATION.md §4.6 went to coverage-5b-audit and the director. The
verdicts below are quoted by key path from records/p4/readout.json. CITABLE / NOT CITABLE is §4.6's, and this receipt
adds no reading of causes.

FILES
  pfd_p4_login.sh        the readout connect, sha256 7716c9bd01d9d44f0e6dd567133da260b096a49aec7444081920a7f20945656a
  p4.out, p4.err         its stdout (readout.json printed in full in section 8), and its stderr (login banner and
                         host line only)
  fence-mac.out, survey.txt  the Mac-side COV2D fence (08:40:59Z, no cov2d-* job) and the login-load survey (login27,
                         load 1.75 on 244)
  pfd_p4_fetch.sh        the records fetch connect (director's go), sha256 675a91124ed17b2194dd3a61fdea17e5b2a537be7558d2f0747f0868c80a7317;
                         login16, 08:50:11–08:50:12Z, ssh rc 0, connect rc 0; stdout fetch.out (base64 tar body replaced by
                         a note giving the decoded tar's sha256), stderr fetch.err (login banner and host line only);
                         fence-mac-fetch.out and survey-fetch.txt before it. Read-only: it listed $V/p4 and tarred the
                         eight files below.
  records/p4/            the eight files the P4 connect wrote in $V/p4: readout.json, readout.stdout, readout.stderr
                         (empty), stage-atime-{before,after-rehash,after-readout}.tsv, stat-p4-{before,after}.txt.
                         Each file's sha256 equals the fetch connect's cluster value. Each also equals the value
                         p4.out printed where it printed one: readout.json 8e05ca9b... (and byte-identical to the copy
                         printed in p4.out section 8), the three atime TSVs and the two stat files. readout.stdout is
                         identical to the stdout block p4.out printed. stat-p4-before.txt is byte-identical to the
                         committed ../p1/stat-before.txt and ../p1/stat-after.txt.

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

THE §4.6 REPORT, VERBATIM (as sent to coverage-5b-audit and the director at about 08:46Z; key paths refer to
records/p4/readout.json, and "$V/p4/readout.json" in it is the cluster copy of that file)

limitation-resolver: 1B pre-check Part 1, P4 readout, reported under FD-1B-PRECHECK-FD-DECLARATION.md §4.6. Two bands read rule S DEPARTS and rule K FAIL, so under §9 this goes through the director to Joseph. Nothing has been repaired.

RUN
- Connect 7716c9bd on login27, 08:42:56–08:43:16Z. ssh rc 0, connect rc 0, readout rc 0. 0 node-h. Part 1 stays at 9.3523 of 18.5.
- The clone was M_A1 8d7a40c2, porcelain 0. All five gated inputs matched: module a7fbbb58, gate-d.json e1838c0a, diag.json 6fd6669e, i0.json 9a4142d3, h2_definition.json b6790761.
- Thread variables were all unset, as inherited.
- The stage was re-hashed with O_NOATIME: staged.json f2f06419; 355 copies, 0 mismatches; 0 stage atimes moved by the rehash.
- The originals were byte-identical to P1's stat-before.txt and stat-after.txt, both before and after the readout.
- The readout moved 287 of 356 stage atimes, through the bound module's reads.
- The fence was clear. One ens1_a1_dry job was RUNNING, which is an allowed name.
- $V/p4/readout.json has sha256 8e05ca9bc2d0f2142b5c8d2bff28f05176c48f27454218390f09658344cea7b0. It records /label "DERIVATION", /window [0.9, 1.1], /resolve_k 4.0 and 16 cells R00–R15.

RULE S (§4.2)
- /groups/flux/rule_S/verdict = "REPRODUCED" (n_resolved 16)
- /groups/detector/rule_S/verdict = "REPRODUCED" (n_resolved 16)
- /bands/Flux, /bands/GEANT_Pion, /bands/MinosEfficiency rule_S/verdict = "REPRODUCED" (n_resolved 16 each)
- /bands/GEANT_Neutron/rule_S/verdict = "DEPARTS" (n_resolved 14). cells_outside R00 R02 R08 R09 R10 R11; values_outside 1.2014260434211335, 1.3983995971629335, 0.8628697063641, 2.236784746210021, 0.774661868550449, 0.7008669416195834.
- /bands/GEANT_Proton/rule_S/verdict = "DEPARTS" (n_resolved 14). cells_outside R01 R05 R07 R08; values_outside 1.1655700559538589, 1.2480385118402284, 1.1226848309922257, 1.1005467893969223.

What this licenses:
- Groups REPRODUCED: with Part 0's interaction checks, "in all three drawn groups the pseudo-experiments reproduce, within 10 % in σ in every resolved cell, the block that the same weight factors give on the simulation side". NOT CITABLE FOR: coverage; that S1's flux or detector block is right; the laterals and normalization surrogates (29.0 % of the trace, gate-d.json:6), C_model and C_resp.
- GEANT_Neutron DEPARTS: "for band GEANT_Neutron the pseudo-experiments and the simulation side give blocks more than 10 % apart in σ in cells R00, R02, R08, R09, R10, R11". A finding for the director. NOT CITABLE FOR: which of a defect and a non-linearity causes it; any repair.
- GEANT_Proton DEPARTS: "for band GEANT_Proton the pseudo-experiments and the simulation side give blocks more than 10 % apart in σ in cells R01, R05, R07, R08". A finding for the director. NOT CITABLE FOR: the same.

RULE K (§4.4)
- /groups/flux/rule_K/verdict = "PASS" (16)
- /groups/detector/rule_K/verdict = "PASS" (16)
- /bands/Flux, /bands/GEANT_Pion, /bands/MinosEfficiency rule_K/verdict = "PASS" (16 each)
- /bands/GEANT_Neutron/rule_K/verdict = "FAIL" (14). cells_outside R00 R02 R08 R09 R10 R11; values_outside 1.2014260680240505, 1.398399671154345, 0.8628697070032427, 2.2367847069679385, 0.7746618716766284, 0.7008669408588012.
- /bands/GEANT_Proton/rule_K/verdict = "FAIL" (14). cells_outside R01 R05 R07 R08; values_outside 1.1655700130666518, 1.2480384958884063, 1.122684817124418, 1.1005467800473963.

What this licenses:
- PASS, for band b = Flux, GEANT_Pion and MinosEfficiency: "full-universe pseudo-data reproduce S1's universe block for band b at the nominal truth". NOT CITABLE FOR: that the toys realize S1's M; coverage.
- FAIL, for GEANT_Neutron and GEANT_Proton: a finding for the director. NOT CITABLE FOR: a repair.

Recorded fact, with no cause read: in both FAIL bands, rule K's cells_outside are the same cells as rule S's. The values agree to about seven significant figures but are not equal.

RULE F (§4.3)
- /groups/flux/rule_F and /bands/Flux/rule_F, identical: n_cells 9; counts F_src 0, F_side 7, F_truth 0, unresolved 2; level F_side "account", F_src "refuted", F_truth "refuted". F_side is attributed in R00 R02 R03 R05 R08 R10 R14. R07 and R13 have factor null.
- /groups/detector/rule_F: n_cells 3; counts F_truth 3; level F_truth "account", F_src and F_side "refuted". Cells R03 R05 R06.
- /bands/GEANT_Neutron/rule_F: n_cells 13; F_truth 13; F_truth "account". Cells R00–R05, R08–R12, R14, R15.
- /bands/GEANT_Pion/rule_F: n_cells 13; F_truth 13; F_truth "account". Cells R00–R07, R10–R13, R15.
- /bands/GEANT_Proton/rule_F: n_cells 14; F_src 1 (R01), F_truth 13; F_truth "account", F_src "refuted". F_truth cells R02–R09, R11–R15.
- /bands/MinosEfficiency/rule_F: n_cells 4; F_truth 4; F_truth "account". Cells R03 R05 R06 R07.

What this licenses:
- F_side the account (the flux group and band Flux): "gate D's departure for band Flux is mostly a comparison of unlike objects, the toys' factors against S1's whole universe at the same truth". NOT CITABLE FOR: why they differ (HF2 is descriptive); which object is right.
- F_truth the account (the detector group and bands GEANT_Neutron, GEANT_Pion, GEANT_Proton and MinosEfficiency): "in the named cells, the dominant same-side factor is F_truth = √(A/M), the full universe at the nominal truth against S1's blocks". The named cells are those listed above. NOT CITABLE FOR: any study of the truth dependence, any mechanism for it, and any statement about which truth the intervals should use: all outside this study, as excluded item (c).

DESCRIPTIVE (§4.5, no verdict role)
- /descriptive/sqrt_A_phi_over_A_flux has 16 values.
- /descriptive/detector_dump_equals_cv: for all 8 detector universes, wt_equals_cv is false and denom_equals_cv is true.

IN EVERY OUTCOME
Gate D's FAIL, Part 0 and every earlier record stand, and so does rule (iii).

NEXT
- The P4 receipt PR, with the connect output, readout.json and the stat and atime records, follows.
- Under §9, Part 0's §6 (a) is updated by a new record. I'll leave that to the director's routing.

ROUTING (§9)
  Rules read DEPARTS and FAIL, so the report goes through the director to Joseph. Part 0's §6 (a) is updated by a
  new record, under the director's routing. Nothing is submitted, deposited or tagged.
