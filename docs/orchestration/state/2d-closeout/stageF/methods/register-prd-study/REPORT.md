# How published papers in our genre present qualifications and weaknesses (2026-10-23)

**Asked for by** Joseph (2026-10-23): "characterize how other PRD papers present qualifications and weaknesses of
their method, and try to replicate them in our language". The long analysis note would then be the complete,
fully-qualified companion. He also said: "it's important to concede that perfect correctness is not always the goal of
the physics community."

**Done by** a research subagent for the director (paper-tighten lane). It was read-only on the repository. Its only
outbound contact was reading arXiv abstract pages, arXiv source tarballs and APS abstract pages.

**Our paper as measured:** origin/main 9cf49713.
- `docs/analysis-note/paper_body.tex`: blob 5868c339.
- `docs/analysis-note/main_paper.tex`: blob edcb1cbc.
- Both are unchanged at a870429c.

**CITABLE FOR:**
- how these 12 papers present limitations;
- the measured qualifier densities under the declared lexicon and its stated precision and recall;
- the style patterns;
- the drafted rewrites, as drafts.

**NOT CITABLE FOR:**
- any physics claim;
- the correctness of any rewrite: none has had the two-direction review;
- the genre as a whole: the corpus was chosen, not sampled.

**Files** (all in this directory):
- `tools/`: the scripts;
- `notes/<arXiv id>.md`: per-paper notes, with 168 machine-verified quotes;
- `abs/`: the abstract pages as read, `ABSPARSE-OUTPUT.txt` and `APS-META.txt`;
- `prose/` and `prose_full/`: the extracted text;
- `calib_*`: the calibration samples and judgments;
- `density_table.md` and `strict_index.txt`.

`src/` holds the downloaded arXiv sources (117 MB). It is input only and should not be committed.

---

## 1. Corpus

Twelve published papers. All are in PRD except three:
- two PRL ML-unfolding measurements (H1, ATLAS), included because the brief names them;
- one JINST methods paper (Wiener-SVD), the unfolding method behind MicroBooNE's results.

Anchors A, B and C of the earlier rater calibration (2504.06857, 2002.12496, 2205.05084) are reused and were
re-verified here.

**How the journal references were verified.** Every journal reference comes from the arXiv abstract page at
`https://arxiv.org/abs/<id>`, parsed by `tools/absparse.py`.
- The parser keys on the label text. arXiv renders it as "Journal&nbsp;reference". The report-number row uses the
  same `jref` CSS class, which is why an earlier parser once took a report number for a journal reference.
- Four papers have no "Journal reference" row on their abs page (marked †). For these, the DOI comes from the page's
  "Related DOI" row, and the journal, volume and page come from the `citation_*` metadata of the APS abstract page
  `https://journals.aps.org/<prd|prl>/abstract/<DOI>`, also read on 2026-10-23.
- 2108.12376 has neither a journal-reference row nor a Related-DOI row. It is matched to PRL 128, 132002 only by the
  identical title on the APS page (‡).

| # | arXiv (version read) | paper | journal reference, as read | genre and why chosen | body words |
|---|---|---|---|---|---|
| 1 | 2106.16210 (v4) | MINERvA, inclusive CC νμ vs muon kinematics at ⟨Eν⟩~6 GeV (the measurement we reproduce) | † no row; Related DOI 10.1103/PhysRevD.104.092007; APS: Physical Review D 104, 092007 (2021-11-19) | MINERvA D'Agostini; fake-data iteration study | 4,641 |
| 2 | 2110.13372 (v2) | MINERvA, inclusive CC νμ at low three-momentum transfer (Eavail, q3) | † no row; Related DOI 10.1103/PhysRevD.106.032001; APS: Physical Review D 106, 032001 (2022-08-01) | MINERvA; model dependence as a named systematic | 8,457 |
| 3 | 2002.12496 (v2) | MINERvA, double-differential inclusive CC νμ at ⟨Eν⟩~3.5 GeV | "Phys. Rev. D 101, 112007 (2020)" | MINERvA; warped-MC unfolding study | 5,409 |
| 4 | 2004.05434 (v2) | T2K, νμ CC0π on oxygen and carbon | "Phys. Rev. D 101, 112004 (2020)" | T2K; regularised and unregularised results; mock-data validations | 9,039 |
| 5 | 2102.03346 (v1) | T2K, first TKI measurement in CC1π⁺Xp | "Phys. Rev. D 103, 112009 (2021)" | T2K; unregularised fit; extreme mock-data tests | 8,005 |
| 6 | 2301.03700 (v4) | MicroBooNE, multi-differential QE-like νμ-Ar | † no row; Related DOI 10.1103/PhysRevD.108.053002; APS: Physical Review D 108, 053002 (2023-09-06) | MicroBooNE Wiener-SVD; A_C matrix; alternative-generator uncertainty | 6,158 |
| 7 | 2310.06082 (v4) | MicroBooNE, generalized kinematic imbalance on argon | "Phys. Rev. D 109, 092007 (2024)" | MicroBooNE; fake-data studies in the supplement | 5,409 |
| 8 | 2504.06857 (v2) | OmniFold on the T2K public simulated ND280 dataset | "Phys. Rev. D 112, 012008 (2025)" | OmniFold neutrino methods paper with a negative comparison (anchor A) | 6,116 |
| 9 | 2205.05084 (v2) | Bias and Priors in Machine Learning Calibrations for HEP | "Phys. Rev. D 106, 036011 (2022)" | ML methods paper whose headline is a negative result (anchor C) | 6,461 |
| 10 | 2405.20041 (v3) | ATLAS, simultaneous unbinned measurement of 24 Z+jets observables | "Phys. Rev. Lett. 133 (2024) 261803" | OmniFold measurement; usage recommendations in the supplement | 3,688 |
| 11 | 2108.12376 (v2) | H1, lepton-jet correlation with ML unfolding (MultiFold) | ‡ no row and no Related DOI; APS page title-matched: Physical Review Letters 128, 132002 (2022-03-31) | first OmniFold measurement on data | 3,407 |
| 12 | 1705.03568 (v2) | Tang et al., Data Unfolding with Wiener-SVD Method | "JINST, 12, P10002 (2017)" | unfolding-methods paper with a pros-and-cons section | 6,591 |

**Notes on the corpus:**
- **Brief's minimums met.** The corpus has 3 MINERvA papers (1-3), 2 T2K (4, 5), 2 MicroBooNE (6, 7) and 4 ML
  unfolding papers (8-11).
- **Versions.** The sources read are the latest arXiv versions. Journal typesetting may differ. Four arXiv
  "Comments" rows state the relation to the journal text:
  - 1705.03568: "match the accepted version by JINST";
  - 2108.12376: "version accepted by PRL";
  - 2205.05084: "v2: Minor updates to match journal version";
  - 2405.20041: "published in PRL".

  No paper was compared with its journal text.
- **Body words** are from the extraction of §3: the abstract plus the body, without floats, appendices or
  supplements.

---

## 2. How each paper presents qualifications and weaknesses

