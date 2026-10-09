# PRD article: editorial and presentation pass before Joseph's full readthrough (2026-10-08)

**CITABLE FOR:**
- what this pass changed in the article's presentation, and why;
- the measured before/after counts;
- the APS/PRD sources consulted and the five comparable papers examined;
- the presentation issues that remain;
- the scope proposals this pass leaves for Joseph.

**NOT CITABLE FOR:** any physics result, claim status, gate, label, release identity or approval. No claim was
strengthened, no result or number changed, no scientific work was launched, and nothing was sent or published.
The routed records (`CLAIMS-20261005-claim-to-evidence.md` and its sources) remain the authority for every
statement in the article.

| | |
|---|---|
| authority | Joseph, 2026-10-08 (goal "Prepare the article for Joseph's full readthrough by completing a PRD editorial and presentation pass"). It authorizes routine editorial changes, one fresh read-only reviewer with at most two review/repair cycles, a reviewable PR (left unmerged), and the standalone-note sync on a matching branch. It authorizes no external message and no publication act. |
| baseline | `origin/main` `b612ee3ac9b517c56e1153223576b7c3f5dcd32a` (merge of PR #55), fetched 2026-10-08. Worktree `MINERvA-OmniFold-prd-editorial-20261008`, branch `docs/prd-editorial-pass-20261008`. |
| read before editing | `AGENTS.md`; `docs/orchestration/CAMPAIGN-REVIEW-20260929.md` (in full); `DECISION-20261006-joseph-publication-approvals.md`; `CLAIMS-20261005-claim-to-evidence.md` (§A–F); `submission/PACKAGE-MANIFEST-20261006.md`; `REVIEW-20261007-paper-completion.md`; `corrections-20261008/RECORD-20261008-release-audit-corrections.md`. Also the compiled article PDF at the baseline (10 pp, read page by page). |
| bound wording checked before editing | the lost-seed disposition and its five required disclosures (`DECISION-20261005-s5p-recompute-extension-and-lost-seed-recovery.md` §5); the forbidden phrasings (`CHECKLIST-20261001-s5p-terminal-and-claims.md` §4); Joseph's κ-scan wording (`publication/kappa/RECORD-20261008-kappa-breakdown.md` §5); the Fig. 2 scope decision ("stands as written"); the four measurements that travel with the adopted covariance (`DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md` §4); the approved AI-use disclosure (verbatim; **not edited**). |

## 1. Campaign-review choice (`CAMPAIGN-REVIEW-20260929.md` §1)

- **Decision answered:** is the article's presentation ready for Joseph's full readthrough as a PRD regular article?
  What does the journal require, what is merely conventional, and what remains for him to decide?
- **Ownership and review:** this session (Claude Opus 5.5) owns the edits. One fresh, read-only reviewer reviews the
  editorial diff in a detached worktree at a fixed commit. The review's recommended Astra-class reviewer is not
  available in this session, so the reviewer is a separate Opus 5.5 context; its independence is per session, not
  per model.
- **Budget and stop:**
  - at most two review/repair cycles;
  - no compute;
  - any scientific-scope question goes to §7, not into the text.

## 2. Sources: journal requirements, observed conventions, recommendations

### 2a. APS/PRD guidance (fetched 2026-10-08)

| item | class | what the source says | source |
|---|---|---|---|
| Regular-article length | **requirement: no limit** | "Research Articles (no length limit)". Letters have a limit (4500 words); regular articles do not. | [PRD authors](https://journals.aps.org/prd/authors); [length guide](https://journals.aps.org/authors/length-guide) |
| Abstract | guidance | "Length should be about 5% of the article and less than 500 words"; one paragraph; "completely self-contained"; "Avoid coined words and unexplained acronyms"; no numbered references. | [Style basics](https://journals.aps.org/authors/style-basics); APS Journals Style Guide for Authors (Feb. 2026), p. 11 |
| Acronyms | guidance | "Abbreviations used more than once should be defined the first time they are introduced in the abstract and in the text." | Style Guide p. 54 |
| Section structure | guidance only | headings "as needed, according to the style for the journal". No mandatory section template. | Style basics; Style Guide pp. 12, 22 |
| Captions | guidance | "Each figure must have a caption that makes the figure intelligible without reference to the text." Units in parentheses, not brackets. | Style Guide p. 44 |
| "Fig." / "Figure"; "Table"; "Ref." | guidance | "Figure" at the start of a sentence, "Fig." elsewhere; tables not abbreviated; "Reference" at the start of a sentence. | Style Guide pp. 18, 66, 70 |
| Units | guidance | SI preferred; avoid multiple slashes ("mb/(MeV sr), not mb/MeV/sr"). | Style Guide pp. 44, 55 |
| Reference titles | guidance (PRD-specific) | "Physical Review D strongly encourages authors to include titles for all references … Authors who elect to use titles in references should use titles in all references." URLs should not appear in the body. | PRD authors; style basics |
| Data Availability Statement | **requirement** | "All published articles must include a Data Availability Statement (DAS)" (PRD since 2024-09-04). Shared data must be cited. Placed after the Acknowledgments and before any appendixes and the references. | PRD authors; [DAS policy](https://journals.aps.org/authors/data-availability-statements); Style Guide p. 22 |
| AI use | **requirement** for substantive use | Disclose "AI tool name and version", "How the AI assisted" and "How the authors directed and verified the AI output". Research uses go in the methods; other uses go in the Acknowledgment. | [APS AI policy](https://journals.aps.org/authors/appropriate-use-ai-tools) |
| AI-generated images | **APS sources conflict** | Style Guide pp. 43–44: no "images generated or modified by generative AI". The AI-policy page: "AI can be used for data visualizations, but authors are responsible for verifying the accuracy". | Style Guide; AI policy |

The Style Guide is the February 2026 PDF linked from the PRD authors page. The old "Physical Review Style and Notation
Guide" URL returned HTTP 403. **No page limit or mandatory section template exists for PRD regular articles**, and none
is assumed here.

### 2b. Five comparable PRD papers (abstract words counted from the arXiv abstract; pages from the published PDF)

| paper | abstract words | pages | top-level sections | DAS | limitations |
|---|---:|---:|---|---|---|
| R. G. Huang et al. (T2K OmniFold), PRD 112, 012008 (2025), arXiv:2504.06857 | 121 | 15 | Introduction; Unbinned unfolding with OmniFold; T2K public dataset; Test setup; Performance and results; Conclusions; Acknowledgments; **Data Availability**; Appendix | yes, headed, after the Acknowledgments | body and Conclusions; none in the abstract |
| D. Ruterbories et al. (MINERvA), PRD 104, 092007 (2021), arXiv:2106.16210 | 120 | 20 | Introduction; Experiment; Simulation; Cross section extraction; Systematic uncertainties; Results; Comparisons; Conclusions | none (pre-policy) | the generator mismodelling is in the abstract; the source limitation is in the Conclusions |
| M. A. Acero et al. (NOvA), PRD 107, 052011 (2023), arXiv:2109.12220 | 127 | 20 | Introduction; Experiment; Simulation; Reconstruction and calibration; Selection; Energy reconstruction and binning; Measurement and results; Uncertainties; Comparisons to generators; Conclusion; Appendix (tables) | in-text pointer (pre-policy) | Uncertainties section and Conclusion |
| P. Abratenko et al. (MicroBooNE), PRD 110, 013006 (2024), arXiv:2402.19216 | 210 | 57 | Introduction; Experiment; Methodology; Data analysis; Model description; Model validation; Model expansions; Results; Conclusion; Appendixes A–B | Supplemental Material (pre-policy) | **in the abstract** (model insufficiency) and in dedicated validation sections |
| K. Abe et al. (T2K TKI), PRD 103, 112009 (2021), arXiv:2102.03346 | 97 | 27 | Introduction; Observables; Experiment; Simulation; Data and selection; Analysis method; Results (comparisons; discussion); Conclusion; Appendixes A–B | in-text pointer (pre-policy) | Results/Discussion |

### 2c. Observed conventions (observations from §2b, not requirements)

1. Abstracts run 97–210 words (median 121). They are declarative, name the generators compared, and none opens with a
   question.
2. The order is consistent: introduction → data/experiment → simulation → method → uncertainties → results → generator
   comparisons → conclusions; then the Acknowledgments, the DAS (when present) and any appendices.
3. None has a section titled "Limitations". Limitations sit in the Conclusions, the results discussion or validation
   sections. One of the five puts a model inadequacy in its abstract.
4. The one post-policy paper (Huang 2025) has a short headed "Data Availability" section citing references.
5. All five are longer than this article (15–57 pp against 10–11), and they use appendices for numerical tables and
   extra comparisons, not for the main argument.
6. Generator comparisons are usually quantified with a χ² over a full covariance. This article cannot do so for its
   five-observable result, and says why (Sec. VII).

### 2d. Editorial recommendations (this pass's judgment, applied in §4 unless listed in §6–§7)

- Make the abstract declarative and within about 150–180 words. Keep the two essential qualifications explicit: the
  rejections are conditional, and there is no qualified five-dimensional measurement.
- Follow PRD's reference-title guidance in all references.
- Move the DAS after the Acknowledgments.
- Define every acronym at first use, and name the generator labels used in Table I and Fig. 3 once in Sec. II.
- Replace campaign vocabulary and chronology with plain statements of the same content.
- Split sentences over about 60 words where the split loses nothing.

## 3. Before/after checklist (measured)

Counts: "texcount" is `texcount -nc` on the source (words outside math and macros; values printed through macros are
not counted); "PDF" is a `pdftotext` word count of the rendered article. The body includes the DAS in both columns.
Before = baseline `b612ee3a`; after = this branch after review cycle 1 (§8).

| item | before | after | note |
|---|---|---|---|
| title | "Unbinned Five-Observable Unfolding of MINERvA Charged-Current Neutrino Data and Calibrated Joint Tests of Generator Predictions" | "Unbinned five-observable unfolding of MINERvA inclusive charged-current neutrino data and calibrated joint tests of generator predictions" | sentence case (as in the published PRD titles of §2b); "inclusive" names the signal |
| abstract words (PDF / texcount) | 234 / 233 | **185 / 187** | 8 → 6 sentences; the rhetorical question is removed; no undefined acronym ("MEC" removed). The implementation reached 182; review cycle 1 restored "report-only" and "principal" and split "checks" from "closure tests" (§8). The remaining 5 words over the 180 aim are required qualifications. |
| abstract qualifications | conditional (principal limitations named); no 5D cross section; recovery report-only; ±4% not an uncertainty; not a measured cross section; no added discrimination | **all retained**, plus the disposition's "with every submitted pseudo-experiment observed" | Joseph's lost-seed disposition says the rejections are stated "as holding with every submitted draw observed"; disclosure 1 (report-only) stays beside it |
| body text words (texcount, incl. DAS) | 5,220 | 5,275 | +1.1%. The definitions, generator and software citations and motivating sentence offset the condensation (§4) |
| caption words (texcount) | 417 | 425 | the Fig. 2 color-scale units ($10^{-40}$ cm²/nucleon) and the Fig. 3 legend labels are now explained |
| pages | 10 | **11** | the extra page is reference titles only (PRD guidance, §2a); the text pages are unchanged |
| floats | 4 figures, 1 table | unchanged | about 1.5 page-equivalents, estimated from the rendered page images (Fig. 1 ≈ 0.44, Fig. 2 ≈ 0.15, Fig. 3 ≈ 0.47, Fig. 4 ≈ 0.35, Table I ≈ 0.10) |
| body sentences (PDF) | 203; mean 32.0 words | 212; mean 29.8 | measured to the Acknowledgments in both builds, so the after column excludes the moved DAS |
| sentences > 60 words (PDF) | 16 | **8** | the remainder are mostly frozen-contract conditions (Sec. VI B) and figure-text artefacts of the extraction |
| sentences > 40 words (PDF) | 58 | 52 | |
| internal/chronology tokens (PDF, body and DAS, Acknowledgments excluded, case-insensitive) | digest 2, bytes 1, catch 4, scheduler 2, design review 1, pre-repair 1, mis-sampled 1, later found 1, later measurement 1, campaign 3, self-validated 1, candidate 3, replay 3 | digest 1, bytes 0, catch 0, scheduler 0, design review 0, pre-repair 0, mis-sampled 0, later found 0, later measurement 0, campaign 0, self-validated 0, candidate 1, replay 3 | corrected after review E5: the first tally stopped at the Acknowledgments and so missed the moved DAS. "digest" ("the digest of every source product") and "replay" stay in the DAS, where they are the precise terms; "design-review value" stays in Sec. VI B (the contract's provenance statement). The reviewer's alternative tokenization gave campaign 4 and scheduler 3 before. |
| undefined acronyms at first use | RPA, MEC, FSI, MINOS, GEANT, 2p2h (spelled out each time) | defined or spelled out once (Sec. II; FSI in Sec. V; MINOS in Sec. II) | |
| notation clash | `W` was both the hadronic invariant mass and the test metric | metric is $\mathcal{W}$ | |
| references | 29; titles only on the `@misc` records; no generator, D'Agostini or ML-software citations; open-data DOI not printed | 37; **titles in all**; GENIE, Valencia 2p2h, NuWro, GiBUU, GEANT4, D'Agostini, scikit-learn and LightGBM cited; DOI printed | the new entries reuse the checked `technote.bib` records; scikit-learn and LightGBM were checked against arXiv:1201.0490 and the NeurIPS 2017 proceedings page |
| DAS placement | numbered Sec. IX, before the Acknowledgments | unnumbered "Data availability" after the Acknowledgments | APS placement (§2a); cross-references now read "see Data availability" |
| `\pubhold` | 1 (deposit identifier) | 1 (unchanged) | |
| build | `build_all.sh` PASS, 123 / 9 / 10 pp | PASS, 123 / 9 / 11 pp | note and primer sources unchanged |

## 4. What changed, by section

- **Abstract:** restructured (method → 2D reproduction → 5D central values and why no measurement → calibrated tests
  → result → conditions → scope), with every qualification kept (§3).
- **Introduction:**
  - a motivating first sentence;
  - the D'Agostini citation, and the opening sentence states the motivation without a comparative claim (softened in review cycle 1, N2);
  - the contribution restated with section pointers, and the specific advance stated against the published
    muon-kinematics comparison (as Sec. VI C already says);
  - the 2D statistical-band coverage item moved out of the list of *higher-dimensional* limitations, where it did not
    belong. It stays beside its claim in Sec. IV B and in the Conclusions.
- **Sec. II:**
  - "playlists" → run periods; AnaTuples glossed; MINOS introduced;
  - RPA and 2p2h spelled out;
  - the labels "GENIE CV" and "GENIE + MEC" defined;
  - generator citations;
  - "repaired flux sampling" → "corrected flux sampling (an exact event-by-event reweighting to the analysis flux, with added 50–100 GeV samples)", per `KNOWN_ISSUES.md` 83 (review cycle 1, B1: the predictions were reweighted, not regenerated).
- **Sec. III:** scikit-learn and LightGBM cited.
- **Sec. IV C:**
  - the mis-sampled-flux parenthesis rewritten without chronology;
  - "the tested candidate" named as the joint-test estimator (VL155 is candidate R, the joint-test estimator).
- **Sec. V:** FSI defined; "pre-repair GENIE" → "GENIE before its flux correction"; "catch" → "overflow"; generator
  labels used.
- **Fig. 2 caption:** the color scales named; the right panel's values stated in units of $10^{-40}$ cm²/nucleon (a multiplier; review cycle 1, B3); "overflow".
- **Fig. 3 caption:** units without multiple slashes; legend labels explained; the long sentence split.
- **Sec. VI A:**
  - metric renamed $\mathcal{W}$;
  - MINOS and GEANT4 named;
  - the data-informed disclosures in plain words ("reviewers of the design", "status outputs of the job controller"),
    with content unchanged;
  - the claim-variant sentence split.
- **Sec. VI B:**
  - states that the conditions are numbered as in the frozen contract, which explains the out-of-order numerals;
  - condition (i) split into shorter sentences, with every number and qualifier kept.
- **Sec. VI C:**
  - the coarse-projection clause, repeated in consecutive paragraphs, now appears once;
  - the power sentence split;
  - the κ-scan text unchanged.
- **Sec. VI D:**
  - "scheduler" → "computing-job time limits";
  - condensed, keeping disclosures 1–5 of the disposition;
  - "self-validated" → "checked only within the analysis".
- **Sec. VI E:** retitled "Hadronic-response condition and recoil-energy sensitivity"; one sentence split.
- **Sec. VII:**
  - retitled "Status of a five-dimensional uncertainty";
  - "digest-bound exception" → "a documented exception that covers that product alone";
  - "adopted bytes" → "the adopted one";
  - the measurement-study paragraph in plain words;
  - the PET pairing phrase avoids "the statistical uncertainty" (AGENTS trap) by saying "a bootstrap
    statistical-covariance estimate";
  - all four travelling measurements unchanged.
- **Conclusions:** split into two paragraphs and condensed; every condition kept.
- **DAS:** moved after the Acknowledgments; "an earlier candidate" → "an earlier version"; content unchanged.
- **Bibliography:**
  - `longbibliography`, which prints titles;
  - the explicit `\bibliographystyle` removed, because it bypassed revtex's control entry; with `aps,prd` revtex
    selects apsrev4-2 itself;
  - two software entries;
  - the open-data DOI printed.

## 5. Required disclosures preserved (checked against the source records)

| disclosure | where it stands after the pass |
|---|---|
| the six amendment-7 conditions | Sec. VI B (all six, numbered as in the contract); the principal two in the abstract, the introduction and the Conclusions |
| sub-fine residual "unmeasured and potentially material" (amendment 8) | Sec. VI B (i) and Sec. VI C, verbatim |
| κ-scan wording (Joseph, 2026-10-08) | Sec. VI C, unchanged |
| lost-seed disclosures 1–5 | Sec. VI D: report-only; exact deterministic reruns (16/16); none reaches T_obs, closest 4.6, next 49.8; B = 1200 for four nulls; the scope of the independent checks |
| data-informed elements and the budget extension | Sec. VI A |
| W1: no added discrimination, post hoc order | Sec. VI C (once), the abstract and the Conclusions |
| W2: exploratory, data-side only, (a)–(c) untested | Sec. VI E, the abstract and the Conclusions |
| Fig. 2: descriptive, no significance, no closure, largest-bias region | Sec. V and the Fig. 2 caption, unchanged in content (Joseph's "stands as written") |
| the adopted covariance's four measurements; no significance quoted | Sec. VII, unchanged in content |
| no 5D measurement; NOT ADMITTED branch | the abstract, the introduction, Sec. VII and the Conclusions |
| 2D band: fixed-truth failure as first built; rebuilt band not re-tested | Sec. IV B (unchanged) and the Conclusions |
| PET diagnostic | Sec. VII |
| AI-use disclosure | the Acknowledgments, verbatim (not edited); the pointer in Sec. III |
| forbidden phrasings (`CHECKLIST-20261001` §4) | none introduced: no "measurement" for the joint test, no p = 0, no "READY" |

## 6. Remaining presentation issues (not fixed in this pass, with the reason)

1. **Figure legibility.** Changing these needs the figure producers and a new release candidate, because RC6
   regenerates and checks Figs. 1–4.
   - Fig. 1: its panel fonts are very small at print size; its residual map is in bin indices; its legend shows
     `MINERvA_Tune_v1` with underscores.
   - Fig. 2: axes in cell indices; colour bars without labels.
   - Fig. 3: axis labels use multiple slashes.
2. **The body length is essentially unchanged.** Most of its length is required disclosure placed beside the claims.
   Large reductions would need the §7 placement decision.
3. **Long sentences:** 7 over 60 words remain. Several are the frozen-contract conditions of Sec. VI B, which this
   pass split only where no qualifier could be detached.
4. **The three PET references** (`technote.bib`, note-owned `@online` entries) print a linked title but no locator
   (already recorded in REVIEW-20261007 E9 for the note owners).
5. **Fig. 3 legend vs text:** the legend says "GENIE-CV"/"GENIE+MEC" and the text says "GENIE CV"/"GENIE + MEC". The
   caption ties them together. A uniform label needs the figure regenerated (item 1).
6. **Author metadata:** ORCIDs and funding were not supplied (package input 2).
7. **The `\pubhold`** for the deposit identifier waits on the separately authorized release decision.
8. **`δ_M1`** is an internal label used as a symbol. It is defined in the text, and it matches the cited repository
   records, so it was kept.

## 7. Proposed scope and policy decisions for Joseph (recorded only; nothing applied)

1. **The AI-use disclosure vs the APS policy.**
   - APS requires the "AI tool name and version". The approved text names the Claude versions but says only "OpenAI
     Codex models". The campaign review records `gpt-6-astra` sessions.
   - APS also places research uses in the methods section. The approved placement is the Acknowledgments with a pointer
     from Sec. III.
   - The text is approved verbatim, so this pass did not edit it. Decide whether to add the Codex model versions
     and/or move the disclosure into Sec. III.
2. **AI-generated images.** The APS Style Guide bars images "generated or modified by generative AI". The APS AI page
   allows AI help with data visualizations. The article's figures are plotted by analysis code that was written with
   AI assistance; no generative image model was used, as far as this pass knows. Decide whether to say so in the
   disclosure or ask the editors.
3. **Supplemental Material.** The longest operational passages could move to PRD Supplemental Material, leaving a
   one-sentence statement and a pointer beside each claim:
   - the nuisance-draw list of Sec. VI A;
   - the lost-pseudo-experiment procedure of Sec. VI D;
   - the 2D rescoring detail of Sec. IV B;
   - the E_avail-definition detail of Sec. V.

   This would shorten the body by roughly 400–600 words. It moves required disclosures away from their claims, which
   is why it is your decision and not an editorial one.
4. **The PET paragraph of Sec. VII.**
   - Option (a): keep it as is (current).
   - Option (b): reduce it to one sentence ("PET classifiers remain diagnostic and method development; no PET
     uncertainty product is adopted [35, 36]").
   - Option (c): drop PET from the article (claims map L12 allows either).

   The exploratory PET-versus-tree comparison is not needed for the article's argument.
5. **Title wording.** The applied title keeps "five-observable unfolding", which the abstract qualifies at once. An
   alternative that puts the tests first is "Calibrated joint tests of generator predictions on an unbinned
   five-observable unfolding of MINERvA inclusive charged-current neutrino data".
6. **Figure regeneration** (§6 item 1) with a new release candidate. This is presentation, but it reissues RC-verified
   files.

## 8. Builds, independent review, standalone sync

### 8a. Implementation (`da4ce85d`)

`build_all.sh` at `da4ce85d` on a clean tree: rc 0, `RESULT :: PASS … head=da4ce85d… tree=clean`, note 123 / primer 9 /
paper 11 pp, 0 BibTeX errors. The Overleaf target (`latexmk -pdf -jobname=output main_paper.tex`, separate outdir)
gave rc 0, 11 pp, 0 undefined. `test_build_all.py`: 38 passed. Pre-commit: 13 checks passed.

### 8b. Review cycle 1 (target `da4ce85d`): NOT READY, 3 blocking, 5 editorial, 3 notes

The reviewer was one fresh, read-only agent (Claude Opus 5.5, no authoring history) in the detached worktree
`MINERvA-OmniFold-prd-editorial-review-20261008`. It built only into a temporary directory, and `git status --short`
was empty afterwards. It confirmed: the rewordings in Sec. IV C, V, VI D and VII; the citations; the complete
$\mathcal{W}$ rename; the DAS placement; the verbatim AI disclosure; and no forbidden phrasing. It re-measured
pages, reference count, abstract words, body words and caption words, and all agreed.

| id | finding | disposition |
|---|---|---|
| B1 | "were generated with a corrected flux sampling" is false: the predictions were reweighted per event, not regenerated (`KNOWN_ISSUES.md` 83, 2026-10-03 update) | fixed: "use a corrected flux sampling (an exact event-by-event reweighting to the analysis flux, with added 50–100 GeV samples)" |
| B2 | the abstract dropped "report-only" (disposition §5, disclosure 1, "beside the claim") | fixed: "with every submitted pseudo-experiment observed after a report-only recovery" |
| B3 | Fig. 2 "offset $10^{-40}$" is a multiplier on the colour bar | fixed: "color-scale values in units of $10^{-40}$ cm²/nucleon" |
| E1 | the PET sentence's antecedent was reversed by the split | fixed: the baseline parenthesis restored |
| E2 | the abstract dropped "principal" (there are six conditions) | fixed |
| E3 | "marginal-normalization and injected-shape closure tests" made the normalization a closure | fixed: "marginal-normalization checks and injected-shape closure tests" |
| E4 | Fig. 3 caption: "above it" lacked an antecedent | fixed: "above the unfolded result" |
| E5 | the record's token counts were inaccurate | fixed (§3; recounted with the DAS included) |
| N1 | "under a realizable assignment of them" dropped | restored |
| N2 | the opening "more completely than one-dimensional projections" sits against "no added discrimination" | softened to a statement without a comparison |
| N3 | LightGBM pages; empty year in Ref. [8]; 0.7 pt overfull (pre-existing) | not changed: the pages and the release year are not verified from a primary source this session |
| not verified by the reviewer | the power-retention clause now covered the GENIE null as well; "admitted separately under its own criteria" added words | both restored to the baseline's scope and wording (the clause sits with the Tune v1 alternatives; "the study's remaining, separately admitted branch") |

### 8c. Review cycle 2 (target `f4669b07`): READY

All cycle-1 findings were resolved, with no new error. The reviewer re-measured: 11 pp; abstract 186 words (`pdftotext`;
this record's 185 is the same one-token gap as in cycle 1); body 5,273 against this record's 5,275 (the same +2 gap);
captions 425. Build: 0 undefined, 0 BibTeX errors, the same five pre-existing BibTeX warnings. Its one note (R1: the
caption row still said "offset") is fixed in this record. `git status --short` was empty in the reviewer worktree
after both cycles. The review budget (two cycles) is spent.
