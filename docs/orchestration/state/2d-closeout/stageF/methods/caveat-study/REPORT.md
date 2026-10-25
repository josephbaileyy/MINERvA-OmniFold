# How comparable published documents handle caveats, and the rules that follow for the paper and the note (2026-10-25)

**Asked for by** Joseph (`DECISION-20261025-joseph-prd-caveat-convention.md`): "the paper should handle it the same
way similar length PRD papers do and the note should handle it the same way similar length notes do".

**Done by** the paper rewrite lane, for the director. It is read-only on the repository. Its only outbound contact was
reading arXiv abstract pages and PDFs. The coding was done by Claude subagents of this session, one per document,
under one codebook. Every quote was verified mechanically against the document text.

**CITABLE FOR:**
- how these nine published documents state caveats, as measured under `CODEBOOK.md`;
- the same measures for our paper (register round r17 with its accuracy fixes) and our note (origin/main `fe92211c`);
- the per-document rules in §5.

**NOT CITABLE FOR:**
- any physics claim;
- the genre as a whole: the comparators were chosen to fit a length band and a genre, not sampled;
- exact rates: two coders of one comparator differ by 25% in row count (§2.4).

**Files** (this directory):
- `CODEBOOK.md`: the coding instructions every coder followed.
- `inv/<doc>.tsv`: the inventories, one row per caveat statement, each with a verified verbatim quote.
- `tables/rates.md` and `tables/placement.md`: the tables of §3.
- `tools/`:
  - `fetch.sh`: arXiv abstract pages and PDFs;
  - `blindcount.py` and `blind_note.py`: blinding and word counts;
  - `tally.py`: quote verification and tables. Run it as `CAVEAT_WORK=<dir holding blind/> python3 -I
    tools/tally.py`. Its `--self-test` plants two false quotes and two true ones.
- `ABSPARSE-OUTPUT.txt`: the abstract-page rows as read.
- `INPUTS.sha256`: the blinded texts that were coded. The texts themselves are not committed.

---

## 1. Corpus

**How lengths were measured.**
- One rule for every document (`tools/blindcount.py`):
  - start at the PDF text (pdftotext), at the abstract's first line;
  - keep the body, the captions and the appendices;
  - drop the title and authors, the acknowledgments, the reference list, any supplement, arXiv stamps, DOI lines
    and page numbers.
- Our note is cut the same way by `tools/blind_note.py`, which also drops its table of contents.
- By this rule our paper is 8,785 words. Its rater copy is 9,348 words, because the rater copy keeps the
  data-availability text.
- Anchors A–C measure 7,703, 7,980 and 8,038 words. Their rater copies were 8,148, 8,992 and 8,583
  (`rater-calibration/REPORT.md` §1). The two rules differ by under 12%, and every anchor is inside the band either
  way.

**How identities were verified.**
- Each identifier, version and journal reference was read from the labelled rows of the arXiv abstract page
  (`ABSPARSE-OUTPUT.txt`).
- Three documents have no journal-reference row (†):
  - 2301.03700 and 2110.13372: the journal reference is from the Related-DOI row. `register-prd-study/REPORT.md`
    §1 confirmed both on their APS pages.
  - 1612.05824: the journal reference is from its Related-DOI row, `10.1088/1748-0221/12/02/P02017`.

**Set P: PRD papers of 7,000–12,000 words in the genre.** Six papers.

