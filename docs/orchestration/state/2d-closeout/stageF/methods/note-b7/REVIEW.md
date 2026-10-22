# Review: batch b7, §10 "Calibrated joint tests of generator predictions" (`sec_joint.tex`)

**Reviewer:** an independent, read-only reviewer. I edited no worktree and made no commit. My scratch outputs are in `S/rv-b7/`.

**Versions compared:**
- **Before:** `b603f9cf:docs/analysis-note/sec_joint.tex`, built in `S/plain-language/builds/note-b7-base`.
  - `origin/main` has since moved to `250025b5`.
  - `git diff --stat b603f9cf origin/main -- docs/analysis-note/` is empty, so the writer's `origin/main`-based probes compare against the same note source.
- **After:** the uncommitted `S/wt-note-b7/docs/analysis-note/sec_joint.tex`. It is the only changed file, and it is byte-identical to the copy in `builds/note-b7/repo`.
  - `wt-note-b7-work/sec_joint.diff` is identical to `git diff`.

## Verdict: ADOPT-AFTER-FIXES

- No BLOCKING finding.
- One SHOULD-FIX was introduced by the batch (F1).
- Two pointer gaps predate the batch (F2, F3). They are not regressions, but the paper's pointers into §10 are only fully backed once they are fixed.

---

## Findings

### F1. SHOULD-FIX: the records sentence now reads as if every record were in one reference (lost scope)

`sec_joint.tex:11-15`
- **Before** (`b603f9cf`:16): "… with their numbers. The records cited in this section are its provenance~\cite{JointTestRecord2026}."
- **After:** "… with their numbers; the supporting records are in Ref.~\cite{JointTestRecord2026}."

`JointTestRecord2026` is a single record (`publication.bib:160`): "Five-dimensional joint generator tests: specification and result", that is, `RECORD-20261005`. The section also cites `JointTestRecovery2026`, `JointTestKappa2026`, `JointTestProjections2026`, `JointTestRecoil2026` and `NoteRecords2026`.
- The old sentence said that the records cited in the section are its provenance.
- The new one says that the supporting records are in one reference.
- Read as printed, the new sentence is false.

**Fix:** "… with their numbers. The specification and the decisions are documented in Ref.~\cite{JointTestRecord2026}; each later study cites its own record."

### F2. SHOULD-FIX (predates the batch; writer's open question 1): the paper's tertile pointer lands on a subsection that does not print the rationale

`paper_body.tex:237-239` says "a coarse $3^{5}$ grid … whose edges are the fine edges nearest the simulated tertiles (\nsec{sec:joint5d-design})".
- §10.1 (`sec_joint.tex:53-58`) prints the edges but not why they were chosen.
- "tertile" does not occur anywhere in the note, before or after.
- `git log -S tertile` touches only the paper.

A source exists and supports the paper's wording:
- `nd-unfolding/s5c_partition.py:14-15`: "Split points are the existing fine-grid edges nearest to the weighted MC-truth quantiles (medians / tertiles) of the signal sample".
- `:45-52`: `coarse_edges` takes the nearest interior fine edge to each weighted quantile k/parts.
- `M4-DEFINITIONS.md:206-207` restates it.

**Decision on question 1: yes, add it.** It is a sourced fact, not a strengthening, and it makes the paper's pointer true.

**Fix:** after the edge list in §10.1, add: "each inner edge is the fine-grid edge nearest a tertile of the signal sample's weighted simulated truth distribution in that coordinate". Add a source comment citing `s5c_partition.py:14-15, 45-52`.

### F3. NIT (predates the batch): "without a multiplicity correction" has no landing in §10.7

`paper_body.tex:1066-1069` says "gives $p<0.05$, without a multiplicity correction, for every test in at least one of the two projections … (\nsec{sec:joint5d-projections})".
- §10.7 (`sec_joint.tex:553-604`) never states that the projected tests are uncorrected.
- The word "multiplicity" occurs only in §10.3.
- The source is `PACKET-20261005-publication-decision.md` §6 (W1): "The marginal tests are report-only. They do not enter the Holm family".

