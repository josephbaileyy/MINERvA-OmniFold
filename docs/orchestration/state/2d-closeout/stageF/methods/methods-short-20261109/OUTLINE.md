# The short methods paper: outline and move map (2026-11-09)

**Recorded by** `director-helper-3`, for the director's review before the full prose is written. No paper text has
been written yet, and no wording is approved.

**Revision, 2026-11-09, after the director's approval and the journal-editor's read.** The structure below is the one the director approved. The prose follows it, with the editor's changes, which are listed in REPORT.md under "The structure":
- a validation-strategy subsection;
- descriptive titles, and JINST numbering;
- Table 1's estimator column;
- Appendix A's three tables not duplicated in S10 (S3 and S5 already carry them).

This outline is kept as the record of what was approved. REPORT.md and the prose are current.

**Branch:** `draft/methods-short-20261109`. It starts from `bc8673186` (methods round 5) with main at `c120e0d07`
merged in (`e9b8ea160`).

**The governing records:**
- `DECISION-20261109-joseph-methods-baseline-and-plan.md` (#976, read at its head `943d5f97`, not yet merged): items 1,
  2, 3.4 and 6;
- `secondary-results/consult-astra-publishable-path-20261109/answer.txt`: `:11` (the three findings, and what moves),
  `:15-19` (what the advisor's story supports), `:29` ((e) as the baseline, E₉₆ as a mitigation with mixed outcomes);
- `secondary-results/referee-methods-round5-20261109/README.md:48-64` (what the eight reads agree on).

**The base's size:** the round-5 rater copy (`manuscript-methods-r5.blind.txt`) is 12,701 words. Its page count is
measured from the PDF built at the base, with the first prose commit.

**The target:**
- about 6,500 words in the rater copy, half the base;
- Tables I and II, and Figs. 1–3;
- no appendix in the paper.

## 1. The structure

Each section lists what it keeps, from round 5's section, and what leaves it. The word counts are targets.

### Abstract (about 170 words)
- **What it says:**
  - the method;
  - the three findings, one sentence each;
  - the failed tests;
  - "illustration only" for the data output.
- **Pending results** are given by keys (§3). There are three:
  - one sentence on FD-PRR (`prr-*`);
  - one clause for each LL5D tune (`ll5d-*`);
  - none for V-HALF. Its classes appear in the body only.

### I. Introduction (about 500 words; round 5: about 900)
- **Keeps:**
  - the context paragraph, with the H1, ATLAS and T2K citations;
  - the scope sentence: "one OmniFold implementation on one data set";
  - the three findings, stated once;
  - a short roadmap.
- **Leaves:**
  - the long summary of results, which Table I and Sec. VI already give;
  - the second statement of every limitation.

### II. Data, observables and method (about 1,000 words; round 5: Secs. II, III and III A, about 2,300)
- **Keeps:**
  - the exposure and playlists;
  - Eq. (1) and one sentence on its 135 MeV constant;
  - that reconstructed W is fixed by (p_T, p_∥, q_3), which four referee reads raise (README `:63`);
  - the two OmniFold steps, and the purity-based and negative-weight background treatments;
  - **configuration (e), named as the frozen baseline (decision item 1),** with its settings, and the 2D estimator;
  - the 16 cells, in one paragraph.
- **Moves to the Supplement:**
  - the playlist-1A copy check;
  - the comparison of E_avail definitions, and the first-order shift from the charged-pion mass, to S2 (the text is
    already there);
  - the generator predictions' definitions and their CH correction, to the new S10 (see "Leaves the paper" below);
  - how the development choices were made:
    - LightGBM chosen over the exact-split and histogram estimators;
    - the iteration-count rule (0.314 against 0.384, and the 20 % rule);
    - the refinement capacity;
    - no cross-fitting, and no early stopping.

    These go to S4, which carries most of them already.
  - the coarse grid and the support rule, to S7.

### III. Finding 1: the 2D benchmark and its limits (about 1,000 words; round 5: Secs. IV B–D in part, about 1,900)
- **Keeps:**
  - the normalization: integral ratio 1.010;
  - per-bin agreement: RMS 0.535 of the published-σ residuals;
  - the χ² against the published covariance, as a descriptive distance: 2.27 over 205 bins, with a 0.04 normalization
    part against 465 for the shape, and Fig. 3;
  - **a new sentence stating the missing cross-covariance:** the two results share the data and the flux, detector
    and generator systematics, and their cross-covariance is not available. The source is the note's
    `sec_results.tex:30`. That sentence is in the note but absent from round 5's paper text, so the χ² becomes descriptive for a stated
    reason;
  - "the source of the shape difference has not been identified";
  - that the learner and background treatment were chosen with the comparison in view, so it is not a blind
    validation;
  - the 2D IBU: differ, with the localisation unresolved;
  - the run-period benchmark: the step does not account for the distance in the best-determined directions;
  - the quadrant agreement of the 16 cells with the 2D result.
- **Moves to the Supplement:**
  - the per-estimator χ² values (3.66, 2.65, 2.70), the purity-closure numbers (5.9, 0.44, 14 of 205), the
    10-iteration check and the median 1.03 % difference, to S4 and S6;
  - the flux-uncertainty comparison (4.01 % against 3.71 %), the eigenmode detail beyond one sentence, and the
    per-group run-period diagnosis, to S6;
  - the run-period benchmark's 132-direction and six-mode detail, to S6.
- **Moves to Sec. V:** the 2D covariance and its coverage test (COV2D), because they concern calibration, not the
  benchmark.

### IV. Finding 2: controlled truth recovery and prior retention (about 1,700 words; round 5: Secs. IV E, F and H in part)
- **Keeps:**
  - the nominal closure;
  - the generator-sized E_avail change recovered in part, with Fig. 2;
  - the exact binned IBU comparison at the same size, and its behaviour at long iteration;
  - the 12-truth fake-data grading, with Table II kept and its criteria fixed before grading;
  - the two held-out GENIE v3 tunes, which grade bias, not coverage;
  - the shifted recoil response, which is descriptive;
  - the 16-cell IBU comparison: the reported cells depend on the algorithm.
- **New, as placeholders:**
  - **FD-PRR**:
    - a compact table of PR-1's class per factor (F1–F4) at the two flagged truths;
    - PR-2a and PR-2b for IBU against (e);
    - PR-3, worded "clears / does not clear at these truths" (FD-PRR §5.3, the director's ruling 2);
    - the §5.4 composite labels, worded "consistent with …" only.
    - No adoption follows (§6).
  - **V-HALF**: each cell's class, given as counts and lists:
    - valid;
    - not valid at a named truth;
    - not assessed, where the rule applies at no truth;
    - unresolved (noise).

    Each is stated as a bias grading under simulated truths, not as a statement about detector adequacy (decision item
    6; the bias-half decision's NOT CITABLE FOR).
- **Moves to the Supplement:**
  - V-ATLAS and V-PRIOR in full: the thresholds, the ρ table and the 1/3 and 1 sensitivity. That goes to the new S11,
    with one sentence left in the paper. **Whether V-HALF replaces them in the paper is a wording choice (W-3,
    below).**
  - the Cramér–Rao detail (121 of 144), to S8.
  - the development-variant rows of Table I.

### V. Finding 3: reproducibility, stability and calibration (about 1,500 words; round 5: Secs. IV A, D, G and H in part)
- **Reproducible:** the result is bitwise independent of the training seed and of the input row order.
- **Not stable:**
  - the rounding-level instability fails the stability requirement (2.6 σ);
  - the B0 sentences, verbatim as approved (`DECISION-20261106-joseph-b0-reconciliation-sentence.md`);
  - RS1's mechanism, in its licensed wording and "on this pseudo-experiment" (`OUTCOME-20261108-rs1-rounding-mechanism.md`
    `:54`ff, its CITABLE FOR);
  - FD-STAB's probe: no variant passed;
  - **E₉₆ as a tested mitigation, within ENS1's CITABLE FOR:** it meets the stability bars and is BIAS_WORSE at 1 of
    17 truths; not adopted, and no estimator replaced. The round-5 sentence is kept as it is.
- **Calibration:**
  - the 2D covariance under-covers at both tunes (COV2D, within its licences);
  - the 16-cell coverage test was stopped at its gate, and its redesign stopped at stage 1. That takes three sentences,
    down from about 600 words;
  - **LL5D, as placeholders,** per tune (G18, AR23) and per reading (`minus2` primary, `all`):
    - COVERS, UNDER-COVERS (cells named, joint flag) or INVALID;
    - or one campaign-level variant, for the case where it stops before the bulk (a failed gate or clipcheck
      TO_JOSEPH).

    Every variant carries LL5D's limits: the bands excluded, the covariance rebuilt per truth rather than per toy, the
    response and run-period terms not drawn, and nothing about the reported data intervals or E₉₆ (consult `:39-43`,
    LL5D `:78-94`).
  - the run-period inconsistency, and the C_PL,5D block added after the differences were seen.
- **Moves to the Supplement:** the gate diagnosis of the 1B test (MaRES, MaCCQE and MvRES; the flux and detector
  splits; the GEANT4 neutron and proton departures; 892 of 900), to S9. S9 is round 5's test designs and keeps that
  number.

### VI. Discussion, limitations and next steps (about 700 words; round 5: Sec. VI and VI A, about 900)
- **Keeps:**
  - the three findings, read together;
  - the checklist sentence ("what must be checked before unfolded intervals are interpreted");
  - the limitations list, cut to the items not already stated with their results.
- **Explicitly not claimed** (decision item 6). Each is a ledger row:
  - that 5D validates the full distribution;
  - V-HALF as a statement about detector adequacy;
  - that the 2D mismodeling is localized in the extra dimensions. This one is a **stated next step**: what such a test
    would need (fixed muon regions, their joint uncertainty and multiplicity, and robustness to plausible unfolding and
    response changes), from consult `:17`;
  - any coverage statement beyond COV2D's licences and LL5D's, once it lands.
- **Wording choice W-4:** whether the paper names the E₉₆ bias–variance study as future work. The decision item 4
  allows the study but says nothing about the paper mentioning it.

### Leaves the paper: Appendix A (round 5: about 2,000 words, Tables III–VII and Fig. 4)
- **Goes to the new S10, "Illustrative output on data":**
  - the 16-cell output (Table III);
  - the per-group uncertainties (Table IV);
  - the correlation matrix (Table V);
  - the generator comparison (Tables VI and VII, and Fig. 4);
  - the generator definitions.
- **The paper keeps** one sentence and a pointer.
- **Data availability** already places the 16-cell files in the Supplement, so it is unchanged.
- **The basis** is consult `:11`: "Move … extensive generator-comparison tables", and the illustrative output is not
  a finding. Three Gemini reads called printing it hazardous (README `:64`).

**Table I** keeps one row per finding-bearing test, about 14 rows, down from 26. The development rows go to S4 and S8,
and the new FD-PRR, V-HALF and LL5D rows are placeholders.

## 2. The files

- **The paper:** `paper_body.tex` is rewritten in place, which keeps one current version. The round-5 text stays at
  `bc8673186` and in its committed blind copy.
- **The registry:** rows that cite `paper_body.tex:N` (ALIASES 38 and 47, ATTRIBUTION 17, and any others a grep
  finds) are re-cited in the same commit. `records_estimators.tex` is regenerated.
- **The Supplement:** `supplemental_body.tex` gains S10 and S11, and the moved text in S2, S4, S6, S8 and S9.
  - Text moved from the paper keeps its source comments.
  - Text from the note keeps its Search line, as round 5 did.
- **The checks:** `check_supp_pointers.py` and `check_body_pointers.py` run over the new body.
- **`main_paper.tex`:**
  - the abstract is replaced;
  - the title is unchanged until wording choice W-1;
  - the acknowledgments and data availability are unchanged.

## 3. Placeholders: pending verdicts as values, prose as declared variants

**The keys, in `make_values_fived16.py`:**
- **New READOUTS entries** `prr`, `ll5d` and `vhalf`. Each gets its path and sha prefix once the record lands.
  - Until then, each key prints `\fvpending{…}`.
  - The bound readout's file names come from the declarations (FD-PRR `prr_read`; LL5D §6; V-HALF's declaration,
    once committed).
- **Value keys:** `prr-pr1-<F>-<truth>`, `prr-pr2a-<truth>`, `prr-pr2b-<truth>`, `prr-pr3-<level>`, `prr-label-<truth>`,
  `ll5d-<tune>-<reading>`, `ll5d-<tune>-<reading>-cells`, and `vhalf-n-<class>` / `vhalf-cells-<class>`.
- **Each value is asserted** to lie in its declaration's class set, quoted with file:line:
  - FD-PRR §5.1 (`:287-292`), §5.2 (`:297-300`), §5.3 (`:307-310`) and §5.4 (`:325-330`);
  - LL5D §6 (`:473-475`) and §5 (`:427`, `:439-440`);
  - the bias-half decision, item 1.

**The variants:**
- A new macro, `\fvvariant{key}{value}{text}`, prints `text` only when `key` has that value.
- While the key is pending, every variant renders as one `[PENDING: key]`, so the paper can't ship. build_all.sh
  already refuses `[PENDING`.
- Each sentence that depends on a pending verdict is written once per possible value. Filling in a result changes a
  value and writes no prose.

**The ledger:** `methods-short-20261109/variants.md` has one row per (key, value). Each row gives the variant's text
id, the declaration's line for that class, and the licence that limits its wording.

**The check:** `check_round.py` asserts:
- that every key's variant set equals its declaration's class set, so no variant is missing or extra;
- that no literal number sits in a variant;
- the paper is built once per value of every pending key, in a self-test, so every variant typesets.

**Composite labels:** FD-PRR's labels can hold together, so they get one sentence each, each printed when its own
label holds. That avoids writing a variant for each of 5⁸ class combinations. The PR-1 classes print as words in the
table.

**Rater copies:** they need filled keys, or a stated draft value. A rater copy with placeholders is not built for
referees, and no referee rounds run now (the work order). check_round builds a draft copy for the word count only.

## 4. Claim ledger and wording choices

- **`methods-short-20261109/ledger.md`** has one row per claim. Each row gives the claim, its record at file:line and
  sha, and its licence: CITABLE FOR quoted, and NOT CITABLE FOR where it applies.
- **Every number is a `\fvval` key or a round-5 printed numeral with its existing source.**
  - check_round's numeral check, from `b0-sentence-paper-20261106`, compares the new paper's numerals against the
    base's.
  - Any numeral new to the base needs a ledger row.
- **Wording choices** (W-rows) go to the PRD-referee read at the end, then to Joseph. They are not decided here:
  - W-1: the title;
  - W-2: the abstract's three-finding sentences;
  - W-3: V-HALF beside or in place of V-ATLAS and V-PRIOR in the paper;
  - W-4: naming the bias–variance study as future work;
  - W-5: the next-step sentence on localization.

## 5. Questions for the director

1. **The body file.** Should `paper_body.tex` be rewritten in place, re-citing the registry rows? My recommendation
   is yes, so there is one current version. The alternative is a new `short_body.tex`, which leaves the registry
   untouched but makes two paper bodies.
2. **Appendix A.** Should it go to the Supplement (S10)? My recommendation is yes, because Data availability already
   points there. The alternative is the note.
3. **The length target.** Is about 6,500 rater-copy words, with Tables I–II and Figs. 1–3, the right size? It is my
   reading of "short" from consult `:1` and `:59` ("short, self-contained").