The full per-paper notes are in `notes/`. Each note has the five requested headings and verified quotes with their
`file:line` and section. All 168 quotes there, and every quote below, pass `tools/verify_quotes.py`, and that check
fires on a planted false quote. A quote is written as in the extracted text: `MATH` stands for inline math, `[N]`
for a citation, `N` for a reference number and `MAC` for a macro.

### 2.1 Summary table

| paper | where limitations live | model dependence / unfolding bias | failed or partial validations | scope | deferral |
|---|---|---|---|---|---|
| 2106.16210 MINERvA | in the methods paragraph where each choice is made; one two-sentence limit in the Conclusions; none in the abstract | phase-space cut "to avoid model dependence"; fake-data study, then the iteration choice | none; a wrong χ² assumption is met by reporting a log-normal χ² as well | once, as the phase-space definition | prior papers only; no supplement pointer in the text |
| 2110.13372 MINERvA | one concession sentence in the Introduction; results discussion | difference between tunes assigned as the "Signal model" systematic | none; the earlier LE result is declared "superseded" | once ("The measurement region is limited to …") | appendix (χ² table) |
| 2002.12496 MINERvA | nowhere as such | pseudodata, including warped MC, then the iteration choice | none | once, in the signal definition | none in the text, though a supplement ships with the arXiv source |
| 2004.05434 T2K | where each choice is made, with its mitigation; a dedicated validations subsection | regularisation bias conceded generically; both regularised and unregularised results reported; signal-model uncertainty | none; each named assumption is followed by "This was validated by …" | once | supplement, appendix, data release |
| 2102.03346 T2K | signal definition; validation subsection; Conclusion | unregularised fit; nuisance parameters "cover the bias" | one post-fit tension, bounded by the mock-data studies | once, as phase-space restrictions | appendix; data release |
| 2301.03700 MicroBooNE | the extraction-and-systematics section | A_C matrix "should be applied"; alternative-generator universe as an uncertainty | none, and no fake-data study is described | once, with the reason for the momentum ranges | supplement: data release, covariances, A_C, uncertainty tables |
| 2310.06082 MicroBooNE | one validation paragraph; supplement | A_C, "even though its effect is small"; fake-data study as a passed test | none | once, in the definitions | supplement; companion paper |
| 2504.06857 OmniFold-T2K | dataset limits in the dataset section; two Conclusions paragraphs | iteration as regularization; bias metric | stated plainly: "did not show strict improvement", with a cause | once; "we will refer to the fake data simply as 'data'" | code; appendix |
| 2205.05084 Bias and priors | the negative result is the headline; caveats on the authors' own method are in footnotes | the subject of the paper | the negative result, in active verbs | once ("we assume … throughout"; "we focused on one-dimensional examples") | Code and Data section |
| 2405.20041 ATLAS | the uncertainty and validation paragraphs; supplement "Usage recommendations" | "unfolding prior" and "hidden variable" uncertainty components | marginal p values inside the passing summary ("except for …, with a p-value of 0.038") | once, as the fiducial volume | supplement user guide; notebooks |
| 2108.12376 H1 | uncertainty paragraph; supplement "Note that …" sentences | Rapgap–Djangoh difference as the bias uncertainty, justified because the two bracket the data | none for the method | once ("in this first application") | supplement; HEPData |
| 1705.03568 Wiener-SVD | one labelled pros-and-cons list | "strictly model dependent", then the remedy: report the smearing matrix | a deliberately improper prior, shown as an illustration | once per toy, at its set-up | none |

### 2.2 What all twelve share

**1. No abstract states a limitation of the method.**
- The measurement abstracts end on a finding or a use. Q[2110.13372]: "The results can be used to improve models for neutrino interactions needed by neutrino oscillation experiments." (Analysis.tex:313, Abstract)
- The two methods papers whose result is negative state it as the claim, in active verbs. Q[2205.05084]: "We demonstrate how some recent proposals for both simulation-based and data-based calibrations inherit properties of the sample used for training, which can result in biases for downstream analyses." (main.tex:85, Abstract)
- The JINST methods paper announces its assessment in one clause. Q[1705.03568]: "Through a couple examples, the pros and cons of the Wiener-SVD approach as well as the nature of the unfolded results are discussed." (unfolding.tex:50, Abstract)
- **Measured** (`tools/abstract_stats.py`): no corpus abstract has more than one scope, condition or status marker,
  so none of the 60 corpus abstract sentences carries two. Our abstract has 7 such markers in 5 sentences.

**2. Scope is stated once, where it is defined, with its reason. Results sentences then carry none.**
- Q[2106.16210]: "To avoid model dependence introduced by correcting for kinematic regions without acceptance, we only report results for charged-current cross section where the muon angle with respect to the neutrino direction is less than MATH , the muon MAC is less than 4.5 GeV, and the muon MAC is between 1.5 GeV and 60 GeV." (main.tex:328, Cross Section Extraction)
- Two devices make one statement cover every later sentence:
  - a naming convention: Q[2504.06857]: "For convenience, in the rest of this article we will refer to the fake data simply as "data", as during unfolding it is treated the same way that real data would be." (main.tex:119, Test Setup)
  - the word "throughout": Q[2205.05084]: "For our analysis of simulation-based calibration, we assume N throughout." (main.tex:237, Prior Dependence and Bias)
- Where an exception is needed, it names the bin. Q[2004.05434]: "The only exception is the backward going angular bin and the highest momentum bin of the high angle slice ( MATH ), where the error can reach 10%." (JointNumuOCCC0piXsec.tex:998)

**3. Model dependence and unfolding bias become a quantity or an object, not a caveat.** Four recipes appear.
- **(a) A named uncertainty component, defined by its procedure.**
  - Q[2108.12376]: "The bias of the unfolding procedure is determined by taking the difference in the result when unfolding with Rapgap and with Djangoh." (desy21-130-with-supplement.tex:168, Uncertainties)
  - Q[2110.13372]: "Finally, an uncertainty is assigned corresponding to the difference between the cross sections extracted using the MnvTune-v1.2 model and using the new model MnvTune-v3 (Signal model, gray solid line in Fig. N)." (Analysis.tex:554, Systematic Uncertainties)
  - ATLAS says plainly where such a term dominates. Q[2405.20041]: "The unfolding uncertainty from the unfolding prior and hidden variables tends to be the dominant contributor for many observables, in particular for the ten jet substructure variables (see Figure N(d))." (l.382)
- **(b) An object handed to the user.**
  - Q[2301.03700]: "The MATH matrix should be applied to any independent theoretical prediction when a comparison is performed to the data reported in this paper." (main.tex:380)
  - The method paper behind it says why. Q[1705.03568]: "Through reporting the new smearing matrix MATH , one can avoid including the bias due to unfolding in the final uncertainties." (discussion.tex:17)
- **(c) A fake-data study followed by a decision.**
  - Q[2106.16210]: "Based on these studies, the data was unfolded using 10 iterations." (main.tex:344)
  - Q[2108.12376]: "The number of iterations is chosen such that the closure tests described below do not dominate the total uncertainty." (l.151, Unfolding method)
