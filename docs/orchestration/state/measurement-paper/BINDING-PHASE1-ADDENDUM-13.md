# Binding addendum 13: MP-2 S2 readings R0–R13, the disclosures, and the S2+S3 compute (2026-10-22)

**By** the paper-tighten lane, as director, from an independent read-only draft (an agent; every source re-hashed or quoted) that the director reviewed and amended, under [`BINDING-PHASE1-ADDENDUM-8.md`](BINDING-PHASE1-ADDENDUM-8.md) and
[`BINDING-PHASE1-ADDENDUM-9.md`](BINDING-PHASE1-ADDENDUM-9.md).

**The request:** `phase1/mp2/S2-IMPLEMENTATION.md`, PR #231, head `dac42a09`. The frozen contract is
`feature_contract_draft.json` `98141c2f…`, re-hashed by the director.

**Timing.** These rulings come before any production model, gate or S3 output exists, as addendum 8 requires. The
four timing-probe models in `fit_probe/` are never read.

**CITABLE FOR:** the readings, the dispositions and the grant below.
**NOT CITABLE FOR:** any result, or any claim (claims are Joseph's).

Items marked **[Joseph]** are flagged to him. He may override any ruling here.

## What the session reported

- All four generators and the Tune v1 C+H table are harmonized under `code-v3` (`3e1ad6e2…`, read-only).
- Every control passed:
  - H0 bitwise;
  - N to ≤ 7.6e-13 relative, with nevt exact;
  - A bitwise;
  - Z: GENIE and NuWro zero; GiBUU as below.
- The S2 charge is 0.282 CPU node-h over 8 jobs. Phase 1 stands at 7.885 of 35.
- The probe measured 152–161 s per model at 4 per node. The best iterations were 2970–3000 of the cap of 3000.

## Rulings on the readings

| # | ruling |
|---|---|
| R0 | **Accepted.** E_avail is MAT's `GetEAvailableTrue`, unthresholded, the analysis coordinate (S1 C3 bitwise). The γ < 10 MeV drop and the species thresholds apply to the species sums, the multiplicities and the leading-particle features. JSON `de_excitation`'s "every feature" is read as excluding the five measurement coordinates |
| R1 | **Accepted.** A per-class 10% draw with `default_rng([lgbm_random_state_k, h, f])`; `[v1_split_seed, 1]` and `[gvg_split_seed, 1]` for V1 and its control. **R1b:** the V1 and control `random_state` are `v1_split_seed` and `gvg_split_seed` |
| R2 | **Accepted.** One c per (G, replica), over the Tune C+H in-grid rows inside G's support. **Carried to S3:** before any S3 output, a committed reading of what J_event's non-domain rows (other nuclei, out of support) carry against each reference, or the computed residual, so that the primary Δ_hyb contains no r_h − r_an term. **[Joseph, informed]** |
| R3 | **Accepted.** V2–V4 on all five replicas; a gate passes only if all five pass |
| R4 | **Accepted.** V1 on replica k = 0 by position |
| R5 | **Accepted.** The bins in `S2-IMPLEMENTATION.md` R5. **R5b (new):** the "no bin beyond 3σ" check of addendum 8 (b) runs over the bins used for χ². Every excluded bin is reported with each side's share, and one-sided bins are reported as support gaps |
| R6 | **Accepted: shape closure.** s = ΣG / ΣT is classifier-independent, because c fixes ΣT to Σ w_truth r_an. The gates assert s equal across the replicas to ≤ 1e-12 relative. The S2 report gives s, g0, and the identity s · k_T · f_CH,an = 1. V2 and V3 are described everywhere as "shape closure at the hybrid's rate". **[Joseph]** For the wording, and for any wish for an absolute-rate test (a contract change) |
| R7 | **Accepted, with sizes as in R10.** The control is two disjoint random subsets of all of G's events, each the size of V1's G sample, drawn with `gvg_split_seed`; V1's protocol; n_estimators fixed to V1's best iteration |
| R8 | **Accepted.** j is the entry index in the declared file order. The JSON's G-fold formula is taken literally |
| R9 | **Accepted.** V4 over the in-support rows, with N their count. The out-of-support count and its w_truth share per J cell are reported |
| R10 | **Ruled differently.** V1's gate sample is replica 0's Tune rows of fold 0 (both halves; ≤ 4M by `v1_split_seed`), weighted w_truth·w_G, against G's events of G-fold 0. The session's pooled V1 is run beside it as **descriptive** |
| R11 | **Accepted.** As addendum 9 amendment 3 |
| R12 | **Accepted.** Before submission, a login-node count (0 node-h) of undecayed charmed hadrons in Tune C+H, GENIE and NuWro against GiBUU. A mismatch above 1e-3 of in-grid rate comes to the director before the GiBUU fit |
| R13 | **Ruled differently.** `tgt == 11` events stay in the harmonized products, H_CH,an and N, as frozen. They are **excluded** from G's training, V1 and V3 samples, under the contract's target rule (MP3-A's precedent). The `S2-IMPLEMENTATION.md` counts are corrected to the receipt's CC counts (CV 1 + 8, MEC 0 + 17) |

## The frozen V2 and V3 thresholds [Joseph]

- Under exact closure, χ²/ndf ≤ 1.5 fails 13–19% of the time at V3's ndf of 5–10, about 45% per replica over the four
  distributions. "No J cell beyond 3σ" fails about 26% over 109 cells.
- The thresholds stay as frozen. The gates report every p-value and every pull.
- Whether to replace them with size-controlled rules is Joseph's decision. It must be committed before the gates job
  runs, or it cannot apply.

## Disclosures

1. **GiBUU Z: accepted as corrected, recorded as post hoc.**
   - Two redefinitions after failures. Each corrected a mis-specified population: a missing final nucleon (an energy
     deficit of 0.94 GeV), and DIS non-conservation (addendum 9 item 4). The 1 MeV tolerance never changed, and the
     failing counts are kept.
   - Established: ν ∥ +z on 822,359 complete non-DIS H events (max 1.3e-6 GeV). C12 inherits it by jobcard identity
     (MP3-C C0). C12 and DIS are unmeasured.
   - The contract's per-event assertion is recorded as not implementable for GiBUU, not as passed.
   - A report-only azimuthal-mean test over the DIS, missing-nucleon and C12 events is invited (0 node-h).
   - New caveat beside addendum 9 item 4: about 0.04% of non-DIS GiBUU-H events lack a low-KE final nucleon.
2. **NuWro three-muon events (52 CC): accepted.**
   - The frozen converter's muon (the last ±13 in `post`), with the extra muons excluded.
   - Before this record lands, a login-node check (0 node-h) reports, for the 52 events, the selected muon's sign and
     position, whether `post[0]` is μ⁻, the muon energies, and their in-grid rate share.
   - If the selected muon is not the primary, a KNOWN_ISSUES row (LOW) records it for the frozen NuWro product. No
     re-run while the share is ≤ 1e-4.
3. **GENIE atomic-electron targets:** as R13.
4. **Job 60101976: no re-run.**
   - It produced only a failure. Its finding (R13) was reproduced under the immutable `code-v2` and `code-v3`, and
     nothing reads its output.
   - `S2-IMPLEMENTATION.md` is corrected:
     - the wrapper hashed `0c92db3b…`; which version the interpreter read is unrecorded;
     - the claim "only the GiBUU reader changed" is shown by a diff or withdrawn;
     - the non-existent `harm_a.failed-60101976` receipt is not cited.
   - Immutable, read-only snapshots are standing practice for every remaining MP-2 job.

## The iteration cap [Joseph]

- n_estimators = 3000 stays as frozen.
- Every fit records validation logloss at 500, 1000, 2000, 2500, 2800 and 3000 trees.
- If V1's best iteration is ≥ 2800, V1 is reported "at the frozen capacity", with a descriptive V1 at 10000 trees
  beside it.
- Raising the cap for all models (about +2.5 node-h) is Joseph's methods call. It is not made here.

## Grant

- **The S2+S3 sub-budget is ≤ 8.5 CPU node-h** (0.28 spent), within the phase-1 ceiling of 35. It replaces addendum 8's
  "about 2–3.5".
- **Tranche A, ≤ 3.5: granted on this record, for the 200 F_primary models and the gate *computations*.** It runs as
  4 jobs of 1 node each, on QOS regular, `--time` ≤ 1:30. Before submission:
  1. The code that implements R10, R7, R13, R5b and R6's s assertion, and the logloss checkpoints, lands in a new
     read-only snapshot. Its sha256 list is committed or hashed in a PR.
  2. The R12 and D2 login-node counts are reported.
  3. The production `--out` is not `fit_probe/`.
  4. The `S2-IMPLEMENTATION.md` corrections of D4 and R13 are committed.
- **Gate verdicts are held for Joseph** (see "The frozen V2 and V3 thresholds"). The jobs may compute and store every
  gate statistic, p-value and pull. No V2 or V3 pass/fail verdict is computed, read or reported until one of two
  things is committed:
  - Joseph's ruling on the thresholds;
  - his choice to keep the frozen ones.

  No one, including the session and the director, reads the V2 or V3 statistics before then. A threshold change is
  meaningful only before the statistics are seen. V1 and V4 are not affected and are reported as soon as they are
  computed.
- **The iteration cap.** The models train at the frozen n_estimators = 3000. Raising it is Joseph's call, and the
  director does not make it unasked. If Joseph raises it before tranche A is submitted, that ruling governs.
- **Tranche B, ≤ 2.3 (F_fallback):** released only after a reported F_primary failure for that G.
- **Tranche C, ≤ 2.4 (S3):** released only after the S2 gate report and the committed S3 reading carried from R2.
- **Stop rule.** Stop and report if any job runs beyond 1.25× its projected wall time, or if tranche A would exceed
  3.5.
- **Standing rules.** The binding's ledger, storage and order rules (§3) apply. Phase 1 would stand at ≤ 16.1 of 35.

## Records

- **The maintenance window.** The S2 jobs ran on 2026-10-22, inside the announced `maintenance_20261021` window
  (10-21 06:00 to 10-27 23:00 PDT). The session records Perlmutter's actual return time with its source, so that
  addendum 8's "after the maintenance window" is evidenced.
- **The probe.** It ran 4 models where 2 were announced, within the stated ≤ 0.1 node-h (0.098). Recorded, no action.