| # | arXiv (version) | document | journal reference | genre | words |
|---|---|---|---|---|---|
| P1 | 2504.06857 (v2) | OmniFold on the T2K public ND280 simulation (anchor A) | Phys. Rev. D 112, 012008 (2025) | ML unfolding, neutrino | 7,703 |
| P2 | 2002.12496 (v2) | MINERvA double-differential inclusive CC νμ, ⟨Eν⟩ ≈ 3.5 GeV (anchor B) | Phys. Rev. D 101, 112007 (2020) | neutrino cross section, unfolding | 7,980 |
| P3 | 2205.05084 (v2) | Bias and priors in ML calibrations for HEP (anchor C) | Phys. Rev. D 106, 036011 (2022) | ML methods for HEP | 8,038 |
| P4 | 2301.03700 (v4) | MicroBooNE multi-differential QE-like νμ–Ar | † Phys. Rev. D 108, 053002 | neutrino cross section, Wiener-SVD | 9,321 (main text; supplement cut) |
| P5 | 2110.13372 (v2) | MINERvA inclusive CC νμ at low three-momentum transfer | † Phys. Rev. D 106, 032001 | neutrino cross section, unfolding | 10,310 |
| P6 | 2102.03346 (v1) | T2K transverse kinematic imbalance in CC1π⁺Xp | Phys. Rev. D 103, 112009 (2021) | neutrino cross section, unregularised fit | 11,922 |

**Set N: published technical documents of 30,000 words or more.** Three documents.

| # | arXiv (version) | document | journal reference | kind | words |
|---|---|---|---|---|---|
| N1 | 2101.03779 (v3) | T2K oscillation analysis with 3.13×10²¹ POT | Phys. Rev. D 103, 112008 (2021) | long PRD analysis paper | 30,678 |
| N2 | 1612.05824 (v2) | Design and construction of the MicroBooNE detector | † JINST 12 (2017) P02017 | JINST technical paper | 31,016 |
| N3 | 2007.06722 (v4) | First ProtoDUNE-SP performance results from a beam test | JINST 15 (2020) P12004 | JINST technical paper | 35,620 |

**Measured and not used:**
- **1502.01550** (T2K, PRD 91, 072010), the note's earlier rater anchor: 26,893 words, below the 30,000-word floor.
- **1706.04965** (CMS particle flow, JINST 12, P10003): 29,148 words, below the floor.
- **1211.0469** (T2K flux, PRD 87, 012001): 17,507 words.
- **2004.05434** (T2K CC0π on O and C, PRD 101, 112004): 14,225 words, above the paper band.
- **1607.00704** (NuMI flux, PRD 94, 092005): 6,265 words.
- **2108.08219** (NOvA, PRD 106, 032004): 5,101 words.
- **2310.06082** (MicroBooNE GKI): not measured, because the blinding rule did not find its abstract in this layout.
  Six papers already met the set's minimum of four.

**Our documents:**
- **The paper.** Register round r17 as it will merge: the scored text plus the three accuracy fixes. 8,785 words.
- **The note.** The build of origin/main `fe92211c`, 121 pages. 53,018 words in all; the appendices start at "Guide
  to the appendices".

## 2. Method

### 2.1 The five kinds

These are the five kinds of the decision, defined for coding in `CODEBOOK.md`:

| kind | what it covers |
|---|---|
| (a) history | superseded work, development narrative |
| (b) deviation | a departure from a predeclared or planned procedure, or a choice made after seeing data or results |
| (c) untested or omitted | an untested property, an omitted effect, an undemonstrated assumption |
| (d) scope | a restriction of the domain of a claim |
| (e) process | internal process vocabulary |
<!-- absence-ok: names the caveat category "untested or omitted" used to classify statements; not a claim that any result is absent from the repository -->

**What counts.** A caveat counts only if it qualifies the document's own method, result or claim. Plain uncertainty
values and statements about other people's work do not count.

### 2.2 Fields

Each statement is recorded with:
- its kind;
- its placement: abstract, intro, inline, syst, limits, concl, appendix, or caption (captions include footnotes);
- whether it leads with the positive;
- whether it carries a number;
- whether the document turns it into an assigned uncertainty;
- an issue label, so that restatements of one caveat can be counted;
- an exact quote.

### 2.3 Coding and verification

- One coder (a Claude subagent) read each whole document. The note was coded in two parts, body and appendices.
- **Verification:** `tally.py` keeps a row only if its quote is a substring of the document text, after whitespace
  is collapsed and line-end hyphens are joined. **All 1,787 rows passed.**
