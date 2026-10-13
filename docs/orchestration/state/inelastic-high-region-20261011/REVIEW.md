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

## Close-out review (2026-10-11)

**Object reviewed:** commit `6f48a9e8`, the close-out's corrections and new §11, in a detached worktree.

**Reviewer:** one fresh, read-only Claude subagent of the same model family. It had no access to the owner's
reasoning and was given a targeted checklist of the eight close-out items Joseph set. Independence is limited to a
fresh context, so this is **not** independent domain validation, and it is not the MINERvA-response or
nuclear-theory review the memo recommends (§11.7).

**Rounds:** one review and one focused correction pass, then stop.

**Budget:** the reviewer ran only file reads, `git diff`, PDF text extraction and a JSON read, so no reduction was
needed. That is not metered by `budget.py` and adds nothing to the ledger. The review worktree's `git status` was
empty afterwards, and the worktree was removed.

**Overall.** No blocker.

**Reviewer-checked:**
- **Frozen files:** PLAN.md, `results/`, `code/` and `logs/` are unchanged.
- **Numbers:** every number token of the reviewed memo survives, except the superseded version string "3.06" in V2.
- **Predecessor memo:** SHA-256 `4f3da639…`.

**Reviewer re-opened:**
- arXiv:2106.16210 §III and Ref. 36;
- arXiv:2609.22662v2, Eq. (1) and the 5 and 30 MeV thresholds;
- `R1_rate_shape.json` (S20: 0.0598 of C) and VL161;
- the cited lines in `CVUniverse.h`, PACKET :277 / :321, `app_statmethods.tex:385`, `runEventLoopOmniFold.cpp` and
  `unfold_nd_omnifold_unbinned.py`;
- the W2B §6 costs.

Items 1, 2, 3, 4, 6 and 8 were met. Items 5 and 7 had the defects below.

| # | Severity | Finding | Disposition |
|---|---|---|---|
| C1 | MAJOR | §6.2 de-excitation row wrong-signed against the table's own "step not occurring" reference: emitted γ and evaporated protons add to A | **Fixed.** Row now +E_γ + ΣT_p(evap), neutrons 0, ≥ 0, with the reference stated |
| C2 | MINOR | ε ≈ 8 MeV is the mean binding, not the separation energy (¹²C: S_p ≈ 16, S_n ≈ 18.7, pn ≈ 27 MeV); "+0.12 / +0.13" are about 0.01–0.02 GeV high | **Fixed.** ε and ε₂ are relabelled. Values are now +0.11 (pp absorption), +0.12 (π⁺n → π⁰p) and T_n < 0.11; no sign changed |
| C3 | MAJOR | §11.3 closure would fail by construction: §5.3 already records that the estimator does not follow A-shape departures; the floor omitted the known bias | **Fixed.** Expected nominal non-closure is stated (s5n C4/C5). Closure is judged against the recorded bias, the floor includes it, and hiding is claimable only above the floor. The Failure row is restated accordingly |
| C4 | MAJOR | Header and CATALOG cited a close-out review not yet in REVIEW.md | **Fixed** by this section, landing in the same commit as the correction pass |
| C5 | MAJOR | §1 item 3 (response study next) contradicted §11.7 (reviews, then V2, then response study) | **Fixed.** §1 item 3 now states the §11.7 order |
| C6 | MAJOR | §7 rule 2 still screened G18_02a_02_11b while V2 now proposes G18_10a_02_11b / AR23_20i; CATALOG said "interpretation only" | **Fixed.** Rule 2 now covers both kinds of configuration, states the nuclear-model confound and the unmeasured spline cost for G18_02a. The proposal change is disclosed in the REPORT header and CATALOG |
| C7 | MINOR | §11.4 outcomes not exhaustive | **Fixed.** Catch-all "Inconclusive (default)" row added |
| C8 | MINOR | §11 omitted the truth fields and `Fr*` weights the closure needs | **Fixed.** Added "Outputs the new pass must also write" to §11.1 |
| C9 | MINOR | §6.3 generalized one coherent scale to explanation (iii) as a whole | **Fixed.** Now reads "the tested coherent scale moves … by only ±0.01 / ±0.002; species family open" |
| C10 | MINOR | LIT-REPORT candidate table still had unqualified rate invariance | **Fixed.** Qualified as "factorized post-vertex kernel at fixed primary dynamics" |
| C11 | MINOR | Species-branch listing had no receipt; `Systematics.h` cited as a bare untracked filename | **Fixed.** Cites the committed `feature_inventory.json` (`e39774e7`, owner-checked). `Systematics.h` is given by full cluster path, with SHA-256 `1bdfa4f0…` and its untracked status (owner-checked) |
| C12 | NIT | "135–140 MeV" should be exactly 135 MeV per π±; "data-side" ambiguity; 1.898/3 = 0.633 gives ≈ 9.4, not 9; stray NuWro line | **Fixed.** 135 MeV, with kaons noted; "data-side" is marked as W2B usage at each site; ≈ 6–9.5 node-h; the NuWro line moved under item 4 |

