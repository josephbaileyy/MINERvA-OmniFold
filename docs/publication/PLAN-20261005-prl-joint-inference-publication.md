# Plan for a five dimensional inference Letter and publication

**Date:** 2026-10-05. **Status:** proposed publication plan for review, not an authorization to execute it.

The closest plausible PRL route is a focused Letter about joint five-observable inference on MINERvA data, supported by the completed unfolding and benchmark studies. The existing short paper supplies its methods and central-value foundation; the final calibrated inference result would supply the new principal result. This route is conditional on that result surviving verification, the missing-seed resolution, and a scientific assessment of the declared response model.

This would be a complete paper within its approved scope. It would not constitute a completed five-dimensional cross-section measurement with a qualified total uncertainty product. If that complete measurement remains a prerequisite for publication, the schedule must wait for it; the manuscript work below cannot close that scientific gap.

This plan lists remaining publication work. Existing campaigns appear only as dependencies to consume or explicitly exclude. Their procedures, staffing, stopping rules, and budgets remain with their current owners. No training, cluster submission, adoption, public deposit, release tag, external message, or journal submission is authorized by writing this plan.

## 1. Decision, ownership and stopping conditions

**Decision to answer:** do the final available results support a scientifically defensible, sufficiently important PRL Letter, and can its exact claims be reproduced from a release suitable for external readers?

Joseph owns scientific scope and publication decisions. A designated manuscript owner prepares the text and release; the coauthors review the scientific interpretation. A fresh independent reviewer examines the fixed evidence and manuscript in a read-only, isolated checkout, preserving any reviewer requirements already imposed by the inference contract. Publication review does not replace the campaign's independent recomputation. No additional agents are appointed by this proposal.

Following the [campaign retrospective][campaign-review], use at most two focused publication review/repair cycles before reassessing the strategy. A material unresolved defect means hold, narrow the claims if scientifically legitimate, or propose a separately bounded investigation. It does not mean continue reviewing until somebody approves. Reviewer agreement is not independent evidence if all reviewers rely on the same original calculation.

The preparation effort ends with one of three written dispositions:

1. **Ready to request submission:** the scoped Letter passes every gate below, with an exact reviewable package and author approval.
2. **Sound result, insufficient PRL case:** prepare a suitable specialist-journal version after an explicit journal decision.
3. **Scientific hold:** the principal inference or retained measurement claim lacks adequate support. Record what is missing and stop the publication push.

Acceptance and publication remain later milestones, controlled in part by editors and referees.

## 2. Evidence snapshot and required waits

This plan uses committed evidence available at approximately 2026-10-05 21:26 UTC:

- Main: `0a988bc44f68c66f042420e391ac445f1fe1d630`.
- Independent recomputation branch: `02df81e64ba10c4d817fc66eb068af1d39ef23eb`.
- Two-dimensional coverage branch: `808628787980f990f6096f67dc15f84b669cb56a`.

These are an evidence snapshot, not a current scheduler observation. Refresh the governing records before execution; a development result or an unmerged report must not silently become an adopted result.

