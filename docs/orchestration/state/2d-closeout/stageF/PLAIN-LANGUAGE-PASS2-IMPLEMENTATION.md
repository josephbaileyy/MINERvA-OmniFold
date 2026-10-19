# Plain-language pass 2: implementation record

**Owner:** the paper-tighten lane, as director (Stage F), 2026-10-19. Under
[`DECISION-20261018-joseph-plain-language-pass2`](../../../DECISION-20261018-joseph-plain-language-pass2.md) and the
frozen brief [`PLAIN-LANGUAGE-PASS2.md`](PLAIN-LANGUAGE-PASS2.md). Prompts and reports are verbatim in
[`plain-language/PLAIN-LANGUAGE-PASS2-REPORTS.md`](plain-language/PLAIN-LANGUAGE-PASS2-REPORTS.md), cited as P1–P25.

**CITABLE FOR:**
- what pass 2 changed and how it was checked;
- the director's rulings on base defects;
- the outside-model rounds and their before and after;
- the physics points the outside referees raised, as triaged.

**NOT CITABLE FOR:**
- any claim beyond themes A and C;
- a resolution of the triaged physics points (they are Joseph's);
- final wording (J3–J5 provisional until the review with Ben);
- any outward act (J6).

## 1. Commits (branch `stageF/plain-language-pass2-20261018`, base `main` `34650231`)

| commit | content |
|---|---|
| `5cb1b038` | decision record and frozen brief |
| `b3fc422b` | note homes for moved content (release candidate, fine grid, 5D coverage numbers); the `sec_5d` residual-proxy correction; theme D (bibliography, `result_status_rows.tex`) |
| `27edd449` | paper and primer integration |
| `df6b9b29` | fixes from the preservation reviews |
| (this record) | the implementation record, the prompts and reports, `run_x.sh`, the agenda |

## 2. What changed

- **Paper abstract:** 233 → 163 words, counted from the PDF. It was 156 after integration, and the review fixes
  restored "under a stated nuisance model" and "a median of".
  - It carries the 2D reproduction (integrated cross section within about one percent).
  - The three- to five-observable results are "central values only".
  - The biases, and the model dependence (a median of about 10–13% per cell) against the 10% precision target set
    in advance.
  - The rejection of the hybrid null hypotheses "under a stated nuisance model".
  - The three limits on interpreting them.
- **Paper body:**
  - The section on the status of the five-dimensional uncertainty now comes before the central-value results
    (Sec. V; label kept).
  - **Theme A:** the fine-grid binning, the halving rate, which estimator the 74% belongs to, the 5D coverage-test
    numbers, and the model-dependence bound against its target. Each cites its record in a comment.
  - **Theme B:** history and repeated caveats moved to the note (paper P2, P4–P9, P16). Each was verified at its
    note location by the reviewer.
  - **P15:** one paragraph collects the choices made after results were seen. Each stays at its claim as well.
  - **P3** (the earlier statistical band) is shortened rather than removed. The Sec. IV receipt gate binds three of
    its values, and disclosure D2 requires the history.
  - **Theme C:** the failed 5D coverage test is stated as miscoverage at the tested truths (F1), and the rejections
    as rejections of hybrid null hypotheses (F15).
  - 12 pages; the last page now holds fewer references.
- **Primer:**
  - Section 3 is reordered: a short findings overview, the 2D trust check, the multi-quantity findings and the
    corner excess, the ranked limits, the joint test (with why its calibration does not rely on the 5D error bars),
    PET briefly, and the extended signal definition.
  - The ranked limits follow the paper's order: biases; the unvalidated, seed-dependent uncertainty; untested or
    failed coverage; the model dependence; then numerical stability.
  - The takeaway includes the joint test, with its six conditions.
  - PET chronology, the six-item condition list, the κ scan and the defect list moved to the paper and the note.
  - Theme-A numbers are added, with siunitx rounding of the same macros.
  - Abstract 130 → 151 words: it gained the joint test, "central values only" and "no significance assigned".
  - 14 → 13 pages.
- **Note and bibliography (theme D):**
  - Seven reference titles are in physics terms, with keys unchanged and old titles in comments.
  - Three missing locators are printed.
  - `result_status_rows.tex` is reworded with the same content.

## 3. Outside-model rounds

The runs used agy (`gemini-3.8-flash-high`) and codex-school (`gpt-6.1-sol`). They were read-only, on copied text, and
each sentence adopted from them was checked against the sources.

| round | what | used for |
|---|---|---|
| X1 (P1–P6) | a PRD referee report, with a presentation critique and an abstract rewrite; a paragraph main-idea and outline analysis, with proportions, repetition and the primer's order | the structure (Sec. V moved), the repetition inventory, the abstract diagnosis, the primer's order |
| X2 (P9–P14) | PRD-style rewrites of the abstract and the worst sections, and of primer §3–4 | the integration writers took the best of each, after checking |
| X3 (P18–P22) | the X1 prompts again, on the pass-2 PDFs | before and after |

**What each model contributed:**
- **GPT-6.1-sol** was careful about claim strength.
  - It gave the sharpest diagnosis of the abstract's growth: "narrow each claim until it needs fewer
    qualifications".
  - It gave the structural recommendation (status before results).
  - It raised the most substantive physics points (§5).
- **Gemini** gave useful register criticism. Its rewrites drift toward stronger claims, in both rounds: "the first
  application … to experimental neutrino data", "unmodeled coverage", the rebuilt band having "resolved"
  undercoverage, and rejections "primarily driven by low-dimensional projections". Each was rejected.

**Before and after** (the outside models' estimates of word share, paper overall):

| model | results | method | caveats | history |
|---|---|---|---|---|
| GPT-6.1-sol, X1 → X3 | 25% → 23% | 30% → 34% | 35% → 35% | 8% → 8% |
| Gemini, X1 → X3 | 17% → 20% | 37% → 35% | 36% → 37% | 10% → 8% |

Both still describe the paper as written to anticipate objections, as "a project audit". The checkable gains were:
- the abstract length;
- the section order;
- the stated numbers in place of hedges;
- less history in the body;
- the primer's order and length.

The caveat share did not move. Pass 2 still keeps every limitation that qualifies a conclusion in the paper, and the
paper has many. GPT-6.1-sol (P20, Part 4) names the next lever: decide the paper's central deliverable (a methods
paper with conditional generator tests), and separate observed results, demonstrated validation properties and
interpretive assumptions. That is the authors' decision, not a wording pass.

## 4. Reviews and fixes

- **Paper** (P23): 1 MATERIAL, 4 MINOR, 11 NOTE.
  - The MATERIAL finding: the abstract had lost both condition qualifiers on the rejection.
  - All MATERIAL and MINOR findings are fixed in `df6b9b29`.
  - All 17 moves to the note were opened and confirmed.
  - Every added number matches its record.
- **Primer, note and bibliography** (P24): 1 MATERIAL, 8 MINOR, 7 NOTE.
  - The MATERIAL finding: the primer ranked the limits differently from the paper.
  - All MATERIAL and MINOR findings and the primer NOTEs are fixed (P25).
  - The note numbers, the residual-proxy correction and the bibliography retitles were confirmed.
- **Director's rulings on base defects** (C7). Each aligns a sentence with sources, and each was confirmed by a
  reviewer:
  - **The paper's stopping rule.** It is a 99.5% look interval plus a precision tier
    (`nd-unfolding/s5p_inference.py:89-114`), not the 95% decision interval.
  - **The primer's corner excess.** It carries the paper's caveat (no mismodelled-response closure; the largest
    regularization bias is there). "Points theorists toward what their models are missing" is cut.
  - **Primer P-9.** The primer now states the model-dependence headline.
  - **The note's `sec_5d` "31–63% recovered".** This is a residual proxy of 0.31–0.63 against a target of at most
    0.25.

## 5. Physics points from the outside referees (triage P7; for Joseph and Ben, not acted on)

| point | triage verdict | what would close it |
|---|---|---|
| Calorimetric recoil-response uncertainty missing from the joint tests | stated wherever a referee looks; the gap is real (high) | a response band propagated through the null calibration (new computation) |
| W is not an independent fifth observable: at reconstruction level it is an exact function of (pT, p∥, q3); at truth level (struck nucleon at rest) it is fixed to within tens of MeV | valid (medium) | reword "five observables" framing; one residual check on a simulation dump |
| The sentence "the Monte Carlo p values remain valid at the number reached" | unsupported as written. The decisions are conservative: the 95% Clopper–Pearson gate bounds each decision's size, and the Holm familywise rate is at most 0.89α (a new calculation in the director's scratchpad, not a record) | replace the sentence with the decision-level statement after Joseph rules |
| NuWro and GiBUU generated on carbon, data on hydrocarbon | valid; disclosed in records, unquantified (medium) | a GENIE CH-vs-C proxy |
| The null inherits Tune v1's hadron composition within cells; the nuisance-averaged versus uniform meaning of "calibrated" | valid, text (medium) | text in the conditions |
| The central-value figures use the purity background treatment, the tests the refined one | partly addressed; captions do not say which; a note obligation to revisit before submission is open (medium) | name the estimator in the captions |

