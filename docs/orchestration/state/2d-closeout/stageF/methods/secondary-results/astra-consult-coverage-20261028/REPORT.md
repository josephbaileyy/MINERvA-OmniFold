# Independent consult: how important is a nuisance-drawn coverage test to the publication? (2026-10-28)

**Asked for by** Joseph (2026-10-28): "I think its worth to investigate the coverage limitation more seriously,
consider having a fresh agent review the option and rate how important this would be for the quality of our measurement
publication".

**Run by** the paper-tighten lane, as director.

**MEASURES:** nothing. It is advice from a model, recorded as given.

**CITABLE FOR:** what the consult rated and recommended, from which inputs.

**NOT CITABLE FOR:** what published papers do, beyond the identities checked below. Any decision to run a coverage
test is Joseph's, with a compute grant.

## How it was run

- **Model and account:** `gpt-6-astra`, reasoning `high`, sandbox `read-only`, on `codex-school2`, rc 0. The run log
  is not committed (`*.log` is ignored); its sha256 begins `a3488f6af232d2f7`.
- **Inputs** (`inputs/`, digests in `SHA256SUMS`):
  - `paper.txt`: pdftotext of the paper built from #413 at `9457beab`;
  - `coverage-options.md`: LIMITATION-PLAN.md §1 verbatim, the coverage facts and costed designs, with its absence-ok
    comments removed;
  - `PROMPT.md`: a neutral prompt with a defined 1–5 importance scale.
- **Stored as `.txt`:** `PROMPT.md` and `coverage-options.md` are kept as `PROMPT.md.txt` and
  `coverage-options.md.txt`, byte-identical to the files the model read, so that the records lint does not apply to
  verbatim input text. `SHA256SUMS` gives their digests.
- **Not given:** the director's recommendation, Joseph's earlier deferral of 1B, and any rater score.
- **Web access:** it opened public arXiv pages for 2106.16210 and 1801.05148.
- **The answer:** `answer.txt`, verbatim.

## What it says, in brief

- **Rating 4 of 5:** "the paper is noticeably weaker without it". A referee would likely request a bounded coverage
  study but not require a pass, because the limitation is disclosed and other validation exists.
- **Standard practice:** comparable PRD papers use fake-data recovery and systematic-universe propagation. An
  independent coverage ensemble of the final total intervals is stronger than they show, not a routine requirement.
- **The design:** 1B, with the nominal control validated first. The cheaper alternative with most of the value is the
  control plus one predeclared GENIE v3 truth.
  - It asks for per-cell results as well as pooled ones, and a statement of the power limitation (about 2.7 points
    per cell at 300 toys).
  - It asks that a pass be stated as "no undercoverage detected at the study's sensitivity", not "the intervals do not
    undercover".
- **Matters more, in its view:**
  - a targeted test of hadronic-response mismodeling beyond C_resp;
  - whether the covariance suits the quoted χ² (marginal coverage does not validate it);
  - tracing the run-period inconsistency into the sixteen-cell uncertainty;
  - a deposited release of the headline numbers.

## Checked by the director

- **Its four papers, on their arXiv pages:**
  - 1801.05148 is "Measurement of inclusive double-differential νμ charged-current cross section with improved
    acceptance in the T2K off-axis near detector", T2K Collaboration, with the journal-reference row "Phys. Rev. D 98,
    012004 (2018)";
  - 2106.16210, 2110.13372 and 2504.06857 were verified earlier (`register-prd-study/REPORT.md` §1;
    `astra-consult-2-20261027/REPORT.md`).
- **Not checked:** its characterization of each paper's validation procedures, and its "Sec. IV F" label for the
  coverage failure. The extraction carries no section headings.

## Not changed

- No compute is granted. `DECISION-20261027-joseph-limitation-plan-f1-bias-test-and-flux-bootstrap.md` item 4's
  deferral of 1B stands until Joseph decides.
- Claims, KI-85 and publication are Joseph's. Nothing is submitted, deposited or tagged.