| Existing work or result | Must this Letter wait? | Required handoff; no duplicate campaign work |
|---|---|---|
| `s5p` primary inference production | Its terminal production record already exists; publication still waits for its scientific closeout. | Consume the owner's final recorded result and disposition. The terminal record currently transcribes evaluation outputs and expressly does not establish the recorded joint result. |
| Independent recomputation and comparer completion | **Yes**, if the Letter uses the joint tests. | Wait for the reviewed final verification required by the contract, with exact input/output identities and unresolved mappings closed. The reviewed report currently says **INCOMPLETE**, despite 712/712 compared rows agreeing. The later development comparison is not the formal verdict. |
| Authorized lost-seed recovery and its independent check | **Yes for the proposed inference Letter.** | Wait for the reviewed resolution report and Joseph's disposition of its effect on the claims. The current missing-seed sensitivity allows every primary rejection to change under realizable worst assignments. Preserve the frozen primary products and report the resolution separately, as authorized. |
| Existing Stage-7 scientific recording and deliverable updates | **Yes**, for the inference material used here. | Consume the campaign's approved text, tables and status decisions. Coordinate the later Letter rewrite so two owners do not edit the same scientific result in parallel. |
| Two-dimensional fixed-truth coverage study | Its outcome is already terminal on its evidence branch; consume the final record rather than rerunning it. | Integrate the independently reproduced undercoverage outcome wherever the paper discusses the tested statistical band. An uncertainty discussion cannot retain the stale statement that coverage is untested. |
| Any repair or successor campaign for a complete measurement uncertainty product | **Only if** the paper claims that repaired product, or Joseph retains complete uncertainties as a publication prerequisite. | Wait for construction, estimator matching, independent verification, validation and adoption under that campaign's own contract. An inference Letter with the scope change in Section 3 does not automatically require that product. |
| PET work, capacity studies, and optional representation comparisons | **No**, when their claims and products are omitted. | Retain PET's diagnostic/method-development status. Do not introduce a publication uncertainty claim to justify waiting for it. |

The [terminal inference record][s5p-terminal], [independent report][s5p-independent], [authorized extension and recovery decision][recovery-decision], and [coverage outcome][coverage-outcome] govern these distinctions. The table is not permission to bypass an existing contract. If final evidence is adverse, waiting longer without a named scientific decision is not a publication strategy.

## 3. Settle the publication scope before final drafting

There is an actual scope decision to make. The [September 1 decision][uncertainties-decision] treated scalar covariance completion as a claim upgrade while explicitly retaining completion of uncertainties before publication. The later [measurement-completion authorization][completion-authorization] requires qualified retained claims and excludes public deposit, release tagging and submission. Choosing an inference narrative does not silently revoke either instruction.

Prepare a short scope proposal for Joseph and the coauthors, with wording along these lines:

> Publish a conditional joint-inference Letter using the final verified `s5p` result and its declared response/nuisance model. Retain the completed central-value and benchmark results only within their supported scope. For this Letter, defer completion of the separate full measurement uncertainty product. Preserve the measurement branch's NOT ADMITTED / NOT READY state and every existing artifact grade and exception condition.

This is proposed decision text, not a decision recorded by this plan. If Joseph does not make that change, uncertainties remain a publication dependency. Final readiness must be recorded for the specifically approved Letter; it must not relabel the complete-measurement campaign as ready.

For the inference route, build one claim-to-evidence table containing: exact claim, tested estimator, null hypothesis, phase-space domain, nuisance/response assumptions, product digest, original measurement, independent check, and scientific disposition. Trace every claim in the abstract, figures and conclusion through it. Revisit the exact open-item records for any retained claim; an old readiness assessment is not current clearance.

The proposed principal claim is **joint incompatibility with specified generator predictions under the declared calibration model**, if the final reports support it. It is not automatically a localized discrepancy, a rejection of an entire generator family, identification of a nuclear mechanism, or proof that five dimensions outperform every marginal analysis.

**Exit gate:** an approved scope and a claim table with no unsupported headline. If the only surviving result is central-value unfolding plus narrow closure, reassess the PRL case before spending a week polishing it.

### If a complete measurement remains the publication requirement

The remaining requirements below are a conditional completion path, not additional work assigned to an ongoing campaign. Consume any qualifying products already delivered by their owners first. A complete measurement needs all of these; the existing successor proposal does not yet establish a feasible five-dimensional design.

