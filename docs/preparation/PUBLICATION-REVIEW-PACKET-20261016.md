# Publication review packet — 2026-10-16

**Preparation only; dependencies pending.** Joseph and Ben can scrutinize the declared conventions and disclosure now. Acceptance of the final uncertainty and its presentation needs the reviewed Stage C rollup, the playlist block and their reviewed combination, followed by Joseph's product and wording decisions. **Full scientific closeout is NOT ACHIEVED.** This packet neither certifies construction completion nor changes an article claim.

**Preparation source snapshot:** `f9ac098588fd4d67abfaca20f15c46d82060e02a`. **Integration refresh, 2026-10-17:** `00af221598eba621e15455522ab23f7bdc21d39c`, including PR #146. The director retains Stage F integration and the final combined product; Joseph retains adoption and outward acts. This packet supplements the owning Stage F documents. The resolved preparation gaps below are distinguished from the pending combined product and final integration. [CURRENT_WORK][current] is a routing view, not authority for additional work.

## What is already decided, and what remains draft

| Standing at the refreshed snapshot | Governing record and review consequence |
|---|---|
| **Approved endpoint:** construction under declared conventions; reproducible central estimator and matched uncertainty construction are the target. | [October 14 decision][endpoint] §2. D/E are deferred for this publication; absent independent production-size MC, a validated continuous nuisance generator and untouched validation evidence prevent full closeout. KI85 is not lifted. No population or simultaneous coverage, calibrated intervals or calibrated covariance-based generator significance follows from construction. |
| **Adopted central value:** LightGBM seed 42, `E_U`; exact-split retained as a cross-check. **Currently adopted covariance:** VL175. | [Central adoption][central] and [VL175 adoption][vl175]. Preserve the post-hoc learner choice and omitted learner dependence. The former seed mismatch is not closed merely by planning a matched statistical ensemble. VL175 does not adopt its Stage C successor. |
| **Approved construction choices:** three-stream bootstrap; null/unconfirmed `NormDISCC`; C07′ omission under the documented rule. | [Recipe ruling][recipe]; [Stage B diagnostics][diag] §6.2. The two links connecting POT counting to the constrained flux remain inferred. Recipe acceptance is not product adoption. |
| **Approved G2 disposition:** carry the unrepaired miss-row-weighting approximation. | [Exact October 15 ruling][g2] §2: tests in `MaRES_0` and `Flux:23`, each at seeds 42 and 43, resolved no effect above trainer seed noise; smaller effects are not excluded, and only two of the systematic universes were tested. Preserve the exact tested fraction from that ruling when final wording is drafted. |
| **Approved requirement for a playlist term; construction now exists, not adopted.** | [October 15 playlist ruling][plrule] requires a separate block after S5. [DESIGN][pldesign] and [REPORT][plreport] record construction and independent recomputation with a separate reader/code, plus the same-model caveat. Do not say “awaiting construction” or “no independent recomputation.” At the preparation snapshot the verifier's output/code files were routed only to scratch. PR #146 commits the six-file [recompute attachment][plrecompute] and its [SHA256SUMS][plchecksums], closing that attachment gap. This adds no S5 combination, adoption or coverage claim. |
| **Existing article approvals survive within their scope.** | [October 6 approvals][approvals]: specialist article, approved author details and AI disclosure; Fig. 2 descriptive only, without significance or response-mismatch closure. The October 14 ruling defers that closure's settings. Existing conditional joint tests remain separate from the measurement uncertainty; PET remains diagnostic/method-development only. Neither the old package readiness sentence nor a replay PASS certifies this narrower endpoint. |

The director's [CHECKLIST][checklist], [DRAFT-disclosures][disclosures] and [AGENDA][agenda] remain the owning documents. Their proposed sentences are **DRAFT**, not approved wording. The proposals below supplement them; they do not replace their dependency order or create another work register.

## Source-traceable gaps for the final review

Statuses below describe committed records at the refreshed snapshot, not current scheduler or remote-storage state.

