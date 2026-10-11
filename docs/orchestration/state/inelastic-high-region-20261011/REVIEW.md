# Review and correction pass: high-E_avail / high-W inelastic investigation

**Object reviewed:** commit `f0352ea4`, frozen, in a detached worktree.

**Reviewer:** one fresh, read-only Claude subagent of the same model family, given no access to the owner's
reasoning. Independence is limited to a fresh context, so this is **not** independent domain validation.

**Rounds:** one review and one focused correction pass, as authorized. There was no second review round.

**Reviewer budget:** 7.30 core-s (`REV-1`…`REV-4`), merged into `logs/budget_ledger.jsonl`. The reviewer's logs and
its independent scripts are in [`review/`](review/); the scripts do not import the owner's code. The review worktree's
`git status` was empty afterwards.

The text below is the owner's restatement of the reviewer's report, with each finding's disposition.

**Overall.** The reviewer found **no blocker** and **upheld INCONCLUSIVE**. GENIE + MEC's |ρ_C − 1| = 0.0665 exceeds
S_C ≤ 0.040 under every definition of the shift, so NO-GO is not reached. GO fails on magnitude by more than 2×.

**Reproduced independently:**
- R_total, R_C, ρ_C, R_M and ρ_M for all five predictions;
- the overflow split, the shape-normalized differences and the S20 fractions (0.495 / 0.060 / 0.764);
- the GENIE CV decomposition of C and M (both orders);
- the ±4% recoil shift (+0.0366 / −0.0376), the jitter floor and the estimator-R versus production difference;
- the per-W table and every emulation contrast.

All agree to ≲ 10⁻³. The reviewer also confirmed:
- **S20 bound:** valid, and using the proton mass instead changes 0 of the 38,220 cells.
- **Decomposition code:** correct.
- **§5.1 physics:** checks.
- **Frozen plan:** PLAN §§1–7 unchanged.
- **Budget:** consistent, with no forbidden action.

**Literature.** The reviewer opened and confirmed Tena-Vidal Tables III and VI, NOMAD Table 3, MINOS Table III and the
Lozano selection and quotes.

## Findings and dispositions

