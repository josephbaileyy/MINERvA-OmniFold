Band diagnosis, P4: the readout (FD-1B-BAND-DIAGNOSIS-DECLARATION.md sections 4.4-4.7 and 5; BINDING-1 rulings 2, 5
and 6). Run by limitation-resolver on login27, 2026-11-09T04:46:06–04:46:10Z, at nice 19 and 0 node-h, with no Slurm
job.

RELEASE: the director's pre-approved go on bdg_p4_login.sh sha256 f145bccec6b71ce52e324cfeeb6880b69e7c3bb812426cf02dc6831710f5669a,
to run once P3's post had passed (126 products; an identical re-stat: #968). The node compared the digest before
running it. The sshproxy certificate is valid to 2026-11-10T00:11:04Z (ssh-keygen -L, read locally).

THE RUN: readout rc 0; connect rc 0; ssh rc 0 (read unpiped).
- Fence clear: no job queued.
- P2's deploy was still at M with no tracked change. The module 658ca918, Part 1's readout.json 8e05ca9b and I0's
  i0.json 9a4142d3 were gated. There were 126 products in $W/unf.
- The thread variables were unset, both as inherited and in Python (numpy 1.26.4), as in P1 and Part 1's P4.
- Section 5: the 73 sources were re-stat'd before the readout (stat-before-readout.txt) and after it
  (stat-after-readout.txt). Both are byte-identical to P1's stat-before.txt (7986e2bf...).
- readout.json, sha256 553c3dff..., was extracted from p4.out, and its sha256 equals the cluster's. readout.stdout is
  65373f7e...; readout.stderr is empty.
- The readout's own controls passed:
  - all 126 products were validated: identity, the one-code keys less estimator_seed, and the estimator at each
    product's seed;
  - seed 42's F_src and resolved cells equal Part 1's readout.json;
  - I0's floor kind is "measured".
  It hashed 163 files at first read: 126 new products, Part 1's 27, the 9 derivation copies and the S1 assembly.

THE READINGS (readout.json /bands/<b>; the window is [0.9, 1.1]; the departing cells are Part 1's)

Section 4.4, the seed (HB1): every departing cell reads SEED-STABLE.
  GEANT_Neutron, R00 R02 R08 R09 R10 R11: SEED-STABLE in all 6 cells.
  GEANT_Proton, R01 R05 R07 R08: SEED-STABLE in all 4 cells.
  - Descriptive: F_src is the same at the five seeds 42, 45, 48, 51 and 54. The largest standard deviation of ln F_src
    over the seeds is 4.4e-16 (GEANT_Neutron), 0 (GEANT_Proton), 3.5e-18 (GEANT_Pion) and 1.7e-18 (MinosEfficiency).
  - The cells outside the window are the same at every seed: Part 1's six and four in the two subject bands, and none
    in GEANT_Pion or MinosEfficiency.
  - §4.7 has no CITABLE FOR row for SEED-STABLE; that outcome only admits the cell to §4.5. So no sentence is licensed
    for the seed reading itself.

Section 4.5, the scale (HB2/HB3): both subject bands read MIXED.
  cell             F_src at eps 1/2, 1, 2       p_up     p_down   cell reading
  GEANT_Neutron
    R00            1.097, 1.201, 1.042          -2.149   0.991    MIXED
    R02            1.027, 1.398, 0.994          -inf     3.655    MIXED
    R08            0.823, 0.863, 1.060          -inf     -0.398   MIXED
    R09            unresolved, 2.237, 1.077     -3.440   (eps 1/2 unresolved)  MIXED
    R10            0.779, 0.775, 1.047          -inf     0.029    MIXED
    R11            0.674, 0.701, 2.371          -inf     -0.148   MIXED
  GEANT_Proton
    R01            unresolved, 1.166, 0.897     -inf     (eps 1/2 unresolved)  MIXED
    R05            unresolved, 1.248, 1.012     -4.244   (eps 1/2 unresolved)  MIXED
    R07            1.018, 1.123, 1.020          -2.531   2.688    MIXED
    R08            1.114, 1.101, 1.096          -0.063   -0.167   CONSTANT
  Band readings: GEANT_Neutron MIXED (all 6 cells MIXED); GEANT_Proton MIXED (R01 R05 R07 MIXED; R08 CONSTANT).
  p_up = -inf where l(2) <= 0, that is, where F_src at eps 2 has returned to 1 or crossed it. This holds in R02, R08, R10
  and R11 for GEANT_Neutron and in R01 for GEANT_Proton.
  §4.7 licence, "§4.5 MIXED or NOT READ": CITABLE FOR "the values only"; NOT CITABLE FOR "a mechanism". So neither band
  is licensed as a non-linearity (SCALES) or as a first-order mismatch (CONSTANT). The single CONSTANT cell (GEANT_Proton
  R08) does not make its band CONSTANT, and on its own it is cited as a value only.

Section 4.6, descriptive (no verdict role):
  - HC, the channels at seed 42, eps 1. F_src^signal and F_src^background in the departing cells:
      GEANT_Neutron signal: R00 1.048, R02 1.149, R08 0.966, R09 1.143, R10 0.956, R11 1.010 (14 cells resolved).
      GEANT_Neutron background: 1 cell resolved. The values in the departing cells (R00 0.152, R02 0.011, R08 5.397, R09
        0.786, R10 5.185, R11 11.732) are therefore mostly in unresolved cells, and are values only.
      GEANT_Proton signal: R01 0.574, R05 1.173, R07 1.015, R08 1.006 (14 cells resolved).
      GEANT_Proton background: 0 cells resolved.
  - F_src(eps) for the reference bands, all 16 cells resolved at every eps:
      GEANT_Pion: outside the window at eps 1/2 in R01 and R09, at eps 1 in none, and at eps 2 in R01, R05, R09 and R14.
      MinosEfficiency: outside the window in no cell at any eps.
  - HW shares and the per-universe cell values s_E,i and s_B,i for every variant are in P2's inputs.json (#965) and
    here in readout.json (/bands/<b>/cell_values).

Section 4.3, from P2 (#965): EQUAL. §4.7 licence: "the pseudo-data and the simulation side carry the same factor on the
same reco rows inside the window, for every detector universe". NOT CITABLE FOR anything inside the estimator, or HW's
rows outside the window.

Section 4.2, from P1 (#955): SAME COMPARISON in all four detector bands, a record of Part 1's products, not a test.

IN EVERY OUTCOME (§4.7): Part 1's record, gate D's FAIL, Part 0, rule (iii) and the coverage test's primary reading
stand. No outcome here is a coverage statement. No repair and no study of the truth dependence (item c) follows from
this campaign (BINDING-1 ruling 1).

COST: P2 0.457 + P3 3.282 = 3.74 CPU node-h of the 9.0 cap (P0, P1 and P4 at 0).

FILES: bdg_p4_login.sh, p4.out (the full transcript: the gates, the stats and readout.json printed), p4.err (the NERSC
banner only), fence-mac.out, survey.txt, readout.json. Digests: SHA256SUMS.txt.