- **(d) A generic concession followed by its mitigation, in one sentence.** Q[2004.05434]: "Despite the care taken to avoid bias, no regularisation method can be perfect and the application of any kind of regularisation will lead to at least some bias and underestimation of uncertainties, however small; therefore both regularised and unregularised results are reported." (JointNumuOCCC0piXsec.tex:912)

**4. Validations are reported as tests: what was tested, the criterion, the outcome.**
- Q[2310.06082]: "We found that the combination of these uncertainties covered the difference between the unfolded fake data prediction and the corresponding alternative-generator theory prediction." (main.tex:692)
- Partial failures are given as numbers inside the summary sentence. Q[2405.20041]: "Chi-squared compatibility tests between the obtained measurements and the known underlying particle-level distributions for each of the 24+2 observables all yielded MATH -values MATH , except for MATH , with a MATH -value of 0.038." (l.475)
- Or as a finding with a cause. Q[2504.06857]: "Our results did not show strict improvement in terms of MATH from using OmniFold-based approaches compared to a conventional unfolding method. Moving from a binned to unbinned approach without the addition of other information yielded generally worse results, which seems to stem from imperfect neural network training." (main.tex:327, Conclusions)
- An assumption is named together with its check. Q[2004.05434]: "It should be noted that the method assumes that the distribution of toys within and between each extracted cross section bin is well approximated by a multi-variate Gaussian distribution. This was validated by analysing the ensembles of toys produced." (JointNumuOCCC0piXsec.tex:979)

**5. What was not done is stated rarely, once, as a plain fact.**
- About one or two such statements per paper. Q[2301.03700]: "Theoretical uncertainties on the models themselves are not included." (main.tex:451)
- Q[2106.16210]: "Only statistical uncertainties were considered in determining the number of iterations." (main.tex:344)
- Q[2504.06857]: "However, this is not a feasible approach for a real data analysis, since it relies on knowing the truth-level target distribution." (main.tex:250)
- **Measured:** STATUS markers ("has not been validated/measured/established", "unmeasured", "post hoc", <!-- absence-ok: quotes or discusses absence wording in the corpus or our paper; not a claim that a result does not exist -->
  "descriptive", …) have a corpus median of 0.2 per 1,000 words. A hand check of all 14 corpus STATUS hits found
  about 2 that are genuine disclaimers of the paper's own claims; the rest are definitions ("the unknown") or model
  descriptions. Ours: 5.7 per 1,000 words, nearly all genuine (§3).