- **Counting unit:** one statement per sentence and kind. Where a coder split one sentence into several issue
  rows, the rows are merged. This affects only our paper (207 rows → 201). The same sentence printed again
  elsewhere, such as a repeated caption, stays a separate statement.

### 2.4 Coder agreement

Two documents were coded twice, by independent coders:

| document | coder 1 | coder 2 | rows matched by the other coder |
|---|---|---|---|
| our paper | 201 rows | 195 rows | 93% and 94% |
| P5 | 80 rows | 60 rows | 71% and 95% |

- **P5 by kind:** coder 1 found a 27, b 7, c 33, d 13; coder 2 found a 17, b 5, c 30, d 8.
- **What this means:** rates are reliable to roughly ±25%. Every difference reported below is much larger than
  that.

### 2.5 Mechanical measures

The coders' positive-first judgments were too lenient to compare: they called 77–100% of rows "positive" in every
document. Two measures computed the same way for every document are reported instead:
- **negation word:** the quote contains not, no, none, neither, nor, cannot, never, without or un-tested;
- **number:** the quote contains a digit or %.

## 3. Results

### 3.1 Rates, per 1,000 words (`tables/rates.md`)

| document | words | (a) | (b) | (c) | (d) | (e) | all | distinct issues | statements per issue | negation word | assigned |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P1 2504.06857 | 7,703 | 0.00 | 0.52 | 3.51 | 3.25 | 0 | 7.27 | 4.54 | 1.60 | 25% | 2% |
| P2 2002.12496 | 7,980 | 0.25 | 0.00 | 1.00 | 1.13 | 0 | 2.38 | 1.38 | 1.73 | 21% | 11% |
| P3 2205.05084 | 8,038 | 0.00 | 0.00 | 1.74 | 3.73 | 0 | 5.47 | 2.74 | 2.00 | 23% | 0% |
| P4 2301.03700 | 9,321 | 0.32 | 0.00 | 1.72 | 1.29 | 0 | 3.33 | 1.61 | 2.07 | 6% | 10% |
| P5 2110.13372 | 10,310 | 2.62 | 0.68 | 3.20 | 1.26 | 0 | 7.76 | 3.39 | 2.29 | 22% | 5% |
| P6 2102.03346 | 11,922 | 0.59 | 0.00 | 1.85 | 2.35 | 0 | 4.78 | 2.43 | 1.97 | 30% | 14% |
| **P range** | | 0–2.6 | 0–0.7 | 1.0–3.5 | 1.1–3.7 | **0** | **2.4–7.8** | **1.4–4.5** | 1.6–2.3 | 6–30% | 0–14% |
| **our paper (r17)** | 8,785 | 0.46 | 0.91 | **13.3** | **7.6** | 0.57 | **22.9** | **10.0** | 2.28 | **35%** | 8% |
| N1 2101.03779 | 30,678 | 1.04 | 0.07 | 2.71 | 0.98 | 0 | 4.79 | 2.51 | 1.91 | 24% | 28% |
| N2 1612.05824 | 31,016 | 0.06 | 0.13 | 1.03 | 0.90 | 0 | 2.13 | 1.55 | 1.38 | 17% | 0% |
| N3 2007.06722 | 35,620 | 0.11 | 0.42 | 1.68 | 0.95 | 0 | 3.17 | 2.27 | 1.40 | 26% | 8% |
| **N range** | | 0.1–1.0 | 0.1–0.4 | 1.0–2.7 | 0.9–1.0 | **0** | **2.1–4.8** | **1.6–2.5** | 1.4–1.9 | 17–26% | 0–28% |
| **our note** | 53,018 | 1.15 | 0.77 | **10.0** | **5.2** | 1.06 | **18.2** | **8.4** | 2.17 | **50%** | 3% |

**What the rates show:**
- **Our paper** states caveats about 3× as often as the most-caveated PRD comparator (22.9 against 7.8 per 1,000
  words) and 4.5× the median (5.1).
