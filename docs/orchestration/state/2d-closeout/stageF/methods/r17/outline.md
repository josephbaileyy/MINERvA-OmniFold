# Reverse outline of the methods paper and the r17 restructuring proposal (2026-10-25)

**Base:** origin/main `e848fa49` (`docs/analysis-note/main_paper.tex`, `paper_body.tex`). **Method:**
`register-method/HANDOFF.md` §3; rules R1–R10 and the KEEP list of `register-prd-study/REPORT.md` §§4–5; the paper's
standard of `DECISION-20261023-joseph-5d-a-and-register-round.md` item 2. Paragraph ids `¶n` are numbered in source
order within each section, and the source line is where the paragraph starts in `paper_body.tex` at `e848fa49`.

**Baseline P1 (sol2, blinded rater copy sha256 `00aaeeb4…`): 3, 3, 3.** Gemini: 2.5, 3, 2.5. All three sol2 runs
quote the earlier-band paragraph (IV B ¶4) and the calibration-budget disclosure (VII C ¶3). Two quote the Fig. 3 seed
sentence, and one quotes the data-availability package text. All three Gemini runs quote VII C ¶3 and IV B ¶4; two
quote the Sec. I scope paragraph and one quotes the V D seed sentence.

## 1. Before: one sentence per paragraph

