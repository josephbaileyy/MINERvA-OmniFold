# Audit of the grandfathered absence claims (2026-10-27)

**Authority:** the director's ruling of 2026-10-26, queued after the TeX reflow (#396). The claims were listed in `tex-reflow-20261026/grandfathered-absence-claims.txt`. The director ruled on the findings on 2026-10-27.

**What it is:** each claim got a real search, by meaning. Then, per paragraph:
- a `% Search: … @ sha` line, or a scoping waiver with its reason; or
- an accuracy fix under the guardrail, where the claim was false as read. A fix narrows the claim to its home and adds no new result.

Anything that adds a printed fact goes to Joseph. This PR is separate from the register round n3.

**Who:**
- **Research:** four Claude Opus 5.5 subagents of the paper rewrite lane's claude-school session, read-only. Their write-ups are in `research/G1.txt`–`G4.txt` and their brief in `research/BRIEF.txt`.
- **Verification, fixes and this report:** the lane, Claude Opus 5.5.
- **agy (gemini-3.8-flash-high, through `run_x.sh`):** the accuracy fixes.

## The count

The list has 20 claims. Judging every line of the note, paper and primer sources at `0d919b1a` with `absence_claims.py`'s own `judge()`, instead of only the lines the reflow changed, finds **21** bare absence claims.

The extra one is a table cell in `sec_pet_campaigns.tex`, "coverage unmeasured" for PET L128S1T24 at K=4. Its paragraph was already one line, so the reflow never touched it. It is true, on the same evidence as the coverage paragraph G4 checked (`DECISION_RECORD-pet-final-design.md:48`), and it gets a Search line here.
<!-- absence-ok: quotes or summarizes the audited sentences of the note, paper and primer, before or after this audit, as its record; not a new absence claim -->

| verdict | claims | what this PR does |
|---|---:|---|
| true as scoped, or scoping | 17 (16 listed + the table cell) | a Search line or a waiver, after a mechanical check that every cited `file:line` exists in range at the cited commit |
| false as read: an accuracy fix narrows the claim | 2 sites in the note (§PET's "remains untested"; the ES's "The one … coverage test"), plus the primer's copy of the second | the fix, an ACC row, agy, and then a Search line |
| false as read, adds a printed fact: Joseph's | 2 (`sec_eavailw.tex`'s pT-axis clause; `app_history.tex`'s positive-semidefiniteness sentence and its "no substitution" clause) | **not edited.** Drafts went to the director, who will put them to Joseph |
<!-- absence-ok: quotes or summarizes the audited sentences of the note, paper and primer, before or after this audit, as its record; not a new absence claim -->