1. **Admit a feasible measurement design.** Define the reported estimand, supported cells/projections, usefulness targets, estimator and interval construction before production. Establish that its accuracy and precision can meet those targets within a priced resource cap. The previous failure of measurement admission must be addressed explicitly; neither a global generator rejection nor a smaller bootstrap spread repairs it.
2. **Match the central estimate and uncertainty construction.** Demonstrate consistency of estimator/backend, training and seed policy, selection, background subtraction, normalization and extraction across the central product and every uncertainty component. Any transfer between recipes needs evidence and a declared justification. Replacing the published central estimator is a separate adoption decision.
3. **Construct the full declared uncertainty model.** Account for data statistics, finite simulation, flux, detector response, interaction-model effects, background, estimator/training variability and material bias/model dependence, with correlations and normalization handled consistently. Specify which effects are probabilistic and which are separate allowances. A prior-shift envelope is not automatically a per-cell bias bound, and summing available matrices does not establish completeness.
4. **Validate the resulting intervals and accuracy.** Independently test the actual matched construction at declared truths/departures and response conditions, with criteria fixed before evaluation. Distinguish nominal closure, statistical coverage, total-interval validation and nuisance-model adequacy. Resolve the known two-dimensional statistical-band failure for any repaired measurement that uses that band; do not extrapolate a two-dimensional result to five dimensions. Validate the intended projections and integrated quantities as well as the retained joint reporting definition.
5. **Verify, adopt and release the exact products.** Independently reproduce the construction, assess seed/ensemble stability against the declared criteria, and obtain Joseph's scientific disposition. Release the central values, uncertainty representation, masks, units, correlations and projection recipe with their validation and exception records. An old byte-scoped adoption cannot qualify new bytes or cure an unresolved gate.

If a successor cannot meet accuracy, coverage or usefulness targets, end with a documented failure or scope proposal rather than enlarging the campaign indefinitely. A qualified two-dimensional measurement would support a narrower paper; it would still leave the full five-dimensional measurement objective unmet. Once the chosen measurement qualifies, continue through the manuscript, release, review and publication stages below using its own matched claims. No credible date for this branch exists until a feasible construction and validation campaign are approved and costed.

## 4. Assess the scientific result after the required handoffs

Do this from the final committed products and approvals, not the presently pending transcriptions. Do not reconstruct or repeat the owners' production/recovery procedures.

### Required numerical and statistical evidence

Prepare a compact result table that identifies each null and domain, total and shape statistic, Monte Carlo numerator and denominator, p-value, Monte Carlo interval, multiplicity decision and determinacy, and applicable robustness labels. Preserve the predeclared ten-test family; do not select a smaller family after observing the outcomes. Report Monte Carlo p-values with their finite resolution, never as zero or as unsupported Gaussian significances.

Keep the frozen primary results and authorized recovery sensitivity distinguishable. Record whether the final interpretation remains conditional, becomes inconclusive, or cannot support the intended headline. The recovery is report-only under its governing decision; a favorable recovery does not replace the original stopping history or silently upgrade the primary analysis.

Report power only for the alternatives, nulls and settings actually evaluated. Poor power cannot support an agreement claim, and high power for one deformation does not establish broad sensitivity to interaction mechanisms.

### Required physics interpretation

The [production-admission contract][admission-contract] defines a fine-grid hybrid null: the stated fine-five-dimensional prediction, with the declared below-cell shapes and nuisance model. State that conditioning accurately. The supported domain is 109 cells for the applicable predictions, while GiBUU uses its 72-cell restricted domain; display that difference beside the comparison rather than hiding it in a supplement.

Assess whether the nuisance and detector-response model is scientifically adequate for the proposed inference. The declared model lacks a recoil-energy-scale band and does not establish complete hadronic-response coverage. Numerical recomputation establishes arithmetic agreement; it does not settle whether omitted plausible responses could explain the discrepancy. Essential conditioning belongs in the Letter itself.

Distinguish the estimator used by the calibrated tests from the older production central-value estimator. A p-value computed for the newer procedure cannot be attached to an older map as though that map were the tested paired result. Figures must identify their estimator and purpose.

