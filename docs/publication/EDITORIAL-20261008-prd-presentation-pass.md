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

### 8d. Final builds, revised PDF, standalone sync and remote heads

| | |
|---|---|
| canonical build at `f4669b07` (clean tree; `docs/analysis-note` is identical at the record-only commits after it) | `build_all.sh` rc 0, `RESULT :: PASS … head=f4669b07… tree=clean`; note 123 / primer 9 / paper 11 pp; 0 BibTeX errors |
| revised PDF (local; not sent) | `../MINERvA-OmniFold-prd-editorial-pdf-20261008/MINERvA-OmniFold-PRD-article-editorial-f4669b07.pdf`, 11 pp, sha256 `6d81cfea…` (the digest includes the build date). The baseline build for comparison is beside it (`…-baseline-b612ee3a.pdf`, `0f62fc7f…`). It shows the one red `[HOLD: …]` for the deposit identifier. |
| standalone before the copy | a fresh worktree of `MINERvA-OmniFold-Analysis-Note` `origin/main` `e1af61e3` equalled canonical `b612ee3a` `docs/analysis-note` in all 115 shared tracked files (`cmp`); only its own `.gitignore` and `AGENTS.md` differ |
| standalone sync | `main_paper.tex`, `paper_body.tex` and `publication.bib` copied from `f4669b07` to the standalone branch **`sync-prd-editorial-pass-20261008`**, commit **`687b48ab345ca2cfa39af85e3d087978e6472c01`**. Afterwards every tracked file equals canonical (`cmp`). Standalone `build_all.sh` rc 0 at 123 / 9 / 11 pp (`head=unknown` is the documented fallback); Overleaf target rc 0, 11 pp, 0 undefined. `pdftotext` of all three PDFs is identical to the canonical build. |
| why a branch | the canonical PR stays unmerged by instruction, so standalone `main` stays equal to canonical `main`. The branch should merge together with the canonical PR. |
| remote heads (`git ls-remote`, 2026-10-08) | `MINERvA-OmniFold`: main = `b612ee3ac9b517c56e1153223576b7c3f5dcd32a`, `docs/prd-editorial-pass-20261008` = `f4669b07…` before this record's commits. `MINERvA-OmniFold-Analysis-Note`: main = `e1af61e3cc5d571be97e10f5e759ccf9afdabfd2`, `sync-prd-editorial-pass-20261008` = `687b48ab345ca2cfa39af85e3d087978e6472c01`. |

### 8e. Closeout (`CAMPAIGN-REVIEW-20260929.md` §6 item 7)

| item | value |
|---|---|
| owner | Claude Opus 5.5 (`claude-opus-5-5`), session `3df6bbfa-2fb6-47ba-a147-f5d566eb0e92`; the effort setting is not exposed to the session |
| helpers | one research agent (web, read-only) for §2; one fresh read-only reviewer for §8b–§8c |
| input commits | canonical `b612ee3a`; standalone `e1af61e3` |
| output commits | canonical `da4ce85d` (implementation) → `f4669b07` (cycle-1 repairs) → record-only commits; standalone `687b48ab` |
| compute | none (local LaTeX builds only) |
| inference cost | unavailable |
| accepted consequential findings | B1–B3 (§8b) |
| residual issues | §6; the scope decisions in §7 |
| decision resolved | the article is presentation-ready for Joseph's readthrough, with the §7 decisions his |

## 9. Joseph's follow-up (2026-10-08, this session) and what it changed

**His words:** "Sure, there should be mention of claude code too. I am willing to fix rerun to fix the hard to read
figures." This answers §7 items 1 and 6. §6 item 1 and §7 items 1 and 6 are superseded by this section. Items 2–5 of
§7 stay open: images policy, Supplemental Material, PET paragraph, title.

**AI-use disclosure (Acknowledgments).**
- It now names the agents and gives model versions, as APS requires ("AI tool name and version"): "…used through the
  Claude Code and OpenAI Codex command-line agents: Anthropic Claude (Opus 4.7, 4.8, 5 and 5.5; Fable 5 and 5.1) and
  OpenAI GPT models (GPT-5.5, GPT-5.6 Sol and Luna, GPT-6 Astra and GPT-6.1), including those used for independent
  review."
- The rest of the approved text is unchanged, and so is its placement.
- **The OpenAI list comes from the repository's records, which are incomplete by construction:**
  - `gpt-6-astra` reviewers (campaign review §3, runtime metadata checked there);
  - `gpt-5.6-sol` and `gpt-5.6-luna` Codex lanes (commit messages, e.g. `9413a8cb`);
  - GPT-6.1 rewriting note sections (`76e8d90e`);
  - `gpt-5.5` in the idea-rate benchmark (`FINDINGS-ARCHIVE-2026-08.md`);
  - `codex-cli` (commit messages).

  **Confirmed by Joseph, 2026-10-08, in this session: "The AI list is correct."**