- **Our note** states caveats about 4× as often as the most-caveated long comparator (18.2 against 4.8).
- **The gap is in the number of distinct caveats, not in repetition.**
  - Our paper has 10.0 distinct caveats per 1,000 words, against 1.4–4.5; it restates each 2.28 times, against
    1.6–2.3 (median 2.0).
  - The note has 8.4 distinct caveats per 1,000 words, against 1.6–2.5; it restates each 2.17 times, against
    1.4–1.9.
- **Untested-or-omitted (c) and scope (d) make up 94% of our paper's excess** over the set-P mean rates.
- **Process vocabulary (e) is zero in all nine comparators.** It is 0.57 per 1,000 words in our paper and 1.06 in our
  note.
- **More of our caveats contain a negation word:** 35% in the paper and 50% in the note, against medians of 22% (P)
  and 24% (N).
- **Fewer of our caveats are turned into an assigned uncertainty:** 8% in the paper and 3% in the note, against up
  to 14% (P) and 28% (N). In set N, 28% of the (c) caveats become an assigned uncertainty.
<!-- absence-ok: names the caveat category "untested or omitted" used to classify statements; not a claim that any result is absent from the repository -->

### 3.2 Placement, by set and kind (% of that kind's statements; `tables/placement.md`)

| set | kind | n | abstract | intro | inline | syst | limits | concl | appendix | caption |
|---|---|---|---|---|---|---|---|---|---|---|
| P | (a) | 39 | 0 | 3 | 85 | 3 | 0 | 8 | 0 | 3 |
| P | (b) | 11 | 0 | 9 | 82 | 0 | 0 | 9 | 0 | 0 |
| P | (c) | 120 | 0 | 2 | 68 | 8 | **0** | 8 | 5 | 10 |
| P | (d) | 117 | 4 | 3 | 59 | 2 | **0** | 15 | 1 | 15 |
| our paper | (c) | 117 | 2 | 3 | 68 | 0 | **18** | 1 | 0 | 9 |
| our paper | (d) | 67 | 6 | 13 | 61 | 0 | **15** | 0 | 0 | 4 |
| N | (a) | 38 | 3 | 21 | 55 | 8 | 0 | 5 | 0 | 8 |
| N | (b) | 21 | 0 | 0 | 81 | 0 | 10 | 5 | 0 | 5 |
| N | (c) | 175 | 1 | 2 | 66 | **17** | 5 | 4 | 0 | 6 |
| N | (d) | 92 | 3 | 9 | 65 | 4 | 3 | 4 | 0 | 11 |
| our note | (a) | 61 | 0 | 3 | 30 | 20 | 0 | 3 | **41** | 3 |
| our note | (c) | 531 | 2 | 6 | 41 | 8 | 8 | 4 | **22** | 8 |
| our note | (d) | 278 | 4 | 8 | 38 | 3 | 5 | 6 | **26** | 12 |
| our note | (e) | 56 | 0 | 2 | 36 | 11 | 0 | 5 | **39** | 7 |

**What placement shows:**
- **No PRD comparator has a limitations section or list.** No heading in the six texts names limitations, and no
  coder placed a caveat in one. They put
  caveats inline, where the method or result is described (62–85%), and restate the principal ones in the
  conclusions (8–16%). Our paper puts 15–18% of its (c) and (d) caveats in Sec. VI, VII D and the VIII A list.
- **PRD abstracts carry scope, not omissions:**
  - (d) in the abstract: 4% in set P;
  - (c) in the abstract: 0% in set P;
  - (c) in the abstract: 2% in our paper.
- **The long comparators keep (c) with their uncertainties.** 17% of their (c) caveats sit in systematics sections.
  They keep history in the introduction or a dedicated "updates since the previous result" passage (21% of (a); N1
  Sec. IV). They put almost no caveat in an appendix. Our note puts 22–41% of each kind in its appendices; its
  history (a) and process (e) are concentrated there.

## 4. How each kind is phrased (verbatim; `[placement]`)

### (a) History

