# Round r21 on the paper: outline (2026-10-29)

**Status:** an outline for the director's approval. Nothing in the paper has been written.

**Under:**
- `DECISION-20261028-joseph-protections-remade-and-r21.md` item 5: one more scored round, with its method, adoption and
  stop rules those of `DECISION-20261025-joseph-register-rounds-paper-rewrite.md`. After r21, register rounds on the
  paper close again.
- The evidence base is `register-retrospective-20261028/REPORT.md`, as the director ruled.

**Base:** the paper after the four protection edits: main `78df7327`, which is #492 merged. The branch
`paper/r21-20261029` was fast-forwarded to it before step 0.

## 1. The operation: one, chosen from the evidence

**A whole-text rewrite from a reverse outline and a fact ledger, by a writer with no history of the text.** The
evidence, from the retrospective:
- **For it (§4 item 2, §2):** the three rounds that rewrote the whole paper from an outline (r12, r17, r19) won 5 of
  their 6 sol runs at strength 2.
- **Against the alternative (§4 "Backfired"):** in-place rewording lost. The four rounds that reworded named passages
  (r13, r14, r16, r20) won 1 of their 8 sol runs at strength 2, and r20 lost 2 of 4.
- **What the operation will not do:** P1 has returned 3 in 39 of 39 runs on 13 versions, and removing a quoted passage
  has never raised it (§0, §3.3). P1 not falling is the realistic expectation, and the pairwise is where this round
  can win.

**Not done in r21:**
- rewording P1's quoted passages in place (r20's operation);
- moving content to the note (no new MOVE is decided);
- any change to facts, numbers, claims, scope, citations or figure meaning (DECISION-20261025 item 4).

## 2. Steps

0. **Baseline.** The paper changed after r20's measurement (#492: the low-stability cells, DA, the duplicate copies,
   Scope).
   - Build the base's blinded rater copy with `rater-calibration/make_rater_copy.sh`, record its sha256 and word
     count, and run P1 with sol2, 3 runs.
   - The base's quoted passages are the round's diagnostic, not its targets.
1. **The reverse outline and the fact ledger,** built by an independent read-only agent from the base:
   - **the outline:** one sentence per paragraph, section by section, saying what the paragraph does;
   - **the ledger:** every fact of the base, meaning every number, qualifier, condition, limitation, citation and
     cross-reference. Each fact carries its `P::`/`MP::` probe text, its macro (`\fvval{…}`, the `values.tex`
     macros) and its KEEP or guardrail status;
   - as in r19's ledger pass (357 facts), with a planted bad probe that the checker must catch.
2. **The writer.**
   - **Who:** a fresh Opus 5.5 subagent, given only:
     - the outline;
     - the ledger;
     - `WRITER-BRIEF.md`, adapted to the paper;
     - rules R1–R10 and the KEEP list (`register-prd-study/REPORT.md`);
     - the paper standard (`DECISION-20261023` item 2);
     - the protected list in §3.
   - **What it does not see:** the base's prose. It composes the paper body from the outline and the ledger, so its
     sentences are new and its facts are the ledger's.
   - **Batches**, sequential, in one writer session for coherence:
     - b1: I–III;
     - b2: IV;
     - b3: V;
     - b4: VI with the Discussion.
     Each batch carries its own ledger slice.
3. **Review.** Each batch gets a fresh independent two-direction reviewer. agy then runs on every printed passage,
   with a planted-strengthening control (P02 included). Each BLOCKING or SHOULD-FIX finding is fixed or recorded.
4. **Gates:**
   - the r21 ledger: every base fact probed, every changed base sentence covered, the protected spans byte-identical,
     no hand-typed numeral in new prose. It extends `paper-protections/check_ledger.py`;
   - `check_sec4_receipts.py` and its self-test, because the gate-bound phrases print verbatim;
   - the registry re-cites;
   - the `make_values_fived16` and `make_supplemental` checks;
   - reflow and absence-claims;
   - every `record-checks.yml` step (`fived16/HANDOFF.md` §5a);
   - a full build.
