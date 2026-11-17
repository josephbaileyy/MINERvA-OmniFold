# History restructure, §9 (sec_5d.tex): cut log

**Under** DECISION-20261113-joseph-note-n4-n5-role.md, the addendum recording Joseph's go of 2026-11-13.

**The rule, verbatim as adopted:** history stays in the note only if removing it would change a reader's understanding
of the reported object, its reproducibility, its evidential independence or its limitations. Everything else goes to
the ledger. Each "fixed before" names its object, and "declared" alone is replaced.

**Referee:** for §9 it gave "10–20%, Compress / appendix. Keep bias, instability, failed coverage, invalid deformation,
and covariance restrictions. Move extended diagnostic traces and investigation details." Its item 6 (§9.6, the null
bound not fixed before production, and the covariance used anyway) is marked "Disclosure—stay".

**Base:** `docs/analysis-note/sec_5d.tex` at `619a1d9b6`. Line numbers are the base's.

**Outcome for §9:** the director's ruling (A) of 2026-11-14. The three bare "declared" become "specified before it
ran", with each object from its records, and the stop rule is "fixed before that stage ran". Four method uses of
"declared" become "specified". No passage is cut. §9's remaining history is the five kinds the referee itself says to
keep: the bias, the instability, the failed and stopped coverage tests, the invalid deformation and the covariance's
restrictions.

**The ruling:** in this note "declared" is the project's word for "specified before it ran", and spelling it out is the
point of the rule. A precision the records support is not a widened claim. The note does not define the word (Search:
`\emph{declared}`; "declared" … means; LaTeX-quoted "declared"; pre-registered; in sec_intro, sec_execsummary, sec_method,
app_guide and main_note @ 619a1d9b6: none).

## The changes