Treat localization in the high-`E_avail`, high-`W` region as descriptive unless an approved test specifically establishes it. Existing repaired external-generator comparisons do not by themselves establish a universal localized DIS anomaly. A statistically significant global shape test does not identify which region or mechanism causes it. A claim that joint information adds discrimination beyond lower-dimensional results needs an actually matched comparison; omit that comparative claim if such evidence is absent.

**Exit gate:** the principal result survives the final missing-seed disposition and has a defensible physical interpretation under explicit assumptions. If a plausible untested response effect is central to the conclusion, either narrow the conclusion honestly or hold for a separately scoped study. Do not hide a conclusion-changing gap in limitations prose.

## 5. Turn the existing short paper into the Letter

The [existing PRL source][paper-source] already contains the unfolding framework, benchmark and central-value story. It does not yet contain the final joint-inference result. Reuse that foundation, then rewrite the abstract, main result and conclusion around the approved claim. Do not begin another broad analysis-note project.

Suggested core sequence:

1. **Physics question and result:** explain the generator-model problem and the specific new finding in language accessible beyond unfolding specialists.
2. **Data and method:** identify the sample, five observables, estimator, supported phase space, and why the joint test addresses that question. Explain that derived observables remain correlated; five observables do not mean five independent measurements.
3. **Validation:** summarize the completed benchmark/closure evidence, distinguish its limits from calibrated test validity, and give the essential response and missing-seed qualifications.
4. **Principal inference:** show final verified total/shape results, multiplicity control, robustness and the permitted physics interpretation.
5. **Consequence:** explain what the result constrains and what a complete measurement release would add.

Use only figures that establish those points. A likely set is a compact benchmark/validation panel, an accurately identified joint central-value projection, and a generator-test/robustness panel or table. These are proposed figure roles, not a requirement for new calculations. Essential validity conditions stay in the core; implementation detail and extended tables can go in End Matter or the supplement.

Update the note and primer consistently with the final campaign handoff and Letter:

- Replace stale two-dimensional coverage language with the actual failed statistical-band test and its narrow scope. This was not a test of the full systematic budget or five-dimensional coverage; it also did not erase the validated central-value benchmark or establish a repaired band.
- Distinguish constructed uncertainty, estimator matching, tested coverage, adoption, and publication interpretation throughout.
- Do not derive the new inference significance from the older adopted scalar covariance. If that covariance is retained anywhere, carry its four adoption measurements and byte-specific exception conditions in the relevant explanation. Otherwise omit precision claims based on it.
- Remove quarantined historical significances and unsupported PET precision statements. Do not repeat withdrawn lower-bound or infinite-ensemble claims.
- Resolve any still-open issue affecting a retained literature statement or physics claim, using its exact governing record.

Make a targeted novelty comparison against the original [OmniFold Letter][omnifold-prl], the [existing neutrino OmniFold study][neutrino-omnifold], and relevant real-data neutrino measurements. Do not claim first use of OmniFold in neutrino physics. Establish precisely what this result adds; avoid a priority claim unless the literature check supports it.

Aim for the current PRL limit of 3,750 word-equivalents in the core and at most two pages of End Matter. Count using the APS length rules, including figure/equation equivalents; a source word count or a four-page PDF is insufficient. The Letter must be convincing without its supplement. Prepare the required 100-word significance justification and an accurate Data Availability Statement. [PRL author instructions][prl-authors]

**Exit gate:** a self-contained manuscript whose title, abstract, figures, numerical table, conclusions and submission justification all describe the same supported result. A concise methods demonstration alone is not automatically a strong PRL case; assess importance and breadth against the [journal criteria][prl-about].

## 6. Prepare a release that reproduces the actual claims

Prepare the release locally for review before requesting any public deposit or tag. Include the following where needed by retained claims:

