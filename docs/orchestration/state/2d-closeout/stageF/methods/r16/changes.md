# Changes, passage by passage: register round r16

Base: origin/main 927f40bf (`paper_body.tex` identical at ff1f8595). Only `paper_body.tex` changed; `main_paper.tex`,
the note, the primer and the PET note are unchanged. Row ids in brackets are `ledger.md`'s.

## The five P1 targets

### 1. The rerun pseudo-experiments (Sec. VII C) [F10–F14]

- **Before:** "The pseudo-experiments that computing time limits interrupted or prevented (224 for calibration, 53 for
  power) were rerun; none reaches the observed statistic in any test or shifted null, so no assignment of the lost
  outcomes changes any decision."
- **After:** "Computing time limits interrupted or prevented 224 calibration and 53 power pseudo-experiments, and the
  decisions use the completed ones. When rerun, none of the lost calibration pseudo-experiments reaches the observed
  statistic in any test or shifted null, so their outcomes change no decision."
- **Decision: KEEP in the paper.** Table IV's B column counts completed draws only, so a reader needs to know what
  happened to the others.
- **A rewording of the §5 disposition, and one narrowing** (corrected by review fix 1):
  - "no assignment of the lost outcomes changes any decision" is Joseph's selected disposition
    (`DECISION-20261005-s5p-recompute-extension-and-lost-seed-recovery.md` §5: "no missing-draw assignment changes
    any decision"), and the note prints the same sentence in `sec:joint5d-lost`. After the recovery every submitted
    draw was observed, so the old clause was true. "So their outcomes change no decision" restates it in terms of
    the observed outcomes.
  - "none" now names the calibration draws, the population whose statistics the record compares with the observed
    statistic (`RECORD-20261006-s5p-lost-seed-recovery-resolution.md` §2, "k_rec = 0 for all ten tests").
- **Made explicit:** the decisions use the completed draws. The note states it, and Table IV's caption implies it.

### 2. "Descriptive ... do not re-grade" (Sec. VII E) [K1]

- **Before:** "These target-corrected evaluations are descriptive and do not re-grade the decisions of Table IV, which
  concern each prediction on the target it was generated for and stand."
- **After:** "These target-corrected evaluations are descriptive. The decisions of Table IV concern each prediction on
  the target it was generated for, and they stand." (Review fix 3: a full stop, not a colon, so that "they stand"
  does not read as the reason.)
- **Decision: KEEP the content.** It is decision-fixed: `DECISION-20261020-joseph-nuwro-ch-claim.md` says to keep the
  ten recorded decisions, and "descriptive" is KEEP-list E3's adjective. The record verb "re-grade" is replaced by its
  content, that the decisions stand. The note keeps "do not re-grade" (`sec:joint5d-ch`).

### 3. The five-iteration rule (Sec. III) [F1]

- **Before:** "Configuration (e) keeps five iterations under a rule fixed before the comparison, because 10, 15, or
  20 did not reduce the rule's measure of model dependence, the largest residual proxy over the development truth
  changes (note)."
- **After:** "Configuration (e) keeps five iterations by a criterion fixed in advance: 10, 15, or 20 iterations did
  not reduce its model dependence, measured as the largest residual proxy over the truth changes used in its
  development (note)."
- **Decision: KEEP the content.** That the criterion was fixed in advance is a methods fact a reader uses to judge the
  choice, so it stays. The rule's internal framing ("the rule's measure") is dropped. The rule itself, its J and H2
  cells and its values (0.314 against at least 0.384) print in the note, `sec:gbdt-model-dependence`.

### 4. The seed panels (Fig. 3 caption) [F5]

- **Before:** "Panel (a) uses the random seeds of the estimator's development studies; panel (b) uses separate
  assessment seeds, which also entered its later development."
- **After:** "Panel (a) uses the random seeds of the estimator's development studies, and panel (b) separate seeds
  that were later also used in its development."