| id | base line | old text | new text | ledger home and the records for the object |
|---|---|---|---|---|
| F1 | :101 | "A declared probe on simulated pseudo-data of two-fold cross-fitting and of two tree regularisations found no variant …" | "A probe on simulated pseudo-data of two-fold cross-fitting and of two tree regularisations, specified before it ran, found no variant …" | 619a1d9b6:sec_5d.tex:101. FD-STAB-DECLARATION.md (first commit f544c6bbb, 2026-11-03; :20 "Nothing runs before the binding"); FD-STAB-BINDING-1.md (2026-11-04, the declaration's sha256 06d8334a…); FD-STAB-BINDING-2.md (the full run bound after the dry run, job 60827080, :26-56) |
| F2 | :101 | "A declared study of the mechanism on one pseudo-experiment found that …" | "A study of the mechanism on one pseudo-experiment, specified before it ran, found that …" | 619a1d9b6:sec_5d.tex:101. fd/rounding-stability-20261106/RS1-DECLARATION.md (a2b67496d, 2026-11-06, "Nothing has run, and nothing runs before the …"); RS1-BINDING-1.md (design, 0d51e054) and RS1-BINDING-2.md (code, e306087e) |
| F3 | :237 | "The declared coverage test of the sixteen-cell result did not run to a result: its first stage stopped under a fail-closed rule declared in advance" | "The coverage test of the sixteen-cell result, specified before it ran, did not run to a result: its first stage stopped under a fail-closed rule fixed before that stage ran" | 619a1d9b6:sec_5d.tex:237. FD-1B-DECLARATION.md (fcdc1afed, 2026-10-30, "the coverage protocol, fixed before any toy"); the rule at FD-1B-STAGED-AMENDMENT-2.md:204 in its first commit 2b8859efc (2026-11-03), unchanged at :222 @ b3f27fab3; the stage's receipt, job 60893641 (receipt.txt @ b3f27fab3, connect 2026-11-06T08:15Z) |
| M1 | :340 | "No separate acceptance weight at the destination binning was declared" | "… was specified" | a method use: no timing |
| M2 | :342 | "An inverse requires a declared regularization" | "… a specified regularization" | as M1 |
| M3 | :350 | "The limit is a declared stability tolerance, not a derived confidence threshold" | "… a specified stability tolerance …"; the sentence before keeps "fixed on 2026-09-18 before production" | as M1 |
| M4 | :353 | "the statistic is a maximum over the declared offset set" | "… the specified offset set" | as M1 |

**Kept as they are:**
- **The referee's item 6** (:294 onward, §9.6): the null bound not fixed before production, the covariance used
  anyway, its restrictions and the four limiting measurements. It is the disclosure the referee says stays.
- **"fixed on 2026-09-18 before production"** (:350): its object is named, inside item 6's disclosure.
- **"under a rule fixed before the comparison"** (:156), **"set before it was run"** (:99) and **"set before the test
  was run"** (:237): each names its object.
- **The data-stability failure, the bootstrap's share of it and the reproducibility limit** (:99), the mechanism
  findings and their scope (:101), the futility failure, the invalid $q_3$ deformation and "No frequentist coverage is
  therefore claimed" (:237).

**Numbers and keys:** `numdiff.py` on the base and new files, comments stripped: none removed, none added; value keys
and macros unchanged.

## The Development-history appendix: new rows

| row | from | content |
|---|---|---|
| D8 | :101 | the stabilization probe: two-fold cross-fitting and two tree regularizations; no variant met the data-stability requirement; the estimator is unchanged |
| D9 | :237 | the end-to-end independent-truth coverage test of the deterministic five-dimensional variant: it failed its futility criterion, set before the test was run; the $q_3$ change did not implement the intended reweighting and is not an interpretable test; no frequentist coverage is claimed for any five-dimensional interval, and the futility verdict does not depend on the $q_3$ experiments |
| D10 | :237, sec_fived16.tex:287 | the coverage test of the sixteen-cell result at the two tunes: ended without a coverage result, its first stage stopped under a fail-closed rule fixed before that stage ran |

Each row restates the body. "Already seen" is "--" in all three, because §9 does not state what had been seen.

**App. I pass, 2026-11-15:** D8, the stabilization probe, was removed from App. I (history-cuts/app_devhistory.md, I5). The probe's negative result stays in §9.3 (:101).

## Disclosure checklist

| disclosure | in §9? | survives |
|---|---|---|
| the 2D adoption after the published distance was known | no (§3) | — |
| the post-observation run-period term | no (§4, §10) | — |
| reused samples and seeds | the mechanism study's single pseudo-experiment, and its scope ("Neither finding is a statement about the data's spread", :101) | ✓ unchanged |
| the invalid q3 deformation | yes, :237 | ✓ unchanged, and in D9 |
| the stopped coverage tests | yes: the futility failure and the sixteen-cell test's stop (:237) | ✓ unchanged in substance (F3 names the objects: specified before it ran; the rule fixed before that stage ran), and in D9 and D10 |
| the data-informed joint-test design and budget extension | no (§11) | — |
| the missing response uncertainty | no (§10) | — |
| the generator-sample problems | no (§10, App. C) | — |
| the target-correction sensitivity | no (§11) | — |
| also found: the null bound not fixed before production (item 6) | yes, :294 onward, :350 | ✓ unchanged |

**A record date, noted only:** FD-STAB-BINDING-2.md's header reads "(director, 2026-11-05)", while its first commit is
578136817 on 2026-11-04. The record states its own date, and nothing here depends on the difference.

## Unreleased support

`UNRELEASED-SUPPORT.md` already lists §9's sites: NoteRecords2026 [34] at :90, :294 and :360. None changes here.

## The two earlier wordings

- **Pass 1** kept the objects with "declared before it ran". The read failed F1–F3 under question 1 as adding timing,
  having the old sentences but only some of the records.
- **Pass 2** dropped the bare word, as §5's V1 did. The read failed F1–F3 again, as weakening; question 2 classed
  F3's "declared in advance" (the rule) as NEEDED.
- The director ruled (A), with "specified" for "declared" and question 1 read against the attached records (pass 3).

## Style pass B, 2026-11-15 (the director's approval of the style-recheck plan, items 1, 2, 3 and 5)

**Source:** the codex style recheck `note-style-recheck-6c38249bcf5c.md` (codex-school, style only). **Base:** this
section at `80e8fb416307bb48c75e97fbb5c9c871c423fc69`, line numbers the base's; each removed passage stays at that sha and line, its ledger home. The
director's condition: keep whatever the read classes NEEDED. The line count is unchanged (`%` lines hold the
numbering).