| Release component | Minimum useful content |
|---|---|
| Numerical results | The tested observable/reporting definitions, units, edges, masks, cell order, relevant central arrays, and prediction domains. |
| Inference definition | Actual estimator configuration, metric and prediction-MC inputs, null and nuisance definitions, declared variants, and multiplicity/stopping rules. The metric is not a general measurement covariance. |
| Calibration and resolution | Sufficient committed statistics/arrays and seed identities to replay the published tests; observed statistics; frozen primary results; separately labelled recovery/sensitivity products; applicable power summaries. |
| Provenance | Source commits, input/output digests, generator configurations, flux/target definitions where relevant, approved scientific records and independent verification routes. |
| Reproduction | A documented standalone path from released sufficient products to every main table and figure, with dependencies, expected outputs and material tolerances. |
| Access boundaries | An explicit account of which inputs are public and which require internal MINERvA access, with the actual access route where one exists. |

Use the existing [release appendix][release-appendix] as a starting inventory, not evidence that a current complete public package already exists. Test the release in an empty checkout/environment independent of the author's analysis directory. Verify masks, row order, units and array alignment, then reproduce the published numerical decisions and figure inputs. An independent reader should not need unpublished absolute paths or an undocumented internal covariance file to replay the released inference.

Public sufficient-product replay and end-to-end event processing are different reproduction levels. If raw AnaTuples and event-level generator samples cannot be released, say so directly. Do not call the public package end-to-end reproducible. Confirm actual rights and MINERvA release requirements for the selected data/products before publication; no general approval bureaucracy is added beyond requirements that apply.

**Exit gate:** a versioned, reviewable release candidate with a successful independent replay of retained claims and an honest account of unavailable inputs.

## 7. Review once the complete target is fixed

Freeze the draft, numerical products, claim table and release candidate for one substantive review. Ask the independent reviewer and coauthors to answer four concrete questions:

1. Are the inference calculation, calibration assumptions and missing-seed interpretation supported by the final evidence?
2. Does each physics statement follow from the tested hypothesis and domain?
3. Can the release reproduce the retained claims, and are its access limits accurately stated?
4. Is there a consequential advance that makes a credible PRL case?

The writer resolves findings, and the reviewer checks the changed artifacts in a second focused pass. Material disagreement about validity means a scientific disposition by Joseph and coauthors, not a vote among assistants. Preserve the findings and resolutions with the reviewed versions. Further review requires a named reason after the two-cycle reassessment point.

A gap discovered here is not an automatic new compute task. First determine whether existing evidence settles it or whether the claim can be removed without destroying the paper. If new scientific work is essential, propose its named decision, observable quantity, predeclared success/failure criteria, resource cap, independent check and terminal outcome separately. Post-data changes must be disclosed and appropriately controlled. Do not reopen completed central-value studies by default.

**Exit gate:** no unresolved material blocker for the approved scope, and explicit coauthor agreement on its scientific content. PRL acceptance is not a review gate we can certify internally.

## 8. Build, synchronize and freeze the submission package

Work in an isolated manuscript branch/worktree and integrate concurrent campaign changes deliberately. Preserve the shared checkout and unrelated work.

Run the existing analysis-note `build_all.sh` to build note, primer and paper, including its unresolved-reference and historical-value checks. Inspect the final PDFs visually for figures, equations, tables, masks, units and typography. Those checks validate deliverables; they are not scientific validation.

Synchronize the corresponding source files, bibliography and figures to the standalone `MINERvA-OmniFold-Analysis-Note` repository. Build and verify there, commit and push both approved source versions, then record both exact remote heads. Repository synchronization is mandatory for analysis-note changes; successful local builds alone do not finish this work.

Prepare a final submission package containing:

- Final Letter PDF and complete LaTeX/figure/bibliography sources.
- End Matter and supplemental files with their own accurate references.
- The 100-word PRL justification and cover letter describing context, findings and relevant submission history.
- Data Availability Statement, release candidate and approved deposit plan.
- Author list, affiliations, contact information, funding and acknowledgments, ORCIDs where applicable, and any substantive AI-use disclosure required by APS.
- Internal scientific/readiness record, reviewer resolutions and exact version manifest. Internal evidence can remain internal; do not upload private material as a supplement by accident.