**Not changed, by design.** The figure legend's "data side" is produced by the frozen `code/make_figure.py`. The
REPORT now defines that phrase in W2B's sense (§9), and the figure is not regenerated.

**Still open, as in the first review:** the *(agent-read)* items, plus every §11 inventory item not marked
owner-checked. The latter rest on the read-only inventory agents' branch listings and greps.

### Close-out record (per `CAMPAIGN-REVIEW-20260929.md` §1 and §6.7)

**Setup.**
- **Decision answered:** Joseph's close-out request. The memo's interpretation is corrected and a no-run feasibility
  specification added; the verdict stays INCONCLUSIVE.
- **Terminal condition:** one targeted review and one correction pass, then stop. Both ran.
- **Owner:** Claude Opus 5.5 (`claude-opus-5-5`), session `de68ac2a-c125-408f-ba1c-8f2380a0f64b`.
- **Reviewer:** one fresh read-only subagent of the same model.
  - The campaign review recommends an Astra High reviewer for consequential review. None was available in this
    session.
  - This review is therefore limited to fresh-context independence, as stated above.
- **Delegated read-only inventory:** two agents of the same model (response inputs; GENIE v3 predictions). Their key
  citations were re-opened by the owner where marked owner-checked.

**Commits.**
- **Input:** `3e9e5188`.
- **Outputs:** `6f48a9e8` (pre-review) and `db87bf78` (correction pass), plus the commit carrying this record.
- **Remote:** checked at `d81f532b`; none of the study's inputs differ there.

**Cost.**
- **Compute:** zero metered reductions. The ledger is unchanged at 1,100.9 / 7,200 core-s. Login-node branch and
  spline listings took seconds and are not metered.
- **Inference cost:** unavailable.

**Findings.**
- **Accepted:** 12 (5 MAJOR, 6 MINOR, 1 NIT), all fixed.
- **Residual open items:** the *(agent-read)* literature items, and the §11 inventory entries not marked
  owner-checked. Neither reviewer the memo recommends (§11.7) has examined it.

## Second close-out pass (2026-10-12): documentation only, not reviewed

- **Decision answered:** Joseph's request to close the study with a corrected validation proposal. The verdict stays
  INCONCLUSIVE. The frozen rule, every number and every artifact are unchanged.
- **Terminal condition:** one documentation pass, one owner self-check, a local commit, then stop. By instruction
  there were **no review rounds and no additional agents**, so this pass has no independent review.
- **Owner:** Claude Opus 5.5 (`claude-opus-5-5`), same session as above.
- **Input:** `19010898`. Remote `main` checked at `f30370cd`. Since the study's base it changed AGENTS.md: the 5D
  "injected-W" closure injected nothing. That change is used in REPORT §8 and §11.3. None of the study's inputs
  changed.
- **Changes:**
  - REPORT §11.3–11.5: the s5n/s5c biases are no longer a closure allowance or floor; per-departure truth recovery
    comes first, then matched/mismatched response dependence; the span test is qualified; work not covered by the
    earlier costs is listed.
  - REPORT §8, §9, §11.6–11.7, and the header: follow from those changes.
  - `REVIEWER-BRIEF.md` (new).
  - CATALOG, MANIFEST overrides and MANIFEST updated.
- **Compute:** none. The ledger is unchanged at 1,100.9 / 7,200 core-s. The §11.5 cost arithmetic came from a local
  arithmetic snippet over W2B's recorded figures. It read no data and is not metered.
- **Residual:** the revised §11 and the brief are unreviewed. The brief is the instrument for the two reviews that
  REPORT §11.7 recommends.