| id | base line | old text | new text | ledger home |
|---|---|---|---|---|
| F4 | :294 | "The covariance does not meet the acceptance criteria of its specification, and its metadata mark it as not passing and as not to be used. The specification requires the null bound to be fixed before production, which was not done for this covariance, so it cannot meet that requirement. This note nevertheless uses this covariance and its projection." (style item 3; the referee's item 6, a disclosure that stays) | "This note uses them with the restrictions stated in this section. The covariance does not meet the acceptance criteria of its specification: its metadata mark it as not passing and as not to be used, and the null bound that the specification requires to be fixed before production was not fixed for it." Kept: the checksum identity and its citation, the non-passing metadata, the missing preproduction null bound, "The use does not extend to any other covariance …, including the two companion covariances", and the four measurements (unchanged). Not adopted from the recheck: "used only for the estimator-seed diagnostics" (the note also uses $C_Z$'s per-source decomposition for attribution, sec_systematics.tex:160; this row first also named the seed-shift scale at sec_eavailw.tex:118, but that comparison, item 4, uses the companion covariances, :344, as found in the read of E3, history-cuts/sec_execsummary.md); pass 1 of the read failed the first wording, "for the purposes, and within the limits, stated in Table~\ref{tab:result-status}", because Table 1's "Technical diagnostic of estimator-seed sensitivity only" does not cover those two uses; the use is now bounded by the section's own restrictions. numdiff: none removed, none added. | 80e8fb416:sec_5d.tex:294 |

## Meaning read (codex-school gpt-6.1-sol, high, read-only; reads/PROMPT-two-question.txt plus records.txt; pass 3 as stated)

- **Pass 1, on the first wording:** OVERALL FAIL.
  - Question 1 failed F1, F2 and F3, as above; D8, D9 and D10 passed.
  - Question 2: nothing removed or shortened, so no NEEDED item lost.
  - No disclosure was lost.
  - The answer is in reads/sec_5d-pass1.txt.
- **Pass 2, the bare word dropped:** OVERALL FAIL. Question 1 failed F1–F3 as weakening; question 2 classed the
  three test "declared" as LEDGER and F3's rule "declared in advance" as NEEDED. reads/sec_5d-pass2.txt.
- **Pass 3, ruling (A), on the wording above:** OVERALL PASS, with no FAILs. Question 1 was read against the attached
  records (reads/sec_5d-pass3-prompt.txt, reads/sec_5d-pass3-records.txt): F1–F3, M1–M4 and D8–D10 pass. Nothing was
  removed, and no disclosure was lost. reads/sec_5d-pass3.txt.

**Style pass B, meaning read (codex-school gpt-6.1-sol, high, read-only; rows S6, C8, F4 and T8 read together, records attached):**
- **Pass 1:** OVERALL FAIL on F4 only ("for the purposes, and within the limits, stated in Table~\ref{tab:result-status}" imported Table 1's estimator-seed-only scope, which omits sec_eavailw.tex:118 and sec_systematics.tex:160). S6, C8 and T8 passed; every removed item was LEDGER or NEEDED and retained; no disclosure lost. reads/styleB-pass1.txt.
- **Pass 2, F4 revised to "with the restrictions stated in this section":** OVERALL PASS, with no FAILs; no NEEDED item lost; no disclosure lost. reads/styleB-pass2.txt.

## Cutdown, 2026-11-16 (lane/note-cutdown-20261116): §9.6, the five-axis covariance C_Z

**Under** Joseph's go for the cutdown (DECISION-20261116-joseph-paper-batch.md at main `99aefd3f0`, sixth answer,
items 31 and 34) and the editor's brief of the same day: the construction, centring, projection and conditioning of
C_Z move to the records document; the status paragraph, the four measurements and what the Supplement cites stay.
**The rule:** as at the head of this file.

**Base:** `sec_5d.tex` at `8342963c16d74bc10d740e5637d602300557e53a`. Line numbers are the base's. The moved text is
in `app_release_records.tex`, under "Construction and audit record of the (E_avail,W) covariance", word for word.