Choose publishing/licensing options with the authors, checking current charges or institutional arrangements only if those choices matter. Optional publicity and cosmetic extras do not belong on the scientific critical path.

**Exit gate:** the exact sources generate the exact PDFs approved by all authors, both repositories are synchronized, and the numerical release matches that version.

## 9. Approve and perform the outward publication actions

Only now present the concrete package for Joseph's final publication decision and all authors' approval. Identify the exact requested acts: release tagging, public data/code deposit, preprint posting if desired, and journal submission. The existing completion authorization explicitly excludes these acts; approval of this planning document is not their authorization.

After those acts are authorized, create the agreed release/deposit identifiers, verify that their actual contents and access settings match the reviewed package, finalize corresponding links, and submit the approved version. Record the preprint identifier and/or journal accession, timestamp, deposited versions and source heads. A preprint makes the work publicly available; it is not PRL acceptance.

## 10. Carry the paper through review and publication

For editorial screening or referee reports, prepare one point-by-point response tied to the exact submitted manuscript and evidence. Separate explanatory revisions from requests for new scientific work. Make each change traceable and keep the response, marked manuscript, clean manuscript and supplement aligned.

If a referee exposes a material scientific deficiency, pause the publication claim until it is resolved or removed legitimately. Any necessary new computation gets its own bounded decision and authorization. Do not promise unspecified reruns or reselect tests until a preferred significance returns.

If PRL declines the paper for scope or importance while the science remains sound, have the authors decide whether a justified appeal or transfer is appropriate. A specialist-journal version can expand the methods and limitations using the same qualified evidence. It must not acquire a complete-measurement claim through a change of journal.

For accepted work, inspect proofs carefully for hypothesis definitions, subscripts, uncertainty language, units, generator domains, multiplicity statements, tables and URLs. Check the public release against the accepted version; preserve earlier versions rather than overwriting their scientific history. Deposit or update the accepted material under the agreed permissions, synchronize final source changes to both repositories, and record the published DOI and archived release identifiers.

**Publication is complete when** the published article, its supplement and cited accessible numerical products correspond to the accepted claims and reproducible version, with both source repositories traceable to that version. Submission, acceptance and publication should remain separate recorded milestones.

## 11. Schedule and resource expectations

These are planning estimates for the remaining manuscript/release work, not measured campaign durations. They assume an available manuscript owner, prompt coauthor review, reusable final campaign products, and no newly discovered scientific blocker.

| Remaining publication work | Estimated effort/calendar allowance | Can proceed while waiting? |
|---|---|---|
| Scope proposal, claim-table skeleton, targeted novelty check, manuscript outline | 1–2 working days | Yes; final scope and claims remain conditional. |
| Consume final evidence and assess retained claims | 1–2 working days after the required handoff | Preparation yes; final disposition no. |
| Letter rewrite and figure/table assembly | 3–5 working days | Methods and layout yes; numerical headline and conclusion wait. |
| Release packaging and independent replay | 2–4 working days | Inventory and packaging framework yes; final products wait. |
| Focused review, repairs, builds, synchronization and submission materials | 3–5 working days | Preliminary preparation yes; final review needs the complete target. |
| Author approval and outward submission | Availability dependent | Exact package must be ready first. |

With overlap, a reasonable target is **about 1–3 weeks to a submission candidate from now if the required handoffs arrive promptly and support the scope**. A safer allowance is roughly **7–12 working days after the required scientific handoff**, with useful preparation completed beforehand. These estimates do not add the existing campaigns' compute time to the new plan and do not guarantee their completion dates.

If uncertainty completion remains required, or a missing response effect needs new validation, no defensible total duration follows from this manuscript schedule. The corresponding scientific plan must establish feasibility and cost first. Peer review, revision and journal production add externally controlled time; this plan makes no publication-date promise.

