# Review of batch b6: Sec. 6 (`sec_results.tex`), Sec. 7 (`sec_3d.tex`), Sec. 8 (`sec_eavailw.tex`)

Reviewer: independent, read-only. Base: 8f2df745 (the three files are byte-identical to rec3; confirmed with `cmp`).
After: the uncommitted tree `S/wt-note-b6`. The current `git diff` is byte-identical to `b6.diff`. The build
`S/plain-language/builds/note-b6/` postdates the last edit to the tex files (22:55:18, then 22:56).
Line numbers below are for the worktree files.

## Findings

### SHOULD-FIX 1: the regularization-bias caveat in Sec. 8.4 lost its referent (`sec_eavailw.tex:212-214`)
- Before (one sentence): "shows where the excess concentrates (Fig.~\ref{fig:eavailWexcess}): mostly at high
  $\Eavail$ and high $W$, in cell-integrated terms (descriptive); the map does not locate an interaction mechanism,
  and the regularization bias of Sec.~\ref{sec:5d} is largest in that region."
- After: the caveat now opens the next paragraph: "These are descriptive central-value statements under the nominal
  detector response. The map does not locate an interaction mechanism, and the regularization bias of
  Sec.~\ref{sec:5d} is largest in this region."
- Problem: the region named just before "this region" is "a small deficit at $W\simeq1.4$--$\SI{1.8}{GeV}$" (and
  before that, "$W<\SI{1.1}{GeV}$"). Read as printed, the bias statement can attach to the wrong region. The paper
  places the bias at high $\Eavail$, high $W$ (`paper_body.tex:816-817`). The limitation has moved away from the
  result it bounds.
- Fix: "... and the regularization bias of Sec.~\ref{sec:5d} is largest at high $\Eavail$ and high $W$." Or move
  the clause back after "the positive excess lies mostly at high $\Eavail$ and high $W$."

### NIT 2: "Every" sharpens a universal that the next sentence breaks (`sec_3d.tex:254-258`)
- Before: "GENIE and NuWro predictions throughout \S\S...--... are repaired ... The FSI-dial studies, departure ratio
  ... and NuWro-shaped prior ... retain unrepaired samples, as stated there."
- After: "Every GENIE and NuWro prediction in \S\S\ref{sec:3d}--\ref{sec:eavailw} is repaired ... Three studies
  keep the unrepaired samples ...: the FSI-dial studies, ..."
- The FSI-dial studies sit in Sec. 7.7, inside the range that "Every" covers. The scope is the same as before, since
  the old "throughout" was just as wide, but "Every" makes the contradiction explicit.
- Fix: "Apart from three studies that keep the unrepaired samples (...), the GENIE and NuWro predictions in
  \S\S...--... are repaired by ...".

### NIT 3: "not established" dropped from the flux hypothesis (`sec_results.tex:160-161`)
- Before: "our leading hypothesis, not established, is the FHC-only constraint file".
- After: "The public release does not let us determine the origin of this difference; our leading hypothesis is the
  FHC-only constraint file."
- The ledger records this as a collapse (P20). The sentence stays true as read: "hypothesis", together with "does
  not let us determine", carries the status. Acceptable. The paper says "for a reason the released inputs do not let
  us determine" (`paper_body.tex:415`), which is consistent.

### NIT 4: §6.2 no longer prints the word that the beside-comment says is printed (`sec_results.tex:69-77`)
- Before: "the truncated result and, as history, the regularization scan of the exact-split cross-check on an
  earlier covariance, together".
- After: "the truncated result together, with a regularization scan made for the exact-split cross-check on an
  earlier covariance and not repeated for the quoted one".
- **The fact is verified.** Three sources agree:
  - `rebuild/REPORT.md` §6: "Not recomputed ... the regularization scan (no producer)";
  - App. statmethods (`app_statmethods.tex:812-814`): "On an earlier $\mathbf{C}^{\ours}$ (not recomputed for the
    quoted covariance) ..., for the exact-split cross-check";
  - the source comment: "Q" is the quoted covariance (`budget_Q`, adopted 2026-10-17).