**Comparators.** Every coded (a) statement is about previously published results or earlier model versions, and it
is framed as an improvement or a supersession. No coded (a) statement in the nine describes an earlier version of the
document's own validation that failed. A search of the nine texts for "earlier version", "previous version",
"initially" and "first version" finds only hardware and algorithm history (N1, N2, N3).
- P5 [intro]: "incorporates both empirical and theoretical improvements to modeling since the original publication,
  and incorporates improvements to the neutrino flux prediction and detector simulation."
- N1 [abstract]: "Significant improvements have been made to the neutrino interaction model and far detector
  reconstruction."
- P6 [inline]: "This results in a significant improvement with respect to previous T2K cross-section analyses [60,
  61] where the uncertainty was around 8.5% [62]."

**Ours.** Paper [inline]: "A coverage test specified in advance scored an earlier version of the statistical band,";
paper [caption, Table I]: "an earlier band failed coverage".

### (b) Deviation and data-informed choices

**Comparators.** Rare: 2 of 6 PRD papers and 3 of 3 long documents. A choice is stated as the method's choice,
together with its basis, at the point where it is made. A long document states an operational deviation with its
consequence. None uses "post hoc" for its own choices, or says who saw what and when. The one occurrence in the nine texts (P3)
describes the field's practice: uncertainties "computed post-hoc".
- P1 [inline]: "We choose a cutoff of 20 iterations for IBU-UniFold and 45 iterations for the OmniFold methods."
- N1 [limits]: "This case was chosen as it gave the best agreement between data and predictions in Tab. XI."
- N3 [inline]: "The electron diverters were therefore left unpowered. A resistive path to ground on each one ensured
  that the actual voltage on the outer electrode was close to zero, which was not the intended voltage."

**Ours.** Paper [inline]: "This learner was chosen after both comparisons were known."; "Its reviewers had already
seen descriptive per-cell residuals of the data."

### (c) Untested or omitted
<!-- absence-ok: names the caveat category "untested or omitted" used to classify statements; not a claim that any result is absent from the repository -->

**Comparators.** An assumption is stated as an assumption, in the active or passive voice. An omitted effect comes
with its reason. The important ones become assigned uncertainties: P 15% and N 28% of (c).
- P2 [inline]: "The axial form factor is assumed to have a dipole form and an axial vector mass of"
- P1 [inline]: "Due to limitations of the data release, this is not the full list of backgrounds typically included
  in a T2K analysis."
- P6 [inline, assigned]: "additional model uncertainties are added (discussed in Section VI B) to allow a variation
  of the input simulation in regions of the underlying particle kinematics where the efficiency is not f[lat]"

**Ours.** Paper [abstract]: "Pseudo-experiments reveal background-subtraction bias, incomplete recovery of
generator-sized truth changes, and statistical undercoverage at the tested truths." The most restated caveat in the
paper is "no calorimetric hadronic-response band" (12 statements). In the note it is the unassigned residual
regularization bias (20).

### (d) Scope

**Comparators.** Scope is a positive definition: what is measured, the phase space, the dataset, the conditions. It is
placed in the abstract, the signal definition and the captions.
- P4 [inline]: "The QE-like signal definition used in this analysis includes all νµ -Ar scattering events with a
  final-state muon with momentum 0.1 < pµ < 1.2 GeV/c, and exactly one proton with 0.3 < pp < 1 GeV/c."
- P1 [inline]: "the rest of this article we will refer to the fake data simply as “data”, as during unfolding it is
  treated the same"
- P3 [abstract]: "whereas prior-independent data-based calibration remains an open problem."

**Ours.** Paper [abstract]: "simulation-calibrated tests of hybrid null hypotheses for five generator predictions all
reject at the 5% familywise level". 37% of the paper's (d) statements carry a negation word, against 14–19% in the
comparator sets.

### (e) Process vocabulary

**Comparators.** None in nine documents. A search of the nine texts for pre-registration, "predeclared", "fixed
before", "specified in advance", "blind analysis" and "unblind" finds no match. None of them reports a predeclared
test.