No new scientific cluster allocation is proposed for the inference-first route. Existing campaigns retain their own resource contracts. Local figure production, builds and sufficient-product replay are remaining verification work, not a new unfolding ensemble. A complete measurement successor, exhaustive uncertainty campaign, PET uncertainty product or broad representation comparison is outside this plan unless the approved claims require it.

## 12. Final checklist

- [ ] Joseph and the coauthors approved the exact scope, including whether completion of separate measurement uncertainties remains a publication prerequisite.
- [ ] Required campaign closeout, formal independent verification and missing-seed interpretation are committed and routed; no development verdict is represented as final.
- [ ] Every retained claim has exact evidence, estimator/domain matching, appropriate calibration and a disposition of material limitations.
- [ ] The Letter has a credible novelty/importance case without unsupported first-use, localization, mechanism or precision claims.
- [ ] Two-dimensional coverage wording reflects the terminal failed test and its actual scope; no unvalidated repair is asserted.
- [ ] No quarantined result or byte-scoped exception has been promoted by implication; complete-measurement readiness remains separately recorded.
- [ ] If a complete measurement is retained, its feasible design, matched total uncertainty, validation and exact-product adoption have all qualified under their governing contract.
- [ ] Main text is self-contained and within the current PRL length rules; submission justification and disclosure statements are complete.
- [ ] The release independently replays the retained numerical claims, with public/private reproduction boundaries explicit.
- [ ] Focused review has no unresolved material blocker; every author approved the exact final version.
- [ ] Note, primer and paper build and pass visual inspection in both repositories; corresponding sources are committed and pushed and both remote heads recorded.
- [ ] Joseph separately authorized the specific public release and submission acts, which use the reviewed package.
- [ ] Referee revisions, accepted proofs, published article and archived products remain consistent and traceable through publication.

## Evidence and policy routes

The adjacent [measurement-successor proposal](PROPOSAL-20261005-scalar-measurement-successor.md) remains a separate proposal for a measurement path. This plan does not execute or replace it. This new local document is not covered by that proposal's independent review or included in its existing delivery bundle.

[campaign-review]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/0a988bc44f68c66f042420e391ac445f1fe1d630/docs/orchestration/CAMPAIGN-REVIEW-20260929.md
[s5p-terminal]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/0a988bc44f68c66f042420e391ac445f1fe1d630/docs/orchestration/RECORD-20261005-s5p-terminal-evaluation-pending-verification.md
[s5p-independent]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/02df81e64ba10c4d817fc66eb068af1d39ef23eb/docs/orchestration/REPORT-20261005-s5p-recompute-final-verification.md
[recovery-decision]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/0a988bc44f68c66f042420e391ac445f1fe1d630/docs/orchestration/DECISION-20261005-s5p-recompute-extension-and-lost-seed-recovery.md
[coverage-outcome]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/808628787980f990f6096f67dc15f84b669cb56a/docs/orchestration/OUTCOME-20261005-2d-fixed-truth-coverage-fail.md
[uncertainties-decision]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/0a988bc44f68c66f042420e391ac445f1fe1d630/docs/orchestration/DECISION-20260901-joseph-oi187-upgrade-not-blocker.md
[completion-authorization]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/0a988bc44f68c66f042420e391ac445f1fe1d630/docs/orchestration/AUTHORIZATION-20260926-precision-measurement-completion.md
[admission-contract]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/0a988bc44f68c66f042420e391ac445f1fe1d630/docs/orchestration/state/s5p/contract-amendment-7-production-admission.json
[paper-source]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/0a988bc44f68c66f042420e391ac445f1fe1d630/docs/analysis-note/paper_body.tex
[release-appendix]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/0a988bc44f68c66f042420e391ac445f1fe1d630/docs/analysis-note/app_release.tex
[omnifold-prl]: https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.124.182001
[neutrino-omnifold]: https://journals.aps.org/prd/abstract/10.1103/sp1f-n9k2
[prl-authors]: https://journals.aps.org/prl/authors
[prl-about]: https://journals.aps.org/prl/about