- **The decision is still honoured.** `DECISION-20261018-joseph-2d-j3-j5-provisional.md:29` (C7: "keep the
  regularization scan and rescoring, labelled historical") is still met where the scan is printed. That appendix
  heading reads "(historical; all cutoff-dependent)".
- **The mismatch.** The comment at `sec_results.tex:77` ("packet C7: kept, labelled historical") now sits beside a
  sentence with no "historical" label.
- Fix (optional):
  - either amend the comment to say that the label is the factual "earlier covariance, not repeated for the quoted
    one", with the heading label in App. statmethods;
  - or print "a historical regularization scan".

### NIT 5: "would justify" is a slightly stronger verb than "is a defence of" (`sec_3d.tex:70-72`)
- Before: "Agreement with a published convention is therefore a defence of the inherited position, not its
  provenance".
- After: "so agreement with a published convention would justify the inherited definition without explaining its
  origin".
- The move to the conditional weakens the sentence. "Justify" asserts success where "defence" did not.
- Fix: "would support the inherited definition without explaining its origin".

### NIT 6: "The same trees" has no antecedent (`sec_eavailw.tex:43-46`)
- "so a shifted $W$ is stored for each lateral universe, as for $q_{3}$ (\S\ref{sec:4d}). The same trees also
  store ..."
- No trees are mentioned before this. "Like $q_{3}$ ... as for $q_{3}$" also says the same thing twice in one
  sentence.
- Fix: "... so a shifted $W$ is stored for each lateral universe (\S\ref{sec:4d}), together with truth hadronic
  diagnostics: ...".

### NIT 7: "methodological band" lost from Sec. 6.4 (`sec_results.tex:234`)
- Before: "The GBDT estimator gives a $\sim1$-unit methodological band (...)".
- After: "The choice of GBDT estimator moves the distance by about one unit: ...".
- The numbers are unchanged: $\chiPaperExact=3.66$, HistGBT $2.70$, LightGBM $2.64$--$2.75$, so the range is about
  1.0.
- What is lost is the characterization of that range as a methodological uncertainty band. "Moves" also reads as a
  shift rather than a spread.
- Fix: "The choice of GBDT estimator spreads the distance over about one unit, a methodological band: ...".

### NIT 8 (pre-existing, not introduced): "not yet used" against "not used" (`sec_3d.tex:421`)
- The `fig:modedecomp` caption says the 3D covariance "is not yet used for any result in this note". Sec. 7.6
  (`:304-307`) and the other captions (`:294`, `:431`, `:523`) say "computed but is not used" or "not used".
- "Not yet" implies that it will be used later. This is a status inconsistency in the batch's chapters, unchanged
  from the base.
- Fix: delete "yet".

## Checks of the six named items

1. **135 MeV sentence (§7.1, `sec_3d.tex:85-95`): correct.**
   - The source, `docs/EAVAIL_DEFINITION.md:98-101`, gives "439 / 65,911 = 0.666%" events changing truth bin and a
     "worst single bin **+1.049%**". The printed values, 0.67 % and "no true-$\Eavail$ bin by more than 1.05 %", are
     correct roundings (1.049 < 1.05).
   - The materiality caveat sits in the next sentence: "This effect has not been assessed against the projection of
     the five-dimensional covariance used in this note, so its materiality is not established." The source
     supports this: `:118`, "It has not been done".
   - The wording matches the paper (`paper_body.tex:180-184`).
   - **The paper's pointer was broken at base.** The base §7.1 printed "This effect is measured but has not been
     assessed", with no numbers, yet the paper cited §7.1 for 0.67 % and 1.05 %. The addition repairs that pointer.
   - "This note does not call it immaterial" was removed as a repeat. Nothing is lost.
2. **§6.2 regularization scan: verified (see NIT 4).** "Not repeated for the quoted one" is exactly what `REPORT.md`
   §6 and `app_statmethods.tex:813` say.
3. **§7.4: no strengthened claim.**
   - The center (0.3 GeV) and width (0.15 GeV) still print in the paragraph's first sentence (`:158`). "This
     Gaussian" refers back to it.
   - "Neither manufactures nor destroys" has the same content as "does not manufacture or destroy". "On this
     injection" is as narrow as "On that test".
   - The removed tail, "rather than as an artifact of this particular injection", was itself an assertion.
     Removing it weakens the claim; it does not strengthen it.
   - Both limitations still follow, along with the hidden-variable threshold failure: other deformations, and
     response mismatch. This matches the record scope in `CAMPAIGN-s5c-20260924-paper-wide-table.md` R4: "One
     injected shape; no suite; no response mismatch".
   - Not the writer's doing: the record supports "recovered" (1.048 against 1.0485). Whether one non-null injection
     tests "manufacture" is a question about the base wording.
4. **Software-detail rewrites: each is still accurate.**
   - Step-1/step-2 "input".
   - "Truth function computes" and "reconstruction function ... with no final clamp to non-negative values".
   - "2D unfolding code is run with three classifier inputs" (was "2D driver uses a three-column feature stack").
   - "3D bin volume" (was "Jacobian").
   - The flux is "applied per $\pT$ bin, with the same value for every $\pPar$ and $\Eavail$ bin" (was "broadcast
     over").
   - `grwght1p`.
   - `FrInel_pi` "disabled in the standard MAT-MINERvA set of systematics" (was "commented out of ... registry").
   - The `gspl2root` total-CC graph.
   - q3 and W "stored for each lateral universe".
   - "MAT's mean-centered covariance blocks normalized by $1/N$".
   - "Would not subtract a scalar jitter floor". This matches `sec_systematics.tex:284`, "No scalar run-to-run
     jitter floor".
   - "Ratio of the unified-throw to the block covariance". Unified throws are defined in §uq-higherdim.
   - Minor loss: GiBUU "built and run \emph{natively} on the compute system" became "built and run natively". The
     location is dropped; harmless.
5. **Paper pointers: every pointed-to fact prints in its subsection.** The note's label numbers in the aux files are
   identical to rec3: 184 labels, 0 differ.

   | Pointer | Fact | Where it prints |
   |---|---|---|
   | `sec:eavail-definition` (7.1) | 0.67 %, 1.05 %, materiality not established | prints |
   | `sec:eavailw-axis` (8.1) | neutron-mass W; "at most about one Monte Carlo standard error"; "cannot be evaluated for GiBUU" | prints, unchanged |
   | `sec:eavailw-definitions` (8.2) | $\pm4$ MeV pT axis; $\pm2$ MeV for 68 %; near-degenerate directions "that origin has not been shown" | prints; region byte-identical to base |
   | `sec:eavailw-generators` (8.3) | +8.3 % for $W<1.1$ GeV | prints; region byte-identical to base |
   | `sec:eavailw-map` (8.4) | map | prints |
   | `sec:eavailw-band` (8.5) | GiBUU 20 GeV limit; target difference via §8.3 | prints |
   | `sec:results-uq` (6.3) | block sizes | `tab:uq` byte-identical |
   | `sec:3d-2p2h` (7.7) and `sec:4d` (7.8) | FSI, Valencia and Ascencio comparisons | print |

   §6.2 and §6.4 have no `\nsec` pointer from the paper. Every number in §§6.2-6.3 survives (see the number
   comparison below).
6. **The records-citation sentence is byte-identical.** "Our flux band carries MAT's per-universe $\nu$--$e$ and
   inverse-muon-decay⏎constraint weights (Ref.~\cite{NoteRecords2026}, superseded values: struck values). The" is
   the same, including the line break, at base `:157-158` and new `:162-163`. All `\cite{NoteRecords2026}` tags in
   the three files are unchanged.

## Mechanics (D)

- **Writer's checker:** `check_ledger.py --self-test` gives rc 0: 181 rows, 247 probes, 0 failures. Its 5 plants
  fire and its control stays silent.
- **My planted probes fail it as they should** (rc 1, 3 failures):
  - 0.67 % placed in `sec:3d-closure`;
  - the deleted "not established," clause;
  - "neither manufactures" put on an X: probe.
- **Paper text:** the pdftotext of `main_paper.pdf` is byte-identical to the rec3 build. The note and paper texts
  contain 0 `??`.
- **Build log:**
  - RESULT :: PASS; BODY-POINTERS :: PASS; SEC4-RECEIPTS 15/15;
  - struck-value containment: note, paper and primer carry 0 of 69 struck values;
  - "no unresolved references" in all five final logs (the `undefined` hits there are font warnings only);
  - RECORDS-PIN: SKIP in the build copy. Rerun by me on the worktree: PASS, 81 citations.
- **`swallowed_text.py`:** "flagged 0" against 8f2df745.
  - Against today's `origin/main` (551f9432) it flags 1, in `sec_5d.tex`.
  - That flag is an artifact of `origin/main` having since moved: b3 has merged.
  - The batch files are unchanged on `origin/main` since 8f2df745, so a merge does not conflict. Rerun RECORDS-MOVE
    after the rebase, because `check_note_records.py` and the records-move ledger changed upstream.
- **Number comparison** (printed §§6-8, before against after):
  - lost only `8` ("8×", now "eightfold"), `1` ×3 ("1-unit", now "about one unit"; "less-than-1", now "less than
    1%"), `0` ("mec=0"), and a duplicate `0.3`, `0.15` and `30` (they still print at `sec_3d.tex:158`);
  - gained `0.67` and `1.05`.

## Register (E): surviving bookkeeping, history or meta-text (8)

1. "No acceptance threshold fixed before the test is on record, so this residual is not graded." (`sec_3d.tex:169-170`)
2. "The comparisons here and in \S\ref{sec:eavailw-band} are made with unchanged figure code from the repaired
   inputs (Ref.~\cite{NoteRecords2026}, superseded values)." (`sec_3d.tex:265-266`)
3. "Both are ratios within the unrepaired GENIE sample (\S\ref{sec:3d-models}), in which the flux defect cancels to
   first order, and neither was recomputed." (`sec_3d.tex:327-329`)
4. "built and run natively, without a container" (`sec_3d.tex:238`)
5. The caption clause "the 3D covariance that would be quoted is not used for any result in this note
   (Ref.~\cite{NoteRecords2026}, superseded values)" appears four times (`sec_3d.tex:294, 421, 431, 523`). It
   repeats `:304-307`.
6. "it has not yet produced a result." (`sec_eavailw.tex:219-220`)
7. "definitions of the five unfolded observables, as used by the article." and "The article distinguishes the five
   classifier inputs, ..." (`sec_eavailw.tex:67`, §8.2). These are unchanged, from a span the comment marks as moved
   verbatim from the article.
8. "the tests of \S\ref{sec:joint5d}, as run, do not correct" (`sec_eavailw.tex`, §8.3). Unchanged and verbatim.

Otherwise the batch reads well. The hedges are collapsed into the claims, there is no "we record" or "stated so
that", and the code-accessor prose has become physics prose. The printed §§6-8 grew from 10,054 to 10,305 words,
mainly from the two-clause splits.

## Verdict

**ADOPT-AFTER-FIXES.** Fix SHOULD-FIX 1, the referent of the regularization-bias caveat in §8.4. NITs 2, 5 and 6 are
one-line edits, and doing them is recommended. No lost fact, no broken paper pointer and no changed protected text
was found.

**Counts checked:**
- 3 files; 3 word diffs read in full (988-line diff);
- every number in printed §§6-8 (token multiset, before against after);
- 14 paper pointers into the batch (12 `\nsec`/`\ref*` uses, 11 distinct labels);
- 184 note label numbers;
- 3 sets of protected or verbatim spans: the constraint-weights sentence; §8.2-8.3 byte-identical; `tab:uq`,
  `tab:compare` and the two §8 tables, via the writer's BASE probes, which I reran;
- 3 sources opened for items 1-3: `EAVAIL_DEFINITION.md`, `rebuild/REPORT.md` with `app_statmethods.tex`, and the
  CAMPAIGN R4 record;
- 1 decision file (C7);
- 16 software rewrites;
- 3 planted probes.

**Not checked:**
- **RECORDS-MOVE:** not rerun; I relied on the writer's PASS output.
- **Writer's `REPORT.md`:** absent from the work directory. The brief requires it, so the word counts, guardrail list
  and open questions exist only in `changes.md` and `ledger.md`.
- **Ledger rows:** not checked individually beyond the checker run. The 181 rows were not each re-read against the
  text.
- **Code:** not checked against `CVUniverse.h` or the 2D extraction code. That covers the "flux applied per $\pT$
  bin" behaviour and the accessor descriptions; I judged those only against the old text.
- **Figures:** not inspected.
- **pdftotext:** sentence-level reading of the printed note was limited to §§6-8.