| id | base line | words cut | disposition | old text | new text | home of the content | why not NEEDED |
|---|---|---|---|---|---|---|---|
| K1 | :326, sentences 4–7 | 73 | moved to main_records | "The same inflation of the vertical bands can be transferred onto a sweep block, … only if … (a condition set in July 2026). This transfer is positive-semidefinite by construction, … It does not put every projected variance above that baseline. A direct rank-N swap is not positive-semidefinite." | removed from the note | `app_release_records.tex`, "Moved from the note's §…eavailw-construction" (ledger row L-cut-Z1) | A property of a transfer that no reported result uses. |
| K2 | :328–:339 | 102 | moved to main_records | "Centering, explicitly." with Eq. zcentering: the per-band blocks' centring, the identity between the CV-centred and mean-centred unified-throw covariances, that the covariance used is the CV-centred variant, the mean-centred variant's √Tr C lower by 7.13%, and that a file's variant is identified by its metadata | removed from the note | as K1 (row L-cut-Z2; row L-thin-C51 re-pinned) | §9.6 "Status" still says which variant is used and that the use extends to no other covariance. The comparison of the two variants concerns a covariance the note uses for no reported result. |
| K3 | :341 | 160 | moved to main_records | "The projection to (E_avail,W)." | removed from the note | as K1 (row L-cut-Z3; row L-thin-C52 re-pinned) | How a 42-cell projection is formed and paired by checksum; the note quotes nothing from that projection except the four measurements, which say what they are computed on. |
| K4 | :343 | 148 | moved to main_records | "Conditioning, and why no rank is quoted." | removed from the note | as K1 (row L-cut-Z4; row L-thin-C53 re-pinned) | The note inverts this covariance nowhere and quotes no rank for it. |
| K5 | :326, end | +37 | pointer inserted | — | "The terms of Eq. zassembly, the transfer of this inflation onto a sweep block, the two centerings, the projection to (E_avail,W) and the conditioning are in the records document (Ref. NoteRecords2026, construction and audit record)." | — (row L-cut-Z5 pins the citation; row L-thin-C50 re-pinned) | The pointer the moved text needs; it states no result. |

**Kept in §9.6:** "Status"; the opening of "Construction" with Eqs. zassembly and zinflation and the definitions under
them; "What the covariance supports" with its four measurements; the closing sentence. The two equations stay for two
reasons. They are where the joint (unified-throw) ensemble enters, which is what the Supplement's pointer to this
subsection is for (`supplemental_body.tex`, the joint-ensemble linearity test). And five note sentences
(`sec_systematics.tex` twice, `app_statmethods.tex` twice, `app_release.tex`) and three records paragraphs cite them by
number. The records' own text (`app_history.tex:273`) says the three requirements of the construction "remain in the
body in the Construction paragraph", which the kept opening sentences are.

**Pointers changed with the move:** `app_statmethods.tex` (§A.2.5, "Scope of mean-centering"): "(§…eavailw-construction,
Eqs. zinflation and zcentering)" becomes "(§…eavailw-construction, Eq. zinflation)"; the kept definition under
Eq. zinflation says the unified-throw diagonal is centred on the central value, which is what that sentence cites.
`app_guide.tex`: "the two centerings of the five-axis covariance (§…eavailw-construction)" becomes "the centering of
the five-axis covariance (§…)", since the body now describes one in words.

### Corrections after the second-model reads of the cutdown (director's ruling, 2026-11-16)

Two second-model reads of this branch at `56c91c6f6` were made for the director; one passed, and one failed two
pointers. The director ruled both fixes. Line numbers are this branch's at `56c91c6f6`.

| id | site | old | new | reason |
|---|---|---|---|---|
| K6 | sec_5d.tex:326, the pointer sentence of row K5 | "The terms of Eq. zassembly, the transfer of this inflation onto a sweep block, the two centerings, the projection to (E_avail,W) and the conditioning are in the records document (Ref. NoteRecords2026, construction and audit record)." | "The transfer of this inflation onto a sweep block, the two centerings, the projection to (E_avail,W) and the conditioning are in the records document (Ref. NoteRecords2026, construction and audit record)." | The note keeps Eq. zassembly, so the pointer must name only what moved. The citation is unchanged, and row L-cut-Z5's probe still holds. The ML term of that equation, moved from §4.7 (history-cuts/sec_systematics.md K2), is in the same records subsection and is reached by the same citation; the sentence no longer names it. |
| K7 | app_release_records.tex, lead-in of "Moved from the note's §…eavailw-construction" | "The four paragraphs that follow stood in the note until its cutdown of 2026-11-16, after Eqs. zassembly–zinflation, which the note keeps." | "The transfer sentences in this paragraph, and the three paragraphs that follow, stood in the note until its cutdown of 2026-11-16, after Eqs. zassembly–zinflation, which the note keeps." | The transfer sentences continue the lead-in's own paragraph; only three paragraphs follow it. The moved text itself is unchanged. |