| Gap / owning checklist items | Evidence available now | Exact missing evidence or decision Joseph and Ben need |
|---|---|---|
| **Stage C terminal construction** — F1–F5 | [Production DESIGN][production] §§7–8, 13–14; [production binding][binding]; [packing binding][packing] binds the revised submission package. Smoke and package-review evidence exists. | `stageC/production/REPORT.md` is absent at the input commit. Need terminal item dispositions, complete operand hashes, `results/s5/production_cov.npz`, `s5.json`, `uq_production_covariance.root`, and the fresh verifier's independent total recomputation from replica/universe vectors. Need actual control/MAT/vector-functional/symmetry/PSD checks and ensemble-precision diagnostics, not inferred success from the smoke test. Need the report's migration/member/exception records and CFS copy hash verification, including the ROOT rollup. No remote absence is inferred from local absence. |
| **Supported production driver** — F6 | [Binding][binding] §3.1 permits a pinned pilot copy and requires its own reviewed PR before adoption; [packing binding][packing] §4 preserves that condition. | Reviewed integration into `2d-unfolding/` on main, with its commit and identity/reproduction evidence. `2d-unfolding/driver_p1.py` is not tracked at this input commit. The tracked pilot copy alone does not satisfy this condition. |
| **Playlist block / combined product** — F7–F9 | [Playlist REPORT][plreport] records construction, frozen checks, recomputation and a CFS route for `playlist_term.npz`; `outputs/playlist_term.json` and the [recompute attachment][plrecompute] are committed. Checklist revision 2 closes F7 and records the constructed/recomputed block in F8, with addition to S5 remaining F9. Primary design is reference-free, uses double ratios and each period's MC response, keeps 1F in group A, and reports raw/reference alternatives only as sensitivities. | Director's S5-plus-playlist report/product and review: exact operands and durable hashes; common cells, `E_U` and S5 functional-map identity; combined symmetry/PSD and vector-based projections; budget with/without the term and comparison to VL175. REPORT §4 explicitly leaves this pending S5. Joseph must adopt the final product and construction choice; no final combined filename/digest is yet specified here. |
| **Disclosure and issue disposition** — F10, J3–J5, K3 | [Disclosures][disclosures] D1–D10; [production][production] §8; [KI85][issues] row 85; [playlist limits][plreport] §3. | Revision 2 with final numbers sourced to reviewed products and completed D10 text; evidence-specific dispositions for KI88/90–94, including actual checks in both publication consumers for KI90. S1 coverage remains untested; historical post-hoc rescoring does not test the new block. Joseph's wording and KI85 disposition remain required. |
| **Adoption and final integration** — J1–J4, R/K/B | [Stage F plan][plan] §4; [October 14 decision][endpoint]. | Joseph's review sequencing with Ben, final uncertainty adoption, claim/disclosure wording, then director-owned numerical integration, ledger/RUN_LOG/status/reference updates, supported replay, builds/synchronization and independent final claims-to-evidence review. This packet supplies none of those outcomes. |

**Limitations to carry into the review:** [production DESIGN][production] §8 distinguishes the background-only arm and interactions X02/X03 (reported, not added) from the total; C08 replaces the former seed-scan block and has limited seed support. Background/signal-miss overlap was not measured; laterals retain trainer noise; learner dependence is omitted. [Playlist DESIGN][pldesign] §§3–4 assumes exchangeable offsets from three groups, has few effective degrees of freedom, leaves possible regularization shrinkage uncorrected and does not subtract statistical/seed noise (including possible overlap). A small reference-scenario distance is an algebraic containment property, **not a coverage test**. Unknown cause and unknown “correct” period remain. Keep these alongside G2, null `NormDISCC`, inferred POT propagation, the unexplained flux-band difference and untested coverage; do not compress them into “validated uncertainties.”

## Affected presentation and replay surfaces

These are proposed integration targets for the director after adoption, not edits authorized by this packet.