**Fix:** in §10.7's first sentence, write "gives $p<0.05$, without a multiplicity correction, for every test …".

### F4. NIT: the B3 additions are correct; "at most about" stacks two hedges

`sec_joint.tex:734-740`
- **Before:** "… met its criterion of at most $0.1\,\sigma_{c}$: it moves the CH prediction by about $5\times10^{-4}$ of $\sigma_{c}$, the standard deviation …"
- **After:** "… met its criterion of at most $0.1\,\sigma_{c}$ in every cell, moving the CH prediction by at most about $5\times10^{-4}\,\sigma_{c}$, where $\sigma_{c}$ is the standard deviation …"

Each addition checked against its source:
- **"in every cell"** is supported.
  - `BINDING-PHASE1-ADDENDUM-7.md:29` gives the acceptance: "|Δ_c/σ_c| ≤ 0.1 in every cell, with the maximum reported".
  - `:26-27` defines the cells as the 72 GiBUU-domain J cells.
  - `mp3c/REPORT.md:31-32` gives the readout over the 72 cells and the acceptance as the maximum over them.
- **"at most"** is supported.
  - `mp3c/REPORT.md:38`: the maximum |Δ_c/σ_c| in reading (a) is 5.1e-4 (cell J93).
  - `:44`: "moves the CH prediction by at most 5e-4 of a null SD".
- "at most 5×10⁻⁴" alone would be slightly false, because 5.1e-4 > 5e-4. That is why "about" has to stay, and "at most about" is the result.

**Optional fix:** "by at most $5.1\times10^{-4}\,\sigma_{c}$". This number is in the cited source.

### F5. NIT (predates the batch, carried into the reworded clause): what σ_c is

The B3 sentence defines σ_c as "the standard deviation of the cell over the null distribution used for the decisions".
- MP3-C takes σ_c from MP3-B (`mp3c/REPORT.md:31`).
- `mp3b/REPORT.md:37` defines reading (a) as "the SD of the J-cell result over NuWro's frozen B = 1751 null".
- A reader of a GiBUU sentence will take the definition to mean GiBUU's null.

This is not introduced by b7; the old text said the same. If it is fixed, write "over NuWro's null distribution used for the decisions".

### F6. NIT (writer's open question 3): "is superseded by their observed outcomes" is not stronger

`sec_joint.tex:540-545`
- **Before:** "Because every submitted draw has now been observed and no recovered draw reaches the observed statistic, the ten rejections are stated as holding with every submitted draw observed, together with the closest margin and the earlier stops given above; the statement of the sensitivity analysis, that every decision could change under some assignment of the lost draws, no longer accompanies them."
- **After:** "With every submitted draw observed and none reaching the observed statistic, the ten rejections hold, with the closest margin and the earlier stops given above. The finding of the sensitivity analysis, that every decision could change under some assignment of the lost draws, is superseded by their observed outcomes."

The governing source is `DECISION-20261005-s5p-recompute-extension-and-lost-seed-recovery.md`.
- §5, `:111-112`: "State the ten rejections as holding with every submitted draw observed".
- "What it changes", `:133-134`: the qualifier "no longer accompanies the rejections. In its place stands the statement that every submitted draw was observed".

"Superseded" means "replaced by later information". That matches "in its place stands", and it does not call the pre-recovery finding wrong.

The scope survives in the same subsection:
- "The recovery is for reporting only: the primary decisions are those of the evaluation before recovery" (unchanged, directly before).
- The three-item list of the checks' scope.
- The determinism check that makes "their observed outcomes" the outcomes of the lost draws.

"the ten rejections hold" adds nothing beyond "no assignment of the lost draws changes any decision", which is already printed at `:524`.

**Decision on question 3: not stronger. Adopt as written.**

### F7. NIT: `REPORT.md` is missing from the work directory

The writer brief requires `REPORT.md` with the word counts, the moves, the qualifiers kept and the check outputs. It is not in `S/wt-note-b7-work/`, and I did not have the writer's reply. I re-ran every check myself (below), so nothing depends on it.