**6. Secondary true caveats go where the reader uses them.**
- **Footnotes** (2205.05084). Q[2205.05084]: "One important caveat is that universality here means prior independence over the space of priors that share the same support as the training set." (main.tex:351, footnote)
- **Supplement "Note that …" sentences** (H1). Q[2108.12376]: "None of these hyperparameters were optimized and all other hyperparemeters are set to their default values." (l.370, Supplement; the misspelling is the source's)
- **User rules with thresholds** (ATLAS). Q[2405.20041]: "Each bin should contain a minimum of 5,000 effective events defined by MATH ." (l.657, Usage recommendations)
- **Pointers.** The pointer to deferred material is one plain clause. Each paper mentions a supplement, appendix or
  data release 0-12 times in its body prose (ours: 2, plus 39 note pointers). Q[2310.06082]: "More details on the systematic uncertainties and the cross-section extraction technique can be found in Ref. [N]." (main.tex:705)

**7. No paper has a dedicated limitations section.**
- The nearest are 1705.03568's labelled pros-and-cons list (discussion.tex:28) and 2504.06857's two Conclusions
  paragraphs (main.tex:327-329).
- No paper has a limitations column in a findings table, a per-result list of what is not validated, or a global <!-- absence-ok: quotes or discusses absence wording in the corpus or our paper; not a claim that a result does not exist -->
  scope paragraph written as negatives.

**8. The corpus does not aim for sentence-level correctness under adversarial reading.** This bears on Joseph's
concession. Several corpus sentences would fail our reviewers' "nothing strengthened" check.
- Q[2004.05434]: "The measurements have been done with and without the use of a data-driven Tikhonov regularisation; comparisons of the results show excellent compatibility and therefore demonstrate the absence of significant model bias in the unfolding of detector smearing effects from the data." (JointNumuOCCC0piXsec.tex:1269, Conclusions)
- Q[2102.03346]: "It has been verified that even in the case of extreme deviations from the input MC model, such as doubling the signal/background interactions or completely turning off the FSI, the cross section extraction method employed can always recover the truth values to within a 1 MATH -uncertainty." (ms.tex:890)
- **Reading (inference):** the genre tolerates claims a strict reader would qualify, because the full record (supplement,
  data release, technical note) is the correctness layer and the reader is assumed to know the conventions. We do
  not need to copy these over-strong sentences. The architecture is what should be copied: scope once, bias as a
  number, validations as tests, and the companion for the rest.

---

## 3. Measured density

### 3.1 Method (reproducible; every command runs from this directory)

```bash
python3 -I tools/tex2prose.py ours/main_paper.tex prose/ours.txt            # and the same for each src/<id>/x/<main>.tex
python3 -I tools/qcount.py table prose/ours.txt prose/<ids>.txt > density_table.md
python3 -I tools/strict_index.py prose/*.txt > strict_index.txt
python3 -I tools/abstract_stats.py ours=ours/main_paper.tex <id>=src/<id>/x/<main>.tex ...
python3 -I tools/qcount.py sample 20261023 15 15 prose/ours.txt <corpus...>  # calibration set 1
```

**Extraction** (`tex2prose.py`, the same rules for every paper):
- **Kept:** the abstract and the body, from the abstract to the first of acknowledgments, `\appendix`,
  bibliography, supplement, or `\end{document}`. `\input` files are expanded. Footnote text is kept inline in
  parentheses.
- **Dropped:** comments and floats (so captions and tables, including our Table I, are not counted), section
  headings, and all math. Inline math becomes one token, `MATH`, and display math `EQ`.
- **Tokens:** citations become `[N]` and references `N`. Our `\nsec` and `\napp` print as "Ref. [N], Sec. N".
- **Sentences** are split at end punctuation, with a protected abbreviation list.
- **Counting units:** a word is a whitespace token containing an alphanumeric character. Our paper gives 6,688 words
  in 243 sentences.

**Lexicon** (`tools/qcount.py`, `LEX`). Each category, and why it counts as a qualifier:

| category | members (regex families) | why it counts |
|---|---|---|
| SCOPE | only (not "not only"), solely, exclusively, within, under the/these/a/each…, as tested / the tested, in this configuration/study/analysis/…, in simulation, at nominal truth, except, excluding, apart from, other than, limited/restricted/confined to, as stated, in general, specified | restricts the domain of a claim. "within" and "in this …" are included because the brief asks for them, and their low precision is measured below |
| COND | under the assumption(s), assume/assumes/assumed/assuming/assumption(s), provided that/the/it, conditional(ly), conditioned, to the extent that, insofar as, if, unless, depends/dependent/dependence on | makes a claim conditional |
| STATUS | is/are/has/have (not / never) (been) {established, validated, measured, tested, shown, demonstrated, identified, evaluated, assessed, known, determined, quantified, included, …}; does not / cannot {establish, exclude, validate, determine, …}; un{measured, validated, tested, known, established, …}; no {validated, evidence, calibrated, claim, independent, significance}; we claim/make/quote/assign no; post hoc; descriptive; exploratory | disclaims or limits the evidential status of the paper's own result: the safeguard Joseph names |
| HEDGE | may, might, could, possibly, potentially, (un)likely, appear(s), suggest(s), seem(s), plausibly, presumably, perhaps, tentatively, in principle, somewhat, partly/partially, in part | epistemic softening |
| CONCESS | although, though, however, but (not "but also"), whereas, nevertheless, nonetheless | concession, the usual frame of a caveat |
| NEG | not, no, none, neither, nor, cannot, n't, without, never | the brief lists "not". Reported separately because most corpus uses are findings |
| APPROX | about, approximately, roughly, nearly, of order, around + number | counted, but **not** a qualifier: it attaches to numbers and appears in every paper of the genre |

**Matching:** matches are greedy, longest first and non-overlapping, with priority STATUS > COND > SCOPE > HEDGE >
CONCESS > NEG. So "has not been validated" counts once, as STATUS. <!-- absence-ok: quotes or discusses absence wording in the corpus or our paper; not a claim that a result does not exist -->

**Derived metrics:**
- "Sentence with a scope restriction" means at least one SCOPE or COND marker.
- A **restrictive parenthetical** is a parenthesis whose non-pointer content contains a marker, "at most" or "at
  least".
- A **pointer parenthetical** contains only a section, figure, table, appendix or reference pointer.

**Known bias of the lexicon.** It was written after reading our paper, so it catches our idioms ("the tested",
"specified", "at nominal truth", "descriptive") better than the corpus's. The calibration below measures this:
recall on ours is 0.75 against 0.42 on the corpus.

### 3.2 Calibration (hand-judged; `calib_judgments.md` has every item)

**Gold standard:** a qualifier restricts, conditions, disclaims, hedges or concedes one of the paper's own claims. A
negation that reports a physics finding, or that describes a model, is not one. There was one rater (this agent),
with no second rater.

| sample | precision | recall |
|---|---|---|
| set 1: 30 random sentences (15 ours, 15 corpus; seed 20261023), marker level, ours | 9/10 = 0.90 | 9/12 = 0.75 |
| set 1 + set 2 (30 more random corpus sentences, seed 99), marker level, corpus | 5/24 = 0.21 | 5/12 = 0.42 |
| set 3: 40 random marker instances (20 ours, 20 corpus; seed 7), precision only | ours 17/20 = 0.85; corpus 5/20 = 0.25 | - |
| set 1, sentence level (sentence has at least one qualifier) | 6/8 = 0.75 | 6/9 = 0.67 |

**What the calibration shows:**
- **The counter is accurate on our paper:** pooled precision 26/30 = 0.87.
- **It over-counts the corpus about fourfold:** pooled precision 10/44 = 0.23. Corpus "not", "but", "within" and
  "if" are mostly findings, contrasts, tolerances and mathematics.
- **It under-counts implicit corpus limitations**, for example "This comes with a cost of modest model biases".
- **Consequence:** the raw table **understates** the gap between us and the corpus.
- **Estimated true qualifier density** (count × precision / recall): about 40 per 1,000 words for ours against about
  8 for the corpus median, roughly 5× (inference; recall rests on 12 gold items per side).

### 3.3 Results (`density_table.md`, `strict_index.txt`; per 1,000 words unless marked)

| doc | words | sent. | mean sent. len. | Q | Q excl. NEG | SCOPE | COND | STATUS | HEDGE | CONCESS | NEG | sent. ≥2 Q | sent. w/ scope restr. | pointer paren. | strict index | sent. w/ strict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **ours** | 6688 | 243 | 27.5 | **34.5** | **23.2** | 10.9 | 3.7 | **5.7** | 1.2 | 1.6 | 11.4 | **28%** | **30%** | **7.9** | **16.1** | **33%** |
| 2106.16210 MINERvA | 4641 | 224 | 20.7 | 11.4 | 8.6 | 3.4 | 0.9 | 0.0 | 1.1 | 3.2 | 2.8 | 4% | 8% | 0.2 | 2.4 | 5% |
| 2110.13372 MINERvA | 8457 | 375 | 22.6 | 14.3 | 9.9 | 4.0 | 0.7 | 0.2 | 2.4 | 2.6 | 4.4 | 5% | 10% | 0.1 | 2.7 | 6% |
| 2002.12496 MINERvA | 5409 | 237 | 22.8 | 14.4 | 10.5 | 5.4 | 0.7 | 0.2 | 1.7 | 2.6 | 3.9 | 4% | 13% | 0.0 | 3.5 | 8% |
| 2004.05434 T2K | 9039 | 321 | 28.2 | 17.0 | 13.1 | 6.0 | 2.3 | 0.1 | 2.2 | 2.4 | 4.0 | 12% | 20% | 0.8 | 3.5 | 9% |
| 2102.03346 T2K | 8005 | 347 | 23.1 | 17.4 | 12.5 | 6.0 | 1.0 | 0.1 | 3.2 | 2.1 | 4.9 | 7% | 15% | 0.1 | 3.4 | 7% |
| 2301.03700 MicroBooNE | 6158 | 284 | 21.7 | 7.1 | 5.7 | 2.8 | 0.5 | 0.3 | 1.3 | 0.8 | 1.5 | 2% | 6% | 0.5 | 1.3 | 3% |
| 2310.06082 MicroBooNE | 5409 | 248 | 21.8 | 15.0 | 10.7 | 2.6 | 3.3 | 0.2 | 1.1 | 3.5 | 4.3 | 5% | 10% | 1.3 | 3.3 | 6% |
| 2504.06857 OmniFold-T2K | 6116 | 233 | 26.2 | 16.5 | 11.4 | 2.8 | 0.8 | 0.0 | 2.9 | 4.9 | 5.1 | 9% | 8% | 0.0 | 1.6 | 4% |
| 2205.05084 Bias/priors | 6461 | 339 | 19.1 | 26.9 | 21.5 | 2.8 | 9.3 | 0.2 | 4.0 | 5.3 | 5.4 | 10% | 21% | 0.0 | 4.2 | 7% |
| 2405.20041 ATLAS | 3688 | 151 | 24.4 | 11.9 | 6.8 | 4.1 | 0.3 | 0.0 | 1.6 | 0.8 | 5.2 | 5% | 10% | 0.8 | 2.2 | 5% |
| 2108.12376 H1 | 3407 | 144 | 23.7 | 12.6 | 10.0 | 5.0 | 0.3 | 0.3 | 2.1 | 2.3 | 2.6 | 6% | 10% | 0.0 | 1.8 | 4% |
| 1705.03568 Wiener-SVD | 6591 | 291 | 22.6 | 9.4 | 6.2 | 2.1 | 1.7 | 0.6 | 1.1 | 0.8 | 3.2 | 3% | 8% | 1.2 | 2.4 | 5% |
| **corpus median [min, max]** | | | 22.7 [19.1, 28.2] | 14.4 [7.1, 26.9] | 10.3 [5.7, 21.5] | 3.7 | 0.8 | 0.2 [0, 0.6] | 1.9 | 2.5 | 4.1 | 5% [2, 12] | 10% [6, 21] | 0.2 [0, 1.3] | 2.6 [1.3, 4.2] | 5.5% [3, 9] |

**Column notes:**
- The strict index drops every low-precision marker found in calibration: all NEG, CONCESS and HEDGE, plus "within",
  "if", "depend… on", "in this …", "in general" and "other than".
- Restrictive parentheticals (0.6 for ours; corpus median 0.4) and APPROX (2.7; corpus 1.1) are in
  `density_table.md`.

**Abstracts only** (`tools/abstract_stats.py`):
- Ours: 135 words in 5 sentences, with 10 markers (74 per 1,000 words). 7 of them are SCOPE, COND or STATUS, in 4 of
  the 5 sentences.
- Corpus: 0-3 markers per abstract (0-22 per 1,000). Eight of the twelve abstracts have no SCOPE, COND or STATUS
  marker at all; the other four have one each.

**Reading:**
- **Out of the corpus range.** On every qualifier metric, our paper is outside the corpus range, not just above its
  median:
  - Q per 1,000 words: 34.5, against a corpus maximum of 26.9. That maximum is Bias-and-priors, whose count is
    inflated by the mathematical "if" (COND 9.3).
  - Strict index: 16.1, against 4.2.
  - Sentences with two or more qualifiers: 28%, against 12%.
  - STATUS: 5.7, against 0.6.
  - Pointer parentheticals: 7.9, against 1.3. These are the 39 "Ref. [N], Sec. N" pointers to the note in the body
    prose; there are 46 `\nsec`/`\napp`/note citations in the source, counting captions and tables.
- **Mean sentence length** (27.5 words) is at the top of the corpus range (T2K has 28.2). It is not an outlier.
- **The largest ratios** are STATUS (about 25× the median) and pointers (about 40×). These are the two things the
  corpus almost never does: say what has not been established, and route the reader elsewhere mid-sentence.
- **HEDGE and CONCESS** are at or below the corpus median. So the problem is not modal softening ("may", "could").
  It is scope, condition and status clauses attached to results.

---

## 4. Patterns to replicate: a style guide derived from the corpus

Each rule names the corpus examples it is drawn from (§2.2 numbers in brackets). "Ours" names the current practice it
replaces.

**R1. State the scope once, as a definition, with its reason, in Sec. I and the abstract. Then results sentences carry
no scope** [2.2-2].
- Use a naming convention so later sentences stay short: "In what follows, 'the five-observable result' means the
  central value of configuration (a) under the observable definitions of Sec. II" (after 2504.06857 main.tex:119;
  "throughout" after 2205.05084 main.tex:237).
