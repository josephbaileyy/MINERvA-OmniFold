# Review disposition: generator-reweighting diagnosis (1 cycle; closed)

**Review:** one fresh, read-only, independent reviewer, a Claude subagent with no part in the analysis, on the
detached commit `c4dca4ca`.
- **What it did:** it wrote nothing in the repository and contacted no cluster. It re-ran `gd_analyze.py` and one
  GBDT unit into a scratch directory, and computed its own extra reductions.
- **Verdict:** **ACCEPT WITH CHANGES.** In its words: "The numbers are right and reproduce exactly, and the code
  implements the plan's definitions. But four headline claims go further than the evidence, and several plan
  departures are not disclosed."
- **Budget:** the plan allows one cycle, so the review is closed. Every finding is dispositioned below. No new
  training was needed.

| # | finding (severity) | disposition |
|---|---|---|
| 1 | "Not an input omission" is unsupported at step 2: PET's truth step lacks true E_avail and q3, which the GBDT gets (BLOCKING) | **Corrected.** §0 item 5 now says the omission is ruled out at step 1, where PET's reco inputs are a superset of the GBDT's, and is **not** ruled out at step 2, where it is untested. §3 names the `*_truthglobals` arms as a hypothesis. |
| 2 | "Mainly … hadronic direction" generalizes NuWro; on GiBUU the largest shortfall is in reco muon p_T (BLOCKING) | **Corrected.** "Mainly" is removed. §0 item 2 gives the reco-marginal gaps per generator: on NuWro E_avail 0.10–0.13 against muon 0.03–0.08; on GiBUU muon p_T 0.23–0.27, then E_avail 0.13–0.14. |
| 3 | Undisclosed departures: GBDT Q3 decomposition, all 32 units refit, the GBDT ≤ 1 core-h sub-cap, earlier iteration files not digest-checked (BLOCKING) | **Disclosed** in §1, departures 1–4. |
| 4 | T3c's "of the gap" treats non-additive, differently normalized R values as shares; the accepted / missed split is the right one (SHOULD-FIX) | **Repaired with the owner's own reductions.** T3c is now the reconstruction-status split. T3e gives the non-reconstructed R by iteration. §0 states the two deficits separately and says they are not additive. |
| 5 | The weight-agreement claim uses the slope alone; r contradicts "as strongly" (SHOULD-FIX) | **Corrected.** r is reported in T3. §0 item 6: equal or larger slope, lower r, so more unrelated variance. |
| 6 | "More iterations would not close it" extrapolates beyond K (SHOULD-FIX) | **Corrected.** §0 item 4 is restricted to k ≤ K, with the mechanism (T3e). k > K is untested. |
| 7 | `recovery_raw` was used where the scorer's rule makes R undefined (NuWro′ p_∥, its 3D cells and reco p_∥); the 3D ranges came from undefined cells (SHOULD-FIX) | **Repaired.** Every reported R outside E_avail now applies the rule (`rec_def`). The undefined cells print as undefined, with injected/floor ratios. The 3D ranges are restated from NuWro and GiBUU only, noting their 1.2× floor. |
| 8 | Planned outputs not reported: the orthogonal residual, per-region m, per-bin residuals, r (SHOULD-FIX) | **Added:** T1 (orth), T1b (per bin), T2 (per-region m and moves-away counts), T3 (r). |
| 9 | `gd_gbdt.py` doubled the CPU cost: `getrusage` already counts all threads (SHOULD-FIX) | **Fixed** in code and in §1. The real total is about 1.1 CPU core-h. |
| 10 | "Deleted locally afterwards" was false at review time (SHOULD-FIX) | **Corrected and made true.** The data were retained for the review and deleted after it, before this commit. |
| 11 | §3's "PET's step 1 is level" holds only on the dev tilt; D5 is already in the frozen rules (E6, B1); "should include" is a recommendation (SHOULD-FIX) | **Replaced** with the reviewer's wording. Weighting generator cases is stated as an owner decision. |
| 12 | The candidate causes ignored the study's contrasts: the 20× step-1 size difference with equal closures disfavors capacity; reco E_avail is given as a scalar; the 40 % figure (SHOULD-FIX) | **Corrected.** Capacity alone is disfavored; truncation is weak for the E_avail marginal; the training budget and optimization remain open. The 40 % figure is removed. |
| N | Notes: oracle detector-level ceiling; deficit present at k = 1; the GBDT also moves away at low acceptance on NuWro (6/8); "is a miss-rule effect" rests on two draws; "condition already holds"; the w_truth weighting; the `02f581a1` MANIFEST claim; no ledger row; reductions run several times | **All applied:** the ceiling is in T3 (0.92–0.93; the GBDT reaches it); k = 1 is in §0 item 2; the counts are in §0 and T2; "consistent with" and "the analogous study-scale difference" are used; departures 7 and 9; the run count is in §1. The **ledger row VL171** (the next dense id) is appended with this commit. |

**The reviewer's own extra reductions** (their split, on 64 PET runs and 24 refit GBDT units) agreed with the
owner's T3c, which was computed independently afterwards in `gd_analyze.py`:
- accepted rows after step 2: PET 0.44–0.57, GBDT 0.56–0.62;
- missed rows: PET −0.05 to 0.30, GBDT 0.24–0.44;
- oracle on missed rows: 0.92–0.93.

They are not used as a source. Every table is printed from the committed results.

**Limits the reviewer could not verify:**
- whether the plan was pushed before any reduction ran;
- the integrity of the earlier iteration files;
- the CFS receipt and the volume read;
- the 35 s aborted launch;
- Joseph's quote;
- design B's definition;
- data-scale behaviour.
