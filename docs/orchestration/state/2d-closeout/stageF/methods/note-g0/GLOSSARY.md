# Glossary of the analysis note's project-internal terms (batch 0)

This is the one vocabulary for the note. Later chapter batches use these replacements and do not coin new ones. Each
entry gives the meaning as checked in the note or its source, the plain replacement (one per meaning; where meanings
differ by context, each context is listed), and whether the term carries a **status** that must survive as a concept.
"Applied" says what `apply_glossary.py` did; counts before/after are in REPORT.md.

Spelling follows the note: US (*centered*, *modeling*).

---

## A. Status vocabulary (meaning-carrying: the status must survive in plain words)

### A1. "in use"
- **Meaning.** The object is the one this note uses for its results. Checked at sec:eavailw-adopted: "The five-axis
  covariance in use ... It is used although it has not passed the acceptance criteria of its specification."
  For the 2D statistical band, "the band in use when it ran" means the band quoted at the time of the coverage test
  (sec:coverage; App. G `coverage-fixed-truth` names it, VL162).
- **Replacement.**
  - five-axis / five-dimensional covariance: **"the five-axis covariance used in this note"** (later in the same
    paragraph: "used here").
  - "not in use" (3D or 4D covariance): **"not used for any result in this note"**; "not yet in use" keeps "yet".
  - 2D statistical band at the time of a test: **"the statistical band quoted when it ran"**.
  - "the variant in use is cv": **"the variant used is the CV-centered one"**.
- **Status: yes.** Keep the distinction *used for results* vs *built but not used*.
- **Applied:** 25 -> 0.

### A2. "adopt", "adopted", "adoption" (status sense)
- **Meaning.** Selected for use in this note's results. *Careful:* it is often narrower than "used for any
  result". The negative-weight treatment is "not adopted" for the measurement but its refined form IS used by the
  generator tests (sec_method, configuration (e)); the raised-refinement-capacity estimator R is "not adopted" but
  has the joint-test estimator's configuration (Table estimators-matrix, row (e)).