- *Ours:* the Sec. I scope paragraph (paper_body.tex:104-121) is written as five sentences of negatives, and its
  content is then repeated per sentence ("at the tested truths", "in simulation", "under the specified …",
  "configuration (a) only").
- **Rewrite the scope paragraph in positive form:** what the paper measures, with which estimators, under which
  simulation. Keep the negatives that change meaning, such as "not a validated five-observable measurement" and
  "hybrid nulls".

**R2. Collect the limitations in one place, and say each once** [2.2-7: the corpus has no limitations section, but
1705.03568's pros-and-cons list and 2504.06857's conclusion paragraphs are the model].
- Because our paper is a validation study, one short "Limitations" subsection (proposed: the end of Sec. VI, or Sec.
  VIII) is the faithful equivalent. Write it as a numbered list of plain declaratives, each with its consequence.
- Table I's "Principal limitation" column then becomes redundant. Either drop it or keep it and drop the
  per-sentence versions. **Do not print the same limitation in three places** (Table I, the result sentence, the
  conclusions), as now.

**R3. Turn a bias into a number, a component or an object, not a caveat** [2.2-3a/b].
- **Where an analysis change is in scope** (Joseph decides): carry the purity-subtraction bias, or the
  generator-shape residual, as a named uncertainty component, as in H1 (Rapgap–Djangoh), MINERvA "Signal model" and
  ATLAS "unfolding prior".
- **Where it is not:** state the bias once with its size, and say once that it is not in the quoted uncertainty
  (E6).
- **The envelope** already follows this pattern. Present it as a defined component (E8), not as "under the specified
  envelope prescription".

**R4. Report each validation as a test: tested what, against what, criterion, outcome** [2.2-4].
- Failures are outcomes and need no apology.
- Write "51 of the 153 cell and projection integrals have a 68% coverage whose upper confidence bound lies below the
  0.66 threshold, with coverage as low as 0.06". The bound must stay: dropping it would change the test.
- Do not write "miscover at the tested truths, most strongly when …" followed by a sentence on what was not
  established.
- Give the diagnosis in one sentence. The "inferred from a Gaussian fit … rather than measured directly" detail goes
  to the note.

**R5. Name each assumption once, next to the check that addresses it, or say it is untested, once** [2.2-4, the <!-- absence-ok: quotes or discusses absence wording in the corpus or our paper; not a claim that a result does not exist -->
2004.05434:979 pattern].
- Our A1 and A2 fit this exactly (paper_body.tex:895-898).
- Delete the later restatements: :993-1002 and the conclusion. The one exception is the theorem's hypothesis, which
  stays (E10).

**R6. Disclosures of what was not done: one sentence each, in the Limitations list or at the point of the choice**
[2.2-5].
- About 1-3 per paper in the corpus. We have about 38 STATUS markers in the body.
- Keep the ones a reader needs to use or interpret a released object correctly:
  - the 2D coverage not tested;
  - the omitted covariance terms;
  - the post-selection of the learner;
  - no recoil-response band;
  - fine-grid convergence not shown.
- Move the rest (the earlier bands, the out-of-scope lists, "the recomputation verifies the calculation, not …") to
  the note.

**R7. Point to the companion note about once per subsection, at the end of a paragraph, as a plain clause** [2.2-6].
- For example: "Construction details, the earlier bands and the seed studies are in Ref. [note], Secs. X-Y"
  (2310.06082:705; 2004.05434:1042).
- *Ours:* 39 pointers in the body prose, most of them mid-sentence parentheticals.
- Put minor true caveats in the note or in footnotes, as "Note that …" sentences (H1 supplement; 2205.05084
  footnotes).

**R8. Keep the abstract to findings, plus at most one framing clause** [2.2-1].
- State the negative findings as findings, in active verbs (2205.05084; 2504.06857).
- The abstract keeps only the qualifiers whose absence would make it false (E1: "hybrid null", "no evidence of").