- **Decision: KEEP as a disclosure.** The same caption calls the panel (b) shapes "not used while it was chosen", and
  Table II says "held-out shapes". The disclosure tells the reader that the pseudo-experiments were later reused in
  development, which the note states in `sec:gbdt-model-dependence` ("Because these samples were used during
  development, they provide no independent validation here").
- **Record:** commit a6b9c705 replaced an earlier "seeds not used before" label with this disclosure.
- **Panel (a):** its clause stays, because the note does not print, for that study, that it used the development
  seeds.
- **What changed:** only the record words "assessment seeds" and "entered".

### 5. The budget extension (Sec. VII C) [F7–F9]

- **Before:** "The calibration's computing budget was later extended by a bounded amount with observed p values
  visible; the error control above is unaffected by this, because it holds for any stopping rule."
- **After:** "The computing time available to the calibration was later increased by a bounded amount after the
  observed p values had become visible. The error control above does not depend on this, because it holds for any rule
  that decides when sampling stops."
- **Review fix 2:** "had been seen" became "had become visible", the record's word; nobody is recorded as having
  viewed them.
- **Decision: KEEP as a disclosure.** It is a choice made with the outcomes visible: KEEP list §4, "disclosing a post
  hoc choice next to the choice"; corpus 2504.06857:250.
- **Record:** `DECISION-20261004-s5p-production-budget-extension.md` §3. The extension was made during production,
  after the looks had become visible, and changed no statistic, criterion or decision rule.
- **Where it sits:** the paragraph that states the design's data-informed elements, directly after the rule whose
  bound covers it. The wording of the reason now matches the bound's own sentence ("whatever rule determines when
  sampling stops"). The sentence before it (the design fixed in advance; its reviewers had seen residuals) is kept,
  with "although" replaced by a semicolon [F7].
- **Pointer:** "The design record and the rerun are given in" becomes "The predeclared design and the rerun are
  described in" [F15].
- **Not added:** the purpose of the extension (to let the sequential rule reach its own stop rather than a budget
  stop) prints in the note, `sec:joint5d-frozen`. It was not added to the paper, under the no-new-claims rule.

## Other changes (target 2)

<!-- absence-ok: this record quotes the paper's own condition (i) and Sec. VIII A item 7, whose source lines carry their Search lines in paper_body.tex; it is not a new claim that a result does not exist -->
- **The scan's limits.** "the scan tests that one direction and bounds neither the actual residual nor the
  convergence" becomes "it probes that one direction". This was a restated caveat: condition (i) states that
  convergence is not shown and the residual unmeasured, and Sec. VIII A item 7 states that a demonstrated bound is
  needed. The note prints the scan's own statement, `sec:joint5d-kappa` [K2, K3].
- **Point estimates.** "The point estimates (k+1)/(B+1) carry no separate validity claim" becomes "The error control
  applies to the decisions, not separately to the point estimates (k+1)/(B+1)". This removes the record word
  "claim" [F6].
- **"Therefore" (Sec. IV B).** "The two-dimensional central value is therefore reproducible ..." loses "therefore".
  The sentence does not follow from the band history that r15 placed before it [F2].
- **The 2D closure sentence (Sec. V A)** is split in two (R10). The decision's wording, "is being moved to the refined
  estimator", is unchanged (`DECISION-20261023-joseph-2d-refined-integrate-ci.md` item 1) [F3, F4].
- **Source comments** were added at each change, naming the record. The file header gained an r16 line.

## Searched and left unchanged (target 2)

- **The earlier-band history in Sec. IV B,** a superseded construction: it stays, for two reasons.
  - Table I's 2D-covariance row gives "an earlier band failed coverage" as its test.
  - `check_sec4_receipts.py` binds the 97.7 % and 78.1 % values to this paragraph.

  Moving it needs a Table I change and a check repoint, which is a decision for the director.
- **"Is being moved to the refined estimator"** is the ongoing development the r15 P1 justification names. Its wording
  is decision-fixed (above).
- **"Does not meet the validation criteria of its specification" (Sec. V D)** uses the note's own wording
  (`sec:eavailw-adopted`). Left unchanged.
- **"A post hoc observation" (condition (ii)) and "In an exploratory sensitivity study"** are KEEP-list disclosures.
- **The scope paragraph, the Limitations list, the abstract, Table I and the CLAIM-ADDITION block** were not touched.
  The r15 gains are kept, and no per-sentence scope was reintroduced.

## Superseded r15 ledger rows

r16 supersedes these rows of `r15/ledger.md`, whose probes or coverage no longer hold on this branch. Their facts are
carried by the r16 rows named. `r15/check_ledger.py` run on this branch reports exactly these 11 failures:
- `G9` ("because it holds for any stopping rule.") → F9;
- `G10` ("so no assignment of the lost outcomes changes any decision.") → F13;
- `G26` (the CH "descriptive and do not re-grade" sentence) → K1;
- `G27` (the scan, "the scan tests that one direction ...") → K2, K3;
- `C4` ("the two-dimensional result is being moved to the refined estimator", now a sentence of its own) → F4;
- the coverage of the r15-base sentences `P73` → F1, `P114` → F2, `P124` → F3, F4, `P149` → F5, `P223` → F6 and
  `P224` → F7.

The r15 ledger keeps its validity at its own branch tip. r16's ledger is the one to check against this branch.