| # | Severity | Finding | Disposition |
|---|---|---|---|
| 1 | MAJOR | §1 placed the residual in the muon and transfer factors. That is false for NuWro, where partition (+0.017) exceeds the net (+0.006). For GENIE CV partition (27%) exceeds transfer (13%). §5.2 also quoted Tune v1's +0.006 as a complete-support value. | **Fixed.** §1 and §5.2 item 1 now say no single factor holds two thirds for any G. The muon step is the largest common component, partition is comparable (GENIE CV) or larger than the net (NuWro), and the per-G shares are given. The CATALOG summary is corrected to match. |
| 2 | MAJOR | The framing leaned toward NO-GO: the title, "fails narrowly", and a post-hoc normalization argument about MEC placed inside the rule outcome. | **Fixed.** The title is now "INCONCLUSIVE under the frozen rule; GO not reached". "Narrowly" is removed (stated 1.7×). The MEC observation moved to a separate block labelled post hoc, outside the rule. Recommendation 1 is marked as a recommendation, not the rule outcome. |
| 3 | MAJOR | "Where the real discrepancy lies" over-states M's robustness, which was tested against one coherent ±4% scale only. "Sits in the transfer step" holds by construction for W-only regions. | **Fixed.** The wording is now "the largest normalization-independent feature, robust to the one coherent response scale tested". The untested species-dependent response and prior leakage are stated. The by-construction point is tagged [D]. Tune v1's overshoot is now restricted to 1.4–1.8 GeV. |
| 4 | MINOR | The p_T endpoints quoted paper/Tune v1 ratios as ρ. | **Fixed.** ρ is 0.74 (0.84 at 0.07–0.15) → 1.10, and ρ(p_T > 0.85) = 1.07, with paper/Tune v1 = 1.195 kept distinct. Test 3 is corrected. |
| 5 | MINOR | The GiBUU deficit was misworded. | **Fixed.** The data exceed GiBUU by 29% and 78%; GiBUU is 22% and 44% below. |
| 6 | MINOR | "Within NOMAD's 5% at 6.5 GeV" is false (−5.9%, 1.2σ). MINOS at 5.9 GeV is 1.4% on the other side. | **Fixed.** The text now says the two data sets bracket GENIE there. |
| 7 | MINOR | S_C and B_C were not computed exactly as PLAN §6 words them. | **Fixed.** S_C = 0.040 (largest linear shift over G) and B_C = 0.031 (s5n + s5c aggregates), with the verdict shown to be invariant under the pre-review values. |
| 8 | MINOR | The order-agreement and MC-spread claims were over-general. | **Fixed.** The text now gives ≤ 0.0045 for the complete-support predictions and Tune v1, and 0.022 / 0.0056 for GiBUU. |
| 9 | MINOR | The plan's GiBUU-on-S20 decomposition was computed but not reported. | **Fixed.** S20 ∩ C rows for all five predictions are added. The full-domain GiBUU row is labelled support-contaminated. S20 partition steps (+0.030 to +0.045) are reported in §5.2. |
| 10 | MINOR | "Sufficient in size [M]" for response hides that one coherent shift cannot reconcile transfer steps that differ by 0.062 across G. | **Fixed.** The claim is retagged [D] as "matches in size", with the non-reconciliation stated. |
| 11 | MINOR | The tests were called "frozen" although written after the data. Test 1 used an untied "+0.04" threshold and pre-declared NO-GO. | **Fixed.** The section is retitled "proposed, written after the data". Thresholds are tied to the tabulated per-G values, a new frozen rule is required, and pre-declared verdicts are removed from §7 and §8 V1. |
| 12 | MINOR | The emulation caveats were thin in §1 (Rein–Sehgal vs Berger–Sehgal, S_RES's reference model, M_A^RES). The opposite NRB direction preferred by Lozano was not addressed. | **Fixed.** The caveats are in §1, §6.1 and §6.5, and the emulation is stated as unable to falsify the tune. A Lozano sign comparison is added to §6.4. |
| 13 | MINOR | The W2B rrzero/rr1 and four s5p digests were not enforced. The amendments' ordering is not git-evidenced. | **Fixed.** All 14 inputs are pinned (W2B manifests; the frozen estimator-R central `fb5cc679…`; jitters recorded on first read) and verified (`COR-verify`, 1.5 core-s). The single-commit limitation is stated in §10. |
| 14 | NIT | (q3, W) do not fix ω "up to m_μ²"; only the one-sided bound holds. | **Fixed** (§5.1). |
| 15 | NIT | Mixed ln and linear values; the Ruterbories condition was omitted; S_DIS 1.062 versus 1.06. | **Fixed.** Linear values are used in §1 (−2.7% / +9.4%), p_∥ > 6 GeV/c is added, and the 1.062213 code value is labelled agent-read next to Table VI's 1.06 ± 0.01. |

## Not verified by the reviewer, still open

- GiBUU's "about 30% low", which is read from a figure.
- The inheritance of inelastic parameters by AR23/AR25/N24/G24.
- The Bodek–Yang–Xu +2.7%.
- The AGKY and G24 claims.
- `ParticleResponseDefaults.h` values.
- The GENIE neutrino direction in the gst files.
- The content of the s5n and s5c receipts beyond the owner's aggregation.
- The R5 event-level code, which the reviewer did not rerun.

These remain marked *(agent-read)* or as owner-only in the memo.

## Budget after correction

Ledger total **1,100.9 / 7,200 core-s**:
- owner reductions, including the 900 core-s crashed run: 1,092.1;
- reviewer: 7.3;
- correction pass: 1.5.
