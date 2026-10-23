# Changes, paragraph by paragraph: register round r15

Base: origin/main afb7e1fa. Each line names the paragraph (`outline.md` ids), what changed, and the rule or record
behind the change. Sentence-level facts and probes are in `ledger.md` (row ids in brackets).

## Abstract (`main_paper.tex`)

- **Sentence 3 is split in two (R10).** The envelope clause becomes "With a model-dependence envelope added to the
  uncertainty, no tested reporting definition meets our 10% precision criterion". The dependence is carried by the
  order (KEEP list E1, E8) [A2].
- **The last two sentences become one (R8).** "As an illustration, simulation-calibrated tests of hybrid null
  hypotheses for five generator predictions all reject at the 5% familywise level, with no evidence of gain over
  matched coarse projections." Both KEEP-list qualifiers stay [A3, A4].
- **What left the abstract, and where it now prints:**
  - "Not physical exclusions" and the missing recoil band: the Sec. I scope paragraph [A5, A6].
  - The convergence assumption: condition (i), with its consequence in Sec. VIII A [A7].
  - The NuWro clause: Sec. VII E only, by DECISION-20261023 item 3a [A8].
- **The source comment at the old `:86`** now records the NuWro move and the decision that made it.
- **Size:** 135 → 114 words.

## I. Introduction and scope

- **¶2.** The pointer to Sec. II is dropped. Sec. II follows directly [I1].
- **¶3.**
  - Table I is described as listing configuration and test. The limitation column is gone (R2) [I2].
  - The secondary application drops "specified" and its calibration clause. The scope states the calibration once
    [I3, I4].
- **Table I.**
  - The "Principal limitation" column is removed (R2: "do not print the same limitation in three places"). Each of
    its nine cells is accounted for in `ledger.md` rows I6–I14.
  - The table is now single-column, with every other cell unchanged [I5].
  - The caption points to Sec. VIII A.
- **¶4, the scope paragraph, rewritten (R1).**
  - It is stated positively, with the naming convention "Throughout, a three- to five-observable result is a
    central value …" [I15, I16].
  - It keeps the meaning-bearing negatives: no validated coverage, not a validated measurement, not exclusions, no
    measurement uncertainty [I17, I19].
  - It states the calibration "within the implemented simulation model" once, with the missing recoil band
    [I19, A6].
  - It points to Sec. VIII A [I20].
  - The paragraph was reflowed so that the registry-cited lines 285, 291 and 311–319 keep their line numbers (REPORT
    §7).

## II. Data, observables, and domains

- **¶7.** The 135 MeV effect is given by its bound only (E2), with no "negligible" added [D1]. The 0.67% migration
  and the materiality hedge print in the note, `sec_3d.tex` [D2, D3].
- **¶8.** The "simultaneous, not independent" restatement is dropped, because Sec. I says it [D4, D5]. The two
  definition pointers are merged into one clause at the end of the paragraph [D6].
- **¶9.** The axis and generator pointers are merged into one clause at the end of the paragraph [D7, D8].

## III. Estimators and validation design

- **¶13.** The training-details pointer becomes a plain clause [M1].
- **¶14.**
  - The Table II pointer moves into the sentence [M2].
  - The configuration-matrix pointer is dropped, because Table II's caption carries it.
  - "Bias in simulation" becomes "bias" [M3]. The lines the registry cites (285, 291) are byte-identical.

## IV. Two-dimensional benchmark

- **¶16, rewritten after E3.**
  - The χ² is "the descriptive covariance-weighted distance" in one sentence (KEEP: "descriptive") [B1].
  - The post-selection fact stays at the choice [B6].
  - "So a reproduction rather than an independent validation" and "its source has not been identified" move to
    Sec. VIII A, item 2 [B3, B7].
  - "Included in no term of the covariance" is collapsed into ¶17's omission sentence [B9].
  - The cross-covariance aside goes: the Fig. 1 caption and the note carry it [B10].
- **¶17.**
  - The three mid-sentence pointers become one clause at the end of the paragraph [B11].
  - The block-sum assumptions and the two-universe tests move to the note (R5) [B12, B13].
  - The omission list of ¶20 joins here as one plain sentence (KEEP list E5) [B14].
  - The parametrized-family assumption moves to the note [B15].