**R9. Definition before claim, instead of a condition clause after it.**
- "We define the envelope …; with it, none of the three reporting schemes reaches 10%" (E8), after 1705.03568's
  per-toy set-up sentence (xs.tex:55).
- The conditionality is carried by order, not by "under the …".

**R10. Prefer two sentences to one sentence with a semicolon and a caveat clause.**
- Our mean sentence length (27.5) and our share of sentences with two or more qualifiers (28%) go together.
- The corpus splits a result and its exception into a result sentence and an exception sentence (2405.20041:475;
  2102.03346:950).

**What the corpus does not do that we do:**
1. A **limitations column** in a findings table, alongside a scope paragraph and per-sentence caveats, so the same
   limitation is stated three times.
2. **Claim-status disclaimers** ("has not been independently validated", "is not established", "unmeasured", "a <!-- absence-ok: quotes or discusses absence wording in the corpus or our paper; not a claim that a result does not exist -->
   post hoc observation"): 5.7 per 1,000 words against 0.2.
3. **Out-of-scope lists** ("What unbinned information could recover, the coverage failure, and the validity of any
   interval lie outside its scope").
4. **Histories of superseded constructions** in the paper body: the earlier statistical bands.
5. **Mid-sentence pointers** to a companion, about 40 times the corpus rate.
6. **Pre-emptive denials of over-readings** ("The independent recomputation verifies the calculation, not whether …";
   "the scan … bounds neither the actual residual nor the convergence"). The corpus trusts the reader's conventions.
7. **Repetition of a condition** in the abstract, the scope paragraph, the result sentence and the conclusion (for
   example the recoil-response omission and fine-grid convergence).

**What we do that the corpus also does, and should keep:**
- disclosing a post hoc choice next to the choice (2504.06857:250);
- naming an untested assumption once (2205.05084:237); <!-- absence-ok: quotes or discusses absence wording in the corpus or our paper; not a claim that a result does not exist -->
- stating a negative result plainly (2205.05084; 2504.06857).

---
## 5. Ten worked examples from our paper

Source: `docs/analysis-note/paper_body.tex` and `main_paper.tex` at origin/main 9cf49713 (blobs 5868c339 and edcb1cbc;
unchanged at a870429c). The ten were picked from the top of the per-sentence marker ranking (`tools/qcount.py`) and
cover the abstract and Secs. II, IV, V, VI and VII D.

Each rewrite keeps every number. "Destination" names where each qualifier that leaves the sentence would go:
- **[S]**: the Sec. I scope paragraph (paper_body.tex:104-121);
- **[L]**: a proposed single "Limitations" subsection, which would replace the scattered per-sentence caveats and
  Table I's last column;
- **[N]**: the companion note, at the section the paper already cites.

**KEEP** marks a qualifier that cannot move without making the sentence false as read, even with the global scope
statement.

The rewrites are drafts in the corpus register. They are not reviewed text. Each still needs the two-direction review
of the register method (nothing lost, nothing strengthened).

### E1. Abstract, main_paper.tex:80-84 and :96-101

> Pseudo-experiments reveal background-subtraction bias, incomplete recovery of generator-sized truth changes, and
> statistical undercoverage at the tested truths; under the specified envelope prescription, no tested reporting
> definition meets our 10% precision criterion. As an illustration, simulation-calibrated tests of hybrid null
> hypotheses for five generator predictions all reject at the 5% familywise level. They are not physical exclusions,
> show no evidence of gain over matched coarse projections, omit calorimetric recoil-response uncertainty, and assume
> fine-grid convergence; NuWro's total (rate-and-shape) rejection is not robust to a hydrocarbon-target correction.

**Corpus-style rewrite:**

> In pseudo-experiments, the background subtraction biases the highest-W cells by up to 4%, generator-sized changes
> of the truth are only partly recovered, and the statistical intervals undercover. With a model-dependence envelope
> added to the uncertainty, none of three tested five-observable reporting schemes reaches a 10% median precision. We
> also show how tests can be calibrated when intervals cannot be validated, by simulating the full analysis chain at
> each hypothesis. Tests of hybrid null hypotheses built from five generator predictions, calibrated within the
> simulation's detector model, all reject at the 5% familywise level, with no evidence of additional discrimination
> over matched coarse projections.

**Where each qualifier goes:**
- "at the tested truths": the sentence-initial "In pseudo-experiments" carries it, and [S] states it in full.
- "under the specified envelope prescription": restated as the condition "With a model-dependence envelope added".
  **KEEP** in that form: the 10% verdict depends on the prescription.
- "hybrid null hypotheses": **KEEP**. Without it, "tests ... of five generator predictions all reject" reads as
  rejecting the generators.
- "not physical exclusions": [S] (paper_body.tex:117-118) and Sec. VII.
- "omit calorimetric recoil-response uncertainty": compressed to "within the simulation's detector model"; the
  detail goes to Sec. VII D (ii) and [L].
- "assume fine-grid convergence": Sec. VII D (i) and [L].
- "no evidence of gain over matched coarse projections": **KEEP** "no evidence of". Writing "no gain" would assert
  an absence the study does not show.
- The NuWro hydrocarbon clause: Sec. VII E. **Flag:** the source comment at main_paper.tex:87 records that
  `DECISION-20261020-joseph-nuwro-ch-claim.md` (provisional) placed this clause in the abstract, so moving it needs
  Joseph's ruling.
- **Number check:** "up to 4%" and "three" were checked against paper_body.tex:490 ("biased by up to 4%") and :718
  ("two of the three tested reporting definitions").

### E2. paper_body.tex:178-184 (the 135 MeV constant)

> Relative to the charged-pion mass, it moves 0.67% of simulated events into another true-Eavail bin and changes no
> true-Eavail bin by more than 1.05%, an effect whose materiality is not established because it has not been
> assessed against the covariance (note).

**Rewrite:**

> Replacing it by the charged-pion mass would change no true-Eavail bin by more than 1.05% (note).

**Where each qualifier goes:**
- The 0.67% bin-migration figure goes to [N].
- "materiality not established ... not assessed against the covariance" goes to [N]. It could also go to [L] as one
  line in a list of effects "not propagated".
- Movable, **provided the rewrite adds no "negligible"**. A model rewrite once invented exactly that claim (handoff
  §1). This is how the corpus treats a definitional choice (see 2110.13372 notes): define it once and give its size,
  with no materiality hedge.

### E3. paper_body.tex:355-371 (the 2D chi-square)

> ...computed with the pseudo-inverse of the published covariance over the 205 bins, which keeps all 205 eigenmodes
> (rank 205, condition number 1.5e12), so that ndf is that rank; we use it only as a descriptive distance. It
> indicates a correlated shape difference, not a normalization difference, spread over many eigenmodes of the
> published covariance, with no single pT or p|| band carrying more than 15% of it; its source has not been
> identified. ... This learner was chosen after both comparisons were known, so the benchmark is a reproduction
> rather than an independent validation.

**Rewrite:**

> Against the full published covariance (all 205 eigenmodes kept), the descriptive distance is chi2/ndf = [value]. The
> difference is in shape, not normalization, and is spread over many eigenmodes, with no single pT or p|| band
> contributing more than 15%. ... We quote the LightGBM result, whose covariance uses the same estimator; it was
> selected after both comparisons had been made.

**Where each qualifier goes:**
- "descriptive": **KEEP** as one adjective. The two results share data, so a reader must not convert the value to a
  p value.
- The condition number and the pseudo-inverse go to [N].
- "its source has not been identified" goes to [L].
- The post-selection disclosure: **KEEP** the fact. It prevents "we quote the LightGBM result" from implying a blind
  choice.
- The inference "reproduction rather than independent validation" goes to [L] and Table I.

### E4. paper_body.tex:441-457 (the 2D statistical block)

This is a 6-sentence paragraph. Four of its sentences concern two earlier bands that are not the quoted block,
including a post hoc rescoring.

**Rewrite:**

> The statistical block is a bootstrap of 300 replicas at the central value's training seed, with the background
> templates resampled; its median is 0.684%. Its coverage, and that of the total, has not been tested (Sec. VIII). <!-- absence-ok: quotes or discusses absence wording in the corpus or our paper; not a claim that a result does not exist -->

**Where each qualifier goes:**
- The earlier-band history (the pre-specified test, the undercoverage, the post hoc rescoring and why it is not
  independent) goes to [N]. This is the r12 rule for chronology, applied to the remaining case.
- The 0.26-sigma replica-mean offset goes to [N].
- "has not been tested": **KEEP** in the paper, in this sentence or in [L]. [S] covers only the three- to <!-- absence-ok: quotes or discusses absence wording in the corpus or our paper; not a claim that a result does not exist -->
  five-observable intervals, so nothing else in the paper says the 2D block is untested. <!-- absence-ok: quotes or discusses absence wording in the corpus or our paper; not a claim that a result does not exist -->
- Corpus precedent: no measurement paper in the corpus reports a superseded uncertainty construction. All report the
  final one and its test (see the T2K and MicroBooNE notes).

### E5. paper_body.tex:461-470 (status of the 2D covariance)

> Its intervals, bias, and covariance have not been independently validated: we claim no coverage, either on
> independent simulated samples or simultaneously over all reported bins and projections, and the covariance provides
> no calibrated significance for generator comparisons. The covariance omits the approximation in the
> systematic-universe unfoldings, the dependence on the machine-learning estimator (Sec. IV A), and the dependence on
> the unfolding model and its regularization, and it assumes that the detector response varies only within its
> parametrized family (note).

**Rewrite** (pattern from 2301.03700, "Theoretical uncertainties on the models themselves are not included."):

> The covariance does not include the learner dependence of Sec. IV A, the dependence on the unfolding model and its
> regularization, or the approximation in the systematic-universe unfoldings.

**Where each qualifier goes:**
- "not independently validated / we claim no coverage ... simultaneously over all bins and projections" goes to [L],
  once.
- "provides no calibrated significance for generator comparisons" goes to [L]. **KEEP** somewhere in the paper,
  because readers will otherwise compute chi2 p values with it.
- "detector response varies only within its parametrized family" goes to [N]. Every systematic-universe covariance in
  the corpus makes this assumption without stating it.
- The omission list stays: **KEEP** it as one plain sentence. It is what a user of the released covariance needs.

### E6. paper_body.tex:487-492 (closure with backgrounds)

> End-to-end pseudo-experiments that include the purity-based background subtraction reproduce the input at nominal
> truth except in the highest-W cells, which are biased by up to 4% in simulation, about one quoted standard deviation
> in one (Eavail,W) cell; the quoted uncertainties omit this bias (Fig. 2).

**Rewrite:**

> With the purity-based background subtraction, pseudo-experiments at nominal truth close except in the highest-W
> cells, where the bias reaches 4%, about one standard deviation in one (Eavail,W) cell (Fig. 2). This bias is not
> included in the quoted uncertainties.

**Where each qualifier goes:**
- "in simulation" is removed. "Pseudo-experiments" already says it, and Sec. III states it globally
  (paper_body.tex:336-338).
- "except in the highest-W cells": **KEEP**. It is the result.
- "the quoted uncertainties omit this bias": **KEEP** as its own sentence.
- **Analysis option, not a wording fix:** the corpus would carry this bias as an uncertainty component (2301.03700
  adds an alternative-generator universe; 2102.03346 uses nuisance parameters that "cover the bias") or as an
  A_C-style object. Either would remove the caveat altogether, but either is a change to the results and needs
  Joseph's decision.

### E7. paper_body.tex:634-643 (seed dependence)

> ...in two further covariances built at two seed settings, changing the seed moves the projected uncertainty by about
> 6.1%, against a stability limit of [bound]%. This rests on one seed pair, and the spread over seed pairs has not
> been measured; five bands built at a fixed seed, which carry [x]% of sqrt(Tr C), cannot vary with it, so their seed
> sensitivity, which could move the total in either direction, is also unmeasured. <!-- absence-ok: quotes or discusses absence wording in the corpus or our paper; not a claim that a result does not exist -->

**Rewrite:**

> For one pair of seed settings, the projected uncertainty moves by 6.1%, beyond the [bound]% stability limit; we
> therefore quote no covariance-based significance for the generator comparisons.

**Where each qualifier goes:**
- "rests on one seed pair": **KEEP**, folded into "for one pair of seed settings". Without it, 6.1% reads as the
  general seed sensitivity.
- "spread over seed pairs not measured" is implied by "one pair", and the detail goes to [N].
- The five fixed-seed bands' unmeasured seed sensitivity ("either direction") goes to [N], with one line in [L]. <!-- absence-ok: quotes or discusses absence wording in the corpus or our paper; not a claim that a result does not exist -->

### E8. paper_body.tex:660-666 (precision target)

> Under the specified envelope prescription, none of the reporting definitions of a five-observable measurement tested
> in a dedicated study meets our 10% precision target. The envelope of a cell is the largest shift ... ; it is a
> sensitivity diagnostic that tracks the regularization bias, not an interval, and the study adds it linearly to the
> probabilistic half-width.

**Rewrite** (define first, then state the result, as 1705.03568 does at each toy set-up):

> To include model dependence, we define the envelope of a cell as the largest shift of its data result when the
> simulation's prior is reweighted to each of five generator-sized changes of the truth, and add it linearly to the
> probabilistic half-width. With the envelope included, none of the three reporting definitions we studied reaches
> the 10% median half-width we set as a target.

**Where each qualifier goes:**
- "Under the specified envelope prescription": **KEEP** the dependence, but carry it by order (definition before
  claim) rather than by a qualifier clause.
- "a sensitivity diagnostic ..., not an interval" goes to [N]. One clause can stay if the reviewers judge that "add
  it linearly" invites reading the sum as a confidence interval.
- "tested in a dedicated study" becomes "we studied".

### E9. paper_body.tex:743-751 (the binned-unfolding diagnostic)

> The diagnostic is binned, signal-only and noise-free, with the detector response fixed at the simulation's, on those
> same truth changes, and covers only the residuals whose diagnosis is stable under the truth resolution (38% of the
> joint-cell residuals above 2%). What unbinned information could recover, the coverage failure, and the validity of
> any interval lie outside its scope. Within that scope, the residual is consistent with the regularization of the
> inverse problem at this binning and prior, rather than with the tree approximation of the classifiers (note).

**Rewrite:**

> For the residuals whose diagnosis is stable under the truth resolution (38% of the joint-cell residuals above 2%),
> this binned, noise-free, signal-only comparison attributes the residual to the regularization of the inverse
> problem at this binning and prior, not to the tree approximation of the classifiers (note).

**Where each qualifier goes:**
- "binned, signal-only and noise-free" and the 38% population: **KEEP**, as adjectives of the comparison. The claim
  is false without its population.
- "detector response fixed at the simulation's" is covered by the Sec. III global statement (paper_body.tex:336-338).
- "on those same truth changes" is already in the paragraph's first sentence (:732-733).
- The sentence listing what lies outside scope goes to [N]. The corpus never lists what a study does not address.
  **Flag:** this paragraph sits inside a CLAIM-ADDITION block (:725-753) whose record is "NOT CITABLE FOR a coverage
  result or an interval". The rewrite makes no such claim, so the out-of-scope sentence is not needed to honour the
  record. The director should confirm that reading.
- **Wording check:** "consistent with ... rather than" became "attributes ... not to". That may strengthen the claim.
  If the review judges it does, keep "is consistent with".

### E10. paper_body.tex:993-1002 (calibration validity) and :1093-1095 (conclusions)

> The calibration is valid for the simulated null to the extent that the pseudo-experiment chain reproduces the
> analysis applied to the data, which is assumption A1. The simulation-size check of condition (iv) is not a test of
> the data process: every pseudo-experiment resamples the same simulated events, so the null distributions are
> conditional on that simulation, and their conditioning on the data-derived lateral shifts has not been validated. <!-- absence-ok: quotes or discusses absence wording in the corpus or our paper; not a claim that a result does not exist -->
> The independent recomputation verifies the calculation, not whether the chain reproduces the data analysis, and no
> rejection rate has been measured for null pseudo-data processed like the data, which would require an independent
> simulation sample.

**Rewrite** (pattern from 2205.05084 and 1705.03568: state the assumption once, plainly, with what would test it):

> The calibration assumes that the pseudo-experiment chain reproduces the analysis of the data (A1). Testing A1 would
> require null pseudo-data from an independent simulation sample processed like the data; the pseudo-experiments here
> all resample the same simulated events and use lateral detector shifts derived from the data.

**Where each qualifier goes:**
- "The simulation-size check is not a test of the data process" and "The independent recomputation verifies the
  calculation, not ..." go to [L]. Both disclaim over-readings that the corpus would leave to the reader. One
  [L] bullet ("A1 is untested") covers both. <!-- absence-ok: quotes or discusses absence wording in the corpus or our paper; not a claim that a result does not exist -->
- "conditional on that simulation" is kept as a fact ("all resample the same simulated events").
- In the conclusions (:1093-1095), "the decision rule controls the familywise error rate at 5% provided the
  calibration is exact": **KEEP** "provided the calibration is exact". It is the theorem's hypothesis, and the
  sentence is false without it.

### Tally

| | count |
|---|---|
| qualifier instances that move to [S], [L] or [N] | 24 |
| instances that must stay (**KEEP**) | 14, in the forms shown, some folded into a compact form |
| items needing a decision before moving | the NuWro abstract clause (E1), the CLAIM-ADDITION scope sentence (E9) |
| analysis options rather than wording fixes | E6 (bias as an uncertainty component) |

---

## 6. Recommendation

**Adopt the corpus's architecture, not its looseness.**
- **Scope.** State the scope once, positively, in Sec. I and in one abstract clause.
- **Limitations.** Collect them in one short numbered Limitations subsection, each stated once as a plain
  declarative, and drop either Table I's limitation column or the per-sentence repetitions.
- **Biases.** Turn biases into numbers, named components or defined envelopes.
- **Validations.** Report each as a test with its criterion and outcome.
- **Note pointers.** Point to the companion note about once per subsection, at a paragraph's end. Move to the note
  the histories, the out-of-scope lists and the pre-emptive denials of over-readings.

**Why.** The measured gap is large and it is specific. On every qualifier metric our paper lies outside the range of
twelve published papers in its genre:
- 34.5 qualifier markers per 1,000 words, against a median of 14.4; after correcting for the counter's precision and
  recall, about 5×;
- 28% of sentences with two or more qualifiers, against 5%;
- claim-status disclaimers about 25× the median;
- mid-sentence note pointers about 40× the median.

Modal hedging and sentence length are not the problem.

**The concession Joseph asked for.** The corpus does not try to make each sentence correct under adversarial
reading; some of its sentences would fail our review (§2.2-8). It relies on conventions and on its companion
material for completeness. Our analysis note can play that role for us.

**The guardrail stays.** Of the 38 qualifier instances in the ten worked examples, 14 (about a third) cannot leave their
sentence without making it false as read:
- the hybrid null;
- "no evidence of";
- "provided the calibration is exact";
- the population of the diagnostic;
- one seed pair;
- the post-selected learner;
- the envelope's definition.

These stay, in compact form.

**Two items need a ruling before they move:** the NuWro clause in the abstract (DECISION-20261020) and the
CLAIM-ADDITION out-of-scope sentence.

**One item is an analysis choice, not a wording fix:** carrying the purity-subtraction bias as an uncertainty
component.

**Suggested next step.** Run one register round under the existing method (fresh writer, fact ledger, two-direction
review, P2 against r13), using §4 R1-R10 as the brief. Keep §5's KEEP list as hard constraints.

## 7. Limits of this study

- **One rater.** One rater (this agent) judged the calibration. Recall rests on 12 gold items per side.
- **Lexicon bias.** The lexicon was written after reading our paper, which biases recall in our favour (measured:
  0.75 against 0.42). The precision correction runs the other way, and the strict index is robust to both.
- **Corpus selection.** The corpus was chosen for methods-validation content, not sampled. Two of its papers are
  PRL letters and one is in JINST.
- **Extraction.** Our Table I (the limitations column) and all captions are excluded from the counts. Our measured
  density is therefore, if anything, an underestimate.
- **Drafts.** The section 5 rewrites are unreviewed. E9's verb ("attributes") may strengthen the claim.

---

**Committed by the director (2026-10-23).** Our paper was measured at `origin/main` `9cf49713`
(`docs/analysis-note/main_paper.tex`, `paper_body.tex`; unchanged at `a870429c`); the scratch copies under `ours/` are
not committed, to keep one version. The downloaded corpus sources and extracted texts (`src/`, `prose/`,
`prose_full/`, `abs/`) are third-party material and are not committed; `INPUTS.sha256` lists each file's sha256, and
the corpus table gives each paper's arXiv id, so they can be fetched again. `tools/verify_quotes.py` needs `prose/`.
