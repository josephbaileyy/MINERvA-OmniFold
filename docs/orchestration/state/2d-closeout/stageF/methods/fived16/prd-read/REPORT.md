# The independent PRD-language read of the paper's 5D text, and agy's check of Q5 (2026-10-27)

**Asked for by** Joseph, through `DECISION-20261027-joseph-5d-wording-q2-q5-and-independent-prd-read.md`:
- items 2 and 3;
- Q3: "what do the independent PRD reviewers say?";
- Q1, Q4, Q7 and Q9: "Do the independent PRD language sessions agree? I notice some qualifications being made".

**Run by** the paper rewrite lane.

**CITABLE FOR:**
- what two outside language raters preferred on these inputs on 2026-10-27;
- the lane's check of each shortened form against the records.

**NOT CITABLE FOR:**
- any physics claim;
- a ruling on wording, which is Joseph's.

## Method

**Raters.** The calibrated pair of `../../register-method/HANDOFF.md`:
- `sol2`: gpt-6.1-sol through codex-school2. The log confirms `model: gpt-6.1-sol`.
- `gemini`: agy gemini-3.8-flash-high.

Both ran only through `register-method/tools/run_x.sh`, read-only, after a smoke test of each route.

**What the raters saw.** `inputs/excerpt.txt`, built by `tools/make_inputs.py`:
- **the paper's printed text,** with every value resolved and every reference numbered from the built paper's `.aux`. This is printed-wording.md §A and §C's paper part, with figure and table bodies left out;
- **for context only,** the two prose paragraphs of Sec. V E, so that Q9's "the study's envelope" has its referent;
- **nothing else:** no record, no packet and no recommendation. Each job's files had neutral names (`document_A.txt`, `manuscript.txt`), because `run_x.sh` prints each input's file name to the rater.

**The text predates the placeholder swap** (commit e277152c). One sentence printed differently from the paper now: "The note gives the cells, the central values and the per-group uncertainties.", where the paper now ends "… and the correlation matrix of the reported covariance." No rated clause is in that sentence.

**Q3** (`prompts/P2S.prompt.txt`) is the calibrated P2 format. It ran blind and pairwise: the three variants were differences in the final paragraph only, and each was compared with each of the others in both orders, with 2 replicates per model. That is 24 runs.

**The qualifications** (`prompts/PQ.prompt.txt`) asked about 26 clauses, numbered C01–C26 (`inputs/clauses.tsv`). For each clause the rater said AS-WRITTEN, BRIEFER (giving the shorter form), COMPANION or OMIT, with a reason. Question T, which is Q4, was asked alongside. There were 4 runs: each model once in the listed order and once reversed.

**One incident, voided.** The sol2 pool was launched twice by mistake, so its jobs raced. Both sol2 pools were killed and their outputs set aside unread. One sol2 pool was then rerun from empty, and every sol2 result below is from that rerun. The gemini pool was unaffected.

## Q3: the sensitivity sentence (P2, both orders; P2 is decisive)

| pair | sol2 (4 runs) | gemini (4 runs) | order flips |
|---|---|---|---|
| (i) three sentences against (ii) one short sentence | (i) 4/4 | (i) 4/4 | none |
| (i) against (iii) one long sentence | (i) 4/4 | (i) 4/4 | none |
| (ii) against (iii) | (ii) 4/4 | (ii) 4/4 | none |

**The ranking is (i) > (ii) > (iii) in all 24 runs,** with no slot bias (A won 6 times and B 6 times, per model).

**The raters' reasons:**
- **sol2:** "Separate sentences make the numerical comparison easier to follow and avoid A's compressed use of 'against'."
- **gemini on (ii):** its ", against at most 18 % for …" is "an unidiomatic, journalistic use of 'against'".
- **gemini on (iii):** it is "a cumbersome, 54-word run-on sentence".

(i) is the drafted text.

## Q4: χ² precision in the paper's table (question T)

| | sol2 fwd | sol2 rev | gemini fwd | gemini rev |
|---|---|---|---|---|
| choice | one decimal | one decimal | integer | integer |

**The raters do not agree.**
- **sol2** chose one decimal: it "preserv[es] small differences between the full and shape-only statistics".
- **gemini** chose integers: "for χ² values of this magnitude with 7 to 16 degrees of freedom, the statistical variance makes fractional digits physically meaningless".

The draft prints integers, and the note prints two decimals.