| Surface | Review action / dependency |
|---|---|
| [Article body][body] `sec:repro2d`, `sec:uq2d`, `sec:conclusions`; [values.tex][values] | Reconcile current VL175/statistical-history wording with the adopted successor. Re-source budget, flux and covariance-dependent comparisons; preserve historical labels. The published-covariance distance uses the unchanged central value and published covariance, so a new uncertainty alone is not a reason for it to change. Shared-data cross-covariance is still missing. |
| Article Fig. 1, `paper_fig1_validation.pdf`, `fig:validation` | Rebuild its own band, uncertainty inset and caption from the adopted combined product; explicitly include the playlist block and preserve the correlated-band warning. Ratios and central curve must remain bound to `E_U`. |
| [Note systematics][systematics] `fig:uqbands`, `fig:bootstrap`, `fig:seedscan`, `sec:uq-combine`; [validation tables][validation] `tab:validation-questions`, `tab:closure-map`, `sec:coverage` | Review the uncertainty projections (`MEFHC_fig6_7_uncertainty_pt/pz`), statistical spread/correlation and seed figures, budget tables, integral and projection uncertainties. Replace or label old ensembles, rather than silently relabel their graphics. Validation tables must distinguish construction checks from coverage; no closure conclusion changes. Audit shared macros and primer summaries. |
| Article Figs. 2–4 and Table `tab:joint`; `values_inference.tex` | No new numerical dependency on the 2D rollup is established. Preserve descriptive higher-dimensional comparisons and the separate conditional joint-test interpretation; no new significance, localization, coverage or reportable uncertainty is implied. |
| [Claims map][claims] L1–L4, readiness passages; [package manifest][manifest] §§2, 4–5 | Reconcile old exact-split/interim pairing and readiness statements against October 11–15 decisions and the final receipts. Source passage order is not authority. Existing approvals do not certify an unreviewed successor. |
| [Release README][release], [article data availability][article], [note release appendix][releaseapp] | RC7's arrays retain the old exact-split Fig. 1; the article already discloses that mismatch. A later release revision needs updated `data/figs/fig_arrays.npz` and manifest, adopted covariance inputs/identities, `expected/values.tex`, plotting/export bindings, checksums and replay receipt. Keep inference inputs separate. No release inputs are changed here. |

**Replay coverage to show explicitly.** RC7 documents sufficient-input replay of the joint tests, recovery reading, W1, fine-grid ratios and its packaged figures. It does **not** reconstruct the new 2D uncertainty or establish coverage. `observed_jitter_p` is not checked by its verifier; the multiplier scan is separately recomputable, outside that verifier. Extraction needs archived calibration products; event processing needs the earlier AnaTuple production and generator samples. The separate checksum inventory/preservation record is not packaged event-level reproduction. Stage F therefore needs a new clean-checkout receipt at each claimed supported tier, with access limits, product hashes and recovery routes; a preserved path or old replay does not certify the new total.

## DRAFT wording and Ben-agenda additions

**DRAFT — endpoint language for consideration only, conditional on reviewed construction and Joseph's adoption:**

> We report a reproducible two-dimensional central value with a matched uncertainty construction under declared conventions. Full scientific closeout is not achieved: the construction has not been independently validated for population or simultaneous interval coverage, and it supplies no calibrated covariance-based generator significance. The independent-validation stages are deferred for this publication.

**DRAFT — playlist disclosure clause, to supplement D5 after adoption:**

> A separate uncertainty block represents an observed run-period inconsistency of unknown cause. Its reference-free double-ratio construction uses the periods' own simulated responses; it does not identify a correct period. The small number of groups, possible regularization shrinkage and retained statistical and training noise limit its interpretation. Containment of the observed differences by this construction is not evidence of coverage.

Final size, projection effects and construction details must come from the reviewed combined report. These sentences have not been inserted into any deliverable or approved by Joseph.

Proposed additions to the director's agenda, with a concrete outcome for each discussion:

1. **Now — scope:** ask whether the title, abstract and conclusions clearly separate 2D construction from conditional joint inference. Outcome: wording recommendations to Joseph, retaining full closeout NOT ACHIEVED and D/E deferred.
2. **Now — convention choices:** scrutinize G2's limited tested domain, POT inference, null `NormDISCC`, stream independence and omitted learner dependence. Outcome: explicit acceptance/disclosure recommendations or a named unresolved objection; no implied new study or collaboration contact.
3. **Now — playlist interpretation:** compare the reference-free construction with its reported sensitivities and discuss exchangeability, grouping, noise overlap and shrinkage, as the refreshed owning agenda item 12 now does. Outcome: recommendations on construction/disclosure, without claiming a known mechanism or coverage. Independent recomputation is recorded; review its scope and the now-committed [evidence attachment][plrecompute].
4. **After products — uncertainty acceptance:** inspect the S5 vector-to-matrix verification, final block inventory, ensemble precision, cell/functional identity and before/after budget. Outcome: a product-specific recommendation; Joseph alone adopts the exact combined bytes and wording.
5. **After integration — publication review:** examine one exact rebuilt PDF and matching replay/source receipts; retain the separation from Table `tab:joint`. Outcome: author corrections and a bounded list of blockers to the actual claims. Scheduling, sending and review sequencing are Joseph's acts.

**Remaining author inputs:** final product/wording adoption and KI85 disposition; Ben review timing; exact manuscript approval; funding/grant acknowledgments (an active hold in [main_paper.tex][article]), optional ORCIDs; deposit location/license/scope and identifier/access route; cover-letter history/referee details; separately authorized standalone push, contact, tag, submission and deposit. The [manifest][manifest] lists author details/AI disclosure as already approved: do not reopen those as missing approvals merely because its original numbered list survives.