- **¶18.** "Size not validated; its consistency check cannot fail" moves to Sec. VIII A, item 1 [B16].
- **¶19.**
  - The replica-mean offset moves to the note (E4) [B17].
  - "Coverage … has not been tested" moves to Sec. VIII A, item 1 (E4 allows it) [B18].
  <!-- absence-ok: this record quotes or paraphrases the paper's own absence statements (each carries its Search line in paper_body.tex or prints at afb7e1fa); it is not a new claim that a result does not exist -->
  - The two-band history shrinks to the first band's failed, pre-specified test, which supports Table I's "an
    earlier band failed coverage" [B19, B20].
  - **Kept against E4:** the post hoc rescoring sentence with 97.7% and 78.1%, because `check_sec4_receipts.py`
    binds those values to `paper_body.tex` (REPORT §6) [B21, B22].
- **¶20.**
  - The status sentence ("not independently validated; we claim no coverage …; no calibrated significance") moves
    to Sec. VIII A, item 1 [B23, B24].
  - "The two-dimensional central value is therefore reproducible …" stays, at the end of ¶19, where it followed in
    the original.

## V. Five observables

- **¶21.**
  - The closure-map pointer moves to the end of the paragraph [V1].
  - The Fig. 2 citation moves into the sentence.
  - The purity bias keeps "in simulation", because `check_sec4_receipts.py` binds the phrase [V2].
  - "This bias is not included in the quoted uncertainties" is now its own sentence (E6) [V3].
- **¶23.**
  - The Fig. 3 citation moves into the sentence [V4].
  - The pointer moves to the end of the paragraph [V5].
  - "Not included in the quoted uncertainties" and "(… which omits the regularization bias)" move to Sec. VIII A,
    item 4 [V6, V8].
  - The phrase "within the quoted total uncertainty in about half of those cells" stays, because the receipt check
    binds it [V7].
- **¶24.** The Fig. 4 citation moves into the outcome sentence (R4) [V9, V10].
- **¶25.**
  - The method of the diagnosis is named in its sentence. "Rather than measured directly" moves to the note [V11,
    V12].
  - "Source not established" moves to Sec. VI, where it is stated once [V13].
  - "Therefore no validated frequentist coverage" goes to the scope [V14].
- **¶26, after E7.**
  - "For one pair of seed settings … beyond a stability limit of 5%; we therefore quote no covariance-based
    generator significance" [V18].
  - The seed-pair spread and the fixed-seed bands move to Sec. VIII A, item 5, with the 26.0% kept. The
    either-direction detail moves to the note [V19].
  - The two pointers become one clause [V16].
- **¶27.** Two sentences are joined by a colon [V20].
- **¶28, after E8 and R9.**
  - The envelope is defined first.
  - "A sensitivity diagnostic that tracks the regularization bias, not an interval" stays as its own sentence. "Adds
    it linearly" would otherwise invite reading the sum as an interval.
  - The result follows the definition [V21–V24].

## VI. What limits the estimator

- **¶29.** The pointers become part of the sentence. The miscoverage sentence now states once that the source of
  the residual bias is not established [L-1, L-2].
- **¶30, the D-ID block.**
  - The Table III pointer moves into the sentence [L-3].
  - The repeated "on those same truth changes" is dropped, because sentence 2 of the block names them [L-4].
  - The out-of-scope sentence is unchanged (REPORT §3) [L-5].
  - A source comment records the ruling.
- **¶31.** The check list names Secs. IV and V in the sentence. "To the extent that …" is dropped here, because
  Sec. I and Sec. VIII A, item 9, state it [L-6, L-7].

## VII. Application

- **¶34.** "These comparisons are descriptive:" is dropped, because the subsection title says it [G1].
- **¶35–36.**
  - The two pointers are merged into one clause at the end of the paragraph [G2, G3].
  - The mismodelled-detector closure moves to Sec. VIII A, item 6 [G5].
  - "It does not locate an interaction mechanism" moves to the note, where it prints twice [G7].
- **¶40.** The calibration pointer, a repeat of ¶38's, is dropped [G8].
- **¶42.** The frozen-design and lost-experiment pointers are merged into one clause [G9, G10].
- **¶44, condition (i).**
  - The measurement and the geometric assumption stay [G11].
  - The carry-over condition moves to Sec. VIII A, item 7, kept whole [G12].