| ¶ | line | words | main idea |
|---|---|---|---|
| abs | MP:70 | 115 | 2D integral within about 1% with a shape difference; 5D central values only; pseudo-experiments reveal three biases; with the envelope no definition meets 10%; the hybrid-null tests all reject, with no evidence of gain. |
| I¶1 | 33 | 123 | Binned unfolding scales badly with dimension; OmniFold is unbinned and has been used at H1, ATLAS and on simulated T2K. |
| I¶2 | 49 | 79 | We reproduce the 2D result and add Eavail, q3 and W for 3D–5D central values; reconstructed W is not independent; data measurements reach 3D. |
| I¶3 | 62 | 167 | A case study; coverage and calibration are distinct; calibration "to the extent that" the chain reproduces the data analysis; Secs. IV–VI are the main results (Table I); Sec. VII is secondary. |
| T1 | 82 | 200 | Findings table (protected). |
| I¶4 | 106 | 201 | Scope, mostly in negatives: one implementation, "not a general assessment"; 3D–5D = central values with "no intervals of validated coverage", "does not deliver"; conditional hybrid-null tests; no recoil band; FWER under assumptions; "not physical exclusions … no measurement uncertainty"; limitations in VIII A; note pointer. |
| II¶1 | 130 | 237 | Data, exposure, signal definition, selection, sample sizes, GENIE + Tune v1. |
| II¶2 | 163 | 163 | Truth definitions of pT, p∥, q3, W, Eavail; the 135 MeV constant and its ≤1.05% effect. |
| II¶3 | 192 | 148 | Reconstructed Eavail, q3, W; W_reco an exact function of (pT, p∥, q3); truth W to within ±2 MeV. |
| II¶4 | 211 | 196 | External predictions; flux reweighting; neutron-mass W; pT axis; the CH-vs-carbon target difference not corrected. |
| II¶5 | 236 | 100 | Fine grid; 3^5 coarse grid; 109 reported cells; GiBUU's 72 cells. |
| III¶1 | 251 | 84 | The two OmniFold steps and cross-section formation. |
| III¶2 | 261 | 107 | Purity-based against negative-weight background treatments. |
| III¶3 | 272 | 30 | No held-out split, early stopping or class balancing. |
| III¶4 | 278 | **395** | Five iterations; regularization; nominal settings; no data search; which configuration serves which result, (f) for 2D, (a) for 5D, (e) for 3D/4D and tests; (e)'s fixed iteration criterion. Table II sits inside it. |
| III¶5 | 338 | 138 | Closure and coverage definitions, pointwise coverage; what the studies reweight; detector response fixed except in the calibration. |
| IVA¶1 | 360 | **243** | Integral ratio 1.010; 95.1% within 10%; χ²/ndf 2.27 with the pinv detail; correlated shape difference; learner dependence; the post-selection disclosure (KEEP); exact-split cross-check. |
| IVB¶1 | 413 | 180 | Four blocks; 6.41% and 4.76% against 6.85% and 4.61%; flux difference not determinable; what the covariance omits. |
| IVB¶2 | 439 | 202 | C_model beside the covariance: 3.71%, "not a calibrated bound", a shape component; why the published comparison omits it. |
| IVB¶3 | 464 | 95 | Run periods inconsistent; a 7% step; cause unknown; the run-period block includes it. |
| IVB¶4 | 477 | 145 | Statistical block 0.676%; then the history of an earlier band (prespecified test failed in the tails) and a post hoc rescoring of a rebuilt band, "not an independent coverage test"; a stray closing sentence, "the 2D central value is reproducible". **Bound by `check_sec4_receipts.py` and Table I.** |
| VA¶1 | 507 | **270** | 4D/5D normalizations at 1–2%; (e) 3D marginal 0.141%; 3D and 4D closures; the purity bias up to 4% at high W, "not included in the quoted uncertainties"; negative weights reduce it; the 2D closure with backgrounds, hence (f). |
| VB¶1 | 548 | 167 | A generator-sized Eavail change only partly recovered (74% at high W); interpreted as regularization bias; other shapes 16–31%. |
| VC¶1 | 574 | 104 | Statistical intervals miscover at the tested truths; 51 of 153 below 0.66. |
| VC¶2 | 587 | 76 | Gaussian diagnosis: a residual bias growing with W; intervals not too narrow; normalizations agree despite bias. |
| VD¶1 | 674 | 93 | The 5D covariance fails its criteria; used only in V B; seed sensitivity 6.1% > 5%; no covariance-based significance. Pointer prints "Secs. 9.6 and 9.6". |
| VD¶2 | 689 | 77 | Rounding-level instability, 2.6 σ; inside the bootstrap uncertainty for (e). |
| VE¶1 | 702 | 153 | Envelope defined; "a sensitivity diagnostic … not an interval"; no definition meets 10%. |
| VE¶2 | 720 | 50 | Envelope 10–13%, comparable to generator differences; motivates Sec. VII. |
| VI¶1 | 757 | 95 | Three results point to the prior retained; whether the miscoverage has the same origin "is not established". |
| VI¶2 | 770 | **224** | The binned diagnostic of Table III; the scope of the diagnostic; the out-of-scope sentence (CLAIM-ADDITION, kept by its record, r15). |
| VI¶3 | 807 | 72 | The checks needed before intervals are interpreted; calibration as the alternative. |
| VII¶1 | 818 | 125 | Why unfold before testing; reconstruction-level tests need the same response; "We have not compared their power". |
| VIIA¶1–3 | 837 | 212 | Descriptive comparisons, no significance; the low-Eavail deficit; the (Eavail, W) excess map; the map describes where the central value differs. |
| VIIB¶1 | 874 | 161 | The hybrid null H0(G) and three distinct properties. |
| VIIB¶2 | 892 | 138 | One calibration pseudo-experiment, step by step; null distributions conditional on the data. |
| VIIB¶3 | 910 | 99 | T_tot, T_sh, the metric Σ. |
| VIIC¶1 | 927 | 91 | Monte Carlo p value; shifted nulls. |
| VIIC¶2 | 937 | 154 | Holm, sequential sampling, the CP rule, A1 and A2, FWER; size averaged over priors; error control on decisions. |
| VIIC¶3 | 955 | 128 | Design fixed before the statistic; reviewers had seen residuals; budget extended after the p values were visible; error control unaffected; lost pseudo-experiments; rerun changes nothing; independent recomputation. |
| VIID¶0–5 | 982 | 453 | Six conditions; (i) convergence not shown, residual unmeasured; (ii) no recoil-response band, the post hoc 2D-projection observation, the ±4% study and what it does not test (**199 words**); (iii); (iv) simulation size; (v)(vi). |
| VIIE¶1 | 1047 | 168 | All rejected; CH correction, NuWro total not robust, GiBUU energy; κ scan; null locations. |
| VIIE¶2 | 1102 | 179 | The contribution; matched projections; "no evidence of additional discrimination"; global assessments; power. ¶1's pointer prints "Secs. 10.9, 10.5, and 10.5". |
| VIII¶1 | 1127 | 70 | Results are Table I's; Sec. VI; FWER "provided the calibration is exact" (KEEP). |
| VIIIA | 1141 | 373 | Nine limitations, of which eight are "has not been …" status sentences, several with two negatives. |
| DA | MP | — | Data availability (protected). |
<!-- absence-ok: quotes or summarizes printed paper text, whose paragraph in paper_body.tex carries its own Search line; not a new absence claim -->

