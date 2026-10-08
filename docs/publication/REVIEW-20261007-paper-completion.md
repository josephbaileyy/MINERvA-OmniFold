# PRD article: paper-completion pass and its independent review (2026-10-07)

**CITABLE FOR:** what this pass changed in the article and why, the independent reviewer's verdicts and findings,
each finding's disposition, the exact versions built, and the scientific decision this pass leaves for Joseph.
This is the publication lane's checked restatement, not a verbatim transcript.
**NOT CITABLE FOR:** any physics result (the routed records remain the authority), coauthor or journal approval, or
s5p's `publication_readiness`, which stays **NOT READY** by its own rule. This article's readiness is assessed
separately (DECISION-20261006 item 1).

| | |
|---|---|
| scope | a bounded paper pass: the approved AI disclosure and author metadata, scientific defensibility of the conditional rejections, and presentation. No compute, no gate change, no campaign reopened. |
| owner | the publication lane (Claude Opus 5.5), worktree `MINERvA-OmniFold-prd-paper-20261007`, branch `docs/prd-paper-completion-20261007` from `origin/main` `5f4ec13a` |
| reviewer | one fresh, read-only Opus 5.5 agent with no authoring history, in the detached worktree `MINERvA-OmniFold-prd-review-20261007`, left clean (`git status --short` empty after both cycles). An Astra-class reviewer (CAMPAIGN-REVIEW §5) was not available in this session. |
| budget | at most two review/repair cycles; both were used. Further review needs a named reason. |

## 1. Scientific findings of this pass (owner, before review)

| id | finding | evidence | change |
|---|---|---|---|
| S1 | The article described the sub-fine-grid variants as "±2 times an estimate of the residual" and their robustness check as "three times their estimate". The contract defines κ·δ_M1, with δ_M1 the **last refinement step**, κ = 2 the **central** extrapolated residual and κ = 3 its upper end. The old wording overstated the margin. | amendment 7 `claims.rejection`, `calibration.m1_shift`; `state/s5p/stage3/m1/*.json` | Described as the contract defines it; the κ = 3 check is labelled report-only; "how far beyond that the decisions would hold has not been evaluated". |
| S2 | The ±4% section said the observed statistics "remain far above their null distributions". This is not true for NuWro shape (Gaussian proxy 2.6–2.8 null SD; k 1 → 3). | W2B report §5 | Replaced by the counts: nine tests keep k = 0, NuWro shape goes from k = 1 to 3. |
| S3 | The response section inferred from the published muon-kinematics comparison that "the condition bears chiefly on the shape information along the hadronic axes". Within this analysis, the matched (p_T, p∥) projection does **not** reject GENIE 2.12.10 CV (p = 0.483 total, 0.629 shape); only its (E_avail, W) projection does. | W1-RECORD §1 (independently reproduced; the GENIE CV observation is post hoc and descriptive) | The published comparison is described as partial evidence and not a test of these hypotheses. The GENIE CV observation is stated with its post-hoc status: the information that rejects it involves the hadronic axes. |
| S4 | What the ±4% establishes and leaves untested was incomplete. | PACKET §5.4 and W2 section; W2B §1, §7; LITERATURE §4; Aliaga abstract (re-fetched from arXiv 2026-10-07) | Stated: a single coherent data-side scale at one magnitude removes no rejection. Untested: (a) the null response, (b) species, energy or resolution effects, or a response difference applied before calibration, (c) larger variations. Also stated: the 4% source covers test-beam p, π and e at 0.35–2.0 GeV/c, with neutrons outside; the low-recoil measurement's hadronic-energy uncertainty rises to 10% at 0.9 < q3 < 1.2 GeV. |
| S5 | The conditions mixed numerical, calibration and physical-model issues. | amendment 7 conditions; RECORD-20261005 §4 ("does not establish the calibration's adequacy") | Grouped as numerical convergence, calibration validity and physical-model adequacy. |
| S6 | A LaTeX comment swallowed "An independent recomputation of every" on main, so the PDF read "reached. p value and decision from …". | `pdftotext` of the main build | Fixed. |

## 2. Review cycle 1 (target `352f156a`): READY WITH CHANGES, 2 blocking, 9 editorial

| id | finding | disposition (`dc19ce17`, `2926e39e`) |
|---|---|---|
| B1 | The conclusions called the ±4% "not … a complete response uncertainty", implying it is a partial one. | Reworded: "applied to the data unfold only, removes no rejection; it is not an uncertainty estimate, and the null distributions were not varied with it." |
| B2 | 0.50–0.86 is **last step / whole coarse-to-fine change** in L2, not step-to-step. So in that norm the steps are not shown to shrink. The 0.45–0.76 rate comes from one sentence of the admission review, computed with a proxy metric (22 pilot products or diagonal), and how the ratio was formed is not recorded. | **Confirmed** by the owner (`campaign-state.json` m1 row; `s5p_prefreeze.py:50`; REVIEW-20260927-s5p-admission-confirmation item 4). Reworded with the reviewer's text, plus the governing frozen rule: amendment 8 `M1_within_fine_cell_residual` requires that the condition be stated as **"unmeasured, potentially material"** with the numbers when the shift is not small, and the article now says so. 0.45–0.76 is presented as the frozen design's proxy-metric assumption; its origin is in the `values_inference.tex` comments. |
| E1 | "could move each statistic in either direction" conflated the observed statistic with the null. | Separated; the net effect on each p is unmeasured. |
| E2 | "Its two rejections therefore rest on the hadronic axes" built a conclusion on a post-hoc observation. | "the information that rejects it involves the hadronic axes". |
| E3 | The condensing dropped "independently reviewed", "required … 16" and "self-validated". | Restored (DECISION-20261005 §5 disclosures 2 and 5). |
| E4 | "hybrid null" was undefined, and the carry-over condition mixed shape and unfolded-result terms. | Defined at H0(G). The condition is stated in unfolded-result terms along δ_M1. |
| E5 | κ = 3 was not said to be report-only. | Added. |
| E6 | "at most about 0.05 null SD" understated the half-simulation shift (prefreeze 0.068). | "at most about 0.07". |
| E7 | Optional: the committed M1 sizes. | Added: 0.55–2.0 (claim) and 1.07–3.6 (robust) null SD (amendment 7 `prefreeze_measurements`). |
| E8 | The abstract dropped "at useful precision". | Restored. |
| E9 | `@online` is unsupported by apsrev4-2 (no URL printed); the cited W2B report contradicted itself (§7 PENDING). | The four new references are `@misc` with printed URLs (`xurl`). W2B §7 corrected (`2926e39e`) and the citation pinned to it. **Residual:** the three PET `@online` entries in the note-owned `technote.bib` still print without a locator; this goes to the note owners. |