**Primer and paper strength fixes** (not absence claims; director's item 3): two primer sentences and one paper sentence said more than their homes, and a primer source comment quoted paper wording that no longer prints. These are fixed with ACC rows and agy.

**After this PR,** `judge()` over every line finds 2 bare absence claims, the two held for Joseph. It found 21 before.

## The accuracy fixes (`ledger.md`, rows ACC-A1 to ACC-A7)

| row | site | before | after | home |
|---|---|---|---|---|
| A1 | sec_pet_campaigns.tex, "Where generator recovery is lost" | "The effect of omitting scalar true $\Eavail$ and $q_3$ from PET's truth inputs remains untested." | "… from PET's truth inputs on the generator cases (NuWro, NuWro$'$, GiBUU) remains untested." | `generator_diagnosis/REPORT-20261006.md:66-67`, "untested here". Nominal and development-tilt tests exist: `improvement_campaign/REPORT-20260922.md:181`; `final_design/DIAGNOSTICS-20260925.md:105`, `:118-120` |
| A2 | sec_execsummary.tex, "Principal limitations" | "The one five-dimensional coverage test, of bias-corrected statistical intervals of a deterministic estimator variant, …" | "The one end-to-end independent-truth coverage test, of bias-corrected statistical intervals of a deterministic five-dimensional estimator variant, …" | `sec_5d.tex` sec:coverage-5d, "An end-to-end independent-truth test assessed …". The development assessment of candidate R (`sec_5d.tex:179`) is a second 5D interval check. **The false wording was round n2's, from the lane's own review fix** |
| A3 | primer_body.tex, the fixed-truth test | "The main cause of the shortfall was found and removed, and the statistical bars now quoted were built again, …" | "Part of the shortfall was traced to one ingredient of those bars, and they were rebuilt without it. The statistical bars now quoted are a separate set, …" | `sec_validation.tex`, "The attribution is partial"; "The band was then rebuilt without this term. The quoted statistical block is a third, different ensemble" |
| A4 | primer_body.tex, "Four limits" | "the one direct test of it" | "the one end-to-end test of it against independent truths" | as A2 |
| A5 | primer_body.tex, seed effect | "shifts by about 6%, more than the 5% …" | "… in the projected quantity it affects most, more than the 5% …; measures that ignore the correlations between cells stay within it." | `sec_5d.tex:306`: s_proj is the correlation-sensitive measure, and "The diagonal-only measures pass". s_proj is a maximum over the declared functionals (`AMENDMENT-20260911-…:41-43`) |
| A6 | paper_body.tex sec:cov5d | "by about 6.1%, beyond a stability limit of 5%." | "by about 6.1% in the most affected projected quantity, beyond …; measures of the diagonal alone stay within it." | as A5 |
| A7 | primer_body.tex source comment | quoted paper wording that no longer prints | names sec:cov5d's current wording | `paper_body.tex` sec:cov5d |
<!-- absence-ok: quotes or summarizes the audited sentences of the note, paper and primer, before or after this audit, as its record; not a new absence claim -->

**Notes on the fixes:**
- **No number is added.** A5 and A6 do not print "43 functionals". The note does not print that count for s_proj; it prints the 43 projection functionals only for the central-value shifts (`sec_5d.tex:312`). An earlier message of the lane's said it did, wrongly.
- **agy:** 5 of 6 AGREE in run 1. Its one REVISE was A3: "Most of the shortfall" claimed more than "The attribution is partial". It changed to "Part of", and run 2 AGREEs. The runs are in `agy/`.
- **printed_diff:** only the ledger's sentences change.
- **The "one … test" wording, checked against the other two 5D interval checks** (director's question, 2026-10-27).
  - **s5n (VL151):** its development experiments are "background-inclusive end-to-end", at nominal and two departure truths, but they are not a coverage test.
    - Its record is `OUTCOME-20260925-s5n-stage1-development-fail.md:13`: "**NOT CITABLE FOR:** any coverage verdict, since no validation seed was run". At `:33`: "**no validation seed.**". At `:35`: "Development seeds were 300000–349999".
    - The ledger row (`VALIDATION_LEDGER.md:208`) ends "Development evidence: … Not a coverage verdict". It takes σ "from 200 bootstrap replicas of one nominal experiment".
  - **s5e (candidate R, VL154),** which the note prints as "the development assessment" (`sec_5d.tex:179`): `OUTCOME-20260926-s5e-oi192-diagnosis-and-candidate.md:15` reads "**NOT CITABLE FOR:** a coverage validation (the assessment is development scale)".
  - **VL150,** the Tier-S coverage of candidate F2 with "1,200 end-to-end pseudo-experiments", is the only one recorded as a coverage test, with a verdict of "FAIL (futility)" (`VALIDATION_LEDGER.md:223`).
  - So "the one end-to-end independent-truth coverage test" (A2) and "the one end-to-end test of it against independent truths" (A4) hold.

## Held for Joseph: drafts sent to the director, not edited

1. **`sec_eavailw.tex:57`**, "the net effect of this difference on the cell contents has not been measured".
   - MP-5 measured it: `state/measurement-paper/phase1/mp5/REPORT.md`, job 60017887, commit `494b3404`, 2026-10-20. Over the 109 joint-test cells:
     - R_c is 0.99649 / 1.000008 / 1.00346 (min / median / max) on the analysis simulation, at its MC floor;
     - GENIE CV's own beam-axis shift is Δ/σ_c −0.47 / 0.00 / +0.53.
   - The proxy is UNRELIABLE for GENIE with MEC, NuWro and GiBUU.
   - Two drafts were sent: (A) print the result; (B) a minimal scope fix. Either needs a citable home for MP-5. The note's body cannot carry a repository path, so that home would be a new records entry.
2. **`app_history.tex:253`, a frozen record paragraph.**
   - "No positive-semidefiniteness measurement exists for either" is false as read. The production status log (`nd-unfolding/CORRECTED_UQ_PRODUCTION_STATUS.md:735`, `:740-741`, job 55912230, 2026-07-14) records "PSD OK" for both adopted constructions: most-negative-to-largest eigenvalue ratios −2.4e-16 and −4.1e-16.
   - The adoption code stops on failure: `nd-unfolding/adopt_unified_5d.py:149-165` @ `0d919b1a`, and `:138-155` @ `07c18aee`, the 2026-07-14 commit that built them.
   - "so no substitution is available" holds only if read as an authorized substitution. Footing-matched candidates exist (VL16, VL17; job 56693207, `VALIDATION_LEDGER.md:460-479`), and none is adopted.
   - The director's mechanism is an erratum paragraph directly after the frozen one, so P5 is untouched. It was drafted and sent.
<!-- absence-ok: quotes or summarizes the audited sentences of the note, paper and primer, before or after this audit, as its record; not a new absence claim -->

## Checks

- **Probes:** `check_probes.py .` reports 7 rows, 15 probes and 0 failures. A planted false probe makes it fail.
- **TeX layout:** `reflow_tex.py --note --check` passes, and the inserted comment lines leave every file's line structure valid.
- **Absence claims:** `judge()` over every line finds 2 bare claims, both held for Joseph.
- **Build:** `build_all.sh` exits 0. The note grows from 120 to 121 pages, because the longer ES sentence moves a page break. Paper 13, primer 15, PET note 26, records 56. There are 0 undefined references and no `??`. SEC4 passes 15 of 15, and RECORDS-PIN, ENTRY-NUMBERS, BODY-POINTERS and RESULT pass.
- **Records:** `check_note_records.py probe` PASS, and its `--self-test` fires 35 of 35. P5 is unaffected by the comment lines added to App. history.

## Files

- `ledger.md`: ACC-A1 to ACC-A7.
- `check_probes.py`: the probe check.
- `research/`: the four write-ups and their brief (text files).
- `agy/`: the prompt, inputs and outputs of both agy runs.
