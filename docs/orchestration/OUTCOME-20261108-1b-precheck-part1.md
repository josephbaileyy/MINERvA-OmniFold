# OUTCOME 2026-11-08: the 1B pre-check, Part 1 (flux and detector groups). Both groups REPRODUCE; bands GEANT_Neutron and GEANT_Proton DEPART

**Recorded by** the director (paper-tighten lane), for Joseph, as `FD-1B-PRECHECK-FD-DECLARATION.md` §9 requires: two
bands read DEPARTS (rule S) and FAIL (rule K). The run lane is limitation-resolver.

**The design:** `state/measurement-paper/5d-community-20261024/FD-1B-PRECHECK-FD-DECLARATION.md`, bound by
`FD-1B-PRECHECK-FD-BINDING-1.md` at M = `ed8f328f`. Addendum A1 (control M rebuilt from the H2 definition) is at
M_A1 = `8d7a40c2` (#921).

**The record:** `fd/receipts-1b/precheck-fd/p4/records/p4/readout.json`, sha256
`8e05ca9bc2d0f2142b5c8d2bff28f05176c48f27454218390f09658344cea7b0` (receipt #930). It was produced by the bound
module's `readout` at M_A1 (module `a7fbbb58`), with all five gated inputs at their pins.
- coverage-5b-audit read the receipt and found it a sound record, with no findings (comment on #930). The stat and
  atime records check out, and every value in the lane's §4.6 report matches readout.json by key path.
- Below, `[path]` is a key path in readout.json.

**The steps:**

| step | receipt | result |
|---|---|---|
| P0 | #876 | |
| P1 | #877 | INVALID on control M |
| P1 rerun | #922 | controls E and M passed |
| CV bitwise check | #924 | A, B and Dnom equal the derivation CV |
| P2, the pilot | #923 | walls PASS |
| P3, the bulk | #928 | 327 products; thread probes match P2's |
| P4, the readout | #930 | |

**The cost:** 9.3523 of the 18.5 CPU node-h cap. The originals were byte-identical by stat before and after every
step.

## The readings (§4.2–§4.5)

| | rule S [`…/rule_S/verdict`] | rule K [`…/rule_K/verdict`] | rule F's account [`…/rule_F`] |
|---|---|---|---|
| **flux group** | REPRODUCED (16 resolved) | PASS (16) | **F_side**, in 7 of 9 cells (R00 R02 R03 R05 R08 R10 R14); R07 and R13 unresolved |
| **detector group** | REPRODUCED (16) | PASS (16) | **F_truth**, in R03 R05 R06 |
| band Flux | REPRODUCED (16) | PASS | as the flux group |
| band GEANT_Pion | REPRODUCED (16) | PASS | F_truth in 13 cells |
| band MinosEfficiency | REPRODUCED (16) | PASS | F_truth in 4 cells (R03 R05 R06 R07) |
| **band GEANT_Neutron** | **DEPARTS** (14 resolved): outside [0.9, 1.1] in R00 R02 R08 R09 R10 R11, at 1.201, 1.398, 0.863, 2.237, 0.775 and 0.701 | **FAIL**: the same cells | F_truth in 13 cells |
| **band GEANT_Proton** | **DEPARTS** (14 resolved): outside in R01 R05 R07 R08, at 1.166, 1.248, 1.123 and 1.101 | **FAIL**: the same cells | F_truth in 13 cells; F_src in R01 |

- **A recorded fact, no cause read:** in both failing bands, rule K's cells_outside are rule S's cells, and the values
  agree to about seven significant figures without being equal.
- **Descriptive only (§4.5):** for all 8 detector universes, `detector_dump_equals_cv` reads wt_equals_cv false and
  denom_equals_cv true. `sqrt_A_phi_over_A_flux` has 16 values.

## CITABLE FOR (§4.6, as licensed)

- **Both groups REPRODUCED.** With Part 0's interaction checks: *"in all three drawn groups the pseudo-experiments
  reproduce, within 10 % in σ in every resolved cell, the block that the same weight factors give on the simulation
  side."*
- **Rule K PASS for bands Flux, GEANT_Pion and MinosEfficiency:** *"full-universe pseudo-data reproduce S1's universe
  block for band b at the nominal truth."*
- **GEANT_Neutron DEPARTS:** *"for band GEANT_Neutron the pseudo-experiments and the simulation side give blocks more
  than 10 % apart in σ in cells R00, R02, R08, R09, R10, R11."* The same sentence holds for GEANT_Proton, in R01, R05,
  R07 and R08.
- **F_side the account, for flux:** *"gate D's departure for band Flux is mostly a comparison of unlike objects, the
  toys' factors against S1's whole universe at the same truth."*
- **F_truth the account, for the detector group and bands:** *"in the named cells, the dominant same-side factor is
  F_truth = √(A/M), the full universe at the nominal truth against S1's blocks."*

## NOT CITABLE FOR

- **Coverage,** in any form. That S1's flux or detector block is right.
- **That the toys realize S1's M.**
- **The terms outside this study:** the lateral and normalization surrogates (29.0 % of the trace, `gate-d.json:6`), C_model
  and C_resp.
- **For GEANT_Neutron and GEANT_Proton:** whether a defect or a non-linearity causes the departure, and any repair.
- **For F_side:** why the objects differ (HF2 is descriptive), or which one is right.
- **For F_truth:** any study of the truth dependence, any mechanism for it, or which truth the intervals should use.
  These are excluded item (c).
- **Any wording for the paper or the note.**

## What it changes, and what stands

- **Part 0's §6 (a) is updated by this record** (§9); Part 0 itself is not edited. The flux group's open question is
  answered by F_side as the account. The detector group's is answered by F_truth, except that two of its bands,
  GEANT_Neutron and GEANT_Proton, depart, with no cause licensed.
- **Unchanged:** gate D's FAIL, Part 0, every earlier record, and 1B's rule (iii).
- **For Joseph, not decided here:**
  - whether to diagnose the GEANT_Neutron and GEANT_Proton departure, which needs a new declaration;
  - whether to lift the exclusion on item (c), the truth dependence, which F_truth now names as the dominant factor in
    most detector cells.

  Neither is started.

Nothing is submitted, deposited or tagged.