## 3. Review cycle 2 (target `dc19ce17`): READY WITH CHANGES; all cycle-1 items resolved, no new scientific defect

| id | finding | disposition |
|---|---|---|
| N1 | The `JointTestRecoil2026` URL pins `2926e39e`, which is not public until this branch merges. | Comment updated (`94b0042a`). The PR merges with a merge commit, which preserves the SHA; the URL is re-checked after the merge (recorded in the PR and the package manifest). |

## 4. Presentation changes (no claim strengthened; the reviewer confirmed this)

- **Abstract:** rebuilt around the question, the method, the conditional result and the principal limitation (no response band; an unconverged fine-grid null). It dropped "and its uncertainty scale" for the 2D reproduction together with that clause's qualifier, which is a narrowing; the qualifier stays in the introduction, the 2D section and the conclusions.
- **Introduction:** states the contribution, its limits and a roadmap.
- **Lost pseudo-experiments:** condensed with all five required disclosures kept (DECISION-20261005 §5). The procedure is routed to pinned repository records: four `@misc` references to the contract and result, the recovery, W1 and W2.
- **AI-use disclosure:** the approved text, verbatim, in the Acknowledgments, with a pointer from Sec. III.
- **Author block:** unchanged, as approved. ORCIDs and funding were not supplied.
- **Layout:** `\raggedbottom` removes a stretched page-1 gap in reprint mode.

## 5. Unresolved scientific decision (for Joseph; nothing was run)

**The sub-fine-grid residual is, under the contract's own frozen rule, "unmeasured, potentially material".**
- The rejections are conditional on the frozen κ = 2 claim rule, whose basis is an assumed geometric convergence rate in a proxy metric.
- Robustness was checked only at κ = 3, where the closest recovered null draw of GENIE + MEC shape lies 4.6 below T_obs = 868.6. The claim-variant margin is 64.7, so the tolerance beyond κ = 3 is unknown for that test.
- The article now says all of this.

The smallest decision is one of:
- **(a) Accept the article as conditional** (recommended for submission; the text now states the limitation as the contract requires).
- **(b) Authorize a report-only κ-breakdown:** the smallest κ at which each decision would change, computed from the released sufficient inputs. This is login-scale (seconds), changes no frozen decision, and would let the article quote the tolerance. It is new scientific computation, so it needs Joseph's authorization.

Neither changes the calorimetric-response condition, which remains unbounded by any validated uncertainty.

> **Update 2026-10-08:** Joseph chose **(b)** on 2026-10-07. Result: `publication/kappa/RECORD-20261008-kappa-breakdown.md`
> (spec frozen at `b75af4f4`; independently reproduced).
> - All ten decisions remain determinate rejections for κ ≤ 5.2547 (frozen reading) or 5.1688 (with the recovered
>   draws).
> - The first loss is GENIE + MEC shape.
> - GiBUU shape survives to κ = 12, and Tune v1 does not depend on κ.
> - The result measures sensitivity along δ_M1 only; no frozen decision changes.
> - **Article: applied 2026-10-08** with Joseph's shorter wording (scoped to the frozen ensembles; see that record's
>   §5). The abstract is unchanged.

## 6. Versions

| object | identity |
|---|---|
| article sources | branch `docs/prd-paper-completion-20261007` head `94b0042a` (`main_paper.tex`, `paper_body.tex`, `values.tex`, `values_inference.tex`, `publication.bib`, `technote.bib`, `figures/`) |
| local build of that head | `build_all.sh` rc 0, containment `RESULT :: PASS … tree=clean`; note 123 pp, primer 9 pp, paper 10 pp. `main_paper.pdf` sha256 `ce9ecf5b2c1b53ec7b02694b7acbad39b4f86a04da54678c056239a09ca53b7e` (TeX Live 2024; the digest includes the build date). One `\pubhold` (the deposit identifier); 0 undefined references; one accepted 0.7 pt overfull (Table I). |
| release candidate | RC4 `46f801bf…` is unchanged. The release reproduces the inference, not article text. The new article numbers are contract values (0.45–0.76; 0.55–2.0 / 1.07–3.6 null SD), literature values (4%, 0.35–2.0 GeV/c, 10%) and W1 p-values that RC4 already recomputes. The data-availability section now lists the fine-grid convergence rates among the numbers not recomputable from the release. |