### F8. NIT: a source comment's provenance is now partly stale

`sec_joint.tex:259` still reads "% … the article's post hoc paragraph (its Sec. VIII C)." above a paragraph that no longer carries the post hoc observation.
- The writer may not edit comments, so this is information only.
- The removal itself is sound. The GENIE observation still prints in §10.7 (`:570-572`, "a post hoc observation") and in the Table 13 caption (`:601-602`).
- No paper pointer depends on §10.3 carrying it:
  - the paper's only pointer to §10.3 (`paper_body.tex:914`) is about the residuals, the budget extension and "holds for any stopping rule", and all three still print in §10.3;
  - the paper's own GENIE post hoc remark (`paper_body.tex:954`) points to its own section, not to the note.
- A planted probe confirms the sentence is gone from §10.3 (see D).

---

## Writer's open questions: decisions

1. **The tertile rationale in §10.1: add it** (F2). It is sourced in `s5c_partition.py:14-15, 45-52`.
2. **The duplicate "specified after the five-dimensional outcomes were known" in §10.3: keep it.** §10.3 says that "each was specified before it ran". Without the clause, a reader of §10.3 alone would take the projection comparison as predeclared before the outcomes, which is the timing claim the guardrail protects. §10.7 states the timing beside its own result. These are two subsections with two readers, not a repeat within one subsection.
3. **Is "superseded" stronger? No** (F6).

## Directions A–E

**A. Lost facts**
- **Numbers.** I compared every numeric token in the pdftotext of §10 (`s10-base.txt` against `s10-after.txt`, about 860 lines each).
  - There are 248 distinct numbers both before and after, and 662 tokens before against 661 after.
  - The one token lost is a "2.12.10", from the removed GENIE sentence in §10.3. It still prints in §10.7 and the Table 13 caption.
  - No number was gained.
- **Words:** 5934 before, 5893 after (pdftotext, tables included).
- **Rewritten sentences.** I read all 18 changed paragraphs (J0, J1, J11, J13-J16, J23-J25, J27-J29, J31, J33, J36, J37) against the old text.
  - Apart from F1, every fact is present.
  - J28-J29 moves the criterion beside the result inside §10.7, and the timing is restated correctly. `PACKET-20261005` §6 "Criteria, fixed now" with "Disclosure: data-informed (the 5D outcomes were seen)", and `W1-RECORD-20261006.md:3-4` "fixed in … §6 before the run", support "specified after the five-dimensional outcomes were known but before the comparison was run".
  - J16 "a factor of 0.45-0.76" agrees with `values_inference.tex:38-39`; r/(1−r) gives the stated residual of about 1-3 times the last step.
- **Paper pointers.**
  - There are 13 `\nsec` pointers into §10 (`paper_body.tex` 239, 859, 887, 914, 918, 924, 968, 984, 1019, 1022, 1025, 1069, 1076) and 1 `\napp{sec:joint5d-fwer}` (902). The fwer pointer lands in App. B.5, outside this batch. That makes 14.
  - All 13 pointed-to facts print in the same subsection before and after, except the tertile rationale at 239 (F2) and the multiplicity remark at 1069 (F3). Both were missing at base too.
  - The `.aux` of the note has 184 labels before and after, with no change of number or page. Every `sec:joint5d*` number is unchanged (10, 10.1-10.10, B.5; tables 11-14; figure 30).

**B. Strengthened claims**
- None. Checked items:
  - "for reporting only (outside the decision rule)" now appears at its first use (`:260`), with the short form after it (`:332`). This follows glossary A7, and its meaning ("not part of the decision rule") is the old one.
  - "not recorded" became "not documented". This keeps the limitation.
  - "exposed" became "showed".
  - The "of the data" added in J11 matches the paper's wording.
- The added specifics ("in every cell", "at most") were verified (F4).

**C. Protected text**
These are byte-identical, old against new:
- "hybrid null hypotheses about five predictions" (once in each).
- The B3 label, including its line break after "a".
  - It matches the literal span in `apply_glossary.py:944-945` (`B3_LABEL`), once in the new file.
