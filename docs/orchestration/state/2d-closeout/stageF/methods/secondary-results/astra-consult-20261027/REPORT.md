# Independent consult: what the paper should keep, shorten or move (2026-10-27)

**Under** `DECISION-20261027-joseph-n4-after-content-cuts-and-paper-scope-consult.md` item 4. Joseph asked for "an
independent unbiased gpt astra high" suggestion of what to move, "based on its understanding of the literature
standards".

**Run by** the paper-tighten lane, as director.

**MEASURES:** nothing. It is advice from a model, recorded as given.

**CITABLE FOR:** what the consult recommended, from which inputs.

**NOT CITABLE FOR:** what published papers do. Its literature claims are its own. Only the identities of the papers it
names are checked below.

## How it was run

- **Model and account:** `gpt-6-astra`, reasoning `high`, sandbox `read-only`. It ran on `codex-school`
  (`CODEX_HOME=~/.codex-school`, `run-codex-school.log`, rc 0).
  - The first attempt, on `codex-school2`, stopped at its usage limit before answering
    (`run-codex-school2-usage-limit.log`).
  - Both accounts are on the delegation allow-list.
- **Inputs** (`inputs/`, digests in `SHA256SUMS`):
  - the paper's printed text at main `602ab31f` (`paper.txt`, pdftotext of `main_paper.pdf`);
  - the note's front matter and table of contents;
  - a neutral description of the 5D result to be added (`5d-addition.md`);
  - the prompt (`PROMPT.md`).
- **Not given:**
  - the paper rewrite lane's candidate list (`../CANDIDATES.md`) or its ranking;
  - the director's recommendation;
  - any rater scores.
- **The answer:** `answer.txt`, 3,745 words, verbatim (kept as .txt so the record stays verbatim: it is the model's text, not a record of ours, and the absence lint applies to our records).

## What it recommends, in brief

1. **Core to keep:**
   - the 2D benchmark;
   - the new 16-cell 5D result, with its covariance and generator comparisons;
   - the background-subtraction finding;
   - the failure to recover generator-sized truth changes, with its focused binned diagnosis;
   - the uncertainty-validation findings, including the new fake-data study's pattern of success and failure.
2. **The major cut: move the whole calibrated hybrid-null joint-testing programme** (§VII B–E, Table IV) to the note,
   and remove its "all ten reject" headline from the abstract. Its reason: with the 5D comparison added, it is a second
   inference framework that needs its own long qualification.
3. **Also MOVE:**
   - the external-prediction convention checks;
   - the superseded statistical bands' history;
   - the data-side background comparison and the full Fig. 2 panel;
   - the incorrectly implemented q3 coverage test;
   - the long exact-binned runs;
   - the (E_avail, W) "where the excess lives" map;
   - the four-generator high-E_avail description;
   - every VII B–E sub-study;
   - the 5D cell-combination figure, whose note placement it confirms.
4. **SHORTEN most supporting diagnostics** to their headline sentence.
5. **KEEP the 5D correlation-sensitivity sentence.**
6. **Caveats it says must stay in the paper:**
   - the old and new 5D products are distinguished;
   - the q3-tilt fake-data failure is stated in the main uncertainty discussion, not only at GiBUU;
   - covariance width, a bias envelope and coverage are kept apart;
   - the 2D result remains a reproduction;
   - each test's scope is stated.
7. **Estimated length:** about 7,000–8,000 words including the 5D addition. That is an editorial estimate, not counted.

## The papers it names: identities checked

Each was checked on its arXiv abstract page on 2026-10-27, for title, authors and DOI. The comparator check had
already checked 2106.16210 (PR #398).

| arXiv | checked | note |
|---|---|---|
| 2504.06857 | Huang et al., "Machine Learning-Assisted Unfolding for Neutrino Cross-section Measurements with the OmniFold Technique", PRD 112, 012008 (2025) | matches |
| 2106.16210 | MINERvA (Ruterbories et al.), PRD 104, 092007 | matches (PR #398) |
| 2110.13372 | MINERvA (Ascencio et al.), low three-momentum transfer, DOI 10.1103/PhysRevD.106.032001 | matches |
| 2105.09923 | Komiske, McCormack, Nachman, "Preserving New Physics while Simultaneously Unfolding All Observables", DOI 10.1103/PhysRevD.104.076027 | matches |
| 2405.20041 | ATLAS, 24 Z+jets observables, PRL 133, 261803 (2024) | matches |
| 2507.09582 | Canelli et al., "A Practical Guide to Unbinned Unfolding", DOI 10.1140/epjc/s10052-025-15265-9 | identity matches; the consult's "EPJC 86, 106 (2026)" volume and page are not shown on the page |

How each paper bears on the recommendation is the consult's reading, and it was not checked.

## Status

This is advice for Joseph, to be read with `../CANDIDATES.md` at the 5D integration, as his decision says. Nothing
moves until he decides.