- **¶45–46, condition (ii).**
  - The either-direction mechanism moves to the note [G13].
  - "Net effect not measured" and "remain conditional on the hadronic response" move to Sec. VIII A, item 8 [G14,
    G17].
  - The post hoc projection result stays at its point [G15].
  - The sensitivity study's untested effects are one sentence with a plain pointer [G16].
  <!-- absence-ok: this record quotes or paraphrases the paper's own absence statements (each carries its Search line in paper_body.tex or prints at afb7e1fa); it is not a new claim that a result does not exist -->
- **¶48.** The margins pointer is dropped, because the conditions introduction already points to the same note
  section [G18].
- **¶50, the calibration-validity paragraph, removed.**
  - A1, the shared simulated events, the unvalidated lateral-shift conditioning and the missing null rejection rate
    move to Sec. VIII A, item 9 [G19, G21, G22, G24].
  - "Not a test of the data process" and "verifies the calculation, not …" move to the note (E10) [G20, G23].
- **¶51.**
  - Table IV is cited in the sentence [G25].
  - The CH replay sentence keeps DECISION-20261020's content [G26].
  - The κ scan keeps "bounds neither the actual residual nor the convergence", because the note does not print it
    [G27].
  - The three pointers are merged into one clause [G28].
- **¶52.**
  - "Within the implemented simulation model" is dropped, because the scope states it [G29].
  - The two pointers are merged into one clause [G30, G31].

## VIII. Discussion and conclusions

- **¶53–54, rewritten (R2, R5).**
  - The conclusions no longer re-list the limitations [C2–C5].
  - They keep the findings summary, the pointer to Sec. VI, and "provided the calibration is exact" (E10) [C1, C6,
    C7].
- **New subsection A, "Limitations" (`\label{sec:limitations}`).** Nine numbered plain declaratives (eight in the first commit; item 3 added by review fix 6), each stated
  once [C8 and the MOVE→L rows]. The source comment gives each item's record and carries the `Search:` lines for
  its absence statements.

## Review fixes (after the independent review, ADOPT-AFTER-FIXES, and the 4/4 pairwise result)

1. **Abstract.** "With a model-dependence envelope added linearly to the uncertainty". The no-definition-meets-10%
   verdict holds only for the linear sum: 9.6% + 1.4% ≥ 11.0% (`sec_5d.tex:339-345`). In quadrature it would be
   about 9.7%. [A2]
2. **IV B, the rescoring sentence.** "Against a second, rebuilt earlier band" restores the band's identity, so that
   the 97.7% cannot be read as the quoted block's coverage. Item 1 of Sec. VIII A says that block has had no coverage
   test. [B21]
   <!-- absence-ok: restates the paper's item 1 of Sec. VIII A, whose Search lines are in paper_body.tex; not a new claim -->
3. **V B pointer.** It now cites both note sections:
   - `sec:val-negweight`, which holds the 74% cell;
   - `sec:val-departure`, which holds the thirty-iteration −26% and the 16–31% figures (`sec_5d.tex:143`, `:236`).
   [V5]
4. **The RE-1 integration ledger.** `re1-integration/check_ledger.py` fails on this branch, by design, for rows
   E17, E18 and C19 and for its main_paper.tex protection.
   - **What supersedes those rows.** r15 rewrote the sentences they probe: Table I's limitation column, the old
     conclusions, and the abstract. r15 supersedes those rows; r15's ledger carries their facts (rows I9, C4, C5 and
     the abstract rows).
   - **What changed in that checker.** Its `--base` default is pinned to the RE-1 integration's base 08fac419,
     instead of the moving origin/main. Its docstring states that it is valid for trees up to afb7e1fa, and how to
     run it there.
   - **Its checks are unchanged.** At afb7e1fa it gives LEDGER PASS (102 rows) and SELF-TEST PASS.
5. **Tooling.** In a separate commit, `tools/registry/results_index.py` and `test_registry.py` find the
   `configuration~(a)` line by its digest, not by line 285.
6. **Small points.**
   - "The following limitations apply to the study's results."
   - Item 9 (formerly 8): the lateral-shift clause is now its own sentence (R10). [G22]
   - New item 3: "The source of the residual bias behind the miscoverage of Sec. V C has not been established."
     - Sec. VI goes back to afb7e1fa's same-origin wording, so each fact is stated once.
     - The item fills Table I's former "source of the residual bias not established" cell. [I11, V13, L-2]
     - Items 3–8 of the first commit are now items 4–9.