- The verbatim specification quote, from `\begin{quote}` to `\end{quote}`: 2449 bytes, identical.
- The other verbatim markers (comment lines 18, 75, 129, 277 and 730) lie in untouched spans.
- All 105 comment lines are identical, in order.
- The 29 `\label`, `\section` and `\subsection` commands are identical, in order.
- The `\paragraph` headings are identical.

**D. Mechanics**
- **The writer's checker.**
  - `check_ledger.py S/wt-note-b7` exits with rc=0: "ledger rows 132, probes 169, failures 0".
  - `--self-test`: the planted probe fires and the true control stays silent.
- **My own planted probe.**
  - It requires the removed GENIE sentence in `sec:joint5d-frozen`.
  - It fails as it should: rc=1, "ZZ1: NOT FOUND in sec:joint5d-frozen", failures 1.
- **The build log** (`wt-note-b7-work/build.out`, `builds/note-b7/build.log`):
  - build_all rc=0;
  - RESULT PASS;
  - BODY-POINTERS PASS (0 internal pointers in 17 body files);
  - SEC4-RECEIPTS PASS (15/15);
  - struck-value containment ok (note, paper and primer 0 of 69; the records carry 64/64 and the PET note 5/5);
  - RECORDS-PIN SKIP (a scratch copy);
  - RECORDS-MOVE does not appear in this build's log or in the base build's log, so it neither ran nor failed.
- **Undefined references:** 0 in the note, paper, primer and PET-note logs. A grep of the records log for "undefined" finds nothing (rc=1).
- **`??`:** none in the pdftotext of the note or of the paper.
- **The paper's pdftotext** is byte-identical (`cmp`) to `builds/rec3` and to `builds/note-b7-base`.
- **`swallowed_text.py S/wt-note-b7 origin/main`:** rc=0, "flagged 0".

**E. Register**
The batch reached the target register for most of the section. The surviving bookkeeping or meta passages are these:
1. `:11-15` "The section gives the pre-registered specification, with its six conditions in its own words (§10.4), the decisions, the recovery of the lost pseudo-experiments and the later sensitivity studies with their numbers; the supporting records are in Ref. …" (a contents list, and F1).
2. `:247` "the status outputs of the job controller showed observed claim $p$ values" (software detail; "the calibration's monitoring output" would do).
3. `:314` "Restated in the terms of this note and grouped by kind, they are as follows."
4. `:538` "the earlier-stop decisions rest on the calibration run's own re-application of the sequential rule, which only that run has checked."
5. `:734` "The GiBUU re-evaluation carries the label required for it, ``B3 …''" (the label is protected; "required for it" is record-keeping tone).
6. `:682` "(beside the recorded tests)" in the subsection title. Titles are frozen, so this is information only.
7. `:693` and `:636` "the recorded decisions" (used as a status word; "the decisions of Table 12" is enough).
8. `:327` "this value comes from the design review, and its derivation is not documented." The limitation must stay; "its derivation is not given" would be less archival.

## Counts checked

- 18 changed paragraphs read against the before text.
- 248 distinct numbers and 662 tokens compared.
- 14 paper pointers (13 into §10).
- 184 note labels compared.
- 3 protected spans, 105 comment lines and 29 structural commands verified byte-identical.
- 132 ledger rows / 169 probes re-run, plus 1 planted probe.
- 7 sources opened: `mp3c/REPORT.md`, `mp3b/REPORT.md`, ADDENDUM-7, `DECISION-20261005` §5, `PACKET-20261005` §6, `W1-RECORD-20261006`, `s5c_partition.py`.

## Not checked

- I did not run `build_copy.sh` myself; I read its logs.
- I did not open the per-sentence sources for the unchanged paragraphs (J2-J10, J12, J17-J22, J26, J30, J32, J34-J35, J38-J39).
- I did not re-verify the 0.45-0.76 design-review rate against the review that produced it; the note already says its derivation is not documented.
- I did not read the P1N rating files for this chapter, so E is my own reading.
- I did not check that the records document's `joint-5d` tag exists beyond the build's records gates.
