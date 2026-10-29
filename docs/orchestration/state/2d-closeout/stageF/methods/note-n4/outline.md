# Note round n4: outline (2026-10-28)

**Lane:** paper rewrite, for the director. **No note edit comes before the director rules on this outline.**

**Base:** origin/main `371cccec` (#413 merged at `c486448c`, then #460). The branch is
`note/n4-front-matter-20261028`, created at `371cccec`; this outline is its only file so far, uncommitted.

**Under:**
- `DECISION-20261028-joseph-protections-n4-release-retrospective.md` (main `7ad03654`): items 2 (front matter) and 3
  (`app_release.tex` released), and item 1, which keeps Joseph's requirements and protections as they are until his
  inventory is decided;
- `DECISION-20261027-joseph-n4-after-content-cuts-and-paper-scope-consult.md`: n4 is the last register round, and
  "no fact leaves both documents" stands;
- the n3 rules: P1N's noise rule (ruled 2026-10-26) and the stop rule (`note-n3/outline.md`);
- the r19 open items (`r19/outline.md`, "Open items for the n4 note round").

## 1. Front matter (decision item 2)

What prints today (words exclude comments and macros):

| piece | file | printed | what it holds |
|---|---|---|---|
| Executive summary | `sec_execsummary.tex` | 914 words, about 2 pp | a framing paragraph; seven result bullets; the status table; "Principal limitations", a pointer list |
| Status table | `result_status_rows.tex` | 284 words | four rows: estimator, uncertainty, checks, interpretation. This is its only instance; the paper does not print it |
| §1 Scope | `sec_intro.tex` | one paragraph | the scope in positive form, plus three coverage limitations |
| §1 Roadmap | `sec_intro.tex` | 204 words | one sentence on the companion article, then the Topic → Section table (about p. 10) |
| §12 Summary | `sec_summary.tex` | four bullets | the conclusions, which repeat the ES bullets |
| §12 Principal limitations | `sec_summary.tex` | one paragraph | the full limitations list |

**Proposed shape (my recommendation, A):**
- **ES: folded to one page, about 450–550 words.** It becomes the note's single results summary: one short paragraph per
  result, giving its headline number, its scope qualifier and a pointer to its body home. The framing paragraph is
  fixed under §2.1 below.
- **The one limitations list: in the ES.** It is §12's full list, moved forward. A reader of a 130-page note meets it
  on p. 2–3, and the ES's pointer list is retired.
- **§1 Scope:** keeps the scope in positive form: one implementation, one data set, the configurations tested; the
  generator tests add no reportable uncertainty; PET is future work. Its three coverage sentences already print in
  the list, so they are replaced by one pointer to it.
- **§12:** its Summary bullets keep only the conclusions the ES does not state, and point to the ES for the results.
  The limitations paragraph becomes a pointer. Outlook and "Reusing the unbinned result" are unchanged.
- **Topic → Section table:** cut. The sentence "The companion journal article is a shortened account …" stays, as
  the opening of §1's last paragraph. The table holds only pointers, apart from one fact, "protocol implemented, not
  yet run". That fact prints in `app_response_mismatch.tex` and `sec_validation.tex`.
- **Status table:** removed. Three of its facts print nowhere else, and each gets a home before the table goes:
  - "Whether it is ready for publication as a measurement has not been established" (2D). This is a deposit-pass
    disclosure (`result_status_rows.tex` comments, `32325db7`). See Q2: I treat it as protected.
  - "a five-setting seed ensemble" (2D uncertainty). Its body home is `sec_systematics.tex`; I will check the phrase
    there.
  - "the covariance's four measured limitations apply". The four are the measurements of `sec:eavailw-adopted`; its
    home there will be cited.

**Alternative (B):** drop the ES. The single summary and the limitations list then live in §12, and the abstract and
§1 point there. B is shorter, but it leaves a 130-page note with no results summary before p. 10.

**Rule for every cut: show where each fact still prints.**
- `note-n4/ledger.md` gets one row per removed or changed sentence, with an `N:file::` probe at the body home of each
  fact it carried, or an `R:` probe where the records print it.
- Every ES and §12 sentence at the base must appear in some row's "before" column (coverage rule 3, as in r19).
- A read-only subagent builds the fact-to-home map independently, and `check_ledger.py` verifies it, as in d2.

## 2. The two items deferred to n4

**2.1 The main-result inconsistency.**
- The note abstract (`main_note.tex:72`, Joseph's d2 wording) opens with "We report a simultaneous measurement … in
  five observables".
- `sec_execsummary.tex:6` and `sec_summary.tex:4` say "The main results are the validation findings."
- The paper's printed Conclusions (`paper_body.tex:355`) say "The principal result is the sixteen-cell cross section
  of Sec. … , with its covariance and generator comparison."

**Proposal:** replace the note's two sentences with the paper's printed sentence, retargeted to `\S\ref{sec:fived16}`.
The scope sentence that follows ("They hold for this implementation, one data set …") stays.
- This aligns both sites with text Joseph has approved twice (both abstracts, and the paper's Conclusions), and it
  adds no claim.
- After the fold only one site remains, because §12 points to the ES.
- **Out of scope, flagged:** the primer says the same thing twice ("Its main results are the tests of the method",
  `primer_body.tex:13`, `:57`). It is a third document, and I leave it unless you add it.

**2.2 "Calibration" in the interval sense.** N1 (`sec_5d.tex:8`, since r19) gives "calibration" to tests and
"coverage" to intervals. There are six sites, re-located on `371cccec`:

| site | now | proposed |
|---|---|---|
| `sec_5d.tex:90` | "a pooled calibration test of its statistical intervals (pull width 1.02)" | "a pooled coverage test of its statistical intervals (pull width 1.02)" |
| `sec_5d.tex:90` | "does not establish calibration for every functional" | "does not establish coverage for every functional" |
| `sec_5d.tex:179` | "a pooled calibration pass cannot qualify this cell" | "a pooled coverage pass cannot qualify this cell" |
| `sec_validation.tex:4` | "checks neither interval calibration nor the adequacy" | "checks neither interval coverage nor the adequacy" |
| `sec_pet_campaigns.tex:61` | "H2S1T24 fails interval calibration" | "H2S1T24 fails interval coverage", if the PET campaign's frozen rule is a coverage rule. I check its record first; if the rule is named "calibration", the name stays, quoted |
| `sec_pet_campaigns.tex:119` | "the measured PET procedure failed calibration" | "failed its coverage test", under the same check |
| `app_statmethods_nd.tex:62` | "constructs calibrated intervals for selected functionals" | "constructs confidence intervals for selected functionals", the cited paper's own title (Stanley et al., `technote.bib:802`) |

These are accuracy and consistency fixes. Each is unscored and gets its own ledger row, as ACC-n3 did.

## 3. `app_release.tex` (decision item 3)

**The package checked against:** `minerva-omnifold-article-release-rc7.tar.gz`, present locally at
`/Users/josephbailey/local-research/MINERvA-OmniFold-prd-editorial-pdf-20261008/` (read only).
- Its sha256 is `27f0caba…566e`, which matches `docs/publication/release/RC7-SHA256SUMS.txt`.
- It holds 33 files: code, `data/{figs,frozen,m1f2,recovery-union}`, `expected/` and the README, which are the 32
  files its SHA256SUMS lists, plus SHA256SUMS itself.

**Method:**
- A claim table, `note-n4/release-claims.md`, lists every factual claim of `app_release.tex`. For each claim it gives
  the evidence: a tarball member, a README line, a SHA256SUMS entry, a `verify_rc.py` step, or a repository record.
  Its verdict is TRUE, FALSE or UNVERIFIABLE.
- Where a claim needs a run (for example "prints `VERIFY: PASS`" in a fresh environment), I run `verify_rc.py` from
  an extraction in my scratchpad, with the pinned requirements. If the environment cannot be built, the verdict is
  UNVERIFIABLE and goes to you; I will not infer one.
- Every FALSE claim comes to you, as with n3's "false as read" rule, before I edit it.

**Already found (to be confirmed in the table):**
- **The article no longer prints any of RC7's figures.** RC7 regenerates the figures of the earlier article: Fig. 1
  validation, Fig. 2 joint localization, Fig. 3 generator context. Since the move and the 5D integration, the
  paper's figures are `paper_fig1_validation`, `paper_fig_bkg_residual`, `paper_fig_deformation` and
  `fd_g_fig_ratio`, and its body cites no note figure (`\nsec` only, no figure pointer).
- So two statements are now false as read:
  - "It also regenerates … figures that the article cites from this note:" (the line-9 sentence);
  - "the arrays behind the article's figures" (Contents and use).
- The raters' line-9 choice, "keep" (d2 B4, 4 of 4), was between two forms that both presume the citation. So I
  propose a truth fix in its place: name the three as note figures ("figures of this note: …"). RC7's relation to
  the article becomes "assembled for an earlier version of the article". I will put this exact wording to you.
- **R1–R4** (d2 B5, "scoped", 4 of 4) apply as the raters chose, if each scoped phrase is TRUE in the table: "of the
  configuration-(a) central value" for "used in this note", at four sites.

**Protection lifted, with a recorded allowance:**
- `app_release.tex` leaves `PROTECTED` in the live checker, `note-n4/check_ledger.py` (a copy of n3's, `--base
  371cccec`).
- The allowance pins each declared (old, new) pair by sha256, as C1A_PINS and D2_PINS do. Any undeclared change to
  the file fails the checker, and the self-test plants one.
- `check_note_records.py`'s reader-paragraph plant sits on this file ("can and cannot recompute}"). That heading is
  not edited, so the plant stays valid.
- The fived16 and r19 checkers are records of their own rounds, pinned to their bases. I leave them unchanged and say
  so in the allowance (see Q4).

## 4. Not in scope (decision item 1)

Until Joseph decides on the inventory, these sentences are left byte-identical wherever they print, including inside
text that is otherwise folded:
- the DECISION-20261005 recovery disclosures, which sit in the ES joint-test bullet: "rerun, for reporting only, so
  every submitted draw has been observed"; "No recovered draw changes a decision";
- the KI-85 2D coverage sentence: ES "Principal limitations", the sentence that prints `\covTwoDCTwo`; and §12's
  "has had no coverage test";
- the deposit and release-status statements: "no release has been tagged or deposited" (§12); RC7 "has not been
  deposited or released under a publication tag"; the status table's readiness sentence;
- Data Availability, `\pubhold`, the abstracts and the title. None is touched.
<!-- absence-ok: lists the printed sentences frozen by the outline, quoting them; not a claim that a result does not exist -->

**The consequence:**
- Where a frozen sentence prints in both the ES and §12, it prints twice until Joseph decides, so "limitations once"
  holds except for these sentences.
- The ES fold keeps the joint-test claim beside its disclosures, both verbatim.

## 5. Process and scoring

- **Batches:**
  - n4-F, the front matter: written last;
  - n4-C, the six calibration sites and the main-result fix;
  - n4-R, `app_release.tex`, made after the claim table.
- **Review:** each batch gets a writer (an Opus 5.5 subagent of this session) and a fresh two-direction reviewer. agy
  then runs on every changed passage, with controls.
- **Guards:**
  - printed_diff on every scripted edit;
  - `reflow_tex.py --note --check`;
  - `check_note_records.py`, all modes;
  - `check_dead_containment.py` (the `\covTwoDCTwo` print count is unchanged, because the frozen sentence stays);
  - the PR-wide `absence_claims.py --base origin/main`, which I now run before every push;
  - the full build, which must show no `??` and no undefined reference.
- **P2N and P1N:** OLD is the note at `371cccec`. These measure the wording of n4-F and n4-R under the noise rule. A
  piece reverts only if its sol2 2-run mean falls by more than 0.25, or the 4-run mean falls after a tie at 0.25.
- **n4 is round 4,** so the stop rule ends register rounds after it, whatever the score.

## Questions for you

1. **Shape:** A, fold the ES to one page and hold the one limitations list there; or B, drop the ES and use §12? I
   recommend A.
2. **Frozen set:** is §4's list the right set of sentences to freeze until Joseph's inventory? In particular, the status
   table's "readiness for publication … not been established": I would move it verbatim into the ES's 2D paragraph.
   Is that move allowed, or must it stay in a table?
3. **Adoption:** the structure (cut, fold, list once) is Joseph's decision. So I propose that P2N and P1N judge only
   the wording: if NEW loses, I revise the wording and the structure stays. n3's ES/§1/§12 pieces were not adopted on
   P2N, so this question will likely arise.
4. **The lifted check:** is the allowance in `note-n4/check_ledger.py` what you meant, with the fived16 and r19
   checkers left as records of their rounds? Or do you want fived16's `PROTECTED` list edited too?
5. **The primer:** add `primer_body.tex:13` and `:57` to §2.1, or leave them?

## Director's rulings on this outline (2026-10-28): approved

1. **A.** The ES is folded to one page as the single results summary, and §12's full limitations list moves into it.
   §1's Scope keeps a pointer, and §12 keeps only the conclusions the ES does not state. The Topic→Section table and
   the status table are cut once the three status-table-only facts have homes.
2. **§4 is the right frozen set.** The readiness sentence may move verbatim, byte-identical, into the ES's 2D
   paragraph, with a probe at its new home. The duplication of frozen sentences between the ES and §12 is accepted
   until Joseph's inventory decision, and is recorded as the one known exception to "limitations once".
3. **P2N and P1N judge the wording within Joseph's structure.** If NEW loses the pairwise, the wording is revised once
   inside the same structure and re-measured. If it still loses, both runs go to the director, and the structure is
   not reverted. The P1 noise rule applies to the wording. The report says plainly that this is the first round in
   which the structure is not on trial.
4. **The allowance lives in `note-n4/check_ledger.py`:** sha256-pinned pairs, a self-test plant, `--base 371cccec`. The
   fived16 and r19 checkers stay as records of their rounds.
5. **Add `primer_body.tex:13` and `:57` to 2a,** with the same sentence, retargeted. The primer's page count is
   reported before and after.
- **2b** is approved as proposed, including the check of the PET campaign's frozen rule name before :61 and :119
  change.
- **3:** lines 9 and 29 of `app_release.tex` are false as read. Every FALSE claim and its proposed truth fix comes to
  the director before any edit. R1–R4 apply only where the table says TRUE. The framing: name the three figures as
  this note's figures, and describe RC7 as assembled for an earlier version of the article.
- **Process:** accepted, including the PR-wide absence check before every push. Batch 1 may start.

## Director's further rulings (2026-10-28, after batch C)

- **Batch C is accepted:** the C1–C6 revisions after agy's dispersion objection; "the frozen coverage rule" as the PET
  record's own name; stopping the agy reads at its observed noise; M1/M2's DIFFERS, which is the decided change.
- **The primer: (a).** It is not edited. The n4 report and the list for Joseph flag it as stale against the
  five-dimensional integration: it predates the sixteen-cell result and says the study "does not deliver a validated
  five-quantity cross-section measurement". That is a content question for Joseph, outside n4.
- **Batch F's length: (b)+(c), about one page.**
  - "Limitations once" means one home per limitation. Each limitation prints at its body home, and the ES points to
    it (the R01 ruling).
  - The frozen 2D sentence stays verbatim in the ES, and the readiness sentence stays in its 2D paragraph.
  - Two conditions: the ledger probes every §12 limitation at its body home before the full list stops printing as
    one paragraph; and the fact-to-home map covers all changed sentences.