**What the outline shows:**
1. Four long paragraphs (III¶4, IVA¶1, VA¶1, VI¶2, 224–395 words) each carry three or four ideas.
2. IV B ends on a history paragraph, and its last sentence ("reproducible") does not follow from it (r16's note).
3. Sec. I puts its roadmap (I¶3) before the scope (I¶4), and the scope is written as negatives that VIII A repeats.
4. VIII A is a list of status disclaimers, not consequences.
5. Two pointers print a section number twice, because two note labels resolve to one section: "Secs. 9.6 and 9.6"
   (V D) and "Secs. 10.9, 10.5, and 10.5" (VII E). Both read as errors.

## 2. Proposed order and moves

The section order stays. The raters and r10/r11 found it conventional, and Sec. VI stays the synthesis. Paragraph
order and paragraph splits change inside sections. No `\label` changes.

| move | where | proposal | rule |
|---|---|---|---|
| S1 | I | I¶1 gains the state of the art: "data measurements reach three dimensions [10–13]" moves from I¶2. I¶3 keeps the case-study question and the coverage/calibration distinction. The roadmap (main results Secs. IV–VI with Table I; Sec. VII secondary; limitations VIII A; note pointer) moves to the end of the scope paragraph. | R1, R7 |
| S2 | I¶4 | Scope rewritten positive-first, as definitions: what the findings cover; "a three- to five-observable result means a central value of …"; the tests are of hybrid nulls, calibrated within the simulation model, FWER under the Sec. VII C assumptions. KEEP: "not a validated five-observable cross-section measurement" (one negative); hybrid null; no recoil-response uncertainty; "not physical exclusions" and "no measurement uncertainty" as one sentence. | R1, R8, KEEP |
| S3 | III¶4 | Split into three: (a) shared settings and their regularizing role, no data search; (b) which configuration serves which result, with "the 2D central value is reproducible" moved here from IVB¶4 (it belongs with (f)'s seeding); (c) (e)'s fixed iteration criterion. | R10 |
| S4 | IV A | Split into two: agreement (ratio, 95.1%, RMS, χ² as a shape difference); estimator dependence with the post-selection disclosure kept next to the choice (KEEP), and the exact-split comparison. The pinv/rank detail stays; it is a fact. | R4, R10, KEEP |
| S5 | IV B | Reorder: blocks and sizes (¶1); the statistical block and its coverage test (¶4); run periods (¶3); C_model (¶2). ¶4 rewritten as a test report: tested what, against what, criterion, outcome, then the post hoc rescoring in one sentence with its reason. The phrases bound by `check_sec4_receipts.py` stay verbatim; Table I's "an earlier band failed coverage" still finds its test here. | R4, R9 |
| S6 | V A | Split into three: normalization checks; closure with backgrounds and the purity bias (KEEP "except in the highest-W cells", "the quoted uncertainties omit this bias" as its own sentence); the 2D closure with backgrounds, which motivates (f). | R10, KEEP |
| S7 | V D | One pointer: "Sec. 9.6". | language |
| S8 | VI¶2 | Split: the diagnostic's result; its population and scope. The CLAIM-ADDITION block's out-of-scope sentence stays (r15: its record requires it). | R10 |
| S9 | VII¶1 | "We have not compared their power with that of a reconstruction-level test" moves to VIII A as one item (the fact stays in the paper). | R6 |
| S10 | VII C¶3 | Reorder by R9: design fixed (with the reviewers' look, KEEP); budget extension (KEEP, at the choice); the error-control consequence; the lost pseudo-experiments and the rerun in two sentences; recomputation. No fact leaves. | R6, R9, R10 |
| S11 | VII D (ii) | Split: the omitted band and why it matters (with the post hoc 2D observation, KEEP as disclosure); the ±4% exploratory study and its limits. | R10 |
| S12 | VII E | ¶1's pointer becomes "Secs. 10.9 and 10.5". | language |
| S13 | VIII A | The nine items (ten with S9) rewritten as plain declaratives, each with its consequence, grouped as 2D (1–2), five observables (3–5), map (6), tests (7–10). The facts and the conditions stay; the stacked "has not been … nor … no" constructions go. | R2, R6, R10 |
| S14 | Fig. 3 caption | The seed sentence, same meaning in plainer words. | language |

**Not touched:** Table I; the `\pubhold`s; acknowledgments, AI acknowledgment, funding and data-availability text;
the abstract, except as S2 requires (none expected); the 5D sections' labelling "(a) for now", the S1 (e) covariance
and the fake-data plan. Every phrase that `check_sec4_receipts.py` binds stays byte-identical.

## 3. What this round cannot move

- **The earlier-band paragraph (IV B ¶4)** is the top complaint in all three sol2 runs. `check_sec4_receipts.py` binds
  its values to `paper_body.tex`, and Table I points to it. S5 rewrites it as a test report around the bound phrases.
  Moving it to the note would need the check repointed and Table I changed, which are protected.
- **The budget-extension disclosure** (VII C ¶3) is a fact fixed by `DECISION-20261004…` §3. S10 reorders it but
  does not remove it.
- **The data-availability text** is Joseph's.