**Ours.** Paper [inline]: "Configuration (e) keeps five iterations by a criterion fixed in advance."; "The test
design was fixed before any observed statistic was computed." Note: "which leaves the recorded decisions standing".

## 5. Rules

They replace the provisional table of the decision's item 3 where they differ. The guardrails of item 4 are unchanged:
- a qualifier stays where leaving it out would make a printed sentence false as read;
- no number or claim changes, and no fact leaves both documents;
- agy agrees on every printed passage;
- the pairwise comparison and P1 decide adoption.

### 5.1 The paper (from set P)

| | rule | provisional | change |
|---|---|---|---|
| R-P1 | **State each caveat once, where the thing it qualifies is described.** Restate only the principal ones in the conclusions, as prose. The paper's restatement rate (2.28 per caveat) should fall to the corpus median (2.0). | (c) "stated once" | adds the placement and the measured target |
| R-P2 | **No limitations list.** No PRD comparator has one. The VIII A items go back inline at the result each qualifies. Sec. VIII then restates the principal limitations in a short prose paragraph. | — | **new** |
| R-P3 | **(a) History leaves the paper.** Where a superseded result bears on a reported one, say what the reported result improves on or supersedes, in one sentence, positive-first. Point to the note. | leaves; prints in the note | adds the "improves on / supersedes" framing |
| R-P4 | **(b) A data-informed choice is stated as a choice, with its basis, once, at the choice.** For example, "We use LightGBM, chosen after the comparisons with the publication." Then state the consequence where a reported result depends on it. Do not use "post hoc", and do not say who saw what. | one sentence at the result, with consequence | adds the choice-with-basis form. The D1 disclosures stay, in this form. |
| R-P5 | **(c) An assumption is stated as an assumption** ("assumes …", "is taken to be …"). An omitted effect is stated with its size or bound where one exists, and with its reason. Lead with what holds. The share of caveats containing a negation word (35%) should fall toward the corpus median (22%). | plain declarative, quantified | adds assumption form, reason, and the measured target |
| R-P6 | **(d) Scope is a positive definition**, in the abstract, Sec. I and the definitions: what is measured and on what. A negative scope statement is used only where a reader would otherwise infer the broader claim, and only once. | once, abstract and Sec. I | adds positive-definition form |
| R-P7 | **(e) Process vocabulary is removed.** Where pre-specification bears on a validity claim (the joint tests), it is stated once as a property of the method ("The statistic and decision rule were fixed before the data were examined"). Outside the joint tests, "fixed in advance", "specified in advance" and "predeclared" are removed. | removed | adds the one exception the joint tests need |
| R-P8 | **The abstract carries scope only.** Omissions and untested properties go in the body. | — | **new, for Joseph:** the abstract is protected text |
| R-P9 | **The measured gap.** Even with R-P1 to R-P7 applied, the paper's distinct caveats (10.0 per 1,000 words) stay above the corpus range (1.4–4.5). The comparators carry fewer distinct caveats because they report fewer secondary results. A register round cannot close this gap. Closing it would mean moving secondary results to the note together with their caveats, which changes the paper's claims, so it is Joseph's decision. | — | **finding, for Joseph** |
<!-- absence-ok: names the caveat category "untested or omitted" used to classify statements; not a claim that any result is absent from the repository -->

### 5.2 The note (from set N)