**Figures 1–3 redrawn** from the released figure arrays (`fig_arrays.npz`, sha256 `72394a2b…`, the RC4/RC6 file), with
`publication/release/figs/make_figs.py`. The article now prints that script's output, so the release regenerates the
printed figures and not only their quantities.

| figure | change |
|---|---|
| Fig. 1 | full width; journal-size type; ratio panels to the published projection with its ±1σ band (from the published covariance in the arrays); residual map with bin-edge labels; the inset numbers drawn in the figure (they reproduce the printed 6.87 % / 6.85 %, 0.089 / 0.598) |
| Fig. 2 | one column with the two panels stacked; bin-edge axes; labelled colour bars (ratio; difference in units of $10^{-40}$ cm²/nucleon); each cell's value printed (the printed ranges 12–30 % and 23–31 % can now be read off the figure) |
| Fig. 3 | units without multiple slashes; legend labels as in the text (GENIE CV, GENIE + MEC, NuWro 21.09, GiBUU 2019); larger type |

- **Unchanged:** the numbers the figures show and every printed value. `fig_numbers.py` still binds them to
  `values.tex`.
- The PDFs carry no timestamp. Two runs with the `requirements-lock.txt` versions (matplotlib 3.11.2, numpy 1.26.4,
  scipy 1.15.2, CPython 3.11.15) give identical bytes: Fig. 1 `938c4fc9…`, Fig. 2 `57f3cc60…`, Fig. 3 `e9d1bb01…`.
- The note and primer keep their own figure files (`model_comp_projections`, `paper_joint_localization`), so they are
  unchanged.
- The page count is unchanged (11). Fig. 1 now takes about two-thirds of a page.

**Release candidate 7** (README `docs/publication/release/RC7-README.md`): RC6 with the new figure code. Its data and
macro files are unchanged. Its identity, reproducibility and verification are recorded in §10.

## 10. RC7: identity, reproducibility and verification (local; not deposited, tagged or sent)

| | |
|---|---|
| tarball | `minerva-omnifold-article-release-rc7.tar.gz`, 15,745,698 bytes, 33 files, sha256 **`27f0caba53c4bbf75310f6d94145ea872ebe77c6a6f55ef48298d95cbcee566e`** (`docs/publication/release/RC7-SHA256SUMS.txt`) |
| source commit | `8fa79cb1`; payload = the RC6 data files, checked against `RC4-SHA256SUMS.txt` |
| byte-reproducible | yes: two builds from a detached clean checkout of `8fa79cb1` gave the same sha256 |
| difference from RC6 | `code/figs/make_figs.py` and `README.md` only. Every `data/` and `expected/` file is identical (checksum lists compared). |
| verification | from an empty directory with the `requirements-lock.txt` versions: `shasum -c SHA256SUMS` OK; `verify_rc.py` rc 0, **`VERIFY: PASS`** (frozen and union replays AGREE with 0 differences; W1 0 differences; figure numbers PASS; negative control OK; Figs. 1–4 regenerated; condition (i) 4/4), 407 s |
| printed figures | `make_figs.py` run from the extracted package reproduces the article's three figure files byte for byte (`938c4fc9…`, `57f3cc60…`, `e9d1bb01…`) |
| location | local: `../MINERvA-OmniFold-prd-editorial-pdf-20261008/`. Not copied to CFS. RC6 stays the preserved candidate on CFS until Joseph decides. |
| review | **not independently reviewed.** The two authorized review cycles (§8) covered the editorial diff before §9–§10. |

**Standalone re-sync after §9–§10:** `main_paper.tex`, `paper_body.tex` and the three new figure files copied from
`eff6a8b3` to `sync-prd-editorial-pass-20261008`, commit **`41eb42d780843f0d1e5041bd9bef2a76cd1a6514`**. Every
canonical `docs/analysis-note` file equals the standalone copy (`cmp`). Standalone `build_all.sh` rc 0 at
123 / 9 / 11 pp, and `pdftotext` of all three PDFs is identical to the canonical build. Standalone `main` is unchanged
at `e1af61e3`. The revised PDF is `../MINERvA-OmniFold-prd-editorial-pdf-20261008/MINERvA-OmniFold-PRD-article-editorial-8fa79cb1.pdf`.

## 11. PET removed from the article; paragraph lengths (Joseph, 2026-10-08)

**PET.** Joseph: "yes drop PET from the letter" (the article). This supersedes §7 item 4.
- The Sec. VII paragraph on full-event point-cloud (PET) classifiers, with its three references, is removed.
- No result, figure or conclusion of the article depended on it. The claim map allows dropping it (row L12), and
  the 2026-08-20 ruling requires only that PET read as diagnostic wherever it appears.