## Reconciliation pending and local verification

PR #146 resolves the checklist and attachment findings below, without edits to the owning files in this integration. Their earlier forms refer to the preparation snapshot; the remaining claims and product dependencies retain their owning records.

- The October 16 CHECKLIST F2 predates the committed [packing binding][packing]; F7/F8 and agenda item 12 predate the [playlist REPORT][plreport]. Checklist revision 2 closes F2 and F7 and records construction/recomputation in F8; the refreshed agenda points to the committed attachment. Combined-product F9 and adoption remain pending. Recorded scheduler counts are dated observations, not live facts.
- The October 16 CHECKLIST F1 allowed named INCONCLUSIVE outcomes for reporting; revision 2 now follows [production DESIGN][production] §8: **every item analysis PASS** for S5, with FAIL or INCONCLUSIVE a stop for that line. A terminal report with an inconclusive item is not an adoptable rollup.
- The October 16 CHECKLIST B1 listed three PDFs; revision 2 now lists note, PET note, primer and paper, matching [AGENTS.md][agents]. This resolves the build-scope discrepancy; no build or standalone synchronization was run here.
- The verifier's scratch-only output/code attachment at the preparation snapshot is now committed in [recompute/][plrecompute], with [SHA256SUMS][plchecksums]. This preserves the existing recomputation and its same-model qualification; it does not verify the pending combined product.
- Claims-map/package historical readiness and RC7 figure assertions lag the later central adoption and current article. Their reconciliation is pending, not an authorization to change claims. Final combination and numerical Stage F integration remain with the director and Joseph.

Local checks: input HEAD and branch matched the contract; the initial worktree was clean. Relative source links were checked for existence; expected missing products above were distinguished from existing records. No scientific script, build, remote verification, scheduler query or inference delegation was run. These document checks make no independent scientific-verification claim.

[campaign]: ../orchestration/CAMPAIGN-REVIEW-20260929.md
[current]: ../CURRENT_WORK.md
[agents]: ../../AGENTS.md
[endpoint]: ../orchestration/DECISION-20261014-joseph-2d-endpoint-and-open-items.md
[central]: ../publication/DECISION-20261011-joseph-2d-central-lightgbm-seed42.md
[vl175]: ../publication/DECISION-20261012-joseph-adopt-2d-c04-repair.md
[recipe]: ../publication/DECISION-20261012-joseph-2d-closeout-recipe.md
[diag]: ../orchestration/state/2d-closeout/stageB/diagnostics/REPORT.md
[g2]: ../orchestration/DECISION-20261015-joseph-g2-carry.md
[plrule]: ../orchestration/DECISION-20261015-joseph-playlist-consistency-term.md
[pldesign]: ../orchestration/state/2d-closeout/playlist-term/DESIGN.md
[plreport]: ../orchestration/state/2d-closeout/playlist-term/REPORT.md
[plrecompute]: ../orchestration/state/2d-closeout/playlist-term/recompute/
[plchecksums]: ../orchestration/state/2d-closeout/playlist-term/recompute/SHA256SUMS
[approvals]: ../publication/DECISION-20261006-joseph-publication-approvals.md
[checklist]: ../orchestration/state/2d-closeout/stageF/CHECKLIST.md
[disclosures]: ../orchestration/state/2d-closeout/stageF/DRAFT-disclosures.md
[agenda]: ../orchestration/state/2d-closeout/stageF/AGENDA-ben-review.md
[production]: ../orchestration/state/2d-closeout/stageC/production/DESIGN.md
[binding]: ../orchestration/AUTHORIZATION-20261015-2d-closeout-stageC-production-binding.md
[packing]: ../orchestration/AUTHORIZATION-20261016-2d-closeout-stageC-packing-binding.md
[plan]: ../orchestration/PLAN-20261011-2d-closeout.md
[issues]: ../../KNOWN_ISSUES.md
[body]: ../analysis-note/paper_body.tex
[article]: ../analysis-note/main_paper.tex
[values]: ../analysis-note/values.tex
[systematics]: ../analysis-note/sec_systematics.tex
[validation]: ../analysis-note/sec_validation.tex
[releaseapp]: ../analysis-note/app_release.tex
[claims]: ../publication/CLAIMS-20261005-claim-to-evidence.md
[manifest]: ../publication/submission/PACKAGE-MANIFEST-20261006.md
[release]: ../publication/release/RC7-README.md