5. **Measure:**
   - the new blinded copy against the base's, both orders, sol2 and gemini;
   - P1 with sol2, 3 runs.
   - **Adoption** (DECISION-20261025 item 2): at least 3 of 4 pairwise wins, no sol2 order flip, and P1 not below the
     base's.
   - **If it is not adopted,** the paper returns to the base, as r20 did.
6. **Close.** Whatever the score, paper register rounds close after r21 (item 5). The report goes to the director,
   and the paper goes to Joseph's and Ben's read.

## 3. Protected in r21 (left as they are)

- **The title and the abstract,** which are Joseph's final wording.
- **The acknowledgments, the AI statement and the funding hold,** and every `\pubhold`.
- **Data Availability, as #492 set it.** It is released, but it was just truth-checked against the release package and
  the Supplemental Material. Re-wording it would need a new claim table (Q2).
- **The claims; the KEEP list's qualifiers; the honesty-required facts; and "Interval coverage has not been
  validated."** (item 4).
- **The gate-bound phrases of `check_sec4_receipts.py`,** which stay verbatim.
- **Every number,** which stays a macro. Tables, figures and captions keep their meaning; caption wording may change
  under the ledger.
<!-- absence-ok: lists the protected printed sentences r21 leaves as they are; not a claim that a result does not exist -->

## 4. Size

The base is about the size of r19/r20's measured copy, 7,404 blinded words; step 0 measures it. A rewrite from the
outline is expected to come out within about ±10% of that. This is an estimate, not a target.

## Questions for the director

1. **One operation, or also an APS copy-edit pass?** Should the writer brief include APS mechanical conventions
   (numerals, serial commas, punctuation), which the retrospective's §5 item 4 notes gemini named in r20? It is cheap,
   but its effect could not then be separated from the rewrite's. I recommend yes: r21 is the last round, so
   separating the effects matters less than the outcome.
2. **Data Availability in r21?** I recommend no: it stays as #492 set it, for the reason in §3.
3. **One writer for all four batches, or a fresh writer per batch** (the register-method default)? I recommend one
   writer session for the whole paper. The win the evidence records is a whole-text rewrite, and per-batch writers
   would make it four partial ones. A fresh reviewer per batch keeps the reviews independent.
4. **The base:** build on #492's head now and merge main as it lands, or wait for #492 to merge? I recommend starting
   step 0 and step 1 now, since both are read-only, and writing nothing until #492 merges.

## The director's rulings (2026-10-29): approved

1. **APS mechanical conventions go into the writer brief:** numerals, serial commas and punctuation. The r21 report
   records that they were added, so the rewrite is not credited with their effect.
2. **Data Availability is out of r21,** protected as #492 set it.
3. **One writer session for all four batches.** Reviewers stay fresh per batch, and the writer never sees the base's
   prose.
4. **Steps 0 and 1 start now,** read-only.

## The adoption rule, fixed before any score

This was committed before step 0 ran, so the rule predates every r21 score (the director's condition). r21 is adopted
if, and only if, all three hold:
1. **The pairwise:** NEW (the r21 paper) beats OLD (the base, main `78df7327`) in at least 3 of the 4 blind runs: sol2
   and gemini, each in both orders, with the paper prompt P2 on the blinded copies from `make_rater_copy.sh`.
2. **No sol2 order flip:** sol2 picks the same document in both orders.
3. **P1 does not fall.** Both of these hold for the 3 sol2 P1 runs on NEW, against the base's 3 runs from step 0:
   - NEW's mean is at least the base's mean;
   - NEW's lowest run is at least the base's lowest run.
   (For a base of 3, 3, 3, both mean that NEW scores 3 or more in every run, which is r19's form.)

If any of the three fails, r21 is not adopted and the paper stays at the base. Either way, register rounds on the paper
then close (DECISION-20261028-joseph-protections-remade-and-r21.md item 5). No re-run, extra run or changed prompt is
allowed after the scores are seen.