- The companion note keeps the PET record.
- The three PET references were also the ones printing without a locator (§6 item 4), so that issue is gone.
- Measured after the removal:
  - body text (texcount) 5,000 → 4,884 words;
  - references 37 → 34;
  - "PET" occurs 0 times in the rendered article;
  - 11 pp.

**Paragraph lengths.** The table counts the five comparable papers' arXiv HTML (LaTeXML `ltx_para`) and this
article's source. Both columns count words, with each inline math expression as one word, and exclude the abstract,
captions, lists, acknowledgments, appendices and references. The methods are equivalent but not identical. LaTeXML can
split a paragraph at a displayed equation.

| paper | paragraphs | median | mean | p90 | max | > 150 words |
|---|---:|---:|---:|---:|---:|---:|
| Ruterbories et al. (MINERvA), PRD 104, 092007 | 41 | 110 | 119 | 198 | 262 | 27% |
| Abe et al. (T2K), PRD 103, 112009 | 62 | 130 | 140 | 230 | 612 | 35% |
| Acero et al. (NOvA), PRD 107, 052011 | 44 | 131 | 153 | 222 | 400 | 43% |
| Huang et al. (T2K OmniFold), PRD 112, 012008 | 39 | 144 | 162 | 256 | 363 | 49% |
| Abratenko et al. (MicroBooNE), PRD 110, 013006 | 151 | 148 | 156 | 227 | 319 | 47% |
| **this article** (after §11) | 37 | **133** | 144 | 256 | 288 | 41% |
| this article at the baseline `b612ee3a` | 36 | 140 | 150 | 258 | 299 | 44% |

The article's paragraphs are within the range of the comparison set: the median is mid-range and the 90th percentile
equals the T2K OmniFold paper's.

**Standalone re-sync after §11:** `main_paper.tex` and `paper_body.tex` copied from `72998cdd`; standalone branch
`sync-prd-editorial-pass-20261008` = **`63d3cd1cbce3bc5e0b29d95e703138e6b9b5b449`**. Every tracked file equals canonical (`cmp`);
standalone `build_all.sh` rc 0 at 123 / 9 / 11 pp; `pdftotext` of all three PDFs identical to the canonical build. Standalone
`main` unchanged at `e1af61e3`; canonical `main` unchanged at `b612ee3a`.

## 12. Image sentence added; title kept (Joseph, 2026-10-08)

Joseph: "add the image sentence, use the current title". This closes §7 items 2 and 5. **No §7 item remains open.**
- **Disclosure (Acknowledgments):** added "The figures were drawn by plotting code from the analysis outputs; no
  image was generated or edited by a generative-AI image tool."
  - It answers the APS Style Guide's bar on images "generated or modified by generative AI or AI-assisted tools",
    beside the APS AI policy's allowance for AI help with data visualizations (§2a).
  - The rest of the disclosure is as in §9 (tool list confirmed by Joseph).
- **Title:** unchanged, "Unbinned five-observable unfolding of MINERvA inclusive charged-current neutrino data and
  calibrated joint tests of generator predictions".

## 13. Merged to both mains (Joseph, 2026-10-08)

Joseph: "coordinate with the implementer session to merge everything onto main and the analysis note only repo".

**Coordination.** The implementer session replied with no objection to this lane's merge. It holds its own branches:
- `followup/prd-release-g11-g12-20261008` is in progress. Joseph told that session directly to deliver it as a
  reviewed, unmerged PR, so it is not merged.
- The read-only audit branch `audit/prd-release-repro-20261008` had no merge authorization. Merging it is Joseph's
  call.
- `analysis/gbdt-model-dependence-20261003` in the note repository is neither lane's.

The implementer's G11 checker passes 14/14 on this article's text.

| | |
|---|---|
| `MINERvA-OmniFold` | PR #56 merged with a merge commit: main = **`dd0515feeb5fee51972bc124e4ef1d3a7d7ed0bf`** (parents `b612ee3a`, `31f55222`) |
| `MINERvA-OmniFold-Analysis-Note` | main fast-forwarded `e1af61e3` → **`657d5bd3c841a65750e7f45471db9cf32d22e7a5`** (= `sync-prd-editorial-pass-20261008`) |
| post-merge check | `build_all.sh` at `dd0515fe` in a fresh detached worktree: rc 0, `RESULT :: PASS … tree=clean`, 123 / 9 / 11 pp. All 117 tracked `docs/analysis-note` files at `dd0515fe` equal Analysis-Note main `657d5bd3` (`cmp`). |
| final article PDF (local; not sent) | `../MINERvA-OmniFold-prd-editorial-pdf-20261008/MINERvA-OmniFold-PRD-article-editorial-31f55222.pdf` (the article sources at `dd0515fe` are those of `31f55222`) |
| release | RC7 `27f0caba…` stays local; RC6 stays the preserved candidate on CFS. Nothing was deposited, tagged, submitted or sent. |