The full table (38 rows) is P7.

## 6. Builds

`build_all.sh`, all four targets, in a scratch copy at `df6b9b29`:
- rc 0, with no unresolved references;
- gates PASS (Sec. IV receipts 15/15);
- pytest 63 passed;
- `check_invariance.py` shows no new mid-line comment. Its numeral differences are the theme-A additions and the
  theme-B moves listed in P16, P17 and P25.

| PDF | pages | sha256 |
|---|---|---|
| main_note.pdf | 123 | `6e70e00b…` |
| main_paper.pdf | 12 | `9bf53d5f…` |
| main_primer.pdf | 13 | `a9452941…` |
| pet_note.pdf | 26 | `df7e2460…` |

## 7. Open for Joseph

- **The physics points in §5.**
- **Framing.** Whether the paper is framed as a methods paper with conditional tests (GPT-6.1-sol's recommendation),
  which would let several caveats become a single scope statement.
- **Remaining flags:**
  - paper F9–F11, F13, F14, F16, F18–F22 and F-p2-2 to F-p2-8 (P16);
  - primer F5, F8–F10, F13 and F-p2-3/4 (P17).
- **Same-model caveat.** Integration, review and triage are Claude Opus 5.5 on claude-school. Two outside models
  reduced the single-model bias, and Ben is the first human outside reader.
