# The second independent scope review: what the measurement-framed paper should keep, shorten or move (2026-10-27)

**Under:**
- `DECISION-20261027-joseph-5d-integration-then-second-scope-review.md` item 3: a second independent scope review,
  under the first's rules;
- `DECISION-20261027-joseph-f1-reprice-and-scope-review-before-r19.md` item 2: it runs now, on the #413 draft, before
  the merge.

**Run by** the paper-tighten lane, as director.

**MEASURES:** nothing. It is advice from a model, recorded as given.

**CITABLE FOR:** what the review recommended, from which inputs.

**NOT CITABLE FOR:**
- what published papers do. Its literature claims are its own, and only the identities of the papers it names are
  checked below;
- any adoption. Nothing moves on its advice. The move of the joint tests is Joseph's decision.

## How it was run

- **Model and account:** `gpt-6-astra`, reasoning `high`, sandbox `read-only`, on `codex-school2`
  (`CODEX_HOME=~/.codex-school2`, rc 0). The run log, like the first review's, is not committed (`*.log` is ignored); its sha256
  begins `b93c464f415e8f73`. Both accounts are on the delegation allow-list.
- **Inputs** (`inputs/`, digests in `SHA256SUMS`):
  - the paper's printed text: pdftotext of `main_paper.pdf` built from #413 at `a55e2686` (`BASE.txt`), with its two
    hold spans visible, as in the first review;
  - the note's pages 1–4 (title page, abstract, executive summary) and its `.toc` file, from the same build;
  - the prompt (`PROMPT.md`).
- **The prompt** is the first review's, with three changes:
  - the paper is described as framed as a measurement paper, about 10,000 words;
  - the 5D description (`5d-addition.md`) is dropped, because the result is now in the paper;
  - a neutral question 4 on structure is added: whether the section order and an introductory summary table (Table I)
    are typical of comparable measurement papers.
- **Not given:**
  - the first review's answer;
  - the paper rewrite lane's candidate list or any ranking;
  - the director's recommendation, the corpus section counts, and any rater score.
- **Web access:** the reviewer opened three public arXiv pages (2106.16210, 2504.06857, 2110.13372; run log lines
  4911–4951). It read nothing internal beyond the inputs.
- **The answer:** `answer.txt`, 3,620 words, verbatim.

## What it recommends, in brief

1. **Organize the paper around the sixteen-cell measurement.**
   - Bring a compact numerical result table into the paper.
   - Explain the uncertainty construction, C_total + C_resp, and what each component represents.
   - Put the fake-data study (Table IV) at the centre.
2. **MOVE the hybrid-null joint-testing programme** (VII C–F, Table VI), its decision rule, lost pseudo-experiments,
   convergence, power and robustness studies, and remove the "all ten reject" claim from the abstract. This is the
   first review's recommendation again.
3. **MOVE** the exact-binned diagnostic (VI, Table III) and several studies of earlier configurations. **SHORTEN** most
   of the 2D benchmark, the background, deformation and coverage studies, and the reporting-definition study.
4. **KEEP** the run-period inconsistency and the joint-test estimator's rounding instability, because that estimator
   produces the headline result.
5. **Structure:** the order is "poorly matched to a measurement paper". The result first appears as subsection V F,
   and its comparison is in VII B.
   - **Table I** "resembles an analysis-note findings register". It omits the sixteen-cell measurement and includes
     the hybrid-null tests. Remove it from the introduction.
   - **The recommended order:** Introduction; data, simulation and observables; cross-section extraction;
     uncertainties and validation; the sixteen-cell result with its comparisons; discussion and conclusions.
6. **Length:** 7,000–8,000 words, excluding references. This is its own estimate.

## Checked by the director

- **Two claims about our documents, checked against the #413 build:**
  - Table I has no sixteen-cell row and does have "all ten hybrid-null tests reject at 5% familywise". Confirmed.
  - The note's abstract says "Its principal result is a cross section in five observables" (`inputs/note-front.txt`
    line 17), but its executive summary says "The main results are the validation findings" (line 51). Confirmed: the
    two disagree.
- **The joint-test estimator is the headline result's estimator** (the paper's Sec. III text, beside Table II).
  Confirmed, so its rounding instability bears on the sixteen-cell result.
- **The six papers it names, on their arXiv abstract pages (2026-10-27):**
  - titles and first authors match the answer for 2106.16210 (Ruterbories), 2110.13372 (Ascencio), 2504.06857
    (Huang), 2405.20041 (ATLAS), 2108.12376 (H1) and 1911.09107 (Andreassen);
  - journal-reference rows: 1911.09107 reads "Phys. Rev. Lett. 124, 182001 (2020)", 2405.20041 "Phys. Rev. Lett. 133
    (2024) 261803", and 2504.06857 "Phys. Rev. D 112, 012008 (2025)";
  - the other three have no journal-reference row. Their journals were verified through the DOI in
    `register-prd-study/REPORT.md` §1: PRD 104, 092007; PRD 106, 032001; and PRL 128, 132002.

## Not changed

- The paper and the note. This record moves nothing.
- The hybrid-null joint-test move is still only "seriously considered". This review and the first come to Joseph
  together, and the secondary-results decision is his.
- Claims, KI-85, `\pubhold`, data-availability and release text are Joseph's. Nothing is submitted, deposited or
  tagged.