## The qualifications: verdicts, and whether each shortened sentence stays true

**Truth column legend:**
- **"true"** means the clause can be cut or shortened, as the raters propose, and the printed sentence stays true as read. The fact is still in the note.
- **"false as read"** means cutting it makes the sentence false as a reader takes it. The shortest true form follows.
- The records cited are the ones the integration already uses (`../ledger.md`).

| # | clause (short) | sol2 ×2 | gemini ×2 | agreement | truth of the cut or shortened sentence |
|---|---|---|---|---|---|
| C01 | "is reported separately from those reporting definitions" | BRIEFER, BRIEFER | OMIT, BRIEFER | all would shorten | **"is also reported": true.** sol2's "uses a different binning from those studied above" is false: the 16 cells are merges of the study's H2 boxes. |
| C02 | the 27 supported boxes, the purity merge, 4 unreported, the support rule | BRIEFER, BRIEFER | COMPANION, COMPANION | split | **True either way;** the note's §10.1 keeps every count. sol2's two forms are true. |
| C03 | **Q9** envelope sentence | BRIEFER ×2 | BRIEFER ×2 | 4/4 shorten | **True:** "Unlike the envelope of Sec. V E, its model term is a covariance built from three generator shifts." gemini's "Its model covariance is built from three generator shifts" is true but drops the contrast that Q9 exists for. sol2's "uses five shifts" misdescribes the envelope, which is the largest of five shifts. |
| C04 | "a training-seed term measured to be zero" | COMPANION ×2 | OMIT ×2 | all would move or cut | **True** (the term is zero, and the note keeps it). |
| C05 | **Q1** "generator-shape model dependence, unscaled and not a calibrated bound" | BRIEFER ×2 (keep "not a calibrated bound") | BRIEFER ×2 (drop it) | 4/4 shorten; split on what goes | **Without "not a calibrated bound": false as read.** gemini's "generator-shape model uncertainty" reads as a calibrated 1σ term, and `cmodel_5d.json`'s label says it is not one. "unscaled" can go: **"it is generator-shape model dependence, not a calibrated bound"** is true. |
| C06 | **Q1** "its coverage at truths held out of its construction has not been validated" | AS-WRITTEN ×2 | OMIT ×2 | split by model | **The sentence stays literally true, but keep the clause.** gemini's reason shows the misreading it prevents: "the empirical validation of coverage across held-out truths is explicitly reported in the very next paragraph". The records say no held-out truth exists (FD-PLAN §3.6), and F0b is NOT CITABLE FOR coverage. The paper's fake-data paragraph does not repeat the note's "These are not held-out truths". |
| C07 | C_resp excludes neutron and muon deposits, … | AS-WRITTEN, BRIEFER | COMPANION ×2 | split | **True** (the definition lists its species positively, and the note keeps the exclusions). sol2's "it excludes neutron and muon deposits and response effects beyond the specified scales" is true. |
| C08 | C_resp "does not enter the generator tests of Sec. VII or the paper's other results" | BRIEFER ×2 | BRIEFER ×2 | 4/4 shorten | **Finding: the drafted clause is ambiguous,** because Sec. VII now contains VII B, whose comparison uses C_resp. sol2's "excluded from the generator tests of Sec. VII and all other results" is **false as read**. True and unambiguous: **"it enters only the sixteen-cell result, its fake-data tests and its comparison in Sec. VII B"**, per cresp.json's label and the note's §10.2. |
| C09 | "(6.74% without C_resp)" | AS-WRITTEN ×2 | AS-WRITTEN ×2 | 4/4 keep | — |
| C10 | "so that no such truth is compared with a covariance that includes its own generator's component" | OMIT ×2 | OMIT ×2 | 4/4 cut | **True;** the preceding clause states it. |
| C11 | "6 further truths, whose offset correction failed its control, are ungraded and given in the note" | COMPANION, BRIEFER | COMPANION ×2 | 3/4 move | **Cut entirely: "we unfold pseudo-data at 12 truths" then reads as the whole study, but 18 were unfolded.** Shortest complete form: **"6 further truths are ungraded (the note gives them)"**. |
| C12 | "Under the reported covariance, without the GiBUU component for the two GiBUU truths" | AS-WRITTEN ×2 | AS-WRITTEN ×2 | 4/4 keep | — (a reviewer's blocking fix) |
| C13 | "the reported uncertainty does not cover the fake-data bias at these GiBUU-like truths or at the q_3 tilt" | AS-WRITTEN, BRIEFER | AS-WRITTEN ×2 | 3/4 keep | Keep: this is the wording of Joseph's f0-limitation decision. sol2's "the biases … exceed the reported uncertainties" is stronger: Stage 0c GiBUU is listed by one cell at z = 2.01, with p = 0.062. |
| C14 | "no diagonal-only χ² is formed" | OMIT ×2 | OMIT ×2 | 4/4 cut | **True.** Joseph's presentation decision (item 3) bars printing a diagonal χ², not saying that none is printed. |
| C15 | GiBUU "compared on the 8 cells with p∥ < 4.5 GeV/c only" | AS-WRITTEN ×2 | AS-WRITTEN ×2 | 4/4 keep | — |
| C16 | "The reported uncertainty does not cover the fake-data bias at the GiBUU-like truths (Sec. V F)." | AS-WRITTEN ×2 | AS-WRITTEN ×2 | 4/4 keep | — |
| C17 | "NuWro and GiBUU are on carbon, with no correction to CH" | AS-WRITTEN ×2 | AS-WRITTEN ×2 | 4/4 keep | — |
| C18 | "Because C_model is built from shifts toward …, those comparisons use a covariance built in part from the compared generator, …" | BRIEFER ×2 | BRIEFER ×2 | 4/4 shorten | **True:** sol2's "The GENIE + MEC, NuWro and GiBUU comparisons use covariance contributions derived from those generators; GENIE CV enters as their common reference." gemini's "the comparisons are not independent of the tested models" covers Tune v1 too, which the records do not support. |
| C19 | **Q7** Scope: "… also has total uncertainties, whose coverage is not validated." | AS-WRITTEN ×2 | BRIEFER ×2 (drop the coverage clause) | split by model | **Without the clause: false as read.** The Scope sentence before it says that 3–5-observable results lack validated intervals, so the 16-cell sentence would read as the validated exception (director ruling 3; ledger guard G3). |
| C20 | "This bias is not included in the uncertainties quoted for the configuration-(a) central value." | AS-WRITTEN ×2 | BRIEFER ×2 (drop the product name) | split by model | **gemini's "not included in the reported uncertainties": false as read,** because "the reported uncertainty" names the sixteen-cell covariance (Sec. V F). |
| C21 | "No uncertainty quoted for the configuration-(a) central value includes the regularization bias, and its five-observable covariance omits it." | BRIEFER ×2 | BRIEFER ×2 | 4/4 shorten | **True:** "The configuration-(a) uncertainties omit the regularization bias." gemini's "The five-observable covariance omits regularization bias" names neither of the two 5D covariances. For the sixteen-cell one, the records make no such reading (Q1). |
| C22 | **Q1** repeat (Generator-sized truth changes): "unscaled and not a calibrated bound, and Sec. V F gives …" | BRIEFER ×2 (keep) | BRIEFER ×2 (drop the qualifier) | 4/4 shorten; split on what goes | **As C05.** sol2's "unscaled and not a calibrated bound; the bias tests are reported in Sec. V F" is true. gemini's forms are false as read. |
| C23 | config-(a) seed pair | BRIEFER ×2 | COMPANION ×2 | split | **True either way** (this is existing config-(a) text, and the note keeps it). |
| C24 | Limitations: "central values without intervals of validated coverage, and no uncertainty quoted for the configuration-(a) …" | BRIEFER ×2 | BRIEFER ×2 | 4/4 shorten | **sol2's forms are true. gemini's are false:** "presented as central values" denies the sixteen-cell total uncertainties. |
| C25 | Limitations: "The sixteen-cell result also has total uncertainties, whose coverage is not validated; …" | BRIEFER ×2 (keep coverage) | BRIEFER ×2 (drop coverage) | 4/4 shorten; split on what goes | **sol2's "… whose coverage has not been validated; Sec. V F reports the bias tests." is true.** gemini's "total uncertainties evaluated against mock data" reads as validation, so it is false as read. |
| C26 | the label "the configuration-(a) central value" | AS-WRITTEN ×2 | BRIEFER ×2 ("the nominal …") | split by model | **"nominal" is false:** configuration (a) is not the nominal estimator, and the sixteen-cell result is configuration (e). A rename would be a naming decision. |

**Agreement:**
- **Within each model,** the two list orders agree on 22 of the 26 clauses.
- **Unanimous across the four runs:**
  - shorten C03, C05, C08, C18, C21, C22, C24 and C25;
  - cut C10 and C14;
  - keep C09, C12 and C15–C17.
- **The models split** on C02, C04, C06, C07, C19, C20, C23 and C26. The pattern is consistent: gemini removes limitations ("apologetic qualifications", "defensive disclaimers") and internal labels, while sol2 keeps them and shortens the wording.
- **Every gemini form that drops a limitation** (C05, C06, C19, C20, C22, C24, C25 and C26) fails the guardrail.
- **The sol2 forms** fail it in two cases only: C01 fwd and C08.

**Unanimous and true.** These cuts and shortenings are unanimous across raters and leave every sentence true:
- C10 and C14, cut;
- C03, C18 and C21, shortened to the forms above;
- C08, to the unambiguous form above.

They are not applied: the printed wording is Joseph's.

**The raters' OTHER lists** (`runs/PQ-analysis.txt` and the run files) add:
- **sol2 would move the truth inventory to the note.**
- **sol2 would shorten the Q5 sentence** to "the remaining nine truths satisfy both criteria".
- **gemini** would replace "configuration (e)" and "the note" with descriptive names and a formal citation.

## Q5: agy's check of the decided sentence (decision item 2)

**The inputs** (`q5/`) are FD-PLAN §3.6 and §7 item 2, FD-F0b-DECLARATION §2's pull definition, and FD-F0b-REPORT §§5–6. Beside them is each graded truth's largest |z| and largest |b|/σ with the noise term N removed, both computed from `fd_f0b_readout.json`. The planted control replaces 2σ with 1σ.

| sentence | agy |
|---|---|
| decided: "At the other 9 truths the bias stays within the reported uncertainty by both criteria: no cell beyond 2σ and p ≥ 0.01." | **FALSE.** "the bias 'stays within the reported uncertainty' is false because a 2σ threshold permits bias up to twice the uncertainty": A7 NuWro reaches 1.34σ in a cell. |
| control: "… no cell beyond 1σ …" | FALSE, correctly: W3 and A7 NuWro fail. |
| alternative 1: "At the other 9 truths the bias passes both criteria: no cell beyond 2σ and p ≥ 0.01." | TRUE |
| alternative 2: "At the other 9 truths the bias is within 2σ in every cell and p ≥ 0.01." | TRUE ("matches") |

**The lane's own check:**
- the criteria are FD-PLAN's (|z| > 2 or p < 0.01, against the leave-own-out matrix);
- z = b/√diag(C + N), where N is at most 1.9 % of σ in any cell;
- the nine truths' largest |b|/σ is 1.34 with or without N;
- each truth's grade matrix is at most the reported covariance (the difference is PSD), so both criteria also hold against the reported covariance itself.

**So the numbers hold. What fails is the reading that "within the reported uncertainty" invites,** namely within 1σ. The decided sentence is in the PR as Joseph chose it, under ledger row Q5. The decision requires agy's agreement, and agy did not agree, so the wording goes back to Joseph with the two alternatives that agy accepts.

## Files

- `prompts/`
- `inputs/` (the excerpt, the clauses, the three Q3 variants and the two PQ inputs)
- `runs/` (28 rater outputs, `status.tsv`, `P2S-analysis.txt` and `PQ-analysis.txt`)
- `tools/` (the input builder, the job writer, the two analyses and the pool runner)
- `q5/` (agy's check, with its control and the alternatives)

## Applied to the final draft (director, 2026-10-27, after this read)

**The rule.**
- Apply every shortening and cut that is unanimous across the four runs and stays true.
- Where the models split, apply sol2's form if it is true, and keep the base text otherwise.
- Never apply an agy form that drops a limitation.
- Q3: keep (i). Q4: keep integers, because the raters split.
- Plus two accuracy fixes and one truth fix (Q5).

Each applied change has a ledger row, `F-<id>`, whose N: probe holds the new text and whose X: probe holds the old (`../ledger.md`).

| # | raters (sol2 ×2 / agy ×2) | applied | why |
|---|---|---|---|
| Q5 | agy: decided form FALSE; alternative 1 TRUE | **"At the other 9 truths the bias passes both criteria: no cell beyond 2σ and p ≥ 0.01."** (paper and note) | **Changed for truth.** Joseph's form, "stays within the reported uncertainty", reads as within 1σ, while the criterion allows 2σ (A7 NuWro reaches 1.34σ). This form states his chosen criteria exactly. |
| C01 | BRIEFER, BRIEFER / OMIT, BRIEFER | base kept | sol2's fwd form is false (a "different binning"). The director's list keeps the base. |
| C02 | BRIEFER ×2 / COMPANION ×2 | "…(edges): each supported box with purity below 0.1 is merged into a neighbour, 4 boxes remain unreported, and every reported cell passes the support rule." | **Split, so sol2's form (true).** The 27 supported boxes stay in the note's §10.1. |
| C03 (Q9) | BRIEFER ×4 | "Unlike the envelope of Sec. V E, its model term is a covariance built from three generator shifts." | Unanimous; the shortest true form. |
| C04 | COMPANION ×2 / OMIT ×2 | "a training-seed term measured to be zero" cut from the paper | The term is zero, and the note keeps it. |
| C05 (Q1) | BRIEFER ×4 | "it represents unscaled generator-shape dependence, not a calibrated bound" | **sol2's form.** It keeps "not a calibrated bound"; agy's forms are false as read. |
| C06 | AS-WRITTEN ×2 / OMIT ×2 | clause kept; **"These are not held-out truths."** added to the paper's fake-data paragraph | **Accuracy fix.** agy read the fake-data study as held-out validation (FD-PLAN §3.6: no held-out truth exists). |
| C07 | AS-WRITTEN, BRIEFER / COMPANION ×2 | base kept | sol2's two runs disagree. |
| C08 | BRIEFER ×4 | "and it enters only this result, its fake-data tests and its comparison in Sec. VII B." | **Accuracy fix.** Sec. VII B uses C_resp, so "the generator tests of Sec. VII" was ambiguous. |
| C09 | AS-WRITTEN ×4 | kept | — |
| C10 | OMIT ×4 | cut | Redundant with the preceding clause. |
| C11 | COMPANION, BRIEFER / COMPANION ×2 | "6 further truths are ungraded (given in the note)." | The shortest form that keeps the count of unfolded truths complete. The reason, the failed offset control, is in the note. |
| C12, C13 | AS-WRITTEN (C13: 3 of 4) | kept | C13 is Joseph's f0-limitation wording. |
| C14 | OMIT ×4 | "; no diagonal-only χ² is formed" cut | Joseph's presentation decision bars printing a diagonal χ², not saying that none is printed. |
| C15–C17 | AS-WRITTEN ×4 | kept | — |
| C18 | BRIEFER ×4 | "The GENIE + MEC, NuWro and GiBUU comparisons use covariance contributions derived from those generators; GENIE CV enters as their common reference." | **sol2's form (true).** agy's covers Tune v1, which the records do not support. |
| C19 (Q7) | AS-WRITTEN ×2 / BRIEFER ×2 | kept | agy's form is false as read (ruling 3; guard G3). |
| C20 | AS-WRITTEN ×2 / BRIEFER ×2 | kept | agy's form is false as read. |
| C21 | BRIEFER ×4 | "The uncertainties of the configuration-(a) central value omit the regularization bias." | sol2's form. |
| C22 (Q1) | BRIEFER ×4 | "…unscaled and not a calibrated bound; Sec. V F reports the fake-data tests of the estimator's bias." | **sol2's form.** It keeps the qualifier. |
| C23 | BRIEFER ×2 / COMPANION ×2 | "The seed dependence of this five-observable covariance was studied with only one seed pair." | **Split, so sol2's form (true).** |
| C24 | BRIEFER ×4 | "The higher-dimensional central values lack intervals of validated coverage, and the uncertainties of the configuration-(a) five-observable central value omit its regularization bias (Sec. V B)." | sol2's form. |
| C25 | BRIEFER ×4 | "…whose coverage is not validated; Sec. V F reports the fake-data tests of the estimator's bias." | **sol2's form.** The coverage clause stays (G3). |
| C26 | AS-WRITTEN ×2 / BRIEFER ×2 | kept | agy's "nominal" is false. |
| Q3 | (i) 24/24 | (i), as drafted | — |
| Q4 | one decimal ×2 / integer ×2 | integers, as drafted | **Split.** Integers match Joseph's example and the comparators. |
<!-- absence-ok: quotes or proposes the paper's printed text (scope and coverage statements of the sixteen-cell result and the configuration-(a) product) as this record's inventory or plan; not a new absence claim -->