| | rule | provisional | change |
|---|---|---|---|
| R-N1 | **State each caveat once, where the method is described.** The uncertainty-related ones go in the uncertainty sections. Restate the principal ones in the summary. The restatement rate (2.17) should fall toward the corpus median (1.4). | where described, and in limitations | adds the uncertainty-section placement. No separate limitations chapter: N has none. |
| R-N2 | **(a) History goes in one place.** That is one "updates since the previous result" passage, framed as improvements. The rest goes to the internal records. Our note puts 41% of its history statements in the appendices, mainly the appendix on superseded work. | kept where it bears on a quoted result; otherwise to the records | adds the single-passage form |
| R-N3 | **(b) The full account of a deviation, with its consequence, stated once where the affected result is described.** An operational deviation is a plain statement of what happened and what it changed. | the full account | adds "once, where the result is described" |
| R-N4 | **(c) Assumptions are stated as assumptions. Each omitted effect is sized or bounded, with its reason.** The share containing a negation word (50%) should fall toward the corpus median (24%). | where described, and in limitations | adds the form and the measured target |
| R-N5 | **(d) Scope is stated once, in the introduction, as a positive definition.** | once, introduction | adds the form |
| R-N6 | **(e) Process vocabulary is removed.** That includes recorded decisions, decision records and obligations. | removed | unchanged |
| R-N7 | **The measured gap.** The note's distinct caveats (8.4 per 1,000 words) are 3–5× the long comparators' (1.6–2.5). The same limit applies as R-P9. | — | **finding, for Joseph** |

## 6. Where a comparator would assign an uncertainty: options for Joseph (not acted on)

Each option changes numbers or claims, so it needs its own decision. Some also need compute (decision item 5).

| our caveat (restatements: paper / note) | comparator practice | what it would take |
|---|---|---|
| Residual regularization bias under generator-sized truth changes, up to 74% at high W, in no quoted uncertainty (10 / 20) | P4: an alternative-model universe added to the covariance ("to account for potential biases due to the nominal MC modeling prediction used in the unfolding procedure"). P6: a model uncertainty about twice the largest generator variation. P5: a "Signal model" systematic. | a model-dependence covariance from the generator-sized truth-change pseudo-experiments; a decision on its prescription |
| The purity background-subtraction bias, up to 4% in the highest-W cells, omitted from the quoted uncertainties (7 / –) | non-closure assigned as an uncertainty (P4, P6 pattern) | a decision; the bias is already measured |
| No calorimetric hadronic-response band, and recoil-response uncertainty omitted from the tests (12 / 13) | detector-response uncertainties in the covariance (all of P4–P6, N1) | building the band and propagating it: compute |
| Seed dependence resting on one seed pair (paper item 5) | P1: training randomness assigned through ensembles until "negligible relative to the systematic and statistical uncertainties" | a seed ensemble: compute |
| Statistical undercoverage at the tested truths (4 / 12) | N1: simulated-data studies turned into an added smearing of the result | a decision on whether and how to scale the band; any choice needs its own coverage test |

## 7. A defect found by the coding

- **Where:** the note, `sec_method.tex:73-74` (built text §3.1).
- **What it says:** "The quoted 2D and 5D central values, all quoted uncertainties and the extended-fiducial value do
  not use it", where "it" is the negative-weight background treatment.
- **Why it is stale:** the 2D result moved to configuration (f), refined negative-weight subtraction, on 2026-10-24.
  See `app_history.tex:91`, `sec_method.tex:110` and `:248`, and `sec_3d.tex:147`. The paper says the same
  (`paper_body.tex:311`).
- **Status:** fixed in its own PR, on the director's ruling
  (`note-fixes/FIX-20261025-negweight-scope.md`).

## 8. Limits of this study

- **The corpus is chosen, not sampled.** It is nine documents. Set N holds long journal papers, because no public
  analysis note of our kind was found. A collaboration-internal note may carry more caveats than a published
  technical paper.
- **One coder per document**, except the two coded twice (§2.4). The coders were Claude subagents. The prompts did
  not name our documents, but they called the comparators "published" and ours not, and our texts were not stripped of
  every internal reference.
- **The P5 coders disagree by 25%** in row count, mostly in (a) and (d). Rates are reliable to roughly that.
- **The positive-first judgment was not reliable** (§2.5). The negation-word share replaces it, and it is a proxy:
  a positive sentence can contain "not".
- **The number measure counts any digit**, including section and reference numbers, so it overstates how often a
  caveat is quantified.
- **The comparators carry fewer results than our paper.** The rate gap (R-P9) partly reflects that. The rules govern
  how a caveat is stated, not how many results the paper reports.