- **Replacement.** By object, never a blanket phrase:
  - a quoted 2D covariance: **"the quoted 2D covariance"**;
  - the five-axis covariance: **"the five-axis covariance used in this note"**;
  - a treatment or estimator not used for the measurement: **"not used for the quoted central values"** (only if
    that is what the source supports; check whether the generator tests use it);
  - a criterion: **"predeclared"** when it was fixed before the study (abstract: "the predeclared 10% criterion").
  - Plain-English uses with a method or recommendation as object ("the most widely adopted method", "we do not adopt
    that recommendation", "we adopt two-tier reporting") are **kept**.
- **Status: yes.**
- **Applied:** 26 -> 5 (all 5 plain-English, except one ambiguous use, open question Q1).

### A3. "constructed, not adopted" / "constructed but not in use"
- **Meaning.** The product exists and has been computed, but no result in the note uses it (sec_3d: the 3D projection
  of the five-axis covariance).
- **Replacement.** **"has been computed but is not used for any result in this note"**.
- **Status: yes** (exists vs is used).
- **Applied:** 1 -> 0.

### A4. "adoption gate"
- **Meaning.** The set of preconditions a product must meet before it is used for a result.
- **Replacement.** **"the choice of covariance"** where the sentence contrasts it with another choice; otherwise
  **"the conditions for using a product for a result"**.
- **Status: yes.**
- **Applied:** 1 -> 0.

### A5. "quotable"
- **Meaning.** The covariance that would be quoted if a 3D covariance were quoted.
- **Replacement.** **"the 3D covariance that would be quoted"**.
- **Status: yes** (hypothetical, not quoted). **Applied:** 2 -> 0.

### A6. "candidate"
- **Meaning.** Two senses. (i) An estimator under test (plain English; keep). (ii) A covariance or product that was
  built but not used ("remain candidates", "the 5D candidate", "corrected candidate").
- **Replacement.** (i) keep. (ii) **"an earlier 5D covariance (construction)"**, "not used for any quoted
  uncertainty", or "five-dimensional covariance", whichever the sentence states. **Exception, kept verbatim:**
  "the candidate split-varied band" (sec:uq-higherdim), a status set deliberately in commit 6964af37; the next
  sentence calls the same band "the band used in this note", a tension for the author (REPORT Q11).
- **Status:** sense (ii) yes. **Applied:** 17 -> 9 (all remaining are sense (i) or plain; one in the protected
  release paragraph).

### A7. "report-only"
- **Meaning.** Computed and reported, but not part of the decision rule (sec_joint).
- **Replacement.** At first use in sec_joint, **"for reporting only (outside the decision rule)"**; after that,
  **"for reporting only"**.
- **Status: yes.** **Applied:** 6 -> 0.

### A8. "frozen"
- **Meaning.** Fixed before production or before any observed statistic (the joint-test design); also, of an
  object, "as it stood for the decisions".
- **Replacement**, by context:
  - "the design was frozen", "were frozen before": **"fixed"**;
  - "the frozen design", "frozen rule", "frozen direction", "frozen variant shifts", "frozen tests", "frozen
    metric": **"predeclared"**;
  - "frozen ensembles", "frozen null (distributions)": **"the (calibration / null) ensembles used for the
    decisions"**;
  - "frozen Holm position": **"original Holm position"**;
  - "frozen stop": **"the stop set by the predeclared rule"** (the rule was predeclared; the stopping point is an
    outcome); "frozen B": **"the B at which its rule stopped"**;
  - in the lost-draw recovery text, "frozen" means **as in the primary (pre-recovery) evaluation**, not
    predeclared: "frozen variant shifts" -> "the variant shifts of the primary evaluation" (the shift S is computed
    from the calibration draws; RECORD-20261006-s5p-lost-seed-recovery-resolution.md sec. 3, "(b) frozen S");
    "frozen sets" (power) -> "the power sets as evaluated for the decisions"; "the frozen evaluation" -> "the
    evaluation before recovery";
  - "frozen Holm position", "frozen boundary": **"its Holm position in the decisions"**, **"its decision boundary"**;
  - "frozen values", "frozen decisions": **"recorded"** (the table already says "recorded");
  - "frozen conversion ... chain": **"unchanged"**; "frozen central value": **"quoted"**; "frozen 4D normalization":
    **"reported"**; "frozen lower-dimensional extractions": **"stored reference"**.
  - **Not changed:** the two uses inside the verbatim quotation of the specification (sec:joint5d-conditions).
- **Status: yes** (predeclared vs post hoc). **Applied:** 32 -> 0 outside the quote (2 in the quote kept).

### A9. "re-qualify"
- **Meaning.** Validate again. **Replacement:** "validate". **Applied:** 1 -> 0.

---

## B. Background treatment

### B1. "footing", "footed", "both-footing"
- **Meaning.** Which background subtraction a production chain uses: purity-based (binned) or negative-weight
  injection (refined). Checked at App. C sec:negweight-footing and App. G `bkg-mode-pins`.
- **Replacement.** **"background treatment"** (noun); "built with purity / negative-weight subtraction" (adjective);
  "purity footing" -> **"purity-based subtraction"**; "both footings" -> **"both background treatments"**; "refined
  footing" -> **"refined negative-weight subtraction"**.
- **Status: yes** (the choice and its open obligation to revisit). **Applied:** 30 -> 0.

### B2. `negweight-refined`, `negweight`, `purity`
- **Meaning.** The three values of the drivers' background-mode option `--bkg-mode`
  (`choices=["purity", "negweight", "negweight-refined"]`, 2d-unfolding/unfold_2d_omnifold_unbinned.py:1363,
  nd-unfolding/unfold_nd_omnifold_unbinned.py:620): purity-based subtraction, negative-weight injection, refined
  negative-weight subtraction.
- **Replacement.** In prose **"refined negative-weight subtraction"**, **"purity-based subtraction"**; the
  identifier stays once as a parenthetical at first use (sec:val-negweight) and in the app_guide label table.
- **Status:** no (a name). **Applied:** 4 -> 2 (first use, label table).

---

## C. Lateral systematics and event-loop modes

### C1. "lateral" (kept, now defined), "vertical"
- **Meaning.** MAT's terms: a *lateral* band shifts reconstructed kinematics; a *vertical* band reweights events.
- **Replacement.** Kept (MINERvA vocabulary); defined at first use in sec_experiment. "lateral block" ->
  **"lateral-band block"**.

### C2 (note). "single-pass" is explained at first use (sec:uq-higherdim): "the single-pass event loop, which
writes every universe in one pass".

### C2. "dump-all", "dumps", "CV event-loop support", "CV-support-limited", "support-limited", "support" (as a variant)
- **Meaning.** The event loop's single pass writes each lateral universe's shifted observables only for events that
  pass the selection at the central value; events that a shift would move into the selection are missing
  (sec_5d: "migrations omitted by the CV-support-limited dump-all sample").
- **Replacement.** **"the single-pass shifted observables"** / **"the single-pass event loop"**; "limited to events
  selected at the central value"; "dumps" (verb) -> **"stores / writes"**; "universe dumps" -> "the trees with
  per-universe content".
- **Status:** yes (the omission it implies). **Applied:** dump-all 3 -> 0, dumps 8 -> 0, support-limited 3 -> 0.

### C3. "selection-complete", "active-universe", "active-lateral", "active" (as a variant)
- **Meaning.** Event loops re-run with one lateral universe active (`MNV101_ACTIVE_UNIVERSE`), re-applying the
  selection to the shifted kinematics, so migrations into the selection are included.
- **Replacement.** **"re-selected"**: "re-selected event loops", "re-unfolds of re-selected universes",
  "re-selected lateral bands". Defined at first use in sec:uq-universes (pointer to sec:uq-higherdim); the identifier
  is in the label table.
- **Status:** yes. **Applied:** 12 + 6 -> 0.

### C4. "universe-complete variants"
- **Meaning.** The per-playlist trees that also carry every universe's weight (App. I: `_universes_full`).
- **Replacement.** "the trees made for the systematic universes". **Applied:** 1 -> 0.

### C5. "production migration gate"
- **Meaning.** The production's way of handling selection migration. **Replacement:** "production treats selection
  migration with ...". **Applied:** 1 -> 0.

---

## D. Campaign, variant and repository labels

Rule: a label leaves the prose. If a reader needs it to find the object in the repository it appears **once**, as a
parenthetical at first use, or in the "Labels used in the repository" table added to `app_guide.tex` (a `tabular`
in `center`, not a float, so no table number moves).

| label | meaning (checked) | replacement in prose | where the label is kept |
|---|---|---|---|
| J28 | audit finding: every N-D/5D kernel divided flux universes by the CV flux (AUDIT-FINDINGS-20260731 J28) | "the flux-corrected covariance" | app_negweight parenthetical "(corrected for audit finding J28)"; label table |
| VL170 | the rebuilt 300-replica 2D statistical band (App. G `coverage-fixed-truth`) | "the earlier rebuilt bootstrap" | label table |
| VL172 | the 2D covariance with that band, before the flux-band repair (App. J errata) | "an earlier covariance built before the flux-band repair" | label table |
| VL175 | the same after the flux-band repair (App. J, sec. "The VL175 construction") | "the earlier construction of App. J.x" | label table; App. J heading (not editable) |
| `KNOWN_ISSUES.md` 92 / 95 | tracker rows | "(App. G, `rvp1pi`)"; "(App. J errata)" | App. G / App. J |
| Stage-1, Stage-2 bootstrap | project phases; the two successive bootstraps had 50 and 300 replicas (app_history.tex:114-118) | "the superseded 50-replica bootstrap", "the 300-replica bootstrap" | -- |
| standard-P4 | the standard production chain's 5D covariance stage | "an earlier 5D covariance from the standard production chain" | App. G `p4-verifier` |
| Q | name of the quoted 2D covariance | "the quoted covariance" | -- |
| B3 | label of the GiBUU sampling-closure check | **kept verbatim** (required by BINDING-PHASE1-ADDENDUM-7 ruling 3); explained in the same sentence | sec_joint, protected span in apply_glossary.py |
| FPS | the extended-fiducial analysis | "extended-fiducial" | App. G tag `fps-battery` |
| `cv`, `mean` | the two five-axis covariance variants (unified-throw covariance centered on the central value / on the throw mean) | "the CV-centered variant", "the mean-centered variant" | parenthetical at first use in sec_systematics and sec:eavailw-adopted; label table |
| `lgbm`, `exact`, `hist`, exact-GBT | learner backends | "LightGBM", "exact-split", "histogram backend" | `\texttt{exact}` at its definition (sec:method-config); label table |
| July sweep, May sweep | the two 2D universe productions | kept as names | label table |
| MnvTune | MAT's name for MINERvA Tune v1 | "MINERvA Tune~v1" | the verbatim specification quote |

---

## E. Bookkeeping vocabulary (no status of its own; the fact behind it is kept)

| term | meaning | replacement |
|---|---|---|
| digest | SHA-256 of a file | "checksum"; "by digest identity" -> "by checksum identity"; "digest-bound exception" -> "an exception limited to the file with its checksum" |
| receipt, receipted | a machine-written record of a run | "record", "whose configuration was recorded", "originally recorded values" |
| lane | an analysis line of work | "analysis" |
| gate (process sense) | a check that stops a run | "a check stops the run"; "ledger-verified ... gated battery" -> "battery, recorded in the validation ledger with its passed published-region check against the control" (the ledger's "anchor gate PASS", VALIDATION_LEDGER.md:1611-1612). The statistical "decision gate" of sec:joint5d-frozen is defined there and kept. |
| discharge(d) | meet an obligation | "meet" |
| ledger-verified | verified in the validation ledger | "recorded with its validation checks" |
| NONQUOTABLE-DIAGNOSTIC | output flag | "labels every output as a diagnostic that must not be quoted" (identifier dropped) |
| design record | the analysis design document | "the analysis design" |
| campaign's self-validated | checked only by the run that did it | "the calibration run's own ..., validated only by that run itself" |
| contract | the stated procedure | "procedure" |
| sibling, these bytes, this object | the other variant; this file; this covariance | "the mean-centered variant", "this file", "this covariance" |
| rollup | the per-band sum | "band sum" |
| omnifile | event-loop output (App. I) | "event-loop output file" |
| headline (meaning "quoted number") | -- | "quoted total", "main tension", "quoted result"; kept where it means a measurement's main result |
| publication uncertainty product | -- | "quoted uncertainty" |

---

## F. Coined labels

| term | meaning | replacement |
|---|---|---|
| anchor (marginalization anchor, validation anchor, Jacobian anchor, "Anchor." item) | the check that marginalizing a higher-dimensional result reproduces the lower-dimensional one | "marginalization check"; "validation reference"; fps item "Published-region check"; figure panel "ratio to the control". Labels such as `sec:3d-anchor` are unchanged. |
| home(s) | the section where a topic is treated in full | "section(s)" |
| two invariants keep the result truth-tree authoritative | two conditions that make every reconstructed signal event part of the truth denominator | "Two conditions make the truth tree the complete reference for the simulated signal" |
| record-only (test, arm) | the response-mismatch test that rescales only the reconstructed Eavail of pseudo-data | "reconstruction-only"; in sec_validation "a closure that rescales only the reconstructed $\Eavail$ of the pseudo-data" |
| replay | a re-evaluation of predeclared tests with a changed input | "re-evaluation", "re-evaluates"; "standalone replay of the same code" -> "standalone rerun" |
| launcher | job script | "job script" |
| in-effect (adjective) | -- | "a truth change that is in effect a 10% signal-rate reduction" |

---

## G. Pointers and code identifiers

### G1. App. G tag pointers "(App.~\ref{app:provenance}, \texttt{tag})"
- **Kept** in the routed form that `check_body_pointers.py` requires (29 -> 30: one KNOWN_ISSUES row became a tag
  pointer). The circumlocutions around them were shortened ("gives the label under which it is recorded there" ->
  "its repository label is listed in App. G, ..."). Whether to move them to footnotes depends on the author's pending
  decision about App. G (open question Q3).

### G2. Code identifiers in prose
- Rule: describe what the code does; keep the identifier only as one `\texttt` parenthetical when a reader needs it
  to find the implementation.
- **Kept as parentheticals:** `CVUniverse::GetEAvailableTrue()`, `NewEavail()`, `Getq3True()`, `RecoQ3()`,
  `GetTrueExperimentersW()`, `RecoW()` (sec:eavail-definition and sec:eavailw-axis state that the definitions *are*
  the code's); `hXSec2D`, `hXSec_pt`, `hXSec_pz` (merged into one parenthetical); `--bkg-mode` (once);
  `MNV101_ACTIVE_UNIVERSE` (once); `--add-norm 0` (once); MAT classes in App. A.2.6 (sec:minerva), whose subject is
  MAT's implementation; the NumPy calls in App. A that specify the estimator.
- **Removed:** `NONQUOTABLE-DIAGNOSTIC`; backend names `lgbm`, `exact`, `hist` in running prose.

---

## H. Not changed in this batch (for the chapter batches)

- **Development history** (HIST): dates such as "Since 2026-10-11", "until 2026-10-11", "(2026-07)", "An earlier
  version of this sentence ...". The *term* "exact-split" is kept as the name of configuration (b); its history
  narrative is register work.
- **five-axis / five-dimensional**: synonyms used 21 / 38 times; pick one per chapter batch (recommended:
  "five-dimensional", which the paper uses).
- **driver, event loop, engine**: defined in App. I; kept.
- Acknowledgments, AI-use, funding, `\pubhold`, the release paragraph of sec_summary, and Apps. G-J: untouched.
